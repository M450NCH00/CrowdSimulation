"""Issue #139 (RF-50): the grid corridor, its clash rule, its measures and the scripted walkers.
No model is called."""

from __future__ import annotations

import json
import re

import pytest

from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.grid import cases as C
from negsim.grid import measures as M
from negsim.grid import render as R
from negsim.grid import walkers as W
from negsim.grid.__main__ import main, run_script
from negsim.grid.world import (
    GridConfig, GridState, Move, Walker, grid_delta, head_on, load_config, run, step,
)

CONFIG = load_config()


def state(*walkers: Walker, seed: int = 1) -> GridState:
    return GridState(CONFIG, list(walkers), seed)


# --- the corridor (AS6) ----------------------------------------------------------------------


def test_config_gives_ras6_sizes():
    assert (CONFIG.cell_m, CONFIG.lanes, CONFIG.rows, CONFIG.start_cells_from_middle) == (0.4, 5, 50, 20)
    assert CONFIG.width_m == pytest.approx(2.0)
    assert CONFIG.tick_s == pytest.approx(0.3077, abs=1e-4)
    assert CONFIG.max_ticks == 195            # 60 s
    assert CONFIG.deadlock_ticks == 10        # 3.0 s, rounded up
    assert (CONFIG.start_row(1), CONFIG.start_row(-1)) == (5, 44)   # the 20th cell from the middle, each side
    assert (CONFIG.goal_row(1), CONFIG.goal_row(-1)) == (49, 0)
    assert CONFIG.x_m(5) == pytest.approx(-7.8) and CONFIG.x_m(44) == pytest.approx(7.8)
    assert CONFIG.y_m(2) == pytest.approx(0.0) and CONFIG.y_m(4) == pytest.approx(0.8)


def test_config_is_checked(tmp_path):
    path = tmp_path / "bad.yaml"
    text = (PACKAGE_ROOT / "configs" / "grid" / "corridor_v1.yaml").read_text(encoding="utf-8")
    path.write_text(text.replace("lanes: 5", "lanes: 4.5"), encoding="utf-8")
    with pytest.raises(ConfigError, match="whole number"):
        load_config(path)
    path.write_text(text + "extra: 1\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown"):
        load_config(path)
    with pytest.raises(ConfigError, match="even number of rows"):
        GridConfig(rows=51)


def test_moves_are_in_the_walkers_own_frame():
    # Heading +x, own left is +y (a higher lane); heading -x, own left is -y.
    assert grid_delta(Move.FORWARD_LEFT, 1) == (1, 1)
    assert grid_delta(Move.FORWARD_LEFT, -1) == (-1, -1)
    assert grid_delta(Move.RIGHT, -1) == (0, 1)
    assert grid_delta(Move.BACK, 1) == (-1, 0)
    assert grid_delta(Move.WAIT, -1) == (0, 0)


# --- the clash rule (AS7, and crossing paths) ------------------------------------------------


def test_a_move_into_an_occupied_cell_does_not_happen():
    s = state(Walker(0, 10, 2, 1), Walker(1, 11, 2, 1))
    actions = step(s, {0: Move.FORWARD, 1: Move.WAIT})
    assert s.walker(0).cell == (10, 2) and actions[0].blocked == "occupied"


def test_a_cell_left_in_the_same_tick_is_still_occupied():
    # Parallel update: occupancy is read at the start of the tick (Burstedde et al.).
    s = state(Walker(0, 10, 2, 1), Walker(1, 11, 2, 1))
    step(s, {0: Move.FORWARD, 1: Move.FORWARD})
    assert s.walker(0).cell == (10, 2) and s.walker(1).cell == (12, 2)


def test_no_swaps_face_to_face():
    s = state(Walker(0, 10, 2, 1), Walker(1, 11, 2, -1))
    actions = step(s, {0: Move.FORWARD, 1: Move.FORWARD})
    assert s.positions() == {0: (10, 2), 1: (11, 2)}
    assert [a.blocked for a in actions] == ["occupied", "occupied"]


def test_crossing_paths_are_blocked():
    # A goes forward-left (10,2)->(11,3); B, heading -x, goes forward-right (11,2)->(10,3): an X.
    s = state(Walker(0, 10, 2, 1), Walker(1, 11, 2, -1))
    assert grid_delta(Move.FORWARD_RIGHT, -1) == (-1, 1)
    actions = step(s, {0: Move.FORWARD_LEFT, 1: Move.FORWARD_RIGHT})
    assert s.positions() == {0: (10, 2), 1: (11, 2)}
    assert [a.blocked for a in actions] == ["crossing", "crossing"]


