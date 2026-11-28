"""The avoidance layer as a whole: every directive field moves behaviour the way it should,
reciprocity violations are logged and repaired, the handoff to the arbiter, the property
that a pair with shares summing to at least 1 never collides, and pluggable dynamics.

Tests here check properties that must hold: a direction of effect, a guarantee, a
symmetry. What a scenario's outcome *is* under plain ORCA (a deadlock, a time) is a result,
reported in the README from the committed runs, and is not asserted here.
"""

from __future__ import annotations

import math
import random

import pytest

from helpers import crowd, free_space, run_avoidance, static
from negsim.avoidance.coordination import (
    FOLLOWER_SHARE,
    LEADER_SHARE,
    TO_ARBITER,
    TO_ORCA,
    ArbitrationSettings,
    SingleFileDetector,
)
from negsim.avoidance.directives import AvoidanceDirective, DirectiveProvider, NullProvider
from negsim.avoidance.simulation import (
    MODE_ARBITER,
    MODE_ORCA,
    STATUS_COLLISION,
    STATUS_COMPLETED,
    AvoidanceSimulation,
)
from negsim.conflict.detection import ConflictDetector
from negsim.core.dynamics import (
    DYNAMICS,
    DynamicsModel,
    HolonomicDynamics,
    UnicycleDynamics,
    clip_velocity,
    holonomic_step,
    make_dynamics,
)
from negsim.core.state import Control, Pose
from negsim.core.world import ARRIVAL_PATH_END

HEAD_ON = "wide_corridor_head_on"
OFFSET = {"geometry": {"lateral_offsets": [0.05, -0.05]}}


def rows_of(result, agent_id):
    return [row for row in result.trajectory if row["agent_id"] == agent_id and row["speed_mps"] is not None]


def abreast(result):
    """The lateral positions of agents 0 and 1 on the step on which they are level with each other."""
    by_step = {}
    for row in result.trajectory:
        by_step.setdefault(row["step"], {})[row["agent_id"]] = row
    step = min((s for s in by_step if len(by_step[s]) == 2), key=lambda s: abs(by_step[s][0]["x_m"] - by_step[s][1]["x_m"]))
    return by_step[step][0]["y_m"], by_step[step][1]["y_m"]


# --- each directive field, on its own -----------------------------------------------------------


@pytest.mark.parametrize("layout", [{}, OFFSET], ids=["symmetric", "offset"])
@pytest.mark.parametrize("side, sign", [("left", 1.0), ("right", -1.0)])
def test_side_preference_decides_the_side_the_two_pass_on(layout, side, sign):
    """Agent 0 walks east, so its left is +y; agent 1 walks west, so its left is -y. With
    both told to keep left each ends up on its own left, and likewise for right, even when
    the layout is 10 cm in favour of the other side."""
    result = run_avoidance(crowd(HEAD_ON, **layout), static(side_preference=side))
    assert result.status == STATUS_COMPLETED
    y0, y1 = abreast(result)
    assert sign * y0 > 0.2 and sign * y1 < -0.2
    assert y0 - y1 == pytest.approx(sign * 0.5, abs=0.02)  # they pass just clear: two radii apart


def test_without_a_side_preference_the_nearer_side_is_taken():
    """In the offset layout each agent starts 5 cm to its own left; plain ORCA keeps it there."""
    y0, y1 = abreast(run_avoidance(crowd(HEAD_ON, **OFFSET)))
    assert y0 > 0.2 and y1 < -0.2


@pytest.mark.parametrize("shares", [(0.5, 0.5), (0.75, 0.25), (1.0, 0.0), (0.25, 0.75), (0.0, 1.0)])
def test_responsibility_share_decides_who_deviates_and_by_how_much(shares):
    """The two have to end up half a metre apart sideways (two radii). Each supplies its
    share of that, so an agent's largest deviation from its line is its share of 0.5 m."""
    provider = static({"responsibility_share": shares[0]}, {"responsibility_share": shares[1]}, side_preference="left")
    result = run_avoidance(crowd(HEAD_ON), provider)
    assert result.status == STATUS_COMPLETED and result.violations == []
    for agent_id in (0, 1):
        assert result.stats[agent_id].deviation_max == pytest.approx(shares[agent_id] * 0.5, abs=0.01)
    if 0.0 in shares:
        idle = shares.index(0.0)
        assert result.stats[idle].deviation_max < 1e-9  # it walked its line exactly
        assert result.stats[idle].exposure_steps == 0  # and ORCA never had to change what it wanted


