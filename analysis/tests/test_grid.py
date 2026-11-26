"""Tests of RF-52's grid analysis (issue #141) on hand-made grid decision points and tracks: the
adapter to RF-45's coder, the grid's side checks, the side kept when passing, and the paired test."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from analysis import grid as G
from analysis.hallucination import check_point, load_codebook
from analysis.intent import load_codebook as load_intent_codebook


def view(lane=2, direction=1, other_lane=1, ahead=10, changes=(), moved=0, history=()):
    """A grid view as ``negsim.grid.prompt.GridView.as_dict`` writes it (5 lanes of 0.4 m)."""
    return {
        "lanes": 5, "lane": lane, "direction": direction, "cell_m": 0.4,
        "seen": [{"label": 1, "cells_ahead": ahead, "lanes_left": (other_lane - lane) * direction, "lane": other_lane,
                  "motion": "towards", "speed_mps": 1.3, "age": 30, "gender": "male", "changes": list(changes),
                  "lanes_moved_left": moved * direction, "lanes_moved_plus_y": moved, "factor_lines": [], "pairwise_lines": []}],
        "history": list(history),
    }


def record(frame="own"):
    key = "resolve_grid_abs_v1" if frame == "absolute" else "resolve_grid_v1"
    return {"session_id": "S_x", "templates": {"core": {"key": key}}, "grid_outcome": {"resolved": True}, "session": {"pair_id": None}}


def grid_point(intent, reason="", option="carry on", side="none", frame="own", **kw):
    return {"agent_id": 0, "number": 1, "index": 0, "parse_error": None, "side": side, "view": view(**kw),
            "parsed": {"intent": intent, "reason": reason, "action": option}}


def adapted(intent, reason="", option="carry on", side="none", frame="own", **kw):
    p = G.as_rf45_point(record(frame), grid_point(intent, reason, option, side, frame, **kw), "run")
    p["flags"] = check_point(p, load_codebook(), load_intent_codebook())
    p["side_flags"] = G.side_flags(p)
    return p


def rules(p):
    return sorted(f["rule"] for f in p["side_flags"])


def test_the_adapter_puts_the_walls_and_the_other_where_the_grid_prompt_does():
    # Heading +x in lane 2 of 5: two lanes to the left wall, two to the right; the other one lane to the right (lane 1).
    p = G.as_rf45_point(record(), grid_point("x", other_lane=1), "run")
    assert p["view"]["place"][0] == "The wall on your left is 1.00 m from you, the wall on your right 1.00 m"
    assert p["view"]["seen"][0]["bearing_rad"] == pytest.approx(-0.5)  # to the right: negative, as in the continuous view
    assert math.degrees(abs(p["view"]["seen"][0]["bearing_rad"])) > load_codebook()["thresholds"]["straight_ahead_deg"]
    q = G.as_rf45_point(record(), grid_point("x", direction=-1, lane=1, other_lane=1, moved=1), "run")
    assert q["view"]["seen"][0]["bearing_rad"] == 0.0
    assert "moved_right" in q["view"]["seen"][0]["changes"]  # heading -x, +y is its own right
    assert q["view"]["place"][0] == "The wall on your left is 0.60 m from you, the wall on your right 1.40 m"


def test_rf45s_moved_side_rule_reads_the_grids_lane_moves():
    true = adapted("Move left.", "Person 1 is drifting to my right, so I go left.", other_lane=1)  # they are one lane to my right
    assert "1:moved_side" not in G._flag_keys(true)
    false = adapted("Move left.", "Person 1 is drifting to my left.", other_lane=1)
    assert "1:moved_side" in G._flag_keys(false)


def test_the_other_put_on_the_wrong_side_or_the_wrong_number_of_lanes_is_a_side_error():
    assert rules(adapted("Keep going.", "Person 1 is one lane to my right.", other_lane=1)) == []
    assert rules(adapted("Keep going.", "Person 1 is one lane to my left.", other_lane=1)) == ["other_side"]
    assert rules(adapted("Keep going.", "They are two lanes to my right.", other_lane=1)) == ["other_side"]
    assert rules(adapted("Keep going.", "Person 1 is in my lane.", other_lane=1)) == ["other_same_lane"]
    assert rules(adapted("Keep going.", "Person 1 is in my lane.", other_lane=2)) == []


def test_an_intent_naming_one_side_or_wall_and_an_option_to_the_other_is_a_side_error():
    assert rules(adapted("Step to my right.", option="step a little to your right", side="right")) == []
    assert rules(adapted("Step to my right.", option="step a little to your left", side="left")) == ["intent_side"]
    blue = adapted("Move towards the blue wall.", option="step a little towards the blue wall", side="left", frame="absolute")
    assert rules(blue) == []
    yellow = adapted("Move towards the blue wall.", option="step a little towards the yellow wall", side="right", frame="absolute")
    assert rules(yellow) == ["intent_wall"]


def test_lane_numbers_are_checked_from_one_at_the_blue_wall():
    # As the prompt numbers them (RF-52's pilot): 5 lanes, internal lane 2 is lane 3, internal lane 1 is lane 4.
    assert G.lane_number({"lanes": 5}, 4) == 1 and G.lane_number({"lanes": 5}, 0) == 5
    good = adapted("Keep to lane 3.", "I am in lane 3 and Person 1 is in lane 4.", frame="absolute", lane=2, other_lane=1)
    assert rules(good) == []
    approaching = adapted("Keep to lane 3.", "He is coming toward me in lane 4.", frame="absolute", lane=2, other_lane=1)
    assert rules(approaching) == []
    bad = adapted("Keep to lane 3.", "I am in lane 2 and Person 1 is in lane 2.", frame="absolute", lane=2, other_lane=1)
    assert rules(bad) == ["other_lane_number", "own_lane_number"]
    head_on = adapted("Keep my line.", "We are head-on in lane 3.", frame="absolute", lane=2, other_lane=2)
    assert rules(head_on) == []
    leaked = adapted("Move to my left.", frame="absolute")
    assert rules(leaked) == ["uses_own_sides"]


def test_a_move_put_on_the_others_wrong_side_is_a_side_error():
    # The reader heads +x; the other moved one lane to the reader's left (+y): to the other's own right.
    right = adapted("Keep clear.", "She moved a lane to her right.", moved=1)
    assert rules(right) == []
    assert rules(adapted("Keep clear.", "They moved one lane to my left.", moved=1)) == []
    wrong = adapted("Keep clear.", "She moved a lane to her left, into my line.", moved=1)
    assert rules(wrong) == ["other_move_side"]
    assert rules(adapted("Keep clear.", "He has drifted two lanes to my left.", moved=1)) == ["other_move_side"]
    # Towards the blue wall is +y.
    blue = adapted("Keep clear.", "She appears to have moved towards the blue wall too.", frame="absolute", moved=1)
    assert rules(blue) == []
    yellow = adapted("Keep clear.", "She appears to have moved towards the yellow wall too.", frame="absolute", moved=1)
    assert rules(yellow) == ["other_move_wall"]


def test_the_side_kept_when_passing_and_the_first_lane_change():
    # Walker 0 heads +x, walker 1 heads -x. At tick 4 walker 1 is one lane to +y of walker 0: on 0's left.
    track = {3: {0: (20, 2), 1: (22, 3)}, 4: {0: (21, 2), 1: (21, 3)}, 5: {0: (22, 2), 1: (20, 3)}}
    assert G.kept_side(track, 5, 0, 1) == "right"   # the other went by on walker 0's left
    assert G.kept_side(track, 5, 1, -1) == "right"  # walker 0 is at -y: walker 1's own left
    assert G.kept_side(track, None, 0, 1) is None
    moves = {0: {0: (5, 2)}, 1: {0: (6, 2)}, 2: {0: (7, 3)}, 3: {0: (8, 2)}}
    assert G._first_change(moves, 0, 1) == "left"
    assert G._first_change(moves, 0, -1) == "right"


def test_the_paired_frames_and_mcnemars_exact_test():
    sessions = pd.DataFrame([
        {"session_id": f"s{i}", "frame": frame, "resolved": value}
        for i, (own, abs_) in enumerate([(True, True)] * 3 + [(True, False)] * 6 + [(False, False)] * 2)
        for frame, value in (("own", own), ("absolute", abs_))
    ])
    paired = G.paired_frames(sessions)
    assert (paired["both"], paired["own_only"], paired["absolute_only"], paired["neither"]) == (3, 6, 0, 2)
    assert paired["mcnemar_exact_p"] == pytest.approx(2 / 2 ** 6)
    assert G.exact_binomial_two_sided(0, 0) == 1.0


def test_conventions_count_one_each_as_towards_the_same_wall():
    agents = pd.DataFrame([
        {"frame": "own", "session_id": "a", "agent": 0, "first_side": "right"}, {"frame": "own", "session_id": "a", "agent": 1, "first_side": "right"},
        {"frame": "own", "session_id": "b", "agent": 0, "first_side": "left"}, {"frame": "own", "session_id": "b", "agent": 1, "first_side": "right"},
        {"frame": "own", "session_id": "c", "agent": 0, "first_side": None}, {"frame": "own", "session_id": "c", "agent": 1, "first_side": "left"},
    ])
    (row,) = G.conventions(agents)
    assert (row["both_right"], row["same_wall"], row["one_only"]) == (1, 1, 1)
