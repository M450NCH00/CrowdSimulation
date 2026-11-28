# Factor analysis of a resolution experiment (RF-8)

## Inputs

- `llm_negotiation/runs/rf_pilot_v2/outcomes.csv`

- Sessions analysed (completed): **72** (independent: 24, non_verbal: 24, talk: 24); left out: none.
- Rows, one per agent per session: **144**.
- Physical outcomes of mode **`plan_only`** (the Step 1 measure).
- Client: deepseek.
- Predictors that vary: `own_age_high`, `own_female`, `other_age_high`, `other_female`, `is_lower_agent`; constant, left out: `own_demographics_hidden`, `other_demographics_unseen`, `own_urgency`.
- Holm's correction at alpha = 0.05, over every term of every model in this report (the chance of any false positive in it is at most alpha); seed 63; codebooks `intent_v2` and `reasons_v1`.

**The other's factors are as the agent was told them.** A factor of the other person counts only if it was printed to the agent at one or more of its decision points (`analysis/load.py`).

## 1. Factor effects

Logistic regression per binary outcome (odds ratios, OR, with 95% intervals), linear regression for a continuous one (coefficients). Per-agent models cluster standard errors by session; per-session models use HC1. Holm's correction runs over every term of every model in this report (the chance of any false positive in it is at most alpha). `all` is every condition together, with condition as a factor. A model whose outcome is separated by the predictors has no finite estimate and is listed as `separation`, never read as an effect.

### Significant after Holm's correction

| Outcome | Subset | Term | Effect [95% CI] | p | Holm p | n |
| --- | --- | --- | --- | --- | --- | --- |
| decision_points | all | condition[talk] | +3.667 [+3.220, +4.114] | < 0.001 | < 0.001 | 72 |
| decision_points | all | condition[non_verbal] | +3.458 [+2.981, +3.936] | < 0.001 | < 0.001 | 72 |

### Every model

