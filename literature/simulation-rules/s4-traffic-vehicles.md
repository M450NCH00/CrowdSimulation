# S4 — Traffic and autonomous vehicles

> **Draft pending supervisor review.** Prepared for issue
> [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). Read date for every entry:
> 2026-10-04.

Companion files: [S1](s1-crowd-simulation.md) · [S2](s2-games.md) · [S3](s3-mapf-robotics.md) ·
[rule catalogue](rule-catalogue-simulation.md) · [category summary](category-summary.md) ·
[research gap](research-gap.md) · [pre-window foundations](pre-window-foundations.md) ·
[missing papers](missing-papers.md) · [search log](search-log.md) · [refs](refs-simulation-rules.bib)

## How to read this file

- The issue gave **no seeds** for S4; every entry here was found by me and confirmed from the
  paper's own page. How each was found is in [search-log.md](search-log.md) §4.
- Categories **A / B / C** are the issue's. This is the sub-area the issue expected to "supply
  genuine category B examples", and it does: four of the seven entries are primarily B. One is primarily C ([Pruekprasert-RightOfWay]).
- **Five of the seven entries were read as arXiv copies of papers that are also published.** Each
  entry says which; section and equation numbers are the arXiv copy's.
- `[inference]` marks my judgement, not the paper's claim.
- **Cross-reference to issue #20.** That review reported that "no arrival-order rule was found in
  anything opened" ([`../game-theory/search-log.md`](../game-theory/search-log.md) §9, and risk R6
  in its §10). **This sub-area contains it.** First-come-first-served appears as the operative rule in [Shah-AROW] and
  [Malikopoulos-SignalFree], and as the measured baseline in [Xu-TreeSearch]; and
  [Pruekprasert-RightOfWay] gives precedence to whoever is "already engaged in the intersection". See
  [rule-catalogue-simulation.md](rule-catalogue-simulation.md) §3.

Contents: [ShalevShwartz-RSS] · [Malikopoulos-SignalFree] · [Xu-TreeSearch] · [Shah-AROW] ·
[Ahmed-MergeAssist] · [Pruekprasert-RightOfWay] · [Mariani-CoordSurvey]

---

### [ShalevShwartz-RSS]: On a Formal Model of Safe and Scalable Self-driving Cars

- Authors / Year / Venue: Shai Shalev-Shwartz, Shaked Shammah, Amnon Shashua (Mobileye) / 2017
  (v6: 27 October 2018) / arXiv:1708.06374.
- Link: https://arxiv.org/abs/1708.06374
- Peer-review status: **[preprint]**. A Crossref title search on 2026-10-04 returned no published
  version. ⚠ It is also a **company technical paper** (affiliation "Mobileye, 2017" on the first
  page), so it shares the caveat of the industry sources in S2: it describes a design, with proofs
  but no experiments.
- Verified: **partly.** Read: Abstract, §1 opening, §3 introduction (the five rules), §3.1, §3.5,
  §3.7 (including §3.7.1), §3.8, §3.11. Not read: §2, §3.2–§3.4, §3.6, §3.7.2, §3.9–§3.10, §4–§6
  (driving policy, sensing). **Read from** `refs/sr_rss_1708_06374.txt`.
- Sub-area: S4
- **Primary category: A** (secondary: C). **Hard to classify — see
  [category-summary.md](category-summary.md) §4.**
- Category justification: the model's core is a *safe distance* each vehicle must keep and a
  *proper response* it must make the moment that distance is lost; if everyone complies "there will
  be no collisions" (Lemma 5, §3.5). The collision — the conflict that matters on a road — is never
  instantiated, so A. But at junctions the model **arbitrates**: "one route has priority over
  others, and vehicles riding on it have the right of way" (§3.7), and the proper response is
  different for the prioritised and the non-prioritised vehicle (Definition 18). That is a C-type
  rule embedded in an A-type framework. No communication is assumed anywhere in the sections read.
- Domain simulated: road vehicles; pedestrians are covered in one subsection (§3.8). No simulation
  is reported.
- The rule, stated precisely: RSS formalises five "common sense" rules (§3): **(1)** do not hit
  someone from behind; **(2)** do not cut in recklessly; **(3)** right-of-way is given, not taken;
  **(4)** be careful of areas with limited visibility; **(5)** if you can avoid an accident without
  causing another one, you must do it. The parts read in full:
  - *Following (rule 1).* A rear car's distance is safe if, were the front car to brake at up to
    `a_max,brake` while the rear car accelerates at up to `a_max,accel` for a response time ρ and
    then brakes at least `a_min,brake`, they would not collide (Definition 1). The minimum distance
    has a closed form in the two speeds and those four parameters (Lemma 2).
  - *Junctions (rule 3).* Between vehicles on two intersecting routes, the longitudinal distance is
    safe if (1) the vehicle on the route **without priority** can accelerate for ρ and then brake
    and still stay out of the other route; or (2) one vehicle is "in front" — closer to the
    intersection region — and would remain in front under worst-case braking and acceleration; or
    (3) their possible arrival-time intervals at every shared point do not overlap (Definitions
    16–17). When the situation becomes dangerous: in case (1) the prioritised vehicle "can drive
    normally" and the other "must brake"; in case (2) the one behind must brake; in case (3) both
    must brake (Definition 18).
  - *"Given, not taken".* A green light or a priority route does not license ignoring a vehicle
    already in the junction: "Even if the yellow car's route has a green light, we do not expect it
    to ignore the red car that is already in the intersection" (§3.7.1, Fig. 9).
  - *Pedestrians.* Priority depends on road type: "in a typical residential street, a pedestrian
    has the priority over the vehicles", whereas on a road with a sidewalk "cars have the
    priority"; and "even if pedestrians do not have priority, if they entered the road at a safe
    distance, cars must brake and let them" pass (§3.8).
