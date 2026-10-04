# Research gap — derived from the collected entries

> **Draft pending supervisor review.** For issue
> [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). Every claim below cites the
> entries that support it. Entry handles in square brackets resolve to
> [S1](s1-crowd-simulation.md), [S2](s2-games.md), [S3](s3-mapf-robotics.md) or
> [S4](s4-traffic-vehicles.md); rule numbers SR1–SR35 resolve to
> [rule-catalogue-simulation.md](rule-catalogue-simulation.md).

Companion files: [category summary](category-summary.md) · [missing papers](missing-papers.md) ·
[search log](search-log.md)

## §0. The evidence base, and what it can and cannot carry

- **27 sources**: 20 peer-reviewed, 3 preprints, 4 industry. Two are surveys, leaving **25 sources
  that each describe at least one rule**, and **35 catalogued rules**.
- This is **not a systematic review**. Twelve sources were the issue's seeds; most of the rest are
  ones I already knew of or reached from the seeds, each confirmed at source; two came from a web
  search run late in the work ([search-log.md](search-log.md) §2–§6).
- **Those two late additions changed this file.** Before them, the draft said no source arbitrated
  between continuous-space agents and no traffic source was primarily a rule-based arbitration.
  Both statements were false. That is direct evidence of how sensitive the conclusions below are
  to what happened to be read.
- Five papers could not be obtained, including both surveys of the pedestrian sub-area
  ([missing-papers.md](missing-papers.md)).
- So every count below is a count **of what was read**, and every "none" means "none among these
  27". Where a claim would not survive a counter-example, I say what the counter-example would be.
- "`[inference]`" marks my reading. Unmarked statements are the cited source's.

**Short version.** The evidence supports a gap, but a narrow one. The field has working machinery
for *applying* a precedence order between conflicting agents (§4). What it lacks is a good
*source* for that order. Wherever the order is stated, it is a random draw, an arbitrary
identifier, or arrival order — and described as arbitrary by its own authors — with one exception,
which takes it from a country's traffic law and notes that the law differs between countries (§5).
Behind that: the rules are hand-written (§1), almost none is checked against how people behave
(§2), and none is shown working on two kinds of agent (§3). The evidence does **not** show that a
communication-free rule is sufficient, and says nothing about whether an LLM could supply a better
order (§6).

---

## §1. Where do the rules come from?

Classifying each of the 25 rule-bearing sources by how its rule was arrived at:

| Origin | Count | Sources |
|---|---|---|
| **Hand-designed** by researchers or engineers | **19** | S1: [Charlton-FastCrowd], [Sung-ArrivalTime], [Sudkhot-BDI-RVO], [MartinezBaselga-AVOCADO], [Tordeux-CFSM]. S2: [SunshineHill-RVO-ORCA], [Martel-ACSyndicate], [Jenner-DriverSF], [Epic-UnrealAvoidance]. S3: [Okumura-PIBT], [Chakravarty-PIBT-FreeSpace], [Zhou-LSRP], [Ma-TokenPassing], [Grover-Deadlock], [Dergachev-ORCA-MAPF]. S4: [ShalevShwartz-RSS], [Malikopoulos-SignalFree], [Shah-AROW], [Ahmed-MergeAssist] |
| **Learned** by reinforcement learning, from simulated instances | **2** | [Yang-S2AN] (the planning order), [Ma-DCC] (the movement policy) |
| **Found by search or optimisation** at run time | **2** | [Zhang-Mutex], [Xu-TreeSearch] |
| **Hand-designed form, parameters calibrated to human data** | **1** | [Xu-AVM] |
| **Precedence order taken from codified law**, inside a hand-designed decision procedure | **1** | [Pruekprasert-RightOfWay] |
| **Derived from observed or elicited human decisions** | **0** | — |

Notes that qualify the table rather than change it:

- "Hand-designed" covers a range. [Grover-Deadlock]'s rule is designed *from* a mathematical
  analysis of when deadlock occurs (§5–§6). [Malikopoulos-SignalFree] derives the control law by
  optimal control but simply *adopts* first-in-first-out for the order (§2). [ShalevShwartz-RSS]
  calls its rules a formalisation of five "common sense" rules (§3) — the authors' common sense,
  not measured behaviour.
