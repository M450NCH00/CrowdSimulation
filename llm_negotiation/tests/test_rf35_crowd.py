"""Encounters sampled from crowds (issue #117, RF-35): the case set, RF-35's config, and bystanders drawn
from a population profile (``design.others.population``)."""

from __future__ import annotations

import copy
from collections import Counter

import pytest

from negsim.configutil import ConfigError, load_yaml
from negsim.populations import Profile, quota_people
from negsim.resolution import experiment as E
from negsim.resolution.design import OthersSpec, ResolutionDesign
from negsim.rulegen.cases import CaseStore

CONFIG = "configs/resolution/rf35_crowd_encounters.yaml"
PROFILE = "configs/populations/singapore_street_v1.yaml"
STORE = CaseStore()


@pytest.fixture(scope="module")
def sessions():
    return E.plan(E.ResolutionConfig.load(CONFIG)).sessions


def test_the_case_set_is_two_cases_per_density_and_tier():
    cases = [STORE.get(case_id, version) for case_id, version in STORE.case_set("rf35_crowd_v1")]
    assert len(cases) == 8
    found = Counter((case["scenario"]["variant"]["density"], case["scenario"]["n_agents"]) for case in cases)
    assert found == {("per_way_25", 50): 4, ("per_way_50", 100): 4}
    assert {case["scenario"]["type"] for case in cases} == {"bidirectional_flow"}


def test_the_config_plans_72_independent_sessions_with_passing_crowd(sessions):
    config = E.ResolutionConfig.load(CONFIG)
    assert config.conditions == ("independent",) or list(config.conditions) == ["independent"]
    assert len(sessions) == 72 and sum(1 for s in sessions if s.repeat > 1) == 8
    assert {s.scenario for s in sessions} == {"passing_crowd"}
    assert config.protocol.max_prompted == 4 and config.protocol.orca_within_groups and config.protocol.distance_to_partner
    assert config.design.others == OthersSpec(None, None, PROFILE)
    raw = load_yaml(CONFIG)
    assert raw["llm"]["client"] == "mock" and "load" not in raw["design"]["factors"]


def test_everyone_else_is_drawn_from_the_profile_at_exact_shares(sessions):
    session = next(s for s in sessions if s.case_id == "flow_32e86a8e")  # 100 people
    others = {agent: p for agent, p in session.personas.items() if agent not in session.agents}
    assert len(others) == 98
    drawn = quota_people(Profile.load(PROFILE), 98, "x")
    # The same profile gives the same counts whatever the seed (exact shares): canes and phones.
    assert sum(p.get("mobility_aid") == "cane" for p in others.values()) == sum(p["mobility_aid"] == "cane" for p in drawn.values())
    assert sum(p.get("distraction") == "phone" for p in others.values()) == sum(p["distraction"] == "phone" for p in drawn.values())
    assert all(set(p) == {"age", "gender", "task", "urgency", "mobility_aid", "assertiveness", "distraction"} for p in others.values())
    assert all(10 <= p["age"] <= 94 for p in others.values())


def test_an_exact_repeat_has_the_same_bystanders_and_another_cell_other_ones(sessions):
    repeats = [s for s in sessions if s.exact_repeat_set]
    first = repeats[0]
    same = [s for s in repeats if s.case_id == first.case_id and s.cell == first.cell]
    assert len(same) == 3 and all(s.personas == first.personas for s in same)
    other = next(s for s in sessions if s.case_id == first.case_id and s.cell != first.cell)
    bystanders = lambda s: {a: p for a, p in s.personas.items() if a not in s.agents}  # noqa: E731
    assert bystanders(other) != bystanders(first)


def test_a_bystanders_cane_or_phone_is_what_others_are_told(sessions):
    config = E.ResolutionConfig.load(CONFIG)
    session = next(s for s in sessions if s.case_id == "flow_32e86a8e")
    seen = E.session_factors(config, session).seen_lines()
    marked = [a for a, p in session.personas.items() if a not in session.agents and (p["mobility_aid"] == "cane" or p["distraction"] == "phone")]
    assert marked and all(int(a) in seen for a in marked)
    plain = next(a for a, p in session.personas.items() if a not in session.agents and p["mobility_aid"] != "cane" and p["distraction"] != "phone")
    assert int(plain) not in seen or all("cane" not in line and "phone" not in line for line in seen[int(plain)])


