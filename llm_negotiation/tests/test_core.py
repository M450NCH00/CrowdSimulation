"""Geometry, unicycle dynamics and the world."""

from __future__ import annotations

import math

import pytest

from negsim.core import (
    AgentSpec,
    Control,
    Polyline,
    Pose,
    Rect,
    World,
    clip_control,
    line_intersection,
    ray_intersection,
    unicycle_step,
    wrap_angle,
)


def make_agent(agent_id: int, start: Pose, goal, radius=0.1, max_speed=0.3) -> AgentSpec:
    path = Polyline([start.xy, goal])
    return AgentSpec(
        agent_id=agent_id, radius=radius, max_speed=max_speed, max_turn_rate=1.0, start=start,
        goal=goal, path=path, side="test", region_entry_s=0.0, region_exit_s=0.0, initial_speed=max_speed,
    )


# --- dynamics ----------------------------------------------------------------------------


def test_unicycle_step_straight_ahead():
    pose = unicycle_step(Pose(1.0, 2.0, 0.0), Control(v=0.3, omega=0.0), dt=0.2)
    assert pose == pytest.approx(Pose(1.06, 2.0, 0.0))


def test_unicycle_step_uses_the_heading_at_the_start_of_the_step():
    # Forward Euler (eq. 2 of the paper): position moves along the old heading, then the heading turns.
    pose = unicycle_step(Pose(0.0, 0.0, math.pi / 2), Control(v=0.3, omega=1.0), dt=0.2)
    assert pose.x == pytest.approx(0.0, abs=1e-12)
    assert pose.y == pytest.approx(0.06)
    assert pose.theta == pytest.approx(math.pi / 2 + 0.2)


def test_unicycle_step_turning_on_the_spot_does_not_move():
    pose = unicycle_step(Pose(0.5, -0.5, 0.3), Control(v=0.0, omega=1.0), dt=0.2)
    assert (pose.x, pose.y) == (0.5, -0.5)
    assert pose.theta == pytest.approx(0.5)


def test_unicycle_step_wraps_the_heading():
    pose = unicycle_step(Pose(0.0, 0.0, math.pi - 0.05), Control(v=0.0, omega=1.0), dt=0.2)
    assert pose.theta == pytest.approx(-math.pi + 0.15)


def test_clip_control_limits_speed_and_turn_rate_and_forbids_reversing():
    assert clip_control(Control(0.9, 5.0), 0.3, 1.0) == Control(0.3, 1.0)
    assert clip_control(Control(-0.2, -5.0), 0.3, 1.0) == Control(0.0, -1.0)
    assert clip_control(Control(0.1, 0.4), 0.3, 1.0) == Control(0.1, 0.4)


# --- geometry ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "angle, expected",
    [(0.0, 0.0), (math.pi, math.pi), (-math.pi, math.pi), (3 * math.pi / 2, -math.pi / 2), (7.0, 7.0 - 2 * math.pi)],
)
def test_wrap_angle(angle, expected):
    assert wrap_angle(angle) == pytest.approx(expected)


def test_line_intersection_of_perpendicular_lines():
    point, t, s = line_intersection((0.0, -2.0), math.pi / 2, (-2.0, 0.0), 0.0)
    assert point == pytest.approx((0.0, 0.0))
    assert (t, s) == pytest.approx((2.0, 2.0))


def test_line_intersection_reports_a_point_behind_with_a_negative_distance():
    point, t, s = line_intersection((0.0, 1.0), math.pi / 2, (-2.0, 0.0), 0.0)
    assert point == pytest.approx((0.0, 0.0))
    assert t == pytest.approx(-1.0) and s == pytest.approx(2.0)


def test_parallel_and_collinear_lines_do_not_intersect():
    assert line_intersection((0.0, 0.0), 0.0, (0.0, 1.0), 0.0) is None
    assert line_intersection((0.0, 0.0), 0.0, (5.0, 0.0), math.pi) is None  # head-on, same line


def test_ray_intersection_requires_the_point_ahead_of_both():
    assert ray_intersection((0.0, -2.0), math.pi / 2, (-2.0, 0.0), 0.0) is not None
    assert ray_intersection((0.0, 1.0), math.pi / 2, (-2.0, 0.0), 0.0) is None  # already past
    assert ray_intersection((0.0, -2.0), -math.pi / 2, (-2.0, 0.0), 0.0) is None  # heading away


def test_polyline_arc_length_and_points():
    path = Polyline([(0.0, 0.0), (3.0, 0.0), (3.0, 4.0)])
    assert path.length == pytest.approx(7.0)
    assert path.point_at(1.5) == pytest.approx((1.5, 0.0))
    assert path.point_at(5.0) == pytest.approx((3.0, 2.0))
    assert path.point_at(99.0) == pytest.approx((3.0, 4.0))
    assert path.heading_at(1.0) == pytest.approx(0.0)
    assert path.heading_at(5.0) == pytest.approx(math.pi / 2)


def test_polyline_projection_and_distance():
    path = Polyline([(0.0, 0.0), (3.0, 0.0), (3.0, 4.0)])
    assert path.project((1.0, 0.5)) == pytest.approx(1.0)
    assert path.distance_to((1.0, 0.5)) == pytest.approx(0.5)
    assert path.project((3.5, 2.0)) == pytest.approx(5.0)
    assert path.distance_to((-1.0, 0.0)) == pytest.approx(1.0)


