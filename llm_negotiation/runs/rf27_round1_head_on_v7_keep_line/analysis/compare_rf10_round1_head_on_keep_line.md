# rf27_round1_head_on_v7_keep_line against rf10_round1_head_on_keep_line, condition independent

Sessions completed in both: 96 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on_keep_line | rf27_round1_head_on_v7_keep_line |
| --- | --- | --- |
| all | 35 / 64: 0.55 (0.43 to 0.66) | 27 / 64: 0.42 (0.31 to 0.54) |
| layout=aligned | 19 / 32: 0.59 (0.42 to 0.74) | 15 / 32: 0.47 (0.31 to 0.64) |
| layout=apart_20cm | 16 / 32: 0.50 (0.34 to 0.66) | 12 / 32: 0.38 (0.23 to 0.55) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 15 | 20 |
| not resolved in the first | 12 | 17 |

McNemar's exact test (two-sided) on the 32 sessions that changed: p = 0.2153.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on_keep_line | collision | 3 | 16 | 8 |
| rf10_round1_head_on_keep_line | near_miss | 1 | 1 | 0 |
| rf10_round1_head_on_keep_line | resolved | 31 | 1 | 3 |
| rf27_round1_head_on_v7_keep_line | collision | 9 | 17 | 6 |
| rf27_round1_head_on_v7_keep_line | near_miss | 4 | 1 | 0 |
| rf27_round1_head_on_v7_keep_line | resolved | 23 | 1 | 3 |

## Stability, unreadable replies, model

- **rf10_round1_head_on_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 5 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (198 sends); template resolve_v6.
- **rf27_round1_head_on_v7_keep_line**: exact-repeat set, 1 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 3 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (197 sends); template resolve_v7.
