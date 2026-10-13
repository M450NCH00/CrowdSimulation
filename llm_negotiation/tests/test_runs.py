"""Whole runs on the mock client: the integration test, the log folder, timing modes,
fallback, aborts and resuming. Everything is written under pytest's temporary folder."""

from __future__ import annotations

import csv
import json
import shutil

import pytest

from helpers import c1_config, c2_config, experiment
from negsim.configutil import PACKAGE_ROOT, ConfigError
from negsim.experiment import ExperimentConfig, RunAborted, execute_run, run_experiment, worst_case_cost
from negsim.llm import BudgetedClient, BudgetGuard, DeepSeekClient, MockClient, PriceTable, SpendLedger
from negsim.runlog import (
    CONFIG_FILE,
    CONVERSATION_FILE,
    LOG_SCHEMA_VERSION,
    OUTCOME_FILE,
    RUN_FILES,
    SUMMARY_COLUMNS,
    SUMMARY_FILE,
    TRAJECTORY_COLUMNS,
    TRAJECTORY_FILE,
    TRANSCRIPT_FILE,
    validate_run_dir,
)
from test_llm import FAKE_KEY, PEAK_TUESDAY, FakeTransport, api_response

CONFIG_DIR = PACKAGE_ROOT / "configs" / "experiments"
QUIET = lambda line: None


def reply(message: str, stance: str) -> str:
    return json.dumps({"message": message, "stance": stance})


def run_one(tmp_path, config: dict, client=None, name="run"):
    plan = experiment(config).plans()[0]
    run_dir = tmp_path / name
    outcome = execute_run(plan, client, run_dir, git={"commit": "abc123", "dirty": False})
    return run_dir, outcome


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_turns(run_dir):
    return [json.loads(line) for line in (run_dir / CONVERSATION_FILE).read_text(encoding="utf-8").splitlines() if line]


def read_trajectory(run_dir):
    with (run_dir / TRAJECTORY_FILE).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


# --- the integration test the issue asks for ---------------------------------------------------


def test_full_doorway_run_with_the_mock_client(tmp_path):
    """A complete doorway run: negotiation, motion, logging. No collisions, the run
    finishes, and the log folder is complete and consistent."""
    run_dir, outcome = run_one(tmp_path, c1_config(), MockClient(policy="task_priority"))

    assert outcome["status"] == "completed"
    assert outcome["collisions"] == {"agent_agent": 0, "agent_wall": 0, "time_s": None, "agents": []}
    assert outcome["deadlock"] is False
    assert outcome["time_to_goal_s"]["0"] is not None and outcome["time_to_goal_s"]["1"] is not None
    assert outcome["makespan_s"] == max(outcome["time_to_goal_s"].values()) <= 15.0

    # The hospital agent (agent 0) was agreed to go first, and did.
    assert outcome["negotiation"]["consensus_reached"] is True
    assert outcome["negotiation"]["negotiated_leader"] == 0 == outcome["first_through"]
    assert outcome["roles"]["negotiated_roles_followed"] is True
    assert outcome["fallback_used"] is False
    assert outcome["ground_truth"]["higher_priority_agent"] == 0
    assert outcome["ground_truth"]["higher_priority_first"] is True
    assert outcome["follower"] == 1 and 0 < outcome["follower_min_speed_mps"] < 0.3

    assert sorted(path.name for path in run_dir.iterdir()) == sorted(RUN_FILES)
    assert validate_run_dir(run_dir) == []


