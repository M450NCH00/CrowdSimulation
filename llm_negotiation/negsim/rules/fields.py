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

Since issue #32 every field says which version of the rule format added it (``since``): a
rule can read only the fields of its own ``schema_version``, so a version 1 or 2 rule reads
exactly what it always could. Version 3 adds the passage fields, the first field that is true
or false (``in_segment``) among them. And a person's group (``ethnic_group``, issue #32) is
**protected**: an agent may see it, but a rule that names it, or anything derived from it, is
refused as ``protected_attribute`` (:func:`protected_reference`), before any other check. Since
issue #61 so is **perceived attractiveness**, how one person sees another: an agent may be told
its own view of someone, but until the supervisor decides, no rule may read it.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from ..avoidance.perception import ENCOUNTER_CLASSES
from ..personas.groups import DEFAULT_GROUP_LABELS
from ..personas.schema import GENDERS, NOT_RULE_REFERENCEABLE
from .errors import RuleError

NUMBER, CATEGORY, BOOLEAN = "number", "category", "boolean"
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
    #: The version of the rule format that added the field (issue #32).
    since: int = 1

    def convert(self, value: Any, unit: Optional[str], where: str) -> Any:
        """A value from a rule, checked against this field and turned into its unit."""
        if self.kind == BOOLEAN:
            if unit is not None:
                raise RuleError("unit", f"{where}: '{self.name}' is true or false and takes no unit, got {unit!r}")
            if not isinstance(value, bool):
                raise RuleError("value", f"{where}: '{self.name}' is true or false, got {value!r}")
            return value
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


def _pair(name, kind, unit, needs, source, meaning, categories=(), since=1) -> FieldSpec:
    return FieldSpec(name, PAIR, kind, unit, tuple(categories), tuple(needs), source, meaning, since)


def _agent(name, kind, unit, needs, source, meaning, categories=(), since=1) -> FieldSpec:
    return FieldSpec(name, AGENT, kind, unit, tuple(categories), tuple(needs), source, meaning, since)


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
        # Version 3 (issue #32): where each is in the single-file passage the two meet in.
        _agent(
            "in_segment", BOOLEAN, None, ("speed", "size"), "observer.in_segment, neighbour_in_segment",
            "whether this person is inside the single-file segment; null outside that class", since=3,
        ),
        _agent(
            "segment_distance_travelled", NUMBER, "m", ("speed", "size"),
            "observer.segment_distance_travelled, neighbour_segment_distance_travelled",
            "how far this person has walked into the single-file segment; null unless inside it", since=3,
        ),
        _agent(
            "segment_distance_ahead", NUMBER, "m", ("speed", "size"),
            "observer.segment_distance_ahead, neighbour_segment_distance_ahead",
            "distance to the end of the single-file segment in front of this person; null unless inside it", since=3,
        ),
        _agent(
            "segment_distance_behind", NUMBER, "m", ("speed", "size"),
            "observer.segment_distance_behind, neighbour_segment_distance_behind",
            "distance to the end of the single-file segment behind this person; null unless inside it", since=3,
        ),
    )
}


def fields_of(schema_version: int) -> tuple[dict[str, FieldSpec], dict[str, FieldSpec]]:
    """The pair-level and agent-level fields a rule of ``schema_version`` may read, in order."""
    return (
        {name: spec for name, spec in PAIR_FIELDS.items() if spec.since <= schema_version},
        {name: spec for name, spec in AGENT_FIELDS.items() if spec.since <= schema_version},
    )


# --- protected attributes (issue #32; issue #61) ------------------------------------------------

