"""Issue #155 (RF-54): the sideways gap after a sidestep (``resolve_v11``).

The user's choices of 2026-11-28: target recovery from a same-wall start ("Recovery cue"), and name the
template v11 (``resolve_v10`` is RF-46's). Under a core template with ``sideways_gap`` the perceiver
works out, for each person seen at the last look too, where their centre was and is against the
agent's, across the agent's path, and how far each moved across in between; the template prints it
only once one of the two has moved across (to 0.1 m), so decision 1 is ``resolve_v9``'s word for word.
Every earlier template records and renders exactly as before.
"""

from __future__ import annotations

import json
import math
from dataclasses import replace

import pytest

from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution import protocol as P
from negsim.resolution.perceive import Body, sideways_since
from negsim.resolution.prompt import CoreTemplate
from negsim.resolution.view import DETAIL_FULL, DETAIL_SHORT, Me, SeenPerson, Sideways, View
from test_encounter_protocol import HEAD_ON, session_on

V9, V11 = CoreTemplate.load("resolve_v9"), CoreTemplate.load("resolve_v11")
RF40 = "configs/resolution/round1_head_on_turn_taking.yaml"
RF54 = "configs/resolution/rf54_round1_head_on_sideways_gap.yaml"
TURN = P.ProtocolSettings(execution=X.EXECUTION_KEEP_LINE_REPLAN, max_decision_points=6, exchange=P.EXCHANGE_TURN_TAKING)
A, B = HEAD_ON["agents"]  # head_on_02dfbadb: walking lines 20 cm apart


def sidestep(side, metres=0.4):
    """A sidestep followed by the plain step the model usually writes (memory: rehearse multi-step plans)."""
    return json.dumps({"intent": "Make room.", "steps": [
        {"start": "now", "speed_mps": 1.1, "sidestep": {"to": side, "metres": metres}},
        {"speed_mps": 1.1, "until": "other_passes"},
    ], "reason": "r"})


def run(core, a_side, b_side):
    answers = {A: [sidestep(a_side)] * 6, B: [sidestep(b_side)] * 6}
    _, record, _ = session_on(HEAD_ON, "silent", answers, settings=TURN, core=core, first_asked=A)
    return record


def content(point):
    return point["prompt"]["messages"][-1]["content"]


# --- the template ---------------------------------------------------------------------------------


def test_resolve_v11_is_v9_word_for_word_plus_the_gap_lines():
    nine, eleven = V9.data, V11.data
    assert eleven["version"] == 11 and eleven["sideways_gap"] is True and V11.sideways_gap and not V9.sideways_gap
    left_alone = ("template_id", "kind", "description", "system", "role", "conditions", "step_format", "event_item", "decision_point",
                  "later_step_start", "until_at_distance", "until_event_as_object", "sidestep", "exchange", "heard_frame")
    for key in left_alone:
        assert eleven[key] == nine[key], key
    assert set(eleven) - set(nine) == {"sideways_gap"}
    extra = {"seen_gap_both", "seen_gap", "gap_where", "gap_trends"}
    assert set(eleven["view"]) - set(nine["view"]) == extra
    assert {k: v for k, v in eleven["view"].items() if k not in extra} == nine["view"]
    assert eleven["provenance"].startswith("Issue #155 (RF-54)") and "resolve_v10 is RF-46's" in eleven["provenance"]


def test_no_earlier_core_template_works_out_the_gap():
    for n in range(1, 10):
        assert not CoreTemplate.load(f"resolve_v{n}").sideways_gap
    for menu in ("resolve_menu_v1", "resolve_menu_abs_v1", "resolve_menu_abs_swap_v1"):
        assert not CoreTemplate.load(menu).sideways_gap


# --- what the perceiver works out -----------------------------------------------------------------


def body(agent, xy, heading_deg=0.0, path_deg=0.0, speed=1.3):
    rad = math.radians(heading_deg)
    return Body(agent, xy, (speed * math.cos(rad), speed * math.sin(rad)), rad, 0.25, path_rad=math.radians(path_deg))


def test_the_gap_is_across_the_agents_path_not_its_direction_of_travel():
    # The agent is mid-sidestep, walking 30 degrees to its right of its path (+x); the other is 6 m ahead
    # and 0.2 m to the agent's right. Across the travel direction, the 6 m along would count as sideways.
    me_then, them_then = body(0, (0.0, 0.0)), body(1, (7.0, -0.2), heading_deg=180.0, path_deg=180.0)
    me_now, them_now = body(0, (0.7, -0.4), heading_deg=-30.0), body(1, (6.0, -0.2), heading_deg=180.0, path_deg=180.0)
    gap = sideways_since(me_then, them_then, me_now, them_now)
    assert gap.gap_then_m == pytest.approx(-0.2) and gap.gap_now_m == pytest.approx(0.2)
    assert gap.moved_me_m == pytest.approx(-0.4) and gap.moved_them_m == pytest.approx(0.0)


