# Work Log — Issue #104: [Experiment] RF-30: round 1 (head-on), non-verbal and talk again under keep_line: does signalling or talking help once sidesteps are kept? (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/104
**Branch:** feat/104-rf30-head-on-keep-line (stacked on `feat/101-rf29-sidestep-metres`, as the RF issues are)
**Started:** 2026-10-25 (Sunday: off-peak all day)

## Understanding the issue
RF-29 found that RF-10's execution (`as_prompted`) undid sidesteps, and that RF-10's independent
plans, re-executed under `keep_line`, resolve 35 of 64 instead of 22. The remaining failure is
mostly coordination (the pavement dance), which is what signalling and talking are for. RF-10's
non-verbal and talk sessions cannot be re-executed (their later decisions saw the old movement), so
this issue runs them again under `keep_line`.

**The user's decisions (2026-10-25):** RF-10's full design for non-verbal and talk (192 sessions,
the same sessions and people as RF-10's); the independent condition from the free re-execution;
cap USD 0.30 (recorded in `CLAUDE.md`). Later rounds use `keep_line` (decided after RF-29).

## Plan
1. Config `round1_head_on_keep_line.yaml`: RF-10's, with `conditions: [non_verbal, talk]`,
   `protocol.execution: keep_line`, cap USD 0.30. A test pins it to RF-10's sessions and people.
2. Mock rehearsal; check the first prompts against RF-10's; pricing; balance; paid batch of 6; rest.
3. Per condition against RF-10 (`analysis.compare --condition`); signals and messages; the gate
   pooled over the 192 design sessions with the independent 64 from the re-execution.
4. Report, README, `CLAUDE.md` balance, addendum in RF-10's report.

## Progress log

### 2026-10-25 — Config and test
- Against RF-10's config the diff is the name, the description, the conditions, the execution and
  the cap. `test_rf30s_config_is_rf10s_non_verbal_and_talk_sessions_under_keep_line` (protocol
  equal but for the execution; templates, `llm` and gate equal; the same 192 sessions and people).
- The plan reads 192 sessions, 96 per condition (64 design, 16 exact repeats, 16 in pairs).

### 2026-10-25 — Rehearsed, gate pooling, priced, first paid batch
- `analysis.gate --with`: pools another experiment's design sessions under the same fixed gate,
  refusing a different gate or a session counted twice (test). Writes `gate_pooled.md`.
- Mock rehearsal (`runs_mock/rf30/`, 192 of 192; a first background attempt started in the repo
  root and never ran): the same 192 session ids, cells, people and weights as RF-10's non-verbal
  and talk; **every first prompt (system and user) word for word RF-10's**; every session under
  `keep_line`.
- Pricing page re-read at 08:18 UTC: identical; recorded. Balance USD 0.86.
- Paid batch of 6 (USD 0.006940): all replies readable; 5 or 6 decision points each; signals in
  4, a message in 1; moves aside kept to the meeting (0.2 to 0.7 m). 3 passed; 2 of the 3
  collisions are the pavement dance. Running the other 186.

### 2026-10-25 — The paid run and the analysis
- 192 of 192. **USD 0.221170** (1,446 calls, off-peak, no error; 7 transport retries costed as
  upper bounds), cap USD 0.30. Balance **USD 0.65**. Same model string and fingerprint as RF-10.
- **Gate, pooled with `runs/rf10_round1_head_on_keep_line`: 102 of 192 (0.53, CI 0.46 to 0.60):
  passes, narrowly.** Independent 0.55, non-verbal 0.58, talk 0.47; paired by cell, no condition
  differs (p = 0.86, 0.49, 0.30).
- Against RF-10's same sessions: non-verbal 17 → 37 (p = 0.0008; readable only p = 0.0066), talk
  20 → 30 (p = 0.099; readable only 0.18).
- Collisions are mostly the pavement dance (non-verbal 16 of 22, talk 19 of 26). Signals are nods,
  eye contact and wave on; 4 of 92 messages name a side; resolving did not go with a signal or a
  message. Of the 102 resolved, 66 passed keeping right (talk only 16 of 30).
- **A bug of mine in `analysis.compare`:** its file was named after the base experiment only, so
  the talk comparison overwrote the non-verbal one. Fixed (a non-default condition is named in the
  file; test), the overwritten files removed and both rerun before writing the report.
- Wrote `comparison_report.md` (one claim, "mostly keeping right", checked against
  `outcomes.csv` and given with its numbers); README row; `CLAUDE.md` balance; addendum in
  RF-10's report.

## Open questions / risks
- Pooling the gate over two runs (the independent re-execution and this run) is a choice: the
  three conditions then come from runs a day apart under the same model string. Stated in the report.
- **For the supervisor:** head-on passes at 0.53 with an interval including 0.50; whether it goes
  on to rule extraction (RF-11).
- **For the user:** the signal vocabulary has no side; a later template could add one (for example
  "point to your left"), which would test whether a side signal ends the pavement dance.

## Summary
**What changed.** `configs/resolution/round1_head_on_keep_line.yaml` (RF-10's non-verbal and talk
under `keep_line`) with its test; `analysis.gate --with` (pooling); `analysis.compare` names the
condition in its file; the paid run with its analysis and `comparison_report.md`; README;
`CLAUDE.md` (approval and balance); addendum in RF-10's report; the pricing check.

**Result.** Under `keep_line`, head-on passes the gate narrowly (102 of 192, 0.53). Signalling and
talking do not help, because they do not carry the side; the remaining failure is the pavement dance.

**How it was verified.** The config test; the mock rehearsal (192 of 192, RF-10's sessions and
people, every first prompt word for word RF-10's); the pricing page and balance before paying; a
paid batch of 6 read before the rest; the gate pooling and compare naming tests; every number in
the report checked against its file.
