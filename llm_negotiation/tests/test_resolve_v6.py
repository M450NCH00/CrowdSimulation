"""Issue #65 (RF-10): RF-9's three fixes, adopted for round 1's screen on the user's delegation.

1. An ``until`` at a distance, and an event written as an object (``resolve_v6``; reply parser,
   executor).
2. A walking person up to 45° off the opposite or the same direction is drifting, not walking
   across (``resolve_v6``; prompt).
3. The encounter does not end on ``no_conflict`` while a plan still runs
   (``protocol.no_conflict_waits_for_plans``).

Each is off under the earlier templates and the default protocol, which render, read and end
exactly as before.
"""

from __future__ import annotations

import json
import math

import pytest

from negsim.configutil import ConfigError
from negsim.negotiation import prompts
from negsim.negotiation.parsing import TurnParseError
from negsim.resolution import execute as X
from negsim.resolution import experiment as E
from negsim.resolution import protocol as P
from negsim.resolution.prompt import DRIFT_MAX_DEG, CoreTemplate, render
from negsim.resolution.reply import ReplyContext, Until, parse_reply
from test_encounter_protocol import STORE, reply, session_on
from test_execute import EVENTS, records, run_plans, steps
from test_perceive import PASSING, at, look, perceiver

V5, V6 = CoreTemplate.load("resolve_v5"), CoreTemplate.load("resolve_v6")
HEAD_ON = STORE.get("head_on_02dfbadb", 2)


def raw_until(until):
    return json.dumps({"intent": "Slow down.", "steps": [{"speed_mps": 0.8, "until": until}], "reason": "r"})


def context(core, distance=9.0):
    return ReplyContext("independent", 2.0, EVENTS, distance, core.later_step_start, core.until_at_distance, core.until_event_as_object)


# --- resolve_v6 against resolve_v5 ----------------------------------------------------------------


def test_resolve_v6_is_resolve_v5_but_for_the_until_sentence_two_headings_and_two_flags():
    assert prompts.load_manifest()["resolve_v6"]["kind"] == "resolution"
    assert (V5.until_at_distance, V5.until_event_as_object, V6.until_at_distance, V6.until_event_as_object) == (False, False, True, True)
    assert V6.later_step_start
    for key in ("conditions", "event_item", "decision_point", "role", "system"):
        assert V6.data[key] == V5.data[key]
    headings = dict(V6.data["view"]["headings"])
    assert set(headings) - set(V5.data["view"]["headings"]) == {"opposite_drifting", "same_drifting"}
    assert {k: v for k, v in V6.data["view"].items() if k != "headings"} == {k: v for k, v in V5.data["view"].items() if k != "headings"}
    assert {k: headings[k] for k in V5.data["view"]["headings"]} == V5.data["view"]["headings"]
    old, new = V5.data["step_format"].splitlines(), V6.data["step_format"].splitlines()
    changed = [(a, b) for a, b in zip(old, new) if a != b]
    assert len(old) == len(new) and len(changed) == 1
    assert changed[0][0].startswith('"until"') and '{"at_distance_m": <metres>}' in changed[0][1] and "in quotes" in changed[0][1]
    for condition in ("independent", "non_verbal", "talk"):
        assert V6.retry(condition) == V5.retry(condition)
        assert V6.system(condition, PASSING) != V5.system(condition, PASSING)


# --- fix 1: the until forms -----------------------------------------------------------------------


@pytest.mark.parametrize("until", [{"other_passes": True}, {"other_passes": "other_passes"}, {"other_passes": ""}, {"other_passes": None}, {"OTHER_PASSES": 1}])
def test_an_event_written_as_an_object_is_read_as_the_event_and_flagged_under_resolve_v6_only(until):
    with pytest.raises(TurnParseError, match="unknown_until"):
        parse_reply(raw_until(until), context(V5))
    parsed = parse_reply(raw_until(until), context(V6))
    assert parsed.steps[0].until == Until(event="other_passes")
    assert parsed.flags == ("until_event_as_object:steps[0].until",)
    assert parsed.steps[0].as_dict()["until"] == "other_passes"  # recorded as its name


@pytest.mark.parametrize("until", [{"other_passes": False}, {"other_waves": True}, {"other_passes": True, "seconds": 2}, {"seconds": 2, "at_distance_m": 2}])
def test_an_object_that_is_not_one_known_event_is_still_unreadable(until):
    with pytest.raises(TurnParseError, match="unknown_until"):
        parse_reply(raw_until(until), context(V6))


