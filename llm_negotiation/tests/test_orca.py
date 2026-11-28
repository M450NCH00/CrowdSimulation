"""ORCA's geometry and its linear programs: half-planes against hand-computed cases, the
two-dimensional program and its fallback against a brute-force solver, and the walls."""

from __future__ import annotations

import itertools
import math
import random

import pytest

from negsim.avoidance.lp import LPResult, linear_program_2, solve, violation
from negsim.avoidance.orca import (
    REGION_APEX,
    REGION_ARC,
    REGION_LEFT_LEG,
    REGION_OVERLAP,
    REGION_RIGHT_LEG,
    agent_half_plane,
    wall_half_plane,
)
from negsim.avoidance.perception import time_to_collision
from negsim.core.geometry import Rect

DT = 0.1


def allowed(line, velocity, tol=1e-9) -> bool:
    return violation(line, velocity) <= tol


def approx(values, expected, tol=1e-9):
    assert len(values) == len(expected)
    for value, want in zip(values, expected):
        assert value == pytest.approx(want, abs=tol), (values, expected)


# --- the half-plane for a pair of agents, by hand ---------------------------------------------
#
# A is at the origin and B at p. The cut-off disc of the velocity obstacle is centred on
# p / tau and has radius R / tau. Each expected value below is worked out in the comment.


def test_arc_when_the_pair_is_not_on_a_collision_course():
    """p = (10, 0), R = 1, tau = 2: the cut-off disc is centred (5, 0) with radius 0.5, so
    its nearest point to v = (1, 0) is (4.5, 0), 3.5 away. A may use half of that room:
    its x velocity may rise to 1 + 1.75 = 2.75."""
    plane = agent_half_plane((10, 0), (1, 0), (1, 0), 1.0, 2.0, DT)
    assert plane.region == REGION_ARC and not plane.on_collision_course
    approx(plane.normal, (-1.0, 0.0))
    assert plane.margin == pytest.approx(-3.5)
    approx(plane.line, (2.75, 0.0, 0.0, 1.0))
    assert allowed(plane.line, (2.75, 3.0)) and allowed(plane.line, (-5.0, 0.0)) and not allowed(plane.line, (2.76, 0.0))


@pytest.mark.parametrize("share, limit", [(0.5, 4.65), (1.0, 4.5), (0.0, 4.8), (0.25, 4.725)])
def test_arc_on_a_collision_course_moves_the_line_by_the_agents_share(share, limit):
    """Same pair with v = (4.8, 0): 0.3 inside the disc's nearest point (4.5, 0). A has to
    make up its share of the 0.3, so its x velocity may be at most 4.8 - share * 0.3."""
    plane = agent_half_plane((10, 0), (4.8, 0), (4.8, 0), 1.0, 2.0, DT, share=share)
    assert plane.region == REGION_ARC and plane.on_collision_course
    assert plane.margin == pytest.approx(0.3)
    approx(plane.line, (limit, 0.0, 0.0, 1.0))


def test_left_leg_of_a_3_4_5_cone():
    """p = (5, 0), R = 3: the legs make an angle whose sine is 3/5 with the axis, so the
    left leg points along (0.8, 0.6) and its outward normal is (-0.6, 0.8). v = (10, 1)
    is to the left of the axis and 5.2 inside that leg (-(10 * -0.6 + 1 * 0.8)). A makes
    up half: the line passes through (10, 1) + 2.6 * (-0.6, 0.8) = (8.44, 3.08)."""
    plane = agent_half_plane((5, 0), (10, 1), (10, 1), 3.0, 1.0, DT)
    assert plane.region == REGION_LEFT_LEG and plane.on_collision_course
    approx(plane.normal, (-0.6, 0.8))
    assert plane.margin == pytest.approx(5.2)
    approx(plane.line, (8.44, 3.08, 0.8, 0.6))
    # The foot of the perpendicular from v lies on the leg: (6.88, 5.16) = 8.6 * (0.8, 0.6).
    foot = (10 + plane.margin * plane.normal[0], 1 + plane.margin * plane.normal[1])
    approx(foot, (6.88, 5.16))


