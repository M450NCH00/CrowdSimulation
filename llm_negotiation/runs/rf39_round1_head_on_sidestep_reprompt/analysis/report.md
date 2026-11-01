# Factor analysis of a resolution experiment (RF-8)

## Inputs

- `llm_negotiation/runs/rf39_round1_head_on_sidestep_reprompt/outcomes.csv`

- Sessions analysed (completed): **816** (independent: 272, non_verbal: 272, talk: 272); left out: none.
- Rows, one per agent per session: **1632**.
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
| kept_left | all | condition[talk] | OR 2.63 [1.84, 3.75] | < 0.001 | < 0.001 | 1630 |
| kept_left | all | knows_other | OR 0.55 [0.41, 0.73] | < 0.001 | 0.041 | 1630 |
| passed_first | all | own_assertiveness | OR 3.85 [2.48, 5.98] | < 0.001 | < 0.001 | 984 |
| passed_first | all | condition[non_verbal] | OR 2.94 [1.79, 4.83] | < 0.001 | 0.015 | 984 |
| passed_first | non_verbal | own_assertiveness | OR 4.88 [2.34, 10.17] | < 0.001 | 0.017 | 374 |
| passed_first | talk | own_assertiveness | OR 5.25 [2.46, 11.20] | < 0.001 | 0.013 | 350 |
| plan_left | all | own_assertiveness | OR 0.25 [0.17, 0.35] | < 0.001 | < 0.001 | 1602 |
| plan_left | all | condition[talk] | OR 2.83 [2.17, 3.71] | < 0.001 | < 0.001 | 1602 |
| plan_left | all | own_residence | OR 0.30 [0.21, 0.42] | < 0.001 | < 0.001 | 1602 |
| plan_left | all | own_urgency | OR 0.40 [0.29, 0.56] | < 0.001 | < 0.001 | 1602 |
| plan_left | all | own_age_high | OR 2.31 [1.64, 3.25] | < 0.001 | 0.001 | 1602 |
| plan_left | all | condition[non_verbal] | OR 1.88 [1.43, 2.46] | < 0.001 | 0.004 | 1602 |
| plan_left | non_verbal | own_assertiveness | OR 0.13 [0.07, 0.26] | < 0.001 | < 0.001 | 544 |
| plan_left | non_verbal | own_residence | OR 0.20 [0.11, 0.39] | < 0.001 | 0.001 | 544 |
| plan_left | talk | own_assertiveness | OR 0.19 [0.11, 0.36] | < 0.001 | < 0.001 | 543 |
| plan_left | talk | own_residence | OR 0.28 [0.15, 0.52] | < 0.001 | 0.037 | 543 |
| plan_right | all | own_residence | OR 2.59 [1.90, 3.53] | < 0.001 | < 0.001 | 1602 |
| plan_right | all | condition[talk] | OR 0.47 [0.36, 0.60] | < 0.001 | < 0.001 | 1602 |
| plan_right | all | own_urgency | OR 2.12 [1.56, 2.88] | < 0.001 | 0.001 | 1602 |
| plan_right | all | own_age_high | OR 0.51 [0.37, 0.69] | < 0.001 | 0.011 | 1602 |
| plan_right | all | knows_other | OR 1.55 [1.25, 1.91] | < 0.001 | 0.036 | 1602 |
| plan_right | talk | own_residence | OR 3.66 [2.08, 6.45] | < 0.001 | 0.005 | 543 |
| plan_slowed | all | other_mobility_aid | OR 4.43 [3.00, 6.54] | < 0.001 | < 0.001 | 1602 |
| plan_slowed | all | other_age_high | OR 4.93 [3.24, 7.50] | < 0.001 | < 0.001 | 1602 |
| plan_slowed | all | knows_other | OR 2.48 [1.95, 3.16] | < 0.001 | < 0.001 | 1602 |
| plan_slowed | all | own_urgency | OR 0.36 [0.26, 0.50] | < 0.001 | < 0.001 | 1602 |
| plan_slowed | all | condition[non_verbal] | OR 2.35 [1.75, 3.15] | < 0.001 | < 0.001 | 1602 |
| plan_slowed | all | other_load | OR 2.72 [1.88, 3.95] | < 0.001 | < 0.001 | 1602 |
| plan_slowed | all | own_age_high | OR 2.42 [1.74, 3.35] | < 0.001 | < 0.001 | 1602 |
| plan_slowed | all | finds_other_attractive | OR 1.80 [1.40, 2.32] | < 0.001 | 0.003 | 1602 |
| plan_slowed | all | own_assertiveness | OR 0.48 [0.34, 0.67] | < 0.001 | 0.009 | 1602 |
| plan_slowed | all | condition[talk] | OR 1.90 [1.41, 2.57] | < 0.001 | 0.020 | 1602 |
| plan_slowed | all | own_mobility_aid | OR 1.97 [1.42, 2.74] | < 0.001 | 0.033 | 1602 |
| plan_slowed | independent | knows_other | OR 3.86 [2.50, 5.98] | < 0.001 | < 0.001 | 515 |
| plan_slowed | independent | other_age_high | OR 5.68 [2.82, 11.43] | < 0.001 | < 0.001 | 515 |
| plan_slowed | independent | finds_other_attractive | OR 2.89 [1.81, 4.60] | < 0.001 | 0.006 | 515 |
| plan_slowed | non_verbal | other_mobility_aid | OR 21.49 [6.33, 72.98] | < 0.001 | < 0.001 | 544 |
| plan_slowed | non_verbal | own_age_high | OR 3.43 [1.89, 6.22] | < 0.001 | 0.036 | 544 |
| plan_slowed | talk | own_urgency | OR 0.27 [0.15, 0.48] | < 0.001 | 0.005 | 543 |
| plan_slowed | talk | other_age_high | OR 5.07 [2.38, 10.81] | < 0.001 | 0.019 | 543 |
| signalled | all | knows_other | OR 39.37 [22.18, 69.86] | < 0.001 | < 0.001 | 1088 |
| signalled | all | own_assertiveness | OR 7.90 [4.32, 14.42] | < 0.001 | < 0.001 | 1088 |
| signalled | all | finds_other_attractive | OR 2.85 [1.99, 4.10] | < 0.001 | < 0.001 | 1088 |
| signalled | non_verbal | knows_other | OR 39.09 [17.78, 85.93] | < 0.001 | < 0.001 | 544 |
| signalled | non_verbal | own_assertiveness | OR 7.79 [3.60, 16.86] | < 0.001 | < 0.001 | 544 |
| signalled | talk | knows_other | OR 52.35 [20.37, 134.55] | < 0.001 | < 0.001 | 544 |
| signalled | talk | own_assertiveness | OR 11.28 [3.91, 32.54] | < 0.001 | 0.005 | 544 |
| signalled | talk | finds_other_attractive | OR 3.67 [2.03, 6.65] | < 0.001 | 0.013 | 544 |
| start_distance_m | all | own_distraction | -1.564 [-2.308, -0.820] | < 0.001 | 0.027 | 61 |
| start_distance_m | all | own_load | +2.018 [+1.046, +2.991] | < 0.001 | 0.034 | 61 |
| start_distance_m | non_verbal | own_mobility_aid | +1.854 [+1.282, +2.426] | < 0.001 | < 0.001 | 44 |
| decision_points | all | condition[non_verbal] | +4.268 [+3.918, +4.619] | < 0.001 | < 0.001 | 816 |
| decision_points | all | condition[talk] | +4.390 [+3.988, +4.791] | < 0.001 | < 0.001 | 816 |
| decision_points | all | load[p1] | +0.779 [+0.413, +1.145] | < 0.001 | 0.022 | 816 |
| resolved_by_llm | all | condition[talk] | OR 2.80 [1.97, 3.98] | < 0.001 | < 0.001 | 816 |
| resolved_by_llm | all | condition[non_verbal] | OR 2.62 [1.84, 3.74] | < 0.001 | < 0.001 | 816 |
| resolved_plan_only | all | condition[talk] | OR 2.80 [1.97, 3.98] | < 0.001 | < 0.001 | 816 |
| resolved_plan_only | all | condition[non_verbal] | OR 2.62 [1.84, 3.74] | < 0.001 | < 0.001 | 816 |
| resolved_plan_orca | all | condition[non_verbal] | OR 2.68 [1.88, 3.82] | < 0.001 | < 0.001 | 816 |
| resolved_plan_orca | all | condition[talk] | OR 2.35 [1.65, 3.34] | < 0.001 | 0.001 | 816 |
| resolved_plan_orca | all | load[p1] | OR 0.52 [0.38, 0.69] | < 0.001 | 0.007 | 816 |

