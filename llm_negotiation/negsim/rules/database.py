"""The rule database: rule files on disk, frozen per version, and the rule sets experiments use.

Layout (``llm_negotiation/rule_db/``)::

    MANIFEST.json                    SHA-256 of every frozen file
    schema/rule.v1.schema.json       the rule format, version 1
    rules/<rule_id>.v<version>.yaml  one file per version of each rule
    rulesets/<name>.yaml             named sets of (rule, version) to switch on together

Why plain files: they can be read and diffed, and git keeps their history. Why a manifest
on top: **a rule version is never edited**. A change is a new file with the next version
number, and the old file stays. The manifest records the SHA-256 of every file when it is
frozen (line endings normalised to LF, as for the prompt templates, so that a Windows
checkout hashes the same); loading refuses a file whose contents no longer match, and a
file the manifest does not list. A rule's status changing, or evidence being added by the
validation sub-issue, is a new version like any other change.

On load every rule file is read, checked against the schema and the rest of the format
(``model.py``), and either kept or refused with its reason. Refused files are reported,
not dropped silently; by default a database with any refusal does not load at all.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT, ConfigError, load_yaml
from .ambiguity import RULE_CLASSES, Clash, clashes
from .errors import RuleError
from .jsonschema_subset import Validator
from .model import SCHEMA_VERSION, USABLE_STATUSES, Rule, parse_rule

RULE_DB_ROOT = PACKAGE_ROOT / "rule_db"
MANIFEST_FILE = "MANIFEST.json"
SCHEMA_PATH = f"schema/rule.v{SCHEMA_VERSION}.schema.json"
RULE_FILE = re.compile(r"^(?P<rule_id>[a-z][a-z0-9_]{2,63})\.v(?P<version>[1-9][0-9]*)\.yaml$")
RULESET_KEYS = ("name", "description", "rules")


def file_sha256(path: Path) -> str:
    """SHA-256 of a text file with its line endings normalised to LF."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_validator(root: Path) -> Validator:
    path = root / SCHEMA_PATH
    if not path.is_file():
        raise ConfigError(f"the rule schema is missing: {path}")
    return Validator(json.loads(path.read_text(encoding="utf-8")))


def read_rule_file(path: Path, validator: Validator, root: Optional[Path] = None) -> Rule:
    """One rule file, checked against the format and against its own file name.

    The manifest is not consulted here (``RuleDatabase.load`` does that); this is also how
    a rule that is not in any database, such as a test fixture, is read.
    """
    where = path.relative_to(root).as_posix() if root is not None else path.name
    name = RULE_FILE.match(path.name)
    try:
        raw = load_yaml(path)
    except ConfigError as exc:
        raise RuleError("file", f"{where}: {exc}") from exc
    rule = parse_rule(raw, validator, where)
    if name is None or (name["rule_id"], int(name["version"])) != (rule.rule_id, rule.version):
        raise RuleError(
            "file",
            f"{where}: a rule file is named <rule_id>.v<version>.yaml after what it contains; this one holds "
            f"{rule.rule_id} version {rule.version}, so it should be {rule.rule_id}.v{rule.version}.yaml",
        )
    return replace(rule, source=where, sha256=file_sha256(path))


@dataclass(frozen=True)
class RuleSet:
    """A named set of rule versions to switch on together."""

    name: str
    description: str
    rules: Mapping[str, int]  # rule_id -> version


@dataclass
class LoadReport:
    """What a load of the database found."""

    loaded: list[Rule] = field(default_factory=list)
    refused: list[tuple[str, RuleError]] = field(default_factory=list)
    clashes: list[Clash] = field(default_factory=list)

    def lines(self) -> list[str]:
        out = [f"{len(self.loaded)} rule version(s) loaded, {len(self.refused)} refused"]
        by_class: dict[str, list[str]] = {}
        for rule in self.loaded:
            by_class.setdefault(rule.encounter, []).append(f"{rule.key} (priority {rule.priority}, {rule.status})")
        for encounter in sorted(by_class):
            out.append(f"  {encounter}: " + ", ".join(sorted(by_class[encounter])))
        for source, error in self.refused:
            out.append(f"  REFUSED {source}: [{error.category}] {error.args[0]}")
        for clash in self.clashes:
            out.append(f"  cannot be switched on together: {clash.describe()}")
        return out


