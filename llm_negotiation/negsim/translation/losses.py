"""What rule format 3 cannot say of an extracted rule, told mechanically (issue #67, RF-12, task 3).

The translator lists what it left out or approximated (``negsim.translation.reply``). Beside that
list, and independent of the model, two checks read the extracted rule itself:

**The factors.** Each column an extracted rule names in ``factors_used`` (RF-11's agent table,
``negsim.extraction.table``) is mapped to the format 3 field that reads it, or to why none does:

| Status | Meaning |
| --- | --- |
| ``readable`` | a format 3 field reads it (``age``, ``gender``; the distance at which a person decided is ``pair.distance_m`` in a condition) |
| ``unobservable`` | only the person knows it (assertiveness, residence, a memory, urgency): the loader refuses such a field as ``unobservable_field`` (``rule-format.md``, section 5) |
| ``no_field`` | people can see or know it, but format 3 has no field for it (a cane, a suitcase, a phone, whether the two know each other, the layout, the surroundings, the time of day, how many decisions a person made) |
| ``communication`` | a signal, words, or the condition that allowed them (D9) |
| ``protected`` | ethnicity or perceived attractiveness, which no rule may read |
| ``behaviour`` | what a person did or what happened (a side, slowing, stopping, the outcome): what the directive has to say, not a condition |
| ``label`` | a label of the table (row, session, person), not a factor |
| ``unknown`` | not a column of the table |

**The action's words.** The extracted rule's ``rule`` and ``action`` are searched for what format
3 has no directive for: a turn by an angle, a turn or a step aside at all (a side preference says
only which side), a start distance or moment, a duration or "until", a walking speed (a speed
scale can only approximate it), stopping or backing up (format 3 backs up only inside a
single-file stretch), and a signal or words. These are flags, read from words, for comparison with
the translator's own list; they never change a rule's category.

**Rule format 4** (issue #108, RF-31) reads more, and says more. A cane, a suitcase and a phone,
the person's own or the other's, are ``readable`` (``agent.`` in a role by a condition,
``either.``/``both.`` in a condition); a person's own private factors (assertiveness, urgency,
residence, a memory) and their own view of the other (whether they know them, whether they find
them attractive) are ``readable`` as ``self.`` fields in that person's own-only condition. The
layout, the surroundings, the time of day and how many decisions a person made still have no
field; signals and words are still ``communication``; ethnicity is still ``protected``. Of the
action's words, only a signal or words is beyond format 4's directives: a start, a speed, a turn
or step aside, a duration, stopping and backing up are steps. ``schema_version`` chooses the map.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

from ..extraction.table import (
    COLUMNS,
    DECISION_COLUMNS,
    MARK_COLUMNS,
    OBSERVABLE,
    OUTCOME_COLUMNS,
    PAIRWISE,
    PERSON,
    PROTECTED_COLUMNS,
    SITUATIONS,
)

READABLE, UNOBSERVABLE, NO_FIELD, COMMUNICATION, PROTECTED, BEHAVIOUR, LABEL, UNKNOWN = (
    "readable", "unobservable", "no_field", "communication", "protected", "behaviour", "label", "unknown",
)
STATUSES = (READABLE, UNOBSERVABLE, NO_FIELD, COMMUNICATION, PROTECTED, BEHAVIOUR, LABEL, UNKNOWN)
#: The statuses of a factor that a format 3 rule cannot read as a condition.
LOST_STATUSES = (UNOBSERVABLE, NO_FIELD, COMMUNICATION, PROTECTED)


def _column_fields() -> dict[str, tuple[str, str]]:
    """Every column of RF-11's agent table: its status, and the format 3 field or the reason."""
    out: dict[str, tuple[str, str]] = {name: (LABEL, "a label of the table") for name in ("row", "session", "person")}
    out["condition"] = (COMMUNICATION, "whether the two could signal or talk")
    out["geometry"] = (NO_FIELD, "the layout (how far apart the two walking lines are): no format 3 field")
    for side in ("own", "other"):
        out[f"{side}_age"] = (READABLE, "age (either., both., agent.; pair.age_difference_years)")
        out[f"{side}_gender"] = (READABLE, "gender (either., both.)")
        out[f"{side}_ethnicity"] = (PROTECTED, "ethnicity: no rule may read it")
    for name in PERSON:
        seen = name in OBSERVABLE
        out[f"own_{name}"] = (NO_FIELD, f"{name}: no format 3 field") if seen else (UNOBSERVABLE, f"{name}: only the person knows it")
        if seen:
            out[f"other_{name}"] = (NO_FIELD, f"{name}: no format 3 field")
    for name in SITUATIONS:
        out[name] = (NO_FIELD, f"{name}: no format 3 field")
    for name in PAIRWISE:
        out[name] = (PROTECTED, "perceived attractiveness: no rule may read it") if name in PROTECTED_COLUMNS else (NO_FIELD, f"{name}: no format 3 field")
    for name in (*DECISION_COLUMNS, *OUTCOME_COLUMNS, *MARK_COLUMNS):
        out[name] = (BEHAVIOUR, "what a person did or what happened")
    out["decision_points"] = (NO_FIELD, "how many decisions a person made: no format 3 field")
    out["first_decision_distance_m"] = (READABLE, "pair.distance_m, in a condition")
    out["signalled"] = (COMMUNICATION, "a signal")
    out["spoke"] = (COMMUNICATION, "words")
    missing = [name for name in COLUMNS if name not in out]
    assert not missing, f"columns with no status: {missing}"
    return out


