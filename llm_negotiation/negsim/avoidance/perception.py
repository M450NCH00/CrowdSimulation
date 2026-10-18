"""The perception record: what one agent can tell about a neighbour that has come into range.

A record is built once, at the moment a neighbour enters an agent's sensing radius, and is
handed to the agent's directive provider. It is the input that rules read, so its fields
are a contract: ``docs/perception.md`` describes each one, and
:data:`PERCEPTION_SCHEMA_VERSION` must be raised whenever a field is added, removed,
renamed or changes meaning.

What is observable
------------------
Of the neighbour, an agent perceives where it is, how it is moving, how big it is, and
those persona attributes that the run's visibility settings allow (the settings of issue
#24: ``age``, ``gender``, ``backstory``, ``speed``, ``size``). The neighbour's **task is
never in a record**, whatever the settings say, and neither are its preferred or maximum
speed, its goal, its path, or any directive it holds. Of itself, an agent knows its own
motion, size, preferred speed, age, gender and (version 3) group. Of its surroundings, it
perceives the nearest wall and the free width of the passage it is in.

Version 2 (issue #28) adds what the two agents of a pair can *both* tell about the two of
them together (:class:`PairFeatures`): the kind of encounter, how far apart their
directions of travel are, how wide the passage between them is, their difference in age,
and, at a single-file segment, how soon each would reach it. These are computed once per
pair, with the lower-numbered agent first, so that the two agents' records carry the same
values to the last bit. That is what lets a rule evaluated on one shared snapshot stand
for each agent evaluating it on its own (``docs/rule-matching.md``).

A field whose value is hidden, or does not exist, is ``None``; it is never left out and
never replaced by a default.

Version 3 (issue #32) adds two things. **A fictional group** (``ethnic_group``): an agent's own
and, when the run's visibility settings show it, the neighbour's; an agent may see it, but it
is flagged as not readable by rules (:data:`NOT_RULE_REFERENCEABLE`), and nothing a rule reads
is derived from it. **Where each of the two is in a single-file passage** they meet in:
``in_segment``, ``segment_distance_travelled``, ``segment_distance_ahead`` and
``segment_distance_behind``, computed once per pair from the two positions and the passage's
geometry, so that both agents get the same values (:func:`segment_position`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from ..core.agent import AgentRuntime
from ..core.geometry import Rect, Vec, wrap_angle
from ..personas.schema import ATTRIBUTES

PERCEPTION_SCHEMA_VERSION = 3

# The kinds of encounter of a pair (``docs/perception.md``, "Pair-level fields").
ENCOUNTER_HEAD_ON = "head_on"
ENCOUNTER_CROSSING = "crossing"
ENCOUNTER_OVERTAKING = "overtaking"
ENCOUNTER_SINGLE_FILE = "single_file_segment"
ENCOUNTER_NONE = "none"  # not approaching each other, and no single-file segment between them
ENCOUNTER_CLASSES = (
    ENCOUNTER_HEAD_ON,
    ENCOUNTER_CROSSING,
    ENCOUNTER_OVERTAKING,
    ENCOUNTER_SINGLE_FILE,
    ENCOUNTER_NONE,
)
#: Directions of travel that differ by less than this make an overtaking encounter, by
#: more than :data:`HEAD_ON_MIN_DIFFERENCE_RAD` a head-on one, and in between a crossing:
#: the range from 0 to 180 degrees cut into three equal parts. A definition with no
#: source [placeholder].
OVERTAKING_MAX_DIFFERENCE_RAD = math.pi / 3.0
HEAD_ON_MIN_DIFFERENCE_RAD = 2.0 * math.pi / 3.0
#: The corridor width between two agents is measured at points this far apart, at most,
#: along the straight line from one to the other.
CORRIDOR_SAMPLE_SPACING_M = 0.25

#: Persona attributes that never appear in a record, whatever the visibility settings.
NEVER_OBSERVABLE = frozenset({"task"})
#: Persona attributes an agent knows about itself and that a record carries.
OWN_ATTRIBUTES = ("age", "gender", "ethnic_group")
#: Below this speed an agent's heading is taken from its pose, not from its velocity.
STATIONARY_SPEED = 1e-6
#: The per-agent passage fields of version 3, in order (``docs/perception.md``).
SEGMENT_FIELDS = ("in_segment", "segment_distance_travelled", "segment_distance_ahead", "segment_distance_behind")
_NO_POSITION: tuple[Optional[bool], Optional[float], Optional[float], Optional[float]] = (None, None, None, None)


@dataclass(frozen=True)
class ObserverState:
    """The observing agent's knowledge of itself."""

    radius_m: float
    speed_mps: float
    heading_rad: float
    preferred_speed_mps: float
    attributes: Mapping[str, Any]
    time_to_segment_s: Optional[float] = None
    in_segment: Optional[bool] = None
    segment_distance_travelled: Optional[float] = None
    segment_distance_ahead: Optional[float] = None
    segment_distance_behind: Optional[float] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "radius_m": self.radius_m,
            "speed_mps": _r(self.speed_mps),
            "heading_rad": _r(self.heading_rad),
            "preferred_speed_mps": self.preferred_speed_mps,
            "attributes": dict(self.attributes),
            "time_to_segment_s": _r(self.time_to_segment_s),
            "in_segment": self.in_segment,
            "segment_distance_travelled": _r(self.segment_distance_travelled),
            "segment_distance_ahead": _r(self.segment_distance_ahead),
            "segment_distance_behind": _r(self.segment_distance_behind),
        }


