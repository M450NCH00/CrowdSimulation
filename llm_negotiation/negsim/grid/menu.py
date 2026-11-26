"""AS3's menu done in cells (issue #140, RF-51; ``docs/action-space.md``, section 8.2).

The user's decision of 2026-11-26: the grid's menu is AS3's menu done in cells, with the corridor
menu's words, so that the grid and the corridor's menu arms differ only by world. The grid therefore
reads RF-47's table (``configs/resolution/menu_table_v1.yaml``) or RF-48's
(``menu_table_abs_v1.yaml``) as they are, and turns each option's amounts into cells and ticks here:

- **carry on**: forward, at the usual speed (no moves first);
- **slow down a little / a lot**: forward at ``speed_factor`` x the usual speed until the other has
  passed. A slower walker moves on fewer ticks (RF-50's ``_due``): 0.81 moves on about 81% of
  ticks, 0.5 on half;
- **stop and wait**: wait for ``seconds`` / tick, rounded (1.0 s / 0.3077 s = 3.25, so 3 ticks),
  then walk on (D5 asks again if the meeting is still predicted);
- **step a little / well** to a side or towards a wall: ``metres`` / cell, rounded, lanes aside,
  each as a move forward and one lane over (moving while walking), then forward. 0.47 m is 1.2
  cells, so one lane; 0.93 m is 2.3 cells, so two lanes. **As far as the wall allows** (AS3): with
  fewer lanes free on that side, as many as there are (``capped_by_wall:<side>``); with none, no
  move (``no_room:<side>``), as RF-47 flags it;
- **step back**: ``metres`` / cell, rounded, at least one cell back (0.5 m is 1.25 cells, so one),
  then walk on.

Every rounding is ``[derived]`` from the table's tagged numbers and RF-50's cell (0.4 m) and tick
(about 0.31 s). A move towards a wall becomes the walker's own side from its heading: wall a is at
+y, which is the own left of a walker heading +x.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from ..resolution.menu import Option
from .world import GridConfig, Move, Walker

#: Wall a (+y) and wall b (-y), as ``negsim.resolution.view.WALLS``.
WALL_A, WALL_B = "a", "b"


def left_wall_of(direction: int) -> str:
    """The wall on the own left of a walker heading ``direction`` (+1: +x, whose left is +y, wall a)."""
    return WALL_A if direction > 0 else WALL_B


@dataclass(frozen=True)
class GridPlan:
    """What a chosen option becomes on the grid: ``moves`` first (each on the walker's next due
    tick; a wait on every tick), then forward; at ``speed_factor`` x the usual speed until the
    other has passed."""

    option: str
    moves: tuple[Move, ...] = ()
    speed_factor: float = 1.0
    flags: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "option": self.option, "moves": [m.value for m in self.moves],
            "speed_factor": self.speed_factor, "flags": list(self.flags),
        }


#: An unreadable reply after the retry, or no decision yet: walk on as before, at the usual speed.
CARRY_ON = GridPlan("carry on")


def lanes_free(config: GridConfig, walker: Walker, side: str) -> int:
    """How many lanes lie between the walker and the wall on its own ``side``."""
    to_plus_y = config.lanes - 1 - walker.lane
    to_minus_y = walker.lane
    left = to_plus_y if walker.direction > 0 else to_minus_y
    right = to_minus_y if walker.direction > 0 else to_plus_y
    return left if side == "left" else right


def cells(metres: float, config: GridConfig, minimum: int = 0) -> int:
    return max(minimum, int(round(metres / config.cell_m)))


def ticks(seconds: float, config: GridConfig) -> int:
    return max(1, int(round(seconds / config.tick_s)))


def plan_for(option: Option, walker: Walker, config: GridConfig) -> GridPlan:
    """The grid plan of a menu option (RF-47's or RF-48's table) for ``walker`` now."""
    if option.kind == "carry_on":
        return GridPlan(option.name)
    if option.kind == "slow":
        return GridPlan(option.name, speed_factor=float(option.speed_factor))
    if option.kind == "wait":
        return GridPlan(option.name, (Move.WAIT,) * ticks(float(option.seconds), config))
    if option.kind == "back_up":
        return GridPlan(option.name, (Move.BACK,) * cells(float(option.metres), config, minimum=1))
    if option.kind != "sidestep":
        raise ValueError(f"unknown option kind {option.kind!r}")
    side = option.to
    if option.towards is not None:
        side = "left" if option.towards == left_wall_of(walker.direction) else "right"
    wanted = cells(float(option.metres), config, minimum=1)
    free = lanes_free(config, walker, side)
    move = Move.FORWARD_LEFT if side == "left" else Move.FORWARD_RIGHT
    if free == 0:
        return GridPlan(option.name, flags=(f"no_room:{side}",))
    if free < wanted:
        return GridPlan(option.name, (move,) * free, flags=(f"capped_by_wall:{side}",))
    return GridPlan(option.name, (move,) * wanted)


def side_of(plan: Optional[GridPlan]) -> str:
    """The side a plan moves to, in the walker's own frame: left, right or none."""
    if plan is None:
        return "none"
    if Move.FORWARD_LEFT in plan.moves:
        return "left"
    if Move.FORWARD_RIGHT in plan.moves:
        return "right"
    return "none"
