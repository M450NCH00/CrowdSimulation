"""The matching policy and the rule provider (issue #28, Parts 4, 5 and 7), and the
consistency property test.

The policy is tested two ways: through a scripted step view, in which the encounter class
and "passed" are set by hand step by step, so that flicker, re-evaluation, priority at a
class change and expiry can be pinned down exactly; and through whole runs of the shipped
scenarios with the rule provider. The property test evaluates the seed database on many
random pairs."""

from __future__ import annotations

import math
import random

import pytest

from helpers import crowd, free_space, run_avoidance
from negsim.avoidance.directives import PLAIN_ORCA, AvoidanceDirective, resolve_pair
from negsim.avoidance.perception import ENCOUNTER_CLASSES, PairFeatures, default_visibility, pair_features, perceive
from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.configutil import PACKAGE_ROOT
from negsim.core.state import Pose
from negsim.rules import ActiveRuleSet, RuleDatabase, RuleDatabaseProvider, RuleError
from negsim.rules.database import RULE_DB_ROOT, load_validator, read_rule_file
from negsim.rules.matching import (
    AMBIGUOUS_MATCH,
    CONFLICT_RESOLUTIONS,
    KEPT,
    NO_RULE_MATCHED,
    RULE_MATCHED,
    RuleMatcher,
    evaluate,
)
from negsim.rules.model import parse_rule
from negsim.rules.snapshot import snapshot_of_pair, snapshot_of_record

VALIDATOR = load_validator(RULE_DB_ROOT)
DATABASE = RuleDatabase.load()
FIXTURES = PACKAGE_ROOT / "tests" / "fixtures" / "rules"
VISIBLE = default_visibility()
AGES = {0: {"age": 25, "gender": "female"}, 1: {"age": 70, "gender": "male"}, 2: {"age": 40, "gender": "male"}}


def make_rule(rule_id, encounter="head_on", priority=10, when=None, roles="symmetric", directive=None, expiry=None):
    raw = {
        "schema_version": 1, "rule_id": rule_id, "version": 1, "status": "test_seed",
        "provenance": {"source_type": "hand_written", "source_ref": "test", "created_at": "2026-10-14",
                       "author": "test", "notes": "", "validation_evidence": []},
        "encounter": encounter, "when": when or {"all": []}, "roles": roles,
        "directive": directive or {"both": {"side_preference": "left"}}, "priority": priority,
    }
    if expiry:
        raw["expiry"] = expiry
    return parse_rule(raw, VALIDATOR, rule_id)


def place(agent, x, y, heading, speed):
    agent.pose = Pose(x, y, heading)
    agent.velocity = (speed * math.cos(heading), speed * math.sin(heading))
    agent.speed = speed


def rules_provider(*rules, check=True, steps=3):
    return RuleDatabaseProvider(ActiveRuleSet.build(list(rules), "test", check=check), VISIBLE, steps)


# --- a scripted step view ------------------------------------------------------------------------


class FakePair:
    def __init__(self, agents):
        self.agents, self.provider_record = agents, None


class ScriptedView:
    """The run loop reduced to what the matcher sees. ``script[step][pair]`` is
    ``(encounter class, passed)``; everything else is computed from three agents placed
    head-on and abreast, 5 m apart, so a snapshot has real numbers in it."""

    def __init__(self, script):
        spec = free_space([{"start": (0, 0), "goal": (20, 0)}, {"start": (5, 0), "goal": (-15, 0)}, {"start": (5, 3), "goal": (-15, 3)}])
        self.world = spec.build_world()
        place(self.world.agents[0], 0.0, 0.0, 0.0, 1.3)
        place(self.world.agents[1], 5.0, 0.0, math.pi, 1.3)
        place(self.world.agents[2], 5.0, 3.0, math.pi, 1.3)
        self.script, self.step, self.time_s = script, 0, 0.0
        self.visibility, self.attributes = VISIBLE, AGES
        self.held: dict[tuple[int, int], AvoidanceDirective] = {}
        self._pairs: dict[tuple[int, int], FakePair] = {}

    @property
    def pairs(self):
        return [self._pairs.setdefault(key, FakePair(key)) for key in sorted(self.script[self.step])]

    def pair(self, key):
        return self._pairs[key]

    def agent(self, agent_id):
        return self.world.agents[agent_id]

    def directions(self, pair):
        i, j = pair.agents
        return [(i, j), (j, i)]

    def current_directive(self, observer, neighbour):
        return self.held.get((observer, neighbour), PLAIN_ORCA)

    def encounter_class(self, i, j):
        return self.script[self.step][(i, j)][0]

    def features(self, i, j):
        real = pair_features(self.agent(i), self.agent(j), (), VISIBLE, AGES, 12.5)
        return PairFeatures(real.agents, self.encounter_class(i, j), real.heading_difference_rad,
                            real.min_corridor_width_m, real.age_difference_years, None, (None, None))

    def passed(self, i, j, clearance):
        return self.script[self.step][(i, j)][1]

    def run(self, matcher):
        """Step through the whole script; return the changes of each step."""
        changes = []
        while self.step < len(self.script):
            found = matcher.step(self)
            self.held.update(found)
            changes.append(found)
            self.step += 1
            self.time_s = self.step / 10.0
        for pair in self._pairs.values():
            matcher.close(pair, self.step, self.time_s, "run_ended")
        return changes


