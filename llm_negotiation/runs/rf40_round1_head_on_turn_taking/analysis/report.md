# Factor analysis of a resolution experiment (RF-8)

## Inputs

- `llm_negotiation/runs/rf40_round1_head_on_turn_taking/outcomes.csv`

- Sessions analysed (completed): **816** (non_verbal: 272, silent: 272, talk: 272); left out: none.
- Rows, one per agent per session: **1632**.
- Physical outcomes of mode **`plan_only`** (the Step 1 measure).
- Client: deepseek.
- Predictors that vary: `own_age_high`, `own_female`, `other_age_high`, `other_female`, `own_urgency`, `own_mobility_aid`, `own_load`, `own_distraction`, `own_assertiveness`, `own_residence`, `own_memory_note`, `other_mobility_aid`, `other_load`, `other_distraction`, `same_ethnicity`, `surroundings_busy`, `time_of_day_late_night`, `finds_other_attractive`, `knows_other`, `is_lower_agent`, `asked_first`; constant, left out: `own_demographics_hidden`, `other_demographics_unseen`, `ethnicity_unseen`, `pairwise_unseen`.
- Holm's correction at alpha = 0.05, over every term of every model in this report (the chance of any false positive in it is at most alpha); seed 63; codebooks `intent_v2` and `reasons_v1`.

**The other's factors are as the agent was told them.** A factor of the other person counts only if it was printed to the agent at one or more of its decision points (`analysis/load.py`).

## 1. Factor effects

Logistic regression per binary outcome (odds ratios, OR, with 95% intervals), linear regression for a continuous one (coefficients). Per-agent models cluster standard errors by session; per-session models use HC1. Holm's correction runs over every term of every model in this report (the chance of any false positive in it is at most alpha). `all` is every condition together, with condition as a factor. A model whose outcome is separated by the predictors has no finite estimate and is listed as `separation`, never read as an effect.

### Significant after Holm's correction

| Outcome | Subset | Term | Effect [95% CI] | p | Holm p | n |
| --- | --- | --- | --- | --- | --- | --- |
| passed_first | all | own_assertiveness | OR 8.40 [5.48, 12.86] | < 0.001 | < 0.001 | 1092 |
| passed_first | non_verbal | own_assertiveness | OR 7.00 [3.22, 15.21] | < 0.001 | < 0.001 | 356 |
| passed_first | silent | own_assertiveness | OR 8.82 [4.32, 18.04] | < 0.001 | < 0.001 | 388 |
| passed_first | talk | own_assertiveness | OR 13.88 [5.32, 36.20] | < 0.001 | < 0.001 | 348 |
| plan_left | all | own_assertiveness | OR 0.35 [0.25, 0.50] | < 0.001 | < 0.001 | 1631 |
| plan_left | all | own_residence | OR 0.35 [0.25, 0.50] | < 0.001 | < 0.001 | 1631 |
| plan_left | all | own_age_high | OR 2.08 [1.50, 2.90] | < 0.001 | 0.011 | 1631 |
| plan_left | non_verbal | own_residence | OR 0.23 [0.12, 0.45] | < 0.001 | 0.010 | 544 |
| plan_left | talk | own_age_high | OR 3.33 [1.93, 5.76] | < 0.001 | 0.013 | 543 |
| plan_right | all | own_residence | OR 2.25 [1.65, 3.06] | < 0.001 | < 0.001 | 1631 |
| plan_right | all | own_age_high | OR 0.52 [0.39, 0.71] | < 0.001 | 0.019 | 1631 |
| plan_right | non_verbal | own_residence | OR 3.19 [1.84, 5.55] | < 0.001 | 0.031 | 544 |
| plan_right | talk | own_age_high | OR 0.31 [0.18, 0.54] | < 0.001 | 0.019 | 543 |
| plan_slowed | all | knows_other | OR 2.73 [2.11, 3.53] | < 0.001 | < 0.001 | 1631 |
| plan_slowed | all | other_mobility_aid | OR 4.72 [3.10, 7.17] | < 0.001 | < 0.001 | 1631 |
| plan_slowed | all | other_age_high | OR 4.30 [2.86, 6.47] | < 0.001 | < 0.001 | 1631 |
| plan_slowed | all | own_assertiveness | OR 0.33 [0.24, 0.46] | < 0.001 | < 0.001 | 1631 |
| plan_slowed | all | own_mobility_aid | OR 2.87 [2.07, 3.99] | < 0.001 | < 0.001 | 1631 |
| plan_slowed | all | own_urgency | OR 0.35 [0.25, 0.49] | < 0.001 | < 0.001 | 1631 |
| plan_slowed | all | other_load | OR 2.89 [1.96, 4.26] | < 0.001 | < 0.001 | 1631 |
| plan_slowed | all | finds_other_attractive | OR 1.84 [1.43, 2.36] | < 0.001 | 0.002 | 1631 |
| plan_slowed | all | condition[silent] | OR 0.51 [0.38, 0.69] | < 0.001 | 0.009 | 1631 |
| plan_slowed | non_verbal | own_mobility_aid | OR 6.64 [2.92, 15.11] | < 0.001 | 0.005 | 544 |
| plan_slowed | non_verbal | own_assertiveness | OR 0.15 [0.06, 0.34] | < 0.001 | 0.006 | 544 |
| plan_slowed | non_verbal | other_mobility_aid | OR 12.02 [4.03, 35.84] | < 0.001 | 0.007 | 544 |
| plan_slowed | silent | knows_other | OR 3.03 [1.97, 4.67] | < 0.001 | < 0.001 | 544 |
| plan_slowed | silent | other_mobility_aid | OR 5.27 [2.71, 10.25] | < 0.001 | < 0.001 | 544 |
| plan_slowed | silent | other_age_high | OR 3.93 [2.13, 7.25] | < 0.001 | 0.009 | 544 |
| plan_slowed | talk | knows_other | OR 3.08 [1.96, 4.85] | < 0.001 | < 0.001 | 543 |
| signalled | all | own_assertiveness | OR 9.46 [4.90, 18.27] | < 0.001 | < 0.001 | 1088 |
| signalled | all | knows_other | OR 164.49 [35.06, 771.68] | < 0.001 | < 0.001 | 1088 |
| signalled | non_verbal | own_assertiveness | OR 9.74 [4.19, 22.63] | < 0.001 | < 0.001 | 544 |
| signalled | non_verbal | knows_other | OR 158.09 [18.67, 1338.37] | < 0.001 | 0.003 | 544 |
| signalled | talk | knows_other | OR 219.44 [37.35, 1289.18] | < 0.001 | < 0.001 | 544 |
| signalled | talk | own_assertiveness | OR 9.89 [3.31, 29.57] | < 0.001 | 0.032 | 544 |
| decision_points | silent | geometry[layout=apart_20cm] | +1.301 [+0.698, +1.905] | < 0.001 | 0.019 | 272 |

### Every model

