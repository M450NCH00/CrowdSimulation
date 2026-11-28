# rf40_round1_head_on_turn_taking against rf39_round1_head_on_sidestep_reprompt, condition non_verbal

Sessions completed in both: 272 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf39_round1_head_on_sidestep_reprompt | rf40_round1_head_on_turn_taking |
| --- | --- | --- |
| all | 35 / 64: 0.55 (0.43 to 0.66) | 40 / 64: 0.62 (0.50 to 0.73) |
| layout=aligned | 18 / 32: 0.56 (0.39 to 0.72) | 18 / 32: 0.56 (0.39 to 0.72) |
| layout=apart_20cm | 17 / 32: 0.53 (0.36 to 0.69) | 22 / 32: 0.69 (0.51 to 0.82) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 21 | 14 |
| not resolved in the first | 19 | 10 |

McNemar's exact test (two-sided) on the 33 sessions that changed: p = 0.4869.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf39_round1_head_on_sidestep_reprompt | collision | 0 | 20 | 2 |
| rf39_round1_head_on_sidestep_reprompt | near_miss | 2 | 1 | 4 |
| rf39_round1_head_on_sidestep_reprompt | resolved | 33 | 1 | 1 |
| rf40_round1_head_on_turn_taking | collision | 2 | 14 | 3 |
| rf40_round1_head_on_turn_taking | near_miss | 1 | 0 | 4 |
| rf40_round1_head_on_turn_taking | resolved | 35 | 0 | 5 |

## Stability, unreadable replies, model

- **rf39_round1_head_on_sidestep_reprompt**: exact-repeat set, 10 of 64 cells with one `plan_only` outcome in every run (256 runs); unreadable after the retry, 57 of 1705 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (1792 sends); template resolve_v8.
- **rf40_round1_head_on_turn_taking**: exact-repeat set, 6 of 64 cells with one `plan_only` outcome in every run (256 runs); unreadable after the retry, 22 of 1776 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (1810 sends); template resolve_v9.
