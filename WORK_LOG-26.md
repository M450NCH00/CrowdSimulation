# Work Log — Issue #26: [Feature] SI-1: ORCA avoidance layer with sensing radius, perception, and an avoidance action space

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/26
**Branch:** `feat/26-orca-avoidance-layer`
**Started:** 2026-10-13 19:58 (UTC+8)

## Understanding the issue

This is the first of six sub-issues that follow #24. The simulator built in #24 can settle a
conflict in exactly one way: it decides who goes first, and slows the other agent down. A
rule extracted from it could therefore only ever prescribe *priority*. The project also wants
rules that prescribe *avoidance* ("keep to the left", "the faster walker goes round"), so that
the conflict never arises. This sub-issue builds the layer that makes avoidance possible, and
nothing more: no rules, no rule database, no LLM call.

What has to exist at the end:

1. **ORCA** (Optimal Reciprocal Collision Avoidance; van den Berg, Guy, Lin, Manocha) for
   holonomic agents, written from the paper and checked against the RVO2 library's source,
   which is to be read and not run and not added as a dependency. Agent-agent and agent-wall
   constraints, the reference algorithm's handling of the infeasible case, a spatial index for
   neighbour search, and dynamics made pluggable so that a vehicle model can be added later.
2. **A sensing radius and a perception record.** When a neighbour comes within the radius, the
   agent builds a documented, versioned record of what it can perceive of that neighbour and
   of its surroundings. Age and gender follow #24's visibility settings; the task is never in
   the record.
3. **An avoidance action space**: an `AvoidanceDirective` (side preference, responsibility
   share, speed scale, clearance margin, passage order), the reciprocity condition on the
   responsibility shares with a logged, documented resolution when a pair violates it, and a
   `DirectiveProvider` interface with two providers (`NullProvider`, `StaticProvider`).
4. **Layer coordination**: ORCA in open space, the existing arbiter where only one agent fits,
   with the handoff documented and tested. Every existing mode and config behaves as before.
5. **Human-scale parameters**, each cited with a locator or marked `[placeholder]`, and kept
   independent of age and gender unless a config links them explicitly.
6. **Five new scenarios**: `wide_corridor_head_on`, `open_crossing`, `overtaking`,
   `corridor_to_bottleneck`, `bidirectional_flow`.
7. **Conflict metrics** defined operationally, so that a later sub-issue can tell a conflict
   that was avoided from one that arose and was resolved.
8. **Logging**: the #24 log schema extended and its version bumped.

Then behaviour checks reported as numbers (not asserted in advance), a performance benchmark at
100, 1,000 and if feasible 10,000 agents, and zero API spend throughout.

Out of scope, as the issue lists: the rule format and database (SI-2), any LLM call (SI-3),
rule extraction, evaluation and validation (SI-4 to SI-6), the MPC-CBF controller,
non-holonomic ORCA, and any change to the arbiter's decision logic or to existing scenario
configs.

### Assumptions and judgement calls (mine, not instructions from the issue)

- **A1. Branch base.** PR #25 (issue #24) is open and unmerged, so, as the issue instructs, this
  branch is cut from `feat/24-llm-negotiation-simulator` (`3995009`) and the PR will target that
  branch and say so. Because the base is not the default branch, GitHub will not close the issue
  on merge.
- **A2. The supervisor's standing instruction is still unrecorded as lifted.** `WORK_LOG-24.md`,
  open question Q1, asked whether "no simulation or experiment code until the literature review
  is complete and discussed" had been lifted. There is no reply on issue #24 or PR #25, and
  `README.md` still marks it "unconfirmed". Issue #26 was written by the user after PR #25 put
  that question at the top of its description, it has no prerequisite gate of its own, and it
  spends nothing. I read that as the user's decision to go on, and I am proceeding; but nothing
  in the repository records the supervisor's position, and I am not going to write that it has
  been lifted. Carried forward as an open question.

## Plan

Written before reading the sources; the progress log records where it changed.

1. Preconditions, baseline test run, branch, this log.
2. Sources, read before any code: the ORCA paper; the RVO2 source (read, not run) and its
   licence; the GameChat reference list (is ORCA its [22]?); sources for human-scale parameters.
   Cache what can be cached under `refs/`.
3. Design, recorded as numbered decisions: where the layer sits beside the arbiter, how
   dynamics become pluggable, the directive fields and what each does to an ORCA constraint,
   the reciprocity policy, the handoff rule, the log schema changes.
4. ORCA core: the half-plane for a pair of agents, the half-planes for a wall segment, the
   two-dimensional linear program, and the fallback program for the infeasible case. Unit
   tests against hand-computed cases as each piece is written.
5. Neighbour search with a spatial index, tested against brute force.
6. Perception record and the visibility rules; tests that hidden attributes never appear.
7. `AvoidanceDirective`, the reciprocity check and its resolution, the provider interface and
   the two providers.
8. Pluggable dynamics and the simulation loop of the ORCA mode; coordination with the arbiter
   and the handoff.
9. Parameters: find sources, write `docs/parameters.md`, mark what is left `[placeholder]`.
10. The five scenarios and their configs.
11. Metrics and logging; bump the log schema version; keep the #24 run folders valid.
12. Property test over seeded two-agent encounters; behaviour checks; benchmark.
13. Docs: `orca.md`, `perception.md`, `parameters.md`, `metrics.md`; updates to
    `derivations.md`, `architecture.md`, `log-schema.md`, the READMEs.
14. Verify every acceptance criterion, push, open the PR against the #24 branch.

## Progress log

### 2026-10-13 19:58 — Preconditions, issue read, baseline

- What I did: checked the remote and `gh auth status` (OK), the working tree (clean), fetched
  `origin`. Read the issue (no comments on it), then, as it asks, `llm_negotiation/README.md`,
  `llm_negotiation/docs/architecture.md` and `WORK_LOG-24.md` with its open questions, and
  after those every module under `negsim/` that the new layer has to sit beside. Checked
  issue #24 and PR #25 for replies to #24's open questions: none.
- Why: workflow steps 0 and 1, and the issue's "Before starting".
- Result / what I found:
  - PR #25 is `OPEN`, not merged, so the branch base is `feat/24-llm-negotiation-simulator`
    (assumption A1).
  - **Baseline: 432 tests pass** (`python -m pytest` in `llm_negotiation/`, 33.5 s) on Python
    3.13.3 in a clean virtual environment built from `requirements.txt`. The system Python has
    no pytest, so, as in #24, nothing is installed into it.
  - The arbiter's entry point for "who leads" is `decide_roles(..., negotiated_leader=...)` at
    `negsim/conflict/roles.py:80`, reached through `Arbiter.resolve(world, negotiated_leaders)`
    (`negsim/control/strategy1.py:106`). That is the seam the directive's `passage_order` will
    use; nothing in either function needs to change.
  - Three things in the existing code that the new layer cannot simply reuse, each of which
    becomes a design decision: `World.step` is hard-wired to the unicycle; `Scenario` and the
    experiment runner assume exactly two agents; and the run loop treats any agent that leaves
    its desired path as an error to be measured, where under ORCA leaving the path is the
    point.
  - The repository already caches two secondary sources on ORCA, from issue #22:
    `refs/sr_gameaipro3_ch19_rvo_orca.txt` and `refs/sr_orca_localmapf_2107_00246.txt`. The
    original paper is not cached.
- Next step: read the sources.

## Open questions / risks

- **Q1 (carried from #24) — has the supervisor's "no simulation code until the literature
  review is complete and discussed" instruction been lifted?** See assumption A2.

## Summary (fill in at the end)

