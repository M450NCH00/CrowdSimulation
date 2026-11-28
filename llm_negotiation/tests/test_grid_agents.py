"""Issue #140 (RF-51): LLM agents on the grid, in their own frame and in the absolute frame.

The grid is an add-on (AS1): everything tested here is in new files (``negsim/grid/``,
``configs/grid/``). The templates are the grid's own, frozen in ``negsim/grid/templates``; their
fixed text is ``resolve_menu_v1``'s (``resolve_menu_abs_v1``'s) silent section word for word, and
the view is in cells and lanes. The menu is AS3's in cells (the user, 2026-11-26).
"""

from __future__ import annotations

import json
import re
import shutil

import pytest

from negsim.configutil import ConfigError
from negsim.llm.mock import MockClient
from negsim.resolution import mock as M
from negsim.resolution import scenarios as S
from negsim.resolution.prompt import CoreTemplate, DebriefTemplate
from negsim.rulegen.protocol import LLMSettings
from negsim.grid import experiment as GE
from negsim.grid import prompt as GP
from negsim.grid.agents import GridSession
from negsim.grid.menu import CARRY_ON, lanes_free, plan_for
from negsim.grid.prompt import GridTemplate
from negsim.grid.world import Move, Walker, head_on, load_config, step

CONFIG = load_config()
OWN = GridTemplate.load("resolve_grid_v1")
ABS = GridTemplate.load("resolve_grid_abs_v1")
LLM = LLMSettings("deepseek-flash", 1.0, 300)
DEBRIEF = DebriefTemplate.load("resolve_debrief_v3")
GRID_OWN, GRID_ABS = "configs/grid/round1_grid.yaml", "configs/grid/round1_grid_abs.yaml"
SIDE_WORDS = re.compile(r"\b(your|their|my) (own )?(left|right)\b", re.I)


def choose(action):
    return json.dumps({"intent": f"I {action}.", "action": action, "reason": "r"})


def client_for(by_walker):
    """A mock that answers each walker with its list of options in turn (the last one repeated),
    and every debrief with RF-47's mock debrief."""
    def policy(request):
        meta = request.metadata
        if meta.get("kind") == "debrief":
            return M._debrief_answer(request, 0)
        options = by_walker[meta["agent_id"]]
        return choose(options[min(int(meta["decision_point"]) - 1, len(options) - 1)])
    return MockClient(policy=policy)


def session(template, lanes, by_walker, **kwargs):
    run = GridSession(CONFIG, lanes, 7, template, client_for(by_walker), LLM, DEBRIEF, **kwargs)
    run.run_session()
    return run, run.as_dict()


# --- the templates ------------------------------------------------------------------------------


def test_the_fixed_text_is_the_corridor_menus_silent_text_word_for_word():
    passing = S.load_scenario("passing")
    assert OWN.system() == CoreTemplate.load("resolve_menu_v1").system("silent", passing)
    assert ABS.system() == CoreTemplate.load("resolve_menu_abs_v1").system("silent", passing)
    assert OWN.retry() == CoreTemplate.load("resolve_menu_v1").retry("silent")
    assert OWN.menu.names == CoreTemplate.load("resolve_menu_v1").menu.names
    assert ABS.menu.names == CoreTemplate.load("resolve_menu_abs_v1").menu.names and ABS.walls == {"a": "the blue wall", "b": "the yellow wall"}
    assert (OWN.frame, ABS.frame) == ("own", "absolute")


def test_a_template_changed_after_freezing_is_refused(tmp_path, monkeypatch):
    shutil.copytree(GP.TEMPLATES_DIR, tmp_path / "templates")
    changed = tmp_path / "templates" / "resolve_grid_v1.yaml"
    changed.write_text(changed.read_text(encoding="utf-8").replace("five", "5"), encoding="utf-8")
    monkeypatch.setattr(GP, "TEMPLATES_DIR", tmp_path / "templates")
    monkeypatch.setattr(GP, "MANIFEST", tmp_path / "templates" / "MANIFEST.json")
    with pytest.raises(ConfigError, match="has changed since it was frozen"):
        GridTemplate.load("resolve_grid_v1")
    with pytest.raises(ConfigError, match="not in"):
        GridTemplate.load("resolve_grid_v9")


