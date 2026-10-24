"""The resolution gate (issue #65, RF-10), on an experiment folder made by hand."""

from __future__ import annotations

import csv
import json

import pytest

from analysis import gate

COLUMNS = ("session_id", "outcome", "condition", "geometry", "repeat", "pair_id",
           "resolved_plan_only", "resolved_plan_orca", "resolved_plain_orca")
GATE = {"plan_only_resolved_min": 0.5, "reason": "More often than not."}


def row(session_id, condition, resolved, geometry="aligned", repeat=1, pair_id="", outcome="completed", orca=False):
    return {"session_id": session_id, "outcome": outcome, "condition": condition, "geometry": geometry, "repeat": str(repeat),
            "pair_id": pair_id, "resolved_plan_only": str(resolved), "resolved_plan_orca": str(resolved or orca),
            "resolved_plain_orca": "False"}


def folder(tmp_path, rows, fixed=GATE):
    path = tmp_path / "rf10"
    path.mkdir()
    experiment = {"experiment_name": "rf10", **({"resolution_gate": fixed} if fixed else {})}
    (path / "config.json").write_text(json.dumps({"experiment": experiment}), encoding="utf-8")
    with (path / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


DESIGN = [row("I1", "independent", True), row("I2", "independent", True, geometry="apart"),
          row("T1", "talk", False), row("T2", "talk", True, geometry="apart")]


def test_the_gate_counts_only_the_designs_completed_sessions_against_the_fixed_threshold(tmp_path):
    extra = [row("I1r2", "independent", False, repeat=2), row("I1r3", "independent", False, repeat=3),  # exact repeats
             row("P1", "talk", False, pair_id="p"), row("P2", "talk", False, pair_id="p"),           # a counterfactual pair
             row("A1", "talk", False, outcome="aborted")]
    result = gate.gate(folder(tmp_path, DESIGN + extra))
    assert result["plan_only"]["resolved"] == 3 and result["plan_only"]["n"] == 4 and result["passes"]
    assert result["threshold"] == 0.5 and result["reason"] == "More often than not."
    assert result["by_condition"]["talk"]["resolved"] == 1 and result["by_geometry"]["apart"]["n"] == 2
    assert result["design_sessions_not_completed"] == {"aborted": 1}
    assert result["baselines"]["plain_orca"]["resolved"] == 0


def test_below_the_threshold_it_fails(tmp_path):
    rows = [row("I1", "independent", True)] + [row(f"T{k}", "talk", False) for k in range(3)]
    result = gate.gate(folder(tmp_path, rows))
    assert result["plan_only"]["rate"] == 0.25 and not result["passes"]
    assert "**fails**" in gate.markdown(result)


def test_without_a_gate_fixed_before_the_run_there_is_nothing_to_apply(tmp_path):
    with pytest.raises(gate.GateError, match="fixed no resolution_gate"):
        gate.gate(folder(tmp_path, DESIGN, fixed=None))


def test_the_command_writes_gate_json_and_gate_md(tmp_path):
    path = folder(tmp_path, DESIGN)
    assert gate.main([str(path)]) == 0
    assert json.loads((path / "analysis" / "gate.json").read_text(encoding="utf-8"))["passes"] is True
    assert "passes" in (path / "analysis" / "gate.md").read_text(encoding="utf-8")
