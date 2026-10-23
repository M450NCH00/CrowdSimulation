"""What an LLM agent perceives in the running simulation (issue #73, RF-17; ``docs/resolution.md``,
D2, D5, D10 and D12).

RF-2's adapter tells an agent what it perceives at the snapshot of a frozen two-person case. This
module builds the same :class:`~negsim.resolution.view.View` from a running simulation, the way a
person in the agent's place would perceive it, with the values of ``configs/resolution/
llm_view_v1.yaml`` (:class:`LLMViewSettings`):

- **Who is seen.** Everyone whose centre is within ``half_angle_deg`` of the way the agent faces
  and within ``range_m``, and is not hidden: the straight line from the agent's centre to theirs
  passes through no nearer person's disc (``occlusion``; Moussaïd, Helbing & Theraulaz 2011, fig. 1)
  and, when ``walls_block_sight``, through no wall. Sorted by distance; within ``detail_range_m``
  in full, beyond it in one short line. ``max_people`` (off by default) is a cost cap: the view
  records how many people it left out (``labels["people_left_out"]``).
- **Labels.** A person keeps the "Person n" label they were first given for the whole encounter.
- **What is heard.** Everything said since the agent last looked, by anyone who was within
  ``hearing_range_m`` when they said it, from any direction. A speaker in view now is named by
  their label; one who is not is "someone", with where the voice came from, roughly, and a
  distance band, as it was when it was said.
- **Signals.** A signal appears on a person only if the agent could see them when it was made;
  ``eye_contact`` and ``nod`` also need the two within ``eye_contact_range_m``.
- **Changes since the agent last looked** (D5), for a person seen both then and now.
- **Time to meet:** the time of closest approach to the encounter partner at the present
  velocities, stated only when that closest approach would be nearer than the encounter's safety
  distance.
- **What the agent has done so far:** its earlier decisions, and what came of them.

**Only what the LLM is told** (D10). Nothing here changes the simulation: ORCA's neighbour search
and the perception record that rules read are as they were. The one record built here, for the
WHERE YOU ARE lines, is built with the run loop's own function (``perception.perceive``) and
handed only to the scenario plug-in.

**Assumptions of this module** (``WORK_LOG-73.md``), none of them sourced:

- *Where a person faces* is their direction of travel; when they stand still or walk backwards,
  the direction their path takes where they are. (The simulator turns a disc to face its
  velocity, which for someone backing out of a passage is the wrong way.)
- *"Moved over"* uses the direction threshold: a person has moved over when where they are now
  lies at least that angle off the line they were walking along when the agent last looked
  (counting only the agent's left and right now). No source gives a threshold in metres.
- *The rough direction of a voice* is one of four quarters of a circle around the listener:
  ahead within 45° of where it faces, behind within 45° of the opposite way, otherwise left or
  right. Walls do not stop sound.
- *The cap keeps the encounter partner*: with ``max_people`` set, the partner is described even
  when more than ``max_people`` people are nearer.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..avoidance.perception import heading_of, perceive
from ..configutil import PACKAGE_ROOT, ConfigError, as_bool, as_number, check_keys, load_yaml
from ..core.geometry import Rect, Vec, point_segment_distance, wrap_angle
from .adapter import _person
from .prompt import SIMULATION_CORE_TEMPLATE, CoreTemplate
from .scenario import Scenario
from .view import (
    CHANGES, DETAIL_FULL, DETAIL_SHORT, MOTION_BACKING, MOTION_STILL, MOTION_WALKING, OUTCOMES, SIGNALS,
    Block, Done, Heard, Me, SeenPerson, TimeToMeet, View,
)

LLM_VIEW_CONFIG = PACKAGE_ROOT / "configs" / "resolution" / "llm_view_v1.yaml"
#: Signals that need the two within ``eye_contact_range_m`` as well as in view.
CLOSE_SIGNALS = ("eye_contact", "nod")
#: A threshold is met at its value: rounding in the arithmetic must not hide that.
_EPS = 1e-9


def _still(speed_mps: float) -> bool:
    """A speed that reads 0.00 m/s, as everything the agent is told rounds it."""
    return round(speed_mps, 2) == 0.0


# --- settings -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class LLMViewSettings:
    """The ``llm_view`` block. ``docs/parameters.md``, section 8, says which values are sourced."""

    half_angle_deg: float
    range_m: float
    detail_range_m: float
    occlusion: bool
    walls_block_sight: bool
    hearing_range_m: float
    heard_close_m: float
    eye_contact_range_m: float
    change_speed_fraction: float
    change_direction_deg: float
    max_people: Optional[int] = None

    def __post_init__(self) -> None:
        if not 0.0 < self.half_angle_deg <= 180.0:
            raise ConfigError(f"llm_view.half_angle_deg: from more than 0 to 180, got {self.half_angle_deg}")
        if self.detail_range_m > self.range_m:
            raise ConfigError("llm_view.detail_range_m: must not exceed range_m")
        if self.eye_contact_range_m > self.range_m:
            raise ConfigError("llm_view.eye_contact_range_m: must not exceed range_m (a signal is seen only in view)")
        if self.heard_close_m > self.hearing_range_m:
            raise ConfigError("llm_view.heard_close_m: must not exceed hearing_range_m")
        if self.max_people is not None and (isinstance(self.max_people, bool) or not isinstance(self.max_people, int) or self.max_people < 1):
            raise ConfigError(f"llm_view.max_people: a whole number of at least 1, or null, got {self.max_people!r}")

    @classmethod
    def from_mapping(cls, block: Any, where: str = "llm_view") -> "LLMViewSettings":
        numbers = ("half_angle_deg", "range_m", "detail_range_m", "hearing_range_m", "heard_close_m", "eye_contact_range_m")
        check_keys(block, where, (*numbers, "occlusion", "walls_block_sight", "change_thresholds"), ("max_people",))
        changes = check_keys(block["change_thresholds"], f"{where}.change_thresholds", ("speed_fraction", "direction_deg"))
        values = {name: as_number(block[name], f"{where}.{name}", minimum=0.0, strict_minimum=True) for name in numbers}
        return cls(
            **values,
            occlusion=as_bool(block["occlusion"], f"{where}.occlusion"),
            walls_block_sight=as_bool(block["walls_block_sight"], f"{where}.walls_block_sight"),
            change_speed_fraction=as_number(changes["speed_fraction"], f"{where}.change_thresholds.speed_fraction", minimum=0.0, strict_minimum=True),
            change_direction_deg=as_number(changes["direction_deg"], f"{where}.change_thresholds.direction_deg", minimum=0.0, strict_minimum=True),
            max_people=block.get("max_people"),
        )

    @classmethod
    def load(cls, path: Path | str = LLM_VIEW_CONFIG) -> "LLMViewSettings":
        data = check_keys(load_yaml(path), str(path), ("schema_version", "llm_view"))
        if data["schema_version"] != 1:
            raise ConfigError(f"{path}: schema_version 1 is the only one, got {data['schema_version']!r}")
        return cls.from_mapping(data["llm_view"], f"{Path(path).name}: llm_view")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# --- bodies and sight ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Body:
    """A person as they physically are at one moment, in the world frame."""

    agent_id: int
    position: Vec
    velocity: Vec
    facing_rad: float  # where they look (see the module's assumptions)
    radius_m: float
    backing: bool = False

    @property
    def speed_mps(self) -> float:
        return math.hypot(*self.velocity)

    @property
    def travel_rad(self) -> float:
        """Their direction of travel; where they face when they stand still."""
        return math.atan2(self.velocity[1], self.velocity[0]) if not _still(self.speed_mps) else self.facing_rad


def body_of(agent: Any) -> Body:
    """The :class:`Body` of a simulation agent (``negsim.core.agent.AgentRuntime``)."""
    path_rad = agent.spec.path.heading_at(agent.path_s)
    vx, vy = agent.velocity
    moving = not _still(math.hypot(vx, vy))
    backing = moving and vx * math.cos(path_rad) + vy * math.sin(path_rad) < 0.0
    facing = heading_of(agent) if moving and not backing else path_rad
    return Body(agent.agent_id, agent.pose.xy, (vx, vy), facing, agent.spec.radius, backing)


def _left(rad: float) -> Vec:
    return (-math.sin(rad), math.cos(rad))


def where(observer: Body, point: Vec) -> tuple[float, float]:
    """The distance to ``point`` and its bearing from where ``observer`` faces (positive to its left)."""
    dx, dy = point[0] - observer.position[0], point[1] - observer.position[1]
    distance = math.hypot(dx, dy)
    return distance, (wrap_angle(math.atan2(dy, dx) - observer.facing_rad) if distance > 0.0 else 0.0)


def in_cone(observer: Body, target: Body, settings: LLMViewSettings) -> bool:
    distance, bearing = where(observer, target.position)
    return distance <= settings.range_m + _EPS and abs(math.degrees(bearing)) <= settings.half_angle_deg + _EPS


def hidden(observer: Body, target: Body, bodies: Sequence[Body], walls: Sequence[Rect], settings: LLMViewSettings) -> bool:
    """Whether the line of sight from ``observer`` to ``target``'s centre is blocked."""
    a, b = observer.position, target.position
    reach = math.dist(a, b)
    if settings.occlusion:
        for other in bodies:
            if other.agent_id in (observer.agent_id, target.agent_id):
                continue
            if math.dist(a, other.position) < reach and point_segment_distance(other.position, a, b) < other.radius_m:
                return True
    return settings.walls_block_sight and any(wall.intersects_segment(a, b) for wall in walls)


