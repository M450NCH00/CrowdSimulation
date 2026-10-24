"""Read ``outcomes.csv`` files and reshape them (issue #63, RF-8, task 2).

A resolution experiment's ``outcomes.csv`` has one row per session (``encounter-protocol.md``,
section 7). The analysis needs two tables:

- **sessions** (:func:`sessions_table`): one row per completed session, with the physical
  outcomes of one mode given to person 1 and person 2. The physical columns' ``_a`` and ``_b``
  are the encounter's first two members (``encounter_agents``: whoever noticed first leads), not
  person 1 and person 2, so they are mapped through it;
- **agents** (:func:`agents_table`): one row per agent per session, from that agent's point of
  view: its own factors, the other's factors **as it was told them**, the pairwise values from its
  own point of view, condition and geometry, and its outcomes.

**As told.** A factor of the other person counts only if it was printed to the agent at one or
more of its decision points:

- the other's age and gender: ``<p>_other_age_shown`` >= 1 (full detail only, with the
  demographics visible);
- an observable core factor: the other has the marked level (the base level has no line), its
  switch ``<name>_visible`` is on (on when the design does not vary it), and
  ``<p>_other_observable_shown`` >= 1;
- a pairwise factor: ``<p>_pairwise_lines_shown`` >= 1; then both levels have a line, so the
  agent was told one or the other;
- the other's ethnicity (RF-26, issue #92): ``<p>_other_ethnicity_shown`` >= 1 (every group has a
  line; the switch ``ethnicity_visible`` off gives 0). The predictor ``same_ethnicity`` is 1 when
  the agent was told the other's group and it is its own; ``ethnicity_unseen`` when it was not
  told. The groups themselves (``own_ethnicity``, ``other_ethnicity`` as told,
  ``other_ethnicity_actual``) are descriptive columns, not predictors: at real shares the smaller
  groups have too few sessions for a term of their own (``WORK_LOG-92.md``, A3).

The agent's own age and gender count only when the demographics are visible (they hide both
people's). Its own core factors are always in its own description.

**Predictors** are 0/1 columns; an age is "high" when it is above the lowest age in the data (a
design has two ages). A told level and "not told" are kept apart where both levels have a line
(``other_age_high`` against ``other_demographics_unseen``; ``finds_other_attractive`` against
``pairwise_unseen``).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd

from .factors import DESIGN_COLUMNS, OBSERVABLE, PAIRWISE, PERSON, SITUATIONS

MODES = ("plan_only", "plan_orca", "plain_orca")
TOGETHER = "together"
COMPLETED = "completed"
CONDITIONS = ("independent", "non_verbal", "talk")

#: The columns this analysis cannot do without. ``encounter_agents`` and the ``_shown`` counts
#: were added by issue #63: an older ``outcomes.csv`` is rebuilt by running its experiment again
#: (a resumed experiment rebuilds its tables from the session records, with no LLM call).
REQUIRED = (
    "session_id", "outcome", "condition", "case_id", "p1_agent", "p2_agent", "encounter_agents",
    "p1_other_age_shown", "p2_other_age_shown",
)


class AnalysisError(ValueError):
    """The input cannot be analysed as it is."""


@dataclass(frozen=True)
class Outcome:
    name: str
    kind: str  # binary | continuous
    level: str  # agent | session
    meaning: str


AGENT_OUTCOMES = (
    Outcome("passed_first", "binary", "agent", "left the conflict zone first (physical; `together` counts as not first)"),
    Outcome("kept_left", "binary", "agent", "kept to its own left at the closest approach (physical; rows where the two were not abreast are left out)"),
    Outcome("stopped", "binary", "agent", "its speed fell below the deadlock monitor's threshold (physical)"),
    Outcome("backed_up", "binary", "agent", "moved against its path (physical)"),
    Outcome("plan_left", "binary", "agent", "its first plan turns to its left only"),
    Outcome("plan_right", "binary", "agent", "its first plan turns to its right only"),
    Outcome("plan_slowed", "binary", "agent", "its first plan slows below its speed at the decision"),
    Outcome("plan_stopped", "binary", "agent", "its first plan stops"),
    Outcome("plan_backed_up", "binary", "agent", "its first plan backs up"),
    Outcome("start_distance_m", "continuous", "agent", "its first plan starts at this distance (plans that start so)"),
    Outcome("signalled", "binary", "agent", "it signalled at least once (non-verbal and talk only)"),
)
SESSION_OUTCOMES = (
    Outcome("resolved_plan_only", "binary", "session", "resolved in `plan_only` (the Step 1 measure)"),
    Outcome("resolved_plan_orca", "binary", "session", "resolved in `plan_orca`"),
    Outcome("resolved_by_llm", "binary", "session", "resolved in `plan_only` before ORCA took over"),
    Outcome("decision_points", "continuous", "session", "decision points of both people"),
)
#: What who-passed-first, passing side, stopped and backed up are, per session (stability, flips).
BEHAVIOUR = ("first", "p1_side", "p2_side", "p1_stopped", "p2_stopped", "p1_backed_up", "p2_backed_up")


# --- reading ------------------------------------------------------------------------------------


def read_outcomes(paths: Sequence[Path | str]) -> pd.DataFrame:
    """Every row of every file, as text (empty cells missing), with ``source`` (the file) and
    ``session_key`` (file and session id: two experiments may use the same id)."""
    if not paths:
        raise AnalysisError("no outcomes.csv given")
    frames = []
    for path in paths:
        path = Path(path)
        if not path.is_file():
            raise AnalysisError(f"{path}: no such file")
        frame = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
        missing = [column for column in REQUIRED if column not in frame.columns]
        if missing:
            raise AnalysisError(
                f"{path}: missing column(s) {missing}. They were added by issue #63; run the experiment again "
                "(python run_experiment.py <config>) to rebuild its tables from the session records, with no LLM call."
            )
        frame.insert(0, "source", str(path))
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    data.insert(1, "session_key", data["source"] + "::" + data["session_id"])
    return data


def read_decisions(paths: Sequence[Path | str]) -> Optional[pd.DataFrame]:
    """``decisions.jsonl`` beside each ``outcomes.csv``, if there is one: one row per decision
    point, with ``session_key``. ``None`` when no file has one."""
    rows = []
    for path in paths:
        found = Path(path).with_name("decisions.jsonl")
        if not found.is_file():
            continue
        for line in found.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                row["session_key"] = f"{path}::{row['session_id']}"
                rows.append(row)
    return pd.DataFrame(rows) if rows else None


def client_of(paths: Sequence[Path | str]) -> set[str]:
    """The client named in each experiment's ``config.json`` (``mock`` or a provider), if any."""
    found = set()
    for path in paths:
        config = Path(path).with_name("config.json")
        if config.is_file():
            found.add(str(json.loads(config.read_text(encoding="utf-8")).get("client_name")))
    return found


