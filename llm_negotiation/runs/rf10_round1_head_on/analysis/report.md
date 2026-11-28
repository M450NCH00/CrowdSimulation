# Factor analysis of a resolution experiment (RF-8)

## Inputs

- `llm_negotiation/runs/rf10_round1_head_on/outcomes.csv`

- Sessions analysed (completed): **288** (independent: 96, non_verbal: 96, talk: 96); left out: none.
- Rows, one per agent per session: **576**.
- Physical outcomes of mode **`plan_only`** (the Step 1 measure).
- Client: deepseek.
- Predictors that vary: `own_age_high`, `own_female`, `other_age_high`, `other_female`, `own_urgency`, `own_mobility_aid`, `own_load`, `own_distraction`, `own_assertiveness`, `own_residence`, `own_memory_note`, `other_mobility_aid`, `other_load`, `other_distraction`, `same_ethnicity`, `surroundings_busy`, `time_of_day_late_night`, `finds_other_attractive`, `knows_other`, `is_lower_agent`; constant, left out: `own_demographics_hidden`, `other_demographics_unseen`, `ethnicity_unseen`, `pairwise_unseen`.
- Holm's correction at alpha = 0.05, over every term of every model in this report (the chance of any false positive in it is at most alpha); seed 63; codebooks `intent_v2` and `reasons_v1`.

**The other's factors are as the agent was told them.** A factor of the other person counts only if it was printed to the agent at one or more of its decision points (`analysis/load.py`).

## 1. Factor effects

Logistic regression per binary outcome (odds ratios, OR, with 95% intervals), linear regression for a continuous one (coefficients). Per-agent models cluster standard errors by session; per-session models use HC1. Holm's correction runs over every term of every model in this report (the chance of any false positive in it is at most alpha). `all` is every condition together, with condition as a factor. A model whose outcome is separated by the predictors has no finite estimate and is listed as `separation`, never read as an effect.

### Significant after Holm's correction

| Outcome | Subset | Term | Effect [95% CI] | p | Holm p | n |
| --- | --- | --- | --- | --- | --- | --- |
| plan_slowed | all | own_assertiveness | OR 0.26 [0.14, 0.48] | < 0.001 | 0.015 | 571 |
| plan_slowed | independent | own_assertiveness | OR 0.05 [0.02, 0.20] | < 0.001 | 0.005 | 187 |
| signalled | all | knows_other | OR 221.31 [23.14, 2116.44] | < 0.001 | 0.002 | 384 |
| signalled | all | finds_other_attractive | OR 5.29 [2.39, 11.72] | < 0.001 | 0.027 | 384 |
| decision_points | all | condition[non_verbal] | +3.667 [+3.508, +3.826] | < 0.001 | < 0.001 | 288 |
| decision_points | all | condition[talk] | +3.698 [+3.529, +3.867] | < 0.001 | < 0.001 | 288 |

### Every model

| outcome | level | subset | status | n | events | clusters | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| passed_first | agent | all | ok | 244 | 60 | 122 |  |
| kept_left | agent | all | ok | 576 | 220 | 288 |  |
| stopped | agent | all | separation | 576 | 3 | 288 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | all | one value | 576 | 0 | - | every row is 0 |
| plan_left | agent | all | ok | 571 | 127 | 288 |  |
| plan_right | agent | all | ok | 571 | 228 | 288 |  |
| plan_slowed | agent | all | ok | 571 | 389 | 288 |  |
| plan_stopped | agent | all | separation | 571 | 2 | 288 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | all | one value | 571 | 0 | - | every row is 0 |
| start_distance_m | agent | all | no data | 6 | - | - | 6 rows for 6 parameters |
| signalled | agent | all | ok | 384 | 248 | 192 |  |
| resolved_plan_only | session | all | ok | 288 | 94 | - |  |
| resolved_plan_orca | session | all | ok | 288 | 104 | - |  |
| resolved_by_llm | session | all | ok | 288 | 94 | - |  |
| decision_points | session | all | ok | 288 | - | - |  |
| passed_first | agent | independent | ok | 88 | 23 | 44 |  |
| kept_left | agent | independent | ok | 192 | 68 | 96 |  |
| stopped | agent | independent | one value | 192 | 0 | - | every row is 0 |
| backed_up | agent | independent | one value | 192 | 0 | - | every row is 0 |
| plan_left | agent | independent | ok | 187 | 33 | 96 |  |
| plan_right | agent | independent | ok | 187 | 68 | 96 |  |
| plan_slowed | agent | independent | ok | 187 | 127 | 96 |  |
| plan_stopped | agent | independent | one value | 187 | 0 | - | every row is 0 |
| plan_backed_up | agent | independent | one value | 187 | 0 | - | every row is 0 |
| start_distance_m | agent | independent | no data | 0 | - | - |  |
| signalled | agent | independent | no data | 0 | - | - |  |
| resolved_plan_only | session | independent | ok | 96 | 36 | - |  |
| resolved_plan_orca | session | independent | ok | 96 | 39 | - |  |
| resolved_by_llm | session | independent | ok | 96 | 36 | - |  |
| decision_points | session | independent | one value | 96 | - | - | every row is 2 |
| passed_first | agent | non_verbal | separation | 74 | 17 | 37 | the outcome is (nearly) separated by the predictors: no finite estimate |
| kept_left | agent | non_verbal | ok | 192 | 68 | 96 |  |
| stopped | agent | non_verbal | one value | 192 | 0 | - | every row is 0 |
| backed_up | agent | non_verbal | one value | 192 | 0 | - | every row is 0 |
| plan_left | agent | non_verbal | ok | 192 | 47 | 96 |  |
| plan_right | agent | non_verbal | ok | 192 | 84 | 96 |  |
| plan_slowed | agent | non_verbal | ok | 192 | 125 | 96 |  |
| plan_stopped | agent | non_verbal | separation | 192 | 1 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | non_verbal | one value | 192 | 0 | - | every row is 0 |
| start_distance_m | agent | non_verbal | no data | 4 | - | - | 4 rows for 4 parameters |
| signalled | agent | non_verbal | ok | 192 | 118 | 96 |  |
| resolved_plan_only | session | non_verbal | ok | 96 | 28 | - |  |
| resolved_plan_orca | session | non_verbal | ok | 96 | 29 | - |  |
| resolved_by_llm | session | non_verbal | ok | 96 | 28 | - |  |
| decision_points | session | non_verbal | ok | 96 | - | - |  |
| passed_first | agent | talk | ok | 82 | 20 | 41 |  |
| kept_left | agent | talk | ok | 192 | 84 | 96 |  |
| stopped | agent | talk | separation | 192 | 3 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | talk | one value | 192 | 0 | - | every row is 0 |
| plan_left | agent | talk | ok | 192 | 47 | 96 |  |
| plan_right | agent | talk | ok | 192 | 76 | 96 |  |
| plan_slowed | agent | talk | ok | 192 | 137 | 96 |  |
| plan_stopped | agent | talk | separation | 192 | 1 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | talk | one value | 192 | 0 | - | every row is 0 |
| start_distance_m | agent | talk | no data | 2 | - | - | 2 rows for 2 parameters |
| signalled | agent | talk | separation | 192 | 130 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| resolved_plan_only | session | talk | ok | 96 | 30 | - |  |
| resolved_plan_orca | session | talk | ok | 96 | 36 | - |  |
| resolved_by_llm | session | talk | ok | 96 | 30 | - |  |
| decision_points | session | talk | ok | 96 | - | - |  |