def test_right_leg_is_the_mirror_image():
    plane = agent_half_plane((5, 0), (10, -1), (10, -1), 3.0, 1.0, DT)
    assert plane.region == REGION_RIGHT_LEG
    approx(plane.normal, (-0.6, -0.8))
    assert plane.margin == pytest.approx(5.2)
    approx(plane.line, (8.44, -3.08, -0.8, 0.6))


def test_outside_the_cone_the_room_is_split_in_half_whatever_the_share():
    """v = (2, 6) is to the left of the 3-4-5 cone: 6 * 0.8 - 2 * 0.6 = 3.6 outside the
    left leg. A may use half of that, 1.8, and the share makes no difference."""
    for share in (0.0, 0.5, 1.0):
        plane = agent_half_plane((5, 0), (2, 6), (2, 6), 3.0, 1.0, DT, share=share)
        assert plane.region == REGION_LEFT_LEG and not plane.on_collision_course
        assert plane.margin == pytest.approx(-3.6)
        approx(plane.line[:2], (2 + 1.8 * 0.6, 6 - 1.8 * 0.8))


def test_a_side_preference_picks_the_leg_when_on_a_collision_course():
    """v = (10, 1) is nearer the left leg. Told to pass on the right, A leaves across the
    right leg instead: 6.8 inside it (10 * 0.6 + 1 * 0.8), so the line passes through
    (10, 1) + 3.4 * (-0.6, -0.8) = (7.96, -1.72)."""
    plane = agent_half_plane((5, 0), (10, 1), (10, 1), 3.0, 1.0, DT, side="right")
    assert plane.region == REGION_RIGHT_LEG
    approx(plane.normal, (-0.6, -0.8))
    assert plane.margin == pytest.approx(6.8)
    approx(plane.line, (7.96, -1.72, -0.8, 0.6))
    same = agent_half_plane((5, 0), (10, 1), (10, 1), 3.0, 1.0, DT, side="left")
    assert same.region == REGION_LEFT_LEG and same.margin == pytest.approx(5.2)


def test_a_side_preference_does_nothing_when_not_on_a_collision_course():
    plain = agent_half_plane((5, 0), (2, 6), (2, 6), 3.0, 1.0, DT)
    for side in ("left", "right"):
        assert agent_half_plane((5, 0), (2, 6), (2, 6), 3.0, 1.0, DT, side=side) == plain


def test_a_side_preference_also_applies_while_the_nearest_point_is_on_the_arc():
    """v = (4.8, 0) with p = (10, 0), R = 1: inside the cut-off disc, nearest the arc. The
    legs have sine 0.1, so the left normal is (-0.1, 0.99499) and v is 0.48 inside it."""
    plane = agent_half_plane((10, 0), (4.8, 0), (4.8, 0), 1.0, 2.0, DT, side="left")
    assert plane.region == REGION_LEFT_LEG
    approx(plane.normal, (-0.1, math.sqrt(0.99)))
    assert plane.margin == pytest.approx(0.48)


def test_an_exact_tie_between_the_legs_is_not_broken_by_default():
    """v = (10, 0) lies on the axis of the 3-4-5 cone, 6 inside each leg. Neither is
    nearer, so the half-plane is taken at the tip of the arc, where it only limits the
    closing speed: 10 now, (5 - 3) / 1 = 2 allowed, 8 to lose."""
    plane = agent_half_plane((5, 0), (10, 0), (10, 0), 3.0, 1.0, DT)
    assert plane.region == REGION_APEX
    approx(plane.normal, (-1.0, 0.0))
    assert plane.margin == pytest.approx(8.0)
    approx(plane.line, (6.0, 0.0, 0.0, 1.0))  # half of 8 off the x velocity, nothing sideways


