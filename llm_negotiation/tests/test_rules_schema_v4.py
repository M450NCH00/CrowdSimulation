"""Issue #108 (RF-31): version 4 of the rule format, beside versions 1 to 3.

Version 4 adds what one person can see of the other (``mobility_aid``, ``load``, ``distraction``),
roles by a condition, own-only conditions (``own_when`` on ``self.`` fields, switching on only the
person's own movement), and a plan of ``steps`` in Step 1's vocabulary (``docs/rule-format.md``,
section 15). Versions 1 to 3 load, match and are followed exactly as before (the rest of the suite);
here: each extension loads, matches and runs, in a head-on and in a crowd, and what it refuses.
"""

from __future__ import annotations

import copy
import json

import pytest

from helpers import crowd
from negsim.avoidance.perception import default_visibility, own_attributes
from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.rulegen import validate as V
from negsim.rulegen.replay import mixed_population, population_of
from negsim.rules import RuleDatabase, RuleError
from negsim.rules.ambiguity import find_clash
from negsim.rules.database import RULE_DB_ROOT, ActiveRuleSet, file_sha256, load_validator, schema_path
from negsim.rules.fields import AGENT_FIELDS, OWN_ATTRACTIVENESS, SELF_FIELDS, VISIBLE_FACTOR_SWITCHES, fields_of, resolve
from negsim.rules.jsonschema_subset import unsupported_keywords
from negsim.rules.model import ConditionRoles, parse_rule
from negsim.rules.provider import RuleDatabaseProvider
from negsim.rules.snapshot import PairSnapshot

SCHEMAS = load_validator(RULE_DB_ROOT)
PROVENANCE = {"source_type": "hand_written", "source_ref": "tests", "created_at": "2026-10-26", "author": "tests", "notes": "", "validation_evidence": []}
VISIBLE = {**default_visibility(), "mobility_aid": True, "load": True, "distraction": True}
SIDESTEP = [{"start": {"at_distance_m": 5}, "sidestep": {"to": "right", "metres": 0.6}, "speed_mps": 1.0}, {"speed_mps": 1.2, "until": "other_passes"}]


def written(**body) -> dict:
    raw = {
        "schema_version": 4, "rule_id": "aided_goes_on", "version": 1, "status": "test_seed", "provenance": PROVENANCE,
        "encounter": "head_on", "when": {"all": []},
        "roles": {"by_condition": {"when": {"field": "agent.mobility_aid", "op": "==", "value": "cane"}, "assign": ["aided", "gives_way"], "tie": "no_match"}},
        "directive": {"aided": {}, "gives_way": {"steps": copy.deepcopy(SIDESTEP)}},
        "priority": 50,
    }
    raw.update(body)
    return raw


def load(raw):
    return parse_rule(raw, SCHEMAS, "test")


def refused(raw) -> RuleError:
    with pytest.raises(RuleError) as error:
        load(raw)
    return error.value


def snap(agent=({}, {}), private=({}, {}), **pair) -> PairSnapshot:
    return PairSnapshot(0, 0.0, (0, 1), {"encounter_class": "head_on", **pair}, agent, private)


def own_when(field, value, then, op="=="):
    return {"when": {"field": field, "op": op, "value": value}, "then": then}


# --- the schema and the catalogue -----------------------------------------------------------------


def test_version_4_is_frozen_and_adds_only_its_four_extensions_to_version_3():
    manifest = json.loads((RULE_DB_ROOT / "MANIFEST.json").read_text(encoding="utf-8"))["files"]
    assert manifest[schema_path(4)]["sha256"] == file_sha256(RULE_DB_ROOT / schema_path(4))
    three = json.loads((RULE_DB_ROOT / schema_path(3)).read_text(encoding="utf-8"))
    four = json.loads((RULE_DB_ROOT / schema_path(4)).read_text(encoding="utf-8"))
    assert unsupported_keywords(four) == set()
    assert set(four["$defs"]) - set(three["$defs"]) == {"role_condition", "step", "steps", "own_movement", "own_when"}
    assert set(four["$defs"]["directive"]["properties"]) - set(three["$defs"]["directive"]["properties"]) == {"steps", "own_when"}
    for name in three["$defs"]:  # everything else is version 3's, unchanged
        if name != "directive":
            assert four["$defs"][name] == three["$defs"][name], name
    RuleDatabase.load(RULE_DB_ROOT)  # the database still loads, every seed rule as before


