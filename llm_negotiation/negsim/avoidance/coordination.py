"""Who decides what for a pair of agents: ORCA, and the arbiter of issue #24.

In open space ORCA alone keeps a pair apart. A single-file segment is different: two
agents that meet inside one cannot pass, and ORCA can only slow them both to a halt.
There the arbiter decides who goes first, as it does in the hallway of issue #24, and the
other agent is held back until the first one is through. The arbiter is used as it is:
nothing in ``negsim.conflict.roles`` or ``negsim.control.strategy1`` was changed. What is
new is a detector for it (:class:`SingleFileDetector`), which is the extension point the
arbiter was built with.

**What each layer does for a pair the arbiter holds.** The arbiter decides the order and
gives the follower a speed bound, which caps the speed the follower *wants* to walk at, so
that it does not enter the segment before the leader has left it. ORCA is never switched
off: it goes on keeping the two bodies apart, with the follower taking all of the
avoidance and the leader none (shares 1 and 0). So a follower waiting at the mouth of the
segment steps out of the way of a leader coming out, and the leader does not slow down
for it.

**When control passes** (``docs/architecture.md``, section 6.4, says the same in full):

*ORCA to arbiter*, for a pair of agents, on the first step on which all of these hold:
  1. each perceives the other (each is among the other's perceived neighbours);
  2. a single-file segment that is too narrow for the two to pass in lies on both their
     paths, and neither has cleared it yet;
  3. the arbiter's own test says the two would be in each other's way there: they would
     occupy the conflict zone at overlapping times
     (``negsim.conflict.timing.is_social_minigame``).

*Arbiter to ORCA*, on the first step on which the conflict zone is no longer live (one of
the two has cleared it) or one of the two has arrived.

*Arbiter to a back-up manoeuvre* (issue #32), on the step on which one of the two starts to
back out of the segment on a ``back_up`` directive: the directive has already decided who goes
first and how, so the pair is not the arbiter's while the manoeuvre lasts
(``negsim.avoidance.simulation``; ``docs/derivations.md``, section 17). A pair in a manoeuvre is
never taken by the arbiter.

**The conflict zone** of a pair at a segment is, on each agent's path, the stretch inside
the segment plus a run-out at each end as long as the two radii and the safety margin
together. An agent whose centre is outside its zone cannot touch an agent whose centre is
inside the segment.

The arbiter thinks in terms of a maximum speed that agents walk at when nothing is in
their way. For an ORCA agent that speed is its preferred speed, not its maximum speed
(which it reaches only when dodging). The arbiter is therefore shown each agent through a
view whose ``max_speed`` is the speed the agent would walk at if left alone.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence

from ..conflict.detection import Conflict, ConflictDetector
from ..conflict.roles import TIE_BREAKS, Role
from ..conflict.timing import is_social_minigame
from ..conflict.zone import ZoneView
from ..control.strategy1 import POLICIES, AgentDecision, Arbiter
from ..core.world import World

Pair = tuple[int, int]

TO_ARBITER, TO_ORCA, TO_BACK_UP = "arbiter", "orca", "back_up"

#: While the arbiter holds a pair, the follower does all of the avoiding and the leader none.
FOLLOWER_SHARE, LEADER_SHARE = 1.0, 0.0


@dataclass(frozen=True)
class ArbitrationSettings:
    """How single-file segments are handled in an avoidance run.

    ``enabled: false`` leaves everything to ORCA; it exists as a negative control.
    """

    enabled: bool = True
    policy: str = "strategy1"
    tie_break: str = "lower_index"

    def __post_init__(self) -> None:
        if self.policy not in POLICIES:
            raise ValueError(f"unknown arbitration policy {self.policy!r}; expected one of {POLICIES}")
        if self.tie_break not in TIE_BREAKS:
            raise ValueError(f"unknown tie_break {self.tie_break!r}; expected one of {TIE_BREAKS}")

    def as_dict(self) -> dict[str, Any]:
        return {"enabled": self.enabled, "policy": self.policy, "tie_break": self.tie_break}


@dataclass(frozen=True)
class Handoff:
    """Control of a pair passing from one layer to the other."""

    step: int
    time_s: float
    pair: Pair
    to: str
    leader: Optional[int]
    role_source: Optional[str]
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "time_s": round(self.time_s, 6),
            "pair": list(self.pair),
            "to": self.to,
            "leader": self.leader,
            "role_source": self.role_source,
            "reason": self.reason,
        }


class SingleFileDetector(ConflictDetector):
    """The conflict zone of two agents at a single-file segment that both have to use.

    ``stretches`` maps an agent to the stretches of its path that run through a segment,
    each ``(segment index, arc length in, arc length out)``; ``widths`` gives the width of
    each segment. A segment counts for a pair only if it is too narrow for the two to
    pass in: narrower than the sum of their two diameters.
    """

    name = "single_file"

    def __init__(
        self,
        safety_margin: float,
        stretches: Mapping[int, Sequence[tuple[int, float, float]]],
        widths: Sequence[float],
    ):
        super().__init__(safety_margin)
        self.stretches = stretches
        self.widths = widths

    def zone(self, a: Any, b: Any) -> Optional[Conflict]:
        """The zone at the first shared segment that either agent has still to clear."""
        runout = self.clearance(a, b)
        diameters = 2.0 * (a.spec.radius + b.spec.radius)
        other = {index: (entry_s, exit_s) for index, entry_s, exit_s in self.stretches.get(b.agent_id, ())}
        for index, entry_s, exit_s in self.stretches.get(a.agent_id, ()):
            if index not in other or self.widths[index] >= diameters:
                continue
            view_a = ZoneView(entry_s - runout - a.path_s, exit_s + runout - a.path_s)
            view_b = ZoneView(other[index][0] - runout - b.path_s, other[index][1] + runout - b.path_s)
            if view_a.cleared and view_b.cleared:
                continue  # both are through this one; look at the next segment they share
            return Conflict((a.agent_id, b.agent_id), {a.agent_id: view_a, b.agent_id: view_b})
        return None


class _SpecView:
    __slots__ = ("radius", "max_speed", "path")

    def __init__(self, radius: float, max_speed: float, path: Any):
        self.radius, self.max_speed, self.path = radius, max_speed, path


class _AgentView:
    """One agent as the arbiter sees it: its ``max_speed`` is its walking speed."""

    __slots__ = ("agent_id", "spec", "pose", "path_s", "done")

    def __init__(self, agent: Any, travel_speed: float):
        self.agent_id = agent.agent_id
        self.spec = _SpecView(agent.spec.radius, travel_speed, agent.spec.path)
        self.pose, self.path_s, self.done = agent.pose, agent.path_s, agent.done


class _WorldView:
    __slots__ = ("agents",)

    def __init__(self, agents: Sequence[_AgentView]):
        self.agents = agents


class Coordinator:
    """Runs the arbiter over the pairs that need it and tracks which pairs it holds."""

    def __init__(
        self,
        settings: ArbitrationSettings,
        safety_margin: float,
        stretches: Mapping[int, Sequence[tuple[int, float, float]]],
        widths: Sequence[float],
        seed: int = 0,
    ):
        self.settings = settings
        self.detector = SingleFileDetector(safety_margin, stretches, widths)
        self.arbiter = Arbiter(
            self.detector, policy=settings.policy, tie_break=settings.tie_break, rng=random.Random(seed)
        )
        self.arbitrated: set[Pair] = set()

    def step(
        self,
        world: World,
        travel_speeds: Mapping[int, float],
        mutual_pairs: Iterable[Pair],
        leaders: Mapping[Pair, int],
        released: Iterable[Pair] = (),
    ) -> tuple[dict[int, AgentDecision], dict[Pair, tuple[int, int]], list[Handoff]]:
        """Decide this step's speed bounds and update the set of pairs the arbiter holds.

        ``mutual_pairs`` are the pairs that perceive each other now (condition 1 of the
        module docstring). ``leaders`` maps a pair to the agent its directives say goes
        first. ``released`` are the pairs in a back-up manoeuvre (issue #32), which the arbiter
        does not hold. Returns the arbiter's decision for every agent in a pair it holds, the
        ``(leader, follower)`` of every held pair that has roles on this step, and the
        handoffs that happened on this step.
        """
        released = set(released)
        watched = set(mutual_pairs) | self.arbitrated
        if not watched:
            return {}, {}, []

        view = _WorldView([_AgentView(agent, travel_speeds.get(agent.agent_id, 0.0)) for agent in world.agents])
        handoffs: list[Handoff] = []
        holding: set[Pair] = set()
        for pair in sorted(watched):
            if pair in released:
                if pair in self.arbitrated:
                    handoffs.append(
                        Handoff(world.step_index, world.time, pair, TO_BACK_UP, None, None, "a back-up manoeuvre took the pair")
                    )
                continue
            a, b = view.agents[pair[0]], view.agents[pair[1]]
            conflict = None if a.done or b.done else self.detector.zone(a, b)
            live = conflict is not None and conflict.live
            if pair in self.arbitrated:
                if live:
                    holding.add(pair)
                else:
                    reason = "an agent arrived" if a.done or b.done else "the conflict zone was cleared"
                    handoffs.append(Handoff(world.step_index, world.time, pair, TO_ORCA, None, None, reason))
            elif live and is_social_minigame(conflict, {a.agent_id: a.spec.max_speed, b.agent_id: b.spec.max_speed}):
                holding.add(pair)

        decisions: dict[int, AgentDecision] = {}
        roles: dict[Pair, tuple[int, int]] = {}
        if holding:
            negotiated = {pair: leaders[pair] for pair in holding if pair in leaders}
            resolved = self.arbiter.resolve(view, negotiated, visible=lambda i, j: (min(i, j), max(i, j)) in holding)
            members = {agent_id for pair in holding for agent_id in pair}
            decisions = {agent_id: resolved[agent_id] for agent_id in members}
            for pair in holding:
                first, second = decisions[pair[0]], decisions[pair[1]]
                if first.role is Role.LEADER and second.role is Role.FOLLOWER:
                    roles[pair] = pair
                elif first.role is Role.FOLLOWER and second.role is Role.LEADER:
                    roles[pair] = (pair[1], pair[0])

        for pair in sorted(holding - self.arbitrated):
            leader = roles[pair][0] if pair in roles else None
            source = decisions[pair[0]].role_source
            handoffs.append(
                Handoff(
                    world.step_index, world.time, pair, TO_ARBITER, leader,
                    None if source is None else source.value, "a single-file conflict is live",
                )
            )
        self.arbitrated = holding
        return decisions, roles, handoffs