- Trigger condition: the safe-distance check is continuous; the *proper response* fires at the
  "Danger Threshold time", the first moment the distance is unsafe both longitudinally and
  laterally (Definitions 9–10, §3.5). So: continuous monitoring, action on predicted conflict.
- Information required: other road users' positions and velocities; the lane/route geometry; and
  **the priority relation between routes** — from the road layout, signs, or signals (§3.7,
  §3.7.1). Four dynamics parameters and a response time must be agreed (Definition 1).
- Tie-breaking: the paper anticipates the question. For "who is in front" when two vehicles are
  20 m and 20.1 m from a junction, it answers that the definition "is effectively being used only
  when there is a safe longitudinal distance between the two cars, and in that case the ordering
  between the cars will be obvious" (Remark 7). Where neither has priority and neither is clearly
  in front, the rule is **both brake** (Definition 17 item 3; Definition 18, third bullet).
  [inference] That is a safe tie-break that produces a standstill, not a resolution — the paper
  does not say who then moves first.
- Guarantees claimed: collision-freedom **if every road agent complies**: Lemma 5 for same-geometry
  multi-lane roads (§3.5); "Utopia is possible", Corollary 2, when occlusions are included
  (§3.11). The framework is designed to assign *responsibility* when not everyone complies, not to
  prevent the accident. No liveness or deadlock-freedom claim in the sections read.
- Evaluation: **none.** The paper argues that statistical validation of safety is infeasible (§1,
  §2 by its heading) and offers proofs instead. No simulation or road data is reported in the
  sections I read; a keyword search of the full text for `experiment` and `simulat` found only
  that argument.
- Does it work: on its own terms it is proved, not tested. The paper's evidence supports *no
  collisions if all comply* and nothing about throughput, delay, or what happens when the
  both-brake case arises.
- Validated against real human or real traffic data: no. Its rules are described as formalised
  "common sense" (§3), not as fitted to driver behaviour.
- Scalability: `[not stated in paper]` as a count. The scalability in the title refers to
  engineering cost; the structural point is that each vehicle evaluates the rule against each other
  vehicle "individually" — a "star-shape calculation" (Remark 8).
- Domain assumptions that limit portability: lane-based coordinates (§3.2); known braking and
  acceleration bounds; a priority relation supplied by infrastructure; all agents obey the same
  parameters.
- Portability to a generic simulator: [inference] **the structure ports; the parameters do not.**
  *Keep a gap you can stop in; when the gap is lost, the non-prioritised party yields; priority is
  given, not taken* is not specific to cars, and §3.8 already applies it to pedestrians. To move it
  to a crowd, the braking model becomes a stopping-distance model for walkers, and — the hard part
  — the *priority relation* has to come from somewhere, because a corridor has no signs. That
  missing priority relation is precisely what the FYP proposes to elicit.
- Limitations and future work stated by the authors: `[not read]` — the relevant later sections
  were not read.
- Relevance to this FYP: [inference] **reuse the frame.** It is the most complete written statement
  in this review of a communication-free right-of-way rule, and "given, not taken" is the cleanest
  available answer to the objection *what if the other agent does not follow the rule*.
- BibTeX: `shalevshwartz2017rss`

---

### [Malikopoulos-SignalFree]: A Decentralized Energy-Optimal Control Framework for Connected Automated Vehicles at Signal-Free Intersections

- Authors / Year / Venue: Andreas A. Malikopoulos, Christos G. Cassandras, Yue J. Zhang / 2018 /
  *Automatica* 93, 244–256.
- Link: https://doi.org/10.1016/j.automatica.2018.03.056 | https://arxiv.org/abs/1602.03786
- Peer-review status: published at *Automatica* (Crossref record
  `refs/sr_cr_10_1016_j_automatica_2018_03_056.json`).
- Verified: **partly.** Read: Abstract, §1 (first part), §2 opening, §2.1, the assumptions and the
  throughput problem set-up in §2.2, §3 opening, §3.2 (end), §4, §5. Not read: the analytical
  solution (§3.1) and the appendices (proofs). **Read from** `refs/sr_malikopoulos_1602_03786.txt`
  (arXiv v8, 31 Mar 2018). ⚠ Mathematical symbols were largely lost in extraction; equations are
  cited by number only.
- Sub-area: S4
- **Primary category: B** (secondary: C).
- Category justification: each vehicle's control depends on information it cannot observe: its
  assigned index, its queue position, and the time the vehicle ahead of it in the queue will enter
  the merging zone — relayed by a "coordinator" that "only enables communication of appropriate
  information among CAVs" and "is not involved in any decision" (§2; information set, Definition
  3, Eq. 17). The crossing *order* itself, though, is set by a rule: first-in-first-out (§2). So
  the outcome depends on message content (B), and the arbitration principle is a fixed rule (C).
- Domain simulated: connected automated vehicles at a four-way intersection without signals. [§2]
- The rule, stated precisely: define a Control Zone of length *L* before a square Merging Zone of
  side *S* (§2, Fig. 1). Vehicles are queued in the order they enter the Control Zone; each must
  enter the Merging Zone no earlier than the one before it in the queue (Eq. 1): "we may impose a
  strict first-in-first-out queueing structure, where each vehicle must enter the MZ in the same
  order it entered the CZ" (§2). On entering, a vehicle is given an identity `(w, i, j)` — a unique
  index, its queue position, and which of four positional relations it has to the vehicle ahead
  (same lane; same road different lane; conflicting road; opposite direction) (§3, Definition 1).
  Its Merging-Zone entry time is then fixed recursively from the previous vehicle's by Eq. (14),
  and it follows the acceleration profile that minimises the integral of squared acceleration
  subject to arriving at that time (Eq. 18). Speed is constant inside the Merging Zone
  (Assumption 2).
