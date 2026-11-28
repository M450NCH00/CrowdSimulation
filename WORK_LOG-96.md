# Work Log — Issue #96: [Feature] Viewer: the LLM's decisions, each agent's factors and its view cone in resolution replays

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/96
**Branch:** feat/96-viewer-decisions-factors-view-cone (stacked on `feat/65-rf10-round1-head-on-screening`,
as the RF issues are)
**Started:** 2026-10-25

## Understanding the issue
The user asked (2026-10-25) for the viewer to show, in a replay of a resolution session: the
decision the LLM gave while the agent carries it out (what it wanted and why); every factor of an
agent when it is clicked (age, gender, ethnicity, ...); and each agent's view (the 75° either side,
10 m) shaded in a lighter tone of its colour, with a switch to show or hide it.

A replay folder is an avoidance run (issue #26) whose `config.json` names its session
(`plans.session_id`). The session record (`sessions/<id>.json`) holds the decision points, replies,
debriefs, personas, pairwise factors and `llm_view`; the replay's `outcome.json`
(`plans.driver.decisions`) holds when each plan and each of its steps started and ended, for that
replay's mode. The viewer only reads logs, so nothing about any experiment changes.

## Plan
1. `viewer.py`: find the record from a replay; build `run.llm` (decisions with their step timing
   from the replay, signals, messages, debriefs, view settings) and add factor rows to each
   agent's details; decision and signal events; messages into `run.conversation`.
2. `viewer.html`: an "LLM decisions" panel (in force highlighted); a caption by each agent (intent
   and current step); check boxes for decisions, view cones and hearing range; the cone cut at
   walls by ray casting; the agent's facing as `perceive.py` defines it.
3. Tests on a mock experiment (`run_resolution` with the mock client) in `tests/test_viz.py`.
4. README viewer section and the docstring.
5. Check in a headless browser that the page draws without an error (the self-test), on the
   mock experiment and on a real RF-10 replay.

## Progress log

### 2026-10-25 — Built and checked
- What I did: `viewer.py` reads the session record beside a replay (`session_record`) and adds
  `run.llm` (decisions with each step's start and end from the replay's driver, debriefs, the
  view settings), factor rows to each agent (the replay's "Persona: none" row is dropped for
  them), LLM rows to the run summary, and decision, signal, message and plan-end events;
  messages also go in the Conversation panel. `viewer.html`: the "LLM decisions" panel, a
  caption by each agent (decision in force, step now, a fresh signal), the agent panel's
  decision, step and private reason, and check boxes for captions, view cones (on by default)
  and hearing range (off). The cone is a fan of rays cut at walls (slab test against each wall
  box), 1 ray per degree.
- Decisions I made (small, the user can change them): view cones on by default because the user
  asked to see them; the decision events are moments on the timeline (a span per plan filled the
  whole bar); the "Design cell" row was dropped from the run summary because it pushed the panel
  far down and the factor rows say the same per agent; "plans stop steering" is shown when the
  pair passed or one arrived, and "ORCA takes over" only for a release the protocol asked for
  (none in RF-10).
- Checks: `tests/test_viz_resolution.py` (13 tests, on a mock talk experiment: the record found
  in both modes, step timing from that mode's driver, view settings, events, factor rows, the
  `</script>` escape, a replay without its record unchanged, step wording, trigger wording);
  `tests/test_viz.py` unchanged and passing. Headless Chrome self-test (the page's own
  `#selftest`): an RF-10 talk session (both replays), a mock resolution session, and the older
  avoidance, crowd (100 agents) and negotiation runs, all "ok". Screenshots read by eye.

## Open questions / risks
- The cone is cut by walls only, not by other people (two-person scenes). Said on the page.
- A whole experiment's `replay/` folder cannot be given in one go (it holds session folders, not
  run folders; 576 replays would make a very large page). One session folder at a time.

## Summary
**What changed.** `negsim/viz/viewer.py` and `viewer.html`: a replay of a resolution session
shows the LLM's decisions (a caption by each agent and an "LLM decisions" panel, with when each
step ran in that replay), each agent's factors and debrief when clicked, decision, signal and
message events, and check boxes for captions, view cones (cut at walls) and hearing range.
Runs without a session record are shown as before. `tests/test_viz_resolution.py` (13 tests),
README's viewer section.

**How it was verified.** The new tests and `tests/test_viz.py`; the full `llm_negotiation` suite,
1892 passed and 5 skipped (RF-10 recorded 1879 passed and 4 skipped; the 13 new tests account for
the passes; I did not trace which test the fifth skip is); the page's self-test in headless Chrome
on RF-10 and mock resolution replays and on older run kinds; screenshots read by eye.
