"""The perception record: what it contains, what the visibility settings hide, and the
guarantee that a neighbour's task never appears in one."""

from __future__ import annotations

import json
import math
import re

import pytest

from helpers import crowd, run_avoidance
from negsim.avoidance.perception import (
    ENVIRONMENT_FIELDS,
    NEVER_OBSERVABLE,
    OBSERVER_FIELDS,
    PERCEPTION_FIELDS,
    PERCEPTION_SCHEMA_VERSION,
    default_visibility,
    environment_features,
    perceive,
    time_to_collision,
    visible_attributes,
)
from negsim.configutil import PACKAGE_ROOT
from negsim.core.geometry import Rect
from negsim.negotiation import prompts
from negsim.personas.schema import ATTRIBUTES

# Distinctive values, so that a leak can be found by searching the serialised record.
OBSERVER = {"age": 31, "gender": "female", "backstory": "OBSERVER-BACKSTORY", "task": "OBSERVER-TASK"}
NEIGHBOUR = {"age": 83, "gender": "nonbinary", "backstory": "NEIGHBOUR-BACKSTORY", "task": "NEIGHBOUR-TASK"}
ATTRIBUTE_MAP = {0: OBSERVER, 1: NEIGHBOUR}
ALL_VISIBLE = {name: True for name in (*ATTRIBUTES, "speed", "size")}
NOTHING_VISIBLE = {name: False for name in ALL_VISIBLE}


def head_on_world():
    """The wide corridor at its start: agent 0 at (-8, 0) walking east, agent 1 at (8, 0) walking west."""
    spec = crowd("wide_corridor_head_on")
    return spec, spec.build_world()


def record(visibility=None, attributes=ATTRIBUTE_MAP, observer=0, neighbour=1):
    spec, world = head_on_world()
    return perceive(
        7, 0.7, world.agents[observer], world.agents[neighbour], world.obstacles,
        default_visibility() if visibility is None else visibility, attributes, 1.3,
    )


# --- contents --------------------------------------------------------------------------------


def test_record_of_a_head_on_neighbour():
    r = record()
    assert (r.schema_version, r.step, r.time_s, r.observer_id, r.neighbour_id) == (PERCEPTION_SCHEMA_VERSION, 7, 0.7, 0, 1)
    assert r.relative_position_m == (16.0, 0.0) and r.distance_m == 16.0
    assert r.bearing_rad == pytest.approx(0.0)  # straight ahead
    assert r.relative_velocity_mps == pytest.approx((-2.6, 0.0))  # the neighbour's velocity minus the observer's
    assert r.closing_speed_mps == pytest.approx(2.6)
    assert r.time_to_collision_s == pytest.approx((16.0 - 0.5) / 2.6)
    assert r.neighbour_radius_m == 0.25 and r.neighbour_speed_mps == pytest.approx(1.3)
    assert r.neighbour_heading_rad == pytest.approx(math.pi)
    assert abs(r.neighbour_heading_relative_rad) == pytest.approx(math.pi)  # coming the other way
    assert r.observer.radius_m == 0.25 and r.observer.speed_mps == pytest.approx(1.3)
    assert r.observer.heading_rad == pytest.approx(0.0) and r.observer.preferred_speed_mps == 1.3


def test_bearing_is_positive_to_the_left_and_follows_the_observers_heading():
    spec = crowd("open_crossing")  # agent 0 at (-8, 0) walking east, agent 1 at (0, -8) walking north
    world = spec.build_world()
    seen_by_0 = perceive(0, 0.0, world.agents[0], world.agents[1], (), ALL_VISIBLE, {}, 1.3)
    seen_by_1 = perceive(0, 0.0, world.agents[1], world.agents[0], (), ALL_VISIBLE, {}, 1.3)
    assert seen_by_0.bearing_rad == pytest.approx(-math.pi / 4)  # ahead and to the right
    assert seen_by_1.bearing_rad == pytest.approx(math.pi / 4)  # ahead and to the left
    assert seen_by_0.neighbour_heading_relative_rad == pytest.approx(math.pi / 2)
    assert seen_by_0.distance_m == pytest.approx(math.hypot(8, 8))


