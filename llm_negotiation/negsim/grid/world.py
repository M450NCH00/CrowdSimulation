"""The grid corridor (issue #139, RF-50): cells, moves, and the tick update with its clash rule.

**The corridor** is ``lanes`` cells across and ``rows`` cells along (``configs/grid/corridor_v1.yaml``,
AS6). A cell is ``(row, lane)``: ``row`` 0 is the end at -x, ``lane`` 0 is the wall at -y. Cell
centres in metres put the corridor's middle at x = 0 and its centre line at y = 0, as in round 1's
continuous corridor, so that ``analysis.lateral`` can read a grid trajectory.

**Moves** are given in the walker's own frame (:class:`Move`): forward; forward and one lane to the
left or right; one lane to the left or right without advancing; wait; one cell back. A walker heading
+x (``direction`` +1) has its own left at +y, one heading -x at -y, as ``analysis.lateral`` counts it.

**The tick** (:func:`step`) is a parallel update, as in Burstedde et al. 2001 (AS7):

1. a walker slower than the reference speed acts only on the ticks at which its walked distance
   reaches the next cell (the rest of the time it holds, ``not_due``); deterministic;
2. a move into a wall, or out past the end behind the walker, does not happen (``wall``);
3. a move into a cell occupied at the start of the tick does not happen (``occupied``). This also
   rules out two people swapping cells: each aims at a cell the other holds;
4. **crossing paths** (an assumption of RF-50's, agreed by the user on 2026-11-25; not in the paper):
   two diagonal moves that cut through each other in one tick (the same midpoint, different targets)
   both do not happen (``crossing``);
5. several aiming at one empty cell: one, drawn from the session's seed, moves; the others stay
   (``contest_lost``). "If more than one particle share the same target cell, one is chosen ...
   This particle moves while its rivals for the same target keep their position"
   (``refs/rf42_burstedde2001_ca_arxiv.txt:168-174``).

A walker that reaches the last row on its way has **arrived** and leaves the grid at the end of that
tick. Standard library only; no model is called anywhere in this package.
"""

from __future__ import annotations

import enum
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from ..configutil import ConfigError, as_number, check_keys, load_yaml, resolve_path

DEFAULT_CONFIG = "configs/grid/corridor_v1.yaml"
#: Float slack when a slow walker's walked distance is compared with a cell.
EPS = 1e-9


class Move(str, enum.Enum):
    """A move in the walker's own frame."""

    FORWARD = "forward"
    FORWARD_LEFT = "forward_left"
    FORWARD_RIGHT = "forward_right"
    LEFT = "left"
    RIGHT = "right"
    WAIT = "wait"
    BACK = "back"


#: Each move as (cells ahead, lanes to the walker's own left).
OWN_DELTA: Mapping[Move, tuple[int, int]] = {
    Move.FORWARD: (1, 0),
    Move.FORWARD_LEFT: (1, 1),
    Move.FORWARD_RIGHT: (1, -1),
    Move.LEFT: (0, 1),
    Move.RIGHT: (0, -1),
    Move.WAIT: (0, 0),
    Move.BACK: (-1, 0),
}

BLOCKED_REASONS = ("not_due", "wall", "occupied", "crossing", "contest_lost")


def grid_delta(move: Move, direction: int) -> tuple[int, int]:
    """``move`` as (rows, lanes) on the grid for a walker heading ``direction`` (+1 or -1)."""
    ahead, left = OWN_DELTA[Move(move)]
    return ahead * direction, left * direction


