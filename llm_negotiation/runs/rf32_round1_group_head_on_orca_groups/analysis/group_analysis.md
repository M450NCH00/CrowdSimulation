# RF-32: group sessions per conflict pair (machine-written)

72 completed sessions, 64 of the design (exact-repeat copies left out).

## Resolved in plan_only, by layout

| Layout | Sessions | Resolved (95% CI) | Fisher p against round 1's pairs | plain ORCA | left_turn | cane | both | rf12_slow | rf12_plain | rf12_holds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2v1_aligned | 16 | 2 / 16 (0.12; 0.04 to 0.36) | 0.004005 | 0 | 16 | 0 | 8 | 0 | 0 | 0 |
| 2v1_apart_20cm | 16 | 2 / 16 (0.12; 0.04 to 0.36) | 0.004005 | 0 | 16 | 0 | 8 | 0 | 0 | 0 |
| 2v2_aligned | 16 | 0 / 16 (0.00; 0.00 to 0.19) | 3e-05 | 0 | 16 | 0 | 8 | 0 | 0 | 0 |
| 2v2_apart_20cm | 16 | 0 / 16 (0.00; 0.00 to 0.19) | 3e-05 | 0 | 16 | 0 | 8 | 0 | 0 | 0 |
| all | 64 | 4 / 64 (0.06; 0.02 to 0.15) | 0.0 | 0 | 64 | 0 | 32 | 0 | 0 | 0 |

Round 1's pairs: 35 / 64 resolved (0.43 to 0.66); sides of the resolved: {'right/right': 27, 'left/left': 8}.

## Conflict pairs

{'n': 192, 'resolved_plan_only': 21, 'sides_plan_only': {'-/-': 7, 'right/right': 7, 'left/left': 7}}

## Identity check per conflict pair

| Arm | Pairs | Reproduced | Same first | Same sides | Resolved | Matched |
| --- | --- | --- | --- | --- | --- | --- |
| plain_orca (resolved_pairs) | 21 | 5 | 8 | 12 | 2 | - |
| plain_orca (all_pairs) | 192 | 8 | 18 | 92 | 32 | - |
| left_turn (resolved_pairs) | 21 | 7 | 15 | 7 | 21 | 21 |
| left_turn (all_pairs) | 192 | 11 | 34 | 53 | 192 | 192 |
| cane (resolved_pairs) | 21 | 6 | 10 | 12 | 3 | 15 |
| cane (all_pairs) | 192 | 12 | 20 | 94 | 32 | 96 |
| both (resolved_pairs) | 21 | 6 | 12 | 9 | 9 | 21 |
| both (all_pairs) | 192 | 13 | 30 | 70 | 120 | 192 |
| rf12_slow (resolved_pairs) | 21 | 9 | 12 | 12 | 4 | 21 |
| rf12_slow (all_pairs) | 192 | 15 | 27 | 96 | 32 | 192 |
| rf12_plain (resolved_pairs) | 21 | 5 | 8 | 12 | 2 | 21 |
| rf12_plain (all_pairs) | 192 | 8 | 18 | 92 | 32 | 192 |
| rf12_holds (resolved_pairs) | 21 | 5 | 8 | 12 | 2 | 21 |
| rf12_holds (all_pairs) | 192 | 8 | 18 | 92 | 32 | 192 |

## How friends got past each oncoming person

{'2v1_aligned': {'not_reached': 13, 'between': 3}, '2v1_apart_20cm': {'not_reached': 8, 'between': 4, 'single_file': 4}, '2v2_aligned': {'not_reached': 58, 'between': 2, 'abreast': 1, 'single_file': 3}, '2v2_apart_20cm': {'not_reached': 62, 'between': 1, 'single_file': 1}, 'all': {'not_reached': 141, 'between': 10, 'single_file': 8, 'abreast': 1}}

Passed cleanly (the oncoming person resolved its pair with each friend), of each formation: {'between': [2, 10], 'single_file': [2, 8], 'abreast': [0, 1], 'not_reached': [0, 141]}

## First plans

- **alone**: {'people': 32, 'readable': 31, 'side': {'both': 9, 'none': 11, 'right': 11}, 'slowed': 16, 'stopped': 0, 'backed_up': 0, 'carry_on': 3, 'mean_turn_degrees': 7.1, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **with_friend**: {'people': 192, 'readable': 186, 'side': {'both': 78, 'none': 10, 'left': 37, 'right': 61}, 'slowed': 108, 'stopped': 0, 'backed_up': 0, 'carry_on': 1, 'mean_turn_degrees': 12.33, 'start_distance_m_mean': 4.0, 'with_start_distance': 1}
- **round1_pairs**: {'people': 128, 'readable': 123, 'side': {'right': 53, 'left': 17, 'both': 47, 'none': 6}, 'slowed': 90, 'stopped': 0, 'backed_up': 0, 'carry_on': 2, 'mean_turn_degrees': 12.83, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **facing_a_cane**: {'people': 80, 'readable': 76, 'side': {'both': 32, 'left': 21, 'right': 23}, 'slowed': 49, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 13.59, 'start_distance_m_mean': None, 'with_start_distance': 0}
- **holds_ground**: {'people': 32, 'readable': 32, 'side': {'none': 20, 'right': 8, 'both': 4}, 'slowed': 12, 'stopped': 0, 'backed_up': 0, 'carry_on': 4, 'mean_turn_degrees': 4.19, 'start_distance_m_mean': 4.0, 'with_start_distance': 1}
- **gives_way**: {'people': 192, 'readable': 185, 'side': {'both': 83, 'left': 37, 'right': 64, 'none': 1}, 'slowed': 112, 'stopped': 0, 'backed_up': 0, 'carry_on': 0, 'mean_turn_degrees': 12.86, 'start_distance_m_mean': None, 'with_start_distance': 0}

## Debriefs

- **groups**: {'debriefs': 245, 'kinds': {'common_sense': 154, 'habit': 78, 'none': 11, 'local_custom': 2}, 'terms': {'keep left': 3, 'keep right': 7, 'single file': 1, 'behind (a friend)': 45, 'between': 0, 'elderly / cane': 111}, 'sources': []}
- **round1_pairs**: {'debriefs': 123, 'kinds': {'local_custom': 12, 'common_sense': 70, 'habit': 38, 'none': 3}, 'terms': {'keep left': 12, 'keep right': 3, 'single file': 0, 'behind (a friend)': 18, 'between': 0, 'elderly / cane': 52}, 'sources': []}

Unreadable after retry: {'decision_points': 252, 'unreadable': 7}
