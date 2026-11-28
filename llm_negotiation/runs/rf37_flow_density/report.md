# rf37_flow_density: the rule set against plain ORCA

Machine-written by `negsim.ruleset_eval` (issue #74, RF-18). Method: `docs/rule-set-evaluation.md`. paired seeds per scenario: flow_15 10, flow_75 10, baseline `orca_perturbed_v1`, sign test at p < 0.05, verdict rule 2 (`docs/rule-set-evaluation.md`, section 3).

## Rules

| Rule | From | Version |
| --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | `runs/rf31_round1_head_on/rule_db_staging/extracted` | 2 |
| `ext_head_on_6455ca5589` | `runs/rf31_round1_head_on_retry/rule_db_staging/extracted` | 2 |

**Left out (2):**

- `ext_head_on_aacce0961b (RF-31, format 4)`: refused by the loader since RF-31 (constant_roles); its roles hold for both people, so it never matched
- `ext_head_on_4eb7a97c8d (RF-11)`: not expressible in either format (signalling and speaking); nobody signals in ORCA

## Verdicts

| Scenario | `passed_screening` | `cane_rule_alone` | `all_runnable` |
| --- | --- | --- | --- |
| flow_15 (realistic) | helps | no change | helps |
| flow_75 (realistic) | helps | harms | helps |

| Rule | Arm | flow_15 | flow_75 | Realistic | Of record (realistic) | Flag |
| --- | --- | --- | --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | `passed_screening` | helps | helps | helps | **helps** | – |
| `ext_head_on_6455ca5589` | `cane_rule_alone` | no change | harms | harms | **harms** | – |

A rule's verdict of record comes from its realistic scenarios; a stress scenario shows whether it works where it applies, and is never a verdict of record on its own (the user's decision of 2026-10-27, issue #112). `harms_where_common`: the rule harms in a stress scenario but not by its verdict of record, flagged for RF-14 (the user's decision of 2026-10-27).

## flow_15

`configs/scenarios/bidirectional_flow.yaml`. The two-way flow, 15 + 15, people at sourced shares.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas). Per seed, mean: n 30, age_65_and_over 7, mobility_aid_cane 1, load_large_suitcase 0, distraction_phone 3, assertiveness_holds_ground 15.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 81.7 | 9.8 | 41.742 | 0.544 | 0 of 10 | 0 | 8.687 | 0.5 / 0.5 |
| `passed_screening` | 61.3 | 0.8 | 46.392 | 0.115 | 0 of 10 | 225.1 | 14.271 | 0.5 / 0.5 |
| `cane_rule_alone` | 85.6 | 11.6 | 39.003 | 1.765 | 0 of 10 | 17.2 | 17.694 | 0.503 / 0.497 |
| `all_runnable` | 66.9 | 3.7 | 44.164 | 1.033 | 0 of 10 | 225.5 | 15.037 | 0.5 / 0.5 |
| `reference_default` | 53.5 | 9.2 | 35.427 | 2.38 | 0 of 10 | 595.3 | 20.421 | 0.523 / 0.477 |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 10/0/0, p = 0.00195; throughput_agents_per_min 7/3/0, p = 0.344; mean_delay_s 7/3/0, p = 0.344; collided_pairs 10/0/0, p = 0.00195; collision_episodes 10/0/0, p = 0.00195.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts; worse mean_delay_s). severe_conflicts 3/5/2, p = 0.727; throughput_agents_per_min 4/6/0, p = 0.754; mean_delay_s 0/10/0, p = 0.00195; collided_pairs 4/6/0, p = 0.754; collision_episodes 4/6/0, p = 0.754.
- `all_runnable`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 9/1/0, p = 0.0215; throughput_agents_per_min 5/5/0, p = 1; mean_delay_s 3/7/0, p = 0.344; collided_pairs 8/1/1, p = 0.0391; collision_episodes 8/1/1, p = 0.0391.
- Uncovered conflicts under `passed_screening` (pairs, all seeds; most frequent first): overtaking T1: 124, overtaking T3: 75, overtaking T4: 2.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 302, not started because one was in force 4200.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): overtaking T2: 636, head_on T3: 625, head_on T2: 409, head_on T4: 95, overtaking T1: 82, overtaking T3: 79.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 81, not started because one was in force 4.
- Uncovered conflicts under `all_runnable` (pairs, all seeds; most frequent first): overtaking T1: 206, overtaking T2: 152, overtaking T3: 81, overtaking T4: 19.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 1599 cross-pair conflicts; plans started 297, not started because one was in force 3986.
- Uncovered conflicts under `reference_default` (pairs, all seeds; most frequent first): overtaking T2: 71.
  Rule conflicts: 112 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.