@dataclass(frozen=True)
class GridConfig:
    cell_m: float = 0.4
    lanes: int = 5
    rows: int = 50
    start_cells_from_middle: int = 20
    reference_speed_mps: float = 1.3
    max_time_s: float = 60.0
    deadlock_window_s: float = 3.0
    body_radius_m: float = 0.25
    source: str = ""

    def __post_init__(self) -> None:
        if self.lanes < 1 or self.rows < 2 or self.rows % 2:
            raise ConfigError(f"grid: need at least 1 lane and an even number of rows, got {self.lanes} x {self.rows}")
        if not 1 <= self.start_cells_from_middle <= self.rows // 2:
            raise ConfigError(f"grid: start_cells_from_middle must be 1 to {self.rows // 2}, got {self.start_cells_from_middle}")

    @property
    def tick_s(self) -> float:
        """One cell at the reference speed (AS6: about 0.31 s)."""
        return self.cell_m / self.reference_speed_mps

    @property
    def max_ticks(self) -> int:
        return math.ceil(self.max_time_s / self.tick_s - EPS)

    @property
    def deadlock_ticks(self) -> int:
        """The deadlock window in ticks, rounded up (3.0 s is 10 ticks)."""
        return math.ceil(self.deadlock_window_s / self.tick_s - EPS)

    @property
    def width_m(self) -> float:
        return self.lanes * self.cell_m

    @property
    def centre_lane(self) -> int:
        return self.lanes // 2

    def x_m(self, row: int) -> float:
        """The centre of ``row`` along the corridor; the middle of the corridor is 0."""
        return (row + 0.5) * self.cell_m - self.rows * self.cell_m / 2

    def y_m(self, lane: float) -> float:
        """The centre of ``lane`` across the corridor; the centre line is 0."""
        return (lane + 0.5) * self.cell_m - self.lanes * self.cell_m / 2

    def start_row(self, direction: int) -> int:
        """The ``start_cells_from_middle``-th cell from the middle, on the side a walker heading
        ``direction`` starts (rows 5 and 44 of 50 for 20 cells)."""
        half = self.rows // 2
        return half - self.start_cells_from_middle if direction > 0 else half - 1 + self.start_cells_from_middle

    def goal_row(self, direction: int) -> int:
        return self.rows - 1 if direction > 0 else 0


def load_config(path: Path | str = DEFAULT_CONFIG) -> GridConfig:
    raw = load_yaml(resolve_path(path))
    where = str(path)
    keys = ("cell_m", "lanes", "rows", "start_cells_from_middle", "reference_speed_mps", "max_time_s", "deadlock_window_s", "body_radius_m")
    check_keys(raw, where, required=("schema_version", "type", *keys), optional=("description",))
    if raw["schema_version"] != 1 or raw["type"] != "grid_corridor":
        raise ConfigError(f"{where}: expected schema_version 1 and type grid_corridor")
    numbers = {key: as_number(raw[key], f"{where}: {key}", minimum=0, strict_minimum=True) for key in keys}
    for key in ("lanes", "rows", "start_cells_from_middle"):
        if numbers[key] != int(numbers[key]):
            raise ConfigError(f"{where}: {key} must be a whole number, got {raw[key]!r}")
        numbers[key] = int(numbers[key])
    return GridConfig(**numbers, source=where)


@dataclass
class Walker:
    """One person on the grid. ``direction`` +1 walks towards +x (row up), -1 towards -x."""

    id: int
    row: int
    lane: int
    direction: int
    speed_mps: float = 1.3
    label: str = ""
    walked_m: float = 0.0
    arrived_tick: Optional[int] = None
    start: tuple[int, int] = field(default=(0, 0))

    def __post_init__(self) -> None:
        if self.direction not in (1, -1):
            raise ConfigError(f"walker {self.id}: direction must be +1 or -1, got {self.direction}")
        if not self.label:
            self.label = chr(ord("A") + self.id) if self.id < 26 else "?"
        self.start = (self.row, self.lane)

    @property
    def cell(self) -> tuple[int, int]:
        return self.row, self.lane

    @property
    def active(self) -> bool:
        return self.arrived_tick is None


@dataclass(frozen=True)
class Action:
    """What one walker did on one tick."""

    walker: int
    intended: Move
    moved: tuple[int, int]          # (rows, lanes) actually moved
    blocked: Optional[str] = None   # one of BLOCKED_REASONS, or None


