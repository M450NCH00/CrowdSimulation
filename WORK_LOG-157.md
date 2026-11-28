# Work Log — Issue #157: RF-55, which half of resolve_v11 helped? Only "they have moved over" on short lines: resolve_v12 on RF-40's silent sessions

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/157
**Branch:** feat/157-rf55-short-moved (cut from `origin/main` at b789c7129, PR #156's merge)
**Started:** 2026-11-28 12:55 UTC

## Understanding the issue
RF-54 (#155) raised the resolved share of RF-40's 256 silent design sessions from 163 to 191
(McNemar p = 0.009). Its template, `resolve_v11`, changed two things at once: on short lines (5 to
10 m) it says that the other moved at all, which `resolve_v9` left out, and at every distance it adds
the gap numbers and "both moved over". RF-55 adds only the first, in `resolve_v9`'s own words, to tell
the two apart.

Decided by the user on 2026-11-28: run the separation test next (after merging PR #156), before RF-46.
The approval and cap are asked for after the mock rehearsal.

## Plan
1. Template `resolve_v12`: `resolve_v9` word for word, plus a short-line key that prints `resolve_v9`'s
   "Since you last looked, they have moved over to your {side}." (only the move over). Freeze it.
2. `prompt.py`: print it on short lines only when the template has the key; earlier templates are
   unchanged (tested).
3. Tests: earlier templates unchanged; decision 1 unchanged; a sidestep then walking on, seen from
   5 to 10 m, prints the line; slowed down and turned are not printed on short lines.
4. Config `configs/resolution/rf55_round1_head_on_short_moved.yaml` (RF-40's silent sessions, only the
   template changed), with a test.
5. Mock rehearsal, cost estimate, then ask the user for the cap.

## Progress log

## Open questions / risks

## Summary (fill in at the end)
