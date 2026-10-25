# Resolution: rf28_round1_head_on_v4pro

Status partial: 6 of 96 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | independent | 6 | 6 | 17% | 17% | 17% | 0% | 5 | 2.0 | 4.0 | 0 |

## How encounters ended

- collision: 3
- passed: 1
- orca_took_over: 2

## Debriefs

- common_sense: 10
- local_custom: 1

## Tokens and cost

Preview (worst case) USD 11.0854656; actual USD 0.011625328 (aborted sessions USD 0.0); cap USD 0.3. At most 0.1122 of a session's preview was used.

## Failure modes

- outcome_completed: 6
- retried_decision_points: 1
- unreadable_decision_point:not_json: 1
