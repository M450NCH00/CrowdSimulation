"""Issue #129 (RF-40): talk and signals as a turn-taking exchange, and the silent condition.

The user's decisions of 2026-11-01: under ``protocol.exchange: turn_taking`` the simulation pauses
while those due are asked one at a time; what one signals or says is seen or heard at once, in
full, and whoever perceives it is asked next in the same pause; who is asked first is
counterbalanced over a cell's repeats; silent (no signal, no talk, asked again under D5) replaces
independent; and ``resolve_v9`` puts a note beside a heard message on which way the speaker faces,
never rewriting the message. The default exchange (``real_time``) and every earlier template and
config behave as before.
"""

from __future__ import annotations

import copy
import json
import math
from collections import Counter
from dataclasses import replace

import pytest

from negsim.configutil import ConfigError, load_yaml, resolve_path
from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution import protocol as P
from negsim.resolution.perceive import Body, LLMViewSettings, frame_of
from negsim.resolution.prompt import CoreTemplate
from negsim.resolution.view import ALL_CONDITIONS, CONDITIONS, FRAME_FACING, FRAME_SAME_WAY, Heard
from test_encounter_protocol import HEAD_ON, points_of, session_on

V8, V9 = CoreTemplate.load("resolve_v8"), CoreTemplate.load("resolve_v9")
CONFIG = "configs/resolution/round1_head_on_turn_taking.yaml"
RF39 = "configs/resolution/round1_head_on_sidestep_reprompt.yaml"
TURN = P.ProtocolSettings(execution=X.EXECUTION_KEEP_LINE_REPLAN, max_decision_points=6, exchange=P.EXCHANGE_TURN_TAKING)
REAL = P.ProtocolSettings(execution=X.EXECUTION_KEEP_LINE_REPLAN, max_decision_points=6)
FAR_HEARING = replace(LLMViewSettings.load(), hearing_range_m=20.0)  # heard at the trigger's distance


def answer(*steps, signal="none", message="", intent="Carry on."):
    return json.dumps({"message": message, "signal": signal, "intent": intent, "steps": list(steps), "reason": "r"})


WALK = {"speed_mps": 1.3, "until": "other_passes"}


def by_step(record):
    found = {}
    for point in record["decision_points"]:
        found.setdefault(point["step"], []).append(point)
    return found


# --- the settings and the templates ---------------------------------------------------------------


def test_the_default_exchange_is_real_time_and_is_left_out_of_the_record():
    assert P.ProtocolSettings().exchange == P.EXCHANGE_REAL_TIME and not P.ProtocolSettings().turn_taking
    assert "exchange" not in P.ProtocolSettings().as_dict()
    assert TURN.as_dict()["exchange"] == "turn_taking" and TURN.turn_taking
    with pytest.raises(ConfigError):
        P.ProtocolSettings(exchange="shouting")
    assert P.ProtocolSettings.from_mapping({"exchange": "turn_taking"}).turn_taking


def test_first_asked_is_only_for_a_paused_exchange():
    with pytest.raises(ConfigError, match="turn_taking"):
        session_on(HEAD_ON, "non_verbal", {}, settings=REAL, core=V8, first_asked=HEAD_ON["agents"][0])


def test_every_earlier_template_loads_and_none_offers_silent():
    assert CONDITIONS == ("independent", "non_verbal", "talk") and ALL_CONDITIONS == (*CONDITIONS, "silent")
    for n in range(1, 9):
        core = CoreTemplate.load(f"resolve_v{n}")
        assert not core.offers("silent") and core.exchange is None and not core.heard_frame
    with pytest.raises(ConfigError, match="silent"):
        V8.retry("silent")


def test_resolve_v9_is_v8_plus_the_silent_section_the_paused_wording_and_the_note():
    eight, nine = V8.data, V9.data
    assert nine["exchange"] == "turn_taking" and nine["heard_frame"] is True and V9.offers("silent")
    assert nine["step_format"] == eight["step_format"] and nine["decision_point"] == eight["decision_point"]
    assert nine["conditions"]["independent"] == eight["conditions"]["independent"]
    for name in ("non_verbal", "talk"):
        assert nine["conditions"][name]["reply_format"] == eight["conditions"][name]["reply_format"]
        assert "see your signal before they decide what to do" in nine["conditions"][name]["instructions"]
    assert "It takes as long to say as it would in life." in eight["conditions"]["talk"]["instructions"]
    assert "It takes as long to say" not in nine["conditions"]["talk"]["instructions"]
    assert "They hear all of it before they decide what to do." in nine["conditions"]["talk"]["instructions"]
    silent = nine["conditions"]["silent"]
    assert silent["reply_format"] == eight["conditions"]["independent"]["reply_format"]
    assert silent["retry"] == eight["conditions"]["independent"]["retry"]
    assert "You may be asked again later, if something changes." in silent["instructions"]
    assert "signal" not in silent["instructions"] and "say" not in silent["instructions"].replace("Say what you do", "")
    extra = {"heard_seen_facing", "heard_seen_same_way"}
    assert set(nine["view"]) - set(eight["view"]) == extra
    assert {k: v for k, v in nine["view"].items() if k not in extra} == eight["view"]


