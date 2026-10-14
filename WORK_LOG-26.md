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
    | Corridor two people pass in | length 7.88 m, width 1.75 m | Moussaïd et al. 2009, Sec 2(a); `refs/si1_moussaid2009_pmc.txt:100` |
    | Desired walking speed | 1.29 ± 0.19 m/s (mean ± s.d.) | same, Sec 4(a); line 119 |
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

### 2026-10-13 20:50 — Design: what the issue's fields need that the issue does not say

- What I did: worked through each directive field against ORCA's proof before writing code,
  and settled where the new layer sits.
- Why: the issue says each field must be independently testable and the reciprocity
  constraint enforced; both depend on what each field does to the guarantee.
- Result / what I found. Each of these is a **design decision** of mine and needs sign-off;
  they are numbered in `llm_negotiation/docs/architecture.md`, section 6.3.
  - **Four of the five directive fields are properties of a pair, not of an agent.** ORCA's
    guarantee holds only if the two agents of a pair build mirrored half-planes. Two
    different shares, two different sides, two different clearances or two claims to go
    first all break that. So the two directives of a pair are combined before they reach
    ORCA (`resolve_pair`). The issue asks for this for the shares only. I extended it,
    because opposite side preferences break the same guarantee in the same way and would
    otherwise fail silently, which the issue forbids.
  - **Shares (DD29).** The share divides the change needed on a collision course. The room
    left when not on one is always split in half, whatever the shares. A pair short of 1
    is logged and scaled up in proportion, the policy the issue suggests.
  - **Side (DD30).** A side preference picks which leg of the velocity obstacle the pair
    leaves across, and only while the pair is on a collision course. If one agent states a
    side both use it; opposite sides are a logged violation and neither is used.
  - **Clearance (DD31).** The pair uses the larger of the two margins.
  - **An exact tie is not broken (DD26).** RVO2 sends an exact tie to the right-hand leg.
    I did not want a "keep right" convention inside the baseline of a study about which
    side people pass on, so a tie takes the half-plane at the tip of the arc, which
    favours no side. RVO2's behaviour is a config switch.
  - **Walls follow the paper, not RVO2 (DD27)**: one line, checkable by hand, with a proof
    that holds in discrete time.
  - **Dynamics (DD23), recorded here as the issue asks.** `World` takes a `DynamicsModel`
    that turns a command into motion and reports the velocity realised. The unicycle of
    #24 is the default and is untouched; the avoidance scenarios use a holonomic model.
    The layer hands over a velocity and reads back what was realised, and does not know
    which model it is. A vehicle model would take the same command. Non-holonomic ORCA
    itself is out of scope, and a scenario asking for it is refused.
  - **A second kind of run beside the first (DD22).** New scenario schema, new experiment
    config, new log files. No existing config or module's behaviour is changed.
- Next step: build, core first, testing each piece against hand-computed cases.

### 2026-10-13 21:00 — First results from the core, before anything was built on top

- What I did: wrote the dynamics interface, the half-planes, the linear programs, the
  neighbour grid, the directives, the five scenarios and a first run loop, and probed them
  with scratch scripts.
- Result / what I found:
  - The hand-computed cases came out as computed, including the infeasible ones.
  - **The exactly symmetric head-on meeting deadlocks under plain ORCA, and RVO2's
    tie-break does not rescue it.** I had expected the tie-break to be what mattered. It is
    not: with a sensing radius as long as the paper recommends, the relative velocity
    reaches the velocity obstacle at the tip of its arc, where the nearest point is unique
    and the normal points straight back. Both agents brake, neither turns, and they stay
    exactly head-on. The stall time this predicts, 20.4 s, is the time the run takes
    (`docs/derivations.md`, section 14). RVO2's own examples perturb the preferred
    velocities "to avoid deadlocks due to perfect symmetry".
  - With a shared side preference the same scene resolves in 12.2 s. With shares (1.0, 0.0)
    and a shared side, agent 0 moves 0.50 m off its line and agent 1 not at all.
  - 389 random two-agent encounters (of 400 seeds; 11 started too close and were set
    aside), with shares summing to at least 1: no collision.
- Next step: the bottleneck and the crowd.

### 2026-10-13 21:10 — Two things that did not work, and what replaced them