def design_with(others, **factors):
    raw = copy.deepcopy(load_yaml(CONFIG)["design"])
    raw["others"] = others
    raw["factors"].update(factors)
    return ResolutionDesign.from_config(raw)


def test_the_population_form_is_checked_and_the_old_form_is_as_before():
    assert design_with({"population": PROFILE}).as_dict()["others"] == {"population": PROFILE}
    assert design_with({"age": 25, "gender": "female"}).as_dict()["others"] == {"age": 25, "gender": "female"}  # issue #110's form
    with pytest.raises(ConfigError, match="load"):
        design_with({"population": PROFILE}, load=["neither"])
    with pytest.raises(ConfigError):
        design_with({"population": PROFILE, "age": 25})
    with pytest.raises(Exception):
        design_with({"population": "configs/populations/no_such_profile.yaml"})


# --- scoring a crowd encounter against plain ORCA (the user's decision after the pilot) ------------

from types import SimpleNamespace  # noqa: E402

from negsim.metrics.avoidance import ProximityEpisode  # noqa: E402
from negsim.resolution import groups as G  # noqa: E402


def measured(episodes, walls=(), goal_times=None, deadlock=False, start=100):
    result = SimpleNamespace(collision_episodes=list(episodes), wall_collision_episodes=list(walls), deadlock=deadlock,
                             goal_times=goal_times or {1: 30.0, 2: 31.0, 3: 32.0})
    return G.Measured(SimpleNamespace(world=SimpleNamespace(dt=0.1)), result, [], start)


def test_contacts_count_the_encounters_people_from_its_start_only():
    found = G.contacts(measured([
        ProximityEpisode((1, 9), 10.5, 10.6, -0.012),   # a member and a bystander, after the start (10 s)
        ProximityEpisode((2, 3), 11.0, 11.1, -0.030),   # two members
        ProximityEpisode((7, 8), 12.0, 12.1, -0.200),   # two bystanders: not counted
        ProximityEpisode((1, 4), 8.0, 9.5, -0.100),     # ended before the start: not counted
    ], walls=[{"agent_id": 3, "start_time_s": 12.0, "end_time_s": 12.2, "max_overlap_m": 0.01}]), [1, 2, 3])
    assert found == {"collisions": 3, "deepest_m": 0.03, "stuck": False}
    assert G.contacts(measured([], goal_times={1: 30.0, 2: None, 3: 32.0}), [1, 2, 3])["stuck"] is True
    assert G.contacts(measured([], deadlock=True), [1, 2, 3])["stuck"] is True


@pytest.mark.parametrize("plans, plain, resolved, verdict", [
    ({"collisions": 2, "deepest_m": 0.01, "stuck": False}, {"collisions": 2, "deepest_m": 0.01, "stuck": False}, True, "same"),
    ({"collisions": 1, "deepest_m": 0.01, "stuck": False}, {"collisions": 2, "deepest_m": 0.02, "stuck": False}, True, "better"),
    ({"collisions": 1, "deepest_m": 0.05, "stuck": False}, {"collisions": 2, "deepest_m": 0.02, "stuck": False}, False, "better"),  # fewer but deeper
    ({"collisions": 3, "deepest_m": 0.01, "stuck": False}, {"collisions": 2, "deepest_m": 0.02, "stuck": False}, False, "worse"),
    ({"collisions": 5, "deepest_m": 0.09, "stuck": False}, {"collisions": 0, "deepest_m": 0.0, "stuck": True}, True, "better"),
    ({"collisions": 0, "deepest_m": 0.0, "stuck": True}, {"collisions": 4, "deepest_m": 0.04, "stuck": False}, False, "worse"),
])
def test_against_orca(plans, plain, resolved, verdict):
    scored = G.against_orca(plans, plain)
    assert scored["resolved"] is resolved and scored["verdict"] == verdict
