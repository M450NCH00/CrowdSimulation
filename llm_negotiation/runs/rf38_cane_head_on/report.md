# rf38_cane_head_on: the rule set against plain ORCA

Machine-written by `negsim.ruleset_eval` (issue #74, RF-18). Method: `docs/rule-set-evaluation.md`. paired seeds per scenario: head_on_cane 30, baseline `orca_perturbed_v1`, sign test at p < 0.05, verdict rule 2 (`docs/rule-set-evaluation.md`, section 3).

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
| head_on_cane (realistic) | helps | no change | no change |

| Rule | Arm | head_on_cane | Realistic | Of record (realistic) | Flag |
| --- | --- | --- | --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | `passed_screening` | helps | helps | **helps** | – |
| `ext_head_on_6455ca5589` | `cane_rule_alone` | no change | no change | **no change** | – |

A rule's verdict of record comes from its realistic scenarios; a stress scenario shows whether it works where it applies, and is never a verdict of record on its own (the user's decision of 2026-10-27, issue #112). `harms_where_common`: the rule harms in a stress scenario but not by its verdict of record, flagged for RF-14 (the user's decision of 2026-10-27).

## head_on_cane

`configs/scenarios/wide_corridor_head_on.yaml`. Two people head-on in a 1.75 m corridor, at 1.3 m/s; exactly one walks with a cane (agent seed % 2), drawn from the cane holders of a realistic crowd of 1,000, the other from its people without a cane.


People: `configs/populations/singapore_street_v1.yaml` (realistic, quotas, exactly one person with mobility_aid cane drawn from a crowd of 1000 at exact shares, the others from its people without). Per seed, mean: n 2, age_65_and_over 1.133, mobility_aid_cane 1, load_large_suitcase 0, distraction_phone 0.167, assertiveness_holds_ground 0.967.

| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 1 | 0 | 9.748 | 0.002 | 0 of 30 | 0 | 1.154 | – |
| `passed_screening` | 0 | 0 | 9.756 | -0.008 | 0 of 30 | 1 | 1.176 | – |
| `cane_rule_alone` | 1 | 0 | 8.717 | 0.737 | 0 of 30 | 1 | 1.14 | – |
| `all_runnable` | 1 | 0 | 8.717 | 0.737 | 0 of 30 | 1 | 0.959 | – |
| `reference_default` | 1 | 0 | 9.721 | -0.034 | 0 of 30 | 1 | 1.264 | – |

Means over the seeds. Tests (better / worse / tied seeds, p):

- `passed_screening`: **helps** (fewer severe conflicts, and neither throughput nor delay worse, nor collisions). severe_conflicts 30/0/0, p = 0; throughput_agents_per_min 3/0/27, p = 0.25; mean_delay_s 3/0/27, p = 0.25; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `cane_rule_alone`: **no change** (no significant difference in severe conflicts; worse throughput_agents_per_min and mean_delay_s). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/30/0, p = 0; mean_delay_s 0/30/0, p = 0; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.
- `all_runnable`: **no change** (no significant difference in severe conflicts; worse throughput_agents_per_min and mean_delay_s). severe_conflicts 0/0/30, p = 1; throughput_agents_per_min 0/30/0, p = 0; mean_delay_s 0/30/0, p = 0; collided_pairs 0/0/30, p = 1; collision_episodes 0/0/30, p = 1.

Copied into the run's own staging database: 5 rule file(s), byte for byte (`rule_db_staging/MANIFEST.json`).
