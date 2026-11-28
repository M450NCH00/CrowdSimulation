"""Persona schema.

A persona is a ``persona_id`` plus a set of attributes. Each attribute is declared once,
in :data:`ATTRIBUTES`, with how to validate it and whether another person could plausibly
see it. Adding an attribute means adding one entry there and one line to a prompt
template; the loader, the visibility settings and the prompt renderer pick it up from
this table and need no change.

Personas have no personal names, on purpose: a name carries gender and ethnicity cues
that would be confounded with the attributes under study. The loader rejects name-like
fields. Agents are referred to as "you" and "the other person" in prompts, and by agent
index and ``persona_id`` in logs.

``ethnic_group`` (issue #32) is a **fictional** group label (``negsim.personas.groups``). It is
hidden by default, it is left out of a persona that does not give it (so personas written
before it existed are unchanged), and **no rule may read it** (``rule_referenceable``).

**The core factors of track #55** (issue #60, RF-5; ``docs/resolution.md``, D15): ``urgency``,
``mobility_aid``, ``load``, ``distraction``, ``assertiveness``, ``residence`` and
``memory_note``, each with two ``levels`` (the first is the base level). They are left out of a
persona that does not give them, and out of the older layers' visibility settings
(:func:`negsim.avoidance.perception.default_visibility`), whose prompts have no line for them:
whether someone else sees one is the resolution design's switch (``<name>_visible``), and their
lines are ``resolve_factors_v1``'s (``negsim.resolution.factors``). ``urgency`` has no line of
its own: it says how urgent the ``task`` is, and the task line carries it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .groups import check_label

SCHEMA_VERSION = 1
GENDERS = ("female", "male", "nonbinary")
MIN_AGE, MAX_AGE = 1, 120
PERSONA_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]*$")
NAME_LIKE_FIELDS = frozenset(
    {"name", "first_name", "last_name", "surname", "given_name", "full_name", "nickname"}
)


class PersonaError(ValueError):
    """A persona definition is invalid."""


def _age(value: Any) -> int:
    # bool is a subclass of int in Python; "true" is not an age.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"must be a whole number of years, got {value!r}")
    if not MIN_AGE <= value <= MAX_AGE:
        raise ValueError(f"must be between {MIN_AGE} and {MAX_AGE}, got {value}")
    return value


def _gender(value: Any) -> str:
    if value not in GENDERS:
        raise ValueError(f"must be one of {list(GENDERS)}, got {value!r}")
    return value


def _text(allow_empty: bool) -> Callable[[Any], str]:
    def validate(value: Any) -> str:
        if value is None and allow_empty:
            return ""
        if not isinstance(value, str):
            raise ValueError(f"must be text, got {value!r}")
        value = " ".join(value.split())
        if not value and not allow_empty:
            raise ValueError("must not be empty")
        return value

    return validate


def _group(value: Any) -> str:
    try:
        return check_label(value)
    except ValueError as exc:
        raise ValueError(str(exc)) from exc


def _level(levels: tuple[str, ...]) -> Callable[[Any], str]:
    def validate(value: Any) -> str:
        if value not in levels:
            raise ValueError(f"must be one of {list(levels)}, got {value!r}")
        return value

    return validate


@dataclass(frozen=True)
class AttributeSpec:
    """One persona attribute.

    ``observable`` says whether another person could plausibly tell it by looking. It is
    the default for the experiment's visibility settings and can be overridden there.
    ``rule_referenceable`` (issue #32) is false for an attribute that an agent may see but no
    rule may read: ``negsim.rules`` refuses any rule that names it (``protected_attribute``).
    ``fill_default`` is false for an optional attribute that is left out of a persona that
    does not give it, instead of being set to its default.
    ``levels`` (issue #60) marks a core factor of track #55: its two levels, the base level
    first. Such an attribute is not in the older layers' visibility settings.
    """

    name: str
    validate: Callable[[Any], Any]
    required: bool
    default: Any
    observable: bool
    rule_referenceable: bool = True
    fill_default: bool = True
    levels: tuple[str, ...] = ()


def _factor(name: str, levels: tuple[str, str], observable: bool) -> AttributeSpec:
    """A core factor of track #55 (issue #60): optional, left out when not given."""
    return AttributeSpec(name, _level(levels), required=False, default=None, observable=observable, fill_default=False, levels=levels)


ATTRIBUTES: dict[str, AttributeSpec] = {
    spec.name: spec
    for spec in (
        AttributeSpec("age", _age, required=True, default=None, observable=True),
        AttributeSpec("gender", _gender, required=True, default=None, observable=True),
        AttributeSpec("backstory", _text(allow_empty=True), required=False, default="", observable=False),
        AttributeSpec("task", _text(allow_empty=False), required=True, default=None, observable=False),
        AttributeSpec(
            "ethnic_group", _group, required=False, default=None, observable=False,
            rule_referenceable=False, fill_default=False,
        ),
        # The core factors (issue #60, RF-5), in the order of the issue's table.
        _factor("urgency", ("routine", "urgent"), observable=False),
        _factor("mobility_aid", ("none", "cane"), observable=True),
        _factor("load", ("none", "large_suitcase"), observable=True),
        _factor("distraction", ("none", "phone"), observable=True),
        _factor("assertiveness", ("gives_way", "holds_ground"), observable=False),
        _factor("residence", ("local", "visitor"), observable=False),
        _factor("memory_note", ("none", "bad_experience"), observable=False),
    )
}
#: Attributes an agent may see but no rule may read (issue #32).
NOT_RULE_REFERENCEABLE = frozenset(name for name, spec in ATTRIBUTES.items() if not spec.rule_referenceable)
#: The core factors of track #55 (issue #60), in order.
FACTOR_ATTRIBUTES = tuple(name for name, spec in ATTRIBUTES.items() if spec.levels)


@dataclass(frozen=True)
class Persona:
    persona_id: str
    attributes: Mapping[str, Any]

    @property
    def age(self) -> int:
        return self.attributes["age"]

    @property
    def gender(self) -> str:
        return self.attributes["gender"]

    @property
    def task(self) -> str:
        return self.attributes["task"]

    @property
    def backstory(self) -> str:
        return self.attributes["backstory"]

    def with_overrides(self, **changes: Any) -> "Persona":
        """A copy with some attributes changed, re-validated.

        This is how an experiment varies one attribute while holding the others fixed.
        The copy's id records what was changed, e.g. ``f25+age=70``. A changed task does
        not alter the id (the task is logged next to the persona), and a changed free-text
        attribute is marked without being spelled out, e.g. ``f25+backstory*``.
        """
        if not changes:
            return self
        parts = []
        for key in sorted(changes):
            if key == "task":
                continue
            value = changes[key]
            # A group label is a name, spelled out like a gender (issue #32), and so is a factor's
            # level (issue #60); only free text is not.
            spec = ATTRIBUTES.get(key)
            named = key == "ethnic_group" or (spec is not None and value in spec.levels)
            free_text = isinstance(value, str) and value not in GENDERS and not named
            parts.append(f"{key}*" if free_text else f"{key}={value}")
        new_id = f"{self.persona_id}+{','.join(parts)}" if parts else self.persona_id
        return validate_persona({**self.attributes, **changes}, persona_id=new_id)

    def as_dict(self) -> dict[str, Any]:
        return {"persona_id": self.persona_id, **self.attributes}


def validate_persona(raw: Any, persona_id: str | None = None) -> Persona:
    """Build a :class:`Persona` from a mapping, or raise :class:`PersonaError`.

    ``raw`` may carry ``persona_id`` itself; ``persona_id`` given here takes precedence
    (used for derived personas, whose ids are not plain identifiers).
    """
    if not isinstance(raw, Mapping):
        raise PersonaError(f"a persona must be a mapping, got {type(raw).__name__}")
    derived = persona_id is not None
    persona_id = persona_id if derived else raw.get("persona_id")
    label = f"persona {persona_id!r}"
    if not isinstance(persona_id, str) or not persona_id:
        raise PersonaError("a persona needs a 'persona_id' (text)")
    if not derived and not PERSONA_ID_PATTERN.match(persona_id):
        raise PersonaError(
            f"{label}: persona_id must be lower-case letters, digits and underscores "
            "(a code, not a name)"
        )

    names = sorted(NAME_LIKE_FIELDS & set(raw))
    if names:
        raise PersonaError(
            f"{label}: field(s) {names} are not allowed. Personas must not have personal "
            "names: a name carries gender and ethnicity cues that would confound the experiment."
        )
    unknown = sorted(set(raw) - set(ATTRIBUTES) - {"persona_id"})
    if unknown:
        raise PersonaError(
            f"{label}: unknown field(s) {unknown}; allowed fields are "
            f"{['persona_id', *ATTRIBUTES]}. To add an attribute, declare it in "
            "negsim/personas/schema.py."
        )

    attributes = {}
    for name, spec in ATTRIBUTES.items():
        if name not in raw:
            if spec.required:
                raise PersonaError(f"{label}: missing required field {name!r}")
            if spec.fill_default:
                attributes[name] = spec.default
            continue
        try:
            attributes[name] = spec.validate(raw[name])
        except ValueError as exc:
            raise PersonaError(f"{label}: {name} {exc}") from exc
    return Persona(persona_id, attributes)
