# Work Log — Issue #137: RF-48: absolute positions: places and moves in the corridor's own frame, not the agent's left and right: resolve_menu_abs_v1 (mock only)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/137
**Branch:** feat/137-rf48-absolute-frame (cut from `feat/136-rf47-menu-of-actions`, since PR #148 is not merged yet; RF-48 builds on RF-47's menu)
**Started:** 2026-11-26 05:38 UTC (from `date -u`)

## Understanding the issue
The supervisor's point 3 (November 2026): "Can test with absolute positioning". In RF-40, DeepSeek
took the other person's left and right for its own: "on your right" was said the wrong way round in
16 of 27, and a heard side made room in only 35 of 100. In a frame both people share, one wall is
the same wall to both, so nobody has to convert.

RF-48 builds RF-47's menu in that frame: `resolve_menu_abs_v1`. Code turns a move named by a wall
into the agent's own left or right for the executor. Mock only; RF-49 runs it.

AS5 as revised by the user on 2026-11-26 (`docs/action-space.md`, section 7; the comment on #137):
- **the walls get neutral landmark names**, not compass names (RF-43's recommendation);
- **positions are measured from one wall**;
- **moves are named by the walls**, and the parser converts them;
- **talk names the walls**, with no facing note;
- **the agent is not told which way it walks**.

The landmark words are this issue's to draft.

## Plan
1. `view.py`: an optional `Frame` on the view, with:
   - the wall on the agent's own left now;
   - its distance to each wall;
   - each person in view's distance from wall a;
   - for each earlier decision, the wall that was on its left.

   Every new field is left out of the record when unset, so earlier records read byte for byte as
   before.
2. `perceive.py`: fill the frame when the core template has walls (`view_in`, `Perceiver.look`).
   WHERE YOU ARE gets the frame's passage line in place of the scenario's "on your left / on your
   right" line, by an override passed to the scenario plug-in's place lines.
3. `prompt.py`: under a template with `walls`, render in the frame:
   - where people are, and which way they drift or cross;
   - what they did since the agent last looked;
   - where an unseen voice came from;
   - how far the agent has moved aside.
4. `menu.py` and `reply.py`: a table option may move `towards` wall a or b. The conversion maps it
   to the agent's own side from its heading now. `ReplyContext` and `menu_context` gain the wall on
   the agent's left.
5. The template `resolve_menu_abs_v1` (frozen), `configs/resolution/menu_table_abs_v1.yaml`, a mock
   policy and the config `round1_head_on_menu_abs.yaml` (RF-47's sessions, only the template and
   table changed).
6. Tests:
   - for each heading, a move named by a wall goes to the same wall;
   - the view in the frame;
   - earlier templates and records unchanged.
7. Mock rehearsal, cost estimate, docs, PR.

## Progress log

### 2026-11-26 05:40 UTC — reading
- **What I did:** read the issue and its comment (AS5 rechecked, landmark names), `docs/action-space.md`
  section 7, RF-43's recommendation (`literature/frames-of-reference/README.md`, section 6), and these files:
  - `resolve_menu_v1`;
  - `scenario_passing_v1`;
  - `view.py`, `perceive.py` (`look`, `_seen_person`, `_done`, `changes_since`, `voice_from`, `view_in`);
  - `prompt.py`'s rendering;
  - `menu.py`, `mock.py`.
- **Found:** a view says the agent's left or right in seven places:
  1. the instruction "Left and right always mean your own left and right";
  2. WHERE YOU ARE (the scenario's "the wall on your left is … m from you");
  3. where a person is ("ahead of you and 12° to your left");
  4. which way they drift or cross;
  5. what they did since the agent last looked ("moved over to your left");
  6. where an unseen voice came from;
  7. how far the agent has moved aside since a decision.

  The sidesteps of the menu are the eighth.
- **What the code measures:**
  - every side in the view is against where the agent faces (`Body.facing_rad`);
  - each decision's sideways movement is against where it faced then;
  - the room to each wall is against its path.

  In a straight corridor along x, a facing within 90° of the path has the same wall on its left, so
  one value per view, the wall on the agent's left, turns every side into a wall.

### 2026-11-26 05:51 UTC — the build
- **What I did:**
  - `view.py`: a `Frame` (the wall on the agent's left now, its distance to each wall), a person's
    `from_a_m`, and an earlier decision's `left_wall`. All of them are left out of the record when unset.
  - `perceive.py`:
    - `Perceiver.look(wall_distances=...)` fills them;
    - `view_in` does so when the core template has walls, from the agent's own record (free width
      to each side). It refuses a path more than 45° off the x axis, or a side with no wall in range.
  - The scenario plug-in's `place_lines` takes an override of its lines (`scenario.py`, `passing.py`).
    With none, the lines are exactly as before.
  - `prompt.py`: under a template with `walls`:
    - a person is ahead of, level with or behind the agent, at a distance from wall a;
    - drifts, crossings, moves over, unseen voices and the agent's own sideways movement go towards a wall;
    - a template with walls refuses a view without a frame.
  - `menu.py`:
    - a sidestep may go `towards: a|b`, which `steps_for` turns into the agent's own side from `left_wall`;
    - a table names its moves one way only;
    - `menu_context(frame=True)` adds `left_wall` (from `body_of(agent).facing_rad`, as the view does).
  - `reply.py`: `ReplyContext.left_wall`. `protocol.py`: one argument.
  - `experiment.py`: the cost preview's worst view has the frame. My first smoke run failed here
    ("the view has no frame"), which is how I found it.
  - The template `resolve_menu_abs_v1` (frozen, MANIFEST), the table `menu_table_abs_v1.yaml`, the mock
    `resolution_menu_abs_rehearsal_v1`, and the config `round1_head_on_menu_abs.yaml`.
- **Choices of mine, flagged for the user:**
  - **The wall names, "the blue wall" (+y) and "the yellow wall" (-y).**
    - Colours have no direction habit and no idiom.
    - RF-43's "the shop side" could draw an agent towards it.
    - "Wall A / wall B" is the plainest option, but it reads less like a place a person is in.
  - **The agent gets its distance to both walls**, and the people it sees are placed from the blue
    wall only. AS5 says "measured from one wall". Both distances for the agent keep the information
    equal to RF-47's view, which gives both.
  - **Ahead, level (85° to 95°) and behind**, with no angle, in place of "ahead of you and 12° to your
    left". The distance from the blue wall says where across.
  - **The same colour is always at +y.** In head-on, person 1 (walking +x) always has the blue wall on
    its left. Swapping the names in a second template would counterbalance this, if the user wants it.
  - **The talk sentence:** "If you say which way you or anyone should go, name the wall: the blue
    wall or the yellow wall." It asks, and does not forbid left and right.
- **Smoke run** (4 sessions, scratchpad):
  - each agent is told the other's distance from the blue wall exactly as the other is told its own;
  - "towards the yellow wall" was coded `right` for the agent whose left is the blue wall;
  - its distance from the blue wall then grew by 0.46 m.

### 2026-11-26 05:52 UTC — tests; the suite and the rehearsal started
- **`tests/test_rf48_absolute_frame.py`:** 31 tests, all passing, together with RF-47's 27.
  - **The acceptance criterion:** for each heading, aligned and 20 cm apart, a move towards the blue
    wall ends at +y and one towards the yellow wall at -y, read from the simulation's positions.
  - **The view:** the two agents' frames agree with each other; no own side appears in any prompt;
    each side is told as a wall, for either wall on the left.
  - **Refusals:** mixed tables, a wall table under a side template and the reverse, and walls that
    are not two different names.
  - **Unchanged:** RF-47's records have no frame keys; earlier templates have no walls.
  - **Also:** the template against `resolve_menu_v1`; no compass word anywhere in the template; the
    config against RF-47's; the mock; the cost preview.
- **Enumeration tests updated with a note:** `test_resolution.py`'s mock policies, and `test_ethnicity.py`'s
  list of configs written before #92.
- **Started in the background:** the full suite, and the full mock rehearsal into `runs_mock/rf48_rehearsal`.
  This is DeepSeek's peak window, so the known `test_stop_at_cap_...` failure is expected.

### 2026-11-26 06:30 UTC — the full suite
- 05:51 to 06:30 UTC: **2419 passed, 16 skipped, 1 failed.**
  - The failure was `test_repo_hygiene.py::test_only_pinned_third_party_packages_are_imported`: my
    test file imported constants from `test_rf47_menu`, a test module that test does not list.
  - I copied the constants into `test_rf48_absolute_frame.py` (with a note) rather than edit the
    hygiene test. Rerun with it: 38 passed.
  - The peak-hours `test_stop_at_cap_...` passed this time.

### 2026-11-26 06:45 UTC — the mock rehearsal
- **The first background run** (05:51 to 06:38 UTC) wrote all 544 sessions, but printed nothing and
  wrote no `outcomes.csv`, `summary.json` or `report.md`. I do not know why.
- **Resumed** with the same command: "completed: 0 session(s) run, 544 already done; actual cost USD
  0.000000", with every output written.
- **`runs_mock/rf48_rehearsal`** (gitignored): RF-47's 544 silent and talk sessions, all completed.
  - 3,411 decision points, 3,727 attempts;
  - **every decision point's view has the frame, and no prompt (fixed text or view) has an own-side
    phrase** (the test's pattern);
  - every option was chosen;
  - 362 sidesteps were capped by the wall and 8 had no room;
  - 152 replies were unreadable after the retry (`unknown_action`). Among them is the mock's own-side
    option, "step a little to your right".
- **`python -m analysis.gate`** reads the run unchanged: 24 of 128 design sessions resolved in
  `plan_only` under the mock. The mock is not a model, so this says nothing about behaviour.

## Open questions / risks
1. **For the user, before RF-49's paid run:** the wall names, the two distances for the agent, the
   ahead/level/behind words, the talk sentence, and whether to counterbalance which colour is on
   person 1's left (above).
2. **The facing.** An agent's left wall comes from where it faces. During a sidestep at 30° it faces
   30° off the path, which leaves the same wall on its left. Only a facing more than 90° off the path
   would flip it. Agents back up facing their path (`body_of`), so nothing in round 1 turns that far.
   It is not guarded in code beyond the 45° check on the path.
3. **The frame is for a corridor along x** (`wide_corridor_head_on`). The group and crowd plug-ins
   inherit the place-line override, but RF-48 neither runs nor tests them in the frame.

## Summary (fill in at the end)
**What changed.** RF-47's menu in the corridor's own frame, behind a template flag (`walls`), mock
only (USD 0):
- **The view** (`view.py`, `perceive.py`, `prompt.py`):
  - the two long walls have landmark names, "the blue wall" and "the yellow wall";
  - the agent is told its distance to each, and the people it sees by their distance from the blue wall;
  - drifts, moves over, unseen voices and its own moves aside go towards a wall;
  - there is no facing note, and the heading is not told.
- **The menu** (`menu.py`, `reply.py`, `protocol.py`): the sidesteps go "towards" a wall, and code
  turns the wall into the agent's own side.
- **New files:** template `resolve_menu_abs_v1` (frozen), table `menu_table_abs_v1.yaml`, config
  `round1_head_on_menu_abs.yaml`, mock policy `resolution_menu_abs_rehearsal_v1`, and 31 tests.
- **Other changes:**
  - the scenario plug-in's place lines take an override;
  - the cost preview's worst view has the frame;
  - two enumeration tests updated with a note;
  - `docs/action-space.md` section 7.1, both READMEs.

**Why.** The supervisor's point 3. RF-40's agents mistook the other's left and right for their own.
In a shared frame nobody converts, and RF-49 measures whether that helps, or whether both now head
for the same wall.

**How it was verified.**
- **The new tests**, including the acceptance criterion: for each heading, a move towards a wall
  goes to that wall, read from the simulation's positions.
- **The full suite:** 2419 passed. The one failure was a hygiene rule my test file broke; after the
  fix, the rerun of the affected tests passed.
- **The mock rehearsal:** the whole design ran (544 sessions), every view had the frame and no prompt
  named an own side, and `analysis.gate` reads it.
