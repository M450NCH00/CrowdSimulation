"""Pair exposure: whether two agents' intended velocities put them on a collision course.

Issue #26 measured conflict per agent: an agent is exposed on a step if the velocity it
wants lies outside the half-plane ORCA allows it because of a neighbour. That half-plane is
offset by the agent's responsibility share, so the measure depends on the shares: in a pair
with shares (1, 0) only one agent is ever exposed, and the same state of the world is
counted differently under different shares (``docs/metrics.md``, section 3).

Issue #30 adds a measure of the *pair* that does not. On each step every agent has an
**intended velocity** v̂: its preferred velocity once its directives have acted on it
(``speed_scale``, the arbiter's bound, a baseline's perturbation), before ORCA's projection.
The pair (i, j) is **exposed** on the step if the relative velocity ``v̂_i − v̂_j`` lies inside
the truncated velocity obstacle of the two bodies, VO^τ_{i|j}: the set of relative
velocities that bring the bodies into contact within τ (``docs/orca.md``, section 3), by
more than a tolerance ε. Bodies that already overlap are exposed.

The obstacle is that of the two bodies alone, radius ``r_i + r_j``: a directive's clearance
margin is left out, so that the measure is the same function in every condition
(``docs/derivations.md``, section 16, which also shows why it cannot depend on the shares).
The horizon is the larger of the two agents' ORCA horizons; in every shipped scenario they
are equal.

The geometry is ORCA's own: the signed distance from the relative velocity to the boundary
of the obstacle is the ``margin`` that ``orca.agent_half_plane`` computes for a pair with no
share, side or clearance (positive inside). Nothing here changes what any agent does.
"""

from __future__ import annotations

import math

from .orca import TIE_BRAKE, agent_half_plane

Vec = tuple[float, float]


def obstacle_depth(rel_pos: Vec, rel_vel: Vec, combined_radius: float, tau: float) -> float:
    """How far inside the truncated velocity obstacle ``rel_vel`` lies; negative outside.

    ``rel_pos`` is the second agent's position minus the first's, ``rel_vel`` the first
    agent's velocity minus the second's (the convention of ``docs/orca.md``, section 3).
    Bodies already closer than ``combined_radius`` are in contact: the depth is infinite.
    """
    px, py = rel_pos
    if px * px + py * py <= combined_radius * combined_radius:
        return math.inf
    # The time step only matters to ORCA's half-plane for overlapping bodies, handled above.
    return agent_half_plane(rel_pos, rel_vel, (0.0, 0.0), combined_radius, tau, tau, tie_break=TIE_BRAKE).margin


def pair_exposed(
    position_i: Vec,
    position_j: Vec,
    intended_i: Vec,
    intended_j: Vec,
    combined_radius: float,
    tau: float,
    eps: float,
) -> bool:
    """Whether the pair is on a collision course at its intended velocities, by more than ``eps``.

    Symmetric in the two agents: swapping them negates both the relative position and the
    relative velocity, and the obstacle is symmetric under that. Reads no directive.
    """
    px, py = position_j[0] - position_i[0], position_j[1] - position_i[1]
    wx, wy = intended_i[0] - intended_j[0], intended_i[1] - intended_j[1]
    gap = math.hypot(px, py) - combined_radius
    # A pair that cannot close its gap within tau even at its full relative speed is not on a
    # collision course; most pairs of a crowd are decided by this test alone.
    if gap > 0.0 and gap > (math.hypot(wx, wy) + eps) * tau:
        return False
    return obstacle_depth((px, py), (wx, wy), combined_radius, tau) > eps
