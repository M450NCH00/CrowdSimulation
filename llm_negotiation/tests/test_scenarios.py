"""The three scenarios: their geometry, their validation, and whether they run end to end."""

from __future__ import annotations

import math

import pytest

from helpers import scenario, simulate
from negsim.configutil import ConfigError
from negsim.conflict import Role
from negsim.control import MotionController, make_controller, register_controller
from negsim.core import Control
from negsim.scenarios import SCENARIOS, build_scenario, load_scenario_config

ALL = ("doorway", "intersection", "hallway")
# How far back the asymmetric variants move one agent (the paper uses 0.25 m, Sec V-A).
OFFSET = {"doorway": 0.25, "intersection": 0.25, "hallway": 0.5}


# --- geometry: the paper's numbers (arXiv:2503.12333v1, Sec V-A) ------------------------------


def test_doorway_matches_the_paper():
    spec = scenario("doorway")
    assert (spec.dt, spec.max_time) == (0.2, 15.0)
    assert spec.region.width == 0.4
    north, south = spec.agents
    assert (north.radius, north.max_speed, north.max_turn_rate) == (0.1, 0.3, 1.0)
    # "start 2 m to the left of the doorway and 0.5 m north or south of it"
    assert north.start.xy == (-2.0, 0.5) and south.start.xy == (-2.0, -0.5)
    assert (north.side, south.side) == ("north", "south")
    # Goals on the far side of the wall and of the centre line, so the paths cross.
    assert north.goal == (1.0, -0.2) and south.goal == (1.0, 0.2)
    assert math.degrees(north.start.theta) == pytest.approx(-10.0)


def test_intersection_matches_the_paper():
    spec = scenario("intersection")
    assert (spec.region.width, spec.region.length) == (0.4, 0.4)
    south, west = spec.agents
    # "Both start 2 m away from the center of the intersection and their goals are 1 m away on the other side."
    assert south.start.xy == pytest.approx((0.0, -2.0)) and south.goal == pytest.approx((0.0, 1.0))
    assert west.start.xy == pytest.approx((-2.0, 0.0)) and west.goal == pytest.approx((1.0, 0.0))
    assert south.region_entry_s == pytest.approx(1.8) and south.region_exit_s == pytest.approx(2.2)


def test_hallway_is_symmetric_under_a_half_turn_and_too_narrow_to_pass():
    spec = scenario("hallway")
    west, east = spec.agents
    assert (west.side, east.side) == ("west", "east")
    for point_w, point_e in zip(west.path.points, east.path.points):
        assert point_e == pytest.approx((-point_w[0], -point_w[1]))
    assert 2 * west.radius + 2 * east.radius > spec.region.width
    assert spec.region.length == 4.0 and west.region_exit_s - west.region_entry_s == pytest.approx(4.0)
    assert spec.conflict.predictor == "desired_path"


@pytest.mark.parametrize("name", ALL)
def test_asymmetric_start_moves_one_agent_away_from_its_goal(name):
    base, moved = scenario(name), scenario(name, start_offsets=[OFFSET[name], 0.0])
    extra = moved.agents[0].path.length - base.agents[0].path.length
    if name == "doorway":
        # As in the repository (scenarios.py:12), the doorway start moves straight back from
        # the wall, not along the slanted path, so the path grows by slightly less.
        assert moved.agents[0].start.x == pytest.approx(base.agents[0].start.x - 0.25)
        assert 0.24 < extra < 0.25
    else:
        assert extra == pytest.approx(OFFSET[name])
    assert moved.agents[1].path.length == pytest.approx(base.agents[1].path.length)
    assert moved.agents[0].goal == base.agents[0].goal


@pytest.mark.parametrize("name", ALL)
def test_swap_sides_exchanges_where_the_two_agents_start(name):
    base, swapped = scenario(name), scenario(name, swap_sides=True)
    assert swapped.agents[0].start == base.agents[1].start
    assert swapped.agents[1].goal == base.agents[0].goal
    assert [a.side for a in swapped.agents] == [a.side for a in base.agents][::-1]
    assert [a.agent_id for a in swapped.agents] == [0, 1]


def test_per_agent_speed_and_size_follow_the_agent_index_not_the_side():
    overrides = {"agents": [{"max_speed": 0.9, "radius": 0.3}, {}]}
    base, swapped = scenario("hallway", **overrides), scenario("hallway", swap_sides=True, **overrides)
    for spec in (base, swapped):
        assert (spec.agents[0].max_speed, spec.agents[0].radius) == (0.9, 0.3)
        assert (spec.agents[1].max_speed, spec.agents[1].radius) == (1.3, 0.25)
    assert base.agents[0].side == "west" and swapped.agents[0].side == "east"


def test_agents_start_at_their_walking_speed_unless_told_otherwise():
    assert scenario("doorway").agents[0].initial_speed == 0.3
    assert scenario("doorway", agent_defaults={"radius": 0.1, "max_speed": 0.3, "max_turn_rate": 1.0, "initial_speed": 0.0}).agents[0].initial_speed == 0.0


