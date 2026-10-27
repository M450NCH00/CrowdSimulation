# Work Log — Issue #112: RF-33: realistic scenarios: sourced population shares, crowds with exact shares, realistic and stress scenarios; round 1 re-evaluated in a realistic crowd

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/112
**Branch:** feat/112-rf33-realistic-scenarios (from `feat/74-rf18-rule-set-crowd-runs`; PR #111 merged
into `feat/108-...` on 2026-10-27, and `main` is not used in this track)
**Started:** 2026-10-27, 10:14 UTC

## Understanding the issue

RF-18 (#74) judged round 1's rules in a crowd whose people got their factors by cycling each
factor's levels (`negsim.rulegen.replay.mixed_population`). Every factor therefore sits at exactly
half: half the crowd is 70, half carries a cane, half pulls a large suitcase, half looks at a phone,
half holds its ground. In the two-way flow the mix is also the **same crowd on every seed** (only
the small scenarios rotate it). The cane rule's "harms" (gridlock on 2 of 10 seeds) is a verdict
about a crowd that does not exist.

The user decided on 2026-10-27: **simulate realistic scenarios wherever possible, and keep
scenarios with exaggerated shares only to test rules that would rarely apply in a normal one.** This
issue makes that possible:

1. sourced shares for every factor a rule can read, each with what was measured, where and when,
   cached in `refs/`, or marked `[placeholder]`;
2. population profiles under `configs/populations/` (`singapore_street_v1`, realistic;
   `stress_all_factors_v1`, today's mix named for what it is);
3. a generator of exact shares (deterministic shuffle of exact quotas per seed, the same people for
   every arm);
4. `population` and `purpose` per scenario of a rule-set evaluation, with verdicts reported by
   purpose and a rule's verdict of record from its realistic scenarios;
5. round 1 rerun as `rf18_round1_realistic`, each rule's verdict compared with RF-18's;
6. docs.

What a rule can read (so what needs a share): `age` and `gender`; the three visible factors
`mobility_aid` (none, cane), `load` (none, large_suitcase), `distraction` (none, phone); and, in
rule format 4's own-only conditions, a person's own unobservable factors (`assertiveness`,
`urgency`, `residence`, `memory_note`). Real ethnicity is read by no rule and stays out of scope.
In the avoidance simulator, age and the factors change no body or speed (`negsim/avoidance/` reads
age only to give it to rules; a suitcase widens a body only in the resolution layer), so the shares
matter through the rules alone.

## Plan

Session 1 (research):
1. Sources for each factor (task 1): the age mix and gender (SingStat), walking aids by age, large
   luggage by kind of place, phone use while walking (observational studies). Cache each in `refs/`.
   For each, what was measured, where and when.
2. Write the sources up (`docs/population-profiles.md`) with each share, its source and its limits.
3. Ask the user the design questions the sources raise (below) before building.

Session 2 (build and run):
4. Profiles under `configs/populations/` (task 2), frozen, loaded and checked.
5. The generator of exact shares, with tests (task 3).
6. Config keys `population` and `purpose` (task 4); verdicts by purpose; earlier configs unchanged.
7. The rerun `rf18_round1_realistic` (task 5) and the comparison with RF-18.
8. Docs (task 6), the full suite, PR.

## Progress log

### 2026-10-27 10:14 UTC — Started
- What I did: merged PR #111 and closed #74 by hand (the user's request), ticked #74 in #55, cut
  this branch from `feat/74-...`. Read #112, `docs/rule-set-evaluation.md`, RF-18's report and
  config, `mixed_population` and `people_for`, the core factor list (`negsim/personas/schema.py`),
  `docs/ethnicity.md` and `literature/demographic-personas/population-data-sources.md` (issue #16's
  SingStat sources: residents against total population).
- Result: the crowd's people are one fixed cycling mix; in the flow, the same 100 people on every
  seed. Age does not change speed in the avoidance simulator.
- Next step: sources (plan step 1).

## Open questions / risks

1. **Whose population?** (raised in issue #16, B5): SingStat's fine age bands are of residents
   (4.23 million of 6.21 million at end-June 2026); the total population comes in broad bands only.
   And neither is the people on a street: who is out walking differs from who lives here.

## Summary (fill in at the end)
