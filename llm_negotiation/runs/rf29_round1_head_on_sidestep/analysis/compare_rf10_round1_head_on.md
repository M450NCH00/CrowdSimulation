# rf29_round1_head_on_sidestep against rf10_round1_head_on, condition independent

Sessions completed in both: 96 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf29_round1_head_on_sidestep |
| --- | --- | --- |
| all | 22 / 64: 0.34 (0.24 to 0.47) | 4 / 64: 0.06 (0.02 to 0.15) |
| layout=aligned | 11 / 32: 0.34 (0.20 to 0.52) | 2 / 32: 0.06 (0.02 to 0.20) |
| layout=apart_20cm | 11 / 32: 0.34 (0.20 to 0.52) | 2 / 32: 0.06 (0.02 to 0.20) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 1 | 21 |
| not resolved in the first | 3 | 39 |

McNemar's exact test (two-sided) on the 24 sessions that changed: p = 0.0003.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 9 | 18 | 10 |
| rf10_round1_head_on | near_miss | 4 | 0 | 1 |
| rf10_round1_head_on | resolved | 22 | 0 | 0 |
| rf29_round1_head_on_sidestep | collision | 20 | 17 | 17 |
| rf29_round1_head_on_sidestep | near_miss | 4 | 2 | 0 |
| rf29_round1_head_on_sidestep | resolved | 3 | 0 | 1 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 5 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (198 sends); template resolve_v6.
- **rf29_round1_head_on_sidestep**: exact-repeat set, 8 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 2 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (194 sends); template resolve_v8.
