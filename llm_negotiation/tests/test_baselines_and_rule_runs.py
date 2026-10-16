"""Baselines and rule-following runs end to end (issue #28, Parts 1 and 7): the frozen
baselines and how an experiment applies them; the perturbation; an experiment with the rule
provider; the files of a version-3 run, their schema check, and the documents. Everything
is written under pytest's temporary folder."""

from __future__ import annotations

import json
import re
import shutil

import pytest

from helpers import avoidance_config, crowd
from negsim.avoidance.simulation import AvoidanceSimulation, Perturbation
from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.experiment import AvoidanceExperiment, execute_avoidance_run, run_avoidance_experiment
from negsim.experiment.baselines import BASELINE_DIR, MANIFEST, load_baseline
from negsim.rules.database import file_sha256
from negsim.runlog import (
    AVOIDANCE_RUN_FILES,
    CONFIG_FILE,
    EVENTS_FILE,
    PAIR_INTERACTIONS_FILE,
    TRAJECTORY_FILE,
    validate_run_dir,
)

GIT = {"commit": "abc123", "dirty": False}
QUIET = lambda line: None  # noqa: E731
RULES = {"provider": "rules", "ruleset": "default"}
PERSONAS = "configs/personas/personas.yaml"


def experiment(**changes):
    return AvoidanceExperiment(avoidance_config(**changes), source="<test>")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


# --- the baselines ----------------------------------------------------------------------------------


def test_the_two_baselines_are_as_the_issue_sets_them():
    primary, secondary = load_baseline("orca_perturbed_v1"), load_baseline("orca_unperturbed_v1")
    assert (primary.role, secondary.role) == ("primary", "secondary")
    assert primary.perturbation == Perturbation(1e-4) and not secondary.perturbation.active
    for baseline in (primary, secondary):
        assert dict(baseline.agent_types) == {"max_neighbours": 40, "sensing_radius": 12.5}
        assert baseline.tie_break == "brake"
        assert "Supervisor sign-off: pending" in baseline.sign_off and "set by the user in issue #28" in baseline.sign_off


def test_a_baseline_file_is_frozen(tmp_path):
    copy = tmp_path / "baselines"
    shutil.copytree(BASELINE_DIR, copy)
    load_baseline("orca_perturbed_v1", copy)
    path = copy / "orca_perturbed_v1.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("max_neighbours: 40", "max_neighbours: 10"), encoding="utf-8")
    with pytest.raises(ConfigError, match="orca_perturbed_v2.yaml"):
        load_baseline("orca_perturbed_v1", copy)
    shutil.copy(copy / "orca_unperturbed_v1.yaml", copy / "orca_unperturbed_v2.yaml")
    with pytest.raises(ConfigError, match="not frozen"):
        load_baseline("orca_unperturbed_v2", copy)
    manifest = json.loads((BASELINE_DIR / MANIFEST).read_text(encoding="utf-8"))
    assert set(manifest["files"]) == {"orca_perturbed_v1.yaml", "orca_unperturbed_v1.yaml"}
    assert all(entry["sha256"] == file_sha256(BASELINE_DIR / name) for name, entry in manifest["files"].items())


@pytest.mark.parametrize("name, message", [("orca_missing_v1", "no such baseline"), ("orca_perturbed", "ends in its version"), (7, "ends in its version")])
def test_an_unknown_baseline_is_refused(name, message):
    with pytest.raises(ConfigError, match=message):
        load_baseline(name)


def test_an_experiment_lays_its_baseline_under_its_own_overrides():
    plans = experiment(
        baseline="orca_perturbed_v1",
        design={"seed": 1, "factors": {"radius": [
            {"name": "primary"},
            {"name": "sensitivity_5m", "scenario_overrides": {"agent_types": {"pedestrian": {"sensing_radius": 5.0}}}},
            {"name": "secondary", "baseline": "orca_unperturbed_v1"},
        ]}},
    ).plans()
    primary, five, secondary = plans
    for plan, radius in ((primary, 12.5), (five, 5.0), (secondary, 12.5)):
        types = plan.scenario_config["agent_types"]["pedestrian"]
        assert (types["max_neighbours"], types["sensing_radius"]) == (40, radius)
    assert primary.perturbation == five.perturbation == Perturbation(1e-4) and not secondary.perturbation.active
    assert (primary.baseline.name, secondary.baseline.name) == ("orca_perturbed_v1", "orca_unperturbed_v1")
    assert experiment().plans()[0].baseline is None  # no baseline: issue #26's settings, as before


