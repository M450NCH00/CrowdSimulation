"""A plain-text print of the grid (issue #139, RF-50): for tests and work logs; no viewer.

The corridor runs left to right (+x); the top line is the lane at +y. Each walker is its label
(``A`` for walker 0, ``B`` for walker 1, ...); ``.`` is an empty cell, ``=`` a wall.

    tick 19  (5.85 s)   A -> +x   B <- -x
    ====================================================
    |..................................................|
    |..................................................|
    |........................AB........................|
    ...
"""

from __future__ import annotations

from typing import Mapping, Sequence

from .world import Action, GridConfig, Run, Walker


def frame(config: GridConfig, positions: Mapping[int, tuple[int, int]], walkers: Sequence[Walker], tick: int,
          actions: Sequence[Action] = ()) -> str:
    labels = {w.id: w.label for w in walkers}
    arrows = "   ".join(f"{w.label} {'->' if w.direction > 0 else '<-'} {'+x' if w.direction > 0 else '-x'}" for w in walkers)
    lines = [f"tick {tick}  ({tick * config.tick_s:.2f} s)   {arrows}", "=" * (config.rows + 2)]
    cells = {cell: wid for wid, cell in positions.items()}
    for lane in reversed(range(config.lanes)):
        row_text = "".join(labels[cells[(row, lane)]] if (row, lane) in cells else "." for row in range(config.rows))
        lines.append(f"|{row_text}|")
    lines.append("=" * (config.rows + 2))
    if actions:
        lines.append("  ".join(
            f"{labels[a.walker]}: {a.intended.value}" + (f" (blocked: {a.blocked})" if a.blocked else "") for a in actions
        ))
    return "\n".join(lines)


def print_run(run: Run, every: int = 1) -> str:
    """Every ``every``-th tick of a run, and its last."""
    out = []
    for i, tick in enumerate(run.ticks):
        if i % every == 0 or i == len(run.ticks) - 1:
            out.append(frame(run.config, tick.positions, run.walkers, tick.tick, tick.actions))
    out.append(f"ended by: {run.ended_by}")
    return "\n\n".join(out) + "\n"
