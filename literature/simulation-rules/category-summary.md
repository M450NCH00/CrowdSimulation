# Category summary — A / B / C across the four sub-areas

> **Draft pending supervisor review.** For issue
> [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). Counts are of the 27 sources with
> a template entry in [S1](s1-crowd-simulation.md), [S2](s2-games.md), [S3](s3-mapf-robotics.md)
> and [S4](s4-traffic-vehicles.md). `[NOT OBTAINED]` stubs and the excluded seed are not counted.

Companion files: [rule catalogue](rule-catalogue-simulation.md) · [research gap](research-gap.md) ·
[missing papers](missing-papers.md) · [search log](search-log.md)

## §1. The definitions applied (from the issue)

- **A — avoid conflict by following a rule.** The rule operates before any conflict state exists.
- **B — resolve conflict through communication.** Agents exchange messages, and the outcome
  depends on the content. Observing another agent's position, velocity or heading is **not**
  communication; B needs a channel carrying information not inferable from physical state.
- **C — resolve conflict by following a rule.** A conflict state already exists, and a rule decides
  the outcome without negotiation.
- **A versus C** turns on whether the conflict state is ever instantiated.

## §2. Counts

### By primary category and sub-area (27 entries)

| | S1 crowd | S2 games | S3 MAPF / robots | S4 traffic | **Total** |
|---|---|---|---|---|---|
| **A** | 6 | 4 | 0 | 1 | **11** |
| **B** | 0 | 0 | 3 | 4 | **7** |
| **C** | 0 | 0 | 6 | 1 | **7** |
| **uncategorised** | 0 | 0 | 1 | 1 | **2** |
| **Total** | 6 | 4 | 10 | 7 | **27** |

### The entries behind each cell

- **A (11):** S1 — [Charlton-FastCrowd], [Sung-ArrivalTime], [Sudkhot-BDI-RVO] (secondary C),
  [MartinezBaselga-AVOCADO], [Tordeux-CFSM], [Xu-AVM]. S2 — [SunshineHill-RVO-ORCA],
  [Martel-ACSyndicate], [Jenner-DriverSF], [Epic-UnrealAvoidance] (secondary C, undocumented).
  S4 — [ShalevShwartz-RSS] (secondary C).
- **B (7):** S3 — [Ma-TokenPassing] (secondary A), [Ma-DCC], [Dergachev-ORCA-MAPF] (secondary C
  and A). S4 — [Malikopoulos-SignalFree] (secondary C), [Xu-TreeSearch] (secondary C, for its
  baseline), [Shah-AROW] (secondary C), [Ahmed-MergeAssist].
- **C (7):** S3 — [Okumura-PIBT] (secondary B, in a variant discussed but not tested),
  [Chakravarty-PIBT-FreeSpace] (secondary A), [Zhou-LSRP], [Yang-S2AN] (secondary A),
  [Zhang-Mutex], [Grover-Deadlock] (secondary A). S4 — [Pruekprasert-RightOfWay] (secondary B,
  weakly).
- **Uncategorised (2):** [Wang-MAPFSurvey] and [Mariani-CoordSurvey]. Both are surveys spanning
  all three categories. Recorded as `uncategorised` with that explanation, as the issue directs,
  rather than forced into one.

### By peer-review status

| | Peer-reviewed | `[preprint]` | `[industry, not peer reviewed]` | Total |
|---|---|---|---|---|
| **A** | 6 | 1 ([ShalevShwartz-RSS]) | 4 (all of S2) | 11 |
| **B** | 6 | 1 ([Ahmed-MergeAssist]) | 0 | 7 |
| **C** | 7 | 0 | 0 | 7 |
| **uncategorised** | 1 | 1 ([Wang-MAPFSurvey]) | 0 | 2 |
| **Total** | **20** | **3** | **4** | 27 |

So on **peer-reviewed sources alone** the split is A 6, B 6, C 7 — close to even.

### By rule (the 35 rows of the catalogue)

A 18 · B 6 · C 11. A is larger at rule level because single S1 and S2 sources each state several
avoidance rules, while most S3 and S4 sources state one or two.

## §3. Imbalance — stated plainly

