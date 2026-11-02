"""RF-40's analysis (issue #129): frames, fits, words against moves, and the listener's next move."""

from __future__ import annotations

import pytest

from analysis import turn_taking as tt


def test_frame_of_tells_the_speakers_side_from_the_listeners():
    assert tt.frame_of("I'll keep to my left, plenty of room.") == "own"
    assert tt.frame_of("Coming through on your right!") == "yours"
    assert tt.frame_of("I'm keeping left, go on your left.") == "both"
    assert tt.frame_of("Right, coming through!") == "other"


def test_fit_reads_each_side_in_its_own_frame():
    assert tt.fit("left", "left") == "fits"            # head-on: both to their own left make room
    assert tt.fit("left", "right") == "towards_same_wall"
    assert tt.fit("left", "none") == "not_both_aside"
    assert tt.fit(None, "left") == "not_both_aside"


def test_words_match_move_flips_the_listeners_side():
    assert tt.words_match_move("I'll keep to my left.", "left") == ("keeping_to_my_side", True)
    assert tt.words_match_move("I'm keeping right.", "left") == ("keeping_to_my_side", False)
    # On the listener's right, facing each other, is the speaker's own left.
    assert tt.words_match_move("Coming through on your right!", "left") == ("coming_through_on_your_side", True)
    assert tt.words_match_move("Coming through on your right!", "right") == ("coming_through_on_your_side", False)
    assert tt.words_match_move("Hello!", "left") is None
    assert tt.words_match_move("I'll keep left.", "none") is None


def test_binomial_two_sided_matches_known_values():
    assert tt.binomial_two_sided(5, 10) == pytest.approx(1.0)
    assert tt.binomial_two_sided(0, 10) == pytest.approx(2 / 1024)
    assert tt.binomial_two_sided(2, 10) == pytest.approx(0.109375)  # R: binom.test(2, 10)
    assert tt.binomial_two_sided(0, 0) == 1.0


def point(agent, number, step, side, message="", heard=(), reason=""):
    return {"agent_id": agent, "number": number, "step": step, "readable": True, "side": side,
            "message": message, "reason": reason, "heard": list(heard)}


def test_heard_sides_takes_the_other_agents_next_decision_that_heard_it():
    said = "I'll keep to my left."
    session = {"session_id": "T_x_r1", "points": [
        point(0, 1, 10, "left", said),
        point(0, 2, 20, "left"),                                    # the speaker again: not the listener
        point(1, 1, 10, "right"),                                   # did not hear it (not in its heard list)
        point(1, 2, 20, "left", heard=[said], reason="She keeps left (my right), so I keep left too."),
    ]}
    [entry] = tt.heard_sides(session)
    assert entry["frame"] == "own" and entry["fit"] == "fits" and not entry["same_pause"] and entry["translates"]


def test_summarise_counts_who_was_asked_first():
    sessions = [
        {"session_id": f"S_{i}", "condition": "silent", "first_asked": "p1" if i % 2 else "p2", "resolved": i < 3, "points": []}
        for i in range(6)
    ]
    summary = tt.summarise(sessions)
    # p1: sessions 1, 3, 5 (resolved: 1); p2: sessions 0, 2, 4 (resolved: 0, 2).
    assert summary["asked_first"]["silent"]["p1"] == [1, 3] and summary["asked_first"]["silent"]["p2"] == [2, 3]
    assert summary["talk_sessions"] == 0
