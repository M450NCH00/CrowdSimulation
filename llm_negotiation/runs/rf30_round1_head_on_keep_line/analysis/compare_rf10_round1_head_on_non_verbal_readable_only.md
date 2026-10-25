# rf30_round1_head_on_keep_line against rf10_round1_head_on, condition non_verbal

Sessions completed in both: 71 (only in the first: 0, only in the second: 0); of them, the design's: 46. **Readable only:** 25 session(s) with an unreadable reply in either run left out.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf30_round1_head_on_keep_line |
| --- | --- | --- |
| all | 12 / 46: 0.26 (0.16 to 0.40) | 26 / 46: 0.57 (0.42 to 0.70) |
| layout=aligned | 5 / 21: 0.24 (0.11 to 0.45) | 12 / 21: 0.57 (0.37 to 0.76) |
| layout=apart_20cm | 7 / 25: 0.28 (0.14 to 0.48) | 14 / 25: 0.56 (0.37 to 0.73) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 7 | 5 |
| not resolved in the first | 19 | 15 |

McNemar's exact test (two-sided) on the 24 sessions that changed: p = 0.0066.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 9 | 13 | 10 |
| rf10_round1_head_on | near_miss | 1 | 1 | 0 |
| rf10_round1_head_on | resolved | 12 | 0 | 0 |
| rf30_round1_head_on_keep_line | collision | 0 | 13 | 5 |
| rf30_round1_head_on_keep_line | near_miss | 2 | 0 | 0 |
| rf30_round1_head_on_keep_line | resolved | 22 | 0 | 4 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 5 of 8 cells with one `plan_only` outcome in every run (18 runs); unreadable after the retry, 0 of 402 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (402 sends); template resolve_v6.
- **rf30_round1_head_on_keep_line**: exact-repeat set, 4 of 8 cells with one `plan_only` outcome in every run (18 runs); unreadable after the retry, 0 of 382 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (387 sends); template resolve_v6.
