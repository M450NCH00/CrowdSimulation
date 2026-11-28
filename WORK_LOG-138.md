# Work Log — Issue #138: [Experiment] RF-49: round 1 (head-on) with the action menu, in the agent's own frame and in an absolute frame, against RF-40's free steps (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/138
**Branch:** `feat/138-rf49-menu-corridor-run` (cut from `origin/feat/129-rf40-turn-taking-talk` after PR #151, RF-52, merged into it)
**Started:** 2026-11-27 06:31 UTC

## Understanding the issue
RF-49 runs round 1's head-on sessions with RF-47's menu of described actions (`resolve_menu_v1`, the
agent's own frame) and RF-48's absolute frame (`resolve_menu_abs_v1`, walls named blue and yellow) in
the continuous corridor, and compares each with RF-40's free steps, session by session. It is the test
RF-52 left open: the grid beat RF-40 (0.87 and 0.85 against 0.64), but the grid changes the world and
the action space together. RF-49 changes only the action space.

- **Decided already:** AS2, silent and talk conditions (RF-42, 2026-11-25). RF-40's cells and
  geometries, so 272 sessions per condition per arm, 1,088 in all.
- **Not decided yet (the user's):** the choices RF-47 and RF-48 flagged before this run; the cap.
- **Paid:** no paid call until `CLAUDE.md` records this issue's approval and cap.
- **Step of the track:** Step 1 (resolve), on how agents are asked to act (SV10 to SV12).

## Plan
1. Put RF-47's and RF-48's flagged choices to the user, and RF-52's open task 3, which RF-49 bears on.
2. Write RF-49's configs from `round1_head_on_menu.yaml` and `round1_head_on_menu_abs.yaml`, with tests
   that the sessions are RF-40's with only the templates (and what the user's answers change) changed.
3. Mock rehearsal of all sessions; a cost estimate from the mock's call counts and RF-40's measured
   cost per call. Ask the user for approval and a cap.
4. Once recorded: balance, prices page, fingerprint; pilot `--limit`, read the replays; the rest
   off-peak with `stop_at_cap`.
5. Analysis against RF-40, paired: the gate, dances, collisions, near misses, unreadable replies,
   `no_room` choices, RF-45's hallucination share with a hand check of 150, the factor effects, RF-37's
   passing distance, and in talk the side messages and their left and right errors.
6. Report, READMEs, `docs/action-space.md`, the balance in `CLAUDE.md`, PR into `feat/129-...`.

## Progress log

### 2026-11-27 06:31 UTC — start
- Updated track #55 for RF-52 (#141 ticked with its findings, the order paragraph, the budget at
  USD 2.62), at the user's request.
- Collected the choices flagged in `WORK_LOG-136.md` (RF-47) and `WORK_LOG-137.md` (RF-48).
- **RF-52 bears on one of them:** both agents leaned to "the yellow wall" from an aligned start in the
  grid's absolute frame. With blue always at +y, RF-49's absolute arm would confound that lean again,
  so counterbalancing the colours is now more than optional.

### 2026-11-27, about 06:33 UTC — the user's decisions
The user answered four questions (all "Recommended"):
- **RF-47's choices accepted as built:** slow-downs of the usual speed; "carry on" as `[]`; the 0.05 m
  wall margin; `resolve_debrief_v3`; the option sentences.
- **RF-48's choices accepted as built:** the blue and yellow walls; both wall distances for the
  agent; ahead/level/behind; the talk sentence.
- **Counterbalance which colour is at +y, at the same size.**
- **RF-52's task 3:** "Test bench now, RF-49 tests". The grid shapes how the continuous prompt is
  written, no grid rule is carried over, and RF-49 tells whether the gain is the menu's.
  Recorded in #141 and #138.

### 2026-11-27 06:35 to 06:52 UTC — the counterbalance and the configs (mock only)
(Times from the files and `date -u`: template 06:35, configs 06:39, tests 06:41.)
- **How to counterbalance without changing existing code.** The design's repeats are the same
  session (D14), except for who is asked first, which goes by parity (`experiment.first_asked`). So
  the absolute frame is split over two configs with `repeats: 2` each (one odd and one even repeat).
  One uses RF-48's template, the other the swapped one. The swapped config's r1 and r2 pair with
  RF-40's r3 and r4.
- **New template `resolve_menu_abs_swap_v1`** (frozen with `negsim.negotiation.freeze`) and table
  `menu_table_abs_swap_v1.yaml`, both written by script (`scratchpad/make_swap.py`). The script
  exchanges "blue" and "yellow" everywhere below RF-48's header.
  - The options and the names in each sentence follow the walls (a first), so in the swap, yellow is
    named first and is the wall positions are measured from.
  - The swap therefore separates the name from the side, but not from the order of listing or from
    being the reference wall. Flagged for the report.
- **Configs** (`scratchpad/make_configs.py`), mock client, `cap_usd: 0.00` until the approval:
  - `rf49_round1_head_on_menu.yaml`: RF-47's under its own name (544 sessions);
  - `rf49_round1_head_on_menu_abs.yaml`: RF-48's with `repeats: 2` (288);
  - `rf49_round1_head_on_menu_abs_swap.yaml`: the same with the swapped template (288).
- **A dead end, kept for the record.** The first swap config dropped the counterfactual pairs, so
  that they would run once. Checked against RF-40, 92 of its 256 sessions then met different
  people: the balanced ethnicity draw is made over the units, and the pairs are units. The pairs are
  now kept in both halves, which makes 16 sessions per condition more than RF-40's 272 (about 3%),
  and all 1,120 sessions meet RF-40's people. Flagged to the user as a small departure from "same size".
- **Tests** `tests/test_rf49_configs.py` (10), with RF-47's, RF-48's and the hygiene tests: **75 passed** (07:01 UTC):
  - the swap template and table are RF-48's with the names exchanged;
  - a session under the swap sends RF-48's prompts with the two words exchanged and carries out the
    same plans, on both geometries, in silent and talk;
  - the configs differ from RF-47's and RF-48's only as intended, and none is paid;
  - every session is RF-40's, with the same people, cell and parity.
  The first run failed only on a wrong record key (`plan`), and the prompts already matched.

### 2026-11-27 07:01 to 08:55 UTC — the rehearsal, the estimate, the approval
- **Mock rehearsals** (`runs_mock/rf49_menu`, `rf49_abs`, `rf49_abs_swap`, gitignored): 544, 288 and
  288 sessions completed, USD 0. The background job reported "failed" only because of my closing
  `tail` over several files; every log ends "completed: N session(s) run".
- **Mock calls:** own frame silent 2,359 and talk 2,531; absolute silent 1,244 + 1,291 and talk
  1,269 + 1,410. 10,104 in all.
- **RF-40's measured cost per call** (`spend_ledger.jsonl`, off-peak): silent USD 0.375 over 2,265
  calls (0.000166), talk USD 0.445 over 2,432 calls (0.000183). RF-40's real silent sessions made
  8.3 calls each; the mock makes 8.7 for RF-49's own frame.
- **Estimate:** own frame USD 0.86, absolute frame USD 0.91, **USD 1.77 in all** at RF-40's cost per
  call. It would be about USD 1.45 if a menu reply were about 50 output tokens shorter (not measured).
- **Balance:** USD 2.61 (07:34 UTC, DeepSeek's balance endpoint, the key not printed). 2.96 less RF-52's
  0.3476 is 2.6124.
- **The user approved** "Full run, cap USD 2.00 (Recommended)" for this issue only. Recorded in
  `CLAUDE.md` (Pending sign-offs, item 1, and the balance under Budget).
- **Caps:**
  - The continuous runner's resume check compares the whole config, budget included
    (`experiment._comparable` leaves out only the source), so each cap is fixed before its pilot.
  - Each experiment's cap counts only its own ledger lines, so the 2.00 is split by the estimate:
    0.95 for the own frame and 0.525 for each absolute half. The three sum to 2.00 (tested).
  - If a config stops at its cap, the rest runs under a new experiment name with what remains (as in
    #100).
- **No peak guard in the continuous runner** (RF-52's was in the grid's own entry point): I start the
  paid runs at 10:00 UTC myself.
- **DeepSeek's prices page** (fetched about 08:50 UTC) matches `configs/llm/deepseek_pricing.yaml`:
  - DeepSeek-V4.1-Flash-1017; 0.003 / 0.15 / 0.60 off-peak, double at peak;
  - peak 01:00 to 04:00 and 06:00 to 10:00 UTC, Monday to Friday;
  - the only newer note is about the search and fetch tools (not used here).

### 2026-11-27 10:00 to 10:12 UTC — the paid pilot, then the rest started
(Times from the pilot script's `date -u` lines.)
- **Pilot** (`--client deepseek --confirm --limit`, started by script at 10:00:11 UTC, off-peak):
  - 12 sessions of the own frame (USD 0.0118);
  - 8 of the absolute frame, blue at +y (USD 0.0079);
  - 8 of the swapped half (USD 0.0068);
  - **USD 0.0265** in all, done 10:09:38 UTC.
- **Model fingerprint:** `bc19ba97cbe016479903222bb1578db6` on every call (206 in the session
  records), RF-40's.
- **Unreadable replies:** 1 decision of 180. In talk, an agent put a signal in `action`: "got
  'hold_up_hand'".
- **Cost per session:** USD 0.00099 (own frame), 0.00098 (absolute), 0.00085 (swap), about USD 0.00013
  per call. RF-40's was 0.00017, so a menu reply is shorter. The full run comes to about **USD 1.07**,
  inside each config's cap.
- **Read every pilot session's choices** (`scratchpad/compact.py`):
  - **Own frame:** 10 of 12 resolved on the plans alone. The choices are almost all "to your right".
  - **Absolute frame:** 9 of 16 resolved (4 of 8 in each half). Six of the seven collisions are the
    two people choosing **the same named wall**, so both move to the same side. Every pair that chose
    different walls passed.
  - **The seventh collision is genuine, not a fault** (`S_head_on_de176842_51dfba80_r1`). Person 2
    stepped "well towards the blue wall" up to the 0.05 m margin. Person 1 held the centre with a
    large suitcase, and the corridor does not leave room (overlap 0.029 m). It is RF-40's geometry,
    so the comparison is fair.
- **Checked that the views are right** where an agent's reason looked wrong (`S_head_on_02dfbadb_cb859069_r2`):
  - Person 1 starts at y = +0.1. Its view says 0.77 m from the blue wall and 0.98 m from the yellow
    wall, as the trajectory has it.
  - It chose the yellow wall "the yellow wall side is closer". That misreads its own distances (an
    RF-45 hallucination), not the view.
- **Lean in the pilot:** both halves lean to the wall at -y (yellow in RF-48's naming, blue in the
  swap). So the lean follows the side, not the colour, but 16 sessions settle nothing.
- **The rest started at 10:12 UTC** (`scratchpad/full.sh`): the three configs one after another,
  resuming past the pilot, with an off-peak check before each. At about 20 s a session it should end
  around 16:30 UTC, long before Saturday's 01:00 UTC (and Saturday has no peak).

### 2026-11-27 10:12 to 10:19 UTC — the analysis module, while the run goes
- **New `analysis/menu.py`** (standard library, no negsim import, as the package requires) with 8
  tests in `analysis/tests/test_menu.py`. The analysis suite: **133 passed**.
- **Why a new module:** `analysis.compare` pairs by session id over first runs only. The swap's ids
  are RF-40's moved by two repeats, and the counterfactual pairs ran in both halves.
- **What it compares** [my choice, for the report]: RF-40's 256 design sessions per condition (all
  four repeats, no pairs), each once per arm. Paired by RF-40's id (McNemar). The pairs are left out
  because they ran twice in the absolute frame.
- **What it reports:**
  - the dance at the start (`sidestep_reprompt.start_kind`);
  - the walls by place and by colour, per half (Fisher's exact test on half by wall and half by
    colour);
  - first moves towards the nearer wall;
  - unreadable replies, `no_room` and `capped_by_wall` flags, and the options chosen;
  - RF-37's pass distance (the closest approach of the two centres in resolved sessions, from
    `trajectory.csv`, against H2's 0.93 ± 0.17 m);
  - walls and sides named in talk.
- **Checked on RF-40 and the pilot:** RF-40 silent resolves 163 of 256 (0.64), as its report says.
- **Already visible in RF-40:** in the 20 cm layout each person starts 10 cm to its own left. Yet
  first moves go towards the farther wall (keep right) 157 to 73 in silent. RF-40 also resolves less
  there (0.56 against 0.71 aligned).

### 2026-11-27 16:02 to 16:17 UTC — the run done; the checks, the analysis, the hand check
- **The run** (`scratchpad/full.sh`) ended at 16:02:11 UTC, exit 0, every config off-peak:
  - own frame 10:11 to 13:02, absolute (blue at +y) 13:02 to 14:32, swap 14:32 to 16:02;
  - every session completed: 544, 288 and 288;
  - spend in the ledger, pilot included: **0.4870, 0.2687, 0.2682, total USD 1.0239** against the
    one cap of USD 2.00 (per-config caps 0.95, 0.525, 0.525); 8,348 calls, all `off_peak`, no
    call error;
  - fingerprint `bc19ba97cbe016479903222bb1578db6` on every call (RF-40's);
  - unreadable decision points: own frame 3 of 2,955 (the option written as "step well to **my**
    left/right"), absolute 0 of 3,143.
- **The balance** (DeepSeek's endpoint, the key not printed) at 16:03 UTC: **USD 1.59**. 2.61 less
  1.0239 is 1.586.
- **`analysis.gate`** (0.50, each config's first repeats): own frame 63 of 128 (0.49), absolute 40
  of 128 (0.31), swap 38 of 128 (0.30): **all fail**. RF-40 passed at 123 of 192 (0.64).
  - The gate's reason text, copied from RF-40's configs, still says "192 sessions ... 3 conditions".
    The threshold is the same; only the wording is stale.
- **`analysis.menu`** over all four repeats (256 sessions per condition, paired with RF-40):

  | Arm | Silent resolved | Talk resolved |
  | --- | --- | --- |
  | RF-40 | 163 (0.64) | 150 (0.59) |
  | menu, own frame | 136 (0.53), McNemar p = 0.018 | 88 (0.34), p < 0.001 |
  | menu, absolute | 79 (0.31), p < 0.001 | 66 (0.26), p < 0.001 |
- **Why the own frame does worse:**
  - The menu makes "carry on" a first choice: a third of first plans (351 of 1,024) against 6% in
    RF-40, where 93% of first plans had a sidestep (median 0.4 m, so RF-40's steps were not bigger).
  - "Step a little" (0.47 m) is under two half-bodies (0.5 m). One person stepping a little while
    the other carries on: own silent 33 of 99 resolved, talk 31 of 116.
  - When both stepped a little to the same own side: 66 of 66 resolved (silent).
- **The absolute frame's walls:** first moves went to wall b (-y) 575 times, to wall a (+y) 156
  times, in both halves. They follow the place, not the colour: Fisher half by wall p = 0.28, by
  colour p < 0.001.
  - Wall b is the one named second and not the one the other is measured from. The design cannot
    tell these apart.
  - The lean makes both people pick the same wall: two little steps went to the same wall in 62
    sessions (2 resolved) and to different walls in 36 (34 resolved), silent.
- **The hand check:** 150 points (75 own, 75 absolute, seed 138), each read against its prompt, and
  the doubtful absolute ones against the full prompt (`scratchpad/prompt_of.py`). The judgements are
  in `hand_judgements.json`.
  - Headline: own frame **1 of 75**, absolute **8 of 75** (Fisher p = 0.034); self-contradiction 0
    and 2.
  - The absolute frame's errors are mostly about where the other is against the walls (6 category
    1), its own place (2 category 2), and a wall named for a side (2 category 3).
- **Two things found while judging, neither a hallucination:**
  - **The history's lines are cumulative** ("Since then you have moved ..." counts from that
    decision to now, as the template's comment says since `resolve_v2`). Two agents in the sample
    added them up as separate moves ("I've already shifted right twice"). The wording invites
    this. Noted, not counted.
  - **The history's sideways distance can be impossible:** "moved 1.3 m over towards the yellow
    wall" for a person pressed against the blue wall. `perceive._done` measures against the facing
    at the decision, which can be turned from the walking line. It happens on 20 of 3,591 RF-40
    points with a history and 9 of 3,858 RF-49 points (values over 1.25 m, so a lower bound).
    This predates RF-49 and does not explain the difference. Changing it would change earlier
    configs' prompts, so it is reported, not fixed.
- **RF-45's keyword coder** (`rf49_analysis/coder/`), reliable rules only: own frame 23 of 2,955,
  absolute 8 of 3,143. It reads left and right, so it cannot see the wall errors the hand check
  found.
- **`analysis.menu` gained section 9** (the two first options as a pair; the lone little step by
  layout) and the hand check's Fisher test, with 1 more test. The suite: **135 passed**.

### 2026-11-27 16:17 to 16:25 UTC — the report and the documents
- `runs/rf49_analysis/report.md`, modelled on RF-52's.
- Added in the report: the grid against the continuous menu on the same 256 silent sessions. The grid
  resolved 223 (own) and 216 (absolute), the menu 136 and 79; paired 103 to 16 and 150 to 13. So
  the grid's gains are the grid's, not the menu's: RF-52's task 3.
- RF-52's "yellow wall" lean is wall b too (`resolve_grid_abs_v1`: a blue, b yellow), so it is the
  same lean as here.
- Factor models were not run [my choice]: the gate failed, and the sessions are kept.
- Updated:
  - `README.md` (RF-49's row; RF-52's row now cites RF-49 and task 3's decision);
  - `llm_negotiation/README.md`;
  - `analysis/README.md` (`analysis.menu`);
  - `docs/action-space.md` (new section 7.2; task 3's and the colours' decisions recorded);
  - `CLAUDE.md` (balance USD 1.59);
  - `.gitignore` (RF-49's replay interaction logs, as RF-40's).

## Open questions / risks
- The swap does not separate the colour's name from its listing order or from being the reference
  wall (see above).
- 32 more sessions than "same size" (the counterfactual pairs in both halves).

## Summary (fill in at the end)
- RF-49 ran: 1,120 sessions, USD 1.024 of a USD 2.00 cap; balance USD 1.59.
- The gate fails in every config: own 0.49, absolute 0.31 and 0.30; RF-40 passed at 0.64.
- The menu does worse than RF-40's free steps in both frames, paired with RF-40:
  - silent 0.53 and 0.31 against 0.64;
  - talk 0.34 and 0.26 against 0.59.
- Causes:
  - "carry on" is a first choice for a third of agents;
  - a lone "a little" (0.47 m) does not clear two 0.5 m bodies;
  - in the absolute frame both lean to the -y wall, by place, not colour.
- Hallucinated (hand check, 75 per frame): own 0.01, absolute 0.11.
- Two older prompt issues are reported, not fixed: cumulative history lines, and an occasionally
  impossible history distance.

### 2026-11-27 16:39 UTC — PR, #55, #138
- PR #152 opened into `feat/129-rf40-turn-taking-talk`. The full negsim suite was started, then
  stopped at the user's request (they are shutting down); **the user will run it next session.**
  The PR says so.
- #55: RF-49 ticked, with the PR and findings; the "Next" paragraph updated. #138: a results comment.

### 2026-11-28 01:46 to 02:37 UTC — the full suite, one fix, the PR's Tests line
- The full negsim suite, run 01:46 to 02:33 UTC (47 min, not the 18 estimated): 2,456 passed,
  18 skipped, 2 failed. It ran in peak hours; the cap-guard test
  (`test_stop_at_cap_runs_until_the_guard_stops_it…`) passed anyway.
- Both failures: `test_ethnicity.py::test_configs_written_before_have_no_ethnicity_anywhere` on
  `rf49_round1_head_on_menu_abs_swap.yaml` and `menu_table_abs_swap_v1.yaml`, missing from its list
  of configs written after #92. The other two RF-49 configs were skipped only because their names end
  like RF-47's and RF-48's. Not an ethnicity leak: the swap config's design is RF-48's (RF-40's
  ethnicity draw, approved), and the menu table is not an experiment config.
- Fix: both added to the list (commit `c6d687883`, 02:36 UTC). `tests/test_ethnicity.py` then passed:
  63 passed, 20 skipped. The full suite was not rerun after this one-line change [my choice].
- PR #152's "Tests" line updated with these results.
