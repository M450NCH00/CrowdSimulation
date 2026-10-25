# Resolution: rf29_round1_head_on_sidestep

Status completed: 96 of 96 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | independent | 96 | 96 | 5% | 14% | 5% | 0% | 85 | 2.0 | 4.0 | 0 |

## How encounters ended

- collision: 84
- passed: 11
- orca_took_over: 1

## Debriefs

- common_sense: 112
- habit: 56
- local_custom: 17
- none: 5

## Tokens and cost

Preview (worst case) USD 2.8429056; actual USD 0.04899507 (aborted sessions USD 0.0); cap USD 0.08. At most 0.0844 of a session's preview was used.

## Failure modes

- outcome_completed: 96
- retried_decision_points: 2
- unreadable_decision_point:missing_until: 1
- unreadable_decision_point:unknown_start: 1
