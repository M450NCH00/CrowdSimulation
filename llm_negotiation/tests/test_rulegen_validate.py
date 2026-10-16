"""Issue #30, Part 7: every proposed rule gets exactly one category, and none is discarded."""

from __future__ import annotations

import pytest

from negsim.avoidance.perception import default_visibility
from negsim.rulegen.validate import (
    CATEGORIES,
    FORMAT_LIMIT,
    INCONSISTENT,
    NEEDS_COMMUNICATION,
    SCHEMA_ERROR,
    VALID,
    is_formula,
    review_flags,
    validate_proposal,
)

SEE_ALL = default_visibility()
HIDDEN = {**SEE_ALL, "age": False, "gender": False}
KEEP_ROOM = {"encounter": "any", "when": {"all": []}, "roles": "symmetric", "directive": {"both": {"clearance_margin": 0.15}}, "priority": 100}
BY_SPEED = {"by": {"field": "agent.speed_mps", "order": "descending", "assign": ["faster", "slower"], "tie": "no_match"}}


def rule(**changes):
    return {**KEEP_ROOM, **changes}


def when(*comparisons):
    return {"all": list(comparisons)}


def by(**changes):
    return {"by": {**BY_SPEED["by"], **changes}}


VALID_RULES = {
    "symmetric, no condition": rule(),
    "a condition with its unit": rule(when=when({"field": "pair.distance_m", "op": "<", "value": 6, "unit": "m"})),
    "roles by speed": rule(roles=BY_SPEED, directive={"faster": {"responsibility_share": 1.0}, "slower": {"responsibility_share": 0.0}}),
    "a passage order": rule(encounter="single_file_segment", roles=by(field="agent.time_to_segment_s", order="ascending", assign=["near", "far"]), directive={"near": {"passage_order": "leader"}, "far": {"passage_order": "follower"}}),
    "age, seen": rule(when=when({"field": "pair.age_difference_years", "op": ">", "value": 20, "unit": "years"})),
}

# category, the loader's or the check's reason, the rule, the session's visibility
CASES = {
    "an errand, which no one can see": (NEEDS_COMMUNICATION, "unobservable_field", rule(when=when({"field": "either.task", "op": "==", "value": "the emergency room"})), SEE_ALL),
    "one person's own point of view": (NEEDS_COMMUNICATION, "unobservable_field", rule(when=when({"field": "self.speed_mps", "op": ">", "value": 1, "unit": "m/s"})), SEE_ALL),
    "a field named for private information": (NEEDS_COMMUNICATION, "private_information", rule(when=when({"field": "either.urgency", "op": "==", "value": "high"})), SEE_ALL),
    "age, hidden in the session": (NEEDS_COMMUNICATION, "hidden_in_session", rule(when=when({"field": "pair.age_difference_years", "op": ">", "value": 20, "unit": "years"})), HIDDEN),
    "roles by age, hidden": (NEEDS_COMMUNICATION, "hidden_in_session", rule(roles=by(field="agent.age"), directive={"faster": {}, "slower": {}}), HIDDEN),
    "shares that sum below 1": (INCONSISTENT, "reciprocity", rule(directive={"both": {"responsibility_share": 0.3}}), SEE_ALL),
    "opposite sides": (INCONSISTENT, "side", rule(roles=BY_SPEED, directive={"faster": {"side_preference": "left"}, "slower": {"side_preference": "right"}}), SEE_ALL),
    "two leaders": (INCONSISTENT, "passage_order", rule(directive={"both": {"passage_order": "leader"}}), SEE_ALL),
    "a key the format does not have": (SCHEMA_ERROR, "schema", rule(name="keep room"), SEE_ALL),
    "a number written as text": (SCHEMA_ERROR, "schema", rule(directive={"both": {"clearance_margin": "0.15"}}), SEE_ALL),
    "arithmetic on numbers only": (SCHEMA_ERROR, "schema", rule(directive={"both": {"responsibility_share": "1/2"}}), SEE_ALL),
    "no tie policy": (SCHEMA_ERROR, "no_tie_policy", rule(roles={"by": {k: v for k, v in BY_SPEED["by"].items() if k != "tie"}}, directive={"faster": {}, "slower": {}}), SEE_ALL),
    "roles that do not fit the directive": (SCHEMA_ERROR, "roles", rule(roles=BY_SPEED), SEE_ALL),
    "a field that does not exist": (SCHEMA_ERROR, "unknown_field", rule(when=when({"field": "pair.colour", "op": "==", "value": "red"})), SEE_ALL),
    "a number without its unit": (SCHEMA_ERROR, "unit", rule(when=when({"field": "pair.distance_m", "op": "<", "value": 6})), SEE_ALL),
    "an intent too long": (SCHEMA_ERROR, "schema", rule(intent="x" * 501), SEE_ALL),
    "three roles": (FORMAT_LIMIT, None, rule(directive={"a": {}, "b": {}, "c": {}}), SEE_ALL),
    "three roles assigned": (FORMAT_LIMIT, None, rule(roles=by(assign=["a", "b", "c"]), directive={"a": {}, "b": {}}), SEE_ALL),
    "a share that grows with the age gap": (FORMAT_LIMIT, None, rule(directive={"both": {"responsibility_share": "0.5 + 0.01 * pair.age_difference_years"}}), SEE_ALL),
    "a threshold that scales with speed": (FORMAT_LIMIT, None, rule(when=when({"field": "pair.distance_m", "op": "<", "value": "2 * agent.speed_mps", "unit": "m"})), SEE_ALL),
    "a side that depends on age": (FORMAT_LIMIT, None, rule(directive={"both": {"side_preference": "left if older"}}), SEE_ALL),
    "a field written as a formula": (FORMAT_LIMIT, None, rule(when=when({"field": "pair.distance_m * 2", "op": "<", "value": 6, "unit": "m"})), SEE_ALL),
    "a tie that scales": (FORMAT_LIMIT, None, rule(roles=by(tie_within="0.05 times the faster speed"), directive={"faster": {}, "slower": {}}), SEE_ALL),
    "roles by gender": (FORMAT_LIMIT, None, rule(roles=by(field="agent.gender"), directive={"faster": {}, "slower": {}}), SEE_ALL),
}


