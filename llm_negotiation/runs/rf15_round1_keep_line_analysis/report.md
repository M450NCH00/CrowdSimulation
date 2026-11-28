# Factor analysis of a resolution experiment (RF-8)

## Inputs

- `llm_negotiation/runs/rf10_round1_head_on_keep_line/outcomes.csv`
- `llm_negotiation/runs/rf30_round1_head_on_keep_line/outcomes.csv`

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
| plan_slowed | all | own_assertiveness | OR 0.10 [0.05, 0.21] | < 0.001 | < 0.001 | 571 |
| plan_slowed | independent | own_assertiveness | OR 0.05 [0.02, 0.20] | < 0.001 | 0.005 | 187 |
| signalled | all | knows_other | OR 444.57 [47.45, 4164.92] | < 0.001 | < 0.001 | 384 |
| signalled | all | own_assertiveness | OR 13.55 [4.47, 41.07] | < 0.001 | 0.003 | 384 |
| signalled | all | finds_other_attractive | OR 6.53 [2.68, 15.89] | < 0.001 | 0.024 | 384 |
| start_distance_m | all | own_mobility_aid | +2.250 [+1.188, +3.312] | < 0.001 | 0.022 | 13 |
| start_distance_m | non_verbal | own_age_high | -1.000 [-1.000, -1.000] | < 0.001 | < 0.001 | 12 |
| start_distance_m | non_verbal | own_mobility_aid | +2.250 [+1.230, +3.270] | < 0.001 | 0.010 | 12 |
| decision_points | all | condition[non_verbal] | +3.365 [+3.153, +3.576] | < 0.001 | < 0.001 | 288 |
| decision_points | all | condition[talk] | +3.458 [+3.235, +3.682] | < 0.001 | < 0.001 | 288 |

### Every model

| outcome | level | subset | status | n | events | clusters | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| passed_first | agent | all | ok | 350 | 55 | 175 |  |
| kept_left | agent | all | ok | 576 | 258 | 288 |  |
| stopped | agent | all | separation | 576 | 1 | 288 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | all | one value | 576 | 0 | - | every row is 0 |
| plan_left | agent | all | ok | 571 | 144 | 288 |  |
| plan_right | agent | all | ok | 571 | 218 | 288 |  |
| plan_slowed | agent | all | ok | 571 | 381 | 288 |  |
| plan_stopped | agent | all | separation | 571 | 3 | 288 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | all | one value | 571 | 0 | - | every row is 0 |
| start_distance_m | agent | all | ok | 13 | - | 13 |  |
| signalled | agent | all | ok | 384 | 243 | 192 |  |
| resolved_plan_only | session | all | ok | 288 | 152 | - |  |
| resolved_plan_orca | session | all | ok | 288 | 158 | - |  |
| resolved_by_llm | session | all | ok | 288 | 143 | - |  |
| decision_points | session | all | ok | 288 | - | - |  |
| passed_first | agent | independent | ok | 110 | 16 | 55 |  |
| kept_left | agent | independent | ok | 192 | 70 | 96 |  |
| stopped | agent | independent | one value | 192 | 0 | - | every row is 0 |
| backed_up | agent | independent | one value | 192 | 0 | - | every row is 0 |
| plan_left | agent | independent | ok | 187 | 33 | 96 |  |
| plan_right | agent | independent | ok | 187 | 68 | 96 |  |
| plan_slowed | agent | independent | ok | 187 | 127 | 96 |  |
| plan_stopped | agent | independent | one value | 187 | 0 | - | every row is 0 |
| plan_backed_up | agent | independent | one value | 187 | 0 | - | every row is 0 |
| start_distance_m | agent | independent | no data | 0 | - | - |  |
| signalled | agent | independent | no data | 0 | - | - |  |
| resolved_plan_only | session | independent | ok | 96 | 52 | - |  |
| resolved_plan_orca | session | independent | ok | 96 | 53 | - |  |
| resolved_by_llm | session | independent | ok | 96 | 43 | - |  |
| decision_points | session | independent | one value | 96 | - | - | every row is 2 |
| passed_first | agent | non_verbal | ok | 124 | 23 | 62 |  |
| kept_left | agent | non_verbal | ok | 192 | 90 | 96 |  |
| stopped | agent | non_verbal | separation | 192 | 1 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | non_verbal | one value | 192 | 0 | - | every row is 0 |
| plan_left | agent | non_verbal | ok | 192 | 48 | 96 |  |
| plan_right | agent | non_verbal | ok | 192 | 86 | 96 |  |
| plan_slowed | agent | non_verbal | ok | 192 | 122 | 96 |  |
| plan_stopped | agent | non_verbal | separation | 192 | 2 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | non_verbal | one value | 192 | 0 | - | every row is 0 |
| start_distance_m | agent | non_verbal | ok | 12 | - | 12 |  |
| signalled | agent | non_verbal | ok | 192 | 110 | 96 |  |
| resolved_plan_only | session | non_verbal | separation | 96 | 53 | - | the outcome is (nearly) separated by the predictors: no finite estimate |
| resolved_plan_orca | session | non_verbal | ok | 96 | 55 | - |  |
| resolved_by_llm | session | non_verbal | separation | 96 | 53 | - | the outcome is (nearly) separated by the predictors: no finite estimate |
| decision_points | session | non_verbal | ok | 96 | - | - |  |
| passed_first | agent | talk | ok | 116 | 16 | 58 |  |
| kept_left | agent | talk | ok | 192 | 98 | 96 |  |
| stopped | agent | talk | one value | 192 | 0 | - | every row is 0 |
| backed_up | agent | talk | one value | 192 | 0 | - | every row is 0 |
| plan_left | agent | talk | ok | 192 | 63 | 96 |  |
| plan_right | agent | talk | ok | 192 | 64 | 96 |  |
| plan_slowed | agent | talk | separation | 192 | 132 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_stopped | agent | talk | separation | 192 | 1 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_backed_up | agent | talk | one value | 192 | 0 | - | every row is 0 |
| start_distance_m | agent | talk | one value | 1 | - | - | every row is 3 |
| signalled | agent | talk | separation | 192 | 133 | 96 | the outcome is (nearly) separated by the predictors: no finite estimate |
| resolved_plan_only | session | talk | ok | 96 | 47 | - |  |
| resolved_plan_orca | session | talk | ok | 96 | 50 | - |  |
| resolved_by_llm | session | talk | ok | 96 | 47 | - |  |
| decision_points | session | talk | ok | 96 | - | - |  |

