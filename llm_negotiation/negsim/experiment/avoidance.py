"""Avoidance experiments: reading a config, expanding its design, running it, writing the logs.

An avoidance experiment is the second kind of experiment this package runs. It is marked
by ``layer: avoidance`` at the top of its config; a config without that key is a
negotiation experiment of issue #24 and is read by ``negsim.experiment.config`` exactly as
before. No avoidance run calls a model, so none costs anything.

An experiment names an avoidance scenario and describes a *design*: named factors, each a
list of named levels. Every combination of one level per factor is one run. A level can
change the scenario (``scenario_overrides``), the directives, the arbitration settings,
who the agents are (``population``) and what they can see of each other (``visibility``).

Who the agents are is kept apart from what they are physically. ``population`` attaches a
persona (age, gender) to an agent and nothing else; an agent's size and speeds come only
from the scenario. An experiment that wants older agents to be slower has to say so
itself, by setting both for the same agent, where anyone reading the config can see it.
"""

from __future__ import annotations

import itertools
import json
import platform
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from .. import __version__
from ..avoidance.coordination import ArbitrationSettings
from ..avoidance.directives import (
    POLICY_PROPORTIONAL,
    SHARE_POLICIES,
    DirectiveProvider,
    StaticProvider,
    make_provider,
)
from ..avoidance.perception import NEVER_OBSERVABLE, PERCEPTION_SCHEMA_VERSION, default_visibility
from ..avoidance.simulation import AvoidanceSimulation, SimulationResult
from ..configutil import (
    PACKAGE_ROOT,
    ConfigError,
    as_bool,
    as_choice,
    as_number,
    check_keys,
    deep_merge,
    load_yaml,
    resolve_path,
)
from ..conflict.roles import TIE_BREAKS
from ..control.strategy1 import POLICIES
from ..personas.loader import load_personas
from ..personas.schema import ATTRIBUTES, Persona, PersonaError
from ..runlog.schema import (
    CONFIG_FILE,
    LOG_SCHEMA_VERSION,
    OUTCOME_FILE,
    RUN_KIND_AVOIDANCE,
    validate_run_dir,
)
from ..runlog.writer import AvoidanceRunLogger, write_avoidance_summary
from ..scenarios.crowd_base import CrowdScenarioSpec
from ..scenarios.registry import build_crowd_scenario, load_scenario_config

LAYER_AVOIDANCE = "avoidance"
SCHEMA_VERSION = 1

_LEVEL_KEYS = ("scenario_overrides", "directives", "arbitration", "population", "visibility")
_DIRECTIVE_KEYS = ("provider", "default", "agents", "pairs", "share_policy")


def is_avoidance_config(raw: Any) -> bool:
    """True if a parsed experiment config is an avoidance experiment."""
    return isinstance(raw, Mapping) and raw.get("layer") == LAYER_AVOIDANCE


@dataclass(frozen=True)
class AvoidanceRunPlan:
    """Everything that defines one avoidance run, before it is executed."""

    index: int
    run_id: str
    experiment_name: str
    seed: int
    repeat: int
    scenario_file: str
    variant: Mapping[str, str]
    scenario_config: Mapping[str, Any]
    population: Mapping[int, Mapping[str, Any]]
    visibility: Mapping[str, bool]
    directives: Mapping[str, Any]
    share_policy: str
    arbitration: ArbitrationSettings
    logging: Mapping[str, Any]

    def provider(self) -> DirectiveProvider:
        return make_provider(self.directives or None)

    def attributes(self) -> dict[int, Mapping[str, Any]]:
        """Each agent's persona attributes, for the perception records."""
        return {agent_id: entry["attributes"] for agent_id, entry in self.population.items()}


