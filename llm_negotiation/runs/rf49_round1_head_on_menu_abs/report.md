# Resolution: rf49_round1_head_on_menu_abs

Status completed: 288 of 288 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | silent | 144 | 144 | 31% | 36% | 31% | 0% | 88 | 5.181 | 7.188 | 0 |
| head_on | passing | talk | 144 | 144 | 25% | 35% | 25% | 0% | 94 | 5.722 | 7.729 | 0 |

## How encounters ended

- collision: 182
- no_conflict: 69
- passed: 37

## Debriefs

- common_sense: 447
- habit: 81
- local_custom: 5
- none: 43

## Tokens and cost

Preview (worst case) USD 50.8405248; actual USD 0.268674924 (aborted sessions USD 0.0); cap USD 0.525. At most 0.0523 of a session's preview was used.

## Failure modes

- outcome_completed: 288
- retried_decision_points: 2
