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

### 2026-09-21 — Peer-review re-check, and an error found in my own issue #16 work
- What I did: re-checked peer-review status for Papers 3 and 5, as the issue requires.
- Why: #18 says published versions are to be preferred where they exist, and #16 had
  recorded one of these as a preprint.
- Result / what I found:
  - Paper 3 confirmed published at **Findings of EMNLP 2024**, as #16 had it.
  - ⚠ **Paper 5 is published at EMNLP 2024 main conference, pages 19617–19634,
    doi:10.18653/v1/2024.emnlp-main.1094.** My #16 entry records it as a `[preprint]` with
    no published version located. **That was wrong.** The cause: I relied on the arXiv
    Comments and Journal-reference fields, which the authors left empty, and treated their
    emptiness as evidence of absence.
  - Consequence beyond the label: the arXiv v4 I read for #16 is a **5-page** document,
    while the published paper spans 18 pages. **I had summarised a short version of a long
    paper.** I re-downloaded and read the published PDF for this issue.
- Next step: read Paper 1's effects tables — the precision trap I was least confident about.

### 2026-09-21 — Paper 1: the trap was real, and my #16 note was incomplete
- What I did: pulled the PMC rendering of Yeung & Ho to get cleaner tables, then worked
  through the total/direct/indirect distinction the issue demands.
- Result / what I found:
  - **Total (`c`) and direct (`c'`) effects are printed only inside Figures 1 and 2**, as
    path-diagram labels. They are in no table and not in the body text. I have recorded
    this plainly rather than guessing at values.
  - **But the text does state the Study 1 direct effects qualitatively**, and they matter:
    direct effects appeared only for obliging and avoiding, and **younger** employees used
    those two passive strategies *more*. The authors flag this as a failure to replicate
    earlier work, and explain it by Hong Kong workplace power distance and respect for
    elders.
  - **This runs opposite to the paper's own abstract**, which reports only the mediated
    result (older → more obliging/avoiding through perceived limitations). Anyone citing
    the abstract alone would get the wrong direction.
  - Study 2 has **no zero-order age effect at all**, linear or quadratic (r from −0.02 to
    0.07) — a contrast with Study 1 that the abstract's "largely replicated" glosses over.
  - Recovered the full Table 1 and Table 2 correlation matrices, including the gender
    columns, which give exact numbers for the null gender result #16 only described.
- Next step: Paper 2.

### 2026-09-21 — Paper 2: my #16 entry had missed the main result
- What I did: read the Filsecker manuscript properly rather than for its invariance result.
- Result / what I found:
  - **The five-factor ROCI-II did not survive in this adolescent sample.** The paper's
    actual outcome is a **revised 17-item, three-factor** instrument — Integrating,
    Dominating, Avoiding. The Obliging items loaded on Integrating and were removed;
    Compromising did not survive either. **My #16 entry did not record this at all**, and it
    changes what the invariance result means: invariance was established for the *revised*
    instrument, not the standard one.
  - **Obliging is the Rahim style closest to yielding, and it is the one that disappeared.**
    That is directly relevant to the FYP and I had missed it.
  - Confirmed there are **no substantive gender differences reported anywhere** in the
    paper, as the issue asked me to check explicitly.
  - Recorded the full invariance fit-index tables for gender and grade, including the 9th
    grade baseline that failed (CFI .828, TLI .793).
  - Logged several internal inconsistencies in the accepted manuscript: two tables both
    numbered 4, a text/table mismatch on the PTS correlations, an undefined scale "RES"
    with a value appearing in no table, and conflicting sub-sample counts.
  - The manuscript has **no Limitations section**; recorded as `[not stated in paper]`
    rather than invented.
- Next step: Papers 3, 4, 5.

### 2026-09-21 — Paper 3: recovered the table #16 said was unreadable
- What I did: re-extracted the PDF in reading order rather than layout-preserving order.
- Why: my #16 entry carries a caveat that Table 1 could not be read because the two-column
  layout merges the MODEL and SETTING columns, and warns anyone citing a cell to re-read
  the PDF. That caveat was worth trying to remove.
