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
