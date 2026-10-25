"""Issue #101: the ``keep_line`` execution, and carrying a run's sessions out again under another
execution with no LLM call (``negsim.resolution.reexecute``)."""

from __future__ import annotations

import csv
import json

import pytest

from negsim.llm.mock import MockClient
from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution import reexecute as R
from test_encounter_protocol import GIT, policy, reply, small_config
from test_execute import records, run_plans

SIDESTEP_THEN_WALK = [{"speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.4}}, {"speed_mps": 1.3, "until": {"seconds": 3}}]
TURN_THEN_WALK = [{"speed_mps": 1.3, "turn": {"to": "left", "degrees": 20}, "until": {"seconds": 1}}, {"speed_mps": 1.3, "until": {"seconds": 3}}]


def y_after_second_step(plan, execution):
    run, _, _ = run_plans(X.MODE_PLAN_ONLY, {0: plan, 1: []}, execution=execution)
    first, second = records(run, 0)
    track = {row.step: row.bodies[0].y for row in run.driver.track}
    return track[first["end_step"]], track[second["end_step"]]


@pytest.mark.parametrize("plan", [SIDESTEP_THEN_WALK, TURN_THEN_WALK], ids=["sidestep", "turn"])
def test_under_keep_line_a_step_without_a_turn_keeps_the_line_and_under_as_prompted_it_steers_back(plan):
    aside, later = y_after_second_step(plan, X.EXECUTION_KEEP_LINE)
    assert aside > 0.3 and later == pytest.approx(aside, abs=0.01)
    aside_old, later_old = y_after_second_step(plan, X.EXECUTION_AS_PROMPTED)
    assert aside_old == pytest.approx(aside, abs=1e-9) and later_old < aside_old - 0.2  # pulled back to its path


def test_keep_line_changes_nothing_for_a_plan_without_a_move_aside():
    plan = {0: [{"speed_mps": 1.0, "until": {"seconds": 2}}], 1: []}
    a = run_plans(X.MODE_PLAN_ONLY, plan, execution=X.EXECUTION_KEEP_LINE)[0].driver.track
    b = run_plans(X.MODE_PLAN_ONLY, plan, execution=X.EXECUTION_AS_PROMPTED)[0].driver.track
    assert [(r.bodies[0].x, r.bodies[0].y) for r in a] == pytest.approx([(r.bodies[0].x, r.bodies[0].y) for r in b])


@pytest.fixture(scope="module")
def source(tmp_path_factory):
    out = tmp_path_factory.mktemp("reexecute")
    config = small_config("reexec_src", conditions=("independent",))
    answer = reply("Step aside, then walk on.", [*TURN_THEN_WALK[:1], {"speed_mps": 1.3, "until": "other_passes"}])
    E.run_resolution(config, client=MockClient(policy=policy({0: answer, 1: answer})), out_root=out, report=lambda _: None, git=GIT)
    return out / "reexec_src"


def rows(folder):
    return {row["session_id"]: row for row in csv.DictReader((folder / "outcomes.csv").open(encoding="utf-8"))}


def test_the_same_execution_reproduces_the_source_exactly(source, tmp_path):
    was = json.loads(next((source / "sessions").glob("*.json")).read_text(encoding="utf-8")).get("protocol", {}).get("execution", "rf4")
    target = R.reexecute(source, was, tmp_path, name="same")
    old, new = rows(source), rows(target)
    physical = [c for c in next(iter(old.values())) if c.endswith(("_plan_only", "_plan_orca", "_plain_orca"))]
    assert set(old) == set(new) and physical
    assert all(old[s][c] == new[s][c] for s in old for c in physical)


def test_another_execution_is_recorded_in_every_session_and_the_config(source, tmp_path):
    target = R.reexecute(source, X.EXECUTION_KEEP_LINE, tmp_path)
    assert target.name == "reexec_src_keep_line"
    for path in (target / "sessions").glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["protocol"]["execution"] == "keep_line" and record["reexecuted_from"]["experiment"] == "reexec_src"
        original = json.loads((source / "sessions" / path.name).read_text(encoding="utf-8"))
        assert record["decision_points"] == original["decision_points"]  # the plans and replies are the source's
        replay = json.loads((target / "replay" / record["session_id"] / "plan_only" / "config.json").read_text(encoding="utf-8"))
        assert replay["experiment_name"] == "reexec_src_keep_line"
    config = json.loads((target / "config.json").read_text(encoding="utf-8"))
    assert config["reexecution"]["execution"] == "keep_line" and config["experiment"]["experiment_name"] == "reexec_src_keep_line"
    assert (target / "NOTE.md").is_file() and len(rows(target)) == len(rows(source))
    with pytest.raises(R.ReexecuteError):  # it never writes over a run
        R.reexecute(source, X.EXECUTION_KEEP_LINE, tmp_path)


def test_a_session_decided_after_the_trigger_is_refused(source, tmp_path):
    copy = tmp_path / "late"
    copy.mkdir()
    for name in ("config.json", "design.jsonl"):
        (copy / name).write_text((source / name).read_text(encoding="utf-8"), encoding="utf-8")
    (copy / "sessions").mkdir()
    path = next((source / "sessions").glob("*.json"))
    record = json.loads(path.read_text(encoding="utf-8"))
    assert R.decided_at_trigger(record)
    record["decision_points"][-1]["time_s"] = record["encounter"]["trigger"]["time_s"] + 1.0
    assert not R.decided_at_trigger(record)
    (copy / "sessions" / path.name).write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(R.ReexecuteError, match="after the trigger"):
        R.reexecute(copy, X.EXECUTION_KEEP_LINE, tmp_path / "out")