def test_the_three_visible_attributes_are_version_4_fields_under_their_own_switches():
    assert VISIBLE_FACTOR_SWITCHES == ("mobility_aid", "load", "distraction")
    for name in VISIBLE_FACTOR_SWITCHES:
        assert AGENT_FIELDS[name].since == 4 and AGENT_FIELDS[name].needs == (name,)
        assert name not in fields_of(3)[1]
    assert "mobility_aid" not in default_visibility()  # off unless a run names it


def test_a_version_3_rule_cannot_use_anything_version_4_added():
    assert refused(written(schema_version=3)).category == "schema"  # roles by a condition
    three = written(schema_version=3, roles="symmetric", directive={"both": {}})
    three["when"] = {"field": "either.mobility_aid", "op": "==", "value": "cane"}
    error = refused(three)
    assert error.category == "unknown_field" and "added in version 4" in str(error)
    three = written(schema_version=3, roles="symmetric", directive={"both": {"steps": SIDESTEP}})
    assert refused(three).category == "schema"


# --- roles by a condition ----------------------------------------------------------------------------


def test_roles_by_a_condition_give_the_first_role_to_the_one_it_holds_for():
    rule = load(written())
    assert isinstance(rule.roles, ConditionRoles) and rule.needs() >= {"mobility_aid"}
    match = rule.match(snap(({"mobility_aid": "none"}, {"mobility_aid": "cane"})))
    assert match.roles == ("gives_way", "aided")
    assert match.steps[0] is not None and match.steps[1] is None


@pytest.mark.parametrize("values", [("cane", "cane"), ("none", "none"), (None, None), (None, "none")])
def test_roles_by_a_condition_do_not_match_when_it_holds_for_both_or_neither(values):
    rule = load(written())
    assert rule.match(snap(tuple({"mobility_aid": value} for value in values))) is None


def test_a_missing_value_does_not_hold():
    rule = load(written())
    match = rule.match(snap(({}, {"mobility_aid": "cane"})))  # the first cannot be seen: not a cane
    assert match.roles == ("gives_way", "aided")


def test_roles_by_a_condition_need_a_tie_policy_and_an_agent_field():
    raw = written()
    del raw["roles"]["by_condition"]["tie"]
    assert refused(raw).category == "no_tie_policy"
    raw = written()
    raw["roles"]["by_condition"]["when"] = {"field": "pair.distance_m", "op": "<", "value": 5, "unit": "m"}
    assert refused(raw).category == "roles"
    raw = written()
    raw["roles"]["by_condition"]["when"] = {"field": "either.mobility_aid", "op": "==", "value": "cane"}
    assert refused(raw).category == "unknown_field"


# --- own-only conditions ----------------------------------------------------------------------------


def test_an_own_only_condition_changes_only_its_own_persons_movement():
    raw = written(roles="symmetric", directive={"both": {"responsibility_share": 0.5, "own_when": own_when("self.assertiveness", "gives_way", {"speed_scale": 0.8, "clearance_margin": 0.2})}})
    rule = load(raw)
    match = rule.match(snap(private=({"assertiveness": "gives_way"}, {"assertiveness": "holds_ground"})))
    assert (match.directives[0].speed_scale, match.directives[0].clearance_margin) == (0.8, 0.2)
    assert (match.directives[1].speed_scale, match.directives[1].clearance_margin) == (1.0, 0.0)
    assert match.directives[0].responsibility_share == match.directives[1].responsibility_share == 0.5


@pytest.mark.parametrize("field, value", [("side_preference", "left"), ("responsibility_share", 1.0), ("passage_order", "leader"), ("back_up", True)])
def test_an_own_only_condition_may_never_set_what_both_must_agree_on(field, value):
    raw = written(roles="symmetric", directive={"both": {"own_when": own_when("self.urgency", "urgent", {field: value})}})
    error = refused(raw)
    assert error.category == "own_only_scope" and field in str(error)


