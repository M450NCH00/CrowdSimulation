"""Issue #157 (RF-55): only "they have moved over" on short lines (``resolve_v12``).

The user's decision of 2026-11-28: separate the two halves of RF-54's ``resolve_v11``. ``resolve_v12`` is
``resolve_v9`` word for word plus ``seen_short_moved``, which prints ``resolve_v9``'s own "Since you last
looked, they have moved over to your {side}." under the short line of someone 5 to 10 m away, when the
perceiver (unchanged) finds they have. Only the move over; no gap numbers, no "both moved over". Every
earlier template records and renders exactly as before.
"""

from __future__ import annotations

import json
import math

from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution import protocol as P
from negsim.resolution.prompt import CoreTemplate
from negsim.resolution.view import DETAIL_FULL, DETAIL_SHORT, Me, SeenPerson, View
from test_encounter_protocol import HEAD_ON, session_on

V9, V12 = CoreTemplate.load("resolve_v9"), CoreTemplate.load("resolve_v12")
RF40 = "configs/resolution/round1_head_on_turn_taking.yaml"
RF54 = "configs/resolution/rf54_round1_head_on_sideways_gap.yaml"
RF55 = "configs/resolution/rf55_round1_head_on_short_moved.yaml"
TURN = P.ProtocolSettings(execution=X.EXECUTION_KEEP_LINE_REPLAN, max_decision_points=6, exchange=P.EXCHANGE_TURN_TAKING)
A, B = HEAD_ON["agents"]  # head_on_02dfbadb: walking lines 20 cm apart
MOVED = "  Since you last looked, they have moved over to your {}."


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


def of(record, agent):
    return [p for p in record["decision_points"] if p["agent_id"] == agent]


# --- the template ---------------------------------------------------------------------------------


def test_resolve_v12_is_v9_word_for_word_plus_the_short_line_move():
    nine, twelve = V9.data, V12.data
    assert twelve["version"] == 12 and not V12.sideways_gap
    assert set(twelve) == set(nine)
    for key in set(nine) - {"version", "provenance", "view"}:
        assert twelve[key] == nine[key], key
    assert set(twelve["view"]) - set(nine["view"]) == {"seen_short_moved"}
    assert {k: v for k, v in twelve["view"].items() if k != "seen_short_moved"} == nine["view"]
    # The same words as a full line's change line.
    assert twelve["view"]["seen_short_moved"] == nine["view"]["seen_changes"]
    assert twelve["provenance"].startswith("Issue #157 (RF-55)") and "resolve_v9's provenance: Issue #129" in twelve["provenance"]


def test_no_earlier_core_template_prints_a_move_on_a_short_line():
    for n in (*range(1, 10), 11):  # resolve_v10 is RF-46's, not written yet
        assert "seen_short_moved" not in CoreTemplate.load(f"resolve_v{n}").data["view"]
    for menu in ("resolve_menu_v1", "resolve_menu_abs_v1", "resolve_menu_abs_swap_v1"):
        assert "seen_short_moved" not in CoreTemplate.load(menu).data.get("view", {})


# --- in a session ---------------------------------------------------------------------------------


def test_same_wall_the_move_is_told_on_the_short_line_and_nothing_else_is_added():
    # Person 1 steps to its right (-y), person 2 to its left (-y): towards the same wall. At decision 2
    # they are about 7.8 m apart, a short line, where resolve_v9 says nothing of the other's move.
    record = run(V12, "right", "left")
    a2, b2 = of(record, A)[1], of(record, B)[1]
    assert a2["view"]["seen"][0]["detail"] == DETAIL_SHORT and b2["view"]["seen"][0]["detail"] == DETAIL_SHORT
    assert MOVED.format("right") in content(a2)  # -y is person 1's right
    assert MOVED.format("left") in content(b2)  # and person 2's left
    every = "".join(content(p) for p in record["decision_points"])
    assert "Sideways," not in every and "both moved over" not in every


def test_opposite_walls_the_move_is_to_the_others_left():
    record = run(V12, "right", "right")
    assert MOVED.format("left") in content(of(record, A)[1])  # person 2 stepped to +y, person 1's left


