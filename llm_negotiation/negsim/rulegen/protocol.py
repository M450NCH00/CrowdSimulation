"""The two protocols of rule generation (issue #30, Parts 5 and 6; ``docs/rule-generation.md``).

**Condition A, negotiate a standing rule** (:class:`RuleNegotiation`). Two agents take turns,
issue #24's dialogue loop: each turn is one request to the model, read by
:func:`parse_negotiation_turn`, retried once if it cannot be read (``request_with_retry``),
and recorded whole. A turn is a JSON object with

``message``           what the agent says (text);
``proposal``          a rule in the rule format, or null;
``accept``            the proposal id of the other agent's latest proposal, or null;
``no_rule_possible``  true if the agent thinks no rule is possible without talking first.

The two have **agreed** when one accepts the other's *latest* proposal by its id (the first
characters of its canonical hash, ``negsim.rules.canonical``) and does not at the same time
propose a different rule: a changed rule is a counter-proposal, never an acceptance. They have
agreed that **no rule is possible** when both say so on consecutive turns. Otherwise the
negotiation ends at the message limit (``no_agreement``), or when a turn cannot be read after
its retry (``parse_failure``). Which agent spoke first, which proposed the rule that was
accepted, and which accepted it are recorded.

**Condition B, state a rule** (:class:`RuleStatement`). One request, with its retry, read by
:func:`parse_statement`: ``{"rule": <rule or null>, "reason": <text>}``.

Nothing here judges a rule: every proposal is kept as written and categorised afterwards
(``negsim.rulegen.validate``).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from ..llm.base import LLMClient, Usage
from ..negotiation.parsing import TurnParseError, _strip_code_fence
from ..negotiation.protocol import MAX_ATTEMPTS_PER_TURN, Attempt, request_with_retry
from ..rules.canonical import PROPOSAL_ID_LENGTH, canonical_hash
from .describe import Templates, negotiation_prompt, statement_prompt
from .design import Session

# How a negotiation can end.
OUTCOME_AGREED = "agreed"
OUTCOME_NO_RULE = "no_rule_possible"
OUTCOME_NO_AGREEMENT = "no_agreement"
OUTCOME_PARSE_FAILURE = "parse_failure"
OUTCOME_ABORTED = "aborted"  # the budget guard refused, or the model could not be used
NEGOTIATION_OUTCOMES = (OUTCOME_AGREED, OUTCOME_NO_RULE, OUTCOME_NO_AGREEMENT, OUTCOME_PARSE_FAILURE, OUTCOME_ABORTED)
# How a statement can end.
OUTCOME_STATED = "stated"
OUTCOME_NULL_RULE = "no_rule"
STATEMENT_OUTCOMES = (OUTCOME_STATED, OUTCOME_NULL_RULE, OUTCOME_PARSE_FAILURE, OUTCOME_ABORTED)

# What an acceptance was.
ACCEPT_AGREED = "agreed"
ACCEPT_WITH_COUNTER = "accepted_but_counter_proposed"  # accepted the other's id while proposing something else
ACCEPT_STALE = "stale"  # the id of an earlier proposal of the other agent, not its latest
ACCEPT_OWN = "own"  # the id of the agent's own proposal
ACCEPT_UNKNOWN = "unknown"  # no proposal has that id
ACCEPT_NOTHING_PROPOSED = "nothing_proposed"  # the other agent has proposed nothing yet

DEFAULT_MAX_MESSAGES_PER_AGENT = 4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _object(raw: Optional[str]) -> dict[str, Any]:
    if raw is None or not raw.strip():
        raise TurnParseError("empty_output")
    try:
        data = json.loads(_strip_code_fence(raw.strip()))
    except ValueError as exc:
        raise TurnParseError("not_json", str(exc)) from exc
    if not isinstance(data, dict):
        raise TurnParseError("not_an_object", f"got {type(data).__name__}")
    return data


# --- condition A --------------------------------------------------------------------------------


@dataclass(frozen=True)
class NegotiationTurn:
    """One turn of condition A as read. ``proposal`` is kept exactly as the model wrote it."""

    message: str
    proposal: Optional[dict[str, Any]]
    accept: Optional[str]
    no_rule_possible: bool

    def as_json(self) -> str:
        """The turn re-serialised as it is kept in the agent's own history."""
        return json.dumps(
            {"message": self.message, "proposal": self.proposal, "accept": self.accept, "no_rule_possible": self.no_rule_possible},
            ensure_ascii=False,
        )


