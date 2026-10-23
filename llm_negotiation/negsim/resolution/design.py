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

**The core and situational factors** (issue #60, RF-5; ``negsim.resolution.factors``) are
optional: a config that names none of them has the same cells, session ids and records as
before. Each core factor has two levels, ``neither`` (both people at the base level) and ``p1``
(person 1 at the other level, person 2 at the base); ``mapping`` balances which of the case's
agents is person 1.

``urgency``               ``neither`` or ``p1``: both errands routine, or person 1's urgent.
                          The two-level form of ``task``: a design has one or the other
``mobility_aid``, ``load``, ``distraction``, ``assertiveness``, ``residence``, ``memory_note``
                          ``neither`` or ``p1``
``<name>_visible``        ``true`` or ``false``, for ``mobility_aid``, ``load`` and
                          ``distraction``: whether others are told it (a switch of a factor
                          the design varies; ``true`` when left out)
``surroundings``          ``quiet`` or ``busy``: the setting, the same for both
``time_of_day``           ``daytime`` or ``late_night``: the same

**The pairwise perception factors** (issue #61, RF-6; ``negsim.resolution.pairwise``) are optional
too: a config that names none of them has the same cells, ids and records as before. Each is a
level of how one person sees the other; 0 is person 1 and 1 is person 2.

``attractiveness_0_sees_1``  ``unremarkable`` or ``attractive``: how person 1 sees person 2
``attractiveness_1_sees_0``  the same, person 2 looking at person 1
``familiarity``              ``strangers`` or ``acquaintances``: the same for both
``attractiveness_visible``, ``familiarity_visible``
                             ``true`` or ``false``: whether the observer is told it at all (a
                             switch of a factor the design varies; ``true`` when left out)

A session's ``pairwise`` block holds them in issue #61's format. Perceived attractiveness is off
unless a design names it, and a paid run with it waits for the ethics sign-off
(``negsim.ethics``; ``experiment.py``).

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
from ..personas.schema import ATTRIBUTES, FACTOR_ATTRIBUTES
from ..rulegen.design import DEFAULT_TASKS, FACTOR_LEVELS as RULEGEN_LEVELS, personas_of, visibility_of
from .factors import SITUATIONS, SWITCHES
from .pairwise import ATTRACTIVENESS_FACTORS, DESIGN_FACTORS as PAIRWISE_DESIGN, LEVELS as PAIRWISE_LEVELS, SWITCHES as PAIRWISE_SWITCHES, block_for
from .view import CONDITIONS

#: The factors of issue #58: a design names all of them, but ``task`` may give way to ``urgency``.
FACTORS = ("age_pair", "gender_pair", "task", "demographics_visible", "mapping")
#: The core factors of issue #60, coded by who has the other level.
NEITHER, P1 = "neither", "p1"
PERSON_FACTORS = FACTOR_ATTRIBUTES
SWITCH_FACTORS = tuple(SWITCHES.values())
SITUATION_FACTORS = tuple(SITUATIONS)
#: The factors of issue #60 (RF-5).
RF5_FACTORS = (*PERSON_FACTORS, *SWITCH_FACTORS, *SITUATION_FACTORS)
#: The pairwise perception factors of issue #61 (RF-6), and their switches.
PAIRWISE_FACTORS = tuple(PAIRWISE_DESIGN)
PAIRWISE_SWITCH_FACTORS = tuple(PAIRWISE_SWITCHES.values())
#: Every factor, in the order a cell, its id and an outcome row list them; the factors of
#: issue #58 keep their order among themselves.
ALL_FACTORS = (
    "age_pair", "gender_pair", "task", *PERSON_FACTORS, "demographics_visible", *SWITCH_FACTORS, *SITUATION_FACTORS,
    *PAIRWISE_FACTORS, *PAIRWISE_SWITCH_FACTORS, "mapping",
)
FACTOR_LEVELS: dict[str, tuple[Any, ...]] = {
    **{name: RULEGEN_LEVELS[name] for name in FACTORS},
    **{name: (NEITHER, P1) for name in PERSON_FACTORS},
    **{name: (True, False) for name in SWITCH_FACTORS},
    **SITUATIONS,
    **{name: PAIRWISE_LEVELS[factor] for name, (factor, _, _) in PAIRWISE_DESIGN.items()},
    **{name: (True, False) for name in PAIRWISE_SWITCH_FACTORS},
}
REQUIRED = ("age_pair", "gender_pair", "demographics_visible", "mapping")
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

    @property
    def factors(self) -> tuple[str, ...]:
        """The factors this design varies, in :data:`ALL_FACTORS` order."""
        return tuple(name for name in ALL_FACTORS if name in self.levels)

    @property
    def uses_factors(self) -> bool:
        """Whether it varies a core or situational factor of issue #60."""
        return any(name in RF5_FACTORS for name in self.levels)

    @property
    def uses_pairwise(self) -> bool:
        """Whether it varies a pairwise perception factor of issue #61."""
        return any(name in PAIRWISE_FACTORS for name in self.levels)

    @property
    def uses_attractiveness(self) -> bool:
        """Whether it varies perceived attractiveness: then a paid run needs the ethics sign-off."""
        return any(name in ATTRACTIVENESS_FACTORS for name in self.levels)

    @classmethod
    def from_config(cls, raw: Any, where: str = "design") -> "ResolutionDesign":
        check_keys(raw, where, ("seed", "factors"), ("repeats", "base_age", "age_difference", "tasks"))
        factors = check_keys(raw["factors"], f"{where}.factors", REQUIRED, tuple(name for name in ALL_FACTORS if name not in REQUIRED))
        if ("task" in factors) == ("urgency" in factors):
            raise ConfigError(f"{where}.factors: name task or urgency (its two-level form), not both and not neither")
        for attribute, switch in SWITCHES.items():
            if switch in factors and attribute not in factors:
                raise ConfigError(f"{where}.factors.{switch}: switches {attribute}, which the design does not vary")
        for factor, switch in PAIRWISE_SWITCHES.items():
            setting = [name for name, (of, _, _) in PAIRWISE_DESIGN.items() if of == factor]
            if switch in factors and not any(name in factors for name in setting):
                raise ConfigError(f"{where}.factors.{switch}: switches {factor}, which the design does not vary (name {' or '.join(setting)})")
        levels = {}
        for name in (name for name in ALL_FACTORS if name in factors):
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
        return math.prod(len(self.levels[name]) for name in self.factors)

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
    """Eight hexadecimal characters that name a cell of the design (of the factors it has, so a
    cell of the factors of issue #58 keeps its code)."""
    return hashlib.sha256(json.dumps({name: cell[name] for name in ALL_FACTORS if name in cell}, sort_keys=True).encode("utf-8")).hexdigest()[:8]


def personas_for(cell: Mapping[str, Any], agents: tuple[int, int], design: "ResolutionDesign") -> dict[int, dict[str, Any]]:
    """The two people of a cell, each assigned to an agent: the age, gender, errand and urgency
    of issue #30, then each core factor the cell varies (issue #60). ``urgency`` picks both errands."""
    people = personas_of({**cell, "task": cell.get("task", "none")}, agents, design)
    lower, higher = agents
    first, second = (lower, higher) if cell["mapping"] == "p1_lower" else (higher, lower)
    for name in PERSON_FACTORS:
        if name not in cell:
            continue
        base, other = ATTRIBUTES[name].levels
        for agent, level in ((first, other if cell[name] == P1 else base), (second, base)):
            if name == "urgency":
                people[agent]["task"] = design.tasks[level]
            people[agent][name] = level
    return people


def visibility_for(cell: Mapping[str, Any]) -> dict[str, bool]:
    """The visibility settings of issue #30, and the switch of each observable core factor the
    cell varies (on unless the cell switches it off)."""
    visibility = visibility_of(cell)
    for attribute, switch in SWITCHES.items():
        if attribute in cell:
            visibility[attribute] = bool(cell.get(switch, True))
    for factor, switch in PAIRWISE_SWITCHES.items():  # issue #61: whether the observer is told it
        if any(name in cell for name, (of, _, _) in PAIRWISE_DESIGN.items() if of == factor):
            visibility[factor] = bool(cell.get(switch, True))
    return visibility


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
    #: The two people's personas: ``age``, ``gender``, ``task`` (text or None), ``urgency``, and
    #: each core factor the design varies (issue #60).
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

    @property
    def factor_levels(self) -> dict[int, dict[str, str]]:
        """Each person's levels of the core factors the design varies (``urgency`` included)."""
        return {agent: {name: persona[name] for name in PERSON_FACTORS if name in persona} for agent, persona in self.personas.items()}

    @property
    def situation(self) -> dict[str, str]:
        """The levels of the situational factors the design varies."""
        return {name: self.cell[name] for name in SITUATION_FACTORS if name in self.cell}

    @property
    def uses_factors(self) -> bool:
        return any(name in RF5_FACTORS for name in self.cell)

    @property
    def uses_pairwise(self) -> bool:
        return any(name in PAIRWISE_FACTORS for name in self.cell)

    @property
    def persons(self) -> tuple[int, int]:
        """The agents of person 1 and person 2, in that order."""
        first = self.agents[0] if self.cell["mapping"] == "p1_lower" else self.agents[1]
        return (first, self.agents[1] if first == self.agents[0] else self.agents[0])

    @property
    def pairwise(self) -> Optional[dict[str, Any]]:
        """The session's pairwise block (issue #61), rows person 1 then person 2; ``None`` if the
        design varies no pairwise factor."""
        return block_for(self.cell, self.persons)

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
            **({"pairwise": self.pairwise} if self.uses_pairwise else {}),  # issue #61: only when the design has one
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
            for values in itertools.product(*(design.levels[name] for name in design.factors)):
                cell = dict(zip(design.factors, values))
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
            personas=personas_for(cell, agents, design), visibility=visibility_for(cell),
        )
        for index, (session_id, condition, case_id, version, agents, scenario, cell, repeat) in enumerate(order, start=1)
    ]