@pytest.mark.parametrize("name", sorted(VALID_RULES))
def test_a_rule_the_format_can_hold_and_both_can_see_is_valid(name):
    result = validate_proposal(VALID_RULES[name], SEE_ALL)
    assert (result.category, result.loader_category) == (VALID, None), result.message


@pytest.mark.parametrize("name", sorted(CASES))
def test_every_category(name):
    category, reason, proposal, visibility = CASES[name]
    result = validate_proposal(proposal, visibility)
    assert (result.category, result.loader_category) == (category, reason), result.message
    assert result.message


def test_every_category_is_exercised():
    assert {category for category, *_ in CASES.values()} | {VALID} == set(CATEGORIES)


def test_the_order_of_precedence():
    private_and_three_roles = rule(when=when({"field": "either.task", "op": "==", "value": "x"}), directive={"a": {}, "b": {}, "c": {}})
    assert validate_proposal(private_and_three_roles, SEE_ALL).category == NEEDS_COMMUNICATION
    three_roles_and_unknown_key = rule(directive={"a": {}, "b": {}, "c": {}}, colour="red")
    assert validate_proposal(three_roles_and_unknown_key, SEE_ALL).category == FORMAT_LIMIT


def test_what_a_model_writes_in_the_writers_keys_is_ignored_and_kept_as_data():
    written = rule(rule_id="my_own_id", version=7, status="validated", provenance={"source_type": "hand_written"}, screening=[{"kind": "crowd"}])
    result = validate_proposal(written, SEE_ALL)
    assert result.category == VALID
    assert result.ignored_metadata == {"rule_id": "my_own_id", "version": 7, "status": "validated", "provenance": {"source_type": "hand_written"}, "screening": [{"kind": "crowd"}]}


def test_not_a_rule_at_all():
    for proposal in ("keep to the left", ["a"], 3):
        result = validate_proposal(proposal, SEE_ALL)
        assert (result.category, result.loader_category) == (SCHEMA_ERROR, "schema")


def test_the_fields_a_proposal_reads_are_recorded():
    result = validate_proposal(VALID_RULES["roles by speed"], SEE_ALL)
    assert result.fields == ["agent.speed_mps"]


@pytest.mark.parametrize(
    "text, formula",
    [
        ("0.5 + 0.01 * pair.age_difference_years", True), ("2 * speed", True), ("left if older", True), ("0.6 per year", True),
        ("1 - age/100", True), ("1/2", False), ("0.5 m", False), ("0.3 m/s", False), ("-0.5", False), ("0.5e-3", False),
        ("0.5-0.1", False), ("leader", False),
    ],
)
def test_what_counts_as_a_formula(text, formula):
    assert is_formula(text) is formula


def test_manual_review_flags_read_words_and_never_change_the_category():
    assert review_flags(["The faster one does the avoiding."]) == []  # a role, not a scaling
    assert review_flags(["Their share grows with the age gap."]) == ["scaling"]
    assert review_flags(["The older they are, the more they should give way."]) == ["the_more_the_more"]
    assert review_flags(["0.01 per year of age difference"]) == ["rate"]
    assert review_flags(["When a group of three people meets one"]) == ["more_than_two_people"]
    result = validate_proposal(rule(intent="The share grows with the age gap."), SEE_ALL, ["I agree."])
    assert result.category == VALID and result.review_flags == ["scaling"]
    result = validate_proposal(rule(directive={"both": {"clearance_margin": "0.1 per year"}}), SEE_ALL)
    assert result.category == FORMAT_LIMIT and result.review_flags == ["rate"]
