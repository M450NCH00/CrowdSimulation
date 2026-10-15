"""The perception record: what one agent can tell about a neighbour that has come into range.

A record is built once, at the moment a neighbour enters an agent's sensing radius, and is
handed to the agent's directive provider. It is the input that rules will read in the next
sub-issue, so its fields are a contract: ``docs/perception.md`` describes each one, and
:data:`PERCEPTION_SCHEMA_VERSION` must be raised whenever a field is added, removed,
renamed or changes meaning.

What is observable
------------------
Of the neighbour, an agent perceives where it is, how it is moving, how big it is, and
those persona attributes that the run's visibility settings allow (the settings of issue
#24: ``age``, ``gender``, ``backstory``, ``speed``, ``size``). The neighbour's **task is
never in a record**, whatever the settings say, and neither are its preferred or maximum
speed, its goal, its path, or any directive it holds. Of itself, an agent knows its own
motion, size, preferred speed, age and gender. Of its surroundings, it perceives the
nearest wall and the free width of the passage it is in.

A field whose value is hidden, or does not exist, is ``None``; it is never left out and
never replaced by a default.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from ..core.agent import AgentRuntime
from ..core.geometry import Rect, Vec, wrap_angle
from ..personas.schema import ATTRIBUTES

PERCEPTION_SCHEMA_VERSION = 1

#: Persona attributes that never appear in a record, whatever the visibility settings.
NEVER_OBSERVABLE = frozenset({"task"})
#: Persona attributes an agent knows about itself and that a record carries.
OWN_ATTRIBUTES = ("age", "gender")
#: Below this speed an agent's heading is taken from its pose, not from its velocity.
STATIONARY_SPEED = 1e-6


@dataclass(frozen=True)
class ObserverState:
    """The observing agent's knowledge of itself."""

    radius_m: float
    speed_mps: float
    heading_rad: float
    preferred_speed_mps: float
    attributes: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "radius_m": self.radius_m,
            "speed_mps": _r(self.speed_mps),
            "heading_rad": _r(self.heading_rad),
            "preferred_speed_mps": self.preferred_speed_mps,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class EnvironmentFeatures:
    """The observer's immediate surroundings.

    ``free_width_left_m`` and ``free_width_right_m`` are the distances from the observer's
    centre to the nearest wall on either side, measured at right angles to the direction
    its desired path takes there. ``free_width_m`` is their sum: the width of the passage.
    Each is ``None`` when there is no wall on that side within the environment range.
    """

    nearest_wall_distance_m: Optional[float]
    free_width_m: Optional[float]
    free_width_left_m: Optional[float]
    free_width_right_m: Optional[float]
    single_file_ahead_m: Optional[float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "nearest_wall_distance_m": _r(self.nearest_wall_distance_m),
            "free_width_m": _r(self.free_width_m),
            "free_width_left_m": _r(self.free_width_left_m),
            "free_width_right_m": _r(self.free_width_right_m),
            "single_file_ahead_m": _r(self.single_file_ahead_m),
        }


@dataclass(frozen=True)
class PerceptionRecord:
    """See ``docs/perception.md`` for the meaning and unit of every field."""

    schema_version: int
    step: int
    time_s: float
    observer_id: int
    neighbour_id: int
    relative_position_m: Vec
    distance_m: float
    bearing_rad: float
    relative_velocity_mps: Optional[Vec]
    closing_speed_mps: Optional[float]
    time_to_collision_s: Optional[float]
    neighbour_radius_m: Optional[float]
    neighbour_speed_mps: Optional[float]
    neighbour_heading_rad: float
    neighbour_heading_relative_rad: float
    neighbour_attributes: Mapping[str, Any]
    observer: ObserverState
    environment: EnvironmentFeatures

    def as_dict(self) -> dict[str, Any]:
        velocity = self.relative_velocity_mps
        return {
            "schema_version": self.schema_version,
            "step": self.step,
            "time_s": _r(self.time_s),
            "observer_id": self.observer_id,
            "neighbour_id": self.neighbour_id,
            "relative_position_m": [_r(self.relative_position_m[0]), _r(self.relative_position_m[1])],
            "distance_m": _r(self.distance_m),
            "bearing_rad": _r(self.bearing_rad),
            "relative_velocity_mps": None if velocity is None else [_r(velocity[0]), _r(velocity[1])],
            "closing_speed_mps": _r(self.closing_speed_mps),
            "time_to_collision_s": _r(self.time_to_collision_s),
            "neighbour_radius_m": self.neighbour_radius_m,
            "neighbour_speed_mps": _r(self.neighbour_speed_mps),
            "neighbour_heading_rad": _r(self.neighbour_heading_rad),
            "neighbour_heading_relative_rad": _r(self.neighbour_heading_relative_rad),
            "neighbour_attributes": dict(self.neighbour_attributes),
            "observer": self.observer.as_dict(),
            "environment": self.environment.as_dict(),
        }


