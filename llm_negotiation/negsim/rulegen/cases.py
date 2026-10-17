"""Conflict cases: a conflict taken from a finished baseline run and frozen as data (issue #30, Part 2).

A **case** is one pair interaction of a primary-baseline run: the scenario and its version,
the run and its seed, the two agents, what each could perceive at the moment the pair formed
(both perception records, and the shared snapshot of every field a rule may read), an empty
slot per agent for the private information a session gives it, the pair's severity tier,
and what happened under the baseline. The outcome is kept for later analysis and is shown
to no condition of rule generation. ``docs/cases.md`` describes every field.

Cases are **immutable and versioned**, like rules: ``cases/<case_id>.v<n>.json``, with the
SHA-256 of every file frozen in ``cases/MANIFEST.json``. A case id is stable: it is derived
from the run and the pair it came from, so extracting again from the same runs gives the
same cases, file for file. A **case set** is the list of cases one extraction selected,
recorded in the manifest with its configuration and a report of what was eligible.

**A new version by re-stepping** (issue #32). When the perception record gains fields, a case
gets a next version that has them: its source run is rebuilt from its config, run again up to
the step its pair formed, and the two records the run builds then are taken, with the snapshot
of the newer rule format; every field of the version it is made from must come out equal, or
nothing is written. The new version says what it was made from (``derived_from``).

    python -m negsim.rulegen.cases extract configs/cases/si3_cases_v1.yaml [--dry-run]
    python -m negsim.rulegen.cases restep --set si3_v1 --new-set si3_v2 [--dry-run]
    python -m negsim.rulegen.cases list [--set NAME]
    python -m negsim.rulegen.cases show CASE_ID [--version N]
    python -m negsim.rulegen.cases check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, TextIO

from ..avoidance.perception import ENCOUNTER_CLASSES, PerceptionRecord
from ..configutil import PACKAGE_ROOT, ConfigError, as_number, check_keys, load_yaml, resolve_path
from ..metrics.avoidance import TIERS, tier_rank
from ..rules.snapshot import snapshot_of_record
from ..runlog.schema import CONFIG_FILE, INTERACTIONS_FILE, OUTCOME_FILE, PAIR_INTERACTIONS_FILE

#: 2 since issue #32: a case may say what it was made from (``derived_from``), and its records
#: are of the perception version of the code that made it.
CASE_FORMAT_VERSION = 2
CASES_ROOT = PACKAGE_ROOT / "cases"
MANIFEST_FILE = "MANIFEST.json"
EXTRACTIONS_DIR = "extractions"
CASE_FILE = re.compile(r"^(?P<case_id>[a-z][a-z0-9_]{2,47})\.v(?P<version>[1-9][0-9]*)\.json$")
#: The baseline cases are taken from (issue #30: "the primary baseline").
PRIMARY_BASELINE = "orca_perturbed_v1"
#: Short names for case ids, so that the rule ids built from them stay readable.
SCENARIO_SHORT = {
    "wide_corridor_head_on": "head_on",
    "open_crossing": "crossing",
    "overtaking": "overtaking",
    "corridor_to_bottleneck": "bottleneck",
    "bidirectional_flow": "flow",
    "passage_meeting": "passage",  # issue #32
}
#: What a stratum may be made of.
STRATUM_KEYS = ("scenario", "variant", "tier", "encounter_class")

# Why a pair or a run was not eligible.
REASON_TIER = "tier_below_minimum"
REASON_ONE_SIDED = "one_sided_formation"  # one of the two did not perceive the other when the pair formed
REASON_FORMATION_CLASS = "formation_class_not_eligible"  # e.g. not approaching each other when the pair formed
REASON_BASELINE = "not_the_primary_baseline"
REASON_PROVIDER = "not_plain_orca"
REASON_SCHEMA = "log_schema_before_version_4"
REASON_NO_RECORDS = "interactions_not_logged"


class CaseError(ConfigError):
    """A case, a case set or the case store that cannot be used."""


def case_id_for(scenario_type: str, experiment: str, run_id: str, pair_id: int) -> str:
    """A stable id: the scenario's short name and a hash of the run and the pair."""
    digest = hashlib.sha256(f"{experiment}/{run_id}/pair{pair_id}".encode("utf-8")).hexdigest()[:8]
    return f"{SCENARIO_SHORT.get(scenario_type, scenario_type)}_{digest}"


