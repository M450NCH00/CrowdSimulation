# Work Log — Issue #32: [Feature] SI-3a.2: fictional ethnicity attribute and meetings inside a single-file passage

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/32
**Branch:** `feat/32-fictional-ethnicity-passage-meetings`
**Started:** 2026-10-16 20:37 (UTC+8)

## Understanding the issue

This is SI-3a.2, a follow-up to #30 (SI-3a). It changes what rule generation shows a model, so
it has to land before #30's paid pilot (Part 11), whose data would otherwise match no later
run. It makes no paid call. Two independent additions:

1. **A fictional ethnicity attribute** (`ethnic_group`), with invented group labels that carry
   no description, as a design factor of rule generation (group pair same or different, and a
   rotation of which label goes to whom) with a visibility switch of its own. Agents may *see*
   it; **no rule may read it**, and a rule that tries is kept as data in a new validation
   category, `protected_attribute`, since a model conditioning on ethnicity is a finding. It
   is off by default and needs a supervisor's ethics sign-off, recorded in `CLAUDE.md`, before
   any paid run may switch it on. Outcomes (who conceded, whose proposal was accepted, who got
   the larger share) are logged so that they can be stratified by group pair and visibility.
   Fictional groups test in-group against out-group (the minimal group paradigm) and cannot
   show how a model treats real ethnicities; the docs must say so.
2. **Meetings inside a single-file passage.** Today the rule format cannot say "the one who
   has walked less far in backs out". New scenarios start two agents at their meeting point
   inside a passage (symmetric and asymmetric, and with different maximum and backing speeds).
   New pair-level perception fields say whether each is inside the passage and how far it is
   from each end, and a new directive, `back_up`, makes an agent back out of the passage, wait
   for the other to clear, and go on. Rule schema version 3 carries both, with a load-time check
   that exactly one role backs up, and a seed rule, `passage_shorter_backs_out`. Intentional
   backing must be told apart from issue #26's walking-backwards artefact.

Then the prompts (a new frozen version), new case versions, a mock that exercises every new
path, a re-preview of the pilot's cost with an options table for open question Q5 of #30, and
behaviour checks over at least 20 seeds.

**What the code already does inside a passage (Part 2.1), established before anything was
written** (the 20:40 entry below has the numbers): the arbiter takes the pair on the first
step, makes the one that will be out of the segment sooner (going forward) the leader, and
gives the follower a speed bound of 0. It has no backing of its own: ORCA, in which the
follower does all of the avoiding (share 1) and the leader none, pushes the follower
*backwards* at almost the leader's speed until the leader has cleared, and that motion is
counted as issue #26's walking-backwards artefact. There is nothing in the arbiter to expose,
so `back_up` is new.

**Assumptions** (small ambiguities, stated rather than asked):
- A1. "A flag marking it as not referenceable by rules" is a flag on the attribute's
  definition (`AttributeSpec.rule_referenceable = False`, exported by the perception module
  and documented in `perception.md`), not a key repeated in every record.
- A2. "Pair-level fields that both agents compute identically" are per-agent values computed
  once per pair from the two positions and the passage geometry, as `time_to_segment_s` is; in
  the rule format they are agent-level fields (`either.`, `both.`, `agent.`). Their names are
  the issue's (`segment_distance_travelled`, not `..._m`).
- A3. The consistency check of 2.5 applies to rules that state `back_up`, as the passage-order
  check applies to rules that state a passage order: such a rule must make exactly one role
  back up. A rule that states no `back_up` leaves an in-passage meeting to the arbiter, as
  before. (A stricter reading is an open question below.)
- A4. Tests that pin what this issue changes (the visibility switches, the directive fields,
  the log schema version) are updated, with the reason recorded; #28's A2 reading.

### Prerequisites (checked before anything else)

- **P1. PRs #25, #27, #29 and #31 merged, and this branch created from `main` — FAILED.** All
  four PRs are in state `MERGED`, but each into its stacked parent branch, not into `main`:
  #25 into `docs/22-simulation-conflict-rules-literature` (PR #23, open), #27 into
  `feat/24-llm-negotiation-simulator`, #29 into `feat/26-orca-avoidance-layer`, #31 into
  `feat/28-rule-format-database-following` (merge commit `32bd93e`). `origin/main` is still
  `5a0f7be` (2026-09-06) and has no `llm_negotiation/` at all; 130 commits of `feat/28` are not
  on it. Between `main` and the simulator stack sit seven open literature PRs (#9, #13, #15,
  #17, #19, #21, #23), each based on the one before. As the issue instructs, I stopped and
  asked. **The user's answer (2026-10-16, in this session): "Stack on #31"**: commit the two
  #30 leftovers to `feat/30-conflict-cases-rule-generation` and push them, cut this branch
  from it, and target the PR at `feat/30-…`. Such a PR will not close #32 on merge (only a
  merge into the default branch does), as #31 did not close #30.
- **P2. The two uncommitted #30 items — DONE.** Both were clear in status, so they were
  committed to `feat/30-conflict-cases-rule-generation` and pushed (`e49ab46..2dad845`), not
  discarded:
  - `a18f727` *feat: optional random starts for the two-way crowd (spawn_pattern: random)*:
    `negsim/scenarios/bidirectional_flow.py`, its tests in `test_crowd_scenarios.py` (7 new),
    a replay check in `test_rulegen_replay.py`, one row each in `llm_negotiation/README.md` and
    `docs/parameters.md`. Before committing, the full suite ran on the working tree: **1,230
    passed** (#30's 1,223 plus these 7; 289 s), pyflakes 4.0.3 clean.
  - `2dad845` *docs: a beginner's guide to the whole repository* (`BEGINNERS_GUIDE.md`,
    1,015 lines; checked for anything resembling an API key first: none).