def test_time_to_collision():
    assert time_to_collision((10.0, 0.0), (-2.0, 0.0), 1.0) == pytest.approx(4.5)
    assert time_to_collision((10.0, 0.0), (2.0, 0.0), 1.0) is None  # moving apart
    assert time_to_collision((10.0, 0.0), (0.0, 0.0), 1.0) is None  # not moving relative to each other
    assert time_to_collision((10.0, 2.0), (-2.0, 0.0), 1.0) is None  # passes 2 m to the side
    assert time_to_collision((10.0, 0.6), (-2.0, 0.0), 1.0) == pytest.approx((10.0 - 0.8) / 2.0)  # a glancing hit
    assert time_to_collision((0.5, 0.0), (1.0, 0.0), 1.0) == 0.0  # already touching


def test_environment_in_a_corridor():
    """The wide corridor is 1.75 m wide, with walls at y = +0.875 and -0.875."""
    spec, world = head_on_world()
    env = environment_features(world.agents[0], world.obstacles, [], 12.5)
    assert env.free_width_left_m == pytest.approx(0.875) and env.free_width_right_m == pytest.approx(0.875)
    assert env.free_width_m == pytest.approx(1.75)
    assert env.nearest_wall_distance_m == pytest.approx(0.875)
    assert env.single_file_ahead_m is None
    # 0.3 m to the left of the centre line, the split changes and the total does not.
    spec = crowd("wide_corridor_head_on", geometry={"lateral_offsets": [0.3, 0.0]})
    env = environment_features(spec.build_world().agents[0], spec.obstacles, [], 12.5)
    assert env.free_width_left_m == pytest.approx(0.575) and env.free_width_right_m == pytest.approx(1.175)
    assert env.free_width_m == pytest.approx(1.75) and env.nearest_wall_distance_m == pytest.approx(0.575)


def test_environment_in_open_space_has_no_walls():
    spec = crowd("open_crossing")
    env = environment_features(spec.build_world().agents[0], spec.obstacles, [], 12.5)
    assert (env.nearest_wall_distance_m, env.free_width_m, env.free_width_left_m, env.free_width_right_m) == (None,) * 4


def test_a_wall_beyond_the_environment_range_does_not_count_toward_the_width():
    far = [Rect(-50, 30, 50, 31), Rect(-50, -1.5, 50, -1.0)]
    spec, world = head_on_world()
    env = environment_features(world.agents[0], far, [], 12.5)
    assert env.free_width_left_m is None and env.free_width_right_m == pytest.approx(1.0)
    assert env.free_width_m is None  # no wall on one side: the passage has no width
    assert env.nearest_wall_distance_m == pytest.approx(1.0)


def test_distance_to_a_single_file_segment_ahead():
    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    agent = world.agents[0]
    (index, entry_s, exit_s), = agent.spec.single_file_stretches
    intervals = [(entry_s, exit_s)]
    assert environment_features(agent, spec.obstacles, intervals, 12.5).single_file_ahead_m == pytest.approx(entry_s)
    assert entry_s == pytest.approx(7.01, abs=0.02)  # starts 7 m from the mouth, along a slightly longer path
    agent.path_s = 0.5 * (entry_s + exit_s)
    assert environment_features(agent, spec.obstacles, intervals, 12.5).single_file_ahead_m == 0.0  # inside it
    agent.path_s = exit_s + 0.1
    assert environment_features(agent, spec.obstacles, intervals, 12.5).single_file_ahead_m is None  # behind it


# --- visibility ------------------------------------------------------------------------------


def test_default_visibility_is_that_of_issue_24():
    assert default_visibility() == prompts.default_visibility()
    # Issue #32 added the ethnic_group switch, off by default: a group is seen only where a run says so.
    assert default_visibility() == {
        "age": True, "gender": True, "backstory": False, "task": False, "ethnic_group": False, "speed": True, "size": True,
    }


def test_by_default_age_and_gender_are_seen_and_nothing_else_of_the_persona():
    r = record()
    assert r.neighbour_attributes == {"age": 83, "gender": "nonbinary"}
    assert r.observer.attributes == {"age": 31, "gender": "female"}  # what the agent knows of itself


