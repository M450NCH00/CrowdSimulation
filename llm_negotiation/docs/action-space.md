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

*Proposed, for RF-50 and RF-51 to settle:*
- **Moves:** forward; forward and one lane to the left or right (the paper's 3 × 3 neighbourhood includes diagonals); one lane aside in place; wait; one cell back.
- **Slower walkers:** a walker slower than 1.3 m/s advances when its walked distance reaches the next cell (deterministic, rebuildable from the seed).
- **Geometries:** round 1's "aligned" puts both in the centre lane. "20 cm apart" (±0.1 m) would round to the same lane, so the second geometry is one lane apart (0.4 m, like `apart_40cm` in `configs/cases/source_head_on.yaml`).
- **Grid measures:**
  - passed;
  - blocked face to face (the grid's collision);
  - squeezed past in adjacent lanes (the grid's near miss);
  - deadlock (no progress for N ticks);
  - the dance;
  - ticks to pass;
  - lanes apart when they pass.

  H1 and H2 apply in steps of 0.4 m, and H3 (where a turn starts) in cells. Targets on speed change apply only through "wait" and slower walkers; RF-52 says which targets apply.
- **Decision points:** event-driven as in D5, up to 6, never every tick. "Wait" lasts 1 s (about 3 ticks) and is then asked again (AS3). Between decisions, a lane change happens once, then the walker goes forward.

## 9. Template names

*The assistant's choice*, written into the issues on 2026-11-25. The user was not asked and may change them. They are set now so that issues worked in parallel do not collide:
- `resolve_v10` (RF-46);
- `resolve_menu_v1` (RF-47);
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

## 11. Still open

- **The way back to the continuous simulator.** The 10,000-agent goal runs ORCA plus rules in continuous space. A grid result could be read as a rule and translated (as RF-12 and RF-31 translate rules), or kept only as a check of the LLM's reasoning. To be decided with RF-52's results in hand (RF-52, task 3).
- **Whether RF-46's line on speech goes into the menu and grid templates:** after RF-46's result.
- **AS5's heading:** rechecked after RF-43.
- **The placeholders, for the supervisor:**
  - "slow down a lot" × 0.5;
  - "stop and wait" 1 s;
  - "step back" 0.5 m;
  - the 30° sidestep angle;
  - the grid's N ticks for a deadlock.

## 12. Sources

| Source | Used for | Where |
| --- | --- | --- |
| Burstedde, Klauck, Schadschneider, Zittartz 2001, "Simulation of pedestrian dynamics using a two-dimensional cellular automaton", *Physica A* 295, 507–525; arXiv cond-mat/0102397 (open access) | cell size, tick, clash rule | `refs/rf42_burstedde2001_ca_arxiv.pdf`, text `.txt` (pypdf 5.1.0), lines 132-146, 168-174, 322-324 |
| Huber et al. 2014 | "slow down a little" | `refs/rf14_huber2014_speed_path.txt:452` |
| Rapos et al. 2021, via RF-37's H1 (abstract only) | the two sidestep sizes | `configs/human_targets/head_on_v1.yaml`, H1 |
| Yamamoto et al. 2019 | shoulder width, body radius | `parameters.md`, `radius` |
| Moussaïd et al. 2009 | corridor width 1.75 m, preferred speed 1.3 m/s | `parameters.md`, `width`, `preferred_speed` |
| Nakahara et al. 2005 | backing speed 0.92 m/s | `parameters.md`, `backing_speed` |
