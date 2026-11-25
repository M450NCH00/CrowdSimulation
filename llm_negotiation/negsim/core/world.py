"""The simulated world: agents, static obstacles and the clock."""

from __future__ import annotations

from typing import Mapping, Optional, Sequence

from .agent import AgentRuntime, AgentSpec
from .dynamics import clip_control, unicycle_step
from .geometry import Rect, dist
from .state import Control

_STOP = Control(0.0, 0.0)
_CONTACT_EPS = 1e-9


class World:
    """Holds any number of agents; nothing in here assumes there are two."""

    def __init__(
        self,
        agents: Sequence[AgentSpec],
        obstacles: Sequence[Rect],
        dt: float,
        goal_tolerance: float,
    ):
        if dt <= 0.0:
            raise ValueError(f"dt must be positive, got {dt}")
        if [a.agent_id for a in agents] != list(range(len(agents))):
            raise ValueError("agent ids must be 0, 1, ... in order")
        self.agents: list[AgentRuntime] = [
            AgentRuntime(spec=a, pose=a.start, speed=a.initial_speed) for a in agents
        ]
        self.obstacles: tuple[Rect, ...] = tuple(obstacles)
        self.dt = dt
        self.goal_tolerance = goal_tolerance
        self.step_index = 0

    @property
    def time(self) -> float:
        """Simulated seconds since the start (a product, so it does not accumulate error)."""
        return self.step_index * self.dt

    def step(self, controls: Mapping[int, Control]) -> dict[int, Control]:
        """Advance every agent by one time step and return the controls actually applied.

        All agents move from the state at the start of the step, so the update is
        simultaneous: no agent sees another's new position before choosing its own.
        Agents that have reached their goal stay where they are.
        """
        applied: dict[int, Control] = {}
        new_poses = {}
        for agent in self.agents:
            wanted = _STOP if agent.done else controls[agent.agent_id]
            control = clip_control(wanted, agent.spec.max_speed, agent.spec.max_turn_rate)
            applied[agent.agent_id] = control
            new_poses[agent.agent_id] = unicycle_step(agent.pose, control, self.dt)

        self.step_index += 1
        for agent in self.agents:
            agent.pose = new_poses[agent.agent_id]
            agent.speed = applied[agent.agent_id].v
            agent.path_s = agent.spec.path.project(agent.pose.xy, s_min=agent.path_s)
            if not agent.done and dist(agent.pose.xy, agent.spec.goal) < self.goal_tolerance:
                agent.goal_time = self.time
        return applied

    @property
    def all_done(self) -> bool:
        return all(agent.done for agent in self.agents)

    def agent_collisions(self) -> list[tuple[int, int]]:
        """Pairs of agents whose discs overlap."""
        pairs = []
        for i, a in enumerate(self.agents):
            for b in self.agents[i + 1 :]:
                if dist(a.pose.xy, b.pose.xy) < a.spec.radius + b.spec.radius - _CONTACT_EPS:
                    pairs.append((a.agent_id, b.agent_id))
        return pairs

    def wall_collisions(self) -> list[int]:
        """Ids of agents whose disc overlaps an obstacle."""
        return [
            agent.agent_id
            for agent in self.agents
            if any(
                obstacle.distance_to(agent.pose.xy) < agent.spec.radius - _CONTACT_EPS
                for obstacle in self.obstacles
            )
        ]

    def mutually_visible(
        self,
        i: int,
        j: int,
        max_range: Optional[float] = None,
        walls_block_sight: bool = True,
    ) -> bool:
        """True if agents ``i`` and ``j`` can see each other. Sight is symmetric here.

        They can if they are no further apart than ``max_range`` (when one is given) and,
        when ``walls_block_sight`` is set, no obstacle lies on the straight line between
        their centres.
        """
        a, b = self.agents[i].pose.xy, self.agents[j].pose.xy
        if max_range is not None and dist(a, b) > max_range:
            return False
        if not walls_block_sight:
            return True
        return not any(obstacle.intersects_segment(a, b) for obstacle in self.obstacles)
