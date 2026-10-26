"""Issue #108 (RF-31): translating extracted rules into rule format 4 (``translate_v2``), what is
still lost, the identity check with each person's factors and own view, and crowd screening of a
crowd given core factors, all on the mock. RF-12's format 3 path is ``test_translation.py``."""

from __future__ import annotations

import json

import pytest
import yaml

from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.llm.mock import MockClient
from negsim.negotiation.prompts import load_template_data
from negsim.rulegen.describe import glossary_text, rule_schema_version_of
from negsim.rules.database import RuleDatabase
from negsim.translation import experiment as T
from negsim.translation import identity as I
from negsim.translation import losses as L
from negsim.translation import mock as M
from negsim.translation import prompt as P
from test_translation import GIT, SESSIONS, SMALL_CROWD, SOURCE, extracted, make_extraction

V2 = "translate_rehearsal_v2"


def sentence_v4(path: str, stem: str = "People slow down when they meet") -> str:
    for n in range(1000):
        sentence = f"{stem} ({n})."
        if M.path_of_v4(sentence) == path:
            return sentence
    raise AssertionError(path)


def config_v4(extraction, name="tr4", **changes):
    raw = {
        "layer": "rule_translation", "experiment_name": name, "extraction": str(extraction), "statuses": ["candidate"],
        "template": "translate_v2", "llm": {"client": "mock", "mock_policy": V2, "transport_retries": 0},
        "budget": {"cap_usd": 0.0}, "identity": {"enabled": True}, "screening": {"enabled": False},
    }
    raw.update(changes)
    return T.TranslationConfig.from_raw(raw)


# --- the templates ---------------------------------------------------------------------------------


def test_translate_v2_uses_rulegen_common_v3_which_describes_format_4_and_v2_is_unchanged():
    templates = P.load("translate_v2")
    assert templates.common_key == "rulegen_common_v3" and rule_schema_version_of(templates.common) == 4
    system = P.system_message(templates)
    assert glossary_text(templates.common, True) in system
    for words in ("by_condition", "own_when", "self.finds_other_attractive", "sidestep", "other_passes", "up to 3", "<0 to 90>"):
        assert words in system, words
    assert "ethnicity" not in glossary_text(templates.common, True)
    old = P.load("translate_v1")  # still the format 3 translator, word for word
    assert old.common_key == "rulegen_common_v2" and "by_condition" not in P.system_message(old)
    v1, _ = load_template_data("translate_v1", "rule_translation")
    v2, _ = load_template_data("translate_v2", "rule_translation")
    for key in ("reply_format", "user", "retry", "factor_line", "exception_line"):
        assert v1[key] == v2[key], key  # the two runs compare part for part


# --- the mock --------------------------------------------------------------------------------------


@pytest.mark.parametrize("path, category", [
    ("valid_condition_steps", "valid"), ("valid_own_when", "valid"), ("valid_after_retry", "valid"),
    ("valid_own_attractiveness", "valid"), ("own_only_scope", "needs_communication"),
    ("protected_attractiveness", "protected_attribute"), ("protected_attribute", "protected_attribute"),
    ("no_rule", T.NOT_EXPRESSIBLE), ("schema_error", "schema_error"),
])
def test_each_format_4_mock_path_gets_its_category(tmp_path, path, category):
    folder = make_extraction(tmp_path / "x", [extracted("x_head_on_a", sentence_v4(path), factors=("own_assertiveness", "other_mobility_aid", "geometry"))])
    config = config_v4(folder)
    plan_ = T.plan(config)
    assert plan_.rule_schema_version == 4
    record = T.translate_once(config, plan_.extraction, plan_.items[0], plan_.templates, MockClient(policy=M.POLICIES[V2]))
    assert record["outcome"] == T.RUN_COMPLETED and len(record["attempts"]) == (2 if path == "valid_after_retry" else 1)
    entry = T.assess(plan_.items[0].extracted, record, 4)
    assert entry["category"] == category
    lost = {item["part"] for item in entry["lost"]}
    assert "geometry" in lost and "own_assertiveness" not in lost and "other_mobility_aid" not in lost


# --- what is lost ------------------------------------------------------------------------------------