def scripted(*classes, passed_at=None, pair=(0, 1)):
    """One pair, its class on each step, and the step from which it has passed."""
    return [{pair: (cls, passed_at is not None and step >= passed_at)} for step, cls in enumerate(classes)]


def outcomes(record):
    return [(entry["outcome"], entry["rule"], entry["count"]) for entry in record.evaluations]


# --- when rules are evaluated ---------------------------------------------------------------------


def test_rules_are_evaluated_when_the_pair_forms():
    keep_left = DATABASE.get("keep_left_head_on", 1)
    view = ScriptedView(scripted("head_on", "head_on", "head_on"))
    changes = view.run(RuleMatcher(ActiveRuleSet.build([keep_left])))
    assert changes[0] == {(0, 1): keep_left.directives["both"], (1, 0): keep_left.directives["both"]}
    assert changes[1] == changes[2] == {}  # held: nothing changes and nothing is evaluated
    assert outcomes(view.pair((0, 1)).provider_record) == [(RULE_MATCHED, "keep_left_head_on@1", 1)]


def test_a_rule_whose_threshold_is_met_later_fires_later():
    """While nothing holds, the pair is evaluated on every step: a rule that needs the two
    within 4 s of colliding (4.56 s when they first see each other) fires once they are.

    (A threshold below 2.9 s would not fire here at all: once ORCA brakes a head-on pair it
    closes the gap at gap / tau per step, so the time to collision stays at tau - dt =
    2.9 s. ``docs/rule-format.md`` notes it.)"""
    close = make_rule("close_only", when={"all": [{"field": "pair.time_to_collision_s", "op": "<=", "value": 4.0, "unit": "s"}]})
    result = run_avoidance(crowd("wide_corridor_head_on"), rules_provider(close))
    (pair,) = result.pairs
    record = pair.provider_record
    assert record.evaluations[0]["outcome"] == NO_RULE_MATCHED and record.evaluations[0]["count"] >= 3
    assert record.evaluations[0]["snapshot"]["pair"]["time_to_collision_s"] > 4.0
    (match,) = record.matches
    assert match["from_step"] == pair.start_step + record.evaluations[0]["count"]
    assert match["snapshot"]["pair"]["time_to_collision_s"] <= 4.0


def test_under_orca_braking_the_time_to_collision_stays_one_step_short_of_the_horizon():
    """The fact the docstring above rests on. In the exactly symmetric head-on under plain
    ORCA, each braking step leaves the gap g (1 - dt/tau) while the two closed at g / tau,
    so the time to collision read on the next step is tau - dt = 2.9 s, step after step.
    A rule needing at most 2.8 s never fires, and the pair deadlocks as without rules; one
    needing at most 2.9 s fires, and its side preference breaks the deadlock."""
    never = make_rule("never_fires", when={"all": [{"field": "pair.time_to_collision_s", "op": "<=", "value": 2.8, "unit": "s"}]})
    result = run_avoidance(crowd("wide_corridor_head_on"), rules_provider(never))
    assert result.deadlock and result.pairs[0].provider_record.matches == []
    at_limit = make_rule("at_the_limit", when={"all": [{"field": "pair.time_to_collision_s", "op": "<=", "value": 2.9, "unit": "s"}]})
    result = run_avoidance(crowd("wide_corridor_head_on"), rules_provider(at_limit))
    (match,) = result.pairs[0].provider_record.matches
    assert not result.deadlock and match["snapshot"]["pair"]["time_to_collision_s"] == pytest.approx(2.9, abs=1e-6)