| outcome | level | subset | status | n | events | clusters | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| passed_first | agent | all | ok | 1092 | 251 | 546 |  |
| kept_left | agent | all | ok | 1632 | 686 | 816 |  |
| stopped | agent | all | separation | 1632 | 21 | 816 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | all | one value | 1632 | 0 | - | every row is 0 |
| plan_left | agent | all | ok | 1631 | 569 | 816 |  |
| plan_right | agent | all | ok | 1631 | 964 | 816 |  |
| plan_slowed | agent | all | ok | 1631 | 1007 | 816 |  |
| plan_stopped | agent | all | separation | 1631 | 3 | 816 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | all | one value | 1631 | 0 | - | every row is 0 |
| start_distance_m | agent | all | ok | 60 | - | 58 |  |
| signalled | agent | all | ok | 1088 | 836 | 544 |  |
| resolved_plan_only | session | all | ok | 816 | 482 | - |  |
| resolved_plan_orca | session | all | ok | 816 | 511 | - |  |
| resolved_by_llm | session | all | ok | 816 | 482 | - |  |
| decision_points | session | all | ok | 816 | - | - |  |
| passed_first | agent | non_verbal | ok | 356 | 85 | 178 |  |
| kept_left | agent | non_verbal | ok | 544 | 236 | 272 |  |
| stopped | agent | non_verbal | separation | 544 | 17 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | non_verbal | one value | 544 | 0 | - | every row is 0 |
| plan_left | agent | non_verbal | ok | 544 | 186 | 272 |  |
| plan_right | agent | non_verbal | ok | 544 | 329 | 272 |  |
| plan_slowed | agent | non_verbal | ok | 544 | 364 | 272 |  |
| plan_stopped | agent | non_verbal | one value | 544 | 0 | - | every row is 0 |
| plan_backed_up | agent | non_verbal | one value | 544 | 0 | - | every row is 0 |
| start_distance_m | agent | non_verbal | ok | 28 | - | 28 |  |
| signalled | agent | non_verbal | ok | 544 | 403 | 272 |  |
| resolved_plan_only | session | non_verbal | ok | 272 | 148 | - |  |
| resolved_plan_orca | session | non_verbal | ok | 272 | 164 | - |  |
| resolved_by_llm | session | non_verbal | ok | 272 | 148 | - |  |
| decision_points | session | non_verbal | ok | 272 | - | - |  |
| passed_first | agent | talk | ok | 348 | 76 | 174 |  |
| kept_left | agent | talk | ok | 544 | 286 | 272 |  |
| stopped | agent | talk | separation | 544 | 2 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | talk | one value | 544 | 0 | - | every row is 0 |
| plan_left | agent | talk | ok | 543 | 238 | 272 |  |
| plan_right | agent | talk | ok | 543 | 283 | 272 |  |
| plan_slowed | agent | talk | ok | 543 | 336 | 272 |  |
| plan_stopped | agent | talk | separation | 543 | 1 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | talk | one value | 543 | 0 | - | every row is 0 |
| start_distance_m | agent | talk | ok | 26 | - | 24 |  |
| signalled | agent | talk | ok | 544 | 433 | 272 |  |
| resolved_plan_only | session | talk | ok | 272 | 159 | - |  |
| resolved_plan_orca | session | talk | ok | 272 | 161 | - |  |
| resolved_by_llm | session | talk | ok | 272 | 159 | - |  |
| decision_points | session | talk | ok | 272 | - | - |  |
| passed_first | agent | silent | ok | 388 | 90 | 194 |  |
| kept_left | agent | silent | ok | 544 | 164 | 272 |  |
| stopped | agent | silent | separation | 544 | 2 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | silent | one value | 544 | 0 | - | every row is 0 |
| plan_left | agent | silent | ok | 544 | 145 | 272 |  |
| plan_right | agent | silent | ok | 544 | 352 | 272 |  |
| plan_slowed | agent | silent | ok | 544 | 307 | 272 |  |
| plan_stopped | agent | silent | separation | 544 | 2 | 272 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | silent | one value | 544 | 0 | - | every row is 0 |
| start_distance_m | agent | silent | no data | 6 | - | - | 6 rows for 6 parameters |
| signalled | agent | silent | no data | 0 | - | - |  |
| resolved_plan_only | session | silent | ok | 272 | 175 | - |  |
| resolved_plan_orca | session | silent | ok | 272 | 186 | - |  |
| resolved_by_llm | session | silent | ok | 272 | 175 | - |  |
| decision_points | session | silent | ok | 272 | - | - |  |

### Each outcome, all conditions together

Per outcome: what it is, and every term of the pooled model (the per-condition terms are in `effects_terms.csv`).

**`passed_first`** (agent): left the conflict zone first (physical; `together` counts as not first). Status: ok, n = 1092, events = 251.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.03 [0.68, 1.58] | 0.876 | 1.000 |
| own_female | OR 1.42 [0.98, 2.06] | 0.063 | 1.000 |
| other_age_high | OR 0.78 [0.45, 1.37] | 0.390 | 1.000 |
| own_urgency | OR 1.47 [0.98, 2.22] | 0.065 | 1.000 |
| own_mobility_aid | OR 1.66 [1.12, 2.48] | 0.012 | 1.000 |
| own_load | OR 1.54 [1.03, 2.30] | 0.036 | 1.000 |
| own_distraction | OR 1.51 [1.00, 2.26] | 0.047 | 1.000 |
| own_assertiveness | OR 8.40 [5.48, 12.86] | < 0.001 | < 0.001 |
| own_residence | OR 0.67 [0.45, 1.02] | 0.060 | 1.000 |
| own_memory_note | OR 0.68 [0.44, 1.05] | 0.079 | 1.000 |
| other_mobility_aid | OR 1.05 [0.61, 1.83] | 0.851 | 1.000 |
| other_load | OR 1.41 [0.83, 2.42] | 0.206 | 1.000 |
| other_distraction | OR 0.73 [0.41, 1.29] | 0.276 | 1.000 |
| same_ethnicity | OR 0.91 [0.66, 1.24] | 0.539 | 1.000 |
| surroundings_busy | OR 0.82 [0.60, 1.13] | 0.230 | 1.000 |
| time_of_day_late_night | OR 0.94 [0.68, 1.29] | 0.684 | 1.000 |
| finds_other_attractive | OR 0.85 [0.60, 1.21] | 0.371 | 1.000 |
| knows_other | OR 1.15 [0.84, 1.57] | 0.397 | 1.000 |
| is_lower_agent | OR 1.25 [0.87, 1.80] | 0.226 | 1.000 |
| asked_first | OR 1.20 [0.83, 1.72] | 0.335 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.17 [0.86, 1.58] | 0.319 | 1.000 |
| condition[silent] | OR 1.08 [0.75, 1.57] | 0.674 | 1.000 |
| condition[talk] | OR 0.83 [0.57, 1.22] | 0.345 | 1.000 |

Left out of the model: other_female (collinear).

**`kept_left`** (agent): kept to its own left at the closest approach (physical; rows where the two were not abreast are left out). Status: ok, n = 1632, events = 686.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.83 [0.62, 1.12] | 0.235 | 1.000 |
| own_female | OR 1.00 [0.99, 1.01] | 0.918 | 1.000 |
| other_age_high | OR 0.80 [0.60, 1.08] | 0.142 | 1.000 |
| own_urgency | OR 0.89 [0.67, 1.18] | 0.433 | 1.000 |
| own_mobility_aid | OR 1.33 [0.99, 1.79] | 0.060 | 1.000 |
| own_load | OR 1.42 [1.06, 1.92] | 0.020 | 1.000 |
| own_distraction | OR 0.78 [0.58, 1.05] | 0.107 | 1.000 |
| own_assertiveness | OR 1.06 [0.80, 1.40] | 0.706 | 1.000 |
| own_residence | OR 0.90 [0.68, 1.19] | 0.460 | 1.000 |
| own_memory_note | OR 0.95 [0.71, 1.25] | 0.697 | 1.000 |
| other_mobility_aid | OR 1.27 [0.94, 1.71] | 0.114 | 1.000 |
| other_load | OR 1.36 [1.01, 1.83] | 0.042 | 1.000 |
| other_distraction | OR 0.75 [0.56, 1.01] | 0.057 | 1.000 |
| same_ethnicity | OR 0.94 [0.71, 1.26] | 0.699 | 1.000 |
| surroundings_busy | OR 0.80 [0.60, 1.07] | 0.136 | 1.000 |
| time_of_day_late_night | OR 0.80 [0.60, 1.08] | 0.143 | 1.000 |
| finds_other_attractive | OR 1.12 [0.90, 1.38] | 0.317 | 1.000 |
| knows_other | OR 0.71 [0.53, 0.96] | 0.024 | 1.000 |
| is_lower_agent | OR 1.00 [0.99, 1.01] | 0.986 | 1.000 |
| asked_first | OR 1.00 [0.99, 1.01] | 0.856 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.46 [1.09, 1.95] | 0.011 | 1.000 |
| condition[silent] | OR 0.55 [0.38, 0.79] | 0.001 | 0.961 |
| condition[talk] | OR 1.47 [1.04, 2.08] | 0.030 | 1.000 |

