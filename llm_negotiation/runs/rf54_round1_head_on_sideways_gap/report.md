# Resolution: rf54_round1_head_on_sideways_gap

Status completed: 272 of 272 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | silent | 272 | 272 | 74% | 74% | 74% | 0% | 46 | 5.585 | 7.846 | 0 |

## How encounters ended

- passed: 226
- collision: 46

## Debriefs

- common_sense: 459
- habit: 62
- local_custom: 3
- none: 19

## Tokens and cost

Preview (worst case) USD 41.6365632; actual USD 0.351222759 (aborted sessions USD 0.0); cap USD 0.6. At most 0.0995 of a session's preview was used.

## Failure modes

- outcome_completed: 272
- retried_decision_points: 72
- unreadable_decision_point:missing_until: 3
- unreadable_decision_point:unknown_start: 33
- unreadable_decision_point:unknown_until: 18
- unreadable_decision_point:until_at_distance_beyond_current: 2
- unreadable_decision_point:until_at_distance_not_positive: 2
