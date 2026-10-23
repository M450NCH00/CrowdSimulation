"""Issue #73 (RF-17): what an LLM agent perceives in the running simulation: the view cone, occlusion,
hearing, signals, changes since it last looked, the time to meet, its history and stable labels
(``docs/resolution.md``, D2, D5, D10 and D12)."""

from __future__ import annotations

import dataclasses
import json
import math
import re
from pathlib import Path

import pytest
import yaml

from helpers import crowd
from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.core.geometry import Rect
from negsim.negotiation import prompts
from negsim.resolution import perceive as P
from negsim.resolution.prompt import SIMULATION_CORE_TEMPLATE, CoreTemplate, render
from negsim.resolution.scenarios import load_scenario
from negsim.resolution.view import CONDITIONS, Me
from test_resolution import GROUP_WORDS, ORDER_WORDS, SUGGESTIONS

V1 = CoreTemplate.load("resolve_v1")
V2 = CoreTemplate.load(SIMULATION_CORE_TEMPLATE)
PASSING = load_scenario("passing")
SETTINGS = P.LLMViewSettings.load()
ME = Me(speed_mps=1.3, preferred_speed_mps=1.3, max_speed_mps=2.0, width_m=0.5)
PEOPLE = {0: {"age": 34, "gender": "female", "errand": "the post office"}, 1: {"age": 71, "gender": "male", "errand": "a secret appointment"}}
SCENARIOS = ("wide_corridor_head_on", "overtaking", "open_crossing", "corridor_to_bottleneck", "passage_meet_middle_v1")


def body(agent, x, y, vx=0.0, vy=0.0, facing=None, radius=0.25, backing=False):
    if facing is None:
        facing = math.atan2(vy, vx) if (vx or vy) and not backing else 0.0
    return P.Body(agent, (x, y), (vx, vy), facing, radius, backing)


def at(agent, distance, degrees, **kwargs):
    """A person ``distance`` m away at ``degrees`` to the left of an observer at the origin facing +x."""
    rad = math.radians(degrees)
    return body(agent, distance * math.cos(rad), distance * math.sin(rad), **kwargs)


def perceiver(agent=0, partner=1, settings=SETTINGS, core=V2, **kwargs):
    return P.Perceiver(agent, partner, settings, PASSING, core, people=kwargs.pop("people", PEOPLE), since_s=kwargs.pop("since_s", 0.0), **kwargs)


def look(bodies, p=None, time_s=1.0, walls=(), exchange=None, **kwargs):
    p = p or perceiver()
    return p.look(time_s, bodies, walls, ME, exchange, **kwargs)


def seen_ids(view):
    by_label = {label: int(agent) for agent, label in view.labels["label_of_agent"].items()}
    return [by_label[person.label] for person in view.seen]


OBSERVER = body(0, 0.0, 0.0, vx=1.3)


# --- the config -----------------------------------------------------------------------------------


def test_the_shipped_settings_are_d12s():
    assert (SETTINGS.half_angle_deg, SETTINGS.range_m, SETTINGS.detail_range_m) == (75.0, 10.0, 5.0)
    assert SETTINGS.occlusion and SETTINGS.walls_block_sight and SETTINGS.max_people is None
    assert (SETTINGS.change_sideways_m, SETTINGS.change_speed_mps, SETTINGS.change_turn_deg) == (0.2, 0.2, 5.0)


TAG = re.compile(r"\[(cited: [^\]]+|derived: [^\]]+|placeholder|design)\]")


def config_lines():
    text = P.LLM_VIEW_CONFIG.read_text(encoding="utf-8")
    block = text.split("llm_view:", 1)[1]
    return [line for line in block.splitlines() if re.match(r"\s+\w+:\s*[^\s#]", line)]


def test_every_value_in_the_llm_view_block_is_tagged():
    lines = config_lines()
    assert len(lines) == 12
    for line in lines:
        assert TAG.search(line), f"llm_view_v1.yaml: {line.strip()!r} has no tag"


