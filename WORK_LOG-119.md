# Work Log — Issue #119: RF-36: crowd encounters, non-verbal: do LLM agents resolve a conflict inside a crowd when they can see each other move and signal?

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/119
**Branch:** feat/119-rf36-crowd-encounters-non-verbal (from `feat/117-rf35-crowd-encounters`, PR #118 open,
commit `a59eeab`; `main` is not used in this track)
**Started:** 2026-10-29, 01:23 UTC

## Understanding the issue

RF-35 (#117) sampled encounters from RF-18's two-way flow and ran them in the independent condition:
against plain ORCA on the same seed, 14 of 64 design sessions resolved (0.22), worse in 50, better in 6;
the plans added collisions in 30 sessions and removed them in 2, the deep ones between the encounter's
own people walking towards each other. In the independent condition each person plans once, alone, and
never sees what the others then do. **The user decided on 2026-10-29**, after RF-35 (its open question
2), to run the same encounters in the non-verbal condition, as RF-34 did for RF-32's groups.

Question: with signals and movement, up to three decision points each (D3, D5), do crowd encounters
resolve more often than in RF-35, and do the plans still add collisions against plain ORCA?

**Paid.** The build is mock only; the paid run needs its own approval and cap in `CLAUDE.md` (pending
item 1). Balance USD 0.32 (after #117, 2026-10-28).

## Plan

1. Config `configs/resolution/rf36_crowd_encounters_non_verbal.yaml`: RF-35's config with
   `conditions: [non_verbal]`; everything else the same except the name, description and the cap,
   which is `0.0` until the user approves one.
2. Mock rehearsal of the 72 sessions; check that later decision points fire in a crowd, and why.
3. `--plan` and an estimate from RF-35's cost per call and RF-34's ratio of non-verbal to
   independent calls.
4. The analysis: `--against` paired with RF-35 by the measure against plain ORCA (the pair measure is
   0 for everyone in a crowd), and the two conditions' contacts compared directly per session (the same
   case and cell give the same bystanders and the same crowd). Tests on the mock.
5. Ask the user to approve the paid run and its cap.
6. Paid run: pilot with `--limit`, read, then the rest; analysis and `crowd_report.md`.

## Progress log

### 2026-10-29 01:23 UTC — issue, branch
- What I did: opened #119; #55 lists it after #117 as next. Branched from #117's branch.
- Found while reading: `groups --against` pairs sessions by `resolved.plan_only`, the scenario's own
  measure, which no session meets in a crowd (RF-35: 0 of 64, plain ORCA too). It needs the measure
  against plain ORCA as well.
- Next step: the config and the mock rehearsal.

### 2026-10-29 01:24 to 01:28 UTC — config; the first mock rehearsal crashed; fix
- What I did: `configs/resolution/rf36_crowd_encounters_non_verbal.yaml`, RF-35's config with
  `conditions: [non_verbal]` (and the name, description, cap 0.0, header). `--plan`: 72 sessions over the
  same 8 cases, at most 16 calls a session (RF-35: 8); loose worst case USD 48.87 (`stop_at_cap` stops a
  run at its cap whatever this says).
- **The mock rehearsal crashed on its first session** (01:25 UTC, 14 s in): `PlanDriver.schedule`, "the
  encounter has been released to ORCA; no plan can be given after it". Reproduced with a probe
  (scratchpad, not committed): members 4, 37, 33, 0; 4 and 0 both eastbound. With `orca_within_groups`
  the driver leaves pairs of one direction out of its "passed" check (`execute.py`, `_over`) and released
  the encounter at step 175 once everyone walking opposite ways had passed. But `passing_crowd` lists
  (4, 0) as a conflict pair (one behind the other, which never "passes"), so the protocol's own end check
  (`protocol.py`, `_end_reason`) kept the encounter open, and at step 176 agent 37 was due a second
  decision point (a bystander came into view, signals, its plan ended).
  - Why it never happened before: RF-34's `passing_group` lists only pairs walking opposite ways; RF-35
    had one decision point a person (the independent condition), all at the start.
- **Fix [mine]:** once the driver has released the encounter, nobody is prompted; who would have been is
  recorded as `encounter.not_prompted_after_release`, named only when someone was. A prompt after a
  release always crashed, so every earlier record and config behaves as before. The alternative,
  ending the protocol's encounter on the driver's release (or dropping one-direction pairs from its
  passed check), would change when RF-35's encounters end on a rerun; not taken.
- Next step: the mock rehearsal again (`--overwrite` does not apply to a resolution experiment, which
  resumes: a new folder, `runs_mock/rf36b/`), the analysis, tests.

### 2026-10-29 01:28 to 01:50 UTC — mock rehearsal, analysis extended, tests
- Mock rehearsal of all 72 from 01:28 UTC: all completed. In 28 of 72 someone was due after the
  driver's release and was not asked.
- `negsim/resolution/groups.py` [mine]: with `--against` a crowd experiment, `paired_crowd`: (1) paired by
  the measure against plain ORCA (both, this only, other only, neither; McNemar's exact test); (2) the
  two runs' plans compared directly (the same cell and case give the same seed, people and crowd), as
  `against_orca` scores them, and by the collision count alone; (3) a count of sessions whose plain-ORCA
  contacts differ between the two, which the pairing assumes is 0. Also `resolved_within` and the counts
  at 5 mm and 1 cm (RF-35's open question 1), beside the measure of record, not replacing it.
  Checked on RF-35's committed analysis: 14 of record, 26 at 5 mm, 34 at 1 cm, as its report counted by
  hand; RF-35 paired with itself: 64 the same, 0 differing.
- Tests: `tests/test_rf36_crowd_non_verbal.py` (7): the config is RF-35's but for the condition; the same
  72 sessions and people as RF-35; the crashing session now completes on the mock with
  `not_prompted_after_release`; RF-35's records do not name it; `paired_crowd`; `resolved_within`; RF-35's
  tolerance counts. 7 passed.
- Neighbouring suites (RF-32, RF-34, RF-35, RF-36, `test_ethnicity`, `test_repo_hygiene`,
  `test_resolution`), 01:52 to 02:13 UTC: 191 passed, 10 skipped. A first pass had one failure, the
  ethnicity check's list of configs that may name RF-30's factor template (as RF-34 and RF-35 found);
  RF-36's config added there with a note.
- **Read from the mock sessions:**
  - 10.4 calls a session (max 18), against RF-35's mock 6.8 and its paid run 6.72; 6.2 decision points a
    session, 206 of them later points (149 second, 57 third); 166 signals.
  - **Later decision points in a crowd are mostly about bystanders.** Of 655 reasons naming someone, 526
    name a bystander (`came_into_view` above all); **108 of 206 later points fired only because a
    bystander came into view.** They fire as soon as D5's 1 s gap allows: median 1.0 s after the
    trigger. That is D5 as written (anyone coming into view), not something built here. The mock's
    encounters last a median 2.8 s after the trigger; RF-35's real ones 3.55 s (2.35 to 5.7), so with a
    1 s gap the cap of 3 is reached at about the time people meet in either case.
- **Cost estimate:** RF-35's mock predicted its paid calls closely (6.8 against 6.72). At 10.4 calls a
  session and RF-35's USD 0.000146 a call, somewhat more for the longer later prompts: **about USD 0.11
  to 0.12** for 72 sessions. Proposed cap **USD 0.15**; balance USD 0.32.

### 2026-10-29 02:14 to 03:14 UTC — asked the user; the mock's replays and analysis
- Pushed the branch and commented on #119; asked the user to approve paid runs for #119 with a cap of
  USD 0.15, and whether D5's "came into view" should count bystanders in crowds (my recommendation: run
  as built, D5 unchanged). No answer yet; no paid call made.
- The mock rehearsal ended at 02:38 UTC with all 72 replays (exit 0).
- `python -m negsim.resolution.groups runs_mock/rf36b/... --against runs/rf35_crowd_encounters`, 02:38 to
  03:14 UTC, exit 0: the new tables render. **Plain ORCA's contacts are the same in all 64 pairs of
  sessions** (`plain_orca_differs` 0 at both densities), so the pairing's assumption holds: the two
  runs share each session's crowd. The mock's own scores (8 of 64 resolved) come from scripted replies
  and mean nothing about the model.

### 2026-10-29 03:47 UTC — the user's answer: run as built, paid runs approved, cap USD 0.15
- The user answered "ok run as built, do with your recommendation": D5 unchanged (a bystander coming
  into view prompts again), and paid runs for #119 only with the recommended cap of **USD 0.15**, a
  pilot first. Recorded in `CLAUDE.md`; the config's cap set. Balance checked (DeepSeek's endpoint, the
  key not printed): **USD 0.32**.
- Off-peak: DeepSeek's peak windows (`configs/llm/`) are 01:00 to 04:00 and 06:00 to 10:00 UTC on
  weekdays; the pilot waits for 04:00, and the run must end its calls before 06:00.

### 2026-10-29 04:01 to 04:13 UTC — pilot (paid): 8 sessions, USD 0.017626, off-peak; over the estimate
- `--client deepseek --confirm --limit 8` from a clean tree (commit `22ef16e`), started 04:01:03 UTC.
  Calls 04:01:16 to 04:04:52 UTC (ledger): 97 calls (71 decisions, 26 debriefs), **USD 0.017626**, all
  off-peak, no transport error. Run ended 04:11:22 with its replays.
- **Above my estimate:** 12.1 calls a session (mock 10.4) at USD 0.000182 a call (RF-35 0.000146: the
  non-verbal prompts are longer), USD 0.0022 a session: **72 sessions ≈ USD 0.159, over the cap of
  0.15.** `stop_at_cap` would stop the run near session 67 of 72.
- The sessions: 8 completed (7 passed, 1 no conflict); 65 decision points, 38 later ones, 18 of them
  only because a bystander came into view; 15 signals (all a raised hand); nobody due after a release.
  6 unreadable, all an `until` distance beyond the current one (0.9 to 1.2 m asked, the partner 0.5 to
  0.7 m away, with `distance_to_partner` on: genuine, as RF-35's 9). Debriefs: no source named, common
  sense, habit, courtesy.
- RF-36's replay interaction logs gitignored as RF-35's are, before any commit of the run.
- I stopped and asked the user whether to raise the cap (my recommendation USD 0.20), since the
  approved cap would leave the design short.

### 2026-10-29 08:48 UTC — the user: finish RF-36, under the approved cap
- The user asked what the credit was being spent on, since verification (RF-14) seemed to be the
  stage. I explained that RF-36 is Step 1 again (crowds, non-verbal), added by the user's decision,
  and that RF-14 (#69, paid: no) comes after it in #55. I recommended stopping at the pilot to keep
  the credit for rounds 2 and 3. The user answered "ok now finished RF-36": finish the run.
- No cap change was asked for, so the run goes on under the approved **USD 0.15** (the pilot's
  0.0176 included); `stop_at_cap` stops it there, near session 67 of 72 by the pilot's rate.
  Balance checked (the key not printed): **USD 0.30**.
- 08:48 UTC is peak (twice the price), so the other 64 sessions wait for 10:01 UTC (background,
  the same command without `--limit`; it resumes after the pilot's 8).

### 2026-10-29 10:01 to 11:14 UTC — the run (paid): stopped at the cap, 66 of 72 sessions
- Started 10:01:03 UTC; calls until 10:36:30 UTC (ledger); the run ended 11:13:14 UTC with its replays,
  exit 3: `stop_at_cap` refused a call in session 67 (USD 0.147095 recorded, that call up to
  USD 0.003215, cap 0.15), as the pilot projected.
- **RF-36 in all: 844 calls (628 decisions, 216 debriefs), USD 0.147095**, all off-peak, no transport
  error. Balance checked (the key not printed): **USD 0.17** (0.30 before the run). Recorded in
  `CLAUDE.md`.
- **66 sessions completed**: 60 of the 64 design sessions, and 6 of the 8 exact repeats. Not run:
  design sessions 67 to 70 (67 aborted after 13 calls, its cost in the ledger, no record), and the two
  last exact repeats (71, 72). The pairing with RF-35 skips a session without a partner, so the
  comparison is over 60 pairs.
- Analysis started 11:14 UTC: `python -m negsim.resolution.groups runs/rf36_crowd_encounters_non_verbal
  --pairs runs/rf30_round1_head_on_keep_line --pairs-condition non_verbal --against
  runs/rf35_crowd_encounters` (round 1's pairs of the same condition, as RF-34).

### 2026-10-29 11:14 to 11:42 UTC — analysis, report, commit
- Analysis 11:14:40 to 11:39:03 UTC, exit 0. **Plain ORCA's contacts identical in all 60 pairs.**
- **Result: no better, somewhat worse.** Against plain ORCA, 9 of 60 resolved against RF-35's 13 on the
  same 60 (paired: both 8, RF-36 only 1, RF-35 only 5, p = 0.22). Plans compared directly: worse than
  RF-35's in 30, the same in 22, better in 8 (p < 0.001). Collisions 487 against RF-35's 373 and plain
  ORCA's 321; more than plain ORCA in 39 sessions, fewer in none. At 5 mm and 1 cm tolerances 14 and 21
  (RF-35, same 60: 23 and 31).
- Who collides (a scratch script, checked to reproduce RF-35's committed table exactly): the deep
  contact between prompted people walking towards each other is unchanged (72 against 70, median
  13.8 mm); grazes with bystanders walking the same way tripled (114 against 38, median 0.4 mm).
- 55 of 60 design sessions had later decision points, 310 in all, **181 fired only by a bystander
  coming into view**; 127 raised hands. 61 of 549 decision points unreadable (56 a distance beyond the
  current one, genuine).
- One exact-repeat set differed between copies (better, then worse: 0.36 against 0.91 mm), unlike
  RF-35's.
- `runs/rf36_crowd_encounters_non_verbal/crowd_report.md`; README row; committed with the run folder
  (interaction logs ignored, 6.1 MB) and the ledger (`425cd70`).
- Full suite 11:43:03 to 12:12:41 UTC: **2222 passed, 10 skipped**.

## Open questions / risks

1. The 6 sessions not run (4 design at 50 per way, 2 exact repeats): about USD 0.013 at this run's
   rate, a new cap needed. With 5 against 1 in the paired comparison and 30 worse against 8 better,
   4 more pairs would not change the conclusion. My recommendation: keep the 60 and spend the credit on
   rounds 2 and 3.
2. Should D5 count only the encounter's own people in a crowd? 181 of 310 later decision points were
   about strangers. A design decision for the user; not tested here.
3. RF-35's questions 1 (a depth tolerance) and 3 (strangers walking the same way treated as a group)
   still apply.
4. Balance USD 0.17. The plan prices a lean round at USD 0.10 to 0.20, so rounds 2 and 3 do not both
   fit without a top-up. RF-14 (#69, next) makes no paid call.

## Summary (fill in at the end)

RF-36 ran RF-35's crowd encounters in the non-verbal condition (the user's decision of 2026-10-29). Built:
no prompt after the driver's release (a bug a same-way conflict pair exposed on the mock), and
`paired_crowd` and `resolved_within` in `groups.py`, with 7 tests. Paid run, approved for this issue
only with a cap of USD 0.15: USD 0.1471, all off-peak, stopped at the cap with 66 of 72 sessions (60 of
64 design). **Non-verbal does not help in a crowd**: 9 of 60 resolved against plain ORCA, against
RF-35's 13 on the same sessions; the plans are worse than RF-35's in 30 sessions and better in 8. The
deep contact between the prompted people is unchanged; the extra is sub-millimetre grazing with
bystanders walking the same way, and most later decision points are triggered by bystanders coming
into view (D5 as written). Balance USD 0.17. Next in #55: RF-14 (#69), verification, no paid call.