def test_format_4_reads_the_seen_and_own_factors_and_still_not_the_layout_signals_or_ethnicity():
    four = {item["column"]: item["status"] for item in L.factor_losses(
        ["own_assertiveness", "own_urgency", "own_memory_note", "own_residence", "other_mobility_aid", "own_load", "other_distraction",
         "knows_other", "finds_other_attractive", "geometry", "surroundings", "decision_points", "signalled", "other_ethnicity", "own_age"], 4)}
    assert {name for name, status in four.items() if status == L.READABLE} == {
        "own_assertiveness", "own_urgency", "own_memory_note", "own_residence", "other_mobility_aid", "own_load", "other_distraction",
        "knows_other", "finds_other_attractive", "own_age"}
    assert (four["geometry"], four["surroundings"], four["decision_points"]) == (L.NO_FIELD,) * 3
    assert four["signalled"] == L.COMMUNICATION and four["other_ethnicity"] == L.PROTECTED
    three = {item["column"]: item["status"] for item in L.factor_losses(["own_assertiveness", "other_mobility_aid", "finds_other_attractive"])}
    assert three == {"own_assertiveness": L.UNOBSERVABLE, "other_mobility_aid": L.NO_FIELD, "finds_other_attractive": L.PROTECTED}  # RF-12's map, unchanged


def test_of_the_actions_words_only_a_signal_or_words_is_beyond_format_4():
    words = ["slows to 0.9 m/s from about 6 m, turns 10 degrees right until the other passes, and nods"]
    assert L.action_flags(words, 4) == ["signal_or_talk"]
    assert set(L.action_flags(words)) >= {"turn_angle", "start", "duration", "speed_value", "signal_or_talk"}


# --- the identity check ------------------------------------------------------------------------------


def test_a_format_4_rule_gets_each_persons_factors_own_view_and_what_the_design_showed():
    row = {"session_id": "s", "p1_agent": "1", "p2_agent": "0", "p1_age": "70", "p2_age": "25", "p1_gender": "female", "p2_gender": "male",
           "p1_mobility_aid": "cane", "p2_mobility_aid": "none", "p1_load": "none", "p2_load": "none", "p1_distraction": "none",
           "p2_distraction": "phone", "p1_assertiveness": "holds_ground", "p2_assertiveness": "gives_way", "p1_urgency": "routine",
           "p2_urgency": "urgent", "p1_residence": "local", "p2_residence": "visitor", "p1_memory_note": "none", "p2_memory_note": "none",
           "p1_finds_other_attractive": "1", "p2_finds_other_attractive": "0", "p1_knows_other": "0", "p2_knows_other": "0",
           "attractiveness_visible": "True", "demographics_visible": "True", "load_visible": "False"}
    three = I.population(row)
    assert three[1]["attributes"] == {"age": 70, "gender": "female"}  # a format 3 rule: as before
    four = I.population(row, 4)
    assert four[1]["attributes"]["mobility_aid"] == "cane" and four[0]["attributes"]["assertiveness"] == "gives_way"
    assert I.pairwise(row) == {(1, 0): {"knows_other": False, "finds_other_attractive": True}, (0, 1): {"knows_other": False, "finds_other_attractive": False}}
    assert I.pairwise({**row, "attractiveness_visible": "False"}) == {(1, 0): {"knows_other": False}, (0, 1): {"knows_other": False}}

    class Plan:
        visibility = {"speed": True, "size": True, "age": True, "gender": True}

    assert I.visibility(Plan(), row) == {"speed": True, "size": True, "age": True, "gender": True}
    assert I.visibility(Plan(), row, 4) == {"speed": True, "size": True, "age": True, "gender": True, "mobility_aid": True, "load": False, "distraction": True}


def test_a_format_4_rule_with_steps_runs_on_step_1_sessions(tmp_path):
    from negsim.rulegen.writer import StagingDatabase

    database = StagingDatabase(tmp_path / "db")
    database.create()
    body = M._head_on("symmetric", {"both": {"own_when": {"when": {"field": "self.assertiveness", "op": "==", "value": "gives_way"},
                                                            "then": {"steps": M._SIDESTEP}}}})
    database.write({"schema_version": 4, "rule_id": "ext_test4", "version": 1, "status": "candidate",
                    "provenance": {"source_type": "extracted", "source_ref": "test", "created_at": "2026-10-26", "author": "test", "notes": "",
                                   "validation_evidence": []}, **body}, "test")
    rule = database.latest("ext_test4")
    rows = I.IdentityCheck(I.SessionSource([PACKAGE_ROOT / SOURCE])).run(rule, database.root, SESSIONS)
    assert [row["session_id"] for row in rows] == SESSIONS
    assert all(row["plain_is_the_recorded_run"] and row["rule_matched"] for row in rows)


