"""The identity check (issue #67, RF-12, task 6): does ORCA with the translated rule do what the LLM
agents did?

Each translated rule is switched on alone, with plain ORCA for every pair it does not match, and run
on each Step 1 session it was extracted from (RF-11's ``provenance.sessions_used``): the session's
case, on the case's own run and seed (``negsim.resolution.replay``), with the session's bodies (a
person pulling a suitcase is wider) and each person's age and gender, seen as the session's design
showed them. Nobody follows a plan: it is ORCA under the rule. It is measured from the session's
first decision with the same code that measured the session (``physical_outcome``), and compared
with what the session's plans did in ``plan_only``:

- ``who_passed_first``: the same agent first out of the conflict zone, or both together;
- ``passing_sides``: each person went by on the same side, in their own frame.

A session is **reproduced** when both hold. The same comparison is made for plain ORCA on the same
seed, so that a rule is credited only with what plain ORCA does not already do. Plain ORCA's run
must also be the one the session recorded (its ``*_plain_orca`` columns): if not, the row says so
and the check is not trusted for it. Nothing is written but the rows: the runs are deterministic,
and each row names its case, seed and the rule's SHA-256, so any of them can be rebuilt.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..experiment.avoidance import AvoidanceRunPlan, forget_rule_database, simulation_for
from ..resolution.execute import MODE_PLAN_ORCA, PlanDriver
from ..resolution.outcomes import TOGETHER, physical_outcome
from ..resolution.factors import with_bodies
from ..resolution.replay import case_of, check_session, pairs_of, plain_orca
from ..resolution.scenarios import load_scenario
from ..rulegen.cases import CaseStore
from ..rulegen.replay import database_path, source_plan
from ..rules.model import Rule

COMPARED = ("who_passed_first", "passing_side_a", "passing_side_b")
ROW_COLUMNS = (
    "session_id", "case_id", "seed", "condition", "rule_matched",
    "step1_who_passed_first", "step1_passing_side_a", "step1_passing_side_b",
    "rule_who_passed_first", "rule_passing_side_a", "rule_passing_side_b", "rule_resolved",
    "plain_who_passed_first", "plain_passing_side_a", "plain_passing_side_b", "plain_resolved",
    "rule_same_first", "rule_same_sides", "rule_reproduces", "plain_same_first", "plain_same_sides", "plain_reproduces",
    "plain_is_the_recorded_run",
)


def _value(value: Any) -> str:
    """An outcome value as the outcome rows write it: an agent id, ``together``, a side, or empty."""
    if value is None or value == "":
        return ""
    if value == TOGETHER or isinstance(value, str) and not value.lstrip("-").replace(".", "", 1).isdigit():
        return str(value)
    return str(int(float(value)))


def _compare(found: Mapping[str, Any], step1: Mapping[str, str]) -> dict[str, bool]:
    first = _value(found["who_passed_first"]) == step1["who_passed_first"]
    sides = all(_value(found[key]) == step1[key] for key in ("passing_side_a", "passing_side_b"))
    return {"same_first": first, "same_sides": sides, "reproduces": first and sides}


class SessionSource:
    """Step 1's sessions, read from their resolution experiments' folders: each record and its
    outcome row. A session found in two folders is refused."""

    def __init__(self, folders: Sequence[Path | str]):
        self.rows: dict[str, dict[str, str]] = {}
        self.folder: dict[str, Path] = {}
        for folder in folders:
            folder = Path(folder)
            with (folder / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    if row["session_id"] in self.folder:
                        raise ValueError(f"session {row['session_id']} is in both {self.folder[row['session_id']]} and {folder}")
                    self.rows[row["session_id"]] = row
                    self.folder[row["session_id"]] = folder

    def record(self, session_id: str) -> dict[str, Any]:
        if session_id not in self.folder:
            raise ValueError(f"session {session_id} is in none of the sources")
        record = json.loads((self.folder[session_id] / "sessions" / f"{session_id}.json").read_text(encoding="utf-8"))
        check_session(record, session_id)
        return record


def population(row: Mapping[str, str]) -> dict[int, dict[str, Any]]:
    """The two people's ages and genders, as the session gave them (nothing else: a rule reads no more)."""
    out: dict[int, dict[str, Any]] = {}
    for person in ("p1", "p2"):
        attributes: dict[str, Any] = {}
        if row.get(f"{person}_age", "") not in ("", "not_told"):
            attributes["age"] = int(float(row[f"{person}_age"]))
        if row.get(f"{person}_gender", "") not in ("", "not_told"):
            attributes["gender"] = row[f"{person}_gender"]
        agent = int(row[f"{person}_agent"])
        out[agent] = {"persona_id": f"{row['session_id']}:{person}", "attributes": attributes}
    return out


def visibility(plan: AvoidanceRunPlan, row: Mapping[str, str]) -> dict[str, bool]:
    """The case's visibility, with age and gender as the session's design showed them."""
    shown = row.get("demographics_visible", "True") not in ("False", "false", "0")
    return {**dict(plan.visibility), "age": shown, "gender": shown}