class AvoidanceExperiment:
    def __init__(self, raw: Mapping[str, Any], source: str = "<config>"):
        self.source = source
        where = self._where = f"experiment config {source}"
        check_keys(
            raw,
            where,
            ("layer", "experiment_name", "scenario", "design"),
            ("schema_version", "description", "scenario_overrides", "personas", *_LEVEL_KEYS[1:], "logging"),
        )
        if raw["layer"] != LAYER_AVOIDANCE:
            raise ConfigError(f"{where}.layer: expected {LAYER_AVOIDANCE!r}, got {raw['layer']!r}")
        if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ConfigError(f"{where}: schema_version {raw['schema_version']!r} is not supported")
        self.experiment_name = _identifier(raw["experiment_name"], f"{where}.experiment_name")
        self.description = " ".join(str(raw.get("description", "")).split())
        self.scenario_file = str(raw["scenario"])
        self.personas_file = raw.get("personas")
        self._personas: Optional[dict[str, Persona]] = None
        self.base = {
            "scenario_overrides": dict(raw.get("scenario_overrides") or {}),
            "directives": dict(raw.get("directives") or {}),
            "arbitration": dict(raw.get("arbitration") or {}),
            "population": dict(raw.get("population") or {}),
            "visibility": raw.get("visibility", "default"),
        }
        self.logging = self._logging(raw.get("logging") or {}, f"{where}.logging")
        self.design = raw["design"]
        self._plans = self._expand()

    @classmethod
    def load(cls, path: Path | str) -> "AvoidanceExperiment":
        raw = load_yaml(resolve_path(path))
        if not isinstance(raw, Mapping):
            raise ConfigError(f"{path}: expected a mapping at the top level")
        return cls(raw, source=str(path))

    def plans(self) -> list[AvoidanceRunPlan]:
        return list(self._plans)

    # --- sections ---------------------------------------------------------------------

    @staticmethod
    def _logging(raw: Any, where: str) -> dict[str, Any]:
        check_keys(raw, where, (), ("trajectory_stride", "interactions"))
        stride = raw.get("trajectory_stride", 1)
        if isinstance(stride, bool) or not isinstance(stride, int) or stride < 1:
            raise ConfigError(f"{where}.trajectory_stride: expected a whole number, 1 or more, got {stride!r}")
        return {
            "trajectory_stride": stride,
            "interactions": as_bool(raw.get("interactions", True), f"{where}.interactions"),
        }

    @staticmethod
    def _arbitration(raw: Any, where: str) -> ArbitrationSettings:
        check_keys(raw, where, (), ("enabled", "policy", "tie_break"))
        return ArbitrationSettings(
            enabled=as_bool(raw.get("enabled", True), f"{where}.enabled"),
            policy=as_choice(raw.get("policy", "strategy1"), f"{where}.policy", POLICIES),
            tie_break=as_choice(raw.get("tie_break", "lower_index"), f"{where}.tie_break", TIE_BREAKS),
        )

    @staticmethod
    def _visibility(raw: Any, where: str) -> dict[str, bool]:
        """The visibility settings of issue #24, read the same way."""
        visibility = default_visibility()
        if raw is None or raw == "default":
            return visibility
        if not isinstance(raw, Mapping):
            raise ConfigError(f"{where}: expected 'default' or a mapping, got {raw!r}")
        for key, value in raw.items():
            if key not in visibility:
                raise ConfigError(f"{where}: unknown attribute {key!r}; known: {sorted(visibility)}")
            visibility[key] = as_bool(value, f"{where}.{key}")
        return visibility

    # --- design -----------------------------------------------------------------------

    def _expand(self) -> list[AvoidanceRunPlan]:
        where = f"{self._where}.design"
        check_keys(self.design, where, (), ("seed", "repeats", "factors"))
        base_seed = int(as_number(self.design.get("seed", 0), f"{where}.seed", minimum=0))
        repeats = int(as_number(self.design.get("repeats", 1), f"{where}.repeats", minimum=1))

        factors = self.design.get("factors") or {}
        if not isinstance(factors, Mapping):
            raise ConfigError(f"{where}.factors: expected a mapping from factor name to a list of levels")
        names, level_lists = [], []
        for factor, levels in factors.items():
            label = f"{where}.factors.{factor}"
            _identifier(factor, label)
            if not isinstance(levels, list) or not levels:
                raise ConfigError(f"{label}: expected a non-empty list of levels")
            parsed = []
            for index, level in enumerate(levels):
                check_keys(level, f"{label}[{index}]", ("name",), _LEVEL_KEYS)
                parsed.append((_identifier(level["name"], f"{label}[{index}].name"), level))
            if len({name for name, _ in parsed}) != len(parsed):
                raise ConfigError(f"{label}: two levels have the same name")
            names.append(str(factor))
            level_lists.append(parsed)

        plans: list[AvoidanceRunPlan] = []
        for combination in itertools.product(*level_lists):
            for repeat in range(1, repeats + 1):
                plans.append(self._plan(len(plans) + 1, base_seed, names, combination, repeat, repeats > 1))
        if len({plan.run_id for plan in plans}) != len(plans):
            raise ConfigError(f"{where}: two runs have the same id; give the levels distinct names")
        return plans

    def _plan(self, index, base_seed, names, combination, repeat, many_repeats) -> AvoidanceRunPlan:
        where = f"{self._where}: run {index}"
        settings = {key: (dict(value) if isinstance(value, Mapping) else value) for key, value in self.base.items()}
        for _, level in combination:
            for key in _LEVEL_KEYS:
                if key not in level:
                    continue
                if key == "visibility" or not isinstance(level[key], Mapping):
                    settings[key] = level[key]
                else:
                    settings[key] = deep_merge(settings[key] or {}, level[key])

        scenario_config = load_scenario_config(self.scenario_file, settings["scenario_overrides"])
        if repeat > 1:
            # Identical repeats of a deterministic run would be the same run. Each repeat
            # gets its own seed for whatever the scenario randomises (starting positions).
            scenario_config["seed"] = int(scenario_config.get("seed", 0)) + repeat - 1
        try:
            spec = build_crowd_scenario(scenario_config)
        except ConfigError as exc:
            raise ConfigError(f"{where}: {exc}") from exc

        directives = dict(settings["directives"] or {})
        check_keys(directives, f"{where}.directives", (), _DIRECTIVE_KEYS)
        share_policy = as_choice(
            directives.pop("share_policy", POLICY_PROPORTIONAL), f"{where}.directives.share_policy", SHARE_POLICIES
        )
        provider = make_provider(directives or None, f"{where}.directives")
        _check_directive_agents(provider, len(spec.agents), f"{where}.directives")

        parts = [f"{index:03d}"] + [name for name, _ in combination]
        if not combination:
            parts.append("base")
        if many_repeats:
            parts.append(f"r{repeat}")
        return AvoidanceRunPlan(
            index=index,
            run_id="_".join(parts),
            experiment_name=self.experiment_name,
            seed=base_seed + index,
            repeat=repeat,
            scenario_file=self.scenario_file,
            variant={factor: name for factor, (name, _) in zip(names, combination)},
            scenario_config=scenario_config,
            population=self._population(settings["population"] or {}, spec, f"{where}.population"),
            visibility=self._visibility(settings["visibility"], f"{where}.visibility"),
            directives=directives,
            share_policy=share_policy,
            arbitration=self._arbitration(settings["arbitration"] or {}, f"{where}.arbitration"),
            logging=self.logging,
        )

    def _population(self, raw: Any, spec: CrowdScenarioSpec, where: str) -> dict[int, dict[str, Any]]:
        """Which persona each agent has. An agent not mentioned has none."""
        check_keys(raw, where, (), ("groups", "agents"))
        assigned: dict[int, Any] = {}
        groups = {agent.group for agent in spec.agents}
        for group, entry in (raw.get("groups") or {}).items():
            if group not in groups:
                raise ConfigError(f"{where}.groups: unknown group {group!r}; this scenario has {sorted(groups)}")
            for agent in spec.agents:
                if agent.group == group:
                    assigned[agent.agent_id] = (entry, f"{where}.groups.{group}")
        for key, entry in (raw.get("agents") or {}).items():
            if isinstance(key, bool) or not isinstance(key, int) or not 0 <= key < len(spec.agents):
                raise ConfigError(
                    f"{where}.agents: {key!r} is not an agent index; this scenario has agents 0 to {len(spec.agents) - 1}"
                )
            assigned[key] = (entry, f"{where}.agents.{key}")

        population = {}
        for agent_id, (entry, label) in sorted(assigned.items()):
            check_keys(entry, label, ("persona",), tuple(ATTRIBUTES))
            personas = self._load_personas()
            if entry["persona"] not in personas:
                raise ConfigError(f"{label}: unknown persona {entry['persona']!r}; known: {sorted(personas)}")
            overrides = {key: entry[key] for key in ATTRIBUTES if key in entry}
            try:
                persona = personas[entry["persona"]].with_overrides(**overrides)
            except PersonaError as exc:
                raise ConfigError(f"{label}: {exc}") from exc
            population[agent_id] = {"persona_id": persona.persona_id, "attributes": dict(persona.attributes)}
        return population

    def _load_personas(self) -> dict[str, Persona]:
        if self._personas is None:
            if not self.personas_file:
                raise ConfigError(
                    f"{self._where}: 'population' refers to a persona, but the config has no 'personas' file"
                )
            try:
                self._personas = load_personas(self.personas_file)
            except PersonaError as exc:
                raise ConfigError(str(exc)) from exc
        return self._personas