## flow_75

`configs/scenarios/bidirectional_flow.yaml`. The two-way flow, 75 + 75, people at sourced shares.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas). Per seed, mean: n 150, age_65_and_over 32, mobility_aid_cane 5, load_large_suitcase 2, distraction_phone 13, assertiveness_holds_ground 75.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1634.2 | 612.1 | 103.644 | 8.111 | 2 of 10 | 0 | 57.325 | 0.518 / 0.482 |
| `passed_screening` | 1086 | 220.5 | 129.98 | 1.676 | 0 of 10 | 5586.8 | 91.646 | 0.715 / 0.285 |
| `cane_rule_alone` | 1686.6 | 1149.4 | 90.783 | 15.273 | 3 of 10 | 462.3 | 120.34 | 0.553 / 0.447 |
| `all_runnable` | 1149.8 | 517 | 105.025 | 7.365 | 0 of 10 | 5784.5 | 89.05 | 0.695 / 0.305 |
| `reference_default` | 1122.6 | 1343 | 85.686 | 21.121 | 3 of 10 | 33579.4 | 151.209 | 0.792 / 0.208 |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 10/0/0, p = 0.00195; throughput_agents_per_min 9/1/0, p = 0.0215; mean_delay_s 4/6/0, p = 0.754; collided_pairs 5/5/0, p = 1; collision_episodes 4/6/0, p = 0.754.
- `cane_rule_alone`: **harms** (gridlocked on seed(s) [30903], where plain ORCA did not). severe_conflicts 4/6/0, p = 0.754; throughput_agents_per_min 0/9/1, p = 0.00391; mean_delay_s 1/9/0, p = 0.0215; collided_pairs 4/6/0, p = 0.754; collision_episodes 2/8/0, p = 0.109.
- `all_runnable`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 9/1/0, p = 0.0215; throughput_agents_per_min 4/6/0, p = 0.754; mean_delay_s 4/6/0, p = 0.754; collided_pairs 5/5/0, p = 1; collision_episodes 5/5/0, p = 1.
- Uncovered conflicts under `passed_screening` (pairs, all seeds; most frequent first): overtaking T2: 4667, overtaking T1: 1912, overtaking T3: 1157, overtaking T4: 760, crossing T2: 114, crossing T3: 14.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 10426, not started because one was in force 101310.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): overtaking T2: 22394, head_on T2: 13119, head_on T3: 8962, overtaking T4: 3385, overtaking T3: 2054, crossing T2: 1400.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 1560, not started because one was in force 812.
- Uncovered conflicts under `all_runnable` (pairs, all seeds; most frequent first): overtaking T2: 11647, overtaking T1: 3047, overtaking T4: 1338, overtaking T3: 1275, crossing T2: 214, none T2: 149.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 38721 cross-pair conflicts; plans started 9374, not started because one was in force 100741.
- Uncovered conflicts under `reference_default` (pairs, all seeds; most frequent first): none T2: 409, overtaking T2: 321, crossing T2: 128, crossing T3: 4.
  Rule conflicts: 32264 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.

Copied into the run's own staging database: 5 rule file(s), byte for byte (`rule_db_staging/MANIFEST.json`).