def sees(observer: Body, target: Body, bodies: Sequence[Body], walls: Sequence[Rect], settings: LLMViewSettings) -> bool:
    return in_cone(observer, target, settings) and not hidden(observer, target, bodies, walls, settings)


def in_sight(observer: Body, bodies: Sequence[Body], walls: Sequence[Rect], settings: LLMViewSettings) -> list[Body]:
    """Everyone ``observer`` sees, nearest first (ties by id)."""
    seen = [b for b in bodies if b.agent_id != observer.agent_id and sees(observer, b, bodies, walls, settings)]
    return sorted(seen, key=lambda b: (math.dist(observer.position, b.position), b.agent_id))


def voice_from(listener: Body, speaker: Body, settings: LLMViewSettings) -> tuple[str, str]:
    """Where a voice came from, roughly, and its distance band: (``HEARD_DIRECTIONS``, ``HEARD_BANDS``)."""
    distance, bearing = where(listener, speaker.position)
    angle = abs(math.degrees(bearing))
    direction = "ahead" if angle <= 45.0 else "behind" if angle >= 135.0 else ("left" if bearing > 0.0 else "right")
    return direction, ("close" if distance <= settings.heard_close_m + _EPS else "far")


def closest_approach(observer: Body, other: Body) -> Optional[tuple[float, float]]:
    """``(seconds, metres)``: when, at the present velocities, the two are nearest, and how near;
    ``None`` if they are not getting closer."""
    rx, ry = other.position[0] - observer.position[0], other.position[1] - observer.position[1]
    vx, vy = other.velocity[0] - observer.velocity[0], other.velocity[1] - observer.velocity[1]
    v2 = vx * vx + vy * vy
    if v2 <= 0.0:
        return None
    t = -(rx * vx + ry * vy) / v2
    if t <= 0.0:
        return None
    return t, math.hypot(rx + vx * t, ry + vy * t)


