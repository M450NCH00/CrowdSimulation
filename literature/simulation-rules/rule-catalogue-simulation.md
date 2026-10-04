# Rule catalogue — conflict-avoidance and conflict-resolution rules as implemented

> ## ⚠ DRAFT — PENDING SUPERVISOR REVIEW
> Nothing in this file is settled. The **Category** column applies the issue's definitions as I
> read them; the **Portable?** column is my judgement, marked `[inference]` throughout; and the
> apparent correspondences in §2 are deliberately **not merged** — whether two similar-looking
> rules are the same rule is a judgement for supervisor review.

Prepared for issue [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). This is the main
deliverable. Sub-area files: [S1](s1-crowd-simulation.md) · [S2](s2-games.md) ·
[S3](s3-mapf-robotics.md) · [S4](s4-traffic-vehicles.md). Also:
[category summary](category-summary.md) · [research gap](research-gap.md) ·
[pre-window foundations](pre-window-foundations.md) · [missing papers](missing-papers.md) ·
[search log](search-log.md) · [refs](refs-simulation-rules.bib).

The companion catalogue of *theoretical* rules from issue #20 is
[`../game-theory/candidate-rule-catalogue.md`](../game-theory/candidate-rule-catalogue.md) (rules
R1–R14). The two are kept in separate files, as the issue requires, and cross-referenced in §3.
Rules here are numbered **SR1–SR35** so the two numberings cannot be confused.

## Rules of this file

1. **Every row cites a source** with a locator. No row states a rule that no source states.
2. **No two sources' rules are merged into one row**, even where they look alike. Look-alikes are
   listed in §2.
3. **Nothing is generalised beyond its source.** "Max agents tested" is the largest count the
   source itself reports for that rule, with the locator. Where a source's own numbers conflict,
   the row says so.
4. **Only rules read at source are in §1.** Rules I know only from a survey's description are in
   §4.
5. A rule that a 2016+ source merely *re-implements or explains* from a pre-window method is
   still listed — under the in-window source, worded as that source words it — because the issue
   asked for pre-window substance to be covered through recent sources. Such rows are marked
   **(pre-window rule, as described by …)**.
6. `[industry]` in the source cell means `[industry, not peer reviewed]`. `[preprint]` means no
   published version was found.

Category key: **A** avoid conflict by rule · **B** resolve through communication · **C** resolve
by rule after contention. A second letter in brackets is a secondary category.

---

## §1. The catalogue

### S1 — pedestrian and crowd simulation

