# rf27_round1_head_on_v7 against rf10_round1_head_on, condition independent

Sessions completed in both: 96 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf27_round1_head_on_v7 |
| --- | --- | --- |
| all | 22 / 64: 0.34 (0.24 to 0.47) | 17 / 64: 0.27 (0.17 to 0.38) |
| layout=aligned | 11 / 32: 0.34 (0.20 to 0.52) | 10 / 32: 0.31 (0.18 to 0.49) |
| layout=apart_20cm | 11 / 32: 0.34 (0.20 to 0.52) | 7 / 32: 0.22 (0.11 to 0.39) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 6 | 16 |
| not resolved in the first | 11 | 31 |

McNemar's exact test (two-sided) on the 27 sessions that changed: p = 0.4421.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 9 | 18 | 10 |
| rf10_round1_head_on | near_miss | 4 | 0 | 1 |
| rf10_round1_head_on | resolved | 22 | 0 | 0 |
| rf27_round1_head_on_v7 | collision | 14 | 18 | 9 |
| rf27_round1_head_on_v7 | near_miss | 4 | 0 | 2 |
| rf27_round1_head_on_v7 | resolved | 17 | 0 | 0 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 5 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (198 sends); template resolve_v6.
- **rf27_round1_head_on_v7**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 3 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (197 sends); template resolve_v7.
