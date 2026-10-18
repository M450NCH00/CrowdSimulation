"""The rule database (issue #28, Part 3): loading and its report, frozen versions, version
history, rule sets and how an experiment switches rules on, the ambiguity check, the index
by encounter class, and the read-only command line. Copies of the database are made under
pytest's temporary folder; the real one is only read."""

from __future__ import annotations

import io
import json
import re
import shutil

import pytest

from negsim.avoidance.perception import default_visibility
from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.rules import ActiveRuleSet, RuleDatabase, RuleError
from negsim.rules.ambiguity import MAX_SITUATIONS, Grid, clashes, find_clash
from negsim.rules.cli import main as ruledb
from negsim.rules.database import MANIFEST_FILE, RULE_DB_ROOT, file_sha256, load_validator, read_rule_file

FIXTURES = PACKAGE_ROOT / "tests" / "fixtures" / "rules"
SEEDS = {"keep_left_head_on", "keep_right_head_on", "overtaker_keeps_clear", "single_file_first_arrival", "younger_yields_head_on"}
#: Issue #32's seed rule, schema version 3, not in the default rule set.
SEEDS_32 = {"passage_shorter_backs_out"}


@pytest.fixture(scope="module")
def database():
    return RuleDatabase.load()


@pytest.fixture()
def copy(tmp_path):
    """A copy of the rule database that a test may damage."""
    target = tmp_path / "rule_db"
    shutil.copytree(RULE_DB_ROOT, target)
    return target


def freeze(root, relative):
    """Add a file to a copy's manifest, as writing a new version would."""
    manifest = json.loads((root / MANIFEST_FILE).read_text(encoding="utf-8"))
    manifest["files"][relative] = {"sha256": file_sha256(root / relative), "frozen_on": "2026-10-14", "note": "test"}
    (root / MANIFEST_FILE).write_text(json.dumps(manifest), encoding="utf-8")


def new_version(root, rule_id, version, **changes):
    """Write ``rule_id`` version ``version`` into a copy: the previous version's text, changed."""
    source = (root / "rules" / f"{rule_id}.v{version - 1}.yaml").read_text(encoding="utf-8")
    text = re.sub(rf"(?m)^version: {version - 1}$", f"version: {version}", source)  # not schema_version
    for old, new in changes.items():
        text = text.replace(old, new)
    (root / "rules" / f"{rule_id}.v{version}.yaml").write_text(text, encoding="utf-8")
    freeze(root, f"rules/{rule_id}.v{version}.yaml")


# --- loading -----------------------------------------------------------------------------------------


def test_the_database_loads_the_six_seed_rules_and_reports_them(database):
    """Five of issue #28 and one of issue #32 (five before it)."""
    assert {rule.rule_id for rule in database.rules} == SEEDS | SEEDS_32 and all(rule.version == 1 for rule in database.rules)
    lines = database.report.lines()
    assert lines[0] == "6 rule version(s) loaded, 0 refused"
    assert any(line.startswith("  head_on: ") for line in lines)
    assert all(rule.status == "test_seed" for rule in database.rules)


def test_every_rule_records_its_provenance_and_status(database):
    for rule in database.rules:
        provenance = rule.provenance
        assert provenance["source_type"] == "hand_written" and provenance["validation_evidence"] == []
        assert provenance["created_at"] == ("2026-10-16" if rule.rule_id in SEEDS_32 else "2026-10-14")
        assert provenance["author"] and provenance["source_ref"]
        assert rule.sha256 == file_sha256(RULE_DB_ROOT / rule.source)


def test_the_two_mirror_rules_are_reported_as_unable_to_be_switched_on_together(database):
    (clash,) = database.report.clashes
    assert {clash.first.rule_id, clash.second.rule_id} == {"keep_left_head_on", "keep_right_head_on"}
    assert "pair.encounter_class='head_on'" in clash.describe()


def test_a_refused_rule_stops_the_load_unless_asked_to_report(copy):
    shutil.copy(FIXTURES / "invalid" / "reads_the_task.v1.yaml", copy / "rules")
    freeze(copy, "rules/reads_the_task.v1.yaml")
    with pytest.raises(ConfigError, match="unobservable_field"):
        RuleDatabase.load(copy)
    report = RuleDatabase.load(copy, strict=False).report
    assert [(source, error.category) for source, error in report.refused] == [("rules/reads_the_task.v1.yaml", "unobservable_field")]
    assert len(report.loaded) == 6


# --- a version is never edited ------------------------------------------------------------------------


def test_an_edited_version_is_refused(copy):
    path = copy / "rules" / "keep_left_head_on.v1.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("value: 1.0, unit: m", "value: 1.2, unit: m"), encoding="utf-8")
    report = RuleDatabase.load(copy, strict=False).report
    refused = {source: error for source, error in report.refused}
    assert refused["rules/keep_left_head_on.v1.yaml"].category == "manifest"
    assert "never edited" in str(refused["rules/keep_left_head_on.v1.yaml"])
    # ... and the rule set that names it can no longer be switched on.
    assert set(refused) == {"rules/keep_left_head_on.v1.yaml", "rulesets/default.yaml"}
    assert refused["rulesets/default.yaml"].category == "ruleset"