# --- conversions --------------------------------------------------------------------------------


def as_bool(series: pd.Series) -> pd.Series:
    """``True``/``False`` text as 1.0/0.0; anything else missing."""
    return series.map({"True": 1.0, "False": 0.0, "true": 1.0, "false": 0.0, "1": 1.0, "0": 0.0}).astype(float)


def as_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype(float)


def _column(data: pd.DataFrame, name: str) -> pd.Series:
    return data[name] if name in data.columns else pd.Series(np.nan, index=data.index, dtype=object)


def _switch(data: pd.DataFrame, name: str) -> pd.Series:
    """A visibility switch: on unless the design switched it off."""
    return as_bool(_column(data, name)).fillna(1.0)


def repeat_group(session_id: str) -> str:
    """The cell's sessions in the exact-repeat set share an id but for ``_r<n>``."""
    return re.sub(r"_r\d+$", "", session_id)


# --- the sessions -------------------------------------------------------------------------------


def sessions_table(raw: pd.DataFrame, mode: str = "plan_only") -> tuple[pd.DataFrame, dict[str, int]]:
    """One row per completed session, with the mode's physical outcomes given to person 1 and
    person 2; and how many sessions were left out, by outcome (``no_encounter``, ``aborted``)."""
    if mode not in MODES:
        raise AnalysisError(f"mode: one of {MODES}, got {mode!r}")
    left_out = raw.loc[raw["outcome"] != COMPLETED, "outcome"].fillna("missing").value_counts().to_dict()
    data = raw.loc[raw["outcome"] == COMPLETED].copy().reset_index(drop=True)
    if data.empty:
        raise AnalysisError("no completed session to analyse")
    out = pd.DataFrame({
        "session_key": data["session_key"], "session_id": data["session_id"], "source": data["source"],
        "condition": data["condition"], "case_id": data["case_id"],
        "geometry": data["geometry"] if "geometry" in data.columns else _column(data, "case_geometry"),
        "exact_repeat_set": as_bool(_column(data, "exact_repeat_set")).fillna(0.0).astype(bool),
        "repeat_group": data["session_key"].map(repeat_group),
        "pair_id": _column(data, "pair_id"), "pair_role": _column(data, "pair_role"), "pair_factor": _column(data, "pair_factor"),
        "p1_agent": as_number(data["p1_agent"]).astype(int), "p2_agent": as_number(data["p2_agent"]).astype(int),
    })
    out["geometry"] = out["geometry"].fillna(out["case_id"])
    for name in DESIGN_COLUMNS:
        if name in data.columns:
            out[name] = data[name]

    members = data["encounter_agents"].fillna("").str.split(";")
    a = members.map(lambda m: int(m[0]) if m and m[0] != "" else -1)
    b = members.map(lambda m: int(m[1]) if len(m) > 1 else -1)
    first = _column(data, f"who_passed_first_{mode}")
    out["first"] = [
        None if pd.isna(value) else TOGETHER if value == TOGETHER else "p1" if int(value) == p1 else "p2" if int(value) == p2 else None
        for value, p1, p2 in zip(first, out["p1_agent"], out["p2_agent"])
    ]
    for person in ("p1", "p2"):
        agent = out[f"{person}_agent"]
        for key, stem in (("side", "passing_side"), ("stopped", "stopped"), ("backed_up", "backed_up")):
            picked = pd.Series(np.nan, index=data.index, dtype=object)
            for which, member in (("a", a), ("b", b)):
                column = f"{stem}_{which}_{mode}"
                if column in data.columns:
                    mask = agent == member
                    picked[mask] = data.loc[mask, column]
            out[f"{person}_{key}"] = picked if key == "side" else as_bool(picked)
    for name in ("resolved_plan_only", "resolved_plan_orca", "resolved_by_llm"):
        out[name] = as_bool(_column(data, name))
    out["decision_points"] = as_number(_column(data, "p1_decision_points")).fillna(0) + as_number(_column(data, "p2_decision_points")).fillna(0)
    return out, {str(key): int(value) for key, value in left_out.items()}


