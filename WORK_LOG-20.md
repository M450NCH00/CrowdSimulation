# Work Log — Issue #20: [Research] Literature: game theory for communication-free conflict resolution rules

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/20
**Branch:** `docs/20-game-theory-conflict-rules`
**Started:** 2026-09-30

## Understanding the issue

The FYP wants to extract a **reusable pattern** from LLM-to-LLM conflict resolution, so that
future conflicts in the crowd simulation are resolved by *applying the pattern* rather than by
re-running an LLM exchange every time. The latest supervisor meeting sharpened the target:

1. The pattern **need not be a dialogue pattern.** It can be a rule agents follow to reach
   consensus **without communicating at all** — a traffic convention.
2. The rule **should not be tied to spatial conflict**; ideally it applies to any generic
   simulator. So the narrow-hallway case is one instance of a general class of conflict games,
   not the subject.

Game theory formalises exactly this object. This issue is **literature only**: collect the
theory and the applied work needed to (a) define precisely what is being extracted, and (b)
justify it in the report.

The payoff artefact is `candidate-rule-catalogue.md` — one row per candidate *runtime* rule
found in the literature, each sourced. The gating test for every paper:

> Could this be written as a function mapping observable agent state → action, per agent,
> with **no dialogue at runtime**? If no, and the paper offers no evidence about when such
> rules hold, exclude it.

### Assumptions I am making (issue was not ambiguous, but these are judgement calls)

- **A1. Branch base.** `github_issue_workflow.md` says branch from an up-to-date `main`. But
  `main` contains **no** `literature/` and **no** `refs/` — every literature PR (#9, #13, #15,
  #17, #19) is still open, and the established convention in this repo is that each issue
  branch is cut from the previous issue branch. I therefore cut this branch from
  `origin/docs/18-demographic-paper-summaries` (`f3427b1`), so prior literature and the
  `refs/` cache stay readable and citable. Deviation logged here deliberately.
- **A2. "Verified" means I opened the page myself.** Following the standard already set by
  issues #16/#18, every entry records whether I read the **full text** or the **abstract page
  only**, and locators are scoped accordingly (an abstract-only entry cites abstract sections,
  never invented page numbers).
- **A3. Paywalled classics.** Several `[foundational]` seeds (Maynard Smith & Price 1973,
  Maynard Smith & Parker 1976, Aumann 1974/1987, Schelling 1960, Lewis 1969) are behind
  publisher paywalls or are printed books. Where I cannot open the primary text, I will say so
  in `search-log.md` and **not** fabricate a locator into it. A confirmed bibliographic record
  (Crossref/publisher page) plus an explicitly-marked secondary statement of the definition is
  the fallback, and it will be labelled as such.

## Plan

1. Set up branch + work log; create `literature/game-theory/`. **(done)**
2. Read the three arXiv G1 seeds and the G4/G5 seeds — cache each to `refs/`.
3. Verify every `[secondhand]` foundational seed's bibliographic record; open primary text
   where reachable; report honestly where not.
4. Mine the G4 survey (`arXiv:2003.11959`) for the sequential-chicken and Stackelberg
   pedestrian work, then confirm each referenced paper independently.
5. G5: Science Advances paper + the data-leakage critique + the authors' reply. Record the
   critique's *specific* technical objections (incl. the strategy-label presentation point).
6. G6 (lower priority): search for convention/strategy transfer across structurally different
   games. Report thinness honestly if thin.
7. Write the six sub-area files using the issue's per-paper template.
8. Write `candidate-rule-catalogue.md` (draft, pending supervisor review) — one row per rule,
   every row sourced, no merging of similarly-named rules.
9. Write `search-log.md` including the required **framing check** (does the literature support
   calling this FYP's extracted pattern a *convention* or a *correlated equilibrium*?).
10. Write `refs-game-theory.bib`; verify acceptance criteria one by one; PR.

## Progress log

### 2026-09-30 — Branch and work log created
- What I did: checked preconditions (`gh auth` OK, tree clean), inspected branch topology,
  cut `docs/20-game-theory-conflict-rules` from `origin/docs/18-demographic-paper-summaries`,
  created `literature/game-theory/`, seeded this log.
- Why: workflow step 0–3. Base choice explained in A1 above.
- Result / what I found: all five prior literature PRs are open; `main` has no `literature/`.
  `refs/ashery2025_social_conventions_oa.html` is **already cached** from issue #16, so the G5
  anchor paper is partly in hand already.
- Next step: fetch and read the G1 arXiv seeds.

## Open questions / risks

- **R1.** Paywalled foundational texts (see A3) may leave some `[foundational]` definitions
  recordable only via a secondary source. That weakens the "formal definitions as the paper
  states them" requirement for those specific entries; it will be flagged per entry.
- **R2.** G6 (transfer across games) looks a priori thin. The issue explicitly permits
  reporting that rather than padding.
- **R3.** The framing check may come back negative — i.e. what this FYP plans to extract may
  not be a convention or a correlated equilibrium in the technical sense. That is a finding,
  and it would change how the report words its contribution.

## Summary (fill in at the end)

_To be completed._
