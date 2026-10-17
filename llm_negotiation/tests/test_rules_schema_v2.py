"""Issue #30, Part 1.3: version 2 of the rule format, beside version 1.

Version 2 adds the source type ``stated``, an ``intent`` and a ``screening`` list, and lets
provenance carry the writer's ``generation`` record and the promotion command's
``promotion`` record (``docs/rule-format.md``, section 12). A version 1 file must still load
exactly as before.
"""

from __future__ import annotations

import copy
import io
import json
from pathlib import Path

import pytest
import yaml

from negsim.configutil import PACKAGE_ROOT
from negsim.rules import RuleDatabase, RuleError
from negsim.rules.cli import main as ruledb
from negsim.rules.database import RULE_DB_ROOT, RuleSchemas, load_validator, read_rule_file, schema_path
from negsim.rules.jsonschema_subset import Validator, unsupported_keywords
from negsim.rules.model import LATEST_SCHEMA_VERSION, SCHEMA_VERSIONS, parse_rule

FIXTURE = PACKAGE_ROOT / "tests" / "fixtures" / "rules" / "v2" / "stated_keeps_clear_any.v1.yaml"
SCHEMAS = load_validator(RULE_DB_ROOT)


def fixture() -> dict:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def test_both_schemas_are_in_the_database_and_frozen():
    """Version 3 (issue #32, ``test_rules_schema_v3.py``) is there too."""
    assert SCHEMA_VERSIONS == (1, 2, 3) and LATEST_SCHEMA_VERSION == 3
    assert isinstance(SCHEMAS, RuleSchemas) and SCHEMAS.versions == (1, 2, 3)
    manifest = json.loads((RULE_DB_ROOT / "MANIFEST.json").read_text(encoding="utf-8"))["files"]
    for version in (1, 2):
        assert schema_path(version) in manifest
        assert unsupported_keywords(json.loads((RULE_DB_ROOT / schema_path(version)).read_text(encoding="utf-8"))) == set()
    RuleDatabase.load(RULE_DB_ROOT)  # the database still loads, with the new schema frozen in it


def test_every_version_1_rule_of_the_database_loads_as_before():
    database = RuleDatabase.load(RULE_DB_ROOT)
    version_1 = [rule for rule in database.rules if rule.schema_version == 1]
    assert len(version_1) == 5  # issue #32's seed rule is of version 3
    for rule in version_1:
        assert (rule.schema_version, rule.intent, rule.screening) == (1, "", ())
        assert rule.describe()["schema_version"] == 1
        # Read against the version 1 schema alone, it gives the same rule.
        alone = read_rule_file(RULE_DB_ROOT / rule.source, Validator(json.loads((RULE_DB_ROOT / schema_path(1)).read_text(encoding="utf-8"))), RULE_DB_ROOT)
        assert alone == rule


def test_a_version_2_rule_loads_with_its_intent_screening_and_generation_record():
    rule = read_rule_file(FIXTURE, SCHEMAS)
    assert (rule.rule_id, rule.version, rule.schema_version, rule.status) == ("stated_keeps_clear_any", 1, 2, "candidate")
    assert rule.provenance["source_type"] == "stated"
    assert rule.intent == "Keep a little more room between the two whenever they meet."
    assert rule.screening[0]["verdict"] == "passed" and rule.provenance["generation"]["sessions"][0]["session_id"] == "B_test_0001"
    assert rule.directives["both"].clearance_margin == 0.15


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda raw: raw.update(schema_version=1), "unknown property 'intent'"),  # version 1 has no intent
        (lambda raw: raw.update(schema_version=4), "must be one of [1, 2, 3]"),  # 3 since issue #32
        (lambda raw: raw.pop("schema_version"), "missing required property 'schema_version'"),
        (lambda raw: raw.update(intent="x" * 501), "at most 500 character"),
        (lambda raw: raw["provenance"].update(source_type="dreamed"), "must be one of"),
        (lambda raw: raw["provenance"]["generation"].update(canonical_hash="abc"), "does not match the pattern"),
        (lambda raw: raw["screening"][0].update(verdict="maybe"), "must be one of"),
        (lambda raw: raw["screening"][0].pop("results"), "missing required property 'results'"),
        (lambda raw: raw.update(colour="blue"), "unknown property 'colour'"),
    ],
)
def test_what_version_2_refuses(change, message):
    raw = fixture()
    change(raw)
    with pytest.raises(RuleError) as error:
        parse_rule(raw, SCHEMAS, "test")
    assert error.value.category == "schema" and message in str(error.value)


