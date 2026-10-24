"""Counterfactual flip rates against the noise floor, and behaviour stability (issue #63, RF-8,
tasks 6 and 7; ``docs/resolution.md``, D14).

**A session's behaviour** is what was measured physically, given to person 1 and person 2: who
passed first (``p1``, ``p2``, ``together`` or nobody), each one's passing side, whether each
stopped, and whether each backed up. Each component is compared on its own, and all of them
together (``behaviour``).

**The noise floor** is the flip rate between two sessions of the same cell in the exact-repeat
set: identical prompts, so any difference is the model's own randomness. Every pair of repeats
of a cell counts (three repeats give three pairs). Pairs from one cell are not independent, so
its 95% interval is a bootstrap over cells.

**A counterfactual pair** (RF-7) is two sessions identical but for one factor. Its flip rate is
the share of pairs whose behaviour differs, with a Wilson 95% interval (each pair is its own
case and condition). A factor's flip rate counts as evidence **only where it is clearly above the
noise floor**: here, where the lower end of its interval is above the upper end of the noise
floor's, in the same condition (all conditions together when compared pooled).

**Stability** (task 7) of a cell of the exact-repeat set is the share of its repeats with the
commonest outcome, as #30's stability was for stated rules (``rule-generation.md``, section 5).
A cell whose commonest behaviour came up in fewer than ``coin_flip_below`` of its repeats (by
default 3 in 4) is listed as a coin flip: with 3 repeats that is any cell whose repeats disagree,
because a fair coin gives a 2-to-1 split three times in four. RF-11 should claim no rule there.
"""

from __future__ import annotations

import itertools
import math
import random
from typing import Optional, Sequence

import pandas as pd

from .load import BEHAVIOUR, CONDITIONS, repeat_group

#: Each compared component, and the session columns it is made of.
COMPONENTS: dict[str, tuple[str, ...]] = {
    "who_passed_first": ("first",),
    "passing_side": ("p1_side", "p2_side"),
    "stopped": ("p1_stopped", "p2_stopped"),
    "backed_up": ("p1_backed_up", "p2_backed_up"),
    "behaviour": BEHAVIOUR,
}
ALL = "all"
COIN_FLIP_BELOW = 0.75
BOOTSTRAP = 2000


def outcome_key(sessions: pd.DataFrame, component: str) -> pd.Series:
    """Each session's value of a component, as text (missing as ``-``)."""
    def text(value) -> str:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return "-"
        return str(int(value)) if isinstance(value, float) else str(value)

    columns = COMPONENTS[component]
    return sessions[list(columns)].apply(lambda row: "|".join(text(row[c]) for c in columns), axis=1)


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """The Wilson score interval of k in n."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def _subsets(sessions: pd.DataFrame) -> list[str]:
    present = set(sessions["condition"])
    return [ALL, *(c for c in CONDITIONS if c in present), *sorted(present - set(CONDITIONS))]


def _repeat_cells(sessions: pd.DataFrame, component: str) -> list[tuple[str, list[str]]]:
    rows = sessions.loc[sessions["exact_repeat_set"]]
    keys = outcome_key(rows, component) if not rows.empty else pd.Series(dtype=str)
    cells = []
    for group, members in rows.groupby("repeat_group", sort=True):
        if len(members) >= 2:
            cells.append((members["condition"].iloc[0], list(keys.loc[members.index])))
    return cells


def noise_floor(sessions: pd.DataFrame, component: str = "behaviour", seed: int = 63, bootstrap: int = BOOTSTRAP) -> pd.DataFrame:
    """The flip rate between repeats of one cell, per condition and pooled."""
    cells = _repeat_cells(sessions, component)
    rows = []
    for subset in _subsets(sessions):
        mine = [values for condition, values in cells if subset == ALL or condition == subset]
        counts = [(sum(a != b for a, b in itertools.combinations(values, 2)), math.comb(len(values), 2)) for values in mine]
        flips, pairs = sum(k for k, _ in counts), sum(n for _, n in counts)
        low = high = math.nan
        if pairs:
            draw = random.Random(f"noise_floor:{seed}:{component}:{subset}")
            rates = []
            for _ in range(bootstrap):
                sample = [counts[draw.randrange(len(counts))] for _ in counts]
                total = sum(n for _, n in sample)
                rates.append(sum(k for k, _ in sample) / total)
            rates.sort()
            low, high = rates[int(0.025 * bootstrap)], rates[min(bootstrap - 1, int(0.975 * bootstrap))]
        rows.append({"component": component, "subset": subset, "cells": len(mine), "pairs": pairs, "flips": flips,
                     "rate": flips / pairs if pairs else math.nan, "ci_low": low, "ci_high": high})
    return pd.DataFrame(rows)


def flip_rates(sessions: pd.DataFrame, component: str = "behaviour") -> pd.DataFrame:
    """The counterfactual pairs' flip rate, per flipped factor, per condition and pooled."""
    rows = sessions.loc[sessions["pair_id"].notna()]
    if rows.empty:
        return pd.DataFrame(columns=["component", "factor", "subset", "pairs", "flips", "rate", "ci_low", "ci_high"])
    keys = outcome_key(rows, component)
    found = []
    for pair_id, members in rows.groupby("pair_id", sort=True):
        roles = dict(zip(members["pair_role"], members.index))
        if set(roles) != {"base", "flipped"} or len(members) != 2:
            continue  # an unfinished pair (a session without an encounter) is left out
        factor, change = members["pair_factor"].iloc[0], members["pair_change"].iloc[0] if "pair_change" in members else None
        if isinstance(change, str) and change:  # issue #92: one person's group flipped, kept apart by what changed
            factor = f"{factor}:{change}"
        found.append({"factor": factor, "condition": members["condition"].iloc[0],
                      "flipped": keys.loc[roles["base"]] != keys.loc[roles["flipped"]]})
    pairs = pd.DataFrame(found)
    out = []
    for factor in sorted(set(pairs["factor"])) if not pairs.empty else []:
        for subset in _subsets(sessions):
            mine = pairs.loc[(pairs["factor"] == factor) & ((pairs["condition"] == subset) if subset != ALL else True)]
            if mine.empty:
                continue
            k, n = int(mine["flipped"].sum()), len(mine)
            low, high = wilson(k, n)
            out.append({"component": component, "factor": factor, "subset": subset, "pairs": n, "flips": k, "rate": k / n, "ci_low": low, "ci_high": high})
    return pd.DataFrame(out)