# --- what is said and signalled -----------------------------------------------------------------


@dataclass(frozen=True)
class Utterance:
    """Something said out loud, and who heard it: each listener's (direction, band) of the voice."""

    time_s: float
    speaker_id: int
    message: str
    heard_by: Mapping[int, tuple[str, str]]


@dataclass(frozen=True)
class SignalMade:
    """A signal, and who could see it when it was made."""

    time_s: float
    signaller_id: int
    signal: str
    seen_by: frozenset[int]


class Exchange:
    """What an encounter's people have said and signalled, with who perceived each, as it was
    when it happened. RF-3 records into it when it carries out a reply."""

    def __init__(self, settings: LLMViewSettings):
        self.settings = settings
        self.utterances: list[Utterance] = []
        self.signals: list[SignalMade] = []

    def say(self, time_s: float, speaker: int, message: str, bodies: Sequence[Body]) -> Optional[Utterance]:
        if not message:
            return None
        by_id = {b.agent_id: b for b in bodies}
        voice = by_id[speaker]
        heard_by = {
            b.agent_id: voice_from(b, voice, self.settings)
            for b in bodies
            if b.agent_id != speaker and math.dist(b.position, voice.position) <= self.settings.hearing_range_m + _EPS
        }
        utterance = Utterance(time_s, speaker, message, heard_by)
        self.utterances.append(utterance)
        return utterance

    def signal(self, time_s: float, signaller: int, signal: str, bodies: Sequence[Body], walls: Sequence[Rect]) -> Optional[SignalMade]:
        if signal not in SIGNALS:
            raise ValueError(f"signal: one of {SIGNALS}, got {signal!r}")
        if signal == "none":
            return None
        by_id = {b.agent_id: b for b in bodies}
        maker = by_id[signaller]
        seen_by = frozenset(
            b.agent_id
            for b in bodies
            if b.agent_id != signaller
            and sees(b, maker, bodies, walls, self.settings)
            and (signal not in CLOSE_SIGNALS or math.dist(b.position, maker.position) <= self.settings.eye_contact_range_m + _EPS)
        )
        made = SignalMade(time_s, signaller, signal, seen_by)
        self.signals.append(made)
        return made


