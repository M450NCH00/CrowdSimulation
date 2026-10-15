"""Experiment configs: reading one, and expanding its design into a list of runs.

An experiment file names a scenario, says whether and how the agents negotiate, and
describes a *design*: which participants meet, and which nuisance factors are crossed
with them. :meth:`ExperimentConfig.plans` expands that into one :class:`RunPlan` per run.

Design factors (``design.mode: factorial`` crosses all of them)
---------------------------------------------------------------
``pairs``              which two participants meet
``scenario_variants``  named sets of scenario overrides (e.g. the asymmetric starts)
``info_variants``      named choices of situational information (condition C4)
``assignment``         which member of the pair is agent 0
``sides``              which side agent 0 starts on
``first_speaker``      which agent opens the dialogue
``repeats``            identical repetitions, each with its own recorded seed

The last four exist to keep confounds under control. Speaking first, being agent 0 (which
decides Strategy 1's tie-break) and starting on a given side could each sway the outcome,
and without balancing them such an effect would be indistinguishable from a persona
effect. Each takes ``counterbalance`` to run both levels.

``design.mode: explicit`` lists the runs one by one instead, for small hand-built designs.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import (
    ConfigError,
    as_bool,
    as_choice,
    as_number,
    check_keys,
    deep_merge,
    load_yaml,
    resolve_path,
)
from ..control.strategy1 import POLICIES
from ..conflict.roles import TIE_BREAKS
from ..llm.mock import POLICIES as MOCK_POLICIES
from ..negotiation.prompts import Participant, load_template, resolve_visibility
from ..negotiation.situation import resolve_info_fields
from ..personas.loader import load_personas
from ..personas.schema import ATTRIBUTES, Persona, PersonaError
from ..scenarios.registry import build_scenario, load_scenario_config

SCHEMA_VERSION = 1
CONDITIONS = ("C0", "C1", "C2", "C3", "C4")
TIMING_MODES = ("pre_conflict", "concurrent")
CLIENTS = ("mock", "deepseek")
DEFAULT_TASKS_FILE = "configs/tasks/gamechat_tasks.yaml"
GROUND_TRUTH_TASK_PRIORITY = "task_priority"

_LEVELS = {
    "assignment": {"fixed": (False,), "swapped": (True,), "counterbalance": (False, True)},
    "sides": {"fixed": (False,), "swapped": (True,), "counterbalance": (False, True)},
    "first_speaker": {"agent_0": (0,), "agent_1": (1,), "counterbalance": (0, 1)},
}


@dataclass(frozen=True)
class TaskTable:
    """GameChat's task types: their priority order and the strings that name them."""

    priority_order: tuple[str, ...]
    task_strings: Mapping[str, tuple[str, ...]]
    source: str

    @classmethod
    def load(cls, path: Path | str) -> "TaskTable":
        raw = load_yaml(resolve_path(path))
        check_keys(raw, str(path), ("priority_order", "task_strings"), ("schema_version", "source"))
        order = tuple(raw["priority_order"])
        strings = {name: tuple(values) for name, values in raw["task_strings"].items()}
        if set(order) != set(strings) or any(not values for values in strings.values()):
            raise ConfigError(f"{path}: priority_order and task_strings must name the same types")
        return cls(order, strings, str(raw.get("source", "")))


@dataclass(frozen=True)
class SlotSpec:
    """How a config describes one participant.

    Either a bare GameChat task type (``{task_type: hospital}``), or a persona, optionally
    with attributes changed for this run (``{persona: f25, age: 70}``) and optionally
    tagged with a task type (``{persona: f70, task_type: hospital}``).
    """

    persona: Optional[str] = None
    overrides: Mapping[str, Any] = field(default_factory=dict)
    task_type: Optional[str] = None

    @classmethod
    def parse(cls, raw: Any, where: str) -> "SlotSpec":
        check_keys(raw, where, (), ("persona", "task_type", *ATTRIBUTES))
        persona, task_type = raw.get("persona"), raw.get("task_type")
        overrides = {key: raw[key] for key in ATTRIBUTES if key in raw}
        if persona is None:
            if overrides:
                raise ConfigError(
                    f"{where}: {sorted(overrides)} can only be set on a persona; a participant "
                    "without one is described by 'task_type' alone"
                )
            if task_type is None:
                raise ConfigError(f"{where}: give a 'persona' or a 'task_type'")
        return cls(persona, overrides, task_type)

    @property
    def label(self) -> str:
        """Short name used in run ids."""
        if self.persona is None:
            return str(self.task_type)
        parts = [self.persona]
        parts += [f"{key}{self.overrides[key]}" for key in ("age", "gender") if key in self.overrides]
        if self.task_type is not None:
            parts.append(self.task_type)
        return "+".join(parts)

    def as_dict(self) -> dict[str, Any]:
        return {"persona": self.persona, "overrides": dict(self.overrides), "task_type": self.task_type}


