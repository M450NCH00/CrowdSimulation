"""A rule-set evaluation (issue #74, RF-18; ``docs/rule-set-evaluation.md``).

    python run_experiment.py configs/rule_set_evaluation/rf18_round1.yaml --plan
    python run_experiment.py configs/rule_set_evaluation/rf18_round1.yaml            # runs/<experiment_name>/
    python run_experiment.py configs/rule_set_evaluation/rf18_round1.yaml --overwrite

The staged rules of the rounds so far are switched on **together**, with ORCA for every pair they
do not match, and run beside plain ORCA on the same seeds, in several scenarios. No model is
called, so it costs nothing.

1. **The run's own staging database.** A run reads one rule database, and rules staged by
   different experiments live in different ones, so each chosen rule's files (every version, so
   that its history runs 1, 2, ...) are copied byte for byte into
   ``runs/<experiment>/rule_db_staging/``, with one rule set per arm. Nothing is edited; a rule
   whose staged file changed after it was copied is refused.
2. **Arms.** Each arm is a rule set (of the copied rules) or a set of another database (a
   reference, given numbers but no verdict). Plain ORCA is always run.
3. **Runs.** Every arm on every scenario, on ``seeds`` paired seeds, each beside plain ORCA on the
   same seed and the same people (``baseline.md``, section 6).
4. **Measures and verdicts** (``measures.py``, ``verdicts.py``), a verdict for each judged arm and
   scenario, and for each rule (the arm with that rule alone), for RF-14 to read.

Re-running resumes: a run whose ``measures.json`` exists is not run again unless ``--overwrite``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from .. import __version__
from ..configutil import PACKAGE_ROOT, ConfigError, as_bool, as_choice, as_number, check_keys, load_yaml, resolve_path
from ..experiment.avoidance import AvoidanceExperiment, AvoidanceRunPlan, execute_avoidance_run, forget_rule_database
from .. import populations as P
from ..rules.database import RuleDatabase, file_sha256
from ..rulegen.replay import database_path, mixed_population, population_of
from ..rulegen.writer import StagingDatabase
from ..translation.experiment import visible_for
from . import verdicts as V
from .measures import run_measures

LAYER = "rule_set_evaluation"
SCHEMA_VERSION = 1
RUNS_DIR = PACKAGE_ROOT / "runs"
STAGING_DIR = "rule_db_staging"
RUNS_SUBDIR = "runs"
PLAIN = "plain"
MEASURES_FILE = "measures.json"
DEFAULT_BASELINE = "orca_perturbed_v1"


def is_rule_set_evaluation_config(raw: Any) -> bool:
    return isinstance(raw, Mapping) and raw.get("layer") == LAYER


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _relative(path: Path | str) -> str:
    resolved = Path(path).resolve()
    return resolved.relative_to(PACKAGE_ROOT).as_posix() if resolved.is_relative_to(PACKAGE_ROOT) else resolved.as_posix()


# --- the config ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceRule:
    rule_id: str
    database: Path      # the staging database it is copied from
    version: int        # the version copied; every version up to it is copied
    #: A new priority, so that two rules that both match one situation can be switched on
    #: together (``rule-matching.md``, section 4): the run's database gets one more version,
    #: the same rule with this priority, and that is the version switched on. ``reason`` says why.
    priority: Optional[int] = None
    reason: str = ""

    @property
    def enabled_version(self) -> int:
        return self.version + (self.priority is not None)


@dataclass(frozen=True)
class Arm:
    name: str
    rules: tuple[str, ...] = ()          # rules of the run's own database
    database: Optional[str] = None       # or a rule set of another database (a reference)
    ruleset: Optional[str] = None
    judged: bool = True
    description: str = ""


@dataclass(frozen=True)
class Scenario:
    name: str
    file: str
    rotate_people: bool
    note: str = ""
    overrides: Mapping[str, Any] = field(default_factory=dict)  # deep-merged into the scenario, e.g. a smaller crowd
    #: Since issue #112 (RF-33): the scenario's people from a profile (``negsim.populations``) in
    #: place of ``people``, and what the scenario is for (``realistic`` or ``stress``). ``pool``: a
    #: small scenario's people are the first of a crowd of this many at the profile's exact shares.
    population: Optional[str] = None
    profile: Optional[P.Profile] = None
    purpose: Optional[str] = None
    pool: Optional[int] = None
    #: Since issue #112: this scenario's number of paired seeds, in place of the config's ``seeds``
    #: (the user's decision of 2026-10-27: more seeds where a factor is rare).
    seeds: Optional[int] = None

    def n_seeds(self, default: int) -> int:
        return self.seeds or default


@dataclass(frozen=True)
class RuleSetEvaluationConfig:
    experiment_name: str
    description: str
    rules: tuple[SourceRule, ...]
    left_out: tuple[Mapping[str, str], ...]
    arms: tuple[Arm, ...]
    scenarios: tuple[Scenario, ...]
    baseline: str
    seed: int
    seeds: int
    people: Mapping[str, Any]
    trajectory_stride: int
    alpha: float
    verdict_rule: int = V.DEFAULT_RULE
    source: str = "<config>"

    @classmethod
    def load(cls, path: Path | str) -> "RuleSetEvaluationConfig":
        resolved = resolve_path(path)
        return cls.from_raw(load_yaml(resolved), str(path))

    @classmethod
    def from_raw(cls, raw: Any, source: str = "<config>") -> "RuleSetEvaluationConfig":
        check_keys(
            raw, source, ("layer", "experiment_name", "rules", "arms", "scenarios"),
            ("schema_version", "description", "left_out", "baseline", "seed", "seeds", "people", "logging", "alpha", "verdict_rule"),
        )
        if raw["layer"] != LAYER:
            raise ConfigError(f"{source}: layer must be {LAYER!r}")
        if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ConfigError(f"{source}: schema_version must be {SCHEMA_VERSION}")
        rules = []
        for rule_id, entry in (raw["rules"] or {}).items():
            where = f"{source}.rules.{rule_id}"
            check_keys(entry, where, ("from", "version"), ("priority", "reason"))
            version = int(as_number(entry["version"], f"{where}.version", minimum=1))
            priority = entry.get("priority")
            if priority is not None:
                priority = int(as_number(priority, f"{where}.priority", minimum=0))
                if not str(entry.get("reason") or "").strip():
                    raise ConfigError(f"{where}: a new priority needs a 'reason'")
            rules.append(SourceRule(str(rule_id), resolve_path(entry["from"]), version, priority, " ".join(str(entry.get("reason") or "").split())))
        known = {rule.rule_id for rule in rules}
        arms, names = [], set()
        for i, entry in enumerate(raw["arms"] or []):
            where = f"{source}.arms[{i}]"
            check_keys(entry, where, ("name",), ("rules", "database", "ruleset", "judged", "description"))
            name = str(entry["name"])
            if name == PLAIN or name in names:
                raise ConfigError(f"{where}.name: {name!r} is {'reserved for plain ORCA' if name == PLAIN else 'used twice'}")
            names.add(name)
            own, other = entry.get("rules"), entry.get("database")
            if bool(own) == bool(other):
                raise ConfigError(f"{where}: give either 'rules' (of this run's own database) or 'database' with 'ruleset'")
            if own:
                unknown = sorted(set(own) - known)
                if unknown:
                    raise ConfigError(f"{where}.rules: {unknown} not listed under 'rules'")
            elif not entry.get("ruleset"):
                raise ConfigError(f"{where}: an arm of another database names its 'ruleset'")
            arms.append(Arm(
                name, tuple(own or ()), other, entry.get("ruleset"),
                as_bool(entry.get("judged", not other), f"{where}.judged"), str(entry.get("description", "")),
            ))
        scenarios = [_scenario(entry, f"{source}.scenarios[{i}]") for i, entry in enumerate(raw["scenarios"] or [])]
        if not arms or not scenarios:
            raise ConfigError(f"{source}: at least one arm and one scenario")
        if len({s.name for s in scenarios}) != len(scenarios):
            raise ConfigError(f"{source}.scenarios: each scenario needs its own name")
        if any(s.purpose for s in scenarios) and not all(s.purpose for s in scenarios):
            raise ConfigError(f"{source}.scenarios: once one scenario says its purpose, every one does (a rule's verdict of record comes from the realistic ones)")
        logging = raw.get("logging") or {}
        check_keys(logging, f"{source}.logging", (), ("trajectory_stride",))
        people = dict(raw.get("people") or {"ages": [25, 70], "genders": ["female", "male"]})
        check_keys(people, f"{source}.people", ("ages", "genders"), ("factors",))
        return cls(
            experiment_name=str(raw["experiment_name"]),
            description=str(raw.get("description", "")),
            rules=tuple(rules),
            left_out=tuple(dict(entry) for entry in (raw.get("left_out") or [])),
            arms=tuple(arms),
            scenarios=tuple(scenarios),
            baseline=str(raw.get("baseline", DEFAULT_BASELINE)),
            seed=int(as_number(raw.get("seed", 0), f"{source}.seed", minimum=0)),
            seeds=int(as_number(raw.get("seeds", 10), f"{source}.seeds", minimum=1)),
            people=people,
            trajectory_stride=int(as_number(logging.get("trajectory_stride", 10), f"{source}.logging.trajectory_stride", minimum=1)),
            alpha=float(as_number(raw.get("alpha", V.ALPHA), f"{source}.alpha", minimum=0.0)),
            verdict_rule=int(as_choice(raw.get("verdict_rule", V.DEFAULT_RULE), f"{source}.verdict_rule", V.RULES)),
            source=source,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_name": self.experiment_name, "description": self.description,
            "rules": {rule.rule_id: {"from": _relative(rule.database), "version": rule.version,
                                     **({"priority": rule.priority, "reason": rule.reason} if rule.priority is not None else {})} for rule in self.rules},
            "left_out": [dict(entry) for entry in self.left_out],
            "arms": [{"name": arm.name, "rules": list(arm.rules), "database": arm.database, "ruleset": arm.ruleset, "judged": arm.judged, "description": arm.description} for arm in self.arms],
            "scenarios": [{"name": s.name, "scenario": s.file, "rotate_people": s.rotate_people, "note": s.note,
                           **({"scenario_overrides": dict(s.overrides)} if s.overrides else {}),
                           **({"population": s.population, "population_sha256": s.profile.sha256} if s.profile else {}),
                           **({"purpose": s.purpose} if s.purpose else {}), **({"pool": s.pool} if s.pool else {}),
                           **({"seeds": s.seeds} if s.seeds else {})} for s in self.scenarios],
            "baseline": self.baseline, "seed": self.seed, "seeds": self.seeds, "people": dict(self.people),
            "trajectory_stride": self.trajectory_stride, "alpha": self.alpha, "verdict_rule": self.verdict_rule,
        }


def _scenario(entry: Any, where: str) -> Scenario:
    check_keys(entry, where, ("name", "scenario"), ("rotate_people", "note", "scenario_overrides", "population", "purpose", "pool", "seeds"))
    rotate = as_bool(entry.get("rotate_people", False), f"{where}.rotate_people")
    purpose = as_choice(entry["purpose"], f"{where}.purpose", P.PURPOSES) if "purpose" in entry else None
    population, profile, pool = entry.get("population"), None, None
    if population is not None:
        profile = P.Profile.load(resolve_path(population))
        if purpose is None:
            raise ConfigError(f"{where}: a scenario with a population says its 'purpose'")
        if purpose != profile.purpose:
            raise ConfigError(f"{where}.purpose: {purpose!r}, but {population} is a {profile.purpose} profile")
        if profile.generator == P.QUOTAS and rotate:
            raise ConfigError(f"{where}: rotate_people is for a cycling mix; a profile of quotas draws new people on every seed")
    if "pool" in entry:
        if profile is None or profile.generator != P.QUOTAS:
            raise ConfigError(f"{where}.pool: only with a population of quotas")
        pool = int(as_number(entry["pool"], f"{where}.pool", minimum=1))
    seeds = int(as_number(entry["seeds"], f"{where}.seeds", minimum=1)) if "seeds" in entry else None
    return Scenario(
        str(entry["name"]), str(entry["scenario"]), rotate, str(entry.get("note", "")), dict(entry.get("scenario_overrides") or {}),
        None if population is None else str(population), profile, purpose, pool, seeds,
    )


# --- the run's own staging database ---------------------------------------------------------------


def assemble(config: RuleSetEvaluationConfig, root: Path) -> list[dict[str, Any]]:
    """Copy each chosen rule's frozen versions into the run's staging database, and write one rule
    set per arm of that database. Returns what was copied, with each source file's hash."""
    staging = StagingDatabase(root)
    if not staging.manifest_path.is_file():
        _write_json(staging.manifest_path, {
            "about": (f"The staging rule database of rule-set evaluation {config.experiment_name} (issue #74, RF-18): copies of "
                      "rules staged by other experiments, byte for byte, and one rule set per arm. Nothing here is in rule_db/ "
                      "unless it is promoted, with a reason."),
            "files": {},
        })
    staging.create()
    copied = []
    for rule in config.rules:
        source = RuleDatabase.load(rule.database, strict=False)
        versions = sorted(r.version for r in source.rules if r.rule_id == rule.rule_id)
        if rule.version not in versions:
            raise ConfigError(f"{rule.rule_id} v{rule.version} is not a loadable rule of {_relative(rule.database)} (it has {versions})")
        for version in range(1, rule.version + 1):
            path = rule.database / "rules" / f"{rule.rule_id}.v{version}.yaml"
            name, _ = staging.copy_in(path, f"copied from {_relative(path)} (RF-18)")
            copied.append({"file": name, "from": _relative(path), "sha256": file_sha256(path)})
        if rule.priority is not None:
            chosen = next(r for r in source.rules if r.rule_id == rule.rule_id and r.version == rule.version)
            written = json.loads(json.dumps(dict(chosen.written)))
            note = (f"RF-18 (issue #74): version {rule.version} with priority {rule.priority} in place of {written['priority']}, "
                    f"nothing else changed. {rule.reason}")
            written.update(version=rule.enabled_version, priority=rule.priority)
            written["provenance"]["notes"] = f"{written['provenance'].get('notes', '')} {note}".strip()
            name, _ = staging.write(written, note)
            copied.append({"file": name, "from": None, "sha256": file_sha256(root / name), "new_version_of": rule.version, "priority": rule.priority})
    for arm in config.arms:
        if arm.rules:
            wanted = {rule.rule_id: rule.enabled_version for rule in config.rules if rule.rule_id in arm.rules}
            staging.write_ruleset(arm.name, wanted, arm.description or f"RF-18 arm {arm.name}")
    forget_rule_database(root)
    RuleDatabase.load(root)  # it must load whole
    return copied


