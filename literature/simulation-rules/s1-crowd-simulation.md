# S1 — Pedestrian and crowd simulation

> **Draft pending supervisor review.** Prepared for issue
> [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). Read date for every entry:
> 2026-10-04.

Companion files: [S2](s2-games.md) · [S3](s3-mapf-robotics.md) · [S4](s4-traffic-vehicles.md) ·
[rule catalogue](rule-catalogue-simulation.md) · [category summary](category-summary.md) ·
[research gap](research-gap.md) · [pre-window foundations](pre-window-foundations.md) ·
[missing papers](missing-papers.md) · [search log](search-log.md) · [refs](refs-simulation-rules.bib)

## How to read this file

- Categories **A / B / C** are the issue's (see [category-summary.md](category-summary.md) §1).
- **Locators** point into the cached text named on each entry's "Read from" line.
- **Four of the six entries were read as arXiv copies of papers that are also published.** Each
  entry says which. Section, equation and figure numbers are the arXiv copy's and should be
  re-checked against the publisher's version before the report quotes them.
- **Equations.** PDF-to-text extraction dropped most mathematical symbols. Where an equation's
  body did not survive, I describe the rule in the words of the surrounding prose and cite the
  equation number the prose gives; I do not reconstruct symbols I could not read.
- `[inference]` marks my judgement, not the paper's claim.
- **A boundary note for this whole sub-area.** Every method here is a *continuous* avoidance rule,
  so every entry is primarily **A**. That uniformity is a finding, not an oversight; see
  [category-summary.md](category-summary.md) §3.

Contents: [Charlton-FastCrowd] · [Sung-ArrivalTime] · [Sudkhot-BDI-RVO] · [MartinezBaselga-AVOCADO]
· [Tordeux-CFSM] · [Xu-AVM] · excluded seed (CrowdVLA) · not-obtained stubs

---

### [Charlton-FastCrowd]: Fast Simulation of Crowd Collision Avoidance

- Authors / Year / Venue: John Charlton, Luis Rene Montana Gonzalez, Steve Maddock, Paul Richmond /
  2019 / *Advances in Computer Graphics (CGI 2019)*, Lecture Notes in Computer Science, Springer,
  pp. 266–277.
- Link: https://doi.org/10.1007/978-3-030-22514-8_22 | https://arxiv.org/abs/1908.10107
- Peer-review status: published at CGI 2019 (Springer LNCS; Crossref record
  `refs/sr_cr_10_1007_978-3-030-22514-8_22.json`). The issue's seed was the arXiv link; the
  published version exists and is cited here.
