# rf29_round1_head_on_sidestep_keep_line against rf10_round1_head_on_keep_line, condition independent

Sessions completed in both: 89 (only in the first: 0, only in the second: 0); of them, the design's: 58. **Readable only:** 7 session(s) with an unreadable reply in either run left out.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on_keep_line | rf29_round1_head_on_sidestep_keep_line |
| --- | --- | --- |
| all | 33 / 58: 0.57 (0.44 to 0.69) | 27 / 58: 0.47 (0.34 to 0.59) |
| layout=aligned | 19 / 30: 0.63 (0.46 to 0.78) | 18 / 30: 0.60 (0.42 to 0.75) |
| layout=apart_20cm | 14 / 28: 0.50 (0.33 to 0.67) | 9 / 28: 0.32 (0.18 to 0.51) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 15 | 18 |
| not resolved in the first | 12 | 13 |

McNemar's exact test (two-sided) on the 30 sessions that changed: p = 0.3616.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on_keep_line | collision | 3 | 16 | 4 |
| rf10_round1_head_on_keep_line | near_miss | 1 | 1 | 0 |
| rf10_round1_head_on_keep_line | resolved | 30 | 1 | 2 |
| rf29_round1_head_on_sidestep_keep_line | collision | 3 | 22 | 2 |
| rf29_round1_head_on_sidestep_keep_line | near_miss | 3 | 1 | 0 |
| rf29_round1_head_on_sidestep_keep_line | resolved | 26 | 0 | 1 |

## Stability, unreadable replies, model

- **rf10_round1_head_on_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (22 runs); unreadable after the retry, 0 of 178 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (179 sends); template resolve_v6.
- **rf29_round1_head_on_sidestep_keep_line**: exact-repeat set, 2 of 8 cells with one `plan_only` outcome in every run (22 runs); unreadable after the retry, 0 of 178 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (178 sends); template resolve_v8.
