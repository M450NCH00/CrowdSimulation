# Hallucinated decisions (RF-45): tables

Written by `python -m analysis.hallucination`; codebook `hallucination_v2`. Shares are flagged decision points, with Wilson 95% intervals. The headline counts categories 1, 2, 5 and 7, of all decision points; self-contradiction counts 3 and 4, of readable ones. Each category's denominator is the decision points it can be judged on (3: an intent the RF-8 codebook can place; 4: a message stating the speaker's own side).

## rf39_round1_head_on_sidestep_reprompt

3987 decision points, 3875 readable.

| | All | independent | non_verbal | talk |
| --- | --- | --- | --- | --- |
| **Headline (1, 2, 5, 7)** | 189 / 3987 (4.7%, 4.1 to 5.4) | 36 / 544 (6.6%, 4.8 to 9.0) | 88 / 1705 (5.2%, 4.2 to 6.3) | 65 / 1738 (3.7%, 2.9 to 4.7) |
| Self-contradiction (3, 4) | 774 / 3875 (20.0%, 18.7 to 21.3) | 133 / 515 (25.8%, 22.2 to 29.8) | 271 / 1648 (16.4%, 14.7 to 18.3) | 370 / 1712 (21.6%, 19.7 to 23.6) |
| 1. misperceived the other | 37 / 3875 (1.0%, 0.7 to 1.3) | 1 / 515 (0.2%, 0.0 to 1.1) | 20 / 1648 (1.2%, 0.8 to 1.9) | 16 / 1712 (0.9%, 0.6 to 1.5) |
| 2. misremembered itself | 2 / 3875 (0.1%, 0.0 to 0.2) | 0 / 515 (0.0%, 0.0 to 0.7) | 1 / 1648 (0.1%, 0.0 to 0.3) | 1 / 1712 (0.1%, 0.0 to 0.3) |
| 3. says one thing, plans another | 763 / 3359 (22.7%, 21.3 to 24.2) | 133 / 454 (29.3%, 25.3 to 33.6) | 271 / 1397 (19.4%, 17.4 to 21.6) | 359 / 1508 (23.8%, 21.7 to 26.0) |
| 4. says a side it does not take | 13 / 59 (22.0%, 13.4 to 34.1) | – | – | 13 / 59 (22.0%, 13.4 to 34.1) |
| 5. not an available action (unreadable) | 112 / 3987 (2.8%, 2.3 to 3.4) | 29 / 544 (5.3%, 3.7 to 7.6) | 57 / 1705 (3.3%, 2.6 to 4.3) | 26 / 1738 (1.5%, 1.0 to 2.2) |
| 7. misstated the setting | 38 / 3875 (1.0%, 0.7 to 1.3) | 6 / 515 (1.2%, 0.5 to 2.5) | 10 / 1648 (0.6%, 0.3 to 1.1) | 22 / 1712 (1.3%, 0.9 to 1.9) |

By decision number (headline):

| Decision | Headline | 1 | 2 | 5 | 7 |
| --- | --- | --- | --- | --- | --- |
| 1 | 67 / 1632 (4.1%, 3.2 to 5.2) | 4 / 1583 (0.3%, 0.1 to 0.6) | 0 / 1583 (0.0%, 0.0 to 0.2) | 49 / 1632 (3.0%, 2.3 to 3.9) | 14 / 1583 (0.9%, 0.5 to 1.5) |
| 2 | 37 / 890 (4.2%, 3.0 to 5.7) | 8 / 871 (0.9%, 0.5 to 1.8) | 1 / 871 (0.1%, 0.0 to 0.6) | 19 / 890 (2.1%, 1.4 to 3.3) | 9 / 871 (1.0%, 0.5 to 2.0) |
| 3 | 36 / 651 (5.5%, 4.0 to 7.6) | 10 / 631 (1.6%, 0.9 to 2.9) | 0 / 631 (0.0%, 0.0 to 0.6) | 20 / 651 (3.1%, 2.0 to 4.7) | 6 / 631 (1.0%, 0.4 to 2.1) |
| 4 | 29 / 426 (6.8%, 4.8 to 9.6) | 9 / 412 (2.2%, 1.2 to 4.1) | 0 / 412 (0.0%, 0.0 to 0.9) | 14 / 426 (3.3%, 2.0 to 5.4) | 6 / 412 (1.5%, 0.7 to 3.1) |
| 5 | 16 / 287 (5.6%, 3.5 to 8.9) | 5 / 278 (1.8%, 0.8 to 4.1) | 0 / 278 (0.0%, 0.0 to 1.4) | 9 / 287 (3.1%, 1.7 to 5.9) | 2 / 278 (0.7%, 0.2 to 2.6) |
| 6 | 4 / 101 (4.0%, 1.6 to 9.7) | 1 / 100 (1.0%, 0.2 to 5.4) | 1 / 100 (1.0%, 0.2 to 5.4) | 1 / 101 (1.0%, 0.2 to 5.4) | 1 / 100 (1.0%, 0.2 to 5.4) |

