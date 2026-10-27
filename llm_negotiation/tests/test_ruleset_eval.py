"""Issue #74 (RF-18): the rule-set evaluation layer, its measures and its verdicts."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from negsim.configutil import ConfigError, PACKAGE_ROOT
from negsim.experiment.cli import main as cli_main
from negsim.rules.canonical import canonical_hash
from negsim.rules.database import RULE_DB_ROOT, RuleDatabase, file_sha256
from negsim.rulegen.writer import StagingDatabase, WriterError
from negsim.ruleset_eval import experiment as E
from negsim.ruleset_eval import measures as M
from negsim.ruleset_eval import verdicts as V

GIT = {"commit": "test", "dirty": False}
RF18 = PACKAGE_ROOT / "configs" / "rule_set_evaluation" / "rf18_round1.yaml"
SMALL_FLOW = {"geometry": {"agents_per_direction": 4, "length": 20.0}, "max_time": 60.0}


def config(**changes):
    raw = {
        "layer": "rule_set_evaluation", "experiment_name": "t",
        "rules": {"keep_left_head_on": {"from": "rule_db", "version": 1}, "younger_yields_head_on": {"from": "rule_db", "version": 1},
                  "overtaker_keeps_clear": {"from": "rule_db", "version": 1}},
        "arms": [{"name": "both", "rules": ["keep_left_head_on", "younger_yields_head_on"]},
                 {"name": "keep_left_alone", "rules": ["keep_left_head_on"]},
                 {"name": "cannot_match", "rules": ["overtaker_keeps_clear"]}],
        "scenarios": [{"name": "head_on", "scenario": "configs/scenarios/wide_corridor_head_on.yaml"}],
        "seed": 100, "seeds": 1,
    }
    raw.update(changes)
    return E.RuleSetEvaluationConfig.from_raw(raw)


# --- the sign test and the verdicts (fixed with the user before any run, task 0) -----------------


def test_the_exact_sign_test_needs_9_of_10_seeds_at_5_percent():
    assert V.sign_test(10, 0) == pytest.approx(2 / 1024)
    assert V.sign_test(9, 1) == pytest.approx(22 / 1024)
    assert V.sign_test(8, 2) == pytest.approx(112 / 1024)
    assert V.sign_test(0, 0) == 1.0
    assert V.sign_test(1, 9) == V.sign_test(9, 1)


def test_ties_and_missing_values_are_dropped_from_the_test():
    result = V.compare([1, 1, 2, None], [2, 1, 1, 3], lower_is_better=True)
    assert (result["better"], result["worse"], result["ties"], result["missing"]) == (1, 1, 1, 1)
    assert result["direction"] == V.SAME


def row(severe, throughput=60.0, delay=1.0, gridlocked=False, matches=1, collided=5, episodes=5):
    return {"severe_conflicts": severe, "throughput_agents_per_min": throughput, "mean_delay_s": delay, "gridlocked": gridlocked,
            "rule_matches": matches, "tiers": {"T4": collided}, "collision_episodes": episodes}


def paired(arm_rows, plain_rows):
    return [{"seed": i, "arm": a, "plain": p} for i, (a, p) in enumerate(zip(arm_rows, plain_rows))]


def test_the_verdicts_follow_the_rule_fixed_before_any_run():
    plain = [row(10, matches=0)] * 10
    assert V.verdict(paired([row(5)] * 10, plain))["verdict"] == V.HELPS
    assert V.verdict(paired([row(5)] * 10, plain), rule=1)["verdict"] == V.HELPS
    assert V.verdict(paired([row(5, throughput=50.0)] * 10, plain))["verdict"] == V.TRADE_OFF
    assert V.verdict(paired([row(5, delay=2.0)] * 10, plain))["verdict"] == V.TRADE_OFF
    assert V.verdict(paired([row(15)] * 10, plain))["verdict"] == V.HARMS
    assert V.verdict(paired([row(10)] * 10, plain))["verdict"] == V.NO_CHANGE
    assert V.verdict(paired([row(5, matches=0)] * 10, plain))["verdict"] == V.NOT_USED
    # 8 of 10 seeds better is not enough at 5%: no change
    assert V.verdict(paired([row(5)] * 8 + [row(15)] * 2, plain))["verdict"] == V.NO_CHANGE
    # a gridlock where plain ORCA had none harms, whatever else improved
    gridlock = V.verdict(paired([row(5)] * 9 + [row(5, gridlocked=True)], plain))
    assert gridlock["verdict"] == V.HARMS and gridlock["new_gridlock_seeds"] == [9]
    # costs alone, with severe conflicts unchanged, are no change (only severe conflicts and gridlock harm)
    assert V.verdict(paired([row(10, throughput=30.0)] * 10, plain))["verdict"] == V.NO_CHANGE


def test_under_rule_2_more_collisions_harm_where_rule_1_saw_fewer_severe_conflicts():
    # Round 1's set 2: fewer near misses, so fewer severe conflicts, but more collisions.
    plain = [row(10, matches=0, collided=3, episodes=3)] * 10
    more_collided = [row(8, collided=6, episodes=3)] * 10
    more_episodes = [row(8, collided=3, episodes=9)] * 10
    assert V.verdict(paired(more_collided, plain), rule=1)["verdict"] == V.HELPS
    assert V.verdict(paired(more_collided, plain), rule=2)["verdict"] == V.HARMS
    assert "more collided pairs" in V.verdict(paired(more_collided, plain))["reasons"][0]
    assert V.verdict(paired(more_episodes, plain))["verdict"] == V.HARMS
    assert "collided_pairs" not in V.verdict(paired(more_episodes, plain), rule=1)["tests"]
    # fewer collisions never help by themselves: severe conflicts decide
    assert V.verdict(paired([row(10, collided=1, episodes=1)] * 10, plain))["verdict"] == V.NO_CHANGE
    with pytest.raises(ValueError):
        V.verdict(paired(more_collided, plain), rule=3)


def test_a_change_of_verdict_rule_rejudges_the_runs_without_running_them_again(tmp_path):
    E.run_evaluation(config(verdict_rule=1), out_root=tmp_path, report=lambda _: None, git=GIT)
    again = E.run_evaluation(config(verdict_rule=2), out_root=tmp_path, report=lambda _: None, git={"commit": "later", "dirty": False})
    assert (again.executed, again.skipped) == (0, 4)
    saved = json.loads((tmp_path / "t" / "config.json").read_text(encoding="utf-8"))
    assert saved["git"] == GIT and saved["judged_git"]["commit"] == "later" and saved["experiment"]["verdict_rule"] == 2
    arm = again.summary["scenarios"]["head_on"]["arms"]["both"]
    assert arm["verdict"]["rule"] == 2 and set(arm["verdict_by_rule"]) == {"1", "2"}


def test_a_rules_reading_over_scenarios_puts_harm_first():
    assert E.overall([V.HELPS, V.HARMS]) == V.HARMS
    assert E.overall([V.NOT_USED, V.HELPS, V.NO_CHANGE]) == V.HELPS
    assert E.overall([V.NOT_USED, V.TRADE_OFF]) == V.TRADE_OFF
    assert E.overall([V.NOT_USED, V.NOT_USED]) == V.NOT_USED


# --- the config ----------------------------------------------------------------------------------


def test_the_round_1_config_loads_with_the_users_priority_for_the_cane_rule():
    loaded = E.RuleSetEvaluationConfig.load(RF18)
    rules = {rule.rule_id: rule for rule in loaded.rules}
    assert rules["ext_head_on_6455ca5589"].priority == 600 and rules["ext_head_on_6455ca5589"].enabled_version == 3
    assert rules["ext_head_on_0ecc2d1a6e"].priority is None and rules["ext_head_on_0ecc2d1a6e"].enabled_version == 2
    assert [arm.name for arm in loaded.arms if not arm.judged] == ["reference_default"]
    assert (loaded.seeds, loaded.alpha, loaded.seed, loaded.verdict_rule) == (10, 0.05, 30900, 2)


@pytest.mark.parametrize("change, message", [
    ({"arms": [{"name": "plain", "rules": ["keep_left_head_on"]}]}, "reserved"),
    ({"arms": [{"name": "a", "rules": ["no_such_rule"]}]}, "not listed"),
    ({"arms": [{"name": "a", "rules": ["keep_left_head_on"], "database": "rule_db", "ruleset": "default"}]}, "either"),
    ({"arms": [{"name": "a", "database": "rule_db"}]}, "ruleset"),
    ({"verdict_rule": 3}, "verdict_rule"),
    ({"rules": {"keep_left_head_on": {"from": "rule_db", "version": 1, "priority": 50}}, "arms": [{"name": "a", "rules": ["keep_left_head_on"]}]}, "reason"),
])
def test_a_config_that_cannot_be_run_as_asked_is_refused(change, message):
    with pytest.raises(ConfigError, match=message):
        config(**change)


# --- the run's own staging database --------------------------------------------------------------


def test_rules_are_copied_byte_for_byte_with_one_rule_set_per_arm(tmp_path):
    copied = E.assemble(config(), tmp_path / "db")
    for entry in copied:
        assert entry["sha256"] == file_sha256(RULE_DB_ROOT / entry["file"])
    database = RuleDatabase.load(tmp_path / "db")
    assert database.rulesets["both"].rules == {"keep_left_head_on": 1, "younger_yields_head_on": 1}
    assert E.assemble(config(), tmp_path / "db") == copied  # idempotent


def test_a_staged_copy_that_differs_from_its_source_is_refused(tmp_path):
    E.assemble(config(), tmp_path / "db")
    path = tmp_path / "db" / "rules" / "keep_left_head_on.v1.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
    with pytest.raises(WriterError, match="frozen with other contents"):
        StagingDatabase(tmp_path / "db").copy_in(RULE_DB_ROOT / "rules" / "keep_left_head_on.v1.yaml", "again")


def test_a_rule_set_is_frozen_once_written(tmp_path):
    staging = StagingDatabase(tmp_path / "db")
    staging.create()
    assert staging.write_ruleset("s", {"keep_left_head_on": 1}, "d")[1] is True
    assert staging.write_ruleset("s", {"keep_left_head_on": 1}, "d")[1] is False
    with pytest.raises(WriterError, match="new name"):
        staging.write_ruleset("s", {"keep_right_head_on": 1}, "d")


def test_two_rules_that_clash_are_refused_together_unless_one_gets_a_new_priority(tmp_path):
    clash = {"rules": {"keep_left_head_on": {"from": "rule_db", "version": 1}, "keep_right_head_on": {"from": "rule_db", "version": 1}},
             "arms": [{"name": "both", "rules": ["keep_left_head_on", "keep_right_head_on"]}]}
    with pytest.raises(ConfigError, match="ambiguous"):
        E.assemble(config(**clash), tmp_path / "refused")
    clash["rules"]["keep_right_head_on"].update(priority=11, reason="test: the right wins")
    E.assemble(config(**clash), tmp_path / "db")
    database = RuleDatabase.load(tmp_path / "db")
    new, old = database.get("keep_right_head_on", 2), database.get("keep_right_head_on", 1)
    assert (new.priority, old.priority) == (11, 10)
    assert canonical_hash(new.written) == canonical_hash(old.written)  # nothing but the priority changed
    assert "the right wins" in new.written["provenance"]["notes"]
    assert database.rulesets["both"].rules == {"keep_left_head_on": 1, "keep_right_head_on": 2}


def test_in_a_small_scenario_the_people_move_on_by_one_so_that_pairs_differ():
    loaded = E.RuleSetEvaluationConfig.load(RF18)
    canes = [tuple(p["mobility_aid"] for p in E.people_for(loaded, 2, repeat, True).values()) for repeat in range(1, 11)]
    assert ("none", "cane") in canes and ("cane", "none") in canes
    assert E.people_for(loaded, 2, 3, False) == E.people_for(loaded, 2, 1, False)


# --- task 8: two hand-made rules switched on together, and an unmatched conflict ----------------


def test_two_rules_together_match_as_documented_and_an_unmatched_conflict_is_logged(tmp_path):
    result = E.run_evaluation(config(), out_root=tmp_path, report=lambda _: None, git=GIT)
    arms = result.summary["scenarios"]["head_on"]["arms"]
    # Ages 25 and 70: the higher priority (younger_yields_head_on, 20) wins over keep_left_head_on (10).
    assert set(arms["both"]["matches_by_rule"]) == {"younger_yields_head_on@1"}
    assert set(arms["keep_left_alone"]["matches_by_rule"]) == {"keep_left_head_on@1"}
    assert arms["both"]["rule_conflicts"]["ambiguous_matches"] == 0
    # A rule for overtaking never matches a head-on: not used, and the head-on is an uncovered conflict.
    assert arms["cannot_match"]["verdict"]["verdict"] == V.NOT_USED
    assert any(u["encounter_class"] == "head_on" for u in arms["cannot_match"]["uncovered"])
    assert arms["plain"]["uncovered"] == []  # plain ORCA matches nothing, so it has nothing to cover
    assert (tmp_path / "t" / "report.md").is_file() and (tmp_path / "t" / "summary.json").is_file()
    again = E.run_evaluation(config(), out_root=tmp_path, report=lambda _: None, git=GIT)
    assert (again.executed, again.skipped) == (0, 4)  # resumes


def test_a_run_with_another_config_in_the_same_folder_is_refused(tmp_path):
    E.run_evaluation(config(), out_root=tmp_path, report=lambda _: None, git=GIT)
    with pytest.raises(ConfigError, match="another config"):
        E.run_evaluation(config(seed=101), out_root=tmp_path, report=lambda _: None, git=GIT)


# --- the measures --------------------------------------------------------------------------------


def test_lanes_are_measured_in_the_two_way_flow_and_nowhere_else(tmp_path):
    small = config(scenarios=[{"name": "flow", "scenario": "configs/scenarios/bidirectional_flow.yaml", "scenario_overrides": SMALL_FLOW}],
                   arms=[{"name": "keep_left_alone", "rules": ["keep_left_head_on"]}], rules={"keep_left_head_on": {"from": "rule_db", "version": 1}})
    result = E.run_evaluation(small, out_root=tmp_path, report=lambda _: None, git=GIT)
    lanes = result.summary["scenarios"]["flow"]["arms"]["keep_left_alone"]["lanes"]
    assert lanes is not None and lanes["share_left"] + lanes["share_right"] == pytest.approx(1.0, abs=0.01)
    head_on = E.run_evaluation(config(experiment_name="t2"), out_root=tmp_path, report=lambda _: None, git=GIT)
    assert head_on.summary["scenarios"]["head_on"]["arms"]["both"]["lanes"] is None


def test_a_pairs_class_is_the_one_it_spent_most_evaluations_in():
    evaluations = [{"encounter_class": "none", "count": 50}, {"encounter_class": "crossing", "count": 2}, {"encounter_class": "head_on", "count": 9}]
    assert M.pair_class({"rules": {"evaluations": evaluations}, "encounter_class_at_start": "none"}) == "head_on"
    assert M.pair_class({"rules": None, "encounter_class_at_start": "overtaking"}) == "overtaking"


def test_delay_is_time_to_goal_minus_the_free_walk():
    config_ = {"scenario": {"agents": [{"agent_id": 0, "path_length_m": 13.0, "preferred_speed_mps": 1.3},
                                        {"agent_id": 1, "path_length_m": 13.0, "preferred_speed_mps": 1.3}]}}
    out = M.delay(config_, {"time_to_goal_s": {"0": 12.0, "1": None}})
    assert out == {"mean_delay_s": 2.0, "max_delay_s": 2.0, "agents_measured": 1}


# --- the command ---------------------------------------------------------------------------------


def test_the_command_plans_without_running_and_refuses_a_client(capsys):
    assert cli_main([str(RF18), "--plan"]) == 0
    assert "150 run(s); no model calls, cost USD 0" in capsys.readouterr().out
    assert cli_main([str(RF18), "--plan", "--client", "mock"]) == 2
    assert cli_main([str(RF18), "--plan", "--confirm"]) == 2


# --- issue #112 (RF-33): populations and purposes --------------------------------------------------

REALISTIC = PACKAGE_ROOT / "configs" / "rule_set_evaluation" / "rf18_round1_realistic.yaml"
RF18_RUN = PACKAGE_ROOT / "runs" / "rf18_round1"
STREET = "configs/populations/singapore_street_v1.yaml"
STRESS = "configs/populations/stress_all_factors_v1.yaml"
HEAD_ON = "configs/scenarios/wide_corridor_head_on.yaml"


def test_rf18s_config_describes_itself_as_its_run_recorded_it():
    recorded = json.loads((RF18_RUN / "config.json").read_text(encoding="utf-8"))["experiment"]
    assert json.loads(json.dumps(E.RuleSetEvaluationConfig.load(RF18).as_dict())) == recorded


def test_rf18s_summary_is_unchanged_when_judged_again_from_its_runs():
    loaded = E.RuleSetEvaluationConfig.load(RF18)
    results = {}
    for path in (RF18_RUN / E.RUNS_SUBDIR).rglob(E.MEASURES_FILE):
        measures = json.loads(path.read_text(encoding="utf-8"))
        results[(measures["scenario"], measures["arm"], measures["seed"])] = measures
    assert len(results) == 150
    recorded = json.loads((RF18_RUN / "summary.json").read_text(encoding="utf-8"))
    again = json.loads(json.dumps(E.summarise(loaded, results)))
    assert again == {"scenarios": recorded["scenarios"], "rule_verdicts": recorded["rule_verdicts"]}


def test_the_realistic_rerun_config_is_rf18s_with_only_the_people_changed():
    old, new = E.RuleSetEvaluationConfig.load(RF18), E.RuleSetEvaluationConfig.load(REALISTIC)
    assert (old.rules, old.arms, old.left_out, old.seed, old.seeds, old.baseline, old.alpha, old.verdict_rule) == \
           (new.rules, new.arms, new.left_out, new.seed, new.seeds, new.baseline, new.alpha, new.verdict_rule)
    by_name = {s.name: s for s in new.scenarios}
    for s in old.scenarios:
        realistic, stress = by_name[f"{s.name}_realistic"], by_name[f"{s.name}_stress"]
        assert realistic.file == stress.file == s.file
        assert (realistic.purpose, realistic.profile.name, stress.purpose, stress.profile.name) == ("realistic", "singapore_street_v1", "stress", "stress_all_factors_v1")
        assert stress.rotate_people == s.rotate_people and not realistic.rotate_people
        assert realistic.pool == (100 if s.rotate_people else None)


def test_a_stress_scenario_gives_rf18s_people_on_every_seed():
    old, new = E.RuleSetEvaluationConfig.load(RF18), E.RuleSetEvaluationConfig.load(REALISTIC)
    stress = {s.name: s for s in new.scenarios}["bottleneck_stress"]
    for repeat in range(1, 11):
        assert stress.profile.people(2, 30900 + repeat, repeat, True) == E.people_for(old, 2, repeat, True)


def scenario(**changes):
    return {"name": "head_on", "scenario": HEAD_ON, **changes}


@pytest.mark.parametrize("entries, message", [
    ([scenario(population=STREET)], "says its 'purpose'"),
    ([scenario(population=STREET, purpose="stress")], "is a realistic profile"),
    ([scenario(population=STRESS, purpose="realistic")], "is a stress profile"),
    ([scenario(population=STREET, purpose="realistic", rotate_people=True)], "rotate_people"),
    ([scenario(population=STRESS, purpose="stress", pool=100)], "pool"),
    ([scenario(pool=100)], "pool"),
    ([scenario(purpose="typical")], "purpose"),
    ([scenario(population=STREET, purpose="realistic"), scenario(name="other")], "every one does"),
    ([scenario(), scenario()], "its own name"),
])
def test_a_scenario_with_a_population_is_checked(entries, message):
    with pytest.raises(ConfigError, match=message):
        config(scenarios=entries)


def test_an_earlier_scenario_describes_itself_as_before():
    described = config().as_dict()["scenarios"][0]
    assert set(described) == {"name", "scenario", "rotate_people", "note"}
    with_population = config(scenarios=[scenario(population=STREET, purpose="realistic", pool=100)]).as_dict()["scenarios"][0]
    assert with_population["population"] == STREET and with_population["purpose"] == "realistic" and with_population["pool"] == 100
    assert with_population["population_sha256"] == E.P.Profile.load(PACKAGE_ROOT / STREET).sha256


def test_a_rules_verdict_of_record_comes_from_its_realistic_scenarios():
    loaded = config(scenarios=[scenario(name="real", purpose="realistic"), scenario(name="stressed", purpose="stress")],
                    arms=[{"name": "keep_left_alone", "rules": ["keep_left_head_on"]}], rules={"keep_left_head_on": {"from": "rule_db", "version": 1}})
    plain, helps, harms = row(10), row(5), row(20)
    results = {}
    for seed in range(1, 11):
        results[("real", "plain", seed)], results[("real", "keep_left_alone", seed)] = plain, {**helps, "rule_matches": 0}
        results[("stressed", "plain", seed)], results[("stressed", "keep_left_alone", seed)] = plain, harms
    filled = {key: {**value, **{k: value.get(k, 0) for k in E.KEPT}, "uncovered": [], "matches_by_rule": {}, "lanes": None,
                    **{k: 0 for k in ("pairs_matched_by_several_rules", "ambiguous_matches", "cross_pair_conflicts", "formation_mismatches",
                                      "plans_started", "plans_skipped_busy", "near_misses", "wall_ms_per_step")}} for key, value in results.items()}
    verdicts = E.summarise(loaded, filled)["rule_verdicts"]["keep_left_head_on"]
    assert verdicts["by_scenario"] == {"real": V.NOT_USED, "stressed": V.HARMS}
    assert verdicts["by_purpose"] == {"realistic": V.NOT_USED, "stress": V.HARMS}
    assert verdicts["overall"] == V.NOT_USED and verdicts["of_record_from"] == "realistic"  # stress never on its own


def test_a_run_with_a_population_gives_every_arm_the_same_people_and_reports_them(tmp_path):
    small = config(scenarios=[{"name": "flow", "scenario": "configs/scenarios/bidirectional_flow.yaml", "scenario_overrides": SMALL_FLOW,
                               "population": STREET, "purpose": "realistic"}],
                   arms=[{"name": "keep_left_alone", "rules": ["keep_left_head_on"]}], rules={"keep_left_head_on": {"from": "rule_db", "version": 1}}, seeds=2)
    planned = E.runs(small, tmp_path / "t")
    by_seed = {}
    for run in planned:
        by_seed.setdefault(run.plan.seed, []).append(run)
    for seed, runs_ in by_seed.items():
        assert len(runs_) == 2 and runs_[0].plan.population == runs_[1].plan.population  # plain and the arm
        assert runs_[0].people == E.P.Profile.load(PACKAGE_ROOT / STREET).people(8, seed)
    assert by_seed[101][0].people != by_seed[102][0].people  # new people on each seed
    result = E.run_evaluation(small, out_root=tmp_path, report=lambda _: None, git=GIT)
    population = result.summary["scenarios"]["flow"]["population"]
    assert population["name"] == "singapore_street_v1" and population["purpose"] == "realistic" and population["limits"]
    assert [entry["seed"] for entry in population["per_seed"]] == [101, 102] and population["mean_per_seed"]["n"] == 8
    assert result.summary["scenarios"]["flow"]["purpose"] == "realistic"
    report = (tmp_path / "t" / "report.md").read_text(encoding="utf-8")
    assert "People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas)" in report and "flow (realistic)" in report
    assert "Of record (realistic)" in report
