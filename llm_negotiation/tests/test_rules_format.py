"""The rule format (issue #28, Part 2): the schema, the fields a rule may read, units, every
operator and group, role assignment and its tie policy, the consistency checks, and the
fixtures. Nothing here runs a simulation."""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import pytest
import yaml

from negsim.avoidance.directives import AvoidanceDirective
from negsim.configutil import PACKAGE_ROOT
from negsim.rules.conditions import OPERATORS, compare, parse_condition
from negsim.rules.database import RULE_DB_ROOT, SCHEMA_PATH, load_validator, read_rule_file
from negsim.rules.errors import CATEGORIES, RuleError
from negsim.rules.fields import AGENT_FIELDS, PAIR_FIELDS, UNITS, UNOBSERVABLE, resolve
from negsim.rules.jsonschema_subset import Validator, json_equal, unsupported_keywords
from negsim.rules.model import parse_rule
from negsim.rules.snapshot import PairSnapshot

FIXTURES = PACKAGE_ROOT / "tests" / "fixtures" / "rules"
VALIDATOR = load_validator(RULE_DB_ROOT)
SCHEMA = json.loads((RULE_DB_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))


def snapshot(pair=None, first=None, second=None, encounter="head_on"):
    """A hand-built snapshot: agents 0 and 1, with only the values given."""
    return PairSnapshot(0, 0.0, (0, 1), {"encounter_class": encounter, **(pair or {})}, (first or {}, second or {}))


def rule(**changes):
    """A small valid rule as written, with ``changes`` laid on top."""
    raw = {
        "schema_version": 1,
        "rule_id": "test_rule",
        "version": 1,
        "status": "test_seed",
        "provenance": {
            "source_type": "hand_written",
            "source_ref": "test",
            "created_at": "2026-10-14",
            "author": "test",
            "notes": "",
            "validation_evidence": [],
        },
        "encounter": "head_on",
        "when": {"all": []},
        "roles": "symmetric",
        "directive": {"both": {"side_preference": "left"}},
        "priority": 10,
    }
    raw.update(changes)
    return parse_rule(raw, VALIDATOR, "test")


# --- the JSON Schema and its validator ---------------------------------------------------------


def test_the_schema_uses_only_keywords_the_validator_implements():
    assert unsupported_keywords(SCHEMA) == set()
    with pytest.raises(ValueError, match="does not implement"):
        Validator({"type": "object", "dependentRequired": {}})


def test_the_validator_reports_where_and_what():
    errors = Validator(SCHEMA).errors({"schema_version": 2, "rule_id": "X"})
    assert any("$.schema_version: must be 1" in error for error in errors)
    assert any("$.rule_id" in error and "pattern" in error for error in errors)
    assert any("missing required property 'when'" in error for error in errors)


def test_json_equality_tells_true_from_one():
    assert json_equal(1, 1.0) and not json_equal(True, 1) and not json_equal(0, False)
    assert json_equal({"a": [1, 2.0]}, {"a": [1.0, 2]}) and not json_equal([1], [1, 1])


def test_every_seed_rule_fits_the_schema_and_the_format():
    for path in sorted((RULE_DB_ROOT / "rules").glob("*.yaml")):
        loaded = read_rule_file(path, VALIDATOR, RULE_DB_ROOT)
        assert loaded.status == "test_seed" and loaded.provenance["validation_evidence"] == []
        assert "Not a claim about human behaviour" in loaded.provenance["notes"]


# --- the fixtures ----------------------------------------------------------------------------------


@pytest.mark.parametrize("path", sorted((FIXTURES / "valid").glob("*.yaml")), ids=lambda path: path.stem)
def test_the_valid_fixtures_load(path):
    read_rule_file(path, VALIDATOR)


@pytest.mark.parametrize("path", sorted((FIXTURES / "invalid").glob("*.yaml")), ids=lambda path: path.stem)
def test_each_invalid_fixture_is_refused_for_its_reason(path):
    expected = path.read_text(encoding="utf-8").splitlines()[0].removeprefix("# expect: ").strip()
    assert expected in CATEGORIES
    with pytest.raises(RuleError) as caught:
        read_rule_file(path, VALIDATOR)
    assert caught.value.category == expected, str(caught.value)


def test_the_fixtures_the_issue_asks_for_are_there():
    names = {path.stem.split(".")[0] for path in FIXTURES.rglob("*.yaml")}
    assert {"gender_keeps_clear_crossing", "reads_the_task", "shares_short_of_one", "unknown_field", "no_tie_policy"} <= names
    assert {"clash_side", "clash_clearance"} <= names
    assert not list(RULE_DB_ROOT.rglob("*fixture*")) and not (RULE_DB_ROOT / "rules" / "gender_keeps_clear_crossing.v1.yaml").exists()


