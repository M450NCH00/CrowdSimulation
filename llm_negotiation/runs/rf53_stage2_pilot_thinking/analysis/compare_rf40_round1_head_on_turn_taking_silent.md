# rf53_stage2_pilot_thinking against rf40_round1_head_on_turn_taking, condition silent

Sessions completed in both: 80 (only in the first: 192, only in the second: 0); of them, the design's: 64.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf40_round1_head_on_turn_taking | rf53_stage2_pilot_thinking |
| --- | --- | --- |
| all | 42 / 64: 0.66 (0.53 to 0.76) | 46 / 64: 0.72 (0.60 to 0.81) |
| layout=aligned | 25 / 32: 0.78 (0.61 to 0.89) | 24 / 32: 0.75 (0.58 to 0.87) |
| layout=apart_20cm | 17 / 32: 0.53 (0.36 to 0.69) | 22 / 32: 0.69 (0.51 to 0.82) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 28 | 14 |
| not resolved in the first | 18 | 4 |

McNemar's exact test (two-sided) on the 32 sessions that changed: p = 0.5966.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf40_round1_head_on_turn_taking | collision | 1 | 15 | 2 |
| rf40_round1_head_on_turn_taking | near_miss | 3 | 0 | 1 |
| rf40_round1_head_on_turn_taking | resolved | 40 | 0 | 2 |
| rf53_stage2_pilot_thinking | collision | 5 | 2 | 4 |
| rf53_stage2_pilot_thinking | near_miss | 2 | 1 | 4 |
| rf53_stage2_pilot_thinking | resolved | 45 | 0 | 1 |

## Stability, unreadable replies, model

- **rf40_round1_head_on_turn_taking**: exact-repeat set, 64 of 64 cells with one `plan_only` outcome in every run (64 runs); unreadable after the retry, 11 of 473 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (490 sends); template resolve_v9.
- **rf53_stage2_pilot_thinking**: exact-repeat set, 0 of 0 cells with one `plan_only` outcome in every run (0 runs); unreadable after the retry, 10 of 459 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (472 sends); template resolve_v9.
