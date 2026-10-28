"""Scenario registry: build a scenario description from a config mapping or a YAML file.

There are two kinds of scenario, each with its own config schema and its own builder:

* the two-agent scenarios of issue #24 (``schema_version: 1``): :func:`build_scenario`,
  :func:`load_scenario`, which return a :class:`~negsim.scenarios.base.ScenarioSpec`;
* the avoidance scenarios of issue #26 (``schema_version: 2``): :func:`build_crowd_scenario`,
  :func:`load_crowd_scenario`, which return a
  :class:`~negsim.scenarios.crowd_base.CrowdScenarioSpec`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional

from ..configutil import ConfigError, deep_merge, load_yaml, resolve_path
from .base import Scenario, ScenarioSpec
from .bidirectional_flow import BidirectionalFlowScenario
from .corridor_to_bottleneck import CorridorToBottleneckScenario
from .crowd_base import CrowdScenario, CrowdScenarioSpec
from .doorway import DoorwayScenario
from .group_head_on import GroupHeadOnScenario
from .hallway import HallwayScenario
from .intersection import IntersectionScenario
from .open_crossing import OpenCrossingScenario
from .overtaking import OvertakingScenario
from .passage_meeting import PassageMeetingScenario
from .wide_corridor_head_on import WideCorridorHeadOnScenario

SCENARIOS: dict[str, type[Scenario]] = {
    cls.type_name: cls for cls in (DoorwayScenario, IntersectionScenario, HallwayScenario)
}

CROWD_SCENARIOS: dict[str, type[CrowdScenario]] = {
    cls.type_name: cls
    for cls in (
        WideCorridorHeadOnScenario,
        OpenCrossingScenario,
        OvertakingScenario,
        CorridorToBottleneckScenario,
        BidirectionalFlowScenario,
        PassageMeetingScenario,  # issue #32
        GroupHeadOnScenario,  # issue #110
    )
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


def build_crowd_scenario(cfg: Mapping[str, Any]) -> CrowdScenarioSpec:
    """Build an avoidance scenario (issue #26) from its config."""
    if not isinstance(cfg, Mapping) or "type" not in cfg:
        raise ConfigError("scenario config: expected a mapping with a 'type' key")
    scenario_type = cfg["type"]
    if scenario_type not in CROWD_SCENARIOS:
        hint = ""
        if scenario_type in SCENARIOS:
            hint = (
                f" {scenario_type!r} is a two-agent scenario of issue #24; it is run by a "
                "negotiation experiment, not by the avoidance layer."
            )
        raise ConfigError(
            f"scenario config: unknown avoidance scenario type {scenario_type!r}; expected one of "
            f"{sorted(CROWD_SCENARIOS)}.{hint}"
        )
    return CROWD_SCENARIOS[scenario_type]().build(cfg)


def load_crowd_scenario(
    path: Path | str, overrides: Optional[Mapping[str, Any]] = None
) -> CrowdScenarioSpec:
    return build_crowd_scenario(load_scenario_config(path, overrides))
