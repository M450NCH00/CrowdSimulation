"""Conflict zones: the stretch of each agent's path that the two agents may not share.

The reasoning behind this module is written out in ``docs/derivations.md``. In short: two
discs moving along two paths can only touch while *both* centres are within
``clearance = r_i + r_j + margin`` of the other agent's path. Call that stretch of each
path the agent's zone. If the two centres are never inside their zones at the same time,
the discs never come closer than ``clearance``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional

from ..core.geometry import Polyline, Vec, line_intersection


@dataclass(frozen=True)
class ZoneView:
    """One agent's view of a conflict zone, as distances along its own predicted path.

    Both distances are measured from the agent's centre: ``d_in`` to where the centre
    enters the zone, ``d_out`` to where it leaves. A negative value means that point is
    already behind the agent.
    """

    d_in: float
    d_out: float

    @property
    def length(self) -> float:
        return self.d_out - self.d_in

    @property
    def inside(self) -> bool:
        return self.d_in <= 0.0 < self.d_out

    @property
    def cleared(self) -> bool:
        return self.d_out <= 0.0


def edge_quantities(view: ZoneView, radius: float) -> tuple[float, float, float]:
    """Translate a centre-based zone into the ``(d, L, l)`` of the follower speed formula.

    ``d`` is the distance from the agent's leading edge to the entry of the conflict
    region, ``L`` is the length of that region and ``l = 2 * radius`` is the body length.
    The leading edge reaches the region when the centre reaches the zone, so ``d`` equals
    ``view.d_in``; the trailing edge leaves the region when the centre leaves the zone, so
    ``d + L + l`` equals ``view.d_out`` (``docs/derivations.md`` section 3).
    """
    body_length = 2.0 * radius
    return view.d_in, view.length - body_length, body_length


def crossing_zone_views(
    p_i: Vec,
    theta_i: float,
    p_j: Vec,
    theta_j: float,
    clearance: float,
    half_length: Optional[float] = None,
    parallel_eps: float = 1e-6,
) -> Optional[tuple[ZoneView, ZoneView, Vec]]:
    """Zone of two agents predicted to keep moving straight along their headings.

    The two lines cross at a point Q at an angle phi. A centre is within ``clearance`` of
    the other line while it is within ``clearance / sin(phi)`` of Q, so that is the zone's
    half-length. Pass ``half_length`` to override it with a fixed value: the GameChat
    repository effectively uses 0.25 m (``mpc_cbf.py:237-239``), and ``half_length = radius``
    reproduces the paper's zero-width model with body length ``l = 2 * radius``.

    Returns ``(view_i, view_j, Q)``, or ``None`` if the headings are parallel.
    """
    hit = line_intersection(p_i, theta_i, p_j, theta_j, eps=parallel_eps)
    if hit is None:
        return None
    point, t_i, t_j = hit
    if half_length is None:
        half_length = clearance / abs(math.sin(theta_j - theta_i))
    return (
        ZoneView(t_i - half_length, t_i + half_length),
        ZoneView(t_j - half_length, t_j + half_length),
        point,
    )


def path_zone_interval(
    path: Polyline,
    other: Polyline,
    clearance: float,
    ds: float = 0.01,
    tol: float = 1e-6,
) -> Optional[tuple[float, float]]:
    """Arc-length interval of ``path`` that lies within ``clearance`` of ``other``.

    Found by sampling ``path`` every ``ds`` metres and refining both ends by bisection.
    If the path comes close to ``other`` more than once, the interval spans all of it,
    which errs on the side of a longer zone. Returns ``None`` if the paths stay apart.
    """

    def inside(s: float) -> bool:
        return other.distance_to(path.point_at(s)) < clearance

    n = max(1, math.ceil(path.length / ds))
    samples = [k * path.length / n for k in range(n + 1)]
    hits = [k for k, s in enumerate(samples) if inside(s)]
    if not hits:
        return None
    first, last = hits[0], hits[-1]
    s_in = 0.0 if first == 0 else _bisect(inside, samples[first - 1], samples[first], tol, want=True)
    s_out = (
        path.length
        if last == n
        else _bisect(inside, samples[last], samples[last + 1], tol, want=False)
    )
    return s_in, s_out


def _bisect(
    inside: Callable[[float], bool], lo: float, hi: float, tol: float, want: bool
) -> float:
    """Narrow ``[lo, hi]`` onto the point where ``inside`` flips; ``inside(hi) == want``.

    Returns ``hi``: for an entry that is just inside the zone and for an exit just outside
    it, so in both cases the zone comes out no shorter than it really is.
    """
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if inside(mid) == want:
            hi = mid
        else:
            lo = mid
    return hi
