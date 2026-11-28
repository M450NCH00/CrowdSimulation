# Hallucinated decisions (RF-45): tables

Written by `python -m analysis.hallucination`; codebook `hallucination_v2`. Shares are flagged decision points, with Wilson 95% intervals. The headline counts categories 1, 2, 5 and 7, of all decision points; self-contradiction counts 3 and 4, of readable ones. Each category's denominator is the decision points it can be judged on (3: an intent the RF-8 codebook can place; 4: a message stating the speaker's own side).

## rf49_round1_head_on_menu

2955 decision points, 2952 readable.

| | All | silent | talk |
| --- | --- | --- | --- |
| **Headline (1, 2, 5, 7)** | 57 / 2955 (1.9%, 1.5 to 2.5) | 27 / 1390 (1.9%, 1.3 to 2.8) | 30 / 1565 (1.9%, 1.3 to 2.7) |
| Self-contradiction (3, 4) | 1101 / 2952 (37.3%, 35.6 to 39.1) | 455 / 1387 (32.8%, 30.4 to 35.3) | 646 / 1565 (41.3%, 38.9 to 43.7) |
| 1. misperceived the other | 35 / 2952 (1.2%, 0.9 to 1.6) | 15 / 1387 (1.1%, 0.7 to 1.8) | 20 / 1565 (1.3%, 0.8 to 2.0) |
| 2. misremembered itself | 5 / 2952 (0.2%, 0.1 to 0.4) | 1 / 1387 (0.1%, 0.0 to 0.4) | 4 / 1565 (0.3%, 0.1 to 0.7) |
| 3. says one thing, plans another | 1100 / 2174 (50.6%, 48.5 to 52.7) | 455 / 976 (46.6%, 43.5 to 49.8) | 645 / 1198 (53.8%, 51.0 to 56.6) |
| 4. says a side it does not take | 1 / 4 (25.0%, 4.6 to 69.9) | – | 1 / 4 (25.0%, 4.6 to 69.9) |
| 5. not an available action (unreadable) | 3 / 2955 (0.1%, 0.0 to 0.3) | 3 / 1390 (0.2%, 0.1 to 0.6) | 0 / 1565 (0.0%, 0.0 to 0.2) |
| 7. misstated the setting | 14 / 2952 (0.5%, 0.3 to 0.8) | 8 / 1387 (0.6%, 0.3 to 1.1) | 6 / 1565 (0.4%, 0.2 to 0.8) |

By decision number (headline):

| Decision | Headline | 1 | 2 | 5 | 7 |
| --- | --- | --- | --- | --- | --- |
| 1 | 12 / 1088 (1.1%, 0.6 to 1.9) | 2 / 1085 (0.2%, 0.1 to 0.7) | 3 / 1085 (0.3%, 0.1 to 0.8) | 3 / 1088 (0.3%, 0.1 to 0.8) | 4 / 1085 (0.4%, 0.1 to 0.9) |
| 2 | 10 / 1038 (1.0%, 0.5 to 1.8) | 8 / 1038 (0.8%, 0.4 to 1.5) | 0 / 1038 (0.0%, 0.0 to 0.4) | 0 / 1038 (0.0%, 0.0 to 0.4) | 2 / 1038 (0.2%, 0.1 to 0.7) |
| 3 | 18 / 511 (3.5%, 2.2 to 5.5) | 15 / 511 (2.9%, 1.8 to 4.8) | 1 / 511 (0.2%, 0.0 to 1.1) | 0 / 511 (0.0%, 0.0 to 0.7) | 2 / 511 (0.4%, 0.1 to 1.4) |
| 4 | 10 / 276 (3.6%, 2.0 to 6.5) | 6 / 276 (2.2%, 1.0 to 4.7) | 0 / 276 (0.0%, 0.0 to 1.4) | 0 / 276 (0.0%, 0.0 to 1.4) | 4 / 276 (1.4%, 0.6 to 3.7) |
| 5 | 7 / 42 (16.7%, 8.3 to 30.6) | 4 / 42 (9.5%, 3.8 to 22.1) | 1 / 42 (2.4%, 0.4 to 12.3) | 0 / 42 (0.0%, 0.0 to 8.4) | 2 / 42 (4.8%, 1.3 to 15.8) |

