"""Issue #66 (RF-11): the rule extractor, on hand-made sources, on round 1's data and on the mock."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pytest

from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.extraction import experiment as X
from negsim.extraction import rules as R
from negsim.extraction import table as T
from negsim.extraction.mock import POLICIES as MOCK_POLICIES
from negsim.extraction.prompt import ExtractTemplate, render, sample_sessions
from negsim.llm.budget import BudgetedClient, BudgetGuard, SpendLedger
from negsim.llm.mock import MockClient
from negsim.llm.pricing import PriceTable

GIT = {"commit": "test", "dirty": False}
ROUND1 = ("runs/rf10_round1_head_on_keep_line", "runs/rf30_round1_head_on_keep_line")
GATE = {"plan_only_resolved_min": 0.5, "reason": "test"}


# --- hand-made sources -----------------------------------------------------------------------------


def outcome_row(session_id, condition="independent", resolved=True, encounter_type="head_on", **changes):
    """One outcomes.csv row with the columns the extractor reads; person 1 is agent 0."""
    row = {
        "session_id": session_id, "outcome": "completed", "case_id": "head_on_x", "geometry": "layout=aligned",
        "encounter_type": encounter_type, "condition": condition, "repeat": "1", "exact_repeat_set": "False", "pair_id": "",
        "p1_agent": "0", "p2_agent": "1", "encounter_agents": "0;1", "demographics_visible": "True",
        "p1_age": "25", "p2_age": "70", "p1_gender": "female", "p2_gender": "male",
        "p1_other_age_shown": "1", "p2_other_age_shown": "0", "p1_other_gender_shown": "1", "p2_other_gender_shown": "1",
        "p1_other_observable_shown": "1", "p2_other_observable_shown": "1", "p1_other_ethnicity_shown": "1", "p2_other_ethnicity_shown": "0",
        "p1_pairwise_lines_shown": "1", "p2_pairwise_lines_shown": "1", "p1_finds_other_attractive": "1", "p2_finds_other_attractive": "0",
        "p1_knows_other": "0", "p2_knows_other": "0", "p1_ethnicity": "chinese", "p2_ethnicity": "malay",
        "surroundings": "quiet", "time_of_day": "daytime",
        "p1_decision_points": "1", "p2_decision_points": "1", "p1_signals": "", "p2_signals": "", "p1_messages": "0", "p2_messages": "0",
        "p1_debrief_kind": "habit", "p2_debrief_kind": "common_sense",
        "p1_first_side": "right", "p2_first_side": "right", "p1_first_slowed": "False", "p2_first_slowed": "True",
        "p1_first_stopped": "False", "p2_first_stopped": "False", "p1_first_backed_up": "False", "p2_first_backed_up": "False",
        "p1_first_start_distance_m": "", "p2_first_start_distance_m": "", "p1_final_side": "right", "p2_final_side": "right",
        "who_passed_first_plan_only": "together", "passing_side_a_plan_only": "right", "passing_side_b_plan_only": "right",
        "stopped_a_plan_only": "False", "stopped_b_plan_only": "False", "backed_up_a_plan_only": "False", "backed_up_b_plan_only": "False",
        "collision_plan_only": "False" if resolved else "True", "near_miss_plan_only": "False", "deadlock_plan_only": "False",
        "resolved_plan_only": "True" if resolved else "False",
        "age_pair": "p1_older", "load": "neither", "p1_load": "none", "p2_load": "large_suitcase",
        "p1_mobility_aid": "none", "p2_mobility_aid": "none", "p1_distraction": "none", "p2_distraction": "none",
    }
    row.update(changes)
    return row


def record_for(row):
    """A session record with one decision point per person, its view and a debrief."""
    points = []
    for agent, partner in ((0, 1), (1, 0)):
        points.append({
            "agent_id": agent, "partner_id": partner, "number": 1, "trigger_reasons": ["trigger", f"perceives:{partner}"],
            "view": {"labels": {"label_of_agent": {str(partner): 1}}, "seen": [{"label": 1, "distance_m": 9.76}]},
            "parsed": {"intent": f"agent {agent} keeps right", "steps": [{"speed_mps": 1.2, "turn": {"to": "right", "degrees": 10}}],
                       "signal": "none", "message": None, "reason": "private"},
        })
    debriefs = [{"agent_id": a, "parsed": {"kind": "habit", "basis": "keep right", "source": None}} for a in (0, 1)]
    return {"session_id": row["session_id"], "decision_points": points, "debriefs": debriefs}


def make_source(folder: Path, rows, gate=GATE):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "sessions").mkdir(exist_ok=True)
    experiment = {"experiment_name": folder.name}
    if gate is not None:
        experiment["resolution_gate"] = gate
    (folder / "config.json").write_text(json.dumps({"layer": "resolution", "client_name": "mock", "experiment": experiment}), encoding="utf-8")
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with (folder / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        (folder / "sessions" / f"{row['session_id']}.json").write_text(json.dumps(record_for(row)), encoding="utf-8")
    return folder


def hand_made(tmp_path, resolved=12, failed=4):
    rows = [outcome_row(f"I_s{i:02d}_r1") for i in range(resolved)]
    rows += [outcome_row(f"I_f{i:02d}_r1", resolved=False, p1_first_side="left") for i in range(failed)]
    rows += [outcome_row("I_s00_r2", repeat="2"), outcome_row("I_x_pair", pair_id="I_x")]  # neither is a design session
    return make_source(tmp_path / "src", rows)


def config_for(sources, name="ext", **changes):
    raw = {
        "layer": "rule_extraction", "experiment_name": name, "sources": [str(s) for s in sources],
        "encounter_descriptions": {"head_on": "Two people meet head-on.", "overtaking": "One passes another."},
        "runs": {"seeds": [1, 2, 3]}, "sample": {"size": 10},
        "llm": {"client": "mock", "mock_policy": "extract_rehearsal_v1"}, "budget": {"cap_usd": 0.05},
    }
    raw.update(changes)
    return X.ExtractionConfig.from_raw(raw)


# --- the tables and the split ------------------------------------------------------------------------


def test_only_design_sessions_are_pooled_and_a_session_in_two_sources_is_refused(tmp_path):
    source = T.read_source(hand_made(tmp_path))
    sessions = T.pooled_sessions([source])
    assert len(sessions) == 16 and all(not s.session_id.endswith("_r2") and "pair" not in s.session_id for s in sessions)
    with pytest.raises(T.ExtractionInputError, match="in both"):
        T.pooled_sessions([source, source])


def test_the_split_is_reproducible_by_session_and_25_percent(tmp_path):
    source = T.read_source(hand_made(tmp_path))
    sessions = T.pooled_sessions([source])
    one = T.build_tables(sessions, [source], "head_on", 0.25, 66)
    two = T.build_tables(sessions, [source], "head_on", 0.25, 66)
    assert [s.session_id for s in one.held_out_sessions] == [s.session_id for s in two.held_out_sessions]
    assert len(one.held_out_sessions) == 3 and len(one.main_sessions) == 9  # floor(12 x 0.25 + 0.5)
    other = T.build_tables(sessions, [source], "head_on", 0.25, 67)
    assert {s.session_id for s in other.held_out_sessions} != {s.session_id for s in one.held_out_sessions}
    # By session: both people of a held-out session are held out, and none of a main one.
    held = {row["session"] for row in one.held_out}
    assert not held & {row["session"] for row in one.main} and len(one.held_out) == 6


def test_failed_sessions_never_enter_the_main_table_or_the_held_out_set(tmp_path):
    source = T.read_source(hand_made(tmp_path))
    tables = T.build_tables(T.pooled_sessions([source]), [source], "head_on", 0.25, 66)
    failed = {tables.label[s.session_id] for s in tables.failed_sessions}
    assert len(failed) == 4
    assert not failed & {row["session"] for row in (*tables.main, *tables.held_out)}
    assert T.failed_table(tables.failed_sessions) == [
        {"condition": "independent", "geometry": "aligned", "first_sides_of_the_two": "left/right", "failure": "collision", "sessions": "4"}]


def test_the_other_persons_factors_are_as_the_agent_was_told_them(tmp_path):
    source = T.read_source(hand_made(tmp_path, resolved=1, failed=0))
    (session,) = T.pooled_sessions([source])
    p1 = T.agent_row(session, "p1", source.record(session.session_id), "untested")
    p2 = T.agent_row(session, "p2", source.record(session.session_id), "untested")
    assert (p1["other_age"], p2["other_age"]) == ("70", T.NOT_TOLD)  # p2 was never shown p1's age
    assert (p1["other_load"], p2["other_load"]) == ("large_suitcase", T.NOT_SEEN)  # p1 has none to see
    assert (p1["other_ethnicity"], p2["other_ethnicity"]) == ("malay", T.NOT_TOLD)
    assert (p1["finds_other_attractive"], p2["finds_other_attractive"]) == ("yes", "no")
    assert p1["first_decision_distance_m"] == "9.8" and p1["signalled"] == "n/a" and p1["spoke"] == "n/a"
    assert (p1["passed_first"], p1["passing_side"], p2["first_slowed"]) == ("together", "right", "yes")


def test_the_gate_skips_a_type_that_fails_it_and_says_so(tmp_path):
    source = make_source(tmp_path / "src", [outcome_row("I_a_r1"), *(outcome_row(f"I_f{i}_r1", resolved=False) for i in range(3))])
    config = config_for([source])
    result = X.run_extraction(config, out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    (entry,) = result.summary["types"]
    assert entry["gate"]["status"] == "fails" and "failed its resolution gate" in entry["skipped"]
    assert not (tmp_path / "out" / "ext" / "head_on" / "runs").exists()
    assert "failed its resolution gate" in (tmp_path / "out" / "ext" / "report.md").read_text(encoding="utf-8")


def test_sources_with_different_gates_or_none_are_refused(tmp_path):
    one = T.read_source(make_source(tmp_path / "a", [outcome_row("I_a_r1")]))
    two = T.read_source(make_source(tmp_path / "b", [outcome_row("I_b_r1")], gate={"plan_only_resolved_min": 0.6, "reason": "x"}))
    with pytest.raises(T.ExtractionInputError, match="different resolution gates"):
        T.gate([one, two], T.pooled_sessions([one, two]), "head_on")
    none = T.read_source(make_source(tmp_path / "c", [outcome_row("I_c_r1")], gate=None))
    with pytest.raises(T.ExtractionInputError, match="no resolution_gate"):
        T.gate([none], T.pooled_sessions([none]), "head_on")
    assert T.gate([none], T.pooled_sessions([none]), "head_on", require=False)["status"] == "no_gate_fixed"


def test_round_1s_gate_is_rf30s_pooled_gate():
    sources = [T.read_source(PACKAGE_ROOT / folder) for folder in ROUND1]
    result = T.gate(sources, T.pooled_sessions(sources), "head_on")
    pooled = json.loads((PACKAGE_ROOT / ROUND1[1] / "analysis" / "gate_pooled.json").read_text(encoding="utf-8"))
    assert (result["resolved"], result["n"], result["passes"]) == (pooled["plan_only"]["resolved"], pooled["plan_only"]["n"], pooled["passes"])
    assert result["ci95"] == pooled["plan_only"]["ci95"]


# --- reading and checking a rule ---------------------------------------------------------------------


def full_rule(**changes):
    rule = {
        "rule": "Each person keeps to their own right.", "applies_when": "two people meet head-on",
        "action": "turn 10 to 15 degrees right from about 9.8 m", "exceptions": ["when the other is not seen"],
        "factors_used": ["other_load"], "needs_communication": False,
        "references": [{"citation": "A guide", "locator": "section 2", "kind": "law_or_guidance", "claim": "keep right"}],
        "debrief_support": {"share": 0.4, "note": "habit"}, "coverage": "most rows",
        "predict": {"target": "first_side", "if": [{"when": {"other_load": "large_suitcase", "other_age": {">=": 60}}, "then": "left"}],
                    "default": "right"},
    }
    rule.update(changes)
    return rule


def test_the_parser_reads_every_field_from_a_fenced_yaml_block():
    import yaml

    text = "Here are the rules.\n```yaml\n" + yaml.safe_dump({"rules": [full_rule()]}, sort_keys=False) + "```\nDone."
    (raw,) = R.read_reply(text)
    checked = R.check_rule(raw)
    assert checked.category == R.VALID and checked.stored
    assert checked.references == [{"citation": "A guide", "locator": "section 2", "kind": "law_or_guidance", "claim": "keep right"}]
    assert checked.predict.as_dict() == {"target": "first_side", "if": [{"when": {"other_load": "large_suitcase", "other_age": {">=": 60}}, "then": "left"}], "default": "right"}
    for key in R.REQUIRED:
        assert key in raw
    assert R.read_reply(yaml.safe_dump({"rules": []})) == []  # no fence: the whole reply
    for bad in ("", "no rules here", "```yaml\nrules: [unclosed\n```", "```yaml\nrule: x\n```"):
        with pytest.raises(R.ReplyError):
            R.read_reply(bad)


def test_no_known_source_is_read_as_one_reference_of_kind_none():
    for written in ("no known source", ["no known source."], [{"citation": "no known source", "locator": "none", "kind": "none", "claim": "none"}]):
        checked = R.check_rule(full_rule(references=written))
        assert checked.category == R.VALID
        assert checked.references == [{"citation": "no known source", "locator": "none", "kind": "none", "claim": "none"}]


@pytest.mark.parametrize("change, message", [
    ({"predict": {"target": "resolved", "default": "yes"}}, "predict.target"),
    ({"predict": {"target": "first_side", "if": [{"when": {"passing_side": "right"}, "then": "right"}], "default": "right"}}, "not a column a rule may read"),
    ({"predict": {"target": "first_side", "if": [{"when": {"first_side": "right"}, "then": "right"}], "default": "right"}}, "its own target"),
    ({"predict": {"target": "first_side", "if": [{"when": {"own_load": {">=": 1}}, "then": "left"}], "default": "right"}}, "compares numbers"),
    ({"predict": {"target": "first_side"}}, "predict.default"),
    ({"references": [{"citation": "x", "kind": "folklore", "locator": "-", "claim": "-"}]}, "kind"),
    ({"needs_communication": "no"}, "needs_communication"),
    ({"rule": ""}, "rule: text"),
])
def test_a_malformed_rule_is_a_schema_error(change, message):
    checked = R.check_rule(full_rule(**change))
    assert checked.category == R.SCHEMA_ERROR and message in checked.message and not checked.stored
    rule = full_rule()
    del rule["coverage"]
    assert R.check_rule(rule).category == R.SCHEMA_ERROR


@pytest.mark.parametrize("change", [
    {"predict": {"target": "first_side", "if": [{"when": {"other_ethnicity": "malay"}, "then": "left"}], "default": "right"}},
    {"predict": {"target": "first_side", "if": [{"when": {"finds_other_attractive": "yes"}, "then": "left"}], "default": "right"}},
    {"predict": {"target": "first_side", "if": [{"when": {"own_ethnicity": "chinese"}, "then": "left"}], "default": "right"}},
    {"factors_used": ["own_ethnicity"]},
    {"factors_used": ["attractiveness_0_sees_1"]},
    {"rule": "Malay walkers keep left."},
    {"action": "give way to someone you find attractive"},
    {"exceptions": ["not between people of the same ethnic group"]},
    {"rule": "Keep right, as Indian walkers do", "predict": {"target": "bogus"}},  # checked before the schema
])
def test_a_rule_that_names_ethnicity_or_attractiveness_is_protected_and_never_stored(change):
    checked = R.check_rule(full_rule(**change))
    assert checked.category == R.PROTECTED_ATTRIBUTE and not checked.stored


def test_pretty_in_prose_is_not_attractiveness():
    assert R.check_rule(full_rule(coverage="pretty much every row")).category == R.VALID


def test_a_rule_that_reads_a_signal_or_says_so_needs_communication():
    reads = R.check_rule(full_rule(predict={"target": "passed_first", "if": [{"when": {"signalled": "yes"}, "then": "yes"}], "default": "no"}))
    says = R.check_rule(full_rule(needs_communication=True))
    assert reads.category == says.category == R.NEEDS_COMMUNICATION and reads.stored and reads.reads_communication


# --- predict and the scorer ------------------------------------------------------------------------


ROWS = [
    {"other_load": "large_suitcase", "other_age": "70", "first_side": "left"},
    {"other_load": "large_suitcase", "other_age": "25", "first_side": "right"},
    {"other_load": "not_seen", "other_age": "70", "first_side": "right"},
    {"other_load": "large_suitcase", "other_age": "not_told", "first_side": "left"},
    {"other_load": "not_seen", "other_age": "25", "first_side": ""},  # unknown target: not scored
]


def test_predict_is_a_decision_list_with_lists_and_comparisons():
    predict = R.read_predict({"target": "first_side", "if": [
        {"when": {"other_load": "large_suitcase", "other_age": {">=": 60}}, "then": "left"},
        {"when": {"other_age": ["not_told", "25"]}, "then": "both"}], "default": "right"})
    assert [predict.decide(row) for row in ROWS] == ["left", "both", "right", "both", "both"]
    assert R.read_predict({"target": "first_side", "if": [{"when": {"other_age": {"!=": 70}}, "then": "x"}], "default": "y"}).decide(ROWS[0]) == "y"


def test_the_scorer_is_exact_on_a_hand_made_table():
    predict = R.read_predict(full_rule()["predict"])  # left with a suitcase and an age of at least 60, else right
    held_out = ROWS
    main = [{"first_side": "right"}] * 3 + [{"first_side": "left"}]
    result = R.fidelity(predict, main, held_out)
    # Known targets: rows 0 to 3. Predicted: left, right, right, right -> right on 0, 1, 2; wrong on 3.
    assert result["held_out"] == {"rows": 4, "correct": 3, "accuracy": 0.75}
    # Baseline: the main table's commonest value, right, is right on rows 1 and 2.
    assert (result["baseline_value"], result["baseline_accuracy"], result["beats_baseline"]) == ("right", 0.5, True)
    assert result["main"] == {"rows": 4, "correct": 3, "accuracy": 0.75}
    assert R.majority([{"t": "b"}, {"t": "a"}], "t") == "a"  # a tie goes to the first value in order


# --- matching across the runs ----------------------------------------------------------------------


def p(target, default, when=None, then=None):
    return R.read_predict({"target": target, "if": [] if when is None else [{"when": when, "then": then}], "default": default})


def test_rules_are_matched_across_three_runs_exactly():
    rows = [{"other_load": "large_suitcase" if i < 1 else "not_seen", "condition": "talk" if i < 30 else "independent"} for i in range(40)]
    keep_right = p("first_side", "right")
    keep_right_but_one = p("first_side", "right", {"other_load": "large_suitcase"}, "left")  # differs on 1 of 40 rows: 97.5%
    keep_right_in_talk = p("first_side", "right", {"condition": "independent"}, "left")       # differs on 10 of 40: 75%
    slow = p("first_slowed", "yes")
    groups = R.group_rules([[keep_right, slow], [keep_right_but_one, None], [keep_right_in_talk, slow, keep_right]], rows, 0.95)
    found = [(g.members, sorted(g.runs())) for g in groups]
    # Run 3's first rule agrees with keep_right on only 75% of the rows, so it starts a group of its
    # own; run 3's keep_right then joins the first group, which has no rule of run 3 yet.
    assert found == [([(0, 0), (1, 0), (2, 2)], [0, 1, 2]), ([(0, 1), (2, 1)], [0, 2]), ([(2, 0)], [2])]
    assert R.agreement(keep_right, keep_right_but_one, rows) == pytest.approx(0.975)
    assert R.agreement(keep_right, slow, rows) is None  # different targets never match


def test_a_group_found_in_two_of_three_runs_is_kept_and_one_found_once_is_unstable(tmp_path):
    source = hand_made(tmp_path)
    config = config_for([source])
    plan_ = X.plan(config).types[0]
    rule = lambda text, default: {"raw": {"rule": text}, "category": R.VALID, "predict": p("first_side", default).as_dict()}  # noqa: E731
    records = [{"rules": [rule("right", "right"), rule("left", "left")]}, {"rules": [rule("right", "right")]},
               {"rules": [{"raw": {}, "category": R.PROTECTED_ATTRIBUTE, "predict": None}]}]
    for record in records:
        record["outcome"] = "completed"
    combined = X.combine(config, plan_, records)
    assert [(g["status"], g["extraction_stability"]) for g in combined["groups"]] == [("candidate", "2/3"), ("unstable", "1/3")]
    assert combined["categories"] == {R.VALID: 3, R.PROTECTED_ATTRIBUTE: 1}


# --- the experiment on the mock --------------------------------------------------------------------


def test_the_mock_extraction_runs_three_times_and_stores_rules_with_fidelity_and_stability(tmp_path):
    config = config_for([PACKAGE_ROOT / f for f in ROUND1], name="round1", encounter_types=["head_on"],
                        encounter_descriptions={"head_on": "Two people meet head-on."}, runs={"seeds": [1101, 1102, 1103]},
                        sample={"size": 15})
    result = X.run_extraction(config, out_root=tmp_path, report=lambda _: None, git=GIT)
    assert result.status == X.STATUS_COMPLETED and len(result.executed) == 3
    folder = tmp_path / "round1" / "head_on"
    split = json.loads((folder / "split.json").read_text(encoding="utf-8"))
    assert (len(split["main_sessions"]), len(split["held_out_sessions"]), len(split["failed_sessions"])) == (76, 26, 90)
    records = [json.loads((folder / "runs" / f"run_{k}.json").read_text(encoding="utf-8")) for k in (1, 2, 3)]
    assert all(10 <= len(r["sampled_sessions"]) <= 20 and set(r["sampled_sessions"]) <= set(split["main_sessions"]) for r in records)
    assert len({tuple(r["sampled_sessions"]) for r in records}) == 3  # each run its own sample
    assert all(r["messages"][0]["role"] == "system" and r["attempts"][0]["raw"] for r in records)
    stored = sorted((folder / "extracted_rules" / "rules").glob("*.yaml"))
    import yaml

    files = [yaml.safe_load(path.read_text(encoding="utf-8")) for path in stored]
    assert files and all(f["measured"]["fidelity"]["held_out"]["rows"] > 0 and f["extraction_stability"] in ("1/3", "2/3", "3/3") for f in files)
    assert all(f["category"] != R.PROTECTED_ATTRIBUTE for f in files)
    assert all(not set(f["provenance"]["held_out_sessions"]) & set(f["provenance"]["sessions_used"]) for f in files)
    assert all(ref["check_status"] == "unchecked" for f in files for ref in f["references"])
    combined = json.loads((folder / "rules.json").read_text(encoding="utf-8"))
    assert combined["categories"][R.PROTECTED_ATTRIBUTE] >= 1  # the mock writes one in some runs: counted
    manifest = json.loads((folder / "extracted_rules" / "MANIFEST.json").read_text(encoding="utf-8"))
    assert sorted(manifest["files"]) == sorted(f"rules/{path.name}" for path in stored)
    # Run again: every run is reused, nothing is rewritten.
    again = X.run_extraction(config, out_root=tmp_path, report=lambda _: None, git=GIT)
    assert again.executed == [] and len(again.skipped) == 3
    assert [json.loads((folder / "runs" / f"run_{k}.json").read_text(encoding="utf-8")) for k in (1, 2, 3)] == records


def test_the_prompt_describes_every_column_and_names_no_protected_column_as_readable():
    template = ExtractTemplate("extract_v1")
    assert set(T.COLUMNS) <= set(template["columns"])
    sources = [T.read_source(PACKAGE_ROOT / folder) for folder in ROUND1]
    tables = T.build_tables(T.pooled_sessions(sources), sources, "head_on", 0.25, 66)
    rendered = render(template, tables, sample_sessions(tables.main_sessions, 1, 15), "Two people meet head-on.")
    system, user = (m["content"] for m in rendered.messages)
    assert "No rule may use them" in system and "no known source" in system
    for session in tables.held_out_sessions:
        assert tables.label[session.session_id] not in user  # held out: never shown
    assert all(tables.label[s] in user for s in rendered.sampled)
    assert "perceives:" not in user  # agent numbers are not the table's persons


def test_an_unreadable_reply_is_retried_once_then_the_run_is_unreadable(tmp_path):
    source = hand_made(tmp_path)
    config = config_for([source], runs={"seeds": [1]}, matching={"min_runs": 1})
    good = MOCK_POLICIES["extract_rehearsal_v1"]
    replies = iter(["not yaml at all", None])

    def flaky(request):
        reply = next(replies, "x")
        return good(request) if reply is None else reply

    result = X.run_extraction(config, client=MockClient(policy=flaky), out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    (record,) = [json.loads(p.read_text(encoding="utf-8")) for p in (tmp_path / "out" / "ext" / "head_on" / "runs").glob("run_*.json")]
    assert record["outcome"] == "completed" and len(record["attempts"]) == 2
    assert record["attempts"][0]["parse_error"] and record["attempts"][1]["appended"][1]["content"].startswith("Your last reply could not be read")
    assert result.status == X.STATUS_COMPLETED
    config2 = config_for([source], name="ext2", runs={"seeds": [1]}, matching={"min_runs": 1})
    X.run_extraction(config2, client=MockClient(policy=lambda r: "never yaml"), out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    (record,) = [json.loads(p.read_text(encoding="utf-8")) for p in (tmp_path / "out" / "ext2" / "head_on" / "runs").glob("run_*.json")]
    assert record["outcome"] == X.RUN_UNREADABLE and len(record["attempts"]) == X.MAX_ATTEMPTS and record["rules"] == []


# --- money -----------------------------------------------------------------------------------------


class PaidMock(MockClient):
    """The mock's replies and token counts, under the paid client's name, so that it is charged."""

    name = "deepseek"


def paid_client(config, ledger):
    guard = BudgetGuard(SpendLedger(ledger), config.budget["cap_usd"], PriceTable.from_yaml(), scope=config.experiment_name)
    return BudgetedClient(PaidMock(policy=MOCK_POLICIES["extract_rehearsal_v1"]), guard)


def signed(tmp_path, *names):
    sentences = {"ethnicity": "Ethics sign-off for the real-ethnicity factor (issue #92): approved by the supervisor on 2026-10-24",
                 "attractiveness": "Ethics sign-off for the perceived-attractiveness factor (issue #61): approved by the supervisor on 2026-10-24"}
    path = tmp_path / "CLAUDE.md"
    path.write_text("\n".join(sentences[name] for name in names), encoding="utf-8")
    return path


def test_a_paid_extraction_sends_nothing_without_confirm(tmp_path):
    config = config_for([hand_made(tmp_path)])

    class Refusing(MockClient):
        name = "deepseek"

        def complete(self, request):  # pragma: no cover - must not be reached
            raise AssertionError("a paid call was made")

    result = X.run_extraction(config, client=Refusing(), out_root=tmp_path / "out", report=lambda _: None, git=GIT,
                              sign_off_file=signed(tmp_path, "ethnicity", "attractiveness"))
    assert result.status == X.STATUS_AWAITING and not (tmp_path / "out" / "ext" / "head_on" / "runs").exists()
    assert json.loads((tmp_path / "out" / "ext" / "preview.json").read_text(encoding="utf-8"))["usd_total"] > 0


def test_a_paid_extraction_needs_the_gate_and_the_sign_offs_of_what_its_table_shows(tmp_path):
    source = hand_made(tmp_path)
    client = paid_client(config_for([source]), tmp_path / "ledger.jsonl")
    with pytest.raises(ConfigError, match="needs the resolution gate"):
        X.run_extraction(config_for([source], gate={"require": False}), client=client, out_root=tmp_path / "out", confirm=True,
                         report=lambda _: None, git=GIT, sign_off_file=signed(tmp_path, "ethnicity", "attractiveness"))
    for missing, present in (("real ethnicity", "attractiveness"), ("perceived attractiveness", "ethnicity")):
        with pytest.raises(ConfigError, match=missing):
            X.run_extraction(config_for([source]), client=client, out_root=tmp_path / "out", confirm=True,
                             report=lambda _: None, git=GIT, sign_off_file=signed(tmp_path, present))
    assert not (tmp_path / "ledger.jsonl").exists()
    statuses = [json.loads(line)["status"] for line in (tmp_path / "out" / "ext" / "invocations.jsonl").read_text(encoding="utf-8").splitlines()]
    assert statuses == ["refused_no_gate", "refused_no_sign_off", "refused_no_sign_off"]


def test_the_budget_guard_stops_a_paid_extraction_at_the_cap_and_a_rerun_redoes_only_the_aborted_run(tmp_path):
    from negsim.llm.base import LLMRequest

    source = hand_made(tmp_path)
    ledger = tmp_path / "ledger.jsonl"
    probe = config_for([source])
    plan_ = X.plan(probe).types[0]
    guard = BudgetGuard(SpendLedger(ledger), 1.0, PriceTable.from_yaml())
    worst = guard.worst_case(LLMRequest(plan_.rendered[0].messages, "deepseek-flash", 1.0, probe.llm["max_tokens"]))
    # The main table has 9 sessions, fewer than the sample, so every run sends the same prompt: the
    # first call fits under this cap, and once it is charged the second cannot.
    config = config_for([source], budget={"cap_usd": worst + 1e-9})
    sign = signed(tmp_path, "ethnicity", "attractiveness")
    first = X.run_extraction(config, client=paid_client(config, ledger), out_root=tmp_path / "out", confirm=True,
                             report=lambda _: None, git=GIT, sign_off_file=sign)
    entries = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
    assert len(entries) == 1 and entries[0]["cost_usd"] <= config.budget["cap_usd"] and entries[0]["experiment"] == "ext"
    assert first.status == X.STATUS_PARTIAL and "budget" in first.aborted
    assert first.summary["cost"]["actual_usd"] == pytest.approx(entries[0]["cost_usd"])  # the ledger's spend, all of it
    runs = tmp_path / "out" / "ext" / "head_on" / "runs"
    outcomes = {path.name: json.loads(path.read_text(encoding="utf-8"))["outcome"] for path in runs.glob("run_*.json")}
    assert outcomes == {"run_1.json": X.RUN_COMPLETED, "run_2.json": X.RUN_ABORTED}
    assert not (tmp_path / "out" / "ext" / "head_on" / "rules.json").exists()  # matched only once every run has a record
    bigger = config_for([source], budget={"cap_usd": 1.0})
    again = X.run_extraction(bigger, client=paid_client(bigger, ledger), out_root=tmp_path / "out", confirm=True,
                             report=lambda _: None, git=GIT, sign_off_file=sign)
    assert again.skipped == ["head_on/run_1"] and again.executed == ["head_on/run_2", "head_on/run_3"]
    assert (runs / "run_2.aborted1.json").is_file() and again.status == X.STATUS_COMPLETED
    ledger_total = math.fsum(json.loads(line)["cost_usd"] for line in ledger.read_text(encoding="utf-8").splitlines())
    assert again.summary["cost"]["actual_usd"] == pytest.approx(ledger_total)


def test_the_config_refuses_a_sample_outside_10_to_20_and_min_runs_above_the_runs():
    with pytest.raises(ConfigError, match="sample.size"):
        config_for(["x"], sample={"size": 21})
    with pytest.raises(ConfigError, match="sample.size"):
        config_for(["x"], sample={"size": 9})
    with pytest.raises(ConfigError, match="min_runs"):
        config_for(["x"], matching={"min_runs": 4})


def test_round_1s_config_reads_and_names_rf30s_pooled_sources():
    config = X.ExtractionConfig.load("configs/extraction/round1_head_on.yaml")
    assert config.sources == ROUND1 and config.gate_required and config.run_seeds == (1101, 1102, 1103)
    assert config.llm["client"] == "mock" and config.template == "extract_v1" and config.held_out_share == 0.25


def test_once_a_run_has_a_record_another_config_is_refused_but_a_new_cap_is_not(tmp_path):
    source = hand_made(tmp_path)
    X.run_extraction(config_for([source]), out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    with pytest.raises(ConfigError, match="another config"):
        X.run_extraction(config_for([source], held_out={"share": 0.5, "seed": 66}), out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    again = X.run_extraction(config_for([source], budget={"cap_usd": 0.5}), out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    assert again.executed == [] and len(again.skipped) == 3