# --- the perturbation ----------------------------------------------------------------------------


def run_head_on(seed, perturbation):
    return AvoidanceSimulation(crowd("wide_corridor_head_on"), seed=seed, perturbation=perturbation).run()


def test_the_perturbation_breaks_the_exactly_symmetric_deadlock_and_is_seeded():
    assert run_head_on(1, Perturbation()).deadlock
    first, again, other = run_head_on(1, Perturbation(1e-4)), run_head_on(1, Perturbation(1e-4)), run_head_on(2, Perturbation(1e-4))
    assert not first.deadlock and first.status == "completed"
    assert [row["x_m"] for row in first.trajectory] == [row["x_m"] for row in again.trajectory]
    assert [row["y_m"] for row in first.trajectory] != [row["y_m"] for row in other.trajectory]


def test_the_perturbation_moves_a_preferred_velocity_by_no_more_than_its_magnitude():
    result = run_head_on(3, Perturbation(1e-4))
    plain = run_head_on(3, Perturbation())
    unperturbed_x = {(row["step"], row["agent_id"]): row for row in plain.trajectory if row["step"] < 14}
    for row in result.trajectory:
        key = (row["step"], row["agent_id"])
        if key in unperturbed_x and row["pref_vx_mps"] is not None:  # before they see each other
            base = unperturbed_x[key]
            moved = ((row["pref_vx_mps"] - base["pref_vx_mps"]) ** 2 + (row["pref_vy_mps"] - base["pref_vy_mps"]) ** 2) ** 0.5
            assert moved <= 1e-4 + 2e-6  # the trajectory rounds to 6 decimals


def test_a_negative_magnitude_is_refused():
    with pytest.raises(ValueError):
        Perturbation(-1e-4)


# --- a rule-following run, and its files ----------------------------------------------------------


@pytest.fixture()
def rule_run(tmp_path):
    plan = experiment(
        baseline="orca_perturbed_v1",
        personas=PERSONAS,
        population={"agents": {0: {"persona": "f25"}, 1: {"persona": "m70"}}},
        directives=RULES,
    ).plans()[0]
    run_dir = tmp_path / "run"
    return run_dir, execute_avoidance_run(plan, run_dir, GIT)


def test_a_rule_run_writes_six_files_that_pass_the_schema_check(rule_run):
    run_dir, outcome = rule_run
    assert sorted(path.name for path in run_dir.iterdir()) == sorted(AVOIDANCE_RUN_FILES)
    assert PAIR_INTERACTIONS_FILE in AVOIDANCE_RUN_FILES and validate_run_dir(run_dir) == []
    assert outcome["log_schema_version"] == 4 and outcome["baseline"] == "orca_perturbed_v1"  # 3 before issue #30


def test_the_run_records_its_active_rule_set_and_baseline(rule_run):
    config = read_json(rule_run[0] / CONFIG_FILE)
    directives = config["directives"]
    assert directives["provider"] == "rules" and directives["ruleset"] == "default" and directives["hysteresis_steps"] == 3
    assert [(rule["rule_id"], rule["version"]) for rule in directives["rules"]] == [
        ("keep_left_head_on", 1), ("overtaker_keeps_clear", 1), ("single_file_first_arrival", 1), ("younger_yields_head_on", 1),
    ]
    assert all(re.fullmatch(r"[0-9a-f]{64}", rule["sha256"]) for rule in directives["rules"])
    assert config["baseline"]["name"] == "orca_perturbed_v1" and config["perturbation"] == {"kind": "rvo2_uniform", "magnitude_mps": 0.0001}
    assert config["scenario"]["agent_types"]["pedestrian"]["max_neighbours"] == 40 and config["perception_schema_version"] == 3  # 2 before issue #32


def test_the_pair_record_has_every_evaluation_the_match_its_roles_snapshot_and_expiry(rule_run):
    run_dir, outcome = rule_run
    (pair,) = read_jsonl(run_dir / PAIR_INTERACTIONS_FILE)
    rules = pair["rules"]
    (match,) = rules["matches"]
    assert (match["rule_id"], match["version"], match["roles"]) == ("younger_yields_head_on", 1, {"0": "yielder", "1": "other"})
    assert match["directives"]["0"]["responsibility_share"] == 1.0 and match["snapshot"]["pair"]["age_difference_years"] == 45
    assert match["end_reason"] == "passed" and match["to_step"] == pair["passed_step"]
    assert sum(entry["count"] for entry in rules["evaluations"]) == outcome["rules"]["evaluations"]["rule_matched"] + outcome["rules"]["evaluations"]["no_rule_matched"]
    assert pair["outcome"] in ("avoided", "resolved", "failed") and rules["independent_agrees"] is True
    assert outcome["interaction_outcomes"]["pairs"] == 1 and outcome["rules"]["matches_begun"] == {"younger_yields_head_on@1": 1}


