# rf18_round1_realistic: the rule set against plain ORCA

Machine-written by `negsim.ruleset_eval` (issue #74, RF-18). Method: `docs/rule-set-evaluation.md`. 10 paired seeds per scenario, baseline `orca_perturbed_v1`, sign test at p < 0.05, verdict rule 2 (`docs/rule-set-evaluation.md`, section 3).

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
| flow_realistic (realistic) | helps | no change | helps |
| bottleneck_realistic (realistic) | no change | no change | no change |
| passage_realistic (realistic) | not used | not used | not used |
| flow_stress (stress) | helps | harms | harms (rule 1: trade-off) |
| bottleneck_stress (stress) | no change | no change | no change |
| passage_stress (stress) | not used | not used | not used |

| Rule | Arm | flow_realistic | bottleneck_realistic | passage_realistic | flow_stress | bottleneck_stress | passage_stress | Realistic | Stress | Of record (realistic) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | `passed_screening` | helps | no change | not used | helps | no change | not used | helps | helps | **helps** |
| `ext_head_on_6455ca5589` | `cane_rule_alone` | no change | no change | not used | harms | no change | not used | no change | harms | **no change** |

A rule's verdict of record comes from its realistic scenarios; a stress scenario shows whether it works where it applies, and is never a verdict of record on its own (the user's decision of 2026-10-27, issue #112).

## flow_realistic

`configs/scenarios/bidirectional_flow.yaml`. The two-way flow, 50 + 50, people at sourced shares, new people on every seed.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas). Per seed, mean: n 100, age_65_and_over 20, mobility_aid_cane 3, load_large_suitcase 1, distraction_phone 9, assertiveness_holds_ground 50.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 804.4 | 203.7 | 77.411 | 4.143 | 0 of 10 | 0 | 30.994 | 0.492 / 0.508 |
| `passed_screening` | 569.1 | 93.7 | 107.236 | 0.95 | 0 of 10 | 2472.5 | 65.103 | 0.611 / 0.389 |
| `cane_rule_alone` | 800.8 | 290.1 | 79.226 | 6.648 | 0 of 10 | 152.8 | 59.541 | 0.487 / 0.513 |
| `all_runnable` | 586.8 | 114.9 | 109.531 | 1.802 | 0 of 10 | 2455.5 | 71.395 | 0.628 / 0.372 |
| `reference_default` | 449.8 | 220.6 | 87.088 | 6.367 | 0 of 10 | 9210.4 | 108.738 | 0.687 / 0.313 |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 10/0/0, p = 0.00195; throughput_agents_per_min 9/1/0, p = 0.0215; mean_delay_s 9/1/0, p = 0.0215; collided_pairs 7/3/0, p = 0.344; collision_episodes 7/3/0, p = 0.344.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 4/6/0, p = 0.754; throughput_agents_per_min 4/6/0, p = 0.754; mean_delay_s 3/7/0, p = 0.344; collided_pairs 2/8/0, p = 0.109; collision_episodes 2/8/0, p = 0.109.
- `all_runnable`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 10/0/0, p = 0.00195; throughput_agents_per_min 8/2/0, p = 0.109; mean_delay_s 5/5/0, p = 1; collided_pairs 7/3/0, p = 0.344; collision_episodes 5/5/0, p = 1.
- Uncovered conflicts under `passed_screening` (pairs, all seeds; most frequent first): overtaking T2: 1721, overtaking T1: 1144, overtaking T3: 579, overtaking T4: 371, crossing T2: 16, crossing T3: 6.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 4077, not started because one was in force 45373.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): overtaking T2: 13036, head_on T2: 6246, head_on T3: 4132, overtaking T3: 1278, overtaking T4: 1102, head_on T4: 956.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 593, not started because one was in force 179.
- Uncovered conflicts under `all_runnable` (pairs, all seeds; most frequent first): overtaking T2: 3298, overtaking T1: 1917, overtaking T3: 662, overtaking T4: 448, crossing T2: 18, crossing T3: 3.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 17377 cross-pair conflicts; plans started 3860, not started because one was in force 42994.
- Uncovered conflicts under `reference_default` (pairs, all seeds; most frequent first): overtaking T2: 218, crossing T2: 57, none T2: 52, crossing T3: 4, crossing T1: 1, crossing T4: 1.
  Rule conflicts: 4377 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.

## bottleneck_realistic

`configs/scenarios/corridor_to_bottleneck.yaml`. Two people from opposite ends of a single-file segment, drawn from a realistic crowd.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, the first of a crowd of 100 at exact shares). Per seed, mean: n 2, age_65_and_over 0.4, mobility_aid_cane 0.1, load_large_suitcase 0.1, distraction_phone 0.2, assertiveness_holds_ground 1.2.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 0 | 0.731 | – |
| `passed_screening` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1 | 0.871 | – |
| `cane_rule_alone` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 0.1 | 0.657 | – |
| `all_runnable` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1 | 0.615 | – |
| `reference_default` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1.4 | 0.707 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- `all_runnable`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): single_file_segment T3: 9.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 0, not started because one was in force 0.

## passage_realistic

`configs/scenarios/passage_meet_middle_v1.yaml`. Round 2's narrow passage (two people meet inside it), drawn from a realistic crowd.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, the first of a crowd of 100 at exact shares). Per seed, mean: n 2, age_65_and_over 0.4, mobility_aid_cane 0.1, load_large_suitcase 0.1, distraction_phone 0.2, assertiveness_holds_ground 1.2.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 0 | – | 10 of 10 | 0 | 2.422 | – |
| `passed_screening` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.874 | – |
| `cane_rule_alone` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.586 | – |
| `all_runnable` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.582 | – |
| `reference_default` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.767 | – |

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