def text_sha256(text: str) -> str:
    """SHA-256 of a text with its line endings normalised to LF, as for rule files."""
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def case_json(case: Mapping[str, Any]) -> str:
    """How a case is written: indented JSON, keys in the order built, ending in a newline."""
    return json.dumps(case, indent=2, ensure_ascii=False) + "\n"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _variant_label(variant: Mapping[str, str]) -> str:
    return "+".join(f"{factor}={level}" for factor, level in variant.items()) or "base"


# --- building one case ----------------------------------------------------------------------------


#: The rule fields a snapshot taken from a perception record of each version holds: those of
#: the rule format whose fields that record carries (issue #32). A record of version 2 gives
#: the fields of rule schema 2, so a case taken from one is what it always was.
SNAPSHOT_SCHEMA_OF_PERCEPTION = {2: 2, 3: 3}


def shared_snapshot(record: Mapping[str, Any], visibility: Mapping[str, bool]) -> dict[str, Any]:
    """The values a rule could read for the pair, from one agent's logged perception record.

    The same as the shared snapshot the run loop evaluates rules on, up to the log's rounding
    (``rule-matching.md``, section 1); demographic fields are empty unless the run had personas.
    It holds the fields the record's version carries (:data:`SNAPSHOT_SCHEMA_OF_PERCEPTION`).
    """
    snapshot = snapshot_of_record(PerceptionRecord.from_dict(record), visibility)
    return snapshot.as_dict(SNAPSHOT_SCHEMA_OF_PERCEPTION[record["schema_version"]])


def build_case(
    run_dir: Path,
    config: Mapping[str, Any],
    outcome: Mapping[str, Any],
    pair: Mapping[str, Any],
    records: Mapping[int, Mapping[str, Any]],
) -> dict[str, Any]:
    """The case of one pair interaction of one run. ``records`` are the two perception records
    built when the pair formed, keyed by the observing agent."""
    scenario = config["scenario"]
    a, b = pair["agents"]
    specs = {agent["agent_id"]: agent for agent in scenario["agents"]}
    baseline = config.get("baseline") or {}
    segments = scenario.get("single_file", {}).get("segments", [])
    goal = outcome.get("time_to_goal_s", {})
    first_through = [segment.get("first_through") for segment in outcome.get("single_file", [])]
    return {
        "case_format_version": CASE_FORMAT_VERSION,
        "case_id": case_id_for(scenario["type"], config["experiment_name"], config["run_id"], pair["pair_id"]),
        "version": 1,
        "scenario": {
            "type": scenario["type"],
            "file": config["scenario_file"],
            "schema_version": scenario["schema_version"],
            "resolved_sha256": text_sha256(json.dumps(scenario, sort_keys=True)),
            "description": scenario.get("description", ""),
            "variant": dict(config.get("variant", {})),
            "n_agents": scenario["n_agents"],
            "dt_s": scenario["dt_s"],
            "geometry": dict(scenario.get("geometry", {})),
            "single_file_segments": [
                {
                    "name": segment["name"],
                    "width_m": segment["width_m"],
                    "length_m": round(max(segment["xmax"] - segment["xmin"], segment["ymax"] - segment["ymin"]), 6),
                }
                for segment in segments
            ],
        },
        "source": {
            "experiment": config["experiment_name"],
            "run_id": config["run_id"],
            "run_index": config["run_index"],
            "seed": config["seed"],
            "seeding": config.get("seeding"),
            "repeat": config["repeat"],
            "baseline": {"name": baseline.get("name"), "sha256": baseline.get("sha256")},
            "perturbation": config.get("perturbation"),
            "git_commit": config.get("git", {}).get("commit"),
            "git_dirty": config.get("git", {}).get("dirty"),
            "created_utc": config["created_utc"],
            "log_schema_version": config["log_schema_version"],
            "pair_id": pair["pair_id"],
        },
        "agents": [a, b],
        "formation": {
            "step": pair["start_step"],
            "time_s": pair["start_time_s"],
            "encounter_class": pair["encounter_class_at_start"],
        },
        "snapshot": shared_snapshot(records[a], config["visibility"]),
        "observations": {str(agent): dict(records[agent]) for agent in (a, b)},
        "bodies": {
            str(agent): {
                "radius_m": specs[agent]["radius_m"],
                "preferred_speed_mps": specs[agent]["preferred_speed_mps"],
                "max_speed_mps": specs[agent]["max_speed_mps"],
                "group": specs[agent]["group"],
            }
            for agent in (a, b)
        },
        "private": {str(agent): {"task": None} for agent in (a, b)},
        "severity_tier": pair["severity_tier"],
        "baseline_outcome": {
            "category": pair["outcome"],
            "severity_tier": pair["severity_tier"],
            "tier_detail": dict(pair["tier_detail"]),
            "pair_exposure_time_s": pair["pair_exposure_time_s"],
            "conflict_exposure_time_s": dict(pair["conflict_exposure_time_s"]),
            "first_pair_exposed_step": pair["first_pair_exposed_step"],
            "min_separation_m": pair["min_separation_m"],
            "passed_time_s": pair["passed_time_s"],
            "end_time_s": pair["end_time_s"],
            "end_reason": pair["end_reason"],
            "run_status": outcome["status"],
            "time_to_goal_s": {str(agent): goal.get(str(agent)) for agent in (a, b)},
            "first_through": first_through[0] if first_through else None,
        },
    }


