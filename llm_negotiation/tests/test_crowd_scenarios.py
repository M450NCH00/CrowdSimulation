"""The five avoidance scenarios: their layouts, their config checks, that each runs end to
end, that the scenarios of issue #24 are untouched, and that every physical parameter in a
shipped config is tagged with where it comes from."""

from __future__ import annotations

import itertools
import math
import re

import pytest
import yaml

from helpers import CROWD_SCENARIOS, SCENARIOS, crowd, run_avoidance, scenario
from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.scenarios import (
    CROWD_SCENARIOS as REGISTERED,
    CROWD_SCHEMA_VERSION,
    CrowdAgentSpec,
    build_crowd_scenario,
    load_crowd_scenario,
    load_scenario,
    load_scenario_config,
)

NAMES = sorted(CROWD_SCENARIOS)
SCENARIO_DIR = PACKAGE_ROOT / "configs" / "scenarios"


# --- what is shipped ----------------------------------------------------------------------------


def test_the_five_scenarios_issue_26_asks_for_are_registered_and_shipped():
    expected = {"wide_corridor_head_on", "open_crossing", "overtaking", "corridor_to_bottleneck", "bidirectional_flow"}
    assert set(REGISTERED) == expected == set(CROWD_SCENARIOS)
    for name in expected:
        assert (SCENARIO_DIR / f"{name}.yaml").is_file()
    assert CROWD_SCHEMA_VERSION == 2


@pytest.mark.parametrize("name", NAMES)
def test_every_shipped_scenario_builds(name):
    spec = crowd(name)
    assert spec.scenario_type == name and spec.dynamics == "holonomic" and spec.dt == 0.1
    assert all(isinstance(agent, CrowdAgentSpec) for agent in spec.agents)
    assert [agent.agent_id for agent in spec.agents] == list(range(len(spec.agents)))
    described = spec.as_dict()
    assert described["schema_version"] == 2 and described["n_agents"] == len(spec.agents)
    assert described["agents"][0]["sensing_radius_m"] == 12.5 and "max_turn_rate_radps" not in described["agents"][0]


@pytest.mark.parametrize("name", NAMES)
def test_every_shipped_scenario_runs_end_to_end(name):
    """Whatever the outcome under plain ORCA, the run reaches an end, no agent goes through
    a wall, and nothing stops because of a collision."""
    spec = crowd(name) if name != "bidirectional_flow" else crowd(name, geometry={"agents_per_direction": 12, "length": 30.0})
    result = run_avoidance(spec, record_trajectory=False)
    assert result.status in ("completed", "deadlock", "timeout")
    assert result.collisions["agent_wall"] == 0
    assert result.steps > 50


def test_the_scenarios_of_issue_24_are_untouched_and_are_a_different_kind():
    for name in ("doorway", "intersection", "hallway"):
        assert load_scenario_config(SCENARIOS[name])["schema_version"] == 1
        assert scenario(name).scenario_type == name  # still loads exactly as before
        with pytest.raises(ConfigError, match="two-agent scenario of issue #24"):
            load_crowd_scenario(SCENARIOS[name])
    for name in NAMES:
        with pytest.raises(ConfigError, match="unknown type"):
            load_scenario(CROWD_SCENARIOS[name])
    with pytest.raises(ConfigError, match="unknown avoidance scenario type"):
        build_crowd_scenario({"type": "roundabout"})
    with pytest.raises(ConfigError, match="'type' key"):
        build_crowd_scenario({})


def test_an_avoidance_scenario_must_say_schema_version_2():
    cfg = load_scenario_config(CROWD_SCENARIOS["open_crossing"])
    for version in (1, 3):
        with pytest.raises(ConfigError, match="schema_version"):
            build_crowd_scenario({**cfg, "schema_version": version})
    without = {key: value for key, value in cfg.items() if key != "schema_version"}
    with pytest.raises(ConfigError, match="missing required key"):
        build_crowd_scenario(without)


