"""The Step 1 encounter protocol (issue #58, RF-3): the trigger, event-driven decision points and
their guards, the conditions, the end and the hand-over to ORCA, the debrief, the session record,
n-person encounters and the cap, and the resolution experiment's storage, resume and outcome row."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import replace

import pytest

from helpers import crowd
from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.configutil import ConfigError
from negsim.experiment.avoidance import simulation_for
from negsim.experiment.cli import main as cli_main
from negsim.llm.mock import MockClient
from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution import mock as M
from negsim.resolution import protocol as P
from negsim.resolution import scenarios as S
from negsim.resolution.outcomes import physical_outcome
from negsim.resolution.reply import Start, Step, Turn, Until
from negsim.resolution.scenarios.passing import PassingScenario
from negsim.rulegen.cases import CaseStore
from negsim.rulegen.protocol import LLMSettings
from negsim.rulegen.replay import source_plan

LLM = LLMSettings("deepseek-flash", 1.0, 400)
GIT = {"commit": "test", "dirty": False}
STORE = CaseStore()
HEAD_ON = STORE.get("head_on_02dfbadb", 2)
PASSAGE = STORE.get("passage_02fac1e4", 1)
OVERTAKING = STORE.get("overtaking_23c5d31e", 2)
CROWD = STORE.get("flow_ba3c7962", 2)

SWERVE_LEFT = json.dumps({"intent": "Move over to my left.", "steps": [{"turn": {"to": "left", "degrees": 25}, "speed_mps": 1.2, "until": "other_passes"}], "reason": "r"})
SLOW = json.dumps({"intent": "Slow down a little.", "steps": [{"speed_mps": 0.6, "until": {"seconds": 2}}], "reason": "r"})
DEBRIEF = M.DEBRIEF_PATHS["with_source"]


def reply(intent="Carry on.", steps=(), **extra):
    return json.dumps({**extra, "intent": intent, "steps": list(steps), "reason": "r"})


def policy(by_agent, default=M.CARRY_ON):
    """A mock policy: per agent, a reply or a list of replies (one per decision point); debriefs answered."""
    def answer(request):
        meta = request.metadata
        if meta.get("kind") == "debrief":
            return DEBRIEF
        chosen = by_agent.get(meta["agent_id"], default)
        if isinstance(chosen, list):
            return chosen[min(meta["decision_point"], len(chosen)) - 1]
        return chosen
    return answer


def session_on(case, condition, answers, scenario="passing", settings=None, simulation=None, pair=None, **kwargs):
    client = MockClient(policy=policy(answers))
    sim = simulation if simulation is not None else simulation_for(source_plan(case))
    run = P.EncounterSession(
        sim, pair or case["agents"], S.load_scenario(scenario), condition, client, LLM, settings or P.ProtocolSettings(), **kwargs
    )
    run.run_session()
    return run, run.as_dict(), client


def points_of(record, agent=None):
    return [p for p in record["decision_points"] if agent is None or p["agent_id"] == agent]


# --- the trigger (D4) -----------------------------------------------------------------------------


def test_the_trigger_does_not_fire_for_someone_merely_in_view():
    # Two people walking toward each other on lines 2.4 m apart see each other, and the distance
    # between them shrinks, but no conflict is predicted: nobody is ever prompted.
    spec = crowd("wide_corridor_head_on", geometry={"width": 4.0, "lateral_offsets": [-1.2, 1.2]})
    run, record, client = session_on(None, "non_verbal", {}, simulation=AvoidanceSimulation(spec), pair=(0, 1))
    assert record["outcome"] == P.SESSION_NO_ENCOUNTER and not client.requests and not record["decision_points"]
    # On the same lines, 20 cm apart, the trigger fires once the two see each other within 10 m.
    spec = crowd("wide_corridor_head_on", geometry={"lateral_offsets": [-0.1, 0.1]})
    run, record, _ = session_on(None, "independent", {}, simulation=AvoidanceSimulation(spec), pair=(0, 1))
    trigger = record["encounter"]["trigger"]
    assert record["outcome"] == P.SESSION_COMPLETED and trigger is not None
    first = points_of(record)[0]
    assert first["trigger_reasons"][0] == P.REASON_TRIGGER
    seen = first["view"]["seen"]
    assert seen and seen[0]["distance_m"] <= 10.0 + 1e-9


def test_someone_who_cannot_see_the_other_is_not_prompted_at_the_trigger():
    # Overtaking: the one behind sees the one ahead; the one ahead cannot see behind and never
    # hears anything, so only the noticing agent is ever prompted.
    run, record, client = session_on(OVERTAKING, "non_verbal", {0: SWERVE_LEFT})
    assert {p["agent_id"] for p in points_of(record)} == {0}
    assert record["encounter"]["prompted"] == [0]
    assert all(r.metadata["agent_id"] == 0 for r in client.requests)


# --- decision points (D5) and their guards --------------------------------------------------------


def test_nothing_new_means_no_second_decision_point():
    # Both carry on: nobody changes, signals or speaks, so nobody is asked again; they collide.
    _, record, _ = session_on(HEAD_ON, "talk", {0: M.CARRY_ON, 1: M.CARRY_ON})
    assert [p["number"] for p in points_of(record)] == [1, 1]
    assert record["encounter"]["end"]["reason"] == P.END_COLLISION
    assert record["encounter"]["end"]["not_resolved_by_llm"]


def test_the_other_slowing_down_prompts_only_the_one_who_noticed():
    _, record, _ = session_on(HEAD_ON, "non_verbal", {0: SLOW, 1: M.CARRY_ON})
    second = [p for p in points_of(record) if p["number"] == 2]
    noticed = next(p for p in second if p["agent_id"] == 1)
    assert "other_slowed_down:0" in noticed["trigger_reasons"]
    # Agent 0 is not asked on that step: it saw nothing new.
    assert not any(p["agent_id"] == 0 and p["step"] == noticed["step"] for p in second)


def test_a_signal_is_an_event_for_whoever_sees_it():
    wave = reply("Wave them on.", [], signal="wave_on")
    _, record, _ = session_on(HEAD_ON, "non_verbal", {0: wave, 1: M.CARRY_ON})
    assert any("signalled:0" in p["trigger_reasons"] for p in points_of(record, 1))
    assert record["signals"][0]["signal"] == "wave_on" and 1 in record["signals"][0]["seen_by"]


def test_a_message_takes_time_to_say_and_is_an_event_for_whoever_hears_it():
    words = "Go ahead."
    stop = reply("Wait for them.", [{"speed_mps": 0, "until": "other_passes"}])
    _, record, _ = session_on(PASSAGE, "talk", {0: reply("Tell them to go first.", [{"speed_mps": 0, "until": "other_passes"}], message=words), 1: stop})
    said = record["utterances"][0]
    first = points_of(record, 0)[0]
    assert said["time_s"] >= first["time_s"] + len(words.split()) / 2.5 - 0.1 - 1e-9  # heard on the first step after it is said
    assert "1" in said["heard_by"]
    assert any("heard:0" in p["trigger_reasons"] for p in points_of(record, 1))
    later = next(p for p in points_of(record, 1) if "heard:0" in p["trigger_reasons"])
    assert words in later["prompt"]["messages"][1]["content"]


def test_no_message_or_signal_reaches_anyone_in_the_independent_condition():
    _, record, client = session_on(HEAD_ON, "independent", {0: reply("Wave.", [], signal="wave_on", message="Hi"), 1: M.CARRY_ON})
    assert not record["signals"] and not record["utterances"]
    assert "signal_ignored" in points_of(record, 0)[0]["parsed"]["flags"]


@pytest.mark.parametrize("event", ["came_into_view", "plan_failing", "plan_ended", "none"])
def test_each_remaining_event_of_d5_fires_and_nothing_fires_without_one(event):
    # Drive a session to its first decision point, then set up the event by hand and ask.
    sim = simulation_for(source_plan(HEAD_ON))
    plans = {0: M.CARRY_ON, 1: M.CARRY_ON} if event == "none" else {0: SWERVE_LEFT, 1: SWERVE_LEFT}
    run = P.EncounterSession(sim, HEAD_ON["agents"], S.load_scenario("passing"), "non_verbal", MockClient(policy=policy(plans)), LLM)
    assert run._find_trigger()
    run._decision_point([(a, b, ["trigger"]) for a, b in ((0, 1), (1, 0))])
    for _ in range(3):
        sim.step()
        run._after_step()
    member = run.members[0]
    if event == "came_into_view":
        member.perceiver.looks[-1].seen.clear()  # as if it had not seen agent 1 when it last looked
        assert "came_into_view:1" in run._d5(member)
    elif event == "plan_failing":
        member.clear_since_decision = True  # it was clear since it decided; now it is on course again
        sim.world.agents[0].velocity = (1.3, 0.0)
        sim.world.agents[1].velocity = (-1.3, 0.0)
        sim.world.agents[1].pose = replace(sim.world.agents[1].pose, y=sim.world.agents[0].pose.y)
        assert P.REASON_PLAN_FAILING in run._d5(member)
    elif event == "plan_ended":
        plan = run.run.driver.plans[0]
        plan.state = X.COMPLETED
        assert P.REASON_PLAN_ENDED in run._d5(member)
        member.ended_noticed = plan.decision_point  # once asked about it, it is not new any more
        assert P.REASON_PLAN_ENDED not in run._d5(member)
    else:
        assert run._d5(member) == []  # both walk on as they were: nothing new to either


def test_an_empty_plan_never_ends_in_the_sense_of_d5():
    sim = simulation_for(source_plan(HEAD_ON))
    run = P.EncounterSession(sim, HEAD_ON["agents"], S.load_scenario("passing"), "non_verbal", MockClient(policy=policy({})), LLM)
    assert run._find_trigger()
    run._decision_point([(0, 1, ["trigger"])])
    sim.step()
    assert run.run.driver.plans[0].state == X.COMPLETED and not run._plan_ended(run.members[0])


def test_the_one_second_gap_and_the_cap_of_three_hold():
    # Both keep slowing and speeding up: the other always has something new to notice.
    wobble = [SLOW, reply("Speed up again.", [{"speed_mps": 1.3, "until": {"seconds": 1}}]), SLOW]
    _, record, _ = session_on(HEAD_ON, "non_verbal", {0: wobble, 1: wobble})
    for agent in (0, 1):
        times = [p["time_s"] for p in points_of(record, agent)]
        assert 1 < len(times) <= 3
        assert all(b - a >= 1.0 - 1e-9 for a, b in zip(times, times[1:]))
    assert all(p["trigger_reasons"] for p in points_of(record))


def test_the_independent_condition_makes_one_call_per_agent_plus_the_debriefs():
    _, record, client = session_on(HEAD_ON, "independent", {0: SLOW, 1: SWERVE_LEFT})
    kinds = [r.metadata["kind"] for r in client.requests]
    assert kinds.count("decision") == 2 and kinds.count("debrief") == 2
    assert record["totals"]["llm_calls"] == 4


def test_an_unreadable_reply_uses_a_decision_point_and_the_agent_carries_on():
    _, record, client = session_on(HEAD_ON, "independent", {0: M.UNREADABLE, 1: SWERVE_LEFT})
    point = points_of(record, 0)[0]
    assert point["parse_error"] and len(point["attempts"]) == 2 and point["plan_given"] == []
    decision = next(d for d in record["decisions"] if d["agent_id"] == 0)
    assert decision["steps"] == []
    # No readable decision: no debrief for it.
    assert [d["agent_id"] for d in record["debriefs"]] == [1]


def test_a_refusal_mid_decision_point_keeps_every_reply_already_paid_for():
    from negsim.llm.budget import BudgetExceededError

    class RefusesTheSecondAgent(MockClient):
        def complete(self, request):
            if request.metadata.get("agent_id") == 1:
                raise BudgetExceededError("the cap is reached")
            return super().complete(request)

    sim = simulation_for(source_plan(HEAD_ON))
    run = P.EncounterSession(sim, HEAD_ON["agents"], S.load_scenario("passing"), "independent",
                             RefusesTheSecondAgent(policy=policy({0: SWERVE_LEFT})), LLM)
    with pytest.raises(BudgetExceededError):
        run.run_session()
    record = run.as_dict()
    assert record["outcome"] == P.SESSION_ABORTED and "BudgetExceededError" in record["error"]
    (kept,) = record["decision_points"]
    assert kept["agent_id"] == 0 and kept["attempts"][0]["raw_output"] == SWERVE_LEFT and kept["plan_given"] is None
    assert not record["decisions"]  # nothing was carried out


def test_orca_takes_over_when_the_llm_has_nothing_left_and_the_conflict_remains():
    # Each slows once, for 2 s, in the independent condition: then nobody can be asked again.
    _, record, _ = session_on(HEAD_ON, "independent", {0: SLOW, 1: SLOW})
    end = record["encounter"]["end"]
    assert end["reason"] == P.END_ORCA_TOOK_OVER and end["not_resolved_by_llm"]
    assert record["release"] == {"step": end["step"], "reason": P.RELEASE_NOT_RESOLVED}


def test_the_debrief_follows_the_agents_last_decision_point():
    _, record, client = session_on(HEAD_ON, "non_verbal", {0: SLOW, 1: M.CARRY_ON})
    debriefs = [r for r in client.requests if r.metadata["kind"] == "debrief"]
    assert {r.metadata["agent_id"] for r in debriefs} == {0, 1}
    for request in debriefs:
        agent = request.metadata["agent_id"]
        last = points_of(record, agent)[-1]
        assert [m["content"] for m in request.messages[:2]] == [m["content"] for m in last["prompt"]["messages"]]
        assert request.messages[2] == {"role": "assistant", "content": last["attempts"][-1]["raw_output"]}
    assert record["debriefs"][0]["parsed"]["source_status"] == "unchecked"


def test_prompt_history_is_one_line_per_earlier_decision_point_never_the_transcript():
    wobble = [SLOW, reply("Speed up again.", [{"speed_mps": 1.3, "until": {"seconds": 1}}]), SLOW]
    _, record, client = session_on(HEAD_ON, "non_verbal", {0: wobble, 1: wobble})
    for request in client.requests:
        if request.metadata["kind"] == "decision" and request.metadata["attempt"] == 1:
            assert len(request.messages) == 2
    third = next(p for p in points_of(record, 0) if p["number"] == 3)
    assert len(third["view"]["history"]) == 2


# --- what is recorded, and the live run against its replay ----------------------------------------


def test_the_live_run_is_its_replay_up_to_the_end_of_the_encounter(tmp_path):
    run, record, _ = session_on(HEAD_ON, "non_verbal", {0: SLOW, 1: SWERVE_LEFT})
    record = {**record, "session_id": "live", "case": {"case_id": HEAD_ON["case_id"], "version": 2}, "scenario": "passing"}
    record["encounter"]["type"] = "head_on"
    from negsim.resolution.replay import replay_session
    replay_session(record, X.MODE_PLAN_ONLY, tmp_path / "plan_only", "t", GIT, STORE)
    rows = (tmp_path / "plan_only" / "trajectory.csv").read_text(encoding="utf-8").splitlines()
    header = rows[0].split(",")
    end = record["encounter"]["end"]["step"]
    live = {a.agent_id: a.pose.xy for a in run.sim.world.agents}
    compared = set()
    for line in rows[1:]:
        values = dict(zip(header, line.split(",")))
        if values["step"] and int(values["step"]) == end:
            agent = int(values["agent_id"])
            assert float(values["x_m"]) == pytest.approx(live[agent][0], abs=6e-5)  # the file rounds to 4 decimals
            assert float(values["y_m"]) == pytest.approx(live[agent][1], abs=6e-5)
            compared.add(agent)
    assert compared == {0, 1}


def test_code_plan():
    steps = (Step(Start("at_distance_m", 4.0), 0.0, None, None, Until(event="other_passes")), Step(None, None, None, 1.0, None))
    coded = P.code_plan(steps, 1.3)
    assert coded == {"carry_on": False, "n_steps": 2, "side": "none", "slowed": True, "stopped": True, "backed_up": True,
                     "start_distance_m": 4.0, "start_after_s": None}
    turns = (Step(None, 1.3, Turn("left", 10), None, Until(seconds=1)), Step(None, 1.3, Turn("right", 10), None, Until(seconds=1)))
    assert P.code_plan(turns, 1.3)["side"] == "both" and not P.code_plan(turns, 1.3)["slowed"]
    assert P.code_plan((), 1.3)["carry_on"]


def test_protocol_settings_are_checked():
    with pytest.raises(ConfigError):
        P.ProtocolSettings.from_mapping({"max_prompted": 1})
    with pytest.raises(ConfigError):
        P.ProtocolSettings.from_mapping({"unknown": 1})
    assert P.ProtocolSettings().decision_points_for("independent") == 1
    assert P.ProtocolSettings().decision_points_for("talk") == 3


# --- more than two people, and the cap ------------------------------------------------------------


def test_an_encounter_of_more_than_two_people_and_the_cap_on_prompted_people():
    settings = P.ProtocolSettings(max_prompted=3)
    _, record, _ = session_on(CROWD, "independent", {}, scenario="passing_crowd", settings=settings)
    encounter = record["encounter"]
    assert len(encounter["agents"]) == 3 and encounter["left_out_by_cap"]
    assert len(encounter["prompted"]) <= 3
    assert set(encounter["prompted"]) <= set(encounter["agents"])
    assert all(len(pair) == 2 and set(pair) <= set(encounter["agents"]) for pair in encounter["pairs"])
    # Each decision names its partner, so that the replay can read it back.
    assert all("partner_id" in decision for decision in record["decisions"])


def test_a_plan_driver_of_more_than_two_needs_each_plans_partner():
    sim = AvoidanceSimulation(crowd("wide_corridor_head_on"))
    driver = X.PlanDriver(X.MODE_PLAN_ONLY, S.load_scenario("passing"), (0, 1))
    assert driver.partner_of(0) == 1
    with pytest.raises(ValueError):
        X.PlanDriver(X.MODE_PLAN_ONLY, S.load_scenario("passing"), (0, 0))
    big = X.PlanDriver(X.MODE_PLAN_ONLY, S.load_scenario("passing"), (0, 1, 2))
    with pytest.raises(ValueError):
        big.partner_of(0)
    assert big.partner_of(0, 2) == 2
    with pytest.raises(ValueError):
        big.partner_of(0, 0)


def test_the_outcome_of_an_n_person_encounter_needs_every_conflict_pair_resolved():
    passing = S.load_scenario("passing")
    sim = AvoidanceSimulation(crowd("bidirectional_flow", geometry={"agents_per_direction": 2, "length": 12.0}))
    members = (0, 1, 2, 3)
    run = X.PlanRun(sim, X.MODE_PLAN_ORCA, passing, members)
    run.advance({}, 1.0)
    with pytest.raises(ValueError):
        run.advance({0: ()}, 1.1)  # with more than two, a plan must name its partner
    for agent, partner in ((0, 2), (1, 3), (2, 0), (3, 1)):
        run.driver.give(sim, agent, (), partner)  # empty plans in plan_orca: plain ORCA
    run.advance({}, math.inf)
    result = run.finish()
    pairs = [(0, 2), (1, 3)]
    row = physical_outcome(sim, result, run.driver.track, members, run.driver.started_step, passing, result.goal_times, pairs=pairs)
    alone = [physical_outcome(sim, result, run.driver.track, pair, run.driver.started_step, passing, result.goal_times)["resolved"] for pair in pairs]
    assert row["encounter_size"] == 4 and row["conflict_pairs"] == 2 and row["conflict_pairs_resolved"] == sum(alone)
    assert row["resolved"] == all(alone)
    two = physical_outcome(sim, result, run.driver.track, (0, 1), run.driver.started_step, passing, result.goal_times)
    assert "encounter_size" not in two  # a two-person row is as it was


# --- the toy scenario: its own trigger, event and column, through the unchanged protocol ---------


class ToyScenario(PassingScenario):
    """Defined only here: a conflict whenever the two are within 7 m and closing, whatever their
    lines; an event of its own; an outcome column of its own."""

    CASE_TYPES = ()

    @classmethod
    def load(cls, key=None):
        base = PassingScenario.load()
        data = {**base.data, "template_id": "scenario_toy", "events": {**base.data["events"], "other_is_close": "the other is within 2 m of you"}}
        return cls("scenario_toy_v1", data, "toy")

    def conflict_predicted(self, simulation, i, j):
        a, b = simulation.world.agents[i], simulation.world.agents[j]
        if a.done or b.done:
            return False
        rx, ry = b.pose.x - a.pose.x, b.pose.y - a.pose.y
        vx, vy = b.velocity[0] - a.velocity[0], b.velocity[1] - a.velocity[1]
        return math.hypot(rx, ry) < 7.0 and rx * vx + ry * vy < 0.0

    def happened(self, event, context):
        if event == "other_is_close":
            return math.dist(context.agent.pose.xy, context.partner.pose.xy) < 2.0
        return super().happened(event, context)

    def outcome_columns(self, simulation, track, agents, start_step, general):
        return {**super().outcome_columns(simulation, track, agents, start_step, general), "toy_column": 42}


TOY_REPLY = json.dumps({"intent": "Slow down until they are close, then move left.", "steps": [
    {"speed_mps": 0.8, "until": "other_is_close"}, {"turn": {"to": "left", "degrees": 30}, "until": "other_passes"}], "reason": "r"})


def small_config(name, ids=("head_on_02dfbadb@2",), conditions=("independent", "non_verbal", "talk"), scenarios=None, policy_name="resolution_rehearsal_v1"):
    return E.ResolutionConfig.from_raw({
        "layer": "resolution", "experiment_name": name, "cases": {"ids": list(ids)}, "conditions": list(conditions),
        "scenarios": scenarios or {},
        "design": {"seed": 1, "factors": {"age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["p1_urgent"],
                                          "demographics_visible": [True], "mapping": ["p1_lower"]}},
        "llm": {"client": "mock", "mock_policy": policy_name},
    })


def test_a_toy_scenario_runs_end_to_end_with_no_change_to_the_protocol(tmp_path, monkeypatch):
    monkeypatch.setitem(S.PLUGINS, "toy", ToyScenario)
    config = small_config("toy", conditions=("non_verbal",), scenarios={"head_on_02dfbadb": "toy"})
    client = MockClient(policy=policy({0: TOY_REPLY, 1: TOY_REPLY}))
    result = E.run_resolution(config, client=client, out_root=tmp_path, report=lambda _: None, git=GIT)
    experiment = tmp_path / "toy"
    record = json.loads(next((experiment / "sessions").glob("*.json")).read_text(encoding="utf-8"))
    assert record["scenario"] == "toy" and record["outcome"] == P.SESSION_COMPLETED
    first = record["decision_points"][0]
    assert first["parsed"]["steps"][0]["until"] == "other_is_close"
    assert "other_is_close" in first["prompt"]["messages"][0]["content"]
    replay = json.loads((experiment / "replay" / record["session_id"] / "plan_only" / "outcome.json").read_text(encoding="utf-8"))
    ended = [step["ended_by"] for decision in replay["plans"]["driver"]["decisions"] for step in decision["step_records"]]
    assert "other_is_close" in ended
    row = json.loads((experiment / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert row["toy_column_plan_only"] == 42 and row["toy_column_plan_orca"] == 42
    assert result.status == E.STATUS_COMPLETED


# --- the experiment: storage, one row per session, resume ----------------------------------------


@pytest.fixture(scope="module")
def experiment(tmp_path_factory):
    out = tmp_path_factory.mktemp("resolution")
    config = small_config("small", ids=("head_on_02dfbadb@2", "passage_02fac1e4@1"))
    result = E.run_resolution(config, out_root=out, report=lambda _: None, git=GIT)
    return config, out, result


def test_the_outcome_writer_gives_one_row_per_session(experiment):
    config, out, result = experiment
    folder = out / "small"
    sessions = sorted((folder / "sessions").glob("*.json"))
    rows = (folder / "outcomes.csv").read_text(encoding="utf-8").splitlines()
    assert len(rows) - 1 == len(sessions) == result.preview["sessions"] == 6
    jsonl = [json.loads(line) for line in (folder / "outcomes.jsonl").read_text(encoding="utf-8").splitlines()]
    assert sorted(row["session_id"] for row in jsonl) == sorted(p.stem for p in sessions)
    for row in jsonl:
        for column in ("resolved_plan_only", "resolved_plan_orca", "not_resolved_by_llm", "resolved_by_llm", "p1_age", "p2_gender",
                       "p1_first_side", "p2_final_stopped", "p1_debrief_kind", "case_geometry", "exact_repeat_set", "llm_calls"):
            assert column in row
        if row["outcome"] == P.SESSION_COMPLETED:
            assert row["resolved_plan_only"] is not None and row["resolved_plain_orca"] is not None


def test_every_decision_point_in_decisions_jsonl_has_its_raw_replies_in_the_session_record(experiment):
    _, out, _ = experiment
    folder = out / "small"
    lines = [json.loads(line) for line in (folder / "decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    assert lines
    for line in lines:
        record = json.loads((folder / "sessions" / f"{line['session_id']}.json").read_text(encoding="utf-8"))
        point = next(p for p in record["decision_points"] if p["index"] == line["index"])
        assert point["agent_id"] == line["agent_id"] and point["attempts"]
        assert all(attempt["raw_output"] for attempt in point["attempts"])
        if line["intent"] is not None:
            assert line["intent"] in point["attempts"][-1]["raw_output"]
    debriefs = [json.loads(line) for line in (folder / "debriefs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert debriefs and all(d["check_status"] == "unchecked" for d in debriefs)


def test_the_files_of_the_layout_are_written(experiment):
    _, out, _ = experiment
    folder = out / "small"
    for name in ("config.json", "invocations.jsonl", "cases.json", "design.jsonl", "preview.json", "decisions.jsonl", "debriefs.jsonl",
                 "outcomes.jsonl", "outcomes.csv", "cost.json", "summary.json", "report.md"):
        assert (folder / name).is_file(), name
    record = json.loads(next((folder / "sessions").glob("*.json")).read_text(encoding="utf-8"))
    assert (folder / "sessions" / f"{record['session_id']}.md").is_file()
    if record["outcome"] == P.SESSION_COMPLETED:
        for mode in X.MODES:
            assert (folder / record["replays"][mode] / "outcome.json").is_file()
    report = (folder / "report.md").read_text(encoding="utf-8")
    assert "plan_only" in report and "Mean decision points" in report


def test_resuming_leaves_every_session_record_byte_for_byte_unchanged(experiment):
    config, out, _ = experiment
    folder = out / "small"
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (folder / "sessions").glob("*")}
    result = E.run_resolution(config, out_root=out, report=lambda _: None, git=GIT)
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (folder / "sessions").glob("*")}
    assert before == after and not result.executed and len(result.skipped) == 6


def test_a_limited_run_resumes_where_it_stopped(tmp_path):
    config = small_config("limited")
    first = E.run_resolution(config, out_root=tmp_path, limit=1, report=lambda _: None, git=GIT)
    assert first.status == E.STATUS_PARTIAL and len(first.executed) == 1
    kept = (tmp_path / "limited" / "sessions" / f"{first.executed[0]}.json").read_bytes()
    second = E.run_resolution(config, out_root=tmp_path, report=lambda _: None, git=GIT)
    assert second.status == E.STATUS_COMPLETED and first.executed[0] in second.skipped and len(second.executed) == 2
    assert (tmp_path / "limited" / "sessions" / f"{first.executed[0]}.json").read_bytes() == kept


def test_another_config_in_the_same_folder_is_refused(experiment):
    config, out, _ = experiment
    changed = replace(config, protocol=P.ProtocolSettings(min_gap_s=2.0))
    with pytest.raises(ConfigError):
        E.run_resolution(changed, out_root=out, report=lambda _: None, git=GIT)


def test_plan_prints_the_worst_case_cost_for_all_three_conditions(capsys):
    assert cli_main(["configs/resolution/resolve_mock_rehearsal.yaml", "--plan"]) == 0
    printed = capsys.readouterr().out
    for condition in ("independent", "non_verbal", "talk"):
        assert f"  {condition}: " in printed
    assert "worst-case cost USD" in printed


def test_the_preview_bounds_the_mock_sessions_tokens(experiment):
    _, out, result = experiment
    summary = json.loads((out / "small" / "summary.json").read_text(encoding="utf-8"))
    assert summary["largest_share_of_the_preview_used"] is not None and summary["largest_share_of_the_preview_used"] <= 1.0
    independent = [row for row in result.preview["per_session"] if row["condition"] == "independent"]
    talk = [row for row in result.preview["per_session"] if row["condition"] == "talk"]
    assert all(row["calls"] == 4 for row in independent) and all(row["calls"] == 8 for row in talk)


def test_a_paid_client_sends_nothing_without_confirm(tmp_path):
    config = small_config("paid", conditions=("independent",))

    class Refusing(MockClient):
        name = "deepseek"

        def complete(self, request):  # pragma: no cover - must not be reached
            raise AssertionError("a paid call was made")

    result = E.run_resolution(config, client=Refusing(), out_root=tmp_path, report=lambda _: None, git=GIT)
    assert result.status == E.STATUS_AWAITING and not (tmp_path / "paid" / "sessions").exists()


def test_a_bad_resolution_config_is_refused():
    with pytest.raises(ConfigError):
        small_config("x", conditions=("negotiated",))
    with pytest.raises(ConfigError):
        E.ResolutionConfig.from_raw({"layer": "resolution", "experiment_name": "x", "cases": {"ids": ["a"]}, "conditions": ["talk"],
                                     "design": {"seed": 1, "factors": {"age_pair": ["same"]}}, "llm": {}})
    with pytest.raises(ConfigError):
        E.plan(small_config("x", scenarios={"not_selected": "passing"}))


def test_a_case_type_no_plug_in_takes_must_be_named():
    with pytest.raises(ConfigError):
        S.plugin_for(STORE.get("crossing_6c29d99f", 2))
    assert S.plugin_for(HEAD_ON) == "passing" and S.plugin_for(CROWD) == "passing_crowd"
    assert S.plugin_for(STORE.get("crossing_6c29d99f", 2), "passing") == "passing"
