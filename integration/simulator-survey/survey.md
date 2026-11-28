# Simulator desk survey (PT-5, part 1; issue #39)

How each candidate simulator works, read from its documentation, papers and source on GitHub or
GitLab on **2026-10-18**. **Nothing was installed, cloned-and-run or executed.** The use-or-build
decision is #40 (PT-6); this file only describes.

Track #34's idea, which this survey serves, is **a proposal, not agreed, and needs the
supervisor's sign-off**: a portable rule core, with two adapters per simulator (a *perception
adapter* from simulator state to a Situation, and an *action adapter* from a Decision to the
simulator's own controls).

## Conventions

- **Sources.** Each statement names its source:
  - a documentation page and its heading;
  - a paper section;
  - or a file and line at a stated commit.
  The cached copy is in `refs/`. For source files, line numbers are those of the file in the
  repository at the commit given; a cached copy has a three-line header, so its own line numbers
  are 3 higher. Repository metadata is in `refs/sim_gh_*.json` / `refs/sim_gl_*.json`.
- **`[not documented]`**: I looked in the pages and files listed for that simulator and did not
  find it. This is not proof that the feature is absent.
- **`[inference]`**: my reading, not a statement in the source.
- **`[not checked]`**: could not be looked at (CrowdGym; see §2).
- **"Recent activity"** = commits on the default branch since 2026-04-18 (six months). The API page
  holds 100, so "100" means "at least 100".
- **The two adapters**, as the survey uses them:
  - *perception*: outside code reads every agent's state on every step;
  - *action*: outside code changes an agent's target, speed or route during a run.

## Contents