def test_a_file_not_in_the_manifest_is_refused_and_a_listed_file_must_exist(copy):
    shutil.copy(FIXTURES / "valid" / "gender_keeps_clear_crossing.v1.yaml", copy / "rules")
    (copy / "rules" / "overtaker_keeps_clear.v1.yaml").unlink()
    refused = {source: error.category for source, error in RuleDatabase.load(copy, strict=False).report.refused}
    assert refused["rules/gender_keeps_clear_crossing.v1.yaml"] == "manifest"
    assert refused["rules/overtaker_keeps_clear.v1.yaml"] == "manifest"  # listed but missing


def test_line_endings_do_not_change_the_hash(tmp_path):
    lf, crlf = tmp_path / "lf.yaml", tmp_path / "crlf.yaml"
    lf.write_bytes(b"a: 1\nb: 2\n")
    crlf.write_bytes(b"a: 1\r\nb: 2\r\n")
    assert file_sha256(lf) == file_sha256(crlf)


def test_a_change_is_a_new_version_and_the_old_one_stays(copy, capsys):
    new_version(copy, "keep_left_head_on", 2, **{"status: test_seed": "status: candidate", "value: 1.0, unit: m": "value: 1.2, unit: m"})
    database = RuleDatabase.load(copy)
    first, second = database.history("keep_left_head_on")
    assert (first.version, first.status, second.version, second.status) == (1, "test_seed", 2, "candidate")
    assert database.get("keep_left_head_on", 1).when.comparisons().__next__().value == 1.0
    assert ruledb(["--db", str(copy), "history", "keep_left_head_on"]) == 0
    printed = capsys.readouterr().out
    assert "keep_left_head_on@1" in printed and "keep_left_head_on@2" in printed
    assert "changed from version 1: status, when" in printed


def test_versions_must_run_one_two_three(copy):
    new_version(copy, "keep_left_head_on", 2)
    (copy / "rules" / "keep_left_head_on.v2.yaml").rename(copy / "rules" / "keep_left_head_on.v3.yaml")
    text = (copy / "rules" / "keep_left_head_on.v3.yaml").read_text(encoding="utf-8").replace("version: 2\n", "version: 3\n")
    (copy / "rules" / "keep_left_head_on.v3.yaml").write_text(text, encoding="utf-8")
    freeze(copy, "rules/keep_left_head_on.v3.yaml")
    manifest = json.loads((copy / MANIFEST_FILE).read_text(encoding="utf-8"))
    del manifest["files"]["rules/keep_left_head_on.v2.yaml"]
    (copy / MANIFEST_FILE).write_text(json.dumps(manifest), encoding="utf-8")
    refused = {error.category for _, error in RuleDatabase.load(copy, strict=False).report.refused}
    assert refused == {"history"}


# --- rule sets, and switching rules on ------------------------------------------------------------------


def test_the_default_rule_set_switches_on_four_seeds_and_not_keep_right(database):
    active = database.activate("default")
    assert {rule.key for rule in active.rules} == {
        "keep_left_head_on@1", "overtaker_keeps_clear@1", "single_file_first_arrival@1", "younger_yields_head_on@1",
    }
    assert [rule.key for rule in active.candidates("head_on")] == ["younger_yields_head_on@1", "keep_left_head_on@1"]
    assert [rule.key for rule in active.candidates("overtaking")] == ["overtaker_keeps_clear@1"]
    assert active.candidates("none") == () and active.candidates(None) == ()


def test_an_experiment_swaps_keep_left_for_keep_right(database):
    active = database.activate("default", enable={"keep_right_head_on": 1}, disable=["keep_left_head_on"])
    assert "keep_right_head_on@1" in {rule.key for rule in active.rules} and "keep_left_head_on@1" not in {rule.key for rule in active.rules}
    with pytest.raises(RuleError) as caught:
        database.activate("default", enable={"keep_right_head_on": 1})
    assert caught.value.category == "ambiguous" and "keep_left_head_on@1 and keep_right_head_on@1" in str(caught.value)


@pytest.mark.parametrize(
    "arguments, category",
    [
        (dict(ruleset="nonexistent"), "ruleset"),
        (dict(enable={"keep_left_head_on": 2}), "ruleset"),
        (dict(enable={"no_such_rule": 1}), "ruleset"),
        (dict(ruleset="default", disable=["keep_right_head_on"]), "ruleset"),
    ],
)
def test_a_bad_rule_set_is_refused_with_a_reason(database, arguments, category):
    with pytest.raises(RuleError) as caught:
        database.activate(**arguments)
    assert caught.value.category == category


def test_only_usable_statuses_can_be_switched_on(copy):
    new_version(copy, "keep_left_head_on", 2, **{"status: test_seed": "status: retired"})
    database = RuleDatabase.load(copy)
    with pytest.raises(RuleError) as caught:
        database.activate(enable={"keep_left_head_on": 2})
    assert caught.value.category == "status"
    database.activate(enable={"keep_left_head_on": 1})  # the old version is still there and usable