# --- layouts ------------------------------------------------------------------------------------


def test_wide_corridor_head_on_layout():
    spec = crowd("wide_corridor_head_on")
    east, west = spec.agents
    assert (east.start.xy, east.goal, east.group) == ((-8.0, 0.0), (8.0, 0.0), "eastbound")
    assert (west.start.xy, west.goal, west.group) == ((8.0, 0.0), (-8.0, 0.0), "westbound")
    assert east.start.theta == 0.0 and abs(west.start.theta) == pytest.approx(math.pi)
    top, bottom = spec.obstacles
    assert (top.ymin, bottom.ymax) == (0.875, -0.875)  # the cited width of 1.75 m
    assert math.dist(east.start.xy, west.start.xy) > east.sensing_radius  # they start out of each other's range
    assert spec.single_file_segments == () and spec.on_collision == "stop"
    shifted = crowd("wide_corridor_head_on", geometry={"lateral_offsets": [0.05, -0.05]})
    assert [agent.start.y for agent in shifted.agents] == [0.05, -0.05]
    assert shifted.agents[0].goal == (8.0, 0.05)  # each walks a line parallel to the walls


def test_open_crossing_layout():
    spec = crowd("open_crossing")
    east, north = spec.agents
    assert (east.start.xy, east.goal) == ((-8.0, 0.0), (8.0, 0.0))
    assert (north.start.xy, north.goal) == ((0.0, -8.0), (0.0, 8.0))
    assert north.start.theta == pytest.approx(math.pi / 2) and spec.obstacles == ()
    later = crowd("open_crossing", geometry={"approach_distances": [8.0, 8.5]})
    assert later.agents[1].start.xy == (0.0, -8.5)


def test_overtaking_layout_and_speeds():
    spec = crowd("overtaking")
    behind, ahead = spec.agents
    assert (behind.start.xy, ahead.start.xy) == ((0.0, 0.0), (4.0, 0.0))
    assert behind.goal == ahead.goal == (40.0, 0.0) and spec.obstacles == ()
    assert (behind.preferred_speed, ahead.preferred_speed) == (1.48, 1.10)  # the measured mean plus and minus one s.d.
    assert behind.max_speed == ahead.max_speed == 2.0 and behind.radius == ahead.radius == 0.25  # nothing else differs
    assert behind.initial_speed == 1.48


def test_corridor_to_bottleneck_opposing_layout():
    spec = crowd("corridor_to_bottleneck")
    east, west = spec.agents
    assert (east.group, west.group) == ("eastbound", "westbound")
    assert east.start.xy == (-9.0, -0.4) and east.goal == (9.0, -0.4)  # each keeps to its own right
    assert west.start.xy == (9.0, 0.4) and west.goal == (-9.0, 0.4)
    # The paths are each other's image under a half turn, and share the centre line of the segment.
    assert [(-x, -y) for x, y in east.path.points] == list(west.path.points)
    assert east.path.points[1] == (-2.6, 0.0) and east.path.points[2] == (2.6, 0.0)
    (segment,) = spec.single_file_segments
    assert (segment.name, segment.width) == ("bottleneck", 0.8)
    assert (segment.rect.xmin, segment.rect.xmax, segment.rect.ymin, segment.rect.ymax) == (-2.0, 2.0, -0.4, 0.4)
    for agent in spec.agents:
        ((index, entry_s, exit_s),) = agent.single_file_stretches
        assert index == 0 and exit_s - entry_s == pytest.approx(4.0, abs=1e-4)  # the segment is 4 m long
        assert agent.path.point_at(entry_s)[0] == pytest.approx(-2.0 if agent.group == "eastbound" else 2.0, abs=1e-4)
    assert len(spec.obstacles) == 4


