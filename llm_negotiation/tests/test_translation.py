"""Issue #67 (RF-12): translating extracted rules into rule format 3, what is lost, the writer, the
identity check on Step 1's sessions and crowd screening, all on the mock."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pytest
import yaml

from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.extraction.experiment import ExtractionStore
from negsim.extraction.prompt import ExtractTemplate
from negsim.extraction.table import COLUMNS
from negsim.llm.budget import BudgetedClient, BudgetGuard, SpendLedger
from negsim.llm.mock import MockClient
from negsim.llm.pricing import PriceTable
from negsim.negotiation.parsing import TurnParseError
from negsim.rulegen.describe import glossary_text
from negsim.rulegen.writer import StagingDatabase
from negsim.rules.database import RuleDatabase
from negsim.translation import experiment as T
from negsim.translation import identity as I
from negsim.translation import losses as L
from negsim.translation import mock as M
from negsim.translation import prompt as P
from negsim.translation.reply import LOST_KINDS, parse_translation

GIT = {"commit": "test", "dirty": False}
SOURCE = "runs/rf30_round1_head_on_keep_line"
SMALL_CROWD = {"geometry": {"agents_per_direction": 4, "length": 20.0}, "max_time": 60.0}


def step1_sessions(n=2):
    """Real round 1 sessions (RF-30): the first ``n`` design sessions, one of them with a person
    wider for a suitcase if there is one."""
    with (PACKAGE_ROOT / SOURCE / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["repeat"] == "1" and not row.get("pair_id")]
    loaded = [row for row in rows if "large_suitcase" in (row["p1_load"], row["p2_load"])][:1]
    rest = [row for row in rows if row not in loaded]
    return [row["session_id"] for row in (loaded + rest)[:n]]


SESSIONS = step1_sessions()


def sentence_for(path: str, stem: str = "People slow down when they meet") -> str:
    """A rule sentence the mock answers by ``path``."""
    for n in range(1000):
        sentence = f"{stem} ({n})."
        if M.path_of(sentence) == path:
            return sentence
    raise AssertionError(path)


def extracted(rule_id, sentence, status="candidate", category="valid", factors=("own_age", "other_load"), sessions=SESSIONS):
    return {
        "rule_id": rule_id, "version": 1, "status": status, "encounter_type": "head_on", "category": category,
        "extraction_stability": "2/3", "rule": sentence, "applies_when": "the other is older or pulls a suitcase",
        "action": "slows to about 0.9 m/s from about 6 m and turns 10 degrees to the right until the other passes",
        "exceptions": ["urgent people do not"], "factors_used": list(factors), "needs_communication": category == "needs_communication",
        "debrief_support": {"share": 0.5, "note": "test"}, "coverage": "test",
        "references": [{"citation": "A study", "locator": "p. 3", "kind": "published_study", "claim": "people slow", "check_status": "unchecked"}],
        "predict": {"target": "first_slowed", "if": [{"when": {"other_load": "large_suitcase"}, "then": "yes"}], "default": "no"},
        "measured": {"fidelity": {"target": "first_slowed", "held_out": {"rows": 4, "correct": 3, "accuracy": 0.75}, "baseline_accuracy": 0.5, "beats_baseline": True}},
        "provenance": {"source_type": "extracted", "experiment": "test_extraction", "sources": [SOURCE], "sessions_used": list(sessions)},
    }


def make_extraction(folder: Path, rules) -> Path:
    """An extraction folder laid out as RF-11's: its config, its summary and its rule store."""
    store = ExtractionStore(folder / "head_on" / "extracted_rules")
    listed = []
    for rule in rules:
        name, _ = store.write(rule, rule["status"])
        listed.append({"rule_id": rule["rule_id"], "status": rule["status"], "file": name})
    (folder / "config.json").write_text(json.dumps({
        "layer": "rule_extraction", "template": ExtractTemplate("extract_v1").identity(),
        "experiment": {"experiment_name": "test_extraction", "encounter_descriptions": {"head_on": "Two people walk towards each other along a corridor."}},
    }), encoding="utf-8")
    (folder / "summary.json").write_text(json.dumps({"types": [{"encounter_type": "head_on", "rules": listed}]}), encoding="utf-8")
    return folder


