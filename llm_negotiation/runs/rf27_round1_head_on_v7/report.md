# Resolution: rf27_round1_head_on_v7

Status completed: 96 of 96 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | independent | 96 | 96 | 23% | 27% | 23% | 0% | 64 | 2.0 | 4.021 | 0 |

## How encounters ended

- passed: 32
- collision: 64

## Debriefs

- common_sense: 114
- habit: 60
- local_custom: 10
- none: 5

## Tokens and cost

Preview (worst case) USD 2.7489024; actual USD 0.049857768 (aborted sessions USD 0.0); cap USD 0.08. At most 0.1024 of a session's preview was used.

## Failure modes

- outcome_completed: 96
- retried_decision_points: 5
- unreadable_decision_point:unknown_start: 3
