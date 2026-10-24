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
is every condition, case and cell, each cell ``repeats`` times, shuffled by the design's seed. A
cell run more than once is in the **exact-repeat set** (D14): identical prompts, which measure
the model's own randomness.

**Which cells** (issue #62, RF-7; ``screening.py``; ``docs/screening-designs.md``) is the
design's ``kind``:

``full``        every combination of the levels (the default, and the only kind before RF-7)
``fractional``  a regular 2^(k-p) fractional factorial of resolution IV or higher, of ``cells``
                16 or 32 (by default the fewer that hold the factors): two-level factors only,
                each a column of the fraction, ``mapping`` included, so that it stays
                counterbalanced; a factor at one level is the same in every cell
``sample``      ``cells`` cells drawn from the full factorial with the seed, each factor's levels
                as equally often as the number allows

Three more keys, each optional: ``geometries`` (D14), the cases the design runs on, of one
encounter type, every cell once on each and the geometry recorded on the session; ``exact_repeats``
(D14), ``{cells, times}``, that many cells, chosen with the seed and balanced, each run ``times``
times in all on one geometry; and ``counterfactual_pairs``, each a base cell and a factor, run as
two sessions identical but for that factor and linked by a ``pair_id``. A config with none of
the four keys (and no ``kind``) has the same cells, session ids and records as before.

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

**Real ethnicity** (issue #92, RF-26; ``negsim.resolution.ethnicity``; ``docs/ethnicity.md``)
replaces the fictional group of issue #32 in this track; the fictional group stays only in the
rule-generation layer. Optional too: a config that names neither factor is as before.

``ethnicity_pair``     ``same`` or ``different``: whether the two people are of one group. Each
                       session's two groups are drawn with the design's seed at the shares of
                       ``ethnicity_shares`` (default ``configs/resolution/ethnicity_sg_2026.yaml``),
                       person 1 first, and kept on the personas (``ethnicity``)
``ethnicity_visible``  ``true`` or ``false``: whether each is told the other's (a switch of
                       ``ethnicity_pair``; ``true`` when left out); one's own is always told

``ethnicity_draw`` (a key of the design, not a factor): ``real`` (the default), person 1 at the
shares; or ``balanced``, every group equally often in a fixed rotation, each session weighted back
to the shares (``ethnicity_weight``; ``ethnicity.py``).

A paid run that varies it waits for the ethics sign-off (``negsim.ethics``; ``experiment.py``).
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError, as_number, check_keys, resolve_path
from ..personas.schema import ATTRIBUTES, FACTOR_ATTRIBUTES
from ..rulegen.design import DEFAULT_TASKS, FACTOR_LEVELS as RULEGEN_LEVELS, personas_of, visibility_of
from .ethnicity import (
    DRAW_BALANCED, DRAW_REAL, DRAWS, ETHNICITY_FACTORS, PAIR_FACTOR, PAIR_LEVELS, SHARES_CONFIG, SWITCH_FACTOR, EthnicityShares,
    balanced_assignment, weights,
)
from .factors import SITUATIONS, SWITCHES
from .pairwise import ATTRACTIVENESS_FACTORS, DESIGN_FACTORS as PAIRWISE_DESIGN, LEVELS as PAIRWISE_LEVELS, SWITCHES as PAIRWISE_SWITCHES, block_for
from .screening import DesignError, aliasing_problems, balanced_sample, balanced_subset, fraction, smallest_runs
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
    "age_pair", "gender_pair", "task", *PERSON_FACTORS, PAIR_FACTOR, "demographics_visible", *SWITCH_FACTORS, SWITCH_FACTOR,
    *SITUATION_FACTORS, *PAIRWISE_FACTORS, *PAIRWISE_SWITCH_FACTORS, "mapping",
)
FACTOR_LEVELS: dict[str, tuple[Any, ...]] = {
    **{name: RULEGEN_LEVELS[name] for name in FACTORS},
    **{name: (NEITHER, P1) for name in PERSON_FACTORS},
    **{name: (True, False) for name in SWITCH_FACTORS},
    **SITUATIONS,
    **{name: PAIRWISE_LEVELS[factor] for name, (factor, _, _) in PAIRWISE_DESIGN.items()},
    **{name: (True, False) for name in PAIRWISE_SWITCH_FACTORS},
    PAIR_FACTOR: PAIR_LEVELS,  # issue #92
    SWITCH_FACTOR: (True, False),
}
REQUIRED = ("age_pair", "gender_pair", "demographics_visible", "mapping")
CONDITION_LETTER = {"independent": "I", "non_verbal": "N", "talk": "T"}
#: The kinds of design (issue #62): which cells of the full factorial a design runs.
KIND_FULL, KIND_FRACTIONAL, KIND_SAMPLE = "full", "fractional", "sample"
KINDS = (KIND_FULL, KIND_FRACTIONAL, KIND_SAMPLE)
#: A counterfactual pair's two sessions.
ROLE_BASE, ROLE_FLIPPED = "base", "flipped"


