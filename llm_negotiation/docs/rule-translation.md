# Rule translation (track #55; issue #67, RF-12)

RF-11 (`rule-extraction.md`) extracts rules in plain words: a condition, an action, exceptions,
factors (columns of its table), references and a `predict` list. negsim cannot run such a rule.
RF-12 translates each kept rule into **rule format 3** (`rule-format.md`), the format negsim's
rule provider follows, checks it with the existing loader, records what the format could not
say, and then runs it: alone in ORCA on the Step 1 sessions it was extracted from (the
**identity check**) and alone in a crowd (**crowd screening**, as in `rule-generation.md`,
section 8).

The supervisor said the format is not important (meeting of 2026-10-20), so this step is kept to
what negsim needs to run a rule. **Format 3 is not extended here**: what it cannot express is a
finding about the format, not about the model.

```
python run_experiment.py configs/translation/round1_head_on.yaml --plan
python run_experiment.py configs/translation/rf12_mock_rehearsal.yaml                # mock, runs_mock/
python run_experiment.py configs/translation/round1_head_on.yaml --client deepseek --confirm
```

Code: `negsim/translation/` (`prompt.py`, `reply.py`, `losses.py`, `identity.py`,
`experiment.py`, `mock.py`). Template: `translate_v1` (frozen). Tests:
`tests/test_translation.py`.

## 1. Which rules

