"""Issue #98 (RF-27): ``resolve_v7``, the user's decisions of 2026-10-25.

The description says where the centre of someone ahead is against the straight line ahead of the
agent, gives their width from 10 m, and calls someone "straight ahead" only within 1°. The reply
parser is unchanged. Every earlier template renders exactly as before.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from negsim.negotiation import prompts
from negsim.resolution import experiment as E
from negsim.resolution.prompt import CoreTemplate, render
from test_perceive import PASSING, body, look, perceiver

V6, V7 = CoreTemplate.load("resolve_v6"), CoreTemplate.load("resolve_v7")
NEW_VIEW_KEYS = {"seen_short_body", "seen_line_offset", "seen_on_line"}


def seen_text(core, distance, lateral, vx=-1.3, radius=0.35, condition="independent"):
    """WHO YOU CAN SEE for an observer at the origin walking +x and the other ``distance`` m ahead,
    ``lateral`` m to the observer's left (negative: right), walking at ``vx``."""
    other = body(1, distance, lateral, vx=vx, radius=radius)
    text = render(look([body(0, 0.0, 0.0, vx=1.3), other], perceiver(core=core)), condition, PASSING, core).user
    return text.split("WHO YOU CAN SEE\n")[1].split("\n\n")[0]


# --- resolve_v7 against resolve_v6 ----------------------------------------------------------------


def test_resolve_v7_is_resolve_v6_but_for_three_view_lines_and_the_direction_setting():
    assert prompts.load_manifest()["resolve_v7"]["kind"] == "resolution"
    assert V6.direction_ahead_deg is None and V7.direction_ahead_deg == 1.0
    keys = set(V7.data) - {"version", "provenance", "direction_ahead_deg"}
    assert keys == set(V6.data) - {"version", "provenance"}
    for key in keys - {"view"}:
        assert V7.data[key] == V6.data[key], key
    assert set(V7.data["view"]) - set(V6.data["view"]) == NEW_VIEW_KEYS
    assert {k: V7.data["view"][k] for k in V6.data["view"]} == V6.data["view"]
    for condition in ("independent", "non_verbal", "talk"):
        assert V7.system(condition, PASSING) == V6.system(condition, PASSING)  # the same cached prefix
        assert V7.retry(condition) == V6.retry(condition)
    # The reply parser's settings are resolve_v6's (the user's decision 5).
    assert (V7.later_step_start, V7.until_at_distance, V7.until_event_as_object) == (V6.later_step_start, V6.until_at_distance, V6.until_event_as_object)


@pytest.mark.parametrize("key", ["resolve_v2", "resolve_v3", "resolve_v4", "resolve_v5", "resolve_v6"])
def test_no_earlier_template_has_the_new_lines(key):
    core = CoreTemplate.load(key)
    assert core.direction_ahead_deg is None and not NEW_VIEW_KEYS & set(core.data["view"])
    text = seen_text(core, 9.76, -0.2)
    assert "straight line ahead" not in text and "straight ahead of you" in text


# --- the line offset -------------------------------------------------------------------------------


@pytest.mark.parametrize(("lateral", "line"), [
    (-0.2, "Their centre is 0.2 m to your right of the straight line ahead of you."),
    (0.2, "Their centre is 0.2 m to your left of the straight line ahead of you."),
    (0.74, "Their centre is 0.7 m to your left of the straight line ahead of you."),
    (0.04, "Their centre is on the straight line ahead of you."),
    (0.0, "Their centre is on the straight line ahead of you."),
])
@pytest.mark.parametrize("distance", [9.76, 4.5])
def test_where_the_others_centre_is_against_the_line_ahead_at_both_detail_levels(lateral, line, distance):
    text = seen_text(V7, distance, lateral)
    assert f"  {line}" in text.splitlines()
    assert text.count("straight line ahead") == 1


def test_a_drifting_walker_is_placed_where_they_are_now():
    rad = math.radians(180.0 - 20.0)
    other = body(1, 6.0, 0.5, vx=1.3 * math.cos(rad), vy=1.3 * math.sin(rad))
    text = render(look([body(0, 0.0, 0.0, vx=1.3), other], perceiver(core=V7)), "talk", PASSING, V7).user
    assert "drifting to your left by 20°" in text and "Their centre is 0.5 m to your left" in text


