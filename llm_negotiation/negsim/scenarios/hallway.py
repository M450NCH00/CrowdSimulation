"""Head-on hallway scenario — not in GameChat; this project's canonical case.

Two agents face each other across a hallway too narrow for them to pass, with a waiting
area at each end. The hallway runs along the x axis and is centred on the origin::

       waiting area (west)            hallway             waiting area (east)

                            +------------------------+
      east agent's goal  <--                          <--  east agent starts     north
                             ========================
      west agent starts  -->                          -->  west agent's goal     south
                            +------------------------+

Each agent keeps to its own right in the waiting areas: it starts ``lateral_offset`` to
the right of the centre line, joins the centre line ``merge_distance`` before the hallway
mouth, and leaves it the same distance after the far mouth. The east agent's path is the
west agent's turned through 180 degrees, so the scenario is symmetric.

Why the paths separate in the waiting areas: a follower that waits on the centre line
would stand exactly where the leader has to come out. With the paths apart, the follower
can wait beside the leader's exit path, and the conflict zone (``negsim.conflict``) ends
where the two paths are far enough apart for the agents to pass.
"""

from __future__ import annotations

from typing import Mapping

from ..configutil import ConfigError
from ..core.geometry import Polyline, Rect, dist
from ..core.state import Pose
from .base import Layout, RegionInfo, Scenario, ScenarioSpec, SlotLayout


class HallwayScenario(Scenario):
    type_name = "hallway"
    geometry_keys = (
        "length",
        "width",
        "room_width",
        "start_setback",
        "merge_distance",
        "lateral_offset",
    )

    def layout(self, geometry: Mapping[str, float], offsets: tuple[float, float]) -> Layout:
        g = geometry
        half_length = g["length"] / 2.0
        if not 0.0 < g["merge_distance"] < g["start_setback"]:
            raise ConfigError(
                "scenario 'hallway'.geometry: need 0 < merge_distance < start_setback "
                "(the path joins the centre line between the start and the hallway mouth)"
            )
        if g["lateral_offset"] <= 0.0:
            raise ConfigError(
                "scenario 'hallway'.geometry.lateral_offset must be positive: with the two "
                "paths on the same line in the waiting areas there is nowhere to wait"
            )
        x_start = half_length + g["start_setback"]
        x_merge = half_length + g["merge_distance"]
        y_off = g["lateral_offset"]

        slots = []
        # sign = +1: starts in the west and walks east; sign = -1: the same path turned 180 degrees.
        for sign, side, offset in ((1.0, "west", offsets[0]), (-1.0, "east", offsets[1])):
            start = (-sign * x_start, -sign * y_off)
            merge_in = (-sign * x_merge, 0.0)
            merge_out = (sign * x_merge, 0.0)
            goal = (sign * x_start, -sign * y_off)
            leg = dist(start, merge_in)
            # A start offset moves the agent back along its first leg, away from its goal.
            start = (
                start[0] - offset * (merge_in[0] - start[0]) / leg,
                start[1] - offset * (merge_in[1] - start[1]) / leg,
            )
            path = Polyline([start, merge_in, merge_out, goal])
            entry = leg + offset + g["merge_distance"]
            slots.append(
                SlotLayout(
                    start=Pose(start[0], start[1], path.heading_at(0.0)),
                    goal=goal,
                    path=path,
                    side=side,
                    region_entry_s=entry,
                    region_exit_s=entry + g["length"],
                )
            )
        half_room = g["room_width"] / 2.0
        half_width = g["width"] / 2.0
        if half_room <= half_width:
            raise ConfigError(
                "scenario 'hallway'.geometry: room_width must be greater than the hallway width"
            )
        obstacles = (
            Rect(-half_length, half_width, half_length, half_room),
            Rect(-half_length, -half_room, half_length, -half_width),
        )
        region = RegionInfo("hallway", width=g["width"], length=g["length"])
        return Layout((slots[0], slots[1]), obstacles, region)

    def check(self, spec: ScenarioSpec) -> None:
        total_width = sum(2.0 * agent.radius for agent in spec.agents)
        if total_width <= spec.region.width:
            raise ConfigError(
                f"scenario 'hallway': the two agents are {total_width:.2f} m wide together and "
                f"could pass each other in a hallway {spec.region.width:.2f} m wide; this "
                "scenario is meant to be a passage only one of them can use at a time"
            )
