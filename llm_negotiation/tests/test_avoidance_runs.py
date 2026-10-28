"""Avoidance experiments end to end: the config and its design, the log folder of a run,
the schema check, the summary, the command line, and the guarantee that nothing is spent.
Everything is written under pytest's temporary folder."""

from __future__ import annotations

import csv
import json
import re
import shutil

import pytest

from negsim.experiment import cli
from helpers import BOTTLENECK, avoidance_config, c1_config, experiment
from negsim.avoidance.directives import DIRECTIVE_FIELDS
from negsim.avoidance.perception import PERCEPTION_FIELDS, PERCEPTION_SCHEMA_VERSION
from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.experiment import (
    AvoidanceExperiment,
    execute_avoidance_run,
    execute_run,
    is_avoidance_config,
    run_avoidance_experiment,
)
from negsim.llm import MockClient
from negsim.runlog import (
    AVOIDANCE_AGENT_KEYS,
    AVOIDANCE_OUTCOME_KEYS,
    AVOIDANCE_RUN_FILES,
    AVOIDANCE_SUMMARY_COLUMNS,
    AVOIDANCE_TRAJECTORY_COLUMNS,
    CONFIG_FILE,
    EVENTS_FILE,
    INTERACTIONS_FILE,
    LOG_SCHEMA_VERSION,
    OUTCOME_FILE,
    RUN_FILES,
    SUMMARY_FILE,
    TRAJECTORY_FILE,
    validate_run_dir,
)

CONFIG_DIR = PACKAGE_ROOT / "configs" / "avoidance"
SHIPPED = sorted(path.name for path in CONFIG_DIR.glob("*.yaml"))
QUIET = lambda line: None
GIT = {"commit": "abc123", "dirty": False}
TASK = "the supermarket to buy groceries"  # the task of every shipped persona
PERSONAS = "configs/personas/personas.yaml"
OFFSET = {"geometry": {"lateral_offsets": [0.05, -0.05]}}


def avoidance(**changes) -> AvoidanceExperiment:
    return AvoidanceExperiment(avoidance_config(**changes), source="<test>")


def run_one(tmp_path, name="run", **changes):
    plan = avoidance(**changes).plans()[0]
    run_dir = tmp_path / name
    return run_dir, execute_avoidance_run(plan, run_dir, GIT)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


# --- the config and its design ------------------------------------------------------------------


def test_an_avoidance_config_is_told_apart_by_its_layer():
    assert is_avoidance_config(avoidance_config()) and not is_avoidance_config(c1_config())
    assert not is_avoidance_config(None) and not is_avoidance_config({"layer": "negotiation"})
    with pytest.raises(ConfigError, match="missing required key"):
        experiment(avoidance_config())  # the negotiation loader does not take it for one of its own


def test_the_smallest_experiment_is_one_plain_orca_run():
    (plan,) = avoidance().plans()
    assert (plan.index, plan.run_id, plan.seed, plan.repeat, plan.variant) == (1, "001_base", 301, 1, {})
    assert plan.directives == {} and plan.provider().name == "null" and plan.share_policy == "proportional"
    assert plan.arbitration.enabled and plan.population == {} and plan.attributes() == {}
    assert plan.visibility == {  # ethnic_group: issue #32, off by default
        "age": True, "gender": True, "backstory": False, "task": False, "ethnic_group": False, "speed": True, "size": True,
    }
    assert plan.logging == {"trajectory_stride": 1, "interactions": True}


def test_factors_are_crossed_in_order_and_each_level_lays_its_settings_on_the_base():
    config = avoidance(
        directives={"provider": "static", "default": {"clearance_margin": 0.1}},
        design={
            "seed": 500,
            "factors": {
                "layout": [{"name": "symmetric"}, {"name": "offset", "scenario_overrides": OFFSET}],
                "side": [
                    {"name": "none"},
                    {"name": "left", "directives": {"default": {"side_preference": "left"}}},
                    {"name": "off", "arbitration": {"enabled": False}, "visibility": {"age": False}},
                ],
            },
        },
    )
    plans = config.plans()
    assert [plan.run_id for plan in plans] == [
        "001_symmetric_none", "002_symmetric_left", "003_symmetric_off",
        "004_offset_none", "005_offset_left", "006_offset_off",
    ]
    assert [plan.seed for plan in plans] == [501] * 6  # paired seeds since issue #30; 501 to 506 per run before
    assert plans[4].variant == {"layout": "offset", "side": "left"}
    assert plans[4].scenario_config["geometry"]["lateral_offsets"] == [0.05, -0.05]
    assert plans[4].scenario_config["geometry"]["width"] == 1.75  # the rest of the scenario is kept
    assert plans[0].scenario_config["geometry"]["lateral_offsets"] == [0.0, 0.0]
    # A level's directives are merged into the base block, not put in its place.
    assert plans[4].directives == {"provider": "static", "default": {"clearance_margin": 0.1, "side_preference": "left"}}
    assert plans[3].directives == {"provider": "static", "default": {"clearance_margin": 0.1}}
    assert [plan.arbitration.enabled for plan in plans] == [True, True, False, True, True, False]
    assert plans[2].visibility["age"] is False and plans[1].visibility["age"] is True