def test_a_rule_set_is_frozen_too(copy):
    path = copy / "rulesets" / "default.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("younger_yields_head_on: 1\n", ""), encoding="utf-8")
    refused = {source: error.category for source, error in RuleDatabase.load(copy, strict=False).report.refused}
    assert refused == {"rulesets/default.yaml": "manifest"}


def test_a_rule_that_reads_what_the_run_hides_is_refused_for_that_run(database):
    active = database.activate("default")
    active.check_visibility(default_visibility())
    with pytest.raises(RuleError) as caught:
        active.check_visibility({**default_visibility(), "age": False})
    assert caught.value.category == "visibility" and "younger_yields_head_on@1" in str(caught.value)
    database.activate("default", disable=["younger_yields_head_on"]).check_visibility({**default_visibility(), "age": False})


# --- the ambiguity check -----------------------------------------------------------------------------


def fixture(name):
    return read_rule_file(next(FIXTURES.rglob(f"{name}.v1.yaml")), load_validator(RULE_DB_ROOT))


def test_the_ambiguous_fixtures_load_one_at_a_time_and_are_refused_together():
    first, second = fixture("clash_side"), fixture("clash_clearance")
    ActiveRuleSet.build([first])
    ActiveRuleSet.build([second])
    with pytest.raises(RuleError) as caught:
        ActiveRuleSet.build([first, second])
    assert caught.value.category == "ambiguous"
    clash = find_clash(first, second)
    assert clash.situation.pair["time_to_collision_s"] <= 5.0 and clash.situation.pair["distance_m"] < 10.0


def test_rules_that_cannot_both_match_are_not_a_clash(database):
    left = database.get("keep_left_head_on", 1)
    assert find_clash(left, fixture("clash_side")) is None  # different priorities
    overtaking = database.get("overtaker_keeps_clear", 1)
    assert clashes([left, overtaking]) == []  # different encounters
    narrow = fixture("clash_side")
    # The same priority and encounter, but conditions that exclude each other.
    import dataclasses

    from negsim.rules.conditions import parse_condition

    wide = dataclasses.replace(narrow, rule_id="wide_only", when=parse_condition({"field": "pair.distance_m", "op": ">=", "value": 10.0, "unit": "m"}, "t"))
    assert find_clash(narrow, wide) is None


def test_the_grid_tries_both_orders_and_the_tie_of_a_role_field(database):
    younger = database.get("younger_yields_head_on", 1)
    grid = Grid(younger, younger)
    ages = {(situation.agent_values[0]["age"], situation.agent_values[1]["age"]) for situation in grid}
    assert any(a is not None and b is not None and a < b for a, b in ages)
    assert any(a is not None and b is not None and a > b for a, b in ages)
    assert any(a is not None and a == b for a, b in ages)
    assert (None, None) in ages and grid.size < MAX_SITUATIONS


# --- the command line --------------------------------------------------------------------------------


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    status = ruledb(list(argv), out=out, err=err)
    return status, out.getvalue(), err.getvalue()


def test_list_shows_every_version_and_the_rule_sets():
    status, out, _ = run_cli("list")
    assert status == 0
    for name in SEEDS:
        assert f"{name}@1" in out
    assert "rule set default: keep_left_head_on@1, overtaker_keeps_clear@1, single_file_first_arrival@1, younger_yields_head_on@1" in out


def test_validate_checks_the_database_or_given_files():
    assert run_cli("validate")[0] == 0
    status, out, _ = run_cli("validate", "--file", *map(str, sorted((FIXTURES / "invalid").glob("*.yaml"))))
    assert status == 1 and out.count("REFUSED") == len(list((FIXTURES / "invalid").glob("*.yaml")))
    status, out, _ = run_cli("validate", "--file", str(FIXTURES / "valid" / "gender_keeps_clear_crossing.v1.yaml"))
    assert status == 0 and out.startswith("OK")


def test_show_prints_a_version_as_written_and_unknown_rules_fail():
    status, out, _ = run_cli("show", "younger_yields_head_on")
    assert status == 0 and out == (RULE_DB_ROOT / "rules" / "younger_yields_head_on.v1.yaml").read_text(encoding="utf-8")
    status, _, err = run_cli("history", "no_such_rule")
    assert status == 1 and "not in the database" in err


def test_the_command_line_writes_nothing(tmp_path):
    before = {path: path.read_bytes() for path in RULE_DB_ROOT.rglob("*") if path.is_file()}
    for argv in (("list",), ("validate",), ("history", "keep_left_head_on"), ("show", "keep_left_head_on")):
        run_cli(*argv)
    after = {path: path.read_bytes() for path in RULE_DB_ROOT.rglob("*") if path.is_file()}
    assert before == after
    import ast

    source = (PACKAGE_ROOT / "negsim" / "rules" / "cli.py").read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"write_text", "write_bytes", "unlink", "rename", "mkdir"}, node.attr
