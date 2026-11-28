# rf29_round1_head_on_sidestep against rf10_round1_head_on, condition independent

Sessions completed in both: 89 (only in the first: 0, only in the second: 0); of them, the design's: 58. **Readable only:** 7 session(s) with an unreadable reply in either run left out.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf29_round1_head_on_sidestep |
| --- | --- | --- |
| all | 21 / 58: 0.36 (0.25 to 0.49) | 4 / 58: 0.07 (0.03 to 0.16) |
| layout=aligned | 11 / 30: 0.37 (0.22 to 0.54) | 2 / 30: 0.07 (0.02 to 0.21) |
| layout=apart_20cm | 10 / 28: 0.36 (0.21 to 0.54) | 2 / 28: 0.07 (0.02 to 0.23) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 1 | 20 |
| not resolved in the first | 3 | 34 |

McNemar's exact test (two-sided) on the 23 sessions that changed: p = 0.0005.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 9 | 18 | 5 |
| rf10_round1_head_on | near_miss | 4 | 0 | 1 |
| rf10_round1_head_on | resolved | 21 | 0 | 0 |
| rf29_round1_head_on_sidestep | collision | 18 | 14 | 16 |
| rf29_round1_head_on_sidestep | near_miss | 4 | 2 | 0 |
| rf29_round1_head_on_sidestep | resolved | 3 | 0 | 1 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (22 runs); unreadable after the retry, 0 of 178 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (179 sends); template resolve_v6.
- **rf29_round1_head_on_sidestep**: exact-repeat set, 8 of 8 cells with one `plan_only` outcome in every run (22 runs); unreadable after the retry, 0 of 178 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (178 sends); template resolve_v8.