@pytest.mark.parametrize("hidden", ["age", "gender"])
def test_a_hidden_attribute_is_not_in_the_record(hidden):
    r = record({**default_visibility(), hidden: False})
    assert hidden not in r.neighbour_attributes
    assert str(NEIGHBOUR[hidden]) not in json.dumps(r.as_dict()["neighbour_attributes"])
    other = "gender" if hidden == "age" else "age"
    assert r.neighbour_attributes == {other: NEIGHBOUR[other]}  # the other one is unaffected


def test_backstory_follows_its_visibility_setting():
    assert "backstory" not in record().neighbour_attributes
    assert record({**default_visibility(), "backstory": True}).neighbour_attributes["backstory"] == "NEIGHBOUR-BACKSTORY"


@pytest.mark.parametrize("visibility", [None, ALL_VISIBLE, NOTHING_VISIBLE, {**ALL_VISIBLE, "age": False}])
def test_the_task_is_never_in_a_record_whatever_the_settings(visibility):
    """Not the neighbour's, and not the observer's own: with every switch on, including the
    one for the task itself, neither task string is anywhere in the serialised record."""
    r = record(visibility)
    text = json.dumps(r.as_dict())
    assert "NEIGHBOUR-TASK" not in text and "OBSERVER-TASK" not in text
    assert "task" not in r.neighbour_attributes and "task" not in r.observer.attributes
    assert '"task"' not in text


def test_never_observable_is_the_task():
    assert NEVER_OBSERVABLE == {"task"}
    assert visible_attributes(NEIGHBOUR, {"task": True, "age": True}) == {"age": 83}
    assert visible_attributes(None, ALL_VISIBLE) == {} and visible_attributes({}, ALL_VISIBLE) == {}


def test_with_nothing_visible_only_position_and_heading_remain():
    r = record(NOTHING_VISIBLE)
    assert r.neighbour_attributes == {}
    assert r.neighbour_radius_m is None and r.neighbour_speed_mps is None
    assert r.relative_velocity_mps is None and r.closing_speed_mps is None and r.time_to_collision_s is None
    assert r.distance_m == 16.0 and r.neighbour_heading_rad == pytest.approx(math.pi)
    serialised = r.as_dict()
    hidden = ("neighbour_radius_m", "neighbour_speed_mps", "relative_velocity_mps", "closing_speed_mps", "time_to_collision_s")
    assert all(key in serialised and serialised[key] is None for key in hidden)  # None, never left out
    for value in ("83", "nonbinary", "NEIGHBOUR"):
        assert value not in json.dumps(serialised["neighbour_attributes"])


def test_hiding_size_hides_the_time_to_collision_but_not_the_speed():
    r = record({**ALL_VISIBLE, "size": False})
    assert r.neighbour_radius_m is None and r.time_to_collision_s is None  # it cannot be worked out without the size
    assert r.neighbour_speed_mps == pytest.approx(1.3) and r.closing_speed_mps == pytest.approx(2.6)
    r = record({**ALL_VISIBLE, "speed": False})
    assert r.neighbour_speed_mps is None and r.relative_velocity_mps is None and r.time_to_collision_s is None
    assert r.neighbour_radius_m == 0.25


def test_an_agent_without_a_persona_has_no_attributes():
    r = record(attributes={})
    assert r.neighbour_attributes == {} and r.observer.attributes == {}
    r = record(attributes={1: NEIGHBOUR})
    assert r.neighbour_attributes == {"age": 83, "gender": "nonbinary"} and r.observer.attributes == {}


def test_hidden_attributes_never_reach_a_record_in_a_whole_run():
    """Every record built during a run, under every visibility setting tried: nothing that
    was switched off, and never a task."""
    spec = crowd("wide_corridor_head_on")
    for visibility in (default_visibility(), NOTHING_VISIBLE, {**default_visibility(), "age": False}, ALL_VISIBLE):
        result = run_avoidance(spec, attributes=ATTRIBUTE_MAP, visibility=visibility)
        assert len(result.interactions) == 2  # each agent perceives the other once
        for interaction in result.interactions:
            data = interaction.record.as_dict()
            text = json.dumps(data)
            assert "TASK" not in text and '"task"' not in text
            for name in ATTRIBUTES:
                if name in NEVER_OBSERVABLE or not visibility.get(name, False):
                    assert name not in data["neighbour_attributes"], (name, visibility)
            assert set(data["neighbour_attributes"]) <= {name for name, on in visibility.items() if on}


