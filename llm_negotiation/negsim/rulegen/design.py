"""The persona design matrix: which persona pair meets in which case, in which order (issue #30, Part 3).

A case is geometry; a **session** puts two people into it. So that later analysis can tell
the effects of geometry, age, gender and task apart, the people are varied by factors,
crossed in full, each of whose levels an experiment config lists:

``age_pair``              ``same`` (both ``base_age``), ``p1_older`` or ``p2_older`` (by
                          ``age_difference`` years)
``gender_pair``           ``same_female``, ``same_male``, ``p1_female`` (person 1 a woman,
                          person 2 a man) or ``p1_male``
``task``                  ``none`` (no private information), ``p1_urgent`` (person 1's errand
                          is urgent, person 2's routine) or ``p2_urgent``
``demographics_visible``  ``true`` or ``false``. False is the control: age and gender appear
                          in neither the situation description nor the field glossary
``mapping``               ``p1_lower`` (person 1 is the case's lower-numbered agent) or
                          ``p1_higher``
``order``                 ``lower_first`` or ``higher_first``: who speaks first (condition A),
                          or who is described first, as "Person 1" (condition B)

Person 1 and person 2 are slots of the design, not names: a session's people have an age, a
gender and possibly an errand, and nothing else (``docs/rule-generation.md``, section 2).
The session list is the full factorial for every case and condition, so every level of
every factor occurs equally often within each; it is in an order shuffled by the design's
seed, and every session has an id derived from what it is, so the list is reproducible.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from ..avoidance.perception import default_visibility
from ..configutil import ConfigError, as_number, check_keys

CONDITION_NEGOTIATED, CONDITION_STATED = "negotiated", "stated"
CONDITIONS = (CONDITION_NEGOTIATED, CONDITION_STATED)
CONDITION_LETTER = {CONDITION_NEGOTIATED: "A", CONDITION_STATED: "B"}

FACTOR_LEVELS: dict[str, tuple[Any, ...]] = {
    "age_pair": ("same", "p1_older", "p2_older"),
    "gender_pair": ("same_female", "same_male", "p1_female", "p1_male"),
    "task": ("none", "p1_urgent", "p2_urgent"),
    "demographics_visible": (True, False),
    "mapping": ("p1_lower", "p1_higher"),
    "order": ("lower_first", "higher_first"),
}
FACTORS = tuple(FACTOR_LEVELS)
#: The two errands of differing urgency, unless a config gives its own. Each completes "on
#: your way to ...". Taken from GameChat's task table (configs/tasks/gamechat_tasks.yaml):
#: a hospital errand, highest in its priority order, and a grocery errand, lowest.
DEFAULT_TASKS = {"urgent": "the emergency room", "routine": "the supermarket"}


@dataclass(frozen=True)
class DesignSettings:
    """The factors' levels, and what the levels mean in years and in words."""

    seed: int
    levels: Mapping[str, tuple[Any, ...]]
    base_age: int
    age_difference: int
    tasks: Mapping[str, str]
    per_case: Mapping[str, Mapping[str, tuple[Any, ...]]] = field(default_factory=dict)

    @classmethod
    def from_config(cls, raw: Any, where: str = "design") -> "DesignSettings":
        check_keys(raw, where, ("seed", "factors"), ("base_age", "age_difference", "tasks", "per_case"))
        levels = cls._levels(raw["factors"], f"{where}.factors", require_all=True)
        per_case = {}
        for case_id, factors in (raw.get("per_case") or {}).items():
            per_case[str(case_id)] = cls._levels(factors, f"{where}.per_case.{case_id}", require_all=False)
        base_age = int(as_number(raw.get("base_age", 25), f"{where}.base_age", minimum=1))
        difference = int(as_number(raw.get("age_difference", 45), f"{where}.age_difference", minimum=1))
        if base_age + difference > 120:
            raise ConfigError(f"{where}: base_age + age_difference must be a possible age, at most 120")
        tasks = dict(DEFAULT_TASKS)
        if raw.get("tasks") is not None:
            check_keys(raw["tasks"], f"{where}.tasks", ("urgent", "routine"))
            tasks = {key: " ".join(str(raw["tasks"][key]).split()) for key in ("urgent", "routine")}
        return cls(int(as_number(raw["seed"], f"{where}.seed", minimum=0)), levels, base_age, difference, tasks, per_case)

    @staticmethod
    def _levels(raw: Any, where: str, require_all: bool) -> dict[str, tuple[Any, ...]]:
        check_keys(raw, where, FACTORS if require_all else (), FACTORS)
        levels = {}
        for name, chosen in raw.items():
            if not isinstance(chosen, list) or not chosen:
                raise ConfigError(f"{where}.{name}: expected a non-empty list of levels from {list(FACTOR_LEVELS[name])}")
            unknown = [level for level in chosen if level not in FACTOR_LEVELS[name] or isinstance(level, bool) != isinstance(FACTOR_LEVELS[name][0], bool)]
            if unknown:
                raise ConfigError(f"{where}.{name}: unknown level(s) {unknown}; the levels are {list(FACTOR_LEVELS[name])}")
            if len(set(chosen)) != len(chosen):
                raise ConfigError(f"{where}.{name}: a level is listed twice")
            levels[name] = tuple(chosen)
        return levels

    def levels_for(self, case_id: str) -> dict[str, tuple[Any, ...]]:
        return {**self.levels, **self.per_case.get(case_id, {})}

    def as_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "factors": {name: list(levels) for name, levels in self.levels.items()},
            "base_age": self.base_age,
            "age_difference": self.age_difference,
            "tasks": dict(self.tasks),
            "per_case": {case: {name: list(levels) for name, levels in factors.items()} for case, factors in self.per_case.items()},
        }


