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

### 2026-10-31 14:27 UTC — The results summary and the compact mapping
- What I did: `llm_negotiation/docs/round1-results.md` (tasks 1 to 6), each number with its file. Read the
  committed reports (RF-9 to RF-38) for every number; #55's digest only as a guide.
- **Decision (mine, [design]): a compact mapping.** The full `mapping.csv` has 402 combinations, 330 seen
  once: not readable as a lookup table. `mapping_compact.csv` reruns the same analysis with
  `--mapping-factors` set to the four factors with a Holm-significant effect (own assertiveness, knowing the
  other, finding the other attractive, own cane), a rule chosen before looking at it. Every other table of
  that run was identical (checked with `cmp`), so only its mapping is kept.
- Corrections found while checking: the placeholders RF-15's task 6 names (hearing range, eye-contact range,
  change thresholds) were replaced by sourced values on 2026-10-23, so section 6 lists the ones still in use
  instead; RF-14 graded RF-10's effects, so the evidence table says which of them survive under `keep_line`.

### 2026-10-31 14:41 UTC — Draft text, talking points, READMEs
- `llm_negotiation/docs/interim-report-draft.md` (task 7): methods and results as report prose, numbers
  from `round1-results.md`; square brackets mark what is to be decided or filled in.
- `literature/paper-summaries/supervisor-meeting-talking-points-rf15-round1.md` (task 8), in the style of
  the RF-9 notes: findings, the user's decisions (including 2026-10-22's, `docs/resolution.md`), and five
  questions for the supervisor. Option (b) of question 2 (use the agents for ORCA's parameters, not rules)
  is **my proposal**, marked *(my view)*.
- Checks while writing: the exact-repeat set is 8 cells per condition, each run three times in all (its
  design session and two more), which I first described wrongly in the draft and fixed
  (`docs/screening-designs.md`, section 6); the attractiveness decision of 2026-10-26 was the supervisor's,
  so it is not listed under the user's decisions; RF-37's "both rules within on H2" is an average of pairs at
  0.50 and 1.25 m, now said in the summary.
- README rows (top level and `llm_negotiation/`).

## Open questions / risks

- **Round 1 only.** The issue covers the rounds finished by early January 2027; this version covers round 1
  and is to be updated after rounds 2 and 3.
- **The compact mapping is my design choice**, not in the issue. The full mapping is kept beside it.
- **The rerun under `keep_line` changes two Holm results** against RF-10's (assertiveness on signalling, and
  a cane on start distance, the latter on 13 rows). RF-10's report is unchanged; the summary uses the rerun.
- **Debriefs:** `round1-results.md` quotes RF-14's 2,681 debriefs (all of round 1's runs) and the rerun's 576
  (the 288 sessions); both are right for what they count.
- Task 2's "how often a resolution depended on a signal or a message" is answered by RF-30's split (resolved
  with and without a signal seen or a message), not by a causal test.
- For the supervisor (talking points, Part 3): the budget (USD 0.17 left, overall cap pending), the direction
  after round 1, the passing distance, pending item 5, and whether round 1 is enough for the interim report.

## Summary (fill in at the end)

- **What changed:** `llm_negotiation/docs/round1-results.md` (the mapping and the results summary),
  `llm_negotiation/docs/interim-report-draft.md` (draft methods and results), the talking points in
  `literature/paper-summaries/`, `runs/rf15_round1_keep_line_analysis/` (RF-8's analysis rerun under
  `keep_line`, with the compact mapping), README rows.
- **Why:** issue #70's tasks 1 to 8, for the interim report of 25 January 2027, covering round 1.
- **Verified:** every number in the summary was checked against the report or file named beside it; the draft
  and talking points take theirs from the summary. No code changed and no model was called; the rerun used the
  existing analysis with RF-10's settings. Tests: see the next entry.