#: Top-level keys of a serialised record, in order. ``docs/perception.md`` must name each.
PERCEPTION_FIELDS = (
    "schema_version",
    "step",
    "time_s",
    "observer_id",
    "neighbour_id",
    "relative_position_m",
    "distance_m",
    "bearing_rad",
    "relative_velocity_mps",
    "closing_speed_mps",
    "time_to_collision_s",
    "neighbour_radius_m",
    "neighbour_speed_mps",
    "neighbour_heading_rad",
    "neighbour_heading_relative_rad",
    "neighbour_attributes",
    "observer",
    "environment",
)
OBSERVER_FIELDS = ("radius_m", "speed_mps", "heading_rad", "preferred_speed_mps", "attributes")
ENVIRONMENT_FIELDS = (
    "nearest_wall_distance_m",
    "free_width_m",
    "free_width_left_m",
    "free_width_right_m",
    "single_file_ahead_m",
)


def _r(value: Optional[float], digits: int = 6) -> Optional[float]:
    return None if value is None else round(value, digits)


def default_visibility() -> dict[str, bool]:
    """What an agent can see of a neighbour unless a run says otherwise.

    The same defaults as issue #24 (``negsim.negotiation.prompts.default_visibility``):
    each persona attribute as its schema entry says (age and gender are visible, task and
    backstory are not), and the physical ``speed`` and ``size``. A test keeps the two equal.
    """
    visibility = {name: spec.observable for name, spec in ATTRIBUTES.items()}
    visibility.update({"speed": True, "size": True})
    return visibility


def time_to_collision(rel_pos: Vec, rel_vel: Vec, combined_radius: float) -> Optional[float]:
    """Seconds until two discs touch if both keep their current velocities.

    ``rel_pos`` and ``rel_vel`` are the neighbour's position and velocity minus the
    observer's. Returns 0 if they already touch and ``None`` if they never will.
    """
    px, py = rel_pos
    wx, wy = rel_vel
    c = px * px + py * py - combined_radius * combined_radius
    if c <= 0.0:
        return 0.0
    a = wx * wx + wy * wy
    b = px * wx + py * wy
    if a == 0.0 or b >= 0.0:
        return None  # not moving relative to each other, or moving apart
    discriminant = b * b - a * c
    if discriminant < 0.0:
        return None  # they pass without touching
    return (-b - math.sqrt(discriminant)) / a


def visible_attributes(
    attributes: Optional[Mapping[str, Any]], visibility: Mapping[str, bool]
) -> dict[str, Any]:
    """The persona attributes of a neighbour that an observer may see.

    An attribute is shown only if the visibility settings switch it on, and never if it
    is in :data:`NEVER_OBSERVABLE`. Empty values are left out.
    """
    if not attributes:
        return {}
    return {
        name: value
        for name, value in attributes.items()
        if name not in NEVER_OBSERVABLE and visibility.get(name, False) and value not in (None, "")
    }


