"""Passing in a crowd: the passing scenario in a bidirectional flow (issue #58, RF-3).

The same description side, events, conflict zone and conflict prediction as
:class:`~negsim.resolution.scenarios.passing.PassingScenario` (``scenario_passing_v1``). Only
who is in the encounter differs (D11, D16): the two people who started it, and then everyone
else who is still walking, within the seeing range of either of them (D12: 10 m), and predicted
to be in conflict with either of them; nearest first (the smaller of the two distances, ties by
agent id). The protocol prompts at most its cap of them.

It exists so that the protocol's handling of more than two prompted people can be rehearsed on
the crowd cases (``flow_*``), ahead of the scenarios that need it (train boarding, the queue:
RF-23, RF-25). **[assumption, ``WORK_LOG-58.md``]**: who joins is not sourced.
"""

from __future__ import annotations

import math
from typing import Any

from ..adapter import SEEING_RANGE_M
from .passing import PassingScenario


class PassingCrowdScenario(PassingScenario):
    CASE_TYPES = ("bidirectional_flow",)

    def encounter_members(self, simulation: Any, i: int, j: int) -> list[int]:
        agents = simulation.world.agents
        pair = (agents[i], agents[j])
        joining = []
        for other in agents:
            k = other.agent_id
            if k in (i, j) or other.done:
                continue
            distance = min(math.dist(other.pose.xy, member.pose.xy) for member in pair)
            if distance <= SEEING_RANGE_M and (self.conflict_predicted(simulation, k, i) or self.conflict_predicted(simulation, k, j)):
                joining.append((distance, k))
        return [i, j, *(k for _, k in sorted(joining))]
