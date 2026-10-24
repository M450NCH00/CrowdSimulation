# Resolution: rf_pilot_v2

Status completed: 72 of 72 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | independent | 24 | 24 | 33% | 33% | 33% | 0% | 13 | 2.0 | 4.0 | 0 |
| head_on | passing | non_verbal | 24 | 24 | 21% | 33% | 21% | 0% | 14 | 5.458 | 8.667 | 0 |
| head_on | passing | talk | 24 | 24 | 17% | 21% | 17% | 0% | 19 | 5.667 | 7.833 | 0 |

## How encounters ended

- collision: 44
- orca_took_over: 2
- no_conflict: 16
- passed: 10

## Debriefs

- common_sense: 122
- habit: 16
- local_custom: 2
- none: 1

## Tokens and cost

Preview (worst case) USD 4.8466944; actual USD 0.061703364 (aborted sessions USD 0.0); cap USD 0.18. At most 0.0726 of a session's preview was used.

## Failure modes

- outcome_completed: 72
- retried_decision_points: 36
- unreadable_decision_point:not_json: 3
- unreadable_decision_point:unknown_until: 24