| outcome | level | subset | status | n | events | clusters | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| passed_first | agent | all | ok | 50 | 10 | 25 |  |
| kept_left | agent | all | ok | 144 | 32 | 72 |  |
| stopped | agent | all | separation | 144 | 1 | 72 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | all | one value | 144 | 0 | - | every row is 0 |
| plan_left | agent | all | separation | 141 | 3 | 72 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_right | agent | all | ok | 141 | 63 | 72 |  |
| plan_slowed | agent | all | ok | 141 | 28 | 72 |  |
| plan_stopped | agent | all | one value | 141 | 0 | - | every row is 0 |
| plan_backed_up | agent | all | one value | 141 | 0 | - | every row is 0 |
| start_distance_m | agent | all | no data | 3 | - | - | 3 rows for 3 parameters |
| signalled | agent | all | ok | 96 | 6 | 48 |  |
| resolved_plan_only | session | all | ok | 72 | 17 | - |  |
| resolved_plan_orca | session | all | ok | 72 | 21 | - |  |
| resolved_by_llm | session | all | ok | 72 | 17 | - |  |
| decision_points | session | all | ok | 72 | - | - |  |
| passed_first | agent | independent | separation | 24 | 3 | 12 | the outcome is (nearly) separated by the predictors: no finite estimate |
| kept_left | agent | independent | ok | 48 | 12 | 24 |  |
| stopped | agent | independent | one value | 48 | 0 | - | every row is 0 |
| backed_up | agent | independent | one value | 48 | 0 | - | every row is 0 |
| plan_left | agent | independent | separation | 45 | 1 | 24 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_right | agent | independent | ok | 45 | 17 | 24 |  |
| plan_slowed | agent | independent | ok | 45 | 7 | 24 |  |
| plan_stopped | agent | independent | one value | 45 | 0 | - | every row is 0 |
| plan_backed_up | agent | independent | one value | 45 | 0 | - | every row is 0 |
| start_distance_m | agent | independent | no data | 0 | - | - |  |
| signalled | agent | independent | no data | 0 | - | - |  |
| resolved_plan_only | session | independent | ok | 24 | 8 | - |  |
| resolved_plan_orca | session | independent | ok | 24 | 8 | - |  |
| resolved_by_llm | session | independent | ok | 24 | 8 | - |  |
| decision_points | session | independent | one value | 24 | - | - | every row is 2 |
| passed_first | agent | non_verbal | separation | 16 | 5 | 8 | the outcome is (nearly) separated by the predictors: no finite estimate |
| kept_left | agent | non_verbal | separation | 48 | 6 | 24 | the outcome is (nearly) separated by the predictors: no finite estimate |
| stopped | agent | non_verbal | separation | 48 | 1 | 24 | the outcome is (nearly) separated by the predictors: no finite estimate |
| backed_up | agent | non_verbal | one value | 48 | 0 | - | every row is 0 |
| plan_left | agent | non_verbal | separation | 48 | 1 | 24 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_right | agent | non_verbal | ok | 48 | 21 | 24 |  |
| plan_slowed | agent | non_verbal | ok | 48 | 10 | 24 |  |
| plan_stopped | agent | non_verbal | one value | 48 | 0 | - | every row is 0 |
| plan_backed_up | agent | non_verbal | one value | 48 | 0 | - | every row is 0 |
| start_distance_m | agent | non_verbal | no data | 3 | - | - | 3 rows for 3 parameters |
| signalled | agent | non_verbal | separation | 48 | 3 | 24 | the outcome is (nearly) separated by the predictors: no finite estimate |
| resolved_plan_only | session | non_verbal | ok | 24 | 5 | - |  |
| resolved_plan_orca | session | non_verbal | ok | 24 | 8 | - |  |
| resolved_by_llm | session | non_verbal | ok | 24 | 5 | - |  |
| decision_points | session | non_verbal | ok | 24 | - | - |  |
| passed_first | agent | talk | separation | 10 | 2 | 5 | the outcome is (nearly) separated by the predictors: no finite estimate |
| kept_left | agent | talk | separation | 48 | 14 | 24 | the outcome is (nearly) separated by the predictors: no finite estimate |
| stopped | agent | talk | one value | 48 | 0 | - | every row is 0 |
| backed_up | agent | talk | one value | 48 | 0 | - | every row is 0 |
| plan_left | agent | talk | separation | 48 | 1 | 24 | the outcome is (nearly) separated by the predictors: no finite estimate |
| plan_right | agent | talk | ok | 48 | 25 | 24 |  |
| plan_slowed | agent | talk | ok | 48 | 11 | 24 |  |
| plan_stopped | agent | talk | one value | 48 | 0 | - | every row is 0 |
| plan_backed_up | agent | talk | one value | 48 | 0 | - | every row is 0 |
| start_distance_m | agent | talk | no data | 0 | - | - |  |
| signalled | agent | talk | separation | 48 | 3 | 24 | the outcome is (nearly) separated by the predictors: no finite estimate |
| resolved_plan_only | session | talk | separation | 24 | 4 | - | the outcome is (nearly) separated by the predictors: no finite estimate |
| resolved_plan_orca | session | talk | ok | 24 | 5 | - |  |
| resolved_by_llm | session | talk | separation | 24 | 4 | - | the outcome is (nearly) separated by the predictors: no finite estimate |
| decision_points | session | talk | ok | 24 | - | - |  |

### Each outcome, all conditions together

Per outcome: what it is, and every term of the pooled model (the per-condition terms are in `effects_terms.csv`).

**`passed_first`** (agent): left the conflict zone first (physical; `together` counts as not first). Status: ok, n = 50, events = 10.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 1.27 [0.24, 6.58] | 0.779 | 1.000 |
| own_female | OR 0.63 [0.14, 2.90] | 0.557 | 1.000 |
| other_age_high | OR 0.47 [0.06, 3.60] | 0.468 | 1.000 |
| is_lower_agent | OR 1.77 [0.36, 8.72] | 0.481 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.24 [0.03, 1.73] | 0.158 | 1.000 |
| condition[non_verbal] | OR 2.78 [0.67, 11.48] | 0.157 | 1.000 |
| condition[talk] | OR 1.23 [0.11, 13.08] | 0.866 | 1.000 |

Left out of the model: other_female (collinear).

**`kept_left`** (agent): kept to its own left at the closest approach (physical; rows where the two were not abreast are left out). Status: ok, n = 144, events = 32.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.41 [0.11, 1.57] | 0.193 | 1.000 |
| own_female | OR 1.00 [1.00, 1.00] | 0.983 | 1.000 |
| other_age_high | OR 0.41 [0.11, 1.57] | 0.193 | 1.000 |
| is_lower_agent | OR 1.00 [1.00, 1.00] | 0.152 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.53 [0.14, 1.98] | 0.342 | 1.000 |
| condition[non_verbal] | OR 0.42 [0.09, 2.03] | 0.279 | 1.000 |
| condition[talk] | OR 1.25 [0.32, 4.79] | 0.749 | 1.000 |

