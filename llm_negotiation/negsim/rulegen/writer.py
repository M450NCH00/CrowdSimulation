"""The rule writer and the staging databases (issue #30, Part 8; ``docs/rule-generation.md``).

**The rule database stays read-only.** Generated rules are written into a *staging*
database of their experiment, ``runs/<experiment>/rule_db_staging/<condition>/``, never into
``rule_db/``. A staging database is laid out as the rule database is (``schema/``, both rule
schemas copied in; ``rules/``; ``rulesets/``; ``MANIFEST.json``), so that it loads with the
same code and its rules can be switched on in a run.

The writer, and only the writer, fills a rule's metadata:

* ``rule_id`` from the condition, the case and the canonical hash: ``neg_`` or ``st_``, the
  case id, and the first ten hexadecimal characters of the hash;
* ``schema_version`` 2, ``version`` 1, ``status`` ``candidate``;
* ``provenance``: the source type (``negotiated`` or ``stated``), the experiment and the case,
  the model and the prompt template, and every session that produced the rule, each with its
  design cell and its time.

Anything a model wrote in those keys is ignored, and logged with its proposal
(``negsim.rulegen.validate``): a model's output is never trusted as provenance. The same
canonical rule from several sessions of one case and condition is stored once, with every
supporting session listed. The canonical form leaves out ``description``, ``intent`` and
``priority`` (``docs/rule-format.md``, section 13), so sessions that agree on what a rule does
may word it differently: the stored rule takes them from the **earliest** supporting session
(by start time, then id), and each session's own proposal stays in its session log.

Writing is **idempotent**, so that an experiment can be run again or resumed: a rule already
stored with the same sessions is left alone; one that more sessions now support is stored again
as its next version, with the sessions added and its screening results kept.

**Promotion** into ``rule_db/`` is never automatic. :func:`promote` (``python -m negsim.rulegen
promote``) copies one staged rule version into a rule database as its next version, only
with a reason, which it records in the rule's provenance. No rule is promoted in issue #30.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import yaml

from ..configutil import ConfigError, PACKAGE_ROOT
from ..rules.database import MANIFEST_FILE, RULE_DB_ROOT, RULE_FILE, RuleDatabase, file_sha256, load_validator, read_rule_file, schema_path
from ..rules.model import SCHEMA_VERSIONS, Rule
from .design import CONDITION_NEGOTIATED, CONDITION_STATED

STAGING_DIR = "rule_db_staging"
ID_PREFIX = {CONDITION_NEGOTIATED: "neg", CONDITION_STATED: "st"}
HASH_CHARACTERS_IN_ID = 10


class WriterError(ConfigError):
    """A rule that cannot be written, or promoted."""


def rule_id_for(condition: str, case_id: str, canonical_hash: str) -> str:
    """The id the writer gives a generated rule: deterministic, never the model's."""
    return f"{ID_PREFIX[condition]}_{case_id}_{canonical_hash[:HASH_CHARACTERS_IN_ID]}"


def rule_yaml(rule: Mapping[str, Any]) -> str:
    return yaml.safe_dump(dict(rule), sort_keys=False, allow_unicode=True, width=100)


