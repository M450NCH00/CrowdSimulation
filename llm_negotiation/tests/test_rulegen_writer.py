"""Issue #30, Part 8: the rule writer, the staging databases, and promotion with a reason."""

from __future__ import annotations

import json
import shutil

import pytest

from negsim.rules.canonical import canonical_hash
from negsim.rules.database import RULE_DB_ROOT, RULE_FILE, RuleDatabase
from negsim.rulegen import cli
from negsim.rulegen.writer import StagingDatabase, Support, WriterError, build_rule, promote, rule_id_for, with_screening

KEEP_ROOM = {"encounter": "any", "when": {"all": []}, "roles": "symmetric", "directive": {"both": {"clearance_margin": 0.15}}, "priority": 100, "intent": "Both keep more room."}
CELL = {"age_pair": "same", "gender_pair": "same_female", "task": "none", "demographics_visible": True, "mapping": "p1_lower", "order": "lower_first"}
TEMPLATE = {"key": "rulegen_negotiate_v1", "sha256": "0" * 64, "uses": {"key": "rulegen_common_v1", "sha256": "1" * 64}}
DIGEST = canonical_hash(KEEP_ROOM)


def support(session_id="A_head_on_x_r1", when="2026-10-16T01:00:00+00:00", proposal=KEEP_ROOM, **changes):
    fields = dict(
        session_id=session_id, design_cell=CELL, model="deepseek-flash", model_returned="deepseek-v4-flash",
        prompt_template=TEMPLATE, created_utc=when, proposed_by=0, repeat=1, proposal=proposal,
    )
    return Support(**{**fields, **changes})


def built(*supports, condition="negotiated"):
    return build_rule(condition, "head_on_de176842", DIGEST, list(supports) or [support()], "test_experiment")


def test_the_id_is_the_writers_deterministic_and_a_valid_rule_file_name():
    assert rule_id_for("negotiated", "head_on_de176842", DIGEST) == f"neg_head_on_de176842_{DIGEST[:10]}"
    assert rule_id_for("stated", "flow_03ea57f6", DIGEST).startswith("st_flow_03ea57f6_")
    assert RULE_FILE.match(f"{rule_id_for('negotiated', 'overtaking_23c5d31e', DIGEST)}.v1.yaml")


def test_the_writer_fills_the_metadata_and_ignores_the_models():
    sneaky = {**KEEP_ROOM, "rule_id": "the_models_own_id", "version": 9, "status": "validated", "provenance": {"source_type": "hand_written", "author": "MODEL-WROTE-THIS"}, "screening": [{"kind": "crowd"}]}
    rule = built(support(proposal=sneaky), condition="stated")
    assert (rule["rule_id"], rule["version"], rule["status"], rule["schema_version"]) == (rule_id_for("stated", "head_on_de176842", DIGEST), 1, "candidate", 2)
    assert "screening" not in rule and rule["provenance"]["source_type"] == "stated" and not {"MODEL-WROTE-THIS", "the_models_own_id", "validated", "hand_written"} & set(json.dumps(rule).replace('"', " ").split())
    generation = rule["provenance"]["generation"]
    assert (generation["experiment"], generation["case_id"], generation["canonical_hash"]) == ("test_experiment", "head_on_de176842", DIGEST)
    assert generation["sessions"][0] == {
        "session_id": "A_head_on_x_r1", "design_cell": CELL, "model": "deepseek-flash", "model_returned": "deepseek-v4-flash",
        "prompt_template": TEMPLATE, "created_utc": "2026-10-16T01:00:00+00:00", "proposed_by": 0, "repeat": 1,
    }
    assert "deepseek-v4-flash" in rule["provenance"]["author"] and "rulegen_negotiate_v1" in rule["provenance"]["author"]
    assert {key: rule[key] for key in ("encounter", "when", "roles", "directive", "priority", "intent")} == {key: KEEP_ROOM[key] for key in ("encounter", "when", "roles", "directive", "priority", "intent")}


def test_one_rule_from_several_sessions_takes_its_words_from_the_earliest():
    later = support("A_head_on_y_r1", "2026-10-16T02:00:00+00:00", {**KEEP_ROOM, "priority": 50, "intent": "Said otherwise."})
    rule = built(later, support())
    assert [entry["session_id"] for entry in rule["provenance"]["generation"]["sessions"]] == ["A_head_on_x_r1", "A_head_on_y_r1"]
    assert (rule["priority"], rule["intent"]) == (100, "Both keep more room.")
    with pytest.raises(WriterError, match="at least one session"):
        build_rule("negotiated", "c", DIGEST, [], "e")


