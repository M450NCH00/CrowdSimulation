"""Replaying a session's plans on its case's own run (issue #59, RF-4; ``docs/resolution.md``, D6
and D13).

A session (RF-3) records every plan its agents gave, with the step it was given at. A replay runs
the case's own run (rebuilt from its experiment config and checked to be that run,
``rulegen.replay.source_plan``), on the same seed, with those plans given at those steps, in
``plan_only`` or ``plan_orca``. D6's second replay is this in ``plan_orca``, with no LLM call.

**The part of a session record a replay reads** (RF-3 writes the rest)::

    {"session_id": "...",
     "case": {"case_id": "head_on_02dfbadb", "version": 2},
     "scenario": "passing",                          # the plug-in (negsim.resolution.scenarios)
     "encounter": {"agents": [0, 1], "type": "head_on"},  # type: the case's encounter class if left out
     "decisions": [{"agent_id": 0, "decision_point": 1, "step": 40, "time_s": 4.0,
                    "steps": [...]}],                # in the reply format, as PlanDriver logs them
     "release": null}                                 # or {"step": n, "reason": "..."}: ORCA took over

**Where:** ``<out>/<experiment>/replay/<session_id>/plan_only/`` and ``.../plan_orca/``, each an
ordinary avoidance run folder (``log-schema.md``). Beside them, ``physical_outcomes.csv`` (one row
per session and mode, and one for plain ORCA on the same seed) and ``report.md``.

**Rebuildable (D13):** each replay's ``outcome.json`` records the seed, the scenario's hash and the
SHA-256 of the plans it ran (``plans`` block). ``--verify`` rebuilds a replay from the session
record alone, into a scratch folder, and checks every file is byte for byte the same; the one line
that cannot be is ``config.json``'s ``created_utc``, the time the folder was written.

    python -m negsim.resolution.replay SESSION.json [SESSION.json ...] --experiment NAME
        [--out runs] [--mode plan_only] [--mode plan_orca] [--overwrite] [--verify]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, TextIO

from ..configutil import PACKAGE_ROOT, ConfigError, load_yaml
from ..experiment.avoidance import AvoidanceRunPlan, execute_avoidance_run, simulation_for
from ..rulegen.cases import CaseStore
from ..rulegen.replay import source_plan
from ..runlog.schema import CONFIG_FILE, OUTCOME_FILE
from ..scenarios.registry import build_crowd_scenario
from .execute import MODE_PLAN_ORCA, MODES, PlanDriver, steps_from_dicts
from .outcomes import MODE_PLAIN_ORCA, c0_baselines, physical_outcome, report, to_csv
from .scenario import Scenario
from .scenarios import load_scenario

SESSION_KEYS = ("session_id", "case", "scenario", "encounter", "decisions")
DECISION_KEYS = ("agent_id", "step", "steps")
REPLAY_DIR = "replay"
OUTCOMES_FILE = "physical_outcomes.csv"
REPORT_FILE = "report.md"
#: The one key of a rebuilt folder that differs from the original: when the folder was written.
UNREPEATABLE = ("created_utc",)


class SessionError(ConfigError):
    """A session record a replay cannot run."""


def load_session(path: Path | str) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8")) if str(path).endswith(".json") else load_yaml(path)
    check_session(raw, str(path))
    return raw


def check_session(session: Any, where: str = "session") -> None:
    if not isinstance(session, Mapping):
        raise SessionError(f"{where}: expected a mapping")
    missing = [key for key in SESSION_KEYS if key not in session]
    if missing:
        raise SessionError(f"{where}: missing {missing}")
    agents = session["encounter"].get("agents") if isinstance(session["encounter"], Mapping) else None
    if not isinstance(agents, list) or len(agents) != 2:
        raise SessionError(f"{where}.encounter.agents: two agent ids")
    steps = []
    for number, decision in enumerate(session["decisions"]):
        absent = [key for key in DECISION_KEYS if key not in decision]
        if absent:
            raise SessionError(f"{where}.decisions[{number}]: missing {absent}")
        if decision["agent_id"] not in agents:
            raise SessionError(f"{where}.decisions[{number}]: agent {decision['agent_id']} is not in the encounter")
        steps.append(decision["step"])
    if not session["decisions"]:
        raise SessionError(f"{where}: no decisions to replay")
    if steps != sorted(steps):
        raise SessionError(f"{where}.decisions: not in the order they were given")


def plans_sha256(session: Mapping[str, Any]) -> str:
    """The SHA-256 of what a replay runs: the decisions and the release, as canonical JSON."""
    payload = {"decisions": session["decisions"], "release": session.get("release")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def case_of(session: Mapping[str, Any], store: Optional[CaseStore] = None) -> dict[str, Any]:
    reference = session["case"]
    return (store or CaseStore()).get(reference["case_id"], reference.get("version"))


def encounter_type(session: Mapping[str, Any], case: Mapping[str, Any]) -> str:
    return session["encounter"].get("type") or case["formation"]["encounter_class"] or case["scenario"]["type"]


def driver_for(session: Mapping[str, Any], mode: str, run_plan: AvoidanceRunPlan, scenario: Scenario) -> PlanDriver:
    """A driver with the session's plans scheduled at their steps, read back with the parser's checks."""
    agents = tuple(session["encounter"]["agents"])
    driver = PlanDriver(mode, scenario, agents)
    specs = build_crowd_scenario(run_plan.scenario_config).agents
    for decision in session["decisions"]:
        agent = int(decision["agent_id"])
        steps = steps_from_dicts(decision["steps"], specs[agent].max_speed, tuple(scenario.events))
        driver.schedule(int(decision["step"]), agent, steps)
    release = session.get("release")
    if release:
        driver.schedule_release(int(release["step"]), str(release["reason"]))
    return driver


def _labels(session: Mapping[str, Any], case: Mapping[str, Any], mode: str) -> dict[str, Any]:
    return {"session_id": session["session_id"], "case_id": case["case_id"], "encounter_type": encounter_type(session, case), "mode": mode}


def plain_orca(session: Mapping[str, Any], case: Mapping[str, Any], run_plan: AvoidanceRunPlan, scenario: Scenario) -> dict[str, Any]:
    """The case's own run with no plan, measured from the session's first decision: plain ORCA's
    goal times (for the delays) and its outcome columns (for the report). Nothing is written."""
    agents = tuple(session["encounter"]["agents"])
    watcher = PlanDriver(MODE_PLAN_ORCA, scenario, agents)  # no plan: it only watches
    simulation = simulation_for(run_plan, watcher)
    result = simulation.run()
    start = int(session["decisions"][0]["step"])
    columns = physical_outcome(simulation, result, watcher.track, agents, start, scenario, result.goal_times, _labels(session, case, MODE_PLAIN_ORCA))
    return {"goal_times": {str(agent): time for agent, time in sorted(result.goal_times.items())}, "physical_outcome": columns}


def replay_session(
    session: Mapping[str, Any],
    mode: str,
    run_dir: Path,
    experiment: str,
    git: Mapping[str, Any],
    store: Optional[CaseStore] = None,
    plain: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Run one session's plans in one mode into ``run_dir``; return its outcome columns."""
    if mode not in MODES:
        raise ValueError(f"mode: one of {MODES}, got {mode!r}")
    check_session(session)
    case = case_of(session, store)
    base = source_plan(case)
    scenario = load_scenario(session["scenario"])
    run_plan = replace(base, run_id=f"{session['session_id']}_{mode}", experiment_name=experiment)
    if plain is None:
        plain = plain_orca(session, case, base, scenario)
    plain_goals = {int(agent): time for agent, time in plain["goal_times"].items()}
    driver = driver_for(session, mode, run_plan, scenario)
    agents = tuple(session["encounter"]["agents"])
    identity = {
        "session_id": session["session_id"],
        "case": {"case_id": case["case_id"], "version": case["version"]},
        "mode": mode,
        "seed": run_plan.seed,
        "scenario_sha256": case["scenario"]["resolved_sha256"],
        "plans_sha256": plans_sha256(session),
    }
    found: dict[str, Any] = {}

    def outcome_extra(simulation: Any, result: Any) -> dict[str, Any]:
        start = driver.started_step if driver.started_step is not None else int(session["decisions"][0]["step"])
        columns = physical_outcome(simulation, result, driver.track, agents, start, scenario, plain_goals, _labels(session, case, mode))
        found["columns"] = columns
        return {
            "plans": {
                **identity,
                "scenario_plugin": scenario.identity(),
                "encounter": {"agents": list(agents), "type": encounter_type(session, case)},
                "driver": driver.as_dict(),
                "physical_outcome": columns,
                "plain_orca": dict(plain),
            }
        }

    execute_avoidance_run(run_plan, run_dir, git, plans=driver, config_extra={"plans": identity}, outcome_extra=outcome_extra)
    return found["columns"]


