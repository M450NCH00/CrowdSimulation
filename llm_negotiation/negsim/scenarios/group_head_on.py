"""Small groups meeting head-on in round 1's corridor (issue #110, RF-32).

The corridor of :mod:`~negsim.scenarios.wide_corridor_head_on`, with any number of people walking
each way instead of one::

      ============================================================   wall
                                                              y = +width / 2
        agent 0  ---->                            <----  agent 2
        agent 1  ---->
                                                              y = -width / 2
      ============================================================   wall
       x = -start_distance                      x = +start_distance

``eastbound`` and ``westbound`` list each person's line of travel, as a distance from the centre
line (``y``, the same frame as ``wide_corridor_head_on``'s ``lateral_offsets``: an eastbound
person's left is ``+y``, a westbound person's ``-y``). Each walks a straight line parallel to the
walls to the far start line, at its own offset. The eastbound people are agents ``0 .. e-1``, in the
order listed, and the westbound ones follow. People walking one way start abreast, on one start
line: a side-by-side group. The two-person scenario is unchanged; this one is a new type.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..configutil import ConfigError, as_number, check_keys
from ..core.geometry import Polyline, Rect
from .crowd_base import CrowdLayout, CrowdScenario, CrowdScenarioSpec, Placement

EASTBOUND, WESTBOUND = "eastbound", "westbound"


def _offsets(raw: Any, where: str) -> list[float]:
    if not isinstance(raw, (list, tuple)) or not raw:
        raise ConfigError(f"{where}: a non-empty list of lateral offsets (m)")
    return [as_number(value, f"{where}[{index}]") for index, value in enumerate(raw)]


class GroupHeadOnScenario(CrowdScenario):
    type_name = "group_head_on"

    def geometry(self, raw: Mapping[str, Any], where: str) -> dict[str, Any]:
        check_keys(raw, where, ("length", "width", "start_distance", EASTBOUND, WESTBOUND), ("wall_thickness",))
        geometry: dict[str, Any] = {
            key: as_number(raw[key], f"{where}.{key}", minimum=0.0, strict_minimum=True)
            for key in ("length", "width", "start_distance")
        }
        geometry["wall_thickness"] = as_number(
            raw.get("wall_thickness", 0.5), f"{where}.wall_thickness", minimum=0.0, strict_minimum=True
        )
        for side in (EASTBOUND, WESTBOUND):
            geometry[side] = _offsets(raw[side], f"{where}.{side}")
        if 2.0 * geometry["start_distance"] > geometry["length"]:
            raise ConfigError(f"{where}: the agents start outside the corridor (2 * start_distance > length)")
        return geometry

    def layout(self, geometry: Mapping[str, Any], seed: int) -> CrowdLayout:
        half_length, half_width = geometry["length"] / 2.0, geometry["width"] / 2.0
        thickness, distance = geometry["wall_thickness"], geometry["start_distance"]
        placements = [
            Placement((-distance, y), (distance, y), Polyline([(-distance, y), (distance, y)]), EASTBOUND)
            for y in geometry[EASTBOUND]
        ] + [
            Placement((distance, y), (-distance, y), Polyline([(distance, y), (-distance, y)]), WESTBOUND)
            for y in geometry[WESTBOUND]
        ]
        walls = (
            Rect(-half_length, half_width, half_length, half_width + thickness),
            Rect(-half_length, -half_width - thickness, half_length, -half_width),
        )
        return CrowdLayout(tuple(placements), walls)

    def check(self, spec: CrowdScenarioSpec) -> None:
        # A body overlapping a wall is refused by CrowdScenario.build for every scenario.
        for side in (EASTBOUND, WESTBOUND):
            mine = sorted((agent.start.xy[1], agent) for agent in spec.agents if agent.group == side)
            for (y0, a), (y1, b) in zip(mine, mine[1:]):
                if y1 - y0 < a.radius + b.radius:
                    raise ConfigError(f"scenario '{self.type_name}': agents {a.agent_id} and {b.agent_id} ({side}) overlap at the start")
