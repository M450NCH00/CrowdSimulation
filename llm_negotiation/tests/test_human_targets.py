"""Issue #122 (RF-37): human target files: every target names its source, and the file is frozen."""

from __future__ import annotations

import copy

import pytest

from negsim.configutil import PACKAGE_ROOT, ConfigError, load_yaml
from negsim.human_targets import targets as T
from negsim.rules.database import file_sha256

HEAD_ON = T.TARGETS_DIR / "head_on_v1.yaml"
REPO = PACKAGE_ROOT.parent
#: The target files are frozen: a change is a new file (pinned when each was written, issue #122).
FROZEN = {
    "head_on_v1.yaml": "7b732845fd93b8e292cc032212e876c49755e01975e40bbe5803914572c50cb1",
}


@pytest.fixture(scope="module")
def head_on():
    return T.TargetFile.load(HEAD_ON)


@pytest.fixture()
def raw():
    return copy.deepcopy(load_yaml(HEAD_ON))


def test_the_target_files_are_frozen():
    for name, sha in FROZEN.items():
        assert file_sha256(T.TARGETS_DIR / name) == sha
    assert sorted(path.name for path in T.TARGETS_DIR.glob("*.yaml")) == sorted(FROZEN)


def test_every_target_names_a_source_whose_copy_is_cached(head_on):
    assert sorted(head_on.targets) == ["C1", "C3", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"]
    for target in head_on.targets.values():
        assert target.source in head_on.sources
        assert target.where and target.read in T.READ and target.setting
    for key, entry in head_on.sources.items():
        assert (REPO / entry["cached"]).is_file(), key
    for place in head_on.sides["places"].values():
        assert place["source"] in head_on.sources


def test_the_tolerances_are_the_users_of_task_0(head_on):
    assert head_on.tolerance == {"value": "within_1_sd", "no_spread": "direction_only",
                                 "disagreement": "report_no_verdict", "decided": "2026-10-30"}
    assert head_on.targets["H1"].band == (0.76, 1.1)   # Rapos2021: 0.93 +/- 0.17 m
    assert head_on.targets["H2"].band == (0.61, 0.97)  # 0.79 +/- 0.18 m
    assert head_on.targets["H3"].band is None and head_on.targets["H3"].check == "increases_with_speed"


def test_another_tolerance_is_refused(raw):
    raw["tolerance"]["value"] = "within_2_sd"
    with pytest.raises(ConfigError, match="tolerance.value"):
        T.TargetFile.from_mapping(raw, "x")


def test_the_two_studies_that_disagree_on_slowing_point_at_each_other(head_on):
    assert head_on.targets["H4"].disagrees_with == "H5" and head_on.targets["H5"].disagrees_with == "H4"


def test_a_one_sided_disagreement_is_refused(raw):
    del raw["targets"]["H5"]["disagrees_with"]
    with pytest.raises(ConfigError, match="disagrees back"):
        T.TargetFile.from_mapping(raw, "x")


def test_a_target_without_a_listed_source_is_refused(raw):
    raw["targets"]["H1"]["source"] = "someone2020"
    with pytest.raises(ConfigError, match="without a source is not a target"):
        T.TargetFile.from_mapping(raw, "x")


def test_a_measure_nothing_computes_is_refused(raw):
    raw["targets"]["H1"]["measure"] = "politeness"
    with pytest.raises(ConfigError, match="measure"):
        T.TargetFile.from_mapping(raw, "x")


def test_a_direction_target_cannot_carry_a_value(raw):
    raw["targets"]["H3"]["value"] = 2.4
    raw["targets"]["H3"]["sd"] = 0.3
    with pytest.raises(ConfigError, match="direction target has no value"):
        T.TargetFile.from_mapping(raw, "x")


def test_a_value_target_needs_a_positive_sd(raw):
    raw["targets"]["H1"]["sd"] = 0
    with pytest.raises(ConfigError, match="sd"):
        T.TargetFile.from_mapping(raw, "x")


def test_an_unknown_age_group_is_refused(raw):
    raw["targets"]["H1"]["applies"]["pair_ages"] = ["teen", "young"]
    with pytest.raises(ConfigError, match="age_groups"):
        T.TargetFile.from_mapping(raw, "x")


def test_the_side_is_not_judged_while_singapores_is_unknown(head_on, raw):
    assert head_on.sides["judged"] is False and head_on.sides["singapore"] == "unknown"
    raw["sides"]["judged"] = True
    with pytest.raises(ConfigError, match="not judged"):
        T.TargetFile.from_mapping(raw, "x")


def test_what_was_left_out_is_listed_with_its_reason(head_on, raw):
    assert [entry["id"] for entry in head_on.not_targets] == ["C2", "H9"]
    assert "model" in head_on.not_targets[0]["reason"]
    raw["not_targets"][0]["id"] = "H1"
    with pytest.raises(ConfigError, match="also a target"):
        T.TargetFile.from_mapping(raw, "x")


def test_every_comparison_whose_setting_differs_says_so(head_on):
    assert {t.id for t in head_on.targets.values() if not t.setting_differs} == {"H5"}  # Moussaid2009's corridor, as round 1's