def test_repeats_get_their_own_scenario_seed():
    plans = avoidance(scenario="configs/scenarios/bidirectional_flow.yaml", design={"repeats": 3}).plans()
    assert [plan.run_id for plan in plans] == ["001_base_r1", "002_base_r2", "003_base_r3"]
    assert [plan.scenario_config["seed"] for plan in plans] == [26, 27, 28]


def test_population_attaches_personas_by_group_and_by_agent():
    config = avoidance(
        personas=PERSONAS,
        population={"groups": {"eastbound": {"persona": "f25"}}, "agents": {1: {"persona": "m70", "age": 81}}},
    )
    population = config.plans()[0].population
    assert population[0] == {"persona_id": "f25", "attributes": {"age": 25, "gender": "female", "backstory": "", "task": TASK}}
    assert population[1]["persona_id"] == "m70+age=81" and population[1]["attributes"]["age"] == 81
    assert config.plans()[0].attributes()[1]["gender"] == "male"


@pytest.mark.parametrize("name, runs", [
    ("si1_bidirectional_flow.yaml", 2), ("si1_bottleneck_handoff.yaml", 8), ("si1_head_on_responsibility.yaml", 12),
    ("si1_head_on_side_preference.yaml", 14), ("si1_open_crossing.yaml", 4), ("si1_overtaking.yaml", 6),
])
def test_every_shipped_avoidance_config_loads(name, runs):
    config = AvoidanceExperiment.load(CONFIG_DIR / name)
    assert len(config.plans()) == runs and config.experiment_name == name[: -len(".yaml")]
    assert len({plan.run_id for plan in config.plans()}) == runs


def test_the_shipped_configs_are_the_six_and_live_apart_from_the_negotiation_ones():
    assert SHIPPED == [
        "si1_bidirectional_flow.yaml", "si1_bottleneck_handoff.yaml", "si1_head_on_responsibility.yaml",
        "si1_head_on_side_preference.yaml", "si1_open_crossing.yaml", "si1_overtaking.yaml",
    ]
    negotiation = sorted(path.name for path in (PACKAGE_ROOT / "configs" / "experiments").glob("*.yaml"))
    assert len(negotiation) == 10 and not set(negotiation) & set(SHIPPED)  # issue #24's ten, untouched


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"layer": "negotiation"}, "expected 'avoidance'"),
        ({"experiment_name": "has spaces"}, "letters, digits"),
        ({"schema_version": 9}, "schema_version"),
        ({"condition": "C0"}, "unknown key"),
        ({"scenario": "configs/scenarios/nowhere.yaml"}, "not found"),
        ({"scenario": "configs/scenarios/hallway.yaml"}, "two-agent scenario of issue #24"),
        ({"scenario_overrides": {"geometry": {"width": 0.9}}}, "cannot pass in a corridor"),
        ({"design": {"factors": {"layout": []}}}, "non-empty list of levels"),
        ({"design": {"factors": {"layout": [{"name": "a"}, {"name": "a"}]}}}, "same name"),
        ({"design": {"factors": {"layout": [{"name": "a", "speed": 2}]}}}, "unknown key"),
        ({"design": {"factors": {"layout": [{"scenario_overrides": {}}]}}}, "missing required key"),
        ({"design": {"repeats": 0}}, "must be at least 1"),
        ({"design": {"pairs": []}}, "unknown key"),
        ({"directives": {"provider": "static", "agents": {2: {"side_preference": "left"}}}}, "do not exist"),
        ({"directives": {"provider": "static", "pairs": [{"observer": 0, "neighbour": 5}]}}, "do not exist"),
        ({"directives": {"provider": "static", "default": {"side_preference": "up"}}}, "expected one of"),
        ({"directives": {"share_policy": "winner"}}, "expected one of"),
        ({"directives": {"provider": "null", "default": {"speed_scale": 0.5}}}, "takes no directives"),
        ({"arbitration": {"policy": "coin"}}, "expected one of"),
        ({"arbitration": {"leader": 0}}, "unknown key"),
        ({"visibility": {"mood": True}}, "unknown attribute"),
        ({"visibility": {"age": "yes"}}, "expected true or false"),
        ({"logging": {"trajectory_stride": 0}}, "whole number, 1 or more"),
        ({"population": {"agents": {0: {"persona": "f25"}}}}, "no 'personas' file"),
        ({"personas": PERSONAS, "population": {"agents": {0: {"persona": "x99"}}}}, "unknown persona"),
        ({"personas": PERSONAS, "population": {"agents": {7: {"persona": "f25"}}}}, "not an agent index"),
        ({"personas": PERSONAS, "population": {"groups": {"northbound": {"persona": "f25"}}}}, "unknown group"),
        ({"personas": PERSONAS, "population": {"agents": {0: {"persona": "f25", "age": 500}}}}, "must be between"),
        ({"personas": PERSONAS, "population": {"agents": {0: {"persona": "f25", "radius": 0.3}}}}, "unknown key"),
    ],
)
def test_a_bad_avoidance_config_is_refused_with_a_reason(changes, message):
    with pytest.raises(ConfigError, match=message):
        avoidance(**changes)


# --- the log folder of one run ------------------------------------------------------------------


@pytest.fixture()
def side_run(tmp_path):
    """The offset head-on with personas, both agents keeping left, and a 20 cm clearance."""
    return run_one(
        tmp_path,
        scenario_overrides=OFFSET,
        personas=PERSONAS,
        population={"agents": {0: {"persona": "f25"}, 1: {"persona": "m70"}}},
        directives={"provider": "static", "default": {"side_preference": "left", "clearance_margin": 0.2}},
    )


