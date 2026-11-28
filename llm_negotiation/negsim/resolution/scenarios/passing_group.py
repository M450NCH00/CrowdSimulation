"""Passing in a small group: head-on in round 1's corridor with three or four people (issue #110,
RF-32; ``docs/resolution.md``, D11, as amended for this issue).

The events, conflict zone, conflict prediction and "resolved" of
:class:`~negsim.resolution.scenarios.passing.PassingScenario`; the description side of
``scenario_passing_group_v1`` (``scenario_passing_v1``'s place lines and events word for word, and
a block of its own). What differs (D16, the encounter side):

- **who can start the encounter** (:meth:`trigger_pairs`): any two people walking opposite ways,
  the case's two first. The case's pair is one pair of a group, and in 2 v 2 it may start on
  diagonal lines that only later converge; any oncoming person someone perceives in conflict can
  start it;
- **who is in it** (:meth:`encounter_members`): everyone in the case who has not arrived, nearest
  first (the smaller of the two distances, ties by agent id); the protocol's cap applies;
- **which pairs count** (:meth:`conflict_pairs`): every pair walking opposite ways, whether or not a
  conflict between them is predicted at the start (in 2 v 2 the diagonal pairs start 0.63 m apart,
  outside the conflict reach, and can still be walked into). Two people of one group are not a
  conflict pair; a collision between them still fails each conflict pair of theirs, since
  ``physical_outcome`` counts a collision with anyone;
- **WHO YOU ARE WITH** (:meth:`extra_blocks`): a person walking side by side with someone is told
  they are out with a friend, and on which side, from the case's layout (someone abreast is at
  90 degrees, outside the view cone of D12, so would not otherwise be known). A person walking
  alone has no such block.

**[assumptions, ``WORK_LOG-110.md``]**: that people of one group are friends and know it; that
nobody is told the people coming the other way are together; who can start and who joins.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from ...configutil import ConfigError
from ...rulegen.describe import fill
from ..view import Block
from .passing import PassingScenario

EASTBOUND, WESTBOUND = "eastbound", "westbound"


def groups_of(geometry: Mapping[str, Any]) -> dict[int, tuple[str, float]]:
    """Each agent's group and line of travel (y) in a ``group_head_on`` layout: the eastbound people
    first, in the order listed, then the westbound ones."""
    out: dict[int, tuple[str, float]] = {}
    for side in (EASTBOUND, WESTBOUND):
        for y in geometry[side]:
            out[len(out)] = (side, float(y))
    return out


def companion_side(geometry: Mapping[str, Any], agent: int) -> str | None:
    """``left`` or ``right``: where ``agent``'s companion walks, in its own frame, at the start; ``None``
    for someone walking alone. An eastbound person's left is ``+y``, a westbound person's ``-y``."""
    groups = groups_of(geometry)
    side, mine = groups[agent]
    others = [y for other, (group, y) in groups.items() if group == side and other != agent]
    if not others:
        return None
    if len(others) > 1:
        raise ConfigError(f"agent {agent} walks with {len(others)} others; WHO YOU ARE WITH is worded for one companion")
    above = others[0] > mine
    return ("left" if above else "right") if side == EASTBOUND else ("right" if above else "left")


class PassingGroupScenario(PassingScenario):
    TEMPLATE = "scenario_passing_group_v1"
    CASE_TYPES = ("group_head_on",)
    MAX_MEMBERS = None

    def extra_blocks(self, case: Mapping[str, Any], record: Mapping[str, Any]) -> list[Block]:
        side = companion_side(case["scenario"]["geometry"], int(record["observer_id"]))
        if side is None:
            return []
        block = self.data["extra_blocks"]["companion"]
        return [Block(block["header"], (fill(block["line"], side=side),))]

    def trigger_pairs(self, simulation: Any, pair: Sequence[int]) -> list[tuple[int, int]]:
        agents = simulation.world.agents
        first = super().trigger_pairs(simulation, pair)
        rest = [
            (i, j) for i in range(len(agents)) for j in range(len(agents))
            if agents[i].spec.group != agents[j].spec.group and (i, j) not in first
        ]
        return first + rest

    def encounter_members(self, simulation: Any, i: int, j: int) -> list[int]:
        agents = simulation.world.agents
        pair = (agents[i], agents[j])
        joining = sorted(
            (min(math.dist(other.pose.xy, member.pose.xy) for member in pair), other.agent_id)
            for other in agents if other.agent_id not in (i, j) and not other.done
        )
        return [i, j, *(k for _, k in joining)]

    def conflict_pairs(self, simulation: Any, members: Sequence[int], observer: int, other: int) -> list[tuple[int, int]]:
        agents = simulation.world.agents
        return [(observer, other)] + [
            (p, q) for k, p in enumerate(members) for q in members[k + 1:]
            if {p, q} != {observer, other} and agents[p].spec.group != agents[q].spec.group
        ]