def _check_directive_agents(provider: DirectiveProvider, n_agents: int, where: str) -> None:
    if not isinstance(provider, StaticProvider):
        return
    named = set(provider.agents) | {agent_id for pair in provider.pairs for agent_id in pair}
    unknown = sorted(agent_id for agent_id in named if agent_id >= n_agents)
    if unknown:
        raise ConfigError(f"{where}: agent(s) {unknown} do not exist; this scenario has agents 0 to {n_agents - 1}")


def _identifier(value: Any, where: str) -> str:
    text = str(value)
    if not text or not all(ch.isalnum() or ch in "_-" for ch in text):
        raise ConfigError(f"{where}: use letters, digits, '_' and '-' only, got {value!r}")
    return text


# --- one run ------------------------------------------------------------------------------------


def _rounded(value: Optional[float], digits: int = 4) -> Optional[float]:
    if value is None or value != value or value in (float("inf"), float("-inf")):
        return None
    return round(value, digits)


def resolved_config(plan: AvoidanceRunPlan, spec: CrowdScenarioSpec, provider: DirectiveProvider, git: Mapping[str, Any]) -> dict[str, Any]:
    """The fully resolved configuration of a run, as written to ``config.json``."""
    population = []
    for agent in spec.agents:
        entry = plan.population.get(agent.agent_id)
        # The task is part of a persona but never part of what another agent perceives; it
        # is left out here as well so that it cannot be mistaken for something a rule saw.
        attributes = None if entry is None else {k: v for k, v in entry["attributes"].items() if k not in NEVER_OBSERVABLE}
        population.append(
            {
                "agent_id": agent.agent_id,
                "group": agent.group,
                "persona_id": None if entry is None else entry["persona_id"],
                "attributes": attributes,
            }
        )
    return {
        "log_schema_version": LOG_SCHEMA_VERSION,
        "run_kind": RUN_KIND_AVOIDANCE,
        "experiment_name": plan.experiment_name,
        "run_id": plan.run_id,
        "run_index": plan.index,
        "seed": plan.seed,
        "repeat": plan.repeat,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git": dict(git),
        "software": {"negsim_version": __version__, "python": platform.python_version()},
        "scenario_file": plan.scenario_file,
        "variant": dict(plan.variant),
        "scenario": spec.as_dict(),
        "population": population,
        "visibility": dict(plan.visibility),
        "directives": {**provider.describe(), "share_policy": plan.share_policy},
        "arbitration": plan.arbitration.as_dict(),
        "logging": dict(plan.logging),
        "perception_schema_version": PERCEPTION_SCHEMA_VERSION,
    }


