# S3 — Multi-agent path finding and multi-robot navigation

> **Draft pending supervisor review.** Prepared for issue
> [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). Read date for every entry:
> 2026-10-04.

Companion files: [S1](s1-crowd-simulation.md) · [S2](s2-games.md) · [S4](s4-traffic-vehicles.md) ·
[rule catalogue](rule-catalogue-simulation.md) · [category summary](category-summary.md) ·
[research gap](research-gap.md) · [pre-window foundations](pre-window-foundations.md) ·
[missing papers](missing-papers.md) · [search log](search-log.md) · [refs](refs-simulation-rules.bib)

## How to read this file

- **Categories** are the issue's: **A** avoid conflict by following a rule (the conflict state is
  never instantiated); **B** resolve conflict through communication (a channel carrying information
  not inferable from physical state); **C** resolve conflict by following a rule (contention
  exists, a rule arbitrates, no negotiation).
- **Locators** point into the cached text named on each entry's "Read from" line. Section, table,
  figure, algorithm and theorem numbers are the paper's own.
- **Read depth is stated per entry.** "Full text read" means every section of the body. Where I
  read a long paper selectively, the entry lists the sections read and makes no claim about the
  rest.
- `[inference]` marks my judgement, not the paper's claim.
- A classification call that applies to this whole sub-area: in MAPF, agents never physically
  collide, because the planner forbids it. I therefore treat **"two agents request the same vertex
  in the planner"** as the conflict state. That is the issue's own wording ("two or more agents
  contest the same cell"). Under that reading, priority-based planners are **C**, not A. This is a
  judgement call; it is discussed in [category-summary.md](category-summary.md) §4.

Contents: [Okumura-PIBT] · [Chakravarty-PIBT-FreeSpace] · [Zhou-LSRP] · [Yang-S2AN] ·
[Zhang-Mutex] · [Ma-TokenPassing] · [Ma-DCC] · [Grover-Deadlock] · [Dergachev-ORCA-MAPF] ·
[Wang-MAPFSurvey] · not-obtained stubs

---

### [Okumura-PIBT]: Priority Inheritance with Backtracking for Iterative Multi-agent Path Finding

