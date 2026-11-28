"""Issue #136 (RF-47): a menu of described actions, with amounts in words (``resolve_menu_v1``).

The user's decisions AS3 and AS4 of 2026-11-25 (``docs/action-space.md``, section 6): the agent
chooses one of nine options, each described in words with no number; code turns the option into
the existing step format by a table in config (``configs/resolution/menu_table_v1.yaml``), so the
executor, the replay and the analyses are reused; an option not on the menu is unreadable; and
every earlier template and config behaves exactly as before.
"""

from __future__ import annotations

import copy
import json
import re
import pytest

from negsim.configutil import ConfigError, load_yaml, resolve_path
from negsim.negotiation.parsing import TurnParseError
from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution import mock as M
from negsim.resolution import protocol as P
from negsim.resolution.menu import MIN_SIDESTEP_M, WALL_MARGIN_M, Menu, load_menu, normalise
from negsim.resolution.prompt import CoreTemplate, DebriefTemplate
from negsim.resolution.reply import ParsedReply, ReplyContext, Sidestep, Step, Until, parse_reply
from test_encounter_protocol import STORE, points_of, session_on

TABLE = "configs/resolution/menu_table_v1.yaml"
MENU_T = CoreTemplate.load("resolve_menu_v1")
MENU = load_menu(TABLE)
V9 = CoreTemplate.load("resolve_v9")
CONFIG = "configs/resolution/round1_head_on_menu.yaml"
RF40 = "configs/resolution/round1_head_on_turn_taking.yaml"
EVENTS = ("other_passes", "other_stops", "i_am_out_of_the_stretch")
TURN = P.ProtocolSettings(execution=X.EXECUTION_KEEP_LINE_REPLAN, max_decision_points=6, exchange=P.EXCHANGE_TURN_TAKING)
ALIGNED = STORE.get("head_on_de176842", 2)
APART = STORE.get("head_on_02dfbadb", 2)


def choose(action, **extra):
    return json.dumps({**extra, "intent": "Do this.", "action": action, "reason": "r"})


def context(room_left=None, room_right=None, condition="silent", usual=1.3, menu=MENU):
    return ReplyContext(condition, 2.0, EVENTS, 6.0, menu=menu, usual_speed_mps=usual, radius_m=0.25, room_left_m=room_left, room_right_m=room_right)


def fails(code, raw, ctx=None):
    with pytest.raises(TurnParseError) as caught:
        parse_reply(raw, ctx or context())
    assert caught.value.code == code, str(caught.value)


# --- the table: AS3's numbers ---------------------------------------------------------------------


def test_the_table_has_as3s_options_and_amounts_in_the_templates_order():
    assert MENU.names == tuple(MENU_T.data["menu_options"]) == MENU_T.menu.names
    by = {o.name: o for o in MENU.options}
    assert by["carry on"].kind == "carry_on"
    assert (by["slow down a little"].speed_factor, by["slow down a lot"].speed_factor) == (0.81, 0.5)
    assert by["slow down a little"].until == by["slow down a lot"].until == "other_passes"
    assert by["stop and wait"].seconds == 1.0
    for side in ("left", "right"):
        assert (by[f"step a little to your {side}"].to, by[f"step a little to your {side}"].metres) == (side, 0.47)
        assert (by[f"step well to your {side}"].to, by[f"step well to your {side}"].metres) == (side, 0.93)
    assert (by["step back"].kind, by["step back"].metres) == ("back_up", 0.5)


@pytest.mark.parametrize("bad, match", [
    ({"plan": "turn"}, "plan"),
    ({"plan": "slow", "speed_factor": 1.2, "until": "other_passes"}, "below 1"),
    ({"plan": "sidestep", "to": "up", "metres": 0.5}, "to"),
    ({"plan": "wait", "seconds": 1, "degrees": 3}, "unknown keys"),
    ({"plan": "back_up", "metres": -1}, "positive"),
])
def test_a_malformed_table_is_refused(tmp_path, bad, match):
    path = tmp_path / "menu.yaml"
    path.write_text(json.dumps({"schema_version": 1, "type": "action_menu", "options": {"an option": bad}}), encoding="utf-8")
    with pytest.raises(ConfigError, match=match):
        Menu.load(path)