def test_diagonal_moves_that_do_not_cross_both_happen():
    s = state(Walker(0, 10, 2, 1), Walker(1, 11, 2, -1))
    step(s, {0: Move.FORWARD_LEFT, 1: Move.FORWARD_LEFT})   # A to (11,3), B to (10,1)
    assert s.positions() == {0: (11, 3), 1: (10, 1)}


def test_a_contest_for_one_cell_has_one_winner_drawn_from_the_seed():
    winners = set()
    for seed in range(1, 30):
        s = state(Walker(0, 10, 2, 1), Walker(1, 12, 2, -1), seed=seed)
        actions = step(s, {0: Move.FORWARD, 1: Move.FORWARD})
        moved = [a.walker for a in actions if a.moved != (0, 0)]
        assert len(moved) == 1
        assert [a.blocked for a in actions if a.walker != moved[0]] == ["contest_lost"]
        winners.add(moved[0])
        again = state(Walker(0, 10, 2, 1), Walker(1, 12, 2, -1), seed=seed)
        assert [a.moved for a in step(again, {0: Move.FORWARD, 1: Move.FORWARD})] == [a.moved for a in actions]
    assert winners == {0, 1}


def test_walls_and_the_end_behind_stop_a_move():
    s = state(Walker(0, 0, 4, 1), Walker(1, 30, 0, -1))
    actions = step(s, {0: Move.LEFT, 1: Move.LEFT})          # walker 1's left is -y: lane -1
    assert [a.blocked for a in actions] == ["wall", "wall"]
    actions = step(s, {0: Move.BACK, 1: Move.WAIT})
    assert actions[0].blocked == "wall" and s.walker(0).cell == (0, 4)


def test_a_slower_walker_advances_when_its_walked_distance_reaches_the_next_cell():
    s = state(Walker(0, 10, 2, 1, speed_mps=0.65), Walker(1, 40, 2, -1))
    rows, reasons = [], []
    for _ in range(6):
        reasons.append(step(s, {0: Move.FORWARD, 1: Move.WAIT})[0].blocked)
        rows.append(s.walker(0).row)
    assert rows == [10, 11, 11, 12, 12, 13]
    assert reasons == ["not_due", None, "not_due", None, "not_due", None]


def test_bad_walkers_are_refused():
    with pytest.raises(ConfigError, match="one cell a tick"):
        state(Walker(0, 10, 2, 1, speed_mps=1.5), Walker(1, 40, 2, -1))
    with pytest.raises(ConfigError, match="one cell"):
        state(Walker(0, 10, 2, 1), Walker(1, 10, 2, -1))
    with pytest.raises(ConfigError, match="outside"):
        state(Walker(0, 10, 5, 1), Walker(1, 40, 2, -1))
    with pytest.raises(ConfigError, match="direction"):
        Walker(0, 10, 2, 0)


def test_a_walker_arrives_at_the_last_row_and_leaves_the_grid():
    s = state(Walker(0, 48, 2, 1), Walker(1, 1, 2, -1))
    step(s, {0: Move.FORWARD, 1: Move.FORWARD})
    assert s.walker(0).arrived_tick == 1 and s.walker(1).arrived_tick == 1 and s.active() == []


# --- the scripted walkers (task 2): their expected outcomes ----------------------------------

EXPECTED = {
    # script, geometry: (resolved, passed, squeezed, face to face, dance, deadlock, passing distance m)
    ("keep_right", "aligned"): (True, True, False, False, False, False, 0.8),
    ("keep_right", "one_lane_apart"): (True, True, False, False, False, False, 0.8),
    ("keep_left", "aligned"): (True, True, False, False, False, False, 0.8),
    ("keep_left", "one_lane_apart"): (True, True, False, False, False, False, 0.8),
    ("hold_and_step_aside", "aligned"): (True, True, False, False, False, False, 0.8),
    ("hold_and_step_aside", "one_lane_apart"): (True, True, False, False, False, False, 0.8),
    ("hold_and_step_aside_1_lane", "aligned"): (False, True, True, False, False, False, 0.4),
    ("hold_and_step_aside_1_lane", "one_lane_apart"): (True, True, False, False, False, False, 0.8),
    ("same_wall_dance", "aligned"): (False, False, False, False, True, True, None),
    ("same_wall_dance", "one_lane_apart"): (False, False, False, False, True, True, None),
    ("both_hold", "aligned"): (False, False, False, True, False, True, None),
    ("both_hold", "one_lane_apart"): (False, True, True, False, False, False, 0.4),
}
KEYS = ("resolved", "passed", "squeezed_past", "blocked_face_to_face", "dance", "deadlock", "passing_distance_m")


