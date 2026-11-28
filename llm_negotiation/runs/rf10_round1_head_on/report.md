# Resolution: rf10_round1_head_on

Status completed: 288 of 288 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | independent | 96 | 96 | 38% | 41% | 38% | 0% | 52 | 2.0 | 4.01 | 0 |
| head_on | passing | non_verbal | 96 | 96 | 29% | 30% | 29% | 0% | 59 | 5.667 | 7.844 | 0 |
| head_on | passing | talk | 96 | 96 | 31% | 38% | 31% | 0% | 55 | 5.698 | 7.802 | 0 |

## How encounters ended

- collision: 166
- passed: 122

## Debriefs

- common_sense: 307
- habit: 196
- local_custom: 57
- none: 11

## Tokens and cost

Preview (worst case) USD 17.6262912; actual USD 0.289517388 (aborted sessions USD 0.0); cap USD 0.35. At most 0.1043 of a session's preview was used.

## Failure modes

- outcome_completed: 288
- retried_decision_points: 33
- unreadable_decision_point:missing_until: 1
- unreadable_decision_point:unknown_start: 26
- unreadable_decision_point:unknown_until: 3
