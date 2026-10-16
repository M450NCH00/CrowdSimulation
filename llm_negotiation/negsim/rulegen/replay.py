"""Single-rule replay and crowd screening of generated rules (issue #30, Part 9).

**Replay.** One generated rule is switched on, alone, with plain ORCA for every pair it does
not match, and run on its case's own scenario: the very run the case was taken from, rebuilt
from its experiment config, on the same seed (paired seeds, ``docs/baseline.md`` section 6),
with the people of the session that produced the rule. The same run with no rule is run
beside it, and is checked to reproduce what the case recorded of the baseline. Generated rules
are never switched on together (a decision of the issue), so no two of them can clash. The
result is recorded, with no pass mark.

**Crowd screening.** The rule is switched on, alone, in the two-way flow (``bidirectional_flow``),
on the primary baseline, for a few seeds, each beside the same flow with no rule. Recorded:
deadlock, collisions and throughput against the baseline. **A rule that gridlocks the flow**
(a run that ends in deadlock or at its time limit with people still walking, on a seed on
which the baseline did neither) **fails screening.** It is marked, never deleted.

Both results go into the rule's ``screening`` block, as the next version of the staged rule.
Run folders are laid out short (``replay/<rule_id>/baseline``, ``replay/<rule_id>/rule``,
``screening/baseline/<run>``, ``screening/<rule_id>/<run>``): Windows refuses a path longer
than 260 characters.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import PACKAGE_ROOT, ConfigError, as_number, check_keys, load_yaml
from ..experiment.avoidance import AvoidanceExperiment, AvoidanceRunPlan, execute_avoidance_run, forget_rule_database
from ..rules.canonical import canonical_hash
from ..rules.model import Rule
from ..runlog.schema import PAIR_INTERACTIONS_FILE
from .cases import text_sha256

KIND_REPLAY, KIND_CROWD = "replay", "crowd"
KINDS = (KIND_REPLAY, KIND_CROWD)
GRIDLOCK_STATUSES = ("deadlock", "timeout")
FLOW_SCENARIO = "configs/scenarios/bidirectional_flow.yaml"


def database_path(root: Path) -> str:
    """How a run's config names a staging database: under ``llm_negotiation/`` if it is there
    (so that committed logs carry no machine's own folders), else in full."""
    try:
        return Path(root).resolve().relative_to(PACKAGE_ROOT).as_posix()
    except ValueError:
        return Path(root).resolve().as_posix()


class ReplayError(ConfigError):
    """A replay or a screening that cannot be run as asked."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def find_source_config(experiment_name: str, root: Path = PACKAGE_ROOT / "configs") -> Path:
    """The avoidance experiment config whose ``experiment_name`` a case's source run names."""
    found = []
    for path in sorted(root.rglob("*.yaml")):
        try:
            raw = load_yaml(path)
        except ConfigError:
            continue
        if isinstance(raw, Mapping) and raw.get("layer") == "avoidance" and raw.get("experiment_name") == experiment_name:
            found.append(path)
    if len(found) != 1:
        raise ReplayError(f"expected one experiment config named {experiment_name!r} under {root}, found {len(found)}")
    return found[0]


def source_plan(case: Mapping[str, Any]) -> AvoidanceRunPlan:
    """The plan of the run a case came from, rebuilt from its config, and checked to be that run."""
    source = case["source"]
    experiment = AvoidanceExperiment.load(find_source_config(source["experiment"]))
    plans = [plan for plan in experiment.plans() if plan.run_id == source["run_id"]]
    if len(plans) != 1:
        raise ReplayError(f"{source['experiment']} has no run {source['run_id']!r}")
    plan = plans[0]
    if plan.seed != source["seed"]:
        raise ReplayError(f"{source['experiment']}/{source['run_id']}: the config now gives seed {plan.seed}, the case was taken on {source['seed']}")
    from ..scenarios.registry import build_crowd_scenario

    resolved = build_crowd_scenario(plan.scenario_config).as_dict()
    if text_sha256(json.dumps(resolved, sort_keys=True)) != case["scenario"]["resolved_sha256"]:
        raise ReplayError(f"{source['experiment']}/{source['run_id']}: the scenario its config now gives is not the one the case was taken from")
    return plan


def population_of(personas: Mapping[int, Mapping[str, Any]], label: str) -> dict[int, dict[str, Any]]:
    """Personas for an avoidance run: age and gender, nothing else (a task is never seen)."""
    return {
        int(agent): {"persona_id": f"{label}:{agent}", "attributes": {"age": person["age"], "gender": person["gender"]}}
        for agent, person in personas.items()
    }


def _run_numbers(outcome: Mapping[str, Any]) -> dict[str, Any]:
    collisions = outcome["collisions"]
    arrived, elapsed = outcome["arrived"], outcome["sim_time_s"]
    return {
        "status": outcome["status"],
        "gridlocked": outcome["status"] in GRIDLOCK_STATUSES,
        "arrived": arrived,
        "n_agents": outcome["n_agents"],
        "sim_time_s": elapsed,
        "makespan_s": outcome["makespan_s"],
        "mean_time_to_goal_s": outcome["totals"]["mean_time_to_goal_s"],
        "throughput_agents_per_min": round(60.0 * arrived / elapsed, 4) if elapsed else None,
        "collision_episodes": collisions["agent_agent"] + collisions["agent_wall"],
        "max_overlap_m": collisions["max_overlap_m"],
        "near_misses": outcome["totals"]["near_misses"],
        "yield_events": outcome["totals"]["yield_events"],
        "pair_exposure_time_s": outcome["totals"].get("pair_exposure_time_s"),
        "tiers": (outcome.get("interaction_outcomes") or {}).get("tiers"),
        "rule_fired": sum(((outcome.get("rules") or {}).get("matches_begun") or {}).values()),
    }


def _pair_numbers(run_dir: Path, agents: Sequence[int], formed_step: int) -> Optional[dict[str, Any]]:
    """The case's pair in a run: of the pair interactions of its two agents (in a crowd they can
    meet more than once), the one that formed nearest the step the case's pair formed."""
    found = [pair for pair in _read_jsonl(run_dir / PAIR_INTERACTIONS_FILE) if pair["agents"] == list(agents)]
    if not found:
        return None
    pair = min(found, key=lambda entry: (abs(entry["start_step"] - formed_step), entry["start_step"]))
    matches = (pair.get("rules") or {}).get("matches") or []
    return {
        "pair_id": pair["pair_id"],
        "start_step": pair["start_step"],
        "interactions_of_the_two": len(found),
        "severity_tier": pair["severity_tier"],
        "category": pair["outcome"],
        "pair_exposure_time_s": pair["pair_exposure_time_s"],
        "min_separation_m": pair["min_separation_m"],
        "yield_events": pair["tier_detail"]["yield_events"],
        "near_misses": pair["tier_detail"]["near_misses"],
        "rule_matched": bool(matches),
        "roles": matches[0]["roles"] if matches else None,
    }


def reproduces_case(pair: Optional[Mapping[str, Any]], case: Mapping[str, Any]) -> bool:
    """Whether a replayed baseline gave the case's pair what the case recorded of it."""
    recorded = case["baseline_outcome"]
    return pair is not None and pair["start_step"] == case["formation"]["step"] and all(
        pair[key] == recorded[key] for key in ("severity_tier", "pair_exposure_time_s", "min_separation_m")
    )


def _directives(rule: Rule, staging_root: Path) -> dict[str, Any]:
    return {"provider": "rules", "database": database_path(staging_root), "enable": {rule.rule_id: rule.version}}


def replay(
    rule: Rule,
    staging_root: Path,
    case: Mapping[str, Any],
    personas: Mapping[int, Mapping[str, Any]],
    visibility: Mapping[str, bool],
    out_dir: Path,
    experiment: str,
    git: Mapping[str, Any],
    where: str = "",
) -> dict[str, Any]:
    """Replay one rule alone on its case's scenario and seed, beside the baseline: a screening
    entry. ``out_dir`` gets the two run folders; ``where`` is how the entry names it."""
    forget_rule_database(staging_root)
    plan = source_plan(case)
    common = dict(experiment_name=experiment, population=population_of(personas, rule.rule_id), visibility=dict(visibility))
    runs = {
        "baseline": replace(plan, run_id=f"{rule.rule_id}_baseline", directives={}, **common),
        "rule": replace(plan, run_id=f"{rule.rule_id}_v{rule.version}", directives=_directives(rule, staging_root), **common),
    }
    results: dict[str, Any] = {"run": {}, "pair": {}, "folders": {}}
    for name, run_plan in runs.items():
        outcome = execute_avoidance_run(run_plan, out_dir / name, git)
        results["run"][name] = _run_numbers(outcome)
        results["pair"][name] = _pair_numbers(out_dir / name, case["agents"], case["formation"]["step"])
        results["folders"][name] = f"{where}/{name}" if where else name
    results["rule_matched_the_case_pair"] = bool((results["pair"]["rule"] or {}).get("rule_matched"))
    results["baseline_reproduces_case"] = reproduces_case(results["pair"]["baseline"], case)
    reasons = []
    if not results["baseline_reproduces_case"]:
        reasons.append("the replayed baseline did not reproduce the case's pair as the case recorded it")
    return {
        "kind": KIND_REPLAY,
        "experiment": experiment,
        "scenario": case["scenario"]["type"],
        "baseline": None if plan.baseline is None else plan.baseline.name,
        "case_id": case["case_id"],
        "seeds": [plan.seed],
        "screened_utc": _utc_now(),
        "verdict": "recorded",
        "reasons": reasons,
        "results": results,
    }


@dataclass(frozen=True)
class ScreeningSettings:
    """Where and how a rule is screened in a crowd."""

    scenario: str = FLOW_SCENARIO
    baseline: str = "orca_perturbed_v1"
    seed: int = 30900
    repeats: int = 2
    scenario_overrides: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_config(cls, raw: Any, where: str = "screening") -> "ScreeningSettings":
        check_keys(raw, where, (), ("enabled", "scenario", "baseline", "seed", "repeats", "scenario_overrides"))
        return cls(
            scenario=str(raw.get("scenario", FLOW_SCENARIO)),
            baseline=str(raw.get("baseline", "orca_perturbed_v1")),
            seed=int(as_number(raw.get("seed", 30900), f"{where}.seed", minimum=0)),
            repeats=int(as_number(raw.get("repeats", 2), f"{where}.repeats", minimum=1)),
            scenario_overrides=dict(raw.get("scenario_overrides") or {}),
        )

    def as_dict(self) -> dict[str, Any]:
        return {"scenario": self.scenario, "baseline": self.baseline, "seed": self.seed, "repeats": self.repeats, "scenario_overrides": dict(self.scenario_overrides)}


def crowd_plans(settings: ScreeningSettings, experiment: str) -> list[AvoidanceRunPlan]:
    """The screening runs with no rule, one per repeat, on paired seeds."""
    config = AvoidanceExperiment(
        {
            "layer": "avoidance",
            "experiment_name": experiment,
            "scenario": settings.scenario,
            "baseline": settings.baseline,
            "scenario_overrides": dict(settings.scenario_overrides),
            "logging": {"trajectory_stride": 10},
            "design": {"seed": settings.seed, "seeding": "paired", "repeats": settings.repeats},
        },
        source="<screening>",
    )
    return config.plans()


def mixed_population(n_agents: int, ages: Sequence[int], genders: Sequence[str]) -> dict[int, dict[str, Any]]:
    """Ages and genders for a crowd, so that a rule that reads them can apply: agent ``k`` gets
    ``ages[k % len(ages)]`` and ``genders[(k // len(ages)) % len(genders)]``."""
    return {
        agent: {"age": ages[agent % len(ages)], "gender": genders[(agent // len(ages)) % len(genders)]}
        for agent in range(n_agents)
    }


def crowd_size(settings: ScreeningSettings) -> int:
    """How many agents the screening crowd has."""
    from ..scenarios.registry import build_crowd_scenario

    return len(build_crowd_scenario(crowd_plans(settings, "crowd_size")[0].scenario_config).agents)


class CrowdScreen:
    """Screens rules one at a time in the same crowd, running each baseline seed once.

    The runs are deterministic and the crowd does not depend on a rule's case, so a rule
    whose canonical form (``rule-format.md``, section 13) was screened already, with the same
    visibility, gets the results of that screening without the flow being run again; its
    entry says which rule version's runs they are (``same_runs_as``). ``out_dir`` gets the run
    folders; ``where`` is how the screening entries name it.
    """

    def __init__(
        self,
        settings: ScreeningSettings,
        out_dir: Path,
        experiment: str,
        git: Mapping[str, Any],
        population: Mapping[int, Mapping[str, Any]],
        where: str = "screening",
    ):
        self.settings, self.out_dir, self.experiment, self.git, self.where = settings, out_dir, experiment, git, where
        self.population = population_of(population, "crowd")
        self.plans = crowd_plans(settings, experiment)
        self._baseline: dict[int, dict[str, Any]] = {}
        self._screened: dict[tuple, tuple[str, list[dict[str, Any]]]] = {}

    def baseline(self, plan: AvoidanceRunPlan) -> dict[str, Any]:
        if plan.seed not in self._baseline:
            folder = self.out_dir / "baseline" / plan.run_id
            run = replace(plan, run_id=f"baseline_{plan.run_id}", population=self.population)
            self._baseline[plan.seed] = _run_numbers(execute_avoidance_run(run, folder, self.git))
        return self._baseline[plan.seed]

    def screen(self, rule: Rule, staging_root: Path, visibility: Mapping[str, bool]) -> dict[str, Any]:
        key = (canonical_hash(rule.written), tuple(sorted(visibility.items())))
        same_runs_as = None
        if key in self._screened:
            same_runs_as, per_seed = self._screened[key]
            per_seed = json.loads(json.dumps(per_seed))
        else:
            forget_rule_database(staging_root)
            per_seed = []
            for plan in self.plans:
                base = self.baseline(plan)
                run = replace(
                    plan,
                    run_id=f"{rule.rule_id}_v{rule.version}_{plan.run_id}",
                    population=self.population,
                    visibility=dict(visibility),
                    directives=_directives(rule, staging_root),
                )
                ruled = _run_numbers(execute_avoidance_run(run, self.out_dir / rule.rule_id / plan.run_id, self.git))
                per_seed.append({
                    "seed": plan.seed, "baseline": base, "rule": ruled,
                    "folders": {"baseline": f"{self.where}/baseline/{plan.run_id}", "rule": f"{self.where}/{rule.rule_id}/{plan.run_id}"},
                })
            self._screened[key] = (rule.key, per_seed)
        reasons = [
            f"seed {entry['seed']}: the flow gridlocked ({entry['rule']['status']}, {entry['rule']['arrived']} of "
            f"{entry['rule']['n_agents']} arrived) where the baseline did not"
            for entry in per_seed
            if entry["rule"]["gridlocked"] and not entry["baseline"]["gridlocked"]
        ]
        summary = {
            "gridlocked_runs": sum(entry["rule"]["gridlocked"] for entry in per_seed),
            "baseline_gridlocked_runs": sum(entry["baseline"]["gridlocked"] for entry in per_seed),
            "collision_episodes": [entry["rule"]["collision_episodes"] for entry in per_seed],
            "baseline_collision_episodes": [entry["baseline"]["collision_episodes"] for entry in per_seed],
            "throughput_agents_per_min": [entry["rule"]["throughput_agents_per_min"] for entry in per_seed],
            "baseline_throughput_agents_per_min": [entry["baseline"]["throughput_agents_per_min"] for entry in per_seed],
            "rule_fired": [entry["rule"]["rule_fired"] for entry in per_seed],
        }
        return {
            "kind": KIND_CROWD,
            "experiment": self.experiment,
            "scenario": Path(self.settings.scenario).stem,
            "baseline": self.settings.baseline,
            "case_id": None,
            "seeds": [plan.seed for plan in self.plans],
            "screened_utc": _utc_now(),
            "verdict": "failed" if reasons else "passed",
            "reasons": reasons,
            "results": {"settings": self.settings.as_dict(), "summary": summary, "per_seed": per_seed, "same_runs_as": same_runs_as},
        }