def parse_negotiation_turn(raw: Optional[str]) -> NegotiationTurn:
    """Read a reply of condition A, or raise :class:`TurnParseError`.

    Tolerated, as in issue #24: whitespace, a Markdown code fence, extra keys. A missing
    ``proposal`` or ``accept`` is null and a missing ``no_rule_possible`` false. Not
    tolerated: a reply that is not a JSON object, a ``message`` that is missing or not text,
    a ``proposal`` that is neither an object nor null, an ``accept`` that is neither text nor
    null, a ``no_rule_possible`` that is not true or false.
    """
    data = _object(raw)
    if "message" not in data:
        raise TurnParseError("missing_message")
    if not isinstance(data["message"], str):
        raise TurnParseError("message_not_text", f"got {type(data['message']).__name__}")
    proposal = data.get("proposal")
    if proposal is not None and not isinstance(proposal, dict):
        raise TurnParseError("proposal_not_an_object", f"got {type(proposal).__name__}")
    accept = data.get("accept")
    if accept is not None and not isinstance(accept, str):
        raise TurnParseError("accept_not_text", f"got {type(accept).__name__}")
    flag = data.get("no_rule_possible", False)
    if not isinstance(flag, bool):
        raise TurnParseError("no_rule_possible_not_a_boolean", f"got {flag!r}")
    accept = None if accept is None or not accept.strip() or accept.strip().lower() == "null" else accept.strip().lower()
    return NegotiationTurn(data["message"].strip(), proposal, accept, flag)


@dataclass
class TurnRecord:
    """One turn as it is logged."""

    turn_index: int
    speaker: int
    shown: str
    attempts: list[Attempt]
    turn: Optional[NegotiationTurn]
    parse_error: Optional[str]
    proposal_hash: Optional[str] = None
    accept_status: Optional[str] = None

    @property
    def usage(self) -> Usage:
        total = Usage()
        for attempt in self.attempts:
            total = total + attempt.usage
        return total

    @property
    def cost_usd(self) -> float:
        return sum(attempt.cost_usd for attempt in self.attempts)

    def as_dict(self) -> dict[str, Any]:
        turn = self.turn
        return {
            "turn_index": self.turn_index,
            "speaker": self.speaker,
            "shown": self.shown,
            "parse_ok": turn is not None,
            "parse_error": self.parse_error,
            "message": None if turn is None else turn.message,
            "proposal": None if turn is None else turn.proposal,
            "proposal_hash": self.proposal_hash,
            "proposal_id": None if self.proposal_hash is None else self.proposal_hash[:PROPOSAL_ID_LENGTH],
            "accept": None if turn is None else turn.accept,
            "accept_status": self.accept_status,
            "no_rule_possible": None if turn is None else turn.no_rule_possible,
            "n_attempts": len(self.attempts),
            "tokens": self.usage.as_dict(),
            "cost_usd": round(self.cost_usd, 10),
            "attempts": [attempt.as_dict() for attempt in self.attempts],
        }


@dataclass(frozen=True)
class LLMSettings:
    model: str
    temperature: float
    max_tokens: int
    thinking: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {"model": self.model, "temperature": self.temperature, "max_tokens": self.max_tokens, "thinking": self.thinking, "json_mode": True}