### Each outcome, all conditions together

Per outcome: what it is, and every term of the pooled model (the per-condition terms are in `effects_terms.csv`).

**`passed_first`** (agent): left the conflict zone first (physical; `together` counts as not first). Status: ok, n = 350, events = 55.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.99 [0.44, 2.21] | 0.971 | 1.000 |
| own_female | OR 1.49 [0.73, 3.04] | 0.271 | 1.000 |
| other_age_high | OR 0.66 [0.24, 1.84] | 0.428 | 1.000 |
| own_urgency | OR 1.25 [0.55, 2.82] | 0.589 | 1.000 |
| own_mobility_aid | OR 1.54 [0.69, 3.42] | 0.287 | 1.000 |
| own_load | OR 0.79 [0.35, 1.77] | 0.563 | 1.000 |
| own_distraction | OR 2.18 [0.96, 4.96] | 0.062 | 1.000 |
| own_assertiveness | OR 3.20 [1.38, 7.39] | 0.007 | 1.000 |
| own_residence | OR 1.30 [0.58, 2.89] | 0.527 | 1.000 |
| own_memory_note | OR 0.98 [0.42, 2.26] | 0.956 | 1.000 |
| other_mobility_aid | OR 2.08 [0.75, 5.76] | 0.158 | 1.000 |
| other_load | OR 1.76 [0.66, 4.69] | 0.258 | 1.000 |
| other_distraction | OR 0.58 [0.18, 1.87] | 0.363 | 1.000 |
| same_ethnicity | OR 0.74 [0.40, 1.37] | 0.343 | 1.000 |
| surroundings_busy | OR 1.52 [0.82, 2.83] | 0.181 | 1.000 |
| time_of_day_late_night | OR 0.94 [0.51, 1.76] | 0.858 | 1.000 |
| finds_other_attractive | OR 1.06 [0.54, 2.10] | 0.862 | 1.000 |
| knows_other | OR 0.57 [0.29, 1.12] | 0.103 | 1.000 |
| is_lower_agent | OR 0.68 [0.33, 1.38] | 0.284 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.93 [0.50, 1.72] | 0.806 | 1.000 |
| condition[non_verbal] | OR 1.28 [0.63, 2.61] | 0.499 | 1.000 |
| condition[talk] | OR 0.85 [0.38, 1.86] | 0.678 | 1.000 |

Left out of the model: other_female (collinear).

**`kept_left`** (agent): kept to its own left at the closest approach (physical; rows where the two were not abreast are left out). Status: ok, n = 576, events = 258.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.34 [0.19, 0.62] | < 0.001 | 0.217 |
| own_female | OR 1.02 [0.97, 1.08] | 0.347 | 1.000 |
| other_age_high | OR 0.35 [0.20, 0.61] | < 0.001 | 0.141 |
| own_urgency | OR 1.17 [0.67, 2.05] | 0.587 | 1.000 |
| own_mobility_aid | OR 1.14 [0.64, 2.02] | 0.658 | 1.000 |
| own_load | OR 0.94 [0.54, 1.64] | 0.827 | 1.000 |
| own_distraction | OR 1.01 [0.57, 1.79] | 0.973 | 1.000 |
| own_assertiveness | OR 0.90 [0.53, 1.54] | 0.706 | 1.000 |
| own_residence | OR 0.73 [0.43, 1.23] | 0.239 | 1.000 |
| own_memory_note | OR 1.50 [0.87, 2.60] | 0.145 | 1.000 |
| other_mobility_aid | OR 1.24 [0.71, 2.18] | 0.450 | 1.000 |
| other_load | OR 0.90 [0.52, 1.56] | 0.711 | 1.000 |
| other_distraction | OR 1.08 [0.63, 1.85] | 0.790 | 1.000 |
| same_ethnicity | OR 0.70 [0.42, 1.18] | 0.180 | 1.000 |
| surroundings_busy | OR 0.87 [0.50, 1.52] | 0.628 | 1.000 |
| time_of_day_late_night | OR 1.46 [0.84, 2.55] | 0.176 | 1.000 |
| finds_other_attractive | OR 1.22 [0.82, 1.82] | 0.318 | 1.000 |
| knows_other | OR 0.45 [0.26, 0.78] | 0.005 | 1.000 |
| is_lower_agent | OR 0.98 [0.92, 1.05] | 0.532 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.39 [0.83, 2.31] | 0.208 | 1.000 |
| condition[non_verbal] | OR 1.62 [0.87, 3.02] | 0.130 | 1.000 |
| condition[talk] | OR 1.95 [1.05, 3.64] | 0.035 | 1.000 |

Left out of the model: other_female (collinear).

**`stopped`** (agent): its speed fell below the deadlock monitor's threshold (physical). Status: separation, n = 576, events = 1.

Left out of the model: other_female (collinear).

**`backed_up`** (agent): moved against its path (physical). Status: one value, n = 576, events = 0.

**`plan_left`** (agent): its first plan turns to its left only. Status: ok, n = 571, events = 144.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.18 [0.61, 2.31] | 0.619 | 1.000 |
| own_female | OR 0.93 [0.62, 1.38] | 0.719 | 1.000 |
| other_age_high | OR 0.44 [0.25, 0.79] | 0.005 | 1.000 |
| own_urgency | OR 0.99 [0.51, 1.93] | 0.974 | 1.000 |
| own_mobility_aid | OR 1.40 [0.72, 2.74] | 0.326 | 1.000 |
| own_load | OR 1.00 [0.51, 1.93] | 0.988 | 1.000 |
| own_distraction | OR 1.09 [0.56, 2.12] | 0.798 | 1.000 |
| own_assertiveness | OR 0.32 [0.15, 0.66] | 0.002 | 1.000 |
| own_residence | OR 0.36 [0.18, 0.74] | 0.005 | 1.000 |
| own_memory_note | OR 0.58 [0.29, 1.14] | 0.112 | 1.000 |
| other_mobility_aid | OR 1.60 [0.92, 2.79] | 0.099 | 1.000 |
| other_load | OR 0.95 [0.54, 1.66] | 0.858 | 1.000 |
| other_distraction | OR 1.26 [0.73, 2.18] | 0.414 | 1.000 |
| same_ethnicity | OR 1.11 [0.72, 1.71] | 0.636 | 1.000 |
| surroundings_busy | OR 0.89 [0.56, 1.39] | 0.604 | 1.000 |
| time_of_day_late_night | OR 1.22 [0.78, 1.90] | 0.376 | 1.000 |
| finds_other_attractive | OR 0.71 [0.47, 1.08] | 0.110 | 1.000 |
| knows_other | OR 0.66 [0.41, 1.05] | 0.078 | 1.000 |
| is_lower_agent | OR 1.16 [0.78, 1.73] | 0.468 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.28 [0.83, 1.98] | 0.260 | 1.000 |
| condition[non_verbal] | OR 1.62 [0.93, 2.81] | 0.086 | 1.000 |
| condition[talk] | OR 2.48 [1.46, 4.23] | < 0.001 | 0.532 |