Design sessions with a headline flag: resolved 22, not 31; without: resolved 202, not 257 (Fisher's exact p = 0.771; an association, not a cause).

Flags by rule: `1:misread_heard_side` 1, `1:moved_into_line` 2, `1:moved_side` 16, `1:position_side` 1, `1:signal_wave` 3, `1:speech` 5, `1:trait_elderly` 7, `2:own_position` 4, `2:own_signal` 1, `3:intent_against_plan` 1100, `4:coming_through_on_your_side` 1, `5:unreadable` 3, `7:no_room` 8, `7:wall_close` 6.
Tags: {'misread_heard_side': 1}.

## rf49_round1_head_on_menu_abs

1570 decision points, 1570 readable.

| | All | silent | talk |
| --- | --- | --- | --- |
| **Headline (1, 2, 5, 7)** | 12 / 1570 (0.8%, 0.4 to 1.3) | 4 / 746 (0.5%, 0.2 to 1.4) | 8 / 824 (1.0%, 0.5 to 1.9) |
| Self-contradiction (3, 4) | 445 / 1570 (28.3%, 26.2 to 30.6) | 233 / 746 (31.2%, 28.0 to 34.6) | 212 / 824 (25.7%, 22.9 to 28.8) |
| 1. misperceived the other | 5 / 1570 (0.3%, 0.1 to 0.7) | 1 / 746 (0.1%, 0.0 to 0.8) | 4 / 824 (0.5%, 0.2 to 1.2) |
| 2. misremembered itself | 0 / 1570 (0.0%, 0.0 to 0.2) | 0 / 746 (0.0%, 0.0 to 0.5) | 0 / 824 (0.0%, 0.0 to 0.5) |
| 3. says one thing, plans another | 442 / 983 (45.0%, 41.9 to 48.1) | 233 / 518 (45.0%, 40.7 to 49.3) | 209 / 465 (44.9%, 40.5 to 49.5) |
| 4. says a side it does not take | 4 / 6 (66.7%, 30.0 to 90.3) | – | 4 / 6 (66.7%, 30.0 to 90.3) |
| 5. not an available action (unreadable) | 0 / 1570 (0.0%, 0.0 to 0.2) | 0 / 746 (0.0%, 0.0 to 0.5) | 0 / 824 (0.0%, 0.0 to 0.5) |
| 7. misstated the setting | 7 / 1570 (0.4%, 0.2 to 0.9) | 3 / 746 (0.4%, 0.1 to 1.2) | 4 / 824 (0.5%, 0.2 to 1.2) |

By decision number (headline):

| Decision | Headline | 1 | 2 | 5 | 7 |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 / 576 (0.2%, 0.0 to 1.0) | 1 / 576 (0.2%, 0.0 to 1.0) | 0 / 576 (0.0%, 0.0 to 0.7) | 0 / 576 (0.0%, 0.0 to 0.7) | 0 / 576 (0.0%, 0.0 to 0.7) |
| 2 | 5 / 555 (0.9%, 0.4 to 2.1) | 2 / 555 (0.4%, 0.1 to 1.3) | 0 / 555 (0.0%, 0.0 to 0.7) | 0 / 555 (0.0%, 0.0 to 0.7) | 3 / 555 (0.5%, 0.2 to 1.6) |
| 3 | 3 / 273 (1.1%, 0.4 to 3.2) | 1 / 273 (0.4%, 0.1 to 2.0) | 0 / 273 (0.0%, 0.0 to 1.4) | 0 / 273 (0.0%, 0.0 to 1.4) | 2 / 273 (0.7%, 0.2 to 2.6) |
| 4 | 1 / 146 (0.7%, 0.1 to 3.8) | 0 / 146 (0.0%, 0.0 to 2.6) | 0 / 146 (0.0%, 0.0 to 2.6) | 0 / 146 (0.0%, 0.0 to 2.6) | 1 / 146 (0.7%, 0.1 to 3.8) |
| 5 | 2 / 20 (10.0%, 2.8 to 30.1) | 1 / 20 (5.0%, 0.9 to 23.6) | 0 / 20 (0.0%, 0.0 to 16.1) | 0 / 20 (0.0%, 0.0 to 16.1) | 1 / 20 (5.0%, 0.9 to 23.6) |

Design sessions with a headline flag: resolved 2, not 9; without: resolved 73, not 172 (Fisher's exact p = 0.517; an association, not a cause).

Flags by rule: `1:signal_wave` 1, `1:slowed` 1, `1:speech` 1, `1:trait_elderly` 2, `3:intent_against_plan` 442, `4:coming_through_on_your_side` 4, `7:no_room` 7.
Tags: none.

## rf49_round1_head_on_menu_abs_swap

1573 decision points, 1573 readable.

| | All | silent | talk |
| --- | --- | --- | --- |
| **Headline (1, 2, 5, 7)** | 18 / 1573 (1.1%, 0.7 to 1.8) | 8 / 719 (1.1%, 0.6 to 2.2) | 10 / 854 (1.2%, 0.6 to 2.1) |
| Self-contradiction (3, 4) | 448 / 1573 (28.5%, 26.3 to 30.8) | 201 / 719 (28.0%, 24.8 to 31.3) | 247 / 854 (28.9%, 26.0 to 32.1) |
| 1. misperceived the other | 5 / 1573 (0.3%, 0.1 to 0.7) | 0 / 719 (0.0%, 0.0 to 0.5) | 5 / 854 (0.6%, 0.3 to 1.4) |
| 2. misremembered itself | 0 / 1573 (0.0%, 0.0 to 0.2) | 0 / 719 (0.0%, 0.0 to 0.5) | 0 / 854 (0.0%, 0.0 to 0.4) |
| 3. says one thing, plans another | 444 / 970 (45.8%, 42.7 to 48.9) | 201 / 478 (42.1%, 37.7 to 46.5) | 243 / 492 (49.4%, 45.0 to 53.8) |
| 4. says a side it does not take | 4 / 4 (100.0%, 51.0 to 100.0) | – | 4 / 4 (100.0%, 51.0 to 100.0) |
| 5. not an available action (unreadable) | 0 / 1573 (0.0%, 0.0 to 0.2) | 0 / 719 (0.0%, 0.0 to 0.5) | 0 / 854 (0.0%, 0.0 to 0.4) |
| 7. misstated the setting | 13 / 1573 (0.8%, 0.5 to 1.4) | 8 / 719 (1.1%, 0.6 to 2.2) | 5 / 854 (0.6%, 0.3 to 1.4) |

By decision number (headline):

| Decision | Headline | 1 | 2 | 5 | 7 |
| --- | --- | --- | --- | --- | --- |
| 1 | 3 / 576 (0.5%, 0.2 to 1.5) | 2 / 576 (0.3%, 0.1 to 1.3) | 0 / 576 (0.0%, 0.0 to 0.7) | 0 / 576 (0.0%, 0.0 to 0.7) | 1 / 576 (0.2%, 0.0 to 1.0) |
| 2 | 1 / 556 (0.2%, 0.0 to 1.0) | 0 / 556 (0.0%, 0.0 to 0.7) | 0 / 556 (0.0%, 0.0 to 0.7) | 0 / 556 (0.0%, 0.0 to 0.7) | 1 / 556 (0.2%, 0.0 to 1.0) |
| 3 | 8 / 255 (3.1%, 1.6 to 6.1) | 2 / 255 (0.8%, 0.2 to 2.8) | 0 / 255 (0.0%, 0.0 to 1.5) | 0 / 255 (0.0%, 0.0 to 1.5) | 6 / 255 (2.4%, 1.1 to 5.0) |
| 4 | 4 / 162 (2.5%, 1.0 to 6.2) | 0 / 162 (0.0%, 0.0 to 2.3) | 0 / 162 (0.0%, 0.0 to 2.3) | 0 / 162 (0.0%, 0.0 to 2.3) | 4 / 162 (2.5%, 1.0 to 6.2) |
| 5 | 2 / 24 (8.3%, 2.3 to 25.8) | 1 / 24 (4.2%, 0.7 to 20.2) | 0 / 24 (0.0%, 0.0 to 13.8) | 0 / 24 (0.0%, 0.0 to 13.8) | 1 / 24 (4.2%, 0.7 to 20.2) |

Design sessions with a headline flag: resolved 1, not 15; without: resolved 69, not 171 (Fisher's exact p = 0.0777; an association, not a cause).

Flags by rule: `1:signal_wave` 2, `1:speech` 1, `1:trait_elderly` 1, `1:trait_phone` 1, `3:intent_against_plan` 444, `4:coming_through_on_your_side` 4, `7:no_room` 13.
Tags: none.

