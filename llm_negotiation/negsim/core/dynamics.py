"""Dynamics: how a command becomes motion.

Two models are provided.

``unicycle``
    GameChat's model (arXiv:2503.12333v1, Sec IV-A, eq. 2), used by every scenario of
    issue #24::

        x'     = v cos(theta)
        y'     = v sin(theta)
        theta' = omega

    integrated with one forward-Euler step per time step, which is what the GameChat
    repository does (``environment.py:33``, ``x_next = _x + A*Ts + B@_u*Ts``, commit
    c49c35a). Its command is a :class:`~negsim.core.state.Control` ``(v, omega)``.

``holonomic``
    The model ORCA assumes: "the robot is holonomic, i.e. it can move in any direction,
    such that the control input of each robot is simply given by a two-dimensional
    velocity vector" (van den Berg et al., "Reciprocal n-body collision avoidance",
    Sec 1). Its command is a velocity vector ``(vx, vy)``, and the position update is the
    paper's eq. 9, ``p_new = p + v_new * dt``.

The models sit behind one interface, :class:`DynamicsModel`, so that the layer that
chooses velocities does not know which one moves the agent. A model reports the velocity
it actually realised; that, not the command, is what other agents observe. A model for a
vehicle would take the same velocity command and realise the nearest motion its wheels
allow; nothing in ``negsim.avoidance`` would have to change for it (though ORCA's
guarantee would then need the tracking error accounted for, which is out of scope here).
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from .geometry import Vec, wrap_angle
from .state import Control, Pose

if TYPE_CHECKING:  # pragma: no cover - import cycle guard, types only
    from .agent import AgentRuntime


def unicycle_step(pose: Pose, control: Control, dt: float) -> Pose:
    """Advance one time step of length ``dt`` seconds."""
    return Pose(
        x=pose.x + control.v * math.cos(pose.theta) * dt,
        y=pose.y + control.v * math.sin(pose.theta) * dt,
        theta=wrap_angle(pose.theta + control.omega * dt),
    )


def clip_control(control: Control, max_speed: float, max_turn_rate: float) -> Control:
    """Clip a control to the actuator limits.

    Linear velocity is limited to ``[0, max_speed]``. GameChat's bounds are symmetric
    (``mpc_cbf.py:72-74``), which lets its robots reverse; a pedestrian model has no use
    for that, so reversing is not allowed here.
    """
    return Control(
        v=min(max_speed, max(0.0, control.v)),
        omega=min(max_turn_rate, max(-max_turn_rate, control.omega)),
    )


def holonomic_step(pose: Pose, velocity: Vec, dt: float, heading_eps: float = 1e-9) -> Pose:
    """Advance one time step at a constant velocity vector.

    The heading follows the direction of motion. An agent that is not moving keeps the
    heading it had, so that a stationary agent still faces somewhere.
    """
    vx, vy = velocity
    theta = math.atan2(vy, vx) if math.hypot(vx, vy) > heading_eps else pose.theta
    return Pose(x=pose.x + vx * dt, y=pose.y + vy * dt, theta=theta)


def clip_velocity(velocity: Vec, max_speed: float) -> Vec:
    """Shorten a velocity vector to ``max_speed`` if it is longer; the direction is kept."""
    vx, vy = velocity
    speed = math.hypot(vx, vy)
    if speed <= max_speed or speed == 0.0:
        return (vx, vy)
    scale = max_speed / speed
    return (vx * scale, vy * scale)


class DynamicsModel(ABC):
    """Turns one agent's command into its motion over one time step."""

    name: ClassVar[str]
    #: The command that leaves an agent where it is.
    idle: ClassVar[Any]

    @abstractmethod
    def advance(
        self, agent: "AgentRuntime", command: Any, dt: float
    ) -> tuple[Pose, Vec, float, Any]:
        """Return ``(new pose, velocity realised, its speed, command as applied after clipping)``."""


class UnicycleDynamics(DynamicsModel):
    """Command: :class:`Control`. The agent moves along its heading and turns at ``omega``."""

    name = "unicycle"
    idle = Control(0.0, 0.0)

    def advance(
        self, agent: "AgentRuntime", command: Control, dt: float
    ) -> tuple[Pose, Vec, float, Control]:
        control = clip_control(command, agent.spec.max_speed, agent.spec.max_turn_rate)
        theta = agent.pose.theta
        velocity = (control.v * math.cos(theta), control.v * math.sin(theta))
        return unicycle_step(agent.pose, control, dt), velocity, control.v, control


class HolonomicDynamics(DynamicsModel):
    """Command: a velocity vector ``(vx, vy)``, realised exactly up to the speed limit."""

    name = "holonomic"
    idle = (0.0, 0.0)

    def advance(
        self, agent: "AgentRuntime", command: Vec, dt: float
    ) -> tuple[Pose, Vec, float, Vec]:
        velocity = clip_velocity(command, agent.spec.max_speed)
        speed = math.hypot(velocity[0], velocity[1])
        return holonomic_step(agent.pose, velocity, dt), velocity, speed, velocity


DYNAMICS: dict[str, type[DynamicsModel]] = {
    model.name: model for model in (UnicycleDynamics, HolonomicDynamics)
}


def make_dynamics(name: str) -> DynamicsModel:
    if name not in DYNAMICS:
        raise ValueError(f"unknown dynamics model {name!r}; available: {sorted(DYNAMICS)}")
    return DYNAMICS[name]()
