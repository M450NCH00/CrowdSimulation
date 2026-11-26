"""Issue #137 (RF-48): the menu in the corridor's own frame (``resolve_menu_abs_v1``).

AS5 as revised by the user on 2026-11-26 (``docs/action-space.md``, section 7): the corridor's two
long walls get neutral landmark names (here "the blue wall" at +y and "the yellow wall" at -y);
where people are is their distance from one wall; moves aside are named by the wall they go
towards, and code turns them into the agent's own left or right; talk names the walls, with no
facing note; the agent is not told which way it walks. Earlier templates, configs and records are
unchanged (AS4).
"""

from __future__ import annotations

import copy
import json
import math
import re

import pytest

from negsim.configutil import ConfigError, load_yaml, resolve_path
from negsim.experiment.avoidance import simulation_for
from negsim.resolution import experiment as E
from negsim.resolution import mock as M
from negsim.resolution import scenarios as S
from negsim.resolution.menu import Menu, load_menu, menu_context, normalise
from negsim.resolution.prompt import CoreTemplate
from negsim.resolution.reply import ReplyContext, Sidestep, Step, parse_reply
from negsim.resolution.view import (
    DETAIL_FULL, MOTION_WALKING, WALL_A, WALL_B, Done, Frame, Heard, Me, SeenPerson, View,
)
from negsim.rulegen.replay import source_plan
from test_encounter_protocol import points_of, session_on
from test_rf47_menu import ALIGNED, APART, CONFIG as RF47_CONFIG, EVENTS, MENU, MENU_T, TURN, choose

TABLE = "configs/resolution/menu_table_abs_v1.yaml"
ABS_T = CoreTemplate.load("resolve_menu_abs_v1")
ABS = load_menu(TABLE)
CONFIG = "configs/resolution/round1_head_on_menu_abs.yaml"
BLUE, YELLOW = "the blue wall", "the yellow wall"
SIDE_WORDS = re.compile(r"\b(your|their|my) (own )?(left|right)\b|\bto (the|your) (left|right)\b", re.I)


def context(left_wall, room_left=None, room_right=None, menu=ABS):
    return ReplyContext(
        "silent", 2.0, EVENTS, 6.0, menu=menu, usual_speed_mps=1.3, radius_m=0.25,
        room_left_m=room_left, room_right_m=room_right, left_wall=left_wall,
    )


# --- the table ------------------------------------------------------------------------------------


def test_the_table_is_rf47s_with_the_sidesteps_named_by_the_walls():
    assert ABS.names == tuple(ABS_T.data["menu_options"]) == ABS_T.menu.names
    assert ABS.by_wall and not ABS.by_side and MENU.by_side and not MENU.by_wall
    renamed = {
        "step a little to your left": "step a little towards the blue wall",
        "step a little to your right": "step a little towards the yellow wall",
        "step well to your left": "step well towards the blue wall",
        "step well to your right": "step well towards the yellow wall",
    }
    by_side, by_wall = {o.name: o for o in MENU.options}, {o.name: o for o in ABS.options}
    assert [renamed.get(name, name) for name in MENU.names] == list(ABS.names)
    for old, option in by_side.items():
        new = by_wall[renamed.get(old, old)]
        if old in renamed:
            assert (new.kind, new.metres, new.to) == (option.kind, option.metres, None)
            assert new.towards == (WALL_A if option.to == "left" else WALL_B)
        else:
            assert new.as_dict() == option.as_dict()


@pytest.mark.parametrize("options, match", [
    ({"a": {"plan": "sidestep", "to": "left", "towards": "a", "metres": 0.5}}, "not both"),
    ({"a": {"plan": "sidestep", "towards": "c", "metres": 0.5}}, "towards"),
    ({"a": {"plan": "sidestep", "towards": "a", "metres": 0.5}, "b": {"plan": "sidestep", "to": "left", "metres": 0.5}}, "some by left and right"),
])
def test_a_table_mixing_sides_and_walls_or_naming_no_wall_is_refused(tmp_path, options, match):
    path = tmp_path / "menu.yaml"
    path.write_text(json.dumps({"schema_version": 1, "type": "action_menu", "options": options}), encoding="utf-8")
    with pytest.raises(ConfigError, match=match):
        Menu.load(path)


def test_a_wall_table_needs_a_template_with_walls_and_a_template_with_walls_a_wall_table():
    data = copy.deepcopy(MENU_T.data)
    data["menu_table"], data["menu_options"] = TABLE, ABS_T.data["menu_options"]
    with pytest.raises(ConfigError, match="names no walls"):
        CoreTemplate("resolve_menu_v1", data, MENU_T.sha256).menu
    data = copy.deepcopy(ABS_T.data)
    data["menu_table"], data["menu_options"] = "configs/resolution/menu_table_v1.yaml", MENU_T.data["menu_options"]
    with pytest.raises(ConfigError, match="names moves by left and right"):
        CoreTemplate("resolve_menu_abs_v1", data, ABS_T.sha256).menu


