# rf30_round1_head_on_keep_line against rf10_round1_head_on, condition talk

Sessions completed in both: 82 (only in the first: 0, only in the second: 0); of them, the design's: 56. **Readable only:** 14 session(s) with an unreadable reply in either run left out.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf10_round1_head_on | rf30_round1_head_on_keep_line |
| --- | --- | --- |
| all | 20 / 56: 0.36 (0.24 to 0.49) | 28 / 56: 0.50 (0.37 to 0.63) |
| layout=aligned | 13 / 28: 0.46 (0.30 to 0.64) | 15 / 28: 0.54 (0.36 to 0.70) |
| layout=apart_20cm | 7 / 28: 0.25 (0.13 to 0.43) | 13 / 28: 0.46 (0.30 to 0.64) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 10 | 10 |
| not resolved in the first | 18 | 18 |

McNemar's exact test (two-sided) on the 28 sessions that changed: p = 0.1849.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf10_round1_head_on | collision | 7 | 11 | 15 |
| rf10_round1_head_on | near_miss | 2 | 0 | 1 |
| rf10_round1_head_on | resolved | 17 | 0 | 3 |
| rf30_round1_head_on_keep_line | collision | 1 | 16 | 5 |
| rf30_round1_head_on_keep_line | near_miss | 1 | 1 | 4 |
| rf30_round1_head_on_keep_line | resolved | 25 | 1 | 2 |

## Stability, unreadable replies, model

- **rf10_round1_head_on**: exact-repeat set, 1 of 8 cells with one `plan_only` outcome in every run (19 runs); unreadable after the retry, 0 of 465 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (466 sends); template resolve_v6.
- **rf30_round1_head_on_keep_line**: exact-repeat set, 4 of 8 cells with one `plan_only` outcome in every run (19 runs); unreadable after the retry, 0 of 445 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (446 sends); template resolve_v6.
