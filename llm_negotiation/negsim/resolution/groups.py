"""Round 1 with three or four people, analysed per conflict pair (issue #110, RF-32, tasks 8 and 9).

A group session (``passing_group``) is resolved only if every pair walking opposite ways is, and its
outcome row gives the first two members' columns only. This module measures **each conflict pair**
of each completed session, three ways, on the case's own run and seed:

- ``plan_only``: the session's plans carried out again (``replay.driver_for``), as Step 1 measures;
- ``plain_orca``: no plan;
- each **rule arm**: ORCA under a staged rule set (round 1's rules), no plan, the identity check of
  RF-12 and RF-31 (``negsim.translation.identity``) per pair: everyone in the case carries what the
  session gave them (age, gender, the cane, their own assertiveness), as a crowd run would.

Per pair: who left the conflict zone first, each person's passing side (in their own frame), and
whether the pair resolved. A rule **reproduces** a pair when both match ``plan_only``'s, as
RF-31's identity check counts it; plain ORCA is scored the same way, so a rule is credited only
with what plain ORCA does not already do.

Beside it: each person's first plan by role (walking alone, or with a friend); how two friends got
past each oncoming person (``between``: the oncoming person went between them; ``single_file``: one
fell in behind the other; ``abreast``: they stayed side by side and the oncoming person passed
outside; ``not_reached``: the run stopped first); the debriefs; and the resolved share by layout
against round 1's pairs (Wilson intervals, Fisher's exact test).

Issue #115 (RF-34), the non-verbal run: round 1's pairs of one condition only (``--pairs-condition``;
RF-30's folder holds non-verbal and talk); a **paired** comparison with another group experiment
on the same design (``--against``, matched by cell and case: the session id without its condition
letter), with the exact sign test on the sessions only one of them resolved; and the later
decision points, why they fired and what was signalled, each split by whether a friend or an
oncoming person caused it.

    python -m negsim.resolution.groups runs/rf32_round1_group_head_on_orca_groups \\
        --pairs runs/rf10_round1_head_on_keep_line \\
        --arm left_turn=runs/rf18_round1_realistic/rule_db_staging:passed_screening:4 ...

    python -m negsim.resolution.groups runs/rf34_round1_group_head_on_non_verbal \\
        --pairs runs/rf30_round1_head_on_keep_line --pairs-condition non_verbal \\
        --against runs/rf32_round1_group_head_on_orca_groups --arm ...

Nothing here calls a model. Every run is deterministic and rebuilt from the session record.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT
from ..experiment.avoidance import forget_rule_database, simulation_for
from ..rulegen.cases import CaseStore
from ..rulegen.replay import database_path
from ..rules.fields import VISIBLE_FACTOR_SWITCHES
from ..rules.snapshot import PRIVATE_ATTRIBUTES
from ..ruleset_eval.verdicts import sign_test
from .execute import MODE_PLAN_ONLY, MODE_PLAN_ORCA, PlanDriver
from .experiment import coded_plan
from .outcomes import RESOLVED, TOGETHER, physical_outcome
from .protocol import SESSION_COMPLETED
from .replay import case_of, driver_for, pairs_of, run_plan_for
from .scenarios import load_scenario

PAIR_COLUMNS = ("who_passed_first", "passing_side_a", "passing_side_b", RESOLVED, "collision", "near_miss", "min_separation_m")
FORMATIONS = ("between", "single_file", "abreast", "not_reached")
#: Words of a debrief's basis counted as naming a rule or a way of passing.
DEBRIEF_TERMS = {
    "keep left": r"keep(ing)?\s+(to\s+(the|my|your)\s+)?left",
    "keep right": r"keep(ing)?\s+(to\s+(the|my|your)\s+)?right",
    "single file": r"single[\s-]file",
    "behind (a friend)": r"\bbehind\b",
    "between": r"\bbetween\b",
    "elderly / cane": r"elder|older|cane",
}


@dataclass(frozen=True)
class Arm:
    """A rule arm: ``ruleset`` of the staging database at ``database``, or ``enable`` (a rule and
    version); ``schema_version`` is the rule format, which says what a person carries."""

    name: str
    database: Path
    ruleset: Optional[str] = None
    enable: Optional[Mapping[str, int]] = None
    schema_version: int = 4

    @classmethod
    def parse(cls, text: str) -> "Arm":
        """``name=database:ruleset:format`` or ``name=database:rule_id@version:format``."""
        name, _, rest = text.partition("=")
        database, _, rest = rest.rpartition(":")
        database, _, chosen = database.rpartition(":")
        if not name or not database or not chosen or not rest.isdigit():
            raise ValueError(f"--arm {text!r}: expected name=database:ruleset:format or name=database:rule_id@version:format")
        if "@" in chosen:
            rule, _, version = chosen.partition("@")
            return cls(name, Path(database), enable={rule: int(version)}, schema_version=int(rest))
        return cls(name, Path(database), ruleset=chosen, schema_version=int(rest))

    def directives(self) -> dict[str, Any]:
        found: dict[str, Any] = {"provider": "rules", "database": database_path(self.database)}
        if self.ruleset is not None:
            found["ruleset"] = self.ruleset
        else:
            found["enable"] = dict(self.enable or {})
        return found


# --- the people, as a crowd run carries them -----------------------------------------------------


def population(record: Mapping[str, Any], schema_version: int) -> dict[int, dict[str, Any]]:
    """Everyone in the session, with what the session gave them that a rule of this format reads:
    age and gender; from format 4, also the cane, suitcase and phone and their own private factors."""
    out = {}
    for agent, persona in record["session"]["personas"].items():
        attributes: dict[str, Any] = {key: persona[key] for key in ("age", "gender") if persona.get(key) is not None}
        if schema_version >= 4:
            attributes.update({name: persona[name] for name in (*VISIBLE_FACTOR_SWITCHES, *PRIVATE_ATTRIBUTES) if persona.get(name) is not None})
        out[int(agent)] = {"persona_id": f"{record['session_id']}:{agent}", "attributes": attributes}
    return out


def visibility(plan: Any, record: Mapping[str, Any], schema_version: int) -> dict[str, bool]:
    shown = record["session"].get("visibility") or {}
    out = {**dict(plan.visibility), "age": bool(shown.get("age", True)), "gender": bool(shown.get("gender", True))}
    if schema_version >= 4:
        out.update({name: bool(shown.get(name, True)) for name in VISIBLE_FACTOR_SWITCHES})
    return out


# --- the runs ------------------------------------------------------------------------------------


@dataclass
class Measured:
    simulation: Any
    result: Any
    track: Sequence[Any]
    start: int
    matched: Optional[bool] = None


def _run(plan: Any, driver: PlanDriver, start: int) -> Measured:
    simulation = simulation_for(plan, driver)
    result = simulation.run()
    begun = driver.started_step if driver.started_step is not None else start
    summary = simulation.provider.summary() if hasattr(simulation.provider, "summary") else None
    matched = None if summary is None else sum(((summary or {}).get("matches_begun") or {}).values()) > 0
    return Measured(simulation, result, driver.track, begun, matched)


def _value(value: Any) -> str:
    if value is None:
        return ""
    if value == TOGETHER or isinstance(value, str):
        return str(value)
    if isinstance(value, bool):
        return str(value)
    return str(int(value)) if isinstance(value, int) or float(value).is_integer() else str(value)


def _pair_columns(measured: Measured, pair: tuple[int, int], scenario: Any, goals: Mapping[int, Optional[float]]) -> dict[str, Any]:
    columns = physical_outcome(measured.simulation, measured.result, measured.track, pair, measured.start, scenario, goals)
    return {key: columns.get(key) for key in PAIR_COLUMNS}


def _same(found: Mapping[str, Any], step1: Mapping[str, Any]) -> dict[str, bool]:
    first = _value(found["who_passed_first"]) == _value(step1["who_passed_first"])
    sides = all(_value(found[key]) == _value(step1[key]) for key in ("passing_side_a", "passing_side_b"))
    return {"same_first": first, "same_sides": sides, "reproduces": first and sides}


def group_of(simulation: Any, agent: int) -> str:
    return simulation.world.agents[agent].spec.group


def formations(measured: Measured, members: Sequence[int]) -> list[dict[str, Any]]:
    """How each pair of friends got past each oncoming person (module docstring)."""
    sim = measured.simulation
    rows = [row for row in measured.track if row.step > measured.start]
    out = []
    groups: dict[str, list[int]] = {}
    for agent in members:
        groups.setdefault(group_of(sim, agent), []).append(agent)
    for group, mine in sorted(groups.items()):
        if len(mine) != 2:
            continue
        a, b = sorted(mine)
        radii = sim.world.agents[a].spec.radius + sim.world.agents[b].spec.radius
        for other in sorted(agent for agent in members if group_of(sim, agent) != group):
            found = "not_reached"
            if rows:
                sign0 = math.copysign(1.0, rows[0].bodies[other].x - (rows[0].bodies[a].x + rows[0].bodies[b].x) / 2.0)
                for row in rows:
                    ahead = row.bodies[other].x - (row.bodies[a].x + row.bodies[b].x) / 2.0
                    if math.copysign(1.0, ahead) != sign0:
                        ya, yb, yo = row.bodies[a].y, row.bodies[b].y, row.bodies[other].y
                        if abs(ya - yb) < radii:
                            found = "single_file"
                        elif min(ya, yb) < yo < max(ya, yb):
                            found = "between"
                        else:
                            found = "abreast"
                        break
            out.append({"group": group, "friends": f"{a};{b}", "oncoming": other, "formation": found})
    return out


def first_plans(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Each prompted person's first readable plan, coded mechanically, with the largest turn."""
    seen, out = set(), []
    for point in record.get("decision_points") or []:
        agent = point["agent_id"]
        if agent in seen:
            continue
        seen.add(agent)
        coded = coded_plan(record, point)
        steps = ((point.get("parsed") or {}).get("steps")) or []
        turns = [float(step["turn"]["degrees"]) for step in steps if step.get("turn")]
        out.append({"agent_id": agent, "readable": coded is not None, **(coded or {}), "max_turn_degrees": max(turns) if turns else 0.0})
    return out


