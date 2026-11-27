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

## Open questions / risks
- The flagged choices and the cap (above).

## Summary (fill in at the end)
