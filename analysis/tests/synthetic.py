"""Synthetic outcome rows, shaped as a resolution experiment's ``outcomes.csv`` (issue #63).

:func:`row` builds one session's row with every column the analysis reads, from a few keyword
arguments; :func:`screen` builds a whole design with planted effects (or none), for the tests of
task 12. Nothing here imitates a model: the effects are planted on purpose, by the probabilities
given.
"""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

AGES = {"low": 25, "high": 70}


def _side(rng: random.Random) -> str:
    return rng.choice(["left", "right"])


def row(
    session_id: str,
    condition: str = "independent",
    *,
    p1_agent: int = 0,
    order: Sequence[int] = (0, 1),
    first: Optional[str] = "p1",  # p1 | p2 | together | None
    sides: Mapping[str, Optional[str]] = None,
    stopped: Mapping[str, bool] = None,
    backed: Mapping[str, bool] = None,
    plans: Mapping[str, Mapping[str, Any]] = None,
    cell: Mapping[str, Any] = None,
    people: Mapping[str, Mapping[str, Any]] = None,
    shown: Mapping[str, Mapping[str, int]] = None,
    signals: Mapping[str, Optional[str]] = None,
    debriefs: Mapping[str, Optional[str]] = None,
    resolved: bool = True,
    outcome: str = "completed",
    exact_repeat_set: bool = False,
    geometry: str = "layout=aligned",
    pair: Optional[tuple[str, str, str]] = None,
) -> dict[str, Any]:
    """One session. ``sides``, ``stopped``, ``backed``, ``plans``, ``people``, ``shown``,
    ``signals`` and ``debriefs`` are keyed by ``p1`` and ``p2``."""
    agents = {"p1": p1_agent, "p2": 1 - p1_agent}
    letter = {order[0]: "a", order[1]: "b"}
    cell = {"age_pair": "same", "gender_pair": "p1_female", "demographics_visible": True, "mapping": "p1_lower" if p1_agent == 0 else "p1_higher", **(cell or {})}
    out: dict[str, Any] = {
        "session_id": session_id, "outcome": outcome, "case_id": "head_on_test", "case_version": 1, "case_geometry": geometry,
        "encounter_type": "head_on", "scenario_plugin": "passing", "condition": condition, "mapping": cell["mapping"],
        "repeat": int(session_id.rsplit("_r", 1)[1]) if "_r" in session_id else 1, "exact_repeat_set": exact_repeat_set,
        "geometry": geometry, "model": "synthetic", "temperature": 1.0,
    }
    if pair is not None:
        out.update({"pair_id": pair[0], "pair_role": pair[1], "pair_factor": pair[2]})
    out.update({key: value for key, value in cell.items() if key != "mapping"})
    for p in ("p1", "p2"):
        person = {"age": 25, "gender": "female", "urgency": "routine", **((people or {}).get(p) or {})}
        plan = {"side": "none", "slowed": False, "stopped": False, "backed_up": False, "start_distance_m": None, **((plans or {}).get(p) or {})}
        seen = {"age": 0, "gender": 0, "observable": 0, **((shown or {}).get(p) or {})}
        out.update({
            f"{p}_agent": agents[p], f"{p}_age": person["age"], f"{p}_gender": person["gender"], f"{p}_urgency": person["urgency"],
            f"{p}_errand": None,
            **{f"{p}_{name}": value for name, value in person.items() if name not in ("age", "gender", "urgency")},
            f"{p}_decision_points": 1, f"{p}_trigger_reasons": "trigger", f"{p}_unreadable": 0,
            f"{p}_signals": (signals or {}).get(p), f"{p}_messages": 0,
            f"{p}_debrief_kind": (debriefs or {}).get(p, "none"), f"{p}_debrief_source": "none",
            **{f"{p}_first_{key}": value for key, value in plan.items()},
            f"{p}_other_age_shown": seen["age"], f"{p}_other_gender_shown": seen["gender"], f"{p}_other_observable_shown": seen["observable"],
        })
        if "pairwise" in seen:
            out[f"{p}_pairwise_lines_shown"] = seen["pairwise"]
    out["encounter_size"] = 2
    out["encounter_agents"] = ";".join(str(a) for a in order)
    who = None if first is None else "together" if first == "together" else agents[first]
    for mode in ("plan_only", "plan_orca"):
        out[f"who_passed_first_{mode}"] = who
        for p in ("p1", "p2"):
            which = letter[agents[p]]
            out[f"passing_side_{which}_{mode}"] = (sides or {}).get(p, "left")
            out[f"stopped_{which}_{mode}"] = bool((stopped or {}).get(p, False))
            out[f"backed_up_{which}_{mode}"] = bool((backed or {}).get(p, False))
        out[f"resolved_{mode}"] = resolved
    out["resolved_by_llm"] = resolved
    return out