def config_for(extraction, name="tr", **changes):
    raw = {
        "layer": "rule_translation", "experiment_name": name, "extraction": str(extraction), "statuses": ["candidate"],
        "llm": {"client": "mock", "mock_policy": "translate_rehearsal_v1", "transport_retries": 0},
        "budget": {"cap_usd": 0.0}, "identity": {"enabled": True},
        "screening": {"enabled": False},
    }
    raw.update(changes)
    return T.TranslationConfig.from_raw(raw)


# --- the template ------------------------------------------------------------------------------


def test_the_template_is_frozen_uses_rulegen_common_v2_and_shows_its_glossary_word_for_word():
    templates = P.load()
    assert templates.identity()["uses"]["key"] == "rulegen_common_v2"
    system = P.system_message(templates)
    assert glossary_text(templates.common, True) in system
    assert "THE FORMAT, WITH PLACEHOLDERS" in system and "HOW TO REPLY" in system
    for kind in LOST_KINDS:
        assert kind in templates.data["reply_format"]


def test_the_user_message_is_the_extracted_rule_its_factors_meanings_and_predict_and_nothing_measured():
    templates = P.load()
    meanings = ExtractTemplate("extract_v1")["columns"]
    rule = extracted("x_head_on_a", "Older people slow down.", factors=("own_age", "not_a_column"))
    rendered = P.render(templates, rule, meanings, "Two people meet.")
    user = rendered.messages[1]["content"]
    assert "Rule: Older people slow down." in user and "- urgent people do not" in user
    assert f"- own_age: {' '.join(meanings['own_age'].split())}" in user
    assert "- not_a_column: not a column of the table" in user
    assert json.dumps(rule["predict"], ensure_ascii=False) in user and "- first_slowed: " in user
    assert "Needs communication (it held only when a signal or words were used): no" in user
    for measured in ("A study", "0.75", "beats_baseline", "test_extraction"):
        assert measured not in user  # references, fidelity and provenance are the code's
    assert rendered.messages[0]["content"] == P.system_message(templates)  # the same for every rule: cacheable


# --- the reply ---------------------------------------------------------------------------------


def test_the_reply_is_read_with_rule_generations_tolerances():
    found = parse_translation('```json\n{"rule": {"encounter": "head_on"}, "lost": [{"part": " a  cane ", "kind": "condition", "how": "left_out"}], "note": "n", "extra": 1}\n```')
    assert found.rule == {"encounter": "head_on"} and found.lost == [{"part": "a cane", "kind": "condition", "how": "left_out"}]
    bare = parse_translation('{"rule": null}')
    assert bare.rule is None and bare.lost == [] and bare.note == ""
    odd = parse_translation('{"rule": null, "lost": [{"part": "x", "kind": "angle", "how": "maybe"}]}')
    assert odd.lost == [{"part": "x", "kind": "other", "kind_as_written": "angle", "how": None}]


@pytest.mark.parametrize("raw, code", [
    ("", "empty_output"), ("not json", "not_json"), ("[1]", "not_an_object"), ('{"lost": []}', "missing_rule"),
    ('{"rule": "keep right"}', "rule_not_an_object"), ('{"rule": null, "lost": "x"}', "lost_not_a_list"),
    ('{"rule": null, "lost": [{"kind": "turn"}]}', "lost_item_malformed"), ('{"rule": null, "note": 3}', "note_not_text"),
])
def test_an_unreadable_reply_says_why(raw, code):
    with pytest.raises(TurnParseError) as error:
        parse_translation(raw)
    assert error.value.code == code


# --- what was lost, mechanically -----------------------------------------------------------------


