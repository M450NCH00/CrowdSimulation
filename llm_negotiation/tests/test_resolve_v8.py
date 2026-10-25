"""Issue #101 (RF-29): ``resolve_v8``, a sidestep by an amount in metres, alongside turning by degrees.

The user's decisions of 2026-10-25: a sidestep walks at the step's ``turn`` angle (30° without one)
until the agent is that far aside, then the agent walks on parallel to its line; the step ends
there or at its ``until`` if that comes first; ``metres`` is more than 0 and at most 3; the
template is ``resolve_v6`` plus the option. Every earlier template reads and runs as before.
"""

from __future__ import annotations

import json
import math

import pytest

from negsim.negotiation import prompts
from negsim.negotiation.parsing import TurnParseError
from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution.prompt import CoreTemplate
from negsim.resolution.protocol import code_plan
from negsim.resolution.reply import ReplyContext, Sidestep, parse_reply
from test_encounter_protocol import HEAD_ON, session_on
from test_execute import EVENTS, records, run_plans
from test_perceive import PASSING

V6, V8 = CoreTemplate.load("resolve_v6"), CoreTemplate.load("resolve_v8")


def context(core, distance=9.0):
    return ReplyContext("independent", 2.0, EVENTS, distance, core.later_step_start, core.until_at_distance, core.until_event_as_object, core.sidestep)


def raw(*steps):
    return json.dumps({"intent": "Make room.", "steps": list(steps), "reason": "r"})


# --- the template ----------------------------------------------------------------------------------


def test_resolve_v8_is_resolve_v6_but_for_the_sidestep_line_the_until_exception_and_the_flag():
    assert prompts.load_manifest()["resolve_v8"]["kind"] == "resolution"
    assert (V6.sidestep, V8.sidestep) == (False, True)
    keys = set(V8.data) - {"version", "provenance", "sidestep"}
    assert keys == set(V6.data) - {"version", "provenance"}
    for key in keys - {"step_format"}:
        assert V8.data[key] == V6.data[key], key
    old, new = V6.data["step_format"].splitlines(), V8.data["step_format"].splitlines()
    added = [line for line in new if line not in old]
    removed = [line for line in old if line not in new]
    assert len(new) == len(old) + 1 and len(added) == 2 and len(removed) == 1
    assert added[0].startswith('"sidestep"') and "metres" in added[0] and "30 degrees" in added[0]
    assert removed[0].startswith('"until"') and added[1] == removed[0].replace("walks backwards.", "walks backwards or sidesteps.")
    for condition in ("independent", "non_verbal", "talk"):
        assert '"sidestep"' in V8.system(condition, PASSING) and '"sidestep"' not in V6.system(condition, PASSING)
        assert V8.retry(condition) == V6.retry(condition)


@pytest.mark.parametrize("key", ["resolve_v1", "resolve_v2", "resolve_v3", "resolve_v4", "resolve_v5", "resolve_v6", "resolve_v7"])
def test_no_earlier_template_has_the_sidestep_flag(key):
    assert not CoreTemplate.load(key).sidestep


# --- the reply parser -------------------------------------------------------------------------------


def test_a_sidestep_is_read_and_needs_no_until():
    reply = parse_reply(raw({"speed_mps": 1.2, "sidestep": {"to": "Right", "metres": 0.6}}), context(V8))
    (step,) = reply.steps
    assert step.sidestep == Sidestep("right", 0.6) and step.until is None and not reply.flags
    assert step.as_dict() == {"speed_mps": 1.2, "sidestep": {"to": "right", "metres": 0.6}}
    both = parse_reply(raw({"turn": {"to": "left", "degrees": 15}, "sidestep": {"to": "left", "metres": 0.5}, "until": "other_passes"}), context(V8))
    assert both.steps[0].turn.degrees == 15 and both.steps[0].until.event == "other_passes"


@pytest.mark.parametrize(("step", "code"), [
    ({"sidestep": {"to": "right", "metres": 0}}, "sidestep_out_of_range"),
    ({"sidestep": {"to": "right", "metres": -0.5}}, "sidestep_out_of_range"),
    ({"sidestep": {"to": "right", "metres": 3.5}}, "sidestep_out_of_range"),
    ({"sidestep": {"to": "up", "metres": 0.5}}, "unknown_sidestep_side"),
    ({"sidestep": {"to": "right"}}, "unknown_sidestep"),
    ({"sidestep": {"to": "right", "metres": 0.5, "speed": 1}}, "unknown_sidestep"),
    ({"sidestep": "right"}, "unknown_sidestep"),
    ({"sidestep": {"to": "right", "metres": "far"}}, "sidestep_not_a_number"),
    ({"sidestep": {"to": "right", "metres": 0.5}, "back_up_m": 1.0}, "sidestep_with_back_up"),
    ({"sidestep": {"to": "right", "metres": 0.5}, "speed_mps": 0}, "sidestep_standing_still"),
    ({"sidestep": {"to": "right", "metres": 0.5}, "turn": {"to": "left", "degrees": 20}}, "sidestep_turn_other_side"),
])
def test_a_bad_sidestep_is_unreadable(step, code):
    with pytest.raises(TurnParseError) as caught:
        parse_reply(raw(step), context(V8))
    assert caught.value.code == code


