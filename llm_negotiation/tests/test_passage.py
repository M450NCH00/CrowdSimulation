"""Issue #32, Part 2: two people who meet inside a single-file passage.

The scenarios that start them there, their backing speeds, and (below) the back-up directive."""

from __future__ import annotations

import csv
import json
import math
import shutil

import pytest

from helpers import avoidance_config, crowd, static
from negsim.avoidance.perception import default_visibility
from negsim.avoidance.simulation import AvoidanceSimulation
from negsim.configutil import ConfigError
from negsim.experiment import AvoidanceExperiment, execute_avoidance_run
from negsim.experiment.avoidance import avoidance_summary_row, build_provider
from negsim.runlog import CONFIG_FILE, EVENTS_FILE, INTERACTIONS_FILE, OUTCOME_FILE, TRAJECTORY_FILE, validate_run_dir
from negsim.scenarios.crowd_base import DEFAULT_BACKING_SPEED

# --- the scenarios --------------------------------------------------------------------------------


@pytest.mark.parametrize("name, travelled", [("passage_meet_middle_v1", (1.7, 1.7)), ("passage_meet_with_speeds_v1", (2.0, 1.4))])
def test_the_two_start_inside_the_passage_where_they_meet(name, travelled):
    spec = crowd(name)
    assert spec.scenario_type == "passage_meeting" and len(spec.agents) == 2
    (segment,) = spec.single_file_segments
    assert (segment.rect.xmin, segment.rect.xmax, segment.width) == (-2.0, 2.0, 0.8)
    east, west = spec.agents
    assert east.start.x == pytest.approx(-2.0 + travelled[0]) and west.start.x == pytest.approx(2.0 - travelled[1])
    assert east.start.y == west.start.y == 0.0
    assert west.start.x - east.start.x - east.radius - west.radius == pytest.approx(0.1)  # at the meeting point, 0.1 m apart
    assert east.start.theta == pytest.approx(0.0) and abs(west.start.theta) == pytest.approx(3.141592653589793)  # facing each other
    for agent in (east, west):
        assert agent.path.points[0] == (agent.start.x, agent.start.y)  # the path starts where the agent is
        (stretch,) = agent.single_file_stretches
        assert stretch[1] == 0.0  # it starts inside the segment
    assert east.goal == (9.0, -0.4) and west.goal == (-9.0, 0.4)  # out of the far end, to its own side


def test_the_variants_are_set_by_the_distances_walked_in():
    asymmetric = crowd("passage_meet_middle_v1", geometry={"travelled": [2.7, 0.7]})
    east, west = asymmetric.agents
    assert (east.start.x, west.start.x) == (pytest.approx(0.7), pytest.approx(1.3))


def test_backing_speeds_and_the_slow_backer():
    middle = crowd("passage_meet_middle_v1")
    assert [agent.backing_speed_mps for agent in middle.agents] == [0.92, 0.92]
    speeds = crowd("passage_meet_with_speeds_v1")
    fast, slow = speeds.agents
    assert (fast.agent_type, fast.max_speed, fast.backing_speed_mps, fast.preferred_speed) == ("pedestrian", 2.0, 0.92, 1.3)
    assert (slow.agent_type, slow.max_speed, slow.backing_speed_mps, slow.preferred_speed) == ("slow_backer", 1.4, 0.43, 1.10)
    described = speeds.as_dict()
    assert described["agent_types"]["slow_backer"]["backing_speed"] == 0.43 and described["agents"][1]["backing_speed_mps"] == 0.43


def test_a_scenario_that_does_not_set_a_backing_speed_resolves_as_before():
    spec = crowd("corridor_to_bottleneck")
    described = spec.as_dict()
    assert "backing_speed" not in described["agent_types"]["pedestrian"] and "backing_speed_mps" not in described["agents"][0]
    assert spec.agents[0].backing_speed is None and spec.agents[0].backing_speed_mps == DEFAULT_BACKING_SPEED == 0.92
    slow = crowd("corridor_to_bottleneck", agent_types={"pedestrian": {"max_speed": 0.8, "preferred_speed": 0.7}})
    assert slow.agents[0].backing_speed_mps == 0.8  # never above its maximum speed


