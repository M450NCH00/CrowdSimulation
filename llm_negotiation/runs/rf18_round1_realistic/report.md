# rf18_round1_realistic: the rule set against plain ORCA

Machine-written by `negsim.ruleset_eval` (issue #74, RF-18). Method: `docs/rule-set-evaluation.md`. paired seeds per scenario: flow_realistic 30, bottleneck_realistic 30, passage_realistic 30, flow_stress 10, bottleneck_stress 10, passage_stress 10, baseline `orca_perturbed_v1`, sign test at p < 0.05, verdict rule 2 (`docs/rule-set-evaluation.md`, section 3).

## Rules

| Rule | From | Version |
| --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | `runs/rf31_round1_head_on/rule_db_staging/extracted` | 2 |
| `ext_head_on_6455ca5589` | `runs/rf31_round1_head_on_retry/rule_db_staging/extracted` | 2 |

**Left out (3):**

- `ext_head_on_aacce0961b (RF-31, format 4)`: refused by the loader since RF-31 (constant_roles); its roles hold for both people, so it never matched
- `ext_head_on_4eb7a97c8d (RF-11)`: not expressible in either format (signalling and speaking); nobody signals in ORCA
- `RF-12's three format 3 translations (0ecc2d1a6e, 6455ca5589, aacce0961b)`: replaced by RF-31's format 4 translations of the same rules (D-A); two act as plain ORCA

## Verdicts

| Scenario | `passed_screening` | `cane_rule_alone` | `all_runnable` |
| --- | --- | --- | --- |
| flow_realistic (realistic) | helps | harms | helps |
| bottleneck_realistic (realistic) | no change | no change | no change |
| passage_realistic (realistic) | not used | not used | not used |
| flow_stress (stress) | helps | harms | harms (rule 1: trade-off) |
| bottleneck_stress (stress) | no change | no change | no change |
| passage_stress (stress) | not used | not used | not used |

| Rule | Arm | flow_realistic | bottleneck_realistic | passage_realistic | flow_stress | bottleneck_stress | passage_stress | Realistic | Stress | Of record (realistic) | Flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | `passed_screening` | helps | no change | not used | helps | no change | not used | helps | helps | **helps** | – |
| `ext_head_on_6455ca5589` | `cane_rule_alone` | harms | no change | not used | harms | no change | not used | harms | harms | **harms** | – |

A rule's verdict of record comes from its realistic scenarios; a stress scenario shows whether it works where it applies, and is never a verdict of record on its own (the user's decision of 2026-10-27, issue #112). `harms_where_common`: the rule harms in a stress scenario but not by its verdict of record, flagged for RF-14 (the user's decision of 2026-10-27).

## flow_realistic

`configs/scenarios/bidirectional_flow.yaml`. The two-way flow, 50 + 50, people at sourced shares, new people on every seed.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas). Per seed, mean: n 100, age_65_and_over 20, mobility_aid_cane 3, load_large_suitcase 1, distraction_phone 9, assertiveness_holds_ground 50.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 808.433 | 267.967 | 75.836 | 6.036 | 0 of 30 | 0 | 30.112 | 0.483 / 0.517 |
| `passed_screening` | 577.6 | 116.9 | 103.495 | 1.586 | 0 of 30 | 2508.73 | 59.165 | 0.625 / 0.375 |
| `cane_rule_alone` | 802.833 | 319.667 | 80.765 | 7.728 | 1 of 30 | 161.4 | 57.808 | 0.484 / 0.516 |
| `all_runnable` | 571.933 | 148.9 | 103.285 | 2.822 | 0 of 30 | 2499.33 | 66.271 | 0.618 / 0.382 |
| `reference_default` | 471.767 | 272.267 | 81.496 | 7.946 | 0 of 30 | 10108.8 | 100.764 | 0.695 / 0.305 |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 30/0/0, p = 0; throughput_agents_per_min 25/5/0, p = 0.000325; mean_delay_s 21/9/0, p = 0.0428; collided_pairs 21/9/0, p = 0.0428; collision_episodes 20/10/0, p = 0.0987.
- `cane_rule_alone`: **harms** (gridlocked on seed(s) [30913], where plain ORCA did not). severe_conflicts 14/16/0, p = 0.856; throughput_agents_per_min 17/12/1, p = 0.458; mean_delay_s 12/18/0, p = 0.362; collided_pairs 13/17/0, p = 0.585; collision_episodes 12/18/0, p = 0.362.
- `all_runnable`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 30/0/0, p = 0; throughput_agents_per_min 23/7/0, p = 0.00522; mean_delay_s 16/14/0, p = 0.856; collided_pairs 19/11/0, p = 0.2; collision_episodes 17/13/0, p = 0.585.
- Uncovered conflicts under `passed_screening` (pairs, all seeds; most frequent first): overtaking T2: 9219, overtaking T1: 3326, overtaking T3: 1799, overtaking T4: 1262, crossing T2: 97, none T2: 29.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 12488, not started because one was in force 138036.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): overtaking T2: 35094, head_on T2: 15943, head_on T3: 13045, overtaking T3: 3669, overtaking T4: 3326, head_on T4: 2599.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 1734, not started because one was in force 694.
- Uncovered conflicts under `all_runnable` (pairs, all seeds; most frequent first): overtaking T2: 12081, overtaking T1: 5452, overtaking T3: 2073, overtaking T4: 1677, crossing T2: 95, none T2: 71.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 53280 cross-pair conflicts; plans started 11936, not started because one was in force 131397.
- Uncovered conflicts under `reference_default` (pairs, all seeds; most frequent first): overtaking T2: 763, none T2: 173, crossing T2: 132, crossing T3: 7, crossing T4: 2, crossing T1: 1.
  Rule conflicts: 17587 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.

