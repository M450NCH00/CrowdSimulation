"""Personas: the schema, the YAML loader, and the fictional group labels (issue #32)."""

from .groups import DEFAULT_FRAMING, DEFAULT_GROUP_LABELS, GroupLabelError, check_framing, check_label, check_labels
from .loader import load_personas
from .schema import (
    ATTRIBUTES,
    FACTOR_ATTRIBUTES,
    GENDERS,
    NAME_LIKE_FIELDS,
    NOT_RULE_REFERENCEABLE,
    SCHEMA_VERSION,
    AttributeSpec,
    Persona,
    PersonaError,
    validate_persona,
)

__all__ = [
    "ATTRIBUTES",
    "DEFAULT_FRAMING",
    "DEFAULT_GROUP_LABELS",
    "FACTOR_ATTRIBUTES",
    "GENDERS",
    "NAME_LIKE_FIELDS",
    "NOT_RULE_REFERENCEABLE",
    "SCHEMA_VERSION",
    "AttributeSpec",
    "GroupLabelError",
    "Persona",
    "PersonaError",
    "check_framing",
    "check_label",
    "check_labels",
    "load_personas",
    "validate_persona",
]