- Trigger condition: once, on entry to the Control Zone — well before the vehicles meet. The
  schedule is then followed; re-evaluation happens only on an "event" such as unexpected braking
  ahead (§3.2, end).
- Information required: own position and speed; the distance to the vehicle directly ahead in the
  lane (by on-board sensor, Assumption 3); and, **through the coordinator**, the unique index,
  queue subset, and the assigned Merging-Zone time of the preceding vehicle (Eq. 17). Perfect,
  delay-free measurement is assumed (Assumption 3).
- Tie-breaking: arrival order. For exactly simultaneous arrivals: "If two or more CAVs enter the CZ
  at the same time, then the coordinator assigns randomly the index w" (§3).
- Guarantees claimed: a closed-form optimal control for each vehicle, and "conditions under which
  feasible solutions satisfying all safety constraints always exist" (Abstract; Theorem 2). The
  guarantee is conditional on feasible initial conditions; the paper says enforcing them "is
  nontrivial" and proposes a "Feasibility Enforcement Zone" before the Control Zone (§2.1
  discussion of Assumption 1; §3.2).
- Evaluation: (1) 20 vehicles at one intersection in MATLAB: *S* = 30 m, *L* = 400 m, minimum gap
  10 m, speed limit 13 m/s (§4). (2) **448 vehicles** through two real Boston intersections in
  tandem, modelled in VISSIM, Poisson arrivals at 450 veh/h per lane, against fixed-time traffic
  lights (§4). Result: fuel consumption improved 46.6% and travel time 30.9% (§4, Fig. 5).
- Does it work: against fixed-time traffic lights, strongly, in simulation. **What the paper
  itself flags:** in the first case study "CAV #16 violates both the control constraint … and the
  state constraint" (§4) — the unconstrained solution was infeasible for that vehicle. And the rule
  is named as a limitation: "The first-in-first-out queue imposes several limitations that can
  become even more apparent in heavy-volume traffic situations" (§5). No turns and no lane changes
  are modelled (§2).
- Validated against real human or real traffic data: no. The second case study uses the *geometry*
  of two real intersections (§4); the traffic is synthetic and every vehicle is automated.
- Scalability: 448 vehicles in total over the simulation, at 450 veh/h per lane (§4). Computation
  time: `[not stated in the sections read]`. Each vehicle's problem has a closed-form solution,
  which is the paper's argument for online use (§3).
- Domain assumptions that limit portability: fixed lanes; a defined control zone with a
  communication relay; 100% automated, compliant vehicles; no turns; perfect sensing. [§2, §2.1]
- Portability to a generic simulator: [inference] the *scheduling skeleton* ports well: define a
  zone around a contested resource, order arrivals first-in-first-out, give each arrival the
  earliest slot after its predecessor. In a simulator the "coordinator" costs nothing, because the
  simulator already knows the arrival order. The energy-optimal control is vehicle-specific and
  does not port.
- Limitations and future work stated by the authors: relax first-in-first-out through a
  higher-level scheduling problem; partial penetration of automated vehicles; errors and delays.
  [§5]
- Relevance to this FYP: [inference] **baseline, and the anchor for the arrival-order rule.** A
  peer-reviewed, implemented instance of *whoever arrived first passes first*, with a random
  tie-break and the authors' own statement that the rule is the weak point.
- BibTeX: `malikopoulos2018signalfree`

---

### [Xu-TreeSearch]: Cooperative Driving at Unsignalized Intersections Using Tree Search

- Authors / Year / Venue: Huile Xu, Yi Zhang, Li Li, Weixia Li / 2020 / *IEEE Transactions on
  Intelligent Transportation Systems* 21(11), 4563–4571.
- Link: https://doi.org/10.1109/TITS.2019.2940641 | https://arxiv.org/abs/1902.01024
- Peer-review status: published at IEEE T-ITS (confirmed by Crossref title search, 2026-10-04).
- Verified: yes (full text read). **Read from** `refs/sr_treesearch_1902_01024.txt` — arXiv v1 (4
  Feb 2019), i.e. the submitted manuscript. ⚠ The published version may differ; numbers below are
  the preprint's Table I.
- Sub-area: S4
- **Primary category: B** (secondary: C, for its baseline).
- Category justification: the method rests on the assumption that "Each vehicle instantly and
  thoroughly shares its driving states (position, velocity, etc.) and intentions with other
  vehicles via vehicle-to-vehicle (V2V) communication" (§II). Shared *intentions* are a B channel.
  The crossing order is then computed jointly. The **baseline** it is measured against,
  first-in-first-out, is a pure C rule, and the paper's numbers on it are the reason this entry is
  here.
- Domain simulated: connected automated vehicles at a four-leg intersection, three lanes per leg.
  [§II, Fig. 1; §IV-A]
