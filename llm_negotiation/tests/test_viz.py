"""The pictures: the trajectory plot of both kinds of run, and the animated viewer.

What is tested here is everything Python puts into the viewer, read from committed run
folders, and that nothing in a log can break out of the page. That the page itself draws
every run without an error was checked in a headless browser when it was written
(WORK_LOG-26.md); a test that needs a browser would not run everywhere.
"""

from __future__ import annotations

import csv
import json
import re
import shutil

import pytest

from negsim.configutil import PACKAGE_ROOT, REPO_ROOT
from negsim.viz import viewer

RUNS = PACKAGE_ROOT / "runs"
HEAD_ON = RUNS / "si1_head_on_side_preference"
BOTTLENECK = RUNS / "si1_bottleneck_handoff" / "001_opposing_no_directive"
FLOW = RUNS / "si1_bidirectional_flow" / "001_limit_10"
DOORWAY = RUNS / "c1_smoke" / "001_hospital-vs-airport_fs0"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def embedded(html: str) -> dict:
    """The data the page holds, found the way a browser finds the end of the element."""
    match = re.search(r'<script id="run-data" type="application/json">(.*?)</script>', html, re.S)
    assert match, "the data block is missing"
    return json.loads(match.group(1))


def build(tmp_path, *paths):
    output = viewer.build_viewer(paths, tmp_path / "view.html")
    html = output.read_text(encoding="utf-8")
    return html, embedded(html)


# --- the plot -----------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "run_dir", [HEAD_ON / "003_symmetric_both_left", BOTTLENECK, FLOW], ids=["two_agents", "bottleneck", "crowd"]
)
def test_the_plot_draws_an_avoidance_run(run_dir, tmp_path):
    pytest.importorskip("matplotlib")
    from negsim.viz.trajectory_plot import plot_run

    before = sorted(path.name for path in run_dir.iterdir())
    image = plot_run(run_dir, tmp_path / "plot.png")
    assert image.is_file() and image.stat().st_size > 5000
    assert sorted(path.name for path in run_dir.iterdir()) == before  # nothing added to the logs


def test_the_plot_title_says_how_an_avoidance_run_ended():
    from negsim.viz.trajectory_plot import _title

    assert _title(read_json(FLOW / "config.json"), read_json(FLOW / "outcome.json")) == (
        "001_limit_10: completed, 100 of 100 arrived, 512 collision episodes"
    )
    assert _title(read_json(BOTTLENECK / "config.json"), read_json(BOTTLENECK / "outcome.json")).endswith(
        "first through: agent 0"
    )


# --- the viewer: what goes into it ------------------------------------------------------------------


def test_an_experiment_folder_gives_one_viewer_with_every_run(tmp_path):
    _, data = build(tmp_path, HEAD_ON)
    folders = sorted(path.name for path in HEAD_ON.iterdir() if (path / "config.json").is_file())
    assert [run["run_id"] for run in data["runs"]] == folders
    assert all(run["kind"] == "avoidance" and len(run["agents"]) == 2 for run in data["runs"])
    # The personas of this experiment are shown with the agents; nothing physical changes.
    assert any("f25" in value for _, value in data["runs"][0]["agents"][0]["details"])


def test_every_track_runs_forward_in_time_from_the_start(tmp_path):
    _, data = build(tmp_path, HEAD_ON, FLOW, DOORWAY)
    assert len(data["runs"]) == 16
    for run in data["runs"]:
        for agent in run["agents"]:
            times = agent["t"]
            assert times[0] == 0.0
            assert all(later > earlier for earlier, later in zip(times, times[1:])), (run["key"], agent["id"])
            assert {len(agent[key]) for key in ("t", "x", "y", "h", "vx", "vy", "wx", "wy", "f", "n")} == {len(times)}
            assert times[-1] <= run["end_time"] + 1e-9


def test_an_avoidance_agent_stops_where_and_when_it_arrived(tmp_path):
    run_dir = HEAD_ON / "003_symmetric_both_left"
    _, data = build(tmp_path, run_dir)
    outcome = read_json(run_dir / "outcome.json")
    with (run_dir / "trajectory.csv").open(encoding="utf-8", newline="") as handle:
        final = {row["agent_id"]: row for row in csv.DictReader(handle) if row["speed_mps"] == ""}
    for agent in data["runs"][0]["agents"]:
        arrival = outcome["time_to_goal_s"][str(agent["id"])]
        assert agent["arrival"] == arrival and agent["t"][-1] == pytest.approx(arrival)
        end = final[str(agent["id"])]
        assert (agent["x"][-1], agent["y"][-1]) == pytest.approx((float(end["x_m"]), float(end["y_m"])), abs=1e-4)
        assert agent["leaves"] is True  # an avoidance agent leaves the scene when it arrives


def test_an_agent_that_never_arrives_is_shown_to_the_end(tmp_path):
    _, data = build(tmp_path, HEAD_ON / "001_symmetric_plain")
    run = data["runs"][0]
    assert run["status"] == "deadlock"
    assert all(agent["arrival"] is None and agent["t"][-1] == pytest.approx(run["end_time"]) for agent in run["agents"])


def test_a_thinned_log_is_marked_as_interpolated(tmp_path):
    _, data = build(tmp_path, FLOW)
    run = data["runs"][0]
    assert run["stride"] == 10
    assert any("interpolated" in value for _, value in run["summary"])
    for agent in run["agents"]:
        logged = agent["t"][:-1]  # the last sample is the arrival
        assert all(abs(t - round(t)) < 1e-6 for t in logged)  # every tenth step of 0.1 s


