"""The ``View``: everything one agent is told at one decision point (``docs/resolution.md``, D2).

A view holds the description block by block, as data, in the order D2 gives:

- ``me``: ABOUT YOU (age and gender when their switches show them, the errand, the speeds, the
  body width, the person's own factor lines);
- ``notes``: YOUR NOTES (RF-5's memory note, off by default, D7);
- ``place`` and ``extra_blocks``: WHERE YOU ARE and any block of the scenario's own, already
  rendered by the scenario plug-in (D16), whose template the view records;
- ``seen``: WHO YOU CAN SEE, each person with a stable label ("Person 1") and a detail level;
- ``heard``: WHAT YOU CAN HEAR;
- ``history``: WHAT YOU HAVE DONE SO FAR, one entry per earlier decision point;
- ``time_to_meet``: the closing line.

Rendering is :mod:`negsim.resolution.prompt`'s. Nothing here holds anything the agent cannot
perceive: no other person's errand, private factors or group. A view records the core and the
scenario template it is meant for, with their SHA-256 (``templates``), and the prompt rendered
from it records them again.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional

CONDITION_INDEPENDENT = "independent"
CONDITION_NON_VERBAL = "non_verbal"
CONDITION_TALK = "talk"
CONDITIONS = (CONDITION_INDEPENDENT, CONDITION_NON_VERBAL, CONDITION_TALK)

#: The signals of D1; ``none`` is no signal.
SIGNALS = ("none", "eye_contact", "nod", "wave_on", "hold_up_hand", "point", "other")

DETAIL_FULL = "full"  # within the detail range: every line
DETAIL_SHORT = "short"  # beyond it, within the seeing range: one line
DETAILS = (DETAIL_FULL, DETAIL_SHORT)

MOTION_WALKING = "walking"
MOTION_STILL = "still"
MOTION_BACKING = "backing"
MOTIONS = (MOTION_WALKING, MOTION_STILL, MOTION_BACKING)

#: What a person did since the agent last looked (D5); RF-17 detects them.
CHANGES = (
    "slowed_down", "sped_up", "stopped", "started_walking", "backing_up",
    "moved_left", "moved_right", "turned", "came_into_view",
)

OUTCOME_COMPLETED = "completed"
OUTCOME_ONGOING = "ongoing"
OUTCOMES = (OUTCOME_COMPLETED, OUTCOME_ONGOING)


@dataclass(frozen=True)
class Me:
    """ABOUT YOU. ``age`` and ``gender`` are ``None`` when their switch hides them."""

    speed_mps: float
    preferred_speed_mps: float
    max_speed_mps: float
    width_m: float
    age: Optional[int] = None
    gender: Optional[str] = None
    errand: Optional[str] = None
    factor_lines: tuple[str, ...] = ()  # rendered by RF-5's factor template, placed verbatim


@dataclass(frozen=True)
class SeenPerson:
    """One person in view. Left and right, and every angle, are the observer's own."""

    label: int  # "Person {label}", stable for the encounter
    detail: str
    distance_m: float
    bearing_rad: float  # where they are: 0 straight ahead, positive to the observer's left
    speed_mps: float
    heading_relative_rad: float  # their direction of travel against the observer's
    closing_speed_mps: Optional[float]
    width_m: float
    motion: str = MOTION_WALKING
    age: Optional[int] = None
    gender: Optional[str] = None
    signal: str = "none"
    changes: tuple[str, ...] = ()
    factor_lines: tuple[str, ...] = ()  # what the observer can see of their factors (RF-5)
    pairwise_lines: tuple[str, ...] = ()  # for this observer only (RF-6)

    def __post_init__(self) -> None:
        if self.detail not in DETAILS:
            raise ValueError(f"detail: one of {DETAILS}, got {self.detail!r}")
        if self.motion not in MOTIONS:
            raise ValueError(f"motion: one of {MOTIONS}, got {self.motion!r}")
        if self.signal not in SIGNALS:
            raise ValueError(f"signal: one of {SIGNALS}, got {self.signal!r}")
        unknown = [change for change in self.changes if change not in CHANGES]
        if unknown:
            raise ValueError(f"changes: unknown {unknown}; known: {CHANGES}")


@dataclass(frozen=True)
class Heard:
    """Something said within hearing range. ``label`` is ``None`` for a speaker not in view."""

    message: str
    label: Optional[int] = None


@dataclass(frozen=True)
class Done:
    """One earlier decision point of this agent, for WHAT YOU HAVE DONE SO FAR."""

    ago_s: float
    intent: str
    outcome: str
    message: str = ""
    signal: str = "none"

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"outcome: one of {OUTCOMES}, got {self.outcome!r}")
        if self.signal not in SIGNALS:
            raise ValueError(f"signal: one of {SIGNALS}, got {self.signal!r}")


@dataclass(frozen=True)
class Block:
    """A block of the scenario's own, such as YOUR QUEUE: a header and its rendered lines."""

    header: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class TimeToMeet:
    label: int
    seconds: float


@dataclass(frozen=True)
class View:
    agent_id: int
    decision_point: int  # 1 for the opening one
    me: Me
    place: tuple[str, ...]
    templates: Mapping[str, Mapping[str, str]]  # {"core": {key, sha256}, "scenario": {key, sha256}}
    seen: tuple[SeenPerson, ...] = ()
    heard: tuple[Heard, ...] = ()
    history: tuple[Done, ...] = ()
    notes: tuple[str, ...] = ()
    extra_blocks: tuple[Block, ...] = ()
    time_to_meet: Optional[TimeToMeet] = None
    labels: Mapping[str, Any] = field(default_factory=dict)  # where the view came from; never rendered

    def __post_init__(self) -> None:
        if self.decision_point < 1:
            raise ValueError("decision_point counts from 1")
        if set(self.templates) != {"core", "scenario"}:
            raise ValueError("a view records its core and its scenario template")
        labels = [person.label for person in self.seen]
        if len(set(labels)) != len(labels):
            raise ValueError(f"two people in view share a label: {labels}")
        if self.time_to_meet is not None and self.time_to_meet.label not in labels:
            raise ValueError("the time to meet names a person who is not in view")

    def meeting_distance_m(self) -> Optional[float]:
        """How far away the person the agent would meet is: the person of the time-to-meet line,
        else the nearest person in view, else ``None``. ``start.at_distance_m`` is read against it."""
        if self.time_to_meet is not None:
            return next(p.distance_m for p in self.seen if p.label == self.time_to_meet.label)
        return min((p.distance_m for p in self.seen), default=None)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