# --- a new version by re-stepping (issue #32) -----------------------------------------------------


def _differences(old: Any, new: Any, where: str) -> list[str]:
    """Every place where ``new`` does not hold what ``old`` holds: a key of ``old`` missing from
    ``new``, or a value that differs. Keys only ``new`` has are what it adds, and are not counted."""
    if isinstance(old, Mapping) and isinstance(new, Mapping):
        found = []
        for key, value in old.items():
            if key not in new:
                found.append(f"{where}.{key}: missing")
            else:
                found += _differences(value, new[key], f"{where}.{key}")
        return found
    return [] if old == new else [f"{where}: {old!r} became {new!r}"]


def restep_case(case: Mapping[str, Any], git: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    """The next version of ``case``, with its source run's perception records as the code now
    builds them: the run is rebuilt from its config, run again up to the step its pair formed,
    and the two records it builds there are taken, with the snapshot of the rule format they
    carry. Every field of ``case``'s records and snapshot must come out equal (the schema
    version aside), or a :class:`CaseError` says where they differ; nothing else of the case
    changes."""
    from ..avoidance.simulation import AvoidanceSimulation
    from ..scenarios.registry import build_crowd_scenario
    from .replay import source_plan  # replay imports this module

    plan = source_plan(case)  # checks the seed, and that the scenario resolves as the case says
    simulation = AvoidanceSimulation(
        build_crowd_scenario(plan.scenario_config), provider=plan.provider(), attributes=plan.attributes(),
        visibility=plan.visibility, arbitration=plan.arbitration, share_policy=plan.share_policy, seed=plan.seed,
        record_trajectory=False, perturbation=plan.perturbation,
    )
    step, (a, b) = case["formation"]["step"], case["agents"]
    while simulation.world.step_index <= step and simulation.status is None:
        simulation.step()
    records = {
        interaction.observer_id: interaction.record.as_dict()
        for interaction in simulation.interactions
        if interaction.start_step == step and {interaction.observer_id, interaction.neighbour_id} == {a, b}
    }
    name = f"{case['case_id']}@{case['version']}"
    if set(records) != {a, b}:
        raise CaseError(f"{name}: re-stepping its source run, the two did not perceive each other at step {step}")
    snapshot = shared_snapshot(records[a], plan.visibility)
    problems = _differences(case["snapshot"], snapshot, "snapshot")
    for agent in (a, b):
        old = {key: value for key, value in case["observations"][str(agent)].items() if key != "schema_version"}
        problems += _differences(old, records[agent], f"observations.{agent}")
    if problems:
        raise CaseError(f"{name}: re-stepping its source run did not give the case back:\n  " + "\n  ".join(problems))
    newer = dict(case)
    newer.update(
        case_format_version=CASE_FORMAT_VERSION,
        version=case["version"] + 1,
        snapshot=snapshot,
        observations={str(agent): records[agent] for agent in (a, b)},
        derived_from={
            "case": name,
            "method": "re-stepped",
            "perception_schema_version": records[a]["schema_version"],
            "git_commit": None if git is None else git.get("commit"),
            "git_dirty": None if git is None else git.get("dirty"),
            "checked": "every field of the records and the snapshot of the version it was made from came out equal",
        },
    )
    return newer


def restep_set(store: "CaseStore", case_set: str, new_set: str, git: Optional[Mapping[str, Any]] = None, write: bool = True) -> list[str]:
    """A next version of every case of ``case_set`` (``restep_case``), frozen, and the new versions
    recorded as the case set ``new_set``. Returns their references."""
    references = []
    for case_id, version in store.case_set(case_set):
        newer = restep_case(store.get(case_id, version), git)
        if write:
            store.add(newer, note=f"case set {new_set}, re-stepped from {case_id}@{version} (issue #32)")
        references.append(f"{case_id}@{newer['version']}")
    if write:
        entry = store.manifest()["case_sets"][case_set]
        store.add_case_set(
            new_set,
            {
                "cases": sorted(references),
                "config": entry["config"],
                "config_sha256": entry["config_sha256"],
                "extraction": entry["extraction"],
                "description": f"The cases of {case_set}, each re-stepped as its next version with perception records of version 3 (issue #32).",
                "derived_from": case_set,
            },
        )
    return references


# --- what is eligible -----------------------------------------------------------------------------


@dataclass
class Candidate:
    """An eligible pair interaction, before it is selected."""

    case_id: str
    run_dir: Path
    pair: Mapping[str, Any]
    stratum: dict[str, Any]


@dataclass
class SourceReport:
    """What one source run held."""

    run: str
    pairs: int = 0
    eligible: int = 0
    excluded: Counter = field(default_factory=Counter)
    run_excluded: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "run": self.run,
            "pairs": self.pairs,
            "eligible": self.eligible,
            "excluded": dict(sorted(self.excluded.items())),
            "run_excluded": self.run_excluded,
        }


