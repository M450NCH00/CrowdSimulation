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

### 2026-10-27 10:15 to 10:22 UTC — Task 1: the sources (draft `docs/population-profiles.md`)
- What I did: searched and read the sources for each share; cached seven files as `refs/rf33_*`.
  Written up in `llm_negotiation/docs/population-profiles.md`, section 2.
- Found:
  - **Age and gender:** SingStat M810011, residents at end-June 2026 (Table Builder API, data
    updated 2026-09-25): five-year bands by sex. 65 and over: 19.5% of residents, 21.3% of those
    aged 10 and over.
  - **A cane:** Gell et al. 2015 (NHATS 2011, US, community-dwelling 65+, n = 7,609, "a cane in the
    last month"), by five-year band, 8.6% at 65–69 to 36.6% at 90+. At Singapore's age mix: 14.8%
    of those 65+, **3.2% of the crowd**. No Singapore figure found. Under 65: **[placeholder]**
    (NHIS 1994 gives counts, not rates; its rate table is not archived).
  - **A phone:** Fernández et al. 2020 (Elche, Spain, 2019, 3,301 pedestrians walking on the
    street, observed at rush hours): "smombie" (looking at the screen) 14.6% at 10–18, 19.3% at
    18–35, 6.4% at 35–65, 1.7% over 65. At Singapore's age mix: **8.9% of the crowd**. Cross-check
    Hao et al. 2022 (four Chinese cities, crossing, any use 32.8%): wider category, not used.
    Chen and Pai 2018 (Taipei) rejected: a case-control sample gives no share.
  - **A large suitcase:** no count found anywhere: **[placeholder]**.
  - **Assertiveness and the other unobservable factors:** designed contrasts, not counted traits:
    **[placeholder]**.
- Dead ends (for the record): PMC's web pages (bot check), Europe PMC's full text for a non-OA
  author manuscript (HTTP 500; NCBI E-utilities worked), BMJ and JMIR PDFs (refused; Europe PMC
  XML worked for JMIR), NHIS Advance Data 292's rate tables (not archived).
- Mistakes corrected: cached the Taipei paper first as "lin2018" and the China one as "gao2022";
  the authors are Chen and Pai, and Hao et al. Renamed before committing.
- Result: a sourced street crowd of 100 has about 21 aged 65+, 3 with a cane, 9 looking at a
  phone, against 50 of each in RF-18's crowd.
- Next step: the design questions for the user (`docs/population-profiles.md`, section 4).

### 2026-10-27 11:14 UTC — The user's four decisions, before any profile or code
- Asked four questions; the user chose the proposed option each time:
  1. **Age mix: SingStat residents** (not Elche's observed mix, not a reweighting).
  2. **From age 10.**
  3. **Placeholders: small marked values**: a cane under 65 0.5%, a large suitcase on a street 1%,
     assertiveness half each way; each `[placeholder]`.
  4. **Rare rules: as designed**: the realistic verdict is the verdict of record; the stress
     scenario is reported beside it, labelled.
- Recorded in `docs/population-profiles.md`, section 4.
- Next step (session 2): the profiles, the generator with tests, the config keys, the rerun.

### 2026-10-27 11:17 to 11:28 UTC — Session 2: the profiles, the generator, the config keys (tasks 2 to 4)
- **Profiles** (`configs/populations/`, frozen, pinned by hash in `tests/test_populations.py`):
  - `singapore_street_v1.yaml` (realistic, `generator: quotas`): SingStat's counts by band and sex
    word for word (a test checks them against `refs/rf33_singstat_M810011_2026.json`), each factor's
    share by age with its source, the four limits.
  - `stress_all_factors_v1.yaml` (stress, `generator: cycle`): RF-18's people exactly (a test
    checks it against `mixed_population` with RF-18's `people`).
- **Generator** `negsim/populations.py`, `quota_people`: per seed, (1) the people over band × sex
  by the largest-remainder method, so the counts are exact; (2) each age drawn evenly within its
  band; (3) each factor's crowd total the nearest whole number to the shares, shared over the bands
  in proportion (capped at a band's size), and who gets it drawn within the band; (4) everyone
  shuffled onto the agents. One random stream per profile and seed (`random.Random("name:seed")`),
  so every arm gets the same people on a seed and every seed new people.
- **Config keys** per scenario (`negsim/ruleset_eval/experiment.py`): `population`, `purpose`
  (must match the profile's; once one scenario has one, all must), `pool`. Scenario names must
  differ. Summary: a scenario with a population gets its profile, limits and per-seed counts; with
  purposes, a rule gets `by_purpose`, and `overall` (the verdict of record) comes from the realistic
  scenarios only (`of_record_from: realistic`). Report: purposes in the verdict table, the rule
  table's realistic/stress columns, and a "People:" line per scenario. Nothing is added to a
  config without these keys.
- **Decisions (mine, [design]), for the user to check:**
  - D-1. **The 90+ band's ages are drawn from 90 to 94** (the table gives "90 Years & Over" only).
  - D-2. **Elche's phone bands laid on SingStat's**: 10–19 (Elche's 10–18), 20–34 (18–35), 35–64
    (35–65), 65+ (over 65). Elche's own bands overlap at 18 and 35.
  - D-3. **Factors are independent of each other within an age band** (no source gives joint
    shares; said in the profile's limits).
  - D-4. **A small scenario's pair is the first two of a crowd of 100 at exact shares** (`pool:
    100`). Exact quotas for 2 people would give the two largest cells (two women in their 30s) on
    every seed, with no factor ever; the pool gives a new, realistic pair on each seed.
  - D-5. **Realistic and stress are separate scenarios of one experiment**, `rf18_round1_realistic`,
    300 runs (6 scenarios × 5 arms × 10 seeds). The stress ones are RF-18's runs again, which checks
    that nothing changed.
- **Found:** RF-18's "half" is not exactly half: 100 is not a multiple of the cycle, so its crowd
  had 48 of 100 with a cane, a suitcase and a phone, and 36 holding their ground. The realistic
  crowd's cane share is 3.55% (3 or 4 of 100), not 3.2%: the 0.5% placeholder under 65 adds 0.4
  points to NHATS's 65+.
- **Tests:** `tests/test_populations.py` 23 passed (exact shares at 37, 100 and 1,000 people;
  by sex and band; deterministic; new people each seed; a cane mostly over 65; the pool; RF-18's
  people; refusals). `tests/test_ruleset_eval.py` 40 passed (24 before, 16 new: **RF-18's config
  describes itself as its run recorded it, and RF-18's summary re-judged from its 150 committed
  `measures.json` is identical**; the scenario refusals; the verdict of record from realistic only;
  a small run with a population).
- One mistake on the way: the first test of exact shares apportioned band totals, but the
  generator apportions band × sex cells (one fewer older person at 100); the test was wrong, not
  the code. The rerun config was first cut wrongly by a script (it matched `people:` inside
  `rotate_people:`); rebuilt with line-anchored keys and read back before use.
- Hygiene and related tests (`test_repo_hygiene`, `test_rulegen_replay`, `test_experiment_config`):
  76 passed. Committed the build (99aeab8c) before the run of record.

### 2026-10-27 11:40 to 12:55 UTC — The run of record: `rf18_round1_realistic`, 300 runs, no model call (task 5)
- `python run_experiment.py configs/rule_set_evaluation/rf18_round1_realistic.yaml` at 99aeab8c
  (clean). 42 s per flow run; the two-person runs take a fraction of a second. stdout went to a
  file and was buffered, so I followed progress by counting `measures.json` files instead.
- **Check: all 150 stress runs give exactly RF-18's measures** (every measure but wall time;
  script compared each run folder with RF-18's).
- **Verdicts of record (realistic):** the left-turn rule **helps** (unchanged: it reads no factor,
  so its runs are the same in both crowds); the cane rule **no change** (RF-18: harms); set 2
  **helps** (RF-18: harms). The cane rule no longer gridlocks (153 matches a run against 1,607), but
  collided pairs are worse on 8 of 10 seeds (216 against 164; p = 0.11, not significant).
- Report: `runs/rf18_round1_realistic/evaluation_report.md` (mine), `report.md` (the code's).
  Bulky logs are gitignored by RF-18's `rf18_*` patterns; committed: config, outcome and measures
  per run, the summary and reports.
- Full suite (run alongside the experiment, 12:02 to 12:30 UTC): **2,164 passed, 10 skipped, no
  failure** (the peak-hour `cost.json` test passed off-peak).
- Docs (task 6): `docs/rule-set-evaluation.md` section 1.1 and limits, `docs/population-profiles.md`
  section 5, both READMEs.

## Open questions / risks

1. ~~**Whose population?**~~ SingStat residents, the user's decision of 2026-10-27 (entry above).
   The limits stay: residents only (4.23 of 6.21 million at end-June 2026), and who is out walking
   differs from who lives here (Elche saw 15.9% over 65, SingStat gives 21.3% of those 10+).
2. **Two shares come from abroad** (a cane: the US, 2011; a phone: Spain, 2019). No Singapore
   figure was found for either. RF-14 should know the realistic crowd rests on them.
3. **A large suitcase has no source at all**, and depends most on the place: 1% is a placeholder
   for a street only. An MRT-station or airport profile would need its own source.
4. **The cane rule's "no change" is not "harmless".** Collisions lean worse on 8 of 10 seeds, and
   its stress verdict is harms. Should such a rule be marked for RF-14 ("harms where the factor is
   common")? The verdict rule does not say. The user's decision.
5. **10 seeds are few for a rare factor**: only 9 of 10 seeds agreeing is significant. 30 seeds
   (21 of 30 needed) would cost about 35 minutes per 10 seeds of the flow. The user's decision.
6. D-1 to D-5 (entry of 11:17 UTC) are mine, for the user to check.

## Summary

**What changed.**
- Sourced shares for a realistic Singapore street crowd (`docs/population-profiles.md`; sources
  cached in `refs/rf33_*`): SingStat residents at end-June 2026 by age and sex, from age 10; a cane
  by age (NHATS 2011, US); looking at a phone by age (Elche 2019, Spain); a large suitcase, a cane
  under 65 and assertiveness as marked placeholders with the user's values.
- Two frozen profiles (`configs/populations/`): `singapore_street_v1` (realistic, exact quotas)
  and `stress_all_factors_v1` (RF-18's crowd, named for what it is).
- A generator of exact shares (`negsim/populations.py`): exact counts per seed, the same people for
  every arm, new people on every seed.
- Per scenario of a rule-set evaluation: `population`, `purpose`, `pool`. A rule's verdict of
  record comes from its realistic scenarios; stress verdicts are reported beside it.
- Round 1 again in a realistic crowd (`runs/rf18_round1_realistic/`): **the left-turn rule still
  helps; the cane rule goes from harms to no change; both together from harms to helps.**

**Why.** The user's decision of 2026-10-27: realistic scenarios wherever possible, with
exaggerated ones only to test rules that rarely apply. RF-18 judged rules in a crowd where about half
carried a cane.

**How it was verified.**
- `tests/test_populations.py` (23) and 16 new tests in `tests/test_ruleset_eval.py` (40 in all).
  These include **RF-18's config and summary coming out identical from its committed run**, and the
  profile's SingStat counts checked against the cached table.
- The 150 stress runs reproduce RF-18's 150 runs exactly.
- Full suite: 2,164 passed, 10 skipped, no failure.
- No model call; USD 0.