def test_a_held_rule_ignores_its_own_condition_until_it_expires():
    """The condition held on the step it matched; once the two step aside they are no
    longer on a collision course and it fails, but the match holds until they have passed."""
    close = make_rule("close_only", when={"all": [{"field": "pair.time_to_collision_s", "op": "<=", "value": 4.0, "unit": "s"}]})
    result = run_avoidance(crowd("wide_corridor_head_on"), rules_provider(close))
    (pair,) = result.pairs
    (match,) = pair.provider_record.matches
    assert match["end_reason"] == "passed" and match["to_step"] == pair.passed_step
    assert pair.passed_step - match["from_step"] > 20


# --- several matches -------------------------------------------------------------------------------


def test_the_highest_priority_wins_and_fields_are_not_merged_across_rules():
    active = DATABASE.activate("default")
    result = run_avoidance(crowd("wide_corridor_head_on"), RuleDatabaseProvider(active, VISIBLE), attributes=AGES)
    (match,) = result.pairs[0].provider_record.matches
    assert match["rule_id"] == "younger_yields_head_on" and match["roles"] == {"0": "yielder", "1": "other"}
    # keep_left_head_on matched too, at a lower priority: its side is NOT added.
    assert match["directives"]["0"] == AvoidanceDirective(responsibility_share=1.0).as_dict()
    assert match["directives"]["1"] == AvoidanceDirective(responsibility_share=0.0).as_dict()


def test_two_rules_at_one_priority_with_different_directives_are_ambiguous_at_run_time():
    """Refused when switched on; with the check off (as only this test does), the run logs
    ambiguous_match and applies the lower rule_id."""
    clash_side = read_rule_file(FIXTURES / "ambiguous" / "clash_side.v1.yaml", VALIDATOR)
    clash_clearance = read_rule_file(FIXTURES / "ambiguous" / "clash_clearance.v1.yaml", VALIDATOR)
    with pytest.raises(RuleError):
        ActiveRuleSet.build([clash_side, clash_clearance])
    result = run_avoidance(crowd("wide_corridor_head_on"), rules_provider(clash_side, clash_clearance, check=False))
    record = result.pairs[0].provider_record
    (match,) = record.matches
    assert match["outcome"] == AMBIGUOUS_MATCH and match["rule_id"] == "clash_clearance"
    assert match["ambiguous_with"] == ["clash_side@1"] and match["directives"]["0"]["clearance_margin"] == 0.3
    assert any(entry["outcome"] == AMBIGUOUS_MATCH for entry in record.evaluations)


def test_two_rules_at_one_priority_that_agree_are_not_ambiguous():
    first = make_rule("aaa_left")
    second = make_rule("bbb_left")
    snapshot = ScriptedView(scripted("head_on"))
    a, b = snapshot.agent(0), snapshot.agent(1)
    found = evaluate(ActiveRuleSet.build([first, second]), snapshot_of_pair(0, 0.0, a, b, snapshot.features(0, 1), VISIBLE, AGES))
    assert found.outcome == RULE_MATCHED and found.match.rule.rule_id == "aaa_left"


def test_with_no_match_the_pair_follows_the_baseline():
    keep_left = DATABASE.get("keep_left_head_on", 1)
    result = run_avoidance(crowd("overtaking"), rules_provider(keep_left))
    (pair,) = result.pairs
    assert pair.provider_record.matches == [] and {entry["outcome"] for entry in pair.provider_record.evaluations} == {NO_RULE_MATCHED}
    assert all(not interaction.directive_changes and interaction.directive == PLAIN_ORCA for interaction in result.interactions)
    plain = run_avoidance(crowd("overtaking"))
    assert [row["x_m"] for row in result.trajectory] == [row["x_m"] for row in plain.trajectory]


# --- holding, hysteresis, priority at a class change -------------------------------------------------