def write_csv(rows: Sequence[Mapping[str, Any]], path: Path, decisions: Optional[Iterable[Mapping[str, Any]]] = None) -> Path:
    """``outcomes.csv`` as negsim writes it (every column, empty for missing), and, if given,
    ``decisions.jsonl`` beside it."""
    names: list[str] = []
    for r in rows:
        names.extend(key for key in r if key not in names)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, lineterminator="\n")
        writer.writeheader()
        for r in rows:
            writer.writerow({key: "" if r.get(key) is None else r.get(key) for key in names})
    if decisions is not None:
        path.with_name("decisions.jsonl").write_text("".join(json.dumps(d) + "\n" for d in decisions), encoding="utf-8")
    return path


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def screen(
    seed: int,
    sessions_per_condition: int = 200,
    conditions: Sequence[str] = ("independent", "talk"),
    urgency_effect: float = 0.0,
    told_load_effect: float = 0.0,
) -> list[dict[str, Any]]:
    """A balanced design of five two-level factors (age, gender, urgency, load, surroundings),
    mapping and geometry, with outcomes drawn at random.

    - ``urgency_effect``: the log-odds that person 1 passes first rises by this when person 1 is
      urgent (and falls by it when not): an effect of ``own_urgency`` on ``passed_first``;
    - ``told_load_effect``: an agent told that the other pulls a large suitcase stops with
      log-odds -1.5 + this (otherwise -1.5): an effect of ``other_load`` on ``stopped``. Person
      2 is told it at a random half of the sessions (the other half it was never printed).

    Every other outcome is drawn with fixed probabilities that no factor changes.
    """
    rng = random.Random(f"screen:{seed}")
    rows = []
    for condition in conditions:
        for k in range(sessions_per_condition):
            bits = [(k >> b) & 1 for b in range(6)]
            older, male, urgent, load, busy, higher = bits
            geometry = "layout=aligned" if rng.random() < 0.5 else "layout=apart_20cm"
            told = rng.random() < 0.5
            cell = {"age_pair": "p1_older" if older else "same", "gender_pair": "p1_male" if male else "p1_female",
                    "urgency": "p1" if urgent else "neither", "load": "p1" if load else "neither",
                    "surroundings": "busy" if busy else "quiet"}
            people = {
                "p1": {"age": AGES["high" if older else "low"], "gender": "male" if male else "female",
                       "urgency": "urgent" if urgent else "routine", "load": "large_suitcase" if load else "none"},
                "p2": {"age": AGES["low"], "gender": "female", "urgency": "routine", "load": "none"},
            }
            shown = {"p1": {"age": 1, "gender": 1, "observable": 1}, "p2": {"age": 1, "gender": 1, "observable": 1 if told else 0}}
            p1_first = rng.random() < _logistic(urgency_effect * (1 if urgent else -1))
            p2_told_load = bool(load and told)
            stopped = {"p1": rng.random() < _logistic(-1.5), "p2": rng.random() < _logistic(-1.5 + told_load_effect * p2_told_load)}
            plans = {p: {"side": rng.choice(["left", "right", "none"]), "slowed": rng.random() < 0.4, "stopped": rng.random() < 0.2,
                         "backed_up": rng.random() < 0.15, "start_distance_m": round(rng.gauss(5.0, 1.0), 2) if rng.random() < 0.5 else None}
                     for p in ("p1", "p2")}
            rows.append(row(
                f"{condition[0].upper()}_test_{k:04d}_r1", condition, p1_agent=1 if higher else 0, order=(0, 1) if rng.random() < 0.5 else (1, 0),
                first="p1" if p1_first else "p2", sides={"p1": _side(rng), "p2": _side(rng)}, stopped=stopped,
                backed={"p1": rng.random() < 0.15, "p2": rng.random() < 0.15}, plans=plans, cell=cell, people=people, shown=shown,
                signals={p: ("nod" if rng.random() < 0.5 else None) for p in ("p1", "p2")} if condition != "independent" else None,
                resolved=rng.random() < 0.6, geometry=geometry,
            ))
    return rows
