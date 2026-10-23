"""Carrying out LLM agents' plans (issue #59, RF-4): the executor, the two modes, the scenario's
execution side, the physical outcome columns, the replay and its rebuild, and runs unchanged."""

from __future__ import annotations

import json
import math

import pytest

from helpers import crowd
from negsim.avoidance.simulation import MODE_PLAN, AvoidanceSimulation
from negsim.experiment.avoidance import simulation_for
from negsim.negotiation.parsing import TurnParseError
from negsim.resolution import execute as X
from negsim.resolution import replay as R
from negsim.resolution.outcomes import GENERAL_COLUMNS, physical_outcome, report
from negsim.resolution.reply import Step
from negsim.resolution.scenario import Scenario
from negsim.resolution.scenarios import load_scenario
from negsim.rulegen.cases import CaseStore
from negsim.rulegen.replay import source_plan

PASSING = load_scenario("passing")
EVENTS = tuple(PASSING.events)
DT = 0.1
GIT = {"commit": "test", "dirty": False}

LEFT = [{"turn": {"to": "left", "degrees": 20}, "speed_mps": 1.3, "until": "other_passes"}]
RIGHT = [{"turn": {"to": "right", "degrees": 20}, "speed_mps": 1.3, "until": "other_passes"}]


def steps(raw):
    return X.steps_from_dicts(raw, 2.0, EVENTS)


def result_json(result):
    return json.dumps({
        "status": result.status, "steps": result.steps, "trajectory": result.trajectory,
        "interactions": [i.as_dict(DT) for i in result.interactions],
        "pairs": [p.as_dict(DT) for p in result.pairs],
        "back_ups": [b.as_dict(DT) for b in result.back_ups],
        "handoffs": [h.as_dict() for h in result.handoffs],
        "goal_times": result.goal_times, "collisions": result.collisions, "artefacts": result.artefacts,
    }, sort_keys=True, default=str)


def run_plans(mode, plans, at_s=3.0, scenario=PASSING, name="wide_corridor_head_on", spec=None, **overrides):
    """Run a shipped scenario plainly until ``at_s``, give ``plans`` (agent -> reply-format steps),
    run to the end, and return (run, result, outcome columns)."""
    sim = AvoidanceSimulation(spec if spec is not None else crowd(name, **overrides))
    run = X.PlanRun(sim, mode, scenario, (0, 1))
    run.advance({}, at_s)
    run.advance({agent: X.steps_from_dicts(raw, sim.world.agents[agent].spec.max_speed, tuple(scenario.events)) for agent, raw in plans.items()}, math.inf)
    result = run.finish()
    columns = physical_outcome(sim, result, run.driver.track, (0, 1), run.driver.started_step, scenario, result.goal_times)
    return run, result, columns


def records(run, agent, number=1):
    plan = [p for p in run.driver.decisions if p.agent_id == agent][number - 1]
    return [record.as_dict() for record in plan.records]


# --- the issue's list -----------------------------------------------------------------------------


def test_head_on_both_swerving_to_their_own_left_does_not_collide_in_plan_only():
    run, result, columns = run_plans(X.MODE_PLAN_ONLY, {0: LEFT, 1: LEFT})
    assert result.status == "completed"
    assert not columns["collision"] and not columns["near_miss"] and not columns["deadlock"]
    assert columns["resolved"] and columns["cleared"]
    assert columns["passing_side_a"] == columns["passing_side_b"] == "left"
    assert columns["who_passed_first"] == "together"
    assert run.driver.release_reason == X.RELEASE_PASSED


def test_one_left_and_one_right_in_a_narrow_corridor_collide_or_nearly_in_plan_only():
    _, _, columns = run_plans(X.MODE_PLAN_ONLY, {0: LEFT, 1: RIGHT}, geometry={"width": 1.2})
    assert columns["collision"] or columns["near_miss"]
    assert not columns["resolved"]


