# RF-18, round 1: do the extracted rules help in the simulation?

Issue #74. Run of 2026-10-27, no model call, USD 0. Method: `docs/rule-set-evaluation.md`; the
meaning of "helps" was fixed with the user before any code or run (`WORK_LOG-74.md`, task 0). The
machine-written tables are `report.md`; the numbers here are from `summary.json` and each run's
`measures.json`. 150 runs: 3 scenarios × 5 arms (plain ORCA, 3 judged rule sets, 1 reference) × 10
paired seeds (30901 to 30910), baseline `orca_perturbed_v1`.

## What was run

| Arm | Rules | Note |
| --- | --- | --- |
| `plain` | none | plain ORCA |
| `passed_screening` | `ext_head_on_0ecc2d1a6e` v2 | set 1: both turn 10° left from 9.8 m until the other passes |
| `cane_rule_alone` | `ext_head_on_6455ca5589` v3 | whoever faces a person with a cane slows (to 0.75, and with a plan if they give way) |
| `all_runnable` | both | set 2 |
| `reference_default` | `rule_db/` `default` | issue #28's hand-written seed rules (keep left head-on and three more); numbers only, no verdict |

**Left out (3):** `aacce0961b` (refused by the loader since RF-31, `constant_roles`); `4eb7a97c8d`
(signalling, not expressible); RF-12's format 3 translations (replaced by RF-31's, two of them plain
ORCA in effect).

**Found before any run: round 1's two rules clash.** Both translations have priority 500, and in a
head-on where one person has a cane both match with different directives, so the loader refused
them together (`rule-matching.md`, section 4). By the user's choice the narrower rule wins where both
match: the cane rule was switched on as v3, the same rule with priority 600, in this run's own
staging database only.

**Check:** seeds 30901 and 30902 of the flow are RF-31's two screening runs. Plain ORCA, the left-turn
rule and the cane rule each give the same outcome on both seeds as RF-31 recorded (status, time,
collisions and every tier count), although the rules here are copies, and the cane rule a new
version.

## Findings

**1. The verdicts.** Rule 1 was fixed before the run; **rule 2, collisions counting separately, is the
user's decision of 2026-10-27 after it** (`docs/rule-set-evaluation.md`, section 3), and is the
verdict of record. They differ for set 2 only.

| Scenario | Set 1 (left turn) | Cane rule alone | Set 2 (both) |
| --- | --- | --- | --- |
| Two-way flow, 50 + 50 | **helps** | **harms** | **harms** (rule 1: trade-off) |
| Opposing bottleneck, 2 people | no change | no change | no change |
| Narrow passage (round 2's layout), 2 people | not used | not used | not used |

Per rule (the arm with it alone): **`ext_head_on_0ecc2d1a6e` helps** (in the flow); **`ext_head_on_6455ca5589`
harms** (it gridlocks the flow on seeds 30902 and 30904, as screening found on 30902).

**2. The two-way flow** (means over 10 seeds; the test is over the seeds):

| Arm | Severe conflicts (T3+T4 pairs) | of them collided (T4) | Collision episodes | Throughput /min | Delay s | Gridlocked | On their left |
| --- | --- | --- | --- | --- | --- | --- | --- |
| plain ORCA | 804 | 164 | 204 | 77.4 | 4.14 | 0 of 10 | 0.49 |
| set 1, left turn | **569** (10 of 10 fewer) | 75 (7 of 10 fewer, n.s.) | 94 (7 of 10, n.s.) | **107.2** (9 of 10) | **0.95** (9 of 10) | 0 | **0.61** (10 of 10) |
| cane rule alone | 814 (5 of 10, n.s.) | 344 (8 of 10 more, n.s.) | 585 (8 of 10 more, n.s.) | 65.6 | 16.3 | **2 of 10** | 0.50 |
| set 2, both | **673** (9 of 10 fewer) | **271** (9 of 10 more) | **462** (10 of 10 more) | 67.9 | **11.6** (10 of 10 worse) | 0 | 0.58 |
| reference (hand-written) | 439 (10 of 10 fewer) | 139 (n.s.) | 191 (n.s.) | 78.3 | 5.18 | 0 | 0.69 |

n.s.: not significant by the sign test (p ≥ 0.05). Plain ORCA's collisions vary widely by seed (46
to 577), which is why halving the mean is not significant for set 1.