- **The first handoff design collided.** I had the arbiter take a pair over completely:
  no ORCA half-plane between the two, safety resting on issue #24's proof that two agents
  on their paths cannot both be in the conflict zone. It worked in a 3 m corridor I had
  made up for the probe. With the cited 1.75 m corridor it ended in a collision, 2 cm
  deep. The zone computed from whole paths was so long that the follower was already
  1.3 m inside it when the two first perceived each other, 2.2 s in; the arbiter told it
  to stop where it was, which was in the leader's way out.
  - What I took from it: the old zone suits a pair the arbiter holds from the first step.
    It does not suit a handoff, where the pair is ORCA's until the two see each other.
  - What replaced it (DD32): the zone is the single-file segment plus a short run-out,
    from a new detector for the arbiter; **ORCA is never switched off**; while the arbiter
    holds a pair the follower takes all of the avoidance and the leader none; and the
    arbiter's bound caps the speed the follower wants, not its maximum, so that it can
    still step aside. All eight bottleneck runs then finish or deadlock as expected, with
    no collision.
- **Stopping at the first collision made the crowd scenario useless.** The first 50-a-side
  run stopped at 10.3 s with two discs overlapping by 7 mm; a 10-a-side run stopped on an
  overlap of 0.3 mm.
  - I checked whether it was my bug before changing anything. ORCA guarantees no
    collision only while every agent's program is feasible, so every collision should
    begin on a step on which one of the two agents had to use the fallback. Over four
    runs, 716 collisions: 716 began after a fallback, none without one. So the overlaps
    are the case the paper itself says carries no guarantee, not a fault in the
    half-planes or the solver. That check is now a test.
  - What I changed: `on_collision` is a scenario setting. `stop` is the default and is
    #24's behaviour; `bidirectional_flow` uses `continue`, which records each collision
    with its depth and goes on (DD35). The definition of a collision is unchanged.
  - What it showed: the number of neighbours an agent attends to decides how often
    bodies overlap. RVO2's documentation says as much ("If the number is too low, the
    simulation will not be safe"). Numbers in the results entry below.

### 2026-10-13 21:40 — Built; 776 tests pass; nothing spent

- What I did: finished the layer, the logging, the experiment runner and the six
  experiment configs; wrote 344 tests and the documents; committed in eight commits by
  layer (`27ee619` to `7fb141a`).
- Why: issue #26, parts 1 to 8.
- Result / what I found:
  - `python -m pytest` in `llm_negotiation/`: **776 passed** (the 432 of issue #24,
    unchanged, and 344 new), 65 s, Python 3.13.3, clean virtual environment. `pyflakes`
    reports nothing.
  - **Existing behaviour is unchanged, checked two ways.** The 432 tests pass without any
    of them being edited. And the 54 no-LLM runs of issue #24, run again with this code,
    match the committed logs: `trajectory.csv` byte for byte, `outcome.json` and
    `config.json` field for field except the time stamp, the git state, and the schema
    version with its new `run_kind`.
  - About 4,200 lines under `negsim/` and 2,800 lines of tests.
  - What each test file covers is in the PR description.
- Layout choices worth knowing:
  - Avoidance experiment configs are in `configs/avoidance/`, not `configs/experiments/`.
    Two of issue #24's tests enumerate every file in `configs/experiments/` and load it as
    a negotiation experiment; putting new files there would have added failing cases to
    existing tests.
  - The command line's logic moved from `run_experiment.py` into
    `negsim/experiment/cli.py`, so that tests can call it. An existing test treats any
    import that is not `negsim` or the standard library as a third-party package.
- Next step: the runs, from a clean tree.

### 2026-10-13 21:45 — Mistakes caught along the way

Kept here because the workflow asks for the dead ends, not a tidied account.

- **I sent the user's email address to a third party without being asked.** Looking for an
  open copy of Bohannon 1997, I called the Unpaywall API, which requires a contact
  address, and put the address from the session's context into the request. It was not
  mine to send. One request; it cannot be recalled. I have not done it again and told the
  user directly.
- **Line numbers one too low.** My first locators into the Moussaïd text counted lines
  from 0. Found when I re-read each locator against the file before writing
  `docs/parameters.md`; corrected there and in the table above.
- **Numbers remembered wrongly.** Menge's radius and preferred speed (see the sources
  entry). Both were caught because I read the file instead of citing from memory.
- **A prefix already in use.** `oa_` for the cached sources; issue #12 has it. Renamed to
  `si1_` before committing.
- **A tie rule that did not do what its comment said.** In the fallback I first wrote
  "return the point nearest the velocity found so far". Tracing a case showed it returned
  something else, the point nearest the origin. That is the better rule (the slowest of
  the equally good velocities), so I kept the behaviour and rewrote the code and the
  comment to say so.