@dataclass(frozen=True)
class PairFeatures:
    """What both agents of a pair can tell about the two of them together.

    Built by :func:`pair_features` with the lower-numbered agent first, once per pair and
    step, so that each of the two gets exactly the same values. ``time_to_segment_s`` and
    ``segment`` (each agent's :func:`segment_position`, issue #32) are in the order of
    ``agents``. ``docs/perception.md`` defines every field.
    """

    agents: tuple[int, int]
    encounter_class: Optional[str]
    heading_difference_rad: float
    min_corridor_width_m: float
    age_difference_years: Optional[float]
    single_file_segment: Optional[str]
    time_to_segment_s: tuple[Optional[float], Optional[float]]
    segment: tuple[tuple, tuple] = (_NO_POSITION, _NO_POSITION)

    def time_to_segment_of(self, agent_id: int) -> Optional[float]:
        return self.time_to_segment_s[self.agents.index(agent_id)]

    def segment_of(self, agent_id: int) -> dict[str, Any]:
        """The agent's passage fields, by name (``SEGMENT_FIELDS``)."""
        return dict(zip(SEGMENT_FIELDS, self.segment[self.agents.index(agent_id)]))

    def as_dict(self) -> dict[str, Any]:
        return {
            "encounter_class": self.encounter_class,
            "heading_difference_rad": _r(self.heading_difference_rad),
            "min_corridor_width_m": _r(self.min_corridor_width_m),
            "age_difference_years": self.age_difference_years,
            "single_file_segment": self.single_file_segment,
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
    pair: PairFeatures

    @property
    def neighbour_time_to_segment_s(self) -> Optional[float]:
        return self.pair.time_to_segment_of(self.neighbour_id)

    @property
    def neighbour_segment(self) -> dict[str, Any]:
        """The neighbour's passage fields (version 3), by name."""
        return self.pair.segment_of(self.neighbour_id)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PerceptionRecord":
        """A record of version 2 or 3 read back from a log (``as_dict``), as far as the log keeps it.

        The log rounds to six decimal places, so the record read back is the logged one, not
        the one the run held. Used by issue #30 to take conflict cases from finished runs. A
        version 2 record has no passage fields: they are read back as missing (``None``).
        """
        version = data.get("schema_version")
        if version not in (2, PERCEPTION_SCHEMA_VERSION):
            raise ValueError(f"a perception record of version 2 or {PERCEPTION_SCHEMA_VERSION} is needed, got {version!r}")
        observer, environment, pair = data["observer"], data["environment"], data["pair"]
        first, second = sorted((data["observer_id"], data["neighbour_id"]))
        own, other = observer.get("time_to_segment_s"), data.get("neighbour_time_to_segment_s")
        own_segment = tuple(observer.get(name) for name in SEGMENT_FIELDS)
        other_segment = tuple(data.get(f"neighbour_{name}") for name in SEGMENT_FIELDS)
        velocity = data["relative_velocity_mps"]
        return cls(
            schema_version=data["schema_version"],
            step=data["step"],
            time_s=data["time_s"],
            observer_id=data["observer_id"],
            neighbour_id=data["neighbour_id"],
            relative_position_m=tuple(data["relative_position_m"]),
            distance_m=data["distance_m"],
            bearing_rad=data["bearing_rad"],
            relative_velocity_mps=None if velocity is None else tuple(velocity),
            closing_speed_mps=data["closing_speed_mps"],
            time_to_collision_s=data["time_to_collision_s"],
            neighbour_radius_m=data["neighbour_radius_m"],
            neighbour_speed_mps=data["neighbour_speed_mps"],
            neighbour_heading_rad=data["neighbour_heading_rad"],
            neighbour_heading_relative_rad=data["neighbour_heading_relative_rad"],
            neighbour_attributes=dict(data["neighbour_attributes"]),
            observer=ObserverState(
                radius_m=observer["radius_m"],
                speed_mps=observer["speed_mps"],
                heading_rad=observer["heading_rad"],
                preferred_speed_mps=observer["preferred_speed_mps"],
                attributes=dict(observer["attributes"]),
                time_to_segment_s=own,
                **dict(zip(SEGMENT_FIELDS, own_segment)),
            ),
            environment=EnvironmentFeatures(**{name: environment[name] for name in ENVIRONMENT_FIELDS}),
            pair=PairFeatures(
                agents=(first, second),
                encounter_class=pair["encounter_class"],
                heading_difference_rad=pair["heading_difference_rad"],
                min_corridor_width_m=pair["min_corridor_width_m"],
                age_difference_years=pair["age_difference_years"],
                single_file_segment=pair["single_file_segment"],
                time_to_segment_s=(own, other) if data["observer_id"] == first else (other, own),
                segment=(own_segment, other_segment) if data["observer_id"] == first else (other_segment, own_segment),
            ),
        )

    def as_dict(self) -> dict[str, Any]:
        velocity = self.relative_velocity_mps
        other = self.neighbour_segment
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
            "neighbour_time_to_segment_s": _r(self.neighbour_time_to_segment_s),
            "neighbour_in_segment": other["in_segment"],
            "neighbour_segment_distance_travelled": _r(other["segment_distance_travelled"]),
            "neighbour_segment_distance_ahead": _r(other["segment_distance_ahead"]),
            "neighbour_segment_distance_behind": _r(other["segment_distance_behind"]),
            "neighbour_attributes": dict(self.neighbour_attributes),
            "observer": self.observer.as_dict(),
            "environment": self.environment.as_dict(),
            "pair": self.pair.as_dict(),
        }