def test_polyline_projection_never_goes_backwards():
    path = Polyline([(0.0, 0.0), (3.0, 0.0)])
    assert path.project((1.0, 0.0), s_min=2.0) == pytest.approx(2.0)


def test_polyline_rejects_degenerate_paths():
    with pytest.raises(ValueError):
        Polyline([(0.0, 0.0)])
    with pytest.raises(ValueError):
        Polyline([(0.0, 0.0), (0.0, 0.0)])


def test_rect_distance_and_segment_test():
    wall = Rect(-0.05, 0.2, 0.05, 1.5)
    assert wall.distance_to((0.0, 0.5)) == 0.0
    assert wall.distance_to((0.0, 0.0)) == pytest.approx(0.2)
    assert wall.distance_to((0.35, 0.2)) == pytest.approx(0.3)
    assert wall.intersects_segment((-1.0, 0.5), (1.0, 0.5))
    assert not wall.intersects_segment((-1.0, 0.0), (1.0, 0.0))
    assert not wall.intersects_segment((-1.0, 0.5), (-0.5, 0.5))


# --- world -------------------------------------------------------------------------------


def test_world_moves_all_agents_from_the_same_instant():
    a = make_agent(0, Pose(0.0, 0.0, 0.0), (5.0, 0.0))
    b = make_agent(1, Pose(0.0, 1.0, 0.0), (5.0, 1.0))
    world = World([a, b], [], dt=0.2, goal_tolerance=0.1)
    world.step({0: Control(0.3, 0.0), 1: Control(0.1, 0.0)})
    assert world.time == pytest.approx(0.2)
    assert world.agents[0].pose.x == pytest.approx(0.06)
    assert world.agents[1].pose.x == pytest.approx(0.02)
    assert world.agents[0].speed == pytest.approx(0.3)
    assert world.agents[0].path_s == pytest.approx(0.06)


def test_world_clips_controls_to_each_agents_own_limits():
    slow = make_agent(0, Pose(0.0, 0.0, 0.0), (5.0, 0.0), max_speed=0.1)
    fast = make_agent(1, Pose(0.0, 1.0, 0.0), (5.0, 1.0), max_speed=0.3)
    world = World([slow, fast], [], dt=1.0, goal_tolerance=0.1)
    applied = world.step({0: Control(9.0, 0.0), 1: Control(9.0, 0.0)})
    assert (applied[0].v, applied[1].v) == (0.1, 0.3)


def test_world_records_goal_time_and_then_keeps_the_agent_still():
    agent = make_agent(0, Pose(0.0, 0.0, 0.0), (0.15, 0.0))
    world = World([agent], [], dt=0.2, goal_tolerance=0.1)
    world.step({0: Control(0.3, 0.0)})
    assert world.agents[0].goal_time == pytest.approx(0.2) and world.all_done
    x = world.agents[0].pose.x
    world.step({0: Control(0.3, 0.0)})
    assert world.agents[0].pose.x == x


def test_world_detects_overlapping_agents_and_walls():
    a = make_agent(0, Pose(0.0, 0.0, 0.0), (5.0, 0.0))
    b = make_agent(1, Pose(0.19, 0.0, 0.0), (5.0, 1.0))
    c = make_agent(2, Pose(3.0, 0.0, 0.0), (5.0, 2.0))
    world = World([a, b, c], [Rect(3.05, -1.0, 3.5, 1.0)], dt=0.2, goal_tolerance=0.1)
    assert world.agent_collisions() == [(0, 1)]
    assert world.wall_collisions() == [2]


def test_touching_is_not_a_collision():
    a = make_agent(0, Pose(0.0, 0.0, 0.0), (5.0, 0.0))
    b = make_agent(1, Pose(0.2, 0.0, 0.0), (5.0, 1.0))
    assert World([a, b], [], 0.2, 0.1).agent_collisions() == []


def test_visibility_depends_on_range_and_optionally_on_walls():
    a = make_agent(0, Pose(-1.0, 0.0, 0.0), (5.0, 0.0))
    b = make_agent(1, Pose(1.0, 0.0, 0.0), (5.0, 1.0))
    world = World([a, b], [Rect(-0.1, -1.0, 0.1, 1.0)], 0.2, 0.1)
    assert not world.mutually_visible(0, 1)
    assert world.mutually_visible(0, 1, walls_block_sight=False)
    assert not world.mutually_visible(0, 1, max_range=1.5, walls_block_sight=False)


def test_world_holds_more_than_two_agents():
    agents = [make_agent(k, Pose(0.0, float(k), 0.0), (5.0, float(k))) for k in range(3)]
    world = World(agents, [], 0.2, 0.1)
    world.step({k: Control(0.3, 0.0) for k in range(3)})
    assert [agent.pose.x for agent in world.agents] == pytest.approx([0.06] * 3)


def test_agent_ids_must_be_consecutive():
    with pytest.raises(ValueError):
        World([make_agent(1, Pose(0.0, 0.0, 0.0), (1.0, 0.0))], [], 0.2, 0.1)
