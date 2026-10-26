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

### 2026-10-26 — Built on the mock (commit b64871d)
- What I did: template `translate_v1` (new kind `rule_translation`; `uses: rulegen_common_v2`, so
  the format text is #32's word for word and its glossary hash is checked on load). I read one
  rendered prompt before freezing it and made two changes: renamed the `yes`/`no` keys (YAML 1.1
  reads them as booleans) and added the meaning of the predicted column, which was missing.
  Frozen before any use. Package `negsim/translation/` (`prompt`, `reply`, `losses`, `identity`,
  `experiment`, `mock`), layer `rule_translation` in `run_experiment.py`, configs
  `configs/translation/round1_head_on.yaml` (cap 0) and `rf12_mock_rehearsal.yaml`.
- Found while building:
  - Plain ORCA in my replay reproduces the source's recorded `*_plain_orca` columns (checked on
    the first session, then on all 76 in the rehearsal: 0 mismatches).
  - **Plain ORCA never "resolves" round 1's head-on**: in all 288 source sessions
    `resolved_plain_orca` is False, with no collision but always a near miss. So the identity
    check is about who went first and on which side, not about resolving.
  - A bug the rehearsal showed: the `validation_evidence` entry's own `kind` was overwritten by
    the reference's `kind`. Renamed to `from: extraction` and `source_kind`.
  - Building a case's run plan takes about 2 s (it scans every config); a replay 0.05 s. The
    plan is cached per case.
- Mock rehearsal on all 16 RF-11 rules (candidate and unstable): 30 s, every category reached;
  the identity check of the mock's rules equals plain ORCA's share (0.36), as expected of a
  symmetric slow-down. Nothing in it is a finding.
- Tests: `tests/test_translation.py`, 36 passed (14.8 s), including the identity check on two
  real RF-30 sessions (one with a suitcase-widened body): a rule that never matches changes
  nothing; a symmetric keep-right rule matches and both pass on their right.
- Worst case for round 1's 4 candidates: **USD 0.028** (`--plan`). DeepSeek balance
  **USD 0.63** at 09:43 UTC (CLAUDE.md recorded 0.64 after #66; 0.01 unexplained, possibly
  rounding). Peak hours until 10:00 UTC.
- Next: the full test suite, docs, then ask the user for the paid run's approval and cap.

### 2026-10-26 — The user's answers; the paid run
- The user approved paid runs for #67 only, cap **USD 0.03** (my recommendation: above the worst
  case of 0.028, so the guard cannot abort a translation), and kept D-A as built (no schema
  version 4). Recorded in `CLAUDE.md` and the config; pricing re-read (no change), recorded in
  `pricing-check.md`.
- Tests: related suites 199 passed. The full suite: 2029 passed, 10 skipped, 2 failed:
  `test_stop_at_cap_...` (the known peak-hour flake, `WORK_LOG-66.md`; the suite started at
  09:4x UTC, peak) and my own config test, which read the config before its cap was raised.
  Both pass on a rerun off-peak (37 passed, 10:11 UTC).
- Waited for off-peak (10:00 UTC). `--client deepseek` without `--confirm`: nothing sent. Then
  `--limit 1` (10:01): `x_head_on_0ecc2d1a6e`, USD 0.0006. I read the reply before going on: a
  careful translation, a no-op rule with every dropped part listed. Then the other three
  (10:05). **Total USD 0.0017**, 4 calls, none retried, all off-peak. Balance USD 0.62 after.
- **Decision (mine, flagged):** the crowd runs are about 24 MB each (432 MB in all), almost all
  `interactions.jsonl` and `pair_interactions.jsonl`. Those and `trajectory.csv` are gitignored
  under `runs/rf12_*/screening/`; each run's `config.json`, `outcome.json` and `events.jsonl`
  are committed (3.4 MB for the experiment). The screening numbers come from `outcome.json`.
  The simulator is deterministic: my replays of plain ORCA reproduced the source's recorded runs
  in 76 of 76 sessions.
- **Results** (`runs/rf12_round1_head_on/translation_report.md`):
  - 3 valid, 1 `not_expressible` (the signalling rule; the translator: "entirely about
    signalling and speaking"). No `format_limit`: the translator dropped what the format could
    not say rather than writing it badly.
  - Two valid translations (`0ecc2d1a6e`, `aacce0961b`) are speed scale 1, no side: **plain
    ORCA**. The third (`6455ca5589`) is "both slow to 0.73 in every head-on": its condition
    (who gives way, facing an older or encumbered other) is gone.
  - Identity check, 76 Step 1 sessions each: every rule matched all 76 and reproduced 0.36 of
    them, **the same as plain ORCA** (same first 0.67, same sides 0.55). No translation changes
    the outcome.
  - Crowd: the two no-ops equal the baseline exactly; **the slow-down gridlocks the flow on both
    seeds** (timeout, 80 and 34 of 100 arrived; 1,518 and 2,262 collision episodes against 86
    and 68).
- Optional task 8 (a second simulator): not done. With nothing of round 1's rules left in
  format 3, a second target is better tried on a later round's rules, or with a richer format.

## Open questions / risks
1. **Format 3 is too narrow for what the agents did.** Who gives way, what each sees of the
   other (a cane, a suitcase, a phone), when they start and how far they turn are what made the
   LLM agents differ from ORCA, and format 3 can read or say none of it. RF-18 (#74) would have
   nothing useful from round 1 to run. Whether to extend the format (a new schema version, its own
   issue), run extracted rules another way, or accept this as the finding is for the user and
   the supervisor.
2. **Should a translator make the "younger slows" step?** `6455ca5589`'s age branch could be
   written as roles by `agent.age`. The template says to add nothing, and the model didn't. A
   `translate_v2` that allows the nearest readable stand-in, with that step listed under
   `lost` as `approximated`, is an option.
3. **One translation per rule, temperature 0** (`[placeholder]`, D-B). Not checked for
   stability.
4. **The identity check cannot tell** a lost translation apart from ORCA behaving unlike the
   plans under any rule. Plain ORCA's share (0.36) is reported beside it for that reason.
5. Crowd screening used two seeds of one flow, as #30 did.
6. Balance: CLAUDE.md recorded USD 0.64 after #66; the endpoint said 0.63 before this run, with
   no ledger line between. Likely rounding of 0.6x; not investigated.

## Summary
**What changed.** A translation step from RF-11's extracted rules to rule format 3:
`negsim/translation/` (prompt, reply, losses, identity check, experiment, mock), frozen template
`translate_v1` (uses `rulegen_common_v2`'s format text word for word), layer `rule_translation`
in `run_experiment.py`, configs `configs/translation/`, `docs/rule-translation.md`, a
`log-schema.md` section, and round 1's paid run `runs/rf12_round1_head_on/` with its report.
Rule format 3 and every earlier config and template are unchanged.

**Why.** Issue #67's tasks 1 to 7 and 9: translate, validate, record what is lost, mark rules
that need communication, write with provenance, check identity on the Step 1 sessions, screen in
a crowd. Task 8 (optional) is not done.

**How it was verified.** `tests/test_translation.py` (36 tests: the template and its glossary,
the reply reader, the column map against every RF-11 column, every mock path's category, the
writer and loader, the identity check on real RF-30 sessions with a no-match rule and a keep-right
rule, the experiment end to end with resume, refusal of a changed config, the paid path
unconfirmed, the budget guard and a rerun, the configs and the command line). The full suite as
above. A mock rehearsal on all 16 RF-11 rules. Plain ORCA's replay checked against the recorded
runs (76 of 76).
