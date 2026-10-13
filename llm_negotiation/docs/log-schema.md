# Log schema, version 1

The logs are this platform's research output: rule extraction will be done from them. This
file says what every file and field means. The machine-checkable part of the schema, the
list of required fields, is in `negsim/runlog/schema.py`; `validate_run_dir` checks a run
folder against it, and the runner runs that check on every folder it writes.

**Versioning.** `log_schema_version` is written into every `config.json` and
`outcome.json`. Raise `LOG_SCHEMA_VERSION` whenever a field is added, removed, renamed or
changes meaning, and add a line to the change log at the end of this file.

## Layout

```
llm_negotiation/
  spend_ledger.jsonl                 one line per paid API call, across all experiments
  runs/<experiment_name>/
    summary.csv                      one row per run
    <run_id>/
      config.json                    everything that defines the run
      conversation.jsonl             one line per turn of the dialogue
      trajectory.csv                 one row per agent per time step
      outcome.json                   what happened
      transcript.md                  the conversation and outcome, for reading
```

Runs made with the mock client go to `runs_mock/` instead, which git ignores.

Conventions: SI units, with the unit in the field name (`_s`, `_m`, `_mps`, `_rad`,
`_radps`, `_usd`). Agents are numbered 0 and 1; a JSON object keyed by agent uses the
strings `"0"` and `"1"`. Times of day are UTC, ISO 8601. `null` means "does not apply" or
"did not happen", never zero.

## `config.json`

The fully resolved configuration: defaults filled in, overrides applied.

| Field | Meaning |
|---|---|
| `log_schema_version` | 1 |
| `experiment_name`, `run_id`, `run_index` | Which experiment; this run's id (also its folder name); its position in the design, from 1 |
| `condition` | `C0` to `C4` |
| `seed` | The run's seed: the design's base seed plus `run_index`. Governs the simulator's random choices only (task phrasing, a random tie-break). The model cannot be seeded. |
| `repeat` | Which repetition of an identical cell, from 1 |
| `created_utc` | When the run started |
| `git.commit`, `git.dirty` | Commit of the code that produced the run, and whether the working tree differed from it. Run folders and the ledger are not counted as differences. |
| `software` | `negsim_version`, `python` |
| `scenario_file`, `scenario_variant` | Scenario YAML used; name of the variant (`base` if the design has none) |
| `scenario` | The resolved scenario: `type`, `dt_s`, `max_time_s`, `goal_tolerance_m`, `geometry`, `swap_sides`, `start_offsets_m`, `region` (kind, width, length), `conflict` (predictor, safety margin, zone half-length), `observation`, `deadlock`, `controller`, `obstacles`, and `agents` |
| `scenario.agents[]` | Per agent: `agent_id`, `side` it starts on, `radius_m`, `max_speed_mps`, `max_turn_rate_radps`, `initial_speed_mps`, `start`, `goal`, desired `path`, `path_length_m`, and where along the path the physical conflict region begins and ends (`region_entry_s_m`, `region_exit_s_m`) |
| `participants[]` | Per agent: `agent_id`, `side`, `task` (the text put in the prompt), `task_type` (a label, or null), and `persona` (`persona_id`, `age`, `gender`, `backstory`, `task`), null for a task-only agent |
| `assignment` | How the config described each agent (`agent_0`, `agent_1`: persona id, overrides, task type), `swap_sides`, `first_speaker` |
| `negotiation.enabled` | false for condition C0 |
| `negotiation.prompt_template` | `key`, `id`, `version` and `sha256` of the template file |
| `negotiation.max_messages_per_agent` | Message limit per agent |
| `negotiation.first_speaker` | Agent that opens the dialogue |
| `negotiation.timing` | `mode` (`pre_conflict` or `concurrent`), `seconds_per_message` |
| `negotiation.info_variant`, `.info_fields` | Name of the information setting, and the situation-report fields that were switched on |
| `negotiation.visibility` | For each attribute, whether an agent could see it of the other |
| `negotiation.rendered_system_prompts` | The exact system prompt given to each agent (`agent_0`, `agent_1`) |
| `llm` | `client` (`deepseek`, `mock`, or null), `model`, `temperature`, `max_tokens`, `thinking`, `json_mode`, `seed_parameter` (always null: the API has none), and for the paid client `base_url`, `timeout_s`, `max_retries`, `budget_cap_usd`, `spend_ledger`, `prices` (source and date) |
| `arbitration` | `policy` (`strategy1` or `none`), `tie_break` |
| `scoring` | `ground_truth` (`task_priority` or null), `priority_order` |
| `budget` | `cap_usd`, `ledger` |

## `conversation.jsonl`

