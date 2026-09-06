# Work Log — Issue #2: [Research] Literature review: LLM-elicited human behavior data for crowd-simulation agents

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/2
**Branch:** docs/2-lit-review-llm-human-behaviour
**Started:** 2026-09-06

## Understanding the issue

The FYP currently has a generated dataset (run01: 140 records from DeepSeek) but
**no literature grounding** for the two claims the report will have to defend:

1. That prompting an LLM for "typical human behaviour" yields data that is
   *valid enough* to feed an agent-based simulation.
2. That behaviour-driven agents are a reasonable direction for crowd simulation
   at all (as opposed to purely rule-based Social Force / CFSM models).

Deliverable is a set of three documents — `papers.md`, `refs.bib`,
`search-log.md` — with 5 verified papers (or fewer, explicitly justified),
each entry following a fixed template, each relevance section tied concretely
back to the DeepSeek dataset this repo generates.

Critically, the issue says **negative/critical results are especially valuable**.
This is not a "find 5 papers that agree with me" task — the supervisor's real
question is whether the approach is valid, so papers that find limits on LLM
behavioural fidelity are load-bearing, not inconvenient.

### Assumptions made

- **A-path**: The issue specifies deliverables under `/CrowdSimulation/literature/`.
  Per `CLAUDE.md`, this repository *is* the CrowdSimulation folder and the
  `/CrowdSimulation` prefix is obsolete after the repo split. So the deliverables
  go in `literature/` at the repo root. Flagging rather than silently relocating.
- **A-refs**: Workflow step 5b requires sources cached locally so claims can be
  re-checked. Cached under `refs/` at the repo root (new directory).

## Plan

1. Verify preconditions, branch, seed this work log. *(done)*
2. Search the required sources (arXiv, Semantic Scholar, Google Scholar, ACM DL)
   for the seed leads + the suggested query set.
3. For each candidate, open the actual abstract/PDF and confirm title, authors,
   year, venue. Never cite from memory of a title. Cache each source to `refs/`.
4. Check forward citations of the seed papers for more recent / more direct work,
   and deliberately hunt for *critical* evaluations (the issue prioritises these).
5. Write `papers.md` using the per-paper template, with every field filled.
6. Write `refs.bib`, deduplicated; check it is compile-clean.
7. Write `search-log.md` — queries run, sources searched, dead ends, and an
   explicit statement if fewer than 5 papers met the bar.
8. Verify per workflow step 5b: every quantitative claim carries a
   section/figure/table reference or is marked `[unverified]`; open questions
   section non-empty; every acceptance-criteria item answered or explicitly
   marked incomplete.
9. Push, open PR with `Closes #2`, comment the PR link on the issue.

## Progress log

### 2026-09-06 — Branch created, issue read, scope understood
- What I did: Read issue #2 in full. Confirmed preconditions (clean tree, main in
  sync with origin, `gh` 2.100.0 authenticated as M450NCH00). Created branch and
  seeded this log.
- Why: Workflow steps 0-3.
- Result / what I found: One path ambiguity (the obsolete `/CrowdSimulation/`
  prefix), resolved as assumption A-path above rather than blocking on it, since
  `CLAUDE.md` is unambiguous that the prefix is dead.
- Next step: Begin the literature search (plan step 2).

### 2026-09-06 — Search done, 6 papers verified from primary sources
- What I did: Ran the suggested query set across arXiv, Semantic Scholar, Google
  Scholar (via web search) and ACM DL. Verified all four seed leads by opening
  the actual abstract pages, then followed forward citations to find critical
  work. Cached every source under `refs/`.
