"""Avoidance directives: validation, the two providers, and how a pair's directives are
combined, including the reciprocity violations and what is done about each."""

from __future__ import annotations

import pytest

from helpers import crowd
from negsim.avoidance.directives import (
    DIRECTIVE_FIELDS,
    DIRECTIVE_FIELDS_V4,
    FIELD_BACK_UP,
    FIELD_ORDER,
    FIELD_SHARE,
    FIELD_SIDE,
    PLAIN_ORCA,
    POLICY_EQUAL_SPLIT,
    POLICY_PROPORTIONAL,
    AvoidanceDirective,
    DirectiveProvider,
    NullProvider,
    StaticProvider,
    make_provider,
    resolve_pair,
    resolve_shares,
)
from negsim.avoidance.perception import default_visibility, perceive
from negsim.configutil import ConfigError

D = AvoidanceDirective


def record(observer: int, neighbour: int):
    world = crowd("wide_corridor_head_on").build_world()
    return perceive(0, 0.0, world.agents[observer], world.agents[neighbour], world.obstacles, default_visibility(), {}, 1.3)


# --- the directive ---------------------------------------------------------------------------


def test_the_fields_and_their_defaults_are_plain_orca():
    """The exact field names: the rule format depends on them. Issue #32 added ``back_up``; the
    fields before it are what a run folder of log schema 4 or earlier holds."""
    assert DIRECTIVE_FIELDS == (
        "side_preference", "responsibility_share", "speed_scale", "clearance_margin", "passage_order", "back_up",
    )
    assert DIRECTIVE_FIELDS_V4 == DIRECTIVE_FIELDS[:-1]
    assert PLAIN_ORCA.as_dict() == {
        "side_preference": "none", "responsibility_share": 0.5, "speed_scale": 1.0,
        "clearance_margin": 0.0, "passage_order": "none", "back_up": False,
    }


@pytest.mark.parametrize(
    "bad",
    [
        {"side_preference": "up"}, {"passage_order": "first"}, {"responsibility_share": 1.01},
        {"responsibility_share": -0.1}, {"speed_scale": -1.0}, {"clearance_margin": -0.05},
        {"back_up": "true"}, {"back_up": 1}, {"back_up": None},
    ],
)
def test_a_directive_with_a_value_out_of_range_is_rejected(bad):
    with pytest.raises(ValueError):
        D(**bad)
    with pytest.raises(ConfigError):
        D.from_mapping(bad)


def test_a_directive_from_a_config_fills_in_what_is_left_out():
    assert D.from_mapping({}) == PLAIN_ORCA
    directive = D.from_mapping({"side_preference": "left", "speed_scale": 0.5})
    assert directive == D(side_preference="left", speed_scale=0.5)
    based = D.from_mapping({"clearance_margin": 0.2}, base=directive)
    assert based == D(side_preference="left", speed_scale=0.5, clearance_margin=0.2)
    with pytest.raises(ConfigError, match="unknown key"):
        D.from_mapping({"side": "left"})
    with pytest.raises(ConfigError, match="expected a number"):
        D.from_mapping({"responsibility_share": "half"})


# --- shares ----------------------------------------------------------------------------------


@pytest.mark.parametrize("given", [(0.5, 0.5), (1.0, 0.0), (0.0, 1.0), (0.7, 0.6), (1.0, 1.0)])
def test_shares_that_sum_to_at_least_one_are_left_alone(given):
    for policy in (POLICY_PROPORTIONAL, POLICY_EQUAL_SPLIT):
        assert resolve_shares(*given, policy=policy) == given


def test_proportional_policy_keeps_the_ratio():
    assert resolve_shares(0.3, 0.3) == pytest.approx((0.5, 0.5))
    assert resolve_shares(0.2, 0.3) == pytest.approx((0.4, 0.6))
    assert resolve_shares(0.0, 0.4) == pytest.approx((0.0, 1.0))
    assert resolve_shares(0.0, 0.0) == (0.5, 0.5)  # no ratio to keep: back to standard ORCA
    a, b = resolve_shares(0.1, 0.25)
    assert a + b == pytest.approx(1.0) and a / b == pytest.approx(0.1 / 0.25)


def test_equal_split_policy_shares_out_what_is_missing():
    assert resolve_shares(0.2, 0.3, policy=POLICY_EQUAL_SPLIT) == pytest.approx((0.45, 0.55))
    assert resolve_shares(0.0, 0.0, policy=POLICY_EQUAL_SPLIT) == pytest.approx((0.5, 0.5))
    assert resolve_shares(0.0, 0.4, policy=POLICY_EQUAL_SPLIT) == pytest.approx((0.3, 0.7))


def test_an_unknown_share_policy_is_rejected():
    with pytest.raises(ValueError, match="unknown share policy"):
        resolve_shares(0.2, 0.2, policy="largest_wins")


# --- combining the two directives of a pair --------------------------------------------------