def test_the_rvo2_tie_break_takes_the_right_leg():
    """RVO2 takes the left leg only if the determinant is strictly positive
    (Agent.cc:574), so an exact tie goes to the right leg."""
    plane = agent_half_plane((5, 0), (10, 0), (10, 0), 3.0, 1.0, DT, tie_break="right")
    assert plane.region == REGION_RIGHT_LEG and plane.margin == pytest.approx(6.0)
    approx(plane.normal, (-0.6, -0.8))
    left = agent_half_plane((5, 0), (10, 0), (10, 0), 3.0, 1.0, DT, tie_break="left")
    assert left.region == REGION_LEFT_LEG
    approx(left.normal, (-0.6, 0.8))


def test_overlapping_agents_are_asked_to_separate_within_one_step():
    """p = (1, 0) with R = 2: one metre too close. To be R apart after dt = 0.5 the
    relative velocity must be 2 m/s away from B; A does half."""
    plane = agent_half_plane((1, 0), (0, 0), (0, 0), 2.0, 1.0, 0.5)
    assert plane.region == REGION_OVERLAP and plane.margin == pytest.approx(2.0)
    approx(plane.normal, (-1.0, 0.0))
    approx(plane.line, (-1.0, 0.0, 0.0, 1.0))


def test_a_clearance_margin_is_the_same_as_a_larger_radius():
    wide = agent_half_plane((10, 0), (4.8, 0), (4.8, 0), 1.0 + 0.4, 2.0, DT)
    assert wide.margin == pytest.approx(0.3 + 0.4 / 2.0)  # the disc grows by 0.4 / tau


def test_an_unknown_side_is_rejected():
    with pytest.raises(ValueError, match="unknown side"):
        agent_half_plane((5, 0), (10, 1), (10, 1), 3.0, 1.0, DT, side="up")


# --- reciprocity: the two half-planes of a pair are mirror images -----------------------------


def random_pair(rng: random.Random):
    """Two agents a little apart. Half the time A walks roughly at B, so that a good part
    of any sample is on a collision course; the rest of the time both velocities are random."""
    radius = rng.uniform(0.4, 1.2)
    distance = rng.uniform(radius * 1.05, 8.0)
    angle = rng.uniform(0.0, 2.0 * math.pi)
    position = (distance * math.cos(angle), distance * math.sin(angle))
    v_b = (rng.uniform(-2, 2), rng.uniform(-2, 2))
    if rng.random() < 0.5:
        aim, speed = angle + rng.uniform(-0.3, 0.3), rng.uniform(0.5, 2.5)
        v_a = (v_b[0] + speed * math.cos(aim), v_b[1] + speed * math.sin(aim))
    else:
        v_a = (rng.uniform(-2, 2), rng.uniform(-2, 2))
    return position, v_a, v_b, radius, rng.uniform(0.5, 4.0)


@pytest.mark.parametrize("side", [None, "left", "right"])
def test_the_two_agents_of_a_pair_build_mirrored_half_planes(side):
    rng = random.Random(2601)
    for _ in range(500):
        p, v_a, v_b, radius, tau = random_pair(rng)
        rel = (v_a[0] - v_b[0], v_a[1] - v_b[1])
        for_a = agent_half_plane(p, rel, v_a, radius, tau, DT, side=side)
        for_b = agent_half_plane((-p[0], -p[1]), (-rel[0], -rel[1]), v_b, radius, tau, DT, side=side)
        assert for_b.margin == pytest.approx(for_a.margin, abs=1e-9)
        approx(for_b.normal, (-for_a.normal[0], -for_a.normal[1]), tol=1e-9)
        assert for_a.region == for_b.region  # "left" is as seen by each agent looking at the other


