# Resolution: rf32_round1_group_head_on_orca_groups

Status completed: 72 of 72 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing_group | independent | 72 | 72 | 8% | 8% | 8% | 0% | 62 | 3.5 | 7.042 | 0 |

## How encounters ended

- passed: 10
- collision: 62

## Debriefs

- common_sense: 154
- habit: 78
- local_custom: 2
- none: 11

## Tokens and cost

Preview (worst case) USD 3.7320912; actual USD 0.061869618 (aborted sessions USD 0.0); cap USD 0.1425. At most 0.083 of a session's preview was used.

## Failure modes

- outcome_completed: 72
- retried_decision_points: 10
- unreadable_decision_point:unknown_start: 5
- unreadable_decision_point:unknown_until: 1
- unreadable_decision_point:until_seconds_not_positive: 1