def test_every_placeholder_is_marked_in_the_config_and_in_the_parameters_document():
    placeholders = [line.split(":")[0].strip() for line in config_lines() if "[placeholder]" in line]
    assert placeholders == ["hearing_range_m", "heard_close_m", "eye_contact_range_m", "sideways_m", "speed_mps", "turn_deg"]
    section = (PACKAGE_ROOT / "docs" / "parameters.md").read_text(encoding="utf-8").split("### 8.2 Placeholders", 1)[1].split("### 8.3", 1)[0]
    for name in ("hearing_range_m", "heard_close_m", "eye_contact_range_m", "change_thresholds"):
        row = next((line for line in section.splitlines() if f"`{name}`" in line), None)
        assert row is not None and "[placeholder]" in row, f"parameters.md 8.2 does not list {name} as a placeholder"


def test_the_config_values_and_the_parameters_document_agree():
    section = (PACKAGE_ROOT / "docs" / "parameters.md").read_text(encoding="utf-8").split("## 8.", 1)[1]
    assert "7 m `[placeholder]`" in section and "3 m `[placeholder]`" in section and "4 m `[placeholder]`" in section
    assert "0.2 m sideways, 0.2 m/s, 5° `[placeholder]`" in section


@pytest.mark.parametrize("change, message", [
    ({"half_angle_deg": 190}, "half_angle_deg"),
    ({"detail_range_m": 12}, "detail_range_m"),
    ({"eye_contact_range_m": 11}, "eye_contact_range_m"),
    ({"heard_close_m": 8}, "heard_close_m"),
    ({"max_people": 0}, "max_people"),
    ({"max_people": True}, "max_people"),
    ({"range_m": 0}, "range_m"),
    ({"occlusion": "yes"}, "occlusion"),
    ({"hearing": 3}, "unknown key"),
])
def test_a_bad_llm_view_block_is_refused(change, message):
    block = yaml.safe_load(P.LLM_VIEW_CONFIG.read_text(encoding="utf-8"))["llm_view"]
    block.update(change)
    with pytest.raises(ConfigError, match=message):
        P.LLMViewSettings.from_mapping(block)


# --- who is seen ----------------------------------------------------------------------------------


@pytest.mark.parametrize("distance, degrees, seen", [
    (5.0, 0.0, True), (5.0, 74.9, True), (5.0, 75.0, True), (5.0, -75.0, True), (5.0, 76.0, False), (5.0, -76.0, False),
    (10.0, 0.0, True), (10.1, 0.0, False), (9.9, 70.0, True), (3.0, 180.0, False),
])
def test_the_view_cone_and_the_seeing_range(distance, degrees, seen):
    view = look([OBSERVER, at(1, distance, degrees)])
    assert bool(view.seen) is seen


def test_someone_behind_a_nearer_person_is_not_seen():
    bodies = [OBSERVER, at(1, 6.0, 0.0), at(2, 3.0, 0.0)]
    assert seen_ids(look(bodies, perceiver(partner=1))) == [2]


def test_occlusion_needs_the_line_of_sight_to_pass_through_the_nearer_disc():
    grazing = body(2, 3.0, 0.25)  # the line of sight touches the disc's edge and no more
    inside = body(2, 3.0, 0.24)
    assert seen_ids(look([OBSERVER, at(1, 6.0, 0.0), grazing])) == [2, 1]
    assert seen_ids(look([OBSERVER, at(1, 6.0, 0.0), inside])) == [2]


def test_only_a_nearer_person_hides_someone():
    assert seen_ids(look([OBSERVER, at(1, 3.0, 0.0), at(2, 6.0, 0.0)])) == [1]  # 2 is hidden, 1 is not
    assert seen_ids(look([OBSERVER, at(1, 3.0, 0.0), at(2, 6.0, 0.0)], perceiver(partner=2))) == [1]


def test_with_occlusion_off_everyone_in_the_cone_is_seen():
    settings = dataclasses.replace(SETTINGS, occlusion=False)
    assert seen_ids(look([OBSERVER, at(1, 6.0, 0.0), at(2, 3.0, 0.0)], perceiver(settings=settings))) == [2, 1]