One JSON object per line, one line per turn. Empty if the run had no dialogue. A turn is
one agent speaking once; it may take two calls to the model if the first reply could not
be read.

| Field | Meaning |
|---|---|
| `turn_index` | From 0 |
| `speaker` | Agent whose turn it is |
| `sim_time_s` | Simulated time of the turn. Always the dialogue's start time in `pre_conflict` mode. |
| `wall_clock_utc` | When the first call of the turn was made |
| `situation_report` | The situation report shown to the speaker, as text; empty if no field was switched on |
| `situation_values` | The numbers behind the report, whether or not each was shown: elapsed time, own and other speed, size, state relative to the conflict region (`approaching`, `inside`, `past`) and distance to it, and the region's kind and size |
| `prompt_messages` | The exact messages sent on the last call of the turn: `[{role, content}, ...]` |
| `raw_output` | The model's reply to that call, verbatim; null if empty |
| `message` | What the other agent is shown: the parsed `message`, or `""` if the turn failed |
| `stance` | `I_GO_FIRST`, `YOU_GO_FIRST` or `UNDECIDED`; `UNDECIDED` if the turn failed |
| `parse_ok` | false if both attempts failed |
| `parse_error` | Why the last attempt failed, or null. Codes: `empty_output`, `not_json`, `not_an_object`, `missing_message`, `message_not_text`, `empty_message`, `missing_stance`, `invalid_stance`, or `api_error: ...` |
| `n_attempts` | 1 or 2 |
| `tokens` | Sums over the attempts: `prompt_tokens`, `completion_tokens`, `prompt_cache_hit_tokens`, `prompt_cache_miss_tokens`, `reasoning_tokens` |
| `cost_usd` | Estimated cost of the turn (0 for the mock) |
| `latency_s` | Wall-clock time spent waiting for the model |
| `attempts[]` | One entry per call, each with `attempt`, `wall_clock_utc`, `prompt_messages`, `request` (model, temperature, max_tokens, json_mode, thinking), `raw_output`, `finish_reason`, `response_id`, `model` and `system_fingerprint` as returned, `usage`, `cost_usd`, `price_tier`, `latency_s`, `parse_error`, `api_error` |

Notes for anyone analysing these:

- **An agent's history contains its own earlier turns re-serialised**, as
  `{"message": ..., "stance": ...}`, not its raw output. For a well-formed reply the two
  differ at most in whitespace and in keys beyond the two required ones.
- **A retry adds two messages** to the prompt of the second attempt, the unreadable reply
  and a request to try again. They are in that attempt's `prompt_messages` and are not
  carried into later turns.
- **What is tolerated when reading a reply:** surrounding whitespace, a Markdown code
  fence, extra keys, and the case of the stance value. Nothing else is repaired.
- **Request headers are never logged.**

## `trajectory.csv`

One row per agent per time step, in time order, then one final row per agent for the state
at the end. A row gives the state at the *start* of a step and the control applied
*during* it. The final rows have empty control columns.

| Column | Meaning |
|---|---|
| `step`, `time_s` | Step number from 0, and its start time |
| `agent_id` | 0 or 1 |
| `x_m`, `y_m`, `theta_rad` | Position of the centre and heading |
| `path_s_m` | Progress along the desired path |
| `v_mps`, `omega_radps` | Linear and angular velocity applied during the step |
| `speed_bound_mps` | The upper bound on speed from the arbiter; the agent's maximum speed if it was not restricted |
| `role` | `leader`, `follower`, or empty if no conflict was live |
| `role_source` | `negotiated`, `strategy1`, or `physical_precedence` (the agreed follower was already inside the zone and could no longer give way) |
| `in_conflict` | Whether a conflict was live: the zone not yet cleared and the two would occupy it at overlapping times |
| `zone_d_in_m`, `zone_d_out_m` | Distance from the centre to where it enters and leaves the conflict zone (`derivations.md`, section 3); negative once passed |
| `dialogue_active` | Whether the dialogue was still going during the step (only ever true in `concurrent` mode) |

## `outcome.json`

