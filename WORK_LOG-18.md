# Work Log — Issue #18: [Docs] Deep-read 5 demographic papers (age, gender) and produce evidenced summaries

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/18
**Parent issue:** [#16](https://github.com/M450NCH00/CrowdSimulation/issues/16)
**Branch:** `docs/18-demographic-paper-summaries`
**Base branch:** `docs/16-demographic-personas-literature` (stack tip)
**Started:** 2026-09-21

## Understanding the issue

Issue #16 produced *extraction-level* entries on these same five papers in
`literature/demographic-personas/`. #18 asks for something different and deeper: a
per-paper summary in the `literature/paper-summaries/` house style (continuing 01–06),
where every claim traces to a locator and where the **precision traps** the issue names
are handled explicitly.

The five precision traps are the real work here — they are all places where my own #16
entries are thinner than #18 requires:

1. **Paper 1 (Yeung & Ho)** — #16 recorded the indirect effects and the zero-order
   correlations. #18 wants **total, direct and indirect effects separated, per study, for
   each of the five strategies**. That is a different table and I have not read it yet.
2. **Paper 2 (Filsecker)** — #16 got the invariance result. #18 wants **measurement
   findings kept strictly apart from substantive findings**, and an explicit statement if
   no substantive gender differences are reported.
3. **Paper 3 (Borah & Mihalcea)** — #18 wants what "bias" is measured *against*.
4. **Paper 4 (Khaki & Choi)** — #18 wants the **full gender × race design**, with gender
   separated only where the paper separates it.
5. **Paper 5 (Liu et al.)** — #18 wants it framed as **values, not conflict behaviour**,
   and an exact record of what the LLM outputs were compared against.

Plus a cross-cutting requirement on Group L: state whether "bias" means **(a) departure
from equal treatment** (a fairness standard) or **(b) departure from real human behaviour**
(an accuracy standard). This is the distinction the FYP actually needs, and #16 did not
record it systematically.

### A constraint that changes how I write these files

The issue caps direct quotes at ~25 words and requires paraphrase elsewhere, because these
summaries may be reused in a Turnitin-checked report. **My #16 files quote heavily.** These
files must therefore be written differently from the ones I wrote yesterday — paraphrase by
default, quote only where exact wording carries the meaning (a construct definition, a
stated limitation). I will not copy text across from the #16 entries.

### Assumptions I am making (flagging per CLAUDE.md)

1. **Base branch = `docs/16-demographic-personas-literature`.** `#18` is a sub-issue of
   `#16` and needs both `literature/paper-summaries/` (from #14) and
   `literature/demographic-personas/` (from #16) present to avoid duplicating them. `main`
   has neither. This continues the established stack: #9 → #13 → #15 → #17 → this.
2. **All five papers are already cached** in `refs/` from #16, so no re-fetching is needed
   except where I find I need a better rendering (e.g. a PMC version with readable tables).
   Every claim is still re-verified against the paper, as the issue requires — the #16
   entries are treated as untrusted notes, not as a source.

## Plan

1. Preconditions; confirm all five cached sources are present and readable.
2. Re-verify peer-review status for Papers 3 and 5, preferring published versions.
3. Deep-read each paper *against its template*, taking the precision traps first, since
   those are the parts most likely to be wrong in my existing #16 notes.
4. Write summaries 07–11, paraphrase-first.
5. Build `extraction-table-demographics.md` with **no cross-paper equivalence**.
6. Build `reading-notes-demographics.md`, which is where comparison and judgement go.
7. `refs-demographics.bib`.
8. Verify: templates complete, locators present, existing files untouched, statistics
   unrounded.

## Progress log

### 2026-09-21 — Preconditions
- What I did: confirmed clean tree; branched from `docs/16-demographic-personas-literature`;
  confirmed all five papers are cached in `refs/` with usable text extracts.
- Why: #18 forbids summarising from an abstract, so I needed to confirm full text is in hand
  for all five before starting. It is.
- Result: all five present. Existing `literature/paper-summaries/` files 01–06,
  `extraction-table.md`, `reading-notes.md` and `refs.bib` noted as **must not be modified**.
- Next step: re-verify peer-review status for Papers 3 and 5, then read Paper 1's effects
  tables, which is the trap I am least confident about.

## Open questions / risks

<pending>

## Summary (fill in at the end)

<pending>
