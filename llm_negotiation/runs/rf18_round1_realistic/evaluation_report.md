# RF-33, round 1 in a realistic crowd: do the verdicts of RF-18 hold?

Issue #112. No model call, USD 0. Method: `docs/rule-set-evaluation.md` (section 1.1) and
`docs/population-profiles.md`. The machine-written tables are `report.md`; the numbers here are from
`summary.json` and each run's `measures.json`. Baseline `orca_perturbed_v1`, verdict rule 2.

**Two runs into one folder** (recorded in `config.json`, `seeds_changed`):
1. 2026-10-27, 11:40 to 12:55 UTC, commit 99aeab8c (clean): 300 runs, every scenario on 10 seeds
   (30901 to 30910).
2. 13:28 to 14:44 UTC, commit 84385390 (clean), after the user decided on more seeds where a factor
   is rare: the three realistic scenarios extended to 30 seeds (30911 to 30930 added, 300 runs).
   The runs on seeds 30901 to 30910 were kept, not run again: a run on a given seed does not depend
   on how many seeds there are.

So: 6 scenarios × 5 arms (plain ORCA, 3 judged rule sets, 1 reference); realistic 30 seeds, stress 10;
600 runs.

## What was run

RF-18's config (`configs/rule_set_evaluation/rf18_round1.yaml`, issue #74) with the same rules,
arms, base seed and verdict rule; only the people, and the realistic scenarios' number of seeds,
change. Each of RF-18's three scenarios runs twice:

| Scenario | People | Seeds | Purpose |
| --- | --- | --- | --- |
| `*_realistic` | `singapore_street_v1`: sourced shares, exact on every seed, new people on every seed. In the flow, per 100: 20 aged 65 and over, 3 with a cane, 9 looking at a phone, 1 with a large suitcase (placeholder), 50 holding their ground (placeholder). The two-person scenarios take the first two of a crowd of 100 | 30 | **verdict of record** |
| `*_stress` | `stress_all_factors_v1`: RF-18's people. Per 100: 50 aged 70, 48 with a cane, 48 with a suitcase, 48 on a phone, 36 holding their ground | 10 | beside it, labelled |

The realistic profile's limits: residents only; the cane share is from the United States (2011) and
the phone share from Spain (2019); a suitcase, a cane under 65 and assertiveness are placeholders
(`docs/population-profiles.md`).

**Check: the stress runs are RF-18's runs.** All 150 give exactly RF-18's measures (every measure
but wall time), so nothing in the build changed an earlier run.

## Findings

**1. The verdicts** (rule 2; rule 1 differs only where shown):

| Scenario | Set 1 (left turn) | Cane rule alone | Set 2 (both) |
| --- | --- | --- | --- |
| Two-way flow, **realistic, 30 seeds** | **helps** | **harms** (gridlock on 1 seed of 30) | **helps** |
| *the same, its first 10 seeds* | *helps* | *no change* | *helps* |
| Two-way flow, stress (= RF-18) | helps | harms | harms (rule 1: trade-off) |
| Opposing bottleneck, realistic / stress | no change / no change | no change / no change | no change / no change |
| Narrow passage, realistic / stress | not used / not used | not used / not used | not used / not used |

**Each rule's verdict of record** (from its realistic scenarios), against RF-18's:

| Rule | RF-18 | Realistic (of record) | Stress | Flag |
| --- | --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e`, both turn 10° left from 9.8 m | helps | **helps** | helps | – |
| `ext_head_on_6455ca5589`, whoever faces a person with a cane slows | harms | **harms** | harms | – (its verdict of record is harms itself) |

**2. The cane rule harms even in a realistic crowd, though rarely.** With 3 people with a cane in
100, it gridlocks the flow on 1 seed of 30: on seed 30913 its run reached the time limit with 80 of
100 people arrived, where plain ORCA and both other sets finished. By the verdict rule fixed before
RF-18's run, one gridlock where plain ORCA has none is harm. Its other measures do not differ from
plain ORCA's (severe conflicts 14 of 30 seeds fewer; collided pairs 13 of 30 fewer; neither
significant). In RF-18's crowd it gridlocked 2 of 10 seeds. **On its first 10 seeds the realistic
verdict was "no change"**: seed 30913 is one of the 20 seeds added. This is the case the user's
decision for more seeds was meant for.

**3. The left-turn rule helps, and with 30 seeds it also cuts collisions.** It reads no factor, so
on the first 10 seeds its runs are the same in both crowds, number for number. Over 30 seeds:
severe conflicts fewer on 30 of 30, throughput better on 25, delay on 21, and **collided pairs
fewer on 21 of 30 (p = 0.043)**, which 10 seeds could not show. Plain ORCA is the same in both
crowds too: in the avoidance simulator a factor changes no body and no speed, only what a rule
reads.

**4. Set 2 helps in a realistic crowd.** The cane rule's few matches (148 a run of 2,499; the
left-turn rule has the other 2,351) do not gridlock it on any seed; set 2 behaves almost as set 1 (severe conflicts 572 against
578). In RF-18's crowd the cane rule took over half of set 2's matches and set 2 harmed.

| Two-way flow, realistic, means over 30 seeds | Severe (T3+T4) | Collided pairs (T4) | Collision episodes | Throughput /min | Delay s | Gridlocked | Rule matches |
| --- | --- | --- | --- | --- | --- | --- | --- |
| plain ORCA | 808 | 187 | 268 | 75.8 | 6.04 | 0 of 30 | 0 |
| set 1, left turn | **578** (30 of 30 fewer) | **94** (21 of 30 fewer) | 117 (20 of 30, n.s.) | **103.5** (25 of 30) | **1.59** (21 of 30) | 0 | 2,509 |
| cane rule alone | 803 (n.s.) | 208 (n.s.) | 320 (n.s.) | 80.8 | 7.73 | **1 of 30** | 161 |
| set 2, both | **572** (30 of 30 fewer) | 111 (19 of 30, n.s.) | 149 (n.s.) | **103.3** (23 of 30) | 2.82 (n.s.) | 0 | 2,499 |
| reference (hand-written) | 472 | – | 272 | 81.5 | 7.95 | 0 | 10,109 |

n.s.: not significant by the sign test (p ≥ 0.05; with 30 seeds, 21 of 30 must agree). Plain
ORCA's means over 30 seeds differ from those over 10 (804 severe conflicts, 164 collided pairs) only
because more seeds are averaged.

**5. The small scenarios say little either way.** In the bottleneck and the passage two people
from a realistic crowd met; a cane appeared on 4 seeds of 30. In the bottleneck the cane rule
matched on those and changed nothing measurable. RF-18's two-person stress pairs never had a phone
(two people moving on by one through a cycle in which a phone changes every 16 people). As in RF-18,
no rule applies in the narrow passage, and plain ORCA deadlocks there on every seed.

**6. What this means for RF-14 and later rounds.**
- Round 1's verdicts of record: **the left-turn rule helps; the cane rule harms**, in a realistic
  crowd as in RF-18's, but on 1 seed of 30 rather than 2 of 10. Set 2 helps.
- The flag `harms_where_common` is given to no round 1 rule: the cane rule's verdict of record is
  harms itself. It would have been given on 10 seeds.
- 10 seeds were too few for a rule about a rare factor: the verdict changed between 10 and 30.

## Open for the user

1. **One gridlock in 30 seeds is "harms".** That is the verdict rule fixed before RF-18's run (any
   seed where the rule gridlocks and plain ORCA does not), and it is applied as fixed. Whether a rare
   gridlock should weigh as much as a frequent one is not something this issue changes.