1. [negsim](#1-negsim-this-repository) · 2. [CrowdGym](#2-crowdgym-the-seniors-fyp) ·
3. [JuPedSim](#3-jupedsim) · 4. [SUMO + JuPedSim](#4-sumo-with-its-jupedsim-coupling) ·
5. [Vadere](#5-vadere) · 6. [Menge](#6-menge) · 7. [Mesa](#7-mesa) ·
8. [Lower priority: pedsim_ros / libpedsim, SteerSuite, RVO2, Sumonity](#8-lower-priority) ·
9. [Commercial tools](#9-commercial-tools)

---

## 1. negsim (this repository)

**Version read:** `llm_negotiation/docs/architecture.md` §1, §6.1, §6.2, as last changed at
`05490dd`. As the issue asks, described from those sections only; the code was not re-read.

- **Links:** `llm_negotiation/` in this repository; `llm_negotiation/docs/architecture.md`.
- **Licence; last release; recent activity:**
  - licence: none is stated for negsim in §1, §6.1 or §6.2;
  - `LICENSES/` holds third-party notices (§1 layout). For example, `lp.py` is "Adapted from
    RVO2, with its notice" (§6.1);
  - releases: none. It is built issue by issue (#24, #26, #28, #30, #32: `architecture.md`
    opening paragraph).
- **Language and API; Python bindings; Windows support:**
  - Python. "The simulator, both clients and the logging use only the Python standard library.
    PyYAML reads the configs; matplotlib is needed only for the optional plot" (§1).
  - Developed and benchmarked on Windows 11 (`WORK_LOG-26.md`, entry 2026-10-14 09:15).
- **Motion models** (§6.1, Dynamics and ORCA rows):
  - two dynamics models, `UnicycleDynamics` (issue #24) and `HolonomicDynamics` (ORCA);
  - ORCA half-planes solved by a linear program adapted from RVO2.
  - The negotiation runs use a path-tracking controller under a speed bound (§1, `control/`).
- **Behaviour or decision layer:**
  - A `DirectiveProvider` turns a `PerceptionRecord` into an `AvoidanceDirective` whenever a new
    neighbour appears (§6.2, step 1; §6.1, Perception and Directives rows).
  - `resolve_pair` combines a pair's two directives into shares, side, clearance and leader
    (§6.2, step 2).
  - The arbiter holds pairs at single-file segments (§6.2, step 3).
  - The rule layer supplies directives from a rule database (§1, `rules/`).
- **Space and time:**
  - continuous 2D: positions, discs, wall blocks, half-planes (§6.1);
  - a fixed time step, "every time step, for every agent that has not arrived, all from the same
    state" (§6.2);
  - `dt` is 0.1 s in the crowd scenarios (`llm_negotiation/configs/scenarios/bidirectional_flow.yaml:14`)
    and 0.2 s in the doorway (`doorway.yaml:10`).
- **Scenario description:** "scenario YAML -> ScenarioSpec (agents, walls, paths, region)" (§1);
  crowd scenarios use `schema_version: 2` (§6.1, Scenarios row); experiments are YAML too (§1).
- **Native support:**
  - **queues** ✗;
  - **waiting areas** ✗ as an element `[not documented]` in §1, §6.1, §6.2;
  - **service points** ✗;
  - **vehicles and boarding** ✗. Issue #39 itself: "a simulator that can host queues, service
    points and vehicles, which negsim cannot". §5 lists "Queue-cutting, non-spatial conflicts" as
    not there;
  - **groups:** a fictional *attribute* group exists (issue #32, `architecture.md` opening
    paragraph), but not groups that walk together `[not documented]`;
  - **scripted events** `[not documented]`.
- **Hooks for the adapters:**
  - **perception:** `perceive` builds a versioned `PerceptionRecord` (§6.1, Perception row).
  - **action:**
    - an `AvoidanceDirective` from the `DirectiveProvider` interface (§6.1, Directives row);
    - the directive's fields reach motion as share, side and clearance (§6.2, steps 2 and 4);
    - `speed_scale` scales the preferred speed (§6.2, step 4);
    - the arbiter's bound caps it (§6.2, step 3).
  - **per-step callback:** none is needed; the run loop is this project's own code
    (`AvoidanceSimulation`, §6.1).
- **Scale reported:** 10,000 agents at 1,364 to 1,602 ms per step, on one thread of an AMD
  Ryzen 5 7535HS laptop. That is "about 0.06 to 0.07 of real time". 1,000 agents took 143 to
  148 ms per step (`WORK_LOG-26.md`, entry 2026-10-14 09:15, benchmark table).
- **Fit for this FYP** `[inference]`:
  - the reference point;
  - today's rules are, in #34's terms, already the "ORCA binding";
  - the first simulator to get a perception adapter (around `perceive`) and an action adapter
    (around `DirectiveProvider`);
  - not a host for queues, service points or vehicles.

---

## 2. CrowdGym (the senior's FYP)

**Version read:** the repository's own distillation only:
- `integration/crowdgym_mapping.md`;
- `dataset/schema/README.md`.

At the start of this issue the user was asked whether the CrowdGym report or code could be shared.
The answer (2026-10-18) was **"Can't share now"**. Everything else here is therefore `[not checked]`.

- **Links:**
  - the report: Goh Chen Wei, NTU AY2025/26 (`CLAUDE.md`). The PDF lies outside this repository;
  - code: not available to this survey;
  - a GitHub search for "crowdgym" lists a public repository **`ntu-fyp-25/crowdgym`** (Python,
    last updated 2026-06-11; search-log query G13). It was **not opened**, because of the user's
    answer. Whether it is the senior's code is unknown (Open question Q1 in `WORK_LOG-39.md`).
- **Licence; last release; recent activity:** `[not checked]`.
- **Language and API; Python bindings; Windows support:**
  - the mapping's adapter is "the only Python that touches CrowdGym's API"
    (`crowdgym_mapping.md:4-6`), so CrowdGym has a Python API;
  - an "in-progress **C++ port**" exists (`crowdgym_mapping.md:6`; `dataset/schema/README.md:22-24`);
  - Windows support: `[not checked]`.
- **Motion models:**
  - "the physical movement model (CFS — the senior found it less jittery at exits)"
    (`crowdgym_mapping.md:100-101`);
  - "less jittery" implies at least one other model was compared `[inference]`, but which is
    `[not checked]`.
- **Behaviour or decision layer:**
  - an overridable `RL_take_action`. The senior "added exit-selection by overriding
    `RL_take_action` and leaving the rest of the step untouched" (`dataset/schema/README.md:52-53`);
  - it returns an `(N, 3)` array, `[move_x, move_y, delta_facing]` per agent
    (`crowdgym_mapping.md:87-98`; `dataset/schema/README.md:65-66`);
  - route choice is by an `AgentJourneyDirector` with a "weighted-distance method"
    (`crowdgym_mapping.md:105-111`).
- **Space and time:**
  - fixed steps: durations are converted as "`steps = fps * seconds`" (`crowdgym_mapping.md:66-67`).
    So there is a frame rate `[inference]`;
  - continuous 2D: actions are 2D velocities, and agents have a side and a front radius
    (`crowdgym_mapping.md:31-37, 90-98`) `[inference]`.
- **Scenario description:**
  - a Spawner with a list of `AgentType`s, each with a distribution weight and the parameters
    `Speed`, `Tau`, `Mass`, `Radius side`, `Radius front` ("CrowdGym report, Table I";
    `crowdgym_mapping.md:22-37`; `dataset/schema/README.md:31-43`);
  - the senior's verification scenarios include Bottleneck, Corner and Crossflow
    (`crowdgym_mapping.md:46-47`);
  - file format: `[not checked]`.
- **Native support:**
  - journeys and exits ✓ (`crowdgym_mapping.md:105-111`);
  - queues, waiting areas, service points, vehicles and boarding, groups, scripted events:
    `[not checked]`.
- **Hooks for the adapters:**
  - **action:** `RL_take_action`, called every step, returns every agent's velocity and turn.
    That is the action adapter's natural attachment point (`crowdgym_mapping.md:87-103`, where the
    planned handler overrides "the desired velocity / target offset").
  - **perception:** the planned trigger needs each agent's neighbours, heading, closing speed,
    own speed and passage width (`crowdgym_mapping.md:52-58`). So state must be readable inside
    the handler `[inference]`.
  - The note says to "Confirm exact class/method names against the CrowdGym source before
    implementing" (`crowdgym_mapping.md:124-127`). So even the names are unverified.
- **Scale reported:** `[not checked]`. The project's goal is 10,000 agents (`CLAUDE.md`).
- **Fit for this FYP** `[inference]`:
  - the deployment target (#34, point 6);
  - its `RL_take_action` already has the shape of an action adapter (one call per step, every
    agent's command out);
  - it cannot be assessed further without the code.

### Is CrowdGym built on JuPedSim? Left open.

**Answer: not settled by what is in this repository.** The evidence is clues, in both directions.

**Pointing towards JuPedSim, or at least its vocabulary:**

1. *Journeys.* CrowdGym routes with an `AgentJourneyDirector` and "journeys"
   (`crowdgym_mapping.md:105-111`). JuPedSim's routing is built from "Journeys" of stages
   (`refs/us_jupedsim_routing.txt`, "Journeys"; §3 below).
2. *CFS.* CrowdGym's movement model is "CFS" (`crowdgym_mapping.md:100`). JuPedSim's main model is
   the Collision-Free Speed model, `CollisionFreeSpeedModel` (JuPedSim "Pedestrian Models" page).
   The JuPedSim-in-SUMO coupling has tested only that model (`sumo.dlr.de/docs/jupedsim.html`,
   NOTE).
3. *The speed.* The senior's verification speed of 0.8 m/s is recorded as "a JuPedSim default for
   model-to-model comparison" (`crowdgym_mapping.md:44-45`).
4. *Scenario names.* JuPedSim's documentation has notebooks called "corner",
   "double-bottleneck" and "model-comparison" (cached as `refs/sim_jps_notebooks_corner.txt`,
   `..._double-bottleneck.txt`, `..._model-comparison.txt`). The corner and double-bottleneck
   notebooks use `CollisionFreeSpeedModel`.

**Pointing away, or not fitting:**

1. *The 0.8 m/s default.* In JuPedSim 1.4.x, 0.8 m/s is the default `desired_speed` only of
   `SocialForceModelAgentParameters`. The collision-free speed models and the generalised
   centrifugal force model default to 1.2 m/s (JuPedSim API reference, the
   `CollisionFreeSpeedModelAgentParameters` and `SocialForceModelAgentParameters` signatures).
   So "CFS at a JuPedSim default of 0.8" does not match the current release. It could match an
   older release, a different model, or a notebook `[inference]`.
2. *The AgentType parameters.* In JuPedSim, `mass` belongs to the generalised centrifugal force
   and social force models, and `tau` to the generalised centrifugal force model (the social
   force model's is `reaction_time`). Neither belongs to the CFS model, whose parameters are
   `time_gap`, `desired_speed`, `radius`, ... (same API reference).
   - "Radius side" and "Radius front" are not JuPedSim parameter names `[not documented]`.
   - The nearest are the generalised centrifugal force model's ellipse semi-axes `a_v`, `a_min`,
     `b_min`, `b_max`.
   - A parameter set mixing these suggests either several models behind one `AgentType`, or a
     different implementation `[inference]`.
3. *The RL interface.* `RL_take_action`, an `(N, 3)` action array and a `delta_facing` turn
   command have no counterpart in JuPedSim's API. JuPedSim offers no per-step callback and no
   facing control: §3, "Hooks". CrowdGym therefore wraps or replaces whatever moves its agents
   `[inference]`.

**What would settle it** (any one is enough):
- CrowdGym's dependency list (`requirements.txt` / `pyproject.toml`), or an `import jupedsim` in
  its source;
- or the report's implementation chapter (the section that describes the physics engine);
- or the senior's confirmation.

If the public `ntu-fyp-25/crowdgym` repository is the senior's and may be read, its dependency
file would answer this in minutes (Open question Q1).

---

## 3. JuPedSim

**Version read:**
- documentation "stable" at https://www.jupedsim.org/stable/, fetched 2026-10-18. Its model list
  (CFS V3, WarpDriver) is that of v1.4.x, and the latest release is v1.4.2;
- source at `master` `6d559df` (2026-10-16).

- **Links:**
  - site: https://www.jupedsim.org/stable/
  - repository: https://github.com/PedestrianDynamics/jupedsim
  - citation: Zenodo DOI 10.5281/zenodo.1293771 (linked from the docs index page; the link is
    not in the cached text, which keeps text only)
- **Licence; last release; recent activity:**
  - licence: LGPL-3.0 "or any later version" (`LICENSE` at `6d559df`). GitHub reports
    `NOASSERTION` (`refs/sim_gh_pedestriandynamics_jupedsim.json`);
  - last release: **v1.4.2, 2026-05-21**. Before it: v1.4.1 (2026-05-05), v1.4.0 (2026-04-29),
    v1.3.2 (2026-02-27) (GitHub releases, `refs/sim_jps_gh_releases.txt`);
  - activity: 100 commits since 2026-04-18 (at least; the API page holds 100); last push
    2026-10-16.
- **Language and API; Python bindings; Windows support:**
  - a C++ core behind a Python API. "Core functionalities ... have been implemented as essential
    components in C++", and JuPedSim "operates as a library based on Python" (docs "JuPedSim"
    history page, "Balancing performance..." and "Empowering with Python-API");
  - a C API too, which SUMO uses (`sumo.dlr.de/docs/jupedsim.html`, Introduction);
  - single-threaded: "JuPedSim now operates single-threaded" (history page, "Balancing
    performance");
  - Python bindings: the package *is* the Python API. PyPI 1.4.2 requires Python ≥3.10, <3.15
    (`refs/sim_jps_pypi_1.4.2_summary.txt`);
  - Windows: a `win_amd64` wheel exists for 1.4.2 (same file).
- **Motion models** (docs "Pedestrian Models"; API reference `Simulation(model=...)`):
  - Collision-Free Speed in three variants: V1 with global parameters, V2 per-agent, V3 with
    rotational steering;
  - the Anticipation Velocity Model;
  - the Generalized Centrifugal Force Model;
  - the Social Force Model;
  - WarpDriver.

  Added over the releases: CFS V2 in v1.1.0, Social Force in v1.2.0, AVM in v1.3.0, CFS V3 and
  WarpDriver in v1.4.0 (release notes).
- **Behaviour or decision layer.** One `iterate()` call runs, in order
  (`libsimulator/src/simulation.cpp:96-132` at `6d559df`):
  1. agent removal;
  2. neighbourhood search;
  3. the **strategical** decision system (journeys);
  4. the **tactical** decision system (routing);
  5. the **operational** decision system (the motion model);
  6. a second neighbourhood update;
  7. the clock advance.

  Behaviour is specified as **journeys**: networks of **stages** (waypoint, exit, waiting queue,
  waiting set, direct steering) linked by **transitions**. Transitions are fixed, weighted
  round-robin, or least-targeted (`refs/us_jupedsim_routing.txt`, "Stages", "Transitions"; API
  `Transition`).

  Anything beyond that is the user's Python between iterations. Direct steering "should allow for
  rapid prototyping of high level agent behaviour such as waiting or queueing ... user will be able
  to use their own logic written in python" (release notes v1.2.0).
- **Space and time:**
  - **continuous**: "a simulation of pedestrian movement over a continuous walkable area" (API
    `Simulation` docstring). The walkable area is "one simple ... polygon", with holes as
    obstacles (docs "Geometry", "Walkable area");
  - the geometry can be switched during a run (`switch_geometry`; release v1.1.0);
  - **fixed time step**, default `dt = 0.01` s (API `Simulation` signature). "No automatic stop
    condition exists" (API `Simulation` docstring).
- **Scenario description:**
  - **Python code** against the API: geometry via Shapely or WKT, stages, journeys, agents with
    model parameters (API `Simulation.add_*`; the notebooks);
  - the earlier XML configuration was replaced by the Python API (history page, "Empowering with
    Python-API");
  - output: SQLite or HDF5 trajectory writers (release notes v1.3.2, v1.4.1);
  - a scenario file format: `[not documented]` in the pages read.
- **Native support:**
  - **queues** ✓: `add_queue_stage(positions)`. Agents wait at the first free spot and move up
    when others leave; `pop(n)` releases the first *n* (API `NotifiableQueueStage`;
    `us_jupedsim_routing.txt`, "Waiting Queue");
  - **waiting areas** ✓: `add_waiting_set_stage(positions)`, filled in order. It is active or
    inactive; switching it to inactive releases everyone (API `WaitingSetStage`,
    `WaitingSetState`; routing page, "Waiting Set");
  - **service points** ~: no service element `[not documented]`. A queue that a script pops at a
    service rate stands in for one; the queues notebook pops one agent per gate on a timer
    (`refs/sim_jps_notebooks_queues_waiting.txt`, the `while` loop calling `queue_gates[i].pop(1)`)
    `[inference]`;
  - **vehicles and boarding** ✗ in JuPedSim alone `[not documented]`. Through SUMO, see §4;
  - **groups** `[not documented]`. "group" does not occur in the API reference;
  - **scripted events** ~: no event system `[not documented]`. Between iterations a script can add
    or remove agents, switch an agent's journey, switch the geometry, pop queues, or toggle waiting
    sets (API `add_agent`, `mark_agent_for_removal`, `switch_agent_journey`, `switch_geometry`).
- **Hooks for the adapters:**
  - **reading state:**
    - `sim.agents()`, `sim.agent(id)`, `agents_in_range(pos, d)` and `agents_in_polygon(poly)`;
    - each `Agent` has `position`, `orientation`, `journey_id`, `stage_id`, `target`, and its
      model's state, e.g. `desired_speed` (API `Agent`, `Simulation`);
    - queue and waiting-set occupancy: `enqueued()`, `waiting()`, `count_targeting()`.
    - **velocity is not exposed for every model.** `SocialForceModelState` has `velocity` and
      `GeneralizedCentrifugalForceModelState` has `speed`. The collision-free speed model states
      list `desired_speed`, `radius`, `time_gap` and the repulsion parameters, but no current
      velocity (API, the `...ModelState` classes). With CFS, a perception adapter would have to
      difference positions between iterations `[inference]`.
  - **setting targets:** `agent.target = (x, y)` "directly steer[s] an agent towards the given
    coordinate". But this works only for an agent in a journey whose only stage is a
    DirectSteering stage; otherwise "any change will be ignored" (API `Agent.target`;
    `add_direct_steering_stage`).
  - **setting routes:** `switch_agent_journey(agent_id, journey_id, stage_id)` (API).
  - **setting speeds:** per-agent model parameters, e.g. CFS V2's `desired_speed`, "can be set
    individually ... and can be changed at any time" (docs "Pedestrian Models", CFS section).
  - **caveat:** "currently there are no checks done when setting properties on an Agent instance"
    (API `Agent`, Note).
  - **per-step callback:** none. The user's loop calls `iterate()` (API `Simulation.iterate`;
    every notebook's `while ...: simulation.iterate()`). So:
    - the **perception adapter** reads agents between `iterate()` calls;
    - the **action adapter** writes targets, journeys and per-agent speeds there `[inference]`;
    - the loop is ours, as in negsim.
- **Scale reported:** not stated in the pages read.
  - The repository has a `performancetest/` folder (repository tree at `6d559df`), but its
    numbers were not read.
  - SUMO's page says JuPedSim's 0.01 s resolution "makes it the runtime-limiting factor in coupled
    simulation scenarios" (`sumo.dlr.de/docs/jupedsim.html`, Introduction).
- **Fit for this FYP** `[inference]`:
  - the strongest candidate for the **second continuous testbed**. It differs from negsim in:
    - the motion models (CFS, social force and others, against ORCA);
    - the step (0.01 s against 0.1 s);
    - having infrastructure (journeys, queues, waiting sets);
  - a host for **queue and waiting scenarios**, but not for queue *cutting* as a stage behaviour
    (already noted in `literature/unseen-scenarios/scenario-standards.md`, [JuPedSim-1.4.2]).
    Joining part-way along a queue, or admitting or refusing a newcomer, would have to be built
    from direct steering;
  - possibly CrowdGym's engine (§2).
  - To build: the loop; the perception adapter (agents → Situation); the action adapter (Decision
    → target / journey / `desired_speed`); queue cutting via direct steering.

---

## 4. SUMO with its JuPedSim coupling

**Version read:**
- documentation at https://sumo.dlr.de/docs/, fetched 2026-10-18. The latest release on the
  Downloads page is **1.28.0** (tag `v1_28_0`);
- coupling source `src/microsim/transportables/MSPModel_JuPedSim.cpp` at `main` `2285bbc`
  (2026-10-18).

- **Links:**
  - coupling: https://sumo.dlr.de/docs/jupedsim.html
  - pedestrians: https://sumo.dlr.de/docs/Simulation/Pedestrians.html
  - repository: https://github.com/eclipse-sumo/sumo
- **Licence; last release; recent activity:**
  - "SUMO is licensed under the EPL-2.0 with GPL v2 or later as a secondary license option"
    (Downloads, "Note on Licensing"). The standard Windows build has no GPL code; the "extra"
    build does (same section);
  - last release: 1.28.0 (Downloads page);
  - activity: 100 commits since 2026-04-18 (at least); last push 2026-10-18
    (`refs/sim_gh_eclipse-sumo_sumo.json`).
- **Language and API; Python bindings; Windows support:**
  - C++ simulator;
  - control by **TraCI**, a TCP client/server protocol (TraCI page, "SUMO startup"), or by
    **libsumo**, in-process and API-compatible (Libsumo page);
  - Python: `pip install eclipse-sumo`, or only `traci`, `libsumo` or `sumolib` (Downloads,
    "Python packages / Virtual environments");
  - Windows: an installer and a zip (Downloads, 1.28.0). On Windows "the latest release of
    JuPedSim is distributed together with the SUMO software distribution" (Pedestrians, "Model
    jupedsim");
  - libsumo with `sumo-gui` "does not work on Windows" (Libsumo, "Limitations").
- **Motion models for people:**
  - `nonInteracting`, `striping` (the default) and `jupedsim` (Pedestrians, "Pedestrian Models");
  - with JuPedSim, the coupling code can select `CollisionFreeSpeed`, `CollisionFreeSpeedV2`,
    `GeneralizedCentrifugalForce` and `SocialForce` (`MSPModel_JuPedSim.cpp:72-79`);
  - but "only the CollisionFreeSpeedModel has been tested extensively so far" (coupling page,
    NOTE), and "its parameters aren't fully exposed" (Pedestrians, "Model jupedsim").
- **Behaviour or decision layer:**
  - a person's **plan**: a sequence of stages, `walk`, `ride` and `stop` (Specification/Persons,
    "Persons" and the three stage sections);
  - plans can come from intermodal routing (Persons, "Person plans can also be generated with
    intermodal routing");
  - for JuPedSim agents, "Rerouters — placed on SUMO edges — define probabilistic next-waypoint
    options" (coupling page, "Technical Background");
  - no decision layer beyond plans and rerouters `[not documented]`.
- **Space and time:**
  - SUMO is a road and sidewalk **network** of edges and lanes. `striping` puts people on lane
    stripes, 0.65 m wide by default (Pedestrians, "Model striping");
  - with JuPedSim, people move in a **continuous 2D walkable area** made from the pedestrian
    network plus extra polygons of type `jupedsim.walkable_area` (Pedestrians, "Model jupedsim");
  - time: a **fixed step**, 1 s by default, settable from 0.001 s to 1.0 s (Simulation/Basic
    Definition, "Defining the Time Step Length");
  - in the coupling, each SUMO step runs `DELTA_T / myJPSDeltaT` JuPedSim iterations, then maps
    positions back onto edges (`MSPModel_JuPedSim.cpp:412-417, 452-491`; coupling page,
    "Technical Background", "typically 0.01 seconds").
- **Scenario description:**
  - **XML**: the network, plus route files with `<person>` plans (Persons, example);
  - additional polygons for JuPedSim (Pedestrians, "Model jupedsim");
  - a walkable area "either via the DXF import tool or by drawing in netedit" (coupling page,
    "Configuration Possibilities").
- **Native support:**
  - **queues** `[not documented]` as a pedestrian element;
  - **waiting areas** ✓:
    - waiting persons at a `busStop`, whose layout is set by `waitingWidth` and `waitingDepth`
      (Public Transport, "Bus stops");
    - at crossings and traffic lights, SUMO's links become active or inactive JuPedSim waiting
      positions. "at the time of writing, these waiting positions are static" (coupling page,
      "Technical Background"; code `MSPModel_JuPedSim.cpp:542`);
  - **service points** ~:
    - a `stop` stage with a duration (Persons, "Stops");
    - "vanishing zones at exits to model ticket control at venues according to the capacity of an
      entrance system" (coupling page, "Configuration Possibilities"; code
      `MSPModel_JuPedSim.cpp:570`);
  - **vehicles and boarding** ✓:
    - `ride` stages on bus and train lines (Persons, "Rides");
    - a vehicle's `personCapacity`, and `boardingDuration`, default 0.5 s, "The time required by a
      person to board and deboard the vehicle" (Definition of Vehicles, "Available vType
      Attributes");
    - "the stop is extended by the 'boardingDuration' of the vehicle or until the 'personCapacity'
      is reached" (same page, "Stops and waypoints");
    - door positions are used only when *exiting*: "The value doors is currently only used when
      exiting a train or bus" (Public Transport, "Access Lanes");
    - in the coupling, "coupled transfer points where agents switch from a vehicle (bus, cars or
      train) to walking or vice versa" (coupling page);
    - but "pedestrians currently do not react to vehicles" in shared space (coupling page,
      "Technical Background");
  - **groups** ~: "id of the travel group. Persons with the same group may share a taxi ride"
    (Persons, ride attributes); not groups that walk together `[not documented]`;
  - **scripted events** ✓: through TraCI, rerouters and traffic lights.
- **Hooks for the adapters:**
  - **per-step loop:** with TraCI the client calls `simulationStep`, and "the simulation does not
    advance to the next step until all clients have called the 'simulationStep' command" (TraCI,
    "Multiple clients"). Subscriptions deliver chosen variables every step (TraCI,
    "Subscriptions");
  - **reading state:** person `position` and `speed` (TraCI/Person Value Retrieval);
  - **setting speeds:** `setSpeed` "Sets the maximum speed in m/s for the named person for
    subsequent step" (TraCI/Change Person State);
  - **setting positions:** `moveToXY` (same page);
  - **setting routes:** `appendStage`, `replaceStage`, `removeStage`, `rerouteTraveltime` (same
    page);
  - **for JuPedSim-modelled persons:** the coupling reads each agent's position from JuPedSim
    after every SUMO step (`MSPModel_JuPedSim.cpp:452`). It changes JuPedSim's speed only to
    follow lane speed limits (`:491`). Whether `moveToXY` and `setSpeed` reach a JuPedSim agent is
    `[not documented]` in the pages and file read.
- **Scale reported:**
  - not stated for pedestrians in the pages read. GitHub describes SUMO as "designed to handle
    large networks" (`refs/sim_gh_eclipse-sumo_sumo.json`);
  - the coupling's runtime is limited by JuPedSim's 0.01 s step (coupling page, Introduction).
- **Fit for this FYP** `[inference]`:
  - the only candidate with **vehicles, stops and boarding** built in. The natural host for the
    bus and MRT boarding scenario cards;
  - but SUMO's own boarding is a time cost per person (`boardingDuration`), not a crowd at a door.
    Lindner et al. 2025 say the same from experience: "Traditional SUMO workflows teleport
    passengers onto the bus" (§3.2; §8 below);
  - the coupling's waiting positions are static, and pedestrians ignore vehicles;
  - so a boarding *conflict* (who goes through the door first, alighting before boarding) would
    still be played out in JuPedSim's 2D area, with SUMO supplying the vehicle and its timing;
  - heavy to learn for one scenario family. A boarding testbed could instead use JuPedSim alone,
    with a scripted "door" waiting set (§3).

---

## 5. Vadere

**Version read:**
- **v4.0** (2026-04-07; `CHANGELOG.md` and the GitLab tag);
- source at GitLab `master` `4c53f1c` (2026-09-29);
- the site https://www.vadere.org/ (fetched 2026-10-18);
- Kleinmeier et al. 2019, *Collective Dynamics* (CC BY 4.0, `refs/sim_vadere_kleinmeier2019_cd.txt`);
- the psychology-layer paper Kleinmeier, Köster & Drury 2020, already cached
  (`refs/pr_arxiv_2005_12712v2_kleinmeier.txt`) and summarised in
  `literature/portable-rules/representations.md`, [Kleinmeier-Cooperation].

- **Links:**
  - site: https://www.vadere.org/
  - repository: https://gitlab.lrz.de/vadere/vadere, with a GitHub copy at
    `pedestrian-dynamics-HM/vadere` (at v4.0, `917aeaf`)
  - paper: doi:10.17815/CD.2019.21
- **Licence; last release; recent activity:**
  - licence: LGPL (`README.md:130`; Download page, "Vadere is Open Source");
  - last release: v4.0, 2026-04-07 (`CHANGELOG.md:28`);
  - activity: GitLab "last activity" 2026-10-16. The GitLab API counted 100 commits since
    2026-04-18 (`refs/sim_gl_vadere_vadere.json`; see search log on this count); the head merge was
    on 2026-09-29.
- **Language and API; Python bindings; Windows support:**
  - Java: "Java 17.0.11 is supported" (`README.md:43`). A GUI jar and a console jar (README,
    "Pre-Built Releases");
  - Python: a **PythonTraciWrapper** over py4j, marked "Work in Progress". Its install steps check
    out a branch `traci_phsc` (`Tools/PythonTraciWrapper/README.md:5, 20, 35`);
  - Windows: "This software runs on Windows, OS X and Linux" (`README.md:9`). Windows zips for
    v4.0 (Download page).
- **Motion models:**
  - "the optimal steps model, the gradient navigation model, and the social force model"
    (`README.md:7`);
  - also behavioural heuristics, biomechanics, Reynolds steering and the optimal velocity model
    (Kleinmeier 2019, Fig. 13 in §3.2.1 and Fig. 15 in §3.2.3);
  - cellular automata as a special case of the optimal steps model (§2.1.2);
  - and, new in v4.0, a `DatabasedStepsModel` that replays trajectories (`CHANGELOG.md:37`).
- **Behaviour or decision layer:**
  - the **psychology layer**: perception → cognition → behaviour, above the locomotion layer, as
    the interfaces `IPerceptionModel` and `ICognitionModel`. Perception ranks *stimuli*;
    cognition sets a self-category; the locomotion model acts on it (Kleinmeier 2020, §II B,
    Figures 11 and 12);
  - its attributes are stored in the scenario's `attributesPsychology` JSON node
    (`CHANGELOG.md:268`);
  - a `TargetChanger` area "changes the target of an agent", either to another target or to
    another agent to follow (`CHANGELOG.md:272`).
- **Space and time:**
  - continuous 2D topography in SI units (README, "Vadere Units");
  - the simulation loop advances simulated time and calls the locomotion model's `update`
    (Kleinmeier 2019, §3.2.2, Listing 2);
  - the optimal steps model is **event-driven**: "each step of an agent is an event. Stepping
    events of multiple agents are ordered in an event queue and executed accordingly" (§2.1.4).
  - So Vadere is the candidate whose motion is *not* fixed-step.
- **Scenario description:**
  - **JSON**: "All scenario files should be in json format", with `name`, `description`,
    `release`, `processWriters` and `scenario` (`Documentation/scenario/scenario-file-specification.md:7`);
  - Kleinmeier 2019 §3.1.1 calls it "a human-readable JSON-based text file".
- **Native support:**
  - **queues** ✗ as an element `[not documented]`. The behavioural heuristics model has a
    `QueueWidthProcessor`, a *measurement* (`CHANGELOG.md:451`);
  - **waiting areas** ✓: targets have a `waitingMode`, `noWaiting`, `individual` (with a
    `waitingTimeDistribution`) or `trafficLight` (`CHANGELOG.md:186-189`, v2.3);
  - **service points** ~: a target with an individual waiting time `[inference]`;
  - **vehicles and boarding** ✗ `[not documented]`;
  - **groups** ✓, via the Centroid Group Model, with a `groupSizeDistribution` per source
    (`CHANGELOG.md:513`). Part of it "has not been validated" (`CHANGELOG.md:87`);
  - **scripted events** ✓: stimuli for the psychology layer (Kleinmeier 2020, §II B), and remote
    control (below).
- **Hooks for the adapters:**
  - **remote control:** Vadere has a **TraCI server**, "to allow remote control" (`CHANGELOG.md:368`,
    v1.2);
  - **reading state:** the Python wrapper's person API includes `getPosition2DList`,
    `getVelocity` and `getIDList`
    (`Tools/PythonTraciWrapper/pythontraciwrapper/_personapi_wrapper.py:6, 36, 52`);
  - **setting targets and speeds:** `setTargetList`, `setFreeFlowSpeed` and `setPosition2D`
    (`_personapi_wrapper.py:70, 26, 46`);
  - **stepping:** `nextStep(simTimeStep)` (`_control_wrapper.py:11`);
  - **in process:** a cognition model is Java code behind `ICognitionModel` (Kleinmeier 2020,
    Figure 12). So:
    - the action adapter could be written *inside* Vadere as a cognition model `[inference]`;
    - or *outside*, over TraCI. The Python route is labelled work in progress.
- **Scale reported:** "simulating thousands of agents in real-time using the OSM with Vadere is not
  yet possible" (Kleinmeier 2019, §2.1.4).
- **Fit for this FYP** `[inference]`:
  - the candidate that differs from negsim in **time** (event-driven steps) and in **motion**
    (optimal steps, where people step rather than glide);
  - it has an existing perception → cognition → behaviour layer that resembles #34's split;
  - weaker on infrastructure: no queues, no vehicles;
  - its Python access is unfinished, so an adapter is either Java or TraCI;
  - the stated real-time limit for thousands of agents argues against it as a scale testbed.

---

## 6. Menge

**Version read:**
- Curtis, Best & Manocha 2016, *Collective Dynamics* (CC BY 4.0), already cached
  (`refs/pr_curtis2016_menge_cd.txt`) and summarised in `literature/portable-rules/representations.md`,
  [Curtis-Menge];
- source at `master` `00f97ea` (2019-12-31);
- the site https://gamma.cs.unc.edu/Menge/ (fetched 2026-10-18).

- **Links:** https://gamma.cs.unc.edu/Menge/ ; https://github.com/MengeCrowdSim/Menge ;
  doi:10.17815/CD.2016.1.
- **Licence; last release; recent activity:**
  - licence: Apache-2.0 (`LICENSE.txt`);
  - last GitHub release: 0.9.1 (2017-04-23); the newest tag is `v0.9.2`;
  - last commit on `master`: 2019-12-31; no commits since 2026-04-18. The repository was last
    pushed on 2025-12-02, on a branch other than `master` `[inference]`
    (`refs/sim_gh_mengecrowdsim_menge.json`);
  - the home page still says "Menge 0.1 is now available" (© 2013).
- **Language and API; Python bindings; Windows support:**
  - C++. Elements are added as plug-ins, shared libraries; "release of the source code is
    preferred" because of C++ runtime compatibility (Curtis 2016, §5, note 8);
  - Python bindings `[not documented]`;
  - Windows: Visual Studio solutions, with the visualisation's dependencies included (`README.md`,
    "Build instructions / Windows").
- **Motion models:**
  - "pedestrian models" as plug-ins. The repository ships `AgtHelbing`, `AgtJohansson`,
    `AgtKaramouzas`, `AgtZanlungo`, `AgtGCF` and `AgtDummy` (`src/Plugins/`, repository tree at
    `00f97ea`);
  - and the built-in ORCA and PedVO (`src/Menge/MengeCore/Orca/`, `src/Menge/MengeCore/PedVO/`,
    same tree). Curtis 2016 §4.1 (Cross Flow) compares "a velocity-obstacle model, a simple
    social-force model, and a predictive social-force model";
  - a pedestrian model "need only define a single function: the function mapping preferred
    velocity to feasible velocity" (§3.8).
- **Behaviour or decision layer:**
  - the **Behavioral Finite State Machine (BFSM)**: states, prioritised transitions made of a
    **Condition** and a **Target**, and **Actions** on entry (§3.5);
  - goal selectors (§3.6);
  - velocity components and modifiers (§3.7);
  - **Tasks**, "arbitrary, user-defined blocks of work" (§3.9);
  - an **event system** of trigger, effect and target (§3.9).

  One step runs: events → FSM transitions → preferred velocity → pedestrian models → tasks
  (`doc/mengeDetails/event_system.md:11-16`).
- **Space and time:**
  - continuous 2D, mapped onto terrain by an Elevation element (§3.9);
  - spatial queries by kd-tree or navigation mesh (§3.9);
  - a **fixed time step** divided into sub-steps: `TIME_STEP = LOGICAL_TIME_STEP / (1 + SUB_STEPS)`
    (`src/Menge/MengeCore/Agents/SimulatorInterface.h:262`);
  - in the Cross Flow comparison each model ran at its own Δt (`representations.md`,
    [Curtis-Menge], ⚠ note on Figure 4).
- **Scenario description:** **XML**: project, scene, behaviour and view files (§3.11;
  `doc/mengeDetails/projSpec.md`, `sceneSpec.md`, `behaveSpec.md` in the tree).
- **Native support:**
  - **queues** `[not documented]` as an element;
  - **waiting areas** ~: "Stationary Agents" is a design principle (§3.3). Goals "can have finite
    'capacity'" (§3.6);
  - **service points** ~: a goal with capacity plus a timed condition `[inference]`;
  - **vehicles and boarding** ✓ by plug-in. **Ped-Air** simulates "passenger loading, unloading,
    and evacuation behaviors in aircraft", with seat assignment by goal selector, luggage bins of
    fixed capacity, and passengers who wait "until the plane is mostly empty" (§4.2). An
    `aircraft` plug-in and load/unload examples are in the repository (`src/Plugins/aircraft`,
    `examples/plugin/aircraft/`);
  - **groups** ✓ by plug-in: `Formations` (§4.2; `src/Plugins/Formations`);
  - **scripted events** ✓: the event system, with triggers on timers, region population or user
    action (§3.9; `event_system.md`).
- **Hooks for the adapters:**
  - **stepping:** `SimulatorInterface::step()` (`SimulatorInterface.h:83`);
  - **reading state:** `getNumAgents()` and `getAgent(i)` (`:90, :100`);
  - **external influence:** `ExternalEvtTrigger`, "the mechanism through which larger systems can
    influence the simulation. External code can gain access to external triggers and arbitrarily
    'activate' them" (`src/Menge/MengeCore/Agents/Events/EventTriggerExternal.h:34-36, 55`);
  - **in process:** the adapters would be C++ plug-ins: a Task or Condition reads state; an Action,
    a VelocityModifier or an event effect applies a Decision `[inference]`.
- **Scale reported:** the Battle scene was run with "16,000, 32,000, and 64,000 agents", reporting
  frame time against thread count (Curtis 2016, §4.1, Figure 7). The values are in the figure and
  were not extracted. "Menge uses primitive locks" (§4.1).
- **Fit for this FYP** `[inference]`:
  - the closest precedent for #34's split: one behaviour layer over swappable motion models
    (`literature/portable-rules/verdict.md`);
  - and the only open-source candidate with aircraft **boarding** behaviour shipped;
  - but dormant since 2019, C++ only, built with Visual Studio;
  - a plug-in adapter means a C++ toolchain this project does not have;
  - better as a *design reference* than as a testbed.

---

## 7. Mesa

**Version read:** documentation "stable" at https://mesa.readthedocs.io/stable/, fetched
2026-10-18. It says the old simulator classes are "Deprecated since version 3.5.0", consistent with
the latest release, **v3.5.1**. Source head on `main`: `2b2c925` (2026-10-18).

- **Links:** https://mesa.readthedocs.io/stable/ ; https://github.com/mesa/mesa (formerly
  `projectmesa/mesa`; GitHub redirects).
- **Licence; last release; recent activity:**
  - licence: "Mesa is an Apache2 licensed agent-based modeling (or ABM) framework in Python"
    (docs index);
  - last release: v3.5.1, 2026-03-15. A tag `v4.0.0a0` exists (`refs/sim_gh_mesa_mesa.json`);
  - activity: 100 commits since 2026-04-18 (at least).
- **Language and API; Python bindings; Windows support:**
  - pure Python, ≥3.12;
  - PyPI classifier "Operating System :: OS Independent" (`refs/sim_mesa_pypi_summary.txt`).
- **Motion models:** none. Mesa provides spaces, not pedestrian dynamics; a continuous space has
  `move_agent` (docs "Overview", "Continuous Space"). Pedestrian models: `[not documented]`.
- **Behaviour or decision layer:**
  - user-written agent methods, activated through `AgentSet`: `do`, `shuffle_do`, by stage or by
    type (docs "Overview", "Agent Activation Patterns");
  - the decision logic *is* the model.
- **Space and time:**
  - **discrete**: `mesa.discrete_space` grids (orthogonal Moore and von Neumann, hexagonal),
    networks, and Voronoi meshes;
  - **continuous**: `ContinuousSpace`. The legacy `mesa.space` is "in maintenance-only mode"
    (docs "Overview", "Spaces in Mesa");
  - time: by default `step()` runs every 1.0 time units, through `run_for` / `run_until`;
  - **events**: `schedule_event(at=/after=)` and `schedule_recurring`, enabling "pure event-driven
    models, hybrid approaches ..., and everything in between" (docs "Overview", "Event
    Scheduling");
  - the older `DEVSimulator` / `ABMSimulator` are deprecated since 3.5.0 (API "Experimental",
    "Devs").
- **Scenario description:** Python code. An experimental `Scenario` class holds parameters (API
  "Experimental", "Scenarios").
- **Native support:** queues, waiting areas, service points, vehicles and boarding, groups: all
  `[not documented]` (none is a Mesa element). **Scripted events** ✓ (event scheduling, above).
- **Hooks for the adapters:**
  - everything is user code, so both adapters are ordinary Python inside `Agent.step` or a
    scheduled event `[inference]`;
  - no per-step callback is needed.
- **Scale reported:** not stated in the pages read.
- **Fit for this FYP** `[inference]`:
  - the **discrete testbed**: a queue as a graph or grid, service as scheduled events, arrival
    order and waiting time as plain attributes;
  - it differs from negsim in exactly the ways §3 of `research-gap.md` lists: discrete space,
    events instead of fixed steps, no motion model;
  - everything queue-specific would be built by this project. That is small: a queue, a server, a
    join/admit/refuse decision point.

---

## 8. Lower priority

Read briefly: the README at the stated commit, plus metadata. No fuller section, as the issue
allows.

### pedsim_ros (`de37726`, 2020-09-18) and libpedsim (`0d8ff5c`, 2022-12-26)

- **pedsim_ros:**
  - "ROS packages for a 2D pedestrian simulator based on social force model", built on an extended
    libpedsim;
  - features "Individual walking using social force model for very large crowds in real time",
    "Group walking", "XML based scene design";
  - tested on ROS hydro, indigo and kinetic; melodic on a branch (`pedsim_ros/README.md`);
  - BSD-2-Clause; no commits since 2020 (`refs/sim_gh_srl-freiburg_pedsim_ros.json`);
  - Windows `[not documented]`.
- **libpedsim:** a C++ library under the LGPL, and the PEDSIM application under the GPL
  (`chgloor/pedsim/README.md`, "License"); no licence on GitHub.
- **Fit** `[inference]`: robotics-oriented. ROS on Windows is outside this project's toolchain.
  Not a testbed.

### SteerSuite (`SteerSuite/Release` `7530270`, 2018-07-30)

- "a set of test cases, tools, and a C++ library for developing and evaluating agent steering AI
  behaviors" (`README.md`);
- GPL-3.0; last release v1.5.1 (2015-05-19) (`refs/sim_gh_steersuite_release.json`). A second
  repository, `SteerSuite/SteerSuite2`, was last pushed in 2019;
- its benchmark paper is already cached (`refs/us_steerbench_singh2009.txt`, issue #36);
- **Fit** `[inference]`: a source of *test cases* (scenario cards), not a host.

### RVO2 (`75822bb`, 2026-09-26)

- the ORCA library negsim's linear program is adapted from (§1);
- C++, Apache-2.0 for the code (`refs/si1_rvo2_75822bb_excerpts.txt`, header). The README is
  CC-BY-SA-4.0;
- the caller owns the loop: `setTimeStep`, `setAgentPrefVelocity(i, v)`, `getAgentPosition(i)`,
  `doStep()` (`examples/Blocks.cc:85, 170, 176`; `src/RVOSimulator.cc:196`, same excerpts file);
- last release v2.0.2 (2016), but 23 commits since 2026-04-18 (`refs/sim_gh_snape_rvo2.json`);
- **Fit** `[inference]`: a motion model, not a simulator. It does not differ from negsim's motion
  model.

### Sumonity (`2d98b2e`, 2025-07-22)

- "integrates the Simulation of Urban MObility (SUMO) with the Unity game engine" (`readme.md`,
  Introduction); C#, MIT;
- Lindner, Pechinger & Bogenberger 2025 (*SUMO Conference Proceedings* 6, 79–90, CC BY 3.0 DE)
  extend it with "a sub-microscopic pedestrian model for city bus boarding": "passenger flow,
  pathfinding, and door congestion in a Unity-based environment". They ran "four bus door
  configurations" and "passenger loads between 1 and 50, yielding 200 unique scenarios"
  (Abstract);
- pedestrians use a navigation mesh (§3.3.1), with states retrieved over TraCI "at each timestep"
  (§3.2);
- **Fit** `[inference]`:
  - the nearest published *bus-boarding* crowd model, and a source of door-configuration scenarios
    and boarding-time comparisons for a scenario card;
  - Unity is too heavy to adopt as a testbed.

---

## 9. Commercial tools

One paragraph each, from public pages only.

- **MassMotion** (Oasys; product page, fetched 2026-10-18, `refs/sim_massmotion_product.txt`):
  - pedestrian simulation with 2D and 3D geometry imported from BIM and CAD formats;
  - a **Software Development Kit** that gives "direct access to the MassMotion crowd simulation
    engine to customise your models ... advanced algorithms and agents";
  - Windows 10 64-bit; stand-alone or network licences;
  - queues, vehicles and the SDK's language are `[not documented]` on that page.
  - `[inference]` Useful as a reference for what practitioners model, not as a testbed: it is
    paid, and its engine is closed.
- **AnyLogic Pedestrian Library:** **could not be read**. `anylogic.help` and `anylogic.com` both
  returned HTTP 403 to an automated request (search log G18). It is listed in the search log as a
  *browser* lead: the pages are public, so they probably open in a browser, but that was not
  checked. Nothing is claimed here.
- **Pathfinder** (Thunderhead Engineering): **could not be read**. The support documentation timed
  out, and the product page timed out on both download attempts after answering one probe (search
  log G19). It is a *browser* lead. Nothing is claimed here.
