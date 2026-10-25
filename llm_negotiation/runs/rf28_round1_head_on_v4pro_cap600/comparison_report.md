# RF-28: round 1 (head-on), `deepseek-v4-pro` against `deepseek-flash`

Issue #100, track #55. Paid run of 2026-10-25 (Sunday, off-peak), approved by the user for this
issue only with a cap of USD 0.30 (`CLAUDE.md`, pending item 1). The question, after RF-27 found the
description was not the cause: **does a stronger model resolve the head-on meeting?** Every number
below comes from a file in this folder or in RF-10's; the process is in `WORK_LOG-100.md`.

## In short

- **No: the stronger model does not resolve it more often.** On RF-10's own 64 independent design
  sessions, with the same prompts word for word, 18 resolved in `plan_only` on `deepseek-v4-pro`
  (0.28, 95% CI 0.19 to 0.40) against 22 on `deepseek-flash` (0.34). Paired, McNemar's exact
  p = 0.57. Head-on fails the 0.50 gate on both models.
- **But it fails differently.** v4-pro almost never makes the "pavement dance" (both stepping
  towards the same wall: 2 collisions, against 18 on flash). Instead one person often holds the
  line and the other steps aside (only one of the two aside in 37 of 64 sessions, against 11). That
  sidestep alone is too small: the pair pass within the 10 cm near-miss distance (24 near misses,
  against 5), which the gate counts as a failure.
- **Exploratory, found after seeing the data:** v4-pro's pairs avoided touching in 42 of 64
  sessions, against 27 on flash (paired McNemar p = 0.014). So the stronger model coordinates
  better, but still under-sizes the sidestep.
- With RF-27, the picture for Step 1 on head-on is: **neither the description nor a stronger
  model of the same family makes the plans resolve the meeting**. What the stronger model changes
  is who gives way, not by how much.

## 1. The run (`cost.json`, `../../spend_ledger.jsonl`, `analysis/compare_rf10_round1_head_on.md`)

| | |
| --- | --- |
| Sessions | 96 of 96 completed, independent condition: 64 of the design, 16 exact repeats, 16 in RF-10's counterfactual pairs |
| The same sessions as RF-10's | the same 96 session ids, cells, people, weights and replay seeds, and **every first prompt word for word RF-10's** (core template `resolve_v6`); only the model and the reply cap differ |
| Reply cap | 600 tokens (RF-10: 300). The user's decision after the first batch: v4-pro pretty-prints its JSON, and at 300 one of 12 replies was cut off on both attempts. A cap is a ceiling: a reply that fits is unchanged. The longest reply here was 325 tokens, so the raise mattered; none was cut off at 600 |
| Cost | **USD 0.164082** this run (385 calls, all off-peak, no error) plus USD 0.011625 for the first 6 sessions at a cap of 300 (`runs/rf28_round1_head_on_v4pro/`): **USD 0.176** for the issue, of the USD 0.30 cap. One call needed a transport retry and is costed as an upper bound (USD 0.0048), so the true spend is at most this |
| Balance | USD 1.08 before, **USD 0.91** after (`GET /user/balance`) |
| Model | `deepseek-v4-pro`, fingerprint `a307abda487cd1b463329ccb945ce396` in every send |
| Unreadable after the retry | **18 of 192 decision points** (flash on the same sessions: 5 of 192). Mostly an `until` the unchanged parser does not know (13, for example `{"event": "other_passes"}`), and `until` or a distance of 0 (3). The parser was kept the same on purpose (the user's decision), so both models answer to one reply format |

## 2. Resolution (`analysis/gate.md`, `analysis/compare_rf10_round1_head_on*.md`)

| Design sessions (independent) | `deepseek-flash` (RF-10) | `deepseek-v4-pro` (RF-28) |
| --- | --- | --- |
| all | 22 / 64: 0.34 (0.24 to 0.47) | 18 / 64: 0.28 (0.19 to 0.40) |
| walking lines aligned | 11 / 32: 0.34 (0.20 to 0.52) | 11 / 32: 0.34 (0.20 to 0.52) |
| walking lines 20 cm apart | 11 / 32: 0.34 (0.20 to 0.52) | 7 / 32: 0.22 (0.11 to 0.39) |
| **readable only**: sessions with every reply readable in both runs (48) | 18 / 48: 0.38 (0.25 to 0.52) | 15 / 48: 0.31 (0.20 to 0.45) |

Paired, all 64: resolved on both 6, only on flash 16, only on v4-pro 12, on neither 30;
McNemar p = 0.57. Readable only (48): 5, 13, 10, 20; p = 0.68. The unreadable replies do not hide a
v4-pro advantage. The exact-repeat set is about as unstable: 3 of 8 cells had one outcome in every
run (flash: 2 of 8).

## 3. How it fails (`analysis/lateral.md`; a move under 5 cm counts as none)

| `plan_only` outcome | Model | Both to their own same side | Towards the same wall | One or both not aside |
| --- | --- | --- | --- | --- |
| collision | flash | 9 | 18 | 10 |
| collision | v4-pro | 0 | **2** | 20 |
| near miss | flash | 4 | 0 | 1 |
| near miss | v4-pro | 12 | 1 | 11 |
| resolved | flash | 22 | 0 | 0 |
| resolved | v4-pro | 8 | 0 | 10 |

- **Who moves.** In the first plans, 40 of v4-pro's 113 readable ones do not turn at all (flash: 6
  of 123). 22 of them give holding the line as the reason: "I am determined and tend to hold my
  ground. … I expect the younger person to give way"; "I am in a hurry to get to the emergency room
  and determined to hold my ground. I'll keep walking straight at my usual pace." When level, only one of the two had moved aside in 37 of 64 sessions (flash: 11), and
  neither in 4 (flash: 0).