# --- validation ------------------------------------------------------------------------------


def config(name: str, **overrides):
    from helpers import SCENARIOS as FILES

    return load_scenario_config(FILES[name], overrides)


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"dt": 0}, "dt"),
        ({"max_time": -1}, "max_time"),
        ({"speed_limit": 3}, "unknown key"),
        ({"geometry": {"door_width": "wide"}}, "door_width"),
        ({"agents": [{"radius": 0.25}, {}]}, "cannot fit"),
        ({"agents": [{"radius": 0.18}, {}]}, "passes"),
        ({"agents": [{"max_speed": 0}, {}]}, "max_speed"),
        ({"agents": [{"wingspan": 2}, {}]}, "unknown key"),
        ({"agents": [{}]}, "two mappings"),
        ({"start_offsets": [0.25]}, "two numbers"),
        ({"start_offsets": [-0.25, 0]}, "start_offsets"),
        ({"conflict": {"predictor": "tea_leaves"}}, "predictor"),
        ({"conflict": {"zone_half_length": 0.05}}, "zone_half_length"),
        ({"controller": {"backend": "mpc_cbf"}}, "not implemented"),
        ({"controller": {"backend": "path_tracking", "lookahead": -1}}, "lookahead"),
    ],
)
def test_bad_doorway_configs_fail_with_a_pointed_message(overrides, message):
    with pytest.raises(ConfigError, match=message):
        build_scenario(config("doorway", **overrides))


def test_hallway_specific_validation():
    with pytest.raises(ConfigError, match="could pass each other"):
        build_scenario(config("hallway", agent_defaults={"radius": 0.15}))
    with pytest.raises(ConfigError, match="lateral_offset"):
        build_scenario(config("hallway", geometry={"lateral_offset": 0.0}))
    with pytest.raises(ConfigError, match="merge_distance"):
        build_scenario(config("hallway", geometry={"merge_distance": 3.0}))
    with pytest.raises(ConfigError, match="fixed value needs predictor"):
        build_scenario(config("hallway", conflict={"zone_half_length": 0.6}))


def test_starts_inside_the_conflict_zone_are_rejected():
    with pytest.raises(ConfigError, match="both agents start inside the conflict zone"):
        build_scenario(config("hallway", conflict={"safety_margin": 1.2}))


def test_unknown_scenario_type():
    with pytest.raises(ConfigError, match="unknown type"):
        build_scenario({"type": "roundabout"})
    assert sorted(SCENARIOS) == ["doorway", "hallway", "intersection"]


# --- end to end under Strategy 1 ---------------------------------------------------------------


@pytest.mark.parametrize("name", ALL)
def test_symmetric_scenario_completes_without_collision(name):
    spec = scenario(name)
    result = simulate(spec)
    assert result.status == "completed"
    assert result.min_gap >= spec.conflict.safety_margin - 1e-6  # never closer than the clearance
    assert result.min_wall_gap > 0.0
    # The tie goes to agent 0, which then never slows; agent 1 gives way and arrives later.
    assert result.entry_times[0] < result.entry_times[1]
    assert result.min_speed[0] == pytest.approx(spec.agents[0].max_speed)
    assert result.min_speed[1] < spec.agents[1].max_speed
    assert result.goal_times[0] < result.goal_times[1]


@pytest.mark.parametrize("name", ALL)
def test_without_arbitration_the_symmetric_scenario_ends_in_a_collision(name):
    """Negative control: it is Strategy 1, not luck, that keeps the agents apart."""
    assert simulate(scenario(name), policy="none").status == "collision"


@pytest.mark.parametrize("name", ALL)
@pytest.mark.parametrize("who_is_back", [0, 1])
def test_the_closer_agent_leads_when_one_starts_further_back(name, who_is_back):
    offsets = [0.0, 0.0]
    offsets[who_is_back] = OFFSET[name]
    result = simulate(scenario(name, start_offsets=offsets))
    assert result.status == "completed"
    assert result.entry_times[1 - who_is_back] < result.entry_times[who_is_back]


@pytest.mark.parametrize("name", ALL)
@pytest.mark.parametrize("leader", [0, 1])
@pytest.mark.parametrize("who_is_back", [None, 0, 1])
def test_a_negotiated_leader_goes_first_whatever_the_geometry(name, leader, who_is_back):
    """All of the paper's variants, with either agent agreed as leader: the leader is first
    through even when it starts further away, which Strategy 1 alone can never produce."""
    offsets = [0.0, 0.0]
    if who_is_back is not None:
        offsets[who_is_back] = OFFSET[name]
    spec = scenario(name, start_offsets=offsets)
    result = simulate(spec, negotiated_leader=leader)
    assert result.status == "completed"
    assert result.entry_times[leader] < result.entry_times[1 - leader]
    assert result.min_gap >= spec.conflict.safety_margin - 1e-6
    assert result.min_speed[leader] == pytest.approx(spec.agents[leader].max_speed)