# --- one agent across one encounter -------------------------------------------------------------


@dataclass(frozen=True)
class Decision:
    """One decision the agent made, and where it was then."""

    time_s: float
    intent: str
    position: Vec
    facing_rad: float
    message: str = ""
    signal: str = "none"


@dataclass
class _Look:
    time_s: float
    seen: dict[int, Body]


@dataclass
class Perceiver:
    """One agent's perception across one encounter: its labels, what it saw when it last looked,
    and its decisions. :meth:`look` builds the view of a decision point; :meth:`decided` records
    the reply given at it.

    ``people`` gives each person's ``age``, ``gender`` and ``errand`` (the adapter's keys); only
    the agent's own errand is ever read. ``show_age`` and ``show_gender`` are the visibility
    switches. ``since_s`` is when the encounter began: the opening view hears what was said from
    then on.
    """

    agent_id: int
    partner_id: int
    settings: LLMViewSettings
    scenario: Scenario
    core: CoreTemplate
    people: Optional[Mapping[Any, Mapping[str, Any]]] = None
    show_age: bool = True
    show_gender: bool = True
    since_s: float = -math.inf
    labels: dict[int, int] = field(default_factory=dict)
    decisions: list[Decision] = field(default_factory=list)
    looks: list[_Look] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.agent_id == self.partner_id:
            raise ValueError("an agent is not its own encounter partner")

    # --- recording --------------------------------------------------------------------------

    def decided(self, time_s: float, me: Body, intent: str, message: str = "", signal: str = "none") -> Decision:
        """Record the reply the agent gave at its latest decision point."""
        if len(self.decisions) >= len(self.looks):
            raise ValueError("a decision follows a look: call look() for the decision point first")
        decision = Decision(time_s, intent, me.position, me.facing_rad, message, signal)
        self.decisions.append(decision)
        return decision

    # --- the view ---------------------------------------------------------------------------

    def look(
        self,
        time_s: float,
        bodies: Sequence[Body],
        walls: Sequence[Rect],
        me: Me,
        exchange: Optional[Exchange] = None,
        *,
        place: Sequence[str] = (),
        extra_blocks: Sequence[Block] = (),
        notes: Sequence[str] = (),
        outcomes: Sequence[str] = (),
        safety_distance_m: Optional[float] = None,
        factor_lines: Optional[Mapping[int, Sequence[str]]] = None,
        pairwise_lines: Optional[Mapping[int, Sequence[str]]] = None,
        labels: Optional[Mapping[str, Any]] = None,
    ) -> View:
        """The view of the agent's next decision point, at ``time_s``.

        ``outcomes`` says what became of each earlier decision's steps (``view.OUTCOMES``), in
        order; carrying plans out is RF-4's, so the caller says. ``safety_distance_m`` is the
        encounter's (:func:`safety_distance`): without it there is no time-to-meet line.
        ``factor_lines`` and ``pairwise_lines`` are the lines RF-5 and RF-6 render for a person,
        by agent id.
        """
        if len(self.looks) != len(self.decisions):
            raise ValueError("the agent has not replied to its last decision point: call decided() first")
        if len(outcomes) != len(self.decisions):
            raise ValueError(f"one outcome per earlier decision: {len(self.decisions)} decisions, {len(outcomes)} outcomes")
        unknown = [o for o in outcomes if o not in OUTCOMES]
        if unknown:
            raise ValueError(f"outcomes: unknown {unknown}; known: {OUTCOMES}")
        if self.looks and time_s <= self.looks[-1].time_s:
            raise ValueError("a decision point comes after the one before it")
        by_id = {b.agent_id: b for b in bodies}
        observer = by_id[self.agent_id]

        visible = in_sight(observer, bodies, walls, self.settings)
        left_out = 0
        if self.settings.max_people is not None and len(visible) > self.settings.max_people:
            kept = visible[: self.settings.max_people]
            partner = by_id.get(self.partner_id)
            if partner in visible and partner not in kept:
                kept[-1] = partner
            left_out = len(visible) - len(kept)
            visible = kept
        for body in visible:
            if body.agent_id not in self.labels:
                self.labels[body.agent_id] = len(self.labels) + 1

        last = self.looks[-1] if self.looks else None
        since = last.time_s if last is not None else self.since_s
        seen = tuple(
            self._seen_person(observer, body, time_s, last, since, exchange, factor_lines, pairwise_lines) for body in visible
        )
        heard = self._heard(time_s, since, exchange, {b.agent_id for b in visible})
        meet = None
        partner = by_id.get(self.partner_id)
        if partner is not None and partner in visible and safety_distance_m is not None:
            approach = closest_approach(observer, partner)
            if approach is not None and approach[1] < safety_distance_m:
                meet = TimeToMeet(self.labels[self.partner_id], approach[0])

        history = tuple(self._done(decision, outcome, observer, time_s) for decision, outcome in zip(self.decisions, outcomes))
        self.looks.append(_Look(time_s, {b.agent_id: b for b in visible}))
        return View(
            agent_id=self.agent_id,
            decision_point=len(self.looks),
            me=me,
            place=tuple(place),
            templates={"core": self.core.identity(), "scenario": self.scenario.identity()},
            seen=seen,
            heard=heard,
            history=history,
            notes=tuple(notes),
            extra_blocks=tuple(extra_blocks),
            time_to_meet=meet,
            labels={
                **dict(labels or {}),
                "time_s": time_s,
                "people_left_out": left_out,
                "llm_view": self.settings.as_dict(),
                "label_of_agent": {str(agent): label for agent, label in sorted(self.labels.items())},
            },
        )

    def _seen_person(self, observer, body, time_s, last, since, exchange, factor_lines, pairwise_lines) -> SeenPerson:
        distance, bearing = where(observer, body.position)
        rx, ry = body.position[0] - observer.position[0], body.position[1] - observer.position[1]
        vx, vy = body.velocity[0] - observer.velocity[0], body.velocity[1] - observer.velocity[1]
        closing = -(rx * vx + ry * vy) / distance if distance > 0.0 else 0.0
        info = _person(self.people, body.agent_id)
        motion = MOTION_STILL if _still(body.speed_mps) else MOTION_BACKING if body.backing else MOTION_WALKING
        if last is None:
            changes: tuple[str, ...] = ()
        elif body.agent_id in last.seen:
            changes = changes_since(last.seen[body.agent_id], body, observer.facing_rad, self.settings)
        else:
            changes = ("came_into_view",)
        return SeenPerson(
            label=self.labels[body.agent_id],
            detail=DETAIL_FULL if distance <= self.settings.detail_range_m + _EPS else DETAIL_SHORT,
            distance_m=distance,
            bearing_rad=bearing,
            speed_mps=body.speed_mps,
            heading_relative_rad=wrap_angle(body.travel_rad - observer.facing_rad),
            closing_speed_mps=closing,
            width_m=2.0 * body.radius_m,
            motion=motion,
            age=info.get("age") if self.show_age else None,
            gender=info.get("gender") if self.show_gender else None,
            signal=self._signal_of(body.agent_id, time_s, since, exchange),
            changes=changes,
            factor_lines=tuple((factor_lines or {}).get(body.agent_id, ())),
            pairwise_lines=tuple((pairwise_lines or {}).get(body.agent_id, ())),
        )

    def _signal_of(self, agent: int, time_s: float, since: float, exchange: Optional[Exchange]) -> str:
        """The latest signal ``agent`` made since the agent last looked that it could see then."""
        if exchange is None:
            return "none"
        made = [s for s in exchange.signals if s.signaller_id == agent and since < s.time_s <= time_s and self.agent_id in s.seen_by]
        return made[-1].signal if made else "none"

    def _heard(self, time_s: float, since: float, exchange: Optional[Exchange], in_view: set[int]) -> tuple[Heard, ...]:
        """What was said since the agent last looked, within its hearing range. A speaker in view
        now is named; one who is not is "someone", from where the voice came when it was said."""
        if exchange is None:
            return ()
        heard = []
        for said in exchange.utterances:
            if not since < said.time_s <= time_s or self.agent_id not in said.heard_by:
                continue
            if said.speaker_id in in_view:
                heard.append(Heard(said.message, self.labels[said.speaker_id]))
            else:
                heard.append(Heard(said.message, None, *said.heard_by[self.agent_id]))
        return tuple(heard)

    def _done(self, decision: Decision, outcome: str, observer: Body, time_s: float) -> Done:
        dx, dy = observer.position[0] - decision.position[0], observer.position[1] - decision.position[1]
        left = _left(decision.facing_rad)
        ahead = (math.cos(decision.facing_rad), math.sin(decision.facing_rad))
        return Done(
            ago_s=time_s - decision.time_s,
            intent=decision.intent,
            outcome=outcome,
            message=decision.message,
            signal=decision.signal,
            sideways_m=dx * left[0] + dy * left[1],
            back_m=-(dx * ahead[0] + dy * ahead[1]),
        )