Left out of the model: other_female (collinear).

**`plan_right`** (agent): its first plan turns to its right only. Status: ok, n = 571, events = 218.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.88 [0.50, 1.56] | 0.667 | 1.000 |
| own_female | OR 1.32 [0.89, 1.96] | 0.160 | 1.000 |
| other_age_high | OR 1.87 [1.06, 3.30] | 0.032 | 1.000 |
| own_urgency | OR 1.52 [0.87, 2.67] | 0.145 | 1.000 |
| own_mobility_aid | OR 0.72 [0.42, 1.26] | 0.256 | 1.000 |
| own_load | OR 0.96 [0.56, 1.64] | 0.868 | 1.000 |
| own_distraction | OR 1.04 [0.60, 1.81] | 0.882 | 1.000 |
| own_assertiveness | OR 1.60 [0.91, 2.80] | 0.100 | 1.000 |
| own_residence | OR 2.31 [1.35, 3.96] | 0.002 | 1.000 |
| own_memory_note | OR 1.71 [0.99, 2.95] | 0.055 | 1.000 |
| other_mobility_aid | OR 1.09 [0.61, 1.94] | 0.772 | 1.000 |
| other_load | OR 1.06 [0.60, 1.85] | 0.843 | 1.000 |
| other_distraction | OR 0.64 [0.35, 1.16] | 0.142 | 1.000 |
| same_ethnicity | OR 1.53 [1.05, 2.24] | 0.027 | 1.000 |
| surroundings_busy | OR 1.05 [0.70, 1.58] | 0.804 | 1.000 |
| time_of_day_late_night | OR 0.55 [0.37, 0.81] | 0.003 | 1.000 |
| finds_other_attractive | OR 1.47 [0.99, 2.18] | 0.054 | 1.000 |
| knows_other | OR 2.12 [1.41, 3.18] | < 0.001 | 0.184 |
| is_lower_agent | OR 0.92 [0.62, 1.38] | 0.688 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.25 [0.86, 1.82] | 0.238 | 1.000 |
| condition[non_verbal] | OR 1.52 [0.97, 2.39] | 0.068 | 1.000 |
| condition[talk] | OR 0.86 [0.56, 1.34] | 0.517 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_slowed`** (agent): its first plan slows below its speed at the decision. Status: ok, n = 571, events = 381.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 2.81 [1.31, 6.06] | 0.008 | 1.000 |
| own_female | OR 0.58 [0.37, 0.91] | 0.018 | 1.000 |
| other_age_high | OR 2.20 [1.07, 4.55] | 0.032 | 1.000 |
| own_urgency | OR 0.52 [0.26, 1.03] | 0.059 | 1.000 |
| own_mobility_aid | OR 1.22 [0.61, 2.44] | 0.567 | 1.000 |
| own_load | OR 2.23 [1.19, 4.21] | 0.013 | 1.000 |
| own_distraction | OR 0.75 [0.37, 1.52] | 0.425 | 1.000 |
| own_assertiveness | OR 0.10 [0.05, 0.21] | < 0.001 | < 0.001 |
| own_residence | OR 1.07 [0.55, 2.07] | 0.842 | 1.000 |
| own_memory_note | OR 2.85 [1.34, 6.05] | 0.006 | 1.000 |
| other_mobility_aid | OR 2.01 [0.92, 4.38] | 0.079 | 1.000 |
| other_load | OR 2.08 [0.98, 4.41] | 0.057 | 1.000 |
| other_distraction | OR 1.97 [0.89, 4.38] | 0.094 | 1.000 |
| same_ethnicity | OR 1.19 [0.75, 1.89] | 0.460 | 1.000 |
| surroundings_busy | OR 1.19 [0.70, 2.01] | 0.527 | 1.000 |
| time_of_day_late_night | OR 1.90 [1.10, 3.29] | 0.021 | 1.000 |
| finds_other_attractive | OR 1.96 [1.23, 3.10] | 0.004 | 1.000 |
| knows_other | OR 2.77 [1.61, 4.75] | < 0.001 | 0.153 |
| is_lower_agent | OR 0.86 [0.54, 1.37] | 0.524 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.19 [0.76, 1.87] | 0.442 | 1.000 |
| condition[non_verbal] | OR 0.74 [0.42, 1.30] | 0.291 | 1.000 |
| condition[talk] | OR 1.04 [0.60, 1.81] | 0.882 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_stopped`** (agent): its first plan stops. Status: separation, n = 571, events = 3.

Left out of the model: other_female (collinear).

**`plan_backed_up`** (agent): its first plan backs up. Status: one value, n = 571, events = 0.

**`start_distance_m`** (agent): its first plan starts at this distance (plans that start so). Status: ok, n = 13.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | +1.125 [-0.412, +2.662] | 0.151 | 1.000 |
| own_female | +0.250 [-0.812, +1.312] | 0.644 | 1.000 |
| other_age_high | +0.375 [-0.950, +1.700] | 0.579 | 1.000 |
| own_urgency | -2.125 [-3.662, -0.588] | 0.007 | 1.000 |
| own_mobility_aid | +2.250 [+1.188, +3.312] | < 0.001 | 0.022 |
| own_distraction | +0.500 [-1.058, +2.058] | 0.529 | 1.000 |
| other_mobility_aid | -0.625 [-1.156, -0.094] | 0.021 | 1.000 |
| same_ethnicity | -0.375 [-1.700, +0.950] | 0.579 | 1.000 |
| geometry[layout=apart_20cm] | -0.125 [-0.656, +0.406] | 0.644 | 1.000 |

Left out of the model: other_female (collinear); own_load (constant); own_assertiveness (collinear); own_residence (collinear); own_memory_note (collinear); other_load (constant); other_distraction (collinear); surroundings_busy (collinear); time_of_day_late_night (collinear); finds_other_attractive (collinear); knows_other (collinear); is_lower_agent (collinear); condition[talk] (collinear).