def test_a_wall_blocks_sight_unless_the_switch_is_off():
    wall = Rect(2.0, -1.0, 2.5, 1.0)
    assert seen_ids(look([OBSERVER, at(1, 5.0, 0.0)], walls=[wall])) == []
    settings = dataclasses.replace(SETTINGS, walls_block_sight=False)
    assert seen_ids(look([OBSERVER, at(1, 5.0, 0.0)], perceiver(settings=settings), walls=[wall])) == [1]


def test_people_in_view_are_sorted_by_distance_and_described_in_full_within_5_m():
    view = look([OBSERVER, at(1, 8.0, 20.0), at(2, 2.0, -30.0), at(3, 5.0, 40.0), at(4, 5.01, -10.0)])
    assert seen_ids(view) == [2, 3, 4, 1]
    assert [p.detail for p in view.seen] == ["full", "full", "short", "short"]
    assert view.labels["people_left_out"] == 0


def test_everyone_visible_is_described_with_no_fixed_count():
    crowd_bodies = [OBSERVER] + [at(k, 1.0 + 0.6 * k, (-1) ** k * 3.0 * k) for k in range(1, 15)]
    view = look(crowd_bodies, perceiver(settings=dataclasses.replace(SETTINGS, occlusion=False)))
    assert len(view.seen) == 14


def test_max_people_is_a_cap_that_records_who_it_left_out_and_keeps_the_partner():
    settings = dataclasses.replace(SETTINGS, max_people=2, occlusion=False)
    bodies = [OBSERVER, at(1, 9.0, 0.0), at(2, 2.0, 30.0), at(3, 3.0, -30.0), at(4, 4.0, 10.0)]
    view = look(bodies, perceiver(settings=settings, partner=1))
    assert seen_ids(view) == [2, 1] and view.labels["people_left_out"] == 2
    view = look(bodies, perceiver(settings=settings, partner=3))
    assert seen_ids(view) == [2, 3] and view.labels["people_left_out"] == 2


def test_the_observer_faces_its_path_when_it_walks_backwards():
    agent = type("A", (), {})()
    agent.agent_id, agent.pose = 0, type("Pose", (), {"xy": (0.0, 0.0), "theta": math.pi})()
    agent.velocity, agent.path_s = (-0.9, 0.0), 1.0
    agent.spec = type("Spec", (), {"radius": 0.25, "path": type("Path", (), {"heading_at": staticmethod(lambda s: 0.0)})()})()
    me = P.body_of(agent)
    assert me.backing and me.facing_rad == 0.0
    assert seen_ids(look([me, at(1, 3.0, 0.0)])) == [1]


# --- stable labels --------------------------------------------------------------------------------


def test_labels_stay_the_same_across_decision_points():
    p = perceiver()
    first = look([OBSERVER, at(1, 6.0, 15.0), at(2, 3.0, -15.0)], p, time_s=1.0)
    assert dict(first.labels["label_of_agent"]) == {"1": 2, "2": 1}
    p.decided(1.0, OBSERVER, "Keep going.")
    # Now 1 is nearer than 2, and 3 comes into view nearest of all.
    second = look([OBSERVER, at(1, 2.0, 15.0), at(2, 4.0, -15.0), at(3, 1.5, 0.0)], p, time_s=2.5, outcomes=["completed"])
    assert seen_ids(second) == [3, 1, 2]
    assert [person.label for person in second.seen] == [3, 2, 1]
    assert second.seen[0].changes == ("came_into_view",)
    assert second.decision_point == 2


def test_a_decision_point_needs_the_reply_to_the_one_before():
    p = perceiver()
    look([OBSERVER, at(1, 6.0, 0.0)], p)
    with pytest.raises(ValueError, match="decided"):
        look([OBSERVER, at(1, 6.0, 0.0)], p, time_s=2.0)
    p.decided(1.0, OBSERVER, "Wait.")
    with pytest.raises(ValueError, match="one outcome"):
        look([OBSERVER, at(1, 6.0, 0.0)], p, time_s=2.0)
    with pytest.raises(ValueError, match="decision follows a look"):
        p.decided(1.0, OBSERVER, "Again.")


