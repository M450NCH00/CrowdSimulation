## rf40_round1_head_on_turn_taking: 256 design sessions, silent

| plan_only outcome | how they stepped when level | sessions |
| --- | --- | --- |
| collision | not_both_aside | 9 |
| collision | same_own_side | 7 |
| collision | towards_same_wall | 58 |
| near_miss | not_both_aside | 10 |
| near_miss | same_own_side | 6 |
| near_miss | towards_same_wall | 3 |
| resolved | not_both_aside | 7 |
| resolved | same_own_side | 156 |

| plan_only outcome | failure mode | sessions |
| --- | --- | --- |
| collision | a sidestep reversed | 33 |
| collision | no reversal | 36 |
| collision | one never sidesteps | 5 |
| near_miss | a sidestep reversed | 12 |
| near_miss | no reversal | 7 |
| resolved | a sidestep reversed | 55 |
| resolved | no reversal | 104 |
| resolved | one never sidesteps | 4 |

## rf53_stage2_pilot_thinking: 64 design sessions, silent

| plan_only outcome | how they stepped when level | sessions |
| --- | --- | --- |
| collision | not_both_aside | 4 |
| collision | same_own_side | 5 |
| collision | towards_same_wall | 2 |
| near_miss | not_both_aside | 4 |
| near_miss | same_own_side | 2 |
| near_miss | towards_same_wall | 1 |
| resolved | not_both_aside | 1 |
| resolved | same_own_side | 45 |

| plan_only outcome | failure mode | sessions |
| --- | --- | --- |
| collision | a sidestep reversed | 8 |
| collision | one never sidesteps | 3 |
| near_miss | a sidestep reversed | 5 |
| near_miss | one never sidesteps | 2 |
| resolved | a sidestep reversed | 11 |
| resolved | no reversal | 34 |
| resolved | one never sidesteps | 1 |

## RF-40's own churn between repeats (silent, 64 cells)

| repeats | changed | resolved, first | resolved, second |
| --- | --- | --- | --- |
| 1 and 2 | 29 | 42 | 39 |
| 1 and 3 | 29 | 42 | 37 |
| 1 and 4 | 31 | 42 | 45 |
| 2 and 3 | 26 | 39 | 37 |
| 2 and 4 | 26 | 39 | 45 |
| 3 and 4 | 28 | 37 | 45 |

## Fisher exact tests, two-sided (pilot 64 against RF-40's 256)

- resolved: pilot 46/64, RF-40 163/256, p = 0.2424
- both towards the same wall: pilot 3/64, RF-40 61/256, p = 0.0004
- both to their own same side: pilot 52/64, RF-40 169/256, p = 0.0227