Left out of the model: other_female (collinear).

**`stopped`** (agent): its speed fell below the deadlock monitor's threshold (physical). Status: separation, n = 1632, events = 21.

Left out of the model: other_female (collinear).

**`backed_up`** (agent): moved against its path (physical). Status: one value, n = 1632, events = 0.

**`plan_left`** (agent): its first plan turns to its left only. Status: ok, n = 1631, events = 569.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 2.08 [1.50, 2.90] | < 0.001 | 0.011 |
| own_female | OR 1.37 [1.10, 1.71] | 0.004 | 1.000 |
| other_age_high | OR 0.70 [0.53, 0.93] | 0.015 | 1.000 |
| own_urgency | OR 0.55 [0.39, 0.76] | < 0.001 | 0.303 |
| own_mobility_aid | OR 1.43 [1.03, 1.99] | 0.032 | 1.000 |
| own_load | OR 1.08 [0.77, 1.50] | 0.666 | 1.000 |
| own_distraction | OR 1.32 [0.95, 1.84] | 0.102 | 1.000 |
| own_assertiveness | OR 0.35 [0.25, 0.50] | < 0.001 | < 0.001 |
| own_residence | OR 0.35 [0.25, 0.50] | < 0.001 | < 0.001 |
| own_memory_note | OR 1.07 [0.77, 1.49] | 0.681 | 1.000 |
| other_mobility_aid | OR 1.41 [1.06, 1.87] | 0.017 | 1.000 |
| other_load | OR 1.37 [1.04, 1.82] | 0.026 | 1.000 |
| other_distraction | OR 0.83 [0.62, 1.10] | 0.190 | 1.000 |
| same_ethnicity | OR 0.88 [0.71, 1.09] | 0.247 | 1.000 |
| surroundings_busy | OR 0.92 [0.74, 1.15] | 0.469 | 1.000 |
| time_of_day_late_night | OR 1.03 [0.83, 1.27] | 0.815 | 1.000 |
| finds_other_attractive | OR 0.95 [0.77, 1.19] | 0.670 | 1.000 |
| knows_other | OR 0.73 [0.59, 0.91] | 0.006 | 1.000 |
| is_lower_agent | OR 0.99 [0.79, 1.23] | 0.921 | 1.000 |
| asked_first | OR 0.91 [0.73, 1.13] | 0.388 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.32 [1.06, 1.64] | 0.013 | 1.000 |
| condition[silent] | OR 0.68 [0.52, 0.89] | 0.004 | 1.000 |
| condition[talk] | OR 1.57 [1.21, 2.04] | < 0.001 | 0.568 |

Left out of the model: other_female (collinear).

**`plan_right`** (agent): its first plan turns to its right only. Status: ok, n = 1631, events = 964.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.52 [0.39, 0.71] | < 0.001 | 0.019 |
| own_female | OR 0.78 [0.64, 0.96] | 0.017 | 1.000 |
| other_age_high | OR 1.47 [1.11, 1.93] | 0.007 | 1.000 |
| own_urgency | OR 1.72 [1.27, 2.32] | < 0.001 | 0.356 |
| own_mobility_aid | OR 0.82 [0.61, 1.11] | 0.200 | 1.000 |
| own_load | OR 0.82 [0.61, 1.10] | 0.189 | 1.000 |
| own_distraction | OR 0.79 [0.59, 1.08] | 0.138 | 1.000 |
| own_assertiveness | OR 1.23 [0.91, 1.67] | 0.186 | 1.000 |
| own_residence | OR 2.25 [1.65, 3.06] | < 0.001 | < 0.001 |
| own_memory_note | OR 1.16 [0.86, 1.56] | 0.321 | 1.000 |
| other_mobility_aid | OR 0.80 [0.61, 1.06] | 0.121 | 1.000 |
| other_load | OR 0.75 [0.57, 0.99] | 0.044 | 1.000 |
| other_distraction | OR 1.15 [0.87, 1.51] | 0.327 | 1.000 |
| same_ethnicity | OR 1.16 [0.94, 1.44] | 0.159 | 1.000 |
| surroundings_busy | OR 1.01 [0.81, 1.25] | 0.950 | 1.000 |
| time_of_day_late_night | OR 1.03 [0.84, 1.27] | 0.767 | 1.000 |
| finds_other_attractive | OR 1.11 [0.91, 1.36] | 0.302 | 1.000 |
| knows_other | OR 1.34 [1.08, 1.66] | 0.008 | 1.000 |
| is_lower_agent | OR 1.03 [0.84, 1.26] | 0.795 | 1.000 |
| asked_first | OR 1.12 [0.91, 1.37] | 0.271 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.83 [0.68, 1.03] | 0.090 | 1.000 |
| condition[silent] | OR 1.21 [0.93, 1.57] | 0.148 | 1.000 |
| condition[talk] | OR 0.70 [0.54, 0.90] | 0.006 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_slowed`** (agent): its first plan slows below its speed at the decision. Status: ok, n = 1631, events = 1007.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.41 [1.01, 1.96] | 0.043 | 1.000 |
| own_female | OR 0.77 [0.60, 1.00] | 0.047 | 1.000 |
| other_age_high | OR 4.30 [2.86, 6.47] | < 0.001 | < 0.001 |
| own_urgency | OR 0.35 [0.25, 0.49] | < 0.001 | < 0.001 |
| own_mobility_aid | OR 2.87 [2.07, 3.99] | < 0.001 | < 0.001 |
| own_load | OR 1.72 [1.23, 2.40] | 0.001 | 1.000 |
| own_distraction | OR 1.01 [0.72, 1.40] | 0.971 | 1.000 |
| own_assertiveness | OR 0.33 [0.24, 0.46] | < 0.001 | < 0.001 |
| own_residence | OR 1.10 [0.79, 1.53] | 0.573 | 1.000 |
| own_memory_note | OR 1.53 [1.11, 2.11] | 0.010 | 1.000 |
| other_mobility_aid | OR 4.72 [3.10, 7.17] | < 0.001 | < 0.001 |
| other_load | OR 2.89 [1.96, 4.26] | < 0.001 | < 0.001 |
| other_distraction | OR 1.20 [0.82, 1.73] | 0.346 | 1.000 |
| same_ethnicity | OR 0.79 [0.62, 1.02] | 0.073 | 1.000 |
| surroundings_busy | OR 1.04 [0.81, 1.33] | 0.785 | 1.000 |
| time_of_day_late_night | OR 1.12 [0.87, 1.44] | 0.395 | 1.000 |
| finds_other_attractive | OR 1.84 [1.43, 2.36] | < 0.001 | 0.002 |
| knows_other | OR 2.73 [2.11, 3.53] | < 0.001 | < 0.001 |
| is_lower_agent | OR 0.94 [0.73, 1.21] | 0.620 | 1.000 |
| asked_first | OR 1.15 [0.89, 1.47] | 0.280 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.82 [0.64, 1.06] | 0.127 | 1.000 |
| condition[silent] | OR 0.51 [0.38, 0.69] | < 0.001 | 0.009 |
| condition[talk] | OR 0.72 [0.53, 0.97] | 0.032 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_stopped`** (agent): its first plan stops. Status: separation, n = 1631, events = 3.

Left out of the model: other_female (collinear).

**`plan_backed_up`** (agent): its first plan backs up. Status: one value, n = 1631, events = 0.