- **The one rule with an outside source takes it from statute, not from behaviour.**
  [Pruekprasert-RightOfWay] uses "Japanese rules for deciding priorities of vehicles" (§II-C),
  cited to a police driving guide. A traffic code is a record of an agreed human convention, which
  makes this the closest thing in the review to a socially grounded rule. It is still not evidence
  of what drivers do.
- Both learned methods learn from **simulation reward, not from human data** ([Yang-S2AN] §4.1,
  §4.4; [Ma-DCC] §IV-B), and both still depend on hand-designed parts: [Yang-S2AN] on two
  engineered features (§4.2), [Ma-DCC] on a hand-written communication trigger (§IV-A).
- Human behaviour is *invoked* as a design guide in three hand-designed sources and measured in
  none of them: "mimicking what humans would do gives the best results" ([Martel-ACSyndicate]
  §15.5.2); agents with an energy-style utility "exhibit human-like trajectories"
  ([SunshineHill-RVO-ORCA] §19.8.2); the default all-way stop "is similar to the real-life human
  behavior" ([Shah-AROW] §VI-B.3).

**Supported claim:** among the sources read, conflict rules are overwhelmingly written by hand (19
of 25), and **no rule's logic was obtained from human decisions**. The nearest are [Xu-AVM], where
people's behaviour sets the *parameters* of a hand-written rule, and [Pruekprasert-RightOfWay],
where a legal code sets the *order*.

**What would overturn it:** an in-window paper that extracts an avoidance or yielding rule from
trajectory data or from human judgements. I did not search for data-driven crowd models
specifically. [Sudkhot-BDI-RVO] §2.1 mentions an "example-based method" that "relies heavily on
the data captured from the real world" (its ref. [27]), and [Pruekprasert-RightOfWay] §I cites
"human-like decision-making" for intersections built on "human drivers' data" (its refs. [4]–[6]).
I opened none of these. **This is a real hole in the search, not a finding of absence.**

---

## §2. How many are validated against real human or traffic behaviour?

| Level of contact with real behaviour | Count (of 25) | Sources |
|---|---|---|
| **Validated**: model output compared quantitatively with recorded human data | **1** | [Xu-AVM] — fundamental diagram and lane-formation time course against laboratory experiments (§5, §4.4) |
| **Tested with real people present**, no comparison against recorded behaviour | **2** | [MartinezBaselga-AVOCADO] — 19 pedestrians sharing an arena with robots (§VI); [Ahmed-MergeAssist] — three drivers on a real freeway (Experimental Results) |
| **Tested on physical robots** (no humans) | **2 more** | [Okumura-PIBT] §5.4; [Grover-Deadlock] §6 |
| **Simulation metrics only** | **15** | [Charlton-FastCrowd], [Sung-ArrivalTime], [Sudkhot-BDI-RVO], [Tordeux-CFSM], [Chakravarty-PIBT-FreeSpace], [Zhou-LSRP], [Yang-S2AN], [Zhang-Mutex], [Ma-TokenPassing], [Ma-DCC], [Dergachev-ORCA-MAPF], [Malikopoulos-SignalFree], [Xu-TreeSearch], [Shah-AROW], [Pruekprasert-RightOfWay] |
| **No evaluation at all** | **5** | [ShalevShwartz-RSS] (proofs only); all four S2 industry sources |

The rows sum to 1 + 2 + 2 + 15 + 5 = 25. [MartinezBaselga-AVOCADO] is counted once, in the second
row, although it also used physical robots.

**Supported claim:** **1 of 25** rule-bearing sources validates its rule against real human
behaviour. Even that one hedges: calibration "was performed manually" and "the comparability of
experiments and simulations is limited" ([Xu-AVM] §5, §4.4).

Two further points from the entries:

- **Realism is often judged by eye.** "Various expected behaviors such as lane formation can be
  observed" ([Charlton-FastCrowd] §4); phenomena are "reproduced" ([Tordeux-CFSM] §4); there is
  "no substitute for subjective evaluation" ([SunshineHill-RVO-ORCA] §19.9).
- **One source argues validation against data is the wrong goal.** [ShalevShwartz-RSS] (§1) holds
  that statistical validation of safety is infeasible and substitutes proof. That is a position on
  safety, not on behavioural realism, but it means the absence of validation is partly a choice.

