# RF-55 against RF-40 and RF-54, silent: 256 design sessions in all three

## Resolved in plan_only (all four repeats)

| Group | RF-40 (v9) | RF-55 (v12) | RF-54 (v11) | RF-55 vs RF-40: lost, gained, p | RF-54 vs RF-55: lost, gained, p |
| --- | --- | --- | --- | --- | --- |
| all | 163/256 (0.64) | 206/256 (0.80) | 191/256 (0.75) | 28, 71, 0.0000 | 49, 34, 0.1239 |
| layout=aligned | 91/128 (0.71) | 100/128 (0.78) | 98/128 (0.77) | 16, 25, 0.2110 | 23, 21, 0.8804 |
| layout=apart_20cm | 72/128 (0.56) | 106/128 (0.83) | 93/128 (0.73) | 12, 46, 0.0000 | 26, 13, 0.0533 |

## How they started, and recovery (analysis.start_walls)

## RF-40 (rf40_round1_head_on_turn_taking)

| Start | Sessions | Resolved | Dance (both change wall at once) | Dance, failed |
| --- | --- | --- | --- | --- |
| same_wall | 111 (0.43) | 44 (0.40) | 0 | 0 |
| opposite_walls | 136 (0.53) | 115 (0.85) | 2 | 1 |
| one_never_sidesteps | 9 (0.04) | 4 (0.44) | 0 | 0 |

## RF-54 (rf54_round1_head_on_sideways_gap)

| Start | Sessions | Resolved | Dance (both change wall at once) | Dance, failed |
| --- | --- | --- | --- | --- |
| same_wall | 97 (0.38) | 53 (0.55) | 2 | 1 |
| opposite_walls | 151 (0.59) | 133 (0.88) | 2 | 1 |
| one_never_sidesteps | 8 (0.03) | 5 (0.62) | 0 | 0 |

## RF-55 (rf55_round1_head_on_short_moved)

| Start | Sessions | Resolved | Dance (both change wall at once) | Dance, failed |
| --- | --- | --- | --- | --- |
| same_wall | 112 (0.44) | 79 (0.71) | 9 | 4 |
| opposite_walls | 134 (0.52) | 119 (0.89) | 3 | 0 |
| one_never_sidesteps | 10 (0.04) | 8 (0.80) | 0 | 0 |

- same_wall, resolved: RF-40 44/111 (0.40), RF-55 79/112 (0.71), RF-54 53/97 (0.55); RF-55 against RF-40, Fisher p = 0.0000
- opposite_walls, resolved: RF-40 115/136 (0.85), RF-55 119/134 (0.89), RF-54 133/151 (0.88); RF-55 against RF-40, Fisher p = 0.3715

## The reaction: a decision after both moved over 0.1 m or more towards the same wall

| Reply | RF-40 (not told) | RF-55 (told they moved) | RF-54 (told the gap) |
| --- | --- | --- | --- |
| back towards the other wall | 19 | 74 | 29 |
| further to the same wall | 99 | 97 | 115 |
| no sidestep | 35 | 12 | 23 |
| unreadable | 10 | 1 | 1 |
| all | 163 | 184 | 168 |

Back towards the other wall: RF-55 74/184, RF-40 19/163, Fisher p = 0.0000
