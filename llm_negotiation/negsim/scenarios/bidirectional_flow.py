"""Two crowds walking through each other along a corridor.

The corridor runs along the x axis and is open at both ends::

      ==================================================================   wall
       o o o o  ---->                                    <----  o o o o
       o o o o  ---->                                    <----  o o o o
       o o o o  ---->                                    <----  o o o o
      ==================================================================   wall
       x = -length / 2                                   x = +length / 2

``agents_per_direction`` agents start in a block at each end, on a square lattice of
spacing ``spawn_spacing`` that fills the width of the corridor row by row. Every agent
walks a straight line to the far end at the lateral position it started from. Agents
0 to N - 1 walk east, agents N to 2N - 1 walk west.

``spawn_jitter`` moves each starting position by a random amount, the same in every run
with the same seed. A perfect lattice is perfectly symmetric, and ORCA has no way of
resolving an exactly symmetric encounter (``docs/orca.md``, section 6); the jitter is
what a real crowd has anyway.
"""

from __future__ import annotations

import math
import random
from typing import Any, Mapping

from ..configutil import ConfigError, as_number, check_keys
from ..core.geometry import Polyline, Rect
from .crowd_base import CrowdLayout, CrowdScenario, Placement, whole_number


class BidirectionalFlowScenario(CrowdScenario):
    type_name = "bidirectional_flow"

    def geometry(self, raw: Mapping[str, Any], where: str) -> dict[str, Any]:
        check_keys(
            raw,
            where,
            ("length", "width", "agents_per_direction", "spawn_spacing"),
            ("spawn_jitter", "wall_clearance", "wall_thickness"),
        )
        geometry: dict[str, Any] = {
            key: as_number(raw[key], f"{where}.{key}", minimum=0.0, strict_minimum=True)
            for key in ("length", "width", "spawn_spacing")
        }
        geometry["agents_per_direction"] = whole_number(
            raw["agents_per_direction"], f"{where}.agents_per_direction", minimum=1
        )
        geometry["spawn_jitter"] = as_number(raw.get("spawn_jitter", 0.0), f"{where}.spawn_jitter", minimum=0.0)
        geometry["wall_clearance"] = as_number(
            raw.get("wall_clearance", 0.5), f"{where}.wall_clearance", minimum=0.0, strict_minimum=True
        )
        geometry["wall_thickness"] = as_number(
            raw.get("wall_thickness", 0.5), f"{where}.wall_thickness", minimum=0.0, strict_minimum=True
        )

        usable = geometry["width"] - 2.0 * geometry["wall_clearance"]
        if usable < 0.0:
            raise ConfigError(f"{where}: the corridor is narrower than twice wall_clearance; no agent fits")
        columns = int(math.floor(usable / geometry["spawn_spacing"] + 1e-9)) + 1
        rows = math.ceil(geometry["agents_per_direction"] / columns)
        block = (rows - 1) * geometry["spawn_spacing"] + geometry["spawn_jitter"]
        if 2.0 * block >= geometry["length"]:
            raise ConfigError(
                f"{where}: {geometry['agents_per_direction']} agents per direction need a block "
                f"{block:.1f} m long at each end, which does not fit twice into a corridor "
                f"{geometry['length']:.1f} m long. Lengthen or widen the corridor."
            )
        geometry["spawn_columns"], geometry["spawn_rows"] = columns, rows
        return geometry

    def layout(self, geometry: Mapping[str, Any], seed: int) -> CrowdLayout:
        g = geometry
        half_length, half_width = g["length"] / 2.0, g["width"] / 2.0
        spacing, jitter, columns = g["spawn_spacing"], g["spawn_jitter"], g["spawn_columns"]
        rng = random.Random(seed)
        span = (columns - 1) * spacing  # the lattice is centred on the centre line of the corridor

        placements = []
        for sign, group in ((1.0, "eastbound"), (-1.0, "westbound")):
            for index in range(g["agents_per_direction"]):
                row, column = divmod(index, columns)
                # Row 0 is the front of the block: the row nearest the middle of the corridor.
                x = -sign * (half_length - (g["spawn_rows"] - 1 - row) * spacing)
                y = -span / 2.0 + column * spacing
                if jitter > 0.0:
                    x += rng.uniform(-jitter, jitter)
                    y += rng.uniform(-jitter, jitter)
                goal = (sign * half_length, y)
                placements.append(Placement((x, y), goal, Polyline([(x, y), goal]), group))

        # The walls reach past the corridor's ends by the depth of a block, so that an
        # agent pushed back at the start still has a wall beside it.
        reach = half_length + g["spawn_rows"] * spacing + jitter
        t = g["wall_thickness"]
        walls = (
            Rect(-reach, half_width, reach, half_width + t),
            Rect(-reach, -half_width - t, reach, -half_width),
        )
        return CrowdLayout(tuple(placements), walls)