# --- the runs ------------------------------------------------------------------------------------


def people_for(config: RuleSetEvaluationConfig, n_agents: int, repeat: int, rotate: bool) -> dict[int, dict[str, Any]]:
    """The run's people, the same for every arm on a seed. In a crowd, one fixed mix (as crowd
    screening); in a small scenario with ``rotate``, a window on the mix that moves on by one person
    per repeat, so that over the seeds the people differ. One person, not ``n_agents``: the mix gives
    factors in blocks (a cane to four people in a row), so moving on by two would only ever pair
    two people alike, and a rule with roles by a condition would never match."""
    offset = repeat - 1 if rotate else 0
    mixed = mixed_population(offset + n_agents, config.people["ages"], config.people["genders"], config.people.get("factors"))
    return {k: mixed[offset + k] for k in range(n_agents)}


def base_plans(config: RuleSetEvaluationConfig, scenario: Scenario) -> list[AvoidanceRunPlan]:
    return AvoidanceExperiment(
        {
            "layer": "avoidance", "experiment_name": config.experiment_name, "scenario": scenario.file, "baseline": config.baseline,
            "scenario_overrides": dict(scenario.overrides),
            "logging": {"trajectory_stride": config.trajectory_stride, "interactions": True},
            "design": {"seed": config.seed, "seeding": "paired", "repeats": scenario.n_seeds(config.seeds)},
        },
        source=f"<{config.experiment_name}:{scenario.name}>",
    ).plans()


