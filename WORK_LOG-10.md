# Work Log — Issue #10: [Docs] Select papers for FYP introduction + Draft sample introduction (Assignment 1)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/10
**Branch:** `docs/10-intro-paper-selection-draft`
**Started:** 2026-09-13

## Understanding the issue

After the second supervisor meeting the research question is: *can LLMs resolve
conflicts by communicating with each other, and does that communication contain a
reusable pattern* that a crowd simulation can apply later without re-running the
LLM-to-LLM exchange? Assignment 1 needs an introduction built on that question.

The issue has two parts:

1. **Paper selection** — choose 3–5 papers **only** from the issue #8 literature review
   (`literature/llm-conflict-resolution/`) that together cover Background, Research gap
   and Study introduction, then write an honest coverage assessment. If coverage is
   insufficient, stop and write `open-gaps.md` only.
2. **Introduction draft** — ≤12-word title, ≤500-word body, IEEE referencing, fixed
   three-part structure, every factual claim cited, no web search, no fabricated
   findings, uncertain support marked `[needs verification against full text]`.

`open-gaps.md` is always produced.

### Assumptions (flagged per CLAUDE.md)

1. **Base branch.** The workflow says branch from `main`, but the literature this issue
   must draw on exists only on `docs/8-lit-review-llm-conflict-resolution` (PR #9, not
   merged). The issue itself names that branch. I branched from its tip (`c87153b`) and
   the PR will target that branch so the diff contains only issue #10's work.
2. **Deliverable location.** The issue gives filenames but no directory. I am placing
   them in `literature/llm-conflict-resolution/assignment1-intro/`, next to the sources
   they cite. Trivial to move if the user prefers a different folder.
3. **What counts as a "source".** The review files summarise papers, but where a full
   text is cached in `refs/` (Wu et al., GameChat, Moeller et al.) I check claims against
   that text as well, not just the summary. This is still inside the sourcing rule, since
   these are the files the review itself cites, and no new papers are introduced.

## Plan

1. Branch + work log (this file), commit.
2. Read both topic files, `refs.bib` and the issue #8 work log; list every candidate
   paper against the three introduction components.
3. Re-check every finding I intend to use against the cached primary source in `refs/`,
   not just against the review's summary. Record any discrepancy.
4. Select 3–5 papers; write `paper-selection.md` with the per-paper template and an
   honest coverage assessment.
5. If coverage is sufficient, draft `introduction-draft.md`; count words mechanically;
   run the issue's quality checklist line by line.
6. Write `open-gaps.md` (always).
7. Verify per workflow §5b; update README status; push; open PR against the issue #8
   branch.

## Progress log

### 2026-09-13 — branch created, work log seeded
- What I did: read issue #10 and `github_issue_workflow.md`; confirmed the working tree
  was clean and `docs/8-lit-review-llm-conflict-resolution` matched its remote; created
  `docs/10-intro-paper-selection-draft` from it.
- Why: the literature is not on `main` yet (see Assumption 1).
- Result / what I found: 14 papers in the review (12 in the 2016–2026 window + 2
  supervisor-assigned); full text cached for 3 of them (Wu, GameChat, Moeller).
- Next step: map candidates to introduction components and re-check claims against
  `refs/`.

### 2026-09-13 — claims re-checked against cached sources; 5 papers selected
- What I did: mapped all 14 review papers to the three introduction components.
  Re-checked every finding I intended to use against `refs/`: Wu full text (§1,
  §6.1–6.2, Table 2, Limitations), GameChat v2 full text (§I, §IV-C, §IV-E, §V-B,
  Table III), Moeller article HTML (Results, Fig. 2A, participants), and the Ashery,
  Zhang and Wang abstracts. Wrote `paper-selection.md`.
- Why: the issue forbids extrapolating findings, and the review's summaries are
  secondary, so a claim is only as good as the primary text behind it.
- Result / what I found:
  - **Selected:** Wu [1], Zhang-DFD [2], GameChat [3], Ashery [4], Moeller [5].
  - **Discrepancy in the issue #8 review:** it says GameChat evaluated only 2 agents,
    but cached arXiv v2 has 3/4/5-agent results (Table IV). Recorded in
    `paper-selection.md`; I did not edit the issue #8 file, which is out of scope here.
  - **Moeller percentages are derived.** The paper states counts (10, 5 and 4 of 19);
    26% and 21% are the review's rounding. The draft uses counts.
  - **Hard choice:** Wang 2015 is the only paper that says *why* crowd simulation
    matters, but a sixth reference breaks the cap. I kept Wu because it gives
    full-text-verified cost evidence for the gap. The alternative is recorded.
  - **Framing decision:** Zhang-DFD already distils LLM behaviour into rule code for
    crowd evacuation, so the gap cannot honestly be "nobody extracts patterns". It is
    stated as "not from LLM-to-LLM conflict dialogue, and not checked against humans",
    and the human-validation half rests on an abstract, so it carries
    `[needs verification against full text]`.
- Next step: coverage is sufficient (with that condition), so draft the introduction.

## Open questions / risks

_(filled in as work proceeds)_

## Summary (fill in at the end)

_(pending)_
