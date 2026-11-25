"""Tests of the hallucination coder (issue #134, RF-45) on hand-made decision points: one true and
one false case per category, the hedges it skips, and the heard-side frames."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from analysis import hallucination as h

PLACE = ["- You are in a passage 1.75 m wide. The wall on your left is 0.77 m from you, the wall on your right 0.98 m."]


def point(intent="", reason="", message="", *, seen=None, heard=None, history=None, place=PLACE, coded=None,
          parse_error=None, width=0.5):
    return {
        "run": "r", "session_id": "s", "condition": "talk", "outcome": "completed", "resolved": True, "pair_id": None,
        "agent_id": 0, "number": 2, "index": 1, "readable": parse_error is None, "parse_error": parse_error,
        "texts": {"intent": intent, "reason": reason, "message": message}, "signal": "none",
        "coded": coded if coded is not None else {"side": "left", "slowed": False, "stopped": False, "backed_up": False},
        "view": {"seen": seen if seen is not None else [other()], "heard": heard or [], "history": history or [],
                 "place": place, "me": {"width_m": width}},
    }


def other(signal="none", motion="walking", changes=(), age=25, bearing_deg=0.0, traits=(), width=0.5):
    import math
    return {"signal": signal, "motion": motion, "changes": list(changes), "age": age, "width_m": width,
            "bearing_rad": math.radians(bearing_deg), "distance_m": 7.0, "factor_lines": list(traits)}


def flags(p):
    codebook, intent_codebook = h.load_codebook(), h.load_intent_codebook()
    return {(f["category"], f["rule"]) for f in h.check_point(p, codebook, intent_codebook)}


# --- category 1: misperceived the other --------------------------------------------------------

def test_signal_claim_flagged_only_when_not_shown():
    assert ("1", "signal_wave") in flags(point(reason="He waved me on, so I keep going."))
    assert ("1", "signal_wave") not in flags(point(reason="He waved me on, so I keep going.", seen=[other(signal="wave_on")]))


def test_speech_claim_needs_a_heard_message():
    assert ("1", "speech") in flags(point(reason="She asked for room, so I step left."))
    assert ("1", "speech") not in flags(point(reason="She asked for room, so I step left.",
                                              heard=[{"message": "Can I pass?", "frame": "facing"}]))


def test_other_moving_to_a_side_checked_against_changes_and_position():
    claim = "He's drifting to my right, so I go left."
    assert ("1", "moved_side") in flags(point(reason=claim))  # nothing shown
    assert ("1", "moved_side") in flags(point(reason=claim, seen=[other(changes=["moved_left"])]))  # the other way
    assert ("1", "moved_side") not in flags(point(reason=claim, seen=[other(changes=["moved_right"])]))
    assert ("1", "moved_side") not in flags(point(reason=claim, seen=[other(bearing_deg=-8)]))  # already to my right
    # "his left", facing, is my right
    assert ("1", "moved_side") not in flags(point(reason="He moved to his left.", seen=[other(changes=["moved_right"])]))


def test_drifting_into_my_line_needs_a_lateral_change():
    assert ("1", "moved_into_line") in flags(point(reason="He's drifting into my line."))
    assert ("1", "moved_into_line") not in flags(point(reason="He's drifting into my line.", seen=[other(changes=["turned"])]))


def test_traits_and_age():
    assert ("1", "trait_cane") in flags(point(reason="Her cane makes her slow."))
    assert ("1", "trait_cane") not in flags(point(reason="Her cane makes her slow.", seen=[other(traits=["They are walking with a cane."])]))
    assert ("1", "trait_elderly") in flags(point(reason="The elderly man needs room."))
    assert ("1", "trait_elderly") not in flags(point(reason="The elderly man needs room.", seen=[other(age=70)]))


def test_hedged_and_negated_claims_are_skipped():
    assert ("1", "signal_wave") not in flags(point(reason="If he waves, I will go first."))
    assert ("1", "stopped") not in flags(point(reason="He hasn't stopped yet. He has not stopped."))
    assert ("1", "slowed") not in flags(point(reason="I'll wait to see whether she slows down."))


def test_misread_heard_side_follows_the_message_frame():
    yours = [{"message": "Plenty of room on your right.", "frame": "facing"}]
    assert ("1", "misread_heard_side") in flags(point(reason="He told me to go right, but since he's facing me that's my left.", heard=yours))
    assert ("1", "misread_heard_side") not in flags(point(reason="He said go right, that's my right.", heard=yours))
    own = [{"message": "I'll keep left.", "frame": "facing"}]
    assert ("1", "misread_heard_side") not in flags(point(reason="She keeps her left, that's my right.", heard=own))
    assert ("1", "misread_heard_side") in flags(point(reason="She keeps her left, that's my left.", heard=own))
    assert h.heard_expected_side([{"message": "Hi there!", "frame": "facing"}]) is None


# --- category 2: misremembered itself ----------------------------------------------------------

def test_own_earlier_move_checked_against_history():
    claim = "I've already stepped to my left, so I hold."
    assert ("2", "own_move") in flags(point(reason=claim))  # no history at all
    assert ("2", "own_move") in flags(point(reason=claim, history=[{"sideways_m": -0.4}]))
    assert ("2", "own_move") not in flags(point(reason=claim, history=[{"sideways_m": 0.4}]))


def test_own_position_checked_against_the_walls():
    assert ("2", "own_position") in flags(point(reason="I'm already on the right side.",
                                                place=["- You are in a passage 1.75 m wide. The wall on your left is 0.30 m from you, the wall on your right 1.45 m."]))
    assert ("2", "own_position") not in flags(point(reason="I'm already on the left side.",
                                                    place=["- You are in a passage 1.75 m wide. The wall on your left is 0.30 m from you, the wall on your right 1.45 m."]))


def test_own_signal_and_speech():
    assert ("2", "own_signal") in flags(point(reason="I already waved, so I go."))
    assert ("2", "own_signal") not in flags(point(reason="I already waved, so I go.", history=[{"signal": "wave_on", "sideways_m": 0}]))
    assert ("2", "own_speech") in flags(point(reason="I've already told him I'm going left."))
    assert ("2", "own_speech") not in flags(point(reason="I've already told him I'm going left.",
                                                  history=[{"message": "I'm going left", "sideways_m": 0}]))


# --- categories 3, 4, 5 -------------------------------------------------------------------------

def test_intent_against_plan():
    assert ("3", "intent_against_plan") in flags(point(intent="Step to my right", coded={"side": "left"}))
    assert ("3", "intent_against_plan") not in flags(point(intent="Step to my left", coded={"side": "left"}))


def test_speech_against_own_move():
    assert ("4", "keeping_to_my_side") in flags(point(message="I'll keep to my right.", coded={"side": "left"}))
    assert ("4", "keeping_to_my_side") not in flags(point(message="I'll keep to my left.", coded={"side": "left"}))


def test_unreadable_is_category_5_and_nothing_else():
    assert flags(point(parse_error="unknown_start: steps[2].start: got 'other_passes'")) == {("5", "unreadable")}
    assert ("5", "unreadable") not in flags(point(reason="I keep left."))


# --- category 7: misstated the setting ---------------------------------------------------------

def test_no_room_checked_against_the_widths():
    assert ("7", "no_room") in flags(point(reason="There is no room to pass, so I stop."))  # 1.75 m holds 0.5 + 0.5
    narrow = ["- You are in a passage 0.90 m wide. The wall on your left is 0.45 m from you, the wall on your right 0.45 m."]
    assert ("7", "no_room") not in flags(point(reason="There is no room to pass, so I stop.", place=narrow))
    # a side named: the gap on that side
    tight = ["- You are in a passage 1.75 m wide. The wall on your left is 0.30 m from you, the wall on your right 1.45 m."]
    assert ("7", "no_room") not in flags(point(reason="There is no room on my left.", place=tight))


def test_a_little_room_is_giving_room_not_a_claim_of_none():
    # hallucination_v1 took "a little room" as "no room"; v2 fixes it (WORK_LOG-134.md)
    assert ("7", "no_room") not in flags(point(intent="Make a little room for her"))
    assert ("7", "no_room") in flags(point(reason="There is little room to pass."))


def test_wall_beside_me():
    assert ("7", "wall_close") in flags(point(reason="I'm against the wall already."))
    hugging = ["- You are in a passage 1.75 m wide. The wall on your left is 0.30 m from you, the wall on your right 1.45 m."]
    assert ("7", "wall_close") not in flags(point(reason="I'm against the wall already.", place=hugging))


# --- the run level ------------------------------------------------------------------------------

def test_shares_headline_and_denominators():
    points = [point(reason="He waved me on."), point(reason="I keep left."), point(parse_error="not_json")]
    codebook, intent_codebook = h.load_codebook(), h.load_intent_codebook()
    for p in points:
        p["flags"] = h.check_point(p, codebook, intent_codebook)
        p["checkable"] = h.checkable(p, intent_codebook)
    s = h.shares(points)
    assert s["headline"]["k"] == 2 and s["headline"]["n"] == 3
    assert s["category_1"]["n"] == 2 and s["category_5"]["n"] == 3


def test_end_to_end_on_a_tiny_run(tmp_path: Path):
    run = tmp_path / "run"
    (run / "sessions").mkdir(parents=True)
    with (run / "outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["session_id", "outcome", "condition", "resolved_plan_only", "pair_id"])
        writer.writerow(["S1", "completed", "silent", "True", ""])
    record = {"session_id": "S1", "condition": "silent", "decision_points": [
        {"index": 0, "agent_id": 0, "number": 1, "parse_error": None,
         "parsed": {"intent": "Keep left", "reason": "He waved me on.", "message": ""},
         "coded": {"side": "left"}, "view": {"seen": [other()], "heard": [], "history": [], "place": PLACE, "me": {"width_m": 0.5}}}]}
    (run / "sessions" / "S1.json").write_text(json.dumps(record), encoding="utf-8")
    out = tmp_path / "out"
    assert h.main([str(run), "--out", str(out), "--sample", "1"]) == 0
    data = json.loads((out / "hallucination.json").read_text(encoding="utf-8"))
    assert data["summary"]["run"]["all"]["headline"]["k"] == 1
    judgements = {"run/S1/dp0": {"flags": {"1:signal_wave": True}, "missed": []}}
    (out / "hand_check_judgements.json").write_text(json.dumps(judgements), encoding="utf-8")
    assert h.main([str(run), "--out", str(out), "--sample", "1"]) == 0
    data = json.loads((out / "hallucination.json").read_text(encoding="utf-8"))
    assert data["hand_check"]["1"]["precision"]["k"] == 1
