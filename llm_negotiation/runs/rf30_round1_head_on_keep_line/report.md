# Resolution: rf30_round1_head_on_keep_line

Status completed: 192 of 192 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | non_verbal | 96 | 96 | 55% | 57% | 55% | 0% | 34 | 5.365 | 7.531 | 0 |
| head_on | passing | talk | 96 | 96 | 49% | 52% | 49% | 0% | 38 | 5.458 | 7.531 | 0 |

## How encounters ended

- passed: 120
- collision: 72

## Debriefs

- common_sense: 197
- habit: 146
- local_custom: 36
- none: 5

## Tokens and cost

Preview (worst case) USD 14.8995072; actual USD 0.221170413 (aborted sessions USD 0.0); cap USD 0.3. At most 0.104 of a session's preview was used.

## Failure modes

- outcome_completed: 192
- retried_decision_points: 23
- unreadable_decision_point:unknown_start: 16
- unreadable_decision_point:unknown_until: 1