@dataclass(frozen=True)
class RunPlan:
    """Everything that defines one run, before it is executed."""

    index: int
    run_id: str
    experiment_name: str
    condition: str
    seed: int
    repeat: int
    scenario_file: str
    scenario_variant: str
    scenario_config: Mapping[str, Any]
    slots: tuple[SlotSpec, SlotSpec]
    participants: tuple[Participant, Participant]
    first_speaker: Optional[int]
    info_variant: str
    info_fields: tuple[str, ...]
    visibility: Mapping[str, bool]
    negotiation: Mapping[str, Any]
    llm: Mapping[str, Any]
    arbitration: Mapping[str, Any]
    scoring: Mapping[str, Any]
    budget: Mapping[str, Any]
    priority_order: tuple[str, ...]

    @property
    def swap_sides(self) -> bool:
        return bool(self.scenario_config.get("swap_sides", False))


class ExperimentConfig:
    def __init__(self, raw: Mapping[str, Any], source: str = "<config>"):
        self.source = source
        where = f"experiment config {source}"
        check_keys(
            raw,
            where,
            ("experiment_name", "condition", "scenario", "negotiation", "design"),
            (
                "schema_version",
                "description",
                "scenario_overrides",
                "llm",
                "arbitration",
                "scoring",
                "budget",
                "personas",
                "tasks",
            ),
        )
        if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
            raise ConfigError(f"{where}: schema_version {raw['schema_version']!r} is not supported")
        self.experiment_name = _identifier(raw["experiment_name"], f"{where}.experiment_name")
        self.condition = as_choice(raw["condition"], f"{where}.condition", CONDITIONS)
        self.description = " ".join(str(raw.get("description", "")).split())
        self.scenario_file = str(raw["scenario"])
        self.scenario_overrides = dict(raw.get("scenario_overrides") or {})

        self.negotiation = self._negotiation(raw["negotiation"], f"{where}.negotiation")
        self.llm = self._llm(raw.get("llm") or {}, f"{where}.llm")
        self.arbitration = self._arbitration(raw.get("arbitration") or {}, f"{where}.arbitration")
        self.scoring = self._scoring(raw.get("scoring") or {}, f"{where}.scoring")
        self.budget = self._budget(raw.get("budget") or {}, f"{where}.budget")
        if (self.condition == "C0") == self.negotiation["enabled"]:
            raise ConfigError(
                f"{where}: condition C0 is 'no LLM, Strategy 1 only', so negotiation.enabled must "
                "be false for C0 and true for every other condition"
            )
        if self.scoring["ground_truth"] is not None and self.condition not in ("C0", "C1"):
            raise ConfigError(
                f"{where}: scoring.ground_truth is set for condition {self.condition}. Only C0 and "
                "C1 are scored against a ground truth; persona conditions have none."
            )

        self.tasks = TaskTable.load(raw.get("tasks", DEFAULT_TASKS_FILE))
        self.personas_file = raw.get("personas")
        self._personas: Optional[dict[str, Persona]] = None
        self.design = dict(raw["design"])
        self._where = where
        self._plans = self._expand()

    @classmethod
    def load(cls, path: Path | str) -> "ExperimentConfig":
        raw = load_yaml(resolve_path(path))
        if not isinstance(raw, Mapping):
            raise ConfigError(f"{path}: expected a mapping at the top level")
        return cls(raw, source=str(path))

    def plans(self) -> list[RunPlan]:
        return list(self._plans)

    # --- sections ---------------------------------------------------------------------

    @staticmethod
    def _negotiation(raw: Any, where: str) -> dict[str, Any]:
        check_keys(
            raw,
            where,
            ("enabled",),
            ("template", "max_messages_per_agent", "timing", "info_fields", "visibility"),
        )
        enabled = as_bool(raw["enabled"], f"{where}.enabled")
        timing = raw.get("timing") or {}
        check_keys(timing, f"{where}.timing", (), ("mode", "seconds_per_message"))
        settings = {
            "enabled": enabled,
            "template": raw.get("template"),
            # "each robot has sent four messages with no agreement" (arXiv:2503.12333v1, Sec IV-C)
            "max_messages_per_agent": int(
                as_number(raw.get("max_messages_per_agent", 4), f"{where}.max_messages_per_agent", minimum=1)
            ),
            "timing": {
                "mode": as_choice(timing.get("mode", "pre_conflict"), f"{where}.timing.mode", TIMING_MODES),
                # "each message is generated within one second" (Sec IV-C)
                "seconds_per_message": as_number(
                    timing.get("seconds_per_message", 1.0),
                    f"{where}.timing.seconds_per_message",
                    minimum=0.0,
                    strict_minimum=True,
                ),
            },
            "info_fields": resolve_info_fields(raw.get("info_fields", "none")),
            "visibility": resolve_visibility(raw.get("visibility", "default")),
        }
        if enabled:
            if not settings["template"]:
                raise ConfigError(f"{where}.template: needed when negotiation is enabled")
            load_template(settings["template"])  # fails here, not mid-experiment
        return settings

    @staticmethod
    def _llm(raw: Any, where: str) -> dict[str, Any]:
        check_keys(raw, where, (), ("client", "model", "temperature", "max_tokens", "thinking", "mock_policy"))
        return {
            "client": as_choice(raw.get("client", "mock"), f"{where}.client", CLIENTS),
            "model": str(raw.get("model", "deepseek-flash")),
            "temperature": as_number(raw.get("temperature", 1.0), f"{where}.temperature", minimum=0.0),
            "max_tokens": int(as_number(raw.get("max_tokens", 300), f"{where}.max_tokens", minimum=1)),
            "thinking": as_choice(raw.get("thinking", "disabled"), f"{where}.thinking", ("disabled", "enabled")),
            "mock_policy": as_choice(
                raw.get("mock_policy", "first_speaker_goes"), f"{where}.mock_policy", sorted(MOCK_POLICIES)
            ),
        }

    @staticmethod
    def _arbitration(raw: Any, where: str) -> dict[str, Any]:
        check_keys(raw, where, (), ("policy", "tie_break"))
        return {
            "policy": as_choice(raw.get("policy", "strategy1"), f"{where}.policy", POLICIES),
            "tie_break": as_choice(raw.get("tie_break", "lower_index"), f"{where}.tie_break", TIE_BREAKS),
        }

    @staticmethod
    def _scoring(raw: Any, where: str) -> dict[str, Any]:
        check_keys(raw, where, (), ("ground_truth",))
        ground_truth = raw.get("ground_truth")
        if ground_truth is not None:
            as_choice(ground_truth, f"{where}.ground_truth", (GROUND_TRUTH_TASK_PRIORITY,))
        return {"ground_truth": ground_truth}

    @staticmethod
    def _budget(raw: Any, where: str) -> dict[str, Any]:
        check_keys(raw, where, (), ("cap_usd", "ledger"))
        return {
            "cap_usd": as_number(raw.get("cap_usd", 0.50), f"{where}.cap_usd", minimum=0.0),
            "ledger": str(raw.get("ledger", "spend_ledger.jsonl")),
        }

    # --- design -----------------------------------------------------------------------

    def _expand(self) -> list[RunPlan]:
        where = f"{self._where}.design"
        mode = as_choice(self.design.get("mode", "factorial"), f"{where}.mode", ("factorial", "explicit"))
        base_seed = int(as_number(self.design.get("seed", 0), f"{where}.seed", minimum=0))
        repeats = int(as_number(self.design.get("repeats", 1), f"{where}.repeats", minimum=1))
        info_variants = self._info_variants(self.design.get("info_variants"), where)

        if mode == "explicit":
            check_keys(self.design, where, ("runs",), ("mode", "seed", "repeats", "info_variants"))
            cells = self._explicit_cells(where)
        else:
            check_keys(
                self.design,
                where,
                ("pairs",),
                ("mode", "seed", "repeats", "info_variants", "scenario_variants", "assignment", "sides", "first_speaker"),
            )
            cells = self._factorial_cells(where)

        multi = {
            "variant": len({cell["variant"][0] for cell in cells}) > 1,
            "info": len(info_variants) > 1,
            "repeat": repeats > 1,
        }
        plans: list[RunPlan] = []
        for cell in cells:
            for info_name, info_fields in info_variants:
                for repeat in range(1, repeats + 1):
                    plans.append(self._plan(len(plans) + 1, base_seed, cell, info_name, info_fields, repeat, multi))
        if not plans:
            raise ConfigError(f"{where}: the design produces no runs")
        if len({plan.run_id for plan in plans}) != len(plans):
            raise ConfigError(f"{where}: two runs have the same id; give the variants distinct names")
        return plans

    def _info_variants(self, raw: Any, where: str) -> list[tuple[str, tuple[str, ...]]]:
        if raw is None:
            return [("default", self.negotiation["info_fields"])]
        if not isinstance(raw, list) or not raw:
            raise ConfigError(f"{where}.info_variants: expected a non-empty list")
        variants = []
        for index, entry in enumerate(raw):
            check_keys(entry, f"{where}.info_variants[{index}]", ("name", "info_fields"))
            variants.append(
                (_identifier(entry["name"], f"{where}.info_variants[{index}].name"), resolve_info_fields(entry["info_fields"]))
            )
        return variants

    def _factorial_cells(self, where: str) -> list[dict[str, Any]]:
        pairs = self.design["pairs"]
        if not isinstance(pairs, list) or not pairs:
            raise ConfigError(f"{where}.pairs: expected a non-empty list of pairs")
        variants_raw = self.design.get("scenario_variants") or [{"name": "base", "overrides": {}}]
        variants = []
        for index, entry in enumerate(variants_raw):
            check_keys(entry, f"{where}.scenario_variants[{index}]", ("name",), ("overrides",))
            variants.append(
                (_identifier(entry["name"], f"{where}.scenario_variants[{index}].name"), dict(entry.get("overrides") or {}))
            )
        levels = {
            factor: _LEVELS[factor][
                as_choice(self.design.get(factor, default), f"{where}.{factor}", _LEVELS[factor])
            ]
            for factor, default in (("assignment", "fixed"), ("sides", "fixed"), ("first_speaker", "agent_0"))
        }
        speakers = levels["first_speaker"] if self.negotiation["enabled"] else (None,)

        cells = []
        for index, pair in enumerate(pairs):
            slots = self._pair(pair, f"{where}.pairs[{index}]")
            for variant in variants:
                for swapped_assignment in levels["assignment"]:
                    for swap_sides in levels["sides"]:
                        for speaker in speakers:
                            cells.append(
                                {
                                    "slots": slots[::-1] if swapped_assignment else slots,
                                    "variant": variant,
                                    "swap_sides": swap_sides,
                                    "first_speaker": speaker,
                                }
                            )
        return cells

    def _explicit_cells(self, where: str) -> list[dict[str, Any]]:
        runs = self.design["runs"]
        if not isinstance(runs, list) or not runs:
            raise ConfigError(f"{where}.runs: expected a non-empty list of runs")
        cells = []
        for index, run in enumerate(runs):
            label = f"{where}.runs[{index}]"
            check_keys(run, label, ("agents",), ("first_speaker", "swap_sides", "variant", "scenario_overrides"))
            speaker: Optional[int] = None
            if self.negotiation["enabled"]:
                speaker = run.get("first_speaker", 0)
                if speaker not in (0, 1):
                    raise ConfigError(f"{label}.first_speaker: expected 0 or 1, got {speaker!r}")
            cells.append(
                {
                    "slots": self._pair(run["agents"], f"{label}.agents"),
                    "variant": (
                        _identifier(run.get("variant", "base"), f"{label}.variant"),
                        dict(run.get("scenario_overrides") or {}),
                    ),
                    "swap_sides": as_bool(run.get("swap_sides", False), f"{label}.swap_sides"),
                    "first_speaker": speaker,
                }
            )
        return cells

    @staticmethod
    def _pair(raw: Any, where: str) -> tuple[SlotSpec, SlotSpec]:
        if not isinstance(raw, (list, tuple)) or len(raw) != 2:
            raise ConfigError(f"{where}: expected exactly two participants")
        return SlotSpec.parse(raw[0], f"{where}[0]"), SlotSpec.parse(raw[1], f"{where}[1]")

    def _plan(
        self,
        index: int,
        base_seed: int,
        cell: Mapping[str, Any],
        info_name: str,
        info_fields: tuple[str, ...],
        repeat: int,
        multi: Mapping[str, bool],
    ) -> RunPlan:
        seed = base_seed + index
        rng = random.Random(seed)
        slots: tuple[SlotSpec, SlotSpec] = cell["slots"]
        participants = (self._participant(0, slots[0], rng), self._participant(1, slots[1], rng))
        variant_name, variant_overrides = cell["variant"]
        overrides = deep_merge(self.scenario_overrides, variant_overrides)
        overrides = deep_merge(overrides, {"swap_sides": cell["swap_sides"]})
        scenario_config = load_scenario_config(self.scenario_file, overrides)
        try:
            build_scenario(scenario_config)
        except ConfigError as exc:
            raise ConfigError(f"{self._where}: run {index}: {exc}") from exc

        self._check_scoring(participants, index)
        if self.negotiation["enabled"]:
            template = load_template(self.negotiation["template"])
            if template.requires_persona and any(p.persona is None for p in participants):
                raise ConfigError(
                    f"{self._where}: run {index}: template {template.key!r} needs a persona for "
                    "every participant"
                )

        parts = [f"{index:03d}", f"{slots[0].label}-vs-{slots[1].label}"]
        if multi["variant"]:
            parts.append(variant_name)
        if multi["info"]:
            parts.append(info_name)
        if cell["first_speaker"] is not None:
            parts.append(f"fs{cell['first_speaker']}")
        if cell["swap_sides"]:
            parts.append("swap")
        if multi["repeat"]:
            parts.append(f"r{repeat}")

        return RunPlan(
            index=index,
            run_id="_".join(parts),
            experiment_name=self.experiment_name,
            condition=self.condition,
            seed=seed,
            repeat=repeat,
            scenario_file=self.scenario_file,
            scenario_variant=variant_name,
            scenario_config=scenario_config,
            slots=slots,
            participants=participants,
            first_speaker=cell["first_speaker"],
            info_variant=info_name,
            info_fields=info_fields,
            visibility=self.negotiation["visibility"],
            negotiation=self.negotiation,
            llm=self.llm,
            arbitration=self.arbitration,
            scoring=self.scoring,
            budget=self.budget,
            priority_order=self.tasks.priority_order,
        )

    def _participant(self, agent_id: int, slot: SlotSpec, rng: random.Random) -> Participant:
        if slot.task_type is not None and slot.task_type not in self.tasks.task_strings:
            raise ConfigError(
                f"{self._where}: unknown task_type {slot.task_type!r}; known: "
                f"{sorted(self.tasks.task_strings)}"
            )
        # "Each agent was randomly given one of the task strings from their type's set"
        # (arXiv:2503.12333v1, Sec V-A). The draw is made from the run's seed either way,
        # so that adding a persona to a run does not change which string the other agent gets.
        drawn = rng.choice(self.tasks.task_strings[slot.task_type]) if slot.task_type else None
        if slot.persona is None:
            return Participant(agent_id, task=drawn, task_type=slot.task_type)

        personas = self._load_personas()
        if slot.persona not in personas:
            raise ConfigError(
                f"{self._where}: unknown persona {slot.persona!r}; known: {sorted(personas)}"
            )
        overrides = dict(slot.overrides)
        if "task" not in overrides and drawn is not None:
            overrides["task"] = drawn
        try:
            persona = personas[slot.persona].with_overrides(**overrides)
        except PersonaError as exc:
            raise ConfigError(f"{self._where}: {exc}") from exc
        return Participant(agent_id, task=persona.task, task_type=slot.task_type, persona=persona)

    def _load_personas(self) -> dict[str, Persona]:
        if self._personas is None:
            if not self.personas_file:
                raise ConfigError(
                    f"{self._where}: a participant refers to a persona, but the config has no "
                    "'personas' file"
                )
            try:
                self._personas = load_personas(self.personas_file)
            except PersonaError as exc:
                raise ConfigError(str(exc)) from exc
        return self._personas

    def _check_scoring(self, participants: Sequence[Participant], index: int) -> None:
        """Ground truth exists only for task-only participants of different, known types."""
        if self.scoring["ground_truth"] != GROUND_TRUTH_TASK_PRIORITY:
            return
        where = f"{self._where}: run {index}"
        if any(participant.persona is not None for participant in participants):
            raise ConfigError(
                f"{where}: scoring.ground_truth is set, but a participant has a persona. Only "
                "task-only conditions (C0, C1) have a ground truth; persona conditions are "
                "recorded without being marked correct or incorrect."
            )
        types = [participant.task_type for participant in participants]
        if types[0] == types[1]:
            raise ConfigError(
                f"{where}: both participants have task type {types[0]!r}, so there is no "
                "higher-priority agent to score against"
            )


def _identifier(value: Any, where: str) -> str:
    text = str(value)
    if not text or not all(ch.isalnum() or ch in "_-" for ch in text):
        raise ConfigError(f"{where}: use letters, digits, '_' and '-' only, got {value!r}")
    return text
