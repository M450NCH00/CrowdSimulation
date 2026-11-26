"""The grid corridor (issue #139, RF-50): an add-on world of cells and discrete moves.

AS1 (the user, 2026-11-25): the grid does not modify the current environment's code. It lives only
in this package, ``configs/grid/`` and its own tests, reuses existing code only by importing it, and
has its own entry point:

    python -m negsim.grid scripts
    python -m negsim.grid run --script keep_right --geometry aligned --seed 1 --print
    python -m negsim.grid cases

The design is ``docs/action-space.md``, section 8. What an LLM agent is told and can choose on the
grid is RF-51 (#140); no model is called in this package.
"""

from .world import GridConfig, GridState, Move, Run, Walker, head_on, load_config, run, step  # noqa: F401
