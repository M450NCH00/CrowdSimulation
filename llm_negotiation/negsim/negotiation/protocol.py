"""The dialogue protocol: two agents take turns until they agree or run out of messages.

GameChat: "When the agents observe each other, they take turns sending messages; they
receive the last message from the other agent, add it to the dialogue history, and query
the LLM ... and will stop conversing if they reach a consensus ... or each robot has sent
four messages with no agreement" (arXiv:2503.12333v1, Sec IV-C).

One :class:`Dialogue` holds one negotiation. The simulation loop decides *when* a turn
happens (all at once, or spread over simulated time); this class decides what is sent,
reads the reply, and keeps the record that becomes ``conversation.jsonl``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from ..core.world import World
from ..llm.base import LLMClient, LLMRequest, LLMResponse, LLMTransientError, Usage
from ..scenarios.base import ScenarioSpec
from .consensus import agreed_leader
from .parsing import ParsedTurn, Stance, TurnParseError, parse_turn_output
from .prompts import Participant, PromptTemplate
from .situation import observe, render_report

# "On malformed output, retry once" (issue #24): two attempts per turn at most.
MAX_ATTEMPTS_PER_TURN = 2

END_CONSENSUS = "consensus"
END_MESSAGE_LIMIT = "message_limit"
END_CONFLICT_OVER = "conflict_over"
END_ABORTED = "aborted"


@dataclass(frozen=True)
class NegotiationSettings:
    template: PromptTemplate
    max_messages_per_agent: int
    first_speaker: int
    info_fields: tuple[str, ...]
    visibility: Mapping[str, bool]
    model: str
    temperature: float
    max_tokens: int
    thinking: bool = False


@dataclass
class Attempt:
    """One call to the model within a turn."""

    attempt: int
    prompt_messages: list[dict[str, str]]
    request: dict[str, Any]
    wall_clock_utc: str
    raw_output: Optional[str] = None
    finish_reason: Optional[str] = None
    response_id: Optional[str] = None
    model: Optional[str] = None
    system_fingerprint: Optional[str] = None
    usage: Usage = field(default_factory=Usage)
    cost_usd: float = 0.0
    price_tier: Optional[str] = None
    latency_s: float = 0.0
    parse_error: Optional[str] = None
    api_error: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "attempt": self.attempt,
            "wall_clock_utc": self.wall_clock_utc,
            "prompt_messages": self.prompt_messages,
            "request": self.request,
            "raw_output": self.raw_output,
            "finish_reason": self.finish_reason,
            "response_id": self.response_id,
            "model": self.model,
            "system_fingerprint": self.system_fingerprint,
            "usage": self.usage.as_dict(),
            "cost_usd": round(self.cost_usd, 10),
            "price_tier": self.price_tier,
            "latency_s": round(self.latency_s, 4),
            "parse_error": self.parse_error,
            "api_error": self.api_error,
        }


@dataclass
class Turn:
    """One agent's turn: what it was shown, what it replied, and how that was read."""

    turn_index: int
    speaker: int
    sim_time_s: float
    wall_clock_utc: str
    situation_report: str
    situation_values: dict[str, Any]
    message: str
    stance: Stance
    parse_ok: bool
    parse_error: Optional[str]
    attempts: list[Attempt]

    @property
    def usage(self) -> Usage:
        total = Usage()
        for attempt in self.attempts:
            total = total + attempt.usage
        return total

    @property
    def cost_usd(self) -> float:
        return sum(attempt.cost_usd for attempt in self.attempts)

    @property
    def latency_s(self) -> float:
        return sum(attempt.latency_s for attempt in self.attempts)

    def as_dict(self) -> dict[str, Any]:
        final = self.attempts[-1]
        return {
            "turn_index": self.turn_index,
            "speaker": self.speaker,
            "sim_time_s": round(self.sim_time_s, 4),
            "wall_clock_utc": self.wall_clock_utc,
            "situation_report": self.situation_report,
            "situation_values": self.situation_values,
            "prompt_messages": final.prompt_messages,
            "raw_output": final.raw_output,
            "message": self.message,
            "stance": self.stance.value,
            "parse_ok": self.parse_ok,
            "parse_error": self.parse_error,
            "n_attempts": len(self.attempts),
            "tokens": self.usage.as_dict(),
            "cost_usd": round(self.cost_usd, 10),
            "latency_s": round(self.latency_s, 4),
            "attempts": [attempt.as_dict() for attempt in self.attempts],
        }