def session_dir(out_root: Path, experiment: str, session_id: str) -> Path:
    return Path(out_root) / experiment / REPLAY_DIR / session_id


def replay_sessions(
    sessions: Sequence[Mapping[str, Any]],
    experiment: str,
    out_root: Path | str = PACKAGE_ROOT / "runs",
    git: Optional[Mapping[str, Any]] = None,
    modes: Sequence[str] = MODES,
    overwrite: bool = False,
    store: Optional[CaseStore] = None,
    report_to: TextIO | None = None,
) -> list[dict[str, Any]]:
    """Replay every session in every mode, and write ``physical_outcomes.csv`` and ``report.md``.
    A replay whose folder already has an outcome is read back, not run, unless ``overwrite``."""
    if git is None:
        from ..experiment.batch import git_state

        git = git_state()
    out_root = Path(out_root)
    rows: list[dict[str, Any]] = []
    for session in sessions:
        check_session(session)
        folder = session_dir(out_root, experiment, session["session_id"])
        plain = None
        for mode in modes:
            run_dir = folder / mode
            if (run_dir / OUTCOME_FILE).is_file() and not overwrite:
                block = json.loads((run_dir / OUTCOME_FILE).read_text(encoding="utf-8"))["plans"]
                columns, plain = block["physical_outcome"], block["plain_orca"]
            else:
                if plain is None:
                    case = case_of(session, store)
                    plain = plain_orca(session, case, source_plan(case), load_scenario(session["scenario"]))
                columns = replay_session(session, mode, run_dir, experiment, git, store, plain)
            rows.append(columns)
            if report_to is not None:
                print(f"{session['session_id']} {mode}: resolved={columns['resolved']}, collision={columns['collision']}, "
                      f"near_miss={columns['near_miss']}, deadlock={columns['deadlock']}", file=report_to)
        if plain is not None:
            rows.append(dict(plain["physical_outcome"]))
    replay_root = out_root / experiment / REPLAY_DIR
    replay_root.mkdir(parents=True, exist_ok=True)
    (replay_root / OUTCOMES_FILE).write_text(to_csv(rows), encoding="utf-8")
    (replay_root / REPORT_FILE).write_text(report(rows, c0_baselines()), encoding="utf-8")
    return rows