def test_a_gender_condition_reads_the_gender_of_either_agent():
    loaded = read_rule_file(FIXTURES / "valid" / "gender_keeps_clear_crossing.v1.yaml", VALIDATOR)
    close = {"time_to_collision_s": 3.0}
    assert loaded.match(snapshot(close, {"gender": "male"}, {"gender": "female"}, "crossing"))
    assert not loaded.match(snapshot(close, {"gender": "male"}, {"gender": "male"}, "crossing"))
    assert not loaded.match(snapshot(close, {"gender": None}, {"gender": None}, "crossing"))  # hidden


# --- fields and units -------------------------------------------------------------------------------


def test_the_field_list_is_what_both_agents_can_see():
    assert set(PAIR_FIELDS) == {
        "encounter_class", "distance_m", "closing_speed_mps", "time_to_collision_s", "heading_difference_rad",
        "min_corridor_width_m", "age_difference_years",
    }
    assert set(AGENT_FIELDS) == {"age", "gender", "speed_mps", "radius_m", "time_to_segment_s"}
    assert "task" in UNOBSERVABLE and not set(UNOBSERVABLE) & (set(PAIR_FIELDS) | set(AGENT_FIELDS))


@pytest.mark.parametrize(
    "reference, prefixes, category",
    [
        ("either.task", ("pair", "either", "both"), "unobservable_field"),
        ("agent.task", ("agent",), "unobservable_field"),
        ("pair.free_width_m", ("pair",), "unobservable_field"),
        ("pair.bearing_rad", ("pair",), "unobservable_field"),
        ("either.preferred_speed_mps", ("either",), "unobservable_field"),
        ("observer.age", ("pair", "either", "both"), "unobservable_field"),
        ("neighbour.speed_mps", ("pair", "either", "both"), "unobservable_field"),
        ("pair.mood", ("pair",), "unknown_field"),
        ("age", ("pair", "either", "both"), "unknown_field"),
        ("agent.age", ("pair", "either", "both"), "unknown_field"),  # agent. only in a role assignment
        ("pair.age", ("pair",), "unknown_field"),  # age is an agent's, not the pair's
    ],
)
def test_a_field_that_cannot_be_read_is_refused_with_its_reason(reference, prefixes, category):
    with pytest.raises(RuleError) as caught:
        resolve(reference, "test", prefixes)
    assert caught.value.category == category


@pytest.mark.parametrize("unit, value, expected", [("rad", math.pi, math.pi), ("deg", 180, math.pi), ("deg", 90.0, math.pi / 2)])
def test_angles_may_be_written_in_degrees(unit, value, expected):
    condition = parse_condition({"field": "pair.heading_difference_rad", "op": ">=", "value": value, "unit": unit}, "t")
    assert condition.value == pytest.approx(expected)


@pytest.mark.parametrize(
    "field, unit", [("pair.distance_m", "m"), ("pair.time_to_collision_s", "s"), ("pair.closing_speed_mps", "m/s"),
                    ("pair.heading_difference_rad", "rad"), ("pair.age_difference_years", "years")],
)
def test_every_unit_is_accepted_for_its_own_field_and_refused_for_another(field, unit):
    assert parse_condition({"field": field, "op": "<", "value": 1, "unit": unit}, "t").value == 1.0
    for other in UNITS:
        if UNITS[other][0] != UNITS[unit][0]:
            with pytest.raises(RuleError) as caught:
                parse_condition({"field": field, "op": "<", "value": 1, "unit": other}, "t")
            assert caught.value.category == "unit"


def test_a_category_takes_no_unit_and_a_number_must_have_one():
    with pytest.raises(RuleError, match="takes no unit"):
        parse_condition({"field": "pair.encounter_class", "op": "==", "value": "head_on", "unit": "m"}, "t")
    with pytest.raises(RuleError, match="must state its unit"):
        parse_condition({"field": "pair.distance_m", "op": "<", "value": 5}, "t")


# --- operators and groups ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "op, value, results",
    [  # results for the actual values 4, 5 and 6 against 5
        ("<", 5, (True, False, False)),
        ("<=", 5, (True, True, False)),
        (">", 5, (False, False, True)),
        (">=", 5, (False, True, True)),
        ("==", 5, (False, True, False)),
        ("!=", 5, (True, False, True)),
        ("in", [4, 6], (True, False, True)),
    ],
)
def test_every_operator_on_a_number(op, value, results):
    condition = parse_condition({"field": "pair.distance_m", "op": op, "value": value, "unit": "m"}, "t")
    assert tuple(condition.evaluate(snapshot({"distance_m": actual})) for actual in (4.0, 5.0, 6.0)) == results
    assert OPERATORS == ("<", "<=", ">", ">=", "==", "!=", "in")