- The rule, stated precisely:
  - *Proposed method.* Treat every possible crossing order as a leaf of a tree (§II, Fig. 3).
    Search it by Monte Carlo tree search (§III-A), with two heuristics in the rollout: on one lane,
    the vehicle nearest the conflict zone goes first; among vehicles through the same conflict
    subzone, the one with the earlier desired arrival goes first, and where no vehicle is earliest
    at all its subzones, "we randomly select one vehicle among all candidate vehicles" (§III-B,
    Algorithm 2). Given an order, each vehicle's arrival time at each conflict subzone is the later
    of its own earliest arrival and the previous occupant's time plus a safety gap (Algorithm 1).
    The order is re-planned every 2 s within a 0.1 s budget (§IV-A, §IV-B).
  - *Baseline rule (what the catalogue records).* "Ad hoc negotiation based strategies organize all
    the vehicles according to the FIFO principle" (§III-B) — vehicles cross in the order they
    arrive, attributed to Dresner and Stone's reservation scheme, which "assigns these grids to
    CAVs in a roughly First-In-First-Out (FIFO) manner" (§I; a pre-window source, see
    [pre-window-foundations.md](pre-window-foundations.md)).
- Trigger condition: pre-emptively, for all vehicles inside the control zone, every 2 s. [§IV-A]
- Information required: positions, velocities and intended routes of all vehicles in the control
  zone, by V2V (§II); the intersection's division into conflict subzones (36 in the test, §IV-A).
- Tie-breaking: for the baseline, arrival order; simultaneous arrivals `[not stated in paper]`. For
  the proposed method, random selection among candidates in the rollout (Algorithm 2, step 2).
- Guarantees claimed: none of optimality; "nearly global-optimal" is an empirical description
  (Abstract). Collision avoidance comes from the safety gap in Algorithm 1 — 1.5 s straight or
  right, 2 s left (Eq. 4).
- Evaluation: (i) exhaustive enumeration on a single-lane intersection with 20 vehicles (§IV-C,
  Fig. 7); (ii) 20-minute simulations at three arrival rates (Table I). Point-queue traffic model
  with Poisson arrivals (§IV-A).
- Does it work — **and what it shows about first-come-first-served:**
  - With 20 vehicles, of "nearly 10 billion" valid orders, the tree-search order ranks 648th and
    **the FIFO order ranks 4,563,421,793rd** (§IV-C). FIFO is close to the middle of the
    distribution, not near the top.
  - Table I, average delay and throughput, FIFO versus tree search:
    150 veh/(lane·h): 1.3053 s, 589 veh vs 0.4499 s, 605 veh;
    300: **39.8313 s**, 1,095 veh vs 1.1407 s, 1,168 veh;
    450: 41.6996 s, 1,205 veh vs 4.8743 s, 1,766 veh.
  - [inference] The arrival-order rule is adequate in light traffic and collapses between 150 and
    300 veh/(lane·h): delay rises about thirty-fold.
  - The paper gives no failure case for its own method.
- Validated against real human or real traffic data: no. [§IV]
- Scalability: 30 vehicles in the parameter study (§IV-B); about 1,000 tree nodes searched within
  0.1 s "in our personal computer" (§IV-B). Largest simultaneous count in the 20-minute runs:
  `[not stated in paper]`.
- Domain assumptions that limit portability: fixed lanes; no lane changes in the control zone;
  constant speed through the conflict zone; full, instant communication (§II).
- Portability to a generic simulator: [inference] the tree search is a centralised optimiser and
  does not port as a per-agent rule. The **finding** ports: any simulator considering
  first-come-first-served as its arbitration rule should expect it to be fair, simple, and
  increasingly costly as load rises.
- Limitations and future work stated by the authors: field tests on prototype vehicles; other
  scenarios such as ramps and work zones. [§V]
- Relevance to this FYP: [inference] **the quantitative evidence on the arrival-order rule.**
  Issue #20 found no such rule in the game-theory literature and asked whether that was a gap; this
  paper shows the rule exists, is the field's standard baseline, and is measurably poor under load.
  That changes the FYP question from *is there an arrival-order rule* to *when does a rule better
  than arrival order pay off*.
- BibTeX: `xu2020treesearch`

---

### [Shah-AROW]: AROW: V2X-based Automated Right-of-Way Algorithm for Cooperative Intersection Management

- Authors / Year / Venue: Ghayoor Shah, Danyang Tian, Ehsan Moradi-Pari, Yaser P. Fallah / 2024 /
  *IEEE Transactions on Intelligent Transportation Systems* 25(9), 10983–10999.
- Link: https://doi.org/10.1109/TITS.2024.3384982 | https://arxiv.org/abs/2304.04958
- Peer-review status: published at IEEE T-ITS (confirmed by Crossref title search, 2026-10-04).
- Verified: **partly.** Read: Abstract, §I (first page), §IV (stages S0–S31 and the heuristics H1
  and H2; non-compliance), §VI-A, §VI-B.1 opening, §VI-B.3, §VII, §VIII. Not read: §II–§III
  (related work, the messaging system), §V (timed-automaton formalisation), §VI-B.2 (theoretical
  versus experimental transition probabilities). **Read from** `refs/sr_arow_2304_04958.txt`
  (arXiv v2, 17 Apr 2024). ⚠ **Table VIII's cells were scrambled in extraction**; the percentages
  below are from the prose of §VI-B.3.
- Sub-area: S4
- **Primary category: B** (secondary: C).
- Category justification: vehicles "use V2X to communicate with each other and negotiate SC-I
  crossing priorities" (§VII), exchanging discovery, announcement, turn-assignment and
  acknowledgement messages (§IV). The outcome is carried by message content — the assigned turns.
  The *content* of the assignment, however, is produced by a fixed rule (earliest arrival first),
  not by bargaining; hence C as secondary. [inference] The paper's word "negotiate" is generous:
  there are no counter-proposals, only acknowledgements.
- Domain simulated: connected vehicles at a four-way all-way stop-controlled intersection (SC-I),
  one lane per approach. [§VI-A]