def test_a_class_that_flickers_triggers_nothing_and_a_steady_change_does():
    high = make_rule("crossing_high", encounter="crossing", priority=50, directive={"both": {"clearance_margin": 0.2}})
    keep_left = DATABASE.get("keep_left_head_on", 1)
    flicker = ["head_on", "crossing", "head_on", "crossing", "crossing", "head_on"]
    view = ScriptedView(scripted(*flicker))
    view.run(RuleMatcher(ActiveRuleSet.build([keep_left, high]), hysteresis_steps=3))
    record = view.pair((0, 1)).provider_record
    assert [entry["rule_id"] for entry in record.matches] == ["keep_left_head_on"] and record.class_used == "head_on"

    steady = ["head_on", "crossing", "crossing", "crossing", "crossing"]
    view = ScriptedView(scripted(*steady))
    view.run(RuleMatcher(ActiveRuleSet.build([keep_left, high]), hysteresis_steps=3))
    record = view.pair((0, 1)).provider_record
    first, second = record.matches
    assert (first["rule_id"], first["end_reason"], first["to_step"], first["replaced_by"]) == ("keep_left_head_on", "replaced", 3, "crossing_high@1")
    assert second["rule_id"] == "crossing_high" and second["from_step"] == 3  # the third steady step


def test_a_held_rule_is_replaced_only_by_a_strictly_higher_priority_at_a_class_change():
    keep_left = DATABASE.get("keep_left_head_on", 1)
    same = make_rule("crossing_same", encounter="crossing", priority=10, directive={"both": {"clearance_margin": 0.2}})
    view = ScriptedView(scripted("head_on", "crossing", "crossing", "crossing", "crossing"))
    view.run(RuleMatcher(ActiveRuleSet.build([keep_left, same]), hysteresis_steps=3))
    record = view.pair((0, 1)).provider_record
    assert [entry["rule_id"] for entry in record.matches] == ["keep_left_head_on"]
    assert (KEPT, None, 1) in outcomes(record)  # evaluated at the class change; kept


def test_after_expiry_the_pair_is_evaluated_again_only_once_its_class_has_changed():
    keep_left = DATABASE.get("keep_left_head_on", 1)
    # Passed at step 2. Then head-on again at once (a jostle: no new match), then none for
    # three steps, then head-on for three: a new encounter, and a new match.
    classes = ["head_on", "head_on", "head_on", "head_on", "none", "none", "none", "head_on", "head_on", "head_on"]
    script = [{(0, 1): (cls, step in (2,))} for step, cls in enumerate(classes)]
    view = ScriptedView(script)
    view.run(RuleMatcher(ActiveRuleSet.build([keep_left]), hysteresis_steps=3))
    first, second = view.pair((0, 1)).provider_record.matches
    assert (first["from_step"], first["to_step"], first["end_reason"]) == (0, 2, "passed")
    assert second["from_step"] == 7 and second["end_reason"] == "run_ended"


def test_a_rule_that_says_out_of_range_does_not_expire_when_the_pair_has_passed():
    lasting = make_rule("lasting", expiry="out_of_range")
    view = ScriptedView(scripted("head_on", "head_on", "none", "none", passed_at=1))
    changes = view.run(RuleMatcher(ActiveRuleSet.build([lasting])))
    (match,) = view.pair((0, 1)).provider_record.matches
    assert match["end_reason"] == "run_ended" and all(change == {} for change in changes[1:])


# --- expiry, and speed_scale ---------------------------------------------------------------------------


def test_a_match_expires_when_the_encounter_has_passed_and_every_field_reverts():
    result = run_avoidance(crowd("wide_corridor_head_on"), rules_provider(DATABASE.get("keep_left_head_on", 1)))
    (pair,) = result.pairs
    (match,) = pair.provider_record.matches
    assert match["end_reason"] == "passed" and match["to_step"] == pair.passed_step
    for interaction in result.interactions:
        assert [change["from_step"] for change in interaction.directive_changes] == [pair.passed_step]
        assert interaction.directive == PLAIN_ORCA and interaction.initial_directive.side_preference == "left"


def test_a_rules_speed_scale_applies_until_closest_approach_and_not_after():
    slow = make_rule("slow_left", directive={"both": {"side_preference": "left", "speed_scale": 0.5}})
    result = run_avoidance(crowd("wide_corridor_head_on"), rules_provider(slow))
    (pair,) = result.pairs
    rows = [row for row in result.trajectory if row["agent_id"] == 0 and row["speed_mps"] is not None]
    scale = {row["step"]: row["speed_scale"] for row in rows}
    assert {scale[step] for step in range(pair.start_step, pair.passed_step)} == {0.5}
    assert {scale[step] for step in scale if step >= pair.passed_step} == {1.0}


