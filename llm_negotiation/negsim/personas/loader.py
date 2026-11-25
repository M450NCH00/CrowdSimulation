"""Load personas from a YAML file."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from ..configutil import ConfigError, load_yaml, resolve_path
from .schema import SCHEMA_VERSION, Persona, PersonaError, validate_persona


def load_personas(path: Path | str) -> dict[str, Persona]:
    """Read every persona in the file, keyed by ``persona_id``.

    Raises :class:`PersonaError` naming the file and the persona at fault.
    """
    path = resolve_path(path)
    try:
        raw = load_yaml(path)
    except ConfigError as exc:
        raise PersonaError(str(exc)) from exc
    if not isinstance(raw, Mapping) or not isinstance(raw.get("personas"), list):
        raise PersonaError(f"{path}: expected a mapping with a 'personas' list")
    version = raw.get("schema_version", SCHEMA_VERSION)
    if version != SCHEMA_VERSION:
        raise PersonaError(f"{path}: schema_version {version!r} is not supported ({SCHEMA_VERSION})")
    unknown = sorted(set(raw) - {"schema_version", "personas"})
    if unknown:
        raise PersonaError(f"{path}: unknown top-level key(s) {unknown}")

    personas: dict[str, Persona] = {}
    for index, entry in enumerate(raw["personas"]):
        try:
            persona = validate_persona(entry)
        except PersonaError as exc:
            raise PersonaError(f"{path}, personas[{index}]: {exc}") from exc
        if persona.persona_id in personas:
            raise PersonaError(f"{path}: persona_id {persona.persona_id!r} is defined twice")
        personas[persona.persona_id] = persona
    if not personas:
        raise PersonaError(f"{path}: no personas defined")
    return personas