**No category is nearly empty overall. Every category is nearly empty somewhere.** The totals look
balanced; the table does not. Category is very largely determined by sub-area:

- **Pedestrians and games (S1, S2): 10 of 10 entries are A.** No entry is B. No entry is
  primarily C. In the two sub-areas closest to this FYP's domain, I found no in-window source
  whose main contribution is a rule for deciding who goes first once two agents are already
  contesting a space. Two entries have a C *component*: [Sudkhot-BDI-RVO]'s stall-triggered
  re-plan, and the undocumented "priority system" in [Epic-UnrealAvoidance].
- **Grid path finding and robots (S3): 0 of 10 entries are primarily A.** Everything is
  arbitration (C) or information-sharing (B).
- **Traffic (S4): 1 of 7 entries is primarily C** ([Pruekprasert-RightOfWay]). Arbitration rules
  are present in more — first-come-first-served is in three others — but there they are embedded
  in, or used as a baseline for, a communication-based method.

**The nearest thing to a counter-example sits just outside S1.** [Dergachev-ORCA-MAPF] takes
continuous-space agents steered by the same avoidance rule as the S1 pedestrian models and adds a
deadlock-resolution layer. I filed it under S3 because its test-bed is abstract disc agents on
maps of rooms and passages and its method is multi-agent path finding; its authors list "crowd
simulation" among the applications (§I). If it were filed under S1, that row would read A 6, B 1.
Either way it is the one source read that arbitrates between continuous-space agents.

**Two caveats on reading the pattern as a finding about the fields.**

1. *Some of it is definitional.* On a grid, "avoidance" and "arbitration" are hard to tell apart
   because agents never physically collide; I chose to call a planner-level contest for a vertex a
   conflict state (first hard case below). A different choice would move up to five S3 entries
   from C to A and largely dissolve the S3 column of the pattern.
2. *Some of it is sampling.* 27 sources is a small, largely seed-led sample, not a systematic
   review. The two S1 surveys that would test the claim were not obtained
   ([missing-papers.md](missing-papers.md) M1, M2). And outside the window the pattern is known to
   break: issue #20 already catalogued a 2014 **category C rule for pedestrians** (cell contention
   in a lattice-gas evacuation model; rule R9 in
   [`../game-theory/candidate-rule-catalogue.md`](../game-theory/candidate-rule-catalogue.md)).
   **The sample itself moved the pattern once already**: the two sources added by a late search
   are the only primary-C entry in S4 and the only arbitration of continuous-space agents
   ([search-log.md](search-log.md) §6). A fuller search would probably move it again.

**A finer imbalance inside B.** The issue hoped S4 would "supply genuine category B examples". It
supplies B examples by the issue's definition — the outcome depends on message content. But in
none of the seven B entries do agents *bargain*. In [Shah-AROW] the messages carry arrival times
and a rule turns them into an order; the others acknowledge. In [Malikopoulos-SignalFree] a relay
passes on a schedule fixed by first-in-first-out. In [Ma-TokenPassing] agents publish plans. In
[Dergachev-ORCA-MAPF] stalled agents share positions and goals and each then runs the same
deterministic solver. In [Ahmed-MergeAssist] a master vehicle circulates an order. **I read no
source, in any sub-area, in which the outcome of a conflict is settled by an exchange of proposals
and counter-proposals.** Auction and argumentation schemes exist — [Mariani-CoordSurvey]
§3.2.2–§3.2.3 describes them — but I know them only at second hand, and that survey calls the
argumentation approach "still at the conceptual level".

## §4. Papers that were hard to classify, and why

**1. The whole PIBT family — [Okumura-PIBT], [Chakravarty-PIBT-FreeSpace], [Zhou-LSRP]: A or C?**
Agents in these planners never collide, which suggests A ("collision-free by construction"). But
the mechanism is that two agents *request the same vertex* and a priority decides between them,
which is the issue's own description of C: "two or more agents contest the same cell". I took the
conflict state to be the contested request, not a physical collision, and classified them **C**.
Deciding locator: PIBT §4.1.1 and Algorithm 1 lines 12–16 (priority inheritance fires when the
wanted vertex is held). **This choice drives the S3 column and needs the supervisor's view.**