**`signalled`** (agent): it signalled at least once (non-verbal and talk only). Status: ok, n = 384, events = 243.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.34 [0.12, 1.00] | 0.051 | 1.000 |
| own_female | OR 1.40 [0.81, 2.42] | 0.233 | 1.000 |
| other_age_high | OR 0.51 [0.15, 1.80] | 0.297 | 1.000 |
| own_urgency | OR 0.50 [0.19, 1.33] | 0.166 | 1.000 |
| own_mobility_aid | OR 2.19 [0.81, 5.91] | 0.123 | 1.000 |
| own_load | OR 0.82 [0.32, 2.08] | 0.669 | 1.000 |
| own_distraction | OR 1.69 [0.63, 4.56] | 0.299 | 1.000 |
| own_assertiveness | OR 13.55 [4.47, 41.07] | < 0.001 | 0.003 |
| own_residence | OR 3.77 [1.14, 12.43] | 0.030 | 1.000 |
| own_memory_note | OR 1.57 [0.61, 4.04] | 0.355 | 1.000 |
| other_mobility_aid | OR 5.36 [1.56, 18.41] | 0.008 | 1.000 |
| other_load | OR 1.09 [0.31, 3.80] | 0.889 | 1.000 |
| other_distraction | OR 0.74 [0.19, 2.93] | 0.670 | 1.000 |
| same_ethnicity | OR 1.42 [0.58, 3.45] | 0.443 | 1.000 |
| surroundings_busy | OR 0.49 [0.15, 1.59] | 0.233 | 1.000 |
| time_of_day_late_night | OR 3.30 [1.23, 8.84] | 0.017 | 1.000 |
| finds_other_attractive | OR 6.53 [2.68, 15.89] | < 0.001 | 0.024 |
| knows_other | OR 444.57 [47.45, 4164.92] | < 0.001 | < 0.001 |
| is_lower_agent | OR 0.62 [0.34, 1.15] | 0.127 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.82 [0.77, 4.28] | 0.173 | 1.000 |
| condition[talk] | OR 3.62 [1.55, 8.44] | 0.003 | 1.000 |

Left out of the model: other_female (collinear).

**`resolved_plan_only`** (session): resolved in `plan_only` (the Step 1 measure). Status: ok, n = 288, events = 152.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 1.55 [0.91, 2.64] | 0.107 | 1.000 |
| gender_pair[p1_male] | OR 1.43 [0.84, 2.44] | 0.192 | 1.000 |
| urgency[p1] | OR 0.71 [0.42, 1.20] | 0.200 | 1.000 |
| mobility_aid[p1] | OR 0.82 [0.48, 1.40] | 0.471 | 1.000 |
| load[p1] | OR 0.60 [0.35, 1.01] | 0.057 | 1.000 |
| distraction[p1] | OR 1.53 [0.90, 2.61] | 0.118 | 1.000 |
| assertiveness[p1] | OR 0.75 [0.44, 1.28] | 0.295 | 1.000 |
| residence[p1] | OR 0.67 [0.39, 1.14] | 0.138 | 1.000 |
| memory_note[p1] | OR 1.28 [0.75, 2.19] | 0.362 | 1.000 |
| ethnicity_pair[different] | OR 0.84 [0.51, 1.39] | 0.500 | 1.000 |
| surroundings[busy] | OR 0.98 [0.57, 1.67] | 0.928 | 1.000 |
| time_of_day[late_night] | OR 0.98 [0.58, 1.68] | 0.954 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 1.08 [0.64, 1.82] | 0.762 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 0.97 [0.57, 1.65] | 0.897 | 1.000 |
| familiarity[strangers] | OR 0.96 [0.56, 1.64] | 0.877 | 1.000 |
| mapping[p1_higher] | OR 0.93 [0.55, 1.58] | 0.789 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.97 [0.60, 1.58] | 0.905 | 1.000 |
| condition[non_verbal] | OR 1.05 [0.58, 1.89] | 0.882 | 1.000 |
| condition[talk] | OR 0.80 [0.45, 1.44] | 0.458 | 1.000 |

**`resolved_plan_orca`** (session): resolved in `plan_orca`. Status: ok, n = 288, events = 158.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 1.42 [0.83, 2.41] | 0.199 | 1.000 |
| gender_pair[p1_male] | OR 1.37 [0.80, 2.34] | 0.251 | 1.000 |
| urgency[p1] | OR 0.76 [0.45, 1.29] | 0.308 | 1.000 |
| mobility_aid[p1] | OR 0.66 [0.39, 1.13] | 0.128 | 1.000 |
| load[p1] | OR 0.57 [0.33, 0.96] | 0.035 | 1.000 |
| distraction[p1] | OR 1.47 [0.86, 2.50] | 0.155 | 1.000 |
| assertiveness[p1] | OR 0.82 [0.48, 1.39] | 0.454 | 1.000 |
| residence[p1] | OR 0.80 [0.47, 1.35] | 0.402 | 1.000 |
| memory_note[p1] | OR 1.24 [0.72, 2.11] | 0.439 | 1.000 |
| ethnicity_pair[different] | OR 0.84 [0.51, 1.39] | 0.507 | 1.000 |
| surroundings[busy] | OR 1.17 [0.68, 1.99] | 0.571 | 1.000 |
| time_of_day[late_night] | OR 1.06 [0.62, 1.82] | 0.819 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 1.09 [0.65, 1.84] | 0.734 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 1.01 [0.59, 1.72] | 0.966 | 1.000 |
| familiarity[strangers] | OR 1.14 [0.67, 1.95] | 0.628 | 1.000 |
| mapping[p1_higher] | OR 1.06 [0.63, 1.80] | 0.820 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.90 [0.55, 1.47] | 0.670 | 1.000 |
| condition[non_verbal] | OR 1.09 [0.61, 1.97] | 0.767 | 1.000 |
| condition[talk] | OR 0.88 [0.49, 1.57] | 0.656 | 1.000 |

