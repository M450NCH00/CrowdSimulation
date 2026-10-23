"""The sessions of a resolution experiment (issue #58, RF-3): which two people meet in which case,
under which condition.

The factors are issue #30's (``negsim.rulegen.design``), less speaking order: in this layer the
agents at one decision point are all prompted on the same world state, so nobody speaks first.

``age_pair``              ``same``, ``p1_older`` or ``p2_older``
``gender_pair``           ``same_female``, ``same_male``, ``p1_female`` or ``p1_male``
``task``                  ``none``, ``p1_urgent`` or ``p2_urgent``: each person's errand
``demographics_visible``  ``true`` or ``false``: whether age and gender are in what anyone is told
``mapping``               ``p1_lower`` or ``p1_higher``: which of the case's two agents is person 1

Person 1 and person 2 are slots of the design: the case's two people (``case["agents"]``). In a
crowd case anyone else the scenario brings into the encounter has no persona. The session list
is the full factorial for every condition and case, each cell ``repeats`` times, shuffled by the
design's seed. A cell run more than once is in the **exact-repeat set** (D14): identical
prompts, which measure the model's own randomness. RF-7 (#62) builds the screening designs.

The fictional group (issue #32) is not a factor of this layer: it stays off (track #55).
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError, as_number, check_keys
from ..rulegen.design import DEFAULT_TASKS, FACTOR_LEVELS as RULEGEN_LEVELS, personas_of, visibility_of
from .view import CONDITIONS

FACTORS = ("age_pair", "gender_pair", "task", "demographics_visible", "mapping")
FACTOR_LEVELS: dict[str, tuple[Any, ...]] = {name: RULEGEN_LEVELS[name] for name in FACTORS}
CONDITION_LETTER = {"independent": "I", "non_verbal": "N", "talk": "T"}


@dataclass(frozen=True)
class ResolutionDesign:
    seed: int
    levels: Mapping[str, tuple[Any, ...]]
    repeats: int = 1
    base_age: int = 25
    age_difference: int = 45
    tasks: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_TASKS))

    #: ``personas_of`` reads it: the fictional group is never on in this layer.
    groups = None

    @classmethod
    def from_config(cls, raw: Any, where: str = "design") -> "ResolutionDesign":
        check_keys(raw, where, ("seed", "factors"), ("repeats", "base_age", "age_difference", "tasks"))
        factors = check_keys(raw["factors"], f"{where}.factors", FACTORS)
        levels = {}
        for name in FACTORS:
            chosen = factors[name]
            allowed = FACTOR_LEVELS[name]
            if not isinstance(chosen, list) or not chosen:
                raise ConfigError(f"{where}.factors.{name}: a non-empty list of levels from {list(allowed)}")
            unknown = [level for level in chosen if level not in allowed or isinstance(level, bool) != isinstance(allowed[0], bool)]
            if unknown:
                raise ConfigError(f"{where}.factors.{name}: unknown level(s) {unknown}; the levels are {list(allowed)}")
            if len(set(chosen)) != len(chosen):
                raise ConfigError(f"{where}.factors.{name}: a level is listed twice")
            levels[name] = tuple(chosen)
        base_age = int(as_number(raw.get("base_age", 25), f"{where}.base_age", minimum=1))
        difference = int(as_number(raw.get("age_difference", 45), f"{where}.age_difference", minimum=1))
        if base_age + difference > 120:
            raise ConfigError(f"{where}: base_age + age_difference must be a possible age, at most 120")
        tasks = dict(DEFAULT_TASKS)
        if raw.get("tasks") is not None:
            check_keys(raw["tasks"], f"{where}.tasks", ("urgent", "routine"))
            tasks = {key: " ".join(str(raw["tasks"][key]).split()) for key in ("urgent", "routine")}
        return cls(
            seed=int(as_number(raw["seed"], f"{where}.seed", minimum=0)),
            levels=levels,
            repeats=int(as_number(raw.get("repeats", 1), f"{where}.repeats", minimum=1)),
            base_age=base_age,
            age_difference=difference,
            tasks=tasks,
        )

    def cells(self) -> int:
        return math.prod(len(self.levels[name]) for name in FACTORS)

    def as_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "factors": {name: list(levels) for name, levels in self.levels.items()},
            "repeats": self.repeats,
            "base_age": self.base_age,
            "age_difference": self.age_difference,
            "tasks": dict(self.tasks),
        }


def cell_code(cell: Mapping[str, Any]) -> str:
    """Eight hexadecimal characters that name a cell of the design."""
    return hashlib.sha256(json.dumps({name: cell[name] for name in FACTORS}, sort_keys=True).encode("utf-8")).hexdigest()[:8]


@dataclass(frozen=True)
class Session:
    session_id: str
    index: int
    condition: str
    case_id: str
    case_version: int
    scenario: str  # the plug-in
    agents: tuple[int, int]  # the case's two people
    cell: Mapping[str, Any]
    repeat: int
    exact_repeat_set: bool
    #: The two people's personas: ``age``, ``gender``, ``task`` (text or None), ``urgency``.
    personas: Mapping[int, Mapping[str, Any]]
    visibility: Mapping[str, bool]

    @property
    def people(self) -> dict[int, dict[str, Any]]:
        """What the protocol tells each of the two about themselves and sees of the other:
        ``age``, ``gender`` and ``errand`` (the perceiver's keys)."""
        return {
            agent: {"age": persona["age"], "gender": persona["gender"], **({"errand": persona["task"]} if persona["task"] else {})}
            for agent, persona in self.personas.items()
        }

    def person_of(self, agent: int) -> Optional[int]:
        """1 or 2: which person of the design ``agent`` is; ``None`` for anyone else."""
        first = self.agents[0] if self.cell["mapping"] == "p1_lower" else self.agents[1]
        return 1 if agent == first else 2 if agent in self.agents else None

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "index": self.index,
            "condition": self.condition,
            "case_id": self.case_id,
            "case_version": self.case_version,
            "scenario": self.scenario,
            "agents": list(self.agents),
            "cell": dict(self.cell),
            "repeat": self.repeat,
            "exact_repeat_set": self.exact_repeat_set,
            "personas": {str(agent): dict(persona) for agent, persona in sorted(self.personas.items())},
            "visibility": dict(self.visibility),
        }