def build_events(result: SimulationResult) -> list[dict[str, Any]]:
    """Everything that happened during a run, in time order, one record per event."""
    events: list[dict[str, Any]] = []
    for violation in result.violations:
        events.append({"type": "reciprocity_violation", **violation})
    for handoff in result.handoffs:
        events.append({"type": "handoff", **handoff.as_dict()})
    for item in result.yields:
        events.append({"type": "yield", "time_s": round(item.start_time_s, 6), **item.as_dict()})
    for episode in result.near_misses:
        events.append({"type": "near_miss", "time_s": round(episode.start_time_s, 6), **episode.as_dict()})
    for episode in result.collision_episodes:
        record = episode.as_dict()
        record["max_overlap_m"] = round(-record.pop("min_separation_m"), 6)
        events.append({"type": "collision", "time_s": round(episode.start_time_s, 6), **record})
    for episode in result.wall_collision_episodes:
        events.append({"type": "wall_collision", "time_s": episode["start_time_s"], **episode})
    order = {name: rank for rank, name in enumerate(("reciprocity_violation", "handoff", "collision", "wall_collision", "near_miss", "yield"))}
    events.sort(key=lambda event: (event["time_s"], order[event["type"]], json.dumps(event, sort_keys=True)))
    return [{"event_index": index, **event} for index, event in enumerate(events)]


