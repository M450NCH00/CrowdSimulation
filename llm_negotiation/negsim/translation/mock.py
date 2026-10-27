"""The mock translator (issue #67, task 9): a deterministic stand-in for the model, for rehearsals.

``translate_rehearsal_v1`` reads the rule to translate out of the prompt and answers in the reply
format. It does not imitate a model; it takes one of :data:`PATHS`, chosen by the SHA-256 of the
rule's own sentence (so a rule always takes the same path, and a rehearsal is exactly
reproducible), and exercises every category of ``negsim.rulegen.validate`` and every reply:

- ``valid``: roles by age when the rule reads an age (the younger slows and does all the avoiding),
  else a symmetric rule that slows both within 6 m; every factor format 3 cannot read is listed as
  a lost condition;
- ``valid_after_retry``: an unreadable first reply, then ``valid``'s;
- ``valid_keeps_room``: a symmetric rule that keeps 0.1 m more room;
- ``format_limit``: roles by gender, a category;
- ``needs_communication``: roles by assertiveness, which only the person knows;
- ``no_rule``: null, with everything lost;
- ``protected_attribute``: a condition on ethnicity (never written);
- ``schema_error``: a directive field format 3 does not have (a turn angle).

``translate_rehearsal_v2`` (issue #108) does the same for ``translate_v2`` and rule format 4
(:data:`PATHS_V4`): roles by a condition on a visible attribute with a plan of steps, an own-only
condition with steps, an own-only condition on the person's own view of the other's
attractiveness (the one place it is readable), an own-only condition that tries to set a side
(``own_only_scope``, needs communication), attractiveness and ethnicity in a condition
(protected), null, and a step outside Step 1's limits (a schema error).
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Optional

from ..llm.base import LLMRequest
from .losses import LOST_STATUSES, factor_losses

PATHS = (
    "valid", "valid_after_retry", "valid_keeps_room", "format_limit", "needs_communication", "no_rule",
    "protected_attribute", "schema_error",
)
_RULE = re.compile(r"^Rule: (.*)$", re.MULTILINE)
_FACTOR = re.compile(r"^- ([a-z_]+): ", re.MULTILINE)
_FACTORS = re.compile(r"^Factors it uses[^\n]*\n((?:- [^\n]*\n?)*)", re.MULTILINE)


def path_of(sentence: str) -> str:
    """The path a rule takes: its sentence's SHA-256, modulo the number of paths."""
    return PATHS[int(hashlib.sha256(sentence.encode("utf-8")).hexdigest(), 16) % len(PATHS)]