def test_log_files_agree_with_each_other(tmp_path):
    run_dir, outcome = run_one(tmp_path, c1_config(), MockClient(policy="task_priority"))
    config, turns, rows = read_json(run_dir / CONFIG_FILE), read_turns(run_dir), read_trajectory(run_dir)
    assert read_json(run_dir / OUTCOME_FILE) == outcome

    assert len(turns) == outcome["negotiation"]["turns_used"] == 3
    assert [[t["speaker"], t["stance"]] for t in turns] == outcome["negotiation"]["stances"]
    # The exact system prompt each agent was given is stored, and is what was actually sent.
    for turn in turns:
        assert turn["prompt_messages"][0]["content"] == config["negotiation"]["rendered_system_prompts"][f"agent_{turn['speaker']}"]
    assert outcome["negotiation"]["tokens"]["prompt_tokens"] == sum(t["tokens"]["prompt_tokens"] for t in turns)

    transcript = (run_dir / TRANSCRIPT_FILE).read_text(encoding="utf-8")
    for turn in turns:
        assert turn["message"] in transcript and f"`{turn['stance']}`" in transcript
    assert "higher-priority agent is agent 0; it went first: yes" in transcript

    # One row per agent per step, plus the final state of each agent.
    assert len(rows) == 2 * (outcome["steps"] + 1)
    assert tuple(rows[0].keys()) == TRAJECTORY_COLUMNS
    assert float(rows[-1]["time_s"]) == outcome["sim_time_s"] and rows[-1]["v_mps"] == ""
    arrival = outcome["time_to_goal_s"]["0"]
    leader_rows = [row for row in rows if row["agent_id"] == "0" and float(row["time_s"]) < arrival]
    assert {float(row["v_mps"]) for row in leader_rows} == {0.3}  # the leader never slows on its way
    follower_rows = [row for row in rows if row["agent_id"] == "1" and row["role"] == "follower"]
    assert follower_rows and all(row["role_source"] == "negotiated" for row in follower_rows)
    assert all(float(row["v_mps"]) <= float(row["speed_bound_mps"]) + 1e-9 for row in follower_rows)


def test_config_json_is_fully_resolved(tmp_path):
    config = c1_config()
    config["negotiation"].update(info_fields=["own_speed"], visibility={"size": False})
    run_dir, _ = run_one(tmp_path, config, MockClient(policy="task_priority"))
    saved = read_json(run_dir / CONFIG_FILE)
    assert saved["log_schema_version"] == LOG_SCHEMA_VERSION
    assert (saved["experiment_name"], saved["condition"], saved["seed"], saved["repeat"]) == ("test_c1", "C1", 101, 1)
    assert saved["git"] == {"commit": "abc123", "dirty": False}
    assert saved["scenario"]["type"] == "doorway" and saved["scenario"]["dt_s"] == 0.2
    assert [a["max_speed_mps"] for a in saved["scenario"]["agents"]] == [0.3, 0.3]
    assert [a["radius_m"] for a in saved["scenario"]["agents"]] == [0.1, 0.1]
    assert [p["task_type"] for p in saved["participants"]] == ["hospital", "grocery"]
    assert [p["side"] for p in saved["participants"]] == ["north", "south"]
    assert saved["assignment"] == {
        "agent_0": {"persona": None, "overrides": {}, "task_type": "hospital"},
        "agent_1": {"persona": None, "overrides": {}, "task_type": "grocery"},
        "swap_sides": False, "first_speaker": 0,
    }
    talk = saved["negotiation"]
    assert talk["prompt_template"]["key"] == "gamechat_task_v1" and len(talk["prompt_template"]["sha256"]) == 64
    assert talk["info_fields"] == ["own_speed"] and talk["visibility"]["size"] is False and talk["visibility"]["age"] is True
    assert talk["first_speaker"] == 0 and talk["timing"] == {"mode": "pre_conflict", "seconds_per_message": 1.0}
    assert saved["llm"]["client"] == "mock" and saved["llm"]["model"] == "deepseek-flash"
    assert saved["llm"]["temperature"] == 1.0 and saved["llm"]["thinking"] == "disabled" and saved["llm"]["seed_parameter"] is None
    assert saved["scoring"] == {"ground_truth": "task_priority", "priority_order": ["hospital", "airport", "grocery"]}


