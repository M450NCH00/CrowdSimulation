"""Time to the conflict region, and whether two agents would be in it at the same time."""

from __future__ import annotations

import math
from typing import Mapping

from .detection import Conflict
from .zone import ZoneView

Interval = tuple[float, float]


def time_to_region(view: ZoneView, speed: float) -> float:
    """Seconds until the agent enters its zone at ``speed`` (GameChat's TTQ); 0 if inside."""
    if view.d_in <= 0.0:
        return 0.0
    return view.d_in / speed if speed > 0.0 else math.inf


def time_to_clear(view: ZoneView, speed: float) -> float:
    """Seconds until the agent has left its zone at ``speed``; 0 if it already has."""
    if view.d_out <= 0.0:
        return 0.0
    return view.d_out / speed if speed > 0.0 else math.inf


def occupancy_interval(view: ZoneView, speed: float) -> Interval:
    """The time interval, from now, during which the agent would be inside its zone."""
    return time_to_region(view, speed), time_to_clear(view, speed)


def intervals_overlap(a: Interval, b: Interval, tol: float = 1e-9) -> bool:
    """True if two open intervals share more than a point.

    One agent arriving at the instant the other leaves is not an overlap. The paper makes
    the same choice: the space an agent occupies "does not contain the endpoints of the
    agent" (arXiv:2503.12333v1, Sec IV-A).
    """
    return a[0] < b[1] - tol and b[0] < a[1] - tol


def is_social_minigame(conflict: Conflict, speeds: Mapping[int, float]) -> bool:
    """GameChat's test for a social mini-game, with the conflict point widened to a zone.

    "If the rays intersect and the time intervals when the agents will occupy Q overlap,
    then the agents are in an SMG" (arXiv:2503.12333v1, Sec IV-B). ``speeds`` are the
    speeds the agents would travel at if left alone.
    """
    if not conflict.live:
        return False
    i, j = conflict.agent_ids
    return intervals_overlap(
        occupancy_interval(conflict.views[i], speeds[i]),
        occupancy_interval(conflict.views[j], speeds[j]),
    )
