"""Can two rules at one priority both match the same pair and tell it different things?

Two rules at the same priority that match the same pair with different directives are an
error (``docs/rule-matching.md``, "Several matches"). This module looks for that before
any run, by trying both rules on a **grid of test situations** built from the rules
themselves. The grid is documented in ``docs/rule-matching.md``; in short:

* the encounter classes both rules can apply to;
* for every pair-level field either rule reads: each constant it is compared with, a
  value just below and just above each, and "missing";
* for every agent-level field either rule reads: the same values, plus values that put
  the two agents in either order and within any tie tolerance, for each of the two agents
  independently, and "missing";
* for a field that is a name or is true or false (issue #32), every value it can take, and
  "missing";
* (version 4, issue #108) the comparisons of a role by a condition and of every own-only
  condition count like the rule's own, and a person's own private factors (``self.``) are varied
  for each of the two independently, as an agent-level field is. Two matches differ if they give
  either agent a different directive or a different plan.

**Why the grid is enough.** Every comparison is between one field and a constant, so
whether it holds can change only at that constant. Between two consecutive constants of a
field nothing changes; one value in each such interval, and the constants themselves,
cover every combination of true and false the comparisons on that field can take. A role
assignment depends only on the order of the two values and whether they are within the
tie tolerance, which the extra values cover. So if two rules can both match some
situation, they both match one of the grid's.

**What it can get wrong, and which way.** The grid varies fields independently: it will
try an age difference of 30 years for two agents whose ages are both 25. A situation that
cannot happen can only make the check report a clash that would never arise, never miss
one that would. Such a report is resolved by giving one rule a higher priority.

A grid larger than :data:`MAX_SITUATIONS` is not tried; the pair is reported as
unchecked, and the run-time check (``ambiguous_match``) is all that covers it.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Any, Iterator, Optional, Sequence

from ..avoidance.perception import ENCOUNTER_CLASSES
from .fields import BOOLEAN, CATEGORY, PAIR, SELF
from .model import Match, RoleAssignment, Rule
from .snapshot import PairSnapshot

#: The encounter classes a rule can apply to (``none`` is not one of them).
RULE_CLASSES = tuple(name for name in ENCOUNTER_CLASSES if name != "none")
MAX_SITUATIONS = 200_000


@dataclass(frozen=True)
class Clash:
    """Two rules at one priority that both match ``situation`` with different directives."""

    first: Rule
    second: Rule
    situation: Optional[PairSnapshot]
    checked: bool = True  # False: the grid was too large to try

    def describe(self) -> str:
        if not self.checked:
            return (
                f"{self.first.key} and {self.second.key} (priority {self.first.priority}) could not be checked: "
                f"more than {MAX_SITUATIONS} test situations"
            )
        return (
            f"{self.first.key} and {self.second.key} are both priority {self.first.priority} and both match "
            f"{_situation_text(self.situation)} with different directives"
        )


def can_overlap(first: Rule, second: Rule) -> bool:
    """Same priority, and an encounter class both can apply to."""
    return first.priority == second.priority and (
        first.encounter == "any" or second.encounter == "any" or first.encounter == second.encounter
    )


def clashes(rules: Sequence[Rule]) -> list[Clash]:
    """Every pair of ``rules`` that can match one situation with different directives."""
    found = []
    ordered = sorted(rules, key=lambda rule: (rule.rule_id, rule.version))
    for index, first in enumerate(ordered):
        for second in ordered[index + 1 :]:
            if can_overlap(first, second):
                clash = find_clash(first, second)
                if clash is not None:
                    found.append(clash)
    return found


def find_clash(first: Rule, second: Rule) -> Optional[Clash]:
    """A situation in which both rules match with different directives, or ``None``."""
    grid = Grid(first, second)
    if grid.size > MAX_SITUATIONS:
        return Clash(first, second, None, checked=False)
    for situation in grid:
        a, b = first.match(situation), second.match(situation)
        if a is not None and b is not None and different(a, b):
            return Clash(first, second, situation)
    return None


def different(a: Match, b: Match) -> bool:
    """Whether two matches of one snapshot tell either agent something different."""
    return a.directives != b.directives or a.steps != b.steps


class Grid:
    """The test situations for two rules (module docstring)."""

    def __init__(self, first: Rule, second: Rule):
        rules = (first, second)
        specific = {rule.encounter for rule in rules if rule.encounter != "any"}
        self.classes = sorted(specific) if specific else list(RULE_CLASSES)
        pair_fields: dict[str, list[Any]] = {}
        agent_fields: dict[str, list[Any]] = {}
        self_fields: dict[str, list[Any]] = {}
        tolerances: dict[str, float] = {}
        kinds: dict[str, Any] = {}
        selves: dict[str, Any] = {}
        for rule in rules:
            for comparison in rule.comparisons():
                spec = comparison.ref.spec
                if spec.level == PAIR and spec.name == "encounter_class":
                    continue  # the classes are a dimension of their own
                if spec.level == SELF:  # version 4: a person's own private factor
                    self_fields.setdefault(spec.name, []).extend(comparison.thresholds())
                    selves[spec.name] = spec
                    continue
                table = pair_fields if spec.level == PAIR else agent_fields
                table.setdefault(spec.name, []).extend(comparison.thresholds())
                kinds[spec.name] = spec
            if isinstance(rule.roles, RoleAssignment):
                spec = rule.roles.ref.spec
                agent_fields.setdefault(spec.name, [])
                kinds[spec.name] = spec
                tolerances[spec.name] = max(tolerances.get(spec.name, 0.0), rule.roles.tie_within)
        self.pair_values = {name: _candidates(kinds[name], values) for name, values in pair_fields.items()}
        self.agent_values = {
            name: _candidates(kinds[name], values, tolerances.get(name)) for name, values in agent_fields.items()
        }
        self.self_values = {name: _candidates(selves[name], values) for name, values in self_fields.items()}

    @property
    def size(self) -> int:
        count = len(self.classes)
        for values in self.pair_values.values():
            count *= len(values)
        for values in [*self.agent_values.values(), *self.self_values.values()]:
            count *= len(values) ** 2
        return count

    def __iter__(self) -> Iterator[PairSnapshot]:
        pair_names, agent_names, self_names = list(self.pair_values), list(self.agent_values), list(self.self_values)
        pair_choices = [self.pair_values[name] for name in pair_names]
        agent_choices = [list(itertools.product(self.agent_values[name], repeat=2)) for name in agent_names]
        self_choices = [list(itertools.product(self.self_values[name], repeat=2)) for name in self_names]
        for encounter in self.classes:
            for pair_combo in itertools.product(*pair_choices):
                pair = {"encounter_class": encounter, **dict(zip(pair_names, pair_combo))}
                for agent_combo in itertools.product(*agent_choices):
                    first = {name: values[0] for name, values in zip(agent_names, agent_combo)}
                    second = {name: values[1] for name, values in zip(agent_names, agent_combo)}
                    if not self_names:
                        yield PairSnapshot(0, 0.0, (0, 1), pair, (first, second))
                        continue
                    for self_combo in itertools.product(*self_choices):
                        mine = {name: values[0] for name, values in zip(self_names, self_combo)}
                        theirs = {name: values[1] for name, values in zip(self_names, self_combo)}
                        yield PairSnapshot(0, 0.0, (0, 1), pair, (first, second), (mine, theirs))


def _candidates(spec: Any, thresholds: list[Any], tolerance: Optional[float] = None) -> list[Any]:
    """The values to try for one field: see the module docstring. ``None`` is "missing"."""
    if spec.kind == CATEGORY:
        return [*spec.categories, None]
    if spec.kind == BOOLEAN:  # issue #32: every value a true-or-false field can take
        return [True, False, None]
    points = sorted({float(value) for value in thresholds})
    gaps = [b - a for a, b in zip(points, points[1:])]
    scale = max([1.0] + [abs(point) for point in points])
    step = min([1e-6 * scale] + [gap / 3.0 for gap in gaps])
    values = set()
    for point in points:
        values.update((point - step, point, point + step))
    if tolerance is not None:  # a role field: both orders, and a tie, around a base value
        base = points[0] if points else 0.0
        for anchor in (base, *sorted(values)):
            values.update((anchor + tolerance + 1.0, anchor - tolerance - 1.0, anchor + tolerance / 2.0))
    if not values:
        values = {0.0}
    return [*sorted(values), None]


def _situation_text(situation: Optional[PairSnapshot]) -> str:
    if situation is None:
        return "an unchecked situation"
    parts = [", ".join(f"pair.{name}={_short(value)}" for name, value in situation.pair.items())]
    if any(situation.agent_values):
        parts += [
            f"agent {index}: " + ", ".join(f"{name}={_short(value)}" for name, value in values.items())
            for index, values in enumerate(situation.agent_values)
        ]
    return f"the situation ({'; '.join(parts)})"


def _short(value: Any) -> str:
    if isinstance(value, float) and math.isfinite(value):
        return f"{value:.6g}"
    return repr(value) if isinstance(value, str) else str(value)
