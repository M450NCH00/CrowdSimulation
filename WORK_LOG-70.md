# Work Log — Issue #70: RF-15: results summary for the interim report, covering the rounds finished by then

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/70
**Branch:** docs/70-rf15-interim-results-summary (from `origin/feat/110-rf32-group-head-on`, after PR #125 merged)
**Started:** 2026-10-31 14:16 UTC

## Understanding the issue

The interim report is due on 25 January 2027. This issue turns the RF results into what the report
needs: the factor-to-decision mapping, the answers of Steps 1 to 4, RF-18's full simulation, the method and
its limits, draft text for the report's methods and results sections, and supervisor talking points. Every
number must trace to a committed report or `cost.json`. Paid: no. Code: none.

**Assumption (stated, not decided by the supervisor):** the issue says it covers the rounds finished by early
January 2027. Only round 1 is finished. The user asked on 2026-10-31 to do RF-15 now, after I proposed
"round 1 now, later rounds added in January". So this version covers round 1 (RF-9 to RF-38) and lists
rounds 2 and 3 as planned work; it is to be updated when later rounds finish.

## Plan

1. Collect the numbers from the committed reports (the digest in #55 is a guide, not a source).
2. RF-10's factor analysis, decision tree and mapping were made under `as_prompted` execution, which undid
   sidesteps (RF-29). Every later result uses `keep_line`. Rerun the existing `python -m analysis`, with
   RF-10's settings, on the `keep_line` outcomes (RF-29's re-execution of the independent condition and
   RF-30's non-verbal and talk): no new code, no model call.
3. Write `llm_negotiation/docs/round1-results.md`: the mapping (task 1) and the results summary (tasks 2 to 6),
   each number with its source file.
4. Write `llm_negotiation/docs/interim-report-draft.md` (task 7).
5. Write the talking points in `literature/paper-summaries/` (task 8).
6. Check every number against its file; README and #55.

## Progress log

### 2026-10-31 14:20 UTC — RF-8's analysis rerun under `keep_line`
- What I did: `python -m analysis` on RF-29's re-execution (independent) and RF-30's outcomes (non-verbal,
  talk), RF-10's settings; output `runs/rf15_round1_keep_line_analysis/` with a `NOTE.md`.
- Why: RF-10's mapping, tree and effects were made under `as_prompted`, which undid sidesteps; every result
  since RF-29 uses `keep_line`. The interim report should use the execution of record. RF-10's folder is
  left as it was.
- Result (`report.md` there):
  - **Nothing on resolution survives Holm** (strongest uncorrected: p1 carrying a load, OR 0.60, p 0.057).
  - Survives: assertiveness, less slowing (OR 0.10) and more signalling (OR 13.6, new under `keep_line`);
    familiarity (OR 445) and attractiveness (OR 6.5) on signalling; a cane, starting earlier (+2.25 m, but on
    13 rows only); the conditions' decision points (+3.4 and +3.5).
  - Decision tree for who passes first: held out 0.837 against 0.843 for always guessing: **no usable
    pattern**, as in RF-10 (0.733 against 0.754).
  - All 80 counterfactual comparisons within the noise floor; 23 of 24 exact-repeat cells are coin flips
    (RF-10: 24 of 24).
  - Mapping: `mapping.csv`.
  - Intent against plan covers non-verbal and talk only (no `decisions.jsonl` in the re-execution); RF-10's
    independent figure stands, since those plans are unchanged.

## Open questions / risks

## Summary (fill in at the end)
