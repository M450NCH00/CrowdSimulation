"""Doorway scenario (GameChat, arXiv:2503.12333v1, Sec V-A).

"both agents must pass through a doorway of size 0.4 m. Both agents start 2 m to the left
of the doorway and 0.5 m north or south of it, with goals on the opposite side."

The paper does not say where the goals are or which way the agents face at the start;
those come from the repository (``scenarios.py:11-15``, commit c49c35a): goals 1 m beyond
the doorway and 0.2 m off the centre line on the far side of it, so the two straight
paths cross just past the doorway, and initial headings turned 10 degrees toward the
centre line. Coordinates here put the middle of the doorway at the origin.
"""

from __future__ import annotations

import math
from typing import Mapping

from ..core.geometry import Polyline, Rect
from ..core.state import Pose
from .base import Layout, RegionInfo, Scenario, SlotLayout


class DoorwayScenario(Scenario):
    type_name = "doorway"
    geometry_keys = (
        "door_width",
        "wall_thickness",
        "wall_extent",
        "start_distance",
        "start_lateral",
        "goal_distance",
        "goal_lateral",
        "start_heading_deg",
    )

    def layout(self, geometry: Mapping[str, float], offsets: tuple[float, float]) -> Layout:
        g = geometry
        half_door, half_wall = g["door_width"] / 2.0, g["wall_thickness"] / 2.0
        slots = []
        for sign, side, offset in ((1.0, "north", offsets[0]), (-1.0, "south", offsets[1])):
            start = (-(g["start_distance"] + offset), sign * g["start_lateral"])
            goal = (g["goal_distance"], -sign * g["goal_lateral"])
            path = Polyline([start, goal])
            heading = -sign * math.radians(g["start_heading_deg"])
            slots.append(
                SlotLayout(
                    start=Pose(start[0], start[1], heading),
                    goal=goal,
                    path=path,
                    side=side,
                    region_entry_s=_arc_length_at_x(path, -half_wall),
                    region_exit_s=_arc_length_at_x(path, half_wall),
                )
            )
        obstacles = (
            Rect(-half_wall, half_door, half_wall, g["wall_extent"]),
            Rect(-half_wall, -g["wall_extent"], half_wall, -half_door),
        )
        region = RegionInfo("doorway", width=g["door_width"], length=g["wall_thickness"])
        return Layout((slots[0], slots[1]), obstacles, region)


def _arc_length_at_x(path: Polyline, x: float) -> float:
    """Arc length at which a two-point path crosses the vertical line at ``x``."""
    (x0, _), (x1, _) = path.points
    return (x - x0) / (x1 - x0) * path.length
