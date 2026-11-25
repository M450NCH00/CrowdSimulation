"""Metric computations.

The metrics are GameChat's (arXiv:2503.12333v1, Sec V): "the number of collisions and
deadlocks ... the percent of scenarios where the higher-priority agent got to Q first and
the average time to goal for the higher priority agent ... the makespan ... the slower
agent's minimum velocity prior to reaching Q ... and the average deviation from the
desired straight-line paths." Where this project measures one differently from the
GameChat repository, the docstring says how; ``docs/gamechat-notes.md`` has the full list.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from ..core.geometry import Polyline, Vec


@dataclass(frozen=True)
class Sample:
    """One agent on one step: where it was and how fast it was told to go."""

    time: float
    agent_id: int
    position: Vec
    speed: float


def makespan(goal_times: Mapping[int, Optional[float]]) -> Optional[float]:
    """Time at which the last agent reached its goal; ``None`` unless all of them did."""
    if not goal_times or any(time is None for time in goal_times.values()):
        return None
    return max(goal_times.values())


def first_through(entry_times: Mapping[int, float]) -> Optional[int]:
    """The agent that reached the conflict region first; ``None`` if none did or it is a tie."""
    if not entry_times:
        return None
    earliest = min(entry_times.values())
    first = [agent_id for agent_id, time in entry_times.items() if time == earliest]
    return first[0] if len(first) == 1 else None


def min_speed_before(
    samples: Sequence[Sample], agent_id: int, before_time: Optional[float]
) -> Optional[float]:
    """Lowest commanded speed of ``agent_id`` on the steps that began before ``before_time``.

    With ``before_time = None`` (the agent never reached the region) every step counts.
    """
    speeds = [
        sample.speed
        for sample in samples
        if sample.agent_id == agent_id and (before_time is None or sample.time < before_time)
    ]
    return min(speeds) if speeds else None


def path_deviation(samples: Sequence[Sample], paths: Mapping[int, Polyline]) -> dict[str, Optional[float]]:
    """Mean distance of the recorded positions from each agent's desired path.

    ``mean`` pools the samples of all agents, which is what the GameChat repository
    reports (``main.py:183-200``). For a straight desired path the two definitions agree;
    this one also works when the desired path has bends, as in the hallway.
    """
    per_agent: dict[int, list[float]] = {agent_id: [] for agent_id in paths}
    for sample in samples:
        per_agent[sample.agent_id].append(paths[sample.agent_id].distance_to(sample.position))
    pooled = [value for values in per_agent.values() for value in values]
    result: dict[str, Optional[float]] = {
        "mean": sum(pooled) / len(pooled) if pooled else None
    }
    for agent_id, values in per_agent.items():
        result[str(agent_id)] = sum(values) / len(values) if values else None
    return result


class DeadlockMonitor:
    """Flags a deadlock when nobody has moved for ``window_s`` seconds.

    The paper defines a deadlock as "situations where no robot can move toward its goal
    for a few seconds" (Sec I). The GameChat repository declares one the first time both
    commanded speeds are below 0.01 m/s on a single step (``main.py:210``). This monitor
    follows the paper: every agent that has not finished must stay below ``speed_eps`` for
    the whole window. A follower that is crawling toward the region is not deadlocked.
    """

    def __init__(self, window_s: float, speed_eps: float):
        self.window_s = window_s
        self.speed_eps = speed_eps
        self._stalled_since: Optional[float] = None

    def update(self, step_start_time: float, step_end_time: float, speeds: Sequence[float]) -> bool:
        """Feed the speeds commanded on one step; returns ``True`` once a deadlock is established."""
        if not speeds or any(speed > self.speed_eps for speed in speeds):
            self._stalled_since = None
            return False
        if self._stalled_since is None:
            self._stalled_since = step_start_time
        return step_end_time - self._stalled_since >= self.window_s - 1e-9


def priority_ground_truth(
    task_types: Mapping[int, Optional[str]], priority_order: Sequence[str]
) -> Optional[int]:
    """The agent whose task type ranks higher, or ``None`` if that is not defined.

    ``priority_order`` lists task types from highest priority to lowest. There is no
    ground truth if a type is missing, unknown, or the same for both agents.
    """
    ranks = {}
    for agent_id, task_type in task_types.items():
        if task_type not in priority_order:
            return None
        ranks[agent_id] = priority_order.index(task_type)
    if len(set(ranks.values())) != len(ranks):
        return None
    return min(ranks, key=ranks.get)
