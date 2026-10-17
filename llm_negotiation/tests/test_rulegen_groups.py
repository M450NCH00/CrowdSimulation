"""Issue #32, Parts 1.3 to 1.5: the fictional group in the design matrix, off by default; the
ethics sign-off a paid run needs; and the per-session outcome rows for analysis by group."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter

import pytest

from negsim.configutil import ConfigError
from negsim.personas.groups import DEFAULT_FRAMING, DEFAULT_GROUP_LABELS
from negsim.rulegen import experiment as rg
from negsim.rulegen.design import (
    ETHNICITY_FACTORS,
    FACTOR_LEVELS,
    FACTORS,
    DesignSettings,
    balance,
    cell_code,
    personas_of,
    sessions_for,
    visibility_of,
)
from negsim.rulegen.outcomes import OUTCOMES_FILE, case_snapshot, rule_effect

FULL = {name: list(levels) for name, levels in FACTOR_LEVELS.items()}
CASES = [("head_on_aaaaaaaa", 1, (0, 1)), ("flow_bbbbbbbb", 1, (13, 51))]
GROUPS = {"enabled": True}
GIT = {"commit": "test", "dirty": False}
SIGN_OFF = "Ethics sign-off for the fictional-group factor (issue #32): approved by the supervisor on 2026-11-02"


def settings(**changes):
    return DesignSettings.from_config({"seed": 7, "factors": FULL, **changes})


def old_cell_code(cell):
    """The cell code as issue #30 wrote it, before the fictional group."""
    return hashlib.sha256(json.dumps({name: cell[name] for name in FACTORS}, sort_keys=True).encode("utf-8")).hexdigest()[:8]


# --- the design ---------------------------------------------------------------------------------------


def test_a_design_without_the_group_has_the_cells_and_session_ids_it_had():
    plain = sessions_for(CASES, settings(), ["negotiated"], {}, "test")
    assert all(cell_code(session.cell) == old_cell_code(session.cell) for session in plain)
    assert all(set(session.cell) == set(FACTORS) and "framing" not in session.as_dict() for session in plain)
    assert all("ethnic_group" not in person for session in plain for person in session.personas.values())
    assert all(session.visibility["ethnic_group"] is False for session in plain)  # hidden, as by default
    off = sessions_for(CASES, settings(ethnicity={"enabled": False}), ["negotiated"], {}, "test")
    assert [session.as_dict() for session in off] == [session.as_dict() for session in plain]  # off is off
    assert "ethnicity" not in settings().as_dict() and settings(ethnicity={"enabled": False}).as_dict()["ethnicity"]["enabled"] is False


def test_with_the_group_on_its_three_factors_are_crossed_in_full_and_balanced():
    design = settings(ethnicity=GROUPS)
    assert design.factors == FACTORS + ETHNICITY_FACTORS
    assert design.cells_per_case() == 3 * 4 * 3 * 2 * 2 * 2 * (2 * 3 * 2) == 3456  # the full factorial, per case
    sessions = sessions_for(CASES[:1], design, ["negotiated"], {}, "test")
    assert len(sessions) == 3456 and len({session.session_id for session in sessions}) == 3456
    for counts in balance(sessions).values():
        for name in (*FACTORS, *ETHNICITY_FACTORS):
            assert len(set(counts[name].values())) == 1, (name, counts[name])
    for first, second in itertools.product(ETHNICITY_FACTORS, (*FACTORS, *ETHNICITY_FACTORS)):
        if first != second:
            pairs = Counter((str(session.cell[first]), str(session.cell[second])) for session in sessions)
            assert len(set(pairs.values())) == 1, (first, second)