def test_a_run_writes_its_five_files_and_they_pass_the_schema_check(side_run):
    run_dir, outcome = side_run
    assert sorted(path.name for path in run_dir.iterdir()) == sorted(AVOIDANCE_RUN_FILES)
    assert validate_run_dir(run_dir) == []
    assert read_json(run_dir / OUTCOME_FILE) == outcome
    assert outcome["status"] == "completed" and outcome["arrived"] == outcome["n_agents"] == 2


def test_config_json_is_fully_resolved(side_run):
    saved = read_json(side_run[0] / CONFIG_FILE)
    assert (saved["log_schema_version"], saved["run_kind"]) == (LOG_SCHEMA_VERSION, "avoidance") == (5, "avoidance")  # 2 before issue #28, 3 before #30, 4 before #32
    assert (saved["experiment_name"], saved["run_id"], saved["run_index"], saved["seed"], saved["repeat"]) == ("test_avoidance", "001_base", 1, 301, 1)
    assert saved["git"] == GIT and saved["variant"] == {} and saved["perception_schema_version"] == PERCEPTION_SCHEMA_VERSION
    scene = saved["scenario"]
    assert scene["type"] == "wide_corridor_head_on" and scene["dynamics"] == "holonomic" and scene["dt_s"] == 0.1
    assert scene["geometry"]["lateral_offsets"] == [0.05, -0.05] and scene["on_collision"] == "stop"
    assert scene["orca"] == {"tie_break": "brake"} and scene["navigation"] == {"lookahead_m": 2.0}
    assert scene["metrics"] == {
        "near_miss_distance_m": 0.1, "yield_speed_fraction": 0.5, "yield_min_duration_s": 1.0, "exposure_eps_mps": 1e-06,
        "pair_exposure_eps_mps": 0.001, "collision_course_min_s": 0.0,  # issue #30
    }
    assert [agent["preferred_speed_mps"] for agent in scene["agents"]] == [1.3, 1.3]
    assert saved["population"] == [
        {"agent_id": 0, "group": "eastbound", "persona_id": "f25", "attributes": {"age": 25, "gender": "female", "backstory": ""}},
        {"agent_id": 1, "group": "westbound", "persona_id": "m70", "attributes": {"age": 70, "gender": "male", "backstory": ""}},
    ]
    assert saved["visibility"]["age"] is True and saved["visibility"]["task"] is False
    assert saved["directives"]["provider"] == "static" and saved["directives"]["share_policy"] == "proportional"
    assert saved["directives"]["default"]["side_preference"] == "left"
    assert saved["arbitration"] == {"enabled": True, "policy": "strategy1", "tie_break": "lower_index"}
    assert saved["logging"] == {"trajectory_stride": 1, "interactions": True}


def test_interactions_hold_the_perception_record_and_the_directive(side_run):
    run_dir, outcome = side_run
    first, second = read_jsonl(run_dir / INTERACTIONS_FILE)
    assert (first["interaction_id"], first["observer_id"], first["neighbour_id"]) == (0, 0, 1)
    assert (second["interaction_id"], second["observer_id"], second["neighbour_id"]) == (1, 1, 0)
    perception = first["perception"]
    assert tuple(perception) == PERCEPTION_FIELDS and tuple(first["directive"]) == DIRECTIVE_FIELDS
    # The record was built at the moment the neighbour came within the sensing radius of 12.5 m.
    assert perception["step"] == first["start_step"] == 14 and perception["time_s"] == first["start_time_s"] == 1.4
    assert 12.24 < perception["distance_m"] <= 12.5
    assert perception["neighbour_attributes"] == {"age": 70, "gender": "male"}  # what agent 0 sees of agent 1
    assert perception["observer"]["attributes"] == {"age": 25, "gender": "female"}
    assert second["perception"]["neighbour_attributes"] == {"age": 25, "gender": "female"}
    assert perception["environment"]["free_width_m"] == pytest.approx(1.75)
    assert first["directive"]["side_preference"] == "left" and first["directive"]["clearance_margin"] == 0.2
    assert first["effective"] == [
        {"from_step": 14, "mutual": True, "responsibility_share": 0.5, "side_preference": "left", "clearance_margin": 0.2}
    ]
    assert first["end_reason"] == "out_of_range" and first["end_step"] > first["start_step"]
    assert first["min_separation_m"] == pytest.approx(0.2, abs=0.006) == outcome["totals"]["min_separation_m"]
    assert first["conflict_exposure_time_s"] == outcome["agents"]["0"]["conflict_exposure_time_s"] > 0
    assert first["arbiter_time_s"] == 0.0


