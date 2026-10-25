# rf28_round1_head_on_v4pro_cap600_keep_line against rf10_round1_head_on_keep_line, condition independent

Sessions completed in both: 77 (only in the first: 0, only in the second: 0); of them, the design's: 48. **Readable only:** 19 session(s) with an unreadable reply in either run left out.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on_keep_line | rf28_round1_head_on_v4pro_cap600_keep_line |
| --- | --- | --- |
| all | 28 / 48: 0.58 (0.44 to 0.71) | 17 / 48: 0.35 (0.23 to 0.50) |
| layout=aligned | 14 / 25: 0.56 (0.37 to 0.73) | 11 / 25: 0.44 (0.27 to 0.63) |
| layout=apart_20cm | 14 / 23: 0.61 (0.41 to 0.78) | 6 / 23: 0.26 (0.13 to 0.46) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 9 | 19 |
| not resolved in the first | 8 | 12 |

McNemar's exact test (two-sided) on the 27 sessions that changed: p = 0.0522.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on_keep_line | collision | 3 | 12 | 4 |
| rf10_round1_head_on_keep_line | near_miss | 0 | 1 | 0 |
| rf10_round1_head_on_keep_line | resolved | 26 | 1 | 1 |
| rf28_round1_head_on_v4pro_cap600_keep_line | collision | 0 | 1 | 16 |
| rf28_round1_head_on_v4pro_cap600_keep_line | near_miss | 4 | 1 | 9 |
| rf28_round1_head_on_v4pro_cap600_keep_line | resolved | 9 | 0 | 8 |

## Stability, unreadable replies, model

- **rf10_round1_head_on_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (22 runs); unreadable after the retry, 0 of 154 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (155 sends); template resolve_v6.
- **rf28_round1_head_on_v4pro_cap600_keep_line**: exact-repeat set, 3 of 8 cells with one `plan_only` outcome in every run (22 runs); unreadable after the retry, 0 of 154 decision points; deepseek-v4-pro / a307abda487cd1b463329ccb945ce396 (155 sends); template resolve_v6.