def test_the_rotation_gives_each_label_to_each_person_equally_often():
    design = settings(ethnicity=GROUPS)
    assert DEFAULT_GROUP_LABELS == ("Kestrop", "Dremmik", "Pellund")
    groups = design.groups
    assert [groups.labels_of({"group_pair": "same", "label_rotation": r}) for r in range(3)] == [
        ("Kestrop", "Kestrop"), ("Dremmik", "Dremmik"), ("Pellund", "Pellund"),
    ]
    assert [groups.labels_of({"group_pair": "different", "label_rotation": r}) for r in range(3)] == [
        ("Kestrop", "Dremmik"), ("Dremmik", "Pellund"), ("Pellund", "Kestrop"),
    ]
    sessions = sessions_for(CASES[:1], design, ["negotiated"], {}, "test")
    for pair in ("same", "different"):
        mine = [session for session in sessions if session.cell["group_pair"] == pair]
        for slot in (0, 1):  # person 1, person 2
            labels = Counter(groups.labels_of(session.cell)[slot] for session in mine)
            assert set(labels) == set(DEFAULT_GROUP_LABELS) and len(set(labels.values())) == 1, (pair, slot, labels)


def test_each_person_carries_its_group_and_the_cell_alone_decides_whether_it_is_seen():
    design = settings(ethnicity=GROUPS)
    cell = {
        "age_pair": "same", "gender_pair": "same_female", "task": "none", "demographics_visible": False,
        "mapping": "p1_higher", "order": "lower_first", "group_pair": "different", "label_rotation": 2, "ethnicity_visible": True,
    }
    people = personas_of(cell, (13, 51), design)
    assert people[51]["ethnic_group"] == "Pellund" and people[13]["ethnic_group"] == "Kestrop"  # person 1 is the higher agent
    seen = visibility_of(cell)
    assert seen["ethnic_group"] is True and seen["age"] is False and seen["gender"] is False  # apart from demographics
    hidden = visibility_of({**cell, "ethnicity_visible": False, "demographics_visible": True})
    assert hidden["ethnic_group"] is False and hidden["age"] is True
    assert visibility_of({key: value for key, value in cell.items() if key not in ETHNICITY_FACTORS})["ethnic_group"] is False
    assert "ethnic_group" not in personas_of(cell, (13, 51), settings())[13]  # no group without the factor


def test_the_framing_and_the_labels_are_settings_recorded_with_every_session():
    design = settings(ethnicity={"enabled": True, "labels": ["Pellund", "Kestrop", "Dremmik", "Brannoq"], "framing": "community"})
    assert design.groups.labels == ("Pellund", "Kestrop", "Dremmik", "Brannoq") and design.groups.framing == "community"
    assert design.groups.levels["label_rotation"] == (0, 1, 2, 3)
    (session, *_) = sessions_for(CASES[:1], design, ["stated"], {"stated": 1}, "test")
    described = session.as_dict()
    assert described["framing"] == "community" and {"group_pair", "label_rotation", "ethnicity_visible"} <= set(described["cell"])
    assert settings(ethnicity=GROUPS).groups.framing == DEFAULT_FRAMING == "ethnic group"
    narrowed = settings(ethnicity={"enabled": True, "factors": {"group_pair": ["different"], "ethnicity_visible": [True]}})
    assert narrowed.cells_per_case() == 288 * 3


@pytest.mark.parametrize(
    "block, message",
    [
        ({}, "missing required key"),
        ({"enabled": "yes"}, "expected true or false"),
        ({"enabled": True, "labels": ["Kestrop", "Dremmik"]}, "at least 3 labels"),
        ({"enabled": True, "labels": ["Kestrop", "Dremmik", "Malay"]}, "real group"),
        ({"enabled": True, "labels": ["Kestrop", "Dremmik", "the Pellund people"]}, "one capitalised word"),
        ({"enabled": True, "framing": "Ethnic Group!"}, "lower-case words"),
        ({"enabled": True, "factors": {"label_rotation": [3]}}, "unknown level"),
        ({"enabled": True, "factors": {"label_rotation": [True]}}, "unknown level"),
        ({"enabled": True, "factors": {"ethnicity_visible": [1]}}, "unknown level"),
        ({"enabled": True, "factors": {"group_pair": ["same", "same"]}}, "listed twice"),
        ({"enabled": True, "factors": {"religion": ["a"]}}, "unknown key"),
        ({"enabled": True, "description": "a proud mountain people"}, "unknown key"),  # labels carry no description
    ],
)
def test_a_bad_group_block_is_refused(block, message):
    with pytest.raises(ConfigError, match=message):
        settings(ethnicity=block)