@pytest.mark.parametrize("shares", [(0.5, 0.5), (1.0, 0.0), (0.0, 1.0), (0.7, 0.6), (1.0, 1.0)])
@pytest.mark.parametrize("side", [None, "left", "right"])
def test_shares_that_sum_to_at_least_one_keep_a_pair_collision_free_for_tau(shares, side):
    """Each agent moves to the nearest velocity its half-plane allows. With shares that sum
    to 1 or more the pair then has no collision within tau, whatever the configuration."""
    rng = random.Random(2602)
    checked = 0
    for _ in range(2000):
        p, v_a, v_b, radius, tau = random_pair(rng)
        rel = (v_a[0] - v_b[0], v_a[1] - v_b[1])
        for_a = agent_half_plane(p, rel, v_a, radius, tau, DT, share=shares[0], side=side)
        for_b = agent_half_plane((-p[0], -p[1]), (-rel[0], -rel[1]), v_b, radius, tau, DT, share=shares[1], side=side)
        new_a, new_b = for_a.line[:2], for_b.line[:2]  # on its own line: the least each must do
        if not for_a.on_collision_course:
            new_a, new_b = v_a, v_b  # nothing needs to change
        ttc = time_to_collision(p, (new_b[0] - new_a[0], new_b[1] - new_a[1]), radius * (1 - 1e-9))
        assert ttc is None or ttc >= tau * (1 - 1e-6), (p, v_a, v_b, radius, tau, ttc)
        checked += for_a.on_collision_course
    assert checked > 200  # a good part of the sample really was on a collision course


def test_shares_that_sum_to_less_than_one_do_not():
    """The reason the reciprocity condition exists: (0.3, 0.3) leaves the pair on a
    collision course in the plain head-on case."""
    p, v_a, v_b = (10.0, 0.0), (2.4, 0.2), (-2.4, 0.0)
    rel = (v_a[0] - v_b[0], v_a[1] - v_b[1])
    for_a = agent_half_plane(p, rel, v_a, 1.0, 2.0, DT, share=0.3)
    for_b = agent_half_plane((-10.0, 0.0), (-rel[0], -rel[1]), v_b, 1.0, 2.0, DT, share=0.3)
    new_a, new_b = for_a.line[:2], for_b.line[:2]
    ttc = time_to_collision(p, (new_b[0] - new_a[0], new_b[1] - new_a[1]), 1.0)
    assert ttc is not None and ttc < 2.0


def test_using_the_room_that_is_left_never_puts_a_pair_on_a_collision_course():
    """Not on a collision course, each agent may move toward the other by half of the
    room, whatever its share. Had the share been applied there too, (1.0, 1.0) would let
    the two use twice the room between them."""
    rng = random.Random(2603)
    for _ in range(2000):
        p, v_a, v_b, radius, tau = random_pair(rng)
        rel = (v_a[0] - v_b[0], v_a[1] - v_b[1])
        for_a = agent_half_plane(p, rel, v_a, radius, tau, DT, share=1.0)
        if for_a.on_collision_course or for_a.region == REGION_OVERLAP:
            continue
        for_b = agent_half_plane((-p[0], -p[1]), (-rel[0], -rel[1]), v_b, radius, tau, DT, share=1.0)
        # Both go as far toward each other as their half-planes allow.
        new_a, new_b = for_a.line[:2], for_b.line[:2]
        ttc = time_to_collision(p, (new_b[0] - new_a[0], new_b[1] - new_a[1]), radius * (1 - 1e-9))
        assert ttc is None or ttc >= tau * (1 - 1e-6)


# --- the two-dimensional linear program ------------------------------------------------------


def line_for(normal, offset):
    """The half-plane {v : v . normal >= offset} as a directed line."""
    nx, ny = normal
    return (offset * nx, offset * ny, ny, -nx)


def test_with_no_half_planes_the_preferred_velocity_is_kept_or_clipped():
    assert solve([], 0, 5.0, (2.0, 0.0)) == LPResult((2.0, 0.0), True, None)
    approx(solve([], 0, 1.0, (3.0, 4.0)).velocity, (0.6, 0.8))


def test_one_half_plane_gives_the_nearest_allowed_velocity():
    approx(solve([line_for((-1, 0), -1.0)], 0, 5.0, (2.0, 0.5)).velocity, (1.0, 0.5))  # x <= 1
    assert solve([line_for((-1, 0), -1.0)], 0, 5.0, (0.5, 0.5)).velocity == (0.5, 0.5)  # already allowed


