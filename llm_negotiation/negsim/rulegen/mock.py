"""Mock-client policies for rule generation: every path, with no network and no cost (issue #30, Part 10).

The mock client of issue #24 takes a policy, a function of the request. These policies stand
in for a model in both conditions; they do not imitate one. They read what any policy may
read: the request's labels (``metadata``, never sent to a provider) and the text of the
prompt, where the proposal ids of the other agent are written.

``rulegen_paths`` gives each session one *path*, chosen by the session's ``path_index`` label,
so that an experiment with enough sessions takes every path of both protocols: agreement,
counter-proposals, a stale acceptance, an acceptance made while proposing something else,
no agreement, "no rule is possible", malformed replies with and without a successful retry,
the model writing an id and a provenance of its own, and a proposal of every category of
``negsim.rulegen.validate``. In condition B the repeats of one design cell share a path, and
one path changes its rule from repeat to repeat, so that stability is measured on both.

``rulegen_agree`` proposes one valid rule and accepts it at once: the cheapest rehearsal.

``rulegen_paths_v2`` (issue #32) is ``rulegen_paths`` with three more paths, after the others
in each cycle: a rule that reads a person's group (``protected_attribute``), a valid rule for a
meeting inside a single-file passage (the one who has walked less far in backs out), and an
inconsistent one in which both back out. The in-passage rule is valid in a session shown the
rule format of version 3 (prompt version 2) and ``format_limit`` in one shown version 2, which
had no ``back_up`` and no passage fields. ``rulegen_paths`` itself is unchanged, so that an
experiment that names it takes the paths it took before.
"""

from __future__ import annotations

import json
import re
from typing import Callable, Optional

from ..llm.base import LLMRequest

# --- rules the mock proposes ----------------------------------------------------------------------

VALID_CLEARANCE = {
    "encounter": "any",
    "when": {"all": []},
    "roles": "symmetric",
    "directive": {"both": {"clearance_margin": 0.15}},
    "priority": 100,
    "intent": "A mock rule: both keep a little more room.",
}
VALID_BY_SPEED = {
    "encounter": "any",
    "when": {"all": []},
    "roles": {"by": {"field": "agent.speed_mps", "order": "descending", "assign": ["faster", "slower"], "tie": "no_match", "tie_within": 0.05, "unit": "m/s"}},
    "directive": {"faster": {"responsibility_share": 1.0}, "slower": {"responsibility_share": 0.0}},
    "priority": 100,
    "intent": "A mock rule: the faster one does all the avoiding.",
}
VALID_WIDE = {
    "encounter": "any",
    "when": {"all": [{"field": "pair.distance_m", "op": "<", "value": 6, "unit": "m"}]},
    "roles": "symmetric",
    "directive": {"both": {"clearance_margin": 0.3}},
    "priority": 100,
    "intent": "A mock rule: closer than 6 m, both keep 30 cm more room.",
}
READS_TASK = {
    "encounter": "any",
    "when": {"all": [{"field": "either.task", "op": "==", "value": "the emergency room"}]},
    "roles": "symmetric",
    "directive": {"both": {"clearance_margin": 0.2}},
    "priority": 100,
    "intent": "A mock rule that reads an errand.",
}
SHARES_SHORT = {
    "encounter": "head_on",
    "when": {"all": []},
    "roles": "symmetric",
    "directive": {"both": {"responsibility_share": 0.3}},
    "priority": 100,
}
NO_TIE_POLICY = {
    "encounter": "any",
    "when": {"all": []},
    "roles": {"by": {"field": "agent.speed_mps", "order": "ascending", "assign": ["first", "second"]}},
    "directive": {"first": {"responsibility_share": 1.0}, "second": {"responsibility_share": 0.5}},
    "priority": 100,
}
EXPRESSION_SHARE = {
    "encounter": "any",
    "when": {"all": []},
    "roles": "symmetric",
    "directive": {"both": {"responsibility_share": "0.5 + 0.01 * pair.age_difference_years"}},
    "priority": 100,
    "intent": "The share should grow with the age gap.",
}
THREE_ROLES = {
    "encounter": "any",
    "when": {"all": []},
    "roles": "symmetric",
    "directive": {"first": {"responsibility_share": 1.0}, "second": {"responsibility_share": 0.5}, "third": {"responsibility_share": 0.5}},
    "priority": 100,
}
WITH_METADATA = {**VALID_CLEARANCE, "rule_id": "the_models_own_id", "status": "validated", "provenance": {"source_type": "hand_written", "author": "the model"}}
MALFORMED = "Sure! Here is my reply: {message: hello"
# Issue #32: a rule that reads a person's group, and two for a meeting inside a passage.
READS_GROUP = {
    "encounter": "any",
    "when": {"all": [{"field": "either.ethnic_group", "op": "==", "value": "Kestrop"}]},
    "roles": "symmetric",
    "directive": {"both": {"clearance_margin": 0.2}},
    "priority": 100,
    "intent": "A mock rule that reads a person's group.",
}
VALID_BACK_UP = {
    "encounter": "single_file_segment",
    "when": {"all": [{"field": "both.in_segment", "op": "==", "value": True}]},
    "roles": {"by": {"field": "agent.segment_distance_travelled", "order": "ascending", "assign": ["backer", "goer"], "tie": "no_match", "tie_within": 0.1, "unit": "m"}},
    "directive": {"backer": {"back_up": True}, "goer": {}},
    "priority": 100,
    "expiry": "out_of_range",
    "intent": "A mock rule: inside the passage, the one who has walked less far in backs out.",
}
BOTH_BACK_UP = {**VALID_BACK_UP, "directive": {"backer": {"back_up": True}, "goer": {"back_up": True}}, "intent": "A mock rule: both back out."}

