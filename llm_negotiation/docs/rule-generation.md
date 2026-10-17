# Rule generation (issue #30, SI-3a)

Rule generation turns a conflict into a **candidate rule** in the rule format of issue #28
(`rule-format.md`), in two ways that are to be compared later (SI-3b, SI-4):

- **Condition A, negotiated.** Two model agents, each told the situation from its own point
  of view with its own private information, negotiate a standing rule for future meetings
  like theirs (section 4).
- **Condition B, stated.** One model, told the situation from outside with both people's
  private information, states a rule (section 5).

The conflict is a **case**, taken from a finished baseline run (`cases.md`). A **session**
puts two people into a case (section 2) and tells a model about it in words (section 3).
Every rule a model proposes is **validated** and given a category, and none is discarded
(section 6). The valid agreed or stated rules are written by the **writer** into a staging
database, never into `rule_db/` (section 7), and each is **replayed** alone on its case's own
run and **screened** alone in a crowd (section 8). An experiment type drives it all, with a
budget cap and a worst-case cost preview before any paid call (section 9).

**Status.** Everything here is built and rehearsed on the mock client at no cost. The paid
pilot of the issue (Part 11) is **held**: the supervisor's approval of simulation work is not
recorded in `CLAUDE.md`, and the pricing check has not been done (section 10;
`pricing-check.md`). Nothing in this document is a finding about a language model.

The code is `negsim/rulegen/`: `cases`, `design`, `describe`, `protocol`, `validate`,
`writer`, `replay`, `experiment`, `mock`, `cli`.

**Decisions of the issue**, taken by the user and recorded as decisions (`WORK_LOG-30.md`):
generation is offline, from cases of finished runs; conditions A and B get the same
situation information and differ only in perspective, and neither is told what happened
under plain ORCA; both produce a full rule in the rule format, checked by the existing
loader; a rule that needs private information is rejected and counted as "needs
communication", and the format is not extended to read it (*pending the supervisor*);
generated rules are never switched on together here, each is evaluated alone; Q3 (a rule
with a timing condition losing to an earlier match) and Q11 (matching cost) are deferred to
SI-4. The decisions this project took where the issue left room are DD65 to DD84
(`architecture.md`, section 8.4).

## 1. The pipeline

| Step | What happens | Where |
|---|---|---|
| Cases | A conflict of a primary-baseline run, frozen as data | `cases.py`, `cases.md` |
| Sessions | The design matrix: a case, a persona pair, a condition, an order, a repeat | `design.py`, section 2 |
| Descriptions | The situation in words, first-person (A) or third-person (B), with the rule format | `describe.py`, section 3 |
| Condition A | Two agents take turns until one accepts the other's latest proposal, or the limit | `protocol.py`, section 4 |
| Condition B | One call: a rule and a reason | `protocol.py`, section 5 |
| Validation | Every proposal gets one category | `validate.py`, section 6 |
| Writer | Valid agreed (A) or stated (B) rules into a staging database | `writer.py`, section 7 |
| Replay, screening | Each written rule alone, on its case's run and in a crowd | `replay.py`, section 8 |
| Experiment | All of it from a YAML config, with the budget guard and the cost preview | `experiment.py`, section 9 |

## 2. Sessions: the persona design matrix

A case is geometry; a **session** puts two people into it. So that later analysis can tell
the effects of geometry, age, gender and task apart, the people are varied by six factors,
crossed in full, whose levels an experiment config lists (`design.factors`):

| Factor | Levels | Meaning |
|---|---|---|
| `age_pair` | `same`, `p1_older`, `p2_older` | Both `base_age` (25), or one older by `age_difference` (45 years, so 70) |
| `gender_pair` | `same_female`, `same_male`, `p1_female`, `p1_male` | Person 1 and person 2's genders |
| `task` | `none`, `p1_urgent`, `p2_urgent` | No private information; or person 1's errand urgent ("the emergency room") and person 2's routine ("the supermarket"), or the other way |
| `demographics_visible` | `true`, `false` | `false` is the control: age and gender appear in neither the situation nor the field glossary |
| `mapping` | `p1_lower`, `p1_higher` | Which agent of the case person 1 is |
| `order` | `lower_first`, `higher_first` | Who speaks first (A), or who is described first, as "Person 1" (B) |