- Result: the reading-order extraction emits each column as a complete list, so the 15 rows
  could be reassembled by position. **I then cross-checked the reconstruction against five
  prose claims made independently of the table** — the all-positive claim, the
  all-conditions-increase claim, the gpt-4-highest claim, the no-interaction model ordering,
  and the goal-setting-lower-first-response claim which holds for two models but not gpt-4.
  All five check out. The full table is now in summary 09 with the method and the caveat
  recorded.
- Also determined what "bias" is measured against: **standard (a), equal treatment** — the
  score's zero point is defined as tasks evenly distributed across genders, and the paper
  places its metric beside demographic parity.

### 2026-09-21 — Paper 4: gender/race separation, and an inconsistency I could not resolve
- What I did: worked through the full gender × race design as the issue requires.
- Result / what I found:
  - Gender is separated from race in §4.1 and §4.2, and I report those separately. **§4.3
    reports only combined gender-by-race cells**, so I state that and extract no gender-only
    effect from it, rather than attempting to disentangle.
  - ⚠ **Condition count is internally inconsistent**: §3.2 says nine gender/race permutations
    including a baseline, giving 540 runs; §4.1 describes six subpopulations plus a baseline,
    which is seven. Reported as printed; unresolved.
  - **Correction to my #16 entry:** I wrote there that no confidence intervals or
    significance tests are reported. That is too strong — §3.2 does specify 95% CIs via
    Equation (1). The accurate statement, which is what summary 10 now says, is that I did
    not find an interval attached to the headline $5.47/$4.97 gender contrast in §4.1.
  - Confirmed the §4.2 internal contradiction ($12.56 vs $12.57 described as female
    benefiting more) that #16 had already flagged.

### 2026-09-21 — Paper 5, and the extraction table's no-synthesis rule
- What I did: read the published EMNLP version; wrote summary 11 framed strictly as values
  rather than conflict behaviour, per the issue.
- Result: recorded the comparison data exactly — WVS wave 7, 94,000 respondents, 13
  categories, 372 value vectors across 62 countries and six age groups, six LLMs, eight
  prompt variants per inquiry. Noted that this is the **only** Group L paper of the three
  whose "bias" standard is **(b) real human beliefs** — and that its claim is deliberately
  about relative inclination, not resemblance to any cohort, a qualification the authors
  state twice and which the title invites readers to overshoot.
- Decision point on the extraction table: the issue forbids cross-paper equivalence there.
  The risk is subtler than it first looks, because several papers share vocabulary —
  "avoiding" appears in Papers 1 and 2 as a Rahim subscale and nowhere in Papers 3–5. I
  added an explicit warning at the top of the table that shared words are not shared
  constructs, and pushed every comparison into the notes file.

### 2026-09-21 — Verification pass
- What I did: checked all five summaries have every template section (12 each, none blank);
  checked existing files 01–06, `extraction-table.md`, `reading-notes.md` and `refs.bib` are
  untouched by `git status`; checked all internal links resolve; checked all five BibTeX
  keys are defined; ran a script to find quotes over the issue's ~25-word cap.
- Result: all pass. The quote script initially flagged three hits in the extraction table,
  which on inspection were regex artifacts spanning *between* two separate short quotes
  rather than single long quotes. Re-ran per quoted span: the longest single quote anywhere
  in the deliverables is **12 words**.

## Open questions / risks

- **⚠ Issue #16's files still contain the Paper 5 preprint error.** The corrected entry is
  in this issue's `refs-demographics.bib`, and the error is documented in
  `reading-notes-demographics.md` §6 item 10. But
  `literature/demographic-personas/llm-demographic-effects.md` and its `refs.bib` still say
  `[preprint]`. **I did not edit them**, because they belong to PR #17, which is open, and
  amending another PR's files from a child branch would make that review harder. **Someone
  needs to fix them** — either on PR #17 before merge, or in a follow-up.
