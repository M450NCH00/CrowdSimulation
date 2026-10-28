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

### 2026-10-28 09:28 UTC — config, mock rehearsal, analysis extended, cost estimate
- What I did:
  - `configs/resolution/round1_group_head_on_non_verbal.yaml`: RF-32's run of record with
    `conditions: [non_verbal]`; everything else the same except the name, description and the cap,
    which is `0.0` until the user approves one.
  - `--plan`: 72 sessions (64 of the design, 8 exact repeats), at most 16 calls a session; loose
    worst case USD 9.08 (`stop_at_cap` stops the run at the cap).
  - Mock rehearsal, all 72 sessions (`runs_mock/rf34/`, 4 min): 12 to 20 calls a session.
  - `negsim/resolution/groups.py`: `--pairs-condition`, `--against` (a paired comparison by cell and
    case, the exact sign test from RF-18's `ruleset_eval.verdicts`), `later_points` (later decision
    points, why each fired, signals, each split by friend or oncoming person); the report's heading
    names the experiment folder. Tests: `tests/test_rf34_group_non_verbal.py` (5).
- Result (mock):
  - later decision points fire in groups (signals seen, someone slowed or turned, plan failing);
  - **a friend walking abreast never sees a signal or causes a prompt** (outside the 75° view);
    a friend counts only once one falls in behind the other ("came into view": 60 of 440 later
    reasons, with 30 of 405 signal sightings by a friend). That is RF-17's view, not a choice made here;
  - the analysis pairs all 64 design sessions with RF-32's real ones by cell and case.
- **Cost estimate**: RF-30's non-verbal pairs took 7.53 calls a session against about 4 for
  independent pairs (×1.9); RF-32's independent groups took 7.02, so about 13 a session here. At
  USD 0.000121 to 0.000147 a call (RF-32's groups; RF-30's non-verbal), **USD 0.12 to 0.14**; the
  mock's own count (16.1 a session, more retries and later points than real agents) gives up to
  USD 0.20. Proposed cap **USD 0.20**; balance USD 0.56.
- **Off-peak:** DeepSeek's peak hours fall between 06:00 and 10:00 UTC on weekdays (`test_stop_at_cap`
  note, #66); the run waits for off-peak.
- Next step: ask the user to approve the paid run and its cap.

## Open questions / risks

- **Design (mine, same as RF-32's):** nothing is changed but the condition, so the run pairs with
  RF-32 session by session. The talk condition is not run.
- In non-verbal, friends abreast cannot see each other's signals (RF-17's 75° view): a group's plan
  is coordinated only through what each was told at the start ("WHO YOU ARE WITH").
- **The run still stops at the first collision**, so the later decision points are censored, as in
  RF-32; the session-level share is not affected.

## Summary (fill in at the end)