**What would overturn it:** the pedestrian-dynamics literature has an established practice of
validating against controlled experiments — [Xu-AVM] itself cites a body of it (§1). My S1 sample
is drawn mostly from computer graphics and robotics, where that practice is rarer. A sample drawn
from *Transportation Research* or *Physica A* would likely show a much higher validated share.
**So "1 of 25" describes this sample. It should not be quoted as a property of crowd simulation
research.**

---

## §3. How many are portable across agent types?

Two different things, kept apart.

**(a) What the papers demonstrate.** **No source evaluates one rule with two different kinds of
agent following it.** The nearest cases:

- [MartinezBaselga-AVOCADO] runs its rule on robots among humans (§VI) — but only the robots follow
  the rule.
- [Martel-ACSyndicate] has pedestrians and vehicles in one scene — but documents only the
  pedestrians' rule (§15.2).
- [ShalevShwartz-RSS] extends its vehicle rule to pedestrians in prose (§3.8) — untested.
- [Okumura-PIBT] claims applicability to "several domains" (Abstract), and [Dergachev-ORCA-MAPF]
  names "mobile robotics, video games, crowd simulation" (§I) — each tests on one kind of agent.

**(b) What recurs across papers.** Two rule families appear in more than one domain, reported by
independent sources:

- **The velocity-obstacle family** appears for pedestrians ([Charlton-FastCrowd],
  [Sung-ArrivalTime], [Sudkhot-BDI-RVO]), for game characters ([SunshineHill-RVO-ORCA],
  [Epic-UnrealAvoidance]) and for robots ([MartinezBaselga-AVOCADO], [Dergachev-ORCA-MAPF]).
  [SunshineHill-RVO-ORCA] §19.2 itself tells the transfer story: designed for physical robots,
  adopted by games.
- **First-come-first-served** appears for vehicles ([Malikopoulos-SignalFree], [Xu-TreeSearch],
  [Shah-AROW]) and, as a named fixed-priority scheme, in grid path finding ([Wang-MAPFSurvey]
  §3.4).

**(c) My own assessment**, from the catalogue's Portable column — `[inference]` throughout: of 35
rules, I judge 3 not portable (SR21, SR22, SR30 — a trained network and two centralised
optimisers), 1 not assessable (SR17), 2 portable only where an alternative route exists (SR4,
SR5), and the remaining 29 portable at least conditionally.

**Supported claim:** portability is **claimed or implied far more often than it is shown**. The
strongest evidence that a conflict rule can cross domains is historical — one avoidance family
(velocity obstacles) did. For *arbitration* rules there is no demonstrated cross-domain transfer in
what I read; there is only the recurrence of first-come-first-served.

**One source says outright that a rule's content does not travel.** The right-of-way order differs
by country — "left in Japan, right in Australia" ([Pruekprasert-RightOfWay] §II-C). `[inference]`
That separates two things usually run together under "portability": the *form* of a precedence
rule (tests on who is already there, on which side, how near) may carry across agent types, while
its *content* is a local convention. For a Singapore-specific dataset that is a point in favour of
eliciting the content per population rather than importing it.

**What the entries say limits portability**, in the authors' own words or assumptions:

- *Space:* a discrete graph ([Okumura-PIBT] §3.1; [Zhou-LSRP] §2; [Ma-TokenPassing] §3.1) versus
  continuous space (all of S1). [Dergachev-ORCA-MAPF] bridges the two by overlaying a grid on the
  stalled agents only (§IV-B).
- *Time:* lock-step updates — "a significant gap in practical situations" ([Okumura-PIBT] §6),
  addressed by [Zhou-LSRP].
- *Homogeneity:* "heterogeneity is not supported in PIBT" ([Chakravarty-PIBT-FreeSpace] §6).
- *Infrastructure:* lanes, control zones, stop lines, a priority relation between routes (all of
  S4); parking endpoints ([Ma-TokenPassing] Definition 1).
- *Topology:* the best guarantee in S3 needs a cycle through every pair of adjacent vertices
  ([Okumura-PIBT] Theorem 1) — which a corridor or doorway does not have.
- *Numbers:* the most explicit precedence rule is defined for at most four vehicles and is switched
  off, in part, when all four approaches are occupied ([Pruekprasert-RightOfWay] §II-A, §IV-A.1).

---

## §4. How are the three categories distributed?

Counts and the full discussion are in [category-summary.md](category-summary.md). The facts used
here:

- By entry: A 11, B 7, C 7, uncategorised 2. On peer-reviewed entries only: A 6, B 6, C 7.
- **By sub-area the split is near-total:** S1 and S2 are 10 of 10 A; S3 has no primary A; S4 has
  one primary C in seven.

**Supported claim, part 1 — the avoidance-only sub-areas need an arbitration layer and say so.**
Rules for pedestrians and game characters are avoidance rules, and their own results report the
failure an arbitration rule exists to prevent:

- Reciprocal avoidance in a symmetric meeting of four or five agents takes 40 to 100 times longer
  than with a detour heuristic — "momentarily deadlocked" ([Sudkhot-BDI-RVO] §5.1, Table 2).
- "ORCA experiences deadlocks from geometrical symmetries, so it fails in all cooperative circle
  scenarios" ([MartinezBaselga-AVOCADO] §V-B).
- ORCA agents at corners "simply become stuck", leading "to frequent deadlocks"
  ([SunshineHill-RVO-ORCA] §19.6).
- Under the collision-free speed model, two agents head-on "are unable to pass each other"
  ([Xu-AVM] §3, of the model in [Tordeux-CFSM]).
- Densely packed agents "get stuck and barely move" ([Sung-ArrivalTime] §5).
- With 40 agents and three narrow passages, ORCA with path planning "was not able to solve a single
  instance" ([Dergachev-ORCA-MAPF] §V).
- And one source proves it is not an implementation accident: symmetric initial conditions
  necessarily deadlock under reactive avoidance, and differing controller gains do not prevent it
  ([Grover-Deadlock] Theorem 1; §1).

Six independent sources report stalls, and a seventh explains why.

**Supported claim, part 2 — the arbitration layer exists, and has been attached to this kind of
agent once.** [Dergachev-ORCA-MAPF] takes continuous-space agents using the same avoidance rule,
detects a stall, and arbitrates locally; with 40 agents and three narrow passages, success goes
from no instance solved to 99% (§V).
So the *mechanism* the FYP needs is not missing from the literature. Arbitration mechanisms also
exist for grid agents (SR18–SR22) and for vehicles (SR28, SR29, SR31, SR34).

`[inference]` **So the gap is not "pedestrian simulators lack conflict resolution".** One in-window
source read provides it for the same class of agent, and others provide it for neighbouring
classes. The gap is in what that mechanism is given to work with — §5.

**Caveats:**

1. **Pre-window pedestrian models already had arbitration rules.** Issue #20 catalogued a 2014 rule
   that arbitrates cell contention (rule R9, Bouzat & Kuperman, in
   [`../game-theory/candidate-rule-catalogue.md`](../game-theory/candidate-rule-catalogue.md)).
   [Xu-AVM] §1 mentions lattice models with a keep-right rule and with back-stepping (its refs.
   [20], [21]). A late search also surfaced a 2003 cellular-automaton "friction" rule for two
   pedestrians wanting the same cell (Kirchner, Nishinari and Schadschneider, *Physical Review E*
   67, 056122 — record confirmed in Crossref; **not read**, so no description is given).
   Cellular-automaton pedestrian models are where conflict-resolution rules would be expected, and
   **I did not search for in-window ones.** That is a gap in this review.
2. **Two in-window S1/S2 fragments exist**: a stall-triggered re-plan (SR5) and an undocumented
   engine "priority system" (SR17).
3. **Part of the S3 side depends on a classification choice** ([category-summary.md](category-summary.md)
   §4, case 1).
4. **Both S1 surveys are unread** ([missing-papers.md](missing-papers.md) M1, M2).

---

## §5. The precedence order — the most reusable part, and the thinnest

The issue called tie-breaking "the part most reusable for this FYP". Across the 35 catalogued
rules, how a symmetric conflict is broken:

