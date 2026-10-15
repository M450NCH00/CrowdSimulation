"""The canonical form of a rule, and its hash: when two rules are the same rule.

``docs/rule-format.md``, section 13, is the definition; issue #30 uses it for agreement in
negotiation (an agent accepts the other's proposal by its hash) and for storing a rule once
whatever number of sessions produced it, and SI-4 will reuse it.

The canonical form keeps what a rule *does* (``encounter``, ``when``, ``roles``,
``directive``, and ``expiry`` if stated) and drops its metadata. Keys are sorted at every
depth and numbers are normalised (a whole number is an integer; any other number keeps 12
significant digits). Nothing else is changed: no unit is converted, no list reordered, no
field at its baseline value removed. That is a deliberately narrow notion of "the same";
semantic equivalence is SI-4's.

It works on anything shaped like a rule, valid or not, so that a proposal the loader would
refuse can still be accepted, counted and compared.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping

#: The keys of a rule that say what it does, in the order the documentation gives them.
CANONICAL_KEYS = ("encounter", "when", "roles", "directive", "expiry")
#: How many hexadecimal characters of the hash an agent is shown and writes back.
PROPOSAL_ID_LENGTH = 12
SIGNIFICANT_DIGITS = 12


def normalise_number(value: Any) -> Any:
    """A number written one way whatever way it came: 6, 6.0 and 6.00 are all 6."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    if isinstance(value, int) or not math.isfinite(value):
        return value
    rounded = float(f"{value:.{SIGNIFICANT_DIGITS}g}")
    return int(rounded) if rounded.is_integer() else rounded


def canonical_value(value: Any) -> Any:
    """``value`` with its keys sorted and its numbers normalised, at every depth."""
    if isinstance(value, Mapping):
        return {str(key): canonical_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [canonical_value(item) for item in value]
    return normalise_number(value)


def canonical_form(rule: Mapping[str, Any]) -> dict[str, Any]:
    """The parts of ``rule`` that say what it does, canonicalised."""
    if not isinstance(rule, Mapping):
        raise TypeError(f"a rule is a mapping, got {type(rule).__name__}")
    return {key: canonical_value(rule[key]) for key in CANONICAL_KEYS if key in rule}


def canonical_json(rule: Mapping[str, Any]) -> str:
    """The canonical form as compact JSON with sorted keys: what is hashed."""
    return json.dumps(canonical_form(rule), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(rule: Mapping[str, Any]) -> str:
    """SHA-256 of the canonical JSON, 64 hexadecimal characters."""
    return hashlib.sha256(canonical_json(rule).encode("utf-8")).hexdigest()


def proposal_id(rule: Mapping[str, Any]) -> str:
    """The first characters of the canonical hash: how a proposal is named to the agents."""
    return canonical_hash(rule)[:PROPOSAL_ID_LENGTH]
