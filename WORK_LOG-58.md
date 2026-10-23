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

## Open questions / risks
- Speech rate (2.5 words/s) and the 1 s no-conflict end are placeholders.
- The protocol does not check `CLAUDE.md` for a paid-run approval: like #30's layer it relies on
  the budget cap and `--confirm`. No paid call is made in this issue.

## Summary (fill in at the end)
