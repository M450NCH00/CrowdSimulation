# Work Log — Issue #12: [Research] Literature: how humans resolve conflicts through talk, codeable strategies for validating LLM conflict resolution

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/12
**Branch:** `docs/12-human-conflict-resolution-literature`
**Started:** 2026-09-19

## Understanding the issue

The FYP needs to answer: *when two LLM agents resolve a conflict by talking, is the
strategy they used one that real people actually use?* To answer that, the project needs
a **coding scheme** — a named set of human conflict-resolution strategies that a
transcript can be classified against — not more descriptive conflict theory.

The issue's selection test is the whole filter: *given an LLM transcript, which category
from this paper would be assigned, and on what textual evidence?* If a paper cannot
answer that, it is excluded, however relevant it sounds.

Two properties raise a paper's value:
1. **Frequency / base rates** — how often humans use each category, so an LLM's
   distribution can be compared against a human one rather than just "possible".
2. **Inter-rater reliability** (kappa, % agreement) — so the coding can be defended.

Sub-areas: A1 conflict-style taxonomies, A2 conversation analysis of disagreement
(including non-resolution), A3 interaction coding schemes for conflict talk,
A4 dispute resolution / mediation, A5 (optional, short) LLM-assisted qualitative coding.

Deliverables: `verbal-conflict-resolution.md`, `candidate-coding-scheme.md`,
`modality-note.md`, `refs.bib`, `search-log.md` under
`literature/human-conflict-resolution/`.

### Assumptions (flagged per CLAUDE.md)

1. **Base branch.** The issue names `docs/8-lit-review-llm-conflict-resolution`. That
   branch is still unmerged (PR #9), and this issue's deliverables build on its
   conventions, so I branched from its tip (`c87153b`) and will target the PR at it.
   Issue #10's branch is a separate stack and is not involved.
2. **Conventions inherited from issues #2 and #8.** Same house style: per-entry
   template, `[unverified]` / `[needs verification against full text]` markers,
   `[non-archival]` on preprints, sources cached under `refs/`, dead ends recorded in
   `search-log.md`.
3. **Caching.** Where a publisher blocks automated fetches, I record the block in
   `search-log.md` rather than quietly citing an unverified page.

## Plan

1. Branch + work log (this file), commit.
2. Read the Pütz paper first — the issue says it is the closest fit (termination formats
   plus frequency data).
3. Work through the remaining verified seeds, then the `[secondhand]` seeds, opening each
   independently. Anything not found gets recorded as not found.
4. Search the sub-areas A1–A4 for 2016–2026 work, applying the codeability test to every
   candidate; A5 last and briefly.
5. Cache every source to `refs/`; record queries, hits, rejections and blocks in
   `search-log.md`.
6. Write `verbal-conflict-resolution.md` grouped by sub-area, then synthesise
   `candidate-coding-scheme.md` (labels kept side by side, never merged), then
   `modality-note.md` and `refs.bib`.
7. Verify per workflow §5b; push; open PR against the issue #8 branch.

## Progress log

### 2026-09-19 — branch created, work log seeded
- What I did: read issue #12 and `github_issue_workflow.md`; confirmed a clean tree;
  branched from `docs/8-lit-review-llm-conflict-resolution` (`c87153b`).
- Why: the issue names that branch, and its `refs/` cache and house style are the
  conventions this review follows.
- Result / what I found: 4 verified seeds + 5 `[secondhand]` seeds to check, across 5
  sub-areas.
- Next step: read the Pütz paper.

## Open questions / risks

_(filled in as work proceeds)_

## Summary (fill in at the end)

_(pending)_