def test_two_half_planes_meet_in_a_corner():
    lines = [line_for((-1, 0), -1.0), line_for((0, 1), 1.0)]  # x <= 1 and y >= 1
    result = solve(lines, 0, 5.0, (2.0, 0.0))
    assert result.feasible
    approx(result.velocity, (1.0, 1.0))


def test_the_speed_limit_is_a_constraint_too():
    result = solve([line_for((0, 1), 1.5)], 0, 2.0, (2.0, 0.0))  # y >= 1.5 inside the disc of radius 2
    assert result.feasible
    approx(result.velocity, (math.sqrt(4 - 1.5**2), 1.5))


def brute_force(lines, max_speed, preferred, n_circle=720):
    """The allowed velocity nearest ``preferred``, or ``None`` if there is none.

    The optimum of this program is the preferred velocity itself, or its projection onto
    a line or onto the speed circle, or a point where two of those boundaries cross. Every
    such candidate is tried."""
    candidates = [preferred]
    length = math.hypot(*preferred)
    if length > 0:
        candidates.append((preferred[0] / length * max_speed, preferred[1] / length * max_speed))
    for px, py, dx, dy in lines:
        t = dx * (preferred[0] - px) + dy * (preferred[1] - py)
        candidates.append((px + t * dx, py + t * dy))
        dot = px * dx + py * dy
        disc = dot * dot + max_speed**2 - (px * px + py * py)
        if disc >= 0:
            for root in (-dot - math.sqrt(disc), -dot + math.sqrt(disc)):
                candidates.append((px + root * dx, py + root * dy))
    for (px, py, dx, dy), (qx, qy, ex, ey) in itertools.combinations(lines, 2):
        det = dx * ey - dy * ex
        if abs(det) > 1e-12:
            t = (ex * (py - qy) - ey * (px - qx)) / det
            candidates.append((px + t * dx, py + t * dy))
    feasible = [
        c for c in candidates
        if math.hypot(*c) <= max_speed + 1e-9 and all(violation(line, c) <= 1e-9 for line in lines)
    ]
    if not feasible:
        return None
    return min(feasible, key=lambda c: (c[0] - preferred[0]) ** 2 + (c[1] - preferred[1]) ** 2)


def random_lines(rng: random.Random, count: int, spread: float):
    lines = []
    for _ in range(count):
        angle = rng.uniform(0.0, 2.0 * math.pi)
        lines.append(line_for((math.cos(angle), math.sin(angle)), rng.uniform(-spread, spread * 0.4)))
    return lines


def test_the_program_agrees_with_a_brute_force_solver():
    rng = random.Random(2604)
    feasible_cases = infeasible_cases = 0
    for _ in range(3000):
        lines = random_lines(rng, rng.randint(1, 8), 2.0)
        preferred = (rng.uniform(-2.5, 2.5), rng.uniform(-2.5, 2.5))
        max_speed = rng.uniform(0.5, 2.5)
        result = solve(lines, 0, max_speed, preferred)
        reference = brute_force(lines, max_speed, preferred)
        if reference is None:
            assert not result.feasible
            infeasible_cases += 1
            continue
        feasible_cases += 1
        assert result.feasible
        distance = math.hypot(result.velocity[0] - preferred[0], result.velocity[1] - preferred[1])
        best = math.hypot(reference[0] - preferred[0], reference[1] - preferred[1])
        assert distance == pytest.approx(best, abs=1e-7)
        assert math.hypot(*result.velocity) <= max_speed + 1e-9
        assert all(violation(line, result.velocity) <= 1e-7 for line in lines)
    assert feasible_cases > 500 and infeasible_cases > 500  # both branches were exercised


# --- the fallback for when no velocity satisfies every half-plane -----------------------------


def worst_violation(lines, velocity):
    return max(violation(line, velocity) for line in lines)


def test_fallback_goes_as_far_as_the_speed_limit_allows():
    """x >= 2 with a speed limit of 1: no velocity qualifies. The least bad is (1, 0),
    which misses by 1."""
    result = solve([line_for((1, 0), 2.0)], 0, 1.0, (0.0, 0.0))
    assert not result.feasible and result.failed_line == 0
    approx(result.velocity, (1.0, 0.0))


