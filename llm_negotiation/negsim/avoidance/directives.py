"""Avoidance directives: what a rule will be able to prescribe, and where they come from.

An :class:`AvoidanceDirective` is one agent's instruction for dealing with one neighbour.
It is obtained from a :class:`DirectiveProvider` at the moment the neighbour enters the
agent's sensing radius, and it holds for as long as the neighbour stays inside it.

Two agents that perceive each other each hold a directive about the other. ORCA's
guarantee depends on the two acting consistently, so the pair's directives are combined by
:func:`resolve_pair` before they reach the ORCA half-planes. Where the two contradict each
other in a way that would break the guarantee, a :class:`ReciprocityViolation` is recorded
and a fixed, documented policy decides what is used instead. Nothing fails silently.
``docs/derivations.md``, sections 9 to 11, has the reasoning.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Any, ClassVar, Mapping, Optional

from ..configutil import ConfigError, as_choice, as_number, check_keys
from .perception import PerceptionRecord

SIDE_LEFT, SIDE_RIGHT, SIDE_NONE = "left", "right", "none"
SIDE_PREFERENCES = (SIDE_LEFT, SIDE_RIGHT, SIDE_NONE)
ORDER_LEADER, ORDER_FOLLOWER, ORDER_NONE = "leader", "follower", "none"
PASSAGE_ORDERS = (ORDER_LEADER, ORDER_FOLLOWER, ORDER_NONE)

#: What standard ORCA does: each agent takes half.
STANDARD_SHARE = 0.5
#: Shares whose sum is short of 1 by no more than this are not a violation.
SHARE_SUM_TOLERANCE = 1e-9

# How a pair of shares that sum to less than 1 is repaired.
POLICY_PROPORTIONAL = "proportional"  # scale both up, keeping their ratio, until they sum to 1
POLICY_EQUAL_SPLIT = "equal_split"  # give each half of what is missing
SHARE_POLICIES = (POLICY_PROPORTIONAL, POLICY_EQUAL_SPLIT)

FIELD_SHARE = "responsibility_share"
FIELD_SIDE = "side_preference"
FIELD_ORDER = "passage_order"


@dataclass(frozen=True)
class AvoidanceDirective:
    """One agent's instruction for one neighbour. The defaults are plain ORCA.

    ``side_preference``
        ``left`` or ``right``: when the two are on a collision course, pass the neighbour
        on that side, as seen by this agent looking at the neighbour. ``none``: take
        whichever side is nearer.
    ``responsibility_share``
        Fraction, in [0, 1], of the change in relative velocity needed to avoid the
        neighbour that this agent makes. Standard ORCA is 0.5.
    ``speed_scale``
        Multiplier on the agent's preferred speed while the neighbour is perceived.
    ``clearance_margin``
        Extra space, in metres, kept between this agent's body and the neighbour's.
    ``passage_order``
        ``leader``: this agent goes first through a single-file segment the two both have
        to use; ``follower``: the neighbour does; ``none``: no instruction.
    """

    side_preference: str = SIDE_NONE
    responsibility_share: float = STANDARD_SHARE
    speed_scale: float = 1.0
    clearance_margin: float = 0.0
    passage_order: str = ORDER_NONE

    def __post_init__(self) -> None:
        if self.side_preference not in SIDE_PREFERENCES:
            raise ValueError(f"side_preference must be one of {SIDE_PREFERENCES}, got {self.side_preference!r}")
        if self.passage_order not in PASSAGE_ORDERS:
            raise ValueError(f"passage_order must be one of {PASSAGE_ORDERS}, got {self.passage_order!r}")
        if not 0.0 <= self.responsibility_share <= 1.0:
            raise ValueError(f"responsibility_share must be in [0, 1], got {self.responsibility_share!r}")
        if self.speed_scale < 0.0:
            raise ValueError(f"speed_scale must not be negative, got {self.speed_scale!r}")
        if self.clearance_margin < 0.0:
            raise ValueError(f"clearance_margin must not be negative, got {self.clearance_margin!r}")

    @classmethod
    def from_mapping(cls, raw: Any, where: str = "directive", base: Optional["AvoidanceDirective"] = None) -> "AvoidanceDirective":
        """A directive from a config mapping; fields left out are taken from ``base``."""
        check_keys(raw, where, (), DIRECTIVE_FIELDS)
        values = dict((base or cls()).as_dict())
        if "side_preference" in raw:
            values["side_preference"] = as_choice(raw["side_preference"], f"{where}.side_preference", SIDE_PREFERENCES)
        if "passage_order" in raw:
            values["passage_order"] = as_choice(raw["passage_order"], f"{where}.passage_order", PASSAGE_ORDERS)
        for name in ("responsibility_share", "speed_scale", "clearance_margin"):
            if name in raw:
                values[name] = as_number(raw[name], f"{where}.{name}", minimum=0.0)
        try:
            return cls(**values)
        except ValueError as exc:
            raise ConfigError(f"{where}: {exc}") from exc

    def as_dict(self) -> dict[str, Any]:
        return {
            "side_preference": self.side_preference,
            "responsibility_share": self.responsibility_share,
            "speed_scale": self.speed_scale,
            "clearance_margin": self.clearance_margin,
            "passage_order": self.passage_order,
        }


#: The exact field names, in order. The next sub-issue's rule format depends on them.
DIRECTIVE_FIELDS = tuple(field.name for field in fields(AvoidanceDirective))
PLAIN_ORCA = AvoidanceDirective()


# --- combining the two directives of a pair --------------------------------------------------


@dataclass(frozen=True)
class ReciprocityViolation:
    """Two directives of one pair that cannot both be honoured, and what was done about it."""

    field: str
    agents: tuple[int, int]
    given: tuple[Any, Any]
    resolved: tuple[Any, Any]
    policy: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "agents": list(self.agents),
            "given": list(self.given),
            "resolved": list(self.resolved),
            "policy": self.policy,
        }


@dataclass(frozen=True)
class PairResolution:
    """What a pair of agents that perceive each other actually uses.

    ``shares`` and ``agents`` are in the same order. ``side`` is the side both pass on,
    or ``None`` for the nearer side. ``leader`` is the agent that goes first through a
    shared single-file segment, or ``None`` if the directives do not say.
    """

    agents: tuple[int, int]
    shares: tuple[float, float]
    side: Optional[str]
    clearance_margin: float
    leader: Optional[int]
    violations: tuple[ReciprocityViolation, ...] = ()

    def share_of(self, agent_id: int) -> float:
        return self.shares[self.agents.index(agent_id)]

    def as_dict(self) -> dict[str, Any]:
        return {
            "agents": list(self.agents),
            "shares": list(self.shares),
            "side": SIDE_NONE if self.side is None else self.side,
            "clearance_margin": self.clearance_margin,
            "leader": self.leader,
        }


def resolve_shares(a: float, b: float, policy: str = POLICY_PROPORTIONAL) -> tuple[float, float]:
    """Two shares that sum to at least 1, as close to the ones given as the policy allows.

    A pair that already sums to 1 or more is returned unchanged: taking more than one's
    share is safe. Otherwise ``proportional`` scales both by ``1 / (a + b)``, which keeps
    their ratio; if both are zero there is no ratio to keep and each gets one half.
    ``equal_split`` adds half of what is missing to each.
    """
    if policy not in SHARE_POLICIES:
        raise ValueError(f"unknown share policy {policy!r}; expected one of {SHARE_POLICIES}")
    total = a + b
    if total >= 1.0 - SHARE_SUM_TOLERANCE:
        return a, b
    if policy == POLICY_EQUAL_SPLIT:
        missing = 1.0 - total
        return a + missing / 2.0, b + missing / 2.0
    if total == 0.0:
        return STANDARD_SHARE, STANDARD_SHARE
    return a / total, b / total


def resolve_pair(
    agent_a: int,
    directive_a: AvoidanceDirective,
    agent_b: int,
    directive_b: AvoidanceDirective,
    share_policy: str = POLICY_PROPORTIONAL,
) -> PairResolution:
    """Combine the two directives of a pair that perceive each other.

    * **Shares** must sum to at least 1 (``docs/derivations.md``, section 9). A pair that
      falls short is a violation, repaired by ``share_policy``.
    * **Side.** Both must pass on the same side. If only one states a side, both use it.
      If the two state different sides, that is a violation and neither is used.
    * **Clearance.** The larger of the two margins is used by both, so that each agent
      gets at least the space it asked for and the two half-planes stay reciprocal.
    * **Passage order.** ``leader`` with ``follower`` or ``none``, and ``none`` with
      ``follower``, name a leader. Two leaders or two followers are a violation and no
      leader is named, which leaves the decision to the arbiter's own rule.
    """
    pair = (agent_a, agent_b)
    violations = []

    given = (directive_a.responsibility_share, directive_b.responsibility_share)
    shares = resolve_shares(*given, policy=share_policy)
    if shares != given:
        violations.append(ReciprocityViolation(FIELD_SHARE, pair, given, shares, share_policy))

    sides = (directive_a.side_preference, directive_b.side_preference)
    stated = {side for side in sides if side != SIDE_NONE}
    if len(stated) == 2:
        side = None
        violations.append(ReciprocityViolation(FIELD_SIDE, pair, sides, (SIDE_NONE, SIDE_NONE), "ignore_both"))
    else:
        side = next(iter(stated), None)

    orders = (directive_a.passage_order, directive_b.passage_order)
    leader: Optional[int] = None
    if orders[0] != ORDER_NONE and orders[0] == orders[1]:
        violations.append(ReciprocityViolation(FIELD_ORDER, pair, orders, (ORDER_NONE, ORDER_NONE), "ignore_both"))
    elif orders[0] == ORDER_LEADER or orders[1] == ORDER_FOLLOWER:
        leader = agent_a
    elif orders[1] == ORDER_LEADER or orders[0] == ORDER_FOLLOWER:
        leader = agent_b

    return PairResolution(
        agents=pair,
        shares=shares,
        side=side,
        clearance_margin=max(directive_a.clearance_margin, directive_b.clearance_margin),
        leader=leader,
        violations=tuple(violations),
    )


# --- where directives come from ---------------------------------------------------------------


class DirectiveProvider(ABC):
    """Supplies a directive when a neighbour enters an agent's sensing radius.

    Later sub-issues add a rule-database provider and a negotiation provider behind this
    same interface.
    """

    name: ClassVar[str]

    @abstractmethod
    def directive(self, record: PerceptionRecord) -> AvoidanceDirective:
        """The directive ``record.observer_id`` holds toward ``record.neighbour_id``."""

    def describe(self) -> dict[str, Any]:
        """What a run records about its provider."""
        return {"provider": self.name}


class NullProvider(DirectiveProvider):
    """Plain ORCA: every directive is the default one."""

    name = "null"

    def directive(self, record: PerceptionRecord) -> AvoidanceDirective:
        return PLAIN_ORCA


class StaticProvider(DirectiveProvider):
    """Directives fixed in a config: a default, per-agent overrides, per-pair overrides.

    The most specific entry wins: a pair entry for (observer, neighbour), else the
    observer's agent entry, else the default. Each entry may set any subset of the fields;
    the rest fall through to the next less specific entry.
    """

    name = "static"

    def __init__(
        self,
        default: Optional[AvoidanceDirective] = None,
        agents: Optional[Mapping[int, AvoidanceDirective]] = None,
        pairs: Optional[Mapping[tuple[int, int], AvoidanceDirective]] = None,
    ):
        self.default = default or PLAIN_ORCA
        self.agents = dict(agents or {})
        self.pairs = dict(pairs or {})

    @classmethod
    def from_config(cls, raw: Any, where: str = "directives") -> "StaticProvider":
        check_keys(raw, where, (), ("provider", "default", "agents", "pairs"))
        default = AvoidanceDirective.from_mapping(raw.get("default") or {}, f"{where}.default")
        agents = {}
        for key, entry in (raw.get("agents") or {}).items():
            agent_id = _agent_id(key, f"{where}.agents")
            agents[agent_id] = AvoidanceDirective.from_mapping(entry or {}, f"{where}.agents.{key}", base=default)
        pairs = {}
        for index, entry in enumerate(raw.get("pairs") or []):
            label = f"{where}.pairs[{index}]"
            check_keys(entry, label, ("observer", "neighbour"), DIRECTIVE_FIELDS)
            observer = _agent_id(entry["observer"], f"{label}.observer")
            neighbour = _agent_id(entry["neighbour"], f"{label}.neighbour")
            if observer == neighbour:
                raise ConfigError(f"{label}: observer and neighbour are the same agent")
            if (observer, neighbour) in pairs:
                raise ConfigError(f"{label}: the pair ({observer}, {neighbour}) is listed twice")
            settings = {key: value for key, value in entry.items() if key in DIRECTIVE_FIELDS}
            pairs[(observer, neighbour)] = AvoidanceDirective.from_mapping(
                settings, label, base=agents.get(observer, default)
            )
        return cls(default, agents, pairs)

    def directive(self, record: PerceptionRecord) -> AvoidanceDirective:
        pair = (record.observer_id, record.neighbour_id)
        if pair in self.pairs:
            return self.pairs[pair]
        return self.agents.get(record.observer_id, self.default)

    def describe(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "default": self.default.as_dict(),
            "agents": {str(agent_id): directive.as_dict() for agent_id, directive in sorted(self.agents.items())},
            "pairs": [
                {"observer": observer, "neighbour": neighbour, **directive.as_dict()}
                for (observer, neighbour), directive in sorted(self.pairs.items())
            ],
        }


PROVIDERS = (NullProvider.name, StaticProvider.name)


def make_provider(raw: Any, where: str = "directives") -> DirectiveProvider:
    """A provider from the ``directives`` block of an experiment config."""
    if raw is None:
        return NullProvider()
    check_keys(raw, where, (), ("provider", "default", "agents", "pairs"))
    name = as_choice(raw.get("provider", NullProvider.name), f"{where}.provider", PROVIDERS)
    if name == NullProvider.name:
        extra = [key for key in ("default", "agents", "pairs") if raw.get(key)]
        if extra:
            raise ConfigError(
                f"{where}: provider 'null' is plain ORCA and takes no directives, but {extra} "
                "is set. Use provider 'static'."
            )
        return NullProvider()
    return StaticProvider.from_config(raw, where)


def _agent_id(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ConfigError(f"{where}: expected an agent index, got {value!r}")
    try:
        agent_id = int(value)
    except ValueError as exc:
        raise ConfigError(f"{where}: expected an agent index, got {value!r}") from exc
    if agent_id < 0:
        raise ConfigError(f"{where}: an agent index cannot be negative, got {value!r}")
    return agent_id
