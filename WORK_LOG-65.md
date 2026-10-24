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

## Open questions / risks
1. **Paid approval for #65 is not recorded** in `CLAUDE.md`. Nothing paid runs until it is.
2. **The screen is underpowered for 16 factors** (about 66 resolved outcomes expected at RF-9's
   24% rate, enough for 3 to 4 terms at 10 events per term). Only large effects will show; the
   report must say so.
3. **The gate (0.50) is my choice on the user's delegation**, not a sourced number. RF-9's pilot
   resolved 24% (before the fixes), so head-on may fail it; that is a Step 1 finding, not an
   error.

## Summary (fill in at the end)
