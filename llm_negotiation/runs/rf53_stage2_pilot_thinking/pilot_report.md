# RF-53, stage 2 pilot: does thinking mode resolve more head-on conflicts? (issue #144)

Run on 2026-11-28, 04:50 to 07:01 UTC (a Saturday, so off-peak), on `deepseek-flash`, fingerprint
`bc19ba97cbe016479903222bb1578db6` on all 632 calls (RF-40's and stage 1's). **Cost USD 0.7702** of a
USD 1.00 cap (632 ledger lines, 80 sessions); balance USD 1.38 before, **USD 0.61** after.

**What was run.** RF-40's silent head-on sessions under the turn-taking exchange: repeat 1 of every cell
(64 design sessions, 32 per geometry) and the 16 counterfactual-pair sessions, with the same people,
seeds and order of asking (`configs/resolution/rf53_stage2_pilot_thinking.yaml`). Only the llm block
changed: thinking on, a reply cap of 16,000 (it counts the reasoning, as stage 1 showed), a 240 s
timeout. Template `resolve_v9`, unchanged.

**How it was compared.** `analysis.compare` pairs the 64 design sessions with RF-40's repeat 1
(`analysis/compare_rf40_round1_head_on_turn_taking_silent.md`). The other tables, which set the pilot
against all four of RF-40's repeats (256 sessions), come from `analysis/pilot_tables.py`
(`analysis/pilot_tables.md`). The 16 pair sessions are in the records but not analysed here.

## The answer: about the same resolution rate, but different failures

| | RF-40, thinking off | Pilot, thinking on |
| --- | --- | --- |
| Resolved in `plan_only`, repeat 1 | 42/64 (0.66, 0.53 to 0.76) | **46/64 (0.72, 0.60 to 0.81)** |
| Resolved, all four repeats | 163/256 (0.64) | |
| aligned | 25/32 (0.78) | 24/32 (0.75) |
| 20 cm apart | 17/32 (0.53) | 22/32 (0.69) |

- **Not a significant gain.** The paired test has 28 sessions resolved in both, 4 in neither, 18 only
  with thinking on and 14 only with it off: McNemar exact p = 0.60. Against all 256 of RF-40's sessions,
  Fisher p = 0.24.
- **The 32 changed sessions are within RF-40's own noise.** RF-40's four repeats differ from each other
  in 26 to 31 of the 64 sessions, and resolve 37 to 45 of them. The pilot's 46 is just above RF-40's best
  repeat (45), but one repeat cannot separate that from noise.
- **The gate (0.50) passes** either way.

## What thinking mode did change: the left-and-right error is mostly gone

How the two people had stepped when they came level (`analysis.lateral`):

| | RF-40 (256) | Pilot (64) | Fisher p |
| --- | --- | --- | --- |
| Both towards the same wall (the frame error) | 61 (0.24) | **3 (0.05)** | 0.0004 |
| Both to their own same side (making room) | 169 (0.66) | **52 (0.81)** | 0.023 |
| One or both not aside | 26 (0.10) | 9 (0.14) | |

This is stage 1's result seen in the simulation: the error behind RF-40's E1 to E3 (both stepping
towards the same wall) dropped from about one session in four to one in twenty.

## Why the rate did not rise with it: the remaining failures

The failed sessions (a collision or near miss in `plan_only`), by what the agents' replies did:

| Failure mode | RF-40 (93 failures) | Pilot (18 failures) |
| --- | --- | --- |
| No reversal, yet still met (mostly towards the same wall) | 43 | **0** |
| A sidestep reversed: someone stepped one way, later the other | 45 | **13** |
| One person never sidestepped | 5 | **5** |

The pilot's 18 failures were read by eye (their first decisions are in `decisions.jsonl`). Two patterns:

- **The swap (13).** At the first decision both step correctly, to opposite sides. At the next, one or
  both "move back" to the other side, so they meet again, sometimes more than once. For example, in
  `S_head_on_de176842_8ea28db3_r1` the first person steps right, then left; the second steps left, then
  right. The reasons usually describe the other's sidestep as "drifting into my left side" or "sweeping
  across from my right to my left", and answer it by moving away from the drift. A sidestep made to give
  room is read as the other person coming at you. Reversals are as common with thinking on (24 of 64
  sessions, 0.38) as off (101 of 256, 0.39). With thinking on, though, they are now most of what fails.
- **The one who holds their line (5).** One person says, at every decision, "Keep walking straight ...
  without yielding" or "hold my line", and never sidesteps. The other's sidestep (0.3 to 0.55 m) is too
  small to pass alone in this corridor. This reads as the persona's assertiveness, not a reasoning error.
  It is in 6 of 64 sessions with thinking on against 9 of 256 off (not tested for significance; few
  cases).

## Tokens, time and readability

| | RF-40, silent | Pilot |
| --- | --- | --- |
| Calls a session | 8.3 | 7.9 |
| Cost a session, off-peak | USD 0.0014 | **USD 0.0096 (7 times as much)** |
| Reasoning tokens, decision calls (472) | 0 | median 1,885, mean 2,249, 90th percentile 4,139, max 7,948 |
| Reasoning tokens, debrief calls (160) | 0 | median 304, mean 354 |
| Reply latency, seconds | | median 9.2, mean 11.0, max 48.6 |
| Cut off at the reply cap | | 0 of 632 (all `finish_reason: stop`) |
| Unreadable after the retry | 11 of 473 decision points | 10 of 459 (all `not_json`: a malformed key) |

The 76 sessions after the first four took 2 hours 9 minutes, one after another.

## What it means for the full stage 2 (not approved)

- **Will a full run answer the question?** On the resolution rate, probably not by much. A gain of a few
  points over RF-40's 0.64 would need many more sessions to show `[inference]`. The full silent run would
  add 192 sessions, which, with RF-40's four repeats, gives a paired comparison on all 256. What the pilot
  already shows with confidence is the change in *how* the agents step.
- **Cost, rough `[inference]`.** At the pilot's USD 0.0096 a session, the other 192 silent sessions would
  be about USD 1.85. The 272 talk sessions would be about USD 3.1, scaling the pilot by RF-40's talk-to-silent
  cost ratio (1.19). **About USD 5 in all**, off-peak. The balance is USD 0.61, so a top-up comes first.
- **Wall time** about 13 hours one after another, at the pilot's rate `[inference]`.
- **Other choices worth weighing before a full run:**
  - the swap is the main failure left, and it is about reading the other's sidestep. It may respond to
    the description of the other's movement more than to more reasoning. That would be a template
    change, a new version under the frozen-template rule.
  - `reasoning_effort: low` might keep most of the frame gain at a lower cost. Stage 1 did not test it.

## Limits

- One repeat of each cell, so each geometry's share has an interval about 0.3 wide.
- Thinking mode ignores temperature. So the pilot's repeat-to-repeat noise is not known: RF-40's noise
  is the floor used above, which may not be the pilot's.
- The failure modes are read from the replies' sidestep directions and from the replay's positions when
  level. The reasons were read by eye for the 18 failures only.
- The silent condition only: talk, where the swap might be talked out, is not in the pilot.
