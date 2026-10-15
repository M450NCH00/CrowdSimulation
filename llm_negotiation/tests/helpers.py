"""Helpers shared by the tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from negsim.control import Arbiter
from negsim.core.geometry import dist
from negsim.experiment import ExperimentConfig
from negsim.scenarios import ScenarioSpec, load_scenario

DOORWAY = "configs/scenarios/doorway.yaml"
INTERSECTION = "configs/scenarios/intersection.yaml"
HALLWAY = "configs/scenarios/hallway.yaml"
SCENARIOS = {"doorway": DOORWAY, "intersection": INTERSECTION, "hallway": HALLWAY}


@dataclass
class SimResult:
    status: str
    goal_times: dict[int, Optional[float]]
    entry_times: dict[int, float]
    min_speed: dict[int, float]
    min_gap: float  # smallest distance between the two bodies' surfaces
    min_wall_gap: float
    max_path_error: float
    roles: list[tuple[Any, Any]] = field(default_factory=list)


def simulate(
    spec: ScenarioSpec,
    policy: str = "strategy1",
    negotiated_leader: Optional[int] = None,
) -> SimResult:
    """Run a scenario with the arbiter and the controller only (no dialogue, no logging)."""
    world, controller = spec.build_world(), spec.build_controller()
    arbiter = Arbiter(spec.build_detector(), policy=policy)
    negotiated = None if negotiated_leader is None else {(0, 1): negotiated_leader}
    result = SimResult("timeout", {}, {}, {0: float("inf"), 1: float("inf")}, float("inf"), float("inf"), 0.0)
    for _ in range(spec.max_steps):
        decisions = arbiter.resolve(world, negotiated)
        result.roles.append((decisions[0].role, decisions[1].role))
        controls = {a.agent_id: controller.compute(a, decisions[a.agent_id].speed_bound, world) for a in world.agents}
        applied = world.step(controls)
        a, b = world.agents
        result.min_gap = min(result.min_gap, dist(a.pose.xy, b.pose.xy) - a.spec.radius - b.spec.radius)
        for agent in world.agents:
            if agent.agent_id not in result.entry_times:
                result.min_speed[agent.agent_id] = min(result.min_speed[agent.agent_id], applied[agent.agent_id].v)
                if agent.path_s >= agent.spec.region_entry_s:
                    result.entry_times[agent.agent_id] = world.time
            result.max_path_error = max(result.max_path_error, agent.spec.path.distance_to(agent.pose.xy))
            for obstacle in world.obstacles:
                result.min_wall_gap = min(result.min_wall_gap, obstacle.distance_to(agent.pose.xy) - agent.spec.radius)
        if world.agent_collisions() or world.wall_collisions():
            result.status = "collision"
            break
        if world.all_done:
            result.status = "completed"
            break
    result.goal_times = {agent.agent_id: agent.goal_time for agent in world.agents}
    return result


def scenario(name: str, **overrides: Any) -> ScenarioSpec:
    return load_scenario(SCENARIOS[name], overrides or None)


def experiment(raw: Mapping[str, Any]) -> ExperimentConfig:
    return ExperimentConfig(raw, source="<test>")


def c1_config(**changes: Any) -> dict[str, Any]:
    """A small task-only experiment on the doorway, as a plain dict that tests can edit."""
    config: dict[str, Any] = {
        "experiment_name": "test_c1",
        "condition": "C1",
        "scenario": DOORWAY,
        "negotiation": {"enabled": True, "template": "gamechat_task_v1"},
        "llm": {"client": "mock", "mock_policy": "task_priority"},
        "scoring": {"ground_truth": "task_priority"},
        "design": {
            "mode": "explicit",
            "seed": 100,
            "runs": [{"agents": [{"task_type": "hospital"}, {"task_type": "grocery"}], "first_speaker": 0}],
        },
    }
    config.update(changes)
    return config


# --- the avoidance layer (issue #26) -----------------------------------------------------------

WIDE_CORRIDOR = "configs/scenarios/wide_corridor_head_on.yaml"
OPEN_CROSSING = "configs/scenarios/open_crossing.yaml"
OVERTAKING = "configs/scenarios/overtaking.yaml"
BOTTLENECK = "configs/scenarios/corridor_to_bottleneck.yaml"
BIDIRECTIONAL = "configs/scenarios/bidirectional_flow.yaml"
CROWD_SCENARIOS = {
    "wide_corridor_head_on": WIDE_CORRIDOR,
    "open_crossing": OPEN_CROSSING,
    "overtaking": OVERTAKING,
    "corridor_to_bottleneck": BOTTLENECK,
    "bidirectional_flow": BIDIRECTIONAL,
}


def crowd(name: str, **overrides: Any):
    """A shipped avoidance scenario, with overrides laid on top of its config."""
    from negsim.scenarios import load_crowd_scenario

    return load_crowd_scenario(CROWD_SCENARIOS[name], overrides or None)


def static(agent_0: Optional[Mapping[str, Any]] = None, agent_1: Optional[Mapping[str, Any]] = None, **default: Any):
    """A StaticProvider: ``default`` for everyone, then per-agent fields for agents 0 and 1."""
    from negsim.avoidance.directives import AvoidanceDirective, StaticProvider

    base = AvoidanceDirective(**default)
    agents = {}
    for agent_id, fields in ((0, agent_0), (1, agent_1)):
        if fields is not None:
            agents[agent_id] = AvoidanceDirective(**{**base.as_dict(), **fields})
    return StaticProvider(default=base, agents=agents)


def run_avoidance(spec, provider=None, **kwargs: Any):
    """Run an avoidance scenario to its end and return the result (no logging to disk)."""
    from negsim.avoidance.simulation import AvoidanceSimulation

    return AvoidanceSimulation(spec, provider, **kwargs).run()


def free_space(agents: list[Mapping[str, Any]], **settings: Any):
    """An avoidance scenario with no walls, built directly: one entry per agent.

    Each entry gives ``start`` and ``goal`` and may override ``radius``,
    ``preferred_speed``, ``max_speed``, ``sensing_radius``, ``max_neighbours``,
    ``time_horizon``. Used for encounters no shipped scenario lays out.
    """
    import math

    from negsim.core.geometry import Polyline
    from negsim.core.state import Pose
    from negsim.scenarios import CrowdAgentSpec, CrowdScenarioSpec
    from negsim.scenarios.base import DeadlockSettings
    from negsim.scenarios.crowd_base import DEFAULT_THRESHOLDS

    specs = []
    for agent_id, entry in enumerate(agents):
        path = Polyline([entry["start"], entry["goal"]])
        preferred = entry.get("preferred_speed", 1.3)
        specs.append(
            CrowdAgentSpec(
                agent_id=agent_id,
                radius=entry.get("radius", 0.25),
                max_speed=entry.get("max_speed", 2.0),
                max_turn_rate=math.inf,
                start=Pose(entry["start"][0], entry["start"][1], path.heading_at(0.0)),
                goal=tuple(entry["goal"]),
                path=path,
                side=f"agent_{agent_id}",
                region_entry_s=path.length,
                region_exit_s=path.length,
                initial_speed=preferred,
                agent_type="test",
                group=f"agent_{agent_id}",
                preferred_speed=preferred,
                sensing_radius=entry.get("sensing_radius", 12.5),
                max_neighbours=entry.get("max_neighbours", 10),
                time_horizon=entry.get("time_horizon", 3.0),
                time_horizon_obst=0.15,
                single_file_stretches=(),
            )
        )
    return CrowdScenarioSpec(
        scenario_type="free_space",
        description="",
        dt=settings.get("dt", 0.1),
        max_time=settings.get("max_time", 60.0),
        goal_tolerance=0.2,
        dynamics="holonomic",
        agents=tuple(specs),
        agent_types={},
        obstacles=(),
        single_file_segments=(),
        single_file_safety_margin=0.1,
        tie_break=settings.get("tie_break", "brake"),
        lookahead=settings.get("lookahead", 2.0),
        cell_size=2.0,
        deadlock=DeadlockSettings(3.0, 0.01),
        thresholds=DEFAULT_THRESHOLDS,
        geometry={},
        seed=0,
        on_collision=settings.get("on_collision", "stop"),
    )


def avoidance_config(**changes: Any) -> dict[str, Any]:
    """A small avoidance experiment on the wide corridor, as a plain dict that tests can edit."""
    config: dict[str, Any] = {
        "layer": "avoidance",
        "experiment_name": "test_avoidance",
        "scenario": WIDE_CORRIDOR,
        "design": {"seed": 300},
    }
    config.update(changes)
    return config


def c2_config(**changes: Any) -> dict[str, Any]:
    """A small persona experiment in the hallway."""
    config: dict[str, Any] = {
        "experiment_name": "test_c2",
        "condition": "C2",
        "scenario": HALLWAY,
        "personas": "configs/personas/personas.yaml",
        "negotiation": {"enabled": True, "template": "persona_v1", "info_fields": "all"},
        "llm": {"client": "mock", "mock_policy": "first_speaker_goes"},
        "design": {
            "mode": "explicit",
            "seed": 200,
            "runs": [{"agents": [{"persona": "f70"}, {"persona": "m25"}], "first_speaker": 0}],
        },
    }
    config.update(changes)
    return config
