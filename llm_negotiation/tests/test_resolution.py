"""Issue #57 (RF-2): the Step 1 templates, the View, the scenario interface, the reply and debrief
parsers, and the mock policies (``docs/resolution.md``, D1 to D3, D8, D16)."""

from __future__ import annotations

import copy
import dataclasses
import json
import math
import re

import pytest

from negsim.configutil import ConfigError
from negsim.llm.mock import MockClient
from negsim.negotiation import prompts
from negsim.negotiation.parsing import TurnParseError
from negsim.negotiation.prompts import TemplateIntegrityError
from negsim.negotiation.protocol import request_with_retry
from negsim.personas.groups import DEFAULT_GROUP_LABELS
from negsim.resolution import adapter, mock
from negsim.resolution.prompt import CoreTemplate, DebriefTemplate, debrief_messages, render
from negsim.resolution.reply import (
    DEBRIEF_KINDS, ReplyContext, parse_debrief, parse_reply, reply_parser,
)
from negsim.resolution.scenario import Scenario
from negsim.resolution.scenarios import PLUGINS, PassingCrowdScenario, PassingGroupScenario, PassingScenario, load_scenario
from negsim.resolution.view import CHANGES, CONDITIONS, SIGNALS, Block, Done, Heard
from negsim.rulegen.cases import CASE_FILE, CASES_ROOT, CaseStore

CORE = CoreTemplate.load()
DEBRIEF = DebriefTemplate.load()
PASSING = load_scenario("passing")
STORE = CaseStore(CASES_ROOT)
ALL_CASES = [STORE.get(m["case_id"], int(m["version"])) for m in (CASE_FILE.match(name) for name in sorted(STORE.manifest()["files"]))]
PAIRS = [case for case in ALL_CASES if case["scenario"]["n_agents"] == 2]
CROWDS = [case for case in ALL_CASES if case["scenario"]["n_agents"] != 2]
PEOPLE = {
    0: {"age": 34, "gender": "female", "errand": "the post office"},
    1: {"age": 71, "gender": "male", "errand": "a secret appointment"},
}

#: Words that would hint at a way of settling a meeting: issue #32's list (test_rulegen_prompts_v2).
SUGGESTIONS = (
    "keep left", "keep right", "keep to the", "to the left", "to the right", "give way", "giving way", "right of way",
    "yield", "courtesy", "polite", "elder", "seniority", "convention", "custom", "should go", "ought", "fair", "etiquette",
    "first come", "ladies", "respect", "shorter", "less far", "further in",
)
#: D2: never "usually", nothing saying someone has to go first, no reply field about it.
ORDER_WORDS = ("first", "priority", "usually", "go before", "goes before", "has to go", "must go")
GROUP_WORDS = (*DEFAULT_GROUP_LABELS, "ethnic", "belong", "community", "eastbound", "westbound", "group")


def view_of(case, agent=None, **kwargs):
    agent = case["agents"][0] if agent is None else agent
    people = {case["agents"][0]: PEOPLE[0], case["agents"][1]: PEOPLE[1]}
    return adapter.opening_view(case, agent, PASSING, CORE, people=people, **kwargs)


def full_view(case, agent=None):
    """A later decision point with every block of D2 filled, as RF-17 and RF-3 will fill them."""
    view = view_of(case, agent)
    seen = view.seen
    if seen:
        seen = (dataclasses.replace(seen[0], signal="wave_on", changes=CHANGES),)
    return dataclasses.replace(
        view, decision_point=2, seen=seen, notes=("A note about an earlier day.",),
        heard=(Heard("Sorry!", 1 if seen else None), Heard("Excuse me.")),
        history=(Done(1.4, "Move over a little.", "ongoing", message="Hello.", signal="nod"), Done(0.4, "Wait.", "completed")),
    )


def every_prompt():
    for case in PAIRS:
        for agent in case["agents"]:
            for condition in CONDITIONS:
                yield case, agent, condition, render(view_of(case, agent), condition, PASSING, CORE)
                yield case, agent, condition, render(full_view(case, agent), condition, PASSING, CORE)


