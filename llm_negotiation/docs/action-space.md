# The action space: what an agent is told and what it can choose (RF-42 to RF-52)

Issue #131 (RF-42), track #55. Written on 2026-11-25.

At the supervisor meeting of November 2026, held after RF-40, the supervisor made eight suggestions about how the agents are asked to act. They are recorded word for word in the root `CLAUDE.md` ("Supervisor decisions") and numbered SV7 to SV14 in `architecture.md`, section 8.8. RF-43 to RF-52 (#132 to #141) act on them.

This document fixes, once, what those issues share:
- the variants;
- the baseline;
- the measures;
- the menu and the amounts behind its words;
- the absolute frame;
- the grid;
- template names, and the order of work.

The decisions are **the user's**, made on 2026-11-25 on their own authority, and numbered **AS** (action space). AS1 is not D1 (the resolution design, `resolution.md`), not DD1 (this project's proposals) and not SV1 (the supervisor's points). Anything marked *proposed* is the assistant's, for the issue named to settle. Anything marked *placeholder* has no source.

## 1. The supervisor's points and the issues that act on them

| SV | Point (short) | Issues |
| --- | --- | --- |
| SV7 | a grid environment, to get rid of angles | RF-50 (#139), RF-51 (#140), RF-52 (#141) |
| SV8 | search on left and right orientation | RF-43 (#132) |
| SV9 | test absolute positioning | RF-48 (#137), RF-51; run in RF-49 (#138), RF-52 |
| SV10 | output words instead of numbers | RF-47 (#136) |
| SV11 | describe the actions and let the agent choose | RF-47 |
| SV12 | the share of hallucinated decisions | RF-45 (#134), then every later run |
| SV13 | behave like the person, with no need to speak like them | RF-46 (#135) |
| SV14 | how the YC Labs game agents' decisions are modelled | RF-44 (#133) |

All eight are recorded as **suggestions** (the notes say "can ..."), not instructions.

## 2. The variants

| | World | Reply | Frame | Template | Built in | Run in |
| --- | --- | --- | --- | --- | --- | --- |
| A | continuous corridor | free steps: m/s, degrees, metres | own left and right | `resolve_v9` | RF-40 | RF-40 (the baseline) |
| B | continuous corridor | a menu, amounts in words | own left and right | `resolve_menu_v1` | RF-47 | RF-49 |
| C | continuous corridor | a menu, amounts in words | absolute | `resolve_menu_abs_v1` | RF-48 | RF-49 |
| D | grid | the grid's moves, in words | own left and right | `resolve_grid_v1` | RF-50, RF-51 | RF-52 |
| E | grid | the grid's moves, in words | absolute | `resolve_grid_abs_v1` | RF-50, RF-51 | RF-52 |

`resolve_v10` (RF-46) is A with one line added on speech. It is not an action-space variant.

## 3. The baseline, and what every run shares

**The baseline is RF-40's silent condition** (#129): 163 of 256 sessions resolved (0.64) in `plan_only` (`runs/rf40_round1_head_on_turn_taking/comparison_report.md`).

New runs keep RF-40's design, so that factor effects and rates compare:
- the people and cells: 32 cells × 2 geometries × 4 repeats, plus 16 sessions in counterfactual pairs, so 272 per condition;
- `deepseek-flash`, thinking off, temperature 1.0, a reply cap of 300 tokens;
- `keep_line_replan`, up to 6 decision points;
- in talk, `turn_taking` with `always_heard`;
- the debrief `resolve_debrief_v2`.

Two checks before any paid run: the model's fingerprint against RF-40's (`bc19ba97...`), and the balance.

- **B and C pair with A session by session:** the same world and people, with only the template changed.
- **D and E pair with each other**, but not with A to C: the grid is a different world, so it is compared with them by rates.

## 4. Measures, for every variant

- **Resolved** in `plan_only`, and the gate (0.50, carried over from RF-10).
- **The pavement dance:** both people move aside towards the same wall.
- **Collisions and near misses** (on the grid: see section 8).
- **Unreadable replies** after the retry.
- **The hallucination share** (RF-45, codebook `hallucination_v1`).
- **The factor effects:** does the agent still act like its person? In RF-40, passing first followed the agent's own assertiveness (OR 8.4), and slowing followed the other person's mobility aid, age and load.
- **RF-37's human targets** where they apply (`configs/human_targets/head_on_v1.yaml`). On the grid, distances come in steps of 0.4 m (section 8).
- **In talk:** messages that name a side, the frame they use, and whether the listener's next move fits (`analysis/turn_taking.py`).

## 5. Conditions (AS2)

**AS2. RF-49 runs silent and talk; RF-52 (the grid) runs silent only** (the user, 2026-11-25).

RF-40 found that signals and talk add nothing over silent. But all its left and right errors were in talk, where an absolute frame should matter most. RF-46 (`resolve_v10`) is talk only, in its own issue.

*Estimate*, at RF-40's cost of about USD 0.0015 a session:
- RF-49 and RF-52 together: about USD 1.2;
- RF-46: about USD 0.4 to 0.5;
- the balance was USD 2.96 on 2026-11-02.

Each paid issue needs its own approval and cap in `CLAUDE.md`.

## 6. The menu, and the amounts behind its words (AS3, AS4)

**AS3. The menu and its amounts** (the user, 2026-11-25: "Accept as proposed"). One option per decision. Code turns each option into the existing step format, so the executor, the replay, `code_plan` and the analyses are reused.

| Option, as the agent reads it | Plan | Source |
| --- | --- | --- |
| carry on as you are | no change (`[]`) | none needed |
| slow down a little | speed × 0.81 | Huber et al. 2014, Results 1: instructed slow walking 1.15 m/s against normal 1.42 m/s (`refs/rf14_huber2014_speed_path.txt:452`). A ratio of walking speeds, not a measured slowing in an encounter. |
| slow down a lot | speed × 0.5 | *placeholder* |
| stop and wait | stand still for 1 s, then asked again if the meeting is still predicted | *placeholder*: D5's "at least 1 s apart" |
| step a little to your left / right | sidestep 0.47 m | Half of H1, 0.93 ± 0.17 m between centres when two young adults pass (Rapos et al. 2021, abstract; RF-37's H1). Two people who each step a little apart pass at H1. About one shoulder width: 49.8 cm effective (Yamamoto et al. 2019; `parameters.md`, `radius`). |
| step well to your left / right | sidestep 0.93 m, or as far as the wall allows | H1: one person alone opens the human passing distance |
| step back | back up 0.5 m at 0.92 m/s | 0.5 m is a *placeholder* (about one body width). The speed is `backing_speed`, from Nakahara et al. 2005 (`parameters.md`). |

- **No option is a turn by an angle**, and none says who goes first.
- A sidestep moves aside at 30° and then walks on parallel. This is `resolve_v8`'s existing angle, itself a placeholder.
- **"As far as the wall allows":** in round 1's corridor (1.75 m wide, body radius 0.25 m), a body's centre can be at most 0.625 m from the middle. So from an aligned start, "step well" is capped at about 0.6 m. RF-47 states the cap and tests it.

**AS4. The menu extends the existing code behind a template flag** (the user, 2026-11-25), as RF-29 (`sidestep: true`) and RF-40 (`exchange: turn_taking`) did:
- the reply parser and the protocol accept an `action` field only when the template says so;
- tests prove that every earlier template and config behaves exactly as before.

This applies to RF-47 and RF-48 only. The grid is an add-on (AS1).

### 6.1 As built in RF-47 (#136)

*Built on 2026-11-26, mock only.* Code: `negsim/resolution/menu.py` (new), with the flag read in `reply.py`, `prompt.py` and `protocol.py`. Table: `configs/resolution/menu_table_v1.yaml` (AS3's numbers, each tagged). Templates: `resolve_menu_v1` and `resolve_debrief_v3`, both frozen. Config: `configs/resolution/round1_head_on_menu.yaml`. Tests: `tests/test_rf47_menu.py`.

- **The template** (`resolve_menu_v1`) is `resolve_v9` word for word, with these changes:
  - each condition's first instruction says how the agent moves is "chosen from the ACTIONS below";
  - the reply has `"action"` (one option's name) in place of `"steps"`;
  - an ACTIONS block replaces the STEPS block: the nine options, each with one sentence that has no number and no angle, and no option says who goes first;
  - the wrapper and the three history outcomes no longer speak of "steps".

  All four conditions have a section. The wording is the assistant's draft.
- **The flag:** `menu_table` names the table. The template lists the options' names and words, and the table must list the same names in the same order, or the template is refused.
- **Reading a reply:**
  - the name is matched ignoring case, extra spaces, surrounding quotes and a full stop;
  - a missing `action`, or a name not on the menu, is unreadable (`missing_action`, `unknown_action`), with one retry as for any other failure;
  - a `steps` key beside it is ignored and flagged (`steps_ignored`);
  - the record keeps the option as `parsed.action`, and earlier records are written as before.
- **What each option becomes**, given to the executor unchanged:
  - "carry on" is `[]`, exactly a free-step reply's "carry on as you are": keep the line (`keep_line_replan`) at the usual speed;
  - the two slow-downs are one step at 0.81 or 0.5 × the agent's *usual* speed, until `other_passes`. This is a `[design]` choice, as is the event: Huber's ratio compares two walking speeds, not a slowing from the current one;
  - "stop and wait" is `speed_mps` 0 for 1 s. The plan then ends, and D5 asks again if the meeting is still predicted;
  - the sidesteps use `resolve_v8`'s sidestep (30°, then parallel) at the usual speed;
  - "step back" is `back_up_m` 0.5 at the backing speed.
- **As far as the wall allows:**
  - a sidestep is planned no further than the room to the wall across the path (from the perception record's `free_width_left_m` or `free_width_right_m`), less the body radius and a 0.05 m margin (`[design]`, so that ORCA's wall margin does not stop the step short of its distance). From an aligned start in round 1's corridor, "step well to your right" becomes **0.57 m**, against AS3's "about 0.6 m", and the step ends `sidestepped` (tested);
  - with under 0.05 m of room there is no sidestep: the plan is `[]`, flagged `no_room:<side>`;
  - a shortened sidestep is flagged `capped_by_wall:<side>`.
- **The debrief, `resolve_debrief_v3`** (*the assistant's choice, for the user; section 3 names `resolve_debrief_v2`*): it is `resolve_debrief_v2` with one more line. A menu decision is listed as `You chose: "step a little to your right".`, where v2 would print the steps code made of it (`"metres": 0.47`), numbers the agent never saw. Decisions with steps read exactly as under v2.
- **The mock:** `resolution_menu_rehearsal_v1` covers every option, a name in other case with a full stop, a signal, a talk message, an option not on the menu, and an unreadable reply.
- **Unchanged (AS4, tested):** `resolve_v1` to `resolve_v9` have no menu; a reply under them reads as before, even with an `action` key; RF-40's config loads as before; and `resolve_debrief_v2` prints steps as before.
- **Mock rehearsal** (`runs_mock/rf47_rehearsal`, not tracked): the whole design ran, RF-40's 272 silent and 272 talk sessions, and all 544 completed.
  - 3,458 decision points, 3,802 attempts;
  - every option was chosen;
  - 386 sidesteps were capped by the wall, and 112 had no room;
  - 168 replies named an option not on the menu and were unreadable after the retry.

  The mock is not a model, so its outcomes say nothing about behaviour.
- **Cost estimate for RF-49** (from RF-40's ledger, `spend_ledger.jsonl`, off-peak):
  - RF-40's silent and talk sessions cost USD 0.375 and 0.445, so USD 0.82 for 544 sessions.
  - Under the menu the fixed text is about 750 characters shorter. That saves almost nothing, because it is the cached prefix (about USD 0.003 per million tokens).
  - A reply without the steps JSON should be shorter. Taking 50 fewer output tokens a decision as an assumption, not a measurement, the total is about **USD 0.71 to 0.82** for 544 sessions, if the menu needs as many calls as RF-40 did.
  - RF-49 runs the menu in two frames, so about USD 1.4 to 1.6 in all. It still needs its own approval and cap.

## 7. The absolute frame (AS5)

**AS5. Compass walls, heading not told: provisional, to be rechecked after RF-43** (the user, 2026-11-25).

- **Walls:** the corridor's two long walls are "the north wall" and "the south wall".
- **Positions** are measured from the north wall:
  - in the corridor, in metres ("you are 0.9 m from the north wall");
  - on the grid, as lanes counted from it ("lane 1, next to the north wall").
- **Moves** are named by the walls ("step a little towards the north wall"). The parser converts them to the agent's own left or right for the executor.
- **The agent is not told which way it walks.** If it were ("you walk east"), it could work out that "keep right" means "the south wall", but that brings back the conversion RF-40's agents got wrong. Without the heading, no keep-right habit can be used. Both outcomes are findings.
- **Talk:** the instructions ask the agent to name sides by the walls. There is no facing note.
- **Recheck:** before RF-48 is built, the user rechecks AS5 against RF-43's literature search (#132).
- **The expected trap:** two agents can both choose "the north wall". RF-49 and RF-52 measure how often they do.

*Revised by the user on 2026-11-26* (the recheck above, asked at the start of RF-47, #136): **the walls get neutral landmark names, not compass names**, as RF-43 recommends (`literature/frames-of-reference/README.md`, section 6, item 3): compass words carry habits models fall back on (north as straight ahead, "left = west"), and a landmark name has none `[inference]`. The rest of AS5 stands: positions from one wall, moves named by the walls, the parser converting, talk naming walls, no facing note, and the heading not told. The landmark words themselves are RF-48's to draft. No study compares compass and landmark names for LLMs (RF-43's gap).

### 7.1 As built in RF-48 (#137)

*Built on 2026-11-26, mock only.* RF-47's menu in the corridor's own frame.
- **Template:** `resolve_menu_abs_v1`, frozen.
- **Table:** `configs/resolution/menu_table_abs_v1.yaml`.
- **Config:** `configs/resolution/round1_head_on_menu_abs.yaml`.
- **Tests:** `tests/test_rf48_absolute_frame.py`.
- **Code:** the frame is read from the template's `walls` in `view.py` (`Frame`), `perceive.py`, `prompt.py`, `menu.py` and `reply.py`. The scenario plug-in's place lines take an override, and the cost preview's worst view has the frame.

**The walls' names** (*the assistant's draft, for the user*): **"the blue wall"** (wall a, at +y) and **"the yellow wall"** (wall b, at -y).
- Colours are landmarks with no direction habit: no "north is ahead", no "left = west", and no idiom such as "a brick wall".
- RF-43's examples ("the window side", "the shop side") were not used, because a shop could draw an agent towards it.
- Which colour is at +y is fixed by the template. In head-on, the person walking +x has the blue wall on their left, and the person walking -x has it on their right. RF-49 could counterbalance this with a second template that swaps the names (section 11).

**What the agent is told**, against `resolve_menu_v1`:
- **The instructions:** "Left and right always mean your own left and right" becomes "The passage has two long walls, the blue wall and the yellow wall. They are the same two walls for everyone here, so where people are and which way anyone moves is told by these walls."
  - In talk, one more sentence follows: "If you say which way you or anyone should go, name the wall: the blue wall or the yellow wall."
  - The reply formats and retries are RF-47's, word for word.
- **WHERE YOU ARE:** "You are in a passage 1.75 m wide, between the blue wall and the yellow wall. You are 0.77 m from the blue wall and 0.98 m from the yellow wall." This replaces `scenario_passing_v1`'s "the wall on your left is …" line.
  - The agent gets both distances. AS5 says positions are measured from one wall, and that holds for the people the agent sees.
  - Giving both keeps the same information as RF-47's view, which also gives both.
- **WHO YOU CAN SEE:** "Person 1, 9.8 m away, ahead of you, 0.98 m from the blue wall."
  - A person is *ahead of*, *level with* (85° to 95°) or *behind* the agent, with no angle and no side. Their distance from the blue wall says where they are across the passage.
  - What one person is told of the other's place is what the other is told of their own (tested).
- **Drifts, crossings and moves over:**
  - "drifting towards the yellow wall by 15°";
  - "across your direction of travel towards …";
  - "moved over towards the blue wall".
- **An unseen voice:** "Someone towards the yellow wall from you, close by, says …". Ahead and behind are as before.
- **What came of a decision:** "Since then you have moved 0.5 m over towards the yellow wall". The wall is the one on that side when the agent decided.
- **No facing note:** `heard_frame` is off. A message is shown as said.
- **The heading is not told.** No compass word appears anywhere in the template (tested).

**The menu.**
- The four sidesteps become:
  - "step a little towards the blue wall" / "… the yellow wall";
  - "step well towards the blue wall" / "… the yellow wall".

  Each has the same sentence as in RF-47, with "towards the … wall" for "to your left/right". The other five options, and every number, are RF-47's.
- The table names a sidestep `towards: a` or `b` in place of `to: left` or `right`. The conversion turns the wall into the agent's own side from the wall on its left when it chooses (`menu_context`, from where it faces, as its view has it). The executor then gets exactly RF-47's sidestep, and the wall cap and its flags name that side.
- **What is refused:**
  - a table naming moves both ways;
  - a wall table under a template with no walls;
  - a side table under a template with walls.
- An own-side option such as "step a little to your right" is not on this menu, so it is unreadable (`unknown_action`).

**Tested (the acceptance criterion):**
- for each heading, aligned and 20 cm apart, "step a little towards the blue wall" moves the person to +y, and "… the yellow wall" moves them to -y;
- two people who both choose the blue wall get different own sides (one left, one right), and both move to +y. This is the trap issue #137 expects, which RF-49 measures.

**Unchanged (AS4, tested):**
- `resolve_v1` to `resolve_v9` and `resolve_menu_v1` have no walls;
- a view without a frame records no `frame`, `from_a_m` or `left_wall`, so earlier records are written as before;
- RF-47's sessions record and render as before;
- the scenario's place lines with no override are as before.

**Mock rehearsal:** see `WORK_LOG-137.md`.

**Cost estimate for RF-49's frame arm:** as RF-47's, about **USD 0.71 to 0.82** off-peak for 544 sessions.
- The fixed text is about the same length.
- The view lines are a few words longer per person (a distance from the blue wall in place of an angle), which is about 1% of the input.
- The same assumptions as RF-47's apply.

## 8. The grid (AS1, AS6, AS7)

**AS1. The grid is an add-on. It does not modify the current environment's code** (the user, 2026-11-25).
- Nothing existing is edited: the continuous corridor, ORCA, the executor, perception and the view, the protocol, the reply parser, the replay, the scenario plug-ins and their registry (`PLUGINS`), existing templates, configs and analysis modules.
- The grid lives only in new files, for example a `negsim/grid/` package with its own entry point, templates, configs and tests. It reuses existing code only by importing it.
- If an existing file would have to change, the user is asked first.
- Before each grid PR, `git diff --stat` against the base lists only new files (plus any change the user approved), and the existing test suite passes unchanged.

**AS6. Cells of 0.4 m, 5 lanes** (the user, 2026-11-25).
- **The cell:** Burstedde et al. 2001: "The size of a cell corresponds to approximately 40 × 40 cm². This is the typical space occupied by a pedestrian in a dense crowd" (arXiv cond-mat/0102397, section 2; `refs/rf42_burstedde2001_ca_arxiv.txt:132-135`).
- **The corridor:** 5 lanes make it 2.0 m wide. Round 1's is 1.75 m (Moussaïd et al. 2009; `parameters.md`), so the grid is 0.25 m wider. The centre lane lets an aligned start fit.
- **Length and starts:** round 1's 20 m and 8 m become 50 cells, with each person starting 20 cells from the middle.
- **Passing distances:** two lanes apart is 0.8 m between centres, inside H1's 0.76 to 1.10 m. Adjacent lanes are 0.4 m, closer than two bodies' 0.5 m (section 4).
- **The tick:** about 0.31 s, one cell at 1.3 m/s (Moussaïd et al. 2009). Burstedde et al. give "approximately 0.3 sec" from the same 1.3 m/s (`refs/rf42_burstedde2001_ca_arxiv.txt:142-146`).

**AS7. Clashes are settled by Burstedde et al.'s rule** (the user, 2026-11-25: the rule was stated in every option of the grid question, and the user chose among them): "If the target cell is occupied, the particle does not move. ... If more than one particle share the same target cell, one is chosen ... This particle moves while its rivals for the same target keep their position" (`refs/rf42_burstedde2001_ca_arxiv.txt:168-174`). The paper's simpler variant picks the winner at random with probability 1/m (line 324). Here:
- the winner is drawn from the session's seed;
- two people facing each other in one lane cannot swap cells: they block.

### 8.1 As built in RF-50 (#139)

*Settled in RF-50, 2026-11-25.* The proposals below were put to the user before building, and the user answered "Yes start". Where the build departs from them, it says so. The code is `negsim/grid/` (its own entry point, `python -m negsim.grid`), its parameters `configs/grid/corridor_v1.yaml` and its tests `tests/test_grid.py`. No existing file of the environment was edited (AS1).

**The corridor.** Lane 0 is the wall at -y and row 0 the end at -x. Cell centres in metres put the middle at x = 0 and the centre line at y = 0, as in round 1's corridor. With 50 rows there is no middle cell. Each person starts in the 20th cell from the middle on their side: rows 5 and 44, centres 7.8 m from the middle, 15.6 m apart (round 1: 8 m and 16 m). A person who reaches the last row on their way has arrived and leaves the grid. A run ends when both have arrived, at a deadlock, or after 60 s (195 ticks), as round 1's corridor.

**Moves**, in the walker's own frame:
- forward;
- forward and one lane to the left or right (the paper's 3 × 3 neighbourhood includes diagonals);
- one lane to the left or right in place;
- wait;
- one cell back.

Heading +x, one's own left is +y; heading -x, it is -y. This is how `analysis.lateral` counts it.

**The tick** is a parallel update. Occupancy is read at the start of the tick, as in the paper, so a cell left in the same tick is still occupied, and a follower does not move up into it until the next tick. Each tick runs in this order:
1. A slower walker acts only on the ticks at which its walked distance reaches the next cell; otherwise it holds. At 0.65 m/s it acts every second tick.
2. A move into a wall, or out past the end behind the walker, does not happen.
3. A move into an occupied cell does not happen. This rules out swaps.
4. **Crossing paths.** Two diagonal moves through one midpoint, to different cells, both do not happen: two people cannot cut through each other in an X. This is an **assumption of RF-50's**, agreed by the user on 2026-11-25, and is not in Burstedde et al.
5. A contest for one empty cell: one winner is drawn from the session's seed and the others stay (AS7).

Every refused move is recorded with its reason: `not_due`, `wall`, `occupied`, `crossing` or `contest_lost`. A run rebuilds exactly from its seed. The contest draws and each walker's own random stream are separate streams of the seed.

**Geometries** (`negsim/grid/cases.py`):

| Round 1's case | Layout | Continuous offsets (m) | Grid lanes | Lost to rounding (m) |
| --- | --- | --- | --- | --- |
| `head_on_de176842` | aligned | 0.0, 0.0 | 2, 2 | 0.0, 0.0 |
| `head_on_02dfbadb` | apart_20cm | +0.1, -0.1 | 2, 2 | 0.1, 0.1 |

An offset rounds to the nearest lane centre, and half a lane rounds towards +y. **What rounding loses:** 0.1 m is a quarter of a lane, so on the grid `apart_20cm` *is* the aligned case. The grid's two geometries are therefore:
- **`aligned`:** lanes 2 and 2.
- **`one_lane_apart`:** lanes 2 and 1, 0.4 m apart. With 5 lanes, one lane apart cannot be symmetric about the centre line. Walker 0 (person 1) keeps the centre lane and walker 1 is one lane to -y. This keeps `apart_20cm`'s sense: each is off to its own left and sees the other to its own right. Which person is off the centre line is a `[design]` choice that RF-51 may counterbalance.

The corridor is also 0.25 m wider than round 1's (AS6).

**Measures** (`negsim/grid/measures.py`):
- **Passed:** the first tick at which each is beyond the other along its own way. In one lane they cannot pass, because there are no swaps.
- **Passing distance:** the sideways gap at the moment they were level.
  - If they were in one row on a tick before passing, it is the fewest lanes between them on those ticks.
  - If they went from one side of each other to the other within a tick, each is taken to move in a straight line, so they were level halfway: the mean of the signed gaps before and after.
  - So H1 applies in steps of 0.2 m, not 0.4 m. Two lanes is 0.8 m, inside H1's 0.76 to 1.10 m.
  - *Changed while building:* the first version took the fewest lanes over every tick they were within a row, which counted an earlier face-to-face moment as the passing distance (`WORK_LOG-139.md`).
- **Blocked face to face** (the grid's collision): before passing, in one lane, in adjacent rows, facing. The centres are 0.4 m apart, closer than two bodies (0.5 m).
- **Squeezed past** (the grid's near miss): passed, but with a passing distance under two body radii (0.5 m). Adjacent lanes count, and so does sliding past diagonally from face to face (half a lane each).
- **The pavement dance:** before passing, either both changed lane towards the same wall on one tick (`dance_ticks`), or they ended up in one lane facing each other after either had changed lane. `first_changes_towards_same_wall` compares each one's first lane change, as `analysis.lateral`'s `towards_same_wall` does.
- **Deadlock:** no one advanced towards their goal for **3.0 s (10 ticks)**. A sideways step or a wait is no progress, so a dance in place ends as a deadlock.
  - *Changed while building* from the 16 ticks (about 5 s) the assistant proposed: 3.0 s is issue #24's window and round 1's corridor's (`deadlock.window_s`), so the two worlds' deadlock rates compare. **Accepted by the user on 2026-11-26** ("do the 3.0s").
  - Round 1's rule is "nobody has moved". The grid's is "nobody has advanced", which also counts a dance in place.
  - The number has no source of its own, so it stays a placeholder (section 11).
- **Resolved:** passed, never blocked face to face, not squeezed, no deadlock, within the time limit. This is round 1's definition.
- **Also reported:** ticks to pass, lane changes, waits, backs and refused moves, per person.

H2 applies in the same steps as H1. H3 (where a move aside starts) applies in cells. Targets on speed change apply only through "wait" and slower walkers. RF-52 says which targets apply.

**What `analysis.gate` and `analysis.lateral` can read.**
- The grid writes `trajectory.csv` with `step`, `agent_id`, `x_m` and `y_m` (cell centres). `analysis.lateral.when_level` reads it unchanged (checked on 2026-11-25).
- `measures.gate_columns` gives `outcome`, `resolved_plan_only` and `collision_plan_only`. The grid carries out moves with no avoidance steering, so its result stands for `plan_only`.
- The grid has no ORCA, so it cannot give `*_plan_orca` or `*_plain_orca`, which `analysis.gate` reads for its baselines. RF-52 decides how to fill them: for example, scripted walkers as the grid's baseline, or a grid-only gate. No existing analysis module was changed.

**Scripted walkers** (`negsim/grid/walkers.py`, no LLM). Each reacts when the other is ahead within 6 cells (2.4 m, a `[design]` choice for the scripts). Over seeds 1 to 20 (`python -m negsim.grid scripts`; the rows are tested):

| Script | aligned | one_lane_apart |
| --- | --- | --- |
| both keep right (one lane in from their right wall) | resolved, 0.8 m | resolved, 0.8 m |
| both keep left | resolved, 0.8 m | resolved, 0.8 m |
| one holds its lane, the other steps 2 lanes away | resolved, 0.8 m | resolved, 0.8 m |
| one holds, the other steps 1 lane away | squeezed past, 0.4 m | resolved, 0.8 m (it starts a lane off) |
| both step towards the same wall, in step (the dance) | dance, deadlock | dance, deadlock |
| both hold their lane | blocked face to face, deadlock | squeezed past, 0.4 m |
| random moves (mostly forward) | resolved in 10 of 20 | resolved in 10 of 20 |

### 8.2 For RF-51 to settle

- **Decision points:** event-driven as in D5, up to 6, never every tick. "Wait" lasts 1 s (about 3 ticks) and is then asked again (AS3). Between decisions, a lane change happens once, then the walker goes forward.

*Decided by the user on 2026-11-26* (asked at the start of RF-51, which then waited for RF-47 and RF-48):
- **The grid's menu is AS3's menu done in cells**, with the same words as the corridor's menu, so that the grid and the menu arms differ only by world. The proposal put to the user:
  - "carry on";
  - slow a little (the walker moves on 81% of ticks) or a lot (half);
  - "stop and wait" (1 s, 3 ticks);
  - step a little = one lane, moving while walking;
  - step well = two lanes;
  - step back = one cell.

  RF-51 fixes the details.
- **RF-51 counterbalances who starts off the centre lane** in `one_lane_apart`: half the sessions put person 2 in the centre lane instead, so that who starts off centre does not mix with the factors.
- **The absolute frame uses neutral landmark names** (AS5 as revised, section 7).

### 8.3 As built in RF-51 (#140)

*Built on 2026-11-26, mock only.* Everything is a new file, and no existing file of the environment changed (AS1). The pieces:
- `negsim/grid/menu.py`, `prompt.py`, `agents.py`, `experiment.py`;
- the templates `resolve_grid_v1` and `resolve_grid_abs_v1`, frozen in **`negsim/grid/templates/`** with their **own `MANIFEST.json`**, so the existing manifest is untouched;
- the configs `configs/grid/round1_grid.yaml` and `round1_grid_abs.yaml`;
- `tests/test_grid_agents.py`.

Run it with `python -m negsim.grid.experiment <config> --out <dir>`. Existing code is reused only by importing it:
- RF-40's design and people;
- RF-47's and RF-48's menu tables and reply parser;
- the retry and the debrief (`resolve_debrief_v3`);
- RF-47's and RF-48's mock policies;
- the view cone.

**The templates (silent only, AS2).**
- **The fixed text** is `resolve_menu_v1`'s silent section and ACTIONS block, byte for byte (tested), so the grid and the corridor's menu differ only by world. `resolve_grid_abs_v1` uses `resolve_menu_abs_v1`'s.
- **The view** is in cells and lanes. ABOUT YOU and the factor lines are as in RF-40. The body width and the top speed are not told: everyone takes one cell, and nobody walks faster than a cell a tick.
- **WHERE YOU ARE:** "You are in a corridor five lanes wide. The floor is divided into square cells 0.4 m across, in lanes along the corridor. Each person takes up one cell, and nobody can step into a cell someone else is in. Walking at 1.30 m/s, you move forward one cell about every 0.3 s." Then where the agent is:
  - own frame: "You have one lane on your left before the wall, and three lanes on your right before the wall."
  - absolute frame: "The lanes are numbered from the blue wall: lane 1 is next to the blue wall, and lane 5 is next to the yellow wall. You are in lane 2." This is AS5's "lane 1, next to the north wall", with RF-48's names.
- **WHO YOU CAN SEE:**
  - own frame: "Person 1, 8 cells ahead of you, one lane to your right: walking towards you at 1.30 m/s."
  - absolute frame: "… in lane 3: …"
  - Changes: "they have moved one lane to your left" or "… towards the yellow wall", stopped, slowed down, and so on.
- **What came of a decision:** "Since then you have moved one lane to your right" (or "… towards the yellow wall"), and the cells backed.
- **The time to meet:** the time until the two would be in adjacent rows, at their current speeds.
- The view's wording is the assistant's draft. One line was reworded before any use ("There two lanes between you …" lacked a verb), and the template was re-hashed.

**The menu in cells** (`negsim/grid/menu.py`, the user's decision of 2026-11-26).
- **Where the amounts come from:** RF-47's and RF-48's tables, read as they are, with each amount rounded to cells and ticks (`[derived]`).
- **What each option becomes:**
  - "carry on": forward;
  - the slow-downs: the walker's speed × 0.81 or 0.5 until the other has passed. A slower walker moves on fewer ticks (RF-50);
  - "stop and wait": 1.0 s / 0.31 s = 3.25, so 3 ticks of waiting, then forward;
  - "step a little": 0.47 m / 0.4 m, so one lane;
  - "step well": 0.93 m, so two lanes. Each lane is a move forward and one lane over, then forward;
  - "step back": 0.5 m, so one cell back, then forward.
- **As far as the wall allows:** with fewer lanes free, as many as there are (`capped_by_wall:<side>`); with none, no move (`no_room:<side>`).
- **In the absolute frame**, a move towards a wall becomes the walker's own side from its heading. Tested: for each heading, it goes to that wall.

**When an agent is asked** (D4 and D5 on the grid; *the assistant's reading, for the user*).
- **A meeting is predicted** when the other is in view, ahead, and at most one lane away. The view is RF-40's 10 m and 75° either side, between cell centres. Two lanes apart (0.8 m) is inside H1, so it is no meeting.
  - The first decision point is the first tick this holds. In round 1's geometries, that is at 9.2 m (23 cells).
- **Asked again** while a meeting is still predicted and before passing, at least 1 s after the last decision (4 ticks), when any of these holds:
  - the other has done something new: moved lanes, stopped, started, slowed down, sped up, walked backwards or came into view;
  - the agent's own plan has ended;
  - the agent's move was blocked.

  At most 6 times.
- **Both are asked at the same tick**, in the order `first_asked` gives. In silent, neither hears the other.
- **An unreadable reply** after the retry changes nothing.
- **A move into a taken cell** is tried again next tick.
- **The debrief** (`resolve_debrief_v3`) follows the run.

**The sessions.**
- **The people and cells:** RF-40's 272 silent sessions (its config is `design_from`), the same people and the same factor lines.
- **The geometries:**
  - `head_on_de176842` becomes `aligned` (lanes 2 and 2);
  - `head_on_02dfbadb` becomes `one_lane_apart`.
- **Who starts off the centre lane is counterbalanced** (the user, 2026-11-26), by repeat:
  - in repeats 1 and 2, person 2 is off centre (lanes 2 and 1, RF-50's layout);
  - in repeats 3 and 4, person 1 is (lanes 3 and 2).

  Either way, each sees the other to its own right. Grouping by repeat pairs keeps this apart from who is asked first, which alternates odd and even.
- **The split:** the 8 counterfactual-pair sessions in this geometry are first runs, so `one_lane_apart` has person 2 off centre in 72 sessions and person 1 in 64. `aligned` has 136.

**The record** of each session:
- its decision points: the view as data, the prompt, the attempts, the option, and the grid plan given;
- the debriefs;
- RF-50's measures (`pair_outcome`) and `gate_columns`;
- a trajectory CSV that `analysis.lateral` can read.

`outcomes.csv` and `summary.json` cover the whole run. `analysis.gate` still needs the ORCA baselines the grid cannot give; that is RF-52's to decide (#141).

**Mock rehearsal** (`runs_mock/rf51_rehearsal`, not tracked): both frames, 272 sessions each.
- All sessions completed.
- Decision points: 1,315 in the own frame and 1,295 in the absolute frame.
- Every option was chosen.
- No agent was asked more than 6 times, and the cap of 6 was reached in 14 sessions.
- No absolute-frame prompt names an own side.

The mock is not a model, so its outcomes say nothing about behaviour.

**Cost estimate for RF-52**, calibrated on RF-40's 2,265 silent calls (`runs/rf40_round1_head_on_turn_taking`):
- **The calibration:** 0.275 tokens per prompt character, 65% of prompt tokens from the cache, and replies of 155 tokens (decision) and 144 (debrief).
- **The low end** takes a decision reply 50 tokens shorter, an assumption as in RF-47.
- **At the mock's call counts:**
  - **USD 0.26 to 0.32 off-peak per frame**, so **0.53 to 0.63 for both**;
  - about double at peak.
- RF-52 needs its own approval and cap.

## 9. Template names

*The assistant's choice*, written into the issues on 2026-11-25. The user was not asked and may change them. They are set now so that issues worked in parallel do not collide:
- `resolve_v10` (RF-46);
- `resolve_menu_v1` (RF-47), with the debrief `resolve_debrief_v3` (added in RF-47);
- `resolve_menu_abs_v1` (RF-48);
- `resolve_grid_v1` and `resolve_grid_abs_v1` (RF-51).

Each is frozen once it is built, like every template.

## 10. RF-41, and the order of work (AS8, AS9)

**AS8. RF-41 (#130) runs after RF-45, as planned** (the user, 2026-11-25). It maps RF-39's and RF-40's free-step decisions, with RF-45's hallucination flag as a column so that dubious decisions can be set aside. Menu runs can be mapped the same way later.

**AS9. The order of work, as proposed** (the user, 2026-11-25):
1. RF-42.
2. RF-43, RF-44 and RF-45 (free; in parallel).
3. RF-41 (free; after RF-45).
4. RF-46 (small, paid).
5. RF-47, then RF-48.
6. RF-49 (paid).
7. RF-50, then RF-51.
8. RF-52 (paid).

RF-50 can be built alongside RF-47 and RF-48.

*Amended by the user on 2026-11-25, after RF-45:*
- **RF-41 is dropped**, so AS8 is withdrawn. #130 is closed as not planned, before any work started, and its text keeps the design and the user's decisions of 2026-11-02. The user's reason: "I think that the issue where we try to use a discrete environment, like a grid environment instead, I think this will provide more insights".
- **The grid moves ahead:** RF-50 (#139) is next.
- RF-46 and the menu (RF-47 to RF-49) stay open, after or alongside the grid. Whether RF-51 and RF-52 also come before them is not yet decided.
- Track #55 records the same change.

*Amended by the user on 2026-11-26, after RF-50:* **RF-47 and RF-48 come before RF-51**, so that the grid's template reuses the menu and the absolute frame. RF-50 is done (#139). The order is now RF-47, RF-48, then RF-51, with RF-49 and RF-52 after their builds.

## 11. Still open

- **The way back to the continuous simulator.** The 10,000-agent goal runs ORCA plus rules in continuous space. A grid result could be read as a rule and translated (as RF-12 and RF-31 translate rules), or kept only as a check of the LLM's reasoning. To be decided with RF-52's results in hand (RF-52, task 3).
- **Whether RF-46's line on speech goes into the menu and grid templates:** after RF-46's result.
- **AS5's heading:** rechecked after RF-43.
- **The walls' names and sides (RF-48):** "the blue wall" and "the yellow wall" are the assistant's draft. In head-on, the blue wall is always on the left of the person walking +x. Whether RF-49 counterbalances this with a second template that swaps the names is the user's choice (section 7.1).
- **The placeholders, for the supervisor:**
  - "slow down a lot" × 0.5;
  - "stop and wait" 1 s;
  - "step back" 0.5 m;
  - the 30° sidestep angle;
  - the grid's N ticks for a deadlock: 10 ticks (3.0 s) as built in RF-50, round 1's window, accepted by the user on 2026-11-26 (section 8.1).

## 12. Sources

| Source | Used for | Where |
| --- | --- | --- |
| Burstedde, Klauck, Schadschneider, Zittartz 2001, "Simulation of pedestrian dynamics using a two-dimensional cellular automaton", *Physica A* 295, 507–525; arXiv cond-mat/0102397 (open access) | cell size, tick, clash rule | `refs/rf42_burstedde2001_ca_arxiv.pdf`, text `.txt` (pypdf 5.1.0), lines 132-146, 168-174, 322-324 |
| Huber et al. 2014 | "slow down a little" | `refs/rf14_huber2014_speed_path.txt:452` |
| Rapos et al. 2021, via RF-37's H1 (abstract only) | the two sidestep sizes | `configs/human_targets/head_on_v1.yaml`, H1 |
| Yamamoto et al. 2019 | shoulder width, body radius | `parameters.md`, `radius` |
| Moussaïd et al. 2009 | corridor width 1.75 m, preferred speed 1.3 m/s | `parameters.md`, `width`, `preferred_speed` |
| Nakahara et al. 2005 | backing speed 0.92 m/s | `parameters.md`, `backing_speed` |