def directives_for(arm: Optional[Arm], staging_root: Path) -> dict[str, Any]:
    if arm is None:
        return {}
    if arm.database is not None:
        return {"provider": "rules", "database": arm.database, "ruleset": arm.ruleset}
    return {"provider": "rules", "database": database_path(staging_root), "ruleset": arm.name}


@dataclass(frozen=True)
class Run:
    scenario: Scenario
    arm: Optional[Arm]
    plan: AvoidanceRunPlan
    folder: Path
    people: Mapping[int, Mapping[str, Any]] = field(default_factory=dict)

    @property
    def arm_name(self) -> str:
        return PLAIN if self.arm is None else self.arm.name


def runs(config: RuleSetEvaluationConfig, experiment_dir: Path) -> list[Run]:
    staging_root = experiment_dir / STAGING_DIR
    visibility = visible_for(4)
    out = []
    for scenario in config.scenarios:
        for plan in base_plans(config, scenario):
            from ..scenarios.registry import build_crowd_scenario

            n_agents = len(build_crowd_scenario(plan.scenario_config).agents)
            if scenario.profile is None:
                given = people_for(config, n_agents, plan.repeat, scenario.rotate_people)
            else:
                given = scenario.profile.people(n_agents, plan.seed, plan.repeat, scenario.rotate_people, scenario.pool)
            people = population_of(given, f"{scenario.name}_r{plan.repeat}")
            for arm in (None, *config.arms):
                name = PLAIN if arm is None else arm.name
                out.append(Run(scenario, arm, replace(
                    plan, run_id=f"{scenario.name}_{name}_s{plan.seed}", population=people, visibility=dict(visibility),
                    directives=directives_for(arm, staging_root),
                ), experiment_dir / RUNS_SUBDIR / scenario.name / name / str(plan.seed), given))
    return out


