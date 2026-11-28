"""What a finished run measured, in the terms of the human targets (issue #122, RF-37; ``docs/human-targets.md``).

Everything here is read back from a run folder (``config.json``, ``outcome.json``, ``trajectory.csv``),
as ``negsim.ruleset_eval.measures`` is, so a measure can be recomputed without running again. Each
measure follows the study's own definition where the study gives one.

**Per pair** (two people meeting head-on; the trajectory must be logged on every step):

* ``min_centre_distance_m``: the smallest distance between the two centres while both are walking.
  Rapos2021's minimal predicted distance is, at the crossing, the distance between the walkers'
  centres (``[inferred]``, from Meerhoff2018's method).
* The **point of minimal distance** (PoMD), Huber2014's: the step at which that distance is smallest.
* Each walker's own frame: its path's direction (start to goal) and the left of it. ``lateral`` is
  its position to its own left of the line through its start, so a person who starts off the centre
  line has deviated by nothing at the start.
* ``lateral_deviation_max_m``: the largest distance from its line, until it arrives (Huber2014,
  section 4.4, "maximal lateral deviation from the straight path").
* ``lateral_share``: its deviation over the two walkers' together; ``None`` if neither deviated.
* ``turning_start_m`` (Huber2014's "start of turning"): the movement direction is the angle of the
  step's displacement, the angular speed its change per second. The start of turning is the first
  step **before the PoMD** whose angular speed exceeds the floor, reported as the distance along the
  walking direction from there to the PoMD. Huber's threshold is each walker's own turning when
  walking alone. A simulated walker alone goes dead straight, so its own is about zero.
  **[design]** The threshold is ``TURN_RATE_FLOOR_RAD_S``, which is above the baseline's
  perturbation and below any avoiding turn. ``None`` if it did not turn before the PoMD.
* ``speed_change_mps`` (Huber2014's "speed change"): the walker's highest speed minus its lowest
  local minimum (a minimum with a higher speed on both sides), until it arrives; 0 with no such
  minimum.
* ``side``: the side it kept to at the PoMD, in its own frame (``left``: the other went by on its
  right), as ``negsim.resolution.outcomes`` defines it.
* ``passed_first``: **[design]** in a head-on meeting the two are abreast at the same moment, so
  the one who first gets ``CLEAR_DISTANCE_M`` past the PoMD along its own path passed first; ``together``
  on the same step. Step 1's own ``who_passed_first`` (the first to leave the conflict zone) is used
  for Step 1's sessions.

**Per crowd** (the two-way flow, any logging stride):

* ``lanes``: ``negsim.ruleset_eval.measures.lanes``, unchanged.
* ``speed_by_density``: on each logged step, the people inside a measuring area across the corridor
  (``|x| <= MEASURE_HALF_LENGTH_M``, Zhang2012's ``Delta x = [-1.0, 1.0] m``); the density is their
  number over the area, the speed their mean speed. One sample per logged step with someone inside.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..ruleset_eval.measures import lanes

#: [design] Above the primary baseline's perturbation (1e-4 m/s, a turn of under 1e-3 rad/s at walking
#: speed) and below any avoiding turn of ORCA; reported with every measure.
TURN_RATE_FLOOR_RAD_S = 0.05
#: [design] How far past the point of minimal distance a person must be to have passed.
CLEAR_DISTANCE_M = 1.0
#: Zhang2012's measuring area: 2 m along the corridor, its whole width.
MEASURE_HALF_LENGTH_M = 1.0
TOGETHER = "together"


@dataclass(frozen=True)
class Sample:
    step: int
    t: float
    x: float
    y: float
    vx: float
    vy: float
    speed: float


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_tracks(run_dir: Path) -> dict[int, list[Sample]]:
    """Each agent's logged samples while it is walking (the row written on its arrival has no velocity
    and is left out)."""
    tracks: dict[int, list[Sample]] = {}
    with (Path(run_dir) / "trajectory.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["vx_mps"] == "":
                continue
            tracks.setdefault(int(row["agent_id"]), []).append(Sample(
                int(row["step"]), float(row["time_s"]), float(row["x_m"]), float(row["y_m"]),
                float(row["vx_mps"]), float(row["vy_mps"]), float(row["speed_mps"])))
    return tracks


class Frame:
    """A walker's own frame: along its path (start to goal) and to its left."""

    def __init__(self, agent: Mapping[str, Any]):
        (x0, y0), (x1, y1) = agent["path"][0], agent["path"][-1]
        length = math.hypot(x1 - x0, y1 - y0)
        self.ox, self.oy = agent["start"]["x"], agent["start"]["y"]
        self.ux, self.uy = (x1 - x0) / length, (y1 - y0) / length

    def along(self, x: float, y: float) -> float:
        return (x - self.ox) * self.ux + (y - self.oy) * self.uy

    def lateral(self, x: float, y: float) -> float:
        return self.ux * (y - self.oy) - self.uy * (x - self.ox)  # > 0: to its own left


