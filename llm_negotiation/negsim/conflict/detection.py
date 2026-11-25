"""Conflict detection between a pair of agents.

A detector predicts where each agent will go and returns the conflict zone that follows
from those predictions. Two predictors are provided:

``heading_ray``
    GameChat's: "the agents compute a ray originating from their respective position and
    moving in the direction of their respective headings" (arXiv:2503.12333v1, Sec IV-B).
    It needs nothing but what one agent can see of the other, and it is right whenever the
    agents travel in straight lines that cross. Used for the doorway and the intersection.

``desired_path``
    Uses each agent's desired path. Needed for the head-on hallway, where the two heading
    rays are collinear and so never "intersect", and where the agents only stop being in
    each other's way some distance beyond the hallway mouth.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Optional

from ..core.agent import AgentRuntime
from ..core.geometry import Vec
from .zone import ZoneView, crossing_zone_views, path_zone_interval


@dataclass(frozen=True)
class Conflict:
    """The conflict zone between two agents, seen from each of them."""

    agent_ids: tuple[int, int]
    views: Mapping[int, ZoneView]
    point: Optional[Vec] = None

    @property
    def live(self) -> bool:
        """True until one of the two agents has left the zone."""
        return all(view.d_out > 0.0 for view in self.views.values())

    def other(self, agent_id: int) -> int:
        i, j = self.agent_ids
        return j if agent_id == i else i


class ConflictDetector(ABC):
    """Returns the conflict zone of a pair of agents, if their predicted paths have one."""

    name: str

    def __init__(self, safety_margin: float):
        if safety_margin < 0.0:
            raise ValueError(f"safety_margin must not be negative, got {safety_margin}")
        self.safety_margin = safety_margin

    def clearance(self, a: AgentRuntime, b: AgentRuntime) -> float:
        return a.spec.radius + b.spec.radius + self.safety_margin

    @abstractmethod
    def zone(self, a: AgentRuntime, b: AgentRuntime) -> Optional[Conflict]:
        """The zone between ``a`` and ``b`` from their current states, or ``None``."""


class HeadingRayDetector(ConflictDetector):
    name = "heading_ray"

    def __init__(self, safety_margin: float, zone_half_length: Optional[float] = None):
        super().__init__(safety_margin)
        if zone_half_length is not None and zone_half_length < 0.0:
            raise ValueError(f"zone_half_length must not be negative, got {zone_half_length}")
        self.zone_half_length = zone_half_length

    def zone(self, a: AgentRuntime, b: AgentRuntime) -> Optional[Conflict]:
        result = crossing_zone_views(
            a.pose.xy,
            a.pose.theta,
            b.pose.xy,
            b.pose.theta,
            self.clearance(a, b),
            self.zone_half_length,
        )
        if result is None:
            return None
        view_a, view_b, point = result
        # GameChat asks for the crossing point to be ahead of both agents. Here it may be
        # behind one of them, because an agent that has passed the point can still be
        # inside the zone; it is only dropped once it is behind both (they are moving apart).
        if view_a.d_in + view_a.d_out < 0.0 and view_b.d_in + view_b.d_out < 0.0:
            return None
        return Conflict((a.agent_id, b.agent_id), {a.agent_id: view_a, b.agent_id: view_b}, point)


class DesiredPathDetector(ConflictDetector):
    name = "desired_path"

    def __init__(self, safety_margin: float, sample_spacing: float = 0.01):
        super().__init__(safety_margin)
        self.sample_spacing = sample_spacing
        self._intervals: dict[tuple[int, int], Optional[tuple[float, float]]] = {}

    def _interval(self, a: AgentRuntime, b: AgentRuntime) -> Optional[tuple[float, float]]:
        key = (a.agent_id, b.agent_id)
        if key not in self._intervals:
            self._intervals[key] = path_zone_interval(
                a.spec.path, b.spec.path, self.clearance(a, b), self.sample_spacing
            )
        return self._intervals[key]

    def zone(self, a: AgentRuntime, b: AgentRuntime) -> Optional[Conflict]:
        interval_a, interval_b = self._interval(a, b), self._interval(b, a)
        if interval_a is None or interval_b is None:
            return None
        return Conflict(
            (a.agent_id, b.agent_id),
            {
                a.agent_id: ZoneView(interval_a[0] - a.path_s, interval_a[1] - a.path_s),
                b.agent_id: ZoneView(interval_b[0] - b.path_s, interval_b[1] - b.path_s),
            },
        )


def make_detector(
    predictor: str, safety_margin: float, zone_half_length: Optional[float] = None
) -> ConflictDetector:
    if predictor == HeadingRayDetector.name:
        return HeadingRayDetector(safety_margin, zone_half_length)
    if predictor == DesiredPathDetector.name:
        if zone_half_length is not None:
            raise ValueError(
                "zone_half_length can only be fixed with the heading_ray predictor; "
                "the desired_path predictor always computes the zone from the paths"
            )
        return DesiredPathDetector(safety_margin)
    raise ValueError(
        f"unknown conflict predictor {predictor!r}; expected 'heading_ray' or 'desired_path'"
    )