- The rule, stated precisely (stages from §IV):
  - **S1, discovery.** On coming within 10 m of the stop line, broadcast a discovery message and
    wait `T1` (2 s) for others' (§IV-B; Table IV). If none arrives, cross.
  - **S21, choose an arbitrator** by a heuristic stored identically in every vehicle. **H1: "The
    last arriving CAV … is chosen as v_arb"**; if two arrive at the same timestamp, compare unique
    identifiers such as MAC addresses and take the one with the lowest ASCII value at the first
    differing character (§IV-C). No message is sent in this stage; it is "simply a computational
    stage".
  - **S22/S23, announce and acknowledge** the arbitrator (§IV-D, §IV-E).
  - **S31, assign turns.** **H2: the arbitrator "assigns turns based on the arrival timestamp of
    every CAV … and prioritizes CAVs that arrived earlier at the SC-I"** (§IV, stage S31).
  - **Later arrivals** during a round are told to wait and join the next round (§IV-B).
  - **Non-compliance.** A vehicle that crosses out of turn broadcasts an exit message; the others
    restart, up to `AROW_thresh = 2` times, after which the protocol is disabled and "the remaining
    compliant CAVs can follow any default heuristic … For this study, the default heuristic is set
    to FIFO" (§IV-F; §VI-A; §VI-B.3).
- Trigger condition: once contention is possible — when two or more vehicles arrive "at similar
  time intervals", operationally within the 2 s discovery window (§I; §IV-B).
- Information required: each vehicle's arrival timestamp and a unique identifier, exchanged by
  V2X; a shared clock good enough to compare timestamps; full connectivity ("Current study assumes
  full connectivity", §VIII).
- Tie-breaking: **stated twice, and differently for the two heuristics.** For the arbitrator (H1):
  deterministic, by lowest identifier (§IV-C). For turn order (H2): "In the situation where more
  than one CAV carries identical arrival timestamp, v_arb can randomly assign turns among them" —
  with the note that identifier order could be used instead, and that any H2 will do "as long as
  all CAVs contain this same heuristic" (§IV, stage S31).
- Guarantees claimed: distinct turns with "no duplicity and ambiguity" (§IV opening). The paper
  says its analysis is "sufficient to validate that the AROW algorithm has no deadlocks" (§VI-B.2,
  in a sentence found by keyword search; I did not read that analysis). "Completeness" is claimed
  from simulated state-transition frequencies under full compliance (§VI-B.1).
- Evaluation: SUMO, 50,000 s per run, 4 / 8 / 16 vehicles circulating through one intersection,
  non-compliance probability 0, 0.1, 0.25 (Tables III–IV), against SUMO's default all-way stop
  ("allway"), traffic lights, and a delay-based scheduler (DCIM). Metrics: frequency of *ambiguous
  instances* — false starts with two or three vehicles in the junction at once — and clearance time
  (§VI-B.3).
- Does it work: on its chosen metric, yes; on delay, it is no better than the default.
  - Full compliance: 100% of instances have a single vehicle in the junction, for every traffic
    level (§VI-B.3).
  - 4 vehicles, non-compliance 0.25: 0.2% ambiguous for AROW; 2.7% for DCIM; 4% for the default
    all-way stop (§VI-B.3).
  - 8 vehicles: 0.6% (non-compliance 0.1) and 3.1% (0.25) for AROW; 8.4% for DCIM. The default
    all-way stop is described as worst "with a total of 15.5%" — ⚠ that sentence straddles a column
    break in the extract, so the attribution of 15.5% to the 8-vehicle all-way case is my reading.
  - Clearance time is "similar to allway with no non-compliance and a slight comparative
    degradation in non-compliance scenarios" (§VII). The gain is in removing ambiguity, not in
    speed.
  - **Reported weakness of the comparator**, relevant to rule design: DCIM gives priority to the
    busier lane, so in dense, uneven traffic "a lesser priority CAV can potentially wait at the
    SC-I for a long time" (§VI-B.3) — a starvation failure of a load-based priority rule.
- Validated against real human or real traffic data: no. The default all-way stop is described as
  "similar to the real-life human behavior at an SC-I" (§VI-B.3) without data. Real-world testing
  is future work (§VIII).
- Scalability: 16 vehicles (§VI-A). The abstract's "scalable for high density traffic" refers to
  that 16-vehicle condition.
- Domain assumptions that limit portability: a single four-way stop; one lane per approach; full
  V2X connectivity; a common heuristic pre-installed in every vehicle.
- Portability to a generic simulator: [inference] **the two heuristics port; the protocol is
  unnecessary in a simulator.** Everything the messages establish — who arrived when — a simulator
  already knows. Strip the messaging and what remains is: *detect near-simultaneous arrival at a
  contested point; order by arrival time; break exact ties by identifier or at random; if someone
  jumps the order, restart at most twice, then fall back.* That is a complete category C rule for
  any agent type. The restart-then-fallback logic for non-compliant agents is the part most worth
  reusing; nothing else in this review handles non-compliance procedurally.
- Limitations and future work stated by the authors: real hardware tests; congested channels and
  message loss; mixed connected and unconnected traffic; emergency vehicles with different
  priorities; learning to predict non-compliance; tuning the timeouts. [§VIII]
- Relevance to this FYP: [inference] **reuse.** It is the closest thing in the review to the FYP's
  target object: an explicit, stateable arbitration rule for a symmetric conflict, with a defined
  tie-break and a defined response to rule-breakers. It also shows that the tie-break is treated as
  *arbitrary* by its authors ("Based on user preference, it can be changed") — the slot the FYP's
  LLM-derived rule would occupy.
- BibTeX: `shah2024arow`

---

### [Ahmed-MergeAssist]: A Cooperative Freeway Merge Assistance System using Connected Vehicles

- Authors / Year / Venue: Md Salman Ahmed, Mohammad A. Hoque, Jackeline Rios-Torres, Asad J.
  Khattak / 2018 / paper #18-05614, 97th Annual Meeting of the Transportation Research Board,
  Washington, D.C., January 2018.
- Link: https://arxiv.org/abs/1805.00508
- Peer-review status: **[preprint]**. ⚠ **Venue flag.** The first page says "Submitted for
  Presentation Only". I could not confirm an archival published version (a Crossref title search
  on 2026-10-04 failed to return a record), and I cannot verify from the document what review a
  presentation-only TRB paper receives. I therefore do not count it as peer reviewed. It is also an
  **extended abstract** ("Word Count: 1241").
