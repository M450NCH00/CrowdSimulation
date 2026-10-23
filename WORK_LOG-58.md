# Work Log — Issue #58: RF-3: Step 1 encounter protocol: trigger, event-driven decision points, three conditions, debrief, one outcome row per session

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/58
**Branch:** feat/58-step1-encounter-protocol (cut from `feat/59-execute-plans-physical-outcomes`, which PR #85 merged into `feat/73-llm-agent-perception-view`; track #55's branches stack, see the memory note on `git checkout main`)
**Started:** 2026-10-23

## Understanding the issue

RF-2 (#57) built the reply format, the templates and the parser. RF-17 (#73) built what an
agent perceives in the running simulation. RF-4 (#59) carries a plan out (`plan_only`,
`plan_orca`) and measures its physical outcome. Nothing yet **runs an encounter**: finds the
moment to ask, asks the agents, carries out what they say, asks again when something new
happens, stops, debriefs, and writes one tidy row per session. This issue is that protocol
(D3 to D6, D8, D13), plus an experiment layer `resolution` that runs sessions over cases,
design cells and the three conditions, on the mock client only.

Pieces the issue asks for, and where they go:

- **Trigger (D4) and members (D16):** the scenario says when a conflict is predicted and who is
  in the encounter. The protocol checks perception (RF-17's view), the shrinking distance and
  "not already in an encounter", and applies the cap on prompted people.
- **Decision points (D5):** event-driven, with the guards (only the noticer, 1 s gap, at most 3,
  the reason logged). Between them the simulator carries out the plans in `plan_only`.
- **Conditions (D3):** independent (1 DP, no message or signal), non-verbal (signals), talk
  (messages, heard as events by listeners).
- **End:** passed, no conflict for 1 s `[placeholder]`, deadlock, time limit. An unresolved
  encounter after the last DP is "not resolved by the LLM" and ORCA takes over.
- **Debrief (D8)**, one per prompted agent.
- **`plan_orca` replay** of every session (RF-4), no LLM call.
- **Storage (D13):** the #30 layout, plus `decisions.jsonl`, `debriefs.jsonl`,
  `outcomes.jsonl/.csv`, `replay/`. A finished session's record is never rewritten.
- **Cost preview** per condition; the **mock rehearsal**; the **tests** listed in task 12.

## Plan

1. **Generalise RF-4 to n people** (needed for the crowd case with four prompted):
   `PlanDriver` takes 2 or more agents, and each plan names its partner (for its events and
   `at_distance_m`). The two-person behaviour must stay exactly as it is (RF-4's tests). The
   outcome row of an n-person encounter keeps the general columns for its first pair, adds
   `encounter_size`, `conflict_pairs`, `conflict_pairs_resolved`, and is resolved only if
   every conflict pair is. The replay accepts n agents and the conflict pairs.
2. **Scenario interface:** `conflict_predicted(simulation, i, j)` and
   `encounter_members(simulation, i, j)`, and a registry lookup by case type. Passing scenario:
   a shared too-narrow segment that one of the two has still to clear, or a closest approach
   under the safety distance at the present or at the desired velocities, not yet passed. A
   new plug-in `passing_crowd` (bidirectional flow): the pair, plus everyone predicted in
   conflict with either of them, nearest first.
3. **`negsim/resolution/protocol.py`:** one session's encounter on its case's source run: the
   trigger, the decision points with D5's events and guards, the conditions, speech that takes
   time, the end and the hand-over to ORCA, the debrief, and the session record.
4. **`negsim/resolution/design.py`:** the #30 factors without `order`; sessions per condition,
   case and cell; `exact_repeat_set`.
5. **`negsim/resolution/experiment.py`:** config (`layer: resolution`), case selection, the
   worst-case cost preview, the budget guard, resume, `--plan`, `--confirm`; per session the
   record, `.md`, `decisions.jsonl`, `debriefs.jsonl`, both replays, the outcome row; then
   `outcomes.jsonl/.csv`, `summary.json`, `report.md`, `cost.json`. Wire it into
   `run_experiment.py`.
6. **Mock policy** for the rehearsal (decisions and debriefs) and
   `configs/resolution/resolve_mock_rehearsal.yaml` (head-on, passage, overtaking, flow with 4
   prompted; all three conditions).
7. **Tests** for every item of task 12, plus RF-4's suite unchanged.
8. **Docs:** a protocol doc with the cost derivation, `log-schema.md` "Resolution
   experiments", `parameters.md` for the new placeholders, `resolution.md` and the READMEs'
   status.

## Progress log

### 2026-10-23 — Start
- What I did: merged PR #85 (RF-4) into `feat/73-...`, closed #59 by hand and ticked it in #55,
  then cut this branch from `feat/59-...`.
- Why: the user asked for #85 to be merged and the next issue in #55's order (#58) to be started.
- Next step: read `docs/resolution.md`, the #30 rulegen layer, `cases.md` section 7 and
  `log-schema.md`, then write the plan.

### 2026-10-23 — Reading done, design choices
- What I did: read `resolution.md`, RF-2/RF-17/RF-4's modules, `rulegen/protocol.py`,
  `design.py`, `experiment.py`, `cases.py`, the log schema and the cost-preview section; timed
  the source runs (head-on 0.07 s, passage 0.02 s, overtaking 0.06 s, the 100-person flow
  21 s).
- Found: `PlanDriver` refuses anything but two agents, so the crowd rehearsal case needs RF-4
  generalised (plan step 1).
- **Assumptions I am making** (not sourced, not the issue's words; to be listed in the docs):
  - *D4 holds per agent for its first prompt.* The issue says every agent in the encounter is
    prompted at the first decision point; D4 says an agent is prompted only if it sees or
    hears the other. I read both as: at the first decision point, every member for whom D4
    holds is prompted; a member who perceives nobody yet (the person ahead in overtaking) is
    first prompted when D4 holds for it.
  - *Conflict predicted (passing):* a shared too-narrow segment not yet cleared by both, or a
    closest approach under the safety distance at the present velocities or at the desired
    ones (path direction, preferred speed), and not yet passed. The desired velocities keep
    two people who have both stopped face to face "in conflict", which the present velocities
    alone would not. The trigger also needs the distance to be shrinking (D4).
  - *A plan "ends" (D5) only if it had steps.* `[]` ("carry on") is not a plan that ends, or an
    agent who says "carry on" would be asked again a second later.
  - *An unreadable reply (after its retry)* counts as a decision point used. The agent carries
    on as it is (`[]` in the driver, so ORCA does not get the credit in `plan_only`), and the
    look is dropped from its perception so its history shows no decision it never made.
  - *Speaking takes time:* words / 2.5 words a second `[placeholder]`, heard when it ends.
  - *ORCA takes over* when every prompted agent has used its decision points and has no plan
    left to run, and the conflict is still predicted. `resolved_by_llm` is then false even if
    the `plan_only` replay is physically resolved, because ORCA did the resolving.
  - *Crowd sessions:* the design's two people are the case's pair; other members get no
    persona (no age, gender or errand).
- Next step: plan step 1 (n-person executor), RF-4's tests unchanged.

### 2026-10-23 — n-person executor, scenario interface, the protocol
- What I did: `PlanDriver` now takes two or more agents; each plan names its partner (two
  agents: the other, as before). The release rule generalises: fewer than two still walking,
  or every two passed with no plan left; with two that is RF-4's rule. RF-4's 29 tests pass
  unchanged. `physical_outcome` of more than two people: the first pair's columns plus
  `encounter_size`, `conflict_pairs`, `conflict_pairs_resolved`, resolved only if every conflict
  pair is. `Scenario` gained `conflict_predicted`, `encounter_members`, `CASE_TYPES`,
  `MAX_MEMBERS`; `passing` predicts; new plug-in `passing_crowd`. Wrote `protocol.py`.
- Smoke runs on the mock (head-on in all three conditions, passage, overtaking, a flow case) found
  three things, each fixed:
  1. **Two people standing still read as "passed".** In the passage case both stopped nose to
     nose; RF-4's pass test (`_passed`: separating and apart) fired on rounding noise in their
     relative velocity, and the encounter ended after one step. The protocol's "passed" now also
     needs no conflict predicted. (RF-4's own release rule is left as it was: it also needs no
     plan running, which holds the two who are stopped by plans.)
  2. **A collision that stops the run** (`on_collision: stop`) ended as a generic "run ended" and
     was not counted as not resolved by the LLM. Now its own end, `collision`, which is.
  3. **`flow_03ea57f6` never triggers**: the pair's lines never come within the safety distance
     while in view. Scanned the eight flow cases: six trigger. `passing_crowd` brings in about
     30 people within 10 m in a dense flow, so the cap is what limits it (recorded per session).
     `flow_ba3c7962` gets all four of a cap of 4 prompted at the first decision point (two of the
     others prompt only two), so the rehearsal uses it.
- Next step: the design module, the experiment layer, the mock policy, the rehearsal config.

### 2026-10-23 — The experiment layer, the tests
- What I did: `design.py` (#30's factors less `order`), `experiment.py` (config, case
  selection, preview, guard, resume, both replays, the tables, report), `transcript.py`, the mock
  policy `resolution_rehearsal_v1`, `configs/resolution/resolve_mock_rehearsal.yaml`, and
  `run_experiment.py` dispatch. 36 tests in `tests/test_encounter_protocol.py`.
- **A bug the tests found:** a signal made at a decision point carried the same time as the
  other agent's look at it, and both D5 and RF-17's view count only what comes *after* a look, so
  nobody ever saw a signal. A signal is now made during the step after the decision point (its
  time is one step later). Messages were not affected: they are heard after they have been said.
- The first full rehearsal (on the code before that fix) ran all 24 sessions: every one reached an
  encounter; ends were passed, collision, no_conflict and orca_took_over. The mock's replies are
  scripted, not a model, so nothing here is a finding.
- **The cost preview** (`--plan`): two-person sessions are bounded at USD 0.029 to 0.030
  (independent), 0.074 to 0.076 (non-verbal), 0.094 to 0.096 (talk), with 6 sends a call at peak
  prices, as in #30. The crowd case's bound is far higher (USD 0.38 to 0.91 a session) because
  with `llm_view.max_people` off all 99 others could be described in full. True but loose; a
  paid crowd run would set `max_people`.
- Wrote `docs/encounter-protocol.md`, `log-schema.md` "Resolution experiments", `parameters.md`
  8.2 (three placeholders) and 8.6, `resolution.md`'s status and as-built notes, both READMEs.

## Open questions / risks
- **`resolved_by_llm` against `resolved_plan_only`.** The issue calls `resolved_plan_only` the
  Step 1 answer. But once ORCA takes over (D6) the `plan_only` replay runs on under ORCA, so its
  physical "resolved" can be ORCA's work. I kept `resolved_plan_only` as the physical column and
  added `resolved_by_llm` (resolved, and ORCA did not take over). To review: which one the
  report should lead with.
- **The trigger reading of "every agent is prompted at the first decision point"** (see the
  assumptions above): in overtaking, the person ahead is never asked unless it hears or sees the
  other. Round 3 ("excuse me") depends on the talk condition for that, which is the design's
  intent, but it should be checked when round 3 is run.
- **`came_into_view` fires a lot in a crowd** (D5 says any new person), so crowd agents use their
  three decision points quickly. Fine for rounds 1 to 3 (two people); rounds 4 and 6 may want it
  limited to people in the encounter.
- Speech rate (2.5 words/s) and the 1 s no-conflict end are placeholders.
- The protocol does not check `CLAUDE.md` for a paid-run approval: like #30's layer it relies on
  the budget cap and `--confirm`. No paid call is made in this issue.

## Summary (fill in at the end)