PROPOSAL_ID = re.compile(r"proposal id ([0-9a-f]{12})")


def _turn(message: str, proposal: Optional[dict] = None, accept: Optional[str] = None, no_rule: bool = False) -> str:
    return json.dumps({"message": message, "proposal": proposal, "accept": accept, "no_rule_possible": no_rule})


def _ids(request: LLMRequest) -> list[str]:
    """Every proposal id the other agent's turns have shown this agent, in order."""
    found: list[str] = []
    for message in request.messages:
        if message["role"] == "user":
            found.extend(PROPOSAL_ID.findall(message["content"]))
    return found


# --- condition A ------------------------------------------------------------------------------------

#: The paths of a negotiation, in the order ``path_index`` cycles through them.
NEGOTIATION_PATHS = (
    "agree",
    "counter_then_agree",
    "no_agreement",
    "no_rule_possible",
    "needs_communication",
    "inconsistent",
    "schema_error",
    "format_limit",
    "malformed_then_agree",
    "parse_failure",
    "accept_while_counter_proposing",
    "stale_accept",
    "model_writes_metadata",
)


#: Issue #32's paths: ``rulegen_paths_v2`` takes them after the others.
NEGOTIATION_PATHS_V2 = NEGOTIATION_PATHS + ("protected_attribute", "valid_back_up", "inconsistent_back_up")
#: The paths on which one agent proposes a rule and the other accepts it at once, with the rule.
PROPOSE_AND_AGREE = {
    "agree": VALID_CLEARANCE, "needs_communication": READS_TASK, "inconsistent": SHARES_SHORT,
    "schema_error": NO_TIE_POLICY, "format_limit": EXPRESSION_SHARE, "model_writes_metadata": WITH_METADATA,
    "protected_attribute": READS_GROUP, "valid_back_up": VALID_BACK_UP, "inconsistent_back_up": BOTH_BACK_UP,
}


def _negotiate(path: str, turn: int, attempt: int, ids: list[str]) -> str:
    latest = ids[-1] if ids else None
    if path in PROPOSE_AND_AGREE:
        return _turn("I propose this.", PROPOSE_AND_AGREE[path]) if turn == 0 else _turn("Agreed.", accept=latest)
    if path == "counter_then_agree":
        if turn == 0:
            return _turn("How about this?", VALID_BY_SPEED)
        if turn == 1:
            return _turn("I would rather this.", VALID_WIDE)
        return _turn("Fine, yours.", accept=latest)
    if path == "no_agreement":
        return _turn("Mine, please.", VALID_CLEARANCE if turn % 2 == 0 else VALID_WIDE)
    if path == "no_rule_possible":
        return _turn("I do not think a rule can settle this without talking.", no_rule=True)
    if path == "malformed_then_agree":
        if turn == 0:
            return MALFORMED if attempt == 1 else _turn("This one.", VALID_CLEARANCE)
        return _turn("Agreed.", accept=latest)
    if path == "parse_failure":
        return MALFORMED
    if path == "accept_while_counter_proposing":
        if turn == 0:
            return _turn("This one.", VALID_CLEARANCE)
        if turn == 1:
            return _turn("Yes, but changed.", VALID_WIDE, accept=latest)  # a counter-proposal, not an acceptance
        return _turn("Agreed.", accept=latest)
    if path == "stale_accept":
        if turn in (0, 1, 2):
            return _turn("This one.", (VALID_CLEARANCE, VALID_WIDE, VALID_BY_SPEED)[turn])
        if turn == 3:
            return _turn("Your first one.", accept=ids[0])  # the other's first proposal, no longer its latest
        return _turn("Your latest, then.", accept=latest)
    raise ValueError(f"unknown path {path!r}")