- Verified: yes (full text read; it is two pages). **Read from**
  `refs/sr_mergeassist_1805_00508.txt`.
- Sub-area: S4
- **Primary category: B.**
- Category justification: the merging order is agreed through "an innovative three-way handshaking
  protocol" and is acted on only "when all the vehicles have mutually acknowledged and accepted the
  merging sequence" (Methodology). The outcome depends on exchanged messages.
- Domain simulated: **not simulated — field-tested** with human-driven vehicles receiving advice.
  [Experimental Results]
- The rule, stated precisely: vehicles broadcast basic safety messages every 0.1 s (identifier,
  GPS position, speed, time, direction), received within 300–500 m. A vehicle entering a ramp
  becomes "master" and triggers the algorithm. It collects neighbours' trajectories, estimates when
  each will reach the merging point, and starts a three-way handshake to distribute the timing
  information and synchronise. Once all have acknowledged, each vehicle displays an advisory such
  as "Slow down" (to a freeway vehicle) or "merge behind" (to the ramp vehicle) (Methodology).
  ⚠ **The rule that turns estimated arrival times into an order is not stated** — the paper says
  only that the system "determines the optimal merging order".
- Trigger condition: when a vehicle enters the ramp. [Methodology]
- Information required: broadcast position, speed, heading and time from all vehicles in range;
  GPS; a shared time base. [Methodology]
- Tie-breaking: `[not stated in paper]`.
- Guarantees claimed: none.
- Evaluation: field tests on Interstate 26 near Johnson City, Tennessee, at exits 27, 32, 34 and 36
  in both directions, with **three drivers** — two on the freeway, one on the ramp, the ramp driver
  timing his entry to create a conflict (Experimental Results). "The merging process in this
  experiment was concluded successfully". No quantitative result.
- Does it work: in the trial described. **Stated shortfall:** "improvements are needed to ensure
  that the system provides advisory to all vehicles involved in the test and that ramp curvatures
  are accounted for" — i.e. not every vehicle received its advisory.
- Validated against real human or real traffic data: **not validated, but tested with real
  drivers on a real road** — the only entry in S4 with any contact with human behaviour. No
  comparison against how drivers merge without the system is reported.
- Scalability: three vehicles. [Experimental Results]
- Domain assumptions that limit portability: ramp-and-freeway geometry; DSRC radios in every
  vehicle; drivers who follow advice.
- Portability to a generic simulator: [inference] low as a rule, since the ordering rule is not
  given. As a pattern it is the same as [Shah-AROW]: one agent initiates, a schedule is circulated,
  everyone acknowledges.
- Limitations and future work stated by the authors: higher levels of automation and other
  scenarios. [Conclusions]
- Relevance to this FYP: [inference] minor: a second category B exemplar, and a reminder that the
  field-tested system in this review is also the one with the least stated rule.
- BibTeX: `ahmed2018mergeassist`

---

### [Pruekprasert-RightOfWay]: Decision Making for Autonomous Vehicles at Unsignalized Intersection in Presence of Malicious Vehicles

- Authors / Year / Venue: Sasinee Pruekprasert, Xiaoyi Zhang, Jérémy Dubut, Chao Huang, Masako
  Kishida / 2019 / *2019 IEEE Intelligent Transportation Systems Conference (ITSC)*, pp. 2299–2304.
- Link: https://doi.org/10.1109/ITSC.2019.8917132 | https://arxiv.org/abs/1904.10158
- Peer-review status: published at IEEE ITSC 2019 (Crossref record
  `refs/sr_cr_late_additions.json`; the arXiv copy carries the 2019 IEEE copyright notice). Found
  by web search late in the work (query `intersection priority rule autonomous vehicles conflict
  resolution right-of-way rule-based unsignalized`), after the first drafts of the synthesis files.
  **It changed two conclusions**; see [search-log.md](search-log.md) §6.
- Verified: yes (full text read). **Read from** `refs/sr_malicious_intersection_1904_10158.txt`
  (arXiv v2, 3 Oct 2019). ⚠ Section headings were reduced to their first letters and **Table I's
  collision and congestion columns were scrambled** in extraction; I report its time-step column,
  which is aligned, and the prose.
- Sub-area: S4
- **Primary category: C** (secondary: B, weakly). **Hard to classify — see
  [category-summary.md](category-summary.md) §4.**
- Category justification: several vehicles want the same intersection, and a **priority order taken
  from right-of-way rules** fixes who decides first; a separate rule fires when all have stopped
  (§II-C, §III-E, §IV-A). Contention exists and a rule arbitrates — C. There is no vehicle-to-
  vehicle messaging; the paper dismisses such approaches as "not scalable to general intersection
  handling" (§I). The weak B element: "every vehicle knows which way every other vehicle is
  intending to use, as every vehicle declares its intention using their turn signal" (§II-A) — a
  one-way declared intention, which the issue's boundary rule would count as a channel.
- Domain simulated: autonomous vehicles at a four-way unsignalised intersection, driving on the
  left, at most four vehicles, one per approach. [§II-A]
