"""A faster agent coming up behind a slower one, both walking the same way. No walls.

::

        agent 0 (faster)  ---->          agent 1 (slower)  -->            goals
        x = 0                            x = headway                      x = travel_distance

The two preferred speeds are set per agent in the config (``agents.overrides``). With both
lateral offsets zero the faster agent is exactly behind the slower one and neither side
is nearer.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..configutil import ConfigError, as_number, check_keys
from ..core.geometry import Polyline
from .crowd_base import CrowdLayout, CrowdScenario, CrowdScenarioSpec, Placement, number_list


class OvertakingScenario(CrowdScenario):
    type_name = "overtaking"

    def geometry(self, raw: Mapping[str, Any], where: str) -> dict[str, Any]:
        check_keys(raw, where, ("headway", "travel_distance"), ("lateral_offsets",))
        geometry: dict[str, Any] = {
            key: as_number(raw[key], f"{where}.{key}", minimum=0.0, strict_minimum=True)
            for key in ("headway", "travel_distance")
        }
        geometry["lateral_offsets"] = list(
            number_list(raw.get("lateral_offsets", [0.0, 0.0]), f"{where}.lateral_offsets", 2)
        )
        if geometry["headway"] >= geometry["travel_distance"]:
            raise ConfigError(
                f"{where}: headway must be less than travel_distance, or the slower agent starts at its goal"
            )
        return geometry

    def layout(self, geometry: Mapping[str, Any], seed: int) -> CrowdLayout:
        headway, distance = geometry["headway"], geometry["travel_distance"]
        y0, y1 = geometry["lateral_offsets"]
        behind = Placement((0.0, y0), (distance, y0), Polyline([(0.0, y0), (distance, y0)]), "behind")
        ahead = Placement((headway, y1), (distance, y1), Polyline([(headway, y1), (distance, y1)]), "ahead")
        return CrowdLayout((behind, ahead), ())

    def check(self, spec: CrowdScenarioSpec) -> None:
        behind, ahead = spec.agents
        if behind.preferred_speed <= ahead.preferred_speed:
            raise ConfigError(
                f"scenario '{self.type_name}': agent 0 starts behind and must be the faster one, but its "
                f"preferred speed is {behind.preferred_speed} m/s against {ahead.preferred_speed} m/s for "
                "agent 1. Set the two speeds under agents.overrides."
            )
