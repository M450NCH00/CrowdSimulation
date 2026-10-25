# rf28_round1_head_on_v4pro_cap600 against rf10_round1_head_on, condition independent

Sessions completed in both: 96 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf28_round1_head_on_v4pro_cap600 |
| --- | --- | --- |
| all | 22 / 64: 0.34 (0.24 to 0.47) | 18 / 64: 0.28 (0.19 to 0.40) |
| layout=aligned | 11 / 32: 0.34 (0.20 to 0.52) | 11 / 32: 0.34 (0.20 to 0.52) |
| layout=apart_20cm | 11 / 32: 0.34 (0.20 to 0.52) | 7 / 32: 0.22 (0.11 to 0.39) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 6 | 16 |
| not resolved in the first | 12 | 30 |

McNemar's exact test (two-sided) on the 28 sessions that changed: p = 0.5716.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 9 | 18 | 10 |
| rf10_round1_head_on | near_miss | 4 | 0 | 1 |
| rf10_round1_head_on | resolved | 22 | 0 | 0 |
| rf28_round1_head_on_v4pro_cap600 | collision | 0 | 2 | 20 |
| rf28_round1_head_on_v4pro_cap600 | near_miss | 12 | 1 | 11 |
| rf28_round1_head_on_v4pro_cap600 | resolved | 8 | 0 | 10 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 5 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (198 sends); template resolve_v6.
- **rf28_round1_head_on_v4pro_cap600**: exact-repeat set, 3 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 18 of 192 decision points; deepseek-v4-pro / a307abda487cd1b463329ccb945ce396 (211 sends); template resolve_v6.