# --- hearing --------------------------------------------------------------------------------------


def test_someone_behind_is_heard_but_not_seen_and_is_someone_behind_you():
    ex = P.Exchange(SETTINGS)
    bodies = [OBSERVER, at(1, 2.0, 180.0, vx=1.5)]
    ex.say(0.5, 1, "Excuse me.", bodies)
    view = look(bodies, exchange=ex)
    assert not view.seen
    assert [(h.message, h.label, h.direction, h.band) for h in view.heard] == [("Excuse me.", None, "behind", "close")]
    assert '- Someone behind you, close by, says: "Excuse me."' in render(view, "talk", PASSING, V2).user
    # resolve_v1 renders the same view as it always did.
    v1_view = dataclasses.replace(view, templates={"core": V1.identity(), "scenario": PASSING.identity()})
    assert '- Someone behind you says: "Excuse me."' in render(v1_view, "talk", PASSING, V1).user


@pytest.mark.parametrize("speaker, direction, band", [
    (at(1, 2.0, 100.0), "left", "close"),
    (at(1, 6.5, -90.0), "right", "far"),
    (at(1, 3.0, 140.0), "behind", "close"),
])
def test_a_voice_out_of_view_has_a_rough_direction_and_a_distance_band(speaker, direction, band):
    ex = P.Exchange(SETTINGS)
    ex.say(0.5, 1, "Hello.", [OBSERVER, speaker])
    heard = look([OBSERVER, speaker], exchange=ex).heard
    assert [(h.direction, h.band) for h in heard] == [(direction, band)]


def test_a_speaker_hidden_ahead_is_someone_ahead_of_you_not_behind():
    ex = P.Exchange(SETTINGS)
    bodies = [OBSERVER, at(1, 5.0, 0.0), at(2, 2.0, 0.0)]
    ex.say(0.5, 1, "Coming through.", bodies)
    view = look(bodies, exchange=ex)
    assert seen_ids(view) == [2]
    assert '- Someone ahead of you, further away, says: "Coming through."' in render(view, "talk", PASSING, V2).user


def test_a_speaker_in_view_is_named_by_label():
    ex = P.Exchange(SETTINGS)
    bodies = [OBSERVER, at(1, 3.0, 0.0)]
    ex.say(0.5, 1, "After you.", bodies)
    view = look(bodies, exchange=ex)
    assert [(h.label, h.direction) for h in view.heard] == [(1, None)]
    assert '- Person 1 says: "After you."' in render(view, "talk", PASSING, V2).user


def test_speech_beyond_the_hearing_range_is_not_heard_and_walls_do_not_stop_it():
    ex = P.Exchange(SETTINGS)
    far, near = at(1, SETTINGS.hearing_range_m + 0.1, 180.0), at(2, SETTINGS.hearing_range_m, 180.0)
    ex.say(0.5, 1, "Far.", [OBSERVER, far, near])
    ex.say(0.5, 2, "Near.", [OBSERVER, far, near])
    view = look([OBSERVER, far, near], walls=[Rect(-3.0, -1.0, -2.5, 1.0)], exchange=ex)
    assert [h.message for h in view.heard] == ["Near."]


def test_only_what_was_said_since_the_agent_last_looked_is_heard():
    ex = P.Exchange(SETTINGS)
    bodies = [OBSERVER, at(1, 3.0, 180.0)]
    p = perceiver(since_s=0.2)
    ex.say(0.1, 1, "Before the encounter.", bodies)
    ex.say(0.5, 1, "One.", bodies)
    assert [h.message for h in look(bodies, p, time_s=1.0, exchange=ex).heard] == ["One."]
    p.decided(1.0, OBSERVER, "Go on.")
    ex.say(1.5, 1, "Two.", bodies)
    ex.say(1.5, 0, "My own words.", bodies)
    assert [h.message for h in look(bodies, p, time_s=2.0, exchange=ex, outcomes=["ongoing"]).heard] == ["Two."]


