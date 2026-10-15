# Log schema, version 4

The logs are this platform's research output: rule extraction will be done from them. This
file says what every file and field means. The machine-checkable part of the schema, the
list of required fields, is in `negsim/runlog/schema.py`; `validate_run_dir` checks a run
folder against it, and the runner runs that check on every folder it writes.

**Versioning.** `log_schema_version` is written into every `config.json` and
`outcome.json`. Raise `LOG_SCHEMA_VERSION` whenever a field is added, removed, renamed or
changes meaning, and add a line to the change log at the end of this file.

**Two kinds of run.** Since version 2 every `config.json` says which kind of run it
describes, in `run_kind`:

| `run_kind` | What it is | Its files |
|---|---|---|
| `negotiation` | A run of issue #24: two agents, an optional dialogue, the arbiter. | `config.json`, `conversation.jsonl`, `trajectory.csv`, `outcome.json`, `transcript.md` |
| `avoidance` | A run of the avoidance layer of issue #26: any number of agents under ORCA and directives, which since version 3 may come from rules (issue #28). | `config.json`, `trajectory.csv`, `interactions.jsonl`, `pair_interactions.jsonl` (version 3), `events.jsonl`, `outcome.json` |

The sections from "Layout" to "`summary.csv`" describe a negotiation run; they are those of
version 1, with the one new field. The section "Avoidance runs" describes the other kind.
The two have files of the same name with different contents; `run_kind` says which is
which. Versions 3 and 4 changed only the avoidance run.

**Old folders stay valid.** A folder written under version 1 has no `run_kind` and is a
negotiation run. `validate_run_dir` checks a folder against the version its own
`config.json` declares (and its perception records against the perception version it
declares), and a test runs it over every committed run folder. The 66 run folders of issue
#24 are version 1 and the 46 of issue #26 version 2; none was rewritten.

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
| `log_schema_version` | 4 (1 in a folder written before issue #26; 2 or 3 in one written by issues #26 and #28) |
| `run_kind` | `negotiation`. Absent from a version 1 folder. |
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
`scenario_variant`, `info_variant`, `seed`, `repeat`); each agent's persona id, age,
gender, task type, task text and starting side (`agent0_persona`, `agent0_age`,
`agent0_gender`, `agent0_task_type`, `agent0_task`, `agent0_side`, and `agent1_persona`,
`agent1_age`, `agent1_gender`, `agent1_task_type`, `agent1_task`, `agent1_side`; the
persona, age and gender cells are empty for a task-only agent); the controlled factors (`swap_sides`,
`first_speaker`, `timing_mode`, `prompt_template`, `model`, `temperature`); the outcome
(`status`, `consensus_reached`, `turns_used`, `end_reason`, `negotiated_leader`,
`first_through`, `negotiated_roles_followed`, `fallback_used`, `collisions`, `deadlock`,
`makespan_s`, `time_to_goal_0_s`, `time_to_goal_1_s`, `follower`,
`follower_min_speed_mps`, `path_deviation_m`); the ground-truth columns
(`higher_priority_agent`, `higher_priority_first`, `higher_priority_time_to_goal_s`),
empty for persona conditions; usage (`llm_calls`, `parse_failures`, `prompt_tokens`,
`completion_tokens`, `cost_usd`, `llm_latency_s`); and `git_commit`.

Empty cells mean null. Booleans are `true` and `false`.

## Avoidance runs

A run of the avoidance layer (`architecture.md`, section 6). It calls no model, so it has
no conversation and no transcript, and nothing is added to the spend ledger.

```
llm_negotiation/
  runs/<experiment_name>/
    summary.csv                      one row per run
    <run_id>/
      config.json                    everything that defines the run
      trajectory.csv                 one row per agent per time step
      interactions.jsonl             one line per interaction: the perception record and the directive
      pair_interactions.jsonl        one line per pair interaction: its outcome, and every rule evaluation and match (version 3)
      events.jsonl                   one line per event: violations, handoffs, yields, near misses, collisions, rule events
      outcome.json                   what happened: every metric, per agent and in total
```

The conventions are those above. Agents are numbered from 0; a JSON object keyed by agent
uses the number as a string.

### `config.json` of an avoidance run