- Verified: yes (full text read). **Read from** `refs/sr_fastcrowd_1908_10107.txt` (arXiv v1).
- Sub-area: S1
- **Primary category: A.**
- Category justification: each agent "selects from the permissible velocities the one closest to
  its desired velocity", where permissible means no collision within a look-ahead time τ (§3). The
  rule runs every iteration on *predicted* collisions; no contention state is created. Agents only
  "observe" neighbours' radius, position and velocity (§3) — publicly visible physical state, so
  not B. (The paper calls this "communication between people" and "messages", but that is the
  FLAME GPU framework's term for the data structure that implements observation — §3, Fig. 2.)
- Domain simulated: pedestrians. [§1, §4]
- The rule, stated precisely: this is ORCA (van den Berg et al., a pre-window method — see
  [pre-window-foundations.md](pre-window-foundations.md)) re-implemented for the GPU; the paper
  does not change the rule. As the paper states it: for each neighbour within the observation
  radius, compute a half-plane of velocities guaranteed not to collide within τ; choose the
  velocity inside all half-planes that is closest to the desired velocity, by linear programming;
  if the half-planes have no common point, choose the velocity that "least penetrates" them (§3,
  Fig. 1). The paper's contributions are a batch GPU linear-program solver and grid-bin spatial
  partitioning (§3).
- Trigger condition: continuously, each simulation iteration, on predicted collision within τ. [§3]
- Information required: each neighbour's radius, current position and velocity, within an
  observation radius; own goal and desired speed. No priorities, no shared clock beyond the
  simulation step. [§3, Fig. 2]
- Tie-breaking: `[not stated in paper]`. The paper says nothing about symmetric head-on encounters.
- Guarantees claimed: collision-free within time τ when the half-planes intersect; **"there is no
  guarantee of collision-free motion"** when they do not, which the paper attributes to "large
  densities of people" (§3). No deadlock or completeness claim.
- Evaluation: (i) a two-way crossing with 2,500 people, in a homogeneous variant (radius 0.5 m,
  desired speed 1.0 m/s) and a variant with three radii and three speeds (§4, Figs. 3–4); (ii) an
  eight-way crossing with 10,000 people (Fig. 5). Both are assessed **by appearance** — "Various
  expected behaviors such as lane formation can be observed" (§4). (iii) Frame time against a
  multi-core CPU ORCA across agent counts (Fig. 6).
- Does it work: the speed-up is supported; the behaviour is not measured. Up to 30× faster than
  multi-core CPU; the CPU is faster below about 2 × 10³ agents (§4). No collision count, flow, or
  density statistic is reported. ⚠ **Internal inconsistency on the headline number:** the abstract
  says "over 100,000 people to be simulated in real time (60 frames per second)"; the results say
  the GPU ran "at close to 30 frames a second (33ms per frame) for up to 5 × 10⁵ agents" (§4). I
  record both and do not reconcile them.
- Validated against real human or real traffic data: no. Realism is asserted from visual
  inspection only (§4).
- Scalability: up to 5 × 10⁵ agents at about 33 ms per frame, limited by 4 GB of GPU memory, on an
  NVIDIA GTX 970 (§4). Scaling beyond that is stated as an expectation, not a result (§4, §5).
- Domain assumptions that limit portability: continuous 2-D space; holonomic disc agents; lock-step
  update; every agent runs the same rule; agents are removed on reaching their goal (§4).
- Portability to a generic simulator: [inference] high, and already demonstrated informally — the
  same ORCA rule appears in robotics ([MartinezBaselga-AVOCADO] builds on it) and in games
  ([SunshineHill-RVO-ORCA] in S2). It ports because it needs only positions and velocities. What
  it does not provide is any answer to *who goes first* when the half-planes leave no room.
- Limitations and future work stated by the authors: memory is the limit; "more computationally
  expensive steering models would include more realistic motion such as side-stepping, more
  realistic densities, and less probability of collisions" (§5).
- Relevance to this FYP: [inference] **scalability evidence, and a baseline.** It shows the
  avoidance layer is not the obstacle to 10,000 agents — the issue's own reason for including it.
  It also shows, by omission, where the gap is: the paper's dense-case fallback is "no guarantee".
- BibTeX: `charlton2019fastcrowd`

---

### [Sung-ArrivalTime]: Crowd Simulation with Arrival Time Constraints

- Authors / Year / Venue: Mankyu Sung, SeongKi Kim / 2020 / *Symmetry* 12(11), 1804 (MDPI).
- Link: https://doi.org/10.3390/sym12111804
- Peer-review status: published at *Symmetry* (MDPI journal; received 12 October 2020, accepted 29
  October 2020 — first page; a 17-day turnaround).
- Verified: yes (full text read). **Read from** `refs/sr_arrivaltime_symmetry.txt` (the published
  version). ⚠ **Every equation body was lost in extraction** (Eqs. 1–8). The rule below is from the
  prose of §3.4–§3.5.
- Sub-area: S1
- **Primary category: A.**
- Category justification: collision avoidance is ORCA unchanged; the paper adds a speed-adjustment
  layer for timing (§3.2, §3.5). Nothing is arbitrated after contention.
- Domain simulated: game / film characters ("agents"); drones are mentioned as a use. [Abstract, §1]
- The rule, stated precisely: (1) offline, build a probabilistic roadmap; where two agents' paths
  share a waypoint, move the second agent's waypoint to a random point within radius *r* of the
  original, to reduce later collisions (§3.3, Fig. 3). (2) Each step, test whether the current
  waypoint is *visible*, meaning no other agent lies within one agent-radius of the straight line
  to it (§3.4, Fig. 5); if visible, raise the maximum-speed parameter, otherwise keep the fixed
  one. (3) Run ORCA to get a collision-free velocity (§3.4). (4) Rescale that velocity by the gap
  between the agent's estimated arrival time and the crowd's average, offset by its assigned time
  constraint, **only when the waypoint is visible** (§3.5).
- Trigger condition: continuously. The timing adjustment is suspended whenever another agent
  blocks the line to the waypoint, i.e. collision avoidance takes precedence. [§3.5]
- Information required: neighbours' positions, velocities and radii (ORCA); **every agent's
  estimated arrival time**, to form the average (§3.5) — a global quantity; a time constraint per
  agent supplied by the user (§3.6).
- Tie-breaking: for shared waypoints, the *second* path to use a waypoint is the one perturbed
  (first-come keeps it), by a random offset (§3.3). For agent–agent encounters:
  `[not stated in paper]` (inherited from ORCA).
- Guarantees claimed: none formal. The abstract's "guarantees the arrival order" is not backed by a
  proof, and §5 concedes "there may be cases where the time constraint cannot be satisfied".
- Evaluation: scenarios with 10 agents (line, ordered line, circle) and 30 agents (obstacles) —
  §4, Figs. 8–12. Frame rate from 5 to 100 agents: "the framerate did not go below 40 frames/s"
  at 100 (§4, Fig. 14). "During the simulation, no collisions were observed" (§4). A usability test
  of the interface with **three** students (Table 2).
- Does it work: in the sparse cases shown. **Stated failure:** "when a large number of agents are
  densely packed in a highly complicated environment they get stuck and barely move to their
  targets. In this case, adjustment of velocities cannot be carried out as all agents are engaged
  in avoiding collisions" (§5). The paper also notes of plain ORCA that "there are still some cases
  when they get stuck" (§2). The authors plan to "find a density threshold parameter within which
  the proposed algorithm would continue to work" — it is not yet known (§5).
- Validated against real human or real traffic data: no. [§4]
- Scalability: 100 agents, at least 40 frames/s including rendering (§4, Fig. 14). The abstract's
  claim to handle "many agents" goes no further than that.
- Domain assumptions that limit portability: flat 2-D environment (§5); holonomic discs; a
  centrally known average arrival time; user-supplied targets.
- Portability to a generic simulator: [inference] the timing layer is a wrapper around any
  velocity-choosing rule and would port; it is not a conflict rule. What is relevant is the
  evidence of what happens to ORCA-based agents under density (they stall), and the
  first-come-keeps-the-waypoint device, which is an arrival-order tie-break applied at planning
  time.
- Limitations and future work stated by the authors: non-flat terrain; unsatisfiable constraints;
  GPU implementation; real character motion. [§5]
- Relevance to this FYP: [inference] minor. Baseline evidence of the stall problem, in a paper that
  is otherwise about something else. ⚠ The comparison in Table 1 (roadmap construction time versus
  A*) and the "first that support arrival order" claim (Abstract) are the authors' and I have not
  checked them.
- BibTeX: `sung2020arrivaltime`

---

### [Sudkhot-BDI-RVO]: Collision Avoidance and Path Planning in Crowd Simulation

- Authors / Year / Venue: Panich Sudkhot, Kok Wai Wong, Chattrakul Sombattheera / 2023 / *ICIC
  Express Letters* 17(1), 13–24.
- Link: http://www.icicel.org/ell/contents/2023/1/el-17-01-02.pdf (DOI on the first page:
  10.24507/icicel.17.01.13)
