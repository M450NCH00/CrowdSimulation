# The perception record, version 3

A perception record is what one agent can tell about a neighbour, and about where it is
itself, at the moment the neighbour comes into range. It is built once per interaction and
handed to the agent's directive provider, which answers with a directive. **It is the
input that rules read** (`rule-format.md`), so its fields are a contract.

Version 2 (issue #28) adds the **pair-level fields**: what the two agents of a pair can
*both* tell about the two of them together. They are the fields a rule's condition may
use, and they are defined in their own section below.

Version 3 (issue #32) adds **where each of the two is in a single-file passage** they meet in
(section "Passage fields") and a **fictional group**, `ethnic_group`, which an agent may see
but **no rule may read** (section "The group").

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
| the neighbour | where it is, how it is moving, which way it faces, how big it is, and the persona attributes the run's visibility settings switch on (its group among them, version 3) | its **task**; its preferred or maximum speed; its goal; its path; any directive it holds |
| itself | its motion, size and preferred speed; its own age, gender and group | its own task (see the note below) |
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
| `ethnic_group` | off | `neighbour_attributes.ethnic_group` (version 3; independent of `age` and `gender`) |
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
| `schema_version` | | 3 |
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
| `neighbour_time_to_segment_s` | s | How soon the neighbour would reach the single-file segment named in `pair.single_file_segment`: its distance to the segment divided by its present speed; 0 if it is inside; `null` if it is standing still, or if `pair.single_file_segment` is `null` |
| `neighbour_in_segment` | true/false | Version 3. Whether the neighbour's centre is inside that segment; `null` if `pair.single_file_segment` is `null` (section "Passage fields") |
| `neighbour_segment_distance_travelled` | m | Version 3. How far the neighbour has walked into the segment; `null` unless it is inside |
| `neighbour_segment_distance_ahead`, `neighbour_segment_distance_behind` | m | Version 3. From the neighbour to the segment's end in front of it and behind it; `null` unless it is inside |
| `neighbour_attributes` | | The neighbour's persona attributes that are visible, e.g. `{"age": 70, "gender": "male"}`. Never `task` |
| `observer` | | The observer's knowledge of itself, below |
| `environment` | | The observer's surroundings, below |
| `pair` | | What both agents can tell about the two of them together: the pair-level fields, below |

`observer`:

| Field | Unit | Meaning |
|---|---|---|
| `radius_m` | m | Its own body radius |
| `speed_mps` | m/s | Its own speed |
| `heading_rad` | rad | The direction it is moving in |
| `preferred_speed_mps` | m/s | The speed it walks at when nothing is in its way, before any directive scales it |
| `attributes` | | Its own age and gender, if it has a persona, and (version 3) its group, if it has one. Never its task |
| `time_to_segment_s` | s | The same as `neighbour_time_to_segment_s`, for itself |
| `in_segment`, `segment_distance_travelled`, `segment_distance_ahead`, `segment_distance_behind` | true/false, m | Version 3. The same as the neighbour's passage fields above, for itself |

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

## Pair-level fields (version 2)

A rule is evaluated once per pair, on one snapshot that both agents share
(`rule-matching.md`). For that to stand for each agent evaluating the rule on its own, a
condition may use only what **both** agents compute **identically**: quantities of the
pair, and attributes of either agent that the other can see. The environment fields above
fail that test (each is measured at the observer's own position, along its own path), and
so do `bearing_rad`, `relative_position_m`, `relative_velocity_mps` and
`neighbour_heading_relative_rad` (each is in the observer's frame, so the two agents get
different numbers). `distance_m`, `closing_speed_mps` and `time_to_collision_s` pass it:
swapping the two agents leaves each unchanged.

The fields of `pair` are added for rules. They are computed by `pair_features`
(`negsim/avoidance/perception.py`) **once per pair and step, with the lower-numbered agent
first**, and the same object goes into both agents' records, so the two carry the same
values to the last bit, not merely the same values up to rounding.

| Field | Unit | Meaning | Needs to be visible |
|---|---|---|---|
| `encounter_class` | | The kind of encounter, decided in the order below | `speed` and `size`; otherwise `null` |
| `heading_difference_rad` | rad | How far apart the two directions of travel are, from 0 (the same way) to π (opposite ways) | nothing: headings are always perceived |
| `min_corridor_width_m` | m | The narrowest free width of the passage along the straight line between the two centres, below | nothing: walls are always perceived |
| `age_difference_years` | years | The difference between the two ages, never negative | `age`, and both agents must have one; otherwise `null` |
| `single_file_segment` | | The name of the single-file segment that makes the class `single_file_segment`; `null` for any other class | as `encounter_class` |

The record also carries, for each of the two, how soon it would reach that segment
(`observer.time_to_segment_s`, `neighbour_time_to_segment_s`): its distance to the
segment's free space, divided by its present speed; 0 if it is inside; `null` if it is
standing still or the class is not `single_file_segment`. Both come from the same
`pair_features` call.

**`encounter_class`.** Decided in this order:

1. **`single_file_segment`**, if a single-file segment the scenario declares is too narrow
   for the two to pass in (narrower than their two diameters together: the arbiter's own
   test, `coordination.py`) and **each** of the two is inside it or facing it. "Facing"
   means the nearest point of the segment is less than 90° off the agent's direction of
   travel. An agent that has come out of the far end has the segment behind it, so the
   pair stops being in this class once one of them is through.
2. **`none`**, if the two are not approaching each other: `p · w ≥ 0`, where `p` is the
   relative position and `w` the relative velocity. Since `d/dt |p|² = 2 p · w`, the
   distance between them is not shrinking. Two agents standing still are `none`.
3. Otherwise by `heading_difference_rad`: **`overtaking`** below 60°, **`head_on`** above
   120°, **`crossing`** from 60° to 120°.

The two angles cut the range from 0° to 180° into three equal parts. **They are a
definition with no source `[placeholder]`**; a sourced classification of pedestrian
encounters would replace them. Both are constants in `perception.py`; changing either is a
new version of this record.

**`min_corridor_width_m`.** Along the straight line from the lower-numbered agent's centre
to the other's, at points no more than 0.25 m apart and including both ends, the distance
to the nearest wall is measured at right angles to the line on each side, and the two are
added. The smallest such width is the value. A side with no wall within the environment
range counts as the environment range: the passage is as wide as either agent can tell.
So in open ground the value is twice the environment range (25 m with the 12.5 m sensing
radius), never `null`, and a rule's "wide enough" test is true there. A point inside a
wall counts as width 0. Between two agents walking along a corridor this is the corridor's
width; between two agents on either side of a bottleneck it is the bottleneck's. The
sampling can miss a narrowing shorter than 0.25 m along the line; no shipped scenario has
one.

These are the only places a pair-level field is not simply a number: `encounter_class`
and `single_file_segment` are names, and every field is `null` when what it needs is
hidden. A rule's comparison on a `null` value is false (`rule-format.md`).

## Passage fields (version 3)

Two agents that meet **inside** a single-file passage cannot pass, and one of them has to back
out (`derivations.md`, section 17). Who should can depend on how far each has walked in, which
version 2 could not say. Four values per agent say it, computed by `segment_position`
(`negsim/avoidance/perception.py`) **once per pair, in the same `pair_features` call as the
times to the segment**, so the two agents' records carry the same values:

| Field | Unit | Meaning |
|---|---|---|
| `in_segment` | true/false | Whether the agent's centre is inside the passage (its free space, the segment's rectangle, edges included) |
| `segment_distance_travelled` | m | How far it has walked in: its distance, along the passage, from the end it came in by |
| `segment_distance_ahead` | m | Its distance, along the passage, to the end in front of it |
| `segment_distance_behind` | m | Its distance, along the passage, to the end behind it |

**Which passage.** The one named in `pair.single_file_segment`: the segment that makes the
pair's class `single_file_segment` (the passage too narrow for the two, which each is inside or
facing). For any other class, or with `speed` or `size` hidden, there is no such passage and all
four are `null`.

**Ahead and behind come from the two positions alone.** The passage's axis is its long side, and
its ends are its short sides. The end *ahead* of an agent is the one on the other agent's side
along the axis; the end *behind* it, the other one. In a meeting each faces the other, so this
needs nothing the other cannot see: no path, no goal, not even a heading, which for an agent
that is backing out points the wrong way. The end it came in by is, in a meeting, the end behind
it, so **`segment_distance_travelled` equals `segment_distance_behind`**; both are kept, as the
issue names both, and the first says what it is for. The four are a *meeting*'s fields: for two
agents walking the **same** way through a passage, the leading agent's "ahead" end is behind it.
No shipped rule or scenario uses them so (open question Q3 of `WORK_LOG-32.md`).

**Null handling.** `in_segment` is `false` for an agent outside the passage and `null` when the
pair has no passage; the three distances are `null` unless the agent is inside, and when the two
are level along the axis (which two bodies in a single-file passage cannot be). A rule's
comparison on a `null` value is false, and a role assignment on one does not apply
(`rule-format.md`, section 4), so a rule about a meeting inside a passage matches only when both
are inside.

*Tested:* `tests/test_perception.py` (the definitions, both agents' records equal, null
handling); `tests/test_rules_matching.py` (the shared snapshot equals each agent's own).

## The group (version 3)

`ethnic_group` is a persona attribute (`negsim/personas/schema.py`) holding a **fictional** label
such as `Kestrop`, from a configurable set of invented names that carry no description
(`fictional-groups.md`). An agent knows its own (`observer.attributes`); it sees the neighbour's
(`neighbour_attributes`) only when the run's `ethnic_group` switch is on, which it is not by
default, independently of the `age` and `gender` switches. A persona that has no group has no
`ethnic_group` key anywhere, so records of runs without groups are as before.

**No rule may read it.** The attribute is flagged as not readable by rules
(`AttributeSpec.rule_referenceable` is false; `NOT_RULE_REFERENCEABLE` in
`negsim.personas.schema`). The rule loader refuses any rule that names it, in a condition, a role
assignment or a tie policy, derived names included, as `protected_attribute`
(`rule-format.md`, section 14); and nothing a rule can read is derived from it: no pair-level
field uses it, and a snapshot (`rule-matching.md`) never holds it, so even a rule that got past
the loader would find nothing to read. It is in the record for what an agent may *see*: the
situation a model is told, and analysis.

## An example

Agent 0 (a woman of 25) in the wide corridor, at the moment agent 1 (a man of 70) comes
within its 12.5 m sensing radius, walking toward it: step 14 of the exactly symmetric
head-on under plain ORCA. The committed `runs/si1_head_on_side_preference/001_symmetric_plain`
holds this record as version 1; this is the same moment as version 3 records it (no passage,
so the passage fields are `null`; no group):

```json
{
  "schema_version": 3,
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
  "neighbour_time_to_segment_s": null,
  "neighbour_in_segment": null,
  "neighbour_segment_distance_travelled": null,
  "neighbour_segment_distance_ahead": null,
  "neighbour_segment_distance_behind": null,
  "neighbour_attributes": {"age": 70, "gender": "male"},
  "observer": {
    "radius_m": 0.25,
    "speed_mps": 1.3,
    "heading_rad": 0.0,
    "preferred_speed_mps": 1.3,
    "attributes": {"age": 25, "gender": "female"},
    "time_to_segment_s": null,
    "in_segment": null,
    "segment_distance_travelled": null,
    "segment_distance_ahead": null,
    "segment_distance_behind": null
  },
  "environment": {
    "nearest_wall_distance_m": 0.875,
    "free_width_m": 1.75,
    "free_width_left_m": 0.875,
    "free_width_right_m": 0.875,
    "single_file_ahead_m": null
  },
  "pair": {
    "encounter_class": "head_on",
    "heading_difference_rad": 3.141593,
    "min_corridor_width_m": 1.75,
    "age_difference_years": 45,
    "single_file_segment": null
  }
}
```

The two have the same body and the same speeds. A persona changes what is perceived and
nothing physical (`parameters.md`, section 5). Agent 1's record of agent 0, built on the
same step, has the same `pair` block, object for object.

## What a provider does with it

A directive provider is a class with one method, `directive(record) -> AvoidanceDirective`
(`negsim/avoidance/directives.py`). It is called once per interaction, with the record
above. Three are provided:

- `NullProvider`: plain ORCA for everyone.
- `StaticProvider`: directives written in the experiment config, by default, per agent, or
  per ordered pair of observer and neighbour. What it returns holds until the interaction
  ends, except `speed_scale`, which since issue #28 stops applying once the encounter has
  passed (`derivations.md`, section 15).
- `RuleDatabaseProvider` (issue #28, `negsim/rules/provider.py`): directives from stored
  rules. Answering `directive(record)` it evaluates the rules on the record alone, as one
  agent on its own would. In a run it also follows each pair from step to step, which is
  where the matching policy of `rule-matching.md` lives: one shared snapshot per pair,
  re-evaluation, holding, priority, expiry.

A negotiation provider is to come behind the same interface.

## Change log

- **1** (2026-10-13, issue #26): first version.
- **2** (2026-10-14, issue #28): the pair-level fields for rules: `pair` (with
  `encounter_class`, `heading_difference_rad`, `min_corridor_width_m`,
  `age_difference_years`, `single_file_segment`), `observer.time_to_segment_s` and
  `neighbour_time_to_segment_s`. Nothing of version 1 was removed or changed meaning. A run
  folder written under version 1 is still checked against version 1.
- **3** (2026-10-16, issue #32): the passage fields, `observer.in_segment`,
  `observer.segment_distance_travelled`, `observer.segment_distance_ahead`,
  `observer.segment_distance_behind` and the four `neighbour_` fields of the same names; and the
  group, `ethnic_group`, in `observer.attributes` and, when its switch is on, in
  `neighbour_attributes`, flagged as not readable by rules. Nothing of version 2 was removed or
  changed meaning. Folders written under versions 1 and 2 are checked against their own; a
  version 2 record still reads back (`PerceptionRecord.from_dict`), its passage fields missing.