#: RF-11's table columns, each with its status and the format 3 field that reads it, or why none does.
COLUMN_FIELDS = _column_fields()


def _column_fields_v4() -> dict[str, tuple[str, str]]:
    """The same, for rule format 4 (issue #108): what it made readable, and nothing else changed."""
    out = dict(COLUMN_FIELDS)
    for name in PERSON:
        if name in OBSERVABLE:
            for side in ("own", "other"):
                out[f"{side}_{name}"] = (READABLE, f"{name} (agent. in a role by a condition; either., both. in a condition)")
        else:
            out[f"own_{name}"] = (READABLE, f"self.{name}, in the person's own-only condition")
    for name in PAIRWISE:
        out[name] = (READABLE, f"self.{name}, in the person's own-only condition (their own view of the other)")
    return out


#: RF-11's table columns for rule format 4 (issue #108).
COLUMN_FIELDS_V4 = _column_fields_v4()


def column_fields(schema_version: int = 3) -> dict[str, tuple[str, str]]:
    return COLUMN_FIELDS_V4 if schema_version >= 4 else COLUMN_FIELDS


def factor_losses(factors_used: Any, schema_version: int = 3) -> list[dict[str, str]]:
    """Each column the extracted rule names, with its status and field (or reason), in its order,
    for rule format ``schema_version`` (3 unless said)."""
    names = factors_used if isinstance(factors_used, list) else [factors_used] if factors_used else []
    table = column_fields(schema_version)
    out = []
    for name in names:
        status, field = table.get(str(name), (UNKNOWN, "not a column of the table"))
        out.append({"column": str(name), "status": status, "field": field})
    return out


#: The action's words that format 3 has no directive for, each with the name its flag is counted under.
ACTION_PATTERNS = (
    ("turn_angle", re.compile(r"\d+(\.\d+)?\s*((to|-|–)\s*\d+(\.\d+)?\s*)?(°|deg\b|degrees?\b)")),
    ("turn_or_step_aside", re.compile(r"\b(turn\w*|veer\w*|swerv\w*|sidestep\w*|step\w* (aside|to|over)|steer\w*|weav\w*)\b")),
    ("start", re.compile(r"\b(from|at|within)\s+(about\s+|around\s+)?\d+(\.\d+)?(\s*(to|-|–)\s*\d+(\.\d+)?)?\s*m\b|\b(first (decision|plan)|close range|when close|only when close|early|late)\b")),
    ("duration", re.compile(r"\b(until|wait\w*|held|for \d+(\.\d+)?\s*s)\b")),
    ("speed_value", re.compile(r"\d+(\.\d+)?\s*((to|-|–)\s*\d+(\.\d+)?\s*)?m/s")),
    ("stop_or_back_up", re.compile(r"\b(stop\w*|back(s|ed|ing)? up|backing)\b")),
    ("signal_or_talk", re.compile(r"\b(signal\w*|nod\w*|wave\w*|waving|eye contact|speak\w*|spoke|say\w*|said|talk\w*|utter\w*|greet\w*|excuse)\b")),
)
FLAGS = tuple(name for name, _ in ACTION_PATTERNS)
#: The flags that rule format 4 still has no directive for (issue #108): the rest are steps.
FLAGS_BEYOND_V4 = ("signal_or_talk",)


def action_flags(texts: Iterable[Any], schema_version: int = 3) -> list[str]:
    """The :data:`ACTION_PATTERNS` found in any of ``texts`` (the extracted rule's words) that rule
    format ``schema_version`` has no directive for: every one for format 3, a signal or words for 4."""
    lowered = " ".join(" ".join(str(text).lower().split()) for text in texts if text)
    beyond = FLAGS if schema_version < 4 else FLAGS_BEYOND_V4
    return [name for name, pattern in ACTION_PATTERNS if name in beyond and pattern.search(lowered)]


def counted(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Across rules: how many rules have each factor status, each action flag, and each kind of
    part the translator said it lost (a rule counts once per status, flag or kind)."""
    statuses: Counter = Counter()
    flags: Counter = Counter()
    kinds: Counter = Counter()
    for entry in entries:
        statuses.update({item["status"] for item in entry.get("factor_losses") or []})
        flags.update(set(entry.get("action_flags") or []))
        kinds.update({item["kind"] for item in entry.get("lost") or []})
    return {
        "rules": len(entries),
        "factor_status": {name: statuses[name] for name in STATUSES if statuses[name]},
        "action_flags": {name: flags[name] for name in FLAGS if flags[name]},
        "lost_kinds": dict(sorted(kinds.items())),
    }