def candidates_of_run(
    run_dir: Path, baseline: str, min_tier: str, formation_classes: Optional[Sequence[str]] = None
) -> tuple[list[Candidate], SourceReport]:
    """The eligible pair interactions of one run, and why the others were not.

    ``formation_classes``, if given, are the encounter classes a pair may have had when it
    formed; ``None`` allows any.
    """
    config = _read_json(run_dir / CONFIG_FILE)
    report = SourceReport(f"{config['experiment_name']}/{config['run_id']}")
    if config.get("log_schema_version", 0) < 4:
        report.run_excluded = REASON_SCHEMA
        return [], report
    if (config.get("baseline") or {}).get("name") != baseline:
        report.run_excluded = REASON_BASELINE
        return [], report
    if config.get("directives", {}).get("provider") != "null":
        report.run_excluded = REASON_PROVIDER
        return [], report
    if not config.get("logging", {}).get("interactions", True):
        report.run_excluded = REASON_NO_RECORDS
        return [], report
    started = {
        (record["observer_id"], record["neighbour_id"], record["start_step"])
        for record in _read_jsonl(run_dir / INTERACTIONS_FILE)
    }
    found = []
    for pair in _read_jsonl(run_dir / PAIR_INTERACTIONS_FILE):
        report.pairs += 1
        if tier_rank(pair["severity_tier"]) < tier_rank(min_tier):
            report.excluded[REASON_TIER] += 1
            continue
        a, b = pair["agents"]
        if (a, b, pair["start_step"]) not in started or (b, a, pair["start_step"]) not in started:
            report.excluded[REASON_ONE_SIDED] += 1
            continue
        if formation_classes is not None and pair["encounter_class_at_start"] not in formation_classes:
            report.excluded[REASON_FORMATION_CLASS] += 1
            continue
        report.eligible += 1
        found.append(
            Candidate(
                case_id=case_id_for(config["scenario"]["type"], config["experiment_name"], config["run_id"], pair["pair_id"]),
                run_dir=run_dir,
                pair=pair,
                stratum={
                    "scenario": config["scenario"]["type"],
                    "variant": _variant_label(config.get("variant", {})),
                    "tier": pair["severity_tier"],
                    "encounter_class": pair["encounter_class_at_start"],
                },
            )
        )
    return found, report


# --- the extraction config ------------------------------------------------------------------------