- Peer-review status: published at *ICIC Express Letters*. As the issue asked, noted: **this is a
  smaller journal** (a letters journal; received May 2022, accepted July 2022). Included because
  the rule description is substantive: it has pseudocode (Algorithm 1).
- Verified: yes (full text read). **Read from** `refs/sr_icicel_2023.txt`. ⚠ **Table 3's numbers
  were lost in extraction**; the percentages quoted from §5.2 are from the prose.
- Sub-area: S1
- **Primary category: A** (secondary: C).
- Category justification: the main rule diverts an agent *before* it reaches a dense area —
  "Our method allows agents to avoid congestion before reaching it" (§5.1) — which is A. A second
  branch fires only after the agent has already been slowed below a speed threshold, and re-plans
  its route (§4.2, Algorithm 1 lines 23–26); that is a response to an existing jam, hence C.
- Domain simulated: pedestrians in an urban scene. [§5.3]
- The rule, stated precisely: each step, set the preferred velocity toward the current sub-goal, or
  the global goal if there is none (Algorithm 1 lines 2–13). Count the agents in a forward sector
  of the agent's sensing range (`getAgentCondense`, §4.1–§4.2). If the count exceeds
  `CONDENSE_THRESHOLD` and the agent has no sub-goal, create one at a **random** angle and
  **random** distance derived from the density reading and push it onto the plan stack (lines
  15–22). If, in addition, the agent's speed has fallen below `VELOCITY_THRESHOLD`, call
  `generatePlan` to compute a new route (lines 23–26). Underneath, RVO handles collision avoidance
  (§4.2). ⚠ The left-or-right choice is given as a formula (end of §4.2) that did not survive
  extraction legibly; I do not restate it.
- Trigger condition: predicted congestion ahead (density threshold) for the sub-goal; **existing**
  slowdown (velocity threshold) for the re-plan. [Algorithm 1; Table 1]
- Information required: positions of agents inside a forward circular sector (§4.1); own speed; a
  navigation graph of the static scene (§3.2).
- Tie-breaking: **random.** The detour point is drawn with `getRandom` for both angle and distance
  (Algorithm 1 lines 17–18).
- Guarantees claimed: none.
- Evaluation: six small scenes with 3, 4, 5, 6, 50 and 100 agents exchanging positions through a
  centre (§5.1, Table 2); a four-group "block" scene with 100 agents, with and without obstacles
  (§5.2); large 2-D and 3-D city scenes (§5.3); a performance limit study (§5.4). Baseline: RVO2.
  Table 2, simulation steps, RVO2 versus this method: S2 (4 agents) 14,654.25 vs 371.0; S3 (5
  agents) 37,176.5 vs 377.25; S6 (100 agents) 1,205.0 vs 710.25.
