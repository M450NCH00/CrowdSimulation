# Work Log — Issue #22: [Research] Literature: rule-based conflict avoidance and resolution in simulators and games

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/22
**Branch:** `docs/22-simulation-conflict-rules-literature`
**Started:** 2026-10-04

## Understanding the issue

Issue #20 catalogued *theory* (conventions, correlated equilibria, priority from asymmetries).
This issue catalogues **rules as actually implemented and evaluated in working systems** —
crowd simulators (S1), games and game engines (S2), multi-agent path finding and multi-robot
navigation (S3), and traffic / autonomous vehicles (S4) — so the FYP can reuse and extend an
existing rule rather than invent one. Because the long-term aim is a rule that drops into any
agent-based simulator, **portability across agent types is assessed for every rule**.

Every paper gets one primary category:

- **A** — avoid conflict by following a rule (the conflict state is never instantiated);
- **B** — resolve conflict through communication (a channel carrying information not inferable
  from physical state);
- **C** — resolve conflict by following a rule (contention exists, a rule arbitrates, no
  negotiation).

Hard constraints I am holding myself to:

- **Recency:** only papers published 2016 or later get a template entry. ORCA, RVO, social
  force, boids, CBS and similar go in `pre-window-foundations.md` as pointers only.
- **Sourcing:** nothing is summarised that I did not open in full text. A paper I cannot open
  gets a `[NOT OBTAINED]` stub and a line in `missing-papers.md` — no abstract-based summary.
- **Locators:** every claim and number carries a section / table / figure / algorithm locator.
- **No over-generalising:** if a paper tests 100 agents, the entry says 100 agents.

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** The workflow says branch from `main`, but `main` has no `literature/`
  and no `refs/`; every literature PR is still open and each issue branch is cut from the
  previous one (see WORK_LOG-20 A1). The issue also requires cross-referencing the issue #20
  catalogue, which exists only on `docs/20-game-theory-conflict-rules`. I therefore cut this
  branch from that branch (`fc80940`). The PR will target that branch, as PR #21 targets #18's.
- **A2. `[NOT OBTAINED]` stubs live inside the sub-area file** they would have belonged to, as
  a headed block with exactly the issue's six lines, rather than as one file per paper. The
  issue says "create the file with only this content", but its deliverables list has one file
  per sub-area, not per paper. `missing-papers.md` is the consolidated list either way.
- **A3. Cache prefix.** Sources for this issue are cached as `refs/sr_*` (simulation rules),
  following the `gt_*` prefix used for issue #20.
- **A4. "Published in 2016 or later"** is judged on the version I cite. A preprint first posted
  in-window with no published version is eligible and labelled `[preprint]`.

## Plan

1. Branch + work log. **(done)**
2. Fetch and read the twelve verified seeds; resolve each arXiv seed to a published version
   where one exists; check the mutex-propagation paper's year; confirm or fail the
   `[secondhand]` velocity-obstacle survey; decide whether CrowdVLA is in scope.
3. Search S2 (games) and S4 (traffic) from scratch — no seeds given. S4 must supply genuine
   category B examples (negotiation / protocol-based merging and intersections).
4. Fill gaps in S1 (lane formation, bottleneck, counterflow) and S3 (communication-based MAPF).
5. Cache every source under `refs/sr_*` and first-page-check each download against the expected
   title (the lesson from issue #20's three wrong-paper downloads).
6. Write the four sub-area files with the issue's per-paper template.
7. Write `pre-window-foundations.md`, `missing-papers.md`, `refs-simulation-rules.bib`.
8. Write `rule-catalogue-simulation.md` (draft; one row per rule; no merging), cross-referenced
   to issue #20's `candidate-rule-catalogue.md`.
9. Write `category-summary.md` and `research-gap.md` from the collected entries only.
10. Write `search-log.md`; verify acceptance criteria one by one (workflow step 5b); PR.

## Progress log

### 2026-10-04 — Branch and work log created
- What I did: checked preconditions (`gh auth` OK, tree clean, remote correct), read the issue
  (no comments on it), cut the branch from `docs/20-game-theory-conflict-rules`, seeded this log.
- Why: workflow steps 0–3. Base choice explained in A1.
- Result / what I found: issue #20's catalogue (R1–R14) is on the parent branch and readable,
  so the cross-reference the issue asks for is possible.
- Next step: fetch the seed papers.

## Open questions / risks

- (to be filled as the work proceeds)

## Summary (fill in at the end)
