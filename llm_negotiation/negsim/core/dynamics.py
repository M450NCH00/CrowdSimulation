"""Unicycle dynamics.

Continuous model (arXiv:2503.12333v1, Sec IV-A, eq. 2)::

    x'     = v cos(theta)
    y'     = v sin(theta)
    theta' = omega

Integrated with one forward-Euler step per time step, which is what the GameChat repository
does (``environment.py:33``, ``x_next = _x + A*Ts + B@_u*Ts``, commit c49c35a).
"""

from __future__ import annotations

import math

from .geometry import wrap_angle
from .state import Control, Pose


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