@pytest.mark.parametrize(
    "geometry, message",
    [
        ({"travelled": [4.0, 0.5]}, "outside the passage"),
        ({"travelled": [0.0, 1.0]}, "outside the passage"),
        ({"travelled": [2.5, 1.5]}, "add up to the passage's length"),
        ({"travelled": [1.9, 1.9]}, "overlap at their starting positions"),
        ({"travelled": [1.7]}, "a list of 2 numbers"),
        ({"passage_width": 1.75}, "passage_width must be less than approach_width"),
        ({"passage_width": 1.2}, "could pass each other"),
        ({"exit_setback": 0.5}, "merge_distance < exit_setback"),
    ],
)
def test_a_passage_that_cannot_be_is_refused(geometry, message):
    with pytest.raises(ConfigError, match=message):
        crowd("passage_meet_middle_v1", geometry=geometry)


def test_a_backing_speed_above_the_maximum_is_refused():
    with pytest.raises(ConfigError, match="backing_speed 2.5 exceeds max_speed 2.0"):
        crowd("passage_meet_middle_v1", agent_types={"pedestrian": {"backing_speed": 2.5}})


@pytest.mark.parametrize(
    "start, speeds",
    [(None, (0.0, 0.0)), (0.5, (0.5, 0.5)), ("preferred", (1.3, 1.1))],
)
def test_the_two_start_at_rest_unless_told_to_start_walking(start, speeds):
    geometry = {} if start is None else {"geometry": {"start_speed": start}}
    spec = crowd("passage_meet_with_speeds_v1", **geometry)
    assert tuple(agent.initial_speed for agent in spec.agents) == speeds
    world = spec.build_world()
    assert world.agents[0].velocity[0] == pytest.approx(speeds[0]) and world.agents[1].velocity[0] == pytest.approx(-speeds[1])


def test_a_start_speed_above_an_agents_maximum_is_refused():
    with pytest.raises(ConfigError, match="would start at 1.6 m/s, above its max_speed 1.4"):
        crowd("passage_meet_with_speeds_v1", geometry={"start_speed": 1.6})
    with pytest.raises(ConfigError, match="start_speed"):
        crowd("passage_meet_with_speeds_v1", geometry={"start_speed": "running"})


# --- the back-up directive and the manoeuvre (Parts 2.4 and 2.5) -----------------------------------


def back_up_run(name="passage_meet_middle_v1", backer=1, visibility=None, **overrides):
    """A run, unperturbed, in which ``backer`` is told to back up throughout (a static directive)."""
    fields = [{}, {}]
    fields[backer] = {"back_up": True}
    return AvoidanceSimulation(crowd(name, **overrides), static(*fields), visibility=visibility).run()


def seed_rule():
    return build_provider({"provider": "rules", "enable": {"passage_shorter_backs_out": 1}}, default_visibility(), "test")


def test_the_one_told_to_back_up_backs_out_waits_outside_and_goes_on_after_the_other():
    result = back_up_run()
    assert result.status == "completed" and result.collisions["agent_agent"] == 0
    (manoeuvre,) = result.back_ups  # one per pair interaction, though the directive holds throughout
    entry = manoeuvre.as_dict(0.1)
    assert (entry["backer"], entry["other"], entry["segment"], entry["end_reason"]) == (1, 0, "passage", "other_cleared")
    assert entry["travelled_m"] == pytest.approx(1.7) and entry["speed_mps"] == 0.92
    # Out of the east end by the two radii and the safety margin, on the centre line.
    assert entry["runout_m"] == pytest.approx(0.6) and entry["target_m"] == [pytest.approx(2.6), 0.0]
    # It backs the 1.7 m it walked in and the run-out, at its backing speed.
    assert entry["backing_distance_m"] == pytest.approx(1.7 + 0.6, abs=1e-3)
    assert entry["backing_time_s"] == pytest.approx((1.7 + 0.6) / 0.92, abs=0.1)
    assert (entry["start_time_s"], entry["out_time_s"]) == (0.0, pytest.approx(2.5)) and entry["waiting_time_s"] > 0.0
    assert entry["end_time_s"] == pytest.approx(entry["out_time_s"] + entry["waiting_time_s"])
    assert result.goal_times[0] < result.goal_times[1]  # the other went first