def changes_since(then: Body, now: Body, facing_rad: float, settings: LLMViewSettings) -> tuple[str, ...]:
    """What a person did between two looks (D5), in ``view.CHANGES`` order; every threshold is met
    at its value (``docs/parameters.md``, section 8.1).

    - **Speed** (Weber's law): a change of at least ``change_speed_fraction`` of their speed at the
      last look; stopping, starting and starting to walk backwards are named as such.
    - **Turned:** their direction of travel differs by at least ``change_direction_deg``.
    - **Moved over to the agent's left or right:** where they are now lies at least
      ``change_direction_deg`` off the line they were walking along at the last look, counting
      only the part of that offset that is across the agent's own left and right now
      (``facing_rad``). A step aside followed by walking on straight is a "move over" and not a turn.
    """
    found = set()
    was_still, is_still = _still(then.speed_mps), _still(now.speed_mps)
    if now.backing and not then.backing:
        found.add("backing_up")
    elif not was_still and is_still:
        found.add("stopped")
    elif was_still and not is_still:
        found.add("started_walking")
    elif now.speed_mps - then.speed_mps >= settings.change_speed_fraction * then.speed_mps - _EPS:
        found.add("sped_up")
    elif then.speed_mps - now.speed_mps >= settings.change_speed_fraction * then.speed_mps - _EPS:
        found.add("slowed_down")
    if not was_still and not then.backing:
        ux, uy = then.velocity[0] / then.speed_mps, then.velocity[1] / then.speed_mps
        dx, dy = now.position[0] - then.position[0], now.position[1] - then.position[1]
        along = dx * ux + dy * uy
        left = _left(facing_rad)
        across_me = (dx - along * ux) * left[0] + (dy - along * uy) * left[1]
        if along > 0.0 and math.degrees(math.atan2(abs(across_me), along)) >= settings.change_direction_deg - _EPS:
            found.add("moved_left" if across_me > 0.0 else "moved_right")
    if not was_still and not is_still and now.backing == then.backing:
        if abs(math.degrees(wrap_angle(now.travel_rad - then.travel_rad))) >= settings.change_direction_deg - _EPS:
            found.add("turned")
    return tuple(change for change in CHANGES if change in found)


