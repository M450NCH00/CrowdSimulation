# Work Log — Issue #65: [Experiment] RF-10: round 1 (head-on), Phase A screening of up to 16 factors (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/65
**Branch:** feat/65-rf10-round1-head-on-screening (stacked on `feat/92-real-ethnicity-factor`, as the
earlier RF issues are; `origin/main` is still at PR #3)
**Started:** 2026-10-24 22:10 (Singapore time; 14:10 UTC)

## Understanding the issue
Round 1 of track #55 (head-on in a corridor, full depth): a paid Phase A screen of up to 16
factors on `wide_corridor_head_on`, in all three conditions, to answer Step 1 (can LLM agents
resolve the conflict, and does signalling or talking help?) and to shortlist 3 to 5 factors for
Phase B. The resolution gate (the `plan_only` rate below which head-on counts as not resolved by the
LLM) must be fixed in the config before the run.

**What blocks the paid run.** `CLAUDE.md` records approval of paid runs for #64 only (pending item
1). The ethics sign-offs for perceived attractiveness and real ethnicity are recorded (items 2 and
3). So everything up to the paid step can be built and rehearsed on the mock; the paid run waits
for a dated approval and cap for #65 in `CLAUDE.md`.

## Decisions the user delegated (2026-10-24)
Before starting I gave the user the list of what needed approving and a cost estimate. The user
replied "just go for what you decide for 3a to 3c". So the following are **my decisions, on the
user's delegation**, not the supervisor's:

- **3a. RF-9's three fixes, all adopted**, in a new frozen core template `resolve_v6` and a new
  protocol setting (old templates and configs behave exactly as before):
  1. an `until` written as an object: an event as `{"other_passes": ...}` is read as the event,
     and `{"at_distance_m": x}` becomes a real `until` (the step ends when the person met is that
     close), written into the step format. RF-9: `unknown_until` was 58 of 63 unreadable sends;
     the two forms are what the model wrote.
  2. a heading 10° to 45° off opposite (or off the same direction) is described as "towards you,
     drifting to your left by N°" rather than "walking across your direction of travel". RF-9: 28
     of 30 agents given the old wording reasoned about a crossing.
  3. the encounter does not end on `no_conflict` while a member's plan is still waiting or running.
     RF-9: 3 of 16 `no_conflict` sessions collided afterwards, with nobody prompted again.
- **3b. The design is the issue's (Option A)**: 32 cells × 2 geometries × 3 conditions, the
  exact-repeat set, and counterfactual pairs; about 276 sessions, about USD 0.24 off-peak. I told
  the user it is underpowered for 16 factors by RF-9's rule (10 events of the rarer outcome per
  term needs about 790 sessions); the counterfactual pairs and Phase B (RF-13) are the backup.
- **3c. The resolution gate: 0.50** pooled `plan_only` resolution rate (see the plan below).
- **3d.** Temperature stays at 1.0 (not delegated; unchanged).

## Cost estimate given to the user (before any work)
From RF-9's 72 paid sessions (`runs/rf_pilot_v2/cost.json`, all off-peak, retries included):
independent USD 0.00046, non-verbal 0.00104, talk 0.00107 a session on average (90th percentile
0.00049, 0.00123, 0.00120). With the factor lines (about +2 to 3%): about USD 0.00088 a session
off-peak, double at peak. Option A (about 276 sessions): about USD 0.24 off-peak, 0.49 at peak;
suggested cap USD 0.35 with `budget.over_cap: stop_at_cap`. Option B (sized to RF-9's noise rule,
about 790 sessions): about USD 0.70 off-peak. Balance USD 1.41 (2026-10-24).

## Plan
1. Fix 1 (`until` forms): `Until.at_distance_m`; parser flags from the template
   (`until_at_distance`, `until_event_as_object`); the executor ends a step at a distance;
   `steps_from_dicts` reads the new form back for replays. Tests.
2. Fix 2 (drift wording): heading phrases `towards_drifting` and `same_drifting` in the
   resolution prompt only (the rulegen `_heading` is shared and unchanged). Tests.
3. Fix 3 (`no_conflict`): `protocol.no_conflict_waits_for_plans` (default false; described only
   when true). Tests.
4. Freeze `resolve_v6` (resolve_v5 + the step-format change + the drift phrases + the flags) in
   the manifest. Tests that pin it against v5.
