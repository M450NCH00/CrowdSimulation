# RF-54: does telling people how the sideways gap changed help a same-wall start recover? (issue #155)

Run on 2026-11-28, 10:46 to 12:40 UTC (a Saturday, so off-peak), on `deepseek-flash`, fingerprint
`bc19ba97cbe016479903222bb1578db6` on every call (RF-40's). **Cost USD 0.3512** of a USD 0.60 cap
(2,134 ledger lines, 272 sessions, all off-peak, no API error); balance USD 5.61 before, **USD 5.26**
after. A 24-session pilot came first (USD 0.0369).

Serves #55's **step 1 (resolve)**: can LLM agents resolve the conflict, and what in their view stops
them? It is not a rule, and nothing here asks who goes first.

**What was run.** RF-40's 272 silent head-on sessions under the turn-taking exchange (32 cells, 2
geometries, 4 repeats, and the 16 counterfactual-pair sessions), with the same people, seeds and order
of asking (`configs/resolution/rf54_round1_head_on_sideways_gap.yaml`). Thinking off, as in RF-40. Only
the core template changed: `resolve_v11` is `resolve_v9` word for word plus, once either person has
moved across their path by 0.1 m or more since the last look, a line worked out by code:

> Since you last looked, you and they have both moved over to your left.
> Sideways, their centre was 0.1 m to your right of yours and is now in line with yours, so the gap
> between your centres has shrunk.

(the first line only when both moved the same way). Decision 1 is unchanged: in all 272 sessions its
prompt is RF-40's word for word (checked on the pilot's 24, and by the tests).

**How it was compared.** Paired with RF-40's silent session of the same id. `analysis.compare` gives
repeat 1 (`analysis/compare_rf40_round1_head_on_turn_taking_silent.md`); `analysis/rf54_tables.py`
(`analysis/rf54_tables.md`) gives all 256 design sessions, RF-40's own churn between repeats, how the
pair started (`analysis.start_walls`) and the reaction after both moved the same way. The 16 pair
sessions are in the records but not analysed here.

## The answer: more sessions resolved, beyond RF-40's own noise

| Resolved in `plan_only` | RF-40 (`resolve_v9`) | RF-54 (`resolve_v11`) | lost, gained | McNemar exact p |
| --- | --- | --- | --- | --- |
| All four repeats (256) | 163 (0.64) | **191 (0.75)** | 40, 68 | **0.009** |
| aligned (128) | 91 (0.71) | 98 (0.77) | 19, 26 | 0.37 |
| 20 cm apart (128) | 72 (0.56) | **93 (0.73)** | 21, 42 | **0.011** |
| Repeat 1 only (64) | 42 (0.66) | 47 (0.73) | 15, 20 | 0.50 |

- **Beyond the noise floor.** RF-40's own repeats, compared two at a time in the same way (64 cells),
  give McNemar p from 0.18 to 0.85; none comes near 0.009. One repeat (64) is too few to show it.
- **The gain is in the 20 cm geometry**, where RF-40 was worst (0.56).
- **The gate (0.50) passes** (0.75).
- For scale: RF-53's thinking-mode pilot, on repeat 1 only, resolved 46/64 for USD 0.77 (80 sessions);
  RF-54 resolved 47/64 on repeat 1, at USD 0.35 for all 272. The two were not run on the same sessions
  beyond repeat 1, so this is not a test.

## Where it came from: recovery after a same-wall start

How the pair started (the wall each first sidestep went towards, `analysis.start_walls`):

| Start | RF-40: sessions, resolved | RF-54: sessions, resolved | Fisher p (resolved share) |
| --- | --- | --- | --- |
| Same wall | 111, 44 (0.40) | 97, **53 (0.55)** | **0.037** |
| Opposite walls | 136, 115 (0.85) | 151, 133 (0.88) | 0.39 |
| One never sidesteps | 9, 4 | 8, 5 | |

- **Same-wall starts recovered more often**, 0.40 to 0.55: the target of `resolve_v11` (the user's
  choice of 2026-11-28, "Recovery cue"). Within them, someone reversed a sidestep in 71 of 111 (0.64)
  under RF-40 and 71 of 97 (0.73) under RF-54, and a reversal ended resolved in 41 of 71 (0.58) and 49
  of 71 (0.69).
- **Part of the gain is chance at decision 1.** Its prompt is the same in both, yet RF-54 drew fewer
  same-wall starts (97 against 111, Fisher p = 0.24; temperature 1.0). Of the 68 sessions gained, 47 began
  on opposite walls in RF-54. Holding RF-40's mix of starts and using RF-54's rates gives about 186
  resolved (RF-40: 163); RF-40's rates on RF-54's mix give about 170. So roughly 7 of the 28 come from
  the starts, about 21 from what happened after them (an estimate, not a test).
- **The dance stayed rare**: both changing wall less than 1.0 s apart, in 2 of RF-54's same-wall starts
  (1 failed) against 0 of RF-40's; 4 and 2 sessions in all. Thinking mode's pilot had it in 10 of its
  18 same-wall starts.

How they had stepped when they came level (`analysis.lateral`, 256 each):

| | RF-40 | RF-54 |
| --- | --- | --- |
| Both towards the same wall | 61 (0.24), none resolved | **39 (0.15)**, 1 resolved |
| Both to their own same side (making room) | 169 (0.66), 156 resolved | 183 (0.71), 175 resolved |
| One or both not aside | 26 (0.10), 7 resolved | 34 (0.13), 15 resolved |

## The reaction itself moved less than the outcome

At a decision where, since that person's last decision, both had moved 0.1 m or more towards the same
wall (measured in the `plan_only` replay, the same way in both runs; in RF-54 these people were told so,
in RF-40 not):

| Reply | RF-40 (not told) | RF-54 (told) |
| --- | --- | --- |
| Back towards the other wall | 19 (0.12) | 29 (0.17) |
| Further to the same wall | 99 | 115 |
| No sidestep | 35 | 23 |
| Unreadable | 10 | 1 |
| All | 163 | 168 |

Back towards the other wall: Fisher p = 0.16. Most people who are told the gap has shrunk still step
further towards the same wall. A same-wall start needs only one of the two to step back, which is why a
small change per decision can still move the session outcome; but the per-decision change is not
significant on its own, and the replies were not read one by one.

In the debriefs (silent design sessions, 512 and 511), "where they were" as the basis of the side went
from 0.53 to 0.67, and the side detail mentions the gap in 0.34 against 0.58: the agents cite the cue.

## What this does not separate (to keep in mind)

- **Two changes in one.** Under `resolve_v9` someone 5 to 10 m away gets one short line with no
  "they have moved over" (full detail only). Decision 2 comes at about 7.5 m, so RF-40's agents were not
  told the other had moved at all. `resolve_v11`'s line is printed on short lines too, so it adds both
  *that* the other moved and *how the gap changed*. This run cannot say which of the two helped.
- **Same model, fingerprint unchanged**, but RF-40 was run on 2026-11-02 and RF-54 on 2026-11-28; a
  change on the provider's side behind the same fingerprint cannot be ruled out (inference).
- **Unreadable replies**: 58 of 1,519 decision points (RF-40: 52 of 1,657), mostly an unknown `start`
  or `until`, the same kinds as before.
- **Human behaviour**: whether people recover this way (or dance) is RF-14's question, not tested here.

## Possible next steps (not decided)

- To separate the two changes: a template that adds only "they have moved over" on short lines (no gap
  numbers), on the same sessions; about USD 0.35 off-peak at this run's cost.
- `resolve_v11` with thinking on, which fixed the frame error (RF-53) while this fixes recovery.