# --- signals --------------------------------------------------------------------------------------


def test_a_signal_from_someone_out_of_view_does_not_appear():
    ex = P.Exchange(SETTINGS)
    behind = at(1, 2.0, 180.0, vx=1.3)  # walking behind the observer, facing the same way
    ex.signal(0.5, 1, "wave_on", [OBSERVER, behind], [])
    assert ex.signals[0].seen_by == frozenset()
    view = look([OBSERVER, behind], exchange=ex)
    assert not view.seen and "wave" not in render(view, "non_verbal", PASSING, V2).user


def test_a_signal_counts_only_if_the_observer_could_see_it_when_it_was_made():
    ex = P.Exchange(SETTINGS)
    then = [OBSERVER, at(1, 3.0, 0.0, vx=-1.3), at(2, 1.5, 0.0)]  # 2 stands between them
    ex.signal(0.5, 1, "wave_on", then, [])
    now = [OBSERVER, at(1, 3.0, 0.0, vx=-1.3)]  # 2 has gone; 1 is in view now
    view = look(now, exchange=ex)
    assert seen_ids(view) == [1] and view.seen[0].signal == "none"


def test_eye_contact_and_a_nod_need_the_two_within_the_eye_contact_range():
    ex = P.Exchange(SETTINGS)
    other = at(1, SETTINGS.eye_contact_range_m + 0.5, 0.0, vx=-1.3)
    for signal in ("eye_contact", "nod", "wave_on"):
        ex.signal(0.5, 1, signal, [OBSERVER, other], [])
    assert [s.signal for s in ex.signals if 0 in s.seen_by] == ["wave_on"]
    view = look([OBSERVER, other], exchange=ex)
    assert view.seen[0].signal == "wave_on"
    close = at(1, SETTINGS.eye_contact_range_m, 0.0, vx=-1.3)
    ex2 = P.Exchange(SETTINGS)
    ex2.signal(0.5, 1, "nod", [OBSERVER, close], [])
    assert look([OBSERVER, close], exchange=ex2).seen[0].signal == "nod"


def test_a_signal_on_a_short_line_is_rendered_by_resolve_v2_only():
    ex = P.Exchange(SETTINGS)
    other = at(1, 7.0, 0.0, vx=-1.3)
    ex.signal(0.5, 1, "wave_on", [OBSERVER, other], [])
    view = look([OBSERVER, other], exchange=ex)
    assert view.seen[0].detail == "short"
    assert "They wave you on." in render(view, "non_verbal", PASSING, V2).user
    v1_view = dataclasses.replace(view, templates={"core": V1.identity(), "scenario": PASSING.identity()})
    assert "wave" not in render(v1_view, "non_verbal", PASSING, V1).user


# --- changes since the agent last looked ---------------------------------------------------------


def change(then, now, elapsed=1.0, facing=0.0):
    return P.changes_since(then, now, elapsed, facing, SETTINGS)


@pytest.mark.parametrize("offset, expected", [
    (0.2, ("moved_left",)), (0.19, ()), (-0.2, ("moved_right",)), (-0.19, ()),
])
def test_moving_sideways_fires_at_the_threshold_and_not_below_it(offset, expected):
    then = body(1, 6.0, 0.0, vx=-1.3)
    now = body(1, 4.7, offset, vx=-1.3)
    assert change(then, now) == expected


def test_sideways_is_against_the_observers_left_and_right_and_ignores_a_straight_course():
    then = body(1, 6.0, 0.0, vx=-1.0, vy=0.5)
    assert change(then, body(1, 5.0, 0.5, vx=-1.0, vy=0.5)) == ()  # on its line: no change
    # The same move off its line, seen by an observer facing the other way: right and left swap.
    assert change(then, body(1, 5.0, 0.75, vx=-1.0, vy=0.5), facing=math.pi) == ("moved_right",)