def turning_start(samples: Sequence[Sample], frame: Frame, pomd_step: int, floor: float = TURN_RATE_FLOOR_RAD_S) -> Optional[float]:
    """Huber2014's start of turning, in metres before the point of minimal distance (module docstring)."""
    at_pomd = next((s for s in samples if s.step == pomd_step), None)
    if at_pomd is None:
        return None
    previous_heading = None
    for before, after in zip(samples, samples[1:]):
        if after.step > pomd_step:
            break
        dx, dy = after.x - before.x, after.y - before.y
        if math.hypot(dx, dy) < 1e-9:
            previous_heading = None
            continue
        heading = math.atan2(dy, dx)
        if previous_heading is not None:
            turn = math.atan2(math.sin(heading - previous_heading), math.cos(heading - previous_heading))
            if abs(turn) / (after.t - before.t) > floor:
                return round(frame.along(at_pomd.x, at_pomd.y) - frame.along(before.x, before.y), 6)
        previous_heading = heading
    return None


def speed_change(samples: Sequence[Sample]) -> float:
    """Huber2014's speed change: the highest speed minus the lowest local minimum (0 with none)."""
    speeds = [s.speed for s in samples]
    minima = []
    for i in range(1, len(speeds) - 1):
        if speeds[i] < speeds[i - 1] and speeds[i] <= speeds[i + 1]:
            if max(speeds[:i]) > speeds[i] and max(speeds[i + 1:]) > speeds[i]:
                minima.append(speeds[i])
    return round(max(speeds) - min(minima), 6) if minima else 0.0


def pair_measures(run_dir: Path, agents: Optional[Sequence[int]] = None, floor: float = TURN_RATE_FLOOR_RAD_S) -> dict[str, Any]:
    """The per-pair measures of one head-on run (module docstring); ``agents`` defaults to the first two."""
    run_dir = Path(run_dir)
    config = _read_json(run_dir / "config.json")
    if config.get("logging", {}).get("trajectory_stride", 1) != 1:
        raise ValueError(f"{run_dir}: the pair measures need the trajectory on every step (trajectory_stride 1)")
    specs = {agent["agent_id"]: agent for agent in config["scenario"]["agents"]}
    a, b = agents if agents is not None else sorted(specs)[:2]
    tracks = read_tracks(run_dir)
    by_step = {agent: {s.step: s for s in tracks.get(agent, [])} for agent in (a, b)}
    both = sorted(set(by_step[a]) & set(by_step[b]))
    if not both:
        return {"agents": [a, b], "min_centre_distance_m": None, "turn_rate_floor_rad_s": floor}
    distance = {step: math.dist((by_step[a][step].x, by_step[a][step].y), (by_step[b][step].x, by_step[b][step].y)) for step in both}
    pomd = min(both, key=lambda step: (distance[step], step))
    frames = {agent: Frame(specs[agent]) for agent in (a, b)}
    per_agent: dict[int, dict[str, Any]] = {}
    for me, other in ((a, b), (b, a)):
        frame, samples = frames[me], tracks[me]
        start = frame.lateral(samples[0].x, samples[0].y)
        mine, theirs = by_step[me][pomd], by_step[other][pomd]
        cross = frame.ux * (theirs.y - mine.y) - frame.uy * (theirs.x - mine.x)  # > 0: the other is on its left
        passed = next((s.step for s in samples if s.step >= pomd and frame.along(s.x, s.y) - frame.along(mine.x, mine.y) >= CLEAR_DISTANCE_M), None)
        per_agent[me] = {
            "lateral_deviation_max_m": round(max(abs(frame.lateral(s.x, s.y) - start) for s in samples), 6),
            "turning_start_m": turning_start(samples, frame, pomd, floor),
            "speed_change_mps": speed_change(samples),
            "side": None if cross == 0.0 else ("left" if cross < 0.0 else "right"),
            "passed_step": passed,
        }
    total = per_agent[a]["lateral_deviation_max_m"] + per_agent[b]["lateral_deviation_max_m"]
    for agent in (a, b):
        per_agent[agent]["lateral_share"] = round(per_agent[agent]["lateral_deviation_max_m"] / total, 6) if total > 1e-6 else None
    pa, pb = per_agent[a]["passed_step"], per_agent[b]["passed_step"]
    if pa is None and pb is None:
        first: Any = None
    elif pa == pb:
        first = TOGETHER
    else:
        first = a if pb is None or (pa is not None and pa < pb) else b
    return {
        "agents": [a, b],
        "min_centre_distance_m": round(distance[pomd], 6),
        "pomd_time_s": round(by_step[a][pomd].t, 6),
        "passed_first": first,
        "per_agent": {str(agent): values for agent, values in per_agent.items()},
        "turn_rate_floor_rad_s": floor,
    }


def speed_by_density(run_dir: Path, half_length_m: float = MEASURE_HALF_LENGTH_M) -> list[tuple[float, float]]:
    """(density in persons per square metre, mean speed in m/s) in the measuring area, one per logged
    step with someone inside it."""
    run_dir = Path(run_dir)
    config = _read_json(run_dir / "config.json")
    width = config["scenario"]["geometry"]["width"]
    area = 2.0 * half_length_m * width
    inside: dict[int, list[float]] = {}
    with (run_dir / "trajectory.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["speed_mps"] != "" and abs(float(row["x_m"])) <= half_length_m:
                inside.setdefault(int(row["step"]), []).append(float(row["speed_mps"]))
    return [(round(len(v) / area, 6), round(sum(v) / len(v), 6)) for _, v in sorted(inside.items())]


def crowd_measures(run_dir: Path) -> dict[str, Any]:
    """The per-crowd measures of one two-way flow run."""
    run_dir = Path(run_dir)
    config = _read_json(run_dir / "config.json")
    return {"lanes": lanes(run_dir, config), "speed_by_density": speed_by_density(run_dir),
            "measure_half_length_m": MEASURE_HALF_LENGTH_M}