def execute(run: Run, git: Mapping[str, Any], overwrite: bool = False) -> tuple[dict[str, Any], bool]:
    """Run one simulation unless its measures exist; return its measures and whether it ran."""
    path = run.folder / MEASURES_FILE
    if path.is_file() and not overwrite:
        return json.loads(path.read_text(encoding="utf-8")), False
    started = time.perf_counter()
    execute_avoidance_run(run.plan, run.folder, git)
    wall = time.perf_counter() - started
    measures = run_measures(run.folder)
    measures["wall_s"] = round(wall, 3)
    measures["wall_ms_per_step"] = round(1000.0 * wall / measures["steps"], 3) if measures["steps"] else None
    _write_json(path, {"seed": run.plan.seed, "scenario": run.scenario.name, "arm": run.arm_name, **measures})
    return measures, True


# --- summary and report --------------------------------------------------------------------------


#: Config keys that change only how finished runs are judged, never a run: a change re-judges the
#: runs on disk without running them again.
ANALYSIS_KEYS = ("alpha", "verdict_rule")
KEPT = ("status", "gridlocked", "arrived", "n_agents", "severe_conflicts", "tiers", "collision_episodes", "near_misses",
        "throughput_agents_per_min", "mean_delay_s", "rule_matches", "plans_started", "plans_skipped_busy", "wall_ms_per_step")


