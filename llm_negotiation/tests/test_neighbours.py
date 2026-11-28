"""Neighbour search: the grid gives exactly what looking at every agent gives."""

from __future__ import annotations

import random

import pytest

from negsim.avoidance.neighbours import SpatialGrid, brute_force_nearest


def scatter(rng: random.Random, count: int, width: float, height: float):
    return [(agent_id, rng.uniform(-width, width), rng.uniform(-height, height)) for agent_id in range(count)]


@pytest.mark.parametrize("cell_size", [0.3, 1.0, 2.0, 7.5, 40.0])
def test_grid_matches_brute_force_on_random_crowds(cell_size):
    """Uniform crowds, corridors and clusters, at cell sizes from much smaller than the
    search radius to much larger: the same neighbours, the same order."""
    rng = random.Random(2610)
    queries = 0
    for _ in range(40):
        count = rng.choice([1, 2, 5, 30, 120])
        entries = scatter(rng, count, rng.choice([2.0, 15.0, 60.0]), rng.choice([0.5, 3.0, 15.0]))
        grid = SpatialGrid(cell_size)
        grid.rebuild(entries)
        assert len(grid) == count
        for agent_id, x, y in rng.sample(entries, min(count, 12)):
            radius, k = rng.choice([0.0, 0.8, 3.0, 12.5, 200.0]), rng.choice([0, 1, 3, 10, 500])
            assert grid.nearest(agent_id, x, y, radius, k) == brute_force_nearest(entries, agent_id, x, y, radius, k)
            queries += 1
    assert queries > 250


def test_an_agent_is_never_its_own_neighbour_and_the_limit_is_respected():
    entries = [(i, float(i), 0.0) for i in range(10)]
    grid = SpatialGrid(1.5)
    grid.rebuild(entries)
    found = grid.nearest(4, 4.0, 0.0, 100.0, 3)
    assert [agent_id for _, agent_id in found] == [3, 5, 2]  # 3 and 5 tie at 1 m: the lower id first
    assert [dist_sq for dist_sq, _ in found] == [1.0, 1.0, 4.0]
    assert grid.nearest(4, 4.0, 0.0, 100.0, 0) == []


def test_the_radius_is_inclusive():
    grid = SpatialGrid(2.0)
    grid.rebuild([(0, 0.0, 0.0), (1, 3.0, 4.0)])
    assert grid.nearest(0, 0.0, 0.0, 5.0, 10) == [(25.0, 1)]
    assert grid.nearest(0, 0.0, 0.0, 4.999, 10) == []


def test_a_far_neighbour_in_range_is_found_past_many_empty_cells():
    grid = SpatialGrid(0.5)
    grid.rebuild([(0, 0.0, 0.0), (1, 12.0, 0.1), (2, -30.0, 0.0)])
    assert [agent_id for _, agent_id in grid.nearest(0, 0.0, 0.0, 12.5, 10)] == [1]


def test_the_search_stops_at_the_kth_neighbour_without_missing_a_nearer_one():
    """A near neighbour in a far corner of a neighbouring cell must not be skipped just
    because k agents were already found in the agent's own cell."""
    entries = [(0, 0.95, 0.95), (1, 0.05, 0.05), (2, 0.1, 0.1), (3, 1.05, 1.0)]  # 3 is 0.11 m away, in the next cell
    grid = SpatialGrid(1.0)
    grid.rebuild(entries)
    assert [agent_id for _, agent_id in grid.nearest(0, 0.95, 0.95, 5.0, 1)] == [3]
    assert grid.nearest(0, 0.95, 0.95, 5.0, 2) == brute_force_nearest(entries, 0, 0.95, 0.95, 5.0, 2)


def test_rebuilding_replaces_the_contents():
    grid = SpatialGrid(1.0)
    grid.rebuild([(0, 0.0, 0.0), (1, 0.5, 0.0)])
    grid.rebuild([(0, 0.0, 0.0)])
    assert len(grid) == 1 and grid.nearest(0, 0.0, 0.0, 10.0, 5) == []
    grid.rebuild([])
    assert len(grid) == 0 and grid.nearest(0, 0.0, 0.0, 10.0, 5) == []


def test_a_cell_size_must_be_positive():
    with pytest.raises(ValueError, match="cell_size"):
        SpatialGrid(0.0)


@pytest.mark.parametrize("cell_size", [0.4, 1.0, 3.0])
def test_pairs_within_matches_brute_force(cell_size):
    rng = random.Random(2611)
    for _ in range(25):
        entries = scatter(rng, rng.choice([2, 20, 80]), rng.choice([3.0, 20.0]), rng.choice([1.0, 6.0]))
        distance = rng.choice([0.0, 0.5, 1.1, 4.0])
        grid = SpatialGrid(cell_size)
        grid.rebuild(entries)
        found = sorted(grid.pairs_within(distance))
        expected = sorted(
            (a_id, b_id, (bx - ax) ** 2 + (by - ay) ** 2)
            for index, (a_id, ax, ay) in enumerate(entries)
            for b_id, bx, by in entries[index + 1 :]
            if (bx - ax) ** 2 + (by - ay) ** 2 <= distance * distance
        )
        assert [(i, j) for i, j, _ in found] == [(i, j) for i, j, _ in expected]
        for (_, _, got), (_, _, want) in zip(found, expected):
            assert got == pytest.approx(want)
        assert len({(i, j) for i, j, _ in found}) == len(found)  # each pair once


def test_the_cost_of_a_query_does_not_grow_with_the_crowd():
    """The point of the grid. In a crowd of constant density, the number of agents a query
    has to look at stays the same when the crowd is made sixteen times larger."""

    def looked_at(side: int) -> float:
        entries = [(row * side + col, float(col), float(row)) for row in range(side) for col in range(side)]
        grid = SpatialGrid(2.0)
        grid.rebuild(entries)
        counter = {"n": 0}
        original = grid._cells

        class Counting(dict):
            def get(self, key, default=None):
                bucket = original.get(key, default)
                counter["n"] += 0 if bucket is None else len(bucket)
                return bucket

        grid._cells = Counting()
        middle = [entry for entry in entries if side // 4 <= entry[1] < 3 * side // 4 and side // 4 <= entry[2] < 3 * side // 4]
        for agent_id, x, y in middle[:50]:
            grid.nearest(agent_id, x, y, 12.5, 10)
        return counter["n"] / min(50, len(middle))

    small, large = looked_at(20), looked_at(80)  # 400 agents, 6,400 agents
    assert large <= small * 1.2
    # About 490 agents lie within the 12.5 m radius; a query looks at a fraction of them.
    assert large < 490 / 3