### Every model

| outcome | level | subset | status | n | events | clusters | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| passed_first | agent | all | ok | 984 | 191 | 492 |  |
| kept_left | agent | all | ok | 1630 | 910 | 815 |  |
| stopped | agent | all | separation | 1632 | 13 | 816 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | all | one value | 1632 | 0 | - | every row is 0 |
| plan_left | agent | all | ok | 1602 | 731 | 815 |  |
| plan_right | agent | all | ok | 1602 | 779 | 815 |  |
| plan_slowed | agent | all | ok | 1602 | 1000 | 815 |  |
| plan_stopped | agent | all | separation | 1602 | 3 | 815 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | all | one value | 1602 | 0 | - | every row is 0 |
| start_distance_m | agent | all | ok | 61 | - | 59 |  |
| signalled | agent | all | ok | 1088 | 769 | 544 |  |
| resolved_plan_only | session | all | ok | 816 | 428 | - |  |
| resolved_plan_orca | session | all | ok | 816 | 451 | - |  |
| resolved_by_llm | session | all | ok | 816 | 428 | - |  |
| decision_points | session | all | ok | 816 | - | - |  |
| passed_first | agent | independent | ok | 260 | 28 | 130 |  |
| kept_left | agent | independent | ok | 544 | 242 | 272 |  |
| stopped | agent | independent | separation | 544 | 1 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | independent | one value | 544 | 0 | - | every row is 0 |
| plan_left | agent | independent | ok | 515 | 175 | 271 |  |
| plan_right | agent | independent | ok | 515 | 295 | 271 |  |
| plan_slowed | agent | independent | ok | 515 | 275 | 271 |  |
| plan_stopped | agent | independent | separation | 515 | 1 | 271 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | independent | one value | 515 | 0 | - | every row is 0 |
| start_distance_m | agent | independent | no data | 6 | - | - | 6 rows for 6 parameters |
| signalled | agent | independent | no data | 0 | - | - |  |
| resolved_plan_only | session | independent | ok | 272 | 100 | - |  |
| resolved_plan_orca | session | independent | ok | 272 | 111 | - |  |
| resolved_by_llm | session | independent | ok | 272 | 100 | - |  |
| decision_points | session | independent | one value | 272 | - | - | every row is 2 |
| passed_first | agent | non_verbal | ok | 374 | 93 | 187 |  |
| kept_left | agent | non_verbal | ok | 542 | 304 | 271 |  |
| stopped | agent | non_verbal | separation | 544 | 5 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | non_verbal | one value | 544 | 0 | - | every row is 0 |
| plan_left | agent | non_verbal | ok | 544 | 255 | 272 |  |
| plan_right | agent | non_verbal | ok | 544 | 265 | 272 |  |
| plan_slowed | agent | non_verbal | ok | 544 | 372 | 272 |  |
| plan_stopped | agent | non_verbal | one value | 544 | 0 | - | every row is 0 |
| plan_backed_up | agent | non_verbal | one value | 544 | 0 | - | every row is 0 |
| start_distance_m | agent | non_verbal | ok | 44 | - | 43 |  |
| signalled | agent | non_verbal | ok | 544 | 359 | 272 |  |
| resolved_plan_only | session | non_verbal | ok | 272 | 162 | - |  |
| resolved_plan_orca | session | non_verbal | ok | 272 | 174 | - |  |
| resolved_by_llm | session | non_verbal | ok | 272 | 162 | - |  |
| decision_points | session | non_verbal | ok | 272 | - | - |  |
| passed_first | agent | talk | ok | 350 | 70 | 175 |  |
| kept_left | agent | talk | ok | 544 | 364 | 272 |  |
| stopped | agent | talk | separation | 544 | 7 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | talk | one value | 544 | 0 | - | every row is 0 |
| plan_left | agent | talk | ok | 543 | 301 | 272 |  |
| plan_right | agent | talk | ok | 543 | 219 | 272 |  |
| plan_slowed | agent | talk | ok | 543 | 353 | 272 |  |
| plan_stopped | agent | talk | separation | 543 | 2 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | talk | one value | 543 | 0 | - | every row is 0 |
| start_distance_m | agent | talk | ok | 11 | - | 10 |  |
| signalled | agent | talk | ok | 544 | 410 | 272 |  |
| resolved_plan_only | session | talk | ok | 272 | 166 | - |  |
| resolved_plan_orca | session | talk | ok | 272 | 166 | - |  |
| resolved_by_llm | session | talk | ok | 272 | 166 | - |  |
| decision_points | session | talk | ok | 272 | - | - |  |

### Each outcome, all conditions together

Per outcome: what it is, and every term of the pooled model (the per-condition terms are in `effects_terms.csv`).

**`passed_first`** (agent): left the conflict zone first (physical; `together` counts as not first). Status: ok, n = 984, events = 191.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.03 [0.68, 1.58] | 0.879 | 1.000 |
| own_female | OR 0.99 [0.67, 1.45] | 0.942 | 1.000 |
| other_age_high | OR 0.58 [0.31, 1.12] | 0.104 | 1.000 |
| own_urgency | OR 1.18 [0.77, 1.80] | 0.443 | 1.000 |
| own_mobility_aid | OR 1.46 [0.96, 2.22] | 0.075 | 1.000 |
| own_load | OR 1.29 [0.85, 1.96] | 0.237 | 1.000 |
| own_distraction | OR 0.84 [0.55, 1.28] | 0.406 | 1.000 |
| own_assertiveness | OR 3.85 [2.48, 5.98] | < 0.001 | < 0.001 |
| own_residence | OR 1.04 [0.68, 1.58] | 0.866 | 1.000 |
| own_memory_note | OR 0.89 [0.58, 1.37] | 0.610 | 1.000 |
| other_mobility_aid | OR 0.72 [0.39, 1.35] | 0.308 | 1.000 |
| other_load | OR 0.35 [0.17, 0.71] | 0.004 | 1.000 |
| other_distraction | OR 1.78 [0.98, 3.22] | 0.057 | 1.000 |
| same_ethnicity | OR 1.02 [0.74, 1.41] | 0.901 | 1.000 |
| surroundings_busy | OR 1.31 [0.95, 1.81] | 0.100 | 1.000 |
| time_of_day_late_night | OR 0.83 [0.59, 1.15] | 0.251 | 1.000 |
| finds_other_attractive | OR 0.85 [0.59, 1.22] | 0.378 | 1.000 |
| knows_other | OR 1.03 [0.74, 1.43] | 0.863 | 1.000 |
| is_lower_agent | OR 1.43 [0.98, 2.10] | 0.064 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.25 [0.91, 1.71] | 0.175 | 1.000 |
| condition[non_verbal] | OR 2.94 [1.79, 4.83] | < 0.001 | 0.015 |
| condition[talk] | OR 2.09 [1.25, 3.48] | 0.005 | 1.000 |

Left out of the model: other_female (collinear).