def test_every_column_of_rf11s_table_has_a_status_and_the_format_reads_only_age_gender_and_distance():
    assert set(L.COLUMN_FIELDS) == set(COLUMNS)
    readable = sorted(name for name, (status, _) in L.COLUMN_FIELDS.items() if status == L.READABLE)
    assert readable == ["first_decision_distance_m", "other_age", "other_gender", "own_age", "own_gender"]
    expected = {"own_assertiveness": L.UNOBSERVABLE, "own_urgency": L.UNOBSERVABLE, "own_residence": L.UNOBSERVABLE,
                "own_memory_note": L.UNOBSERVABLE, "other_load": L.NO_FIELD, "other_mobility_aid": L.NO_FIELD,
                "other_distraction": L.NO_FIELD, "knows_other": L.NO_FIELD, "geometry": L.NO_FIELD, "signalled": L.COMMUNICATION,
                "spoke": L.COMMUNICATION, "condition": L.COMMUNICATION, "own_ethnicity": L.PROTECTED, "other_ethnicity": L.PROTECTED,
                "finds_other_attractive": L.PROTECTED, "first_side": L.BEHAVIOUR, "passing_side": L.BEHAVIOUR}
    assert {name: L.COLUMN_FIELDS[name][0] for name in expected} == expected
    assert L.factor_losses(["own_age", "nonsense"]) == [
        {"column": "own_age", "status": L.READABLE, "field": L.COLUMN_FIELDS["own_age"][1]},
        {"column": "nonsense", "status": L.UNKNOWN, "field": "not a column of the table"},
    ]


def test_the_action_words_are_flagged_for_what_format_3_has_no_directive_for():
    text = "speed drops from 1.3 to 0.8-1.1 m/s from about 9.8 m and is held until other_passes, turning 10 to 20 degrees"
    assert L.action_flags([text]) == ["turn_angle", "turn_or_step_aside", "start", "duration", "speed_value"]
    assert L.action_flags(["People nod and say excuse me, then stop or back up."]) == ["stop_or_back_up", "signal_or_talk"]
    assert L.action_flags(["Both keep to the right."]) == []
    counts = L.counted([{"factor_losses": L.factor_losses(["own_age", "other_load", "own_load"]), "action_flags": ["start"],
                         "lost": [{"kind": "condition"}, {"kind": "condition"}]},
                        {"factor_losses": [], "action_flags": ["start", "duration"], "lost": [{"kind": "turn"}]}])
    assert counts == {"rules": 2, "factor_status": {"readable": 1, "no_field": 1}, "action_flags": {"start": 2, "duration": 1},
                      "lost_kinds": {"condition": 1, "turn": 1}}


# --- the mock, and the category of every path ----------------------------------------------------


@pytest.mark.parametrize("path, category", [
    ("valid", "valid"), ("valid_after_retry", "valid"), ("valid_keeps_room", "valid"), ("format_limit", "format_limit"),
    ("needs_communication", "needs_communication"), ("no_rule", T.NOT_EXPRESSIBLE), ("protected_attribute", "protected_attribute"),
    ("schema_error", "schema_error"),
])
def test_each_mock_path_gets_its_category(tmp_path, path, category):
    folder = make_extraction(tmp_path / "x", [extracted("x_head_on_a", sentence_for(path))])
    config = config_for(folder)
    plan_ = T.plan(config)
    record = T.translate_once(config, plan_.extraction, plan_.items[0], plan_.templates, MockClient(policy=M.POLICIES["translate_rehearsal_v1"]))
    assert record["outcome"] == T.RUN_COMPLETED and len(record["attempts"]) == (2 if path == "valid_after_retry" else 1)
    entry = T.assess(plan_.items[0].extracted, record)
    assert entry["category"] == category
    assert {"part": "other_load", "kind": "condition", "how": "left_out"} in entry["lost"]


