"""Issue #30, Part 7: every proposed rule gets exactly one category, and none is discarded. Issue
#32: a rule that reads a group is a category of its own, and what a later version of the rule
format added is a format limit of the version a session was shown."""

from __future__ import annotations

import pytest

from negsim.avoidance.perception import default_visibility
from negsim.rulegen.validate import (
    CATEGORIES,
    FORMAT_LIMIT,
    INCONSISTENT,
    NEEDS_COMMUNICATION,
    PROTECTED_ATTRIBUTE,
    SCHEMA_ERROR,
    VALID,
    is_formula,
    review_flags,
    session_terms,
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
    "a person's group, which no rule may read": (PROTECTED_ATTRIBUTE, "protected_attribute", rule(when=when({"field": "either.ethnic_group", "op": "==", "value": "Kestrop"})), SEE_ALL),
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


# --- issue #32: a person's group, backing up, and a later version of the format ---------------------

BACK_UP = {
    "encounter": "single_file_segment",
    "when": {"all": [{"field": "both.in_segment", "op": "==", "value": True}]},
    "roles": {"by": {"field": "agent.segment_distance_travelled", "order": "ascending", "assign": ["backer", "goer"], "tie": "no_match", "tie_within": 0.1, "unit": "m"}},
    "directive": {"backer": {"back_up": True}, "goer": {}},
    "priority": 100,
}


def test_a_rule_that_reads_a_group_is_protected_whatever_else_is_wrong_with_it():
    everything_wrong = rule(
        when=when({"field": "either.ethnic_group", "op": "==", "value": "x"}, {"field": "either.task", "op": "==", "value": "y"}),
        directive={"a": {}, "b": {}, "c": {}},
    )
    result = validate_proposal(everything_wrong, SEE_ALL)
    assert (result.category, result.loader_category) == (PROTECTED_ATTRIBUTE, "protected_attribute") and result.message
    by_label = rule(roles=by(assign=["kestrop", "other"]), directive={"kestrop": {}, "other": {}})
    as_a_value = rule(when=when({"field": "either.gender", "op": "==", "value": "Pellund"}))
    for proposal in (by_label, as_a_value):
        assert validate_proposal(proposal, SEE_ALL, schema_version=3).category == PROTECTED_ATTRIBUTE


def test_the_words_a_session_introduced_its_groups_with_are_protected_only_if_it_showed_them():
    shown = {"visibility": {"ethnic_group": True}, "framing": "community", "personas": {"0": {"ethnic_group": "Brannoq"}, "1": {"ethnic_group": "Kestrop"}}}
    assert session_terms(shown) == ("Brannoq", "Kestrop", "community")
    assert session_terms({**shown, "visibility": {"ethnic_group": False}}) == () and session_terms({"visibility": {}, "personas": {}}) == ()
    naming = rule(when=when({"field": "either.gender", "op": "==", "value": "Brannoq"}))
    assert validate_proposal(naming, SEE_ALL, terms=session_terms(shown)).category == PROTECTED_ATTRIBUTE
    assert validate_proposal(naming, SEE_ALL).category == SCHEMA_ERROR  # not a default label, and not shown: a wrong value
    roles = rule(roles=by(assign=["community_first", "other"]), directive={"community_first": {}, "other": {}})
    assert validate_proposal(roles, SEE_ALL, terms=session_terms(shown)).category == PROTECTED_ATTRIBUTE


def test_what_a_later_version_of_the_format_added_is_a_format_limit_of_an_earlier_one():
    """A session shown rule format 2 (issue #30's prompts) had no back_up and no passage fields: a
    rule that needs them is one its format could not express. Shown format 3, it is valid."""
    for version, category in ((2, FORMAT_LIMIT), (3, VALID)):
        result = validate_proposal(BACK_UP, SEE_ALL, schema_version=version)
        assert result.category == category, result.message
    assert "has no back_up" in validate_proposal(BACK_UP, SEE_ALL, schema_version=2).message
    ordering_only = {**BACK_UP, "when": {"all": []}, "directive": {"backer": {"passage_order": "follower"}, "goer": {"passage_order": "leader"}}}
    result = validate_proposal(ordering_only, SEE_ALL, schema_version=2)
    assert result.category == FORMAT_LIMIT and "segment_distance_travelled" in result.message
    assert validate_proposal(ordering_only, SEE_ALL, schema_version=3).category == VALID


def test_a_rule_that_backs_up_both_or_says_so_of_both_at_once_is_inconsistent():
    both = {**BACK_UP, "directive": {"backer": {"back_up": True}, "goer": {"back_up": True}}}
    result = validate_proposal(both, SEE_ALL, schema_version=3)
    assert (result.category, result.loader_category) == (INCONSISTENT, "back_up")
    symmetric = rule(encounter="single_file_segment", directive={"both": {"back_up": True}})
    assert validate_proposal(symmetric, SEE_ALL, schema_version=3).category == INCONSISTENT
    as_words = {**BACK_UP, "directive": {"backer": {"back_up": "if it has walked less far in"}, "goer": {}}}
    assert validate_proposal(as_words, SEE_ALL, schema_version=3).category == FORMAT_LIMIT