**`kept_left`** (agent): kept to its own left at the closest approach (physical; rows where the two were not abreast are left out). Status: ok, n = 1630, events = 910.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.00 [0.74, 1.34] | 0.997 | 1.000 |
| own_female | OR 1.00 [0.98, 1.01] | 0.486 | 1.000 |
| other_age_high | OR 0.93 [0.69, 1.24] | 0.613 | 1.000 |
| own_urgency | OR 0.97 [0.73, 1.28] | 0.804 | 1.000 |
| own_mobility_aid | OR 1.05 [0.78, 1.42] | 0.738 | 1.000 |
| own_load | OR 1.31 [0.97, 1.77] | 0.074 | 1.000 |
| own_distraction | OR 1.21 [0.90, 1.64] | 0.207 | 1.000 |
| own_assertiveness | OR 0.80 [0.60, 1.06] | 0.122 | 1.000 |
| own_residence | OR 0.86 [0.65, 1.13] | 0.279 | 1.000 |
| own_memory_note | OR 1.02 [0.77, 1.35] | 0.911 | 1.000 |
| other_mobility_aid | OR 0.97 [0.72, 1.31] | 0.855 | 1.000 |
| other_load | OR 1.21 [0.90, 1.63] | 0.206 | 1.000 |
| other_distraction | OR 1.11 [0.83, 1.50] | 0.471 | 1.000 |
| same_ethnicity | OR 0.80 [0.60, 1.07] | 0.141 | 1.000 |
| surroundings_busy | OR 0.66 [0.49, 0.89] | 0.006 | 1.000 |
| time_of_day_late_night | OR 0.92 [0.68, 1.23] | 0.551 | 1.000 |
| finds_other_attractive | OR 1.12 [0.91, 1.38] | 0.288 | 1.000 |
| knows_other | OR 0.55 [0.41, 0.73] | < 0.001 | 0.041 |
| is_lower_agent | OR 1.00 [0.98, 1.01] | 0.936 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.12 [0.84, 1.49] | 0.447 | 1.000 |
| condition[non_verbal] | OR 1.63 [1.15, 2.30] | 0.006 | 1.000 |
| condition[talk] | OR 2.63 [1.84, 3.75] | < 0.001 | < 0.001 |

Left out of the model: other_female (collinear).

**`stopped`** (agent): its speed fell below the deadlock monitor's threshold (physical). Status: separation, n = 1632, events = 13.

Left out of the model: other_female (collinear).

**`backed_up`** (agent): moved against its path (physical). Status: one value, n = 1632, events = 0.

**`plan_left`** (agent): its first plan turns to its left only. Status: ok, n = 1602, events = 731.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 2.31 [1.64, 3.25] | < 0.001 | 0.001 |
| own_female | OR 0.97 [0.78, 1.22] | 0.816 | 1.000 |
| other_age_high | OR 0.84 [0.63, 1.12] | 0.241 | 1.000 |
| own_urgency | OR 0.40 [0.29, 0.56] | < 0.001 | < 0.001 |
| own_mobility_aid | OR 1.18 [0.85, 1.64] | 0.333 | 1.000 |
| own_load | OR 1.08 [0.77, 1.51] | 0.659 | 1.000 |
| own_distraction | OR 1.42 [1.02, 1.98] | 0.038 | 1.000 |
| own_assertiveness | OR 0.25 [0.17, 0.35] | < 0.001 | < 0.001 |
| own_residence | OR 0.30 [0.21, 0.42] | < 0.001 | < 0.001 |
| own_memory_note | OR 0.89 [0.64, 1.24] | 0.499 | 1.000 |
| other_mobility_aid | OR 1.09 [0.82, 1.46] | 0.554 | 1.000 |
| other_load | OR 1.07 [0.81, 1.42] | 0.636 | 1.000 |
| other_distraction | OR 1.10 [0.83, 1.45] | 0.525 | 1.000 |
| same_ethnicity | OR 0.82 [0.66, 1.02] | 0.072 | 1.000 |
| surroundings_busy | OR 0.70 [0.56, 0.86] | 0.001 | 0.736 |
| time_of_day_late_night | OR 0.90 [0.72, 1.12] | 0.341 | 1.000 |
| finds_other_attractive | OR 1.09 [0.88, 1.37] | 0.429 | 1.000 |
| knows_other | OR 0.72 [0.58, 0.89] | 0.003 | 1.000 |
| is_lower_agent | OR 1.08 [0.87, 1.35] | 0.478 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.07 [0.86, 1.32] | 0.549 | 1.000 |
| condition[non_verbal] | OR 1.88 [1.43, 2.46] | < 0.001 | 0.004 |
| condition[talk] | OR 2.83 [2.17, 3.71] | < 0.001 | < 0.001 |

Left out of the model: other_female (collinear).

**`plan_right`** (agent): its first plan turns to its right only. Status: ok, n = 1602, events = 779.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.51 [0.37, 0.69] | < 0.001 | 0.011 |
| own_female | OR 1.06 [0.86, 1.31] | 0.575 | 1.000 |
| other_age_high | OR 1.09 [0.82, 1.44] | 0.574 | 1.000 |
| own_urgency | OR 2.12 [1.56, 2.88] | < 0.001 | 0.001 |
| own_mobility_aid | OR 1.06 [0.78, 1.44] | 0.700 | 1.000 |
| own_load | OR 0.85 [0.63, 1.15] | 0.296 | 1.000 |
| own_distraction | OR 0.72 [0.53, 0.98] | 0.034 | 1.000 |
| own_assertiveness | OR 1.80 [1.33, 2.45] | < 0.001 | 0.119 |
| own_residence | OR 2.59 [1.90, 3.53] | < 0.001 | < 0.001 |
| own_memory_note | OR 1.17 [0.86, 1.59] | 0.318 | 1.000 |
| other_mobility_aid | OR 0.94 [0.70, 1.25] | 0.657 | 1.000 |
| other_load | OR 0.94 [0.71, 1.25] | 0.690 | 1.000 |
| other_distraction | OR 0.94 [0.71, 1.25] | 0.685 | 1.000 |
| same_ethnicity | OR 1.21 [0.98, 1.49] | 0.077 | 1.000 |
| surroundings_busy | OR 1.39 [1.13, 1.71] | 0.002 | 1.000 |
| time_of_day_late_night | OR 1.13 [0.92, 1.40] | 0.245 | 1.000 |
| finds_other_attractive | OR 0.93 [0.76, 1.15] | 0.510 | 1.000 |
| knows_other | OR 1.55 [1.25, 1.91] | < 0.001 | 0.036 |
| is_lower_agent | OR 0.94 [0.76, 1.17] | 0.603 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.96 [0.78, 1.19] | 0.719 | 1.000 |
| condition[non_verbal] | OR 0.68 [0.53, 0.89] | 0.004 | 1.000 |
| condition[talk] | OR 0.47 [0.36, 0.60] | < 0.001 | < 0.001 |

Left out of the model: other_female (collinear).

**`plan_slowed`** (agent): its first plan slows below its speed at the decision. Status: ok, n = 1602, events = 1000.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 2.42 [1.74, 3.35] | < 0.001 | < 0.001 |
| own_female | OR 0.92 [0.72, 1.19] | 0.524 | 1.000 |
| other_age_high | OR 4.93 [3.24, 7.50] | < 0.001 | < 0.001 |
| own_urgency | OR 0.36 [0.26, 0.50] | < 0.001 | < 0.001 |
| own_mobility_aid | OR 1.97 [1.42, 2.74] | < 0.001 | 0.033 |
| own_load | OR 1.77 [1.28, 2.45] | < 0.001 | 0.400 |
| own_distraction | OR 1.38 [1.00, 1.91] | 0.050 | 1.000 |
| own_assertiveness | OR 0.48 [0.34, 0.67] | < 0.001 | 0.009 |
| own_residence | OR 0.89 [0.64, 1.23] | 0.471 | 1.000 |
| own_memory_note | OR 1.03 [0.74, 1.42] | 0.871 | 1.000 |
| other_mobility_aid | OR 4.43 [3.00, 6.54] | < 0.001 | < 0.001 |
| other_load | OR 2.72 [1.88, 3.95] | < 0.001 | < 0.001 |
| other_distraction | OR 0.96 [0.66, 1.38] | 0.819 | 1.000 |
| same_ethnicity | OR 0.95 [0.74, 1.20] | 0.648 | 1.000 |
| surroundings_busy | OR 1.07 [0.84, 1.36] | 0.595 | 1.000 |
| time_of_day_late_night | OR 1.14 [0.89, 1.46] | 0.286 | 1.000 |
| finds_other_attractive | OR 1.80 [1.40, 2.32] | < 0.001 | 0.003 |
| knows_other | OR 2.48 [1.95, 3.16] | < 0.001 | < 0.001 |
| is_lower_agent | OR 1.03 [0.80, 1.32] | 0.819 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.90 [0.71, 1.14] | 0.386 | 1.000 |
| condition[non_verbal] | OR 2.35 [1.75, 3.15] | < 0.001 | < 0.001 |
| condition[talk] | OR 1.90 [1.41, 2.57] | < 0.001 | 0.020 |