def test_the_schema_check_notices_damage_to_the_pair_file(rule_run, tmp_path):
    run_dir = rule_run[0]
    for damage in ("missing_field", "outcome", "count", "rule_block", "event"):
        copy = tmp_path / damage
        shutil.copytree(run_dir, copy)
        pairs = read_jsonl(copy / PAIR_INTERACTIONS_FILE)
        if damage == "missing_field":
            del pairs[0]["passed_step"]
        elif damage == "outcome":
            pairs[0]["outcome"] = "survived"
        elif damage == "count":
            pairs = []
        elif damage == "rule_block":
            del pairs[0]["rules"]["matches"][0]["end_reason"]
        (copy / PAIR_INTERACTIONS_FILE).write_text("".join(json.dumps(pair) + "\n" for pair in pairs), encoding="utf-8")
        if damage == "event":
            (copy / EVENTS_FILE).write_text(json.dumps({"event_index": 0, "type": "rule_vibes", "time_s": 0.0}) + "\n", encoding="utf-8")
        assert validate_run_dir(copy) != [], damage


def test_a_plain_run_has_pair_interactions_too_without_rules(tmp_path):
    plan = experiment(baseline="orca_unperturbed_v1").plans()[0]
    outcome = execute_avoidance_run(plan, tmp_path / "plain", GIT)
    (pair,) = read_jsonl(tmp_path / "plain" / PAIR_INTERACTIONS_FILE)
    assert pair["rules"] is None and outcome["rules"] is None
    assert pair["outcome"] == "failed" and pair["outcome_detail"]["deadlock"]  # the exactly symmetric head-on
    assert outcome["interaction_outcomes"] == {
        "pairs": 1, "avoided": 0, "resolved": 0, "failed": 1,
        "pairs_with": {"exposed": 1, "pair_exposed": 1, "yielded": 1, "collided": 0, "deadlocked": 1, "open_at_timeout": 0},
        "tiers": {"T0": 0, "T1": 0, "T2": 0, "T3": 0, "T4": 1},  # issue #30: a deadlock is T4
    }


def test_logging_interactions_off_leaves_out_the_pair_file_but_keeps_the_counts(tmp_path):
    plan = experiment(logging={"interactions": False}, directives=RULES).plans()[0]
    outcome = execute_avoidance_run(plan, tmp_path / "thin", GIT)
    assert (tmp_path / "thin" / PAIR_INTERACTIONS_FILE).read_text(encoding="utf-8") == ""
    assert outcome["interaction_outcomes"]["pairs"] == 1 and validate_run_dir(tmp_path / "thin") == []


@pytest.mark.parametrize(
    "directives, message",
    [
        ({"provider": "rules", "ruleset": "nope"}, "unknown rule set"),
        ({"provider": "rules", "enable": {"keep_left_head_on": 1, "keep_right_head_on": 1}}, "cannot be switched on together"),
        ({"provider": "rules", "enable": {"keep_left_head_on": "1"}}, "mapping from rule_id to version"),
        ({"provider": "rules", "disable": "keep_left_head_on"}, "a list of rule ids"),
        ({"provider": "rules", "hysteresis_steps": 0}, "1 or more"),
        ({"provider": "static", "ruleset": "default"}, "apply only to provider 'rules'"),
        ({"provider": "rules", "default": {"side_preference": "left"}}, "unknown key"),
    ],
)
def test_a_bad_rules_block_is_refused_with_a_reason(directives, message):
    with pytest.raises(ConfigError, match=message):
        experiment(directives=directives)


def test_a_rule_set_that_reads_a_hidden_attribute_is_refused_for_that_run():
    with pytest.raises(ConfigError, match="visibility"):
        experiment(directives=RULES, visibility={"age": False})
    experiment(directives={**RULES, "disable": ["younger_yields_head_on"]}, visibility={"age": False})