def _mean(values: Sequence[Optional[float]]) -> Optional[float]:
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 3) if values else None


def summarise(
    config: RuleSetEvaluationConfig, results: Mapping[tuple[str, str, int], Mapping[str, Any]],
    people: Optional[Mapping[tuple[str, int], Mapping[str, int]]] = None,
) -> dict[str, Any]:
    """Per scenario and arm: the paired seeds, means, the verdict, rule conflicts and uncovered conflicts.
    Since issue #112, a scenario with a population also gets its profile and the people of each seed
    (``people``: counts by scenario and seed, :func:`negsim.populations.counts`), and with purposes a
    rule's verdict of record comes from its realistic scenarios."""
    scenarios = {}
    for scenario in config.scenarios:
        seeds = sorted({seed for (s, _, seed) in results if s == scenario.name})
        plain = [results[(scenario.name, PLAIN, seed)] for seed in seeds]
        arms = {PLAIN: _arm_summary(plain)}
        for arm in config.arms:
            mine = [results[(scenario.name, arm.name, seed)] for seed in seeds]
            entry = _arm_summary(mine)
            paired = [{"seed": seed, "arm": a, "plain": p} for seed, a, p in zip(seeds, mine, plain)]
            entry["verdict"] = V.verdict(paired, config.alpha, config.verdict_rule) if arm.judged else None
            entry["verdict_by_rule"] = {str(rule): V.verdict(paired, config.alpha, rule)["verdict"] for rule in V.RULES} if arm.judged else None
            entry["per_seed"] = [{"seed": seed, "arm": {k: a[k] for k in KEPT}, "plain": {k: p[k] for k in KEPT}} for seed, a, p in zip(seeds, mine, plain)]
            arms[arm.name] = entry
        scenarios[scenario.name] = {"file": scenario.file, "note": scenario.note, "seeds": seeds, "arms": arms}
        if scenario.purpose:
            scenarios[scenario.name]["purpose"] = scenario.purpose
        if scenario.profile:
            per_seed = [{"seed": seed, **people[(scenario.name, seed)]} for seed in seeds] if people else []
            keys = [key for key in (per_seed[0] if per_seed else {}) if key != "seed"]
            scenarios[scenario.name]["population"] = {
                **scenario.profile.describe(), **({"pool": scenario.pool} if scenario.pool else {}),
                "mean_per_seed": {key: _mean([row[key] for row in per_seed]) for key in keys}, "per_seed": per_seed,
            }
    purposes = {s.purpose for s in config.scenarios if s.purpose}
    rule_verdicts = {}
    for rule in config.rules:
        alone = next((arm for arm in config.arms if arm.rules == (rule.rule_id,) and arm.judged), None)
        if alone is None:
            continue
        by_scenario = {name: s["arms"][alone.name]["verdict"]["verdict"] for name, s in scenarios.items()}
        entry = {"arm": alone.name, "by_scenario": by_scenario, "overall": overall(by_scenario.values())}
        if purposes:
            # The user's decision of 2026-10-27 (issue #112): the verdict of record comes from the
            # realistic scenarios; a stress scenario's is reported beside it, never on its own.
            entry["by_purpose"] = {purpose: overall([v for name, v in by_scenario.items() if scenarios[name]["purpose"] == purpose])
                                   for purpose in P.PURPOSES if purpose in purposes}
            entry["overall"] = entry["by_purpose"].get(P.REALISTIC)
            entry["of_record_from"] = P.REALISTIC
            # The user's decision of 2026-10-27 (issue #112): a rule that harms where its factor is
            # common, but not in a realistic crowd, is flagged for RF-14 (and its successors).
            entry["flag"] = HARMS_WHERE_COMMON if entry["by_purpose"].get(P.STRESS) == V.HARMS and entry["overall"] != V.HARMS else None
        rule_verdicts[rule.rule_id] = entry
    return {"scenarios": scenarios, "rule_verdicts": rule_verdicts}


#: A rule's flag: it harms in a stress scenario, but its verdict of record does not (issue #112).
HARMS_WHERE_COMMON = "harms_where_common"


def overall(verdicts: Sequence[str]) -> str:
    """**[design]** A rule's reading over the scenarios: harms anywhere, then helps somewhere, then
    a trade-off somewhere, then no change somewhere, else not used."""
    verdicts = list(verdicts)
    for outcome in (V.HARMS, V.HELPS, V.TRADE_OFF, V.NO_CHANGE):
        if outcome in verdicts:
            return outcome
    return V.NOT_USED