def test_persona_run_in_the_hallway_logs_personas_and_is_not_scored(tmp_path):
    run_dir, outcome = run_one(tmp_path, c2_config(), MockClient(policy="first_speaker_goes"))
    assert outcome["status"] == "completed" and outcome["collisions"]["agent_agent"] == 0
    assert outcome["ground_truth"] is None  # nothing is called correct or incorrect
    assert validate_run_dir(run_dir) == []
    saved = read_json(run_dir / CONFIG_FILE)
    assert [p["persona"]["persona_id"] for p in saved["participants"]] == ["f70", "m25"]
    assert [(p["persona"]["age"], p["persona"]["gender"]) for p in saved["participants"]] == [(70, "female"), (25, "male")]
    turns = read_turns(run_dir)
    assert turns[0]["situation_report"].startswith("What you can see right now:")
    assert turns[0]["situation_values"]["own_distance_to_region_m"] == pytest.approx(2.3425, abs=1e-3)
    transcript = (run_dir / TRANSCRIPT_FILE).read_text(encoding="utf-8")
    assert "Ground truth: none for this condition" in transcript and "correct" not in transcript.lower().replace("incorrect", "")
    for text in (json.dumps(saved), transcript, json.dumps(turns)):
        assert '"name"' not in text


def test_a_run_without_negotiation_still_writes_every_file(tmp_path):
    config = c1_config(condition="C0", negotiation={"enabled": False})
    run_dir, outcome = run_one(tmp_path, config)
    assert validate_run_dir(run_dir) == []
    assert (run_dir / CONVERSATION_FILE).read_text() == ""
    assert outcome["negotiation"]["enabled"] is False and outcome["fallback_used"] is None
    assert outcome["roles"]["role_source_steps"]["negotiated"] == 0 and outcome["roles"]["role_source_steps"]["strategy1"] > 0
    assert outcome["first_through"] == 0  # the tie goes to the lower index
    assert outcome["ground_truth"]["higher_priority_first"] is True
    saved = read_json(run_dir / CONFIG_FILE)
    assert saved["llm"]["client"] is None and saved["negotiation"]["rendered_system_prompts"] is None


# --- the dialogue decides the motion -------------------------------------------------------------


@pytest.mark.parametrize("first_speaker", [0, 1])
@pytest.mark.parametrize("scripted_leader", [0, 1])
def test_whoever_the_agents_agree_on_goes_first(tmp_path, first_speaker, scripted_leader):
    opener_stance = "I_GO_FIRST" if first_speaker == scripted_leader else "YOU_GO_FIRST"
    closer_stance = "YOU_GO_FIRST" if opener_stance == "I_GO_FIRST" else "I_GO_FIRST"
    client = MockClient(script=[reply("a", opener_stance), reply("b", closer_stance)])
    config = c1_config(scoring={})
    config["design"]["runs"][0]["first_speaker"] = first_speaker
    _, outcome = run_one(tmp_path, config, client)
    assert outcome["negotiation"]["negotiated_leader"] == scripted_leader == outcome["first_through"]
    assert outcome["negotiation"]["stances"][0][0] == first_speaker


def test_no_consensus_falls_back_to_strategy_1_and_says_so(tmp_path):
    run_dir, outcome = run_one(tmp_path, c1_config(), MockClient(policy="insist"))
    talk = outcome["negotiation"]
    assert talk["consensus_reached"] is False and talk["end_reason"] == "message_limit"
    assert talk["turns_used"] == 8 and talk["messages_per_agent"] == {"0": 4, "1": 4}
    assert outcome["fallback_used"] is True and outcome["fallback_reasons"] == ["no_consensus"]
    assert outcome["status"] == "completed" and outcome["collisions"]["agent_agent"] == 0
    assert outcome["roles"]["negotiated_leader"] is None and outcome["roles"]["negotiated_roles_followed"] is None
    assert "Consensus: no (8 turns; dialogue ended: message_limit)" in (run_dir / TRANSCRIPT_FILE).read_text()


def test_unreadable_replies_are_logged_and_the_run_still_completes(tmp_path):
    client = MockClient(script=["not json", "still not json", reply("You first.", "YOU_GO_FIRST"), reply("Thanks.", "I_GO_FIRST")])
    run_dir, outcome = run_one(tmp_path, c1_config(), client)
    turns = read_turns(run_dir)
    assert turns[0]["parse_ok"] is False and turns[0]["stance"] == "UNDECIDED" and turns[0]["n_attempts"] == 2
    assert turns[0]["parse_error"].startswith("not_json")
    assert [a["raw_output"] for a in turns[0]["attempts"]] == ["not json", "still not json"]
    assert outcome["negotiation"]["parse_failures"] == 1 and outcome["negotiation"]["retries"] == 1
    assert outcome["negotiation"]["consensus_reached"] is True and outcome["negotiation"]["negotiated_leader"] == 0
    assert validate_run_dir(run_dir) == []
    assert "nothing (the reply could not be read)" in (run_dir / TRANSCRIPT_FILE).read_text()


