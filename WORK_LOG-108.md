# Work Log — Issue #108: RF-31: rule format 4: what one person sees of the other, roles by a condition, own-only conditions, actions as steps

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/108
**Branch:** feat/108-rf31-rule-format-4 (stacked on `feat/67-rf12-translate-rule-format3`, PR #107 merged)
**Started:** 2026-10-26 12:14 UTC

## Understanding the issue

RF-12 (#67) translated RF-11's four kept head-on rules into rule format 3 and found that format 3
kept almost nothing: two translations are plain ORCA, the third (both slow in every head-on)
gridlocks the crowd, and the signalling rule cannot be written. Every translation reproduces 0.36
of the 76 Step 1 sessions, plain ORCA's own share. What made the LLM agents differ from ORCA is
exactly what format 3 cannot read or say: who gives way, what each sees of the other (a cane, a
suitcase, a phone), and when they start, how far they turn and until when.

The user decided on 2026-10-26 to extend the format as **schema version 4**, with four
extensions, before RF-14 and RF-18:

1. **Visible attributes:** `mobility_aid`, `load`, `distraction` as agent-level category fields
   (`since: 4`), each under its own visibility switch, carried through the avoidance layer's
   people, the perception record and the rule snapshot.
2. **Roles by a condition:** `roles: {by_condition: {when, assign, tie: no_match}}`; the rule does
   not apply when both or neither meet the condition.
3. **Own-only conditions (3b):** a role's directive may carry `own_when`, a condition on the
   person's own private factors under a new prefix `self.` (assertiveness, urgency, residence,
   memory note, knowing the other, and perceived attractiveness as `self.finds_other_attractive`).
   It may switch on only the person's own movement (`speed_scale`, `clearance_margin`, `steps`);
   anything else is refused (`own_only_scope`).
4. **Actions as steps:** a directive field `steps` in Step 1's vocabulary, carried out by the
   existing plan executor under `keep_line`, with ORCA still avoiding underneath, started once per
   encounter for that person on a rule match.

Perceived attractiveness becomes readable by a rule (format 4, own view only), which the
supervisor agreed (the user, 2026-10-26, issue comment). Real ethnicity stays unreadable in every
version. Versions 1 to 3 must load, match and be followed exactly as before.

The paid part (task 9, re-translating round 1's four rules, about USD 0.002) needs its own
approval and cap in `CLAUDE.md`; nothing is recorded for #108 yet, so the build stays on the mock
until the user gives one.

## Plan

1. Task 1: record the decisions (CLAUDE.md supervisor decision with date and reason; the track
   constraint amended; `pairwise-factors.md` section 7; README; #55). Ethics-gate sentences unchanged.
2. Task 2: `rule_db/schema/rule.v4.schema.json`, frozen in `rule_db/MANIFEST.json`;
   `SCHEMA_VERSIONS = (1, 2, 3, 4)`.
3. Task 3: the three visible attributes through fields, perception (own attributes only when the
   switch is on), snapshot, visibility config.
4. Task 4: roles by a condition in the model and the matcher (and the ambiguity grid).
5. Task 5: own-only conditions: `self.` fields, the scope check, the protected-attribute check
   per version; rulegen validate follows.
6. Task 6: steps: a crowd plan driver that reuses `PlanDriver`'s step mechanics; the matcher
   starts a plan on a match; attach it only when an active rule has steps. Measure the cost.
7. Task 7: templates `rulegen_common_v3` (format 4, glossary pinned) and `translate_v2`.
8. Task 8: `negsim.translation` accepts version 4; the losses map updated; the identity check
   carries the session's visible attributes and private factors.
9. Task 9: re-translate round 1 (paid, after approval), identity check, crowd screening.
10. Task 10/11: docs and tests.

## Progress log

### 2026-10-26 12:14 UTC — Read the issue, the track and the code
- What I did: read #55 (next unchecked issue is #108), #108 and its comment, RF-12's report,
  `rule-format.md`, `rule-matching.md`, `rule-translation.md`, `negsim/rules/` (fields, model,
  conditions, snapshot, matching, provider, database), `negsim/resolution/execute.py` and
  `reply.py`, `negsim/translation/`, `negsim/rulegen/validate.py` and `describe.py`, the avoidance
  simulation's driver hooks and the avoidance experiment's provider and visibility parsing.
- Result / what I found:
  - The persona schema already has `mobility_aid`, `load`, `distraction` (and the private
    factors) as factor attributes, so a crowd population can already be given them; the
    perception record's `neighbour_attributes` already passes any persona attribute whose
    visibility switch is on. What is missing is the switch (the avoidance config accepts only
    `default_visibility()`'s keys), the observer's own value, and the snapshot fields.
  - `AvoidanceDirective` is a frozen dataclass whose field list is a log contract
    (`DIRECTIVE_FIELDS`), so `steps` and `own_when` should live beside it in the rule, not in it.
  - `PlanDriver` serves one encounter with a fixed set of agents; its per-plan mechanics
    (`_move_on`, `_ended`, `_step_velocity`, ...) are reusable by a driver for a crowd.
  - The simulation has one `plans` slot; the identity check already uses it for a watcher, so a
    rule's steps driver must combine with it.
- Next step: design decisions below, then build task by task.

### 2026-10-26 13:30 UTC — Tasks 1 to 6 built on the mock
- What I did: task 1 (CLAUDE.md supervisor decision and track constraint, `pairwise-factors.md`
  section 7, #55's constraint line); the version 4 schema, frozen; the three visible attributes;
  roles by a condition; own-only conditions with `self.` fields and the scope check; steps parsed
  with Step 1's parser and run by `negsim/rules/plans.py` (`RuleStepDriver`, a `PlanDriver` without
  a fixed encounter, under `plan_orca` and `keep_line`), attached by the simulation only when the
  rule provider has one (`Drivers` joins it to a run's own driver). Rule generation's validator
  follows.
- Result: a head-on trial in the shipped corridor: plain ORCA deadlocks (the two are exactly
  symmetric); under a version 4 rule (roles by a cane, the other sidesteps 0.6 m at 5 m, then walks
  until the other passes) the sidestep holds through the plain step, the person goes back to their
  path after passing, nobody touches.
- Five existing tests failed after the build, all enumerations of the catalogue or of the schema
  versions (`test_rules_format`, two in `test_rules_schema_v2`, the documented field table) and one
  loader reason (`either.urgency`: `unknown_field` became `unobservable_field`). I gated the two new
  "unobservable" names (`urgency`, `knows_other`) to version 4 rules, so a version 1 to 3 rule is
  refused exactly as before and that test passes unchanged; the catalogue tests gained lines for
  version 4 (noted in each); the table is documented.
- Changed from the plan (D-E): the observer's own **core factors** (all seven, not only the three
  visible ones, and not gated by their switches) are in its record's `attributes` when its persona
  has them, because its own-only condition needs its own private factors in the snapshot it builds
  from its own record (the formation check). No persona of a run before this issue has them, so
  every earlier record is unchanged; the perception schema version stays 3.

### 2026-10-26 13:50 UTC — Task 6: the cost of steps in a crowd
- What I did: the two-way flow (50 + 50, `configs/scenarios/bidirectional_flow.yaml`, no
  perturbation), people given ages, genders, canes (one in three) and assertiveness in turn; best of
  3 runs each, trajectory not recorded; then a profile of one run.
- Result:
  | Run | Steps | Wall time (s) | Steps per second | Collision episodes |
  | --- | --- | --- | --- | --- |
  | plain ORCA | 877 | 12.3 | 71.2 | 512 |
  | format 3 rule (the younger slows and gives way) | 1,032 | 22.3 | 46.3 | 498 |
  | format 4 rule, same matching, no steps | 1,200 (timeout, 99 of 100 arrived) | 23.7 | 50.7 | 694 |
  | format 4 rule with steps and an own-only condition | 1,113 | 29.8 to 31.5 | 35.3 to 37.4 | 972 |
  - Per step, the steps rule took 1.36 times as long as the same rule without steps, and 1.31 times
    the format 3 rule. **The driver's own code is about 0.7% of the run** (profile: `plans.py`
    0.18 s, `execute.py` 0.19 s, the passing scenario's events 0.01 s, of 53.5 s); the rest of the
    difference is the motion the plans cause (more steps, more pairs to match, harder ORCA problems).
    Matching itself is about 15% of a rule run (`rules/matching.py`), the larger cost towards 10,000
    agents.
  - The trial rule doubled collision episodes in this dense flow (a sidestep into the other stream,
    then keeping that line): a property of that rule, which crowd screening exists to catch.
- Next step: templates, translation, tests, docs; then ask the user about the paid run.

### 2026-10-26 14:30 UTC — Tasks 7, 8, 10 and 11 on the mock
- What I did: `rulegen_common_v3` (format 4; its glossary generated from the catalogue and the
  version 4 schema, pinned) and `translate_v2` (translate_v1 for format 4; reply format, kinds, user
  message and retry word for word), both frozen. `negsim.translation` takes the format from the
  template's common template; losses map, identity check (each person's factors, own view and what
  the design showed) and crowd factors (`screening.factors`) for format 4; a mock policy
  `translate_rehearsal_v2` with a path for each new form and refusal. Configs
  `rf31_round1_head_on.yaml` (mock until approved, cap 0) and `rf31_mock_rehearsal.yaml`. Tests:
  `test_rules_schema_v4.py` (39), `test_translation_v4.py` (17). Docs: `rule-format.md` section 15,
  `rule-matching.md`, `rule-translation.md` section 13, `log-schema.md`, `perception.md`.
- Result: the mock rehearsal on RF-11's 16 stored rules completes: 4 valid (2 runnable, 2 extracted
  as needing communication), and each refusal in its category. A bug found on the way: a loop in the
  config reader reused the name `name`, so `--plan` printed a factor as the experiment name; fixed
  before anything ran under it.
- Worst case of the paid run (`--plan`): **USD 0.043** (4 calls, reply cap 2,500, peak, no cache).

## Design decisions in this issue (mine, for the user to check)

Marked as decisions, not instructions: each is an assumption where the issue leaves room.

- **D-A, the form of `own_when`.** A role's directive entry may carry
  `own_when: {when: <condition>, then: {speed_scale, clearance_margin, steps}}`. The entry's other
  fields apply as always; the fields under `then` apply only while `when` holds for that person.
  A field under `then` other than the three is refused as `own_only_scope`, checked before the
  schema so that the reason is plain (as `no_tie_policy` is). One `own_when` per role.
- **D-B, what `own_when` may read.** `self.` fields and `pair.` fields (the person computes both);
  not `either.`/`both.` (it is about the person's own part).
- **D-C, the `self.` fields.** `assertiveness` (gives_way, holds_ground), `urgency` (routine,
  urgent), `residence` (local, visitor), `memory_note` (none, bad_experience), `knows_other` (true
  or false; RF-6's familiarity, acquaintances = true), `finds_other_attractive` (true or false;
  RF-6's matrix entry for this person looking at the other, attractive = true). Missing when not
  designed, and a comparison on a missing value is false.
- **D-D, the snapshot.** Private values go in a part of the snapshot of their own (`private`),
  read only by `own_when` and never by `when` or roles. The two agents' shared snapshot still
  equals what each builds from its own record in everything public; each agent's own
  `own_when` reads only its own private values, so its directive is the same either way.
- **D-E, perception record** (as built; see the progress entry of 13:30). The observer's own core
  factors are in its record's `attributes` when its persona has them; no earlier persona has any,
  so every earlier record is byte for byte as before and `PERCEPTION_SCHEMA_VERSION` stays 3.
- **D-F, visibility switches.** The avoidance config accepts the three new switch names besides
  `default_visibility()`'s; the default dict does not gain them, so earlier configs' recorded
  visibility is unchanged. Unset means off.
- **D-G, steps in the crowd.** Run by a crowd plan driver that reuses `PlanDriver`'s step
  mechanics under `plan_orca` and `keep_line`. A person runs one plan at a time: a match that would
  start a plan while the person's earlier plan still runs is skipped and counted (the policy the
  back-up manoeuvre already has, `rule-matching.md` section 7). After the last step the person
  keeps their line until the pair has passed (or the partner arrived, or the pair closed).
- **D-H, the step vocabulary in a rule.** `start: {at_distance_m}`, `speed_mps`,
  `turn: {to, degrees}`, `sidestep: {to, metres}`, `back_up_m`,
  `until: other_passes | {seconds} | {at_distance_m}`; checked with Step 1's own step parser
  (`reply._step`), so the limits are Step 1's (turn 0 to 90 degrees, sidestep up to 3 m).

- **D-I, rule generation's category for `own_only_scope`**: `needs_communication`. A side, share,
  order or back-up switched on by one person's private factor would need the other to be told it.
  A loader `steps` refusal is `schema_error`.
- **D-J, crowd screening for format 4** gives the crowd core factors in turn (`screening.factors`):
  for RF-31, a cane, a suitcase, a phone and assertiveness each on half the people [design]. Nobody
  in the crowd has a view of another, so an own-only condition on `knows_other` or
  `finds_other_attractive` never holds there; and a suitcase does not widen anyone in a crowd.
- **D-K, the reply cap for `translate_v2`**: 2,500 tokens [placeholder] (RF-12: 1,500), since a
  rule with steps is longer.

## Open questions / risks

- Paid task 9 needs the user's approval and cap recorded in `CLAUDE.md` first.
- Step 1 printed a cane, suitcase or phone only within 5 m (D2); a format 4 rule reads them at any
  distance. A rule conditioned on them may therefore fire earlier than the agents could have seen
  them.
- A step's speed is in m/s, as Step 1's; in a crowd of people with other preferred speeds, an
  absolute speed means something different for each. Kept as Step 1's vocabulary, as the issue
  asks.

## Summary (fill in at the end)
