# RF-55: which half of `resolve_v11` helped? (issue #157)

Run on 2026-11-28, 13:24 to 15:13 UTC (a Saturday, so off-peak), on `deepseek-flash`, fingerprint
`bc19ba97cbe016479903222bb1578db6` on every call (RF-40's and RF-54's). **Cost USD 0.3420** of a USD 0.60
cap (2,116 ledger lines, 272 sessions, all off-peak, no API error); balance USD 5.26 before, **USD 4.91**
after. A 24-session pilot came first (USD 0.0281).

Serves #55's **step 1 (resolve)**: what in the agents' view lets a head-on pair resolve the conflict.
It is not a rule, and nothing here asks who goes first.

**What was run.** RF-40's 272 silent head-on sessions (the same people, seeds and order of asking as
RF-40 and RF-54; `configs/resolution/rf55_round1_head_on_short_moved.yaml`), thinking off. Only the core
template changed. `resolve_v12` is `resolve_v9` word for word, plus `resolve_v9`'s own "Since you last
looked, they have moved over to your {side}." under the short line of someone 5 to 10 m away, which
`resolve_v9` printed on full lines (under 5 m) only. No gap numbers, no "both moved over". RF-54's
`resolve_v11` had added two things at once; this run adds only the first:

| | short lines (5 to 10 m) | full lines (under 5 m) |
| --- | --- | --- |
| RF-40, `resolve_v9` | nothing of the other's move | "they have moved over to your {side}" |
| **RF-55, `resolve_v12`** | **"they have moved over to your {side}"** | as `resolve_v9` |
| RF-54, `resolve_v11` | "you and they have both moved over…" (when so) and the gap numbers | as `resolve_v9`, plus the same two lines |

Decision 1 is unchanged: its prompt is RF-40's word for word (checked on the pilot's 24, and by the tests).

**How it was compared.** Paired by session id with RF-40 and RF-54, over all 256 design sessions
(4 repeats; the 16 pair sessions are in the records but not analysed), with RF-54's method:
`analysis/rf55_tables.py` (`analysis/rf55_tables.md`); `analysis.compare` for repeat 1
(`analysis/compare_rf40_round1_head_on_turn_taking_silent.md`).

## The answer: telling the move was the helpful half; the gap numbers did not add to it

| Resolved in `plan_only` (256 each) | RF-40 (`v9`) | **RF-55 (`v12`)** | RF-54 (`v11`) |
| --- | --- | --- | --- |
| All | 163 (0.64) | **206 (0.80)** | 191 (0.75) |
| aligned (128) | 91 (0.71) | 100 (0.78) | 98 (0.77) |
| 20 cm apart (128) | 72 (0.56) | **106 (0.83)** | 93 (0.73) |

| Paired test (McNemar exact) | lost, gained | p |
| --- | --- | --- |
| RF-55 against RF-40 (the move on short lines) | 28, 71 | **< 0.0001** |
| — 20 cm apart | 12, 46 | < 0.0001 |
| — aligned | 16, 25 | 0.21 |
| RF-54 against RF-55 (the gap numbers, given the move) | 49, 34 | 0.12 |
| — 20 cm apart | 26, 13 | 0.053 |

- **Telling people at 5 to 10 m that the other has moved over** raised the resolved share from 0.64 to
  0.80. RF-40's own repeats, compared two at a time, give p from 0.18 to 0.85 (RF-54's report).
- **RF-54's gap numbers did not add to it.** Against RF-55, `resolve_v11` resolved 15 fewer sessions;
  not significant overall (p = 0.12), close to it in the 20 cm geometry (p = 0.053). So RF-54's gain
  came from the move being told at all, and the numbers, if anything, took some of it away.
- **Not luck at decision 1 this time.** RF-55 drew 112 same-wall starts, RF-40 111 (RF-54 drew 97).

## Recovery from a same-wall start

| Start (`analysis.start_walls`) | RF-40 | **RF-55** | RF-54 |
| --- | --- | --- | --- |
| Same wall: sessions, resolved | 111, 44 (0.40) | 112, **79 (0.71)** | 97, 53 (0.55) |
| Opposite walls: sessions, resolved | 136, 115 (0.85) | 134, 119 (0.89) | 151, 133 (0.88) |
| Dance in same-wall starts (both change wall less than 1.0 s apart), failed | 0 | **9, 4 failed** | 2, 1 failed |

- Same-wall starts recovered 0.71 against RF-40's 0.40 (Fisher p < 0.0001) and RF-54's 0.55 (p = 0.021).
- **The dance rose with it**, as RF-54's issue warned: 9 of 112 same-wall starts, 4 of which failed.
  It costs fewer sessions than the recoveries gain.

The reaction the line is meant to change, at a decision where, since that person's last decision, both
had moved 0.1 m or more towards the same wall (measured in the `plan_only` replay, the same in all three):

| Reply | RF-40 (not told) | **RF-55 (told they moved)** | RF-54 (told the gap) |
| --- | --- | --- | --- |
| Back towards the other wall | 19 (0.12) | **74 (0.40)** | 29 (0.17) |
| Further to the same wall | 99 | 97 | 115 |
| No sidestep | 35 | 12 | 23 |
| Unreadable | 10 | 1 | 1 |
| All | 163 | 184 | 168 |

Back towards the other wall: RF-55 against RF-40, Fisher p < 0.0001; against RF-54, p < 0.0001. In RF-54
this per-decision change was small and not significant; in RF-55 it is large.

## Why the numbers did worse (not tested; to keep in mind)

- Sampled RF-54 replies at these decisions (4, by a fixed random seed, all "further to the same wall")
  read a small or unchanged centre-to-centre gap as room: "we're already offset … easing further left
  keeps the gap wide" (gap 0.2 m, unchanged); "a small extra sidestep to my right opens a real gap"
  (in line, unchanged). The gap is centre to centre, and two bodies need about 0.5 m or more; the agents
  did not make that comparison. RF-54's work log listed this as a risk. *Four replies, an inference.*
- RF-55's sampled replies that kept going to the same wall give reasons about the other person (age, a
  cane, a phone) rather than the geometry. *Also four replies.*

## What this does not settle

- **Sensitivity differs.** `resolve_v12` reports a move with `resolve_v9`'s threshold (2° off the line
  they were walking along: about 4 cm across for a second's walk at 1.3 m/s); `resolve_v11` printed its
  lines from 0.1 m. So RF-55 may tell smaller moves than RF-54 did.
- **"Both moved over" was not tested alone**, only together with the numbers in RF-54.
- **Unreadable replies**: 35 of 1,524 decision points (RF-40: 52 of 1,657).
- **Human behaviour**: whether people recover this way, and how often they dance, is RF-14's question.

## Possible next steps (not decided)

- Make `resolve_v12`'s short-line move the base for later head-on runs (RF-46's talk condition, the grid
  comparison), in place of `resolve_v9`. It costs nothing more per call.
- `resolve_v12` with thinking on (RF-53 fixed the frame error; this fixes recovery), or in the
  non-verbal and talk conditions.