def test_corridor_to_bottleneck_merging_layout():
    spec = crowd("corridor_to_bottleneck", geometry={"flow": "merging"})
    north, south = spec.agents
    assert (north.group, south.group) == ("north_lane", "south_lane")
    assert north.start.xy == (-9.0, 0.4) and south.start.xy == (-9.0, -0.4)  # side by side at the west end
    assert north.goal == (9.0, 0.4) and south.goal == (9.0, -0.4)
    assert north.path.points[1:3] == south.path.points[1:3]  # both go through on the centre line


def test_bidirectional_flow_layout():
    spec = crowd("bidirectional_flow")
    assert len(spec.agents) == 100 and spec.on_collision == "continue"
    east = [agent for agent in spec.agents if agent.group == "eastbound"]
    west = [agent for agent in spec.agents if agent.group == "westbound"]
    assert [agent.agent_id for agent in east] == list(range(50)) and [agent.agent_id for agent in west] == list(range(50, 100))
    assert all(agent.start.x < -12 and agent.goal[0] == 25.0 for agent in east)
    assert all(agent.start.x > 12 and agent.goal[0] == -25.0 for agent in west)
    assert all(agent.goal[1] == agent.start.y for agent in spec.agents)  # each keeps its lateral position
    assert (spec.geometry["spawn_columns"], spec.geometry["spawn_rows"]) == (4, 13)
    assert all(abs(agent.start.y) <= 1.5 + 0.1 for agent in spec.agents)  # 0.5 m off the walls, give or take the jitter
    # The two blocks start out of each other's sensing range.
    assert min(agent.start.x for agent in west) - max(agent.start.x for agent in east) > 12.5


def test_bidirectional_flow_is_reproducible_and_the_seed_matters():
    starts = lambda spec: [agent.start.xy for agent in spec.agents]
    assert starts(crowd("bidirectional_flow")) == starts(crowd("bidirectional_flow"))
    assert starts(crowd("bidirectional_flow")) != starts(crowd("bidirectional_flow", seed=27))
    lattice = crowd("bidirectional_flow", geometry={"spawn_jitter": 0.0})
    assert {round(agent.start.y, 9) for agent in lattice.agents} == {-1.5, -0.5, 0.5, 1.5}


def test_the_flow_can_start_from_random_places():
    spec = crowd("bidirectional_flow", geometry={"spawn_pattern": "random"})
    east = [agent for agent in spec.agents if agent.group == "eastbound"]
    west = [agent for agent in spec.agents if agent.group == "westbound"]
    assert len(east) == len(west) == 50
    # In the block the lattice would fill: the same density, out of each other's sensing range.
    assert all(-25.0 <= agent.start.x <= -13.0 and abs(agent.start.y) <= 1.5 for agent in east)
    assert all(13.0 <= agent.start.x <= 25.0 and abs(agent.start.y) <= 1.5 for agent in west)
    for group in (east, west):
        for one, other in itertools.combinations(group, 2):
            assert math.dist(one.start.xy, other.start.xy) >= 0.6
    assert len({round(agent.start.y, 3) for agent in spec.agents}) > 90  # not four lanes
    assert all(agent.goal[1] == agent.start.y for agent in spec.agents)  # each keeps its lateral position
    assert [agent.start.x for agent in east] == sorted((agent.start.x for agent in east), reverse=True)  # front first
    starts = lambda spec: [agent.start.xy for agent in spec.agents]
    assert starts(crowd("bidirectional_flow", geometry={"spawn_pattern": "random"})) == starts(spec)
    assert starts(crowd("bidirectional_flow", geometry={"spawn_pattern": "random"}, seed=27)) != starts(spec)
    wider = crowd("bidirectional_flow", geometry={"spawn_pattern": "random", "spawn_min_distance": 0.7})
    assert min(math.dist(a.start.xy, b.start.xy) for a, b in itertools.combinations(wider.agents[:50], 2)) >= 0.7