@dataclass(frozen=True)
class ExtractionConfig:
    case_set: str
    description: str
    sources: tuple[str, ...]
    baseline: str
    min_tier: str
    formation_classes: Optional[tuple[str, ...]]
    strata_by: tuple[str, ...]
    per_stratum: int
    per_stratum_by_scenario: Mapping[str, int]
    seed: int
    source_file: str
    source_sha256: str

    @classmethod
    def load(cls, path: Path | str) -> "ExtractionConfig":
        resolved = resolve_path(path)
        raw = load_yaml(resolved)
        where = f"case extraction config {path}"
        check_keys(raw, where, ("case_set", "sources", "strata"), ("schema_version", "description", "eligibility"))
        if raw.get("schema_version", 1) != 1:
            raise CaseError(f"{where}: schema_version {raw['schema_version']!r} is not supported")
        name = str(raw["case_set"])
        if not re.fullmatch(r"[a-z][a-z0-9_]{1,40}", name):
            raise CaseError(f"{where}.case_set: lower-case letters, digits and '_', got {name!r}")
        sources = raw["sources"]
        if not isinstance(sources, list) or not sources:
            raise CaseError(f"{where}.sources: expected a list of experiment folders under llm_negotiation/")
        eligibility = check_keys(
            raw.get("eligibility") or {}, f"{where}.eligibility", (), ("baseline", "min_tier", "formation_classes")
        )
        min_tier = str(eligibility.get("min_tier", "T1"))
        if min_tier not in TIERS:
            raise CaseError(f"{where}.eligibility.min_tier: one of {list(TIERS)}, got {min_tier!r}")
        formation = eligibility.get("formation_classes")
        if formation is not None and (
            not isinstance(formation, list) or not formation or any(name not in ENCOUNTER_CLASSES for name in formation)
        ):
            raise CaseError(f"{where}.eligibility.formation_classes: a list of encounter classes from {list(ENCOUNTER_CLASSES)}, got {formation!r}")
        strata = check_keys(raw["strata"], f"{where}.strata", ("by", "per_stratum", "seed"))
        by = tuple(strata["by"]) if isinstance(strata["by"], list) else ()
        if not by or any(key not in STRATUM_KEYS for key in by) or len(set(by)) != len(by):
            raise CaseError(f"{where}.strata.by: a list of distinct keys from {list(STRATUM_KEYS)}, got {strata['by']!r}")
        per = strata["per_stratum"]
        default, by_scenario = per, {}
        if isinstance(per, Mapping):
            check_keys(per, f"{where}.strata.per_stratum", ("default",), tuple(SCENARIO_SHORT))
            default = per["default"]
            by_scenario = {name: int(as_number(value, f"{where}.strata.per_stratum.{name}", minimum=0)) for name, value in per.items() if name != "default"}
        return cls(
            case_set=name,
            description=" ".join(str(raw.get("description", "")).split()),
            sources=tuple(str(source) for source in sources),
            baseline=str(eligibility.get("baseline", PRIMARY_BASELINE)),
            min_tier=min_tier,
            formation_classes=None if formation is None else tuple(formation),
            strata_by=by,
            per_stratum=int(as_number(default, f"{where}.strata.per_stratum", minimum=0)),
            per_stratum_by_scenario=by_scenario,
            seed=int(as_number(strata["seed"], f"{where}.strata.seed", minimum=0)),
            source_file=str(path).replace("\\", "/"),
            source_sha256=text_sha256(resolved.read_text(encoding="utf-8")),
        )

    def quota(self, scenario: str) -> int:
        return self.per_stratum_by_scenario.get(scenario, self.per_stratum)


def select(candidates: Sequence[Candidate], config: ExtractionConfig) -> tuple[list[Candidate], list[dict[str, Any]]]:
    """Stratified sampling: within each stratum, up to its quota, seeded per stratum.

    Each stratum draws from a random stream of its own, seeded by the configured seed and the
    stratum's key, from its candidates sorted by case id. Adding a source or a stratum
    therefore never changes what another stratum selects.
    """
    strata: dict[tuple, list[Candidate]] = {}
    for candidate in candidates:
        key = tuple(candidate.stratum[name] for name in config.strata_by)
        strata.setdefault(key, []).append(candidate)
    chosen, table = [], []
    for key in sorted(strata, key=lambda item: tuple(str(part) for part in item)):
        members = sorted(strata[key], key=lambda candidate: candidate.case_id)
        stratum = dict(zip(config.strata_by, key))
        quota = config.quota(members[0].stratum["scenario"])
        rng = random.Random(f"{config.seed}:{json.dumps(stratum, sort_keys=True)}")
        picked = sorted(rng.sample(members, min(quota, len(members))), key=lambda candidate: candidate.case_id)
        chosen.extend(picked)
        table.append({"stratum": stratum, "eligible": len(members), "selected": [candidate.case_id for candidate in picked]})
    return chosen, table