def test_a_reply_unreadable_twice_is_recorded_with_both_attempts(tmp_path):
    folder = make_extraction(tmp_path / "x", [extracted("x_head_on_a", sentence_for("valid"))])
    config = config_for(folder)
    plan_ = T.plan(config)
    record = T.translate_once(config, plan_.extraction, plan_.items[0], plan_.templates, MockClient(policy=lambda r: "no"))
    assert record["outcome"] == T.RUN_UNREADABLE and [a["parse_error"] for a in record["attempts"]] == ["not_json: Expecting value: line 1 column 1 (char 0)"] * 2
    assert T.assess(plan_.items[0].extracted, record)["category"] is None


# --- reading RF-11's store -----------------------------------------------------------------------


def test_round_1s_extraction_hands_over_its_four_candidates_and_one_needs_communication():
    found = T.read_extraction(PACKAGE_ROOT / "runs/rf11_round1_head_on", ["candidate"])
    assert [r.rule_id for r in found.rules] == ["x_head_on_0ecc2d1a6e", "x_head_on_4eb7a97c8d", "x_head_on_6455ca5589", "x_head_on_aacce0961b"]
    assert [r.data["category"] for r in found.rules].count("needs_communication") == 1
    assert len(T.read_extraction(PACKAGE_ROOT / "runs/rf11_round1_head_on", ["candidate", "unstable"]).rules) == 16


def test_a_rule_file_changed_after_its_extraction_froze_it_is_refused(tmp_path):
    folder = make_extraction(tmp_path / "x", [extracted("x_head_on_a", "A rule.")])
    path = folder / "head_on" / "extracted_rules" / "rules" / "x_head_on_a.v1.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("A rule.", "Another rule."), encoding="utf-8")
    with pytest.raises(ConfigError, match="not the file its extraction store froze"):
        T.read_extraction(folder, ["candidate"])


# --- the writer ----------------------------------------------------------------------------------


def test_a_valid_translation_is_written_in_format_3_with_the_codes_provenance_and_unchecked_references(tmp_path):
    folder = make_extraction(tmp_path / "x", [extracted("x_head_on_a", sentence_for("valid"))])
    config = config_for(folder)
    plan_ = T.plan(config)
    record = T.translate_once(config, plan_.extraction, plan_.items[0], plan_.templates, MockClient(policy=M.POLICIES["translate_rehearsal_v1"]))
    rule = T.build_rule(config, plan_.extraction, plan_.items[0].extracted, record, runnable=True)
    assert rule["rule_id"] == "ext_head_on_a" and rule["schema_version"] == 3 and rule["status"] == "candidate"
    provenance = rule["provenance"]
    assert provenance["source_type"] == "extracted" and plan_.items[0].extracted.sha256 in provenance["source_ref"]
    assert provenance["validation_evidence"] == [{"from": "extraction", "citation": "A study", "locator": "p. 3",
                                                   "source_kind": "published_study", "claim": "people slow", "status": "unchecked"}]
    assert "NOT RUNNABLE" not in provenance["notes"]
    assert "NOT RUNNABLE IN ORCA" in T.build_rule(config, plan_.extraction, plan_.items[0].extracted, record, runnable=False)["provenance"]["notes"]
    database = T.staging(tmp_path / "exp")
    database.write(rule, "test")
    loaded = RuleDatabase.load(database.root)  # the loader reads it as any rule database
    assert [r.rule_id for r in loaded.rules] == ["ext_head_on_a"] and loaded.rules[0].written["roles"]["by"]["field"] == "agent.age"
    assert "rule-translation experiment" in json.loads(database.manifest_path.read_text(encoding="utf-8"))["about"]


# --- the identity check on real Step 1 sessions --------------------------------------------------


def staged(tmp_path, body):
    database = StagingDatabase(tmp_path / "db")
    database.create()
    rule = {"schema_version": 3, "rule_id": "ext_test", "version": 1, "status": "candidate",
            "provenance": {"source_type": "extracted", "source_ref": "test", "created_at": "2026-10-26", "author": "test", "notes": "",
                           "validation_evidence": []},
            **body}
    database.write(rule, "test")
    return database, database.latest("ext_test")


