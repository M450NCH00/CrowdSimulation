"""The mock extractor (issue #66, task 8): a deterministic stand-in for the model, for rehearsals.

``extract_rehearsal_v1`` reads the main table out of the prompt and answers with rules in the
reply format, in a ``yaml`` fence. It does not imitate a model; it exercises every path:

- a rule in every run: each person's commonest first side (``predict`` with a default only);
- a rule in some runs, by the sample shown: slowing when the other is seen with a load (a
  branch), so that matching across runs finds it 1, 2 or 3 times;
- a rule that reads ethnicity in some runs (``protected_attribute``, never stored);
- a rule that reads ``signalled``, when the table has signals (``needs_communication``).

Which runs get the varying rules depends only on the sessions sampled, so a mock run is exactly
reproducible.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from collections import Counter
from typing import Any, Optional

import yaml

from ..llm.base import LLMRequest

_TABLE = re.compile(r"RESOLVED SESSIONS, ONE ROW PER PERSON[^\n]*\n```csv\n(.*?)\n```", re.DOTALL)
_SAMPLED = re.compile(r"^Session (S\d+) ", re.MULTILINE)


def _commonest(values: list[str], fallback: str) -> str:
    counts = Counter(value for value in values if value)
    if not counts:
        return fallback
    best = max(counts.values())
    return sorted(value for value, count in counts.items() if count == best)[0]


def _rule(text: str, target: str, default: str, branches: list[dict[str, Any]], factors: list[str], communication: bool) -> dict[str, Any]:
    return {
        "rule": text,
        "applies_when": "the two people meet",
        "action": text,
        "exceptions": ["the failed sessions where both turned towards the same wall"],
        "factors_used": factors,
        "needs_communication": communication,
        "references": "no known source",
        "debrief_support": {"share": 0.5, "note": "mock"},
        "coverage": "mock",
        "predict": {"target": target, "if": branches, "default": default},
    }


def extract_rehearsal_v1(request: LLMRequest) -> Optional[str]:
    user = "\n".join(m["content"] for m in request.messages if m["role"] == "user")
    found = _TABLE.search(user)
    if found is None:
        return "I could not find the table."
    rows = list(csv.DictReader(io.StringIO(found.group(1))))
    sampled = _SAMPLED.findall(user)
    digest = int(hashlib.sha256(" ".join(sampled).encode("utf-8")).hexdigest(), 16)
    side = _commonest([row.get("first_side", "") for row in rows], "none")
    rules = [_rule(f"Each person turns to their own {side}.", "first_side", side, [], ["condition"], False)]
    if digest % 3 != 0:
        loaded = [row.get("first_slowed", "") for row in rows if row.get("other_load") == "large_suitcase"]
        rules.append(_rule(
            "A person who sees the other pulling a large suitcase slows down.", "first_slowed",
            _commonest([row.get("first_slowed", "") for row in rows], "no"),
            [{"when": {"other_load": "large_suitcase"}, "then": _commonest(loaded, "yes")}], ["other_load"], False,
        ))
    if digest % 2 == 0:
        rules.append(_rule(
            "People pass on the side their group prefers.", "passing_side", "right",
            [{"when": {"other_ethnicity": "malay"}, "then": "left"}], ["other_ethnicity"], False,
        ))
    if any(row.get("signalled") == "yes" for row in rows):
        rules.append(_rule(
            "A person who signals goes first.", "passed_first",
            _commonest([row.get("passed_first", "") for row in rows], "together"),
            [{"when": {"signalled": "yes"}, "then": "yes"}], ["signalled"], True,
        ))
    return "```yaml\n" + yaml.safe_dump({"rules": rules}, sort_keys=False, allow_unicode=True) + "```"


POLICIES = {"extract_rehearsal_v1": extract_rehearsal_v1}
