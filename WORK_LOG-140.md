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

### 2026-11-26 07:05 UTC — reading, then the build
- **Read:**
  - RF-50's `world.py`, `measures.py`, `cases.py` and `__main__.py`;
  - the continuous protocol: `_ask`, `_apply`, `_factor_lines`, `_debrief`;
  - the experiment layer: `run_session`, `first_asked`, `session_factors`, `Session`;
  - `request_with_retry`, `load_template_data`, the price table, and RF-40's records.
- **Found:**
  - the existing template manifest is an existing file, so the grid's templates live in their own
    folder with their own manifest (AS1);
  - RF-40's 1,632 session records are in the repo with prompts and measured token counts, so the
    cost estimate can be calibrated on them;
  - RF-47's and RF-48's mock policies already answer with every option of each menu.
- **Built (new files only):**
  - `negsim/grid/menu.py`: RF-47's and RF-48's tables, with the amounts rounded to cells and ticks.
  - `negsim/grid/prompt.py`: the view as data (`GridView`), and the template's loading, with a hash
    check against the grid's own manifest, and rendering.
  - `negsim/grid/templates/`: the two templates and `MANIFEST.json`, generated from `resolve_menu_v1`
    and `resolve_menu_abs_v1` so that the shared text is copied, not retyped.
  - `negsim/grid/agents.py`: the session. It uses its own tick loop around RF-50's `step`, with the
    same end rules as `world.run`, because `run` has no hook after a tick, where a plan's moves are
    consumed.
  - `negsim/grid/experiment.py`: RF-40's silent sessions, the counterbalance, records, outcomes and
    the cost estimate. It refuses any condition but silent, and any paid client or cap.
  - The two configs.
- **Smoke run (4 sessions):** the prompts read correctly, and sides and lanes check out from both
  walkers' positions.
  - One line lacked a verb ("There two lanes between you and the wall on your left"). It became "You
    have two lanes on your left before the wall, …", and the template was re-hashed before any use.
- **AS1 check:** `git diff --cached --diff-filter=M` against the base lists no file. Every change is new.
- **Choices of mine, flagged for the user:**
  - **When an agent is asked.** A meeting is predicted when the other is in view, ahead, and at most
    one lane away (two lanes is 0.8 m, inside H1). An agent is asked again only while that holds: a
    change of the other's, its own plan ending, or a blocked move, at least 1 s apart, up to 6 times.
  - **Both asked at the same tick** in `first_asked`'s order. In silent, neither hears the other.
  - **A move into a taken cell** is tried again next tick (and may prompt a new decision). A move
    into a wall is dropped.
  - **The time to meet** is the time until the two are in adjacent rows.
  - **No body width and no top speed** in the view (one cell each; a cell a tick at most). **One
    format for everyone in view**, near or far. RF-40's template shows the same lines on a short line
    too, less the speed and body width.
  - **The counterbalance** goes by repeat pairs (1-2 against 3-4), so that it does not move with who
    is asked first, which alternates odd and even. The 8 counterfactual-pair sessions are first runs,
    so the split is 72 against 64.
  - **The view's wording.**

### 2026-11-26 07:15 UTC — tests and the rehearsal
- **`tests/test_grid_agents.py`:** 20 tests, passing together with RF-50's and the hygiene test
  (65 in all). Three first failures were my own test mistakes:
  - a walker placed next to the wall it was to step towards;
  - in the known state each sees the other to its *right*, as in `apart_20cm`;
  - two who carry on reach the grid's 3 s deadlock after 4 decision points each, not 6.
