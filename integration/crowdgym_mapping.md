# Wiring the dataset into CrowdGym

This is the bridge between `dataset/generated/behaviour_records.jsonl` and the
senior's CrowdGym environment. The dataset itself stays language-neutral
(JSON/CSV); this adapter is the only Python that touches CrowdGym's API, so the
in-progress **C++ port only needs its own thin re-implementation of this file**,
not a new dataset.

CrowdGym has exactly two places the data plugs into:

```
behaviour_records.jsonl
        |
        |  adapter.build_agent_types()            adapter.build_conflict_policy()
        v                                                 v
  CrowdGym Spawner / AgentType list          overridden RL_take_action (conflict handler)
        |                                                 |
        v                                                 v
  heterogeneous crowd (speed/size/tau)      humans-not-deadlocking behaviour at bottlenecks
```

## A. AgentType parameters  (CrowdGym report, Table I)

One `AgentType` per `(age_group, gender)` cell — 10 types. Its `distribution
weight` is that cell's Singapore population share from `personas.yaml`
(`population_weight`, **VERIFY vs SingStat**).

Numeric params come from `personas.yaml` base values, shifted by the LLM's coarse
attributes in the behaviour record. Starting rules (tune in step 6):

| CrowdGym param | Formula |
|---|---|
| `Speed` | `clip(record.movement_profile.walking_speed_mps.estimate, persona.free_flow_speed_mps*0.7, persona.free_flow_speed_mps*1.3)` ; sample per agent from `U(record...low, record...high)` |
| `Tau` | `{fast:0.3, normal:0.5, slow:0.7}[record.movement_profile.reaction_speed]` |
| `Mass` | `persona.anthropometry.mass_kg * {small:0.9, medium:1.0, large:1.15}[body_size]` |
| `Radius side` | `persona.anthropometry.shoulder_width_m/2 * body_size_factor` |
| `Radius front` | `persona.anthropometry.depth_m/2 * body_size_factor` |

Because the conflict behaviour differs by scenario but an `AgentType` does not,
build the `AgentType` list **per scenario** (the movement profile is nearly
scenario-invariant, but generating it per scenario lets you catch cases where the
LLM says e.g. elderly slow down much more in a crossflow).

> Calibration note: the senior's verification runs used `Speed = 0.8 m/s`
> (a JuPedSim default for model-to-model comparison). Our records use realistic
> free-flow speeds (~1.0-1.5 m/s). When reproducing the senior's Bottleneck /
> Corner / Crossflow numbers, either scale our speeds down to their baseline or
> re-run their baseline at realistic speeds — don't compare across the two.

## B. Conflict-resolution policy  (overridden `RL_take_action`)

### Trigger (when the handler fires for an agent)
All of:
- another agent within `1.5 m` and roughly ahead (`dot(heading, to_other) > 0.5`);
- closing (`d/dt distance < 0`);
- own speed `< 0.2 * desired` for `>= 0.4 s` (i.e. actually stuck), **or** the
  agent is inside a passage narrower than `2 * (Radius side)` shared with an
  opposing agent.

### Lookup
```python
key = (scenario_id, self.age_group, self.gender)
row = policy[key]      # from behaviour_records.jsonl -> conflict_behaviour
```
`row` gives `primary_action`, `fallback_action`, `yield_likelihood`,
`expected_resolution_time` (-> `steps = fps * seconds` via
`action_space.yaml.resolution_time_buckets`), and `priority_rules`.

### Pairwise resolution without pairwise data (DD1)
```python
p_self_yields = clip(
    row_self.yield_likelihood
    + priority_bias(row_self.priority_rules, other)     # +0.30 if a rule matches other (stroller, elderly, ...)
    - priority_bias(row_other.priority_rules, self),
    0.0, 1.0)

if rng.random() < p_self_yields:
    action = row_self.primary_action if row_self.primary_action in ("yield_step_aside","halt","slow","back_off") \
             else "yield_step_aside"
else:
    action = row_self.primary_action
```
`priority_bias` is a small hand-maintained table built during validation (step 6)
by parsing the free-text `priority_rules` into tags: `has_stroller`, `is_elderly`,
`is_child`, `carrying_load`, `committed_first`, `has_right_of_way`, ...

### Action -> CrowdGym `(N, 3)` row
Use `action_space.yaml -> high_level[].crowdgym_effect`. Summary:

| action | `[move_x, move_y]` | `delta_facing` |
|---|---|---|
| `proceed` | `desired_dir * desired_speed` | toward waypoint |
| `slow` | `desired_dir * 0.5*desired_speed` | toward waypoint |
| `halt` | `(0, 0)` | toward other agent |
| `yield_step_aside` | `lateral_dir * 0.5` for ~`0.6 s`, then `(0,0)` | keep |
| `speed_up` | `desired_dir * 1.25*desired_speed` (clip) | toward waypoint |
| `back_off` | `-desired_dir * 0.4*desired_speed` for ~`0.5 s` | toward other |
| `reroute` | `(0,0)` this step + request new journey/path | keep |

Keep the physical movement model (CFS — the senior found it less jittery at
exits) running underneath; the handler only *overrides the desired velocity /
target offset* for agents currently in a triggered conflict, then hands control
back once `steps` have elapsed or the trigger clears.

## C. Journey / route choice (optional, later)

For `num_exits > 1` scenarios, when `primary_action == "reroute"` or
`decision_factors` mention crowding/signage, bias the `AgentJourneyDirector`
weights: e.g. elderly `+` weight on the nearest/widest exit; "follow the crowd"
`+` weight on the currently most-used exit; "known route" `-` sensitivity to
congestion. This is a soft override of the senior's weighted-distance method.

## Minimal adapter interface (to implement in step 7)

```python
# integration/adapter.py  (sketch — not yet implemented)
def load_records(path) -> dict[tuple, dict]: ...          # key -> behaviour_record
def build_agent_types(records, scenario_id, personas) -> list[AgentTypeCfg]: ...
def build_conflict_policy(records, scenario_id) -> dict[tuple, ConflictRow]: ...
def priority_bias(rules: list[str], other_agent) -> float: ...
def action_to_command(action: str, agent, other, ctx) -> tuple[float,float,float]: ...
```

Nothing here calls CrowdGym yet; it is written against the interfaces described
in the senior's report (Spawner / AgentType, `RL_take_action`,
`AgentJourneyDirector`). Confirm exact class/method names against the CrowdGym
source before implementing.
