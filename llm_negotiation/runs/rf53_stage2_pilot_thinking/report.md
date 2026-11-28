# Resolution: rf53_stage2_pilot_thinking

Status completed: 80 of 80 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | silent | 80 | 80 | 76% | 74% | 76% | 0% | 12 | 5.737 | 7.9 | 0 |

## How encounters ended

- collision: 12
- passed: 68

## Debriefs

- common_sense: 115
- habit: 20
- local_custom: 21
- none: 4

## Tokens and cost

Preview (worst case) USD 360.409248; actual USD 0.770159664 (aborted sessions USD 0.0); cap USD 1.0. At most 0.034 of a session's preview was used.

## Failure modes

- outcome_completed: 80
- retried_decision_points: 13
- unreadable_decision_point:not_json: 10