@dataclass(frozen=True)
class CounterfactualPair:
    """Two cells identical but for ``factor``: ``base``, and ``base`` with ``factor`` at ``to``."""

    base: Mapping[str, Any]
    factor: str
    to: Any

    @property
    def flipped(self) -> dict[str, Any]:
        return {**self.base, self.factor: self.to}

    @property
    def code(self) -> str:
        """Eight hexadecimal characters that name the pair: its base cell, factor and level."""
        named = {"base": cell_code(self.base), "factor": self.factor, "to": self.to}
        return hashlib.sha256(json.dumps(named, sort_keys=True).encode("utf-8")).hexdigest()[:8]

    def as_dict(self) -> dict[str, Any]:
        return {"base": dict(self.base), "factor": self.factor, "to": self.to}


@dataclass(frozen=True)
class ResolutionDesign:
    seed: int
    levels: Mapping[str, tuple[Any, ...]]
    repeats: int = 1
    base_age: int = 25
    age_difference: int = 45
    tasks: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_TASKS))
    #: Issue #62: which cells (``full``, ``fractional``, ``sample``), and how many (``None`` for a
    #: full design; for a fractional one, the run size, 16 or 32).
    kind: str = KIND_FULL
    size: Optional[int] = None
    #: Issue #62 (D14): the cases the design runs on, ``id`` or ``id@version``; empty when the
    #: config's ``cases`` choose them.
    geometries: tuple[str, ...] = ()
    #: Issue #62 (D14): ``(cells, times)`` of the exact-repeat set, or ``None``.
    exact_repeats: Optional[tuple[int, int]] = None
    counterfactual_pairs: tuple[CounterfactualPair, ...] = ()
    #: Whether the config named ``kind``: an older config is described as before.
    kind_given: bool = False
    #: Issue #92: the shares the groups are drawn at, for a design that varies ``ethnicity_pair``.
    ethnicity_shares: Optional[EthnicityShares] = None
    #: Issue #92: how the groups are drawn, ``real`` or ``balanced``.
    ethnicity_draw: str = DRAW_REAL

    #: ``personas_of`` reads it: the fictional group is never on in this layer.
    groups = None

    @property
    def factors(self) -> tuple[str, ...]:
        """The factors this design varies, in :data:`ALL_FACTORS` order."""
        return tuple(name for name in ALL_FACTORS if name in self.levels)

    @property
    def uses_factors(self) -> bool:
        """Whether it varies a core or situational factor of issue #60, or real ethnicity (issue
        #92), whose lines are in the factor template too."""
        return any(name in RF5_FACTORS or name in ETHNICITY_FACTORS for name in self.levels)

    @property
    def uses_ethnicity(self) -> bool:
        """Whether it varies real ethnicity (issue #92): then a paid run needs the ethics sign-off."""
        return PAIR_FACTOR in self.levels

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
        check_keys(
            raw, where, ("seed", "factors"),
            ("repeats", "base_age", "age_difference", "tasks", "kind", "cells", "geometries", "exact_repeats", "counterfactual_pairs",
             "ethnicity_shares", "ethnicity_draw"),
        )
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
        if SWITCH_FACTOR in factors and PAIR_FACTOR not in factors:
            raise ConfigError(f"{where}.factors.{SWITCH_FACTOR}: switches real ethnicity, which the design does not vary (name {PAIR_FACTOR})")
        for key in ("ethnicity_shares", "ethnicity_draw"):
            if raw.get(key) is not None and PAIR_FACTOR not in factors:
                raise ConfigError(f"{where}.{key}: for a design that varies {PAIR_FACTOR}")
        if raw.get("ethnicity_draw", DRAW_REAL) not in DRAWS:
            raise ConfigError(f"{where}.ethnicity_draw: one of {list(DRAWS)}, got {raw.get('ethnicity_draw')!r}")
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
        kind = str(raw.get("kind", KIND_FULL))
        if kind not in KINDS:
            raise ConfigError(f"{where}.kind: one of {list(KINDS)}, got {kind!r}")
        size = None
        if kind == KIND_FULL and raw.get("cells") is not None:
            raise ConfigError(f"{where}.cells: a full design has every cell; cells is for kind fractional or sample")
        if kind == KIND_SAMPLE and raw.get("cells") is None:
            raise ConfigError(f"{where}.cells: a sample needs the number of cells to draw")
        if raw.get("cells") is not None:
            size = int(as_number(raw["cells"], f"{where}.cells", minimum=1))
        design = cls(
            seed=int(as_number(raw["seed"], f"{where}.seed", minimum=0)),
            levels=levels,
            repeats=int(as_number(raw.get("repeats", 1), f"{where}.repeats", minimum=1)),
            base_age=base_age,
            age_difference=difference,
            tasks=tasks,
            kind=kind,
            size=size,
            geometries=cls._geometries(raw.get("geometries"), f"{where}.geometries"),
            kind_given="kind" in raw,
            ethnicity_shares=EthnicityShares.load(resolve_path(raw.get("ethnicity_shares") or SHARES_CONFIG)) if PAIR_FACTOR in factors else None,
            ethnicity_draw=str(raw.get("ethnicity_draw", DRAW_REAL)),
        )
        if kind == KIND_FRACTIONAL:
            try:
                design = replace(design, size=size or smallest_runs(len(design.screened)))
            except DesignError as exc:
                raise ConfigError(f"{where}: {exc}") from exc
        try:
            cells = design.cell_list()
        except DesignError as exc:
            raise ConfigError(f"{where}: {exc}") from exc
        if raw.get("exact_repeats") is not None:
            block = check_keys(raw["exact_repeats"], f"{where}.exact_repeats", ("cells", "times"))
            chosen = int(as_number(block["cells"], f"{where}.exact_repeats.cells", minimum=1))
            times = int(as_number(block["times"], f"{where}.exact_repeats.times", minimum=2))
            if chosen > len(cells):
                raise ConfigError(f"{where}.exact_repeats.cells: {chosen}, but the design has {len(cells)} cell(s)")
            if design.repeats > 1:
                raise ConfigError(f"{where}: repeats runs every cell again; exact_repeats picks a few. Name one, not both")
            design = replace(design, exact_repeats=(chosen, times))
        pairs = raw.get("counterfactual_pairs")
        if pairs is not None:
            if not isinstance(pairs, list) or not pairs:
                raise ConfigError(f"{where}.counterfactual_pairs: a non-empty list of {{base, factor, to}}")
            found = tuple(design._pair(entry, f"{where}.counterfactual_pairs[{k}]") for k, entry in enumerate(pairs))
            codes = [pair.code for pair in found]
            if len(set(codes)) != len(codes):
                raise ConfigError(f"{where}.counterfactual_pairs: a pair is listed twice")
            design = replace(design, counterfactual_pairs=found)
        return design

    @staticmethod
    def _geometries(raw: Any, where: str) -> tuple[str, ...]:
        if raw is None:
            return ()
        if not isinstance(raw, list) or not raw or not all(isinstance(entry, str) and entry for entry in raw):
            raise ConfigError(f"{where}: a non-empty list of case ids, each id or id@version")
        ids = [entry.partition("@")[0] for entry in raw]
        if len(set(ids)) != len(ids):
            raise ConfigError(f"{where}: a case is listed twice")
        return tuple(raw)

    def _pair(self, raw: Any, where: str) -> CounterfactualPair:
        """A counterfactual pair from the config: ``base`` gives a level of every factor the design
        varies (one with a single level may be left out), ``factor`` the one that differs, and
        ``to`` its other level (left out when the factor has only two levels)."""
        entry = check_keys(raw, where, ("base", "factor"), ("to",))
        base = check_keys(entry["base"], f"{where}.base", self.screened, tuple(name for name in self.factors if name not in self.screened))
        cell = {}
        for name in self.factors:
            level = base.get(name, self.levels[name][0])
            if level not in self.levels[name] or isinstance(level, bool) != isinstance(self.levels[name][0], bool):
                raise ConfigError(f"{where}.base.{name}: one of the design's levels, {list(self.levels[name])}, got {level!r}")
            cell[name] = level
        factor = entry["factor"]
        if factor not in self.factors:
            raise ConfigError(f"{where}.factor: a factor the design names, one of {list(self.factors)}, got {factor!r}")
        if factor == "mapping":
            raise ConfigError(f"{where}.factor: the two sessions of a pair keep the same mapping; flip another factor")
        allowed = FACTOR_LEVELS[factor]
        others = [level for level in allowed if level != cell[factor]]
        if "to" not in entry and len(others) != 1:
            raise ConfigError(f"{where}.to: {factor} has more than two levels; name the one to flip to, from {others}")
        to = entry.get("to", others[0] if others else None)
        if to not in others or isinstance(to, bool) != isinstance(allowed[0], bool):
            raise ConfigError(f"{where}.to: a level of {factor} other than the base's, one of {others}, got {to!r}")
        return CounterfactualPair(cell, factor, to)

    @property
    def screened(self) -> tuple[str, ...]:
        """The factors a screening design varies: those with more than one level."""
        return tuple(name for name in self.factors if len(self.levels[name]) > 1)

    def cell_list(self) -> list[dict[str, Any]]:
        """The design's cells, each a level of every factor, in :data:`ALL_FACTORS` order."""
        names = self.factors
        if self.kind == KIND_FULL:
            return [dict(zip(names, values)) for values in itertools.product(*(self.levels[name] for name in names))]
        fixed = {name: self.levels[name][0] for name in names if len(self.levels[name]) == 1}
        varied = self.screened
        if self.kind == KIND_FRACTIONAL:
            wider = [name for name in varied if len(self.levels[name]) != 2]
            if wider:
                raise DesignError(f"a fractional design takes two-level factors only: {wider} have more; narrow each to two levels, or use kind sample")
            rows = fraction(len(varied), self.size)
            problems = aliasing_problems(rows, varied)
            if problems:  # never, for a design of the tables; checked on the cells all the same
                raise DesignError(f"the fraction is not of resolution IV: {'; '.join(problems)}")
            chosen = [{name: self.levels[name][0 if sign < 0 else 1] for name, sign in zip(varied, row)} for row in rows]
        else:
            draws = balanced_sample([self.levels[name] for name in varied], self.size, random.Random(f"sample:{self.seed}"))
            chosen = [dict(zip(varied, values)) for values in draws]
        return [{name: {**fixed, **cell}[name] for name in names} for cell in chosen]

    def cells(self) -> int:
        if self.kind == KIND_FULL:
            return math.prod(len(self.levels[name]) for name in self.factors)
        return int(self.size)

    def exact_repeat_plan(self, cells: Sequence[Mapping[str, Any]], case_ids: Sequence[str]) -> dict[tuple[str, str], int]:
        """The exact-repeat set (D14): ``(cell code, case id)`` to how many times in all, for the
        cells chosen with the seed (balanced across each factor's levels where possible), each on
        one case, the cases taken in turn in an order drawn with the seed. Empty without one."""
        if self.exact_repeats is None:
            return {}
        count, times = self.exact_repeats
        rng = random.Random(f"exact_repeats:{self.seed}")
        chosen = balanced_subset(cells, {name: self.levels[name] for name in self.screened}, count, rng)
        rng.shuffle(chosen)
        return {(cell_code(cells[index]), case_ids[k % len(case_ids)]): times for k, index in enumerate(chosen)}

    def as_dict(self) -> dict[str, Any]:
        described = {
            "seed": self.seed,
            "factors": {name: list(levels) for name, levels in self.levels.items()},
            "repeats": self.repeats,
            "base_age": self.base_age,
            "age_difference": self.age_difference,
            "tasks": dict(self.tasks),
        }
        # Issue #62: only what a config names, so that an older config is described as before.
        if self.kind_given or self.kind != KIND_FULL:
            described["kind"] = self.kind
        if self.size is not None:
            described["cells"] = self.size
        if self.geometries:
            described["geometries"] = list(self.geometries)
        if self.exact_repeats is not None:
            described["exact_repeats"] = {"cells": self.exact_repeats[0], "times": self.exact_repeats[1]}
        if self.counterfactual_pairs:
            described["counterfactual_pairs"] = [pair.as_dict() for pair in self.counterfactual_pairs]
        if self.ethnicity_shares is not None:  # issue #92: only when used
            described["ethnicity_shares"] = self.ethnicity_shares.as_dict()
            if self.ethnicity_draw != DRAW_REAL:  # only when not the default
                described["ethnicity_draw"] = self.ethnicity_draw
        return described

    def ethnicity_assignment(self, units: Mapping[tuple[str, str], set]) -> dict[tuple[str, str], dict[str, tuple[str, str]]]:
        """Issue #92: for each unit, ``(case id, cell code)`` or ``(case id, "x" + pair code)``, and
        each level of ``ethnicity_pair`` it runs at, person 1's group and person 2's. ``real``:
        drawn from the stream of the design's seed, the case and the cell or pair. ``balanced``:
        :func:`~negsim.resolution.ethnicity.balanced_assignment`."""
        if self.ethnicity_draw == DRAW_BALANCED:
            return balanced_assignment({unit: frozenset(levels) for unit, levels in units.items()}, self.seed)
        return {
            (case_id, draw): {level: self.ethnicity_shares.draw(level, f"{self.seed}:{case_id}:{draw}") for level in sorted(levels)}
            for (case_id, draw), levels in units.items()
        }


