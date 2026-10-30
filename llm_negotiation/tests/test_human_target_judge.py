"""Issue #122 (RF-37): judging a subject against the human targets, on hand-made records."""

from __future__ import annotations

import pytest

from negsim.human_targets import judge as J
from negsim.human_targets.targets import TARGETS_DIR, TargetFile


@pytest.fixture(scope="module")
def targets():
    return TargetFile.load(TARGETS_DIR / "head_on_v1.yaml")


def _pair(distance=0.9, shares=(0.5, 0.5), first="together", ages=(25, 25), seed=1, speed=1.3, starts=(2.0, 2.0),
          changes=(0.0, 0.0), sides=("right", "right"), assertiveness=("gives_way", "gives_way")):
    per_agent = {str(i): {"lateral_share": shares[i], "turning_start_m": starts[i], "speed_change_mps": changes[i], "side": sides[i]}
                 for i in (0, 1)}
    return {"seed": seed, "speed_mps": speed, "agents": [0, 1], "passed_first": first,
            "people": [{"age": ages[i], "gender": "male", "assertiveness": assertiveness[i]} for i in (0, 1)],
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