def test_a_larger_share_means_a_larger_deviation():
    deviations = []
    for share in (0.2, 0.4, 0.6, 0.8, 1.0):
        provider = static({"responsibility_share": share}, {"responsibility_share": 1.0 - share}, side_preference="right")
        deviations.append(run_avoidance(crowd(HEAD_ON), provider).stats[0].deviation_max)
    assert deviations == sorted(deviations) and deviations[-1] - deviations[0] > 0.35


@pytest.mark.parametrize("scale", [1.0, 0.6, 0.3])
def test_speed_scale_slows_the_agent_only_until_the_encounter_has_passed(scale):
    """Issue #28, Part 5: the scale applies while the neighbour is perceived and the two
    have not yet passed each other, and not before or after. (Issue #26's version of this
    test had it last while the neighbour was in range.)"""
    result = run_avoidance(crowd(HEAD_ON), static(side_preference="left", speed_scale=scale))
    assert result.status == STATUS_COMPLETED
    expired = result.interactions[0].speed_scale_expired_step
    assert (expired is None) == (scale == 1.0)
    passed = result.pairs[0].passed_step
    wanted = [(row["step"], row["n_neighbours"], math.hypot(row["pref_vx_mps"], row["pref_vy_mps"])) for row in rows_of(result, 0)]
    alone = [speed for step, n, speed in wanted if n == 0]
    before = [speed for step, n, speed in wanted if n == 1 and step < passed]
    after = [speed for step, n, speed in wanted if n == 1 and step >= passed]
    assert alone and before and after
    assert all(speed == pytest.approx(1.3, abs=1e-5) for speed in alone + after)
    assert all(speed == pytest.approx(1.3 * scale, abs=1e-5) for speed in before)
    assert {row["speed_scale"] for row in rows_of(result, 0) if row["n_neighbours"] == 1 and row["step"] < passed} == {scale}
    if expired is not None:
        assert expired == passed


def test_a_smaller_speed_scale_takes_longer_and_shows_up_as_yielding():
    times, yields = [], []
    for scale in (1.0, 0.6, 0.3):
        result = run_avoidance(crowd(HEAD_ON), static(side_preference="left", speed_scale=scale))
        times.append(result.goal_times[0])
        yields.append(len(result.yields))
    # Issue #26's version also asked that 0.3 take more than twice as long as 1.0, which held
    # only while the scale lasted until the neighbour was out of range (issue #28, Part 5).
    assert times[0] < times[1] < times[2]
    # Below half its preferred speed for over a second, an agent is yielding: 0.3 is, 0.6 is not.
    assert yields == [0, 0, 2]


def test_speed_scale_never_takes_an_agent_past_its_maximum_speed():
    result = run_avoidance(crowd(HEAD_ON), static(side_preference="left", speed_scale=5.0))
    assert max(row["speed_mps"] for row in rows_of(result, 0)) <= 2.0 + 1e-9
    passed = result.pairs[0].passed_step  # after this the scale no longer applies (issue #28)
    wanted = [math.hypot(r["pref_vx_mps"], r["pref_vy_mps"]) for r in rows_of(result, 0) if r["n_neighbours"] and r["step"] < passed]
    assert wanted and all(speed == pytest.approx(2.0, abs=1e-5) for speed in wanted)


@pytest.mark.parametrize("margin", [0.0, 0.1, 0.2, 0.3])
def test_clearance_margin_is_the_gap_the_two_keep(margin):
    result = run_avoidance(crowd(HEAD_ON), static(side_preference="left", clearance_margin=margin))
    assert result.status == STATUS_COMPLETED
    assert result.min_separation_m == pytest.approx(margin, abs=0.006)
    assert result.min_separation_m >= margin - 1e-9
    # A near miss is two bodies closer than 0.1 m: only the smallest margin has one.
    assert len(result.near_misses) == (1 if margin < 0.1 else 0)


def test_the_larger_of_two_clearance_margins_is_kept_by_both():
    provider = static({"clearance_margin": 0.3}, {"clearance_margin": 0.05}, side_preference="left")
    result = run_avoidance(crowd(HEAD_ON), provider)
    assert result.min_separation_m == pytest.approx(0.3, abs=0.006)
    assert {entry["clearance_margin"] for i in result.interactions for entry in i.effective} == {0.3}


@pytest.mark.parametrize("flow", ["opposing", "merging"])
@pytest.mark.parametrize("leader", [0, 1])
def test_passage_order_decides_who_goes_first_through_the_bottleneck(flow, leader):
    orders = [{"passage_order": "follower"}, {"passage_order": "follower"}]
    orders[leader] = {"passage_order": "leader"}
    result = run_avoidance(crowd("corridor_to_bottleneck", geometry={"flow": flow}), static(*orders))
    assert result.status == STATUS_COMPLETED and result.violations == []
    entries = {agent_id: times[0] for agent_id, times in result.segment_entry_times.items()}
    follower = 1 - leader
    assert entries[leader] < entries[follower]
    handoff = result.handoffs[0]
    assert (handoff.to, handoff.leader, handoff.role_source) == (TO_ARBITER, leader, "negotiated")