Left out of the model: other_female (collinear).

**`plan_stopped`** (agent): its first plan stops. Status: separation, n = 1602, events = 3.

Left out of the model: other_female (collinear).

**`plan_backed_up`** (agent): its first plan backs up. Status: one value, n = 1602, events = 0.

**`start_distance_m`** (agent): its first plan starts at this distance (plans that start so). Status: ok, n = 61.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | +0.589 [-0.517, +1.696] | 0.297 | 1.000 |
| own_female | +0.035 [-0.285, +0.356] | 0.829 | 1.000 |
| other_age_high | +0.558 [+0.138, +0.978] | 0.009 | 1.000 |
| own_urgency | -1.318 [-2.126, -0.509] | 0.001 | 0.971 |
| own_mobility_aid | +1.185 [+0.334, +2.037] | 0.006 | 1.000 |
| own_load | +2.018 [+1.046, +2.991] | < 0.001 | 0.034 |
| own_distraction | -1.564 [-2.308, -0.820] | < 0.001 | 0.027 |
| own_assertiveness | +0.597 [-0.139, +1.333] | 0.112 | 1.000 |
| own_residence | +0.118 [-0.625, +0.861] | 0.755 | 1.000 |
| other_mobility_aid | +0.512 [+0.134, +0.891] | 0.008 | 1.000 |
| other_load | +0.201 [-0.127, +0.528] | 0.229 | 1.000 |
| other_distraction | -0.438 [-0.931, +0.056] | 0.082 | 1.000 |
| same_ethnicity | -0.101 [-0.578, +0.376] | 0.679 | 1.000 |
| surroundings_busy | -0.122 [-0.496, +0.252] | 0.522 | 1.000 |
| time_of_day_late_night | -0.268 [-0.749, +0.213] | 0.274 | 1.000 |
| finds_other_attractive | -0.209 [-0.699, +0.282] | 0.405 | 1.000 |
| knows_other | +0.345 [-0.142, +0.831] | 0.165 | 1.000 |
| is_lower_agent | +0.001 [-0.366, +0.368] | 0.996 | 1.000 |
| geometry[layout=apart_20cm] | -0.047 [-0.332, +0.238] | 0.744 | 1.000 |
| condition[non_verbal] | +0.089 [-0.316, +0.494] | 0.665 | 1.000 |
| condition[talk] | +0.172 [-0.503, +0.846] | 0.618 | 1.000 |

Left out of the model: other_female (collinear); own_memory_note (collinear).

**`signalled`** (agent): it signalled at least once (non-verbal and talk only). Status: ok, n = 1088, events = 769.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.68 [0.39, 1.18] | 0.173 | 1.000 |
| own_female | OR 1.29 [1.01, 1.65] | 0.045 | 1.000 |
| other_age_high | OR 1.22 [0.76, 1.97] | 0.410 | 1.000 |
| own_urgency | OR 1.72 [1.01, 2.93] | 0.047 | 1.000 |
| own_mobility_aid | OR 1.16 [0.68, 1.98] | 0.587 | 1.000 |
| own_load | OR 1.21 [0.71, 2.06] | 0.480 | 1.000 |
| own_distraction | OR 1.48 [0.87, 2.52] | 0.151 | 1.000 |
| own_assertiveness | OR 7.90 [4.32, 14.42] | < 0.001 | < 0.001 |
| own_residence | OR 0.55 [0.32, 0.93] | 0.027 | 1.000 |
| own_memory_note | OR 1.65 [0.97, 2.80] | 0.064 | 1.000 |
| other_mobility_aid | OR 1.94 [1.19, 3.15] | 0.008 | 1.000 |
| other_load | OR 1.72 [1.04, 2.85] | 0.034 | 1.000 |
| other_distraction | OR 0.84 [0.52, 1.35] | 0.464 | 1.000 |
| same_ethnicity | OR 1.51 [0.98, 2.34] | 0.061 | 1.000 |
| surroundings_busy | OR 0.75 [0.48, 1.17] | 0.209 | 1.000 |
| time_of_day_late_night | OR 1.24 [0.80, 1.91] | 0.342 | 1.000 |
| finds_other_attractive | OR 2.85 [1.99, 4.10] | < 0.001 | < 0.001 |
| knows_other | OR 39.37 [22.18, 69.86] | < 0.001 | < 0.001 |
| is_lower_agent | OR 0.90 [0.70, 1.15] | 0.380 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.70 [0.46, 1.07] | 0.101 | 1.000 |
| condition[talk] | OR 2.20 [1.44, 3.38] | < 0.001 | 0.209 |

Left out of the model: other_female (collinear).

**`resolved_plan_only`** (session): resolved in `plan_only` (the Step 1 measure). Status: ok, n = 816, events = 428.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.96 [0.72, 1.28] | 0.778 | 1.000 |
| gender_pair[p1_male] | OR 0.82 [0.61, 1.09] | 0.177 | 1.000 |
| urgency[p1] | OR 1.15 [0.86, 1.54] | 0.356 | 1.000 |
| mobility_aid[p1] | OR 1.20 [0.90, 1.61] | 0.218 | 1.000 |
| load[p1] | OR 0.57 [0.43, 0.77] | < 0.001 | 0.133 |
| distraction[p1] | OR 1.07 [0.80, 1.44] | 0.631 | 1.000 |
| assertiveness[p1] | OR 0.75 [0.56, 1.00] | 0.053 | 1.000 |
| residence[p1] | OR 0.88 [0.66, 1.17] | 0.378 | 1.000 |
| memory_note[p1] | OR 0.92 [0.68, 1.22] | 0.553 | 1.000 |
| ethnicity_pair[different] | OR 0.88 [0.66, 1.18] | 0.392 | 1.000 |
| surroundings[busy] | OR 1.02 [0.77, 1.37] | 0.873 | 1.000 |
| time_of_day[late_night] | OR 1.07 [0.80, 1.43] | 0.647 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 1.02 [0.76, 1.36] | 0.912 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 0.95 [0.71, 1.27] | 0.740 | 1.000 |
| familiarity[strangers] | OR 1.07 [0.80, 1.43] | 0.661 | 1.000 |
| mapping[p1_higher] | OR 0.88 [0.66, 1.17] | 0.374 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.81 [0.61, 1.08] | 0.144 | 1.000 |
| condition[non_verbal] | OR 2.62 [1.84, 3.74] | < 0.001 | < 0.001 |
| condition[talk] | OR 2.80 [1.97, 3.98] | < 0.001 | < 0.001 |

