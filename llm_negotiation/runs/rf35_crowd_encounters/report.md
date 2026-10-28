# Resolution: rf35_crowd_encounters

Status partial: 8 of 72 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing_crowd | independent | 8 | 8 | 0% | 0% | 0% | 0% | 0 | 3.75 | 7.5 | 8 |

## How encounters ended

- passed: 5
- no_conflict: 3

## Debriefs

- common_sense: 12
- habit: 16
- none: 1

## Tokens and cost

Preview (worst case) USD 23.5078848; actual USD 0.008886522 (aborted sessions USD 0.0); cap USD 0.1. At most 0.0697 of a session's preview was used.

## Failure modes

- outcome_completed: 8
- retried_decision_points: 1
- unreadable_decision_point:until_at_distance_beyond_current: 1
