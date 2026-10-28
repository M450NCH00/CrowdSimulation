"""Round 1 with three or four people (issue #110, RF-32): the group_head_on scenario type, the group
cases, the passing_group plug-in (who starts, who joins, which pairs count, WHO YOU ARE WITH), the
scenario hooks' defaults, a persona for everyone (``design.others``) and RF-32's config."""

from __future__ import annotations

import copy

import pytest

from negsim.configutil import ConfigError, load_yaml
from negsim.experiment.avoidance import simulation_for
from negsim.llm.mock import MockClient
from negsim.resolution import experiment as E
from negsim.resolution import mock as M
from negsim.resolution import protocol as P
from negsim.resolution import scenarios as S
from negsim.resolution.design import ResolutionDesign, others_for
from negsim.resolution.scenarios.passing_group import companion_side
from negsim.rulegen.cases import CaseStore
from negsim.rulegen.protocol import LLMSettings
from negsim.rulegen.replay import source_plan
from negsim.scenarios.registry import build_crowd_scenario, load_scenario_config

STORE = CaseStore()
CASES = dict(STORE.case_set("rf32_group_v1"))
TWO_V_ONE, TWO_V_ONE_APART = STORE.get("group_75a57582", 1), STORE.get("group_6bc7f193", 1)
TWO_V_TWO, TWO_V_TWO_APART = STORE.get("group_37a3c705", 1), STORE.get("group_206147b4", 1)
LLM = LLMSettings("deepseek-flash", 1.0, 300)
CONFIG = "configs/resolution/round1_group_head_on.yaml"


def scenario_with(eastbound, westbound):
    raw = copy.deepcopy(load_scenario_config("configs/scenarios/group_head_on.yaml"))
    raw["geometry"].update({"eastbound": eastbound, "westbound": westbound})
    return build_crowd_scenario(raw)


def session_on(case, answers=None):
    def answer(request):
        meta = request.metadata
        return M.DEBRIEF_PATHS["with_source"] if meta.get("kind") == "debrief" else (answers or {}).get(meta["agent_id"], M.CARRY_ON)
    run = P.EncounterSession(
        simulation_for(source_plan(case)), case["agents"], S.load_scenario("passing_group"), "independent",
        MockClient(policy=answer), LLM, P.ProtocolSettings(max_prompted=4),
    )
    run.run_session()
    return run.as_dict()


def last_message(point):
    return point["prompt"]["messages"][-1]["content"]


# --- the scenario type ----------------------------------------------------------------------------


def test_each_group_starts_side_by_side_eastbound_first():
    spec = scenario_with([0.315, -0.315], [0.315, -0.315])
    assert [(agent.group, agent.start.xy) for agent in spec.agents] == [
        ("eastbound", (-8.0, 0.315)), ("eastbound", (-8.0, -0.315)), ("westbound", (8.0, 0.315)), ("westbound", (8.0, -0.315)),
    ]
    assert [tuple(agent.goal) for agent in spec.agents] == [(8.0, 0.315), (8.0, -0.315), (-8.0, 0.315), (-8.0, -0.315)]


def test_a_layout_that_does_not_fit_is_refused():
    with pytest.raises(ConfigError, match="overlap"):
        scenario_with([0.2, -0.2], [0.0])
    with pytest.raises(ConfigError, match="overlapping a wall"):
        scenario_with([0.7], [0.0])
    with pytest.raises(ConfigError, match="non-empty list"):
        scenario_with([], [0.0])


def test_the_group_cases_are_one_pair_of_each_layout():
    assert set(CASES) == {"group_75a57582", "group_6bc7f193", "group_37a3c705", "group_206147b4"}
    layouts = {STORE.get(case_id, version)["scenario"]["variant"]["layout"] for case_id, version in CASES.items()}
    assert layouts == {"2v1_aligned", "2v1_apart_20cm", "2v2_aligned", "2v2_apart_20cm"}
    for case in (TWO_V_ONE, TWO_V_ONE_APART, TWO_V_TWO, TWO_V_TWO_APART):
        assert case["severity_tier"] == "T3" and case["formation"]["encounter_class"] == "head_on"
        assert S.plugin_for(case) == "passing_group"
    assert TWO_V_ONE["scenario"]["n_agents"] == 3 and TWO_V_TWO["scenario"]["n_agents"] == 4


# --- the plug-in ----------------------------------------------------------------------------------


@pytest.mark.parametrize("case, sides", [
    (TWO_V_ONE, {0: "right", 1: "left", 2: None}),             # eastbound: left is +y
    (TWO_V_ONE_APART, {0: "right", 1: "left", 2: None}),
    (TWO_V_TWO, {0: "right", 1: "left", 2: "left", 3: "right"}),  # westbound: left is -y
    (TWO_V_TWO_APART, {0: "right", 1: "left", 2: "left", 3: "right"}),
])
def test_where_each_persons_friend_walks(case, sides):
    geometry = case["scenario"]["geometry"]
    assert {agent: companion_side(geometry, agent) for agent in sides} == sides