**`start_distance_m`** (agent): its first plan starts at this distance (plans that start so). Status: ok, n = 60.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | +0.417 [-0.983, +1.817] | 0.560 | 1.000 |
| own_female | +0.207 [-0.727, +1.141] | 0.664 | 1.000 |
| other_age_high | -0.717 [-1.486, +0.052] | 0.068 | 1.000 |
| own_urgency | -0.052 [-1.098, +0.995] | 0.923 | 1.000 |
| own_mobility_aid | -0.248 [-0.952, +0.456] | 0.490 | 1.000 |
| own_load | +1.103 [-0.402, +2.608] | 0.151 | 1.000 |
| own_distraction | -1.248 [-2.675, +0.180] | 0.087 | 1.000 |
| own_assertiveness | +0.454 [-1.009, +1.918] | 0.543 | 1.000 |
| own_memory_note | +0.329 [-1.026, +1.685] | 0.634 | 1.000 |
| other_mobility_aid | +0.522 [+0.009, +1.036] | 0.046 | 1.000 |
| other_load | +0.452 [-0.168, +1.073] | 0.153 | 1.000 |
| other_distraction | +0.297 [-0.559, +1.153] | 0.497 | 1.000 |
| same_ethnicity | -0.140 [-0.768, +0.487] | 0.661 | 1.000 |
| surroundings_busy | +0.239 [-0.608, +1.086] | 0.580 | 1.000 |
| time_of_day_late_night | -0.676 [-1.373, +0.020] | 0.057 | 1.000 |
| finds_other_attractive | +0.837 [-0.003, +1.676] | 0.051 | 1.000 |
| knows_other | +0.387 [-0.835, +1.609] | 0.535 | 1.000 |
| is_lower_agent | +0.001 [-0.570, +0.572] | 0.998 | 1.000 |
| asked_first | +0.046 [-0.468, +0.561] | 0.860 | 1.000 |
| geometry[layout=apart_20cm] | +0.250 [-0.164, +0.664] | 0.237 | 1.000 |
| condition[silent] | -0.430 [-1.100, +0.239] | 0.208 | 1.000 |
| condition[talk] | -0.021 [-0.570, +0.528] | 0.940 | 1.000 |

Left out of the model: other_female (collinear); own_residence (collinear).

**`signalled`** (agent): it signalled at least once (non-verbal and talk only). Status: ok, n = 1088, events = 836.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.05 [0.58, 1.92] | 0.868 | 1.000 |
| own_female | OR 0.98 [0.78, 1.23] | 0.869 | 1.000 |
| other_age_high | OR 1.49 [0.89, 2.47] | 0.126 | 1.000 |
| own_urgency | OR 0.55 [0.28, 1.11] | 0.095 | 1.000 |
| own_mobility_aid | OR 1.59 [0.86, 2.94] | 0.139 | 1.000 |
| own_load | OR 1.29 [0.66, 2.52] | 0.456 | 1.000 |
| own_distraction | OR 0.81 [0.40, 1.63] | 0.553 | 1.000 |
| own_assertiveness | OR 9.46 [4.90, 18.27] | < 0.001 | < 0.001 |
| own_residence | OR 1.27 [0.65, 2.49] | 0.492 | 1.000 |
| own_memory_note | OR 1.61 [0.90, 2.89] | 0.106 | 1.000 |
| other_mobility_aid | OR 2.23 [1.35, 3.69] | 0.002 | 1.000 |
| other_load | OR 1.32 [0.78, 2.22] | 0.296 | 1.000 |
| other_distraction | OR 1.15 [0.69, 1.92] | 0.583 | 1.000 |
| same_ethnicity | OR 0.79 [0.49, 1.28] | 0.336 | 1.000 |
| surroundings_busy | OR 1.15 [0.69, 1.90] | 0.592 | 1.000 |
| time_of_day_late_night | OR 0.94 [0.57, 1.56] | 0.819 | 1.000 |
| finds_other_attractive | OR 2.02 [1.34, 3.05] | < 0.001 | 0.629 |
| knows_other | OR 164.49 [35.06, 771.68] | < 0.001 | < 0.001 |
| is_lower_agent | OR 1.20 [0.94, 1.54] | 0.146 | 1.000 |
| asked_first | OR 0.85 [0.68, 1.06] | 0.143 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.90 [0.56, 1.45] | 0.672 | 1.000 |
| condition[talk] | OR 1.67 [1.03, 2.68] | 0.036 | 1.000 |

Left out of the model: other_female (collinear).

**`resolved_plan_only`** (session): resolved in `plan_only` (the Step 1 measure). Status: ok, n = 816, events = 482.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.86 [0.64, 1.15] | 0.316 | 1.000 |
| gender_pair[p1_male] | OR 1.05 [0.79, 1.41] | 0.737 | 1.000 |
| urgency[p1] | OR 1.58 [1.18, 2.11] | 0.002 | 1.000 |
| mobility_aid[p1] | OR 0.96 [0.71, 1.28] | 0.763 | 1.000 |
| load[p1] | OR 0.85 [0.64, 1.14] | 0.291 | 1.000 |
| distraction[p1] | OR 1.41 [1.06, 1.89] | 0.020 | 1.000 |
| assertiveness[p1] | OR 0.86 [0.64, 1.14] | 0.293 | 1.000 |
| residence[p1] | OR 0.88 [0.65, 1.17] | 0.372 | 1.000 |
| memory_note[p1] | OR 1.17 [0.88, 1.57] | 0.285 | 1.000 |
| ethnicity_pair[different] | OR 0.85 [0.64, 1.13] | 0.253 | 1.000 |
| surroundings[busy] | OR 0.88 [0.66, 1.18] | 0.395 | 1.000 |
| time_of_day[late_night] | OR 0.70 [0.53, 0.94] | 0.019 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 0.90 [0.68, 1.21] | 0.487 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 0.97 [0.73, 1.30] | 0.852 | 1.000 |
| familiarity[strangers] | OR 0.81 [0.60, 1.08] | 0.151 | 1.000 |
| mapping[p1_higher] | OR 1.16 [0.87, 1.55] | 0.319 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.73 [0.55, 0.97] | 0.029 | 1.000 |
| condition[silent] | OR 1.54 [1.08, 2.19] | 0.016 | 1.000 |
| condition[talk] | OR 1.19 [0.84, 1.68] | 0.334 | 1.000 |

**`resolved_plan_orca`** (session): resolved in `plan_orca`. Status: ok, n = 816, events = 511.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.84 [0.62, 1.12] | 0.234 | 1.000 |
| gender_pair[p1_male] | OR 0.98 [0.73, 1.32] | 0.903 | 1.000 |
| urgency[p1] | OR 1.60 [1.19, 2.15] | 0.002 | 1.000 |
| mobility_aid[p1] | OR 1.03 [0.77, 1.38] | 0.837 | 1.000 |
| load[p1] | OR 0.92 [0.69, 1.24] | 0.580 | 1.000 |
| distraction[p1] | OR 1.13 [0.84, 1.52] | 0.403 | 1.000 |
| assertiveness[p1] | OR 1.11 [0.82, 1.48] | 0.506 | 1.000 |
| residence[p1] | OR 0.99 [0.73, 1.32] | 0.925 | 1.000 |
| memory_note[p1] | OR 1.13 [0.84, 1.52] | 0.409 | 1.000 |
| ethnicity_pair[different] | OR 0.91 [0.68, 1.22] | 0.532 | 1.000 |
| surroundings[busy] | OR 0.86 [0.64, 1.15] | 0.300 | 1.000 |
| time_of_day[late_night] | OR 0.80 [0.60, 1.08] | 0.143 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 0.78 [0.58, 1.05] | 0.099 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 1.00 [0.74, 1.34] | 0.974 | 1.000 |
| familiarity[strangers] | OR 0.77 [0.57, 1.03] | 0.081 | 1.000 |
| mapping[p1_higher] | OR 1.22 [0.91, 1.64] | 0.191 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.83 [0.62, 1.11] | 0.209 | 1.000 |
| condition[silent] | OR 1.44 [1.01, 2.07] | 0.046 | 1.000 |
| condition[talk] | OR 0.95 [0.67, 1.35] | 0.789 | 1.000 |