- **⚠ Issue #16's entry for Paper 2 is materially incomplete**, for the same reason: it does
  not record that the five-factor structure failed and was replaced by a 17-item
  three-factor version. That is not a wrong statement, but it omits the paper's main result.
  Same disposition as above.
- **Paper 1's total and direct effects are unread.** They exist only inside Figures 1 and 2.
  A reader with the figures could supply the numbers in about ten minutes; I could not, and
  summary 07 says so in place. **This is the largest single gap in these five summaries**,
  because the direct effects are the ones that contradict the abstract.
- **Paper 2's inconsistencies are unresolved** because I read the accepted manuscript. Most
  are probably artifacts of that version, but the page range (525–536 vs 526–536) and the
  sub-sample counts (471/535 vs 464/534) should be checked against the Hogrefe version
  before any of those numbers is cited.
- **Paper 4's condition count is unresolved** (nine vs six-plus-baseline).
- **No paper in this set puts an age persona into a contested interaction**, and `run01` is
  organised primarily by age band. This is recorded as gap 4 in
  `reading-notes-demographics.md` and is, in my view, the most consequential gap for the
  project.
- **No human evidence in this set covers `run01`'s `child` band**, and none covers the
  elderly in a conflict setting. The human samples span roughly 14–16 (Paper 2) and 20–68 /
  23–66 (Paper 1).
- **Replication status of all three Group L papers is unknown.** Two are venue-fresh and one
  uses a single model. Weight accordingly.

## Summary

**What changed.** Added eight files to `literature/paper-summaries/`, continuing the
existing numbering without touching 01–06:

- `07-older-workers-conflict-management.md` (Template H)
- `08-roci-ii-adolescents.md` (Template H)
- `09-implicit-bias-multi-agent.md` (Template L)
- `10-fairness-llm-negotiator.md` (Template L)
- `11-generation-gap-age-bias.md` (Template L)
- `extraction-table-demographics.md` (Part 2, no synthesis)
- `reading-notes-demographics.md` (Part 3, all judgement)
- `refs-demographics.bib` (5 entries, separate from the existing `refs.bib`)

Plus newly cached sources under `refs/` (`p18_*`).

**Why.** Issue #16 produced extraction-level notes on these same five papers. #18 asked for
deep reads with every claim located, and named five precision traps. Working through those
traps turned up **three substantive errors or omissions in my own #16 work**: Paper 5's
peer-review status, Paper 2's main result, and an over-strong claim about Paper 4's
statistics. It also let me recover Paper 3's Table 1, which #16 had marked unreadable.

**How it was verified** (no test suite; §5b of `github_issue_workflow.md`):
- All five papers read in full; none summarised from an abstract.
- Citation metadata confirmed from the paper itself plus one authoritative metadata source
  (ACL Anthology BibTeX export or Crossref), all cached under `refs/`. Version read is
  recorded for each, including the two read in a version that is not the version of record.
- Every template section filled; nothing left blank. Where a paper does not state something,
  it is marked `[not stated in paper]` rather than inferred — this applies to Paper 2's
  limitations, Paper 1's Study 2 direct effects, and Paper 5's turn structure.
- Statistics reported exactly as printed, including two sets of numbers that contradict
  their own surrounding text (Paper 2's PTS correlations, Paper 4's §4.2 figures).
- Quote cap verified by script and by inspection: longest single quote is 12 words.
- Existing files 01–06, `extraction-table.md`, `reading-notes.md` and `refs.bib` confirmed
  untouched via `git status`.
- All internal links resolve; all five BibTeX keys defined and used.

**What I did not do.** No new papers searched for, no LLM run, no experiment, no edits to
`literature/demographic-personas/realism-vs-bias-comparison.md` — all out of scope per the
issue. Suggested changes to that file are recorded in `reading-notes-demographics.md` §1
instead, as the issue directs.