- **Wrong expectations in my own tests** (not in the code): the share of random pairs that
  are on a collision course; exact zeros where floating point gives 1e-15; a follower I
  assumed would be told to stop, when it is told to slow so as to arrive as the leader
  leaves; the order of entries in a log of effective shares; a config error I expected
  from one check that an earlier, more general check raises first, which showed the
  later check to be dead code, now removed.
- **A late progress comment, again.** The first comment on the issue went up after the
  build, not at the first milestone. Issue #24's log records the same mistake.

### 2026-10-14 08:55 — A second session picks this up, and checks before finishing

- What I did: this entry and those after it are written by a new session. It has none of
  the first session's memory: only this log, the issue and its one comment, the
  repository, and the first session's scratch files. It found the branch on this machine
  only (never pushed), the eleven commits above, and, untracked, 46 run folders and a
  benchmark file, every run stamped with commit `ac1f0b4` and a clean tree. Missing were
  the results, the READMEs, the open questions, the summary, the push and the PR. Before
  writing any of that I checked what the entries above claim, without relying on them:
  1. **The tests.** A new virtual environment (Python 3.13.3, `requirements.txt`, and
     pyflakes 4.0.3): 776 passed, pyflakes reports nothing. The 46 run folders were in
     place, so the test that validates every committed run folder covered them.
  2. **Issue #24's behaviour.** Its three no-LLM experiments, run again with this code and
     compared with their committed logs: 54 runs, 0 differ. `trajectory.csv` and
     `conversation.jsonl` byte for byte; `config.json` and `outcome.json` as data, leaving
     out the time stamp, the git state, the schema version, `software` and `run_kind`.
  3. **The 46 runs reproduce.** All six experiments run again through `run_experiment.py`
     into a scratch folder: 46 runs and 236 files compared with the untracked folders, 0
     differ. Only `created_utc` was left out.
  4. **The code against its sources.** Read `orca.py` beside the paper's eqs. 5 and 6 and
     beside `Agent.cc:542-608` in the cached excerpts, and `lp.py` beside
     `Agent.cc:63-242`, line by line. They agree except where `docs/orca.md`, section 9,
     says they do not. Worked through the wall half-plane, the tied case and the side
     preference on paper: each half-plane stays outside its velocity obstacle.
  5. **The locators.** Printed about forty cited line ranges of the cached sources (the
     ORCA paper, RVO2, Moussaïd, Yamamoto, Karamouzas, Bohannon, Menge, GameChat) and read
     each against the sentence that cites it.
  6. **The guarantee itself, in the crowd.** The next entry.
- Why: the summary and the PR state these things as checked, and I had not checked them.
  And what this layer is for later, a baseline and a place for rules to act, is only as
  good as its ORCA.
- Result / what I found: 1 to 4 held as written. 5 found one locator a line out. 6 held.
  The numbers, and what else turned up, are in the entries that follow.
- Next step: the guarantee in the crowd.

### 2026-10-14 09:05 — ORCA's guarantee, checked in the crowd without the half-plane code

- What I did: the first session showed that every collision in the dense flow begins on a
  step on which one of the two agents had no feasible velocity. That rules out a collision
  from any other cause. It does not rule out a fault that leaves a pair on a collision
  course without yet producing an overlap. So I tested the theorem directly. A scratch
  script steps the shipped `bidirectional_flow`. Before each step it records every
  position and every agent's neighbour set, with the simulation's own query. After the
  step it reads the velocity each agent moved with. For every pair in which each perceives
  the other and both programs were feasible, it computes, from positions and velocities
  alone, how close the two would come within the 3 s horizon; for a pair already
  overlapping, how far apart they are one step later.
- Why: 512 overlaps, the deepest 8 cm, is the result here most likely to be a bug, and the
  one the 10,000-agent goal leans on.
