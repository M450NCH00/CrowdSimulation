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

Version 3 (issue #28) adds rules to the avoidance run: a new file of pair interactions
(``pair_interactions.jsonl``: each pair's outcome category, and every rule evaluation and
match), the baseline and the perturbation in ``config.json``, the directive's later
changes and the expiry of its ``speed_scale`` in ``interactions.jsonl``, two rule events,
and the outcome categories and rule counts in ``outcome.json``. A negotiation run is as in
version 2. Folders written under version 2 are checked against version 2.

Version 4 (issue #30) adds pair exposure and the severity tiers to the avoidance run: in
``pair_interactions.jsonl`` the pair's own exposure, its first exposed step, its tier and
what decided it, and ``pair_exposed`` beside the per-agent ``exposed``; in ``outcome.json``
the tier counts and the total pair exposure; and the two new metric thresholds. A
negotiation run is as in version 3. Folders written under version 3 are checked against
version 3.

Version 5 (issue #32) adds backing up: the directive field ``back_up`` in
``interactions.jsonl``; a ``back_up`` column in ``trajectory.csv`` (the phase of the agent's
back-up manoeuvre); a ``back_up`` event; in ``outcome.json`` a ``back_up`` block (every
manoeuvre, and its times and distances per agent) and, among the artefacts, how far each agent
walked backwards on steps that count toward the artefact; three summary columns. Perception
records are version 3 (the passage fields and the group). A negotiation run is as in version 4.
Folders written under version 4 are checked against version 4.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

LOG_SCHEMA_VERSION = 5
SUPPORTED_LOG_SCHEMA_VERSIONS = (1, 2, 3, 4, 5)

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
PAIR_INTERACTIONS_FILE = "pair_interactions.jsonl"
EVENTS_FILE = "events.jsonl"
#: The files of a negotiation run.
RUN_FILES = (CONFIG_FILE, CONVERSATION_FILE, TRAJECTORY_FILE, OUTCOME_FILE, TRANSCRIPT_FILE)
#: The files of an avoidance run (version 3; version 2 had no pair interactions).
AVOIDANCE_RUN_FILES = (CONFIG_FILE, TRAJECTORY_FILE, INTERACTIONS_FILE, PAIR_INTERACTIONS_FILE, EVENTS_FILE, OUTCOME_FILE)
AVOIDANCE_RUN_FILES_V2 = tuple(name for name in AVOIDANCE_RUN_FILES if name != PAIR_INTERACTIONS_FILE)

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
    "seeding",
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
    "baseline",
    "perturbation",
)
#: As version 3 wrote it, without ``seeding``; version 2 had no baseline or perturbation either.
AVOIDANCE_CONFIG_KEYS_V3 = tuple(key for key in AVOIDANCE_CONFIG_KEYS if key != "seeding")
AVOIDANCE_CONFIG_KEYS_V2 = AVOIDANCE_CONFIG_KEYS_V3[:-2]

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
    "back_up",
)
#: As versions 2 to 4 wrote it, without the back-up phase (issue #32).
AVOIDANCE_TRAJECTORY_COLUMNS_V4 = AVOIDANCE_TRAJECTORY_COLUMNS[:-1]

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
    "directive_changes",
    "speed_scale_expired_step",
    "speed_scale_expired_time_s",
    "effective",
    "perceived_time_s",
    "conflict_exposure_time_s",
    "arbiter_time_s",
    "min_separation_m",
)
INTERACTION_KEYS_V2 = tuple(
    key for key in INTERACTION_KEYS if key not in ("directive_changes", "speed_scale_expired_step", "speed_scale_expired_time_s")
)
INTERACTION_END_REASONS = ("out_of_range", "observer_arrived", "neighbour_arrived", "run_ended")

