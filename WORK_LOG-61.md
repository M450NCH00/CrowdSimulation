# Work Log — Issue #61: RF-6: pairwise perception factors (perceived attractiveness, familiarity), shown only to the observer

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/61
**Branch:** feat/61-pairwise-perception-factors (cut from `feat/60-core-factors-visibility-situational`, which PR #87 merged into `feat/58-step1-encounter-protocol`; track #55's branches stack, see the memory note on `git checkout main`)
**Started:** 2026-10-23

## Understanding the issue

The supervisor suggested attractiveness as a factor, "represented in a matrix". Attractiveness is
not a property of one person: it is how one person sees another, and it need not be mutual. So
this issue adds **pairwise** factors, one value per (who looks, who is seen), on the mock only:

- **Perceived attractiveness**, a matrix: row = who is looking, column = who is seen, levels
  `unremarkable` and `attractive`, diagonal empty.
- **Familiarity**, symmetric: `strangers` or `acquaintances`.
- **Where the lines go** (D2): under the seen person's label in WHO YOU CAN SEE, in the
  observer's own view only, and only while that person is in view. Nobody is told what someone
  else perceives, and nothing is said of a person who is only heard.
- **Switches** `attractiveness_visible`, `familiarity_visible`: off means no line at all, for
  either level (on, *both* levels have a line: "You do not find them especially attractive." is
  said too, unlike RF-5's base levels, which say nothing).
- **Design factors** `attractiveness_0_sees_1`, `attractiveness_1_sees_0`, `familiarity`.
- **Outcome rows**: each person's own perception as 0 or 1, for RF-8.
- **Ethics gate**: attractiveness off by default; a paid run with it on is refused unless
  `CLAUDE.md` records the supervisor's sign-off, reusing the fictional-group gate.
- **Validation**: a rule that reads perceived attractiveness is `protected_attribute` (kept,
  counted, never written). It stays in RF-8's analysis and the factor-to-decision mapping.
- **Docs only**: a full matrix for 10,000 agents is 10^8 entries; a crowd version would keep
  only neighbours within sensing range.

**What I found before planning.**

1. **Most of the plumbing exists.** RF-2 gave `SeenPerson` a `pairwise_lines` slot ("for this
   observer only (RF-6)"), RF-17's `Perceiver.look` and `view_in` take `pairwise_lines` by agent
   id and attach them only to people in view, and `resolve_v2` prints them after the factor
   lines, verbatim. So no core template changes: the lines go into a **new frozen template of
   their own**, as RF-5's did (`resolve_pairwise_v1`, kind `resolution_pairwise`).
2. **"The session config".** A resolution experiment has no per-session config: sessions come
   from the design. I read task 1's block as the *session's* pairwise block: written with each
   session (`design.jsonl`, the session record) in the issue's format, and loadable from it. The
   design's sessions add `agents` (which case agent each row is), because person 1 is agent 1
   under `mapping: p1_higher`. Without `agents`, rows are agents 0, 1, ... by id, so the issue's
   block loads as written ("agent 0 finds agent 1 attractive"). *An interpretation, recorded.*
3. **Rows are the design's persons.** `attractiveness_0_sees_1` is row 0 looking at column 1:
   person 1 looking at person 2. Every other person factor is by slot (person 1 has the other
   level) and only `mapping` ties a slot to the case geometry; indexing by case agent instead
   would tie the perception to which end of the corridor someone starts at. *My choice,
   recorded.*
4. **Only in full detail, as RF-5.** `resolve_v2` prints a person's extra lines only within the
   detail range (5 m, D2); from 5 to 10 m it prints one short line. Changing that needs a new core
   template. **Consequence, found in RF-5's rehearsal records:** in the head-on case
   (`head_on_02dfbadb`, round 1), every decision point fired 5.0 to 9.8 m away (the first at
   9.8 m, at the edge of the seeing range), so *no* RF-5 observable line and no RF-6 line would
   ever reach an agent there. The independent condition has only that one decision point. In the
   passage (0.6 m) and overtaking (4.0 m) cases they do. Flagged below for the user.
5. **The gate.** `negsim.rulegen.experiment` checks one exact sentence in `CLAUDE.md`. The
   resolution experiment has no gate yet (the group is never on there). I move the check to a
   small shared module and add a second sentence for attractiveness.
6. **Protected words.** The rule loader's protected check reads a stem (`ethnic`) and whole
   words. I add stems for attractiveness (`attract` and a few synonyms). The refusal message has
   to name what was read (today it always says "a person's group").

## Plan

1. **Template** `resolve_pairwise_v1.yaml` (kind `resolution_pairwise`), frozen: one line per
   factor and level, the issue's wording.
2. **`negsim/resolution/pairwise.py`:** the factors and levels, the template loader,
   `PairwiseFactors` (load the block, check it, the lines one observer is told of each other
   person, the 0/1 values, `as_dict`).
3. **Protocol and view:** `EncounterSession(pairwise=...)` passes the observer's own lines into
   its views; nothing else changes.
4. **Design:** the three factors and two switches (switch only with its factor); the session's
   `pairwise` block; the switches in `visibility`. A config with none of them: same cells, ids
   and records as before. `uses_factors` keeps meaning RF-5's factors.
5. **Experiment:** `templates.pairwise`; the record's `pairwise`; numeric outcome columns; the
   cost preview counts the longest pairwise lines; the ethics gate (`refused_no_sign_off`) in
   `run_resolution` and a note in `--plan`.
6. **Validation (task 7):** perceived attractiveness protected in the rule loader and the
   rule-generation check, with its own message.
7. **Tests** (task 9) and a mock rehearsal config.
8. **Docs:** a new `docs/pairwise-factors.md` (the block, rendering, switches, design, columns,
   the gate's exact sentence, rules, 10,000 agents), and `resolution.md`, `log-schema.md`,
   `encounter-protocol.md`, `rule-format.md`, the READMEs, and a pointer in `CLAUDE.md`'s
   pending sign-offs to the sentence's exact form (not the sign-off itself).

## Progress log

### 2026-10-23 — Start
- What I did: read #61, `resolution.md` (D2), the persona schema, `fictional-groups.md` (the
  gate), `rulegen/validate.py`, the rule loader's protected check and its tests, RF-5's factors
  module, template, design, experiment and work log, and the view, perceive, prompt and protocol
  modules. Checked the trigger distances in RF-5's rehearsal records (`runs_mock/`, not tracked).
- Result / what I found: the six points under "What I found before planning".
- Next step: the template and the pairwise module.

### 2026-10-23 — The gate, the template, the pairwise module
- What I did: moved the sign-off check to `negsim/ethics.py` (the file, both sentences,
  `recorded`); `rulegen.experiment.ethnicity_signed_off` still reads its own module's
  `SIGN_OFF_FILE`, so issue #32's tests patch it as before. Wrote and froze
  `resolve_pairwise_v1` (kind `resolution_pairwise`, registered in `prompts.TEMPLATE_KINDS`),
  with the issue's four lines word for word. Wrote `negsim/resolution/pairwise.py`:
  `PairwiseTemplate`, `PairwiseFactors` (load the block, check it, `lines_for` one observer,
  `values` as 0/1, `as_dict`), and `block_for` (a design cell's block).
- Why: plan steps 1, 2 and the gate of step 5.
- Result / what I found: nothing unexpected. A `null` off the diagonal means "not designed", so
  a design may set one direction only.

### 2026-10-23 — Wiring: protocol, design, experiment, transcript
- What I did: `EncounterSession(pairwise=...)` adds `pairwise_lines` (the agent's own) to each
  of its views; RF-17's `Perceiver.look` already attaches them only to people in view. The design
  gains the three factors and two switches, before `mapping` in `ALL_FACTORS`; a switch needs its
  factor; `uses_factors` now means RF-5's factors only (it was "anything not of #58", which
  would have pulled in RF-5's template and values for a pairwise-only design); new
  `uses_pairwise`, `uses_attractiveness`, `Session.persons`, `Session.pairwise`. The experiment:
  `templates.pairwise`, the record's `pairwise`, `config.json`'s `pairwise`, the cost preview,
  the outcome columns, the gate in `run_resolution` (before the cap check, as #32's) and a line
  in `--plan`. The transcript prints the block.
- Why: plan steps 3 to 5.
- Result / what I found: **one column I added beyond the issue:** `p1_pairwise_lines_shown`, the
  number of the person's decision points at which a pairwise line about the other was actually
  printed. Because of point 4 (the 5 m detail range), the designed value alone would let RF-8
  read "no effect" where the agent was simply never told. It counts only full-detail entries,
  since a view keeps a short-detail person's lines as data although `resolve_v2` does not print
  them. *My addition, recorded.*

### 2026-10-23 — Task 7: the rule check
- What I did: `negsim/rules/fields.py` gains `PERCEIVED_ATTRACTIVENESS` in `PROTECTED` (not in
  the persona table: it belongs to a pair, and `test_protected_attribute` pins
  `NOT_RULE_REFERENCEABLE == {"ethnic_group"}`), `ATTRACTIVENESS_PATTERN` (`attract`, `beaut`,
  `handsome`, `pretty`, "good looking" however joined), `PROTECTED_NAMES` and
  `protected_attribute_of`. The three refusal messages (loader `resolve`, `parse_rule`,
  `validate_proposal`) now name what was read; the group's wording is unchanged, word for word.
- Why: task 7.
- Result / what I found: before adding the stems I searched `rule_db/`, `negsim/`, `configs/`
  and `cases/` for them: only the new template matched, so no seed rule or case is affected.
  *Synonyms are my choice*: the issue says "a rule that reads perceived attractiveness"; a model
  might write "good_looking" or "pretty" instead. Flagged below in case the list is too broad.

### 2026-10-23 — Tests and the rehearsal
- What I did: `tests/test_pairwise.py` (52 tests); `configs/resolution/resolve_pairwise_mock_rehearsal.yaml`
  (24 sessions: an asymmetric matrix, attractiveness shown and hidden, familiarity crossed,
  `mapping: p1_higher`; head-on, passage, overtaking; independent and talk). Ran it: 24 of 24
  completed.
- Result / what I found:
  - **Two of my first tests were wrong.** One compared a tuple from an in-memory record with a
    list (RF-5's log notes the same trap). The other had the person behind in the overtaking
    case speak at 4.0 m, outside the 3.2 m hearing range, so the person ahead was never prompted
    and the test would have passed vacuously; it now closes in first, and the test asserts that
    the person ahead *is* prompted, with nobody in view and one voice heard.
  - Also wrong at first: a one-row matrix without `agents` is refused for having one agent,
    before the shape check. That is correct behaviour; the test case now gives two agents.
  - **By eye** (`T_passage_36a66c39_59fa2eed_r1`, person 1 = agent 1): agent 1 is told "You
    find them attractive." and agent 0 "You do not find them especially attractive.", each after
    the age and gender lines, both "You know each other from your classes."; neither sees the
    other's line. The transcript shows the block with `agents: [1, 0]`.
  - **The outcome rows** (all 24): `p1_finds_other_attractive` 1 and `p2_...` 0 everywhere;
    `p*_knows_other` follows the cell. Lines shown: passage 1 and 1 (familiarity still shown
    with attractiveness switched off); overtaking 0 for the person ahead (never prompted) and 1
    for the one behind; **head-on 0 and 0 in all eight sessions**, independent and talk, which
    confirms point 4.
- Next step: docs, full suite.

### 2026-10-23 — Docs
- What I did: a new `docs/pairwise-factors.md` (the lines and who is told them, prompt only,
  the block, the design, what is logged, the gate's exact sentence, rules, a crowd of 10,000, the
  open points). Updated `resolution.md` (built so far, D2 as built, the constraints),
  `log-schema.md` (`config.json`, `refused_no_sign_off`, `design.jsonl`, the record's
  `pairwise`, the change log; no version change), `encounter-protocol.md` (outcome columns,
  section 9), `rule-format.md` (sections 5 and 14), `rule-generation.md` (the category),
  `fictional-groups.md` (the shared check), both READMEs, and one pointer sentence in
  `CLAUDE.md`'s "Pending sign-offs" to where the sentence's exact form is documented. Item 2
  there stays **PENDING**; nothing records a sign-off.
- The crowd note's numbers are my arithmetic, labelled as such in the doc: the 150°, 10 m cone
  is about 131 m², so at 1 person/m² about 131 people per agent and about 1.3 million directed
  entries for 10,000 agents (1.3% of the 100 million); within 5 m, about 0.33 million.

### 2026-10-23 — The user's decision: resolve_v3 (open question 1)
- **Decision (the user, 2026-10-23, after reading PR #88):** "Ok let's go with your fix of
  resolve_v3", the fix proposed in open question 1. The core template prints a person's factor
  lines (RF-5's observable ones, RF-6's pairwise ones) on the short line too, 5 to 10 m away.
- What I did:
  - **`resolve_v3`**: `resolve_v2` word for word plus one key, `seen_short_extra` (`"  {line}"`,
    as `seen_extra`). Frozen. Its system message is v2's (and v1's) byte for byte, and a view
    without factor lines renders exactly as under v2 (tested at 3 m, 8 m, 8 m off to the side,
    and behind).
  - **The renderer** prints the factor and pairwise lines after a short line only when the
    template has the key, so v1 and v2 render as before. `CoreTemplate.prints_extra_lines(detail)`
    says which template prints what.
  - **The default** (`prompt.default_core`): `resolve_v3` for a design that varies an RF-5 or
    RF-6 factor, `resolve_v2` otherwise, in the experiment layer and in the protocol. A config
    that names a core template keeps it. *Why not v3 for everything:* a design without factors
    would then record another template hash, and an older run folder would refuse to resume. RF-5's
    committed rehearsal names `resolve_v2`, so it is unchanged; `--plan` now warns that its lines
    for others reach an agent only within 5 m.
  - **`p1_pairwise_lines_shown`** asks the session's core template whether a short-line entry
    was printed, instead of counting full detail only.
  - **The rehearsal** now names `resolve_v3`, and person 1 also walks with a cane
    (`mobility_aid: p1`), so that the fix shows for an RF-5 line too.
- Result / what I found:
  - **An RF-5 bug, found by the rehearsal**: "person 1: urgency is one of ['routine', 'urgent'],
    got None". With `task: none` each persona has `urgency: None`, and `Session.factor_levels`
    passed it to `SessionFactors`, which refused every session. So any RF-5 design with no errand
    could not run; RF-5's own tests all used `task: p1_urgent`. Fixed: a person with no errand
    has no urgency level. Tested.
  - **The rehearsal on `resolve_v3`** (24 of 24 completed): in the head-on case every decision
    point now shows its pairwise lines (1 of 1 in the independent condition, 3 of 3 or 2 of 2 in
    talk), all on short lines at 9.8 m and closer. By eye, person 2's view at 9.8 m: "- Person 1,
    9.8 m away, straight ahead of you: walking in the opposite direction to you." then "They are
    walking with a cane." and "You know each other from your classes." (attractiveness switched
    off in that cell); person 1's view has the familiarity line only (person 2 has no cane).
    Passage and overtaking as before.
  - The test that pinned the limit now runs both templates: lines at every decision point under
    v3, none under an explicitly named v2.
- **What `resolve_v3` does not change:** age, gender and body width stay full-detail lines (D2).
  So at 8 m an agent can be told "You find them attractive." without being told the person's
  gender. Open question 7.

## Open questions / risks

1. ~~**Lines only within 5 m (point 4 above).**~~ **Decided by the user (2026-10-23):
   `resolve_v3`**, built (above). What follows is the question as it was asked. In round 1's head-on case no RF-5 observable line
   and no RF-6 line reaches an agent, because every decision point there is beyond the detail
   range. A `resolve_v3` that prints these lines on the short line too (5 to 10 m) would fix it
   for both issues; it is a new core template, so it is for the user to decide, and D2 would
   need a note. Confirmed by this issue's rehearsal: no line was shown in any of the eight
   head-on sessions. Until then, `p1_pairwise_lines_shown` lets RF-8 tell "not told" apart from
   "told, no effect".
2. **The ethics sign-off for perceived attractiveness** is still pending (`CLAUDE.md`, item 2).
   The gate counts attractiveness as on whenever a design *names* one of its factors, even with
   the switch off or only the `unremarkable` level. That is stricter than needed (with the switch
   off nothing reaches the model), on purpose: an ethics gate should not depend on a reading of
   the levels.
3. **The protected words** (`attract`, `beaut`, `handsome`, `pretty`, "good looking") are my
   choice. They match nothing in the repository today. If one ever blocks a legitimate rule (a
   role named `pretty_close`, say), the list is in one place (`fields.ATTRACTIVENESS_PATTERN`).
4. **"You know each other from your classes."** (the issue's wording) presumes a shared class,
   which may read oddly with `age_pair: p1_older` (25 and 70). A `resolve_pairwise_v2` could say
   "You know each other." `pairwise-factors.md`, section 9, says so.
5. **Familiarity is not a rule field**: a rule naming it is `unknown_field` (`schema_error`), as
   for RF-5's observable factors. Both people know it, so it could become a pair field; that is
   for RF-11 and RF-12.
6. **Counting for RF-7:** five more two-level design factors (three, and two switches).
7. **Factor lines from 10 m, demographics only within 5 m** (`resolve_v3`). The short line still
   gives no age, gender or body width. If the supervisor's example ("men yield to women they
   find attractive") is to be tested in the head-on case, the agent at 8 m is told whom it finds
   attractive but not their gender. A `resolve_v4` could put age and gender on the short line
   too. That changes what `demographics_visible` means beyond 5 m, so it is for the user.
8. **Printing the factor lines from 10 m is a prompt choice, not a sourced range.** No source here
   says at what distance a cane, a phone or a familiar face is recognised. `pairwise-factors.md`,
   section 1, and `parameters.md`, section 8.7, say so.

## Summary (fill in at the end)

**What changed.**
- **Two pairwise factors.** Perceived attractiveness is a matrix (row = who is looking, column
  = who is seen) and need not be mutual. Familiarity is the same for both. They live in a
  session's `pairwise` block, in issue #61's format plus `agents`
  (`negsim/resolution/pairwise.py`).
- **Who is told what.** Each observer is told only its own row, under the person it sees, in
  WHO YOU CAN SEE, from a new frozen template (`resolve_pairwise_v1`). Only people in view get
  a line, and `resolve_v2` prints it in full detail only. Nobody is told how another sees them,
  and nothing is said of a person who is only heard.
- **Switches.** `attractiveness_visible` and `familiarity_visible`: on, either level has a line;
  off, neither.
- **Design factors.** `attractiveness_0_sees_1`, `attractiveness_1_sees_0`, `familiarity`, two
  levels each; 0 is person 1. A config that names none of them writes exactly what it wrote
  before.
- **Outcome rows.** Each person's own view as 0 or 1 (`p1_finds_other_attractive`,
  `p1_knows_other`), and how often a line was actually shown (`p1_pairwise_lines_shown`).
- **The ethics gate.** A paid run that varies perceived attractiveness is refused
  (`refused_no_sign_off`) until `CLAUDE.md` records the supervisor's sign-off in one exact
  sentence. The check is the fictional group's, now shared in `negsim/ethics.py`. A mock run
  needs none.
- **Rules.** A rule that reads perceived attractiveness is `protected_attribute`: refused by the
  loader, and kept and counted by rule generation. It stays in the outcome rows for RF-8.
- **Docs.** A new `docs/pairwise-factors.md` (with the 10,000-agent note, task 8) and updates to
  seven other docs, both READMEs, and a pointer in `CLAUDE.md`.
- **After the user's decision (2026-10-23): `resolve_v3`.**
  - It prints a person's factor lines (RF-5's observable ones, RF-6's pairwise ones) under the
    short line too, from 10 m.
  - It is the default core template of a design that varies an RF-5 or RF-6 factor; a design
    without factors keeps `resolve_v2`, and `--plan` warns when a factor design names `resolve_v2`.
  - D2 is amended to match, in `resolution.md` and `architecture.md`.
- **An RF-5 bug fixed on the way:** a design with `task: none` and any core factor refused every
  session.

**Why.** Issue #61; the supervisor's suggestion of attractiveness "represented in a matrix"
(2026-10-20); `docs/resolution.md`, D2.

**How it was verified.**
- 52 new tests in `tests/test_pairwise.py`, covering every test the issue lists:
  - an asymmetric matrix in each view;
  - neither agent sees the other's perception (unit and protocol level);
  - nothing for a person behind, outside the cone, beyond 5 m, or only heard;
  - the gate refuses a paid run, and lets it through once the sentence is recorded;
  - older configs and records unchanged.
- **Full suite: 1709 passed**, 0 failed (`uv run ... pytest`, 8 min 50 s; 1657 before plus the 52
  new). The tests that read the docs pass again after the docs commit (24).
- A 24-session mock rehearsal, 24 of 24 completed, with the prompts and outcome rows checked by
  eye (above).
- `python -m negsim.resolution.replay ... --verify` rebuilds both replays of two rehearsal
  sessions byte for byte.
- No paid call. No sign-off recorded anywhere.
- **After `resolve_v3`:**
  - 16 more tests in `tests/test_pairwise.py` (68 in all):
    - v3 against v2 (system text, line keys, the same rendering without factor lines);
    - the lines at 8 and 9.9 m and none behind, outside the cone or beyond 10 m;
    - the default template, the protocol's default and the `--plan` warning;
    - the head-on case under both templates;
    - the no-errand design.
  - **Full suite: 1725 passed**, 0 failed (9 min 28 s). The doc-reading tests pass again after
    the docs commit (24).
  - The rehearsal on `resolve_v3`: 24 of 24 completed, with lines shown at every head-on
    decision point.
  - Replays of two of its sessions rebuild byte for byte (`--verify`).

**Open for the user:** question 7 (age and gender still only within 5 m under `resolve_v3`), and
question 2 (the ethics sign-off, still pending).
