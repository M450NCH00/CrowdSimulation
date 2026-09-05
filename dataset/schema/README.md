# Dataset schema and CrowdGym mapping

Four schemas:

| File | What it validates | When it is written |
|---|---|---|
| `scenario.schema.json` | an entry in `../scenarios.yaml` | authored by hand |
| `persona.schema.json` | an age-group entry in `../personas.yaml` | authored by hand |
| `raw_response.schema.json` | one row per DeepSeek API call (incl. every repeat) | during generation (step 5) |
| `behaviour_record.schema.json` | one aggregated record per `(scenario x persona)` cell | during aggregation (step 5) |

Cardinality: `scenarios (14) x age_groups (5) x genders (2) = 140` behaviour
records, each aggregated from `repeats` raw responses.

## File formats

- `scenarios.yaml`, `personas.yaml`, `action_space.yaml` — YAML, hand-edited.
- `raw/` — JSON Lines (`.jsonl`), one `RawResponse` per line.
- `behaviour_records.jsonl` and `behaviour_records.csv` — the deliverable. JSONL
  is canonical; the CSV is a flattened convenience view.

Everything is plain text / JSON / CSV — **no Python pickles**. The in-progress
C++ CrowdGym port can read the same files; only the adapter in
`../../integration/` is language-specific (DD3).

## How a BehaviourRecord maps onto CrowdGym

CrowdGym has two consumption points. The adapter
(`integration/crowdgym_mapping.md`) does the conversion.

### 1. AgentType numeric parameters (Table I of the CrowdGym report)

Base values come from `personas.yaml` (literature-informed). The LLM's coarse
attributes shift them. `w` = shoulder_width_m, `d` = depth_m.

| CrowdGym param | Source | Rule (starting point, tune later) |
|---|---|---|
| `Speed` (m/s) | `movement_profile.walking_speed_mps.estimate` | use the LLM estimate, clamped to `personas.yaml` low/high for that age group; keep the model's own low/high as the sampling range |
| `Tau` (s) | `movement_profile.reaction_speed` | `fast -> 0.3`, `normal -> 0.5`, `slow -> 0.7` |
| `Mass` (kg) | `personas.yaml.anthropometry.mass_kg` x `body_size` factor | `small 0.9`, `medium 1.0`, `large 1.15` |
| `Radius side` (m) | `w/2` x `body_size` factor | factor as above |
| `Radius front` (m) | `d/2` x `body_size` factor | factor as above |
| AgentType `distribution weight` | `personas.yaml.population_weight[age][gender]` | one AgentType per `(age,gender)` cell; weights = SG population share (VERIFY vs SingStat) |

> Note: the senior's verification runs used `Speed = 0.8 m/s` (a JuPedSim default
> for model comparison), which is well below real free-flow (~1.3-1.4 m/s). Our
> records use realistic speeds; flag this difference when comparing against the
> senior's baseline numbers.

### 2. Conflict-resolution policy (overridden `RL_take_action`)

The senior added exit-selection by overriding `RL_take_action` and leaving the
rest of the step untouched. We do the same: a handler watches for a conflict
trigger (two agents mutually facing, closing range, near-zero speed inside a
`passage_width_m` opening) and looks up:

```
policy[(scenario_id, self.age, self.gender)] -> {
    primary_action, fallback_action, yield_likelihood,
    expected_resolution_time -> steps (fps * seconds),
    priority_rules
}
```

`action_space.yaml.crowdgym_effect` says how each `primary_action` becomes an
`(N, 3)` row `[move_x, move_y, delta_facing]`.

**Pairwise outcomes without pairwise generation (DD1).** When agent A meets agent
B we do not have an `A-vs-B` record. Instead:

```
p_A_yields = clip( yield_likelihood[A]
                   + priority_bias(A, B)      # from A.priority_rules, e.g. +0.3 if B has a stroller / is elderly
                   - priority_bias(B, A), 0, 1)
outcome:
  if random() < p_A_yields:  A -> yield_step_aside / halt ;  B -> proceed
  else:                      A -> primary_action           ;  B -> yield or its own primary_action
```

This keeps generation at `scenarios x personas` (140 records) instead of
`scenarios x persona-pairs` (14 x 100 = 1400). `priority_rules` strings are
parsed into a small hand-maintained bias table during validation (step 6).

### 3. Journey / route choice (optional, later)

For scenarios with `num_exits > 1` or an alternative route, `primary_action =
reroute` plus `decision_factors` feed the `AgentJourneyDirector` weighting (e.g.
elderly bias toward the nearer/wider exit; "follow the crowd" vs "known route").

## Aggregation (raw -> canonical)

For each `(scenario, persona)` cell with `repeats` raw responses:

- `primary_action` = mode across repeats; `primary_action_agreement` = its frequency.
- `yield_likelihood` = mean; `yield_likelihood_std` = standard deviation.
- categorical fields (`patience`, `reaction_speed`, ...) = mode.
- `walking_speed_mps.estimate` = mean; `.low/.high` = min/max across repeats.
- `decision_factors` / `priority_rules` = union, then keep those mentioned in
  `>= 50%` of repeats.
- Low `primary_action_agreement` (< 0.6) is **kept and flagged** — disagreement is
  a finding about how reliable the LLM "world model" is, per the research question.
