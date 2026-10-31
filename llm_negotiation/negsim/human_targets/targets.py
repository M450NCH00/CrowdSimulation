"""Human target files (issue #122, RF-37; ``docs/human-targets.md``).

A target file is a frozen file under ``configs/human_targets/`` that says what published studies
measured of people meeting head-on, and how close the simulation must come:

- ``tolerance``: the user's decision of 2026-10-30, fixed before any rule was measured. A **value**
  target (a mean and a reported SD) is met within one SD of the study's mean; a **direction** target
  (a finding with no reported spread) is judged on its direction only, by a named ``check``; two
  targets that disagree (``disagrees_with``) are shown side by side with no verdict.
- ``targets``: each names its ``source`` (under ``sources``), where in the source it comes from, how
  much of the source was read, the study's setting, and how the simulation's setting ``differs``.
- ``sides``: which side people pass on, by place. A parameter, not a target: for Singapore no study
  was found, so it is not judged.
- ``not_targets``: what was looked at and left out, with the reason.

Only measures and checks this module knows are accepted, so that a target file cannot name a
measure nothing computes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional

from ..configutil import PACKAGE_ROOT, ConfigError, as_choice, as_number, check_keys, load_yaml
from ..rules.database import file_sha256

TARGETS_DIR = PACKAGE_ROOT / "configs" / "human_targets"
VALUE, DIRECTION = "value", "direction"
KINDS = (VALUE, DIRECTION)
READ = ("full text", "abstract")
#: What the measures of ``negsim.human_targets.measures`` compute: per pair, per agent, or per crowd.
MEASURES = (
    "min_centre_distance_m", "turning_start_m", "speed_change_mps", "lateral_share", "passed_first",
    "lane_share_majority_side", "speed_by_density",
)
#: How a direction target is judged; each is defined in ``docs/human-targets.md``, section 3.
CHECKS = (
    "increases_with_speed", "no_speed_change", "speed_decreases", "giver_adapts_more", "not_predicted_by_traits",
    "younger_adapts_more", "segregated", "speed_decreases_with_density",
)
TOLERANCE = {"value": "within_1_sd", "no_spread": "direction_only", "disagreement": "report_no_verdict"}
APPLIES = ("pair_ages", "encounter", "roles_differ", "scenario")
SIDES = ("left", "right")


@dataclass(frozen=True)
class Target:
    id: str
    claim: str
    kind: str
    measure: str
    source: str
    where: str
    read: str
    setting: str
    differs: tuple[str, ...]
    applies: Mapping[str, Any] = field(default_factory=dict)
    value: Optional[float] = None
    sd: Optional[float] = None
    unit: Optional[str] = None
    check: Optional[str] = None
    reported: Mapping[str, Any] = field(default_factory=dict)
    disagrees_with: Optional[str] = None

    @property
    def band(self) -> Optional[tuple[float, float]]:
        """The interval a value target is met within: the study's mean +/- one SD."""
        if self.kind != VALUE:
            return None
        return round(self.value - self.sd, 6), round(self.value + self.sd, 6)

    @property
    def setting_differs(self) -> bool:
        return bool(self.differs)


@dataclass(frozen=True)
class TargetFile:
    name: str
    source: str        # the file, relative to the package when it is inside it
    sha256: str
    tolerance: Mapping[str, str]
    age_groups: Mapping[str, tuple[int, int]]
    targets: Mapping[str, Target]
    sides: Mapping[str, Any]
    not_targets: tuple[Mapping[str, str], ...]
    sources: Mapping[str, Mapping[str, Any]]

    @classmethod
    def load(cls, path: Path | str) -> "TargetFile":
        path = Path(path)
        try:
            source = path.resolve().relative_to(PACKAGE_ROOT).as_posix()
        except ValueError:
            source = path.as_posix()
        return cls.from_mapping(load_yaml(path), source, file_sha256(path))

    @classmethod
    def from_mapping(cls, raw: Any, source: str, sha256: str = "") -> "TargetFile":
        where = f"human targets {source}"
        head = check_keys(raw, where, ("schema_version", "name", "tolerance", "age_groups", "targets", "sides", "not_targets", "sources"))
        if head["schema_version"] != 1:
            raise ConfigError(f"{where}: schema_version 1 is the only one, got {head['schema_version']!r}")
        tolerance = check_keys(head["tolerance"], f"{where}.tolerance", (*TOLERANCE, "decided"))
        for key, expected in TOLERANCE.items():  # the user's rules of task 0; another rule is a new schema
            as_choice(tolerance[key], f"{where}.tolerance.{key}", (expected,))
        sources = head["sources"]
        if not isinstance(sources, Mapping) or not sources:
            raise ConfigError(f"{where}.sources: a mapping of source name to its citation")
        for key, entry in sources.items():
            check_keys(entry, f"{where}.sources.{key}", ("cite", "cached"))
        groups = {}
        for name, span in (head["age_groups"] or {}).items():
            if not isinstance(span, list) or len(span) != 2 or not all(isinstance(v, int) and not isinstance(v, bool) for v in span) or span[1] < span[0]:
                raise ConfigError(f"{where}.age_groups.{name}: [from, to], whole years")
            groups[str(name)] = (span[0], span[1])
        raw_targets = head["targets"]
        if not isinstance(raw_targets, Mapping) or not raw_targets:
            raise ConfigError(f"{where}.targets: at least one target")
        targets = {str(key): _target(str(key), entry, sources, groups, f"{where}.targets.{key}") for key, entry in raw_targets.items()}
        for target in targets.values():
            other = target.disagrees_with
            if other is not None and (other not in targets or targets[other].disagrees_with != target.id):
                raise ConfigError(f"{where}.targets.{target.id}.disagrees_with: {other!r} must be a target that disagrees back")
        sides = _sides(head["sides"], sources, f"{where}.sides")
        not_targets = []
        for i, entry in enumerate(head["not_targets"] or []):
            entry = check_keys(entry, f"{where}.not_targets[{i}]", ("id", "claim", "source", "reason"))
            if entry["id"] in targets:
                raise ConfigError(f"{where}.not_targets[{i}]: {entry['id']!r} is also a target")
            not_targets.append({key: " ".join(str(value).split()) for key, value in entry.items()})
        return cls(name=str(head["name"]), source=source, sha256=sha256, tolerance=dict(tolerance), age_groups=groups,
                   targets=targets, sides=sides, not_targets=tuple(not_targets),
                   sources={str(k): dict(v) for k, v in sources.items()})

    def describe(self) -> dict[str, Any]:
        return {"name": self.name, "file": self.source, "sha256": self.sha256, "tolerance": dict(self.tolerance),
                "targets": sorted(self.targets), "not_targets": [entry["id"] for entry in self.not_targets]}


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{where}: a non-empty text")
    return " ".join(value.split())


