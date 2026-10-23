# Work Log — Issue #60: RF-5: the core factors (seven, including a memory note) with visibility switches, and up to four situational factors

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/60
**Branch:** feat/60-core-factors-visibility-situational (cut from `feat/58-step1-encounter-protocol`, which PR #86 merged into `feat/59-execute-plans-physical-outcomes`; track #55's branches stack, see the memory note on `git checkout main`)
**Started:** 2026-10-23

## Understanding the issue

Step 4 needs more factors than age, gender and errand, so that the factor analysis (RF-8) can
find which ones drive a decision. This issue adds the **core** factors that every round keeps
(D15) and up to four **situational** ones, on the mock only:

- **Seven person attributes**, two levels each: `urgency` (routine, urgent), `mobility_aid`
  (none, cane), `load` (none, large_suitcase), `distraction` (none, phone), `assertiveness`
  (gives_way, holds_ground), `residence` (local, visitor), `memory_note` (none,
  bad_experience). Three are observable (mobility aid, load, distraction), four are not.
- **Where the lines go** (D2): a person's own lines in ABOUT YOU, the memory note in YOUR
  NOTES, what someone else can see of them in WHO YOU CAN SEE (only when that person is in view
  *and* the factor's visibility switch is on), the situational lines in WHERE YOU ARE, the same
  for everyone.
- **`load` widens the body**, fixed from the start of the run (D1: bodies never change size
  during a run).
- **Visibility switches** for the observable ones, as design factors, like
  `demographics_visible`.
- **Design coding:** each factor is "neither agent" or "one agent"; the existing `mapping`
  factor balances which agent.
- **Validation:** a rule reading `assertiveness`, `residence` or `memory_note` is
  `needs_communication`.
- **Tests**, including that everything written before this issue renders exactly as before.

**What I found before planning.**

1. The issue says the lines go into "a new template version, `resolve_v2`". That name is
   taken: RF-17 (#73) froze `resolve_v2` after this issue was written. `resolve_v2`'s own
   provenance already says "Factor lines (RF-5, RF-6) are rendered by their own templates and
   placed here verbatim", and the `View` already has the slots (`Me.factor_lines`, `notes`,
   `SeenPerson.factor_lines`). So the lines go into a **new frozen template of their own**,
   `resolve_factors_v1` (kind `resolution_factors`), and `resolve_v2` renders them unchanged.
   No core template is edited or re-versioned. *A deviation from the issue's wording, recorded
   here; the issue's intent (new wording only in a new frozen template) is kept.*
2. **Task 6 is not true today.** A rule naming `either.assertiveness` is refused as
   `unknown_field`, which `negsim.rulegen.validate` counts as `schema_error`, not
   `needs_communication`. It needs the three attributes in the rule loader's table of
   unobservable fields (`negsim/rules/fields.py`, `UNOBSERVABLE`).
3. **Adding attributes to the persona table changes old records** unless kept out of
   `default_visibility()`: that dict is built from the table and recorded by every avoidance,
   negotiation, rule-generation and resolution run, and two tests pin it exactly. The new
   attributes have their own switches in the resolution design, and the older layers' prompts
   have no line for them, so they are left out of it.
4. `load`'s body can be widened the way `docs/parameters.md`, section 5, already documents for
   linking a persona to a physical change: a per-agent `agents.overrides.<id>.radius` in the
   run's scenario config. The replays must apply the same override, so the session record has
   to carry it.

## Plan

1. **Schema:** declare the seven in `ATTRIBUTES` with their levels (`AttributeSpec.levels`);
   keep them out of `default_visibility()` (both copies); a level value is spelled out in a
   derived persona id, not marked as free text.
2. **Factor template** `resolve_factors_v1.yaml`, a new kind `resolution_factors`, frozen in
   the manifest: the self, other and note lines per level, and the situational lines.
3. **`negsim/resolution/factors.py`:** the situational factors' table, the template loader,
   `SessionFactors` (one session's levels, switches and lines: own, notes, what others see,
   the place), the values config `configs/resolution/factors_v1.yaml` (`load`'s added width,
   `surroundings`' hearing ranges, all `[placeholder]`), and `with_bodies` (the scenario
   override for a wider body).
4. **Views:** `view_in` takes a person's own lines and the situational lines; the protocol
   passes a session's factor lines into every view.
5. **Design:** optional factors, each "neither" or "p1"; `urgency` as the two-level form of
   `task` (one or the other); the visibility switches; the situational factors. A config that
   names none of them gives the same cells, ids, session records and outcome columns as before.
6. **Experiment:** a wider body in the live run, in plain ORCA and in both replays; the
   hearing range of the session's `surroundings`; factor levels in the outcome row; the cost
   preview counts the factor lines.
7. **Validation (task 6):** the three unobservable attributes in `UNOBSERVABLE`.
8. **Tests** (task 8) and a mock rehearsal config with the factors on.
9. **Docs:** `resolution.md`, `parameters.md` (new placeholders), `encounter-protocol.md`,
   `log-schema.md`, the READMEs.

## Progress log

### 2026-10-23 — Start
- What I did: merged PR #86 (RF-3) into `feat/59-...`, closed #58 by hand and ticked it in #55
  (the user's request). Read #60, `resolution.md` (D1, D2, D7, D15, D16), the persona schema and
  loader, `resolve_v2`, the view, perceive, protocol, design, experiment and replay modules,
  `parameters.md` section 8, and the tests that pin the visibility defaults.
- Why: to place each piece of the issue in the code RF-2 to RF-3 left.
- Result / what I found: the four points under "What I found before planning".
- Next step: the schema and the factor template.

### 2026-10-23 — Schema, template, factors module
- What I did: declared the seven in `ATTRIBUTES` (`AttributeSpec.levels`, optional, left out when
  not given); kept them out of both `default_visibility()` copies; wrote and froze
  `resolve_factors_v1` (new kind `resolution_factors`); wrote `negsim/resolution/factors.py`
  (`FactorTemplate`, `FactorValues`, `SessionFactors`, `with_bodies`) and
  `configs/resolution/factors_v1.yaml`.
- Why: the plan's steps 1 to 3.
- Result / what I found: **a mistake of mine, caught by an existing test.** I first froze the
  visibility list into a module constant at import time. `test_the_schema_is_a_table_...` adds an
  attribute with `monkeypatch` and expects `default_visibility()` to pick it up; a constant broke
  that contract. Now filtered at call time, and the constant is gone.
- **Wording changed from the issue's examples** (decision, recorded in the template's provenance):
  the issue's lines named a corridor ("The corridor around you is ...", "in a corridor like this
  one"), and D16 says the pipeline never names a scenario. Now "It is quiet around you." / "It is
  busy and noisy around you." and "... in a place like this one." "Noisy" says what the factor
  changes outside the prompt (the hearing range); the scene is not made busier. Every other line is
  the issue's, word for word.
- Next step: views, protocol, design, experiment, replay.

### 2026-10-23 — Wiring: views, protocol, design, experiment, replays
- What I did: `view_in` takes a person's own lines and the situational lines; the protocol passes a
  session's lines into every view (`EncounterSession(factors=...)`). The design gains optional
  factors (`neither`/`p1`), the switches and the situational factors; `urgency` replaces `task`
  when named. The experiment builds `SessionFactors` per session, widens the loaded body through
  `agents.overrides.<id>.radius` in the run's scenario config, sets the hearing range from
  `surroundings`, records `factors` and `bodies`, adds the levels to the outcome row, and counts the
  factor lines in the cost preview. `replay.run_plan_for` applies the bodies in plain ORCA and both
  replays.
- Why: steps 4 to 6. A config that names no new factor must write exactly what it wrote before:
  cells, cell codes and ids are computed over the factors a cell has, and `as_dict` adds keys only
  when the design uses a new factor (the resume check compares `config.json` with `as_dict`).
- Result / what I found: **`load` does not fit two passage cases.** The first rehearsal stopped at
  `scenario 'passage_meeting': agents 0 and 1 overlap at their starting positions`. I checked every
  head-on, passage and overtaking case with each agent widened (a scratch script): with 0.2 m, only
  `passage_02fac1e4` and `passage_10e542c2` (both "asymmetric") fail; with 0.1 m every case fits. I
  did **not** shrink the placeholder to make a case fit. Instead `plan()` now refuses such a design
  before anything runs, naming the case (`check_bodies`), and the question is below for the user.
  The rehearsal uses `passage_067961e3` instead.
- Next step: task 6, tests, rehearsal.

### 2026-10-23 — Task 6, the rehearsal, the tests
- What I did: added `assertiveness`, `residence` and `memory_note` to the rule loader's
  `UNOBSERVABLE` (`negsim/rules/fields.py`). Left `urgency` out on purpose: `either.urgency` is
  already `needs_communication` (as `private_information`), and a test pins that reason. Ran
  `configs/resolution/resolve_factors_mock_rehearsal.yaml` (24 sessions, all with an encounter,
  1 min). Wrote `tests/test_factors.py` (34 tests).
- Result / what I found:
  - The rendered prompts hold every line in the block D2 says (checked by eye on a head-on
    session: ABOUT YOU, YOUR NOTES, WHERE YOU ARE for both people; the 70-year-old visitor is
    told "Your body is 0.70 m wide").
  - Person 2 sees the cane, the suitcase and the phone of person 1 when within 5 m; with
    `load_visible: false` only the cane and the phone. Person 1 sees nothing of person 2 (base
    levels).
  - `python -m negsim.resolution.replay ... --verify` rebuilds both replays of a loaded session
    byte for byte; their `config.json` shows radius 0.35 m for the loaded agent.
  - **A switched-off load still shows as width:** WHO YOU CAN SEE gives every person's body
    width, so the hidden suitcase person is "0.70 m wide". That is the body the simulator moves,
    so it is told truthfully; documented (`parameters.md`, 8.7).
  - **Observable lines only within 5 m:** from 5 to 10 m `resolve_v2` prints one short line per
    person (D2), with no factor lines. A cane 8 m away is not mentioned. Documented, not changed
    (it would need a new core template).
  - **"give way" in the assertiveness line.** The issue's line "You are easy-going and tend to
    give way." contains a phrase on issue #32's list of words that hint at a way of settling a
    meeting. Here the disposition is the factor itself, and the line appears only when a design
    varies assertiveness, so I kept the issue's wording and exempted only that phrase for that
    attribute in the new wording test. Flagged below.
  - Four of my first tests were wrong (a `radius_m` key, tuples in an in-memory record, a test
    that gave both people the same hidden levels so it could not tell them apart, and the
    wording exemption above); fixed, 34 pass.
- Next step: docs, full suite.

### 2026-10-23 — Situational factors: the session's choice (task 7)
- **Chosen: `surroundings` (quiet, busy) and `time_of_day` (daytime, late_night).**
  - `surroundings` is the one candidate that also acts on the talk condition, through the hearing
    range that RF-17 already said should depend on it (`parameters.md`, 8.4).
  - `time_of_day` changes nothing physical, so it tests whether the setting alone moves a
    decision. Late at night, wariness of a stranger is plausible.
- **Not chosen: `companion`.** The simulator moves one disc per person. "You are walking with a
  friend" describes a pair and a width the replay does not have, and the LLM may plan for both
  (for example "we both move over"). The confound between prompt and physics would be larger than
  for any other factor. It would need a group model first.
- **Two slots left free** of RF-7's 16: D15 lets each round add its own factors (a pram on the
  train, for example). Note the count: the issue's 12 person factors plus these 2 make 14,
  *without* the visibility switches (`demographics_visible`, three `<name>_visible`) and `mapping`,
  which are also two-level design factors. RF-7 has to decide whether those count against the 16.

### 2026-10-23 — Docs
- What I did: `resolution.md` (built so far, D2 and D7 as built, D12's hearing range, D15), a new
  `parameters.md` section 8.7 (three placeholders and the design values), `rule-format.md` (the
  three fields), `encounter-protocol.md` (outcome columns, section 9), `log-schema.md` (`factors`,
  `bodies`, change log; no version change), both READMEs.
- Result: while writing 8.7 I checked my Pearsons locators against the cached file and corrected
  two (department stores is `:1146`, not `:1145`). The inside-urban homes value is unreadable in
  the scan ("JIB.0"), so the doc cites only the 41 dB of suburban homes and conclusion 2(d)'s
  45 dB.

### 2026-10-23 — The user's decision: new passage cases (option b)
- **Decision (the user, 2026-10-23, after reading PR #87):** option (b), new passage cases whose
  pair starts further apart, rather than leaving cases out or shrinking the width.
- **What I found first: it was all eight cases, not two.** Every `si32_passage_v1` case starts the
  pair exactly 0.1 m apart, body to body (measured: centres 0.6 m apart). With 0.2 m added, the
  asymmetric ones overlap by about 1e-16 m and the symmetric ones are apart by about 1e-16 m.
  Rounding alone made four of them "fit", touching. My earlier report of "6 of 8 fit" was wrong.
  So `check_bodies` now also refuses a loaded body that starts closer to anyone than the
  scenario's near-miss distance (0.1 m); with that, all eight are refused, and the head-on and
  overtaking cases still fit.
- **What I did:**
  - Two new source experiments, `configs/cases/rf5_source_passage_meet_middle.yaml` and
    `..._with_speeds.yaml` (new files; issue #32's untouched). They repeat issue #32's layouts
    with each person 0.1 m less far in: [1.6, 1.6], [2.6, 0.6], [1.9, 1.3]. The pair starts
    0.3 m apart, 0.2 m with one person loaded. *Design choice, mine:* 0.1 m less each, so that
    a loaded pair is a whole near-miss distance clear of the near-miss line, and the layouts
    stay recognisably issue #32's.
  - For [1.9, 1.3] I checked by the arithmetic of `derivations.md` section 18 that the
    distance-optimal and the time-optimal choice of who backs out still differ (agent 1 by
    distance, 3.8 m against 5.0 m; agent 0 by time, 2.7 s against 4.4 s).
  - Committed the configs first, so that the runs record a clean tree. Ran both (16 runs, no
    model). Extracted `rf5_passage_v1` with `configs/cases/rf5_passage_cases_v1.yaml`, whose rules
    are issue #32's word for word: 8 cases, all T3. `python -m negsim.rulegen.cases check`
    passes.
  - All eight take a loaded person under both mappings (tested). The rehearsal now uses
    `passage_36a66c39` and ran 24 of 24.
- **A difference to know about:** issue #32's at-rest cases deadlocked under plain ORCA (T4).
  With 0.3 m of room, plain ORCA creeps the pair past each other in 12 to 39 s, so every new
  case is T3. Round 2's passage conflicts are a little less severe than issue #32's, and results
  on the two sets are not comparable number for number. Documented in `cases.md`, section 9.

## Open questions / risks

1. ~~**`load` in round 2.**~~ **Decided by the user (2026-10-23): new passage cases**, built as
   case set `rf5_passage_v1` (above). What remains: these cases are T3 where issue #32's at-rest
   ones were T4 (above), and a design that varies `load` must use them, while a design that does
   not can use either set. Round 2 (RF-19, #75) chooses which.
2. **Three new placeholders** (`parameters.md`, 8.7): the suitcase's 0.2 m, and the quiet (8.9 m)
   and busy (3.2 m) hearing ranges. The hearing ranges use cited inputs with an assumed
   background for each level.
3. **"give way" in the assertiveness line** (the issue's wording). It names an outcome, as a
   disposition. If the supervisor reads it as steering the decision, a `resolve_factors_v2` could
   say "You are easy-going." / "You are determined." instead.
4. **Prompt-only physics.** A cane does not slow the agent, a phone does not narrow its view, a busy
   place has nobody in it. A factor's effect is an effect on the decision only (documented). If
   RF-8 finds, say, that the cane changes plans, a replay still walks at full speed.
5. **Rule fields.** A rule cannot read the observable factors (mobility aid, load, distraction)
   either: they are not in the perception record, so a rule naming them is `unknown_field`
   (`schema_error`). Whether they become rule fields is for RF-11 and RF-12.
6. **Counting factors for RF-7** (above): 14 named factors plus switches and `mapping`.
7. **A switched-off load still shows as width** (above). If the switch is meant to hide the load
   entirely, the width line would have to go too, which `resolve_v2` cannot do without a new
   version.

## Summary (fill in at the end)

**What changed.**
- Seven core factors are in the persona table, rendered from a new frozen template
  (`resolve_factors_v1`) into the blocks of D2.
- The three observable ones have visibility switches, as design factors.
- Two situational factors: `surroundings` (which also sets the hearing range) and `time_of_day`.
- `load` widens the body for the whole run, and the live run, plain ORCA and both replays all use
  that body.
- The design codes each factor as `neither` or `p1`; `urgency` is the two-level form of `task`.
- A rule reading `assertiveness`, `residence` or `memory_note` is `needs_communication`.
- A config that names none of the new factors writes exactly what it wrote before.
- After the user's decision: a new case set, `rf5_passage_v1`, with room for a wider body, and a
  plan-time check that refuses a loaded body starting within the near-miss distance.

**Why.** Issue #60 and `docs/resolution.md`, D1, D2, D7 and D15.

**How it was verified.**
- 34 new tests in `tests/test_factors.py`.
- Full suite: 1641 passed and 1 failed. The failure was `test_repo_hygiene`'s check on imports:
  `test_factors.py` imports helpers from three other test modules, which that test's list of local
  modules did not name. I added the three names, and the hygiene tests then passed (7). The
  rule's purpose, to catch unpinned third-party packages, is unchanged.
- A 24-session mock rehearsal, with the prompts checked by eye.
- The replays rebuilt with `--verify`, byte for byte.
- No paid call.

The open questions above are for the user, the first one especially.
