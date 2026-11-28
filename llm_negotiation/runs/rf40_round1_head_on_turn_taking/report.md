# Resolution: rf40_round1_head_on_turn_taking

Status completed: 816 of 816 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | non_verbal | 272 | 272 | 54% | 60% | 54% | 0% | 94 | 6.529 | 8.654 | 0 |
| head_on | passing | silent | 272 | 272 | 64% | 68% | 64% | 0% | 78 | 6.092 | 8.327 | 0 |
| head_on | passing | talk | 272 | 272 | 58% | 59% | 58% | 0% | 98 | 6.702 | 8.941 | 0 |

## How encounters ended

- collision: 270
- passed: 546

## Debriefs

- common_sense: 1285
- habit: 266
- local_custom: 23
- none: 57

## Tokens and cost

Preview (worst case) USD 141.0527808; actual USD 1.226091876 (aborted sessions USD 0.0); cap USD 1.8. At most 0.1239 of a session's preview was used.

## Failure modes

- outcome_completed: 816
- retried_decision_points: 164
- unreadable_decision_point:missing_until: 7
- unreadable_decision_point:not_json: 14
- unreadable_decision_point:sidestep_standing_still: 1
- unreadable_decision_point:unknown_start: 61
- unreadable_decision_point:unknown_until: 25
- unreadable_decision_point:until_at_distance_beyond_current: 4
- unreadable_decision_point:until_at_distance_not_positive: 8
- unreadable_decision_point:until_at_distance_with_nobody_in_view: 1
