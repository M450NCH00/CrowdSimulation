# Pilot measures: rf_pilot

12 session record(s) (completed 12). Estimated cost USD 0.013398 against a worst-case preview of USD 4.7708352; cache-hit share of input tokens 0.664; sends by price tier {'off_peak': 105}. Reply cap 400 tokens.

## Tokens per send

| Kind | Sends | Prompt mean / median / max | Reply mean / median / max | Cache hit share | Cut off at the cap | Largest share of the bound |
| --- | --- | --- | --- | --- | --- | --- |
| decision | 81 | 976.49 / 941 / 1268 | 131.57 / 133 / 190 | 0.6619 | 0 | 0.5353 |
| debrief | 24 | 1426.92 / 1415.5 / 1683 | 74.04 / 72.0 / 94 | 0.669 | 0 | 0.4107 |

## Per condition

| Condition | Sessions | Sends mean / median / max (bound on calls, each up to 6 sends) | Decision points per agent | Cost USD (preview) | Per session mean / max | Largest share of a session's preview |
| --- | --- | --- | --- | --- | --- | --- |
| independent | 3 | 4.33 / 4 / 5 (4) | 1: 6 | 0.001577 (0.088279) | 0.000526 / 0.000635 | 0.0216 |
| non_verbal | 6 | 9.67 / 10.0 / 11 (8) | 3: 12 | 0.007437 (0.447444) | 0.001239 / 0.001422 | 0.0191 |
| talk | 3 | 11.33 / 12 / 12 (8) | 3: 6 | 0.004384 (0.284353) | 0.001461 / 0.001509 | 0.0159 |

## Trigger reasons, signals and messages

- **independent**: triggers {'trigger': 6, 'perceives': 6}; signals none; messages 0
- **non_verbal**: triggers {'other_turned': 23, 'trigger': 12, 'perceives': 12, 'other_moved_left': 10, 'other_moved_right': 8, 'other_slowed_down': 1, 'plan_failing': 1}; signals {'hold_up_hand': 1}; messages 0
- **talk**: triggers {'came_into_view': 7, 'trigger': 6, 'perceives': 6, 'other_turned': 4, 'plan_failing': 3, 'other_moved_right': 2, 'other_moved_left': 1}; signals none; messages 0

## Unreadable sends, by reason

- decision:start_on_later_step: 34
- decision:unknown_until: 1

## Passing, per mode and condition

| Mode / condition | Sessions | Resolved | Collision | Near miss | Who passed first | Passing sides (a/b) |
| --- | --- | --- | --- | --- | --- | --- |
| plan_only/independent | 3 | 0 | 3 | 3 | {'none': 3} | {'right/right': 2, 'left/left': 1} |
| plan_only/non_verbal | 6 | 0 | 6 | 6 | {'none': 6} | {'right/right': 4, 'left/left': 2} |
| plan_only/talk | 3 | 0 | 2 | 3 | {'none': 2, 'together': 1} | {'right/right': 3} |
| plan_orca/independent | 3 | 0 | 0 | 3 | {'together': 3} | {'right/right': 2, 'left/left': 1} |
| plan_orca/non_verbal | 6 | 0 | 0 | 6 | {'together': 6} | {'right/right': 5, 'left/left': 1} |
| plan_orca/talk | 3 | 0 | 0 | 3 | {'together': 3} | {'right/right': 3} |
| plain_orca/independent | 3 | 0 | 0 | 3 | {'together': 3} | {'left/left': 2, 'right/right': 1} |
| plain_orca/non_verbal | 6 | 0 | 0 | 6 | {'together': 6} | {'right/right': 3, 'left/left': 3} |
| plain_orca/talk | 3 | 0 | 0 | 3 | {'together': 3} | {'right/right': 3} |

Resolved by the LLM (resolved in `plan_only` and not handed to ORCA): {'independent': 0, 'non_verbal': 0, 'talk': 0}