**`resolved_plan_orca`** (session): resolved in `plan_orca`. Status: ok, n = 816, events = 451.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.99 [0.74, 1.32] | 0.937 | 1.000 |
| gender_pair[p1_male] | OR 0.77 [0.58, 1.03] | 0.079 | 1.000 |
| urgency[p1] | OR 1.21 [0.91, 1.62] | 0.197 | 1.000 |
| mobility_aid[p1] | OR 1.16 [0.87, 1.56] | 0.314 | 1.000 |
| load[p1] | OR 0.52 [0.38, 0.69] | < 0.001 | 0.007 |
| distraction[p1] | OR 1.04 [0.77, 1.39] | 0.806 | 1.000 |
| assertiveness[p1] | OR 0.95 [0.71, 1.27] | 0.722 | 1.000 |
| residence[p1] | OR 0.90 [0.67, 1.21] | 0.486 | 1.000 |
| memory_note[p1] | OR 0.94 [0.70, 1.26] | 0.692 | 1.000 |
| ethnicity_pair[different] | OR 0.91 [0.68, 1.21] | 0.514 | 1.000 |
| surroundings[busy] | OR 0.99 [0.74, 1.32] | 0.939 | 1.000 |
| time_of_day[late_night] | OR 1.01 [0.75, 1.35] | 0.951 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 1.10 [0.83, 1.47] | 0.507 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 0.94 [0.70, 1.26] | 0.695 | 1.000 |
| familiarity[strangers] | OR 1.09 [0.81, 1.45] | 0.580 | 1.000 |
| mapping[p1_higher] | OR 0.82 [0.62, 1.10] | 0.192 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.91 [0.68, 1.21] | 0.509 | 1.000 |
| condition[non_verbal] | OR 2.68 [1.88, 3.82] | < 0.001 | < 0.001 |
| condition[talk] | OR 2.35 [1.65, 3.34] | < 0.001 | 0.001 |

**`resolved_by_llm`** (session): resolved in `plan_only` before ORCA took over. Status: ok, n = 816, events = 428.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.96 [0.72, 1.28] | 0.778 | 1.000 |
| gender_pair[p1_male] | OR 0.82 [0.61, 1.09] | 0.177 | 1.000 |
| urgency[p1] | OR 1.15 [0.86, 1.54] | 0.356 | 1.000 |
| mobility_aid[p1] | OR 1.20 [0.90, 1.61] | 0.218 | 1.000 |
| load[p1] | OR 0.57 [0.43, 0.77] | < 0.001 | 0.133 |
| distraction[p1] | OR 1.07 [0.80, 1.44] | 0.631 | 1.000 |
| assertiveness[p1] | OR 0.75 [0.56, 1.00] | 0.053 | 1.000 |
| residence[p1] | OR 0.88 [0.66, 1.17] | 0.378 | 1.000 |
| memory_note[p1] | OR 0.92 [0.68, 1.22] | 0.553 | 1.000 |
| ethnicity_pair[different] | OR 0.88 [0.66, 1.18] | 0.392 | 1.000 |
| surroundings[busy] | OR 1.02 [0.77, 1.37] | 0.873 | 1.000 |
| time_of_day[late_night] | OR 1.07 [0.80, 1.43] | 0.647 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 1.02 [0.76, 1.36] | 0.912 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 0.95 [0.71, 1.27] | 0.740 | 1.000 |
| familiarity[strangers] | OR 1.07 [0.80, 1.43] | 0.661 | 1.000 |
| mapping[p1_higher] | OR 0.88 [0.66, 1.17] | 0.374 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.81 [0.61, 1.08] | 0.144 | 1.000 |
| condition[non_verbal] | OR 2.62 [1.84, 3.74] | < 0.001 | < 0.001 |
| condition[talk] | OR 2.80 [1.97, 3.98] | < 0.001 | < 0.001 |

**`decision_points`** (session): decision points of both people. Status: ok, n = 816.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | +0.170 [-0.195, +0.535] | 0.362 | 1.000 |
| gender_pair[p1_male] | +0.024 [-0.340, +0.388] | 0.897 | 1.000 |
| urgency[p1] | -0.122 [-0.484, +0.240] | 0.510 | 1.000 |
| mobility_aid[p1] | -0.148 [-0.514, +0.218] | 0.428 | 1.000 |
| load[p1] | +0.779 [+0.413, +1.145] | < 0.001 | 0.022 |
| distraction[p1] | -0.070 [-0.433, +0.293] | 0.706 | 1.000 |
| assertiveness[p1] | +0.300 [-0.059, +0.659] | 0.102 | 1.000 |
| residence[p1] | -0.023 [-0.386, +0.340] | 0.901 | 1.000 |
| memory_note[p1] | +0.196 [-0.168, +0.560] | 0.292 | 1.000 |
| ethnicity_pair[different] | +0.055 [-0.297, +0.408] | 0.757 | 1.000 |
| surroundings[busy] | +0.055 [-0.307, +0.418] | 0.765 | 1.000 |
| time_of_day[late_night] | +0.112 [-0.249, +0.474] | 0.541 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | +0.060 [-0.300, +0.419] | 0.745 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | -0.222 [-0.585, +0.141] | 0.231 | 1.000 |
| familiarity[strangers] | -0.274 [-0.639, +0.091] | 0.141 | 1.000 |
| mapping[p1_higher] | +0.326 [-0.038, +0.690] | 0.079 | 1.000 |
| geometry[layout=apart_20cm] | +0.027 [-0.326, +0.379] | 0.881 | 1.000 |
| condition[non_verbal] | +4.268 [+3.918, +4.619] | < 0.001 | < 0.001 |
| condition[talk] | +4.390 [+3.988, +4.791] | < 0.001 | < 0.001 |

## 2. Decision tree

Predicts **`passed_first`** per agent, depth at most 3, on 984 rows (the predictors that vary, with condition and geometry). Figure: `tree.png`.

- Accuracy on the rows it was grown on: 0.820; always guessing the commoner outcome: 0.806.
- Accuracy on held-out sessions (5-fold, grouped by session): 0.803.
- Splits on: `condition[non_verbal]`, `condition[talk]`, `is_lower_agent`, `other_load`, `own_age_high`, `own_assertiveness`.

A tree no better on held-out sessions than the commoner outcome has found no usable pattern.

```
|--- own_assertiveness <= 0.50
|   |--- own_age_high <= 0.50
|   |   |--- other_load <= 0.50
|   |   |   |--- weights: [380.00, 53.00] class: 0
|   |   |--- other_load >  0.50
|   |   |   |--- weights: [193.00, 10.00] class: 0
|   |--- own_age_high >  0.50
|   |   |--- is_lower_agent <= 0.50
|   |   |   |--- weights: [45.00, 8.00] class: 0
|   |   |--- is_lower_agent >  0.50
|   |   |   |--- weights: [42.00, 17.00] class: 0
|--- own_assertiveness >  0.50
|   |--- condition[non_verbal] <= 0.50
|   |   |--- condition[talk] <= 0.50
|   |   |   |--- weights: [49.00, 8.00] class: 0
|   |   |--- condition[talk] >  0.50
|   |   |   |--- weights: [42.00, 43.00] class: 1
|   |--- condition[non_verbal] >  0.50
|   |   |--- own_age_high <= 0.50
|   |   |   |--- weights: [16.00, 29.00] class: 1
|   |   |--- own_age_high >  0.50
|   |   |   |--- weights: [26.00, 23.00] class: 0
```

## 3. Counterfactual pairs against the noise floor

The noise floor is the flip rate between repeats of one cell of the exact-repeat set (identical prompts), with a bootstrap 95% interval over cells. A pair's flip rate (Wilson 95% interval) counts as evidence only where its lower end is above the noise floor's upper end, in the same condition. Components: `who_passed_first`, `passing_side`, `stopped`, `backed_up`, `behaviour` (`behaviour` is all of them together).

### The noise floor