# --- the store ------------------------------------------------------------------------------------


class CaseStore:
    """The frozen case files and case sets under ``llm_negotiation/cases/``."""

    def __init__(self, root: Path | str = CASES_ROOT):
        self.root = Path(root)
        self.manifest_path = self.root / MANIFEST_FILE

    # --- reading -----------------------------------------------------------------------------

    def manifest(self) -> dict[str, Any]:
        if not self.manifest_path.is_file():
            return {
                "about": (
                    "SHA-256 of every conflict case file (issue #30), with line endings normalised to LF. "
                    "negsim refuses a case file that is not listed here or whose contents no longer match. A case "
                    "is frozen once listed: a changed case is a new file with the next version, never an edit. "
                    "case_sets records which cases each extraction selected, with its configuration."
                ),
                "case_format_version": CASE_FORMAT_VERSION,
                "files": {},
                "case_sets": {},
            }
        return _read_json(self.manifest_path)

    def check(self) -> list[str]:
        """Every way the store does not match its manifest; empty if it does."""
        manifest = self.manifest()
        listed = dict(manifest.get("files", {}))
        problems = []
        for path in sorted(self.root.glob("*.json")):
            if path.name == MANIFEST_FILE:
                continue
            entry = listed.pop(path.name, None)
            if entry is None:
                problems.append(f"{path.name}: not in {MANIFEST_FILE}")
            elif text_sha256(path.read_text(encoding="utf-8")) != entry["sha256"]:
                problems.append(f"{path.name}: its contents are not the version frozen in {MANIFEST_FILE}")
            elif CASE_FILE.match(path.name) is None:
                problems.append(f"{path.name}: a case file is named <case_id>.v<version>.json")
        problems.extend(f"{name}: listed in {MANIFEST_FILE} but not found" for name in sorted(listed))
        for name, entry in manifest.get("case_sets", {}).items():
            for reference in entry["cases"]:
                case_id, version = reference.split("@")
                if f"{case_id}.v{version}.json" not in manifest.get("files", {}):
                    problems.append(f"case set {name}: {reference} is not in the store")
        return problems

    def _require_frozen(self) -> None:
        problems = self.check()
        if problems:
            raise CaseError("the case store does not match its manifest:\n  " + "\n  ".join(problems))

    def get(self, case_id: str, version: Optional[int] = None) -> dict[str, Any]:
        """A case, checked against the manifest; the latest version unless one is named."""
        self._require_frozen()
        versions = sorted(
            int(match["version"])
            for path in self.root.glob(f"{case_id}.v*.json")
            if (match := CASE_FILE.match(path.name)) and match["case_id"] == case_id
        )
        if not versions:
            raise CaseError(f"no case {case_id!r} in {self.root}")
        chosen = versions[-1] if version is None else version
        if chosen not in versions:
            raise CaseError(f"case {case_id!r} has versions {versions}, not {version!r}")
        return _read_json(self.root / f"{case_id}.v{chosen}.json")

    def case_set(self, name: str) -> list[tuple[str, int]]:
        sets = self.manifest().get("case_sets", {})
        if name not in sets:
            raise CaseError(f"no case set {name!r}; known: {sorted(sets)}")
        return [(reference.split("@")[0], int(reference.split("@")[1])) for reference in sets[name]["cases"]]

    def all_cases(self) -> list[dict[str, Any]]:
        self._require_frozen()
        return [_read_json(self.root / name) for name in sorted(self.manifest().get("files", {}))]

    # --- writing (only ever adds) --------------------------------------------------------------

    def add(self, case: Mapping[str, Any], note: str = "") -> tuple[str, bool]:
        """Freeze a case. Returns its file name and whether anything was written.

        The same content again is not an error and writes nothing; different content under a
        frozen name is refused.
        """
        name = f"{case['case_id']}.v{case['version']}.json"
        text = case_json(case)
        manifest = self.manifest()
        path = self.root / name
        if name in manifest["files"] or path.is_file():
            if path.is_file() and text_sha256(path.read_text(encoding="utf-8")) == text_sha256(text):
                return name, False
            raise CaseError(f"{name} is frozen with other contents; a changed case is the next version, never an edit")
        self.root.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        manifest["files"][name] = {
            "sha256": text_sha256(text),
            "frozen_on": date.today().isoformat(),
            "scenario": case["scenario"]["type"],
            "severity_tier": case["severity_tier"],
            "source": f"{case['source']['experiment']}/{case['source']['run_id']}, pair {case['source']['pair_id']}",
            "note": note,
        }
        self._write_manifest(manifest)
        return name, True

    def add_case_set(self, name: str, entry: Mapping[str, Any]) -> bool:
        """Record a case set; the same record again writes nothing, a different one is refused."""
        manifest = self.manifest()
        existing = manifest["case_sets"].get(name)
        if existing is not None:
            if existing == dict(entry):
                return False
            raise CaseError(f"case set {name!r} is already recorded with other contents; name the new set differently")
        manifest["case_sets"][name] = dict(entry)
        self._write_manifest(manifest)
        return True

    def _write_manifest(self, manifest: Mapping[str, Any]) -> None:
        manifest = dict(manifest)
        manifest["files"] = dict(sorted(manifest["files"].items()))
        self.manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