def test_self_fields_are_read_only_in_an_own_only_condition():
    for name in SELF_FIELDS:
        assert resolve(f"self.{name}", "x", ("self", "pair"), 4).prefix == "self"
    raw = written(roles="symmetric", directive={"both": {}}, when={"field": "self.assertiveness", "op": "==", "value": "gives_way"})
    assert refused(raw).category == "unobservable_field"
    for prefix in ("either", "both"):
        raw = written(roles="symmetric", directive={"both": {}}, when={"field": f"{prefix}.assertiveness", "op": "==", "value": "gives_way"})
        assert refused(raw).category == "unobservable_field"
        raw = written(roles="symmetric", directive={"both": {}}, when={"field": f"{prefix}.urgency", "op": "==", "value": "urgent"})
        assert refused(raw).category == "unobservable_field"  # version 4: refused as private, not unknown
    raw = written(roles="symmetric", directive={"both": {"own_when": own_when("either.mobility_aid", "cane", {"speed_scale": 0.9})}})
    assert refused(raw).category == "unknown_field"  # an own-only condition reads self. and pair. only


def test_perceived_attractiveness_is_readable_only_as_the_persons_own_view_in_version_4():
    raw = written(roles="symmetric", directive={"both": {"own_when": own_when(OWN_ATTRACTIVENESS, True, {"clearance_margin": 0.1})}})
    rule = load(raw)
    assert rule.match(snap(private=({"finds_other_attractive": True}, {}))).directives[0].clearance_margin == 0.1
    for where in ("either.finds_other_attractive", "both.finds_other_attractive", "self.finds_other_attractive", "either.attractiveness"):
        attempt = written(roles="symmetric", directive={"both": {}}, when={"field": where, "op": "==", "value": True})
        assert refused(attempt).category == "protected_attribute", where
    attempt = written(roles="symmetric", directive={"both": {"own_when": own_when("self.attractiveness", True, {"speed_scale": 0.9})}})
    assert refused(attempt).category == "protected_attribute"  # only the one name
    attempt = written(roles={"by_condition": {"when": {"field": "agent.finds_other_attractive", "op": "==", "value": True}, "assign": ["a", "b"], "tie": "no_match"}}, directive={"a": {}, "b": {}})
    assert refused(attempt).category == "protected_attribute"
    three = copy.deepcopy(raw)
    three["schema_version"] = 3
    assert refused(three).category in ("schema", "protected_attribute")  # version 3 cannot hold it at all


@pytest.mark.parametrize("field", ["self.ethnicity", "self.ethnic_group", "self.malay", "pair.same_ethnicity"])
def test_ethnicity_is_refused_in_version_4_everywhere(field):
    raw = written(roles="symmetric", directive={"both": {"own_when": own_when(field, "x", {"speed_scale": 0.9})}})
    assert refused(raw).category == "protected_attribute"
    raw = written(roles="symmetric", directive={"both": {}}, when={"field": field.replace("self.", "either."), "op": "==", "value": "x"})
    assert refused(raw).category == "protected_attribute"


# --- steps --------------------------------------------------------------------------------------------


@pytest.mark.parametrize("change, category", [
    (lambda steps: steps[1].pop("until"), "steps"),  # a plain step needs an until
    (lambda steps: steps[0]["sidestep"].update(metres=3.5), "schema"),
    (lambda steps: steps[0].update(turn={"to": "left", "degrees": 120}), "schema"),
    (lambda steps: steps[0].update(turn={"to": "left", "degrees": 10}), "steps"),  # a turn to the other side of the sidestep
    (lambda steps: steps[1].update(until="other_stops"), "schema"),  # not a rule's event
    (lambda steps: steps[0].update(start={"after_seconds": 1}), "schema"),
])
def test_steps_are_checked_with_step_1s_own_limits(change, category):
    raw = written()
    change(raw["directive"]["gives_way"]["steps"])
    assert refused(raw).category == category


