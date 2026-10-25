# rf28_round1_head_on_v4pro_cap600_keep_line against rf10_round1_head_on_keep_line, condition independent

Sessions completed in both: 96 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on_keep_line | rf28_round1_head_on_v4pro_cap600_keep_line |
| --- | --- | --- |
| all | 35 / 64: 0.55 (0.43 to 0.66) | 21 / 64: 0.33 (0.23 to 0.45) |
| layout=aligned | 19 / 32: 0.59 (0.42 to 0.74) | 13 / 32: 0.41 (0.26 to 0.58) |
| layout=apart_20cm | 16 / 32: 0.50 (0.34 to 0.66) | 8 / 32: 0.25 (0.13 to 0.42) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 11 | 24 |
| not resolved in the first | 10 | 19 |

McNemar's exact test (two-sided) on the 34 sessions that changed: p = 0.0243.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on_keep_line | collision | 3 | 16 | 8 |
| rf10_round1_head_on_keep_line | near_miss | 1 | 1 | 0 |
| rf10_round1_head_on_keep_line | resolved | 31 | 1 | 3 |
| rf28_round1_head_on_v4pro_cap600_keep_line | collision | 0 | 1 | 18 |
| rf28_round1_head_on_v4pro_cap600_keep_line | near_miss | 11 | 1 | 12 |
| rf28_round1_head_on_v4pro_cap600_keep_line | resolved | 9 | 0 | 12 |

## Stability, unreadable replies, model

- **rf10_round1_head_on_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 5 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (198 sends); template resolve_v6.
- **rf28_round1_head_on_v4pro_cap600_keep_line**: exact-repeat set, 3 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 18 of 192 decision points; deepseek-v4-pro / a307abda487cd1b463329ccb945ce396 (211 sends); template resolve_v6.
