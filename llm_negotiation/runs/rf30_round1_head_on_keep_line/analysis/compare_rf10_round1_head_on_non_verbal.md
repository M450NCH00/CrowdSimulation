# rf30_round1_head_on_keep_line against rf10_round1_head_on, condition non_verbal

Sessions completed in both: 96 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf30_round1_head_on_keep_line |
| --- | --- | --- |
| all | 17 / 64: 0.27 (0.17 to 0.38) | 37 / 64: 0.58 (0.46 to 0.69) |
| layout=aligned | 8 / 32: 0.25 (0.13 to 0.42) | 20 / 32: 0.62 (0.45 to 0.77) |
| layout=apart_20cm | 9 / 32: 0.28 (0.16 to 0.45) | 17 / 32: 0.53 (0.36 to 0.69) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 10 | 7 |
| not resolved in the first | 27 | 20 |

McNemar's exact test (two-sided) on the 34 sessions that changed: p = 0.0008.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 11 | 19 | 13 |
| rf10_round1_head_on | near_miss | 3 | 1 | 0 |
| rf10_round1_head_on | resolved | 16 | 0 | 1 |
| rf30_round1_head_on_keep_line | collision | 1 | 16 | 5 |
| rf30_round1_head_on_keep_line | near_miss | 4 | 0 | 1 |
| rf30_round1_head_on_keep_line | resolved | 33 | 0 | 4 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 3 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 17 of 544 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (561 sends); template resolve_v6.
- **rf30_round1_head_on_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 11 of 515 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (531 sends); template resolve_v6.