def test_without_a_spawn_pattern_the_flow_resolves_exactly_as_before():
    """Runs and frozen conflict cases hash the resolved scenario (issue #30), so the keys
    are only written when set."""
    spec = crowd("bidirectional_flow")
    assert "spawn_pattern" not in spec.geometry and "spawn_min_distance" not in spec.geometry
    assert {round(agent.start.y, 1) for agent in crowd("bidirectional_flow", geometry={"spawn_jitter": 0.0}).agents} == {-1.5, -0.5, 0.5, 1.5}
    explicit = crowd("bidirectional_flow", geometry={"spawn_pattern": "lattice"})
    assert [agent.start.xy for agent in explicit.agents] == [agent.start.xy for agent in spec.agents]


@pytest.mark.parametrize(
    "geometry, message",
    [
        ({"spawn_pattern": "spiral"}, "expected one of"),
        ({"spawn_min_distance": 0.7}, "applies to spawn_pattern random only"),
        ({"spawn_pattern": "random", "spawn_min_distance": 0.0}, "greater than"),
        ({"spawn_pattern": "random", "spawn_min_distance": 1.5}, "could not place 50 agents"),
        ({"spawn_pattern": "random", "spawn_min_distance": 0.3}, "overlap at their starting positions"),
    ],
)
def test_a_random_start_that_cannot_be_had_is_refused(geometry, message):
    with pytest.raises(ConfigError, match=message):
        crowd("bidirectional_flow", geometry=geometry)


def test_the_number_of_agents_in_the_flow_is_configurable():
    for count in (1, 7, 200):
        spec = crowd("bidirectional_flow", geometry={"agents_per_direction": count, "length": 120.0})
        assert len(spec.agents) == 2 * count


# --- config checks ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name, overrides, message",
    [
        ("wide_corridor_head_on", {"geometry": {"width": 0.9}}, "cannot pass in a corridor"),
        ("wide_corridor_head_on", {"geometry": {"start_distance": 11.0}}, "start outside the corridor"),
        ("wide_corridor_head_on", {"geometry": {"lateral_offsets": [0.7, 0.0]}}, "starts overlapping a wall"),
        ("wide_corridor_head_on", {"geometry": {"lateral_offsets": [0.0]}}, "expected a list of 2 numbers"),
        ("wide_corridor_head_on", {"geometry": {"height": 3.0}}, "unknown key"),
        ("wide_corridor_head_on", {"geometry": {"start_distance": 0.2}}, "overlap at their starting positions"),
        ("open_crossing", {"geometry": {"goal_distance": 0.0}}, "must be greater than 0"),
        ("overtaking", {"agents": {"overrides": {0: {"preferred_speed": 1.0}}}}, "must be the faster one"),
        ("overtaking", {"geometry": {"headway": 50.0}}, "headway must be less than travel_distance"),
        ("corridor_to_bottleneck", {"geometry": {"bottleneck_width": 1.2}}, "meant to be single-file"),
        ("corridor_to_bottleneck", {"geometry": {"bottleneck_width": 0.45}}, "cannot follow the path"),
        ("corridor_to_bottleneck", {"geometry": {"approach_width": 0.95, "lateral_offset": 0.1}}, "cannot pass in the wide part"),
        ("corridor_to_bottleneck", {"geometry": {"approach_width": 0.7}}, "bottleneck_width must be less than approach_width"),
        ("corridor_to_bottleneck", {"geometry": {"flow": "sideways"}}, "expected one of"),
        ("corridor_to_bottleneck", {"geometry": {"start_setback": 9.0}}, "start_setback <= approach_length"),
        ("corridor_to_bottleneck", {"geometry": {"lateral_offset": 0.9}}, "outside the wide part"),
        ("bidirectional_flow", {"geometry": {"agents_per_direction": 0}}, "whole number, 1 or more"),
        ("bidirectional_flow", {"geometry": {"agents_per_direction": 500}}, "does not fit twice"),
        ("bidirectional_flow", {"geometry": {"spawn_spacing": 0.4}}, "overlap at their starting positions"),
        ("open_crossing", {"agent_types": {"pedestrian": {"preferred_speed": 2.5}}}, "exceeds max_speed"),
        ("open_crossing", {"agent_types": {"pedestrian": {"max_neighbours": 2.5}}}, "whole number"),
        ("open_crossing", {"agent_types": {"pedestrian": {"radius": 0.0}}}, "must be greater than 0"),
        ("open_crossing", {"agent_types": {"pedestrian": {"time_horizon_obst": 0.05}}}, "shorter than the time step"),
        ("open_crossing", {"agents": {"default_type": "robot"}}, "unknown agent type"),
        ("open_crossing", {"agents": {"overrides": {5: {"radius": 0.3}}}}, "not an agent index"),
        ("open_crossing", {"agents": {"overrides": {0: {"age": 70}}}}, "unknown key"),
        ("open_crossing", {"agents": {"groups": {"southbound": "pedestrian"}}}, "unknown group"),
        ("open_crossing", {"orca": {"tie_break": "coin"}}, "expected one of"),
        ("open_crossing", {"on_collision": "ignore"}, "expected one of"),
        ("open_crossing", {"dynamics": "bicycle"}, "expected one of"),
        ("open_crossing", {"metrics": {"yield_speed_fraction": 1.5}}, "must be at most 1"),
        ("open_crossing", {"seed": -1}, "whole number, 0 or more"),
        ("open_crossing", {"wind": 3}, "unknown key"),
    ],
)
def test_a_bad_scenario_config_is_refused_with_a_reason(name, overrides, message):
    with pytest.raises(ConfigError, match=message):
        crowd(name, **overrides)


