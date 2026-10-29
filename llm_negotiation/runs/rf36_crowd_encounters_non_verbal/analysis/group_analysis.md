# rf36_crowd_encounters_non_verbal: group sessions per conflict pair (machine-written)

66 completed sessions, 60 of the design (exact-repeat copies left out).

## Resolved in plan_only, by layout

| Layout | Sessions | Resolved (95% CI) | Fisher p against round 1's pairs | plain ORCA |  |
| --- | --- | --- | --- | --- |  |
| density=per_way_25 | 32 | 0 / 32 (0.00; 0.00 to 0.11) | 0.0 | 0 |  |
| density=per_way_50 | 28 | 0 / 28 (0.00; 0.00 to 0.12) | 0.0 | 0 |  |
| all | 60 | 0 / 60 (0.00; 0.00 to 0.06) | 0.0 | 0 |  |

Round 1's pairs: 37 / 64 resolved (0.46 to 0.69); sides of the resolved: {'left/left': 14, 'right/right': 23}.

## Conflict pairs

{'n': 249, 'resolved_plan_only': 6, 'sides_plan_only': {'right/right': 6}}

## Identity check per conflict pair

| Arm | Pairs | Reproduced | Same first | Same sides | Resolved | Matched |
| --- | --- | --- | --- | --- | --- | --- |
| plain_orca (resolved_pairs) | 6 | 4 | 4 | 6 | 0 | - |
| plain_orca (all_pairs) | 249 | 171 | 179 | 236 | 0 | - |

## How friends got past each oncoming person

{'density=per_way_25': {'single_file': 64, 'abreast': 8, 'not_reached': 24}, 'density=per_way_50': {'not_reached': 26, 'single_file': 86}, 'all': {'single_file': 150, 'abreast': 8, 'not_reached': 50}}

Passed cleanly (the oncoming person resolved its pair with each friend), of each formation: {'between': [0, 0], 'single_file': [6, 150], 'abreast': [0, 8], 'not_reached': [0, 50]}

## First plans

- **alone**: {'people': 8, 'readable': 8, 'side': {'right': 5, 'none': 3}, 'slowed': 5, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 11.88, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **with_friend**: {'people': 195, 'readable': 166, 'side': {'both': 41, 'right': 65, 'none': 29, 'left': 31}, 'slowed': 105, 'stopped': 1, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 12.43, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **round1_pairs**: {'people': 128, 'readable': 123, 'side': {'left': 25, 'right': 57, 'both': 37, 'none': 4}, 'slowed': 83, 'stopped': 2, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 13.15, 'start_distance_m_mean': 3.0, 'with_start_distance': 4}
- **facing_a_cane**: {'people': 75, 'readable': 60, 'side': {'both': 14, 'none': 8, 'left': 11, 'right': 27}, 'slowed': 40, 'stopped': 1, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 13.42, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **holds_ground**: {'people': 77, 'readable': 62, 'side': {'none': 29, 'right': 13, 'both': 15, 'left': 5}, 'slowed': 21, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 6.92, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **gives_way**: {'people': 126, 'readable': 112, 'side': {'both': 26, 'right': 57, 'left': 26, 'none': 3}, 'slowed': 89, 'stopped': 1, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 15.44, 'start_distance_m_mean': None, 'with_start_distance': 0}

## Debriefs

- **groups**: {'debriefs': 216, 'kinds': {'common_sense': 107, 'habit': 101, 'none': 8}, 'terms': {'keep left': 15, 'keep right': 37, 'single file': 0, 'behind (a friend)': 34, 'between': 1, 'elderly / cane': 63}, 'sources': []}
- **round1_pairs**: {'debriefs': 128, 'kinds': {'local_custom': 9, 'habit': 52, 'common_sense': 66, 'none': 1}, 'terms': {'keep left': 27, 'keep right': 4, 'single file': 0, 'behind (a friend)': 20, 'between': 0, 'elderly / cane': 57}, 'sources': []}

Unreadable after retry: {'decision_points': 549, 'unreadable': 61}

## Against plain ORCA on the same seed (issue #117)

| Layout | Sessions | Resolved: no more collisions, none deeper, none stuck (95% CI) | Better | Same | Worse | Sign test p | Collisions, plans / plain ORCA | Stuck, plans / plain ORCA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| density=per_way_25 | 32 | 8 / 32 (0.25; 0.13 to 0.42) | 0 | 8 | 24 | 0.0 | 193 / 152 | 0 / 0 |
| density=per_way_50 | 28 | 1 / 28 (0.04; 0.01 to 0.18) | 1 | 0 | 27 | 0.0 | 294 / 169 | 0 / 0 |
| all | 60 | 9 / 60 (0.15; 0.08 to 0.26) | 1 | 8 | 51 | 0.0 | 487 / 321 | 0 / 0 |

Resolved with depths within a tolerance counted as equal (not the measure of record): density=per_way_25: 5 mm 8, 10 mm 15; density=per_way_50: 5 mm 6, 10 mm 6; all: 5 mm 14, 10 mm 21

## Resolved in plan_only, by the number of people in the encounter

| People | Sessions | Resolved (95% CI) |
| --- | --- | --- |
| 4 | 60 | 0 / 60 (0.00; 0.00 to 0.06) |

## Decision points after each person's first

{'sessions': 60, 'with_any': 55, 'later': 310, 'later_readable': 283, 'in_resolved_sessions': 0, 'reasons': {'came_into_view:friend': 803, 'signalled:oncoming': 88, 'plan_ended': 48, 'came_into_view:oncoming': 37, 'other_turned:oncoming': 30, 'plan_failing': 14, 'other_slowed_down:oncoming': 13, 'other_moved_left:oncoming': 6, 'other_moved_right:oncoming': 5, 'other_sped_up:oncoming': 3, 'other_moved_right:friend': 1, 'other_turned:friend': 1}, 'signals': {'hold_up_hand': 127}, 'signals_seen_by': {'friend': 530, 'oncoming': 109}}

## Paired with the other group experiment (same cell and case)

| Layout | Sessions | Both resolved | This only | Other only | Neither | Sign test p |
| --- | --- | --- | --- | --- | --- | --- |
| density=per_way_25 | 32 | 0 | 0 | 0 | 32 | 1.0 |
| density=per_way_50 | 28 | 0 | 0 | 0 | 28 | 1.0 |
| all | 60 | 0 | 0 | 0 | 60 | 1.0 |

## Paired with the other crowd experiment (same cell and case), against plain ORCA (issue #119)

| Layout | Sessions | Both resolved | This only | Other only | Neither | Sign test p | Plans against the other's: better / same / worse (p) | By collisions alone (p) | Plain ORCA differs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| density=per_way_25 | 32 | 8 | 0 | 0 | 24 | 1.0 | 3 / 19 / 10 (0.092285) | 0 / 22 / 10 (0.001953) | 0 |
| density=per_way_50 | 28 | 0 | 1 | 5 | 22 | 0.21875 | 5 / 3 / 20 (0.004077) | 3 / 9 / 16 (0.004425) | 0 |
| all | 60 | 8 | 1 | 5 | 46 | 0.21875 | 8 / 22 / 30 (0.000472) | 3 / 31 / 26 (1.5e-05) | 0 |
