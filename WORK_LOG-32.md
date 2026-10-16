# Work Log — Issue #32: [Feature] SI-3a.2: fictional ethnicity attribute and meetings inside a single-file passage

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/32
**Branch:** `feat/32-fictional-ethnicity-passage-meetings`
**Started:** 2026-10-16 20:37 (UTC+8)

## Understanding the issue

<To be filled in before any code is written.>

### Prerequisites (checked before anything else)

- **P1. PRs #25, #27, #29 and #31 merged, and this branch created from `main` — FAILED.** All
  four PRs are in state `MERGED`, but each into its stacked parent branch, not into `main`:
  #25 into `docs/22-simulation-conflict-rules-literature` (PR #23, open), #27 into
  `feat/24-llm-negotiation-simulator`, #29 into `feat/26-orca-avoidance-layer`, #31 into
  `feat/28-rule-format-database-following` (merge commit `32bd93e`). `origin/main` is still
  `5a0f7be` (2026-09-06) and has no `llm_negotiation/` at all; 130 commits of `feat/28` are not
  on it. Between `main` and the simulator stack sit seven open literature PRs (#9, #13, #15,
  #17, #19, #21, #23), each based on the one before. As the issue instructs, I stopped and
  asked. **The user's answer (2026-10-16, in this session): "Stack on #31"**: commit the two
  #30 leftovers to `feat/30-conflict-cases-rule-generation` and push them, cut this branch
  from it, and target the PR at `feat/30-…`. Such a PR will not close #32 on merge (only a
  merge into the default branch does), as #31 did not close #30.
- **P2. The two uncommitted #30 items — DONE.** Both were clear in status, so they were
  committed to `feat/30-conflict-cases-rule-generation` and pushed (`e49ab46..2dad845`), not
  discarded:
  - `a18f727` *feat: optional random starts for the two-way crowd (spawn_pattern: random)*:
    `negsim/scenarios/bidirectional_flow.py`, its tests in `test_crowd_scenarios.py` (7 new),
    a replay check in `test_rulegen_replay.py`, one row each in `llm_negotiation/README.md` and
    `docs/parameters.md`. Before committing, the full suite ran on the working tree: **1,230
    passed** (#30's 1,223 plus these 7; 289 s), pyflakes 4.0.3 clean.
  - `2dad845` *docs: a beginner's guide to the whole repository* (`BEGINNERS_GUIDE.md`,
    1,015 lines; checked for anything resembling an API key first: none).
- **P3. `WORK_LOG-30.md` read**, including DD65 to DD84 and open questions Q1 to Q6. This issue
  is implemented against those decisions as they stand; any change is recorded below as one.

## Plan

<To be filled in before any code is written.>

## Progress log

### 2026-10-16 20:37 — Prerequisites checked; branch created

- What I did: read `github_issue_workflow.md` and the issue; checked P1 to P3 (above); asked
  the user about P1; committed and pushed the #30 leftovers; created this branch from
  `feat/30-conflict-cases-rule-generation` at `2dad845`.
- Why: the issue makes all three hard stops.
- Result / what I found: P1 failed (the stack never reached `main`); the user chose to stack.
- Next step: read the code and documents this issue changes (the arbiter first, since Part 2.1
  asks for its in-passage behaviour to be documented before anything is written), then fill in
  the understanding and the plan.

## Open questions / risks

<Filled in as they arise.>

## Summary (fill in at the end)

<What changed, why, how it was verified.>
