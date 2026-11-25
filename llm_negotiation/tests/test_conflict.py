"""Conflict zones, detection, time to the conflict region, roles, and the follower speed bound."""

from __future__ import annotations

import math
import random

import pytest

from negsim.conflict import (
    Conflict,
    DesiredPathDetector,
    HeadingRayDetector,
    Role,
    RoleSource,
    ZoneView,
    crossing_zone_views,
    decide_roles,
    edge_quantities,
    intervals_overlap,
    is_social_minigame,
    make_detector,
    occupancy_interval,
    path_zone_interval,
    strategy1_leader,
    time_to_clear,
    time_to_region,
)
from negsim.control import Arbiter, follower_bound_from_views, follower_speed_bound
from negsim.core import AgentRuntime, AgentSpec, Polyline, Pose, World
from negsim.core.geometry import heading_vec, point_segment_distance


def agent(agent_id, x, y, heading_deg, goal=None, radius=0.1, max_speed=0.3, path=None) -> AgentSpec:
    theta = math.radians(heading_deg)
    if path is None:
        ux, uy = heading_vec(theta)
        path = Polyline([(x, y), goal or (x + 10 * ux, y + 10 * uy)])
    return AgentSpec(
        agent_id=agent_id, radius=radius, max_speed=max_speed, max_turn_rate=1.0, start=Pose(x, y, theta),
        goal=path.points[-1], path=path, side="test", region_entry_s=0.0, region_exit_s=0.0, initial_speed=max_speed,
    )


def runtime(spec: AgentSpec) -> AgentRuntime:
    return AgentRuntime(spec=spec, pose=spec.start, speed=spec.initial_speed)


def conflict_of(view_0: ZoneView, view_1: ZoneView) -> Conflict:
    return Conflict((0, 1), {0: view_0, 1: view_1})


# --- zones ---------------------------------------------------------------------------------


def test_crossing_zone_at_a_right_angle():
    # South-to-north and west-to-east, both 2 m from the crossing: the intersection scenario.
    view_i, view_j, point = crossing_zone_views((0, -2), math.pi / 2, (-2, 0), 0.0, clearance=0.25)
    assert point == pytest.approx((0.0, 0.0))
    assert (view_i.d_in, view_i.d_out) == pytest.approx((1.75, 2.25))
    assert (view_j.d_in, view_j.d_out) == pytest.approx((1.75, 2.25))


@pytest.mark.parametrize("angle_deg", [15, 26.3, 45, 90, 135, 160])
def test_auto_zone_keeps_a_waiting_agent_clear_of_the_other_path(angle_deg):
    """The property the zone exists for (docs/derivations.md, section 4).

    A centre standing at the entry of its zone is exactly ``clearance`` from the other
    agent's line, at any crossing angle.
    """
    clearance, phi = 0.25, math.radians(angle_deg)
    view_i, _, point = crossing_zone_views((-3, 0), 0.0, (-3 * math.cos(phi), -3 * math.sin(phi)), phi, clearance)
    entry = (point[0] - view_i.length / 2, point[1])  # agent i travels along +x through the crossing
    far, near = (-50 * math.cos(phi), -50 * math.sin(phi)), (50 * math.cos(phi), 50 * math.sin(phi))
    assert point_segment_distance(entry, far, near) == pytest.approx(clearance)


def test_a_fixed_quarter_metre_zone_is_too_short_for_the_doorways_shallow_crossing():
    """Why 'auto' exists. The GameChat repository uses 0.25 m whatever the angle
    (mpc_cbf.py:237-239). At the doorway's 26-degree crossing, an agent waiting 0.25 m
    short of the crossing point is only 0.11 m from the other agent's line: less than two
    0.1 m radii, so a leader passing by would hit it."""
    phi = math.radians(26.3)
    waiting_point = (-0.25, 0.0)
    far, near = (-50 * math.cos(phi), -50 * math.sin(phi)), (50 * math.cos(phi), 50 * math.sin(phi))
    assert point_segment_distance(waiting_point, far, near) == pytest.approx(0.25 * math.sin(phi))
    assert point_segment_distance(waiting_point, far, near) < 0.2


def test_fixed_half_length_overrides_the_automatic_one():
    view_i, _, _ = crossing_zone_views((0, -2), math.pi / 2, (-2, 0), 0.0, clearance=0.25, half_length=0.1)
    assert (view_i.d_in, view_i.d_out) == pytest.approx((1.9, 2.1))