def later_points(record: Mapping[str, Any]) -> dict[str, Any]:
    """Each person's decision points after their first: why each fired, every reason that names
    someone counted as caused by a friend (two members who are no conflict pair) or by an oncoming
    person; and the signals made, with who saw them (issue #115)."""
    opposite = {frozenset(pair) for pair in pairs_of(record) or []}

    def by(agent: int, other: int) -> str:
        return "oncoming" if frozenset((agent, other)) in opposite else "friend"

    seen, reasons, readable = set(), Counter(), 0
    for point in record.get("decision_points") or []:
        agent = point["agent_id"]
        if agent not in seen:
            seen.add(agent)
            continue
        readable += not point.get("parse_error")
        for reason in point.get("trigger_reasons") or []:
            name, _, other = reason.rpartition(":")
            reasons[f"{name}:{by(agent, int(other))}" if other.isdigit() else reason] += 1
    signals = Counter(str(made.get("signal")) for made in record.get("signals") or [])
    seen_by = Counter(by(int(made["signaller_id"]), int(other)) for made in record.get("signals") or [] for other in made.get("seen_by") or [])
    points = len(record.get("decision_points") or [])
    return {"later": points - len(seen), "later_readable": readable, "reasons": dict(reasons),
            "signals": dict(signals), "signals_seen_by": dict(seen_by)}