@pytest.mark.parametrize("walls", [{"a": "x"}, {"a": "x", "b": "x"}, {"a": "x", "b": ""}])
def test_a_template_whose_walls_are_not_two_different_names_is_refused(walls):
    data = copy.deepcopy(ABS_T.data)
    data["walls"] = walls
    with pytest.raises(ConfigError, match="two different names"):
        CoreTemplate("resolve_menu_abs_v1", data, ABS_T.sha256)


# --- the conversion: a wall becomes the agent's own side now -------------------------------------


def test_a_move_towards_a_wall_is_turned_into_the_side_that_wall_is_on():
    for left_wall, blue_side in ((WALL_A, "left"), (WALL_B, "right")):
        yellow_side = "right" if blue_side == "left" else "left"
        assert parse_reply(choose("step a little towards the blue wall"), context(left_wall)).steps == (Step(sidestep=Sidestep(blue_side, 0.47)),)
        assert parse_reply(choose("step well towards the yellow wall"), context(left_wall)).steps == (Step(sidestep=Sidestep(yellow_side, 0.93)),)
    # The wall cap and its flags name the agent's own side, as under RF-47.
    parsed = parse_reply(choose("step well towards the blue wall"), context(WALL_B, room_left=1.0, room_right=0.8))
    assert parsed.steps == (Step(sidestep=Sidestep("right", 0.5)),) and parsed.flags == ("capped_by_wall:right",)
    assert parsed.action == "step well towards the blue wall"


def test_a_move_towards_a_wall_needs_the_wall_on_the_agents_left():
    with pytest.raises(ValueError, match="wall on the agent's left"):
        parse_reply(choose("step a little towards the blue wall"), context(None))


def test_an_own_side_option_is_not_on_the_walls_menu():
    with pytest.raises(Exception) as caught:
        parse_reply(choose("step a little to your right"), context(WALL_A))
    assert getattr(caught.value, "code", None) == "unknown_action"


def test_each_heading_has_the_wall_on_its_left_as_the_view_has_it():
    sim = simulation_for(source_plan(ALIGNED))
    a, b = ALIGNED["agents"]
    lefts = {agent: menu_context(sim, agent, frame=True)["left_wall"] for agent in (a, b)}
    assert lefts == {a: WALL_A, b: WALL_B}  # one walks +x (its left is +y), the other -x
    assert "left_wall" not in menu_context(sim, a)  # RF-47's context, as it was


# --- the acceptance criterion: for each heading, towards a wall is towards that wall ---------------


@pytest.mark.parametrize("case", [ALIGNED, APART], ids=["aligned", "apart_20cm"])
@pytest.mark.parametrize("wall, sign", [("blue", 1.0), ("yellow", -1.0)])
def test_for_each_heading_a_move_towards_a_wall_goes_towards_that_wall(case, wall, sign):
    for mover in case["agents"]:
        other = next(agent for agent in case["agents"] if agent != mover)
        sim = simulation_for(source_plan(case))
        start_y = sim.world.agents[mover].pose.xy[1]
        answers = {mover: [choose(f"step a little towards the {wall} wall")] * 6, other: [choose("stop and wait")] * 6}
        run, record, _ = session_on(case, "silent", answers, settings=TURN, core=ABS_T, first_asked=mover, simulation=sim)
        point = points_of(record, mover)[0]
        assert point["parsed"]["action"] == f"step a little towards the {wall} wall"
        moved = sim.world.agents[mover].pose.xy[1] - start_y
        assert sign * moved > 0.3, (mover, moved)  # wall a (blue) is at +y, whichever way the mover walks


def test_two_people_choosing_the_same_wall_head_for_the_same_side_of_the_corridor():
    # The expected trap of a shared frame (issue #137): each "towards the blue wall" is a different
    # own side (one left, one right), and both bodies move to +y.
    a, b = ALIGNED["agents"]
    sim = simulation_for(source_plan(ALIGNED))
    answers = {agent: [choose("step a little towards the blue wall")] * 6 for agent in (a, b)}
    run, record, _ = session_on(ALIGNED, "silent", answers, settings=TURN, core=ABS_T, first_asked=a, simulation=sim)
    sides = {agent: points_of(record, agent)[0]["coded"]["side"] for agent in (a, b)}
    assert sides == {a: "left", b: "right"}


# --- the view in the frame -------------------------------------------------------------------------