def test_without_the_flag_a_sidestep_is_an_unknown_key_as_before():
    with pytest.raises(TurnParseError) as caught:  # no until, and the sidestep does not count
        parse_reply(raw({"sidestep": {"to": "right", "metres": 0.5}}), context(V6))
    assert caught.value.code == "missing_until"
    reply = parse_reply(raw({"sidestep": {"to": "right", "metres": 0.5}, "until": {"seconds": 2}}), context(V6))
    assert reply.steps[0].sidestep is None and reply.flags == ("unknown_step_key:steps[0].sidestep",)


def test_a_sidestep_codes_its_side_and_a_recorded_one_reads_back():
    reply = parse_reply(raw({"sidestep": {"to": "left", "metres": 0.5}}), context(V8))
    assert code_plan(reply.steps, 1.3)["side"] == "left"
    back = X.steps_from_dicts([step.as_dict() for step in reply.steps], 2.0, EVENTS)
    assert back == reply.steps


# --- carrying it out ----------------------------------------------------------------------------------


SIDESTEP_LEFT = [{"speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.4}}]


def angle_during(run, agent, record):
    """The direction of travel (degrees, + to the left of +x) of the moves a record ran, but the
    last, clipped one. A track row is the state after its step's move, so the step that began the
    record still shows the old heading."""
    rows = [row for row in run.driver.track if record["start_step"] < row.step < record["end_step"]]
    assert rows
    return [math.degrees(math.atan2(row.bodies[agent].vy, row.bodies[agent].vx)) for row in rows]


@pytest.mark.parametrize(("plan", "degrees"), [
    (SIDESTEP_LEFT, X.DEFAULT_SIDESTEP_DEGREES),
    ([{"speed_mps": 1.3, "turn": {"to": "left", "degrees": 15}, "sidestep": {"to": "left", "metres": 0.4}}], 15.0),
])
def test_a_sidestep_moves_aside_at_its_angle_ends_at_its_distance_and_keeps_the_new_line(plan, degrees):
    run, _, _ = run_plans(X.MODE_PLAN_ONLY, {0: plan, 1: []}, execution=X.EXECUTION_AS_PROMPTED)
    (record,) = records(run, 0)
    assert record["ended_by"] == X.ENDED_SIDESTEPPED and record["aside_m"] == pytest.approx(0.4, abs=X.SIDESTEP_DONE_EPS_M)
    assert all(abs(a - degrees) < 0.5 for a in angle_during(run, 0, record))
    track = {row.step: row.bodies[0] for row in run.driver.track}
    start_y = track[record["start_step"] - 1].y
    after = [track[k].y for k in range(record["end_step"], record["end_step"] + 10) if k in track]
    assert after and all(abs(y - (start_y + 0.4)) < 0.01 for y in after)  # walks on parallel to its line


def test_an_until_that_comes_sooner_ends_the_sidestep_part_way():
    plan = [{"speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.4}, "until": {"seconds": 0.3}}]
    run, _, _ = run_plans(X.MODE_PLAN_ONLY, {0: plan, 1: []}, execution=X.EXECUTION_AS_PROMPTED)
    (record,) = records(run, 0)
    assert record["ended_by"] == X.ENDED_SECONDS and 0.0 < record["aside_m"] < 0.4


def test_a_step_without_a_sidestep_records_no_aside():
    run, _, _ = run_plans(X.MODE_PLAN_ONLY, {0: [{"speed_mps": 1.3, "until": {"seconds": 1}}], 1: []}, execution=X.EXECUTION_AS_PROMPTED)
    assert "aside_m" not in records(run, 0)[0]


def test_a_session_under_resolve_v8_reads_and_carries_out_a_sidestep_and_resolve_v6_does_not():
    answer = raw({"speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.5}})
    _, record, _ = session_on(HEAD_ON, "independent", {0: answer, 1: answer}, core=V8)
    for point in record["decision_points"]:
        assert point["parse_error"] is None and point["plan_given"] == [{"speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.5}}]
        assert point["coded"]["side"] == "right"
    assert '"sidestep"' in record["decision_points"][0]["prompt"]["messages"][0]["content"]
    _, old, _ = session_on(HEAD_ON, "independent", {0: answer, 1: answer}, core=V6)
    assert all(point["parse_error"].startswith("missing_until") for point in old["decision_points"])


# --- the config ----------------------------------------------------------------------------------------


def test_rf29s_config_is_rf10s_independent_sessions_with_only_the_template_changed():
    old = E.ResolutionConfig.load("configs/resolution/round1_head_on_screening.yaml")
    new = E.ResolutionConfig.load("configs/resolution/round1_head_on_sidestep.yaml")
    assert new.experiment_name == "rf29_round1_head_on_sidestep" and new.conditions == ("independent",)
    assert new.templates["core"] == "resolve_v8" and {k: v for k, v in new.templates.items() if k != "core"} == {k: v for k, v in old.templates.items() if k != "core"}
    assert new.llm == old.llm and new.budget["cap_usd"] == 0.08 and new.budget["over_cap"] == "stop_at_cap"
    old_sessions = {s.session_id: s for s in E.plan(old).sessions if s.condition == "independent"}
    new_sessions = {s.session_id: s for s in E.plan(new).sessions}
    assert set(new_sessions) == set(old_sessions) and len(new_sessions) == 96
    for session_id, session in new_sessions.items():
        assert session.personas == old_sessions[session_id].personas, session_id