def test_back_up_then_wait_until_the_other_passes():
    back_and_wait = [{"back_up_m": 1.0}, {"speed_mps": 0, "until": "other_passes"}]
    run, result, columns = run_plans(X.MODE_PLAN_ONLY, {0: back_and_wait, 1: [{"turn": {"to": "left", "degrees": 35}, "until": "other_passes"}]})
    first, second = records(run, 0)
    assert first["ended_by"] == X.ENDED_BACKED_UP and second["ended_by"] == "other_passes"
    assert second["start_step"] == first["end_step"]
    assert columns["backed_up_a"] and columns["stopped_a"] and not columns["backed_up_b"]
    assert columns["backed_distance_a_m"] == pytest.approx(1.0, abs=0.01)
    assert columns["resolved"] and result.goal_times[0] is not None  # after its plan it walked on to its goal
    # Backing up in a plan is intentional: never counted as the walking-backwards artefact.
    assert result.artefacts["agents"]["0"]["backward_episodes"] == 0


@pytest.mark.parametrize("start, check", [
    ({"at_distance_m": 4}, lambda sim, k: math.dist(*(sim[k].bodies[a].xy for a in (0, 1))) <= 4.0 + 1e-9),
    ({"after_seconds": 1.5}, lambda sim, k: sim[k].time_s >= 4.5 - 1e-9),
])
def test_a_delayed_start_waits(start, check):
    run, _, _ = run_plans(X.MODE_PLAN_ORCA, {0: [{"start": start, **LEFT[0]}], 1: [{"start": start, **LEFT[0]}]})
    began = records(run, 0)[0]["start_step"]
    track = {row.step: row for row in run.driver.track}  # the state at the start of step k is row k
    assert began > 30
    assert check(track, began) and not check(track, began - 1)


def test_until_other_passes_ends_on_the_first_step_on_which_the_other_is_behind_and_getting_further():
    run, _, _ = run_plans(X.MODE_PLAN_ONLY, {0: LEFT, 1: LEFT})
    ended = records(run, 0)[0]["end_step"]
    spec = run.simulation.world.agents[0].spec

    def passed(k):
        me, other = run.driver.track[k - 1].bodies[0], run.driver.track[k - 1].bodies[1]
        assert run.driver.track[k - 1].step == k
        heading = spec.path.heading_at(me.path_s)
        rx, ry = other.x - me.x, other.y - me.y
        behind = rx * math.cos(heading) + ry * math.sin(heading) < 0.0
        return behind and rx * (other.vx - me.vx) + ry * (other.vy - me.vy) > 0.0

    assert passed(ended) and not any(passed(k) for k in range(31, ended))


@pytest.mark.parametrize("name", ["wide_corridor_head_on", "overtaking", "passage_meet_middle_v1", "bidirectional_flow"])
def test_empty_plans_in_plan_orca_reproduce_plain_orca_exactly(name):
    plain = AvoidanceSimulation(crowd(name)).run()
    sim = AvoidanceSimulation(crowd(name))
    run = X.PlanRun(sim, X.MODE_PLAN_ORCA, PASSING, (0, 1))
    run.advance({}, 2.0)
    run.advance({0: (), 1: ()}, math.inf)
    assert result_json(run.finish()) == result_json(plain)
    assert [p.outcome for p in run.driver.decisions] == ["completed", "completed"]


def test_empty_plans_in_plan_orca_reproduce_a_cases_perturbed_baseline_run_exactly():
    plan = source_plan(CaseStore().get("head_on_02dfbadb", 2))
    plain = simulation_for(plan).run()
    driver = X.PlanDriver(X.MODE_PLAN_ORCA, PASSING, (0, 1))
    driver.schedule(30, 0, ())
    driver.schedule(30, 1, ())
    assert result_json(simulation_for(plan, driver).run()) == result_json(plain)


class ToyScenario(Scenario):
    """A scenario of its own: an event the executor has never heard of, and a column of its own."""

    DATA = {
        "template_id": "scenario_toy", "version": 1, "kind": "resolution_scenario", "description": "a test",
        "place": {}, "events": {"i_have_walked_2_m": "until you have walked 2 m"}, "extra_blocks": {}, "factor_lines": {},
    }

    def happened(self, event, context):
        if event != "i_have_walked_2_m":
            return super().happened(event, context)
        start = context.memory.setdefault("from", context.agent.pose.xy)
        return math.dist(start, context.agent.pose.xy) >= 2.0

    def zone_exits(self, simulation, track, agents, start_step):
        return {agent: track[-1].time_s for agent in agents}

    def outcome_columns(self, simulation, track, agents, start_step, general):
        return {"toy_walked_m": round(math.dist(track[0].bodies[0].xy, track[-1].bodies[0].xy), 3)}

    def resolved(self, columns):
        return not columns["collision"]


