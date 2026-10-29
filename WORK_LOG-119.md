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

## Open questions / risks

## Summary (fill in at the end)