def test_plain_orca_is_the_run_each_session_recorded_and_a_rule_that_never_matches_changes_nothing(tmp_path):
    database, rule = staged(tmp_path, {"encounter": "head_on", "when": {"all": [{"field": "pair.distance_m", "op": "<", "value": 0.0, "unit": "m"}]},
                                       "roles": "symmetric", "directive": {"both": {"side_preference": "right"}}, "priority": 100})
    rows = I.IdentityCheck(I.SessionSource([PACKAGE_ROOT / SOURCE])).run(rule, database.root, SESSIONS)
    assert [row["session_id"] for row in rows] == SESSIONS
    for row in rows:
        assert row["plain_is_the_recorded_run"] and not row["rule_matched"]
        assert [row[f"rule_{k}"] for k in I.COMPARED] == [row[f"plain_{k}"] for k in I.COMPARED]
        assert row["rule_reproduces"] == row["plain_reproduces"]


def test_a_keep_right_rule_matches_and_both_pass_on_their_right(tmp_path):
    database, rule = staged(tmp_path, {"encounter": "head_on", "when": {"all": []}, "roles": "symmetric",
                                       "directive": {"both": {"side_preference": "right"}}, "priority": 100})
    rows = I.IdentityCheck(I.SessionSource([PACKAGE_ROOT / SOURCE])).run(rule, database.root, SESSIONS)
    for row in rows:
        assert row["rule_matched"] and (row["rule_passing_side_a"], row["rule_passing_side_b"]) == ("right", "right")
        assert row["rule_same_sides"] == ((row["step1_passing_side_a"], row["step1_passing_side_b"]) == ("right", "right"))
    summary = I.summarise(rows)
    assert summary["trusted"] == len(SESSIONS) and summary["rule_matched"] == len(SESSIONS)
    assert summary["all"]["rule_reproduces"] == pytest.approx(sum(r["rule_reproduces"] for r in rows) / len(rows))
    assert I.as_csv(rows).splitlines()[0] == ",".join(I.ROW_COLUMNS)


def test_a_session_found_in_two_sources_is_refused():
    with pytest.raises(ValueError, match="is in both"):
        I.SessionSource([PACKAGE_ROOT / SOURCE, PACKAGE_ROOT / SOURCE])


def test_the_people_and_their_visibility_are_the_sessions():
    row = {"session_id": "s", "p1_agent": "1", "p2_agent": "0", "p1_age": "70", "p2_age": "25", "p1_gender": "female",
           "p2_gender": "male", "demographics_visible": "False"}
    assert I.population(row) == {1: {"persona_id": "s:p1", "attributes": {"age": 70, "gender": "female"}},
                                 0: {"persona_id": "s:p2", "attributes": {"age": 25, "gender": "male"}}}

    class Plan:
        visibility = {"speed": True, "size": True, "age": True, "gender": True, "task": False}

    assert I.visibility(Plan(), row) == {"speed": True, "size": True, "age": False, "gender": False, "task": False}


# --- the experiment ------------------------------------------------------------------------------


def rules_of_every_kind():
    return [
        extracted("x_head_on_valid", sentence_for("valid")),
        extracted("x_head_on_room", sentence_for("valid_keeps_room")),
        extracted("x_head_on_comm", sentence_for("valid", "People nod"), category="needs_communication", factors=("signalled",)),
        extracted("x_head_on_limit", sentence_for("format_limit")),
        extracted("x_head_on_none", sentence_for("no_rule")),
        extracted("x_head_on_unstable", sentence_for("valid", "Some people"), status="unstable"),
    ]


