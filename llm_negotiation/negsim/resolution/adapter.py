"""The opening view of a frozen two-person case, from its perception record (issue #57).

RF-17 (#73) builds views from the running simulation. Until then, this adapter tells an agent
of a frozen case (``cases/``, issue #30) what it would perceive at the case's snapshot,
applying D2 (``docs/resolution.md``) to the agent's own perception record:

- the other person is **in view** when they are within ``VIEW_HALF_ANGLE_DEG`` of straight
  ahead and ``SEEING_RANGE_M`` away (Moussaïd, Helbing & Theraulaz 2011), in **full detail**
  within ``DETAIL_RANGE_M`` (Rio, Dachner & Warren 2018) and in one short line beyond it. With
  two people nobody can hide the other, so there is no occlusion to apply;
- an agent who sees nobody is told so. The snapshot of a case is when its pair formed, which is
  not always a decision point: in the head-on cases the two are 12.4 m apart, beyond the seeing
  range, and in the overtaking cases the one ahead has the other behind them. RF-3's trigger
  (D4) finds the real decision points;
- **the time to meet** is the time of closest approach at the current velocities,
  ``-(r . v) / |v|^2`` with ``r`` and ``v`` the other's position and velocity relative to the
  agent, stated only for a person in view who is getting closer.

Only what the agent can perceive is read: its own record and body, and its own errand. The
other person's errand, private information and group are never read. The flow cases (pairs out
of crowds of 100) are refused: the record describes only the pair, and a crowd's view is RF-17's.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError
from .prompt import CoreTemplate
from .scenario import Scenario
from .view import DETAIL_FULL, DETAIL_SHORT, MOTION_STILL, MOTION_WALKING, Me, SeenPerson, TimeToMeet, View

#: Half the view cone, in degrees: Moussaïd, Helbing & Theraulaz 2011 (phi), D12.
VIEW_HALF_ANGLE_DEG = 75.0
#: How far an agent sees people, in metres: the same source (d_max), D12.
SEEING_RANGE_M = 10.0
#: Within this distance a person is described in full: Rio, Dachner & Warren 2018, D12.
DETAIL_RANGE_M = 5.0

PERSON_KEYS = ("age", "gender", "errand")


def in_view(distance_m: float, bearing_rad: float) -> bool:
    return distance_m <= SEEING_RANGE_M and abs(math.degrees(bearing_rad)) <= VIEW_HALF_ANGLE_DEG


def time_to_meet(record: Mapping[str, Any]) -> Optional[float]:
    """Seconds to closest approach at the current velocities, or ``None`` if not getting closer."""
    velocity = record.get("relative_velocity_mps")
    if velocity is None:
        return None
    (rx, ry), (vx, vy) = record["relative_position_m"], velocity
    v2 = vx * vx + vy * vy
    if v2 <= 0.0:
        return None
    t = -(rx * vx + ry * vy) / v2
    return t if t > 0.0 else None


def _person(people: Optional[Mapping[Any, Mapping[str, Any]]], agent: int) -> Mapping[str, Any]:
    if not people:
        return {}
    person = people.get(agent, people.get(str(agent), {}))
    unknown = sorted(set(person) - set(PERSON_KEYS))
    if unknown:
        raise ConfigError(f"person {agent}: unknown key(s) {unknown}; known: {PERSON_KEYS}")
    return person


def opening_view(
    case: Mapping[str, Any],
    agent: int,
    scenario: Scenario,
    core: Optional[CoreTemplate] = None,
    people: Optional[Mapping[Any, Mapping[str, Any]]] = None,
    show_age: bool = True,
    show_gender: bool = True,
    notes: Sequence[str] = (),
) -> View:
    """The view of ``agent`` at the case's snapshot: its first decision point.

    ``people`` gives each agent's ``age``, ``gender`` and ``errand`` (optional; a missing errand
    is the case's private task). ``show_age`` and ``show_gender`` are the visibility switches:
    off, neither the agent's own nor the other's is stated.
    """
    core = core or CoreTemplate.load()
    if case["scenario"]["n_agents"] != 2:
        raise ConfigError(
            f"case {case['case_id']} has {case['scenario']['n_agents']} people; the opening view of a frozen "
            "case is built for two-person cases only (a crowd's view is RF-17's)"
        )
    others = [a for a in case["agents"] if a != agent]
    if agent not in case["agents"] or len(others) != 1:
        raise ConfigError(f"agent {agent} is not one of case {case['case_id']}'s pair {case['agents']}")
    other = others[0]
    record = case["observations"][str(agent)]
    observer, body = record["observer"], case["bodies"][str(agent)]
    me_info, them_info = _person(people, agent), _person(people, other)

    errand = me_info.get("errand")
    if errand is None:
        errand = (case.get("private", {}).get(str(agent)) or {}).get("task")
    me = Me(
        speed_mps=observer["speed_mps"],
        preferred_speed_mps=observer["preferred_speed_mps"],
        max_speed_mps=body["max_speed_mps"],
        width_m=2.0 * observer["radius_m"],
        age=me_info.get("age") if show_age else None,
        gender=me_info.get("gender") if show_gender else None,
        errand=errand,
    )

    seen: list[SeenPerson] = []
    meet = None
    if record["neighbour_speed_mps"] is not None and in_view(record["distance_m"], record["bearing_rad"]):
        speed = record["neighbour_speed_mps"]
        seen.append(
            SeenPerson(
                label=1,
                detail=DETAIL_FULL if record["distance_m"] <= DETAIL_RANGE_M else DETAIL_SHORT,
                distance_m=record["distance_m"],
                bearing_rad=record["bearing_rad"],
                speed_mps=speed,
                heading_relative_rad=record["neighbour_heading_relative_rad"],
                closing_speed_mps=record["closing_speed_mps"],
                width_m=2.0 * record["neighbour_radius_m"],
                motion=MOTION_STILL if round(speed, 2) == 0.0 else MOTION_WALKING,
                age=them_info.get("age") if show_age else None,
                gender=them_info.get("gender") if show_gender else None,
            )
        )
        t = time_to_meet(record)
        meet = None if t is None else TimeToMeet(1, t)

    return View(
        agent_id=agent,
        decision_point=1,
        me=me,
        place=tuple(scenario.place_lines(case, record)),
        templates={"core": core.identity(), "scenario": scenario.identity()},
        seen=tuple(seen),
        notes=tuple(notes),
        extra_blocks=tuple(scenario.extra_blocks(case, record)),
        time_to_meet=meet,
        labels={"case_id": case["case_id"], "case_version": case["version"], "snapshot_step": record["step"]},
    )
