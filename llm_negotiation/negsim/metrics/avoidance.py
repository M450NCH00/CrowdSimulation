"""Conflict metrics of the avoidance layer.

``docs/metrics.md`` defines each metric in words and gives the default thresholds; this
module is the arithmetic. The point of the set is to let a later sub-issue tell a
conflict that was *avoided* (it never arose) from one that arose and was then *resolved*:

``conflict exposure``
    An agent is exposed on a step if the velocity it wanted lies in the half-plane ORCA
    forbids it because of another agent, so that ORCA had to change it. No exposure over
    a whole interaction means the conflict never arose. (Counted in
    ``negsim.avoidance.simulation``, where the half-planes are.)
``yield event``
    An agent walking at less than a set fraction of its preferred speed for at least a
    set time. A conflict settled by somebody waiting shows up as one.
``near miss``
    Two bodies closer than a set distance.

A collision keeps the definition of issue #24: two discs overlapping. It is found here
with the same tracker as a near miss, with the distance set to zero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

Pair = tuple[int, int]


@dataclass(frozen=True)
class YieldEvent:
    agent_id: int
    start_time_s: float
    end_time_s: float
    min_speed_mps: float

    @property
    def duration_s(self) -> float:
        return self.end_time_s - self.start_time_s

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "start_time_s": round(self.start_time_s, 6),
            "end_time_s": round(self.end_time_s, 6),
            "duration_s": round(self.duration_s, 6),
            "min_speed_mps": round(self.min_speed_mps, 6),
        }


class YieldTracker:
    """Finds the yield events of one agent.

    A yield event is a run of consecutive time steps on each of which the agent's speed
    was below ``fraction`` times its preferred speed, lasting at least ``min_duration``
    seconds. The preferred speed is the agent's own, before any directive scales it: an
    agent told to slow down by a directive is yielding.
    """

    def __init__(self, agent_id: int, preferred_speed: float, fraction: float, min_duration: float):
        self.agent_id = agent_id
        self.threshold = fraction * preferred_speed
        self.min_duration = min_duration
        self.events: list[YieldEvent] = []
        self._start: Optional[float] = None
        self._end = 0.0
        self._min_speed = math.inf

    def update(self, step_start: float, step_end: float, speed: float) -> None:
        """Feed the speed the agent moved at during one step."""
        if speed < self.threshold:
            if self._start is None:
                self._start, self._min_speed = step_start, speed
            self._end = step_end
            self._min_speed = min(self._min_speed, speed)
        else:
            self.close()

    def close(self) -> None:
        """End the current run, if any; call when the agent arrives or the run ends."""
        if self._start is not None and self._end - self._start >= self.min_duration - 1e-9:
            self.events.append(YieldEvent(self.agent_id, self._start, self._end, self._min_speed))
        self._start = None

    @property
    def total_time_s(self) -> float:
        return sum(event.duration_s for event in self.events)


@dataclass(frozen=True)
class ArtefactThresholds:
    """When the two ORCA artefacts issue #26 found are counted (``docs/metrics.md``, section 10).

    Diagnostics, not conflict metrics: they count where the vehicle, not a rule, may be
    what differs from people. Each is a definition with no source.
    """

    #: Walking backwards: moving against the direction of one's own path faster than this.
    backward_speed_mps: float = 0.1
    #: Hurried along: moving faster than (1 + this) times the speed one wants, with a
    #: perceived neighbour behind.
    hurried_fraction: float = 0.05
    #: Either counts only if it lasts at least this long.
    min_duration_s: float = 1.0

    def as_dict(self) -> dict[str, float]:
        return {
            "backward_speed_mps": self.backward_speed_mps,
            "hurried_fraction": self.hurried_fraction,
            "min_duration_s": self.min_duration_s,
        }


class EpisodeTracker:
    """Runs of consecutive time steps on which a condition held, lasting at least ``min_duration``."""

    def __init__(self, min_duration: float):
        self.min_duration = min_duration
        self.episodes: list[tuple[float, float]] = []
        self._start: Optional[float] = None
        self._end = 0.0

    def update(self, step_start: float, step_end: float, holding: bool) -> None:
        if holding:
            if self._start is None:
                self._start = step_start
            self._end = step_end
        else:
            self.close()

    def close(self) -> None:
        if self._start is not None and self._end - self._start >= self.min_duration - 1e-9:
            self.episodes.append((self._start, self._end))
        self._start = None

    @property
    def total_time_s(self) -> float:
        return sum(end - start for start, end in self.episodes)


@dataclass
class ProximityEpisode:
    """A stretch of time during which two bodies were closer than a threshold."""

    pair: Pair
    start_time_s: float
    end_time_s: float
    min_separation_m: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "pair": list(self.pair),
            "start_time_s": round(self.start_time_s, 6),
            "end_time_s": round(self.end_time_s, 6),
            "min_separation_m": round(self.min_separation_m, 6),
        }


@dataclass
class ProximityTracker:
    """Finds the episodes during which two bodies were closer than ``distance``.

    The separation of a pair is the distance between the surfaces of the two discs; it is
    negative when they overlap. An episode begins on the first time step at whose end the
    separation is below ``distance`` and ends on the first at whose end it is not; a pair
    that comes close twice has two episodes.

    With ``distance`` set to the near-miss threshold the episodes are near misses. With
    it set to zero they are collisions, and the depth of the worst overlap is minus the
    episode's smallest separation.
    """

    distance: float
    events: list[ProximityEpisode] = field(default_factory=list)
    _open: dict[Pair, ProximityEpisode] = field(default_factory=dict)

    def update(self, time_s: float, separations: dict[Pair, float]) -> None:
        """Feed the separation of every pair that is closer than ``distance`` at ``time_s``."""
        for pair, separation in separations.items():
            current = self._open.get(pair)
            if current is None:
                self._open[pair] = ProximityEpisode(pair, time_s, time_s, separation)
            else:
                current.end_time_s = time_s
                current.min_separation_m = min(current.min_separation_m, separation)
        for pair in [pair for pair in self._open if pair not in separations]:
            self.events.append(self._open.pop(pair))

    def close(self) -> None:
        for pair in sorted(self._open):
            self.events.append(self._open.pop(pair))

    @property
    def count(self) -> int:
        """Episodes so far, counting those still going on."""
        return len(self.events) + len(self._open)

    def count_for(self, agent_id: int) -> int:
        return sum(1 for event in self.events if agent_id in event.pair)
