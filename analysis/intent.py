"""The intent codebook and the intent-against-plan check (issue #63, RF-8, task 10).

**Coding the intent.** The free-text ``intent`` of each readable reply is coded into strategy
categories (keep to a side, slow down, stop and wait, back up, carry on, or ``other``) by the
keyword codebook ``codebooks/intent_v<n>.json``, with no LLM. The codebook is versioned and
committed; a change is a new version. An intent the codebook cannot place is ``other``.

**Coding the plan.** The plan is the decision point's ``coded`` record (negsim's ``code_plan``,
from ``steps``): a turn is keep to a side (on its side), a speed below the current one is slow
down, a speed of 0 is stop and wait, ``back_up_m`` is back up, and no steps, or steps that do
none of these, is carry on.

**A mismatch** is an intent that says something the plan does not do: a category of the intent
missing from the plan's, or a side the intent names that the plan does not turn to (a plan that
turns both ways covers either). A plan that does more than its intent says is not a mismatch.
Intents coded ``other`` and unreadable replies are counted but left out of the rate.

**Why it matters:** a high mismatch rate means the structured plan cannot be trusted on its own,
which the rule extractor (RF-11) needs to know.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Optional

import pandas as pd

from .noise import wilson

CODEBOOKS = Path(__file__).resolve().parent / "codebooks"
INTENT_CODEBOOK = "intent_v1"
CATEGORIES = ("keep_to_side", "slow_down", "stop_and_wait", "back_up", "carry_on")
OTHER, CARRY_ON = "other", "carry_on"
MATCH, MISMATCH, UNCODED, UNREADABLE = "match", "mismatch", "uncoded", "unreadable"


@lru_cache(maxsize=None)
def load_codebook(name: str = INTENT_CODEBOOK) -> dict[str, Any]:
    data = json.loads((CODEBOOKS / f"{name}.json").read_text(encoding="utf-8"))
    if data.get("codebook") != "intent" or list(data["categories"]) != list(CATEGORIES):
        raise ValueError(f"{name}: not an intent codebook with the categories {CATEGORIES}")
    return data


def _any(patterns, text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def code_intent(text: Optional[str], codebook: Mapping[str, Any]) -> tuple[frozenset[str], Optional[str]]:
    """The intent's categories (``{other}`` when none matches) and the side it names, if one:
    ``left``, ``right``, or ``None`` (none, both, or said of the other person)."""
    text = (text or "").strip()
    found = {name for name, patterns in codebook["categories"].items() if _any(patterns, text)}
    if found - {CARRY_ON}:
        found.discard(CARRY_ON)
    side = None
    if not _any(codebook["side"]["unknown_when"], text):
        left, right = _any(codebook["side"]["left"], text), _any(codebook["side"]["right"], text)
        side = "left" if left and not right else "right" if right and not left else None
    return (frozenset(found) or frozenset({OTHER})), side


def code_plan(coded: Optional[Mapping[str, Any]]) -> tuple[frozenset[str], str]:
    """The plan's categories and its side (``left``, ``right``, ``both`` or ``none``)."""
    coded = coded or {}
    side = coded.get("side") or "none"
    found = set()
    if side in ("left", "right", "both"):
        found.add("keep_to_side")
    if coded.get("slowed"):
        found.add("slow_down")
    if coded.get("stopped"):
        found.add("stop_and_wait")
    if coded.get("backed_up"):
        found.add("back_up")
    return frozenset(found or {CARRY_ON}), side


def check(decisions: pd.DataFrame, codebook_name: str = INTENT_CODEBOOK) -> pd.DataFrame:
    """One row per decision point: the coded intent, the coded plan, and match or mismatch."""
    codebook = load_codebook(codebook_name)
    rows = []
    for record in decisions.to_dict("records"):
        entry = {"session_key": record["session_key"], "session_id": record["session_id"], "agent_id": record["agent_id"],
                 "number": record.get("number"), "condition": record["condition"], "intent": record.get("intent")}
        error = record.get("parse_error")  # missing values come back from a frame as NaN, which is truthy
        if (isinstance(error, str) and error) or not isinstance(record.get("intent"), str) or not isinstance(record.get("coded"), dict):
            rows.append({**entry, "status": UNREADABLE})
            continue
        said, said_side = code_intent(record["intent"], codebook)
        done, done_side = code_plan(record["coded"])
        entry.update({"intent_categories": ";".join(sorted(said)), "intent_side": said_side,
                      "plan_categories": ";".join(sorted(done)), "plan_side": done_side})
        if said == {OTHER}:
            rows.append({**entry, "status": UNCODED, "why": ""})
            continue
        missing = sorted(said - done)
        wrong_side = said_side is not None and done_side not in (said_side, "both")
        why = [f"intent says {name}, the plan does not" for name in missing]
        if wrong_side:
            why.append(f"intent says {said_side}, the plan turns {done_side}")
        rows.append({**entry, "status": MISMATCH if why else MATCH, "why": "; ".join(why)})
    return pd.DataFrame(rows)


def summary(checked: pd.DataFrame) -> pd.DataFrame:
    """Per condition and in all: decision points, unreadable, uncoded, compared, mismatches, and
    the mismatch rate with a Wilson 95% interval."""
    out = []
    groups = [("all", checked)] + [(condition, part) for condition, part in checked.groupby("condition", sort=True)]
    for subset, part in groups:
        compared = part.loc[part["status"].isin([MATCH, MISMATCH])]
        k, n = int((compared["status"] == MISMATCH).sum()), len(compared)
        low, high = wilson(k, n)
        out.append({"subset": subset, "decision_points": len(part), "unreadable": int((part["status"] == UNREADABLE).sum()),
                    "uncoded": int((part["status"] == UNCODED).sum()), "compared": n, "mismatches": k,
                    "rate": k / n if n else float("nan"), "ci_low": low, "ci_high": high})
    return pd.DataFrame(out)
