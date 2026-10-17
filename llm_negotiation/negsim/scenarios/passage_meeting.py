"""Two people who meet inside a single-file passage (issue #32, Part 2.2).

The layout of ``corridor_to_bottleneck`` (a wide corridor, a stretch only one person can use at a
time, a wide corridor again), with one difference: the two do not start in the wide parts. They
start **inside the passage, at the point where they meet**, facing each other, each having walked
some way in from its own end::

      ==================================================================   outer wall
                         +----------------------+
        wide approach    |      wall block      |    wide approach
                         +----------------------+
                           0 ->  gap  <- 1                              y = 0
                         +----------------------+
                         |      wall block      |
                         +----------------------+
      ==================================================================   outer wall
                     x = -length / 2       x = +length / 2

Agent 0 came in at the west end and walks east; agent 1 came in at the east end and walks west.
``travelled`` gives how far each has walked in, its centre's distance from the end it came in by,
so their centres are ``passage_length - travelled[0] - travelled[1]`` apart. Equal values are a
meeting in the middle; unequal ones put the meeting nearer the end of the one that has walked
less. Each path runs from where the agent starts along the centre line, out of the far end, and
on to its own side of the corridor, as in ``corridor_to_bottleneck``; it ends ``exit_setback``
beyond that end.

The meeting has already happened when the run starts: what ORCA, the arbiter or a rule does next
is the experiment. By default the two **start at rest**, having stopped face to face
(``start_speed`` 0). ``start_speed: preferred`` starts each walking toward the other at its own
preferred speed instead, as in every other scenario (and as the arbiter's behaviour was first
measured, ``docs/derivations.md``, section 17.1); a number starts both at that speed. A walking
start leaves ORCA a collision to undo on the first step. Whoever backs out does so without a path
behind it to follow: it backs along the passage (``docs/derivations.md``, section 17).
"""

from __future__ import annotations

from typing import Any, Mapping

from ..configutil import ConfigError, as_number, check_keys
from ..core.geometry import Polyline, Rect
from .crowd_base import CrowdLayout, CrowdScenario, CrowdScenarioSpec, Placement, SingleFileSegment, number_list

#: ``start_speed: preferred``: each starts walking at its own preferred speed, as the agents of
#: every other scenario do.
START_PREFERRED = "preferred"
_LENGTHS = (
    "approach_width",
    "approach_length",
    "passage_width",
    "passage_length",
    "merge_distance",
    "lateral_offset",
    "exit_setback",
)


class PassageMeetingScenario(CrowdScenario):
    type_name = "passage_meeting"

    def geometry(self, raw: Mapping[str, Any], where: str) -> dict[str, Any]:
        check_keys(raw, where, (*_LENGTHS, "travelled"), ("wall_thickness", "start_speed"))
        geometry: dict[str, Any] = {
            key: as_number(raw[key], f"{where}.{key}", minimum=0.0, strict_minimum=True) for key in _LENGTHS
        }
        geometry["travelled"] = list(number_list(raw["travelled"], f"{where}.travelled", 2, minimum=0.0))
        geometry["wall_thickness"] = as_number(
            raw.get("wall_thickness", 0.5), f"{where}.wall_thickness", minimum=0.0, strict_minimum=True
        )
        start = raw.get("start_speed", 0.0)
        geometry["start_speed"] = START_PREFERRED if start == START_PREFERRED else as_number(start, f"{where}.start_speed", minimum=0.0)
        length = geometry["passage_length"]
        if geometry["passage_width"] >= geometry["approach_width"]:
            raise ConfigError(f"{where}: passage_width must be less than approach_width")
        for index, distance in enumerate(geometry["travelled"]):
            if not 0.0 < distance < length:
                raise ConfigError(
                    f"{where}.travelled[{index}]: {distance} m puts agent {index} outside the passage, which is {length} m "
                    "long; each starts inside it"
                )
        if sum(geometry["travelled"]) >= length:
            raise ConfigError(
                f"{where}.travelled: {geometry['travelled']} m add up to the passage's length ({length} m) or more: the two "
                "would start past each other"
            )
        if not geometry["merge_distance"] < geometry["exit_setback"] <= geometry["approach_length"]:
            raise ConfigError(
                f"{where}: need merge_distance < exit_setback <= approach_length (a path leaves the centre line in the "
                "wide part and ends inside it)"
            )
        if geometry["lateral_offset"] >= geometry["approach_width"] / 2.0:
            raise ConfigError(f"{where}: lateral_offset puts a path outside the wide part of the corridor")
        return geometry

    def layout(self, geometry: Mapping[str, Any], seed: int) -> CrowdLayout:
        g = geometry
        half = g["passage_length"] / 2.0
        half_narrow, half_wide = g["passage_width"] / 2.0, g["approach_width"] / 2.0
        far = half + g["approach_length"]
        x_merge, x_end = half + g["merge_distance"], half + g["exit_setback"]
        y_off = g["lateral_offset"]
        west_start, east_start = -half + g["travelled"][0], half - g["travelled"][1]
        start_speed = None if g["start_speed"] == START_PREFERRED else g["start_speed"]
        # Each keeps to its own right once out: south of the centre line walking east, north walking west.
        placements = (
            Placement(
                (west_start, 0.0), (x_end, -y_off), Polyline([(west_start, 0.0), (x_merge, 0.0), (x_end, -y_off)]), "eastbound",
                initial_speed=start_speed,
            ),
            Placement(
                (east_start, 0.0), (-x_end, y_off), Polyline([(east_start, 0.0), (-x_merge, 0.0), (-x_end, y_off)]), "westbound",
                initial_speed=start_speed,
            ),
        )
        t = g["wall_thickness"]
        walls = (
            Rect(-far, half_wide, far, half_wide + t),
            Rect(-far, -half_wide - t, far, -half_wide),
            Rect(-half, half_narrow, half, half_wide),
            Rect(-half, -half_wide, half, -half_narrow),
        )
        segment = SingleFileSegment("passage", Rect(-half, -half_narrow, half, half_narrow), g["passage_width"])
        return CrowdLayout(placements, walls, (segment,))

    def check(self, spec: CrowdScenarioSpec) -> None:
        narrow, wide = spec.geometry["passage_width"], spec.geometry["approach_width"]
        total = sum(2.0 * agent.radius for agent in spec.agents)
        if total <= narrow:
            raise ConfigError(
                f"scenario '{self.type_name}': the two agents are {total:.2f} m wide together and could pass each other "
                f"in a passage {narrow:.2f} m wide; it is meant to be single-file"
            )
        if total >= wide:
            raise ConfigError(
                f"scenario '{self.type_name}': the two agents are {total:.2f} m wide together and cannot pass in the "
                f"wide part of the corridor ({wide:.2f} m)"
            )
