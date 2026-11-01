"""RF-39's analysis (issue #127): the dance at the start, its ending, and the side across repeats."""

from __future__ import annotations

import math

import pytest

from analysis import sidestep_reprompt as sr


def test_start_kind_reads_each_side_in_its_own_frame():
    assert sr.start_kind("left", "right") == "towards_same_wall"
    assert sr.start_kind("right", "left") == "towards_same_wall"
    assert sr.start_kind("left", "left") == "same_own_side"
    assert sr.start_kind("right", "none") == "not_both_aside"
    assert sr.start_kind(None, "left") == "not_both_aside"   # an unreadable reply


def test_more_room_needs_five_centimetres():
    line = "- You are in a passage 1.75 m wide. The wall on your left is {} m from you, the wall on your right {} m."
    assert sr.more_room([line.format("0.88", "0.87")]) is None
    assert sr.more_room([line.format("0.98", "0.77")]) == "left"
    assert sr.more_room([line.format("0.77", "0.98")]) == "right"
    assert sr.more_room(["- It is quiet around you."]) is None


def test_fisher_exact_matches_the_textbook_value():
    # The tea-tasting table [[3, 1], [1, 3]]: two-sided p = 0.4857.
    assert sr.fisher_exact(3, 1, 1, 3) == pytest.approx(0.4857, abs=1e-4)
    # [[1, 9], [11, 3]]: two-sided p = 0.002759 (R's fisher.test).
    assert sr.fisher_exact(1, 9, 11, 3) == pytest.approx(0.002759, abs=1e-5)
    assert sr.fisher_exact(0, 0, 0, 0) == 1.0


def test_coin_test_matches_a_fair_coin_and_flags_a_preference():
    # Exactly the binomial(4, 0.5) shares of 160 units: no excess of units all one way.
    fair = {0: 10, 1: 40, 2: 60, 3: 40, 4: 10}
    result = sr.coin_test(fair)
    assert result["share_right"] == 0.5
    assert result["all_one_way_expected_share"] == pytest.approx(0.125)
    assert result["chi2"] == pytest.approx(0.0, abs=1e-9)
    assert result["p"] == pytest.approx(1.0)
    # Every unit all one way, half left and half right: the same share of right, a strong excess.
    fixed = sr.coin_test({0: 50, 4: 50})
    assert fixed["share_right"] == 0.5 and fixed["all_one_way_share"] == 1.0
    assert fixed["p"] < 1e-6


def session(unit, repeat, condition, sides_0, sides_1, resolved, messages=("",), level=(0.4, 0.4)):
    def agent(sides):
        return {"first_side": sides[0], "sides": list(sides), "decisions": len(sides), "more_room": None,
                "messages": list(messages), "signals": ["none"] * len(sides), "side_basis": "either_side"}
    return {"session_id": f"{unit}_r{repeat}", "unit": unit, "repeat": repeat, "condition": condition,
            "geometry": "layout=aligned", "outcome": "resolved" if resolved else "collision", "resolved": resolved,
            "agents": {0: agent(sides_0), 1: agent(sides_1)},
            "level": {"own_0_m": level[0], "own_1_m": level[1]}}


def test_a_dance_at_the_start_and_how_it_ended():
    sessions = [
        # independent: one dance, unresolved; one making room, resolved
        session("I_a", 1, "independent", ["left"], ["right"], False, level=(0.4, -0.4)),
        session("I_b", 1, "independent", ["left"], ["left"], True),
        # non-verbal: a dance ended by one agent changing side and saying so; a dance that stayed
        session("N_a", 1, "non_verbal", ["left", "right"], ["right", "right"], True, messages=("", "I'll go right")),
        session("N_b", 1, "non_verbal", ["left", "left"], ["right", "right"], False, level=(0.4, -0.4)),
    ]
    out = sr.summarise(sessions)
    assert out["start"]["independent"]["towards_same_wall"]["k"] == 0
    assert out["start"]["independent"]["towards_same_wall"]["n"] == 1
    assert out["start"]["non_verbal"]["towards_same_wall"]["k"] == 1
    ending = out["dance_ending"]["non_verbal"]
    assert ending["resolved"]["switched"] == {"none": 0, "one": 1, "both": 0}
    assert ending["resolved"]["a_message_names_a_side"] == 1
    assert ending["not_resolved"]["switched"]["none"] == 1
    assert ending["not_resolved"]["when_level"] == {"towards_same_wall": 1}
    assert "non_verbal" in out["dance_vs_independent"]


def test_without_independent_silent_is_the_reference_and_its_dances_are_read_as_asked_again():
    # Issue #129 (RF-40): silent replaces independent; it is asked again, so its dances end too.
    sessions = [
        session("S_a", 1, "silent", ["left", "right"], ["right", "right"], True),
        session("S_b", 1, "silent", ["left"], ["right"], False, level=(0.4, -0.4)),
        session("T_a", 1, "talk", ["left", "right"], ["right", "right"], True),
    ]
    out = sr.summarise(sessions)
    assert out["reference"] == "silent" and set(out["dance_vs_independent"]) == {"talk"}
    assert out["dance_ending"]["silent"]["resolved"]["switched"] == {"none": 0, "one": 1, "both": 0}
    assert "against silent" in sr.markdown(out)


def test_side_units_need_four_runs_that_moved_aside():
    sessions = [session("N_a", r, "non_verbal", ["right"], [side], True) for r, side in
                zip((1, 2, 3, 4), ("left", "left", "right", "none"))]
    out = sr.summarise(sessions)
    assert out["side"]["all"]["right_of_4"] == {0: 0, 1: 0, 2: 0, 3: 0, 4: 1}   # agent 0: right 4 of 4
    assert out["side"]["left_out"] == {"not_aside_or_unreadable_in_some_run": 1}   # agent 1: one run not aside
    assert out["stated"]["unit_all_one_way"] == {"either_side": 4}
    assert math.isclose(out["side"]["all"]["share_right"], 1.0)