- Authors / Year / Venue: Keisuke Okumura, Manao Machida, Xavier Défago, Yasumasa Tamura / 2022 /
  *Artificial Intelligence* 310, article 103752. Conference version: IJCAI 2019 (the issue's seed).
- Link: https://doi.org/10.1016/j.artint.2022.103752 | https://arxiv.org/abs/1901.11282 |
  conference: https://www.ijcai.org/proceedings/2019/0076.pdf
- Peer-review status: published at *Artificial Intelligence* (journal); earlier version published
  at IJCAI 2019.
- Verified: yes (full text read, §1–§6; appendix not read). **Read from**
  `refs/sr_pibt_aij_1901_11282v5.txt` — arXiv v5 dated 27 Jun 2022, which the arXiv record links to
  the journal DOI. The publisher's typeset copy was not opened, so **page numbers are not given**;
  section and algorithm numbers are from the arXiv v5 text. The IJCAI version
  (`refs/sr_pibt_ijcai2019.txt`) was opened only to confirm it is the same algorithm; the journal
  version is preferred, as the issue asked, and "Difference from Conference Versions" in §1 says
  the journal adds experiments, theory on rotations, and a stress test.
- Sub-area: S3
- **Primary category: C** (secondary: B, in the decentralised variant only — §4.5).
- Category justification: the rule fires when two agents want the same next vertex: the higher
  priority agent takes it and "pushes" the occupant (§4.1.1; Algorithm 1 lines 12–16). Contention
  is instantiated and then arbitrated by priority, with no bargaining. In the centralised form
  nothing is exchanged. §4.5 describes a decentralised form in which agents "talk directly" to
  propagate priority inheritance and backtracking, which would be B; the paper only discusses it,
  and every experiment is centralised (§4, opening paragraph; §5.4).
- Domain simulated: abstract agents on a graph; one physical demonstration with toio robots.
  [§3.1, §5.4]
- The rule, stated precisely: at every timestep, (1) each agent's priority `p_i` is incremented by
  1 if it is not at its goal, otherwise reset to its tie-breaker `ε_i` (Alg. 1 line 3); (2) agents
  are processed in decreasing priority (lines 4–7); (3) each agent sorts its current vertex and
  neighbours by distance to its goal (lines 9–10) and tries them in order, skipping any vertex
  already reserved for the next timestep (line 12) and the vertex of the agent it inherited from
  (line 13, which prevents swaps); (4) if the chosen vertex is occupied by an agent that has not
  yet planned, that agent *inherits* the priority and is planned next, recursively (lines 15–16);
  (5) if the recursion returns `invalid`, the agent tries its next candidate; if none works it
  stays put and returns `invalid` to whoever pushed it (lines 20–21) — this is the backtracking.
  [Algorithm 1; §4.1.1–§4.2]
- Trigger condition: once contention has occurred — i.e. when the vertex an agent wants is wanted
  or held by another agent in the same one-timestep plan. Evaluated every timestep. [§4.1; Alg. 1
  lines 12–16]
- Information required: the shared graph; each agent's current vertex and goal; a distance-to-goal
  evaluation for neighbouring vertices; **all agents' priorities**; a global synchronous clock.
  [§3.1, §4.2; §4.4.1 "Distance evaluation"; §4.5 "PIBT requires agents to know others' priorities"]
- Tie-breaking: **two explicit mechanisms.** (a) Between agents: each agent has a tie-breaker
  `ε_i ∈ [0, 1)`, "distinct for agents", so that priorities are always unique; the effective order
  is *longest time since last at goal first*, then `ε_i` (§4.2, Alg. 1 lines 2–3). The paper does
  not say how `ε_i` is chosen in the base algorithm; in PIBT+ it is set so that agents farther from
  their goal start with higher priority (Algorithm 2 line 2). (b) Between candidate vertices at
  equal distance: "the presence (or absence) of an agent is used as a tie-breaking rule", to avoid
  unnecessary priority inheritance (§4.2).
- Guarantees claimed: **reachability, not completeness.** If every pair of adjacent vertices lies
  on a simple cycle (e.g. a biconnected graph), every agent reaches its goal within
  `diam(G)·|A|` timesteps (Theorem 1). Agents are *not* guaranteed to be at their goals
  simultaneously, so PIBT is "incomplete for conventional MAPF" (§1, §4.3.1). Collision-free and
  swap-free by construction (§4.1.2). Complete for pickup-and-delivery under the same graph
  condition (Theorem 3). A rotation-free variant holds on biconnected graphs with `|A| < |V|`
  (Theorem 4). Per-timestep cost `O(|A|·(Δ(G) + F + lg|A|))` (Proposition 1). No optimality claim
  ("neither complete nor optimal", §2.1).
- Evaluation: (i) one-shot MAPF on ten grids from the MAPF benchmark, 25 scenarios each, agents
  increased in steps of ten "up to the maximum (1000 agents in most cases)", 30 s time limit,
  against HCA*, EECBS, Push and Swap, CBS and BCP; metrics are success rate, runtime, sum-of-costs
  and makespan relative to lower bounds (§5.1.1, Fig. 6). (ii) Pickup-and-delivery on a 21×35
  grid, 500 tasks, 10–50 agents, 100 instances per setting, against Token Passing (§5.2.1, Fig. 8).
  (iii) Stress test, 2,000–10,000 agents on the benchmark's largest map (§5.3). (iv) A demo on a
  7×5 virtual grid with physical robots (§5.4).
- Does it work: on the paper's evidence, yes for speed and scale, with a named failure mode.
  Solutions for a thousand agents arrive in "≤ 5 seconds in large maps" (§5.1.2). **Reported
  failures:** on `random-32-32-20` PIBT failed 674 instances, all by hitting the makespan limit
  (Table 1). The paper gives two causes: reachability does not put all agents on their goals at
  once, and graphs lacking the cycle condition let agents "stop moving" as in Fig. 5 (§5.1.2,
  "Failure reasons of PIBT"). A livelock was observed with naive PIBT on one-shot MAPF (§4.4.1).
  "Almost all selected grids did not satisfy the graph condition of reachability" (§5.1.1), so the
  headline guarantee did not apply to most of the benchmark.
- Validated against real human or real traffic data: no. The only real-world element is a robot
  demonstration (§5.4); no human data is used anywhere.
- Scalability: 10,000 agents on `orz900d` (1491×656, 96,603 vertices), "around ten milliseconds
  per one timestep on an ordinary laptop", runtime roughly linear in agents; this measures runtime
  only, "regardless of whether the planning succeeded" (§5.3.1–§5.3.2, Fig. 9).
- Domain assumptions that limit portability: discrete graph; synchronous unit-time moves (the
  authors name asynchrony as the gap to practice, §6); known goals; homogeneous agents; centralised
  in every experiment; the guarantee needs a cycle-rich graph. [§3.1, §4.3.1, §6]
- Portability to a generic simulator: [inference] **high for the idea, conditional for the
  guarantee.** The rule needs only "who wants what next" and a total order on agents, both of
  which any lock-step simulator has, and nothing in it is specific to robots. What would have to
  change: continuous-space simulators need a discretisation of "the next cell" (see
  [Chakravarty-PIBT-FreeSpace]); non-lock-step simulators need [Zhou-LSRP]; and in a corridor or
  doorway — the FYP's own scenarios — the cycle condition fails, which is exactly where the paper
  reports agents getting stuck (Fig. 5).
- Limitations and future work stated by the authors: asynchrony between agents' moves is "a
  significant gap in practical situations" (§6).
- Relevance to this FYP: [inference] **reuse as the baseline arbitration rule, and extend the
  priority.** PIBT's priority is *time since last at goal* plus an arbitrary tie-breaker. That
  tie-breaker is the slot an LLM-elicited, persona-dependent ordering would fill. It also bears on
  the 10,000-agent goal: this is the only paper in the review that reports a timing at that scale.
- BibTeX: `okumura2022pibt` (and `okumura2019pibt` for the conference version)

---

### [Chakravarty-PIBT-FreeSpace]: A Scalable Post-Processing Pipeline for Large-Scale Free-Space Multi-Agent Path Planning with PIBT

- Authors / Year / Venue: Arjo Chakravarty, Michael X. Grey, M. A. Viraj J. Muthugala, Rajesh
  Mohan Elara / 2026 / *Mathematics* 14(7), 1195 (MDPI).
- Link: https://doi.org/10.3390/math14071195 (arXiv preprint: https://arxiv.org/abs/2506.16748)
- Peer-review status: published at *Mathematics* (MDPI journal; received 2 March 2026, accepted
  21 March 2026 — first page).
- Verified: yes (full text read). **Read from** `refs/sr_pibt_freespace_math.txt` (the published
  version). ⚠ The text extraction of **Tables 1–3 lost the alignment between map names and rows**;
  I quote only the cells whose meaning is unambiguous and say so where it matters.
- Sub-area: S3
- **Primary category: C** (secondary: A, for the smoothing stage).
- Category justification: the conflict rule is PIBT, unchanged in kind (§3.1), hence C. The new
  contribution is a smoother that deliberately *avoids creating* new contention by refusing to
  smooth through "critical interaction" regions (§3.2), which is avoidance by construction (A);
  when it fails, a prioritised SIPP repair arbitrates (§3.2), which is C again.
- Domain simulated: robots in free space, approximated by an 8-connected grid. [§1, §2.3]
- The rule, stated precisely: (1) run PIBT on an 8-connected grid, extending the neighbour set and
  the swap check to diagonals (§3.1, Fig. 1); (2) mark every state within one hop of another agent
  as a *critical interaction* (§3.2); (3) string-pull each agent's path between consecutive
  critical interactions, treating other agents' critical regions as time-bound obstacles in the
  line-of-sight test, and keeping the arrival time at each critical interaction fixed (Algorithm 1
  lines 9, 22–36); (4) for any pair of smoothed trajectories that still intersect, resolve with
  prioritised SIPP (Algorithm 1 lines 37–43).
- Trigger condition: PIBT stage — on contention, as in [Okumura-PIBT]. Smoothing stage — runs only
  where agents are *not* interacting. Repair stage — after a new intersection has been created.
  [§3.2]
- Information required: full PIBT trajectories of all agents (the smoother is a centralised
  post-process), the obstacle list, and a shared time base. [Algorithm 1 inputs]
- Tie-breaking: `[not stated in paper]` for the PIBT stage beyond citing PIBT. For the SIPP repair
  the paper says only "a priority-based scheme" without saying how priority is assigned (§3.2).
- Guarantees claimed: **none.** "Our work also makes no claims about the optimality or completeness
  of our method" (§6). The smoother alone is "not … a guaranteed collision-free path" (§3.2).
- Evaluation: MAPF benchmark maps, against AA-CCBS+SIPP; metrics are solve time, arc length,
  intersections introduced, path-length reduction (§4.1–§4.2). Paths are "on average, 0.8% longer"
  than the optimal baseline, computed only over the 1,906 of 4,948 scenarios the baseline solved
  (§4.2). Ablation (Table 4, `Berlin_1_256`): intersections introduced at 50 / 100 / 200 agents are
  0 / 2 / 11 for the proposed method, 3 / 6 / 12 with 4-connected PIBT, and 13 / 63 / 170 when
  critical regions are ignored. Average path-length reduction 7.3%, overhead 19% at 100 robots (§5).
- Does it work: partly, and the authors say where not. Smoothing gains fall as density rises
  (Table 5: 27.8% at 4 agents to 12.9% at 20) and are "as low as 0%" in corridor-like warehouse
  maps (§5). "Perhaps the most significant drawback" is the need for a fallback repair (§5).
  ⚠ **The abstract says the method scales "to over 500 agents"; the largest agent count I can find
  in any table is 200 (Table 4) and solve-time rows stop at 100 (Tables 1 and 3).** Fig. 5 is
  captioned "100 s of robots" and was not legible in the text extract. I therefore record 200 as
  the largest *tabulated* count and treat 500 as an abstract-level claim.
- Validated against real human or real traffic data: no. [§4]
- Scalability: largest tabulated count 200 agents (Table 4); a 100-agent row of 27.8 s appears in
  Table 3 with path smoothing (map attribution uncertain because of the extraction problem noted
  above). Implementation is in Python (§4.2).
- Domain assumptions that limit portability: homogeneous robots; no kinodynamics; grid
  discretisation; centralised; synchronous. [§6]
- Portability to a generic simulator: [inference] useful mainly as evidence that a grid rule can
  be lifted to continuous space **only where agents are not interacting**. Its central insight —
  "PIBT negotiations are local", so hand control to the rule only inside a two-hop interaction
  zone (§3.2) — is the reusable part: it gives a clean split between a cheap free-flow mover and a
  conflict rule.
- Limitations and future work stated by the authors: no kinodynamics; heterogeneity "is not
  supported in PIBT"; makespan cannot be reduced; the SIPP "escape hatch … is less than ideal",
  with ORCA, control barrier functions or PIBT itself suggested as replacements. [§6]
- Relevance to this FYP: [inference] baseline / architectural precedent. The explicit statement
  that PIBT does not support heterogeneous agents (§6) matters, because the FYP's personas are a
  form of heterogeneity.
- BibTeX: `chakravarty2026pibtfreespace`

---

### [Zhou-LSRP]: Loosely Synchronized Rule-Based Planning for Multi-Agent Path Finding with Asynchronous Actions

- Authors / Year / Venue: Shuai Zhou, Shizhe Zhao, Zhongqiang Ren / 2025 / *Proceedings of the AAAI
  Conference on Artificial Intelligence* 39(14), 14763–14770.
- Link: https://doi.org/10.1609/aaai.v39i14.33618 | https://arxiv.org/abs/2412.11678
- Peer-review status: published at AAAI 2025.
- Verified: yes (full text of the main paper read; the appendix in the arXiv "extended version" was
  not read). **Read from** `refs/sr_lsrp_2412_11678.txt` (arXiv v2, which carries the AAAI
  copyright line). The two-column layout interleaved Algorithm 2 with the prose in extraction, so
  line numbers of Algorithm 2 are cited only where the prose names them.
- Sub-area: S3
- **Primary category: C.**
- Category justification: same arbitration as PIBT — "When two agents seek to occupy the same
  position, the higher-priority agent is able to take this location, and pushes the lower-priority
  agent" (§3.1) — generalised to actions of different durations. No message exchange.
- Domain simulated: abstract agents on a graph with per-agent, per-edge traversal durations. [§2]
- The rule, stated precisely: maintain a list of timestamps. At the smallest timestamp `t_min`,
  take the agents whose current action ends at `t_min` (Algorithm 1 lines 11–12). In descending
  priority, call `ASY-PUSH` on each (lines 18–20). `ASY-PUSH` sorts the agent's neighbouring
  vertices by distance to goal and takes the first that is not occupied; if the vertex is held by
  an agent that is also due to plan and has not yet planned, it recursively pushes that agent,
  waits until the pushed agent's move finishes, and **caches** its own wait-then-move action for
  future execution (§4.3, Cases 1–3; Algorithm 3). A `ban` list prevents cyclic pushes (§4.3,
  Case 2). The `LSRP-SWAP` variant adds a swap operation for agents that need to exchange places
  (§6).
- Trigger condition: once contention has occurred, at the planning timestamp of the agents
  involved. Not every agent plans at every timestamp. [§4.2, §4.4]
- Information required: the graph; every agent's goal, current individual state
  `(p, v, t_p, t_v)`, and priority; known action durations `D(i, v1, v2)`; and "All agents share a
  global clock" (§2). [§2, §4.1]
- Tie-breaking: priorities are initialised by `INITPRIORITY()`, "which can be set in different
  ways (such as using random numbers)" (§4.2). The toy example uses `{0.99, 0.66, 0.33}` (§4.3).
  The analysis requires that "LSRP initializes all agents with a unique priority" (§5). Priority
  then grows by one per iteration until the agent reaches its goal, when it is reset (Algorithm 1
  lines 9–10). Vertex ties: sorted by distance to goal; no secondary rule is stated.
- Guarantees claimed: **weak termination only**, i.e. every agent reaches its goal at least once,
  and only on a "c-graph" (a cycle of length `N + 1` through every pair of adjacent vertices):
  within `diam(G)·N²·D_max` (Theorems 1–2, given with proof *sketches*). The swap variant voids
  both theorems (§6). The paper says it is "trading off completeness and solution optimality for
  scalability" (§1).
- Evaluation: three benchmark maps (Empty-16, Den520d, Warehouse), 25 instances per agent count,
  30 s limit, durations 1.0–5.0, against a modified CCBS and prioritised SIPP (§7). Median ratio to
  baselines about 4× in sum-of-costs and 1.25× in makespan (§7.2, Figs. 5–6). Accounting for
  asynchrony gives solutions "usually 30% and sometimes up to 75% cheaper" than ignoring it (§7.3,
  Fig. 7).
- Does it work: yes for scale, at a stated cost in quality. **Reported failure:** plain LSRP can
  loop forever on a solvable instance — two agents "iteratively push each other and can never
  successfully swap" (§6, Fig. 3). In the cluttered Warehouse map plain LSRP is only on par with
  SIPP; the swap variant is needed (§7.1).
- Validated against real human or real traffic data: no. [§7]
- Scalability: "LSRP-SWAP runs fastest and handles up to 1000 agents in our tests" within the 30 s
  limit (§7.1). Per-step runtime is not tabulated in the text I read.
- Domain assumptions that limit portability: graph; known deterministic durations; shared global
  clock; centralised planner; guarantee only on c-graphs. [§2, §5]
- Portability to a generic simulator: [inference] this is the paper that removes PIBT's lock-step
  assumption, so it matters if the target simulator lets agents act on different clocks or at
  different speeds — which a persona-based pedestrian model does. The price is a cache of
  committed future actions per agent.
- Limitations and future work stated by the authors: develop an anytime version to improve
  solution quality within the runtime limit. [§8]
- Relevance to this FYP: [inference] extend-if-needed. Relevant only if agents have different
  speeds or the simulator is not lock-step.
- BibTeX: `zhou2025lsrp`

---

### [Yang-S2AN]: Attention-based Priority Learning for Limited Time Multi-Agent Path Finding

- Authors / Year / Venue: Yibin Yang, Mingfeng Fan, Chengyang He, Jianqiang Wang, Heye Huang,
  Guillaume Sartoretti / 2024 / *Proc. 23rd International Conference on Autonomous Agents and
  Multiagent Systems (AAMAS 2024)*, 9 pages. Page range `[not identified]` — not printed on the
  copy read.
- Link: https://marmotlab.org/publications/54-AAMAS2024-LearnedPP.pdf
- Peer-review status: published at AAMAS 2024.
- Verified: yes (full text of the main paper read; the appendix containing the repair algorithm
  was not available in the copy read). **Read from** `refs/sr_learnedpp_aamas2024.txt`. Equations
  did not survive extraction; nothing below depends on them.
- Sub-area: S3
- **Primary category: C** (secondary: A). **Hard to classify — see
  [category-summary.md](category-summary.md) §4.**
- Category justification: the paper's object is a *priority order* — who plans first and who must
  plan around whom — which is an arbitration rule (C). But in pure prioritised planning the
  lower-priority agent plans around existing paths, so no conflicting pair of plans is ever
  created, which reads as A. What decides it for me is that this method uses a low-level planner
  with **soft** constraints: collisions do occur in the output, are counted in the reward, and are
  then repaired (§4.1 "Reward"; §4.5). Contention is instantiated, so C. The contrast-case value
  is that the ordering is **learned**, not hand-written.
- Domain simulated: abstract agents on a 2-D grid. [§3.1]
- The rule, stated precisely: a transformer-style network (S2AN) picks, one at a time, which agent
  plans next (§4.1 "Action"; §4.3). Each chosen agent is planned by SIPPS treating earlier agents'
  paths as soft moving obstacles (§4.1 "State transition"). Two hand-designed features feed the
  network: a *harmful* flag (does the agent's goal disconnect its neighbourhood? Fig. 4) and a
  *target matrix* (which agents' goals each agent's path passes through, §4.2). If the result still
  has collisions, colliding agents are re-planned with their goals moved back to their starts
  (§4.5). The learned ordering itself cannot be written down as a rule — it is a network.
- Trigger condition: offline, once, before execution: the order is fixed for the whole instance.
  [§4.1]
- Information required: the full map and all starts and goals, centrally (§4.1 "State"). This is a
  global-information method.
- Tie-breaking: by the network's output probabilities; greedy at inference, sampled in training
  (§4.4). No hand-written tie-break. The intuition the authors give for the target matrix is the
  nearest thing to a stated rule: "when an agent no longer obstructs others, it can be selected as
  the highest-priority agent among the remaining ones" (§4.2).
- Guarantees claimed: none of completeness or optimality. "Prioritized planning algorithms are
  neither complete nor optimal" (§2.2). Linear time complexity is claimed (Abstract; §4.5).
- Evaluation: 100 random 32×32 maps with 20% obstacles plus 100 empty maps; success rate, reach
  rate, makespan, episode length, runtime; against PIBT and time-limited PBS (§5.2, Fig. 6), and
  against the learned planners PRIMAL and DHC (§5.3, Fig. 7). Ablation in Table 1: removing the
  target matrix cuts test reward from 17.77 to 7.13 (−59%).
- Does it work — and **what the learned method gains over the hand-written rule, and at what
  cost** (the question the issue asked of this paper):
  - *Gain:* higher success rate than PIBT "in scenarios characterized by dense obstacles", and than
    PBS at 140–250 agents where PBS "often fails to find any solutions within the allocated time"
    (§5.2).
  - *Cost 1 — speed:* the authors concede that PIBT "can be executed in less than 1 second" (§5.2);
    their own method is "typically within seconds for teams of up to 180 agents" (§1, contribution
    2). ⚠ The success and runtime values are in Fig. 6, which did not survive text extraction, so I
    give no numbers for the size of the gain.
  - *Cost 2 — scale:* the largest team is 250 agents (Figs. 6–7 axes; §5.2), against thousands for
    the hand-written rule in [Okumura-PIBT].
  - *Cost 3 — the rule is opaque and needs training* (one GPU of a 4×3090 server, §5.1), and two of
    its key inputs are hand-engineered features anyway (§4.2).
  - *Cost 4 — global information:* PIBT needs local contention only; this needs the whole instance.
    The authors say as much: "By providing a global map and sacrificing a reasonable amount of
    time, we can achieve enhanced performance" (§5.3).
  - *Reported degradation:* reach rate drops below PRIMAL's once the agent count exceeds 180
    (§5.3).
- Validated against real human or real traffic data: no. [§5]
- Scalability: up to 250 agents on a 32×32 map (§5.2, Figs. 6–7). Runtime per instance: in Fig. 6,
  not recoverable from the text extract.
- Domain assumptions that limit portability: grid; one-shot; centralised; full observability;
  trained on one map family. [§3.1, §5]
- Portability to a generic simulator: [inference] low. The output is an ordering for a specific
  instance produced by a network trained on grid maps. Nothing transfers to another agent type
  without retraining.
- Limitations and future work stated by the authors: no limitations or future-work section. The
  conclusion (§6) restates results only. The one self-criticism is in §5.3: the reach rate falls
  below PRIMAL's above 180 agents, which "suggests that the repair method employed may not be
  robust enough". `[otherwise not stated in paper]`
- Relevance to this FYP: [inference] **contrast case, and a warning.** It shows that replacing a
  hand-written priority with a learned one buys success rate in hard instances but loses the
  properties the FYP wants from an *extracted rule*: interpretability, locality and scale. That is
  an argument for the FYP's stated direction (extract a rule, then apply it) over *let the model
  decide each time*.
- BibTeX: `yang2024s2an`

---

### [Zhang-Mutex]: Multi-Agent Path Finding with Mutex Propagation

- Authors / Year / Venue: Han Zhang, Jiaoyang Li, Pavel Surynek, Sven Koenig, T. K. Satish Kumar /
  2020 / *Proc. 30th International Conference on Automated Planning and Scheduling (ICAPS 2020)*.
  Page range `[not identified]`.
- Link: https://ojs.aaai.org/index.php/ICAPS/article/view/6677
- Peer-review status: published at ICAPS 2020. ⚠ **This is not the version the issue named.** The
  issue's seed is the journal article of the same title (*Artificial Intelligence* 311, 103766,
  October 2022, authors Zhang, Li, Surynek, Kumar, Koenig — confirmed in Crossref,
  `refs/sr_cr_mutex.json`). **Year check requested by the issue: both versions are inside the
  2016+ window.** The journal version is behind the publisher's paywall and was not obtained (stub
  below and in [missing-papers.md](missing-papers.md)); the open ICAPS version was read instead.
  Any extension the journal version adds is not represented here.
