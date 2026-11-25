# rf39_round1_head_on_sidestep_reprompt against rf30_round1_head_on_keep_line, condition non_verbal

Sessions completed in both: 96 (only in the first: 0, only in the second: 176); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf30_round1_head_on_keep_line | rf39_round1_head_on_sidestep_reprompt |
| --- | --- | --- |
| all | 37 / 64: 0.58 (0.46 to 0.69) | 35 / 64: 0.55 (0.43 to 0.66) |
| layout=aligned | 20 / 32: 0.62 (0.45 to 0.77) | 18 / 32: 0.56 (0.39 to 0.72) |
| layout=apart_20cm | 17 / 32: 0.53 (0.36 to 0.69) | 17 / 32: 0.53 (0.36 to 0.69) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 19 | 18 |
| not resolved in the first | 16 | 11 |

McNemar's exact test (two-sided) on the 34 sessions that changed: p = 0.8642.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf30_round1_head_on_keep_line | collision | 1 | 16 | 5 |
| rf30_round1_head_on_keep_line | near_miss | 4 | 0 | 1 |
| rf30_round1_head_on_keep_line | resolved | 33 | 0 | 4 |
| rf39_round1_head_on_sidestep_reprompt | collision | 0 | 20 | 2 |
| rf39_round1_head_on_sidestep_reprompt | near_miss | 2 | 1 | 4 |
| rf39_round1_head_on_sidestep_reprompt | resolved | 33 | 1 | 1 |

## Stability, unreadable replies, model

- **rf30_round1_head_on_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 11 of 515 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (531 sends); template resolve_v6.
- **rf39_round1_head_on_sidestep_reprompt**: exact-repeat set, 58 of 64 cells with one `plan_only` outcome in every run (80 runs); unreadable after the retry, 22 of 596 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (631 sends); template resolve_v8.