| # | Rule name | Source (paper, locator) | Category | Domain | Trigger | Information required | Tie-break | Max agents tested | Validated against real data? | Portable? `[inference]` |
|---|---|---|---|---|---|---|---|---|---|---|
| **SR1** | **Half-plane velocity selection** (pre-window rule ORCA, as implemented on GPU): take the velocity nearest the desired one that lies in every neighbour's collision-free half-plane; if none exists, the one that "least penetrates" them. | [Charlton-FastCrowd] §3, Fig. 1 | A | Pedestrians | Every iteration, on collision predicted within look-ahead τ | Neighbours' radius, position, velocity within an observation radius | `[not stated in paper]` | 5 × 10⁵ at ~33 ms/frame (§4). ⚠ Abstract says 100,000 at 60 fps — the paper's two statements differ | No — judged by appearance (§4) | **Yes.** Needs only positions and velocities. Gives no answer when the half-planes leave no room ("no guarantee of collision-free motion", §3) |
| **SR2** | **Visibility-gated arrival-time speed adjustment**: after the avoidance step, rescale speed by the gap between own estimated arrival time and the crowd average — only while no other agent blocks the line to the next waypoint. | [Sung-ArrivalTime] §3.4–§3.5 | A | Game / film characters | Continuous; suspended whenever another agent is in the way | Neighbours' state (for ORCA) **plus every agent's estimated arrival time** | `[not stated in paper]` (inherits ORCA's) | 100, ≥ 40 frames/s incl. rendering (§4, Fig. 14) | No | **As a wrapper, yes**; it is a timing layer, not a conflict rule. Authors report it stops working when agents are densely packed (§5) |
| **SR3** | **Shared-waypoint perturbation**: when a second path uses a waypoint already used by another, move the second path's waypoint to a random point within radius *r*. | [Sung-ArrivalTime] §3.3, Fig. 3 | A | Game / film characters | Offline, at planning | The roadmap and a use-count per waypoint | **First user keeps the waypoint; the later one is displaced, randomly** | 30 in the obstacle scene (§4, Fig. 12) | No | **Yes** for any roadmap-based simulator. Reduces conflicts; does not resolve one |
| **SR4** | **Density-triggered random detour**: if the number of agents in a forward sector exceeds a threshold, insert a sub-goal at a random angle and distance. | [Sudkhot-BDI-RVO] §4.2, Algorithm 1 lines 15–22 | A | Pedestrians | Predicted congestion ahead (count over threshold) | Positions of agents in a forward sector | **Random** (Alg. 1 lines 17–18) | ⚠ Paper states 40,000 (Abstract, §6), also "ten thousands" (§5.3) and 720,000 (§5.4) — not consistent | No | **Only where a detour exists.** Useless in a doorway or single corridor |
| **SR5** | **Stall-triggered re-plan**: if, in a dense area, own speed has fallen below a threshold, compute a new route. | [Sudkhot-BDI-RVO] §4.2, Algorithm 1 lines 23–26; Table 1 | C | Pedestrians | After the agent has already been slowed | Own speed; navigation graph | Left/right choice given by a formula not legible in the extract: `[not recovered]` | as SR4 | No | **Only where an alternative route exists** |
| **SR6** | **Adaptive share of the avoidance effort**: hold, per neighbour, a degree of cooperation α ∈ [0,1]; take on the (1 − α) share of the velocity change needed; update α online from whether the neighbour is seen to deviate. α = 0.5 reproduces ORCA. | [MartinezBaselga-AVOCADO] §IV-A (Eqs. 6–8), §IV-B (Eqs. 10–11, 15), Algorithm 1 | A | Robots, and robots among pedestrians | Continuous at 20 Hz; adaptation rises as time-to-collision falls | Neighbours' positions and velocities within 2.5 m, plus own memory of each neighbour's last velocity | Bias term `b_i` (a prior on the other's cooperativeness; default 0, Table I) | 25 in simulation (§V-B); 3 robots + 3 people on hardware (§VI) | **No** — *tested with* 19 pedestrians (§VI), not compared against recorded human behaviour | **Yes — strongest candidate in S1.** One number per neighbour encodes "who yields, by how much". ⚠ A wrong prior causes collisions (§V-A, Fig. 6) |
| **SR7** | **Attention-scaled noise for symmetry breaking**: perturb the *perceived* velocity of the other agent by uniform noise scaled by (1 − attention). | [MartinezBaselga-AVOCADO] §IV-D, Eqs. 18–19 | A | Robots | Continuous; acts before the encounter becomes close | As SR6 | **This row *is* a tie-break: random noise.** ⚠ The paper describes the noise schedule two contradictory ways (see S1 entry) | as SR6 | No | **Yes.** The authors say it "can also be applied to other VO-based methods such as ORCA" (§IV-D) |
| **SR8** | **Collision-free speed model**: speed = min(free speed, (gap ahead − body length)/T), zero at contact; direction = desired direction plus exponential repulsion from neighbours. | [Tordeux-CFSM] §2.1, Eqs. 2–6 | A | Pedestrians | Continuous | Neighbours' **positions only** | `[not stated in paper]`. `[inference]` an exactly head-on pair stops and stays stopped; confirmed in simulation by [Xu-AVM] §3 | Not stated; 9 m × 3 m corridor up to 6 ped/m² (§3.1) | No — phenomena "reproduced" qualitatively (§4) | **Yes, as a safety floor.** One distance and one clamp. Guarantees no overlap (§2.2) and resolves nothing |
| **SR9** | **Anticipation velocity model**: steer sideways away from where each neighbour is *predicted* to be `t_a` seconds ahead, weighting oncoming neighbours twice as heavily as same-direction ones; speed as SR8. | [Xu-AVM] §2.1–§2.2, Eqs. 1–10; parameters Table 3 | A | Pedestrians (bidirectional corridor) | Continuous, on predicted proximity | Neighbours' positions and velocities | **Random**: when the neighbour's predicted position is exactly ahead, the sideways direction "is chosen randomly" (§2.1) | 300 (§4.4) | **YES** — fundamental diagram and lane-formation time course against laboratory experiments (§5; §4.4). Calibration "performed manually"; comparability "limited" by the authors' own account | **Moderately.** Structure is general; parameters are calibrated to one population and geometry |

### S2 — video games and game AI (all `[industry, not peer reviewed]`)

| # | Rule name | Source (paper, locator) | Category | Domain | Trigger | Information required | Tie-break | Max agents tested | Validated against real data? | Portable? `[inference]` |
|---|---|---|---|---|---|---|---|---|---|---|
| **SR10** | **Reciprocal half-dodge** (pre-window rule RVO, as described by the chapter): each agent moves "only halfway out of the way of a collision", expecting the other to do the same. | [SunshineHill-RVO-ORCA] `[industry]` §19.2.1, §19.3 | A | Game characters | Every frame, on projected collision | Neighbours' positions and velocities; assumes their current velocity is their preferred one | `[not stated in chapter]` | `[not stated]` — no evaluation in the chapter | No | **Yes.** Guarantee holds for two agents and no obstacles only (§19.3) |
| **SR11** | **Keep the current passing side** (pre-window rule ORCA, as described by the chapter): choose trajectories that preserve whichever side the two agents are already set to pass on, and widen the separation. | [SunshineHill-RVO-ORCA] `[industry]` §19.4–§19.5 | A | Game characters | Every frame | As SR10, plus the closest-approach vector that defines *sidedness* | **The initial geometry decides**; exactly head-on: `[not stated in chapter]` | `[not stated]` | No | **Yes, as a tie-break principle.** ⚠ Deadlocks at corners, where the initial side is the wrong one (§19.6) |
| **SR12** | **Sub-stepped avoidance with ramped weights**: run several avoidance iterations per movement step, starting with dodge-weights well below 0.5 and ramping up to 0.5. | [SunshineHill-RVO-ORCA] `[industry]` §19.7.1–§19.7.2 | A | Game characters | Several times per frame | All agents' velocities immediately after each iteration — available to a simulator, not to a robot | n/a (a convergence device) | `[not stated]` | No | **Yes — simulator-only.** Exploits the fact that a simulator knows every agent's next velocity at once |
| **SR13** | **Penalty-scored velocity with a sidedness-change penalty**: score candidate velocities by distance from preferred velocity plus collision penalties that grow as the collision nears, plus a penalty per neighbour whose passing side would change. | [SunshineHill-RVO-ORCA] `[industry]` §19.8–§19.8.1 | A | Game characters | Every frame | As SR11 | Lowest score | `[not stated]` | No | **Yes.** "Makes no guarantees of collision avoidance" (§19.8) |
| **SR14** | **Hull-steering around a vehicle, minimum heading change**: if the straight line to the destination crosses the vehicle's expanded convex hull, head for the reachable hull vertex that least changes the intended heading. | [Martel-ACSyndicate] `[industry]` §15.4.2, Fig. 15.10 | A | Game pedestrians vs. carriages | On predicted intersection | The vehicle's part geometry and velocity | **Minimum deviation from intended heading**; heuristic: "an agent crossing a moving vehicle will often try to go behind it" (§15.5.2) | `[not stated]` | No — "mimicking what humans would do" is asserted (§15.5.2) | **Geometry: yes.** As a conflict rule it is one-sided: the pedestrian always yields (§15.2) |
| **SR15** | **Design-time route separation**: routine traffic follows looping splines, each "defined to ensure that it did not interact with any other spline". | [Jenner-DriverSF] `[industry]` §17.2 | A | Game vehicles (civilian traffic) | Never at runtime — fixed at design time | Own spline only | n/a — no conflict can arise | "thousands of vehicles" (§17.7), no count or method given | No | **Yes, for background agents.** Removes conflicts for the bulk of a population at zero runtime cost |
| **SR16** | **Trait-weighted path cost**: score candidate paths by lane changes, proximity to other vehicles' *predicted* positions, oncoming-lane and sidewalk use, and predicted collisions — with weights set by per-agent personality traits. | [Jenner-DriverSF] `[industry]` §17.2.2, §17.5, §17.6.6 | A | Game vehicles (pursuit, racing) | About once per second, for the next few seconds | Other vehicles' published predicted paths ⚠ (a plan, not physical state — see category-summary §4) | Lowest cost; equal costs `[not stated in chapter]`. **Weights differ per agent by personality** (§17.2.2) | as SR15; achieved through level of detail (§17.2.1) | No — weights "arrived at empirically" (§17.6.6) | **The idea, yes.** Closest precedent for persona-dependent avoidance |
| **SR17** | **Engine RVO with a priority system**: closest-to-preferred velocity that avoids nearby agents, plus "a priority system to help resolve potential collisions". | [Epic-UnrealAvoidance] `[industry]` Overview | A (C) | Game characters | Continuous, within a consideration radius | Nearby agents' positions and velocities | `[not stated]` — the priority system is named, not described | `[not stated]` | No | **Not assessable** — the page does not describe the rule well enough to reimplement |

### S3 — multi-agent path finding and multi-robot navigation

| # | Rule name | Source (paper, locator) | Category | Domain | Trigger | Information required | Tie-break | Max agents tested | Validated against real data? | Portable? `[inference]` |
|---|---|---|---|---|---|---|---|---|---|---|
| **SR18** | **Priority inheritance with backtracking (PIBT)**: each timestep, in priority order, take the free neighbouring vertex nearest your goal; if it is occupied, the occupant inherits your priority and must move first; if it cannot, it reports back and you try your next choice. | [Okumura-PIBT] §4.1–§4.2, Algorithm 1 | C (B in the decentralised variant, §4.5) | Abstract agents on a graph; robots in one demo | On contention for a vertex, every timestep | Graph; all agents' positions, goals and **priorities**; global synchronous clock | **Priority = timesteps since last at goal + a unique per-agent ε ∈ [0,1)** (Alg. 1 lines 2–3). Among equal-distance vertices: prefer the unoccupied one (§4.2). PIBT+ seeds ε by distance to goal (Alg. 2) | **10,000**, ~10 ms per timestep, runtime only (§5.3). Solution quality tested to 1,000 (§5.1) | No (robot demo only, §5.4) | **Yes for lock-step simulators.** ⚠ The guarantee needs a cycle through every adjacent pair (Theorem 1); corridors fail it (Fig. 5) |
| **SR19** | **8-connected PIBT with safety-aware smoothing**: run PIBT on an 8-connected grid; straighten each path only *between* "critical interactions" (within one hop of another agent); repair any new intersection with prioritised SIPP. | [Chakravarty-PIBT-FreeSpace] §3.1–§3.2, Algorithm 1 | C (A for the smoothing step) | Robots in free space | PIBT on contention; smoothing only where agents are not interacting | All agents' full PIBT trajectories (centralised post-process) | `[not stated in paper]` beyond citing PIBT; repair uses "a priority-based scheme", unspecified (§3.2) | 200 in a table (Table 4). ⚠ Abstract says "over 500" | No | **The split, yes**: a cheap mover in free flow, the rule only inside the interaction zone. Authors: heterogeneity "is not supported in PIBT" (§6) |
| **SR20** | **Asynchronous push (LSRP)**: PIBT's push, for actions of different durations: plan only the agents whose action ends now; a pusher waits until the pushed agent's move completes and caches its own wait-then-move. | [Zhou-LSRP] §4.2–§4.3, Algorithms 1–3 | C | Abstract agents on a graph | On contention, at the planning timestamp of the agents involved | Graph; agents' states with timestamps; known action durations; shared global clock (§2) | Initial priorities "can be set in different ways (such as using random numbers)" (§4.2); must be unique (§5) | 1,000, with the swap variant, 30 s limit (§7.1) | No | **Yes, where agents act on different clocks or speeds.** Plain version can loop forever (§6, Fig. 3) |
| **SR21** | **Learned planning order (S2AN)**: a network chooses which agent plans next; each planned agent treats earlier agents' paths as soft obstacles; leftover collisions are repaired by sending colliding agents back to their starts. | [Yang-S2AN] §4.1, §4.3, §4.5 | C (A) | Abstract agents on a grid | Offline, once per instance | **The whole instance**: map, all starts, all goals | The network's output; no hand-written rule (§4.4) | 250 on a 32×32 map (§5.2) | No | **No.** A trained network for one map family; nothing transfers without retraining |
| **SR22** | **Mutex-derived constraints in conflict-based search**: detect that two agents' cost-bounded paths cannot coexist by propagating mutual exclusions through their path diagrams; resolve by constraint sets built from those exclusions. | [Zhang-Mutex] §3, §5, Algorithms 1–5 | C | Abstract agents on a grid | When two planned paths are found to conflict | Complete: graph, all starts, goals and current plans, held centrally | None behavioural — the search branches on both alternatives (§2.2) | In figures only, not recoverable: `[not stated in text]` | No | **No as a runtime rule** (centralised optimal search). Its conflict typology (Fig. 1) is reusable as test cases |
| **SR23** | **Token passing**: one agent at a time holds a shared token containing every agent's path; the holder plans a path avoiding all of them and writes it in. | [Ma-TokenPassing] §4.1, Algorithm 1 | B (A) | Warehouse robots | Pre-emptive — whenever an agent finishes its path | The token: all other agents' full remaining paths, tasks, assignments | **Order in which the token is handed out** — "one after the other"; order among simultaneous requesters `[not stated in paper]` | 500, 6,121 ms per timestep (Fig. 7) | No | **Mechanism yes, preconditions no.** Needs a shared blackboard and one parking spot per agent (Definition 1) |
| **SR24** | **Decision-causal communication trigger**: ask a neighbour for a message only if masking that neighbour out of your observation would change the action you would take. | [Ma-DCC] §IV-A, Eq. 1 | B | Abstract agents on a grid | Every timestep, per neighbour in a 9×9 view | Local observation; then the neighbour's message | n/a for the trigger. The action itself comes from a trained network: `[not stated]` as a rule | 128 on an 80×80 map (§V-A) | No | **The trigger, yes** — a domain-free test for "does this neighbour matter to me". The policy does not port |
| **SR25** | **Detect-then-rotate deadlock resolution**: run a collision-constrained controller; when velocity is near zero away from the goal, declare deadlock; rotate the robots about each other at the safety distance until they have swapped; resume. | [Grover-Deadlock] §6, Fig. 9; Definition 1 | C (A) | Robots | After a deadlock is detected | All robots' positions; own goal | ⚠ **Direction of rotation `[not stated in paper]`** in the sections read (derivation deferred to an earlier paper). Random perturbation is explicitly rejected (§2, §6) | **3** (§6) | No (hardware test) | **The finding, more than the rule**: symmetric conflicts necessarily deadlock under reactive avoidance (Theorem 1). The rotation needs free space on both sides |
| **SR33** | **Stall detection, then local path-finding among the stalled**: avoid with ORCA; if own average speed over 250 steps is near zero *and a neighbour reports the same*, the agents nearby share positions and goals, each builds the same small grid problem and solves it with the same deterministic solver, they follow the plan, then resume. | [Dergachev-ORCA-MAPF] §IV-A–§IV-C, Algorithm 1 | B (C, A) | Abstract disc agents in continuous 2-D space | After a deadlock is detected | Neighbours' positions and velocities; their **reported average speeds**; then participants' **positions and waypoint goals**, exchanged; a grid map known to all | **Random**: "Each agent in the MAPF mode is randomly assigned a unique priority" (§IV-B a); priority gives first choice of start and goal cell | 40 (§V) | No | **Yes — the architecture closest to a pedestrian simulator.** In a simulator the exchange is unnecessary. Plain ORCA "was not able to solve a single instance" with 40 agents and three narrow passages (§V) |

### S4 — traffic and autonomous vehicles

| # | Rule name | Source (paper, locator) | Category | Domain | Trigger | Information required | Tie-break | Max agents tested | Validated against real data? | Portable? `[inference]` |
|---|---|---|---|---|---|---|---|---|---|---|
| **SR26** | **Safe following distance and proper response**: keep a gap in which you could stop if the one ahead braked hardest; the moment the gap is lost, brake. | [ShalevShwartz-RSS] `[preprint]` §3.1, Definition 1, Lemma 2; §3.5, Definition 10 | A | Road vehicles | Continuous check; response at the "Danger Threshold time" | Others' positions and velocities; four agreed dynamics bounds and a response time | n/a (same-direction case is asymmetric by construction: the rear one is responsible) | None — no evaluation; proofs only | No | **Structure yes, parameters no.** A stopping-distance rule for any agent with bounded acceleration |
| **SR27** | **Route priority, "given, not taken"**: where two routes cross, the vehicle on the non-priority route must be able to stop short of the other route, and must brake when it cannot; but a priority holder must still brake for someone already in the junction if it safely can. | [ShalevShwartz-RSS] `[preprint]` §3.7, Definitions 16–18; §3.7.1, Fig. 9; §3.8 for pedestrians | A (C) | Road vehicles; pedestrians (§3.8) | When the distance between the two becomes unsafe | As SR26, plus **the priority relation between routes** (layout, signs, signals) | Priority route first; else whoever is "in front" (nearer the crossing region, Definition 16); else **both brake** (Definition 18) | None — no evaluation | No | **Yes, if a priority relation exists.** A corridor supplies none — which is the FYP's opening |
| **SR28** | **First-in-first-out control-zone scheduling**: vehicles enter the merging zone in the order they entered the control zone; each takes the earliest safe slot after its predecessor. | [Malikopoulos-SignalFree] §2 (Eq. 1), §3 (Eq. 14, Definition 3) | B (C) | Automated vehicles at an unsignalled intersection | Once, on entering the control zone | Own state; gap to the vehicle ahead; **and, relayed by a coordinator, the predecessor's assigned entry time and one's queue position** | **Arrival order; simultaneous arrivals indexed at random by the coordinator** (§3) | 448 vehicles over a run, 450 veh/h per lane (§4) | No — real intersection *geometry*, synthetic traffic (§4) | **Yes, the skeleton.** In a simulator the coordinator is free. Authors name FIFO as the limitation (§5) |
| **SR29** | **First-in-first-out crossing order (as a baseline)**: vehicles cross in the order they arrive. | [Xu-TreeSearch] §I, §III-B; results §IV-C, Table I | C | Automated vehicles at an unsignalled intersection | On arrival | Arrival order | Arrival order; simultaneous arrivals `[not stated in paper]` | 20-minute runs at up to 450 veh/(lane·h) (Table I); count `[not stated]` | No | **Yes — and measured.** Delay 1.3 s at 150 veh/(lane·h), 39.8 s at 300 (Table I); ranks 4,563,421,793rd of ~10 billion orders for 20 vehicles (§IV-C) |
| **SR30** | **Searched crossing order (tree search with heuristics)**: search the tree of crossing orders by Monte Carlo tree search, guided by two heuristics: *nearest on its lane first* and *earliest desired arrival at a shared subzone first*. | [Xu-TreeSearch] §III-A–§III-B, Algorithms 1–2 | B | Automated vehicles at an unsignalled intersection | Every 2 s, for all vehicles in the control zone | Positions, velocities **and intentions** of all vehicles, by V2V (§II) | **Random** among candidates when no vehicle is earliest at all its subzones (Algorithm 2 step 2) | 30 in the parameter study (§IV-B) | No | **No** as a per-agent rule (a centralised optimiser) |
| **SR31** | **Arbitrated turn assignment by arrival time (AROW)**: vehicles arriving within a 2 s window elect an arbitrator by a shared heuristic; it assigns crossing turns earliest-arrival-first; later arrivals wait for the next round. | [Shah-AROW] §IV-B to §IV, stage S31; heuristics H1, H2 | B (C) | Connected vehicles at a four-way stop | When two or more arrive "at similar time intervals" | Each vehicle's arrival timestamp and unique identifier, exchanged by V2X; comparable clocks | **Arbitrator (H1): the last to arrive; equal timestamps → lowest identifier. Turns (H2): earliest first; equal timestamps → random** — "Based on user preference, it can be changed" | 16 (§VI-A) | No — the default all-way stop is called "similar to the real-life human behavior" without data (§VI-B.3) | **Yes, with the messaging removed** — a simulator already knows who arrived when |
| **SR32** | **Restart-then-fallback on non-compliance**: if a vehicle crosses out of turn, the others restart the round; after two restarts, abandon the protocol and fall back to first-in-first-out. | [Shah-AROW] §IV-F; §VI-A (`AROW_thresh = 2`); §VI-B.3 | C | Connected vehicles at a four-way stop | After a rule is broken | An exit message from the offender (in a simulator: the observation that it moved) | Fallback is arrival order | 16; non-compliance probability up to 0.25 (§VI-A) | No | **Yes.** The only procedural treatment of rule-breakers in this review |
| **SR34** | **Right-of-way priority order from traffic law**: give way, in this order of importance, to a vehicle (A) already engaged in the intersection, (B) on your left-hand side, (C) closer to the intersection by more than 2 m; then decide in that order. | [Pruekprasert-RightOfWay] §II-C, §IV-A.1; decision game §III | C (B, weakly — turn signals) | Autonomous vehicles at an unsignalised four-way intersection | Every 0.1 s while approaching or inside | Every vehicle's exact position, speed, acceleration and entering/inside/leaving status; intended routes from turn signals | **Presence, then side, then distance.** The side rule is switched off when all four approaches are occupied (§IV-A.1); the remainder is a **random** order. Source: Japanese traffic rules; "left in Japan, right in Australia" (§II-C) | **4** (§II-A) | No — taken from a driving guide, not from observed drivers | **The pattern, yes; the content, no.** Three tests on observable geometry. The designated side is a per-country convention |
| **SR35** | **Randomised standstill breaker**: if every vehicle is stationary and behaving as predicted, a vehicle that believes it has top priority (or saw the standstill one step earlier) accelerates with probability 0.25. | [Pruekprasert-RightOfWay] §III-E | C | Autonomous vehicles at an unsignalised four-way intersection | After a standstill | That all velocities are zero and all predictions held | **This row *is* a tie-break: a 1-in-4 chance per step.** Justified by an impossibility result for deterministic symmetric choice (§III-E, citing Lehmann & Rabin 1981) | 4 | No | **Yes.** Needs only "nobody is moving" |

**Not in the table, by rule 1:** [Ahmed-MergeAssist] (S4, `[preprint]`). It describes a three-way
handshake that circulates a merging order, but **does not state the rule that produces the
order** (Methodology), so there is no rule to put in a row. The two surveys
([Wang-MAPFSurvey], [Mariani-CoordSurvey]) contribute no rows of their own; rules known only
through them are in §4.

---

## §2. Apparent correspondences — NOT merged

In each case: what looks the same, and what is actually different.

**C1. SR1 ↔ SR11 ↔ SR6 (all "ORCA").** SR1 is ORCA re-implemented without change; SR11 is a
practitioner's explanation of what ORCA's constraint amounts to (keep the passing side); SR6 is
ORCA with the fixed half-share replaced by an adaptive one. `[inference]` SR1 and SR11 very likely
describe the same rule from two angles — but one source states it as geometry and the other as a
tie-break principle, and only SR11 reports the corner-deadlock failure. SR6 is a different rule
that *contains* ORCA as the special case α = 0.5 (its §IV-A). **Do not merge.**

**C2. SR10 (half-dodge) ↔ SR6 (adaptive share).** Both divide the avoidance effort between two
agents. SR10 fixes the split at one half and *assumes* reciprocity; SR6 estimates the split
because reciprocity cannot be assumed. The chapter behind SR10 independently notes that the weights
need not sum to 1 (§19.7.1). **Do not merge.**

**C3. SR18 (PIBT) ↔ SR19 ↔ SR20 (its extensions).** SR19 and SR20 both use PIBT's arbitration
unchanged in kind. They differ in what they add (a smoother; asynchronous timing) and in what
they guarantee (SR19 nothing; SR20 weak termination on a narrower graph class). **Do not merge.**

**C4. SR28 ↔ SR29 ↔ SR31 (all "first come, first served").** The same ordering principle in three
papers, and the differences are exactly what a simulator designer needs to know:
- SR28 fixes order at entry to a *zone* 245–400 m before the conflict, and breaks ties at random.
- SR29 is the principle as a bare baseline, with tie-breaking unstated — and is the only one with
  **measured cost**.
- SR31 applies it only among vehicles arriving within a 2 s *window*, and breaks ties at random or
  by identifier.

`[inference]` These are one principle with three different definitions of "arrived" (crossed a
distant line; unspecified; came within 10 m inside a time window). **Do not merge** — "when does
an agent count as having arrived" is the substantive design choice, and the papers disagree.

**C5. SR3, SR4, SR7, SR9, SR20, SR28, SR30, SR31, SR33, SR34, SR35 (random tie-breaks).** Eleven
rules in three sub-areas break symmetric cases by a random draw. They randomise different things —
a waypoint offset (SR3), a detour point (SR4), perceived velocity (SR7), dodge side (SR9), initial
priority (SR20), queue index (SR28), rollout candidate (SR30), turn order (SR31), a priority
number (SR33), the residual order once the legal tests are exhausted (SR34), and whether to move
at all this step (SR35) — so they are not one rule. But as a pattern it is the single most common
tie-break in this catalogue, and one source gives a reason: deterministic choice cannot break a
perfectly symmetric standstill ([Pruekprasert-RightOfWay] §III-E). See
[research-gap.md](research-gap.md) §5.

**C6. SR14 (pedestrian yields to vehicle) ↔ SR27 (non-priority route yields).** Both resolve a
conflict by a fixed asymmetry between the parties. SR14's asymmetry is by **agent type**, decided
by the game's designers and undocumented for the other party. SR27's is by **location** (which
route), supplied by infrastructure, with an explicit duty on the priority holder too. **Do not
merge.**

**C7. SR15 (non-intersecting splines) ↔ SR3 (perturb shared waypoints).** Both remove conflicts at
planning time by keeping routes apart. SR15 is absolute and hand-authored; SR3 is a randomised
reduction. **Do not merge.**

**C8. SR25 ↔ SR33 ↔ SR35 ↔ SR5 (all "detect a stall, then do something different").** Four rules
share the two-stage shape. They detect differently — near-zero commanded velocity away from the
goal (SR25); near-zero *average* speed over 250 steps confirmed by a neighbour (SR33); everyone
stationary and predictable (SR35); own speed below a threshold in a dense area (SR5). And they
resolve differently — rotate about each other; solve a local path-finding problem; accelerate with
probability 0.25; re-plan the route. `[inference]` The detectors look interchangeable and the
resolvers do not: SR25 needs free space on both sides, SR5 needs an alternative route, SR33 needs
a grid and shared goals, SR35 needs nothing. **Do not merge.**

**C9. SR27 ↔ SR34 (both "right of way").** Both give precedence at a junction from the road rules.
SR27 takes the priority relation as an *input* supplied by infrastructure and proves safety given
it; SR34 *states* a particular country's relation (presence, then left-hand side, then distance)
and simulates it. SR27 says nothing about which side has priority; SR34 says nothing about safe
distances. `[inference]` They are complementary halves and would compose. **Do not merge.**

**C10. SR32 ↔ SR34 (both handle agents that break the rule).** SR32 detects an out-of-turn crossing
and restarts the protocol, twice at most. SR34 has rule-following vehicles re-fit their belief
about the priority order to what they observe (its §IV-B.2). One is procedural, the other
inferential. **Do not merge.**

---

## §3. Cross-reference to issue #20's catalogue (theory ↔ implementation)

Issue #20's rules are R1–R14 in
[`../game-theory/candidate-rule-catalogue.md`](../game-theory/candidate-rule-catalogue.md). The
pairings below are `[inference]` throughout: no paper on either side cites the other. They are
offered as correspondences for supervisor review, **not** as claims that the rules are the same.

| Theory (issue #20) | Implementation (this issue) | What corresponds | What does not |
|---|---|---|---|
| *(an open question, not a rule)* — #20's search log §10, risk R6: "No arrival-order rule was found anywhere". Not to be confused with catalogue rule R6 (threshold aggregation) | **SR28, SR29, SR31** | **The rule #20 could not find in the game-theory literature is the standard baseline in traffic.** It also appears in the MAPF survey as a named fixed-priority scheme ([Wang-MAPFSurvey] §3.4, citing a pre-window source) | It is used here as an engineering default and a fairness device, not derived as an equilibrium. #20's related finding — that the "host concedes" norm evolves more readily than "owner keeps" — is not contradicted, only not addressed |
| **R7** social law: a fixed function from own state to action, agreed offline (*keep right*) | **SR15** (design-time route separation); **SR11** (keep the current passing side); **SR26–SR27** (RSS); **SR34** (legal right-of-way order) | All are standing conventions needing no runtime exchange. SR15 is R7's offline synthesis done by hand. **SR34 is the closest match to R7's own example**: #20 recorded R7's canonical instance as *keep to the right*, and SR34's middle test is *give way to the left* — a side convention fixed in advance by law | R7 takes only the agent's *own* state; SR11, SR26–27 and SR34 need the other's position |
| **R9** strategy-dependent cell contention: when *k* agents want one cell, draw the winner from a matrix keyed on their cooperate/defect labels | **SR18** PIBT | Both arbitrate contention for one cell among several agents, with no negotiation | R9 is stochastic and keyed on a behavioural label; SR18 is deterministic and keyed on waiting time. R9 can leave the cell empty; SR18 always moves the highest-priority agent |
| **R12** Stackelberg priority: the faster party leads | **SR27** route priority; **SR31** arrival-time priority; **SR34** legal priority order | All assign precedence from an observable asymmetry. **SR34 is structurally the same kind of object as R12**: a one-round sequential game solved by backward induction in priority order (its §III-A) is a leader–follower game | The asymmetry differs every time: speed (R12), route (SR27), arrival time (SR31), presence-then-side-then-distance (SR34). That is four different answers to "who goes first" |
| **R13** reactive angular yield: decelerate for an agent already crossing in front | **SR27**'s "given, not taken" clause; **SR14**'s "go behind a crossing vehicle" | All three say: whoever is already in the contested space is yielded to | R13 has explicit angle thresholds validated on 117 real scenarios; SR27 is proved, not tested; SR14 is a design note |
| **R5** defer to the higher resource-holding potential; **R1/R2** role asymmetry | **SR14** (pedestrian yields to vehicle); **SR16** (trait-weighted cost) | Precedence from an attribute of the agent rather than of the situation | R5 is an evolved equilibrium; SR14 and SR16 are designer choices with no stated justification |
| **R3** correlate on an external public cue | Traffic lights as treated in **SR27** (§3.7.1); the random index in **SR28** | An external signal breaks the symmetry | SR27 adds that the signal does not override presence in the junction |
| **R4** private recommendation from a trusted device; humans comply 70–75% | **SR28**'s coordinator; [Ahmed-MergeAssist]'s driver advisories; **SR32**'s non-compliance handling | A third party issues each agent its instruction | #20 has compliance *data* (192 subjects). Here compliance is either assumed (SR28) or a simulation parameter set to 0.1 or 0.25 with no empirical basis (SR32). **#20's measured figure would be a defensible input for SR32's parameter** |
| **R8 / R14** sequential chicken: a non-zero collision probability is necessary | **SR6** with a mis-set prior; **SR27**'s both-brake case; **SR35** | #20's theory says safe-and-live cannot both be guaranteed without a signal; the implementations show both failure modes — SR6 collides when its prior is wrong (§V-A), SR27 stops both parties — and SR35 is the engineering answer: randomise who moves, citing an impossibility result for deterministic symmetric choice | SR35 randomises *moving*, not *colliding*: its paper reports no collisions among rule-following or selfish vehicles (§V-B) |

**The one substantive update this cross-reference makes to issue #20:** its open question (search
log risk R6) — whether an arrival-order rule exists — is answered. It exists, it is widely used, and
[Xu-TreeSearch] gives numbers for what it costs.

---

## §4. Rules known only at second hand — deliberately NOT in the table

Kept out of §1 because I did not read their sources. Listed so they are not lost.

| Rule | Known only from | Why not in §1 |
|---|---|---|
| **Auction for right-of-way**: vehicles bid for the intersection cells they need; among colliding trajectories the highest bidder goes first. | [Mariani-CoordSurvey] §3.2.2, citing its refs. [98], [23], [20] | Original papers not identified or opened. The survey warns the mechanism can starve low bidders |
| **Reservation with an intersection manager**; cells granted "roughly" first-in-first-out. | [Mariani-CoordSurvey] §3.2.1; [Xu-TreeSearch] §I — both citing Dresner & Stone | Pre-window; see [pre-window-foundations.md](pre-window-foundations.md) P14 |
| **Transient leader election** by distance to the intersection and speed. | [Mariani-CoordSurvey] §3.2.1, citing its ref. [94] | Not opened. SR31's H1 is an in-window, read-at-source instance of the same device with a different criterion |
| **Argumentation between vehicles** about who should give way. | [Mariani-CoordSurvey] §3.2.3, citing its ref. [62] (the survey authors' own proposal) | Not opened; described by its authors as "still at the conceptual level" |
| **Mechanism-design priority with a VCG-like tax.** | [Wang-MAPFSurvey] §3.4.4, citing Friedrich et al. (2024) | Not opened |
| **winPIBT** — PIBT over a window of several steps. | [Wang-MAPFSurvey] §3.4.4 | Not opened |
| **Delay-based intersection scheduling with priority to the busier lane** (DCIM). | [Shah-AROW] §VI-B.3, citing its ref. [32] | Not opened. Described only by a competitor, which reports that it starves low-priority lanes |
| **"Move right if in conflict"** as an emergent convention under broadcast communication. | [Wang-MAPFSurvey] §6.5 | **The survey gives no citation for it.** It is a remark, not a sourced rule |
| **Keep-right traffic rule in pedestrian lattice models.** | [Xu-AVM] §1, citing its refs. [20], [21] (Muramatsu et al.; Fang et al.) | Pre-window and not opened. Noted because it is the only mention of a side-convention for *pedestrians* in anything I read |