# --- off by default, and the sign-off a paid run needs ---------------------------------------------


def raw_config(**changes):
    raw = {
        "layer": "rule_generation",
        "experiment_name": "rg_groups",
        "cases": {"set": "si3_v1", "ids": ["head_on_de176842"]},
        "conditions": ["negotiated", "stated"],
        "design": {
            "seed": 32,
            "factors": {
                "age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["none"],
                "demographics_visible": [True], "mapping": ["p1_lower"], "order": ["lower_first", "higher_first"],
            },
            "ethnicity": {"enabled": True, "factors": {"label_rotation": [0]}},
        },
        "statement": {"repeats": 1},
        "llm": {"client": "mock", "mock_policy": "rulegen_paths"},
        "replay": {"enabled": False},
        "screening": {"enabled": False},
    }
    raw.update(changes)
    return raw


def config(**changes):
    return rg.RuleGenConfig.from_raw(raw_config(**changes), "test")


def quiet(*_):
    pass


def test_every_shipped_config_leaves_the_group_off():
    from negsim.configutil import PACKAGE_ROOT

    for path in sorted((PACKAGE_ROOT / "configs" / "rule_generation").glob("*.yaml")):
        loaded = rg.RuleGenConfig.load(path)
        if "mock_groups" not in path.name:  # a mock rehearsal of the group switches it on explicitly
            assert loaded.design.groups is None, path.name


def test_the_sign_off_is_one_exact_sentence_in_claude_md(tmp_path):
    claude = tmp_path / "CLAUDE.md"
    assert not rg.ethnicity_signed_off(claude)  # no file
    claude.write_text("Ethics sign-off from the supervisor: pending unless recorded otherwise.\n", encoding="utf-8")
    assert not rg.ethnicity_signed_off(claude)
    claude.write_text("## Approvals\n- " + SIGN_OFF + ".\n", encoding="utf-8")
    assert rg.ethnicity_signed_off(claude)
    assert not rg.ethnicity_signed_off(tmp_path / "missing.md")


def test_the_repository_records_no_sign_off_yet():
    """Nothing in this issue may claim the supervisor's approval (Part 1.4)."""
    assert not rg.ethnicity_signed_off()


def test_a_paid_run_with_the_group_on_is_refused_until_the_sign_off_is_recorded(tmp_path, monkeypatch):
    paid = config(llm={"client": "deepseek"}, budget={"cap_usd": 100.0, "ledger": str(tmp_path / "ledger.jsonl")})
    with pytest.raises(ConfigError, match="ethics sign-off is not recorded in CLAUDE.md"):
        rg.run_rule_generation(paid, out_root=tmp_path, confirm=True, report=quiet, git=GIT)
    folder = tmp_path / "rg_groups"
    assert not (folder / rg.SESSIONS_DIR).exists() and not (tmp_path / "ledger.jsonl").exists()
    (line,) = (folder / rg.INVOCATIONS_FILE).read_text(encoding="utf-8").splitlines()
    assert json.loads(line)["status"] == "refused_no_sign_off"
    # With the sentence recorded, the run goes on to the next check: confirmation.
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(SIGN_OFF + "\n", encoding="utf-8")
    monkeypatch.setattr(rg, "SIGN_OFF_FILE", claude)
    assert rg.run_rule_generation(paid, out_root=tmp_path, report=quiet, git=GIT).status == "awaiting_confirmation"
    # A paid run with the group off, and any mock run, need no sign-off.
    monkeypatch.setattr(rg, "SIGN_OFF_FILE", tmp_path / "missing.md")
    off_design = {**raw_config()["design"], "ethnicity": {"enabled": False}}
    off = config(llm={"client": "deepseek"}, budget={"cap_usd": 100.0}, experiment_name="rg_groups_off", design=off_design)
    assert rg.run_rule_generation(off, out_root=tmp_path, report=quiet, git=GIT).status == "awaiting_confirmation"


