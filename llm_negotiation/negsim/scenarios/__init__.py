"""Scenarios: the base class, the doorway, the intersection, the hallway, and the registry."""

from .base import (
    ConflictSettings,
    DeadlockSettings,
    Layout,
    ObservationSettings,
    RegionInfo,
    Scenario,
    ScenarioSpec,
    SlotLayout,
)
from .doorway import DoorwayScenario
from .hallway import HallwayScenario
from .intersection import IntersectionScenario
from .registry import SCENARIOS, build_scenario, load_scenario, load_scenario_config

__all__ = [
    "SCENARIOS",
    "ConflictSettings",
    "DeadlockSettings",
    "DoorwayScenario",
    "HallwayScenario",
    "IntersectionScenario",
    "Layout",
    "ObservationSettings",
    "RegionInfo",
    "Scenario",
    "ScenarioSpec",
    "SlotLayout",
    "build_scenario",
    "load_scenario",
    "load_scenario_config",
]
