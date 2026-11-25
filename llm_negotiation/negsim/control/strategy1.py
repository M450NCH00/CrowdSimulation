"""Strategy 1 velocity scaling: how fast the follower may go, and who is the follower.

The leader goes at its maximum speed. The follower "selects a velocity so it reaches Q at
the instant that agent j completely clears Q" (arXiv:2503.12333v1, Sec IV-D). The
derivation of the generalised bound used here is in ``docs/derivations.md``.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Mapping, Optional

from ..conflict.detection import ConflictDetector
from ..conflict.roles import Role, RoleSource, decide_roles
from ..conflict.timing import is_social_minigame
from ..conflict.zone import ZoneView, edge_quantities
from ..core.world import World

POLICIES = ("strategy1", "none")


def follower_speed_bound(
    d_i: float, d_j: float, v_j: float, l_j: float, L: float, v_i_max: float
) -> float:
    """Upper bound on the follower's speed: ``d_i * v_j / (d_j + L + l_j)``, capped at ``v_i_max``.

    ``d_i``, ``d_j``
        distance from the leading edge of the follower ``i`` and of the leader ``j`` to
        the entry of the conflict region [m].
    ``v_j``
        the leader's speed [m/s].
    ``l_j``
        the leader's body length [m]; for a disc of radius ``r`` this is ``2 * r``.
    ``L``
        length of the conflict region along the leader's path [m].
    ``v_i_max``
        the follower's own maximum speed [m/s].

    The leader's trailing edge is out of the region after ``(d_j + L + l_j) / v_j`` seconds;
    the follower's leading edge must not be at the entry before then. With ``L = 0``,
    ``l_j = l`` and ``v_j = v_max`` this is the paper's ``d_i * v_max / (l + d_j)``.
    """
    if v_i_max < 0.0 or v_j < 0.0:
        raise ValueError("speeds must not be negative")
    remaining = d_j + L + l_j
    if remaining <= 0.0:
        return v_i_max  # the leader is already clear
    if d_i <= 0.0:
        return 0.0  # the follower is at the entry and the leader is not clear: wait
    return min(v_i_max, d_i * v_j / remaining)


def follower_bound_from_views(
    follower_view: ZoneView,
    leader_view: ZoneView,
    leader_radius: float,
    leader_speed: float,
    follower_max_speed: float,
) -> float:
    """:func:`follower_speed_bound` fed from the zone views the detector returns."""
    d_j, region_length, body_length = edge_quantities(leader_view, leader_radius)
    return follower_speed_bound(
        follower_view.d_in, d_j, leader_speed, body_length, region_length, follower_max_speed
    )


@dataclass
class AgentDecision:
    """What the arbiter decided for one agent on one step (logged with the trajectory)."""

    speed_bound: float
    role: Optional[Role] = None
    role_source: Optional[RoleSource] = None
    in_conflict: bool = False
    zone_d_in: Optional[float] = None
    zone_d_out: Optional[float] = None


class Arbiter:
    """Applies Strategy 1 to every pair of agents and returns each agent's speed bound.

    ``policy = "none"`` detects conflicts but imposes no bound. It exists as a negative
    control: with it, the symmetric scenarios end in a collision.

    The pairwise loop works for any number of agents, but nothing here orders three or
    more agents consistently (a cycle of followers is possible). Only two-agent runs are
    supported by the experiment runner.
    """

    def __init__(
        self,
        detector: ConflictDetector,
        policy: str = "strategy1",
        tie_break: str = "lower_index",
        rng: Optional[random.Random] = None,
    ):
        if policy not in POLICIES:
            raise ValueError(f"unknown arbitration policy {policy!r}; expected one of {POLICIES}")
        self.detector = detector
        self.policy = policy
        self.tie_break = tie_break
        self.rng = rng
        self._tie_winners: dict[tuple[int, int], int] = {}

    def resolve(
        self,
        world: World,
        negotiated_leaders: Optional[Mapping[tuple[int, int], int]] = None,
        visible: Optional[Callable[[int, int], bool]] = None,
    ) -> dict[int, AgentDecision]:
        """Speed bound and role for every agent, from the current state of the world.

        ``negotiated_leaders`` maps a pair ``(i, j)`` with ``i < j`` to the agent the two
        agreed should go first. ``visible(i, j)`` says whether the two can see each other;
        a conflict between agents that cannot is not detected, since detection rests on
        what one agent observes of the other.
        """
        decisions = {a.agent_id: AgentDecision(speed_bound=a.spec.max_speed) for a in world.agents}
        active = [a for a in world.agents if not a.done]
        for index, a in enumerate(active):
            for b in active[index + 1 :]:
                if visible is not None and not visible(a.agent_id, b.agent_id):
                    continue
                conflict = self.detector.zone(a, b)
                if conflict is None:
                    continue
                pair = (a.agent_id, b.agent_id)
                for agent in (a, b):
                    decision = decisions[agent.agent_id]
                    if decision.zone_d_in is None:
                        view = conflict.views[agent.agent_id]
                        decision.zone_d_in, decision.zone_d_out = view.d_in, view.d_out

                max_speeds = {a.agent_id: a.spec.max_speed, b.agent_id: b.spec.max_speed}
                if not is_social_minigame(conflict, max_speeds):
                    continue

                roles = decide_roles(
                    conflict,
                    max_speeds,
                    (negotiated_leaders or {}).get(pair),
                    self.tie_break,
                    self.rng,
                    self._tie_winners.get(pair),
                )
                if roles.tie_broken:
                    self._tie_winners[pair] = roles.leader_id

                leader = world.agents[roles.leader_id]
                follower = world.agents[roles.follower_id]
                lead, follow = decisions[leader.agent_id], decisions[follower.agent_id]
                lead.in_conflict = follow.in_conflict = True
                follow.role, follow.role_source = Role.FOLLOWER, roles.source
                if lead.role is None:
                    lead.role, lead.role_source = Role.LEADER, roles.source
                if self.policy == "strategy1":
                    bound = follower_bound_from_views(
                        conflict.views[follower.agent_id],
                        conflict.views[leader.agent_id],
                        leader.spec.radius,
                        leader.spec.max_speed,
                        follower.spec.max_speed,
                    )
                    follow.speed_bound = min(follow.speed_bound, bound)
        return decisions
