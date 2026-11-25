"""Who leads and who follows through a conflict zone.

GameChat's fallback, "Strategy 1", gives the lead to the agent that would reach the
conflict point sooner: "Agent i checks if TTQ_i < TTQ_j ... If so, then agent i simply
chooses v_max as its linear velocity for the whole game, taking the leader role"
(arXiv:2503.12333v1, Sec IV-D). A negotiated agreement overrides that, as long as it can
still be carried out.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional

from .detection import Conflict
from .timing import time_to_clear, time_to_region

TIE_TOLERANCE_S = 1e-6
TIE_BREAKS = ("lower_index", "random")


class Role(str, Enum):
    LEADER = "leader"
    FOLLOWER = "follower"


class RoleSource(str, Enum):
    NEGOTIATED = "negotiated"
    STRATEGY1 = "strategy1"
    # A negotiated follower that is already inside the zone cannot give way any more.
    PHYSICAL_PRECEDENCE = "physical_precedence"


@dataclass(frozen=True)
class RoleDecision:
    leader_id: int
    follower_id: int
    source: RoleSource
    tie_broken: bool = False

    def role_of(self, agent_id: int) -> Role:
        return Role.LEADER if agent_id == self.leader_id else Role.FOLLOWER


def strategy1_leader(conflict: Conflict, max_speeds: Mapping[int, float]) -> Optional[int]:
    """Strategy 1: the agent with the shorter time to the conflict region leads.

    If both are already inside, the one that will be out sooner leads. Returns ``None``
    when the two are tied.
    """
    i, j = conflict.agent_ids
    for measure in (time_to_region, time_to_clear):
        t_i = measure(conflict.views[i], max_speeds[i])
        t_j = measure(conflict.views[j], max_speeds[j])
        if abs(t_i - t_j) > TIE_TOLERANCE_S:
            return i if t_i < t_j else j
    return None


def break_tie(conflict: Conflict, tie_break: str, rng: Optional[random.Random] = None) -> int:
    """Pick a leader for a tied pair.

    The paper assumes exact ties "do not occur as in practice, due to numerical error in
    computation" (Sec IV-D, proof of Theorem IV.3). This simulator is deterministic, so a
    symmetric scenario *does* produce an exact tie, and the tie is broken explicitly: by
    the lower agent index (the default, which the experiment design balances by swapping
    which participant is agent 0) or by a seeded random draw.
    """
    if tie_break == "lower_index":
        return min(conflict.agent_ids)
    if tie_break == "random":
        if rng is None:
            raise ValueError("tie_break='random' needs a seeded random.Random")
        return rng.choice(sorted(conflict.agent_ids))
    raise ValueError(f"unknown tie_break {tie_break!r}; expected one of {TIE_BREAKS}")


def decide_roles(
    conflict: Conflict,
    max_speeds: Mapping[int, float],
    negotiated_leader: Optional[int] = None,
    tie_break: str = "lower_index",
    rng: Optional[random.Random] = None,
    tie_winner: Optional[int] = None,
) -> RoleDecision:
    """Combine a negotiated agreement, physical precedence and Strategy 1.

    ``tie_winner`` is the leader chosen the last time this pair was tied, so that a random
    tie-break is drawn once and then kept.
    """
    i, j = conflict.agent_ids
    if negotiated_leader is not None and negotiated_leader not in (i, j):
        raise ValueError(f"negotiated leader {negotiated_leader} is not one of agents {i}, {j}")

    inside = [k for k in (i, j) if conflict.views[k].d_in <= 0.0]
    if len(inside) == 1:
        leader = inside[0]
        if negotiated_leader is None:
            source = RoleSource.STRATEGY1
        elif negotiated_leader == leader:
            source = RoleSource.NEGOTIATED
        else:
            source = RoleSource.PHYSICAL_PRECEDENCE
        return RoleDecision(leader, conflict.other(leader), source)

    if negotiated_leader is not None:
        return RoleDecision(
            negotiated_leader, conflict.other(negotiated_leader), RoleSource.NEGOTIATED
        )

    leader = strategy1_leader(conflict, max_speeds)
    tied = leader is None
    if tied:
        leader = tie_winner if tie_winner is not None else break_tie(conflict, tie_break, rng)
    return RoleDecision(leader, conflict.other(leader), RoleSource.STRATEGY1, tie_broken=tied)
