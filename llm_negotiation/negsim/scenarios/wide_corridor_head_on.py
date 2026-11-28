"""Two agents meeting head-on in a corridor wide enough for them to pass.

The corridor runs along the x axis and is centred on the origin::

      ============================================================   wall
                                                              y = +width / 2
        agent 0  ---->                            <----  agent 1
                                                              y = -width / 2
      ============================================================   wall
       x = -start_distance                      x = +start_distance

Each agent walks a straight line parallel to the walls, to the point the other started
from, shifted by its own lateral offset. With both offsets zero the two are exactly
head-on and the scene is symmetric under a half turn *and* under a reflection in the
centre line of the corridor; this is the case in which neither side is nearer. With
offsets ``[d, -d]`` each agent starts a little to its own left, the reflection symmetry
is gone, and one passing side is nearer than the other.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..configutil import ConfigError, as_number, check_keys
from ..core.geometry import Polyline, Rect
from .crowd_base import CrowdLayout, CrowdScenario, CrowdScenarioSpec, Placement, number_list


class WideCorridorHeadOnScenario(CrowdScenario):
    type_name = "wide_corridor_head_on"

    def geometry(self, raw: Mapping[str, Any], where: str) -> dict[str, Any]:
        check_keys(raw, where, ("length", "width", "start_distance"), ("wall_thickness", "lateral_offsets"))
        geometry: dict[str, Any] = {
            key: as_number(raw[key], f"{where}.{key}", minimum=0.0, strict_minimum=True)
            for key in ("length", "width", "start_distance")
        }
        geometry["wall_thickness"] = as_number(
            raw.get("wall_thickness", 0.5), f"{where}.wall_thickness", minimum=0.0, strict_minimum=True
        )
        geometry["lateral_offsets"] = list(
            number_list(raw.get("lateral_offsets", [0.0, 0.0]), f"{where}.lateral_offsets", 2)
        )
        if 2.0 * geometry["start_distance"] > geometry["length"]:
            raise ConfigError(f"{where}: the agents start outside the corridor (2 * start_distance > length)")
        return geometry

    def layout(self, geometry: Mapping[str, Any], seed: int) -> CrowdLayout:
        half_length, half_width = geometry["length"] / 2.0, geometry["width"] / 2.0
        thickness, distance = geometry["wall_thickness"], geometry["start_distance"]
        y0, y1 = geometry["lateral_offsets"]
        east = Placement((-distance, y0), (distance, y0), Polyline([(-distance, y0), (distance, y0)]), "eastbound")
        west = Placement((distance, y1), (-distance, y1), Polyline([(distance, y1), (-distance, y1)]), "westbound")
        walls = (
            Rect(-half_length, half_width, half_length, half_width + thickness),
            Rect(-half_length, -half_width - thickness, half_length, -half_width),
        )
        return CrowdLayout((east, west), walls)

    def check(self, spec: CrowdScenarioSpec) -> None:
        total = sum(2.0 * agent.radius for agent in spec.agents)
        if total >= spec.geometry["width"]:
            raise ConfigError(
                f"scenario '{self.type_name}': the two agents are {total:.2f} m wide together and cannot "
                f"pass in a corridor {spec.geometry['width']:.2f} m wide; this scenario needs room to pass"
            )