#: Perceived attractiveness (issue #61, RF-6): how attractive one person finds another. It belongs
#: to a pair, not to a person, so it is not in the persona table. An agent may be told its own view
#: of someone, but until the supervisor decides (``CLAUDE.md``, "Pending sign-offs") no rule may
#: read it. It stays in the outcome rows, for the factor analysis (RF-8) and the mapping.
PERCEIVED_ATTRACTIVENESS = "perceived_attractiveness"
#: What no rule may read, each with the reason. An agent may see them, or be told its own view.
PROTECTED: dict[str, str] = {
    **{
        name: (
            "a person's group is something an agent may see but no rule may read: a rule that conditions on it, "
            "or on anything derived from it, is refused (docs/rule-format.md, section 14; docs/fictional-groups.md)"
        )
        for name in sorted(NOT_RULE_REFERENCEABLE)
    },
    PERCEIVED_ATTRACTIVENESS: (
        "how attractive one person finds another is something an agent may be told of its own view but, until the "
        "supervisor decides, no rule may read: a rule that conditions on it is refused, and counted (docs/rule-format.md, "
        "section 14; docs/pairwise-factors.md, section 7)"
    ),
}
#: What a refusal calls each protected attribute.
PROTECTED_NAMES = {"ethnic_group": "a person's group", PERCEIVED_ATTRACTIVENESS: "perceived attractiveness"}
#: The word that marks a field as about ethnicity, whatever else its name says: ``ethnic_group``,
#: ``same_ethnic_group``, ``ethnicity``, ``ethnic_difference``.
PROTECTED_STEM = "ethnic"
#: What marks a field as about attractiveness, whatever else its name says (issue #61): anything
#: containing ``attract`` (``attractive``, ``attractiveness``, ``attraction``), ``beaut``,
#: ``handsome`` or ``pretty``, or "good looking" however it is joined.
ATTRACTIVENESS_PATTERN = re.compile(r"attract|beaut|handsome|pretty|good[\s_-]*looking")
_TOKEN = re.compile(r"[^a-z0-9]+")


def protected_reference(text: Any, terms: Iterable[str] = ()) -> Optional[str]:
    """The protected word ``text`` uses, or ``None``.

    ``text`` uses one if it contains :data:`PROTECTED_STEM` or a match of
    :data:`ATTRACTIVENESS_PATTERN` anywhere, or if one of its words (split at anything but letters
    and digits, ignoring case) is the name of a protected attribute, one of the default group
    labels, or one of ``terms``: the words a session introduced groups with, and its labels
    (``negsim.rulegen.validate``).
    """
    if not isinstance(text, str):
        return None
    lowered = text.lower()
    if PROTECTED_STEM in lowered:
        return PROTECTED_STEM
    found = ATTRACTIVENESS_PATTERN.search(lowered)
    if found is not None:
        return found.group(0)
    words = set(_TOKEN.split(lowered)) - {""}
    for term in (*PROTECTED, *DEFAULT_GROUP_LABELS, *terms):
        if term.lower() in words or term.lower() == lowered:
            return term
    return None


def protected_attribute_of(word: str) -> str:
    """The protected attribute a word that :func:`protected_reference` returned is about."""
    return PERCEIVED_ATTRACTIVENESS if ATTRACTIVENESS_PATTERN.search(word.lower()) else "ethnic_group"

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
    # Issue #60 (RF-5): core factors nobody else can see (docs/resolution.md, D9).
    "assertiveness": "a person's assertiveness is known only to them: another agent cannot see it",
    "residence": "where a person lives is known only to them: another agent cannot see it",
    "memory_note": "a person's memory of an earlier encounter is known only to them: another agent cannot see it",
}


@dataclass(frozen=True)
class FieldRef:
    """A field as a rule names it: the prefix, and what the field is."""

    written: str
    prefix: str
    spec: FieldSpec


def resolve(
    reference: Any, where: str, prefixes: tuple[str, ...], schema_version: Optional[int] = None, terms: Iterable[str] = ()
) -> FieldRef:
    """The field a rule names, or a :class:`RuleError` saying why it cannot be read.

    ``prefixes`` are the prefixes allowed where the field appears: those of a condition, or
    ``agent`` in a role assignment. ``schema_version``, if given, is the rule's: a field a
    later version added is unknown to it. ``terms`` are more protected words
    (:func:`protected_reference`). A protected reference is refused before anything else.
    """
    word = protected_reference(reference, terms)
    if word is not None:
        attribute = protected_attribute_of(word)
        raise RuleError(
            "protected_attribute",
            f"{where}: '{reference}' refers to {PROTECTED_NAMES[attribute]} ({word!r}), which no rule may read: "
            f"{PROTECTED[attribute]}. The attempt is kept, as data.",
        )
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
    spec = table[name]
    if schema_version is not None and spec.since > schema_version:
        raise RuleError(
            "unknown_field",
            f"{where}: '{reference}' was added in version {spec.since} of the rule format; a rule of schema_version "
            f"{schema_version} cannot read it",
        )
    return FieldRef(reference, prefix, spec)