def test_passed_means_separating_and_clear():
    spec = free_space([{"start": (0, 0), "goal": (20, 0)}, {"start": (5, 0.6), "goal": (-15, 0.6)}])
    simulation = AvoidanceSimulation(spec)
    a, b = simulation.world.agents
    a.pose, a.velocity = Pose(0.0, 0.0, 0.0), (1.0, 0.0)
    b.velocity = (-1.0, 0.0)  # set exactly: sin(pi) is not exactly 0 in floating point
    b.pose = Pose(0.0, 0.6, math.pi)  # abreast: closest approach, p . v = 0
    assert not simulation._passed(0, 1, 0.0)
    b.pose = Pose(-0.1, 0.6, math.pi)  # just past: separating, 0.608 m apart, more than the 0.5 m of two radii
    assert simulation._passed(0, 1, 0.0) and not simulation._passed(0, 1, 0.2)  # but not clear of a 0.2 m margin
    b.pose = Pose(0.2, 0.6, math.pi)  # not yet abreast: still approaching
    assert not simulation._passed(0, 1, 0.0)


# --- several neighbours ------------------------------------------------------------------------------


def test_contradictory_matches_of_one_agent_are_logged_as_a_cross_pair_conflict():
    keep_left = DATABASE.get("keep_left_head_on", 1)
    right_crossing = make_rule("crossing_right", encounter="crossing", directive={"both": {"side_preference": "right"}})
    script = [{(0, 1): ("head_on", False), (0, 2): ("crossing", False)} for _ in range(4)]
    view = ScriptedView(script)
    matcher = RuleMatcher(ActiveRuleSet.build([keep_left, right_crossing]))
    view.run(matcher)
    (event,) = matcher.conflict_events  # logged once, when it appears
    assert (event["agent_id"], event["field"], event["step"]) == (0, "side_preference", 0)
    assert {item["value"] for item in event["values"]} == {"left", "right"}
    assert event["resolution"] == CONFLICT_RESOLUTIONS["side_preference"]
    assert view.pair((0, 1)).provider_record.conflicts == [event] == view.pair((0, 2)).provider_record.conflicts
    # Each pair keeps its own side: nothing was changed to settle it.
    assert view.held[(0, 1)].side_preference == "left" and view.held[(0, 2)].side_preference == "right"


# --- the provider ----------------------------------------------------------------------------------


def head_on_record(observer, visibility=VISIBLE, attributes=AGES):
    world = crowd("wide_corridor_head_on").build_world()
    agents = world.agents
    return perceive(0, 0.0, agents[observer], agents[1 - observer], world.obstacles, visibility, attributes, 1.3)


def test_the_provider_answers_from_one_record_with_the_observers_role():
    provider = RuleDatabaseProvider(DATABASE.activate("default"), VISIBLE)
    assert provider.directive(head_on_record(0)) == AvoidanceDirective(responsibility_share=1.0)  # the younger
    assert provider.directive(head_on_record(1)) == AvoidanceDirective(responsibility_share=0.0)
    assert provider.directive(head_on_record(0, attributes={})) == AvoidanceDirective(side_preference="left")


def test_the_provider_returns_the_baseline_when_nothing_matches():
    provider = RuleDatabaseProvider(DATABASE.activate(enable={"overtaker_keeps_clear": 1}), VISIBLE)
    assert provider.directive(head_on_record(0)) is PLAIN_ORCA


def test_the_provider_refuses_a_run_that_hides_what_its_rules_read():
    with pytest.raises(RuleError, match="visibility"):
        RuleDatabaseProvider(DATABASE.activate("default"), {**VISIBLE, "age": False})


def test_a_whole_run_with_the_provider_and_what_it_records():
    provider = RuleDatabaseProvider(DATABASE.activate("default"), VISIBLE)
    result = run_avoidance(crowd("wide_corridor_head_on"), provider)
    summary = result.provider_summary
    assert summary["matches_begun"] == {"keep_left_head_on@1": 1} and summary["match_ends"] == {"passed": 1}
    assert summary["formation_checks"] == 2 and summary["formation_mismatches"] == 0
    assert result.pairs[0].provider_record.independent_agrees is True
    assert provider.describe()["rules"][0]["sha256"] and provider.describe()["ruleset"] == "default"


# --- the shared snapshot and each agent's own -----------------------------------------------------


