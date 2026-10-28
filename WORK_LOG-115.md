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

### 2026-10-28, about 09:30 UTC — the user's answer: paid runs approved, cap USD 0.20
- The user approved paid runs for #115 only, **cap USD 0.20** (the proposed cap). Recorded in
  `CLAUDE.md`; the config's cap set. Balance checked: **USD 0.56** (DeepSeek's endpoint).
- The neighbouring suites (`test_rf32_group`, `test_ethnicity`, `test_repo_hygiene`,
  `test_resolution`): 158 passed, 10 skipped, 1 failed: the ethnicity check's list of configs that may
  name RF-30's factor template (as RF-32 found). RF-34's config added with a note; it passes.

### 2026-10-28 10:01 UTC — pilot (paid): 8 sessions, USD 0.0186, off-peak
- What I did: waited for off-peak (10:00 UTC), then `--client deepseek --confirm --limit 8`. Calls
  10:01:15 to 10:04:41 UTC (ledger): 119 calls, USD 0.018599, all off-peak, no transport error.
- Result:
  - **USD 0.0023 a session**, above my estimate (14.9 calls a session, USD 0.000156 a call):
    72 sessions ≈ USD 0.17, inside the cap.
  - Plans are rich and use the condition: people open a gap, fall into single file, give way to the
    cane, raise a hand (3 signals, all seen by the oncoming people, one also by a friend behind).
    Live: 2 of 8 passed; `plan_only`: 1 of 7 design sessions resolved.
  - Each person's three decision points are mostly used by about 4.4 s (one a second, D5's
    `min_gap_s`, someone always turning or slowing); the meetings come at about 6 s. As in RF-30's
    pairs; noted, not changed.
  - **Problem found: 5 of 83 decision points lost to a check that measured to the wrong person.**
    6 replies were unreadable after their retry; 5 were refused as `start`/`until` `at_distance_m`
    "beyond current": "2.5 m, but the other is 0.7 m away". In every one the nearest person in view
    was the friend ahead (0.50 to 0.67 m, after one fell in behind), no time-to-meet line was shown,
    and the partner, the oncoming person the executor measures `at_distance_m` to
    (`execute.py`, `_within`), was 5 to 7 m away. The reply check reads `View.meeting_distance_m()`:
    the time-to-meet person, else **the nearest person in view**. With two people both are the same
    person; in RF-32 (independent) every prompt came at the trigger, before anyone fell behind. So
    this is new with groups and later decision points. (The sixth: `start: "other_passes"`, as RF-32.)
  - `groups.py` crashed without `--pairs` (the report formatted round 1's missing interval); fixed.
- I stopped the paid run and asked the user, since the fix changes what is measured.

### 2026-10-28, between 10:07 and 11:01 UTC — the user's decision: fix, and run all 72 again
(The question was asked at 10:07; the clock read 11:01 after the build, the mock rehearsal and the tests below.)
- The user chose "Fix, rerun all 72" (of: the same with the cap raised to USD 0.25; run as built).
- Built: `protocol.distance_to_partner` (off by default, named in a record only when on, so every
  earlier record replays as before; replays never re-check distances, `execute.py` reads them back
  with an unbounded distance). When on, the reply check's distance is the centre-to-centre distance
  to the plan's partner, as the executor's `_within` measures it; the view's distance once the partner
  has arrived. Documented in `docs/encounter-protocol.md`.
- A refused reply changes what happens next (the agent carries on with its old plan, and others see
  that), so unlike RF-32's pilot this one **cannot be re-executed**: all 72 sessions run again under the
  new config `round1_group_head_on_non_verbal_partner.yaml` (experiment
  `rf34_round1_group_head_on_non_verbal_partner`, cap USD 0.1814 = 0.20 − the pilot's 0.018599). The
  pilot's config and folder (`runs/rf34_round1_group_head_on_non_verbal`) stay as built, the config
  marked as the pilot's.
- Tests: the new config is the pilot's but for the setting; the default and checks; a mock session
  where person 0 falls in behind their friend, then answers "until 3 m" with no time-to-meet line
  (forced): refused with the setting off, as in the pilot, accepted with it on.
- Mock rehearsal of the new config, all 72 sessions (`runs_mock/rf34p/`); every record names
  `distance_to_partner: true`.
- `groups.py`: the report no longer crashes without `--pairs`.

### 2026-10-28 11:02 UTC — the paid run of record, all 72 sessions (off-peak)
- From a clean tree (commit `5ef775d`). Calls 11:02:17 to 11:29:42 UTC (ledger), run ended 11:32:45
  with its replays. 990 calls, **USD 0.150197**, all off-peak, no transport error.
- #115's spend: USD 0.168796 of the USD 0.20 cap. Balance after: **USD 0.39** (0.56 before).

### 2026-10-28, about 11:35 UTC — the analysis and the report
- `python -m negsim.resolution.groups ... --pairs runs/rf30_round1_head_on_keep_line --pairs-condition
  non_verbal --against runs/rf32_round1_group_head_on_orca_groups`, RF-32's six arms.
- Result (`runs/rf34_round1_group_head_on_non_verbal_partner/group_report.md`):
  - **9 of 64 design sessions resolved in `plan_only` (0.14, CI 0.08 to 0.25)**, against RF-32's 4 of 64
    and RF-30's non-verbal pairs' 37 of 64 (Fisher p < 0.0001). Paired with RF-32: 9 here only, 4 there
    only, **none in both**, 51 neither (sign test p = 0.27).
  - 58 collisions, all with an oncoming person (60 collision events, none between friends), 6.0 to 7.7 s.
  - Resolved conflict pairs 37 (RF-32: 21): right to right 20, left to left 4; single file passed cleanly
    11 of 14 (RF-32: 2 of 8).
  - 48 signals (nods, raised hands); decision points: 2.85 a person, the last at 4.4 s (median), the
    first collision 1.7 s after it; RF-30's pairs also 4.4 s.
  - No distance refusal (unreadable 10 of 722: 8 `start` written as an event, 2 unknown `until`).
  - Rules: as RF-32 (left turn resolves 64 of 64 under ORCA; no rule reproduces the agents).
  - Holds ground and did not slow: 15 of 32 (RF-32: 20 of 32).
- Checked before writing: every number against `analysis/group_summary.json`, `group_sessions.json`,
  the replays' `events.jsonl` (collision partners) and the ledger; one sentence about why first plans
  lean right reworded, since the run cannot tell its cause.
- `CLAUDE.md` (balance), `README.md` (RF-34's row).

## Open questions / risks

- **Design (mine, same as RF-32's):** nothing is changed but the condition, so the run pairs with
  RF-32 session by session. The talk condition is not run.
- In non-verbal, friends abreast cannot see each other's signals (RF-17's 75° view): a group's plan
  is coordinated only through what each was told at the start ("WHO YOU ARE WITH").
- **The run still stops at the first collision**, so the later decision points are censored, as in
  RF-32; the session-level share is not affected.

## Summary (fill in at the end)