def test_fallback_splits_the_difference_between_opposed_half_planes():
    """x <= -1 and x >= 1: the least bad is x = 0, missing both by 1. Of all such
    velocities the slowest is returned, not one at the speed limit."""
    result = solve([line_for((-1, 0), 1.0), line_for((1, 0), 1.0)], 0, 5.0, (0.3, 0.2))
    assert not result.feasible
    approx(result.velocity, (0.0, 0.0))


def test_fallback_finds_the_point_that_misses_three_half_planes_equally():
    lines = [line_for((math.cos(a), math.sin(a)), 1.0) for a in (0.0, 2 * math.pi / 3, 4 * math.pi / 3)]
    result = solve(lines, 0, 5.0, (4.0, 0.0))
    assert not result.feasible
    approx(result.velocity, (0.0, 0.0), tol=1e-9)
    for line in lines:
        assert violation(line, result.velocity) == pytest.approx(1.0)


def test_fallback_does_not_depend_on_the_preferred_velocity():
    """"In these dense cases, the new velocity selected for the robot does not depend on
    the robot's preferred velocity" (the paper, Sec 5.3)."""
    lines = [line_for((math.cos(a), math.sin(a)), 1.0) for a in (0.3, 2.5, 4.4)]
    results = [solve(lines, 0, 3.0, preferred).velocity for preferred in ((2.0, 0.0), (-1.0, 1.0), (0.0, -2.5))]
    for velocity in results[1:]:
        approx(velocity, results[0], tol=1e-9)


def test_fallback_never_relaxes_a_wall():
    """A wall says x <= 0.5 and an agent says x >= 2. The wall is kept exactly and the
    agent's half-plane is missed by 1.5; the velocity does not run along the wall."""
    result = solve([line_for((-1, 0), -0.5), line_for((1, 0), 2.0)], 1, 5.0, (0.0, 3.0))
    assert not result.feasible and result.failed_line == 1
    approx(result.velocity, (0.5, 0.0))
    assert violation(line_for((-1, 0), -0.5), result.velocity) <= 1e-12


def test_fallback_minimises_the_worst_violation():
    """Against a dense search: no velocity inside the speed limit and the walls does
    better than the one returned, to within the fineness of the search."""
    rng = random.Random(2605)
    checked = 0
    while checked < 60:
        n_hard = rng.randint(0, 2)
        hard = [line_for((math.cos(a), math.sin(a)), rng.uniform(-1.5, -0.2)) for a in (rng.uniform(0, 6.28) for _ in range(n_hard))]
        soft = random_lines(rng, rng.randint(2, 6), 2.0)
        max_speed = rng.uniform(0.8, 2.0)
        result = solve(hard + soft, n_hard, max_speed, (rng.uniform(-2, 2), rng.uniform(-2, 2)))
        if result.feasible:
            continue
        checked += 1
        assert math.hypot(*result.velocity) <= max_speed + 1e-9
        assert all(violation(line, result.velocity) <= 1e-7 for line in hard)
        achieved = worst_violation(soft, result.velocity)
        steps = 80
        best = math.inf
        for ix in range(-steps, steps + 1):
            for iy in range(-steps, steps + 1):
                candidate = (ix * max_speed / steps, iy * max_speed / steps)
                if math.hypot(*candidate) <= max_speed and all(violation(line, candidate) <= 0 for line in hard):
                    best = min(best, worst_violation(soft, candidate))
        assert achieved <= best + 1e-9, (achieved, best)
        assert achieved >= best - 2.0 * max_speed / steps  # and the search could not have missed by more than a cell


def test_direction_objective_of_the_inner_program():
    """The fallback's inner program maximises along a direction instead of minimising a distance."""
    failed, velocity = linear_program_2([line_for((-1, 0), -1.0)], 5.0, (1.0, 0.0), True)
    assert failed == 1
    approx(velocity, (1.0, 0.0))  # as far along +x as x <= 1 allows; of those, the slowest


