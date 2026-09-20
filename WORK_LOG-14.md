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

### 2026-09-20 — access re-attempted; 4 of 6 readable in full
- What I did: re-attempted the two papers blocked during issue #12. John Benjamins
  (article and catalogue pages) and IngentaConnect both returned 403 for Pütz & Hassan;
  Taylor & Francis returned 403 for Toluei & Tahririan; no repository copy exists for
  either.
- Why: the issue forbids summarising from an abstract unless the paper is genuinely
  inaccessible, so I had to establish that it is.
- Result / what I found: **one real gain** — the ERIC record (EJ1402229) carries the
  *complete* abstract for Toluei & Tahririan, including the two non-resolution
  conditions that the Semantic Scholar copy used in issue #12 had truncated
  mid-sentence. Papers 05 and 06 are written as abstract-only with the boundary marked.
- Next step: read the four accessible papers and build locators.

### 2026-09-20 — deep reading; three metadata findings
- What I did: read Wu et al., Zhang et al., GameChat and Rahim & Magner in full from the
  cached PDFs, using a small helper that maps a search hit to its PDF page via form-feed
  counting, then cross-checked against the printed page numbers in each paper.
- Why: every claim needs a locator, and page numbers guessed from a text extract would
  not survive checking.
- Result / what I found:
  - **GameChat version problem.** The cached PDF is **arXiv v2, 9 May 2026**, and it
    states **no venue**; the cached arXiv page has no Comments or Journal-reference
    field either. A published IEEE MRS version does exist
    (doi:10.1109/MRS66243.2025.11357267, issued 4 December 2025), confirmed from
    Crossref — so **the preprint I read is four months newer than the published paper**.
    Issue #8's `refs.bib` cites it as "IEEE MRS 2025" without recording that the text
    consulted was the preprint. Flagged in the summary, in `refs.bib` and in the notes.
  - **Zhang et al. authorship.** All four authors are at NTU, not two as
    `literature/llm-conflict-resolution/topic1-llm-conflict.md` says.
  - **Wu et al. do validate against human data — but only in one case study.** The
    Keynesian Beauty Contest is compared against a New York Times experiment with
    N = 61,140 (§4.2, p. 5168); the evacuation case has no human comparison, and the
    authors say better metrics are future work (§7, p. 5171). The Conclusion's blanket
    "aligns well with real-world data" (§8, p. 5171) is broader than the EE evidence.
  - **pdftotext misaligns Zhang's Tables 3 and 4** (bolded cells shift rows), so those
    values were read from the rendered PDF pages, not the text extract. Noted in the
    summary file.
- Next step: write the six summaries, the extraction table and the notes.

### 2026-09-20 — deliverables written and checked
- What I did: wrote six summary files (correct template per group), `extraction-table.md`,
  `reading-notes.md` and `refs.bib`. Then ran mechanical checks: every template section
  present in every file; BibTeX keys cited vs defined; a scan for quotes over the ~25-word
  limit.
- Why: workflow §5b and the issue's acceptance criteria.
- Result / what I found: **five quotes exceeded ~25 words** (the NYT sentence in Wu, three
  passages in GameChat, one in Toluei). Each was cut to a short quote with the surrounding
  wording paraphrased. All six files carry every section; 0 dangling BibTeX keys; locator
  counts range from 134 (Zhang) down to 10 and 12 for the two paywalled papers, where the
  only available locator is "Abstract".
- Next step: push and open the PR.

## Open questions / risks

- **Half the human-side evidence is abstract-only.** Papers 05 and 06 could not be opened.
  Their category *definitions* and coding procedures are unread, so the project should not
  finalise a coding scheme on them. Both files mark the boundary explicitly.
- **The novelty finding needs to reach the supervisor now.** GameChat already has two LLM
  agents resolving a doorway conflict by dialogue (§IV-C, p. 4; Table III, p. 6), and DFD
  already extracts a reusable decision function from LLM-driven crowds (§4.4, p. 11).
  Neither does both, and neither validates against human behaviour — so the FYP's
  defensible claim is the conjunction, stated narrowly. Written up in `reading-notes.md`
  §3.
- **The GameChat citation in this repo is currently imprecise.** Earlier files cite the
  IEEE MRS 2025 venue while the text everyone has read is the newer arXiv v2. Section and
  table numbers may not match the published version. Fixing the other files is out of
  scope for this issue; flagged instead.
- **Zhang et al.'s ground truth is Gemma3:27b** (§5.1, p. 13) while the simulation design
  it borrows is Wu et al.'s GPT-4 setup (§4, p. 5166). "Reproduces LLM crowd behaviour"
  therefore means one model's behaviour in another's setup. Recorded as tension T5.
- **Rahim's five styles have no transcript procedure.** The instrument assigns scores from
  28 self-report items (p. 123). Applying the labels to dialogue is an extension, not a
  validated use.
- **Table values for Zhang were read from the rendered PDF, not the text extract**, because
  `pdftotext` misaligns bolded cells. Anyone re-checking should look at pp. 17 and 19 of
  the PDF rather than the `.txt`.
- **No cross-paper category mapping was performed**, as instructed. That means the
  extraction table deliberately leaves "obliging", "submission" and "relinquishing a
  position" unconnected. The mapping decision is still pending and blocks the synthesis
  issue that depends on this one.

## Summary

**What changed.** Added `literature/paper-summaries/` with six per-paper summaries
(`01`–`06`), `extraction-table.md`, `reading-notes.md` and `refs.bib`; imported
`refs/zhang2026_dfd.pdf`/`.txt` from the merged issue #10 work; removed a stale
`refs/sage_73785_chapter.pdf`. No code, no dataset work.

**Access reality.** Four papers read in full (Wu; Zhang; GameChat arXiv v2; Rahim &
Magner). Two are paywalled (Pütz & Hassan; Toluei & Tahririan) and are summarised from
their abstracts with the boundary stated at the top of each file — for Toluei the
*complete* abstract was obtained from ERIC, which fixed a truncation carried over from
issue #12.

**Three findings worth the supervisor's attention:**
1. **Novelty is narrower than it looks.** GameChat does the dialogue half; DFD does the
   extraction half. The FYP's claim has to be the conjunction plus human validation
   (`reading-notes.md` §3).
2. **A version/citation hazard.** The GameChat text in this repo is arXiv v2 (May 2026),
   newer than the IEEE MRS version (December 2025) that the repo cites.
3. **Wu et al.'s human-data validation covers KBC only**, not the evacuation case study
   that this project actually draws on.

**How it was verified** (workflow §5b):
- **Template completeness checked mechanically** — all six files carry every section of
  their group's template; nothing left blank (`[not stated in paper]`, `[none reported]`
  and `[not accessible]` used instead).
- **Locators**: 92 (Wu), 134 (Zhang), 119 (GameChat), 36 (Rahim & Magner) section/page/
  table references; 10 and 12 for the paywalled pair, where "Abstract" is the only
  honest locator.
- **Quote limit enforced by script** — five over-length quotes found and trimmed; zero
  remain above ~25 words.
- **BibTeX** — six keys defined, six cited, none dangling.
- **Metadata confirmed from the papers themselves** for the four readable ones, and
  explicitly marked as record-confirmed for the two that are not.
- **Inference marked** — 16 `[inference]` tags across the six files, separating my
  judgements from the papers' claims; my methodological concerns are kept in
  `reading-notes.md` §4, away from the authors' own stated limitations.