def test_parallel_headings_have_no_crossing_zone():
    assert crossing_zone_views((0, 0), 0.0, (0, 1), 0.0, clearance=0.25) is None


@pytest.mark.parametrize("angle_deg", [30, 60, 90, 120])
def test_path_zone_agrees_with_the_closed_form_for_straight_crossing_paths(angle_deg):
    """Two independent implementations of the same zone must agree."""
    clearance, phi = 0.3, math.radians(angle_deg)
    path_i = Polyline([(-4.0, 0.0), (4.0, 0.0)])
    path_j = Polyline([(-4 * math.cos(phi), -4 * math.sin(phi)), (4 * math.cos(phi), 4 * math.sin(phi))])
    s_in, s_out = path_zone_interval(path_i, path_j, clearance)
    half = clearance / math.sin(phi)
    assert (s_in, s_out) == pytest.approx((4.0 - half, 4.0 + half), abs=1e-4)


def test_path_zone_of_paths_that_stay_apart_is_none():
    assert path_zone_interval(Polyline([(0, 0), (5, 0)]), Polyline([(0, 1), (5, 1)]), clearance=0.5) is None


def test_path_zone_of_a_head_on_corridor_covers_the_shared_stretch_and_the_run_out():
    # Two paths that share the x axis between -1 and 1 and peel apart at 45 degrees beyond it.
    east = Polyline([(-2, -1), (-1, 0), (1, 0), (2, -1)])
    west = Polyline([(2, 1), (1, 0), (-1, 0), (-2, 1)])
    s_in, s_out = path_zone_interval(east, west, clearance=0.5)
    leg = math.sqrt(2.0)
    # The legs are at right angles, so they are 0.5 apart 0.5 from the corner.
    assert s_in == pytest.approx(leg - 0.5, abs=1e-4)
    assert s_out == pytest.approx(leg + 2.0 + 0.5, abs=1e-4)


def test_edge_quantities_restate_a_centre_zone_as_d_L_l():
    d, region_length, body_length = edge_quantities(ZoneView(1.75, 2.25), radius=0.1)
    assert (d, region_length, body_length) == pytest.approx((1.75, 0.3, 0.2))
    assert d + region_length + body_length == pytest.approx(2.25)  # = the centre's distance to the zone exit


# --- detection -----------------------------------------------------------------------------


def test_heading_ray_detector_finds_a_crossing_conflict():
    south, west = runtime(agent(0, 0, -2, 90)), runtime(agent(1, -2, 0, 0))
    conflict = HeadingRayDetector(safety_margin=0.05).zone(south, west)
    assert conflict is not None and conflict.live
    assert conflict.point == pytest.approx((0.0, 0.0))
    assert conflict.views[0].d_in == pytest.approx(1.75)  # (0.1 + 0.1 + 0.05) / sin 90 = 0.25


def test_heading_ray_detector_uses_each_pairs_radii():
    south, west = runtime(agent(0, 0, -2, 90, radius=0.2)), runtime(agent(1, -2, 0, 0, radius=0.1))
    conflict = HeadingRayDetector(safety_margin=0.0).zone(south, west)
    assert conflict.views[0].length == pytest.approx(0.6)  # 2 * (0.2 + 0.1)


def test_heading_ray_detector_no_conflict_when_not_crossing():
    parallel = HeadingRayDetector(0.05).zone(runtime(agent(0, 0, 0, 0)), runtime(agent(1, 0, 1, 0)))
    assert parallel is None
    head_on = HeadingRayDetector(0.05).zone(runtime(agent(0, -2, 0, 0)), runtime(agent(1, 2, 0, 180)))
    assert head_on is None  # collinear rays: the case the hallway needs the path detector for
    moving_apart = HeadingRayDetector(0.05).zone(runtime(agent(0, 0, 1, 90)), runtime(agent(1, 1, 0, 0)))
    assert moving_apart is None


def test_heading_ray_conflict_stays_live_until_the_leader_is_out_of_the_zone():
    detector = HeadingRayDetector(safety_margin=0.05)
    west = runtime(agent(1, -2, 0, 0))
    just_past = detector.zone(runtime(agent(0, 0, 0.1, 90)), west)  # 0.1 m beyond the crossing point
    assert just_past is not None and just_past.live and just_past.views[0].inside
    clear = detector.zone(runtime(agent(0, 0, 0.3, 90)), west)  # beyond the 0.25 m half-length
    assert clear is not None and not clear.live and clear.views[0].cleared


