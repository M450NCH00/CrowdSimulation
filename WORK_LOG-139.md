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
  (**changed while building; see the progress log, 09:26**);
- **crossing paths** (an assumption of the assistant's, not an RF-42 decision): two people swapping
  cells, or cutting through each other diagonally in one tick, are blocked;
- slower walkers advance one cell each time their walked distance reaches the next cell;
- if an existing file has to change, stop and ask.

## Progress log

### 2026-11-25 09:19 UTC — branch and work log
- What I did: closed #130 as not planned with a note (the user's choice over deleting it), struck
  RF-41 through in #55 and added the amendment to the order of work; cut this branch.
- Next step: build `negsim/grid/`.

### 2026-11-25 09:26 UTC — the package, and the deadlock window
- What I did: wrote `configs/grid/corridor_v1.yaml` (tagged values) and `negsim/grid/`: `world.py`
  (config, moves, the tick, `run`), `measures.py`, `render.py`, `walkers.py`, `cases.py`,
  `__main__.py`.
- **Decision changed from what the user agreed:** the deadlock window is **3.0 s (10 ticks)**, not the
  16 ticks (about 5 s) I proposed. Reason: 3.0 s is issue #24's window and round 1's corridor's
  (`configs/scenarios/wide_corridor_head_on.yaml`, `deadlock.window_s`), which I had not checked
  when I proposed 16; with the same window the two worlds' deadlock rates compare. It is still a
  placeholder (section 11) and one number in the config. Flagged to the user at the end. (Entry times corrected at 09:33 from the files' modification times: I first wrote estimates, 09:40, 10:05 and 10:20.)
- One difference stays: round 1 counts a deadlock when nobody *moved*; the grid when nobody
  *advanced* (a sideways step is no progress), so two people dancing in place end as a deadlock.
- Starts: with 50 rows there is no middle cell, so "20 cells from the middle" is read as *in the 20th
  cell from the middle*: rows 5 and 44, centres 7.8 m from the middle (round 1: 8 m).
- Parallel update read literally from Burstedde et al.: occupancy at the start of the tick, so a
  cell vacated in the same tick is still occupied.

### 2026-11-25 09:28 UTC — first run of the scripts; the passing distance redefined
- What I did: `python -m negsim.grid scripts --seeds 20`.
- Found: random walkers showed a passing distance of 0.0 m in 4 runs. The first definition took the
  fewest lanes over every tick the two were within a row, so an earlier face-to-face moment counted
  as the passing distance.
- Changed to: the sideways gap at the moment they were level: on a tick in one row if there was
  one, otherwise halfway through the tick in which they went by (each moving in a straight line),
  the mean of the signed gaps before and after. It can be half a lane (0.6 m), so H1 applies in
  steps of 0.2 m. Sliding past diagonally from face to face is then one lane (0.4 m): squeezed.
- Checked that `analysis.lateral.when_level` reads a grid `trajectory.csv` unchanged (with
  `analysis/requirements.txt`): 0.8 m apart, the yielder 0.8 m to its own right.

### 2026-11-25 09:33 UTC — tests; the docs section
- `tests/test_grid.py`: 38 tests (sizes, own frame, every clash rule, slow walkers, arrival, the
  scripted walkers' expected outcomes over 5 seeds × 2 geometries, invariants and rebuild over 40
  random seeds, three hand-built passing-distance cases, round 1's cases, the print, the entry point,
  and that no module outside `negsim/grid/` imports it). All pass (1.1 s).
- `docs/action-space.md`: section 8.1 "As built in RF-50" (moves, tick, geometries and what
  rounding loses, measures, the scripts' results, what `analysis.gate`/`lateral` can read), 8.2 the
  decision points left to RF-51, the amendment to AS8/AS9 in section 10, and section 11's deadlock
  placeholder. This is the one existing file edited, as task 4 asks.

### 2026-11-25 09:53 UTC — the full suite: three failures, none from the grid
- What I ran: the whole negsim suite (`uv run ... python -m pytest`, from 09:34 UTC):
  **2359 passed, 12 skipped, 3 failed** in 15 min 26 s. Separately, `tests/test_grid.py` with
  `tests/test_repo_hygiene.py`: 45 passed.
- The three failures, and why they are not this branch's:
  - `test_personas_and_prompts.py::test_every_template_file_matches_its_pinned_hash` and
    `::test_prompts_never_contain_a_personal_name_field`: `resolve_v9`'s entry in
    `negsim/negotiation/templates/MANIFEST.json` has no `"kind": "resolution"` (`resolve_v8`'s has),
    so the tests load it as a negotiation template. Written that way in RF-40's commit `85a577386`
    (2026-11-01); this branch changes nothing under `negsim/negotiation/` (`git diff --stat` against
    the base is empty there). Not fixed here: it is an existing file outside the grid (AS1), and
    RF-40's branch, which has no PR yet, is where it belongs. For the user.
  - `test_encounter_protocol.py::test_stop_at_cap_...`: the known failure at DeepSeek's peak hours
    (01-04 and 06-10 UTC on weekdays), a `cost.json` gap from #64's code (`WORK_LOG-66.md`). It ran at
    about 09:35 UTC.
- A check of the two template tests on a clean checkout of the base, in a scratch worktree, failed
  to check out (Windows path length: "Filename too long" under `runs/rf28_...`). The half-made
  worktree was removed and pruned. The cause above is read from the manifest and its history instead.
- `git diff --stat origin/feat/129-rf40-turn-taking-talk`: only new files, plus
  `docs/action-space.md` (task 4) and this log.

## Open questions / risks
1. **Deadlock window** 3.0 s (10 ticks) instead of the agreed 16 ticks: see 09:26. For the user.
2. **Crossing paths blocked** is RF-50's assumption, not Burstedde et al.'s; agreed by the user
   before building. A blocked X leaves both in place, and two scripts that repeat it would deadlock.
3. **Which person is off the centre line** in `one_lane_apart` (walker 0 keeps the centre lane):
   a `[design]` choice; RF-51 may counterbalance it.
4. **`analysis.gate` needs `*_plan_orca` and `*_plain_orca`**, which the grid cannot give (no
   ORCA). RF-52 decides: scripted walkers as the grid's baseline, or a grid-only gate.
5. **The corridor is 2.0 m, round 1's 1.75 m** (AS6), and starts 15.6 m apart against 16 m: grid
   rates compare with round 1's by rate only (section 3).
6. **README status lines** (root `README.md`, `llm_negotiation/README.md`) are not updated: under
   the user's AS1 rule ("ask the user before changing any existing file for it"), asked at the end.
7. **`resolve_v9` has no `kind` in the template manifest** (RF-40's commit `85a577386`): two
   existing tests fail on the base branch. A one-line fix on RF-40's branch; for the user.

## Summary (fill in at the end)
**What changed.** A grid corridor as an add-on world, with no model call (USD 0):
- `negsim/grid/` (new; entry point `python -m negsim.grid`): the corridor of AS6, moves in the
  walker's own frame, a parallel tick with AS7's clash rule plus RF-50's crossing-paths rule,
  slower walkers, arrival, deadlock and time limit;
- the measures: passed, passing distance (the gap when level), blocked face to face, squeezed past,
  the dance, deadlock, resolved, ticks to pass, per-person counts;
- a text print, scripted walkers, round 1's cases on the grid;
- `configs/grid/corridor_v1.yaml` (tagged values), `tests/test_grid.py` (38 tests);
- `docs/action-space.md`: section 8.1 as built, 8.2 left to RF-51, AS8 withdrawn and AS9 amended
  (section 10), the deadlock placeholder (section 11).

**Why.** The supervisor's point 1 (SV7): a grid limits the action space and removes angles. The user
moved the grid ahead of RF-41 (dropped), RF-46 and the menu on 2026-11-25.

**How it was verified.**
- The scripted walkers give their expected outcomes on both geometries over 5 seeds (tested); over
  20 seeds, `python -m negsim.grid scripts` gives the table in section 8.1.
- Each clash rule, slow walkers, arrival and seed rebuild are tested directly; 40 random seeds per
  geometry keep the invariants (one person a cell, inside the grid, at most one row and lane a tick,
  no swaps).
- `analysis.lateral.when_level` reads a grid trajectory unchanged.
- Full suite: 2359 passed, 12 skipped, 3 failed, all three pre-existing (09:53 entry). AS1: the diff
  against the base lists only new files, plus `docs/action-space.md` (task 4) and this log.