5. The resolution gate as a config key, recorded and printed by `--plan`; the analysis applies it.
6. `configs/resolution/round1_head_on_screening.yaml`: 16 factors, 32 cells, 2 geometries, three
   conditions, exact-repeat set, counterfactual pairs (one ethnicity_pair flip, two p2_ethnicity
   flips), `resolve_v6`, `as_prompted`, the gate, reply cap 300, `stop_at_cap`, client mock until
   approval. Rehearse it on the mock end to end; `--plan` for sessions per group pair and preview.
7. Full test suite. Commit, push.
8. **Stop before the paid run** until `CLAUDE.md` records the approval and cap for #65. Then:
   balance check, `--limit` batch, read transcripts, the rest off-peak; analysis (tasks 5 to 8).

## Progress log

### 2026-10-24 22:10 — Start
- What I did: read #55, #65, `WORK_LOG-64.md` (findings, recommendation), the pilot's cost record
  and report; read the reply parser, executor, protocol and prompt code for the three fixes.
- Result: the three fixes each fit an existing gating pattern (template flag like
  `later_step_start`; protocol setting like `execution`), so old configs stay byte-identical.
- Next step: fix 1.

### 2026-10-24 22:15 to 23:00 — The three fixes, resolve_v6, the gate (commit 714ccc9)
- **The pilot's unreadable `until`s**, tallied from `runs/rf_pilot*`: the event as an object with
  every kind of value (`true`, `"other_passes"`, `""`, `null`, `1`), and `{"at_distance_m": 2.0}`
  (also 2.5, 3, and 0 twice). So fix 1 accepts both forms: `{event: anything but false}` is read
  as the event and flagged `until_event_as_object`; `{"at_distance_m": d}` is a real `until`,
  checked as a start at a distance is (positive, someone in view, no further than now; the start's
  checks moved into a shared `_at_distance`, its failure codes unchanged, tested). The executor
  ends such a step with `ended_by: at_distance`. `steps_from_dicts` reads it back, so a replay
  rebuilds the run. Gated by two template flags, as `later_step_start` was.
- **The drift (fix 2).** `negsim.rulegen.describe._heading` is shared with the rule-generation
  layer, so it is untouched: `prompt._walking_heading` uses the new phrases only when the template
  has them. Someone standing still keeps the old words ("facing ... drifting" would mean nothing).
  **Changed my mind on the wording** before freezing: RF-9 suggested "coming towards you, drifting
  to your left", but "towards you" is false for someone behind the agent walking the other way,
  and the clause after it already says whether the distance shrinks. The phrase is "in the
  opposite direction to you, drifting to your left by 15°". The 45° band is a placeholder
  (`docs/parameters.md`, 8.2).
- **`no_conflict` (fix 3).** RF-9's 3 collisions: `no_conflict` ended the encounter while a step
  back to the old line was still to run, and the replay then carried it out with nobody asked
  again. `protocol.no_conflict_waits_for_plans` (default false, described only when true) keeps
  the encounter open while any member's plan waits or runs. On a head-on step-aside-and-back plan
  the encounter now ends `passed` at 6.6 s with 4 decision points, against `no_conflict` at 4.2 s
  with 2 (a test).
- **`resolve_v6`** frozen in the manifest (sha256 b3b89563…). It is `resolve_v5` but for the
  `until` sentence, two headings and two flags; a test pins every other key against v5.
- **The gate** is an optional config block `resolution_gate` (rate and reason, both required),
  recorded in `config.json` only when set and printed by `--plan`.
- A slip: a stray `cat > "$TMPDIR/freeze_v6.py"` in a shell line waited on stdin and left an
  empty file `C:\Users\chooz\AppData\Local\Temp\freeze_v6.py` (outside the repo; harmless). The
  manifest was written by a script in the scratchpad instead.
- Tests: `tests/test_resolve_v6.py`, 29 passed; with `test_repo_hygiene.py` (which now lists
  `test_execute` as a local module), 34 passed.

### 2026-10-24 23:00 — The screen's config (commit 8616db3)
- `configs/resolution/round1_head_on_screening.yaml`, experiment `rf10_round1_head_on`. `--plan`:
  **288 sessions**, 96 per condition: 64 of the design, 16 exact repeats and 16 in pairs each.
  My estimate to the user said about 276: I counted the pairs as 36 sessions, but each pair is
  2 sessions × 2 geometries × 3 conditions = 12, so 4 pairs are 48. At USD 0.00088 a session that
  is **about USD 0.25 off-peak** (0.51 at peak); the proposed cap of USD 0.35 still leaves about 38%
  headroom.
