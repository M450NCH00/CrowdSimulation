# Work Log — Issue #73: RF-17: what an LLM agent perceives: view cone, occlusion, hearing, changes since it last looked

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/73
**Branch:** feat/73-llm-agent-perception-view (cut from `feat/57-resolve-templates-view-parser`, which PR #83 merged into `docs/72-record-resolution-design`; track #55's branches stack, see the memory note on `git checkout main`)
**Started:** 2026-10-23

## Understanding the issue

RF-2 (#57) defined the `View`, everything one LLM agent is told at one decision point
(`docs/resolution.md`, D2), and built it only for the snapshot of a frozen two-person case. This
issue builds the `View` from the **running simulation**, the way a person in the agent's place
would perceive it:

- **seen:** everyone whose centre is within 75° of the agent's heading and 10 m, not hidden
  behind a nearer person's disc or (switchable) a wall; full detail within 5 m, one short line
  beyond; no fixed count (`max_people` is an optional cost cap that records what it left out);
- **heard:** speech since the last decision point, from anyone within the hearing range, from
  any direction; an unseen speaker is "someone" with a rough direction and a distance band;
- **signals:** only if the observer could see the signaller when it was made (eye contact and
  nod also within an eye-contact range);
- **changes since you last looked** (D5 thresholds), **time to meet** (only when the closest
  approach is inside the safety distance), **history lines** (own earlier intents and what came
  of them);
- **stable labels** for the whole encounter;
- a config block `llm_view` with sourced values and marked placeholders.

It changes **only what the LLM is told** (D10): ORCA's neighbour search and the perception
record rules read stay byte for byte as they are.

Out of scope: when agents are prompted (RF-3), carrying out plans (RF-4), any change to ORCA or
the perception record. Paid calls: none.

## Plan

1. Branch, work log (this file).
2. Read `resolution.md` (D2, D5, D10, D12), `perception.py`, `simulation.py`, `perception.md`,
   `parameters.md`, architecture DD8, and RF-2's `negsim/resolution/`.
3. **Template:** `resolve_v1` cannot word task 4 (an unseen speaker is always "Someone behind
   you") or task 8 (the history says only finished or ongoing). Asked the user; they chose a new
   version, `resolve_v2`: `resolve_v1` word for word plus only the missing lines. `resolve_v1`
   stays as it is, and views still render through it.
4. `configs/resolution/llm_view_v1.yaml` (the `llm_view` block, tagged) and its loader.
5. `negsim/resolution/perceive.py`: sight (cone, range, occlusion by discs and walls), hearing,
   signals, changes, time to meet, history, labels; a builder that reads a running
   `AvoidanceSimulation` without changing it.
6. Tests: the list of task 9, plus "building views every step leaves a run byte for byte the
   same".
7. Docs (`parameters.md` section 8, `resolution.md`, READMEs), full test suite, push, PR
   (targets `feat/57-resolve-templates-view-parser`), comment on #73.

## Progress log

### 2026-10-23 — Read the issue, the spec and the code
- What I did: closed #57 by hand (PR #83 merged into a stacked branch), ticked it in #55, read
  #73 and everything in its "Before starting" list, and RF-2's package.
- Result / what I found:
  - **`resolve_v1` falls short of tasks 4 and 8**, although its provenance says it holds lines
    for every block RF-17 fills: `heard_unseen` is fixed as "Someone behind you says", which is
    false for a speaker hidden ahead or beyond the seeing range ahead, and has no distance band;
    `history_outcome` is only "finished" or "still carrying out". A signal on a short (5 to 10 m)
    line has no wording either. **Decision (the user's, 2026-10-23): add `resolve_v2`.**
  - Sight through walls already has a switch in the world (`World.mutually_visible`,
    architecture DD8); RF-17 uses the same segment-through-rectangle test.
  - The conflict zone's safety distance is the two radii plus the scenario's
    `single_file.safety_margin` (`negsim.conflict.detection.ConflictDetector.clearance`).
- Next step: the config and `perceive.py`.

### 2026-10-23 — `resolve_v2`, written, previewed, frozen
- What I did: copied `resolve_v1` to `resolve_v2` and added only `heard_unseen_from` (with
  `heard_directions`, `heard_bands`), `seen_short_signal`, `history_sideways`,
  `history_no_sideways`, `history_back` and the outcome `replaced`. Taught the renderer to use
  each line only when the template has it. Before freezing, rendered a head-on and an overtaking
  run from the unfrozen file and read every prompt: the person ahead in the overtaking case is
  told `- Someone behind you, close by, says: "Excuse me."` and sees nobody; the overtaker's
  wave does not reach them. Then frozen: `resolve_v2` cea7f2d6….
- Why: the user's decision above. The system message (the fixed text) is `resolve_v1`'s byte
  for byte, so a cached prefix is the same under both.
- **The outcome `replaced` is my addition**, beyond the issue's wording: at the third decision
  point the first decision's steps were replaced by the second's before they ended, and neither
  "finished" nor "still carrying out" is true of them. `resolve_v1` refuses to render it
  (`ConfigError`), rather than say something false.

### 2026-10-23 — `negsim/resolution/perceive.py` and `configs/resolution/llm_view_v1.yaml`
- What I did: the settings (`LLMViewSettings`, every value tagged), `Body` (a person as they
  physically are), sight (`in_cone`, `hidden`, `in_sight`), hearing (`voice_from`), the
  `Exchange` (what was said and signalled, and who perceived each, **as it was when it
  happened**), `Perceiver` (one agent across one encounter: labels, last look, decisions,
  `look` and `decided`), `changes_since`, and the simulation side (`bodies_in`,
  `safety_distance`, `own_record`, `perceiver_for`, `view_in`).
- Decisions I made that the issue left open (all **my assumptions**, open to change; also in
  `parameters.md` 8.3):
  1. **Placeholder values:** hearing 7 m, "close by" within 3 m, eye contact and nod within 4 m.
     Round values, none sourced; the change thresholds are D5's 0.2 m, 0.2 m/s and 5°.
  2. **Where a person faces:** their direction of travel; when standing still or walking
     backwards, the direction of their path where they are. The simulator turns a disc to face
     its velocity, so an agent backing out of a passage would otherwise "look" away from the
     person it is backing away from.
  3. **"Moved over to your left"** is how far the other is off the straight line they were on at
     the last look, along the observer's left now. Someone crossing at a steady angle has not
     moved over.
  4. **The rough direction of a voice:** four quarters (ahead, behind within 45°, else left or
     right), as it was when the words were said. **Walls do not stop sound.**
  5. **The cap keeps the encounter partner** even when more than `max_people` are nearer.
  6. **The time to meet** uses the safety distance of the conflict zone (two radii plus the
     scenario's `single_file.safety_margin`, 0.1 m in every shipped scenario), and is given only
     for the encounter partner.
  7. **Changes are worked out for everyone seen at both looks**, but `resolve_v1` and `v2` render
     them only on full-detail lines, as RF-2 did; a short line stays one line (D2). A signal on a
     short line is the exception, in `v2`.
  8. **What came of a decision** is the net displacement since, against the way the agent faced
     then: sideways (stated even when nil) and further back (stated when more than 0.05 m). What
     became of its steps (finished, still going, replaced) is passed in: carrying out plans is
     RF-4's.
  9. **The WHERE YOU ARE lines** come from a perception record built for the purpose with the
     run loop's own function, `perception.perceive`, handed to the scenario plug-in and dropped.
     Nothing is stored in the simulation.
- Next step: tests.

### 2026-10-23 — Tests
- What I did: `tests/test_perceive.py` (79 tests): everything in task 9, the config's tags and
  placeholders against `parameters.md`, every path of hearing and signals, the history lines,
  and from the running simulation: a run with views built every 7 steps against a plain run in
  five scenarios (trajectory, every interaction with its perception record, pairs, back-ups,
  goal times, collisions: one JSON string each, equal), views rendered through `resolve_v1` and
  `resolve_v2` in every condition with none of RF-2's order, convention or group words, a view
  with every block of D2 filled, and a 100-person crowd.
- Two tests first used the wrong scenario: the plain head-on run and the open crossing both end
  in deadlock (they are exactly symmetric), so nobody arrives; the arrival test uses the
  overtaking run, which completes. In the two-way crowd, agent 0 sees nobody until about step
  100, when the two crowds have closed in.
- Checked that `resolve_v1` renders as before: RF-2's 336 renders (every two-person case, both
  agents, every condition, the opening and a full view) hashed in a temporary worktree of
  `feat/57-resolve-templates-view-parser` and on this branch: both `02b881ba…`. The worktree was
  removed.

## Open questions / risks

- **Q1. The new placeholders** (hearing 7 m, close by 3 m, eye contact 4 m) are round numbers
  of mine. RF-5's `surroundings` factor is meant to set the hearing range; until then every
  result that depends on who heard what rests on a placeholder.
- **Q2. Walls do not stop sound**, and a voice's direction is one of four quarters. Both are
  simplifications; a scenario with someone speaking round a corner would need more.
- **Q3. Facing while backing or standing** (decision 2) changes who an agent sees compared with
  the disc's own heading. The perception record that rules read still uses the disc's heading
  (`perception.heading_of`), so the LLM's view and the record can disagree about what is
  "ahead" for an agent that is backing up. That is D10's split, but worth knowing in RF-4.
- **Q4. `replaced`** is an outcome the issue did not name (see above). RF-4 has to say, for
  every earlier decision, which of the three applies.
- **Q5. Only two-person encounters are tested end to end**, with a crowd view as a check that
  views scale. Rounds 4 and 6 prompt more than two people (D11); the `Perceiver` takes one
  partner, so those builds will need a set of partners.
- No paid call was made; `spend_ledger.jsonl` is untouched.

### 2026-10-23 — Verification
- Full suite: `uv run --no-project --python 3.13 --with pytest==9.1.1 --with PyYAML==6.0.3
  --with matplotlib==3.10.8 python -m pytest` in `llm_negotiation/`: **1530 passed, 1 failed**
  (468 s). The failure was `test_repo_hygiene.py::test_only_pinned_third_party_packages_are_imported`:
  `test_perceive.py` imports RF-2's word lists from `test_resolution`, which the hygiene test
  took for a third-party package. Added `test_resolution` to its local modules, as `test_llm`
  already is; that file, `test_perceive.py` and `test_resolution.py` then **157 passed**. So
  1531 of 1531.
- `pyflakes` on `negsim/resolution/`: clean.
- `git diff` of `negsim/avoidance/` against the base branch: empty.
- Docs: root `README.md` (RF-17 row), `llm_negotiation/README.md` (roadmap item, a section
  "What an LLM agent perceives (issue #73)", a "Changing things" row, the Documents line),
  `docs/resolution.md` (what is built), `docs/parameters.md` section 8.

## Summary

**What changed.** `negsim/resolution/perceive.py` (new) builds an LLM agent's `View` from the
running simulation: the 75° cone and 10 m range, occlusion by nearer discs and (switchable)
walls, full detail within 5 m, an optional `max_people` cap that records what it left out,
stable labels, hearing from any direction (an unseen speaker is "someone" with a rough direction
and a distance band), signals only if seen when made, changes since the last look against D5's
thresholds, the time to meet inside the safety distance, and history lines saying what came of
each decision. Its values are in `configs/resolution/llm_view_v1.yaml`, every one tagged. A new
frozen template, `resolve_v2` (the user's choice), is `resolve_v1` plus only the lines `v1`
could not say; `resolve_v1` is untouched and still renders every view. The `View` gained
optional fields (`Heard.direction`, `Heard.band`, `Done.sideways_m`, `Done.back_m`) and the
outcome `replaced`.

**Why.** Issue #73 (RF-17): an agent is to be told what a person in its place would perceive,
not everyone around it, and changes only what the LLM is told (D10).

**How it was verified.** 79 new tests (task 9's list; the config against `parameters.md`; a
watched run byte for byte equal to a plain run, perception records included, in five scenarios;
views from five scenarios and a 100-person crowd through both templates in every condition); RF-2's
336 `resolve_v1` renders hashed equal on the base branch and here; the full suite passes (1531).

**Acceptance criteria.**
- [x] Views are built from the simulation for every block of D2, and render through
  `resolve_v1` (and `resolve_v2`, which words what `v1` cannot).
- [x] Every placeholder is marked as one in the config and in `parameters.md` (tested).
- [x] Existing runs, baselines and perception records are unchanged, and the full test suite
  passes.