#: Top-level keys of a serialised record of version 2, in order.
_PERCEPTION_FIELDS_V2 = (
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
    "neighbour_time_to_segment_s",
    "neighbour_attributes",
    "observer",
    "environment",
    "pair",
)
#: Top-level keys of a serialised record, in order. ``docs/perception.md`` must name each.
PERCEPTION_FIELDS = (
    *_PERCEPTION_FIELDS_V2[:16],
    *(f"neighbour_{name}" for name in SEGMENT_FIELDS),
    *_PERCEPTION_FIELDS_V2[16:],
)
_OBSERVER_FIELDS_V2 = ("radius_m", "speed_mps", "heading_rad", "preferred_speed_mps", "attributes", "time_to_segment_s")
OBSERVER_FIELDS = (*_OBSERVER_FIELDS_V2, *SEGMENT_FIELDS)
ENVIRONMENT_FIELDS = (
    "nearest_wall_distance_m",
    "free_width_m",
    "free_width_left_m",
    "free_width_right_m",
    "single_file_ahead_m",
)
PAIR_FIELDS = (
    "encounter_class",
    "heading_difference_rad",
    "min_corridor_width_m",
    "age_difference_years",
    "single_file_segment",
)

#: The fields of each earlier version, so that a run folder written then still checks
#: out against what it declares (``negsim.runlog.schema``).
FIELDS_BY_VERSION = {
    1: {
        "record": tuple(name for name in _PERCEPTION_FIELDS_V2 if name not in ("neighbour_time_to_segment_s", "pair")),
        "observer": _OBSERVER_FIELDS_V2[:-1],
        "environment": ENVIRONMENT_FIELDS,
        "pair": (),
    },
    2: {"record": _PERCEPTION_FIELDS_V2, "observer": _OBSERVER_FIELDS_V2, "environment": ENVIRONMENT_FIELDS, "pair": PAIR_FIELDS},
    3: {"record": PERCEPTION_FIELDS, "observer": OBSERVER_FIELDS, "environment": ENVIRONMENT_FIELDS, "pair": PAIR_FIELDS},
}


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


