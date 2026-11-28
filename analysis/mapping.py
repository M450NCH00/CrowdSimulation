"""The factor-to-decision mapping (issue #63, RF-8, task 8).

Every factor combination observed, from an agent's point of view (its own factors and the other's
as it was told them, the geometry), per condition, with how many rows it has and, per outcome,
how many of them are known and the share that are 1. This is the lookup table that would let a
large simulation skip the LLM (``literature/trained-deciders/verdict.md``, point 2); the decision
tree is its compressed form. A combination seen once gives a share of 0 or 1 from one row: read
the counts with the shares.
"""

from __future__ import annotations

from typing import Sequence

import pandas as pd

from .load import AGENT_OUTCOMES

MAPPED = tuple(o.name for o in AGENT_OUTCOMES if o.kind == "binary")


def mapping_table(agents: pd.DataFrame, factors: Sequence[str]) -> pd.DataFrame:
    keys = ["condition", *factors]
    rows = []
    for values, part in agents.groupby(keys, sort=True, dropna=False):
        entry = dict(zip(keys, values if isinstance(values, tuple) else (values,)))
        entry["rows"] = len(part)
        for name in MAPPED:
            known = part[name].dropna()
            entry[f"n_{name}"] = len(known)
            entry[f"p_{name}"] = float(known.mean()) if len(known) else float("nan")
        rows.append(entry)
    table = pd.DataFrame(rows)
    for factor in factors:
        if pd.api.types.is_float_dtype(table[factor]):
            table[factor] = table[factor].astype(int)
    return table
