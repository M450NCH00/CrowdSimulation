# Work Log — Issue #4: [Docs] Compile literature review README (papers 1, 2, 3, 7)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/4
**Branch:** docs/4-literature-readme (based on `docs/2-lit-review-llm-human-behaviour`)
**Started:** 2026-09-07

## Understanding the issue

`literature/papers.md` (produced by issue #2) holds seven full review entries in a
dense, template-driven format aimed at *me* re-checking claims. This issue asks for a
different artefact from a **subset** of that material: a standalone, plain-language
`literature/README.md` covering papers **1, 2, 3 and 7**, readable by someone who never
opens `papers.md`.

Key constraints, read carefully:

- **Identify the four papers by their position/handle in `papers.md`**, explicitly not
  from memory or from the issue text. Verified before writing anything (see below).
- The relevance sections must be **pulled from the existing `Relevance` field**, not
  rewritten from scratch. So this is a compilation/reframing task, not a new analysis.
- **Every claim must trace to a verifiable source**; anything unverifiable gets
  `[unverified — needs confirmation]`.
- Needs a closing paragraph naming the **research gap** — what none of the four
  address, which this FYP does.

### Paper identification (done first, from the file itself)

`grep -nE "^### \[" literature/papers.md` gives this order, and the summary table at the
top of `papers.md` numbers them identically 1–7:

| # | Handle | Title |
|---|--------|-------|
| 1 | `[Aher-TE]` | Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies |
| 2 | `[Argyle-OOM]` | Out of One, Many: Using Language Models to Simulate Human Samples |
| 3 | `[Cheng-MP]` | Marked Personas: Using Natural Language Prompts to Measure Stereotypes in Language Models |
| 4 | `[Wang-NYR]` | LLM-based Human Simulations Have Not Yet Been Reliable |
| 5 | `[Hullman-VAL]` | This human study did not involve human subjects |
| 6 | `[Zhong-DDC]` | Data-driven Crowd Modeling Techniques: A Survey |
| 7 | `[Park-GA]` | Generative Agents: Interactive Simulacra of Human Behavior |

**Selected: 1 Aher-TE, 2 Argyle-OOM, 3 Cheng-MP, 7 Park-GA.** Body order and summary
table agree, so the numbering is unambiguous. Noting the incidental pattern for the PR
description: the selected four are exactly the peer-reviewed LLM-behaviour papers —
the excluded three are the two preprints (4, 5) and the crowd-simulation survey (6).

### Assumptions made

- **A-path**: the issue writes `/CrowdSimulation/literature/README.md`. As with issue
  #2, `CLAUDE.md` says this repo *is* CrowdSimulation and the prefix is obsolete, so the
  file goes at `literature/README.md`.
- **A-branch**: the issue names `docs/2-lit-review-llm-human-behaviour` under "Branch".
  That branch has an **open, unmerged PR (#3)**. Rather than silently extending an open
  PR's scope, I branched `docs/4-literature-readme` off it and will target the PR at it.
  GitHub auto-retargets to `main` if PR #3 merges first. Flagged rather than assumed
  silently — if the intent was to commit straight onto the lit branch, this is a
  one-command change.

## Plan

1. Verify preconditions; confirm paper numbering from `papers.md` itself. *(done)*
2. Create branch + work log. *(done)*
3. Re-read the four full entries in `papers.md`, especially each `Relevance` field.
4. Write `literature/README.md`: intro → four paper sections → closing gap paragraph.
5. Verify: every claim traceable; no number without a source; self-contained.
6. Push, open PR stating which handles were selected and why (acceptance criterion 1).

## Progress log

### 2026-09-07 — Branch created, papers identified from the file
- What I did: Confirmed clean tree and that the lit branch is in sync with origin.
  Identified papers 1/2/3/7 by grepping the headings in `papers.md` and cross-checking
  against its summary table, before reading any content.
- Why: The issue explicitly forbids guessing which papers these are.
- Result / what I found: Unambiguous — body order and table numbering match.
- Next step: Write the README from the existing entries.

### 2026-09-07 - README written; a factual error in papers.md found and fixed
- What I did: Re-read the four full entries in `papers.md`, wrote
  `literature/README.md`, then verified every repo path and repo-fact the README
  asserts against the actual files.
- Why: Plan steps 3-5; the issue's sourcing rule requires every claim to trace to
  a verifiable source.
- Result / what I found:
  - All nine repo paths linked from the README exist. DD1/DD2/DD4 wording checked
    against `README.md` lines 94-103 and quoted accurately.
  - Persona cell count verified: `dataset/personas.yaml` has 5 age groups
    (child, teenager, young_adult, middle_aged, elderly) x 2 genders = **10
    cells**, and `dataset/scenarios.yaml` has **14** scenarios. 14 x 10 = 140,
    matching run01's 140 records. So the README's "ten persona cells" is correct.
  - **Error found and fixed.** Both `papers.md` (written for issue #2) and my
    first draft of the README referred to a free-text `rationale` field on a
    behaviour record. **There is no such field.** Dumping the schema shows the
    free-text field is `conflict_behaviour.narrative`; `decision_factors` is an
    array and does exist. Corrected in three places across the two files. This
    was my own error from issue #2, carried forward - worth recording because the
    Marked Words audit recommendation depends on naming the right field.
  - Confirmed the related claim that "`aggregation` already records per-repeat
    spread" IS correct: `aggregation.yield_likelihood_std` and
    `aggregation.primary_action_agreement` both exist in the schema.
- Next step: push and open the PR.

### 2026-09-08 - Correction: Cheng et al. does not support DD2; added paper 8
- What I did: A question about DD2 (why observer framing lowers stereotype risk versus
  Argyle et al.'s first-person backstories) sent me back to Cheng et al.'s actual prompt
  set. Downloaded the published PDF and read **Table A9**.
- Why: I had asserted in both `papers.md` and `literature/README.md` that Cheng et al.'s
  prompts "were also third-person descriptive". That claim was load-bearing for DD2.
- Result / what I found:
  - **The claim was wrong.** Table A9 lists **six** prompts spanning *both* framings:
    three first-person ("Imagine you are a(n) [X]. Please describe yourself.") and three
    third-person ("Describe a(n) [X]."; "Imagine a(n) [X]. Please describe [pronoun].").
  - **The more important fact I had missed:** the authors report they "did not find
    statistically significant differences in distributions of top words across prompts"
    and analysed all six in aggregate. So Cheng et al. tested observer framing directly
    and found no benefit - which makes the paper mild evidence *against* DD2's premise,
    not the justification for it that I wrote.
  - **Root cause:** I verified Cheng et al. from the ACL Anthology landing page and the
    ar5iv HTML. Neither renders the appendix. The published PDF does. Logged in
    `search-log.md` as a method note: where a claim depends on what a prompt said, read
    the PDF appendix.
  - **Consequence:** correcting this left DD2 with no citation at all. Searched for work
    on persona-assignment effects and added **entry 8, Deshpande et al. (2023), EMNLP
    Findings** - persona assignment raises ChatGPT toxicity up to 6x across >500k
    generations. Verified from the ACL Anthology landing page. It supports the
    *mechanism* DD2 relies on, though it measures toxicity rather than stereotype
    content, which the entry states plainly.
- Files touched: `papers.md` (Cheng entry rewritten + correction note + entry 8 added +
  summary table), `literature/README.md` (Cheng section), `refs.bib` (8th entry),
  `search-log.md` (addendum), `refs/` (cached the PDF).
- Verified: refs.bib re-validated - 8 entries, braces balance, no duplicate keys or
  titles, required fields present. Keys cross-check both ways. All 8 entries carry every
  template field.
- Next step: propagate to `docs/biweekly-updates/update-01.md` on the issue #5 branch.

## Open questions / risks

1. **Fixing `papers.md` widens this PR beyond issue #4's stated deliverable.**
   The `rationale` -> `conflict_behaviour.narrative` correction touches a file
   owned by issue #2 / PR #3. I judged that leaving a known-wrong field name in
   place to keep the diff clean would be worse. If you would rather keep the two
   PRs strictly separate, the `papers.md` hunk can be moved to PR #3.
2. **Branch choice.** Issue #4 names `docs/2-lit-review-llm-human-behaviour` as
   the branch, but that branch has an open unmerged PR (#3). I branched off it
   instead and targeted the PR at it, rather than silently growing PR #3's scope.
   GitHub retargets to `main` automatically if PR #3 merges first. Say the word
   if you want this squashed straight onto the lit branch.
3. **The gap paragraph is scoped to four papers, and says so.** The claim that no
   *wider* work has done this is explicitly marked
   `[unverified - needs confirmation]`, because four papers cannot support it.
   Entries 4, 5 and 6 in `papers.md` bear on it and should be read before the
   claim goes in the report. This is a deliberate limit, not an omission.
4. **Section/figure numbers are inherited from `papers.md`** and were read from
   ar5iv renderings rather than published PDFs. The README repeats that caveat,
   but anything quoted verbatim in the report still needs confirming.
5. **The "why it matters" sections are compiled from the existing `Relevance`
   fields, as the issue requires** - so they inherit those fields' judgement
   calls, including relevance ratings that are my assessment rather than a
   measurement. The supervisor should sanity-check the transfer arguments.

## Summary

**What changed.** Added `literature/README.md`: a standalone, plain-language
compilation of papers 1, 2, 3 and 7 from `literature/papers.md`. Also corrected a
wrong field name in `literature/papers.md`.

Structure follows the issue: a one-paragraph intro tying the review to the
dataset-generation stage; one section per paper with title/authors/year, a
plain-language account of method and findings, stated limitations, and a "why it
matters for this project" section compiled from that paper's existing `Relevance`
field; and a closing section naming the research gap.

**Paper identification** (acceptance criterion 1). Selected from `papers.md`'s own
heading order, cross-checked against its summary table, before reading content:
**1 = [Aher-TE]**, **2 = [Argyle-OOM]**, **3 = [Cheng-MP]**, **7 = [Park-GA]**.
Body order and table numbering agree, so the mapping is unambiguous. The four
selected happen to be exactly the peer-reviewed LLM-behaviour papers; the three
excluded are two preprints (4, 5) and the crowd-simulation survey (6).

**The gap section** names five specific absences rather than asserting novelty:
none of the four targets crowd/pedestrian simulation; none produces a reusable
frozen behaviour dataset (all query the model live); none operates near 10,000
agents (Park et al.'s 25 agents is the largest, and its cost is why); none is
validated outside a US/English context (Argyle et al. and Cheng et al. both say
so explicitly); and none maps elicited behaviour onto a physics-based simulator's
numeric parameters (this project's DD4 / `integration/crowdgym_mapping.md`).

**How it was verified.**
- Every repo path linked from the README was confirmed to exist (9/9).
- Every repo fact was checked against the source file rather than assumed: DD1,
  DD2 and DD4 quoted against `README.md`; the 10 persona cells and 14 scenarios
  counted from the YAML; the `|delta yield_likelihood| > 0.25` threshold and the
  "Gender / age bias audit" heading confirmed in `VALIDATION.md` section 5.
- That check caught one real error - a `rationale` field that does not exist -
  which is now fixed in both files.
- Paper-level numbers are inherited unchanged from `papers.md`, which verified
  them against cached primary sources in `refs/`.
- The one claim that could not be supported (that the gap holds against the wider
  literature) is marked `[unverified - needs confirmation]` rather than asserted.
