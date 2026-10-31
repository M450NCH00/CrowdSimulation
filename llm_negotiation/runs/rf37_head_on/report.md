# rf37_head_on: the rule set against plain ORCA

Machine-written by `negsim.ruleset_eval` (issue #74, RF-18). Method: `docs/rule-set-evaluation.md`. paired seeds per scenario: head_on 30, head_on_slow 30, head_on_normal 30, head_on_fast 30, baseline `orca_perturbed_v1`, sign test at p < 0.05, verdict rule 2 (`docs/rule-set-evaluation.md`, section 3).

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
| head_on (realistic) | helps | no change | helps |
| head_on_slow (realistic) | helps | no change | helps |
| head_on_normal (realistic) | helps | no change | helps |
| head_on_fast (realistic) | helps | no change | helps |

| Rule | Arm | head_on | head_on_slow | head_on_normal | head_on_fast | Realistic | Of record (realistic) | Flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | `passed_screening` | helps | helps | helps | helps | helps | **helps** | – |
| `ext_head_on_6455ca5589` | `cane_rule_alone` | no change | no change | no change | no change | no change | **no change** | – |

A rule's verdict of record comes from its realistic scenarios; a stress scenario shows whether it works where it applies, and is never a verdict of record on its own (the user's decision of 2026-10-27, issue #112). `harms_where_common`: the rule harms in a stress scenario but not by its verdict of record, flagged for RF-14 (the user's decision of 2026-10-27).

## head_on

`configs/scenarios/wide_corridor_head_on.yaml`. Two people head-on in a 1.75 m corridor, at 1.3 m/s, drawn from a realistic crowd.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, the first of a crowd of 100 at exact shares). Per seed, mean: n 2, age_65_and_over 0.367, mobility_aid_cane 0.133, load_large_suitcase 0.033, distraction_phone 0.167, assertiveness_holds_ground 1.033.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 9.748 | 0.002 | 0 of 30 | 0 | 1.096 | – |
| `passed_screening` | 0 | 0 | 9.756 | -0.008 | 0 of 30 | 1 | 1.17 | – |
| `cane_rule_alone` | 1 | 0 | 9.609 | 0.102 | 0 of 30 | 0.133 | 1.12 | – |
| `all_runnable` | 0.133 | 0 | 9.617 | 0.092 | 0 of 30 | 1 | 1.083 | – |
| `reference_default` | 1 | 0 | 9.702 | -0.023 | 0 of 30 | 1 | 1.185 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 30/0/0, p = 0; throughput_agents_per_min 3/0/27, p = 0.25; mean_delay_s 3/0/27, p = 0.25; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/4/26, p = 0.125; mean_delay_s 0/4/26, p = 0.125; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `all_runnable`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 26/0/4, p = 0; throughput_agents_per_min 3/4/23, p = 1; mean_delay_s 3/4/23, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): head_on T3: 26.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 2, not started because one was in force 0.

## head_on_slow

`configs/scenarios/wide_corridor_head_on.yaml`. As head_on, both at Huber2014's slow speed, 1.15 m/s.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, the first of a crowd of 100 at exact shares). Per seed, mean: n 2, age_65_and_over 0.367, mobility_aid_cane 0.133, load_large_suitcase 0.033, distraction_phone 0.167, assertiveness_holds_ground 1.033.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 8.617 | 0.014 | 0 of 30 | 0 | 1.018 | – |
| `passed_screening` | 0 | 0 | 8.633 | -0.013 | 0 of 30 | 1 | 1.088 | – |
| `cane_rule_alone` | 1 | 0 | 8.514 | 0.104 | 0 of 30 | 0.133 | 1.065 | – |
| `all_runnable` | 0.133 | 0 | 8.528 | 0.08 | 0 of 30 | 1 | 0.977 | – |
| `reference_default` | 1 | 0 | 8.583 | -0.021 | 0 of 30 | 1 | 1.141 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 30/0/0, p = 0; throughput_agents_per_min 8/0/22, p = 0.00781; mean_delay_s 8/0/22, p = 0.00781; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/4/26, p = 0.125; mean_delay_s 0/4/26, p = 0.125; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `all_runnable`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 26/0/4, p = 0; throughput_agents_per_min 7/4/19, p = 0.549; mean_delay_s 7/4/19, p = 0.549; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): head_on T3: 26.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 2, not started because one was in force 0.

## head_on_normal

`configs/scenarios/wide_corridor_head_on.yaml`. As head_on, both at Huber2014's normal speed, 1.42 m/s.

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, the first of a crowd of 100 at exact shares). Per seed, mean: n 2, age_65_and_over 0.367, mobility_aid_cane 0.133, load_large_suitcase 0.033, distraction_phone 0.167, assertiveness_holds_ground 1.033.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 10.62 | 0.032 | 0 of 30 | 0 | 1.149 | – |
| `passed_screening` | 0 | 0 | 10.62 | 0.032 | 0 of 30 | 1 | 1.155 | – |
| `cane_rule_alone` | 1 | 0 | 10.456 | 0.132 | 0 of 30 | 0.133 | 1.142 | – |
| `all_runnable` | 0.133 | 0 | 10.456 | 0.132 | 0 of 30 | 1 | 1.106 | – |
| `reference_default` | 1 | 0 | 10.602 | -0.008 | 0 of 30 | 1 | 1.181 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 30/0/0, p = 0; throughput_agents_per_min 0/0/30, p = 1; mean_delay_s 0/0/30, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/4/26, p = 0.125; mean_delay_s 0/4/26, p = 0.125; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `all_runnable`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 26/0/4, p = 0; throughput_agents_per_min 0/4/26, p = 0.125; mean_delay_s 0/4/26, p = 0.125; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): head_on T3: 26.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 2, not started because one was in force 0.

## head_on_fast

`configs/scenarios/wide_corridor_head_on.yaml`. As head_on, both at Huber2014's fast speed, 1.78 m/s (below the scenario's max_speed of 2.0).

People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, the first of a crowd of 100 at exact shares). Per seed, mean: n 2, age_65_and_over 0.367, mobility_aid_cane 0.133, load_large_suitcase 0.033, distraction_phone 0.167, assertiveness_holds_ground 1.033.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 13.333 | 0.011 | 0 of 30 | 0 | 1.4 | – |
| `passed_screening` | 0 | 0 | 13.333 | 0.011 | 0 of 30 | 1 | 1.418 | – |
| `cane_rule_alone` | 1 | 0 | 13.086 | 0.11 | 0 of 30 | 0.133 | 1.364 | – |
| `all_runnable` | 0.133 | 0 | 13.086 | 0.11 | 0 of 30 | 1 | 1.288 | – |
| `reference_default` | 1 | 0 | 13.25 | 0.011 | 0 of 30 | 1 | 1.42 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 30/0/0, p = 0; throughput_agents_per_min 0/0/30, p = 1; mean_delay_s 0/0/30, p = 1; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/4/26, p = 0.125; mean_delay_s 0/4/26, p = 0.125; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `all_runnable`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 26/0/4, p = 0; throughput_agents_per_min 0/4/26, p = 0.125; mean_delay_s 0/4/26, p = 0.125; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- Uncovered conflicts under `cane_rule_alone` (pairs, all seeds; most frequent first): head_on T3: 26.
  Rule conflicts: 0 pairs matched by several rules, 0 ambiguous matches, 0 cross-pair conflicts; plans started 2, not started because one was in force 0.

Copied into the run's own staging database: 5 rule file(s), byte for byte (`rule_db_staging/MANIFEST.json`).