# --- the menu in cells --------------------------------------------------------------------------


def walker(lane, direction, row=20):
    return Walker(0, row, lane, direction)


def test_each_option_becomes_its_moves_in_cells():
    by = {o.name: o for o in OWN.menu.options}
    w = walker(2, 1)
    assert plan_for(by["carry on"], w, CONFIG) == CARRY_ON
    assert plan_for(by["slow down a little"], w, CONFIG).speed_factor == 0.81
    assert plan_for(by["slow down a lot"], w, CONFIG).speed_factor == 0.5
    assert plan_for(by["stop and wait"], w, CONFIG).moves == (Move.WAIT,) * 3  # 1.0 s / 0.3077 s, rounded
    assert plan_for(by["step back"], w, CONFIG).moves == (Move.BACK,)  # 0.5 m / 0.4 m, rounded
    assert plan_for(by["step a little to your left"], w, CONFIG).moves == (Move.FORWARD_LEFT,)  # 0.47 m: one lane
    assert plan_for(by["step well to your right"], w, CONFIG).moves == (Move.FORWARD_RIGHT,) * 2  # 0.93 m: two lanes


def test_a_step_aside_goes_no_further_than_the_wall_allows():
    well_left = next(o for o in OWN.menu.options if o.name == "step well to your left")
    assert lanes_free(CONFIG, walker(3, 1), "left") == 1 and lanes_free(CONFIG, walker(3, -1), "left") == 3
    capped = plan_for(well_left, walker(3, 1), CONFIG)
    assert capped.moves == (Move.FORWARD_LEFT,) and capped.flags == ("capped_by_wall:left",)
    none = plan_for(well_left, walker(4, 1), CONFIG)
    assert none.moves == () and none.flags == ("no_room:left",)


@pytest.mark.parametrize("direction", [1, -1])
def test_for_each_heading_a_move_towards_a_wall_goes_to_that_wall(direction):
    by = {o.name: o for o in ABS.menu.options}
    for name, sign in (("step a little towards the blue wall", 1), ("step well towards the yellow wall", -1)):
        state = head_on(CONFIG, (2, 2), seed=1)  # rows 5 and 44: far apart
        w = state.walkers[0] if direction > 0 else state.walkers[1]
        start = w.lane
        for move in plan_for(by[name], w, CONFIG).moves:
            step(state, {w.id: move})
        assert (w.lane - start) * sign > 0, (name, direction)  # wall a (blue) is at +y, whichever way the walker heads


# --- the view, for a known grid state ----------------------------------------------------------


def known(template):
    """Walker 0 (heading +x) in row 20, lane 3; walker 1 (heading -x) in row 28, lane 2: 8 cells apart."""
    run = GridSession(CONFIG, (3, 2), 1, template, client_for({0: ["carry on"], 1: ["carry on"]}), LLM, DEBRIEF,
                      people={0: {"age": 25, "gender": "female", "errand": "work"}, 1: {"age": 70, "gender": "male"}})
    run.state.walkers[0].row, run.state.walkers[1].row = 20, 28
    return run


def test_the_view_in_the_agents_own_frame():
    run = known(OWN)
    zero, one = OWN.description(run._view(0)), OWN.description(run._view(1))
    assert "- You are in a corridor five lanes wide." in zero and "cells 0.4 m across" in zero
    assert "- You have one lane on your left before the wall, and three lanes on your right before the wall." in zero
    assert "- Person 1, 8 cells ahead of you, one lane to your right: walking towards you at 1.30 m/s." in zero
    assert "  They look about 70 years old." in zero and "  They look like a man." in zero
    assert "- You have two lanes on your left before the wall, and two lanes on your right before the wall." in one
    # Each sees the other to its own right, as in round 1's apart_20cm.
    assert "- Person 1, 8 cells ahead of you, one lane to your right: walking towards you at 1.30 m/s." in one
    assert "At your current speeds you would meet Person 1 in about 1.1 s." in zero  # 7 cells x 0.4 m / 2.6 m/s