def test_the_trajectory_says_which_directive_was_active_and_which_layer_was_in_charge(side_run):
    run_dir, outcome = side_run
    rows = read_csv(run_dir / TRAJECTORY_FILE)
    assert tuple(rows[0].keys()) == AVOIDANCE_TRAJECTORY_COLUMNS
    assert len(rows) == sum(len([r for r in rows if r["agent_id"] == a and r["speed_mps"]]) for a in "01") + 2  # and a final row each
    interactions = {str(item["interaction_id"]): item for item in read_jsonl(run_dir / INTERACTIONS_FILE)}
    for row in rows:
        if not row["speed_mps"]:
            continue  # a final row: the state at the end, no control
        assert row["control_mode"] == "orca" and row["role"] == "" and row["speed_bound_mps"] == ""
        ids = row["interactions"].split(";") if row["interactions"] else []
        assert len(ids) == int(row["n_neighbours"])
        for key in ids:  # the directive active on this step, found through the interaction it belongs to
            item = interactions[key]
            assert item["observer_id"] == int(row["agent_id"]) and item["start_step"] <= int(row["step"]) < item["end_step"]
            assert item["directive"]["side_preference"] == "left"
    before = [row for row in rows if row["agent_id"] == "0" and int(row["step"]) < 14 and row["speed_mps"]]
    assert before and all(row["interactions"] == "" and row["exposed"] == "false" for row in before)
    exposed = [row for row in rows if row["agent_id"] == "0" and row["exposed"] == "true"]
    assert len(exposed) * 0.1 == pytest.approx(outcome["agents"]["0"]["conflict_exposure_time_s"])
    assert float(rows[-1]["time_s"]) == outcome["sim_time_s"] and rows[-1]["control_mode"] == ""


def test_outcome_holds_every_metric_for_every_agent_and_in_total(side_run):
    outcome = side_run[1]
    assert tuple(outcome) == AVOIDANCE_OUTCOME_KEYS and outcome["run_kind"] == "avoidance"
    assert set(outcome["agents"]) == {"0", "1"}
    for metrics in outcome["agents"].values():
        assert tuple(metrics) == AVOIDANCE_AGENT_KEYS
        assert metrics["time_to_goal_s"] == pytest.approx(12.2, abs=0.2) and metrics["interactions"] == 1
        assert metrics["path_deviation_max_m"] == pytest.approx(0.3, abs=0.06)  # half of the 0.5 + 0.2 m apart, less its 5 cm start
        assert metrics["yield_events"] == metrics["near_misses"] == metrics["fallback_steps"] == metrics["one_sided_steps"] == 0
        assert metrics["min_wall_gap_m"] > 0.2 and metrics["arbiter_time_s"] == 0.0
    totals = outcome["totals"]
    assert totals["interactions"] == 2 and totals["steps_with_fallback"] == 0 and totals["near_misses"] == 0
    assert totals["conflict_exposure_time_s"] == pytest.approx(sum(m["conflict_exposure_time_s"] for m in outcome["agents"].values()))
    assert outcome["makespan_s"] == max(outcome["time_to_goal_s"].values())
    assert outcome["collisions"] == {"agent_agent": 0, "agent_wall": 0, "time_s": None, "agents": [], "max_overlap_m": None}
    assert outcome["deadlock"] is False and outcome["reciprocity_violations"] == [] and outcome["handoffs"] == []
    assert outcome["single_file"] == [] and outcome["thresholds"]["near_miss_distance_m"] == 0.1


def test_a_reciprocity_violation_is_in_the_events_and_in_the_outcome(tmp_path):
    run_dir, outcome = run_one(
        tmp_path,
        scenario_overrides=OFFSET,
        directives={"provider": "static", "agents": {0: {"responsibility_share": 0.3, "side_preference": "left"}, 1: {"responsibility_share": 0.3, "side_preference": "right"}}},
    )
    events = read_jsonl(run_dir / EVENTS_FILE)
    violations = [event for event in events if event["type"] == "reciprocity_violation"]
    assert [event["field"] for event in violations] == ["responsibility_share", "side_preference"]
    assert violations[0] == {
        "event_index": 0, "type": "reciprocity_violation", "step": 14, "time_s": 1.4, "field": "responsibility_share",
        "agents": [0, 1], "given": [0.3, 0.3], "resolved": [0.5, 0.5], "policy": "proportional",
    }
    assert violations[1]["given"] == ["left", "right"] and violations[1]["resolved"] == ["none", "none"]
    assert [v["field"] for v in outcome["reciprocity_violations"]] == ["responsibility_share", "side_preference"]
    assert [event["event_index"] for event in events] == list(range(len(events)))
    assert [event["time_s"] for event in events] == sorted(event["time_s"] for event in events)
    assert validate_run_dir(run_dir) == []


def test_the_handoff_is_logged_step_by_step_and_as_events(tmp_path):
    run_dir, outcome = run_one(
        tmp_path,
        scenario=BOTTLENECK,
        directives={"provider": "static", "agents": {0: {"passage_order": "follower"}, 1: {"passage_order": "leader"}}},
    )
    assert outcome["status"] == "completed" and validate_run_dir(run_dir) == []
    handoffs = [event for event in read_jsonl(run_dir / EVENTS_FILE) if event["type"] == "handoff"]
    assert [(h["to"], h["leader"], h["role_source"]) for h in handoffs] == [("arbiter", 1, "negotiated"), ("orca", None, None)]
    assert [h["pair"] for h in handoffs] == [[0, 1], [0, 1]] and outcome["handoffs"] == [
        {key: value for key, value in h.items() if key not in ("event_index", "type")} for h in handoffs
    ]
    assert outcome["single_file"][0]["segment"] == "bottleneck" and outcome["single_file"][0]["first_through"] == 1
    entry = outcome["single_file"][0]["entry_time_s"]
    assert entry["1"] < entry["0"]
    # Issue #32: when each came out at the far end; in a bottleneck, the one in first is out first.
    exit_ = outcome["single_file"][0]["exit_time_s"]
    assert outcome["single_file"][0]["first_out"] == 1 and entry["1"] < exit_["1"] < exit_["0"]
    rows = read_csv(run_dir / TRAJECTORY_FILE)
    held = [row for row in rows if row["control_mode"] == "arbiter"]
    assert {int(row["step"]) for row in held} == set(range(handoffs[0]["step"], handoffs[1]["step"]))
    assert {(row["agent_id"], row["role"]) for row in held if row["role"]} == {("0", "follower"), ("1", "leader")}
    assert all(row["zone_d_in_m"] and row["speed_bound_mps"] for row in held)
    assert outcome["agents"]["0"]["arbiter_time_s"] == pytest.approx(len(held) / 2 * 0.1)
    assert [event["agent_id"] for event in read_jsonl(run_dir / EVENTS_FILE) if event["type"] == "yield"] == [0]