# --- timing modes --------------------------------------------------------------------------------


def test_pre_conflict_mode_pauses_the_clock_during_the_dialogue(tmp_path):
    run_dir, outcome = run_one(tmp_path, c1_config(), MockClient(policy="task_priority"))
    assert {turn["sim_time_s"] for turn in read_turns(run_dir)} == {0.0}
    assert outcome["negotiation"]["start_time_s"] == outcome["negotiation"]["end_time_s"] == 0.0
    assert outcome["roles"]["role_source_steps"]["strategy1"] == 0


def test_concurrent_mode_advances_the_clock_between_messages(tmp_path):
    config = c1_config()
    config["negotiation"]["timing"] = {"mode": "concurrent", "seconds_per_message": 1.0}
    run_dir, outcome = run_one(tmp_path, config, MockClient(policy="task_priority"))
    turns = read_turns(run_dir)
    assert [turn["sim_time_s"] for turn in turns] == [0.0, 1.0, 2.0]
    assert outcome["negotiation"]["end_time_s"] == 2.0
    # Until they agreed, Strategy 1 was in charge: that is recorded as a fallback.
    assert outcome["roles"]["role_source_steps"]["strategy1"] == 10  # 2.0 s / 0.2 s
    assert outcome["fallback_used"] is True and outcome["fallback_reasons"] == ["conflict_before_consensus"]
    assert outcome["status"] == "completed" and outcome["collisions"]["agent_agent"] == 0
    rows = read_trajectory(run_dir)
    assert {row["dialogue_active"] for row in rows if float(row["time_s"]) < 2.0 and row["v_mps"]} == {"true"}
    assert {row["dialogue_active"] for row in rows if float(row["time_s"]) > 2.0} == {"false"}


def test_concurrent_mode_can_reverse_the_roles_strategy_1_had_assigned(tmp_path):
    """The paper's 'SMG Comm.' case: the agents are already in a conflict, Strategy 1 has
    made agent 0 the leader, and the dialogue then gives the lead to agent 1."""
    config = c1_config(scoring={})
    config["negotiation"]["timing"] = {"mode": "concurrent", "seconds_per_message": 1.0}
    client = MockClient(script=[reply("You go.", "YOU_GO_FIRST"), reply("Going.", "I_GO_FIRST")])
    run_dir, outcome = run_one(tmp_path, config, client)
    assert outcome["negotiation"]["negotiated_leader"] == 1 == outcome["first_through"]
    assert outcome["status"] == "completed" and outcome["collisions"]["agent_agent"] == 0
    roles_of_agent_0 = [row["role"] for row in read_trajectory(run_dir) if row["agent_id"] == "0" and row["role"]]
    assert roles_of_agent_0[0] == "leader" and roles_of_agent_0[-1] == "follower"


def test_concurrent_mode_reports_changed_situations_to_the_agents(tmp_path):
    config = c2_config()
    config["negotiation"]["timing"] = {"mode": "concurrent", "seconds_per_message": 0.5}
    run_dir, _ = run_one(tmp_path, config, MockClient(policy="first_speaker_goes"))
    first, second = read_turns(run_dir)[:2]
    assert second["situation_values"]["elapsed_time_s"] == 0.5
    assert second["situation_values"]["own_distance_to_region_m"] < first["situation_values"]["other_distance_to_region_m"]
    assert "0.5 s." in second["situation_report"]


def slow_talkers(seconds_per_message: float) -> dict:
    """Agent 0 leads under Strategy 1 (agent 1 starts 0.2 m further back) and reaches the
    conflict zone about 5.5 s in; it is out again at about 9.2 s. The agents' second
    message, which would give the lead to agent 1, arrives ``seconds_per_message`` in."""
    config = c1_config(scoring={})
    config["negotiation"].update(
        timing={"mode": "concurrent", "seconds_per_message": seconds_per_message}, max_messages_per_agent=1
    )
    config["design"]["runs"][0]["scenario_overrides"] = {"start_offsets": [0.0, 0.2]}
    return config