def test_v9_and_v12_differ_only_by_the_added_lines():
    # Both to their own left (apart): no conflict is left after decision 1, so nothing is added.
    for a_side, b_side, at_least in (("right", "left", 2), ("right", "right", 2), ("left", "left", 0)):
        nine, twelve = run(V9, a_side, b_side), run(V12, a_side, b_side)
        # The same replies give the same encounter, the same views and the same system messages.
        assert [(p["agent_id"], p["time_s"]) for p in nine["decision_points"]] == [(p["agent_id"], p["time_s"]) for p in twelve["decision_points"]]
        assert [p["view"] for p in nine["decision_points"]] == [
            {**p["view"], "templates": n["view"]["templates"]} for p, n in zip(twelve["decision_points"], nine["decision_points"])]
        assert [p["prompt"]["messages"][0] for p in nine["decision_points"]] == [p["prompt"]["messages"][0] for p in twelve["decision_points"]]
        added = 0
        for n, t in zip(nine["decision_points"], twelve["decision_points"]):
            lines = content(t).split("\n")
            if t["view"]["seen"] and t["view"]["seen"][0]["detail"] == DETAIL_SHORT:
                kept = [line for line in lines if line not in (MOVED.format("left"), MOVED.format("right"))]
                assert "\n".join(kept) == content(n)
                added += len(lines) - len(kept)
            else:
                assert content(t) == content(n)
        assert added >= at_least, (a_side, b_side)  # decision 2 of each person, at least


def test_nobody_moving_over_means_the_same_prompts():
    carry_on = json.dumps({"intent": "Carry on.", "steps": [], "reason": "r"})
    answers = {A: carry_on, B: carry_on}
    _, nine, _ = session_on(HEAD_ON, "silent", answers, settings=TURN, core=V9, first_asked=A)
    _, twelve, _ = session_on(HEAD_ON, "silent", answers, settings=TURN, core=V12, first_asked=A)
    assert [content(p) for p in nine["decision_points"]] == [content(p) for p in twelve["decision_points"]]


# --- the rendering ----------------------------------------------------------------------------------


def described(core, changes, detail):
    person = SeenPerson(label=1, detail=detail, distance_m=7.0 if detail == DETAIL_SHORT else 4.0, bearing_rad=0.0, speed_mps=1.3,
                        heading_relative_rad=math.pi, closing_speed_mps=2.6, width_m=0.5, changes=changes)
    view = View(agent_id=0, decision_point=2, me=Me(1.3, 1.3, 2.0, 0.5), place=(), templates={"core": {}, "scenario": {}}, seen=(person,))
    return core.description(view)


def test_a_short_line_tells_only_the_move_over():
    short = described(V12, ("slowed_down", "moved_left", "turned"), DETAIL_SHORT)
    assert MOVED.format("left") + "\n" in short + "\n" and "slowed down" not in short and "turned" not in short
    assert "moved over" not in described(V9, ("slowed_down", "moved_left", "turned"), DETAIL_SHORT)
    assert "moved over" not in described(V12, ("slowed_down", "turned"), DETAIL_SHORT)
    assert "moved over" not in described(V12, ("came_into_view",), DETAIL_SHORT)


def test_a_full_line_is_resolve_v9s():
    for changes in ((), ("moved_right",), ("slowed_down", "moved_left", "turned")):
        assert described(V12, changes, DETAIL_FULL) == described(V9, changes, DETAIL_FULL)


# --- the config -------------------------------------------------------------------------------------


def test_rf55_is_rf54_with_only_the_name_the_template_and_the_cap_changed():
    rf40, rf54, rf55 = (E.ResolutionConfig.load(c) for c in (RF40, RF54, RF55))
    assert rf55.experiment_name == "rf55_round1_head_on_short_moved" and rf55.conditions == ("silent",)
    assert (rf55.design, rf55.protocol, rf55.resolution_gate, rf55.llm_view, rf55.factor_values, rf55.llm) == (
        rf54.design, rf54.protocol, rf54.resolution_gate, rf54.llm_view, rf54.factor_values, rf54.llm)
    assert (rf55.design, rf55.llm) == (rf40.design, rf40.llm)
    assert rf55.templates == {**rf40.templates, "core": "resolve_v12"}
    assert rf55.llm["client"] == "mock" and rf55.llm_settings().thinking is False
    assert {k: v for k, v in rf55.budget.items() if k != "cap_usd"} == {k: v for k, v in rf40.budget.items() if k != "cap_usd"}


def test_every_rf55_session_is_rf40s_silent_session_with_the_same_people():
    rf40 = {s.session_id: s for s in E.plan(E.ResolutionConfig.load(RF40)).sessions if s.condition == "silent"}
    rf55 = {s.session_id: s for s in E.plan(E.ResolutionConfig.load(RF55)).sessions}
    assert len(rf55) == 272 and set(rf55) == set(rf40)
    for key, session in rf55.items():
        theirs = rf40[key]
        assert dict(session.personas) == dict(theirs.personas) and session.cell == theirs.cell and session.repeat == theirs.repeat


def test_the_cap_is_the_one_claude_md_records_for_issue_157():
    from negsim.configutil import REPO_ROOT, load_yaml, resolve_path

    recorded = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "**Approved for issue #157 only, 2026-11-28:**" in recorded and "**USD 0.60** on that experiment's own calls
     (`experiment_name: rf55" in recorded
    assert load_yaml(resolve_path(RF55))["budget"]["cap_usd"] == 0.60