def test_the_default_directive_is_plain_orca():
    """A StaticProvider that sets nothing behaves exactly like the NullProvider."""
    spec = crowd(HEAD_ON, **OFFSET)
    plain, explicit = run_avoidance(spec, NullProvider()), run_avoidance(spec, static())
    assert plain.trajectory == explicit.trajectory and plain.goal_times == explicit.goal_times


# --- reciprocity ----------------------------------------------------------------------------


def test_shares_short_of_one_are_logged_once_and_repaired():
    spec = crowd(HEAD_ON, **OFFSET)
    short = run_avoidance(spec, static({"responsibility_share": 0.3}, {"responsibility_share": 0.3}))
    assert len(short.violations) == 1
    violation = short.violations[0]
    assert violation["field"] == "responsibility_share" and violation["agents"] == [0, 1]
    assert violation["given"] == [0.3, 0.3] and violation["resolved"] == pytest.approx([0.5, 0.5])
    assert violation["policy"] == "proportional" and violation["time_s"] == pytest.approx(1.4)
    # Repaired to (0.5, 0.5), the run is the plain ORCA run, step for step.
    assert short.trajectory == run_avoidance(spec).trajectory
    assert {entry["responsibility_share"] for i in short.interactions for entry in i.effective} == {0.5}
    assert [i.directive.responsibility_share for i in short.interactions] == [0.3, 0.3]  # what was asked is kept on record


def test_the_share_policy_can_be_changed():
    spec = crowd(HEAD_ON)
    provider = static({"responsibility_share": 0.4}, {"responsibility_share": 0.0}, side_preference="left")
    proportional = run_avoidance(spec, provider)
    equal = run_avoidance(spec, provider, share_policy="equal_split")
    assert proportional.violations[0]["resolved"] == pytest.approx([1.0, 0.0])
    assert equal.violations[0]["resolved"] == pytest.approx([0.7, 0.3])
    assert proportional.stats[1].deviation_max < 1e-9 and equal.stats[1].deviation_max == pytest.approx(0.15, abs=0.01)


def test_opposite_side_preferences_are_logged_and_neither_is_used():
    spec = crowd(HEAD_ON, **OFFSET)
    clash = run_avoidance(spec, static({"side_preference": "left"}, {"side_preference": "right"}))
    assert [v["field"] for v in clash.violations] == ["side_preference"]
    assert clash.violations[0]["given"] == ["left", "right"] and clash.violations[0]["resolved"] == ["none", "none"]
    assert clash.trajectory == run_avoidance(spec).trajectory
    assert {entry["side_preference"] for i in clash.interactions for entry in i.effective} == {"none"}


def test_a_side_stated_by_one_agent_is_used_by_both():
    result = run_avoidance(crowd(HEAD_ON), static({"side_preference": "right"}, {}))
    assert result.violations == [] and result.status == STATUS_COMPLETED
    y0, y1 = abreast(result)
    assert y0 < -0.2 and y1 > 0.2
    assert {entry["side_preference"] for i in result.interactions for entry in i.effective} == {"right"}


def test_two_claims_to_go_first_are_logged_and_the_arbiter_decides_by_its_own_rule():
    result = run_avoidance(crowd("corridor_to_bottleneck"), static(passage_order="leader"))
    assert [v["field"] for v in result.violations] == ["passage_order"]
    assert result.status == STATUS_COMPLETED
    assert (result.handoffs[0].leader, result.handoffs[0].role_source) == (0, "strategy1")  # the lower index, on a tie


def test_a_provider_that_returns_something_else_is_caught():
    class Broken(DirectiveProvider):
        name = "broken"

        def directive(self, record):
            return {"side_preference": "left"}

    with pytest.raises(TypeError, match="not an AvoidanceDirective"):
        run_avoidance(crowd(HEAD_ON), Broken())


def test_the_provider_is_called_once_per_interaction_with_the_perception_record():
    class Recording(DirectiveProvider):
        name = "recording"

        def __init__(self):
            self.records = []

        def directive(self, record):
            self.records.append(record)
            return AvoidanceDirective()

    provider = Recording()
    result = run_avoidance(crowd(HEAD_ON), provider)
    assert [(r.observer_id, r.neighbour_id) for r in provider.records] == [(0, 1), (1, 0)]
    # Called at the moment the neighbour entered the sensing radius of 12.5 m ...
    assert all(r.distance_m <= 12.5 < r.distance_m + 2 * 1.3 * 0.1 for r in provider.records)
    assert all(r.time_s == pytest.approx(1.4) for r in provider.records)
    # ... and the record handed over is the one that is logged.
    assert [i.record for i in result.interactions] == provider.records