def sessions_for(
    cases: Sequence[tuple[str, int, tuple[int, int], str]],
    design: ResolutionDesign,
    conditions: Sequence[str],
    experiment: str,
) -> list[Session]:
    """Every condition, case and cell, each ``design.repeats`` times; shuffled by the design's seed.
    ``cases`` are ``(case_id, version, agents, scenario plug-in)``. Ids come from what a session is."""
    unordered = []
    for condition in conditions:
        if condition not in CONDITIONS:
            raise ConfigError(f"unknown condition {condition!r}; the conditions are {list(CONDITIONS)}")
        for case_id, version, agents, scenario in cases:
            for values in itertools.product(*(design.levels[name] for name in FACTORS)):
                cell = dict(zip(FACTORS, values))
                for repeat in range(1, design.repeats + 1):
                    session_id = f"{CONDITION_LETTER[condition]}_{case_id}_{cell_code(cell)}_r{repeat}"
                    unordered.append((session_id, condition, case_id, version, tuple(sorted(agents)), scenario, cell, repeat))
    ids = [entry[0] for entry in unordered]
    if len(set(ids)) != len(ids):
        raise ConfigError(f"experiment {experiment}: two sessions have the same id; a case is listed twice")
    order = sorted(unordered, key=lambda entry: entry[0])
    random.Random(f"{experiment}:{design.seed}").shuffle(order)
    return [
        Session(
            session_id=session_id, index=index, condition=condition, case_id=case_id, case_version=version,
            scenario=scenario, agents=agents, cell=cell, repeat=repeat, exact_repeat_set=design.repeats > 1,
            personas=personas_of(cell, agents, design), visibility=visibility_of(cell),
        )
        for index, (session_id, condition, case_id, version, agents, scenario, cell, repeat) in enumerate(order, start=1)
    ]