def test_desired_path_detector_handles_the_head_on_case():
    east = Polyline([(-2, -1), (-1, 0), (1, 0), (2, -1)])
    west = Polyline([(2, 1), (1, 0), (-1, 0), (-2, 1)])
    a = runtime(agent(0, -2, -1, 45, path=east))
    b = runtime(agent(1, 2, 1, 225, path=west))
    conflict = DesiredPathDetector(safety_margin=0.3).zone(a, b)  # clearance 0.1 + 0.1 + 0.3 = 0.5
    assert conflict is not None and conflict.live
    assert conflict.views[0].d_in == pytest.approx(math.sqrt(2.0) - 0.5, abs=1e-4)
    a.path_s = 1.0
    assert DesiredPathDetector(0.3).zone(a, b).views[0].d_in == pytest.approx(math.sqrt(2.0) - 1.5, abs=1e-4)


def test_make_detector():
    assert isinstance(make_detector("heading_ray", 0.05, 0.25), HeadingRayDetector)
    assert isinstance(make_detector("desired_path", 0.05), DesiredPathDetector)
    with pytest.raises(ValueError):
        make_detector("desired_path", 0.05, zone_half_length=0.25)
    with pytest.raises(ValueError):
        make_detector("telepathy", 0.05)


# --- time to the conflict region -------------------------------------------------------------


def test_time_to_region_and_time_to_clear():
    view = ZoneView(d_in=1.5, d_out=2.1)
    assert time_to_region(view, 0.3) == pytest.approx(5.0)
    assert time_to_clear(view, 0.3) == pytest.approx(7.0)
    assert occupancy_interval(view, 0.3) == pytest.approx((5.0, 7.0))


def test_time_to_region_is_zero_inside_and_infinite_when_stationary():
    assert time_to_region(ZoneView(-0.2, 0.4), 0.3) == 0.0
    assert time_to_clear(ZoneView(-0.6, -0.1), 0.3) == 0.0
    assert time_to_region(ZoneView(1.0, 2.0), 0.0) == math.inf


def test_intervals_overlap_but_touching_does_not_count():
    assert intervals_overlap((0.0, 2.0), (1.0, 3.0))
    assert not intervals_overlap((0.0, 2.0), (2.5, 3.0))
    assert not intervals_overlap((0.0, 2.0), (2.0, 3.0))  # arrives as the other leaves


def test_social_minigame_needs_overlapping_occupancy():
    speeds = {0: 0.3, 1: 0.3}
    assert is_social_minigame(conflict_of(ZoneView(1.75, 2.25), ZoneView(1.75, 2.25)), speeds)
    # One agent is 3 m further back: it arrives long after the other has left. No conflict.
    assert not is_social_minigame(conflict_of(ZoneView(1.75, 2.25), ZoneView(4.75, 5.25)), speeds)
    # ...unless it is fast enough to arrive while the other is still inside (5.9 s < 7.5 s).
    assert is_social_minigame(conflict_of(ZoneView(1.75, 2.25), ZoneView(4.75, 5.25)), {0: 0.3, 1: 0.8})
    assert not is_social_minigame(conflict_of(ZoneView(-0.6, -0.1), ZoneView(0.2, 0.7)), speeds)  # one has left


# --- roles ---------------------------------------------------------------------------------


def test_strategy1_gives_the_lead_to_the_shorter_time_to_region():
    speeds = {0: 0.3, 1: 0.3}
    assert strategy1_leader(conflict_of(ZoneView(1.5, 2.0), ZoneView(1.75, 2.25)), speeds) == 0
    assert strategy1_leader(conflict_of(ZoneView(1.75, 2.25), ZoneView(1.5, 2.0)), speeds) == 1


def test_strategy1_compares_times_not_distances():
    # Agent 1 is further away but three times as fast.
    assert strategy1_leader(conflict_of(ZoneView(1.5, 2.0), ZoneView(3.0, 3.5)), {0: 0.3, 1: 0.9}) == 1