@pytest.mark.parametrize("op", ["<", "<=", ">", ">=", "==", "!=", "in"])
def test_a_comparison_on_a_missing_value_is_false_whatever_the_operator(op):
    value = [5] if op == "in" else 5
    condition = parse_condition({"field": "pair.time_to_collision_s", "op": op, "value": value, "unit": "s"}, "t")
    assert condition.evaluate(snapshot({"time_to_collision_s": None})) is False
    assert compare(None, op, value) is False


def test_categories_compare_with_equals_not_equals_and_in():
    on = lambda raw, encounter: parse_condition(raw, "t").evaluate(snapshot(encounter=encounter))  # noqa: E731
    assert on({"field": "pair.encounter_class", "op": "==", "value": "crossing"}, "crossing")
    assert on({"field": "pair.encounter_class", "op": "!=", "value": "crossing"}, "head_on")
    assert on({"field": "pair.encounter_class", "op": "in", "value": ["overtaking", "crossing"]}, "crossing")
    assert not on({"field": "pair.encounter_class", "op": "in", "value": ["overtaking"]}, "crossing")
    with pytest.raises(RuleError) as caught:
        parse_condition({"field": "pair.encounter_class", "op": "==", "value": "sideways"}, "t")
    assert caught.value.category == "value"


def test_either_and_both_quantify_over_the_two_agents():
    either = parse_condition({"field": "either.age", "op": ">=", "value": 60, "unit": "years"}, "t")
    both = parse_condition({"field": "both.age", "op": ">=", "value": 60, "unit": "years"}, "t")
    for ages, expected in (((70, 20), (True, False)), ((70, 65), (True, True)), ((20, 30), (False, False)), ((70, None), (True, False))):
        situation = snapshot(first={"age": ages[0]}, second={"age": ages[1]})
        assert (either.evaluate(situation), both.evaluate(situation)) == expected, ages


def test_groups_nest_and_an_empty_all_is_true():
    assert parse_condition({"all": []}, "t").evaluate(snapshot())
    nested = parse_condition(
        {"all": [
            {"field": "pair.distance_m", "op": "<", "value": 10, "unit": "m"},
            {"any": [
                {"field": "pair.time_to_collision_s", "op": "<", "value": 2, "unit": "s"},
                {"field": "both.speed_mps", "op": ">", "value": 1.0, "unit": "m/s"},
            ]},
        ]},
        "t",
    )
    fast = {"speed_mps": 1.3}
    assert nested.evaluate(snapshot({"distance_m": 5, "time_to_collision_s": 9}, fast, fast))
    assert nested.evaluate(snapshot({"distance_m": 5, "time_to_collision_s": 1}, {"speed_mps": 0.2}, fast))
    assert not nested.evaluate(snapshot({"distance_m": 5, "time_to_collision_s": 9}, {"speed_mps": 0.2}, fast))
    assert not nested.evaluate(snapshot({"distance_m": 50, "time_to_collision_s": 1}, fast, fast))
    with pytest.raises(RuleError, match="at least one item"):
        parse_condition({"any": []}, "t")


def test_the_fixture_with_every_operator_matches_exactly_when_it_should():
    loaded = read_rule_file(FIXTURES / "valid" / "every_operator.v1.yaml", VALIDATOR)
    pair = {"distance_m": 8.0, "time_to_collision_s": 4.0, "closing_speed_mps": 2.0, "heading_difference_rad": math.pi,
            "age_difference_years": 10, "min_corridor_width_m": 1.75}
    big, small = {"radius_m": 0.30, "age": 30, "speed_mps": 1.0}, {"radius_m": 0.25, "age": 40, "speed_mps": 1.0}
    found = loaded.match(snapshot(pair, big, small))
    assert found and found.roles == ("larger", "smaller") and found.directives[1].side_preference == "right"
    assert loaded.match(snapshot(pair, small, big)).roles == ("smaller", "larger")
    assert loaded.match(snapshot({**pair, "heading_difference_rad": math.radians(149)}, big, small)) is None
    assert loaded.match(snapshot({**pair, "min_corridor_width_m": 2.0}, big, small)) is None  # no branch of the any
    assert loaded.match(snapshot(pair, big, {**small, "radius_m": 0.295})) is None  # within the 1 cm tie tolerance
    assert loaded.match(snapshot(pair, big, small, "overtaking")) is None  # pair.encounter_class in [head_on, crossing]


# --- roles, directives and the consistency checks -------------------------------------------------------