# --- the pairwise guarantee, on many random encounters --------------------------------------------

ENCOUNTER_SEEDS = 500


def random_encounter(seed: int):
    """Two agents in open space on paths that pass near each other, everything else random:
    sizes, speeds, horizons, sensing radii, shares that sum to at least 1, a common side or
    none, a clearance margin, and how an exact tie is resolved."""
    rng = random.Random(seed)
    agents = []
    for _ in range(2):
        angle, distance = rng.uniform(0, 2 * math.pi), rng.uniform(5.0, 9.0)
        start = (distance * math.cos(angle), distance * math.sin(angle))
        through = (rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8))
        heading = (through[0] - start[0], through[1] - start[1])
        norm = math.hypot(*heading)
        length = norm + rng.uniform(5.0, 9.0)
        preferred = rng.uniform(0.8, 1.8)
        agents.append(
            {
                "start": start,
                "goal": (start[0] + heading[0] / norm * length, start[1] + heading[1] / norm * length),
                "radius": rng.uniform(0.2, 0.35),
                "preferred_speed": preferred,
                "max_speed": preferred * rng.uniform(1.0, 1.6),
                "time_horizon": rng.uniform(1.0, 4.0),
                "sensing_radius": rng.uniform(4.0, 14.0),
            }
        )
    first = rng.uniform(0.0, 1.0)
    second = rng.uniform(1.0 - first, 1.0)
    provider = static(
        {"responsibility_share": first},
        {"responsibility_share": second},
        side_preference=rng.choice(["none", "left", "right"]),
        clearance_margin=rng.choice([0.0, 0.0, 0.1, 0.3]),
    )
    return free_space(agents, tie_break=rng.choice(["brake", "right", "left"])), provider


def test_no_collision_in_random_two_agent_encounters_when_the_shares_sum_to_at_least_one():
    """The property issue #26 asks for. 500 seeds; the encounters that start with the two
    agents within half a metre of touching are set aside, and every other one is run to
    its end. None may end in a collision."""
    ran = 0
    worst = math.inf
    for seed in range(ENCOUNTER_SEEDS):
        spec, provider = random_encounter(seed)
        a, b = spec.agents
        if math.hypot(a.start.x - b.start.x, a.start.y - b.start.y) < a.radius + b.radius + 0.5:
            continue
        result = run_avoidance(spec, provider, record_trajectory=False)
        ran += 1
        assert result.status != STATUS_COLLISION, f"seed {seed}: {result.collisions}"
        assert result.collisions["agent_agent"] == 0 and result.violations == []
        assert result.steps_with_fallback == 0, f"seed {seed}"  # with two agents the program is always feasible
        worst = min(worst, result.min_separation_m)
    assert ran >= 0.95 * ENCOUNTER_SEEDS
    assert worst >= -1e-9


def test_a_collision_only_ever_begins_right_after_a_fallback():
    """In a crowd, ORCA's fallback can let two discs overlap (the paper, Sec 5.3). Nothing
    else may: every collision in a dense two-way flow begins on a step on which one of
    the two agents had no feasible velocity."""
    spec = crowd("bidirectional_flow", geometry={"agents_per_direction": 24, "length": 30.0}, seed=3)
    sim = AvoidanceSimulation(spec, record_trajectory=False)
    after_fallback = unexplained = 0
    while sim.status is None and sim.world.step_index < spec.max_steps:
        open_before = set(sim.overlaps._open)
        sim.step()
        for pair in set(sim.overlaps._open) - open_before:
            if set(pair) & sim.fallback_agents:
                after_fallback += 1
            else:
                unexplained += 1
    result = sim.finish()
    assert unexplained == 0
    assert after_fallback == result.collisions["agent_agent"] > 0  # the test did see collisions
    assert result.collisions["agent_wall"] == 0  # the walls are never given up