def test_a_toy_scenarios_own_event_and_outcome_column_work_without_changing_the_executor():
    toy = ToyScenario("scenario_toy_v1", ToyScenario.DATA, "0" * 64)
    run, _, columns = run_plans(X.MODE_PLAN_ONLY, {0: [{"speed_mps": 0.5, "until": "i_have_walked_2_m"}], 1: []}, scenario=toy)
    record = records(run, 0)[0]
    assert record["ended_by"] == "i_have_walked_2_m"
    assert (record["end_time_s"] - record["start_time_s"]) == pytest.approx(2.0 / 0.5, abs=0.15)
    assert "toy_walked_m" in columns and columns["resolved"] == (not columns["collision"])
    with pytest.raises(TurnParseError):
        steps([{"speed_mps": 1.0, "until": "i_have_walked_2_m"}])  # the passing scenario has no such event


def test_a_run_with_no_driver_is_unchanged_and_a_watching_driver_changes_nothing():
    for name in ("wide_corridor_head_on", "passage_meet_middle_v1"):
        plain = AvoidanceSimulation(crowd(name)).run()
        assert result_json(AvoidanceSimulation(crowd(name), plans=None).run()) == result_json(plain)
        watched = AvoidanceSimulation(crowd(name), plans=X.PlanDriver(X.MODE_PLAN_ONLY, PASSING, (0, 1))).run()
        assert result_json(watched) == result_json(plain)


# --- the executor in detail -----------------------------------------------------------------------


def test_a_turn_offsets_the_preferred_direction_from_the_path_by_its_degrees_and_speed_sets_its_length():
    run, result, _ = run_plans(X.MODE_PLAN_ONLY, {0: [{"turn": {"to": "left", "degrees": 25}, "speed_mps": 1.1, "until": {"seconds": 1}}], 1: []})
    row = next(r for r in result.trajectory if r["agent_id"] == 0 and r["step"] == 30)
    assert row["control_mode"] == MODE_PLAN
    angle = math.degrees(math.atan2(row["pref_vy_mps"], row["pref_vx_mps"]))
    assert math.hypot(row["pref_vx_mps"], row["pref_vy_mps"]) == pytest.approx(1.1, abs=1e-3)
    assert angle == pytest.approx(25.0, abs=0.5)  # agent 0 walks along +x on the centre line: its left is +y
    assert records(run, 0)[0]["end_step"] == 40


def test_a_step_without_a_speed_walks_at_the_agents_own_speed_and_speed_zero_stands_still():
    _, result, _ = run_plans(X.MODE_PLAN_ONLY, {0: [{"turn": {"to": "right", "degrees": 10}, "until": {"seconds": 1}}], 1: [{"speed_mps": 0, "until": {"seconds": 1}}]})
    mine = next(r for r in result.trajectory if r["agent_id"] == 0 and r["step"] == 31)
    theirs = next(r for r in result.trajectory if r["agent_id"] == 1 and r["step"] == 31)
    assert math.hypot(mine["pref_vx_mps"], mine["pref_vy_mps"]) == pytest.approx(1.3, abs=1e-6)
    assert theirs["pref_vx_mps"] == theirs["pref_vy_mps"] == 0.0


def test_plan_only_ignores_only_the_encounters_pair_and_only_while_the_encounter_is_on():
    driver = X.PlanDriver(X.MODE_PLAN_ONLY, PASSING, (0, 1))
    assert not driver.ignores(0, 1)  # not begun
    sim = AvoidanceSimulation(crowd("bidirectional_flow"))
    run = X.PlanRun(sim, X.MODE_PLAN_ONLY, PASSING, (0, 1))
    run.advance({0: steps(LEFT)}, 0.5)
    assert run.driver.ignores(0, 1) and run.driver.ignores(1, 0)
    assert not run.driver.ignores(0, 2) and not run.driver.ignores(2, 3)
    orca = X.PlanDriver(X.MODE_PLAN_ORCA, PASSING, (0, 1))
    orca.started_step = 0
    assert not orca.ignores(0, 1)