# --- the outcome rows ----------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def grouped(tmp_path_factory):
    out = tmp_path_factory.mktemp("groups")
    result = rg.run_rule_generation(config(), out_root=out, report=quiet, git=GIT)
    folder = result.experiment_dir
    rows = [json.loads(line) for line in (folder / OUTCOMES_FILE).read_text(encoding="utf-8").splitlines()]
    records = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in (folder / rg.SESSIONS_DIR).glob("*.json")}
    return result, rows, records


def test_every_session_has_an_outcome_row_with_what_to_stratify_by(grouped):
    result, rows, records = grouped
    assert len(rows) == len(records) == 2 * 2 * 2 * (1 + 1)  # order x group pair x shown, in A and in B
    for row in rows:
        session = records[row["session_id"]]["session"]
        assert row["groups_on"] and row["framing"] == "ethnic group" and row["label_rotation"] == 0
        assert row["group_pair"] == session["cell"]["group_pair"] and row["ethnicity_visible"] == session["cell"]["ethnicity_visible"]
        labels = {agent: person["ethnic_group"] for agent, person in row["people"].items()}
        assert labels == {agent: person["ethnic_group"] for agent, person in session["personas"].items()}
        assert (len(set(labels.values())) == 1) == (row["group_pair"] == "same")
        assert row["outcome"] == records[row["session_id"]]["outcome"]


def test_the_rows_say_who_proposed_who_conceded_and_who_got_the_larger_share(grouped):
    _, rows, records = grouped
    agreed = [row for row in rows if row["outcome"] == "agreed"]
    assert agreed
    for row in agreed:
        agreement = records[row["session_id"]]["agreement"]
        assert (row["proposed_by"], row["conceded_by"]) == (agreement["proposed_by"], agreement["accepted_by"])
        assert row["proposed_by"] != row["conceded_by"] and sum(row["proposals_by"].values()) >= 1
    for row in rows:
        if row["category"] == "valid":
            effect = row["effect"]
            assert effect["loads"]
            assert effect["larger_share"] in (("equal", *row["agents"]) if effect["matches"] else (None,))
        if row["outcome"] not in ("agreed", "stated"):
            assert row["effect"] is None and row["conceded_by"] is None


def test_the_summary_counts_outcomes_by_group_pair_and_visibility_and_reports_the_design_size(grouped):
    result, rows, _ = grouped
    summary = result.summary
    assert summary["groups"]["on"] is True
    assert set(summary["groups"]["strata"]) == {
        f"{condition}/{pair}/{shown}" for condition in ("negotiated", "stated") for pair in ("same", "different") for shown in ("shown", "hidden")
    }
    assert sum(entry["sessions"] for entry in summary["groups"]["strata"].values()) == len(rows)
    design = summary["design"]
    assert design["groups_on"] and design["cells_per_case"] == {"head_on_de176842": 8}
    assert design["factors"]["label_rotation"] == 1 and design["sessions"] == 16


@pytest.fixture(scope="module")
def version_2(tmp_path_factory):
    """Prompt version 2 with the mock's paths of issue #32, the group on, two cases."""
    cfg = config(
        experiment_name="rg_prompt_v2",
        cases={"set": "si3_v1", "ids": ["head_on_de176842", "overtaking_2d08db11"]},
        negotiation={"template": "rulegen_negotiate_v2"},
        statement={"template": "rulegen_state_v2", "repeats": 1},
        llm={"client": "mock", "mock_policy": "rulegen_paths_v2"},
    )
    result = rg.run_rule_generation(cfg, out_root=tmp_path_factory.mktemp("v2"), report=quiet, git=GIT)
    folder = result.experiment_dir
    validations = [json.loads(line) for line in (folder / rg.VALIDATION_FILE).read_text(encoding="utf-8").splitlines()]
    records = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in (folder / rg.SESSIONS_DIR).glob("*.json")}
    return result, validations, records


