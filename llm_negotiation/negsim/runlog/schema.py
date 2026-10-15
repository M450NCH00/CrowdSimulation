"""The log schema: which files a run writes and which fields each must contain.

``docs/log-schema.md`` describes every field in words. The lists here are the machine-
checkable part: :func:`validate_run_dir` verifies a run folder against them, and is used
both by the tests and by the runner as a self-check after each run.

Bump :data:`LOG_SCHEMA_VERSION` whenever a field is added, removed, renamed or changes
meaning, and describe the change in ``docs/log-schema.md``.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

LOG_SCHEMA_VERSION = 1

CONFIG_FILE = "config.json"
CONVERSATION_FILE = "conversation.jsonl"
TRAJECTORY_FILE = "trajectory.csv"
OUTCOME_FILE = "outcome.json"
TRANSCRIPT_FILE = "transcript.md"
SUMMARY_FILE = "summary.csv"
RUN_FILES = (CONFIG_FILE, CONVERSATION_FILE, TRAJECTORY_FILE, OUTCOME_FILE, TRANSCRIPT_FILE)

CONFIG_KEYS = (
    "log_schema_version",
    "experiment_name",
    "run_id",
    "run_index",
    "condition",
    "seed",
    "repeat",
    "created_utc",
    "git",
    "software",
    "scenario_file",
    "scenario_variant",
    "scenario",
    "participants",
    "assignment",
    "negotiation",
    "llm",
    "arbitration",
    "scoring",
    "budget",
)
CONFIG_NEGOTIATION_KEYS = (
    "enabled",
    "prompt_template",
    "max_messages_per_agent",
    "first_speaker",
    "timing",
    "info_variant",
    "info_fields",
    "visibility",
    "rendered_system_prompts",
)
CONFIG_LLM_KEYS = ("client", "model", "temperature", "max_tokens", "thinking", "json_mode")

TURN_KEYS = (
    "turn_index",
    "speaker",
    "sim_time_s",
    "wall_clock_utc",
    "situation_report",
    "situation_values",
    "prompt_messages",
    "raw_output",
    "message",
    "stance",
    "parse_ok",
    "parse_error",
    "n_attempts",
    "tokens",
    "cost_usd",
    "latency_s",
    "attempts",
)
ATTEMPT_KEYS = (
    "attempt",
    "wall_clock_utc",
    "prompt_messages",
    "request",
    "raw_output",
    "finish_reason",
    "response_id",
    "model",
    "system_fingerprint",
    "usage",
    "cost_usd",
    "price_tier",
    "latency_s",
    "parse_error",
    "api_error",
)

TRAJECTORY_COLUMNS = (
    "step",
    "time_s",
    "agent_id",
    "x_m",
    "y_m",
    "theta_rad",
    "path_s_m",
    "v_mps",
    "omega_radps",
    "speed_bound_mps",
    "role",
    "role_source",
    "in_conflict",
    "zone_d_in_m",
    "zone_d_out_m",
    "dialogue_active",
)

OUTCOME_KEYS = (
    "log_schema_version",
    "run_id",
    "status",
    "status_detail",
    "sim_time_s",
    "steps",
    "negotiation",
    "roles",
    "fallback_used",
    "fallback_reasons",
    "collisions",
    "deadlock",
    "makespan_s",
    "time_to_goal_s",
    "region_entry_time_s",
    "first_through",
    "follower",
    "follower_min_speed_mps",
    "min_speed_before_region_mps",
    "path_deviation_m",
    "ground_truth",
)
OUTCOME_NEGOTIATION_KEYS = (
    "enabled",
    "started",
    "start_time_s",
    "end_time_s",
    "end_reason",
    "consensus_reached",
    "turns_used",
    "messages_per_agent",
    "stances",
    "negotiated_leader",
    "llm_calls",
    "parse_failures",
    "retries",
    "tokens",
    "cost_usd",
    "llm_latency_s",
)

SUMMARY_COLUMNS = (
    "experiment_name",
    "run_id",
    "condition",
    "scenario",
    "scenario_variant",
    "info_variant",
    "seed",
    "repeat",
    "agent0_persona",
    "agent0_age",
    "agent0_gender",
    "agent0_task_type",
    "agent0_task",
    "agent0_side",
    "agent1_persona",
    "agent1_age",
    "agent1_gender",
    "agent1_task_type",
    "agent1_task",
    "agent1_side",
    "swap_sides",
    "first_speaker",
    "timing_mode",
    "prompt_template",
    "model",
    "temperature",
    "status",
    "consensus_reached",
    "turns_used",
    "end_reason",
    "negotiated_leader",
    "first_through",
    "negotiated_roles_followed",
    "fallback_used",
    "collisions",
    "deadlock",
    "makespan_s",
    "time_to_goal_0_s",
    "time_to_goal_1_s",
    "follower",
    "follower_min_speed_mps",
    "path_deviation_m",
    "higher_priority_agent",
    "higher_priority_first",
    "higher_priority_time_to_goal_s",
    "llm_calls",
    "parse_failures",
    "prompt_tokens",
    "completion_tokens",
    "cost_usd",
    "llm_latency_s",
    "git_commit",
)

STATUSES = ("completed", "collision", "deadlock", "timeout", "aborted")


def _missing(mapping: dict, keys: tuple[str, ...], where: str) -> list[str]:
    return [f"{where}: missing key {key!r}" for key in keys if key not in mapping]


def validate_run_dir(run_dir: Path | str) -> list[str]:
    """Check a run folder against the schema. Returns a list of problems (empty if none)."""
    run_dir = Path(run_dir)
    problems = [f"missing file {name}" for name in RUN_FILES if not (run_dir / name).is_file()]
    if problems:
        return problems

    config = json.loads((run_dir / CONFIG_FILE).read_text(encoding="utf-8"))
    problems += _missing(config, CONFIG_KEYS, CONFIG_FILE)
    problems += _missing(config.get("negotiation", {}), CONFIG_NEGOTIATION_KEYS, f"{CONFIG_FILE}.negotiation")
    problems += _missing(config.get("llm", {}), CONFIG_LLM_KEYS, f"{CONFIG_FILE}.llm")
    if config.get("log_schema_version") != LOG_SCHEMA_VERSION:
        problems.append(f"{CONFIG_FILE}: log_schema_version is not {LOG_SCHEMA_VERSION}")

    turns = []
    with (run_dir / CONVERSATION_FILE).open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle):
            if not line.strip():
                continue
            turn = json.loads(line)
            turns.append(turn)
            problems += _missing(turn, TURN_KEYS, f"{CONVERSATION_FILE} line {number + 1}")
            for attempt in turn.get("attempts", []):
                problems += _missing(attempt, ATTEMPT_KEYS, f"{CONVERSATION_FILE} line {number + 1} attempt")
    if [turn.get("turn_index") for turn in turns] != list(range(len(turns))):
        problems.append(f"{CONVERSATION_FILE}: turn_index is not 0, 1, 2, ...")

    with (run_dir / TRAJECTORY_FILE).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header is None or tuple(header) != TRAJECTORY_COLUMNS:
            problems.append(f"{TRAJECTORY_FILE}: header does not match the schema")
        elif next(reader, None) is None:
            problems.append(f"{TRAJECTORY_FILE}: no rows")

    outcome = json.loads((run_dir / OUTCOME_FILE).read_text(encoding="utf-8"))
    problems += _missing(outcome, OUTCOME_KEYS, OUTCOME_FILE)
    problems += _missing(outcome.get("negotiation", {}), OUTCOME_NEGOTIATION_KEYS, f"{OUTCOME_FILE}.negotiation")
    if outcome.get("status") not in STATUSES:
        problems.append(f"{OUTCOME_FILE}: unknown status {outcome.get('status')!r}")
    if outcome.get("negotiation", {}).get("turns_used") != len(turns):
        problems.append(f"{OUTCOME_FILE}: turns_used does not match {CONVERSATION_FILE}")

    transcript = (run_dir / TRANSCRIPT_FILE).read_text(encoding="utf-8")
    for turn in turns:
        if turn.get("message") and turn["message"] not in transcript:
            problems.append(f"{TRANSCRIPT_FILE}: turn {turn.get('turn_index')} message is missing")
    return problems
