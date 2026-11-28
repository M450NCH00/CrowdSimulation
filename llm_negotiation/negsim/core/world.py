"""The simulated world: agents, static obstacles and the clock."""

from __future__ import annotations

import math
from typing import Any, Mapping, Optional, Sequence

from .agent import AgentRuntime, AgentSpec
from .dynamics import DynamicsModel, UnicycleDynamics
from .geometry import Rect, dist

_CONTACT_EPS = 1e-9

#: An agent has arrived when its centre is within the goal tolerance of its goal point.
ARRIVAL_GOAL_DISC = "goal_disc"
#: An agent has arrived when its progress along its desired path is within the goal
#: tolerance of the path's end. An agent that was pushed sideways still arrives.
ARRIVAL_PATH_END = "path_end"
ARRIVAL_RULES = (ARRIVAL_GOAL_DISC, ARRIVAL_PATH_END)


class World:
    """Holds any number of agents; nothing in here assumes there are two.

    ``dynamics`` is the model that turns a command into motion (``negsim.core.dynamics``).
    It defaults to the unicycle, which is what every scenario of issue #24 uses.
    """

    def __init__(
        self,
        agents: Sequence[AgentSpec],
        obstacles: Sequence[Rect],
        dt: float,
        goal_tolerance: float,
        dynamics: Optional[DynamicsModel] = None,
        arrival: str = ARRIVAL_GOAL_DISC,
    ):
        if dt <= 0.0:
            raise ValueError(f"dt must be positive, got {dt}")
        if [a.agent_id for a in agents] != list(range(len(agents))):
            raise ValueError("agent ids must be 0, 1, ... in order")
        if arrival not in ARRIVAL_RULES:
            raise ValueError(f"unknown arrival rule {arrival!r}; expected one of {ARRIVAL_RULES}")
        self.agents: list[AgentRuntime] = [
            AgentRuntime(
                spec=a,
                pose=a.start,
                speed=a.initial_speed,
                velocity=(
                    a.initial_speed * math.cos(a.start.theta),
                    a.initial_speed * math.sin(a.start.theta),
                ),
            )
            for a in agents
        ]
        self.obstacles: tuple[Rect, ...] = tuple(obstacles)
        self.dt = dt
        self.goal_tolerance = goal_tolerance
        self.dynamics: DynamicsModel = dynamics if dynamics is not None else UnicycleDynamics()
        self.arrival = arrival
        self.step_index = 0

    @property
    def time(self) -> float:
        """Simulated seconds since the start (a product, so it does not accumulate error)."""
        return self.step_index * self.dt

    def step(self, controls: Mapping[int, Any]) -> dict[int, Any]:
        """Advance every agent by one time step and return the commands actually applied.

        A command is whatever the world's dynamics model takes: a ``Control`` for the
        unicycle, a velocity vector for the holonomic model.

        All agents move from the state at the start of the step, so the update is
        simultaneous: no agent sees another's new position before choosing its own.
        Agents that have reached their goal stay where they are.
        """
        applied: dict[int, Any] = {}
        moved = {}
        for agent in self.agents:
            wanted = self.dynamics.idle if agent.done else controls[agent.agent_id]
            pose, velocity, speed, command = self.dynamics.advance(agent, wanted, self.dt)
            applied[agent.agent_id] = command
            moved[agent.agent_id] = (pose, velocity, speed)

        self.step_index += 1
        for agent in self.agents:
            agent.pose, agent.velocity, agent.speed = moved[agent.agent_id]
            agent.path_s = agent.spec.path.project(agent.pose.xy, s_min=agent.path_s)
            if not agent.done and self._arrived(agent):
                agent.goal_time = self.time
        return applied

    def _arrived(self, agent: AgentRuntime) -> bool:
        if self.arrival == ARRIVAL_PATH_END:
            return agent.path_s >= agent.spec.path.length - self.goal_tolerance
        return dist(agent.pose.xy, agent.spec.goal) < self.goal_tolerance

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