# --- frozen templates ------------------------------------------------------------------------------


def test_the_three_templates_are_frozen_with_their_kinds():
    manifest = prompts.load_manifest()
    assert manifest["resolve_v1"]["kind"] == "resolution"
    assert manifest["resolve_debrief_v1"]["kind"] == "resolution_debrief"
    assert manifest["scenario_passing_v1"]["kind"] == "resolution_scenario"
    assert CORE.sha256 == manifest["resolve_v1"]["sha256"] and PASSING.sha256 == manifest["scenario_passing_v1"]["sha256"]
    assert DEBRIEF.sha256 == manifest["resolve_debrief_v1"]["sha256"]
    assert not {"resolve_v1", "resolve_debrief_v1", "scenario_passing_v1"} & set(prompts.available_templates())


def test_an_edited_template_is_refused(tmp_path, monkeypatch):
    import shutil

    copy_dir = tmp_path / "templates"
    shutil.copytree(prompts.TEMPLATE_DIR, copy_dir)
    monkeypatch.setattr(prompts, "TEMPLATE_DIR", copy_dir)
    path = copy_dir / "resolve_v1.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("Decide as this person would.", "Decide."), encoding="utf-8")
    with pytest.raises(TemplateIntegrityError):
        CoreTemplate.load()


def test_the_core_template_names_no_scenario():
    """D16: nothing specific to one scenario in the core template."""
    text = (prompts.TEMPLATE_DIR / "resolve_v1.yaml").read_text(encoding="utf-8")
    for name in (*PASSING.events, "passage", "corridor", "narrow", "stretch", "queue", "wall"):
        assert name not in text, name


# --- rendering ---------------------------------------------------------------------------------------


def test_every_case_renders_in_every_condition_with_every_placeholder_filled():
    assert len(PAIRS) == 28 + 8 and len(CROWDS) == 16 + 4  # every file of cases/: 28 of two people (and issue #60's 8 passage cases), 16 out of crowds (and issue #110's 4 out of groups)
    count = 0
    for case, agent, condition, rendered in every_prompt():
        assert [m["role"] for m in rendered.messages] == ["system", "user"]
        for message in rendered.messages:
            assert not re.search(r"\{[a-z_]+\}", message["content"]), (case["case_id"], message["content"])
        assert rendered.templates == {"core": CORE.identity(), "scenario": PASSING.identity()}
        assert rendered.as_dict()["templates"] == rendered.templates
        count += 1
    assert count == len(PAIRS) * 2 * len(CONDITIONS) * 2


def test_crowd_cases_are_refused_until_rf17():
    for case in CROWDS:
        with pytest.raises(ConfigError, match="two-person"):
            view_of(case)


def test_the_order_is_fixed_text_then_description_then_wrapper():
    case = STORE.get("passage_25f09e61")
    rendered = render(view_of(case), "talk", PASSING, CORE)
    system = rendered.system
    assert system.index("You are playing") < system.index("HOW TO REPLY") < system.index("STEPS")
    user = rendered.user
    order = ["ABOUT YOU", "WHERE YOU ARE", "WHO YOU CAN SEE", "At your current speeds", "What do you do now?"]
    assert [user.index(word) for word in order] == sorted(user.index(word) for word in order)
    later = render(full_view(case), "talk", PASSING, CORE).user
    order = ["ABOUT YOU", "YOUR NOTES", "WHERE YOU ARE", "WHO YOU CAN SEE", "WHAT YOU CAN HEAR", "WHAT YOU HAVE DONE SO FAR", "At your current speeds", "Something has changed"]
    assert [later.index(word) for word in order] == sorted(later.index(word) for word in order)


def test_the_fixed_text_is_byte_identical_across_agents_and_decision_points():
    """The prefix the provider's cache reuses: one system message per condition and scenario."""
    systems = {condition: set() for condition in CONDITIONS}
    for _, _, condition, rendered in every_prompt():
        systems[condition].add(rendered.system)
    assert all(len(texts) == 1 for texts in systems.values())
    assert len({next(iter(texts)) for texts in systems.values()}) == 3  # and the conditions differ


