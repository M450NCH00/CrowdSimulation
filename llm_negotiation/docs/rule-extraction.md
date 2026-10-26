# Rule extraction (track #55, Step 2; issue #66, RF-11)

Step 1 asked whether LLM agents can resolve a conflict (`resolution.md`). Step 2 takes the
sessions in which they **did**, and finds the hidden rule or pattern behind how they resolved
it, with the reference the rule comes from. An LLM, the **extractor**, reads the results and
writes the rules. Everything around it is code: the held-out split, the tables, the sample, the
checks, the fidelity score, matching the rules of three runs, and storing them with provenance.

```
python run_experiment.py configs/extraction/round1_head_on.yaml --plan
python run_experiment.py configs/extraction/round1_head_on.yaml                      # mock, runs_mock/
python run_experiment.py configs/extraction/round1_head_on.yaml --client deepseek --confirm
```

Code: `negsim/extraction/` (`table.py`, `prompt.py`, `rules.py`, `experiment.py`, `mock.py`).
Template: `extract_v1` (`negsim/negotiation/templates/`, frozen). Tests:
`tests/test_extraction.py`, and `analysis/tests/test_extraction_tables.py`, which checks the
extractor's tables against RF-8's analysis on round 1's data.

## 1. Which sessions

- **Sources.** One encounter type's sessions may be in several resolution experiments. Round 1's
  independent condition is RF-10's re-executed under `keep_line`
  (`runs/rf10_round1_head_on_keep_line`), and its non-verbal and talk conditions are RF-30's
  (`runs/rf30_round1_head_on_keep_line`). The extractor pools their **design** sessions, as
  `analysis.gate --with` does: the first run of each cell, and no counterfactual pair, so that no
  cell counts twice. A session found in two sources is refused.
- **Resolved** means resolved physically in the `plan_only` replay (RF-4): both left the
  conflict zone, with no collision, no near miss and no deadlock, within the time limit
  (`resolved_plan_only`). Only completed sessions count.
- **The gate.** An encounter type is extracted only if it passed the resolution gate its
  experiments fixed before their runs (`resolution_gate` in each `config.json`; all must be
  equal). The gate is recomputed over the pooled design sessions. A type that fails it is
  skipped, and the report says so. A mock rehearsal of sources that fixed no gate may go on with
  `gate.require: false`; a paid run may not.
- **The rule is extracted from resolved sessions only.** The failed ones are shown separately
  (section 3), so that a rule can say where it does not hold.

## 2. The held-out split

Before anything is shown to the extractor, a seeded 25% of the type's resolved sessions is set
aside (`held_out.share`, `held_out.seed`). The split is by session, so both people of a held-out
session are held out. The extractor never sees them: neither in the table nor in the sample.
They are used for one thing only, the fidelity score (section 6).

## 3. What the extractor is shown

One system message (the role, the task in the order of the issue's task 3, the predict format and
the reply format, all fixed text) and one user message:

- **The main table**: one row per agent per resolved session, in words, with the columns
  `extract_v1` describes:
  - the condition, geometry and person;
  - each person's own factors;
  - **the other person's factors only as the agent was told them**, RF-8's rule
    (`analysis/load.py`): the other's age and gender when shown, an observable factor's marked
    level when its switch is on and it was shown (else `not_seen`), the other's group when shown
    (else `not_told`), and the pairwise lines when shown;
  - the situation;
  - the agent's own decisions: decision points, the distance at its first decision, the first
    plan's side, slowing, stopping and backing up, its start distance, the last plan's side,
    whether it signalled or spoke, and its debrief kind;
  - the measured outcome in `plan_only`: who passed first, the passing side, stopped, backed up;
  - `cell_stability`: `coin_flip` for a cell of the exact-repeat set whose commonest behaviour
    came up in fewer than 3 in 4 of its repeats (RF-8's rule, `analysis/noise.py`), `stable`, or
    `untested`.

  A table of one row per agent, not per session, because a rule such as "keep right" is about
  what each person does, and the other's factors are as each one was told them.
- **The failed sessions**, counted by condition, geometry, the first sides of the two plans, and
  what went wrong (collision, deadlock, near miss, not cleared, in that order). With 16 factors
  almost every failed session is its own factor combination, so they are not counted per full
  combination. A second table gives, for each level of each design factor that varies, how many
  sessions resolved and how many failed.
- **The coin-flip cells**, as a count, with the rows marked in the table.
- **10 to 20 resolved sessions in full** (`sample.size`): each decision point's distance, why it
  fired (without the agent numbers, which are not the table's persons), intent, steps, signal,
  message and private reason, and each person's debrief. The sample covers each outcome and
  condition first: the strata are the condition and the two passing sides, one session of each
  in an order the run's seed shuffles, and the rest at random.

The encounter is described by the config's `encounter_descriptions` (one line per type), so the
template names no scenario (D16).

## 4. What the extractor writes

A YAML block with a list `rules`. Each rule has:

| Field | Contents |
| --- | --- |
| `rule`, `applies_when`, `action` | the rule; its concrete condition; its concrete action, with when it starts and how much |
| `exceptions` | where it does not hold, including from the failed sessions |
| `factors_used` | column names |
| `needs_communication` | true if it held only when a signal or a message was used |
| `references` | each `citation`, `locator`, `kind`, `claim`; or `no known source` |
| `debrief_support` | the share of the rule's sessions whose debriefs give the same basis, and a note |
| `coverage` | which rows it describes |
| `predict` | a decision list over the table's own columns: `target`, `if` (each a `when` and a `then`), `default` |

`predict` may read only the situation, each person's factors, when the agent decided, and whether
it signalled or spoke (`table.CONDITION_COLUMNS`), never its own target. It may predict an agent's
first or last side, slowing, stopping, backing up, signalling, speaking, or the measured outcome
(`table.TARGETS`). A `when` is a conjunction; a list means "one of"; `{">=": 60}` compares a
number column.

An unreadable reply is asked again once (`retry` of the template); a second unreadable reply makes
the run `unreadable`.

## 5. The checks

In this order (`negsim/extraction/rules.py`; the categories are `negsim.rulegen.validate`'s):

1. **`protected_attribute`**: the rule reads a person's ethnicity or perceived attractiveness, in
   `predict` (`own_ethnicity`, `other_ethnicity`, `finds_other_attractive`), in `factors_used`, or
   in its own words (`ethnic`, `attract`, `beaut`, `handsome`, "good looking", the group names;
   "pretty" alone is not taken for attractiveness in prose). It is kept in the run's record and
   counted, **never stored as a rule and never passed to RF-12**. The screen (RF-10) measures such
   a bias; no rule may apply it.
2. **`schema_error`**: a field is missing or malformed, or `predict` cannot be evaluated.
3. **`needs_communication`**: otherwise valid, but it says it needs communication, or `predict`
   reads `signalled` or `spoke` (D9). Stored and tagged.
4. **`valid`**.

## 6. Fidelity

`predict` is applied mechanically to the held-out rows whose target is known, and its accuracy is
reported against the **majority-class baseline**: always predicting the main table's commonest
value of the target. The same accuracy on the main table is reported as in-sample fit. Fidelity
says whether the rule describes the LLM agents' behaviour. Whether it describes people is RF-14's
question.

The code also counts, for the main-table rows the rule predicts rightly, the debrief kinds the
agents gave (`measured.debrief_kinds_where_it_holds`), beside the extractor's own
`debrief_support`.

## 7. Three runs, and which rules are kept

One extraction is one random sample (temperature 1.0, no seed), so it is made **three times**
(`runs.seeds`), each with its own seeded sample of sessions shown in full; the tables are the
same.

- **Matching:** two rules from different runs match when they predict the same target and decide
  alike on at least `matching.agreement_min` of the main table's rows (95%, `[placeholder]`, the
  issue's). Rules are grouped in run order: a rule joins the first group whose first rule it
  matches and that has no rule of its run yet.
- **Keeping:** a group found in at least `matching.min_runs` (2) of the 3 runs is a
  `candidate`, with its `extraction_stability` (2/3 or 3/3). A group found once is stored as
  `unstable`, and not passed to RF-12.

## 8. What is stored

Under `runs/<experiment>/` (`runs_mock/` for the mock):

```
config.json, invocations.jsonl, preview.json   the config, the sources (with each outcomes.csv's SHA-256), the template; each invocation; the worst case
summary.json, report.md
<type>/split.json                             the gate, the main, held-out and failed session ids, the labels (S001...), the coin-flip cells
<type>/tables/main.csv, held_out.csv, failed.csv, factors.csv
<type>/runs/run_<k>.json                      the exact messages, every attempt's raw reply, model, fingerprint, tokens and cost;
                                              each rule as written, its category, predict and fidelity
<type>/rules.json                             the groups across the runs, and every category counted
<type>/extracted_rules/MANIFEST.json, rules/<rule_id>.v1.yaml
```

A run's record is written once, when the run ends, and never rewritten: running the experiment
again reuses it, and redoes only a run that was aborted (set aside as `run_<k>.aborted<n>.json`).
Once a run has a record, a different config, client or source data is refused, except the budget,
which changes nothing that is sent. The rules are matched once every run has a record.

The rule files are laid out as the writer's staging databases are (`negsim.rulegen.writer`:
write-once files, each frozen with its SHA-256 in a manifest), but they are not a rule database:
these rules are not in a rule format yet (RF-12 translates them), so nothing checks them against
the rule schemas. Each holds the representative rule as the extractor wrote it, and the code's
own fields: `rule_id` (`x_<type>_` and a hash), `status`, `category`, `extraction_stability`,
`measured` (fidelity, debrief kinds, the matching rules of the other runs), and `provenance`: the
experiment, the model and template, the sources, the session ids used, the held-out ids, the
failed sessions shown, each run's sample, and the references and debrief sources marked
`unchecked` (RF-14 checks them).

## 9. Money

Each run is one call (two if the reply must be asked again). `--plan` gives the worst case:
peak prices, nothing cached, every reply at the full allowance, every retry taken. A paid run
needs `--confirm`, the resolution gate, and the ethics sign-offs of what its table shows (the
table holds each person's ethnicity and perceived attractiveness, which the extractor sees and no
rule may read). Every call goes through the budget guard on the experiment's own calls. A worst
case above the cap does not stop a confirmed run from starting (as the resolution layer's
`budget.over_cap: stop_at_cap`): the guard refuses any call that could take the experiment's
recorded spend past the cap, and the run it belongs to is recorded as aborted and redone by a
rerun.
