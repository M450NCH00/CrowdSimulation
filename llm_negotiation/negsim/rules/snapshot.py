"""The values a rule is evaluated on: one pair of agents, at one step.

There are two ways to build one, and the point of the module is that they agree:

* :func:`snapshot_of_pair`, from the state of the world: the **shared snapshot** that the
  run loop evaluates the rules on, once per pair (``docs/rule-matching.md``);
* :func:`snapshot_of_record`, from **one agent's perception record alone**: what that agent
  would evaluate if it applied the rules by itself.

For two agents that perceive each other on the same step, the shared snapshot and the
snapshot each builds from its own record are equal, value for value. That rests on three
things: a rule reads only fields both agents compute identically (``fields.py``); the
pair-level fields are computed once, with the lower-numbered agent first, and shared
(``perception.py``); and an agent's own attributes count only if the other agent can see
them, under the run's visibility settings, which are the same for both. The property test
checks the equality on random pairs (``tests/test_rules_matching.py``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from ..avoidance.perception import PairFeatures, PerceptionRecord, time_to_collision
from ..core.agent import AgentRuntime
from .fields import AGENT_FIELDS, PAIR_FIELDS


@dataclass(frozen=True)
class PairSnapshot:
    """What one evaluation of the rules reads, for one pair at one step.

    ``agents`` is the pair with the lower-numbered agent first, and ``agent_values`` is in
    the same order. ``pair`` holds the pair-level fields and ``agent_values`` the
    agent-level ones, by the names of ``fields.py`` without their prefix. A value that is
    hidden or does not exist is ``None``.
    """

    step: int
    time_s: float
    agents: tuple[int, int]
    pair: Mapping[str, Any]
    agent_values: tuple[Mapping[str, Any], Mapping[str, Any]]

    @property
    def encounter_class(self) -> Optional[str]:
        return self.pair.get("encounter_class")

    def agent_value(self, index: int, name: str) -> Any:
        return self.agent_values[index].get(name)

    def same_values(self, other: "PairSnapshot") -> bool:
        """Equal in everything a rule can read (the step and time aside)."""
        return (self.agents, dict(self.pair), [dict(v) for v in self.agent_values]) == (
            other.agents, dict(other.pair), [dict(v) for v in other.agent_values]
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "time_s": _r(self.time_s),
            "agents": list(self.agents),
            "pair": {name: _r(self.pair.get(name)) for name in PAIR_FIELDS},
            "agent": {
                str(agent_id): {name: _r(values.get(name)) for name in AGENT_FIELDS}
                for agent_id, values in zip(self.agents, self.agent_values)
            },
        }


def _r(value: Any) -> Any:
    return round(value, 6) if isinstance(value, float) else value


def _visible_attribute(attributes: Optional[Mapping[str, Any]], name: str, visibility: Mapping[str, bool]) -> Any:
    if not visibility.get(name, False) or not attributes:
        return None
    value = attributes.get(name)
    return None if value in (None, "") else value


def snapshot_of_pair(
    step: int,
    time_s: float,
    first: AgentRuntime,
    second: AgentRuntime,
    features: PairFeatures,
    visibility: Mapping[str, bool],
    attributes: Mapping[int, Mapping[str, Any]],
) -> PairSnapshot:
    """The shared snapshot of a pair, from the state of the world on this step.

    ``features`` must be the pair's :class:`PairFeatures` of this step. The two agents may
    be given in either order.
    """
    a, b = (first, second) if first.agent_id < second.agent_id else (second, first)
    see_speed, see_size = visibility.get("speed", False), visibility.get("size", False)
    px, py = b.pose.x - a.pose.x, b.pose.y - a.pose.y
    distance = math.hypot(px, py)
    closing = ttc = None
    if see_speed:
        wx, wy = b.velocity[0] - a.velocity[0], b.velocity[1] - a.velocity[1]
        closing = -(px * wx + py * wy) / distance if distance > 0.0 else 0.0
        if see_size:
            ttc = time_to_collision((px, py), (wx, wy), a.spec.radius + b.spec.radius)
    pair = {
        "encounter_class": features.encounter_class,
        "distance_m": distance,
        "closing_speed_mps": closing,
        "time_to_collision_s": ttc,
        "heading_difference_rad": features.heading_difference_rad,
        "min_corridor_width_m": features.min_corridor_width_m,
        "age_difference_years": features.age_difference_years,
    }
    values = []
    for agent in (a, b):
        persona = attributes.get(agent.agent_id)
        values.append(
            {
                "age": _visible_attribute(persona, "age", visibility),
                "gender": _visible_attribute(persona, "gender", visibility),
                "speed_mps": agent.speed if see_speed else None,
                "radius_m": agent.spec.radius if see_size else None,
                "time_to_segment_s": features.time_to_segment_of(agent.agent_id),
            }
        )
    return PairSnapshot(step, time_s, (a.agent_id, b.agent_id), pair, (values[0], values[1]))


def snapshot_of_record(record: PerceptionRecord, visibility: Mapping[str, bool]) -> PairSnapshot:
    """The snapshot one agent would build from its own perception record alone.

    The observer's own attributes, speed and size count only where the neighbour could see
    them (``visibility``): a rule may read only what both agents can see. The neighbour's
    are in the record only where they are visible already.
    """
    see_speed, see_size = visibility.get("speed", False), visibility.get("size", False)
    observer = record.observer
    own = {
        "age": _visible_attribute(observer.attributes, "age", visibility),
        "gender": _visible_attribute(observer.attributes, "gender", visibility),
        "speed_mps": observer.speed_mps if see_speed else None,
        "radius_m": observer.radius_m if see_size else None,
        "time_to_segment_s": observer.time_to_segment_s,
    }
    seen = record.neighbour_attributes
    other = {
        "age": seen.get("age"),
        "gender": seen.get("gender"),
        "speed_mps": record.neighbour_speed_mps,
        "radius_m": record.neighbour_radius_m,
        "time_to_segment_s": record.neighbour_time_to_segment_s,
    }
    pair = {
        "encounter_class": record.pair.encounter_class,
        "distance_m": record.distance_m,
        "closing_speed_mps": record.closing_speed_mps,
        "time_to_collision_s": record.time_to_collision_s,
        "heading_difference_rad": record.pair.heading_difference_rad,
        "min_corridor_width_m": record.pair.min_corridor_width_m,
        "age_difference_years": record.pair.age_difference_years,
    }
    if record.observer_id < record.neighbour_id:
        return PairSnapshot(record.step, record.time_s, (record.observer_id, record.neighbour_id), pair, (own, other))
    return PairSnapshot(record.step, record.time_s, (record.neighbour_id, record.observer_id), pair, (other, own))
