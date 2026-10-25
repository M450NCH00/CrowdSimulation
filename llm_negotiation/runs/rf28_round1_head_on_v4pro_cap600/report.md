# Resolution: rf28_round1_head_on_v4pro_cap600

Status completed: 96 of 96 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | independent | 96 | 96 | 28% | 29% | 28% | 0% | 62 | 2.0 | 4.01 | 0 |

## How encounters ended

- passed: 29
- collision: 38
- orca_took_over: 24
- no_conflict: 5

## Debriefs

- common_sense: 144
- habit: 14
- local_custom: 16

## Tokens and cost

Preview (worst case) USD 15.6473856; actual USD 0.164082116 (aborted sessions USD 0.0); cap USD 0.28. At most 0.0709 of a session's preview was used.

## Failure modes

- outcome_completed: 96
- retried_decision_points: 19
- unreadable_decision_point:missing_until: 1
- unreadable_decision_point:unknown_start: 1
- unreadable_decision_point:unknown_until: 13
- unreadable_decision_point:until_at_distance_not_positive: 1
- unreadable_decision_point:until_seconds_not_positive: 2