- The rule, stated precisely:
  - **The priority order.** A vehicle about to enter must give way, "in order of importance", to
    any vehicle **(A) already engaged in the intersection, (B) on its left-hand side, (C)
    significantly closer to the intersection** (§II-C). As implemented (§IV-A.1): if *j* is inside
    and *k* is not, *j* precedes *k*; else, if there are fewer than four vehicles and *j* is on
    *k*'s left, *j* precedes *k*; else, if *j* is closer to the centre by **more than 2 metres**,
    *j* precedes *k*. The vehicle picks at random a total order consistent with these.
  - **The decision.** Given the order, vehicles choose acceleration patterns as a one-round
    sequential game of perfect information, solved by backward induction in priority order (§III-A,
    §III-C). Each vehicle's cost is a safety term that grows as others come within 25 m, plus a
    speed term (§III-B). The top-priority vehicle's safety cost is waived except in real danger —
    "in order to break symmetric situations where all vehicles would be too conservative"
    (§III-B.2).
  - **Updating.** A rule-following vehicle recomputes the order whenever the right-of-way facts
    change, and, if others do not behave as predicted, re-fits the order to what it observes
    (§IV-B).
  - **The deadlock rule.** If all vehicles are stationary and all were correctly predicted, a
    vehicle that believes it has top priority — or that saw the deadlock on the previous step —
    sets its acceleration to 10 m/s² **with probability 0.25** (§III-E).
- Trigger condition: continuously, every 0.1 s, for vehicles approaching or inside the intersection
  (§V-A); the deadlock rule once contention has produced a standstill (§III-E).
- Information required: "the precise configuration" of every vehicle — position, speed,
  acceleration, and whether it is entering, inside or leaving (§III-D; Eq. 1) — and each vehicle's
  intended route, from its turn signal (§II-A). No messages.
