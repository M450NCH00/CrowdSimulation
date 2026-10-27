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


def row(severe, throughput=60.0, delay=1.0, gridlocked=False, matches=1):
    return {"severe_conflicts": severe, "throughput_agents_per_min": throughput, "mean_delay_s": delay, "gridlocked": gridlocked, "rule_matches": matches}


def paired(arm_rows, plain_rows):
    return [{"seed": i, "arm": a, "plain": p} for i, (a, p) in enumerate(zip(arm_rows, plain_rows))]


def test_the_verdicts_follow_the_rule_fixed_before_any_run():
    plain = [row(10, matches=0)] * 10
    assert V.verdict(paired([row(5)] * 10, plain))["verdict"] == V.HELPS
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
    assert (loaded.seeds, loaded.alpha, loaded.seed) == (10, 0.05, 30900)


@pytest.mark.parametrize("change, message", [
    ({"arms": [{"name": "plain", "rules": ["keep_left_head_on"]}]}, "reserved"),
    ({"arms": [{"name": "a", "rules": ["no_such_rule"]}]}, "not listed"),
    ({"arms": [{"name": "a", "rules": ["keep_left_head_on"], "database": "rule_db", "ruleset": "default"}]}, "either"),
    ({"arms": [{"name": "a", "database": "rule_db"}]}, "ruleset"),
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