def test_a_template_whose_options_differ_from_its_table_is_refused():
    data = copy.deepcopy(MENU_T.data)
    data["menu_options"] = dict(list(data["menu_options"].items())[1:])
    with pytest.raises(ConfigError, match="lists the options"):
        CoreTemplate("resolve_menu_v1", data, MENU_T.sha256).menu


@pytest.mark.parametrize("written", ["step well to your right", "Step Well To Your Right.", '  "step  well to your right" ', "STEP WELL TO YOUR RIGHT"])
def test_an_options_name_is_matched_ignoring_case_spaces_quotes_and_a_full_stop(written):
    assert normalise(written) == "step well to your right"
    assert MENU.find(written).name == "step well to your right"


# --- the reply ------------------------------------------------------------------------------------


def test_each_option_becomes_its_plan_in_the_step_format():
    expect = {
        "carry on": (),
        "slow down a little": (Step(speed_mps=1.05, until=Until(event="other_passes")),),  # 1.3 x 0.81
        "slow down a lot": (Step(speed_mps=0.65, until=Until(event="other_passes")),),
        "stop and wait": (Step(speed_mps=0.0, until=Until(seconds=1.0)),),
        "step a little to your left": (Step(sidestep=Sidestep("left", 0.47)),),
        "step a little to your right": (Step(sidestep=Sidestep("right", 0.47)),),
        "step well to your left": (Step(sidestep=Sidestep("left", 0.93)),),
        "step well to your right": (Step(sidestep=Sidestep("right", 0.93)),),
        "step back": (Step(back_up_m=0.5),),
    }
    assert tuple(expect) == MENU.names
    for name, steps in expect.items():
        parsed = parse_reply(choose(name), context())
        assert parsed.action == name and parsed.steps == steps and parsed.flags == ()
        assert parsed.as_dict()["action"] == name


def test_the_slower_speeds_are_of_the_agents_usual_speed():
    assert parse_reply(choose("slow down a little"), context(usual=1.0)).steps[0].speed_mps == 0.81
    assert parse_reply(choose("slow down a lot"), context(usual=0.7)).steps[0].speed_mps == 0.35


def test_an_option_not_on_the_menu_or_no_action_is_unreadable():
    fails("unknown_action", choose("step aside"))
    fails("unknown_action", choose("turn left 20 degrees"))
    fails("missing_action", json.dumps({"intent": "Walk on.", "steps": [], "reason": "r"}))
    fails("action_not_text", json.dumps({"intent": "Walk on.", "action": 3, "reason": "r"}))
    fails("missing_intent", json.dumps({"action": "carry on", "reason": "r"}))


def test_steps_beside_an_action_are_ignored_and_flagged():
    parsed = parse_reply(json.dumps({"intent": "i", "action": "carry on", "steps": [{"speed_mps": 9, "until": "now"}], "reason": "r"}), context())
    assert parsed.steps == () and "steps_ignored" in parsed.flags


def test_signal_and_message_follow_the_condition_as_before():
    raw = choose("stop and wait", signal="wave_on", message="After you.")
    talk = parse_reply(raw, context(condition="talk"))
    assert (talk.signal, talk.message) == ("wave_on", "After you.")
    silent = parse_reply(raw, context(condition="silent"))
    assert (silent.signal, silent.message) == ("none", "") and {"signal_ignored", "message_ignored"} <= set(silent.flags)