Design sessions with a headline flag: resolved 45, not 103; without: resolved 347, not 273 (Fisher's exact p = 2.8e-08; an association, not a cause).

Flags by rule: `1:moved_into_line` 4, `1:moved_side` 11, `1:position_side` 3, `1:signal_wave` 5, `1:speech` 6, `1:trait_elderly` 8, `1:trait_suitcase` 1, `2:own_position` 1, `2:own_signal` 1, `3:intent_against_plan` 763, `4:coming_through_on_your_side` 13, `5:unreadable` 112, `7:no_room` 23, `7:wall_close` 16.
Tags: none.

## rf40_round1_head_on_turn_taking

5256 decision points, 5135 readable.

| | All | non_verbal | silent | talk |
| --- | --- | --- | --- | --- |
| **Headline (1, 2, 5, 7)** | 282 / 5256 (5.4%, 4.8 to 6.0) | 94 / 1776 (5.3%, 4.3 to 6.4) | 87 / 1657 (5.3%, 4.3 to 6.4) | 101 / 1823 (5.5%, 4.6 to 6.7) |
| Self-contradiction (3, 4) | 1251 / 5135 (24.4%, 23.2 to 25.6) | 391 / 1754 (22.3%, 20.4 to 24.3) | 462 / 1605 (28.8%, 26.6 to 31.0) | 398 / 1776 (22.4%, 20.5 to 24.4) |
| 1. misperceived the other | 106 / 5135 (2.1%, 1.7 to 2.5) | 50 / 1754 (2.9%, 2.2 to 3.7) | 20 / 1605 (1.2%, 0.8 to 1.9) | 36 / 1776 (2.0%, 1.5 to 2.8) |
| 2. misremembered itself | 5 / 5135 (0.1%, 0.0 to 0.2) | 3 / 1754 (0.2%, 0.1 to 0.5) | 0 / 1605 (0.0%, 0.0 to 0.2) | 2 / 1776 (0.1%, 0.0 to 0.4) |
| 3. says one thing, plans another | 1234 / 4577 (27.0%, 25.7 to 28.3) | 391 / 1555 (25.1%, 23.1 to 27.4) | 462 / 1421 (32.5%, 30.1 to 35.0) | 381 / 1601 (23.8%, 21.8 to 25.9) |
| 4. says a side it does not take | 18 / 73 (24.7%, 16.2 to 35.6) | – | – | 18 / 73 (24.7%, 16.2 to 35.6) |
| 5. not an available action (unreadable) | 121 / 5256 (2.3%, 1.9 to 2.7) | 22 / 1776 (1.2%, 0.8 to 1.9) | 52 / 1657 (3.1%, 2.4 to 4.1) | 47 / 1823 (2.6%, 1.9 to 3.4) |
| 7. misstated the setting | 50 / 5135 (1.0%, 0.7 to 1.3) | 19 / 1754 (1.1%, 0.7 to 1.7) | 15 / 1605 (0.9%, 0.6 to 1.5) | 16 / 1776 (0.9%, 0.6 to 1.5) |

By decision number (headline):

| Decision | Headline | 1 | 2 | 5 | 7 |
| --- | --- | --- | --- | --- | --- |
| 1 | 51 / 1632 (3.1%, 2.4 to 4.1) | 5 / 1598 (0.3%, 0.1 to 0.7) | 0 / 1598 (0.0%, 0.0 to 0.2) | 34 / 1632 (2.1%, 1.5 to 2.9) | 12 / 1598 (0.8%, 0.4 to 1.3) |
| 2 | 78 / 1432 (5.4%, 4.4 to 6.7) | 32 / 1398 (2.3%, 1.6 to 3.2) | 2 / 1398 (0.1%, 0.0 to 0.5) | 34 / 1432 (2.4%, 1.7 to 3.3) | 10 / 1398 (0.7%, 0.4 to 1.3) |
| 3 | 68 / 1039 (6.5%, 5.2 to 8.2) | 32 / 1013 (3.2%, 2.2 to 4.4) | 1 / 1013 (0.1%, 0.0 to 0.6) | 26 / 1039 (2.5%, 1.7 to 3.6) | 9 / 1013 (0.9%, 0.5 to 1.7) |
| 4 | 42 / 672 (6.2%, 4.7 to 8.3) | 25 / 660 (3.8%, 2.6 to 5.5) | 0 / 660 (0.0%, 0.0 to 0.6) | 12 / 672 (1.8%, 1.0 to 3.1) | 5 / 660 (0.8%, 0.3 to 1.8) |
| 5 | 34 / 372 (9.1%, 6.6 to 12.5) | 11 / 362 (3.0%, 1.7 to 5.4) | 2 / 362 (0.6%, 0.2 to 2.0) | 10 / 372 (2.7%, 1.5 to 4.9) | 11 / 362 (3.0%, 1.7 to 5.4) |
| 6 | 9 / 109 (8.3%, 4.4 to 15.0) | 1 / 104 (1.0%, 0.2 to 5.2) | 0 / 104 (0.0%, 0.0 to 3.6) | 5 / 109 (4.6%, 2.0 to 10.3) | 3 / 104 (2.9%, 1.0 to 8.1) |

Design sessions with a headline flag: resolved 88, not 124; without: resolved 369, not 187 (Fisher's exact p = 5.26e-10; an association, not a cause).

Flags by rule: `1:misread_heard_side` 14, `1:moved_into_line` 12, `1:moved_side` 41, `1:position_side` 5, `1:signal_wave` 10, `1:speech` 20, `1:trait_elderly` 7, `1:trait_suitcase` 2, `2:own_signal` 3, `2:own_speech` 2, `3:intent_against_plan` 1234, `4:coming_through_on_your_side` 16, `4:keeping_to_my_side` 2, `5:unreadable` 121, `7:no_room` 33, `7:wall_close` 17.
Tags: {'misread_heard_side': 14}.