**`resolved_by_llm`** (session): resolved in `plan_only` before ORCA took over. Status: ok, n = 288, events = 143.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 1.43 [0.83, 2.43] | 0.195 | 1.000 |
| gender_pair[p1_male] | OR 1.51 [0.88, 2.58] | 0.135 | 1.000 |
| urgency[p1] | OR 0.77 [0.45, 1.31] | 0.332 | 1.000 |
| mobility_aid[p1] | OR 0.83 [0.48, 1.42] | 0.491 | 1.000 |
| load[p1] | OR 0.52 [0.30, 0.88] | 0.015 | 1.000 |
| distraction[p1] | OR 1.61 [0.94, 2.74] | 0.083 | 1.000 |
| assertiveness[p1] | OR 0.66 [0.39, 1.14] | 0.134 | 1.000 |
| residence[p1] | OR 0.79 [0.46, 1.35] | 0.388 | 1.000 |
| memory_note[p1] | OR 1.29 [0.75, 2.22] | 0.349 | 1.000 |
| ethnicity_pair[different] | OR 0.77 [0.46, 1.26] | 0.296 | 1.000 |
| surroundings[busy] | OR 0.93 [0.55, 1.60] | 0.804 | 1.000 |
| time_of_day[late_night] | OR 1.04 [0.61, 1.78] | 0.895 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | OR 1.09 [0.64, 1.83] | 0.754 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | OR 0.98 [0.57, 1.67] | 0.932 | 1.000 |
| familiarity[strangers] | OR 1.19 [0.69, 2.04] | 0.524 | 1.000 |
| mapping[p1_higher] | OR 0.92 [0.54, 1.57] | 0.758 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.98 [0.60, 1.61] | 0.945 | 1.000 |
| condition[non_verbal] | OR 1.57 [0.87, 2.85] | 0.137 | 1.000 |
| condition[talk] | OR 1.20 [0.66, 2.16] | 0.548 | 1.000 |

**`decision_points`** (session): decision points of both people. Status: ok, n = 288.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | -0.116 [-0.317, +0.085] | 0.257 | 1.000 |
| gender_pair[p1_male] | -0.103 [-0.312, +0.105] | 0.331 | 1.000 |
| urgency[p1] | -0.033 [-0.237, +0.172] | 0.753 | 1.000 |
| mobility_aid[p1] | +0.111 [-0.090, +0.311] | 0.279 | 1.000 |
| load[p1] | +0.153 [-0.045, +0.351] | 0.130 | 1.000 |
| distraction[p1] | +0.063 [-0.137, +0.264] | 0.537 | 1.000 |
| assertiveness[p1] | +0.140 [-0.063, +0.342] | 0.177 | 1.000 |
| residence[p1] | +0.116 [-0.083, +0.315] | 0.254 | 1.000 |
| memory_note[p1] | -0.014 [-0.221, +0.193] | 0.892 | 1.000 |
| ethnicity_pair[different] | +0.007 [-0.207, +0.222] | 0.947 | 1.000 |
| surroundings[busy] | +0.038 [-0.167, +0.243] | 0.716 | 1.000 |
| time_of_day[late_night] | -0.069 [-0.273, +0.135] | 0.509 | 1.000 |
| attractiveness_0_sees_1[unremarkable] | -0.104 [-0.305, +0.098] | 0.313 | 1.000 |
| attractiveness_1_sees_0[unremarkable] | -0.034 [-0.238, +0.170] | 0.744 | 1.000 |
| familiarity[strangers] | -0.163 [-0.361, +0.035] | 0.107 | 1.000 |
| mapping[p1_higher] | +0.076 [-0.123, +0.275] | 0.456 | 1.000 |
| geometry[layout=apart_20cm] | -0.018 [-0.231, +0.195] | 0.868 | 1.000 |
| condition[non_verbal] | +3.365 [+3.153, +3.576] | < 0.001 | < 0.001 |
| condition[talk] | +3.458 [+3.235, +3.682] | < 0.001 | < 0.001 |

## 2. Decision tree

Predicts **`passed_first`** per agent, depth at most 3, on 350 rows (the predictors that vary, with condition and geometry). Figure: `tree.png`.

- Accuracy on the rows it was grown on: 0.860; always guessing the commoner outcome: 0.843.
- Accuracy on held-out sessions (5-fold, grouped by session): 0.837.
- Splits on: `knows_other`, `other_mobility_aid`, `own_assertiveness`, `own_distraction`, `own_female`, `own_residence`.

A tree no better on held-out sessions than the commoner outcome has found no usable pattern.

```
|--- own_assertiveness <= 0.50
|   |--- own_distraction <= 0.50
|   |   |--- other_mobility_aid <= 0.50
|   |   |   |--- weights: [157.00, 10.00] class: 0
|   |   |--- other_mobility_aid >  0.50
|   |   |   |--- weights: [62.00, 9.00] class: 0
|   |--- own_distraction >  0.50
|   |   |--- own_residence <= 0.50
|   |   |   |--- weights: [14.00, 4.00] class: 0
|   |   |--- own_residence >  0.50
|   |   |   |--- weights: [13.00, 6.00] class: 0
|--- own_assertiveness >  0.50
|   |--- knows_other <= 0.50
|   |   |--- own_female <= 0.50
|   |   |   |--- weights: [15.00, 7.00] class: 0
|   |   |--- own_female >  0.50
|   |   |   |--- weights: [7.00, 13.00] class: 1
|   |--- knows_other >  0.50
|   |   |--- own_distraction <= 0.50
|   |   |   |--- weights: [15.00, 6.00] class: 0
|   |   |--- own_distraction >  0.50
|   |   |   |--- weights: [12.00, 0.00] class: 0
```

## 3. Counterfactual pairs against the noise floor

The noise floor is the flip rate between repeats of one cell of the exact-repeat set (identical prompts), with a bootstrap 95% interval over cells. A pair's flip rate (Wilson 95% interval) counts as evidence only where its lower end is above the noise floor's upper end, in the same condition. Components: `who_passed_first`, `passing_side`, `stopped`, `backed_up`, `behaviour` (`behaviour` is all of them together).

### The noise floor