- Tie-breaking: **the most explicit in the review, and the only one taken from outside the
  authors' own design.**
  - First by presence (already in the intersection), then by side (the vehicle on the left), then
    by distance (closer by more than 2 m) (§II-C, §IV-A.1).
  - The source of the rule is traffic law: "we use Japanese rules for deciding priorities of
    vehicles" (§II-C, citing a National Police Agency guide for foreign drivers).
  - **The rule is acknowledged to be country-specific:** "Rules are slightly different in other
    countries, especially on the side that have more priority (e.g., left in Japan, right in
    Australia)" (§II-C).
  - **Four vehicles, one on each approach, defeat it** — each has another on its left — which is
    why the left-hand rule is applied only when "the number of vehicles is less than 4" (§IV-A.1).
    What remains is a random choice of order, and, at a standstill, the probabilistic rule above.
  - The paper gives a reason randomness is unavoidable: "it is impossible to avoid such a
    situation using only deterministic choices, and a solution is to introduce some randomness"
    (§III-E, citing Lehmann and Rabin's 1981 result on the dining philosophers).
- Guarantees claimed: none. Robustness is argued from simulation.
- Evaluation: Matlab; four vehicles; 2,000 simulations, 1,000 from rest and 1,000 with random
  initial speeds; four mixes — all rule-following ("angelic"); three rule-following and one that
  always claims priority ("demonic"); four that initially claim priority but adapt
  ("intermediate"); three intermediate and one choosing accelerations at random ("irrational")
  (§V-B). Metrics: collision rate, a "congestion" rate (two vehicles with crossing paths inside at
  once), and total time.
- Does it work: with rule-followers and with selfish vehicles, yes; not with a random one.
  - "For cases 1, 2, and 3, all vehicles successfully leave the intersection without any
    collisions. Some collisions are detected for the case 4, due to the unpredictable behaviour of
    the irrational vehicle" (§V-B).
  - **A selfish vehicle makes the intersection faster.** Average total time from rest: 56.87 steps
    with four rule-followers, **53.98 with one selfish vehicle among them** (Table I). The authors'
    reading: "the selfish vehicle makes the decision making easier: it will force itself through
    the intersection, so that angelic vehicles have no choice but to let it go first" (§V-B).
  - With a random vehicle, time rises to 91.88 steps (Table I).
  - With non-zero initial speeds there are "more congestions" because vehicles "have less time to
    make their decision" (§V-B).
- Validated against real human or real traffic data: no. The rule comes from a driving guide, not
  from observed drivers. The paper notes that human-behaviour-based approaches exist (§I, its
  refs. [4]–[6]) and does not use one.
- Scalability: **four vehicles**, by assumption (§II-A). Computing the order-refit means solving
  the game "for any total order" (§IV-B.2), which is factorial in the number of vehicles —
  `[inference]`; the paper does not discuss cost.
- Domain assumptions that limit portability: one vehicle per approach; fixed paths, control of
  acceleration only; perfect observation; a finite set of four acceleration patterns (§V-A).
- Portability to a generic simulator: [inference] **the priority order ports as a pattern; its
  content does not, and that is the useful lesson.** *Yield to whoever is already in the contested
  space, then to whoever is on a designated side, then to whoever is clearly nearer* is three
  tests on observable geometry — a category C rule needing no messages. But the designated side is
  a legal convention that differs between countries, and for pedestrians there is no statute to
  read it from. The rule's shape is reusable; its middle term has to be supplied per population.
- Limitations and future work stated by the authors: "systematic experiments based on more
  sophisticated and practical traffic simulators", and "more detailed techniques … to eliminate the
  potential hazards" (§VI).
- Relevance to this FYP: [inference] **the most directly relevant single paper in S4.** It is an
  explicit, communication-free precedence rule for a symmetric conflict; it handles agents who
  break the rule; it shows that the rule's content is a *local social convention* rather than a
  universal; and it documents exactly where such a rule runs out (four-way symmetry) and what is
  then done (a coin flip). The FYP's Singapore-specific scope is the pedestrian analogue of
  "left in Japan, right in Australia".
- BibTeX: `pruekprasert2019rightofway`

---

### [Mariani-CoordSurvey]: Coordination of Autonomous Vehicles: Taxonomy and Survey

- Authors / Year / Venue: Stefano Mariani, Giacomo Cabri, Franco Zambonelli / 2021 / *ACM Computing
  Surveys* 54(1), article 19.
- Link: https://doi.org/10.1145/3431231 | https://arxiv.org/abs/2001.02443
- Peer-review status: published at ACM Computing Surveys (the arXiv record carries the journal
  reference and DOI).
- Verified: **partly.** Read: Abstract, §3.1, §3.2 (all four subsections), §3.8. Not read: §2
  (problem taxonomy), §3.3–§3.7 (parking, ride sharing, ramp merging, platooning, traffic flow),
  §4 (challenges). **Read from** `refs/sr_coordtaxonomy_2001_02443.txt` — arXiv v1 (8 Jan 2020),
  the *submitted* version ("submitted to ACM CSUR"); the published version may differ.
- Sub-area: S4
- **Primary category: uncategorised (survey).** Used as the 2016+ source covering pre-window
  intersection-management methods, and for its taxonomy, which lines up closely with the issue's
  three categories.
- Category justification: n/a. Its four classes, ordered by the autonomy left to vehicles (§3.1,
  Fig. 1, Table 3), map as follows `[inference]`:

  | Survey class | Definition (§3.1) | Issue category |
  |---|---|---|
  | Centralised | one coordinator decides; vehicles "must abide by design" | C (a rule or authority arbitrates) |
  | Negotiation | vehicles "propose" within a fixed protocol — auctions, Contract Net | B |
  | Agreement | vehicles define the protocol itself — argumentation, DCOP | B |
  | Emergent | no protocol; each acts on "the perceptions it collects about other participants" | A |

- Domain simulated: n/a.
- The rule, stated precisely: none of its own. What it supplies for intersections (§3.2):
  - **Reservation** (Dresner and Stone, the survey's ref. [35] — pre-window): "incoming vehicles
    request assignment of a time slot for crossing to the intersection manager, who computes
    decisions based on a local control policy" (§3.2.1).
  - **Leader election without infrastructure**: a transient leader "elected by considering factors
    such as the distance to the intersection, the traveling speed" acts as intersection manager
    (§3.2.1) — the same device as [Shah-AROW]'s arbitrator.
  - **Auction**: vehicles bid for the cells they need; among vehicles on colliding trajectories the
    highest bidder gets right-of-way (§3.2.2).
  - **Argumentation**: the authors' own proposal, in which vehicles "engage in open dialogues while
    approaching the intersection … arguing with each other about possible ways to avoid that
    conflict" — described as "still at the conceptual level" (§3.2.3).
  - **Emergent**: each vehicle "responds in a reactive way to the actions of the other agents"
    (§3.2.4).
- Trigger condition / Information required / Tie-breaking: n/a (survey). It does not tabulate
  tie-breaking for the methods it surveys: `[not stated]` in the sections read.
- Guarantees claimed (the survey's own summary judgements, §3.8):
  - Centralised approaches "offer the best guarantees in terms of safety and liveness".
  - Negotiation risks "losing fair treatment … to the point of failing in liveness (e.g., inducing
    starvation of vehicles)"; and for auctions, bidding strategy "can sometimes prevent others to
    win auctions, with the risk for them to experience indefinitely long waiting times" (§3.2.2).
  - Agreement approaches are "definitely the less explored ones".
  - Emergent approaches "appear not suitable for those coordination problems where there is the
    need of guaranteeing accurate and predictable behaviour at the level of individual vehicles,
    such as in crossing intersections or in ramp merging".
- Evaluation: none of its own. It states that "there is need of systematic, comparative, and
  quantitative analysis … of the different coordination approaches" (§3.8).
- Does it work: n/a. One empirical remark, quoted with its source status: emergent crossing is
  "already at work in the real world" at unsignalled intersections in "many over-congested African
  and Asian cities", where "crashes are frequent, and so it is impossible to predict the
  time-to-cross" (§3.2.4). ⚠ That is the survey authors' characterisation; **no data source is
  cited for it** in the passage.
- Validated against real human or real traffic data: n/a.
- Scalability: n/a. It says centralised approaches "may fall short" at urban scale (§3.8).
- Domain assumptions that limit portability: the surveyed methods assume connected, automated
  vehicles.
- Portability to a generic simulator: [inference] the taxonomy itself is the portable thing. Its
  ordering axis — how much freedom the agent keeps — is domain-free, and the survey closes by
  pointing to "concurrency control, distributed systems, social systems, and multi-agent systems"
  as holding ready solutions (§3.8).
- Limitations and future work stated by the authors: the call for comparative quantitative
  analysis (§3.8). §4 was not read.
- Relevance to this FYP: [inference] two things. (1) Its verdict on emergent (category A)
  approaches at intersections is a sourced counter-weight to the supervisor's hypothesis: a
  communication-free rule is judged adequate for flow-level problems and *not* for
  individual-level conflicts where a guarantee is needed. The FYP's corridor and doorway cases are
  individual-level conflicts. (2) The argumentation approach (§3.2.3) is, in effect, the FYP's
  original dialogue-based design, proposed for vehicles and acknowledged to be conceptual only.
- BibTeX: `mariani2021coordsurvey`