- Verified: yes (ICAPS version; §1–§2, §6–§9 read in full; §3–§5, the formal development, read
  selectively — definitions, algorithm headers and theorem statements). **Read from**
  `refs/sr_mutex_icaps2020.txt`.
- Sub-area: S3
- **Primary category: C.**
- Category justification: the method sits inside Conflict-Based Search, which "starts with an
  individual minimum-cost path for each agent" and "lazily resolves conflicts between pairs of
  agents by adding spatio-temporal constraints" (§1). Conflicts between planned paths are
  instantiated first and resolved afterwards by a rule for generating constraints. A single
  centralised planner does this; nothing is negotiated.
- Domain simulated: abstract agents on four-neighbour grids. [§2.1, §7]
- The rule, stated precisely: build each agent's multi-valued decision diagram (MDD) of
  cost-bounded paths. Two MDD nodes at the same level are *mutex* if no pair of conflict-free
  sub-paths reaches them; initial mutexes are the vertex and edge conflicts, and further mutexes
  are propagated level by level (§3; Algorithm 1). Two agents have a *cardinal* conflict iff the
  goal-level nodes are mutex (Theorem 1; Corollary 1). Cardinal conflicts are then resolved by
  constraint sets derived from the mutexes instead of a single-vertex constraint (§5; Algorithms
  3–5). The resulting solver, CBSH-MP, keeps rectangle reasoning for the other conflict types (§6).
