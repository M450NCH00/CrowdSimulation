"""The pilot's measures (issue #64, RF-9, task 4), on a two-session experiment folder made by hand."""

from __future__ import annotations

import csv
import json

import pytest

from analysis import pilot


def attempt(prompt, completion, hit=0, cost=0.001, finish="stop", parse_error=None, tier="off_peak"):
    return {"usage": {"prompt_tokens": prompt, "completion_tokens": completion, "prompt_cache_hit_tokens": hit,
                      "prompt_cache_miss_tokens": prompt - hit}, "cost_usd": cost, "price_tier": tier,
            "finish_reason": finish, "parse_error": parse_error, "api_error": None}


def record(session_id, condition, points, debriefs, signals=(), utterances=(), cost=0.0, calls=0):
    return {
        "session_id": session_id, "condition": condition, "outcome": "completed",
        "decision_points": points, "debriefs": debriefs, "signals": list(signals), "utterances": list(utterances),
        "encounter": {"prompted": [0, 1]}, "totals": {"llm_calls": calls, "cost_usd": cost},
    }


@pytest.fixture
def experiment(tmp_path):
    folder = tmp_path / "rf_pilot"
    (folder / "sessions").mkdir(parents=True)
    independent = record("I_1", "independent", [
        {"agent_id": 0, "trigger_reasons": ["trigger", "perceives:1"], "attempts": [attempt(1000, 100, hit=500)]},
        {"agent_id": 1, "trigger_reasons": ["perceives:0"], "attempts": [attempt(1000, 400, finish="length", parse_error="not_json: cut off"),
                                                                          attempt(1100, 80)]},
    ], [{"attempts": [attempt(1500, 60)]}], cost=0.004, calls=4)
    talk = record("T_1", "talk", [
        {"agent_id": 0, "trigger_reasons": ["trigger"], "attempts": [attempt(900, 90)]},
        {"agent_id": 0, "trigger_reasons": ["signalled"], "attempts": [attempt(1200, 90, hit=1000)]},
    ], [], signals=[{"signal": "nod"}, {"signal": "nod"}, {"signal": "wave_on"}], utterances=[{"message": "Sorry."}], cost=0.002, calls=2)
    for rec in (independent, talk):
        (folder / "sessions" / f"{rec['session_id']}.json").write_text(json.dumps(rec), encoding="utf-8")
    (folder / "preview.json").write_text(json.dumps({
        "usd_total": 0.2, "reply_cap_tokens": 400, "sends_per_call": 6,
        "per_session": [
            {"session_id": "I_1", "calls": 4, "usd_bound": 0.04, "S_decision_tokens": 2000, "S_debrief_tokens": 3000},
            {"session_id": "T_1", "calls": 8, "usd_bound": 0.16, "S_decision_tokens": 2400, "S_debrief_tokens": 3000},
        ],
    }), encoding="utf-8")
    columns = ["condition", "resolved_by_llm"]
    for mode in pilot.MODES:
        columns += [f"run_status_{mode}", f"resolved_{mode}", f"collision_{mode}", f"near_miss_{mode}", f"who_passed_first_{mode}",
                    f"passing_side_a_{mode}", f"passing_side_b_{mode}"]
    rows = [
        {"condition": "independent", "resolved_by_llm": "True", **{f"run_status_{m}": "completed" for m in pilot.MODES},
         "resolved_plan_only": "True", "who_passed_first_plan_only": "0", "passing_side_a_plan_only": "left", "passing_side_b_plan_only": "left"},
        {"condition": "talk", "resolved_by_llm": "False", **{f"run_status_{m}": "completed" for m in pilot.MODES},
         "collision_plan_only": "True"},
    ]
    with (folder / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, columns, restval="")
        writer.writeheader()
        writer.writerows(rows)
    return folder


def test_tokens_cost_and_cache_are_counted_per_kind_of_call(experiment):
    measured = pilot.measure(experiment)
    decision, debrief = measured["per_kind"]["decision"], measured["per_kind"]["debrief"]
    assert decision["sends"] == 5 and debrief["sends"] == 1
    assert decision["prompt_tokens"]["max"] == 1200 and decision["completion_tokens"]["max"] == 400
    assert decision["cut_off_at_reply_cap"] == 1
    assert decision["cache_hit_share"] == pytest.approx(1500 / 5200, abs=1e-4)
    assert decision["largest_share_of_the_bound_on_one_prompt"] == pytest.approx(0.55)  # 1100 / 2000
    assert debrief["largest_share_of_the_bound_on_one_prompt"] == pytest.approx(0.5)
    assert measured["cost_usd"] == pytest.approx(0.006) and measured["sends_by_price_tier"] == {"off_peak": 6}
    assert measured["cache_hit_share_of_input"] == pytest.approx(1500 / 6700, abs=1e-4)
    assert measured["unreadable_sends"] == {"decision:not_json": 1}


def test_per_condition_calls_decision_points_triggers_and_signals(experiment):
    measured = pilot.measure(experiment)
    independent, talk = measured["per_condition"]["independent"], measured["per_condition"]["talk"]
    assert independent["decision_points_per_agent"] == {1: 2}
    assert talk["decision_points_per_agent"] == {0: 1, 2: 1}  # agent 1 was prompted but never asked
    assert independent["trigger_reasons"] == {"perceives": 2, "trigger": 1}
    assert talk["signals"] == {"nod": 2, "wave_on": 1} and talk["messages"] == 1 and independent["messages"] == 0
    assert independent["largest_share_of_a_session_preview"] == pytest.approx(0.1) and talk["calls_bound_per_session"] == 8


def test_passing_and_the_report(experiment, tmp_path):
    measured = pilot.measure(experiment)
    assert measured["passing"]["plan_only/independent"]["who_passed_first"] == {"0": 1}
    assert measured["passing"]["plan_only/independent"]["passing_sides"] == {"left/left": 1}
    assert measured["passing"]["plan_only/talk"]["collision"] == 1 and measured["passing"]["plan_only/talk"]["who_passed_first"] == {"none": 1}
    assert measured["passing"]["resolved_by_llm"] == {"independent": 1, "talk": 0}
    assert pilot.main([str(experiment), "--out", str(tmp_path / "out")]) == 0
    text = (tmp_path / "out" / "pilot_measures.md").read_text(encoding="utf-8")
    assert "## Tokens per send" in text and "each up to 6 sends" in text and "decision:not_json: 1" in text
    assert json.loads((tmp_path / "out" / "pilot_measures.json").read_text(encoding="utf-8"))["experiment"] == "rf_pilot"