def build_outcome(plan: AvoidanceRunPlan, spec: CrowdScenarioSpec, result: SimulationResult) -> dict[str, Any]:
    dt = spec.dt
    ids = sorted(result.stats)
    yields_by_agent: dict[int, list] = {agent_id: [] for agent_id in ids}
    for item in result.yields:
        yields_by_agent[item.agent_id].append(item)
    near_by_agent = {agent_id: 0 for agent_id in ids}
    for episode in result.near_misses:
        for agent_id in episode.pair:
            near_by_agent[agent_id] += 1

    agents = {}
    for agent_id in ids:
        stats = result.stats[agent_id]
        agents[str(agent_id)] = {
            "time_to_goal_s": _rounded(result.goal_times[agent_id]),
            "distance_m": _rounded(stats.distance_m),
            "path_deviation_mean_m": _rounded(stats.deviation_sum / stats.samples if stats.samples else None, 6),
            "path_deviation_max_m": _rounded(stats.deviation_max if stats.samples else None, 6),
            "interactions": stats.interactions,
            "interaction_time_s": _rounded(stats.interaction_steps * dt),
            "conflict_exposure_time_s": _rounded(stats.exposure_steps * dt),
            "orca_altered_time_s": _rounded(stats.altered_steps * dt),
            "yield_events": len(yields_by_agent[agent_id]),
            "yield_time_s": _rounded(sum(item.duration_s for item in yields_by_agent[agent_id])),
            "near_misses": near_by_agent[agent_id],
            "min_separation_m": _rounded(stats.min_separation_m, 6),
            "min_wall_gap_m": _rounded(stats.min_wall_gap_m, 6),
            "fallback_steps": stats.fallback_steps,
            "one_sided_steps": stats.one_sided_steps,
            "arbiter_time_s": _rounded(stats.arbiter_steps * dt),
        }

    goal_times = [time for time in result.goal_times.values() if time is not None]
    samples = sum(stats.samples for stats in result.stats.values())
    totals = {
        "interactions": len(result.interactions),
        "conflict_exposure_time_s": _rounded(sum(stats.exposure_steps for stats in result.stats.values()) * dt),
        "yield_events": len(result.yields),
        "yield_time_s": _rounded(sum(item.duration_s for item in result.yields)),
        "near_misses": len(result.near_misses),
        "min_separation_m": _rounded(result.min_separation_m, 6),
        "mean_time_to_goal_s": _rounded(sum(goal_times) / len(goal_times) if goal_times else None),
        "mean_path_deviation_m": _rounded(
            sum(stats.deviation_sum for stats in result.stats.values()) / samples if samples else None, 6
        ),
        "max_path_deviation_m": _rounded(max((stats.deviation_max for stats in result.stats.values()), default=None), 6),
        "steps_with_fallback": result.steps_with_fallback,
        "fallback_agent_steps": sum(stats.fallback_steps for stats in result.stats.values()),
        "one_sided_agent_steps": sum(stats.one_sided_steps for stats in result.stats.values()),
    }

    single_file = []
    for index, segment in enumerate(spec.single_file_segments):
        entries = {
            agent_id: times[index] for agent_id, times in sorted(result.segment_entry_times.items()) if index in times
        }
        earliest = min(entries.values(), default=None)
        first = [agent_id for agent_id, time in entries.items() if time == earliest]
        single_file.append(
            {
                "segment": segment.name,
                "entry_time_s": {str(agent_id): _rounded(time) for agent_id, time in entries.items()},
                "first_through": first[0] if len(first) == 1 else None,
            }
        )

    all_arrived = len(goal_times) == len(ids)
    return {
        "log_schema_version": LOG_SCHEMA_VERSION,
        "run_kind": RUN_KIND_AVOIDANCE,
        "run_id": plan.run_id,
        "status": result.status,
        "sim_time_s": _rounded(result.sim_time_s),
        "steps": result.steps,
        "n_agents": len(ids),
        "arrived": len(goal_times),
        "collisions": dict(result.collisions),
        "deadlock": result.deadlock,
        "makespan_s": _rounded(max(goal_times)) if all_arrived and goal_times else None,
        "time_to_goal_s": {str(agent_id): _rounded(result.goal_times[agent_id]) for agent_id in ids},
        "agents": agents,
        "totals": totals,
        "single_file": single_file,
        "reciprocity_violations": list(result.violations),
        "handoffs": [handoff.as_dict() for handoff in result.handoffs],
        "thresholds": {**spec.thresholds.as_dict(), "deadlock": spec.deadlock.as_dict()},
    }


