"""Issue #122 (RF-37): judging a subject against the human targets, on hand-made records."""

from __future__ import annotations

import pytest

from negsim.human_targets import judge as J
from negsim.human_targets.targets import TARGETS_DIR, TargetFile


@pytest.fixture(scope="module")
def targets():
    return TargetFile.load(TARGETS_DIR / "head_on_v1.yaml")


def _pair(distance=0.9, shares=(0.5, 0.5), first="together", ages=(25, 25), seed=1, speed=1.3, starts=(2.0, 2.0),
          changes=(0.0, 0.0), sides=("right", "right"), assertiveness=("gives_way", "gives_way"), aids=(None, None)):
    per_agent = {str(i): {"lateral_share": shares[i], "turning_start_m": starts[i], "speed_change_mps": changes[i], "side": sides[i]}
                 for i in (0, 1)}
    return {"seed": seed, "speed_mps": speed, "agents": [0, 1], "passed_first": first,
            "people": [{"age": ages[i], "gender": "male", "assertiveness": assertiveness[i], "mobility_aid": aids[i]} for i in (0, 1)],
            "measures": {"min_centre_distance_m": distance, "per_agent": per_agent}}


def test_a_value_target_is_met_within_one_sd(targets):
    h1 = targets.targets["H1"]  # 0.93 +/- 0.17 m, two young adults
    assert J.judge(h1, targets, [_pair(0.80), _pair(1.0)], [])["verdict"] == J.WITHIN
    assert J.judge(h1, targets, [_pair(0.51)] * 3, [])["verdict"] == J.OUTSIDE
    assert J.judge(h1, targets, [_pair(0.9, ages=(70, 25))], [])["verdict"] == J.NOT_COMPARABLE  # not two young adults


def test_pairs_with_an_older_adult_are_h2s(targets):
    found = J.judge(targets.targets["H2"], targets, [_pair(0.7, ages=(25, 70)), _pair(0.9, ages=(25, 25))], [])
    assert found["n"] == 1 and found["verdict"] == J.WITHIN


def test_the_studies_that_disagree_on_slowing_get_no_verdict(targets):
    found = J.judge(targets.targets["H4"], targets, [_pair(changes=(0.3, 0.05))], [])
    assert found["verdict"] == J.NO_VERDICT and found["share_slowing"] == 0.5


def test_turning_earlier_at_a_higher_speed_agrees_with_h3(targets):
    pairs = [_pair(seed=s, speed=1.15, starts=(2.0, 2.0)) for s in range(10)]
    pairs += [_pair(seed=s, speed=1.78, starts=(2.6, 2.8)) for s in range(10)]
    found = J.judge(targets.targets["H3"], targets, pairs, [])
    assert found["verdict"] == J.AGREES and (found["study_way"], found["other_way"]) == (10, 0)
    assert J.judge(targets.targets["H3"], targets, pairs[:10], [])["verdict"] == J.NOT_COMPARABLE  # one speed


def test_the_giver_adapting_more_agrees_with_h6(targets):
    pairs = [_pair(shares=(0.3, 0.7), first=0) for _ in range(8)] + [_pair(first="together")]
    assert J.judge(targets.targets["H6"], targets, pairs, [])["verdict"] == J.AGREES
    assert J.judge(targets.targets["H6"], targets, [_pair(shares=(0.7, 0.3), first=0)] * 8, [])["verdict"] == J.OPPOSITE
    assert J.judge(targets.targets["H6"], targets, [_pair(first="together")], [])["verdict"] == J.NOT_COMPARABLE


def test_roles_decided_by_assertiveness_are_opposite_to_h7(targets):
    decided = [_pair(first=0, assertiveness=("holds_ground", "gives_way")) for _ in range(10)]
    found = J.judge(targets.targets["H7"], targets, decided, [])
    assert found["verdict"] == J.OPPOSITE and found["predicted_by"] == ["assertiveness"]
    mixed = decided[:5] + [_pair(first=1, assertiveness=("holds_ground", "gives_way")) for _ in range(5)]
    assert J.judge(targets.targets["H7"], targets, mixed, [])["verdict"] == J.AGREES


CANE = ("mobility_aid", "cane")


def test_age_that_only_travels_with_the_cane_is_not_separable(targets):
    """Issue #124: the cane user is the older and always goes first. H7's check flags age; with the cane
    held fixed, age cannot be told apart from it, and nothing else is left to test."""
    pairs = [_pair(first=0, ages=(75, 30), aids=("cane", None)) for _ in range(8)]
    assert J.judge(targets.targets["H7"], targets, pairs, [])["predicted_by"] == ["older"]
    found = J.not_predicted_by_traits_given(pairs, targets.age_groups, CANE)
    assert found["verdict"] == J.NOT_COMPARABLE and found["not_separable"] == ["older"]
    assert found["traits"]["older"]["not_separable"]["with"] == {"holder_passed_first": 8, "other_passed_first": 0}