def test_while_one_backs_out_the_other_comes_on_no_faster_and_the_trajectory_says_who_does_what():
    result = back_up_run()
    rows = [row for row in result.trajectory if row["speed_mps"] is not None]
    backer = [row for row in rows if row["agent_id"] == 1]
    phases = [row["back_up"] for row in backer]
    assert phases[:25] == ["backing"] * 25 and "waiting" in phases and phases[-1] is None
    assert all(row["speed_mps"] == pytest.approx(0.92, abs=1e-6) for row in backer[:25])  # its own backing speed
    proceeding = [row for row in rows if row["agent_id"] == 0 and row["step"] < 25]
    assert all(row["back_up"] == "proceeding" and row["control_mode"] == "back_up" for row in proceeding)
    assert all(row["speed_mps"] <= 0.92 + 1e-6 for row in proceeding)  # at the backer's pace, not its own 1.3
    assert all(row["control_mode"] == "back_up" for row in backer if row["back_up"] is not None)


@pytest.mark.parametrize("backer, travelled, speed, steps", [(0, 2.0, 0.92, 29), (1, 1.4, 0.43, 47)])
def test_each_backs_at_its_own_backing_speed(backer, travelled, speed, steps):
    """passage_meet_with_speeds_v1: agent 1 has walked less far in but backs at 0.43 m/s."""
    (manoeuvre,) = back_up_run("passage_meet_with_speeds_v1", backer=backer).back_ups
    assert manoeuvre.speed_mps == speed and manoeuvre.travelled_m == pytest.approx(travelled)
    assert manoeuvre.backing_steps == steps == math.ceil(round((travelled + 0.6) / speed / 0.1, 9))


def test_backing_out_the_one_that_is_out_sooner_is_quicker_than_backing_out_the_one_that_walked_less():
    """docs/derivations.md, section 18: with these speeds the distance-optimal and the time-optimal
    choice differ, and the time-optimal one finishes first."""
    fast, slow = back_up_run("passage_meet_with_speeds_v1", backer=0), back_up_run("passage_meet_with_speeds_v1", backer=1)
    assert fast.status == slow.status == "completed"
    assert fast.back_ups[0].backing_distance_m > slow.back_ups[0].backing_distance_m  # it walks further back ...
    assert fast.sim_time_s < slow.sim_time_s - 2.0  # ... and the two are through sooner


def test_intentional_backing_is_never_the_artefact_and_the_artefact_is_still_counted():
    """Issue #26's walking-backwards artefact against issue #32's backing (docs/metrics.md, section 10)."""
    backed = back_up_run()
    assert backed.back_ups[0].backing_steps == 25  # 2.5 s backwards at 0.92 m/s: an artefact episode if it counted
    assert backed.artefacts["agents"]["1"]["backward_episodes"] == 0 and backed.artefacts["totals"]["backward_distance_m"] == 0.0
    # The arbiter's own way, when the two meet walking: no manoeuvre, and the follower is pushed
    # back by ORCA (shares 1 and 0) at nearly the leader's speed: the artefact.
    pushed = AvoidanceSimulation(crowd("passage_meet_middle_v1", geometry={"start_speed": "preferred"})).run()
    assert pushed.status == "completed" and pushed.back_ups == []
    follower = pushed.artefacts["agents"]["1"]
    assert follower["backward_episodes"] == 1 and follower["backward_time_s"] == pytest.approx(2.5)
    assert follower["backward_distance_m"] == pytest.approx(2.963, abs=0.01)