@pytest.mark.parametrize("script, geometry", sorted(EXPECTED))
def test_scripted_walkers_give_their_expected_outcomes(script, geometry):
    for seed in range(1, 6):
        outcome = M.pair_outcome(run_script(CONFIG, script, geometry, seed))
        assert tuple(outcome[k] for k in KEYS) == EXPECTED[(script, geometry)], (seed, outcome)


def test_keeping_right_moves_each_to_its_own_right():
    result = run_script(CONFIG, "keep_right", "aligned", 1)
    lanes = {wid: lane for wid, (_, lane) in result.ticks[25].positions.items()}
    assert lanes == {0: 1, 1: 3}   # walker 0's right is -y, walker 1's is +y
    assert result.ended_by == "all_arrived"


def test_the_dance_is_both_towards_the_same_wall_on_every_tick():
    outcome = M.pair_outcome(run_script(CONFIG, "same_wall_dance", "aligned", 1))
    assert outcome["dance_ticks"] == CONFIG.deadlock_ticks
    assert outcome["first_changes_towards_same_wall"] and not outcome["dance_into_same_lane"]
    assert outcome["walkers"]["0"]["lane_changes"] == CONFIG.deadlock_ticks


def test_random_walkers_keep_the_grids_invariants_and_rebuild_from_the_seed():
    for seed in range(1, 41):
        for geometry in C.GEOMETRIES:
            result = run_script(CONFIG, "random", geometry, seed)
            for before, after in zip(result.ticks, result.ticks[1:]):
                cells = list(after.positions.values())
                assert len(cells) == len(set(cells))
                for wid, (row, lane) in after.positions.items():
                    assert 0 <= row < CONFIG.rows and 0 <= lane < CONFIG.lanes
                    r0, l0 = before.positions[wid]
                    assert abs(row - r0) <= 1 and abs(lane - l0) <= 1
                if len(after.positions) == 2 and len(before.positions) == 2:
                    assert not (after.positions[0] == before.positions[1] and after.positions[1] == before.positions[0])
            again = run_script(CONFIG, "random", geometry, seed)
            assert [t.positions for t in again.ticks] == [t.positions for t in result.ticks]
    a, b = run_script(CONFIG, "random", "aligned", 1), run_script(CONFIG, "random", "aligned", 2)
    assert [t.positions for t in a.ticks] != [t.positions for t in b.ticks]


def test_a_run_needs_a_policy_for_every_walker():
    with pytest.raises(ConfigError, match="no policy"):
        run(head_on(CONFIG, (2, 2), 1), {0: W.hold_lane()})


# --- the measures ----------------------------------------------------------------------------


def _scripted(moves0, moves1, lanes=(2, 2), rows=(20, 23)):
    """A run from fixed move lists (then forward)."""
    s = state(Walker(0, rows[0], lanes[0], 1), Walker(1, rows[1], lanes[1], -1))
    plan = {0: list(moves0), 1: list(moves1)}

    def policy(st, me, rng):
        return plan[me.id].pop(0) if plan[me.id] else Move.FORWARD

    return run(s, {0: policy, 1: policy})


def test_sliding_past_diagonally_from_face_to_face_is_half_a_lane_each():
    # Rows 20 and 23, one lane: after one tick face to face (21, 22); then each slides diagonally
    # to its own left: they end two lanes apart, level halfway at one lane (0.4 m): squeezed.
    outcome = M.pair_outcome(_scripted([Move.FORWARD, Move.FORWARD_LEFT], [Move.FORWARD, Move.FORWARD_LEFT]))
    assert outcome["blocked_face_to_face"] and outcome["passed"]
    assert outcome["lanes_apart_when_passing"] == 1.0 and outcome["squeezed_past"] and not outcome["resolved"]


def test_level_side_by_side_uses_the_gap_when_level():
    # Rows 20 and 22, one lane apart; walker 1 slides to lane 4: level at row 21, two lanes apart.
    outcome = M.pair_outcome(_scripted([Move.FORWARD], [Move.FORWARD_RIGHT], lanes=(2, 3), rows=(20, 22)))
    assert outcome["lanes_apart_when_passing"] == 2.0 and outcome["passing_distance_m"] == 0.8 and outcome["resolved"]


