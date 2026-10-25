# Work Log — Issue #98: [Experiment] RF-27: round 1 (head-on), tell the agents how far apart the walking lines are (resolve_v7): are the sidestep failures the model or the description? (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/98
**Branch:** feat/98-rf27-resolve-v7-walking-lines (stacked on `feat/96-viewer-decisions-factors-view-cone`,
which is stacked on RF-10's branch, as the RF issues are)
**Started:** 2026-10-25 (Sunday: off-peak all day)

## Understanding the issue
RF-10 (#65) found head-on fails the resolution gate: 59 of 192 sessions resolved in `plan_only`.
Of 116 collisions, 49 stepped towards the same wall, 40 had one or both not stepping aside, 27
made room too narrowly. The description an agent gets leaves out three things a person would
see: how far the other is from one's own line, the other's width beyond 5 m, and direction finer
than 5° ("straight ahead" hides up to 0.86 m sideways at 9.8 m). This issue builds `resolve_v7`,
which gives them, and compares it with `resolve_v6` on RF-10's independent cells.

**The user's decisions (2026-10-25, all five as recommended in the issue):** (1) say where the
other is relative to one's own line; (2) from 10 m; (3) the other's width from 10 m; (4) "straight
ahead" only within 1°; (5) the reply parser unchanged.

**Paid-run approval (2026-10-25):** the user approved paid runs for this issue only, cap USD 0.08
on `rf27_round1_head_on_v7`; recorded in `CLAUDE.md`, pending item 1.

## Plan
1. `resolve_v7.yaml`: `resolve_v6` word for word plus three view lines (`seen_short_body`,
   `seen_line_offset`, `seen_on_line`) and one setting, `direction_ahead_deg: 1`. Freeze it in
   `MANIFEST.json`.
2. `prompt.py`: render the new lines only for a template that has them, so every older template
   renders exactly as before. The offset is computed from the view itself (distance × sin of the
   bearing, from the line ahead of the agent), so it works in any scenario; given for anyone ahead
   (bearing within 90°), on the short line and in full detail.
3. Tests (`tests/test_resolve_v7.py`): v7 differs from v6 only by those keys; both sides, on the
   line, rounding, a drifting walker, someone behind (no line), the width from 10 m, the 1°
   direction, older templates unchanged, and a mock session end to end.
4. Config `configs/resolution/round1_head_on_v7.yaml`: RF-10's design, independent only, the same
   cells, geometries and exact-repeat set, `resolve_v7`; no counterfactual pairs; cap USD 0.08,
   `stop_at_cap`.
5. Mock rehearsal through `analysis.gate` and `analysis.lateral`.
6. Paid: check the balance, 6 sessions, read them, then the rest.
7. Compare with RF-10's independent sessions: resolution rate per layout, how they stepped, the
   sideways gap, stability on the exact-repeat set, unreadable rate, model string and fingerprint.
8. Report, README, CLAUDE.md balance.

## Progress log

### 2026-10-25 — Built, rehearsed, checked
- **`resolve_v7`** (frozen, `MANIFEST.json`): `resolve_v6` plus `seen_line_offset` ("Their centre is
  0.2 m to your right of the straight line ahead of you."), `seen_on_line` ("Their centre is on
  the straight line ahead of you."), `seen_short_body` (the full-detail width line, from 10 m) and
  `direction_ahead_deg: 1`. **The wording is mine, within the user's decision (a):** "centre",
  because both widths are now given and the agent can work out the clearance; "the straight line
  ahead of you", because it holds whether the agent walks or stands. The offset is distance × sin
  of the bearing (the view's own numbers), to 0.1 m, for anyone within 90° of straight ahead.
  The system text is byte for byte `resolve_v6`'s, so the prompt cache prefix is shared.
- **`prompt.py`**: each new line renders only when the template has its key; `_direction_within`
  is `describe._direction` with the threshold as a parameter (the shared rulegen function is
  unchanged).
- **Config** `round1_head_on_v7.yaml`. **A first version left RF-10's counterfactual pairs out,
  and the mock rehearsal showed that 29 of its 80 sessions then got different people:** the
  balanced ethnicity draw rotates over every unit of the design, pairs included. With the pairs
  kept, the design is RF-10's independent sessions exactly: the same 96 session ids, cells,
  personas, ethnicity weights and replay seeds (checked against RF-10's records; and a test).
  So the run is **96 sessions** (64 design, 16 exact repeats, 16 in pairs), not the 88 the issue
  estimated (it also counted the repeat set as 24 extra, but its first runs are design sessions).
  About USD 0.054 off-peak; the cap stays USD 0.08.
- **`analysis/compare.py`** (new, with tests): the two runs paired session by session; McNemar's
  exact test on the sessions that changed; sidesteps; stability; unreadable; model strings.
- Tests: `tests/test_resolve_v7.py` 24, `analysis/tests/test_compare.py` 8, all passing.
- Mock rehearsal (`runs_mock/rf27_v2/`, 96 of 96) through `analysis.gate`, `analysis.lateral`,
  `analysis.compare`: all ran. (`runs_mock/rf27/` is the first, 80-session version; ignored by git.)
- Before paying (Sunday, off-peak all day): balance **USD 1.13** (`GET /user/balance`, key not
  printed); pricing page re-read and saved (`refs/ln_deepseek_pricing_2026-10-25.txt`): no change,
  `date_checked` 2026-10-25, recorded in `docs/pricing-check.md`.
- Paid batch of 6 (USD 0.003094): 12 of 12 replies readable; model `deepseek-flash`, fingerprint
  `e72d3c7f663d3e1383b00b3884cb4501`, the same as RF-10's. The agents use the new lines ("He is
  old and slightly to my right, so I edge a little to my left"). **A first sign, to check on the
  whole run:** in the 20 cm layout both are told the other is 0.2 m to their right; some step
  away from the other (to their own left), some keep right by habit, and when the two differ they
  step towards the same wall. Running the other 90.

### 2026-10-25 — The paid run and the comparison
- The other 90 sessions: 96 of 96 completed. **USD 0.049858** in the ledger (386 calls, all
  off-peak, no error, no upper-bound estimate), cap USD 0.08; balance **USD 1.08** afterwards
  (`GET /user/balance`). Same model string and fingerprint in every send, the same as RF-10's.
- Full suite while the run went: 2 failures, both expected guards, fixed: RF-27's config joins
  RF-10's in `test_configs_written_before_have_no_ethnicity_anywhere`'s skip list, and the price
  table's pinned `date_checked` moves to 2026-10-25 (`tests/test_llm.py`).
- `analysis.gate`: 17 of 64 (0.27, CI 0.17 to 0.38): fails. `analysis.compare` against RF-10's
  same sessions: 22 → 17; paired 6 / 16 / 11 / 31; McNemar exact p = 0.44. Same-wall collisions 18
  and 18; compatible-but-narrow collisions 9 → 14; exact-repeat cells stable 2 of 8 in both.
- Read further (scratch scripts, numbers in the report): first plans in the 20 cm layout turned
  left (away from the other) 21 → 33 of 64 agents, and the largest planned turn fell from 12° to
  10° (IQR 8 to 10); colliding pairs' sideways gap when level 0.34 → 0.26 m. Giving the sidestep
  back before level is minor (13 of 82 colliding agents under v7, 5 of 74 under v6).
- Wrote `runs/rf27_round1_head_on_v7/comparison_report.md`; README roadmap row; `CLAUDE.md`
  balance. Every number in the report checked against its file.

## Open questions / risks
- Wording of the new lines is mine, within the user's decision (a); see the progress log. Option
  (b) (the predicted passing distance) was not tested.
- **For the user:** whether to test the model directly (`deepseek-v4-pro`, or thinking mode on;
  paid) or a step format in metres sideways (a new template and parser change), and whether later
  rounds use `resolve_v6` or `resolve_v7`. Recommendation: keep `resolve_v6` (v7 cost the same and
  did not help) unless the metres format or a stronger model is tried.
- **For the supervisor (via RF-11):** head-on fails the gate under both templates.

## Summary
**What changed.** Core template `resolve_v7` (frozen) and its rendering in `prompt.py`, off for
every earlier template; `configs/resolution/round1_head_on_v7.yaml` (RF-10's 96 independent
sessions, the same people and seeds, under `resolve_v7`); `analysis/compare.py` (two runs of the
same sessions, paired, McNemar's exact test); the paid run `runs/rf27_round1_head_on_v7/` with
its analysis and `comparison_report.md`; the pricing check of 2026-10-25; `CLAUDE.md` records the
approval (#98 only, USD 0.08) and the balance; README.

**Result.** Telling the agents where the other is, the other's width from 10 m and finer
directions did not help: 17 of 64 resolved against 22 (p = 0.44). The agents used the lines but
did not coordinate on a side and planned smaller sidesteps. The head-on failures are the model's
judgement, not the description's; head-on still fails the gate.

**How it was verified.** `tests/test_resolve_v7.py` (24) and `analysis/tests/test_compare.py` (8);
the full `llm_negotiation` suite (2 expected guard failures, fixed and rerun); a mock rehearsal of
all 96 sessions through the analysis; the session-by-session match with RF-10 (ids, cells,
people, weights, seeds, the system text); a paid batch of 6 read before the rest; the ledger
against the account balance; every number in the report checked against its file.
