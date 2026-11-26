# Work Log — Issue #140: RF-51: what an agent is told and can choose on the grid, in its own frame and in an absolute frame: resolve_grid_v1 (mock only)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/140
**Branch:** feat/140-rf51-grid-agents (cut from `origin/feat/129-rf40-turn-taking-talk` after PRs #148 and #149 merged into it)
**Started:** 2026-11-26 06:58 UTC (from `date -u`)

## Understanding the issue
RF-50 built the grid corridor (`negsim/grid/`) and tested it with scripted walkers. RF-51 puts LLM
agents on it:
- **What they are told:** where they and the other person are, in cells and lanes.
- **What they choose:** one move from a menu described in words.
- **Two frames:** the agent's own left and right (`resolve_grid_v1`), and the absolute frame
  (`resolve_grid_abs_v1`).

Mock only; RF-52 runs it.

Fixed before this issue:
- **AS1 (the user, 2026-11-25):** the grid is an add-on. No existing file of the environment is
  edited; the grid has its own files and entry point, and the user is asked before any existing file
  changes. Before the PR, `git diff --stat` against the base lists only new files.
- **AS2:** RF-52 runs silent only.
- **The user's decisions of 2026-11-26** (`docs/action-space.md` section 8.2; the comment on #140):
  - **the grid's menu is AS3's menu done in cells**, with the corridor menu's words;
  - **who starts off the centre lane in `one_lane_apart` is counterbalanced**;
  - **the absolute frame uses neutral landmark names**, as RF-48 built them;
  - **between decisions, a lane change happens once and then the walker goes forward**; decision
    points are event-driven as in D5, up to 6.
- **Sessions:** RF-40's silent cells and people, on RF-50's grid geometries.

## Plan
Everything is a new file under `negsim/grid/`, `configs/grid/` or `tests/`. Existing code is reused
only by importing it:
- RF-40's design and people (`experiment.plan`, `session_factors`, `session_pairwise`, `first_asked`);
- RF-47's and RF-48's menu tables and reply parser (`parse_reply`);
- the retry (`request_with_retry`), the debrief (`resolve_debrief_v3`, `debrief_messages`) and the
  mock policies of RF-47 and RF-48;
- the view cone (`perceive.in_cone`).

1. `negsim/grid/templates/` with its own `MANIFEST.json`, so no existing manifest changes, and
   `negsim/grid/prompt.py` to load and render them: `resolve_grid_v1` and `resolve_grid_abs_v1`
   (frozen, silent).
2. `negsim/grid/menu.py`: an option of RF-47's or RF-48's table becomes a grid plan in cells:
   - lanes = metres / cell, rounded;
   - wait ticks = seconds / tick, rounded;
   - back cells = metres / cell, rounded, at least 1;
   - slow = the walker's speed times the factor.
3. `negsim/grid/agents.py`: a grid session. It runs the grid tick by tick (RF-50's `step`), with:
   - D4 and D5 on the grid;
   - a view per decision point;
   - the plan carried out between decisions;
   - a debrief at the end;
   - RF-50's measures.
4. `negsim/grid/experiment.py`: the configs `configs/grid/round1_grid.yaml` and
   `round1_grid_abs.yaml`, the sessions, records, outcomes and a cost estimate, run with
   `python -m negsim.grid.experiment`.
5. Tests: the view's text for a known grid state in both frames, the menu in cells, the session,
   and AS1 (no existing file changed).
6. Mock rehearsal in both frames, cost estimate, docs, PR.

## Progress log

## Open questions / risks

## Summary (fill in at the end)
