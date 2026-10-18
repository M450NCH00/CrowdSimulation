# Shortlist for the hands-on trial (PT-5 → PT-6, issue #39 → #40)

**This is a recommendation from a desk survey, not a decision.** The use-or-build decision is
#40's. Track #34's portable-rule idea, which these roles serve, is itself **a proposal that needs
the supervisor's sign-off**. Everything here is `[inference]` from `survey.md` and
`comparison.md`, except where a source is cited.

## The constraint that shapes the list

#40 may install only **released PyPI packages, pinned, in a new virtual environment**. Java and C++
builds are not allowed, and nor is running a cloned repository (#40, "Permission"). Of the
candidates:

| Candidate | Installable from PyPI? |
|---|---|
| JuPedSim | yes, `jupedsim`, with a `win_amd64` wheel (`refs/sim_jps_pypi_1.4.2_summary.txt`) |
| Mesa | yes, `Mesa`, Python ≥3.12 (`refs/sim_mesa_pypi_summary.txt`) |
| SUMO | yes, `eclipse-sumo`, plus `traci` and `libsumo` (SUMO Downloads, "Python packages"). JuPedSim is bundled with the Windows *distribution* (Pedestrians, "Model jupedsim"); whether the pip wheel includes it is `[not documented]` |
| Vadere | no: Java jars (README) |
| Menge | no: C++ build (README) |
| CrowdGym | no: code not shared (`WORK_LOG-39.md`, A2) |

Vadere and Menge can therefore only be judged from the desk, as #40 already anticipates.

## The shortlist

### 1. JuPedSim 1.4.2: the second continuous testbed, and the queue and waiting host

**Why:**
- It differs from negsim where portability can break (`research-gap.md` §3):
  - other motion models: collision-free speed, social force and others, against ORCA;
  - a step ten times smaller: 0.01 s against 0.1 s;
  - infrastructure negsim lacks: journeys, queues, waiting sets (survey §3).
- It is actively released (v1.4.2, 2026-05-21) and installs from PyPI on Windows.
- It is the most likely engine under CrowdGym (survey §2, the JuPedSim question). If so, adapters
  written for it would carry over to the deployment target.

**What #40 must test with it:**

- **Trial 1, a queue with a newcomer:**
  - A `NotifiableQueueStage` of 10 positions, served by `pop(1)` on a timer (the pattern of the
    queues notebook).
  - The newcomer at 30 s. The stage itself cannot insert part-way: agents wait at "the first
    available spot" (routing page, "Waiting Queue"). So test two routes:
    - (a) the newcomer under **direct steering** to the slot ahead of position 3;
    - (b) "refuse" as `switch_agent_journey` into the queue, which should put them at the back.
  - Record whether (a) needs the queue to be rebuilt, and how many lines "admit" takes.
- **Trial 2, a door:**
  - A waiting set on the platform as the waiting crowd. Release it by setting it inactive.
  - Alighting agents added at the door with an exit journey, so that flow goes both ways through
    one opening.
  - Record whether the collision-free speed model **deadlocks** in two-way door flow. That is
    itself a conflict this FYP cares about.
- **Trial 3, the two adapters:**
  - Read every agent's position each iteration, and the queue order with `enqueued()`.
  - Velocity: CFS states expose none (survey §3, "Hooks"). Measure the difference-of-positions
    workaround, or use the social force model, whose state has `velocity`.
  - Mid-run, change one agent's `desired_speed`, and its route (`switch_agent_journey`). Check
    when each takes effect.
  - Check what happens when `agent.target` is set outside a direct-steering journey: the docs
    say it is "ignored".
- **Trial 4, scale:**
  - 1,000 and 10,000 agents, CFS, a plain corridor;
  - report time per iteration **and per simulated second** (100 iterations at 0.01 s), because
    negsim's 1.36–1.60 s per step is per 0.1 s (`WORK_LOG-26.md`);
  - JuPedSim is single-threaded (history page).
- **Determinism:** `Simulation` takes no seed in its signature (API). Check whether two identical
  runs give identical trajectories.
- **Logging:** the SQLite and HDF5 trajectory writers (release notes v1.3.2, v1.4.1).

### 2. Mesa 3.5.1: the discrete queue model

**Why:**
- It is the candidate that differs most in **structure**: discrete space (grid, network), event
  scheduling instead of fixed steps, and no motion model (survey §7). That is the third kind of
  testbed #34, point 6 asks for.
- Queue cutting is a conflict about **order**, not space. A discrete model states arrival order
  and time waited directly, which a continuous simulator can only approximate.
- Pure Python, Apache-2.0, released 2026-03-15 and very active.

**What #40 must test with it:**

- **Trial 1:**
  - The line as an ordered list, or as a `Network` of cells.
  - Service as `schedule_recurring`; the newcomer as `schedule_event(at=30)`.
  - "Admit" and "refuse" as one decision point that the action adapter fills.
  - Record the lines of code. It should be small, because Mesa supplies nothing queue-specific.
- **Trial 2 (optional):** a door as a capacity-one cell, with alighting before boarding as a
  priority rule. This tests whether the *discrete* form of a boarding conflict is expressible,
  not whether it looks right.
- **Trial 3:** perception and action are plain Python. Confirm that a rule engine's Decision can be
  applied inside a scheduled event as easily as inside `step()`.
- **Trial 4:** 1,000 and 10,000 queueing agents, time per event or step.
- **Determinism:** `Model(seed=..., rng=...)` (API "Model"). Check that the same seed gives the same
  event order.
- **API check:** the event-scheduling methods (`run_for`, `schedule_event`, `schedule_recurring`)
  are documented on the stable docs, which mark the older simulator classes "Deprecated since
  version 3.5.0" (API "Experimental"). Confirm that they exist in 3.5.1, not only in a later
  development version.

### 3. SUMO 1.28.0 with JuPedSim: the boarding host. Conditional, third.

**Why:**
- It is the only candidate with vehicles, stops, capacities and boarding built in (survey §4).
- It is the published route by which JuPedSim meets transport ("transfer points" between vehicle
  and walking: coupling page).

**Why it is conditional:**
- SUMO's own boarding is a duration per person (`boardingDuration`, default 0.5 s). Lindner et
  al. 2025 note that standard SUMO "teleport[s] passengers onto the bus" (§3.2).
- In the coupling, waiting positions are "static", and "pedestrians currently do not react to
  vehicles" (coupling page).
- So the door *conflict* itself may have to be built in JuPedSim anyway, as in JuPedSim's trial 2.
- Try SUMO only if JuPedSim's trial 2 shows that a stand-alone door lacks something a vehicle
  model provides: arrival times, capacity, dwell time.

**What #40 must test with it (if tried):**
- **Install:** whether `pip install eclipse-sumo==1.28.0` on Windows includes JuPedSim, i.e.
  whether `--pedestrian.model jupedsim` runs. This is `[not documented]` for the wheel.
- **Trial 2:**
  - A bus with `personCapacity` at a `busStop`, people waiting, some alighting.
  - Do boarders walk to a door inside the JuPedSim area, or vanish on boarding?
  - Is alighting-before-boarding expressible at all?
- **Trial 3:**
  - Over TraCI, read person positions every step.
  - Call `person.setSpeed` and `moveToXY` on a **JuPedSim-modelled** person. Whether either has
    any effect is the survey's main open point for SUMO (survey §4, "Hooks").
- **Trial 1 and trial 4:** skip. There is no pedestrian queue element, and the coupling is
  "runtime-limited" by JuPedSim (coupling page).

## Not shortlisted, and why

- **Vadere:**
  - It would be the best *event-driven continuous* testbed: optimal-steps events, and a
    psychology layer that resembles #34's split (survey §5).
  - But it cannot be installed under #40's permission (Java); its Python wrapper is "Work in
    Progress"; it has no queues or vehicles; and it states that thousands of agents in real time
    are "not yet possible" with the optimal steps model.
  - Keep it as the alternate if the supervisor wants a continuous testbed that differs in *time*
    as well as in motion.
- **Menge:**
  - The best *design reference*: a behaviour FSM over swappable motion models, external event
    triggers, and an aircraft-boarding plug-in (survey §6).
  - But it is dormant since 2019, and C++ only.
  - Read its `ExternalEvtTrigger` and Ped-Air design when the adapters are designed.
- **CrowdGym:** the target, not a trial candidate. Its code is not shared (A2). See Open question
  Q1 in `WORK_LOG-39.md`.
- **pedsim_ros, SteerSuite, RVO2, Sumonity, commercial tools** (survey §8, §9):
  - ROS-only, dormant, the same model as negsim, Unity, or paid.
  - Sumonity's paper and SteerSuite's test cases are worth citing in scenario cards.

## One thing the trials should not decide

Which simulator CrowdGym is built on. If JuPedSim is chosen in #40 *because* of CrowdGym, that
reason rests on the open question in survey §2, and should be stated as conditional until it is
answered.
