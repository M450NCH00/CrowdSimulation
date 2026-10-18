"""Issue #32, Part 1.2: a person's group may be seen, but no rule may read it.

The loader refuses any rule that names it (``protected_attribute``), and, independently of
the loader, no execution path from a rule reaches it: no field a rule can read is the group or
is derived from it, and no snapshot a rule is evaluated on holds it."""

from __future__ import annotations

import json
import math
import random

import pytest

from helpers import crowd
from negsim.avoidance.perception import default_visibility, pair_features, perceive
from negsim.personas.groups import DEFAULT_GROUP_LABELS
from negsim.personas.schema import ATTRIBUTES, NOT_RULE_REFERENCEABLE
from negsim.rules import RuleDatabase
from negsim.rules.database import RULE_DB_ROOT, load_validator
from negsim.rules.errors import RuleError
from negsim.rules.fields import AGENT_FIELDS, CONDITION_PREFIXES, PAIR_FIELDS, ROLE_PREFIXES, protected_reference, resolve
from negsim.rules.model import parse_rule, protected_part
from negsim.rules.provider import RuleDatabaseProvider
from negsim.rules.snapshot import snapshot_of_pair, snapshot_of_record

SEEN = {**default_visibility(), "ethnic_group": True}
VALIDATOR = load_validator(RULE_DB_ROOT)


def rule(**body):
    base = {
        "schema_version": 2, "rule_id": "probe", "version": 1, "status": "test_seed",
        "provenance": {"source_type": "hand_written", "source_ref": "test", "created_at": "2026-10-16", "author": "test", "notes": "", "validation_evidence": []},
        "encounter": "head_on", "when": {"all": []}, "roles": "symmetric", "directive": {"both": {"clearance_margin": 0.1}}, "priority": 10,
    }
    return {**base, **body}


@pytest.mark.parametrize(
    "reference",
    ["pair.ethnic_group", "either.ethnic_group", "both.ethnic_group", "agent.ethnic_group", "ethnic_group",
     "pair.same_ethnic_group", "pair.ethnicity_difference", "either.ethnicity", "agent.Ethnic_Group", "either.pellund"],
)
def test_every_way_of_naming_the_group_is_protected_whatever_the_prefix(reference):
    for prefixes in (CONDITION_PREFIXES, ROLE_PREFIXES):
        with pytest.raises(RuleError) as caught:
            resolve(reference, "where", prefixes)
        assert caught.value.category == "protected_attribute", reference


def test_the_words_of_a_session_are_protected_and_ordinary_words_are_not():
    assert protected_reference("pair.same_group") is None  # not protected by itself ...
    assert protected_reference("pair.same_group", ("ethnic", "group")) == "group"  # ... but where groups were introduced so
    assert protected_reference("either.community", ("community",)) == "community"
    assert protected_reference("Kestrop") == "Kestrop" and protected_reference("kestrop") == "Kestrop"
    for ordinary in ("either.age", "pair.distance_m", "agent.speed_mps", "yielder", "no_match", "female"):
        assert protected_reference(ordinary) is None


@pytest.mark.parametrize(
    "body, where",
    [
        ({"when": {"all": [{"field": "either.ethnic_group", "op": "==", "value": "Pellund"}]}}, "when"),
        ({"when": {"any": [{"field": "pair.distance_m", "op": "<", "value": 3, "unit": "m"}, {"field": "pair.same_ethnic_group", "op": "==", "value": True}]}}, "when"),
        ({"roles": {"by": {"field": "agent.ethnic_group", "order": "ascending", "assign": ["a", "b"], "tie": "no_match"}}, "directive": {"a": {}, "b": {}}}, "roles"),
        ({"roles": {"by": {"field": "agent.age", "order": "ascending", "assign": ["a", "b"], "tie": "agent.ethnic_group"}}, "directive": {"a": {}, "b": {}}}, "roles"),  # the tie policy
        ({"roles": {"by": {"field": "agent.age", "order": "ascending", "assign": ["a", "b"], "tie": "no_match", "tie_within": "same ethnic group"}}, "directive": {"a": {}, "b": {}}}, "roles"),
        ({"roles": {"by": {"field": "agent.age", "order": "ascending", "assign": ["a", "b"]}}, "directive": {"a": {}, "b": {}}, "when": {"all": [{"field": "either.gender", "op": "==", "value": "Dremmik"}]}}, "when"),
    ],
)
def test_the_loader_refuses_the_group_in_a_condition_a_role_assignment_and_a_tie_policy(body, where):
    with pytest.raises(RuleError) as caught:
        parse_rule(rule(**body), VALIDATOR, "probe")
    assert caught.value.category == "protected_attribute" and f"probe.{where}" in str(caught.value)