class RuleDatabase:
    """Every rule version in the database, and its rule sets. Read-only."""

    def __init__(self, root: Path, rules: Sequence[Rule], rulesets: Mapping[str, RuleSet], report: LoadReport):
        self.root = root
        self.report = report
        self.rulesets = dict(rulesets)
        self._rules = {(rule.rule_id, rule.version): rule for rule in rules}

    @classmethod
    def load(cls, root: Path | str = RULE_DB_ROOT, strict: bool = True) -> "RuleDatabase":
        """Read and check every file. With ``strict`` (the default) any refusal is an error."""
        root = Path(root)
        validator = load_validator(root)
        report = LoadReport()
        manifest = _read_manifest(root)
        listed = dict(manifest)

        def frozen(path: Path) -> None:
            relative = path.relative_to(root).as_posix()
            entry = listed.pop(relative, None)
            if entry is None:
                raise RuleError("manifest", f"{relative}: not in {MANIFEST_FILE}; every file must be frozen there")
            if file_sha256(path) != entry["sha256"]:
                raise RuleError(
                    "manifest",
                    f"{relative}: its contents are not the version frozen in {MANIFEST_FILE}. A frozen file is never "
                    "edited: write the change as the next version, in a new file.",
                )

        try:
            frozen(root / SCHEMA_PATH)
        except RuleError as exc:
            report.refused.append((SCHEMA_PATH, exc))
        for path in sorted((root / "rules").glob("*.yaml")):
            source = path.relative_to(root).as_posix()
            try:
                frozen(path)
                report.loaded.append(read_rule_file(path, validator, root))
            except RuleError as exc:
                report.refused.append((source, exc))

        by_id: dict[str, list[int]] = {}
        for rule in report.loaded:
            by_id.setdefault(rule.rule_id, []).append(rule.version)
        for rule_id, versions in sorted(by_id.items()):
            if sorted(versions) != list(range(1, len(versions) + 1)):
                report.refused.append(
                    (f"rules/{rule_id}.v*.yaml", RuleError("history", f"{rule_id}: versions {sorted(versions)} do not run 1, 2, 3, ...; an old version is never removed"))
                )

        rulesets = {}
        for path in sorted((root / "rulesets").glob("*.yaml")):
            source = path.relative_to(root).as_posix()
            try:
                frozen(path)
                ruleset = _read_ruleset(path, source)
                rulesets[ruleset.name] = ruleset
            except RuleError as exc:
                report.refused.append((source, exc))
        for missing in sorted(listed):
            report.refused.append((missing, RuleError("manifest", f"{missing}: listed in {MANIFEST_FILE} but not found")))

        database = cls(root, report.loaded, rulesets, report)
        for name, ruleset in rulesets.items():
            try:
                ActiveRuleSet.build(database.resolve(ruleset.rules), name=name)
            except RuleError as exc:
                report.refused.append((f"rulesets/{name}.yaml", exc))
        usable = [rule for rule in report.loaded if rule.status in USABLE_STATUSES]
        latest = {}
        for rule in usable:
            if rule.rule_id not in latest or rule.version > latest[rule.rule_id].version:
                latest[rule.rule_id] = rule
        report.clashes = clashes(list(latest.values()))
        if strict and report.refused:
            raise ConfigError("the rule database did not load:\n" + "\n".join(report.lines()))
        return database

    # --- looking things up --------------------------------------------------------------------

    @property
    def rules(self) -> list[Rule]:
        return [self._rules[key] for key in sorted(self._rules)]

    def get(self, rule_id: str, version: int) -> Rule:
        try:
            return self._rules[(rule_id, version)]
        except KeyError:
            known = sorted(version for rid, version in self._rules if rid == rule_id)
            detail = f"versions {known}" if known else "no versions"
            raise RuleError("ruleset", f"rule {rule_id!r} version {version!r} is not in the database ({rule_id} has {detail})") from None

    def history(self, rule_id: str) -> list[Rule]:
        """Every version of a rule, oldest first."""
        versions = [rule for (rid, _), rule in sorted(self._rules.items()) if rid == rule_id]
        if not versions:
            raise RuleError("ruleset", f"rule {rule_id!r} is not in the database")
        return versions

    def resolve(self, wanted: Mapping[str, int]) -> list[Rule]:
        """The rule versions a set names, each checked to exist and to be usable."""
        rules = []
        for rule_id, version in sorted(wanted.items()):
            rule = self.get(rule_id, version)
            if rule.status not in USABLE_STATUSES:
                raise RuleError(
                    "status",
                    f"{rule.key} has status {rule.status!r}; only {list(USABLE_STATUSES)} may be switched on",
                )
            rules.append(rule)
        return rules

    def activate(
        self,
        ruleset: Optional[str] = None,
        enable: Optional[Mapping[str, int]] = None,
        disable: Iterable[str] = (),
    ) -> "ActiveRuleSet":
        """The rules one experiment switches on: a named set, then ``disable``, then ``enable``.

        Refused if two of them can clash (``ambiguity.py``).
        """
        wanted: dict[str, int] = {}
        if ruleset is not None:
            if ruleset not in self.rulesets:
                raise RuleError("ruleset", f"unknown rule set {ruleset!r}; known: {sorted(self.rulesets)}")
            wanted.update(self.rulesets[ruleset].rules)
        for rule_id in disable:
            if rule_id not in wanted:
                raise RuleError("ruleset", f"cannot disable {rule_id!r}: it is not switched on")
            del wanted[rule_id]
        for rule_id, version in (enable or {}).items():
            wanted[rule_id] = version
        return ActiveRuleSet.build(self.resolve(wanted), name=ruleset)