def test_two_feasible_agents_that_perceive_each_other_never_choose_velocities_that_collide_within_tau():
    """The guarantee itself, checked in the same crowd from positions and velocities alone,
    without the half-plane code. Whenever two agents perceive each other and both programs
    are feasible, the closest the two would come within the horizon, at the velocities they
    chose, is no less than the sum of their radii. And a pair that already overlaps is
    apart again one step later."""
    spec = crowd("bidirectional_flow", geometry={"agents_per_direction": 24, "length": 30.0}, seed=3)
    sim = AvoidanceSimulation(spec, record_trajectory=False)
    agents, dt = sim.world.agents, spec.dt
    apart = overlapping = 0
    while sim.status is None and sim.world.step_index < spec.max_steps:
        active = [a for a in agents if a.goal_time is None]
        before = {a.agent_id: a.pose.xy for a in active}
        perceived = {
            a.agent_id: {j for _, j in sim.grid.nearest(a.agent_id, *a.pose.xy, a.spec.sensing_radius, a.spec.max_neighbours)}
            for a in active
        }
        sim.step()
        for i in perceived:
            for j in perceived[i]:
                if i > j or i not in perceived[j] or {i, j} & sim.fallback_agents:
                    continue
                a, b = agents[i], agents[j]
                reach = a.spec.radius + b.spec.radius
                px, py = before[j][0] - before[i][0], before[j][1] - before[i][1]
                vx, vy = b.velocity[0] - a.velocity[0], b.velocity[1] - a.velocity[1]
                if math.hypot(px, py) <= reach:
                    overlapping += 1
                    closest = math.hypot(px + vx * dt, py + vy * dt)  # where they are one step later
                else:
                    apart += 1
                    speed_sq = vx * vx + vy * vy
                    t = min(a.spec.time_horizon, max(0.0, -(px * vx + py * vy) / speed_sq)) if speed_sq else 0.0
                    closest = math.hypot(px + vx * t, py + vy * t)  # the nearest they come within tau
                assert closest >= reach - 1e-7, (sim.world.step_index, i, j, closest)
    assert apart > 10_000 and overlapping > 0  # both cases were met, the first on many pairs
    assert sim.finish().collisions["agent_agent"] > 0  # in a run in which bodies did overlap


# --- symmetry -----------------------------------------------------------------------------------


def test_an_exactly_symmetric_start_stays_exactly_symmetric_under_plain_orca():
    """Plain ORCA has nothing that could tell the two sides apart, so it must not. Every
    recorded position is the other agent's turned through a half turn, to the last bit,
    and nobody moves sideways at all."""
    result = run_avoidance(crowd(HEAD_ON))
    zero, one = rows_of(result, 0), rows_of(result, 1)
    assert len(zero) == len(one) > 50
    for a, b in zip(zero, one):
        assert (a["x_m"], a["y_m"]) == (-b["x_m"], -b["y_m"])
        assert a["y_m"] == 0.0 and a["vy_mps"] == 0.0


def test_a_shared_side_preference_keeps_the_half_turn_symmetry():
    result = run_avoidance(crowd(HEAD_ON), static(side_preference="left"))
    for a, b in zip(rows_of(result, 0), rows_of(result, 1)):
        assert (a["x_m"], a["y_m"]) == pytest.approx((-b["x_m"], -b["y_m"]), abs=1e-9)


# --- the handoff between ORCA and the arbiter ------------------------------------------------------


def bottleneck(**kwargs):
    return run_avoidance(crowd("corridor_to_bottleneck"), **kwargs)


def test_control_passes_to_the_arbiter_and_back_exactly_once():
    result = bottleneck()
    assert result.status == STATUS_COMPLETED
    to_arbiter, to_orca = result.handoffs
    assert (to_arbiter.to, to_arbiter.pair, to_arbiter.leader, to_arbiter.role_source) == (TO_ARBITER, (0, 1), 0, "strategy1")
    assert (to_orca.to, to_orca.pair, to_orca.reason) == (TO_ORCA, (0, 1), "the conflict zone was cleared")
    assert to_arbiter.step < to_orca.step

    modes = {agent_id: [(row["step"], row["control_mode"]) for row in rows_of(result, agent_id)] for agent_id in (0, 1)}
    for agent_id in (0, 1):
        under = [step for step, mode in modes[agent_id] if mode == MODE_ARBITER]
        assert under == list(range(to_arbiter.step, to_orca.step))  # one unbroken stretch, the same for both
        assert all(mode == MODE_ORCA for step, mode in modes[agent_id] if step not in under)
        assert result.stats[agent_id].arbiter_steps == len(under)


def test_the_handoff_happens_when_the_two_first_perceive_each_other():
    """Condition 1 of the handoff: both must perceive the other. They start 18 m apart with
    a sensing radius of 12.5 m and close at 2.6 m/s, so that is 2.2 s in. With a radius of
    7 m it is later, by the time it takes to close another 5.5 m."""
    assert bottleneck().handoffs[0].time_s == pytest.approx(2.2)
    shorter = crowd("corridor_to_bottleneck", agent_types={"pedestrian": {"sensing_radius": 7.0}})
    assert run_avoidance(shorter).handoffs[0].time_s == pytest.approx(4.3, abs=0.11)