def test_the_artefact_distance_counts_only_within_its_episodes():
    from negsim.metrics.avoidance import EpisodeTracker

    tracker = EpisodeTracker(1.0)
    for step in range(5):  # 0.5 s: too short to be an episode
        tracker.update(step * 0.1, (step + 1) * 0.1, True, 0.1)
    tracker.update(0.5, 0.6, False)
    for step in range(10, 22):  # 1.2 s
        tracker.update(step * 0.1, (step + 1) * 0.1, True, 0.1)
    tracker.close()
    assert len(tracker.episodes) == 1 and tracker.total_amount == pytest.approx(1.2)


def test_the_arbiter_does_not_hold_a_pair_in_a_manoeuvre():
    """The seed rule ties when the two have walked in equally far, so the arbiter takes the pair;
    once its leader has crept 0.1 m in, the rule matches and the manoeuvre takes the pair from it."""
    result = AvoidanceSimulation(crowd("passage_meet_middle_v1"), seed_rule()).run()
    assert [(handoff.to, handoff.step) for handoff in result.handoffs] == [("arbiter", 0), ("back_up", 28)]
    (manoeuvre,) = result.back_ups
    assert (manoeuvre.backer, manoeuvre.start_step) == (1, 28) and result.status == "completed"
    arbiter_rows = [row for row in result.trajectory if row["control_mode"] == "arbiter"]
    assert arbiter_rows and max(row["step"] for row in arbiter_rows) < 28


def test_a_manoeuvre_ends_as_the_arbiters_zone_clears_so_the_arbiter_never_takes_the_pair_then():
    """Measured along the passage's axis with a 1 mm tolerance, a manoeuvre could end a step before
    the arbiter's conflict zone was clear, and the arbiter then held the pair for that step: this
    run of the behaviour checks did (docs/derivations.md, section 17)."""
    from negsim.configutil import PACKAGE_ROOT, load_yaml
    from negsim.scenarios.registry import build_crowd_scenario

    raw = load_yaml(PACKAGE_ROOT / "configs" / "rule_following" / "si32_passage_meet_with_speeds.yaml")
    (plan,) = [plan for plan in AvoidanceExperiment(raw, source="<test>").plans() if plan.run_id == "104_asymmetric_walking_seed_rule_r4"]
    simulation = AvoidanceSimulation(
        build_crowd_scenario(plan.scenario_config), provider=plan.provider(), visibility=plan.visibility,
        arbitration=plan.arbitration, share_policy=plan.share_policy, seed=plan.seed, perturbation=plan.perturbation,
    )
    result = simulation.run()
    (manoeuvre,) = result.back_ups
    assert (manoeuvre.backer, manoeuvre.end_reason) == (1, "other_cleared") and result.handoffs == []  # it had two
    (exit_s,) = [exit_s for _, _, exit_s in simulation.world.agents[0].spec.single_file_stretches]
    progress = {row["step"]: row["path_s_m"] for row in result.trajectory if row["agent_id"] == 0}
    clear = exit_s + manoeuvre.runout_m
    assert progress[manoeuvre.end_step - 1] < clear <= progress[manoeuvre.end_step]


def test_the_seed_rule_backs_out_the_one_that_has_walked_less_far_in():
    result = AvoidanceSimulation(crowd("passage_meet_middle_v1", geometry={"travelled": [2.7, 0.7]}), seed_rule()).run()
    (manoeuvre,) = result.back_ups
    assert (manoeuvre.backer, manoeuvre.start_step, manoeuvre.travelled_m) == (1, 0, pytest.approx(0.7))
    (match,) = result.pairs[0].provider_record.as_dict()["matches"]
    assert (match["rule_id"], match["roles"]) == ("passage_shorter_backs_out", {"0": "goes_on", "1": "backs_out"})
    assert result.handoffs == [] and result.status == "completed"