- Does it work: against the one baseline, yes, and the baseline's failure is itself informative.
  Plain RVO2 takes about 40× and 100× more steps than the proposed method with **only four and
  five agents** meeting head-on (Table 2, S2–S3). The paper describes this as "the traditional
  approach is momentarily deadlocked as the agent moves towards the center of density" (§5.1).
  ⚠ Table 2 is not monotone — RVO2 needs fewer steps at 6, 50 and 100 agents than at 4 or 5 — and
  the paper does not explain why. I report the numbers as printed.
- Validated against real human or real traffic data: no. The claim that the method makes agents
  move "similarly to real world movement" (§4.2) is not tested.
- Scalability: ⚠ **the paper gives three different figures and they do not agree.** Abstract and
  §6: "up to 40,000 agents". §5.4: visualised at 24 FPS for 600 agents; rendering falls to 0.4–0.04
  FPS from 19,600 to 102,400 agents; and "we have 1 GB of RAM and can carry out simulation up to
  720000 agents". §5.3 says "ten thousands of agents are simulated" in the 3-D scene. I record
  40,000 as the authors' headline claim and flag it as not consistently supported by §5.4.
- Domain assumptions that limit portability: continuous 2-D; RVO2 underneath; a pre-built
  navigation graph from polygon corners (§3.2).
- Portability to a generic simulator: [inference] the pattern — *look ahead for density, and if it
  exceeds a threshold, take a randomised detour* — is domain-free and cheap. It only works where
  there *is* somewhere else to go. In a doorway or a single corridor there is no detour, so it
  cannot resolve the FYP's deadlock cases.
- Limitations and future work stated by the authors: handle more agents; improve visualisation;
  improve the internal planning algorithm. [§6]
- Relevance to this FYP: [inference] its most useful content is the baseline row: independent
  evidence that reciprocal velocity avoidance alone performs very badly in symmetric head-on
  meetings of a handful of agents. Treat the paper's own claims with the caution its venue and
  internal inconsistencies warrant.
- BibTeX: `sudkhot2023bdirvo`

---

### [MartinezBaselga-AVOCADO]: AVOCADO: Adaptive Optimal Collision Avoidance driven by Opinion

- Authors / Year / Venue: Diego Martinez-Baselga, Eduardo Sebastián, Eduardo Montijano, Luis
  Riazuelo, Carlos Sagüés, Luis Montano / 2025 / *IEEE Transactions on Robotics*. Volume and pages
  `[not identified]` — the copy read gives only the DOI.
- Link: https://doi.org/10.1109/TRO.2025.3552350 | https://arxiv.org/abs/2407.00507
- Peer-review status: published at IEEE T-RO. The arXiv copy states "This paper has been accepted
  for publication at IEEE Transactions on Robotics" and gives that DOI. The issue's seed was the
  arXiv link; the published version exists and is cited.
- Verified: yes — Abstract, §I, §III, §IV, §V, §VI, §VII read; §II (related work) skimmed; the
  proofs of Propositions 1–2 not checked. **Read from** `refs/sr_avocado_2407_00507.txt` (arXiv v4,
  1 Apr 2025).
- Sub-area: S1 (filed here because the issue seeded it under S1; the experiments are on robots and
  it could equally sit in S3).
- **Primary category: A.** *The issue asked for this one to be checked carefully as a possible
  boundary case. It is not one, and the reasons are specific:*
- Category justification:
  - **Not B.** The "opinion" is an internal estimate each robot forms about how cooperative the
    other is. The paper says existing opinion dynamics assume the values "can be communicated.
    This is not the case in this work" (§IV-B), and that the method works "using only relative
    position and velocity measurements from onboard sensors and without the need of any
    communication infrastructure" (§III). Under the issue's boundary rule, observing position and
    velocity is not communication.
  - **Not C.** The rule runs every 0.05 s on *predicted* collision (§III, §IV-A). Even its
    symmetry-breaker acts before contention: noise is injected "when the agent is far from the
    robot, decreasing the noise to zero when the robot and the agent are close to a potential
    collision" (§IV-D).
  - What makes it *look* like a boundary case is that it does the job a negotiation would do —
    settling who gives way — purely by each side watching whether the other deviates. That is
    [inference] the most direct example in this review of the supervisor's point that the rule
    "need not involve communication at runtime".