def test_the_view_in_the_absolute_frame_names_lanes_from_the_blue_wall_and_no_side():
    run = known(ABS)
    zero, one = ABS.description(run._view(0)), ABS.description(run._view(1))
    numbering = "- The lanes are numbered from the blue wall: lane 1 is next to the blue wall, and lane 5 is next to the yellow wall."
    assert f"{numbering} You are in lane 2." in zero and f"{numbering} You are in lane 3." in one
    assert "- Person 1, 8 cells ahead of you, in lane 3: walking towards you at 1.30 m/s." in zero
    assert "- Person 1, 8 cells ahead of you, in lane 2: walking towards you at 1.30 m/s." in one
    assert not SIDE_WORDS.search(zero + one + ABS.system())


def test_someone_out_of_range_is_not_seen_and_no_meeting_is_predicted():
    run = known(OWN)
    run.state.walkers[1].row = 47  # 27 cells: 10.8 m, beyond the 10 m seeing range
    text = OWN.description(run._view(0))
    assert "- You do not see anyone nearby." in text and "meet" not in text
    assert not run._meeting(run.state.walkers[0], run.state.walkers[1])


def test_a_move_since_the_last_look_and_what_came_of_a_decision_in_both_frames():
    for template, moved, done in (
        (OWN, "they have moved one lane to your left", "Since then you have moved one lane to your right."),
        (ABS, "they have moved one lane towards the yellow wall", "Since then you have moved one lane towards the yellow wall."),
    ):
        run, record = session(template, (2, 2), {0: ["step a little to your right" if template is OWN else "step a little towards the yellow wall", "carry on"],
                                                 1: ["step a little to your left" if template is OWN else "step a little towards the yellow wall", "carry on"]})
        texts = [p["prompt"]["messages"][1]["content"] for p in record["decision_points"] if p["number"] == 2]
        assert any(moved in t for t in texts) and any(done in t for t in texts), texts


# --- the session --------------------------------------------------------------------------------


def test_both_stepping_to_their_own_right_pass_two_lanes_apart():
    run, record = session(OWN, (2, 2), {0: ["step a little to your right", "carry on"], 1: ["step a little to your right", "carry on"]})
    g = record["grid_outcome"]
    assert record["outcome"] == "completed" and g["resolved"] and g["passing_distance_m"] == 0.8
    assert record["gate_columns"]["resolved_plan_only"] == "True"


def test_both_choosing_the_blue_wall_head_into_one_lane():
    # The expected trap of a shared frame (RF-48): each "towards the blue wall" is a different own side.
    run, record = session(ABS, (2, 2), {0: ["step a little towards the blue wall"], 1: ["step a little towards the blue wall"]})
    first = [p for p in record["decision_points"] if p["number"] == 1]
    assert {p["agent_id"]: p["side"] for p in first} == {0: "left", 1: "right"}
    assert record["grid_outcome"]["first_changes_towards_same_wall"] and not record["grid_outcome"]["resolved"]


def test_two_who_carry_on_are_blocked_face_to_face_asked_again_and_end_in_a_deadlock():
    run, record = session(OWN, (2, 2), {0: ["carry on"], 1: ["carry on"]})
    g = record["grid_outcome"]
    assert g["blocked_face_to_face"] and g["deadlock"] and not g["resolved"]
    # Asked at the trigger, then every 4 ticks while blocked, until nobody has advanced for 3 s (10 ticks).
    numbers = {a: max(p["number"] for p in record["decision_points"] if p["agent_id"] == a) for a in (0, 1)}
    assert numbers == {0: 4, 1: 4}
    assert "blocked" in [r for p in record["decision_points"] for r in p["reasons"]]
    gaps = [b["tick"] - a["tick"] for a, b in zip(record["decision_points"][::2], record["decision_points"][2::2])]
    assert min(gaps) >= 4  # D5's 1 s apart: 4 ticks of 0.31 s
    assert len(record["debriefs"]) == 2 and all(d["parsed"] for d in record["debriefs"])