def test_back_up_does_nothing_outside_a_passage_the_two_meet_in():
    # In open space it changes nothing at all.
    offsets = {"geometry": {"lateral_offsets": [0.05, -0.05]}}
    plain = AvoidanceSimulation(crowd("wide_corridor_head_on", **offsets)).run()
    told = AvoidanceSimulation(crowd("wide_corridor_head_on", **offsets), static({}, {"back_up": True})).run()
    assert told.back_ups == []
    assert [(row["x_m"], row["y_m"]) for row in told.trajectory] == [(row["x_m"], row["y_m"]) for row in plain.trajectory]
    # Before a single-file segment it names the other as the one to go first, and the arbiter
    # holds the one told to back up at the mouth: it never has to back out.
    result = AvoidanceSimulation(crowd("corridor_to_bottleneck"), static({}, {"back_up": True})).run()
    assert result.back_ups == [] and result.status == "completed"
    first = result.handoffs[0]
    assert (first.to, first.leader, first.role_source) == ("arbiter", 0, "negotiated")


def test_back_up_needs_the_other_ahead_of_it():
    simulation = AvoidanceSimulation(crowd("passage_meet_middle_v1"))
    a, b = simulation.world.agents
    assert simulation._meeting_segment(1, 0)[1] == 1.0  # agent 1 backs east, away from agent 0
    assert simulation._meeting_segment(0, 1)[1] == -1.0
    b.pose = type(b.pose)(-1.5, 0.0, b.pose.theta)  # agent 1 now west of agent 0, still facing west: 0 is behind it
    assert simulation._meeting_segment(1, 0) is None
    a.pose = type(a.pose)(-5.0, 0.0, a.pose.theta)  # agent 0 out of the passage, in the wide part
    assert simulation._meeting_segment(0, 1) is None


def test_what_the_agents_can_see_does_not_change_the_manoeuvre():
    hidden = {**default_visibility(), "speed": False, "size": False}
    seen, unseen = back_up_run(), back_up_run(visibility=hidden)
    assert [m.as_dict(0.1) for m in seen.back_ups] == [m.as_dict(0.1) for m in unseen.back_ups]


# --- what a run logs (log schema version 5) ----------------------------------------------------------

GIT = {"commit": "abc123", "dirty": False}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.fixture()
def backed_run(tmp_path):
    """The seed rule in the asymmetric meeting, under the primary baseline, logged to disk."""
    config = avoidance_config(
        experiment_name="test_passage",
        scenario="configs/scenarios/passage_meet_middle_v1.yaml",
        scenario_overrides={"geometry": {"travelled": [2.7, 0.7]}},
        baseline="orca_perturbed_v1",
        directives={"provider": "rules", "enable": {"passage_shorter_backs_out": 1}},
    )
    plan = AvoidanceExperiment(config, source="<test>").plans()[0]
    run_dir = tmp_path / "experiment" / "run"
    return run_dir, execute_avoidance_run(plan, run_dir, GIT), config


