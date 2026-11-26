# Work Log — Issue #136: RF-47: a menu of described actions, with amounts in words instead of angles and metres: resolve_menu_v1 (mock only)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/136
**Branch:** feat/136-rf47-menu-of-actions (cut from `origin/feat/129-rf40-turn-taking-talk` after PR #147 merged into it)
**Started:** 2026-11-26 03:18 UTC (from `date -u`)

## Understanding the issue
The supervisor's points 4 and 5 (November 2026): let the agent choose one described action from a
menu, with amounts in words, instead of writing a speed in m/s, a turn in degrees and a sidestep in
metres. Code turns each option into the existing step format, so the executor (`keep_line_replan`),
the replay, `code_plan` and the analyses are reused unchanged. Mock only: no paid call (RF-49 runs it).

Fixed before this issue (RF-42, `llm_negotiation/docs/action-space.md`):
- **AS3:** the menu and its amounts (section 6): carry on; slow down a little (speed × 0.81, Huber
  2014); slow down a lot (× 0.5, placeholder); stop and wait (1 s, then asked again, placeholder);
  step a little left/right (0.47 m, half of H1); step well left/right (0.93 m, H1, or as far as the
  wall allows, about 0.6 m from an aligned start); step back (0.5 m, placeholder, at the backing speed).
  A sidestep moves aside at 30° (`resolve_v8`'s placeholder) and then walks on parallel.
- **AS4:** the menu extends the existing parser and protocol behind a template flag; every earlier
  template and config behaves exactly as before (tested).
- **AS2:** build silent and talk; RF-49 runs both.
- Section 3: new runs keep RF-40's design (cells, people, `keep_line_replan`, 6 decision points,
  `turn_taking` with `always_heard` in talk, `resolve_debrief_v2`).

**Why now (the user's order of 2026-11-26):** after RF-50, the user chose to do RF-47 and RF-48
before RF-51, so that the grid's template reuses the menu and the absolute frame. Answers given in
the same question, for later issues (recorded here and in `docs/action-space.md`):
- **AS5 revised:** the absolute frame uses **neutral landmark names** for the walls (RF-43's
  recommendation, `literature/frames-of-reference/README.md` section 6, item 3), not compass names.
  For RF-48 and RF-51.
- **The grid's menu is AS3's menu done in cells** (RF-51).
- **RF-51 counterbalances** who starts off the centre lane in `one_lane_apart`.

## Plan
1. `negsim/resolution/menu.py` (new): the menu table (option → plan in the step format), loaded
   from a config file, and the conversion of a chosen option into steps, given the agent's usual
   speed and the room to each wall (from `avoidance.perception.environment_features`).
2. `configs/resolution/menu_table_v1.yaml` (new): AS3's numbers, tagged.
3. `reply.py`: under a template with a menu, a reply has `action` (one option's name) in place of
   `steps`; an unknown option is unreadable (one retry, as now); the steps are built by the menu.
   `ParsedReply` gains `action`, written to the record only when set. `ReplyContext` gains the menu
   and what the conversion needs, all defaulting to "no menu".
4. `prompt.py`: `CoreTemplate.menu`; the ACTIONS block of the fixed text. `protocol.py`: pass the
   menu context when the core template has one.
5. Templates (frozen, in MANIFEST): `resolve_menu_v1` (resolve_v9 with the menu in place of the
   step format, all four sections), and, if needed, a debrief that names the chosen option rather
   than its numbers.
6. Mock policy `resolution_menu_rehearsal_v1` (every option, an unknown option, an unreadable reply,
   signals, a talk message).
7. Tests: each option's movement in `plan_only`; unknown option unreadable; the wall cap; earlier
   templates and RF-40's config unchanged.
8. Config `round1_head_on_menu.yaml`: RF-40's sessions, silent and talk, only the template changed.
   Mock rehearsal, cost estimate.
9. Docs: `docs/action-space.md` section, README rows.

## Progress log

### 2026-11-26 03:21 UTC — branch, reading
- What I did: cut the branch; read the issue, `docs/action-space.md`, `reply.py`, `prompt.py`,
  `protocol.py` (`_ask`, `_apply`, `_record`, `code_plan`), `execute.py`'s docstring, `mock.py`,
  `resolve_v9`, `resolve_debrief_v2`, RF-40's config and tests.
- Found:
  - `[]` already means "carry on as you are" in `resolve_v9` and the executor: keep the line (under
    `keep_line_replan`) at the usual speed. The menu's "carry on" is the same plan, so a choice of
    it is exactly A's `[]`.
  - The perception record already measures the free width to each wall across the agent's path
    (`environment_features`): the wall cap is that width minus the body radius.
  - `CoreTemplate` needs sections for independent, non-verbal and talk, so non-verbal comes free.
  - The debrief prints each decision's steps as JSON; under the menu that would show the agent
    numbers it never wrote.

### 2026-11-26 03:35 UTC — the build
- What I did:
  - `negsim/resolution/menu.py` (new): the table, name matching, the conversion to steps, the
    wall cap, and `menu_context` (usual speed, radius, room to each wall from `environment_features`);
  - `reply.py`: under a menu, `action` in place of `steps` (`missing_action`, `unknown_action`,
    `steps_ignored`); `ParsedReply.action`, written only when set; `ReplyContext` gains the menu
    fields, all defaulting to "no menu";
  - `prompt.py`: `CoreTemplate.menu` (the template's options must equal the table's, in order) and
    the ACTIONS block; `DebriefTemplate.text` lists a menu decision by its option when the
    template has an `action` line;
  - `protocol.py`: three lines, which pass the menu context when the core template has one;
  - templates `resolve_menu_v1` (resolve_v9's view line for line, except the three history outcomes)
    and `resolve_debrief_v3`, frozen; `configs/resolution/menu_table_v1.yaml`; the mock policy
    `resolution_menu_rehearsal_v1`; the config `round1_head_on_menu.yaml` (RF-40's, silent and
    talk, core and debrief templates and the mock policy changed, `cap_usd: 0.00`).
- **Choices of mine, flagged for the user** (none is in AS3 as written):
  - **the slow-downs are of the agent's usual speed**, not its current one, until `other_passes`.
    Huber's 0.81 compares two walking speeds (instructed slow against normal), so the usual speed
    is its base. A slowed agent that chooses "slow down a little" again is not slowed further;
  - **"carry on" is `[]`**: keep the line at the usual speed, as in `resolve_v9`. An agent standing
    after "stop and wait" walks on if it chooses "carry on";
  - **a 0.05 m wall margin** on the cap: without it ORCA's own wall margin could stop a sidestep
    short of its distance, and a sidestep with no `until` would never end. The cap from an
    aligned start is then 0.57 m (AS3: "about 0.6 m"). Tested: the step ends `sidestepped`;
  - **`resolve_debrief_v3`** in place of section 3's `resolve_debrief_v2`, so that the debrief
    names the option and not numbers the agent never saw. One line differs;
  - **the option sentences** are my wording. "Stop and wait" and "step back" first ended "unless
    you are asked again first". The test that no option says who goes first caught the word
    "first", so before any use it became "unless you are asked again" (the template was re-hashed).
    The first rehearsal used the old wording, so it was stopped and run again in a new folder,
    `runs_mock/rf47_rehearsal`.
- Scratch sessions: every option gives its plan in `plan_only`, and every sidestep, capped or not,
  ends `sidestepped`.

### 2026-11-26 04:13 UTC — tests, the full suite, the rehearsal, the cost
- `tests/test_rf47_menu.py`: 27 tests (the table, refusals, name matching, each option's plan,
  usual speed, unknown and missing action, steps ignored, signals by condition, the wall cap, an
  event the scenario lacks, earlier templates and records unchanged, the debrief, the template
  against v9, no number or "first" in ACTIONS, each option's movement in a session, the retry,
  the config against RF-40's, the mock).
- Enumeration tests updated with a note: `test_resolution.py`'s mock policy names, and
  `test_ethnicity.py`'s list of configs written before #92 (the new config, and the table, which is
  not an experiment config).
- **The full suite** (03:37 to 04:09 UTC): 2388 passed, 12 skipped, 3 failed. Two failures were
  the `test_ethnicity` enumeration above, and they pass after the update. The third,
  `test_stop_at_cap_...`, is the known peak-hours failure; rerun at 04:11 UTC, off-peak, it passed.
- **The mock rehearsal**, RF-40's 544 sessions, silent and talk: all completed; 3,458 decision
  points; every option was chosen; 386 sidesteps capped by the wall, 112 with no room; 168 replies
  unreadable after the retry (`unknown_action`).
- **Cost estimate for RF-49** (from `spend_ledger.jsonl`, RF-40, off-peak):
  - silent USD 0.375 and talk USD 0.445, so USD 0.82 for 544 sessions;
  - the fixed text is shorter, but it is the cached prefix (about USD 0.003 per million tokens), so
    that saves nothing;
  - assuming 50 fewer output tokens a decision (not measured), the total is **USD 0.71 to 0.82**
    per frame at RF-40's call counts, or about USD 1.4 to 1.6 for both of RF-49's frames.

## Open questions / risks
1. **For the user, before RF-49's paid run:** the four choices above (the slow-downs' base speed,
   "carry on" as `[]`, the 0.05 m wall margin, `resolve_debrief_v3`) and the option sentences.
2. **The menu has no "speed up" and no "walk on again" apart from "carry on".** That is AS3 as
   decided. "Carry on" from standing still means walking on.
3. **An agent can choose a sidestep with no room** (112 times in the mock, which ignores what it is
   told). The plan is then `[]`, flagged (`no_room:<side>`), and the agent is not told that the
   step did not happen, except through its history next time ("you have not moved over to either
   side"). Its view already gives the distance to each wall (`scenario_passing_v1`, WHERE YOU ARE:
   "The wall on your left is {left} m from you"). In RF-49, count `no_room` as a possible
   hallucination (RF-45's "chose something not possible").
4. **The cost estimate assumes RF-40's call counts.** The menu may change how often agents are asked
   again, for example after each 1 s wait.

## Summary (fill in at the end)