The rules an extraction stored with `status: candidate` (found in at least 2 of its 3 runs),
read from its store and checked against the SHA-256 the store froze each with. An `unstable`
rule is not passed on (RF-11's rule); a mock rehearsal may include them (`statuses`), a paid run
may not. A rule that reads ethnicity or attractiveness is never stored by RF-11, so it never
arrives here.

## 2. What the translator is shown

One system message, the same for every rule (so the provider can cache it): the role, the task,
and the rule format exactly as `rulegen_common_v2` described it to rule generation (#32): the
keys, the kinds of meeting, comparisons, prefixes, the field list generated from the field
catalogue and the format 3 schema (refused if it is not the list that template was frozen with),
the directive fields and the format example with placeholders. The task:

1. write the one format 3 rule that comes closest to the rule given;
2. add nothing the rule does not say;
3. where the format cannot say a part (a condition it has no field for, when an action starts,
   a turn by an angle, how long it lasts, a signal or words), leave it out or write the nearest
   thing, and list the part under `lost`;
4. give `null` if nothing of it can be written;
5. never read ethnicity or perceived attractiveness.

One user message: the encounter (the extraction config's line), the rule's `rule`,
`applies_when`, `action`, `exceptions`, `needs_communication`, each column of `factors_used`
with the meaning the extraction template (`extract_v1`) gave it, the `predict` list, and the
meaning of the column it predicts. **Not shown:** its fidelity, debrief support, references or
provenance.

The reply is one JSON object: `rule` (format 3, or null), `lost` (each part with its `kind`:
`condition`, `start`, `turn`, `speed`, `duration`, `signal_or_talk` or `other`, and `how`:
`left_out` or `approximated`) and `note`. It is read with rule generation's tolerances and asked
again once if it cannot be read (`reply.py`).

## 3. The category of a translation

`negsim.rulegen.validate.validate_proposal`, in format 3, with age, gender, speed and size
visible, so the categories and their precedence are rule generation's (`rule-generation.md`,
section 6): `protected_attribute`, `needs_communication` (it reads what the two cannot both see,
such as assertiveness), `format_limit`, `inconsistent`, `schema_error`, `valid`. One more:
**`not_expressible`**, when the translator gave `null`. A `format_limit` or `not_expressible`
translation is counted as a finding about format 3.

## 4. What was lost

Two records, side by side, per rule and counted across rules (`summary.json`, `lost`):

- **The translator's own list** (`lost`), by kind.
- **Mechanical checks of the extracted rule, independent of the model** (`losses.py`):
  - each column of `factors_used` mapped to the format 3 field that reads it, or to why none
    does: `readable` (age, gender; the distance at which a person decided, as
    `pair.distance_m`), `unobservable` (assertiveness, residence, a memory, urgency: only the
    person knows them, and the loader refuses them as `unobservable_field`), `no_field` (a
    cane, a suitcase, a phone, whether the two know each other, the layout, the surroundings,
    the time of day, how many decisions a person made), `communication` (a signal, words, the
    condition), `protected`, `behaviour` (what was done or happened), `label`, `unknown`;
  - the words of `rule` and `action` searched for what format 3 has no directive for: a turn by
    an angle, a turn or step aside at all (a side preference says only which side), a start
    distance or moment, a duration or "until", a walking speed (a speed scale only
    approximates it), stopping or backing up (format 3 backs up only inside a single-file
    stretch), a signal or words. These are flags read from words; they never change a category.

## 5. Rules that need communication

A rule extracted as `needs_communication` (it held only when a signal or words were used, D9)
is translated and, if valid, written, but marked **not runnable in ORCA** (its notes say so):
nobody signals or talks in ORCA. It is not replayed or screened. The report counts how many
there are and how many were written.

## 6. The writer

A valid translation is written into the experiment's staging database,
`runs/<experiment>/rule_db_staging/extracted/`, laid out as rule generation's
(`negsim.rulegen.writer.StagingDatabase`: write-once files frozen in a manifest; the rule loader
reads it). The code, never the model, fills:

- `rule_id`: `ext_` and the extracted rule's id without its `x_`
  (`x_head_on_6455ca5589` becomes `ext_head_on_6455ca5589`);
- `schema_version` 3, `version` 1, `status` `candidate`; `description` is the extracted rule's
  sentence, `intent` the translator's if it gave one;
- `provenance.source_type: extracted`; `source_ref` names the extracted rule, its version, file
  and SHA-256, and the translation record; `author` names the model and template;
- `validation_evidence`: the extracted rule's references, each `status: unchecked` (RF-14
  checks them).

**The `extraction` block is not in the rule file** (a decision of this issue, `WORK_LOG-67.md`,
D-A). Format 3's `provenance` takes no other keys, and adding one would be a new schema version,
which the issue rules out. The block (the extraction experiment, rule id and version, file,
SHA-256, status, stability, category, target and held-out fidelity) is in the translation
record and in `summary.json`, and `source_ref` names the same rule and SHA-256 in the rule file.

## 7. The identity check

Each runnable rule is switched on alone (plain ORCA for every pair it does not match) and run on
each Step 1 session it was extracted from (`provenance.sessions_used`): the session's case, on
the case's own run and seed, with the session's bodies (a person pulling a suitcase is wider),
and each person's age and gender, visible as the session's design showed them. Nobody follows a
plan. It is measured from the session's first decision with the code that measured the session
(`negsim.resolution.outcomes.physical_outcome`), and compared with what the session's plans did
in `plan_only`:

- the same agent first out of the conflict zone, or both together (`who_passed_first`);
- each person went by on the same side, in their own frame (`passing_side_a`, `_b`).

A session is **reproduced** when both hold. The same is measured for **plain ORCA on the same
seed**, so that a rule is credited only with what plain ORCA does not already do. Plain ORCA must
also be the run the session recorded (its `*_plain_orca` columns); a session where it is not is
left out of the shares and counted. Shares are given over all sessions and over those the rule
matched. A low share means the translation lost something, or that ORCA under a rule does not
behave as the agents' plans did; the check cannot tell the two apart, which is a limitation.

On round 1, plain ORCA never resolves a head-on in `plan_only`'s sense: in all 288 sessions the
two never touch but come within the near-miss distance. So the identity check compares who went
first and on which side, not whether the meeting was resolved.

The rows are `identity/<rule_id>.csv`; the summary is a `screening` entry of kind `replay`
(`verdict: recorded`, no pass mark) in the rule's next version. Nothing else is written: the runs
are deterministic, and each row names its case and seed.

## 8. Crowd screening

`negsim.rulegen.replay.CrowdScreen`, unchanged: the rule alone in the two-way flow
(`bidirectional_flow`, 50 + 50) on the primary baseline, for `screening.repeats` paired seeds,
beside the same flow with no rule; ages and genders in turn from `screening.ages` and `genders`
(round 1's 25 and 70, female and male). A rule that gridlocks the flow where the baseline did not
fails. The result is a `screening` entry of kind `crowd` in the rule's next version.

## 9. What is stored

Under `runs/<experiment>/` (`runs_mock/` for the mock):

```
config.json, invocations.jsonl, preview.json   the config, the extraction's rules (file, SHA-256), the template; each invocation; the worst case
translations/<x_rule_id>.json                  the exact messages, every attempt's raw reply, model, tokens and cost, the reply as read
rule_db_staging/extracted/                     the staging database: ext_<...>.v1.yaml (the translation), .v2.yaml (with its screening)
identity/<ext_rule_id>.csv                     one row per Step 1 session
screening/                                     the crowd runs (avoidance run folders)
summary.json, report.md                        per rule: the category, what was lost, the identity check, the crowd; counted across rules
```

A translation record is written once and never rewritten: running the experiment again reuses
it, and redoes only an aborted one (set aside as `<rule_id>.aborted<n>.json`). Writing, the
identity check and screening are idempotent: a staged rule that has its screening already is
not run again. Once a translation has a record, a changed config (other than the budget, the
identity check or the screening) is refused.

## 10. Money

One call per rule (two if the reply must be asked again). `--plan` gives the worst case: peak
prices, nothing cached, every reply at the full allowance (`llm.max_tokens`, 1,500 by default),
every retry taken. A paid run needs `--confirm` and translates only `candidate` rules; every call
goes through the budget guard on the experiment's own calls. For round 1's four candidates the
worst case is **USD 0.028**. The translator sees no ethnicity or attractiveness, so no ethics
sign-off is needed.

## 11. Round 1

`runs/rf12_round1_head_on/translation_report.md` (paid, 2026-10-26, USD 0.0017). Of RF-11's four
kept rules, three translations are valid and one (signalling) is not expressible. Two of the
valid ones are the same as plain ORCA, and the third (both people slow in every head-on)
gridlocks the crowd. None changes the Step 1 outcome: 0.36 reproduced, plain ORCA's own share.

## 12. Not done here

- Promotion into `rule_db/` (RF-14), and running the whole rule set together (RF-18).
- Extending format 3.
- **Optional task 8, a second simulator**: not done in this issue.