# --- walls -----------------------------------------------------------------------------------

WALL = Rect(-5.0, 1.0, 5.0, 2.0)  # a wall block above the agent, its face at y = 1


def test_wall_half_plane_limits_the_approach_speed():
    """Agent of radius 0.25 at the origin, the wall's face 1 m above: a gap of 0.75. With a
    horizon of 0.5 s it may approach the wall at up to 0.75 / 0.5 = 1.5 m/s."""
    line = wall_half_plane((0.0, 0.0), 0.25, WALL, 0.5, 2.0)
    approx(line, (0.0, 1.5, -1.0, 0.0))
    assert allowed(line, (2.0, 1.5)) and allowed(line, (-2.0, -2.0)) and not allowed(line, (0.0, 1.51))


def test_wall_half_plane_at_a_corner_points_at_the_corner():
    """Beside the wall's end, the nearest point is its corner (5, 1). From (5.6, 0.2) it is
    1 m away along (-0.6, 0.8): the agent may close on it at (1 - 0.25) / 0.5 = 1.5 m/s."""
    line = wall_half_plane((5.6, 0.2), 0.25, WALL, 0.5, 2.0)
    approx(line, (-0.6 * 1.5, 0.8 * 1.5, -0.8, -0.6))
    assert allowed(line, (1.0, 0.0)) and not allowed(line, (-1.2, 1.6))


def test_a_wall_out_of_reach_gives_no_half_plane():
    assert wall_half_plane((0.0, 0.0), 0.25, WALL, 0.15, 2.0) is None  # gap 0.75 > 0.15 * 2.0
    assert wall_half_plane((0.0, 0.5), 0.25, WALL, 0.15, 2.0) is not None  # gap 0.25 <= 0.3


def test_a_touching_agent_may_not_move_into_the_wall_at_all():
    line = wall_half_plane((0.0, 0.75), 0.25, WALL, 0.5, 2.0)
    approx(line, (0.0, 0.0, -1.0, 0.0))
    assert allowed(line, (1.0, 0.0)) and not allowed(line, (0.0, 0.01))


def test_obeying_the_wall_half_plane_never_reaches_the_wall():
    """In discrete time: an agent that always approaches as fast as the half-plane allows
    closes a fixed fraction dt / tau of the gap each step and never touches, as long as
    the horizon is at least one time step (docs/derivations.md, section 12)."""
    for tau_obst in (0.1, 0.15, 0.5):
        y = 0.0
        for _ in range(400):
            line = wall_half_plane((0.0, y), 0.25, WALL, tau_obst, 2.0)
            speed = 2.0 if line is None else min(2.0, line[1])  # straight at the wall, as fast as allowed
            y += speed * DT
            assert WALL.distance_to((0.0, y)) - 0.25 >= -1e-12
    # With a horizon shorter than the step the bound is too loose, and the agent goes through.
    y = 0.0
    for _ in range(20):
        line = wall_half_plane((0.0, y), 0.25, WALL, 0.05, 2.0)
        y += (2.0 if line is None else min(2.0, line[1])) * DT
    assert WALL.distance_to((0.0, y)) - 0.25 < 0


def test_wall_half_planes_of_a_corridor_always_allow_standing_still():
    """Every wall half-plane contains the zero velocity, so the walls alone can never make
    the program infeasible: this is what lets the fallback keep them hard."""
    walls = [Rect(-5, 1, 5, 2), Rect(-5, -2, 5, -1), Rect(2, -1, 3, -0.3)]
    rng = random.Random(2606)
    for _ in range(300):
        position = (rng.uniform(-4, 1.5), rng.uniform(-0.7, 0.7))
        lines = [line for wall in walls if (line := wall_half_plane(position, 0.25, wall, 0.3, 2.0)) is not None]
        assert all(violation(line, (0.0, 0.0)) <= 1e-12 for line in lines)
        assert solve(lines, len(lines), 2.0, (rng.uniform(-2, 2), rng.uniform(-2, 2))).feasible