def test_an_agreement_reached_too_late_cannot_be_carried_out(tmp_path):
    """The agents agree that agent 1 should lead while agent 0 is already inside the
    conflict zone. Agent 0 cannot give way any more, so it carries on; the run records
    that the agreement was not followed, and why."""
    client = MockClient(script=[reply("You go.", "YOU_GO_FIRST"), reply("Going.", "I_GO_FIRST")])
    _, outcome = run_one(tmp_path, slow_talkers(7.0), client)
    assert outcome["negotiation"]["consensus_reached"] is True and outcome["negotiation"]["negotiated_leader"] == 1
    assert outcome["first_through"] == 0 and outcome["roles"]["negotiated_roles_followed"] is False
    assert outcome["fallback_reasons"] == ["conflict_before_consensus", "negotiated_roles_not_feasible"]
    assert outcome["roles"]["role_source_steps"]["physical_precedence"] > 0
    assert outcome["status"] == "completed" and outcome["collisions"]["agent_agent"] == 0


def test_a_dialogue_overtaken_by_events_is_stopped(tmp_path):
    """If the leader is already out of the conflict zone when the next message is due,
    there is nothing left to negotiate: the dialogue ends without spending another call."""
    client = MockClient(script=[reply("You go.", "YOU_GO_FIRST"), reply("Going.", "I_GO_FIRST")])
    _, outcome = run_one(tmp_path, slow_talkers(11.0), client)
    talk = outcome["negotiation"]
    assert talk["end_reason"] == "conflict_over" and talk["turns_used"] == 1 and talk["consensus_reached"] is False
    assert len(client.requests) == 1
    assert outcome["fallback_reasons"] == ["no_consensus"] and outcome["first_through"] == 0
    assert outcome["status"] == "completed"


# --- failure outcomes ------------------------------------------------------------------------------


def test_a_collision_ends_the_run_and_is_reported(tmp_path):
    config = c1_config(condition="C0", negotiation={"enabled": False}, arbitration={"policy": "none"})
    run_dir, outcome = run_one(tmp_path, config)
    assert outcome["status"] == "collision"
    assert outcome["collisions"]["agent_agent"] == 1 and outcome["collisions"]["agents"] == [0, 1]
    assert outcome["collisions"]["time_s"] == outcome["sim_time_s"]
    assert outcome["makespan_s"] is None and validate_run_dir(run_dir) == []


def test_a_run_that_cannot_finish_in_time_is_a_timeout(tmp_path):
    config = c1_config(condition="C0", negotiation={"enabled": False})
    config["design"]["runs"][0]["scenario_overrides"] = {"max_time": 3.0}
    _, outcome = run_one(tmp_path, config)
    assert outcome["status"] == "timeout" and outcome["sim_time_s"] == 3.0
    assert outcome["time_to_goal_s"] == {"0": None, "1": None} and outcome["first_through"] is None


def paid_client(tmp_path, cap, responses, ledger=None):
    """The real DeepSeek client behind the budget guard, on a fake transport, at peak rates."""
    transport = FakeTransport(*responses)
    deepseek = DeepSeekClient(FAKE_KEY, transport=transport, sleep=lambda s: None)
    ledger = ledger or SpendLedger(tmp_path / "ledger.jsonl")
    guard = BudgetGuard(ledger, cap, PriceTable.from_yaml())
    return BudgetedClient(deepseek, guard, now=lambda: PEAK_TUESDAY), transport, ledger


