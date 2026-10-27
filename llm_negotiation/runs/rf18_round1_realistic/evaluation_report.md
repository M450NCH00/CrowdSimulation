# RF-33, round 1 in a realistic crowd: do the verdicts of RF-18 hold?

Issue #112. Run of 2026-10-27 (11:40 to 12:55 UTC, commit 99aeab8c, clean), no model call, USD 0.
Method: `docs/rule-set-evaluation.md` (section 1.1) and `docs/population-profiles.md`. The
machine-written tables are `report.md`; the numbers here are from `summary.json` and each run's
`measures.json`. 300 runs: 6 scenarios × 5 arms (plain ORCA, 3 judged rule sets, 1 reference) ×
10 paired seeds (30901 to 30910), baseline `orca_perturbed_v1`, verdict rule 2.

## What was run

RF-18's config (`configs/rule_set_evaluation/rf18_round1.yaml`, issue #74), with the same rules,
arms, seeds and verdict rule. Only the people change. Each of RF-18's three scenarios runs twice:

| Scenario | People | Purpose |
| --- | --- | --- |
| `*_realistic` | `singapore_street_v1`: sourced shares, exact on every seed, new people on every seed. In the flow, per 100: 20 aged 65 and over, 3 with a cane, 9 looking at a phone, 1 with a large suitcase (placeholder), 50 holding their ground (placeholder). The two-person scenarios take the first two of a crowd of 100 | **verdict of record** |
| `*_stress` | `stress_all_factors_v1`: RF-18's people. Per 100: 50 aged 70, 48 with a cane, 48 with a suitcase, 48 on a phone, 36 holding their ground | beside it, labelled |

The realistic profile's limits: residents only; the cane share is from the United States (2011) and
the phone share from Spain (2019); a suitcase, a cane under 65 and assertiveness are placeholders
(`docs/population-profiles.md`).

**Check: the stress runs are RF-18's runs.** All 150 give exactly RF-18's measures (every measure
but wall time), so nothing in the build changed an earlier run.

## Findings

**1. The verdicts** (rule 2; rule 1 differs only where shown):

| Scenario | Set 1 (left turn) | Cane rule alone | Set 2 (both) |
| --- | --- | --- | --- |
| Two-way flow, **realistic** | **helps** | **no change** | **helps** |
| Two-way flow, stress (= RF-18) | helps | harms | harms (rule 1: trade-off) |
| Opposing bottleneck, realistic / stress | no change / no change | no change / no change | no change / no change |
| Narrow passage, realistic / stress | not used / not used | not used / not used | not used / not used |

**Each rule's verdict of record** (from its realistic scenarios), against RF-18's:

| Rule | RF-18 | Realistic (of record) | Stress |
| --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e`, both turn 10° left from 9.8 m | helps | **helps** | helps |
| `ext_head_on_6455ca5589`, whoever faces a person with a cane slows | harms | **no change** | harms |

**2. The left-turn rule's verdict does not depend on who is in the crowd.** It reads no factor, so
its runs are the same in both crowds, number for number (severe conflicts 569 against plain ORCA's
804, 10 of 10 seeds; throughput and delay better on 9 of 10; 61% keep to their left). Plain ORCA is
the same in both crowds too: in the avoidance simulator a factor changes no body and no speed, only
what a rule reads.

**3. The cane rule no longer gridlocks the crowd, but it is not shown to be harmless.** With 3
people with a cane in 100 instead of 48, it matched 153 times a run instead of 1,607, and no seed
gridlocked (RF-18: seeds 30902 and 30904). Its collisions still lean worse: collided pairs 216 on
average against plain ORCA's 164, worse on 8 of 10 seeds; collision episodes 290 against 204, 8 of
10. With 10 seeds the sign test needs 9 of 10 (p = 0.11 here), so "no change" means **not shown to
differ**, not shown to be the same. Its stress verdict (harms) says that where it applies often, it
does harm.

| Two-way flow, means over 10 seeds | Severe (T3+T4) | Collided pairs (T4) | Collision episodes | Throughput /min | Delay s | Gridlocked | Rule matches |
| --- | --- | --- | --- | --- | --- | --- | --- |
| plain ORCA (both crowds) | 804 | 164 | 204 | 77.4 | 4.14 | 0 of 10 | 0 |
| cane rule, realistic | 801 (4 of 10 fewer) | 216 (8 of 10 more, n.s.) | 290 (8 of 10 more, n.s.) | 79.2 | 6.65 | 0 of 10 | 153 |
| cane rule, stress (= RF-18) | 814 | 344 | 585 | 65.6 | 16.3 | **2 of 10** | 1,607 |
| set 2, realistic | **587** (10 of 10 fewer) | 89 (7 of 10 fewer, n.s.) | 115 (5 of 10, n.s.) | 109.5 (8 of 10, n.s.) | 1.80 (5 of 10) | 0 | 2,456 |
| set 2, stress (= RF-18) | 673 (9 of 10 fewer) | **271** (9 of 10 more) | **462** (10 of 10 more) | 67.9 | **11.6** (10 of 10 worse) | 0 | 2,744 |

The plain ORCA row's collided pairs come from RF-18's report (the same runs). n.s.: not significant
by the sign test (p ≥ 0.05).

**4. Set 2 goes from harms to helps.** In RF-18 the cane rule took over half of set 2's matches
(13,767 of 27,439) and its collisions with them. In a realistic crowd it takes 1,509 of 24,555; the
left-turn rule does the rest, and set 2 behaves almost as set 1 (severe conflicts 587 against 569).
Set 2's cross-pair conflicts fall from 31,094 to 17,377 over the 10 seeds.

**5. The small scenarios say little either way.** In the bottleneck and the passage, two people
from a realistic crowd met; a cane appeared on 1 seed of 10 (bottleneck, seed 30904), where the cane
rule matched once and changed nothing. RF-18's two-person stress pairs never had a phone (two people
moving on by one through a cycle in which a phone changes every 16 people). As in RF-18, no rule
applies in the narrow passage, and plain ORCA deadlocks there on every seed.

**6. What this means for RF-14 and later rounds.**
- The verdict of record for round 1: **the left-turn rule helps; the cane rule shows no change in
  a realistic crowd and harms where canes are common.** RF-18's "harms" for the cane rule was a
  verdict about a crowd where half carry a cane.
- A rule about a rare factor can only show its effect over more seeds or more people. Under the
  user's decision (2026-10-27) the realistic verdict stands as the verdict of record; the stress
  verdict is the warning. Whether to run more seeds for such rules is open (below).

## Open for the user

1. **The cane rule: "no change" with collisions worse on 8 of 10 seeds.** Should a rule whose
   realistic verdict is "no change" but whose stress verdict is "harms" stay staged for RF-14 as it
   is, or be marked (for example "harms where the factor is common")? The verdict rule does not say.
2. **More seeds for rare factors.** 10 seeds detect only a 9-of-10 effect. With 30 seeds, 21 of
   30 would be enough (p = 0.043; 20 of 30 gives p = 0.099), at a cost of run time only: about 35
   minutes per 10 seeds of the flow's five arms (42 s a run in this run).