**2. [Yang-S2AN]: A or C?** In pure prioritised planning, later agents plan around earlier ones,
so no conflicting pair of plans is ever produced (A). This paper uses soft constraints, counts the
resulting collisions in its reward, and repairs them afterwards (§4.1 "Reward", §4.5). Contention
is instantiated, so **C**, with A secondary. The same method with hard constraints would be A.

**3. [Ma-TokenPassing]: B or A?** Given the token, each agent plans a collision-free path, so no
conflict arises (A). But the token is a channel carrying *intended plans* — the issue's own example
of what makes something B. **B**, with A secondary. Deciding locator: §4.1 ("a synchronized shared
block of memory that contains the current paths of all agents").

**4. [ShalevShwartz-RSS]: A or C?** The framework keeps vehicles a stopping distance apart so that
no collision can occur (A; Lemma 5). At junctions it also says who must brake and who may proceed,
by route priority (C; Definition 18). I took the collision as the conflict state and classified
**A**, with C secondary. If the conflict state is taken instead to be "both want the junction",
its junction rule is C.

**5. [Shah-AROW], [Malikopoulos-SignalFree] and [Dergachev-ORCA-MAPF]: B or C?** In all three, the
*principle* that settles the conflict is a fixed rule — earliest arrival first in the first two, a
deterministic solver with randomly drawn priorities in the third — which is C. But in each the
rule runs on information that has to be told: an assigned turn, a predecessor's schedule, the
other agents' goals. The issue's test for B is that "the outcome depends on the content of that
exchange". **B**, with C secondary, applied consistently to all three. `[inference]` For a
*simulator* this distinction collapses: the simulator already knows arrival order and goals, so the
same rules are C with no messages at all. This is recorded per rule in the catalogue's Portable
column (SR28, SR31, SR33).

**6. [Pruekprasert-RightOfWay]: C, despite turn signals.** Vehicles learn each other's intended
route from turn signals (§II-A). A declared intention is not physical state, so by the letter of
the boundary rule that is a B channel. I classified **C**: the signal is a one-way, standing
declaration; the conflict is settled by a priority order computed from positions (§IV-A.1); and
the paper itself rejects vehicle-to-vehicle communication (§I). **The issue's boundary rule does
not say how to treat conventional, non-negotiated signals** such as indicators — or, for
pedestrians, gaze and body orientation. Worth a decision.

**7. [Jenner-DriverSF]: A, although it reads other agents' plans.** Its planner scores candidate
paths against other vehicles' *predicted* paths, which each vehicle publishes (§17.2.1, §17.5). A
predicted path is not physical state, so by the letter of the boundary rule this is a B channel. I
classified **A**, because nothing passes between agents and no outcome hangs on a message: the
simulator exposes its own state to its own planner. **The issue's A/B boundary was written with
robots in mind and does not say how to treat a simulator that can see everything.** Worth a
decision, because the FYP's rule will run in a simulator.

**8. [Charlton-FastCrowd]: A, despite the word "messages".** The paper says agents communicate by
"messages" (§3, Fig. 2). These are the FLAME GPU framework's data structure for looking up
neighbours' radius, position and velocity — observation, not communication.

**9. [MartinezBaselga-AVOCADO]: not a boundary case.** The issue flagged it as a possible one. Its
"opinion" is a private estimate formed from observed motion; the paper states that the values are
*not* communicated (§IV-B) and that no communication infrastructure is needed (§III). It acts on
predicted collision, including its symmetry-breaker (§IV-D). **A**, unambiguously — and the most
direct support in this review for a rule that settles "who yields" with no channel at all.

**10. [Grover-Deadlock]: C, with an A phase.** Classified by the paper's own stated strategy:
"allow [deadlock] to occur and then correct it" (§7).

**Three of these ten cases (5, 6, 7) are the same underlying question** — what counts as
communication when the agents are in a simulator, or use conventional signals — and the issue's
boundary rules do not settle it. `[inference]` A workable refinement for this FYP would be to
split B into *"information is shared, then a rule decides"* and *"the agents bargain"*. On that
split, every B entry in this review is the first kind and none is the second.