| Field | Meaning |
|---|---|
| `log_schema_version`, `run_id` | |
| `status` | `completed` (both agents reached their goals), `collision`, `deadlock`, `timeout` (the scenario's `max_time` ran out), or `aborted` (a call was refused by the budget guard or the model could not be used) |
| `status_detail` | Reason for an `aborted` run; otherwise null |
| `sim_time_s`, `steps` | When the run ended |
| `negotiation.enabled`, `.started` | Whether there was to be a dialogue, and whether it began |
| `negotiation.start_time_s`, `.end_time_s` | Simulated times |
| `negotiation.end_reason` | `consensus`, `message_limit`, `conflict_over` (one agent was already through, so nothing was left to negotiate), `run_ended`, `aborted`; null without a dialogue |
| `negotiation.consensus_reached` | true or false; null without a dialogue |
| `negotiation.turns_used`, `.messages_per_agent` | |
| `negotiation.stances` | `[speaker, stance]` for every turn, in order |
| `negotiation.negotiated_leader` | Agent both agreed should go first; null without consensus |
| `negotiation.llm_calls`, `.parse_failures`, `.retries` | Calls made; turns on which both attempts failed; second attempts made |
| `negotiation.tokens`, `.cost_usd`, `.llm_latency_s` | Totals |
| `roles.negotiated_leader` | As above |
| `roles.executed_leader`, `.executed_follower` | Who actually went through first, and second |
| `roles.negotiated_roles_followed` | Whether those agree; null if there was no agreement or nobody got through |
| `roles.role_source_steps` | Number of live-conflict steps on which the roles came from each source |
| `fallback_used` | true if Strategy 1, or physical precedence, decided the roles on any live-conflict step of a run that was meant to negotiate them; null if negotiation was disabled |
| `fallback_reasons` | Any of `no_consensus`, `conflict_before_consensus` (`concurrent` mode: the conflict began before the agents agreed), `negotiated_roles_not_feasible`, `dialogue_not_started` |
| `collisions` | `agent_agent` and `agent_wall` counts, `time_s`, `agents` involved. A run stops at its first collision. Two discs collide when their centres are closer than the sum of their radii. |
| `deadlock` | true if every unfinished agent stayed below the scenario's `speed_eps` for its `window_s` |
| `makespan_s` | Time at which the last agent reached its goal; null unless both did |
| `time_to_goal_s` | Per agent; null if it did not arrive |
| `region_entry_time_s` | Per agent: when its centre crossed the entry of the physical conflict region |
| `first_through`, `follower` | The agent that entered the region first, and the other |
| `follower_min_speed_mps` | The follower's lowest commanded speed before it entered the region. GameChat's "Min v". |
| `min_speed_before_region_mps` | The same quantity for each agent |
| `path_deviation_m` | Mean distance of the recorded positions from the desired path: `mean` over both agents' samples, and per agent |
| `ground_truth` | **null for every persona condition.** For C0 and C1: `type`, `priority_order`, `higher_priority_agent`, `higher_priority_first` (did it enter the region first), `higher_priority_time_to_goal_s` |

**Persona conditions carry no judgement.** There is no field anywhere in a C2, C3 or C4 run
that calls an outcome correct, incorrect, expected or fair. The config loader refuses to
score a run with a persona in it (`test_experiment_config.py`).

## `transcript.md`

A rendering, for people, of `config.json`, `conversation.jsonl` and `outcome.json`: the
participants, the system prompts, each turn (what the speaker was shown, what it said, its
stance, any failed attempt), and the outcome. It contains nothing that is not in those
three files, and `validate_run_dir` checks that every message in the conversation appears
in it.

## `summary.csv`

One row per run of the experiment, in design order, rewritten whenever the experiment is
run. Columns: identification (`experiment_name`, `run_id`, `condition`, `scenario`,
`scenario_variant`, `info_variant`, `seed`, `repeat`); each agent's `persona`, `age`,
`gender`, `task_type`, `task` and `side`; the controlled factors (`swap_sides`,
`first_speaker`, `timing_mode`, `prompt_template`, `model`, `temperature`); the outcome
(`status`, `consensus_reached`, `turns_used`, `end_reason`, `negotiated_leader`,
`first_through`, `negotiated_roles_followed`, `fallback_used`, `collisions`, `deadlock`,
`makespan_s`, `time_to_goal_0_s`, `time_to_goal_1_s`, `follower`,
`follower_min_speed_mps`, `path_deviation_m`); the ground-truth columns
(`higher_priority_agent`, `higher_priority_first`, `higher_priority_time_to_goal_s`),
empty for persona conditions; usage (`llm_calls`, `parse_failures`, `prompt_tokens`,
`completion_tokens`, `cost_usd`, `llm_latency_s`); and `git_commit`.

Empty cells mean null. Booleans are `true` and `false`.

## `spend_ledger.jsonl`

One line per paid call: `utc`, `experiment`, `run_id`, `turn_index`, `speaker`, `attempt`,
`model`, the token counts, `price_tier` (`peak` or `off_peak`), `cost_usd`,
`cost_is_upper_bound` (true when a send failed and was counted at its worst case),
`prices_date_checked`, `error`, and `cumulative_usd`. See `llm-backend.md`, section 5.

## Change log

- **1** (2026-10-13, issue #24): first version.
