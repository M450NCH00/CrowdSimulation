"""The rule database's read-only command line (issue #28). Run from ``llm_negotiation/``:

    python ruledb.py list
    python ruledb.py validate
    python ruledb.py validate --file tests/fixtures/rules/invalid/*.yaml
    python ruledb.py history keep_left_head_on
    python ruledb.py show younger_yields_head_on

It lists, checks and shows; it never writes. See ``negsim/rules/cli.py``.
"""

from negsim.rules.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