def own_attributes(attributes: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    if not attributes:
        return {}
    return {name: attributes[name] for name in OWN_ATTRIBUTES if attributes.get(name) not in (None, "")}


def heading_of(agent: AgentRuntime) -> float:
    """Direction of travel; the pose's heading for an agent that is standing still."""
    vx, vy = agent.velocity
    if math.hypot(vx, vy) > STATIONARY_SPEED:
        return math.atan2(vy, vx)
    return agent.pose.theta


def environment_features(
    agent: AgentRuntime,
    obstacles: Sequence[Rect],
    single_file_intervals: Sequence[tuple[float, float]],
    environment_range: float,
) -> EnvironmentFeatures:
    """Nearest wall, free width of the passage, and distance to a single-file segment."""
    position = agent.pose.xy
    nearest = min((wall.distance_to(position) for wall in obstacles), default=None)

    path_heading = agent.spec.path.heading_at(agent.path_s)
    left = (-math.sin(path_heading), math.cos(path_heading))
    right = (-left[0], -left[1])
    widths = []
    for direction in (left, right):
        hits = [wall.ray_distance(position, direction) for wall in obstacles]
        hits = [hit for hit in hits if hit is not None and hit <= environment_range]
        widths.append(min(hits) if hits else None)
    free_left, free_right = widths
    free_width = None if free_left is None or free_right is None else free_left + free_right

    ahead = None
    for entry_s, exit_s in single_file_intervals:
        if agent.path_s < exit_s:
            ahead = max(0.0, entry_s - agent.path_s)
            break
    return EnvironmentFeatures(nearest, free_width, free_left, free_right, ahead)


def perceive(
    step: int,
    time_s: float,
    observer: AgentRuntime,
    neighbour: AgentRuntime,
    obstacles: Sequence[Rect],
    visibility: Mapping[str, bool],
    attributes: Mapping[int, Mapping[str, Any]],
    preferred_speed: float,
    single_file_intervals: Sequence[tuple[float, float]] = (),
    environment_range: float = math.inf,
) -> PerceptionRecord:
    """Build the record of ``neighbour`` as ``observer`` perceives it right now."""
    px, py = neighbour.pose.x - observer.pose.x, neighbour.pose.y - observer.pose.y
    distance = math.hypot(px, py)
    own_heading = heading_of(observer)
    other_heading = heading_of(neighbour)
    see_speed, see_size = visibility.get("speed", False), visibility.get("size", False)

    relative_velocity = closing = ttc = None
    if see_speed:
        wx = neighbour.velocity[0] - observer.velocity[0]
        wy = neighbour.velocity[1] - observer.velocity[1]
        relative_velocity = (wx, wy)
        closing = -(px * wx + py * wy) / distance if distance > 0.0 else 0.0
        if see_size:
            ttc = time_to_collision((px, py), (wx, wy), observer.spec.radius + neighbour.spec.radius)

    return PerceptionRecord(
        schema_version=PERCEPTION_SCHEMA_VERSION,
        step=step,
        time_s=time_s,
        observer_id=observer.agent_id,
        neighbour_id=neighbour.agent_id,
        relative_position_m=(px, py),
        distance_m=distance,
        bearing_rad=wrap_angle(math.atan2(py, px) - own_heading) if distance > 0.0 else 0.0,
        relative_velocity_mps=relative_velocity,
        closing_speed_mps=closing,
        time_to_collision_s=ttc,
        neighbour_radius_m=neighbour.spec.radius if see_size else None,
        neighbour_speed_mps=neighbour.speed if see_speed else None,
        neighbour_heading_rad=other_heading,
        neighbour_heading_relative_rad=wrap_angle(other_heading - own_heading),
        neighbour_attributes=visible_attributes(attributes.get(neighbour.agent_id), visibility),
        observer=ObserverState(
            radius_m=observer.spec.radius,
            speed_mps=observer.speed,
            heading_rad=own_heading,
            preferred_speed_mps=preferred_speed,
            attributes=own_attributes(attributes.get(observer.agent_id)),
        ),
        environment=environment_features(observer, obstacles, single_file_intervals, environment_range),
    )