def _target(key: str, raw: Any, sources: Mapping[str, Any], groups: Mapping[str, Any], where: str) -> Target:
    entry = check_keys(raw, where, ("claim", "kind", "measure", "source", "where", "read", "setting", "differs", "applies"),
                       ("value", "sd", "unit", "check", "reported", "reported_speeds", "disagrees_with"))
    kind = as_choice(entry["kind"], f"{where}.kind", KINDS)
    if entry["source"] not in sources:
        raise ConfigError(f"{where}.source: {entry['source']!r} is not under 'sources'; a target without a source is not a target")
    read = str(entry["read"])
    if read not in READ:
        raise ConfigError(f"{where}.read: expected one of {list(READ)}, got {read!r}")
    differs = entry["differs"]
    if not isinstance(differs, list):
        raise ConfigError(f"{where}.differs: a list (empty when the study's setting is matched)")
    applies = check_keys(entry["applies"], f"{where}.applies", (), APPLIES)
    for i, group in enumerate(applies.get("pair_ages") or []):
        if group != "any" and group not in groups:
            raise ConfigError(f"{where}.applies.pair_ages[{i}]: {group!r} is not under 'age_groups'")
    value = sd = check = None
    if kind == VALUE:
        if "check" in entry:
            raise ConfigError(f"{where}: a value target is judged by its SD, not by a check")
        value = as_number(entry.get("value"), f"{where}.value")
        sd = as_number(entry.get("sd"), f"{where}.sd", minimum=0.0, strict_minimum=True)
        if "unit" not in entry:
            raise ConfigError(f"{where}.unit: a value target gives its unit")
    else:
        if "value" in entry or "sd" in entry:
            raise ConfigError(f"{where}: a direction target has no value or SD (that would make it a value target); put its numbers under 'reported'")
        check = as_choice(entry.get("check"), f"{where}.check", CHECKS)
    reported = dict(entry.get("reported") or {})
    if "reported_speeds" in entry:
        reported["speeds_mps"] = dict(entry["reported_speeds"])
    return Target(
        id=key, claim=_text(entry["claim"], f"{where}.claim"), kind=kind,
        measure=as_choice(entry["measure"], f"{where}.measure", MEASURES), source=str(entry["source"]),
        where=_text(entry["where"], f"{where}.where"), read=read, setting=_text(entry["setting"], f"{where}.setting"),
        differs=tuple(_text(item, f"{where}.differs[{i}]") for i, item in enumerate(differs)),
        applies=dict(applies), value=value, sd=sd, unit=entry.get("unit"), check=check, reported=reported,
        disagrees_with=entry.get("disagrees_with"),
    )


def _sides(raw: Any, sources: Mapping[str, Any], where: str) -> dict[str, Any]:
    sides = check_keys(raw, where, ("judged", "singapore", "places"))
    if sides["judged"] is not False or sides["singapore"] != "unknown":
        raise ConfigError(f"{where}: the side is not judged while Singapore's is unknown (decision 6; no published study found in #69)")
    places = {}
    for name, entry in (sides["places"] or {}).items():
        entry = check_keys(entry, f"{where}.places.{name}", ("side", "shares", "source", "read"), ("note",))
        as_choice(entry["side"], f"{where}.places.{name}.side", SIDES)
        if entry["source"] not in sources:
            raise ConfigError(f"{where}.places.{name}.source: {entry['source']!r} is not under 'sources'")
        places[str(name)] = dict(entry)
    return {"judged": False, "singapore": "unknown", "places": places}