def test_a_collision_and_a_near_miss_are_events(tmp_path):
    flow = {"geometry": {"agents_per_direction": 24, "length": 30.0}, "seed": 3}
    run_dir, outcome = run_one(tmp_path, scenario="configs/scenarios/bidirectional_flow.yaml", scenario_overrides=flow)
    events = read_jsonl(run_dir / EVENTS_FILE)
    collisions = [event for event in events if event["type"] == "collision"]
    assert len(collisions) == outcome["collisions"]["agent_agent"] > 0
    assert max(event["max_overlap_m"] for event in collisions) == outcome["collisions"]["max_overlap_m"] > 0
    assert min(event["time_s"] for event in collisions) == outcome["collisions"]["time_s"]
    assert all(set(event) >= {"pair", "start_time_s", "end_time_s", "max_overlap_m"} for event in collisions)
    assert len([event for event in events if event["type"] == "near_miss"]) == outcome["totals"]["near_misses"]
    assert len([event for event in events if event["type"] == "yield"]) == outcome["totals"]["yield_events"]
    assert outcome["status"] != "collision" and outcome["n_agents"] == 48  # the crowd scenario records it and goes on
    assert outcome["totals"]["steps_with_fallback"] > 0 and validate_run_dir(run_dir) == []


def test_logging_can_be_thinned_for_large_runs(tmp_path):
    run_dir, outcome = run_one(tmp_path, scenario_overrides=OFFSET, logging={"trajectory_stride": 10, "interactions": False})
    assert validate_run_dir(run_dir) == []
    rows = read_csv(run_dir / TRAJECTORY_FILE)
    assert {int(row["step"]) % 10 for row in rows if row["speed_mps"]} == {0}
    assert (run_dir / INTERACTIONS_FILE).read_text() == ""
    assert outcome["totals"]["interactions"] == 2  # still counted
    full = run_one(tmp_path, name="full", scenario_overrides=OFFSET)[1]
    assert outcome["agents"] == full["agents"]  # thinning the log changes nothing that is measured


# --- the task never reaches a log, and a persona never changes the physics ----------------------------


def test_the_task_is_in_no_file_of_a_run(side_run):
    run_dir, _ = side_run
    for path in run_dir.iterdir():
        text = path.read_text(encoding="utf-8")
        assert TASK not in text and "supermarket" not in text, path.name
        assert '"task"' not in text.replace('"task": false', ""), path.name  # only the visibility switch names it


def test_a_persona_changes_nothing_physical(tmp_path):
    """The same experiment with no personas, with one pair, and with the pair the other
    way round: the motion is the same to the last digit."""
    people = lambda a, b: {"personas": PERSONAS, "population": {"agents": {0: {"persona": a}, 1: {"persona": b}}}}
    runs = {
        "nobody": run_one(tmp_path, name="nobody", scenario_overrides=OFFSET),
        "f25_m70": run_one(tmp_path, name="f25_m70", scenario_overrides=OFFSET, **people("f25", "m70")),
        "m70_f25": run_one(tmp_path, name="m70_f25", scenario_overrides=OFFSET, **people("m70", "f25")),
    }
    reference = (runs["nobody"][0] / TRAJECTORY_FILE).read_bytes()
    for name, (run_dir, outcome) in runs.items():
        assert (run_dir / TRAJECTORY_FILE).read_bytes() == reference, name
        assert outcome["agents"] == runs["nobody"][1]["agents"], name
        agents = read_json(run_dir / CONFIG_FILE)["scenario"]["agents"]
        assert [(a["radius_m"], a["preferred_speed_mps"], a["max_speed_mps"]) for a in agents] == [(0.25, 1.3, 2.0)] * 2
    seen = [i["perception"]["neighbour_attributes"] for i in read_jsonl(runs["m70_f25"][0] / INTERACTIONS_FILE)]
    assert seen == [{"age": 25, "gender": "female"}, {"age": 70, "gender": "male"}]  # only what is perceived differs
    assert [i["perception"]["neighbour_attributes"] for i in read_jsonl(runs["nobody"][0] / INTERACTIONS_FILE)] == [{}, {}]