def _arm_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    uncovered: Counter = Counter()
    for row in rows:
        for entry in row["uncovered"]:
            uncovered[(entry["encounter_class"], entry["tier"])] += entry["pairs"]
    lanes = [row["lanes"] for row in rows if row.get("lanes")]
    return {
        "means": {key: _mean([row[key] for row in rows]) for key in (
            "severe_conflicts", "collision_episodes", "near_misses", "throughput_agents_per_min", "mean_delay_s", "rule_matches", "wall_ms_per_step")},
        "gridlocked_runs": sum(row["gridlocked"] for row in rows),
        "lanes": {"share_left": _mean([l["share_left"] for l in lanes]), "share_right": _mean([l["share_right"] for l in lanes]),
                  "mean_offset_to_own_left_m": _mean([l["mean_offset_to_own_left_m"] for l in lanes])} if lanes else None,
        "rule_conflicts": {key: sum(row[key] for row in rows) for key in (
            "pairs_matched_by_several_rules", "ambiguous_matches", "cross_pair_conflicts", "formation_mismatches", "plans_started", "plans_skipped_busy")},
        "matches_by_rule": dict(sum((Counter(row["matches_by_rule"]) for row in rows), Counter())),
        "uncovered": [{"encounter_class": cls, "tier": tier, "pairs": n} for (cls, tier), n in sorted(uncovered.items(), key=lambda item: (-item[1], item[0]))],
    }


def _cell(entry: Mapping[str, Any], rule: int) -> str:
    """The verdict in force, and any other rule's that differs from it."""
    others = [f"rule {r}: {v}" for r, v in (entry.get("verdict_by_rule") or {}).items() if int(r) != rule and v != entry["verdict"]["verdict"]]
    return entry["verdict"]["verdict"] + (f" ({'; '.join(others)})" if others else "")


def _num(value: Any) -> str:
    return "–" if value is None else (f"{value:g}" if isinstance(value, (int, float)) else str(value))