def test_a_trait_that_matters_beyond_the_cane_is_still_found(targets):
    """The cane user goes first when holding ground and gives way otherwise: assertiveness decides."""
    pairs = [_pair(first=0, assertiveness=("holds_ground", "gives_way"), aids=("cane", None)) for _ in range(8)]
    pairs += [_pair(first=1, assertiveness=("gives_way", "holds_ground"), aids=("cane", None)) for _ in range(8)]
    found = J.not_predicted_by_traits_given(pairs, targets.age_groups, CANE)
    assert found["verdict"] == J.OPPOSITE and found["predicted_by"] == ["assertiveness"]
    assert found["traits"]["assertiveness"]["separated"]["p"] < 0.001
    # the cane alone deciding, whatever the assertiveness, is not the trait's doing
    alone = [_pair(first=0, assertiveness=(a, b), aids=("cane", None)) for a, b in [("holds_ground", "gives_way"), ("gives_way", "holds_ground")] * 8]
    assert J.not_predicted_by_traits_given(alone, targets.age_groups, CANE)["verdict"] == J.AGREES


def test_pairs_the_cane_does_not_separate_keep_h7s_sign_test(targets):
    pairs = [_pair(first=0, assertiveness=("holds_ground", "gives_way")) for _ in range(10)]
    found = J.not_predicted_by_traits_given(pairs, targets.age_groups, CANE)
    assert found["verdict"] == J.OPPOSITE and found["traits"]["assertiveness"]["unseparated"]["level_passed_first"] == 10
    assert found["traits"]["assertiveness"]["unseparated"]["p"] == round(J.judge(targets.targets["H7"], targets, pairs, [])["traits"]["assertiveness"]["p"], 6)


def test_a_trait_tested_elsewhere_is_still_listed_when_its_cane_pairs_are_one_sided(targets):
    """PR #125's review: a sign test on pairs without a cane must not hide one-sided cane pairs."""
    pairs = [_pair(first=0, ages=(75, 30)) for _ in range(3)] + [_pair(first=0, ages=(75, 30), aids=("cane", None))]
    found = J.not_predicted_by_traits_given(pairs, targets.age_groups, CANE)
    assert "unseparated" in found["traits"]["older"] and found["not_separable"] == ["older"]


def test_an_age_beyond_every_group_is_not_younger_by_group(targets):
    found = J.holder_younger([_pair(first=0, ages=(99, 70), aids=("cane", None))], targets.age_groups, CANE)
    assert found["by_group"]["pairs"] == 0 and found["by_years"]["pairs"] == 0


def test_who_goes_first_when_the_cane_user_is_the_younger(targets):
    pairs = [_pair(first=0, ages=(50, 70), aids=("cane", None)), _pair(first="together", ages=(70, 80), aids=(None, "cane")),
             _pair(first=1, ages=(70, 72), aids=("cane", None)), _pair(first=0, ages=(80, 30), aids=("cane", None)),
             _pair(first=0, ages=(30, 70))]  # no cane: not counted
    found = J.holder_younger(pairs, targets.age_groups, CANE)
    assert found["by_years"] == {"pairs": 2, "holder": 1, "other": 1, "together": 0, "none": 0}
    assert found["by_group"] == {"pairs": 1, "holder": 1, "other": 0, "together": 0, "none": 0}  # 50 against 70 only


def test_fisher_moved_unchanged():
    from negsim.resolution import groups as G
    from negsim.ruleset_eval import verdicts as V
    assert G.fisher is V.fisher and V.fisher(3, 1, 1, 3) == pytest.approx(0.485714, abs=1e-6)


def test_the_young_adapting_more_agrees_with_h8(targets):
    pairs = [_pair(shares=(0.2, 0.8), ages=(70, 25)) for _ in range(6)]
    assert J.judge(targets.targets["H8"], targets, pairs, [])["verdict"] == J.AGREES


def test_lanes_and_speed_against_density(targets):
    separated = {"lanes": {"agents": 100, "share_left": 0.2, "share_right": 0.8}, "speed_by_density": [(0.5, 1.3), (1.0, 1.1), (2.0, 0.8)]}
    mixed = {"lanes": {"agents": 100, "share_left": 0.48, "share_right": 0.52}, "speed_by_density": [(0.5, 1.0), (1.0, 1.1), (2.0, 1.2)]}
    assert J.judge(targets.targets["C1"], targets, [], [separated] * 6)["verdict"] == J.AGREES
    assert J.judge(targets.targets["C1"], targets, [], [mixed] * 6)["verdict"] == J.OPPOSITE
    assert J.judge(targets.targets["C3"], targets, [], [separated] * 6)["verdict"] == J.AGREES
    assert J.judge(targets.targets["C3"], targets, [], [mixed] * 6)["verdict"] == J.OPPOSITE
    assert J.judge(targets.targets["C3"], targets, [_pair()], [])["verdict"] == J.NOT_COMPARABLE


def test_sides_count_pairs_that_kept_the_same_own_side():
    found = J.sides([_pair(sides=("left", "left")), _pair(sides=("right", "right")), _pair(sides=("left", "right"))])
    assert (found["left"], found["right"], found["mixed"]) == (1, 1, 1)
