# rf39_round1_head_on_sidestep_reprompt against rf29_round1_head_on_sidestep_keep_line, condition independent

Sessions completed in both: 86 (only in the first: 0, only in the second: 176); of them, the design's: 57. **Readable only:** 10 session(s) with an unreadable reply in either run left out.

## Resolved in `plan_only` (the design's sessions; 95% Wilson intervals)

| Group | rf29_round1_head_on_sidestep_keep_line | rf39_round1_head_on_sidestep_reprompt |
| --- | --- | --- |
| all | 24 / 57: 0.42 (0.30 to 0.55) | 20 / 57: 0.35 (0.24 to 0.48) |
| layout=aligned | 15 / 28: 0.54 (0.36 to 0.70) | 12 / 28: 0.43 (0.27 to 0.61) |
| layout=apart_20cm | 9 / 29: 0.31 (0.17 to 0.49) | 8 / 29: 0.28 (0.15 to 0.46) |

## The same sessions, paired

| | resolved in the second | not resolved in the second |
| --- | --- | --- |
| resolved in the first | 9 | 15 |
| not resolved in the first | 11 | 22 |

McNemar's exact test (two-sided) on the 26 sessions that changed: p = 0.5572.

## How they stepped, when level (`analysis.lateral`)

| Run | `plan_only` outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| rf29_round1_head_on_sidestep_keep_line | collision | 3 | 23 | 2 |
| rf29_round1_head_on_sidestep_keep_line | near_miss | 4 | 1 | 0 |
| rf29_round1_head_on_sidestep_keep_line | resolved | 23 | 0 | 1 |
| rf39_round1_head_on_sidestep_reprompt | collision | 2 | 24 | 3 |
| rf39_round1_head_on_sidestep_reprompt | near_miss | 2 | 0 | 6 |
| rf39_round1_head_on_sidestep_reprompt | resolved | 19 | 0 | 1 |

## Stability, unreadable replies, model

- **rf29_round1_head_on_sidestep_keep_line**: exact-repeat set, 1 of 8 cells with one `plan_only` outcome in every run (21 runs); unreadable after the retry, 0 of 172 decision points; deepseek-flash / e72d3c7f663d3e1383b00b3884cb4501 (172 sends); template resolve_v8.
- **rf39_round1_head_on_sidestep_reprompt**: exact-repeat set, 52 of 57 cells with one `plan_only` outcome in every run (70 runs); unreadable after the retry, 0 of 172 decision points; deepseek-flash / bc19ba97cbe016479903222bb1578db6 (174 sends); template resolve_v8.