def test_a_run_with_a_manoeuvre_logs_it_everywhere_and_passes_the_schema_check(backed_run):
    run_dir, outcome, _ = backed_run
    assert validate_run_dir(run_dir) == [] and outcome["log_schema_version"] == 5 and outcome["status"] == "completed"
    block = outcome["back_up"]
    (manoeuvre,) = block["manoeuvres"]
    assert (manoeuvre["backer"], manoeuvre["other"], manoeuvre["end_reason"]) == (1, 0, "other_cleared")
    assert block["agents"] == {
        "1": {
            "manoeuvres": 1, "backing_time_s": manoeuvre["backing_time_s"], "waiting_time_s": manoeuvre["waiting_time_s"],
            "backing_distance_m": manoeuvre["backing_distance_m"],
        }
    }
    assert block["totals"]["manoeuvres"] == 1 and block["totals"]["backing_distance_m"] == pytest.approx(1.375, abs=0.01)
    events = [event for event in read_jsonl(run_dir / EVENTS_FILE) if event["type"] == "back_up"]
    assert [event["phase"] for event in events] == ["started", "out", "ended"]
    assert events[0]["travelled_m"] == pytest.approx(0.7) and events[-1]["reason"] == "other_cleared"
    with (run_dir / TRAJECTORY_FILE).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert {row["back_up"] for row in rows} == {"backing", "waiting", "proceeding", ""}
    assert all(row["control_mode"] == "back_up" for row in rows if row["back_up"])
    # Each agent's directive, from the rule as it evaluates it on its own record: the backer's backs up.
    directives = {entry["observer_id"]: entry["directive"]["back_up"] for entry in read_jsonl(run_dir / INTERACTIONS_FILE)}
    assert directives == {0: False, 1: True}
    # Both start inside the passage, so both "enter" it on the first step and first_through
    # cannot say who got through first; first_out, from when each came out at the far end, can.
    (segment,) = outcome["single_file"]
    assert segment["entry_time_s"] == {"0": 0.1, "1": 0.1} and segment["first_through"] is None
    assert segment["first_out"] == 0 and segment["exit_time_s"]["0"] < segment["exit_time_s"]["1"]
    row = avoidance_summary_row(json.loads((run_dir / CONFIG_FILE).read_text(encoding="utf-8")), outcome)
    assert (row["back_up_manoeuvres"], row["backing_distance_m"]) == (1, block["totals"]["backing_distance_m"])
    assert row["backward_distance_m"] == outcome["artefacts"]["totals"]["backward_distance_m"]
    assert (row["first_through"], row["first_out"]) == (None, 0)


def test_the_schema_check_notices_a_manoeuvre_that_does_not_add_up(backed_run, tmp_path):
    run_dir = backed_run[0]
    for damage in ("event", "block", "reason", "exit", "column"):
        copy = tmp_path / damage
        shutil.copytree(run_dir, copy)
        if damage == "event":
            kept = [event for event in read_jsonl(copy / EVENTS_FILE) if not (event["type"] == "back_up" and event["phase"] == "out")]
            for index, event in enumerate(kept):
                event["event_index"] = index
            (copy / EVENTS_FILE).write_text("".join(json.dumps(event) + "\n" for event in kept), encoding="utf-8")
        elif damage in ("block", "reason", "exit"):
            outcome = json.loads((copy / OUTCOME_FILE).read_text(encoding="utf-8"))
            if damage == "block":
                del outcome["back_up"]["totals"]
            elif damage == "exit":
                del outcome["single_file"][0]["first_out"]
            else:
                outcome["back_up"]["manoeuvres"][0]["end_reason"] = "gave_up"
            (copy / OUTCOME_FILE).write_text(json.dumps(outcome), encoding="utf-8")
        else:
            text = (copy / TRAJECTORY_FILE).read_text(encoding="utf-8")
            (copy / TRAJECTORY_FILE).write_text(text.replace(",back_up\n", ",back_out\n", 1), encoding="utf-8")
        assert validate_run_dir(copy) != [], damage


def test_the_viewer_shows_who_backs_out_and_when(backed_run):
    from negsim.viz import viewer

    run = viewer.load_run(backed_run[0])
    assert run["back_ups"] == 1 and any(label == "Backing out of a passage" for label, _ in run["summary"])
    backer, other = run["agents"][1], run["agents"][0]
    assert any(flags & viewer.FLAG_BACKING for flags in backer["f"]) and any(flags & viewer.FLAG_WAITING for flags in backer["f"])
    assert any(flags & viewer.FLAG_PROCEEDING for flags in other["f"]) and not any(flags & viewer.FLAG_BACKING for flags in other["f"])
    texts = [event["text"] for event in run["events"] if event["type"] == "back_up"]
    assert texts[0] == "Agent 1 starts to back out of the passage for agent 0, having walked 0.7 m in"
    assert texts[1] == "Agent 1 is out of the passage and waits for agent 0" and texts[2] == "Agent 1 goes on (other cleared)"