## bottleneck_realistic

`configs/scenarios/corridor_to_bottleneck.yaml`. Two people from opposite ends of a single-file segment, drawn from a realistic crowd.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, the first of a crowd of 100 at exact shares). Per seed, mean: n 2, age_65_and_over 0.367, mobility_aid_cane 0.133, load_large_suitcase 0.033, distraction_phone 0.167, assertiveness_holds_ground 1.033.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 6.667 | 2.035 | 0 of 30 | 0 | 0.761 | – |
| `passed_screening` | 1 | 0 | 6.667 | 2.035 | 0 of 30 | 1 | 0.857 | – |
| `cane_rule_alone` | 1 | 0 | 6.664 | 2.04 | 0 of 30 | 0.133 | 0.684 | – |
| `all_runnable` | 1 | 0 | 6.664 | 2.04 | 0 of 30 | 1 | 0.64 | – |
| `reference_default` | 1 | 0 | 6.667 | 2.035 | 0 of 30 | 1.367 | 0.717 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/0/30, p = 1; mean_delay_s 0/0/30, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/1/29, p = 1; mean_delay_s 0/1/29, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `all_runnable`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/1/29, p = 1; mean_delay_s 0/1/29, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): single_file_segment T3: 26.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 2, not started because one was in force 0.

## passage_realistic

`configs/scenarios/passage_meet_middle_v1.yaml`. Round 2's narrow passage (two people meet inside it), drawn from a realistic crowd.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, the first of a crowd of 100 at exact shares). Per seed, mean: n 2, age_65_and_over 0.367, mobility_aid_cane 0.133, load_large_suitcase 0.033, distraction_phone 0.167, assertiveness_holds_ground 1.033.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 0 | – | 30 of 30 | 0 | 2.027 | – |
| `passed_screening` | 1 | 0 | 0 | – | 30 of 30 | 0 | 1.581 | – |
| `cane_rule_alone` | 1 | 0 | 0 | – | 30 of 30 | 0 | 1.324 | – |
| `all_runnable` | 1 | 0 | 0 | – | 30 of 30 | 0 | 1.345 | – |
| `reference_default` | 1 | 0 | 0 | – | 30 of 30 | 0 | 1.533 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **not used** (no rule of the set matched on any seed). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/0/30, p = 1; mean_delay_s 0/0/0, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `cane_rule_alone`: **not used** (no rule of the set matched on any seed). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/0/30, p = 1; mean_delay_s 0/0/0, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `all_runnable`: **not used** (no rule of the set matched on any seed). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/0/30, p = 1; mean_delay_s 0/0/0, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- Uncovered conflicts under `passed_screening` (pairs, all seeds; most frequent first): single_file_segment T4: 21, single_file_segment T3: 9.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): single_file_segment T4: 21, single_file_segment T3: 9.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.
- Uncovered conflicts under `all_runnable` (pairs, all seeds; most frequent first): single_file_segment T4: 21, single_file_segment T3: 9.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.
- Uncovered conflicts under `reference_default` (pairs, all seeds; most frequent first): single_file_segment T4: 21, single_file_segment T3: 9.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.

## flow_stress

`configs/scenarios/bidirectional_flow.yaml`. RF-18's flow, its people (48 of 100 with a cane, a suitcase, a phone).

