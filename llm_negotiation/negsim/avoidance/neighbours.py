"""Neighbour search with a uniform grid, so that a step does not cost the square of the crowd.

The plane is cut into square cells of side ``cell_size``. Rebuilding the grid is one pass
over the agents. A query looks at the cell an agent is in, then at the ring of cells
around it, then at the next ring, and stops as soon as no cell further out can hold a
neighbour that would be kept. With ``k`` neighbours wanted, a crowd of any size costs each
agent a number of cells that depends on the local density, not on the size of the crowd.

(The ORCA paper suggests a k-d tree for this, Sec 5.1, and the RVO2 library uses one. A
grid does the same job, is rebuilt in one pass, and is easier to check; issue #26 allows
either. The grid here was written for this project.)
"""

from __future__ import annotations

import math
from typing import Iterable, Iterator

Entry = tuple[int, float, float]  # agent id, x, y


class SpatialGrid:
    def __init__(self, cell_size: float):
        if cell_size <= 0.0:
            raise ValueError(f"cell_size must be positive, got {cell_size}")
        self.cell_size = cell_size
        self._cells: dict[tuple[int, int], list[Entry]] = {}
        self._bounds = (0, 0, -1, -1)  # min cx, min cy, max cx, max cy; empty when max < min

    def rebuild(self, entries: Iterable[Entry]) -> None:
        """Replace the grid's contents with ``(agent id, x, y)`` entries."""
        size = self.cell_size
        cells: dict[tuple[int, int], list[Entry]] = {}
        for entry in entries:
            key = (math.floor(entry[1] / size), math.floor(entry[2] / size))
            bucket = cells.get(key)
            if bucket is None:
                cells[key] = [entry]
            else:
                bucket.append(entry)
        self._cells = cells
        if cells:
            xs = [key[0] for key in cells]
            ys = [key[1] for key in cells]
            self._bounds = (min(xs), min(ys), max(xs), max(ys))
        else:
            self._bounds = (0, 0, -1, -1)

    def __len__(self) -> int:
        return sum(len(bucket) for bucket in self._cells.values())

    def nearest(
        self, agent_id: int, x: float, y: float, radius: float, k: int
    ) -> list[tuple[float, int]]:
        """The ``k`` agents nearest ``(x, y)`` that are no further away than ``radius``.

        Returns ``(squared distance, agent id)`` pairs, nearest first; equal distances are
        ordered by agent id, so the result does not depend on the order of insertion.
        ``agent_id`` itself is left out.
        """
        if k <= 0 or radius < 0.0:
            return []
        size = self.cell_size
        cx, cy = math.floor(x / size), math.floor(y / size)
        min_cx, min_cy, max_cx, max_cy = self._bounds
        radius_sq = radius * radius
        limit_sq = radius_sq  # nothing beyond this can still be kept
        found: list[tuple[float, int]] = []
        cells = self._cells
        # No occupied cell lies beyond this ring, and none beyond the radius matters.
        last_ring = min(
            math.ceil(radius / size),
            max(cx - min_cx, max_cx - cx, cy - min_cy, max_cy - cy, 0),
        )

        for ring in range(last_ring + 1):
            # Every point of a cell on this ring is at least (ring - 1) cells away.
            if ring > 1:
                gap = (ring - 1) * size
                if gap * gap > limit_sq:
                    break
            for key in _ring(cx, cy, ring, min_cx, min_cy, max_cx, max_cy):
                bucket = cells.get(key)
                if bucket is None:
                    continue
                for other_id, ox, oy in bucket:
                    if other_id == agent_id:
                        continue
                    dx, dy = ox - x, oy - y
                    dist_sq = dx * dx + dy * dy
                    if dist_sq <= limit_sq:
                        found.append((dist_sq, other_id))
            if len(found) >= k:
                found.sort()
                del found[k:]
                limit_sq = found[-1][0]
        found.sort()
        del found[k:]
        return found

    def pairs_within(self, distance: float) -> Iterator[tuple[int, int, float]]:
        """Every unordered pair of agents no further apart than ``distance``.

        Yields ``(lower id, higher id, squared distance)``, each pair once.
        """
        if distance < 0.0:
            return
        size = self.cell_size
        reach = math.ceil(distance / size)
        distance_sq = distance * distance
        cells = self._cells
        for (cx, cy), bucket in cells.items():
            for index, (a_id, ax, ay) in enumerate(bucket):
                for b_id, bx, by in bucket[index + 1 :]:
                    dist_sq = (bx - ax) ** 2 + (by - ay) ** 2
                    if dist_sq <= distance_sq:
                        yield (a_id, b_id, dist_sq) if a_id < b_id else (b_id, a_id, dist_sq)
            # Each pair of different cells is visited once: from the cell that comes first
            # in (x, then y) order.
            for ox in range(0, reach + 1):
                for oy in range(-reach if ox > 0 else 1, reach + 1):
                    other = cells.get((cx + ox, cy + oy))
                    if other is None:
                        continue
                    for a_id, ax, ay in bucket:
                        for b_id, bx, by in other:
                            dist_sq = (bx - ax) ** 2 + (by - ay) ** 2
                            if dist_sq <= distance_sq:
                                yield (a_id, b_id, dist_sq) if a_id < b_id else (b_id, a_id, dist_sq)


def _ring(
    cx: int, cy: int, ring: int, min_cx: int, min_cy: int, max_cx: int, max_cy: int
) -> Iterator[tuple[int, int]]:
    """Cells at Chebyshev distance ``ring`` from ``(cx, cy)``, inside the occupied bounds."""
    if ring == 0:
        yield (cx, cy)
        return
    lo_x, hi_x = max(cx - ring, min_cx), min(cx + ring, max_cx)
    for y in (cy - ring, cy + ring):
        if min_cy <= y <= max_cy:
            for x in range(lo_x, hi_x + 1):
                yield (x, y)
    lo_y, hi_y = max(cy - ring + 1, min_cy), min(cy + ring - 1, max_cy)
    for x in (cx - ring, cx + ring):
        if min_cx <= x <= max_cx:
            for y in range(lo_y, hi_y + 1):
                yield (x, y)


def brute_force_nearest(
    entries: Iterable[Entry], agent_id: int, x: float, y: float, radius: float, k: int
) -> list[tuple[float, int]]:
    """The same answer as :meth:`SpatialGrid.nearest`, by looking at every agent.

    Kept as the reference the grid is tested against.
    """
    radius_sq = radius * radius
    found = []
    for other_id, ox, oy in entries:
        if other_id == agent_id:
            continue
        dx, dy = ox - x, oy - y
        dist_sq = dx * dx + dy * dy
        if dist_sq <= radius_sq:
            found.append((dist_sq, other_id))
    found.sort()
    return found[: max(k, 0)]
