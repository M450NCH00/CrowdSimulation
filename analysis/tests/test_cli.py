"""``python -m analysis <outcomes.csv>`` writes the report, the tree and the mapping (issue #63,
acceptance criterion 1)."""

from __future__ import annotations

import json
import subprocess
import sys

from analysis import cli
from conftest import ROOT
from synthetic import screen, write_csv

FILES = ("report.md", "agents.csv", "effects_terms.csv", "effects_models.csv", "tree.txt", "tree.png", "mapping.csv",
         "noise_floor.csv", "flip_rates.csv", "stability.csv", "reason_mentions.csv", "debrief_kinds.csv", "stated_vs_measured.csv",
         "intent_check.csv", "intent_summary.csv")


def decisions_for(rows):
    return [{"session_id": r["session_id"], "agent_id": r[f"{p}_agent"], "number": 1, "condition": r["condition"], "parse_error": None,
             "intent": "Move over to my left.", "reason": "They have a suitcase.",
             "coded": {"carry_on": False, "side": "left", "slowed": False, "stopped": False, "backed_up": False}}
            for r in rows for p in ("p1", "p2")]


def test_python_m_analysis_writes_the_report_the_tree_and_the_mapping(tmp_path):
    rows = screen(seed=7, sessions_per_condition=80, urgency_effect=2.0)
    path = write_csv(rows, tmp_path / "exp" / "outcomes.csv", decisions_for(rows))
    (tmp_path / "exp" / "config.json").write_text(json.dumps({"client_name": "mock"}), encoding="utf-8")
    done = subprocess.run([sys.executable, "-m", "analysis", str(path)], cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    out = tmp_path / "exp" / "analysis"
    for name in FILES:
        assert (out / name).is_file(), name
    report = (out / "report.md").read_text(encoding="utf-8")
    for heading in ("## 1. Factor effects", "## 2. Decision tree", "## 3. Counterfactual pairs", "## 4. Behaviour stability",
                    "## 5. The factor-to-decision mapping", "## 6. Stated against measured", "## 7. Intent against plan"):
        assert heading in report
    assert "Made with the mock client" in report and "own_urgency" in report
    assert "|--- " in (out / "tree.txt").read_text(encoding="utf-8")
    assert (out / "tree.png").read_bytes()[:4] == b"\x89PNG"


def test_a_bad_input_is_an_error_message_not_a_traceback(tmp_path):
    done = subprocess.run([sys.executable, "-m", "analysis", str(tmp_path / "missing.csv")], cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 2 and done.stderr.startswith("error:") and "Traceback" not in done.stderr


def test_several_files_are_analysed_together_and_their_session_ids_kept_apart(tmp_path):
    rows = screen(seed=8, sessions_per_condition=40)
    first, second = write_csv(rows, tmp_path / "a" / "outcomes.csv"), write_csv(rows, tmp_path / "b" / "outcomes.csv")
    results = cli.analyse([first, second])
    assert len(results.sessions) == 2 * len(rows) and results.sessions["session_key"].is_unique
    written = cli.write(results, tmp_path / "out")
    assert {p.name for p in written} >= {"report.md", "mapping.csv", "tree.txt"}
    assert "No `decisions.jsonl` beside the outcomes" in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