def test_a_sidestep_goes_no_further_than_the_wall_allows():
    # 0.875 m from the centre to the right wall (an aligned start in round 1's 1.75 m corridor):
    # the body's centre can go 0.875 - 0.25 = 0.625 m, less the margin.
    capped = parse_reply(choose("step well to your right"), context(room_right=0.875))
    assert capped.steps == (Step(sidestep=Sidestep("right", round(0.875 - 0.25 - WALL_MARGIN_M, 2))),)
    assert capped.flags == ("capped_by_wall:right",)
    # "a little" fits, and the other side's wall does not matter.
    assert parse_reply(choose("step a little to your right"), context(room_left=0.3, room_right=0.875)).flags == ()
    # With no room left, no sidestep: the plan is carry on, flagged.
    tight = parse_reply(choose("step a little to your left"), context(room_left=0.25 + WALL_MARGIN_M + MIN_SIDESTEP_M / 2))
    assert tight.steps == () and tight.flags == ("no_room:left",)
    # No wall in range on that side: nothing is capped.
    assert parse_reply(choose("step well to your left"), context()).steps == (Step(sidestep=Sidestep("left", 0.93)),)


def test_a_menu_option_must_end_at_an_event_of_the_scenario():
    narrow = ReplyContext("silent", 2.0, ("i_am_out_of_the_stretch",), 6.0, menu=MENU, usual_speed_mps=1.3)
    with pytest.raises(ValueError, match="not an event of this scenario"):
        parse_reply(choose("slow down a little"), narrow)


# --- earlier templates and records unchanged (AS4) -------------------------------------------------


def test_no_earlier_template_has_a_menu_and_their_replies_read_as_before():
    for n in range(1, 10):
        assert CoreTemplate.load(f"resolve_v{n}").menu is None
    raw = json.dumps({"intent": "Walk on.", "action": "step back", "steps": [{"speed_mps": 1.0, "until": {"seconds": 1}}], "reason": "r"})
    parsed = parse_reply(raw, ReplyContext("silent", 2.0, EVENTS, 6.0))
    assert parsed.action is None and parsed.steps == (Step(speed_mps=1.0, until=Until(seconds=1.0)),)
    assert "action" not in parsed.as_dict()
    assert list(parsed.as_dict()) == ["condition", "message", "signal", "intent", "steps", "reason", "flags"]


def test_the_debrief_names_the_option_under_v3_and_lists_steps_otherwise():
    chosen = ParsedReply("silent", "", "none", "Move right.", (Step(sidestep=Sidestep("right", 0.47)),), "r", (), "step a little to your right")
    free = ParsedReply("silent", "", "none", "Move right.", (Step(sidestep=Sidestep("right", 0.47)),), "r")
    v2, v3 = DebriefTemplate.load("resolve_debrief_v2"), DebriefTemplate.load("resolve_debrief_v3")
    text = v3.text([chosen])
    assert 'You chose: "step a little to your right".' in text and "metres" not in text
    assert v3.text([free]) == v2.text([free])  # a decision with steps reads as under v2
    assert '"metres": 0.47' in v2.text([chosen])  # v2 knows no action line: as before
    assert v3.side_question and v3.data["text"] == v2.data["text"] and v3.data["reply_format"] == v2.data["reply_format"]


# --- the template ----------------------------------------------------------------------------------


def test_the_template_is_v9_with_the_menu_in_place_of_the_step_format():
    assert MENU_T.exchange == "turn_taking" and MENU_T.heard_frame
    for condition in ("independent", "non_verbal", "talk", "silent"):
        assert MENU_T.offers(condition)
    assert MENU_T.data["view"]["seen_full"] == V9.data["view"]["seen_full"]
    differ = {k for k in V9.data["view"] if MENU_T.data["view"].get(k) != V9.data["view"][k]}
    assert differ == {"history_outcome"}
    assert MENU_T.data["role"] == V9.data["role"] and MENU_T.data["decision_point"]["opening"] == V9.data["decision_point"]["opening"]


def test_the_actions_block_names_every_option_with_no_number_or_angle_and_nobody_first():
    from negsim.resolution import scenarios as S

    system = MENU_T.system("silent", S.load_scenario("passing"))
    actions = system[system.index("\nACTIONS\n"):]
    for name in MENU.names:
        assert f'"{name}": ' in actions
    assert not re.search(r"\d", actions) and "degree" not in actions and "metre" not in actions
    assert not re.search(r"\b(first|go ahead|let them|priority|right of way)\b", actions, re.I)
    assert "STEPS" not in system and '"steps"' not in system and '"action"' in system


# --- in a session: each option moves as planned, in plan_only --------------------------------------