def test_the_experiment_translates_writes_replays_and_screens_and_a_rerun_changes_nothing(tmp_path):
    folder = make_extraction(tmp_path / "x", rules_of_every_kind())
    config = config_for(folder, screening={"enabled": True, "repeats": 1, "scenario_overrides": SMALL_CROWD})
    out = tmp_path / "out"
    result = T.run_translation(config, out_root=out, report=lambda _: None, git=GIT)
    assert result.status == T.STATUS_COMPLETED and len(result.executed) == 5  # the unstable rule is not translated
    counts = result.summary["counts"]
    assert counts["categories"] == {"valid": 3, "format_limit": 1, T.NOT_EXPRESSIBLE: 1}
    assert counts["written"] == 3 and counts["runnable_in_orca"] == 2
    assert counts["needs_communication_extracted"] == 1 and counts["needs_communication_written_not_runnable"] == 1
    by = {entry["extracted_rule_id"]: entry for entry in result.summary["rules"]}
    for runnable in ("x_head_on_valid", "x_head_on_room"):
        kinds = [entry["kind"] for entry in by[runnable]["screening"]]
        assert kinds == ["replay", "crowd"] and by[runnable]["screening_version"] == 2
        identity = by[runnable]["screening"][0]["results"]["identity"]
        assert identity["sessions"] == len(SESSIONS) and identity["plain_not_the_recorded_run"] == 0
        assert (out / "tr" / T.IDENTITY_DIR / f"{by[runnable]['staged_rule_id']}.csv").is_file()
    assert "screening" not in by["x_head_on_comm"] and by["x_head_on_comm"]["staged_rule_id"] == "ext_head_on_comm"
    files = sorted(p.name for p in (out / "tr" / T.STAGING_DIR / "rules").iterdir())
    assert files == ["ext_head_on_comm.v1.yaml", "ext_head_on_room.v1.yaml", "ext_head_on_room.v2.yaml",
                     "ext_head_on_valid.v1.yaml", "ext_head_on_valid.v2.yaml"]
    RuleDatabase.load(out / "tr" / T.STAGING_DIR)
    report = (out / "tr" / "report.md").read_text(encoding="utf-8")
    assert "not runnable in ORCA" in report and "format_limit" in report
    before = {p: p.read_bytes() for p in (out / "tr").rglob("*") if p.is_file() and p.name != "invocations.jsonl"}
    again = T.run_translation(config, out_root=out, report=lambda _: None, git=GIT)
    assert again.executed == [] and len(again.skipped) == 5
    after = {p: p.read_bytes() for p in (out / "tr").rglob("*") if p.is_file() and p.name != "invocations.jsonl"}
    assert after == before  # nothing translated, written, replayed or screened again