def test_before_the_handoff_orca_is_alone_and_nobody_is_bounded():
    result = bottleneck()
    first = result.handoffs[0].step
    for agent_id in (0, 1):
        early = [row for row in rows_of(result, agent_id) if row["step"] < first]
        assert early and all(row["speed_bound_mps"] is None and row["role"] is None for row in early)
        assert all(row["speed_mps"] == pytest.approx(1.3) for row in early)


def test_the_follower_stays_out_of_the_segment_until_the_leader_has_left_it():
    """The arbiter's guarantee, read off the trajectory: the two are never both inside
    their conflict zones (the segment and its run-outs) on the same step."""
    spec = crowd("corridor_to_bottleneck")
    result = run_avoidance(spec)
    runout = 0.25 + 0.25 + spec.single_file_safety_margin
    zones = {}
    for agent in spec.agents:
        (_, entry_s, exit_s), = agent.single_file_stretches
        zones[agent.agent_id] = (entry_s - runout, exit_s + runout)
    inside = {agent_id: set() for agent_id in (0, 1)}
    for row in result.trajectory:
        low, high = zones[row["agent_id"]]
        if low < row["path_s_m"] < high:
            inside[row["agent_id"]].add(row["step"])
    assert inside[0] and inside[1] and not inside[0] & inside[1]
    assert max(inside[0]) < min(inside[1])  # the leader (agent 0) was through before the follower went in


def test_the_arbiters_speed_bound_caps_what_the_follower_wants_not_what_it_may_do():
    result = bottleneck()
    held = [row for row in rows_of(result, 1) if row["control_mode"] == MODE_ARBITER]
    assert {row["role"] for row in held if row["role"]} == {"follower"}
    for row in held:
        wanted = math.hypot(row["pref_vx_mps"], row["pref_vy_mps"])
        assert wanted <= row["speed_bound_mps"] + 1e-5
    # It was held well below its preferred speed of 1.3 m/s, so as to reach the segment as
    # the leader left it. It was never told to stop.
    assert 0.0 < min(row["speed_bound_mps"] for row in held) < 0.75
    # Getting out of the leader's way it may move a little faster than it wants to, never past its limit.
    assert any(row["speed_mps"] > row["speed_bound_mps"] + 1e-6 for row in held)
    assert max(row["speed_mps"] for row in held) <= 2.0 + 1e-9


def test_the_leader_is_not_slowed_and_the_follower_does_the_avoiding():
    spec = crowd("corridor_to_bottleneck")
    result = run_avoidance(spec)
    leader_path = spec.agents[0].path.length
    assert result.goal_times[0] == pytest.approx((leader_path - spec.goal_tolerance) / 1.3, abs=0.11)  # as if alone
    assert result.stats[0].deviation_max < 0.02 < 0.3 < result.stats[1].deviation_max
    shares = {i.observer_id: [entry["responsibility_share"] for entry in i.effective] for i in result.interactions}
    # The arbiter takes the pair on the step they first perceive each other: while it holds
    # them the leader does none of the avoiding and the follower all of it; afterwards half each.
    assert shares[0] == [LEADER_SHARE, 0.5] and shares[1] == [FOLLOWER_SHARE, 0.5]


def test_with_the_arbiter_switched_off_nothing_is_handed_over():
    result = bottleneck(arbitration=ArbitrationSettings(enabled=False))
    assert result.handoffs == [] and result.status != STATUS_COMPLETED
    assert all(row["control_mode"] == MODE_ORCA for row in result.trajectory if row["control_mode"])
    # Without it both walked into the segment at once, which is what the arbiter is there to prevent.
    assert result.segment_entry_times[0][0] == result.segment_entry_times[1][0]


def test_no_arbiter_is_involved_where_there_is_no_single_file_segment():
    for name in (HEAD_ON, "open_crossing", "overtaking"):
        sim = AvoidanceSimulation(crowd(name), static(passage_order="leader"))
        assert sim.coordinator is None
        result = sim.run()
        assert result.handoffs == [] and all(stats.arbiter_steps == 0 for stats in result.stats.values())