def test_roles_follow_the_order_and_a_tie_is_no_match():
    younger = rule(
        roles={"by": {"field": "agent.age", "order": "ascending", "assign": ["yielder", "other"], "tie": "no_match"}},
        directive={"yielder": {"responsibility_share": 1.0}, "other": {"responsibility_share": 0.0}},
    )
    assert younger.match(snapshot(first={"age": 25}, second={"age": 70})).roles == ("yielder", "other")
    assert younger.match(snapshot(first={"age": 70}, second={"age": 25})).roles == ("other", "yielder")
    assert younger.match(snapshot(first={"age": 40}, second={"age": 40})) is None
    assert younger.match(snapshot(first={"age": 40}, second={"age": None})) is None  # cannot be ordered


def test_fields_a_rule_leaves_out_take_their_baseline_values():
    loaded = rule(directive={"both": {"clearance_margin": 0.2}})
    assert loaded.directives["both"] == AvoidanceDirective(clearance_margin=0.2)
    assert loaded.set_fields["both"] == ("clearance_margin",)


@pytest.mark.parametrize(
    "directive, category",
    [
        ({"a": {"responsibility_share": 0.4}, "b": {"responsibility_share": 0.5}}, "reciprocity"),
        ({"a": {"responsibility_share": 1.0}, "b": {}}, None),  # 1.0 + the baseline 0.5
        ({"a": {"responsibility_share": 0.0}, "b": {"responsibility_share": 1.0}}, None),
        ({"a": {"passage_order": "leader"}, "b": {"passage_order": "follower"}}, None),
        ({"a": {"passage_order": "leader"}, "b": {}}, "passage_order"),
        ({"a": {"passage_order": "follower"}, "b": {"passage_order": "follower"}}, "passage_order"),
        ({"a": {"side_preference": "left"}, "b": {"side_preference": "right"}}, "side"),
        ({"a": {"side_preference": "left"}, "b": {}}, None),
    ],
)
def test_the_consistency_checks_on_two_roles(directive, category):
    raw = dict(roles={"by": {"field": "agent.age", "order": "ascending", "assign": ["a", "b"], "tie": "no_match"}}, directive=directive)
    if category is None:
        rule(**raw)
        return
    with pytest.raises(RuleError) as caught:
        rule(**raw)
    assert caught.value.category == category


@pytest.mark.parametrize("share, ok", [(0.5, True), (0.6, True), (0.49, False), (0.0, False)])
def test_a_symmetric_rule_needs_a_share_of_at_least_one_half(share, ok):
    if ok:
        rule(directive={"both": {"responsibility_share": share}})
    else:
        with pytest.raises(RuleError, match="section 9"):
            rule(directive={"both": {"responsibility_share": share}})


def test_a_role_assignment_orders_numbers_only():
    with pytest.raises(RuleError) as caught:
        rule(roles={"by": {"field": "agent.gender", "order": "ascending", "assign": ["a", "b"], "tie": "no_match"}},
             directive={"a": {}, "b": {}})
    assert caught.value.category == "operator"


# --- no code is ever run --------------------------------------------------------------------------------


def test_nothing_in_the_rules_package_can_run_code_from_a_rule():
    """No eval, exec, compile or dynamic import anywhere in negsim/rules. (The one getattr,
    in matching.py, takes its names from a constant tuple in the code, never from a rule.)"""
    for path in sorted((PACKAGE_ROOT / "negsim" / "rules").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"eval", "exec", "compile", "__import__"}, (path.name, node.func.id)
            if isinstance(node, ast.Attribute):
                assert node.attr not in {"import_module", "literal_eval"}, (path.name, node.attr)


def test_text_that_looks_like_code_is_compared_and_never_run(tmp_path):
    with pytest.raises(RuleError) as caught:
        read_rule_file(FIXTURES / "invalid" / "code_as_a_value.v1.yaml", VALIDATOR)
    assert caught.value.category == "value"
    loaded = yaml.safe_load((FIXTURES / "invalid" / "code_as_a_value.v1.yaml").read_text(encoding="utf-8"))
    loaded["when"]["all"][0]["field"] = "pair.__class__"
    with pytest.raises(RuleError) as caught:
        parse_rule(loaded, VALIDATOR, "test")
    assert caught.value.category == "schema"  # the field-name pattern does not even admit it


def test_the_seed_rules_are_written_with_the_real_field_names():
    names = set(PAIR_FIELDS) | set(AGENT_FIELDS)
    directive_fields = set(AvoidanceDirective().as_dict())
    for path in sorted((RULE_DB_ROOT / "rules").glob("*.yaml")):
        loaded = read_rule_file(path, VALIDATOR, RULE_DB_ROOT)
        for ref in loaded.field_refs():
            assert ref.spec.name in names
        for written in loaded.written["directive"].values():
            assert set(written) <= directive_fields
    assert Path(RULE_DB_ROOT / SCHEMA_PATH).is_file()