def test_plan_only_frees_the_encounter_of_the_arbiter_and_plan_orca_keeps_it():
    wait = [{"speed_mps": 1.3, "until": {"seconds": 3}}]
    rows = {}
    for mode in X.MODES:
        _, result, _ = run_plans(mode, {0: wait, 1: wait}, at_s=0.0, name="passage_meet_middle_v1", geometry={"start_speed": "preferred"})
        rows[mode] = [r for r in result.trajectory if r["agent_id"] == 1 and r["speed_bound_mps"] is not None and r["speed_bound_mps"] < 1.3]
    held = rows[X.MODE_PLAN_ORCA]
    assert held, "the arbiter makes agent 1 the follower in this passage"
    assert all(math.hypot(r["pref_vx_mps"], r["pref_vy_mps"]) <= r["speed_bound_mps"] + 1e-3 for r in held)
    free = [r for r in rows[X.MODE_PLAN_ONLY] if r["step"] < 30]
    assert free and all(math.hypot(r["pref_vx_mps"], r["pref_vy_mps"]) == pytest.approx(1.3, abs=2e-3) for r in free)


def test_a_later_decision_replaces_what_is_left_of_the_plan():
    sim = AvoidanceSimulation(crowd("wide_corridor_head_on"))
    run = X.PlanRun(sim, X.MODE_PLAN_ONLY, PASSING, (0, 1))
    run.advance({0: steps([{"speed_mps": 1.0, "until": {"seconds": 5}}])}, 2.0)
    state = run.advance({0: steps(LEFT), 1: steps(LEFT)}, 3.0)
    assert state.outcomes[0] == ("replaced", "ongoing") and state.outcomes[1] == ("ongoing",)
    first = [p for p in run.driver.decisions if p.agent_id == 0][0]
    assert first.records[-1].ended_by == X.ENDED_REPLACED and first.ended_step == 20
    assert [p.decision_point for p in run.driver.decisions] == [1, 2, 1]
    state = run.advance({}, math.inf)
    assert state.finished and state.outcomes[0] == ("replaced", "completed")


def test_other_stops_and_after_the_last_step_the_agent_steers_back_to_its_goal():
    run, result, _ = run_plans(
        X.MODE_PLAN_ONLY,
        {0: [{"speed_mps": 0.6, "until": "other_stops"}], 1: [{"speed_mps": 0, "until": {"seconds": 2}}]},
    )
    record = records(run, 0)[0]
    assert record["ended_by"] == "other_stops"
    stopped_at = next(row.step for row in run.driver.track if row.step > 30 and row.bodies[1].speed_mps < 0.01)
    assert record["end_step"] == stopped_at  # the first step whose starting state has the other below 0.01 m/s
    after = next(r for r in result.trajectory if r["agent_id"] == 0 and r["step"] == record["end_step"])
    assert math.hypot(after["pref_vx_mps"], after["pref_vy_mps"]) == pytest.approx(1.3, abs=1e-6)


def test_i_am_out_of_the_stretch_ends_when_the_agent_has_backed_out_of_the_passage():
    # Each has walked 1.7 m into a 4 m passage; agent 0 backs up 3 m but ends the step as soon as it is out.
    run, _, columns = run_plans(
        X.MODE_PLAN_ONLY,
        {0: [{"back_up_m": 3.0, "until": "i_am_out_of_the_stretch"}], 1: [{"speed_mps": 0, "until": {"seconds": 1}}]},
        at_s=0.0, name="passage_meet_middle_v1",
    )
    record = records(run, 0)[0]
    assert record["ended_by"] == "i_am_out_of_the_stretch"
    segment = run.simulation.spec.single_file_segments[0].rect
    at_end = run.driver.track[record["end_step"] - 1].bodies[0]
    assert not (segment.xmin <= at_end.x <= segment.xmax)
    assert 1.6 < columns["backed_distance_a_m"] < 3.0
    assert columns["conflict_zone"].startswith("single_file_segment:")