def test_the_flags_follow_the_trajectory(tmp_path):
    _, data = build(tmp_path, BOTTLENECK)
    flags = data["flags"]
    assert sorted(flags.values()) == [1, 2, 4, 8, 16, 32, 64]
    with (BOTTLENECK / "trajectory.csv").open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["speed_mps"] != ""]
    seen = set()
    for agent in data["runs"][0]["agents"]:
        mine = [row for row in rows if int(row["agent_id"]) == agent["id"]]
        assert len(mine) == len(agent["f"]) - 1  # one sample per logged step, and the arrival
        for row, value in zip(mine, agent["f"]):
            assert bool(value & flags["arbiter"]) == (row["control_mode"] == "arbiter")
            assert bool(value & flags["exposed"]) == (row["exposed"] == "true")
            assert bool(value & flags["fallback"]) == (row["fallback"] == "true")
            assert bool(value & flags["leader"]) == (row["role"] == "leader")
            assert bool(value & flags["follower"]) == (row["role"] == "follower")
            seen.add(value)
    assert any(value & flags["arbiter"] for value in seen) and any(value & flags["exposed"] for value in seen)


def test_every_logged_event_is_in_the_viewer(tmp_path):
    for run_dir, arrivals in ((BOTTLENECK, 2), (FLOW, 0)):  # arrivals are listed for two agents, not a crowd
        _, data = build(tmp_path, run_dir)
        events = data["runs"][0]["events"]
        logged = read_jsonl(run_dir / "events.jsonl")
        shown = [event for event in events if event["type"] != "arrival"]
        assert sorted((e["type"], e["t"]) for e in shown) == sorted((e["type"], e["time_s"]) for e in logged)
        assert sum(event["type"] == "arrival" for event in events) == arrivals
        assert all(event["text"] for event in events)
        assert [event["t"] for event in events] == sorted(event["t"] for event in events)


def test_a_negotiation_run_shows_its_conversation_and_roles(tmp_path):
    _, data = build(tmp_path, DOORWAY)
    run = data["runs"][0]
    assert run["kind"] == "negotiation" and run["dt"] == 0.2 and run["stride"] == 1
    turns = read_jsonl(DOORWAY / "conversation.jsonl")
    assert [(t["speaker"], t["stance"], t["message"]) for t in run["conversation"]] == [
        (t["speaker"], t["stance"], t["message"]) for t in turns
    ]
    leader = data["flags"]["leader"]
    assert any(value & leader for value in run["agents"][0]["f"])  # agent 0 led, as the outcome says
    assert all(agent["leaves"] is False for agent in run["agents"])  # issue #24's agents stay where they arrive


def test_nothing_in_a_log_can_break_out_of_the_page(tmp_path):
    """An LLM's message is text from outside. It must not be able to close the element that
    holds the data and run as code; it must come back out exactly as it went in."""
    copy = tmp_path / "experiment" / DOORWAY.name
    shutil.copytree(DOORWAY, copy)
    turns = read_jsonl(copy / "conversation.jsonl")
    hostile = "</script><script>document.title='pwned'</script><!-- &   </SCRIPT>"
    turns[0]["message"] = hostile
    (copy / "conversation.jsonl").write_text("".join(json.dumps(turn) + "\n" for turn in turns), encoding="utf-8")
    html, data = build(tmp_path, copy)
    assert data["runs"][0]["conversation"][0]["message"] == hostile
    block = html.split('<script id="run-data" type="application/json">', 1)[1].split("</script>", 1)[0]
    assert "<" not in block


def test_the_page_needs_nothing_from_the_network(tmp_path):
    html, _ = build(tmp_path, BOTTLENECK)
    assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", html)
    assert "fetch(" not in html and "XMLHttpRequest" not in html and "import(" not in html


def test_the_template_has_one_place_for_the_data_and_one_for_the_title():
    template = viewer.TEMPLATE.read_text(encoding="utf-8")
    assert template.count(viewer.DATA_PLACEHOLDER) == 1 and template.count(viewer.TITLE_PLACEHOLDER) == 1


# --- the viewer: the command line -----------------------------------------------------------------------


def test_the_command_line_writes_the_viewer_and_reports_where(tmp_path, capsys):
    output = tmp_path / "out" / "view.html"
    assert viewer.main([str(BOTTLENECK), "--out", str(output), "--no-open"]) == 0
    assert output.is_file() and str(output.resolve()) in capsys.readouterr().out


def test_the_command_line_refuses_a_folder_with_no_runs(tmp_path, capsys):
    assert viewer.main([str(tmp_path), "--no-open"]) == 2
    assert "not a run folder" in capsys.readouterr().err


def test_without_out_the_viewer_goes_to_a_folder_git_ignores():
    assert viewer.default_output([BOTTLENECK]) == viewer.VIEWS_DIR / "si1_bottleneck_handoff__001_opposing_no_directive.html"
    assert viewer.default_output([HEAD_ON]) == viewer.VIEWS_DIR / "si1_head_on_side_preference.html"
    ignored = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "llm_negotiation/views/" in ignored
    assert "llm_negotiation/runs/**/trajectory.png" in ignored  # nor does the plot's default image get committed
