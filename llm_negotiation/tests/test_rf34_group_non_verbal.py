"""Round 1 with three or four people, non-verbal (issue #115, RF-34): the config differs from RF-32's
run of record only in its condition, a non-verbal group session on the mock, and the analysis's
additions (round 1's pairs of one condition, the paired comparison, the later decision points)."""

from __future__ import annotations

import csv
import json

from negsim.configutil import load_yaml
from negsim.experiment.avoidance import simulation_for
from negsim.llm.mock import MockClient
from negsim.resolution import groups as G
from negsim.resolution import mock as M
from negsim.resolution import protocol as P
from negsim.resolution import scenarios as S
from negsim.rulegen.cases import CaseStore
from negsim.rulegen.protocol import LLMSettings
from negsim.rulegen.replay import source_plan

STORE = CaseStore()
TWO_V_ONE = STORE.get("group_75a57582", 1)
RF32 = "configs/resolution/round1_group_head_on_orca_groups.yaml"
RF34 = "configs/resolution/round1_group_head_on_non_verbal.yaml"


def test_the_config_is_rf32s_run_of_record_but_for_the_condition():
    rf32, rf34 = load_yaml(RF32), load_yaml(RF34)
    assert rf34["conditions"] == ["non_verbal"] and rf32["conditions"] == ["independent"]
    assert rf34["experiment_name"] == "rf34_round1_group_head_on_non_verbal"
    assert rf34["protocol"]["max_decision_points"] == 3 and rf34["protocol"]["orca_within_groups"] is True
    assert rf34["llm"]["client"] == "mock"  # the paid run names deepseek on the command line
    different = {"conditions", "experiment_name", "description", "budget"}
    assert {key: value for key, value in rf34.items() if key not in different} == {key: value for key, value in rf32.items() if key not in different}
    assert {k: v for k, v in rf34["budget"].items() if k != "cap_usd"} == {k: v for k, v in rf32["budget"].items() if k != "cap_usd"}


def session_on(case, answers):
    def answer(request):
        meta = request.metadata
        if meta.get("kind") == "debrief":
            return M.DEBRIEF_PATHS["with_source"]
        return answers.get((meta["agent_id"], meta.get("decision_point", 1)), answers.get(meta["agent_id"], M.CARRY_ON))
    run = P.EncounterSession(
        simulation_for(source_plan(case)), case["agents"], S.load_scenario("passing_group"), "non_verbal",
        MockClient(policy=answer), LLMSettings("deepseek-flash", 1.0, 300),
        P.ProtocolSettings(max_prompted=4, max_decision_points=3, execution="keep_line", orca_within_groups=True),
    )
    run.run_session()
    return run.as_dict()


def test_a_signal_is_seen_by_the_oncoming_person_not_by_the_friend_abreast():
    record = session_on(TWO_V_ONE, {0: M.RESOLVE_PATHS["signal_wave_on"]})
    made = [s for s in record["signals"] if s["signaller_id"] == 0]
    assert made and made[0]["seen_by"] == [2]  # the friend (1) walks abreast, outside the 75° view
    later = [p for p in record["decision_points"] if p["agent_id"] == 2 and "trigger" not in p["trigger_reasons"]]
    assert any(reason == "signalled:0" for p in later for reason in p["trigger_reasons"])
    counted = G.later_points(record)
    assert counted["signals"] == {"wave_on": len(made)} and counted["signals_seen_by"] == {"oncoming": len(made)}
    assert counted["reasons"].get("signalled:oncoming", 0) >= 1 and "signalled:friend" not in counted["reasons"]
    assert counted["later"] == len(record["decision_points"]) - 3