def test_an_agent_that_is_never_in_a_stretch_never_gets_out_of_one():
    run, _, _ = run_plans(X.MODE_PLAN_ONLY, {0: [{"speed_mps": 1.0, "until": "i_am_out_of_the_stretch"}], 1: LEFT})
    assert records(run, 0)[0]["ended_by"] != "i_am_out_of_the_stretch"


def test_a_release_hands_the_encounter_back_to_orca():
    sim = AvoidanceSimulation(crowd("wide_corridor_head_on", geometry={"lateral_offsets": [0.1, -0.1]}))
    run = X.PlanRun(sim, X.MODE_PLAN_ONLY, PASSING, (0, 1))
    run.advance({0: (), 1: ()}, 3.0)
    assert run.driver.active and run.driver.ignores(0, 1)
    run.release("not_resolved_by_the_llm")
    run.advance({}, 3.1)
    assert not run.driver.active and not run.driver.ignores(0, 1)
    assert run.driver.release_record() == {"step": 30, "reason": "not_resolved_by_the_llm"}
    result = run.finish()
    assert result.collisions["agent_agent"] == 0  # ORCA took over in time


def test_steps_from_dicts_uses_the_parsers_checks():
    assert steps([]) == ()
    assert steps(LEFT)[0] == Step(turn=steps(LEFT)[0].turn, speed_mps=1.3, until=steps(LEFT)[0].until)
    for bad in ([{"speed_mps": 3.0, "until": {"seconds": 1}}], [{"speed_mps": 1.0}], [{"turn": {"to": "up", "degrees": 5}, "until": {"seconds": 1}}]):
        with pytest.raises(TurnParseError):
            steps(bad)
    with pytest.raises(ValueError):
        steps([{"back_up_m": 1.0, "speed_mps": 1.0}])  # a speed on a back-up step is not the reply format
    with pytest.raises(ValueError):
        X.PlanDriver("orca_only", PASSING, (0, 1))
    with pytest.raises(ValueError):
        X.PlanDriver(X.MODE_PLAN_ONLY, PASSING, (0, 0))


# --- the outcome columns, the replay and its rebuild -----------------------------------------------


SESSION = {
    "session_id": "test_head_on_keep_left",
    "case": {"case_id": "head_on_02dfbadb", "version": 2},
    "scenario": "passing",
    "encounter": {"agents": [0, 1]},
    "decisions": [
        {"agent_id": 0, "decision_point": 1, "step": 30, "time_s": 3.0,
         "steps": [{"start": {"at_distance_m": 6}, "turn": {"to": "left", "degrees": 15}, "speed_mps": 1.2, "until": "other_passes"}]},
        {"agent_id": 1, "decision_point": 1, "step": 30, "time_s": 3.0, "steps": [{"turn": {"to": "left", "degrees": 15}, "until": "other_passes"}]},
        {"agent_id": 1, "decision_point": 2, "step": 45, "time_s": 4.5, "steps": [{"speed_mps": 1.0, "turn": {"to": "left", "degrees": 10}, "until": "other_passes"}]},
    ],
    "release": None,
}


@pytest.fixture(scope="module")
def replayed(tmp_path_factory):
    out = tmp_path_factory.mktemp("replays")
    rows = R.replay_sessions([SESSION], "test_rf4", out, GIT)
    return out, rows


def test_hand_written_plans_run_in_both_modes_and_fill_every_physical_column(replayed):
    out, rows = replayed
    assert [row["mode"] for row in rows] == ["plan_only", "plan_orca", "plain_orca"]
    for row in rows:
        assert set(GENERAL_COLUMNS) <= set(row) and "conflict_zone" in row and "resolved" in row
        empty = [key for key in GENERAL_COLUMNS if row[key] is None]
        assert empty == ["collision_kinds"], (row["mode"], empty)  # no collision: no kind to name
    assert rows[0]["resolved"] and rows[1]["resolved"]
    assert rows[2]["min_separation_m"] == CaseStore().get("head_on_02dfbadb", 2)["baseline_outcome"]["min_separation_m"]
    folder = R.session_dir(out, "test_rf4", SESSION["session_id"])
    for mode in X.MODES:
        outcome = json.loads((folder / mode / "outcome.json").read_text(encoding="utf-8"))
        block = outcome["plans"]
        assert block["seed"] == 30102 and block["mode"] == mode
        assert block["scenario_sha256"] == CaseStore().get("head_on_02dfbadb", 2)["scenario"]["resolved_sha256"]
        assert block["plans_sha256"] == R.plans_sha256(SESSION)
        assert [d["outcome"] for d in block["driver"]["decisions"]] == ["completed", "replaced", "completed"]
    assert (out / "test_rf4" / "replay" / R.OUTCOMES_FILE).read_text(encoding="utf-8").count("\n") == 4


