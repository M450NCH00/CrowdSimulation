"""The rule database's command line. Read-only: it lists, checks and shows, and writes nothing.

    python ruledb.py list                       every rule version, and the rule sets
    python ruledb.py validate                   load and check the whole database
    python ruledb.py validate --file PATH ...   check rule files outside it (a fixture, a candidate)
    python ruledb.py history RULE_ID            every version of a rule, and what changed
    python ruledb.py show RULE_ID [--version N] a rule version as written

(``python -m negsim.rules`` is the same.) ``--db PATH`` reads another database folder.
Exit status: 0 when everything checked out, 1 when something was refused or not found.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from ..configutil import ConfigError, resolve_path
from .database import RULE_DB_ROOT, RuleDatabase, load_validator, read_rule_file
from .errors import RuleError
from .model import Rule

#: Fields of a rule that ``history`` compares between consecutive versions.
COMPARED = (
    "schema_version", "status", "description", "intent", "provenance", "encounter", "when", "roles", "directive",
    "priority", "expiry", "screening",
)


def main(argv: Optional[list[str]] = None, out: Optional[TextIO] = None, err: Optional[TextIO] = None) -> int:
    out, err = out or sys.stdout, err or sys.stderr
    parser = argparse.ArgumentParser(prog="ruledb", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=str(RULE_DB_ROOT), help="the rule database folder (default: rule_db)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="every rule version, and the rule sets")
    check = commands.add_parser("validate", help="load and check the database, or the files given")
    check.add_argument("--file", nargs="+", type=Path, help="rule files to check on their own")
    history = commands.add_parser("history", help="every version of one rule")
    history.add_argument("rule_id")
    show = commands.add_parser("show", help="one rule version as written")
    show.add_argument("rule_id")
    show.add_argument("--version", type=int, help="default: the latest")
    args = parser.parse_args(argv)
    root = resolve_path(args.db)

    if args.command == "validate":
        return _validate(root, args.file, out)
    try:
        database = RuleDatabase.load(root)
    except ConfigError as exc:
        print(f"the rule database did not load; run 'validate' for the details\n{exc}", file=err)
        return 1
    try:
        if args.command == "list":
            _list(database, out)
        elif args.command == "history":
            _history(database, args.rule_id, out)
        else:
            versions = database.history(args.rule_id)
            rule = versions[-1] if args.version is None else database.get(args.rule_id, args.version)
            out.write((database.root / rule.source).read_text(encoding="utf-8"))
    except RuleError as exc:
        print(exc, file=err)
        return 1
    return 0


def _list(database: RuleDatabase, out: TextIO) -> None:
    sets: dict[tuple[str, int], list[str]] = {}
    for name, ruleset in sorted(database.rulesets.items()):
        for rule_id, version in ruleset.rules.items():
            sets.setdefault((rule_id, version), []).append(name)
    print(f"{'rule':34} {'status':10} {'encounter':20} {'priority':>8} {'expiry':12} {'source':12} {'created':10} rule sets", file=out)
    for rule in database.rules:
        provenance = rule.provenance
        print(
            f"{rule.key:34} {rule.status:10} {rule.encounter:20} {rule.priority:>8} {rule.expiry:12} "
            f"{provenance['source_type']:12} {provenance['created_at']:10} "
            f"{', '.join(sets.get((rule.rule_id, rule.version), [])) or '-'}",
            file=out,
        )
    print(file=out)
    for name, ruleset in sorted(database.rulesets.items()):
        enabled = ", ".join(f"{rule_id}@{version}" for rule_id, version in sorted(ruleset.rules.items()))
        print(f"rule set {name}: {enabled}", file=out)
    for clash in database.report.clashes:
        print(f"cannot be switched on together: {clash.describe()}", file=out)


def _validate(root: Path, files: Optional[list[Path]], out: TextIO) -> int:
    if files:
        validator = load_validator(root)
        failures = 0
        for path in files:
            try:
                rule = read_rule_file(path, validator)
                print(f"OK       {path}: {rule.key}, {rule.encounter}, priority {rule.priority}", file=out)
            except RuleError as exc:
                failures += 1
                print(f"REFUSED  {path}: [{exc.category}] {exc.args[0]}", file=out)
        return 1 if failures else 0
    database = RuleDatabase.load(root, strict=False)
    for line in database.report.lines():
        print(line, file=out)
    return 1 if database.report.refused else 0


def _history(database: RuleDatabase, rule_id: str, out: TextIO) -> None:
    previous: Optional[Rule] = None
    for rule in database.history(rule_id):
        provenance = rule.provenance
        print(f"{rule.key}  status {rule.status}  created {provenance['created_at']}  by {provenance['author']}", file=out)
        print(f"    source: {provenance['source_type']}, {provenance['source_ref']}", file=out)
        print(f"    file: {rule.source}  sha256 {rule.sha256}", file=out)
        if provenance.get("notes"):
            print(f"    notes: {' '.join(str(provenance['notes']).split())}", file=out)
        print(f"    validation evidence: {len(provenance.get('validation_evidence') or [])} item(s)", file=out)
        if previous is not None:
            changed = [key for key in COMPARED if previous.written.get(key) != rule.written.get(key)]
            print(f"    changed from version {previous.version}: {', '.join(changed) or 'nothing'}", file=out)
        previous = rule


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
