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
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from .. import __version__
from ..configutil import PACKAGE_ROOT, ConfigError, as_bool, as_number, check_keys, load_yaml, resolve_path
from ..experiment.avoidance import AvoidanceExperiment, AvoidanceRunPlan, execute_avoidance_run, forget_rule_database
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
    source: str = "<config>"

    @classmethod
    def load(cls, path: Path | str) -> "RuleSetEvaluationConfig":
        resolved = resolve_path(path)
        return cls.from_raw(load_yaml(resolved), str(path))

    @classmethod
    def from_raw(cls, raw: Any, source: str = "<config>") -> "RuleSetEvaluationConfig":
        check_keys(
            raw, source, ("layer", "experiment_name", "rules", "arms", "scenarios"),
            ("schema_version", "description", "left_out", "baseline", "seed", "seeds", "people", "logging", "alpha"),
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
        scenarios = []
        for i, entry in enumerate(raw["scenarios"] or []):
            where = f"{source}.scenarios[{i}]"
            check_keys(entry, where, ("name", "scenario"), ("rotate_people", "note"))
            scenarios.append(Scenario(str(entry["name"]), str(entry["scenario"]), as_bool(entry.get("rotate_people", False), f"{where}.rotate_people"), str(entry.get("note", ""))))
        if not arms or not scenarios:
            raise ConfigError(f"{source}: at least one arm and one scenario")
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
            source=source,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_name": self.experiment_name, "description": self.description,
            "rules": {rule.rule_id: {"from": _relative(rule.database), "version": rule.version,
                                     **({"priority": rule.priority, "reason": rule.reason} if rule.priority is not None else {})} for rule in self.rules},
            "left_out": [dict(entry) for entry in self.left_out],
            "arms": [{"name": arm.name, "rules": list(arm.rules), "database": arm.database, "ruleset": arm.ruleset, "judged": arm.judged, "description": arm.description} for arm in self.arms],
            "scenarios": [{"name": s.name, "scenario": s.file, "rotate_people": s.rotate_people, "note": s.note} for s in self.scenarios],
            "baseline": self.baseline, "seed": self.seed, "seeds": self.seeds, "people": dict(self.people),
            "trajectory_stride": self.trajectory_stride, "alpha": self.alpha,
        }


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
            "logging": {"trajectory_stride": config.trajectory_stride, "interactions": True},
            "design": {"seed": config.seed, "seeding": "paired", "repeats": config.seeds},
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
            people = population_of(people_for(config, n_agents, plan.repeat, scenario.rotate_people), f"{scenario.name}_r{plan.repeat}")
            for arm in (None, *config.arms):
                name = PLAIN if arm is None else arm.name
                out.append(Run(scenario, arm, replace(
                    plan, run_id=f"{scenario.name}_{name}_s{plan.seed}", population=people, visibility=dict(visibility),
                    directives=directives_for(arm, staging_root),
                ), experiment_dir / RUNS_SUBDIR / scenario.name / name / str(plan.seed)))
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


KEPT = ("status", "gridlocked", "arrived", "n_agents", "severe_conflicts", "collision_episodes", "near_misses",
        "throughput_agents_per_min", "mean_delay_s", "rule_matches", "plans_started", "plans_skipped_busy", "wall_ms_per_step")


def _mean(values: Sequence[Optional[float]]) -> Optional[float]:
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 3) if values else None


def summarise(config: RuleSetEvaluationConfig, results: Mapping[tuple[str, str, int], Mapping[str, Any]]) -> dict[str, Any]:
    """Per scenario and arm: the paired seeds, means, the verdict, rule conflicts and uncovered conflicts."""
    scenarios = {}
    for scenario in config.scenarios:
        seeds = sorted({seed for (s, _, seed) in results if s == scenario.name})
        plain = [results[(scenario.name, PLAIN, seed)] for seed in seeds]
        arms = {PLAIN: _arm_summary(plain)}
        for arm in config.arms:
            mine = [results[(scenario.name, arm.name, seed)] for seed in seeds]
            entry = _arm_summary(mine)
            paired = [{"seed": seed, "arm": a, "plain": p} for seed, a, p in zip(seeds, mine, plain)]
            entry["verdict"] = V.verdict(paired, config.alpha) if arm.judged else None
            entry["per_seed"] = [{"seed": seed, "arm": {k: a[k] for k in KEPT}, "plain": {k: p[k] for k in KEPT}} for seed, a, p in zip(seeds, mine, plain)]
            arms[arm.name] = entry
        scenarios[scenario.name] = {"file": scenario.file, "note": scenario.note, "seeds": seeds, "arms": arms}
    rule_verdicts = {}
    for rule in config.rules:
        alone = next((arm for arm in config.arms if arm.rules == (rule.rule_id,) and arm.judged), None)
        if alone is None:
            continue
        by_scenario = {name: s["arms"][alone.name]["verdict"]["verdict"] for name, s in scenarios.items()}
        rule_verdicts[rule.rule_id] = {"arm": alone.name, "by_scenario": by_scenario, "overall": overall(by_scenario.values())}
    return {"scenarios": scenarios, "rule_verdicts": rule_verdicts}


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


