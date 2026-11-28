# Simulator comparison (PT-5, part 1; issue #39)

This is one matrix: a row per simulator and a column per field of the issue's template. It is
split into **four tables** (A to D) so that each stays readable. Every table has the same rows in
the same order. The detail behind each cell, with full quotations, is in `survey.md`, in the
section with the same number.

**Cell conventions:**
- every cell ends with a **source key** in square brackets (key list below);
- `[not documented]`: looked for in the listed sources and not found;
- `[not checked]`: the source could not be read (CrowdGym, AnyLogic, Pathfinder);
- `[inference]`: my reading, not the source's words;
- ✓ supported natively, ~ partly or by workaround, ✗ absent.

Read on 2026-10-18. Nothing was installed or run.

## Source keys

| Key | Source (cached copy in `refs/` unless in-repo) |
|---|---|
| NS | `llm_negotiation/docs/architecture.md` §1, §6.1, §6.2 (at `05490dd`) |
| NS-CFG | `llm_negotiation/configs/scenarios/bidirectional_flow.yaml:14`, `doorway.yaml:10` |
| NS-WL | `WORK_LOG-26.md`, entry 2026-10-14 09:15 (benchmark table) |
| I39 | issue #39 body ("which negsim cannot") |
| CG | `integration/crowdgym_mapping.md` (line numbers given in the cell) |
| CGS | `dataset/schema/README.md` (line numbers given in the cell) |
| U | the user's answer of 2026-10-18 ("Can't share now"), `WORK_LOG-39.md` A2 |
| JPS-API | jupedsim.org/stable API reference (`sim_jps_api_jupedsim_index.txt`), class or method named in the cell |
| JPS-MOD | jupedsim.org "Pedestrian Models" (`sim_jps_pedestrian_models_index.txt`) |
| JPS-RT | jupedsim.org "Routing" (`us_jupedsim_routing.txt`), heading named in the cell |
| JPS-HIST | jupedsim.org "JuPedSim" history page (`sim_jps_history.txt`) |
| JPS-REL | GitHub release notes (`sim_jps_gh_releases.txt`) |
| JPS-SRC | `libsimulator/src/simulation.cpp:96-132` at `6d559df` |
| JPS-GEO | jupedsim.org "Geometry", "Walkable area" |
| JPS-NB | jupedsim.org notebooks: queues_waiting, direct_steering |
| JPS-META | `sim_gh_pedestriandynamics_jupedsim.json`; `sim_jps_pypi_1.4.2_summary.txt`; `LICENSE` at `6d559df` |
| SU-CPL | sumo.dlr.de/docs/jupedsim.html (`sim_sumo_jupedsim.txt`) |
| SU-PED | SUMO "Simulation/Pedestrians" |
| SU-PER | SUMO "Specification/Persons" |
| SU-PT | SUMO "Simulation/Public Transport" |
| SU-VEH | SUMO "Definition of Vehicles, Vehicle Types, and Routes" |
| SU-BD | SUMO "Simulation/Basic Definition", "Defining the Time Step Length" |
| SU-TR | SUMO "TraCI" index; "TraCI/Person Value Retrieval"; "TraCI/Change Person State" |
| SU-DL | SUMO "Downloads" (1.28.0; "Python packages"; "Note on Licensing") |
| SU-LIB | SUMO "Libsumo", "Limitations" |
| SU-SRC | `src/microsim/transportables/MSPModel_JuPedSim.cpp` at `2285bbc` |
| SU-META | `sim_gh_eclipse-sumo_sumo.json` |
| VA-RM | Vadere `README.md` at `4c53f1c` |
| VA-CL | Vadere `CHANGELOG.md` at `4c53f1c` |
| VA-P19 | Kleinmeier et al. 2019, *Collective Dynamics* (`sim_vadere_kleinmeier2019_cd.txt`) |
| VA-P20 | Kleinmeier, Köster & Drury 2020 (`pr_arxiv_2005_12712v2_kleinmeier.txt`) |
| VA-SFS | Vadere `Documentation/scenario/scenario-file-specification.md:7` |
| VA-TW | Vadere `Tools/PythonTraciWrapper/`: `README.md`, `_personapi_wrapper.py`, `_control_wrapper.py` |
| VA-META | `sim_gl_vadere_vadere.json`; vadere.org "Download" |
| ME-P16 | Curtis, Best & Manocha 2016, *Collective Dynamics* (`pr_curtis2016_menge_cd.txt`) |
| ME-SRC | Menge at `00f97ea`: `SimulatorInterface.h`, `EventTriggerExternal.h`, `doc/mengeDetails/event_system.md`, repository tree (`sim_menge_tree_00f97ea.txt`), `README.md` |
| ME-META | `sim_gh_mengecrowdsim_menge.json`; `LICENSE.txt`; gamma.cs.unc.edu/Menge |
| MS-OV | mesa.readthedocs.io/stable "Overview" |
| MS-API | mesa.readthedocs.io/stable API "Experimental" |
| MS-META | `sim_gh_mesa_mesa.json`; `sim_mesa_pypi_summary.txt`; docs index |
| PR | pedsim_ros `README.md` at `de37726`; `sim_gh_srl-freiburg_pedsim_ros.json` |
| SS | SteerSuite `Release` `README.md` at `7530270`; `sim_gh_steersuite_release.json` |
| RV | `si1_rvo2_75822bb_excerpts.txt`; `sim_gh_snape_rvo2.json` |
| SN | Sumonity `readme.md` at `2d98b2e`; `sim_gh_tum-vt_sumonity.json` |
| SN-P25 | Lindner, Pechinger & Bogenberger 2025, *SUMO Conf. Proc.* 6 (`sim_sumonity_lindner2025_scp.txt`) |
| MM | oasys-software.com MassMotion product page (`sim_massmotion_product.txt`) |
| SL | `search-log.md` (pages that could not be fetched) |