def test_a_replay_is_rebuilt_byte_for_byte_from_the_session_record_alone(replayed):
    out, _ = replayed
    folder = R.session_dir(out, "test_rf4", SESSION["session_id"])
    for mode in X.MODES:
        assert R.verify(json.loads(json.dumps(SESSION)), mode, folder / mode) == []
    other = json.loads(json.dumps(SESSION))
    other["decisions"][0]["steps"][0]["speed_mps"] = 1.1
    assert R.verify(other, "plan_only", folder / "plan_only")[0].endswith("(plans_sha256 differs)")


def test_the_live_run_and_the_replay_of_its_log_are_the_same_run(tmp_path):
    plan = source_plan(CaseStore().get("head_on_02dfbadb", 2))
    sim = simulation_for(plan)
    run = X.PlanRun(sim, X.MODE_PLAN_ONLY, PASSING, (0, 1))
    run.advance({}, 3.0)
    run.advance({0: steps(SESSION["decisions"][0]["steps"]), 1: steps(SESSION["decisions"][1]["steps"])}, 4.5)
    run.advance({1: steps(SESSION["decisions"][2]["steps"])}, math.inf)
    live = run.finish()
    session = {**SESSION, "decisions": run.driver.decisions_record(), "release": run.driver.release_record()}
    assert [(d["agent_id"], d["step"], d["steps"]) for d in session["decisions"]] == [(d["agent_id"], d["step"], d["steps"]) for d in SESSION["decisions"]]
    driver = R.driver_for(session, X.MODE_PLAN_ONLY, plan, PASSING)
    assert result_json(simulation_for(plan, driver).run()) == result_json(live)


def test_the_cli_replays_and_verifies(tmp_path, capsys):
    path = tmp_path / "session.json"
    path.write_text(json.dumps({**SESSION, "decisions": SESSION["decisions"][:2]}), encoding="utf-8")
    assert R.main([str(path), "--experiment", "cli_rf4", "--out", str(tmp_path / "runs"), "--mode", "plan_orca"]) == 0
    assert (tmp_path / "runs" / "cli_rf4" / "replay" / SESSION["session_id"] / "plan_orca" / "outcome.json").is_file()
    assert not (tmp_path / "runs" / "cli_rf4" / "replay" / SESSION["session_id"] / "plan_only").exists()
    assert R.main([str(path), "--experiment", "cli_rf4", "--out", str(tmp_path / "runs"), "--mode", "plan_orca", "--verify"]) == 0
    assert "plan_orca: the same" in capsys.readouterr().out


def test_a_bad_session_is_refused():
    for change in ({"decisions": []}, {"encounter": {"agents": [0]}}, {"decisions": [{**SESSION["decisions"][0], "agent_id": 5}]},
                   {"decisions": list(reversed(SESSION["decisions"]))}):
        with pytest.raises(R.SessionError):
            R.check_session({**SESSION, **change})
    with pytest.raises(R.SessionError):
        R.check_session({key: value for key, value in SESSION.items() if key != "case"})


def test_the_report_gives_the_rate_per_encounter_type_and_mode_beside_plain_orca_and_c0(replayed):
    _, rows = replayed
    text = report(rows, [{"experiment": "c0_no_llm_doorway", "scenario": "doorway", "runs": 18, "resolved": 18}])
    assert "| head_on | plan_only | 1 | 1/1 (100%) |" in text
    assert "| head_on | plain_orca | 1 | 0/1 (0%) |" in text  # the case's own baseline was a near miss (T3)
    assert "| c0_no_llm_doorway | doorway | 18 | 18/18 (100%) |" in text
    assert "No C0 runs were found." in report(rows, [])
