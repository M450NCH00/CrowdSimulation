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

## Open questions / risks

## Summary (fill in at the end)