class RuleNegotiation:
    """One session of condition A."""

    def __init__(
        self,
        case: Mapping[str, Any],
        session: Session,
        templates: Templates,
        client: LLMClient,
        llm: LLMSettings,
        max_messages_per_agent: int = DEFAULT_MAX_MESSAGES_PER_AGENT,
        labels: Optional[Mapping[str, Any]] = None,
    ):
        if max_messages_per_agent < 1:
            raise ValueError("max_messages_per_agent must be at least 1")
        self.case, self.session, self.templates, self.client, self.llm = case, session, templates, client, llm
        self.max_messages_per_agent = max_messages_per_agent
        self.labels = dict(labels or {})
        self.order = (session.first, session.second)
        self.system_prompts = {agent: negotiation_prompt(case, session, agent, templates) for agent in self.order}
        self._history: dict[int, list[dict[str, str]]] = {agent: [] for agent in self.order}
        self.turns: list[TurnRecord] = []
        #: Each agent's latest proposal: (turn index, the proposal as written, its canonical hash).
        self.latest: dict[int, tuple[int, dict[str, Any], str]] = {}
        self.proposed: dict[int, list[str]] = {agent: [] for agent in self.order}
        self.outcome: Optional[str] = None
        self.agreement: Optional[dict[str, Any]] = None
        self.error: Optional[str] = None

    @property
    def max_turns(self) -> int:
        return 2 * self.max_messages_per_agent

    def run(self) -> str:
        while self.outcome is None:
            self.take_turn()
        return self.outcome

    def _shown(self, index: int, speaker: int) -> str:
        """What the speaker is told on its turn: the other's last turn, then whose turn it is.

        An ``accept`` that did not make an agreement is shown as what it was, an id that is not
        the speaker's latest proposal, unless it *was* that id written beside a different rule:
        a counter-proposal, which the speaker is shown as the new proposal it is.
        """
        words = self.templates.data["turns"]
        if index == 0:
            return words["first"]
        previous = self.turns[-1]
        lines = [words["header"]]
        turn = previous.turn
        if turn.message:
            lines.append(words["message"].replace("{message}", turn.message))
        if turn.proposal is not None:
            text = json.dumps(turn.proposal, ensure_ascii=False)
            lines.append(words["proposal"].replace("{proposal_id}", previous.proposal_hash[:PROPOSAL_ID_LENGTH]).replace("{proposal}", text))
        if turn.accept is not None and previous.accept_status not in (ACCEPT_AGREED, ACCEPT_WITH_COUNTER):
            lines.append(words["accept_other"].replace("{accept}", turn.accept))
        if turn.no_rule_possible:
            lines.append(words["no_rule"])
        return "\n".join(lines) + "\n\n" + words["your_turn"]

    def take_turn(self) -> TurnRecord:
        if self.outcome is not None:
            raise RuntimeError("the negotiation is over")
        index = len(self.turns)
        speaker = self.order[index % 2]
        other = self.order[(index + 1) % 2]
        shown = self._shown(index, speaker)
        base = [{"role": "system", "content": self.system_prompts[speaker]}, *self._history[speaker], {"role": "user", "content": shown}]
        try:
            reply = request_with_retry(
                self.client, base, self.llm.model, self.llm.temperature, self.llm.max_tokens, self.llm.thinking,
                {**self.labels, "turn_index": index, "speaker": speaker, "speaker_role": "first" if index % 2 == 0 else "second"},
                parse_negotiation_turn, self.templates.data["turns"]["retry"],
            )
        except Exception as exc:  # refused before anything was sent: nothing to record but why
            self.outcome, self.error = OUTCOME_ABORTED, f"{type(exc).__name__}: {exc}"
            raise
        record = TurnRecord(index, speaker, shown, reply.attempts, reply.parsed, reply.failure)
        self.turns.append(record)
        if reply.stopped is not None:
            self.outcome, self.error = OUTCOME_ABORTED, f"{type(reply.stopped).__name__}: {reply.stopped}"
            raise reply.stopped
        if reply.parsed is None:
            self.outcome = OUTCOME_PARSE_FAILURE
            return record
        turn: NegotiationTurn = reply.parsed
        self._history[speaker] += [{"role": "user", "content": shown}, {"role": "assistant", "content": turn.as_json()}]
        if turn.proposal is not None:
            record.proposal_hash = canonical_hash(turn.proposal)
            self.proposed[speaker].append(record.proposal_hash)
        if turn.accept is not None:
            record.accept_status = self._accept_status(turn, record, speaker, other)
            if record.accept_status == ACCEPT_AGREED:
                proposal_turn, rule, digest = self.latest[other]
                self.outcome = OUTCOME_AGREED
                self.agreement = {
                    "rule": rule,
                    "canonical_hash": digest,
                    "proposal_id": digest[:PROPOSAL_ID_LENGTH],
                    "proposed_by": other,
                    "proposed_at_turn": proposal_turn,
                    "accepted_by": speaker,
                    "accepted_at_turn": index,
                    "proposer_spoke_first": other == self.order[0],
                }
                return record
        if turn.proposal is not None:
            self.latest[speaker] = (index, turn.proposal, record.proposal_hash)
        if turn.no_rule_possible and index > 0 and self.turns[-2].turn is not None and self.turns[-2].turn.no_rule_possible:
            self.outcome = OUTCOME_NO_RULE
            return record
        if len(self.turns) >= self.max_turns:
            self.outcome = OUTCOME_NO_AGREEMENT
        return record

    def _accept_status(self, turn: NegotiationTurn, record: TurnRecord, speaker: int, other: int) -> str:
        matches = lambda digest: digest.startswith(turn.accept) and len(turn.accept) >= PROPOSAL_ID_LENGTH  # noqa: E731
        latest = self.latest.get(other)
        if latest is not None and matches(latest[2]):
            if turn.proposal is not None and record.proposal_hash != latest[2]:
                return ACCEPT_WITH_COUNTER
            return ACCEPT_AGREED
        if any(matches(digest) for digest in self.proposed[other]):
            return ACCEPT_STALE
        if any(matches(digest) for digest in self.proposed[speaker]) or (record.proposal_hash and matches(record.proposal_hash)):
            return ACCEPT_OWN
        return ACCEPT_NOTHING_PROPOSED if latest is None else ACCEPT_UNKNOWN

    # --- what is logged ---------------------------------------------------------------------------

    def proposals(self) -> list[dict[str, Any]]:
        """Every proposal made, in order, with who made it and whether it was the one agreed."""
        agreed = None if self.agreement is None else (self.agreement["proposed_at_turn"], self.agreement["canonical_hash"])
        return [
            {
                "turn_index": record.turn_index,
                "proposer": record.speaker,
                "proposal": record.turn.proposal,
                "canonical_hash": record.proposal_hash,
                "agreed": agreed == (record.turn_index, record.proposal_hash),
            }
            for record in self.turns
            if record.turn is not None and record.turn.proposal is not None
        ]

    def totals(self) -> dict[str, Any]:
        usage = Usage()
        for record in self.turns:
            usage = usage + record.usage
        return {
            "turns": len(self.turns),
            "llm_calls": sum(len(record.attempts) for record in self.turns),
            "retries": sum(len(record.attempts) - 1 for record in self.turns),
            "tokens": usage.as_dict(),
            "cost_usd": round(sum(record.cost_usd for record in self.turns), 10),
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "condition": "negotiated",
            "outcome": self.outcome,
            "error": self.error,
            "first_speaker": self.order[0],
            "second_speaker": self.order[1],
            "max_messages_per_agent": self.max_messages_per_agent,
            "max_attempts_per_turn": MAX_ATTEMPTS_PER_TURN,
            "agreement": self.agreement,
            "system_prompts": {str(agent): prompt for agent, prompt in self.system_prompts.items()},
            "turns": [record.as_dict() for record in self.turns],
            "proposals": self.proposals(),
            "totals": self.totals(),
        }


