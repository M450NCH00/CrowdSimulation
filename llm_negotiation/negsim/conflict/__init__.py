"""Conflict layer: zones, detection, time to the conflict region, role assignment."""

from .detection import (
    Conflict,
    ConflictDetector,
    DesiredPathDetector,
    HeadingRayDetector,
    make_detector,
)
from .roles import Role, RoleDecision, RoleSource, break_tie, decide_roles, strategy1_leader
from .timing import (
    intervals_overlap,
    is_social_minigame,
    occupancy_interval,
    time_to_clear,
    time_to_region,
)
from .zone import ZoneView, crossing_zone_views, edge_quantities, path_zone_interval

__all__ = [
    "Conflict",
    "ConflictDetector",
    "DesiredPathDetector",
    "HeadingRayDetector",
    "Role",
    "RoleDecision",
    "RoleSource",
    "ZoneView",
    "break_tie",
    "crossing_zone_views",
    "decide_roles",
    "edge_quantities",
    "intervals_overlap",
    "is_social_minigame",
    "make_detector",
    "occupancy_interval",
    "path_zone_interval",
    "strategy1_leader",
    "time_to_clear",
    "time_to_region",
]
