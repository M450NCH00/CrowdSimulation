"""ORCA half-planes: which velocities one agent may choose because of one neighbour or wall.

Written from van den Berg, Guy, Lin and Manocha, "Reciprocal n-body collision avoidance"
(the paper GameChat cites as [22]); ``docs/orca.md`` has the derivation, section by
section, and says where this differs from the RVO2 library and why.

Notation, for an agent ``A`` and a neighbour ``B``:

``p``   position of ``B`` minus position of ``A``
``v``   velocity of ``A`` minus velocity of ``B`` (the relative velocity)
``R``   combined radius: the two radii plus any clearance margin
``tau`` time horizon

The velocity obstacle is the set of relative velocities that bring the two within ``R``
of each other at some time up to ``tau`` (paper, eq. 2). In the plane of relative
velocities it is a cone with its tip at the origin, cut off near the tip by an arc of the
disc of radius ``R / tau`` centred on ``p / tau`` (paper, Fig. 1b). Its boundary has three
parts: that **arc**, and the two straight **legs**. "Left" and "right" are as seen from
``A`` looking at ``B``.

A half-plane is returned as a directed line ``(px, py, dx, dy)``; the allowed velocities
are on the line or to its left (see ``negsim.avoidance.lp``).
"""

from __future__ import annotations

import math
from typing import NamedTuple, Optional

from ..core.geometry import Rect
from .lp import Line

LEFT, RIGHT = "left", "right"
SIDES = (LEFT, RIGHT)

# Where on the boundary of the velocity obstacle the half-plane was built.
REGION_ARC = "arc"
REGION_LEFT_LEG = "left_leg"
REGION_RIGHT_LEG = "right_leg"
REGION_APEX = "apex"  # an exact tie between the two legs, resolved without choosing a side
REGION_OVERLAP = "overlap"  # the two are already closer than the combined radius

#: How an exact tie between the two legs is resolved when no side preference applies.
TIE_BRAKE = "brake"  # take the half-plane at the tip of the arc: both slow down, neither turns
TIE_RIGHT = "right"  # the right leg, as the RVO2 library does
TIE_LEFT = "left"
TIE_BREAKS = (TIE_BRAKE, TIE_RIGHT, TIE_LEFT)

#: The relative velocity counts as lying on the cone's axis when the sine of its angle to
#: the axis is no larger than this.
TIE_EPS = 1e-9

DEFAULT_SHARE = 0.5


class AgentHalfPlane(NamedTuple):
    line: Line
    #: Unit normal of the line, pointing into the allowed half-plane.
    normal: tuple[float, float]
    #: Signed distance, along ``normal``, from the relative velocity to the boundary of
    #: the velocity obstacle. Positive: the pair is on a collision course and the relative
    #: velocity has to change by this much. Negative: it is not, and this much room is left.
    margin: float
    region: str

    @property
    def on_collision_course(self) -> bool:
        return self.margin > 0.0