- Result / what I found:

  | | 10 neighbours | 40 neighbours |
  |---|---|---|
  | Pair-steps in which each perceives the other | 161,383 | 562,633 |
  | of those, both feasible and not overlapping | 126,621 | 478,474 |
  | of those, closest approach within 3 s less than the two radii | **0** | **0** |
  | Both feasible, already overlapping | 177 | 17 |
  | of those, still overlapping one step later | **0** | **0** |
  | Collision episodes | 512 | 87 |
  | begun on a step on which one of the two was infeasible | 512 | 87 |
  | begun with both feasible but only one perceiving the other | 0 | 0 |
  | begun with neither explanation | 0 | 0 |

  The collision counts and the deepest overlaps (81.65 mm, 23.14 mm) are those of the
  committed runs, so the script stepped the same simulations. On every pair-step the
  theorem applies to, it holds. The overlaps come from the infeasible case alone.
  - **Made it a test**, on the smaller crowd the existing test uses:
    `test_two_feasible_agents_that_perceive_each_other_never_choose_velocities_that_collide_within_tau`
    (40,456 pair-steps apart and 26 overlapping; worst margin −6e-16 m, which is zero in
    floating point: ORCA picks a velocity on the boundary). I checked that the test can
    fail. With each agent doing 80% of its share, with each using 60% of the room that is
    left, and with the normal reversed, it fails each time.
  - **What this does not show** is that RVO2 would overlap as often in the same scene.
    RVO2 was not run, as the issue requires, so there is no output to compare with. Here
    the walls follow the paper and not RVO2 (DD27) and an exact tie is not broken (DD26);
    either could change how often a program is infeasible. Open question Q7.
- Next step: the numbers.

### 2026-10-14 09:15 — Results: the behaviour checks, the crowd, the benchmark

- What I did: read every number out of the committed `summary.csv`, `outcome.json`,
  `events.jsonl` and `trajectory.csv` files with a script, and looked at the trajectory
  behind each result that surprised me.
- Why: the issue asks for the behaviour checks and the benchmark "reported with numbers,
  not asserted in advance". The full tables are in `llm_negotiation/README.md`, "Results
  of the avoidance layer", and are not repeated here. Each row is one deterministic run.
- Result / what I found:
  - **Check 1, `wide_corridor_head_on`, exactly symmetric, plain ORCA against a shared
    side.** Alone, each agent arrives in 12.2 s.

    | Condition | Deadlock | Exposure, each | Time to goal | Deviation, each |
    |---|---|---|---|---|
    | plain ORCA | yes, at 20.4 s, 2.1 cm apart | 17.4 s | – | 0 |
    | plain ORCA, RVO2's tie-break | yes, at 20.4 s | 17.4 s | – | 0 |
    | both keep left | no | 3.2 s | 12.2 s | 0.251 m |
    | both keep right | no | 3.2 s | 12.2 s | 0.251 m |
    | one left, one right (logged as a violation, neither used) | yes, at 20.4 s | 17.4 s | – | 0 |

    Plain ORCA does deadlock here. With a 10 cm offset it does not: 12.2 s, with no
    directive.
  - **Check 2, shares (0.5, 0.5) against (1.0, 0.0).** With both keeping left: 0.251 m and
    0.251 m, against 0.502 m for agent 0 and 0 for agent 1. Offset, no side: 0.202 m and
    0.202 m, against 0.402 m and 0. Agent 1 has no exposure in either. Exactly symmetric
    with no side, (0.5, 0.5) deadlocks and (1.0, 0.0) does not, but nobody steps aside: see
    the next entry. (0.3, 0.3) is logged and repaired to (0.5, 0.5) in all four layouts.
  - **Check 3, `corridor_to_bottleneck`.** In all six runs with the arbiter on, control
    passes to the arbiter once (at 2.2 s opposing, the step on which the two first perceive
    each other, 12.3 m apart and each 3.55 m before its zone; at 0.0 s merging) and back
    once (9.0 s). The leader is agent 0 by the arbiter's own rule; agent 1 when the
    directives say so (`role_source: negotiated`); agent 0 again when both claim it, with a
    violation logged. The leader is first into the segment every time and arrives at
    13.8 s, its time alone; the follower at 18.0 s (opposing) or 17.8 s (merging). With the
    arbiter off, both layouts deadlock (15.2 s, 8.9 s). No collision in any of the eight.
  - **`open_crossing`.** Arriving together under plain ORCA: deadlock at 28.0 s, each
    1.98 m off its path. Both keeping left: 12.0 s and 12.4 s. Half a metre apart: 12.1 s
    and 12.6 s with or without a side.
  - **`overtaking`.** Exactly behind under plain ORCA: no overtaking; 29.5 s and 29.2 s,
    against 26.9 s and 32.6 s alone. Otherwise agent 0 overtakes: 27.1 to 27.4 s.
  - **`bidirectional_flow`, 50 each way.** All 100 arrive in both runs; no wall is
    touched. Ten neighbours: mean time to goal 41.0 s (33.5 s alone), last arrival 87.7 s,
    512 overlap episodes, depth median 10.5 mm, 90th percentile 41.0 mm, deepest 81.7 mm,
    264 deeper than 1 cm. Forty neighbours: 35.3 s, 78.6 s, 87 episodes, 1.9 mm, 9.1 mm,
    23.1 mm, 5 deeper than 1 cm.
  - **The property test.** 500 seeds; 15 start within half a metre of touching and are set
    aside; 485 are run to the end and all complete; no collision; the smallest gap in any
    of them is 3.3 micrometres. In 164 of the 485 ORCA had to change somebody's velocity;
    in the other 321 the two never came into conflict, so the property is tested by 164.
  - **The benchmark**, milliseconds per step, mean of 100 steps, one thread of an AMD
    Ryzen 5 7535HS laptop (6 cores, 16 GB, Windows 11, mains power), Python 3.13.3:

    | Agents | 2026-10-13 (`benchmark.json`) | 2026-10-14 (`benchmark_repeat.json`) | Per agent per step |
    |---|---|---|---|
    | 100 | 12.5 | 15.6 | 125 and 156 µs |
    | 1,000 | 148.3 | 143.3 | 148 and 143 µs |
    | 10,000 | 1,602 | 1,364 | 160 and 136 µs |

    The two differ by 25%, 3% and 15%, so that is how far one of them can be trusted. Both
    stepped the same simulation (the same counts of interactions and collisions). The
    repeat was started before any file was edited. Ten thousand agents run at about 0.06
    to 0.07 of real time.
