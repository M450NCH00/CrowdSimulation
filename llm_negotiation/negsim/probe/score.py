"""Score a probe's reply (issue #144, RF-53, stage 1).

The probes ask for the answer alone on the first line (``configs/probe/frames_probes_v1.yaml``,
``answer_line``). The scorer reads that line only, for one label of the probe's kind:

- ``side``: ``left``, ``right``, or ``cannot_tell`` (the answer probes 13 and 15 expect);
- ``their_side``: the side of the other person, as said to them ("your right" means their right).
  A side given as "my ..." is in the speaker's own frame, which the question rules out: ``unclear``;
- ``wall``: ``north`` or ``south``; ``named_side``: ``window`` or ``shop``; ``lane``: ``1`` to ``5``.

A first line naming both options (for example "Left (their right)") is read by the first one named
and flagged ``ambiguous``, for the hand check. A line with none is ``unclear``, as is an empty reply
(for example one cut off by the reply cap while the model was still reasoning). The scorer is plain
keyword matching, so that every score can be checked by eye.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

KINDS = ("side", "their_side", "wall", "named_side", "lane")
CANNOT_TELL, UNCLEAR, EMPTY = "cannot_tell", "unclear", "empty"
CORRECT, WRONG = "correct", "wrong"

#: Phrases that say the side cannot be known (probes 13 and 15). Checked before left and right, so
#: "cannot tell whether it is left or right" is read as cannot_tell.
CANNOT_TELL_PATTERNS = (
    r"\bcan ?not\b", r"\bcan'?t\b", r"\bcan’t\b", r"\bunknown\b", r"\bunclear\b", r"\bundetermin",
    r"\bnot (?:enough|possible|known|specified|given|stated|clear)\b", r"\bimpossible\b", r"\bdepends\b",
    r"\bneither\b", r"\bambiguous\b", r"\bno way to\b", r"\binsufficient\b", r"\bnot determinable\b",
)
WORDS = {
    "side": ("left", "right"),
    "their_side": ("left", "right"),
    "wall": ("north", "south"),
    "named_side": ("window", "shop"),
}


@dataclass(frozen=True)
class Score:
    first_line: str
    label: str
    outcome: str  # correct, wrong or unclear
    ambiguous: bool

    def as_dict(self) -> dict[str, Any]:
        return {"first_line": self.first_line, "label": self.label, "outcome": self.outcome, "ambiguous": self.ambiguous}


def first_line(content: Optional[str]) -> str:
    """The first non-empty line, without markdown emphasis, heading marks or surrounding quotes."""
    for line in (content or "").splitlines():
        cleaned = re.sub(r"[*_`#>]+", " ", line).strip().strip("\"'“”‘’").strip()
        cleaned = re.sub(r"^(?:answer|final answer)\s*[:\-–]\s*", "", cleaned, flags=re.I).strip()
        if cleaned:
            return cleaned
    return ""


def read_label(kind: str, line: str) -> tuple[str, bool]:
    """The label the line gives, and whether it named more than one option."""
    if kind not in KINDS:
        raise ValueError(f"unknown probe kind {kind!r}; expected one of {KINDS}")
    if not line:
        return EMPTY, False
    lowered = line.lower()
    if kind == "lane":
        # A lane number on its own: not part of a longer number or a decimal ("3.5"), but a full stop
        # after it ("Lane 3.") is the end of the sentence.
        found = re.findall(r"(?<![\d.])([1-5])(?!\d|\.\d)", lowered)
        return (found[0], len(set(found)) > 1) if found else (UNCLEAR, False)
    if kind == "side" and any(re.search(pattern, lowered) for pattern in CANNOT_TELL_PATTERNS):
        return CANNOT_TELL, False
    hits = sorted((match.start(), word) for word in WORDS[kind] for match in re.finditer(rf"\b{word}\b", lowered))
    if not hits:
        return UNCLEAR, False
    if kind == "their_side" and re.search(r"\bmy\s+(?:left|right)\b", lowered):
        return UNCLEAR, False
    return hits[0][1], len({word for _, word in hits}) > 1


def score(probe: Mapping[str, Any], content: Optional[str]) -> Score:
    line = first_line(content)
    label, ambiguous = read_label(probe["kind"], line)
    correct: Sequence[str] = probe["correct"]
    wrong: Sequence[str] = probe["wrong"]
    outcome = CORRECT if label in correct else WRONG if label in wrong else UNCLEAR
    return Score(line, label, outcome, ambiguous)