def run_with(case, a_choices, b_choices=("carry on",), condition="silent"):
    a, b = case["agents"]
    answers = {a: [choose(c) for c in a_choices], b: [choose(c) for c in b_choices]}
    run, record, client = session_on(case, condition, answers, settings=TURN, core=MENU_T, first_asked=a)
    return run, record, a, b


def first_plan(run, agent):
    return next(plan for plan in run.run.driver.decisions if plan.agent_id == agent and plan.decision_point == 1)


def test_step_well_to_your_right_ends_at_the_wall_and_keeps_that_line():
    run, record, a, _ = run_with(ALIGNED, ["step well to your right"] * 6)
    point = points_of(record, a)[0]
    assert point["parsed"]["action"] == "step well to your right" and point["parsed"]["flags"] == ["capped_by_wall:right"]
    metres = point["plan_given"][0]["sidestep"]["metres"]
    assert 0.5 < metres < 0.625  # AS3: about 0.6 m from an aligned start in round 1's corridor
    step = first_plan(run, a).records[0]
    assert step.ended_by == X.ENDED_SIDESTEPPED and step.aside_m == pytest.approx(metres, abs=0.02)


def test_step_a_little_and_the_others_movements_in_plan_only():
    run, record, a, b = run_with(APART, ["step a little to your left"] * 6, ["step a little to your right"] * 6)
    for agent, side in ((a, "left"), (b, "right")):
        step = first_plan(run, agent).records[0]
        assert step.ended_by == X.ENDED_SIDESTEPPED and step.aside_m == pytest.approx(0.47, abs=0.02)
        assert points_of(record, agent)[0]["coded"]["side"] == side
    run, record, a, _ = run_with(ALIGNED, ["step back"])
    assert first_plan(run, a).records[0].ended_by == X.ENDED_BACKED_UP
    run, record, a, _ = run_with(ALIGNED, ["stop and wait"])
    assert first_plan(run, a).records[0].ended_by == X.ENDED_SECONDS
    assert len(points_of(record, a)) >= 2  # asked again after the wait, the meeting still predicted
    run, record, a, _ = run_with(ALIGNED, ["slow down a little"])
    point = points_of(record, a)[0]
    assert point["coded"]["slowed"] and point["plan_given"][0]["until"] == "other_passes"
    run, record, a, _ = run_with(ALIGNED, ["carry on"])
    assert points_of(record, a)[0]["plan_given"] == [] and points_of(record, a)[0]["coded"]["carry_on"]


def test_an_unknown_option_gets_one_retry_and_is_then_counted_unreadable():
    run, record, a, _ = run_with(ALIGNED, ["step aside"] * 6)
    point = points_of(record, a)[0]
    assert len(point["attempts"]) == 2 and str(point["parse_error"]).startswith("unknown_action") and point["parsed"] is None


# --- the config and the mock -----------------------------------------------------------------------


def raw(path):
    return copy.deepcopy(load_yaml(resolve_path(path)))


def test_rf47s_config_is_rf40s_sessions_with_only_the_menu_templates_changed():
    rf40, new = E.ResolutionConfig.load(RF40), E.ResolutionConfig.load(CONFIG)
    assert new.experiment_name == "rf47_round1_head_on_menu"
    assert new.conditions == ("silent", "talk")
    assert new.templates == {**rf40.templates, "core": "resolve_menu_v1", "debrief": "resolve_debrief_v3"}
    assert new.protocol == rf40.protocol and new.design == rf40.design and new.resolution_gate == rf40.resolution_gate
    assert new.llm == {**rf40.llm, "mock_policy": "resolution_menu_rehearsal_v1"} and new.llm["client"] == "mock"


def test_the_menu_mock_covers_every_option_and_the_failure_paths():
    chosen = {json.loads(reply)["action"] for reply in M.MENU_PATHS.values() if reply is not None}
    assert {normalise(name) for name in chosen} >= set(MENU.names) and "step aside" in chosen
    assert M.POLICIES["resolution_rehearsal_v1"] is M.resolution_rehearsal_v1  # the earlier policy, as it was
