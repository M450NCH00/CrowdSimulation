"""2D geometry helpers (standard library only).

Angles are in radians, measured anticlockwise from the +x axis. Lengths are in metres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

Vec = tuple[float, float]


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the interval (-pi, pi]."""
    wrapped = math.fmod(angle + math.pi, 2.0 * math.pi)
    if wrapped <= 0.0:
        wrapped += 2.0 * math.pi
    return wrapped - math.pi


def heading_vec(theta: float) -> Vec:
    return (math.cos(theta), math.sin(theta))


def dist(a: Vec, b: Vec) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def line_intersection(
    p: Vec, theta_p: float, q: Vec, theta_q: float, eps: float = 1e-9
) -> Optional[tuple[Vec, float, float]]:
    """Intersect the line through ``p`` with heading ``theta_p`` and the one through ``q``.

    Returns ``(point, t, s)`` where ``t`` and ``s`` are the signed distances from ``p`` and
    ``q`` to the point, measured along their headings (negative means the point is behind).
    Returns ``None`` when the lines are parallel.
    """
    ux, uy = heading_vec(theta_p)
    wx, wy = heading_vec(theta_q)
    det = ux * wy - uy * wx  # sin of the angle from u to w
    if abs(det) < eps:
        return None
    dx, dy = q[0] - p[0], q[1] - p[1]
    t = (dx * wy - dy * wx) / det
    s = (dx * uy - dy * ux) / det
    return ((p[0] + t * ux, p[1] + t * uy), t, s)


def ray_intersection(
    p: Vec, theta_p: float, q: Vec, theta_q: float, eps: float = 1e-9
) -> Optional[tuple[Vec, float, float]]:
    """Like :func:`line_intersection`, but only when the point lies ahead of both origins.

    This is GameChat's conflict test: "the agents compute a ray originating from their
    respective position and moving in the direction of their respective headings"
    (Mahadevan et al., arXiv:2503.12333v1, Sec IV-B).
    """
    hit = line_intersection(p, theta_p, q, theta_q, eps)
    if hit is None or hit[1] < 0.0 or hit[2] < 0.0:
        return None
    return hit


def point_segment_distance(p: Vec, a: Vec, b: Vec) -> float:
    """Distance from point ``p`` to the segment ``a``-``b``."""
    return dist(p, _closest_on_segment(p, a, b)[0])


def _closest_on_segment(p: Vec, a: Vec, b: Vec) -> tuple[Vec, float]:
    """Closest point on segment ``a``-``b`` to ``p`` and its parameter ``u`` in [0, 1]."""
    abx, aby = b[0] - a[0], b[1] - a[1]
    length_sq = abx * abx + aby * aby
    if length_sq == 0.0:
        return a, 0.0
    u = ((p[0] - a[0]) * abx + (p[1] - a[1]) * aby) / length_sq
    u = min(1.0, max(0.0, u))
    return (a[0] + u * abx, a[1] + u * aby), u


class Polyline:
    """A path made of straight segments, addressed by arc length ``s`` from its first point."""

    def __init__(self, points: Sequence[Vec]):
        pts = [(float(x), float(y)) for x, y in points]
        if len(pts) < 2:
            raise ValueError("a path needs at least two points")
        cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            seg = dist(a, b)
            if seg <= 0.0:
                raise ValueError(f"a path may not repeat a point: {a}")
            cum.append(cum[-1] + seg)
        self.points: tuple[Vec, ...] = tuple(pts)
        self._cum: tuple[float, ...] = tuple(cum)

    @property
    def length(self) -> float:
        return self._cum[-1]

    def _segment_index(self, s: float) -> int:
        """Index of the segment containing arc length ``s`` (the later one at a vertex)."""
        last = len(self.points) - 2
        for k in range(last + 1):
            if s < self._cum[k + 1]:
                return k
        return last

    def point_at(self, s: float) -> Vec:
        """Point at arc length ``s``; ``s`` is clamped to the path."""
        s = min(self.length, max(0.0, s))
        k = self._segment_index(s)
        a, b = self.points[k], self.points[k + 1]
        u = (s - self._cum[k]) / (self._cum[k + 1] - self._cum[k])
        return (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))

    def heading_at(self, s: float) -> float:
        """Direction of travel at arc length ``s``."""
        k = self._segment_index(min(self.length, max(0.0, s)))
        a, b = self.points[k], self.points[k + 1]
        return math.atan2(b[1] - a[1], b[0] - a[0])

    def project(self, p: Vec, s_min: float = 0.0) -> float:
        """Arc length of the point on the path closest to ``p``, never less than ``s_min``.

        ``s_min`` makes progress along the path monotone: pass the previous result so that
        an agent cannot appear to move backwards along its own path.
        """
        best_s, best_d = min(self.length, max(0.0, s_min)), math.inf
        for k in range(len(self.points) - 1):
            if self._cum[k + 1] < s_min:
                continue
            closest, u = _closest_on_segment(p, self.points[k], self.points[k + 1])
            s = self._cum[k] + u * (self._cum[k + 1] - self._cum[k])
            if s < s_min:
                s = s_min
                closest = self.point_at(s)
            d = dist(p, closest)
            if d < best_d - 1e-12:
                best_s, best_d = s, d
        return best_s

    def distance_to(self, p: Vec) -> float:
        """Shortest distance from ``p`` to the path."""
        return min(
            point_segment_distance(p, a, b) for a, b in zip(self.points, self.points[1:])
        )

    def as_list(self) -> list[list[float]]:
        return [[x, y] for x, y in self.points]


@dataclass(frozen=True)
class Rect:
    """An axis-aligned rectangular obstacle (a wall block)."""

    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def __post_init__(self) -> None:
        if not (self.xmin < self.xmax and self.ymin < self.ymax):
            raise ValueError(f"degenerate rectangle: {self}")

    def distance_to(self, p: Vec) -> float:
        """Distance from ``p`` to the rectangle; zero if ``p`` is inside it."""
        dx = max(self.xmin - p[0], 0.0, p[0] - self.xmax)
        dy = max(self.ymin - p[1], 0.0, p[1] - self.ymax)
        return math.hypot(dx, dy)

    def intersects_segment(self, a: Vec, b: Vec) -> bool:
        """True if the segment ``a``-``b`` passes through the rectangle (slab method)."""
        t0, t1 = 0.0, 1.0
        for start, delta, lo, hi in (
            (a[0], b[0] - a[0], self.xmin, self.xmax),
            (a[1], b[1] - a[1], self.ymin, self.ymax),
        ):
            if delta == 0.0:
                if start < lo or start > hi:
                    return False
                continue
            ta, tb = (lo - start) / delta, (hi - start) / delta
            if ta > tb:
                ta, tb = tb, ta
            t0, t1 = max(t0, ta), min(t1, tb)
            if t0 > t1:
                return False
        return True

    def as_dict(self) -> dict[str, float]:
        return {"xmin": self.xmin, "ymin": self.ymin, "xmax": self.xmax, "ymax": self.ymax}