def test_the_summary_has_the_rule_columns(tmp_path):
    # A level's directives are laid on the base's, so the rules go in a level of their own.
    config = experiment(design={"seed": 5, "factors": {"mode": [{"name": "rules", "directives": RULES}, {"name": "plain"}]}})
    result = run_avoidance_experiment(config, out_root=tmp_path, report=QUIET, git=GIT)
    rows = result.rows
    assert rows[0]["ruleset"] == "default" and rows[0]["rules_fired"] == "keep_left_head_on@1=1" and rows[0]["pairs"] == 1
    assert rows[1]["ruleset"] is None and rows[1]["rules_fired"] is None
    assert (tmp_path / "test_avoidance" / "001_rules" / TRAJECTORY_FILE).is_file()


# --- the documents keep up -------------------------------------------------------------------------


def test_the_schema_document_names_every_field_of_version_3():
    from negsim.runlog import schema

    document = (PACKAGE_ROOT / "docs" / "log-schema.md").read_text(encoding="utf-8")
    assert "- **3** (2026-10-14, issue #28)" in document
    for group in (
        "PAIR_INTERACTION_KEYS", "PAIR_INTERACTION_END_REASONS", "PAIR_OUTCOME_DETAIL_KEYS", "PAIR_RULE_KEYS",
        "RULE_EVALUATION_KEYS", "RULE_EVALUATION_OUTCOMES", "RULE_MATCH_KEYS", "RULE_MATCH_END_REASONS",
        "INTERACTION_OUTCOMES", "INTERACTION_OUTCOME_KEYS", "RULE_SUMMARY_KEYS",
    ):
        for field in getattr(schema, group):
            pattern = r"(?<![A-Za-z0-9_])" + re.escape(field) + r"(?![A-Za-z0-9_])"
            assert re.search(pattern, document), f"{group}: '{field}' is not described in docs/log-schema.md"


def test_the_documents_issue_28_asks_for_exist():
    docs = PACKAGE_ROOT / "docs"
    for name in ("baseline", "rule-format", "rule-matching", "perception", "derivations", "architecture", "log-schema"):
        assert (docs / f"{name}.md").is_file(), name
    baseline = (docs / "baseline.md").read_text(encoding="utf-8")
    assert "Values set by the user in this issue. Supervisor sign-off: pending unless the work log records otherwise." in baseline
    assert "orca_perturbed_v1" in baseline and "orca_unperturbed_v1" in baseline and "[placeholder]" in baseline
    derivations = (docs / "derivations.md").read_text(encoding="utf-8")
    assert "## 15." in derivations and "p · v" in derivations
    rule_format = (docs / "rule-format.md").read_text(encoding="utf-8")
    for word in ("schema_version", "validation_evidence", "no_match", "tie_within", "either.", "both.", "agent.", "expiry"):
        assert word in rule_format, word
    matching = (docs / "rule-matching.md").read_text(encoding="utf-8")
    for word in ("shared snapshot", "no_rule_matched", "ambiguous_match", "cross_pair_conflict", "hysteresis", "grid"):
        assert word in matching, word


# --- the two artefacts of issue #26 are counted, not fixed ------------------------------------------


def test_walking_backwards_is_counted_where_issue_26_saw_it():
    """Shares (1, 0) and no side, exactly head-on: agent 0 backed away along its line for 7 s."""
    from helpers import static

    result = AvoidanceSimulation(crowd("wide_corridor_head_on"), static({"responsibility_share": 1.0}, {"responsibility_share": 0.0})).run()
    agents = result.artefacts["agents"]
    assert agents["0"]["backward_episodes"] == 1 and agents["0"]["backward_time_s"] >= 5.0
    assert agents["1"]["backward_episodes"] == 0 and result.artefacts["totals"]["agents_backward"] == 1


def test_being_hurried_along_is_counted_where_issue_26_saw_it():
    """Exactly behind, unperturbed: the slower walker in front was pushed from 1.10 to 1.29 m/s."""
    result = AvoidanceSimulation(crowd("overtaking")).run()
    agents = result.artefacts["agents"]
    assert agents["1"]["hurried_episodes"] >= 1 and agents["1"]["hurried_time_s"] > 10.0
    assert agents["0"]["hurried_episodes"] == 0  # the one behind is held back, not hurried


def test_an_ordinary_pass_has_neither_artefact():
    result = AvoidanceSimulation(crowd("wide_corridor_head_on", geometry={"lateral_offsets": [0.05, -0.05]})).run()
    totals = result.artefacts["totals"]
    assert (totals["backward_episodes"], totals["hurried_episodes"]) == (0, 0)
    assert result.artefacts["thresholds"] == {"backward_speed_mps": 0.1, "hurried_fraction": 0.05, "min_duration_s": 1.0}