- **The left-turn rule helps, by the rule fixed before the run**: fewer severe conflicts on every
  seed, the crowd through faster on 9 of 10, less delay on 9 of 10, and no gridlock. Its gain is in
  **near misses** (T3 pairs fewer on 10 of 10, p = 0.002); collisions are fewer on 7 of 10, which is
  not significant. It also makes the crowd keep to its left (61% against 49%), although the agents
  of Step 1 mostly passed on their right (47 of 76 sessions, RF-31).
- **The cane rule harms**: it gridlocks the flow on 2 of 10 seeds, with 2.9 times plain ORCA's
  collision episodes on average. Half this crowd carries a cane, so the rule applies far more often
  than it would in a real crowd (limitation 2).
- **Set 2 harms under rule 2; it was a trade-off by rule 1, the rule fixed before the run, which
  understated its harm.**
  Its severe conflicts are fewer (9 of 10), but only because near misses are fewer: **collided pairs
  are more on 9 of 10 seeds (p = 0.02) and collision episodes more on all 10 (p = 0.002)**, and delay
  is worse on all 10. Rule 1's main measure counts a pair at T3 or T4 alike, so a pair that collides
  instead of nearly missing is not counted as worse; the user decided that collisions count
  separately (rule 2), under which set 2 harms. The left-turn rule still helps under rule 2: its
  collisions are not worse (fewer on 7 of 10 seeds).
- **The hand-written reference** (`keep_left_head_on` and three more, issue #28; fixtures that make
  no claim about people) cuts severe conflicts further than the extracted rule (439 against 569) and
  makes more of the crowd keep left (69%), with collisions and throughput as plain ORCA's and delay a
  little worse. It is a reference, not judged.

**3. The two small scenarios.**

- **Opposing bottleneck: no change.** The two meet as a `single_file_segment` pair for most of the
  encounter and become `head_on` only for the last two steps before they pass, so the left-turn rule
  matches once, starts its plans too late to change anything, and every number is plain ORCA's to the
  third decimal. The cane rule matched on 2 of the 10 seeds (the two with a cane in a mixed pair),
  with the same result.
- **Narrow passage: not used.** Plain ORCA deadlocks on every seed (they start face to face, inside
  the passage); every arm does too. No rule matches: the pair is `single_file_segment` throughout, a
  class round 1's head-on rules do not cover. This is round 2's own scenario.

**4. Rule conflicts** (the flow, all seeds):

- **Pairs matched by more than one rule: 0** in every extracted arm; **ambiguous matches: 0** (the
  clash was settled by priority before the run). The reference set has 3,804 pairs matched by more
  than one of its rules over their life, settled by priority as documented.
- **Cross-pair conflicts: 31,094 in set 2** (0 in either rule alone): a person told to slow down by
  the cane rule towards one neighbour and not by the left-turn rule towards another; the smallest
  speed scale applies (`rule-matching.md`, section 7), so **the cane rule's slowing spreads** to that
  person's other encounters.
- **Plans not started because one was in force:** under the left-turn rule, 45,373 matches did not
  start a plan, against 4,077 that did. A person runs one plan at a time (`rule-matching.md`,
  section 7), so in a dense flow the first left turn is held while several others pass. What the rule
  does in a crowd is shaped as much by this policy as by the rule.

**5. Uncovered conflicts: what no rule covers.** Under set 2 in the flow (pairs at T1 or above that no
rule matched, all seeds): **overtaking** 15,368 (T2 12,560, T4 1,231, T3 930, T1 647), then a pair with
no class (`none`, 238) and crossing (127 at T2). Under set 1 alone, overtaking 3,815 and crossing 22.
In the bottleneck and the passage: **single-file segments** (every run of the passage).