def execute_avoidance_run(
    plan: AvoidanceRunPlan, run_dir: Path | str, git: Optional[Mapping[str, Any]] = None
) -> dict[str, Any]:
    """Run one avoidance simulation, write its folder, and return the outcome."""
    spec = build_crowd_scenario(plan.scenario_config)
    provider = plan.provider()
    simulation = AvoidanceSimulation(
        spec,
        provider=provider,
        attributes=plan.attributes(),
        visibility=plan.visibility,
        arbitration=plan.arbitration,
        share_policy=plan.share_policy,
        seed=plan.seed,
        trajectory_stride=plan.logging["trajectory_stride"],
    )
    result = simulation.run()

    logger = AvoidanceRunLogger(run_dir)
    logger.write_config(resolved_config(plan, spec, provider, git or {"commit": None, "dirty": None}))
    logger.write_trajectory(result.trajectory)
    interactions = result.interactions if plan.logging["interactions"] else []
    logger.write_interactions(interaction.as_dict(spec.dt) for interaction in interactions)
    logger.write_events(build_events(result))
    outcome = build_outcome(plan, spec, result)
    logger.write_outcome(outcome)

    problems = validate_run_dir(run_dir)
    if problems:
        raise RuntimeError(f"run {plan.run_id} wrote a log folder that fails its own schema: {problems}")
    return outcome


# --- a whole experiment -------------------------------------------------------------------------