def test_a_segment_wide_enough_for_the_pair_is_not_single_file_for_it():
    """A 0.8 m segment is single-file for two 0.5 m bodies and not for two 0.3 m ones."""

    class Agent:
        def __init__(self, agent_id, radius, path_s):
            self.agent_id, self.path_s = agent_id, path_s
            self.spec = type("Spec", (), {"radius": radius})()

    stretches = {0: [(0, 7.0, 11.0)], 1: [(0, 7.0, 11.0)]}
    detector = SingleFileDetector(0.1, stretches, [0.8])
    assert isinstance(detector, ConflictDetector)
    wide = detector.zone(Agent(0, 0.25, 0.0), Agent(1, 0.25, 0.0))
    assert wide is not None and wide.live
    view = wide.views[0]
    assert (view.d_in, view.d_out) == pytest.approx((7.0 - 0.6, 11.0 + 0.6))  # the segment and a 0.6 m run-out each end
    assert detector.zone(Agent(0, 0.15, 0.0), Agent(1, 0.15, 0.0)) is None  # these two can pass inside
    assert detector.zone(Agent(0, 0.25, 12.0), Agent(1, 0.25, 12.0)) is None  # both are through
    assert not detector.zone(Agent(0, 0.25, 12.0), Agent(1, 0.25, 3.0)).live  # one is through: no longer live
    assert SingleFileDetector(0.1, {0: [(0, 7.0, 11.0)], 1: []}, [0.8]).zone(Agent(0, 0.25, 0.0), Agent(1, 0.25, 0.0)) is None


# --- leaving the scene, and bookkeeping ---------------------------------------------------------


def test_an_agent_that_has_arrived_is_no_longer_anyones_neighbour():
    """Overtaking: the faster agent arrives first. From then on the slower one walks alone."""
    result = run_avoidance(crowd("overtaking", **{"geometry": {"lateral_offsets": [0.3, 0.0]}}))
    arrival = result.goal_times[0]
    assert arrival < result.goal_times[1]
    later = [row for row in rows_of(result, 1) if row["time_s"] >= arrival]
    assert later and all(row["n_neighbours"] == 0 and row["interactions"] == "" for row in later)
    reasons = {(i.observer_id, i.neighbour_id): i.end_reason for i in result.interactions}
    assert reasons == {(0, 1): "observer_arrived", (1, 0): "neighbour_arrived"}


def test_an_interaction_ends_when_the_neighbour_is_out_of_range_and_exposure_is_counted_inside_it():
    result = run_avoidance(crowd(HEAD_ON), static(side_preference="left"))
    for interaction in result.interactions:
        assert interaction.end_reason == "out_of_range" and interaction.end_step > interaction.start_step
        assert 0 < interaction.exposure_steps < interaction.perceived_steps
        assert interaction.exposure_steps == result.stats[interaction.observer_id].exposure_steps
        assert interaction.min_separation_m == pytest.approx(result.min_separation_m)
    assert result.stats[0].interactions == 1 and result.stats[0].one_sided_steps == 0


def test_two_agents_that_never_get_in_each_others_way_have_no_exposure():
    """Parallel walkers three metres apart perceive each other the whole way and ORCA
    never has to change anything: the conflict never arose."""
    spec = free_space([{"start": (0, 0), "goal": (20, 0)}, {"start": (0, 3), "goal": (20, 3)}])
    result = run_avoidance(spec)
    assert result.status == STATUS_COMPLETED and len(result.interactions) == 2
    for stats in result.stats.values():
        assert stats.exposure_steps == 0 and stats.altered_steps == 0 and stats.deviation_max < 1e-9
    assert result.yields == [] and result.near_misses == []


def test_perceiving_is_one_sided_when_the_sensing_radii_differ():
    """Agent 0 senses 12 m and agent 1 only 4 m. Until they are 4 m apart only agent 0 has
    an interaction; the steps on which it perceives without being perceived are counted."""
    spec = free_space(
        [
            {"start": (-8, 0.3), "goal": (8, 0.3), "sensing_radius": 12.0},
            {"start": (8, -0.3), "goal": (-8, -0.3), "sensing_radius": 4.0},
        ]
    )
    result = run_avoidance(spec)
    assert result.status == STATUS_COMPLETED
    starts = {i.observer_id: i.start_time_s for i in result.interactions}
    assert starts[0] < starts[1]
    assert result.stats[0].one_sided_steps > 0 and result.stats[1].one_sided_steps == 0
    first = next(i for i in result.interactions if i.observer_id == 0)
    assert [entry["mutual"] for entry in first.effective][:2] == [False, True]


def test_stop_on_collision_ends_the_run_and_continue_goes_on():
    """A dense two-way flow under plain ORCA is the simplest run in which two discs overlap.
    By default that ends the run, as in issue #24; a crowd scenario can record it and go on."""
    settings = {"geometry": {"agents_per_direction": 24, "length": 30.0}, "seed": 3}
    stopped = run_avoidance(crowd("bidirectional_flow", on_collision="stop", **settings), record_trajectory=False)
    carried_on = run_avoidance(crowd("bidirectional_flow", on_collision="continue", **settings), record_trajectory=False)
    assert stopped.status == STATUS_COLLISION and stopped.collisions["agent_agent"] == 1
    assert stopped.collisions["time_s"] == pytest.approx(stopped.sim_time_s)
    assert carried_on.status != STATUS_COLLISION and carried_on.sim_time_s > stopped.sim_time_s
    assert carried_on.collisions["agent_agent"] > 1 and carried_on.collisions["time_s"] == stopped.collisions["time_s"]
    assert carried_on.collisions["max_overlap_m"] > 0 and len(carried_on.collision_episodes) == carried_on.collisions["agent_agent"]


