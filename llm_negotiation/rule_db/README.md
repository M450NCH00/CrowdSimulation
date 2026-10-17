# The rule database (issue #28)

The rules the `RuleDatabaseProvider` follows (`negsim/rules/`). The format is in
`docs/rule-format.md`, the matching policy in `docs/rule-matching.md`.

```
schema/rule.v1.schema.json       the rule format, version 1 (JSON Schema)
schema/rule.v2.schema.json       version 2 (issue #30): rules a model generates
schema/rule.v3.schema.json       version 3 (issue #32): backing out of a single-file passage
rules/<rule_id>.v<n>.yaml        one file per version of each rule
rulesets/<name>.yaml             named sets of rule versions an experiment can switch on
MANIFEST.json                    SHA-256 of every file above: what is frozen
```

**Every rule here is a `test_seed`**: written to exercise the machinery, and not a claim
about how people behave. Checking rules against human evidence is the validation
sub-issue's (SI-6). Test fixtures, including deliberately invalid rules, live in
`tests/fixtures/rules/`, never here.

**A version is never edited.** Each file's SHA-256 (with line endings normalised to LF) is
frozen in `MANIFEST.json`, and loading refuses a file that does not match or is not listed.
A changed rule, including a changed status or added validation evidence, is a new file with
the next version number, and the old one stays. There is no tool that writes here yet:
issue #28 keeps the command line read-only. Until one exists (it will be needed by SI-3),
adding a version means writing the file, computing its hash with
`negsim.rules.database.file_sha256`, adding the entry to `MANIFEST.json`, and checking with
`python ruledb.py validate`.

Read it from `llm_negotiation/`:

```
python ruledb.py list                          every version, its status, and the rule sets
python ruledb.py validate                      load and check everything; exit 1 if anything is refused
python ruledb.py validate --file PATH ...      check rule files that are not in the database
python ruledb.py history keep_left_head_on     every version of a rule and what changed
python ruledb.py show younger_yields_head_on   one version as written
```

The six seed rules: `keep_left_head_on`, `keep_right_head_on` (its mirror image, not in the
`default` rule set: the two cannot be switched on together), `overtaker_keeps_clear`,
`single_file_first_arrival`, `younger_yields_head_on` (the issue's example rule), and, from
issue #32, `passage_shorter_backs_out` (schema version 3, not in the `default` rule set: of
two people who meet inside a single-file passage, the one who has walked less far in backs
out; `docs/rule-format.md`, section 14).