def _num(value: Any) -> str:
    return "–" if value is None else (f"{value:g}" if isinstance(value, (int, float)) else str(value))


def report_markdown(config: RuleSetEvaluationConfig, summary: Mapping[str, Any], copied: Sequence[Mapping[str, Any]]) -> str:
    lines = [f"# {config.experiment_name}: the rule set against plain ORCA", "",
             "Machine-written by `negsim.ruleset_eval` (issue #74, RF-18). Method: `docs/rule-set-evaluation.md`. "
             f"{config.seeds} paired seeds per scenario, baseline `{config.baseline}`, sign test at p < {config.alpha:g}.", ""]
    lines += ["## Rules", "", "| Rule | From | Version |", "| --- | --- | --- |"]
    lines += [f"| `{rule.rule_id}` | `{_relative(rule.database)}` | {rule.version} |" for rule in config.rules]
    if config.left_out:
        lines += ["", f"**Left out ({len(config.left_out)}):**", ""]
        lines += [f"- `{entry.get('rule')}`: {entry.get('reason')}" for entry in config.left_out]
    lines += ["", "## Verdicts", "", "| Scenario | " + " | ".join(f"`{arm.name}`" for arm in config.arms if arm.judged) + " |",
              "| --- |" + " --- |" * sum(arm.judged for arm in config.arms)]
    for name, s in summary["scenarios"].items():
        lines.append(f"| {name} | " + " | ".join(s["arms"][arm.name]["verdict"]["verdict"] for arm in config.arms if arm.judged) + " |")
    if summary["rule_verdicts"]:
        lines += ["", "| Rule | Arm | " + " | ".join(summary["scenarios"]) + " | Overall |", "| --- | --- |" + " --- |" * (len(summary["scenarios"]) + 1)]
        for rule_id, entry in summary["rule_verdicts"].items():
            lines.append(f"| `{rule_id}` | `{entry['arm']}` | " + " | ".join(entry["by_scenario"].values()) + f" | **{entry['overall']}** |")
    for name, s in summary["scenarios"].items():
        lines += ["", f"## {name}", "", f"`{s['file']}`" + (f". {s['note']}" if s["note"] else ""), "",
                  "| Arm | Severe conflicts | Collisions | Throughput /min | Delay s | Gridlocked | Rule matches | ms/step | Left / right |",
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
    if config_path.is_file():
        before = json.loads(config_path.read_text(encoding="utf-8"))
        if before.get("experiment") != described["experiment"] and any((experiment_dir / RUNS_SUBDIR).rglob(MEASURES_FILE)) and not overwrite:
            raise ConfigError(f"{experiment_dir}: it holds runs made with another config; give it a new experiment_name, or --overwrite")
    copied = assemble(config, experiment_dir / STAGING_DIR)
    _write_json(config_path, {**described, "created_utc": _utc_now(), "git": dict(git), "copied": copied})
    planned = runs(config, experiment_dir)
    results = {}
    for i, run in enumerate(planned, 1):
        measures, ran = execute(run, git, overwrite)
        result.executed += ran
        result.skipped += not ran
        results[(run.scenario.name, run.arm_name, run.plan.seed)] = measures
        if ran:
            report(f"  [{i}/{len(planned)}] {run.scenario.name} {run.arm_name} seed {run.plan.seed}: {measures['status']}, "
                   f"severe {measures['severe_conflicts']}, {measures['wall_s']:.1f} s")
    summary = summarise(config, results)
    result.summary = summary
    _write_json(experiment_dir / "summary.json", {"experiment": config.experiment_name, "written_utc": _utc_now(), **summary})
    (experiment_dir / "report.md").write_text(report_markdown(config, summary, copied), encoding="utf-8", newline="\n")
    return result


def print_plan(config: RuleSetEvaluationConfig, out: Callable[[str], None] = print) -> None:
    arms = [PLAIN, *(arm.name for arm in config.arms)]
    out(f"{config.experiment_name}: rule-set evaluation, {len(config.scenarios)} scenario(s) x {len(arms)} arm(s) x {config.seeds} seed(s) "
        f"= {len(config.scenarios) * len(arms) * config.seeds} run(s); no model calls, cost USD 0")
    for rule in config.rules:
        out(f"  rule {rule.rule_id} v{rule.version} from {_relative(rule.database)}")
    for arm in config.arms:
        what = ", ".join(arm.rules) if arm.rules else f"{arm.database}:{arm.ruleset}"
        out(f"  arm {arm.name}: {what}{'' if arm.judged else ' (reference, not judged)'}")
    for scenario in config.scenarios:
        out(f"  scenario {scenario.name}: {scenario.file}{' (people rotate over the seeds)' if scenario.rotate_people else ''}")


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
