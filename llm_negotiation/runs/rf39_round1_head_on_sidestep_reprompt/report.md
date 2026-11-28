# Resolution: rf39_round1_head_on_sidestep_reprompt

Status completed: 816 of 816 session(s) have a record.

## Physical resolution, per encounter type and condition

Resolved as the scenario defines it (the passing scenarios: both left the conflict zone with no collision, no near miss and no deadlock, within the time limit), in each mode's replay. `by LLM` is the Step 1 answer: resolved in `plan_only` and not handed to ORCA. `plain ORCA` is the case's own run with no plan, on the same seed; the cases were chosen as severe conflicts, so plain ORCA often passes within the near-miss distance.

| Encounter type | Scenario | Condition | Sessions | With an encounter | plan_only | plan_orca | by LLM | plain ORCA | Not resolved by LLM | Mean decision points | Mean calls | Cap reached |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| head_on | passing | independent | 272 | 272 | 37% | 41% | 37% | 0% | 154 | 2.0 | 4.026 | 0 |
| head_on | passing | non_verbal | 272 | 272 | 60% | 64% | 60% | 0% | 84 | 6.268 | 8.588 | 0 |
| head_on | passing | talk | 272 | 272 | 61% | 61% | 61% | 0% | 97 | 6.39 | 8.537 | 0 |

## How encounters ended

- passed: 479
- collision: 323
- orca_took_over: 12
- no_conflict: 2

## Debriefs

- common_sense: 1273
- habit: 249
- local_custom: 40
- none: 40

## Tokens and cost

Preview (worst case) USD 107.4299904; actual USD 0.988491981 (aborted sessions USD 0.0); cap USD 1.6. At most 0.1221 of a session's preview was used.

## Failure modes

- outcome_completed: 816
- retried_decision_points: 164
- unreadable_decision_point:missing_until: 31
- unreadable_decision_point:not_json: 11
- unreadable_decision_point:sidestep_standing_still: 5
- unreadable_decision_point:unknown_start: 21
- unreadable_decision_point:unknown_until: 36
- unreadable_decision_point:until_at_distance_beyond_current: 3
- unreadable_decision_point:until_at_distance_not_positive: 5
