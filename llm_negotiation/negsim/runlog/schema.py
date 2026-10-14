"""The log schema: which files a run writes and which fields each must contain.

``docs/log-schema.md`` describes every field in words. The lists here are the machine-
checkable part: :func:`validate_run_dir` verifies a run folder against them, and is used
both by the tests and by the runner as a self-check after each run.

Bump :data:`LOG_SCHEMA_VERSION` whenever a field is added, removed, renamed or changes
meaning, and describe the change in ``docs/log-schema.md``.

Version 2 (issue #26) added a second kind of run. Every ``config.json`` now says which
kind it is in ``run_kind``:

``negotiation``
    A run of issue #24: two agents, an optional dialogue, the arbiter. Its files and
    fields are those of version 1 plus ``run_kind``.
``avoidance``
    A run of the avoidance layer: any number of agents under ORCA and directives. It has
    its own set of files (:data:`AVOIDANCE_RUN_FILES`) and its own fields.

A folder written under version 1 is still valid and is checked against version 1.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

LOG_SCHEMA_VERSION = 2
SUPPORTED_LOG_SCHEMA_VERSIONS = (1, 2)

RUN_KIND_NEGOTIATION = "negotiation"
RUN_KIND_AVOIDANCE = "avoidance"
RUN_KINDS = (RUN_KIND_NEGOTIATION, RUN_KIND_AVOIDANCE)

CONFIG_FILE = "config.json"
CONVERSATION_FILE = "conversation.jsonl"
TRAJECTORY_FILE = "trajectory.csv"
OUTCOME_FILE = "outcome.json"
TRANSCRIPT_FILE = "transcript.md"
SUMMARY_FILE = "summary.csv"
INTERACTIONS_FILE = "interactions.jsonl"
EVENTS_FILE = "events.jsonl"
#: The files of a negotiation run.
RUN_FILES = (CONFIG_FILE, CONVERSATION_FILE, TRAJECTORY_FILE, OUTCOME_FILE, TRANSCRIPT_FILE)
#: The files of an avoidance run.
AVOIDANCE_RUN_FILES = (CONFIG_FILE, TRAJECTORY_FILE, INTERACTIONS_FILE, EVENTS_FILE, OUTCOME_FILE)

CONFIG_KEYS = (
    "log_schema_version",
    "run_kind",
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

#: ``config.json`` of a negotiation run as version 1 wrote it: no ``run_kind``.
CONFIG_KEYS_V1 = tuple(key for key in CONFIG_KEYS if key != "run_kind")

# --- avoidance runs (version 2) -----------------------------------------------------------------

AVOIDANCE_CONFIG_KEYS = (
    "log_schema_version",
    "run_kind",
    "experiment_name",
    "run_id",
    "run_index",
    "seed",
    "repeat",
    "created_utc",
    "git",
    "software",
    "scenario_file",
    "variant",
    "scenario",
    "population",
    "visibility",
    "directives",
    "arbitration",
    "logging",
    "perception_schema_version",
)

AVOIDANCE_TRAJECTORY_COLUMNS = (
    "step",
    "time_s",
    "agent_id",
    "x_m",
    "y_m",
    "theta_rad",
    "path_s_m",
    "vx_mps",
    "vy_mps",
    "speed_mps",
    "pref_vx_mps",
    "pref_vy_mps",
    "control_mode",
    "speed_bound_mps",
    "role",
    "role_source",
    "in_conflict",
    "zone_d_in_m",
    "zone_d_out_m",
    "n_neighbours",
    "speed_scale",
    "exposed",
    "fallback",
    "interactions",
)

INTERACTION_KEYS = (
    "interaction_id",
    "observer_id",
    "neighbour_id",
    "start_step",
    "start_time_s",
    "end_step",
    "end_time_s",
    "end_reason",
    "perception",
    "directive",
    "effective",
    "perceived_time_s",
    "conflict_exposure_time_s",
    "arbiter_time_s",
    "min_separation_m",
)
INTERACTION_END_REASONS = ("out_of_range", "observer_arrived", "neighbour_arrived", "run_ended")

EVENT_TYPES = ("reciprocity_violation", "handoff", "yield", "near_miss", "collision", "wall_collision")
EVENT_KEYS = ("event_index", "type", "time_s")

AVOIDANCE_OUTCOME_KEYS = (
    "log_schema_version",
    "run_kind",
    "run_id",
    "status",
    "sim_time_s",
    "steps",
    "n_agents",
    "arrived",
    "collisions",
    "deadlock",
    "makespan_s",
    "time_to_goal_s",
    "agents",
    "totals",
    "single_file",
    "reciprocity_violations",
    "handoffs",
    "thresholds",
)
AVOIDANCE_AGENT_KEYS = (
    "time_to_goal_s",
    "distance_m",
    "path_deviation_mean_m",
    "path_deviation_max_m",
    "interactions",
    "interaction_time_s",
    "conflict_exposure_time_s",
    "orca_altered_time_s",
    "yield_events",
    "yield_time_s",
    "near_misses",
    "min_separation_m",
    "min_wall_gap_m",
    "fallback_steps",
    "one_sided_steps",
    "arbiter_time_s",
)
AVOIDANCE_TOTAL_KEYS = (
    "interactions",
    "conflict_exposure_time_s",
    "yield_events",
    "yield_time_s",
    "near_misses",
    "min_separation_m",
    "mean_time_to_goal_s",
    "mean_path_deviation_m",
    "max_path_deviation_m",
    "steps_with_fallback",
    "fallback_agent_steps",
    "one_sided_agent_steps",
)

AVOIDANCE_SUMMARY_COLUMNS = (
    "experiment_name",
    "run_id",
    "scenario",
    "variant",
    "seed",
    "repeat",
    "n_agents",
    "provider",
    "arbitration_enabled",
    "status",
    "arrived",
    "collisions",
    "max_overlap_m",
    "deadlock",
    "makespan_s",
    "mean_time_to_goal_s",
    "conflict_exposure_time_s",
    "yield_events",
    "yield_time_s",
    "near_misses",
    "min_separation_m",
    "steps_with_fallback",
    "fallback_agent_steps",
    "reciprocity_violations",
    "handoffs",
    "first_through",
    "time_to_goal_0_s",
    "time_to_goal_1_s",
    "path_deviation_max_0_m",
    "path_deviation_max_1_m",
    "conflict_exposure_0_s",
    "conflict_exposure_1_s",
    "git_commit",
)

#: An avoidance run makes no model call, so it cannot be ``aborted``.
AVOIDANCE_STATUSES = ("completed", "collision", "deadlock", "timeout")


def _missing(mapping: dict, keys: tuple[str, ...], where: str) -> list[str]:
    return [f"{where}: missing key {key!r}" for key in keys if key not in mapping]


def validate_run_dir(run_dir: Path | str) -> list[str]:
    """Check a run folder against the schema. Returns a list of problems (empty if none).

    The folder is checked against the version and the kind of run its own ``config.json``
    declares, so a folder written before the schema was last changed still checks out.
    """
    run_dir = Path(run_dir)
    if not (run_dir / CONFIG_FILE).is_file():
        # Without a config there is no telling what kind of run this was meant to be.
        return [f"missing file {name}" for name in RUN_FILES if not (run_dir / name).is_file()]
    config = json.loads((run_dir / CONFIG_FILE).read_text(encoding="utf-8"))
    version = config.get("log_schema_version")
    if version not in SUPPORTED_LOG_SCHEMA_VERSIONS:
        return [
            f"{CONFIG_FILE}: log_schema_version {version!r} is not one of {list(SUPPORTED_LOG_SCHEMA_VERSIONS)}"
        ]
    kind = config.get("run_kind", RUN_KIND_NEGOTIATION if version == 1 else None)
    if kind == RUN_KIND_AVOIDANCE:
        return _validate_avoidance(run_dir, config)
    if kind == RUN_KIND_NEGOTIATION:
        return _validate_negotiation(run_dir, config, CONFIG_KEYS_V1 if version == 1 else CONFIG_KEYS)
    return [f"{CONFIG_FILE}: run_kind {kind!r} is not one of {list(RUN_KINDS)}"]


def _validate_negotiation(run_dir: Path, config: dict, config_keys: tuple[str, ...]) -> list[str]:
    problems = [f"missing file {name}" for name in RUN_FILES if not (run_dir / name).is_file()]
    if problems:
        return problems

    problems += _missing(config, config_keys, CONFIG_FILE)
    problems += _missing(config.get("negotiation", {}), CONFIG_NEGOTIATION_KEYS, f"{CONFIG_FILE}.negotiation")
    problems += _missing(config.get("llm", {}), CONFIG_LLM_KEYS, f"{CONFIG_FILE}.llm")

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


def _read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _validate_avoidance(run_dir: Path, config: dict) -> list[str]:
    # Imported here: the schema of a negotiation run does not depend on the avoidance layer.
    from ..avoidance.directives import DIRECTIVE_FIELDS
    from ..avoidance.perception import FIELDS_BY_VERSION, NEVER_OBSERVABLE, PERCEPTION_SCHEMA_VERSION

    problems = [f"missing file {name}" for name in AVOIDANCE_RUN_FILES if not (run_dir / name).is_file()]
    if problems:
        return problems
    problems += _missing(config, AVOIDANCE_CONFIG_KEYS, CONFIG_FILE)
    # A folder is checked against the perception record its own config declares, so that
    # one written before the record last changed still checks out.
    perception_version = config.get("perception_schema_version")
    if perception_version not in FIELDS_BY_VERSION:
        problems.append(
            f"{CONFIG_FILE}: perception_schema_version {perception_version!r} is not one of {sorted(FIELDS_BY_VERSION)}"
        )
        perception_version = PERCEPTION_SCHEMA_VERSION
    record_fields = FIELDS_BY_VERSION[perception_version]

    with (run_dir / TRAJECTORY_FILE).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header is None or tuple(header) != AVOIDANCE_TRAJECTORY_COLUMNS:
            problems.append(f"{TRAJECTORY_FILE}: header does not match the schema")
        elif next(reader, None) is None:
            problems.append(f"{TRAJECTORY_FILE}: no rows")

    interactions = _read_jsonl(run_dir / INTERACTIONS_FILE)
    for number, interaction in enumerate(interactions):
        where = f"{INTERACTIONS_FILE} line {number + 1}"
        problems += _missing(interaction, INTERACTION_KEYS, where)
        perception = interaction.get("perception", {})
        problems += _missing(perception, record_fields["record"], f"{where} perception")
        problems += _missing(perception.get("observer", {}), record_fields["observer"], f"{where} perception.observer")
        problems += _missing(
            perception.get("environment", {}), record_fields["environment"], f"{where} perception.environment"
        )
        if record_fields["pair"]:
            problems += _missing(perception.get("pair") or {}, record_fields["pair"], f"{where} perception.pair")
        problems += _missing(interaction.get("directive", {}), DIRECTIVE_FIELDS, f"{where} directive")
        if interaction.get("end_reason") not in INTERACTION_END_REASONS:
            problems.append(f"{where}: unknown end_reason {interaction.get('end_reason')!r}")
        for block in ("neighbour_attributes",), ("observer", "attributes"):
            attributes = perception
            for key in block:
                attributes = attributes.get(key, {}) if isinstance(attributes, dict) else {}
            leaked = sorted(NEVER_OBSERVABLE & set(attributes))
            if leaked:
                problems.append(f"{where}: {'.'.join(block)} contains {leaked}, which is never observable")
    if [interaction.get("interaction_id") for interaction in interactions] != list(range(len(interactions))):
        problems.append(f"{INTERACTIONS_FILE}: interaction_id is not 0, 1, 2, ...")

    events = _read_jsonl(run_dir / EVENTS_FILE)
    for number, event in enumerate(events):
        where = f"{EVENTS_FILE} line {number + 1}"
        problems += _missing(event, EVENT_KEYS, where)
        if event.get("type") not in EVENT_TYPES:
            problems.append(f"{where}: unknown event type {event.get('type')!r}")
    if [event.get("event_index") for event in events] != list(range(len(events))):
        problems.append(f"{EVENTS_FILE}: event_index is not 0, 1, 2, ...")

    outcome = json.loads((run_dir / OUTCOME_FILE).read_text(encoding="utf-8"))
    problems += _missing(outcome, AVOIDANCE_OUTCOME_KEYS, OUTCOME_FILE)
    if outcome.get("status") not in AVOIDANCE_STATUSES:
        problems.append(f"{OUTCOME_FILE}: unknown status {outcome.get('status')!r}")
    agents = outcome.get("agents", {})
    if len(agents) != outcome.get("n_agents"):
        problems.append(f"{OUTCOME_FILE}: agents does not have one entry per agent")
    for agent_id, metrics in agents.items():
        problems += _missing(metrics, AVOIDANCE_AGENT_KEYS, f"{OUTCOME_FILE}.agents.{agent_id}")
    problems += _missing(outcome.get("totals", {}), AVOIDANCE_TOTAL_KEYS, f"{OUTCOME_FILE}.totals")

    def count(event_type: str) -> int:
        return sum(1 for event in events if event.get("type") == event_type)

    if len(outcome.get("reciprocity_violations", [])) != count("reciprocity_violation"):
        problems.append(f"{OUTCOME_FILE}: reciprocity_violations does not match {EVENTS_FILE}")
    if len(outcome.get("handoffs", [])) != count("handoff"):
        problems.append(f"{OUTCOME_FILE}: handoffs does not match {EVENTS_FILE}")
    if config.get("logging", {}).get("interactions", True):
        if outcome.get("totals", {}).get("interactions") != len(interactions):
            problems.append(f"{OUTCOME_FILE}: totals.interactions does not match {INTERACTIONS_FILE}")
    return problems