def test_protected_is_decided_before_anything_else():
    # No tie policy, an unknown key and shares that sum below 1: still protected_attribute, as data.
    body = {
        "roles": {"by": {"field": "agent.ethnic_group", "order": "ascending", "assign": ["a", "b"]}},
        "directive": {"a": {"responsibility_share": 0.1}, "b": {"responsibility_share": 0.1}}, "colour": "red",
    }
    with pytest.raises(RuleError) as caught:
        parse_rule(rule(**body), VALIDATOR)
    assert caught.value.category == "protected_attribute"
    assert protected_part(rule(**body)) == ("roles.by.field", "agent.ethnic_group", "ethnic")


def test_the_session_can_add_words_and_a_rule_without_them_still_loads():
    body = {"when": {"all": [{"field": "pair.distance_m", "op": "<", "value": 5, "unit": "m"}]}, "description": "a group of two"}
    parse_rule(rule(**body), VALIDATOR)  # "group" outside the condition and roles is not read
    with pytest.raises(RuleError, match="protected_attribute"):
        parse_rule(rule(roles={"by": {"field": "agent.age", "order": "ascending", "assign": ["in_group", "out_group"], "tie": "no_match"}},
                        directive={"in_group": {}, "out_group": {}}), VALIDATOR, terms=("group",))


# --- no execution path reaches it ----------------------------------------------------------------------


def test_no_field_a_rule_can_read_is_the_group_or_derived_from_it():
    assert NOT_RULE_REFERENCEABLE == {"ethnic_group"}
    for table in (PAIR_FIELDS, AGENT_FIELDS):
        for name, spec in table.items():
            text = f"{name} {spec.source} {spec.meaning}".lower()
            assert "ethnic" not in text and "group" not in text, name
            assert "ethnic_group" not in spec.needs, name
    assert all(spec.rule_referenceable for name, spec in ATTRIBUTES.items() if name != "ethnic_group")


def groups_of(rng):
    return {
        agent: {"age": rng.randint(5, 95), "gender": rng.choice(["female", "male", "nonbinary"]), "ethnic_group": rng.choice(DEFAULT_GROUP_LABELS)}
        for agent in (0, 1)
    }


def test_no_snapshot_holds_the_group_even_when_both_see_it():
    """Both ways of building a snapshot, on random states of the bottleneck with each agent's
    group set and visible: neither the attribute nor any label appears in what a rule reads."""
    rng = random.Random(32)
    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    a, b = world.agents
    for trial in range(200):
        for agent in (a, b):
            agent.pose = type(agent.pose)(rng.uniform(-9, 9), rng.uniform(-0.6, 0.6), rng.uniform(-math.pi, math.pi))
            speed = rng.uniform(0, 2)
            agent.velocity = (speed * math.cos(agent.pose.theta), speed * math.sin(agent.pose.theta))
            agent.speed = speed
        attributes = groups_of(rng)
        features = pair_features(a, b, world.obstacles, SEEN, attributes, 12.5, spec.single_file_segments)
        shared = json.dumps(snapshot_of_pair(trial, 0.0, a, b, features, SEEN, attributes).as_dict()).lower()
        record = perceive(trial, 0.0, a, b, world.obstacles, SEEN, attributes, 1.3, environment_range=12.5, pair=features)
        assert record.neighbour_attributes["ethnic_group"] == attributes[1]["ethnic_group"]  # it is seen ...
        own = json.dumps(snapshot_of_record(record, SEEN).as_dict()).lower()
        for text in (shared, own):  # ... and never read
            assert "ethnic" not in text and not any(label.lower() in text for label in DEFAULT_GROUP_LABELS)


def test_whether_a_rule_matches_never_depends_on_the_group():
    """Every seed rule, on random pairs, matches the same with and without groups, seen or not."""
    database = RuleDatabase.load(RULE_DB_ROOT)
    active = database.activate("default")
    provider = RuleDatabaseProvider(active, SEEN)
    rng = random.Random(33)
    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    a, b = world.agents
    checked = 0
    for trial in range(300):
        for agent in (a, b):
            agent.pose = type(agent.pose)(rng.uniform(-9, 9), rng.uniform(-0.6, 0.6), rng.uniform(-math.pi, math.pi))
            speed = rng.uniform(0, 2)
            agent.velocity = (speed * math.cos(agent.pose.theta), speed * math.sin(agent.pose.theta))
            agent.speed = speed
        with_groups = groups_of(rng)
        without = {agent: {k: v for k, v in values.items() if k != "ethnic_group"} for agent, values in with_groups.items()}
        answers = []
        for attributes, visibility in ((with_groups, SEEN), (without, SEEN), (with_groups, default_visibility())):
            features = pair_features(a, b, world.obstacles, visibility, attributes, 12.5, spec.single_file_segments)
            record = perceive(trial, 0.0, a, b, world.obstacles, visibility, attributes, 1.3, environment_range=12.5, pair=features)
            answers.append(provider.directive(record))
        assert answers[0] == answers[1] == answers[2]
        checked += 1
    assert checked == 300
