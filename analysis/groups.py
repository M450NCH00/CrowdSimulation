"""Real ethnicity: per-group outcomes and population-weighted figures (issue #92, RF-26).

Two tables, each only when the outcome rows carry real ethnicity:

- **By group** (:func:`by_group`): per agent, by its own group and the other's group **as told**
  (``not told`` where the other's line never reached it), the number of agent rows and the share
  with each binary agent outcome. Unweighted: this is the comparison between groups that a
  ``balanced`` draw gives enough rows for. Descriptive only: Holm's correction and the factor
  models are elsewhere (``effects.py``), where the design's ``same_ethnicity`` is a predictor.
- **Weighted** (:func:`weighted`): each session outcome, unweighted and weighted by the session's
  ``ethnicity_weight``, which makes the sessions stand for two residents of Singapore met at
  random (``llm_negotiation/negsim/resolution/ethnicity.py``, :func:`weights`). With Kish's
  effective number of sessions, (sum w)^2 / sum w^2: what the weighting costs in precision.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .factors import ETHNICITY_GROUPS
from .load import AGENT_OUTCOMES, SESSION_OUTCOMES

NOT_TOLD = "not told"


def by_group(agents: pd.DataFrame) -> pd.DataFrame | None:
    """Agent rows by (own group, the other's group as told), with each binary outcome's share."""
    if "own_ethnicity" not in agents.columns:
        return None
    frame = agents.assign(other_told=agents["other_ethnicity"].fillna(NOT_TOLD))
    outcomes = [o.name for o in AGENT_OUTCOMES if o.kind == "binary" and o.name in frame.columns]
    rows = []
    order = [*ETHNICITY_GROUPS, NOT_TOLD]
    for own in ETHNICITY_GROUPS:
        for other in order:
            mine = frame.loc[(frame["own_ethnicity"] == own) & (frame["other_told"] == other)]
            if mine.empty:
                continue
            row = {"own": own, "other_as_told": other, "n": len(mine)}
            for name in outcomes:
                values = pd.to_numeric(mine[name], errors="coerce").dropna()
                row[name] = float(values.mean()) if len(values) else np.nan
                row[f"{name}_n"] = len(values)
            rows.append(row)
    return pd.DataFrame(rows)


def weighted(sessions: pd.DataFrame) -> pd.DataFrame | None:
    """Each session outcome's rate, unweighted and weighted back to random resident pairs."""
    if "ethnicity_weight" not in sessions.columns or sessions["ethnicity_weight"].isna().all():
        return None
    rows = []
    for outcome in SESSION_OUTCOMES:
        if outcome.name not in sessions.columns or outcome.kind != "binary":
            continue
        values = pd.to_numeric(sessions[outcome.name], errors="coerce")
        w = pd.to_numeric(sessions["ethnicity_weight"], errors="coerce")
        kept = values.notna() & w.notna()
        if not kept.any():
            continue
        x, wk = values[kept].astype(float), w[kept].astype(float)
        rows.append({
            "outcome": outcome.name, "sessions": int(kept.sum()), "unweighted": float(x.mean()),
            "weighted": float((x * wk).sum() / wk.sum()) if wk.sum() > 0 else np.nan,
            "effective_sessions": float(wk.sum() ** 2 / (wk ** 2).sum()) if (wk ** 2).sum() > 0 else np.nan,
        })
    return pd.DataFrame(rows)