def test_two_plain_directives_resolve_to_plain_orca_without_violations():
    resolution = resolve_pair(3, PLAIN_ORCA, 7, PLAIN_ORCA)
    assert resolution.agents == (3, 7) and resolution.shares == (0.5, 0.5)
    assert resolution.side is None and resolution.clearance_margin == 0.0 and resolution.leader is None
    assert resolution.violations == ()
    assert resolution.share_of(3) == 0.5 and resolution.share_of(7) == 0.5


def test_shares_short_of_one_are_a_violation_and_are_repaired():
    resolution = resolve_pair(0, D(responsibility_share=0.2), 1, D(responsibility_share=0.3))
    assert resolution.shares == pytest.approx((0.4, 0.6))
    assert resolution.share_of(0) == pytest.approx(0.4) and resolution.share_of(1) == pytest.approx(0.6)
    (violation,) = resolution.violations
    assert violation.field == FIELD_SHARE and violation.agents == (0, 1)
    assert violation.given == (0.2, 0.3) and violation.resolved == pytest.approx((0.4, 0.6))
    assert violation.policy == POLICY_PROPORTIONAL
    assert violation.as_dict()["given"] == [0.2, 0.3]
    other = resolve_pair(0, D(responsibility_share=0.2), 1, D(responsibility_share=0.3), POLICY_EQUAL_SPLIT)
    assert other.shares == pytest.approx((0.45, 0.55)) and other.violations[0].policy == POLICY_EQUAL_SPLIT


def test_shares_above_one_are_not_a_violation():
    resolution = resolve_pair(0, D(responsibility_share=0.9), 1, D(responsibility_share=0.8))
    assert resolution.shares == (0.9, 0.8) and resolution.violations == ()


@pytest.mark.parametrize(
    "side_a, side_b, expected, violated",
    [
        ("none", "none", None, False),
        ("left", "left", "left", False),
        ("right", "right", "right", False),
        ("left", "none", "left", False),  # one states a side: both use it
        ("none", "right", "right", False),
        ("left", "right", None, True),  # they contradict each other: neither is used
        ("right", "left", None, True),
    ],
)
def test_side_preferences_of_a_pair(side_a, side_b, expected, violated):
    resolution = resolve_pair(0, D(side_preference=side_a), 1, D(side_preference=side_b))
    assert resolution.side == expected
    assert [v.field for v in resolution.violations] == ([FIELD_SIDE] if violated else [])
    if violated:
        assert resolution.violations[0].given == (side_a, side_b)
        assert resolution.violations[0].resolved == ("none", "none")


@pytest.mark.parametrize(
    "order_a, order_b, leader, violated",
    [
        ("none", "none", None, False),
        ("leader", "follower", 0, False),
        ("follower", "leader", 1, False),
        ("leader", "none", 0, False),
        ("none", "follower", 0, False),
        ("follower", "none", 1, False),
        ("none", "leader", 1, False),
        ("leader", "leader", None, True),  # both claim the way
        ("follower", "follower", None, True),  # both give it up
    ],
)
def test_passage_orders_of_a_pair(order_a, order_b, leader, violated):
    resolution = resolve_pair(0, D(passage_order=order_a), 1, D(passage_order=order_b))
    assert resolution.leader == leader
    assert [v.field for v in resolution.violations] == ([FIELD_ORDER] if violated else [])


def test_the_larger_clearance_margin_is_used_by_both():
    resolution = resolve_pair(0, D(clearance_margin=0.1), 1, D(clearance_margin=0.3))
    assert resolution.clearance_margin == 0.3 and resolution.violations == ()


def test_several_violations_in_one_pair_are_all_reported():
    a = D(side_preference="left", responsibility_share=0.1, passage_order="leader")
    b = D(side_preference="right", responsibility_share=0.1, passage_order="leader")
    resolution = resolve_pair(4, a, 9, b)
    assert sorted(v.field for v in resolution.violations) == sorted([FIELD_SHARE, FIELD_SIDE, FIELD_ORDER])
    assert resolution.shares == (0.5, 0.5) and resolution.side is None and resolution.leader is None
    assert resolution.as_dict() == {
        "agents": [4, 9], "shares": [0.5, 0.5], "side": "none", "clearance_margin": 0.0, "leader": None, "backer": None,
    }  # "backer" since issue #32


def test_the_one_that_backs_up_lets_the_other_go_first():
    """Issue #32: ``back_up`` names a backer, and the other is the pair's leader."""
    for backer, other in ((3, 7), (7, 3)):
        directives = {backer: D(back_up=True), other: D()}
        resolution = resolve_pair(3, directives[3], 7, directives[7])
        assert (resolution.backer, resolution.leader, resolution.violations) == (backer, other, ())
    assert resolve_pair(3, D(), 7, D()).backer is None


def test_two_that_back_up_are_a_violation_and_neither_does():
    resolution = resolve_pair(3, D(back_up=True), 7, D(back_up=True))
    assert (resolution.backer, resolution.leader) == (None, None)
    (violation,) = resolution.violations
    assert violation.as_dict() == {
        "field": FIELD_BACK_UP, "agents": [3, 7], "given": [True, True], "resolved": [False, False], "policy": "ignore_both",
    }


