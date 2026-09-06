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

## Open questions / risks

- (to be filled during the work)

## Summary (fill in at the end)

- (to be filled at the end)