def test_budget_refusal_aborts_the_run_and_keeps_what_was_logged(tmp_path):
    """Each reply here costs about USD 0.0008 and a call is only allowed if its worst case
    (about USD 0.0015, counting possible resends) still fits: two calls go through, the
    third is refused."""
    expensive = (200, api_response(reply("Hm.", "UNDECIDED"), prompt=1400, completion=300, hit=0))
    client, transport, ledger = paid_client(tmp_path, 0.003, [expensive] * 8)
    plan = experiment(c1_config()).plans()[0]
    with pytest.raises(RunAborted, match="BudgetExceededError"):
        execute_run(plan, client, tmp_path / "run")
    outcome = read_json(tmp_path / "run" / OUTCOME_FILE)
    assert outcome["status"] == "aborted" and "call refused" in outcome["status_detail"]
    assert outcome["negotiation"]["end_reason"] == "aborted"
    assert len(read_turns(tmp_path / "run")) == outcome["negotiation"]["turns_used"] == len(transport.calls) == 2
    assert ledger.total_usd() == pytest.approx(2 * 0.00078) and ledger.total_usd() <= 0.003
    assert validate_run_dir(tmp_path / "run") == []


def test_a_turn_that_was_paid_for_is_logged_even_if_its_retry_is_refused(tmp_path):
    """The first reply is unreadable and costs money; the budget guard then refuses the
    retry. The turn must still be in the conversation log, with both attempts accounted for."""
    garbage = (200, api_response("not json at all", prompt=1400, completion=300, hit=0))
    client, transport, ledger = paid_client(tmp_path, 0.002, [garbage] * 2)
    plan = experiment(c1_config()).plans()[0]
    with pytest.raises(RunAborted):
        execute_run(plan, client, tmp_path / "run")
    turns = read_turns(tmp_path / "run")
    assert len(turns) == 1 and len(transport.calls) == 1 and len(ledger.entries()) == 1
    turn = turns[0]
    assert turn["parse_ok"] is False and turn["stance"] == "UNDECIDED" and turn["n_attempts"] == 2
    assert turn["attempts"][0]["raw_output"] == "not json at all" and turn["attempts"][0]["cost_usd"] > 0
    assert turn["attempts"][1]["api_error"].startswith("BudgetExceededError") and turn["attempts"][1]["raw_output"] is None
    assert turn["cost_usd"] == pytest.approx(ledger.total_usd())
    outcome = read_json(tmp_path / "run" / OUTCOME_FILE)
    assert outcome["status"] == "aborted" and outcome["negotiation"]["turns_used"] == 1
    assert validate_run_dir(tmp_path / "run") == []


# --- secrets ---------------------------------------------------------------------------------------


def test_the_api_key_never_reaches_any_log_file(tmp_path):
    """Run a negotiation through the real DeepSeek client (with a fake transport) and
    search every byte it wrote for the key and for anything that looks like a header."""
    replies = [reply("Hospital.", "UNDECIDED"), "broken", reply("You go.", "YOU_GO_FIRST"), reply("Going.", "I_GO_FIRST")]
    client, transport, ledger = paid_client(tmp_path, 0.50, [(200, api_response(text)) for text in replies])
    ledger_path = ledger.path
    run_dir, outcome = run_one(tmp_path, c1_config(), client)
    assert outcome["negotiation"]["llm_calls"] == 4 and outcome["negotiation"]["cost_usd"] > 0
    assert all(call["headers"]["Authorization"].endswith(FAKE_KEY) for call in transport.calls)  # it was used...
    for path in [*run_dir.iterdir(), ledger_path]:
        text = path.read_text(encoding="utf-8")
        assert FAKE_KEY not in text and "Authorization" not in text and "Bearer" not in text, path.name  # ...and never written
    assert read_json(run_dir / CONFIG_FILE)["llm"]["client"] == "deepseek"
    assert len(SpendLedger(ledger_path).entries()) == 4
    assert SpendLedger(ledger_path).total_usd() == pytest.approx(outcome["negotiation"]["cost_usd"])


# --- experiments -----------------------------------------------------------------------------------


def test_run_experiment_writes_one_summary_row_per_run(tmp_path):
    config = ExperimentConfig.load(CONFIG_DIR / "c1_smoke.yaml")
    result = run_experiment(config, client_name="mock", out_root=tmp_path, report=QUIET)
    assert len(result.executed) == 6 and result.skipped == [] and result.aborted is None
    assert result.experiment_dir == tmp_path / "c1_smoke" and result.summary_path == result.experiment_dir / SUMMARY_FILE
    with result.summary_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert tuple(rows[0].keys()) == SUMMARY_COLUMNS
    assert [row["run_id"] for row in rows] == [plan.run_id for plan in config.plans()]
    assert {row["status"] for row in rows} == {"completed"} and {row["collisions"] for row in rows} == {"0"}
    assert [row["higher_priority_first"] for row in rows] == ["true"] * 6  # the mock ranks tasks perfectly
    assert [row["first_speaker"] for row in rows] == ["0", "0", "1", "1", "0", "0"]
    for plan in config.plans():
        assert validate_run_dir(result.experiment_dir / plan.run_id) == []


