# Work Log — Issue #14: [Docs] Deep-read 6 selected papers and produce evidenced summaries

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/14
**Branch:** `docs/14-deep-read-paper-summaries`
**Started:** 2026-09-20

## Understanding the issue

Six papers have been selected as the core of the FYP's validation argument — three on
what **LLM agents** do when resolving conflict, three on what **humans** do when
resolving conflict through talk. Each needs a summary in which **every factual claim
carries a locator** (section, page, table or figure), read from the paper itself rather
than from an abstract, a search result, or memory.

Three deliverable types: six per-paper files (two templates, by group), an
`extraction-table.md` that records what each paper says **without mapping categories
across papers**, and a `reading-notes.md` for my own observations — tensions, gaps, a
**novelty check** on each Group 1 paper, and my own methodological concerns kept separate
from the authors'.

The rules that shape the work:
- read the cached copy in `refs/` or fetch the PDF; no abstract-only summaries unless the
  paper is genuinely inaccessible, in which case say so and mark the boundary;
- quotes under ~25 words, quoted and located; everything else paraphrased;
- `[not stated in paper]` / `[none reported]` rather than inference or blanks;
- confirm citation metadata **from the paper itself**, since several were found via
  search.

### Assumptions (flagged per CLAUDE.md)

1. **Base branch.** The issue names `docs/12-human-conflict-resolution-literature`
   (PR #13, open). I branched from its tip so the PR diff contains only issue #14's work,
   and will target the PR at that branch. If PR #13 merges first, retarget.
2. **One cached file imported across branches.** `refs/zhang2026_dfd.pdf` (+ `.txt`) was
   cached on the issue #10 branch, which has since merged into `docs/8`. I checked those
   two files into this branch rather than merging `docs/8` wholesale, to keep the diff to
   this issue's work. The paper is CC-BY, so redistribution is fine.
3. **Page locators.** `pdftotext -layout` preserves page breaks, so page numbers are
   computed from the extracted text and cross-checked against the printed page numbers in
   the PDF where they appear. Section numbers come from the paper's own headings.

## Plan

1. Branch + work log (this file), commit.
2. Confirm which of the six are already cached in full text (expect 4 of 6: Wu, Zhang,
   GameChat, Rahim & Magner) and re-attempt access for the two that were blocked during
   issue #12 (Pütz & Hassan; Toluei & Tahririan).
3. Read each accessible paper properly, building locators as I go.
4. Write the six summary files using the correct template per group.
5. Write `extraction-table.md` — verbatim terminology, no cross-paper mapping.
6. Write `reading-notes.md` — tensions, gaps, novelty check for all three Group 1 papers,
   my own concerns separated from the authors'.
7. `refs.bib`; verify per workflow §5b (every section filled, every claim located);
   push; PR against the issue #12 branch.

## Progress log

### 2026-09-20 — branch created, work log seeded
- What I did: confirmed `#13` is the pull request for issue #12, not an issue, so this is
  issue **#14**. Branched from `docs/12-human-conflict-resolution-literature`; imported
  the cached Zhang PDF; removed a stale `refs/sage_73785_chapter.pdf` (an HTML error page
  saved with a `.pdf` extension during issue #12).
- Why: the issue names that branch, and four of the six papers are already cached there
  or on the merged issue #10 work.
- Result / what I found: full text available locally for 4 of 6 — Wu (1,448 lines
  extracted), Zhang (2,079), GameChat (617), Rahim & Magner (861). Papers 5 and 6 were
  blocked by publishers during issue #12 and need another attempt.
- Next step: re-attempt Pütz & Hassan and Toluei & Tahririan, then start reading.

## Open questions / risks

_(filled in as work proceeds)_

## Summary (fill in at the end)

_(pending)_