def test_who_starts_who_joins_and_which_pairs_count():
    plugin = S.load_scenario("passing_group")
    sim = simulation_for(source_plan(TWO_V_TWO))
    starts = plugin.trigger_pairs(sim, TWO_V_TWO["agents"])
    assert starts[:2] == [(1, 2), (2, 1)]  # the case's pair first
    assert set(starts) == {(i, j) for i in (0, 1) for j in (2, 3)} | {(j, i) for i in (0, 1) for j in (2, 3)}
    members = plugin.encounter_members(sim, 0, 2)
    assert members[:2] == [0, 2] and sorted(members) == [0, 1, 2, 3]
    assert plugin.conflict_pairs(sim, members, 0, 2) == [(0, 2), (0, 3), (2, 1), (1, 3)]


def test_the_hooks_defaults_are_what_the_protocol_did():
    head_on = STORE.get("head_on_02dfbadb", 2)
    passing = S.load_scenario("passing")
    sim = simulation_for(source_plan(head_on))
    assert passing.trigger_pairs(sim, head_on["agents"]) == [(0, 1), (1, 0)]
    crowd = STORE.get("flow_ba3c7962", 2)
    plugin = S.load_scenario("passing_crowd")
    sim = simulation_for(source_plan(crowd))
    for _ in range(60):
        sim.step()
    a, b = crowd["agents"]
    members = plugin.encounter_members(sim, a, b)[:4]
    expected = [(a, b)] + [
        (p, q) for k, p in enumerate(members) for q in members[k + 1:] if {p, q} != {a, b} and plugin.conflict_predicted(sim, p, q)
    ]
    assert plugin.conflict_pairs(sim, members, a, b) == expected


def test_a_group_session_prompts_everyone_and_counts_every_pair_walking_opposite_ways():
    record = session_on(TWO_V_TWO)
    encounter = record["encounter"]
    assert sorted(encounter["prompted"]) == [0, 1, 2, 3]
    assert sorted(map(sorted, encounter["pairs"])) == [[0, 2], [0, 3], [1, 2], [1, 3]]
    first = encounter["trigger"]
    assert {first["agent_id"], first["other_id"]} in ({0, 2}, {0, 3}, {1, 2}, {1, 3})
    assert encounter["pairs"][0] == [first["agent_id"], first["other_id"]]
    for point in record["decision_points"]:  # everyone walks with a friend in 2 v 2
        assert "WHO YOU ARE WITH" in last_message(point)


def test_only_someone_walking_with_a_friend_is_told_so():
    record = session_on(TWO_V_ONE_APART)
    told = {point["agent_id"]: "WHO YOU ARE WITH" in last_message(point) for point in record["decision_points"]}
    assert told == {0: True, 1: True, 2: False}
    lone = next(point for point in record["decision_points"] if point["agent_id"] == 2)
    assert [person["label"] for person in lone["view"]["seen"]] == [1, 2]  # both oncoming people in view
    friend = next(point for point in record["decision_points"] if point["agent_id"] == 1)
    assert "They are on your left." in last_message(friend)


# --- a persona for everyone -----------------------------------------------------------------------


def design_with(**changes):
    raw = load_yaml(CONFIG)["design"]
    raw = {**copy.deepcopy(raw), **changes}
    return ResolutionDesign.from_config(raw)


def test_everyone_beyond_the_design_two_gets_a_persona_at_the_base_levels():
    design = design_with()
    cell = {"age_pair": "p1_older", "gender_pair": "p1_female", "urgency": "neither", "mobility_aid": "p1", "assertiveness": "p1",
            "demographics_visible": True, "mapping": "p1_higher"}
    people = {2: {"gender": "female"}, 1: {"gender": "male"}}
    out = others_for(cell, people, {0: 1, 3: 2}, design)
    assert out[0] == {"age": 25, "gender": "male", "task": design.tasks["routine"], "urgency": "routine", "mobility_aid": "none",
                      "assertiveness": "gives_way"}
    assert out[3]["gender"] == "female"
    with pytest.raises(ConfigError, match="as_companion"):
        others_for(cell, people, {4: None}, design)


def test_others_is_checked_and_refused_with_factors_set_for_two_only():
    with pytest.raises(ConfigError, match="others.gender"):
        design_with(others={"gender": "somebody"})
    with pytest.raises(ConfigError, match="at most 120"):
        design_with(others={"gender": "male", "age": 130})
    raw = copy.deepcopy(load_yaml(CONFIG)["design"])
    raw["factors"]["ethnicity_pair"] = ["same"]
    with pytest.raises(ConfigError, match="drawn or set for the design's two people only"):
        ResolutionDesign.from_config(raw)
    assert "others" not in design_with(others=None).as_dict()


def test_rf32s_config_plans_72_sessions_with_everyone_given_a_persona():
    plan = E.plan(E.ResolutionConfig.load(CONFIG))
    assert len(plan.sessions) == 72 and {s.condition for s in plan.sessions} == {"independent"}
    assert sum(s.exact_repeat_set for s in plan.sessions) == 12  # 4 cells, 3 times each
    for session in plan.sessions:
        case = plan.cases[session.case_id]
        assert sorted(session.personas) == list(range(case["scenario"]["n_agents"]))
        assert session.persons[0] == 2  # person 1: the westbound one of the case's pair
        assert session.scenario == "passing_group"
        for agent, persona in session.personas.items():
            if agent not in session.agents:
                assert persona["mobility_aid"] == "none" and persona["assertiveness"] == "gives_way" and persona["age"] == 25
    lone = [s for s in plan.sessions if plan.cases[s.case_id]["scenario"]["n_agents"] == 3]
    assert all(companion_side(plan.cases[s.case_id]["scenario"]["geometry"], s.persons[0]) is None for s in lone)