def test_speed_and_age_change_together_only_when_a_config_says_both(tmp_path):
    """Linking them is possible, and has to be written down: the persona under population,
    the speed under the scenario's per-agent overrides."""
    linked = run_one(
        tmp_path,
        scenario_overrides={**OFFSET, "agents": {"overrides": {1: {"preferred_speed": 1.0}}}},
        personas=PERSONAS,
        population={"agents": {1: {"persona": "m70"}}},
    )
    agents = read_json(linked[0] / CONFIG_FILE)["scenario"]["agents"]
    assert [a["preferred_speed_mps"] for a in agents] == [1.3, 1.0]
    assert linked[1]["time_to_goal_s"]["1"] > linked[1]["time_to_goal_s"]["0"] + 2.0


def test_hidden_attributes_stay_out_of_the_logged_records(tmp_path):
    people = {"personas": PERSONAS, "population": {"agents": {0: {"persona": "f25"}, 1: {"persona": "m70"}}}}
    run_dir, _ = run_one(tmp_path, scenario_overrides=OFFSET, visibility={"age": False, "size": False}, **people)
    for interaction in read_jsonl(run_dir / INTERACTIONS_FILE):
        perception = interaction["perception"]
        assert set(perception["neighbour_attributes"]) == {"gender"}
        assert perception["neighbour_radius_m"] is None and perception["time_to_collision_s"] is None
        assert perception["neighbour_speed_mps"] is not None
    assert read_json(run_dir / CONFIG_FILE)["visibility"]["age"] is False


# --- the schema check ---------------------------------------------------------------------------


@pytest.mark.parametrize("missing", AVOIDANCE_RUN_FILES)
def test_schema_check_notices_a_missing_file(side_run, missing):
    (side_run[0] / missing).unlink()
    problems = validate_run_dir(side_run[0])
    assert f"missing file {missing}" in problems


@pytest.mark.parametrize(
    "file, path",
    [
        (CONFIG_FILE, ["population"]), (CONFIG_FILE, ["directives"]), (CONFIG_FILE, ["perception_schema_version"]),
        (OUTCOME_FILE, ["totals"]), (OUTCOME_FILE, ["handoffs"]), (OUTCOME_FILE, ["agents", "0", "conflict_exposure_time_s"]),
        (OUTCOME_FILE, ["totals", "steps_with_fallback"]),
    ],
)
def test_schema_check_notices_a_missing_field(side_run, file, path):
    data = read_json(side_run[0] / file)
    node = data
    for key in path[:-1]:
        node = node[key]
    del node[path[-1]]
    (side_run[0] / file).write_text(json.dumps(data), encoding="utf-8")
    assert any(f"missing key '{path[-1]}'" in problem for problem in validate_run_dir(side_run[0]))


def test_schema_check_notices_damage_to_the_other_files(side_run, tmp_path):
    run_dir = side_run[0]
    for damage in ("perception_field", "directive_field", "leaked_task", "interaction_count", "event_type", "trajectory", "status", "version", "kind"):
        copy_dir = tmp_path / damage
        shutil.copytree(run_dir, copy_dir)
        interactions = read_jsonl(copy_dir / INTERACTIONS_FILE)
        if damage == "perception_field":
            del interactions[0]["perception"]["time_to_collision_s"]
        elif damage == "directive_field":
            del interactions[1]["directive"]["passage_order"]
        elif damage == "leaked_task":
            interactions[0]["perception"]["neighbour_attributes"]["task"] = "anything"
        elif damage == "interaction_count":
            interactions = interactions[:1]
        (copy_dir / INTERACTIONS_FILE).write_text("\n".join(json.dumps(i) for i in interactions) + "\n", encoding="utf-8")
        if damage == "event_type":
            (copy_dir / EVENTS_FILE).write_text(json.dumps({"event_index": 0, "type": "mystery", "time_s": 0.0}) + "\n", encoding="utf-8")
        elif damage == "trajectory":
            (copy_dir / TRAJECTORY_FILE).write_text("step,time\n0,0\n", encoding="utf-8")
        elif damage in ("status", "version", "kind"):
            file = OUTCOME_FILE if damage == "status" else CONFIG_FILE
            data = read_json(copy_dir / file)
            data.update({"status": "aborted"} if damage == "status" else {"log_schema_version": LOG_SCHEMA_VERSION + 1} if damage == "version" else {"run_kind": "other"})
            (copy_dir / file).write_text(json.dumps(data), encoding="utf-8")
        assert validate_run_dir(copy_dir) != [], damage
    assert "never observable" in " ".join(validate_run_dir(tmp_path / "leaked_task"))


def test_a_negotiation_run_now_says_its_kind_and_the_new_version(tmp_path):
    plan = experiment(c1_config()).plans()[0]
    execute_run(plan, MockClient(policy="task_priority"), tmp_path / "talk", git=GIT)
    saved = read_json(tmp_path / "talk" / CONFIG_FILE)
    assert (saved["log_schema_version"], saved["run_kind"]) == (5, "negotiation")  # 2 before issue #28, 3 before #30, 4 before #32
    assert sorted(path.name for path in (tmp_path / "talk").iterdir()) == sorted(RUN_FILES)  # its files are unchanged
    assert validate_run_dir(tmp_path / "talk") == []