def test_the_conditions_ask_for_what_they_allow():
    independent, non_verbal, talk = (CORE.system(c, PASSING) for c in CONDITIONS)
    assert '"message"' not in independent and '"signal"' not in independent
    assert '"message"' not in non_verbal and '"signal"' in non_verbal
    assert '"message"' in talk and '"signal"' in talk
    for text in (independent, non_verbal, talk):
        assert "intent" in text and "Nobody else knows your intent or your reason." in text
        assert text.index('"intent"') < text.index('"steps"') < text.index('"reason"')  # D1: intent before steps, reason last
    assert "hearing range" in talk and "hearing range" not in non_verbal
    for signal in SIGNALS:
        assert f'"{signal}"' in non_verbal and f'"{signal}"' in talk


def test_the_scenario_events_are_listed_in_the_step_format():
    for condition in CONDITIONS:
        text = CORE.system(condition, PASSING)
        for name, words in PASSING.events.items():
            assert f'"{name}" ({words})' in text


def test_a_view_rendered_with_other_templates_is_refused():
    view = view_of(STORE.get("passage_25f09e61"))
    wrong = dataclasses.replace(view, templates={"core": {"key": "resolve_v1", "sha256": "0" * 64}, "scenario": PASSING.identity()})
    with pytest.raises(ConfigError, match="was built for templates"):
        render(wrong, "talk", PASSING, CORE)


# --- what the agent can perceive -----------------------------------------------------------------------


def test_nothing_the_agent_cannot_perceive_appears():
    for case, agent, condition, rendered in every_prompt():
        text = (rendered.system + "\n" + rendered.user).lower()
        mine, theirs = ("the post office", "a secret appointment") if agent == case["agents"][0] else ("a secret appointment", "the post office")
        assert mine in text and theirs not in text  # one's own errand is told, the other's never
        assert text.count("usual walking speed") == 1  # one's own, never the other's
        for word in GROUP_WORDS:
            assert word.lower() not in text, word


def test_the_view_cone_and_ranges_of_d2():
    head_on = STORE.get("head_on_02dfbadb", 2)  # 12.4 m apart: beyond the 10 m seeing range
    assert view_of(head_on).seen == () and "You do not see anyone nearby." in render(view_of(head_on), "talk", PASSING, CORE).user
    overtaking = STORE.get("overtaking_23c5d31e", 2)  # the one behind sees the one ahead; not the other way round
    assert len(view_of(overtaking, 0).seen) == 1 and view_of(overtaking, 1).seen == ()
    passage = STORE.get("passage_25f09e61")
    (person,) = view_of(passage).seen
    assert person.detail == "full" and person.label == 1
    near = copy.deepcopy(head_on)
    record = near["observations"]["0"]
    record["distance_m"], record["relative_position_m"] = 7.2, [7.2, -0.2]
    (person,) = view_of(near).seen
    assert person.detail == "short"
    user = render(view_of(near), "independent", PASSING, CORE).user
    assert "- Person 1, 7.2 m away, straight ahead of you: walking in the opposite direction to you." in user
    assert "Their body" not in user and "They look" not in user  # one short line beyond 5 m
    record["bearing_rad"] = math.radians(76)
    assert view_of(near).seen == ()


def test_the_time_to_meet_is_the_time_of_closest_approach():
    record = STORE.get("head_on_02dfbadb", 2)["observations"]["0"]
    assert adapter.time_to_meet(record) == pytest.approx(12.360001 * 2.599958 / (2.599958**2 + 0.000104**2), rel=1e-6)
    away = {**record, "relative_velocity_mps": [2.6, 0.0]}
    assert adapter.time_to_meet(away) is None
    view = view_of(STORE.get("overtaking_23c5d31e", 2), 0)
    assert view.time_to_meet.label == 1 and "you would meet Person 1 in about 10.5 s." in render(view, "talk", PASSING, CORE).user