---

## A. Practicalities

| Simulator | Version read | Licence | Last release; recent activity | Language and API | Python bindings | Windows |
|---|---|---|---|---|---|---|
| **negsim** | `architecture.md` at `05490dd` [NS] | none stated in §1/§6.1/§6.2 [NS] | no releases; built per issue #24–#32 [NS] | Python, standard library + PyYAML [NS §1] | native [NS §1] | developed and benchmarked on Windows 11 [NS-WL] |
| **CrowdGym** | repo notes only [U] | [not checked] [U] | [not checked] [U] | Python API; C++ port in progress [CG:4-7; CGS:22-24] | Python [CG:4-6] | [not checked] [U] |
| **JuPedSim** | docs "stable" (v1.4.x); source `6d559df` [JPS-META] | LGPL-3.0-or-later [JPS-META] | v1.4.2, 2026-05-21; ≥100 commits in 6 months [JPS-REL; JPS-META] | C++ core, Python API, C API; single-threaded [JPS-HIST; SU-CPL] | yes, PyPI, Python 3.10–3.14 [JPS-META] | `win_amd64` wheel [JPS-META] |
| **SUMO + JuPedSim** | docs 2026-10-18 (1.28.0); source `2285bbc` [SU-DL; SU-META] | EPL-2.0, GPL-2.0+ secondary [SU-DL] | 1.28.0; ≥100 commits in 6 months [SU-DL; SU-META] | C++; TraCI over TCP, or libsumo in-process [SU-TR; SU-LIB] | `eclipse-sumo`, `traci`, `libsumo` on pip [SU-DL] | installer; JuPedSim bundled; libsumo GUI not on Windows [SU-DL; SU-PED; SU-LIB] |
| **Vadere** | v4.0; source `4c53f1c` [VA-CL; VA-META] | LGPL [VA-RM:130] | v4.0, 2026-04-07; GitLab active 2026-10-16 [VA-CL:28; VA-META] | Java 17; GUI and console jars [VA-RM:43] | py4j TraCI wrapper, "Work in Progress" [VA-TW README:5] | yes [VA-RM:9; VA-META] |
| **Menge** | paper 2016; source `00f97ea` [ME-P16; ME-META] | Apache-2.0 [ME-META] | 0.9.1, 2017-04-23; last `master` commit 2019-12-31; 0 in 6 months [ME-META] | C++, plug-ins as shared libraries, XML [ME-P16 §3.11, §5 n.8] | [not documented] [ME-SRC; ME-P16] | Visual Studio solutions [ME-SRC README] |
| **Mesa** | docs "stable" (3.5.x); head `2b2c925` [MS-META; MS-API] | Apache-2.0 [MS-META] | v3.5.1, 2026-03-15; ≥100 commits in 6 months [MS-META] | Python library [MS-META] | native, Python ≥3.12 [MS-META] | "OS Independent" [MS-META] |
| **pedsim_ros** | README `de37726` [PR] | BSD-2-Clause [PR] | no releases; last commit 2020-09-18 [PR] | C++ / ROS packages [PR] | via ROS [not documented] [PR] | [not documented] [PR] |
| **SteerSuite** | README `7530270` [SS] | GPL-3.0 [SS] | v1.5.1, 2015-05-19; last commit 2018-07-30 [SS] | C++ library, test cases, tools [SS] | [not documented] [SS] | VS 2012 solution in `build/` [SS] |
| **RVO2** | `75822bb` [RV] | Apache-2.0 (code) [RV] | v2.0.2, 2016; 23 commits in 6 months [RV] | C++ library; caller owns the loop [RV] | [not documented] [RV] | [not documented] [RV] |
| **Sumonity** | readme `2d98b2e`; paper 2025 [SN; SN-P25] | MIT [SN] | no releases; last commit 2025-07-22 [SN] | C# / Unity, SUMO over TraCI [SN; SN-P25 §3.2] | [not documented] [SN] | [not documented] [SN] |
| **MassMotion** | product page 2026-10-18 [MM] | commercial: stand-alone / network licences [MM] | [not documented] [MM] | desktop application + SDK [MM] | [not documented] [MM] | Windows 10 64-bit [MM] |
| **AnyLogic Ped. Lib.** | not read: HTTP 403 [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] |
| **Pathfinder** | not read: timeout [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] |