def avoidance_summary_row(config: Mapping[str, Any], outcome: Mapping[str, Any]) -> dict[str, Any]:
    """One row of an avoidance experiment's ``summary.csv``."""
    totals, agents, collisions = outcome["totals"], outcome["agents"], outcome["collisions"]
    first_through = [segment["first_through"] for segment in outcome["single_file"]]

    def of(agent_id: str, key: str) -> Any:
        return agents[agent_id][key] if agent_id in agents else None

    return {
        "experiment_name": config["experiment_name"],
        "run_id": config["run_id"],
        "scenario": config["scenario"]["type"],
        "variant": "+".join(f"{factor}={level}" for factor, level in config["variant"].items()),
        "seed": config["seed"],
        "repeat": config["repeat"],
        "n_agents": outcome["n_agents"],
        "provider": config["directives"]["provider"],
        "arbitration_enabled": config["arbitration"]["enabled"],
        "status": outcome["status"],
        "arrived": outcome["arrived"],
        "collisions": collisions["agent_agent"] + collisions["agent_wall"],
        "max_overlap_m": collisions["max_overlap_m"],
        "deadlock": outcome["deadlock"],
        "makespan_s": outcome["makespan_s"],
        "mean_time_to_goal_s": totals["mean_time_to_goal_s"],
        "conflict_exposure_time_s": totals["conflict_exposure_time_s"],
        "yield_events": totals["yield_events"],
        "yield_time_s": totals["yield_time_s"],
        "near_misses": totals["near_misses"],
        "min_separation_m": totals["min_separation_m"],
        "steps_with_fallback": totals["steps_with_fallback"],
        "fallback_agent_steps": totals["fallback_agent_steps"],
        "reciprocity_violations": len(outcome["reciprocity_violations"]),
        "handoffs": len(outcome["handoffs"]),
        "first_through": first_through[0] if first_through else None,
        "time_to_goal_0_s": of("0", "time_to_goal_s"),
        "time_to_goal_1_s": of("1", "time_to_goal_s"),
        "path_deviation_max_0_m": of("0", "path_deviation_max_m"),
        "path_deviation_max_1_m": of("1", "path_deviation_max_m"),
        "conflict_exposure_0_s": of("0", "conflict_exposure_time_s"),
        "conflict_exposure_1_s": of("1", "conflict_exposure_time_s"),
        "git_commit": (config["git"].get("commit") or "")[:10],
    }


@dataclass
class AvoidanceExperimentResult:
    experiment_dir: Path
    summary_path: Optional[Path] = None
    executed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    rows: list[dict[str, Any]] = field(default_factory=list)


def run_avoidance_experiment(
    config: AvoidanceExperiment,
    out_root: Optional[Path | str] = None,
    limit: Optional[int] = None,
    overwrite: bool = False,
    report: Callable[[str], None] = print,
    git: Optional[Mapping[str, Any]] = None,
) -> AvoidanceExperimentResult:
    """Execute an avoidance experiment's runs in order and write its ``summary.csv``.

    A run whose folder already holds an outcome is skipped unless ``overwrite`` is set.
    Avoidance runs are deterministic and free, so skipping only saves time.
    """
    plans = config.plans()
    if limit is not None:
        plans = plans[:limit]
    experiment_dir = Path(out_root if out_root is not None else PACKAGE_ROOT / "runs") / config.experiment_name
    experiment_dir.mkdir(parents=True, exist_ok=True)
    result = AvoidanceExperimentResult(experiment_dir)
    if git is None:
        from .batch import git_state

        git = git_state()

    for plan in plans:
        run_dir = experiment_dir / plan.run_id
        if (run_dir / OUTCOME_FILE).is_file() and not overwrite:
            result.skipped.append(plan.run_id)
            report(f"[{plan.index}/{len(plans)}] {plan.run_id}: already done, skipped")
            continue
        outcome = execute_avoidance_run(plan, run_dir, git)
        result.executed.append(plan.run_id)
        collisions = outcome["collisions"]["agent_agent"] + outcome["collisions"]["agent_wall"]
        report(
            f"[{plan.index}/{len(plans)}] {plan.run_id}: {outcome['status']}, "
            f"{outcome['arrived']}/{outcome['n_agents']} arrived, {collisions} collision(s), "
            f"conflict exposure {outcome['totals']['conflict_exposure_time_s']} s"
        )

    for plan in plans:
        run_dir = experiment_dir / plan.run_id
        if (run_dir / OUTCOME_FILE).is_file():
            result.rows.append(
                avoidance_summary_row(
                    json.loads((run_dir / CONFIG_FILE).read_text(encoding="utf-8")),
                    json.loads((run_dir / OUTCOME_FILE).read_text(encoding="utf-8")),
                )
            )
    result.summary_path = write_avoidance_summary(experiment_dir, result.rows)
    return result