def design_key(session_id: str) -> str:
    """The session id without its condition letter (``I_group_..._r1`` and ``N_group_..._r1`` are the
    same cell, case and repeat)."""
    return session_id.split("_", 1)[1]


class GroupAnalysis:
    """Measures every completed session of a group experiment, per conflict pair."""

    def __init__(self, folder: Path | str, arms: Sequence[Arm] = (), store: Optional[CaseStore] = None):
        self.folder = Path(folder)
        self.arms = list(arms)
        self.store = store or CaseStore()
        self.records = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((self.folder / "sessions").glob("*.json")) if ".aborted" not in path.name
        ]

    def session(self, record: Mapping[str, Any]) -> dict[str, Any]:
        case = case_of(record, self.store)
        scenario = load_scenario(record["scenario"])
        base = run_plan_for(record, case)
        agents = tuple(int(agent) for agent in record["encounter"]["agents"])
        start = int(record["decisions"][0]["step"])
        pairs = pairs_of(record) or [(agents[0], agents[1])]
        plain = _run(base, PlanDriver(MODE_PLAN_ORCA, scenario, agents), start)
        goals = dict(plain.result.goal_times)
        step1 = _run(base, driver_for(record, MODE_PLAN_ONLY, base, scenario), start)
        measured = {"plan_only": step1, "plain_orca": plain}
        for arm in self.arms:
            forget_rule_database(arm.database)
            plan = replace(
                base, run_id=f"{record['session_id']}_{arm.name}", population=population(record, arm.schema_version),
                visibility=visibility(base, record, arm.schema_version), directives=arm.directives(),
            )
            measured[arm.name] = _run(plan, PlanDriver(MODE_PLAN_ORCA, scenario, agents), start)
        variant = case["scenario"].get("variant") or {}
        rows = []
        for pair in pairs:
            row: dict[str, Any] = {
                "session_id": record["session_id"], "case_id": case["case_id"], "layout": variant.get("layout"),
                "agent_a": pair[0], "agent_b": pair[1],
            }
            found = {mode: _pair_columns(m, pair, scenario, goals) for mode, m in measured.items()}
            for mode, columns in found.items():
                row.update({f"{mode}_{key}": columns[key] for key in PAIR_COLUMNS})
                if mode != "plan_only":
                    row.update({f"{mode}_{key}": value for key, value in _same(columns, found["plan_only"]).items()})
                if mode in [arm.name for arm in self.arms]:
                    row[f"{mode}_matched"] = measured[mode].matched
            rows.append(row)
        return {
            "session_id": record["session_id"], "layout": variant.get("layout"), "case_id": case["case_id"],
            "n_people": case["scenario"]["n_agents"], "pairs": rows,
            "resolved": {mode: all(row[f"{mode}_{RESOLVED}"] for row in rows) for mode in measured},
            "formations": formations(step1, agents),
            "first_plans": [
                {**plan, "with_friend": sum(group_of(step1.simulation, a) == group_of(step1.simulation, plan["agent_id"]) for a in agents) > 1,
                 **{key: record["session"]["personas"][str(plan["agent_id"])].get(key) for key in ("age", "gender", "mobility_aid", "assertiveness")}}
                for plan in first_plans(record)
            ],
            "debriefs": [d.get("parsed") or {} for d in record.get("debriefs") or []],
            "unreadable": sum(1 for p in record.get("decision_points") or [] if p.get("parse_error")),
            "decision_points": len(record.get("decision_points") or []),
            "condition": record.get("condition"),
            "later_points": later_points(record),
        }

    def run(self, report=None) -> list[dict[str, Any]]:
        out = []
        for record in self.records:
            if record["outcome"] != SESSION_COMPLETED:
                continue
            out.append(self.session(record))
            if report is not None:
                report(f"{record['session_id']}: plan_only {out[-1]['resolved']['plan_only']}")
        return out