@dataclass(frozen=True)
class Session:
    """One session of rule generation: a case, a cell of the design, a condition, a repeat."""

    session_id: str
    index: int
    condition: str
    case_id: str
    case_version: int
    agents: tuple[int, int]
    cell: Mapping[str, Any]
    repeat: int
    #: Each agent's persona: ``age``, ``gender``, ``task`` (text or None) and ``urgency``.
    personas: Mapping[int, Mapping[str, Any]]
    visibility: Mapping[str, bool]
    #: Condition A: the first speaker. Condition B: the agent described as Person 1.
    first: int

    @property
    def second(self) -> int:
        return self.agents[1] if self.first == self.agents[0] else self.agents[0]

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "index": self.index,
            "condition": self.condition,
            "case_id": self.case_id,
            "case_version": self.case_version,
            "agents": list(self.agents),
            "cell": dict(self.cell),
            "repeat": self.repeat,
            "personas": {str(agent): dict(persona) for agent, persona in sorted(self.personas.items())},
            "visibility": dict(self.visibility),
            "first": self.first,
        }


def cell_code(cell: Mapping[str, Any]) -> str:
    """Eight hexadecimal characters that name a cell of the design."""
    return hashlib.sha256(json.dumps({name: cell[name] for name in FACTORS}, sort_keys=True).encode("utf-8")).hexdigest()[:8]


def personas_of(cell: Mapping[str, Any], agents: tuple[int, int], settings: DesignSettings) -> dict[int, dict[str, Any]]:
    """The two people of a cell, each assigned to an agent of the case."""
    older = settings.base_age + settings.age_difference
    ages = {"same": (settings.base_age, settings.base_age), "p1_older": (older, settings.base_age), "p2_older": (settings.base_age, older)}[cell["age_pair"]]
    genders = {
        "same_female": ("female", "female"),
        "same_male": ("male", "male"),
        "p1_female": ("female", "male"),
        "p1_male": ("male", "female"),
    }[cell["gender_pair"]]
    urgencies = {"none": (None, None), "p1_urgent": ("urgent", "routine"), "p2_urgent": ("routine", "urgent")}[cell["task"]]
    people = [
        {
            "age": ages[k],
            "gender": genders[k],
            "task": None if urgencies[k] is None else settings.tasks[urgencies[k]],
            "urgency": urgencies[k],
        }
        for k in (0, 1)
    ]
    lower, higher = agents
    first, second = (lower, higher) if cell["mapping"] == "p1_lower" else (higher, lower)
    return {first: people[0], second: people[1]}


def visibility_of(cell: Mapping[str, Any]) -> dict[str, bool]:
    """What one agent can see of the other in a session: the defaults, with age and gender
    switched off when the cell hides demographics. A task is never visible."""
    visibility = default_visibility()
    if not cell["demographics_visible"]:
        visibility["age"] = visibility["gender"] = False
    return visibility


def sessions_for(
    cases: Sequence[tuple[str, int, tuple[int, int]]],
    settings: DesignSettings,
    conditions: Sequence[str],
    repeats: Mapping[str, int],
    experiment: str,
) -> list[Session]:
    """The full session list: for every condition and case, every cell of its factors, each
    as many times as its condition repeats; shuffled by the design's seed.

    ``cases`` are ``(case_id, version, agents)``. Session ids are derived from what a session
    is, never from its place in the list.
    """
    unordered = []
    for condition in conditions:
        if condition not in CONDITIONS:
            raise ConfigError(f"unknown condition {condition!r}; the conditions are {list(CONDITIONS)}")
        for case_id, version, agents in cases:
            levels = settings.levels_for(case_id)
            for values in itertools.product(*(levels[name] for name in FACTORS)):
                cell = dict(zip(FACTORS, values))
                for repeat in range(1, repeats.get(condition, 1) + 1):
                    session_id = f"{CONDITION_LETTER[condition]}_{case_id}_{cell_code(cell)}_r{repeat}"
                    unordered.append((session_id, condition, case_id, version, agents, cell, repeat))
    ids = [entry[0] for entry in unordered]
    if len(set(ids)) != len(ids):
        raise ConfigError(f"experiment {experiment}: two sessions have the same id; a case is listed twice")
    rng = random.Random(f"{experiment}:{settings.seed}")
    order = sorted(unordered, key=lambda entry: entry[0])
    rng.shuffle(order)
    sessions = []
    for index, (session_id, condition, case_id, version, agents, cell, repeat) in enumerate(order, start=1):
        lower, higher = agents
        sessions.append(
            Session(
                session_id=session_id,
                index=index,
                condition=condition,
                case_id=case_id,
                case_version=version,
                agents=agents,
                cell=cell,
                repeat=repeat,
                personas=personas_of(cell, agents, settings),
                visibility=visibility_of(cell),
                first=lower if cell["order"] == "lower_first" else higher,
            )
        )
    return sessions


def balance(sessions: Sequence[Session], by: Optional[Sequence[str]] = None) -> dict[str, Any]:
    """How often each level of each factor occurs, within each condition and case.

    A full factorial is balanced: within a block every level of a factor has the same count,
    and so has every pair of levels of two factors.
    """
    by = tuple(by or ("condition", "case_id"))
    blocks: dict[str, dict[str, dict[str, int]]] = {}
    for session in sessions:
        block = "/".join(str(getattr(session, key)) for key in by)
        counts = blocks.setdefault(block, {name: {} for name in FACTORS})
        for name in FACTORS:
            level = str(session.cell[name])
            counts[name][level] = counts[name].get(level, 0) + 1
    return blocks