@pytest.mark.parametrize("hidden", [None, "age", "gender", "speed", "size"])
def test_the_shared_snapshot_equals_what_each_agent_builds_from_its_own_record(hidden):
    """Part 4's equivalence, checked on 300 random states of the bottleneck (walls and a
    single-file segment), with random ages and genders, under each visibility setting."""
    visibility = dict(VISIBLE) if hidden is None else {**VISIBLE, hidden: False}
    rng = random.Random(28)
    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    a, b = world.agents
    for trial in range(300):
        for agent in (a, b):
            place(agent, rng.uniform(-9, 9), rng.uniform(-0.6, 0.6), rng.uniform(-math.pi, math.pi), rng.choice([0.0, rng.uniform(0, 2)]))
        attributes = {agent.agent_id: {"age": rng.randint(5, 95), "gender": rng.choice(["female", "male", "nonbinary"])} for agent in (a, b)}
        features = pair_features(a, b, world.obstacles, visibility, attributes, 12.5, spec.single_file_segments)
        shared = snapshot_of_pair(trial, 0.0, a, b, features, visibility, attributes)
        for observer, neighbour in ((a, b), (b, a)):
            record = perceive(trial, 0.0, observer, neighbour, world.obstacles, visibility, attributes, 1.3,
                              environment_range=12.5, pair=features)
            assert snapshot_of_record(record, visibility).same_values(shared), (trial, observer.agent_id)


# --- the consistency property test --------------------------------------------------------------------


SCENES = {}


def random_pair(rng):
    """Two agents in open ground or in the bottleneck, anywhere, moving any way, any ages."""
    name = "corridor_to_bottleneck" if rng.random() < 0.5 else "open_crossing"
    if name not in SCENES:
        spec = crowd(name)
        SCENES[name] = (spec, spec.build_world())
    spec, world = SCENES[name]
    a, b = world.agents
    span = 9.0 if name == "corridor_to_bottleneck" else 8.0
    for agent in (a, b):
        y = rng.uniform(-0.6, 0.6) if name == "corridor_to_bottleneck" else rng.uniform(-span, span)
        place(agent, rng.uniform(-span, span), y, rng.uniform(-math.pi, math.pi), rng.choice([0.0, rng.uniform(0.0, 2.0)]))
    attributes = {agent.agent_id: {"age": rng.randint(5, 95), "gender": rng.choice(["female", "male", "nonbinary"])} for agent in (a, b)}
    return spec, world, a, b, attributes


def consistency_counts(active, trials=4000, seed=28):
    counts = {"pairs": 0, "matched": 0, "reciprocity_violations": 0, "non_complementary": 0, "ties": 0, "classes": {}}
    rng = random.Random(seed)
    for trial in range(trials):
        spec, world, a, b, attributes = random_pair(rng)
        features = pair_features(a, b, world.obstacles, VISIBLE, attributes, 12.5, spec.single_file_segments)
        snapshot = snapshot_of_pair(trial, 0.0, a, b, features, VISIBLE, attributes)
        counts["pairs"] += 1
        counts["classes"][snapshot.encounter_class] = counts["classes"].get(snapshot.encounter_class, 0) + 1
        for rule in active.candidates(snapshot.encounter_class):
            if rule.roles is not None and rule.when.evaluate(snapshot) and rule.roles.roles(snapshot) is None:
                counts["ties"] += 1  # the rule applied, but the two tied: no_match
        found = evaluate(active, snapshot)
        if found.match is None:
            directives = (PLAIN_ORCA, PLAIN_ORCA)
        else:
            counts["matched"] += 1
            directives = found.match.directives
        resolution = resolve_pair(0, directives[0], 1, directives[1])
        counts["reciprocity_violations"] += len(resolution.violations)
        orders = {directives[0].passage_order, directives[1].passage_order}
        counts["non_complementary"] += orders in ({"leader"}, {"follower"})
    return counts


@pytest.mark.parametrize("swap", [False, True], ids=["default", "keep_right_instead"])
def test_the_seed_database_never_gives_a_pair_inconsistent_directives(swap):
    active = DATABASE.activate("default", enable={"keep_right_head_on": 1}, disable=["keep_left_head_on"]) if swap else DATABASE.activate("default")
    counts = consistency_counts(active)
    assert counts["reciprocity_violations"] == 0 and counts["non_complementary"] == 0
    assert counts["matched"] > 300 and counts["ties"] > 0  # the property was exercised, ties included
    assert set(counts["classes"]) <= set(ENCOUNTER_CLASSES) and len(counts["classes"]) == len(ENCOUNTER_CLASSES)
