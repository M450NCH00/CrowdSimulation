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

## Open questions / risks
- Pooling the gate over two runs (the independent re-execution and this run) is a choice: the
  three conditions then come from runs a day apart under the same model string. Stated in the report.

## Summary (fill in at the end)