| component | subset | cells | pairs | flips | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| who_passed_first | all | 24 | 72 | 50 | 0.694 | 0.583 | 0.778 |
| who_passed_first | independent | 8 | 24 | 17 | 0.708 | 0.458 | 0.917 |
| who_passed_first | non_verbal | 8 | 24 | 17 | 0.708 | 0.500 | 0.917 |
| who_passed_first | talk | 8 | 24 | 16 | 0.667 | 0.667 | 0.667 |
| passing_side | all | 24 | 72 | 32 | 0.444 | 0.333 | 0.556 |
| passing_side | independent | 8 | 24 | 8 | 0.333 | 0.083 | 0.583 |
| passing_side | non_verbal | 8 | 24 | 12 | 0.500 | 0.333 | 0.667 |
| passing_side | talk | 8 | 24 | 12 | 0.500 | 0.250 | 0.667 |
| stopped | all | 24 | 72 | 0 | 0 | 0 | 0 |
| stopped | independent | 8 | 24 | 0 | 0 | 0 | 0 |
| stopped | non_verbal | 8 | 24 | 0 | 0 | 0 | 0 |
| stopped | talk | 8 | 24 | 0 | 0 | 0 | 0 |
| backed_up | all | 24 | 72 | 0 | 0 | 0 | 0 |
| backed_up | independent | 8 | 24 | 0 | 0 | 0 | 0 |
| backed_up | non_verbal | 8 | 24 | 0 | 0 | 0 | 0 |
| backed_up | talk | 8 | 24 | 0 | 0 | 0 | 0 |
| behaviour | all | 24 | 72 | 60 | 0.833 | 0.736 | 0.917 |
| behaviour | independent | 8 | 24 | 22 | 0.917 | 0.792 | 1 |
| behaviour | non_verbal | 8 | 24 | 19 | 0.792 | 0.542 | 0.958 |
| behaviour | talk | 8 | 24 | 19 | 0.792 | 0.708 | 0.917 |

### The counterfactual pairs

| factor | component | subset | pairs | flips | rate | ci_low | ci_high | noise_rate | noise_high | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attractiveness_0_sees_1 | who_passed_first | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.694 | 0.778 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | independent | 2 | 0 | 0 | 0 | 0.658 | 0.708 | 0.917 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.708 | 0.917 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.667 | 0.667 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.694 | 0.778 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | independent | 2 | 0 | 0 | 0 | 0.658 | 0.708 | 0.917 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.708 | 0.917 | not distinguishable from the noise floor |
| ethnicity_pair | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.667 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | all | 6 | 5 | 0.833 | 0.436 | 0.970 | 0.694 | 0.778 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.708 | 0.917 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.708 | 0.917 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | who_passed_first | talk | 2 | 2 | 1 | 0.342 | 1 | 0.667 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.694 | 0.778 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.708 | 0.917 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.708 | 0.917 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | who_passed_first | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.667 | 0.667 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | all | 6 | 1 | 0.167 | 0.030 | 0.564 | 0.444 | 0.556 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | independent | 2 | 0 | 0 | 0 | 0.658 | 0.333 | 0.583 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.500 | 0.667 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | passing_side | talk | 2 | 0 | 0 | 0 | 0.658 | 0.500 | 0.667 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.444 | 0.556 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.333 | 0.583 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.500 | 0.667 | not distinguishable from the noise floor |
| ethnicity_pair | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.500 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | all | 6 | 2 | 0.333 | 0.097 | 0.700 | 0.444 | 0.556 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.333 | 0.583 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | non_verbal | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.500 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | passing_side | talk | 2 | 0 | 0 | 0 | 0.658 | 0.500 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | all | 6 | 4 | 0.667 | 0.300 | 0.903 | 0.444 | 0.556 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.333 | 0.583 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.500 | 0.667 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | passing_side | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.500 | 0.667 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| ethnicity_pair | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | all | 6 | 0 | 0 | 0 | 0.390 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | independent | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | non_verbal | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | stopped | talk | 2 | 0 | 0 | 0 | 0.658 | 0 | 0 | not distinguishable from the noise floor |
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
| attractiveness_0_sees_1 | behaviour | all | 6 | 3 | 0.500 | 0.188 | 0.812 | 0.833 | 0.917 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | independent | 2 | 0 | 0 | 0 | 0.658 | 0.917 | 1 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.792 | 0.958 | not distinguishable from the noise floor |
| attractiveness_0_sees_1 | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.792 | 0.917 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | all | 6 | 5 | 0.833 | 0.436 | 0.970 | 0.833 | 0.917 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.917 | 1 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.792 | 0.958 | not distinguishable from the noise floor |
| ethnicity_pair | behaviour | talk | 2 | 2 | 1 | 0.342 | 1 | 0.792 | 0.917 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | all | 6 | 5 | 0.833 | 0.436 | 0.970 | 0.833 | 0.917 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | independent | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.917 | 1 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.792 | 0.958 | not distinguishable from the noise floor |
| p2_ethnicity:chinese->indian | behaviour | talk | 2 | 2 | 1 | 0.342 | 1 | 0.792 | 0.917 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | all | 6 | 5 | 0.833 | 0.436 | 0.970 | 0.833 | 0.917 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | independent | 2 | 2 | 1 | 0.342 | 1 | 0.917 | 1 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | non_verbal | 2 | 2 | 1 | 0.342 | 1 | 0.792 | 0.958 | not distinguishable from the noise floor |
| p2_ethnicity:malay->indian | behaviour | talk | 2 | 1 | 0.500 | 0.095 | 0.905 | 0.792 | 0.917 | not distinguishable from the noise floor |

## 4. Behaviour stability

Per cell of the exact-repeat set: the share of its repeats with the commonest outcome (1: every repeat the same). A cell whose commonest behaviour came up in fewer than 0.75 of its repeats is a coin flip, and RF-11 should claim no rule there.

| Component | Cells | Mean | Lowest | Cells with every repeat the same |
| --- | --- | --- | --- | --- |
| who_passed_first | 24 | 0.611 | 0.333 | 2 |
| passing_side | 24 | 0.778 | 0.667 | 8 |
| stopped | 24 | 1 | 1 | 24 |
| backed_up | 24 | 1 | 1 | 24 |
| behaviour | 24 | 0.486 | 0.333 | 1 |

### Coin-flip cells: 23 of 24