def test_later_points_split_by_friend_and_oncoming():
    record = {
        "encounter": {"pairs": [[0, 2], [1, 2]]},
        "decision_points": [
            {"agent_id": 0, "trigger_reasons": ["trigger", "perceives:2"]},
            {"agent_id": 2, "trigger_reasons": ["perceives:0"]},
            {"agent_id": 0, "trigger_reasons": ["came_into_view:1", "other_turned:2", "plan_failing"]},
            {"agent_id": 2, "trigger_reasons": ["signalled:1"], "parse_error": "x"},
        ],
        "signals": [{"signaller_id": 1, "signal": "nod", "seen_by": [2, 0]}],
    }
    found = G.later_points(record)
    assert found["later"] == 2 and found["later_readable"] == 1
    assert found["reasons"] == {"came_into_view:friend": 1, "other_turned:oncoming": 1, "plan_failing": 1, "signalled:oncoming": 1}
    assert found["signals"] == {"nod": 1} and found["signals_seen_by"] == {"oncoming": 1, "friend": 1}


def write_folder(folder, rows, sessions=None):
    folder.mkdir(parents=True, exist_ok=True)
    names = sorted({key for row in rows for key in row})
    with (folder / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)
    (folder / "sessions").mkdir(exist_ok=True)
    for row in rows:
        (folder / "sessions" / f"{row['session_id']}.json").write_text(json.dumps({"decision_points": [], "debriefs": []}), encoding="utf-8")
    if sessions is not None:
        (folder / "analysis").mkdir(exist_ok=True)
        (folder / "analysis" / "group_sessions.json").write_text(json.dumps(sessions), encoding="utf-8")


def test_round1_pairs_of_one_condition(tmp_path):
    base = {"pair_id": "", "repeat": "1", "case_geometry": "g", "passing_side_a_plan_only": "right", "passing_side_b_plan_only": "right"}
    write_folder(tmp_path, [
        {**base, "session_id": "N_a", "condition": "non_verbal", "resolved_plan_only": "True"},
        {**base, "session_id": "T_a", "condition": "talk", "resolved_plan_only": "False"},
        {**base, "session_id": "N_b", "condition": "non_verbal", "resolved_plan_only": "False", "repeat": "2"},
    ])
    assert [p["session_id"] for p in G.pair_sessions(tmp_path)] == ["N_a", "T_a"]
    assert [p["session_id"] for p in G.pair_sessions(tmp_path, "non_verbal")] == ["N_a"]


def test_the_paired_comparison_matches_cell_and_case_across_conditions(tmp_path):
    assert G.design_key("I_group_75a57582_2911fef8_r1") == G.design_key("N_group_75a57582_2911fef8_r1") == "group_75a57582_2911fef8_r1"
    independent = [("I_group_a_1_r1", True), ("I_group_a_2_r1", False), ("I_group_b_3_r1", False), ("I_group_b_4_r1", False), ("I_group_b_4_r2", True)]
    write_folder(
        tmp_path / "rf32",
        [{"session_id": s, "repeat": s[-1]} for s, _ in independent],
        [{"session_id": s, "resolved": {"plan_only": r}} for s, r in independent],
    )
    against = G.against_sessions(tmp_path / "rf32")
    assert against == {"group_a_1_r1": True, "group_a_2_r1": False, "group_b_3_r1": False, "group_b_4_r1": False}  # no exact-repeat copy
    design = [
        {"session_id": "N_group_a_1_r1", "layout": "2v1", "resolved": {"plan_only": True}},
        {"session_id": "N_group_a_2_r1", "layout": "2v1", "resolved": {"plan_only": True}},
        {"session_id": "N_group_b_3_r1", "layout": "2v2", "resolved": {"plan_only": True}},
        {"session_id": "N_group_b_4_r1", "layout": "2v2", "resolved": {"plan_only": False}},
        {"session_id": "N_group_c_5_r1", "layout": "2v2", "resolved": {"plan_only": True}},  # not in the other: left out
    ]
    found = G.paired(design, against)
    assert found["2v1"] == {"both": 1, "this_only": 1, "other_only": 0, "neither": 0, "n": 2, "sign_test_p": 1.0}
    assert found["all"] == {"both": 1, "this_only": 2, "other_only": 0, "neither": 1, "n": 4, "sign_test_p": 0.5}
