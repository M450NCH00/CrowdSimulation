"""The tables of the behaviour checks and the benchmark (issue #28, Verification): how a
spread and a side are computed, that the tables come from the committed logs, that the
document quoting them quotes them exactly, and that the benchmark runs."""

from __future__ import annotations

import csv
import json
import math

from negsim.configutil import PACKAGE_ROOT
from negsim.rules import benchmark
from negsim.rules.report import EXPERIMENTS, experiment_tables, main, report, side_passed, spread
from negsim.runlog.schema import AVOIDANCE_TRAJECTORY_COLUMNS

DOCUMENT = PACKAGE_ROOT / "docs" / "behaviour-checks.md"


def test_a_spread_is_the_mean_the_standard_deviation_and_the_range_if_there_is_one():
    assert spread([1.0, 2.0, 3.0], 2) == "2.00 ± 1.00 [1.00, 3.00]"
    assert spread([0.5, 0.5], 1) == "0.5 ± 0.0"  # no range when every value is the same
    assert spread([4.0], 1) == "4.0 ± 0.0"
    assert spread([None, 2.0, None, 4.0], 1) == "3.0 ± 1.4 [2.0, 4.0]"  # missing values are left out
    assert spread([None], 1) == spread([], 1) == "–"
    assert spread([1.0, 3.0], 1, ranged=False) == "2.0 ± 1.4"


def write_trajectory(path, points, theta):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, AVOIDANCE_TRAJECTORY_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for step, (x, y) in enumerate(points):
            writer.writerow({"step": step, "time_s": step / 10, "agent_id": 0, "x_m": x, "y_m": y, "theta_rad": theta})


def test_the_side_is_seen_from_the_agent_walking_its_own_way(tmp_path):
    cases = [
        ([(0, 0), (1, 0.2), (2, 0.3), (3, 0)], 0.0, "left"),  # walking +x, stepping to +y
        ([(0, 0), (1, -0.2), (2, -0.3), (3, 0)], 0.0, "right"),
        ([(0, 0), (-1, -0.2), (-2, -0.3), (-3, 0)], math.pi, "left"),  # walking -x, its left is -y
        ([(0, 0), (0.2, 1), (0.3, 2)], math.pi / 2, "right"),  # walking +y, its right is +x
        ([(0, 0), (1, 0.04), (2, -0.03)], 0.0, "none"),  # within 5 cm of its line
    ]
    for points, theta, expected in cases:
        write_trajectory(tmp_path / "trajectory.csv", points, theta)
        assert side_passed(tmp_path) == expected, (points, theta)


def test_an_experiment_with_no_runs_says_so(tmp_path):
    assert experiment_tables("si2_nothing", tmp_path) == ["### si2_nothing", "", "No runs found.", ""]


def test_the_tables_are_read_from_the_committed_logs():
    lines = experiment_tables("si2_keep_left_vs_right")
    assert lines[0] == "### si2_keep_left_vs_right"
    rows = [line for line in lines if line.startswith("| perturbed") or line.startswith("| unperturbed")]
    assert len(rows) == 8  # four conditions, in each of the two tables
    keep_left = next(row for row in rows if row.startswith("| perturbed, keep_left | 20 |"))
    assert "| 0 / 20 / 0 |" in keep_left and "keep_left_head_on@1 ×20 | left 20 |" in keep_left
    keep_right = next(row for row in rows if row.startswith("| unperturbed, keep_right | 20 |"))
    assert "keep_right_head_on@1 ×20 | right 20 |" in keep_right


def test_the_command_line_writes_the_tables(tmp_path):
    out = tmp_path / "tables.md"
    assert main(["si2_keep_left_vs_right", "--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == report(["si2_keep_left_vs_right"]) + "\n"


def test_the_benchmark_times_both_modes_and_the_provider(tmp_path):
    """A tiny flow, a few steps: what it measures, not how fast (it has no pass mark)."""
    out = tmp_path / "benchmark.json"
    assert benchmark.main(["--agents", "8", "--steps", "3", "--repeats", "2", "--out", str(out)]) == 0
    report_ = json.loads(out.read_text(encoding="utf-8"))
    assert report_["baseline"] == "orca_perturbed_v1" and report_["ruleset"] == "default"
    assert set(report_["git"]) == {"commit", "dirty"}
    (row,) = report_["results"]
    assert row["agents"] == 8 and row["steps_timed"] == 3 and row["repeats"] == 2
    assert len(row["plain"]["ms_per_step_mean_each"]) == len(row["rules"]["ms_per_step_mean_each"]) == 2
    rules = row["rules"]["first_repeat"]
    parts = rules["update_ms_per_step_mean"] + rules["directive_ms_per_step_mean"]
    assert abs(rules["provider_ms_per_step_mean"] - parts) <= 0.002  # the provider's time is its two parts (rounded)
    assert sum(rules["evaluations"].values()) > 0  # the matching policy did run
    assert "provider_ms_per_step_mean" not in row["plain"]["first_repeat"]


def test_the_behaviour_checks_document_quotes_every_table_exactly():
    """docs/behaviour-checks.md quotes the tables; regenerate them with
    ``python -m negsim.rules.report`` if the logs change."""
    document = set(DOCUMENT.read_text(encoding="utf-8").splitlines())
    lines = [line for line in report(EXPERIMENTS).splitlines() if line.strip()]
    missing = [line for line in lines if line not in document]  # whole lines, not parts of them
    assert not missing, missing[:3]
