"""Reading the translator's reply (issue #67, RF-12).

A JSON object with ``rule`` (a format 3 rule, or null when no part of the extracted rule can be
written), ``lost`` (a list of the parts left out or approximated) and ``note`` (text). Read with
rule generation's tolerances (``negsim.rulegen.protocol``): whitespace, a code fence, extra keys.
Not read, and asked again once: a reply that is not a JSON object, no ``rule``, a ``rule`` that is
neither an object nor null, a ``lost`` that is not a list of objects each with a ``part`` in text,
a ``note`` that is not text. A missing ``lost`` is an empty list, a missing ``note`` empty.

A part's ``kind`` and ``how`` are kept as written; one outside :data:`LOST_KINDS` is counted under
``other`` (``kind_as_written`` keeps the model's word), and a ``how`` outside :data:`LOST_HOW` is
``None``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from ..negotiation.parsing import TurnParseError
from ..rulegen.protocol import _object

#: The kinds of part the template lists, in its order.
LOST_KINDS = ("condition", "start", "turn", "speed", "duration", "signal_or_talk", "other")
LOST_HOW = ("left_out", "approximated")


@dataclass(frozen=True)
class Translation:
    rule: Optional[dict[str, Any]]
    lost: list[dict[str, Any]] = field(default_factory=list)
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {"rule": self.rule, "lost": [dict(item) for item in self.lost], "note": self.note}


def _part(item: Any, index: int) -> dict[str, Any]:
    if not isinstance(item, dict) or not isinstance(item.get("part"), str) or not item["part"].strip():
        raise TurnParseError("lost_item_malformed", f"lost[{index}] is not an object with a part in text")
    kind = item.get("kind")
    out: dict[str, Any] = {"part": " ".join(item["part"].split()), "kind": kind if kind in LOST_KINDS else "other"}
    if kind not in LOST_KINDS:
        out["kind_as_written"] = kind
    how = item.get("how")
    out["how"] = how if how in LOST_HOW else None
    return out


def parse_translation(raw: Optional[str]) -> Translation:
    """Read a translator's reply, or raise :class:`TurnParseError`."""
    data = _object(raw)
    if "rule" not in data:
        raise TurnParseError("missing_rule")
    rule = data["rule"]
    if rule is not None and not isinstance(rule, dict):
        raise TurnParseError("rule_not_an_object", f"got {type(rule).__name__}")
    lost = data.get("lost")
    if lost is None:
        lost = []
    if not isinstance(lost, list):
        raise TurnParseError("lost_not_a_list", f"got {type(lost).__name__}")
    note = data.get("note")
    if note is None:
        note = ""
    if not isinstance(note, str):
        raise TurnParseError("note_not_text", f"got {type(note).__name__}")
    return Translation(rule, [_part(item, index) for index, item in enumerate(lost)], " ".join(note.split()))
