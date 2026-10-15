"""Simulator core: state, dynamics models, agents, world, geometry."""

from .agent import AgentRuntime, AgentSpec
from .dynamics import (
    DYNAMICS,
    DynamicsModel,
    HolonomicDynamics,
    UnicycleDynamics,
    clip_control,
    clip_velocity,
    holonomic_step,
    make_dynamics,
    unicycle_step,
)
from .geometry import Polyline, Rect, Vec, dist, line_intersection, ray_intersection, wrap_angle
from .state import Control, Pose
from .world import ARRIVAL_GOAL_DISC, ARRIVAL_PATH_END, ARRIVAL_RULES, World

__all__ = [
    "ARRIVAL_GOAL_DISC",
    "ARRIVAL_PATH_END",
    "ARRIVAL_RULES",
    "DYNAMICS",
    "AgentRuntime",
    "AgentSpec",
    "Control",
    "DynamicsModel",
    "HolonomicDynamics",
    "Polyline",
    "Pose",
    "Rect",
    "UnicycleDynamics",
    "Vec",
    "World",
    "clip_control",
    "clip_velocity",
    "dist",
    "holonomic_step",
    "line_intersection",
    "make_dynamics",
    "ray_intersection",
    "unicycle_step",
    "wrap_angle",
]
