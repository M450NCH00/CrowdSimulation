"""Scenario registry: build a :class:`ScenarioSpec` from a config mapping or a YAML file."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional

from ..configutil import ConfigError, deep_merge, load_yaml, resolve_path
from .base import Scenario, ScenarioSpec
from .doorway import DoorwayScenario
from .hallway import HallwayScenario
from .intersection import IntersectionScenario

SCENARIOS: dict[str, type[Scenario]] = {
    cls.type_name: cls for cls in (DoorwayScenario, IntersectionScenario, HallwayScenario)
}


def build_scenario(cfg: Mapping[str, Any]) -> ScenarioSpec:
    if not isinstance(cfg, Mapping) or "type" not in cfg:
        raise ConfigError("scenario config: expected a mapping with a 'type' key")
    scenario_type = cfg["type"]
    if scenario_type not in SCENARIOS:
        raise ConfigError(
            f"scenario config: unknown type {scenario_type!r}; expected one of {sorted(SCENARIOS)}"
        )
    return SCENARIOS[scenario_type]().build(cfg)


def load_scenario_config(
    path: Path | str, overrides: Optional[Mapping[str, Any]] = None
) -> dict[str, Any]:
    """Read a scenario YAML file and lay ``overrides`` on top of it."""
    cfg = load_yaml(resolve_path(path))
    if not isinstance(cfg, Mapping):
        raise ConfigError(f"{path}: expected a mapping at the top level")
    return deep_merge(cfg, overrides or {})


def load_scenario(path: Path | str, overrides: Optional[Mapping[str, Any]] = None) -> ScenarioSpec:
    return build_scenario(load_scenario_config(path, overrides))
