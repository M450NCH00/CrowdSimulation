# rf55_round1_head_on_short_moved against rf40_round1_head_on_turn_taking, condition silent

Sessions completed in both: 272 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf40_round1_head_on_turn_taking | rf55_round1_head_on_short_moved |
| --- | --- | --- |
| all | 42 / 64: 0.66 (0.53 to 0.76) | 51 / 64: 0.80 (0.68 to 0.88) |
| layout=aligned | 25 / 32: 0.78 (0.61 to 0.89) | 26 / 32: 0.81 (0.65 to 0.91) |
| layout=apart_20cm | 17 / 32: 0.53 (0.36 to 0.69) | 25 / 32: 0.78 (0.61 to 0.89) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 35 | 7 |
| not resolved in the first | 16 | 6 |

McNemar's exact test (two-sided) on the 23 sessions that changed: p = 0.0931.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf40_round1_head_on_turn_taking | collision | 1 | 15 | 2 |
| rf40_round1_head_on_turn_taking | near_miss | 3 | 0 | 1 |
| rf40_round1_head_on_turn_taking | resolved | 40 | 0 | 2 |
| rf55_round1_head_on_short_moved | collision | 0 | 8 | 2 |
| rf55_round1_head_on_short_moved | near_miss | 2 | 0 | 1 |
| rf55_round1_head_on_short_moved | resolved | 46 | 1 | 4 |

## Stability, unreadable replies, model

- **rf40_round1_head_on_turn_taking**: exact-repeat set, 14 of 64 cells with one `plan_only` outcome in every run (256 runs); unreadable after the retry, 52 of 1657 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (1721 sends); template resolve_v9.
- **rf55_round1_head_on_short_moved**: exact-repeat set, 31 of 64 cells with one `plan_only` outcome in every run (256 runs); unreadable after the retry, 35 of 1524 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (1572 sends); template resolve_v12.
