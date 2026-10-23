"""The passing scenarios of rounds 1 to 3 (``docs/resolution.md``, D17): head-on in a corridor,
meeting in a narrow passage, and someone behind saying "excuse me". They share one description
side, ``scenario_passing_v1``: the wall, passage and narrowing lines of issue #32, and the events
``other_passes``, ``other_stops`` and ``i_am_out_of_the_stretch``.

**The execution side** (issue #59, RF-4). Each is read from the state at the start of a step:

- ``other_passes``: the partner is behind the agent (behind the direction of the agent's path where
  it is) and the distance between them is growing; or the partner has arrived. Also, for the one
  who is overtaken: the partner was behind the agent when the step began, and is now ahead of it
  with the distance growing.
- ``other_stops``: the partner's speed is below ``STOPPED_MPS`` (0.01 m/s, the deadlock
  monitor's ``speed_eps``).
- ``i_am_out_of_the_stretch``: the agent has been inside a single-file segment (its centre in the
  segment's free space, as the perception record's ``in_segment`` counts it) since the step began,
  and now is not, by either end. An agent that is never inside one never gets out of one.

**The conflict zone:**

- if both paths run through the same single-file segment, too narrow for the two to pass in, the
  zone is that segment. An agent has left it when it is beyond the far end along its own path by
  the two radii and the scenario's safety margin, as the arbiter counts it (``first_out``);
- otherwise (a corridor wide enough to pass in), the zone is a disc round the point midway
  between the two at their closest approach, of radius the two radii plus the safety margin.
  An agent has left it at the first step after the closest approach on which it is outside the
  disc.

**Resolved** means: the two left the conflict zone (cleared), with no collision, no near miss
and no deadlock, within the run's time limit.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Optional, Sequence

from ...rulegen.describe import _place
from ..scenario import EventContext, Scenario

#: Below this speed the partner has stopped (m/s): the deadlock monitor's ``speed_eps`` of every
#: passing scenario, issue #24's design value. **[design]**
STOPPED_MPS = 0.01
ZONE_SEGMENT = "single_file_segment"
ZONE_CLOSEST_APPROACH = "closest_approach"


def _inside(point: tuple[float, float], rect: Any) -> bool:
    return rect.xmin <= point[0] <= rect.xmax and rect.ymin <= point[1] <= rect.ymax


def _along(me: Any, other: Any) -> float:
    """How far ``other`` is ahead of ``me`` along the direction of ``me``'s path where it is."""
    heading = me.spec.path.heading_at(me.path_s)
    return (other.pose.x - me.pose.x) * math.cos(heading) + (other.pose.y - me.pose.y) * math.sin(heading)


def _separating(me: Any, other: Any) -> bool:
    rx, ry = other.pose.x - me.pose.x, other.pose.y - me.pose.y
    vx, vy = other.velocity[0] - me.velocity[0], other.velocity[1] - me.velocity[1]
    return rx * vx + ry * vy > 0.0


def shared_segment(simulation: Any, agents: Sequence[int]) -> Optional[tuple[int, Any]]:
    """The single-file segment both agents' paths run through that is too narrow for them to pass
    in (index, segment), or ``None``."""
    world_agents = simulation.world.agents
    a, b = (world_agents[agent].spec for agent in agents)
    diameters = 2.0 * (a.radius + b.radius)
    theirs = {index for index, _, _ in b.single_file_stretches}
    for index, _, _ in a.single_file_stretches:
        segment = simulation.spec.single_file_segments[index]
        if index in theirs and segment.width < diameters:
            return index, segment
    return None


class PassingScenario(Scenario):
    TEMPLATE = "scenario_passing_v1"
    #: The case types of rounds 1 to 3 (``negsim.scenarios``). The place lines read only walls,
    #: passage widths and narrowings, so a case of another type renders the same way.
    CASE_TYPES = ("wide_corridor_head_on", "passage_meeting", "overtaking")

    def place_lines(self, case: Mapping[str, Any], record: Mapping[str, Any]) -> list[str]:
        """``describe._place``, the lines of ``rulegen_negotiate_v2`` (issue #32), unchanged."""
        return _place(case, record, self.data["place"])

    # --- the execution side (issue #59) ---------------------------------------------------------

    def happened(self, event: str, context: EventContext) -> bool:
        me, other, memory = context.agent, context.partner, context.memory
        if event == "other_passes":
            if other.goal_time is not None:
                return True
            along = _along(me, other)
            memory.setdefault("behind_at_start", along < 0.0)
            if not _separating(me, other):
                return False
            return along < 0.0 or (memory["behind_at_start"] and along > 0.0)
        if event == "other_stops":
            return other.goal_time is None and math.hypot(*other.velocity) < STOPPED_MPS
        if event == "i_am_out_of_the_stretch":
            segments = context.simulation.spec.single_file_segments
            if any(_inside(me.pose.xy, segment.rect) for segment in segments):
                memory["was_inside"] = True
                return False
            return bool(memory.get("was_inside"))
        return super().happened(event, context)

    def zone_exits(self, simulation: Any, track: Sequence[Any], agents: Sequence[int], start_step: int) -> dict[int, Optional[float]]:
        rows = [row for row in track if row.step > start_step]
        exits: dict[int, Optional[float]] = {agent: None for agent in agents}
        if not rows:
            return exits
        specs = {agent: simulation.world.agents[agent].spec for agent in agents}
        reach = sum(spec.radius for spec in specs.values()) + simulation.spec.single_file_safety_margin
        found = shared_segment(simulation, agents)
        if found is not None:
            index = found[0]
            for agent in agents:
                exit_s = next(exit_ for i, _, exit_ in specs[agent].single_file_stretches if i == index)
                exits[agent] = next(
                    (row.time_s for row in rows if row.bodies[agent].done or row.bodies[agent].path_s >= exit_s + reach),
                    None,
                )
            return exits
        a, b = agents
        nearest = min(range(len(rows)), key=lambda k: (math.dist(rows[k].bodies[a].xy, rows[k].bodies[b].xy), k))
        pa, pb = rows[nearest].bodies[a].xy, rows[nearest].bodies[b].xy
        middle = ((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0)
        for agent in agents:
            exits[agent] = next(
                (row.time_s for row in rows[nearest:] if row.bodies[agent].done or math.dist(row.bodies[agent].xy, middle) > reach),
                None,
            )
        return exits

    def outcome_columns(self, simulation: Any, track: Sequence[Any], agents: Sequence[int], start_step: int, general: Mapping[str, Any]) -> dict[str, Any]:
        found = shared_segment(simulation, agents)
        return {"conflict_zone": ZONE_CLOSEST_APPROACH if found is None else f"{ZONE_SEGMENT}:{found[1].name}"}

    def resolved(self, columns: Mapping[str, Any]) -> bool:
        return bool(columns["cleared"]) and not (columns["collision"] or columns["near_miss"] or columns["deadlock"])