# --- rebuilding (D13) ---------------------------------------------------------------------------


def _comparable(path: Path) -> bytes:
    data = path.read_bytes()
    if path.name == CONFIG_FILE:
        config = json.loads(data)
        for key in UNREPEATABLE:
            config.pop(key, None)
        return json.dumps(config, sort_keys=True).encode("utf-8")
    return data


def verify(session: Mapping[str, Any], mode: str, run_dir: Path, store: Optional[CaseStore] = None) -> list[str]:
    """Rebuild a replay from the session record alone and compare it with ``run_dir``, file by
    file. Returns the differences (empty: byte for byte the same, but for ``created_utc``)."""
    config = json.loads((Path(run_dir) / CONFIG_FILE).read_text(encoding="utf-8"))
    if config.get("plans", {}).get("plans_sha256") != plans_sha256(session):
        return [f"{run_dir}: ran other plans than this session's (plans_sha256 differs)"]
    with tempfile.TemporaryDirectory() as scratch:
        rebuilt = Path(scratch) / mode
        replay_session(session, mode, rebuilt, config["experiment_name"], config["git"], store)
        problems = []
        names = sorted({p.name for p in Path(run_dir).iterdir()} | {p.name for p in rebuilt.iterdir()})
        for name in names:
            mine, theirs = Path(run_dir) / name, rebuilt / name
            if not mine.is_file() or not theirs.is_file():
                problems.append(f"{name}: in only one of the two folders")
            elif _comparable(mine) != _comparable(theirs):
                problems.append(f"{name}: differs")
        return problems


def main(argv: Optional[list[str]] = None, out: Optional[TextIO] = None) -> int:
    out = out or sys.stdout
    parser = argparse.ArgumentParser(prog="python -m negsim.resolution.replay", description=__doc__.split("\n\n")[0])
    parser.add_argument("sessions", nargs="+", help="session records (JSON)")
    parser.add_argument("--experiment", required=True, help="the experiment the replays belong to")
    parser.add_argument("--out", default=str(PACKAGE_ROOT / "runs"), help="the runs folder (default: runs/)")
    parser.add_argument("--mode", action="append", choices=MODES, help="a mode to run (default: both)")
    parser.add_argument("--overwrite", action="store_true", help="run again a replay that already has an outcome")
    parser.add_argument("--verify", action="store_true", help="rebuild each existing replay and check it is the same")
    args = parser.parse_args(argv)
    sessions = [load_session(path) for path in args.sessions]
    modes = args.mode or list(MODES)
    if args.verify:
        failed = 0
        for session in sessions:
            for mode in modes:
                run_dir = session_dir(Path(args.out), args.experiment, session["session_id"]) / mode
                problems = verify(session, mode, run_dir)
                failed += bool(problems)
                print(f"{session['session_id']} {mode}: " + ("the same" if not problems else "; ".join(problems)), file=out)
        return 1 if failed else 0
    rows = replay_sessions(sessions, args.experiment, args.out, modes=modes, overwrite=args.overwrite, report_to=out)
    print(f"{len(rows)} outcome rows in {Path(args.out) / args.experiment / REPLAY_DIR / OUTCOMES_FILE}", file=out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