# --- the extraction -------------------------------------------------------------------------------


@dataclass
class ExtractionReport:
    config: ExtractionConfig
    sources: list[SourceReport]
    strata: list[dict[str, Any]]
    selected: list[str]
    written: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_set": self.config.case_set,
            "config": self.config.source_file,
            "config_sha256": self.config.source_sha256,
            "baseline": self.config.baseline,
            "min_tier": self.config.min_tier,
            "formation_classes": None if self.config.formation_classes is None else list(self.config.formation_classes),
            "strata_by": list(self.config.strata_by),
            "per_stratum": self.config.per_stratum,
            "per_stratum_by_scenario": dict(self.config.per_stratum_by_scenario),
            "seed": self.config.seed,
            "sources": [source.as_dict() for source in self.sources],
            "strata": self.strata,
            "selected": list(self.selected),
        }

    def lines(self) -> list[str]:
        out = [f"case set {self.config.case_set}: {len(self.selected)} case(s) selected"]
        pairs = sum(source.pairs for source in self.sources)
        eligible = sum(source.eligible for source in self.sources)
        out.append(f"  {len(self.sources)} source run(s), {pairs} pair interaction(s), {eligible} eligible (tier {self.config.min_tier} and above)")
        for row in self.strata:
            label = ", ".join(f"{key} {value}" for key, value in row["stratum"].items())
            out.append(f"  {label}: {row['eligible']} eligible, selected {', '.join(row['selected']) or 'none'}")
        return out