def report_markdown(config: RuleSetEvaluationConfig, summary: Mapping[str, Any], copied: Sequence[Mapping[str, Any]]) -> str:
    lines = [f"# {config.experiment_name}: the rule set against plain ORCA", "",
             "Machine-written by `negsim.ruleset_eval` (issue #74, RF-18). Method: `docs/rule-set-evaluation.md`. "
             + (f"{config.seeds} paired seeds per scenario" if not any(s.seeds for s in config.scenarios) else
                "paired seeds per scenario: " + ", ".join(f"{s.name} {s.n_seeds(config.seeds)}" for s in config.scenarios))
             + f", baseline `{config.baseline}`, sign test at p < {config.alpha:g}, "
             f"verdict rule {config.verdict_rule} (`docs/rule-set-evaluation.md`, section 3).", ""]
    lines += ["## Rules", "", "| Rule | From | Version |", "| --- | --- | --- |"]
    lines += [f"| `{rule.rule_id}` | `{_relative(rule.database)}` | {rule.version} |" for rule in config.rules]
    if config.left_out:
        lines += ["", f"**Left out ({len(config.left_out)}):**", ""]
        lines += [f"- `{entry.get('rule')}`: {entry.get('reason')}" for entry in config.left_out]
    lines += ["", "## Verdicts", "", "| Scenario | " + " | ".join(f"`{arm.name}`" for arm in config.arms if arm.judged) + " |",
              "| --- |" + " --- |" * sum(arm.judged for arm in config.arms)]
    for name, s in summary["scenarios"].items():
        label = f"{name} ({s['purpose']})" if s.get("purpose") else name
        lines.append(f"| {label} | " + " | ".join(_cell(s["arms"][arm.name], config.verdict_rule) for arm in config.arms if arm.judged) + " |")
    if summary["rule_verdicts"]:
        by_purpose = [p for p in P.PURPOSES if any(p in (e.get("by_purpose") or {}) for e in summary["rule_verdicts"].values())]
        extra = "".join(f" {p.capitalize()} |" for p in by_purpose)
        record = "Of record (realistic)" if by_purpose else "Overall"
        flag = " Flag |" if by_purpose else ""
        lines += ["", "| Rule | Arm | " + " | ".join(summary["scenarios"]) + f" |{extra} {record} |{flag}",
                  "| --- | --- |" + " --- |" * (len(summary["scenarios"]) + len(by_purpose) + 1 + bool(by_purpose))]
        for rule_id, entry in summary["rule_verdicts"].items():
            cells = "".join(f" {_num((entry.get('by_purpose') or {}).get(p))} |" for p in by_purpose)
            flagged = f" {_num(entry.get('flag'))} |" if by_purpose else ""
            lines.append(f"| `{rule_id}` | `{entry['arm']}` | " + " | ".join(entry["by_scenario"].values()) + f" |{cells} **{_num(entry['overall'])}** |{flagged}")
        if by_purpose:
            lines += ["", "A rule's verdict of record comes from its realistic scenarios; a stress scenario shows whether it works where it "
                      "applies, and is never a verdict of record on its own (the user's decision of 2026-10-27, issue #112). "
                      f"`{HARMS_WHERE_COMMON}`: the rule harms in a stress scenario but not by its verdict of record, flagged for RF-14 "
                      "(the user's decision of 2026-10-27)."]
    for name, s in summary["scenarios"].items():
        lines += ["", f"## {name}", "", f"`{s['file']}`" + (f". {s['note']}" if s["note"] else ""), ""]
        if s.get("population"):
            pop = s["population"]
            mean = ", ".join(f"{k} {_num(v)}" for k, v in pop["mean_per_seed"].items())
            lines += [f"People: `{pop['file']}` ({pop['purpose']}, {pop['generator']}"
                      + (f", the first of a crowd of {pop['pool']} at exact shares" if pop.get("pool") else "") + f"). Per seed, mean: {mean}.", ""]
        lines += ["| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for arm_name, entry in s["arms"].items():
            m, lanes = entry["means"], entry["lanes"]
            lines.append(f"| `{arm_name}` | {_num(m['severe_conflicts'])} | {_num(m['collision_episodes'])} | {_num(m['throughput_agents_per_min'])} | "
                         f"{_num(m['mean_delay_s'])} | {entry['gridlocked_runs']} of {len(s['seeds'])} | {_num(m['rule_matches'])} | {_num(m['wall_ms_per_step'])} | "
                         + (f"{_num(lanes['share_left'])} / {_num(lanes['share_right'])}" if lanes else "–") + " |")
        lines += ["", "Means over the seeds. Tests (better / worse / tied seeds, p):", ""]
        for arm_name, entry in s["arms"].items():
            if entry.get("verdict"):
                v = entry["verdict"]
                tests = "; ".join(f"{k} {t['better']}/{t['worse']}/{t['ties']}, p = {t['p']:.3g}" for k, t in v["tests"].items())
                lines.append(f"- `{arm_name}`: **{v['verdict']}** ({'; '.join(v['reasons'])}). {tests}.")
        for arm_name, entry in s["arms"].items():
            if arm_name != PLAIN and entry["uncovered"]:
                top = ", ".join(f"{u['encounter_class']} {u['tier']}: {u['pairs']}" for u in entry["uncovered"][:6])
                lines.append(f"- Uncovered conflicts under `{arm_name}` (pairs, all seeds; most frequent first): {top}.")
                conflicts = entry["rule_conflicts"]
                lines.append(f"  Rule conflicts: {conflicts['pairs_matched_by_several_rules']} pairs matched by several rules, "
                             f"{conflicts['ambiguous_matches']} ambiguous matches, {conflicts['cross_pair_conflicts']} cross-pair conflicts; "
                             f"plans started {conflicts['plans_started']}, not started because one was in force {conflicts['plans_skipped_busy']}.")
    lines += ["", f"Copied into the run's own staging database: {len(copied)} rule file(s), byte for byte (`rule_db_staging/MANIFEST.json`).", ""]
    return "\n".join(lines)


def _runs_part(described: Mapping[str, Any]) -> dict[str, Any]:
    """What of a config decides the runs (everything but ``ANALYSIS_KEYS``)."""
    return {key: value for key, value in described.items() if key not in ANALYSIS_KEYS}


def _seeds_of(described: Mapping[str, Any]) -> dict[str, int]:
    """How many seeds each scenario of a described config has."""
    default = described.get("seeds", 10)
    return {s["name"]: s.get("seeds", default) for s in described.get("scenarios", [])}


def _without_seeds(described: Mapping[str, Any]) -> dict[str, Any]:
    """The runs part without the numbers of seeds. A run on a given seed does not depend on how
    many seeds there are (its people depend on the seed alone), so a folder may take more seeds
    and keep the runs it has (issue #112)."""
    part = {key: value for key, value in _runs_part(described).items() if key != "seeds"}
    part["scenarios"] = [{k: v for k, v in s.items() if k != "seeds"} for s in part.get("scenarios", [])]
    return part


@dataclass
class EvaluationResult:
    experiment_dir: Path
    executed: int = 0
    skipped: int = 0
    summary: Optional[dict[str, Any]] = None


def run_evaluation(
    config: RuleSetEvaluationConfig, out_root: Optional[Path | str] = None, overwrite: bool = False,
    report: Callable[[str], None] = print, git: Optional[Mapping[str, Any]] = None,
) -> EvaluationResult:
    experiment_dir = Path(out_root if out_root is not None else RUNS_DIR) / config.experiment_name
    result = EvaluationResult(experiment_dir)
    if git is None:
        from ..experiment.batch import git_state

        git = git_state()
    experiment_dir.mkdir(parents=True, exist_ok=True)
    config_path = experiment_dir / "config.json"
    described = {"layer": LAYER, "schema_version": SCHEMA_VERSION, "experiment": config.as_dict(), "software": {"negsim": __version__}}
    created, first_git, seeds_changed = _utc_now(), dict(git), []
    if config_path.is_file():
        before = json.loads(config_path.read_text(encoding="utf-8"))
        if _without_seeds(before.get("experiment") or {}) != _without_seeds(described["experiment"]) and any((experiment_dir / RUNS_SUBDIR).rglob(MEASURES_FILE)) and not overwrite:
            raise ConfigError(f"{experiment_dir}: it holds runs made with another config; give it a new experiment_name, or --overwrite")
        if not overwrite:
            created, first_git = before.get("created_utc", created), before.get("git", first_git)
            seeds_changed = list(before.get("seeds_changed") or [])
            if _seeds_of(before.get("experiment") or {}) != _seeds_of(described["experiment"]):
                seeds_changed.append({"utc": _utc_now(), "git": dict(git), "from": _seeds_of(before.get("experiment") or {}),
                                      "to": _seeds_of(described["experiment"])})
    copied = assemble(config, experiment_dir / STAGING_DIR)
    # ``git`` is the commit the runs were made with; ``judged_git`` the one that last judged them; ``seeds_changed``
    # each time the numbers of seeds changed (the runs added then record their own commit in their config.json).
    _write_json(config_path, {**described, "created_utc": created, "git": first_git, "judged_utc": _utc_now(), "judged_git": dict(git), "copied": copied,
                              **({"seeds_changed": seeds_changed} if seeds_changed else {})})
    planned = runs(config, experiment_dir)
    people = {(run.scenario.name, run.plan.seed): P.counts(run.people) for run in planned if run.scenario.profile is not None}
    results = {}
    for i, run in enumerate(planned, 1):
        measures, ran = execute(run, git, overwrite)
        result.executed += ran
        result.skipped += not ran
        results[(run.scenario.name, run.arm_name, run.plan.seed)] = measures
        if ran:
            report(f"  [{i}/{len(planned)}] {run.scenario.name} {run.arm_name} seed {run.plan.seed}: {measures['status']}, "
                   f"severe {measures['severe_conflicts']}, {measures['wall_s']:.1f} s")
    summary = summarise(config, results, people)
    result.summary = summary
    _write_json(experiment_dir / "summary.json", {"experiment": config.experiment_name, "written_utc": _utc_now(), **summary})
    (experiment_dir / "report.md").write_text(report_markdown(config, summary, copied), encoding="utf-8", newline="\n")
    return result


def print_plan(config: RuleSetEvaluationConfig, out: Callable[[str], None] = print) -> None:
    arms = [PLAIN, *(arm.name for arm in config.arms)]
    total = sum(len(arms) * s.n_seeds(config.seeds) for s in config.scenarios)
    seeds = f"{config.seeds} seed(s)" if not any(s.seeds for s in config.scenarios) else "the scenario's seeds"
    out(f"{config.experiment_name}: rule-set evaluation, {len(config.scenarios)} scenario(s) x {len(arms)} arm(s) x {seeds} "
        f"= {total} run(s); no model calls, cost USD 0")
    for rule in config.rules:
        out(f"  rule {rule.rule_id} v{rule.version} from {_relative(rule.database)}")
    for arm in config.arms:
        what = ", ".join(arm.rules) if arm.rules else f"{arm.database}:{arm.ruleset}"
        out(f"  arm {arm.name}: {what}{'' if arm.judged else ' (reference, not judged)'}")
    for scenario in config.scenarios:
        people = f", people {scenario.population}" + (f" (the first of {scenario.pool})" if scenario.pool else "") if scenario.population else ""
        out(f"  scenario {scenario.name}: {scenario.file}{' (people rotate over the seeds)' if scenario.rotate_people else ''}"
            f"{people}{f', {scenario.purpose}' if scenario.purpose else ''}{f', {scenario.seeds} seeds' if scenario.seeds else ''}")


def cli_run(args: argparse.Namespace) -> int:
    """What ``run_experiment.py`` does with a config that says ``layer: rule_set_evaluation``."""
    try:
        if args.client:
            raise ConfigError(f"{args.config} is a rule-set evaluation, which calls no model; --client does not apply to it")
        config = RuleSetEvaluationConfig.load(args.config)
        print_plan(config)
        if args.plan:
            return 0
        result = run_evaluation(config, out_root=args.out, overwrite=args.overwrite)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"done: {result.executed} run(s) executed, {result.skipped} already done, cost USD 0")
    print(f"logs: {result.experiment_dir}")
    return 0