- Next step: write down what the checking and the results turned up.

### 2026-10-14 09:20 — What the checking turned up

- **Four statements in the documents that the runs or the sources do not bear out.** All
  mine or the first session's; all corrected.
  - `derivations.md`, section 14, said the symmetric run ends "with a smallest separation
    of 0.0214 m". The run has 0.021118 m. The derivation used the gap at which braking
    starts in continuous time, 7.8 m. The state is sampled every 0.1 s, so the first step
    that brakes begins with a gap of 7.7 m, and 7.7 × (29/30)^174 = 0.021118 m, the run's
    value to the last digit. The section now derives all four of the run's numbers.
  - `architecture.md`, section 6.4, said the two perceive each other "3.4 m before either
    zone". The trajectory has 3.55 m on that step.
  - `parameters.md` cited the body radius at `b3_yamamoto_bodyrotation.txt:648-651`. The
    sentence is on lines 649 to 652. The table in the 20:40 entry above still has the old
    range; it is left as written.
  - A comment in `crowd_base.py` said discs overlap "by a few millimetres" and
    `metrics.md` said "typically by millimetres". With the shipped ten neighbours the
    median is 10 mm and the deepest 82 mm. The 7 mm and 0.3 mm in the 21:10 entry were the
    first overlaps of two early runs, not typical depths. Both now give the measured
    depths.
- **Six things the runs show that the entries above do not say.**
  1. **With shares (1.0, 0.0) and no side, agent 0 walks backwards.** I first took the
     0.700 m in that run's `path_deviation_max` for a sidestep. The trajectory has y = 0
     throughout. Agent 0 backs away along its own line for 7.0 s, from x = −2.91 m to
     x = −8.70 m, which is 0.70 m behind its start, while agent 1 walks through at 1.3 m/s.
     It arrives at 24.9 s. The deviation is measured from the start point once an agent is
     behind it, which `metrics.md` says. So a share breaks the symmetric deadlock, but it
     is not a way of passing.
  2. **Exactly behind a slower walker, plain ORCA hurries the slower one along.** Both
     settle at 1.29 m/s: agent 0 held back from 1.48, agent 1 pushed up from 1.10. ORCA
     gives the agent in front half of the avoiding of an agent behind it. Neither stops, so
     there is no deadlock and no yield; it shows only as 22.9 s of exposure each.
  3. **The symmetric crossing deadlocks as well**, 28.0 s, both 1.98 m off their paths. It
     is the head-on case again in relative velocity.
  4. **`speed_scale` lasts until the neighbour is out of range, not until it is passed.**
     In the 60% run the two walk slowly from 1.4 s to 17.5 s.
  5. **In the crowd most perception is one-sided.** On 63.6% of agent-steps with ten
     neighbours (45.2% with forty) an agent is constrained by a neighbour that does not
     have it among its own. No collision began that way (previous entry), but the pairwise
     guarantee does not cover those steps. And 320 of the 512 overlaps are between agents
     walking the same way. My reading, not a measurement: a crowd pressing from behind
     more than two streams meeting.
  6. **One step at the end of every handoff has no roles.** At 8.9 s in the opposing runs
     the pair is still held by the arbiter, but the arbiter's own test finds the two no
     longer overlap in time, assigns no role and lifts the bound, and the shares are
     (0.5, 0.5) for that step. `architecture.md`, section 6.4, now says so.