# --- the record is a versioned, documented contract ---------------------------------------------


def test_the_serialised_record_has_exactly_the_declared_fields():
    data = record().as_dict()
    assert tuple(data) == PERCEPTION_FIELDS
    assert tuple(data["observer"]) == OBSERVER_FIELDS and tuple(data["environment"]) == ENVIRONMENT_FIELDS
    json.dumps(data)  # and it is plain JSON


def test_the_perception_document_names_every_field_and_the_version():
    document = (PACKAGE_ROOT / "docs" / "perception.md").read_text(encoding="utf-8")
    assert f"# The perception record, version {PERCEPTION_SCHEMA_VERSION}" in document
    for field in (*PERCEPTION_FIELDS, *OBSERVER_FIELDS, *ENVIRONMENT_FIELDS):
        pattern = r"(?<![A-Za-z0-9_])" + re.escape(field) + r"(?![A-Za-z0-9_])"
        assert re.search(pattern, document), f"'{field}' is not described in docs/perception.md"


# --- version 3: where each is in a passage, and the group (issue #32) --------------------------


def in_the_bottleneck(x0: float, x1: float, speed: float = 1.3):
    """The bottleneck's two agents moved inside its 4 m segment (x from -2 to 2), facing each other."""
    from negsim.core.state import Pose

    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    a, b = world.agents
    a.pose, a.velocity = Pose(x0, 0.0, 0.0), (speed, 0.0)
    b.pose, b.velocity = Pose(x1, 0.0, math.pi), (-speed, 0.0)
    return spec, world


def passage_of(spec, world, observer=0, neighbour=1, visibility=None, attributes=None):
    return perceive(
        3, 0.3, world.agents[observer], world.agents[neighbour], world.obstacles,
        default_visibility() if visibility is None else visibility, attributes or {}, 1.3,
        segments=spec.single_file_segments,
    )


def test_segment_position_is_measured_from_the_ends_toward_and_away_from_the_other():
    from negsim.avoidance.perception import segment_position

    passage = Rect(-2.0, -0.4, 2.0, 0.4)
    # Agent at x = 0.7 meeting one at 1.3: the end ahead is the east end (1.3 m), the end behind the west (2.7 m).
    assert segment_position((0.7, 0.0), (1.3, 0.0), passage) == (True, pytest.approx(2.7), pytest.approx(1.3), pytest.approx(2.7))
    assert segment_position((1.3, 0.0), (0.7, 0.0), passage) == (True, pytest.approx(0.7), pytest.approx(3.3), pytest.approx(0.7))
    assert segment_position((2.5, 0.0), (0.7, 0.0), passage) == (False, None, None, None)  # outside: no distances
    assert segment_position((2.0, 0.0), (0.7, 0.0), passage) == (True, 0.0, 4.0, 0.0)  # on the end: inside
    assert segment_position((0.5, 0.1), (0.5, -0.1), passage) == (True, None, None, None)  # level: no ahead or behind
    upright = Rect(-0.4, -2.0, 0.4, 2.0)  # a passage along y
    assert segment_position((0.0, -1.5), (0.0, 1.0), upright) == (True, pytest.approx(0.5), pytest.approx(3.5), pytest.approx(0.5))


