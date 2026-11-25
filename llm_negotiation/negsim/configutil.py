"""Small helpers for reading YAML configs and failing with a message a person can act on."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

import yaml

# llm_negotiation/ — config paths inside config files are relative to this folder.
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PACKAGE_ROOT.parent


class ConfigError(ValueError):
    """A config file is missing something, has something extra, or has a bad value."""


def load_yaml(path: Path | str) -> Any:
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        try:
            return yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise ConfigError(f"{path}: not valid YAML: {exc}") from exc


def resolve_path(path: Path | str) -> Path:
    """Resolve a path from a config file: absolute as given, otherwise under llm_negotiation/."""
    path = Path(path)
    return path if path.is_absolute() else PACKAGE_ROOT / path


def check_keys(
    mapping: Any, where: str, required: Iterable[str] = (), optional: Iterable[str] = ()
) -> Mapping[str, Any]:
    """Check that ``mapping`` is a mapping with all ``required`` keys and no unknown ones."""
    if not isinstance(mapping, Mapping):
        raise ConfigError(f"{where}: expected a mapping, got {type(mapping).__name__}")
    required, optional = list(required), list(optional)
    missing = [key for key in required if key not in mapping]
    if missing:
        raise ConfigError(f"{where}: missing required key(s) {missing}")
    unknown = [key for key in mapping if key not in required and key not in optional]
    if unknown:
        raise ConfigError(
            f"{where}: unknown key(s) {unknown}; allowed keys are {sorted(required + optional)}"
        )
    return mapping


def as_number(
    value: Any,
    where: str,
    minimum: Optional[float] = None,
    strict_minimum: bool = False,
) -> float:
    """A real number (bool is rejected), optionally bounded below."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{where}: expected a number, got {value!r}")
    number = float(value)
    if number != number or number in (float("inf"), float("-inf")):
        raise ConfigError(f"{where}: expected a finite number, got {value!r}")
    if minimum is not None:
        if strict_minimum and number <= minimum:
            raise ConfigError(f"{where}: must be greater than {minimum}, got {value!r}")
        if not strict_minimum and number < minimum:
            raise ConfigError(f"{where}: must be at least {minimum}, got {value!r}")
    return number


def as_bool(value: Any, where: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{where}: expected true or false, got {value!r}")
    return value


def as_choice(value: Any, where: str, choices: Iterable[str]) -> str:
    choices = list(choices)
    if value not in choices:
        raise ConfigError(f"{where}: expected one of {choices}, got {value!r}")
    return value


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """``base`` with ``override`` laid on top; nested mappings are merged, lists replaced."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
