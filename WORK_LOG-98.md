# Work Log — Issue #98: [Experiment] RF-27: round 1 (head-on), tell the agents how far apart the walking lines are (resolve_v7): are the sidestep failures the model or the description? (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/98
**Branch:** feat/98-rf27-resolve-v7-walking-lines (stacked on `feat/96-viewer-decisions-factors-view-cone`,
which is stacked on RF-10's branch, as the RF issues are)
**Started:** 2026-10-25 (Sunday: off-peak all day)

## Understanding the issue
RF-10 (#65) found head-on fails the resolution gate: 59 of 192 sessions resolved in `plan_only`.
Of 116 collisions, 49 stepped towards the same wall, 40 had one or both not stepping aside, 27
made room too narrowly. The description an agent gets leaves out three things a person would
see: how far the other is from one's own line, the other's width beyond 5 m, and direction finer
than 5° ("straight ahead" hides up to 0.86 m sideways at 9.8 m). This issue builds `resolve_v7`,
which gives them, and compares it with `resolve_v6` on RF-10's independent cells.

**The user's decisions (2026-10-25, all five as recommended in the issue):** (1) say where the
other is relative to one's own line; (2) from 10 m; (3) the other's width from 10 m; (4) "straight
ahead" only within 1°; (5) the reply parser unchanged.

**Paid-run approval (2026-10-25):** the user approved paid runs for this issue only, cap USD 0.08
on `rf27_round1_head_on_v7`; recorded in `CLAUDE.md`, pending item 1.

## Plan
1. `resolve_v7.yaml`: `resolve_v6` word for word plus three view lines (`seen_short_body`,
   `seen_line_offset`, `seen_on_line`) and one setting, `direction_ahead_deg: 1`. Freeze it in
   `MANIFEST.json`.
2. `prompt.py`: render the new lines only for a template that has them, so every older template
   renders exactly as before. The offset is computed from the view itself (distance × sin of the
   bearing, from the line ahead of the agent), so it works in any scenario; given for anyone ahead
   (bearing within 90°), on the short line and in full detail.
3. Tests (`tests/test_resolve_v7.py`): v7 differs from v6 only by those keys; both sides, on the
   line, rounding, a drifting walker, someone behind (no line), the width from 10 m, the 1°
   direction, older templates unchanged, and a mock session end to end.
4. Config `configs/resolution/round1_head_on_v7.yaml`: RF-10's design, independent only, the same
   cells, geometries and exact-repeat set, `resolve_v7`; no counterfactual pairs; cap USD 0.08,
   `stop_at_cap`.
5. Mock rehearsal through `analysis.gate` and `analysis.lateral`.
6. Paid: check the balance, 6 sessions, read them, then the rest.
7. Compare with RF-10's independent sessions: resolution rate per layout, how they stepped, the
   sideways gap, stability on the exact-repeat set, unreadable rate, model string and fingerprint.
8. Report, README, CLAUDE.md balance.

## Progress log

## Open questions / risks
- Wording of the new lines is mine, within the user's decision (a); recorded below when written.

## Summary (fill in at the end)