- Trigger condition: once a conflict between two agents' current planned paths is found at a
  constraint-tree node. [§1, §2.2]
- Information required: complete — the full graph and every agent's start, goal and current
  planned path, held by one planner. [§2.1–§2.2]
- Tie-breaking: this is an optimal search, so *which agent yields* is not decided by a tie-break:
  both alternatives are branched on (§2.2, "splits the CT node into two child CT nodes"). The only
  stated tie-break is internal: mutexes are popped "with the smallest level, breaking ties in
  favor of node mutexes" (Algorithm 1 line 4). Which agent ends up waiting is whatever the
  optimal solution dictates. So for the FYP's purpose: `[not stated in paper]` as a behavioural
  tie-break.
- Guarantees claimed: CBSH-MP "is complete and optimal" for sum-of-costs MAPF (§6, citing §5.1).
- Evaluation: (i) four hand-built cardinal-conflict instances (Fig. 1), measured in constraint-tree
  node expansions (Table 1); CBSH-MP "solves all instances within one second" and expands one node
  for rectangle, corridor and goal-vertex conflicts, three for switching agents (§7.1). (ii) Four
  benchmark maps — empty-16-16, random-32-32-20, maze-128-128-1, lak303d — 25 scenarios per agent
  count, five-minute limit, against CBSH-RM and CBSH (§7.2, Figs. 3–4).