| How the tie is broken | Rules | Count |
|---|---|---|
| **Not stated** (or not legible in the source) | SR1, SR2, SR5, SR8, SR10, SR17, SR19, SR25 (direction of rotation), SR29 (simultaneous arrivals) | 9 |
| **Random draw** | SR3, SR4, SR7, SR9, SR20 ("such as using random numbers"), SR28, SR30, SR31 (turn order), SR33, SR34 (what the legal tests leave undecided), SR35 | 11 |
| **Arrival order** | SR3 (first user keeps the waypoint), SR23 (order of token hand-out), SR28, SR29, SR31, SR32 | 6 |
| **Geometry of the encounter** | SR11 (keep the passing side already implied), SR14 (least change of heading), SR27 (whoever is nearer the crossing), SR34 (already inside; on the left; nearer by 2 m) | 4 |
| **A fixed attribute of the agent or its place** | SR14 (agent type), SR16 (personality weights), SR27 (route priority), SR6 (a prior on the other's cooperativeness) | 4 |
| **An arbitrary identifier** | SR18 (a unique ε per agent), SR31 (lowest MAC address, for the arbitrator) | 2 |
| **Accumulated waiting** | SR18 (timesteps since last at goal) | 1 |
| **A learned function** | SR21 | 1 |
| **Not applicable** (the rule is not a tie-break and contains none) | SR12, SR13, SR15, SR22, SR24, SR26 | 6 |

Rows overlap — a rule with a primary and a fallback tie-break is counted in both — so the counts
sum to more than 35.

**Supported claims:**

1. **In 9 of the 29 rules where the question applies, the source does not say how a symmetric case
   is broken.** That includes the most widely adopted avoidance rule in the review, in every form
   in which it appears (SR1, SR10, and SR11 for the exactly head-on case).
2. **The most common *stated* tie-break is a random draw (11 rules), then arrival order (6).**
3. **Randomness is not just a default; one source argues it is necessary.** "it is impossible to
   avoid such a situation using only deterministic choices, and a solution is to introduce some
   randomness" ([Pruekprasert-RightOfWay] §III-E, citing a 1981 result on symmetric distributed
   systems). [Grover-Deadlock] (Theorem 1) proves the companion fact for continuous motion:
   symmetric set-ups deadlock under deterministic reactive control. `[inference]` Together these
   say a deterministic rule can resolve a conflict only by finding an **asymmetry** to key on. The
   question for any proposed rule is therefore: *which asymmetry?*
4. **Where authors comment on the asymmetry they chose, they call it arbitrary.** "Based on user
   preference, it can be changed" ([Shah-AROW] §IV, stage S31). Priorities "can be set in different
   ways (such as using random numbers)" ([Zhou-LSRP] §4.2). [Okumura-PIBT] requires only that the
   tie-breaker be "distinct for agents" (§4.2). [Xu-AVM] chooses the dodge side "randomly" (§2.1).
   [Dergachev-ORCA-MAPF] assigns priority "randomly" (§IV-B).
5. **One precedence order has a source outside its authors' own design — traffic law — and its
   authors note that it is country-specific** ([Pruekprasert-RightOfWay] §II-C). It is not checked
   against behaviour, it covers at most four vehicles, and it fails by its own account when all
   four approaches are occupied, where it falls back to a random order (§IV-A.1).
6. **No precedence order in any rule read is derived from, or checked against, how people resolve
   the same tie.** The four attribute-based ones are: a designer's choice with no data
   ([Martel-ACSyndicate], [Jenner-DriverSF] — weights "arrived at empirically", §17.6.6); a
   property of the road, not of the agents ([ShalevShwartz-RSS]); and a tunable prior whose default
   is neutral ([MartinezBaselga-AVOCADO] Table I).
7. **The one arbitration rule with cost data is the arrival-order rule, and it is poor under
   load**: delay rises from 1.3 s to 39.8 s as demand doubles, and for 20 vehicles it ranks
   4,563,421,793rd of about 10 billion possible orders ([Xu-TreeSearch] Table I, §IV-C). Its own
   users name it as the limitation ([Malikopoulos-SignalFree] §5).
8. **A mis-set attribute-based order is worse than a neutral one.** A robot with a wrong prior
   about the other's cooperativeness collides ([MartinezBaselga-AVOCADO] §V-A, Fig. 6), and a
   load-based priority starves the low-priority lane ([Shah-AROW] §VI-B.3, of its comparator).
9. **Rule-breakers do not necessarily make things worse.** With one vehicle that always claims
   priority among three rule-followers, an intersection cleared *faster* than with four
   rule-followers — 53.98 against 56.87 time steps — because "the selfish vehicle makes the
   decision making easier" ([Pruekprasert-RightOfWay] §V-B, Table I). `[inference]` An asymmetry
   that everyone can see resolves the conflict even when it is not a fair one. That is the same
   mechanism as claim 3, observed in a simulation.