@pytest.mark.parametrize("before, after, expected", [
    (1.0, 1.2, ("sped_up",)), (1.0, 1.19, ()), (1.2, 1.0, ("slowed_down",)), (1.19, 1.0, ()),
    (1.0, 0.0, ("stopped",)), (0.0, 1.0, ("started_walking",)),
])
def test_speed_changes_fire_at_the_threshold_and_not_below_it(before, after, expected):
    then = body(1, 6.0, 0.0, vx=-before, facing=math.pi)
    now = body(1, 6.0 - before, 0.0, vx=-after, facing=math.pi)
    assert change(then, now) == expected


@pytest.mark.parametrize("degrees, expected", [(5.0, ("turned",)), (4.9, ())])
def test_a_turn_fires_at_the_threshold_and_not_below_it(degrees, expected):
    then = body(1, 6.0, 0.0, vx=-1.3)
    rad = math.pi + math.radians(degrees)
    now = body(1, 4.7, 0.0, vx=1.3 * math.cos(rad), vy=1.3 * math.sin(rad))
    assert change(then, now) == expected


def test_starting_to_back_up_is_its_own_change():
    then = body(1, 2.0, 0.0, vx=-1.0, facing=math.pi)
    now = body(1, 2.5, 0.0, vx=0.9, facing=math.pi, backing=True)
    found = change(then, now, elapsed=0.5)
    assert "backing_up" in found and "turned" not in found and "sped_up" not in found


def test_changes_are_rendered_for_a_person_seen_at_both_decision_points():
    p = perceiver()
    look([OBSERVER, at(1, 4.0, 0.0, vx=-1.3)], p, time_s=1.0)
    p.decided(1.0, OBSERVER, "Keep going.")
    view = look([OBSERVER, body(1, 3.0, 0.3, vx=-0.5)], p, time_s=2.0, outcomes=["ongoing"])
    assert view.seen[0].changes == ("slowed_down", "moved_left")
    assert "  Since you last looked, they have slowed down and moved over to your left." in render(view, "talk", PASSING, V2).user


# --- time to meet ---------------------------------------------------------------------------------


def test_the_time_to_meet_is_shown_only_inside_the_safety_distance():
    head_on = [OBSERVER, body(1, 8.0, 0.1, vx=-1.3)]
    view = look(head_on, safety_distance_m=0.6)
    assert view.time_to_meet is not None and view.time_to_meet.label == 1
    assert view.time_to_meet.seconds == pytest.approx(8.0 / 2.6)
    wide = [OBSERVER, body(1, 8.0, 0.7, vx=-1.3)]
    assert look(wide, safety_distance_m=0.6).time_to_meet is None
    assert look(head_on).time_to_meet is None  # no safety distance given: no line
    hidden_partner = [OBSERVER, body(1, 8.0, 0.0, vx=-1.3), body(2, 3.0, 0.0)]
    assert look(hidden_partner, safety_distance_m=0.6).time_to_meet is None


# --- what the agent has done ----------------------------------------------------------------------


def test_history_lines_say_what_came_of_each_decision():
    p = perceiver()
    look([OBSERVER, at(1, 6.0, 0.0, vx=-1.3)], p, time_s=1.0)
    p.decided(1.0, OBSERVER, "Move over to my left.", message="Hi.", signal="nod")
    moved = body(0, 1.0, 0.21, vx=1.3)
    look([moved, at(1, 4.0, 0.0, vx=-1.3)], p, time_s=2.0, outcomes=["ongoing"])
    p.decided(2.0, moved, "Stop and wait.")
    backed = body(0, 0.4, 0.21, vx=0.0)
    view = look([backed, at(1, 2.0, 0.0, vx=-1.3)], p, time_s=3.0, outcomes=["replaced", "completed"])
    text = render(view, "talk", PASSING, V2).user
    assert [d.ago_s for d in view.history] == [2.0, 1.0]
    assert view.history[0].sideways_m == pytest.approx(0.21) and view.history[0].back_m == pytest.approx(-0.4)
    assert view.history[1].sideways_m == pytest.approx(0.0) and view.history[1].back_m == pytest.approx(0.6)
    assert '- 2.0 s ago you decided: "Move over to my left."\n  You said: "Hi."\n  You nodded.\n  Since then you have moved 0.2 m over to your left.\n  You changed those steps at your next decision.' in text
    assert '- 1.0 s ago you decided: "Stop and wait."\n  Since then you have not moved over to either side.\n  You are now 0.6 m further back than where you were then.\n  You have finished those steps.' in text


