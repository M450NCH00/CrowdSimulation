# The rule format, schema versions 1 to 3

A rule says: **when** two agents meet in a certain way, **give them roles**, and **tell each
role what to do**. Rules are stored in the rule database (`rule_db/`), one file per version
of each rule, and followed by the `RuleDatabaseProvider` (`rule-matching.md`). Later
sub-issues will have an LLM propose rules (SI-3) and extract them from behaviour (SI-4) **in
exactly this format**, so it is written down here in full.

**A rule is data, never code.** A condition compares fields from a fixed list with
constants written in the rule. There is no expression to parse, nothing is looked up by a
name taken from a file, and nothing in a rule is ever passed to `eval` or `exec` or run in
any other way. A test scans the package for such calls (`tests/test_rules_format.py`).

The structure is fixed by a JSON Schema, `rule_db/schema/rule.v1.schema.json`, and every
rule is checked against it when it is loaded. The schema can only say what is allowed where;
the checks of section 9 say the rest. Sections 1 to 11 describe version 1. **Version 2**
(issue #30, section 12) adds what generated rules need: the source type `stated`, an
`intent`, and the results of `screening` them; a version 1 file loads exactly as before.
Section 13 defines the **canonical form** of a rule, by which two rules are the same.
**Version 3** (issue #32, section 14) adds what a meeting inside a single-file passage needs:
the directive field `back_up`, `true` or `false` as the value of a comparison, and four
passage fields; versions 1 and 2 load exactly as before. In every version, a rule that reads
a person's group is refused (`protected_attribute`, section 14).

## 1. An example

The issue's example rule, as it is in the database (`rule_db/rules/younger_yields_head_on.v1.yaml`):

```yaml
schema_version: 1
rule_id: younger_yields_head_on
version: 1
status: test_seed
description: >
  When two people of quite different ages meet head-on and are within six seconds of
  colliding, the younger does all of the avoiding.
provenance:
  source_type: hand_written
  source_ref: "issue #28 (SI-2), Part 6, seed rules; the example rule of Part 2"
  created_at: 2026-10-14
  author: "the user (specification in issue #28); written out by Claude Code (claude-opus-5-5)"
  notes: >
    Test fixture only. Not a claim about human behaviour. ...
  validation_evidence: []
encounter: head_on
when:
  all:
    - {field: pair.time_to_collision_s, op: "<=", value: 6.0, unit: s}
    - {field: pair.age_difference_years, op: ">=", value: 20, unit: years}
roles:
  by: {field: agent.age, order: ascending, assign: [yielder, other], tie: no_match}
directive:
  yielder: {responsibility_share: 1.0}
  other: {responsibility_share: 0.0}
priority: 20
```

## 2. The parts of a rule

| Key | Required | Value |
|---|---|---|
| `schema_version` | yes | `1`: the version of this format |
| `rule_id` | yes | Lower case letters, digits and `_`, starting with a letter, 3 to 64 long. The same for every version of a rule |
| `version` | yes | 1, 2, 3, ...: this version of the rule |
| `status` | yes | `test_seed`, `candidate`, `validated`, `rejected` or `retired` (section 8) |
| `description` | no | What the rule says, in words, for people |
| `provenance` | yes | Where the rule came from (below) |
| `encounter` | yes | The encounter class it applies to: `head_on`, `crossing`, `overtaking`, `single_file_segment`, or `any` (section 3) |
| `when` | yes | Its condition (section 4). `{all: []}` is "always" |
| `roles` | yes | `symmetric`, or a role assignment (section 6) |
| `directive` | yes | One directive per role (section 7) |
| `priority` | yes | A whole number from 0 to 1000; higher wins (`rule-matching.md`) |
| `expiry` | no | `passed` (the default) or `out_of_range` (section 7) |

`provenance`:

| Key | Value |
|---|---|
| `source_type` | `hand_written`, `negotiated` (SI-3) or `extracted` (SI-4); in version 2 also `stated` (section 12) |
| `source_ref` | Free text now: where it came from. Later a run id, a conversation id, or a paper reference |
| `created_at` | The date, `YYYY-MM-DD` |
| `author` | A person, or a model with its prompt version |
| `notes` | Anything a reader should know; may be empty |
| `validation_evidence` | A list, empty until the validation sub-issue (SI-6) fills it. Each entry is an object; its form is SI-6's to define |

## 3. Encounters

A rule applies only to pairs in its encounter class (or to any class, with `any`). The
class is a pair-level field of the perception record, defined in `perception.md`, section
"Pair-level fields":

| Class | When |
|---|---|
| `single_file_segment` | A declared single-file segment too narrow for the two is ahead of both (each is inside it or facing it). Decided first |
| `head_on` | Approaching each other, directions of travel more than 120° apart |
| `crossing` | Approaching each other, 60° to 120° apart |
| `overtaking` | Approaching each other, less than 60° apart |
| `none` | Not approaching each other. No rule applies, not even one written for `any` |

The class needs the agents' speeds and sizes to be visible; when they are not, it is
missing and no rule applies.

## 4. Conditions

A condition is a **comparison**, or a group:

```yaml
{field: pair.distance_m, op: "<", value: 5.0, unit: m}       # a comparison
all: [<condition>, <condition>, ...]                          # every one holds (an empty all holds)
any: [<condition>, <condition>, ...]                          # at least one holds (at least one item)
```

Groups nest to any depth. A comparison has:

| Key | Value |
|---|---|
| `field` | A field from section 5, with its prefix |
| `op` | `<`, `<=`, `>`, `>=`, `==`, `!=`, or `in` |
| `value` | A number or a name; for `in`, a list of them |
| `unit` | **Every comparison on a number states its unit**, and it must be the field's unit: `m`, `s`, `m/s`, `rad`, `years`. An angle may also be written in `deg`, which is converted. A comparison on a name has no unit |

**Operators.** The four orderings apply to numbers only; `==`, `!=` and `in` to numbers and
names. `in` holds if the value equals any item of the list.

**A comparison on a missing value is false.** A value is missing when the run's visibility
settings hide it, or when it does not exist for the pair: a time to collision for two agents
that would not collide, a time to a segment outside the single-file class. Every operator
gives false on it, `!=` and `in` included. A rule never fires on something its agents could
not see.

## 5. What a rule may read

A rule is evaluated once per pair, on one snapshot the two agents share. That stands for
each agent applying the rule on its own **only if both compute every value the rule reads
identically** (`rule-matching.md`, section 1). So a rule may read only:

- **pair-level fields**, the same whichever agent computes them; and
- **attributes of either agent that the other can see** under the run's visibility settings.

The prefix says how a field is used:

| Prefix | Where | Meaning |
|---|---|---|
| `pair.` | conditions | A pair-level field |
| `either.` | conditions | An agent-level field: the comparison holds for **at least one** of the two |
| `both.` | conditions | An agent-level field: the comparison holds for **each** of the two |
| `agent.` | role assignments | An agent-level field: the two agents' values are ordered against each other |

Pair-level fields (`pair.`):

| Field | Unit | Meaning | Needs visible |
|---|---|---|---|
| `encounter_class` | name | One of the five classes of section 3 | `speed`, `size` |
| `distance_m` | m | Between the two centres | |
| `closing_speed_mps` | m/s | How fast the distance is shrinking; negative if growing | `speed` |
| `time_to_collision_s` | s | Until the bodies touch at present velocities; missing if they would not | `speed`, `size` |
| `heading_difference_rad` | rad | How far apart the directions of travel are, 0 to π | |
| `min_corridor_width_m` | m | The narrowest free width along the line between them; as far as can be seen in open ground (`perception.md`) | |
| `age_difference_years` | years | The difference between the two ages | `age` |

Agent-level fields (`either.`, `both.`, `agent.`):

| Field | Unit | Meaning | Needs visible |
|---|---|---|---|
| `age` | years | Age | `age` |
| `gender` | name: `female`, `male`, `nonbinary` | Gender | `gender` |
| `speed_mps` | m/s | Present speed | `speed` |
| `radius_m` | m | Body radius | `size` |
| `time_to_segment_s` | s | Distance to the single-file segment over present speed; 0 inside; missing standing still or outside that class | `speed`, `size` |
| `in_segment` | true/false | **Version 3.** Whether this person is inside the single-file segment; missing outside that class | `speed`, `size` |
| `segment_distance_travelled` | m | **Version 3.** How far this person has walked into the segment; missing unless inside it | `speed`, `size` |
| `segment_distance_ahead` | m | **Version 3.** Distance to the segment's end in front of this person; missing unless inside it | `speed`, `size` |
| `segment_distance_behind` | m | **Version 3.** Distance to the segment's end behind this person; missing unless inside it | `speed`, `size` |

The four version 3 fields (issue #32, `perception.md`, "Passage fields") are computed once per
pair from the two positions and the passage: "ahead" is the end on the other person's side,
"behind" the other end, and in a meeting `segment_distance_travelled` equals
`segment_distance_behind`. **A rule may read a field only if its `schema_version` has it**: to a
rule of version 1 or 2 the four are `unknown_field`, so such a rule reads what it always could.
`in_segment` is true or false: it is compared with `==`, `!=` or `in`, with `true` or `false` and
no unit, and cannot order two agents.

Every rule also reads the encounter class, so every rule needs `speed` and `size` visible.
A run whose visibility settings hide something one of its rules reads is refused before it
starts (`visibility`), naming the rule.

**What a rule may not read, and why** (refused as `unobservable_field`):

| Field | Why the two agents cannot both use it |
|---|---|
| `task` | Never in a perception record: no agent sees another's errand |
| `backstory` | Free text, hidden by default; not something two agents can compare |
| `assertiveness`, `residence`, `memory_note` | Core factors of track #55 (issue #60) that only the person knows: the other agent cannot see them. A rule-generation check counts such a rule as `needs_communication` |
| `preferred_speed_mps`, `max_speed_mps`, `goal`, `path` | An agent knows its own, never another's |
| `nearest_wall_distance_m`, `free_width_m`, `free_width_left_m`, `free_width_right_m`, `single_file_ahead_m` | Measured at one agent's own position or along its own path: the two get different values. Use `pair.min_corridor_width_m` and `agent.time_to_segment_s` |
| `bearing_rad`, `relative_position_m`, `relative_velocity_mps`, `neighbour_heading_relative_rad` | In one agent's own frame. Use `pair.heading_difference_rad` |
| Any field under `observer.`, `neighbour.`, `self.`, `other.`, ... | Names one agent from its own point of view: each agent would read the *other* one's value. Use `either.`/`both.` or `agent.` |

**This refusal is a category of its own for the negotiation sub-issue (SI-3).** A rule that
needs such a field could only be followed if the two agents told each other something first.
It is not executed in SI-2; it is reported with the reason, and SI-3 can take it up.
Anything not in these tables is `unknown_field`.

**What a rule may never read: a person's group** (`protected_attribute`, issue #32). An agent may
see another's fictional group (`perception.md`, "The group"), but no rule may condition on it.
A rule whose condition or role assignment, its tie policy and role names included, names it, or
anything derived from it (any name containing `ethnic`, such as `pair.same_ethnic_group`), or a
group label, is refused as `protected_attribute`, **before every other check**: whatever else is
wrong with such a rule, that is what it is counted as. Section 14 has the details. **Since issue
#61 so is perceived attractiveness**, how one person sees another, until the supervisor decides
(`pairwise-factors.md`, section 7).

## 6. Roles

`roles: symmetric` gives both agents the same directive, under the single role name `both`.

A **role assignment** orders the two agents by an agent-level number and gives them the
two roles in turn:

```yaml
roles:
  by: {field: agent.age, order: ascending, assign: [yielder, other], tie: no_match}
```

| Key | Value |
|---|---|
| `field` | An `agent.` field that is a number |
| `order` | `ascending`: the agent with the smaller value gets the first role. `descending`: the larger |
| `assign` | The two role names, distinct, not `both` |
| `tie` | **Required.** What happens when the two values tie. Version 1 offers one policy, `no_match`: the rule does not apply to the pair, and the next rule down, or the baseline, decides |
| `tie_within`, `unit` | Optional: values no more than this far apart (in the unit stated, which must fit the field) count as a tie. Without it only exactly equal values tie |

A missing value cannot be ordered: the rule does not apply either.

## 7. Directives

`directive` has one entry per role, named as the roles are (`both` for a symmetric rule).
Each entry may set any of the fields of `AvoidanceDirective` (`architecture.md`, DD28), with
exactly these names: the first five in every version, `back_up` from version 3:

| Field | Values | What it does |
|---|---|---|
| `side_preference` | `left`, `right`, `none` | On a collision course, pass the other on that side, as each agent sees it looking at the other. Both keeping `left` pass right shoulder to right shoulder |
| `responsibility_share` | 0 to 1 | On a collision course, the share of the change needed that this agent makes. Plain ORCA is 0.5 |
| `speed_scale` | 0 or more | Multiplies the agent's preferred speed |
| `clearance_margin` | metres, 0 or more | Extra space kept between the two bodies |
| `passage_order` | `leader`, `follower`, `none` | Who goes first through a single-file segment, handed to the arbiter |
| `back_up` | `true`, `false` | Version 3. Inside a single-file segment the two meet in, back out of it at one's own backing speed, wait for the other to come through, and go on (`derivations.md`, section 17). The other goes first. A rule that sets it makes exactly one of two roles back up (section 14) |

**A field the rule does not set takes its baseline value** (plain ORCA: no side, 0.5, 1, 0,
none, false). A pair follows one rule at a time; fields are never merged across rules
(`rule-matching.md`).

**Expiry.** By default everything a rule tells a pair stops applying when the encounter has
passed: the two are separating and clear of each other by more than their clearance margin
(`derivations.md`, section 15). `expiry: out_of_range` keeps it until the pair interaction
ends instead (the neighbour leaves the sensing radius, or one of them arrives). Use it for a
directive that matters after the two bodies have separated, such as a passage order, which
the arbiter uses for as long as it holds the pair.

## 8. Versions and status

**A version is never edited.** Any change, including a change of status or added evidence,
is a new file, `<rule_id>.v<n+1>.yaml`, and the old file stays. `rule_db/MANIFEST.json`
freezes the SHA-256 of every file; a file that does not match, or is not listed, is refused
(`manifest`), and the versions of a rule must run 1, 2, 3, ... (`history`).
`python ruledb.py history <rule_id>` shows every version and what changed between them.

| Status | Meaning | May be switched on |
|---|---|---|
| `test_seed` | Written to exercise the machinery; makes no claim about people (all of SI-2's) | yes |
| `candidate` | Proposed (by negotiation, extraction or hand), not yet checked against evidence | yes |
| `validated` | Checked against human evidence (SI-6) | yes |
| `rejected` | Checked and found wanting | no |
| `retired` | No longer used | no |

## 9. What is checked when a rule is loaded

In this order; the first failure refuses the rule, with its category and a message saying
what and where. `python ruledb.py validate --file <path>` checks any rule file this way.

| Category | Refused when |
|---|---|
| `file` | The file cannot be read, or is not named `<rule_id>.v<version>.yaml` after what it holds |
| `protected_attribute` | The condition or the role assignment (its tie policy and role names included) names a person's group, anything derived from it, or a group label (issue #32; checked before everything else, section 14) |
| `no_tie_policy` | A role assignment does not state `tie` (checked first, so that the reason is plain) |
| `schema` | The structure does not fit the JSON Schema of the version the rule names: a missing or unknown key, a wrong type, a value outside its list, a version that does not exist |
| `unknown_field` | A field not in section 5, or a prefix where it does not belong |
| `unobservable_field` | A field the two agents cannot both see (section 5) |
| `unit` | A number without its unit, a unit that does not fit the field, or a unit on a name |
| `value` | A value of the wrong kind, such as a gender that is not one of the three |
| `operator` | An ordering of a name, or a role assignment by a name |
| `roles` | The directive's entries do not match the role names |
| `reciprocity` | The two roles' responsibility shares sum to less than 1 (a symmetric rule: its share is below 0.5). ORCA keeps a pair free of collisions only if they sum to at least 1 (`derivations.md`, section 9) |
| `passage_order` | Passage orders that are not one `leader` and one `follower` (or neither set) |
| `back_up` | Version 3. A rule that sets `back_up` for any role does not make exactly one of two roles back up, or makes the role that backs up go first (section 14) |
| `side` | Two roles told to pass on opposite sides: both would step the same way (`derivations.md`, section 10) |

In the database, also: `manifest` and `history` (section 8). When an experiment switches
rules on: `ruleset` (a rule or version not in the database), `status` (a rejected or retired
rule), `ambiguous` (two rules that could tell one pair different things at one priority:
`rule-matching.md`, section 4), and `visibility` (section 5).

The test fixtures under `tests/fixtures/rules/` hold one refused rule for each category.

## 10. Rule sets: which rules an experiment follows

A rule set is a named, frozen list of rule versions, `rule_db/rulesets/<name>.yaml`:

```yaml
name: default
description: ...
rules:
  keep_left_head_on: 1
  overtaker_keeps_clear: 1
  single_file_first_arrival: 1
  younger_yields_head_on: 1
```

An experiment switches rules on in its `directives` block, at the top or in a level of a
factor:

```yaml
directives:
  provider: rules
  ruleset: default                       # start from a rule set (optional)
  disable: [keep_left_head_on]           # then leave some out
  enable: {keep_right_head_on: 1}        # then add rule versions
  hysteresis_steps: 3                    # the matching policy's hysteresis (rule-matching.md)
```

That is how `keep_right_head_on`, which is not in `default`, is compared with
`keep_left_head_on`: a level that disables one and enables the other. Switching both on at
once is refused (`ambiguous`). Every run records the rules it followed, each with its
version and the SHA-256 of its file (`log-schema.md`).

## 11. Things a rule author should know about ORCA

- **A time to collision below about 3 s is rare.** Once ORCA brakes a head-on pair it closes
  the gap at gap / τ per step, so the time to collision read on the next step is τ − dt =
  2.9 s, step after step. A condition `time_to_collision_s <= 2.8 s` never fires in the
  shipped head-on (`tests/test_rules_matching.py`).
- **A side preference and a share act only on a collision course.** Off one, they change
  nothing (`derivations.md`, sections 9 and 10).
- **A share of 1 with no side can mean walking backwards.** In an exactly symmetric head-on
  the agent with share 1 backs away along its line instead of stepping aside (issue #26).
  `younger_yields_head_on` sets no side, so it shows this.
- **`min_corridor_width_m` is measured across the line between the two**, so a slanted line
  measures a little wider than the corridor (0.80 m for the 0.8 m bottleneck at the start of
  the shipped scenario).

## 12. Schema version 2 (issue #30)

Version 2 is for rules that a model generates (issue #30): one model stating a rule, or two
negotiating one (`rule-generation.md`). **What a rule does is the same in both versions**:
encounter, condition, roles, directives, priority, expiry, and every check of section 9.
Version 2 adds three keys and two records of provenance; the schema is
`rule_db/schema/rule.v2.schema.json`.

| Key | Where | Required | Value |
|---|---|---|---|
| `schema_version` | top | yes | `2` |
| `stated` | a value of `provenance.source_type` | | One model stated the rule, seeing both agents (condition B of issue #30). Beside `negotiated` (two model agents agreed on it, condition A), `hand_written` and `extracted` |
| `intent` | top | no | What the rule is meant to do, in words, at most 500 characters. **Never executed.** Used later to find rules the format could not express (`rule-generation.md`, section 6) |
| `screening` | top | no | The results of replaying the rule and of screening it in a crowd, a list of objects: `kind` (`replay` or `crowd`), `experiment`, `scenario`, `baseline`, `case_id`, `seeds`, `screened_utc`, `verdict` (`passed`, `failed`, or `recorded` for a replay, which has no pass mark), `reasons`, and `results` (the numbers, against the baseline on the same seeds) |
| `generation` | `provenance` | no | Filled only by the rule writer: `experiment`, `condition` (`negotiated` or `stated`), `case_id`, `canonical_hash` (section 13), and `sessions`, every session that produced the rule, each with `session_id`, `design_cell`, `model`, `model_returned`, `prompt_template`, `created_utc`, `proposed_by` and `repeat` |
| `promotion` | `provenance` | no | Filled only by the promotion command: `from_database`, `staged_rule`, `staged_sha256`, `reason`, `promoted_utc`, `by` |

A version 2 rule, as the test fixture `tests/fixtures/rules/v2/stated_keeps_clear_any.v1.yaml`
has it (shortened):

```yaml
schema_version: 2
rule_id: stated_keeps_clear_any
version: 1
status: candidate
intent: Keep a little more room between the two whenever they meet.
provenance:
  source_type: stated
  ...
  generation: {experiment: ..., condition: stated, case_id: ..., canonical_hash: ..., sessions: [...]}
encounter: any
when: {all: []}
roles: symmetric
directive:
  both: {clearance_margin: 0.15}
priority: 100
screening:
  - {kind: crowd, scenario: bidirectional_flow, baseline: orca_perturbed_v1, verdict: passed, ...}
```

**Reading both versions.** The loader reads `schema_version` first and checks the rule
against the schema of that version (`negsim/rules/database.py`, `RuleSchemas`); both
schema files are frozen in the manifest. A version 1 file is therefore read exactly as it
was before version 2 existed: version 1 has no `intent`, no `screening` and no `stated`,
and a version 1 file that uses any of them is still refused (`schema`). Any other version
number is refused with the versions that exist.

**Migration notes.** Nothing is migrated automatically, and no file is rewritten: a version
is never edited (section 8).

- A version 1 rule stays a version 1 rule, and loads, matches and is followed exactly as
  before.
- To give a rule an intent, a screening record or a promotion record, write its **next
  version** (`<rule_id>.v<n+1>.yaml`) with `schema_version: 2`, and freeze it in the
  manifest. Every version 1 key means the same in version 2, so the rest may be copied as
  it is; the test `test_version_1_is_unchanged_it_does_not_take_stated_or_intent` checks
  that one rule written in either version is the same rule.
- Rules the writer of issue #30 generates are version 2 from their first version.
- `python ruledb.py history <rule_id>` lists, between consecutive versions, changes to
  `schema_version`, `intent` and `screening` as well as to the rest.

## 13. The canonical form of a rule (issue #30)

Two rules are **the same rule** when their canonical forms are equal. The canonical form is
what the two agents of condition A accept by hash, and what the writer stores a rule once
under however many sessions produced it (`rule-generation.md`); SI-4 will reuse it. It is
`negsim/rules/canonical.py`:

1. **What is in it**: what the rule does, and nothing else. The keys `encounter` and `when`
   (its condition), `roles`, `directive`, and `expiry` if the rule states one. Everything
   else is metadata and left out: `schema_version`, `rule_id`, `version`, `status`,
   `description`, `intent`, `provenance`, `priority`, `screening`.
2. **Keys sorted**, at every depth.
3. **Numbers normalised**: every number is written the same way whatever way it was
   written: a whole number as an integer (`6`, `6.0` and `6.00` are all `6`), any other
   number rounded to 12 significant digits and written as the shortest decimal that gives
   it back. `true` and `false` are not numbers.
4. **Nothing else is changed.** Units are not converted (`90 deg` and `1.5708 rad` differ),
   the items of `all`, `any` and `in` keep their order, and a field set to its baseline
   value is not removed. Telling such rules apart from rules that differ in substance is
   semantic equivalence, which is SI-4's.
5. **Serialised** as JSON with no spaces (`separators=(",", ":")`), keys sorted, UTF-8,
   and **hashed** with SHA-256. The hash is 64 hexadecimal characters; a *proposal id* is
   its first 12, which is what an agent is shown and writes back.

The canonical form can be computed for anything shaped like a rule, valid or not: a
proposal that the loader would refuse still has a hash, so that it can be accepted, counted
and compared like any other (`rule-generation.md`, section 6).
*Tested:* `tests/test_rulegen_canonical.py`.

## 14. Schema version 3 (issue #32), and what no rule may read

Version 3 is for two people who meet **inside** a single-file passage, where neither can pass
and one has to back out (`derivations.md`, sections 17 and 18). Before it, the format could
not say "the one who has walked less far in backs out": it had no field for how far each had
walked in, and no directive for backing out. Everything of version 2 is in version 3 and means
the same; version 3 adds three things, and the schema is `rule_db/schema/rule.v3.schema.json`.

| What | Where | Value |
|---|---|---|
| `schema_version` | top | `3` |
| `back_up` | a directive field | `true` or `false` (section 7) |
| `true`, `false` | the value of a comparison | For a field that is true or false, so far only `in_segment`: compared with `==`, `!=` or `in`, with no unit; it cannot order two agents |
| `in_segment`, `segment_distance_travelled`, `segment_distance_ahead`, `segment_distance_behind` | agent-level fields (`either.`, `both.`, `agent.`) | Section 5 and `perception.md`, "Passage fields": whether each is inside the single-file segment the two meet in, and how far it has walked in and is from each end. Missing (null) outside the passage, and a comparison of a missing value is false |

The seed rule `passage_shorter_backs_out` (`status: test_seed`, not in the `default` rule set)
is version 3, shortened:

```yaml
schema_version: 3
rule_id: passage_shorter_backs_out
version: 1
status: test_seed
encounter: single_file_segment
when:
  all:
    - {field: both.in_segment, op: "==", value: true}
roles:
  by: {field: agent.segment_distance_travelled, order: ascending, assign: [backs_out, goes_on], tie: no_match, tie_within: 0.1, unit: m}
directive:
  backs_out: {back_up: true}
  goes_on: {}
priority: 30
expiry: out_of_range
```

It applies the distance criterion of `derivations.md`, section 18; distances walked in within
0.1 m of each other are a tie, and then the rule does not apply and the arbiter's own rule
decides. **It is a test fixture, not a claim about how people behave.** `expiry: out_of_range`
because `passed` is measured between the two bodies, which separate while one backs out; the
manoeuvre, once begun, runs to its end whatever the directive does.

**Reading three versions.** As in section 12: the loader checks a rule against the schema of
the version it names. A version 1 or 2 rule is read exactly as before, and can use none of
what version 3 added: `back_up` in its directive and `true` or `false` as a value are `schema`
errors, and a passage field is `unknown_field` ("added in version 3"). Every field records the
version that added it (`fields.py`, `since`), and a rule reads only those of its own version.

**Who backs up: the consistency check** (DD97). A rule that sets `back_up` for any of its
roles must make **exactly one of two roles** back up, and the one that backs up may not also
be told to go first:

| The rule says | Result |
|---|---|
| `back_up: true` for one role, nothing or `false` for the other | loads |
| `back_up: true` for both roles | refused, `back_up`: neither would get through |
| `back_up: false` for one or both roles, `true` for neither | refused, `back_up`: both would go on |
| `back_up` (true or false) in a symmetric rule | refused, `back_up`: both would back up, or neither would |
| `back_up: true` and `passage_order: leader` in one role | refused, `back_up`: the one that backs out lets the other go first |
| nothing about `back_up` | not checked for it: a meeting inside a passage is then left to the arbiter (`derivations.md`, section 17.1) |

So "both back up, or both proceed, is inconsistent" (the issue's words) is read as being about
a rule that says who backs up; a rule that says nothing of it is not made to. Rule generation
counts the category `back_up` as `inconsistent` (`rule-generation.md`, section 6). When two
agents' directives disagree at run time instead (two that back up, from two providers or two
rules), the pair's combination repairs it as for the other fields (`architecture.md`, DD96):
neither backs up.

**What no rule may read: a person's group** (`protected_attribute`, DD88). An agent may see
another's fictional group when a run shows it (`perception.md`, "The group";
`fictional-groups.md`), but no rule may condition on it. A rule is refused as
`protected_attribute`, **before every other check**, if its condition or its role assignment
(the field, the role names and the tie policy included) names:

- anything containing `ethnic` (`either.ethnic_group`, `pair.same_ethnic_group`,
  `agent.ethnicity`, a role named `ethnic_insider`);
- the attribute itself, or one of the default group labels, as a word (`value: Dremmik`, a role
  named `kestrop`);
- in rule generation, a word the session introduced groups with, or one of its labels
  (`negsim.rulegen.validate`).

**Nor perceived attractiveness** (issue #61, `protected_attribute`). An agent may be told its
own view of someone ("You find them attractive.", `pairwise-factors.md`), but until the
supervisor decides no rule may read it. A rule is refused in the same way, before every other
check, if its condition or role assignment (the same parts) contains `attract` (`attractive`,
`attractiveness`, `attraction`), `beaut`, `handsome` or `pretty`, or "good looking" however it
is joined (`fields.py`, `ATTRACTIVENESS_PATTERN`). The refusal says which of the two it read; the
group's message is unchanged. This keeps attractiveness out of the rule database only: it stays
in the outcome rows and the factor analysis (RF-8).

**Nor real ethnicity** (issue #92, `protected_attribute`; `ethnicity.md`, section 7). Track #55
tells an agent its own census group and, when the design shows it, the other's ("They look
Malay."), so that the screen can measure whether a model treats people differently; no rule may
read it. A field named with `ethnic` (`ethnicity_pair`, `p1_ethnicity`) was already refused, with
the group's message. Since issue #92 a rule is refused in the same way if its condition or role
assignment names a census group or a word for race, as a whole word: `chinese`, `malay`,
`malays`, `indian`, `indians`, `race`, `races`, `racial` (`fields.py`, `REAL_ETHNICITY_WORDS`), and
the refusal says "a person's ethnicity". "Others" alone is an ordinary word and is not refused.

Whatever else is wrong with such a rule, that is what it is counted as: a model trying to
condition a rule on ethnicity is a finding, and the attempt is kept as data, in a category of
its own (`rule-generation.md`, section 6). Independently of the loader, **no field a rule can
read is the group or derived from it, and no snapshot holds it** (`snapshot.py`); tests check
both, and that whether a rule matches never changes with whether the group is seen
(`tests/test_protected_attribute.py`).

**Migration notes.** As for version 2, nothing is rewritten. A rule that is to back one up, or
to read a passage field, is written as its next version with `schema_version: 3`. Rules the
writer generates from sessions of the second prompt version (issue #32) are version 3
(`rule-generation.md`, section 3); those of the first stay version 2.
*Tested:* `tests/test_rules_schema_v3.py`, `tests/test_protected_attribute.py`.