- **That settles the side but not the room.** With one person on their line, the other's
  sidestep has to give the whole clearance. It often does not: v4-pro's pairs passed with a median
  closest gap between bodies of 0.003 m (flash: -0.029 m, that is, overlapping).
- **Exploratory (not fixed before the run):** no contact at all, near misses allowed. Flash 27 of
  64 (0.42, 0.31 to 0.54), v4-pro 42 of 64 (0.66, 0.53 to 0.76); paired, both 18, only flash 9,
  only v4-pro 24, neither 13, McNemar p = 0.014. The gate stays as fixed: a near miss is not a
  resolution.

## 4. What it means

- **Step 1 on head-on, after RF-10, RF-27 and RF-28:** the LLM agents' own plans resolve about a
  third of head-on meetings, whether they are told where the other is (RF-27) or the model is the
  stronger one of the family (RF-28). The gate is failed three times over.
- **What differs between models is coordination.** The stronger model mostly avoids stepping
  towards the same wall by letting one person hold the line. That is a real pattern, and a
  candidate rule ("one keeps the line, the other gives way"), but the plans do not give enough
  room for it to work physically.
- **The common failure is sizing.** On both models and both templates the sidesteps are planned
  in degrees and seconds that do not add up to enough metres for two bodies. That points at the
  step format (option 2 of RF-27's report: a sidestep in metres), not at the model or the
  description.
- **For RF-11 and the supervisor:** head-on fails the gate on every setup tried. By RF-10's issue
  rule, no rule is extracted from it unless the supervisor says otherwise. The supervisor may
  want to see section 3: the side choice is extractable even though the plans fail physically.

## 5. Caveats

- **The reply cap differs from RF-10's** (600 against 300). Flash's replies stayed under 300
  (RF-9's largest: 214 tokens), so they would not have changed; the difference matters only for
  v4-pro's longer replies (largest 325).
- **More unreadable replies on v4-pro** (18 against 5 of 192), from formats the unchanged parser
  refuses. The readable-only comparison gives the same answer.
- **The no-contact result is exploratory**: chosen after seeing the near misses, one test.
- **One model family, temperature 1.0, thinking off, independent condition only.** A model of
  another family, or thinking mode, was not tried (`gpt-6-astra` was weighed and left for later,
  WORK_LOG-100.md).

## Addendum, 2026-10-25: an executor rule (issue #101)

Found in RF-29 (issue #101, `runs/rf29_round1_head_on_sidestep/comparison_report.md`): under `protocol.execution: as_prompted` a step with no `turn` steered the agent back to the path it started on, so a move aside followed by a plain step ("walk on until the other passes") was partly undone before the meeting. The prompt says the agent keeps its line. The independent sessions were carried out again from their recorded plans under `keep_line` (the line kept; no LLM call, exact because every independent decision came at the trigger). Under `keep_line`: flash 35 of 64, v4-pro 21 of 64 (paired p = 0.024): **v4-pro does worse**. Its "one holds the line" strategy leaves a lone sidestep to give the whole clearance (18 of 19 collisions with one or both not aside). The common failure across the runs is then coordination, not sizing. (`runs/rf28_round1_head_on_v4pro_cap600_keep_line/`.)