- Does it work: yes on corridor-like maps, marginally on open ones. On the empty map CBSH-MP "only
  has a small advantage"; in the three narrower maps it wins on runtime and success rate (§7.2).
  It is *slower* than rectangle reasoning on rectangle conflicts, because mutex propagation has a
  larger overhead (§7.1). ⚠ Agent counts and success rates are on the axes of Figs. 3–4, which did
  not survive extraction; I give none.
- Validated against real human or real traffic data: no. [§7]
- Scalability: `[not stated in paper]` as a number in the text I could read (in Figs. 3–4 only).
  The method is an optimal solver for an NP-hard problem (§1), so it is not a large-scale method.
- Domain assumptions that limit portability: grid; lock-step; centralised; full information; known
  goals; agents wait at their goal forever. [§2.1]
- Portability to a generic simulator: [inference] **low as a runtime rule, useful as a
  vocabulary.** It cannot run per-agent in a simulator. But its typology of conflicts — rectangle,
  corridor, goal-vertex, switching-agents (Fig. 1) — is a ready-made list of conflict *shapes*
  against which a simpler rule can be tested. The corridor conflict (Fig. 1b: "one of the two
  agents needs to wait until the other agent exits the corridor") is the FYP's narrow-hallway case.
- Limitations and future work stated by the authors: use mutexes for semi- and non-cardinal
  conflicts; apply to MAPF variants with implicit conflicts; lazily built Boolean models. [§9]
- Relevance to this FYP: [inference] baseline of last resort (the optimal answer on tiny
  instances) and a source of test scenarios; not a rule to reuse.
- BibTeX: `zhang2020mutex`

---

### [Ma-TokenPassing]: Lifelong Multi-Agent Path Finding for Online Pickup and Delivery Tasks

- Authors / Year / Venue: Hang Ma, Jiaoyang Li, T. K. Satish Kumar, Sven Koenig / 2017 / *Proc.
  16th Conference on Autonomous Agents and MultiAgent Systems (AAMAS 2017)*. Page range
  `[not identified]`.
- Link: https://arxiv.org/abs/1705.10868
- Peer-review status: published at AAMAS 2017 (the arXiv copy carries the AAMAS proceedings
  notice). Not a seed: it is the baseline [Okumura-PIBT] compares against (PIBT §5.2); located
  through the arXiv API by title and read at source.
- Verified: yes (full text read). **Read from** `refs/sr_tokenpassing_1705_10868.txt`.
- Sub-area: S3
- **Primary category: B** (secondary: A).
- Category justification: coordination runs through "the token … a synchronized shared block of
  memory that contains the current paths of all agents, task set, and agent assignments" (§4.1).
  An agent's **intended future path** is not inferable from its physical state, so this is the
  issue's own example of a B channel ("broadcasting an intended plan"). Given the token, each
  agent plans a path that does not collide with those in it, so contention never arises (A).
- Domain simulated: warehouse robots, modelled as agents on a grid. [§1, §6]
- The rule, stated precisely: one agent at a time holds the token (Algorithm 1 lines 5–6). The
  holder picks, among tasks whose pickup and delivery cells are not the end of any other path in
  the token, the one with the nearest pickup (lines 7–11), and writes into the token a
  cost-minimal space-time A* path that avoids every path already there (line 12). If no task is
  available it rests, unless it is sitting on some task's delivery cell, in which case it moves to
  a free endpoint "to avoid deadlocks" (lines 13–16). TPTS additionally lets the holder take over
  a task from an agent that would reach its pickup later (§4.2, Algorithm 2).
- Trigger condition: continuously / pre-emptively — whenever an agent reaches the end of its path
  it requests the token and plans; no conflict is ever detected. [§4.1]
- Information required: the token (every other agent's full remaining path, the task set,
  assignments), the shared map, a global clock, and precomputed distances to all endpoints. [§4.1]
- Tie-breaking: the order in which the system hands the token to requesting agents: "The system
  then sends the token to each agent that requests it, one after the other" (§4.1). **The order
  among simultaneous requesters is `[not stated in paper]`.** Whoever plans first effectively has
  priority, because later planners must avoid its path.
- Guarantees claimed: "All well-formed MAPD instances are solvable, and TP solves them" (Theorem
  3); likewise TPTS (Theorem 5). *Well-formed* means finitely many tasks, at least as many non-task
  endpoints as agents, and a path between any two endpoints that crosses no other endpoint
  (Definition 1). No optimality.
- Evaluation: a 21×35 warehouse grid, 500 tasks, 10–50 agents, six task frequencies (§6, Table 1),
  and an 81×81 grid, 1,000 tasks, 100–500 agents, for TP only (§6 "Scalability", Fig. 7). Metrics:
  makespan, service time, runtime per timestep.
- Does it work: yes, with a clear trade-off. TP runtimes are "less than 10 milliseconds" in the
  small warehouse; TPTS under 200 ms; the centralised baseline under 4,000 ms (§6). In return TP
  has the worst solution quality: TPTS and CENTRAL cut service time by "up to about 42 percent" and
  48 percent (§6). **Degradation at scale:** in the large warehouse TP takes 90.83 ms per timestep
  at 100 agents but 538.22 ms at 200 and 6,121.06 ms at 500 (Fig. 7 table). The paper's own text
  says the runtime "is smaller than 500 milliseconds for 200 agents", which **disagrees with its
  own table value of 538.22 ms**; I record both.
- Validated against real human or real traffic data: no. [§6]
- Scalability: 500 agents, 6,121.06 ms per timestep (Fig. 7). Computations "are not run in
  parallel in our experiments" (§6).
- Domain assumptions that limit portability: grid; lock-step; well-formed infrastructure with
  parking endpoints; a single synchronised shared memory; homogeneous agents. [§3.2, §4.1]
- Portability to a generic simulator: [inference] the mechanism — publish your plan, then
  everyone else plans around it — ports to any agent type, but it presupposes a shared blackboard
  and parking spots. A pedestrian crowd has neither. [Okumura-PIBT] states the same limitation:
  TP "requires … non-task endpoints" (PIBT §4.4.2).
- Limitations and future work stated by the authors: `[not stated in paper]` as a limitations
  section; the conclusion restates results (§7).
- Relevance to this FYP: [inference] the cleanest **category B** exemplar in S3, and useful
  because [Okumura-PIBT] reports beating it on runtime and being "comparable to or better" on
  solution quality without any shared plan (PIBT §5.2.2) — evidence, from the competing method's
  authors, that a no-communication rule can match a communication-based one.
- BibTeX: `ma2017tokenpassing`

---

### [Ma-DCC]: Learning Selective Communication for Multi-Agent Path Finding

- Authors / Year / Venue: Ziyuan Ma, Yudong Luo, Jia Pan / 2022 / *IEEE Robotics and Automation
  Letters* 7(2), 1455–1462.
- Link: https://doi.org/10.1109/LRA.2021.3139145 | https://arxiv.org/abs/2109.05413
- Peer-review status: published at IEEE RA-L (Crossref record). Not a seed: it is the survey
  [Wang-MAPFSurvey]'s example of request–response communication (§6.5, Table 9, "Ma et al.,
  2021b"; the survey's reference list gives the same RA-L volume and pages). Located through the
  arXiv API by title and read at source.
- Verified: yes (full text read). **Read from** `refs/sr_dcc_2109_05413.txt` (arXiv v2, 23 Dec
  2021). Equations partly lost in extraction; Eq. (1) is legible.
- Sub-area: S3
- **Primary category: B.**
- Category justification: agents exchange learned message vectors by request and reply, and the
  final action is computed from the aggregated messages (§IV-A, §IV-B d–e). The messages are
  internal embeddings, not physical state.
- Domain simulated: abstract agents on 2-D four-neighbour grids with partial observability. [§III-B]
- The rule, stated precisely — in two parts, because only one part is a rule:
  - *When to communicate (a stated rule).* Agent `i` computes the action it would take from its
    local observation, and the action it would take with neighbour `j` masked out. It requests a
    message from `j` **only if the two actions differ** (§IV-A; communication scope
    `C_i = {j : a_i ≠ a_{i,−j}}`, Eq. 1).
  - *What to do (not a rule).* A deep Q-network maps the aggregated messages to one of five actions
    (§IV-B e). This cannot be written as a function of observable state.
- Trigger condition: every timestep, for every neighbour inside the 9×9 field of view (§IV-C c).
  Communication fires on *predicted influence*, before any collision.
- Information required: a local 9×9 observation with obstacle, agent and four heuristic channels
  (§IV-B a); plus received messages and the relative positions of the sender's neighbours (§IV-B
  d).