| component | subset | cells | pairs | flips | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| who_passed_first | all | 192 | 1152 | 723 | 0.628 | 0.596 | 0.658 |
| who_passed_first | independent | 64 | 384 | 215 | 0.560 | 0.495 | 0.617 |
| who_passed_first | non_verbal | 64 | 384 | 263 | 0.685 | 0.641 | 0.729 |
| who_passed_first | talk | 64 | 384 | 245 | 0.638 | 0.589 | 0.688 |
| passing_side | all | 192 | 1152 | 520 | 0.451 | 0.416 | 0.485 |
| passing_side | independent | 64 | 384 | 171 | 0.445 | 0.388 | 0.497 |
| passing_side | non_verbal | 64 | 384 | 180 | 0.469 | 0.406 | 0.523 |
| passing_side | talk | 64 | 384 | 169 | 0.440 | 0.375 | 0.500 |
| stopped | all | 192 | 1152 | 36 | 0.031 | 0.016 | 0.049 |
| stopped | independent | 64 | 384 | 3 | 0.008 | 0 | 0.023 |
| stopped | non_verbal | 64 | 384 | 12 | 0.031 | 0.008 | 0.062 |
| stopped | talk | 64 | 384 | 21 | 0.055 | 0.016 | 0.094 |
| backed_up | all | 192 | 1152 | 0 | 0 | 0 | 0 |
| backed_up | independent | 64 | 384 | 0 | 0 | 0 | 0 |
| backed_up | non_verbal | 64 | 384 | 0 | 0 | 0 | 0 |
| backed_up | talk | 64 | 384 | 0 | 0 | 0 | 0 |
| behaviour | all | 192 | 1152 | 914 | 0.793 | 0.767 | 0.819 |
| behaviour | independent | 64 | 384 | 290 | 0.755 | 0.706 | 0.797 |
| behaviour | non_verbal | 64 | 384 | 312 | 0.812 | 0.768 | 0.854 |
| behaviour | talk | 64 | 384 | 312 | 0.812 | 0.773 | 0.852 |

### The counterfactual pairs

| factor | component | subset | pairs | flips | rate | ci_low | ci_high | noise_rate | noise_high | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attractiveness_0_sees_1 | who_passed_first | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.628 | 0.658 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.560 | 0.617 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.685 | 0.729 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | talk | 2 | 0 | 0 | 0 | 0.658 | 0.638 | 0.688 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.628 | 0.658 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.560 | 0.617 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.685 | 0.729 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.638 | 0.688 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.628 | 0.658 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | independent | 2 | 2 | 1 | 0.342 | 1 | 0.560 | 0.617 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.685 | 0.729 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | talk | 2 | 0 | 0 | 0 | 0.658 | 0.638 | 0.688 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | all | 6 | 1 | 0.167 | 0.030 | 0.564 | 0.628 | 0.658 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | independent | 2 | 0 | 0 | 0 | 0.658 | 0.560 | 0.617 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.685 | 0.729 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.638 | 0.688 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.451 | 0.485 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.445 | 0.497 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.469 | 0.523 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.440 | 0.500 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.451 | 0.485 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | independent | 2 | 2 | 1 | 0.342 | 1 | 0.445 | 0.497 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.469 | 0.523 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.440 | 0.500 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.451 | 0.485 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | independent | 2 | 2 | 1 | 0.342 | 1 | 0.445 | 0.497 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.469 | 0.523 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.440 | 0.500 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | all | 6 | 1 | 0.167 | 0.030 | 0.564 | 0.451 | 0.485 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.445 | 0.497 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.469 | 0.523 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | talk | 2 | 0 | 0 | 0 | 0.658 | 0.440 | 0.500 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.031 | 0.049 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0.008 | 0.023 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.031 | 0.062 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.055 | 0.094 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.031 | 0.049 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0.008 | 0.023 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.031 | 0.062 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.055 | 0.094 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.031 | 0.049 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0.008 | 0.023 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.031 | 0.062 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.055 | 0.094 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.031 | 0.049 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0.008 | 0.023 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.031 | 0.062 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.055 | 0.094 | not distinguishable from the noise floor |
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
| attractiveness_0_sees_1 | behaviour | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.793 | 0.819 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | independent | 2 | 2 | 1 | 0.342 | 1 | 0.755 | 0.797 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.812 | 0.854 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.812 | 0.852 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | all | 6 | 6 | 1 | 0.610 | 1 | 0.793 | 0.819 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | independent | 2 | 2 | 1 | 0.342 | 1 | 0.755 | 0.797 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.812 | 0.854 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | talk | 2 | 2 | 1 | 0.342 | 1 | 0.812 | 0.852 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.793 | 0.819 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | independent | 2 | 2 | 1 | 0.342 | 1 | 0.755 | 0.797 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.812 | 0.854 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.812 | 0.852 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.793 | 0.819 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.755 | 0.797 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.812 | 0.854 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.812 | 0.852 | not distinguishable from the noise floor |

## 4. Behaviour stability

Per cell of the exact-repeat set: the share of its repeats with the commonest outcome (1: every repeat the same). A cell whose commonest behaviour came up in fewer than 0.75 of its repeats is a coin flip, and RF-11 should claim no rule there.

| Component | Cells | Mean | Lowest | Cells with every repeat the same |
| --- | --- | --- | --- | --- |
| who_passed_first | 192 | 0.611 | 0.250 | 12 |
| passing_side | 192 | 0.721 | 0.500 | 39 |
| stopped | 192 | 0.984 | 0.750 | 180 |
| backed_up | 192 | 1 | 1 | 192 |
| behaviour | 192 | 0.487 | 0.250 | 1 |

### Coin-flip cells: 158 of 192

| Cell | Condition | Repeats | Stability | Who passed first | Commonest behaviour |
| --- | --- | --- | --- | --- | --- |
| I_head_on_02dfbadb_02604456 | independent | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_0f57f8a5 | independent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_1caa9a84 | independent | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_231c8154 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_2ec958bb | independent | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_3cb16ae9 | independent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_3dee0df5 | independent | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_51dfba80 | independent | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_55c9ae40 | independent | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_68f09b97 | independent | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_74cb78c1 | independent | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_7eed7b59 | independent | 4 | 0.250 | 0.500 | p2\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_800a3b04 | independent | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_81bae7c3 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_9950986f | independent | 4 | 0.500 | 1 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_9b752a36 | independent | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_b1d97a31 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_b7fe7ead | independent | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_bcb9cb2c | independent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_cb859069 | independent | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_ce2a06ef | independent | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_dbd98c92 | independent | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_02604456 | independent | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_1caa9a84 | independent | 4 | 0.250 | 0.500 | p2\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_231c8154 | independent | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_2ec958bb | independent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_3dee0df5 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_55c9ae40 | independent | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_5767d932 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_68f09b97 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_6ab9c72e | independent | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_74cb78c1 | independent | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_7eed7b59 | independent | 4 | 0.250 | 0.500 | p2\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_800a3b04 | independent | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_81bae7c3 | independent | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_8ea28db3 | independent | 4 | 0.500 | 0.500 | p2\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_9950986f | independent | 4 | 0.500 | 1 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_9b752a36 | independent | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_b1d97a31 | independent | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_b59c2831 | independent | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_b6a40c60 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_b7fe7ead | independent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_bcb9cb2c | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_c36d5d49 | independent | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_cb859069 | independent | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_ce2a06ef | independent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_dbd98c92 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_e57e5fb0 | independent | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_f3d09c23 | independent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_f79677df | independent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_02604456 | non_verbal | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_1868bff4 | non_verbal | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_1caa9a84 | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_231c8154 | non_verbal | 4 | 0.250 | 0.250 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_2ec958bb | non_verbal | 4 | 0.250 | 0.500 | p2\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_3cb16ae9 | non_verbal | 4 | 0.250 | 0.250 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_3dee0df5 | non_verbal | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_51dfba80 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_55c9ae40 | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_5767d932 | non_verbal | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_68f09b97 | non_verbal | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_6ab9c72e | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_74cb78c1 | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_800a3b04 | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_8ea28db3 | non_verbal | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_9b752a36 | non_verbal | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_b1d97a31 | non_verbal | 4 | 0.250 | 0.250 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_b59c2831 | non_verbal | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_b6a40c60 | non_verbal | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_b7fe7ead | non_verbal | 4 | 0.250 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_bcb9cb2c | non_verbal | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_cb859069 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_dbd98c92 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_e57e5fb0 | non_verbal | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_f3d09c23 | non_verbal | 4 | 0.250 | 0.500 | p2\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_f79677df | non_verbal | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_02604456 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_0f57f8a5 | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_1868bff4 | non_verbal | 4 | 0.250 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_1caa9a84 | non_verbal | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_231c8154 | non_verbal | 4 | 0.250 | 0.500 | p2\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_2ec958bb | non_verbal | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_3dee0df5 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_51dfba80 | non_verbal | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_68f09b97 | non_verbal | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_6ab9c72e | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_74cb78c1 | non_verbal | 4 | 0.250 | 0.250 | p2\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_800a3b04 | non_verbal | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_81bae7c3 | non_verbal | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_8ea28db3 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_9950986f | non_verbal | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_9b752a36 | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_b1d97a31 | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_b59c2831 | non_verbal | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_b6a40c60 | non_verbal | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_b7fe7ead | non_verbal | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_bcb9cb2c | non_verbal | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_c36d5d49 | non_verbal | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_cb859069 | non_verbal | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_e57e5fb0 | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_f3d09c23 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_f79677df | non_verbal | 4 | 0.250 | 0.250 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_02604456 | talk | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_0f57f8a5 | talk | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_1868bff4 | talk | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_1caa9a84 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_231c8154 | talk | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_2ec958bb | talk | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_3cb16ae9 | talk | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_3dee0df5 | talk | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_51dfba80 | talk | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_5767d932 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_68f09b97 | talk | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_6ab9c72e | talk | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_74cb78c1 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_7eed7b59 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_81bae7c3 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_8ea28db3 | talk | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_9950986f | talk | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_9b752a36 | talk | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_b59c2831 | talk | 4 | 0.250 | 0.500 | p2\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_b7fe7ead | talk | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_bcb9cb2c | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_c36d5d49 | talk | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_cb859069 | talk | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_ce2a06ef | talk | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_dbd98c92 | talk | 4 | 0.500 | 1 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_e57e5fb0 | talk | 4 | 0.250 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_f3d09c23 | talk | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_f79677df | talk | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_0f57f8a5 | talk | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_1868bff4 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_1caa9a84 | talk | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_231c8154 | talk | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_2ec958bb | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_3cb16ae9 | talk | 4 | 0.250 | 0.250 | p2\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_3dee0df5 | talk | 4 | 0.500 | 1 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_51dfba80 | talk | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_55c9ae40 | talk | 4 | 0.250 | 0.250 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_5767d932 | talk | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_68f09b97 | talk | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_74cb78c1 | talk | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_7eed7b59 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_800a3b04 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_81bae7c3 | talk | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_8ea28db3 | talk | 4 | 0.250 | 0.250 | -\|left\|left\|1\|0\|0\|0 |
| T_head_on_de176842_9950986f | talk | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_9b752a36 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_b1d97a31 | talk | 4 | 0.250 | 0.250 | p2\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_b59c2831 | talk | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_b7fe7ead | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_bcb9cb2c | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_c36d5d49 | talk | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_cb859069 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_ce2a06ef | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_e57e5fb0 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_f3d09c23 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_f79677df | talk | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |

## 5. The factor-to-decision mapping

Every observed combination of `own_age_high`, `own_female`, `other_age_high`, `other_female`, `own_urgency`, `own_mobility_aid`, `own_load`, `own_distraction`, `own_assertiveness`, `own_residence`, `own_memory_note`, `other_mobility_aid`, `other_load`, `other_distraction`, `same_ethnicity`, `surroundings_busy`, `time_of_day_late_night`, `finds_other_attractive`, `knows_other`, `is_lower_agent`, `geometry`, per condition, from the agent's point of view: **402 combinations** in `mapping.csv`, each with its rows and, per outcome, how many are known and the share that are 1. Read the counts with the shares: a combination seen once gives 0 or 1 from one row. The 25 combinations with the most rows:

| condition | own_age_high | own_female | other_age_high | other_female | own_urgency | own_mobility_aid | own_load | own_distraction | own_assertiveness | own_residence | own_memory_note | other_mobility_aid | other_load | other_distraction | same_ethnicity | surroundings_busy | time_of_day_late_night | finds_other_attractive | knows_other | is_lower_agent | geometry | rows | p_passed_first | p_kept_left | p_stopped | p_backed_up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 8 | 0.143 | 0.500 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 8 | 0.167 | 0.625 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 8 | 0 | 0.625 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 8 | 0.143 | 0.750 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 8 | 0.250 | 0.625 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 8 | 0 | 0.500 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 7 | 0.167 | 0.571 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 7 | 0 | 0.571 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 7 | 0.143 | 0.571 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 7 | 0 | 0.429 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 7 | 0.250 | 0.571 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 7 | 0 | 0.714 | 0 | 0 |
| talk | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | layout=aligned | 4 | 0.250 | 0.750 | 0 | 0 |
| talk | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0.667 | 0.500 | 0 | 0 |
| talk | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0.500 | 1 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 0.750 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0 | 0.750 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 4 | - | 0.500 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0 | 1 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 1 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | layout=aligned | 4 | 0 | 0 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 4 | 0 | 0.250 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | layout=aligned | 4 | 0 | 0.250 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | layout=apart_20cm | 4 | 0 | 1 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | layout=aligned | 4 | 0.333 | 0 | 0 | 0 |

## 6. Stated against measured

How often each factor is named in the agents' private `reason` (keyword codebook `reasons_v1`), beside its strongest measured effect in the per-agent models of all conditions together. Named often: in at least 0.1 of the reasons. Measured: a term significant after Holm's correction. A factor named often with no measured effect, or the reverse, is a finding.

| Factor | Share of reasons naming it | Measured effect | Outcome | Term | Estimate (OR or coef.) | Holm p | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| age | 0.222 | yes | plan_slowed | other_age_high | 4.926 | < 0.001 | named often, and a measured effect |
| gender | 0.054 | no | passed_first | own_female | 0.986 | 1.000 | neither |
| urgency | 0.133 | yes | plan_slowed | own_urgency | 0.358 | < 0.001 | named often, and a measured effect |
| mobility_aid | 0.293 | yes | plan_slowed | other_mobility_aid | 4.425 | < 0.001 | named often, and a measured effect |
| load | 0.376 | yes | plan_slowed | other_load | 2.721 | < 0.001 | named often, and a measured effect |
| distraction | 0.261 | yes | start_distance_m | own_distraction | -1.564 | 0.027 | named often, and a measured effect |
| assertiveness | 0.228 | yes | plan_left | own_assertiveness | 0.245 | < 0.001 | named often, and a measured effect |
| residence | 0.000 | yes | plan_left | own_residence | 0.298 | < 0.001 | a measured effect, rarely named |
| memory_note | 0.143 | no | passed_first | own_memory_note | 0.894 | 1.000 | named often, no measured effect |
| surroundings | 0.081 | no | plan_left | surroundings_busy | 0.695 | 0.736 | neither |
| time_of_day | 0.025 | no | passed_first | time_of_day_late_night | 0.825 | 1.000 | neither |
| perceived_attractiveness | 0.020 | yes | signalled | finds_other_attractive | 2.852 | < 0.001 | a measured effect, rarely named |
| familiarity | 0.061 | yes | signalled | knows_other | 39.365 | < 0.001 | a measured effect, rarely named |
| ethnicity_pair | - | no | passed_first | same_ethnicity | 1.021 | 1.000 | neither |
| is_lower_agent | - | no | passed_first | is_lower_agent | 1.433 | 1.000 | neither |

**Where saying and doing disagree:** `residence` (a measured effect, rarely named), `memory_note` (named often, no measured effect), `perceived_attractiveness` (a measured effect, rarely named), `familiarity` (a measured effect, rarely named).

### The debriefs' kind of basis

One per prompted agent (D8); every source is unchecked until RF-14.

| kind | independent | non_verbal | talk | all |
| --- | --- | --- | --- | --- |
| local_custom | 12 | 13 | 15 | 40 |
| habit | 72 | 89 | 88 | 249 |
| common_sense | 415 | 431 | 427 | 1273 |
| none | 16 | 11 | 13 | 40 |
| (none given) | 29 | 0 | 1 | 30 |
| all | 544 | 544 | 544 | 1632 |

## 7. Intent against plan

Each readable intent coded by the keyword codebook `intent_v2` (keep to a side, slow down, stop and wait, back up, carry on, or `other`), against the plan coded from its steps. A mismatch is an intent that says something the plan does not do. Intents coded `other` and unreadable replies are left out of the rate. A high rate means the structured plan cannot be trusted on its own (RF-11).