def test_strategy1_reports_a_tie_and_decide_roles_breaks_it():
    tie, speeds = conflict_of(ZoneView(1.75, 2.25), ZoneView(1.75, 2.25)), {0: 0.3, 1: 0.3}
    assert strategy1_leader(tie, speeds) is None
    decision = decide_roles(tie, speeds)
    assert (decision.leader_id, decision.follower_id, decision.tie_broken) == (0, 1, True)
    assert decision.source is RoleSource.STRATEGY1
    assert decision.role_of(0) is Role.LEADER and decision.role_of(1) is Role.FOLLOWER


def test_random_tie_break_is_seeded_and_can_be_latched():
    tie, speeds = conflict_of(ZoneView(1.75, 2.25), ZoneView(1.75, 2.25)), {0: 0.3, 1: 0.3}
    draws = [decide_roles(tie, speeds, tie_break="random", rng=random.Random(seed)).leader_id for seed in range(20)]
    assert set(draws) == {0, 1}
    assert draws == [decide_roles(tie, speeds, tie_break="random", rng=random.Random(seed)).leader_id for seed in range(20)]
    assert decide_roles(tie, speeds, tie_break="random", rng=random.Random(0), tie_winner=1).leader_id == 1
    with pytest.raises(ValueError):
        decide_roles(tie, speeds, tie_break="random")
    with pytest.raises(ValueError):
        decide_roles(tie, speeds, tie_break="coin")


def test_a_negotiated_leader_overrides_strategy1():
    closer_is_0 = conflict_of(ZoneView(1.5, 2.0), ZoneView(1.75, 2.25))
    decision = decide_roles(closer_is_0, {0: 0.3, 1: 0.3}, negotiated_leader=1)
    assert (decision.leader_id, decision.source) == (1, RoleSource.NEGOTIATED)


def test_an_agent_already_inside_the_zone_keeps_the_lead():
    # Agent 0 is inside; the agents then agree that agent 1 should go first. Too late.
    agent_0_inside = conflict_of(ZoneView(-0.1, 0.4), ZoneView(0.8, 1.3))
    decision = decide_roles(agent_0_inside, {0: 0.3, 1: 0.3}, negotiated_leader=1)
    assert (decision.leader_id, decision.source) == (0, RoleSource.PHYSICAL_PRECEDENCE)
    assert decide_roles(agent_0_inside, {0: 0.3, 1: 0.3}, negotiated_leader=0).source is RoleSource.NEGOTIATED
    assert decide_roles(agent_0_inside, {0: 0.3, 1: 0.3}).source is RoleSource.STRATEGY1


def test_negotiated_leader_must_be_one_of_the_pair():
    with pytest.raises(ValueError):
        decide_roles(conflict_of(ZoneView(1, 2), ZoneView(1, 2)), {0: 0.3, 1: 0.3}, negotiated_leader=7)


# --- the follower speed bound ----------------------------------------------------------------


@pytest.mark.parametrize("d_i, d_j, length, v_max", [(2.0, 2.0, 0.2, 0.3), (2.25, 2.0, 0.2, 0.3), (1.0, 3.0, 0.5, 1.4)])
def test_follower_speed_reduces_to_the_papers_formula(d_i, d_j, length, v_max):
    """With L = 0, l_j = l and v_j = v_max the bound is d_i * v_max / (l + d_j)
    (arXiv:2503.12333v1, Sec IV-D)."""
    paper = d_i * v_max / (length + d_j)
    assert follower_speed_bound(d_i, d_j, v_j=v_max, l_j=length, L=0.0, v_i_max=10.0) == pytest.approx(paper)


def test_follower_arrives_exactly_when_the_leader_has_cleared():
    d_i, d_j, v_j, l_j, region = 1.8, 2.4, 0.3, 0.2, 0.6
    v_i = follower_speed_bound(d_i, d_j, v_j, l_j, region, v_i_max=10.0)
    assert d_i / v_i == pytest.approx((d_j + region + l_j) / v_j)


def test_a_longer_region_or_a_longer_leader_slows_the_follower_more():
    base = follower_speed_bound(2.0, 2.0, 0.3, 0.2, 0.0, 10.0)
    assert follower_speed_bound(2.0, 2.0, 0.3, 0.2, 1.0, 10.0) < base
    assert follower_speed_bound(2.0, 2.0, 0.3, 0.6, 0.0, 10.0) < base


