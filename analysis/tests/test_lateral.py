"""The lateral separation when level (issue #65, RF-10), on replays made by hand."""

from __future__ import annotations

import csv

import pytest

from analysis import lateral

COLUMNS = ("session_id", "outcome", "repeat", "pair_id", "resolved_plan_only", "collision_plan_only")


def replay(folder, session_id, y0_end, y1_end):
    """Two walkers 10 m apart closing at 1 m/s each; each drifts linearly to its end y."""
    path = folder / "replay" / session_id / "plan_only"
    path.mkdir(parents=True)
    with (path / "trajectory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("step", "time_s", "agent_id", "x_m", "y_m"))
        for step in range(11):
            share = step / 10
            writer.writerow((step, step, 0, -5 + step, 0.1 + share * (y0_end - 0.1)))
            writer.writerow((step, step, 1, 5 - step, -0.1 + share * (y1_end + 0.1)))


@pytest.fixture
def experiment(tmp_path):
    rows = [
        {"session_id": "R", "outcome": "completed", "repeat": "1", "pair_id": "", "resolved_plan_only": "True", "collision_plan_only": "False"},
        {"session_id": "C", "outcome": "completed", "repeat": "1", "pair_id": "", "resolved_plan_only": "False", "collision_plan_only": "True"},
        {"session_id": "X", "outcome": "completed", "repeat": "2", "pair_id": "", "resolved_plan_only": "False", "collision_plan_only": "True"},
    ]
    with (tmp_path / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    replay(tmp_path, "R", 0.5, -0.5)   # each moves 0.4 m away from the other's line
    replay(tmp_path, "C", 0.1, -0.1)   # nobody moves
    return tmp_path


def test_it_measures_when_level_and_groups_the_designs_sessions_by_outcome(experiment):
    summary = lateral.summarise(experiment)
    assert set(summary) == {"resolved", "collision"} and summary["collision"]["sessions"] == 1  # the repeat is left out
    assert summary["resolved"]["separation_median_m"] == pytest.approx(0.6, abs=0.06)  # level at step 5: 0.3 - (-0.3)
    assert summary["resolved"]["aside_median_m"] == pytest.approx(0.2, abs=0.03)
    assert summary["collision"]["separation_median_m"] == pytest.approx(0.2) and summary["collision"]["aside_median_m"] == 0.0
    assert "| collision | 1 |" in lateral.markdown(summary)


def test_it_tells_making_room_from_both_stepping_towards_the_same_wall(experiment):
    rows = list(csv.DictReader((experiment / "outcomes.csv").open(encoding="utf-8", newline="")))
    rows.append({"session_id": "D", "outcome": "completed", "repeat": "1", "pair_id": "", "resolved_plan_only": "False", "collision_plan_only": "True"})
    with (experiment / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    replay(experiment, "D", 0.5, 0.3)  # agent 0 to its left (+y), agent 1 to its right (+y): the same wall
    summary = lateral.summarise(experiment)
    assert summary["resolved"]["sidesteps"] == {"same_own_side": 1, "towards_same_wall": 0, "not_both_aside": 0}
    assert summary["collision"]["sidesteps"] == {"same_own_side": 0, "towards_same_wall": 1, "not_both_aside": 1}
    assert "| collision | 0 | 1 | 1 |" in lateral.markdown(summary)


@pytest.mark.parametrize(
    ("own_0", "own_1", "kind"),
    [(0.3, 0.3, "same_own_side"), (-0.3, -0.2, "same_own_side"), (0.3, -0.3, "towards_same_wall"), (0.3, 0.04, "not_both_aside")],
)
def test_sidestep(own_0, own_1, kind):
    assert lateral.sidestep(own_0, own_1) == kind