# --- one row per agent --------------------------------------------------------------------------


def agents_table(raw: pd.DataFrame, sessions: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """One row per agent per session (task 2), and the predictor columns, in a fixed order."""
    data = raw.loc[raw["outcome"] == COMPLETED].reset_index(drop=True)
    ages = pd.concat([as_number(data["p1_age"]), as_number(data["p2_age"])]) if "p1_age" in data.columns else pd.Series(dtype=float)
    low = ages.min() if ages.notna().any() else np.nan
    demographics = _switch(data, "demographics_visible")
    rows = []
    for me, other in (("p1", "p2"), ("p2", "p1")):
        frame = pd.DataFrame({
            "session_key": sessions["session_key"], "session_id": sessions["session_id"], "condition": sessions["condition"],
            "geometry": sessions["geometry"], "case_id": sessions["case_id"], "role": me,
            "agent": sessions[f"{me}_agent"], "other_agent": sessions[f"{other}_agent"],
        })
        own_age, other_age = as_number(_column(data, f"{me}_age")), as_number(_column(data, f"{other}_age"))
        own_gender, other_gender = _column(data, f"{me}_gender"), _column(data, f"{other}_gender")
        age_told = as_number(_column(data, f"{me}_other_age_shown")).fillna(0) >= 1
        gender_told = as_number(_column(data, f"{me}_other_gender_shown")).fillna(0) >= 1
        frame["own_age"], frame["other_age"] = own_age, other_age
        frame["own_gender"], frame["other_gender"] = own_gender, other_gender
        frame["other_age_told"], frame["other_gender_told"] = age_told.astype(float), gender_told.astype(float)
        # Predictors: own age and gender (told only with the demographics visible), the other's as told.
        frame["own_age_high"] = ((own_age > low) & (demographics == 1)).astype(float)
        frame["own_female"] = ((own_gender == "female") & (demographics == 1)).astype(float)
        frame["own_demographics_hidden"] = (demographics == 0).astype(float)
        frame["other_age_high"] = ((other_age > low) & age_told).astype(float)
        frame["other_female"] = ((other_gender == "female") & gender_told).astype(float)
        frame["other_demographics_unseen"] = (~age_told).astype(float)
        observable_told = as_number(_column(data, f"{me}_other_observable_shown")).fillna(0) >= 1
        for name, (_, marked, observable) in PERSON.items():
            if f"{me}_{name}" not in data.columns:
                continue
            frame[f"own_{name}"] = (data[f"{me}_{name}"] == marked).astype(float)
            if observable:
                told = (data[f"{other}_{name}"] == marked) & (_switch(data, f"{name}_visible") == 1) & observable_told
                frame[f"other_{name}"] = told.astype(float)
                frame[f"other_{name}_actual"] = (data[f"{other}_{name}"] == marked).astype(float)
        for name, (_, marked) in SITUATIONS.items():
            if name in data.columns:
                frame[f"{name}_{marked}"] = (data[name] == marked).astype(float)
        if f"{me}_ethnicity" in data.columns:  # issue #92: one's own is always told, the other's as told
            own_group, other_group = data[f"{me}_ethnicity"], data[f"{other}_ethnicity"]
            ethnicity_told = as_number(_column(data, f"{me}_other_ethnicity_shown")).fillna(0) >= 1
            frame["own_ethnicity"] = own_group.to_numpy()
            frame["other_ethnicity"] = other_group.where(ethnicity_told).to_numpy()
            frame["other_ethnicity_actual"] = other_group.to_numpy()
            frame["same_ethnicity"] = ((own_group == other_group) & ethnicity_told).astype(float)
            frame["ethnicity_unseen"] = (~ethnicity_told).astype(float)
        shown = _column(data, f"{me}_pairwise_lines_shown")
        if shown.notna().any():
            pairwise_told = as_number(shown).fillna(0) >= 1
            for column in PAIRWISE:
                if f"{me}_{column}" in data.columns:
                    frame[column] = ((as_number(data[f"{me}_{column}"]) == 1) & pairwise_told).astype(float)
            frame["pairwise_unseen"] = (~pairwise_told).astype(float)
        frame["is_lower_agent"] = (frame["agent"] < frame["other_agent"]).astype(float)

        # Outcomes, physical (the sessions table's mode) and of the first coded plan.
        first = sessions["first"]
        frame["passed_first"] = np.where(first.isna(), np.nan, (first == me).astype(float))
        side = sessions[f"{me}_side"]
        frame["kept_left"] = side.map({"left": 1.0, "right": 0.0}).astype(float)
        frame["stopped"], frame["backed_up"] = sessions[f"{me}_stopped"], sessions[f"{me}_backed_up"]
        plan_side = _column(data, f"{me}_first_side")
        has_plan = plan_side.notna()
        frame["plan_left"] = np.where(has_plan, (plan_side == "left").astype(float), np.nan)
        frame["plan_right"] = np.where(has_plan, (plan_side == "right").astype(float), np.nan)
        for key in ("slowed", "stopped", "backed_up"):
            frame[f"plan_{key}"] = as_bool(_column(data, f"{me}_first_{key}"))
        frame["start_distance_m"] = as_number(_column(data, f"{me}_first_start_distance_m"))
        signals = _column(data, f"{me}_signals")
        frame["signalled"] = np.where(sessions["condition"] == "independent", np.nan, signals.notna().astype(float))
        frame["decision_points"] = as_number(_column(data, f"{me}_decision_points"))
        frame["debrief_kind"] = _column(data, f"{me}_debrief_kind").to_numpy()
        rows.append(frame)
    agents = pd.concat(rows, ignore_index=True)
    order = [
        "own_age_high", "own_female", "own_demographics_hidden", "other_age_high", "other_female", "other_demographics_unseen",
        *(f"own_{name}" for name in PERSON), *(f"other_{name}" for name in OBSERVABLE), "same_ethnicity", "ethnicity_unseen",
        *(f"{name}_{marked}" for name, (_, marked) in SITUATIONS.items()), *PAIRWISE, "pairwise_unseen", "is_lower_agent",
    ]
    return agents, [column for column in order if column in agents.columns]


def varied(frame: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    """The columns that take more than one value in ``frame``."""
    return [column for column in columns if frame[column].nunique(dropna=True) > 1]