- **The mock rehearsal** (`runs_mock/rf51_rehearsal`), both frames, 07:13 to 07:15 UTC: 272 of 272
  sessions completed in each.

  | | own frame | absolute frame |
  | --- | --- | --- |
  | decision points | 1,315 | 1,295 |
  | calls | 2,070 | 2,054 |
  | debriefs | 515 | 515 |
  | unreadable after the retry (`unknown_action`) | 136 | 116 |
  | capped by the wall | 26 | 32 |
  | no room | 12 | 0 |

  - Every option was chosen in both.
  - No agent was asked more than 6 times; 6 was reached in 14 absolute-frame sessions.
  - No absolute-frame prompt names an own side (0 of 1,295).
  - The mock's outcomes say nothing about behaviour.
- **Cost estimate for RF-52** (`summary.json`, `cost_estimate`), calibrated on RF-40's 2,265 silent
  calls:
  - **the calibration:** 0.275 tokens per prompt character, 65% of prompt tokens cached, and replies
    of 155 tokens (decision) and 144 (debrief);
  - **the range:** RF-40's reply length, and 50 tokens shorter for a decision (an assumption, as in RF-47);
  - **own frame:** USD 0.263 to 0.310 off-peak (0.526 to 0.620 peak);
  - **absolute frame:** USD 0.269 to 0.316 off-peak (0.539 to 0.631 peak);
  - **both: about USD 0.53 to 0.63 off-peak**, at the mock's call counts. A model may need more or
    fewer calls.

### 2026-11-26 07:31 UTC — the full suite
- 07:13 to 07:31 UTC: **2439 passed, 16 skipped, 1 failed.**
  - The failure was `test_encounter_protocol.py::test_stop_at_cap_runs_until_the_guard_stops_it_and_the_spend_stays_under_the_cap`,
    the known one that fails in DeepSeek's peak hours (06-10 UTC on weekdays).
  - It touches no grid file. It passed off-peak in RF-47's and RF-48's runs of the suite, on the same
    existing code.
  - It was not rerun off-peak for this issue.
- No existing test needed a change: the grid adds only new files.

## Open questions / risks
1. **For the user, before RF-52's paid run:** the choices above, especially when an agent is asked
   again, and the view's wording in both frames.
2. **`analysis.gate` needs the ORCA baselines**, which the grid cannot give. The grid's
   `outcomes.csv` has `resolved_plan_only` and `collision_plan_only`; the gate is RF-52's to decide
   (#141, open decision).
3. **The deadlock window (3 s) can end a run before the agents have used their 6 decision points**
   (tested: two who carry on are asked 4 times). This is RF-50's rule, accepted by the user, applied
   to LLM agents. A model that waits twice in a row could be cut off.
4. **Only `wide_corridor_head_on`'s two geometries** are mapped; other cases are refused.

## Summary (fill in at the end)
**What changed.** LLM agents on the grid, in new files only (AS1), mock only (USD 0):
- **Templates:** `resolve_grid_v1` (own frame) and `resolve_grid_abs_v1` (lanes numbered from the blue
  wall), frozen in the grid's own template folder and manifest. Their fixed text is the corridor menu's
  silent text, byte for byte; the view is in cells and lanes.
- **The menu:** RF-47's and RF-48's, done in cells.
- **The session:** D4 and D5 on the grid, the plan carried out between decisions, and a debrief.
- **The experiment:** RF-40's 272 silent sessions on the grid, with who starts off the centre lane
  counterbalanced, and a cost estimate calibrated on RF-40's silent calls.
- **Docs:** `docs/action-space.md` section 8.3, both READMEs.

**Why.** The supervisor's points 1, 3 and 5: a grid limits the action space and removes angles. The
two frames test whether naming walls instead of sides helps there too.

**How it was verified.**
- **New tests:** 20, among them the view's text for a known grid state in both frames, a move towards
  a wall for each heading, and the counterbalance.
- **The full suite:** 2439 passed. The one failure was the known peak-hours test, which no grid file
  touches.
- **AS1:** no existing file modified.
- **The mock rehearsal:** both frames, 272 of 272 sessions each.
- **Cost estimate for RF-52:** about USD 0.53 to 0.63 off-peak for both frames.
