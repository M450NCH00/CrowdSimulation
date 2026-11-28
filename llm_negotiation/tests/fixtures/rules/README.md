# Rule fixtures (issue #28)

Test fixtures for `tests/test_rules_format.py` and `tests/test_rules_database.py`. They are
kept here, never in `rule_db/`, and nothing in a run reads them.

- `valid/`: rules that load. `gender_keeps_clear_crossing` is the rule with a gender
  condition the issue asks for; `every_operator` uses every operator, group and unit.
- `invalid/`: rules that are refused. The first line of each says which category of
  refusal it must get (`# expect: <category>`, `negsim/rules/errors.py`).
- `ambiguous/`: two rules that each load, but that match the same pair at the same
  priority with different directives, so that switching both on is refused.