def cell_code(cell: Mapping[str, Any]) -> str:
    """Eight hexadecimal characters that name a cell of the design (of the factors it has, so a
    cell of the factors of issue #58 keeps its code)."""
    return hashlib.sha256(json.dumps({name: cell[name] for name in ALL_FACTORS if name in cell}, sort_keys=True).encode("utf-8")).hexdigest()[:8]


def personas_for(
    cell: Mapping[str, Any], agents: tuple[int, int], design: "ResolutionDesign", ethnicity: Optional[tuple[str, str]] = None,
) -> dict[int, dict[str, Any]]:
    """The two people of a cell, each assigned to an agent: the age, gender, errand and urgency
    of issue #30, then each core factor the cell varies (issue #60). ``urgency`` picks both errands.
    ``ethnicity`` (issue #92) is person 1's group and person 2's, when the design varies it."""
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
    if ethnicity is not None:
        people[first]["ethnicity"], people[second]["ethnicity"] = ethnicity
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
    if PAIR_FACTOR in cell:  # issue #92: whether each is told the other's ethnicity
        visibility["ethnicity"] = bool(cell.get(SWITCH_FACTOR, True))
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
    #: each core factor the design varies (issue #60); ``ethnicity`` when the design varies it
    #: (issue #92).
    personas: Mapping[int, Mapping[str, Any]]
    visibility: Mapping[str, bool]
    #: Issue #62, only when used: the case's geometry when the design lists ``geometries`` (D14),
    #: and a counterfactual pair's id, this session's role in it and the factor that differs.
    geometry: Optional[str] = None
    pair_id: Optional[str] = None
    pair_role: Optional[str] = None
    pair_factor: Optional[str] = None
    #: Issue #92, only when the design varies ethnicity: the session's weight back to the shares.
    ethnicity_weight: Optional[float] = None

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
        """Each person's levels of the core factors the design varies (``urgency`` included). A
        person with no errand (``task: none``) has no urgency, so none is given (issue #61 found
        that ``None`` was passed on as a level, and the session refused)."""
        return {
            agent: {name: persona[name] for name in PERSON_FACTORS if persona.get(name) is not None}
            for agent, persona in self.personas.items()
        }

    @property
    def situation(self) -> dict[str, str]:
        """The levels of the situational factors the design varies."""
        return {name: self.cell[name] for name in SITUATION_FACTORS if name in self.cell}

    @property
    def uses_factors(self) -> bool:
        return any(name in RF5_FACTORS or name in ETHNICITY_FACTORS for name in self.cell)

    @property
    def ethnicity(self) -> dict[int, str]:
        """Each person's group of real ethnicity (issue #92); empty unless the design varies it."""
        return {agent: persona["ethnicity"] for agent, persona in self.personas.items() if persona.get("ethnicity") is not None}

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
            **({"geometry": self.geometry} if self.geometry is not None else {}),  # issue #62: only when used
            **({"pair_id": self.pair_id, "pair_role": self.pair_role, "pair_factor": self.pair_factor} if self.pair_id is not None else {}),
            **({"ethnicity_weight": self.ethnicity_weight} if self.ethnicity_weight is not None else {}),  # issue #92
            "personas": {str(agent): dict(persona) for agent, persona in sorted(self.personas.items())},
            "visibility": dict(self.visibility),
            **({"pairwise": self.pairwise} if self.uses_pairwise else {}),  # issue #61: only when the design has one
        }