## B. How it works: motion, behaviour, space and time, scenario

| Simulator | Motion models | Behaviour or decision layer | Space | Time | Scenario description |
|---|---|---|---|---|---|
| **negsim** | unicycle and holonomic dynamics; ORCA half-planes + LP; path tracking under a speed bound [NS §1, §6.1] | `DirectiveProvider` → `AvoidanceDirective` per new neighbour; pair resolution; arbiter at single-file segments; rule layer [NS §6.1, §6.2] | continuous 2D [NS §6.1] | fixed step, all agents from the same state; dt 0.1 s (crowd), 0.2 s (doorway) [NS §6.2; NS-CFG] | YAML → `ScenarioSpec`, `schema_version: 2` [NS §1, §6.1] |
| **CrowdGym** | "CFS", found "less jittery at exits" [CG:100-101] | overridable `RL_take_action` → `(N,3)` `[move_x, move_y, delta_facing]`; `AgentJourneyDirector` [CG:87-111; CGS:52-66] | continuous 2D [inference from CG:31-37, 90-98] | fixed frame rate: `steps = fps * seconds` [inference from CG:66-67] | Spawner + `AgentType` list (Speed, Tau, Mass, Radius side/front, weight) [CG:22-37]; file format [not checked] |
| **JuPedSim** | CFS (V1, V2, V3), Anticipation Velocity, Generalized Centrifugal Force, Social Force, WarpDriver [JPS-MOD; JPS-REL] | strategic (journeys) → tactical (routing) → operational (model) each `iterate()` [JPS-SRC]; journeys of stages and transitions [JPS-RT "Stages", "Transitions"] | continuous walkable polygon; switchable at run time [JPS-GEO; JPS-API `switch_geometry`] | fixed step, default 0.01 s; no stop condition [JPS-API `Simulation`] | Python code; XML replaced [JPS-API; JPS-HIST]; file format [not documented] |
| **SUMO + JuPedSim** | `nonInteracting`, `striping` (default), `jupedsim`; with JuPedSim only CFS "tested extensively" [SU-PED; SU-CPL NOTE; SU-SRC:72-79] | person plans of `walk` / `ride` / `stop`; intermodal routing; rerouters [SU-PER; SU-CPL] | road/sidewalk network (striping); continuous 2D walkable area (JuPedSim) [SU-PED] | fixed step, default 1 s, 0.001–1.0 s; JuPedSim sub-steps at ~0.01 s [SU-BD; SU-SRC:412-417; SU-CPL] | XML network + person routes; polygons `jupedsim.walkable_area`; netedit / DXF [SU-PER; SU-PED; SU-CPL] |
| **Vadere** | optimal steps, gradient navigation, social force; BHM, biomechanics, Reynolds, OVM; CA via OSM [VA-RM:7; VA-P19 §2.1.2, §3.2.3] | psychology layer perception → cognition → behaviour [VA-P20 §II B]; `TargetChanger` [VA-CL:272] | continuous 2D, SI units [VA-RM; VA-P19 §3.2.1] | OSM **event-driven** (event queue of steps); loop advances sim time [VA-P19 §2.1.4, §3.2.2] | JSON [VA-SFS; VA-P19 §3.1.1] |
| **Menge** | ORCA, PedVO built in; Helbing, Johansson, Karamouzas, Zanlungo, GCF as plug-ins [ME-SRC tree; ME-P16 §3.8] | BFSM (states, prioritised Condition + Target, Actions); goal selectors; velocity modifiers; Tasks; events [ME-P16 §3.5–3.9] | continuous 2D + Elevation; kd-tree or navmesh queries [ME-P16 §3.9] | fixed step with sub-steps [ME-SRC `SimulatorInterface.h:262`]; per-model Δt in comparisons [ME-P16 Fig. 4] | XML project / scene / behaviour / view [ME-P16 §3.11] |
| **Mesa** | none (no pedestrian model) [MS-OV; not documented] | user-written `step` methods via `AgentSet` [MS-OV "Agent Activation"] | **discrete** grids, hex, network, Voronoi; or continuous [MS-OV "Spaces"] | step every 1.0 time unit, or **event scheduling** (`schedule_event`, `schedule_recurring`) [MS-OV "Event Scheduling"] | Python code; experimental `Scenario` [MS-API "Scenarios"] |
| **pedsim_ros** | social force (extended libpedsim) [PR] | "Social activities simulation", groups [PR] | 2D [PR] | [not documented] [PR] | XML scenes [PR] |
| **SteerSuite** | steering library [SS] | [not documented] [SS] | [not documented] [SS] | [not documented] [SS] | test cases (SteerBench) [SS] |
| **RVO2** | ORCA [RV] | none; caller sets preferred velocity [RV] | continuous 2D [RV] | fixed step `setTimeStep` [RV `Blocks.cc:85`] | C++ code [RV] |
| **Sumonity** | Unity navmesh pedestrians, density-based speed [SN-P25 §3.3.1] | [not documented] [SN-P25] | 3D Unity scene over SUMO network [SN; SN-P25] | per SUMO step over TraCI [SN-P25 §3.2] | Unity project + SUMO files [SN] |
| **MassMotion** | [not documented] [MM] | [not documented] [MM] | 2D and 3D geometry [MM] | [not documented] [MM] | BIM / CAD import (.fbx, .ifc, .dwg) [MM] |
| **AnyLogic Ped. Lib.** | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] |
| **Pathfinder** | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] |