class Dialogue:
    def __init__(
        self,
        settings: NegotiationSettings,
        participants: Mapping[int, Participant],
        spec: ScenarioSpec,
        client: LLMClient,
        labels: Optional[Mapping[str, Any]] = None,
    ):
        if len(participants) != 2:
            raise ValueError("negotiation is implemented for exactly two agents")
        if settings.first_speaker not in participants:
            raise ValueError(f"first_speaker {settings.first_speaker} is not one of the agents")
        if settings.max_messages_per_agent < 1:
            raise ValueError("max_messages_per_agent must be at least 1")
        self.settings = settings
        self.participants = dict(participants)
        self.spec = spec
        self.client = client
        self.labels = dict(labels or {})
        first = settings.first_speaker
        second = next(agent_id for agent_id in self.participants if agent_id != first)
        self.order = (first, second)
        self.system_prompts = {
            agent_id: settings.template.render_system(
                self.participants[agent_id],
                self.participants[other_id],
                spec.scenario_type,
                settings.visibility,
            )
            for agent_id, other_id in ((first, second), (second, first))
        }
        self._history: dict[int, list[dict[str, str]]] = {first: [], second: []}
        self.turns: list[Turn] = []
        self.started_at: Optional[float] = None
        self.ended_at: Optional[float] = None
        self.end_reason: Optional[str] = None
        self.leader: Optional[int] = None

    # --- state ---------------------------------------------------------------------------

    @property
    def started(self) -> bool:
        return self.started_at is not None

    @property
    def active(self) -> bool:
        return self.started and self.end_reason is None

    @property
    def consensus(self) -> bool:
        return self.end_reason == END_CONSENSUS

    @property
    def max_turns(self) -> int:
        return 2 * self.settings.max_messages_per_agent

    def start(self, sim_time: float) -> None:
        if self.started:
            raise RuntimeError("the dialogue has already started")
        self.started_at = sim_time

    def stop(self, reason: str, sim_time: float) -> None:
        if self.end_reason is None:
            self.end_reason, self.ended_at = reason, sim_time

    # --- one turn ------------------------------------------------------------------------

    def take_turn(self, world: World) -> Turn:
        """Ask the next speaker for its turn, using the world as it is now."""
        if not self.active:
            raise RuntimeError("the dialogue is not active")
        settings, template = self.settings, self.settings.template
        index = len(self.turns)
        speaker, other = self.order[index % 2], self.order[(index + 1) % 2]

        observation = observe(world, self.spec, speaker, other, self.started_at)
        report = render_report(observation, settings.info_fields, settings.visibility, template)
        if index == 0:
            said = template.first_turn()
        elif self.turns[-1].message:
            said = template.incoming(self.turns[-1].message)
        else:
            said = template.no_reply()
        user_content = f"{report}\n\n{said}" if report else said
        base_messages = [
            {"role": "system", "content": self.system_prompts[speaker]},
            *self._history[speaker],
            {"role": "user", "content": user_content},
        ]

        attempts: list[Attempt] = []
        parsed: Optional[ParsedTurn] = None
        stopped: Optional[Exception] = None
        messages = base_messages
        for number in range(1, MAX_ATTEMPTS_PER_TURN + 1):
            request = LLMRequest(
                messages=messages,
                model=settings.model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                json_mode=True,
                thinking=settings.thinking,
                metadata={**self.labels, "turn_index": index, "speaker": speaker, "attempt": number},
            )
            attempt = Attempt(
                attempt=number,
                prompt_messages=[dict(m) for m in messages],
                request=request.params(),
                wall_clock_utc=_utc_now(),
            )
            try:
                response = self.client.complete(request)
            except LLMTransientError as exc:
                attempt.api_error = str(exc)
                attempts.append(attempt)
                continue
            except Exception as exc:  # the budget guard refused, or the model cannot be used
                if not attempts:
                    raise  # nothing was said and nothing was paid for: there is no turn to record
                attempt.api_error = f"{type(exc).__name__}: {exc}"
                attempts.append(attempt)
                stopped = exc
                break
            attempts.append(attempt)
            _fill(attempt, response)
            try:
                parsed = parse_turn_output(response.content)
                break
            except TurnParseError as exc:
                attempt.parse_error = str(exc)
                # Show the model what it sent, then ask again.
                messages = list(base_messages)
                if response.content and response.content.strip():
                    messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": template.retry()})

        failure = None
        if parsed is None:
            # No attempt produced a readable turn: it stands as silence, with no position taken.
            failure = attempts[-1].parse_error or f"api_error: {attempts[-1].api_error}"
            parsed = ParsedTurn("", Stance.UNDECIDED)
        turn = Turn(
            turn_index=index,
            speaker=speaker,
            sim_time_s=world.time,
            wall_clock_utc=attempts[0].wall_clock_utc,
            situation_report=report,
            situation_values=observation.as_dict(),
            message=parsed.message,
            stance=parsed.stance,
            parse_ok=failure is None,
            parse_error=failure,
            attempts=attempts,
        )
        self.turns.append(turn)
        self._history[speaker].extend(
            [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": parsed.as_json()},
            ]
        )
        if stopped is not None:
            # The turn's earlier attempt was paid for, so it is on record; now let the
            # caller see why the dialogue cannot go on.
            raise stopped
        self._check_end(world.time)
        return turn

    def _check_end(self, sim_time: float) -> None:
        if len(self.turns) >= 2:
            previous, current = self.turns[-2], self.turns[-1]
            leader = agreed_leader(
                (previous.speaker, previous.stance), (current.speaker, current.stance)
            )
            if leader is not None:
                self.leader = leader
                self.stop(END_CONSENSUS, sim_time)
                return
        if len(self.turns) >= self.max_turns:
            self.stop(END_MESSAGE_LIMIT, sim_time)

    # --- summary -------------------------------------------------------------------------

    def messages_sent(self) -> dict[int, int]:
        return {
            agent_id: sum(1 for turn in self.turns if turn.speaker == agent_id)
            for agent_id in self.order
        }

    def totals(self) -> dict[str, Any]:
        usage = Usage()
        for turn in self.turns:
            usage = usage + turn.usage
        return {
            "llm_calls": sum(len(turn.attempts) for turn in self.turns),
            "parse_failures": sum(1 for turn in self.turns if not turn.parse_ok),
            "retries": sum(len(turn.attempts) - 1 for turn in self.turns),
            "tokens": usage.as_dict(),
            "cost_usd": round(sum(turn.cost_usd for turn in self.turns), 10),
            "llm_latency_s": round(sum(turn.latency_s for turn in self.turns), 4),
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _fill(attempt: Attempt, response: LLMResponse) -> None:
    attempt.raw_output = response.content
    attempt.finish_reason = response.finish_reason
    attempt.response_id = response.response_id
    attempt.model = response.model
    attempt.system_fingerprint = response.system_fingerprint
    attempt.usage = response.usage
    attempt.cost_usd = response.cost_usd
    attempt.price_tier = response.price_tier
    attempt.latency_s = response.latency_s