# --- statistics ----------------------------------------------------------------------------------


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[Optional[float], Optional[float]]:
    if n == 0:
        return None, None
    p = k / n
    centre, half = (p + z * z / (2 * n)) / (1 + z * z / n), z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)


def fisher(a: int, b: int, c: int, d: int) -> float:
    """Two-sided p of Fisher's exact test on [[a, b], [c, d]] (as likely or less likely tables)."""
    n, row, col = a + b + c + d, a + b, a + c

    def prob(x: int) -> float:
        return math.comb(col, x) * math.comb(n - col, row - x) / math.comb(n, row)

    observed = prob(a)
    lo, hi = max(0, row + col - n), min(row, col)
    return round(min(1.0, sum(p for x in range(lo, hi + 1) if (p := prob(x)) <= observed * (1 + 1e-9))), 6)


# --- round 1's pairs, for comparison -------------------------------------------------------------


def pair_sessions(folder: Path | str, condition: Optional[str] = None) -> list[dict[str, Any]]:
    """Round 1's two-person sessions (an experiment folder): design sessions only (no exact-repeat
    copy and no counterfactual pair), of ``condition`` if given, with their plan_only outcome and
    first plans."""
    folder = Path(folder)
    with (folder / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        rows = {row["session_id"]: row for row in csv.DictReader(handle)}
    out = []
    for session_id, row in sorted(rows.items()):
        if row.get("pair_id") or row.get("repeat") not in ("1", ""):
            continue
        if condition is not None and row.get("condition") != condition:
            continue
        record = json.loads((folder / "sessions" / f"{session_id}.json").read_text(encoding="utf-8"))
        out.append({
            "session_id": session_id, "geometry": row.get("case_geometry"), "resolved": row["resolved_plan_only"] == "True",
            "sides": (row["passing_side_a_plan_only"], row["passing_side_b_plan_only"]), "first_plans": first_plans(record),
            "debriefs": [d.get("parsed") or {} for d in record.get("debriefs") or []],
        })
    return out


# --- another group experiment on the same design, for a paired comparison ------------------------


def against_sessions(folder: Path | str) -> dict[str, bool]:
    """Another group experiment's design sessions, by :func:`design_key`: whether each resolved in
    plan_only, read from its analysis (``analysis/group_sessions.json``, written by this module)."""
    folder = Path(folder)
    with (folder / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        design_ids = {row["session_id"] for row in csv.DictReader(handle) if row.get("repeat") == "1"}
    found = json.loads((folder / "analysis" / "group_sessions.json").read_text(encoding="utf-8"))
    return {design_key(s["session_id"]): bool(s["resolved"]["plan_only"]) for s in found if s["session_id"] in design_ids}


def paired(design: Sequence[Mapping[str, Any]], against: Mapping[str, bool]) -> dict[str, Any]:
    """This experiment's design sessions against the other's of the same cell and case, by layout:
    both resolved, this one only, the other only, neither; the exact sign test on the sessions only
    one of them resolved (McNemar's exact test)."""
    out: dict[str, Any] = {}
    for layout in sorted({s["layout"] for s in design}) + ["all"]:
        counts = Counter()
        for s in design:
            key = design_key(s["session_id"])
            if (layout != "all" and s["layout"] != layout) or key not in against:
                continue
            mine, theirs = bool(s["resolved"]["plan_only"]), against[key]
            counts["both" if mine and theirs else "this_only" if mine else "other_only" if theirs else "neither"] += 1
        out[layout] = {name: counts[name] for name in ("both", "this_only", "other_only", "neither")}
        out[layout]["n"] = sum(counts.values())
        out[layout]["sign_test_p"] = round(sign_test(counts["this_only"], counts["other_only"]), 6)
    return out


# --- the tables ----------------------------------------------------------------------------------


def _share(values: Sequence[bool]) -> str:
    values = list(values)
    if not values:
        return "-"
    low, high = wilson(sum(values), len(values))
    return f"{sum(values)} / {len(values)} ({sum(values) / len(values):.2f}; {low:.2f} to {high:.2f})"


def _plans_table(plans: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    readable = [p for p in plans if p["readable"]]
    starts = [p["start_distance_m"] for p in readable if p.get("start_distance_m") is not None]
    return {
        "people": len(plans), "readable": len(readable),
        "side": dict(Counter(p["side"] for p in readable)),
        "slowed": sum(bool(p["slowed"]) for p in readable), "stopped": sum(bool(p["stopped"]) for p in readable),
        "backed_up": sum(bool(p["backed_up"]) for p in readable), "carry_on": sum(bool(p["carry_on"]) for p in readable),
        "mean_turn_degrees": round(sum(p["max_turn_degrees"] for p in readable) / len(readable), 2) if readable else None,
        "start_distance_m_mean": round(sum(starts) / len(starts), 2) if starts else None, "with_start_distance": len(starts),
    }


def _debrief_table(debriefs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    terms = {name: sum(1 for d in debriefs if re.search(pattern, str(d.get("basis") or ""), re.IGNORECASE)) for name, pattern in DEBRIEF_TERMS.items()}
    sources = sorted({str(d.get("source")) for d in debriefs if d.get("source") and str(d.get("source")).strip().lower() not in ("none", "n/a", "")})
    return {"debriefs": len(debriefs), "kinds": dict(Counter(str(d.get("kind")) for d in debriefs)), "terms": terms, "sources": sources}


def summarise(
    sessions: Sequence[Mapping[str, Any]], pairs: Sequence[Mapping[str, Any]], arms: Sequence[Arm], design_ids: Optional[set] = None,
    against: Optional[Mapping[str, bool]] = None,
) -> dict[str, Any]:
    """Every table of the report, as numbers. ``design_ids``: the sessions of the design (no exact-repeat
    copy); ``against``: another group experiment's design sessions (:func:`against_sessions`)."""
    design = [s for s in sessions if design_ids is None or s["session_id"] in design_ids]
    out: dict[str, Any] = {"sessions": len(sessions), "design_sessions": len(design)}
    pair_k = sum(p["resolved"] for p in pairs)
    resolved = {}
    for layout in sorted({s["layout"] for s in design}) + ["all"]:
        mine = [s for s in design if layout == "all" or s["layout"] == layout]
        k = sum(s["resolved"]["plan_only"] for s in mine)
        resolved[layout] = {
            "n": len(mine), "plan_only": k, "ci": wilson(k, len(mine)),
            "plain_orca": sum(s["resolved"]["plain_orca"] for s in mine),
            "vs_pairs_fisher_p": fisher(k, len(mine) - k, pair_k, len(pairs) - pair_k) if mine and pairs else None,
            **{arm.name: sum(s["resolved"][arm.name] for s in mine) for arm in arms},
        }
    out["resolved"] = resolved
    out["pairs_round1"] = {"n": len(pairs), "plan_only": pair_k, "ci": wilson(pair_k, len(pairs))}
    every = [row for s in design for row in s["pairs"]]
    out["conflict_pairs"] = {
        "n": len(every), "resolved_plan_only": sum(bool(r["plan_only_resolved"]) for r in every),
        "sides_plan_only": dict(Counter(f"{r['plan_only_passing_side_a'] or '-'}/{r['plan_only_passing_side_b'] or '-'}" for r in every if r["plan_only_resolved"])),
    }
    round1_sides = Counter(f"{a or '-'}/{b or '-'}" for p in pairs if p["resolved"] for a, b in [p["sides"]])
    out["pairs_round1"]["sides_resolved"] = dict(round1_sides)
    identity = {}
    for mode in ["plain_orca", *(arm.name for arm in arms)]:
        for which, subset in (("resolved_pairs", [r for r in every if r["plan_only_resolved"]]), ("all_pairs", every)):
            identity.setdefault(mode, {})[which] = {
                "n": len(subset),
                "reproduces": sum(bool(r[f"{mode}_reproduces"]) for r in subset),
                "same_first": sum(bool(r[f"{mode}_same_first"]) for r in subset),
                "same_sides": sum(bool(r[f"{mode}_same_sides"]) for r in subset),
                "resolved": sum(bool(r[f"{mode}_{RESOLVED}"]) for r in subset),
                **({"matched": sum(bool(r.get(f"{mode}_matched")) for r in subset)} if mode != "plain_orca" else {}),
            }
    out["identity"] = identity
    out["formations"] = {
        layout: dict(Counter(f["formation"] for s in design if layout == "all" or s["layout"] == layout for f in s["formations"]))
        for layout in sorted({s["layout"] for s in design}) + ["all"]
    }
    def passed_cleanly(session: Mapping[str, Any], formation: Mapping[str, Any]) -> bool:
        """Whether the oncoming person resolved its conflict pair with each of the two friends."""
        friends = {int(agent) for agent in formation["friends"].split(";")}
        mine = [row for row in session["pairs"] if formation["oncoming"] in (row["agent_a"], row["agent_b"])
                and {row["agent_a"], row["agent_b"]} - {formation["oncoming"]} <= friends]
        return bool(mine) and all(row["plan_only_resolved"] for row in mine)

    out["formations_passed_cleanly"] = {
        formation: [sum(passed_cleanly(s, f) for s in design for f in s["formations"] if f["formation"] == formation),
                    sum(1 for s in design for f in s["formations"] if f["formation"] == formation)]
        for formation in FORMATIONS
    }
    plans = [p for s in design for p in s["first_plans"]]
    out["first_plans"] = {
        "alone": _plans_table([p for p in plans if not p["with_friend"]]),
        "with_friend": _plans_table([p for p in plans if p["with_friend"]]),
        "round1_pairs": _plans_table([p for s in pairs for p in s["first_plans"]]),
        "facing_a_cane": _plans_table([p for s in design for p in s["first_plans"] if p["mobility_aid"] != "cane"
                                       and any(q["mobility_aid"] == "cane" for q in s["first_plans"])]),
        "holds_ground": _plans_table([p for p in plans if p["assertiveness"] == "holds_ground"]),
        "gives_way": _plans_table([p for p in plans if p["assertiveness"] == "gives_way"]),
    }
    out["debriefs"] = {"groups": _debrief_table([d for s in sessions for d in s["debriefs"]]),
                       "round1_pairs": _debrief_table([d for p in pairs for d in p["debriefs"]])}
    out["unreadable"] = {"decision_points": sum(s["decision_points"] for s in sessions), "unreadable": sum(s["unreadable"] for s in sessions)}
    later = [s["later_points"] for s in design if "later_points" in s]
    if later:
        def total(name: str) -> dict[str, int]:
            found = Counter()
            for row in later:
                found.update(row[name])
            return dict(found.most_common())

        resolved_later = [s["later_points"]["later"] for s in design if "later_points" in s and s["resolved"]["plan_only"]]
        out["later_points"] = {
            "sessions": len(later), "with_any": sum(1 for row in later if row["later"]),
            "later": sum(row["later"] for row in later), "later_readable": sum(row["later_readable"] for row in later),
            "in_resolved_sessions": sum(resolved_later),
            "reasons": total("reasons"), "signals": total("signals"), "signals_seen_by": total("signals_seen_by"),
        }
    if against is not None:
        out["paired"] = paired(design, against)
    return out


def pairs_csv(sessions: Sequence[Mapping[str, Any]]) -> str:
    rows = [row for s in sessions for row in s["pairs"]]
    names: list[str] = []
    for row in rows:
        names.extend(key for key in row if key not in names)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=names, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: "" if row.get(key) is None else row.get(key) for key in names})
    return buffer.getvalue()


def report_markdown(summary: Mapping[str, Any], arms: Sequence[Arm], experiment: str = "RF-32") -> str:
    lines = [f"# {experiment}: group sessions per conflict pair (machine-written)", "",
             f"{summary['sessions']} completed sessions, {summary['design_sessions']} of the design (exact-repeat copies left out).", "",
             "## Resolved in plan_only, by layout", "",
             "| Layout | Sessions | Resolved (95% CI) | Fisher p against round 1's pairs | plain ORCA | " + " | ".join(a.name for a in arms) + " |",
             "| --- | --- | --- | --- | --- | " + " | ".join("---" for _ in arms) + " |"]
    for layout, row in summary["resolved"].items():
        lines.append(f"| {layout} | {row['n']} | {_share([True] * row['plan_only'] + [False] * (row['n'] - row['plan_only']))} | "
                     f"{row['vs_pairs_fisher_p']} | {row['plain_orca']} | " + " | ".join(str(row[a.name]) for a in arms) + " |")
    pr = summary["pairs_round1"]
    lines += ["", f"Round 1's pairs: {pr['plan_only']} / {pr['n']} resolved ({pr['ci'][0]:.2f} to {pr['ci'][1]:.2f}); "
              f"sides of the resolved: {pr['sides_resolved']}.", "",
              "## Conflict pairs", "", f"{summary['conflict_pairs']}", "", "## Identity check per conflict pair", "",
              "| Arm | Pairs | Reproduced | Same first | Same sides | Resolved | Matched |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for mode, parts in summary["identity"].items():
        for which, row in parts.items():
            lines.append(f"| {mode} ({which}) | {row['n']} | {row['reproduces']} | {row['same_first']} | {row['same_sides']} | {row['resolved']} | {row.get('matched', '-')} |")
    lines += ["", "## How friends got past each oncoming person", "", f"{summary['formations']}", "",
              f"Passed cleanly (the oncoming person resolved its pair with each friend), of each formation: {summary['formations_passed_cleanly']}", "",
              "## First plans", ""]
    for name, table in summary["first_plans"].items():
        lines.append(f"- **{name}**: {table}")
    lines += ["", "## Debriefs", ""]
    for name, table in summary["debriefs"].items():
        lines.append(f"- **{name}**: {table}")
    lines += ["", f"Unreadable after retry: {summary['unreadable']}"]
    if "later_points" in summary:
        lines += ["", "## Decision points after each person's first", "", f"{summary['later_points']}"]
    if "paired" in summary:
        lines += ["", "## Paired with the other group experiment (same cell and case)", "",
                  "| Layout | Sessions | Both resolved | This only | Other only | Neither | Sign test p |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for layout, row in summary["paired"].items():
            lines.append(f"| {layout} | {row['n']} | {row['both']} | {row['this_only']} | {row['other_only']} | {row['neither']} | {row['sign_test_p']} |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m negsim.resolution.groups", description=__doc__.split("\n\n")[0])
    parser.add_argument("folder", type=Path, help="the group experiment's folder")
    parser.add_argument("--pairs", type=Path, help="round 1's two-person experiment folder to compare with")
    parser.add_argument("--pairs-condition", help="only round 1's pairs of this condition (issue #115)")
    parser.add_argument("--against", type=Path, help="another group experiment on the same design, analysed by this module, to pair with (issue #115)")
    parser.add_argument("--arm", action="append", default=[], help="name=database:ruleset:format or name=database:rule_id@version:format")
    parser.add_argument("--out", type=Path, help="where to write (default: the folder's analysis/)")
    args = parser.parse_args(argv)
    arms = [Arm.parse(text) for text in args.arm]
    analysis = GroupAnalysis(args.folder, arms)
    sessions = analysis.run(report=lambda line: print(line, file=sys.stderr))
    pairs = pair_sessions(args.pairs, args.pairs_condition) if args.pairs else []
    with (args.folder / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        design_ids = {row["session_id"] for row in csv.DictReader(handle) if row.get("repeat") == "1"}
    summary = summarise(sessions, pairs, arms, design_ids, against_sessions(args.against) if args.against else None)
    out = args.out or args.folder / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "group_pairs.csv").write_text(pairs_csv(sessions), encoding="utf-8", newline="\n")
    (out / "group_sessions.json").write_text(json.dumps(sessions, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    (out / "group_summary.json").write_text(json.dumps({"arms": [a.__dict__ | {"database": str(a.database)} for a in arms], **summary}, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    (out / "group_analysis.md").write_text(report_markdown(summary, arms, args.folder.name), encoding="utf-8", newline="\n")
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
