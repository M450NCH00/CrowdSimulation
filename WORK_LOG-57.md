# Work Log — Issue #57: RF-2: Step 1 templates (independent, non-verbal, talk) and a debrief, the View structure, the scenario interface, and the reply parser

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/57
**Branch:** feat/57-resolve-templates-view-parser (cut from `docs/72-record-resolution-design`, as track #55's branches stack; see the memory note on `git checkout main`)
**Started:** 2026-10-22

## Understanding the issue

Step 1 of track #55 asks whether LLM agents can resolve a conflict, and how, without being
asked for a rule. This issue writes the prompts an agent is shown and reads its replies, as
`llm_negotiation/docs/resolution.md` (D1 to D3, D8, D16) decides:

- a `View`: everything one agent is told at one decision point, block by block (D2);
- a scenario plug-in interface, description side (D16), with the passing scenarios of rounds
  1 to 3 in one frozen scenario template `scenario_passing_v1.yaml`;
- a core template `resolve_v1.yaml` with one section per condition (independent, non-verbal,
  talk) and a debrief template `resolve_debrief_v1.yaml`, frozen with the existing tool;
- a reply parser (D1) and a debrief parser (D8), with one retry;
- mock policies `resolve_paths_v1` and `debrief_paths_v1`, and tests.

Out of scope: views from the running simulation (RF-17), carrying out plans (RF-4), running
sessions (RF-3), new persona factors (RF-5, RF-6). Paid calls: none.

## Plan

1. Branch, work log (this file).
2. Templates: `scenario_passing_v1` (the place lines of `rulegen_negotiate_v2` word for word,
   the three passing events), `resolve_v1` (role, per-condition instructions and reply format,
   every D2 block's lines, the decision-point wrapper), `resolve_debrief_v1`. Register three
   new template kinds in `prompts.TEMPLATE_KINDS` (adding kinds changes nothing for the
   existing templates). Freeze the three with `negsim.negotiation.freeze`.
3. `negsim/resolution/`: `view.py` (the `View` and its blocks, rendering), `scenario.py`
   (`Scenario` base, `PassingScenario`), `adapter.py` (first decision point of a frozen
   two-person case), `prompt.py` (messages for a decision point, the debrief), `reply.py`
   (reply and debrief parsers), `mock.py` (the two mock policies).
4. Tests: render every case in every condition; nothing the agent cannot perceive; no
   convention words; no "first"/"priority"; every parser path; the fixed text byte-identical
   across agents and decision points; a toy second scenario defined only in the tests.
5. Full test suite; the existing templates must still render byte for byte as before.
6. Push, PR (targets `docs/72-record-resolution-design`), comment on #57.

## Progress log

### 2026-10-22 — Read the issue, the spec and the existing code
- What I did: read #55 (track), #57, `docs/resolution.md`, `prompts.py`, `parsing.py`,
  `freeze.py`, `rulegen/describe.py`, `rulegen/mock.py`, the `request_with_retry` helper of
  `negotiation/protocol.py`, and the case files.
- Why: the issue's "Before starting" list.
- Result / what I found:
  - #56 and #72 are merged, so #57 is the next unchecked issue of #55's order.
  - **The frozen cases' snapshots are often not a decision point under D2.** The head-on and
    bottleneck cases are frozen at 12.3 to 12.4 m apart and the crossings at 11.3 to 11.7 m,
    beyond D2's 10 m seeing range; in the overtaking cases the person ahead has the other
    straight behind them (bearing about 180°), outside the 75° cone; the passage cases are at
    0.6 m. The 16 `flow_*` files are pairs out of 100-person crowds. So the adapter applies
    D2's cone and ranges as written, and an agent who sees nobody is told so; the real first
    decision point is found by RF-3's trigger (D4), not by this adapter.
- Next step: write the templates.

### 2026-10-22 — Templates written, previewed, then frozen
- What I did: wrote `scenario_passing_v1`, `resolve_v1` and `resolve_debrief_v1`; added three
  kinds (`resolution`, `resolution_debrief`, `resolution_scenario`) to
  `prompts.TEMPLATE_KINDS`. Before freezing, rendered a passage, a head-on and an overtaking
  case from the unfrozen files with a scratch script and read every prompt.
- Why: once frozen, any wording change needs a new version.
- Result / what I found: three wording fixes made before freezing (so no version was spent on
  them): "Say what you do from now on, as the way you move" read badly and became "...: how
  you move"; "The other people" became "Other people"; the debrief rendered `"Go left.".` with
  a doubled full stop, so the intent and the steps went on two lines. Then frozen with
  `python -m negsim.negotiation.freeze`:
  `scenario_passing_v1` f3ca88c2…, `resolve_v1` 58555439…, `resolve_debrief_v1` 1c23e5a7….
- Next step: the package and the tests.

### 2026-10-22 — `negsim/resolution/` and its tests
- What I did: `view.py`, `scenario.py` + `scenarios/passing.py`, `prompt.py`, `adapter.py`,
  `reply.py`, `mock.py`; `tests/test_resolution.py` (71 tests).
- Decisions I made that the issue left open (all **my assumptions**, open to change):
  1. **"first" and "priority" are tested strictly**, as substrings of everything an agent is
     shown. To make that possible the step format says "the opening step", not "the first
     step", and the wrapper keys are `opening` and `again`.
  2. **The fixed text is the system message**: role, the condition's instructions and reply
     format, and the step format with the scenario's events. The agent's top speed is in
     ABOUT YOU ("The fastest you can walk is 2.00 m/s"), not in the fixed text, so the fixed
     text stays the same for every agent.
  3. **Every decision point is one fresh two-message request** (system + description); earlier
     decisions reach the agent through WHAT YOU HAVE DONE SO FAR, not through a growing chat.
     The "again" wrapper says the new reply replaces whatever is left of the earlier steps
     (RF-3/RF-4 must carry out plans that way).
  4. **The non-verbal and talk instructions say "You may be asked again later, if something
     changes."**; the independent ones do not (one decision point, D3). True of the protocol,
     but it may change how agents plan; flagged for review.
  5. **`until` is required on every step except one that walks backwards**, which ends when it
     has walked back that far; a speed or turn on a back-up step is ignored and flagged (D1:
     backing is at the agent's backing speed). Missing `until` elsewhere is a parse failure
     (`missing_until`), beyond the issue's list, because a step with no end has no meaning.
  6. **A missing `reason` is not a failure**: `""`, flagged `no_reason`. An unknown key inside
     a step is tolerated and flagged (`unknown_step_key:...`).
  7. **`start.at_distance_m` is read against "the person you would meet"**: the person of the
     time-to-meet line, else the nearest person in view. With nobody in view it is a parse
     failure (`start_at_distance_with_nobody_in_view`).
  8. **Time to meet = time of closest approach** (`-(r.v)/(v.v)`), not the record's time to
     collision, which is `None` when two people would pass without touching
     (`head_on_ff0aa402`). Added to `parameters.md` 8.3.
  9. **The debrief continues the agent's last decision point** (its prompt, its raw reply,
     then D8's question with every intent and step), so the agent knows what is being asked
     about and the provider can reuse the cached prefix.
  10. **The visibility switches hide age and gender for both people**, as
      `rulegen.describe` does for `demographics_visible`.
  11. **The crowd cases (`flow_*`, 100 people) are refused** by the adapter: the issue asks for
      a two-person adapter and the record describes only the pair. RF-17 builds crowd views.
      So "every case in `cases/`" is tested as every two-person case (28 files) plus a test
      that the 16 crowd files are refused.
- Result: 71 new tests pass.
- Next step: check the old templates and run the full suite.

### 2026-10-22 — Verification
- What I did:
  - Rendered every pre-existing template (rulegen v1 and v2, both conditions, all three case
    sets, demographics shown and hidden; the negotiation templates for three scenes): 534
    renders, hashed together, in a temporary worktree of `docs/72-record-resolution-design`
    and on this branch. Both `b97b717e…`: byte for byte the same. The worktree was removed.
  - Full suite: `uv run --no-project --python 3.13 --with pytest==9.1.1 --with PyYAML==6.0.3
    --with matplotlib==3.10.8 python -m pytest` in `llm_negotiation/`: **1452 passed** (300 s).
  - `pyflakes` on `negsim/resolution` and the test file: clean.
- Docs: `README.md` (RF-2 row), `llm_negotiation/README.md` (roadmap item, a short section
  "Step 1 prompts (issue #57)", a "Changing things" row for adding a scenario, the Documents
  line), `docs/resolution.md` (what is built), `docs/parameters.md` (turn limit placeholder,
  time-to-meet definition).

### 2026-10-22 — Pushed, PR #83
- Pushed `feat/57-resolve-templates-view-parser`; opened PR #83 against
  `docs/72-record-resolution-design` (the stacked base, as PR #82 targeted `docs/56-...`).
  `Closes #57` does not fire on a merge into a non-default branch, so #57 may need closing by
  hand. Commented on #57 with the PR link and Q1.

## Open questions / risks

- **Q1. The frozen cases' snapshots are mostly not decision points.** Head-on and bottleneck
  cases at 12.3-12.4 m, crossings at 11.3-11.7 m (beyond 10 m); the person being overtaken
  cannot see the overtaker. Their opening views say "You do not see anyone nearby." RF-3 needs
  to step a case forward to D4's trigger (or extract cases at the trigger) before any of them
  is sent to a model. Not a defect of this issue, but it decides RF-3's design.
- **Q2. "You may be asked again later"** (decision 4 above) is in the frozen non-verbal and
  talk text. If the user prefers agents not to know, that is `resolve_v2`.
- **Q3. Placeholders used:** the 0-90° turn range (`MAX_TURN_DEGREES`, added to
  `parameters.md` 8.2). The hearing range and eye-contact range are not used here (RF-17).
- **Q4. Factor lines** (RF-5, RF-6) are placed verbatim from whatever template renders them;
  `resolve_v1` has no wording of its own for them. If RF-5 wants them in the core template,
  that is a new core version.
- **Q5. `Me.max_speed_mps` comes from the case's `bodies`**, which the agent is now told
  ("The fastest you can walk is …"). Telling the agent its top speed is needed for the
  speed range of the reply, but it is new information compared with issue #32's prompts.
- No paid call was made; `spend_ledger.jsonl` is untouched.

## Summary

**What changed.** `negsim/resolution/` (new): the `View` of D2, the scenario interface of D16
with the passing plug-in, the renderer, the opening-view adapter for frozen two-person cases,
the reply parser of D1 and the debrief parser of D8 (both raise `TurnParseError`, so issue
#24's `request_with_retry` gives one retry), and the mock policies `resolve_paths_v1` and
`debrief_paths_v1`. Three frozen templates: `resolve_v1`, `resolve_debrief_v1`,
`scenario_passing_v1`. `prompts.TEMPLATE_KINDS` gained three kinds; nothing else in the
existing code changed.

**Why.** Step 1 of track #55 (#57): the prompts and reply reading for asking LLM agents to
resolve a conflict, with no reply field about who goes first.

**How it was verified.** 71 new tests (every two-person case in every condition, at the
opening and at a later decision point with every block filled; nothing the agent cannot
perceive; no convention, "first" or "priority" wording; the fixed text byte-identical; every
parser and debrief path; every mock path through the retry helper; a toy queue scenario
through the unchanged core template). The full suite passes (1452). The 534 renders of the
existing templates are byte for byte as on the base branch.

**Acceptance criteria.**
- [x] The core, debrief and passing-scenario templates are frozen and render for every case and
  condition (every two-person case; the crowd cases are refused by design, Q1/decision 11).
- [x] A second scenario can be added without editing the core template or the parser.
- [x] Parser and mock tests pass.
- [x] Every existing template still renders byte for byte as before, and the full test suite
  passes.