def test_resolve_v1_refuses_an_outcome_it_has_no_words_for():
    p = perceiver(core=V1)
    look([OBSERVER, at(1, 6.0, 0.0)], p)
    p.decided(1.0, OBSERVER, "Wait.")
    look([OBSERVER, at(1, 6.0, 0.0)], p, time_s=2.0, outcomes=["completed"])
    p.decided(2.0, OBSERVER, "Go.")
    view = look([OBSERVER, at(1, 6.0, 0.0)], p, time_s=3.0, outcomes=["replaced", "ongoing"])
    with pytest.raises(ConfigError, match="replaced"):
        render(view, "talk", PASSING, V1)


# --- from the running simulation ------------------------------------------------------------------


def run_with_views(name, every=1, condition_check=False):
    """Run a scenario; on every ``every``-th step build both agents' views (and reply, so the next
    view is a later decision point). Returns the result and the views."""
    sim = AvoidanceSimulation(crowd(name))
    ex = P.Exchange(SETTINGS)
    perceivers = {a: P.perceiver_for(sim, a, 1 - a, PASSING, people=PEOPLE) for a in (0, 1)}
    views = []
    while sim.status is None and sim.world.step_index < sim.spec.max_steps:
        if sim.world.step_index % every == 0 and sim.world.step_index > 0:
            for agent, p in perceivers.items():
                if sim.world.agents[agent].done:
                    continue
                view = P.view_in(sim, p, ex, outcomes=["ongoing"] * len(p.decisions))
                views.append(view)
                me = P.body_of(sim.world.agents[agent])
                p.decided(sim.world.time, me, "Carry on.", message="Hello." if agent == 1 else "", signal="wave_on")
                ex.say(sim.world.time, agent, "Hello." if agent == 1 else "", P.bodies_in(sim))
                ex.signal(sim.world.time, agent, "wave_on", P.bodies_in(sim), sim.world.obstacles)
        sim.step()
    return sim.finish(), views


def result_json(result):
    dt = 0.1
    return json.dumps({
        "status": result.status, "steps": result.steps, "trajectory": result.trajectory,
        "interactions": [i.as_dict(dt) for i in result.interactions],
        "pairs": [p.as_dict(dt) for p in result.pairs],
        "back_ups": [b.as_dict(dt) for b in result.back_ups],
        "goal_times": result.goal_times, "collisions": result.collisions,
    }, sort_keys=True, default=str)


@pytest.mark.parametrize("name", SCENARIOS)
def test_building_views_leaves_the_run_and_its_perception_records_byte_for_byte_the_same(name):
    plain = AvoidanceSimulation(crowd(name)).run()
    watched, views = run_with_views(name, every=7)
    assert views
    assert result_json(watched) == result_json(plain)


@pytest.mark.parametrize("name", SCENARIOS)
def test_views_from_the_simulation_render_through_resolve_v1_and_v2_in_every_condition(name):
    _, views = run_with_views(name, every=9)
    for view in views:
        for core in (V1, V2):
            built = dataclasses.replace(view, templates={"core": core.identity(), "scenario": PASSING.identity()})
            for condition in CONDITIONS:
                prompt = render(built, condition, PASSING, core)
                shown = (prompt.system + "\n" + prompt.user).lower()
                assert not [w for w in (*ORDER_WORDS, *SUGGESTIONS, *GROUP_WORDS) if w in shown]
                assert "secret appointment" not in shown or view.agent_id == 1