def test_a_body_with_no_path_falls_back_on_its_facing():
    # The grid's bodies (negsim.grid.agents) carry no path direction.
    plain = Body(0, (0.0, 0.0), (0.0, 0.0), math.pi / 2, 0.25)
    assert plain.path_rad is None
    gap = sideways_since(plain, Body(1, (1.0, 3.0), (0.0, 0.0), 0.0, 0.25), replace(plain, position=(0.0, 0.0)), Body(1, (2.0, 3.0), (0.0, 0.0), 0.0, 0.25))
    assert gap.gap_then_m == pytest.approx(-1.0) and gap.gap_now_m == pytest.approx(-2.0)  # facing +y: its left is -x


# --- in a session ---------------------------------------------------------------------------------


def test_same_wall_both_moved_over_and_the_gap_stayed_the_same_on_a_short_line():
    # Person 1 steps to its right, person 2 to its left: towards the same wall. At decision 2 they are
    # about 7.8 m apart, so the other is on a short line, which in resolve_v9 says nothing of the move.
    record = run(V11, "right", "left")
    a2 = [p for p in record["decision_points"] if p["agent_id"] == A][1]
    b2 = [p for p in record["decision_points"] if p["agent_id"] == B][1]
    assert a2["view"]["seen"][0]["detail"] == DETAIL_SHORT
    assert ("  Since you last looked, you and they have both moved over to your right.\n"
            "  Sideways, their centre was 0.2 m to your right of yours and is now 0.2 m to your right of yours, "
            "so the gap between your centres has stayed the same.") in content(a2)
    assert "you and they have both moved over to your left." in content(b2)
    gap = a2["view"]["seen"][0]["sideways"]
    assert gap["moved_me_m"] == pytest.approx(-0.4, abs=0.01) and gap["moved_them_m"] == pytest.approx(-0.4, abs=0.01)
    assert gap["gap_then_m"] == pytest.approx(-0.2, abs=0.01) and gap["gap_now_m"] == pytest.approx(-0.2, abs=0.01)
    # The agent's own move agrees with WHAT YOU HAVE DONE SO FAR, measured across its facing at decision 1,
    # which is its path to within ORCA's sub-millimetre drift.
    assert a2["view"]["history"][0]["sideways_m"] == pytest.approx(gap["moved_me_m"], abs=1e-3)


def test_opposite_walls_the_gap_grew_and_the_crossing_is_named_by_both_sides():
    record = run(V11, "right", "right")
    a2 = [p for p in record["decision_points"] if p["agent_id"] == A][1]
    assert ("  Sideways, their centre was 0.2 m to your right of yours and is now 0.6 m to your left of yours, "
            "so the gap between your centres has grown.") in content(a2)
    assert "both moved over" not in content(a2)


def test_decision_1_and_every_record_under_v9_are_as_before():
    for a_side, b_side in (("right", "left"), ("right", "right")):
        nine, eleven = run(V9, a_side, b_side), run(V11, a_side, b_side)
        first = lambda r: [p for p in r["decision_points"] if p["step"] == r["decision_points"][0]["step"]]
        assert [content(p) for p in first(nine)] == [content(p) for p in first(eleven)]
        assert [p["prompt"]["messages"][0] for p in nine["decision_points"]] == [p["prompt"]["messages"][0] for p in eleven["decision_points"]]
        assert all("sideways" not in s for p in nine["decision_points"] for s in p["view"]["seen"])
        assert "Sideways," not in "".join(content(p) for p in nine["decision_points"])
        # The same replies give the same encounter: only the description differs.
        assert [(p["agent_id"], p["time_s"]) for p in nine["decision_points"]] == [(p["agent_id"], p["time_s"]) for p in eleven["decision_points"]]


def test_nobody_moving_across_means_no_gap_line():
    carry_on = json.dumps({"intent": "Carry on.", "steps": [], "reason": "r"})
    answers = {A: carry_on, B: carry_on}
    _, nine, _ = session_on(HEAD_ON, "silent", answers, settings=TURN, core=V9, first_asked=A)
    _, eleven, _ = session_on(HEAD_ON, "silent", answers, settings=TURN, core=V11, first_asked=A)
    assert [content(p) for p in nine["decision_points"]] == [content(p) for p in eleven["decision_points"]]


