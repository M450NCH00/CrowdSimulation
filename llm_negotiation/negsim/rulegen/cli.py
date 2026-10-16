"""The command line of rule generation's staging databases (issue #30, Part 8).

    python -m negsim.rulegen list runs/si3_pilot/rule_db_staging/negotiated
    python -m negsim.rulegen promote runs/si3_pilot/rule_db_staging/negotiated RULE_ID --reason "why"

``list`` shows what a staging database holds. ``promote`` copies one staged rule version into
the rule database (``rule_db/`` unless ``--database`` names another) as that rule's next
version, and refuses without a reason; the reason is recorded in the rule's provenance.
Nothing promotes a rule automatically, and no rule is promoted in issue #30.

(Running an experiment is ``run_experiment.py``'s; cases have ``python -m negsim.rulegen.cases``.)
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional, TextIO

from ..configutil import ConfigError, resolve_path
from ..rules.database import RULE_DB_ROOT
from .writer import StagingDatabase, promote


def main(argv: Optional[list[str]] = None, out: Optional[TextIO] = None) -> int:
    out = out or sys.stdout
    parser = argparse.ArgumentParser(prog="negsim.rulegen", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="the rules of a staging database")
    listing.add_argument("staging", help="the staging database folder, e.g. runs/<experiment>/rule_db_staging/negotiated")
    lift = commands.add_parser("promote", help="copy a staged rule into the rule database, with a reason")
    lift.add_argument("staging", help="the staging database folder")
    lift.add_argument("rule_id")
    lift.add_argument("--reason", required=True, help="why this rule should leave the staging database (required)")
    lift.add_argument("--version", type=int, help="the staged version to promote (default: the newest)")
    lift.add_argument("--database", default=str(RULE_DB_ROOT), help="the rule database to promote into (default: rule_db)")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            database = StagingDatabase(resolve_path(args.staging)).load()
            for rule in database.rules:
                generation = rule.provenance.get("generation", {})
                verdicts = ", ".join(f"{item['kind']} {item['verdict']}" for item in rule.screening) or "not screened"
                print(f"{rule.key:48} {rule.provenance['source_type']:10} {len(generation.get('sessions', []))} session(s); {verdicts}", file=out)
        else:
            path = promote(resolve_path(args.staging), args.rule_id, args.reason, args.version, resolve_path(args.database))
            print(f"promoted: {path}", file=out)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
