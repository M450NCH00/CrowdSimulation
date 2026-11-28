# Resolution: rf49_round1_head_on_menu_abs_swap

Status completed: 288 of 288 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | silent | 144 | 144 | 31% | 38% | 31% | 0% | 89 | 4.993 | 6.993 | 0 |
| head_on | passing | talk | 144 | 144 | 25% | 35% | 25% | 0% | 94 | 5.931 | 7.938 | 0 |

## How encounters ended

- no_conflict: 71
- collision: 183
- passed: 34

## Debriefs

- common_sense: 456
- habit: 75
- local_custom: 2
- none: 43

## Tokens and cost

Preview (worst case) USD 50.8114944; actual USD 0.268239702 (aborted sessions USD 0.0); cap USD 0.525. At most 0.0556 of a session's preview was used.

## Failure modes

- outcome_completed: 288
- retried_decision_points: 1
