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

### 2026-10-23 — the published tables, and a gap in them
- What I did: fetched NIST/SEMATECH e-Handbook section 5.3.3.4.7 (Table 3.17) and the design
  file of every 16- and 32-run design it lists (`refs/rf7_nist_2to<k>m<p>.txt`, tracked: a US
  government work).
- Found: Table 3.17 stops at **11 factors in 32 runs**, but the issue needs 12 and 16 in 32.
  A search turned up Chen & Cheng (2006, *Ann. Statist.* 34: 546-558; arXiv:math/0605616),
  whose Corollary 3.6 says every regular resolution IV design with 5N/16 < k < N/2 factors is a
  projection of the saturated resolution IV design (k = N/2), which is unique and has minimum
  aberration. For N = 32 that is the 2^(16-11) design of every odd-length product of 5 base
  factors. Preprint kept local (arXiv licence), passages in
  `refs/rf7_chen_cheng2006_excerpts.txt` (tracked).
- Decision: 16 runs with 5 to 8 factors and 32 runs with 6 to 11 use NIST's generators; 12 to
  16 in 32 runs use the saturated design and, below 16, the deletion with minimum aberration,
  found by an exhaustive search (`scratchpad/projections.py`, now repeated in a test). The
  designs nest: 123, 124, 125, 134, 135, 145, 234, 235, 245, 345, 12345, taken in order. Cross
  check: the same search for 11 factors finds NIST's word-length pattern (A4 = 25, A6 = 27).
  Theory check: deleting 4 points of AG(4,2) destroys at most 102 of its 140 planes, so A4 = 38
  is the minimum for 12 factors, as found.
- **Flag:** the 12 to 15 factor generators are derived as the paper prescribes, not copied from
  a printed table. Wu & Hamada (*Experiments*, 2nd ed., Appendix 5A) or Chen, Sun & Wu (1993)
  should list them; I could not open either. A reader with access can compare.

### 2026-10-23 — where the code goes
- Decision (assumption, see "Understanding the issue"): the resolution layer, not rulegen.
  Generic parts in `negsim/resolution/screening.py`; `design.py` gains `kind`, `cells`,
  `geometries`, `exact_repeats`, `counterfactual_pairs`.
- Design choices made here (none is a supervisor decision; each is in
  `docs/screening-designs.md`):
  - `mapping` is a column of the fraction like any other, so it is balanced and clear of
    two-factor interactions, and counts towards the 16. Crossing it on top of the fraction
    would double round 1 to 480 sessions, against D15's 240.
  - A factor at one level is fixed; at two levels it is screened; more levels are refused in a
    fraction (`sample` takes them).
  - Factors take columns in `ALL_FACTORS` order, level 1 = -1. Which factor gets which column
    decides which two-factor interactions are aliased together, not the main effects.
  - `exact_repeats.times` counts every run of the cell, the design's own included (3 = the
    design session + 2 more): that is what gives D15's 240 sessions for round 1
    (192 + 8 x 2 x 3).
  - The exact-repeat cells are the same in every condition; their geometries are taken in turn.
  - With `design.geometries` the config's `cases` give only the store (naming the cases twice
    could disagree); the geometries must be of one encounter type and plug-in.
  - A counterfactual pair runs on every case and condition; its `to` may be a level the design
    does not otherwise use (for example `age_pair: p2_older`); flipping `mapping` is refused.
  - The sample and the exact-repeat set use their own seeded generators (`sample:<seed>`,
    `exact_repeats:<seed>`), independent of the experiment's name, so the same design block
    gives the same cells under any name; the session order keeps RF-3's `<experiment>:<seed>`.

### 2026-10-23 — built, and old configs unchanged
- What I did: `screening.py`, the design and experiment changes, `--plan` lines, outcome columns
  `geometry`, `pair_id`, `pair_role`, `pair_factor` (only when used), `tests/test_screening.py`
  (39 tests), and `configs/resolution/resolve_screening_mock_rehearsal.yaml`.
- Checked that old configs are unchanged: a worktree of the previous commit (8e67310) and this
  branch gave identical sessions (`as_dict`), configs and cost previews for all three resolution
  configs; the test suite repeats this against RF-3's algorithm.
