"""Intersection scenario (GameChat, arXiv:2503.12333v1, Sec V-A).

"the intersection the agents must pass through is 0.4 m by 0.4 m. Both start 2 m away from
the center of the intersection and their goals are 1 m away on the other side."

One agent comes up from the south, the other in from the west, as in the repository
(``scenarios.py:66-70``, commit c49c35a). The middle of the intersection is the origin.
"""

from __future__ import annotations

import math
from typing import Mapping

from ..core.geometry import Polyline, Rect
from ..core.state import Pose
from .base import Layout, RegionInfo, Scenario, SlotLayout


class IntersectionScenario(Scenario):
    type_name = "intersection"
    geometry_keys = ("size", "wall_extent", "start_distance", "goal_distance")

    def layout(self, geometry: Mapping[str, float], offsets: tuple[float, float]) -> Layout:
        g = geometry
        half = g["size"] / 2.0
        slots = []
        # (direction of travel, side the agent comes from, start offset)
        for (ux, uy), side, offset in (((0.0, 1.0), "south", offsets[0]), ((1.0, 0.0), "west", offsets[1])):
            back = g["start_distance"] + offset
            start = (-ux * back, -uy * back)
            goal = (ux * g["goal_distance"], uy * g["goal_distance"])
            path = Polyline([start, goal])
            slots.append(
                SlotLayout(
                    start=Pose(start[0], start[1], math.atan2(uy, ux)),
                    goal=goal,
                    path=path,
                    side=side,
                    region_entry_s=back - half,
                    region_exit_s=back + half,
                )
            )
        far = g["wall_extent"]
        obstacles = tuple(
            Rect(min(sx * half, sx * far), min(sy * half, sy * far), max(sx * half, sx * far), max(sy * half, sy * far))
            for sx in (-1.0, 1.0)
            for sy in (-1.0, 1.0)
        )
        region = RegionInfo("intersection", width=g["size"], length=g["size"])
        return Layout((slots[0], slots[1]), obstacles, region)