def run_head_on(rule=None, attributes=None, pairwise=None):
    attributes = attributes if attributes is not None else {0: {"age": 30, "gender": "female"}, 1: {"age": 70, "gender": "male", "mobility_aid": "cane"}}
    provider = None if rule is None else RuleDatabaseProvider(ActiveRuleSet.build([rule]), VISIBLE)
    sim = AvoidanceSimulation(crowd("wide_corridor_head_on"), provider, attributes=attributes, visibility=VISIBLE, pairwise=pairwise)
    return sim, sim.run()


def lateral(result, agent):
    return [row["y_m"] for row in result.trajectory if row["agent_id"] == agent]


def test_in_a_head_on_the_one_who_gives_way_sidesteps_keeps_that_line_and_only_then_goes_back():
    """The step followed by a plain step (memory: rehearse multi-step plans): the sidestep holds
    through the plain step until the two have passed."""
    plain_sim, plain = run_head_on()
    sim, result = run_head_on(load(written()))
    assert plain.status == "deadlock" and result.status == "completed" and result.collisions["agent_agent"] == 0
    ys = lateral(result, 0)
    assert min(ys) == pytest.approx(-0.6, abs=0.02)  # 0.6 m to its right, as asked
    assert max(abs(y) for y in lateral(result, 1)) < 1e-6  # the one with the cane keeps its line
    plans = result.provider_summary["plans"]
    assert plans["plans_started"] == 1 and plans["steps_ended_by"] == {"other_passes": 1, "sidestepped": 1}
    assert plans["plans_over"] == {"passed": 1}
    track = sim.plans.decisions[0].records
    passed_step = track[1].end_step
    held = [row["y_m"] for row in result.trajectory if row["agent_id"] == 0 and track[0].end_step <= row["step"] <= passed_step]
    assert all(y == pytest.approx(-0.6, abs=0.02) for y in held)  # the plain step did not undo the sidestep
    assert abs(ys[-1]) < 0.05  # back on its path afterwards


def test_a_rule_without_steps_attaches_no_driver_and_a_run_without_rules_is_unchanged():
    raw = written(directive={"aided": {}, "gives_way": {"responsibility_share": 1.0}})
    sim, _ = run_head_on(load(raw))
    assert sim.plans is None and sim.provider.step_driver is None
    sim, _ = run_head_on()
    assert sim.plans is None


def test_an_own_only_condition_can_give_or_withhold_the_plan():
    raw = written(directive={"aided": {}, "gives_way": {"own_when": own_when("self.assertiveness", "gives_way", {"steps": copy.deepcopy(SIDESTEP)})}})
    for level, expect_plan in (("gives_way", True), ("holds_ground", False)):
        attributes = {0: {"age": 30, "gender": "female", "assertiveness": level}, 1: {"age": 70, "gender": "male", "mobility_aid": "cane"}}
        _, result = run_head_on(load(raw), attributes)
        assert (result.provider_summary["plans"]["plans_started"] == 1) is expect_plan
        assert result.provider_summary["formation_mismatches"] == 0


def test_a_pairwise_view_reaches_the_own_only_condition_and_the_independent_evaluation():
    raw = written(roles="symmetric", directive={"both": {"own_when": own_when(OWN_ATTRACTIVENESS, True, {"steps": copy.deepcopy(SIDESTEP)})}})
    attributes = {0: {"age": 30, "gender": "female"}, 1: {"age": 70, "gender": "male"}}
    _, result = run_head_on(load(raw), attributes, pairwise={(0, 1): {"finds_other_attractive": True}})
    summary = result.provider_summary
    assert summary["plans"]["plans_started"] == 1 and summary["formation_mismatches"] == 0