# --- from the running simulation ----------------------------------------------------------------


def bodies_in(simulation: Any) -> list[Body]:
    """Everyone still in the scene of an ``AvoidanceSimulation``: an agent that has arrived has left it."""
    return [body_of(agent) for agent in simulation.world.agents if not agent.done]


def safety_distance(simulation: Any, i: int, j: int) -> float:
    """The encounter's safety distance: the two radii and the scenario's safety margin, as the
    conflict zone counts it (``negsim.conflict.detection.ConflictDetector.clearance``)."""
    agents = simulation.world.agents
    return agents[i].spec.radius + agents[j].spec.radius + simulation.spec.single_file_safety_margin


def scene_of(simulation: Any) -> dict[str, Any]:
    """The part of a case (``negsim.rulegen.cases``) a scenario plug-in's place lines read."""
    spec = simulation.spec
    return {
        "scenario": {
            "type": spec.scenario_type,
            "n_agents": len(simulation.world.agents),
            "single_file_segments": [
                {
                    "name": segment.name,
                    "width_m": segment.width,
                    "length_m": round(max(segment.rect.xmax - segment.rect.xmin, segment.rect.ymax - segment.rect.ymin), 6),
                }
                for segment in spec.single_file_segments
            ],
        }
    }


def own_record(simulation: Any, observer: int, partner: int) -> dict[str, Any]:
    """The observer's perception record of its partner right now, built as the run loop builds
    one (``perception.perceive``), for the scenario's WHERE YOU ARE lines only. Nothing is stored
    in the simulation."""
    agents = simulation.world.agents
    a = agents[observer]
    record = perceive(
        simulation.world.step_index,
        simulation.world.time,
        a,
        agents[partner],
        simulation.world.obstacles,
        simulation.visibility,
        simulation.attributes,
        a.spec.preferred_speed,
        [(entry_s, exit_s) for _, entry_s, exit_s in a.spec.single_file_stretches],
        simulation.environment_range,
        segments=simulation.spec.single_file_segments,
    )
    return record.as_dict()


