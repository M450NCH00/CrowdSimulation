"""Issue #32, Part 2.5: version 3 of the rule format, beside versions 1 and 2.

Version 3 adds the directive field ``back_up``, true or false as the value of a comparison, and
the four passage fields (``docs/rule-format.md``, section 14). Versions 1 and 2 load exactly as
before and can use none of it. A rule that says who backs up must make exactly one of two roles
back up, and not the role that goes first; one that says nothing of it is not checked for it.
"""

from __future__ import annotations

import copy
import json

import pytest
import yaml

from negsim.avoidance.directives import PLAIN_ORCA
from negsim.rules import RuleDatabase, RuleError
from negsim.rules.canonical import canonical_hash
from negsim.rules.database import RULE_DB_ROOT, file_sha256, load_validator, read_rule_file, schema_path
from negsim.rules.jsonschema_subset import unsupported_keywords
from negsim.rules.model import parse_rule
from negsim.rules.snapshot import PairSnapshot

SCHEMAS = load_validator(RULE_DB_ROOT)
SEED = RULE_DB_ROOT / "rules" / "passage_shorter_backs_out.v1.yaml"


def seed() -> dict:
    return yaml.safe_load(SEED.read_text(encoding="utf-8"))


def with_directive(directive, roles=None, version=3) -> dict:
    raw = seed()
    raw["schema_version"] = version
    raw["directive"] = directive
    if roles is not None:
        raw["roles"] = roles
    return raw


def refused(raw) -> RuleError:
    with pytest.raises(RuleError) as error:
        parse_rule(raw, SCHEMAS, "test")
    return error.value


def snapshot(encounter="single_file_segment", inside=(True, True), travelled=(1.0, 2.0)) -> PairSnapshot:
    values = tuple({"in_segment": inside[k], "segment_distance_travelled": travelled[k]} for k in (0, 1))
    return PairSnapshot(0, 0.0, (0, 1), {"encounter_class": encounter}, values)


# --- the schema --------------------------------------------------------------------------------------


def test_version_3_is_frozen_and_is_version_2_with_back_up_and_true_or_false():
    manifest = json.loads((RULE_DB_ROOT / "MANIFEST.json").read_text(encoding="utf-8"))["files"]
    assert manifest[schema_path(3)]["sha256"] == file_sha256(RULE_DB_ROOT / schema_path(3))
    two = json.loads((RULE_DB_ROOT / schema_path(2)).read_text(encoding="utf-8"))
    three = json.loads((RULE_DB_ROOT / schema_path(3)).read_text(encoding="utf-8"))
    assert unsupported_keywords(three) == set()
    # Everything else is version 2's, word for word.
    expected = copy.deepcopy(two)
    for key in ("$id", "title", "description"):
        expected[key] = three[key]
    expected["properties"]["schema_version"] = {"const": 3}
    expected["$defs"]["scalar"] = {"type": ["number", "string", "boolean"]}
    expected["$defs"]["directive"]["properties"]["back_up"] = {"type": "boolean"}
    assert three == expected


def test_versions_1_and_2_can_use_nothing_version_3_added():
    error = refused(with_directive({"backs_out": {"back_up": True}, "goes_on": {}}, version=2))
    assert error.category == "schema" and "unknown property 'back_up'" in str(error)
    raw = with_directive({"backs_out": {"passage_order": "follower"}, "goes_on": {"passage_order": "leader"}}, version=2)
    error = refused(raw)  # its condition compares with true: no boolean value in version 2
    assert error.category == "schema"
    raw["when"] = {"all": []}
    error = refused(raw)  # and it orders the two on a passage field
    assert error.category == "unknown_field" and "added in version 3" in str(error)


def test_true_or_false_is_compared_for_equality_only_and_takes_no_unit():
    base = with_directive({"backs_out": {"back_up": True}, "goes_on": {}})
    for comparison, category in (
        ({"field": "both.in_segment", "op": "<", "value": True}, "operator"),
        ({"field": "both.in_segment", "op": "==", "value": True, "unit": "m"}, "unit"),
        ({"field": "both.in_segment", "op": "==", "value": 1}, "value"),
        ({"field": "agent.in_segment", "op": "==", "value": True}, "unknown_field"),  # agent. orders, it does not compare
    ):
        raw = copy.deepcopy(base)
        raw["when"] = {"all": [comparison]}
        assert refused(raw).category == category, comparison
    raw = copy.deepcopy(base)
    raw["roles"]["by"]["field"] = "agent.in_segment"
    raw["roles"]["by"].pop("unit")
    raw["roles"]["by"].pop("tie_within")
    error = refused(raw)
    assert error.category == "operator" and "true or false" in str(error)
    for value in (True, False, [True]):
        raw = copy.deepcopy(base)
        raw["when"] = {"all": [{"field": "either.in_segment", "op": "in" if isinstance(value, list) else "!=", "value": value}]}
        parse_rule(raw, SCHEMAS, "test")


# --- the consistency check ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "directive, message",
    [
        ({"backs_out": {"back_up": True}, "goes_on": {"back_up": True}}, "both back up"),
        ({"backs_out": {"back_up": False}, "goes_on": {"back_up": False}}, "both go on"),
        ({"backs_out": {"back_up": False}, "goes_on": {}}, "both go on"),  # saying false for one is saying it
        ({"backs_out": {"back_up": True, "passage_order": "leader"}, "goes_on": {"passage_order": "follower"}}, "backs up and goes first"),
    ],
)
def test_a_rule_that_says_who_backs_up_must_make_exactly_one_role_back_up(directive, message):
    error = refused(with_directive(directive))
    assert error.category == "back_up" and message in str(error)


