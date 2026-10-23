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

## Open questions / risks

## Summary (fill in at the end)