def test_agent_types_can_be_given_by_group_and_overridden_per_agent():
    slow = {"radius": 0.3, "preferred_speed": 0.9, "max_speed": 1.5, "sensing_radius": 8.0, "max_neighbours": 5, "time_horizon": 2.0, "time_horizon_obst": 0.2}
    spec = crowd(
        "bidirectional_flow",
        geometry={"agents_per_direction": 4, "length": 30.0, "spawn_spacing": 1.2},
        agent_types={"slow": slow},
        agents={"groups": {"westbound": "slow"}, "overrides": {0: {"preferred_speed": 1.6}}},
    )
    assert [agent.agent_type for agent in spec.agents] == ["pedestrian"] * 4 + ["slow"] * 4
    assert spec.agents[0].preferred_speed == 1.6 and spec.agents[1].preferred_speed == 1.3
    assert (spec.agents[4].radius, spec.agents[4].preferred_speed, spec.agents[4].max_neighbours) == (0.3, 0.9, 5)
    assert spec.agents[4].time_horizon == 2.0 and spec.agents[4].sensing_radius == 8.0


# --- physical parameters and demographic attributes are separate ----------------------------------


def test_a_scenario_has_no_way_of_reading_age_or_gender():
    """Nothing demographic can be set on an agent type or on an agent: the scenario schema
    has no such key, so a persona cannot change a size or a speed by itself."""
    for key in ("age", "gender", "persona"):
        with pytest.raises(ConfigError, match="unknown key"):
            crowd("open_crossing", agent_types={"pedestrian": {key: 70}})
        with pytest.raises(ConfigError, match="unknown key"):
            crowd("open_crossing", agents={"overrides": {0: {key: 70}}})
        with pytest.raises(ConfigError, match="unknown key"):
            crowd("open_crossing", **{key: 70})
    described = crowd("open_crossing").as_dict()
    assert {"age", "gender", "persona"}.isdisjoint(described["agents"][0])
    assert {"age", "gender", "persona"}.isdisjoint(described["agent_types"]["pedestrian"])


def test_every_shipped_scenario_uses_the_same_pedestrian():
    """One set of physical defaults, so that a difference between scenarios is not a
    difference in the bodies walking through them."""
    reference = crowd("open_crossing").agent_types["pedestrian"].as_dict()
    assert reference == {
        "radius": 0.25, "preferred_speed": 1.3, "max_speed": 2.0, "sensing_radius": 12.5,
        "max_neighbours": 10, "time_horizon": 3.0, "time_horizon_obst": 0.15,
    }
    for name in NAMES:
        assert crowd(name).agent_types["pedestrian"].as_dict() == reference, name
    # The sensing radius is the ORCA paper's bound, with the two radii added.
    assert reference["sensing_radius"] == reference["time_horizon"] * 2 * reference["max_speed"] + 2 * reference["radius"]


