# The perception record, version 1

A perception record is what one agent can tell about a neighbour, and about where it is
itself, at the moment the neighbour comes into range. It is built once per interaction and
handed to the agent's directive provider, which answers with a directive. **It is the
input that rules will read in the next sub-issue**, so its fields are a contract.

The code is `negsim/avoidance/perception.py`. The record is logged, whole, in
`interactions.jsonl` (`log-schema.md`).

**Versioning.** `schema_version` is in every record and `perception_schema_version` in
every `config.json`. Raise `PERCEPTION_SCHEMA_VERSION` whenever a field is added, removed,
renamed or changes meaning, and add a line to the change log at the end of this file. A
test fails if a field of the record is not described here
(`tests/test_perception.py::test_the_perception_document_names_every_field_and_the_version`).

## When a record is built

An agent's *perceived neighbours* are the nearest `max_neighbours` agents no further away
than its sensing radius `R` (both are parameters of its agent type). An **interaction** of
agent A with neighbour B begins on the first step on which B is one of A's perceived
neighbours. On that step, before anyone moves, A's record of B is built from the state of
the world at that instant.

The interaction ends when B is further than `R` from A, or either of them arrives. If B
comes back into range later, that is a new interaction with a new record.

A record is A's. B's record of A is a separate one, built when A becomes one of B's
perceived neighbours, which is the same step if the two have the same `R` and neither is
crowded out of the other's `max_neighbours`.

## What is observable

| Of | An agent perceives | And never |
|---|---|---|
| the neighbour | where it is, how it is moving, which way it faces, how big it is, and the persona attributes the run's visibility settings switch on | its **task**; its preferred or maximum speed; its goal; its path; any directive it holds |
| itself | its motion, size and preferred speed; its own age and gender | its own task (see the note below) |
| its surroundings | the nearest wall, the free width of the passage it is in, and how far ahead a single-file segment is | anything about walls beyond the environment range |

**The task is never in a record.** Not the neighbour's, whatever the visibility settings
say, including the setting for the task itself; and not the agent's own. Issue #26 asks
for the first. The second is this project's choice: a record describes what is
*perceived*, and leaving the task out altogether means that no rule can depend on it by
accident. A later sub-issue that wants rules to depend on the agent's own errand will have
to add that deliberately, with a new version of this record.

**Visibility** is governed by the settings of issue #24, read the same way
(`visibility: default` or a mapping of switches in an experiment config):

| Switch | Default | What it hides when off |
|---|---|---|
| `age` | on | `neighbour_attributes.age` |
| `gender` | on | `neighbour_attributes.gender` |
| `backstory` | off | `neighbour_attributes.backstory` |
| `task` | off | nothing: the task is never shown, on or off |
| `speed` | on | `neighbour_speed_mps`, `relative_velocity_mps`, `closing_speed_mps`, `time_to_collision_s` |
| `size` | on | `neighbour_radius_m`, `time_to_collision_s` |

**A hidden value is `null`. It is never left out and never replaced by a default.** A
hidden persona attribute is absent from `neighbour_attributes`, which is a mapping of only
what is seen. An agent with no persona has an empty mapping.

`time_to_collision_s` needs both the neighbour's velocity and its size, so hiding either
hides it. Position and heading are always perceived: an agent that is in range is seen to
be somewhere, facing some way.

## The fields

Positions are in metres in the world frame (x to the east, y to the north). Angles are in
radians, anticlockwise positive. Values are rounded to six decimal places in the log.

| Field | Unit | Meaning |
|---|---|---|
| `schema_version` | | 1 |
| `step`, `time_s` | –, s | The step and the simulated time at which the record was built: when the neighbour came into range |
| `observer_id`, `neighbour_id` | | The agent whose record this is, and the neighbour it is about |
| `relative_position_m` | m, m | The neighbour's position minus the observer's, `[dx, dy]` |
| `distance_m` | m | Between the two centres |
| `bearing_rad` | rad | Direction of the neighbour as seen from the observer: the angle from the observer's heading to the line toward the neighbour. 0 is dead ahead, positive is to the observer's left, ±π is directly behind |
| `relative_velocity_mps` | m/s, m/s | The neighbour's velocity minus the observer's, `[dvx, dvy]`. `null` if `speed` is hidden |
| `closing_speed_mps` | m/s | How fast the distance is shrinking; negative if it is growing. `null` if `speed` is hidden |
| `time_to_collision_s` | s | Time until the two bodies touch if both keep their present velocities. 0 if they touch already. `null` if they would not touch, or if `speed` or `size` is hidden |
| `neighbour_radius_m` | m | The neighbour's body radius: half its width. `null` if `size` is hidden |
| `neighbour_speed_mps` | m/s | The neighbour's speed. `null` if `speed` is hidden |
| `neighbour_heading_rad` | rad | The direction the neighbour is moving in, in the world frame; the direction it faces if it is standing still |
| `neighbour_heading_relative_rad` | rad | The same, relative to the observer's heading: 0 means the same way, ±π means head-on, +π/2 means crossing from the observer's right to its left |
| `neighbour_attributes` | | The neighbour's persona attributes that are visible, e.g. `{"age": 70, "gender": "male"}`. Never `task` |
| `observer` | | The observer's knowledge of itself, below |
| `environment` | | The observer's surroundings, below |

