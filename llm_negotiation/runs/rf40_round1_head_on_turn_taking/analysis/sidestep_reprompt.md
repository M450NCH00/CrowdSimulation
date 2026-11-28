# RF-39: the sidestep with a second chance

768 completed design sessions (all repeats, no counterfactual pair). Rates are resolved in `plan_only`, k / n (rate, 95% Wilson interval).

## 1. Resolved, by condition

| Condition | All repeats | First runs only |
| --- | --- | --- |
| silent | 163 / 256 (0.64, 0.58 to 0.69) | 42 / 64 (0.66, 0.53 to 0.76) |
| non_verbal | 144 / 256 (0.56, 0.50 to 0.62) | 40 / 64 (0.62, 0.50 to 0.73) |
| talk | 150 / 256 (0.59, 0.52 to 0.64) | 41 / 64 (0.64, 0.52 to 0.75) |

## 2. How the first plans stepped, and how many of each resolved

| Condition | Both to their own same side | Towards the same wall (a dance) | One or both not aside |
| --- | --- | --- | --- |
| silent | 87 / 108 (0.81, 0.72 to 0.87) | 38 / 92 (0.41, 0.32 to 0.52) | 38 / 56 (0.68, 0.55 to 0.79) |
| non_verbal | 100 / 131 (0.76, 0.68 to 0.83) | 27 / 89 (0.30, 0.22 to 0.41) | 17 / 36 (0.47, 0.32 to 0.63) |
| talk | 99 / 118 (0.84, 0.76 to 0.89) | 36 / 107 (0.34, 0.25 to 0.43) | 15 / 31 (0.48, 0.32 to 0.65) |

A dance at the start, resolved in non_verbal against silent: Fisher's exact p = 0.1629.

A dance at the start, resolved in talk against silent: Fisher's exact p = 0.3040.

## 3. How a dance at the start ended (every condition asked again)

| Condition | Ended | Sessions | Changed side: none / one / both | A message names a side | Someone pointed | Decision points (median) | When level: own same side / same wall / not both aside |
| --- | --- | --- | --- | --- | --- | --- | --- |
| silent | resolved | 38 | 1 / 37 / 0 | 0 | 0 | 6.0 | 36 / 0 / 2 |
| silent | not_resolved | 54 | 25 / 28 / 1 | 0 | 0 | 9.5 | 3 / 42 / 9 |
| non_verbal | resolved | 27 | 3 / 23 / 1 | 0 | 1 | 6 | 24 / 0 / 3 |
| non_verbal | not_resolved | 62 | 49 / 12 / 1 | 0 | 0 | 10.0 | 4 / 51 / 7 |
| talk | resolved | 36 | 2 / 33 / 1 | 10 | 1 | 6.0 | 33 / 0 / 3 |
| talk | not_resolved | 71 | 51 / 19 / 1 | 30 | 4 | 10 | 4 / 64 / 3 |

## 4. How the two stood when level, by outcome

| Condition | Outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| silent | collision | 7 | 58 | 9 |
| silent | near_miss | 6 | 3 | 10 |
| silent | resolved | 156 | 0 | 7 |
| non_verbal | collision | 4 | 66 | 12 |
| non_verbal | near_miss | 9 | 6 | 15 |
| non_verbal | resolved | 131 | 1 | 12 |
| talk | collision | 3 | 86 | 2 |
| talk | near_miss | 4 | 4 | 7 |
| talk | resolved | 141 | 0 | 9 |

## 5. The side across a cell's 4 repeats (first plans), against a weighted coin

Units left out: {'not_aside_or_unreadable_in_some_run': 102}.

| Units | n | Right in 0 / 1 / 2 / 3 / 4 of 4 | Share right | All one way: observed (coin) | chi-square (df 1), p |
| --- | --- | --- | --- | --- | --- |
| all | 282 | 14 / 48 / 68 / 83 / 69 | 0.63 | 0.29 (0.18) | 29.878, p < 0.0001 |
| condition non_verbal | 99 | 5 / 14 / 23 / 30 / 27 | 0.65 | 0.32 (0.19) | 10.784, p = 0.0010 |
| condition silent | 84 | 0 / 11 / 18 / 29 / 26 | 0.71 | 0.31 (0.26) | 1.415, p = 0.2342 |
| condition talk | 99 | 9 / 23 / 27 / 24 / 16 | 0.54 | 0.25 (0.13) | 14.314, p = 0.0002 |
| geometry layout=aligned | 135 | 5 / 21 / 31 / 40 / 38 | 0.66 | 0.32 (0.20) | 12.352, p = 0.0004 |
| geometry layout=apart_20cm | 147 | 9 / 27 / 37 / 43 / 31 | 0.60 | 0.27 (0.16) | 16.392, p = 0.0001 |

## 6. The first side against the room each agent was told it had

More room: a wall at least 5 cm farther on one side in the first prompt.

| Geometry | Took the more-room side | Took the less-room side | Neither side had more room |
| --- | --- | --- | --- |
| layout=aligned | 0 | 0 | 696 |
| layout=apart_20cm | 432 | 282 | 0 |

## 7. What the agents said (`side_basis`, debrief v2)

| Group | Answers |
| --- | --- |
| all | where_they_were 739, more_room 514, either_side 130, what_they_did 96, custom_or_rule 28, did_not_move_aside 27, missing 2 |
| custom_or_rule: took the more-room side | False 7, True 1 |
| did_not_move_aside: took the more-room side | True 5, False 3 |
| either_side: took the more-room side | True 12, False 10 |
| missing: took the more-room side | False 1 |
| more_room: took the more-room side | True 193, False 99 |
| unit_all_one_way | where_they_were 143, more_room 127, either_side 34, what_they_did 21, custom_or_rule 5, did_not_move_aside 2 |
| unit_split | where_they_were 376, more_room 295, either_side 55, what_they_did 50, custom_or_rule 17, did_not_move_aside 3 |
| what_they_did: took the more-room side | True 27, False 15 |
| where_they_were: took the more-room side | True 194, False 147 |
