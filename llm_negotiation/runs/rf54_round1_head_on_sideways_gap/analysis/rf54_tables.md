# RF-54 against RF-40, silent: 256 design sessions in both

## Resolved in plan_only (all four repeats)

| Group | RF-40 | RF-54 | lost | gained | McNemar p |
| --- | --- | --- | --- | --- | --- |
| all | 163/256 | 191/256 | 40 | 68 | 0.0091 |
| layout=aligned | 91/128 | 98/128 | 19 | 26 | 0.3713 |
| layout=apart_20cm | 72/128 | 93/128 | 21 | 42 | 0.0111 |

## RF-40's own churn between two of its repeats (64 cells), the noise floor

| repeats | lost | gained | McNemar p |
| --- | --- | --- | --- |
| 1 and 2 | 16 | 13 | 0.7111 |
| 1 and 3 | 17 | 12 | 0.4583 |
| 1 and 4 | 14 | 17 | 0.7201 |
| 2 and 3 | 14 | 12 | 0.8450 |
| 2 and 4 | 10 | 16 | 0.3269 |
| 3 and 4 | 10 | 18 | 0.1849 |

## How they started, and recovery (analysis.start_walls)

## rf40_round1_head_on_turn_taking

| Start | Sessions | Resolved | Dance (both change wall at once) | Dance, failed |
| --- | --- | --- | --- | --- |
| same_wall | 111 (0.43) | 44 (0.40) | 0 | 0 |
| opposite_walls | 136 (0.53) | 115 (0.85) | 2 | 1 |
| one_never_sidesteps | 9 (0.04) | 4 (0.44) | 0 | 0 |

## rf54_round1_head_on_sideways_gap

| Start | Sessions | Resolved | Dance (both change wall at once) | Dance, failed |
| --- | --- | --- | --- | --- |
| same_wall | 97 (0.38) | 53 (0.55) | 2 | 1 |
| opposite_walls | 151 (0.59) | 133 (0.88) | 2 | 1 |
| one_never_sidesteps | 8 (0.03) | 5 (0.62) | 0 | 0 |

- same_wall, resolved: RF-54 53/97 (0.55), RF-40 44/111 (0.40), Fisher p = 0.0368
- opposite_walls, resolved: RF-54 133/151 (0.88), RF-40 115/136 (0.85), Fisher p = 0.3947
- same-wall starts: RF-54 97/256, RF-40 111/256, Fisher p = 0.2421 (decision 1's prompt is the same)
- paired starts: {"one_never_sidesteps -> one_never_sidesteps": 1, "one_never_sidesteps -> opposite_walls": 5, "one_never_sidesteps -> same_wall": 3, "opposite_walls -> one_never_sidesteps": 5, "opposite_walls -> opposite_walls": 76, "opposite_walls -> same_wall": 55, "same_wall -> one_never_sidesteps": 2, "same_wall -> opposite_walls": 70, "same_wall -> same_wall": 39}

## The reaction: a decision after both moved over 0.1 m or more towards the same wall

| Reply | RF-40 (not told) | RF-54 (told) |
| --- | --- | --- |
| back towards the other wall | 19 | 29 |
| further to the same wall | 99 | 115 |
| no sidestep | 35 | 23 |
| unreadable | 10 | 1 |
| all | 163 | 168 |

Back towards the other wall: RF-54 29/168, RF-40 19/163, Fisher p = 0.1622
