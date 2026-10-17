"""A rule's condition: comparisons of fields with constants, in ``all`` and ``any`` groups.

The condition language is data and nothing else. A comparison names a field from the
list in ``fields.py``, one of seven operators, a constant, and the constant's unit. There
is no expression to parse, nothing is looked up by name at run time beyond that list, and
nothing is ever passed to ``eval`` or ``exec``: a condition can only compare the values of
a snapshot with constants written in the rule.

**A comparison on a missing value is false.** A field is missing (``None``) when the run's
visibility settings hide it, or when it does not exist for the pair (a time to collision
for two agents that would not collide). Every operator gives false on it, ``!=`` and
``in`` included, so that a rule never fires on something its agents could not see.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Mapping, Optional

from .errors import RuleError
from .fields import BOOLEAN, CATEGORY, CONDITION_PREFIXES, FieldRef, resolve
from .snapshot import PairSnapshot

ORDERING = ("<", "<=", ">", ">=")
OPERATORS = ORDERING + ("==", "!=", "in")


def compare(actual: Any, op: str, value: Any) -> bool:
    """``actual op value``; false whenever ``actual`` is missing."""
    if actual is None:
        return False
    if op == "in":
        return any(actual == option for option in value)
    if op == "==":
        return actual == value
    if op == "!=":
        return actual != value
    if op == "<":
        return actual < value
    if op == "<=":
        return actual <= value
    if op == ">":
        return actual > value
    if op == ">=":
        return actual >= value
    raise ValueError(f"unknown operator {op!r}")


class Condition(ABC):
    @abstractmethod
    def evaluate(self, snapshot: PairSnapshot) -> bool:
        """Whether the condition holds on ``snapshot``."""

    @abstractmethod
    def comparisons(self) -> Iterator["Comparison"]:
        """Every comparison in the condition."""


@dataclass(frozen=True)
class Comparison(Condition):
    """``field op value``. ``value`` is in the field's own unit (a tuple for ``in``)."""

    ref: FieldRef
    op: str
    value: Any

    def evaluate(self, snapshot: PairSnapshot) -> bool:
        name = self.ref.spec.name
        if self.ref.prefix == "pair":
            return compare(snapshot.pair.get(name), self.op, self.value)
        results = [compare(snapshot.agent_value(index, name), self.op, self.value) for index in (0, 1)]
        return any(results) if self.ref.prefix == "either" else all(results)

    def comparisons(self) -> Iterator["Comparison"]:
        yield self

    def thresholds(self) -> tuple[Any, ...]:
        """The constants this comparison tests against."""
        return tuple(self.value) if self.op == "in" else (self.value,)


@dataclass(frozen=True)
class Group(Condition):
    """``all`` (every item holds; true when empty) or ``any`` (at least one holds)."""

    kind: str
    items: tuple[Condition, ...]

    def evaluate(self, snapshot: PairSnapshot) -> bool:
        if self.kind == "all":
            return all(item.evaluate(snapshot) for item in self.items)
        return any(item.evaluate(snapshot) for item in self.items)

    def comparisons(self) -> Iterator[Comparison]:
        for item in self.items:
            yield from item.comparisons()


def parse_condition(raw: Any, where: str, schema_version: Optional[int] = None, terms: Iterable[str] = ()) -> Condition:
    """A condition from its written form (already checked against the JSON Schema).

    ``schema_version`` is the rule's: it may read only the fields of its version.
    ``terms`` are more words that name a person's group (``fields.protected_reference``).
    """
    if not isinstance(raw, Mapping):
        raise RuleError("schema", f"{where}: a condition is a comparison, or a mapping with 'all' or 'any'")
    for kind in ("all", "any"):
        if kind in raw:
            items = raw[kind]
            if kind == "any" and not items:
                raise RuleError("schema", f"{where}.any: must have at least one item")
            return Group(
                kind,
                tuple(parse_condition(item, f"{where}.{kind}[{index}]", schema_version, terms) for index, item in enumerate(items)),
            )
    return _comparison(raw, where, schema_version, terms)


def _comparison(raw: Mapping[str, Any], where: str, schema_version: Optional[int] = None, terms: Iterable[str] = ()) -> Comparison:
    ref = resolve(raw.get("field"), f"{where}.field", CONDITION_PREFIXES, schema_version, terms)
    op, unit, value = raw.get("op"), raw.get("unit"), raw.get("value")
    if op not in OPERATORS:
        raise RuleError("operator", f"{where}.op: expected one of {list(OPERATORS)}, got {op!r}")
    if ref.spec.kind == CATEGORY and op in ORDERING:
        raise RuleError("operator", f"{where}: '{ref.written}' is a category; only ==, != and in apply, got {op!r}")
    if ref.spec.kind == BOOLEAN and op in ORDERING:
        raise RuleError("operator", f"{where}: '{ref.written}' is true or false; only ==, != and in apply, got {op!r}")
    if op == "in":
        if not isinstance(value, list) or not value:
            raise RuleError("value", f"{where}.value: 'in' needs a non-empty list, got {value!r}")
        converted: Any = tuple(ref.spec.convert(item, unit, f"{where}.value") for item in value)
    else:
        if isinstance(value, list):
            raise RuleError("value", f"{where}.value: a list goes with 'in' only, not {op!r}")
        converted = ref.spec.convert(value, unit, f"{where}.value")
    return Comparison(ref, op, converted)