@dataclass(frozen=True)
class ActiveRuleSet:
    """The rules one run follows, indexed by encounter class.

    ``by_class`` maps each encounter class to the rules that can apply to it (its own and
    those written for ``any``), highest priority first and, within a priority, by
    ``rule_id``: the order in which ``matching.evaluate`` tries them.
    """

    name: Optional[str]
    rules: tuple[Rule, ...]
    by_class: Mapping[str, tuple[Rule, ...]]
    unchecked: tuple[Clash, ...] = ()

    @classmethod
    def build(cls, rules: Sequence[Rule], name: Optional[str] = None, check: bool = True) -> "ActiveRuleSet":
        """Index ``rules``; refuse them if two can clash (unless ``check`` is off, which only
        the tests of the run-time check use)."""
        found = clashes(rules) if check else []
        definite = [clash for clash in found if clash.checked]
        if definite:
            raise RuleError(
                "ambiguous",
                "these rules cannot be switched on together:\n  " + "\n  ".join(clash.describe() for clash in definite)
                + "\nGive one of each pair a different priority, or switch one off.",
            )
        order = sorted(rules, key=lambda rule: (-rule.priority, rule.rule_id, rule.version))
        by_class = {
            encounter: tuple(rule for rule in order if rule.encounter in (encounter, "any")) for encounter in RULE_CLASSES
        }
        return cls(name, tuple(order), by_class, tuple(clash for clash in found if not clash.checked))

    def candidates(self, encounter_class: Optional[str]) -> tuple[Rule, ...]:
        return self.by_class.get(encounter_class, ()) if encounter_class else ()

    def needs(self) -> set[str]:
        needed: set[str] = set()
        for rule in self.rules:
            needed.update(rule.needs())
        return needed

    def check_visibility(self, visibility: Mapping[str, bool]) -> None:
        """Refuse a run whose visibility settings hide a field one of its rules reads."""
        for rule in self.rules:
            hidden = sorted(name for name in rule.needs() if not visibility.get(name, False))
            if hidden:
                raise RuleError(
                    "visibility",
                    f"{rule.key} reads what this run's visibility settings hide ({hidden}); its agents could not "
                    "follow it. Switch the rule off, or make what it reads visible.",
                )

    def describe(self) -> list[dict[str, Any]]:
        return [rule.describe() for rule in sorted(self.rules, key=lambda rule: rule.rule_id)]


def _read_manifest(root: Path) -> dict[str, Mapping[str, Any]]:
    path = root / MANIFEST_FILE
    if not path.is_file():
        raise ConfigError(f"the rule database has no {MANIFEST_FILE}: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    files = data.get("files")
    if not isinstance(files, Mapping):
        raise ConfigError(f"{path}: expected a 'files' mapping")
    return {name: entry for name, entry in files.items()}


def _read_ruleset(path: Path, source: str) -> RuleSet:
    try:
        raw = load_yaml(path)
    except ConfigError as exc:
        raise RuleError("file", f"{source}: {exc}") from exc
    if not isinstance(raw, Mapping) or set(raw) - set(RULESET_KEYS) or "name" not in raw or "rules" not in raw:
        raise RuleError("ruleset", f"{source}: a rule set has 'name', 'rules' and optionally 'description'")
    if raw["name"] != path.stem:
        raise RuleError("ruleset", f"{source}: its name {raw['name']!r} must match its file name")
    rules = raw["rules"]
    if not isinstance(rules, Mapping) or not all(
        isinstance(version, int) and not isinstance(version, bool) and version >= 1 for version in rules.values()
    ):
        raise RuleError("ruleset", f"{source}: 'rules' maps each rule_id to the version switched on, e.g. keep_left_head_on: 1")
    return RuleSet(raw["name"], " ".join(str(raw.get("description", "")).split()), dict(rules))
