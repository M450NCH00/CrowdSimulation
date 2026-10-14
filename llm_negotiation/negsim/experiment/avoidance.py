"""Avoidance experiments: reading a config, expanding its design, running it, writing the logs.

An avoidance experiment is the second kind of experiment this package runs. It is marked
by ``layer: avoidance`` at the top of its config; a config without that key is a
negotiation experiment of issue #24 and is read by ``negsim.experiment.config`` exactly as
before. No avoidance run calls a model, so none costs anything.

An experiment names an avoidance scenario and describes a *design*: named factors, each a
list of named levels. Every combination of one level per factor is one run. A level can
change the scenario (``scenario_overrides``), the directives, the arbitration settings,
who the agents are (``population``), what they can see of each other (``visibility``), and
which frozen baseline the ORCA layer follows (``baseline``, issue #28).

Directives come from a provider: ``null`` (plain ORCA), ``static`` (written in the
config), or, since issue #28, ``rules``: the rule database (``negsim.rules``), with a named
rule set and any rules switched on or off on top of it.

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
from ..avoidance.simulation import INTERACTION_OUTCOMES, AvoidanceSimulation, Perturbation, SimulationResult
from ..rules import RuleDatabase, RuleDatabaseProvider, RuleError
from ..rules.matching import DEFAULT_HYSTERESIS_STEPS
from .baselines import Baseline, load_baseline
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

_LEVEL_KEYS = ("scenario_overrides", "directives", "arbitration", "population", "visibility", "baseline")
_STATIC_DIRECTIVE_KEYS = ("provider", "default", "agents", "pairs", "share_policy")
_RULE_DIRECTIVE_KEYS = ("provider", "ruleset", "enable", "disable", "hysteresis_steps", "database", "share_policy")
_DIRECTIVE_KEYS = tuple(dict.fromkeys(_STATIC_DIRECTIVE_KEYS + _RULE_DIRECTIVE_KEYS))
PROVIDER_RULES = RuleDatabaseProvider.name
_DATABASES: dict[Path, RuleDatabase] = {}


def rule_database(path: Any = "rule_db") -> RuleDatabase:
    """The rule database at ``path`` (under ``llm_negotiation/``), loaded once per process."""
    root = resolve_path(path).resolve()
    if root not in _DATABASES:
        _DATABASES[root] = RuleDatabase.load(root)
    return _DATABASES[root]


def build_provider(directives: Mapping[str, Any], visibility: Mapping[str, bool], where: str) -> DirectiveProvider:
    """The directive provider an experiment's ``directives`` block asks for.

    ``null`` and ``static`` are issue #26's (``make_provider``). ``rules`` reads the rule
    database: ``ruleset`` names a rule set, ``disable`` lists rule ids to leave out of it,
    ``enable`` maps rule ids to the versions to add, and ``hysteresis_steps`` sets the
    matching policy's hysteresis (``docs/rule-matching.md``).
    """
    if directives.get("provider") != PROVIDER_RULES:
        unknown = [key for key in directives if key not in _STATIC_DIRECTIVE_KEYS]
        if unknown:
            raise ConfigError(f"{where}: {unknown} apply only to provider 'rules'")
        return make_provider(directives or None, where)
    check_keys(directives, where, ("provider",), _RULE_DIRECTIVE_KEYS)
    enable = directives.get("enable") or {}
    if not isinstance(enable, Mapping) or not all(
        isinstance(version, int) and not isinstance(version, bool) for version in enable.values()
    ):
        raise ConfigError(f"{where}.enable: expected a mapping from rule_id to version, e.g. keep_right_head_on: 1")
    disable = directives.get("disable") or []
    if not isinstance(disable, list):
        raise ConfigError(f"{where}.disable: expected a list of rule ids")
    steps = directives.get("hysteresis_steps", DEFAULT_HYSTERESIS_STEPS)
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 1:
        raise ConfigError(f"{where}.hysteresis_steps: expected a whole number, 1 or more, got {steps!r}")
    database = str(directives.get("database", "rule_db"))
    try:
        active = rule_database(database).activate(directives.get("ruleset"), enable, disable)
        return RuleDatabaseProvider(active, visibility, steps, database)
    except RuleError as exc:
        raise ConfigError(f"{where}: {exc}") from exc


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
    baseline: Optional[Baseline] = None
    perturbation: Perturbation = Perturbation()

    def provider(self) -> DirectiveProvider:
        return build_provider(self.directives, self.visibility, "directives")

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
            "baseline": raw.get("baseline"),
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
        """``interactions: false`` leaves out the per-interaction records: since issue #28
        both ``interactions.jsonl`` and ``pair_interactions.jsonl``. The outcome still counts them."""
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

        baseline = None
        overrides = settings["scenario_overrides"] or {}
        if settings["baseline"] is not None:
            try:
                baseline = load_baseline(settings["baseline"])
            except ConfigError as exc:
                raise ConfigError(f"{where}: {exc}") from exc
            # The baseline goes under the experiment's own overrides, so that a level can
            # still vary one of its settings (and the run records both).
            overrides = deep_merge(baseline.scenario_overrides(load_scenario_config(self.scenario_file)), overrides)
        scenario_config = load_scenario_config(self.scenario_file, overrides)
        if repeat > 1:
            # Identical repeats of a deterministic run would be the same run. Each repeat
            # gets its own seed for whatever the scenario randomises (starting positions).
            scenario_config["seed"] = int(scenario_config.get("seed", 0)) + repeat - 1
        try:
            spec = build_crowd_scenario(scenario_config)
        except ConfigError as exc:
            raise ConfigError(f"{where}: {exc}") from exc

        visibility = self._visibility(settings["visibility"], f"{where}.visibility")
        directives = dict(settings["directives"] or {})
        check_keys(directives, f"{where}.directives", (), _DIRECTIVE_KEYS)
        share_policy = as_choice(
            directives.pop("share_policy", POLICY_PROPORTIONAL), f"{where}.directives.share_policy", SHARE_POLICIES
        )
        provider = build_provider(directives, visibility, f"{where}.directives")
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
            visibility=visibility,
            directives=directives,
            share_policy=share_policy,
            arbitration=self._arbitration(settings["arbitration"] or {}, f"{where}.arbitration"),
            logging=self.logging,
            baseline=baseline,
            perturbation=baseline.perturbation if baseline is not None else Perturbation(),
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
        "baseline": None if plan.baseline is None else plan.baseline.describe(),
        "perturbation": plan.perturbation.as_dict(),
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
    for pair in result.pairs:
        record = pair.provider_record
        if record is None:
            continue
        for entry in record.evaluations:
            if entry["outcome"] == "ambiguous_match":
                events.append(
                    {
                        "type": "ambiguous_match",
                        "time_s": entry["from_time_s"],
                        "step": entry["from_step"],
                        "pair": list(pair.agents),
                        "applied": entry["rule"],
                        "ambiguous_with": entry["ambiguous_with"],
                    }
                )
    conflicts = {}
    for pair in result.pairs:
        for event in [] if pair.provider_record is None else pair.provider_record.conflicts:
            conflicts[id(event)] = event  # one event can be on several pairs' records
    for event in conflicts.values():
        events.append({"type": "cross_pair_conflict", **event})
    order = {
        name: rank
        for rank, name in enumerate(
            ("reciprocity_violation", "handoff", "ambiguous_match", "cross_pair_conflict", "collision", "wall_collision", "near_miss", "yield")
        )
    }
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

    outcomes: dict[str, Any] = {"pairs": len(result.pairs), **{name: 0 for name in INTERACTION_OUTCOMES}}
    ingredients = {"exposed": 0, "yielded": 0, "collided": 0, "deadlocked": 0, "open_at_timeout": 0}
    for pair in result.pairs:
        outcomes[pair.outcome] += 1
        detail = pair.outcome_detail
        ingredients["exposed"] += detail["exposed"]
        ingredients["yielded"] += detail["yield_events"] > 0
        ingredients["collided"] += detail["collisions"] > 0
        ingredients["deadlocked"] += detail["deadlock"]
        ingredients["open_at_timeout"] += detail["open_at_timeout"]
    outcomes["pairs_with"] = ingredients

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
        "interaction_outcomes": outcomes,
        "rules": result.provider_summary,
        "baseline": None if plan.baseline is None else plan.baseline.name,
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
        perturbation=plan.perturbation,
    )
    result = simulation.run()

    logger = AvoidanceRunLogger(run_dir)
    logger.write_config(resolved_config(plan, spec, provider, git or {"commit": None, "dirty": None}))
    logger.write_trajectory(result.trajectory)
    interactions = result.interactions if plan.logging["interactions"] else []
    logger.write_interactions(interaction.as_dict(spec.dt) for interaction in interactions)
    pairs = result.pairs if plan.logging["interactions"] else []
    logger.write_pair_interactions(pair.as_dict(spec.dt) for pair in pairs)
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
        **_rule_columns(config, outcome),
        "git_commit": (config["git"].get("commit") or "")[:10],
    }


def _rule_columns(config: Mapping[str, Any], outcome: Mapping[str, Any]) -> dict[str, Any]:
    """The summary columns added by issue #28 (log schema version 3); empty for older runs."""
    counts = outcome.get("interaction_outcomes") or {}
    rules = outcome.get("rules") or {}
    fired = rules.get("matches_begun") or {}
    return {
        "baseline": outcome.get("baseline"),
        "ruleset": config["directives"].get("ruleset"),
        "pairs": counts.get("pairs"),
        "avoided": counts.get("avoided"),
        "resolved": counts.get("resolved"),
        "failed": counts.get("failed"),
        "rules_fired": ";".join(f"{key}={count}" for key, count in sorted(fired.items())) or None,
        "ambiguous_matches": (rules.get("evaluations") or {}).get("ambiguous_match") if rules else None,
        "cross_pair_conflicts": rules.get("cross_pair_conflicts") if rules else None,
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