| Field | Meaning |
|---|---|
| `log_schema_version`, `run_kind` | 4 (2 in a folder of issue #26, 3 in one of issue #28), `avoidance` |
| `experiment_name`, `run_id`, `run_index` | Which experiment; the id of this run (also its folder name); its position in the design, from 1 |
| `seed`, `repeat` | The seed of the run, which seeds a random tie-break by the arbiter and, under a perturbed baseline, the perturbation; which repetition, from 1. How the seed was derived is `seeding` |
| `seeding` | Version 4. `paired`: the design's base seed plus `repeat`, the same for every level of every factor, so that a baseline run and a rule run of one scenario instance share their seed (the default since issue #30, `baseline.md`, section 6). `per_run`: the base seed plus `run_index`, as every run of versions 2 and 3 was seeded |
| `created_utc`, `git`, `software` | As for a negotiation run |
| `scenario_file` | The scenario YAML used |
| `variant` | The level of each factor of the design, e.g. `{"layout": "offset", "condition": "both_left"}` |
| `scenario` | The resolved scenario: `schema_version` (2), `type`, `dt_s`, `max_time_s`, `goal_tolerance_m`, `arrival`, `dynamics`, `seed` (of the randomness in the scenario itself), `on_collision`, `geometry`, `agent_types`, `orca` (`tie_break`), `navigation` (`lookahead_m`), `neighbour_search` (`cell_size_m`), `single_file` (`safety_margin_m`, `segments`), `deadlock`, `metrics` (the thresholds), `n_agents`, `obstacles`, and `agents` |
| `scenario.agents[]` | Per agent: `agent_id`, `agent_type`, `group`, `side`, `radius_m`, `preferred_speed_mps`, `max_speed_mps`, `initial_speed_mps`, `sensing_radius_m`, `max_neighbours`, `time_horizon_s`, `time_horizon_obst_s`, `start`, `goal`, desired `path`, `path_length_m`, and `single_file_stretches` (where its path enters and leaves each single-file segment) |
| `population[]` | Per agent: `agent_id`, `group`, `persona_id` and `attributes` (`age`, `gender`, `backstory`), or nulls for an agent with no persona. The task of the persona is not written: it plays no part in an avoidance run |
| `visibility` | For each attribute, whether an agent could see it of a neighbour |
| `directives` | The provider (`provider`: `null`, `static`, or `rules`) and `share_policy` (`proportional` or `equal_split`). For `static`, what it was configured with (`default`, `agents`, `pairs`). For `rules` (version 3), **the active rule set**: `database` (the folder), `ruleset` (the name of the rule set the run started from, or null), `rules` (every rule switched on: `rule_id`, `version`, `schema_version` (version 4), `status`, `encounter`, `priority`, `expiry`, and the `sha256` of its frozen file), `hysteresis_steps`, and `unchecked_pairs` (pairs of rules the ambiguity check could not try; `rule-matching.md`) |
| `arbitration` | `enabled`, `policy`, `tie_break`: how single-file segments were handled |
| `logging` | `trajectory_stride` (every how-many-th step is in `trajectory.csv`) and `interactions` (whether the per-interaction records, `interactions.jsonl` and, in version 3, `pair_interactions.jsonl`, were filled; the outcome counts them either way) |
| `perception_schema_version` | Version of the perception record (`perception.md`): 2 since issue #28, 1 in a folder of issue #26 |
| `baseline` | Version 3. The frozen baseline the run followed (`baseline.md`), or null: `name`, `version`, `role` (`primary` or `secondary`), `file`, `sha256`, `perturbation`, `orca`, `agent_types` (the settings it laid on every agent type), `sign_off`. A level of the experiment may still have changed a setting after it; `scenario` holds what was used |
| `perturbation` | Version 3. What was added to every preferred velocity on every step (`kind`: `rvo2_uniform`; `magnitude_mps`, 0 for none) |

### `trajectory.csv` of an avoidance run

One row per agent per time step, for the agents that had not yet arrived, then one final
row per agent for the state at the end. As for a negotiation run, a row gives the state at
the *start* of a step and what was done *during* it, and the final rows have only the
state. With `trajectory_stride` above 1 only every such step is written; the final rows
always are.

| Column | Meaning |
|---|---|
| `step`, `time_s` | Step number from 0, and its start time |
| `agent_id` | |
| `x_m`, `y_m`, `theta_rad` | Position of the centre, and the direction of motion |
| `path_s_m` | Progress along the desired path |
| `vx_mps`, `vy_mps`, `speed_mps` | The velocity the agent moved at during the step |
| `pref_vx_mps`, `pref_vy_mps` | The velocity it wanted: along its path at its preferred speed, scaled by its directives and capped by the arbiter |
| `control_mode` | `orca`, or `arbiter` if the agent was in a pair the arbiter held on this step (`architecture.md`, section 6.4) |
| `speed_bound_mps` | The bound the arbiter put on the speed the agent wants; empty unless `control_mode` is `arbiter` |
| `role`, `role_source` | `leader` or `follower`, and where the order came from: `negotiated` (here: the `passage_order` of the directives), `strategy1` (the rule of the arbiter itself) or `physical_precedence`. Empty unless the arbiter held the agent and the conflict was live |
| `in_conflict` | Whether the arbiter found a live single-file conflict for the agent on this step |
| `zone_d_in_m`, `zone_d_out_m` | Distance along the path to where the agent enters and leaves the conflict zone at the segment; negative once passed |
| `n_neighbours` | How many neighbours the agent perceived |
| `speed_scale` | The scale its directives put on its preferred speed on this step: the smallest `speed_scale` among them, 1 if it perceived nobody |
| `exposed` | Whether its preferred velocity was outside a half-plane induced by another agent, so that ORCA had to change it (`metrics.md`, section 3) |
| `fallback` | Whether no velocity satisfied all its half-planes, so that the fallback of ORCA chose (`orca.md`, section 7) |
| `interactions` | The `interaction_id` of each of its interactions that was active on this step, separated by `;`. **This is how the active directive is recorded**: each id is a line of `interactions.jsonl`, which holds the directive |

### `interactions.jsonl`

One JSON object per line, one line per interaction, in the order they began. An
interaction is the dealings of one agent with one neighbour, from the step the neighbour
became one of its perceived neighbours to the step it went out of range
(`metrics.md`, section 2). Empty if the experiment sets `logging.interactions: false`.

| Field | Meaning |
|---|---|
| `interaction_id` | From 0 |
| `observer_id`, `neighbour_id` | Whose interaction, and with whom |
| `start_step`, `start_time_s` | When the neighbour came into range |
| `end_step`, `end_time_s`, `end_reason` | When and why it ended: `out_of_range`, `observer_arrived`, `neighbour_arrived` or `run_ended` |
| `perception` | **The perception record at the moment the neighbour came into range**, whole (`perception.md`) |
| `directive` | The directive the provider returned for it when it began: `side_preference`, `responsibility_share`, `speed_scale`, `clearance_margin`, `passage_order`. With `null` and `static` providers it holds for the whole interaction, except that its `speed_scale` stops applying once the encounter has passed (version 3) |
| `directive_changes` | Version 3. Each later change of the directive by a provider that follows pairs (the rule database), in order: `from_step`, `from_time_s`, and the five fields. Empty otherwise. A rule match that begins, is replaced or expires shows here; `pair_interactions.jsonl` says which rule and why |
| `speed_scale_expired_step`, `speed_scale_expired_time_s` | Version 3. When the directive's `speed_scale` stopped applying because the encounter had passed (`derivations.md`, section 15). Only with a provider that does not follow pairs, and only if the scale was not 1; null otherwise |
| `effective` | What was actually used, as a list of entries, a new one each time it changed: `from_step`, `mutual` (whether the neighbour perceived the observer too), `responsibility_share`, `side_preference`, `clearance_margin`. It differs from `directive` when the two directives of the pair were combined, when a violation was repaired, and while the arbiter held the pair |
| `perceived_time_s` | Time during which the neighbour was among the perceived neighbours of the observer |
| `conflict_exposure_time_s` | Time during which the preferred velocity of the observer was outside the half-plane induced by this neighbour |
| `arbiter_time_s` | Time during which the arbiter held the pair |
| `min_separation_m` | Smallest distance between the surfaces of the two bodies during the interaction |

### `pair_interactions.jsonl` (version 3)

One JSON object per line, one line per **pair interaction**, in the order they began. A
pair interaction is two agents, from the first step on which either perceives the other to
the first on which neither does, one of them has arrived, or the run has ended. It is the
unit rules are matched on (`rule-matching.md`) and the unit categorised as avoided,
resolved or failed (`metrics.md`, section 9). Every avoidance run has them, whatever its
provider. Empty if the experiment sets `logging.interactions: false`.

| Field | Meaning |
|---|---|
| `pair_id` | From 0 |
| `agents` | The two agents, the lower-numbered first |
| `start_step`, `start_time_s` | When the pair formed |
| `encounter_class_at_start` | The pair's encounter class on that step (`perception.md`), or null if hidden |
| `end_step`, `end_time_s`, `end_reason` | When and why it ended: `out_of_range`, `agent_arrived` or `run_ended` |
| `passed_step`, `passed_time_s` | The first step on which the encounter had passed: the two separating and clear of each other by more than the pair's clearance margin (`derivations.md`, section 15); null if it never did |
| `conflict_exposure_time_s` | For each of the two (keyed by agent), the time during which its preferred velocity was outside the half-plane induced by the other. Depends on the responsibility shares (`metrics.md`, section 3) |
| `pair_exposure_time_s` | Version 4. The time during which the two intended velocities put the pair on a collision course: inside the two bodies' velocity obstacle by more than `pair_exposure_eps_mps` (`metrics.md`, section 11). Does not depend on the shares |
| `first_pair_exposed_step` | Version 4. The first step on which the pair was exposed; null if it never was |
| `min_separation_m` | Smallest distance between the two bodies while the pair was open and one perceived the other |
| `outcome` | `avoided`, `resolved` or `failed` (`metrics.md`, section 9) |
| `outcome_detail` | What decided it: `exposed` (either had exposure), `pair_exposed` (version 4: the pair had pair exposure, which the category does not use but another reading of it could), `yield_events` (yield events of either that overlapped the pair interaction), `collisions` (collision episodes between the two that did), `deadlock` (the run ended in deadlock with the pair open), `open_at_timeout` (the run reached its time limit with the pair open) |
| `severity_tier` | Version 4. `T0` (interaction only), `T1` (on a collision course), `T2` (a yield event), `T3` (a near miss) or `T4` (deadlock or collision): the highest that applies (`metrics.md`, section 11) |
| `tier_detail` | Version 4. What decided the tier: `pair_exposure_time_s`, `yield_events` and `near_misses` (of either, or between the two, that overlapped the pair interaction), `collisions`, `deadlock` |
| `rules` | Null unless the provider is the rule database; otherwise what the matching policy did, below |

`rules`:

| Field | Meaning |
|---|---|
| `state_at_end` | `unmatched`, `held` or `spent` (a match expired and nothing has matched since) |
| `independent_agrees` | Whether, on the step the pair formed, each agent evaluating the rules on its own perception record got the same directive as the shared snapshot gave it (`rule-matching.md`, "Evaluation on a shared snapshot"). Should always be true |
| `evaluations` | **Every evaluation, with its outcome.** Consecutive evaluations with the same outcome, rule and encounter class share one entry: `from_step`, `from_time_s`, `to_step`, `count` (how many evaluations, one per step), `encounter_class`, `outcome` (`rule_matched`, `no_rule_matched`, `ambiguous_match`, or `kept`: a held rule stayed because nothing of strictly higher priority matched), `rule` (`rule_id@version` applied, or null), `ambiguous_with` (the other rules at the same priority that matched with different directives), `candidates` (how many rules were tried), and `snapshot`: the values the conditions were evaluated on, at the first evaluation of the entry (null if no rule was tried) |
| `matches` | Every match, in order: `rule_id`, `version`, `priority`, `encounter`, `expiry`, `outcome` (`rule_matched` or `ambiguous_match`), `ambiguous_with`, `from_step`, `from_time_s`, **the role each agent received** (`roles`, keyed by agent) and **the resulting directive** (`directives`, keyed by agent: all five fields, the rule's and the baseline values of those it leaves out), the `snapshot` it matched on, and **when and why it ended**: `to_step`, `to_time_s`, `end_reason` (`passed`, `replaced` by a rule of higher priority, `out_of_range`, `agent_arrived`, `run_ended`) and `replaced_by` |
| `cross_pair_conflicts` | The cross-pair conflicts this pair was part of, as in `events.jsonl` |

A `snapshot` has `step`, `time_s`, `agents`, `pair` (every pair-level field a rule can
read) and `agent` (every agent-level field, keyed by agent); a hidden value is null
(`rule-format.md`).

### `events.jsonl`

One JSON object per line, in time order. Every event has `event_index` (from 0), `type`
and `time_s`.

| `type` | Further fields | Meaning |
|---|---|---|
| `reciprocity_violation` | `step`, `field`, `agents`, `given`, `resolved`, `policy` | The two directives of a pair contradicted each other in `field` (`responsibility_share`, `side_preference` or `passage_order`). `given` is what the two asked for, `resolved` what was used, `policy` the rule that decided (`derivations.md`, sections 9 to 11). Logged once, when the pair first perceive each other |
| `handoff` | `step`, `pair`, `to`, `leader`, `role_source`, `reason` | Control of a pair passed `to` the `arbiter` or back to `orca` |
| `yield` | `agent_id`, `start_time_s`, `end_time_s`, `duration_s`, `min_speed_mps` | A yield event (`metrics.md`, section 4). `time_s` is its start |
| `near_miss` | `pair`, `start_time_s`, `end_time_s`, `min_separation_m` | A near miss (`metrics.md`, section 5) |
| `collision` | `pair`, `start_time_s`, `end_time_s`, `max_overlap_m` | Two bodies overlapped |
| `wall_collision` | `agent_id`, `start_time_s`, `end_time_s`, `max_overlap_m` | A body overlapped a wall |
| `ambiguous_match` | `step`, `pair`, `applied`, `ambiguous_with` | Version 3. Two rules at the top priority matched the pair with different directives; `applied` is the one with the lower `rule_id` (`rule-matching.md`). One event per entry of the pair's evaluation log |
| `cross_pair_conflict` | `step`, `agent_id`, `field`, `values`, `resolution` | Version 3. The rule matches of one agent's pairs contradict each other in `field` (`side_preference`, `speed_scale` or `passage_order`); `values` lists each pair, its rule and its value; `resolution` says how it is settled (`rule-matching.md`). Logged when the conflict appears |

### `outcome.json` of an avoidance run

| Field | Meaning |
|---|---|
| `log_schema_version`, `run_kind`, `run_id` | |
| `status` | `completed` (every agent arrived), `collision` (two bodies overlapped and the scenario stops on that), `deadlock`, or `timeout` (the `max_time` of the scenario ran out). Never `aborted`: no model is called |
| `sim_time_s`, `steps` | When the run ended |
| `n_agents`, `arrived` | How many agents, and how many reached the end of their path |
| `collisions` | `agent_agent` and `agent_wall` (numbers of episodes), `time_s` (of the first), `agents` involved, `max_overlap_m` (the deepest overlap; null if none). With `on_collision: stop` the run ends at the first; with `continue` they are counted |
| `deadlock` | true if every agent that had not arrived stayed below the threshold speed for the window |
| `makespan_s` | When the last agent arrived; null unless all did |
| `time_to_goal_s` | Per agent; null if it did not arrive |
| `agents` | Per agent, every metric: `time_to_goal_s`, `distance_m`, `path_deviation_mean_m`, `path_deviation_max_m`, `interactions`, `interaction_time_s`, `conflict_exposure_time_s`, `orca_altered_time_s`, `yield_events`, `yield_time_s`, `near_misses`, `min_separation_m`, `min_wall_gap_m`, `fallback_steps`, `one_sided_steps`, `arbiter_time_s` (`metrics.md`) |
| `totals` | Over all agents: `interactions`, `conflict_exposure_time_s`, `pair_exposure_time_s` (version 4: summed over the pair interactions), `yield_events`, `yield_time_s`, `near_misses`, `min_separation_m`, `mean_time_to_goal_s`, `mean_path_deviation_m`, `max_path_deviation_m`, `steps_with_fallback`, `fallback_agent_steps`, `one_sided_agent_steps` |
| `single_file` | Per single-file segment: `segment`, `entry_time_s` per agent, and `first_through` |
| `reciprocity_violations` | Every violation, as in `events.jsonl` without `event_index` and `type` |
| `handoffs` | Every handoff, likewise |
| `thresholds` | The metric thresholds the run used (since version 4 also `pair_exposure_eps_mps` and `collision_course_min_s`), and the deadlock settings |
| `interaction_outcomes` | Version 3. `pairs` (how many pair interactions), `avoided`, `resolved`, `failed`, and `pairs_with`: how many pairs were `exposed`, `pair_exposed` (version 4), `yielded`, `collided`, `deadlocked` and `open_at_timeout` (a pair can count under several). Version 4: `tiers`, the number of pairs in each of `T0` to `T4` |
| `rules` | Version 3. Null unless the provider is the rule database; otherwise `evaluations` (how many evaluations ended in each outcome), `matches_begun` (by `rule_id@version`: **which rules fired, and how often**), `match_ends` (by reason), `cross_pair_conflicts` (how many were logged), `formation_checks` and `formation_mismatches` (the run-time check of the shared snapshot against each agent's own evaluation, `rule-matching.md`; the second should be 0) |
| `baseline` | Version 3. The name of the baseline the run followed, or null |
| `artefacts` | Version 3. Counts of the two ORCA artefacts of issue #26 (`metrics.md`, section 10): `thresholds`; per agent (`agents`) `backward_episodes`, `backward_time_s`, `hurried_episodes`, `hurried_time_s`; and `totals`, the same summed, with `agents_backward` and `agents_hurried` |

### `summary.csv` of an avoidance experiment

One row per run, in design order: identification (`experiment_name`, `run_id`, `scenario`,
`variant`, `seed`, `repeat`, `n_agents`); the settings (`provider`, `arbitration_enabled`);
the outcome (`status`, `arrived`, `collisions`, `max_overlap_m`, `deadlock`, `makespan_s`,
`mean_time_to_goal_s`); the conflict metrics (`conflict_exposure_time_s`, `yield_events`,
`yield_time_s`, `near_misses`, `min_separation_m`, `steps_with_fallback`,
`fallback_agent_steps`, `reciprocity_violations`, `handoffs`, `first_through`); the same
for agents 0 and 1, which is all there are in four of the five scenarios
(`time_to_goal_0_s`, `time_to_goal_1_s`, `path_deviation_max_0_m`,
`path_deviation_max_1_m`, `conflict_exposure_0_s`, `conflict_exposure_1_s`); from
version 3, the baseline and the rules (`baseline`, `ruleset`, `pairs`, `avoided`,
`resolved`, `failed`, `rules_fired` as `rule_id@version=count` separated by `;`,
`ambiguous_matches`, `cross_pair_conflicts`, `backward_episodes`, `hurried_episodes`), empty for a run written before; from
version 4, pair exposure and the tiers (`pair_exposure_time_s`, `pairs_t0`, `pairs_t1`, `pairs_t2`, `pairs_t3`,
`pairs_t4`), empty for a run written before; and
`git_commit`.

## `spend_ledger.jsonl`

One line per paid call: `utc`, `experiment`, `run_id`, `turn_index`, `speaker`, `attempt`,
`model`, the token counts, `price_tier` (`peak` or `off_peak`), `cost_usd`,
`cost_is_upper_bound` (true when a send failed and was counted at its worst case),
`prices_date_checked`, `error`, and `cumulative_usd`. See `llm-backend.md`, section 5.

## Change log

- **1** (2026-10-13, issue #24): first version.
- **2** (2026-10-13, issue #26): a second kind of run. `run_kind` added to every
  `config.json`. A `negotiation` run is otherwise as in version 1. An `avoidance` run has
  its own files: `config.json`, `trajectory.csv` (with the velocity as a vector, the
  preferred velocity, `control_mode`, and the ids of the active interactions),
  `interactions.jsonl`, `events.jsonl` and `outcome.json`; and the `summary.csv` of an
  avoidance experiment has its own columns. Folders written under version 1 stay valid.
- **3** (2026-10-14, issue #28): rules. An avoidance run gains `pair_interactions.jsonl`
  (each pair interaction's outcome category, and every rule evaluation and match with its
  roles, directives, snapshot and expiry); `baseline` and `perturbation` in `config.json`,
  and the active rule set under `directives`; `directive_changes` and the expiry of
  `speed_scale` in `interactions.jsonl`; the events `ambiguous_match` and
  `cross_pair_conflict`; `interaction_outcomes`, `rules` and `baseline` in
  `outcome.json`, with `artefacts` (counts of walking backwards and of being hurried along); and eleven summary columns. `logging.interactions` now also governs
  `pair_interactions.jsonl`. Perception records are version 2. A negotiation run is as in
  version 2. Folders written under versions 1 and 2 stay valid and are checked against
  their own version.
- **4** (2026-10-15, issue #30): pair exposure and severity tiers. An avoidance run gains, in
  `pair_interactions.jsonl`, `pair_exposure_time_s`, `first_pair_exposed_step`, `severity_tier`,
  `tier_detail` and `outcome_detail.pair_exposed`; in `outcome.json`, `interaction_outcomes.tiers`,
  `interaction_outcomes.pairs_with.pair_exposed` and `totals.pair_exposure_time_s`; in `config.json`,
  `seeding`, and the two new thresholds in `scenario.metrics` (and in `outcome.json`'s `thresholds`);
  and six summary columns. The categories `avoided`, `resolved`, `failed` mean what they meant in
  version 3. A negotiation run is as in version 3. Folders written under versions 1 to 3 stay valid
  and are checked against their own version.