| Cell | Condition | Repeats | Stability | Who passed first | Commonest behaviour |
| --- | --- | --- | --- | --- | --- |
| I_head_on_02dfbadb_02604456 | independent | 3 | 0.667 | 1 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_1caa9a84 | independent | 3 | 0.667 | 0.667 | p1\|left\|left\|0\|0\|0\|0 |
| I_head_on_02dfbadb_55c9ae40 | independent | 3 | 0.333 | 0.333 | together\|right\|right\|0\|0\|0\|0 |
| I_head_on_02dfbadb_8ea28db3 | independent | 3 | 0.333 | 0.667 | p1\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_3dee0df5 | independent | 3 | 0.333 | 0.333 | p2\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_800a3b04 | independent | 3 | 0.333 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_9b752a36 | independent | 3 | 0.333 | 0.667 | p1\|left\|left\|0\|0\|0\|0 |
| I_head_on_de176842_c36d5d49 | independent | 3 | 0.333 | 0.333 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_02dfbadb_02604456 | non_verbal | 3 | 0.333 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_1caa9a84 | non_verbal | 3 | 0.333 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_55c9ae40 | non_verbal | 3 | 0.667 | 0.667 | together\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_3dee0df5 | non_verbal | 3 | 0.333 | 0.333 | together\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_800a3b04 | non_verbal | 3 | 0.333 | 0.333 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_9b752a36 | non_verbal | 3 | 0.333 | 0.333 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_de176842_c36d5d49 | non_verbal | 3 | 0.667 | 0.667 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_02604456 | talk | 3 | 0.667 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_1caa9a84 | talk | 3 | 0.667 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_02dfbadb_55c9ae40 | talk | 3 | 0.333 | 0.667 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_02dfbadb_8ea28db3 | talk | 3 | 0.667 | 0.667 | -\|left\|left\|0\|0\|0\|0 |
| T_head_on_de176842_3dee0df5 | talk | 3 | 0.333 | 0.667 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_800a3b04 | talk | 3 | 0.667 | 0.667 | -\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_9b752a36 | talk | 3 | 0.333 | 0.667 | together\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_c36d5d49 | talk | 3 | 0.667 | 0.667 | together\|right\|right\|0\|0\|0\|0 |

## 5. The factor-to-decision mapping

Every observed combination of `own_age_high`, `own_female`, `other_age_high`, `other_female`, `own_urgency`, `own_mobility_aid`, `own_load`, `own_distraction`, `own_assertiveness`, `own_residence`, `own_memory_note`, `other_mobility_aid`, `other_load`, `other_distraction`, `same_ethnicity`, `surroundings_busy`, `time_of_day_late_night`, `finds_other_attractive`, `knows_other`, `is_lower_agent`, `geometry`, per condition, from the agent's point of view: **402 combinations** in `mapping.csv`, each with its rows and, per outcome, how many are known and the share that are 1. Read the counts with the shares: a combination seen once gives 0 or 1 from one row. The 25 combinations with the most rows:

| condition | own_age_high | own_female | other_age_high | other_female | own_urgency | own_mobility_aid | own_load | own_distraction | own_assertiveness | own_residence | own_memory_note | other_mobility_aid | other_load | other_distraction | same_ethnicity | surroundings_busy | time_of_day_late_night | finds_other_attractive | knows_other | is_lower_agent | geometry | rows | p_passed_first | p_kept_left | p_stopped | p_backed_up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 5 | 0 | 0.800 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 5 | 0.250 | 0.600 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 5 | 0 | 0 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 5 | 0 | 0.400 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 5 | 0.200 | 0.600 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 5 | 0 | 0.600 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0.750 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.750 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0.333 | 0.500 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.750 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0 | 1 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 0.750 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0.333 | 0.500 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.500 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 1 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | layout=apart_20cm | 4 | 0 | 0.750 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=aligned | 4 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | layout=apart_20cm | 4 | 0 | 0.750 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | layout=apart_20cm | 3 | 0 | 0.667 | 0 | 0 |

## 6. Stated against measured

How often each factor is named in the agents' private `reason` (keyword codebook `reasons_v1`), beside its strongest measured effect in the per-agent models of all conditions together. Named often: in at least 0.1 of the reasons. Measured: a term significant after Holm's correction. A factor named often with no measured effect, or the reverse, is a finding.

| Factor | Share of reasons naming it | Measured effect | Outcome | Term | Estimate (OR or coef.) | Holm p | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| age | 0.193 | no | kept_left | other_age_high | 0.354 | 0.141 | named often, no measured effect |
| gender | 0.044 | no | passed_first | own_female | 1.492 | 1.000 | neither |
| urgency | 0.122 | no | passed_first | own_urgency | 1.252 | 1.000 | named often, no measured effect |
| mobility_aid | 0.245 | yes | start_distance_m | own_mobility_aid | 2.250 | 0.022 | named often, and a measured effect |
| load | 0.286 | no | passed_first | own_load | 0.787 | 1.000 | named often, no measured effect |
| distraction | 0.225 | no | passed_first | own_distraction | 2.183 | 1.000 | named often, no measured effect |
| assertiveness | 0.243 | yes | plan_slowed | own_assertiveness | 0.104 | < 0.001 | named often, and a measured effect |
| residence | 0.003 | no | passed_first | own_residence | 1.295 | 1.000 | neither |
| memory_note | 0.132 | no | passed_first | own_memory_note | 0.977 | 1.000 | named often, no measured effect |
| surroundings | 0.076 | no | passed_first | surroundings_busy | 1.524 | 1.000 | neither |
| time_of_day | 0.015 | no | passed_first | time_of_day_late_night | 0.945 | 1.000 | neither |
| perceived_attractiveness | 0.028 | yes | signalled | finds_other_attractive | 6.527 | 0.024 | a measured effect, rarely named |
| familiarity | 0.058 | yes | signalled | knows_other | 444.571 | < 0.001 | a measured effect, rarely named |
| ethnicity_pair | - | no | passed_first | same_ethnicity | 0.743 | 1.000 | neither |
| is_lower_agent | - | no | passed_first | is_lower_agent | 0.677 | 1.000 | neither |

**Where saying and doing disagree:** `age` (named often, no measured effect), `urgency` (named often, no measured effect), `load` (named often, no measured effect), `distraction` (named often, no measured effect), `memory_note` (named often, no measured effect), `perceived_attractiveness` (a measured effect, rarely named), `familiarity` (a measured effect, rarely named).

### The debriefs' kind of basis

One per prompted agent (D8); every source is unchecked until RF-14.

| kind | independent | non_verbal | talk | all |
| --- | --- | --- | --- | --- |
| local_custom | 24 | 12 | 24 | 60 |
| habit | 64 | 79 | 67 | 210 |
| common_sense | 96 | 99 | 98 | 293 |
| none | 3 | 2 | 3 | 8 |
| (none given) | 5 | 0 | 0 | 5 |
| all | 192 | 192 | 192 | 576 |

## 7. Intent against plan

Each readable intent coded by the keyword codebook `intent_v2` (keep to a side, slow down, stop and wait, back up, carry on, or `other`), against the plan coded from its steps. A mismatch is an intent that says something the plan does not do. Intents coded `other` and unreadable replies are left out of the rate. A high rate means the structured plan cannot be trusted on its own (RF-11).