- Tie-breaking: `[not stated in paper]` as a rule; argmax over Q-values (§IV-B c). Collisions in
  the environment are handled "by recursively resetting the related agents to previous states"
  (§III-B) — which is a C-type fallback, stated in one sentence and not analysed.
- Guarantees claimed: none.
- Evaluation: 40×40 and 80×80 maps at obstacle density 0.3; 200 cases per agent count in
  {4, 8, 16, 32, 64}, plus 128 on the larger map; against PRIMAL, DHC, and a nearest-two-neighbours
  baseline RR-N2 (§V). Average steps, Table II: on 40×40 with 32 agents, 135.55 for DCC, 147.26 for
  DHC, 170.48 for PRIMAL, 82.60 for the centralised planner ODrM*. ⚠ The row labels of Table II
  were partly scrambled in extraction; this row is the one whose alignment I am confident of.
- Does it work: it beats the other learned methods; it does not match a classical planner. Even at
  its best it takes more steps than ODrM* (Table II). The paper's own conclusion is that
  communication should be *reduced*: "agents will obtain irrelevant and redundant information from
  others due to broadcast communication, which harms the cooperation" (§V-A). Stated limitation:
  selecting neighbours costs up to `O(n·p)` (§V-B "Limitations").
- Validated against real human or real traffic data: no. [§V]
- Scalability: 128 agents on an 80×80 map (§V-A). Runtime `[not stated in paper]`.
- Domain assumptions that limit portability: grid; lock-step; homogeneous agents with shared
  network weights (§IV-C); trained up to 16 agents on 40×40 (§IV-C b).
- Portability to a generic simulator: [inference] the policy does not port (it is a trained
  network). The *communication trigger* does: *only consult a neighbour if its presence would
  change what I do* is a stateable, domain-free rule for deciding when an interaction counts as a
  conflict worth resolving.
- Limitations and future work stated by the authors: the selection cost above; extending to
  centralised-training frameworks; finding the maximum number of agents it can handle. [§V-B, §VI]
- Relevance to this FYP: [inference] **category B exemplar, and a result that favours the
  supervisor's hypothesis**: in a method built on communication, less communication did better.
- BibTeX: `ma2022dcc`

---

### [Grover-Deadlock]: The Before, During, and After of Multi-Robot Deadlock

- Authors / Year / Venue: Jaskaran Grover, Changliu Liu, Katia Sycara / *The International Journal
  of Robotics Research* 42(6), 317–336; published online 2022-07-09 (Crossref,
  doi:10.1177/02783649221074718). The arXiv comment says "WAFR 2020 Special Issue".
- Link: https://doi.org/10.1177/02783649221074718 | https://arxiv.org/abs/2206.01781
- Peer-review status: published at IJRR. Not a seed and not reached from a seed's reference list:
  I knew of the paper beforehand, located it through the arXiv API by title, and confirmed the
  journal record in Crossref. Logged as such in [search-log.md](search-log.md).