def test_the_visibility_switches_hide_age_and_gender_for_both():
    case = STORE.get("passage_25f09e61")
    shown = render(view_of(case), "talk", PASSING, CORE).user
    assert "34 years old" in shown and "about 71 years old" in shown and "a woman" in shown and "a man" in shown
    hidden = render(view_of(case, show_age=False, show_gender=False), "talk", PASSING, CORE).user
    assert "years old" not in hidden and "woman" not in hidden and "a man" not in hidden


def test_an_unknown_person_key_is_refused():
    case = STORE.get("passage_25f09e61")
    with pytest.raises(ConfigError, match="unknown key"):
        adapter.opening_view(case, 0, PASSING, CORE, people={0: {"group": "x"}})


# --- neutral wording -----------------------------------------------------------------------------------


def test_no_convention_and_no_order_wording_in_anything_an_agent_is_shown():
    texts = [CORE.retry(c) for c in CONDITIONS] + [CORE.data["decision_point"]["opening"], CORE.data["decision_point"]["again"]]
    texts += [rendered.system + "\n" + rendered.user for *_, rendered in every_prompt()]
    for text in texts:
        lowered = text.lower()
        for phrase in SUGGESTIONS + ORDER_WORDS:
            assert phrase not in lowered, phrase
        assert "{name}" not in lowered


def test_the_debrief_never_asks_who_went_first():
    """The debrief names "a local custom" (D8, word for word), so issue #32's list does not apply to it."""
    reply = parse_reply(mock.RESOLVE_PATHS["swerve_left"], ReplyContext("talk", 2.0, tuple(PASSING.events), 5.0))
    text = DEBRIEF.text([reply]).lower() + DEBRIEF.retry().lower()
    for phrase in ("first", "priority", "go before", "goes before"):
        assert phrase not in text
    assert "that is a perfectly good answer." in text and '"none"' in text


# --- the reply parser -----------------------------------------------------------------------------------

CONTEXT = ReplyContext("talk", 1.5, tuple(PASSING.events), 6.0)


def reply(**fields):
    base = {"message": "", "signal": "none", "intent": "Walk on.", "steps": [], "reason": "Why not."}
    base.update(fields)
    return json.dumps({k: v for k, v in base.items() if v is not ...})


def fails(code, raw, context=CONTEXT):
    with pytest.raises(TurnParseError) as caught:
        parse_reply(raw, context)
    assert caught.value.code == code, str(caught.value)


def test_a_full_reply_reads_as_d1_shows_it():
    raw = reply(
        message="Excuse me, I'll keep to this side.", signal="eye_contact",
        intent="Move over to my left a little early and keep walking at a steady pace.",
        steps=[{"start": {"at_distance_m": 6}, "turn": {"to": "left", "degrees": 10}, "speed_mps": 1.1, "until": {"seconds": 2}},
               {"speed_mps": 1.1, "until": "other_passes"}],
        reason="There's a wall close on my right.",
    )
    parsed = parse_reply(raw, CONTEXT)
    assert parsed.message.startswith("Excuse me") and parsed.signal == "eye_contact" and parsed.flags == ()
    first, second = parsed.steps
    assert first.start.kind == "at_distance_m" and first.start.value == 6.0 and first.turn.to == "left" and first.turn.degrees == 10.0
    assert second.until.event == "other_passes" and second.start is None
    assert parsed.as_dict()["steps"][0] == {"start": {"at_distance_m": 6.0}, "speed_mps": 1.1, "turn": {"to": "left", "degrees": 10.0}, "until": {"seconds": 2.0}}
    assert "priority" not in parsed.as_dict()


def test_tolerances_whitespace_a_code_fence_extra_keys_and_case():
    raw = "\n  ```json\n" + reply(signal=" NOD ", extra="x", steps=[{"until": "Other_Passes", "speed_mps": 1}]) + "\n```  \n"
    parsed = parse_reply(raw, CONTEXT)
    assert parsed.signal == "nod" and parsed.steps[0].until.event == "other_passes"
    parsed = parse_reply(reply(steps=[{"until": {"seconds": 1}, "side": "left"}]), CONTEXT)
    assert parsed.flags == ("unknown_step_key:steps[0].side",)