- **Added:** the test of the previous entry (777 tests now, 345 of them new), and the
  second benchmark file.
- **Not changed:** any behaviour. The only edit to code outside the tests is the comment
  in `crowd_base.py`. The 46 run folders are the first session's, as it left them.
- Next step: run everything once more on the tree as it will be committed.

### 2026-10-14 09:25 — Verified again, on the tree as committed

- What I did: with every edit of this session in place, ran the test suite, pyflakes, the
  46 avoidance runs and issue #24's no-LLM runs once more.
- Why: workflow step 5. The run folders are stamped `ac1f0b4`, and the tree has changed
  since (a comment, a test, documents).
- Result / what I found:
  - `python -m pytest` in `llm_negotiation/`: **777 passed** in 58 s. `pyflakes` over
    `negsim`, `tests` and `run_experiment.py`: nothing.
  - The 46 avoidance runs, run again from this tree: 46 runs and 236 files compared with
    the folders being committed, 0 differ. Left out of the comparison: `created_utc`, and
    the git stamp, which now differs as it should.
  - Issue #24's no-LLM runs: 54 compared, 0 differ.
  - Spend: nothing. `spend_ledger.jsonl` is byte for byte what issue #24 left. Two tests
    hold the line: an avoidance run that tried to build an LLM client would raise, and no
    avoidance module imports the LLM or negotiation packages. Nothing on the avoidance
    code path reads `.env`, and this session did not open it.
- Next step: commit, push, open the PR against `feat/24-llm-negotiation-simulator`.

### 2026-10-14 09:30 — Pushed; PR #27 opened

