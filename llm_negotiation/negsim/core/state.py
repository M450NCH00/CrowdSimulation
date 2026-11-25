"""State and control of one agent.

GameChat uses "single-integrator unicycle dynamics. The state (x, y, theta) consists of 2D
position and heading, and the control inputs (v, omega) consist of both linear and angular
velocity" (arXiv:2503.12333v1, Sec IV-A).
"""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import Vec


@dataclass(frozen=True)
class Pose:
    """Position in metres and heading in radians."""

    x: float
    y: float
    theta: float

    @property
    def xy(self) -> Vec:
        return (self.x, self.y)


@dataclass(frozen=True)
class Control:
    """Linear velocity ``v`` in m/s and angular velocity ``omega`` in rad/s."""

    v: float
    omega: float