@pytest.mark.parametrize("value", [True, False])
def test_a_symmetric_rule_cannot_say_who_backs_up(value):
    raw = with_directive({"both": {"back_up": value}}, roles="symmetric")
    error = refused(raw)
    assert error.category == "back_up" and "exactly one of two roles" in str(error)


@pytest.mark.parametrize(
    "directive",
    [
        {"backs_out": {"back_up": True}, "goes_on": {}},
        {"backs_out": {"back_up": True}, "goes_on": {"back_up": False}},
        {"backs_out": {"back_up": True, "passage_order": "follower"}, "goes_on": {"passage_order": "leader"}},
        {"backs_out": {"passage_order": "follower"}, "goes_on": {"passage_order": "leader"}},  # says nothing of backing up
        {"backs_out": {"responsibility_share": 1.0}, "goes_on": {}},
    ],
)
def test_rules_that_back_up_exactly_one_role_or_say_nothing_of_it_load(directive):
    rule = parse_rule(with_directive(directive), SCHEMAS, "test")
    assert [rule.directives[name].back_up for name in ("backs_out", "goes_on")] == [
        directive["backs_out"].get("back_up", False), directive["goes_on"].get("back_up", False),
    ]


PASSAGE_FIELDS = ("in_segment", "segment_distance_travelled", "segment_distance_ahead", "segment_distance_behind")


@pytest.mark.parametrize("name", PASSAGE_FIELDS)
def test_the_loaders_observability_check_accepts_every_passage_field_under_every_prefix(name):
    """Part 2.3: the passage fields are computed from what both agents see, so the loader, which
    refuses a field that either cannot see (``unobservable_field``), accepts them: in a condition
    as ``either.`` and ``both.``, and in a role assignment as ``agent.``."""
    value, unit = (True, None) if name == "in_segment" else (1.0, "m")
    for prefix in ("either", "both"):
        raw = seed()
        comparison = {"field": f"{prefix}.{name}", "op": "==" if unit is None else ">", "value": value}
        if unit is not None:
            comparison["unit"] = unit
        raw["when"] = {"all": [comparison]}
        rule = parse_rule(raw, SCHEMAS, "test")
        assert name in {ref.spec.name for ref in rule.field_refs()}, prefix
    if name != "in_segment":  # a true-or-false field cannot order the two
        raw = seed()
        raw["roles"]["by"]["field"] = f"agent.{name}"
        assert parse_rule(raw, SCHEMAS, "test").roles.ref.spec.name == name


def test_back_up_is_part_of_what_a_rule_is():
    """The canonical form (docs/rule-format.md, section 13) keeps it: a rule that backs one up is
    not the same rule as one that does not."""
    plain = with_directive({"backs_out": {"passage_order": "follower"}, "goes_on": {"passage_order": "leader"}})
    backing = with_directive({"backs_out": {"passage_order": "follower", "back_up": True}, "goes_on": {"passage_order": "leader"}})
    assert canonical_hash(plain) != canonical_hash(backing)


# --- the seed rule -----------------------------------------------------------------------------------


def test_the_seed_rule_is_a_version_3_test_seed_outside_the_default_set():
    rule = read_rule_file(SEED, SCHEMAS, RULE_DB_ROOT)
    assert (rule.rule_id, rule.version, rule.schema_version, rule.status) == ("passage_shorter_backs_out", 1, 3, "test_seed")
    assert "Not a claim about human behaviour" in rule.provenance["notes"]
    assert (rule.encounter, rule.priority, rule.expiry) == ("single_file_segment", 30, "out_of_range")
    assert rule.roles.ref.written == "agent.segment_distance_travelled" and rule.roles.order == "ascending"
    assert rule.roles.assign == ("backs_out", "goes_on") and (rule.roles.tie, rule.roles.tie_within) == ("no_match", 0.1)
    assert rule.directives["backs_out"].back_up is True and rule.directives["goes_on"] == PLAIN_ORCA
    database = RuleDatabase.load(RULE_DB_ROOT)
    assert "passage_shorter_backs_out" not in {rule.rule_id for rule in database.activate("default").rules}


def test_the_seed_rule_matches_two_people_both_inside_and_no_one_else():
    rule = read_rule_file(SEED, SCHEMAS, RULE_DB_ROOT)
    match = rule.match(snapshot())
    assert match.roles == ("backs_out", "goes_on") and match.directive_of(0).back_up and not match.directive_of(1).back_up
    assert rule.match(snapshot(travelled=(2.5, 0.4))).roles == ("goes_on", "backs_out")
    assert rule.match(snapshot(travelled=(1.0, 1.08))) is None  # within 0.1 m: a tie, no_match
    assert rule.match(snapshot(inside=(True, False), travelled=(1.0, None))) is None  # one is outside
    # A missing value (the fields are null outside the single-file class, or hidden) never matches.
    assert rule.match(snapshot(inside=(None, None), travelled=(None, None))) is None
    assert rule.match(snapshot(encounter="head_on")) is None