def test_follower_speed_scales_with_the_leaders_speed_and_is_capped_at_its_own_maximum():
    assert follower_speed_bound(2.0, 2.0, 0.6, 0.2, 0.0, 10.0) == pytest.approx(2 * follower_speed_bound(2.0, 2.0, 0.3, 0.2, 0.0, 10.0))
    assert follower_speed_bound(5.0, 1.0, 0.3, 0.2, 0.0, v_i_max=0.25) == 0.25


def test_follower_waits_at_the_entry_and_is_released_once_the_leader_is_clear():
    assert follower_speed_bound(0.0, 0.5, 0.3, 0.2, 0.3, 0.3) == 0.0
    assert follower_speed_bound(-0.05, 0.5, 0.3, 0.2, 0.3, 0.3) == 0.0
    assert follower_speed_bound(0.0, -0.6, 0.3, 0.2, 0.3, 0.3) == 0.3  # leader's trailing edge is out


def test_follower_speed_rejects_negative_speeds():
    with pytest.raises(ValueError):
        follower_speed_bound(1.0, 1.0, -0.3, 0.2, 0.0, 0.3)


def test_bound_from_zone_views_equals_the_formula_on_edge_quantities():
    follower, leader, radius = ZoneView(1.4, 2.0), ZoneView(1.75, 2.25), 0.1
    d_j, region, body = edge_quantities(leader, radius)
    expected = follower_speed_bound(follower.d_in, d_j, 0.3, body, region, 0.3)
    assert follower_bound_from_views(follower, leader, radius, 0.3, 0.3) == pytest.approx(expected)
    assert expected == pytest.approx(1.4 * 0.3 / 2.25)


# --- the arbiter -----------------------------------------------------------------------------


def crossing_world() -> World:
    return World([agent(0, 0, -2, 90, goal=(0, 1)), agent(1, -2, 0, 0, goal=(1, 0))], [], dt=0.2, goal_tolerance=0.1)


def test_arbiter_bounds_only_the_follower():
    decisions = Arbiter(HeadingRayDetector(0.05)).resolve(crossing_world())
    assert decisions[0].role is Role.LEADER and decisions[0].speed_bound == pytest.approx(0.3)
    assert decisions[1].role is Role.FOLLOWER
    assert decisions[1].speed_bound == pytest.approx(1.75 * 0.3 / 2.25)
    assert decisions[1].in_conflict and decisions[1].zone_d_in == pytest.approx(1.75)


def test_arbiter_honours_a_negotiated_leader():
    decisions = Arbiter(HeadingRayDetector(0.05)).resolve(crossing_world(), {(0, 1): 1})
    assert decisions[1].role is Role.LEADER and decisions[0].role is Role.FOLLOWER
    assert decisions[0].role_source is RoleSource.NEGOTIATED
    assert decisions[0].speed_bound < 0.3 and decisions[1].speed_bound == pytest.approx(0.3)


def test_arbiter_policy_none_detects_but_does_not_slow_anyone():
    decisions = Arbiter(HeadingRayDetector(0.05), policy="none").resolve(crossing_world())
    assert decisions[1].in_conflict and decisions[1].speed_bound == pytest.approx(0.3)
    with pytest.raises(ValueError):
        Arbiter(HeadingRayDetector(0.05), policy="pray")


def test_arbiter_ignores_agents_that_cannot_see_each_other():
    decisions = Arbiter(HeadingRayDetector(0.05)).resolve(crossing_world(), visible=lambda i, j: False)
    assert not decisions[0].in_conflict and decisions[1].speed_bound == pytest.approx(0.3)


def test_arbiter_keeps_the_same_leader_after_a_random_tie_break():
    for seed in range(6):
        arbiter = Arbiter(HeadingRayDetector(0.05), tie_break="random", rng=random.Random(seed))
        world = crossing_world()
        first = arbiter.resolve(world)
        leader = 0 if first[0].role is Role.LEADER else 1
        assert all(arbiter.resolve(world)[leader].role is Role.LEADER for _ in range(5))


def test_arbiter_handles_three_agents_pairwise():
    world = World(
        [agent(0, 0, -2, 90, goal=(0, 1)), agent(1, -2, 0, 0, goal=(1, 0)), agent(2, 5, 5, 0, goal=(9, 5))],
        [], dt=0.2, goal_tolerance=0.1,
    )
    decisions = Arbiter(HeadingRayDetector(0.05)).resolve(world)
    assert decisions[1].role is Role.FOLLOWER and not decisions[2].in_conflict
