# rf39_round1_head_on_sidestep_reprompt against rf29_round1_head_on_sidestep_keep_line, condition independent

Sessions completed in both: 96 (only in the first: 0, only in the second: 176); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf29_round1_head_on_sidestep_keep_line | rf39_round1_head_on_sidestep_reprompt |
| --- | --- | --- |
| all | 27 / 64: 0.42 (0.31 to 0.54) | 20 / 64: 0.31 (0.21 to 0.43) |
| layout=aligned | 18 / 32: 0.56 (0.39 to 0.72) | 12 / 32: 0.38 (0.23 to 0.55) |
| layout=apart_20cm | 9 / 32: 0.28 (0.16 to 0.45) | 8 / 32: 0.25 (0.13 to 0.42) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 9 | 18 |
| not resolved in the first | 11 | 26 |

McNemar's exact test (two-sided) on the 29 sessions that changed: p = 0.2649.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf29_round1_head_on_sidestep_keep_line | collision | 4 | 25 | 3 |
| rf29_round1_head_on_sidestep_keep_line | near_miss | 4 | 1 | 0 |
| rf29_round1_head_on_sidestep_keep_line | resolved | 26 | 0 | 1 |
| rf39_round1_head_on_sidestep_reprompt | collision | 2 | 25 | 9 |
| rf39_round1_head_on_sidestep_reprompt | near_miss | 2 | 0 | 6 |
| rf39_round1_head_on_sidestep_reprompt | resolved | 19 | 0 | 1 |

## Stability, unreadable replies, model

- **rf29_round1_head_on_sidestep_keep_line**: exact-repeat set, 1 of 8 cells with one `plan_only` outcome in every run (24 runs); unreadable after the retry, 2 of 192 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (194 sends); template resolve_v8.
- **rf39_round1_head_on_sidestep_reprompt**: exact-repeat set, 58 of 64 cells with one `plan_only` outcome in every run (80 runs); unreadable after the retry, 8 of 192 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (202 sends); template resolve_v8.