def perceiver_for(
    simulation: Any,
    agent: int,
    partner: int,
    scenario: Scenario,
    settings: Optional[LLMViewSettings] = None,
    core: Optional[CoreTemplate] = None,
    **kwargs: Any,
) -> Perceiver:
    """A :class:`Perceiver` for ``agent``'s encounter with ``partner``, starting now: the shipped
    ``llm_view`` settings and ``resolve_v2`` unless others are given."""
    return Perceiver(
        agent, partner, settings or LLMViewSettings.load(), scenario, core or CoreTemplate.load(SIMULATION_CORE_TEMPLATE),
        since_s=kwargs.pop("since_s", simulation.world.time), **kwargs,
    )


def view_in(
    simulation: Any,
    perceiver: Perceiver,
    exchange: Optional[Exchange] = None,
    *,
    notes: Sequence[str] = (),
    outcomes: Sequence[str] = (),
    factor_lines: Optional[Mapping[int, Sequence[str]]] = None,
    pairwise_lines: Optional[Mapping[int, Sequence[str]]] = None,
) -> View:
    """The view of ``perceiver``'s agent at the simulation's present step: every block of D2.

    ABOUT YOU from the agent's body and its own ``people`` entry; WHERE YOU ARE (and any block of
    the scenario's own) from the scenario plug-in and the agent's own record; the rest from
    :meth:`Perceiver.look`. Reads the simulation and changes nothing in it.
    """
    agents = simulation.world.agents
    agent = agents[perceiver.agent_id]
    if agent.done:
        raise ValueError(f"agent {agent.agent_id} has arrived and left the scene")
    record = own_record(simulation, perceiver.agent_id, perceiver.partner_id)
    scene = scene_of(simulation)
    info = _person(perceiver.people, agent.agent_id)
    me = Me(
        speed_mps=agent.speed,
        preferred_speed_mps=agent.spec.preferred_speed,
        max_speed_mps=agent.spec.max_speed,
        width_m=2.0 * agent.spec.radius,
        age=info.get("age") if perceiver.show_age else None,
        gender=info.get("gender") if perceiver.show_gender else None,
        errand=info.get("errand"),
    )
    return perceiver.look(
        simulation.world.time,
        bodies_in(simulation),
        simulation.world.obstacles,
        me,
        exchange,
        place=perceiver.scenario.place_lines(scene, record),
        extra_blocks=perceiver.scenario.extra_blocks(scene, record),
        notes=notes,
        outcomes=outcomes,
        safety_distance_m=safety_distance(simulation, perceiver.agent_id, perceiver.partner_id),
        factor_lines=factor_lines,
        pairwise_lines=pairwise_lines,
        labels={
            "scenario_type": simulation.spec.scenario_type,
            "step": simulation.world.step_index,
            "partner_id": perceiver.partner_id,
        },
    )
