"""Issue #122 (RF-37): the human-target measures, on hand-built trajectories whose answers are known."""

from __future__ import annotations

import json

import pytest

from negsim.human_targets import measures as M

DT = 0.1


def _run(tmp_path, rows, agents, stride=1, scenario_type="wide_corridor_head_on", width=1.75):
    tmp_path.mkdir(parents=True, exist_ok=True)
    config = {"logging": {"trajectory_stride": stride},
              "scenario": {"type": scenario_type, "geometry": {"width": width}, "agents": agents}}
    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")
    lines = ["step,time_s,agent_id,x_m,y_m,vx_mps,vy_mps,speed_mps"]
    lines += [",".join(str(v) for v in row) for row in rows]
    (tmp_path / "trajectory.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return tmp_path


def _agent(agent_id, start, goal):
    return {"agent_id": agent_id, "start": {"x": start[0], "y": start[1]}, "goal": {"x": goal[0], "y": goal[1]},
            "path": [list(start), list(goal)]}


def _head_on(tmp_path, dip=False):
    """Agent 0 walks straight east at 1 m/s from x = -5; agent 1 walks west from x = 5 and, between
    2 and 3 m along its path, moves 0.6 m to +y (its own right) and stays there. They are abreast at
    t = 5 s, 0.6 m apart. With ``dip``, agent 0's logged speed drops to 0.8 m/s on steps 40 to 45."""
    rows = []
    for step in range(101):
        t = round(step * DT, 6)
        speed0 = 0.8 if dip and 40 <= step <= 45 else 1.0
        y1 = min(max(t - 2.0, 0.0), 1.0) * 0.6
        rows.append((step, t, 0, round(-5 + t, 6), 0.0, 1.0, 0.0, speed0))
        rows.append((step, t, 1, round(5 - t, 6), round(y1, 6), -1.0, 0.0, 1.0))
    return _run(tmp_path, rows, [_agent(0, (-5, 0), (5, 0)), _agent(1, (5, 0), (-5, 0))])


def test_the_pair_measures_of_a_known_meeting(tmp_path):
    found = M.pair_measures(_head_on(tmp_path, dip=True))
    assert found["min_centre_distance_m"] == pytest.approx(0.6)
    assert found["pomd_time_s"] == pytest.approx(5.0)
    zero, one = found["per_agent"]["0"], found["per_agent"]["1"]
    assert zero["lateral_deviation_max_m"] == 0.0 and one["lateral_deviation_max_m"] == pytest.approx(0.6)
    assert zero["lateral_share"] == 0.0 and one["lateral_share"] == 1.0
    assert zero["turning_start_m"] is None                   # it never turned
    assert one["turning_start_m"] == pytest.approx(3.0)      # turned at 2 m along, abreast at 5 m
    assert zero["speed_change_mps"] == pytest.approx(0.2) and one["speed_change_mps"] == 0.0
    assert zero["side"] == "right" and one["side"] == "right"  # the other went by on each one's left
    assert found["passed_first"] == M.TOGETHER


def test_who_passed_first_and_the_side_kept_to_the_left(tmp_path):
    rows = []
    for step in range(101):
        t = round(step * DT, 6)
        rows.append((step, t, 0, round(-5 + t, 6), 0.3, 1.0, 0.0, 1.0))     # 0.3 m to its own left
        rows.append((step, t, 1, round(5 - 1.2 * t, 6), 0.0, -1.2, 0.0, 1.2))  # faster
    found = M.pair_measures(_run(tmp_path, rows, [_agent(0, (-5, 0.3), (5, 0.3)), _agent(1, (5, 0), (-5, 0))]))
    assert found["per_agent"]["0"]["side"] == "left"    # the other is on its right
    assert found["per_agent"]["1"]["side"] == "left"    # agent 0 is at +y, on agent 1's right
    assert found["per_agent"]["0"]["lateral_deviation_max_m"] == 0.0  # measured from its own start
    assert found["per_agent"]["0"]["lateral_share"] is None            # neither deviated
    assert found["passed_first"] == 1


def test_a_turn_slower_than_the_floor_is_not_a_turn(tmp_path):
    rows = []
    for step in range(101):
        t = round(step * DT, 6)
        rows.append((step, t, 0, round(-5 + t, 6), round(0.002 * t * t, 8), 1.0, 0.0, 1.0))  # a drift turning at 0.004 rad/s
        rows.append((step, t, 1, round(5 - t, 6), 1.0, -1.0, 0.0, 1.0))
    run = _run(tmp_path, rows, [_agent(0, (-5, 0), (5, 0)), _agent(1, (5, 1), (-5, 1))])
    assert M.pair_measures(run)["per_agent"]["0"]["turning_start_m"] is None
    assert M.pair_measures(run, floor=0.001)["per_agent"]["0"]["turning_start_m"] is not None


def test_the_pair_measures_need_every_step(tmp_path):
    run = _head_on(tmp_path)
    config = json.loads((run / "config.json").read_text(encoding="utf-8"))
    config["logging"]["trajectory_stride"] = 10
    (run / "config.json").write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="every step"):
        M.pair_measures(run)


def test_the_row_written_on_arrival_is_left_out(tmp_path):
    run = _head_on(tmp_path)
    with (run / "trajectory.csv").open("a", encoding="utf-8") as handle:
        handle.write("101,10.1,1,-5.1,0.6,,,\n")
    assert len(M.read_tracks(run)[1]) == 101


def test_speed_by_density_counts_the_people_in_the_measuring_area(tmp_path):
    rows = [
        (0, 0.0, 0, -0.5, 1.0, 1.0, 0.0, 1.0),
        (0, 0.0, 1, 0.9, -1.0, -1.2, 0.0, 1.2),
        (0, 0.0, 2, 3.0, 0.0, 1.0, 0.0, 1.0),     # outside |x| <= 1 m
        (10, 1.0, 0, 0.5, 1.0, 0.6, 0.0, 0.6),
        (20, 2.0, 0, 5.0, 1.0, 1.0, 0.0, 1.0),    # nobody inside: no sample
    ]
    run = _run(tmp_path, rows, [_agent(i, (-10, 0), (10, 0)) for i in range(3)], stride=10, scenario_type="bidirectional_flow", width=4.0)
    assert M.speed_by_density(run) == [(0.25, 1.1), (0.125, 0.6)]   # 2 and 1 people over 2 m x 4 m
