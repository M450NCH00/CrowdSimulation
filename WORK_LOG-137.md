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

## Open questions / risks

## Summary (fill in at the end)