- Verified: yes — **selectively.** Read in full: Abstract, §1, §2, §3, §4 up to the start of
  Phase 1, §5 from the set-theoretic definition onward, §6, §7. Not read: the remainder of §4's
  lemmas and all appendices (proofs). **Read from** `refs/sr_deadlock_2206_01781.txt` (arXiv v1,
  the accepted manuscript in the journal's template; journal page numbers are not on this copy).
- Sub-area: S3
- **Primary category: C** (secondary: A).
- Category justification: the paper's stated position is that "a guaranteed way to resolve
  deadlock is to allow it to occur and then correct it using a reactive mechanism" (§7). A
  deadlock is detected, then a fixed manoeuvre resolves it (§6) — C. Before that, a control-barrier
  quadratic program keeps robots apart continuously (§3) — A. No messages are exchanged; the
  controller is "decentralized" (Abstract).
- Domain simulated: robots (single-integrator points; Khepera IV robots in experiments). [§3, §6]
- The rule, stated precisely: **Phase 1** — each robot solves a QP for the velocity closest to its
  goal-seeking velocity subject to one collision constraint per other robot (§3, Eqs. 6–8).
  Deadlock is declared when both the commanded velocity is near zero and the robot is not at its
  goal (Definition 1; §6 item 1: compare against "small thresholds"). **Phase 2** — the robots
  *rotate around each other* at exactly the safety distance, by feedback linearisation, with the
  extra constraint that their velocities sum to zero so the centroid stays fixed, until they have
  swapped positions (§6 item 2). **Phase 3** — resume the plain goal-seeking controller, which is
  now feasible (§6 item 3).
- Trigger condition: once contention has occurred — on detected deadlock. [§6 item 1]
- Information required: positions of all other robots (to form the constraints), own goal. For
  Phase 2, the paired robot's position and a shared sense of rotation. [§3; §6]
- Tie-breaking: this paper is the most informative in the review on *why* ties are a problem, and
  the least on how to break one.
  - It proves symmetric head-on set-ups **necessarily** deadlock, and that giving the two robots
    different controller gains does not prevent it (Theorem 1, §4; §1: "heterogeneity in robots'
    controller parameters is not sufficient to avoid deadlock").
  - It rejects random perturbation as a tie-break because it "lack[s] formal guarantees" and
    "there is no guarantee that deadlock will not relapse" (§2; §6).
  - **The direction of rotation in Phase 2 is `[not stated in paper]` in the sections I read** —
    the controller derivation is deferred to the appendix of an earlier paper (§6 item 2, citing
    Grover et al. 2019). So the one choice that actually breaks the symmetry is not specified here.
- Guarantees claimed: collision avoidance in Phase 1 by construction (§3); the three-phase strategy
  "ensures that the robots will not fall back in deadlock and will converge to their goals"
  (Theorem 8), **proved for N = 2, with N = 3 called "a trivial extension"** (§6).
- Evaluation: simulation with two and three robots and experiments on Khepera IV robots (§6, Figs.
  10–12). No quantitative table. For nonholonomic robots deadlock only occurred when body frames
  were perfectly aligned, so the experiment "simulated a virtual deadlock at t = 0" (§6).
- Does it work: for two and three robots, in the configurations tested. The authors are explicit
  about the limit: the number of admissible deadlock configurations for N = 1, 2, 3, 4 is 1, 1, 4,
  18 (§5), which "makes the analysis and resolution for N ≥ 4 complex" (§7). Only one of the two
  three-robot deadlock categories was observed, "so our resolution algorithm is specific for this
  category" (§6).
- Validated against real human or real traffic data: no. Tested on physical robots, which is a
  hardware test, not a comparison with recorded behaviour. [§6]
- Scalability: **three robots.** [§6]
- Domain assumptions that limit portability: holonomic single-integrator dynamics; no actuator
  limits (§3); continuous space; every robot runs the same controller.
- Portability to a generic simulator: [inference] the *finding* ports better than the rule. The
  finding — perfectly symmetric conflicts deadlock under any purely reactive avoidance rule, and
  differing parameters do not fix it — applies to any agent type and explains why a crowd simulator
  using reactive avoidance alone stalls in a corridor. The rule (rotate about each other) needs
  free space on both sides, which a corridor does not have.
- Limitations and future work stated by the authors: extend to N ≥ 4; apply the analysis to
  velocity obstacles and the safe-set method. [§7]
- Relevance to this FYP: [inference] **the theoretical justification for needing a category C rule
  at all.** It is the strongest source for the claim that an avoidance rule is not enough and an
  arbitration rule must sit behind it — the same two-layer split issue #20's shortlist proposed.
- BibTeX: `grover2022deadlock`

---

### [Dergachev-ORCA-MAPF]: Distributed Multi-agent Navigation Based on Reciprocal Collision Avoidance and Locally Confined Multi-agent Path Finding

- Authors / Year / Venue: Stepan Dergachev, Konstantin Yakovlev / 2021 / *2021 IEEE 17th
  International Conference on Automation Science and Engineering (CASE)*, pp. 1489–1494.
- Link: https://doi.org/10.1109/CASE49439.2021.9551564 | https://arxiv.org/abs/2107.00246
- Peer-review status: published at IEEE CASE 2021 (Crossref record
  `refs/sr_cr_late_additions.json`; the arXiv copy states "This is a preprint of the paper accepted
  to CASE'21"). Not a seed: found by web search late in the work (query
  `navmesh local avoidance game engine agents deadlock doorway peer-reviewed paper`), after the
  first drafts of the synthesis files were written. **It changed two conclusions**; see
  [search-log.md](search-log.md) §6.
- Verified: yes (full text read; it is five pages). **Read from**
  `refs/sr_orca_localmapf_2107_00246.txt` (arXiv v1). ⚠ Fig. 3 (success rates) and Table I did not
  survive text extraction; the numbers below are from the prose of §I and §V.
- Sub-area: S3 (continuous-space multi-agent navigation; the paper names "mobile robotics, video
  games, crowd simulation" as applications, §I).
- **Primary category: B** (secondary: C and A). **Hard to classify — see
  [category-summary.md](category-summary.md) §4.**
- Category justification: three mechanisms in sequence. Normally agents avoid each other with ORCA
  (A). When a deadlock is detected — a conflict state that already exists — it is resolved by a
  deterministic procedure, not by bargaining (C). But that procedure runs on information the agents
  must tell each other: on detection, "the agents involved in deadlock exchange the information on
  their current positions and desired goals" (§I), and detection itself needs neighbours to report
  their average speed (§IV-A). Goals and averaged speeds are not inferable from momentary physical
  state, so by the issue's boundary rule the resolution is B. I apply the same test as for
  [Shah-AROW]: the outcome depends on the content of the exchange. `[inference]` In a simulator the
  exchange is unnecessary and the same rule is C.
- Domain simulated: abstract disc agents moving freely in continuous 2-D space over a known grid
  map. [§III]
- The rule, stated precisely:
  - *Normal mode.* Follow an individually planned any-angle path; set velocity by ORCA (§IV;
    Algorithm 1 lines 11–12).
  - *Deadlock detection.* Each step, compute own average speed over the last *k* steps. If it is
    below `v_low`, ask the agents in communication range for theirs; "If any of the neighbours
    report its mean speed to be lower than v_low, then the deadlock is considered to be detected"
    (§IV-A). Parameters used: *k* = 250, `v_low` = 0.001 (§V).
  - *Who takes part.* The detecting agent's neighbours and their neighbours switch to "MAPF mode"
    (§IV-B a).
  - *Local instance.* The bounding rectangle of the participants, plus an offset, overlaid on the
    grid (§IV-B b). Each participant takes the nearest free cell as its start and, as its goal, the
    reachable cell nearest its next waypoint — **in priority order, so that a higher-priority agent
    gets first choice of cell** (§IV-B c).
  - *Solve.* Every participant runs the same deterministic solver on the same shared model, so all
    obtain the same plan with "no central controller": Push and Rotate first (fast, always
    succeeded in their tests), then bounded-suboptimal conflict-based search for a cheaper plan if
    it finishes within the time cap (§IV, §IV-C). Both solvers are pre-window methods; see
    [pre-window-foundations.md](pre-window-foundations.md).
  - *Return.* When all have finished their plans, go back to normal mode (Algorithm 1 lines 19–22).
    An outside agent that wanders in is added and the instance is rebuilt (lines 23–27).
- Trigger condition: once contention has occurred — on detected deadlock: at least two
  neighbouring agents with near-zero average speed over 250 steps. [§IV-A]
- Information required: neighbours' positions and velocities within 3 cells (for ORCA); neighbours'
  **reported average speeds**; and, once in MAPF mode, participants' **positions and current
  waypoint goals**, exchanged; the static grid map, known to all. [§III assumptions 1 and 5; §IV]
- Tie-breaking: **random.** "Each agent in the MAPF mode is randomly assigned a unique priority"
  (§IV-B a). The priority decides who gets the nearest start cell and the best goal cell. ⚠ The
  paper also says the whole procedure is deterministic so that every agent computes the same
  answer (§IV); **how a random priority is made identical across agents is `[not stated in
  paper]`.**
- Guarantees claimed: none for the whole pipeline. ORCA's collision guarantee "under certain mild
  assumptions" is cited (§II); Push and Rotate is called "a complete, polynomial-time algorithm"
  (§IV-C); the combination is not proved.
- Evaluation: four grid maps — two 64×64 "Gaps" maps (two halls joined by 1 or 3 narrow passages),
  a 64×64 warehouse, a 32×32 rooms map; 5 to 40 agents; **250 instances per agent count**; agents
  are discs of radius 0.3 cell (0.49 for the avoidance computation); against plain ORCA with path
  planning ("ORCA*") and the authors' earlier hybrid ("Base") (§V). Success means every agent
  reaches its goal within 20,000 steps.
- Does it work: yes in confined maps, and the baseline's failure is the more important result.
  - "on the Gaps 3 map, our approach was able to solve 99% of tasks involving 40 agents while
    BASE's success rate was slightly above 70% and **ORCA was not able to solve a single instance
    in this setup**" (§V).
  - The headline: success "raises from 10-15% to 95-99% in certain cases" (§I).
  - On the open Warehouse map the difference "is negligible" — "even basic collision avoidance
    techniques perform well" where there are no confined passages (§V).
  - **Not 100%.** The authors' explanation: the transition, when agents move to their grid start
    cells "relying only on collision avoidance" (§V).
  - Resolution is frequent and large: up to 95 solver calls for 40 agents on the rooms map; up to
    32 of 40 agents drawn into one local instance on the single-passage map (§V).
  - The cheaper-plan solver "failed to find solutions in numerous cases" within the 1 s cap (§V).
- Validated against real human or real traffic data: no. [§V]
- Scalability: 40 agents (§V). Runtime `[not stated in paper]` beyond the 1 s cap on solving.
- Domain assumptions that limit portability: a static grid map known to every agent; homogeneous
  discs smaller than half a cell; perfect control and perfect sensing within range; agents willing
  and able to exchange goals. [§III]
- Portability to a generic simulator: [inference] **high, and this is the architecture the FYP's
  simulator most resembles.** It is the only source in the review that takes continuous-space,
  velocity-avoiding agents — the same kind as a pedestrian model — and bolts an arbitration layer
  onto them. What a simulator would change: drop the message exchange (it already knows goals and
  speeds), and replace the random priority with something meaningful. The detection rule (two
  neighbours both stalled over a window) is domain-free and cheap.
- Limitations and future work stated by the authors: kinematic constraints; unknown environments.
  [§VI]
- Relevance to this FYP: [inference] **reuse the structure; the open slot is the priority.** Its
  architecture — avoid by default, detect a stall, arbitrate locally, resume — is the two-layer
  split issue #20's shortlist recommended, here implemented and measured. Its precedence order is a
  random draw.
- BibTeX: `dergachev2021orcamapf`

---

### [Wang-MAPFSurvey]: Where Paths Collide: A Comprehensive Survey of Classic and Learning-Based Multi-Agent Pathfinding

- Authors / Year / Venue: Shiyue Wang, Haozheng Xu, Yuhan Zhang, Jingran Lin, Changhong Lu,
  Xiangfeng Wang, Wenhao Li / 2025 / arXiv:2505.19219. The copy is headed "Preprint. Under review."
- Link: https://arxiv.org/abs/2505.19219
- Peer-review status: **[preprint]**. I searched Crossref by title for a published version and
  found none (2026-10-04).
- Verified: **partly.** This is a 100+ page survey; I read §2.2–§2.3, §3.4 (opening), §3.4.4,
  §3.4.7–§3.4.8, §6.5, and keyword-searched the rest. I make no claim about any other section.
  **Read from** `refs/sr_mapf_survey_2505_19219.txt` — ⚠ this is **v2** (31 Jul 2025); the issue
  linked v1. Section numbers are v2's.
- Sub-area: S3
- **Primary category: uncategorised (survey).** A survey has no single mechanism. It is used here
  as an entry point and as the 2016+ source that describes pre-window methods, as the issue
  prescribed.
- Category justification: n/a — but its own taxonomy maps onto the issue's categories and is
  recorded below.
- Domain simulated: n/a (survey of grid MAPF). 
- The rule, stated precisely: none of its own. What it supplies:
  - **The one-line statement of the priority family:** "lower-priority agents must defer to
    higher-priority paths" (§3.4.8); "a conflict is effectively 'won' by the higher-priority
    agent's path" (Table 4).
  - **Pre-window pointers** (recorded in [pre-window-foundations.md](pre-window-foundations.md),
    not summarised): prioritised planning (Erdmann & Lozano-Pérez, 1987) and **First Come First
    Served (Dresner & Stone, 2004)** as *fixed* priority schemes (§3.4 opening).
  - **Three in-window enhancement families** for priority search: priority inheritance
    (PIBT / winPIBT), conflict-driven merging, and mechanism-design priority with a VCG-like tax
    (§3.4.4).
  - **A five-way typology of communication** in learned MAPF: none, broadcast, priority-based
    (top-k neighbours), attention-based, request–response (§6.5, Table 9).
- Trigger condition: n/a.
- Information required: its centralised / decentralised split is defined by information: a
  decentralised agent's decision rule acts on "its (potentially partial) view of the environment"
  (§2.2, Eq. 4).
- Tie-breaking: the survey's Fig. 8 shows the consequence of the choice rather than a rule for
  making it: on one 2×5 instance, planning green-then-orange succeeds and orange-then-green "yields
  no feasible solution, demonstrating that a 'wrong' priority can break completeness" (§3.4, Fig.
  8 caption).
- Guarantees claimed: reported second-hand, so I record only the survey's own summary: static
  priority search is "generally not guaranteed to find an optimal solution" and "typically yields
  suboptimal or incomplete results in large grids" (Table 4).
- Evaluation: none of its own.
- Does it work: n/a. One observation that bears on the supervisor's hypothesis, quoted with its
  hedge: with broadcast communication, "Social conventions (e.g., 'move right if in conflict') can
  emerge, but the overhead of repeated broadcasts can be high" (§6.5). ⚠ The survey gives **no
  citation** for that sentence, so it is the survey authors' remark, not a sourced finding.
- Validated against real human or real traffic data: n/a. My keyword search of the cached text for
  `human` and `pedestrian` found no discussion of validating MAPF rules against human behaviour.
- Scalability: reports that the "most advanced classical methods … can handle thousands" (§1) —
  second-hand.
- Domain assumptions that limit portability: the surveyed field is grid-based (§2).
- Portability to a generic simulator: n/a.
- Limitations and future work stated by the authors: not read.
- Relevance to this FYP: [inference] entry point and terminology. Two things are worth carrying
  forward: the communication typology (§6.5) gives finer labels inside category B, and the Fig. 8
  example is a compact illustration, for the report, of why the *choice* of priority order — the
  thing the FYP wants to extract — matters.
- ⚠ **Citation caution.** The survey cites PIBT as "Originally proposed by Okumura et al. (2022a)"
  and winPIBT as "(Okumura et al., 2019)" (§3.4.4). PIBT was first published at IJCAI 2019 (see
  [Okumura-PIBT]); 2022 is the journal version. Do not copy the survey's dating into the report.
- BibTeX: `wang2025mapfsurvey`

---

## Not obtained

### [NOT OBTAINED] Multi-agent path finding with mutex propagation (journal version)
- Authors / Year / Venue: Han Zhang, Jiaoyang Li, Pavel Surynek, T. K. Satish Kumar, Sven Koenig /
  2022 / *Artificial Intelligence* 311, 103766
- Link tried: https://doi.org/10.1016/j.artint.2022.103766 ;
  https://www.sciencedirect.com/science/article/abs/pii/S0004370222001060
- Reason unavailable: paywall
- Date attempted: 2026-10-04
- Status: awaiting PDF from user

### [NOT OBTAINED] Fast, On-line Collision Avoidance for Dynamic Vehicles Using Buffered Voronoi Cells
- Authors / Year / Venue: Dingjiang Zhou, Zijian Wang, Saptarshi Bandyopadhyay, Mac Schwager /
  2017 / *IEEE Robotics and Automation Letters* 2(2), 1047–1054
- Link tried: https://doi.org/10.1109/LRA.2017.2656241 (Unpaywall reports no open-access copy)
- Reason unavailable: paywall
- Date attempted: 2026-10-04
- Status: awaiting PDF from user
