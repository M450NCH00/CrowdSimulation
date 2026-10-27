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

**A person's group is never in a snapshot** (issue #32): only the fields of ``fields.py`` are,
and none of them is the group or derived from it, so no rule can read it, whatever it says.

**Version 4 (issue #108).** The three visible attributes (``mobility_aid``, ``load``,
``distraction``) are agent-level fields like age, each counted only where its visibility switch
is on. A person's **own private factors** (the ``self.`` fields) are kept apart, in ``private``:
an own-only condition reads only its own person's, and nothing else reads them. The shared
snapshot holds both people's; the one an agent builds from its own record holds only its own,
which is all its own directive depends on, so the two still give it the same directive. Equality
(:meth:`PairSnapshot.same_values`) is over the shared part, as before.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from ..avoidance.perception import SEGMENT_FIELDS, PairFeatures, PerceptionRecord, time_to_collision
from ..core.agent import AgentRuntime
from .fields import AGENT_FIELDS, PAIR_FIELDS, SELF_FIELDS, VISIBLE_FACTOR_SWITCHES, fields_of

#: The person attributes behind the ``self.`` fields; the two pairwise ones come from a run's
#: ``pairwise`` views, keyed by (observer, neighbour).
PRIVATE_ATTRIBUTES = ("assertiveness", "urgency", "residence", "memory_note")
PAIRWISE_PRIVATE = ("knows_other", "finds_other_attractive")
#: The fields that were in every snapshot before version 4: an older run's logged snapshots are
#: exactly these, and a later field is logged only when someone has a value for it.
_BEFORE_V4 = 3


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
    #: Version 4: each person's own private factors, in the same order; ``{}`` for one whose
    #: values the builder does not know (the other person, in a snapshot built from one record).
    private: tuple[Mapping[str, Any], Mapping[str, Any]] = ({}, {})

    @property
    def encounter_class(self) -> Optional[str]:
        return self.pair.get("encounter_class")

    def agent_value(self, index: int, name: str) -> Any:
        return self.agent_values[index].get(name)

    def private_value(self, index: int, name: str) -> Any:
        """A ``self.`` field of the person at ``index``: their own, which only an own-only condition reads."""
        return self.private[index].get(name)

    def same_values(self, other: "PairSnapshot") -> bool:
        """Equal in everything a rule can read (the step and time aside)."""
        return (self.agents, dict(self.pair), [dict(v) for v in self.agent_values]) == (
            other.agents, dict(other.pair), [dict(v) for v in other.agent_values]
        )

    def as_dict(self, schema_version: Optional[int] = None) -> dict[str, Any]:
        """Every field a rule may read, or, with ``schema_version``, every field a rule of
        that version may read (so that a case taken from an older record is as it was).

        Without ``schema_version``, a field version 4 added is written only when one of the two
        has a value for it, and the private part (``self``) only when it holds a value, so that the
        snapshot of a run with none of them is exactly what it was before version 4 (issue #108)."""
        if schema_version is None:
            pair_fields, agent_fields = fields_of(_BEFORE_V4)
            agent_fields = {
                **agent_fields,
                **{name: spec for name, spec in AGENT_FIELDS.items() if name not in agent_fields and any(v.get(name) is not None for v in self.agent_values)},
            }
            pair_fields = {**pair_fields, **{name: spec for name, spec in PAIR_FIELDS.items() if name not in pair_fields}}
        else:
            pair_fields, agent_fields = fields_of(schema_version)
        out = {
            "step": self.step,
            "time_s": _r(self.time_s),
            "agents": list(self.agents),
            "pair": {name: _r(self.pair.get(name)) for name in pair_fields},
            "agent": {
                str(agent_id): {name: _r(values.get(name)) for name in agent_fields}
                for agent_id, values in zip(self.agents, self.agent_values)
            },
        }
        if (schema_version is None or schema_version >= 4) and any(v is not None for values in self.private for v in values.values()):
            out["self"] = {
                str(agent_id): {name: values.get(name) for name in SELF_FIELDS}
                for agent_id, values in zip(self.agents, self.private)
            }
        return out


def _r(value: Any) -> Any:
    return round(value, 6) if isinstance(value, float) else value


def _visible_attribute(attributes: Optional[Mapping[str, Any]], name: str, visibility: Mapping[str, bool]) -> Any:
    if not visibility.get(name, False) or not attributes:
        return None
    value = attributes.get(name)
    return None if value in (None, "") else value


