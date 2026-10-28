# Resolution: rf34_round1_group_head_on_non_verbal

Status partial: 8 of 72 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing_group | non_verbal | 8 | 8 | 12% | 12% | 12% | 0% | 6 | 10.375 | 14.875 | 0 |

## How encounters ended

- collision: 6
- passed: 2

## Debriefs

- common_sense: 19
- habit: 10
- none: 1

## Tokens and cost

Preview (worst case) USD 9.083988; actual USD 0.018598632 (aborted sessions USD 0.0); cap USD 0.2. At most 0.0926 of a session's preview was used.

## Failure modes

- outcome_completed: 8
- retried_decision_points: 6
- unreadable_decision_point:start_at_distance_beyond_current: 3
- unreadable_decision_point:unknown_start: 1
- unreadable_decision_point:until_at_distance_beyond_current: 2
