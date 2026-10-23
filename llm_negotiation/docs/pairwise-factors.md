# Pairwise perception factors (issue #61, RF-6)

A **pairwise** factor is how one person sees another. It belongs to a pair of people, not to one
person, and it need not be mutual. The supervisor suggested attractiveness as a factor,
"represented in a matrix" (meeting of 2026-10-20, `CLAUDE.md`). A score per person could not say
"men yield to women they find attractive", because that depends on who is looking at whom. So
this issue adds two pairwise factors to the Step 1 design of track #55, on the mock only:

| Factor | Levels (base first) | Mutual | Design factors |
| --- | --- | --- | --- |
| `perceived_attractiveness` | `unremarkable`, `attractive` | no: a matrix | `attractiveness_0_sees_1`, `attractiveness_1_sees_0` |
| `familiarity` | `strangers`, `acquaintances` | yes | `familiarity` |

Code: `negsim/resolution/pairwise.py`. Wording: the frozen template `resolve_pairwise_v1`
(kind `resolution_pairwise`). Tests: `tests/test_pairwise.py`. Rehearsal:
`configs/resolution/resolve_pairwise_mock_rehearsal.yaml`.

**Ethics sign-off from the supervisor for perceived attractiveness: pending unless recorded
otherwise** (`CLAUDE.md`, "Pending sign-offs", item 2). Attractiveness is off by default, and no
paid run may switch it on until the sign-off is recorded (section 6). Until then, RF-10 (#65)
drops both attractiveness factors.

## 1. What each person is told

An observer is told, of a person it can see, **its own** perception of them, in WHO YOU CAN SEE,
under that person's label (`docs/resolution.md`, D2):

```
WHO YOU CAN SEE
- Person 1, 0.8 m away, straight ahead of you.
  They are walking at 1.30 m/s, in the opposite direction to you, and the distance between you is shrinking.
  Their body is 0.50 m wide.
  They look about 25 years old.
  They look like a man.
  You find them attractive.
  You know each other from your classes.
```

(From the mock rehearsal, `T_passage_36a66c39_59fa2eed_r1`, person 1's first view. Person 2,
in the same session, is told "You do not find them especially attractive." of person 1.)

| Level | Line (`resolve_pairwise_v1`, issue #61's words) |
| --- | --- |
| `attractive` | You find them attractive. |
| `unremarkable` | You do not find them especially attractive. |
| `acquaintances` | You know each other from your classes. |
| `strangers` | You have never seen them before. |

- **Only the observer's own row.** Person 2 is never told how person 1 sees them, and the
  other way round. The lines are built per observer (`PairwiseFactors.lines_for`) and placed in
  that observer's view only.
- **Only while the person is in view** (RF-17): within 75° of straight ahead, within 10 m, and
  not hidden. A person behind, outside the cone, or only heard gets no line.
- **Only in full detail, within 5 m.** The core template `resolve_v2` prints a person's extra
  lines (RF-5's observable factor lines and these) only in full detail; from 5 to 10 m it prints
  one short line per person (D2). The pairwise lines follow D2 as it stands. **The
  consequence in round 1 is serious.** In the head-on case (`head_on_02dfbadb`) every decision
  point of the rehearsals of RF-5 and of this issue was 5.0 to 9.8 m away (the first at 9.8 m,
  at the edge of the seeing range). There no pairwise line, and no RF-5 observable line, ever
  reaches an agent; the independent condition has only that one decision point. In the passage
  and overtaking cases they do reach the agent (`tests/test_pairwise.py`, the head-on test, pins
  this). A `resolve_v3` that prints these lines on the short line too would change it; that is a
  new core template and a decision for the user (`WORK_LOG-61.md`, open question 1). The
  outcome row says how often a line was actually shown (section 5), so the analysis can tell "not
  told" from "told, and no effect".
- **With a switch on, both levels have a line**, so that "not attractive" is said as plainly as
  "attractive"; RF-5's base levels say nothing. **With it off, neither has**: the factor is in
  the design and the record, but the observer is told nothing about it.
- The lines go after RF-5's observable factor lines, attractiveness before familiarity.

## 2. Only in the prompt

Neither factor changes anything in the simulator: no speed, no clearance, no body. A factor's
effect is an effect on the decision only. "You find them attractive" is a feeling the agent is
told it has. No appearance is described, so the factor tests whether being told this changes the
plan. It cannot show how a model judges anyone's looks, and it says nothing about real
attractiveness.

## 3. The block

A session's `pairwise` block, in issue #61's format (`design.jsonl`, the session record):

```yaml
pairwise:
  agents: [1, 0]              # which agent each row (and column) is
  perceived_attractiveness:   # row = who is looking, column = who is seen
    - [null, attractive]      # the agent of row 0 finds the agent of row 1 attractive
    - [unremarkable, null]    # the agent of row 1 does not find the agent of row 0 attractive
  familiarity: strangers      # symmetric: the same for everyone in the block
```

- **`agents`** names the agent of each row. Without it the rows are agents 0, 1, ... by id, so
  issue #61's block loads as written ("agent 0 finds agent 1 attractive"). A design's session
  always lists person 1 first and person 2 second. Under `mapping: p1_higher` person 1 is the
  case's agent 1, so the block says `agents: [1, 0]`.
- **The diagonal is `null`**: nobody is seen by themselves. A `null` off the diagonal was not
  designed: no line, and no value in the outcome row.
- **Familiarity is one value** for the block. For two people that is the pair's. A crowd
  version would need a symmetric matrix (section 8).
- `PairwiseFactors.from_block` refuses a matrix that is not square with one row per agent, a
  diagonal that is not `null`, a level that is not one of the factor's two, repeated agents, and
  any other key.

**Rows are the design's persons, not the case's agents** (a choice of this issue, recorded in
`WORK_LOG-61.md`). Every other person factor is coded by slot (person 1 has the other level), and
only `mapping` ties a slot to the case geometry. Indexing by agent id instead would tie a
perception to which end of the corridor someone starts at.

## 4. The design

| Factor | Levels | What it sets |
| --- | --- | --- |
| `attractiveness_0_sees_1` | `unremarkable`, `attractive` | row 0, column 1: how person 1 sees person 2 |
| `attractiveness_1_sees_0` | `unremarkable`, `attractive` | row 1, column 0: how person 2 sees person 1 |
| `familiarity` | `strangers`, `acquaintances` | the same for both |
| `attractiveness_visible` | `true`, `false` | whether either is told its attractiveness line (`true` when left out) |
| `familiarity_visible` | `true`, `false` | whether either is told the familiarity line (`true` when left out) |

- All five are optional. A config that names none of them gives the same cells, session ids,
  session records and outcome columns as before (tested on both earlier rehearsal configs).
- A switch needs its factor: `attractiveness_visible` without an attractiveness factor is
  refused, and so is `familiarity_visible` without `familiarity`.
- A design may set one direction only. The other row is then `null` and its person is told
  nothing about attractiveness.
- Crossing the two directions gives the four cases "neither", "person 1 only", "person 2 only"
  and "both". With `gender_pair` crossed, this can express the supervisor's example.
- `templates.pairwise` (default `resolve_pairwise_v1`) is only for a design that names one.
- **For RF-7:** these are five more two-level design factors (three factors and two switches),
  beside RF-5's 14 named factors, their switches and `mapping`.

## 5. What is logged

- **`design.jsonl`** and a session record's `session`: the `pairwise` block, and the switches in
  `visibility` (`perceived_attractiveness`, `familiarity`), only for a factor the design varies.
- **The session record:** `pairwise` (the block, `visible`, and the template with its SHA-256)
  and `templates.pairwise`. Every view keeps each seen person's `pairwise_lines`.
- **`config.json`:** `templates.pairwise`, and `pairwise.template` with its SHA-256.
- **The outcome row** (`outcomes.jsonl`, `outcomes.csv`), per person, from that person's own
  point of view, for RF-8:

| Column | Value |
| --- | --- |
| `p1_finds_other_attractive`, `p2_...` | 1 if this person finds the other attractive, 0 if not, empty if not designed. As designed, whether or not the person was told: the switch is the cell's `attractiveness_visible` |
| `p1_knows_other`, `p2_...` | 1 for `acquaintances`, 0 for `strangers` (the same for both) |
| `p1_pairwise_lines_shown`, `p2_...` | at how many of this person's decision points it was shown a pairwise line about the other (in full detail, section 1) |

  The cell's own columns (`attractiveness_0_sees_1`, ... as levels) are in the row as well.
- **The transcript** (`sessions/<id>.md`) has a line `- Pairwise: {...}` with the block.

## 6. The ethics gate

Perceived attractiveness is **off by default**: it is on only when a design names
`attractiveness_0_sees_1` or `attractiveness_1_sees_0`, whatever the levels and the switch. **No
paid run may switch it on** until the user records the supervisor's ethics sign-off in
`CLAUDE.md`, in this sentence with the date filled in:

> Ethics sign-off for the perceived-attractiveness factor (issue #61): approved by the supervisor on YYYY-MM-DD

The resolution experiment refuses such a paid run before anything is sent: no session, no
ledger line, and `refused_no_sign_off` in `invocations.jsonl`. `--plan` says so. The check is the
fictional group's (`docs/fictional-groups.md`, section 6), shared in `negsim/ethics.py`, with a
sentence of its own; one sign-off never stands for the other. **A mock run needs none**, so that
the pipeline can be rehearsed. **Familiarity is not gated.** Only the user may add the sentence,
once the supervisor has approved. Nothing in this issue does, and the repository records no
sign-off (tested).

## 7. Rules: kept out of the rule database only

**Until the supervisor decides, no rule may read perceived attractiveness.** The rule loader
refuses, as `protected_attribute` and before every other check, a rule whose condition or roles
(the field, the role names and the tie policy) contain `attract` (`attractive`,
`attractiveness`, `attraction`), `beaut`, `handsome` or `pretty`, or "good looking" however it
is joined (`negsim/rules/fields.py`, `ATTRACTIVENESS_PATTERN`; `rule-format.md`, section 14). In
rule generation such a rule is **kept and counted** in the category `protected_attribute`, and
never written as a rule: a model trying to condition a rule on attractiveness is a finding, not
an error to hide.

**This keeps attractiveness out of the rule database only.** It stays in the design, in the
outcome rows (section 5), in RF-8's factor analysis, and in the factor-to-decision mapping. That
mapping is what the supervisor asked for: which factors drive the decision. Whether an extracted
rule may later read it is the supervisor's decision.

**Familiarity is not protected.** A rule naming it is `unknown_field` (`schema_error`) because no
perception record holds it, like RF-5's observable factors (`WORK_LOG-60.md`, open question 5).
Whether it becomes a rule field is for RF-11 and RF-12.

## 8. A crowd of 10,000 (documented, not built)

A full matrix for 10,000 agents has 10,000 × 10,000 = 100 million entries, 99,990,000 of them off
the diagonal. Nearly all are never used: a pairwise line is told only of someone in view, within
10 m. **A crowd version would store an entry only for pairs within sensing range**, as a sparse
map from (observer, seen) to a level:

- **Created when needed.** An entry is drawn when a pair first comes within the seeing range,
  from a seeded rule (a fixed share of `attractive`, say, or a model of who finds whom
  attractive). It is then kept for the run, so the same observer sees the same person the same
  way every time.
- **How many.** A rough count, from this project's numbers, not a measurement. The view cone is
  150° and 10 m, an area of (150/360) × π × 10² ≈ 131 m². At a density of 1 person/m², each
  agent has about 131 people in view, so about 1.3 million directed entries for 10,000 agents,
  1.3% of the full matrix. Within the 5 m detail range, the area is ≈ 33 m², about 0.33 million
  entries.
- **Familiarity** would need a symmetric sparse matrix (one entry per unordered pair), or groups
  of acquaintances drawn at the start.
- **When it matters.** The LLM is used only in conflicts set up on purpose or mined from crowd
  runs (D9), and the crowd simulation runs ORCA and the extracted rules, which may not read
  attractiveness (section 7). So the crowd needs pairwise values only to prompt a mined conflict
  with them, or for a rule the supervisor later allows to read them.

## 9. What these factors cannot show, and the open points

- **Prompt only** (section 2): no appearance is described, and nothing physical changes.
- **The 5 m limit** (section 1): in head-on encounters the lines never reach the agent under
  `resolve_v2`.
- **"From your classes"** is the issue's wording. It presumes a shared class, which may read
  oddly with an age gap of 45 years (`age_pair: p1_older`). A `resolve_pairwise_v2` could say
  "You know each other." instead.
- **The supervisor's example** ("men yield to women they find attractive") needs `gender_pair`
  crossed with the attractiveness factors, and the outcome measured in the replay (who passed
  first), not asked: no reply field asks who goes first (D1).