| subset | decision_points | unreadable | uncoded | compared | mismatches | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 3987 | 112 | 516 | 3359 | 763 | 0.227 | 0.213 | 0.242 |
| independent | 544 | 29 | 61 | 454 | 133 | 0.293 | 0.253 | 0.336 |
| non_verbal | 1705 | 57 | 251 | 1397 | 271 | 0.194 | 0.174 | 0.216 |
| talk | 1738 | 26 | 204 | 1508 | 359 | 0.238 | 0.217 | 0.260 |

### Examples of mismatches

| condition | session_id | agent_id | intent | plan_categories | plan_side | why |
| --- | --- | --- | --- | --- | --- | --- |
| non_verbal | N_head_on_02dfbadb_b6a40c60_r2 | 0 | Hold my line toward the emergency room and keep my pace, glancing up from my phone to acknowledge the man ahead. | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_de176842_b7fe7ead_r4 | 0 | Keep walking at my pace toward the emergency room and hold my line | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_de176842_b7fe7ead_r4 | 0 | Acknowledge my classmate and keep my line toward the emergency room without slowing down | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_de176842_800a3b04_r2 | 0 | Let the woman pass on my right while I keep moving toward the emergency room | keep_to_side;slow_down | right | intent says left, the plan turns right |
| talk | T_head_on_02dfbadb_bcb9cb2c_r4 | 0 | Hold my line down the middle of the passage, stay alert and keep eye contact so he sees me and my suitcase and doesn't walk into me. | keep_to_side;slow_down | left | intent says carry_on, the plan does not |
| talk | T_head_on_02dfbadb_bcb9cb2c_r4 | 1 | Keep well to my right and slow down to let the woman with the cane and suitcase pass comfortably | slow_down | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| talk | T_head_on_02dfbadb_bcb9cb2c_r4 | 0 | Hold my line with a little room on my right so he passes on my left and we don't collide | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| talk | T_head_on_02dfbadb_800a3b04_r4 | 1 | Keep walking to the supermarket and give the elderly man with the suitcase room to pass | keep_to_side;slow_down | left | intent says carry_on, the plan does not |
| talk | T_head_on_02dfbadb_b6a40c60_r4 | 0 | Keep walking at my pace toward the emergency room, using my cane and glancing up from my phone when needed. | keep_to_side | left | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_1868bff4_r3 | 1 | Hold my line and pace to the emergency room, but make eye contact so she knows I'm coming and doesn't walk into me | keep_to_side | right | intent says carry_on, the plan does not |
| independent | I_head_on_de176842_9b752a36_r3 | 1 | Get to the emergency room as quickly as I can without slowing down for the young man ahead. | keep_to_side | right | intent says carry_on, the plan does not |
| independent | I_head_on_02dfbadb_81bae7c3_r3 | 0 | Keep walking toward the supermarket, giving way a little to Person 1 since the passage is narrow. | keep_to_side;slow_down | right | intent says carry_on, the plan does not |
| independent | I_head_on_02dfbadb_3dee0df5_r2 | 1 | Keep walking to the supermarket in my lane, holding my line so Person 1 passes me cleanly on the side with more room. | keep_to_side;slow_down | right | intent says carry_on, the plan does not |
| independent | I_head_on_de176842_800a3b04_r4 | 1 | Keep walking to the supermarket, giving the elderly man with the suitcase plenty of room to pass. | keep_to_side | right | intent says carry_on, the plan does not |
| independent | I_head_on_de176842_68f09b97_r2 | 0 | Keep walking straight to the supermarket; I have my suitcase and cane and won't be dodging about in this narrow passage. | keep_to_side;slow_down | right | intent says carry_on, the plan does not |

### Intents the codebook could not place (the commonest)

- 4 x "Give the elderly man with the cane and suitcase plenty of room to pass"
- 3 x "Give the elderly woman with the suitcase plenty of room to pass"
- 2 x "Acknowledge my classmate and keep moving toward the emergency room"
- 2 x "Give the older woman with the suitcase plenty of room and pass her politely"
- 2 x "Acknowledge my classmate as we pass while keeping my line and pace with the suitcase"

## 8. Real ethnicity

Descriptive. A difference between groups here is the model's behaviour towards people it was told are of a group, not a fact about those groups, and no rule may read ethnicity (`llm_negotiation/docs/ethnicity.md`).

### By group, the other's as told (unweighted agent rows)

| own | other_as_told | n | passed_first | kept_left | stopped | backed_up | plan_slowed | plan_left | plan_right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chinese | chinese | 234 | 0.200 | 0.470 | 0.009 | 0 | 0.618 | 0.360 | 0.588 |
| chinese | malay | 69 | 0.200 | 0.609 | 0 | 0 | 0.582 | 0.522 | 0.403 |
| chinese | indian | 84 | 0.136 | 0.595 | 0 | 0 | 0.687 | 0.530 | 0.434 |
| chinese | others | 60 | 0.289 | 0.542 | 0.017 | 0 | 0.695 | 0.559 | 0.407 |
| malay | chinese | 69 | 0.111 | 0.609 | 0.014 | 0 | 0.642 | 0.522 | 0.478 |
| malay | malay | 198 | 0.157 | 0.687 | 0.010 | 0 | 0.592 | 0.607 | 0.342 |
| malay | indian | 63 | 0.053 | 0.587 | 0.016 | 0 | 0.587 | 0.444 | 0.524 |
| malay | others | 72 | 0.220 | 0.542 | 0.014 | 0 | 0.507 | 0.507 | 0.352 |
| indian | chinese | 84 | 0.205 | 0.595 | 0.012 | 0 | 0.614 | 0.494 | 0.422 |
| indian | malay | 63 | 0.158 | 0.587 | 0 | 0 | 0.823 | 0.581 | 0.419 |
| indian | indian | 192 | 0.237 | 0.427 | 0.005 | 0 | 0.721 | 0.374 | 0.579 |
| indian | others | 60 | 0.342 | 0.617 | 0 | 0 | 0.517 | 0.328 | 0.621 |
| others | chinese | 60 | 0.237 | 0.542 | 0.017 | 0 | 0.650 | 0.367 | 0.533 |
| others | malay | 72 | 0.268 | 0.542 | 0 | 0 | 0.643 | 0.329 | 0.586 |
| others | indian | 60 | 0.105 | 0.617 | 0.017 | 0 | 0.638 | 0.517 | 0.431 |
| others | others | 192 | 0.197 | 0.562 | 0.005 | 0 | 0.535 | 0.412 | 0.513 |

Each share is over the rows where the outcome is defined (`<outcome>_n` in `ethnicity_groups.csv`).

### Weighted back to random resident pairs

Each session weighted by `ethnicity_weight`, so that the sessions stand for two residents met at random (each at the resident shares; residents only). Use the weighted rate for a population-level figure; the effective number of sessions is what the weighting leaves.

| outcome | sessions | unweighted | weighted | effective_sessions |
| --- | --- | --- | --- | --- |
| resolved_plan_only | 816 | 0.525 | 0.480 | 288.580 |
| resolved_plan_orca | 816 | 0.553 | 0.516 | 288.580 |
| resolved_by_llm | 816 | 0.525 | 0.480 | 288.580 |

## How to read this report

- **An effect here is an effect on what the LLM agents did**, in this design: a screen, so main effects are estimated clear of two-factor interactions only when the design is a resolution IV fraction (`llm_negotiation/docs/screening-designs.md`, section 3).
- **Separation** (an outcome predicted perfectly by some predictor) leaves a model with no finite estimate; it is listed, not reported as an effect. Rare outcomes with many factors cause it: D14 aims at about 10 events per factor.
- **The mapping is sparse** when there are many factors: most combinations are seen once or twice.
- **The codebooks are drafts** until RF-9's pilot (`analysis/codebooks/`): a mention or a coded intent is a keyword match, not a reading of the text.