| subset | decision_points | unreadable | uncoded | compared | mismatches | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 1039 | 17 | 122 | 900 | 209 | 0.232 | 0.206 | 0.261 |
| non_verbal | 515 | 11 | 58 | 446 | 99 | 0.222 | 0.186 | 0.263 |
| talk | 524 | 6 | 64 | 454 | 110 | 0.242 | 0.205 | 0.284 |

### Examples of mismatches

| condition | session_id | agent_id | intent | plan_categories | plan_side | why |
| --- | --- | --- | --- | --- | --- | --- |
| non_verbal | N_head_on_02dfbadb_2ec958bb_r1 | 1 | Keep walking to the supermarket at my usual pace, looking up enough to avoid another collision | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_5767d932_r1 | 0 | Keep heading to the emergency room, glance up to avoid another collision | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_c36d5d49_r1 | 0 | Acknowledge my classmate and keep moving briskly toward the emergency room, passing on his right | carry_on | none | intent says keep_to_side, the plan does not |
| talk | T_head_on_02dfbadb_cb859069_r1 | 0 | Keep walking to the supermarket, ready to give way to the elderly woman. | keep_to_side;slow_down | left | intent says carry_on, the plan does not |
| non_verbal | N_head_on_de176842_8ea28db3_r1 | 1 | Keep walking to the supermarket and give way to my classmate with the cane. | keep_to_side;slow_down | both | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_68f09b97_r1 | 0 | Keep walking steadily on my side of the passage and let the oncoming woman pass me on her own side. | carry_on | none | intent says keep_to_side, the plan does not |
| talk | T_head_on_de176842_68f09b97_r1 | 0 | Keep my steady line so the young woman passes on her side, since she has already moved over to my right | carry_on | none | intent says keep_to_side, the plan does not |
| talk | T_head_on_de176842_68f09b97_r1 | 1 | Keep to the right side of the passage and continue toward the supermarket, staying clear of the wall on my right | keep_to_side | left | intent says right, the plan turns left |
| talk | T_head_on_de176842_b59c2831_r1 | 1 | Keep walking toward the emergency room while glancing up from my phone to notice Person 1 and be ready to give way. | keep_to_side;slow_down | right | intent says carry_on, the plan does not |
| talk | T_head_on_de176842_b59c2831_r1 | 0 | Keep to my right, acknowledge the thanks, and pass comfortably | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |

### Intents the codebook could not place (the commonest)

- 2 x "Greet my classmate and give way so he can pass with his cane while his attention is on his phone"
- 2 x "Give the elderly woman with the cane and suitcase plenty of room and let her pass safely"
- 1 x "Keep to my line and watch the oncoming man so I don't get bumped again"
- 1 x "Keep moving toward the emergency room while giving the oncoming man a clear lane, avoiding another collision"
- 1 x "Greet the person I know from class and keep moving briskly toward the emergency room."

## 8. Real ethnicity

Descriptive. A difference between groups here is the model's behaviour towards people it was told are of a group, not a fact about those groups, and no rule may read ethnicity (`llm_negotiation/docs/ethnicity.md`).

### By group, the other's as told (unweighted agent rows)

| own | other_as_told | n | passed_first | kept_left | stopped | backed_up | plan_slowed | plan_left | plan_right |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chinese | chinese | 72 | 0.119 | 0.389 | 0 | 0 | 0.722 | 0.236 | 0.417 |
| chinese | malay | 30 | 0.167 | 0.533 | 0 | 0 | 0.517 | 0.310 | 0.379 |
| chinese | indian | 36 | 0.091 | 0.528 | 0 | 0 | 0.583 | 0.139 | 0.167 |
| chinese | others | 15 | 0.111 | 0.200 | 0 | 0 | 0.733 | 0.133 | 0.333 |
| malay | chinese | 30 | 0.056 | 0.533 | 0 | 0 | 0.733 | 0.433 | 0.133 |
| malay | malay | 84 | 0.179 | 0.548 | 0 | 0 | 0.560 | 0.321 | 0.333 |
| malay | indian | 24 | 0.091 | 0.583 | 0 | 0 | 0.750 | 0.292 | 0.458 |
| malay | others | 24 | 0.231 | 0.458 | 0.042 | 0 | 0.522 | 0.304 | 0.217 |
| indian | chinese | 36 | 0.227 | 0.528 | 0 | 0 | 0.556 | 0.222 | 0.333 |
| indian | malay | 24 | 0 | 0.583 | 0 | 0 | 0.833 | 0.167 | 0.500 |
| indian | indian | 72 | 0.159 | 0.361 | 0 | 0 | 0.771 | 0.243 | 0.471 |
| indian | others | 15 | 0.500 | 0.467 | 0 | 0 | 0.533 | 0.133 | 0.600 |
| others | chinese | 15 | 0.556 | 0.200 | 0 | 0 | 0.667 | 0.200 | 0.400 |
| others | malay | 24 | 0.077 | 0.458 | 0 | 0 | 0.875 | 0.333 | 0.375 |
| others | indian | 15 | 0.083 | 0.467 | 0 | 0 | 0.786 | 0.143 | 0.357 |
| others | others | 60 | 0.105 | 0.300 | 0 | 0 | 0.650 | 0.217 | 0.533 |

Each share is over the rows where the outcome is defined (`<outcome>_n` in `ethnicity_groups.csv`).

### Weighted back to random resident pairs

Each session weighted by `ethnicity_weight`, so that the sessions stand for two residents met at random (each at the resident shares; residents only). Use the weighted rate for a population-level figure; the effective number of sessions is what the weighting leaves.

| outcome | sessions | unweighted | weighted | effective_sessions |
| --- | --- | --- | --- | --- |
| resolved_plan_only | 288 | 0.528 | 0.520 | 90.075 |
| resolved_plan_orca | 288 | 0.549 | 0.563 | 90.075 |
| resolved_by_llm | 288 | 0.497 | 0.491 | 90.075 |

## How to read this report

- **An effect here is an effect on what the LLM agents did**, in this design: a screen, so main effects are estimated clear of two-factor interactions only when the design is a resolution IV fraction (`llm_negotiation/docs/screening-designs.md`, section 3).
- **Separation** (an outcome predicted perfectly by some predictor) leaves a model with no finite estimate; it is listed, not reported as an effect. Rare outcomes with many factors cause it: D14 aims at about 10 events per factor.
- **The mapping is sparse** when there are many factors: most combinations are seen once or twice.
- **The codebooks are drafts** until RF-9's pilot (`analysis/codebooks/`): a mention or a coded intent is a keyword match, not a reading of the text.