- Domain simulated: holonomic robots, and robots among human pedestrians. [§III, §VI]
- The rule, stated precisely: for each neighbour *i* within the perception radius, hold a scalar
  degree of cooperation `α_i ∈ [0, 1]` (1 = the other does all the avoiding, 0 = it ignores me).
  Compute the smallest change `u_i` in relative velocity that leaves the velocity obstacle (Eq. 6);
  the robot takes on the `(1 − α_i)` share, which defines a half-plane of admissible velocities
  (Eq. 7); choose the velocity nearest the desired one inside all half-planes by a linear program
  (Eq. 8). `α_i = 0.5` "corresponds to the ORCA algorithm" (§IV-A). `α_i` is updated online by a
  nonlinear opinion-dynamics law (Eq. 10) driven by an *attention* term that rises as predicted
  time-to-collision falls (Eq. 11) and by an estimate, from the other agent's observed velocity
  change, of how much it is cooperating (Eq. 15). Full loop: Algorithm 1.
- Trigger condition: continuously, at 20 Hz; adaptation of `α_i` switches on as predicted
  time-to-collision shrinks. [§III; Eq. 11]
- Information required: positions and velocities of agents within a 2.5 m sensing radius, and the
  robot's own previous observation of each (§V; Algorithm 1 line 4). No goals of others, no
  priorities, no messages.
- Tie-breaking: **explicit, and the most carefully designed in S1.** Symmetric encounters are
  broken by adding uniformly distributed noise `μ ~ U(−ε, ε)`, scaled by `(1 − A_i)`, to the
  *perceived* velocity of the other agent (§IV-D, Eqs. 18–19). The nonlinear law then bifurcates to
  one of two stable equilibria (Proposition 2). A bias term `b_i` can encode a prior about the
  other's cooperativeness; default `b_i = 0` (Table I). The authors note the mechanism "can also be
  applied to other VO-based methods such as ORCA" (§IV-D). ⚠ **The paper describes the noise
  schedule two ways.** Eq. (19) and the sentence introducing it say noise is largest when the
  agent is far and falls to zero near collision; a later sentence in the same subsection says "The
  intensity of the perturbation increases when the distance between robot and agent i decreases".
  I follow Eq. (19) and flag the contradiction.
- Guarantees claimed: the linear program "is guaranteed to have a solution unless the intersection
  of the OCA_i sets is empty", in which case the robot takes the "least unsafe" velocity (§IV-A);
  the adaptive law has two stable equilibria under a stated gain condition (Proposition 2). No
  collision-freedom or deadlock-freedom theorem.
- Evaluation: simulated circle and crossing scenarios, N = 10 to 25 in steps of 3, five proportions
  of cooperative robots, **128 random scenarios per combination**, against ORCA, T-MPC, SARL and
  RL-RVO (§V-B, Figs. 11–14). Real experiments: three Turtlebot 2 robots and up to three
  pedestrians at a time in a 6×6 m arena, **19 pedestrians, 15 of them external to the project, 33
  experiments** (§VI).
- Does it work: better than the comparators in mixed settings, with failures the authors show
  rather than hide.
  - "ORCA experiences deadlocks from geometrical symmetries, so it fails in all cooperative circle
    scenarios" (§V-B) — a third independent report of this failure, after [Sudkhot-BDI-RVO] and
    [SunshineHill-RVO-ORCA].
  - **A wrong prior causes collisions.** "Extreme bias values can lead to collisions" (§V-A, Fig. 6
    cases b and e): a robot that assumes the other is uncooperative collides with a cooperative
    one, and vice versa.
  - No single parameter setting wins everywhere: the variant biased toward expecting cooperation
    is worst in circle scenarios and best in crossing scenarios (§V-B).
  - Having no planning horizon, it "sometimes enter[s] in conflicting situations that lead to local
    minima or unavoidable collisions" (§VII).
  - ⚠ Success rates are in the heat-maps of Figs. 11–12, which did not survive extraction; I give
    no numbers.
- Validated against real human or real traffic data: **no, with a qualification.** It was *tested
  with* real pedestrians (§VI), who were given start and goal points but "no instructions on how to
  behave". That is a hardware trial reported through trajectory plots (Figs. 16–18), not a
  comparison of the rule's behaviour against recorded human behaviour. No statistic from the human
  trials is given.
- Scalability: 25 agents in simulation (§V-B); six agents (three robots, three people) on hardware
  (§VI). Compute time per step is in Fig. 14 (not legible); the text says the geometric methods
  need "hundreds of milliseconds … in crowded environments" and grow linearly with neighbours
  (§V-B). The claim that the underlying linear program handles "thousands of nearby agents in
  milliseconds" is cited to the ORCA paper, not shown here (end of §IV-D).
- Domain assumptions that limit portability: holonomic single-integrator dynamics (§III);
  continuous 2-D; agents assumed "not competitive" (§III); convex obstacles only without a
  higher-level planner (§V-C).