### Each outcome, all conditions together

Per outcome: what it is, and every term of the pooled model (the per-condition terms are in `effects_terms.csv`).

**`passed_first`** (agent): left the conflict zone first (physical; `together` counts as not first). Status: ok, n = 244, events = 60.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.52 [0.18, 1.52] | 0.235 | 1.000 |
| own_female | OR 0.71 [0.31, 1.65] | 0.426 | 1.000 |
| other_age_high | OR 0.70 [0.22, 2.26] | 0.554 | 1.000 |
| own_urgency | OR 1.36 [0.50, 3.69] | 0.543 | 1.000 |
| own_mobility_aid | OR 1.81 [0.65, 5.06] | 0.258 | 1.000 |
| own_load | OR 1.16 [0.41, 3.27] | 0.783 | 1.000 |
| own_distraction | OR 1.66 [0.49, 5.58] | 0.413 | 1.000 |
| own_assertiveness | OR 2.34 [0.69, 7.97] | 0.172 | 1.000 |
| own_residence | OR 2.78 [1.06, 7.26] | 0.037 | 1.000 |
| own_memory_note | OR 0.88 [0.30, 2.62] | 0.820 | 1.000 |
| other_mobility_aid | OR 2.02 [0.71, 5.73] | 0.186 | 1.000 |
| other_load | OR 1.12 [0.37, 3.40] | 0.848 | 1.000 |
| other_distraction | OR 0.67 [0.23, 1.98] | 0.468 | 1.000 |
| same_ethnicity | OR 0.81 [0.41, 1.58] | 0.528 | 1.000 |
| surroundings_busy | OR 1.09 [0.55, 2.16] | 0.806 | 1.000 |
| time_of_day_late_night | OR 1.11 [0.54, 2.29] | 0.776 | 1.000 |
| finds_other_attractive | OR 0.38 [0.16, 0.91] | 0.030 | 1.000 |
| knows_other | OR 1.12 [0.52, 2.40] | 0.777 | 1.000 |
| is_lower_agent | OR 1.14 [0.48, 2.70] | 0.763 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.74 [0.96, 3.18] | 0.070 | 1.000 |
| condition[non_verbal] | OR 0.65 [0.31, 1.37] | 0.259 | 1.000 |
| condition[talk] | OR 0.91 [0.44, 1.88] | 0.805 | 1.000 |

Left out of the model: other_female (collinear).

**`kept_left`** (agent): kept to its own left at the closest approach (physical; rows where the two were not abreast are left out). Status: ok, n = 576, events = 220.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.59 [0.32, 1.06] | 0.077 | 1.000 |
| own_female | OR 1.02 [0.95, 1.10] | 0.523 | 1.000 |
| other_age_high | OR 0.50 [0.29, 0.87] | 0.014 | 1.000 |
| own_urgency | OR 1.10 [0.63, 1.91] | 0.746 | 1.000 |
| own_mobility_aid | OR 1.26 [0.71, 2.25] | 0.428 | 1.000 |
| own_load | OR 1.03 [0.59, 1.81] | 0.911 | 1.000 |
| own_distraction | OR 2.44 [1.37, 4.35] | 0.002 | 1.000 |
| own_assertiveness | OR 0.84 [0.48, 1.47] | 0.550 | 1.000 |
| own_residence | OR 0.58 [0.33, 0.99] | 0.047 | 1.000 |
| own_memory_note | OR 0.53 [0.30, 0.95] | 0.034 | 1.000 |
| other_mobility_aid | OR 0.89 [0.52, 1.53] | 0.676 | 1.000 |
| other_load | OR 0.86 [0.50, 1.49] | 0.599 | 1.000 |
| other_distraction | OR 1.80 [1.05, 3.10] | 0.033 | 1.000 |
| same_ethnicity | OR 0.98 [0.58, 1.65] | 0.940 | 1.000 |
| surroundings_busy | OR 1.23 [0.71, 2.14] | 0.469 | 1.000 |
| time_of_day_late_night | OR 0.87 [0.50, 1.52] | 0.631 | 1.000 |
| finds_other_attractive | OR 0.98 [0.67, 1.44] | 0.937 | 1.000 |
| knows_other | OR 0.54 [0.31, 0.95] | 0.031 | 1.000 |
| is_lower_agent | OR 1.01 [0.93, 1.09] | 0.833 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.61 [0.96, 2.69] | 0.070 | 1.000 |
| condition[non_verbal] | OR 1.00 [0.53, 1.89] | 1.000 | 1.000 |
| condition[talk] | OR 1.47 [0.80, 2.68] | 0.210 | 1.000 |

Left out of the model: other_female (collinear).

**`stopped`** (agent): its speed fell below the deadlock monitor's threshold (physical). Status: separation, n = 576, events = 3.

Left out of the model: other_female (collinear).

**`backed_up`** (agent): moved against its path (physical). Status: one value, n = 576, events = 0.