# --- the note on which way a speaker faces --------------------------------------------------------


def body(agent, heading_deg, x=0.0):
    rad = math.radians(heading_deg)
    return Body(agent, (x, 0.0), (1.3 * math.cos(rad), 1.3 * math.sin(rad)), facing_rad=rad, radius_m=0.25)


@pytest.mark.parametrize("heading, frame", [(180, FRAME_FACING), (140, FRAME_FACING), (90, None), (40, FRAME_SAME_WAY), (0, FRAME_SAME_WAY)])
def test_frame_of_reads_the_speakers_heading_against_the_listeners(heading, frame):
    assert frame_of(body(0, 0.0), body(1, heading, x=5.0)) == frame


def test_a_heard_frame_is_left_out_of_a_view_record_unless_set():
    with pytest.raises(ValueError):
        Heard("Hi.", 1, frame="sideways")
    run, record, _ = session_on(HEAD_ON, "talk", {0: answer(WALK, message="Hello!")}, settings=REAL, core=V8, view_settings=FAR_HEARING)
    heard = [h for p in record["decision_points"] for h in p["view"]["heard"]]
    assert heard and all("frame" not in h for h in heard)


# --- the paused exchange --------------------------------------------------------------------------


def test_the_first_asked_goes_first_and_the_other_sees_its_signal_in_the_same_pause():
    a, b = HEAD_ON["agents"]
    answers = {b: [answer(WALK, signal="wave_on")], a: [answer(WALK)]}
    _, record, _ = session_on(HEAD_ON, "non_verbal", answers, settings=TURN, core=V9, first_asked=b)
    assert record["encounter"]["first_asked"] == b and record["protocol"]["exchange"] == "turn_taking"
    opening = by_step(record)[record["decision_points"][0]["step"]]
    assert [(p["agent_id"], p["turn"]) for p in opening] == [(b, 0), (a, 1)]
    seen = opening[1]["view"]["seen"][0]
    assert seen["signal"] == "wave_on"
    assert "They wave you on." in opening[1]["prompt"]["messages"][-1]["content"]
    # Under the real-time exchange, the same replies: the wave is made during the next step, unseen at the first prompts.
    _, real, _ = session_on(HEAD_ON, "non_verbal", answers, settings=REAL, core=V8)
    first = by_step(real)[real["decision_points"][0]["step"]]
    assert all(p["view"]["seen"][0]["signal"] == "none" for p in first) and all("turn" not in p for p in real["decision_points"])
    assert "first_asked" not in real["encounter"]


def test_a_message_is_heard_in_full_in_the_same_pause_with_the_note_and_word_for_word():
    a, b = HEAD_ON["agents"]
    said = "I'll keep to my left."
    _, record, _ = session_on(
        HEAD_ON, "talk", {a: [answer(WALK, message=said)], b: [answer(WALK)]}, settings=TURN, core=V9, first_asked=a, view_settings=FAR_HEARING,
    )
    opening = by_step(record)[record["decision_points"][0]["step"]]
    assert [p["agent_id"] for p in opening] == [a, b]
    heard = list(opening[1]["view"]["heard"])
    assert heard == [{"message": said, "label": 1, "direction": None, "band": None, "frame": FRAME_FACING}]
    text = opening[1]["prompt"]["messages"][-1]["content"]
    assert f'Person 1 says: "{said}" (Person 1 is facing you: their left is your right, and their right is your left.)' in text
    assert record["utterances"][0]["message"] == said and record["utterances"][0]["time_s"] == opening[0]["time_s"]


