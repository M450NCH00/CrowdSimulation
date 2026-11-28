# rf28_round1_head_on_v4pro_cap600 against rf10_round1_head_on, condition independent

Sessions completed in both: 77 (only in the first: 0, only in the second: 0); of them, the design's: 48. **Readable only:** 19 session(s) with an unreadable reply in either run left out.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf28_round1_head_on_v4pro_cap600 |
| --- | --- | --- |
| all | 18 / 48: 0.38 (0.25 to 0.52) | 15 / 48: 0.31 (0.20 to 0.45) |
| layout=aligned | 8 / 25: 0.32 (0.17 to 0.52) | 10 / 25: 0.40 (0.23 to 0.59) |
| layout=apart_20cm | 10 / 23: 0.43 (0.26 to 0.63) | 5 / 23: 0.22 (0.10 to 0.42) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 5 | 13 |
| not resolved in the first | 10 | 20 |

McNemar's exact test (two-sided) on the 23 sessions that changed: p = 0.6776.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 7 | 14 | 4 |
| rf10_round1_head_on | near_miss | 4 | 0 | 1 |
| rf10_round1_head_on | resolved | 18 | 0 | 0 |
| rf28_round1_head_on_v4pro_cap600 | collision | 0 | 2 | 17 |
| rf28_round1_head_on_v4pro_cap600 | near_miss | 4 | 1 | 9 |
| rf28_round1_head_on_v4pro_cap600 | resolved | 8 | 0 | 7 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (22 runs); unreadable after the retry, 0 of 154 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (155 sends); template resolve_v6.
- **rf28_round1_head_on_v4pro_cap600**: exact-repeat set, 3 of 8 cells with one `plan_only` outcome in every run (22 runs); unreadable after the retry, 0 of 154 decision points; deepseek-v4-pro / a307abda487cd1b463329ccb945ce396 (155 sends); template resolve_v6.