**`plan_left`** (agent): its first plan turns to its left only. Status: ok, n = 571, events = 127.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.67 [0.80, 3.50] | 0.173 | 1.000 |
| own_female | OR 1.49 [0.97, 2.30] | 0.069 | 1.000 |
| other_age_high | OR 0.68 [0.39, 1.19] | 0.179 | 1.000 |
| own_urgency | OR 1.35 [0.58, 3.11] | 0.484 | 1.000 |
| own_mobility_aid | OR 1.13 [0.50, 2.55] | 0.778 | 1.000 |
| own_load | OR 1.07 [0.51, 2.25] | 0.858 | 1.000 |
| own_distraction | OR 1.08 [0.49, 2.37] | 0.844 | 1.000 |
| own_assertiveness | OR 0.33 [0.14, 0.78] | 0.011 | 1.000 |
| own_residence | OR 0.25 [0.11, 0.58] | 0.001 | 0.883 |
| own_memory_note | OR 0.63 [0.29, 1.35] | 0.235 | 1.000 |
| other_mobility_aid | OR 1.18 [0.69, 2.02] | 0.547 | 1.000 |
| other_load | OR 1.10 [0.63, 1.91] | 0.738 | 1.000 |
| other_distraction | OR 1.36 [0.78, 2.37] | 0.278 | 1.000 |
| same_ethnicity | OR 0.98 [0.62, 1.53] | 0.918 | 1.000 |
| surroundings_busy | OR 0.80 [0.49, 1.29] | 0.357 | 1.000 |
| time_of_day_late_night | OR 1.02 [0.64, 1.64] | 0.921 | 1.000 |
| finds_other_attractive | OR 0.70 [0.46, 1.07] | 0.099 | 1.000 |
| knows_other | OR 1.11 [0.68, 1.81] | 0.664 | 1.000 |
| is_lower_agent | OR 1.12 [0.73, 1.74] | 0.598 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.97 [0.63, 1.50] | 0.900 | 1.000 |
| condition[non_verbal] | OR 1.57 [0.91, 2.73] | 0.108 | 1.000 |
| condition[talk] | OR 1.57 [0.92, 2.69] | 0.100 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_right`** (agent): its first plan turns to its right only. Status: ok, n = 571, events = 228.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.98 [0.57, 1.71] | 0.956 | 1.000 |
| own_female | OR 0.68 [0.47, 0.98] | 0.037 | 1.000 |
| other_age_high | OR 1.53 [0.92, 2.57] | 0.104 | 1.000 |
| own_urgency | OR 0.80 [0.46, 1.38] | 0.420 | 1.000 |
| own_mobility_aid | OR 1.22 [0.71, 2.12] | 0.469 | 1.000 |
| own_load | OR 1.06 [0.62, 1.81] | 0.834 | 1.000 |
| own_distraction | OR 1.17 [0.68, 2.03] | 0.574 | 1.000 |
| own_assertiveness | OR 1.84 [1.06, 3.20] | 0.031 | 1.000 |
| own_residence | OR 2.37 [1.42, 3.95] | < 0.001 | 0.625 |
| own_memory_note | OR 1.15 [0.67, 1.98] | 0.607 | 1.000 |
| other_mobility_aid | OR 1.23 [0.72, 2.12] | 0.444 | 1.000 |
| other_load | OR 1.02 [0.61, 1.73] | 0.935 | 1.000 |
| other_distraction | OR 1.23 [0.72, 2.10] | 0.458 | 1.000 |
| same_ethnicity | OR 1.59 [1.08, 2.35] | 0.018 | 1.000 |
| surroundings_busy | OR 0.95 [0.64, 1.42] | 0.815 | 1.000 |
| time_of_day_late_night | OR 0.88 [0.59, 1.30] | 0.521 | 1.000 |
| finds_other_attractive | OR 1.38 [0.95, 2.00] | 0.093 | 1.000 |
| knows_other | OR 1.88 [1.26, 2.79] | 0.002 | 1.000 |
| is_lower_agent | OR 1.02 [0.70, 1.48] | 0.914 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.03 [0.71, 1.50] | 0.858 | 1.000 |
| condition[non_verbal] | OR 1.40 [0.89, 2.21] | 0.144 | 1.000 |
| condition[talk] | OR 1.16 [0.75, 1.79] | 0.516 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_slowed`** (agent): its first plan slows below its speed at the decision. Status: ok, n = 571, events = 389.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.68 [0.89, 3.17] | 0.111 | 1.000 |
| own_female | OR 0.89 [0.57, 1.39] | 0.616 | 1.000 |
| other_age_high | OR 3.44 [1.57, 7.57] | 0.002 | 1.000 |
| own_urgency | OR 0.71 [0.38, 1.33] | 0.279 | 1.000 |
| own_mobility_aid | OR 2.28 [1.22, 4.25] | 0.010 | 1.000 |
| own_load | OR 2.02 [1.10, 3.70] | 0.023 | 1.000 |
| own_distraction | OR 0.77 [0.41, 1.44] | 0.412 | 1.000 |
| own_assertiveness | OR 0.26 [0.14, 0.48] | < 0.001 | 0.015 |
| own_residence | OR 0.81 [0.43, 1.51] | 0.506 | 1.000 |
| own_memory_note | OR 0.97 [0.52, 1.83] | 0.930 | 1.000 |
| other_mobility_aid | OR 2.33 [1.10, 4.91] | 0.027 | 1.000 |
| other_load | OR 1.92 [0.95, 3.90] | 0.070 | 1.000 |
| other_distraction | OR 1.19 [0.60, 2.36] | 0.608 | 1.000 |
| same_ethnicity | OR 1.38 [0.90, 2.14] | 0.144 | 1.000 |
| surroundings_busy | OR 1.22 [0.76, 1.96] | 0.417 | 1.000 |
| time_of_day_late_night | OR 1.61 [1.01, 2.56] | 0.045 | 1.000 |
| finds_other_attractive | OR 1.97 [1.26, 3.06] | 0.003 | 1.000 |
| knows_other | OR 2.36 [1.41, 3.96] | 0.001 | 0.752 |
| is_lower_agent | OR 0.84 [0.54, 1.33] | 0.463 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.98 [0.64, 1.50] | 0.934 | 1.000 |
| condition[non_verbal] | OR 0.83 [0.50, 1.39] | 0.480 | 1.000 |
| condition[talk] | OR 1.22 [0.72, 2.06] | 0.464 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_stopped`** (agent): its first plan stops. Status: separation, n = 571, events = 2.

Left out of the model: other_female (collinear).

**`plan_backed_up`** (agent): its first plan backs up. Status: one value, n = 571, events = 0.

**`start_distance_m`** (agent): its first plan starts at this distance (plans that start so). Status: no data, n = 6.

Left out of the model: other_female (collinear); own_urgency (constant); own_mobility_aid (constant); own_load (constant); own_distraction (constant); own_assertiveness (constant); own_residence (constant); own_memory_note (collinear); other_mobility_aid (constant); other_distraction (collinear); same_ethnicity (collinear); surroundings_busy (collinear); time_of_day_late_night (collinear); knows_other (constant); is_lower_agent (collinear); geometry[layout=apart_20cm] (collinear); condition[talk] (collinear).

**`signalled`** (agent): it signalled at least once (non-verbal and talk only). Status: ok, n = 384, events = 248.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.23 [0.38, 3.95] | 0.733 | 1.000 |
| own_female | OR 0.91 [0.55, 1.52] | 0.724 | 1.000 |
| other_age_high | OR 1.40 [0.50, 3.88] | 0.522 | 1.000 |
| own_urgency | OR 1.32 [0.41, 4.25] | 0.643 | 1.000 |
| own_mobility_aid | OR 5.59 [1.56, 20.05] | 0.008 | 1.000 |
| own_load | OR 0.45 [0.13, 1.61] | 0.219 | 1.000 |
| own_distraction | OR 0.59 [0.16, 2.16] | 0.425 | 1.000 |
| own_assertiveness | OR 11.80 [2.74, 50.87] | < 0.001 | 0.640 |
| own_residence | OR 0.92 [0.23, 3.72] | 0.909 | 1.000 |
| own_memory_note | OR 1.59 [0.41, 6.22] | 0.502 | 1.000 |
| other_mobility_aid | OR 4.58 [1.68, 12.45] | 0.003 | 1.000 |
| other_load | OR 1.14 [0.36, 3.67] | 0.822 | 1.000 |
| other_distraction | OR 1.07 [0.36, 3.18] | 0.909 | 1.000 |
| same_ethnicity | OR 1.07 [0.41, 2.79] | 0.891 | 1.000 |
| surroundings_busy | OR 0.39 [0.12, 1.28] | 0.121 | 1.000 |
| time_of_day_late_night | OR 1.53 [0.54, 4.35] | 0.423 | 1.000 |
| finds_other_attractive | OR 5.29 [2.39, 11.72] | < 0.001 | 0.027 |
| knows_other | OR 221.31 [23.14, 2116.44] | < 0.001 | 0.002 |
| is_lower_agent | OR 0.66 [0.40, 1.10] | 0.111 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.42 [0.61, 3.28] | 0.415 | 1.000 |
| condition[talk] | OR 1.93 [0.83, 4.51] | 0.127 | 1.000 |

Left out of the model: other_female (collinear).

**`resolved_plan_only`** (session): resolved in `plan_only` (the Step 1 measure). Status: ok, n = 288, events = 94.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.98 [0.56, 1.74] | 0.954 | 1.000 |
| gender_pair[p1_male] | OR 1.17 [0.66, 2.06] | 0.589 | 1.000 |
| urgency[p1] | OR 1.63 [0.93, 2.88] | 0.090 | 1.000 |
| mobility_aid[p1] | OR 0.84 [0.47, 1.49] | 0.546 | 1.000 |
| load[p1] | OR 0.58 [0.33, 1.02] | 0.060 | 1.000 |
| distraction[p1] | OR 1.60 [0.90, 2.82] | 0.106 | 1.000 |
| assertiveness[p1] | OR 0.47 [0.26, 0.84] | 0.011 | 1.000 |
| residence[p1] | OR 1.29 [0.73, 2.28] | 0.378 | 1.000 |
| memory_note[p1] | OR 0.93 [0.52, 1.66] | 0.807 | 1.000 |
| ethnicity_pair[different] | OR 1.09 [0.65, 1.83] | 0.756 | 1.000 |
| surroundings[busy] | OR 0.97 [0.55, 1.70] | 0.908 | 1.000 |
| time_of_day[late_night] | OR 0.96 [0.54, 1.70] | 0.891 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 1.11 [0.64, 1.92] | 0.711 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 1.04 [0.59, 1.82] | 0.900 | 1.000 |
| familiarity[strangers] | OR 0.76 [0.43, 1.34] | 0.341 | 1.000 |
| mapping[p1_higher] | OR 1.08 [0.61, 1.92] | 0.791 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.25 [0.73, 2.12] | 0.414 | 1.000 |
| condition[non_verbal] | OR 0.67 [0.36, 1.26] | 0.213 | 1.000 |
| condition[talk] | OR 0.74 [0.40, 1.37] | 0.341 | 1.000 |

**`resolved_plan_orca`** (session): resolved in `plan_orca`. Status: ok, n = 288, events = 104.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 1.03 [0.60, 1.80] | 0.906 | 1.000 |
| gender_pair[p1_male] | OR 1.33 [0.77, 2.31] | 0.310 | 1.000 |
| urgency[p1] | OR 1.52 [0.88, 2.64] | 0.134 | 1.000 |
| mobility_aid[p1] | OR 0.70 [0.40, 1.23] | 0.219 | 1.000 |
| load[p1] | OR 0.62 [0.36, 1.08] | 0.090 | 1.000 |
| distraction[p1] | OR 1.33 [0.77, 2.31] | 0.306 | 1.000 |
| assertiveness[p1] | OR 0.55 [0.31, 0.95] | 0.034 | 1.000 |
| residence[p1] | OR 1.28 [0.74, 2.23] | 0.378 | 1.000 |
| memory_note[p1] | OR 1.03 [0.59, 1.80] | 0.917 | 1.000 |
| ethnicity_pair[different] | OR 0.87 [0.52, 1.45] | 0.593 | 1.000 |
| surroundings[busy] | OR 1.21 [0.70, 2.11] | 0.492 | 1.000 |
| time_of_day[late_night] | OR 1.18 [0.68, 2.05] | 0.563 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 0.90 [0.53, 1.53] | 0.698 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 1.17 [0.67, 2.03] | 0.577 | 1.000 |
| familiarity[strangers] | OR 1.21 [0.70, 2.11] | 0.490 | 1.000 |
| mapping[p1_higher] | OR 0.85 [0.49, 1.49] | 0.575 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.93 [0.55, 1.55] | 0.770 | 1.000 |
| condition[non_verbal] | OR 0.61 [0.33, 1.15] | 0.127 | 1.000 |
| condition[talk] | OR 0.87 [0.48, 1.57] | 0.643 | 1.000 |

**`resolved_by_llm`** (session): resolved in `plan_only` before ORCA took over. Status: ok, n = 288, events = 94.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.98 [0.56, 1.74] | 0.954 | 1.000 |
| gender_pair[p1_male] | OR 1.17 [0.66, 2.06] | 0.589 | 1.000 |
| urgency[p1] | OR 1.63 [0.93, 2.88] | 0.090 | 1.000 |
| mobility_aid[p1] | OR 0.84 [0.47, 1.49] | 0.546 | 1.000 |
| load[p1] | OR 0.58 [0.33, 1.02] | 0.060 | 1.000 |
| distraction[p1] | OR 1.60 [0.90, 2.82] | 0.106 | 1.000 |
| assertiveness[p1] | OR 0.47 [0.26, 0.84] | 0.011 | 1.000 |
| residence[p1] | OR 1.29 [0.73, 2.28] | 0.378 | 1.000 |
| memory_note[p1] | OR 0.93 [0.52, 1.66] | 0.807 | 1.000 |
| ethnicity_pair[different] | OR 1.09 [0.65, 1.83] | 0.756 | 1.000 |
| surroundings[busy] | OR 0.97 [0.55, 1.70] | 0.908 | 1.000 |
| time_of_day[late_night] | OR 0.96 [0.54, 1.70] | 0.891 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 1.11 [0.64, 1.92] | 0.711 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 1.04 [0.59, 1.82] | 0.900 | 1.000 |
| familiarity[strangers] | OR 0.76 [0.43, 1.34] | 0.341 | 1.000 |
| mapping[p1_higher] | OR 1.08 [0.61, 1.92] | 0.791 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.25 [0.73, 2.12] | 0.414 | 1.000 |
| condition[non_verbal] | OR 0.67 [0.36, 1.26] | 0.213 | 1.000 |
| condition[talk] | OR 0.74 [0.40, 1.37] | 0.341 | 1.000 |

**`decision_points`** (session): decision points of both people. Status: ok, n = 288.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | -0.044 [-0.204, +0.117] | 0.593 | 1.000 |
| gender_pair[p1_male] | -0.096 [-0.260, +0.068] | 0.250 | 1.000 |
| urgency[p1] | -0.023 [-0.185, +0.139] | 0.783 | 1.000 |
| mobility_aid[p1] | +0.091 [-0.071, +0.253] | 0.271 | 1.000 |
| load[p1] | +0.116 [-0.042, +0.273] | 0.151 | 1.000 |
| distraction[p1] | +0.008 [-0.157, +0.172] | 0.924 | 1.000 |
| assertiveness[p1] | -0.107 [-0.270, +0.057] | 0.200 | 1.000 |
| residence[p1] | -0.046 [-0.207, +0.115] | 0.574 | 1.000 |
| memory_note[p1] | +0.070 [-0.095, +0.235] | 0.405 | 1.000 |
| ethnicity_pair[different] | -0.056 [-0.222, +0.109] | 0.506 | 1.000 |
| surroundings[busy] | -0.151 [-0.313, +0.012] | 0.069 | 1.000 |
| time_of_day[late_night] | +0.039 [-0.124, +0.203] | 0.639 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | -0.077 [-0.232, +0.079] | 0.333 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | -0.011 [-0.172, +0.151] | 0.894 | 1.000 |
| familiarity[strangers] | -0.245 [-0.404, -0.086] | 0.003 | 1.000 |
| mapping[p1_higher] | -0.093 [-0.259, +0.073] | 0.271 | 1.000 |
| geometry[layout=apart_20cm] | +0.004 [-0.154, +0.161] | 0.964 | 1.000 |
| condition[non_verbal] | +3.667 [+3.508, +3.826] | < 0.001 | < 0.001 |
| condition[talk] | +3.698 [+3.529, +3.867] | < 0.001 | < 0.001 |

## 2. Decision tree

Predicts **`passed_first`** per agent, depth at most 3, on 244 rows (the predictors that vary, with condition and geometry). Figure: `tree.png`.

- Accuracy on the rows it was grown on: 0.783; always guessing the commoner outcome: 0.754.
- Accuracy on held-out sessions (5-fold, grouped by session): 0.733.
- Splits on: `finds_other_attractive`, `own_assertiveness`, `own_memory_note`, `own_mobility_aid`, `own_residence`, `own_urgency`, `surroundings_busy`.

A tree no better on held-out sessions than the commoner outcome has found no usable pattern.

```
|--- own_mobility_aid <= 0.50
|   |--- own_residence <= 0.50
|   |   |--- finds_other_attractive <= 0.50
|   |   |   |--- weights: [77.00, 18.00] class: 0
|   |   |--- finds_other_attractive >  0.50
|   |   |   |--- weights: [55.00, 6.00] class: 0
|   |--- own_residence >  0.50
|   |   |--- own_memory_note <= 0.50
|   |   |   |--- weights: [19.00, 7.00] class: 0
|   |   |--- own_memory_note >  0.50
|   |   |   |--- weights: [5.00, 7.00] class: 1
|--- own_mobility_aid >  0.50
|   |--- own_assertiveness <= 0.50
|   |   |--- surroundings_busy <= 0.50
|   |   |   |--- weights: [8.00, 7.00] class: 0
|   |   |--- surroundings_busy >  0.50
|   |   |   |--- weights: [11.00, 3.00] class: 0
|   |--- own_assertiveness >  0.50
|   |   |--- own_urgency <= 0.50
|   |   |   |--- weights: [6.00, 4.00] class: 0
|   |   |--- own_urgency >  0.50
|   |   |   |--- weights: [3.00, 8.00] class: 1
```

## 3. Counterfactual pairs against the noise floor

The noise floor is the flip rate between repeats of one cell of the exact-repeat set (identical prompts), with a bootstrap 95% interval over cells. A pair's flip rate (Wilson 95% interval) counts as evidence only where its lower end is above the noise floor's upper end, in the same condition. Components: `who_passed_first`, `passing_side`, `stopped`, `backed_up`, `behaviour` (`behaviour` is all of them together).

### The noise floor

| component | subset | cells | pairs | flips | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| who_passed_first | all | 24 | 72 | 50 | 0.694 | 0.569 | 0.806 |
| who_passed_first | independent | 8 | 24 | 17 | 0.708 | 0.458 | 0.875 |
| who_passed_first | non_verbal | 8 | 24 | 15 | 0.625 | 0.417 | 0.750 |
| who_passed_first | talk | 8 | 24 | 18 | 0.750 | 0.500 | 0.958 |
| passing_side | all | 24 | 72 | 30 | 0.417 | 0.278 | 0.528 |
| passing_side | independent | 8 | 24 | 8 | 0.333 | 0.083 | 0.583 |
| passing_side | non_verbal | 8 | 24 | 12 | 0.500 | 0.250 | 0.667 |
| passing_side | talk | 8 | 24 | 10 | 0.417 | 0.167 | 0.667 |
| stopped | all | 24 | 72 | 4 | 0.056 | 0 | 0.139 |
| stopped | independent | 8 | 24 | 0 | 0 | 0 | 0 |
| stopped | non_verbal | 8 | 24 | 0 | 0 | 0 | 0 |
| stopped | talk | 8 | 24 | 4 | 0.167 | 0 | 0.333 |
| backed_up | all | 24 | 72 | 0 | 0 | 0 | 0 |
| backed_up | independent | 8 | 24 | 0 | 0 | 0 | 0 |
| backed_up | non_verbal | 8 | 24 | 0 | 0 | 0 | 0 |
| backed_up | talk | 8 | 24 | 0 | 0 | 0 | 0 |
| behaviour | all | 24 | 72 | 62 | 0.861 | 0.792 | 0.931 |
| behaviour | independent | 8 | 24 | 20 | 0.833 | 0.750 | 0.958 |
| behaviour | non_verbal | 8 | 24 | 21 | 0.875 | 0.750 | 1 |
| behaviour | talk | 8 | 24 | 21 | 0.875 | 0.750 | 1 |

### The counterfactual pairs

| factor | component | subset | pairs | flips | rate | ci_low | ci_high | noise_rate | noise_high | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attractiveness_0_sees_1 | who_passed_first | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.694 | 0.806 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | independent | 2 | 0 | 0 | 0 | 0.658 | 0.708 | 0.875 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.625 | 0.750 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.750 | 0.958 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | all | 6 | 1 | 0.167 | 0.030 | 0.564 | 0.694 | 0.806 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.708 | 0.875 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.625 | 0.750 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | talk | 2 | 0 | 0 | 0 | 0.658 | 0.750 | 0.958 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.694 | 0.806 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.708 | 0.875 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.625 | 0.750 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | talk | 2 | 2 | 1 | 0.342 | 1 | 0.750 | 0.958 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | all | 6 | 5 | 0.833 | 0.436 | 0.970 | 0.694 | 0.806 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | independent | 2 | 2 | 1 | 0.342 | 1 | 0.708 | 0.875 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.625 | 0.750 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.750 | 0.958 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.417 | 0.528 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | independent | 2 | 0 | 0 | 0 | 0.658 | 0.333 | 0.583 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.500 | 0.667 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | talk | 2 | 2 | 1 | 0.342 | 1 | 0.417 | 0.667 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.417 | 0.528 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.333 | 0.583 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.500 | 0.667 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.417 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.417 | 0.528 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.333 | 0.583 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.500 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | talk | 2 | 0 | 0 | 0 | 0.658 | 0.417 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.417 | 0.528 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | independent | 2 | 2 | 1 | 0.342 | 1 | 0.333 | 0.583 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.500 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.417 | 0.667 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.056 | 0.139 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.167 | 0.333 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.056 | 0.139 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.167 | 0.333 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.056 | 0.139 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.167 | 0.333 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.056 | 0.139 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.167 | 0.333 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | backed_up | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | backed_up | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | backed_up | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | backed_up | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | backed_up | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | backed_up | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | backed_up | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | backed_up | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | backed_up | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | backed_up | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | backed_up | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | backed_up | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | backed_up | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | backed_up | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | backed_up | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | backed_up | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.861 | 0.931 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | independent | 2 | 0 | 0 | 0 | 0.658 | 0.833 | 0.958 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.875 | 1 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | talk | 2 | 2 | 1 | 0.342 | 1 | 0.875 | 1 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.861 | 0.931 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | independent | 2 | 2 | 1 | 0.342 | 1 | 0.833 | 0.958 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.875 | 1 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.875 | 1 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.861 | 0.931 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.833 | 0.958 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.875 | 1 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | talk | 2 | 2 | 1 | 0.342 | 1 | 0.875 | 1 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | all | 6 | 6 | 1 | 0.610 | 1 | 0.861 | 0.931 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | independent | 2 | 2 | 1 | 0.342 | 1 | 0.833 | 0.958 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.875 | 1 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | talk | 2 | 2 | 1 | 0.342 | 1 | 0.875 | 1 | not distinguishable from the noise floor |

## 4. Behaviour stability

Per cell of the exact-repeat set: the share of its repeats with the commonest outcome (1: every repeat the same). A cell whose commonest behaviour came up in fewer than 0.75 of its repeats is a coin flip, and RF-11 should claim no rule there.

| Component | Cells | Mean | Lowest | Cells with every repeat the same |
| --- | --- | --- | --- | --- |
| who_passed_first | 24 | 0.597 | 0.333 | 3 |
| passing_side | 24 | 0.792 | 0.667 | 9 |
| stopped | 24 | 0.972 | 0.667 | 22 |
| backed_up | 24 | 1 | 1 | 24 |
| behaviour | 24 | 0.472 | 0.333 | 0 |

### Coin-flip cells: 24 of 24

| Cell | Condition | Repeats | Stability | Who passed first | Commonest behaviour |
| --- | --- | --- | --- | --- | --- |
| I_head_on_02dfbadb_02604456 | independent | 3 | 0.333 | 0.333 | p2\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_1caa9a84 | independent | 3 | 0.333 | 0.333 | together\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_55c9ae40 | independent | 3 | 0.667 | 0.667 | p1\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_8ea28db3 | independent | 3 | 0.333 | 0.667 | p1\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_3dee0df5 | independent | 3 | 0.667 | 0.667 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_800a3b04 | independent | 3 | 0.667 | 0.667 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_9b752a36 | independent | 3 | 0.667 | 1 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_c36d5d49 | independent | 3 | 0.333 | 0.333 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_02604456 | non_verbal | 3 | 0.667 | 0.667 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_1caa9a84 | non_verbal | 3 | 0.333 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_55c9ae40 | non_verbal | 3 | 0.333 | 0.667 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_8ea28db3 | non_verbal | 3 | 0.333 | 0.333 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_3dee0df5 | non_verbal | 3 | 0.667 | 0.667 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_800a3b04 | non_verbal | 3 | 0.333 | 0.667 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_9b752a36 | non_verbal | 3 | 0.667 | 1 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_c36d5d49 | non_verbal | 3 | 0.333 | 0.667 | p2\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_02604456 | talk | 3 | 0.333 | 0.333 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_1caa9a84 | talk | 3 | 0.667 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_55c9ae40 | talk | 3 | 0.667 | 1 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_8ea28db3 | talk | 3 | 0.333 | 0.333 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_3dee0df5 | talk | 3 | 0.333 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_800a3b04 | talk | 3 | 0.333 | 0.333 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_9b752a36 | talk | 3 | 0.667 | 0.667 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_c36d5d49 | talk | 3 | 0.333 | 0.333 | -\|left\|left\|0\|0\|0\|0 |

## 5. The factor-to-decision mapping

Every observed combination of `own_age_high`, `own_female`, `other_age_high`, `other_female`, `own_urgency`, `own_mobility_aid`, `own_load`, `own_distraction`, `own_assertiveness`, `own_residence`, `own_memory_note`, `other_mobility_aid`, `other_load`, `other_distraction`, `same_ethnicity`, `surroundings_busy`, `time_of_day_late_night`, `finds_other_attractive`, `knows_other`, `is_lower_agent`, `geometry`, per condition, from the agent's point of view: **402 combinations** in `mapping.csv`, each with its rows and, per outcome, how many are known and the share that are 1. Read the counts with the shares: a combination seen once gives 0 or 1 from one row. The 25 combinations with the most rows:

| condition | own_age_high | own_female | other_age_high | other_female | own_urgency | own_mobility_aid | own_load | own_distraction | own_assertiveness | own_residence | own_memory_note | other_mobility_aid | other_load | other_distraction | same_ethnicity | surroundings_busy | time_of_day_late_night | finds_other_attractive | knows_other | is_lower_agent | geometry | rows | p_passed_first | p_kept_left | p_stopped | p_backed_up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 5 | 0 | 0.400 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 5 | 0 | 0.400 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 5 | 0 | 0.200 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 5 | 0.500 | 0.800 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 5 | 0.500 | 0.400 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 5 | 0 | 0.600 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0.750 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.250 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.750 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0.333 | 0.500 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0.500 | 0.500 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0.500 | 0.750 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0 | 0 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0.500 | 0.750 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0.250 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0.333 | 0.500 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | - | 0.750 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 1 | 1 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | - | 0.750 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 1 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | layout=apart_20cm | 3 | 0 | 0.333 | 0.333 | 0 |

## 6. Stated against measured

How often each factor is named in the agents' private `reason` (keyword codebook `reasons_v1`), beside its strongest measured effect in the per-agent models of all conditions together. Named often: in at least 0.1 of the reasons. Measured: a term significant after Holm's correction. A factor named often with no measured effect, or the reverse, is a finding.

| Factor | Share of reasons naming it | Measured effect | Outcome | Term | Estimate (OR or coef.) | Holm p | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| age | 0.198 | no | passed_first | own_age_high | 0.524 | 1.000 | named often, no measured effect |
| gender | 0.050 | no | passed_first | own_female | 0.710 | 1.000 | neither |
| urgency | 0.125 | no | passed_first | own_urgency | 1.362 | 1.000 | named often, no measured effect |
| mobility_aid | 0.256 | no | passed_first | own_mobility_aid | 1.809 | 1.000 | named often, no measured effect |
| load | 0.313 | no | passed_first | own_load | 1.157 | 1.000 | named often, no measured effect |
| distraction | 0.226 | no | passed_first | own_distraction | 1.660 | 1.000 | named often, no measured effect |
| assertiveness | 0.249 | yes | plan_slowed | own_assertiveness | 0.256 | 0.015 | named often, and a measured effect |
| residence | 0.001 | no | plan_right | own_residence | 2.370 | 0.625 | neither |
| memory_note | 0.136 | no | passed_first | own_memory_note | 0.881 | 1.000 | named often, no measured effect |
| surroundings | 0.081 | no | passed_first | surroundings_busy | 1.090 | 1.000 | neither |
| time_of_day | 0.014 | no | passed_first | time_of_day_late_night | 1.111 | 1.000 | neither |
| perceived_attractiveness | 0.032 | yes | signalled | finds_other_attractive | 5.293 | 0.027 | a measured effect, rarely named |
| familiarity | 0.064 | yes | signalled | knows_other | 221.307 | 0.002 | a measured effect, rarely named |
| ethnicity_pair | - | no | passed_first | same_ethnicity | 0.806 | 1.000 | neither |
| is_lower_agent | - | no | passed_first | is_lower_agent | 1.142 | 1.000 | neither |

**Where saying and doing disagree:** `age` (named often, no measured effect), `urgency` (named often, no measured effect), `mobility_aid` (named often, no measured effect), `load` (named often, no measured effect), `distraction` (named often, no measured effect), `memory_note` (named often, no measured effect), `perceived_attractiveness` (a measured effect, rarely named), `familiarity` (a measured effect, rarely named).

### The debriefs' kind of basis

One per prompted agent (D8); every source is unchecked until RF-14.

| kind | independent | non_verbal | talk | all |
| --- | --- | --- | --- | --- |
| local_custom | 24 | 14 | 19 | 57 |
| habit | 64 | 70 | 62 | 196 |
| common_sense | 96 | 103 | 108 | 307 |
| none | 3 | 5 | 3 | 11 |
| (none given) | 5 | 0 | 0 | 5 |
| all | 192 | 192 | 192 | 576 |

## 7. Intent against plan

Each readable intent coded by the keyword codebook `intent_v2` (keep to a side, slow down, stop and wait, back up, carry on, or `other`), against the plan coded from its steps. A mismatch is an intent that says something the plan does not do. Intents coded `other` and unreadable replies are left out of the rate. A high rate means the structured plan cannot be trusted on its own (RF-11).

| subset | decision_points | unreadable | uncoded | compared | mismatches | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 1283 | 30 | 167 | 1086 | 266 | 0.245 | 0.220 | 0.271 |
| independent | 192 | 5 | 24 | 163 | 55 | 0.337 | 0.269 | 0.413 |
| non_verbal | 544 | 17 | 81 | 446 | 91 | 0.204 | 0.169 | 0.244 |
| talk | 547 | 8 | 62 | 477 | 120 | 0.252 | 0.215 | 0.292 |

### Examples of mismatches

| condition | session_id | agent_id | intent | plan_categories | plan_side | why |
| --- | --- | --- | --- | --- | --- | --- |
| non_verbal | N_head_on_02dfbadb_1caa9a84_r3 | 1 | Keep well to my right, slow down, and let Person 1 pass on my left without any collision | slow_down | none | intent says keep_to_side, the plan does not |
| talk | T_head_on_02dfbadb_8ea28db3_r1 | 0 | Acknowledge her wave, keep to my right side of the passage, and pass her with a friendly nod. | carry_on | none | intent says keep_to_side, the plan does not |
| talk | T_head_on_de176842_6ab9c72e_r1 | 1 | Keep to my right so he can pass with his suitcase, and greet him warmly as we pass | slow_down | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| independent | I_head_on_de176842_9b752a36_r2 | 1 | Keep walking steadily to the emergency room, holding my line with my suitcase so the young man makes room. | slow_down | none | intent says carry_on, the plan does not |
| talk | T_head_on_02dfbadb_1868bff4_r1 | 1 | Keep walking toward the emergency room without yielding, staying on my line with my suitcase. | keep_to_side;slow_down | right | intent says carry_on, the plan does not |
| talk | T_head_on_02dfbadb_1868bff4_r1 | 1 | Hold my line toward the emergency room but avoid a collision with her | keep_to_side | both | intent says carry_on, the plan does not |
| non_verbal | N_head_on_de176842_5841fc4a_x10cdea10 | 0 | keep walking to the supermarket and slip past him without fuss | keep_to_side | both | intent says carry_on, the plan does not |
| talk | T_head_on_de176842_5841fc4a_x42411b7c_flipped | 0 | keep walking to the supermarket and give way slightly so we can pass each other | keep_to_side;slow_down | both | intent says carry_on, the plan does not |
| independent | I_head_on_de176842_c36d5d49_r1 | 0 | Keep heading to the emergency room without slowing down, and greet Person 1 as we pass. | keep_to_side | right | intent says carry_on, the plan does not |
| independent | I_head_on_02dfbadb_3dee0df5_r1 | 1 | Keep walking to the supermarket without being knocked into again, holding my line in the passage. | keep_to_side;slow_down | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_3dee0df5_r1 | 1 | Acknowledge Person 1 and keep walking on my side of the passage | carry_on | none | intent says keep_to_side, the plan does not |
| non_verbal | N_head_on_02dfbadb_3dee0df5_r1 | 1 | Keep my line on my side of the passage and walk past Person 1 without giving way | carry_on | none | intent says keep_to_side, the plan does not |
| independent | I_head_on_de176842_2ec958bb_r1 | 1 | Keep walking to the supermarket without being bumped into again, holding my line but watching where I'm going. | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_5841fc4a_x3d3cadc7_base | 0 | Keep walking to the supermarket and give way slightly so we pass easily | keep_to_side;slow_down | both | intent says carry_on, the plan does not |
| independent | I_head_on_02dfbadb_f79677df_r1 | 0 | Keep walking to the supermarket and give the elderly man with the cane plenty of room to pass. | keep_to_side;slow_down | both | intent says carry_on, the plan does not |

### Intents the codebook could not place (the commonest)

- 2 x "greet my classmate warmly as we pass in the passage"
- 1 x "Keep well clear of the man with the cane and suitcase since he's distracted on his phone, and ease past him"
- 1 x "Keep moving toward the emergency room while making sure we can pass each other safely in the narrow passage."
- 1 x "Acknowledge her wave and pass her safely while continuing toward the emergency room."
- 1 x "Greet Person 1 warmly and give way so she can pass with her suitcase."

## 8. Real ethnicity

Descriptive. A difference between groups here is the model's behaviour towards people it was told are of a group, not a fact about those groups, and no rule may read ethnicity (`llm_negotiation/docs/ethnicity.md`).

### By group, the other's as told (unweighted agent rows)

| own | other_as_told | n | passed_first | kept_left | stopped | backed_up | plan_slowed | plan_left | plan_right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chinese | chinese | 72 | 0.219 | 0.472 | 0 | 0 | 0.694 | 0.250 | 0.403 |
| chinese | malay | 30 | 0.214 | 0.433 | 0 | 0 | 0.655 | 0.207 | 0.379 |
| chinese | indian | 36 | 0.231 | 0.389 | 0 | 0 | 0.722 | 0.222 | 0.306 |
| chinese | others | 15 | 0.250 | 0.133 | 0 | 0 | 0.867 | 0.133 | 0.400 |
| malay | chinese | 30 | 0.143 | 0.433 | 0 | 0 | 0.600 | 0.267 | 0.267 |
| malay | malay | 84 | 0.278 | 0.476 | 0.024 | 0 | 0.643 | 0.298 | 0.321 |
| malay | indian | 24 | 0.273 | 0.292 | 0 | 0 | 0.625 | 0.333 | 0.292 |
| malay | others | 24 | 0.375 | 0.458 | 0 | 0 | 0.609 | 0.348 | 0.304 |
| indian | chinese | 36 | 0.231 | 0.389 | 0 | 0 | 0.556 | 0.222 | 0.250 |
| indian | malay | 24 | 0.182 | 0.292 | 0.042 | 0 | 0.667 | 0.292 | 0.417 |
| indian | indian | 72 | 0.250 | 0.222 | 0 | 0 | 0.757 | 0.086 | 0.614 |
| indian | others | 15 | 0.333 | 0.600 | 0 | 0 | 0.467 | 0.067 | 0.400 |
| others | chinese | 15 | 0.250 | 0.133 | 0 | 0 | 0.733 | 0.067 | 0.533 |
| others | malay | 24 | 0.125 | 0.458 | 0 | 0 | 0.833 | 0.250 | 0.375 |
| others | indian | 15 | 0.444 | 0.600 | 0 | 0 | 0.643 | 0.143 | 0.357 |
| others | others | 60 | 0.233 | 0.300 | 0 | 0 | 0.733 | 0.217 | 0.533 |

Each share is over the rows where the outcome is defined (`<outcome>_n` in `ethnicity_groups.csv`).

### Weighted back to random resident pairs

Each session weighted by `ethnicity_weight`, so that the sessions stand for two residents met at random (each at the resident shares; residents only). Use the weighted rate for a population-level figure; the effective number of sessions is what the weighting leaves.

| outcome | sessions | unweighted | weighted | effective_sessions |
| --- | --- | --- | --- | --- |
| resolved_plan_only | 288 | 0.326 | 0.331 | 90.075 |
| resolved_plan_orca | 288 | 0.361 | 0.345 | 90.075 |
| resolved_by_llm | 288 | 0.326 | 0.331 | 90.075 |

## How to read this report

- **An effect here is an effect on what the LLM agents did**, in this design: a screen, so main effects are estimated clear of two-factor interactions only when the design is a resolution IV fraction (`llm_negotiation/docs/screening-designs.md`, section 3).
- **Separation** (an outcome predicted perfectly by some predictor) leaves a model with no finite estimate; it is listed, not reported as an effect. Rare outcomes with many factors cause it: D14 aims at about 10 events per factor.
- **The mapping is sparse** when there are many factors: most combinations are seen once or twice.
- **The codebooks are drafts** until RF-9's pilot (`analysis/codebooks/`): a mention or a coded intent is a keyword match, not a reading of the text.