#: ``pair_interactions.jsonl`` (version 4): one line per pair interaction.
PAIR_INTERACTION_KEYS = (
    "pair_id",
    "agents",
    "start_step",
    "start_time_s",
    "encounter_class_at_start",
    "end_step",
    "end_time_s",
    "end_reason",
    "passed_step",
    "passed_time_s",
    "conflict_exposure_time_s",
    "pair_exposure_time_s",
    "first_pair_exposed_step",
    "min_separation_m",
    "outcome",
    "outcome_detail",
    "severity_tier",
    "tier_detail",
    "rules",
)
#: The same, as version 3 wrote it: no pair exposure and no tier.
PAIR_INTERACTION_KEYS_V3 = tuple(
    key
    for key in PAIR_INTERACTION_KEYS
    if key not in ("pair_exposure_time_s", "first_pair_exposed_step", "severity_tier", "tier_detail")
)
PAIR_INTERACTION_END_REASONS = ("out_of_range", "agent_arrived", "run_ended")
PAIR_OUTCOME_DETAIL_KEYS = ("exposed", "pair_exposed", "yield_events", "collisions", "deadlock", "open_at_timeout")
PAIR_OUTCOME_DETAIL_KEYS_V3 = tuple(key for key in PAIR_OUTCOME_DETAIL_KEYS if key != "pair_exposed")
PAIR_TIER_DETAIL_KEYS = ("pair_exposure_time_s", "yield_events", "near_misses", "collisions", "deadlock")
SEVERITY_TIERS = ("T0", "T1", "T2", "T3", "T4")
#: The ``rules`` block of a pair interaction, when the run's provider follows rules.
PAIR_RULE_KEYS = ("state_at_end", "independent_agrees", "evaluations", "matches", "cross_pair_conflicts")
RULE_EVALUATION_KEYS = (
    "from_step",
    "from_time_s",
    "to_step",
    "count",
    "encounter_class",
    "outcome",
    "rule",
    "ambiguous_with",
    "candidates",
    "snapshot",
)
RULE_EVALUATION_OUTCOMES = ("rule_matched", "no_rule_matched", "ambiguous_match", "kept")
RULE_MATCH_KEYS = (
    "rule_id",
    "version",
    "priority",
    "encounter",
    "expiry",
    "outcome",
    "ambiguous_with",
    "from_step",
    "from_time_s",
    "roles",
    "directives",
    "snapshot",
    "to_step",
    "to_time_s",
    "end_reason",
    "replaced_by",
)
RULE_MATCH_END_REASONS = ("passed", "replaced", "out_of_range", "agent_arrived", "run_ended")
INTERACTION_OUTCOMES = ("avoided", "resolved", "failed")