def test_the_view_gives_positions_and_moves_in_the_frame_and_never_a_side():
    run, record, _ = session_on(
        APART, "talk", {agent: [choose("step a little towards the yellow wall", message="", signal="none")] * 6 for agent in APART["agents"]},
        settings=TURN, core=ABS_T, first_asked=APART["agents"][0],
    )
    first = {agent: points_of(record, agent)[0] for agent in APART["agents"]}
    a, b = APART["agents"]
    fa, fb = first[a]["view"]["frame"], first[b]["view"]["frame"]
    assert (fa["left_wall"], fb["left_wall"]) == (WALL_A, WALL_B)
    for frame in (fa, fb):
        assert frame["from_a_m"] + frame["from_b_m"] == pytest.approx(1.75, abs=0.01)
    # What one is told of the other's place is what the other is told of its own (a paused exchange: one world state).
    assert first[a]["view"]["seen"][0]["from_a_m"] == pytest.approx(fb["from_a_m"], abs=0.005)
    assert first[b]["view"]["seen"][0]["from_a_m"] == pytest.approx(fa["from_a_m"], abs=0.005)
    for point in record["decision_points"]:
        user = point["prompt"]["messages"][1]["content"]
        assert not SIDE_WORDS.search(user), user
        assert f"- You are in a passage 1.75 m wide, between {BLUE} and {YELLOW}. You are " in user
        assert re.search(r"- Person 1, \d+\.\d m away, (ahead of|level with|behind) you, \d\.\d\d m from the blue wall[:.]", user), user


def frame_view(**overrides):
    person = SeenPerson(1, DETAIL_FULL, 6.0, 0.05, 1.3, math.radians(165), 2.6, 0.5, MOTION_WALKING, changes=("moved_left",), from_a_m=0.9)
    values = dict(
        agent_id=0, decision_point=2, me=Me(1.3, 1.3, 2.0, 0.5), place=("- A place line.",),
        templates={"core": ABS_T.identity(), "scenario": S.load_scenario("passing").identity()},
        seen=(person,), heard=(Heard("Hello.", None, "left", "close"),),
        history=(Done(1.0, "Move.", "completed", sideways_m=0.47, back_m=0.0, left_wall=WALL_B),),
        frame=Frame(WALL_B, 0.6, 1.15),
    )
    values.update(overrides)
    return View(**values)


def test_each_side_of_the_view_is_told_as_a_wall():
    text = ABS_T.description(frame_view())
    # The agent's left is the yellow wall here (it walks -x): a person drifting to its left, a move
    # over to its left, a voice from its left and its own move to the left are all towards yellow.
    assert "- Person 1, 6.0 m away, ahead of you, 0.90 m from the blue wall." in text
    assert "drifting towards the yellow wall by 15°" in text
    assert "Since you last looked, they have moved over towards the yellow wall." in text
    assert '- Someone towards the yellow wall from you, close by, says: "Hello."' in text
    assert "Since then you have moved 0.5 m over towards the yellow wall." in text
    assert not SIDE_WORDS.search(text)
    flipped = ABS_T.description(frame_view(
        frame=Frame(WALL_A, 0.6, 1.15), history=(Done(1.0, "Move.", "completed", sideways_m=-0.47, back_m=0.0, left_wall=WALL_A),),
    ))
    assert "drifting towards the blue wall" in flipped and "moved over towards the blue wall" in flipped
    assert "towards the blue wall from you" in flipped and "moved 0.5 m over towards the yellow wall" in flipped


@pytest.mark.parametrize("bearing_deg, words", [(30, "ahead of you"), (90, "level with you"), (-91, "level with you"), (150, "behind you")])
def test_where_someone_is_has_no_side_only_ahead_level_or_behind(bearing_deg, words):
    view = frame_view()
    person = view.seen[0].__class__(**{**view.seen[0].__dict__, "bearing_rad": math.radians(bearing_deg)})
    text = ABS_T.description(frame_view(seen=(person,)))
    assert f"{words}, 0.90 m from the blue wall" in text


def test_a_template_in_the_frame_refuses_a_view_without_one():
    with pytest.raises(ConfigError, match="has no frame"):
        ABS_T.description(frame_view(frame=None))


def test_the_cost_preview_builds_its_worst_view_in_the_frame():
    scenario = S.load_scenario("passing")
    view = E.worst_view(ABS_T, scenario, ALIGNED, 1, 1, 1, "the supermarket")
    text = ABS_T.description(view)
    assert view.frame is not None and "9.99 m from the blue wall" in text and "between the blue wall and the yellow wall" in text
    assert E.plan(E.ResolutionConfig.load(CONFIG)).preview["usd_total"] > 0


# --- earlier templates and records unchanged -------------------------------------------------------


def test_no_earlier_template_has_walls_and_a_view_without_a_frame_records_as_before():
    for key in [f"resolve_v{n}" for n in range(1, 10)] + ["resolve_menu_v1"]:
        assert CoreTemplate.load(key).walls is None
    described = frame_view(frame=None, seen=(replace_from_a(None),), history=(Done(1.0, "Move.", "completed", sideways_m=0.47, back_m=0.0),)).as_dict()
    assert "frame" not in described and "from_a_m" not in described["seen"][0] and "left_wall" not in described["history"][0]