def private_of(
    attributes: Optional[Mapping[str, Any]], agent_id: int, other_id: int, pairwise: Optional[Mapping[tuple[int, int], Mapping[str, Any]]]
) -> dict[str, Any]:
    """One person's own private factors (version 4, issue #108): from their own attributes, and from
    their own view of the other (``pairwise[(agent_id, other_id)]``). Never visibility-gated: a person
    knows their own. Empty when the run gives none of them, which is every run before version 4."""
    out: dict[str, Any] = {}
    for name in PRIVATE_ATTRIBUTES:
        value = (attributes or {}).get(name)
        if value not in (None, ""):
            out[name] = value
    view = (pairwise or {}).get((agent_id, other_id)) or {}
    for name in PAIRWISE_PRIVATE:
        if view.get(name) is not None:
            out[name] = bool(view[name])
    return out


def snapshot_of_pair(
    step: int,
    time_s: float,
    first: AgentRuntime,
    second: AgentRuntime,
    features: PairFeatures,
    visibility: Mapping[str, bool],
    attributes: Mapping[int, Mapping[str, Any]],
    pairwise: Optional[Mapping[tuple[int, int], Mapping[str, Any]]] = None,
) -> PairSnapshot:
    """The shared snapshot of a pair, from the state of the world on this step.

    ``features`` must be the pair's :class:`PairFeatures` of this step. The two agents may
    be given in either order. ``pairwise`` holds each person's own view of the other (version 4).
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
    values, private = [], []
    for agent, other in ((a, b), (b, a)):
        persona = attributes.get(agent.agent_id)
        values.append(
            {
                "age": _visible_attribute(persona, "age", visibility),
                "gender": _visible_attribute(persona, "gender", visibility),
                "speed_mps": agent.speed if see_speed else None,
                "radius_m": agent.spec.radius if see_size else None,
                "time_to_segment_s": features.time_to_segment_of(agent.agent_id),
                **features.segment_of(agent.agent_id),
                **{name: _visible_attribute(persona, name, visibility) for name in VISIBLE_FACTOR_SWITCHES},
            }
        )
        private.append(private_of(persona, agent.agent_id, other.agent_id, pairwise))
    return PairSnapshot(step, time_s, (a.agent_id, b.agent_id), pair, (values[0], values[1]), (private[0], private[1]))


def snapshot_of_record(
    record: PerceptionRecord, visibility: Mapping[str, bool], pairwise: Optional[Mapping[tuple[int, int], Mapping[str, Any]]] = None
) -> PairSnapshot:
    """The snapshot one agent would build from its own perception record alone.

    The observer's own attributes, speed and size count only where the neighbour could see
    them (``visibility``): a rule may read only what both agents can see. The neighbour's
    are in the record only where they are visible already. Of the private part (version 4) the
    observer knows only its own: its own attributes, and its own view of the neighbour in
    ``pairwise``.
    """
    see_speed, see_size = visibility.get("speed", False), visibility.get("size", False)
    observer = record.observer
    own = {
        "age": _visible_attribute(observer.attributes, "age", visibility),
        "gender": _visible_attribute(observer.attributes, "gender", visibility),
        "speed_mps": observer.speed_mps if see_speed else None,
        "radius_m": observer.radius_m if see_size else None,
        "time_to_segment_s": observer.time_to_segment_s,
        **{name: getattr(observer, name) for name in SEGMENT_FIELDS},
        **{name: _visible_attribute(observer.attributes, name, visibility) for name in VISIBLE_FACTOR_SWITCHES},
    }
    mine = private_of(observer.attributes, record.observer_id, record.neighbour_id, pairwise)
    seen = record.neighbour_attributes
    other = {
        "age": seen.get("age"),
        "gender": seen.get("gender"),
        "speed_mps": record.neighbour_speed_mps,
        "radius_m": record.neighbour_radius_m,
        "time_to_segment_s": record.neighbour_time_to_segment_s,
        **record.neighbour_segment,
        **{name: seen.get(name) for name in VISIBLE_FACTOR_SWITCHES},
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
        return PairSnapshot(record.step, record.time_s, (record.observer_id, record.neighbour_id), pair, (own, other), (mine, {}))
    return PairSnapshot(record.step, record.time_s, (record.neighbour_id, record.observer_id), pair, (other, own), ({}, mine))