- Portability to a generic simulator: [inference] **high, and it carries the idea most relevant to
  the FYP.** The rule needs only positions and velocities, and it parameterises *who yields, and by
  how much* as one number per neighbour. A persona could supply that number's prior (`b_i`). The
  paper's own Fig. 6 is the warning: a mis-set prior produces collisions, so a persona-derived
  prior would need the online correction, not a fixed table.
- Limitations and future work stated by the authors: integrate with a higher-level planner; general
  dynamics and 3-D; distinguish non-cooperation from an agent that is itself busy avoiding others.
  [§VII]
- Relevance to this FYP: [inference] **extend.** The strongest candidate in S1 for a reusable
  mechanism: a communication-free, continuous rule with an explicit, tunable asymmetry.
- BibTeX: `martinezbaselga2025avocado`

---

### [Tordeux-CFSM]: Collision-Free Speed Model for Pedestrian Dynamics

- Authors / Year / Venue: Antoine Tordeux, Mohcine Chraibi, Armin Seyfried / 2016 / *Traffic and
  Granular Flow '15*, Springer, pp. 225–232.
- Link: https://doi.org/10.1007/978-3-319-33482-0_29 | https://arxiv.org/abs/1512.05597
- Peer-review status: published in the *Traffic and Granular Flow '15* proceedings volume
  (Springer book chapter; Crossref type `book-chapter`).
- ⚠ **Window check.** The published version is dated 2016 (Crossref). The arXiv preprint was posted
  17 December 2015. I treat it as in-window on the publication date (work-log assumption A4).
  **This is a borderline call and is flagged for the supervisor**; if the window is to be judged on
  first public appearance, this entry moves to [pre-window-foundations.md](pre-window-foundations.md).
- Verified: yes (full text read). **Read from** `refs/sr_cfsm_1512_05597.txt` (arXiv v1; the
  published chapter was not opened). Not a seed: it is the "CSM" baseline in [Xu-AVM] (AVM §3),
  located through the arXiv API by title.
- Sub-area: S1
- **Primary category: A.**
- Category justification: the model is "by construction collision-free" (§2.1): speed is a function
  of the gap ahead that is zero at contact (condition 5). No conflict state can be entered.
- Domain simulated: pedestrians. [§1]
- The rule, stated precisely: velocity = speed × direction, set separately (Eq. 4). **Speed:**
  `V(s) = min{v0, max{0, (s − ℓ)/T}}`, where *s* is the distance to the nearest pedestrian in a
  strip ahead of width equal to the pedestrian diameter ℓ (Eqs. 2–3; §2.1). **Direction:** the
  desired direction plus a sum over neighbours of a repulsion `R(s) = a·exp((ℓ − s)/D)` pointing
  away from each neighbour, normalised (Eq. 6). Five parameters; the values used are `v0 = 1.2
  m/s`, `ℓ = 0.3 m`, `T = 1 s`, `a = 5`, `D = 0.1 m` (Fig. 2).
