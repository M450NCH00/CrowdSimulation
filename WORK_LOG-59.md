# Work Log — Issue #59: RF-4: carry out the agents' plans in the simulator (plan_only and plan_orca) and add physical outcomes

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/59
**Branch:** feat/59-execute-plans-physical-outcomes (cut from `feat/73-llm-agent-perception-view`, which PR #84 merged into `feat/57-resolve-templates-view-parser`; track #55's branches stack, see the memory note on `git checkout main`)
**Started:** 2026-10-23

## Understanding the issue

RF-2 (#57) parses an agent's reply into `steps` (speed, turn, back-up, start, until), and RF-17
(#73) tells the agent what it perceives in the running simulation. Nothing yet **carries a plan
out**. This issue makes the simulator do so, step by step, so that:

- a plan counts as a resolution only if it works physically (two plans can both sound right and
  still collide);
- the next decision point (RF-3) sees what the plan did.

Plain ORCA already passes a head-on pair on its own. So in the Step 1 measure, **`plan_only`**,
ORCA must not steer the encounter's two agents away from each other. It still handles walls and
everyone else. **`plan_orca`** runs the same plans with full ORCA on top; D6's second replay
is that, with no LLM call.

Also in scope: an `advance(world, plans, until_time)` interface for RF-3, a replay of a recorded
session's plans that can be rebuilt byte for byte from the session record (D13), the physical
outcome columns, and a report of the physical resolution rate.

**Events come from the scenario (D16):** the executor knows no event; it asks the scenario. The
passing scenario (rounds 1 to 3) defines `other_passes`, `other_stops` and
`i_am_out_of_the_stretch`.

Out of scope: prompting (RF-3), body-size changes (D1), crowd screening of rules (RF-12, RF-18).
Paid calls: none.

## Plan

1. Branch, work log (this file).
2. Read `resolution.md` (D1, D6, D16), `simulation.py`, `directives.py`, `rulegen/replay.py`,
   `orca.md`, `baseline.md` section 6, `metrics.md`, `parameters.md`.
3. **The hook.** One optional plan driver in `AvoidanceSimulation`. Without it, every line runs
   as before. With it, the driver may replace an agent's preferred velocity, and in `plan_only`
   drop the half-plane between the encounter's two agents.
4. **The executor** (`negsim/resolution/execute.py`): per-agent plan state, start conditions,
   step transitions, until (seconds or a scenario event), back-up distance, replacement by a
   later decision; `PlanRun` and `advance()`.
5. **The scenario's execution side** (`scenario.py`, `scenarios/passing.py`): events, the
   conflict zone (for "who passed first"), the scenario's own columns, and what "resolved" means.
6. **Physical outcomes and the report** (`negsim/resolution/outcomes.py`).
7. **Replay** (`negsim/resolution/replay.py`): a session's plans on its case's own run, same
   seed, both modes; `outcome.json` records the seed, the scenario hash and the plans' SHA-256;
   a command rebuilds a replay from the session record alone.
8. Tests: task 7's list, plus the rebuild test and "a run with no driver is unchanged".
9. Docs (`resolution.md`, `log-schema.md`, `parameters.md` if any value is added, READMEs),
   full suite, push, PR (targets `feat/73-llm-agent-perception-view`), comment on #59.

## Progress log

### 2026-10-23 — Merged PR #84, closed #73, read #59 and the code
- What I did: merged PR #84 into `feat/57-resolve-templates-view-parser` (a merge commit, as
  PR #83 was), closed #73 by hand with a note, ticked it in #55, and read #59 with everything in
  its "Before starting" list.
- Result / what I found:
  - `AvoidanceSimulation.step` builds every agent's preferred velocity in one loop (step 4) and
    adds one ORCA half-plane per perceived neighbour. A plan hooks in at those two points, and
    nothing else needs to change.
  - The passage source runs (`si32_source_*`) run with the arbiter on (the default), so a plain
    run of a passage case includes Strategy 1's speed bound. `plan_only` must free the
    encounter's agents of it as well as of ORCA, or the arbiter would get the credit.
  - `path_s` only moves forward (`Path.project(..., s_min)`), so an agent walking backwards
    keeps its path tangent. A back-up step backs along that tangent.
  - `config.json` carries `created_utc`. A rebuilt replay can therefore match byte for byte in
    every file except that one line.
- Next step: the hook and the executor.

### 2026-10-23 — The hook, the executor, the scenario's execution side
- What I did:
  - **`AvoidanceSimulation(plans=...)`**: one optional driver, called at five points:
    `prepare` before velocities, `velocity` per agent, `ignores` per neighbour half-plane,
    `backing` in the artefact count, `after_step`, and `finish` from `finish()`. A plan agent's
    trajectory rows say `control_mode: plan`. With no driver, no line runs differently.
  - **`negsim/resolution/execute.py`**: `Plan` (per decision: state, current step, per-step
    records with `ended_by`), `PlanDriver` (schedules, carries out, ignores the pair in
    `plan_only`, releases the encounter, tracks the two agents step by step), `PlanRun`,
    `advance()`, `WorldState`.
  - A plan given live (`give`) and one scheduled for a replay (`schedule`) both take effect in
    the next `prepare`. So a live run and the replay of its log are the same code path; a test
    checks they give the same run.
  - **`Scenario`** gains `happened`, `zone_exits`, `outcome_columns` and `resolved`. The passing
    plug-in fills them in. `EventContext` gives an event the simulation, the two agents, when the
    step began, and a per-step memory.
- Result / what I found (smoke runs on the head-on scenario, decision at 3 s):
  - **Both turning 20° left for 2 s collides in `plan_only`.** The step ends before they meet,
    and both steer back to the centre line. That is the plan's own failure, which is exactly what
    `plan_only` must show. With `until: other_passes` they pass 0.75 m apart, `together`, and
    ORCA takes the encounter back on the step they have passed.
  - **Left and right, empty plans:** collide in `plan_only`. In `plan_orca` they stall, because
    the unperturbed, exactly aligned head-on is the known brake tie (`orca.md`, section 4).
- Next step: physical outcomes, replay.

### 2026-10-23 — Outcomes, replay, rebuild
- What I did: `outcomes.py` (the general columns, the scenario's own columns, "resolved", the
  report) and `replay.py` (a session's plans on its case's own run via
  `rulegen.replay.source_plan`, both modes, `--verify`). `execute_avoidance_run` gained
  `plans`, `config_extra` and `outcome_extra`, and `simulation_for(plan)` builds a run's
  simulation; without the new arguments the folder is as before.
- Result: a hand-written session on `head_on_02dfbadb@2` (both 15° left until `other_passes`,
  one starting at 6 m) resolves in both modes. Plain ORCA on the same seed comes 0.010156 m close,
  **exactly the case's recorded `min_separation_m`**, so the replay ran the case's own run.
  `--verify` rebuilt both folders, and every file was the same except `created_utc`.
- **The plain ORCA run of this case is "not resolved"**: its pass within 0.1 m is a near miss
  (the case's tier is T3). That follows from the issue's definition.

### 2026-10-23 — Tests
- What I did: `tests/test_execute.py`, 29 tests: every item of task 7, plus the rebuild, the live
  run against the replay of its log, the CLI, the report, replacement, release, the arbiter in each
  mode, `other_stops`, `i_am_out_of_the_stretch`, and the parser's checks on recorded steps.
- Two first-run failures, both in the tests:
  - `main()` had bound `sys.stdout` as a default argument, so pytest could not capture it. Fixed
    in `replay.py`.
  - The arbiter test looked at agent 0, but the arbiter makes agent 1 the follower in this
    passage.
- **Dropped:** a test that re-ran a committed source run and compared it byte for byte with the
  committed folder. The folder was written under log schema 4, before issue #32's trajectory
  columns, and git checks it out with CRLF, so it cannot match. `test_rulegen_cases`'s
  re-extraction test already checks that old runs reproduce.

## Open questions / risks

These are **assumptions I made**, not sourced values and not the issue's words. All are
listed, with reasons, in `parameters.md`, section 8.5:

- **A step with no `speed_mps`** walks at the agent's own speed.
- **A back-up step** backs against the path direction where the agent is. With an `until` as
  well, it ends at whichever comes first.
- **The plan is in force from its decision.** In `plan_only` that includes the delay before a
  delayed first step, so ORCA cannot steer during it.
- **The arbiter:** lifted in `plan_only` (it too steers the two apart), kept in `plan_orca` (it
  is part of the plain run in the passage cases).
- **When ORCA takes the encounter back** in `plan_only`: a release by the protocol, an arrival,
  or the two have passed with no plan left. RF-3 decides when to release. What ORCA does after a
  release is in the same run; RF-3 has to record it separately (D6).
- **`other_passes`** adds one case to the issue's definition: the person being overtaken sees
  the overtaker pass. **Known limit:** for the person ahead, an overtaker who gives up and drops
  back also fires it.
- **The conflict zone** in a corridor wide enough to pass is a disc round the midpoint at
  closest approach. A side-by-side pass therefore reads `together`; the issue asks "who passed
  first", and in a wide corridor neither did.
- **"Stopped"** counts the start, so in the passage cases that start at rest both agents always
  count as stopped.
- **The C0 baseline** in the report is GameChat's doorway, intersection and hallway (Strategy 1),
  not these encounters. The issue asks for it "beside"; the report says it is not like for like.
- **The session-record fields a replay reads** (`replay.py` docstring) are fixed here, before
  RF-3 writes session records. RF-3 must write at least those fields, or change both.

## Summary (fill in at the end)