**`resolved_by_llm`** (session): resolved in `plan_only` before ORCA took over. Status: ok, n = 816, events = 482.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.86 [0.64, 1.15] | 0.316 | 1.000 |
| gender_pair[p1_male] | OR 1.05 [0.79, 1.41] | 0.737 | 1.000 |
| urgency[p1] | OR 1.58 [1.18, 2.11] | 0.002 | 1.000 |
| mobility_aid[p1] | OR 0.96 [0.71, 1.28] | 0.763 | 1.000 |
| load[p1] | OR 0.85 [0.64, 1.14] | 0.291 | 1.000 |
| distraction[p1] | OR 1.41 [1.06, 1.89] | 0.020 | 1.000 |
| assertiveness[p1] | OR 0.86 [0.64, 1.14] | 0.293 | 1.000 |
| residence[p1] | OR 0.88 [0.65, 1.17] | 0.372 | 1.000 |
| memory_note[p1] | OR 1.17 [0.88, 1.57] | 0.285 | 1.000 |
| ethnicity_pair[different] | OR 0.85 [0.64, 1.13] | 0.253 | 1.000 |
| surroundings[busy] | OR 0.88 [0.66, 1.18] | 0.395 | 1.000 |
| time_of_day[late_night] | OR 0.70 [0.53, 0.94] | 0.019 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 0.90 [0.68, 1.21] | 0.487 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 0.97 [0.73, 1.30] | 0.852 | 1.000 |
| familiarity[strangers] | OR 0.81 [0.60, 1.08] | 0.151 | 1.000 |
| mapping[p1_higher] | OR 1.16 [0.87, 1.55] | 0.319 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.73 [0.55, 0.97] | 0.029 | 1.000 |
| condition[silent] | OR 1.54 [1.08, 2.19] | 0.016 | 1.000 |
| condition[talk] | OR 1.19 [0.84, 1.68] | 0.334 | 1.000 |

**`decision_points`** (session): decision points of both people. Status: ok, n = 816.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | +0.458 [+0.058, +0.859] | 0.025 | 1.000 |
| gender_pair[p1_male] | -0.151 [-0.550, +0.248] | 0.458 | 1.000 |
| urgency[p1] | -0.417 [-0.815, -0.019] | 0.040 | 1.000 |
| mobility_aid[p1] | +0.437 [+0.036, +0.839] | 0.033 | 1.000 |
| load[p1] | +0.370 [-0.030, +0.770] | 0.070 | 1.000 |
| distraction[p1] | +0.099 [-0.300, +0.498] | 0.627 | 1.000 |
| assertiveness[p1] | +0.297 [-0.097, +0.691] | 0.140 | 1.000 |
| residence[p1] | -0.156 [-0.555, +0.243] | 0.443 | 1.000 |
| memory_note[p1] | +0.271 [-0.129, +0.671] | 0.184 | 1.000 |
| ethnicity_pair[different] | +0.232 [-0.155, +0.620] | 0.239 | 1.000 |
| surroundings[busy] | +0.151 [-0.248, +0.550] | 0.459 | 1.000 |
| time_of_day[late_night] | +0.255 [-0.144, +0.654] | 0.210 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | -0.139 [-0.533, +0.255] | 0.489 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | -0.115 [-0.515, +0.285] | 0.574 | 1.000 |
| familiarity[strangers] | +0.078 [-0.321, +0.477] | 0.701 | 1.000 |
| mapping[p1_higher] | -0.198 [-0.595, +0.200] | 0.329 | 1.000 |
| geometry[layout=apart_20cm] | +0.569 [+0.181, +0.956] | 0.004 | 1.000 |
| condition[silent] | -0.437 [-0.893, +0.018] | 0.060 | 1.000 |
| condition[talk] | +0.173 [-0.322, +0.668] | 0.494 | 1.000 |

## 2. Decision tree

Predicts **`passed_first`** per agent, depth at most 3, on 1092 rows (the predictors that vary, with condition and geometry). Figure: `tree.png`.

- Accuracy on the rows it was grown on: 0.817; always guessing the commoner outcome: 0.770.
- Accuracy on held-out sessions (5-fold, grouped by session): 0.796.
- Splits on: `own_assertiveness`, `own_distraction`, `own_load`, `own_memory_note`, `own_mobility_aid`, `own_urgency`, `surroundings_busy`.

A tree no better on held-out sessions than the commoner outcome has found no usable pattern.

```
|--- own_assertiveness <= 0.50
|   |--- own_urgency <= 0.50
|   |   |--- own_distraction <= 0.50
|   |   |   |--- weights: [576.00, 55.00] class: 0
|   |   |--- own_distraction >  0.50
|   |   |   |--- weights: [47.00, 10.00] class: 0
|   |--- own_urgency >  0.50
|   |   |--- own_load <= 0.50
|   |   |   |--- weights: [57.00, 9.00] class: 0
|   |   |--- own_load >  0.50
|   |   |   |--- weights: [44.00, 18.00] class: 0
|--- own_assertiveness >  0.50
|   |--- own_mobility_aid <= 0.50
|   |   |--- surroundings_busy <= 0.50
|   |   |   |--- weights: [27.00, 36.00] class: 1
|   |   |--- surroundings_busy >  0.50
|   |   |   |--- weights: [40.00, 31.00] class: 0
|   |--- own_mobility_aid >  0.50
|   |   |--- own_memory_note <= 0.50
|   |   |   |--- weights: [20.00, 56.00] class: 1
|   |   |--- own_memory_note >  0.50
|   |   |   |--- weights: [30.00, 36.00] class: 1
```

## 3. Counterfactual pairs against the noise floor

The noise floor is the flip rate between repeats of one cell of the exact-repeat set (identical prompts), with a bootstrap 95% interval over cells. A pair's flip rate (Wilson 95% interval) counts as evidence only where its lower end is above the noise floor's upper end, in the same condition. Components: `who_passed_first`, `passing_side`, `stopped`, `backed_up`, `behaviour` (`behaviour` is all of them together).

### The noise floor

| component | subset | cells | pairs | flips | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| who_passed_first | all | 192 | 1152 | 762 | 0.661 | 0.627 | 0.694 |
| who_passed_first | non_verbal | 64 | 384 | 257 | 0.669 | 0.604 | 0.729 |
| who_passed_first | talk | 64 | 384 | 239 | 0.622 | 0.562 | 0.677 |
| who_passed_first | silent | 64 | 384 | 266 | 0.693 | 0.638 | 0.742 |
| passing_side | all | 192 | 1152 | 498 | 0.432 | 0.396 | 0.469 |
| passing_side | non_verbal | 64 | 384 | 159 | 0.414 | 0.349 | 0.474 |
| passing_side | talk | 64 | 384 | 177 | 0.461 | 0.404 | 0.516 |
| passing_side | silent | 64 | 384 | 162 | 0.422 | 0.357 | 0.484 |
| stopped | all | 192 | 1152 | 61 | 0.053 | 0.031 | 0.076 |
| stopped | non_verbal | 64 | 384 | 49 | 0.128 | 0.078 | 0.180 |
| stopped | talk | 64 | 384 | 6 | 0.016 | 0 | 0.039 |
| stopped | silent | 64 | 384 | 6 | 0.016 | 0 | 0.039 |
| backed_up | all | 192 | 1152 | 0 | 0 | 0 | 0 |
| backed_up | non_verbal | 64 | 384 | 0 | 0 | 0 | 0 |
| backed_up | talk | 64 | 384 | 0 | 0 | 0 | 0 |
| backed_up | silent | 64 | 384 | 0 | 0 | 0 | 0 |
| behaviour | all | 192 | 1152 | 923 | 0.801 | 0.773 | 0.828 |
| behaviour | non_verbal | 64 | 384 | 302 | 0.786 | 0.729 | 0.839 |
| behaviour | talk | 64 | 384 | 311 | 0.810 | 0.768 | 0.849 |
| behaviour | silent | 64 | 384 | 310 | 0.807 | 0.758 | 0.854 |

### The counterfactual pairs