## C. Native support

| Simulator | Queues | Waiting areas | Service points | Vehicles and boarding | Groups | Scripted events |
|---|---|---|---|---|---|---|
| **negsim** | ✗ [I39; NS] | ✗ [not documented] [NS] | ✗ [I39] | ✗ [I39] | attribute group only, not walking groups [NS opening] | [not documented] [NS] |
| **CrowdGym** | [not checked] [U] | [not checked] [U] | [not checked] [U] | [not checked] [U] | [not checked] [U] | journeys/exits ✓; others [not checked] [CG:105-111; U] |
| **JuPedSim** | ✓ `add_queue_stage`, `pop(n)` [JPS-API `NotifiableQueueStage`; JPS-RT "Waiting Queue"] | ✓ waiting set, active/inactive [JPS-API `WaitingSetStage`; JPS-RT "Waiting Set"] | ~ queue popped by script [inference; JPS-NB queues] | ✗ alone [not documented] [JPS-API] | [not documented] [JPS-API] | ~ by script between iterations; no event system [JPS-API] |
| **SUMO + JuPedSim** | [not documented] as pedestrian element [SU-PER; SU-PT] | ✓ bus-stop waiting; signal-driven JuPedSim waiting positions, "static" [SU-PT "Bus Stops"; SU-CPL; SU-SRC:542] | ~ `stop` stage with duration; vanishing zones for ticket control [SU-PER "Stops"; SU-CPL; SU-SRC:570] | ✓ `ride`, `personCapacity`, `boardingDuration` 0.5 s; transfer points; doors only on exit; pedestrians ignore vehicles [SU-PER; SU-VEH; SU-PT; SU-CPL] | ~ travel group for a shared taxi [SU-PER] | ✓ TraCI, rerouters, traffic lights [SU-TR; SU-CPL] |
| **Vadere** | ✗ as element; `QueueWidthProcessor` is a measure [VA-CL:451] | ✓ target `waitingMode` individual / trafficLight [VA-CL:186-189] | ~ target with waiting time [inference; VA-CL:186] | ✗ [not documented] [VA-RM; VA-CL] | ✓ Centroid Group Model, part "not validated" [VA-CL:513, 87] | ✓ stimuli; TraCI [VA-P20 §II B; VA-CL:368] |
| **Menge** | [not documented] [ME-P16; ME-SRC] | ~ stationary agents; goals with finite capacity [ME-P16 §3.3, §3.6] | ~ goal capacity + timed condition [inference; ME-P16 §3.6] | ✓ aircraft boarding plug-in (Ped-Air) [ME-P16 §4.2; ME-SRC tree] | ✓ Formations plug-in [ME-P16 §4.2; ME-SRC tree] | ✓ event system (trigger, effect, target) [ME-P16 §3.9; ME-SRC `event_system.md`] |
| **Mesa** | [not documented] [MS-OV] | [not documented] [MS-OV] | [not documented] [MS-OV] | [not documented] [MS-OV] | [not documented] [MS-OV] | ✓ `schedule_event` / `schedule_recurring` [MS-OV] |
| **pedsim_ros** | [not documented] [PR] | [not documented] [PR] | [not documented] [PR] | [not documented] [PR] | ✓ "Group walking" [PR] | [not documented] [PR] |
| **SteerSuite** | [not documented] [SS] | [not documented] [SS] | [not documented] [SS] | [not documented] [SS] | [not documented] [SS] | [not documented] [SS] |
| **RVO2** | ✗ (a motion library) [RV] | ✗ [RV] | ✗ [RV] | ✗ [RV] | ✗ [RV] | ✗ [RV] |
| **Sumonity** | [not documented] [SN-P25] | [not documented] [SN-P25] | [not documented] [SN-P25] | ✓ city-bus boarding with door configurations [SN-P25 Abstract] | [not documented] [SN-P25] | [not documented] [SN-P25] |
| **MassMotion** | [not documented] [MM] | [not documented] [MM] | [not documented] [MM] | [not documented] [MM] | [not documented] [MM] | [not documented] [MM] |
| **AnyLogic Ped. Lib.** | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] |
| **Pathfinder** | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] |

