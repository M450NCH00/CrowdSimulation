# Work Log — Issue #115: RF-34: round 1 with three or four people, non-verbal: do groups resolve a head-on when they can see each other move and signal?

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/115
**Branch:** feat/115-rf34-group-head-on-non-verbal (from `feat/110-rf32-group-head-on`, PR #114 open;
`main` is not used in this track)
**Started:** 2026-10-28, 09:06 UTC

## Understanding the issue

RF-32 (#110) ran round 1's head-on with three or four people in the independent condition only:
4 of 64 design sessions resolved in `plan_only` (0.06), against 35 of 64 (0.55) for round 1's pairs.
Every collision was with an oncoming person. In the independent condition each person decides once,
at the trigger, and never sees what anyone else then does; a group plan such as "open a gap" only
works if the oncoming person sees the gap and uses it. **The user decided on 2026-10-28**, after
RF-32, to follow it up with a non-verbal run (of the three follow-ups RF-32 listed: non-verbal, a
wider corridor for 2 v 2, extraction from group sessions).

Question: in the non-verbal condition (signals and movement, up to three decision points each, D3
and D5), do groups resolve more often than in RF-32's independent run, and near the pairs' rate
(RF-30, non-verbal: 37 of 64, 0.58)?

**Paid.** The build is mock only; the paid run needs its own approval and cap in `CLAUDE.md`
(pending item 1). Balance USD 0.56 (after #110, 2026-10-28).

## Plan

1. Config `configs/resolution/round1_group_head_on_non_verbal.yaml`: RF-32's run of record
   (`round1_group_head_on_orca_groups.yaml`) with `conditions: [non_verbal]`, nothing else changed.
2. Mock rehearsal of the 72 sessions; check later decision points in groups (why they fire) and that a
   friend abreast, outside the 75° view, neither sees signals nor triggers a prompt.
3. `--plan`, and an estimate from RF-30's non-verbal sessions and RF-32's cost per call.
4. The analysis (`negsim.resolution.groups`): round 1's pairs of one condition (`--pairs-condition`);
   a paired comparison with RF-32's independent sessions (`--against`); later decision points, why they
   fired, and signals. Tests on the mock.
5. Ask the user to approve the paid run and its cap.
6. Paid run: pilot with `--limit`, read, then the rest; analysis and `group_report.md`.

## Progress log

### 2026-10-28 09:06 UTC — issue, branch
- What I did: opened #115 and added it to #55's order after #110; branched from #110's branch.
- Found while reading: RF-30's non-verbal pairs took 7.53 calls a session (2 people), USD 0.00111 a
  session; RF-32's independent groups USD 0.000121 a call, 7.02 calls a session (from the ledger).
  `groups.py` compares with every design session of the pairs folder, whatever its condition: RF-30's
  folder holds non-verbal and talk, so it needs a filter.
- Next step: the config and the mock rehearsal.

## Open questions / risks

## Summary (fill in at the end)