def test_no_agent_is_asked_more_than_six_times():
    run, record = session(OWN, (2, 2), {0: ["stop and wait"], 1: ["step back"]})
    assert all(sum(1 for p in record["decision_points"] if p["agent_id"] == a) <= 6 for a in (0, 1))


def test_who_is_asked_first_is_the_sessions_and_an_unreadable_reply_changes_nothing():
    run, record = session(OWN, (2, 1), {0: ["step aside"], 1: ["carry on"]}, first_asked=1)
    first = record["decision_points"][:2]
    assert [p["agent_id"] for p in first] == [1, 0] and first[0]["tick"] == first[1]["tick"]
    bad = [p for p in record["decision_points"] if p["agent_id"] == 0]
    assert all(p["parsed"] is None and str(p["parse_error"]).startswith("unknown_action") and len(p["attempts"]) == 2 for p in bad)
    assert run.members[0].plan == CARRY_ON


# --- the experiment -----------------------------------------------------------------------------


def test_the_sessions_are_rf40s_silent_ones_with_who_is_off_centre_counterbalanced():
    config = GE.GridExperimentConfig.load(GRID_OWN)
    _, sessions = GE.grid_sessions(config)
    assert len(sessions) == 272 and {s.condition for s in sessions} == {"silent"}
    layouts = [GE.lanes_of(config, s) for s in sessions]
    assert sum(1 for g, lanes, off in layouts if g == "aligned" and lanes == (2, 2)) == 136
    assert {(lanes, off) for g, lanes, off in layouts if g == "one_lane_apart"} == {((2, 1), "p2"), ((3, 2), "p1")}
    for s, (g, lanes, off) in zip(sessions, layouts):
        if g == "one_lane_apart":
            assert off == ("p1" if s.repeat in (3, 4) else "p2")
    abs_config = GE.GridExperimentConfig.load(GRID_ABS)
    assert abs_config.templates["core"] == "resolve_grid_abs_v1" and abs_config.llm["mock_policy"] == "resolution_menu_abs_rehearsal_v1"


@pytest.mark.parametrize("change, match", [
    ({"conditions": ["silent", "talk"]}, "silent only"),
    ({"llm": {"client": "deepseek"}}, "mock only"),
    ({"budget": {"cap_usd": 0.5, "ledger": "spend_ledger.jsonl"}}, "mock only"),
])
def test_the_config_refuses_other_conditions_and_any_paid_run(tmp_path, change, match):
    import yaml

    raw = yaml.safe_load(open(GE.resolve_path(GRID_OWN), encoding="utf-8"))
    for key, value in change.items():
        raw[key] = {**raw[key], **value} if isinstance(value, dict) else value
    path = tmp_path / "grid.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ConfigError, match=match):
        GE.GridExperimentConfig.load(path)


def test_the_cost_estimate_is_calibrated_on_rf40s_silent_calls():
    cal = GE.calibration()
    assert 0.15 < cal["tokens_per_char"] < 0.5 and 0 < cal["cache_hit_share"] < 1 and cal["calls"] > 1000
    _, record = session(OWN, (2, 2), {0: ["carry on"], 1: ["carry on"]})
    estimate = GE.estimate_cost([record], "deepseek-flash", cal)
    assert estimate["calls"] == record["totals"]["calls"]
    assert 0 < estimate["off_peak"]["low_usd"] <= estimate["off_peak"]["high_usd"] <= estimate["peak"]["high_usd"]
