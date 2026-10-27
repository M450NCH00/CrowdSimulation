# rf18_round1: the rule set against plain ORCA

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
| flow | helps | harms | harms (rule 1: trade-off) |
| bottleneck | no change | no change | no change |
| passage | not used | not used | not used |

| Rule | Arm | flow | bottleneck | passage | Overall |
| --- | --- | --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | `passed_screening` | helps | no change | not used | **helps** |
| `ext_head_on_6455ca5589` | `cane_rule_alone` | harms | no change | not used | **harms** |

## flow

`configs/scenarios/bidirectional_flow.yaml`. The two-way flow, 50 + 50, as crowd screening.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 804.4 | 203.7 | 77.411 | 4.143 | 0 of 10 | 0 | 28.799 | 0.492 / 0.508 |
| `passed_screening` | 569.1 | 93.7 | 107.236 | 0.95 | 0 of 10 | 2472.5 | 58.074 | 0.611 / 0.389 |
| `cane_rule_alone` | 813.9 | 585.2 | 65.643 | 16.282 | 2 of 10 | 1607.3 | 52.805 | 0.5 / 0.5 |
| `all_runnable` | 673.4 | 461.6 | 67.863 | 11.609 | 0 of 10 | 2743.9 | 53.385 | 0.583 / 0.417 |
| `reference_default` | 439.3 | 191.2 | 78.295 | 5.18 | 0 of 10 | 8827.5 | 88.646 | 0.694 / 0.306 |

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

## bottleneck

`configs/scenarios/corridor_to_bottleneck.yaml`. Two people from opposite ends of a single-file segment.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 0 | 0.715 | – |
| `passed_screening` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1 | 0.831 | – |
| `cane_rule_alone` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 0.2 | 0.703 | – |
| `all_runnable` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1 | 0.648 | – |
| `reference_default` | 1 | 0 | 6.667 | 2.035 | 0 of 10 | 1.5 | 0.746 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- `all_runnable`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/10, p = 1; throughput_agents_per_min 0/0/10, p = 1; mean_delay_s 0/0/10, p = 1; collided_pairs 0/0/10, p = 1; collision_episodes 0/0/10, p = 1.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): single_file_segment T3: 8.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 2, not started because one was in force 0.

## passage

`configs/scenarios/passage_meet_middle_v1.yaml`. A scenario no rule was extracted from, round 2's narrow passage (two people meet inside it).

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 0 | – | 10 of 10 | 0 | 2.175 | – |
| `passed_screening` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.801 | – |
| `cane_rule_alone` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.537 | – |
| `all_runnable` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.511 | – |
| `reference_default` | 1 | 0 | 0 | – | 10 of 10 | 0 | 1.831 | – |

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
