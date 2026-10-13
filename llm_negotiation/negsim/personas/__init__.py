"""Personas: the schema and the YAML loader."""

from .loader import load_personas
from .schema import (
    ATTRIBUTES,
    GENDERS,
    NAME_LIKE_FIELDS,
    SCHEMA_VERSION,
    AttributeSpec,
    Persona,
    PersonaError,
    validate_persona,
)

__all__ = [
    "ATTRIBUTES",
    "GENDERS",
    "NAME_LIKE_FIELDS",
    "SCHEMA_VERSION",
    "AttributeSpec",
    "Persona",
    "PersonaError",
    "load_personas",
    "validate_persona",
]
