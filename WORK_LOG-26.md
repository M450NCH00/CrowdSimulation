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

### 2026-10-13 20:40 — Sources read: the ORCA paper, RVO2 (read, not run), parameter sources

- What I did:
  - Downloaded the ORCA paper from its authors' page and read all of it.
  - Cloned `github.com/snape/RVO2` into the session scratchpad with `--no-checkout` and read
    files through `git show`. Nothing was checked out, built, installed or executed.
  - Checked the GameChat reference list in the copy cached by #24.
  - Looked for sources for the physical parameters: first in what the repository already
    caches, then on the web, downloading the raw page or file each time and reading the number
    in it myself instead of trusting a summary or my memory.
  - Cached everything under `refs/` with the prefix `si1_`. (I first used `oa_`, then saw that
    issue #12 already uses that prefix for something else, and renamed before committing.)
- Why: the issue's Part 1 (confirm the citation, read RVO2, confirm its licence) and Part 5
  (a citation with a locator for every physical parameter, or a `[placeholder]` tag).
- Result / what I found:
  - **Citation confirmed, for GameChat v1 only.** ORCA is reference [22] in arXiv:2503.12333v1
    (`refs/ln_gamechat_arxiv_v1.txt:596-598`): J. van den Berg, S. J. Guy, M. Lin, D. Manocha,
    "Reciprocal n-body collision avoidance", in *Robotics Research: The 14th International
    Symposium ISRR*, pp. 3–19, Springer, 2011. In v2 of the same paper [22] is a different work
    (`refs/mahadevan2025_gamechat.txt:558`). The repository's own Crossref record gives the DOI
    `10.1007/978-3-642-19457-3_1` and pages 3–19 (`refs/sr_cr_prewindow.json`). "ISRR 2011" in
    the issue is the year the proceedings were published; the year the symposium was held is
    not stated in anything I read.
  - **GameChat says of ORCA exactly what this sub-issue is about:** "deadlocks often result
    due to the structure of the half-planes [23]" (`refs/ln_gamechat_arxiv_v1.txt:73`).
  - **RVO2**, commit `75822bb` (branch `main`, 2026-09-25). Licence: **Apache-2.0** for the
    source files (SPDX header of `src/Agent.cc`, lines 5–6; `LICENSE` at the root), copyright
    "2008 University of North Carolina at Chapel Hill". The README and citation file are
    CC-BY-SA-4.0. There is no `NOTICE` file.
  - **RVO2 departs from the paper in three places that matter here.** Line numbers are those
    of `src/Agent.cc` at that commit, cached in `refs/si1_rvo2_75822bb_excerpts.txt`.
    1. *Walls.* The paper builds a wall's half-plane at the point of the velocity obstacle
       closest to the optimisation velocity and sets that velocity to zero for obstacles
       (Sec 5.4). RVO2 projects the agent's *current* velocity instead (lines 455–535).
    2. *An exact tie between the two sides.* The paper takes "the closest point on the boundary
       of the velocity obstacle" (Eq. 5) and does not say what happens when two points are
       equally close. RVO2 takes the right-hand leg (`det(...) > 0` picks the left leg, anything
       else the right; lines 574–588).
    3. *The share of the avoidance* is the constant 0.5 (line 607). There is no per-agent
       parameter to change, which is the reason the issue gives for not using RVO2's bindings.
  - **RVO2's own examples work around perfect symmetry.** `examples/Blocks.cc:178` and
    `examples/Roadmap.cc:322` add a random vector of length up to 0.0001 to every preferred
    velocity, under the comment "Perturb a little to avoid deadlocks due to perfect symmetry."
    So the reference implementation does not claim that plain ORCA resolves an exactly
    symmetric encounter. That bears directly on the first behaviour check in the issue.
  - **A gap in the issue's reciprocity condition, found on paper before any code.** The issue
    says the guarantee needs α_i + α_j ≥ 1. That is right when the pair is on a collision
    course. When it is not, ORCA's half-plane lets each agent move *toward* the velocity
    obstacle, by its share of the room that is left; with shares that sum to more than 1 the
    pair could then steer itself onto a collision course. Standard ORCA never meets this
    because its shares sum to exactly 1. So the share cannot simply multiply `u` in both cases.
    Design decision to follow.
  - **Parameter sources found, each read in the raw source and cached:**

    | Quantity | Value in the source | Source and locator |
    |---|---|---|
    | Corridor two people pass in | length 7.88 m, width 1.75 m | Moussaïd et al. 2009, Sec 2(a); `refs/si1_moussaid2009_pmc.txt:99` |
    | Desired walking speed | 1.29 ± 0.19 m/s (mean ± s.d.) | same, Sec 4(a); line 118 |
    | Comfortable gait speed, range of group means | 1.272 m/s (women in their seventies) to 1.462 m/s (men in their forties) | Bohannon 1997, abstract; `refs/si1_bohannon1997_pubmed_abstract.txt` |
    | Maximum gait speed, range of group means | 1.749 to 2.533 m/s | same |
    | Effective shoulder width in passing | 49.8 cm (half of it: 24.9 cm) | Yamamoto et al. 2019, Sec 4.3; `refs/b3_yamamoto_bodyrotation.txt:648-651` |
    | Shoulder width by gender | men 48.4 cm (SD 3.7), women 41.0 cm (SD 1.4); five men, four women | same, Table 2 and Sec 7; lines 1068–1079, 1096–1099 |
    | Corridor widths at which two people were made to pass | 60 to 140 cm | same, Sec 3; lines 344–345 |
    | Interaction time horizon of pedestrians | about 3 s ("consistent with previous research demonstrating ... 2–4 s") | Karamouzas et al. 2014, p. 3; `refs/si1_karamouzas2014_1412_1082.txt:136-138` |
    | ORCA settings used for pedestrians in practice | neighbour distance 5 m, 10 neighbours, τ 3.0 s, obstacle τ 0.15 s, radius 0.2 m, preferred speed 1.34 m/s, maximum 2 m/s | Menge example `examples/core/4square/4squareS.xml`, lines 15 and 22; `refs/si1_menge_4squareS.xml` |

  - **What I could not get.** The full text of Bohannon 1997 is behind a paywall; only its
    abstract was read, so only the two ends of its age-by-sex table are available, not the
    table. Weidmann's 1.34 m/s, the usual citation for walking speed, was not obtained in any
    form; Menge uses that number without citing it.
  - **A number I had wrong from memory.** I expected Menge's example to say radius 0.19 m and
    preferred speed 1.04 m/s. The file says 0.2 and 1.34. Recorded because it is the reason
    every number above was read from its source.
- Next step: the design.

## Open questions / risks

- **Q1 (carried from #24) — has the supervisor's "no simulation code until the literature
  review is complete and discussed" instruction been lifted?** See assumption A2.

## Summary (fill in at the end)