def against_noise(flips: pd.DataFrame, floors: pd.DataFrame) -> pd.DataFrame:
    """Each flip rate beside the noise floor of its subset, with the verdict."""
    if flips.empty:
        return flips
    merged = flips.merge(
        floors.rename(columns={"rate": "noise_rate", "ci_low": "noise_low", "ci_high": "noise_high", "pairs": "noise_pairs", "flips": "noise_flips", "cells": "noise_cells"}),
        on=["component", "subset"], how="left",
    )

    def verdict(row) -> str:
        if pd.isna(row["noise_high"]):
            return "no noise floor to compare with"
        return "above the noise floor" if row["ci_low"] > row["noise_high"] else "not distinguishable from the noise floor"

    merged["verdict"] = merged.apply(verdict, axis=1)
    return merged


def stability(sessions: pd.DataFrame, coin_flip_below: float = COIN_FLIP_BELOW) -> pd.DataFrame:
    """Per cell of the exact-repeat set: its repeats, each component's stability, the commonest
    behaviour, and whether it is a coin flip."""
    rows = sessions.loc[sessions["exact_repeat_set"]]
    if rows.empty:
        return pd.DataFrame()
    keys = {component: outcome_key(rows, component) for component in COMPONENTS}
    out = []
    for group, members in rows.groupby("repeat_group", sort=True):
        if len(members) < 2:
            continue
        entry = {"cell": repeat_group(members["session_id"].iloc[0]), "source": members["source"].iloc[0],
                 "condition": members["condition"].iloc[0], "case_id": members["case_id"].iloc[0], "repeats": len(members)}
        for component in COMPONENTS:
            counts = keys[component].loc[members.index].value_counts()
            entry[f"stability_{component}"] = counts.iloc[0] / len(members)
        entry["commonest_behaviour"] = keys["behaviour"].loc[members.index].value_counts().index[0]
        entry["coin_flip"] = bool(entry["stability_behaviour"] < coin_flip_below)
        out.append(entry)
    return pd.DataFrame(out)


def stability_distribution(table: pd.DataFrame) -> pd.DataFrame:
    """How many cells have each stability, per component."""
    if table.empty:
        return pd.DataFrame()
    rows = []
    for component in COMPONENTS:
        for value, count in table[f"stability_{component}"].round(4).value_counts().sort_index().items():
            rows.append({"component": component, "stability": value, "cells": int(count)})
    return pd.DataFrame(rows)


def summaries(sessions: pd.DataFrame, seed: int = 63, components: Optional[Sequence[str]] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The noise floor and the flip rates against it, for every component."""
    components = list(components or COMPONENTS)
    floors = pd.concat([noise_floor(sessions, c, seed) for c in components], ignore_index=True)
    flips = pd.concat([flip_rates(sessions, c) for c in components], ignore_index=True)
    return floors, against_noise(flips, floors)