# --- every physical parameter says where it comes from --------------------------------------------

TAG = re.compile(r"\[(cited: [^\]]+|derived: [^\]]+|placeholder|design)\]")
# Lines that set a mode or a name, not a quantity.
NOT_A_QUANTITY = {"schema_version", "type", "description", "dynamics", "on_collision", "flow", "default_type", "tie_break"}


def quantity_lines(name: str):
    """(key, line) for every line of a shipped scenario config that sets a number or a list."""
    for line in (SCENARIO_DIR / f"{name}.yaml").read_text(encoding="utf-8").splitlines():
        code = line.split("#", 1)[0].rstrip()
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*|\d+):\s*(\S.*)$", code)
        if match and match.group(1) not in NOT_A_QUANTITY and not match.group(1).isdigit():
            yield match.group(1), line


@pytest.mark.parametrize("name", NAMES)
def test_every_quantity_in_a_shipped_scenario_is_tagged(name):
    lines = list(quantity_lines(name))
    assert len(lines) >= 20
    for key, line in lines:
        assert TAG.search(line), f"{name}.yaml: '{key}' has no [cited: ...], [derived: ...], [placeholder] or [design] tag"
    # The file parses to the same keys the scan found: no quantity was missed by the scan.
    parsed = yaml.safe_load((SCENARIO_DIR / f"{name}.yaml").read_text(encoding="utf-8"))

    def leaves(node):
        for key, value in node.items():
            if isinstance(value, dict):
                yield from leaves(value)
            elif key not in NOT_A_QUANTITY:
                yield str(key)

    assert sorted(key for key, _ in lines) == sorted(leaves(parsed))


def placeholders():
    found = []
    for name in NAMES:
        for key, line in quantity_lines(name):
            if "[placeholder]" in line:
                found.append((name, key))
    return found


def test_the_parameters_document_lists_every_placeholder_and_every_source():
    """docs/parameters.md is what a reader of the report will check: every placeholder in a
    shipped config is named there as a placeholder, and every source cited in a config is
    listed there with where its copy is."""
    document = (PACKAGE_ROOT / "docs" / "parameters.md").read_text(encoding="utf-8")
    assert placeholders() == [
        ("bidirectional_flow", "spawn_spacing"),
        ("corridor_to_bottleneck", "bottleneck_width"),
        ("corridor_to_bottleneck", "bottleneck_length"),
    ]
    section = document.split("## 3. Placeholders", 1)[1].split("\n## ", 1)[0]
    for name, key in placeholders():
        assert f"`{key}`" in section and f"`{name}`" in section, (name, key)
        assert "[placeholder]" in section
    cited = set()
    for name in NAMES:
        for _, line in quantity_lines(name):
            for tag in TAG.findall(line):
                if tag.startswith(("cited: ", "derived: ")):
                    cited.add(tag.split(": ", 1)[1].split(",")[0].split(" line")[0].split(";")[0].strip())
    assert cited == {"Moussaid et al. 2009", "Yamamoto et al. 2019", "Karamouzas et al. 2014", "Menge 4squareS.xml", "ORCA paper"}
    for source in cited:
        assert source in document, f"{source} is cited in a config but not listed in docs/parameters.md"
    for cached in ("si1_moussaid2009_pmc.txt", "b3_yamamoto_bodyrotation.txt", "si1_karamouzas2014_1412_1082.txt",
                   "si1_menge_4squareS.xml", "si1_orca_vandenberg2011.txt", "si1_bohannon1997_pubmed_abstract.txt"):
        assert cached in document and (PACKAGE_ROOT.parent / "refs" / cached).is_file(), cached