So the conflicts round 1's rules leave are **people walking the same way, one catching up**
(overtaking), and **meeting in a single-file passage**. These are the scenarios already next in the
track: round 2 (the narrow passage) and round 3 (someone behind says "excuse me"). The loop agrees
with the order of #55; nothing new is proposed.

**6. Cost per step**, towards 10,000 agents (`benchmark_passed_screening.json`,
`benchmark_all_runnable.json`; `python -m negsim.rules.benchmark`, the two-way flow at the same
density at each size, 100 steps, median of 3 repeats, the crowd given this run's people; run with
nothing else on the machine, no sleep events):

| Crowd | Plain ORCA ms/step | Set 1 ms/step | Set 2 ms/step | Inside the rule provider (set 1, set 2) |
| --- | --- | --- | --- | --- |
| 100 | 70.4 / 70.1 | 129.7 (×1.84) | 121.1 (×1.73) | 49.0, 45.7 ms (38% of a rule step) |
| 1,000 | 686.7 / 673.8 | 1,037.6 (×1.51) | 1,057.7 (×1.57) | 363.6, 365.0 ms (35%) |

(Plain ORCA was timed beside each set; both are given.) For comparison, issue #28's hand-written
`default` set on 2026-10-15: ×2.32 at 100 and ×2.98 at 1,000 (`runs/si2_benchmark/benchmark.json`;
its absolute times are not comparable, as plain ORCA then took 52 ms at 100). **The rules add about
half again to a step at 1,000 agents; plain ORCA itself grows about tenfold from 100 to 1,000** (so
roughly 7 s a step at 10,000 if it keeps growing linearly, an extrapolation, not a measurement): the
10,000-agent goal is limited by ORCA and neighbour search before it is limited by the rules. A third
of a rule step is matching; the rest is the different motion the rules cause.

## What this means for the track

- **For RF-14 (#69):** `ext_head_on_0ecc2d1a6e` **helps** in the simulation; `ext_head_on_6455ca5589`
  **harms**. By the two filters (#55, "Decisions"), RF-14 still grades both against human evidence.
  The left-turn rule, if supported, would be promoted; if not, it is a heuristic that reduces near
  misses, not a model of people (and it sends people left where the LLM agents went right).
- **For RF-32 (#110):** the rule worth checking with three or four LLM agents is the left-turn rule.
- **The rules of round 1 cover head-ons only.** Most of what goes wrong in the flow is overtaking,
  and the passage is a single-file meeting; rounds 2 and 3 are aimed at exactly these.

## The user's decisions after the run (2026-10-27)

1. **Collisions count separately** (rule 2, above): set 2 harms; the other verdicts are unchanged.
   Re-judged from the runs' `measures.json`, with no simulation run again.
2. **Realistic scenarios wherever possible.** Half this crowd carries a cane (crowd screening's mix),
   which decides how often the cane rule applies: its "harms" is a verdict about a crowd that does not
   exist. People's factors should come at sourced, realistic shares, with scenarios of exaggerated
   shares kept only to test rules that would rarely apply in a normal one, and labelled so. The cane
   rule's verdict is to be redone in a realistic crowd: RF-33 (#112).

## Limitations

1. Two of the three scenarios have two people; only the flow is a crowd. One crowd size (100) in the
   runs; the benchmark adds 1,000.
2. Half the crowd carries a cane, and a rule reads a cane at any distance (Step 1's agents saw one only
   within 5 m).
3. "Covered" means a rule matched the pair at some point: the bottleneck's pair counts as covered
   although it was a single-file meeting for most of its encounter.
4. The verdict is about the simulation, not about people: whether a rule is what people do is RF-14's.
5. Wall time per step in `report.md` was measured while other work ran on the machine (indicative
   only); the benchmark was run on a quiet machine.

## Files

`report.md` (machine-written), `summary.json`, `config.json` (with every file copied),
`rule_db_staging/` (the run's own database: five rule files and three rule sets),
`runs/<scenario>/<arm>/<seed>/` (`config.json`, `outcome.json`, `measures.json`; the bulky logs,
`events.jsonl` too, are not committed and are rebuilt with `--overwrite`), `benchmark_*.json`.