- **P3. `WORK_LOG-30.md` read**, including DD65 to DD84 and open questions Q1 to Q6. This issue
  is implemented against those decisions as they stand; any change is recorded below as one.

## Plan

Written before writing code; the progress log records where it changes. Baseline: **1,230
tests pass**, pyflakes 4.0.3 clean (P2 above; Python 3.13.3, PyYAML 6.0.3, pytest 9.1.1,
matplotlib 3.10.8, a fresh virtual environment in the session scratchpad).

The constraint that shapes most of it: **nothing frozen may change.** Committed runs and cases
hash the resolved scenario, sessions are named by a hash of their design cell, the v1 prompt
templates pin a hash of the field glossary, the old mock's paths cycle by index, and committed
run folders are checked against their own log version. So every addition is versioned or
written only when set, and the old versions keep working.

1. **Part 2.1 first**: write down what the arbiter does in an in-passage meeting, from the
   code and from the scratchpad measurement (done: 20:40 entry), in `derivations.md`.
2. **`ethnic_group` (1.1, 1.2).** A persona attribute, hidden by default, never filled in when
   absent (so #24's personas and logs are unchanged), validated as a fictional label. Perception
   record version 3 carries it (own and, when visible, the neighbour's). In `negsim/rules`: a
   new refusal category `protected_attribute`, checked before the schema, for any reference to
   it in a condition, a role assignment or a tie policy, derived names included. Tests,
   including that no execution path reaches it (no field reads it, no snapshot holds it).
3. **Segment fields (2.3).** `in_segment`, `segment_distance_travelled`, `_ahead`, `_behind`,
   computed once per pair in `pair_features`, in both records and both snapshots; `null`
   outside the passage. Rule fields gain the schema version that added them, and a `boolean`
   kind.
4. **Rule schema 3, `back_up` and the manoeuvre (2.4, 2.5).** `rule.v3.schema.json` (boolean
   values, `back_up`), frozen; v1 and v2 load unchanged and cannot read v3 fields. The
   consistency check. In the run loop: a back-up manoeuvre (back out to beyond the passage's
   end, wait for the other to clear, go on) at the agent's own backing speed, a new optional
   physical parameter; the pair released from the arbiter while it lasts; its own phase in the
   trajectory, events and outcome, and excluded from the walking-backwards artefact. Log schema
   version 5, with folders of versions 1 to 4 still checked against their own.
5. **Scenarios and the seed rule (2.2, 2.5).** A `passage_meeting` scenario type;
   `passage_meet_middle_v1.yaml` and `passage_meet_with_speeds_v1.yaml`, every number cited or
   tagged; the seed rule `passage_shorter_backs_out` (`test_seed`); the choice criterion in
   `derivations.md`.
6. **The design factors (1.3 to 1.5).** An optional `design.ethnicity` block (off unless
   `enabled: true`): `group_pair`, `label_rotation`, `ethnicity_visible`, the labels and the
   framing word. Cells and session ids of designs without it unchanged. A paid run with it on
   refused unless `CLAUDE.md` records the sign-off. Per-session outcome rows for stratification.
   The full-factorial size, reported.
7. **Prompts, cases, mock (Part 3).** Templates version 2 (frozen with the existing tool), the
   glossary generated per template version so that version 1 still checks; new case versions
   of the 18 cases by re-stepping their source runs (every field of the old version checked
   equal); case-source runs and cases for the two new scenarios; a new mock policy beside the
   old one; validation of `protected_attribute` and of the previous format's category.
8. **Behaviour checks**: 20 seeds, both new scenarios and their variants, the arbiter's
   fallback against the seed rule against plain ORCA: deadlocks, time to clear, backing
   distance (intentional and artefact), makespan.
9. **End-to-end mock runs** with ethnicity on, then off, with the in-passage cases.
10. **Part 4**: the pilot's worst case under the new prompt version, the mock's largest valid
    reply as a floor for m, and the options table for Q5. The pilot config is not changed.
11. **Docs**: `fictional-groups.md` (new); `perception.md`, `rule-format.md`, `derivations.md`,
    `cases.md`, `rule-generation.md`, `log-schema.md`, `metrics.md`, `parameters.md`,
    `architecture.md` (decisions from DD85), READMEs.
12. **Verify** (full suite with the network blocked, pyflakes, a search for the API key, zero
    spend), push, and a PR into `feat/30-conflict-cases-rule-generation`.

## Progress log

### 2026-10-16 20:37 — Prerequisites checked; branch created

- What I did: read `github_issue_workflow.md` and the issue; checked P1 to P3 (above); asked
  the user about P1; committed and pushed the #30 leftovers; created this branch from
  `feat/30-conflict-cases-rule-generation` at `2dad845`.
- Why: the issue makes all three hard stops.
- Result / what I found: P1 failed (the stack never reached `main`); the user chose to stack.
- Next step: read the code and documents this issue changes (the arbiter first, since Part 2.1
  asks for its in-passage behaviour to be documented before anything is written), then fill in
  the understanding and the plan.

### 2026-10-16 20:40 — Part 2.1: what the arbiter does when two agents meet inside a passage

- What I did: read `negsim/avoidance/coordination.py`, `negsim/control/strategy1.py`,
  `negsim/conflict/{roles,timing,zone}.py` and the run loop, then measured it. A scratchpad
  script (not shipped) subclasses `corridor_to_bottleneck` to start both agents inside its
  4 m, 0.8 m segment, facing each other 0.1 m apart, and runs it with the arbiter on and off.
- What the code does, step by step:
  1. **Trigger.** On the first step on which the two perceive each other, a single-file
     segment lies on both paths and neither has cleared it, and their occupancy intervals of
     the conflict zone overlap. Both being inside already, both intervals start at 0: the
     arbiter takes the pair on step 0.
  2. **Who goes first** (`decide_roles`). Exactly one inside: it leads (physical precedence).
     Both inside: a negotiated leader if the directives name one (`passage_order`); otherwise
     Strategy 1, whose first measure (time to the zone) ties at 0, so its second decides: the
     time to *clear* the zone going forward at the agent's walking speed, `d_out / v`. The one
     out sooner leads; an exact tie goes to the lower index (or a seeded draw).
  3. **The follower** gets a speed bound of 0 (`follower_speed_bound`: it is at or past the
     zone's entry and the leader is not clear), so the speed it *wants* is 0. ORCA is not
     switched off: the follower takes all of the avoidance (share 1), the leader none (share 0).
  4. **Nobody decides to back up.** The leader walks on at its full speed; in a passage too
     narrow to step aside, the only velocities ORCA allows the follower are backward ones, so it
     is pushed back at nearly the leader's speed until the leader has cleared the zone. That
     is issue #26's walking-backwards artefact (`metrics.md`, section 10), and it is counted as
     one. The arbiter's own view of the follower does not move meanwhile: `path_s` never
     decreases, so its `d_in` stays where it was.
- Measured (one seed; no perturbation):

  | Start (agent 0, agent 1 in, m) | Arbiter | Result |
  |---|---|---|
  | 1.7, 1.7 (symmetric) | on | leader 0 (tie, lower index); agent 1 pushed back 0.0–2.4 s at up to 1.282 m/s, from x = 0.30 to 3.24 (1.24 m past the end); handed back to ORCA at 2.3 s; completed 12.3 s; 1 backward episode, 2.5 s |
  | 2.7, 0.7 (agent 0 further in) | on | leader 0 (out sooner); agent 1 pushed back 0.0–1.6 s at up to 1.277 m/s, x 1.30 to 3.21; completed 11.3 s |
  | both | off | deadlock at 4.6 s: the two creep together at about 0.01 m/s and stop; no backward motion |
  | 2.7, 0.7, agent 1 walking 0.5 m/s with a maximum of 0.8 | on | **collision at 0.3 s**: the follower cannot retreat as fast as the leader (share 0) advances |

- So: at equal speeds the arbiter's fallback already makes the agent that has walked *less*
  far in give way, but by an ORCA artefact, not by a decision, at a speed nobody chose, and only
  while the follower can outrun the leader backwards. There is no backing inside the arbiter to
  expose as a directive, so `back_up` is new; it will release the pair from the arbiter while it
  runs (the 21:30 entry and DD93 below say how).
- Next step: the plan; the labels; then the code.

### 2026-10-16 21:10 — Part 1.1: the default labels, searched

- What I did: web searches (standard mode), one or more per candidate, recorded in full in
  `docs/fictional-groups.md`. Treated as data.
- Result: **Zorvel, Kestrop, Dremmik** pass: no exact hit as an ethnonym, nationality, place,
  language, surname or word, including searches aimed at Malay, Tamil and Chinese; their near
  matches are a drug brand (Zoryve), a Danish street (Kestrupvej) and a tool brand (Dremel).
  Rejected: *Orvane* (the French river Orvanne and a former commune of that name), *Kelbrin*
  (Kilbrin, a parish in Cork), *Hollvek* (Höllviken, Sweden), *Fyrrel* (the surnames Farrell,
  Ferrell), *Quorlan* (the Cornish place-name element *korlan*), and three that passed the search
  but echo a word of a Singapore community, which a fictional label must not: *Velorn* (Tamil
  *vel*), *Tessivar* (the Tamil pronoun *ivar*), *Melvori* (*Melayu*). *Brannoq* passed and
  is kept as a spare (its nearest match is an ancient Gaulish tribe, the Brannovices).
- Also for Part 2.4: the backing speed can be cited. Nakahara, Ishii, Ida, Nakazawa and Yamamoto
  (2005), ISBS 2005, pp. 823–826, "Results and Discussion": ten healthy adults (21.8 years)
  walked backwards at 0.43 (slow), 0.92 (normal) and 1.68 (fast) m/s; the normal pace agrees
  with Grasso, Bianchi and Lacquaniti (1998). One small sample of young adults: it is a cited
  value, not a population norm, and `parameters.md` will say so.

### 2026-10-16 21:16–21:35 — Parts 1.1, 1.2 (the loader), 2.2 and 2.3: three commits (logged afterwards)

- **How this entry was written.** The session that made `6948213`, `cb4a3d2` and `85ca01a`
  ended before it logged them, and left the next step half-written in the working tree. This
  entry was written on 2026-10-17, in the next session, from those commits, their messages and
  the code, tests and documents they changed, not from a memory of the work. Nothing is
  claimed here that those do not show.
- What was done:
  - `6948213` (21:16), **perception record version 3**. The passage fields `in_segment`,
    `segment_distance_travelled`, `segment_distance_ahead` and `segment_distance_behind`,
    computed once per pair from the two positions and the passage alone ("ahead" is the end on
    the other's side), so both agents' records hold the same values (A2); null outside the
    passage. `ethnic_group`, a persona attribute holding a fictional label
    (`negsim/personas/groups.py`: the default labels, their validation, a guard list of real
    group names, the framing word), hidden by default, left out of a persona that does not give
    it, and flagged on its definition as not readable by rules (A1). Version 2 records still
    read back. `perception.md`, "Passage fields (version 3)" and "The group (version 3)".
  - `cb4a3d2` (21:25), **`protected_attribute`**. The loader refuses any rule whose condition
    or role assignment (its field, role names and tie policy included) names the group or
    anything derived from it, before every other check; tests that no field a rule can read
    and no snapshot holds the group, and that matching never depends on it
    (`tests/test_protected_attribute.py`, six invalid fixtures). The four passage fields in the
    rule catalogue, each field now with the rule-format version that added it (`since`); the
    first template version's glossary generated from the fields it describes, so that its
    pinned hash still holds.
  - `85ca01a` (21:35), **the in-passage scenarios**: scenario type `passage_meeting`,
    `passage_meet_middle_v1.yaml` and `passage_meet_with_speeds_v1.yaml`; `backing_speed`, an
    optional physical parameter (Nakahara et al. 2005, cached under `refs/`);
    `parameters.md`.
- What those commits left unrecorded or undone, found on resuming:
  1. **`docs/fictional-groups.md` does not exist.** The 21:10 entry says the label searches
     are "recorded in full" there, but no commit on any branch has the file, nor has the
     working tree. The searches are to be done again in this session and recorded as the issue
     asks. The 21:10 entry's results are a summary of searches whose queries were not kept.
  2. Sections that the code and the documents cite but that were not written:
     `rule-format.md` section 14, `derivations.md` sections 17 and 18.
  3. Decision numbers: only DD86 (the framing word, in `groups.py`) was cited, and the 20:40
     entry refers to a DD93 (releasing the pair from the arbiter) and a "21:30 entry", neither
     of which was written. The numbering is set in the next entry, keeping both.
  4. No test count was recorded after the three commits.

### 2026-10-17 08:51 — Session resumed: Parts 2.4 and 2.5 finished, tested and documented

- **What I found.** The branch at `85ca01a`, not pushed. In the working tree, uncommitted and
  untested, plan step 4: rule schema 3 (`rule.v3.schema.json`, frozen in `MANIFEST.json`);
  the directive field `back_up` and how a pair's two directives combine on it; the consistency
  check; a cross-pair conflict on it in the matcher; the manoeuvre in the run loop (phases,
  end reasons, the arbiter releasing the pair, intentional backing left out of the artefact);
  log schema 5; the seed rule `passage_shorter_backs_out` (frozen in `MANIFEST.json`). No
  tests and no documents for any of it.
- **Baseline.** A fresh virtual environment in this session's scratchpad (Python 3.13.3,
  PyYAML 6.0.3, pytest 9.1.1, matplotlib 3.10.8, pyflakes 4.0.3). The full suite on the working
  tree as found: **14 failed**, every one pinning something the uncommitted work changes (log
  schema version 4 in four tests, the five directive fields, a pair resolution's dict, five
  seed rules and two schemas in six, the log document in two).
- **Before writing any test, I ran the manoeuvre** (scratchpad scripts, not shipped) in both
  scenarios and their variants, under the arbiter, plain ORCA, `back_up` given to either
  agent, and the seed rule. Every back-up run got both through without a collision. Four
  things were wrong or doubtful, and were changed:
  1. **The two started walking into each other, 0.1 m apart**, so the first step was a
     collision for ORCA to undo, in every condition: the agent ORCA gave the avoiding to was
     pushed backwards at up to 1.27 m/s on step 0. Two people who *have met* are better started
     at rest, face to face. Changed: `start_speed` (default 0; `preferred` starts each at its
     own preferred speed, as before and as every other scenario does; a number starts both at
     it). The two v1 configs were edited to say so: they were never pushed and nothing uses
     them yet, and "never edit" is about configs something depends on. This is a decision
     (DD91), and **it decides what the arbiter's way does** (item 5), so the behaviour checks
     report both starts.
  2. **A backer already moving back faster kept that speed.** With share 0, ORCA does not let
     an agent reduce its velocity's component away from a neighbour that is closing in. In the
     tied symmetric case, where the arbiter had pushed the follower back at 1.27 m/s before
     the seed rule matched, the backer went on at 1.21 to 1.34 m/s, not its 0.92. Changed:
     while one backs out, the other's preferred speed is capped at the backer's backing speed
     (DD95). The backer then backs at exactly its backing speed, and the two move as one
     (tested).
  3. **The new artefact distance counted steps outside its episodes**: 0.5 to 0.7 m of
     "artefact distance" in runs with no artefact episode at all. Changed: it is counted within
     the episodes only (`EpisodeTracker.total_amount`).
  4. **Whether a manoeuvre started depended on the visibility settings** (through the pair
     features, which are null when speed or size is hidden), and nothing checked that the other
     was ahead of the backer. Changed: the segment the two meet in is found from the geometry
     (`_meeting_segment`): too narrow for the two, on both paths, not yet left by the other,
     the backer's centre inside it, the other ahead of it along its path.
  Also: the viewer called a pair passing to a manoeuvre "handed back to ORCA" and showed the
  new event as a bare word; it now says what happened, and flags backing, waiting and the
  other agent.
- **What the arbiter does from rest** (new; `derivations.md`, section 17.1, which also holds
  Part 2.1's account now, as plan step 1 said it would): it does not get the two through. A
  leader with share 0 may not close in faster than its own velocity already does, and a
  follower standing in front of a standing leader is on no collision course, so nothing pushes
  it back. Unperturbed, in `passage_meet_middle_v1`: the leader pushes the touching follower
  back at 0.030 m/s for the whole 60 s, a time-out with neither through (above the deadlock
  threshold of 0.01 m/s); perturbed, a deadlock at about 4 s. From the walking start the
  arbiter's way gets them through as the 20:40 entry measured (unperturbed: the follower
  walks backwards 2.5 s, 2.96 m; through at 12.3 s).
- **Tests added**: in `test_passage.py`, the start speeds and 14 tests of the manoeuvre and its
  logs (who backs out, at what speed, the other's pace, the trajectory's phases, the
  time-optimal against the distance-optimal choice, the artefact kept apart, the arbiter
  releasing the pair, the seed rule end to end, no effect outside a passage, the other behind,
  visibility, the schema check of a run and damage to it, the viewer); `test_rules_schema_v3.py`
  (the schema, what versions 1 and 2 cannot do, true or false, the consistency check, the seed
  rule); in `test_directives.py`, the backer and the leader of a pair. Updated because the
  issue changes what they pin (#28's A2 reading): the log schema version (four tests), the
  directive fields, a pair resolution's dict, the seed rules and schemas (six), the viewer's
  flags.
- **Documents**: `derivations.md` sections 17 (the arbiter's way, the manoeuvre, its interplay
  with ORCA and the arbiter, intentional backing) and 18 (which of the two to back out);
  `rule-format.md` section 14 (version 3, the consistency check, `protected_attribute`) and
  sections 7 and 9; `log-schema.md` version 5; `metrics.md` section 10; `parameters.md`
  (`start_speed`); `rule-matching.md` (the cross-pair conflict); `rule_db/README.md`.
- **Decisions** (numbered on from #30's DD84; `architecture.md` will list them):
  - **DD85.** The default labels Zorvel, Kestrop, Dremmik, in that rotation order, Brannoq a
    spare (`fictional-groups.md`, to be redone and written in this session).
  - **DD86.** The framing word defaults to "ethnic group"; it is a setting recorded with every
    session. Pending supervisor review (the issue's words).
  - **DD87.** `ethnic_group` is a persona attribute: hidden by default, left out of a persona
    that does not give it, and flagged on its definition as not readable by rules (A1).
  - **DD88.** `protected_attribute`: any reference containing "ethnic", the attribute's name,
    a default label, or (in rule generation) a session's own words, anywhere in a condition or
    a role assignment (field, role names, tie policy), refused before every other check.
  - **DD89.** The passage fields are computed once per pair from the two positions and the
    passage; "ahead" is the end on the other's side; null outside the passage, outside the
    single-file class, or when the two are level (A2).
  - **DD90.** Every rule field records the format version that added it; a rule reads only
    its own version's fields; a case taken from a version 2 record keeps its snapshot; a
    template's glossary is generated for the format version it describes.
  - **DD91.** `passage_meeting` places the two at the meeting point, 0.1 m apart, each path
    starting where its agent stands; **at rest by default** (item 1 above).
  - **DD92.** `backing_speed` is an optional agent-type parameter, 0.92 m/s when not set
    (Nakahara et al. 2005, the normal pace of ten young adults), never above the maximum
    speed, written into a resolved scenario only when set.
  - **DD93.** A pair in a back-up manoeuvre is taken from the arbiter (a handoff
    `to: back_up`), and the arbiter does not take it while the manoeuvre lasts.
  - **DD94.** The manoeuvre: back along the segment, away from the other, to the run-out
    `r_i + r_j + margin` beyond the end on the centre line (the edge of the conflict zone),
    at the backer's backing speed; wait until the other has come out by the same distance,
    has arrived, or the two have lost sight of each other; then go on. It starts only inside a
    segment the two meet in, read from the geometry (item 4); one per agent at a time, one
    per pair interaction.
  - **DD95.** While the backer backs out, the shares are 0 for it and 1 for the other, and the
    other's preferred speed is capped at the backer's backing speed; while it waits, 1 and 0.
  - **DD96.** `back_up` names the pair's leader (the other one). Two that back up are a
    reciprocity violation, and neither does; a directive that backs up and leads is a
    violation, and the backing stands.
  - **DD97.** The consistency check reads A3: a rule that sets `back_up` for any role makes
    exactly one of two roles back up, and not the one it makes go first; a symmetric rule
    cannot set it; a rule that sets nothing of it is not checked for it. Refused as `back_up`,
    counted as `inconsistent` in rule generation.
  - **DD98.** The backing phase is never counted toward the walking-backwards artefact;
    everything else is, a waiting backer's backward motion included. The artefact's distance is
    counted within its episodes.
  - **DD99.** Log schema 5 (`log-schema.md`, change log); folders of versions 1 to 4 are
    checked against their own.
  - **DD100.** Rule schema 3 is version 2 with `back_up` and `true`/`false` values; versions 1
    and 2 can use neither, nor the passage fields.
- Committed as `5d3b052`; 1,324 tests pass (260 s), pyflakes clean. Progress comment on the
  issue.

### 2026-10-17 09:40 — Part 1.1 again: the labels searched and written down; Zorvel replaced

- What I did: the searches of the 21:10 entry again, since their record was lost (Q5), with
  the web search tool in standard mode: each default label and the spare exactly, as a people,
  tribe, language, village, place or surname, and against Malay, Tamil and Chinese; then
  replacement candidates. Every query and result is in `docs/fictional-groups.md`, section 2,
  with the pages they came from. Treated as data.
- Result:
  - **Zorvel is rejected.** It ends in *vel*, the Tamil word for spear and the root of Tamil
    names such as Thangavel: exactly the echo for which the 21:10 entry rejected *Velorn*. The
    two judgements were inconsistent; this applies the stricter one to both.
  - Kestrop and Dremmik pass again (nearest: the surnames Westrop and Kestle; Dremel, Dremmen).
  - The spare, Brannoq, has no exact match either, but its first syllable sounds like Pulau
    Brani, an island of Singapore (Malay *berani*, "brave"): faint, but a Singapore echo, so it
    stays a spare. *Thressik* (nearest: an ancient Thracian river and tribe, and a fictional
    reptilian race; it also rhymes with Dremmik) and *Vorlesk* (German *vorlesen*) were not
    used. **Pellund** passed (nearest: Pellworm, a German island; the old English word and
    surname Pell; the Scandinavian name Pelle) and replaces Zorvel.
  - **DD85, as it stands now: Kestrop, Dremmik, Pellund**, in that order of rotation; Brannoq
    the spare. Nothing frozen used Zorvel. Code, a fixture and three tests that named it
    changed to the new set.
- Also written: `docs/fictional-groups.md` sections 1, 2, 4, 6 and 7 (the attribute, the
  labels and every search, why no rule may read it, the sign-off status, what fictional
  groups cannot show). Sections 3 and 5 come with the design factors (plan step 6).
- Next step: the design factors (plan step 6).

### 2026-10-17 10:20 — Parts 1.3 to 1.5: the group in the design, off by default, and logged by outcome

- What I did:
  - **The design** (`negsim/rulegen/design.py`): an optional `design.ethnicity` block, off
    unless `enabled: true`, with the labels, the framing word and three factors, crossed with
    the six of issue #30: `group_pair` (same, different), `label_rotation` (which label person 1
    gets; person 2 the same one or the next round the set) and `ethnicity_visible`, a switch apart
    from `demographics_visible`. Each person gets its label (`ethnic_group`), the session its
    `framing`. A design without the block, or with it off, has exactly the cells and session ids
    it had (a cell's code hashes the group's factors only when it has them; tested against the
    old formula).
  - **Off by default, and the sign-off**: no shipped config has the block. A paid run with it on
    is refused before anything is sent unless `CLAUDE.md` holds the sentence "Ethics sign-off for
    the fictional-group factor (issue #32): approved by the supervisor on YYYY-MM-DD"
    (`refused_no_sign_off` in `invocations.jsonl`). A test checks that the repository records no
    sign-off. **Ethics sign-off from the supervisor: pending unless recorded otherwise.**
  - **The outcome rows** (`negsim/rulegen/outcomes.py`, `outcomes.jsonl`): one per session, group
    on or off, with what to stratify by and what came of it: proposals per person, whose was
    accepted (`proposed_by`), who accepted the other's (`conceded_by`), who said no rule is
    possible, and for the agreed or stated rule its category and what it does to each person on
    the case's own pair: role, directive, **who gets the larger responsibility share**, who goes
    first, who backs up. `summary.json` gains `design` (the full factorial's size) and `groups`
    (outcomes by condition, group pair and visibility); `--plan` prints the size.
  - The rule-generation log is version 2; `log-schema.md`, `rule-generation.md` section 2 and
    `fictional-groups.md` sections 3, 5 and 6 say what changed.
- Result: 25 new tests (`tests/test_rulegen_groups.py`); the 185 tests of rule generation pass.
  **The full factorial** with the group, every level: 288 × 12 = **3,456 cells per case and
  condition**, so with K = 3 statements 13,824 sessions per case; with groups and demographics
  hidden, many of these show a model the same words. SI-3b will need a fraction; none is chosen.
- Decisions:
  - **DD101.** The rotation is cyclic: person 2 of a `different` pair gets the next label round
    the set, so `label_rotation` has one level per label and the factors stay crossed. It uses
    three of the six ordered different pairs; each label is each person's equally often.
  - **DD102.** `ethnicity_visible: false` hides the groups from both people, a person's own
    included, so the control shows nothing of them (as `demographics_visible` does for age and
    gender).
  - **DD103.** The sign-off is one exact sentence in `CLAUDE.md`, with a date; only the user adds
    it. A mock run needs none.
  - **DD104.** What a rule does to each person is read on the case's own snapshot with the
    session's people in it (ages and genders as far as the session shows them), not on a run.
  - **DD105.** The rule-generation log is version 2 (`outcomes.jsonl` and the group).
- Next step: the prompts, the cases, the mock and validation (plan step 7).

### 2026-10-17 11:20 — Part 3: prompt version 2, validation, the mock, and re-stepping cases

- What I did:
  - **Prompt version 2**, frozen with #24's tool (`rulegen_common_v2`, `rulegen_negotiate_v2`,
    `rulegen_state_v2`; their hashes in `MANIFEST.json`, the glossary's pinned inside the
    common template). The common template describes rule format 3 (its glossary, generated as
    before, adds the four passage fields, a true-or-false line, `back_up` and what a rule using
    it must say); the condition templates add lines for standing still, for being inside the
    passage (how far in, how far to each end, and in A the other's distance in) and, only when
    the session shows groups, each person's group. Before freezing I rendered them for a
    meeting inside the passage, read them, and checked that a hidden group appears nowhere.
    Version 1 is untouched and renders exactly as before (the renderer uses a line only if the
    template has it).
  - **Validation**: a category of its own, `protected_attribute`, first in precedence; the
    session's own labels and framing words protected where it showed them; what a later rule
    format added (`back_up`, a passage field, true or false) is `format_limit` for a session
    shown an earlier one; the loader's `back_up` counts as `inconsistent`. Each session record
    says the format its prompt described (`rule_schema_version`), and the writer writes rules in
    it (format 3 for prompt version 2).
  - **The mock**: a second policy, `rulegen_paths_v2`, with three more paths after the old ones
    (a rule that reads a group, a valid in-passage rule, an inconsistent one); `rulegen_paths`
    unchanged. The in-passage rule is valid with prompt version 2 and a format limit with
    version 1.
  - **Re-stepping cases** (`restep_case`, `python -m negsim.rulegen.cases restep`): a case's
    next version, made by running its source run again to the step its pair formed and taking
    the two records the run builds then; every field of the old version must come out equal.
    **A dry run over all 18 cases of `si3_v1` gave every field back** (81 s), so the current
    code reproduces the source runs exactly. Case format 2 adds `derived_from`.
- Tests: 12 for prompt version 2 (`test_rulegen_prompts_v2.py`), 5 for validation, 1 for
  re-stepping, 3 for the mock and a whole experiment on prompt version 2 with the group on
  (every new path, its category, rules written in format 3). The validation table gains the new
  category (the issue adds one; #28's A2 reading).
- Decisions:
  - **DD106.** Prompt version 2 is version 1 with exactly the four kinds of line and the rule
    format 3 glossary; it also says the single-file kind of meeting covers a stretch the two are
    in. Version 1 stays the default of a config, so that issue #30's configs mean what they
    meant.
  - **DD107.** `protected_attribute` is a validation category of its own, before every other.
  - **DD108.** A rule that uses what a later rule format added is `format_limit` for a session
    shown the earlier format.
  - **DD109.** A new mock policy beside the old, whose paths are unchanged.
  - **DD110.** Cases get new versions by re-stepping their source runs, checked field by field.
- **A change of plan, ahead of Part 4.** The plan (step 10) said the pilot config would not be
  changed. The issue says this work must land before the pilot "otherwise the pilot's data would
  not match any later run", so the pilot should run on prompt version 2. I will point the pilot
  at prompt version 2 and the re-stepped cases, and change nothing else (not its cap, not its
  design): recorded as a decision there.
- Next step: commit; then, from a clean tree, the passage case-source runs, the re-stepped
  cases and the passage cases.

### 2026-10-17 14:02 — Session resumed: Part 3 checked and committed

- **What I found.** The branch at `328e32c`, never pushed (`origin/feat/30-…` is still at
  `2dad845`, its base). In the working tree, uncommitted: the work of the 11:20 entry, and
  three things that entry does not mention:
  1. Two case-source configs, `configs/cases/source_passage_meet_middle.yaml` and
     `source_passage_meet_with_speeds.yaml` (written 09:58, never run: no `runs/si32_*`).
  2. A change to the run loop and the outcome (written 10:06, *after* the work log's last
     write at 10:04, so not logged anywhere): each agent's time out of each single-file
     segment at its far end (`segment_exit_times`), and in `outcome.json`'s `single_file`
     entries `exit_time_s` and `first_out`. Two who start inside a passage both "enter" it on
     step 0, so `first_through` is null for every passage run; `first_out` says who got
     through first. Untested and undocumented; taken up in the next entry.
  3. A correction to the record: **the headings of the last two entries do not match the
     clock.** The "10:20" entry's commit, `328e32c`, is stamped 09:53, and the "11:20" entry's
     files were written between 09:52 and 10:06. The work they describe is as stated; their
     times are not. From here on, headings are read from the clock.
- **Baseline.** A fresh virtual environment in this session's scratchpad (Python 3.13.3,
  PyYAML 6.0.3, pytest 9.1.1, matplotlib 3.10.8, pyflakes 4.0.3). The full suite on the
  working tree as found: **1 failed, 1,369 passed** (303 s). The failure,
  `test_every_proposal_is_categorised_and_none_is_discarded`, pins that issue #30's mock
  (`rulegen_paths`) yields every category in `CATEGORIES`; Part 3 added `protected_attribute`
  to that tuple, and the old policy, unchanged by design (DD109), never yields it. Updated
  under A4: the old policy is expected to yield issue #30's five categories, and the test of
  `rulegen_paths_v2` now asserts that it yields **all six in both conditions** (it did). The
  two files: 59 passed. pyflakes clean.
- **Committed** the 11:20 entry's work without items 1 and 2 above, which belong to the
  passage cases. Item 2 only adds keys that no test reads (`validate_run_dir` checks for
  missing keys, not extra ones), so the suite's result on the working tree holds for the
  commit without it.
- Next step: the exit times (tests, `log-schema.md`, and `first_out` in a case's
  `baseline_outcome`); then the case-source runs, the passage cases and the re-stepped cases.

### 2026-10-17 14:28 — Exit times, a case's format by its content, the configs, and a one-step mismatch fixed

- What I did:
  1. **The exit times** (the 14:02 entry's item 2), tested and documented. Each entry of an
     outcome's `single_file` has `exit_time_s` per agent and `first_out`; the schema check
     requires both in a version-5 outcome; `summary.csv` gains `first_out`; and a case's
     `baseline_outcome` gains it. Log schema 5 is not pushed yet, so it stays version 5 and its
     change log says so (`log-schema.md`).
  2. **A case's format version now follows what it holds.** Part 3 set every new case to
     format 2, so extracting `si3_cases_v1.yaml` again from issue #30's committed runs gave files
     that differed from the frozen ones in that number alone, and the store would refuse them
     ("frozen with other contents"). That breaks the module's own promise that the same runs
     give the same files. Now a case whose records are of perception version 2 is format 1, as
     before; format 2 is a case with version 3 records (which says `first_out`) or a re-stepped
     one (`derived_from`). Tested: all 18 files of `si3_v1` come back byte for byte (2 s). The
     manifest's `case_format_version` is the newest format it holds.
  3. **A stratum key, `experiment`.** Both passage scenarios are of type `passage_meeting` and
     their case-source configs name their levels alike, so strata by scenario and variant would
     have pooled the two scenarios' layouts. The passage extraction
     (`configs/cases/si32_passage_cases_v1.yaml`) is stratified by experiment and layout, one case
     each: 8 cases. The tier is not a stratum there: from rest, the same layout deadlocks under
     one seed and times out under the other, so the tier follows the seed, not the situation.
  4. **The behaviour-check configs**, `configs/rule_following/si32_passage_meet_middle.yaml`
     (240 runs) and `si32_passage_meet_with_speeds.yaml` (320): distances walked in × start
     (rest, walking) × mode, 20 paired seeds, primary baseline, trajectory stride 10 as issue
     #28's checks. Modes: `arbiter` (the baseline as it is), `seed_rule` (the seed rule alone, the
     arbiter as its fallback), `orca_only` (the arbiter off); and in the with-speeds scenario
     `time_optimal`, agent 0 told to back up by a static directive: the choice that
     `derivations.md` section 18 says is quicker there, and that no rule can state (nobody can
     see a backing speed).
  5. **A trial of the behaviour checks in scratch** (all 560 runs, 88 s, the tables drafted)
     found one thing wrong. In 11 of the 80 seed-rule runs with the slow backer, the arbiter took
     the pair on the step its manoeuvre ended and gave it back on the next ("the conflict zone
     was cleared"). The manoeuvre ended when the other's centre was 1 mm short of the run-out
     beyond the end, measured along the passage's axis; the arbiter's zone counts the other clear
     at the run-out along its own path. So the backer was held one step longer (0.1 s), and the
     log showed an arbiter episode that was not one. Fixed: the manoeuvre ends by the arbiter's
     own criterion. After the fix, none of the 560 runs has it. A regression test on the run
     that showed it (`104_asymmetric_walking_seed_rule_r4`, which had two handoffs and now has
     none).
  6. Found and kept as a result: in the with-speeds scenario every seed-rule run, and most
     time-optimal runs, have one walking-backwards episode. Traced in one run, it is the
     backer's *waiting* phase (4.7 to 5.9 s): ORCA pushes the waiting backer back 0.33 m and
     0.15 m aside as the other comes out (Q4). DD98 counts that as the artefact, as designed. In
     the equal-speed scenario the wait is shorter than an episode's 1 s minimum, so no episode.
- Tests updated because the issue changes what they pin (A4):
  `test_the_committed_experiments_are_pinned_to_their_own_seeds` required every config under
  `configs/avoidance/` and `configs/rule_following/` to seed `per_run`. Its intent (DD66) is the
  15 configs of issues #26 and #28, whose runs predate paired seeding. It now names those 15,
  and checks that the si32 configs are paired, so the modes of one repeat share a seed.
- Result: full suite **1,372 passed** (196 s), plus the regression test run alone (passed);
  pyflakes clean.
- Decisions:
  - **DD111.** Who came out of a single-file segment first (`first_out`, and each agent's
    `exit_time_s`) is part of log schema 5, of a case's baseline outcome, and of `summary.csv`.
  - **DD112.** A case's format version follows its content: format 1 for records of perception
    version 2, so that issue #30's extraction stays reproducible file for file.
  - **DD113.** A back-up manoeuvre ends when the other is out of the conflict zone by the
    arbiter's own measure (its progress along its path past the segment's exit by the run-out).
  - **DD114.** The behaviour checks: the three modes the issue names, plus a `time_optimal`
    reference in the with-speeds scenario; 20 paired seeds; the primary baseline only (under
    the unperturbed one, 20 seeds would be 20 copies of one run).
  - **DD115.** The passage cases are stratified by source experiment and layout (one each), not
    by tier.
- Next step: commit; then, from the clean tree, the case-source runs, the behaviour-check runs,
  the re-stepped set, and the passage cases.

### 2026-10-17 14:35 — The runs and the cases, made from a clean tree at `d57e854`

- What I did, in this order (the order matters: run logs do not make a tree dirty, the case
  store does):
  1. The two case-source experiments (`runs/si32_source_passage_meet_*`, 16 runs) and the two
     behaviour checks (`runs/si32_passage_meet_*`, 560 runs): 90 s, every run's config records
     `d57e854`, not dirty. 23 MB, with a trajectory stride of 10 in the checks, as #28's.
  2. **The re-stepped set**, `python -m negsim.rulegen.cases restep --set si3_v1 --new-set
     si3_v2` (63 s): **every field of all 18 cases came out equal**, and each version 2 records
     `d57e854`, not dirty, in `derived_from`. Version 1 of each is kept as it was.
  3. **The passage cases**, `extract configs/cases/si32_passage_cases_v1.yaml`: 16 eligible pairs
     (every pair forms on step 0, both inside, class `single_file_segment`, T3 walking, T3 or T4
     from rest), **8 cases**, the ids the scratch trial gave.
- A mistake, found and undone: the first extraction wrote the case set's description as "The
  in-passage cases of issue", because in YAML an unquoted ` #32` starts a comment. Nothing was
  committed. I removed only that extraction's 8 files, its report and its two manifest entries
  (the re-stepped set untouched), quoted the description, and extracted again: the same 8 cases.
  **Issue #30's `si3_cases_v1.yaml` has the same defect**: its frozen set reads "The first case
  set of issue". Its config and its manifest entry are frozen, so it stays, recorded here.
- Tests: a test of the two committed sets (si3_v2: version 2 of every si3_v1 case, records of
  perception version 3, from a clean tree; si32_passage_v1: one case per experiment and layout,
  both inside on step 0, `first_out` null from rest and agent 0 walking). The case, replay,
  description, prompt and hygiene tests pass (82).
- Next step: the behaviour-check tables in `negsim.rules.report`, quoted in
  `behaviour-checks.md`; `cases.md`.

## Open questions / risks

- **Q1 (carried from #30). The supervisor's approval of simulation work, and now of the
  ethnicity factor, is not recorded in `CLAUDE.md`.** This issue makes no paid call. The
  ethnicity factor is off by default and a paid run with it on is refused until the ethics
  sign-off is recorded there (Part 1.4).
- **Q2. How should an in-passage meeting start?** At rest (DD91, the default) the arbiter's
  way does not get the two through; walking, it does, by issue #26's artefact
  (`derivations.md`, section 17.1). The behaviour checks report both. Which one SI-3b's cases
  should come from is the user's and the supervisor's call; `start_speed` is one setting.
- **Q3. The consistency check reads A3**: only a rule that says who backs up must back up
  exactly one role. A stricter reading (any single-file rule that can match two people both
  inside must say who backs up) would refuse rules that leave the meeting to the arbiter,
  as every rule before this issue does. Not adopted; easy to add if wanted.
- **Q4. The backer waits on the passage's centre line**, where the other comes out, and ORCA
  moves it aside (sometimes backwards: counted as the artefact). A person would step aside
  first; doing so would need the simulator to pick a side, which would build a convention into
  it. Recorded, not changed.
- **Q5. The label searches of the 21:10 entry were not kept** (the 2026-10-16 21:16–21:35
  entry, item 1). Redone on 2026-10-17 (the 09:40 entry): Zorvel failed the 21:10 entry's own
  echo rule and was replaced by Pellund. The labels remain a decision for supervisor review
  (DD85): a searched label is one with no meaning found, not one with no associations.

## Summary (fill in at the end)

<What changed, why, how it was verified.>