| factor | component | subset | pairs | flips | rate | ci_low | ci_high | noise_rate | noise_high | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attractiveness_0_sees_1 | who_passed_first | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.661 | 0.694 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.669 | 0.729 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.622 | 0.677 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | silent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.693 | 0.742 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.661 | 0.694 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.669 | 0.729 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.622 | 0.677 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | silent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.693 | 0.742 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.661 | 0.694 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.669 | 0.729 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.622 | 0.677 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | silent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.693 | 0.742 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.661 | 0.694 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.669 | 0.729 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | talk | 2 | 2 | 1 | 0.342 | 1 | 0.622 | 0.677 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | silent | 2 | 2 | 1 | 0.342 | 1 | 0.693 | 0.742 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.432 | 0.469 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.414 | 0.474 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | talk | 2 | 0 | 0 | 0 | 0.658 | 0.461 | 0.516 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | silent | 2 | 2 | 1 | 0.342 | 1 | 0.422 | 0.484 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.432 | 0.469 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.414 | 0.474 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | talk | 2 | 0 | 0 | 0 | 0.658 | 0.461 | 0.516 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | silent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.422 | 0.484 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.432 | 0.469 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.414 | 0.474 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.461 | 0.516 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | silent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.422 | 0.484 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.432 | 0.469 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.414 | 0.474 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.461 | 0.516 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | silent | 2 | 0 | 0 | 0 | 0.658 | 0.422 | 0.484 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.053 | 0.076 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.128 | 0.180 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.016 | 0.039 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | silent | 2 | 0 | 0 | 0 | 0.658 | 0.016 | 0.039 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.053 | 0.076 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.128 | 0.180 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.016 | 0.039 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | silent | 2 | 0 | 0 | 0 | 0.658 | 0.016 | 0.039 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.053 | 0.076 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.128 | 0.180 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.016 | 0.039 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | silent | 2 | 0 | 0 | 0 | 0.658 | 0.016 | 0.039 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0.053 | 0.076 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0.128 | 0.180 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0.016 | 0.039 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | silent | 2 | 0 | 0 | 0 | 0.658 | 0.016 | 0.039 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | backed_up | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | backed_up | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | backed_up | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | backed_up | silent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | backed_up | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | backed_up | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | backed_up | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | backed_up | silent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | backed_up | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | backed_up | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | backed_up | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | backed_up | silent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | backed_up | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | backed_up | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | backed_up | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | backed_up | silent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.801 | 0.828 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.786 | 0.839 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.810 | 0.849 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | silent | 2 | 2 | 1 | 0.342 | 1 | 0.807 | 0.854 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | all | 6 | 5 | 0.833 | 0.436 | 0.970 | 0.801 | 0.828 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.786 | 0.839 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.810 | 0.849 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | silent | 2 | 2 | 1 | 0.342 | 1 | 0.807 | 0.854 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | all | 6 | 5 | 0.833 | 0.436 | 0.970 | 0.801 | 0.828 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.786 | 0.839 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.810 | 0.849 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | silent | 2 | 2 | 1 | 0.342 | 1 | 0.807 | 0.854 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | all | 6 | 5 | 0.833 | 0.436 | 0.970 | 0.801 | 0.828 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.786 | 0.839 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | talk | 2 | 2 | 1 | 0.342 | 1 | 0.810 | 0.849 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | silent | 2 | 2 | 1 | 0.342 | 1 | 0.807 | 0.854 | not distinguishable from the noise floor |

## 4. Behaviour stability

Per cell of the exact-repeat set: the share of its repeats with the commonest outcome (1: every repeat the same). A cell whose commonest behaviour came up in fewer than 0.75 of its repeats is a coin flip, and RF-11 should claim no rule there.

| Component | Cells | Mean | Lowest | Cells with every repeat the same |
| --- | --- | --- | --- | --- |
| who_passed_first | 192 | 0.595 | 0.250 | 13 |
| passing_side | 192 | 0.734 | 0.500 | 45 |
| stopped | 192 | 0.973 | 0.500 | 172 |
| backed_up | 192 | 1 | 1 | 192 |
| behaviour | 192 | 0.483 | 0.250 | 5 |

### Coin-flip cells: 163 of 192

| Cell | Condition | Repeats | Stability | Who passed first | Commonest behaviour |
| --- | --- | --- | --- | --- | --- |
| N_head_on_02dfbadb_02604456 | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_0f57f8a5 | non_verbal | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_1868bff4 | non_verbal | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_1caa9a84 | non_verbal | 4 | 0.250 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_231c8154 | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_2ec958bb | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_3cb16ae9 | non_verbal | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_51dfba80 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_5767d932 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_68f09b97 | non_verbal | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_6ab9c72e | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_74cb78c1 | non_verbal | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_7eed7b59 | non_verbal | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_800a3b04 | non_verbal | 4 | 0.250 | 0.500 | p2\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_8ea28db3 | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_9950986f | non_verbal | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_9b752a36 | non_verbal | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_b1d97a31 | non_verbal | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_b59c2831 | non_verbal | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_b7fe7ead | non_verbal | 4 | 0.250 | 0.250 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_bcb9cb2c | non_verbal | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_c36d5d49 | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_cb859069 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_ce2a06ef | non_verbal | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_dbd98c92 | non_verbal | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_f3d09c23 | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_0f57f8a5 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_1868bff4 | non_verbal | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_1caa9a84 | non_verbal | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_231c8154 | non_verbal | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_3cb16ae9 | non_verbal | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_55c9ae40 | non_verbal | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_5767d932 | non_verbal | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_68f09b97 | non_verbal | 4 | 0.250 | 0.250 | p2\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_6ab9c72e | non_verbal | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_74cb78c1 | non_verbal | 4 | 0.250 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_800a3b04 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_81bae7c3 | non_verbal | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_9950986f | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_9b752a36 | non_verbal | 4 | 0.250 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_b1d97a31 | non_verbal | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_b59c2831 | non_verbal | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_b6a40c60 | non_verbal | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_b7fe7ead | non_verbal | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_bcb9cb2c | non_verbal | 4 | 0.250 | 0.250 | p2\|right\|right\|1\|0\|0\|0 |
| N_head_on_de176842_c36d5d49 | non_verbal | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_ce2a06ef | non_verbal | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_dbd98c92 | non_verbal | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_f79677df | non_verbal | 4 | 0.500 | 1 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_02604456 | silent | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_0f57f8a5 | silent | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_1868bff4 | silent | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_1caa9a84 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_231c8154 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_2ec958bb | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_3cb16ae9 | silent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_3dee0df5 | silent | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_51dfba80 | silent | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_55c9ae40 | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_5767d932 | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_68f09b97 | silent | 4 | 0.250 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_6ab9c72e | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_74cb78c1 | silent | 4 | 0.250 | 0.500 | p2\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_800a3b04 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_81bae7c3 | silent | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_8ea28db3 | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_9950986f | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_9b752a36 | silent | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_b1d97a31 | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_b59c2831 | silent | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_b6a40c60 | silent | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_b7fe7ead | silent | 4 | 0.500 | 1 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_bcb9cb2c | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_c36d5d49 | silent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_cb859069 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_ce2a06ef | silent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_dbd98c92 | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_02dfbadb_e57e5fb0 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_f3d09c23 | silent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| S_head_on_02dfbadb_f79677df | silent | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_0f57f8a5 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_1868bff4 | silent | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| S_head_on_de176842_1caa9a84 | silent | 4 | 0.250 | 0.250 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_de176842_2ec958bb | silent | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_3cb16ae9 | silent | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_3dee0df5 | silent | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_51dfba80 | silent | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_55c9ae40 | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_de176842_5767d932 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_68f09b97 | silent | 4 | 0.250 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_6ab9c72e | silent | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_74cb78c1 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_7eed7b59 | silent | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_800a3b04 | silent | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_81bae7c3 | silent | 4 | 0.250 | 0.250 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_de176842_9950986f | silent | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_9b752a36 | silent | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_b1d97a31 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_b6a40c60 | silent | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_bcb9cb2c | silent | 4 | 0.250 | 0.500 | p1\|left\|left\|0\|1\|0\|0 |
| S_head_on_de176842_c36d5d49 | silent | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_cb859069 | silent | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| S_head_on_de176842_ce2a06ef | silent | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_dbd98c92 | silent | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_e57e5fb0 | silent | 4 | 0.250 | 0.250 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_f3d09c23 | silent | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| S_head_on_de176842_f79677df | silent | 4 | 0.250 | 0.250 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_02604456 | talk | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_0f57f8a5 | talk | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_1868bff4 | talk | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_1caa9a84 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_231c8154 | talk | 4 | 0.500 | 0.750 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_2ec958bb | talk | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_3cb16ae9 | talk | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_3dee0df5 | talk | 4 | 0.250 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_51dfba80 | talk | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_55c9ae40 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_68f09b97 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_6ab9c72e | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_74cb78c1 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_800a3b04 | talk | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_81bae7c3 | talk | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_9950986f | talk | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_9b752a36 | talk | 4 | 0.500 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_b1d97a31 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_b59c2831 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_b6a40c60 | talk | 4 | 0.500 | 1 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_b7fe7ead | talk | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_bcb9cb2c | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_cb859069 | talk | 4 | 0.500 | 0.750 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_ce2a06ef | talk | 4 | 0.500 | 1 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_dbd98c92 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_e57e5fb0 | talk | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_f3d09c23 | talk | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_f79677df | talk | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_02604456 | talk | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_0f57f8a5 | talk | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_1868bff4 | talk | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_1caa9a84 | talk | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_231c8154 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_3cb16ae9 | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_3dee0df5 | talk | 4 | 0.500 | 0.500 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_51dfba80 | talk | 4 | 0.250 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_55c9ae40 | talk | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_68f09b97 | talk | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_6ab9c72e | talk | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_74cb78c1 | talk | 4 | 0.250 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_800a3b04 | talk | 4 | 0.500 | 0.500 | together\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_81bae7c3 | talk | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_8ea28db3 | talk | 4 | 0.250 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_9950986f | talk | 4 | 0.250 | 0.500 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_9b752a36 | talk | 4 | 0.500 | 0.500 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_b1d97a31 | talk | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_b6a40c60 | talk | 4 | 0.500 | 1 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_b7fe7ead | talk | 4 | 0.500 | 0.500 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_bcb9cb2c | talk | 4 | 0.500 | 0.750 | p1\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_c36d5d49 | talk | 4 | 0.500 | 0.750 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_cb859069 | talk | 4 | 0.500 | 0.750 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_ce2a06ef | talk | 4 | 0.500 | 0.500 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_dbd98c92 | talk | 4 | 0.250 | 0.250 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_e57e5fb0 | talk | 4 | 0.500 | 0.500 | p2\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_f3d09c23 | talk | 4 | 0.500 | 0.750 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_f79677df | talk | 4 | 0.250 | 0.500 | -\|right\|right\|0\|0\|0\|0 |

