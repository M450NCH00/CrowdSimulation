"""What happened between two people on the grid (issue #139, RF-50; ``docs/action-space.md``,
section 8). Read from a :class:`~negsim.grid.world.Run`; two people walking in opposite directions.

- **passed**: the first tick at which each is beyond the other along its own way (no swaps, so they
  cannot pass in one lane).
- **lanes apart when passing**: the sideways gap at the moment they were level. If they were level
  (in one row) on a tick before passing, the fewest lanes between them on those ticks. If they went
  from one side of each other to the other within a tick, each is taken to move in a straight line
  through the tick, so they were level halfway: the mean of the signed gaps before and after, which
  can be half a lane (a walker sliding past diagonally). Times ``cell_m``, the passing distance
  between centres (H1, in steps of 0.2 m). *Changed while building (``WORK_LOG-139.md``, 09:28):*
  a first version took the fewest lanes over every tick they were within a row, which counted an
  earlier face-to-face moment as the passing distance.
- **blocked face to face** (the grid's collision): before passing, in one lane, in adjacent rows,
  facing. Their centres are one cell (0.4 m) apart, closer than two bodies (0.5 m), and neither can
  go on.
- **squeezed past** (the grid's near miss): passed, but fewer lanes apart than two bodies need
  (``lanes * cell_m < 2 * body_radius_m``; with 0.4 m cells, adjacent lanes).
- **the pavement dance**: before passing, on one tick both changed lane towards the same wall
  (``dance_ticks``); or they ended up in one lane facing each other after either had changed lane
  (``dance_into_same_lane``). ``first_changes_towards_same_wall`` compares each one's first lane
  change, whenever it came, as ``analysis.lateral``'s ``towards_same_wall`` does when they are level.
- **deadlock**: the run ended because no one advanced for the deadlock window.
- **resolved**: passed, never blocked face to face, not squeezed, no deadlock, within the time
  limit, as round 1's continuous corridor counts it (``negsim/resolution/scenarios/passing.py``).
"""

from __future__ import annotations

import csv
import io
from typing import Any, Optional

from .world import Run


def _beyond(rows: dict[int, int], directions: dict[int, int], a: int, b: int) -> bool:
    return (rows[a] - rows[b]) * directions[a] > 0


def pair_outcome(run: Run, a: int = 0, b: int = 1) -> dict[str, Any]:
    directions = run.directions
    if directions[a] == directions[b]:
        raise ValueError("pair_outcome: the two must walk in opposite directions")
    config = run.config
    passed_tick: Optional[int] = None
    lanes_when_passing: Optional[float] = None
    level_gaps: list[int] = []
    previous_signed_gap: Optional[int] = None
    face_to_face_ticks = 0
    dance_ticks = 0
    dance_into_same_lane = False
    changed_lane = False
    first_change: dict[int, int] = {}
    counts = {wid: {"lane_changes": 0, "waits": 0, "backs": 0, "blocked": {}} for wid in (a, b)}

    for tick in run.ticks:
        both = a in tick.positions and b in tick.positions
        lane_moves = {}
        for action in tick.actions:
            if action.walker not in counts:
                continue
            c = counts[action.walker]
            if action.blocked:
                c["blocked"][action.blocked] = c["blocked"].get(action.blocked, 0) + 1
            if action.moved[1]:
                c["lane_changes"] += 1
                lane_moves[action.walker] = action.moved[1]
            if action.intended.value == "wait":
                c["waits"] += 1
            if action.intended.value == "back" and action.moved[0]:
                c["backs"] += 1
        if passed_tick is not None or not both:
            continue
        # Lane changes on the way to this tick, before passing.
        for wid, dlane in lane_moves.items():
            first_change.setdefault(wid, 1 if dlane > 0 else -1)
            changed_lane = True
        if len(lane_moves) == 2 and (lane_moves[a] > 0) == (lane_moves[b] > 0):
            dance_ticks += 1
        (ra, la), (rb, lb) = tick.positions[a], tick.positions[b]
        rows = {a: ra, b: rb}
        if ra == rb:
            level_gaps.append(abs(la - lb))
        facing = la == lb and ra + directions[a] == rb and rb + directions[b] == ra
        if facing:
            face_to_face_ticks += 1
            if changed_lane:
                dance_into_same_lane = True
        if _beyond(rows, directions, a, b):
            passed_tick = tick.tick
            candidates = [float(g) for g in level_gaps]
            if not level_gaps and previous_signed_gap is not None:
                candidates.append(abs(previous_signed_gap + (la - lb)) / 2)
            lanes_when_passing = min(candidates) if candidates else float(abs(la - lb))
        previous_signed_gap = la - lb

    passed = passed_tick is not None
    squeezed = bool(passed and lanes_when_passing is not None and lanes_when_passing * config.cell_m < 2 * config.body_radius_m)
    deadlock = run.ended_by == "deadlock"
    blocked_face_to_face = face_to_face_ticks > 0
    first_same_wall = len(first_change) == 2 and first_change[a] == first_change[b]
    return {
        "ended_by": run.ended_by,
        "ticks": run.ticks[-1].tick,
        "passed": passed,
        "passed_tick": passed_tick,
        "time_to_pass_s": None if passed_tick is None else round(passed_tick * config.tick_s, 3),
        "lanes_apart_when_passing": lanes_when_passing if passed else None,
        "passing_distance_m": None if not passed else round(lanes_when_passing * config.cell_m, 3),
        "blocked_face_to_face": blocked_face_to_face,
        "face_to_face_ticks": face_to_face_ticks,
        "squeezed_past": squeezed,
        "dance": dance_ticks > 0 or dance_into_same_lane,
        "dance_ticks": dance_ticks,
        "dance_into_same_lane": dance_into_same_lane,
        "first_changes_towards_same_wall": first_same_wall,
        "deadlock": deadlock,
        "resolved": passed and not blocked_face_to_face and not squeezed and not deadlock,
        "walkers": {str(wid): counts[wid] for wid in (a, b)},
    }


def gate_columns(outcome: dict[str, Any]) -> dict[str, str]:
    """The columns ``analysis.gate`` and ``analysis.lateral`` read from an outcome row, as far as the
    grid can give them. The grid carries out moves with no avoidance steering, so its result stands
    for ``plan_only``. It has no ORCA, so ``*_plan_orca`` and ``*_plain_orca`` are not given
    (``docs/action-space.md``, section 8): ``analysis.gate`` as it stands needs them."""
    return {
        "outcome": "completed",
        "resolved_plan_only": str(bool(outcome["resolved"])),
        "collision_plan_only": str(bool(outcome["blocked_face_to_face"])),
    }


TRAJECTORY_COLUMNS = ("step", "agent_id", "x_m", "y_m", "row", "lane")


def trajectory_csv(run: Run) -> str:
    """One row per walker per tick, with the columns ``analysis.lateral`` reads (``step``,
    ``agent_id``, ``x_m``, ``y_m``: cell centres in metres) and the cell."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(TRAJECTORY_COLUMNS)
    for tick in run.ticks:
        for wid, (row, lane) in sorted(tick.positions.items()):
            writer.writerow([tick.tick, wid, f"{run.config.x_m(row):.3f}", f"{run.config.y_m(lane):.3f}", row, lane])
    return out.getvalue()