def test_both_agents_records_carry_the_same_passage_fields():
    spec, world = in_the_bottleneck(0.7, 1.3)
    first, second = passage_of(spec, world, 0, 1), passage_of(spec, world, 1, 0)
    assert first.pair.encounter_class == "single_file_segment" and first.pair is not None
    mine, theirs = first.as_dict(), second.as_dict()
    for name in ("in_segment", "segment_distance_travelled", "segment_distance_ahead", "segment_distance_behind"):
        assert mine["observer"][name] == theirs[f"neighbour_{name}"]
        assert mine[f"neighbour_{name}"] == theirs["observer"][name]
    assert mine["observer"]["in_segment"] is True and mine["observer"]["segment_distance_travelled"] == pytest.approx(2.7)
    assert mine["neighbour_segment_distance_travelled"] == pytest.approx(0.7)
    assert mine["observer"]["segment_distance_ahead"] == pytest.approx(1.3) and mine["neighbour_segment_distance_ahead"] == pytest.approx(3.3)
    # travelled is, in a meeting, the distance to the end behind
    assert mine["observer"]["segment_distance_travelled"] == mine["observer"]["segment_distance_behind"]


def test_passage_fields_are_null_outside_the_passage_and_without_one():
    spec, world = in_the_bottleneck(-3.5, 1.3)  # agent 0 still in the wide part, facing the segment
    record_ = passage_of(spec, world).as_dict()
    assert record_["pair"]["encounter_class"] == "single_file_segment"
    assert record_["observer"]["in_segment"] is False
    assert [record_["observer"][name] for name in ("segment_distance_travelled", "segment_distance_ahead", "segment_distance_behind")] == [None, None, None]
    assert record_["neighbour_in_segment"] is True and record_["neighbour_segment_distance_travelled"] == pytest.approx(0.7)
    hidden = passage_of(spec, world, visibility={**default_visibility(), "size": False}).as_dict()  # no class: no passage
    assert hidden["observer"]["in_segment"] is None and hidden["neighbour_in_segment"] is None
    open_space = record().as_dict()  # the wide corridor has no segment at all
    assert open_space["observer"]["in_segment"] is None and open_space["neighbour_segment_distance_ahead"] is None


def test_an_agent_knows_its_own_group_and_sees_the_others_only_when_switched_on():
    groups = {0: {"age": 31, "gender": "female", "ethnic_group": "Pellund"}, 1: {"age": 83, "gender": "male", "ethnic_group": "Kestrop"}}
    hidden = record(attributes=groups)
    assert hidden.observer.attributes == {"age": 31, "gender": "female", "ethnic_group": "Pellund"}
    assert "ethnic_group" not in hidden.neighbour_attributes and default_visibility()["ethnic_group"] is False
    shown = record(visibility={**default_visibility(), "ethnic_group": True}, attributes=groups)
    assert shown.neighbour_attributes == {"age": 83, "gender": "male", "ethnic_group": "Kestrop"}
    alone = record(visibility={**default_visibility(), "ethnic_group": True, "age": False, "gender": False}, attributes=groups)
    assert alone.neighbour_attributes == {"ethnic_group": "Kestrop"}  # independent of age and gender
    assert "Kestrop" not in json.dumps(record(attributes=groups).as_dict())


def test_the_group_is_flagged_as_not_readable_by_rules():
    from negsim.personas.schema import NOT_RULE_REFERENCEABLE

    assert NOT_RULE_REFERENCEABLE == {"ethnic_group"}
    assert ATTRIBUTES["ethnic_group"].observable is False and ATTRIBUTES["ethnic_group"].rule_referenceable is False


def test_a_version_2_record_reads_back_with_its_passage_fields_missing():
    from negsim.avoidance.perception import FIELDS_BY_VERSION, PerceptionRecord

    spec, world = in_the_bottleneck(0.7, 1.3)
    current = passage_of(spec, world).as_dict()
    assert PerceptionRecord.from_dict(current).as_dict() == current  # version 3 reads back as it was written
    old = {key: value for key, value in current.items() if key in FIELDS_BY_VERSION[2]["record"]}
    old["observer"] = {key: value for key, value in current["observer"].items() if key in FIELDS_BY_VERSION[2]["observer"]}
    old["schema_version"] = 2
    back = PerceptionRecord.from_dict(old)
    assert back.observer.in_segment is None and back.neighbour_segment == dict.fromkeys(back.neighbour_segment)
    assert back.pair.time_to_segment_s == PerceptionRecord.from_dict(current).pair.time_to_segment_s
    with pytest.raises(ValueError, match="version 2 or 3"):
        PerceptionRecord.from_dict({**current, "schema_version": 1})