# --- condition B --------------------------------------------------------------------------------


@dataclass(frozen=True)
class Statement:
    rule: Optional[dict[str, Any]]
    reason: str


def parse_statement(raw: Optional[str]) -> Statement:
    """Read a reply of condition B, or raise :class:`TurnParseError`.

    A JSON object with ``rule`` (an object, or null) and an optional ``reason`` (text).
    Tolerated: whitespace, a code fence, extra keys. A missing ``rule`` is not tolerated.
    """
    data = _object(raw)
    if "rule" not in data:
        raise TurnParseError("missing_rule")
    rule = data["rule"]
    if rule is not None and not isinstance(rule, dict):
        raise TurnParseError("rule_not_an_object", f"got {type(rule).__name__}")
    reason = data.get("reason", "")
    if reason is None:
        reason = ""
    if not isinstance(reason, str):
        raise TurnParseError("reason_not_text", f"got {type(reason).__name__}")
    return Statement(rule, reason.strip())


@dataclass
class RuleStatement:
    """One session (one repeat) of condition B."""

    case: Mapping[str, Any]
    session: Session
    templates: Templates
    client: LLMClient
    llm: LLMSettings
    labels: Mapping[str, Any] = field(default_factory=dict)
    outcome: Optional[str] = None
    statement: Optional[Statement] = None
    attempts: list[Attempt] = field(default_factory=list)
    parse_error: Optional[str] = None
    error: Optional[str] = None
    canonical_hash: Optional[str] = None
    prompt: str = ""

    def run(self) -> str:
        self.prompt = statement_prompt(self.case, self.session, self.templates)
        try:
            reply = request_with_retry(
                self.client, [{"role": "system", "content": self.prompt}], self.llm.model, self.llm.temperature,
                self.llm.max_tokens, self.llm.thinking, {**self.labels, "turn_index": 0, "speaker": None},
                parse_statement, self.templates.data["retry"],
            )
        except Exception as exc:
            self.outcome, self.error = OUTCOME_ABORTED, f"{type(exc).__name__}: {exc}"
            raise
        self.attempts, self.parse_error = reply.attempts, reply.failure
        if reply.stopped is not None:
            self.outcome, self.error = OUTCOME_ABORTED, f"{type(reply.stopped).__name__}: {reply.stopped}"
            raise reply.stopped
        if reply.parsed is None:
            self.outcome = OUTCOME_PARSE_FAILURE
            return self.outcome
        self.statement = reply.parsed
        if self.statement.rule is None:
            self.outcome = OUTCOME_NULL_RULE
        else:
            self.outcome = OUTCOME_STATED
            self.canonical_hash = canonical_hash(self.statement.rule)
        return self.outcome

    def totals(self) -> dict[str, Any]:
        usage = Usage()
        for attempt in self.attempts:
            usage = usage + attempt.usage
        return {
            "llm_calls": len(self.attempts),
            "retries": max(0, len(self.attempts) - 1),
            "tokens": usage.as_dict(),
            "cost_usd": round(sum(attempt.cost_usd for attempt in self.attempts), 10),
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "condition": "stated",
            "outcome": self.outcome,
            "error": self.error,
            "person_1": self.session.first,
            "person_2": self.session.second,
            "max_attempts": MAX_ATTEMPTS_PER_TURN,
            "system_prompt": self.prompt,
            "parse_error": self.parse_error,
            "rule": None if self.statement is None else self.statement.rule,
            "reason": None if self.statement is None else self.statement.reason,
            "canonical_hash": self.canonical_hash,
            "attempts": [attempt.as_dict() for attempt in self.attempts],
            "totals": self.totals(),
        }


def stability(hashes: list[Optional[str]]) -> float:
    """The fraction of repeats that gave the most common canonical hash (no rule counts as one
    answer); 1 when every repeat gave the same rule. Semantic equivalence is SI-4's."""
    if not hashes:
        return float("nan")
    counts: dict[Optional[str], int] = {}
    for digest in hashes:
        counts[digest] = counts.get(digest, 0) + 1
    return max(counts.values()) / len(hashes)
