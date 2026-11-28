"""The pair-level fields of the perception record (version 2, issue #28): what both agents of
a pair can tell about the two of them, computed so that the two get the same values."""

from __future__ import annotations

import math
import random
from types import SimpleNamespace

import pytest

from helpers import crowd, free_space, run_avoidance
from negsim.avoidance.perception import (
    ENCOUNTER_CROSSING,
    ENCOUNTER_HEAD_ON,
    ENCOUNTER_NONE,
    ENCOUNTER_OVERTAKING,
    ENCOUNTER_SINGLE_FILE,
    HEAD_ON_MIN_DIFFERENCE_RAD,
    OVERTAKING_MAX_DIFFERENCE_RAD,
    PAIR_FIELDS,
    corridor_width_between,
    default_visibility,
    pair_features,
)
from negsim.core.geometry import Rect
from negsim.core.state import Pose

VISIBLE = default_visibility()
AGES = {0: {"age": 25, "gender": "female"}, 1: {"age": 70, "gender": "male"}}


def features(spec, world=None, visibility=VISIBLE, attributes=AGES, swap=False):
    world = world or spec.build_world()
    a, b = world.agents[0], world.agents[1]
    if swap:
        a, b = b, a
    radius = max(agent.spec.sensing_radius for agent in world.agents)
    return pair_features(a, b, world.obstacles, visibility, attributes, radius, spec.single_file_segments)


def place(agent, x, y, heading, speed):
    """Put an agent at (x, y), moving along ``heading`` at ``speed``."""
    agent.pose = Pose(x, y, heading)
    agent.velocity = (speed * math.cos(heading), speed * math.sin(heading))
    agent.speed = speed


def two_in_open_ground():
    return free_space([{"start": (0.0, 0.0), "goal": (20.0, 0.0)}, {"start": (5.0, 0.0), "goal": (25.0, 0.0)}])


# --- the encounter classes of the shipped scenarios ------------------------------------------------


def test_the_shipped_scenarios_start_in_the_class_their_names_say():
    assert features(crowd("wide_corridor_head_on")).encounter_class == ENCOUNTER_HEAD_ON
    assert features(crowd("open_crossing")).encounter_class == ENCOUNTER_CROSSING
    assert features(crowd("overtaking")).encounter_class == ENCOUNTER_OVERTAKING
    for flow in ("opposing", "merging"):
        found = features(crowd("corridor_to_bottleneck", geometry={"flow": flow}))
        assert (found.encounter_class, found.single_file_segment) == (ENCOUNTER_SINGLE_FILE, "bottleneck"), flow


def test_two_agents_that_are_not_approaching_are_no_encounter():
    spec = two_in_open_ground()
    world = spec.build_world()
    place(world.agents[0], 0.0, 0.0, math.pi, 1.3)  # walking away from each other
    place(world.agents[1], 5.0, 0.0, 0.0, 1.3)
    assert features(spec, world).encounter_class == ENCOUNTER_NONE
    place(world.agents[0], 0.0, 0.0, 0.0, 0.0)  # both standing still
    place(world.agents[1], 5.0, 0.0, math.pi, 0.0)
    assert features(spec, world).encounter_class == ENCOUNTER_NONE
    place(world.agents[0], 0.0, 0.0, 0.0, 1.3)  # walking the same way at the same speed: not closing
    place(world.agents[1], 5.0, 0.0, 0.0, 1.3)
    assert features(spec, world).encounter_class == ENCOUNTER_NONE


@pytest.mark.parametrize(
    "difference_deg, expected",
    [(0, ENCOUNTER_OVERTAKING), (59, ENCOUNTER_OVERTAKING), (61, ENCOUNTER_CROSSING), (90, ENCOUNTER_CROSSING),
     (119, ENCOUNTER_CROSSING), (121, ENCOUNTER_HEAD_ON), (180, ENCOUNTER_HEAD_ON)],
)
def test_the_class_of_an_approaching_pair_follows_the_heading_difference(difference_deg, expected):
    """Agent 1 stands 5 m ahead of agent 0 and walks toward it, its direction of travel
    turned ``difference_deg`` from agent 0's. Agent 0 walks fast enough that they close."""
    spec = two_in_open_ground()
    world = spec.build_world()
    place(world.agents[0], 0.0, 0.0, 0.0, 2.0)
    place(world.agents[1], 5.0, 0.0, math.radians(difference_deg), 0.5)
    found = features(spec, world)
    assert found.heading_difference_rad == pytest.approx(math.radians(difference_deg))
    assert found.encounter_class == expected
    assert OVERTAKING_MAX_DIFFERENCE_RAD == pytest.approx(math.radians(60))
    assert HEAD_ON_MIN_DIFFERENCE_RAD == pytest.approx(math.radians(120))


def test_a_pair_is_single_file_only_while_both_face_the_segment():
    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    found = features(spec, world)
    assert found.encounter_class == ENCOUNTER_SINGLE_FILE
    # Agent 0 is through: east of the segment and walking away from it.
    place(world.agents[0], 3.5, -0.2, 0.0, 1.3)
    assert features(spec, world).encounter_class != ENCOUNTER_SINGLE_FILE
    # Agent 0 inside the segment counts as facing it, whichever way it moves.
    place(world.agents[0], 0.0, 0.0, math.pi / 2, 0.0)
    assert features(spec, world).encounter_class == ENCOUNTER_SINGLE_FILE