def test_strategy_1_alone_puts_the_higher_priority_agent_first_exactly_half_the_time(tmp_path):
    """Condition C0 on the paper's 18 doorway variants. Strategy 1 ignores the tasks, and
    the design gives each agent index the higher priority equally often, so the rate is
    exactly 50% -- the figure the paper reports for its non-communicating methods."""
    result = run_experiment(ExperimentConfig.load(CONFIG_DIR / "c0_no_llm.yaml"), out_root=tmp_path, report=QUIET)
    assert len(result.rows) == 18
    assert all(row["status"] == "completed" and row["collisions"] == 0 for row in result.rows)
    assert sum(row["higher_priority_first"] for row in result.rows) == 9
    assert all(row["consensus_reached"] is None and row["cost_usd"] == 0.0 for row in result.rows)


@pytest.mark.parametrize("name", sorted(path.name for path in CONFIG_DIR.glob("*.yaml")))
def test_every_shipped_config_runs_on_the_mock_client(tmp_path, name):
    """Conditions C0 to C4 are all supported: the first two runs of each shipped design
    complete without a collision and leave valid log folders."""
    config = ExperimentConfig.load(CONFIG_DIR / name)
    result = run_experiment(config, client_name="mock", out_root=tmp_path, limit=2, report=QUIET)
    assert len(result.executed) == 2
    for row in result.rows:
        assert row["status"] == "completed" and row["collisions"] == 0, row["run_id"]
        assert validate_run_dir(result.experiment_dir / row["run_id"]) == []
        assert (row["higher_priority_first"] is None) == (config.condition not in ("C0", "C1"))


def test_finished_runs_are_skipped_on_a_second_invocation(tmp_path):
    config = ExperimentConfig.load(CONFIG_DIR / "c1_smoke.yaml")
    first = run_experiment(config, client_name="mock", out_root=tmp_path, limit=3, report=QUIET)
    counting = MockClient(policy="task_priority")
    second = run_experiment(config, client=counting, out_root=tmp_path, report=QUIET)
    assert second.skipped == first.executed and len(second.executed) == 3
    assert len(counting.requests) == 9  # three runs of three turns: nothing was paid for twice
    assert len(second.rows) == 6
    third = run_experiment(config, client=MockClient(policy="task_priority"), out_root=tmp_path, overwrite=True, report=QUIET)
    assert len(third.executed) == 6 and third.skipped == []


def test_a_rehearsal_folder_is_never_mistaken_for_a_real_run(tmp_path):
    config = ExperimentConfig.load(CONFIG_DIR / "c1_smoke.yaml")
    run_experiment(config, client_name="mock", out_root=tmp_path, limit=1, report=QUIET)
    paid, transport, _ = paid_client(tmp_path, 0.50, [(200, api_response())])
    with pytest.raises(ConfigError, match="already holds a run made with client 'mock'"):
        run_experiment(config, client=paid, out_root=tmp_path, limit=1, report=QUIET)
    assert transport.calls == []


def test_mock_runs_go_to_an_ignored_folder_by_default():
    from negsim.experiment import MOCK_RUNS_DIR, RUNS_DIR

    assert RUNS_DIR == PACKAGE_ROOT / "runs" and MOCK_RUNS_DIR == PACKAGE_ROOT / "runs_mock"
    ignored = (PACKAGE_ROOT.parent / ".gitignore").read_text(encoding="utf-8")
    assert "llm_negotiation/runs_mock/" in ignored


