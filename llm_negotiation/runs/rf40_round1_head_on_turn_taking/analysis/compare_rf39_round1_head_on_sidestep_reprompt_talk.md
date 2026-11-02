# rf40_round1_head_on_turn_taking against rf39_round1_head_on_sidestep_reprompt, condition talk

Sessions completed in both: 272 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf39_round1_head_on_sidestep_reprompt | rf40_round1_head_on_turn_taking |
| --- | --- | --- |
| all | 37 / 64: 0.58 (0.46 to 0.69) | 41 / 64: 0.64 (0.52 to 0.75) |
| layout=aligned | 19 / 32: 0.59 (0.42 to 0.74) | 25 / 32: 0.78 (0.61 to 0.89) |
| layout=apart_20cm | 18 / 32: 0.56 (0.39 to 0.72) | 16 / 32: 0.50 (0.34 to 0.66) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 23 | 14 |
| not resolved in the first | 18 | 9 |

McNemar's exact test (two-sided) on the 32 sessions that changed: p = 0.5966.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf39_round1_head_on_sidestep_reprompt | collision | 0 | 21 | 3 |
| rf39_round1_head_on_sidestep_reprompt | near_miss | 0 | 1 | 2 |
| rf39_round1_head_on_sidestep_reprompt | resolved | 36 | 0 | 1 |
| rf40_round1_head_on_turn_taking | collision | 1 | 17 | 1 |
| rf40_round1_head_on_turn_taking | near_miss | 1 | 2 | 1 |
| rf40_round1_head_on_turn_taking | resolved | 41 | 0 | 0 |

## Stability, unreadable replies, model

- **rf39_round1_head_on_sidestep_reprompt**: exact-repeat set, 12 of 64 cells with one `plan_only` outcome in every run (256 runs); unreadable after the retry, 26 of 1738 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (1779 sends); template resolve_v8.
- **rf40_round1_head_on_turn_taking**: exact-repeat set, 13 of 64 cells with one `plan_only` outcome in every run (256 runs); unreadable after the retry, 47 of 1823 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (1889 sends); template resolve_v9.