@pytest.mark.parametrize("backer_first", [True, False])
def test_a_passage_order_that_puts_the_one_backing_up_first_gives_way_to_the_backing(backer_first):
    """A directive that backs up and also leads contradicts itself: the backing stands, and the
    other leads."""
    backing, other = D(back_up=True, passage_order="leader"), D()
    resolution = resolve_pair(3, backing, 7, other) if backer_first else resolve_pair(3, other, 7, backing)
    backer, leader = (3, 7) if backer_first else (7, 3)
    assert (resolution.backer, resolution.leader) == (backer, leader)
    (violation,) = resolution.violations
    assert (violation.field, violation.policy) == (FIELD_ORDER, "the_one_backing_up_follows")
    assert violation.resolved == (("follower", "leader") if backer_first else ("leader", "follower"))


def test_resolution_does_not_depend_on_which_agent_is_named_first():
    a, b = D(side_preference="left", responsibility_share=0.2, clearance_margin=0.1, passage_order="follower"), D(responsibility_share=0.6)
    forward, backward = resolve_pair(0, a, 1, b), resolve_pair(1, b, 0, a)
    assert forward.share_of(0) == pytest.approx(backward.share_of(0))
    assert forward.share_of(1) == pytest.approx(backward.share_of(1))
    assert (forward.side, forward.clearance_margin, forward.leader) == (backward.side, backward.clearance_margin, backward.leader)


# --- providers -------------------------------------------------------------------------------


def test_both_providers_implement_the_interface():
    assert issubclass(NullProvider, DirectiveProvider) and issubclass(StaticProvider, DirectiveProvider)
    assert NullProvider.name == "null" and StaticProvider.name == "static"
    with pytest.raises(TypeError):
        DirectiveProvider()  # abstract


def test_null_provider_is_plain_orca_for_everyone():
    provider = NullProvider()
    assert provider.directive(record(0, 1)) == PLAIN_ORCA and provider.directive(record(1, 0)) == PLAIN_ORCA
    assert provider.describe() == {"provider": "null"}


def test_static_provider_the_most_specific_entry_wins():
    provider = StaticProvider(
        default=D(speed_scale=0.9),
        agents={0: D(speed_scale=0.9, side_preference="left")},
        pairs={(0, 1): D(speed_scale=0.9, side_preference="left", responsibility_share=1.0)},
    )
    assert provider.directive(record(0, 1)) == D(speed_scale=0.9, side_preference="left", responsibility_share=1.0)
    assert provider.directive(record(1, 0)) == D(speed_scale=0.9)  # agent 1 has no entry: the default
    del provider.pairs[(0, 1)]
    assert provider.directive(record(0, 1)) == D(speed_scale=0.9, side_preference="left")


def test_static_provider_from_a_config_layers_the_entries():
    provider = make_provider(
        {
            "provider": "static",
            "default": {"side_preference": "left"},
            "agents": {0: {"responsibility_share": 1.0}, "1": {"responsibility_share": 0.0}},
            "pairs": [{"observer": 0, "neighbour": 1, "clearance_margin": 0.2}],
        }
    )
    assert isinstance(provider, StaticProvider)
    assert provider.default == D(side_preference="left")
    assert provider.agents[0] == D(side_preference="left", responsibility_share=1.0)  # inherits the default
    assert provider.agents[1] == D(side_preference="left", responsibility_share=0.0)
    assert provider.pairs[(0, 1)] == D(side_preference="left", responsibility_share=1.0, clearance_margin=0.2)
    described = provider.describe()
    assert described["provider"] == "static" and described["default"]["side_preference"] == "left"
    assert described["agents"]["1"]["responsibility_share"] == 0.0
    assert described["pairs"] == [{"observer": 0, "neighbour": 1, **provider.pairs[(0, 1)].as_dict()}]


def test_make_provider_defaults_to_plain_orca():
    assert isinstance(make_provider(None), NullProvider)
    assert isinstance(make_provider({}), NullProvider)
    assert isinstance(make_provider({"provider": "null"}), NullProvider)


@pytest.mark.parametrize(
    "bad, message",
    [
        ({"provider": "rules"}, "expected one of"),
        ({"provider": "null", "default": {"side_preference": "left"}}, "takes no directives"),
        ({"provider": "static", "defaults": {}}, "unknown key"),
        ({"provider": "static", "agents": {-1: {}}}, "cannot be negative"),
        ({"provider": "static", "agents": {"zero": {}}}, "expected an agent index"),
        ({"provider": "static", "pairs": [{"observer": 0}]}, "missing required key"),
        ({"provider": "static", "pairs": [{"observer": 2, "neighbour": 2}]}, "same agent"),
        ({"provider": "static", "pairs": [{"observer": 0, "neighbour": 1}, {"observer": 0, "neighbour": 1}]}, "listed twice"),
        ({"provider": "static", "default": {"responsibility_share": 2.0}}, r"must be in \[0, 1\]"),
    ],
)
def test_a_bad_directives_config_is_refused_with_a_reason(bad, message):
    with pytest.raises(ConfigError, match=message):
        make_provider(bad)
