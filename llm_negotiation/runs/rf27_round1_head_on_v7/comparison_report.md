# RF-27: round 1 (head-on), `resolve_v7` against `resolve_v6`

Issue #98, track #55. Paid run of 2026-10-25 (Sunday, off-peak), approved by the user for this issue
only with a cap of USD 0.08 (`CLAUDE.md`, pending item 1). The question, left open by RF-10
(`WORK_LOG-65.md`, advice 4): **are the head-on failures the model's spatial judgement, or what the
description leaves out?** Every number below comes from a file in this folder or in RF-10's; the
file is named with it. The process is in `WORK_LOG-98.md`.

## In short

- **Telling the agents where the other is did not help.** On the same 64 design sessions, 17
  resolved in `plan_only` under `resolve_v7` (0.27, 95% CI 0.17 to 0.38) against 22 under
  `resolve_v6` (0.34, 0.24 to 0.47). Paired session by session, 16 went from resolved to not and
  11 the other way: McNemar's exact p = 0.44, no detectable difference either way.
- **Head-on still fails the 0.50 gate**, and the upper end of `resolve_v7`'s interval (0.38) is
  below it, so the missing information does not explain the failure.
- **The agents did use the new lines, but it did not make them coordinate.** Told the other is
  0.2 m to their right, about half stepped away from the other (to their own left) and half kept
  right as before; when the two chose differently, they stepped towards the same wall (18
  collisions under each template). They also planned smaller turns (median largest turn 10°
  against 12° in that layout), and colliding pairs were closer sideways when level (median 0.26 m
  against 0.34 m).
- **So the failures are the model's, not the description's**: choosing a side that the other
  will also choose, and sizing the sidestep for two bodies 0.5 to 0.7 m wide. RF-11 should treat
  head-on as not resolved by this model, unless the supervisor says otherwise.

## 1. The run (`cost.json`, `../../spend_ledger.jsonl`, `analysis/compare_rf10_round1_head_on.md`)

| | |
| --- | --- |
| Sessions | 96 of 96 completed, independent condition: 64 of the design (32 cells × 2 geometries), 16 exact repeats, 16 in RF-10's four counterfactual pairs |
| The same sessions as RF-10's | the same 96 session ids, cells, people (ethnicity included), weights and replay seeds as RF-10's independent sessions (checked; `tests/test_resolve_v7.py`); the system message byte for byte the same; the description differs only by `resolve_v7`'s lines |
| What `resolve_v7` adds | "Their centre is 0.2 m to your right of the straight line ahead of you." (or "on the straight line ahead of you"), from 10 m; the other's width from 10 m; "straight ahead" only within 1° (the user's decisions of 2026-10-25) |
| Cost | **USD 0.049858** (ledger, 386 calls, all off-peak, no error), USD 0.00052 a session |
| Balance | USD 1.13 before, **USD 1.08** after (`GET /user/balance`) |
| Model | `deepseek-flash`, fingerprint `e72d3c7f663d3e1383b00b3884cb4501` in every send, the same as RF-10's on 2026-10-24 |
| Unreadable after the retry | 3 of 192 decision points (RF-10's same sessions: 5 of 192) |

Why 96 and not the issue's 88: RF-10's balanced ethnicity draw rotates the groups over every unit
of the design, counterfactual pairs included. Without the pairs, 29 of 80 sessions got different
people, so the pairs were kept (`WORK_LOG-98.md`).

## 2. Resolution (`analysis/gate.md`, `analysis/compare_rf10_round1_head_on.md`)

| Design sessions (independent) | `resolve_v6` (RF-10) | `resolve_v7` (RF-27) |
| --- | --- | --- |
| all | 22 / 64: 0.34 (0.24 to 0.47) | 17 / 64: 0.27 (0.17 to 0.38) |
| walking lines aligned | 11 / 32: 0.34 (0.20 to 0.52) | 10 / 32: 0.31 (0.18 to 0.49) |
| walking lines 20 cm apart | 11 / 32: 0.34 (0.20 to 0.52) | 7 / 32: 0.22 (0.11 to 0.39) |
| `plan_orca` (baseline) | | 19 / 64: 0.30 |
| plain ORCA | 0 / 64 | 0 / 64 |

Paired: resolved under both 6, only under `resolve_v6` 16, only under `resolve_v7` 11, under
neither 31. That 27 of 64 sessions changed outcome is in line with RF-10's noise floor (identical
prompts gave a different behaviour in 0.86 of pairs), which is why the test is paired and exact.
The exact-repeat set is as unstable as before: 2 of 8 cells had one outcome in every run under
each template.