- Two test expectations of mine were wrong, not the code: the alias message names the earlier
  factor first ("1 is aliased with 6"), and 32 cells per geometry give 16 per level, not 8.
- Found: the rehearsal's **worst-case preview is USD 17.36** for 252 sessions (round 1's shape).
  See open questions.

### 2026-10-23 — verified end to end on the mock
- The rehearsal (`resolve_screening_mock_rehearsal.yaml`) ran all 252 sessions on the mock in
  9 min 43 s, into the scratchpad (not committed): 252 completed. 126 sessions per geometry,
  72 in the exact-repeat set (8 cells x 3 runs x 3 conditions), 12 in the pair (6 base, 6
  flipped). Each of the 24 exact-repeat groups recorded identical prompts and identical outcomes.
  The mock used at most 7.7% of a session's preview (its tokens are its own count, not
  DeepSeek's). Its "resolutions" are scripted and mean nothing about a model.
- Full suite: 1764 passed (1725 before + 39 new) in 9 min 43 s. It started before the docs
  commit, so every test file that reads a document or README was run again afterwards: 1106
  passed.

## Open questions / risks
- **Round 1 cannot run under a cap near USD 0.50 as the runner stands.** The preview is a strict
  bound (peak prices, 6 sends per call, the longest description), about USD 0.03 to 0.10 per
  session, and a paid run whose bound exceeds the cap is refused. Track #55 estimates round 1 at
  "of the order of USD 0.50". RF-9's pilot measures the real cost per session; then either the
  cap is set above the bound, or the guard compares something tighter (for example the
  measured cost with a margin). Not changed here: it is a budget question for the user and the
  supervisor (paid runs are still pending, `CLAUDE.md` item 1).
- The 12 to 15 factor generators are derived (Chen & Cheng 2006 plus a tested search), not
  read from a printed table (see the first entry).
- **Which factor gets which column** is fixed by `ALL_FACTORS` order. It does not affect main
  effects, but it decides the two-factor interaction alias chains. If RF-10 expects a specific
  interaction (say urgency x assertiveness), it may want to control the assignment; not
  built, because nothing asks for it yet.
- The rulegen layer has no screening designs (assumption above). If the user wants them there
  too, `screening.py` is layer-free, but rulegen's `order` and three- and four-level factors
  would need decisions.
- `balanced_subset` is a local search: "balanced where possible" is met for the cases tested
  (8 of 32 cells, 12 factors: every factor 4 and 4) but not proven optimal for every design.

## Summary (fill in at the end)
**What changed.** The resolution layer can now screen many factors cheaply:
- `design.kind` is `full` (unchanged default), `fractional` (a regular 2^(k-p) fraction of 16
  or 32 cells at resolution IV or higher, checked on its cells; up to 16 two-level factors in
  32, `mapping` one of them) or `sample` (a seeded, balanced random sample).
- `design.geometries` (D14): cases of one encounter type, every cell once on each, the
  geometry recorded on every session and outcome row.
- `design.exact_repeats` (D14): a balanced, seeded handful of cells run several times on one
  geometry with byte-identical prompts.
- `design.counterfactual_pairs`: two sessions identical but for one factor, linked by
  `pair_id`.
- `--plan` reports all of it. A round-1-shaped mock rehearsal config is added.

The generators are NIST's (Table 3.17) and, for 12 to 16 factors in 32 runs, Chen & Cheng
2006's projections of the saturated 2^(16-11) design. All sources are cached in `refs/`. New
doc: `llm_negotiation/docs/screening-designs.md`.

**Why.** A full factorial of 12 to 16 factors is 4,096 to 65,536 cells per case and condition.
Round 1 (D15) needs 32 cells x 2 geometries + the exact-repeat set = 240 sessions.

**How it was verified.**
- 39 new tests, covering every item of the issue's test list.
- The generators match the cached NIST files, and the 12–16 factor designs pass an exhaustive
  minimum-aberration search.
- Old configs give identical sessions, ids, configs and previews: checked against the previous
  commit in a worktree, and in tests against RF-3's algorithm.
- The full suite passes (1764).
- A 252-session mock run completed end to end.

**Not done / for the user.** No paid call. The rulegen layer is unchanged (an assumption). The
worst-case preview of round 1's shape (USD 17.36) is far above #55's estimate. See open
questions.
