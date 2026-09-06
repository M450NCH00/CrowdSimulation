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

## Open questions / risks

- (to be filled during the work)

## Summary (fill in at the end)

- (to be filled at the end)
