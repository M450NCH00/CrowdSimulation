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
What RF-11 hands over (`runs/rf11_round1_head_on/head_on/`): 16 stored rules, of which 4 are
`candidate` (found in 2 or 3 of 3 runs) and go to RF-12; the 12 `unstable` ones do not
(`rule-extraction.md`, section 7). One candidate is `needs_communication` (signalling).

The candidates read RF-11 table columns that format 3 has no field for: `own_assertiveness`
(the loader refuses assertiveness as `unobservable_field`), `other_mobility_aid`, `other_load`,
`other_distraction`. Only age and gender have format 3 fields. So `format_limit` and "what was
lost" will be the main findings, as the issue expects.

1. **Template `translate_v1`** (new kind `rule_translation`, frozen). It `uses`
   `rulegen_common_v2`, so the format 3 description, glossary and format example are #32's
   word for word (glossary hash checked on load). The user message is the extracted rule:
   `rule`, `applies_when`, `action`, `exceptions`, `needs_communication`, `factors_used` with
   each column's meaning from the extraction template it came from (`extract_v1`), and
   `predict`. The reply is one JSON object: `rule` (format 3, or null when nothing of it can be
   written), `lost` (each part left out or approximated, with a `kind` from a fixed list and
   `how`), `note`.
2. **Validate** each translated rule with `negsim.rulegen.validate.validate_proposal`, format 3.
3. **What was lost**, two ways, side by side: the translator's own `lost` list; and a
   mechanical check, independent of the model: each `factors_used` column mapped to a format 3
   field or to why it has none (unobservable, no field, communication, protected), and the
   action's words searched for a turn angle, a start distance, a "wait until", a speed and a
   signal. Counted across rules.
4. **`needs_communication`** extracted rules: translated, written if valid, marked not
   runnable in ORCA, not replayed or screened. Counted.
5. **Writer**: a staging database `runs/<exp>/rule_db_staging/extracted/` (the writer's
   `StagingDatabase`), rule ids `ext_<type>_<hash>` from RF-11's `x_` id,
   `provenance.source_type: extracted`, `validation_evidence` = the references, each
   `unchecked`.
6. **Identity check**: each runnable rule alone, plus plain ORCA, on the Step 1 sessions it was
   extracted from (`provenance.sessions_used`): the session's case, seed, bodies, ages and
   genders, measured from its first decision with the same outcome code (`physical_outcome`).
   Share reproducing Step 1's `plan_only` who-passed-first and both passing sides, beside plain
   ORCA's share on the same seeds. Plain ORCA is checked against the source's recorded
   `*_plain_orca` columns.
7. **Crowd screening** with `negsim.rulegen.replay.CrowdScreen`, one rule at a time (#30,
   section 8).
8. Optional second simulator: only if time allows.
9. **Tests** on the mock, then a mock rehearsal on RF-11's real rules.
10. **Paid run**: about 4 calls. Needs its own approval and cap in `CLAUDE.md`. I stop and ask
    before any paid call.

### Design decisions taken here (flagged for the user)
- **D-A. The `extraction` block is not in the rule file.** Format 3's `provenance` is closed
  (`additionalProperties: false`), so a rule file with `provenance.extraction` would need a
  schema version 4, and the issue says not to extend format 3. Instead the rule file names the
  RF-11 rule (id, version, file, SHA-256) in `source_ref`, and the full `extraction` block is in
  the translation record and the summary. If the user wants it inside the rule file, that is a
  new schema version, a separate decision.
- **D-B. Temperature 0** `[placeholder]` for the translator: one translation per rule, so the
  model's most likely one, not a random sample (RF-11 sampled at 1.0 because it ran three times).
- **D-C. Only `candidate` rules** are translated in a paid run (RF-11's rule). A mock rehearsal
  may include `unstable` ones to exercise more paths.
- **D-D. The identity check compares with Step 1's `plan_only` outcome** (the outcome RF-11's
  "resolved" and "passing side" columns come from), and reports plain ORCA's share on the same
  seeds beside it, so that a rule is credited only with what plain ORCA does not already do.

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
