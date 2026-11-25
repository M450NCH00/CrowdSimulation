"""Round 1's head-on cases placed on the grid (issue #139, RF-50, task 3).

Round 1 (RF-10 to RF-40) used two geometries of the continuous corridor (1.75 m wide, 20 m long,
each person starting 8 m from the middle):

- ``head_on_de176842``, ``aligned``: both walking lines on the centre line;
- ``head_on_02dfbadb``, ``apart_20cm``: person 1 (walker 0, heading +x) 0.1 m to +y, person 2
  (walker 1, heading -x) 0.1 m to -y, so each is 0.1 m to its own left and sees the other to its
  own right.

On the grid a walking line is a lane (0.4 m). A lateral offset rounds to the nearest lane centre
(:func:`lane_of`; half a lane rounds towards +y). **What rounding loses:** 0.1 m is a quarter of a
lane, so ``apart_20cm`` lands both people in the centre lane: on the grid it is the aligned case.
The grid's second geometry is therefore **one lane apart** (0.4 m, between round 1's ``apart_20cm``
and the source run's ``apart_40cm``), proposed in RF-42 (section 8). With 5 lanes, one lane apart
cannot be symmetric about the centre line: walker 0 keeps the centre lane and walker 1 is one lane
to -y, which keeps ``apart_20cm``'s sense (each sees the other to its own right). Which person is
off the centre line is a choice of RF-50's (``[design]``); RF-51 may counterbalance it.
"""

from __future__ import annotations

import json
import math
from typing import Any, Mapping, Sequence

from ..configutil import resolve_path
from .world import GridConfig

#: The grid's geometries: (walker 0's lane offset, walker 1's) in lanes from the centre lane.
GEOMETRIES: Mapping[str, tuple[int, int]] = {
    "aligned": (0, 0),
    "one_lane_apart": (0, -1),
}

#: Round 1's case files (configs/resolution/round1_head_on_turn_taking.yaml, design.geometries).
ROUND1_CASES = ("head_on_de176842", "head_on_02dfbadb")


def lanes_for(config: GridConfig, geometry: str) -> tuple[int, int]:
    if geometry not in GEOMETRIES:
        raise ValueError(f"unknown grid geometry {geometry!r}; known: {sorted(GEOMETRIES)}")
    a, b = GEOMETRIES[geometry]
    return config.centre_lane + a, config.centre_lane + b


def lane_of(config: GridConfig, offset_m: float) -> int:
    """The lane whose centre is nearest a lateral offset from the centre line (metres, +y);
    half a lane rounds towards +y. Clamped to the corridor."""
    centre_y = config.y_m(config.centre_lane)
    lane = config.centre_lane + math.floor((offset_m - centre_y) / config.cell_m + 0.5)
    return max(0, min(config.lanes - 1, lane))


def place_case(config: GridConfig, case: Mapping[str, Any]) -> dict[str, Any]:
    """Where a continuous head-on case's two people start on the grid, and what rounding loses."""
    geometry = case["scenario"]["geometry"]
    offsets = [float(v) for v in geometry["lateral_offsets"]]
    lanes = [lane_of(config, v) for v in offsets]
    on_grid = [config.y_m(lane) for lane in lanes]
    return {
        "case_id": case["case_id"],
        "layout": case["scenario"].get("variant", {}).get("layout"),
        "continuous": {
            "width_m": geometry["width"], "length_m": geometry["length"], "start_distance_m": geometry["start_distance"],
            "lateral_offsets_m": offsets, "lines_apart_m": round(abs(offsets[0] - offsets[1]), 3),
        },
        "grid": {
            "width_m": round(config.width_m, 3), "length_m": round(config.rows * config.cell_m, 3),
            "start_x_m": [round(config.x_m(config.start_row(1)), 3), round(config.x_m(config.start_row(-1)), 3)],
            "lanes": lanes, "lateral_offsets_m": [round(v, 3) for v in on_grid],
            "lanes_apart": abs(lanes[0] - lanes[1]),
        },
        "rounding_lost_m": [round(abs(o - g), 3) for o, g in zip(offsets, on_grid)],
    }


def load_case(case_id: str, version: int = 2) -> dict[str, Any]:
    return json.loads(resolve_path(f"cases/{case_id}.v{version}.json").read_text(encoding="utf-8"))


def round1_placements(config: GridConfig, case_ids: Sequence[str] = ROUND1_CASES) -> list[dict[str, Any]]:
    return [place_case(config, load_case(case_id)) for case_id in case_ids]