def test_a_listener_is_asked_in_the_same_pause_whatever_the_time_since_its_last_prompt():
    # Agent a's first plan ends after 1 s (same speed: nothing for b to notice); asked again (plan
    # ended), a waves b on, and b, which had nothing new of its own, is asked at the same step.
    a, b = HEAD_ON["agents"]
    answers = {
        a: [answer({"speed_mps": 1.3, "until": {"seconds": 1.0}}), answer(WALK, signal="wave_on"), answer(WALK)],
        b: [answer(WALK), answer(WALK)],
    }
    _, record, _ = session_on(HEAD_ON, "non_verbal", answers, settings=TURN, core=V9, first_asked=a)
    later = [p for p in points_of(record, a) if p["number"] == 2]
    assert later and P.REASON_PLAN_ENDED in later[0]["trigger_reasons"]
    same = by_step(record)[later[0]["step"]]
    assert [(p["agent_id"], p["turn"]) for p in same] == [(a, 0), (b, 1)]
    assert same[1]["trigger_reasons"] == [f"{P.REASON_SIGNALLED}:{a}"]
    # Each member at most once per pause, and the pause takes no simulated time.
    for points in by_step(record).values():
        assert len({p["agent_id"] for p in points}) == len(points)
        assert len({p["time_s"] for p in points}) == 1


# --- the silent condition -------------------------------------------------------------------------


def test_silent_is_asked_again_but_cannot_signal_or_speak():
    a, b = HEAD_ON["agents"]
    dance = {  # both to the same wall: their plans fail and they are asked again
        a: [answer({"speed_mps": 1.3, "sidestep": {"to": "right", "metres": 0.4}}, WALK, signal="wave_on", message="Go!"), answer(WALK)],
        b: [answer({"speed_mps": 1.3, "sidestep": {"to": "left", "metres": 0.4}}, WALK), answer(WALK)],
    }
    _, record, _ = session_on(HEAD_ON, "silent", dance, settings=TURN, core=V9, first_asked=a)
    assert record["max_decision_points_per_agent"] == 6
    assert len(points_of(record, a)) >= 2 and len(points_of(record, b)) >= 2
    first = points_of(record, a)[0]
    assert first["parsed"]["signal"] == "none" and first["parsed"]["message"] == ""
    assert {"signal_ignored", "message_ignored"} <= set(first["parsed"]["flags"])
    assert not record["signals"] and not record["utterances"]
    system = first["prompt"]["messages"][0]["content"]
    assert "You may be asked again later, if something changes." in system and '"signal"' not in system


# --- the experiment layer ---------------------------------------------------------------------------


def raw(path):
    return copy.deepcopy(load_yaml(resolve_path(path)))


def test_the_template_and_the_exchange_must_agree_and_the_template_must_offer_each_condition():
    nine_real = raw(CONFIG)
    del nine_real["protocol"]["exchange"]
    with pytest.raises(ConfigError, match="turn_taking exchange"):
        E.ResolutionConfig.from_raw(nine_real)
    eight_turn = raw(RF39)
    eight_turn["protocol"]["exchange"] = "turn_taking"
    with pytest.raises(ConfigError, match="real_time exchange"):
        E.ResolutionConfig.from_raw(eight_turn)
    eight_silent = raw(RF39)
    eight_silent["conditions"] = ["silent"]
    with pytest.raises(ConfigError, match="no section"):
        E.ResolutionConfig.from_raw(eight_silent)


def test_rf40s_config_is_rf39s_sessions_with_turn_taking_silent_and_resolve_v9():
    rf39, new = E.ResolutionConfig.load(RF39), E.ResolutionConfig.load(CONFIG)
    assert new.experiment_name == "rf40_round1_head_on_turn_taking"
    assert new.conditions == ("silent", "non_verbal", "talk")
    assert new.templates == {**rf39.templates, "core": "resolve_v9"}
    assert new.protocol == replace(rf39.protocol, exchange=P.EXCHANGE_TURN_TAKING)
    assert new.llm == rf39.llm and new.resolution_gate == rf39.resolution_gate and new.design == rf39.design
    assert new.budget["cap_usd"] == 0.0  # no paid run approved for #129 yet
    sessions = E.plan(new).sessions
    assert len(sessions) == 816 and Counter(s.condition for s in sessions) == {"silent": 272, "non_verbal": 272, "talk": 272}
    # The same people as RF-39's sessions of the same cell (silent: as RF-39's non-verbal ones).
    old = {s.session_id: s for s in E.plan(rf39).sessions}
    for session in sessions:
        twin = old["N" + session.session_id[1:]] if session.condition == "silent" else old[session.session_id]
        assert session.personas == twin.personas and session.cell == twin.cell, session.session_id
    # Who is asked first: person 1 in repeats 1 and 3, person 2 in 2 and 4.
    for session in sessions:
        one = session.agents[0] if session.cell["mapping"] == "p1_lower" else session.agents[1]
        assert (E.first_asked(session) == one) == (session.repeat % 2 == 1), session.session_id
    design = [s for s in sessions if s.pair_id is None]
    assert Counter(E.first_asked(s) == (s.agents[0] if s.cell["mapping"] == "p1_lower" else s.agents[1]) for s in design) == {True: 384, False: 384}
