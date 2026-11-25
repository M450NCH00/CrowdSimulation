# rf39_round1_head_on_sidestep_reprompt against rf30_round1_head_on_keep_line, condition talk

Sessions completed in both: 96 (only in the first: 0, only in the second: 176); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf30_round1_head_on_keep_line | rf39_round1_head_on_sidestep_reprompt |
| --- | --- | --- |
| all | 30 / 64: 0.47 (0.35 to 0.59) | 37 / 64: 0.58 (0.46 to 0.69) |
| layout=aligned | 16 / 32: 0.50 (0.34 to 0.66) | 19 / 32: 0.59 (0.42 to 0.74) |
| layout=apart_20cm | 14 / 32: 0.44 (0.28 to 0.61) | 18 / 32: 0.56 (0.39 to 0.72) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 20 | 10 |
| not resolved in the first | 17 | 17 |

McNemar's exact test (two-sided) on the 27 sessions that changed: p = 0.2478.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf30_round1_head_on_keep_line | collision | 1 | 19 | 6 |
| rf30_round1_head_on_keep_line | near_miss | 1 | 2 | 5 |
| rf30_round1_head_on_keep_line | resolved | 27 | 1 | 2 |
| rf39_round1_head_on_sidestep_reprompt | collision | 0 | 21 | 3 |
| rf39_round1_head_on_sidestep_reprompt | near_miss | 0 | 1 | 2 |
| rf39_round1_head_on_sidestep_reprompt | resolved | 36 | 0 | 1 |

## Stability, unreadable replies, model

- **rf30_round1_head_on_keep_line**: exact-repeat set, 1 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 6 of 524 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (531 sends); template resolve_v6.
- **rf39_round1_head_on_sidestep_reprompt**: exact-repeat set, 58 of 64 cells with one `plan_only` outcome in every run (80 runs); unreadable after the retry, 11 of 613 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (633 sends); template resolve_v8.
