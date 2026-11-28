# rf54_round1_head_on_sideways_gap against rf40_round1_head_on_turn_taking, condition silent

Sessions completed in both: 272 (only in the first: 0, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf40_round1_head_on_turn_taking | rf54_round1_head_on_sideways_gap |
| --- | --- | --- |
| all | 42 / 64: 0.66 (0.53 to 0.76) | 47 / 64: 0.73 (0.62 to 0.83) |
| layout=aligned | 25 / 32: 0.78 (0.61 to 0.89) | 23 / 32: 0.72 (0.55 to 0.84) |
| layout=apart_20cm | 17 / 32: 0.53 (0.36 to 0.69) | 24 / 32: 0.75 (0.58 to 0.87) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 27 | 15 |
| not resolved in the first | 20 | 2 |

McNemar's exact test (two-sided) on the 35 sessions that changed: p = 0.4996.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf40_round1_head_on_turn_taking | collision | 1 | 15 | 2 |
| rf40_round1_head_on_turn_taking | near_miss | 3 | 0 | 1 |
| rf40_round1_head_on_turn_taking | resolved | 40 | 0 | 2 |
| rf54_round1_head_on_sideways_gap | collision | 0 | 8 | 0 |
| rf54_round1_head_on_sideways_gap | near_miss | 5 | 0 | 4 |
| rf54_round1_head_on_sideways_gap | resolved | 43 | 0 | 4 |

## Stability, unreadable replies, model

- **rf40_round1_head_on_turn_taking**: exact-repeat set, 14 of 64 cells with one `plan_only` outcome in every run (256 runs); unreadable after the retry, 52 of 1657 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (1721 sends); template resolve_v9.
- **rf54_round1_head_on_sideways_gap**: exact-repeat set, 22 of 64 cells with one `plan_only` outcome in every run (256 runs); unreadable after the retry, 58 of 1519 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (1591 sends); template resolve_v11.
