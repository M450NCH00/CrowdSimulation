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

**One closing brace short** (issue #108, the user's decision of 2026-10-26; only where a config asks,
``reader.repair_one_brace``). A reply that is not JSON, and outside its strings has exactly one more
``{`` than ``}``, is tried with one ``}`` inserted at every place one can go (before each ``,``, ``}``
or ``]``, and at the end). It is repaired only if **exactly one** placement gives a reply that reads
and whose rule the caller accepts (the experiment: the loader reads it whole, ``accepts_structure``); the record
keeps the raw reply and says where the brace went (:func:`repair_one_brace`). Otherwise it stays
unreadable. RF-31's translation of ``x_head_on_6455ca5589`` left a nested own-only condition unclosed
in both its replies; appending the brace at the end would have given a different, wrong structure.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

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


def _brace_balance(text: str) -> int:
    """``{`` minus ``}`` outside JSON strings."""
    depth, inside, escaped = 0, False, False
    for char in text:
        if inside:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                inside = False
        elif char == '"':
            inside = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
    return depth


@dataclass(frozen=True)
class Repair:
    """A reply read after one ``}`` was inserted: where, and how many placements were tried and accepted."""

    translation: Translation
    inserted_at: int
    placements_tried: int
    placements_accepted: int

    def as_dict(self) -> dict[str, Any]:
        return {"kind": "one_closing_brace", "inserted_at": self.inserted_at, "placements_tried": self.placements_tried,
                "placements_accepted": self.placements_accepted}


def repair_one_brace(raw: Optional[str], accept: Callable[[Translation], bool]) -> Optional[Repair]:
    """The one reading of ``raw`` with a single ``}`` inserted that reads and that ``accept`` takes, or
    ``None`` (none, or more than one): see the module docstring."""
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        text = text.rsplit("```", 1)[0]
    try:
        json.loads(text)
        return None  # it reads already: nothing to repair
    except json.JSONDecodeError:
        pass
    if _brace_balance(text) != 1:
        return None
    places = [index for index, char in enumerate(text) if char in ",}]"] + [len(text.rstrip())]
    accepted: dict[str, tuple[int, Translation]] = {}
    for index in places:
        candidate = text[:index] + "}" + text[index:]
        try:
            translation = parse_translation(candidate)
        except TurnParseError:
            continue
        if accept(translation):
            accepted.setdefault(json.dumps(translation.as_dict(), sort_keys=True), (index, translation))
    if len(accepted) != 1:
        return None
    ((index, translation),) = accepted.values()
    return Repair(translation, index, len(places), len(accepted))
