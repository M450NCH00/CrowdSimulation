"""The viewer on the replay of a resolution session (issue #96): the LLM's decisions, each
agent's factors and what it could see, read from the session record beside the replay.

Built on a mock experiment, so no paid call is made. As in ``test_viz.py``, what is tested is
what Python puts into the page; that the page draws it was checked in a headless browser when
it was written (``WORK_LOG-96.md``).
"""

from __future__ import annotations

import json
import shutil

import pytest

from negsim.llm.mock import MockClient
from negsim.resolution import experiment as E
from negsim.viz import viewer
from test_encounter_protocol import GIT, SWERVE_LEFT, policy, reply, small_config

#: Says something, signals, and turns to its left; its words try to close the page's data block.
TALKER = reply(
    "Let them by </script><script>alert(1)</script>",
    [{"start": {"at_distance_m": 4}, "speed_mps": 1.0, "turn": {"to": "left", "degrees": 20}, "until": "other_passes"}],
    message="After you!", signal="wave_on",
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def experiment(tmp_path_factory):
    out = tmp_path_factory.mktemp("viewer_resolution")
    config = small_config("viewer_talk", conditions=("talk",))
    client = MockClient(policy=policy({0: TALKER, 1: SWERVE_LEFT}))
    E.run_resolution(config, client=client, out_root=out, report=lambda _: None, git=GIT)
    return out / "viewer_talk"


@pytest.fixture(scope="module")
def session(experiment):
    path = next((experiment / "sessions").glob("*.json"))
    return read_json(path)


def page(tmp_path, *paths):
    html = viewer.build_viewer(paths, tmp_path / "view.html").read_text(encoding="utf-8")
    start = html.index('<script id="run-data" type="application/json">') + len('<script id="run-data" type="application/json">')
    return html, json.loads(html[start:html.index("</script>", start)])


@pytest.mark.parametrize("mode", ["plan_only", "plan_orca"])
def test_a_replay_finds_its_session_and_shows_every_decision_point(experiment, session, tmp_path, mode):
    replay = experiment / session["replays"][mode].replace("\\", "/")
    _, data = page(tmp_path, replay)
    run = data["runs"][0]
    llm = run["llm"]
    assert llm["session_id"] == session["session_id"] and llm["condition"] == "talk" and llm["mode"] == mode
    assert len(llm["decisions"]) == len(session["decision_points"]) > 0
    first = next(d for d in llm["decisions"] if d["agent"] == 0)
    point = next(p for p in session["decision_points"] if p["agent_id"] == 0)
    assert first["t"] == point["time_s"] and first["intent"] == point["parsed"]["intent"]
    assert first["steps"] == ["from 4 m away: walk at 1 m/s 20° to the left until the other has passed"]
    assert first["signal"] == "waves the other on" and first["message"] == "After you!" and first["why"] == "the encounter begins"
    assert first["cap"] == session["max_decision_points_per_agent"] and first["distance_m"] is not None
    # When each step ran comes from the replay's own driver, for this mode.
    played = read_json(replay / "outcome.json")["plans"]["driver"]["decisions"]
    entry = next(e for e in played if e["agent_id"] == 0 and e["decision_point"] == first["number"])
    assert [span for span in first["step_times"] if span] == [[s["start_time_s"], s["end_time_s"]] for s in entry["step_records"]]


def test_the_view_is_the_sessions_and_every_decision_signal_and_message_is_an_event(experiment, session, tmp_path):
    _, data = page(tmp_path, experiment / session["replays"]["plan_only"].replace("\\", "/"))
    run = data["runs"][0]
    view = session["llm_view"]
    assert run["llm"]["view"] == {key: view[key] for key in ("half_angle_deg", "range_m", "detail_range_m", "hearing_range_m", "walls_block_sight")}
    kinds = [event["type"] for event in run["events"]]
    assert kinds.count("decision") == len(session["decision_points"])
    assert kinds.count("signal") == len(session["signals"]) > 0
    assert kinds.count("message") == len(session["utterances"]) > 0
    assert [turn["message"] for turn in run["conversation"]] == [said["message"] for said in session["utterances"]]
    assert [event["t"] for event in run["events"]] == sorted(event["t"] for event in run["events"])


def test_clicking_an_agent_shows_its_factors(experiment, session, tmp_path):
    _, data = page(tmp_path, experiment / session["replays"]["plan_only"].replace("\\", "/"))
    details = {agent["id"]: dict(agent["details"]) for agent in data["runs"][0]["agents"]}
    person = session["session"]["personas"]["0"]
    assert details[0]["Age"] == str(person["age"]) and details[0]["Gender"] == person["gender"]
    assert details[0]["Body width"].startswith("0.5 m") and "Persona" not in details[0]
    assert details[0]["Debrief"] and "The other may be shown" in details[0]


def test_nothing_an_agent_says_can_break_out_of_the_page(experiment, session, tmp_path):
    html, data = page(tmp_path, experiment / session["replays"]["plan_only"].replace("\\", "/"))
    assert "<script>alert(1)" not in html
    assert any("</script><script>alert(1)" in d["intent"] for d in data["runs"][0]["llm"]["decisions"])


def test_a_replay_without_its_record_is_shown_as_before(experiment, session, tmp_path):
    copy = tmp_path / "elsewhere" / "plan_only"
    shutil.copytree(experiment / session["replays"]["plan_only"].replace("\\", "/"), copy)
    run = viewer.load_run(copy)
    assert "llm" not in run and not any(event["type"] in ("decision", "signal", "message") for event in run["events"])
    assert dict(run["agents"][0]["details"])["Persona"] == "none"


@pytest.mark.parametrize(
    ("step", "words"),
    [
        ({"start": "now", "speed_mps": 0.6, "until": {"seconds": 2}}, "walk at 0.6 m/s for 2 s"),
        ({"speed_mps": 0, "until": "other_stops"}, "stand still until the other stops"),
        ({"start": {"after_seconds": 1.5}, "back_up_m": 1.0}, "after 1.5 s: walk backwards 1 m"),
        ({"start": "other_passes", "speed_mps": 1.3, "until": {"at_distance_m": 2}}, "once the other has passed: walk at 1.3 m/s until 2 m away"),
        ({"turn": {"to": "right", "degrees": 15}, "until": "i_am_out_of_the_stretch"}, "15° to the right until out of the narrow stretch"),
        ({}, "carry on"),
    ],
)
def test_a_step_in_words(step, words):
    assert viewer.step_text(step) == words


def test_why_a_decision_point_fired_in_words():
    assert viewer._why(["trigger", "perceives:1"]) == "the encounter begins"
    assert viewer._why(["other_moved_left:1", "signalled:1", "plan_failing"]) == "agent 1 moved left, agent 1 signalled, its plan is failing"