def test_defaults_and_carry_on():
    parsed = parse_reply(json.dumps({"intent": "Carry on.", "steps": []}), CONTEXT)
    assert parsed.signal == "none" and parsed.message == "" and parsed.steps == () and parsed.reason == ""
    assert parsed.flags == ("no_reason",)
    fails("missing_steps", json.dumps({"intent": "Carry on.", "reason": "x"}))


@pytest.mark.parametrize(
    "code, raw",
    [
        ("empty_output", "  "),
        ("not_json", "Sure! {intent: go"),
        ("not_an_object", "[1, 2]"),
        ("missing_intent", json.dumps({"steps": []})),
        ("empty_intent", reply(intent="  ")),
        ("intent_not_text", reply(intent=3)),
        ("steps_not_a_list", reply(steps={"until": "other_passes"})),
        ("step_not_an_object", reply(steps=["walk"])),
        ("unknown_signal", reply(signal="salute")),
        ("message_not_text", reply(message=["hi"])),
        ("start_on_later_step", reply(steps=[{"until": {"seconds": 1}}, {"start": "now", "until": {"seconds": 1}}])),
        ("unknown_start", reply(steps=[{"start": "soon", "until": {"seconds": 1}}])),
        ("unknown_start", reply(steps=[{"start": {"at_time": 3}, "until": {"seconds": 1}}])),
        ("start_at_distance_beyond_current", reply(steps=[{"start": {"at_distance_m": 6.5}, "until": {"seconds": 1}}])),
        ("start_at_distance_not_positive", reply(steps=[{"start": {"at_distance_m": 0}, "until": {"seconds": 1}}])),
        ("start_after_seconds_negative", reply(steps=[{"start": {"after_seconds": -1}, "until": {"seconds": 1}}])),
        ("start_not_a_number", reply(steps=[{"start": {"after_seconds": "2"}, "until": {"seconds": 1}}])),
        ("speed_out_of_range", reply(steps=[{"speed_mps": 1.51, "until": {"seconds": 1}}])),
        ("speed_out_of_range", reply(steps=[{"speed_mps": -0.1, "until": {"seconds": 1}}])),
        ("speed_not_a_number", reply(steps=[{"speed_mps": True, "until": {"seconds": 1}}])),
        ("unknown_turn_side", reply(steps=[{"turn": {"to": "up", "degrees": 10}, "until": {"seconds": 1}}])),
        ("unknown_turn", reply(steps=[{"turn": "left", "until": {"seconds": 1}}])),
        ("turn_degrees_out_of_range", reply(steps=[{"turn": {"to": "left", "degrees": 91}, "until": {"seconds": 1}}])),
        ("turn_degrees_out_of_range", reply(steps=[{"turn": {"to": "left", "degrees": -5}, "until": {"seconds": 1}}])),
        ("back_up_not_positive", reply(steps=[{"back_up_m": 0}])),
        ("back_up_not_positive", reply(steps=[{"back_up_m": -1}])),
        ("until_seconds_not_positive", reply(steps=[{"until": {"seconds": 0}}])),
        ("unknown_event", reply(steps=[{"until": "other_waves"}])),
        ("unknown_until", reply(steps=[{"until": {"minutes": 1}}])),
        ("missing_until", reply(steps=[{"speed_mps": 1.0}])),
        ("reason_not_text", reply(reason=42)),
    ],
)
def test_every_parse_failure_has_its_code(code, raw):
    fails(code, raw)


def test_limits_are_inclusive_and_read_from_the_context():
    parse_reply(reply(steps=[{"speed_mps": 1.5, "turn": {"to": "right", "degrees": 90}, "until": {"seconds": 0.1}}]), CONTEXT)
    parse_reply(reply(steps=[{"start": {"at_distance_m": 6.0}, "speed_mps": 0, "until": "other_stops"}]), CONTEXT)
    fails("speed_out_of_range", reply(steps=[{"speed_mps": 1.5, "until": {"seconds": 1}}]), ReplyContext("talk", 1.4, tuple(PASSING.events), 6.0))
    fails("start_at_distance_with_nobody_in_view", reply(steps=[{"start": {"at_distance_m": 3}, "until": {"seconds": 1}}]), ReplyContext("talk", 1.5, tuple(PASSING.events)))


