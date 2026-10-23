# Work Log — Issue #62: [Feature] RF-7: screening designs (fractional factorial, random sample) and counterfactual pairs

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/62
**Branch:** feat/62-screening-designs-counterfactual-pairs (cut from `feat/61-pairwise-perception-factors`, as every RF branch is stacked on the previous one)
**Started:** 2026-10-23

## Understanding the issue
The resolution layer's design (`negsim/resolution/design.py`, RF-3) crosses every factor in
full. With 12 to 16 two-level factors that is 4,096 to 65,536 cells per case and condition, far
beyond the budget (about 240 sessions for round 1, D15). RF-7 adds screening designs:

- `design.kind`: `full` (today's behaviour, the default), `fractional` (a regular 2^(k-p)
  fractional factorial of resolution IV or higher, generators from a published table), and
  `sample` (N cells drawn with the seed, balanced per factor where possible);
- counterfactual pairs: two sessions identical except for one factor, linked by `pair_id`;
- geometries (D14): 2 or 3 cases of one encounter type, each cell run once on each, with
  geometry recorded on the session;
- the exact-repeat set (D14): a few cells, chosen with the seed and balanced, run `times` times
  on identical prompts and one geometry: the noise floor for RF-8;
- `--plan` reports all of it with the worst-case cost.

A config without `design.kind` (and the new keys) must give exactly the cells and session ids,
and the same records, as before.

**Assumption (flagged):** the issue was written when only `negsim/rulegen/design.py` existed
(issue #30's layer) and points there. Since then RF-3 (#58) added `negsim/resolution/design.py`,
whose docstring already says "RF-7 (#62) builds the screening designs", and geometries and the
exact-repeat set (tasks 6 and 7) are D14's, which belong only to the resolution layer. So the
screening designs are built for the resolution layer, the one RF-10 screens with. The rulegen
layer (#30, superseded by track #55) is left exactly as it was, which also satisfies task 5's
"the `rulegen` layer keeps [order] as before". The generic parts (the fraction, the sample, the
balanced subset) are in their own module, so the rulegen layer could use them later.

## Plan
1. Fetch and cache the published generator tables (NIST/SEMATECH e-Handbook, Table 3.17 and its
   design files; Chen & Cheng 2006 for 12 to 16 factors in 32 runs) in `refs/`.
2. `negsim/resolution/screening.py`: the generator table, the run matrix of a 2^(k-p) design,
   a resolution check on the cells themselves, the word-length pattern, the balanced random
   sample, and a balanced subset for the exact-repeat set.
3. `design.py`: `kind`, `cells` (the run size), `geometries`, `exact_repeats`,
   `counterfactual_pairs`; sessions with `geometry`, `pair_id` and `pair_role` only when used.
4. `experiment.py`: cases from `design.geometries` (one encounter type), `--plan` lines, outcome
   columns for geometry and pairs.
5. Tests (the issue's list), a mock rehearsal config for round 1's screening shape, docs.

## Progress log

## Open questions / risks

## Summary (fill in at the end)
