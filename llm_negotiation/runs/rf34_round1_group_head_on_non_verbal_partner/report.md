# Resolution: rf34_round1_group_head_on_non_verbal_partner

Status completed: 72 of 72 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing_group | non_verbal | 72 | 72 | 15% | 18% | 15% | 0% | 58 | 10.028 | 13.75 | 0 |

## How encounters ended

- collision: 58
- passed: 14

## Debriefs

- common_sense: 116
- habit: 128
- none: 8

## Tokens and cost

Preview (worst case) USD 9.083988; actual USD 0.150196728 (aborted sessions USD 0.0); cap USD 0.1814. At most 0.0912 of a session's preview was used.

## Failure modes

- outcome_completed: 72
- retried_decision_points: 16
- unreadable_decision_point:unknown_start: 8
- unreadable_decision_point:unknown_until: 2