def test_a_back_up_step_ends_by_its_distance_and_ignores_speed_and_turn():
    parsed = parse_reply(reply(steps=[{"back_up_m": 1.0, "speed_mps": 1.0, "turn": {"to": "left", "degrees": 5}}, {"speed_mps": 0, "until": "other_passes"}]), CONTEXT)
    step = parsed.steps[0]
    assert step.back_up_m == 1.0 and step.speed_mps is None and step.turn is None and step.until is None
    assert parsed.flags == ("speed_ignored_on_back_up:steps[0]", "turn_ignored_on_back_up:steps[0]")


def test_a_message_or_signal_a_condition_does_not_allow_is_ignored_and_flagged():
    raw = reply(message="Hello there", signal="wave_on")
    independent = parse_reply(raw, dataclasses.replace(CONTEXT, condition="independent"))
    assert independent.message == "" and independent.signal == "none" and independent.flags == ("message_ignored", "signal_ignored")
    non_verbal = parse_reply(raw, dataclasses.replace(CONTEXT, condition="non_verbal"))
    assert non_verbal.message == "" and non_verbal.signal == "wave_on" and non_verbal.flags == ("message_ignored",)
    talk = parse_reply(raw, CONTEXT)
    assert talk.message == "Hello there" and talk.signal == "wave_on" and talk.flags == ()
    quiet = parse_reply(reply(message="", signal="none"), dataclasses.replace(CONTEXT, condition="independent"))
    assert quiet.flags == ()  # an empty message and "none" are not something said or signalled
    odd = parse_reply(reply(message=["hi"], signal=7), dataclasses.replace(CONTEXT, condition="independent"))
    assert odd.flags == ("message_ignored", "signal_ignored")  # ignored, whatever it is


def test_the_context_comes_from_the_view():
    view = view_of(STORE.get("overtaking_23c5d31e", 2), 0)
    context = ReplyContext.of(view, "talk", PASSING.events)
    assert context.max_speed_mps == 2.0 and context.distance_m == pytest.approx(4.0, abs=0.1)
    assert context.events == ("other_passes", "other_stops", "i_am_out_of_the_stretch")
    assert ReplyContext.of(view_of(STORE.get("overtaking_23c5d31e", 2), 1), "talk", PASSING.events).distance_m is None


# --- the debrief ----------------------------------------------------------------------------------------


def test_the_debrief_parser():
    with_source = parse_debrief(mock.DEBRIEF_PATHS["with_source"])
    assert with_source.kind == "law_or_guidance" and with_source.source == "A mock citation, 2020." and with_source.source_status == "unchecked"
    none = parse_debrief(mock.DEBRIEF_PATHS["none"])
    assert none.kind == "none" and none.source is None and none.source_status == "unchecked" and none.flags == ()
    assert parse_debrief(json.dumps({"basis": "x", "kind": " Habit ", "source": None, "applies_to": "all"})).source is None
    flagged = parse_debrief(json.dumps({"basis": "x", "kind": "none", "source": "A book", "applies_to": "all"}))
    assert flagged.flags == ("source_but_kind_none",)
    assert set(DEBRIEF_KINDS) == {"law_or_guidance", "published_study", "local_custom", "habit", "common_sense", "none"}


@pytest.mark.parametrize(
    "code, data",
    [
        ("missing_basis", {"kind": "none", "source": "none", "applies_to": "x"}),
        ("empty_basis", {"basis": " ", "kind": "none", "source": "none", "applies_to": "x"}),
        ("missing_kind", {"basis": "x", "source": "none", "applies_to": "x"}),
        ("unknown_kind", {"basis": "x", "kind": "instinct", "source": "none", "applies_to": "x"}),
        ("missing_source", {"basis": "x", "kind": "none", "applies_to": "x"}),
        ("missing_applies_to", {"basis": "x", "kind": "none", "source": "none"}),
        ("source_not_text", {"basis": "x", "kind": "none", "source": 3, "applies_to": "x"}),
    ],
)
def test_every_debrief_failure_has_its_code(code, data):
    with pytest.raises(TurnParseError) as caught:
        parse_debrief(json.dumps(data))
    assert caught.value.code == code