EVENT_TYPES = (
    "reciprocity_violation",
    "handoff",
    "yield",
    "near_miss",
    "collision",
    "wall_collision",
    "ambiguous_match",
    "cross_pair_conflict",
    "back_up",
)
EVENT_TYPES_V4 = EVENT_TYPES[:8]
EVENT_TYPES_V2 = EVENT_TYPES[:6]
#: The phases a ``back_up`` event reports (issue #32).
BACK_UP_EVENT_PHASES = ("started", "out", "ended")
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
    "interaction_outcomes",
    "rules",
    "baseline",
    "artefacts",
    "back_up",
)
AVOIDANCE_OUTCOME_KEYS_V4 = AVOIDANCE_OUTCOME_KEYS[:-1]
AVOIDANCE_OUTCOME_KEYS_V2 = AVOIDANCE_OUTCOME_KEYS[:-5]
ARTEFACT_KEYS = ("thresholds", "agents", "totals")
ARTEFACT_AGENT_KEYS_V4 = ("backward_episodes", "backward_time_s", "hurried_episodes", "hurried_time_s")
ARTEFACT_AGENT_KEYS = ARTEFACT_AGENT_KEYS_V4 + ("backward_distance_m",)
ARTEFACT_TOTAL_KEYS_V4 = ARTEFACT_AGENT_KEYS_V4 + ("agents_backward", "agents_hurried")
ARTEFACT_TOTAL_KEYS = ARTEFACT_AGENT_KEYS + ("agents_backward", "agents_hurried")
#: The ``back_up`` block of an outcome (version 5, issue #32).
BACK_UP_KEYS = ("manoeuvres", "agents", "totals")
BACK_UP_MANOEUVRE_KEYS = (
    "backer", "other", "pair_id", "segment", "travelled_m", "speed_mps", "runout_m", "target_m",
    "start_step", "start_time_s", "out_step", "out_time_s", "end_step", "end_time_s", "end_reason",
    "backing_time_s", "waiting_time_s", "backing_distance_m",
)
BACK_UP_AGENT_KEYS = ("manoeuvres", "backing_time_s", "waiting_time_s", "backing_distance_m")
BACK_UP_END_REASONS = ("other_cleared", "other_arrived", "pair_ended", "run_ended")
#: An entry of an outcome's ``single_file`` (version 5 adds when each agent came out at the far end).
SINGLE_FILE_KEYS = ("segment", "entry_time_s", "first_through", "exit_time_s", "first_out")
INTERACTION_OUTCOME_KEYS = ("pairs", "avoided", "resolved", "failed", "pairs_with", "tiers")
INTERACTION_OUTCOME_KEYS_V3 = INTERACTION_OUTCOME_KEYS[:-1]
RULE_SUMMARY_KEYS = (
    "evaluations",
    "matches_begun",
    "match_ends",
    "cross_pair_conflicts",
    "formation_checks",
    "formation_mismatches",
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
    "pair_exposure_time_s",
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
AVOIDANCE_TOTAL_KEYS_V3 = tuple(key for key in AVOIDANCE_TOTAL_KEYS if key != "pair_exposure_time_s")

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
    "baseline",
    "ruleset",
    "pairs",
    "avoided",
    "resolved",
    "failed",
    "rules_fired",
    "ambiguous_matches",
    "cross_pair_conflicts",
    "backward_episodes",
    "hurried_episodes",
    "pair_exposure_time_s",
    "pairs_t0",
    "pairs_t1",
    "pairs_t2",
    "pairs_t3",
    "pairs_t4",
    "back_up_manoeuvres",
    "backing_distance_m",
    "backward_distance_m",
    "first_out",
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
    from ..avoidance.directives import DIRECTIVE_FIELDS, DIRECTIVE_FIELDS_V4
    from ..avoidance.perception import FIELDS_BY_VERSION, NEVER_OBSERVABLE, PERCEPTION_SCHEMA_VERSION

    # A folder is checked against the log schema and the perception record its own config
    # declares, so that one written before either last changed still checks out.
    version = config.get("log_schema_version", LOG_SCHEMA_VERSION)
    v3, v5 = version >= 3, version >= 5
    files = AVOIDANCE_RUN_FILES if v3 else AVOIDANCE_RUN_FILES_V2
    problems = [f"missing file {name}" for name in files if not (run_dir / name).is_file()]
    if problems:
        return problems
    config_keys = AVOIDANCE_CONFIG_KEYS if version >= 4 else AVOIDANCE_CONFIG_KEYS_V3 if v3 else AVOIDANCE_CONFIG_KEYS_V2
    problems += _missing(config, config_keys, CONFIG_FILE)
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
        if header is None or tuple(header) != (AVOIDANCE_TRAJECTORY_COLUMNS if v5 else AVOIDANCE_TRAJECTORY_COLUMNS_V4):
            problems.append(f"{TRAJECTORY_FILE}: header does not match the schema")
        elif next(reader, None) is None:
            problems.append(f"{TRAJECTORY_FILE}: no rows")

    interactions = _read_jsonl(run_dir / INTERACTIONS_FILE)
    for number, interaction in enumerate(interactions):
        where = f"{INTERACTIONS_FILE} line {number + 1}"
        problems += _missing(interaction, INTERACTION_KEYS if v3 else INTERACTION_KEYS_V2, where)
        perception = interaction.get("perception", {})
        problems += _missing(perception, record_fields["record"], f"{where} perception")
        problems += _missing(perception.get("observer", {}), record_fields["observer"], f"{where} perception.observer")
        problems += _missing(
            perception.get("environment", {}), record_fields["environment"], f"{where} perception.environment"
        )
        if record_fields["pair"]:
            problems += _missing(perception.get("pair") or {}, record_fields["pair"], f"{where} perception.pair")
        problems += _missing(interaction.get("directive", {}), DIRECTIVE_FIELDS if v5 else DIRECTIVE_FIELDS_V4, f"{where} directive")
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
    event_types = EVENT_TYPES if v5 else EVENT_TYPES_V4 if v3 else EVENT_TYPES_V2
    for number, event in enumerate(events):
        where = f"{EVENTS_FILE} line {number + 1}"
        problems += _missing(event, EVENT_KEYS, where)
        if event.get("type") not in event_types:
            problems.append(f"{where}: unknown event type {event.get('type')!r}")
    if [event.get("event_index") for event in events] != list(range(len(events))):
        problems.append(f"{EVENTS_FILE}: event_index is not 0, 1, 2, ...")

    outcome = json.loads((run_dir / OUTCOME_FILE).read_text(encoding="utf-8"))
    problems += _missing(outcome, AVOIDANCE_OUTCOME_KEYS if v5 else AVOIDANCE_OUTCOME_KEYS_V4 if v3 else AVOIDANCE_OUTCOME_KEYS_V2, OUTCOME_FILE)
    if outcome.get("status") not in AVOIDANCE_STATUSES:
        problems.append(f"{OUTCOME_FILE}: unknown status {outcome.get('status')!r}")
    agents = outcome.get("agents", {})
    if len(agents) != outcome.get("n_agents"):
        problems.append(f"{OUTCOME_FILE}: agents does not have one entry per agent")
    for agent_id, metrics in agents.items():
        problems += _missing(metrics, AVOIDANCE_AGENT_KEYS, f"{OUTCOME_FILE}.agents.{agent_id}")
    v4 = config.get("log_schema_version", LOG_SCHEMA_VERSION) >= 4
    totals_keys = AVOIDANCE_TOTAL_KEYS if v4 else AVOIDANCE_TOTAL_KEYS_V3
    problems += _missing(outcome.get("totals", {}), totals_keys, f"{OUTCOME_FILE}.totals")

    def count(event_type: str) -> int:
        return sum(1 for event in events if event.get("type") == event_type)

    if len(outcome.get("reciprocity_violations", [])) != count("reciprocity_violation"):
        problems.append(f"{OUTCOME_FILE}: reciprocity_violations does not match {EVENTS_FILE}")
    if len(outcome.get("handoffs", [])) != count("handoff"):
        problems.append(f"{OUTCOME_FILE}: handoffs does not match {EVENTS_FILE}")
    if config.get("logging", {}).get("interactions", True):
        if outcome.get("totals", {}).get("interactions") != len(interactions):
            problems.append(f"{OUTCOME_FILE}: totals.interactions does not match {INTERACTIONS_FILE}")
    if v3:
        problems += _validate_pairs(run_dir, config, outcome)
    if v5:
        problems += _validate_back_up(outcome, count("back_up"))
    return problems


def _validate_back_up(outcome: dict, events: int) -> list[str]:
    """The additions of version 5 (issue #32): the back-up manoeuvres and their counts, and when
    each agent came out of each single-file segment."""
    problems: list[str] = []
    for number, entry in enumerate(outcome.get("single_file") or []):
        problems += _missing(entry, SINGLE_FILE_KEYS, f"{OUTCOME_FILE}.single_file[{number}]")
    block = outcome.get("back_up") or {}
    problems += _missing(block, BACK_UP_KEYS, f"{OUTCOME_FILE}.back_up")
    manoeuvres = block.get("manoeuvres") or []
    for number, entry in enumerate(manoeuvres):
        where = f"{OUTCOME_FILE}.back_up.manoeuvres[{number}]"
        problems += _missing(entry, BACK_UP_MANOEUVRE_KEYS, where)
        if entry.get("end_reason") not in BACK_UP_END_REASONS:
            problems.append(f"{where}: unknown end_reason {entry.get('end_reason')!r}")
    for agent_id, entry in (block.get("agents") or {}).items():
        problems += _missing(entry, BACK_UP_AGENT_KEYS, f"{OUTCOME_FILE}.back_up.agents.{agent_id}")
    problems += _missing(block.get("totals") or {}, BACK_UP_AGENT_KEYS, f"{OUTCOME_FILE}.back_up.totals")
    expected = sum(1 + (entry.get("out_step") is not None) + (entry.get("end_step") is not None) for entry in manoeuvres)
    if events != expected:
        problems.append(f"{OUTCOME_FILE}: back_up.manoeuvres does not match the back_up events of {EVENTS_FILE}")
    return problems


def _validate_pairs(run_dir: Path, config: dict, outcome: dict) -> list[str]:
    """The additions of version 3: pair interactions, their rule records, and the counts;
    and of version 4: pair exposure and the severity tiers."""
    problems: list[str] = []
    v4 = config.get("log_schema_version", LOG_SCHEMA_VERSION) >= 4
    pairs = _read_jsonl(run_dir / PAIR_INTERACTIONS_FILE)
    for number, pair in enumerate(pairs):
        where = f"{PAIR_INTERACTIONS_FILE} line {number + 1}"
        problems += _missing(pair, PAIR_INTERACTION_KEYS if v4 else PAIR_INTERACTION_KEYS_V3, where)
        problems += _missing(
            pair.get("outcome_detail") or {},
            PAIR_OUTCOME_DETAIL_KEYS if v4 else PAIR_OUTCOME_DETAIL_KEYS_V3,
            f"{where} outcome_detail",
        )
        if pair.get("outcome") not in INTERACTION_OUTCOMES:
            problems.append(f"{where}: unknown outcome {pair.get('outcome')!r}")
        if pair.get("end_reason") not in PAIR_INTERACTION_END_REASONS:
            problems.append(f"{where}: unknown end_reason {pair.get('end_reason')!r}")
        if v4:
            if pair.get("severity_tier") not in SEVERITY_TIERS:
                problems.append(f"{where}: unknown severity_tier {pair.get('severity_tier')!r}")
            problems += _missing(pair.get("tier_detail") or {}, PAIR_TIER_DETAIL_KEYS, f"{where} tier_detail")
        rules = pair.get("rules")
        if rules is None:
            continue
        problems += _missing(rules, PAIR_RULE_KEYS, f"{where} rules")
        for entry in rules.get("evaluations", []):
            problems += _missing(entry, RULE_EVALUATION_KEYS, f"{where} rules.evaluations")
            if entry.get("outcome") not in RULE_EVALUATION_OUTCOMES:
                problems.append(f"{where}: unknown evaluation outcome {entry.get('outcome')!r}")
        for entry in rules.get("matches", []):
            problems += _missing(entry, RULE_MATCH_KEYS, f"{where} rules.matches")
            if entry.get("end_reason") not in RULE_MATCH_END_REASONS:
                problems.append(f"{where}: unknown end_reason of a match {entry.get('end_reason')!r}")
    if [pair.get("pair_id") for pair in pairs] != list(range(len(pairs))):
        problems.append(f"{PAIR_INTERACTIONS_FILE}: pair_id is not 0, 1, 2, ...")

    counts = outcome.get("interaction_outcomes") or {}
    problems += _missing(
        counts, INTERACTION_OUTCOME_KEYS if v4 else INTERACTION_OUTCOME_KEYS_V3, f"{OUTCOME_FILE}.interaction_outcomes"
    )
    if sum(counts.get(name, 0) for name in INTERACTION_OUTCOMES) != counts.get("pairs"):
        problems.append(f"{OUTCOME_FILE}: avoided + resolved + failed is not the number of pairs")
    tiers = counts.get("tiers") or {}
    if v4 and sum(tiers.get(tier, 0) for tier in SEVERITY_TIERS) != counts.get("pairs"):
        problems.append(f"{OUTCOME_FILE}: the tier counts do not add up to the number of pairs")
    if config.get("logging", {}).get("interactions", True):
        if counts.get("pairs") != len(pairs):
            problems.append(f"{OUTCOME_FILE}: interaction_outcomes.pairs does not match {PAIR_INTERACTIONS_FILE}")
        for name in INTERACTION_OUTCOMES:
            if counts.get(name) != sum(1 for pair in pairs if pair.get("outcome") == name):
                problems.append(f"{OUTCOME_FILE}: interaction_outcomes.{name} does not match {PAIR_INTERACTIONS_FILE}")
        if v4:
            for tier in SEVERITY_TIERS:
                if tiers.get(tier) != sum(1 for pair in pairs if pair.get("severity_tier") == tier):
                    problems.append(f"{OUTCOME_FILE}: interaction_outcomes.tiers.{tier} does not match {PAIR_INTERACTIONS_FILE}")
    if outcome.get("rules") is not None:
        problems += _missing(outcome["rules"], RULE_SUMMARY_KEYS, f"{OUTCOME_FILE}.rules")
    v5 = config.get("log_schema_version", LOG_SCHEMA_VERSION) >= 5
    artefacts = outcome.get("artefacts") or {}
    problems += _missing(artefacts, ARTEFACT_KEYS, f"{OUTCOME_FILE}.artefacts")
    for agent_id, entry in (artefacts.get("agents") or {}).items():
        problems += _missing(entry, ARTEFACT_AGENT_KEYS if v5 else ARTEFACT_AGENT_KEYS_V4, f"{OUTCOME_FILE}.artefacts.agents.{agent_id}")
    problems += _missing(artefacts.get("totals") or {}, ARTEFACT_TOTAL_KEYS if v5 else ARTEFACT_TOTAL_KEYS_V4, f"{OUTCOME_FILE}.artefacts.totals")
    return problems