@dataclass
class GridState:
    config: GridConfig
    walkers: list[Walker]
    seed: int
    tick: int = 0
    contest_rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        ids = [w.id for w in self.walkers]
        if len(set(ids)) != len(ids):
            raise ConfigError(f"walker ids repeat: {ids}")
        for w in self.walkers:
            self._check_inside(w.row, w.lane, f"walker {w.id}")
            if w.speed_mps <= 0 or w.speed_mps > self.config.reference_speed_mps + EPS:
                raise ConfigError(
                    f"walker {w.id}: speed must be above 0 and at most {self.config.reference_speed_mps} m/s "
                    f"(one cell a tick), got {w.speed_mps}"
                )
        cells = [w.cell for w in self.walkers]
        if len(set(cells)) != len(cells):
            raise ConfigError(f"two walkers start in one cell: {cells}")
        # A string seed is hashed the same way on every run and machine.
        self.contest_rng = random.Random(f"{self.seed}:contest")

    def _check_inside(self, row: int, lane: int, where: str) -> None:
        if not (0 <= row < self.config.rows and 0 <= lane < self.config.lanes):
            raise ConfigError(f"{where}: cell {(row, lane)} is outside the {self.config.rows} x {self.config.lanes} grid")

    def walker(self, walker_id: int) -> Walker:
        return next(w for w in self.walkers if w.id == walker_id)

    def active(self) -> list[Walker]:
        return [w for w in self.walkers if w.active]

    def occupied(self) -> dict[tuple[int, int], int]:
        return {w.cell: w.id for w in self.active()}

    def positions(self) -> dict[int, tuple[int, int]]:
        return {w.id: w.cell for w in self.active()}


def _due(state: GridState, walker: Walker) -> bool:
    """Whether a walker acts this tick: its walked distance reaches the next cell."""
    walker.walked_m += walker.speed_mps * state.config.tick_s
    if walker.walked_m + EPS >= state.config.cell_m:
        walker.walked_m -= state.config.cell_m
        return True
    return False


def step(state: GridState, intents: Mapping[int, Move]) -> list[Action]:
    """Carry out one tick for every active walker; ``intents`` holds each one's move (default wait)."""
    config = state.config
    walkers = state.active()
    occupied = state.occupied()
    actions: dict[int, Action] = {}
    movers: dict[int, tuple[tuple[int, int], tuple[int, int]]] = {}  # id -> (from, to)

    for w in walkers:
        move = Move(intents.get(w.id, Move.WAIT))
        if not _due(state, w):
            actions[w.id] = Action(w.id, move, (0, 0), "not_due")
            continue
        drow, dlane = grid_delta(move, w.direction)
        if (drow, dlane) == (0, 0):
            actions[w.id] = Action(w.id, move, (0, 0))
            continue
        target = (w.row + drow, w.lane + dlane)
        if not (0 <= target[0] < config.rows and 0 <= target[1] < config.lanes):
            actions[w.id] = Action(w.id, move, (0, 0), "wall")
        elif target in occupied:
            actions[w.id] = Action(w.id, move, (0, 0), "occupied")
        else:
            movers[w.id] = (w.cell, target)

    # Crossing paths: two diagonal moves through one midpoint, to different cells.
    crossing: set[int] = set()
    ids = sorted(movers)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            (fa, ta), (fb, tb) = movers[a], movers[b]
            diagonal = fa[0] != ta[0] and fa[1] != ta[1] and fb[0] != tb[0] and fb[1] != tb[1]
            same_midpoint = (fa[0] + ta[0], fa[1] + ta[1]) == (fb[0] + tb[0], fb[1] + tb[1])
            if diagonal and same_midpoint and ta != tb:
                crossing.update((a, b))
    for wid in sorted(crossing):
        actions[wid] = Action(wid, Move(intents.get(wid, Move.WAIT)), (0, 0), "crossing")
        del movers[wid]

    # Contests for one empty cell: one winner drawn from the session's seed.
    by_target: dict[tuple[int, int], list[int]] = {}
    for wid, (_, target) in movers.items():
        by_target.setdefault(target, []).append(wid)
    for target in sorted(by_target):
        rivals = sorted(by_target[target])
        winner = rivals[0] if len(rivals) == 1 else state.contest_rng.choice(rivals)
        for wid in rivals:
            w = state.walker(wid)
            move = Move(intents.get(wid, Move.WAIT))
            if wid != winner:
                actions[wid] = Action(wid, move, (0, 0), "contest_lost")
                continue
            actions[wid] = Action(wid, move, (target[0] - w.row, target[1] - w.lane))

    for w in walkers:
        drow, dlane = actions[w.id].moved
        w.row += drow
        w.lane += dlane
    state.tick += 1
    for w in walkers:
        if w.row == config.goal_row(w.direction):
            w.arrived_tick = state.tick
    return [actions[w.id] for w in walkers]


