# rf30_round1_head_on_keep_line against rf10_round1_head_on, condition talk

Sessions completed in both: 96 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf30_round1_head_on_keep_line |
| --- | --- | --- |
| all | 20 / 64: 0.31 (0.21 to 0.43) | 30 / 64: 0.47 (0.35 to 0.59) |
| layout=aligned | 13 / 32: 0.41 (0.26 to 0.58) | 16 / 32: 0.50 (0.34 to 0.66) |
| layout=apart_20cm | 7 / 32: 0.22 (0.11 to 0.39) | 14 / 32: 0.44 (0.28 to 0.61) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 10 | 10 |
| not resolved in the first | 20 | 24 |

McNemar's exact test (two-sided) on the 30 sessions that changed: p = 0.0987.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 7 | 12 | 17 |
| rf10_round1_head_on | near_miss | 6 | 0 | 2 |
| rf10_round1_head_on | resolved | 17 | 0 | 3 |
| rf30_round1_head_on_keep_line | collision | 1 | 19 | 6 |
| rf30_round1_head_on_keep_line | near_miss | 1 | 2 | 5 |
| rf30_round1_head_on_keep_line | resolved | 27 | 1 | 2 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 1 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 8 of 547 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (557 sends); template resolve_v6.
- **rf30_round1_head_on_keep_line**: exact-repeat set, 1 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 6 of 524 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (531 sends); template resolve_v6.
