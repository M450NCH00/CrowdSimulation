# RF-39: the sidestep with a second chance

768 completed design sessions (all repeats, no counterfactual pair). Rates are resolved in `plan_only`, k / n (rate, 95% Wilson interval).

## 1. Resolved, by condition

| Condition | All repeats | First runs only |
| --- | --- | --- |
| independent | 91 / 256 (0.36, 0.30 to 0.42) | 20 / 64 (0.31, 0.21 to 0.43) |
| non_verbal | 150 / 256 (0.59, 0.52 to 0.64) | 35 / 64 (0.55, 0.43 to 0.66) |
| talk | 151 / 256 (0.59, 0.53 to 0.65) | 37 / 64 (0.58, 0.46 to 0.69) |

## 2. How the first plans stepped, and how many of each resolved

| Condition | Both to their own same side | Towards the same wall (a dance) | One or both not aside |
| --- | --- | --- | --- |
| independent | 79 / 95 (0.83, 0.74 to 0.89) | 0 / 90 (0.00, 0.00 to 0.04) | 12 / 71 (0.17, 0.10 to 0.27) |
| non_verbal | 85 / 107 (0.79, 0.71 to 0.86) | 47 / 120 (0.39, 0.31 to 0.48) | 18 / 29 (0.62, 0.44 to 0.77) |
| talk | 89 / 100 (0.89, 0.81 to 0.94) | 41 / 124 (0.33, 0.25 to 0.42) | 21 / 32 (0.66, 0.48 to 0.80) |

A dance at the start, resolved in non_verbal against independent: Fisher's exact p < 0.0001.

A dance at the start, resolved in talk against independent: Fisher's exact p < 0.0001.

## 3. How a dance at the start ended (non-verbal and talk)

| Condition | Ended | Sessions | Changed side: none / one / both | A message names a side | Someone pointed | Decision points (median) | When level: own same side / same wall / not both aside |
| --- | --- | --- | --- | --- | --- | --- | --- |
| non_verbal | resolved | 47 | 9 / 37 / 1 | 0 | 0 | 6 | 36 / 3 / 8 |
| non_verbal | not_resolved | 73 | 54 / 15 / 4 | 0 | 0 | 10 | 4 / 63 / 6 |
| talk | resolved | 41 | 3 / 37 / 1 | 9 | 1 | 5 | 36 / 1 / 4 |
| talk | not_resolved | 83 | 64 / 17 / 2 | 41 | 4 | 10 | 2 / 74 / 7 |

## 4. How the two stood when level, by outcome

| Condition | Outcome | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| independent | collision | 7 | 96 | 35 |
| independent | near_miss | 16 | 2 | 9 |
| independent | resolved | 85 | 0 | 6 |
| non_verbal | collision | 1 | 76 | 3 |
| non_verbal | near_miss | 5 | 5 | 16 |
| non_verbal | resolved | 137 | 3 | 10 |
| talk | collision | 4 | 86 | 6 |
| talk | near_miss | 0 | 3 | 6 |
| talk | resolved | 143 | 1 | 7 |

## 5. The side across a cell's 4 repeats (first plans), against a weighted coin

Units left out: {'not_aside_or_unreadable_in_some_run': 110}.

| Units | n | Right in 0 / 1 / 2 / 3 / 4 of 4 | Share right | All one way: observed (coin) | chi-square (df 1), p |
| --- | --- | --- | --- | --- | --- |
| all | 274 | 36 / 69 / 63 / 67 / 39 | 0.50 | 0.27 (0.12) | 63.82, p < 0.0001 |
| condition independent | 72 | 2 / 12 / 18 / 27 / 13 | 0.63 | 0.21 (0.18) | 2.042, p = 0.1530 |
| condition non_verbal | 102 | 13 / 27 / 21 / 23 / 18 | 0.51 | 0.30 (0.13) | 33.552, p < 0.0001 |
| condition talk | 100 | 21 / 30 / 24 / 17 / 8 | 0.40 | 0.29 (0.15) | 15.559, p = 0.0001 |
| geometry layout=aligned | 133 | 19 / 32 / 29 / 33 / 20 | 0.51 | 0.29 (0.13) | 38.819, p < 0.0001 |
| geometry layout=apart_20cm | 141 | 17 / 37 / 34 / 34 / 19 | 0.50 | 0.26 (0.12) | 25.893, p < 0.0001 |

## 6. The first side against the room each agent was told it had

More room: a wall at least 5 cm farther on one side in the first prompt.

| Geometry | Took the more-room side | Took the less-room side | Neither side had more room |
| --- | --- | --- | --- |
| layout=aligned | 0 | 0 | 697 |
| layout=apart_20cm | 366 | 337 | 0 |

## 7. What the agents said (`side_basis`, debrief v2)

| Group | Answers |
| --- | --- |
| all | more_room 604, where_they_were 547, either_side 221, custom_or_rule 52, what_they_did 50, missing 32, did_not_move_aside 30 |
| custom_or_rule: took the more-room side | False 18, True 3 |
| did_not_move_aside: took the more-room side | True 4, False 1 |
| either_side: took the more-room side | True 23, False 19 |
| more_room: took the more-room side | True 201, False 181 |
| unit_all_one_way | where_they_were 121, more_room 118, either_side 39, what_they_did 11, custom_or_rule 11 |
| unit_split | more_room 339, where_they_were 278, either_side 120, custom_or_rule 28, what_they_did 26, did_not_move_aside 5 |
| what_they_did: took the more-room side | True 14, False 13 |
| where_they_were: took the more-room side | True 121, False 105 |