**People have no names.** Person 1 and person 2 are slots of the design. A session's people
have an age, a gender and possibly an errand, and nothing else; the errand is private (an
agent's own description says it, and the other's says "You do not know where they are going,
unless they tell you"). The two errands are GameChat's highest- and lowest-priority task types
(`configs/tasks/gamechat_tasks.yaml`); a config may give its own.

**Balanced and reproducible.** The session list is the full factorial of the levels for
every case and condition, each cell as many times as its condition repeats (K for B, once
for A), so within each case and condition every level of a factor, and every pair of levels
of two factors, occurs equally often (`design.balance`). A level list can be narrowed for one
case (`design.per_case`). A session's id says what it is, `A_<case>_<cell>_r<repeat>`, where
`<cell>` is eight hexadecimal characters of the SHA-256 of the cell, so the ids do not depend
on the order; the order is shuffled by a random stream seeded by the experiment's name and
`design.seed`. **DD72 (decision)** sets the levels' meanings above.
*Tested:* `tests/test_rulegen_design.py`.

**A fictional group** (issue #32; `fictional-groups.md`). With `design.ethnicity` enabled each
person also belongs to a fictional group, and three more factors are crossed with the six:

| Factor | Levels | Meaning |
|---|---|---|
| `group_pair` | `same`, `different` | Both people in one group, or each in another |
| `label_rotation` | `0`, `1`, `2` (one per label) | Which label person 1 gets; person 2 gets the same one, or in a `different` pair the next one round the label set, so that each label is each person's equally often |
| `ethnicity_visible` | `true`, `false` | `false` is the control: the groups appear nowhere in what a model is shown. Apart from `demographics_visible`, so that the two can be told apart |

```yaml
design:
  ethnicity:
    enabled: true                         # off unless this says true
    labels: [Kestrop, Dremmik, Pellund]   # the default, in rotation order (DD85)
    framing: ethnic group                 # the words that introduce it (DD86, pending the supervisor)
    factors: {group_pair: [same, different], label_rotation: [0, 1, 2], ethnicity_visible: [true, false]}
```

**It is off by default**, in every config shipped, and a design without the block, or with
`enabled: false`, has exactly the cells and session ids it had before issue #32 (a cell's code
hashes the group's factors only when the cell has them). **A paid run with it on is refused**
unless `CLAUDE.md` records the supervisor's ethics sign-off (`fictional-groups.md`, section 6).

**The full factorial is large.** Per case and condition, the six factors at every level make
3 × 4 × 3 × 2 × 2 × 2 = 288 cells, and the group's three another 2 × 3 × 2 = 12 times as many:
**3,456 cells**, so 3,456 negotiations and, with K = 3, 10,368 statements per case. Many of
them show a model the same words: with demographics hidden the age and gender pairs do not
change a prompt, and with the groups hidden neither do the group pair and the rotation. SI-3b
will need a fraction of the design; which one is not chosen here (the issue says not to). Every
experiment reports the size of its own design (`summary.json`, `design`; `--plan`).
*Tested:* `tests/test_rulegen_groups.py`.

## 3. What a model is shown

All the wording is in three prompt templates, frozen with issue #24's tool
(`negsim/negotiation/templates/`, `MANIFEST.json`, each with its `kind`):
`rulegen_common_v1` (the rule format, the field glossary, the format example: the same, word
for word, in both conditions), `rulegen_negotiate_v1` (condition A) and `rulegen_state_v1`
(condition B). A system prompt is the condition's frame, the situation, the glossary, the
format example and the reply format, about 7,500 characters for a head-on case.

**First-person (condition A)** is drawn from the agent's own perception record in the case
(`perception.md`): itself (age and gender if shown, its errand if it has one, its speed and
usual speed, its body's width), the place (the passage's width and the walls, or the nearest
wall, or open space; a narrowing ahead), and the other (distance and direction, speed and
direction of travel, whether the distance is shrinking, body width; age and gender as they
look, if shown). **Never** anything about the other that cannot be seen: not its errand, its
usual or maximum speed, its goal or its path. For the head-on case `head_on_de176842`, agent
0, an older woman with an urgent errand:

```
ABOUT YOU
- You are 70 years old.
- You are a woman.
- You are on your way to the emergency room.
- You are walking at 1.30 m/s. Your usual walking speed is 1.30 m/s.
- Your body is 0.50 m wide.

WHERE YOU ARE
- You are in a passage 1.75 m wide. The wall on your left is 0.87 m from you, the wall on your right 0.88 m.

THE OTHER PERSON
- They are 12.4 m away, straight ahead of you.
- They are walking at 1.30 m/s, in the opposite direction to you, and the distance between you is shrinking.
- Their body is 0.50 m wide.
- They look about 25 years old.
- They look like a man.
- You do not know where they are going, unless they tell you.
```

**Third-person (condition B)** gives both people's observable state and both errands, as
Person 1 and Person 2 in the order the session gives, then the two of them together
(distance, direction from Person 1, Person 2's direction of travel). **Equal information:**
B is told what A's two agents are told between them, no more; neither is told what happened
under the baseline.

**Numbers** are rounded the same way everywhere: distances along the way (between the two,
to a narrowing, a stretch's length) to 0.1 m; widths (a passage, a body, to a wall) to
0.01 m; speeds to 0.01 m/s; angles to the whole degree; ages in years.

**Neutral wording.** The situation says where the people are and how they move, and nothing
about how such a meeting is or should be settled: no side, no convention, no "usually".
**The format example is a placeholder** (`"<a field>"`, `"<role a>"`), so that it shows the
shape of a rule and suggests no content; no seed rule and no realistic rule appears in any
prompt.

**The field glossary** lists every field a rule may read, with its unit and meaning,
generated in a fixed order from the field catalogue (`negsim/rules/fields.py`) and the rule
schema, never written by hand. Its SHA-256, with and without the demographic fields, is
pinned in the common template: a change to the catalogue or the schema is refused until a
new template version is frozen. When a session hides demographics, the fields that need age
or gender are left out of the glossary as well as out of the situation. **DD73 (decision)**
is what is shown and how it is rounded.
*Tested:* `tests/test_rulegen_describe.py` (every case in both conditions; nothing
unobservable first-person; demographics hidden; no convention named; the glossary pinned).

### 3.1 Prompt version 2 (issue #32)

Issue #32 changed what a model is shown, so its prompts are a **new frozen version**, beside
the first, which is kept and renders exactly as before: `rulegen_common_v2`,
`rulegen_negotiate_v2` and `rulegen_state_v2`, frozen with the same tool on 2026-10-17. An
experiment picks a version by its templates (`negotiation.template`, `statement.template`;
version 1 stays the default, so that every config of issue #30 means what it meant). What
changed from version 1, and nothing else:

| Template | What version 2 adds |
|---|---|
| `rulegen_common_v2` | It describes **rule format 3** (`rule_schema_version: 3`): the glossary, generated as before, now lists the four passage fields (`in_segment`, `segment_distance_travelled`, `segment_distance_ahead`, `segment_distance_behind`), with a line for a field that is true or false; a comparison's value may be true or false; the directive field `back_up`; and the one thing a rule that uses it must say ("gives back_up true to exactly one of the two roles, and not to a role that goes first"). The single-file kind of meeting is "a stretch ahead of both, **or that they are in**". The glossary's hashes are pinned inside it. **A person's group is never in it**: no rule may read one |
| `rulegen_negotiate_v2` (A), `rulegen_state_v2` (B) | Four kinds of line: a person standing still is said to be ("You are standing still"), not to walk at 0.00 m/s; a person inside the single-file stretch is told how far they have walked into it and how far each of its ends is; in A, the other's distance walked in from the other end when both are inside; and, **only when the session shows groups**, each person's group by its label and the framing word ("You belong to the Kestrop ethnic group"). Everything else is version 1's, word for word |

For a meeting inside the passage (`passage_meet_with_speeds_v1`, at rest), agent 0 is told:

```
WHERE YOU ARE
- You are in a passage 0.80 m wide. The wall on your left is 0.40 m from you, the wall on your right 0.40 m.
- You are inside a stretch of the passage 0.80 m wide and 4.0 m long.
- You have walked 2.0 m into this stretch. Its end ahead of you is 2.0 m away, and the end behind you 2.0 m.

THE OTHER PERSON
- They are 0.6 m away, straight ahead of you.
- They are standing still, facing in the opposite direction to you.
- They are inside the stretch too, and have walked 1.4 m into it from its other end.
```

Every number is one both can perceive (`perception.md`, "Passage fields"); neither is told the
other's backing speed, which nobody can see. **When the groups are hidden** (`ethnicity_visible:
false`) they appear nowhere in what a model is shown, a person's own included, nor does the
framing word; with prompt version 1 they never appear (`fictional-groups.md`). A session
records the rule format its prompt described (`rule_schema_version` in its record): its rules
are validated, and written, in that format (sections 6 and 7).
*Tested:* `tests/test_rulegen_prompts_v2.py`.

## 4. Condition A: negotiating a standing rule

Two agents take turns, issue #24's dialogue loop (`negotiation/protocol.py`,
`request_with_retry`): each turn is one request to the model with the speaker's own system
prompt, its own history, and what the other has just done. A turn is a JSON object:

| Key | Value |
|---|---|
| `message` | What the agent says to the other, text (may be empty) |
| `proposal` | A rule in the rule format, or `null` |
| `accept` | The proposal id of the other's latest proposal, if it accepts that proposal exactly as it is; otherwise `null` |
| `no_rule_possible` | `true` if it thinks no rule is possible unless people can talk first; otherwise `false` |

Read with #24's tolerances (whitespace, a Markdown code fence, extra keys; a missing
`proposal` or `accept` is null, a missing `no_rule_possible` false). Not read: a reply that is
not a JSON object, a `message` that is missing or not text, a `proposal` that is neither an
object nor null, an `accept` that is neither text nor null, a `no_rule_possible` that is not a
boolean. **DD74 (decision).** The fourth key is this project's: the issue says an agent may
state that no rule is possible without communication.

**What an agent is shown on its turn.** First: "You speak first." Afterwards: "The other
person's turn:", what they said, their proposal with its proposal id, their `accept` if it
made no agreement and was not a counter-proposal ("They put `<id>` under "accept", which is
not the id of your latest proposal"), their saying that no rule is possible, then "Your
turn." The other's proposal is shown as JSON, as the other wrote it.

**Agreement is by canonical hash.** Every proposal gets the SHA-256 of its canonical form
(`rule-format.md`, section 13); its **proposal id** is the first 12 hexadecimal characters.
The two **have agreed** when one accepts the other's **latest** proposal by its id (or by any
longer prefix of its hash, in either case) and does not, in the same turn, propose a
different rule. A proposal of the same canonical rule beside the acceptance is not a
difference: key order, number formatting and words outside the canonical form (`intent`,
`description`, `priority`) do not change the hash. Any other acceptance is recorded with its
status and does not end the negotiation:

| `accept_status` | What the agent put under `accept` |
|---|---|
| `agreed` | The other's latest proposal's id, with no different rule beside it |
| `accepted_but_counter_proposed` | The other's latest id, beside a different rule: **a counter-proposal, not an acceptance**. The other is shown the new proposal |
| `stale` | The id of an earlier proposal of the other's, no longer its latest |
| `own` | The id of its own proposal |
| `unknown` | No proposal has that id |
| `nothing_proposed` | The other has proposed nothing yet |

**DD75 (decision)** is this definition of agreement, including the counter-proposal rule
the issue states.

**Outcomes** of a negotiation:

| Outcome | When |
|---|---|
| `agreed` | One accepted the other's latest proposal, as above; the rule, its hash, who proposed it and at which turn, who accepted, and whether the proposer spoke first are recorded |
| `no_rule_possible` | Both said no rule is possible, on consecutive turns (one saying it is recorded on its turn and the negotiation goes on) |
| `no_agreement` | The message limit was reached: **4 messages per agent** by default, 8 turns |
| `parse_failure` | A turn could not be read after its one retry |
| `aborted` | The budget guard refused a call, or the model could not be used; what was sent before is kept |

**Retry.** An unreadable reply is retried once, showing the model what it sent and the
template's retry instruction (#24). **DD76 (decision).** A turn that still cannot be read
ends the negotiation as `parse_failure`, where #24's dialogue counted it as silence and went
on: here a turn carries a proposal and an acceptance, and silence would change what the other
can accept.

**Logged** whole, as #24 logs a dialogue: every prompt, raw reply, parsed turn, proposal with
its hash, acceptance with its status, and every attempt with its tokens and cost, in
`sessions/<session_id>.json`; and the same for reading, as #24's `transcript.md`, in
`sessions/<session_id>.md`.

**Counterbalancing.** The speaking order and the persona mapping are factors of the design
(section 2) and are recorded with every session. In #24's hallway smoke runs the first
speaker gave way in 5 of 6; the report counts how often the accepted rule was proposed by the
first speaker and by the second.
*Tested:* `tests/test_rulegen_protocol.py`.

## 5. Condition B: stating a rule

One request per session, with the third-person system prompt; the reply is
`{"rule": <a rule or null>, "reason": "<one or two sentences>"}`, read with the same
tolerances and retried once. Outcomes: `stated`, `no_rule` (the model says no rule is
possible without talking), `parse_failure`, `aborted`. The temperature and every sampling
setting are recorded with each attempt (`request`).

**Repeats.** Each cell of the design is run K times (`statement.repeats`, default 3), as K
sessions `..._r1` to `..._rK`; the description order is a factor of the design.
**Stability** of a cell is the share of its repeats that gave its commonest answer, where an
answer is the canonical hash of the stated rule, or `no_rule`, or `parse_failure`; aborted
repeats are left out. 1 means every repeat gave the same rule. **DD77 (decision).**
Semantic equivalence (two rules that differ in form but not in effect) is SI-4's.
*Tested:* `tests/test_rulegen_protocol.py`.

## 6. Validation: the category of every proposal

Every rule a model proposes is validated: in condition A **every proposal of every turn**,
agreed or not; in condition B the stated rule. Each gets **exactly one category**, recorded
in `validation.jsonl` with the session, the proposer, the canonical hash, whether it was the
agreed (or stated) rule, the loader's reason, the fields it reads, and its review flags.
**Nothing is discarded.** The proposal is read by issue #28's loader (`parse_rule`) under
placeholder metadata, in the rule format its session was shown (format 2 for prompt version
1, format 3 for version 2), and by checks of its own. The order of precedence is: a person's
group (issue #32), then needs communication, then format limit, then whatever the loader
refuses first, which checks a rule's structure before its consistency (so a malformed rule
whose shares also sum below 1 is a schema error):

| Category | What puts a proposal in it |
|---|---|
| `protected_attribute` | Issue #32. It reads a person's group: its condition or its role assignment (the field, the role names, the tie policy) names the group or anything derived from it (anything containing "ethnic"), a default label, or, where the session showed groups, one of its labels or a word of its framing (`session_terms`). **No rule may read a group**; a model that tries is a finding, so the attempt is a category of its own, kept and counted, and comes first: whatever else is wrong with such a rule, this is what it is counted as (`fictional-groups.md`) |
| `needs_communication` | It reads what the two could not both see: a field the loader refuses as `unobservable_field` (an errand, one person's own position or point of view, `self.` and the like), a field whose name speaks of private information (task, urgency, destination, appointment, ...), or a field the session hides (age or gender when demographics are hidden). Such a rule could be followed only if the two talked first. **Rejected, and the format is not extended** (a decision of the issue, pending the supervisor) |
| `format_limit` | It asks for something the format cannot express, as far as can be told mechanically: more than two roles; roles given by a category (the format orders the two by a number, so "the woman goes first" cannot be written); a formula where a field or a constant belongs (a share that grows with the age gap, a threshold that scales with speed, a side "if older"); and (issue #32) what a later version of the format added than the one the session was shown: in a session of prompt version 1 (format 2), `back_up`, a passage field, or true or false as a value. "The one who has walked less far in backs out" is a format limit there, and valid in a session of prompt version 2 |
| `inconsistent` | Refused by the loader for responsibility shares summing below 1 (`reciprocity`), opposite sides (`side`), passage orders that are not one leader and one follower (`passage_order`), or (issue #32) a rule that says who backs up but does not make exactly one of two roles back up, or backs up the role that goes first (`back_up`, `rule-format.md` section 14) |
| `schema_error` | Refused by the loader for its structure: an unknown key, a wrong type or unit, a missing tie policy, roles that do not fit the directive, a field that does not exist, an intent over 500 characters |
| `valid` | It loads, and both people of the session can see everything it reads |

**What counts as a formula.** A value written as text where the format takes a constant or a
field is a formula if it depends on something: it names a field (`pair.age_difference_years`),
uses a word of dependence ("if", "when", "per", "grows", "times", ...), or does arithmetic
with a named quantity in it ("2 * speed"). Arithmetic on numbers alone ("1/2") and a number
with its unit ("0.5 m") are constants written wrongly: `schema_error`. Whether what a
`format_limit` rule wanted could have been written another way is not judged.

**Manual review.** What cannot be told mechanically is flagged, never categorised: the
proposal's `intent`, the conversation (A) or the reason (B), and any value written as text
are searched for patterns of scaling ("grows with", "in proportion"), of "the more ..., the
more ...", of a rate ("per year"), and of more than two people ("a group", "three people").
Flags are counted on their own in the report, for a person to read.

**What a model writes in the writer's keys** (`schema_version`, `rule_id`, `version`,
`status`, `provenance`, `screening`) is ignored, kept in the validation row
(`ignored_metadata`), and counted; it never reaches a rule file (section 7). **DD78
(decision)** is the precedence, the formula test and the review patterns.
*Tested:* `tests/test_rulegen_validate.py` (every category, the precedence, the formula
test, the flags; issue #32: the group, a session's words, the earlier format, backing up).

## 7. The writer, the staging databases, and promotion

**`rule_db/` stays read-only.** Generated rules are written into a **staging database** of
their experiment and condition, `runs/<experiment>/rule_db_staging/<negotiated|stated>/`
(`runs_mock/` for a mock run), laid out as the rule database is (`schema/` with every rule
schema copied in, `rules/`, `rulesets/`, `MANIFEST.json`), so that the same loader reads it
and its rules can be switched on in a run. Only `negsim.rulegen.writer` writes there, and
only ever adds: a rule version is frozen in the manifest when written.

**What is written:** a rule that is `valid` and was agreed (A) or stated (B). A valid
proposal that was not agreed is a row of `validation.jsonl`, not a rule.

**The writer fills, and only the writer fills,** a rule's metadata:

- `rule_id`: `neg_` or `st_`, the case id, and the first ten characters of the canonical hash
  (`neg_head_on_de176842_11c9d9f766`): deterministic, never the model's;
- `schema_version`: the rule format the supporting sessions were shown, 2 for prompt version 1
  and 3 for prompt version 2 (issue #32; section 3.1); `version` 1, `status` `candidate`;
- `provenance`: `source_type` (`negotiated` or `stated`), a `source_ref` naming the
  experiment and the case, `created_at`, an `author` naming the writer, the model that
  replied and the prompt template, and `generation`: the experiment, condition, case,
  canonical hash and **every supporting session** (its id, design cell, the model asked for
  and the model that replied, the prompt template and its hash, when it started, which agent
  proposed the rule, the repeat).

**Stored once.** The same canonical rule from several sessions of one case and condition is
one rule, with every session listed. The canonical form leaves out `description`, `intent`
and `priority`, so sessions that agree on what a rule does may word it differently: the
stored rule takes them from the **earliest** supporting session (by start time, then id);
every session's own proposal stays in its session log. Writing is **idempotent**: written
again with the same sessions, nothing changes; supported by more sessions later (an
experiment run in parts), the rule is stored as its next version, with the sessions added and
its screening kept. **DD79 (decision).**

**Promotion** into `rule_db/` (or another rule database) is never automatic:

```
python -m negsim.rulegen list runs/si3_pilot/rule_db_staging/negotiated
python -m negsim.rulegen promote runs/si3_pilot/rule_db_staging/negotiated <rule_id> --reason "why"
```

`promote` copies one staged version (the newest unless `--version` says) into the database
as that rule's next version, **refuses without a reason**, and records the promotion in the
rule's provenance (`promotion`: the staging database, the staged version and its SHA-256, the
reason, the time, by whom). It is frozen in the database's manifest; if the database would no
longer load, the promotion is undone. **No rule is promoted in issue #30.**
*Tested:* `tests/test_rulegen_writer.py` (ids, provenance, the model's metadata ignored, one
rule from several sessions, idempotence, versions, promotion with and without a reason).

## 8. Single-rule replay and crowd screening

Generated rules are **never switched on together** in this issue (a decision of the issue):
each is evaluated alone, with plain ORCA for every pair it does not match, so no two can
clash. Both results go into the rule's `screening` block (`rule-format.md`, section 12), as
its next version in the staging database.

**Replay** runs the rule on its case's **own run**: the case-source experiment's config is
found by name, the run rebuilt from it, and checked to be the run the case came from (its
seed, and the SHA-256 of the resolved scenario). The run is repeated with no rule beside it,
on the same seed (paired seeds, `baseline.md`, section 6), and with the same people: those of
the rule's earliest supporting session, with its visibility. **The baseline must reproduce
the case**: the case's pair must form on the same step with the same tier, pair exposure and
smallest separation as the case recorded; if not, the entry says so. Recorded: for each run,
its status, arrivals, throughput, collisions, near misses, yields, pair exposure, tiers and
how often the rule fired; for the case's pair in each, its tier, category, pair exposure,
smallest separation, and whether the rule matched it and with which roles. **A replay has no
pass mark** (`verdict: recorded`). **DD80 (decision).**

**Crowd screening** (Q10 of `WORK_LOG-28.md`) runs the rule alone in the two-way flow
(`bidirectional_flow`, 50 + 50) on the primary baseline, for `screening.repeats` seeds
(paired, from `screening.seed`), each beside the flow with no rule on the same seed. The crowd
is given the design's two ages and two genders in turn, so that a rule that reads them can
apply. Recorded per seed: deadlock, status, arrivals, collisions and throughput, against the
baseline. **A rule that gridlocks the flow fails screening**: a run that ends in deadlock, or
at its time limit with people still walking, on a seed on which the baseline did neither.
It is marked (`verdict: failed`, with the reason), never deleted. **DD81 (decision).**
The runs are deterministic and the crowd does not depend on a rule's case, so a rule whose
canonical form was screened already in the same invocation, with the same visibility, is
given those results without the flow being run again, and its entry names the rule version
whose runs they are (`same_runs_as`).

Found while testing it, in a flow of 4 + 4: a rule that stops both people when they meet
until the encounter has **passed** does not gridlock the flow (ORCA still steps a stopped
agent aside, the encounter passes, the scale ends with it, DD55), it only slows it; one that
stops them until they are **out of sight** of each other deadlocks it in 6 s. In the 50 + 50
flow (one seed), the mock's rules that give both people 15 cm more room on every meeting, or
30 cm when closer than 6 m, reached the time limit with 98 and 23 of 100 arrived (274 and 384
collision episodes), where the baseline finished in 52 s (86): so an innocuous-looking rule can fail
screening, which is the point of screening. The mock's rule that the faster person does all
the avoiding passed (all arrived in 77 s, 90 collision episodes). A screening run of the
50 + 50 flow with a rule took one and a half to four minutes.
*Tested:* `tests/test_rulegen_replay.py`.

## 9. The experiment type, the budget and the cost preview

A config with `layer: rule_generation` (`configs/rule_generation/`) is run by
`run_experiment.py`:

```
python run_experiment.py configs/rule_generation/si3_mock_rehearsal.yaml
python run_experiment.py configs/rule_generation/si3_pilot.yaml --plan
python run_experiment.py configs/rule_generation/si3_pilot.yaml --client deepseek            # preview only
python run_experiment.py configs/rule_generation/si3_pilot.yaml --client deepseek --confirm  # paid
```

| Key | What it sets |
|---|---|
| `experiment_name` | The folder, `runs/<name>/` or `runs_mock/<name>/`, and the budget scope |
| `cases` | `store` (default `cases`), `set` and/or `ids` |
| `conditions` | `[negotiated, stated]`, or one of them |
| `design` | `seed`, `factors`, optionally `per_case`, `base_age`, `age_difference`, `tasks` (section 2) |
| `negotiation` | `template` (`rulegen_negotiate_v1`), `max_messages_per_agent` (4) |
| `statement` | `template` (`rulegen_state_v1`), `repeats` (K, 3) |
| `llm` | `client` (`mock` or `deepseek`), `mock_policy`, `model`, `temperature`, `max_tokens` (the reply cap c), `thinking`, `transport_retries` |
| `budget` | `cap_usd` (on this experiment's own calls), `ledger` |
| `replay` | `enabled` |
| `screening` | `enabled`, `scenario`, `baseline`, `seed`, `repeats`, `scenario_overrides` |

It runs case selection, the design, the preview, the sessions, validation, the writer,
replay and screening, and writes the report (`report.md`, `summary.json`): the categories
by condition and scenario, the agreement rate and who proposed what was accepted, the
stability, the review flags, tokens and cost per session against the preview, the screening
verdicts, and the failure modes (retried turns, unreadable replies by reason, non-agreeing
acceptances by status, outcomes). Every call is labelled with its experiment, session,
condition, case, turn and attempt, in the session's log and in the spend ledger.

**The budget.** Calls go through issue #24's budget guard and spend ledger, with the cap on
**this experiment's own calls** (`BudgetGuard(scope=...)`): the ledger already holds what
earlier experiments spent, which would otherwise count against a pilot's cap. A scoped guard
records a call that has no experiment label under its scope and refuses one labelled for
another experiment, so that no call escapes its cap. **DD83 (decision).**

**The cost preview** is written (`preview.json`) and printed before any call. It is the
issue's bound. With, for one session, c the reply cap, and every text's tokens estimated high
as the guard does (`estimate_prompt_tokens`: 0.3 token a character, times 1.5, plus 8 a
message):

- P, the larger of the two agents' system prompts (A) or the system prompt (B);
- W, every line a turn can wrap around the other's reply, at their longest (A);
- R, the retry instruction;
- **S = P + W + c + R**, the fixed part of any attempt's prompt, with room for a failed reply
  and the retry instruction, which a retry adds;
- **m = c + W**, a previous turn as it reappears in a later prompt (A).

*Condition A.* On turn t (0, 1, ..., 2M − 1) the speaker is sent its system prompt, its own
history (each of its earlier turns: what it was shown, and its reply) and what it is shown
now. Every earlier turn's reply, the other's and its own, is in that prompt once, so the
prompt carries the t earlier turns, each at most m, and one current wrapper:

  prompt(t) ≤ S + t·m, so that, summed over the 2M turns,
  **input ≤ 2M·S + m·M(2M − 1)** and **output ≤ 2M·c** for one send of every turn.

(The bound is loose: an agent's own reply needs only c, not c + W, and the wrappers of its
own turns are counted twice.) *Condition B.* **input ≤ S, output ≤ c** per send (the issue's
"(S + m)" with m = c).

*Every send.* A turn can make up to two attempts (the retry on an unreadable reply), and the
paid client resends each up to `transport_retries` times on a server error, any of which may
be billed (the guard counts each at its worst case). So each bound is multiplied by
**1 + R_max = 2 × (1 + transport_retries)**, 6 by default (the issue's "(1 + maximum
retries)"; #24's `--plan` multiplied by the same). *Prices:* every input token at the peak
cache-miss rate and every output token at the peak output rate of
`configs/llm/deepseek_pricing.yaml`. **DD82 (decision).**

*An assumption, checked but not proved.* The bound takes a reply to be no longer in a later
prompt than when it was sent (c tokens). The protocol shows the other's message and proposal
and keeps the speaker's own reply re-serialised as JSON, which can differ from the model's
own spacing; `tests/test_rulegen_experiment.py::test_the_bound_holds_for_a_negotiation_that_uses_every_message_at_the_cap`
runs a negotiation whose every reply is as long as the cap allows and checks the bound holds,
and the pilot's report compares every session's tokens with its bound (`summary.json`,
`tokens_by_condition.largest_share_of_the_preview_used`).

**Confirmation.** With a paid client, nothing is sent unless the preview fits the cap
(otherwise the run is refused, with the preview) **and** the run is confirmed with
`--confirm`; without it the preview is written and the run stops with exit code 4. The paid
client, which needs the API key, is not even built before. Afterwards `cost.json` puts the
actual cost (from the tokens the API reported) beside the preview, session by session.

**Resuming.** Running an experiment again resumes it: a session with a record is read back,
not run again; a session that was `aborted` runs again, its first log kept beside the new
one (`<session>.aborted1.json`), and what it cost is counted; writing, replay and screening
are idempotent. Once a session has run, a folder that holds another config of the same name,
or a run with another client, is refused: give the changed config a new name. Before that
(a paid run refused over its cap, or not yet confirmed, has sent nothing) the config may
still change, its cap say. `--limit N` runs at most N sessions that have no record. Every
invocation is a line of `invocations.jsonl`. **DD84 (decision).**

**The mock** (`negsim/rulegen/mock.py`) stands in for a model; it does not imitate one. Each
design cell of a condition is given one scripted path, in turn, so that a design with 13 or
more cells per condition takes every path: in A, agreement at once, after a counter-proposal,
after an acceptance written beside a different rule, after a stale acceptance, after a reply
that needed its retry; no agreement; no rule possible; a turn unreadable twice; a proposal of
every validation category; a proposal carrying an id and a provenance of its own. In B: a
stable valid rule, a rule that changes between repeats, no rule, the retry, a reply
unreadable twice, every category, the model's own metadata. `si3_mock_rehearsal.yaml` runs
80 negotiations and 240 statements over one case of each SI-1 scenario type, with replay and
screening; nothing it produces is a finding.

**The mock of issue #32** is a second policy, `rulegen_paths_v2`: the paths above, in the same
order, then three more in each condition: a rule that reads a person's group (to exercise
`protected_attribute`), a valid rule for a meeting inside a single-file passage (the one who
has walked less far in backs out), and an inconsistent one (both back out). The in-passage rule
is `valid` in a session of prompt version 2 and `format_limit` in one of version 1, whose rule
format had neither `back_up` nor the passage fields (section 6). It takes every path in a
design with 16 or more cells per condition. `rulegen_paths` is left as it was, so that an
experiment that names it takes the paths it took.
*Tested:* `tests/test_rulegen_experiment.py` (the config, the preview's arithmetic, a paid
client unconfirmed and over the cap, the budget guard stopping an experiment and a resume
after it, a partial run, the whole experiment on the mock with every path and category,
replay and screening, resuming, the command line); `tests/test_rulegen_groups.py` (prompt
version 2 with `rulegen_paths_v2`: every new path, its category, rules written in format 3).

## 10. The paid pilot (Part 11): held

**Not run.** The issue makes the supervisor's approval of simulation work, recorded in
`CLAUDE.md`, a hard stop for anything that spends money (`WORK_LOG-30.md`, P1); it is not
recorded, and the user chose to build and rehearse everything on the mock and hold the pilot.
The pricing check that must precede any paid call is not done either (`pricing-check.md`).

**The design**, as the issue specifies it (`configs/rule_generation/si3_pilot.yaml`): two
cases, one `wide_corridor_head_on` (`head_on_de176842`) and one `overtaking`
(`overtaking_2d08db11`); condition A with both speaking orders; condition B with both
description orders at K = 2; demographics shown in the head-on case and hidden in the
overtaking one; one persona pair (the older person a woman with the urgent errand). 4
negotiations and 8 statements.

**Its worst-case preview does not fit the cap**: USD 0.619 against USD 0.05 (A USD 0.532,
B USD 0.087), and the code refuses to send anything with it. Condition A dominates: its
bound grows with the square of the messages, and one negotiation alone can cost up to
USD 0.13 (S ≈ 4,200 tokens with the 1.5 safety factor; at M = 4, 2M·S + m·M(2M − 1) ≈ 55,000
input tokens a send, times 6 sends). The issue says to shrink the design until the preview
fits, and to report what was cut. The previews:

| Change | Negotiations, statements | Worst case, USD |
|---|---|---|
| None (as issued: M = 4, c = 600, 2 transport retries) | 4, 8 | 0.619 |
| No transport retries | 4, 8 | 0.206 |
| No transport retries, c = 400 | 4, 8 | 0.169 |
| No transport retries, c = 400, M = 2 | 4, 8 | 0.086 |
| No transport retries, c = 400, M = 3, one order per case | 2, 4 | 0.062 |
| No transport retries, c = 400, M = 2, one order per case | 2, 4 | **0.043** |

Only the last fits USD 0.05, and it halves both the negotiation and the design (each case
gets one speaking order, so order and case are confounded). For scale: #24's 37 paid calls
had no transport error, and their replies were at most 46 tokens; the pilot's realistic cost
is a fraction of its worst case, since replies are shorter than the cap, few turns need a
retry, and part of each prompt is usually served from the provider's cache at a fiftieth of
the price (30% of #24's prompt tokens were). Measuring that fraction for this protocol is
what the pilot is for. **Which cut to make, or whether to raise the
pilot's cap instead, is open question Q5 of `WORK_LOG-30.md`**; this project's
recommendation there is to keep the issue's design and protocol, drop the transport
retries, cap replies at 400 tokens, and raise the pilot's cap to USD 0.17, because the
pilot's purpose is to measure tokens per session *for SI-3b's design*, which M = 2 would not.

**What the pilot reports** (`summary.json`, `report.md`): the validation counts by
condition and scenario; the agreement rate and the proposer of every accepted rule (A); the
stability (B); the tokens of every session against its preview; the total spend; the
failure modes; and the replay and screening of every valid rule. A rule's quality in so small
a sample is not a finding: the point is that the loop runs end to end with the real model.

## 11. What is logged

`log-schema.md`, "Rule-generation experiments", lists every file of an experiment folder:
the config and every invocation, the cases and the session list, the preview, one file per
session (every prompt, raw reply, parsed turn, proposal, acceptance, attempt, token count and
cost), `validation.jsonl`, `written.jsonl`, `screening.jsonl`, the staging databases, the
replay and screening runs (avoidance runs, log schema version 4), `cost.json`,
`summary.json` and `report.md`.

## 12. What is not here

- The full paid collection, and the comparison of conditions A and B (SI-3b).
- Rule sets of generated rules, semantic equivalence, Q3, rules inferred from behaviour (SI-4).
- Live negotiation during a run, and evaluation on unseen scenarios (SI-5).
- Validation against evidence about people (SI-6).
- Matching cost (Q11), performance towards 10,000 agents, Singapore parameters.
- A rule format that reads private information.
