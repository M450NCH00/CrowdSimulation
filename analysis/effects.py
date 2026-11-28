"""Factor effects (issue #63, RF-8, task 4).

One model per outcome and subset:

- **logistic regression** for a binary outcome, reported as odds ratios with 95% confidence
  intervals; **linear regression** for a continuous one (start distance, decision points),
  reported as coefficients;
- **main effects**, plus any named interaction (``a:b``, the product of two 0/1 columns);
- **standard errors clustered by session** for the per-agent models, because the two rows of
  one session are not independent; heteroskedasticity-robust (HC1) for the per-session models,
  which have one row per session;
- **Holm-corrected p-values** (the intercept left out). A term is reported as significant when
  its Holm p-value is below ``alpha``. By default the family is **every term of every model in
  the report** (``report``), so that the chance of even one false positive anywhere in it is at
  most ``alpha``: a screen fits some 45 models, and a family of one model would let one or two
  terms through by chance in nearly every report with no effect at all (found on synthetic data,
  ``WORK_LOG-63.md``). ``subset`` (the models of one condition, or of all together) and
  ``model`` are narrower families, for a reader who states which one they used;
- **each condition separately**, and all conditions together with condition as a factor.

A column that does not vary in a subset, or that is a linear combination of the columns before
it, is left out of that model and listed. A logistic model whose outcome is (nearly) separated
by the predictors has no finite estimate: it is reported as ``separation``, with no estimate and
no p-value, never as an effect. Statements about a factor rest on the per-term table, where each
estimate carries its interval.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.tools.sm_exceptions import ConvergenceWarning, PerfectSeparationError, PerfectSeparationWarning

from .factors import BASE_LEVEL, DESIGN_COLUMNS, factor_of
from .load import AGENT_OUTCOMES, CONDITIONS, SESSION_OUTCOMES, AnalysisError, Outcome, varied

ALPHA = 0.05
ALL = "all"
#: A logistic coefficient this large (odds ratio beyond e^10) means the outcome is separated.
SEPARATION_LOGIT = 10.0

OK, SEPARATION, NO_DATA, ONE_VALUE, FAILED = "ok", "separation", "no data", "one value", "failed"
#: Over which terms Holm's correction runs.
FAMILIES = ("report", "subset", "model")


@dataclass
class Fitted:
    outcome: str
    level: str
    subset: str
    kind: str
    status: str
    n: int
    events: Optional[int]
    clusters: Optional[int]
    dropped: list[str] = field(default_factory=list)
    terms: list[dict] = field(default_factory=list)
    note: str = ""


def dummies(series: pd.Series, name: str) -> pd.DataFrame:
    """0/1 columns ``name[level]``, one per level but the base (``factors.BASE_LEVEL``, else the
    first in sorted order)."""
    values = series.astype("string")
    levels = sorted(values.dropna().unique())
    if len(levels) < 2:
        return pd.DataFrame(index=series.index)
    base = BASE_LEVEL.get(name) if BASE_LEVEL.get(name) in levels else levels[0]
    return pd.DataFrame({f"{name}[{level}]": (values == level).fillna(False).astype(float) for level in levels if level != base}, index=series.index)


def session_predictors(sessions: pd.DataFrame) -> list[str]:
    """The design columns that vary across the sessions (the cell's factors as designed)."""
    return varied(sessions, [name for name in DESIGN_COLUMNS if name in sessions.columns])


def design_matrix(frame: pd.DataFrame, numeric: Sequence[str], categorical: Sequence[str], interactions: Sequence[str] = ()) -> pd.DataFrame:
    """The predictors: the 0/1 columns as they are, each categorical column as dummies, and each
    interaction ``a:b`` as the product of two of them."""
    parts = [frame[list(numeric)].astype(float)] + [dummies(frame[name], name) for name in categorical]
    matrix = pd.concat(parts, axis=1)
    for term in interactions:
        a, _, b = term.partition(":")
        if a not in matrix.columns or b not in matrix.columns:
            raise AnalysisError(f"interaction {term!r}: both sides must be predictors; known: {sorted(matrix.columns)}")
        matrix[term] = matrix[a] * matrix[b]
    return matrix


def full_rank(matrix: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Leave out each column that does not vary, or that the intercept and the columns kept before
    it already span; the rest, in order, and what was left out."""
    kept, dropped = [], []
    base = np.ones((len(matrix), 1))
    for column in matrix.columns:
        values = matrix[column].to_numpy(dtype=float)
        if np.nanstd(values) == 0.0:
            dropped.append(f"{column} (constant)")
            continue
        trial = np.column_stack([base, matrix[kept].to_numpy(dtype=float), values]) if kept else np.column_stack([base, values])
        if np.linalg.matrix_rank(trial) < trial.shape[1]:
            dropped.append(f"{column} (collinear)")
            continue
        kept.append(column)
    return matrix[kept], dropped


def fit_one(frame: pd.DataFrame, outcome: Outcome, numeric: Sequence[str], categorical: Sequence[str], subset: str,
            cluster: Optional[str], interactions: Sequence[str] = (), alpha: float = ALPHA) -> Fitted:
    """One model of ``outcome`` on ``frame``'s rows where the outcome is known."""
    rows = frame.loc[frame[outcome.name].notna()]
    kind = "logistic" if outcome.kind == "binary" else "linear"
    fitted = Fitted(outcome.name, outcome.level, subset, kind, OK, len(rows), None, None)
    if rows.empty:
        fitted.status = NO_DATA
        return fitted
    y = rows[outcome.name].astype(float)
    if outcome.kind == "binary":
        fitted.events = int(y.sum())
    if y.nunique() < 2:
        fitted.status, fitted.note = ONE_VALUE, f"every row is {y.iloc[0]:g}"
        return fitted
    matrix, fitted.dropped = full_rank(design_matrix(rows, numeric, categorical, interactions))
    if matrix.shape[1] == 0:
        fitted.status, fitted.note = NO_DATA, "no predictor varies"
        return fitted
    X = sm.add_constant(matrix, has_constant="add")
    if len(rows) <= X.shape[1]:
        fitted.status, fitted.note = NO_DATA, f"{len(rows)} rows for {X.shape[1]} parameters"
        return fitted
    if cluster is not None:
        groups = pd.factorize(rows[cluster])[0]
        fitted.clusters = int(groups.max() + 1)
        if fitted.clusters < 2:
            fitted.status, fitted.note = NO_DATA, "one session: no clustered standard error"
            return fitted
        cov = {"cov_type": "cluster", "cov_kwds": {"groups": groups}}
    else:
        cov = {"cov_type": "HC1"}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            if kind == "logistic":
                result = sm.Logit(y, X).fit(disp=0, maxiter=200, **cov)
            else:
                result = sm.OLS(y, X).fit(**cov)
        except (PerfectSeparationError, np.linalg.LinAlgError, ValueError, ZeroDivisionError) as error:
            fitted.status = SEPARATION if isinstance(error, PerfectSeparationError) else FAILED
            fitted.note = str(error).splitlines()[0][:200]
            return fitted
    if kind == "logistic":
        separated = any(issubclass(w.category, PerfectSeparationWarning) for w in caught)
        converged = bool(result.mle_retvals.get("converged", True)) and not any(issubclass(w.category, ConvergenceWarning) for w in caught)
        if separated or not converged or np.abs(result.params.drop("const")).max() > SEPARATION_LOGIT or not np.isfinite(result.bse).all():
            fitted.status = SEPARATION
            fitted.note = "the outcome is (nearly) separated by the predictors: no finite estimate"
            return fitted
    params, bse, pvalues, ci = result.params, result.bse, result.pvalues, result.conf_int(alpha=0.05)
    for name in (name for name in params.index if name != "const"):
        entry = {
            "outcome": outcome.name, "level": outcome.level, "subset": subset, "model": kind, "term": name, "factor": factor_of(name),
            "estimate": float(params[name]), "se": float(bse[name]), "ci_low": float(ci.loc[name, 0]), "ci_high": float(ci.loc[name, 1]),
            "p": float(pvalues[name]), "n": fitted.n, "events": fitted.events, "clusters": fitted.clusters,
        }
        if kind == "logistic":
            entry.update({"odds_ratio": math.exp(entry["estimate"]), "or_low": math.exp(entry["ci_low"]), "or_high": math.exp(entry["ci_high"])})
        fitted.terms.append(entry)
    correct([fitted], "model", alpha)
    return fitted


def correct(fitted: Sequence[Fitted], family: str = "report", alpha: float = ALPHA) -> None:
    """Holm's correction over each family of terms: ``p_holm``, ``significant`` and
    ``holm_family`` on every term, in place."""
    if family not in FAMILIES:
        raise AnalysisError(f"Holm family: one of {FAMILIES}, got {family!r}")
    groups: dict[tuple, list[dict]] = {}
    for model in fitted:
        key = () if family == "report" else (model.subset,) if family == "subset" else (model.outcome, model.subset)
        groups.setdefault(key, []).extend(model.terms)
    for terms in groups.values():
        if not terms:
            continue
        adjusted = multipletests([t["p"] for t in terms], alpha=alpha, method="holm")[1]
        for t, p in zip(terms, adjusted):
            t.update({"p_holm": float(p), "significant": bool(p < alpha), "holm_family": family, "family_size": len(terms)})


def run_all(agents: pd.DataFrame, predictors: Sequence[str], sessions: pd.DataFrame, interactions: Sequence[str] = (),
            alpha: float = ALPHA, family: str = "report") -> list[Fitted]:
    """Every outcome, pooled (condition as a factor) and in each condition, with Holm's correction
    over ``family``."""
    conditions = [c for c in CONDITIONS if c in set(agents["condition"])] + sorted(set(agents["condition"]) - set(CONDITIONS))
    design = session_predictors(sessions)
    agent_interactions = [term for term in interactions if all(side in predictors for side in term.split(":"))]
    session_interactions = [term for term in interactions if term not in agent_interactions]
    fitted = []
    for subset in [ALL, *conditions]:
        mine = agents if subset == ALL else agents.loc[agents["condition"] == subset]
        theirs = sessions if subset == ALL else sessions.loc[sessions["condition"] == subset]
        categorical = ["geometry"] + (["condition"] if subset == ALL else [])
        for outcome in AGENT_OUTCOMES:
            fitted.append(fit_one(mine, outcome, predictors, categorical, subset, "session_key", agent_interactions, alpha))
        for outcome in SESSION_OUTCOMES:
            fitted.append(fit_one(theirs, outcome, [], [*design, *categorical], subset, None, session_interactions, alpha))
    correct(fitted, family, alpha)
    return fitted


def terms_frame(fitted: Sequence[Fitted]) -> pd.DataFrame:
    return pd.DataFrame([term for model in fitted for term in model.terms])


def models_frame(fitted: Sequence[Fitted]) -> pd.DataFrame:
    return pd.DataFrame([
        {"outcome": m.outcome, "level": m.level, "subset": m.subset, "model": m.kind, "status": m.status, "n": m.n,
         "events": m.events, "clusters": m.clusters, "terms": len(m.terms), "left_out": "; ".join(m.dropped), "note": m.note}
        for m in fitted
    ])