def test_an_until_at_a_distance_is_read_under_resolve_v6_with_the_checks_of_a_start():
    with pytest.raises(TurnParseError, match="unknown_until"):
        parse_reply(raw_until({"at_distance_m": 2.0}), context(V5))
    parsed = parse_reply(raw_until({"at_distance_m": 2}), context(V6))
    assert parsed.steps[0].until == Until(at_distance_m=2.0) and parsed.flags == ()
    assert parsed.steps[0].as_dict()["until"] == {"at_distance_m": 2.0}
    for until, distance, code in (({"at_distance_m": 0}, 9.0, "until_at_distance_not_positive"),
                                  ({"at_distance_m": 3.0}, 2.5, "until_at_distance_beyond_current"),
                                  ({"at_distance_m": 3.0}, None, "until_at_distance_with_nobody_in_view"),
                                  ({"at_distance_m": "near"}, 9.0, "until_not_a_number")):
        with pytest.raises(TurnParseError, match=code):
            parse_reply(raw_until(until), context(V6, distance))


def test_a_starts_failure_codes_are_unchanged():
    raw = json.dumps({"intent": "Wait.", "steps": [{"start": {"at_distance_m": 3.0}, "speed_mps": 0.5, "until": {"seconds": 1}}], "reason": "r"})
    for core in (V5, V6):
        with pytest.raises(TurnParseError, match="start_at_distance_beyond_current"):
            parse_reply(raw, context(core, 2.0))


def test_a_step_with_an_until_at_a_distance_ends_when_the_other_is_that_close():
    slow = [{"speed_mps": 0.8, "until": {"at_distance_m": 3}}]
    assert steps(slow)[0].until == Until(at_distance_m=3.0)  # a replay reads it back
    run, _, _ = run_plans(X.MODE_PLAN_ORCA, {0: slow, 1: []})
    (record,) = records(run, 0)
    assert record["ended_by"] == X.ENDED_AT_DISTANCE
    track = {row.step: row for row in run.driver.track}
    gap = lambda k: math.dist(*(track[k].bodies[a].xy for a in (0, 1)))
    assert gap(record["end_step"]) <= 3.0 + 1e-9 < gap(record["end_step"] - 1)


# --- fix 2: the drift ----------------------------------------------------------------------------


def heading_text(core, degrees_off_opposite, speed=1.3, distance=8.0):
    """The other, ``distance`` m ahead, walking ``degrees_off_opposite`` off straight towards the
    observer, turned to the observer's left (positive) or right (negative)."""
    rad = math.radians(180.0 - degrees_off_opposite)
    other = at(1, distance, 0.0, vx=speed * math.cos(rad), vy=speed * math.sin(rad))
    return render(look([at(0, 0.0, 0.0, vx=1.3), other], perceiver(core=core)), "talk", PASSING, core).user


@pytest.mark.parametrize("off, side", [(20.0, "left"), (-20.0, "right"), (40.0, "left"), (-12.0, "right")])
def test_a_walker_up_to_45_degrees_off_opposite_is_drifting_under_resolve_v6(off, side):
    old, new = heading_text(V5, off), heading_text(V6, off)
    assert "across your direction of travel" in old
    assert f"walking in the opposite direction to you, drifting to your {side} by {round(abs(off))}°" in new
    assert "across" not in new


@pytest.mark.parametrize("off", [0.0, 5.0, -9.0, 50.0, 90.0, -120.0])
def test_beyond_the_drift_band_resolve_v6_renders_what_resolve_v5_does(off):
    assert abs(off) <= 10.0 or abs(off) > DRIFT_MAX_DEG
    assert heading_text(V6, off) == heading_text(V5, off)


def test_a_drift_off_the_same_direction_and_someone_standing_still():
    rad = math.radians(25.0)
    ahead = at(1, 4.0, 0.0, vx=1.0 * math.cos(rad), vy=1.0 * math.sin(rad))
    text = render(look([at(0, 0.0, 0.0, vx=1.3), ahead], perceiver(core=V6)), "talk", PASSING, V6).user
    assert "in the same direction as you, drifting to your left by 25°" in text
    still = at(1, 4.0, 0.0, facing=math.radians(160.0))
    texts = [render(look([at(0, 0.0, 0.0, vx=1.3), still], perceiver(core=core)), "talk", PASSING, core).user for core in (V5, V6)]
    assert texts[0] == texts[1] and "drifting" not in texts[1]  # a drift is a way of walking, not of facing


# --- fix 3: no_conflict while a plan runs ----------------------------------------------------------


ASIDE_AND_BACK = reply("Step aside, then back.", [{"turn": {"to": "right", "degrees": 20}, "speed_mps": 1.3, "until": {"seconds": 1.5}},
                                                  {"turn": {"to": "left", "degrees": 20}, "speed_mps": 1.3, "until": {"seconds": 3}}])