class StagingDatabase:
    """A rule database that only the writer writes to, and only ever adds to."""

    def __init__(self, root: Path | str):
        self.root = Path(root)

    @property
    def manifest_path(self) -> Path:
        return self.root / MANIFEST_FILE

    def create(self) -> None:
        """Lay the database out, with both rule schemas copied in and frozen. Idempotent."""
        (self.root / "rules").mkdir(parents=True, exist_ok=True)
        (self.root / "rulesets").mkdir(parents=True, exist_ok=True)
        (self.root / "schema").mkdir(parents=True, exist_ok=True)
        manifest = self.manifest()
        for version in SCHEMA_VERSIONS:
            name = schema_path(version)
            target = self.root / name
            if not target.is_file():
                shutil.copyfile(RULE_DB_ROOT / name, target)
            if name not in manifest["files"]:
                manifest["files"][name] = {"sha256": file_sha256(target), "frozen_on": date.today().isoformat(), "note": "Copied from rule_db/."}
        self._write_manifest(manifest)

    def manifest(self) -> dict[str, Any]:
        if self.manifest_path.is_file():
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return {
            "about": (
                "A staging rule database of a rule-generation experiment (issue #30): generated rules, status "
                "candidate, written by negsim.rulegen.writer only. SHA-256 of every file, line endings normalised "
                "to LF; a file is frozen once listed, and a change is the next version. Nothing here is in rule_db/ "
                "unless it is promoted, with a reason."
            ),
            "files": {},
        }

    def _write_manifest(self, manifest: Mapping[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        files = dict(manifest["files"])
        ordered = {name: files[name] for name in sorted(files, key=lambda name: (not name.startswith("schema/"), name))}
        self.manifest_path.write_text(
            json.dumps({**manifest, "files": ordered}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
        )

    def write(self, rule: Mapping[str, Any], note: str) -> tuple[str, bool]:
        """Freeze a rule version. The same content again writes nothing; other content under a
        frozen name is refused."""
        name = f"rules/{rule['rule_id']}.v{rule['version']}.yaml"
        path = self.root / name
        text = rule_yaml(rule)
        manifest = self.manifest()
        if name in manifest["files"] or path.is_file():
            if path.is_file() and path.read_text(encoding="utf-8").replace("\r\n", "\n") == text:
                return name, False
            raise WriterError(f"{name} is frozen with other contents; a change is the next version, never an edit")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        manifest["files"][name] = {"sha256": file_sha256(path), "frozen_on": date.today().isoformat(), "note": note}
        self._write_manifest(manifest)
        return name, True

    def copy_in(self, source: Path | str, note: str) -> tuple[str, bool]:
        """Freeze a copy of a rule file frozen in another database (issue #74): the same text,
        line endings LF, under the same name. The same text again writes nothing; other text
        under a frozen name is refused."""
        source = Path(source)
        name = f"rules/{source.name}"
        path = self.root / name
        text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
        manifest = self.manifest()
        if name in manifest["files"] or path.is_file():
            if path.is_file() and path.read_text(encoding="utf-8").replace("\r\n", "\n") == text:
                return name, False
            raise WriterError(f"{name} is frozen with other contents; a change is the next version, never an edit")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        manifest["files"][name] = {"sha256": file_sha256(path), "frozen_on": date.today().isoformat(), "note": note}
        self._write_manifest(manifest)
        return name, True

    def write_ruleset(self, name: str, rules: Mapping[str, int], description: str) -> tuple[str, bool]:
        """Freeze a named rule set (issue #74), as ``rule_db/rulesets/`` holds them. The same set
        again writes nothing; another set under a frozen name is refused."""
        relative = f"rulesets/{name}.yaml"
        path = self.root / relative
        text = yaml.safe_dump({"name": name, "description": description, "rules": dict(rules)}, sort_keys=False, allow_unicode=True, width=100)
        manifest = self.manifest()
        if relative in manifest["files"] or path.is_file():
            if path.is_file() and path.read_text(encoding="utf-8").replace("\r\n", "\n") == text:
                return relative, False
            raise WriterError(f"{relative} is frozen with another set; a different set is a new file with a new name")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        manifest["files"][relative] = {"sha256": file_sha256(path), "frozen_on": date.today().isoformat(), "note": "a rule set of RF-18 (issue #74)"}
        self._write_manifest(manifest)
        return relative, True

    def load(self) -> RuleDatabase:
        return RuleDatabase.load(self.root)

    def latest(self, rule_id: str) -> Optional[Rule]:
        """The newest version of a rule, or ``None`` if the database has none.

        Read on its own, checked against the manifest, rather than by loading the whole
        database, whose check of every pair of rules for clashes grows with the square of their
        number and is not needed to find one rule.
        """
        if not self.manifest_path.is_file():
            return None
        files = self.manifest()["files"]
        versions = sorted(
            int(found["version"])
            for name in files
            if name.startswith("rules/") and (found := RULE_FILE.match(name[len("rules/"):])) and found["rule_id"] == rule_id
        )
        if not versions:
            return None
        name = f"rules/{rule_id}.v{versions[-1]}.yaml"
        if file_sha256(self.root / name) != files[name]["sha256"]:
            raise WriterError(f"{self.root / name}: its contents are not the version frozen in the staging manifest")
        return read_rule_file(self.root / name, load_validator(self.root), self.root)

    def stage(self, rule: Mapping[str, Any], note: str) -> tuple[str, int, bool]:
        """Store a generated rule (``build_rule``) idempotently.

        New: as version 1. Stored already with the same sessions: nothing. Now supported by
        more sessions: as the next version, with every session and the screening results of the
        version before. Returns the file holding the rule now, its version, and whether anything
        was written.
        """
        latest = self.latest(rule["rule_id"])
        if latest is None:
            name, written = self.write(rule, note)
            return name, rule["version"], written
        sessions = lambda written: {entry["session_id"] for entry in written["provenance"]["generation"]["sessions"]}  # noqa: E731
        before, now = sessions(latest.written), sessions(rule)
        if now == before:
            return latest.source, latest.version, False
        if not before <= now:
            raise WriterError(
                f"{latest.key} was supported by sessions {sorted(before - now)} that no longer support it: the session "
                "logs changed under the staging database"
            )
        newer = json.loads(json.dumps(dict(rule)))
        newer["version"] = latest.version + 1
        if latest.screening:
            newer["screening"] = [dict(entry) for entry in latest.screening]
        newer["provenance"]["notes"] += (
            f" Version {newer['version']} adds {len(now - before)} supporting session(s) to version {latest.version}."
        )
        name, written = self.write(newer, f"{note}; {len(now - before)} session(s) added")
        return name, newer["version"], written


@dataclass(frozen=True)
class Support:
    """One session that produced a rule: what the provenance records of it, and the rule as
    that session's model wrote it (``proposal``, not recorded in the provenance)."""

    session_id: str
    design_cell: Mapping[str, Any]
    model: str
    model_returned: Optional[str]
    prompt_template: Mapping[str, Any]
    created_utc: str
    proposed_by: Optional[int] = None
    repeat: Optional[int] = None
    proposal: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "design_cell": dict(self.design_cell),
            "model": self.model,
            "model_returned": self.model_returned,
            "prompt_template": dict(self.prompt_template),
            "created_utc": self.created_utc,
            "proposed_by": self.proposed_by,
            "repeat": self.repeat,
        }


def build_rule(
    condition: str,
    case_id: str,
    canonical_hash: str,
    supports: Sequence[Support],
    experiment: str,
    schema_version: int = 2,
) -> dict[str, Any]:
    """The rule file the writer stores for a valid proposal: the model's body, from the
    earliest supporting session, and the writer's metadata. ``schema_version`` is the version of
    the rule format the sessions were shown, which the rule was checked in: 2 for issue #30's
    prompts, 3 for issue #32's."""
    if not supports:
        raise WriterError("a generated rule needs at least one session that produced it")
    supports = sorted(supports, key=lambda support: (support.created_utc, support.session_id))
    first = supports[0]
    proposal = first.proposal
    # The model that replied, as its API named it; the one asked for if no reply named one.
    models = sorted({support.model_returned or support.model for support in supports})
    template = first.prompt_template.get("key", "?")
    rule: dict[str, Any] = {
        "schema_version": schema_version,
        "rule_id": rule_id_for(condition, case_id, canonical_hash),
        "version": 1,
        "status": "candidate",
    }
    if "description" in proposal:
        rule["description"] = proposal["description"]
    if "intent" in proposal:
        rule["intent"] = proposal["intent"]
    rule["provenance"] = {
        "source_type": condition,
        "source_ref": f"rule-generation experiment {experiment}, case {case_id}, {len(supports)} session(s)",
        "created_at": first.created_utc[:10],
        "author": f"negsim.rulegen.writer, from {', '.join(models)} with prompt template {template}",
        "notes": (
            "Generated by a language model in issue #30's rule generation and written by the writer: its id and "
            "provenance are the writer's, never the model's. A candidate, not checked against evidence about people."
        ),
        "validation_evidence": [],
        "generation": {
            "experiment": experiment,
            "condition": condition,
            "case_id": case_id,
            "canonical_hash": canonical_hash,
            "sessions": [support.as_dict() for support in supports],
        },
    }
    for key in ("encounter", "when", "roles", "directive", "priority", "expiry"):
        if key in proposal:
            rule[key] = proposal[key]
    return rule


def with_screening(rule: Mapping[str, Any], entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The next version of a staged rule, with the results of replaying and screening it."""
    newer = json.loads(json.dumps(dict(rule)))
    newer["version"] = rule["version"] + 1
    newer["screening"] = [*rule.get("screening", []), *[dict(entry) for entry in entries]]
    newer["provenance"]["notes"] = (
        rule["provenance"]["notes"] + f" Version {newer['version']} adds the results of replaying and screening the rule; "
        "what the rule does is unchanged."
    )
    return newer


# --- promotion ----------------------------------------------------------------------------------


def promote(
    staging_root: Path | str,
    rule_id: str,
    reason: str,
    version: Optional[int] = None,
    database_root: Path | str = RULE_DB_ROOT,
    by: str = "a person, with negsim.rulegen promote",
) -> Path:
    """Copy one staged rule version into a rule database as that rule's next version.

    Refused without a reason. The copy records where it came from, the SHA-256 of the staged
    file, the reason and when, in ``provenance.promotion``; it is frozen in the database's
    manifest, and the database must still load afterwards.
    """
    if not isinstance(reason, str) or not reason.strip():
        raise WriterError("a promotion needs a reason: say why this rule should leave the staging database")
    staging = StagingDatabase(staging_root)
    staged = staging.load()
    versions = [rule for rule in staged.rules if rule.rule_id == rule_id]
    if not versions:
        raise WriterError(f"no rule {rule_id!r} in the staging database {staging_root}")
    chosen = versions[-1] if version is None else next((rule for rule in versions if rule.version == version), None)
    if chosen is None:
        raise WriterError(f"{rule_id} has versions {[rule.version for rule in versions]} in {staging_root}, not {version}")
    target_root = Path(database_root)
    target = RuleDatabase.load(target_root)
    next_version = 1 + max((rule.version for rule in target.rules if rule.rule_id == rule_id), default=0)
    source = Path(staging_root)
    try:
        where = source.resolve().relative_to(PACKAGE_ROOT).as_posix()
    except ValueError:
        where = source.as_posix()
    promoted = json.loads(json.dumps(dict(chosen.written)))
    promoted["version"] = next_version
    promoted["provenance"]["promotion"] = {
        "from_database": where,
        "staged_rule": chosen.key,
        "staged_sha256": chosen.sha256,
        "reason": " ".join(reason.split()),
        "promoted_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "by": by,
    }
    name = f"rules/{rule_id}.v{next_version}.yaml"
    path = target_root / name
    manifest_path = target_root / MANIFEST_FILE
    before = manifest_path.read_text(encoding="utf-8")
    path.write_text(rule_yaml(promoted), encoding="utf-8", newline="\n")
    manifest = json.loads(before)
    manifest["files"][name] = {
        "sha256": file_sha256(path),
        "frozen_on": date.today().isoformat(),
        "note": f"Promoted from {where} ({chosen.key}): {' '.join(reason.split())}",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    try:
        RuleDatabase.load(target_root)  # the database must still load
    except ConfigError:
        path.unlink()
        manifest_path.write_text(before, encoding="utf-8", newline="\n")
        raise
    return path
