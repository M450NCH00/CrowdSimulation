# Work Log — Issue #52: [Research] Literature: describing environments to LLMs (simulators and crowds first), and how well each method works

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/52
**Branch:** docs/52-environment-description-llm-review
**Started:** 2026-10-19

## Understanding the issue

negsim tells an LLM much less about a scene than a person in it could perceive. Layer 1 (live
negotiation) handles exactly two agents, and the place is one fixed paragraph per scenario type
(`persona_v1.yaml`, `scenes:`) plus a short report of distances and speeds. Layer 4 (rule
generation) describes one other person in detail (`describe.py`, `first_person`, `third_person`)
and everyone else in one line: "Other people are walking around you as well."
(`rulegen_negotiate_v2.yaml`, `place_others`).

Before any prompt is redesigned, the issue asks for a literature review, five papers read in full,
on how studies describe a simulator's environment (crowd simulators first) to an LLM, and what
evidence there is on how well each method works. Questions: Q1 methods (form, content, how numbers
and directions are written); Q2 measured comparisons of formats; Q3 how many agents are described
and how; Q4 perceivable versus omniscient, and visible attributes; Q5 the research gap, with the
searches behind it; Q6 a verdict for negsim (a proposal), with offline token counts for 2, 5 and 10
nearby people.

Literature only: no code, no change to `llm_negotiation/`, no LLM calls of any kind.

**Assumptions:**
- A1. **Base branch.** As the issue says, and as in track #34, the branch is cut from
  `docs/beginners-guide-issues-35-41` (PR #51), not `main`, and the PR will target it. `git checkout
  main` was not run (memory note on half-failed checkouts).
- A2. **Token counts (Q6).** "Counting tokens offline" is read as: render example descriptions as
  text and count them with an open tokenizer that runs locally, with no API call. DeepSeek publishes
  its tokenizer on Hugging Face; if it cannot be obtained offline, an open tokenizer of a similar
  family is used and named, and the counts are labelled estimates.
- A3. **Which negsim files may be read.** The issue lists what to read "before starting". For Q6 I
  may need to see an actual rendered description to count it; I will build examples from the
  templates already read (the `situation` block and `persona_v1.yaml`) rather than open more code.

## Plan

1. Read only the prescribed inputs (done; see the first progress entry).
2. Search: confirm the seed leads from their own pages (arXiv API, venue pages), and run new searches
   for the three relevance tiers. Record every search and every paper screened in `search-log.md`.
3. Choose the five, by tier: at least one with a measured comparison of description formats.
4. Fetch the five full texts to `refs/ed_*.pdf`, extract to `refs/ed_*.txt` with `pdftotext`, and
   search the extracts rather than reading whole documents.
5. Write `entries.md` (five full entries, every claim quoted with a locator), in the priority order
   the issue gives: Q1-Q3 for each, then Q5, Q4, Q6.
6. Write `findings.md` (method table, results with quotations, research gap with its searches),
   `verdict.md` (one page, a proposal, with offline token counts), `missing-papers.md`, the BibTeX.
7. Check every quotation against the cached text (a script), then `.gitignore` any non-open copies.
8. Push, open the PR against `docs/beginners-guide-issues-35-41`, comment on the issue.

## Progress log

### 2026-10-19 — Branch and prescribed reading
- What I did: checked `gh auth`, the remote and a clean tree; cut
  `docs/52-environment-description-llm-review` from `docs/beginners-guide-issues-35-41`. Read the
  prescribed inputs only: `describe.py` (module docstring, `first_person`, `third_person`),
  `situation.py` (module docstring), `persona_v1.yaml`, the `situation` block of
  `rulegen_negotiate_v2.yaml`; in `llm-behavioural-conflict.md` the entries [Wang-SAMALM],
  [Baimbetova-PedAwareAV], [Yoldas-YieldBias], [Seo-LLMDR] and the [Cross-HypotheticalMinds] row;
  `paper-summaries/02-sense-think-act-reflect.md` and `03-gamechat.md`. For conventions only:
  `literature/trained-deciders/` (entries, search log, missing papers) and `.gitignore`.
- Why: the issue limits the starting reading to these.
- Result / what I found: negsim's description today, in the issue's terms: **first-person or
  third-person prose**, in fixed lines; geometry as passage width and wall distances; one other
  agent with distance, egocentric direction ("ahead of you and 30° to your left"), speed, heading,
  whether the gap is closing, body width, and (when visible) apparent age and gender; numbers in SI
  units at fixed rounding (0.1 m along, 0.01 m across, 0.01 m/s, whole degrees). Anyone beyond the
  one neighbour: one generic line.
- Next step: searches and screening.

## Open questions / risks

(filled in as the work goes)

## Summary (fill in at the end)

