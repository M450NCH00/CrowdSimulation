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

### 2026-09-19 — seeds verified; two of the issue's seeds were wrong
- What I did: verified every seed independently. Publisher pages were almost all blocked
  (John Benjamins, T&F, SAGE, Wiley, Elsevier, JSTOR all returned 403 or paywalls), so I
  used Crossref, OpenAlex and Semantic Scholar API records, plus open-access PDFs where
  they existed, and recorded the route per entry.
- Why: the issue forbids listing anything seen only in another paper's reference list,
  and forbids reporting findings not read from a source.
- Result / what I found:
  - **The Greatbatch & Dingwall seed is misattributed.** "Dispute Resolution without
    Disputing: How the Interactional Organization of Mediation Hearings Minimizes
    Argument" is by **Angela Cristina Garcia**, single-authored, *American Sociological
    Review* 56(6):818-835 (1991). Crossref and OpenAlex agree. Greatbatch and Dingwall
    have their own mediation work, but not this paper.
  - **The Pütz seed has a second author** — Pütz **& Hassan**, 2024, JLAC 14(2):199-228.
  - Sillars et al. 1982: the publisher page lists **four** authors; Crossref lists three.
    Took the publisher page as correct.
  - Dersley & Wootton, Rees-Miller and Pomerantz confirmed as real; the latter two had
    no retrievable abstract, so no findings are claimed from them.
- Next step: fill the sub-areas the seeds do not cover.

### 2026-09-19 — full texts obtained where possible; A3 is the thin sub-area
- What I did: chased open-access copies. Four full texts were obtained and text-extracted:
  Rahim & Magner (1995) CFA, the KODIS corpus paper, and the two arXiv A5 papers; plus
  the Caughlin & Vangelisti (2006) handbook chapter, used only for the modality note.
- Why: abstracts give category *names* but not definitions, counts, or reliability.
- Result / what I found:
  - **Rahim & Magner 1995 was the key get.** Rahim's 1983 abstract never names the five
    styles, so without it the taxonomy would have rested on my own memory. The 1995 paper
    defines all five verbatim, gives the reliability figures, and quotes
    Weider-Hatfield's "three, not five" conclusion. The draft flags that the quotation was
    read there and not in Weider-Hatfield's own text.
  - **KODIS gives the best base rate in the review**: ~18% of human text-chat dyadic
    disputes ended in impasse, against 3.5% in a deal-making corpus. That is the natural
    comparison for how often LLM agents fail to resolve.
  - **CACS could not be opened.** A web-search summary offered a partial category list;
    I did not use it, because it is not an opened source. Recorded as the highest-value
    retrieval.
  - **A3 is thin and is reported as thin** — one scheme (VTCS) at its coarsest three-class
    level, no reliability figure, manual not obtained. I did not pad it.
- Next step: write the deliverables.

### 2026-09-19 — deliverables written and checked
- What I did: wrote the five files, then ran mechanical checks: every `refs/` file
  referenced exists (13/13), every BibTeX key cited is defined (12/12, no dangling), and
  every entry carries all 12 template fields.
- Why: workflow §5b.
- Result / what I found: 12 entries; A1-A4 all covered, A5 short as instructed. 10
  `[needs verification against full text]` markers, all on things an abstract could not
  supply. Removed `refs/sage_73785_chapter.pdf`, a download that returned HTML rather
  than a PDF.
- Next step: push and open the PR.

## Open questions / risks

- **Most entries are abstract-level, not full text.** Eight of the twelve rest on
  Crossref/OpenAlex/Semantic Scholar records because publishers blocked access. That is
  stated per entry, but it means the review reports *category names* far more reliably
  than *category definitions*, *counts* or *reliability figures*. Anyone relying on this
  for the report should pull the five full texts listed at the end of `search-log.md`.
- **No human-behaviour entry reports inter-rater reliability.** Only the A5 method papers
  do. A coding scheme with no published reliability is exactly what the issue warned
  leaves the coding open to challenge. Retrieving the VTCS manual and the Pütz & Hassan
  full text is the way to close this.
- **The CACS gap is the biggest single hole.** It was designed for coding argument in
  conversation, which is precisely this project's need, and it could not be opened.
- **Merging labels is a judgement I deliberately did not make.** `obliging` /
  `submission` / `relinquishing a position` look like the same thing and are presented
  side by side, unmerged, with the reasons they may not be. This needs supervisor
  sign-off before any coding starts.
- **Rahim's five styles are a questionnaire instrument, not a transcript scheme.** Using
  them to code talk is an extension. Weider-Hatfield argues the factor structure is
  wrong anyway. I kept them as an optional layer rather than the backbone.
- **The modality gap is real and only partly sourced.** I found evidence that verbal and
  affective coding of the same conflicts can diverge (via Caughlin & Vangelisti), but
  nothing that directly compares verbal and non-verbal resolution of a *passing* conflict.
  The nearest evidence is Yamamoto et al. (2019), already in the repo from issue #8.
- **One quotation is second-hand by necessity** — Weider-Hatfield's "three, not five"
  (p. 364), read in Rahim & Magner. Flagged in place.
- **Pike & Sillars (1985)** is cited in `modality-note.md` as reported by Caughlin &
  Vangelisti, not opened. Flagged in place.

## Summary

**What changed.** Added `literature/human-conflict-resolution/` with
`verbal-conflict-resolution.md` (12 entries, grouped A1-A5, full template each),
`candidate-coding-scheme.md` (draft, pending supervisor approval), `modality-note.md`,
`refs.bib` (17 keys) and `search-log.md`; cached ~30 new source files under `refs/`.
No code, no dataset work.

**What the review yields.** Three layers a transcript can be coded at:
- **L1 tactic per utterance** — avoidance / integrative / distributive (Sillars et al.
  1982, built for conflict transcripts);
- **L2 how the episode ended** — submission / stand-off / compromise (Pütz & Hassan
  2024), and closure acts relinquishing-a-position / acknowledging-repair, plus
  non-resolution (Toluei & Tahririan 2022);
- **L3 outcome** — agreement vs impasse (KODIS).
Plus an optional, contested **L0 style** layer (Rahim's five).

**Base rates found** (the property the issue prioritised): submission > stand-off >
compromise; most conflicts end after two or three disagreements; ~18% of human text-chat
disputes end in impasse; 136 strategic interruptions across 23 mediation sessions.

**Corrections to the issue's own seeds:** the ASR mediation paper is by Garcia, not
Greatbatch & Dingwall; the Pütz paper has a second author (Hassan).

**How it was verified** (workflow §5b):
- **Template completeness checked mechanically** — all 12 entries carry all 12 fields.
- **BibTeX cross-checked** — 12 cited keys, 0 dangling; the 5 extra keys are the
  not-usable and supporting works, each labelled as such in the file.
- **Cache references checked** — all 13 `refs/` paths named in the deliverables exist.
- **Every number traced** to an opened source or marked `[needs verification against full
  text]` (10 markers).
- **Frequency data and inter-rater reliability recorded for every entry**, including
  "none reported" where absent — which is most of them.
- **Dead ends recorded, not hidden** — 7 blocked publishers, 5 unreachable items, and 5
  candidates rejected for failing the codeability test, all in `search-log.md`.
- **Nothing cited secondhand:** the CACS category list that surfaced in a search-result
  summary was deliberately not used, because no CACS source could be opened.