def corridor_width_between(
    start: Vec,
    end: Vec,
    obstacles: Sequence[Rect],
    environment_range: float,
    spacing: float = CORRIDOR_SAMPLE_SPACING_M,
) -> float:
    """The narrowest free width of the passage along the straight line from ``start`` to ``end``.

    At points no more than ``spacing`` apart along the line, including both ends, the
    distance to the nearest wall is measured at right angles to the line on each side,
    and the two are added. A side with no wall within ``environment_range`` counts as
    ``environment_range``: as far as either agent can see. A point inside a wall has
    width 0. The smallest width found is returned.
    """
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    nx, ny = (-dy / length, dx / length) if length > 0.0 else (0.0, 1.0)
    count = max(1, math.ceil(length / spacing))
    narrowest = math.inf
    for k in range(count + 1):
        t = k / count
        point = (start[0] + t * dx, start[1] + t * dy)
        width = 0.0
        for direction in ((nx, ny), (-nx, -ny)):
            nearest = environment_range
            for wall in obstacles:
                hit = wall.ray_distance(point, direction)
                if hit is not None and hit < nearest:
                    nearest = hit
            width += nearest
        if width < narrowest:
            narrowest = width
    return narrowest


def _heading_into(position: Vec, heading: float, rect: Rect) -> bool:
    """Inside ``rect``, or facing it: its nearest point is less than 90 degrees off ``heading``."""
    if rect.distance_to(position) == 0.0:
        return True
    qx = min(max(position[0], rect.xmin), rect.xmax)
    qy = min(max(position[1], rect.ymin), rect.ymax)
    return math.cos(heading) * (qx - position[0]) + math.sin(heading) * (qy - position[1]) > 0.0


def _time_to_reach(agent: AgentRuntime, rect: Rect) -> Optional[float]:
    """Distance to ``rect`` divided by the agent's present speed; 0 inside; ``None`` standing still."""
    distance = rect.distance_to(agent.pose.xy)
    if distance == 0.0:
        return 0.0
    speed = agent.speed
    return distance / speed if speed > STATIONARY_SPEED else None


def segment_position(
    position: Vec, other: Vec, rect: Rect
) -> tuple[bool, Optional[float], Optional[float], Optional[float]]:
    """Where an agent is in the single-file passage it meets another agent in (version 3).

    Returns ``(in_segment, segment_distance_travelled, segment_distance_ahead,
    segment_distance_behind)``. The passage is the free space ``rect``: its long side is its
    axis, and its two short sides are its ends. **Inside** means the agent's centre is in the
    rect. The end **ahead** of the agent is the one on the other agent's side along the axis,
    and the end **behind** it the other one: in a meeting each faces the other, so nothing but
    the two positions and the passage is needed, and both agents compute the same values.
    **Travelled**, how far it has walked in, is its distance from the end behind it, by which
    it came in; in a meeting it equals the distance behind. The three distances are ``None``
    when the agent is outside, and when the two are level along the axis (two bodies in a
    single-file passage cannot be).
    """
    x, y = position
    if not (rect.xmin <= x <= rect.xmax and rect.ymin <= y <= rect.ymax):
        return False, None, None, None
    along_x = rect.xmax - rect.xmin >= rect.ymax - rect.ymin
    axis = 0 if along_x else 1
    low, high = (rect.xmin, rect.xmax) if along_x else (rect.ymin, rect.ymax)
    mine, theirs = position[axis], other[axis]
    if theirs == mine:
        return True, None, None, None
    ahead, behind = (high - mine, mine - low) if theirs > mine else (mine - low, high - mine)
    return True, behind, ahead, behind


def classify_encounter(
    a: AgentRuntime,
    b: AgentRuntime,
    heading_a: float,
    heading_b: float,
    heading_difference: float,
    segments: Sequence[Any] = (),
) -> tuple[str, Optional[int]]:
    """The kind of encounter of a pair, and the single-file segment it is about, if any.

    In this order (``docs/perception.md``, "Pair-level fields"):

    1. ``single_file_segment`` if a segment the scenario declares is too narrow for the two
       to pass in (narrower than their two diameters together, as for the arbiter) and
       each is inside it or facing it;
    2. ``none`` if they are not approaching each other: ``p · w >= 0``, with ``p`` and
       ``w`` the relative position and velocity;
    3. otherwise by how far apart their directions of travel are: ``overtaking`` below
       60 degrees, ``head_on`` above 120, ``crossing`` in between.

    ``segments`` are objects with ``rect`` and ``width``, such as the scenario's
    ``SingleFileSegment``.
    """
    diameters = 2.0 * (a.spec.radius + b.spec.radius)
    for index, segment in enumerate(segments):
        if segment.width >= diameters:
            continue
        if _heading_into(a.pose.xy, heading_a, segment.rect) and _heading_into(b.pose.xy, heading_b, segment.rect):
            return ENCOUNTER_SINGLE_FILE, index
    px, py = b.pose.x - a.pose.x, b.pose.y - a.pose.y
    wx, wy = b.velocity[0] - a.velocity[0], b.velocity[1] - a.velocity[1]
    if px * wx + py * wy >= 0.0:
        return ENCOUNTER_NONE, None
    if heading_difference < OVERTAKING_MAX_DIFFERENCE_RAD:
        return ENCOUNTER_OVERTAKING, None
    if heading_difference > HEAD_ON_MIN_DIFFERENCE_RAD:
        return ENCOUNTER_HEAD_ON, None
    return ENCOUNTER_CROSSING, None