def replace_from_a(value):
    person = frame_view().seen[0]
    return person.__class__(**{**person.__dict__, "from_a_m": value})


def test_rf47s_sessions_record_and_render_as_before():
    a, b = APART["agents"]
    run, record, _ = session_on(APART, "silent", {a: [choose("step a little to your left")] * 6, b: [choose("carry on")] * 6}, settings=TURN, core=MENU_T, first_asked=a)
    for point in record["decision_points"]:
        assert "frame" not in point["view"]
        assert all("from_a_m" not in person for person in point["view"]["seen"])
        assert all("left_wall" not in done for done in point["view"]["history"])
    scenario = S.load_scenario("passing")
    case, record_ = ALIGNED, ALIGNED["observations"][str(a)]
    assert scenario.place_lines(case, record_) == scenario.place_lines(case, record_, None)
    assert "The wall on your left" in scenario.place_lines(case, record_)[0]


# --- the template ----------------------------------------------------------------------------------


def test_the_template_is_rf47s_with_the_walls_in_place_of_left_and_right():
    assert ABS_T.exchange == "turn_taking" and not ABS_T.heard_frame and ABS_T.walls == {WALL_A: BLUE, WALL_B: YELLOW}
    for condition in ("independent", "non_verbal", "talk", "silent"):
        assert ABS_T.offers(condition)
    v, v1 = ABS_T.data["view"], MENU_T.data["view"]
    differ = {k for k in set(v) | set(v1) if v.get(k) != v1.get(k)}
    assert differ == {"heard_seen_facing", "heard_seen_same_way", "heard_directions", "history_sideways", "directions", "headings", "since_last_look"}
    assert {k: x for k, x in v["since_last_look"].items() if not k.startswith("moved_")} == {k: x for k, x in v1["since_last_look"].items() if not k.startswith("moved_")}
    assert ABS_T.data["decision_point"] == MENU_T.data["decision_point"] and ABS_T.data["role"] == MENU_T.data["role"]
    for condition in ("independent", "non_verbal", "talk", "silent"):
        old, new = MENU_T.data["conditions"][condition], ABS_T.data["conditions"][condition]
        assert new["reply_format"] == old["reply_format"] and new["retry"] == old["retry"]
        assert "Left and right always mean your own left and right." in old["instructions"]
        assert "Left and right" not in new["instructions"] and "the blue wall and the yellow wall" in new["instructions"]
    assert "name the wall" in ABS_T.data["conditions"]["talk"]["instructions"]


def test_the_fixed_text_names_no_own_side_and_no_number_and_nobody_first():
    for condition in ("silent", "talk"):
        system = ABS_T.system(condition, S.load_scenario("passing"))
        assert not SIDE_WORDS.search(system) and not re.search(r"\bleft and right\b", system, re.I)
        actions = system[system.index("\nACTIONS\n"):]
        for name in ABS.names:
            assert f'"{name}": ' in actions
        assert not re.search(r"\d", actions) and "degree" not in actions and "metre" not in actions
        assert not re.search(r"\b(first|go ahead|let them|priority|right of way|north|south|east|west)\b", actions, re.I)
    # The heading is not told: no compass word and no "walk east" anywhere in the template.
    text = json.dumps(ABS_T.data)
    assert not re.search(r"\b(north|south|east|west)(ward)?\b", text, re.I)


# --- the config and the mock -----------------------------------------------------------------------


def test_rf48s_config_is_rf47s_with_only_the_frame_template_changed():
    rf47, new = E.ResolutionConfig.load(RF47_CONFIG), E.ResolutionConfig.load(CONFIG)
    assert new.experiment_name == "rf48_round1_head_on_menu_abs" and new.conditions == rf47.conditions
    assert new.templates == {**rf47.templates, "core": "resolve_menu_abs_v1"}
    assert new.protocol == rf47.protocol and new.design == rf47.design and new.resolution_gate == rf47.resolution_gate
    assert new.llm == {**rf47.llm, "mock_policy": "resolution_menu_abs_rehearsal_v1"} and new.llm["client"] == "mock"
    assert load_yaml(resolve_path(CONFIG))["budget"]["cap_usd"] == 0.0


def test_the_frame_mock_covers_every_option_and_the_failure_paths():
    chosen = {normalise(json.loads(reply)["action"]) for reply in M.MENU_ABS_PATHS.values() if reply is not None}
    assert chosen >= set(ABS.names) and "step a little to your right" in chosen
    assert M.POLICIES["resolution_menu_rehearsal_v1"] is M.resolution_menu_rehearsal_v1  # RF-47's, as it was