def test_every_committed_run_folder_still_passes_the_schema_check():
    """The 66 run folders of issue #24 were written under version 1 and must stay valid;
    the folders of issue #26 are version 2, those of issue #28 version 3, those of
    issue #30 version 4, and those of issue #32 version 5."""
    versions = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    kinds = {"negotiation": 0, "avoidance": 0}
    for config_path in sorted((PACKAGE_ROOT / "runs").glob("*/*/config.json")):
        config = read_json(config_path)
        assert validate_run_dir(config_path.parent) == [], config_path.parent
        versions[config["log_schema_version"]] += 1
        kinds[config.get("run_kind", "negotiation")] += 1
        if config_path.parent.parent.name.startswith(("c0_", "c1_", "c2_")):
            assert config["log_schema_version"] == 1 and "run_kind" not in config
    assert versions[1] == 66  # 54 no-LLM runs and 12 paid ones, as issue #24 left them
    assert versions[5] == 16 + 560 + 16 + 8 + 4  # issue #32: the in-passage case sources and behaviour checks; issue #60: the passage case sources with the pair 0.3 m apart; issue #110: the group head-on case sources; issue #117: RF-35's crowd flow sources
    assert kinds["avoidance"] == versions[2] + versions[3] + versions[4] + versions[5]


# --- a whole experiment, and the command line -----------------------------------------------------


def small_experiment():
    return avoidance(
        design={"seed": 700, "factors": {
            "layout": [{"name": "symmetric"}, {"name": "offset", "scenario_overrides": OFFSET}],
            "side": [{"name": "plain"}, {"name": "left", "directives": {"provider": "static", "default": {"side_preference": "left"}}}],
        }}
    )


def test_run_experiment_writes_one_summary_row_per_run(tmp_path):
    result = run_avoidance_experiment(small_experiment(), out_root=tmp_path, report=QUIET, git=GIT)
    assert result.executed == ["001_symmetric_plain", "002_symmetric_left", "003_offset_plain", "004_offset_left"]
    assert result.experiment_dir == tmp_path / "test_avoidance" and result.summary_path == result.experiment_dir / SUMMARY_FILE
    rows = read_csv(result.summary_path)
    assert tuple(rows[0].keys()) == AVOIDANCE_SUMMARY_COLUMNS
    assert [row["run_id"] for row in rows] == result.executed
    assert [row["variant"] for row in rows] == ["layout=symmetric+side=plain", "layout=symmetric+side=left", "layout=offset+side=plain", "layout=offset+side=left"]
    assert [row["provider"] for row in rows] == ["null", "static", "null", "static"]
    assert {row["scenario"] for row in rows} == {"wide_corridor_head_on"} and {row["n_agents"] for row in rows} == {"2"}
    assert {row["git_commit"] for row in rows} == {"abc123"}
    assert [row["status"] for row in rows][1:] == ["completed"] * 3
    for run_id in result.executed:
        assert validate_run_dir(result.experiment_dir / run_id) == []


def test_finished_runs_are_skipped_and_can_be_redone(tmp_path):
    first = run_avoidance_experiment(small_experiment(), out_root=tmp_path, limit=2, report=QUIET, git=GIT)
    assert len(first.executed) == 2 and len(first.rows) == 2
    second = run_avoidance_experiment(small_experiment(), out_root=tmp_path, report=QUIET, git=GIT)
    assert second.skipped == first.executed and len(second.executed) == 2 and len(second.rows) == 4
    third = run_avoidance_experiment(small_experiment(), out_root=tmp_path, overwrite=True, report=QUIET, git=GIT)
    assert len(third.executed) == 4 and third.skipped == []


def test_a_run_is_reproducible_to_the_byte(tmp_path):
    one = run_avoidance_experiment(small_experiment(), out_root=tmp_path / "a", limit=2, report=QUIET, git=GIT)
    two = run_avoidance_experiment(small_experiment(), out_root=tmp_path / "b", limit=2, report=QUIET, git=GIT)
    for run_id in one.executed:
        for name in (TRAJECTORY_FILE, INTERACTIONS_FILE, EVENTS_FILE, OUTCOME_FILE):
            assert (one.experiment_dir / run_id / name).read_bytes() == (two.experiment_dir / run_id / name).read_bytes(), (run_id, name)


def test_the_command_line_runs_an_avoidance_experiment(tmp_path, capsys):
    assert cli.main([str(CONFIG_DIR / "si1_open_crossing.yaml"), "--plan"]) == 0
    listed = capsys.readouterr().out
    assert "si1_open_crossing: avoidance layer, 4 run(s), no model calls, cost USD 0" in listed
    assert "001_symmetric_plain" in listed and "004_agent_1_later_both_left" in listed
    assert not (tmp_path / "si1_open_crossing").exists()

    assert cli.main([str(CONFIG_DIR / "si1_open_crossing.yaml"), "--out", str(tmp_path), "--limit", "2"]) == 0
    printed = capsys.readouterr().out
    assert "done: 2 run(s) executed, 0 skipped, cost USD 0" in printed
    assert len(read_csv(tmp_path / "si1_open_crossing" / SUMMARY_FILE)) == 2


def test_the_command_line_refuses_a_client_for_an_avoidance_experiment(tmp_path, capsys):
    assert cli.main([str(CONFIG_DIR / "si1_open_crossing.yaml"), "--client", "deepseek", "--out", str(tmp_path)]) == 2
    assert "calls no model; --client does not apply" in capsys.readouterr().err
    assert not (tmp_path / "si1_open_crossing").exists()