def test_nobody_level_or_behind_gets_a_line_offset():
    core = V7
    for degrees in (90.0, 120.0, -150.0):
        person = SimpleNamespace(bearing_rad=math.radians(degrees), distance_m=3.0)
        assert core._line_offset(person) == []
    person = SimpleNamespace(bearing_rad=math.radians(80.0), distance_m=3.0)
    assert core._line_offset(person) == ["  Their centre is 3.0 m to your left of the straight line ahead of you."]
    assert V6._line_offset(SimpleNamespace(bearing_rad=0.1, distance_m=3.0)) == []


# --- the width and the direction -------------------------------------------------------------------


def test_the_others_width_is_given_from_10_m():
    far6, far7 = seen_text(V6, 9.76, -0.2), seen_text(V7, 9.76, -0.2)
    assert "Their body is 0.70 m wide." not in far6 and "  Their body is 0.70 m wide." in far7.splitlines()
    near7 = seen_text(V7, 4.5, -0.2)
    assert near7.count("Their body is 0.70 m wide.") == 1  # the full-detail line, not twice


@pytest.mark.parametrize(("lateral", "v6", "v7"), [
    (0.1, "straight ahead of you", "straight ahead of you"),            # 0.6 degrees at 9.76 m
    (-0.2, "straight ahead of you", "ahead of you and 1° to your right"),  # 1.2 degrees
    (0.6, "straight ahead of you", "ahead of you and 4° to your left"),    # 3.5 degrees
    (1.2, "ahead of you and 7° to your left", "ahead of you and 7° to your left"),
])
def test_straight_ahead_is_within_1_degree_under_resolve_v7_and_5_before(lateral, v6, v7):
    assert v6 in seen_text(V6, 9.76, lateral).splitlines()[0]
    assert v7 in seen_text(V7, 9.76, lateral).splitlines()[0]


# --- the config -------------------------------------------------------------------------------------


def test_rf27s_config_is_rf10s_independent_sessions_under_resolve_v7():
    old = E.ResolutionConfig.load("configs/resolution/round1_head_on_screening.yaml")
    new = E.ResolutionConfig.load("configs/resolution/round1_head_on_v7.yaml")
    assert new.experiment_name == "rf27_round1_head_on_v7" and new.conditions == ("independent",)
    assert new.templates["core"] == "resolve_v7" and old.templates["core"] == "resolve_v6"
    assert new.budget["cap_usd"] == 0.08 and new.budget["over_cap"] == "stop_at_cap"
    old_sessions = {s.session_id: s for s in E.plan(old).sessions if s.condition == "independent"}
    new_sessions = {s.session_id: s for s in E.plan(new).sessions}
    assert set(new_sessions) == set(old_sessions) and len(new_sessions) == 96
    for session_id, session in new_sessions.items():
        assert session.personas == old_sessions[session_id].personas, session_id


@pytest.mark.parametrize(("path", "name", "max_tokens", "cap"), [
    ("configs/resolution/round1_head_on_v4pro.yaml", "rf28_round1_head_on_v4pro", 300, 0.30),  # the first 6 sessions
    ("configs/resolution/round1_head_on_v4pro_cap600.yaml", "rf28_round1_head_on_v4pro_cap600", 600, 0.28),  # the run of record
])
def test_rf28s_configs_are_rf10s_independent_sessions_on_deepseek_v4_pro(path, name, max_tokens, cap):
    # Issue #100 (RF-28): the same sessions, resolve_v6 as in RF-10; the model changed, and in the
    # run of record the reply cap too (the user's decision: v4-pro's pretty-printed JSON ran past 300).
    old = E.ResolutionConfig.load("configs/resolution/round1_head_on_screening.yaml")
    new = E.ResolutionConfig.load(path)
    assert new.experiment_name == name and new.conditions == ("independent",)
    assert new.templates == old.templates and new.llm["model"] == "deepseek-v4-pro" and old.llm["model"] == "deepseek-flash"
    assert new.llm["max_tokens"] == max_tokens and old.llm["max_tokens"] == 300
    others = lambda llm: {k: v for k, v in llm.items() if k not in ("model", "max_tokens")}
    assert others(new.llm) == others(old.llm)
    assert new.budget["cap_usd"] == cap and new.budget["over_cap"] == "stop_at_cap"
    old_sessions = {s.session_id: s for s in E.plan(old).sessions if s.condition == "independent"}
    new_sessions = {s.session_id: s for s in E.plan(new).sessions}
    assert set(new_sessions) == set(old_sessions) and len(new_sessions) == 96
    for session_id, session in new_sessions.items():
        assert session.personas == old_sessions[session_id].personas, session_id