- Why: Issue's search protocol steps 1-4; workflow step 5b requires local caches.
- Result / what I found:
  - All four seed leads are real and correctly attributed. Park et al. is UIST'23,
    Argyle et al. is *Political Analysis* (doi 10.1017/pan.2023.2), Aher et al. is
    ICML'23 (oral), Horton et al. is arXiv 2301.07543 / NBER w31122.
  - Forward-citation search surfaced two strong *critical* papers the issue
    explicitly prioritises: Wang et al., "LLM-based Human Simulations Have Not Yet
    Been Reliable" (arXiv 2501.08579, v3 Jul 2026), and Cheng, Durmus & Jurafsky,
    "Marked Personas" (ACL'23, Best Social Impact Paper).
  - Cheng et al. and Wang et al. both bear *directly* on run01's flagged
    "female personas yield more" pattern. Wang et al. §3.1 states LLMs are "3-6
    times more likely to generate gender-stereotypical behavioural patterns".
    This reframes that validation finding from an oddity into an expected,
    literature-documented failure mode — the single most useful outcome of this
    search for the supervisor conversation.
  - Found a peer-reviewed crowd-simulation anchor: Zhong, Li, Huang, Lu & Cai,
    "Data-driven Crowd Modeling Techniques: A Survey", ACM TOMACS 32(1) Art. 4.
    Wentong Cai is at NTU — the same school as the senior's CrowdGym FYP.
  - Decision: report **6** papers, not 5. The 6th (Zhong et al.) covers the
    issue's fourth scope bullet (data-driven crowd/pedestrian behaviour models),
    which none of the five LLM papers covers. Logged in `search-log.md`.
- Next step: write papers.md / refs.bib / search-log.md.

### 2026-09-06 — Dead ends and a correction
- What I did: Tried ACM DL directly for both the Generative Agents full text and
  the TOMACS survey; tried the Semantic Scholar API for citation counts.
- Why: The issue names ACM DL as a required source, and citation counts are
  needed to justify the `[non-archival]` label on the one preprint.
- Result / what I found:
  - `dl.acm.org` returns **HTTP 403** to automated fetches — both the DOI landing
    page and the full-text HTML. Worked around it via arXiv/ar5iv for Park et al.
    and an open-access author mirror for the TOMACS survey, then verified the
    survey's title/authors/venue/DOI **from the PDF's own front matter and ACM
    reference block**, which is stronger evidence than the landing page.
  - Semantic Scholar API returned HTTP 429 (rate limited) on almost every call
    even at 25 s spacing. Only Horton et al. came back (544 citations). Citation
    counts for the rest are therefore **not** used as evidence in `papers.md`.
  - **Correction to an intermediate reading:** my first fetch of the Generative
    Agents evaluation implied the human-crowdworker baseline ranked below every
    ablation. Re-checking against a second independent source gives the real
    ordering: full 29.89 > no-reflection 26.88 > no-reflection-no-planning 25.64
    > **crowdworker 22.95** > no-memory-planning-reflection 21.21. The crowdworker
    baseline ranks 4th of 5, i.e. above the most-ablated condition but below all
    the others. Recorded because it changes how strong that result actually is.
- Next step: write the deliverables.

### 2026-09-06 - Deliverables written and verified
- What I did: Wrote `literature/papers.md` (7 entries), `literature/refs.bib`
  (7 entries) and `literature/search-log.md`. Ran a structural validator over
  the .bib and a cross-check between the two files.
- Why: Plan steps 5-8; acceptance criteria in the issue.
- Result / what I found:
  - .bib: UTF-8 clean, 71 balanced brace pairs, 7 entries parsed, no duplicate
    keys, no duplicate titles, all required fields present per entry type, no
    unescaped `%`. **Caveat: no LaTeX toolchain on this machine** (no
    `bibtex` / `biber` / `pdflatex`), so "compiles" was verified structurally,
    not by an actual BibTeX run. Flagged under risks.
  - Cross-check: the 7 BibTeX keys in papers.md and the 7 in refs.bib match
    exactly in both directions; all 7 entries carry every template field.
  - 4 `[unverified]` markers and 7 `[non-archival]` markers placed.
- Next step: push and open the PR.

## Open questions / risks

1. **`refs.bib` was not compiled by a real BibTeX run.** No LaTeX toolchain is
   installed here. A structural validator confirmed balanced braces, unique keys,
   unique titles, required fields per entry type and no unescaped `%`, but the
   acceptance criterion says "compiles". **Run it through the actual report
   template once before relying on it.** The `@misc` preprint entries are the
   most likely to render differently under a specific bibliography style.
2. **ACM Digital Library returned HTTP 403 to every automated fetch**, and the
   issue names it as a required source. Worked around by verifying Zhong et al.
   from the PDF's own ACM reference block and Park et al. from arXiv plus the ACM
   citation record. Nothing in `papers.md` depends on an unverified ACM claim,
   but a human on a university network should spot-check both DOIs.
3. **Wang et al.'s venue is unresolved.** A companion GitHub repo labels it
   "ICLR 2025"; arXiv lists no venue. Treated as a preprint and marked
   `[unverified]`. Resolve before the report cites it - if it *is* peer-reviewed,
   the review gets stronger, since it is the entry carrying the gender-stereotype
   finding.
4. **Section/figure numbers come from ar5iv renderings of arXiv versions**, not
   from published camera-ready PDFs. Usually identical, not guaranteed. Two
   fetches of Aher et al. disagreed on where the hyper-accuracy-distortion
   discussion sits, so it is cited as "sections 7-8" rather than a single section.
   Confirm any number that gets quoted verbatim in the report.
5. **I reported 7 papers where the issue asked for 5.** Justified in
   `search-log.md` on scope-coverage grounds, but it is a judgement call and the
   supervisor may prefer a tighter set. The five LLM-validity entries alone
   satisfy the issue as literally written.
6. **One seed lead was dropped.** Horton et al. was verified as real and
   relevant but ranked below the seven adopted entries; reasoning is in
   `search-log.md`. This is a defensible call, not a confident one - it is
   well-cited (544 per Semantic Scholar) and a supervisor may expect to see it.
7. **"Utopian illusion" (arXiv 2510.21180) is worth a second look** before the
   report is written. Its claim - that LLM social simulations drift toward
   unrealistically harmonious outcomes - may describe this project's specific
   failure mode (conflict agents that always de-escalate) better than anything
   in the adopted set. Not adopted here only to avoid a third preprint.
8. **Citation counts could not be gathered** (Semantic Scholar returned 429s).
   None are used as evidence, so no claim depends on this, but if the report
   wants them an API key is needed.
9. **Relevance ratings are my judgement, not a measurement.** The 1-5 scores and
   the specific transfer arguments should be reviewed by the supervisor - they
   encode assumptions about where this project is heading that only the
   supervisor can confirm.

## Summary

**What changed.** Added a new top-level `literature/` folder with the three
deliverables the issue specified, plus a `refs/` folder caching every source.

- `literature/papers.md` - 7 verified papers, each using the issue's full
  template with no blank fields, each with an explicit transfer argument to this
  project's dataset design or validation plan.
- `literature/refs.bib` - 7 deduplicated entries, structurally validated.
- `literature/search-log.md` - sources, queries, forward-citation results,
  rejected candidates (with reasons, including for a dropped seed lead), and an
  honest record of the two access failures.
- `refs/` - cached HTML/PDF of every cited source so claims can be re-checked.
- `README.md` - one line added to the directory layout so `literature/` is
  discoverable.

**Why.** The FYP had a generated dataset but no literature grounding for the two
claims the report must defend: that LLM-elicited behaviour is a valid simulation
input, and that behaviour-driven crowd agents are a reasonable direction at all.

**The most useful finding.** The `run01` validation flagged a systematic "female
personas yield more than male" pattern as an open item for the supervisor. Two
independent papers say this is a *documented, expected* property of the method,
not a bug in the prompt: Wang et al. section 3.1 report LLMs are "3-6 times more
likely to generate gender-stereotypical behavioural patterns", and Aher et al.
found a large gender asymmetry in yielding (60% vs 20% acceptance of unfair
offers, p<1e-16) in the Ultimatum Game - structurally the same yield/refuse
decision this dataset encodes. Cheng et al. then supply a runnable audit method
(Marked Words) and the specific warning that flattering-sounding gender
differences are the ones that survive plausibility checks. That reframes the
supervisor conversation from "is this a bug?" to "here is the known failure
mode, and here is how we audit it."

**A second finding worth surfacing.** Hullman et al.'s exploratory/confirmatory
distinction implies the honest claim for this report is "a plausible, internally
consistent behaviour prior", not "a validated substitute for human behavioural
data". Park et al.'s cost figure (thousands of dollars for 25 agents over two
simulated days) is the citable evidence for DD1, but their ablation also shows
what freezing the table gives up (TrueSkill 29.89 -> 21.21 without memory and
reflection). Both are recorded in `papers.md` rather than smoothed over.

**How it was verified.** Per workflow step 5b:
- Every quantitative claim carries a section/figure/table reference, or is
  marked `[unverified]` (4 such markers).
- Every title, author list, year and venue was confirmed by opening the actual
  abstract page or PDF - never from memory of a title. One mis-attribution I
  introduced myself (guessing "Zhu Wang" for the TOMACS survey) was caught and
  corrected to Zhong et al. from the PDF front matter, and is logged.
- One substantive misreading (the Park et al. crowdworker baseline ranking) was
  caught by cross-checking a second source and corrected; both the error and the
  correction are recorded rather than quietly fixed.
- `refs.bib`: 7 entries, no duplicate keys or titles, required fields present,
  balanced braces, valid UTF-8. Not compiled by real BibTeX - see risk 1.
- Cross-check: BibTeX keys in `papers.md` and `refs.bib` match exactly in both
  directions; all 7 entries carry every template field.
- Every acceptance-criteria item is answered; the ACM DL access failure is
  stated explicitly rather than omitted.
- Sources cached in `refs/`.
