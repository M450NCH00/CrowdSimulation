"""Observation to text: the situation report an agent is shown before it speaks.

The report is rebuilt from the state of the world every turn, because the agents may be
moving while they talk. Every line is one field that an experiment can switch on or off
(``negotiation.info_fields``), so that an ablation can test whether a piece of
information changes the outcome.

What counts as observable
-------------------------
An agent knows everything about itself. Of the other agent it is shown only what a
person standing there could plausibly perceive:

=========================  =====================================================================
shown                      why it is observable
=========================  =====================================================================
current speed              one can see how fast someone is walking (visibility key ``speed``)
body width                 one can see how big someone is (visibility key ``size``)
distance to the region     one can see where someone is
time to the region         worked out from the two above, at the *current* speed
=========================  =====================================================================

Never shown, whatever the settings: the other agent's maximum speed (one sees how fast
someone is going, not how fast they could go), its goal, its planned path, and the role it
has been given. The other agent's age, gender, task and backstory are persona attributes
and are handled by the prompt template under the same visibility settings.

All quantities are in SI units and rounded the same way everywhere: speeds, sizes and
distances to two decimal places, times to one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..configutil import ConfigError
from ..core.agent import AgentRuntime
from ..core.world import World
from ..scenarios.base import ScenarioSpec
from .prompts import PromptTemplate

INFO_FIELDS: tuple[str, ...] = (
    "elapsed_time",
    "own_speed",
    "own_max_speed",
    "own_size",
    "own_distance_to_region",
    "own_time_to_region",
    "other_speed",
    "other_size",
    "other_distance_to_region",
    "other_time_to_region",
    "region_geometry",
)

# A field about the other agent is shown only if this visibility setting allows it.
REQUIRES_VISIBILITY = {
    "other_speed": "speed",
    "other_time_to_region": "speed",
    "other_size": "size",
}

STATIONARY_SPEED = 0.01  # m/s; below this the other agent is described as not moving

APPROACHING, INSIDE, PAST = "approaching", "inside", "past"


def resolve_info_fields(raw: Any) -> tuple[str, ...]:
    """Info fields from an experiment config: ``"all"``, ``"none"`` or a list of names."""
    if raw is None or raw == "none":
        return ()
    if raw == "all":
        return INFO_FIELDS
    if not isinstance(raw, (list, tuple)):
        raise ConfigError(f"info_fields: expected 'all', 'none' or a list, got {raw!r}")
    unknown = [name for name in raw if name not in INFO_FIELDS]
    if unknown:
        raise ConfigError(f"info_fields: unknown field(s) {unknown}; known: {list(INFO_FIELDS)}")
    return tuple(name for name in INFO_FIELDS if name in raw)


@dataclass(frozen=True)
class RegionStatus:
    """Where an agent is relative to the physical conflict region.

    ``distance`` is from the agent's leading edge to the region's entry along its path,
    and is zero once the agent is inside or past the region.
    """

    state: str
    distance: float


def region_status(agent: AgentRuntime) -> RegionStatus:
    front = agent.path_s + agent.spec.radius
    rear = agent.path_s - agent.spec.radius
    if front < agent.spec.region_entry_s:
        return RegionStatus(APPROACHING, agent.spec.region_entry_s - front)
    if rear < agent.spec.region_exit_s:
        return RegionStatus(INSIDE, 0.0)
    return RegionStatus(PAST, 0.0)


@dataclass(frozen=True)
class Observation:
    """The numbers behind one situation report (logged alongside the text)."""

    elapsed_time: float
    own_speed: float
    own_max_speed: float
    own_size: float
    own_region: RegionStatus
    other_speed: float
    other_size: float
    other_region: RegionStatus
    region_kind: str
    region_width: float
    region_length: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "elapsed_time_s": round(self.elapsed_time, 4),
            "own_speed_mps": round(self.own_speed, 4),
            "own_max_speed_mps": round(self.own_max_speed, 4),
            "own_size_m": round(self.own_size, 4),
            "own_region_state": self.own_region.state,
            "own_distance_to_region_m": round(self.own_region.distance, 4),
            "other_speed_mps": round(self.other_speed, 4),
            "other_size_m": round(self.other_size, 4),
            "other_region_state": self.other_region.state,
            "other_distance_to_region_m": round(self.other_region.distance, 4),
            "region_kind": self.region_kind,
            "region_width_m": self.region_width,
            "region_length_m": self.region_length,
        }


def observe(
    world: World, spec: ScenarioSpec, agent_id: int, other_id: int, dialogue_start_time: float
) -> Observation:
    """What ``agent_id`` can tell about itself and ``other_id`` right now."""
    own, other = world.agents[agent_id], world.agents[other_id]
    return Observation(
        elapsed_time=world.time - dialogue_start_time,
        own_speed=own.speed,
        own_max_speed=own.spec.max_speed,
        own_size=own.spec.body_length,
        own_region=region_status(own),
        other_speed=other.speed,
        other_size=other.spec.body_length,
        other_region=region_status(other),
        region_kind=spec.region.kind,
        region_width=spec.region.width,
        region_length=spec.region.length,
    )


def _m(value: float) -> str:
    return f"{value:.2f}"


def _s(value: float) -> str:
    return f"{value:.1f}"


def render_report(
    observation: Observation,
    info_fields: tuple[str, ...],
    visibility: Mapping[str, bool],
    template: PromptTemplate,
) -> str:
    """The report text, or an empty string if no field is switched on."""
    report = template.report
    kind = observation.region_kind
    values = {
        "elapsed_time": _s(observation.elapsed_time),
        "own_speed": _m(observation.own_speed),
        "own_max_speed": _m(observation.own_max_speed),
        "own_size": _m(observation.own_size),
        "own_distance": _m(observation.own_region.distance),
        "own_time": _s(observation.own_region.distance / observation.own_max_speed),
        "other_speed": _m(observation.other_speed),
        "other_size": _m(observation.other_size),
        "other_distance": _m(observation.other_region.distance),
        "other_time": _s(
            observation.other_region.distance / max(observation.other_speed, STATIONARY_SPEED)
        ),
        "own_region": report["own_region"][kind],
        "other_region": report["other_region"][kind],
        "region_kind": kind,
        "width": _m(observation.region_width),
        "length": _m(observation.region_length),
    }

    lines = []
    for name in info_fields:
        needed = REQUIRES_VISIBILITY.get(name)
        if needed is not None and not visibility.get(needed, False):
            continue
        key = _line_key(name, observation)
        if key is None:
            continue
        text = report["region_geometry"][kind] if key == "region_geometry" else report["lines"][key]
        lines.append(text.format_map(values))
    if not lines:
        return ""
    return "\n".join([report["header"], *lines])


def _line_key(name: str, observation: Observation) -> str | None:
    """Which template line a field uses in the agent's current state, if any."""
    for prefix, status in (("own", observation.own_region), ("other", observation.other_region)):
        if name == f"{prefix}_distance_to_region" and status.state != APPROACHING:
            return f"{prefix}_distance_{status.state}"
        if name == f"{prefix}_time_to_region" and status.state != APPROACHING:
            return None  # the distance line already says where the agent is
    if name == "other_time_to_region" and observation.other_speed < STATIONARY_SPEED:
        return "other_time_stationary"
    return name
