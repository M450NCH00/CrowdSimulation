# rf27_round1_head_on_v7_keep_line against rf10_round1_head_on_keep_line, condition independent

Sessions completed in both: 88 (only in the first: 0, only in the second: 0); of them, the design's: 59. **Readable only:** 8 session(s) with an unreadable reply in either run left out.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on_keep_line | rf27_round1_head_on_v7_keep_line |
| --- | --- | --- |
| all | 34 / 59: 0.58 (0.45 to 0.69) | 24 / 59: 0.41 (0.29 to 0.53) |
| layout=aligned | 19 / 30: 0.63 (0.46 to 0.78) | 13 / 30: 0.43 (0.27 to 0.61) |
| layout=apart_20cm | 15 / 29: 0.52 (0.34 to 0.69) | 11 / 29: 0.38 (0.23 to 0.56) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 15 | 19 |
| not resolved in the first | 9 | 16 |

McNemar's exact test (two-sided) on the 28 sessions that changed: p = 0.0872.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on_keep_line | collision | 3 | 16 | 4 |
| rf10_round1_head_on_keep_line | near_miss | 1 | 1 | 0 |
| rf10_round1_head_on_keep_line | resolved | 31 | 1 | 2 |
| rf27_round1_head_on_v7_keep_line | collision | 8 | 16 | 6 |
| rf27_round1_head_on_v7_keep_line | near_miss | 4 | 1 | 0 |
| rf27_round1_head_on_v7_keep_line | resolved | 21 | 1 | 2 |

## Stability, unreadable replies, model

- **rf10_round1_head_on_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (20 runs); unreadable after the retry, 0 of 176 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (177 sends); template resolve_v6.
- **rf27_round1_head_on_v7_keep_line**: exact-repeat set, 3 of 8 cells with one `plan_only` outcome in every run (20 runs); unreadable after the retry, 0 of 176 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (178 sends); template resolve_v7.