People: `configs/populations/stress_all_factors_v1.yaml` (stress, cycle). Per seed, mean: n 100, age_65_and_over 50, mobility_aid_cane 48, load_large_suitcase 48, distraction_phone 48, assertiveness_holds_ground 36.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 804.4 | 203.7 | 77.411 | 4.143 | 0 of 10 | 0 | 26.603 | 0.492 / 0.508 |
| `passed_screening` | 569.1 | 93.7 | 107.236 | 0.95 | 0 of 10 | 2472.5 | 54.524 | 0.611 / 0.389 |
| `cane_rule_alone` | 813.9 | 585.2 | 65.643 | 16.282 | 2 of 10 | 1607.3 | 47.7 | 0.5 / 0.5 |
| `all_runnable` | 673.4 | 461.6 | 67.863 | 11.609 | 0 of 10 | 2743.9 | 48.133 | 0.583 / 0.417 |
| `reference_default` | 439.3 | 191.2 | 78.295 | 5.18 | 0 of 10 | 8827.5 | 83.722 | 0.694 / 0.306 |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 10/0/0, p = 0.00195; throughput_agents_per_min 9/1/0, p = 0.0215; mean_delay_s 9/1/0, p = 0.0215; collided_pairs 7/3/0, p = 0.344; collision_episodes 7/3/0, p = 0.344.
- `cane_rule_alone`: **harms** (gridlocked on seed(s) [30902, 30904], where plain ORCA did not). severe_conflicts 5/5/0, p = 1; throughput_agents_per_min 2/8/0, p = 0.109; mean_delay_s 2/8/0, p = 0.109; collided_pairs 2/8/0, p = 0.109; collision_episodes 2/8/0, p = 0.109.
- `all_runnable`: **harms** (more collided pairs and collision episodes than plain ORCA). severe_conflicts 9/1/0, p = 0.0215; throughput_agents_per_min 3/7/0, p = 0.344; mean_delay_s 0/10/0, p = 0.00195; collided_pairs 1/9/0, p = 0.0215; collision_episodes 0/10/0, p = 0.00195.
- Uncovered conflicts under `passed_screening` (pairs, all seeds; most frequent first): overtaking T2: 1721, overtaking T1: 1144, overtaking T3: 579, overtaking T4: 371, crossing T2: 16, crossing T3: 6.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 4077, not started because one was in force 45373.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): overtaking T2: 16593, head_on T2: 5011, overtaking T4: 1678, overtaking T3: 1403, head_on T3: 1250, crossing T2: 719.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 1183, not started because one was in force 8962.
- Uncovered conflicts under `all_runnable` (pairs, all seeds; most frequent first): overtaking T2: 12560, overtaking T4: 1231, overtaking T3: 930, overtaking T1: 647, none T2: 238, crossing T2: 127.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 31094 cross-pair conflicts; plans started 3828, not started because one was in force 32083.
- Uncovered conflicts under `reference_default` (pairs, all seeds; most frequent first): overtaking T2: 344, crossing T2: 41, none T2: 29, crossing T3: 1.
  Rule conflicts: 3804 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.

## bottleneck_stress

`configs/scenarios/corridor_to_bottleneck.yaml`. RF-18's bottleneck, its people.

People: `configs/populations/stress_all_factors_v1.yaml` (stress, cycle). Per seed, mean: n 2, age_65_and_over 1, mobility_aid_cane 0.8, load_large_suitcase 0.5, distraction_phone 0, assertiveness_holds_ground 0.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 0 | 0.74 | – |
| `passed_screening` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1 | 0.711 | – |
| `cane_rule_alone` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 0.2 | 0.642 | – |
| `all_runnable` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1 | 0.557 | – |
| `reference_default` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1.5 | 0.65 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- `all_runnable`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): single_file_segment T3: 8.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 2, not started because one was in force 0.

## passage_stress

`configs/scenarios/passage_meet_middle_v1.yaml`. RF-18's passage, its people.

People: `configs/populations/stress_all_factors_v1.yaml` (stress, cycle). Per seed, mean: n 2, age_65_and_over 1, mobility_aid_cane 0.8, load_large_suitcase 0.5, distraction_phone 0, assertiveness_holds_ground 0.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 0 | – | 10 of 10 | 0 | 2.102 | – |
| `passed_screening` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.652 | – |
| `cane_rule_alone` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.536 | – |
| `all_runnable` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.407 | – |
| `reference_default` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.637 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **not used** (no rule of the set matched on any seed). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/0, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- `cane_rule_alone`: **not used** (no rule of the set matched on any seed). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/0, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- `all_runnable`: **not used** (no rule of the set matched on any seed). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/0, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- Uncovered conflicts under `passed_screening` (pairs, all seeds; most frequent first): single_file_segment T4: 9, single_file_segment T3: 1.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): single_file_segment T4: 9, single_file_segment T3: 1.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.
- Uncovered conflicts under `all_runnable` (pairs, all seeds; most frequent first): single_file_segment T4: 9, single_file_segment T3: 1.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.
- Uncovered conflicts under `reference_default` (pairs, all seeds; most frequent first): single_file_segment T4: 9, single_file_segment T3: 1.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.

Copied into the run's own staging database: 5 rule file(s), byte for byte (`rule_db_staging/MANIFEST.json`).