#: A scripted or model-driven policy: the state, the walker, and that walker's own random stream.
Policy = Callable[[GridState, Walker, random.Random], Move]


@dataclass
class Tick:
    """The grid after ``tick`` ticks, and what each walker did on the way there."""

    tick: int
    positions: dict[int, tuple[int, int]]
    actions: list[Action]


@dataclass
class Run:
    config: GridConfig
    seed: int
    walkers: list[Walker]
    ticks: list[Tick]
    ended_by: str           # all_arrived, deadlock or timeout

    @property
    def directions(self) -> dict[int, int]:
        return {w.id: w.direction for w in self.walkers}


def run(state: GridState, policies: Mapping[int, Policy], max_ticks: Optional[int] = None) -> Run:
    """Run the grid until every walker has arrived, a deadlock, or the time limit.

    A deadlock: for ``config.deadlock_ticks`` ticks in a row no active walker advanced towards its
    goal (a sideways step or a wait is no progress)."""
    config = state.config
    limit = config.max_ticks if max_ticks is None else max_ticks
    missing = [w.id for w in state.walkers if w.id not in policies]
    if missing:
        raise ConfigError(f"no policy for walker(s) {missing}")
    streams = {w.id: random.Random(f"{state.seed}:walker:{w.id}") for w in state.walkers}
    ticks = [Tick(state.tick, state.positions(), [])]
    still = 0
    ended_by = "timeout"
    while state.tick < limit:
        if not state.active():
            ended_by = "all_arrived"
            break
        intents = {w.id: Move(policies[w.id](state, w, streams[w.id])) for w in state.active()}
        actions = step(state, intents)
        ticks.append(Tick(state.tick, state.positions(), actions))
        advanced = any(a.moved[0] * state.walker(a.walker).direction > 0 for a in actions)
        still = 0 if advanced else still + 1
        if not state.active():
            ended_by = "all_arrived"
            break
        if still >= config.deadlock_ticks:
            ended_by = "deadlock"
            break
    return Run(config, state.seed, [w for w in state.walkers], ticks, ended_by)


def head_on(config: GridConfig, lanes: Sequence[int], seed: int, speeds: Sequence[float] = (1.3, 1.3)) -> GridState:
    """Round 1's two people on the grid: walker 0 heads +x from the -x side, walker 1 heads -x."""
    if len(lanes) != 2 or len(speeds) != 2:
        raise ConfigError("head_on: give two lanes and two speeds")
    walkers = [
        Walker(0, config.start_row(1), int(lanes[0]), 1, float(speeds[0])),
        Walker(1, config.start_row(-1), int(lanes[1]), -1, float(speeds[1])),
    ]
    return GridState(config, walkers, seed)


def as_dict(config: GridConfig) -> dict[str, Any]:
    return {
        "cell_m": config.cell_m, "lanes": config.lanes, "rows": config.rows,
        "start_cells_from_middle": config.start_cells_from_middle,
        "reference_speed_mps": config.reference_speed_mps, "tick_s": round(config.tick_s, 6),
        "max_ticks": config.max_ticks, "deadlock_ticks": config.deadlock_ticks,
        "body_radius_m": config.body_radius_m, "source": config.source,
    }
