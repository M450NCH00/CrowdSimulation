# Resolution: rf36_crowd_encounters_non_verbal

Status aborted: 66 of 72 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing_crowd | non_verbal | 66 | 66 | 0% | 0% | 0% | 0% | 0 | 8.318 | 12.606 | 66 |

## How encounters ended

- passed: 64
- no_conflict: 2

## Debriefs

- common_sense: 107
- habit: 101
- none: 8

## Tokens and cost

Preview (worst case) USD 48.866976; actual USD 0.144901104 (aborted sessions USD 0.0); cap USD 0.15. At most 0.1108 of a session's preview was used.

## Failure modes

- outcome_completed: 66
- retried_decision_points: 67
- unreadable_decision_point:missing_until: 1
- unreadable_decision_point:not_json: 2
- unreadable_decision_point:start_at_distance_beyond_current: 4
- unreadable_decision_point:unknown_until: 2
- unreadable_decision_point:until_at_distance_beyond_current: 52