## D. Hooks for the two adapters, scale, and fit

| Simulator | Perception hook (read all agents each step) | Action hook (target, speed, route mid-run) | Per-step callback | Scale reported | Fit for this FYP `[inference]` |
|---|---|---|---|---|---|
| **negsim** | `perceive` → `PerceptionRecord` [NS §6.1] | `AvoidanceDirective` (share, side, clearance, leader, speed_scale); arbiter bound [NS §6.2] | own loop [NS §6.1] | 10,000 agents: 1.36–1.60 s/step, one thread [NS-WL] | reference; the ORCA binding [survey §1] |
| **CrowdGym** | state readable in the handler [inference from CG:52-58] | `RL_take_action` → `(N,3)` per step [CG:87-103] | `RL_take_action` each step [CGS:52-53] | [not checked] [U] | deployment target [survey §2] |
| **JuPedSim** | `agents()`, `agent(id)`, `agents_in_range`, `agents_in_polygon`; `position`, `orientation`, `stage_id`, model state; no velocity in CFS states [JPS-API `Agent`, `Simulation`, `...ModelState`] | `agent.target` (direct-steering journeys only); `switch_agent_journey`; per-agent `desired_speed` "changed at any time"; no checks on set [JPS-API; JPS-MOD] | none: user loop calls `iterate()` [JPS-API; JPS-NB] | not stated; SUMO calls it "runtime-limiting" [SU-CPL] | second continuous testbed; queues and waiting [survey §3] |
| **SUMO + JuPedSim** | TraCI `getPosition`, `getSpeed`, subscriptions [SU-TR] | `setSpeed`, `moveToXY`, `appendStage` / `replaceStage` / `removeStage`; effect on JuPedSim persons [not documented] [SU-TR; SU-SRC:452, 491] | client calls `simulationStep`; sim waits for all clients [SU-TR "Multiple clients"] | pedestrians: not stated; "large networks" [SU-META] | host for boarding (vehicle side) [survey §4] |
| **Vadere** | TraCI: `getPosition2DList`, `getVelocity` [VA-TW `_personapi_wrapper.py:52, 36`] | `setTargetList`, `setFreeFlowSpeed`, `setPosition2D`; or a Java cognition model [VA-TW `:70, 26, 46`; VA-P20 Fig. 12] | `nextStep(simTimeStep)` over TraCI [VA-TW `_control_wrapper.py:11`] | "thousands of agents in real-time ... not yet possible" (OSM) [VA-P19 §2.1.4] | event-driven testbed; psychology-layer precedent [survey §5] |
| **Menge** | `getNumAgents()`, `getAgent(i)`; Task / Condition plug-in [ME-SRC `SimulatorInterface.h:90, 100`; ME-P16 §3.5, §3.9] | `ExternalEvtTrigger.activate()`; Action, VelocityModifier, event effect plug-ins [ME-SRC `EventTriggerExternal.h:34-36, 55`; ME-P16 §3.7, §3.9] | `step()` [ME-SRC `SimulatorInterface.h:83`] | Battle scene, 16k / 32k / 64k agents, Fig. 7 [ME-P16 §4.1] | design reference; aircraft boarding precedent [survey §6] |
| **Mesa** | user code [MS-OV] | user code [MS-OV] | own `step` / scheduled events [MS-OV] | not stated [MS-OV; MS-META] | discrete queue testbed [survey §7] |
| **pedsim_ros** | ROS topics [not documented in README] [PR] | [not documented] [PR] | ROS node loop [not documented] [PR] | "very large crowds in real time" (no number) [PR] | not a testbed (ROS) [survey §8] |
| **SteerSuite** | [not documented] [SS] | [not documented] [SS] | [not documented] [SS] | not stated [SS] | source of test cases [survey §8] |
| **RVO2** | `getAgentPosition(i)` [RV `Blocks.cc:170`] | `setAgentPrefVelocity(i, v)` [RV `Blocks.cc:176`] | caller calls `doStep()` [RV `RVOSimulator.cc:196`] | not stated [RV] | not a simulator; same model as negsim [survey §8] |
| **Sumonity** | TraCI pedestrian states "at each timestep" [SN-P25 §3.2] | [not documented] [SN-P25] | per SUMO step [SN-P25 §3.2] | 1–50 passengers per scenario, 200 scenarios [SN-P25 Abstract] | boarding evidence for a scenario card [survey §8] |
| **MassMotion** | SDK "direct access" to engine [MM] | SDK [MM] | [not documented] [MM] | not stated [MM] | reference only (paid) [survey §9] |
| **AnyLogic Ped. Lib.** | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL; survey §9] |
| **Pathfinder** | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL] | [not checked] [SL; survey §9] |

## What the matrix says, in four lines `[inference]`

1. Each family differs from negsim along a different axis:
   - **continuous, different motion model, fixed small step**: JuPedSim;
   - **event-driven steps**: Vadere;
   - **discrete space and events**: Mesa.
2. **Queues and waiting areas** are native only in JuPedSim (queue, waiting set) and partly in
   Vadere (waiting targets). **Vehicles and boarding** are native only in SUMO (time-based), and in
   Menge's and Sumonity's plug-ins (behaviour-based).
3. **No candidate offers a per-step callback.** In every open-source candidate but CrowdGym, the
   adapters attach in a loop this project writes around `iterate()` / `simulationStep` /
   `nextStep` / `doStep`. CrowdGym's `RL_take_action` is the one built-in per-step decision hook.
4. Only negsim and Menge report a scale near 10,000 agents.
   - Vadere states a limit below it for real time.
   - JuPedSim's is not stated.
   - Scale has to be measured in #40, not read.