def test_in_a_crowd_a_version_4_rule_runs_and_one_plan_per_person_at_a_time():
    raw = written(when={"field": "pair.distance_m", "op": "<", "value": 8, "unit": "m"},
                  directive={"aided": {"responsibility_share": 0.0}, "gives_way": {"responsibility_share": 1.0, "steps": copy.deepcopy(SIDESTEP),
                                                                                  "own_when": own_when("self.assertiveness", "holds_ground", {"steps": [{"speed_mps": 1.3, "until": {"seconds": 1.0}}]})}})
    spec = crowd("bidirectional_flow", geometry={"agents_per_direction": 10, "length": 24.0}, max_time=60.0)
    people = mixed_population(len(spec.agents), (25, 70), ("female", "male"), {"mobility_aid": ["none", "cane"], "assertiveness": ["gives_way", "holds_ground"]})
    sim = AvoidanceSimulation(spec, RuleDatabaseProvider(ActiveRuleSet.build([load(raw)]), VISIBLE), attributes=people, visibility=VISIBLE, record_trajectory=False)
    result = sim.run()
    summary = result.provider_summary
    assert result.status == "completed" and summary["formation_mismatches"] == 0
    plans = summary["plans"]
    assert plans["plans_started"] > 0
    assert plans["plans_taken_up"] == plans["plans_started"]
    starts = [plan.given_step for plan in sim.plans.decisions]
    by_agent: dict[int, list] = {}
    for plan in sim.plans.decisions:
        by_agent.setdefault(plan.agent_id, []).append(plan)
    for plans_of_agent in by_agent.values():  # a person's next plan starts only after the last one is over
        for earlier, later in zip(plans_of_agent, plans_of_agent[1:]):
            assert later.given_step >= earlier.ended_step
    assert starts == sorted(starts)


# --- the snapshot and the perception record -----------------------------------------------------------


def test_the_observers_own_factors_reach_its_record_only_when_it_has_them():
    assert own_attributes({"age": 30, "gender": "female"}) == {"age": 30, "gender": "female"}  # every earlier run
    assert own_attributes({"age": 30, "gender": "female", "mobility_aid": "cane", "assertiveness": "gives_way"}) == {
        "age": 30, "gender": "female", "mobility_aid": "cane", "assertiveness": "gives_way"}


def test_a_snapshot_logs_version_4_fields_only_when_someone_has_them():
    plain = snap(({"age": 30}, {"age": 70}))
    assert "mobility_aid" not in plain.as_dict()["agent"]["0"] and "self" not in plain.as_dict()
    seen = snap(({"mobility_aid": "cane"}, {}), ({"assertiveness": "gives_way"}, {}))
    logged = seen.as_dict()
    assert logged["agent"]["0"]["mobility_aid"] == "cane" and logged["self"]["0"]["assertiveness"] == "gives_way"
    assert "self" not in seen.as_dict(3) and "mobility_aid" not in seen.as_dict(3)["agent"]["0"]


# --- the ambiguity grid ---------------------------------------------------------------------------------


def test_the_grid_finds_two_version_4_rules_that_give_different_plans():
    first = load(written())
    other = written(rule_id="aided_goes_on_left")
    other["directive"]["gives_way"]["steps"][0]["sidestep"]["to"] = "left"
    clash = find_clash(first, load(other))
    assert clash is not None and clash.checked
    same = find_clash(first, load(written(rule_id="aided_goes_on_again")))
    assert same is None


def test_the_grid_varies_a_persons_own_factors():
    a = load(written(roles="symmetric", directive={"both": {"own_when": own_when("self.urgency", "urgent", {"speed_scale": 1.2})}}))
    b = load(written(rule_id="calm", roles="symmetric", directive={"both": {}}))
    clash = find_clash(a, b)
    assert clash is not None and clash.situation.private != ({}, {})


# --- rule generation's categories ----------------------------------------------------------------------


SEE = {**VISIBLE}


def body(raw):
    return {key: raw[key] for key in ("encounter", "when", "roles", "directive", "priority")}


def test_validate_counts_a_version_4_proposal_in_the_right_category():
    assert V.validate_proposal(body(written()), SEE, schema_version=4).category == V.VALID
    scope = written(roles="symmetric", directive={"both": {"own_when": own_when("self.urgency", "urgent", {"side_preference": "left"})}})
    result = V.validate_proposal(body(scope), SEE, schema_version=4)
    assert (result.category, result.loader_category) == (V.NEEDS_COMMUNICATION, "own_only_scope")
    attractive = written(roles="symmetric", directive={"both": {"own_when": own_when(OWN_ATTRACTIVENESS, True, {"speed_scale": 0.9})}})
    assert V.validate_proposal(body(attractive), SEE, schema_version=4).category == V.VALID
    assert V.validate_proposal(body(attractive), SEE, schema_version=3).category == V.FORMAT_LIMIT
    hidden = {**SEE, "mobility_aid": False}
    assert V.validate_proposal(body(written()), hidden, schema_version=4).category == V.NEEDS_COMMUNICATION


