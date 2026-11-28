# rf35_crowd_encounters: group sessions per conflict pair (machine-written)

72 completed sessions, 64 of the design (exact-repeat copies left out).

## Resolved in plan_only, by layout

| Layout | Sessions | Resolved (95% CI) | Fisher p against round 1's pairs | plain ORCA |  |
| --- | --- | --- | --- | --- |  |
| density=per_way_25 | 32 | 0 / 32 (0.00; 0.00 to 0.11) | 0.0 | 0 |  |
| density=per_way_50 | 32 | 0 / 32 (0.00; 0.00 to 0.11) | 0.0 | 0 |  |
| all | 64 | 0 / 64 (0.00; 0.00 to 0.06) | 0.0 | 0 |  |

Round 1's pairs: 35 / 64 resolved (0.43 to 0.66); sides of the resolved: {'right/right': 27, 'left/left': 8}.

## Conflict pairs

{'n': 264, 'resolved_plan_only': 12, 'sides_plan_only': {'right/right': 11, '-/-': 1}}

## Identity check per conflict pair

| Arm | Pairs | Reproduced | Same first | Same sides | Resolved | Matched |
| --- | --- | --- | --- | --- | --- | --- |
| plain_orca (resolved_pairs) | 12 | 5 | 5 | 12 | 0 | - |
| plain_orca (all_pairs) | 264 | 193 | 194 | 263 | 0 | - |

## How friends got past each oncoming person

{'density=per_way_25': {'single_file': 64, 'abreast': 8, 'not_reached': 24}, 'density=per_way_50': {'not_reached': 32, 'single_file': 96}, 'all': {'single_file': 160, 'abreast': 8, 'not_reached': 56}}

Passed cleanly (the oncoming person resolved its pair with each friend), of each formation: {'between': [0, 0], 'single_file': [11, 160], 'abreast': [0, 8], 'not_reached': [2, 56]}

## First plans

- **alone**: {'people': 8, 'readable': 8, 'side': {'right': 1, 'both': 4, 'none': 3}, 'slowed': 4, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 11.88, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **with_friend**: {'people': 208, 'readable': 197, 'side': {'left': 38, 'right': 69, 'none': 26, 'both': 64}, 'slowed': 92, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 14.92, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **round1_pairs**: {'people': 128, 'readable': 123, 'side': {'right': 53, 'left': 17, 'both': 47, 'none': 6}, 'slowed': 90, 'stopped': 0, 'backed_up': 0, 'carry_on': 2, 'mean_turn_degrees': 12.83, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **facing_a_cane**: {'people': 77, 'readable': 75, 'side': {'left': 17, 'none': 8, 'both': 24, 'right': 26}, 'slowed': 32, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 16.73, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **holds_ground**: {'people': 82, 'readable': 76, 'side': {'none': 29, 'left': 7, 'right': 13, 'both': 27}, 'slowed': 10, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 8.16, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **gives_way**: {'people': 134, 'readable': 129, 'side': {'left': 31, 'right': 57, 'both': 41}, 'slowed': 86, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 18.72, 'start_distance_m_mean': None, 'with_start_distance': 0}

## Debriefs

- **groups**: {'debriefs': 228, 'kinds': {'habit': 88, 'common_sense': 124, 'none': 16}, 'terms': {'keep left': 8, 'keep right': 26, 'single file': 0, 'behind (a friend)': 40, 'between': 2, 'elderly / cane': 81}, 'sources': []}
- **round1_pairs**: {'debriefs': 123, 'kinds': {'local_custom': 12, 'common_sense': 70, 'habit': 38, 'none': 3}, 'terms': {'keep left': 12, 'keep right': 3, 'single file': 0, 'behind (a friend)': 18, 'between': 0, 'elderly / cane': 52}, 'sources': []}

Unreadable after retry: {'decision_points': 240, 'unreadable': 12}

## Against plain ORCA on the same seed (issue #117)

| Layout | Sessions | Resolved: no more collisions, none deeper, none stuck (95% CI) | Better | Same | Worse | Sign test p | Collisions, plans / plain ORCA | Stuck, plans / plain ORCA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| density=per_way_25 | 32 | 8 / 32 (0.25; 0.13 to 0.42) | 0 | 8 | 24 | 0.0 | 163 / 152 | 0 / 0 |
| density=per_way_50 | 32 | 6 / 32 (0.19; 0.09 to 0.35) | 6 | 0 | 26 | 0.000535 | 226 / 184 | 0 / 0 |
| all | 64 | 14 / 64 (0.22; 0.14 to 0.33) | 6 | 8 | 50 | 0.0 | 389 / 336 | 0 / 0 |

## Resolved in plan_only, by the number of people in the encounter

| People | Sessions | Resolved (95% CI) |
| --- | --- | --- |
| 4 | 64 | 0 / 64 (0.00; 0.00 to 0.06) |

## Decision points after each person's first

{'sessions': 64, 'with_any': 0, 'later': 0, 'later_readable': 0, 'in_resolved_sessions': 0, 'reasons': {}, 'signals': {}, 'signals_seen_by': {}}