def test_a_half_lane_passing_distance():
    # Diagonal neighbours one lane apart pass with walker 1 sliding one lane away: level halfway at 1.5 lanes.
    outcome = M.pair_outcome(_scripted([Move.FORWARD], [Move.FORWARD_RIGHT], lanes=(2, 3), rows=(20, 21)))
    assert outcome["lanes_apart_when_passing"] == 1.5 and outcome["passing_distance_m"] == 0.6
    assert not outcome["squeezed_past"] and outcome["resolved"]


def test_gate_columns_and_the_trajectory_analysis_lateral_reads():
    result = run_script(CONFIG, "hold_and_step_aside", "aligned", 1)
    outcome = M.pair_outcome(result)
    assert M.gate_columns(outcome) == {"outcome": "completed", "resolved_plan_only": "True", "collision_plan_only": "False"}
    lines = M.trajectory_csv(result).splitlines()
    assert lines[0] == "step,agent_id,x_m,y_m,row,lane"
    assert lines[1:3] == ["0,0,-7.800,0.000,5,2", "0,1,7.800,0.000,44,2"]


# --- round 1's cases on the grid (task 3) ----------------------------------------------------


def test_round1_cases_on_the_grid_and_what_rounding_loses():
    aligned, apart = C.round1_placements(CONFIG)
    assert aligned["layout"] == "aligned" and aligned["grid"]["lanes"] == [2, 2] and aligned["rounding_lost_m"] == [0.0, 0.0]
    # 20 cm apart rounds both to the centre lane: on the grid it is the aligned case.
    assert apart["layout"] == "apart_20cm" and apart["grid"]["lanes"] == [2, 2] and apart["rounding_lost_m"] == [0.1, 0.1]
    assert apart["continuous"]["width_m"] == 1.75 and apart["grid"]["width_m"] == 2.0
    assert C.lanes_for(CONFIG, "one_lane_apart") == (2, 1)
    assert C.lane_of(CONFIG, 0.2) == 3 and C.lane_of(CONFIG, -0.2) == 2   # half a lane rounds to +y
    assert C.lane_of(CONFIG, 5.0) == 4


def test_one_lane_apart_keeps_apart_20cms_sense():
    # In apart_20cm each sees the other to its own right; so on the grid.
    s = head_on(CONFIG, C.lanes_for(CONFIG, "one_lane_apart"), 1)
    assert W.other_ahead(s, s.walker(0))[1] < 0 and W.other_ahead(s, s.walker(1))[1] < 0


# --- the print, the entry point, and AS1 -----------------------------------------------------


def test_the_text_print():
    s = head_on(CONFIG, (2, 1), 1)
    text = R.frame(CONFIG, s.positions(), s.walkers, 0)
    lines = text.splitlines()
    assert len(lines) == CONFIG.lanes + 3 and lines[1] == "=" * (CONFIG.rows + 2)
    assert lines[4] == "|" + "." * 5 + "A" + "." * 44 + "|"      # lane 2
    assert lines[5] == "|" + "." * 44 + "B" + "." * 5 + "|"      # lane 1
    assert "A -> +x" in lines[0] and "B <- -x" in lines[0]


def test_the_entry_point(tmp_path, capsys):
    assert main(["cases"]) == 0 and "head_on_02dfbadb" in capsys.readouterr().out
    assert main(["run", "--script", "keep_right", "--seed", "2", "--out", str(tmp_path / "r")]) == 0
    record = json.loads((tmp_path / "r" / "outcome.json").read_text(encoding="utf-8"))
    assert record["outcome"]["resolved"] and record["grid"]["deadlock_ticks"] == 10
    assert (tmp_path / "r" / "trajectory.csv").is_file() and "ended by: all_arrived" in (tmp_path / "r" / "grid.txt").read_text(encoding="utf-8")
    assert main(["scripts", "--seeds", "2"]) == 0 and "| same_wall_dance | aligned | 0 |" in capsys.readouterr().out


def test_the_grid_is_an_add_on_nothing_else_imports_it():
    """AS1: the grid lives in its own files; no existing module reaches into it."""
    for path in (PACKAGE_ROOT / "negsim").rglob("*.py"):
        if "grid" in path.relative_to(PACKAGE_ROOT / "negsim").parts or "__pycache__" in path.parts:
            continue
        assert not re.search(r"negsim\.grid|from \.+grid\b", path.read_text(encoding="utf-8")), path
