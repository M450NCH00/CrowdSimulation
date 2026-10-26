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


POLICIES = {"translate_rehearsal_v1": translate_rehearsal_v1}
