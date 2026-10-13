"""Scenarios: the two-agent scenarios of issue #24, the avoidance scenarios of issue #26, and the registry."""

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
from .bidirectional_flow import BidirectionalFlowScenario
from .corridor_to_bottleneck import CorridorToBottleneckScenario
from .crowd_base import (
    CROWD_SCHEMA_VERSION,
    AgentType,
    CrowdAgentSpec,
    CrowdLayout,
    CrowdScenario,
    CrowdScenarioSpec,
    MetricThresholds,
    Placement,
    SingleFileSegment,
)
from .doorway import DoorwayScenario
from .hallway import HallwayScenario
from .intersection import IntersectionScenario
from .open_crossing import OpenCrossingScenario
from .overtaking import OvertakingScenario
from .registry import (
    CROWD_SCENARIOS,
    SCENARIOS,
    build_crowd_scenario,
    build_scenario,
    load_crowd_scenario,
    load_scenario,
    load_scenario_config,
)
from .wide_corridor_head_on import WideCorridorHeadOnScenario

__all__ = [
    "CROWD_SCENARIOS",
    "CROWD_SCHEMA_VERSION",
    "SCENARIOS",
    "AgentType",
    "BidirectionalFlowScenario",
    "ConflictSettings",
    "CorridorToBottleneckScenario",
    "CrowdAgentSpec",
    "CrowdLayout",
    "CrowdScenario",
    "CrowdScenarioSpec",
    "DeadlockSettings",
    "DoorwayScenario",
    "HallwayScenario",
    "IntersectionScenario",
    "Layout",
    "MetricThresholds",
    "ObservationSettings",
    "OpenCrossingScenario",
    "OvertakingScenario",
    "Placement",
    "RegionInfo",
    "Scenario",
    "ScenarioSpec",
    "SingleFileSegment",
    "SlotLayout",
    "WideCorridorHeadOnScenario",
    "build_crowd_scenario",
    "build_scenario",
    "load_crowd_scenario",
    "load_scenario",
    "load_scenario_config",
]
