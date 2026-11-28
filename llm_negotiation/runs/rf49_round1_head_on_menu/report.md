# Resolution: rf49_round1_head_on_menu

Status completed: 544 of 544 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | silent | 272 | 272 | 54% | 57% | 54% | 0% | 110 | 5.11 | 7.129 | 0 |
| head_on | passing | talk | 272 | 272 | 35% | 46% | 35% | 0% | 148 | 5.754 | 7.761 | 0 |

## How encounters ended

- passed: 89
- collision: 258
- no_conflict: 197

## Debriefs

- common_sense: 796
- habit: 187
- local_custom: 11
- none: 94

## Tokens and cost

Preview (worst case) USD 93.7564416; actual USD 0.487005048 (aborted sessions USD 0.0); cap USD 0.95. At most 0.0533 of a session's preview was used.

## Failure modes

- outcome_completed: 544
- retried_decision_points: 7
- unreadable_decision_point:unknown_action: 3
