# Rule translation: rf31_round1_head_on_retry

RF-31, round 1 (head-on), the retry: RF-11's kept rule x_head_on_6455ca5589 translated once more into rule format 4 with translate_v2, its reply read with the one-brace repair, then validated, written, run on its Step 1 sessions and screened in the two-way flow, as rf31_round1_head_on.

Status: completed; client deepseek; cost USD 0.000410 (worst case USD 0.010878, cap USD 0.05).

From `runs/rf11_round1_head_on` (candidate rules): 1 rule(s), 1 translated; categories {'valid': 1}; written 1; runnable in ORCA 1; extracted as needing communication 0 (written but not runnable: 0).

A `format_limit` or `not_expressible` translation is a finding about rule format 4, not about the model.

| Extracted rule | Category | Lost (translator) | Factors format 4 cannot read | Action words with no directive | Identity check | Crowd |
| --- | --- | --- | --- | --- | --- | --- |
| `x_head_on_6455ca5589`: A gives_way person slows on the first plan when the other was described as elderly, using a cane, pulling a large suitcase, or looking at a phone. | valid | condition (approximated): other_mobility_aid is cane or other_load is large_suitcase or other_distraction is phone or other_age is 70; condition (approximated): own_assertiveness is gives_way; speed (approximated): speed drops from 1.3 to 0.8-1.1 m/s; start (approximated): from about 9.8 m or from 2.0-3.0 m; duration (approximated): held until other_passes; condition (left_out): holds_ground people often do not slow on the first plan even for a loaded or elderly other; condition (left_out): urgent people keep 1.3 m/s or only slow at 2.0 m; other (left_out): coin_flip rows are not certain | none | none | 0.34 against plain ORCA 0.36 (n 76; the rule matched 32, reproducing 0.22 of those) | failed (seed 30902: the flow gridlocked (timeout, 93 of 100 arrived) where the baseline did not) |

Across the 1 translated rule(s), rules with each: factor status {'readable': 1}; action words {}; kinds the translator said it lost {'condition': 1, 'duration': 1, 'other': 1, 'speed': 1, 'start': 1}.

The identity check runs each runnable rule alone in ORCA on the Step 1 sessions it was extracted from, and gives the share whose who-passed-first and both passing sides match what the agents' plans did in `plan_only`, beside plain ORCA on the same seeds. References are copied from the extraction, unchecked (RF-14).
