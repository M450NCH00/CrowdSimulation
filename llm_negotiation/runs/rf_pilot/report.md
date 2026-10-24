# Resolution: rf_pilot

Status partial: 12 of 72 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | independent | 3 | 3 | 0% | 0% | 0% | 0% | 3 | 2.0 | 4.333 | 0 |
| head_on | passing | non_verbal | 6 | 6 | 0% | 0% | 0% | 0% | 6 | 6.0 | 9.667 | 0 |
| head_on | passing | talk | 3 | 3 | 0% | 0% | 0% | 0% | 3 | 6.0 | 11.333 | 0 |

## How encounters ended

- collision: 11
- orca_took_over: 1

## Debriefs

- common_sense: 19
- habit: 5

## Tokens and cost

Preview (worst case) USD 4.7708352; actual USD 0.013397892 (aborted sessions USD 0.0); cap USD 0.2. At most 0.0883 of a session's preview was used.

## Failure modes

- outcome_completed: 12
- retried_decision_points: 21
- unreadable_decision_point:start_on_later_step: 14