class IdentityCheck:
    """Runs translated rules on Step 1 sessions. Plain ORCA, and each case's run plan (slow to
    rebuild), are computed once per session and case and reused for every rule."""

    def __init__(self, sessions: SessionSource, store: Optional[CaseStore] = None):
        self.sessions = sessions
        self.store = store or CaseStore()
        self._cases: dict[tuple[str, Any], tuple[Mapping[str, Any], AvoidanceRunPlan]] = {}
        self._plain: dict[str, dict[str, Any]] = {}

    def _base(self, record: Mapping[str, Any]) -> tuple[Mapping[str, Any], AvoidanceRunPlan]:
        key = (record["case"]["case_id"], record["case"].get("version"))
        if key not in self._cases:
            case = case_of(record, self.store)
            self._cases[key] = (case, source_plan(case))
        case, plan = self._cases[key]
        return case, with_bodies(plan, record.get("bodies"))  # as run_plan_for, from the cached plan

    def _plain_of(self, record: Mapping[str, Any], case: Mapping[str, Any], plan: AvoidanceRunPlan) -> dict[str, Any]:
        if record["session_id"] not in self._plain:
            self._plain[record["session_id"]] = plain_orca(record, case, plan, load_scenario(record["scenario"]))
        return self._plain[record["session_id"]]

    def row(self, rule: Rule, staging_root: Path, session_id: str) -> dict[str, Any]:
        record = self.sessions.record(session_id)
        source = self.sessions.rows[session_id]
        case, base = self._base(record)
        scenario = load_scenario(record["scenario"])
        agents = tuple(record["encounter"]["agents"])
        plain = self._plain_of(record, case, base)
        plan = replace(
            base, run_id=f"{session_id}_{rule.rule_id}", population=population(source), visibility=visibility(base, source),
            directives={"provider": "rules", "database": database_path(staging_root), "enable": {rule.rule_id: rule.version}},
        )
        watcher = PlanDriver(MODE_PLAN_ORCA, scenario, agents)  # no plan: it only watches
        simulation = simulation_for(plan, watcher)
        result = simulation.run()
        start = int(record["decisions"][0]["step"])
        goals = {int(agent): time for agent, time in plain["goal_times"].items()}
        ruled = physical_outcome(simulation, result, watcher.track, agents, start, scenario, goals, None, pairs_of(record))
        summary = simulation.provider.summary() or {}
        step1 = {key: _value(source.get(f"{key}_plan_only", "")) for key in COMPARED}
        recorded = {key: _value(source.get(f"{key}_plain_orca", "")) for key in COMPARED}
        plain_columns = plain["physical_outcome"]
        mine, theirs = _compare(ruled, step1), _compare(plain_columns, step1)
        return {
            "session_id": session_id, "case_id": case["case_id"], "seed": base.seed, "condition": source.get("condition", ""),
            "rule_matched": sum((summary.get("matches_begun") or {}).values()) > 0,
            **{f"step1_{key}": step1[key] for key in COMPARED},
            **{f"rule_{key}": _value(ruled[key]) for key in COMPARED}, "rule_resolved": bool(ruled.get("resolved")),
            **{f"plain_{key}": _value(plain_columns[key]) for key in COMPARED}, "plain_resolved": bool(plain_columns.get("resolved")),
            "rule_same_first": mine["same_first"], "rule_same_sides": mine["same_sides"], "rule_reproduces": mine["reproduces"],
            "plain_same_first": theirs["same_first"], "plain_same_sides": theirs["same_sides"], "plain_reproduces": theirs["reproduces"],
            "plain_is_the_recorded_run": all(_value(plain_columns[key]) == recorded[key] for key in COMPARED),
        }

    def run(self, rule: Rule, staging_root: Path, session_ids: Sequence[str]) -> list[dict[str, Any]]:
        forget_rule_database(staging_root)
        return [self.row(rule, staging_root, session_id) for session_id in session_ids]


def share(rows: Sequence[Mapping[str, Any]], column: str) -> Optional[float]:
    return None if not rows else round(sum(bool(row[column]) for row in rows) / len(rows), 4)


def summarise(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The identity share and its parts, for the rule and for plain ORCA, over the sessions whose
    plain ORCA run is the recorded one; and the same among the sessions the rule matched."""
    trusted = [row for row in rows if row["plain_is_the_recorded_run"]]
    matched = [row for row in trusted if row["rule_matched"]]
    out: dict[str, Any] = {"sessions": len(rows), "plain_not_the_recorded_run": len(rows) - len(trusted), "trusted": len(trusted),
                           "rule_matched": len(matched)}
    for name, subset in (("all", trusted), ("matched", matched)):
        out[name] = {
            "n": len(subset),
            **{f"rule_{part}": share(subset, f"rule_{part}") for part in ("reproduces", "same_first", "same_sides", "resolved")},
            **{f"plain_{part}": share(subset, f"plain_{part}") for part in ("reproduces", "same_first", "same_sides", "resolved")},
        }
    return out


def as_csv(rows: Sequence[Mapping[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=ROW_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in ROW_COLUMNS})
    return buffer.getvalue()