- Trigger condition: continuously (a first-order differential equation; Euler step 0.01 s). [§3]
- Information required: positions of neighbours only. Not even their velocities. [§2.1]
- Tie-breaking: `[not stated in paper]`. With two pedestrians exactly head-on, each has the other
  in its front strip, so both speeds go to zero by Eq. (5); the repulsion in Eq. (6) is exactly
  opposed to the desired direction, with no lateral component. [inference] The model as written
  therefore has no way out of a perfectly symmetric head-on meeting. The paper does not discuss
  this; [Xu-AVM] confirms it in simulation ("In the CSM, the two agents are unable to pass each
  other", AVM §3).
- Guarantees claimed: **collision-freedom, with a short proof** (§2.2): the set of non-overlapping
  configurations is invariant under any dynamics satisfying condition (5), "valid for any direction
  model". No deadlock claim.
- Evaluation: simulation in a 9 m × 3 m corridor from random initial conditions (§3). Counter-flow
  lane formation observed up to 6 ped/m² (§3.1, Fig. 3); oscillating flow at a bottleneck (§3.2,
  Fig. 4). Agent counts are not stated; at 2 ped/m² in 27 m² that is about 54 agents `[my
  arithmetic, not the paper's]`.
- Does it work: qualitatively. **Stated limits:** lanes disappear when noise is added — with noise
  of standard deviation 0.1 m/s "the lane formation breaks as soon as ρ ≈ 2 ped/m²" (§3.1); and
  "stop-and-go phenomena can not be described" (§4).
- Validated against real human or real traffic data: no. The paper says phenomena "observed in
  real data … are reproduced" (§4) but fits nothing and compares no numbers.
- Scalability: `[not stated in paper]`. "Low computational effort" is asserted (Abstract) without a
  measurement.
- Domain assumptions that limit portability: continuous 2-D; disc agents of equal size; first-order
  dynamics (no inertia); a desired direction supplied from outside. [§2]
- Portability to a generic simulator: [inference] the *speed* half is fully portable and is the
  cheapest collision-prevention rule in this review: one distance, one clamp. It guarantees safety
  and nothing else — it converts every unresolved conflict into a standstill. That makes it a
  natural safety floor underneath a separate arbitration rule.
- Limitations and future work stated by the authors: "Further mechanisms (and parameters) remain to
  be introduced". [§4]
- Relevance to this FYP: [inference] **reuse as the safety layer; do not expect it to resolve
  anything.** It is the clearest demonstration in the review that "collision-free by construction"
  and "deadlock-free" are different properties.
- BibTeX: `tordeux2016cfsm`

---

### [Xu-AVM]: Anticipation in a velocity-based model for pedestrian dynamics

- Authors / Year / Venue: Qiancheng Xu, Mohcine Chraibi, Armin Seyfried / 2021 / *Transportation
  Research Part C: Emerging Technologies* 133, 103464.
- Link: https://doi.org/10.1016/j.trc.2021.103464 | https://arxiv.org/abs/2107.00624
- Peer-review status: published at *Transportation Research Part C* (Crossref record
  `refs/sr_cr_10_1016_j_trc_2021_103464.json`). Not a seed and not reached from a seed's reference
  list: I knew of the paper beforehand, located it through the arXiv API by title, and confirmed
  the journal record in Crossref. Logged as such in [search-log.md](search-log.md).
- Verified: yes (full text read, including Appendices A–C). **Read from**
  `refs/sr_avm_2107_00624.txt` — arXiv v1, headed "Preprint submitted to Elsevier, July 2, 2021".
  ⚠ The published version may differ; section and equation numbers are the preprint's.
- Sub-area: S1
- **Primary category: A.**
- Category justification: the agent steers on *predicted* positions a time `t_a` ahead (Eq. 2) and
  its speed is clamped by the free gap (Eq. 10), so overlap is excluded and avoidance begins before
  contact. Only positions and velocities are used.
- Domain simulated: pedestrians in bidirectional corridor flow. [§1, §4]
- The rule, stated precisely: **Direction** (§2.1) — (a) consider agents in the half-plane ahead of
  the current or desired heading (Eq. 1); (b) for each, predict the separation `t_a` seconds ahead
  assuming constant velocities, floored at contact distance (Eq. 2); (c) weight its influence by
  `exp` of minus that predicted separation over a range *D*, times a factor that is `k` for a
  neighbour heading the same way and `2k` for one heading the opposite way (Eqs. 3–4) — which makes
  agents follow others going their way; (d) push **sideways only**, perpendicular to the desired
  direction, away from the neighbour's predicted position (Eq. 5); (e) sum, normalise, and relax
  toward the result with time constant τ (Eqs. 6–7). **Speed** (§2.2) — the minimum of free speed
  and (gap to the nearest agent in the direction of motion) / *T* (Eqs. 8–10). Validated parameter
  set: `r = 0.18 m`, `k = 6`, `D = 0.01 m`, `T = 0.6 s`, `τ = 0.3 s`, `t_a = 0.75 s` (bidirectional),
  free speed `N(1.55, 0.18²) m/s` (Table 3).
- Trigger condition: continuously, on predicted proximity. [§2.1]
- Information required: neighbours' positions and velocities; own desired direction. [§2.1]
- Tie-breaking: **stated, and it is random.** "when this predicted position is aligned with the
  desired direction of i, the direction of n_{i,j} in Eq. 5 is chosen randomly" between the two
  sideways directions (§2.1, after Eq. 5). The two-agent crossing test additionally sets the two
  free speeds "very similar but not quite equal to avoid the symmetric movement" (§3, Fig. 5) —
  i.e. the authors side-step symmetry by construction in that test.
- Guarantees claimed: none stated formally; the speed sub-model is the collision-free one of
  [Tordeux-CFSM] ("the same as in the generalized collision-free velocity model", §2.2).
- Evaluation: (i) three two-agent scenarios — overtaking, head-on, crossing (§3, Figs. 3–5); (ii)
  bidirectional corridor with periodic boundaries, 20–200 and 20–300 agents, 30 runs per setting,
  400 s each, measuring jamming probability and a lane-order parameter (§4, Figs. 8–11); (iii)
  fundamental diagrams against laboratory experiments (§5, Figs. 13–16).
- Does it work: yes relative to its two predecessors, with honestly reported gaps.
  - Head-on, two agents: the predecessor "CSM" agents "are unable to pass each other"; with this
    model both sidestep (§3).
  - The density at which jamming sets in is higher than for either predecessor (§4.2, Fig. 8) —
    but it still jams. At the default parameters the transition from "never jams" to "always jams"
    is at about 140 agents ≈ 1.35 m⁻² (§4.3, Appendix A).
  - **More anticipation is not better.** Jamming probability falls and then rises with prediction
    time (Appendix A, Fig. A.17). And — unlike the predecessors — stronger neighbour influence
    *increases* jamming (§4.3).
  - A 1 m wide corridor jams almost always, at any density tested (Appendix B).
  - More varied free speeds mean less jamming (Appendix C).
- Validated against real human or real traffic data: **yes** — the only entry in S1 that is.
  Calibrated against the fundamental diagram of laboratory bidirectional-flow experiments (cited as
  refs. [22, 28], Zhang et al.), with the unidirectional diagram then reproduced without re-fitting
  (§5, Figs. 13, 16), and the time-course of lane formation compared with an experiment in a 3.6 m
  corridor (§4.4, Fig. 11b). **Authors' own caveats:** calibration "was performed manually" (§5);
  "the comparability of experiments and simulations is limited" because lanes may have begun
  forming outside the measured area (§4.4); and simulated agents are more erratic than people at
  high density because they "always jostle to move further and are apparently unaware of the
  strategy of simply standing still" (§5). No experimental data exists above 4.5 m⁻² (§1, §5).
- Scalability: 300 agents (§4.4). No runtime reported: `[not stated in paper]`.
- Domain assumptions that limit portability: continuous 2-D; disc agents; a corridor geometry in
  every multi-agent test; a desired direction supplied externally. [§2, §4]
- Portability to a generic simulator: [inference] moderate. The structure — predict, weight
  oncoming more than same-direction, dodge sideways, break exact ties at random — is general. The
  parameter values are calibrated on German laboratory participants in a corridor and would need
  re-calibrating for any other population or agent type. That is directly relevant to a
  Singapore-specific dataset.
- Limitations and future work stated by the authors: no separate section; the caveats above are in
  §4.4 and §5.
- Relevance to this FYP: [inference] **the benchmark for "validated".** It shows what validation
  against human data looks like in this field (fundamental diagram plus a lane-order time series),
  and that even a validated model's symmetric-conflict tie-break is a coin flip. It also names a
  human strategy its agents lack — standing still and letting the other pass — which is a yielding
  rule, i.e. what the FYP is trying to extract.
- BibTeX: `xu2021avm`

---

## Seed excluded from this issue

**"CrowdVLA: Embodied Vision-Language-Action Agents for Context-Aware Crowd Simulation"**
(Hwang, Hong, Kim, Seon, Nam, Jang, Kang; arXiv:2604.05525v1, 7 April 2026; `[preprint]`).
Opened and scope-checked (Abstract, §1, contribution list, keyword scan of the body;
`refs/sr_crowdvla_2604_05525.txt`). **Excluded: it is not about conflict rules.** It models each
pedestrian as a fine-tuned vision–language–action policy that selects among learned motion skills
(Abstract; §1 contributions), and positions itself explicitly *against* rule-based control:
it aims "to generate natural, realistic motions without hand-crafted rule-based controllers" (§2,
related work) and describes its goal as "risk-aware decision making rather than rigid rule
adherence" (evaluation section). There is no stated rule to catalogue. It belongs
with the LLM-agent literature and is noted for a later issue; nothing from it is used here.

---

## Not obtained

### [NOT OBTAINED] A survey on Velocity Obstacle paradigm
- Authors / Year / Venue: Federico Vesentini, Riccardo Muradore, Paolo Fiorini / 2024 / *Robotics
  and Autonomous Systems* 174, 104645
- Link tried: https://doi.org/10.1016/j.robot.2024.104645 ;
  https://www.sciencedirect.com/science/article/abs/pii/S0921889024000289
- Reason unavailable: paywall
- Date attempted: 2026-10-04
- Status: awaiting PDF from user

### [NOT OBTAINED] Algorithms for Microscopic Crowd Simulation: Advancements in the 2010s
- Authors / Year / Venue: W. van Toll, J. Pettré / 2021 / *Computer Graphics Forum* 40(2), 731–754
- Link tried: https://doi.org/10.1111/cgf.142664 ; https://inria.hal.science/hal-03197198/document
- Reason unavailable: other — the open-access copy on HAL is behind an automated-browser check
  ("Making sure you're not a bot!") that the download tool could not pass; the publisher copy is
  paywalled
- Date attempted: 2026-10-04
- Status: awaiting PDF from user

### [NOT OBTAINED] Implicit Crowds
- Authors / Year / Venue: Ioannis Karamouzas, Nick Sohre, Rahul Narain, Stephen J. Guy / 2017 /
  *ACM Transactions on Graphics* 36(4)
- Link tried: https://doi.org/10.1145/3072959.3073705 ; https://dl.acm.org/doi/pdf/10.1145/3072959.3073705
- Reason unavailable: login required (the ACM download returned an access page, not the PDF)
- Date attempted: 2026-10-04
- Status: awaiting PDF from user