def test_the_debrief_follows_the_last_decision_point():
    case = STORE.get("passage_25f09e61")
    last = render(full_view(case), "talk", PASSING, CORE)
    context = ReplyContext.of(full_view(case), "talk", PASSING.events)
    decisions = [parse_reply(mock.RESOLVE_PATHS["talk_message"], context), parse_reply(mock.RESOLVE_PATHS["back_up_then_wait"], context)]
    messages, templates = debrief_messages(last, mock.RESOLVE_PATHS["back_up_then_wait"], decisions, DEBRIEF)
    assert messages[:2] == [dict(m) for m in last.messages]  # the same prefix: the cache reuses it
    assert messages[2] == {"role": "assistant", "content": mock.RESOLVE_PATHS["back_up_then_wait"]}
    question = messages[3]["content"]
    assert question.startswith("Stepping out of the role now. Earlier, as this person, you:")
    assert '- decided: "Tell them and carry on."' in question and "Your steps were: none, you carried on as you were." in question
    assert 'You said: "Excuse me."' in question and '"back_up_m": 1.0' in question
    assert templates == {"core": CORE.identity(), "scenario": PASSING.identity(), "debrief": DEBRIEF.identity()}
    with pytest.raises(ValueError):
        DEBRIEF.text([])


def test_agent_words_are_never_read_as_placeholders():
    context = ReplyContext("talk", 2.0, tuple(PASSING.events), 5.0)
    odd = parse_reply(reply(intent="Say {reply_format} and {steps}", message="{decisions}"), context)
    text = DEBRIEF.text([odd])
    assert '"Say {reply_format} and {steps}"' in text and 'You said: "{decisions}"' in text


# --- the mock policies, through issue #24's retry --------------------------------------------------------


def ask(policy, path_index, context, retry_text, parse=None):
    client = MockClient(policy=policy)
    return request_with_retry(
        client, [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}], "mock", 0.0, 400, False,
        {"path_index": path_index}, parse or reply_parser(context), retry_text,
    )


EXPECTED = {
    "carry_on": (1, None), "swerve_left": (1, None), "swerve_right": (1, None), "slow_then_resume": (1, None),
    "stop_until_other_passes": (1, None), "back_up_then_wait": (1, None), "delayed_start": (1, None),
    **{f"signal_{s}": (1, None) for s in SIGNALS if s != "none"},
    "talk_message": (1, None), "unreadable_then_carry_on": (2, None), "unreadable_twice": (2, "not_json"),
    "out_of_range": (2, "speed_out_of_range"), "unknown_event": (2, "unknown_event"),
}


@pytest.mark.parametrize("condition", CONDITIONS)
def test_every_mock_path(condition):
    assert tuple(EXPECTED) == mock.RESOLVE_PATH_NAMES
    context = ReplyContext(condition, 1.4, tuple(PASSING.events), 5.0)
    for index, path in enumerate(mock.RESOLVE_PATH_NAMES):
        result = ask(mock.resolve_paths_v1, index, context, CORE.retry(condition))
        attempts, failure = EXPECTED[path]
        assert len(result.attempts) == attempts, path
        assert (result.failure or "").split(":")[0] == (failure or ""), (path, result.failure)
        if failure is None:
            parsed = result.parsed
            if path.startswith("signal_"):
                expected = "none" if condition == "independent" else path[len("signal_"):]
                assert parsed.signal == expected and (("signal_ignored" in parsed.flags) == (condition == "independent"))
            if path == "talk_message":
                assert parsed.message == ("Excuse me." if condition == "talk" else "")
            if path == "carry_on":
                assert parsed.steps == ()
    shown = ask(mock.resolve_paths_v1, mock.RESOLVE_PATH_NAMES.index("unreadable_then_carry_on"), context, CORE.retry(condition))
    assert shown.attempts[1].prompt_messages[-1]["content"] == CORE.retry(condition)  # the retry is the template's