def test_a_staging_database_is_laid_out_as_the_rule_database_and_only_grows(tmp_path):
    staging = StagingDatabase(tmp_path / "rule_db_staging" / "negotiated")
    staging.create()
    staging.create()  # idempotent
    rule = built()
    name, written = staging.write(rule, "a note")
    assert written and (staging.root / name).is_file() and name == f"rules/{rule['rule_id']}.v1.yaml"
    manifest = json.loads(staging.manifest_path.read_text(encoding="utf-8"))
    assert set(manifest["files"]) == {"schema/rule.v1.schema.json", "schema/rule.v2.schema.json", name}
    loaded = staging.load().get(rule["rule_id"], 1)
    assert loaded.status == "candidate" and loaded.provenance["generation"]["case_id"] == "head_on_de176842"
    assert staging.write(rule, "again") == (name, False)
    with pytest.raises(WriterError, match="frozen with other contents"):
        staging.write({**rule, "priority": 7}, "an edit")


def test_staging_is_idempotent_and_grows_by_versions(tmp_path):
    staging = StagingDatabase(tmp_path / "staging")
    staging.create()
    one = built()
    assert staging.stage(one, "first")[1:] == (1, True)
    assert staging.stage(one, "again")[1:] == (1, False)
    screened = with_screening(one, [{"kind": "replay", "experiment": "test_experiment", "scenario": "wide_corridor_head_on", "baseline": "orca_perturbed_v1", "case_id": "head_on_de176842", "seeds": [1], "screened_utc": "now", "verdict": "recorded", "reasons": [], "results": {}}])
    staging.write(screened, "screened")
    two = built(support(), support("A_head_on_y_r1", "2026-10-16T02:00:00+00:00"))
    name, version, written = staging.stage(two, "more sessions")
    assert (version, written) == (3, True)
    third = staging.latest(one["rule_id"])
    assert third.version == 3 and len(third.screening) == 1  # the screening is kept: what the rule does is the same
    assert len(third.provenance["generation"]["sessions"]) == 2 and "adds 1 supporting session" in third.provenance["notes"]
    assert staging.stage(two, "same")[1:] == (3, False)
    newest = max((r for r in staging.load().rules if r.rule_id == one["rule_id"]), key=lambda r: r.version)
    assert (third.key, third.sha256, third.source) == (newest.key, newest.sha256, newest.source)  # read alone, as the whole database reads it
    assert staging.latest("not_there") is None
    with pytest.raises(WriterError, match="no longer support it"):
        staging.stage(built(support("A_other_r1")), "fewer")
    (staging.root / third.source).write_text("edited", encoding="utf-8")
    with pytest.raises(WriterError, match="not the version frozen"):
        staging.latest(one["rule_id"])


def test_promotion_needs_a_reason_and_records_it(tmp_path):
    staging = StagingDatabase(tmp_path / "staging")
    staging.create()
    rule = built()
    staging.write(rule, "staged")
    database = tmp_path / "rule_db"
    shutil.copytree(RULE_DB_ROOT, database)
    for reason in ("", "   ", None):
        with pytest.raises(WriterError, match="needs a reason"):
            promote(staging.root, rule["rule_id"], reason, database_root=database)
    path = promote(staging.root, rule["rule_id"], "  Checked by hand\n against the case. ", database_root=database, by="a test")
    promoted = RuleDatabase.load(database).get(rule["rule_id"], 1)  # the database still loads
    record = promoted.provenance["promotion"]
    assert record["reason"] == "Checked by hand against the case." and record["by"] == "a test"
    assert record["staged_rule"] == f"{rule['rule_id']}@1" and record["staged_sha256"] == staging.load().get(rule["rule_id"], 1).sha256
    assert path.name == f"{rule['rule_id']}.v1.yaml" and promoted.status == "candidate"
    assert promote(staging.root, rule["rule_id"], "again", database_root=database).name.endswith(".v2.yaml")
    with pytest.raises(WriterError, match="no rule"):
        promote(staging.root, "nothing_here", "why", database_root=database)
    with pytest.raises(WriterError, match="not 5"):
        promote(staging.root, rule["rule_id"], "why", version=5, database_root=database)
    assert not [r for r in RuleDatabase.load(RULE_DB_ROOT).rules if r.rule_id == rule["rule_id"]]  # the real rule_db is untouched


def test_the_command_line_lists_and_promotes_only_with_a_reason(tmp_path, capsys):
    staging = StagingDatabase(tmp_path / "staging")
    staging.create()
    rule = built()
    staging.write(rule, "staged")
    database = tmp_path / "rule_db"
    shutil.copytree(RULE_DB_ROOT, database)
    assert cli.main(["list", str(staging.root)]) == 0
    assert f"{rule['rule_id']}@1" in capsys.readouterr().out
    with pytest.raises(SystemExit) as refused:
        cli.main(["promote", str(staging.root), rule["rule_id"], "--database", str(database)])
    assert refused.value.code == 2  # argparse: --reason is required
    assert cli.main(["promote", str(staging.root), rule["rule_id"], "--reason", "a test", "--database", str(database)]) == 0
    assert "promoted" in capsys.readouterr().out
    assert cli.main(["promote", str(staging.root), rule["rule_id"], "--reason", " ", "--database", str(database)]) == 1