@pytest.mark.parametrize("leader", [None, 0, 1])
@pytest.mark.parametrize("who_is_back", [None, 0, 1])
def test_doorway_with_the_repositorys_fixed_margin_is_safe_for_the_papers_agents(leader, who_is_back):
    """The replication configs fix the zone half-length at the GameChat repository's
    0.25 m. That is not safe in general (test_conflict.py), so check it for every variant
    and every role assignment the replication can produce."""
    offsets = [0.0, 0.0]
    if who_is_back is not None:
        offsets[who_is_back] = 0.25
    spec = scenario("doorway", start_offsets=offsets, conflict={"zone_half_length": 0.25})
    result = simulate(spec, negotiated_leader=leader)
    assert result.status == "completed" and result.min_gap > 0.1
    assert max(result.goal_times.values()) <= spec.max_time


def test_the_papers_zero_width_model_collides_at_the_intersection():
    """A finding, not a bug. The paper treats agents as "thin, car-like objects of length l
    and zero width" (Sec IV-A). Taken literally for discs (l = 2r, conflict region of
    length zero), the follower's disc reaches the crossing point while the leader's is
    still 0.14 m away, and the two 0.1 m discs overlap. See docs/derivations.md section 5."""
    literal = scenario("intersection", conflict={"zone_half_length": 0.1, "safety_margin": 0.0})
    assert simulate(literal).status == "collision"
    assert simulate(scenario("intersection", conflict={"safety_margin": 0.0})).status == "completed"


@pytest.mark.parametrize("leader", [0, 1])
def test_hallway_with_a_slower_larger_agent(leader):
    spec = scenario("hallway", max_time=80, agents=[{}, {"max_speed": 0.7, "radius": 0.3}])
    result = simulate(spec, negotiated_leader=leader)
    assert result.status == "completed"
    assert result.entry_times[leader] < result.entry_times[1 - leader]
    assert result.min_gap >= spec.conflict.safety_margin - 1e-6


def test_follower_speed_in_the_symmetric_intersection_matches_the_formula():
    """Both centres start 2 m from the crossing; the zone is 0.25 m either side of it.
    Bound = d_i * v / (d_j + L + l) = 1.75 * 0.3 / 2.25 = 0.2333 m/s. The paper's Table II
    reports 0.233 for the same case ("GameChat Ground Truth", intersection)."""
    result = simulate(scenario("intersection"))
    assert result.min_speed[1] == pytest.approx(1.75 * 0.3 / 2.25, abs=1e-6)
    assert result.roles[0] == (Role.LEADER, Role.FOLLOWER)


@pytest.mark.parametrize("name", ALL)
def test_agents_stay_on_their_desired_paths(name):
    spec = scenario(name)
    assert simulate(spec).max_path_error < 0.25 * spec.agents[0].radius


def test_walls_can_block_sight_at_the_intersection():
    """GameChat does not model occlusion, so by default the agents see each other from the
    start. With walls_block_sight the corner hides them until they are close."""
    assert scenario("intersection").build_world().mutually_visible(0, 1, walls_block_sight=False)
    assert not scenario("intersection").build_world().mutually_visible(0, 1, walls_block_sight=True)
    for name in ("doorway", "hallway"):
        assert scenario(name).build_world().mutually_visible(0, 1, walls_block_sight=True)


# --- the controller plug point ---------------------------------------------------------------


def test_a_new_controller_backend_plugs_in_by_name():
    @register_controller("test_crawl")
    class Crawl(MotionController):
        def __init__(self, lookahead: float = 0.0, top_speed: float = 0.05):
            self.top_speed = top_speed

        def compute(self, agent, speed_bound, world):
            return Control(min(speed_bound, self.top_speed), 0.0)

    assert isinstance(make_controller("test_crawl"), Crawl)
    spec = scenario("intersection", controller={"backend": "test_crawl", "top_speed": 0.07}, max_time=2.0)
    world, controller = spec.build_world(), spec.build_controller()
    world.step({a.agent_id: controller.compute(a, 0.3, world) for a in world.agents})
    assert world.agents[0].speed == pytest.approx(0.07)
    with pytest.raises(ValueError, match="already registered"):
        register_controller("test_crawl")(Crawl)


def test_path_tracker_never_exceeds_the_bound_and_stops_at_the_goal():
    spec = scenario("doorway")
    world, controller = spec.build_world(), spec.build_controller()
    agent = world.agents[0]
    assert controller.compute(agent, 0.12, world).v == pytest.approx(0.12)
    assert controller.compute(agent, 5.0, world).v == pytest.approx(0.3)
    assert controller.compute(agent, -1.0, world).v == 0.0
    agent.goal_time = 1.0
    assert controller.compute(agent, 0.3, world) == Control(0.0, 0.0)