def test_the_command_line_still_runs_a_negotiation_experiment(tmp_path, capsys):
    config = PACKAGE_ROOT / "configs" / "experiments" / "c0_no_llm.yaml"
    assert cli.main([str(config), "--out", str(tmp_path), "--limit", "1"]) == 0
    assert "c0_no_llm_doorway: condition C0, 1 run(s)" in capsys.readouterr().out


# --- nothing is spent ----------------------------------------------------------------------------


def test_an_avoidance_experiment_calls_no_model_and_spends_nothing(tmp_path, monkeypatch):
    """No client is ever built, nothing is added to the spend ledger, and the network guard
    of conftest.py is never tripped."""
    import negsim.experiment.batch as batch
    import negsim.llm.deepseek as deepseek

    def forbidden(*args, **kwargs):
        raise AssertionError("an avoidance run tried to build an LLM client")

    monkeypatch.setattr(batch, "make_client", forbidden)
    monkeypatch.setattr(deepseek.DeepSeekClient, "from_env", classmethod(forbidden))
    monkeypatch.setattr(deepseek.DeepSeekClient, "complete", forbidden)
    ledger = PACKAGE_ROOT / "spend_ledger.jsonl"
    before = ledger.read_bytes()
    for name in ("si1_open_crossing.yaml", "si1_bottleneck_handoff.yaml"):
        config = AvoidanceExperiment.load(CONFIG_DIR / name)
        run_avoidance_experiment(config, out_root=tmp_path, limit=2, report=QUIET, git=GIT)
    assert ledger.read_bytes() == before
    assert not any("ledger" in path.name for path in tmp_path.rglob("*"))


def test_the_avoidance_layer_does_not_import_the_llm_package():
    import ast

    for path in sorted((PACKAGE_ROOT / "negsim" / "avoidance").glob("*.py")) + [PACKAGE_ROOT / "negsim" / "experiment" / "avoidance.py"]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            for name in names:
                assert "llm" not in name.split(".") and "negotiation" not in name.split("."), (path.name, name)


# --- the documents keep up with the code -----------------------------------------------------------


def test_the_schema_document_names_every_avoidance_field():
    from negsim.runlog import schema

    document = (PACKAGE_ROOT / "docs" / "log-schema.md").read_text(encoding="utf-8")
    assert f"# Log schema, version {LOG_SCHEMA_VERSION}" in document and "- **2** (2026-10-13, issue #26)" in document
    for group in (
        "AVOIDANCE_RUN_FILES", "AVOIDANCE_CONFIG_KEYS", "AVOIDANCE_TRAJECTORY_COLUMNS", "INTERACTION_KEYS",
        "INTERACTION_END_REASONS", "EVENT_TYPES", "EVENT_KEYS", "AVOIDANCE_OUTCOME_KEYS", "AVOIDANCE_AGENT_KEYS",
        "AVOIDANCE_TOTAL_KEYS", "AVOIDANCE_SUMMARY_COLUMNS", "AVOIDANCE_STATUSES", "RUN_KINDS",
    ):
        for field in getattr(schema, group):
            pattern = r"(?<![A-Za-z0-9_])" + re.escape(field) + r"(?![A-Za-z0-9_])"
            assert re.search(pattern, document), f"{group}: '{field}' is not described in docs/log-schema.md"


def test_the_metrics_document_records_the_default_thresholds():
    from negsim.scenarios.crowd_base import DEFAULT_THRESHOLDS

    document = (PACKAGE_ROOT / "docs" / "metrics.md").read_text(encoding="utf-8")
    for name in ("interaction", "conflict_exposure_time", "yield_event", "near_miss", "collision", "deadlock"):
        assert f"`{name}`" in document, name
    for key, value in DEFAULT_THRESHOLDS.as_dict().items():
        assert f"`{key}`" in document, key
    assert "| `near_miss_distance_m` | 0.1 m |" in document and "| `yield_speed_fraction` | 0.5 |" in document
    assert "| `yield_min_duration_s` | 1.0 s |" in document and "| `exposure_eps_mps` | 1e-6 m/s |" in document


def test_the_documents_issue_26_asks_for_exist_and_say_where_each_piece_lives():
    docs = PACKAGE_ROOT / "docs"
    for name in ("orca", "perception", "parameters", "metrics", "derivations", "architecture", "log-schema"):
        assert (docs / f"{name}.md").is_file(), name
    architecture = (docs / "architecture.md").read_text(encoding="utf-8")
    for module in ("orca.py", "lp.py", "neighbours.py", "perception.py", "directives.py", "coordination.py", "simulation.py"):
        assert module in architecture and (PACKAGE_ROOT / "negsim" / "avoidance" / module).is_file(), module
    for word in ("AvoidanceDirective", "DirectiveProvider", "NullProvider", "StaticProvider", "PerceptionRecord", "DynamicsModel"):
        assert word in architecture, word
    orca = (docs / "orca.md").read_text(encoding="utf-8")
    assert "75822bb" in orca and "Apache" in orca and "Sec 5.3" in orca and "Sec 5.4" in orca
    derivations = (docs / "derivations.md").read_text(encoding="utf-8")
    assert "## 9." in derivations and "reciprocity" in derivations.lower()
    notices = (PACKAGE_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert "RVO2" in notices and "Apache" in notices and (PACKAGE_ROOT / "LICENSES" / "Apache-2.0.txt").is_file()