def sessions_for(
    cases: Sequence[tuple[str, int, tuple[int, int], str]],
    design: ResolutionDesign,
    conditions: Sequence[str],
    experiment: str,
    geometry_of: Optional[Mapping[str, str]] = None,
) -> list[Session]:
    """Every condition, case and cell of the design, each ``design.repeats`` times (or, with an
    exact-repeat set, its cells that many times on their case); then every counterfactual pair, as
    two sessions on every case; shuffled by the design's seed. ``cases`` are ``(case_id, version,
    agents, scenario plug-in)``; ``geometry_of`` names each case's geometry when the design lists
    geometries. Ids come from what a session is: ``<I|N|T>_<case>_<cell code>_r<repeat>``, and a
    pair's ``<I|N|T>_<case>_<cell code>_x<pair code>``."""
    cells = design.cell_list()
    repeats = design.exact_repeat_plan(cells, [case[0] for case in cases])
    unordered = []
    for condition in conditions:
        if condition not in CONDITIONS:
            raise ConfigError(f"unknown condition {condition!r}; the conditions are {list(CONDITIONS)}")
        letter = CONDITION_LETTER[condition]
        for case_id, version, agents, scenario in cases:
            common = {"condition": condition, "case_id": case_id, "case_version": version, "agents": tuple(sorted(agents)), "scenario": scenario}
            for cell in cells:
                times = repeats.get((cell_code(cell), case_id), 1) if repeats else design.repeats
                in_set = times > 1 if repeats else design.repeats > 1
                for repeat in range(1, times + 1):
                    session_id = f"{letter}_{case_id}_{cell_code(cell)}_r{repeat}"
                    unordered.append({
                        **common, "session_id": session_id, "cell": cell, "repeat": repeat, "exact_repeat_set": in_set,
                        "_unit": (case_id, cell_code(cell)),
                    })
            for pair in design.counterfactual_pairs:
                pair_id = f"{letter}_{case_id}_x{pair.code}"
                for role, cell in ((ROLE_BASE, pair.base), (ROLE_FLIPPED, pair.flipped)):
                    unordered.append({
                        **common, "session_id": f"{letter}_{case_id}_{cell_code(cell)}_x{pair.code}", "cell": dict(cell), "repeat": 1,
                        "exact_repeat_set": False, "pair_id": pair_id, "pair_role": role, "pair_factor": pair.factor,
                        "_unit": (case_id, f"x{pair.code}"),  # both sessions of a pair see the same people
                    })
    ids = [entry["session_id"] for entry in unordered]
    if len(set(ids)) != len(ids):
        raise ConfigError(f"experiment {experiment}: two sessions have the same id; a case is listed twice")
    order = sorted(unordered, key=lambda entry: entry["session_id"])
    random.Random(f"{experiment}:{design.seed}").shuffle(order)
    # Issue #92: the two people's groups, by unit (every session of a unit sees the same people).
    assigned: dict = {}
    if design.ethnicity_shares is not None:
        units: dict = {}
        for entry in order:
            units.setdefault(entry["_unit"], set()).add(entry["cell"][PAIR_FACTOR])
        assigned = design.ethnicity_assignment(units)

    def groups_of(entry: Mapping[str, Any]) -> Optional[tuple[str, str]]:
        return assigned[entry["_unit"]][entry["cell"][PAIR_FACTOR]] if assigned else None

    weight_of = (
        dict(zip(range(len(order)), weights(design.ethnicity_shares, [groups_of(e) for e in order])))
        if assigned else {}
    )
    return [
        Session(
            index=index, **{key: value for key, value in entry.items() if key != "_unit"},
            personas=personas_for(entry["cell"], entry["agents"], design, groups_of(entry)), visibility=visibility_for(entry["cell"]),
            geometry=(geometry_of or {}).get(entry["case_id"]) if design.geometries else None,
            ethnicity_weight=weight_of.get(index - 1),
        )
        for index, entry in enumerate(order, start=1)
    ]
