# rf10_round1_head_on_keep_line against rf10_round1_head_on, condition independent

Sessions completed in both: 96 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf10_round1_head_on_keep_line |
| --- | --- | --- |
| all | 22 / 64: 0.34 (0.24 to 0.47) | 35 / 64: 0.55 (0.43 to 0.66) |
| layout=aligned | 11 / 32: 0.34 (0.20 to 0.52) | 19 / 32: 0.59 (0.42 to 0.74) |
| layout=apart_20cm | 11 / 32: 0.34 (0.20 to 0.52) | 16 / 32: 0.50 (0.34 to 0.66) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 22 | 0 |
| not resolved in the first | 13 | 29 |

McNemar's exact test (two-sided) on the 13 sessions that changed: p = 0.0002.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 9 | 18 | 10 |
| rf10_round1_head_on | near_miss | 4 | 0 | 1 |
| rf10_round1_head_on | resolved | 22 | 0 | 0 |
| rf10_round1_head_on_keep_line | collision | 3 | 16 | 8 |
| rf10_round1_head_on_keep_line | near_miss | 1 | 1 | 0 |
| rf10_round1_head_on_keep_line | resolved | 31 | 1 | 3 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 5 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (198 sends); template resolve_v6.
- **rf10_round1_head_on_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 5 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (198 sends); template resolve_v6.