def test_version_1_is_unchanged_it_does_not_take_stated_or_intent():
    raw = yaml.safe_load((RULE_DB_ROOT / "rules" / "keep_left_head_on.v1.yaml").read_text(encoding="utf-8"))
    parse_rule(raw, SCHEMAS, "test")
    for change in ({"provenance": {**raw["provenance"], "source_type": "stated"}}, {"intent": "anything"}, {"screening": []}):
        with pytest.raises(RuleError, match="schema"):
            parse_rule({**copy.deepcopy(raw), **change}, SCHEMAS, "test")
    # The same rule written as version 2 is the same rule.
    as_two = {**copy.deepcopy(raw), "schema_version": 2}
    one, two = parse_rule(raw, SCHEMAS, "one"), parse_rule(as_two, SCHEMAS, "two")
    assert (one.when, one.roles, one.directives, one.priority) == (two.when, two.roles, two.directives, two.priority)


def test_the_checks_after_the_schema_apply_to_version_2_as_to_version_1():
    raw = fixture()
    raw["directive"] = {"both": {"responsibility_share": 0.3}}
    with pytest.raises(RuleError) as error:
        parse_rule(raw, SCHEMAS, "test")
    assert error.value.category == "reciprocity"
    raw = fixture()
    raw["when"] = {"all": [{"field": "either.task", "op": "==", "value": "x"}]}
    with pytest.raises(RuleError) as error:
        parse_rule(raw, SCHEMAS, "test")
    assert error.value.category == "unobservable_field"


def test_a_database_refuses_a_version_2_schema_it_has_not_frozen(tmp_path):
    import shutil

    copy_root = tmp_path / "db"
    shutil.copytree(RULE_DB_ROOT, copy_root)
    manifest = json.loads((copy_root / "MANIFEST.json").read_text(encoding="utf-8"))
    del manifest["files"][schema_path(2)]
    (copy_root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    database = RuleDatabase.load(copy_root, strict=False)
    assert any(source == schema_path(2) and error.category == "manifest" for source, error in database.report.refused)


def test_history_compares_the_new_fields(tmp_path):
    import shutil

    root = tmp_path / "db"
    shutil.copytree(RULE_DB_ROOT, root)
    raw = fixture()
    second = copy.deepcopy(raw)
    second["version"] = 2
    second["intent"] = "Keep more room."
    for version, data in ((1, raw), (2, second)):
        (root / "rules" / f"stated_keeps_clear_any.v{version}.yaml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8", newline="\n")
    from negsim.rules.database import file_sha256

    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    for version in (1, 2):
        name = f"rules/stated_keeps_clear_any.v{version}.yaml"
        manifest["files"][name] = {"sha256": file_sha256(root / name), "frozen_on": "2026-10-15", "note": "test"}
    (root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    out = io.StringIO()
    assert ruledb(["--db", str(root), "history", "stated_keeps_clear_any"], out=out) == 0
    assert "changed from version 1: intent" in out.getvalue()
    listing = io.StringIO()
    assert ruledb(["--db", str(root), "list"], out=listing) == 0
    assert "stated" in listing.getvalue()


def test_the_document_describes_version_2():
    document = (PACKAGE_ROOT / "docs" / "rule-format.md").read_text(encoding="utf-8")
    for word in ("schema_version: 2", "`stated`", "`intent`", "`screening`", "`generation`", "`promotion`", "migrat"):
        assert word in document, word
    assert Path(RULE_DB_ROOT / schema_path(2)).is_file()
