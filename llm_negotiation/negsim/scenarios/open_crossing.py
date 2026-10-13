"""Two agents whose paths cross at a right angle, with no walls anywhere.

Agent 0 walks east along the x axis and agent 1 north along the y axis; the paths cross
at the origin::

                         ^  goal of agent 1
                         |
        agent 0  ------> + ------>  goal of agent 0
                         |
                         ^
                      agent 1

With equal approach distances and equal speeds both would be at the crossing at the same
instant, and the scene is symmetric under a reflection in the diagonal, which swaps the
two agents.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..configutil import as_number, check_keys
from ..core.geometry import Polyline
from .crowd_base import CrowdLayout, CrowdScenario, Placement, number_list


class OpenCrossingScenario(CrowdScenario):
    type_name = "open_crossing"

    def geometry(self, raw: Mapping[str, Any], where: str) -> dict[str, Any]:
        check_keys(raw, where, ("approach_distances", "goal_distance"))
        distances = number_list(raw["approach_distances"], f"{where}.approach_distances", 2, minimum=0.0)
        return {
            "approach_distances": list(distances),
            "goal_distance": as_number(
                raw["goal_distance"], f"{where}.goal_distance", minimum=0.0, strict_minimum=True
            ),
        }

    def layout(self, geometry: Mapping[str, Any], seed: int) -> CrowdLayout:
        d0, d1 = geometry["approach_distances"]
        beyond = geometry["goal_distance"]
        east = Placement((-d0, 0.0), (beyond, 0.0), Polyline([(-d0, 0.0), (beyond, 0.0)]), "eastbound")
        north = Placement((0.0, -d1), (0.0, beyond), Polyline([(0.0, -d1), (0.0, beyond)]), "northbound")
        return CrowdLayout((east, north), ())
