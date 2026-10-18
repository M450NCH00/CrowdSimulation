# Work Log — Issue #36: [Research] PT-2 Literature: testing rules on unseen scenarios (transfer, generalisation, scenario descriptions)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/36
**Branch:** `docs/36-unseen-scenario-testing-literature`
**Started:** 2026-10-18

## Understanding the issue

Issue #34 proposes, **without anyone's agreement yet**, that rules extracted from LLM agents be
written over a portable vocabulary and tested on scenarios they were not extracted from (queue
cutting, bus and MRT boarding, lifts), described as simulator-independent *scenario cards*. The
claim to test is "the same kind of conflict, in any simulator", not "any conflict", because the
game-theory review found no evidence that conventions transfer between structurally different games
(`literature/game-theory/g6-transfer-across-games.md`, "What this means for the FYP", points 1-2).

This issue is literature only (no code, no paid calls). It asks:

- **Q1** how other fields test whether a model, policy or rule generalises to situations it was not
  built from (Melting Pot; Zhang et al. 2026's out-of-domain test, cross-referenced only;
  cross-scenario validation of pedestrian models);
- **Q2** what the behavioural-spillover studies g6 §3 could not obtain say about conventions
  carrying over to structurally different games: read what is open, stub the rest;
- **Q3** how test scenarios are specified so that several simulators can run them (RiMEA, ISO 20414,
  IMO MSC.1/Circ.1238, OpenSCENARIO, ODD, SteerBench, JuPedSim journeys/stages), and what each
  cannot express;
- **Q4** how LLM-agent studies separate recall of a norm from generalisation (cross-referencing g5
  §4 and Cross et al. 2025, not re-summarising them);
- **Q5** a draft test protocol for the FYP: transfer levels L0-L4, hold-out, freezing, baselines,
  metrics, and scenario-card fields, each cited or marked as a proposal.

Deliverables go in `literature/unseen-scenarios/`, sources in `refs/`.

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** `origin/main` is still `5a0f7be` and has none of the files the issue says to
  read. Branches have been stacked since #8 (the user chose this for #30 and #32). The files the
  issue names are all on `docs/35-simulator-independent-rule-representations` (PR #43, head
  `affa370`, in sync with origin), and #36 is the next issue in the same track, so I cut this branch
  from there and will target the PR at it. A merge into a non-default branch will not close #36 by
  itself.
- **A2. Cache prefix.** Sources for this issue are cached as `refs/us_*` (unseen scenarios),
  following `gt_*` (#20), `sr_*` (#22) and `pr_*` (#35).
- **A3. What is committed** (the repository is public; #35's A7). Text extracts and PDFs are
  committed only for openly licensed copies, arXiv, and public standards/documentation pages that
  allow it; copies with no open licence are kept on disk only, text included, and listed in
  `.gitignore` with a re-download link.
- **A4. Reads beyond "these, and only these".** Issue #34's "Constraints for every issue in this
  track" was already read for #35 and binds this issue too (no paid calls; mark design decisions vs
  assumptions). I also looked at the *format* of #35's work log and `missing-papers.md` to keep the
  same conventions; no content from them is used. To give Zhang et al.'s out-of-domain test a
  locator I search the cached text `refs/zhang2026_dfd.txt` for that one passage, because the
  summary's sections 2 and 6 mention the out-of-domain set but not how it was built.
- **A5. Stubs** for sources that cannot be opened go in the file where the entry would have gone
  (`methods.md` or `scenario-standards.md`) with exactly the issue's six lines, and are listed in
  `missing-papers.md`.

## Plan

1. Branch and work log. **(done)**
2. Read what the issue lists. **(done)**
3. Confirm and cache the seed sources in the issue's priority order: (1) scenario standards,
   (2) generalisation methods, (3) the six spillover leads, (4) leakage.
4. Write `scenario-standards.md` (Q3), with one comparison table of what each format can and cannot
   express.
5. Write `methods.md` (Q1, Q2, Q4).
6. Write `test-protocol-draft.md` (Q5), citing an entry or marking "proposal" for every level,
   metric and card field.
7. Write `verdict.md` (one page), `search-log.md`, `missing-papers.md`,
   `refs-unseen-scenarios.bib`.
8. Verify against §5b of the workflow (locators, open questions, every Q answered), push, open the
   PR against the #35 branch.

## Progress log

### 2026-10-18 — Branch, background read
- What I did: cut `docs/36-unseen-scenario-testing-literature` from the #35 branch (A1); read issue
  #34's "The idea", g6 §2-§3 and "What this means for the FYP", g5 §4, the Zhang summary §§2 and 6,
  and the scenario ids in `dataset/scenarios.yaml`.
- Why: the issue's "Before starting" list.
- Result / what I found: the 14 scenario ids include three that the unseen-scenario track names as
  targets (`lift_boarding_capacity`, `bus_queue_boarding`, `mrt_door_alight_board`). Queue cutting is
  not among them. The Zhang summary records only that there were "three [seeds] for the
  out-of-domain set" (§2) and that all three datasets come from the same LLM simulation (§6), so the
  out-of-domain construction must be located in the cached paper text.
- Next step: cache the scenario standards.

## Open questions / risks

(to be filled during the work)

## Summary (fill in at the end)