def extract(config: ExtractionConfig, store: Optional[CaseStore] = None, write: bool = True) -> ExtractionReport:
    """Find the eligible pairs of the source runs, sample them by stratum, and freeze the cases."""
    store = store or CaseStore()
    candidates, reports = [], []
    for source in config.sources:
        folder = resolve_path(source)
        runs = sorted(path.parent for path in folder.glob(f"*/{CONFIG_FILE}"))
        if not runs:
            raise CaseError(f"{source}: no run folders found")
        for run_dir in runs:
            found, report = candidates_of_run(run_dir, config.baseline, config.min_tier, config.formation_classes)
            candidates.extend(found)
            reports.append(report)
    chosen, table = select(candidates, config)
    report = ExtractionReport(config, reports, table, [candidate.case_id for candidate in chosen])
    if not write:
        return report

    by_run: dict[Path, list[Candidate]] = {}
    for candidate in chosen:
        by_run.setdefault(candidate.run_dir, []).append(candidate)
    references = []
    for run_dir, members in sorted(by_run.items()):
        config_json = _read_json(run_dir / CONFIG_FILE)
        outcome = _read_json(run_dir / OUTCOME_FILE)
        wanted = {(candidate.pair["agents"][0], candidate.pair["agents"][1], candidate.pair["start_step"]) for candidate in members}
        records: dict[tuple[int, int, int], dict] = {}
        for record in _read_jsonl(run_dir / INTERACTIONS_FILE):
            observer, neighbour, step = record["observer_id"], record["neighbour_id"], record["start_step"]
            if (min(observer, neighbour), max(observer, neighbour), step) in wanted:
                records[(observer, neighbour, step)] = record["perception"]
        for candidate in members:
            a, b = candidate.pair["agents"]
            step = candidate.pair["start_step"]
            case = build_case(run_dir, config_json, outcome, candidate.pair, {a: records[(a, b, step)], b: records[(b, a, step)]})
            name, written = store.add(case, note=f"case set {config.case_set}")
            if written:
                report.written.append(name)
            references.append(f"{case['case_id']}@{case['version']}")
    extraction_file = f"{EXTRACTIONS_DIR}/{config.case_set}.json"
    (store.root / EXTRACTIONS_DIR).mkdir(parents=True, exist_ok=True)
    (store.root / extraction_file).write_text(json.dumps(report.as_dict(), indent=2) + "\n", encoding="utf-8", newline="\n")
    store.add_case_set(
        config.case_set,
        {
            "cases": sorted(references),
            "config": config.source_file,
            "config_sha256": config.source_sha256,
            "extraction": extraction_file,
            "description": config.description,
        },
    )
    return report


# --- the command line -----------------------------------------------------------------------------


def main(argv: Optional[list[str]] = None, out: Optional[TextIO] = None) -> int:
    out = out or sys.stdout
    parser = argparse.ArgumentParser(prog="negsim.rulegen.cases", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--store", default=str(CASES_ROOT), help="the case store folder (default: cases)")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("extract", help="extract a case set from baseline runs")
    run.add_argument("config")
    run.add_argument("--dry-run", action="store_true", help="report what would be selected; write nothing")
    restep = commands.add_parser("restep", help="a next version of every case of a set, re-stepped from its source run (issue #32)")
    restep.add_argument("--set", dest="case_set", required=True)
    restep.add_argument("--new-set", required=True)
    restep.add_argument("--dry-run", action="store_true", help="re-step and check every case; write nothing")
    listing = commands.add_parser("list", help="the cases, or one case set")
    listing.add_argument("--set", dest="case_set")
    show = commands.add_parser("show", help="one case as frozen")
    show.add_argument("case_id")
    show.add_argument("--version", type=int)
    commands.add_parser("check", help="check the store against its manifest")
    args = parser.parse_args(argv)
    store = CaseStore(resolve_path(args.store))
    try:
        if args.command == "extract":
            report = extract(ExtractionConfig.load(args.config), store, write=not args.dry_run)
            for line in report.lines():
                print(line, file=out)
            if not args.dry_run:
                print(f"  written: {len(report.written)} new case file(s); the rest were frozen already", file=out)
        elif args.command == "restep":
            from ..experiment.batch import git_state

            references = restep_set(store, args.case_set, args.new_set, git_state(), write=not args.dry_run)
            for reference in references:
                print(f"  {reference}: every field of its previous version came out equal", file=out)
            print(f"case set {args.new_set}: {len(references)} case(s)" + (" (dry run: nothing written)" if args.dry_run else ""), file=out)
        elif args.command == "list":
            manifest = store.manifest()
            names = sorted(manifest.get("files", {}))
            if args.case_set:
                names = [f"{case_id}.v{version}.json" for case_id, version in store.case_set(args.case_set)]
            for name in names:
                entry = manifest["files"][name]
                print(f"{name:32} {entry['scenario']:24} {entry['severity_tier']}  {entry['source']}", file=out)
            for name, entry in sorted(manifest.get("case_sets", {}).items()):
                print(f"case set {name}: {len(entry['cases'])} case(s), from {entry['config']}", file=out)
        elif args.command == "show":
            print(case_json(store.get(args.case_id, args.version)), end="", file=out)
        else:
            problems = store.check()
            for problem in problems:
                print(f"PROBLEM {problem}", file=out)
            print("the case store matches its manifest" if not problems else f"{len(problems)} problem(s)", file=out)
            return 1 if problems else 0
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
