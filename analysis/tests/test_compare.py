"""Two runs of the same sessions compared cell for cell (issue #98, RF-27), on experiments made by hand."""

from __future__ import annotations

import csv
import json
from math import comb

import pytest

from analysis import compare

COLUMNS = ("session_id", "outcome", "condition", "repeat", "exact_repeat_set", "geometry", "pair_id", "resolved_plan_only", "collision_plan_only")


def replay(folder, session_id, y0_end, y1_end):
    """Two walkers 10 m apart closing at 1 m/s each; each drifts linearly to its end y (as test_lateral)."""
    path = folder / "replay" / session_id / "plan_only"
    path.mkdir(parents=True)
    with (path / "trajectory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("step", "time_s", "agent_id", "x_m", "y_m"))
        for step in range(11):
            share = step / 10
            writer.writerow((step, step, 0, -5 + step, 0.1 + share * (y0_end - 0.1)))
            writer.writerow((step, step, 1, 5 - step, -0.1 + share * (y1_end + 0.1)))


def experiment(folder, outcomes, model="m", unreadable=()):
    """``outcomes``: session id -> (resolved, condition, repeat, exact_repeat_set)."""
    folder.mkdir()
    (folder / "sessions").mkdir()
    rows = []
    for session_id, (resolved, condition, repeat, exact) in outcomes.items():
        rows.append({
            "session_id": session_id, "outcome": "completed", "condition": condition, "repeat": str(repeat),
            "exact_repeat_set": str(exact), "geometry": "layout=aligned", "pair_id": "",
            "resolved_plan_only": str(resolved), "collision_plan_only": str(not resolved),
        })
        # Making room when resolved; both towards the same wall (+y) when not.
        replay(folder, session_id, 0.5, -0.5) if resolved else replay(folder, session_id, 0.5, 0.3)
        point = {"parse_error": "bad" if session_id in unreadable else None, "attempts": [{"model": model, "system_fingerprint": "fp"}]}
        record = {"decision_points": [point, dict(point, parse_error=None)], "templates": {"core": {"key": "resolve_x"}}}
        (folder / "sessions" / f"{session_id}.json").write_text(json.dumps(record), encoding="utf-8")
    with (folder / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return folder


@pytest.fixture
def pair(tmp_path):
    ids = [f"I_c{k}_r1" for k in range(6)]
    base = {s: (k < 2, "independent", 1, False) for k, s in enumerate(ids)}
    new = {s: (k < 5, "independent", 1, False) for k, s in enumerate(ids)}
    # An exact-repeat cell: three runs, stable in the second experiment only.
    for r, (b, n) in enumerate([(True, True), (False, True), (True, True)], start=1):
        sid = f"I_rep_r{r}"
        base[sid], new[sid] = (b, "independent", r, True), (n, "independent", r, True)
    base["T_c0_r1"] = new["T_c0_r1"] = (True, "talk", 1, False)  # another condition: left out
    return experiment(tmp_path / "base", base, unreadable={"I_c0_r1"}), experiment(tmp_path / "new", new, model="m2")


def test_the_same_sessions_are_paired_and_counted(pair):
    result = compare.compare(*pair, "independent")
    assert result["sessions_in_common"] == 9 and result["design_sessions"] == 7  # the repeat's runs 2 and 3 are not the design's
    assert result["rate"]["base"]["resolved"] == 3 and result["rate"]["new"]["resolved"] == 6
    assert result["paired"] == {"both": 3, "only_base": 0, "only_new": 3, "neither": 1, "mcnemar_p": 0.25}
    assert result["stability"]["base"] == {"cells": 1, "same_in_every_run": 0, "runs": 3}
    assert result["stability"]["new"] == {"cells": 1, "same_in_every_run": 1, "runs": 3}
    assert result["sessions"]["base"]["unreadable"] == 1 and "m2 / fp" in result["sessions"]["new"]["models"]
    assert result["sidesteps"]["base"]["collision"] == {"same_own_side": 0, "towards_same_wall": 4, "not_both_aside": 0}
    assert result["sidesteps"]["new"]["resolved"] == {"same_own_side": 6, "towards_same_wall": 0, "not_both_aside": 0}
    text = compare.markdown(result)
    assert "| resolved in the first | 3 | 0 |" in text and "p = 0.2500" in text


@pytest.mark.parametrize(("b", "c"), [(0, 0), (0, 3), (3, 0), (2, 7), (19, 4), (5, 5)])
def test_mcnemar_is_the_two_sided_exact_binomial(b, c):
    n = b + c
    expected = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(min(b, c) + 1)) / 2**n)
    assert compare.mcnemar_exact(b, c) == pytest.approx(expected)
    assert compare.mcnemar_exact(b, c) == compare.mcnemar_exact(c, b)


def test_readable_only_leaves_out_a_session_unreadable_in_either_run(pair):
    result = compare.compare(*pair, "independent", readable_only=True)
    assert result["readable_only"] and result["dropped_unreadable"] == 1  # I_c0_r1, unreadable in the first run
    assert result["sessions_in_common"] == 8 and result["design_sessions"] == 6
    assert result["paired"]["both"] == 2 and result["paired"]["only_new"] == 3
    assert "Readable only:** 1 session(s)" in compare.markdown(result)
    assert not compare.compare(*pair, "independent")["readable_only"]


def test_two_experiments_with_nothing_in_common_are_refused(pair, tmp_path):
    other = experiment(tmp_path / "other", {"I_x_r1": (True, "independent", 1, False)})
    with pytest.raises(compare.CompareError):
        compare.compare(pair[0], other, "independent")