def test_a_view_from_the_simulation_fills_every_block_of_d2():
    sim = AvoidanceSimulation(crowd("wide_corridor_head_on"))
    while math.dist(sim.world.agents[0].pose.xy, sim.world.agents[1].pose.xy) > 4.0:
        sim.step()
    ex = P.Exchange(SETTINGS)
    p = P.perceiver_for(sim, 0, 1, PASSING, people=PEOPLE, since_s=0.0)
    first = P.view_in(sim, p, ex)
    p.decided(sim.world.time, P.body_of(sim.world.agents[0]), "Move over to my left a little.", signal="eye_contact")
    for _ in range(3):
        sim.step()
    bodies = P.bodies_in(sim)
    ex.say(sim.world.time, 1, "Sorry!", bodies)
    ex.signal(sim.world.time, 1, "nod", bodies, sim.world.obstacles)
    sim.step()
    view = P.view_in(sim, p, ex, notes=("You walked here yesterday.",), outcomes=["ongoing"],
                     factor_lines={1: ("They are carrying a heavy bag.",)})
    text = render(view, "talk", PASSING, V2).user
    for header in ("ABOUT YOU", "YOUR NOTES", "WHERE YOU ARE", "WHO YOU CAN SEE", "WHAT YOU CAN HEAR", "WHAT YOU HAVE DONE SO FAR"):
        assert header in text
    assert "At your current speeds you would meet Person 1" in text
    assert '- Person 1 says: "Sorry!"' in text and "They nod at you." in text
    assert "They are carrying a heavy bag." in text
    assert "- You are on your way to the post office." in text and "secret appointment" not in text
    assert "You are in a passage 1.75 m wide" in text
    assert first.decision_point == 1 and view.decision_point == 2
    assert view.labels["scenario_type"] == "wide_corridor_head_on" and view.labels["partner_id"] == 1


def test_a_crowd_run_gives_views_with_many_people_and_hides_those_behind_others():
    sim = AvoidanceSimulation(crowd("bidirectional_flow"))
    for _ in range(100):  # the two crowds have closed in
        sim.step()
    p = P.perceiver_for(sim, 0, 1, PASSING)
    view = P.view_in(sim, p)
    assert len(view.seen) > 2
    unhidden = P.view_in(sim, P.perceiver_for(sim, 0, 1, PASSING, settings=dataclasses.replace(SETTINGS, occlusion=False)))
    assert len(unhidden.seen) > len(view.seen)
    render(view, "independent", PASSING, V2)


def test_an_arrived_agent_has_no_view():
    sim = AvoidanceSimulation(crowd("overtaking"))
    assert sim.run().status == "completed"
    with pytest.raises(ValueError, match="arrived"):
        P.view_in(sim, P.perceiver_for(sim, 0, 1, PASSING))


def test_resolve_v2_keeps_resolve_v1s_fixed_text_and_adds_only_lines():
    for condition in CONDITIONS:
        assert V1.system(condition, PASSING) == V2.system(condition, PASSING)
    one, two = V1.data["view"], V2.data["view"]
    assert {k: v for k, v in two.items() if k in one and k != "history_outcome"} == {k: v for k, v in one.items() if k != "history_outcome"}
    assert sorted(set(two) - set(one)) == ["heard_bands", "heard_directions", "heard_unseen_from", "history_back", "history_no_sideways", "history_sideways", "seen_short_signal"]
    assert two["history_outcome"] == {**one["history_outcome"], "replaced": "  You changed those steps at your next decision."}
    assert prompts.load_manifest()["resolve_v2"]["kind"] == "resolution"
    assert {k: V2.data[k] for k in ("conditions", "step_format", "event_item", "decision_point", "role", "system")} == {
        k: V1.data[k] for k in ("conditions", "step_format", "event_item", "decision_point", "role", "system")
    }


def test_nothing_in_the_avoidance_layer_imports_the_resolution_package():
    root = PACKAGE_ROOT / "negsim" / "avoidance"
    for path in sorted(Path(root).glob("*.py")):
        assert not re.search(r"negsim\.resolution|from \.\.resolution", path.read_text(encoding="utf-8")), path.name
