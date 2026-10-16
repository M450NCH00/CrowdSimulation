"""Issue #32, Part 2: two people who meet inside a single-file passage.

The scenarios that start them there, their backing speeds, and (below) the back-up directive."""

from __future__ import annotations

import pytest

from helpers import crowd
from negsim.configutil import ConfigError
from negsim.scenarios.crowd_base import DEFAULT_BACKING_SPEED

# --- the scenarios --------------------------------------------------------------------------------


@pytest.mark.parametrize("name, travelled", [("passage_meet_middle_v1", (1.7, 1.7)), ("passage_meet_with_speeds_v1", (2.0, 1.4))])
def test_the_two_start_inside_the_passage_where_they_meet(name, travelled):
    spec = crowd(name)
    assert spec.scenario_type == "passage_meeting" and len(spec.agents) == 2
    (segment,) = spec.single_file_segments
    assert (segment.rect.xmin, segment.rect.xmax, segment.width) == (-2.0, 2.0, 0.8)
    east, west = spec.agents
    assert east.start.x == pytest.approx(-2.0 + travelled[0]) and west.start.x == pytest.approx(2.0 - travelled[1])
    assert east.start.y == west.start.y == 0.0
    assert west.start.x - east.start.x - east.radius - west.radius == pytest.approx(0.1)  # at the meeting point, 0.1 m apart
    assert east.start.theta == pytest.approx(0.0) and abs(west.start.theta) == pytest.approx(3.141592653589793)  # facing each other
    for agent in (east, west):
        assert agent.path.points[0] == (agent.start.x, agent.start.y)  # the path starts where the agent is
        (stretch,) = agent.single_file_stretches
        assert stretch[1] == 0.0  # it starts inside the segment
    assert east.goal == (9.0, -0.4) and west.goal == (-9.0, 0.4)  # out of the far end, to its own side


def test_the_variants_are_set_by_the_distances_walked_in():
    asymmetric = crowd("passage_meet_middle_v1", geometry={"travelled": [2.7, 0.7]})
    east, west = asymmetric.agents
    assert (east.start.x, west.start.x) == (pytest.approx(0.7), pytest.approx(1.3))


def test_backing_speeds_and_the_slow_backer():
    middle = crowd("passage_meet_middle_v1")
    assert [agent.backing_speed_mps for agent in middle.agents] == [0.92, 0.92]
    speeds = crowd("passage_meet_with_speeds_v1")
    fast, slow = speeds.agents
    assert (fast.agent_type, fast.max_speed, fast.backing_speed_mps, fast.preferred_speed) == ("pedestrian", 2.0, 0.92, 1.3)
    assert (slow.agent_type, slow.max_speed, slow.backing_speed_mps, slow.preferred_speed) == ("slow_backer", 1.4, 0.43, 1.10)
    described = speeds.as_dict()
    assert described["agent_types"]["slow_backer"]["backing_speed"] == 0.43 and described["agents"][1]["backing_speed_mps"] == 0.43


def test_a_scenario_that_does_not_set_a_backing_speed_resolves_as_before():
    spec = crowd("corridor_to_bottleneck")
    described = spec.as_dict()
    assert "backing_speed" not in described["agent_types"]["pedestrian"] and "backing_speed_mps" not in described["agents"][0]
    assert spec.agents[0].backing_speed is None and spec.agents[0].backing_speed_mps == DEFAULT_BACKING_SPEED == 0.92
    slow = crowd("corridor_to_bottleneck", agent_types={"pedestrian": {"max_speed": 0.8, "preferred_speed": 0.7}})
    assert slow.agents[0].backing_speed_mps == 0.8  # never above its maximum speed


@pytest.mark.parametrize(
    "geometry, message",
    [
        ({"travelled": [4.0, 0.5]}, "outside the passage"),
        ({"travelled": [0.0, 1.0]}, "outside the passage"),
        ({"travelled": [2.5, 1.5]}, "add up to the passage's length"),
        ({"travelled": [1.9, 1.9]}, "overlap at their starting positions"),
        ({"travelled": [1.7]}, "a list of 2 numbers"),
        ({"passage_width": 1.75}, "passage_width must be less than approach_width"),
        ({"passage_width": 1.2}, "could pass each other"),
        ({"exit_setback": 0.5}, "merge_distance < exit_setback"),
    ],
)
def test_a_passage_that_cannot_be_is_refused(geometry, message):
    with pytest.raises(ConfigError, match=message):
        crowd("passage_meet_middle_v1", geometry=geometry)


def test_a_backing_speed_above_the_maximum_is_refused():
    with pytest.raises(ConfigError, match="backing_speed 2.5 exceeds max_speed 2.0"):
        crowd("passage_meet_middle_v1", agent_types={"pedestrian": {"backing_speed": 2.5}})