def test_by_default_no_conflict_can_end_the_encounter_while_a_plan_still_runs():
    run, record, _ = session_on(HEAD_ON, "non_verbal", {0: ASIDE_AND_BACK, 1: ASIDE_AND_BACK}, settings=P.ProtocolSettings(execution="as_prompted"))
    assert record["encounter"]["end"]["reason"] == P.END_NO_CONFLICT and run._plans_running()
    assert "no_conflict_waits_for_plans" not in record["protocol"]


def test_with_the_wait_the_encounter_stays_open_until_the_plans_have_run():
    settings = P.ProtocolSettings(execution="as_prompted", no_conflict_waits_for_plans=True)
    run, record, _ = session_on(HEAD_ON, "non_verbal", {0: ASIDE_AND_BACK, 1: ASIDE_AND_BACK}, settings=settings)
    end = record["encounter"]["end"]
    assert end["reason"] != P.END_NO_CONFLICT or not run._plans_running()
    assert end["time_s"] > 4.2 and len(record["decision_points"]) > 2  # asked again as the step back brought them together
    assert record["protocol"]["no_conflict_waits_for_plans"] is True


def test_the_wait_is_described_only_when_on_and_must_be_true_or_false():
    assert "no_conflict_waits_for_plans" not in P.ProtocolSettings().as_dict()
    assert P.ProtocolSettings.from_mapping({"no_conflict_waits_for_plans": False}) == P.ProtocolSettings()
    assert P.ProtocolSettings.from_mapping({"no_conflict_waits_for_plans": True}).as_dict()["no_conflict_waits_for_plans"] is True
    with pytest.raises(ConfigError):
        P.ProtocolSettings.from_mapping({"no_conflict_waits_for_plans": "yes"})


# --- the resolution gate (task 3) and the screen's config ----------------------------------------


RAW = {
    "layer": "resolution", "experiment_name": "raw", "cases": {"ids": ["head_on_02dfbadb@2"]}, "conditions": ["talk"],
    "design": {"seed": 1, "factors": {"age_pair": ["same"], "gender_pair": ["p1_female"], "task": ["p1_urgent"], "demographics_visible": [True], "mapping": ["p1_lower"]}},
    "llm": {"client": "mock"},
}
GATE = {"plan_only_resolved_min": 0.5, "reason": "More often than not."}


def test_the_gate_is_recorded_only_when_set_and_needs_a_rate_and_a_reason():
    assert E.ResolutionConfig.from_raw(RAW).resolution_gate is None
    assert "resolution_gate" not in E.ResolutionConfig.from_raw(RAW).as_dict()
    gated = E.ResolutionConfig.from_raw({**RAW, "resolution_gate": GATE})
    assert gated.as_dict()["resolution_gate"] == {"plan_only_resolved_min": 0.5, "reason": "More often than not."}
    for bad in ({"plan_only_resolved_min": 0.5}, {"reason": "r"}, {**GATE, "plan_only_resolved_min": 1.5},
                {**GATE, "plan_only_resolved_min": -0.1}, {**GATE, "reason": "  "}, {**GATE, "mode": "plan_orca"}):
        with pytest.raises(ConfigError):
            E.ResolutionConfig.from_raw({**RAW, "resolution_gate": bad})


SCREEN = "configs/resolution/round1_head_on_screening.yaml"


def test_the_round_1_screen_is_the_issues_design_with_rf9s_fixes_and_the_gate():
    config = E.ResolutionConfig.load(SCREEN)
    varied = [name for name, levels in config.design.levels.items() if len(levels) == 2]
    assert len(varied) == 16 and config.design.kind == "fractional"
    for name in ("age_pair", "gender_pair", "urgency", "mobility_aid", "load", "distraction", "assertiveness", "residence",
                 "attractiveness_0_sees_1", "attractiveness_1_sees_0", "familiarity", "memory_note", "ethnicity_pair",
                 "surroundings", "time_of_day", "mapping"):
        assert name in varied
    assert config.conditions == ("independent", "non_verbal", "talk")
    assert config.templates["core"] == "resolve_v6" and config.protocol.execution == "as_prompted"
    assert config.protocol.no_conflict_waits_for_plans and config.llm["max_tokens"] == 300 and config.llm["temperature"] == 1.0
    assert config.resolution_gate["plan_only_resolved_min"] == 0.5
    assert config.llm["client"] == "mock"  # a paid run waits for CLAUDE.md's approval and cap for #65
    assert config.budget["over_cap"] == "stop_at_cap"
    said = []
    plan = E.print_plan(config, out=said.append)
    assert len(plan.sessions) == 288
    assert any("resolution gate" in line and "0.50" in line for line in said)