Left out of the model: other_female (collinear).

**`stopped`** (agent): its speed fell below the deadlock monitor's threshold (physical). Status: separation, n = 144, events = 1.

Left out of the model: other_female (collinear).

**`backed_up`** (agent): moved against its path (physical). Status: one value, n = 144, events = 0.

**`plan_left`** (agent): its first plan turns to its left only. Status: separation, n = 141, events = 3.

Left out of the model: other_female (collinear).

**`plan_right`** (agent): its first plan turns to its right only. Status: ok, n = 141, events = 63.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 0.37 [0.14, 0.96] | 0.040 | 1.000 |
| own_female | OR 1.52 [0.62, 3.76] | 0.363 | 1.000 |
| other_age_high | OR 1.55 [0.62, 3.87] | 0.343 | 1.000 |
| is_lower_agent | OR 0.89 [0.33, 2.37] | 0.818 | 1.000 |
| geometry[layout=apart_20cm] | OR 2.83 [1.38, 5.78] | 0.004 | 0.561 |
| condition[non_verbal] | OR 1.28 [0.57, 2.86] | 0.545 | 1.000 |
| condition[talk] | OR 1.88 [0.87, 4.09] | 0.109 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_slowed`** (agent): its first plan slows below its speed at the decision. Status: ok, n = 141, events = 28.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 4.65 [1.26, 17.18] | 0.021 | 1.000 |
| own_female | OR 1.25 [0.49, 3.20] | 0.636 | 1.000 |
| other_age_high | OR 8.61 [2.56, 28.96] | < 0.001 | 0.064 |
| is_lower_agent | OR 1.00 [0.41, 2.42] | 0.996 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.05 [0.38, 2.91] | 0.931 | 1.000 |
| condition[non_verbal] | OR 1.51 [0.51, 4.44] | 0.454 | 1.000 |
| condition[talk] | OR 1.74 [0.57, 5.28] | 0.329 | 1.000 |

Left out of the model: other_female (collinear).

**`plan_stopped`** (agent): its first plan stops. Status: one value, n = 141, events = 0.

**`plan_backed_up`** (agent): its first plan backs up. Status: one value, n = 141, events = 0.

**`start_distance_m`** (agent): its first plan starts at this distance (plans that start so). Status: no data, n = 3.

Left out of the model: own_age_high (constant); other_age_high (collinear); other_female (collinear); geometry[layout=apart_20cm] (collinear).

**`signalled`** (agent): it signalled at least once (non-verbal and talk only). Status: ok, n = 96, events = 6.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| own_age_high | OR 2.29 [0.41, 12.61] | 0.343 | 1.000 |
| own_female | OR 1.00 [0.13, 7.73] | 1.000 | 1.000 |
| other_age_high | OR 2.29 [0.24, 22.05] | 0.475 | 1.000 |
| is_lower_agent | OR 1.00 [0.16, 6.26] | 1.000 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.31 [0.29, 5.98] | 0.731 | 1.000 |
| condition[talk] | OR 1.00 [0.19, 5.31] | 1.000 | 1.000 |

Left out of the model: other_female (collinear).

**`resolved_plan_only`** (session): resolved in `plan_only` (the Step 1 measure). Status: ok, n = 72, events = 17.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.78 [0.23, 2.70] | 0.700 | 1.000 |
| gender_pair[p1_male] | OR 2.07 [0.59, 7.25] | 0.255 | 1.000 |
| mapping[p1_higher] | OR 0.78 [0.23, 2.64] | 0.695 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.27 [0.38, 4.26] | 0.693 | 1.000 |
| condition[non_verbal] | OR 0.52 [0.14, 1.89] | 0.320 | 1.000 |
| condition[talk] | OR 0.39 [0.10, 1.61] | 0.195 | 1.000 |

**`resolved_plan_orca`** (session): resolved in `plan_orca`. Status: ok, n = 72, events = 21.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.71 [0.23, 2.20] | 0.550 | 1.000 |
| gender_pair[p1_male] | OR 1.07 [0.33, 3.49] | 0.908 | 1.000 |
| mapping[p1_higher] | OR 1.07 [0.35, 3.28] | 0.903 | 1.000 |
| geometry[layout=apart_20cm] | OR 0.62 [0.19, 1.99] | 0.419 | 1.000 |
| condition[non_verbal] | OR 1.00 [0.30, 3.39] | 1.000 | 1.000 |
| condition[talk] | OR 0.52 [0.14, 1.94] | 0.332 | 1.000 |

**`resolved_by_llm`** (session): resolved in `plan_only` before ORCA took over. Status: ok, n = 72, events = 17.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | OR 0.78 [0.23, 2.70] | 0.700 | 1.000 |
| gender_pair[p1_male] | OR 2.07 [0.59, 7.25] | 0.255 | 1.000 |
| mapping[p1_higher] | OR 0.78 [0.23, 2.64] | 0.695 | 1.000 |
| geometry[layout=apart_20cm] | OR 1.27 [0.38, 4.26] | 0.693 | 1.000 |
| condition[non_verbal] | OR 0.52 [0.14, 1.89] | 0.320 | 1.000 |
| condition[talk] | OR 0.39 [0.10, 1.61] | 0.195 | 1.000 |

**`decision_points`** (session): decision points of both people. Status: ok, n = 72.

| Term | Effect [95% CI] | p | Holm p |
| --- | --- | --- | --- |
| age_pair[p1_older] | -0.375 [-0.783, +0.033] | 0.071 | 1.000 |
| gender_pair[p1_male] | +0.375 [-0.149, +0.899] | 0.161 | 1.000 |
| mapping[p1_higher] | -0.042 [-0.455, +0.372] | 0.843 | 1.000 |
| geometry[layout=apart_20cm] | +0.292 [-0.120, +0.703] | 0.165 | 1.000 |
| condition[non_verbal] | +3.458 [+2.981, +3.936] | < 0.001 | < 0.001 |
| condition[talk] | +3.667 [+3.220, +4.114] | < 0.001 | < 0.001 |

## 2. Decision tree

Predicts **`passed_first`** per agent, depth at most 3, on 50 rows (the predictors that vary, with condition and geometry). Figure: `tree.png`.

- Accuracy on the rows it was grown on: 0.820; always guessing the commoner outcome: 0.800.
- Accuracy on held-out sessions (5-fold, grouped by session): 0.800.
- Splits on: `condition[non_verbal]`, `geometry[layout=apart_20cm]`, `is_lower_agent`.

A tree no better on held-out sessions than the commoner outcome has found no usable pattern.

```
|--- geometry[layout=apart_20cm] <= 0.50
|   |--- condition[non_verbal] <= 0.50
|   |   |--- is_lower_agent <= 0.50
|   |   |   |--- weights: [8.00, 1.00] class: 0
|   |   |--- is_lower_agent >  0.50
|   |   |   |--- weights: [7.00, 2.00] class: 0
|   |--- condition[non_verbal] >  0.50
|   |   |--- is_lower_agent <= 0.50
|   |   |   |--- weights: [3.00, 2.00] class: 0
|   |   |--- is_lower_agent >  0.50
|   |   |   |--- weights: [2.00, 3.00] class: 1
|--- geometry[layout=apart_20cm] >  0.50
|   |--- is_lower_agent <= 0.50
|   |   |--- weights: [9.00, 2.00] class: 0
|   |--- is_lower_agent >  0.50
|   |   |--- weights: [11.00, 0.00] class: 0
```

## 3. Counterfactual pairs against the noise floor

The noise floor is the flip rate between repeats of one cell of the exact-repeat set (identical prompts), with a bootstrap 95% interval over cells. A pair's flip rate (Wilson 95% interval) counts as evidence only where its lower end is above the noise floor's upper end, in the same condition. Components: `who_passed_first`, `passing_side`, `stopped`, `backed_up`, `behaviour` (`behaviour` is all of them together).

### The noise floor

| component | subset | cells | pairs | flips | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| who_passed_first | all | 6 | 60 | 35 | 0.583 | 0.333 | 0.733 |
| who_passed_first | independent | 2 | 20 | 14 | 0.700 | 0.700 | 0.700 |
| who_passed_first | non_verbal | 2 | 20 | 14 | 0.700 | 0.600 | 0.800 |
| who_passed_first | talk | 2 | 20 | 7 | 0.350 | 0 | 0.700 |
| passing_side | all | 6 | 60 | 22 | 0.367 | 0.200 | 0.500 |
| passing_side | independent | 2 | 20 | 10 | 0.500 | 0.400 | 0.600 |
| passing_side | non_verbal | 2 | 20 | 4 | 0.200 | 0 | 0.400 |
| passing_side | talk | 2 | 20 | 8 | 0.400 | 0.400 | 0.400 |
| stopped | all | 6 | 60 | 0 | 0 | 0 | 0 |
| stopped | independent | 2 | 20 | 0 | 0 | 0 | 0 |
| stopped | non_verbal | 2 | 20 | 0 | 0 | 0 | 0 |
| stopped | talk | 2 | 20 | 0 | 0 | 0 | 0 |
| backed_up | all | 6 | 60 | 0 | 0 | 0 | 0 |
| backed_up | independent | 2 | 20 | 0 | 0 | 0 | 0 |
| backed_up | non_verbal | 2 | 20 | 0 | 0 | 0 | 0 |
| backed_up | talk | 2 | 20 | 0 | 0 | 0 | 0 |
| behaviour | all | 6 | 60 | 46 | 0.767 | 0.600 | 0.900 |
| behaviour | independent | 2 | 20 | 18 | 0.900 | 0.900 | 0.900 |
| behaviour | non_verbal | 2 | 20 | 15 | 0.750 | 0.600 | 0.900 |
| behaviour | talk | 2 | 20 | 13 | 0.650 | 0.400 | 0.900 |

### The counterfactual pairs

No counterfactual pair in the data.

## 4. Behaviour stability

Per cell of the exact-repeat set: the share of its repeats with the commonest outcome (1: every repeat the same). A cell whose commonest behaviour came up in fewer than 0.75 of its repeats is a coin flip, and RF-11 should claim no rule there.

| Component | Cells | Mean | Lowest | Cells with every repeat the same |
| --- | --- | --- | --- | --- |
| who_passed_first | 6 | 0.633 | 0.400 | 1 |
| passing_side | 6 | 0.800 | 0.600 | 1 |
| stopped | 6 | 1 | 1 | 6 |
| backed_up | 6 | 1 | 1 | 6 |
| behaviour | 6 | 0.500 | 0.400 | 0 |

### Coin-flip cells: 5 of 6

| Cell | Condition | Repeats | Stability | Who passed first | Commonest behaviour |
| --- | --- | --- | --- | --- | --- |
| I_head_on_02dfbadb_4c33115a | independent | 5 | 0.400 | 0.600 | -\|right\|right\|0\|0\|0\|0 |
| I_head_on_de176842_48eb8404 | independent | 5 | 0.400 | 0.600 | -\|left\|left\|0\|0\|0\|0 |
| N_head_on_02dfbadb_4c33115a | non_verbal | 5 | 0.600 | 0.600 | -\|right\|right\|0\|0\|0\|0 |
| N_head_on_de176842_48eb8404 | non_verbal | 5 | 0.400 | 0.400 | p1\|right\|right\|0\|0\|0\|0 |
| T_head_on_de176842_48eb8404 | talk | 5 | 0.400 | 0.600 | -\|right\|right\|0\|0\|0\|0 |

## 5. The factor-to-decision mapping

Every observed combination of `own_age_high`, `own_female`, `other_age_high`, `other_female`, `is_lower_agent`, `geometry`, per condition, from the agent's point of view: **72 combinations** in `mapping.csv`, each with its rows and, per outcome, how many are known and the share that are 1. Read the counts with the shares: a combination seen once gives 0 or 1 from one row. The 25 combinations with the most rows:

| condition | own_age_high | own_female | other_age_high | other_female | is_lower_agent | geometry | rows | p_passed_first | p_kept_left | p_stopped | p_backed_up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| independent | 0 | 0 | 0 | 1 | 0 | layout=apart_20cm | 6 | 0.333 | 0.167 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 1 | layout=apart_20cm | 6 | 0 | 0 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 0 | layout=apart_20cm | 6 | 0 | 0 | 0 | 0 |
| talk | 0 | 1 | 0 | 0 | 1 | layout=apart_20cm | 6 | 0 | 0.333 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | layout=apart_20cm | 6 | 1 | 0.333 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 1 | layout=apart_20cm | 6 | 0 | 0.167 | 0 | 0 |
| non_verbal | 0 | 1 | 1 | 0 | 1 | layout=aligned | 5 | 0.333 | 0.200 | 0 | 0 |
| independent | 1 | 0 | 0 | 1 | 0 | layout=aligned | 5 | 0.500 | 0.400 | 0 | 0 |
| non_verbal | 1 | 0 | 0 | 1 | 0 | layout=aligned | 5 | 0.667 | 0.200 | 0 | 0 |
| talk | 0 | 1 | 1 | 0 | 1 | layout=aligned | 5 | 0.500 | 0.200 | 0 | 0 |
| talk | 1 | 0 | 0 | 1 | 0 | layout=aligned | 5 | 0 | 0.200 | 0 | 0 |
| independent | 0 | 1 | 1 | 0 | 1 | layout=aligned | 5 | 0 | 0.400 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 2 | 0 | 0 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 1 | layout=aligned | 2 | 0 | 0.500 | 0 | 0 |
| independent | 0 | 0 | 0 | 1 | 0 | layout=aligned | 2 | 0 | 0.500 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | layout=aligned | 2 | - | 0 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 1 | layout=aligned | 2 | - | 0.500 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 0 | layout=aligned | 2 | 0 | 0.500 | 0 | 0 |
| talk | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 2 | - | 0.500 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 0 | layout=apart_20cm | 2 | - | 0.500 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 1 | layout=apart_20cm | 2 | - | 0.500 | 0 | 0 |
| non_verbal | 0 | 0 | 0 | 1 | 1 | layout=aligned | 2 | - | 0 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 1 | layout=aligned | 2 | 1 | 0.500 | 0 | 0 |
| independent | 0 | 1 | 0 | 0 | 0 | layout=apart_20cm | 2 | 0 | 0 | 0 | 0 |
| non_verbal | 0 | 1 | 0 | 0 | 1 | layout=aligned | 2 | 1 | 0.500 | 0 | 0 |

## 6. Stated against measured

How often each factor is named in the agents' private `reason` (keyword codebook `reasons_v1`), beside its strongest measured effect in the per-agent models of all conditions together. Named often: in at least 0.1 of the reasons. Measured: a term significant after Holm's correction. A factor named often with no measured effect, or the reverse, is a finding.

| Factor | Share of reasons naming it | Measured effect | Outcome | Term | Estimate (OR or coef.) | Holm p | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| age | 0.250 | no | plan_slowed | other_age_high | 8.607 | 0.064 | named often, no measured effect |
| gender | 0.122 | no | passed_first | own_female | 0.634 | 1.000 | named often, no measured effect |
| urgency | 0.014 | - | - | - | - | - | not varied in this data |
| mobility_aid | 0 | - | - | - | - | - | not varied in this data |
| load | 0 | - | - | - | - | - | not varied in this data |
| distraction | 0 | - | - | - | - | - | not varied in this data |
| assertiveness | 0 | - | - | - | - | - | not varied in this data |
| residence | 0 | - | - | - | - | - | not varied in this data |
| memory_note | 0 | - | - | - | - | - | not varied in this data |
| surroundings | 0 | - | - | - | - | - | not varied in this data |
| time_of_day | 0 | - | - | - | - | - | not varied in this data |
| perceived_attractiveness | 0 | - | - | - | - | - | not varied in this data |
| familiarity | 0 | - | - | - | - | - | not varied in this data |
| is_lower_agent | - | no | passed_first | is_lower_agent | 1.774 | 1.000 | neither |

**Where saying and doing disagree:** `age` (named often, no measured effect), `gender` (named often, no measured effect).

### The debriefs' kind of basis

One per prompted agent (D8); every source is unchecked until RF-14.

| kind | independent | non_verbal | talk | all |
| --- | --- | --- | --- | --- |
| local_custom | 2 | 0 | 0 | 2 |
| habit | 8 | 2 | 6 | 16 |
| common_sense | 34 | 46 | 42 | 122 |
| none | 1 | 0 | 0 | 1 |
| (none given) | 3 | 0 | 0 | 3 |
| all | 48 | 48 | 48 | 144 |

## 7. Intent against plan

Each readable intent coded by the keyword codebook `intent_v2` (keep to a side, slow down, stop and wait, back up, carry on, or `other`), against the plan coded from its steps. A mismatch is an intent that says something the plan does not do. Intents coded `other` and unreadable replies are left out of the rate. A high rate means the structured plan cannot be trusted on its own (RF-11).

| subset | decision_points | unreadable | uncoded | compared | mismatches | rate | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 315 | 27 | 2 | 286 | 78 | 0.273 | 0.224 | 0.327 |
| independent | 48 | 3 | 0 | 45 | 6 | 0.133 | 0.063 | 0.262 |
| non_verbal | 131 | 23 | 1 | 107 | 36 | 0.336 | 0.254 | 0.430 |
| talk | 136 | 1 | 1 | 134 | 36 | 0.269 | 0.201 | 0.349 |

### Examples of mismatches

| condition | session_id | agent_id | intent | plan_categories | plan_side | why |
| --- | --- | --- | --- | --- | --- | --- |
| non_verbal | N_head_on_de176842_54f8aa95_r1 | 1 | Keep walking to the supermarket and pass Person 1 with a bit of room | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_de176842_54f8aa95_r1 | 0 | keep walking to the supermarket, staying slightly right to pass without bumping | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| talk | T_head_on_02dfbadb_737d345b_r1 | 0 | Keep walking to the supermarket, staying eased to my right so we can pass each other comfortably. | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| talk | T_head_on_de176842_48eb8404_r5 | 1 | Keep to my right side of the passage so the young woman can pass on my left without trouble. | slow_down | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| non_verbal | N_head_on_02dfbadb_737d345b_r1 | 0 | Keep walking to the supermarket and pass Person 1 without any fuss. | keep_to_side | right | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_737d345b_r1 | 1 | Keep walking to the supermarket and pass the older man with room to spare. | keep_to_side | both | intent says carry_on, the plan does not |
| non_verbal | N_head_on_02dfbadb_737d345b_r1 | 0 | Keep walking to the supermarket and pass Person 1 smoothly. | keep_to_side;slow_down | right | intent says carry_on, the plan does not |
| talk | T_head_on_02dfbadb_15a44363_r1 | 0 | Keep to the right side of the passage and let the older woman cross in front of me safely. | slow_down | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| talk | T_head_on_02dfbadb_15a44363_r1 | 1 | Keep well to the right and slow a little so the young man can cross in front of me safely | slow_down | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| talk | T_head_on_de176842_4c33115a_r1 | 1 | Keep walking to the supermarket, sticking to the right side to pass easily | carry_on | none | intent says keep_to_side, the plan does not; intent says right, the plan turns none |
| independent | I_head_on_02dfbadb_b4042637_r1 | 1 | Keep walking to the supermarket, giving the older woman a little extra room as we pass. | keep_to_side | right | intent says carry_on, the plan does not |
| independent | I_head_on_de176842_15a44363_r1 | 1 | Keep walking to the supermarket, giving the young man a bit of room to pass. | keep_to_side | both | intent says carry_on, the plan does not |
| independent | I_head_on_02dfbadb_4c33115a_r1 | 1 | Keep walking to the supermarket and pass Person 1 without bumping into her. | keep_to_side | right | intent says carry_on, the plan does not |
| independent | I_head_on_02dfbadb_4c33115a_r3 | 1 | Keep walking to the supermarket and pass Person 1 without fuss. | keep_to_side | right | intent says carry_on, the plan does not |
| independent | I_head_on_de176842_737d345b_r1 | 0 | Keep walking to the supermarket, giving the oncoming young woman plenty of room to pass. | keep_to_side | both | intent says carry_on, the plan does not |

### Intents the codebook could not place (the commonest)

- 1 x "Pass the oncoming man comfortably"
- 1 x "Pass Person 1 cleanly in the narrow passage"

## How to read this report

- **An effect here is an effect on what the LLM agents did**, in this design: a screen, so main effects are estimated clear of two-factor interactions only when the design is a resolution IV fraction (`llm_negotiation/docs/screening-designs.md`, section 3).
- **Separation** (an outcome predicted perfectly by some predictor) leaves a model with no finite estimate; it is listed, not reported as an effect. Rare outcomes with many factors cause it: D14 aims at about 10 events per factor.
- **The mapping is sparse** when there are many factors: most combinations are seen once or twice.
- **The codebooks are drafts** until RF-9's pilot (`analysis/codebooks/`): a mention or a coded intent is a keyword match, not a reading of the text.
