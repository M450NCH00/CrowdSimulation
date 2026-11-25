# Work Log — Issue #139: RF-50: a grid corridor: cells, discrete moves and measures, tested with scripted walkers (no model call)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/139
**Branch:** feat/139-rf50-grid-corridor (cut from `origin/feat/129-rf40-turn-taking-talk`, as RF-43 to RF-45 were)
**Started:** 2026-11-25 09:19 UTC (from `date -u`)

## Understanding the issue
The supervisor's point 1 (November 2026): try a grid, so that an agent chooses among a few moves
instead of angles. RF-50 builds only the world: a corridor of cells, the moves, how clashes are
settled, the measures, and a text print, tested with scripted walkers. No LLM, no model call, no
template (what the LLM is told is RF-51, #140; the paid run is RF-52, #141).

Fixed before this issue (RF-42, `llm_negotiation/docs/action-space.md`, section 8):
- **AS1:** the grid is an add-on. Only new files; reuse by import; ask the user before editing any
  existing file; before the PR, `git diff --stat` lists only new files (plus approved changes).
- **AS6:** cells of 0.4 m, 5 lanes (2.0 m), 50 cells long, each person starting 20 cells from the
  middle, a tick of about 0.31 s (one cell at 1.3 m/s).
- **AS7:** Burstedde et al.'s clash rule: a move into an occupied cell does not happen; several
  aiming at one empty cell, one drawn from the session's seed moves, the rest stay; no swaps.

Left to this issue (section 8, *proposed*): the moves, slower walkers, the geometries, the grid's
measures, and N ticks for a deadlock.

**Why now:** on 2026-11-25 the user dropped RF-41 (#130, closed as not planned) and moved the grid
ahead of RF-46 and the menu: "I think that the issue where we try to use a discrete environment,
like a grid environment instead, I think this will provide more insights". Recorded in #55.
AS8 is withdrawn and AS9's order amended; this branch records both in `docs/action-space.md`.

## Plan
1. `negsim/grid/` (new package): the corridor and its parameters, moves in the walker's own frame,
   the tick update with AS7's clash rule, slower walkers, the measures, a text print, round 1's
   cases placed on the grid, and an entry point `python -m negsim.grid`.
2. Parameters in a new tagged config, `configs/grid/corridor_v1.yaml` (the repo's `[cited]`,
   `[derived]`, `[design]`, `[placeholder]` tags).
3. Scripted walkers (no LLM): both keep right, both keep left, one holds and one steps aside, both
   towards the same wall (a dance), random moves. Their expected outcomes as tests, plus tests of
   each clash rule and of rebuilding a run from its seed.
4. Round 1's head-on cases on the grid, with what rounding loses.
5. The grid section of `docs/action-space.md` (section 8), and AS8/AS9's amendment (section 10).
6. Tests: the new ones, and the existing suite unchanged. `git diff --stat` against the base.

## Settings agreed with the user before building (2026-11-25, in conversation)
The user answered "Yes start" to these, proposed by the assistant:
- deadlock after N ticks with no progress: proposed 16 ticks (about 5 s), a placeholder
  (**changed while building; see the progress log, 09:40**);
- **crossing paths** (an assumption of the assistant's, not an RF-42 decision): two people swapping
  cells, or cutting through each other diagonally in one tick, are blocked;
- slower walkers advance one cell each time their walked distance reaches the next cell;
- if an existing file has to change, stop and ask.

## Progress log

### 2026-11-25 09:19 UTC — branch and work log
- What I did: closed #130 as not planned with a note (the user's choice over deleting it), struck
  RF-41 through in #55 and added the amendment to the order of work; cut this branch.
- Next step: build `negsim/grid/`.

## Open questions / risks

## Summary (fill in at the end)
