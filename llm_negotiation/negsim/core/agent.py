"""Agents: the fixed specification and the state that changes during a run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .geometry import Polyline, Vec
from .state import Pose


@dataclass(frozen=True)
class AgentSpec:
    """Everything about an agent that does not change during a run.

    ``region_entry_s`` and ``region_exit_s`` are the arc lengths along ``path`` at which the
    path enters and leaves the scenario's physical conflict region (the doorway, the
    crossing, the hallway). They are used for what an agent can see and say about the
    region and for the "who got there first" metrics; the safety arithmetic uses the
    conflict zone computed in ``negsim.conflict``.
    """

    agent_id: int
    radius: float
    max_speed: float
    max_turn_rate: float
    start: Pose
    goal: Vec
    path: Polyline
    side: str
    region_entry_s: float
    region_exit_s: float
    initial_speed: float

    def __post_init__(self) -> None:
        if self.radius <= 0.0:
            raise ValueError(f"agent {self.agent_id}: radius must be positive, got {self.radius}")
        if self.max_speed <= 0.0:
            raise ValueError(f"agent {self.agent_id}: max_speed must be positive, got {self.max_speed}")
        if self.max_turn_rate <= 0.0:
            raise ValueError(
                f"agent {self.agent_id}: max_turn_rate must be positive, got {self.max_turn_rate}"
            )
        if not 0.0 <= self.initial_speed <= self.max_speed:
            raise ValueError(
                f"agent {self.agent_id}: initial_speed {self.initial_speed} is outside "
                f"[0, max_speed={self.max_speed}]"
            )

    @property
    def body_length(self) -> float:
        """Extent of the body along its direction of travel: the diameter of the disc."""
        return 2.0 * self.radius

    def as_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "side": self.side,
            "radius_m": self.radius,
            "max_speed_mps": self.max_speed,
            "max_turn_rate_radps": self.max_turn_rate,
            "initial_speed_mps": self.initial_speed,
            "start": {"x": self.start.x, "y": self.start.y, "theta_rad": self.start.theta},
            "goal": {"x": self.goal[0], "y": self.goal[1]},
            "path": self.path.as_list(),
            "path_length_m": self.path.length,
            "region_entry_s_m": self.region_entry_s,
            "region_exit_s_m": self.region_exit_s,
        }


@dataclass
class AgentRuntime:
    """An agent's changing state.

    ``speed`` is the linear velocity commanded on the most recent step. Before the first
    step it is ``spec.initial_speed``: the agents are taken to be already walking when they
    first see each other. ``velocity`` is the same motion as a vector in the world frame;
    it is what another agent can observe of this one.
    """

    spec: AgentSpec
    pose: Pose
    speed: float
    path_s: float = 0.0
    goal_time: Optional[float] = None
    velocity: Vec = (0.0, 0.0)

    @property
    def agent_id(self) -> int:
        return self.spec.agent_id

    @property
    def done(self) -> bool:
        return self.goal_time is not None
