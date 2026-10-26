# Work Log — Issue #67: [Feature] RF-12: translate extracted rules to rule format 3, record what is lost, then replay and crowd-screen them

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/67
**Branch:** feat/67-rf12-translate-rule-format3 (stacked on `feat/66-rf11-rule-extractor`, as every RF branch is; PR #106 merged 2026-10-26)
**Started:** 2026-10-26

## Understanding the issue
RF-11 (#66) extracted plain-language rules from round 1's resolved head-on sessions. They are
not in a rule format, so negsim cannot run them. RF-12 builds the translation step: an LLM
turns each extracted rule into one rule of format 3 (`docs/rule-format.md`), the existing
loader checks it, and what the format could not say is recorded as a finding about the format.
Then each translated rule is written (with provenance back to RF-11), replayed on the Step 1
cases it came from (the identity check: does ORCA plus the rule reproduce the Step 1 physical
outcome?), and screened alone in a crowd as in #30, section 8.

Priority is low (the supervisor: the format is not important). Keep to what negsim needs; do
not extend format 3.

## Plan
(filled in below, after reading the code)

## Progress log

### 2026-10-26 — start
- What I did: checked the state the user asked about. PR #106 (#66) was already merged
  (05:27 UTC), #66 already closed (05:27), and track #55 already ticks #66 with its summary.
  So the next issue in #55's order of work is #67 (RF-12). Branched from
  `feat/66-rf11-rule-extractor`.
- Next step: read `resolution.md` D1/D9, `rule-format.md`, `rulegen_common_v2`, `validate.py`,
  `writer.py`, `replay.py`, and RF-11's stored rules; then write the plan.

## Open questions / risks

## Summary (fill in at the end)