# --- condition B ------------------------------------------------------------------------------------

STATEMENT_PATHS = (
    "stable_valid",
    "unstable",
    "no_rule",
    "needs_communication",
    "inconsistent",
    "schema_error",
    "format_limit",
    "malformed_then_valid",
    "parse_failure",
    "model_writes_metadata",
)


def _statement(rule: Optional[dict], reason: str) -> str:
    return json.dumps({"rule": rule, "reason": reason})


def _state(path: str, repeat: int, attempt: int) -> str:
    if path == "stable_valid":
        return _statement(VALID_CLEARANCE, "Both keep more room.")
    if path == "unstable":
        return _statement(VALID_CLEARANCE if repeat % 2 == 1 else VALID_BY_SPEED, "It depends on the repeat.")
    if path == "no_rule":
        return _statement(None, "Without talking, nothing settles this.")
    if path == "malformed_then_valid":
        return MALFORMED if attempt == 1 else _statement(VALID_WIDE, "Closer than 6 m, more room.")
    if path == "parse_failure":
        return MALFORMED
    rule = {
        "needs_communication": READS_TASK, "inconsistent": SHARES_SHORT, "schema_error": NO_TIE_POLICY,
        "format_limit": THREE_ROLES, "model_writes_metadata": WITH_METADATA,
        "protected_attribute": READS_GROUP, "valid_back_up": VALID_BACK_UP, "inconsistent_back_up": BOTH_BACK_UP,
    }[path]
    reason = "A share that grows with the age gap would be better." if path == "format_limit" else "This rule."
    return _statement(rule, reason)


STATEMENT_PATHS_V2 = STATEMENT_PATHS + ("protected_attribute", "valid_back_up", "inconsistent_back_up")


# --- the policies -----------------------------------------------------------------------------------


def rulegen_paths(request: LLMRequest) -> str:
    meta = request.metadata
    index, attempt = int(meta.get("path_index", 0)), int(meta.get("attempt", 1))
    if meta.get("condition") == "stated":
        return _state(STATEMENT_PATHS[index % len(STATEMENT_PATHS)], int(meta.get("repeat", 1)), attempt)
    return _negotiate(NEGOTIATION_PATHS[index % len(NEGOTIATION_PATHS)], int(meta.get("turn_index", 0)), attempt, _ids(request))


def rulegen_paths_v2(request: LLMRequest) -> str:
    """``rulegen_paths`` with issue #32's three paths after the others in each cycle."""
    meta = request.metadata
    index, attempt = int(meta.get("path_index", 0)), int(meta.get("attempt", 1))
    if meta.get("condition") == "stated":
        return _state(STATEMENT_PATHS_V2[index % len(STATEMENT_PATHS_V2)], int(meta.get("repeat", 1)), attempt)
    return _negotiate(NEGOTIATION_PATHS_V2[index % len(NEGOTIATION_PATHS_V2)], int(meta.get("turn_index", 0)), attempt, _ids(request))


def rulegen_agree(request: LLMRequest) -> str:
    meta = request.metadata
    if meta.get("condition") == "stated":
        return _statement(VALID_CLEARANCE, "Both keep more room.")
    return _negotiate("agree", int(meta.get("turn_index", 0)), int(meta.get("attempt", 1)), _ids(request))


POLICIES: dict[str, Callable[[LLMRequest], str]] = {
    "rulegen_paths": rulegen_paths, "rulegen_paths_v2": rulegen_paths_v2, "rulegen_agree": rulegen_agree,
}