def test_an_aborted_experiment_stops_and_can_be_resumed(tmp_path):
    config = ExperimentConfig.load(CONFIG_DIR / "c1_smoke.yaml")
    responses = [(200, api_response(reply("Hm.", "UNDECIDED")))] * 60
    ledger = SpendLedger(tmp_path / "ledger.jsonl")

    def paid(cap):
        return paid_client(tmp_path, cap, responses, ledger)[0]

    stopped = run_experiment(config, client=paid(0.002), out_root=tmp_path, report=QUIET)
    assert stopped.aborted and "BudgetExceededError" in stopped.aborted
    assert len(stopped.executed) < 6 and ledger.total_usd() <= 0.002
    aborted_run = config.plans()[len(stopped.executed)].run_id
    assert read_json(tmp_path / "c1_smoke" / aborted_run / OUTCOME_FILE)["status"] == "aborted"
    resumed = run_experiment(config, client=paid(0.50), out_root=tmp_path, report=QUIET)
    assert resumed.aborted is None and resumed.skipped == stopped.executed
    assert aborted_run in resumed.executed and len(resumed.rows) == 6  # the aborted run was redone


def test_worst_case_cost_is_an_upper_bound_well_under_the_cap_for_the_smoke_runs():
    for name in ("c1_smoke.yaml", "c2_smoke.yaml"):
        config = ExperimentConfig.load(CONFIG_DIR / name)
        bound = worst_case_cost(config, config.plans(), sends_per_call=3)
        assert 0 < bound < 0.50, (name, bound)
    c0 = ExperimentConfig.load(CONFIG_DIR / "c0_no_llm.yaml")
    assert worst_case_cost(c0, c0.plans()) == 0.0


# --- the log schema --------------------------------------------------------------------------------


@pytest.fixture()
def good_run(tmp_path):
    run_dir, _ = run_one(tmp_path, c1_config(), MockClient(policy="task_priority"), name="good")
    return run_dir


def test_schema_check_passes_on_a_real_run(good_run):
    assert validate_run_dir(good_run) == []


@pytest.mark.parametrize("missing", RUN_FILES)
def test_schema_check_notices_a_missing_file(good_run, missing):
    (good_run / missing).unlink()
    assert validate_run_dir(good_run) == [f"missing file {missing}"]


@pytest.mark.parametrize(
    "file, key",
    [(CONFIG_FILE, "seed"), (CONFIG_FILE, "git"), (CONFIG_FILE, "participants"), (OUTCOME_FILE, "fallback_used"), (OUTCOME_FILE, "path_deviation_m"), (OUTCOME_FILE, "ground_truth")],
)
def test_schema_check_notices_a_missing_field(good_run, file, key):
    data = read_json(good_run / file)
    del data[key]
    (good_run / file).write_text(json.dumps(data), encoding="utf-8")
    assert f"{file}: missing key '{key}'" in validate_run_dir(good_run)


def test_schema_check_notices_a_damaged_conversation_or_trajectory(good_run, tmp_path):
    for damage in ("turn_field", "turn_count", "transcript", "trajectory"):
        copy_dir = tmp_path / damage
        shutil.copytree(good_run, copy_dir)
        turns = read_turns(copy_dir)
        if damage == "turn_field":
            del turns[1]["raw_output"]
        elif damage == "turn_count":
            turns = turns[:-1]
        if damage in ("turn_field", "turn_count"):
            (copy_dir / CONVERSATION_FILE).write_text("\n".join(json.dumps(t) for t in turns) + "\n", encoding="utf-8")
        elif damage == "transcript":
            text = (copy_dir / TRANSCRIPT_FILE).read_text(encoding="utf-8")
            (copy_dir / TRANSCRIPT_FILE).write_text(text.replace(turns[0]["message"], "something else"), encoding="utf-8")
        else:
            (copy_dir / TRAJECTORY_FILE).write_text("step,time\n0,0\n", encoding="utf-8")
        assert validate_run_dir(copy_dir) != [], damage


def test_trajectory_plot_is_drawn_from_the_log_folder(good_run, tmp_path):
    pytest.importorskip("matplotlib")
    from negsim.viz.trajectory_plot import plot_run

    image = plot_run(good_run, tmp_path / "plot.png")
    assert image.is_file() and image.stat().st_size > 5000
    assert sorted(path.name for path in good_run.iterdir()) == sorted(RUN_FILES)  # nothing added to the logs