def test_a_version_3_session_cannot_say_what_version_4_added():
    for raw in (written(), written(roles="symmetric", directive={"both": {"steps": SIDESTEP}})):
        assert V.validate_proposal(body(raw), SEE, schema_version=3).category == V.FORMAT_LIMIT
    seen = written(roles="symmetric", directive={"both": {}}, when={"field": "either.mobility_aid", "op": "==", "value": "cane"})
    assert V.validate_proposal(body(seen), SEE, schema_version=3).category == V.FORMAT_LIMIT


# --- crowd populations ------------------------------------------------------------------------------------


def test_a_crowd_can_be_given_core_factors_without_changing_ages_and_genders():
    before = mixed_population(12, (25, 70), ("female", "male"))
    after = mixed_population(12, (25, 70), ("female", "male"), {"mobility_aid": ["none", "cane"], "assertiveness": ["gives_way", "holds_ground"]})
    assert [{k: v[k] for k in ("age", "gender")} for v in after.values()] == list(before.values())
    assert [after[k]["mobility_aid"] for k in range(12)] == ["none"] * 4 + ["cane"] * 4 + ["none"] * 4
    assert [after[k]["assertiveness"] for k in range(12)] == ["gives_way"] * 8 + ["holds_ground"] * 4
    persons = population_of(after, "crowd")
    assert persons[4]["attributes"] == {"age": 25, "gender": "female", "mobility_aid": "cane", "assertiveness": "gives_way"}
    assert population_of(before, "crowd")[0]["attributes"] == {"age": 25, "gender": "female"}  # as before


# --- a role condition that can never give two different roles (the user's decision of 2026-10-26) ----


@pytest.mark.parametrize("condition", [
    {"field": "agent.speed_mps", "op": ">=", "value": 0, "unit": "m/s"},  # RF-31's x_head_on_aacce0961b
    {"field": "agent.age", "op": ">=", "value": 0, "unit": "years"},
    {"field": "agent.speed_mps", "op": "<", "value": 0, "unit": "m/s"},  # never true
    {"field": "agent.mobility_aid", "op": "in", "value": ["none", "cane"]},
    {"any": [{"field": "agent.load", "op": "==", "value": "none"}, {"field": "agent.load", "op": "==", "value": "large_suitcase"}]},
    {"all": [{"field": "agent.radius_m", "op": ">", "value": 0.2, "unit": "m"}, {"field": "agent.radius_m", "op": "<", "value": 0.1, "unit": "m"}]},
])
def test_a_role_condition_that_holds_for_both_or_neither_in_every_situation_is_refused(condition):
    raw = written(roles={"by_condition": {"when": condition, "assign": ["a", "b"], "tie": "no_match"}}, directive={"a": {}, "b": {}})
    error = refused(raw)
    assert error.category == "constant_roles"
    assert V.validate_proposal(body(raw), SEE, schema_version=4).category == V.INCONSISTENT


@pytest.mark.parametrize("condition", [
    {"field": "agent.speed_mps", "op": ">", "value": 1.0, "unit": "m/s"},
    {"field": "agent.age", "op": ">=", "value": 60, "unit": "years"},
    {"field": "agent.distraction", "op": "==", "value": "phone"},
    {"all": [{"field": "agent.mobility_aid", "op": "==", "value": "cane"}, {"field": "pair.distance_m", "op": "<", "value": 5, "unit": "m"}]},
])
def test_a_role_condition_that_can_differ_loads(condition):
    raw = written(roles={"by_condition": {"when": condition, "assign": ["a", "b"], "tie": "no_match"}}, directive={"a": {}, "b": {}})
    assert isinstance(load(raw).roles, ConditionRoles)
