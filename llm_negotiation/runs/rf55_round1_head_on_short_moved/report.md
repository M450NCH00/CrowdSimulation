# Resolution: rf55_round1_head_on_short_moved

Status completed: 272 of 272 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | silent | 272 | 272 | 81% | 79% | 81% | 0% | 42 | 5.603 | 7.779 | 0 |

## How encounters ended

- passed: 230
- collision: 42

## Debriefs

- common_sense: 460
- habit: 57
- local_custom: 5
- none: 22

## Tokens and cost

Preview (worst case) USD 41.6365632; actual USD 0.341973492 (aborted sessions USD 0.0); cap USD 0.6. At most 0.1088 of a session's preview was used.

## Failure modes

- outcome_completed: 272
- retried_decision_points: 48
- unreadable_decision_point:missing_until: 1
- unreadable_decision_point:unknown_start: 26
- unreadable_decision_point:unknown_until: 6
- unreadable_decision_point:until_at_distance_beyond_current: 2
