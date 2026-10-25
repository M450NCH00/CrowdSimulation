# RF-30: round 1 (head-on), the three conditions under `keep_line`

Issue #104, track #55. Paid run of 2026-10-25 (Sunday, off-peak), approved by the user for this issue
only with a cap of USD 0.30 (`CLAUDE.md`, pending item 1). Every number below comes from a file
named with it; the process is in `WORK_LOG-104.md`.

## In short

- **Head-on passes the gate under `keep_line`, narrowly.** Pooled over the 192 design sessions of the
  three conditions, as RF-10's gate was fixed: **102 of 192 resolved in `plan_only` (0.53, 95% CI 0.46
  to 0.60)** against the 0.50 threshold. The interval includes 0.50: it passes on the point estimate,
  not by a clear margin. (RF-10, under the rule that undid sidesteps: 59 of 192, 0.31.)
- **Signalling and talking still do not help.** Independent 0.55, non-verbal 0.58, talk 0.47; paired
  by cell, none differs from another (McNemar p = 0.86, 0.49, 0.30).
- **Each condition gained from `keep_line`** against RF-10's same sessions: non-verbal 17 → 37
  (p = 0.0008), talk 20 → 30 (p = 0.099), independent 22 → 35 (p = 0.0002, re-executed in RF-29).
- **What still fails is the pavement dance**: in most collisions both stepped aside, towards the same
  wall (non-verbal 16 of 22, talk 19 of 26). **The agents' signals and words do not say which way**:
  nods, eye contact and "wave on" make up nearly all signals, and only 4 of 92 messages name a side.
  They communicate goodwill and who goes first, not the side, which is what the dance needs.

## 1. The run (`cost.json`, `../../spend_ledger.jsonl`)

| | |
| --- | --- |
| Sessions | 192 of 192, non-verbal and talk, 96 each (64 design, 16 exact repeats, 16 in pairs): RF-10's same sessions and people; every first prompt word for word RF-10's |
| Execution | `protocol.execution: keep_line` (a step with no turn keeps the agent's line; issue #101); everything else RF-10's |
| Independent | not rerun: `runs/rf10_round1_head_on_keep_line/` (RF-29's exact re-execution of RF-10's independent sessions) |
| Cost | **USD 0.221170** (1,446 calls, off-peak, no error; 7 transport retries costed as upper bounds) of the USD 0.30 cap; balance USD 0.86 → **0.65** |
| Unreadable | non-verbal 11 of 515 decision points, talk 6 of 524 (RF-10: 17 of 544, 8 of 547) |
| Model | `deepseek-flash`, fingerprint `e72d3c7f663d3e1383b00b3884cb4501`, as RF-10's |

## 2. The gate (`analysis/gate_pooled.md`)

Pooled with `runs/rf10_round1_head_on_keep_line` (the same fixed gate; no session counted twice;
`analysis.gate --with`). **The pooling is a choice**: the independent condition comes from a
re-execution of RF-10's plans (exact, no call) and the other two from this run a day later, on the
same model string and fingerprint.

| Group | Resolved | Rate (95% CI) |
| --- | --- | --- |
| **all (the gate)** | **102 / 192** | **0.53 (0.46 to 0.60): passes** |
| independent | 35 / 64 | 0.55 (0.43 to 0.66) |
| non-verbal | 37 / 64 | 0.58 (0.46 to 0.69) |
| talk | 30 / 64 | 0.47 (0.35 to 0.59) |
| walking lines aligned | 55 / 96 | 0.57 (0.47 to 0.67) |
| walking lines 20 cm apart | 47 / 96 | 0.49 (0.39 to 0.59) |
| `plan_orca` (baseline) | 106 / 192 | 0.55 (0.48 to 0.62) |
| plain ORCA | 0 / 192 | 0.00 (0.00 to 0.02) |

## 3. Against RF-10, condition by condition (`analysis/compare_rf10_round1_head_on_*.md`)

| Condition | RF-10 (`as_prompted`) | RF-30 (`keep_line`) | Paired: only RF-10 / only RF-30 | McNemar p | Readable only |
| --- | --- | --- | --- | --- | --- |
| non-verbal | 17 / 64 | 37 / 64 | 7 / 27 | 0.0008 | 12 / 46 → 26 / 46, p = 0.0066 |
| talk | 20 / 64 | 30 / 64 | 10 / 20 | 0.099 | 20 / 56 → 28 / 56, p = 0.18 |

## 4. The conditions against each other, paired by cell

| | Both | Only the first | Only the second | Neither | McNemar p |
| --- | --- | --- | --- | --- | --- |
| independent vs non-verbal | 21 | 14 | 16 | 13 | 0.86 |
| independent vs talk | 16 | 19 | 14 | 15 | 0.49 |
| non-verbal vs talk | 17 | 20 | 13 | 14 | 0.30 |

## 5. How it fails, and what the agents communicate (`analysis/lateral.md`)

| `plan_only` outcome | Condition | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| collision | independent | 3 | 16 | 8 |
| collision | non-verbal | 1 | 16 | 5 |
| collision | talk | 1 | 19 | 6 |
| resolved | non-verbal | 33 | 0 | 4 |
| resolved | talk | 27 | 1 | 2 |

- **Signals:**
  - non-verbal: nod 131, eye contact 67, wave on 21, hold up a hand 9;
  - talk: nod 99, eye contact 98, wave on 95, hold up a hand 15, point 4.
- **Messages:** 92 in 44 of the 64 talk sessions. **4 name a side** ("Thanks, coming through on your
  right!", "Excuse me, coming through on your left!"); the rest greet or give way.
- **Resolving did not go with communicating:**
  - non-verbal: 29 of 49 sessions with a signal seen resolved, 8 of 15 without;
  - talk: 17 of 34 with a message, 13 of 30 without; 25 of 55 with a signal seen, 5 of 9 without.

## 6. What it means

- **Step 1 for head-on:** with plans carried out as the prompt describes them, `deepseek-flash` agents
  resolve about half of head-on meetings on their own plans, in every condition. That just meets
  the 0.50 gate (point estimate 0.53, lower bound 0.46).
- **Communication does not help, because it does not carry the side.** The available signals (nod,
  eye contact, wave on, hold up a hand, point) say "I see you" or "you go first", not "I'll go to my
  right"; and in talk the agents rarely say a side. A pair that both step aside, towards the same
  wall, is not saved by a nod.
- **The failure that remains is a convention problem**, the kind a rule like "keep right" solves.
  That is a candidate for Step 2 (RF-11): of the 102 resolved sessions, 66 passed keeping right
  (independent 27 of 35, non-verbal 23 of 37, talk 16 of 30; `passing_side_*_plan_only` in
  `outcomes.csv`), and the failures are mostly pairs that did not settle on one side.
- **For the supervisor:** whether head-on counts as resolved by the LLM (0.53, interval including
  0.50) and so goes on to rule extraction in RF-11.

## 7. Caveats

- **The pooled gate mixes a re-execution (independent) with a new run (non-verbal, talk).** Both
  are RF-10's sessions under `keep_line`, on the same model string and fingerprint.
- **`keep_line` is the user's reading of the prompt**, decided after RF-29; RF-10's original numbers
  stand as what `as_prompted` made of the same kind of plans.
- **The model's own randomness is large** (exact-repeat cells with one outcome in every run: 2 of 8
  non-verbal, 1 of 8 talk), so a single run is one sample.
- One model at temperature 1.0; the signal vocabulary is the template's (`resolve_v6`).