def test_a_segment_wide_enough_for_the_pair_is_not_single_file_for_it():
    """The arbiter's test: a segment counts only if it is narrower than the two diameters
    together. The shipped scenario refuses a segment the pair could pass in, so the same
    free space is declared here with other widths."""
    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    a, b = world.agents
    rect = spec.single_file_segments[0].rect
    for width, expected in ((0.99, ENCOUNTER_SINGLE_FILE), (1.0, ENCOUNTER_HEAD_ON), (1.5, ENCOUNTER_HEAD_ON)):
        segment = SimpleNamespace(name="declared", rect=rect, width=width)
        found = pair_features(a, b, world.obstacles, VISIBLE, AGES, 12.5, [segment])
        assert found.encounter_class == expected, width


# --- times to the segment ----------------------------------------------------------------------------


def test_time_to_segment_is_distance_over_speed_zero_inside_and_none_standing_still():
    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    found = features(spec, world)
    # Each starts 9 m from the middle; the segment's free space begins 2 m from the middle.
    assert found.time_to_segment_s == pytest.approx((7.0 / 1.3, 7.0 / 1.3))
    place(world.agents[0], -1.0, 0.0, 0.0, 1.0)
    place(world.agents[1], 4.0, 0.0, math.pi, 0.0)
    found = features(spec, world)
    assert found.time_to_segment_s == (0.0, None)
    assert found.time_to_segment_of(0) == 0.0 and found.time_to_segment_of(1) is None


def test_times_to_segment_are_none_outside_the_single_file_class():
    assert features(crowd("wide_corridor_head_on")).time_to_segment_s == (None, None)


# --- the corridor width ----------------------------------------------------------------------------


#: The two agents of the bottleneck start at (-9, -0.4) and (9, 0.4). The line between them
#: is tilted, and the width is measured at right angles to it, so the 0.8 m segment
#: measures a little more than 0.8 m across that line.
BOTTLENECK_ACROSS_THE_LINE = 0.8 / math.cos(math.atan2(0.8, 18.0))


def test_corridor_width_between_two_agents():
    assert features(crowd("wide_corridor_head_on")).min_corridor_width_m == pytest.approx(1.75)
    assert features(crowd("corridor_to_bottleneck")).min_corridor_width_m == pytest.approx(BOTTLENECK_ACROSS_THE_LINE)
    assert BOTTLENECK_ACROSS_THE_LINE == pytest.approx(0.80079, abs=1e-5)
    flow = crowd("bidirectional_flow")
    world = flow.build_world()
    place(world.agents[0], -5.0, 0.3, 0.0, 1.3)  # two agents on one line along the 4 m corridor
    place(world.agents[1], 5.0, 0.3, math.pi, 1.3)
    assert features(flow, world).min_corridor_width_m == pytest.approx(4.0)


def test_in_open_ground_the_width_is_as_far_as_can_be_seen():
    assert features(crowd("open_crossing")).min_corridor_width_m == pytest.approx(2 * 12.5)
    assert corridor_width_between((0.0, 0.0), (3.0, 4.0), (), 5.0) == pytest.approx(10.0)


def test_a_line_through_a_wall_has_width_zero_and_a_short_line_is_still_measured():
    wall = Rect(1.0, -1.0, 2.0, 1.0)
    assert corridor_width_between((0.0, 0.0), (3.0, 0.0), [wall], 10.0) == 0.0
    corridor = [Rect(-10.0, 0.5, 10.0, 1.0), Rect(-10.0, -1.0, 10.0, -0.5)]
    assert corridor_width_between((0.0, 0.0), (0.0, 0.0), corridor, 10.0) == pytest.approx(1.0)  # same point


# --- what the visibility settings hide -----------------------------------------------------------------


def test_hiding_speed_or_size_hides_the_class_and_the_times():
    spec = crowd("corridor_to_bottleneck")
    for hidden in ("speed", "size"):
        found = features(spec, visibility={**VISIBLE, hidden: False})
        assert (found.encounter_class, found.single_file_segment, found.time_to_segment_s) == (None, None, (None, None))
        assert found.min_corridor_width_m == pytest.approx(BOTTLENECK_ACROSS_THE_LINE)  # walls are always perceived


def test_the_age_difference_needs_age_visible_and_both_ages():
    spec = crowd("wide_corridor_head_on")
    assert features(spec).age_difference_years == 45
    assert features(spec, visibility={**VISIBLE, "age": False}).age_difference_years is None
    assert features(spec, attributes={1: AGES[1]}).age_difference_years is None
    assert features(spec, attributes={}).age_difference_years is None


# --- the same values for both agents ---------------------------------------------------------------------


def test_the_pair_fields_are_the_same_whichever_agent_is_named_first():
    rng = random.Random(28)
    spec = crowd("corridor_to_bottleneck")
    world = spec.build_world()
    for _ in range(500):
        for agent in world.agents:
            place(agent, rng.uniform(-9, 9), rng.uniform(-0.6, 0.6), rng.uniform(-math.pi, math.pi), rng.uniform(0, 2))
        assert features(spec, world) == features(spec, world, swap=True)


def test_both_records_of_a_pair_share_one_pair_block_in_a_run():
    result = run_avoidance(crowd("wide_corridor_head_on"), attributes=AGES)
    first, second = result.interactions[:2]
    assert (first.observer_id, second.observer_id) == (0, 1) and first.start_step == second.start_step
    assert first.record.pair is second.record.pair
    assert tuple(first.record.as_dict()["pair"]) == PAIR_FIELDS
    assert first.record.observer.time_to_segment_s is None and first.record.neighbour_time_to_segment_s is None
