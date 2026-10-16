"""Issue #30, Part 9: single-rule replay on a case's own run, and crowd screening."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from negsim.avoidance.perception import default_visibility
from negsim.rules.canonical import canonical_hash
from negsim.rulegen import replay as rp
from negsim.rulegen.cases import CaseStore
from negsim.rulegen.writer import StagingDatabase, Support, build_rule, with_screening

GIT = {"commit": "test", "dirty": False}
SMALL_CROWD = {"geometry": {"agents_per_direction": 4, "length": 20.0}, "max_time": 60.0}
CASE = CaseStore().get("head_on_de176842")
PEOPLE = {0: {"age": 70, "gender": "female"}, 1: {"age": 25, "gender": "male"}}
KEEP_ROOM = {"encounter": "any", "when": {"all": []}, "roles": "symmetric", "directive": {"both": {"clearance_margin": 0.15}}, "priority": 100}
# Both stop on meeting head-on, until out of sight of each other: the flow deadlocks.
STOP_UNTIL_APART = {"encounter": "head_on", "when": {"all": []}, "roles": "symmetric", "directive": {"both": {"speed_scale": 0.0}}, "priority": 100, "expiry": "out_of_range"}
# Both stop on meeting, until the encounter has passed: ORCA still steps a stopped agent aside,
# the encounter passes, the scale ends, and the flow gets through, slower.
STOP_UNTIL_PASSED = {**STOP_UNTIL_APART, "encounter": "any", "expiry": "passed"}


def staged(tmp_path, proposal):
    staging = StagingDatabase(tmp_path / "rule_db_staging" / "stated")
    staging.create()
    digest = canonical_hash(proposal)
    support = Support("B_test_r1", {"order": "lower_first"}, "deepseek-flash", None, {"key": "rulegen_state_v1"}, "2026-10-16T00:00:00+00:00", proposal=proposal)
    rule = build_rule("stated", CASE["case_id"], digest, [support], "test")
    staging.stage(rule, "test")
    return staging, staging.latest(rule["rule_id"])


def test_the_source_run_of_a_case_is_rebuilt_and_checked():
    plan = rp.source_plan(CASE)
    assert (plan.run_id, plan.seed, plan.baseline.name) == (CASE["source"]["run_id"], CASE["source"]["seed"], "orca_perturbed_v1")
    with pytest.raises(rp.ReplayError, match="seed"):
        rp.source_plan({**CASE, "source": {**CASE["source"], "seed": CASE["source"]["seed"] + 1}})
    with pytest.raises(rp.ReplayError, match="not the one the case was taken from"):
        rp.source_plan({**CASE, "scenario": {**CASE["scenario"], "resolved_sha256": "0" * 64}})
    with pytest.raises(rp.ReplayError, match="expected one experiment config"):
        rp.find_source_config("no_such_experiment")


def test_a_rule_is_replayed_alone_on_its_cases_run_beside_a_baseline_that_reproduces_the_case(tmp_path):
    staging, rule = staged(tmp_path, KEEP_ROOM)
    entry = rp.replay(rule, staging.root, CASE, PEOPLE, default_visibility(), tmp_path / "replay" / rule.rule_id, "test", GIT, f"replay/{rule.rule_id}")
    results = entry["results"]
    assert entry["kind"] == "replay" and entry["verdict"] == "recorded" and entry["reasons"] == [] and entry["seeds"] == [CASE["source"]["seed"]]
    assert results["baseline_reproduces_case"] and results["rule_matched_the_case_pair"]
    assert results["pair"]["baseline"]["severity_tier"] == CASE["baseline_outcome"]["severity_tier"] == "T3"
    assert results["pair"]["rule"]["min_separation_m"] > 0.1 > results["pair"]["baseline"]["min_separation_m"]  # 15 cm more room: no near miss
    assert results["run"]["baseline"]["rule_fired"] == 0 and results["run"]["rule"]["rule_fired"] == 1
    config = json.loads((tmp_path / "replay" / rule.rule_id / "rule" / "config.json").read_text(encoding="utf-8"))
    assert [enabled["rule_id"] for enabled in config["directives"]["rules"]] == [rule.rule_id]
    assert config["seed"] == CASE["source"]["seed"] and config["population"][0]["attributes"] == PEOPLE[0]
    assert results["folders"] == {"baseline": f"replay/{rule.rule_id}/baseline", "rule": f"replay/{rule.rule_id}/rule"}
    newer = with_screening(rule.written, [entry])
    staging.write(newer, "screened")
    assert staging.latest(rule.rule_id).screening[0]["kind"] == "replay"  # the schema takes the entry


def test_a_replayed_baseline_that_does_not_reproduce_the_case_is_reported():
    pair = {"start_step": CASE["formation"]["step"], **{key: CASE["baseline_outcome"][key] for key in ("severity_tier", "pair_exposure_time_s", "min_separation_m")}}
    assert rp.reproduces_case(pair, CASE)
    assert not rp.reproduces_case({**pair, "min_separation_m": 0.5}, CASE) and not rp.reproduces_case(None, CASE)


def test_a_rule_that_gridlocks_the_crowd_fails_screening_and_one_that_does_not_passes(tmp_path):
    settings = rp.ScreeningSettings(repeats=1, scenario_overrides=SMALL_CROWD)
    population = rp.mixed_population(rp.crowd_size(settings), (25, 70), ("female", "male"))
    screen = rp.CrowdScreen(settings, tmp_path / "screening", "test", GIT, population)
    staging, stops = staged(tmp_path, STOP_UNTIL_APART)
    failed = screen.screen(stops, staging.root, default_visibility())
    (seed,) = failed["results"]["per_seed"]
    assert failed["verdict"] == "failed" and seed["rule"]["status"] == "deadlock" and not seed["baseline"]["gridlocked"]
    assert failed["reasons"] and "gridlocked" in failed["reasons"][0]
    for proposal in (KEEP_ROOM, STOP_UNTIL_PASSED):
        _, rule = staged(tmp_path, proposal)
        passed = screen.screen(rule, staging.root, default_visibility())
        ruled = passed["results"]["per_seed"][0]["rule"]
        assert passed["verdict"] == "passed" and passed["reasons"] == [] and ruled["rule_fired"] > 0 and ruled["arrived"] == ruled["n_agents"]
        assert passed["results"]["per_seed"][0]["baseline"] == seed["baseline"]  # the baseline seed is run once
    assert ruled["sim_time_s"] > seed["baseline"]["sim_time_s"]  # stopping until passed: through, but slower
    assert len(list((tmp_path / "screening" / "baseline").iterdir())) == 1
    assert staging.latest(stops.rule_id).version == 1  # screening never deletes or edits a rule


def test_the_case_pair_is_the_interaction_that_formed_nearest_the_case(tmp_path):
    lines = [
        {"pair_id": 4, "agents": [0, 1], "start_step": 10, "severity_tier": "T0"},
        {"pair_id": 9, "agents": [0, 1], "start_step": 50, "severity_tier": "T3"},
        {"pair_id": 7, "agents": [0, 2], "start_step": 49, "severity_tier": "T4"},
    ]
    for line in lines:
        line.update(outcome="avoided", pair_exposure_time_s=0.0, min_separation_m=1.0, tier_detail={"yield_events": 0, "near_misses": 0}, rules=None)
    (tmp_path / "pair_interactions.jsonl").write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
    found = rp._pair_numbers(tmp_path, [0, 1], 46)
    assert (found["pair_id"], found["interactions_of_the_two"], found["severity_tier"]) == (9, 2, "T3")
    assert rp._pair_numbers(tmp_path, [1, 2], 46) is None


def test_a_mixed_crowd_and_where_a_staging_database_is_named(tmp_path):
    crowd = rp.mixed_population(6, (25, 70), ("female", "male"))
    assert [crowd[k]["age"] for k in range(6)] == [25, 70, 25, 70, 25, 70]
    assert [crowd[k]["gender"] for k in range(6)] == ["female", "female", "male", "male", "female", "female"]
    assert rp.database_path(rp.PACKAGE_ROOT / "runs" / "x" / "rule_db_staging" / "stated") == "runs/x/rule_db_staging/stated"
    assert rp.database_path(tmp_path) == tmp_path.resolve().as_posix()


def test_screening_settings():
    settings = rp.ScreeningSettings.from_config({"enabled": True, "repeats": 3, "seed": 5})
    assert [plan.seed for plan in rp.crowd_plans(settings, "x")] == [6, 7, 8]  # paired seeds: base + repeat
    with pytest.raises(rp.ConfigError):
        rp.ScreeningSettings.from_config({"repeats": 0})
    assert replace(settings, repeats=1).as_dict()["repeats"] == 1