# --- the experiment ----------------------------------------------------------------------------------


def test_the_experiment_writes_format_4_rules_screens_them_in_a_crowd_with_factors_and_a_rerun_changes_nothing(tmp_path):
    rules = [
        extracted("x_head_on_cane", sentence_v4("valid_condition_steps"), factors=("other_mobility_aid",)),
        extracted("x_head_on_own", sentence_v4("valid_own_when"), factors=("own_assertiveness",)),
        extracted("x_head_on_scope", sentence_v4("own_only_scope")),
    ]
    folder = make_extraction(tmp_path / "x", rules)
    config = config_v4(folder, screening={"enabled": True, "repeats": 1, "scenario_overrides": SMALL_CROWD,
                                          "factors": {"mobility_aid": ["none", "cane"], "assertiveness": ["gives_way", "holds_ground"]}})
    out = tmp_path / "out"
    result = T.run_translation(config, out_root=out, report=lambda _: None, git=GIT)
    summary = result.summary
    assert result.status == T.STATUS_COMPLETED and summary["rule_schema_version"] == 4
    assert summary["counts"]["categories"] == {"valid": 2, "needs_communication": 1} and summary["counts"]["runnable_in_orca"] == 2
    by = {entry["extracted_rule_id"]: entry for entry in summary["rules"]}
    for name in ("x_head_on_cane", "x_head_on_own"):
        assert [entry["kind"] for entry in by[name]["screening"]] == ["replay", "crowd"]
        crowd = by[name]["screening"][1]
        assert crowd["verdict"] in ("passed", "failed") and crowd["results"]["summary"]["rule_fired"]
    staged = yaml.safe_load((out / "tr4" / T.STAGING_DIR / "rules" / "ext_head_on_cane.v1.yaml").read_text(encoding="utf-8"))
    assert staged["schema_version"] == 4 and "RF-31" in staged["provenance"]["notes"]
    manifest = json.loads((out / "tr4" / T.STAGING_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    assert "rule format 4" in manifest["about"]
    RuleDatabase.load(out / "tr4" / T.STAGING_DIR)
    assert "rule format 4" in (out / "tr4" / "report.md").read_text(encoding="utf-8")
    config_json = json.loads((out / "tr4" / "config.json").read_text(encoding="utf-8"))
    assert config_json["experiment"]["screening"]["factors"] == {"mobility_aid": ["none", "cane"], "assertiveness": ["gives_way", "holds_ground"]}
    before = {p: p.read_bytes() for p in (out / "tr4").rglob("*") if p.is_file() and p.name != "invocations.jsonl"}
    again = T.run_translation(config, out_root=out, report=lambda _: None, git=GIT)
    assert again.executed == []
    assert {p: p.read_bytes() for p in (out / "tr4").rglob("*") if p.is_file() and p.name != "invocations.jsonl"} == before


def test_the_crowd_factors_are_checked():
    with pytest.raises(ConfigError, match="screening.factors.mobility_aid"):
        config_v4("x", screening={"enabled": False, "factors": {"mobility_aid": ["crutch"]}})
    with pytest.raises(ConfigError, match="screening.factors.ethnicity"):
        config_v4("x", screening={"enabled": False, "factors": {"ethnicity": ["chinese"]}})
    assert "factors" not in config_v4("x", screening={"enabled": True}).as_dict()["screening"]  # a format 3 config records as before


def test_rf31s_config_translates_rf11s_candidates_with_translate_v2_under_the_cap_claude_md_records():
    config = T.TranslationConfig.load("configs/translation/rf31_round1_head_on.yaml")
    plan_ = T.plan(config)
    assert config.template == "translate_v2" and config.statuses == ("candidate",) and plan_.rule_schema_version == 4
    assert config.budget["cap_usd"] == 0.05 and config.llm["client"] == "mock" and plan_.preview["fits_the_cap"]
    claude = (PACKAGE_ROOT.parent / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Approved for issue #108 only, 2026-10-26" in claude and "**USD 0.05**" in claude
    assert [item.extracted.rule_id for item in plan_.items] == ["x_head_on_0ecc2d1a6e", "x_head_on_4eb7a97c8d", "x_head_on_6455ca5589", "x_head_on_aacce0961b"]
