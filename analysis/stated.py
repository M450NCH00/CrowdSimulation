"""Stated against measured (issue #63, RF-8, task 9).

What the agents *said* drove them, beside what the factor analysis shows *did*:

- **named in the private reason**: per factor, the share of readable decision points whose
  ``reason`` names it (``codebooks/reasons_v<n>.json``, keywords, no LLM), and the share of
  agents that named it at least once;
- **the debrief's kind** (``docs/resolution.md``, D8): how often each kind of basis was given,
  per condition.

**Measured** is taken from the per-agent models of all conditions together (condition as a
factor): a factor has a measured effect when any of its terms, on any per-agent outcome, is
significant after Holm's correction. A factor named in at least ``named_often`` of the reasons
counts as often named. The two disagreeing, in either direction, is a finding in itself, and is
listed.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, Sequence

import pandas as pd

from .effects import ALL, OK, Fitted

CODEBOOKS = Path(__file__).resolve().parent / "codebooks"
REASONS_CODEBOOK = "reasons_v1"
NAMED_OFTEN = 0.10
DEBRIEF_KINDS = ("law_or_guidance", "published_study", "local_custom", "habit", "common_sense", "none")

NAMED_AND_MEASURED = "named often, and a measured effect"
NAMED_NOT_MEASURED = "named often, no measured effect"
MEASURED_NOT_NAMED = "a measured effect, rarely named"
NEITHER = "neither"
NOT_VARIED = "not varied in this data"


@lru_cache(maxsize=None)
def load_codebook(name: str = REASONS_CODEBOOK) -> dict[str, Any]:
    data = json.loads((CODEBOOKS / f"{name}.json").read_text(encoding="utf-8"))
    if data.get("codebook") != "reasons":
        raise ValueError(f"{name}: not a reasons codebook")
    return data


def mentions(decisions: Optional[pd.DataFrame], codebook_name: str = REASONS_CODEBOOK) -> pd.DataFrame:
    """Per factor: readable reasons, how many name it and the share; agents, how many named it
    at least once and the share."""
    factors = load_codebook(codebook_name)["factors"]
    columns = ["factor", "reasons", "naming", "share_of_reasons", "agents", "agents_naming", "share_of_agents"]
    if decisions is None or decisions.empty:
        return pd.DataFrame(columns=columns)
    readable = decisions.loc[decisions["reason"].map(lambda r: isinstance(r, str) and r.strip() != "")]
    agent_of = readable["session_key"].astype(str) + "#" + readable["agent_id"].astype(str)
    agents = agent_of.nunique()
    rows = []
    for factor, patterns in factors.items():
        named = readable["reason"].map(lambda text: any(re.search(p, text, re.IGNORECASE) for p in patterns))
        k = int(named.sum())
        by_agent = int(agent_of[named].nunique())
        rows.append({"factor": factor, "reasons": len(readable), "naming": k, "share_of_reasons": k / len(readable) if len(readable) else float("nan"),
                     "agents": agents, "agents_naming": by_agent, "share_of_agents": by_agent / agents if agents else float("nan")})
    return pd.DataFrame(rows, columns=columns)


def debrief_kinds(agents: pd.DataFrame) -> pd.DataFrame:
    """How often each kind of basis was given in the debriefs, per condition and in all (one per
    prompted agent; a missing debrief is ``(none given)``)."""
    kinds = agents["debrief_kind"].astype("string").fillna("(none given)")
    table = pd.crosstab(kinds, agents["condition"], margins=True, margins_name="all")
    order = [k for k in (*DEBRIEF_KINDS, "(none given)") if k in table.index] + sorted(set(table.index) - set(DEBRIEF_KINDS) - {"(none given)", "all"}) + ["all"]
    return table.loc[order]


def stated_against_measured(named: pd.DataFrame, fitted: Sequence[Fitted], varied_factors: Sequence[str], named_often: float = NAMED_OFTEN) -> pd.DataFrame:
    """Per factor: how often it was named, its strongest measured effect (the smallest Holm
    p-value among its terms in the pooled per-agent models), and the verdict."""
    terms = [t for m in fitted if m.level == "agent" and m.subset == ALL and m.status == OK for t in m.terms]
    factors = list(dict.fromkeys([*named["factor"], *varied_factors]))
    rows = []
    for factor in factors:
        share = named.loc[named["factor"] == factor, "share_of_reasons"]
        share = float(share.iloc[0]) if len(share) else float("nan")
        mine = [t for t in terms if t["factor"] == factor]
        best = min(mine, key=lambda t: t["p_holm"]) if mine else None
        effect = any(t["significant"] for t in mine)
        often = share >= named_often if share == share else False
        if factor not in varied_factors:
            verdict = NOT_VARIED
        elif often and effect:
            verdict = NAMED_AND_MEASURED
        elif often:
            verdict = NAMED_NOT_MEASURED
        elif effect:
            verdict = MEASURED_NOT_NAMED
        else:
            verdict = NEITHER
        rows.append({
            "factor": factor, "share_of_reasons": share, "measured_effect": effect if factor in varied_factors else None,
            "strongest_outcome": best["outcome"] if best else None, "strongest_term": best["term"] if best else None,
            "strongest_estimate": best.get("odds_ratio", best["estimate"]) if best else None,
            "strongest_p_holm": best["p_holm"] if best else None, "verdict": verdict,
        })
    return pd.DataFrame(rows)
