"""A wide corridor that narrows to a segment only one agent can use at a time.

The corridor runs along the x axis; the narrow segment is centred on the origin::

      ==================================================================   outer wall
                         +----------------------+
        wide approach    |      wall block      |    wide approach
                         +----------------------+
                           single-file segment                          y = 0
                         +----------------------+
                         |      wall block      |
                         +----------------------+
      ==================================================================   outer wall
                     x = -length / 2       x = +length / 2

In the wide parts the agents are steered by ORCA. The segment is where the arbiter of
issue #24 decides who goes first.

``flow: opposing``
    Agent 0 starts in the west and agent 1 in the east, and each has to get to the other
    end. Each keeps to its own right in the wide parts: it starts ``lateral_offset`` to
    the right of the centre line, joins the centre line ``merge_distance`` before the
    mouth of the segment, and leaves it the same distance after the far mouth. The layout
    is the hallway of issue #24 with wide approaches, and is symmetric under a half turn.

``flow: merging``
    Both agents start in the west, side by side, agent 0 to the north of the centre line
    and agent 1 to the south, and both have to get through to the east, where each goes
    back to its own side.

Why the paths leave the centre line in the wide parts: an agent that waits its turn on
the centre line stands exactly where the other has to come out.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..configutil import ConfigError, as_choice, as_number, check_keys
from ..core.geometry import Polyline, Rect
from .crowd_base import CrowdLayout, CrowdScenario, CrowdScenarioSpec, Placement, SingleFileSegment

FLOW_OPPOSING, FLOW_MERGING = "opposing", "merging"
FLOWS = (FLOW_OPPOSING, FLOW_MERGING)

_LENGTHS = (
    "approach_width",
    "approach_length",
    "bottleneck_width",
    "bottleneck_length",
    "start_setback",
    "merge_distance",
    "lateral_offset",
)


class CorridorToBottleneckScenario(CrowdScenario):
    type_name = "corridor_to_bottleneck"

    def geometry(self, raw: Mapping[str, Any], where: str) -> dict[str, Any]:
        check_keys(raw, where, _LENGTHS, ("wall_thickness", "flow"))
        geometry: dict[str, Any] = {
            key: as_number(raw[key], f"{where}.{key}", minimum=0.0, strict_minimum=True) for key in _LENGTHS
        }
        geometry["wall_thickness"] = as_number(
            raw.get("wall_thickness", 0.5), f"{where}.wall_thickness", minimum=0.0, strict_minimum=True
        )
        geometry["flow"] = as_choice(raw.get("flow", FLOW_OPPOSING), f"{where}.flow", FLOWS)
        if geometry["bottleneck_width"] >= geometry["approach_width"]:
            raise ConfigError(f"{where}: bottleneck_width must be less than approach_width")
        if not geometry["merge_distance"] < geometry["start_setback"] <= geometry["approach_length"]:
            raise ConfigError(
                f"{where}: need merge_distance < start_setback <= approach_length (an agent starts in "
                "the wide part and joins the centre line before it reaches the mouth of the segment)"
            )
        if geometry["lateral_offset"] >= geometry["approach_width"] / 2.0:
            raise ConfigError(f"{where}: lateral_offset puts the agents outside the wide part of the corridor")
        return geometry

    def layout(self, geometry: Mapping[str, Any], seed: int) -> CrowdLayout:
        g = geometry
        half_length = g["bottleneck_length"] / 2.0
        half_narrow, half_wide = g["bottleneck_width"] / 2.0, g["approach_width"] / 2.0
        far = half_length + g["approach_length"]
        x_start = half_length + g["start_setback"]
        x_merge = half_length + g["merge_distance"]
        y_off = g["lateral_offset"]

        def through(start_x: float, start_y: float, goal_y: float, group: str) -> Placement:
            """A path from one wide part to the other along the centre line of the segment."""
            sign = 1.0 if start_x < 0.0 else -1.0  # +1: walks east
            start, goal = (start_x, start_y), (-start_x, goal_y)
            path = Polyline([start, (-sign * x_merge, 0.0), (sign * x_merge, 0.0), goal])
            return Placement(start, goal, path, group)

        if g["flow"] == FLOW_OPPOSING:
            # Each keeps to its own right: south of the centre line walking east, north walking west.
            placements = (
                through(-x_start, -y_off, -y_off, "eastbound"),
                through(x_start, y_off, y_off, "westbound"),
            )
        else:
            placements = (
                through(-x_start, y_off, y_off, "north_lane"),
                through(-x_start, -y_off, -y_off, "south_lane"),
            )

        t = g["wall_thickness"]
        walls = (
            Rect(-far, half_wide, far, half_wide + t),
            Rect(-far, -half_wide - t, far, -half_wide),
            Rect(-half_length, half_narrow, half_length, half_wide),
            Rect(-half_length, -half_wide, half_length, -half_narrow),
        )
        segment = SingleFileSegment(
            "bottleneck", Rect(-half_length, -half_narrow, half_length, half_narrow), g["bottleneck_width"]
        )
        return CrowdLayout(placements, walls, (segment,))

    def check(self, spec: CrowdScenarioSpec) -> None:
        # (An agent too wide for the segment has already been refused: its path would pass
        # closer to a wall than its own radius.)
        narrow, wide = spec.geometry["bottleneck_width"], spec.geometry["approach_width"]
        total = sum(2.0 * agent.radius for agent in spec.agents)
        if total <= narrow:
            raise ConfigError(
                f"scenario '{self.type_name}': the two agents are {total:.2f} m wide together and could "
                f"pass each other in a segment {narrow:.2f} m wide; it is meant to be single-file"
            )
        if total >= wide:
            raise ConfigError(
                f"scenario '{self.type_name}': the two agents are {total:.2f} m wide together and cannot "
                f"pass in the wide part of the corridor ({wide:.2f} m)"
            )
