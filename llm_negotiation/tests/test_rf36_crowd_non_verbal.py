"""Crowd encounters, non-verbal (issue #119, RF-36): the config differs from RF-35's only in its condition
and plans the same sessions' people; nobody is prompted once the driver has handed the encounter to ORCA
(the mock rehearsal's crash); and the analysis's paired comparison of two crowd experiments."""

from __future__ import annotations

import json

import pytest

from negsim.configutil import load_yaml
from negsim.resolution import experiment as E
from negsim.resolution import groups as G

RF35 = "configs/resolution/rf35_crowd_encounters.yaml"
RF36 = "configs/resolution/rf36_crowd_encounters_non_verbal.yaml"


def test_the_config_is_rf35s_but_for_the_condition():
    rf35, rf36 = load_yaml(RF35), load_yaml(RF36)
    assert rf36["conditions"] == ["non_verbal"] and rf35["conditions"] == ["independent"]
    assert rf36["experiment_name"] == "rf36_crowd_encounters_non_verbal"
    assert rf36["protocol"]["max_decision_points"] == 3
    assert rf36["llm"]["client"] == "mock"  # the paid run names deepseek on the command line
    different = {"conditions", "experiment_name", "description", "budget"}
    assert {key: value for key, value in rf36.items() if key not in different} == {key: value for key, value in rf35.items() if key not in different}
    assert {k: v for k, v in rf36["budget"].items() if k != "cap_usd"} == {k: v for k, v in rf35["budget"].items() if k != "cap_usd"}


def test_the_sessions_pair_with_rf35s_and_have_the_same_people():
    rf35 = {G.design_key(s.session_id): s for s in E.plan(E.ResolutionConfig.load(RF35)).sessions}
    rf36 = {G.design_key(s.session_id): s for s in E.plan(E.ResolutionConfig.load(RF36)).sessions}
    assert len(rf36) == 72 and set(rf36) == set(rf35)
    assert all(rf36[key].personas == rf35[key].personas and rf36[key].case_id == rf35[key].case_id for key in rf36)
    assert {s.condition for s in rf36.values()} == {"non_verbal"}


@pytest.fixture(scope="module")
def first_session(tmp_path_factory):
    """The session the first mock rehearsal crashed on (the plan's first): one of the encounter's
    people was due a later decision point after the driver had released the encounter, since two
    members walking the same way (a conflict pair of passing_crowd, left to ORCA) never "pass"."""
    out = tmp_path_factory.mktemp("rf36")
    config = E.ResolutionConfig.load(RF36)
    E.run_resolution(config, client_name="mock", out_root=out, limit=1)
    (path,) = (out / config.experiment_name / "sessions").glob("*.json")
    return json.loads(path.read_text(encoding="utf-8"))


def test_nobody_is_prompted_after_the_driver_releases_the_encounter(first_session):
    record = first_session
    assert record["outcome"] == "completed"
    encounter = record["encounter"]
    assert encounter["not_prompted_after_release"]  # someone was due, and was not asked
    assert set(encounter["not_prompted_after_release"]) <= set(encounter["agents"])
    assert len(encounter["agents"]) == 4  # the cap of 4 was reached, as in RF-35


def test_a_record_with_nobody_due_after_a_release_does_not_name_it():
    # Every earlier record: RF-35's sessions, independent, never had anyone due after a release.
    record = json.loads(next(iter(sorted((E.resolve_path("runs/rf35_crowd_encounters") / "sessions").glob("*.json")))).read_text(encoding="utf-8"))
    assert "not_prompted_after_release" not in record["encounter"]


def contacts(collisions, deepest, stuck=False):
    return {"collisions": collisions, "deepest_m": deepest, "stuck": stuck}


def scored(session_id, layout, plans, plain):
    return {"session_id": session_id, "layout": layout, "against_orca": G.against_orca(plans, plain)}


def test_the_paired_crowd_comparison():
    plain = contacts(2, 0.005)
    rf35 = {
        "flow_a_1_r1": G.against_orca(contacts(3, 0.010), plain),   # worse than ORCA
        "flow_a_2_r1": G.against_orca(contacts(2, 0.005), plain),   # resolved
        "flow_b_3_r1": G.against_orca(contacts(4, 0.030), plain),   # worse than ORCA
        "flow_b_4_r1": G.against_orca(contacts(2, 0.004), contacts(1, 0.002)),
    }
    design = [
        scored("N_flow_a_1_r1", "d25", contacts(2, 0.004), plain),            # resolved here only; better than RF-35's
        scored("N_flow_a_2_r1", "d25", contacts(2, 0.005), plain),            # both; the same as RF-35's
        scored("N_flow_b_3_r1", "d50", contacts(4, 0.012), plain),            # neither; better (shallower)
        scored("N_flow_b_4_r1", "d50", contacts(2, 0.004), contacts(9, 9.0)), # plain ORCA differs: counted
        scored("N_flow_c_5_r1", "d50", contacts(0, 0.0), plain),              # not in RF-35: left out
    ]
    found = G.paired_crowd(design, rf35)
    assert found["d25"]["against_orca"] == {"both": 1, "this_only": 1, "other_only": 0, "neither": 0, "n": 2, "sign_test_p": 1.0}
    assert found["d25"]["direct"] == {"better": 1, "same": 1, "worse": 0, "sign_test_p": 1.0}
    assert found["d25"]["direct_collisions_only"] == {"better": 1, "same": 1, "worse": 0, "sign_test_p": 1.0}
    assert found["d50"]["direct"]["better"] == 1 and found["d50"]["direct_collisions_only"]["same"] == 2
    assert found["all"]["against_orca"]["n"] == 4 and found["all"]["plain_orca_differs"] == 1
    assert found["d25"]["plain_orca_differs"] == 0


def test_resolved_within_a_tolerance():
    within = lambda plans, plain, t: G.resolved_within(G.against_orca(plans, plain), t)  # noqa: E731
    assert within(contacts(2, 0.009), contacts(2, 0.005), 0.005) is True
    assert within(contacts(2, 0.011), contacts(2, 0.005), 0.005) is False
    assert within(contacts(3, 0.005), contacts(2, 0.005), 0.01) is False   # a collision more is never within
    assert within(contacts(0, 0.0, stuck=True), contacts(0, 0.0), 0.01) is False


def test_rf35s_analysis_gives_its_reports_tolerance_counts():
    # crowd_report.md: 14 of 64 of record, 26 at 5 mm, 34 at 1 cm (counted by hand in #117).
    design = G._analysed_design_sessions(E.resolve_path("runs/rf35_crowd_encounters"))
    assert len(design) == 64 and sum(s["against_orca"]["resolved"] for s in design) == 14
    assert [sum(G.resolved_within(s["against_orca"], t) for s in design) for t in G.TOLERANCES_M] == [26, 34]