# --- the rendering ----------------------------------------------------------------------------------


def described(gap, detail=DETAIL_FULL):
    person = SeenPerson(label=1, detail=detail, distance_m=4.0, bearing_rad=0.0, speed_mps=1.3, heading_relative_rad=math.pi,
                        closing_speed_mps=2.6, width_m=0.5, sideways=gap)
    view = View(agent_id=0, decision_point=2, me=Me(1.3, 1.3, 2.0, 0.5), place=(), templates={"core": {}, "scenario": {}}, seen=(person,))
    return V11.description(view)


@pytest.mark.parametrize("gap, words", [
    (Sideways(0.3, 0.0, 0.3, 0.0), "their centre was 0.3 m to your left of yours and is now in line with yours, so the gap between your centres has shrunk."),
    (Sideways(-0.6, -0.2, 0.0, 0.4), "their centre was 0.6 m to your right of yours and is now 0.2 m to your right of yours, so the gap between your centres has shrunk."),
    (Sideways(0.0, 0.5, -0.25, 0.25), "their centre was in line with yours and is now 0.5 m to your left of yours, so the gap between your centres has grown."),
])
def test_the_gap_line_names_each_side_and_the_trend(gap, words):
    for detail in (DETAIL_FULL, DETAIL_SHORT):
        assert "  Sideways, " + words in described(gap, detail)


def test_moves_under_5_cm_are_not_told_and_opposite_moves_are_not_both():
    assert "Sideways" not in described(Sideways(0.2, 0.24, 0.04, -0.04))
    text = described(Sideways(0.2, 0.9, -0.3, 0.4))
    assert "both moved over" not in text and "has grown." in text


def test_a_gap_is_left_out_of_a_view_record_unless_set():
    view = View(agent_id=0, decision_point=1, me=Me(1.3, 1.3, 2.0, 0.5), place=(), templates={"core": {}, "scenario": {}},
                seen=(SeenPerson(1, DETAIL_FULL, 4.0, 0.0, 1.3, math.pi, 2.6, 0.5),))
    assert "sideways" not in view.as_dict()["seen"][0]
    with_gap = replace(view, seen=(replace(view.seen[0], sideways=Sideways(0.1, 0.2, 0.0, 0.1)),))
    assert with_gap.as_dict()["seen"][0]["sideways"] == {"gap_then_m": 0.1, "gap_now_m": 0.2, "moved_me_m": 0.0, "moved_them_m": 0.1}


# --- the config -------------------------------------------------------------------------------------


def test_rf54_is_rf40s_silent_sessions_with_only_the_template_changed():
    rf40, rf54 = E.ResolutionConfig.load(RF40), E.ResolutionConfig.load(RF54)
    assert rf54.experiment_name == "rf54_round1_head_on_sideways_gap" and rf54.conditions == ("silent",)
    assert (rf54.design, rf54.protocol, rf54.resolution_gate, rf54.llm_view, rf54.factor_values, rf54.llm) == (
        rf40.design, rf40.protocol, rf40.resolution_gate, rf40.llm_view, rf40.factor_values, rf40.llm)
    assert rf54.templates == {**rf40.templates, "core": "resolve_v11"}
    assert rf54.llm["client"] == "mock" and rf54.llm_settings().thinking is False
    assert {k: v for k, v in rf54.budget.items() if k != "cap_usd"} == {k: v for k, v in rf40.budget.items() if k != "cap_usd"}


def test_every_rf54_session_is_rf40s_silent_session_with_the_same_people():
    rf40 = {s.session_id: s for s in E.plan(E.ResolutionConfig.load(RF40)).sessions if s.condition == "silent"}
    rf54 = {s.session_id: s for s in E.plan(E.ResolutionConfig.load(RF54)).sessions}
    assert len(rf54) == 272 and set(rf54) == set(rf40)
    for key, session in rf54.items():
        theirs = rf40[key]
        assert dict(session.personas) == dict(theirs.personas) and session.cell == theirs.cell and session.repeat == theirs.repeat


def test_the_cap_is_the_one_claude_md_records_for_issue_155():
    from negsim.configutil import REPO_ROOT, load_yaml, resolve_path

    recorded = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "**Approved for issue #155 only, 2026-11-28:**" in recorded and "**USD 0.60** on" in recorded
    assert load_yaml(resolve_path("configs/resolution/rf54_round1_head_on_sideways_gap.yaml"))["budget"]["cap_usd"] == 0.60