## 5. The factor-to-decision mapping

Every observed combination of `own_age_high`, `own_female`, `other_age_high`, `other_female`, `own_urgency`, `own_mobility_aid`, `own_load`, `own_distraction`, `own_assertiveness`, `own_residence`, `own_memory_note`, `other_mobility_aid`, `other_load`, `other_distraction`, `same_ethnicity`, `surroundings_busy`, `time_of_day_late_night`, `finds_other_attractive`, `knows_other`, `is_lower_agent`, `asked_first`, `geometry`, per condition, from the agent's point of view: **786 combinations** in `mapping.csv`, each with its rows and, per outcome, how many are known and the share that are 1. Read the counts with the shares: a combination seen once gives 0 or 1 from one row. The 25 combinations with the most rows:

| condition | own_age_high | own_female | other_age_high | other_female | own_urgency | own_mobility_aid | own_load | own_distraction | own_assertiveness | own_residence | own_memory_note | other_mobility_aid | other_load | other_distraction | same_ethnicity | surroundings_busy | time_of_day_late_night | finds_other_attractive | knows_other | is_lower_agent | asked_first | geometry | rows | p_passed_first | p_kept_left | p_stopped | p_backed_up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| silent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 6 | 0.250 | 0.500 | 0 | 0 |
| silent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 6 | 0 | 0.333 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 6 | 0 | 0.667 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 6 | 0 | 0.667 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 6 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 6 | 0 | 0.667 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 5 | 0 | 0.600 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | layout=aligned | 5 | 0 | 0.800 | 0 | 0 |
| silent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | layout=aligned | 5 | 0 | 0.600 | 0 | 0 |
| silent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 5 | 0.400 | 0.400 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | layout=aligned | 5 | 0.250 | 0.400 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 5 | 0.250 | 0.600 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 4 | 0 | 1 | 0 | 0 |
| silent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | layout=aligned | 4 | 0 | 0.750 | 0 | 0 |
| silent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| silent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0 | 0.750 | 0 | 0 |
| silent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 1 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| talk | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | layout=apart_20cm | 2 | 1 | 1 | 0 | 0 |

## 6. Stated against measured

How often each factor is named in the agents' private `reason` (keyword codebook `reasons_v1`), beside its strongest measured effect in the per-agent models of all conditions together. Named often: in at least 0.1 of the reasons. Measured: a term significant after Holm's correction. A factor named often with no measured effect, or the reverse, is a finding.

| Factor | Share of reasons naming it | Measured effect | Outcome | Term | Estimate (OR or coef.) | Holm p | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| age | 0.214 | yes | plan_slowed | other_age_high | 4.305 | < 0.001 | named often, and a measured effect |
| gender | 0.050 | no | passed_first | own_female | 1.421 | 1.000 | neither |
| urgency | 0.118 | yes | plan_slowed | own_urgency | 0.352 | < 0.001 | named often, and a measured effect |
| mobility_aid | 0.296 | yes | plan_slowed | other_mobility_aid | 4.717 | < 0.001 | named often, and a measured effect |
| load | 0.350 | yes | plan_slowed | other_load | 2.887 | < 0.001 | named often, and a measured effect |
| distraction | 0.252 | no | passed_first | own_distraction | 1.507 | 1.000 | named often, no measured effect |
| assertiveness | 0.279 | yes | passed_first | own_assertiveness | 8.398 | < 0.001 | named often, and a measured effect |
| residence | 0.001 | yes | plan_left | own_residence | 0.353 | < 0.001 | a measured effect, rarely named |
| memory_note | 0.134 | no | passed_first | own_memory_note | 0.681 | 1.000 | named often, no measured effect |
| surroundings | 0.076 | no | passed_first | surroundings_busy | 0.824 | 1.000 | neither |
| time_of_day | 0.025 | no | passed_first | time_of_day_late_night | 0.935 | 1.000 | neither |
| perceived_attractiveness | 0.019 | yes | plan_slowed | finds_other_attractive | 1.836 | 0.002 | a measured effect, rarely named |
| familiarity | 0.051 | yes | plan_slowed | knows_other | 2.730 | < 0.001 | a measured effect, rarely named |
| asked_first | - | no | passed_first | asked_first | 1.195 | 1.000 | neither |
| ethnicity_pair | - | no | passed_first | same_ethnicity | 0.907 | 1.000 | neither |
| is_lower_agent | - | no | passed_first | is_lower_agent | 1.252 | 1.000 | neither |

**Where saying and doing disagree:** `distraction` (named often, no measured effect), `residence` (a measured effect, rarely named), `memory_note` (named often, no measured effect), `perceived_attractiveness` (a measured effect, rarely named), `familiarity` (a measured effect, rarely named).

### The debriefs' kind of basis

One per prompted agent (D8); every source is unchecked until RF-14.

| kind | non_verbal | silent | talk | all |
| --- | --- | --- | --- | --- |
| local_custom | 6 | 4 | 13 | 23 |
| habit | 122 | 57 | 87 | 266 |
| common_sense | 394 | 462 | 429 | 1285 |
| none | 22 | 21 | 14 | 57 |
| (none given) | 0 | 0 | 1 | 1 |
| all | 544 | 544 | 544 | 1632 |

## 7. Intent against plan

