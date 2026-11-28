"""Issue #155 (RF-54): how a head-on pair started, and whether both changed wall at once."""

from __future__ import annotations

import csv
import json

from analysis import start_walls as W


def step(side):
    return {"start": "now", "speed_mps": 1.0, "sidestep": {"to": side, "metres": 0.4}}


def decision(sid, agent, number, time_s, *steps):
    return {"session_id": sid, "agent_id": agent, "number": number, "time_s": time_s, "steps": list(steps)}


def write_run(folder, sessions):
    folder.mkdir()
    rows = [{"session_id": sid, "condition": "silent", "outcome": "completed", "resolved_plan_only": str(ok)} for sid, (ok, _) in sessions.items()]
    rows.append({"session_id": "S_pair_x1", "condition": "silent", "outcome": "completed", "resolved_plan_only": "True"})
    rows.append({"session_id": "S_talk", "condition": "talk", "outcome": "completed", "resolved_plan_only": "True"})
    with (folder / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (folder / "decisions.jsonl").open("w", encoding="utf-8") as handle:
        for _, (_, decisions) in sessions.items():
            for d in decisions:
                handle.write(json.dumps(d) + "\n")
    return folder


def test_walls_follow_each_agents_facing():
    # Agent 0's right and agent 1's left are both the -y wall.
    assert W.sidesteps([decision("s", 0, 1, 2.4, step("right"))]) == [(2.4, -1)]
    assert W.sidesteps([decision("s", 1, 1, 2.4, step("left"))]) == [(2.4, -1)]
    assert W.classify({0: [decision("s", 0, 1, 2.4, step("right"))], 1: [decision("s", 1, 1, 2.4, step("left"))]})["start"] == "same_wall"
    assert W.classify({0: [decision("s", 0, 1, 2.4, step("right"))], 1: [decision("s", 1, 1, 2.4, step("right"))]})["start"] == "opposite_walls"
    assert W.classify({0: [decision("s", 0, 1, 2.4, {"speed_mps": 1.0, "until": "other_passes"})], 1: []})["start"] == "one_never_sidesteps"


def test_a_dance_is_both_changing_wall_at_the_same_decision_time():
    a = [decision("s", 0, 1, 2.4, step("right")), decision("s", 0, 2, 3.4, step("left"))]
    b = [decision("s", 1, 1, 2.4, step("left")), decision("s", 1, 2, 3.4, step("right"))]
    assert W.classify({0: a, 1: b}) == {"start": "same_wall", "dance": True, "reversed": True}
    late = [decision("s", 1, 1, 2.4, step("left")), decision("s", 1, 2, 4.4, step("right"))]
    assert W.classify({0: a, 1: late})["dance"] is False
    # The turn-taking exchange may ask the second person 0.1 s after the first: still at once.
    next_step = [decision("s", 1, 1, 2.4, step("left")), decision("s", 1, 2, 3.5, step("right"))]
    assert W.classify({0: a, 1: next_step})["dance"] is True


def test_the_table_counts_design_sessions_only_and_pairs_by_id(tmp_path):
    same = [decision("S1", 0, 1, 2.4, step("right")), decision("S1", 1, 1, 2.4, step("left"))]
    opposite = [decision("S2", 0, 1, 2.4, step("left")), decision("S2", 1, 1, 2.4, step("left"))]
    base = write_run(tmp_path / "base", {"S1": (False, same), "S2": (True, opposite)})
    fixed = [decision("S1", 0, 1, 2.4, step("right")), decision("S1", 1, 1, 2.4, step("right"))]
    new = write_run(tmp_path / "new", {"S1": (True, fixed), "S2": (True, opposite)})
    counts = W.table(W.sessions(base))
    assert counts["same_wall"] == {"n": 1, "resolved": 0, "dance": 0, "dance_failed": 0}
    assert counts["opposite_walls"]["n"] == 1 and counts["one_never_sidesteps"]["n"] == 0
    assert W.paired(W.sessions(base), W.sessions(new)) == {"n": 2, "start_moves": {"opposite_walls -> opposite_walls": 1, "same_wall -> opposite_walls": 1}}
    assert "| same_wall | 1 (0.50) | 0 (0.00) | 0 | 0 |" in W.markdown("base", counts)