- **The fourth counterfactual pair** flips `attractiveness_0_sees_1` (person 1 told it finds person
  2 attractive) rather than urgency: attractiveness is the bias factor the user put in the screen
  beside ethnicity, and a pair tests it directly. The other three are RF-26's ethnicity flips.
- 16 factors in 32 cells is the saturated resolution IV design: every slot used, as the issue
  asks. Ethnicity per pair of groups, drawn balanced: from 6 (chinese/others) to 42 (malay/malay)
  sessions; persons drawn 20% to 28% per group (the `--plan` table).
- Worst-case preview USD 17.63; `stop_at_cap` lets a confirmed run start and stops it at the cap.

### 2026-10-24 23:30 — The gate in the analysis, and the mock rehearsal (commit 5c3f783)
- `analysis/gate.py` (`python -m analysis.gate <experiment folder>`) applies the gate with the
  threshold read from the run's `config.json`, never from the command line, so it cannot be moved
  after the results are seen. 4 tests (`analysis/tests/test_gate.py`).
- **Mock rehearsal of the whole screen** (`runs_mock/rf10/`, git-ignored): 288 of 288 sessions
  completed, no error. The gate counts exactly the design's 192 (168 plain first runs plus the
  first runs of the 24 exact-repeat sessions marked `repeat` 1); the mock "fails" it at 22 of 192,
  which says nothing about a model (the mock's replies are scripted). RF-8's
  `python -m analysis` runs end to end on it, with the ethnicity tables.
- **Separation, as #55 warned:** on the mock, 17 of 60 models are separated (no finite estimate),
  5 have no data. This is about the mock's scripted outcomes, but the real screen has 16 factors
  on about 46 resolved sessions (at RF-9's 0.24), so it will happen there too. Not one of the
  decisions the user delegated: open question 4 below.
- **The Holm family is fixed now, before the run:** the whole report, RF-8's default (RF-8: on 20
  no-effect synthetic screens it gave 0 false positives, against 17 for a family of one model).

### 2026-10-25 00:00 — Full suite; where this stops
- Full `llm_negotiation` suite: **1 failed, 1879 passed, 4 skipped** (13 min). The failure was
  `test_configs_written_before_have_no_ethnicity_anywhere` on the new config: the test guards
  configs written before #92, and RF-10's varies ethnicity on purpose. Added it to the test's
  skip list beside the ethnicity rehearsal; `test_ethnicity.py` then 57 passed, 5 skipped.
  `analysis/tests`: 64 passed.
- **Stopped here, before any paid call.** Next, once `CLAUDE.md` records the approval and cap for
  #65: check the balance (free `GET /user/balance`), re-check the price page, `--limit 6` with
  `--client deepseek --confirm` off-peak, read the transcripts (the new `until` forms, the drift
  wording, the encounters kept open), then the rest; `python -m analysis.gate`, `python -m
  analysis` per condition and pooled, and tasks 6 to 8.

## Open questions / risks
1. **Paid approval for #65 is not recorded** in `CLAUDE.md`. Nothing paid runs until it is.
2. **The screen is underpowered for 16 factors** (about 69 resolved outcomes in 288 sessions at
   RF-9's 24% rate, 46 in the design's 192: enough for 4 to 7 terms at 10 events per term, not 19). Only large effects will show; the
   report must say so.
3. **The gate (0.50) is my choice on the user's delegation**, not a sourced number. RF-9's pilot
   resolved 24% (before the fixes), so head-on may fail it; that is a Step 1 finding, not an
   error.
4. **How to handle separated models, to fix before the results (#55, from RF-8):** Firth
   regression, fewer predictors, or relying on the counterfactual pairs. My recommendation:
   report a separated model as such (as RF-8 already does) and rest a factor's claim on its flip
   rate in the counterfactual pairs against the exact-repeat noise floor, plus its descriptive
   table; Firth would need a new dependency and a new estimator, which is more than this issue's
   session. The user's call.
5. **The paid run's numbers:** 288 sessions (not the 276 first estimated), about USD 0.25
   off-peak; the proposed cap USD 0.35 needs recording in `CLAUDE.md` with the approval.

## Summary (fill in at the end)