def test_a_changed_config_is_refused_once_translations_exist(tmp_path):
    folder = make_extraction(tmp_path / "x", [extracted("x_head_on_a", sentence_for("valid_keeps_room"))])
    T.run_translation(config_for(folder, identity={"enabled": False}), out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    changed = config_for(folder, identity={"enabled": False}, llm={"client": "mock", "temperature": 0.5, "transport_retries": 0})
    with pytest.raises(ConfigError, match="new experiment_name"):
        T.run_translation(changed, out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    # what is done after the calls may change: the identity check is run on the second invocation
    later = T.run_translation(config_for(folder), out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    assert later.summary["rules"][0]["screening"][0]["kind"] == "replay"


class PaidMock(MockClient):
    """The mock's replies and token counts, under the paid client's name, so that it is charged."""

    name = "deepseek"


def test_a_paid_translation_sends_nothing_without_confirm_and_translates_only_candidates(tmp_path):
    folder = make_extraction(tmp_path / "x", rules_of_every_kind())

    class Refusing(MockClient):
        name = "deepseek"

        def complete(self, request):  # pragma: no cover - must not be reached
            raise AssertionError("a paid call was made")

    result = T.run_translation(config_for(folder), client=Refusing(), out_root=tmp_path / "out", report=lambda _: None, git=GIT)
    assert result.status == T.STATUS_AWAITING and not (tmp_path / "out" / "tr" / T.TRANSLATIONS_DIR).exists()
    assert json.loads((tmp_path / "out" / "tr" / "preview.json").read_text(encoding="utf-8"))["usd_total"] > 0
    with pytest.raises(ConfigError, match="only candidate rules"):
        T.run_translation(config_for(folder, name="tr2", statuses=["candidate", "unstable"]), client=Refusing(), out_root=tmp_path / "out",
                          confirm=True, report=lambda _: None, git=GIT)


def test_the_budget_guard_stops_a_paid_translation_at_the_cap_and_a_rerun_redoes_only_the_aborted_one(tmp_path):
    from negsim.llm.base import LLMRequest

    # The same rule under two ids: the two prompts are the same, so the first call fits under this
    # cap, and once it is charged the second cannot.
    sentence = sentence_for("valid_keeps_room")
    folder = make_extraction(tmp_path / "x", [extracted("x_head_on_a", sentence), extracted("x_head_on_b", sentence)])
    ledger = tmp_path / "ledger.jsonl"
    probe = config_for(folder)
    plan_ = T.plan(probe)
    guard = BudgetGuard(SpendLedger(ledger), 1.0, PriceTable.from_yaml())
    worst = guard.worst_case(LLMRequest(plan_.items[0].rendered.messages, "deepseek-flash", 0.0, probe.llm["max_tokens"]))
    config = config_for(folder, identity={"enabled": False}, budget={"cap_usd": worst + 1e-9})

    def client(cfg):
        guard = BudgetGuard(SpendLedger(ledger), cfg.budget["cap_usd"], PriceTable.from_yaml(), scope=cfg.experiment_name)
        return BudgetedClient(PaidMock(policy=M.POLICIES["translate_rehearsal_v1"]), guard)

    first = T.run_translation(config, client=client(config), out_root=tmp_path / "out", confirm=True, report=lambda _: None, git=GIT)
    assert first.status == T.STATUS_PARTIAL and "budget" in first.aborted and first.executed == ["x_head_on_a", "x_head_on_b"]
    entries = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
    assert len(entries) == 1 and entries[0]["experiment"] == "tr"
    bigger = config_for(folder, identity={"enabled": False}, budget={"cap_usd": 1.0})
    again = T.run_translation(bigger, client=client(bigger), out_root=tmp_path / "out", confirm=True, report=lambda _: None, git=GIT)
    assert again.skipped == ["x_head_on_a"] and again.executed == ["x_head_on_b"] and again.status == T.STATUS_COMPLETED
    assert (tmp_path / "out" / "tr" / T.TRANSLATIONS_DIR / "x_head_on_b.aborted1.json").is_file()
    total = math.fsum(json.loads(line)["cost_usd"] for line in ledger.read_text(encoding="utf-8").splitlines())
    assert again.summary["cost"]["actual_usd"] == pytest.approx(total)


def test_the_config_refuses_unknown_statuses_and_bad_crowd_people():
    for bad in ({"statuses": ["kept"]}, {"statuses": []}, {"screening": {"ages": ["old"]}}, {"screening": {"genders": ["other"]}},
                {"llm": {"mock_policy": "nope"}}):
        with pytest.raises(ConfigError):
            config_for("x", **bad)


def test_round_1s_config_translates_rf11s_candidates_with_no_paid_call_approved_yet():
    config = T.TranslationConfig.load(PACKAGE_ROOT / "configs/translation/round1_head_on.yaml")
    assert config.extraction == "runs/rf11_round1_head_on" and config.statuses == ("candidate",)
    assert config.budget["cap_usd"] == 0.0 and config.llm["client"] == "mock" and config.template == "translate_v1"
    assert config.screening is not None and config.screening.repeats == 2 and config.crowd_ages == (25, 70)


def test_the_command_line_plans_a_translation_and_refuses_overwrite(capsys):
    from negsim.experiment.cli import main

    assert main([str(PACKAGE_ROOT / "configs/translation/round1_head_on.yaml"), "--plan"]) == 0
    assert "rule translation of 4 rule(s)" in capsys.readouterr().out
    assert main([str(PACKAGE_ROOT / "configs/translation/round1_head_on.yaml"), "--overwrite"]) == 2
