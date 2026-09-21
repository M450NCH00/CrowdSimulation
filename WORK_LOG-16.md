# Work Log — Issue #16: [Research] Literature: gender and age personas in LLM-to-LLM conflict resolution

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/16
**Branch:** `docs/16-demographic-personas-literature`
**Base branch:** `docs/14-deep-read-paper-summaries` (stack tip — `literature/` is not yet on `main`)
**Started:** 2026-09-21

## Understanding the issue

The FYP wants LLM agents to negotiate who yields in a spatial conflict (GameChat-style),
then distil a reusable resolution pattern. Phase 1's `run01` dataset already shows a
systematic effect: **female personas yield more than male personas** across many
scenario/age cells (`dataset/generated/validation_report.md`, "REVIEW" section, 54 items,
e.g. `bus_queue_boarding/child: yield_likelihood male=0.433 female=0.867, Δ=-0.43`).

The question this review must serve is **not** "is there a gender effect" — run01 already
shows one. It is: **is that effect realism or artifact?** Inside a transcript the two are
indistinguishable. They separate only by comparing the LLM effect against human evidence.
Hence the deliverable that matters is `realism-vs-bias-comparison.md`, and every other
file feeds it:

- B1/B2 (LLM side) → the left column: what effects LLMs show, how personas were specified,
  whether the persona did anything at all.
- B3/B4 (human side) → the right column: what real pedestrians and real disputants do.
- B5 → population composition, so a simulated crowd's demographic mix is defensible.

### Assumptions I am making (flagging per CLAUDE.md)

1. **Location scope = Singapore.** CLAUDE.md states "Scope confirmed 2026-09-04: dataset is
   Singapore-only, organised by age group and gender". B5 therefore targets Singapore
   sources. Recorded, not blocking.
2. **Base branch = `docs/14`, not `main`.** `main` contains no `literature/` directory at
   all; PRs #9 → #13 → #15 are a stack. Branching off `main` would make the PR diff
   unreadable against the literature it must not duplicate. This follows the convention
   already established by PRs #13 and #15.
3. **"Age" includes the persona age *bands* used in run01** (child, teenager, young adult,
   middle-aged, elderly), matching `dataset/personas.yaml`, when judging whether an LLM
   paper's age manipulation is comparable.

## Plan

1. Preconditions; read existing `literature/**` and all `refs.bib` files so nothing is
   re-collected. Record what is already present.
2. **Confirm the GameChat claim** the issue flags: that GameChat's agents carry no gender
   or age. Check the cached PDF text (`refs/mahadevan2025_gamechat.txt`) directly rather
   than trusting the existing summary.
3. Open every verified seed lead, one at a time. Confirm title/authors/year/venue/DOI from
   the page itself. Record peer-review status; for arXiv preprints, check for a published
   version.
4. Extract per templates L (B1/B2) and H (B3/B4). Locator on every number.
5. Fill gaps with targeted searches where a sub-area is short of 2 qualifying papers.
6. Verify the `[secondhand]` seed (Wang / Morgenstern / Dickerson) or report not found.
7. Build `realism-vs-bias-comparison.md`, including the run01 row.
8. B5: Singapore population composition sources.
9. `search-log.md`, including the novelty check.
10. Self-verify against §5b of `github_issue_workflow.md` and the issue's acceptance
    criteria, then PR.

## Progress log

### 2026-09-21 — Preconditions and scoping
- What I did: checked remote/auth/tree-clean; enumerated branches and PR bases; read
  `literature/paper-summaries/03-gamechat.md` and every existing `refs.bib`; pulled the
  gender findings out of `dataset/generated/validation_report.md`.
- Why: the issue forbids re-collecting papers already in the repo, and I needed the exact
  run01 numbers for the comparison table's run01 row.
- Result / what I found:
  - `main` has **no** `literature/` directory; all literature lives on the open PR stack
    #9 → #13 → #15. Branching off `docs/14` accordingly.
  - Existing bib coverage (must not duplicate): Rahim conflict-style instrument papers,
    CA-based verbal conflict papers (Putz, Toluei, Dersley, Garcia, Pomerantz,
    Rees-Miller), LLM multi-agent papers (GameChat, Shall We Team Up, Sense/Think/Act/
    Reflect, NegotiationArena, GovSim, Abdelnabi, Ashery), and pedestrian-dynamics papers
    (Yamamoto body rotation, Boomers data guidance, Echeverría-Huarte, Terwilliger, Jülich
    archive). **None of these are demographic-effect papers** — the overlap risk is low;
    the Rahim cluster is the one to cross-reference rather than re-enter, per the issue's
    B4 instruction.
  - run01's effect is large and consistent in direction: every flagged
    `yield_likelihood` delta is male < female, Δ ranging −0.27 to −0.43.
- Next step: verify the GameChat "no gender/age" claim from the cached full text.

## Open questions / risks

- **Location scope.** Recorded as Singapore per CLAUDE.md (assumption 1 above). If the
  supervisor widens the simulation beyond Singapore, B5 must be redone — demographic
  effects on conflict style are reported as culture-specific.

## Summary (fill in at the end)

<pending>