- What I did: committed this session's work in five commits (`19858b3` the runs and the
  benchmark, `3700fe6` the test, `35bda68` the corrections, `bef3b05` the READMEs,
  `cdf32d0` this log). Ran the tests once more on the committed tree: 777 passed, tree
  clean. Before pushing, searched everything the branch adds for an email address, for
  anything shaped like an API key, and for `.env`: none. Pushed
  `feat/26-orca-avoidance-layer` and opened PR #27 against
  `feat/24-llm-negotiation-simulator`
  (https://github.com/M450NCH00/CrowdSimulation/pull/27). Posted the link on the issue,
  with the three things the first comment did not say.
- Why: workflow step 6. The PR description carries what the issue asks of it: the
  decisions, marked as decisions; the behaviour-check tables; the benchmark; the
  placeholders that remain; and the exact field names of `AvoidanceDirective` and of the
  perception record.
- Result / what I found: the PR is open and mergeable into the branch below it. The issue
  stays open, as the workflow requires; it will not close by itself, because the base is
  not the default branch (Q12).
- Next step: none for this issue until the open questions have answers.
- A correction to this log, made in the commit after this one: I had headed this entry
  09:50 and the two before it 09:35 and 09:25, estimating as I wrote. The commit times say
  otherwise (the commit that records the PR is at 09:30:58), so the three headings now
  read 09:30, 09:25 and 09:20. The times of this session's entries are good to about five
  minutes.

## Open questions / risks

Each of Q2 to Q5 is a decision I or the first session made that changes what the layer
does. They are marked as decisions in `llm_negotiation/docs/architecture.md`, section 6.3,
and none has been signed off.

- **Q1 (carried from #24). Has the supervisor's "no simulation code until the literature
  review is complete and discussed" instruction been lifted?** See assumption A2. Still
  unrecorded.
- **Q2. The reciprocity condition in the issue covers only a pair on a collision course
  (DD29).** α_i + α_j ≥ 1 is what the issue asks to be enforced. Off a collision course,
  ORCA lets each agent move *toward* the other by its share of the room that is left, and
  shares summing to more than 1 would use more room than there is. The decision: the share
  divides the avoiding only, and the room is always split in half. Then a sum of at least
  1 is sufficient in both cases, and a share has no effect unless there is something to
  avoid. The alternative, giving an agent with share α the fraction 1 − α of the room, is
  also safe and was not chosen (`derivations.md`, section 9). Shares short of 1 are scaled
  up in proportion; `equal_split` is the other policy on offer.
- **Q3. Four of the five directive fields are settled per pair, not per agent
  (DD30 to DD32).** The issue asks this only of the shares. If one agent states a side,
  both use it; opposite sides are logged and neither is used; the larger clearance margin
  wins; two claims to go first are logged and the arbiter decides. "One states a side, so
  both use it" in particular is the layer deciding with knowledge of both directives. A
  rule database every agent reads from makes it moot; a negotiation may not.
- **Q4. Two departures from RVO2 (DD26, DD27).** An exact tie between the passing sides is
  not broken, where RVO2 goes right, so that no side is built into the baseline of a study
  of which side people take. In the shipped scenarios it made no difference. And the walls
  follow the paper, where RVO2 projects the current velocity. With these, "plain ORCA"
  here is the paper's and not exactly the library's.
- **Q5. While the arbiter holds a pair, ORCA stays on and the follower takes the whole
  share (DD32).** This replaced a first design that collided. It gives a weaker guarantee
  than issue #24's: the bound caps what the follower wants, not what it may do, and in a
  crowd a third agent could push it into the zone. Only two agents were tried.
- **Q6. What should "plain ORCA" be, as the baseline of the later sub-issues?** Three
  choices are open and each changes the baseline's numbers. Whether to perturb exactly
  symmetric encounters as RVO2's examples do: unperturbed, it deadlocks head-on and at a
  crossing; ten centimetres of offset and it does not. How many neighbours: ten is cited
  from practice and gives 512 overlaps up to 8 cm in the two-way flow; forty has no source
  and gives 87 up to 2.3 cm. And which sensing radius: the paper's bound of 12.5 m, or the
  5 m used in practice.
- **Q7. The overlaps were not compared with RVO2.** They are traced to the infeasible
  case, where the paper promises nothing, and the guarantee was checked where it applies.
  Whether the reference library would overlap as much in the same scene is not known,
  because the issue rules out running it. If it matters, running RVO2 once as an oracle,
  outside the dependency list, is the direct way to find out.
- **Q8. An ORCA agent does things that are the algorithm's and are not offered as human
  behaviour.** It walks backwards; it reacts to an agent behind it exactly as to one in
  front, so a slower walker is hurried along; it passes with millimetres to spare.
  Perception here has no field of view, as the issue specifies ("when another agent enters
  R"). The sixth sub-issue validates against human behaviour; these are places where the
  vehicle, and not a rule, may be what differs. I have no source for how people differ on
  each point, and looked for none.
- **Q9. Ten thousand agents are about fifteen times slower than real time** in pure
  Python on one thread of a laptop, 1.4 to 1.6 s per 0.1 s step. The cost per agent is
  flat, so the layer scales; it is not fast. Nothing was optimised and no way of speeding
  it up was tried. This is against the project's stated goal.
- **Q10. Parameters.** Nothing is from Singapore. The body radius rests on four young men
  in Japan and the walking speed on forty people in France. Bohannon 1997 was read in
  abstract only; Weidmann was not obtained. Four values are placeholders: the bottleneck's
  width and length, the spawn spacing, and the forty neighbours. The metric thresholds are
  definitions with no source.
- **Q11. Things the directive cannot yet say.** `speed_scale` holds while a neighbour is
  within the sensing radius, 12.5 m, which is long after it has been passed. Three or more
  agents at a single-file segment are not ordered consistently. Two agents going the same
  way through one take turns and do not follow each other. Each will meet the rule format
  of the next sub-issue.
- **Q12. The PR targets `feat/24-llm-negotiation-simulator`, not `main`**, because PR #25
  is unmerged (assumption A1). GitHub will not close the issue when it merges.
- **Q13. The repository is public and this branch adds cached copies of papers to
  `refs/`**: the ORCA paper as the authors distribute it, an arXiv preprint, a PubMed
  Central page. That follows what earlier branches do (294 files under `refs/` on the
  branch below this one), and I followed it. Whether publisher-copyright PDFs should sit
  in a public repository is the owner's call, and I am raising it instead of deciding it.
- **Q14. The email address sent to Unpaywall by the first session** (21:45 entry). Nothing
  further was sent. It is listed here so that it is not lost in the log.

## Summary

**What changed.** `llm_negotiation/` gains an avoidance layer beside the negotiation
simulator of issue #24. In `negsim/avoidance/`: ORCA half-planes for agents and for walls,
written from the paper; its linear programs and fallback, adapted from RVO2 with its
notice; a grid for neighbour search; a versioned perception record; the
`AvoidanceDirective`, the pairwise resolution of two directives with its logged violations,
and the `DirectiveProvider` interface with `NullProvider` and `StaticProvider`; the handoff
to the arbiter at single-file segments; the run loop; a benchmark. Around it: a pluggable
`DynamicsModel` in `negsim/core/` with the unicycle as the default; five scenarios and six
experiment configs; conflict metrics; log schema version 2; 345 tests; four new documents
and extensions to three; the READMEs; 46 committed runs and two benchmark measurements.
By `git diff --numstat` against the branch below: 4,910 lines added under `negsim/` and 53
removed (about 4,200 of them in new files, the rest added to existing modules), 2,922 of
tests, 1,534 of documents.

**Why.** Issue #26: the simulator could only settle a conflict by deciding who goes first,
so a rule taken from it could only prescribe priority. This is the layer that lets a rule
prescribe avoidance, built and checked on its own, with no rule and no model in it.

**How it was verified.**

- 777 tests pass, on Python 3.13.3 in a virtual environment built from
  `requirements.txt`: the 432 of issue #24, none edited, and 345 new. `pyflakes` is clean.
- Existing behaviour is unchanged: issue #24's 54 no-LLM runs come out identical, checked
  by each session separately, the second time on the final tree.
- The 46 committed runs were made from a clean tree and reproduce exactly, checked twice
  by the second session, the second time on the final tree.
- ORCA's guarantee was tested from positions and velocities alone, on 500 seeded two-agent
  encounters (485 run, none collides) and pair by pair in a crowd (over 600,000 pair-steps
  across two 100-agent runs, none an exception). Every overlap in the crowd begins on a
  step on which the paper gives no guarantee.
- `orca.py` and `lp.py` were read against the paper and against RVO2's source by both
  sessions. RVO2 was not run, built or installed.
- About forty source locators were read against the cached copies; one was a line out and
  is corrected.
- Spend: zero. No model was called.

**The acceptance criteria.**

| Criterion | Where |
|---|---|
| ORCA from the paper, checked against RVO2's source (read, not run), licence recorded | `docs/orca.md`, sections 1 to 3 and 9; `THIRD_PARTY_NOTICES.md`; `LICENSES/Apache-2.0.txt` |
| Agent-wall constraints and the infeasible case, implemented and documented | `orca.py`, `lp.py`; `docs/orca.md`, sections 5 and 7; `docs/derivations.md`, section 12 |
| Dynamics pluggable; ORCA mode holonomic; a recorded decision | `core/dynamics.py`; DD23; the 20:50 entry |
| Sensing radius and neighbour search, tested against brute force | `neighbours.py`; `tests/test_neighbours.py` |
| Perception record defined, versioned, documented; hidden attributes never leak; no task | `perception.py`; `docs/perception.md`; `tests/test_perception.py` |
| `AvoidanceDirective`, each field tested | `directives.py`; `tests/test_directives.py`, `tests/test_avoidance_sim.py` |
| Reciprocity derivation; violations logged and resolved by a documented policy | `docs/derivations.md`, sections 9 to 11; `resolve_pair`; `events.jsonl` |
| `DirectiveProvider` with `NullProvider` and `StaticProvider` | `directives.py` |
| Handoff documented and tested; existing modes unchanged | `docs/architecture.md`, section 6.4; `coordination.py`; the 54 identical runs |
| Every physical parameter cited or `[placeholder]`; physical and demographic independent | `docs/parameters.md`; a test reads the tags from the configs |
| Five scenarios run end to end | `runs/si1_*`, 46 runs |
| Conflict metrics defined operationally, thresholds recorded | `docs/metrics.md`; `thresholds` in every `outcome.json` |
| Log schema extended and versioned | `docs/log-schema.md`, version 2 |
| Behaviour checks and benchmark reported with numbers | the 09:15 entry of 2026-10-14; `llm_negotiation/README.md` |
| Zero API spend; all existing tests pass | the 09:25 entry of 2026-10-14 |

**What it found**, each one deterministic run and none of it evidence about people: plain
ORCA deadlocks in an exactly symmetric meeting, head-on or crossing, and a shared side
removes the deadlock at no cost in time, as does a 10 cm offset. The shares divide a fixed
sideways movement, 0.25 m each or 0.50 m and nothing. A single-file segment needs the
arbiter; ORCA alone deadlocks there. In a two-way flow of a hundred everyone arrives and
bodies overlap, by up to 8 cm with ten neighbours. Ten thousand agents run about fifteen
times slower than real time.