`observer`:

| Field | Unit | Meaning |
|---|---|---|
| `radius_m` | m | Its own body radius |
| `speed_mps` | m/s | Its own speed |
| `heading_rad` | rad | The direction it is moving in |
| `preferred_speed_mps` | m/s | The speed it walks at when nothing is in its way, before any directive scales it |
| `attributes` | | Its own age and gender, if it has a persona. Never its task |

`environment`:

| Field | Unit | Meaning |
|---|---|---|
| `nearest_wall_distance_m` | m | From the observer's centre to the nearest wall. `null` if the scene has no walls |
| `free_width_left_m`, `free_width_right_m` | m | From the observer's centre to the nearest wall on its left and on its right, measured at right angles to the direction its desired path takes at that point. `null` if there is no wall on that side within the environment range |
| `free_width_m` | m | The sum of the two: the free width of the passage the observer is in. `null` if either side is open |
| `single_file_ahead_m` | m | Distance along the observer's path to the next single-file segment; 0 if it is inside one; `null` if none lies ahead |

The **environment range** is the largest sensing radius of any agent in the scene.

`single_file_ahead_m` is not in the list issue #26 gives. It was added because the
directive has a field, `passage_order`, that only means something at a single-file
segment, and without this a rule would have no way of telling that one is coming.

Left and right for the free widths are taken from the direction of the *path*, not of the
velocity, so that they do not flip when an agent sidesteps.

## An example

Agent 0 (a woman of 25) in the wide corridor, at the moment agent 1 (a man of 70) comes
within its 12.5 m sensing radius, walking toward it. From
`runs/si1_head_on_side_preference/001_symmetric_plain/interactions.jsonl`:

```json
{
  "schema_version": 1,
  "step": 14,
  "time_s": 1.4,
  "observer_id": 0,
  "neighbour_id": 1,
  "relative_position_m": [12.36, 0.0],
  "distance_m": 12.36,
  "bearing_rad": 0.0,
  "relative_velocity_mps": [-2.6, 0.0],
  "closing_speed_mps": 2.6,
  "time_to_collision_s": 4.561538,
  "neighbour_radius_m": 0.25,
  "neighbour_speed_mps": 1.3,
  "neighbour_heading_rad": 3.141593,
  "neighbour_heading_relative_rad": 3.141593,
  "neighbour_attributes": {"age": 70, "gender": "male"},
  "observer": {
    "radius_m": 0.25,
    "speed_mps": 1.3,
    "heading_rad": 0.0,
    "preferred_speed_mps": 1.3,
    "attributes": {"age": 25, "gender": "female"}
  },
  "environment": {
    "nearest_wall_distance_m": 0.875,
    "free_width_m": 1.75,
    "free_width_left_m": 0.875,
    "free_width_right_m": 0.875,
    "single_file_ahead_m": null
  }
}
```

The two have the same body and the same speeds. A persona changes what is perceived and
nothing physical (`parameters.md`, section 5).

## What a provider does with it

A directive provider is a class with one method, `directive(record) -> AvoidanceDirective`
(`negsim/avoidance/directives.py`). It is called once per interaction, with the record
above, and what it returns holds until the interaction ends. Two are provided:

- `NullProvider`: plain ORCA for everyone.
- `StaticProvider`: directives written in the experiment config, by default, per agent, or
  per ordered pair of observer and neighbour.

A rule-database provider and a negotiation provider are to come behind the same interface.

## Change log

- **1** (2026-10-13, issue #26): first version.