def agent_half_plane(
    rel_pos: tuple[float, float],
    rel_vel: tuple[float, float],
    own_velocity: tuple[float, float],
    combined_radius: float,
    tau: float,
    dt: float,
    share: float = DEFAULT_SHARE,
    side: Optional[str] = None,
    tie_break: str = TIE_BRAKE,
) -> AgentHalfPlane:
    """The velocities agent ``A`` may choose because of neighbour ``B`` (paper, eq. 6).

    ``u`` is the vector from the relative velocity to a point on the boundary of the
    velocity obstacle and ``n`` the outward normal there. The paper allows ``A`` the
    half-plane ``{v : (v - (v_A + u / 2)) . n >= 0}``. Two things are generalised here.

    **The share.** When the pair is on a collision course, ``A`` must make up ``share`` of
    ``u`` instead of half. When it is not, the room that is left is still split in half,
    whatever the share: with any other split two shares that sum to more than 1 would
    let the pair steer onto a collision course (``docs/derivations.md``, section 9).

    **The side.** Normally the boundary point is the nearest one (paper, eq. 5). When the
    pair is on a collision course and ``side`` is given, the point is taken on that leg
    instead, so that ``A`` passes ``B`` on that side. Both agents must use the same side
    for their half-planes to be reciprocal; ``negsim.avoidance.directives`` sees to that.
    """
    px, py = rel_pos
    vx, vy = rel_vel
    dist_sq = px * px + py * py
    radius_sq = combined_radius * combined_radius

    if dist_sq <= radius_sq:
        # Already closer than the combined radius: ask for separation within one time step.
        wx, wy = vx - px / dt, vy - py / dt
        w_len = math.hypot(wx, wy)
        if w_len > 0.0:
            nx, ny = wx / w_len, wy / w_len
        elif dist_sq > 0.0:
            dist = math.sqrt(dist_sq)
            nx, ny = -px / dist, -py / dist
        else:
            nx, ny = 1.0, 0.0
        return _half_plane(own_velocity, nx, ny, combined_radius / dt - w_len, share, REGION_OVERLAP)

    wx, wy = vx - px / tau, vy - py / tau  # from the centre of the cut-off disc to v
    w_sq = wx * wx + wy * wy
    dot = wx * px + wy * py

    if dot < 0.0 and dot * dot > radius_sq * w_sq:
        # v looks at the arc: the nearest boundary point is on it.
        w_len = math.sqrt(w_sq)
        nx, ny = wx / w_len, wy / w_len
        margin, region = combined_radius / tau - w_len, REGION_ARC
    else:
        cross = px * wy - py * wx  # positive: v is to the left of the cone's axis
        tied = abs(cross) <= TIE_EPS * math.sqrt(dist_sq * w_sq)
        if tie_break == TIE_RIGHT:
            nearest = LEFT if cross > 0.0 else RIGHT  # RVO2: "det(...) > 0" is the left leg
        elif tie_break == TIE_LEFT:
            nearest = RIGHT if cross < 0.0 else LEFT
        elif tied:
            nearest = None
        else:
            nearest = LEFT if cross > 0.0 else RIGHT

        if nearest is None:
            # Neither leg is nearer. Take the tangent at the tip of the arc, which favours
            # no side: it only limits how fast the two may close.
            dist = math.sqrt(dist_sq)
            nx, ny = -px / dist, -py / dist
            margin = (vx * px + vy * py) / dist - (dist - combined_radius) / tau
            region = REGION_APEX
        else:
            nx, ny = _leg_normal(px, py, dist_sq, radius_sq, combined_radius, nearest)
            margin = -(vx * nx + vy * ny)
            region = REGION_LEFT_LEG if nearest == LEFT else REGION_RIGHT_LEG

    if side is not None and margin > 0.0:
        # On a collision course with a side to pass on: leave the cone across that leg.
        if side not in SIDES:
            raise ValueError(f"unknown side {side!r}; expected one of {SIDES}")
        nx, ny = _leg_normal(px, py, dist_sq, radius_sq, combined_radius, side)
        margin = -(vx * nx + vy * ny)
        region = REGION_LEFT_LEG if side == LEFT else REGION_RIGHT_LEG

    return _half_plane(own_velocity, nx, ny, margin, share, region)


def _leg_normal(
    px: float, py: float, dist_sq: float, radius_sq: float, radius: float, side: str
) -> tuple[float, float]:
    """Outward unit normal of one leg of the cone.

    The leg is the axis direction turned by the cone's half-angle, whose sine is
    ``radius / |p|``; the outward normal is the leg turned a further quarter turn away
    from the axis.
    """
    leg = math.sqrt(dist_sq - radius_sq)
    if side == LEFT:
        lx, ly = (px * leg - py * radius) / dist_sq, (px * radius + py * leg) / dist_sq
        return (-ly, lx)
    lx, ly = (px * leg + py * radius) / dist_sq, (-px * radius + py * leg) / dist_sq
    return (ly, -lx)


def _half_plane(
    own_velocity: tuple[float, float], nx: float, ny: float, margin: float, share: float, region: str
) -> AgentHalfPlane:
    # On a collision course the agent makes up its share of the change needed; otherwise
    # it may use half of the room that is left.
    offset = share * margin if margin > 0.0 else DEFAULT_SHARE * margin
    line = (own_velocity[0] + offset * nx, own_velocity[1] + offset * ny, ny, -nx)
    return AgentHalfPlane(line, (nx, ny), margin, region)


def wall_half_plane(
    position: tuple[float, float],
    radius: float,
    wall: Rect,
    tau_obst: float,
    max_speed: float,
) -> Optional[Line]:
    """The velocities an agent may choose because of one wall block (paper, Sec 5.4).

    The paper takes the half-plane tangent to the wall's velocity obstacle at the point
    closest to the optimisation velocity, and sets that velocity to zero for obstacles.
    For a convex wall that point lies straight toward the wall's nearest point ``q``, at
    ``(|q - p| - radius) / tau_obst`` from the origin, so the half-plane says: do not
    approach the nearest point faster than the gap divided by the horizon
    (``docs/orca.md``, section 5).

    Returns ``None`` when the wall is too far away for the half-plane to exclude any
    velocity the agent could have, or when the agent's centre is inside the wall (a
    collision, which the run reports and stops on).
    """
    x, y = position
    qx = wall.xmin if x < wall.xmin else wall.xmax if x > wall.xmax else x
    qy = wall.ymin if y < wall.ymin else wall.ymax if y > wall.ymax else y
    dx, dy = qx - x, qy - y
    distance = math.hypot(dx, dy)
    if distance == 0.0:
        return None
    gap = distance - radius
    if gap > tau_obst * max_speed:
        return None
    nx, ny = dx / distance, dy / distance  # toward the wall
    bound = max(gap, 0.0) / tau_obst
    return (bound * nx, bound * ny, -ny, nx)