def encounter_of(
    a: AgentRuntime, b: AgentRuntime, visibility: Mapping[str, bool], segments: Sequence[Any] = ()
) -> tuple[Optional[str], Optional[int], float]:
    """The encounter class of a pair, the index of its single-file segment, and the heading
    difference: the cheap part of :func:`pair_features`, in the same fixed order.

    The class needs ``speed`` (are they approaching?) and ``size`` (is a segment too
    narrow for them?) to be visible; without either it is ``None``.
    """
    if a.agent_id > b.agent_id:
        a, b = b, a
    heading_a, heading_b = heading_of(a), heading_of(b)
    difference = abs(wrap_angle(heading_b - heading_a))
    if not (visibility.get("speed", False) and visibility.get("size", False)):
        return None, None, difference
    encounter, index = classify_encounter(a, b, heading_a, heading_b, difference, segments)
    return encounter, index, difference


def pair_features(
    a: AgentRuntime,
    b: AgentRuntime,
    obstacles: Sequence[Rect],
    visibility: Mapping[str, bool],
    attributes: Mapping[int, Mapping[str, Any]],
    environment_range: float,
    segments: Sequence[Any] = (),
) -> PairFeatures:
    """What both agents of a pair can tell about the two of them, computed in a fixed order.

    The lower-numbered agent is always taken first, whichever order the two are given in,
    so the result is the same for both. Visibility: ``encounter_class`` (and with it the
    times to a single-file segment) needs ``speed``, to tell whether the two are
    approaching, and ``size``, to tell whether a segment is too narrow for them; without
    either it is ``None``. ``age_difference_years`` needs ``age``. The direction of travel
    and the walls are always perceived.
    """
    if a.agent_id > b.agent_id:
        a, b = b, a
    if math.isinf(environment_range):
        environment_range = max(a.spec.sensing_radius, b.spec.sensing_radius)

    encounter, index, difference = encounter_of(a, b, visibility, segments)
    segment_name = None
    times: tuple[Optional[float], Optional[float]] = (None, None)
    positions = (_NO_POSITION, _NO_POSITION)
    if index is not None:
        segment = segments[index]
        segment_name = segment.name
        times = (_time_to_reach(a, segment.rect), _time_to_reach(b, segment.rect))
        positions = (segment_position(a.pose.xy, b.pose.xy, segment.rect), segment_position(b.pose.xy, a.pose.xy, segment.rect))

    age_difference = None
    if visibility.get("age", False):
        age_a = (attributes.get(a.agent_id) or {}).get("age")
        age_b = (attributes.get(b.agent_id) or {}).get("age")
        if age_a not in (None, "") and age_b not in (None, ""):
            age_difference = abs(age_a - age_b)

    return PairFeatures(
        agents=(a.agent_id, b.agent_id),
        encounter_class=encounter,
        heading_difference_rad=difference,
        min_corridor_width_m=corridor_width_between(a.pose.xy, b.pose.xy, obstacles, environment_range),
        age_difference_years=age_difference,
        single_file_segment=segment_name,
        time_to_segment_s=times,
        segment=positions,
    )


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
    *,
    segments: Sequence[Any] = (),
    pair: Optional[PairFeatures] = None,
) -> PerceptionRecord:
    """Build the record of ``neighbour`` as ``observer`` perceives it right now.

    ``pair`` may be passed in when it has already been computed for this pair on this
    step (the run loop does, so that the two records share it); otherwise it is computed
    here from ``segments`` and the rest.
    """
    if pair is None:
        pair = pair_features(observer, neighbour, obstacles, visibility, attributes, environment_range, segments)
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
            time_to_segment_s=pair.time_to_segment_of(observer.agent_id),
            **pair.segment_of(observer.agent_id),
        ),
        environment=environment_features(observer, obstacles, single_file_intervals, environment_range),
        pair=pair,
    )