Each readable intent coded by the keyword codebook `intent_v2` (keep to a side, slow down, stop and wait, back up, carry on, or `other`), against the plan coded from its steps. A mismatch is an intent that says something the plan does not do. Intents coded `other` and unreadable replies are left out of the rate. A high rate means the structured plan cannot be trusted on its own (RF-11).

| subset | decision_points | unreadable | uncoded | compared | mismatches | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 5256 | 121 | 558 | 4577 | 1234 | 0.270 | 0.257 | 0.283 |
| non_verbal | 1776 | 22 | 199 | 1555 | 391 | 0.251 | 0.231 | 0.274 |
| silent | 1657 | 52 | 184 | 1421 | 462 | 0.325 | 0.301 | 0.350 |
| talk | 1823 | 47 | 175 | 1601 | 381 | 0.238 | 0.218 | 0.259 |

### Examples of mismatches

| condition | session_id | agent_id | intent | plan_categories | plan_side | why |
| --- | --- | --- | --- | --- | --- | --- |
| talk | T_head_on_02dfbadb_e57e5fb0_r4 | 0 | Keep close to the right wall so the elderly man with the suitcase can pass on my left, and continue on to the supermarket. | slow_down | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| silent | S_head_on_02dfbadb_6ab9c72e_r1 | 0 | Keep heading toward the emergency room, giving Person 1 plenty of room to pass since I'm slow with the cane and suitcase. | keep_to_side | right | intent says slow_down, the plan does not |
| silent | S_head_on_02dfbadb_6ab9c72e_r1 | 0 | Keep making room for Person 1 to pass, staying to my right since I'm slower with the cane and suitcase. | keep_to_side | right | intent says slow_down, the plan does not |
| talk | T_head_on_de176842_5841fc4a_x3d3cadc7_base | 1 | Keep walking to the supermarket and give way to the oncoming woman so we can pass comfortably in the narrow passage. | keep_to_side | left | intent says carry_on, the plan does not |
| silent | S_head_on_02dfbadb_b1d97a31_r4 | 1 | Keep giving the older man plenty of room to pass, staying to my right side of the passage. | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| silent | S_head_on_02dfbadb_b1d97a31_r4 | 1 | Keep well to my right so the older man and I can pass each other comfortably. | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| talk | T_head_on_02dfbadb_b59c2831_r1 | 1 | Keep walking to the emergency room while glancing up to acknowledge Person 1 so we don't bump into each other | keep_to_side | left | intent says carry_on, the plan does not |
| talk | T_head_on_02dfbadb_b59c2831_r1 | 1 | Keep moving quickly toward the emergency room, staying to my left so Person 1 can pass on his side. | carry_on | none | intent says keep_to_side, the plan does not; intent says left, the plan turns none |
| talk | T_head_on_02dfbadb_b59c2831_r1 | 0 | Keep to my right, give my classmate a friendly nod back, and carry on past her to the supermarket. | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| non_verbal | N_head_on_de176842_8ea28db3_r2 | 1 | Carry on toward the supermarket, keeping to the right side of the passage | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| silent | S_head_on_de176842_1caa9a84_r4 | 0 | Keep heading to the supermarket while giving the man with the cane and suitcase plenty of room to pass. | keep_to_side;slow_down | left | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_c36d5d49_r2 | 0 | Acknowledge Person 1 and keep moving quickly toward the emergency room, holding my line. | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_74cb78c1_r2 | 1 | Keep to the right and let the oncoming person pass without fuss. | slow_down | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| non_verbal | N_head_on_02dfbadb_02604456_r2 | 0 | Greet my classmate and keep well to my left so she and her suitcase pass easily | slow_down | none | intent says keep_to_side, the plan does not; intent says left, the plan turns none |
| non_verbal | N_head_on_de176842_7eed7b59_r3 | 0 | Keep well to the left and slow down a bit more so the elderly woman looking at her phone can pass safely | slow_down | none | intent says keep_to_side, the plan does not; intent says left, the plan turns none |

### Intents the codebook could not place (the commonest)

- 3 x "Give way to the elderly man with the cane and greet him as we pass"
- 2 x "Give the elderly woman with the suitcase plenty of room and greet her as we pass."
- 2 x "Keep my line and pace toward the emergency room; I'm not swerving for anyone tonight."
- 2 x "Give the elderly woman with a cane plenty of room as we pass"
- 2 x "Give way to the older woman with the suitcase and greet her as we pass"

## 8. Real ethnicity

Descriptive. A difference between groups here is the model's behaviour towards people it was told are of a group, not a fact about those groups, and no rule may read ethnicity (`llm_negotiation/docs/ethnicity.md`).

### By group, the other's as told (unweighted agent rows)

| own | other_as_told | n | passed_first | kept_left | stopped | backed_up | plan_slowed | plan_left | plan_right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chinese | chinese | 234 | 0.203 | 0.308 | 0.009 | 0 | 0.639 | 0.227 | 0.730 |
| chinese | malay | 69 | 0.250 | 0.435 | 0 | 0 | 0.638 | 0.348 | 0.580 |
| chinese | indian | 84 | 0.200 | 0.476 | 0.012 | 0 | 0.738 | 0.393 | 0.512 |
| chinese | others | 60 | 0.152 | 0.450 | 0.033 | 0 | 0.650 | 0.350 | 0.617 |
| malay | chinese | 69 | 0.159 | 0.435 | 0.029 | 0 | 0.681 | 0.478 | 0.522 |
| malay | malay | 198 | 0.164 | 0.556 | 0.010 | 0 | 0.556 | 0.480 | 0.470 |
| malay | indian | 63 | 0.220 | 0.397 | 0 | 0 | 0.667 | 0.286 | 0.683 |
| malay | others | 72 | 0.240 | 0.417 | 0.028 | 0 | 0.569 | 0.403 | 0.444 |
| indian | chinese | 84 | 0.280 | 0.476 | 0.036 | 0 | 0.679 | 0.298 | 0.667 |
| indian | malay | 63 | 0.098 | 0.397 | 0.016 | 0 | 0.698 | 0.429 | 0.524 |
| indian | indian | 192 | 0.266 | 0.302 | 0.005 | 0 | 0.688 | 0.266 | 0.688 |
| indian | others | 60 | 0.417 | 0.367 | 0 | 0 | 0.433 | 0.300 | 0.600 |
| others | chinese | 60 | 0.394 | 0.450 | 0 | 0 | 0.550 | 0.367 | 0.550 |
| others | malay | 72 | 0.260 | 0.417 | 0 | 0 | 0.611 | 0.347 | 0.597 |
| others | indian | 60 | 0.188 | 0.367 | 0.033 | 0 | 0.717 | 0.350 | 0.583 |
| others | others | 192 | 0.261 | 0.510 | 0.016 | 0 | 0.490 | 0.385 | 0.531 |

Each share is over the rows where the outcome is defined (`<outcome>_n` in `ethnicity_groups.csv`).

### Weighted back to random resident pairs

Each session weighted by `ethnicity_weight`, so that the sessions stand for two residents met at random (each at the resident shares; residents only). Use the weighted rate for a population-level figure; the effective number of sessions is what the weighting leaves.

| outcome | sessions | unweighted | weighted | effective_sessions |
| --- | --- | --- | --- | --- |
| resolved_plan_only | 816 | 0.591 | 0.577 | 288.580 |
| resolved_plan_orca | 816 | 0.626 | 0.611 | 288.580 |
| resolved_by_llm | 816 | 0.591 | 0.577 | 288.580 |

## How to read this report

- **An effect here is an effect on what the LLM agents did**, in this design: a screen, so main effects are estimated clear of two-factor interactions only when the design is a resolution IV fraction (`llm_negotiation/docs/screening-designs.md`, section 3).
- **Separation** (an outcome predicted perfectly by some predictor) leaves a model with no finite estimate; it is listed, not reported as an effect. Rare outcomes with many factors cause it: D14 aims at about 10 events per factor.
- **The mapping is sparse** when there are many factors: most combinations are seen once or twice.
- **The codebooks are drafts** until RF-9's pilot (`analysis/codebooks/`): a mention or a coded intent is a keyword match, not a reading of the text.
