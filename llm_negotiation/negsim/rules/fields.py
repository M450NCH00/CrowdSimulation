"""The fields a rule may read: which ones, in what unit, and what has to be visible for each.

A rule's condition is evaluated once per pair, on one snapshot that both agents share
(``docs/rule-matching.md``). That stands for each agent evaluating the rule on its own only
if every field the rule reads is one that **both agents compute identically**. Two kinds
of field pass that test, and only they are on the list below:

* **pair-level quantities**, which come out the same whichever agent computes them
  (``docs/perception.md``, "Pair-level fields");
* **attributes of either agent that the other can see** under the run's visibility
  settings.

A rule that reads anything else is refused when it is loaded. A field that exists but is
known to fail the test (the task, a quantity measured at one agent's own position, a
quantity in one agent's own frame) is refused as ``unobservable_field``, with the reason:
such a rule could only be followed if the two agents talked to each other first, which is
a category of its own for the negotiation sub-issue (SI-3). Anything not on either list is
``unknown_field``.

A rule names a field with a prefix that says how it is used:

``pair.<name>``     a pair-level field, in a condition
``either.<name>``   an agent-level field, in a condition: true if the comparison holds for
                    at least one of the two agents
``both.<name>``     an agent-level field, in a condition: true if it holds for each of them
``agent.<name>``    an agent-level field, in a role assignment: the two agents' values are
                    compared with each other

``docs/rule-format.md`` has the same tables in prose.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional

from ..avoidance.perception import ENCOUNTER_CLASSES
from ..personas.schema import GENDERS
from .errors import RuleError

NUMBER, CATEGORY = "number", "category"
PAIR, AGENT = "pair", "agent"

#: Where a field may be named, by prefix.
CONDITION_PREFIXES = ("pair", "either", "both")
ROLE_PREFIXES = ("agent",)
#: Prefixes that name one agent from its own point of view. The two agents of a pair would
#: read different agents' values through them, so they fail the test above.
OBSERVER_RELATIVE_PREFIXES = ("observer", "neighbour", "neighbor", "self", "other", "me", "them", "own")

#: Units a number may be stated in, each with the unit of the field it can be used for and
#: the factor that converts a value in it to that unit.
UNITS: dict[str, tuple[str, float]] = {
    "m": ("m", 1.0),
    "s": ("s", 1.0),
    "m/s": ("m/s", 1.0),
    "rad": ("rad", 1.0),
    "deg": ("rad", math.pi / 180.0),
    "years": ("years", 1.0),
}


@dataclass(frozen=True)
class FieldSpec:
    """One field a rule may read.

    ``needs`` are the visibility switches that must be on for the two agents to see it;
    with any of them off the field is unobservable in that run, and a rule set that reads
    it is refused for that run (``RuleSet.check_visibility``). ``source`` says where in the
    perception record the value comes from.
    """

    name: str
    level: str
    kind: str
    unit: Optional[str]
    categories: tuple[str, ...]
    needs: tuple[str, ...]
    source: str
    meaning: str

    def convert(self, value: Any, unit: Optional[str], where: str) -> Any:
        """A value from a rule, checked against this field and turned into its unit."""
        if self.kind == CATEGORY:
            if unit is not None:
                raise RuleError("unit", f"{where}: '{self.name}' is a category and takes no unit, got {unit!r}")
            if not isinstance(value, str) or value not in self.categories:
                raise RuleError(
                    "value", f"{where}: '{self.name}' is one of {list(self.categories)}, got {value!r}"
                )
            return value
        if unit is None:
            raise RuleError(
                "unit", f"{where}: a comparison on '{self.name}' must state its unit ({self.unit!r}); none was given"
            )
        if unit not in UNITS or UNITS[unit][0] != self.unit:
            allowed = sorted(name for name, (base, _) in UNITS.items() if base == self.unit)
            raise RuleError("unit", f"{where}: '{self.name}' is in {self.unit!r}; the unit may be {allowed}, got {unit!r}")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise RuleError("value", f"{where}: '{self.name}' is a number, got {value!r}")
        return float(value) * UNITS[unit][1]


def _pair(name, kind, unit, needs, source, meaning, categories=()) -> FieldSpec:
    return FieldSpec(name, PAIR, kind, unit, tuple(categories), tuple(needs), source, meaning)


def _agent(name, kind, unit, needs, source, meaning, categories=()) -> FieldSpec:
    return FieldSpec(name, AGENT, kind, unit, tuple(categories), tuple(needs), source, meaning)


#: The encounter classes a pair can be in. ``none`` is a class of the pair, but a rule
#: cannot be written for it: a rule's ``encounter`` is one of the other four, or ``any``.
RULE_ENCOUNTERS = tuple(name for name in ENCOUNTER_CLASSES if name != "none") + ("any",)

PAIR_FIELDS: dict[str, FieldSpec] = {
    spec.name: spec
    for spec in (
        _pair(
            "encounter_class", CATEGORY, None, ("speed", "size"), "pair.encounter_class",
            "head_on, crossing, overtaking, single_file_segment or none", ENCOUNTER_CLASSES,
        ),
        _pair("distance_m", NUMBER, "m", (), "distance_m", "distance between the two centres"),
        _pair(
            "closing_speed_mps", NUMBER, "m/s", ("speed",), "closing_speed_mps",
            "how fast the distance is shrinking; negative if it is growing",
        ),
        _pair(
            "time_to_collision_s", NUMBER, "s", ("speed", "size"), "time_to_collision_s",
            "time until the bodies touch at present velocities; null if they would not",
        ),
        _pair(
            "heading_difference_rad", NUMBER, "rad", (), "pair.heading_difference_rad",
            "how far apart the two directions of travel are, 0 to pi",
        ),
        _pair(
            "min_corridor_width_m", NUMBER, "m", (), "pair.min_corridor_width_m",
            "narrowest free width of the passage along the line between the two",
        ),
        _pair(
            "age_difference_years", NUMBER, "years", ("age",), "pair.age_difference_years",
            "the difference between the two ages, never negative",
        ),
    )
}

AGENT_FIELDS: dict[str, FieldSpec] = {
    spec.name: spec
    for spec in (
        _agent("age", NUMBER, "years", ("age",), "observer.attributes.age, neighbour_attributes.age", "age"),
        _agent(
            "gender", CATEGORY, None, ("gender",), "observer.attributes.gender, neighbour_attributes.gender",
            "gender", GENDERS,
        ),
        _agent("speed_mps", NUMBER, "m/s", ("speed",), "observer.speed_mps, neighbour_speed_mps", "present speed"),
        _agent("radius_m", NUMBER, "m", ("size",), "observer.radius_m, neighbour_radius_m", "body radius"),
        _agent(
            "time_to_segment_s", NUMBER, "s", ("speed", "size"),
            "observer.time_to_segment_s, neighbour_time_to_segment_s",
            "distance to the single-file segment over present speed; null outside that class",
        ),
    )
}

#: Fields that exist, in the perception record or in an agent's own state, and that a
#: rule may not read, each with the reason. Refused as ``unobservable_field``.
UNOBSERVABLE: dict[str, str] = {
    "task": "the task is never in a perception record (docs/perception.md): no agent can see another's",
    "backstory": "free text, hidden by default, and not something two agents can compare",
    "preferred_speed_mps": "an agent knows its own preferred speed but never perceives a neighbour's",
    "max_speed_mps": "an agent knows its own maximum speed but never perceives a neighbour's",
    "goal": "an agent never perceives another's goal",
    "path": "an agent never perceives another's path",
    "nearest_wall_distance_m": "measured at one agent's own position; the two agents get different values",
    "free_width_m": "measured at one agent's own position, across its own path; use pair.min_corridor_width_m",
    "free_width_left_m": "measured at one agent's own position, across its own path",
    "free_width_right_m": "measured at one agent's own position, across its own path",
    "single_file_ahead_m": "measured along one agent's own path, which the other does not see; use agent.time_to_segment_s",
    "bearing_rad": "in one agent's own frame; the two agents get different values",
    "relative_position_m": "in one agent's own frame; the two agents get different values",
    "relative_velocity_mps": "in one agent's own frame; the two agents get different values",
    "neighbour_heading_relative_rad": "in one agent's own frame; use pair.heading_difference_rad",
}


@dataclass(frozen=True)
class FieldRef:
    """A field as a rule names it: the prefix, and what the field is."""

    written: str
    prefix: str
    spec: FieldSpec


def resolve(reference: Any, where: str, prefixes: tuple[str, ...]) -> FieldRef:
    """The field a rule names, or a :class:`RuleError` saying why it cannot be read.

    ``prefixes`` are the prefixes allowed where the field appears: those of a condition, or
    ``agent`` in a role assignment.
    """
    if not isinstance(reference, str) or "." not in reference:
        raise RuleError("unknown_field", f"{where}: {reference!r} is not a field; write it as <prefix>.<name>")
    prefix, name = reference.split(".", 1)
    for part in name.split("."):
        if part in UNOBSERVABLE:
            raise RuleError(
                "unobservable_field",
                f"{where}: '{reference}' cannot be read by a rule: {UNOBSERVABLE[part]}. A rule that needs it could "
                "only be followed if the agents talked first (a category for the negotiation sub-issue).",
            )
    if prefix in OBSERVER_RELATIVE_PREFIXES:
        raise RuleError(
            "unobservable_field",
            f"{where}: '{reference}' names one agent from its own point of view, so the two agents of a pair would "
            "read different agents' values. Use either./both. in a condition and agent. in a role assignment.",
        )
    level = PAIR if prefix == "pair" else AGENT if prefix in ("either", "both", "agent") else None
    table = PAIR_FIELDS if level == PAIR else AGENT_FIELDS if level == AGENT else None
    if table is None or name not in table:
        known = [f"pair.{field}" for field in PAIR_FIELDS] + [f"<either|both|agent>.{field}" for field in AGENT_FIELDS]
        raise RuleError("unknown_field", f"{where}: '{reference}' is not a field a rule can read; known: {known}")
    if prefix not in prefixes:
        raise RuleError(
            "unknown_field",
            f"{where}: '{reference}' cannot be used here; the prefix must be one of {list(prefixes)}",
        )
    return FieldRef(reference, prefix, table[name])
