# Work Log — Issue #40: [Research] PT-6 Simulators, part 2: hands-on trial of the shortlist, and the use-or-build decision

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/40
**Branch:** docs/40-simulator-hands-on-trial
**Started:** 2026-10-18

## Understanding the issue

Track #34 proposes (not agreed; needs the supervisor's sign-off) that extracted rules become
portable: a rule core over a fixed vocabulary, two adapters per simulator, and tests on unseen
scenarios such as queue cutting and boarding. #39 surveyed simulators from the desk and
shortlisted JuPedSim, Mesa and (conditionally) SUMO. This issue tries them by hand and decides,
for each role (second continuous testbed, discrete testbed, boarding host), between
**(a) use**, **(b) refer and build** and **(c) hybrid**.

Four trials per simulator where they apply: a queue with a newcomer; a bus or train door; the two
adapters in miniature; scale at 1,000 and 10,000 agents. For each: what worked, code size,
determinism, logging. Deliverables: `integration/simulator-survey/hands-on.md`, `decision.md`,
`spikes/` (throwaway code, pinned requirements).

**Base branch.** Track #34 branches stack on the previous issue's branch, because `origin/main` is
still at the initial commits. This branch is cut from `docs/39-simulator-desk-survey` (PR #47,
open), which holds the shortlist this issue needs.

## Plan

1. Read `shortlist.md` and `comparison.md` (done before branching).
2. Ask the user whether the standing supervisor instruction (`README.md`, "Status of that
   instruction: unconfirmed") allows throwaway trial code. Record the answer **before** any install.
3. Create a new venv (outside `llm_negotiation/`, gitignored), install pinned `jupedsim` and
   `mesa` from PyPI only. Record exact versions and the Python version.
4. JuPedSim: trials 1, 2, 3, 4; determinism; logging.
5. Mesa: trials 1, 2 (optional), 3, 4; determinism; API check of the event-scheduling methods.
6. SUMO: only if JuPedSim's trial 2 shows a stand-alone door lacks what a vehicle model gives.
7. Write `hands-on.md`, then `decision.md` (matrix with proposed weights, recommendation marked as
   a proposal).
8. Check `llm_negotiation/` is untouched and its tests pass. Push, PR against the #39 branch.

## Progress log

### 2026-10-18 — Start
- What I did: read issue #40, `shortlist.md`, `comparison.md`, the `README.md` standing
  instruction and `WORK_LOG-39.md` Q1. Created the branch from `docs/39-simulator-desk-survey`.
- Result / what I found: prerequisite met (`shortlist.md` exists on the #39 branch). #39's Q1
  (whether `ntu-fyp-25/crowdgym` is the senior's and may be read) has no answer on the issue, so I
  do not open that repository. Python 3.12 and 3.13 are installed (Mesa 3.5.1 needs ≥3.12).
- Next step: ask the user the standing-instruction question.

## Open questions / risks

## Summary (fill in at the end)
