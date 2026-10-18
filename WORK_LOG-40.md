# Work Log — Issue #40: [Research] PT-6 Simulators, part 2: hands-on trial of the shortlist, and the use-or-build decision

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/40
**Branch:** docs/40-simulator-hands-on-trial
**Started:** 2026-10-18

## Understanding the issue

Track #34 proposes (not agreed; needs the supervisor's sign-off) that extracted rules become
portable: a rule core over a fixed vocabulary, two adapters per simulator, and tests on unseen
scenarios such as queue cutting and boarding. #39 surveyed simulators from the desk and
shortlisted JuPedSim, Mesa and (conditionally) SUMO. This issue tries them by hand and decides,
for each role (second continuous testbed, discrete testbed, boarding host), between
**(a) use**, **(b) refer and build** and **(c) hybrid**.

Four trials per simulator where they apply: a queue with a newcomer; a bus or train door; the two
adapters in miniature; scale at 1,000 and 10,000 agents. For each: what worked, code size,
determinism, logging. Deliverables: `integration/simulator-survey/hands-on.md`, `decision.md`,
`spikes/` (throwaway code, pinned requirements).

**Base branch.** Track #34 branches stack on the previous issue's branch, because `origin/main` is
still at the initial commits. This branch is cut from `docs/39-simulator-desk-survey` (PR #47,
open), which holds the shortlist this issue needs.

## Plan

1. Read `shortlist.md` and `comparison.md` (done before branching).
2. Ask the user whether the standing supervisor instruction (`README.md`, "Status of that
   instruction: unconfirmed") allows throwaway trial code. Record the answer **before** any install.
3. Create a new venv (outside `llm_negotiation/`, gitignored), install pinned `jupedsim` and
   `mesa` from PyPI only. Record exact versions and the Python version.
4. JuPedSim: trials 1, 2, 3, 4; determinism; logging.
5. Mesa: trials 1, 2 (optional), 3, 4; determinism; API check of the event-scheduling methods.
6. SUMO: only if JuPedSim's trial 2 shows a stand-alone door lacks what a vehicle model gives.
7. Write `hands-on.md`, then `decision.md` (matrix with proposed weights, recommendation marked as
   a proposal).
8. Check `llm_negotiation/` is untouched and its tests pass. Push, PR against the #39 branch.

## Progress log

### 2026-10-18 — Start
- What I did: read issue #40, `shortlist.md`, `comparison.md`, the `README.md` standing
  instruction and `WORK_LOG-39.md` Q1. Created the branch from `docs/39-simulator-desk-survey`.
- Result / what I found: prerequisite met (`shortlist.md` exists on the #39 branch). #39's Q1
  (whether `ntu-fyp-25/crowdgym` is the senior's and may be read) has no answer on the issue, so I
  do not open that repository. Python 3.12 and 3.13 are installed (Mesa 3.5.1 needs ≥3.12).
- Next step: ask the user the standing-instruction question.

### 2026-10-18 — The user's answers (before any install)
- What I did: asked the user two questions with the question tool.
- Result:
  - **A1. Standing instruction.** Question: does the standing supervisor instruction (no
    simulation or experiment code until the literature review is complete and discussed;
    `README.md`, status unconfirmed) allow throwaway trial code for #40? **Answer: "Yes,
    proceed".** The instruction's status with the supervisor stays unconfirmed, as in #24 to #32;
    this answer is the user's, not a recorded supervisor approval.
  - **A2. CrowdGym repository (#39 Q1).** Question: may I read `ntu-fyp-25/crowdgym`? **Answer:
    "Leave it unopened".** So whether CrowdGym is built on JuPedSim stays open, and the "fit with
    CrowdGym" criterion in `decision.md` is stated as conditional.
- Next step: new venv, pinned wheels only.

### 2026-10-18 — Install
- What I did: `py -3.13 -m venv integration/simulator-survey/spikes/.venv` (gitignored by the
  existing `.venv/` rule), then `pip install --only-binary=:all: jupedsim==1.4.2 mesa==3.5.1`.
  `--only-binary=:all:` refuses source distributions, so no setup or build script can run.
  `pip freeze` → `spikes/requirements.txt`.
- Result / what I found:
  - **`import mesa` failed** with `ModuleNotFoundError: No module named 'networkx'`.
    `mesa/__init__.py` imports `discrete_space.network`, which imports `networkx`, but Mesa 3.5.1's
    metadata lists `networkx` only under extras (`network`, `all`, ...). Fixed by pinning
    `networkx==3.7` (wheel). A packaging defect in Mesa 3.5.1, worth one line in `hands-on.md`.
  - JuPedSim's wheel pulled in PySide6, VTK and matplotlib (its visualiser dependencies). Large,
    but all wheels.
  - **Shortlist API check passes:** Mesa 3.5.1 has `Model.run_for`, `run_until`, `schedule_event`
    and `schedule_recurring`, and `Model(seed=..., rng=...)`. `Model.__init__` registers a default
    recurring `step` every 1.0 time unit (`mesa/model.py:184-190`).
- Next step: JuPedSim trial 1.

### 2026-10-18 — JuPedSim trial 1 (queue with a newcomer)
- What I did: `spikes/jps_trial1_queue.py`: 10 people on a `NotifiableQueueStage`, `pop(1)` every
  10 s, a newcomer beside position 3 at 30 s. Tried four routes.
- Result / what I found:
  - **refuse** (newcomer switched into the queue journey): works; JuPedSim sends them to the back.
  - **steer** (direct steering to the gap ahead of position 3): the newcomer wedges beside the
    line at (3.19, 3.51), is never enqueued and never served. Physical cutting-in is invisible to
    the queue.
  - **admit by switching journeys** (positions ≥3 step out under direct steering, the newcomer
    joins, they rejoin): **failed**; the newcomer still ended at the back. First I switched all of
    them in one go; then one at a time, each after the previous was enqueued. Same result.
  - **Root cause, by probe** (`spikes/jps_probe_queue_switch.py`): `switch_agent_journey` does
    **not** remove an agent from the queue's `enqueued()` list. Agent 3 walked 2 m away and stayed
    listed; the agents behind it did not move up. The entry went only when it was popped.
  - **admit by remove and re-add** (`mark_agent_for_removal`, then `add_agent` in the new order):
    **failed** too. Removed agents' ids also stay in `enqueued()` and keep their slots, and the
    re-added agents were enqueued by arrival at the queue (nearest first: P10, P9, NEW, P8, ...),
    not by add order.
  - **So JuPedSim 1.4.2's queue stage is FIFO only: join at the back, leave at the front.** Neither
    insertion (admit) nor leaving mid-queue (reneging, being sent away) can be expressed with it.
    `[inference]` The stale entries look like a defect, not a design choice; I did not check
    JuPedSim's issue tracker.
  - **admit with our own queue** (`spikes/jps_trial1_ownqueue.py`): the queue order is a Python
    list; every queuer is on a direct-steering journey and steered to the slot of its index each
    iteration. Admit = `list.insert(2, ...)`, refuse = `list.append(...)`. **Works:** the newcomer
    is in slot 3 at (3.6, 3.0) within 2 s, the people behind step back, the minimum spacing stays
    ≥0.795 m, and the newcomer is served at 60 s (three pops after arriving third).
- Decision point: this is route (b) "refer and build" in miniature: JuPedSim for motion, our own
  queue logic. It is the route I take for trial 2 and the adapters.
- Next step: trial 2 (door).

## Open questions / risks

## Summary (fill in at the end)