def test_the_mocks_new_paths_come_after_its_old_ones_which_are_unchanged():
    from negsim.rulegen import mock

    assert mock.NEGOTIATION_PATHS_V2[: len(mock.NEGOTIATION_PATHS)] == mock.NEGOTIATION_PATHS and len(mock.NEGOTIATION_PATHS) == 13
    assert mock.NEGOTIATION_PATHS_V2[13:] == ("protected_attribute", "valid_back_up", "inconsistent_back_up")
    assert mock.STATEMENT_PATHS_V2[len(mock.STATEMENT_PATHS):] == ("protected_attribute", "valid_back_up", "inconsistent_back_up")
    assert {"rulegen_paths", "rulegen_paths_v2", "rulegen_agree"} == set(mock.POLICIES)


def test_with_prompt_version_2_every_new_path_is_taken_and_categorised(version_2):
    from negsim.rulegen.validate import CATEGORIES

    result, validations, records = version_2
    assert result.status == "completed" and len(records) == 32
    assert all(record["rule_schema_version"] == 3 for record in records.values())
    found = Counter((row["condition"], row["category"], row["loader_category"]) for row in validations)
    for condition in ("negotiated", "stated"):
        assert {row["category"] for row in validations if row["condition"] == condition} == set(CATEGORIES), condition
        assert found[(condition, "protected_attribute", "protected_attribute")] >= 1
        assert found[(condition, "inconsistent", "back_up")] >= 1
    backing = [row for row in validations if "agent.segment_distance_travelled" in row["fields"]]
    assert backing and {row["category"] for row in backing} <= {"valid", "inconsistent"}
    assert any(row["category"] == "valid" for row in backing)


def test_a_rule_written_from_prompt_version_2_is_of_rule_format_3(version_2):
    result, _, _ = version_2
    folder = result.experiment_dir
    written = [json.loads(line) for line in (folder / rg.WRITTEN_FILE).read_text(encoding="utf-8").splitlines()]
    from negsim.rulegen.writer import StagingDatabase

    formats = set()
    for entry in written:
        rule = StagingDatabase(folder / "rule_db_staging" / entry["condition"]).latest(entry["rule_id"])
        formats.add(rule.schema_version)
        if "backer" in rule.directives:
            assert rule.directives["backer"].back_up is True
    assert formats == {3}
    assert any("backer" in StagingDatabase(folder / "rule_db_staging" / entry["condition"]).latest(entry["rule_id"]).directives for entry in written)


def test_a_rules_effect_is_read_on_the_cases_pair_with_the_sessions_people():
    case = {
        "snapshot": {
            "step": 3, "time_s": 0.3, "agents": [0, 1],
            "pair": {"encounter_class": "head_on", "distance_m": 9.0, "closing_speed_mps": 2.6, "time_to_collision_s": 3.3,
                     "heading_difference_rad": 3.1, "min_corridor_width_m": 1.75, "age_difference_years": None},
            "agent": {str(agent): {"age": None, "gender": None, "speed_mps": 1.3, "radius_m": 0.25, "time_to_segment_s": None} for agent in (0, 1)},
        },
    }
    session = {
        "visibility": {"age": True, "gender": True, "speed": True, "size": True},
        "personas": {"0": {"age": 25, "gender": "female"}, "1": {"age": 70, "gender": "male"}},
    }
    snapshot = case_snapshot(case, session)
    assert snapshot.agent_values[1]["age"] == 70 and snapshot.pair["age_difference_years"] == 45
    younger_yields = {
        "encounter": "head_on", "when": {"all": []},
        "roles": {"by": {"field": "agent.age", "order": "ascending", "assign": ["yielder", "other"], "tie": "no_match"}},
        "directive": {"yielder": {"responsibility_share": 1.0}, "other": {"responsibility_share": 0.0}}, "priority": 10,
    }
    effect = rule_effect(younger_yields, case, session)
    assert effect["matches"] and effect["roles"] == {"0": "yielder", "1": "other"} and effect["larger_share"] == 0
    hidden = rule_effect(younger_yields, case, {**session, "visibility": {**session["visibility"], "age": False}})
    assert hidden["loads"] and not hidden["matches"]  # the ages are not shown: the two cannot be ordered
    broken = rule_effect({"encounter": "head_on"}, case, session)
    assert (broken["loads"], broken["reason"]) == (False, "schema")
