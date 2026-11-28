# Rule extraction: rf11_round1_head_on

RF-11, round 1 (head-on): the rules behind how LLM agents resolved head-on meetings in a corridor, extracted three times from RF-30's pooled design sessions, each with references, debrief support and a held-out fidelity score.

Status: completed; client deepseek; cost USD 0.022513 (worst case USD 0.107499, cap USD 0.05).

## head_on

Gate: 102 of 192 design sessions resolved in `plan_only`, 0.53 (95% CI 0.46 to 0.60); threshold 0.5: **passes**.

Main table 76 sessions (152 rows); held out 26 sessions (52 rows); failed sessions shown 90. Coin-flip cells: 23 of 24 repeated.

| Run | Outcome | Rules | Categories | Cost (USD) |
| --- | --- | --- | --- | --- |
| 1 | completed | 8 | {'valid': 5, 'schema_error': 1, 'needs_communication': 2} | 0.009193 |
| 2 | completed | 8 | {'valid': 6, 'needs_communication': 2} | 0.006460 |
| 3 | completed | 9 | {'valid': 4, 'schema_error': 3, 'needs_communication': 2} | 0.006860 |

Across the runs: {'valid': 15, 'schema_error': 4, 'needs_communication': 6} (a `protected_attribute` rule is counted, never stored).

| Rule | Status | Found in | Target | Held-out accuracy | References |
| --- | --- | --- | --- | --- | --- |
| A gives_way person turns to their own right in their first plan as a small step aside, mostly slowing at the same time. | unstable | 1/3 | `first_side` | 18/52 (0.35) against 0.46 for always `right` | no known source |
| A holds_ground person keeps their line at full speed on the first decision and only steps aside or slows at close range. | candidate | 2/3 | `first_slowed` | 43/52 (0.83) against 0.75 for always `yes` | no known source |
| A gives_way person slows on the first plan when the other was described as elderly, using a cane, pulling a large suitcase, or looking at a phone. | candidate | 3/3 | `first_slowed` | 37/52 (0.71) against 0.75 for always `yes` | no known source |
| In the apart_20cm layout the pair keep to the side their final plan already takes and almost never stop or back up. | candidate | 2/3 | `stopped` | 52/52 (1.00) against 1.00 for always `no` | no known source |
| Stopping and backing up are rare and appear mainly when a holds_ground person in a talk session faces a cane or load and the plan is failing. (needs communication) | unstable | 1/3 | `stopped` | 52/52 (1.00) against 1.00 for always `no` | no known source |
| People signal with eye contact, a nod or a wave when the other drifts toward their side or the plan is failing, and speak mainly to warn about a load or greet a known other. (needs communication) | candidate | 2/3 | `signalled` | 40/52 (0.77) against 0.35 for always `yes` | no known source |
| People resolve by common sense and habit rather than by law or a published study, and the few who name a local custom describe keeping left on Singapore walkways. | unstable | 1/3 | `spoke` | 50/52 (0.96) against 0.96 for always `n/a` | no known source |
| People default to steering to their own right when they meet someone coming the other way, turning a modest angle early. | unstable | 1/3 | `first_side` | 23/52 (0.44) against 0.46 for always `right` | Singapore pedestrian keep-left convention as reported by participants; no known source |
| In a giving-way pair with one constrained or elderly person, the pair settles on passing to their own right. | unstable | 1/3 | `passing_side` | 38/52 (0.73) against 0.73 for always `right` | Everyday courtesy and keep-side custom reported by participants |
| Signalling is used opportunistically by holders of ground and by people who know each other, accompanying a turn rather than replacing it. (needs communication) | unstable | 1/3 | `signalled` | 46/52 (0.88) against 0.35 for always `yes` | no known source |
| Speaking in the talk condition is rare and short, an excuse-me phrase alongside a modest turn, not a negotiation. (needs communication) | unstable | 1/3 | `spoke` | 51/52 (0.98) against 0.96 for always `n/a` | no known source |
| A first plan that weaves both ways crosses the other's line and the pair collides or near-misses, the weave coming from dithering gives_way people. | unstable | 1/3 | `passed_first` | 29/52 (0.56) against 0.58 for always `together` | no known source |
| People default to turning to their own right to make room, so the pair passes right shoulder to right shoulder. | unstable | 1/3 | `first_side` | 20/52 (0.38) against 0.46 for always `right` | no known source |
| A person who holds their ground sends no turn and lets the other go round them. | unstable | 1/3 | `first_side` | 20/52 (0.38) against 0.46 for always `right` | no known source |
| People speak only in the talk condition, and then mostly to excuse themselves, warn, or greet a known or older person; one short utterance per person. (needs communication) | unstable | 1/3 | `spoke` | 2/52 (0.04) against 0.96 for always `n/a` | no known source |
| The urgent, unencumbered person speeds up instead of yielding, turning only slightly at 3 m, and the encounter often goes to a near miss or collision. | unstable | 1/3 | `first_slowed` | 42/52 (0.81) against 0.75 for always `yes` | no known source |

Fidelity says whether a rule describes the LLM agents' behaviour, not whether it describes people (RF-14). References and debrief sources are unchecked.