def _head_on(roles: Any, directive: dict[str, Any], when: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
    return {"encounter": "head_on", "when": {"all": when or []}, "roles": roles, "directive": directive, "priority": 100,
            "intent": "A mock translation."}


def _by(field: str, assign: list[str]) -> dict[str, Any]:
    return {"by": {"field": field, "order": "ascending", "assign": assign, "tie": "no_match"}}


def _valid(factors: list[str]) -> dict[str, Any]:
    if any(name in ("own_age", "other_age") for name in factors):
        return _head_on(_by("agent.age", ["yields", "goes_on"]), {"yields": {"speed_scale": 0.8, "responsibility_share": 1.0}, "goes_on": {"responsibility_share": 0.0}})
    return _head_on("symmetric", {"both": {"speed_scale": 0.8}}, [{"field": "pair.distance_m", "op": "<=", "value": 6.0, "unit": "m"}])


def translate_rehearsal_v1(request: LLMRequest) -> Optional[str]:
    user = "\n".join(m["content"] for m in request.messages if m["role"] == "user")
    found = _RULE.search(user)
    if found is None:
        return "I could not find the rule."
    block = _FACTORS.search(user)
    factors = _FACTOR.findall(block.group(1)) if block else []
    path = path_of(found.group(1))
    lost = [{"part": item["column"], "kind": "condition", "how": "left_out"} for item in factor_losses(factors) if item["status"] in LOST_STATUSES]
    retried = any(m["role"] == "assistant" for m in request.messages)
    if path == "valid_after_retry" and not retried:
        return "Here is the rule: it slows the younger person."
    rules = {
        "valid": _valid(factors),
        "valid_after_retry": _valid(factors),
        "valid_keeps_room": _head_on("symmetric", {"both": {"clearance_margin": 0.1}}),
        "format_limit": _head_on(_by("agent.gender", ["yields", "goes_on"]), {"yields": {"responsibility_share": 1.0}, "goes_on": {"responsibility_share": 0.0}}),
        "needs_communication": _head_on(_by("agent.assertiveness", ["yields", "goes_on"]), {"yields": {"responsibility_share": 1.0}, "goes_on": {"responsibility_share": 0.0}}),
        "no_rule": None,
        "protected_attribute": _head_on("symmetric", {"both": {"speed_scale": 0.9}}, [{"field": "either.ethnicity", "op": "==", "value": "chinese"}]),
        "schema_error": _head_on("symmetric", {"both": {"turn_deg": 15}}),
    }
    if path == "no_rule":
        lost.append({"part": found.group(1), "kind": "other", "how": "left_out"})
    else:
        lost.append({"part": "when it starts", "kind": "start", "how": "approximated"})
    return "```json\n" + json.dumps({"rule": rules[path], "lost": lost, "note": f"mock path {path}"}) + "\n```"


# --- rule format 4 (issue #108, RF-31) ------------------------------------------------------------

#: ``translate_rehearsal_v2``'s paths, for ``translate_v2``: every new form of rule format 4, and
#: every refusal it adds or keeps.
PATHS_V4 = (
    "valid_condition_steps", "valid_own_when", "valid_after_retry", "valid_own_attractiveness", "own_only_scope",
    "protected_attractiveness", "protected_attribute", "no_rule", "schema_error",
)
_SIDESTEP = [{"start": {"at_distance_m": 4.0}, "sidestep": {"to": "right", "metres": 0.4}, "speed_mps": 1.0},
             {"speed_mps": 1.1, "until": "other_passes"}]


def path_of_v4(sentence: str) -> str:
    return PATHS_V4[int(hashlib.sha256(sentence.encode("utf-8")).hexdigest(), 16) % len(PATHS_V4)]


def _by_condition(field: str, value: str, assign: list[str]) -> dict[str, Any]:
    return {"by_condition": {"when": {"field": field, "op": "==", "value": value}, "assign": assign, "tie": "no_match"}}


def _seen(factors: list[str]) -> tuple[str, str]:
    """The visible attribute a rule reads, if any (a cane by default), and its level."""
    for name, level in (("mobility_aid", "cane"), ("load", "large_suitcase"), ("distraction", "phone")):
        if f"other_{name}" in factors or f"own_{name}" in factors:
            return f"agent.{name}", level
    return "agent.mobility_aid", "cane"


def _own(field: str, value: Any, then: dict[str, Any]) -> dict[str, Any]:
    return {"when": {"field": field, "op": "==", "value": value}, "then": then}


def translate_rehearsal_v2(request: LLMRequest) -> Optional[str]:
    user = "\n".join(m["content"] for m in request.messages if m["role"] == "user")
    found = _RULE.search(user)
    if found is None:
        return "I could not find the rule."
    block = _FACTORS.search(user)
    factors = _FACTOR.findall(block.group(1)) if block else []
    path = path_of_v4(found.group(1))
    lost = [{"part": item["column"], "kind": "condition", "how": "left_out"} for item in factor_losses(factors, 4) if item["status"] in LOST_STATUSES]
    retried = any(m["role"] == "assistant" for m in request.messages)
    if path == "valid_after_retry" and not retried:
        return "Here is the rule: the one who sees a cane steps aside."
    field, level = _seen(factors)
    condition_steps = _head_on(_by_condition(field, level, ["seen", "gives_way"]),
                               {"seen": {"responsibility_share": 0.0}, "gives_way": {"responsibility_share": 1.0, "steps": _SIDESTEP}})
    rules = {
        "valid_condition_steps": condition_steps,
        "valid_after_retry": condition_steps,
        "valid_own_when": _head_on("symmetric", {"both": {"own_when": _own("self.assertiveness", "gives_way", {"speed_scale": 0.8, "steps": _SIDESTEP})}}),
        "valid_own_attractiveness": _head_on("symmetric", {"both": {"own_when": _own("self.finds_other_attractive", True, {"clearance_margin": 0.1})}}),
        "own_only_scope": _head_on("symmetric", {"both": {"own_when": _own("self.assertiveness", "gives_way", {"side_preference": "left"})}}),
        "protected_attractiveness": _head_on("symmetric", {"both": {"speed_scale": 0.9}}, [{"field": "either.finds_other_attractive", "op": "==", "value": True}]),
        "protected_attribute": _head_on("symmetric", {"both": {"speed_scale": 0.9}}, [{"field": "either.ethnicity", "op": "==", "value": "chinese"}]),
        "no_rule": None,
        "schema_error": _head_on("symmetric", {"both": {"steps": [{"turn": {"to": "left", "degrees": 120}, "until": "other_passes"}]}}),
    }
    if path == "no_rule":
        lost.append({"part": found.group(1), "kind": "other", "how": "left_out"})
    return "```json\n" + json.dumps({"rule": rules[path], "lost": lost, "note": f"mock path {path}"}) + "\n```"


POLICIES = {"translate_rehearsal_v1": translate_rehearsal_v1, "translate_rehearsal_v2": translate_rehearsal_v2}