# --- dynamics ----------------------------------------------------------------------------------


def test_the_two_dynamics_models_are_registered_behind_one_interface():
    assert sorted(DYNAMICS) == ["holonomic", "unicycle"]
    assert isinstance(make_dynamics("holonomic"), HolonomicDynamics) and isinstance(make_dynamics("unicycle"), UnicycleDynamics)
    assert all(issubclass(model, DynamicsModel) for model in DYNAMICS.values())
    with pytest.raises(ValueError, match="unknown dynamics model"):
        make_dynamics("bicycle")


def test_holonomic_step_moves_along_the_velocity_and_faces_that_way():
    pose = holonomic_step(Pose(1.0, 2.0, 0.0), (0.0, -2.0), 0.5)
    assert (pose.x, pose.y) == (1.0, 1.0) and pose.theta == pytest.approx(-math.pi / 2)
    assert holonomic_step(Pose(1.0, 2.0, 0.7), (0.0, 0.0), 0.5) == Pose(1.0, 2.0, 0.7)  # standing still keeps its heading
    assert clip_velocity((3.0, 4.0), 2.5) == pytest.approx((1.5, 2.0)) and clip_velocity((0.3, 0.4), 2.5) == (0.3, 0.4)


def test_the_world_defaults_to_the_unicycle_of_issue_24():
    """Every existing scenario builds a world without naming a model, and gets the unicycle."""
    from helpers import scenario

    world = scenario("doorway").build_world()
    assert isinstance(world.dynamics, UnicycleDynamics) and world.arrival == "goal_disc"
    applied = world.step({0: Control(0.2, 0.5), 1: Control(9.0, -9.0)})
    assert applied[0] == Control(0.2, 0.5) and applied[1] == Control(0.3, -1.0)  # clipped to the actuator limits
    agent = world.agents[0]
    assert agent.speed == 0.2 and math.hypot(*agent.velocity) == pytest.approx(0.2)


def test_an_avoidance_world_is_holonomic_and_arrives_by_progress_along_the_path():
    world = crowd(HEAD_ON).build_world()
    assert isinstance(world.dynamics, HolonomicDynamics) and world.arrival == ARRIVAL_PATH_END
    assert world.agents[0].velocity == pytest.approx((1.3, 0.0)) and world.agents[1].velocity == pytest.approx((-1.3, 0.0))
    world.step({0: (0.0, 1.0), 1: (-5.0, 0.0)})
    assert world.agents[0].pose.xy == pytest.approx((-8.0, 0.1))  # it moved sideways: no heading constraint
    assert world.agents[1].velocity == pytest.approx((-2.0, 0.0))  # clipped to the maximum speed


def test_another_dynamics_model_can_be_plugged_in_without_touching_the_layer():
    """The layer only ever hands a velocity to the world's model and reads back what was
    realised. Here a model that realises 70% of what it is asked for stands in for one
    with its own constraints: nothing else changes, and the agents still pass safely."""

    class Sluggish(DynamicsModel):
        name = "sluggish"
        idle = (0.0, 0.0)

        def advance(self, agent, command, dt):
            velocity = clip_velocity((0.7 * command[0], 0.7 * command[1]), agent.spec.max_speed)
            return holonomic_step(agent.pose, velocity, dt), velocity, math.hypot(*velocity), velocity

    sim = AvoidanceSimulation(crowd(HEAD_ON, **OFFSET))
    sim.world.dynamics = Sluggish()
    result = sim.run()
    assert result.status == STATUS_COMPLETED and result.collisions["agent_agent"] == 0
    plain = run_avoidance(crowd(HEAD_ON, **OFFSET))
    assert result.goal_times[0] == pytest.approx(plain.goal_times[0] / 0.7, abs=0.6)
    # What neighbours observe is the realised velocity, not the command.
    assert max(row["speed_mps"] for row in rows_of(result, 0)) == pytest.approx(0.7 * 1.3, abs=0.05)


def test_non_holonomic_avoidance_is_refused_for_now():
    from negsim.configutil import ConfigError

    with pytest.raises(ConfigError, match="non-holonomic ORCA is out of scope"):
        crowd(HEAD_ON, dynamics="unicycle")