`[inference]` Claims 3–9 together are the sharpest statement of the gap this review supports:
**the field has working machinery for applying a precedence order, a theoretical reason why some
asymmetry is needed, and almost nothing to say about which asymmetry people actually use.** For
vehicles there is at least a statute to copy. For pedestrians in a corridor or doorway there is
none. That is where an elicited, population-specific rule would attach — as the precedence order
inside an existing arbitration scheme (SR18, SR27, SR31, SR33, SR34), not as a new scheme.

---

## §6. What the evidence does *not* support

Stated because the issue asks that a gap not be manufactured.

- **It does not show that a communication-free rule is sufficient.** One survey concludes that
  emergent, no-communication approaches "appear not suitable for those coordination problems where
  there is the need of guaranteeing accurate and predictable behaviour at the level of individual
  vehicles, such as in crossing intersections" ([Mariani-CoordSurvey] §3.8), and the one source
  that arbitrates between continuous-space agents does so by having them exchange goals
  ([Dergachev-ORCA-MAPF] §I). Against that: a no-message precedence rule clears a four-way
  intersection without collisions even with a selfish vehicle present ([Pruekprasert-RightOfWay]
  §V-B); a no-communication rule is reported as much faster than a plan-sharing one and
  "comparable to or better" in solution quality ([Okumura-PIBT] §5.2.2, versus
  [Ma-TokenPassing]); and in a method built on communication, less communication did better
  ([Ma-DCC] §V-A). `[inference]` The evidence is mixed and domain-dependent. What it does support
  is narrower: in a *simulator*, the information the communication carries — who arrived when, who
  intends what — is already available, so the same rules run without messages
  ([category-summary.md](category-summary.md) §4, cases 5–7).
- **It does not show that learned rules beat hand-written ones.** The one direct comparison finds
  a learned order more successful in obstacle-dense instances and worse on speed, scale,
  information required and interpretability ([Yang-S2AN] §5.2–§5.3; S3 entry).
- **It says nothing about whether an LLM can supply a better order.** No source read uses a
  language model. The one seed that does was excluded as out of scope and not analysed
  ([S1](s1-crowd-simulation.md), "Seed excluded").
- **It does not show that any catalogued rule is unsuitable for 10,000 agents.** Two sources report
  that scale or beyond — 10,000 for an arbitration rule at about 10 ms per step, runtime only
  ([Okumura-PIBT] §5.3), and 5 × 10⁵ for an avoidance rule ([Charlton-FastCrowd] §4). Scale is not
  where the gap is. (The two most explicit precedence rules are, however, tested on very few
  agents: 4 in [Pruekprasert-RightOfWay], 16 in [Shah-AROW].)
- **It does not establish that personas matter to conflict outcomes.** One shipped system
  parameterises avoidance by per-agent traits ([Jenner-DriverSF] §17.2.2), one model finds that
  more varied walking speeds reduce jamming ([Xu-AVM] Appendix C), and one finds that a single
  assertive agent speeds an intersection up ([Pruekprasert-RightOfWay] §V-B). None tests whether
  *who the agents are* should change *who yields*. That question belongs to issues #16 and #18,
  not here.

---

## §7. The gap, in one paragraph, with its conditions

Among 27 sources on implemented conflict rules — 25 of them describing rules — the rules are
hand-written in 19 and learned from simulation in 2; none takes its logic from human decisions
(§1). One is validated against human data (§2). None is demonstrated on two kinds of agent (§3).
Pedestrian and game-character rules are avoidance rules; six sources report the stalls that an
arbitration rule would resolve, and one shows such a rule attached to the same kind of agent,
working (§4). Where arbitration rules exist, the precedence order they apply is random,
identifier-based, or first-come-first-served, and is called arbitrary by its own authors; the
single exception copies a national traffic code and remarks that other countries differ (§5).
`[inference]` **The gap is therefore not the absence of a conflict-resolution mechanism. It is the
absence of a behaviourally grounded source for the precedence order that those mechanisms need —
and, for pedestrians, the absence of any codified source at all.**

**This statement is conditional on:** a sample of 27 that is largely seed-led and not systematic,
and that has already shifted once under two late additions; five unobtained papers, two of them
the surveys most likely to contain counter-examples; no search of in-window cellular-automaton
pedestrian models, data-driven crowd models, or human-like driver models; pre-window
counter-examples already known (§4, caveat 1); and one classification choice that the supervisor
has not yet reviewed. Each is a way the statement could be wrong, and each is listed in
[search-log.md](search-log.md) §7.