## 3. How the agents used the new lines

First plans of the design's sessions (each agent's first readable reply; the side of the first
turn in it):

| Layout | Template | Opening turn: left / right / none | Pairs: same own side / opposite / one without a turn | Largest planned turn, median (IQR) |
| --- | --- | --- | --- | --- |
| aligned | `resolve_v6` | 9 / 51 / 2 (2 unreadable) | 21 / 7 / 4 | 14° (10 to 15) |
| aligned | `resolve_v7` | 11 / 50 / 3 | 20 / 9 / 3 | 12° (10 to 15) |
| 20 cm apart | `resolve_v6` | 21 / 36 / 4 (3 unreadable) | 14 / 11 / 7 | 12° (10 to 15) |
| 20 cm apart | `resolve_v7` | 33 / 29 / 2 | 20 / 10 / 2 | 10° (8 to 10) |

- **Aligned:** `resolve_v7` says "on the straight line ahead of you", which is what "straight
  ahead" already implied. Behaviour hardly changed: most keep right.
- **20 cm apart:** each is told the other's centre is 0.2 m to its **right**. The share stepping
  to its own **left**, away from the other, rose from 21 to 33 of 64 agents ("He is old and
  slightly to my right, so I edge a little to my left to leave him space"). Others kept right as
  before ("a small shift to my right opens a clear gap"). The two cues point opposite ways for
  the two people, so the pairs that split (one left, one right) stepped towards the same wall as
  often as before (10 against 11 pairs). And the agents planned *smaller* turns once told the
  other was only 0.2 m off their line.

How they stepped when level (`analysis/lateral.md`; a move under 5 cm counts as none):

| `plan_only` outcome | Template | Both to their own same side | Towards the same wall | One or both not aside | Sideways gap when level, median |
| --- | --- | --- | --- | --- | --- |
| collision | `resolve_v6` | 9 | 18 | 10 | 0.34 m |
| collision | `resolve_v7` | 14 | 18 | 9 | 0.26 m |
| resolved | `resolve_v6` | 22 | 0 | 0 | 0.84 m |
| resolved | `resolve_v7` | 17 | 0 | 0 | 0.91 m |

Under `resolve_v7`, more collisions are pairs that made room on compatible sides but too
narrowly (14 against 9). Giving the sidestep back before the two are level (a step "back" that
starts too early) is a minor cause under both: 13 of 82 colliding agents under `resolve_v7`, 5
of 74 under `resolve_v6`, kept less than half of their largest move aside when level.

## 4. What it means

- **The description was not the bottleneck.** With the sideways offset, the other's width and
  finer directions, the agents resolve no more often. RF-10's failures are the model's: it does
  not settle on a side the other will also take, and it does not size a sidestep for two bodies
  from degrees and durations. This is a Step 1 finding about `deepseek-flash` at temperature 1.0.
- **For RF-11:** head-on fails the gate under both templates; by RF-10's issue rule no rule is
  extracted from it unless the supervisor says otherwise. The agents still pass mostly keeping
  right (both templates), which a side rule could describe, but that is the supervisor's call.
- **Options, each a decision for the user (none is done here):**
  1. A stronger model or thinking mode on the same sessions (`deepseek-v4-pro`, about 4× the
     price; or `deepseek-flash` with thinking on): tests "the model" directly. Paid; needs its
     own approval.
  2. A step format in metres sideways ("move 0.5 m to your right") instead of degrees and
     durations: tests whether the conversion, not the judgement, is what fails. A new template
     and a parser change.
  3. Keep `resolve_v6` for later rounds: `resolve_v7` cost the same and did not help.

## 5. Caveats

- **One model, one temperature, independent condition only.** Non-verbal and talk were left out
  as the issue decided (RF-10 found no difference between conditions).
- **Power:** 64 paired sessions show a large change only. A rise to the gate (0.50) would have
  shown; a change of a few sessions either way would not.
- **The wording is one choice** within the user's decision (a): "centre", "the straight line
  ahead of you". Another wording, or the passing distance (option b in the issue), might do
  differently.
- **Same sessions, a day apart.** The model string and fingerprint were the same in both runs.