def test_the_debrief_mock_paths():
    for index, name in enumerate(mock.DEBRIEF_PATH_NAMES):
        result = ask(mock.debrief_paths_v1, index, None, DEBRIEF.retry(), parse=parse_debrief)
        assert result.failure is None and (result.parsed.source is None) == (name == "none")
    assert set(mock.POLICIES) == {"resolve_paths_v1", "debrief_paths_v1", "resolution_rehearsal_v1"}  # the last: issue #58


# --- a second scenario: added without touching the core template or the parser ------------------------------


class QueueScenario(Scenario):
    """A toy scenario defined only here: a counter queue, with a block and an event of its own."""

    DATA = {
        "template_id": "scenario_toyqueue", "version": 1, "kind": "resolution_scenario",
        "description": "A toy queue, for the tests only.",
        "place": {"queue": "- You are in a queue at a counter. {ahead} people are ahead of you."},
        "events": {"queue_moves": "until the queue moves on", "i_reach_the_counter": "until you reach the counter"},
        "extra_blocks": {"queue": {"header": "YOUR QUEUE", "line": "- You have been waiting for {minutes} minutes."}},
        "factor_lines": {"crowding": {"busy": "- The hall is busy.", "quiet": "- The hall is quiet."}},
    }

    def place_lines(self, case, record):
        return [self.data["place"]["queue"].replace("{ahead}", "3")]

    def extra_blocks(self, case, record):
        block = self.data["extra_blocks"]["queue"]
        return [Block(block["header"], (block["line"].replace("{minutes}", "4"),))]


def test_a_second_scenario_renders_through_the_same_core_template():
    queue = QueueScenario("scenario_toyqueue_v1", QueueScenario.DATA, "a" * 64)
    case = STORE.get("passage_25f09e61")
    view = adapter.opening_view(case, 0, queue, CORE)
    view = dataclasses.replace(view, place=view.place + tuple(queue.factor_lines({"crowding": "busy"})))
    rendered = render(view, "talk", queue, CORE)
    assert rendered.templates == {"core": CORE.identity(), "scenario": {"key": "scenario_toyqueue_v1", "sha256": "a" * 64}}
    assert '"queue_moves" (until the queue moves on) or "i_reach_the_counter" (until you reach the counter)' in rendered.system
    assert "other_passes" not in rendered.system and "passage" not in rendered.user
    assert "WHERE YOU ARE\n- You are in a queue at a counter. 3 people are ahead of you.\n- The hall is busy." in rendered.user
    assert rendered.user.index("WHERE YOU ARE") < rendered.user.index("YOUR QUEUE") < rendered.user.index("WHO YOU CAN SEE")
    context = ReplyContext.of(view, "talk", queue.events)
    assert parse_reply(reply(steps=[{"speed_mps": 0, "until": "queue_moves"}]), context).steps[0].until.event == "queue_moves"
    fails("unknown_event", reply(steps=[{"speed_mps": 0, "until": "other_passes"}]), context)
    # the core template's text outside the scenario's parts is the passing scenario's, byte for byte
    passing = render(view_of(case, 0), "talk", PASSING, CORE).system
    assert rendered.system.replace(CORE.events_text(queue), "") == passing.replace(CORE.events_text(PASSING), "")
    with pytest.raises(ConfigError, match="no line for"):
        queue.factor_lines({"crowding": "empty"})


def test_scenario_plugins_and_their_templates():
    assert PLUGINS == {"passing": PassingScenario, "passing_crowd": PassingCrowdScenario, "passing_group": PassingGroupScenario}  # passing_crowd: issue #58; passing_group: issue #110
    with pytest.raises(ConfigError, match="unknown scenario"):
        load_scenario("escalator")
    with pytest.raises(ConfigError, match="at least one event"):
        QueueScenario("scenario_toyqueue_v1", {**QueueScenario.DATA, "events": {}}, "a" * 64)
    with pytest.raises(ConfigError, match="missing key"):
        QueueScenario("scenario_toyqueue_v1", {k: v for k, v in QueueScenario.DATA.items() if k != "events"}, "a" * 64)
    assert PASSING.factor_lines({}) == []
