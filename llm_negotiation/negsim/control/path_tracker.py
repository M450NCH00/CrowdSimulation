"""Default controller backend: follow the desired path, as fast as the speed bound allows."""

from __future__ import annotations

import math

from ..core.agent import AgentRuntime
from ..core.geometry import wrap_angle
from ..core.state import Control
from ..core.world import World
from .base import MotionController, register_controller


@register_controller("path_tracking")
class PathTrackingController(MotionController):
    """Steer toward a point a fixed distance ahead on the desired path.

    The agent turns to face a "carrot" ``lookahead`` metres further along its path than
    the point nearest to it, as fast as its turn-rate limit allows, and drives at exactly
    ``speed_bound``. It does not slow down for bends, so any drop in an agent's speed in
    the logs comes from conflict resolution and nothing else.

    It does not avoid obstacles: the scenarios lay the desired paths clear of the walls,
    and the run reports a wall collision if an agent strays into one.
    """

    def __init__(self, lookahead: float = 0.3):
        if lookahead <= 0.0:
            raise ValueError(f"lookahead must be positive, got {lookahead}")
        self.lookahead = lookahead

    def compute(self, agent: AgentRuntime, speed_bound: float, world: World) -> Control:
        if agent.done:
            return Control(0.0, 0.0)
        path = agent.spec.path
        target = path.point_at(min(path.length, agent.path_s + self.lookahead))
        desired_heading = math.atan2(target[1] - agent.pose.y, target[0] - agent.pose.x)
        heading_error = wrap_angle(desired_heading - agent.pose.theta)
        limit = agent.spec.max_turn_rate
        omega = min(limit, max(-limit, heading_error / world.dt))
        speed = min(agent.spec.max_speed, max(0.0, speed_bound))
        return Control(speed, omega)

    def params(self) -> dict:
        return {"backend": self.name, "lookahead": self.lookahead}
