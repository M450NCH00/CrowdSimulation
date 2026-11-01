"""Issue #127 (RF-39): the sidestep with a second chance.

``resolve_v8`` (the sidestep in metres) in the non-verbal and talk conditions, where an agent may be
prompted again (D5). Before any paid call (the lesson of RF-29, issue #101): a later decision that
replaces a sidestep part-way is carried out as it says, and ``keep_line_replan`` keeps the line a
step took the agent to across a later decision, where ``keep_line`` steers it back to its path while
a new plan's first step waits and after a plan of no steps (``[]``, "carry on as you are").
"""

from __future__ import annotations

import json
import math

import pytest

from helpers import crowd
from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution import protocol as P
from negsim.negotiation.parsing import TurnParseError
from negsim.resolution.mock import debrief_paths_v1
from negsim.resolution.prompt import CoreTemplate, DebriefTemplate
from negsim.resolution.reply import SIDE_BASES, parse_debrief
from negsim.llm.base import LLMRequest
from test_encounter_protocol import HEAD_ON, points_of, session_on
from test_execute import EVENTS, PASSING, records, run_plans

V8 = CoreTemplate.load("resolve_v8")
CONFIG = "configs/resolution/round1_head_on_sidestep_reprompt.yaml"

SIDESTEP_RIGHT_THEN_WALK = [{"speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.4}}, {"speed_mps": 1.3, "until": {"seconds": 3}}]
REPLANS = {
    "waits_seconds": [{"start": {"after_seconds": 1.0}, "speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.8}}],
    "waits_distance": [{"start": {"at_distance_m": 2.0}, "speed_mps": 1.3, "turn": {"to": "left", "degrees": 20}, "until": "other_passes"}],
    "carry_on": [],
}


def replan_part_way(second, execution):
    """Agent 0 sidesteps 0.4 m to its right from 3.0 s; at 3.4 s, part-way, a later decision gives it
    ``second``. Returns (the run, y at the start, y when replaced, y every 0.1 s for the next 0.8 s)."""
    sim = AvoidanceSimulation(crowd("wide_corridor_head_on"))
    run = X.PlanRun(sim, X.MODE_PLAN_ONLY, PASSING, (0, 1), execution)
    run.advance({}, 3.0)
    y0 = sim.world.agents[0].pose.y
    run.advance({0: X.steps_from_dicts(SIDESTEP_RIGHT_THEN_WALK, 2.0, EVENTS)}, 3.4)
    replaced_at = sim.world.agents[0].pose.y
    run.advance({0: X.steps_from_dicts(second, 2.0, EVENTS)}, 3.4)
    after = []
    for k in range(1, 9):
        run.advance({}, 3.4 + 0.1 * k)
        after.append(sim.world.agents[0].pose.y)
    return run, y0, replaced_at, after


# --- the executor across a later decision ------------------------------------------------------------


@pytest.mark.parametrize("name", list(REPLANS))
def test_keep_line_replan_keeps_the_line_while_a_later_plan_waits_and_after_carry_on(name):
    _, y0, replaced_at, after = replan_part_way(REPLANS[name], X.EXECUTION_KEEP_LINE_REPLAN)
    assert replaced_at < y0 - 0.15  # part-way through the sidestep to the right
    assert all(y == pytest.approx(replaced_at, abs=0.01) for y in after)  # nothing has begun yet: the line is kept


@pytest.mark.parametrize("name", list(REPLANS))
def test_under_keep_line_the_same_later_plans_steer_back_to_the_path_as_before(name):
    # keep_line is unchanged, so that RF-29's and RF-30's runs re-execute exactly as recorded.
    _, y0, replaced_at, after = replan_part_way(REPLANS[name], X.EXECUTION_KEEP_LINE)
    assert after[-1] > replaced_at + 0.05 and after[-1] < y0


@pytest.mark.parametrize("execution", [X.EXECUTION_KEEP_LINE, X.EXECUTION_KEEP_LINE_REPLAN])
def test_a_later_sidestep_the_other_way_ends_where_it_says_and_keeps_that_line(execution):
    second = [{"speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.8}}, {"speed_mps": 1.3, "until": {"seconds": 3}}]
    run, y0, replaced_at, _ = replan_part_way(second, execution)
    run.advance({}, 6.5)
    first, later = [p for p in run.driver.decisions if p.agent_id == 0]
    assert first.records[-1].ended_by == X.ENDED_REPLACED and first.records[-1].aside_m == pytest.approx(y0 - replaced_at, abs=1e-6)
    sidestep, _ = later.records
    assert sidestep.ended_by == X.ENDED_SIDESTEPPED and sidestep.aside_m == pytest.approx(0.8, abs=X.SIDESTEP_DONE_EPS_M)
    level = replaced_at + 0.8
    track = {row.step: row.bodies[0].y for row in run.driver.track}
    during_walk = [track[k] for k in range(sidestep.end_step, sidestep.end_step + 15) if k in track]
    assert during_walk and all(y == pytest.approx(level, abs=X.SIDESTEP_DONE_EPS_M + 0.01) for y in during_walk)


@pytest.mark.parametrize("plan", [
    SIDESTEP_RIGHT_THEN_WALK,
    [{"speed_mps": 1.3, "turn": {"to": "left", "degrees": 20}, "until": {"seconds": 1}}, {"start": {"after_seconds": 1.0}, "speed_mps": 1.3, "until": {"seconds": 2}}],
    [{"start": {"at_distance_m": 4.0}, "speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.5}}],
    [],
], ids=["sidestep_then_walk", "turn_then_a_waiting_step", "a_waiting_first_step", "carry_on"])
def test_with_one_decision_keep_line_replan_is_keep_line(plan):
    # The independent condition (one decision point) is carried out exactly as under keep_line.
    a = run_plans(X.MODE_PLAN_ONLY, {0: plan, 1: []}, execution=X.EXECUTION_KEEP_LINE)[0].driver.track
    b = run_plans(X.MODE_PLAN_ONLY, {0: plan, 1: []}, execution=X.EXECUTION_KEEP_LINE_REPLAN)[0].driver.track
    assert [(r.bodies[0].x, r.bodies[0].y) for r in a] == [(r.bodies[0].x, r.bodies[0].y) for r in b]


# --- a session: the second prompt reports the sidestep -----------------------------------------------


def answer(*steps, intent="Make room."):
    return json.dumps({"intent": intent, "steps": list(steps), "signal": "none", "reason": "r"})


def test_a_pavement_dance_prompts_again_and_the_prompt_says_how_far_aside_the_agent_moved():
    # Both step to the same wall (0 to its right, 1 to its left): their plan fails, and each is
    # asked again; the second prompt says what the sidestep did.
    dance = {
        0: [answer({"speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.4}}, {"speed_mps": 1.3, "until": "other_passes"}), answer()],
        1: [answer({"speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.4}}, {"speed_mps": 1.3, "until": "other_passes"}), answer()],
    }
    settings = P.ProtocolSettings(execution=X.EXECUTION_KEEP_LINE_REPLAN)
    _, record, _ = session_on(HEAD_ON, "non_verbal", dance, settings=settings, core=V8)
    for agent, side in ((0, "right"), (1, "left")):
        points = points_of(record, agent)
        assert len(points) >= 2 and points[0]["parse_error"] is None, agent
        again = points[1]["prompt"]["messages"][-1]["content"]
        assert "WHAT YOU HAVE DONE SO FAR" in again
        assert f"Since then you have moved 0.4 m over to your {side}." in again, again


# --- the config ----------------------------------------------------------------------------------------


def test_rf39s_config_is_rf30s_sessions_with_resolve_v8_all_three_conditions_and_every_cell_repeated():
    # The user's decisions of 2026-11-01: 4 repeats, three conditions, keep_line_replan, 6 decision
    # points, and the debrief that asks why that side.
    rf30 = E.ResolutionConfig.load("configs/resolution/round1_head_on_keep_line.yaml")
    rf29 = E.ResolutionConfig.load("configs/resolution/round1_head_on_sidestep.yaml")
    new = E.ResolutionConfig.load(CONFIG)
    assert new.experiment_name == "rf39_round1_head_on_sidestep_reprompt"
    assert new.conditions == ("independent", "non_verbal", "talk")
    assert new.templates == {**rf29.templates, "debrief": "resolve_debrief_v2"} and new.templates["core"] == "resolve_v8"
    assert new.protocol.execution == X.EXECUTION_KEEP_LINE_REPLAN and new.protocol.max_decision_points == 6
    changed = ("execution", "max_decision_points")
    assert {k: v for k, v in new.protocol.as_dict().items() if k not in changed} == {k: v for k, v in rf30.protocol.as_dict().items() if k not in changed}
    assert new.llm == rf30.llm and new.resolution_gate == rf30.resolution_gate
    assert new.budget["cap_usd"] == 1.20 and new.budget["over_cap"] == "stop_at_cap"  # the cap CLAUDE.md records for #127
    sessions = E.plan(new).sessions
    assert len(sessions) == 816
    for condition in new.conditions:
        mine = [s for s in sessions if s.condition == condition]
        assert len(mine) == 272 and sum(s.pair_id is None for s in mine) == 256  # 32 cells x 2 geometries x 4, and 16 in pairs
    # Repeat 1 (and every pair) has RF-30's ids and people, and RF-29's for independent.
    old = {s.session_id: s for s in E.plan(rf30).sessions} | {s.session_id: s for s in E.plan(rf29).sessions}
    first = [s for s in sessions if s.pair_id is not None or s.session_id.endswith("_r1")]
    assert len(first) == 3 * (64 + 16)
    for session in first:
        assert session.session_id in old, session.session_id
        assert session.personas == old[session.session_id].personas, session.session_id
    # Every repeat of a cell has the same people as its first run.
    by_id = {s.session_id: s for s in sessions}
    for session in sessions:
        if session.pair_id is None:
            assert session.personas == by_id[session.session_id.rsplit("_r", 1)[0] + "_r1"].personas


# --- the debrief that asks why that side (resolve_debrief_v2) --------------------------------------

D1, D2 = DebriefTemplate.load("resolve_debrief_v1"), DebriefTemplate.load("resolve_debrief_v2")
BASE = {"basis": "Habit.", "kind": "habit", "source": "none", "applies_to": "my first decision"}


def test_resolve_debrief_v2_is_v1_plus_the_side_paragraph_the_two_keys_and_the_flag():
    one, two = D1.data, D2.data
    assert not D1.side_question and D2.side_question
    for key in ("decision", "steps", "no_steps", "said", "signal"):
        assert one[key] == two[key], key
    first, second = one["text"].split("\n\n"), two["text"].split("\n\n")
    assert second[0] == first[0] and second[-1] == first[-1] == "{reply_format}"
    assert second[1].startswith("If you moved to one side, why that side and not the other?") and "either side would have done as well" in second[1]
    for basis in SIDE_BASES:
        assert f'"{basis}"' in two["reply_format"], basis
    assert set(two["reply_format"].splitlines()) >= set(one["reply_format"].splitlines()[:-1])


@pytest.mark.parametrize(("extra", "basis", "flags"), [
    ({"side_basis": "Either_Side", "side_detail": "Both were free."}, "either_side", []),
    ({"side_basis": "keep_left", "side_detail": "x"}, None, ["unknown_side_basis"]),
    ({}, None, ["no_side_basis"]),
])
def test_a_side_answer_is_read_and_a_bad_one_is_flagged_not_refused(extra, basis, flags):
    reply = parse_debrief(json.dumps({**BASE, **extra}), side=True).as_dict()
    assert reply["side_basis"] == basis and reply["flags"] == flags and reply["kind"] == "habit"
    assert reply["side_detail"] == extra.get("side_detail")


def test_without_the_flag_a_debrief_is_read_and_written_as_before():
    plain = parse_debrief(json.dumps(BASE)).as_dict()
    assert "side_basis" not in plain and "side_detail" not in plain
    assert parse_debrief(json.dumps({**BASE, "side_basis": "either_side"})).as_dict() == plain
    with pytest.raises(TurnParseError):
        parse_debrief(json.dumps({**BASE, "kind": "other"}), side=True)  # the rest is checked as before


def test_the_mock_adds_the_side_keys_only_when_the_question_asks_for_them():
    def request(text):
        return LLMRequest(messages=({"role": "user", "content": text},), model="m", temperature=1.0, max_tokens=300, metadata={"path_index": 0})
    assert "side_basis" not in json.loads(debrief_paths_v1(request("Was what you did based on anything?")))
    assert json.loads(debrief_paths_v1(request('... "side_basis": ...')))["side_basis"] in SIDE_BASES


def session_with_debrief(debrief_reply, debrief_template):
    """An independent head-on session under resolve_v8, both sidestepping 0.4 m to their right, each
    debrief answered with ``debrief_reply``."""
    from negsim.experiment.avoidance import simulation_for
    from negsim.llm.mock import MockClient
    from negsim.resolution.scenarios import load_scenario
    from negsim.rulegen.replay import source_plan
    from test_encounter_protocol import LLM
    move = answer({"speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.4}})
    client = MockClient(policy=lambda request: debrief_reply if request.metadata.get("kind") == "debrief" else move)
    run = P.EncounterSession(
        simulation_for(source_plan(HEAD_ON)), HEAD_ON["agents"], load_scenario("passing"), "independent", client, LLM,
        P.ProtocolSettings(execution=X.EXECUTION_KEEP_LINE_REPLAN), core=V8, debrief=debrief_template,
    )
    run.run_session()
    return run.as_dict(), client


def test_a_session_under_resolve_debrief_v2_asks_why_that_side_and_records_the_answer():
    reply = json.dumps({**BASE, "side_basis": "where_they_were", "side_detail": "They were a little to my left."})
    record, client = session_with_debrief(reply, D2)
    asked = [r for r in client.requests if r.metadata.get("kind") == "debrief"]
    assert len(asked) == 2 and all("why that side and not the other?" in r.messages[-1]["content"] for r in asked)
    assert [d["parsed"]["side_basis"] for d in record["debriefs"]] == ["where_they_were"] * 2
    rows = E.debrief_rows({**record, "session_id": "s"})  # an experiment's record names its session
    assert [(row["side_basis"], row["side_detail"]) for row in rows] == [("where_they_were", "They were a little to my left.")] * 2
    # Under resolve_debrief_v1 the same session is asked and recorded as before.
    old, client = session_with_debrief(json.dumps(BASE), D1)
    assert all("why that side" not in r.messages[-1]["content"] for r in client.requests if r.metadata.get("kind") == "debrief")
    assert all("side_basis" not in d["parsed"] for d in old["debriefs"]) and all("side_basis" not in row for row in E.debrief_rows({**old, "session_id": "s"}))
