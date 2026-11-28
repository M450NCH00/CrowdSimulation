# Pilot measures: rf_pilot_v2

72 session record(s) (completed 72). Estimated cost USD 0.061703 against a worst-case preview of USD 4.8466944; cache-hit share of input tokens 0.7049; sends by price tier {'off_peak': 492}. Reply cap 400 tokens.

## Tokens per send

| Kind | Sends | Prompt mean / median / max | Reply mean / median / max | Cache hit share | Cut off at the cap | Largest share of the bound |
| --- | --- | --- | --- | --- | --- | --- |
| decision | 351 | 991.43 / 966 / 1361 | 138.05 / 142 / 214 | 0.718 | 0 | 0.5094 |
| debrief | 141 | 1551.13 / 1587 / 1889 | 75.06 / 75 / 113 | 0.6842 | 0 | 0.4421 |

## Per condition

| Condition | Sessions | Sends mean / median / max (bound on calls, each up to 6 sends) | Decision points per agent | Cost USD (preview) | Per session mean / max | Largest share of a session's preview |
| --- | --- | --- | --- | --- | --- | --- |
| independent | 24 | 4.0 / 4.0 / 4 (4) | 1: 48 | 0.01097 (0.721267) | 0.000457 / 0.000567 | 0.0189 |
| non_verbal | 24 | 8.67 / 9.0 / 11 (8) | 1: 4, 2: 5, 3: 39 | 0.025054 (1.820189) | 0.001044 / 0.001372 | 0.0181 |
| talk | 24 | 7.83 / 8.0 / 9 (8) | 1: 4, 3: 44 | 0.025679 (2.305238) | 0.00107 / 0.001356 | 0.0141 |

## Trigger reasons, signals and messages

- **independent**: triggers {'trigger': 48, 'perceives': 48}; signals none; messages 0
- **non_verbal**: triggers {'other_turned': 72, 'trigger': 48, 'perceives': 48, 'other_moved_left': 37, 'plan_failing': 23, 'other_moved_right': 15, 'other_slowed_down': 4, 'plan_ended': 3, 'came_into_view': 2, 'other_sped_up': 1, 'signalled': 1}; signals {'eye_contact': 2, 'nod': 1}; messages 0
- **talk**: triggers {'other_turned': 84, 'trigger': 48, 'perceives': 48, 'other_moved_right': 36, 'other_moved_left': 34, 'plan_failing': 13, 'other_slowed_down': 8, 'signalled': 1}; signals {'eye_contact': 2, 'hold_up_hand': 1}; messages 1

## Unreadable sends, by reason

- decision:unknown_until: 58
- decision:not_json: 5

## Passing, per mode and condition

| Mode / condition | Sessions | Resolved | Collision | Near miss | Who passed first | Passing sides (a/b) |
| --- | --- | --- | --- | --- | --- | --- |
| plan_only/independent | 24 | 8 | 12 | 16 | {'none': 12, 'together': 9, '1': 2, '0': 1} | {'right/right': 18, 'left/left': 6} |
| plan_only/non_verbal | 24 | 5 | 16 | 19 | {'none': 16, '0': 3, 'together': 3, '1': 2} | {'right/right': 21, 'left/left': 3} |
| plan_only/talk | 24 | 4 | 19 | 20 | {'none': 19, 'together': 3, '0': 1, '1': 1} | {'right/right': 17, 'left/left': 7} |
| plan_orca/independent | 24 | 8 | 0 | 16 | {'together': 20, '1': 2, '0': 2} | {'right/right': 22, 'left/left': 2} |
| plan_orca/non_verbal | 24 | 8 | 0 | 16 | {'together': 15, '0': 5, '1': 4} | {'right/right': 23, 'left/left': 1} |
| plan_orca/talk | 24 | 5 | 0 | 19 | {'together': 19, '0': 3, '1': 2} | {'right/right': 19, 'left/left': 5} |
| plain_orca/independent | 24 | 0 | 0 | 24 | {'together': 24} | {'right/right': 12, 'left/left': 12} |
| plain_orca/non_verbal | 24 | 0 | 0 | 24 | {'together': 24} | {'right/right': 12, 'left/left': 12} |
| plain_orca/talk | 24 | 0 | 0 | 24 | {'together': 24} | {'left/left': 12, 'right/right': 12} |

Resolved by the LLM (resolved in `plan_only` and not handed to ORCA): {'independent': 8, 'non_verbal': 5, 'talk': 4}
