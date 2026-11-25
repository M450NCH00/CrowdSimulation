"""Scripted walkers for the grid (issue #139, RF-50, task 2): no LLM, no model call.

Each is a :data:`~negsim.grid.world.Policy`. They see the whole grid; what an LLM agent is told on
the grid is RF-51 (#140). "Ahead" and "to my left" are in the walker's own frame. A script reacts
when the other is ahead within ``react_cells`` (default 6 cells, 2.4 m: a choice for the scripts,
``[design]``, not a measured distance).

- :func:`keep_side`: move to the lane ``lanes_from_wall`` in from the wall on one's own right (or
  left), then walk on. Both keeping right end two lanes apart (0.8 m) from either of round 1's
  geometries.
- :func:`hold_lane`: always forward.
- :func:`step_aside`: move ``lanes`` lanes away from the other (to ``default_side`` if in the
  same lane), then walk on.
- :func:`dancer`: while the other is ahead and less than two lanes off, step sideways in place,
  first to ``first_side``, then back, and so on. Two dancers in step move towards the same wall on
  every tick: the pavement dance.
- :func:`random_walker`: a move drawn from the walker's own seeded stream.
"""

from __future__ import annotations

import random
from typing import Callable, Optional

from .world import GridState, Move, Policy, Walker

REACT_CELLS = 6


def other_ahead(state: GridState, me: Walker) -> Optional[tuple[int, int]]:
    """The nearest other active walker ahead: (cells ahead, lanes to my own left)."""
    best = None
    for other in state.active():
        if other.id == me.id:
            continue
        ahead = (other.row - me.row) * me.direction
        if ahead <= 0:
            continue
        left = (other.lane - me.lane) * me.direction
        if best is None or ahead < best[0]:
            best = (ahead, left)
    return best


def _own_lane_offset(state: GridState, me: Walker, target_lane: int) -> int:
    """Lanes from my lane to ``target_lane``, to my own left positive."""
    return (target_lane - me.lane) * me.direction


def _wall_lane(state: GridState, me: Walker, side: str, lanes_from_wall: int) -> int:
    """The lane ``lanes_from_wall`` in from the wall on my own ``side``."""
    lanes = state.config.lanes
    right_wall_lane = 0 if me.direction > 0 else lanes - 1
    left_wall_lane = lanes - 1 - right_wall_lane
    if side == "right":
        return right_wall_lane + lanes_from_wall * (1 if right_wall_lane == 0 else -1)
    return left_wall_lane + lanes_from_wall * (1 if left_wall_lane == 0 else -1)


def _towards(offset: int) -> Move:
    return Move.FORWARD if offset == 0 else (Move.FORWARD_LEFT if offset > 0 else Move.FORWARD_RIGHT)


def keep_side(side: str = "right", lanes_from_wall: int = 1, react_cells: int = REACT_CELLS) -> Policy:
    if side not in ("left", "right"):
        raise ValueError(f"keep_side: side must be left or right, got {side!r}")

    def policy(state: GridState, me: Walker, rng: random.Random) -> Move:
        seen = other_ahead(state, me)
        if seen is None or seen[0] > react_cells:
            return Move.FORWARD
        return _towards(_own_lane_offset(state, me, _wall_lane(state, me, side, lanes_from_wall)))

    policy.__name__ = f"keep_{side}"
    return policy


def hold_lane() -> Policy:
    def policy(state: GridState, me: Walker, rng: random.Random) -> Move:
        return Move.FORWARD

    return policy


def step_aside(lanes: int = 2, default_side: str = "right", react_cells: int = REACT_CELLS) -> Policy:
    """Move ``lanes`` lanes away from the other, from the lane it was in when it reacted."""
    target: dict[int, int] = {}

    def policy(state: GridState, me: Walker, rng: random.Random) -> Move:
        seen = other_ahead(state, me)
        if me.id not in target:
            if seen is None or seen[0] > react_cells:
                return Move.FORWARD
            away_left = seen[1] < 0 or (seen[1] == 0 and default_side == "left")
            wanted = me.lane + (lanes if away_left else -lanes) * me.direction
            target[me.id] = max(0, min(state.config.lanes - 1, wanted))
        if seen is None:
            return Move.FORWARD
        return _towards(_own_lane_offset(state, me, target[me.id]))

    return policy


def dancer(first_side: str = "left", react_cells: int = REACT_CELLS) -> Policy:
    steps: dict[int, int] = {}

    def policy(state: GridState, me: Walker, rng: random.Random) -> Move:
        seen = other_ahead(state, me)
        if seen is None or seen[0] > react_cells or abs(seen[1]) >= 2:
            return Move.FORWARD
        n = steps.get(me.id, 0)
        steps[me.id] = n + 1
        left = (first_side == "left") == (n % 2 == 0)
        return Move.LEFT if left else Move.RIGHT

    return policy


#: The random walker's weights: mostly forward, so that a run usually gets somewhere.
RANDOM_WEIGHTS = {
    Move.FORWARD: 4, Move.FORWARD_LEFT: 1, Move.FORWARD_RIGHT: 1, Move.LEFT: 1, Move.RIGHT: 1, Move.WAIT: 1, Move.BACK: 1,
}


def random_walker() -> Policy:
    moves, weights = list(RANDOM_WEIGHTS), list(RANDOM_WEIGHTS.values())

    def policy(state: GridState, me: Walker, rng: random.Random) -> Move:
        return rng.choices(moves, weights)[0]

    return policy


#: The scripted pairs of task 2, as (walker 0's policy, walker 1's policy) factories.
SCRIPTS: dict[str, Callable[[], tuple[Policy, Policy]]] = {
    "keep_right": lambda: (keep_side("right"), keep_side("right")),
    "keep_left": lambda: (keep_side("left"), keep_side("left")),
    "hold_and_step_aside": lambda: (hold_lane(), step_aside(lanes=2)),
    "hold_and_step_aside_1_lane": lambda: (hold_lane(), step_aside(lanes=1)),
    "same_wall_dance": lambda: (dancer("left"), dancer("right")),
    "both_hold": lambda: (hold_lane(), hold_lane()),
    "random": lambda: (random_walker(), random_walker()),
}
