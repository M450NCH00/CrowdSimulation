# FYP meeting — findings on conflict rules in simulators, games, robots and traffic

Speaking notes for the meeting on Tuesday 6 October 2026, drawn from the eleven papers most
relevant to the FYP out of the 27 reviewed for issue #22. At most three were picked from each of
the four sub-areas. The first column gives each paper's handle, which is how it is named in the
review files under `literature/simulation-rules/`:

| Handle | Paper | Sub-area |
|---|---|---|
| Charlton | Charlton et al. (CGI 2019), *Fast Simulation of Crowd Collision Avoidance* | S1 crowd |
| AVM | Xu, Chraibi & Seyfried (Transp. Res. C 2021), *Anticipation in a velocity-based model for pedestrian dynamics* | S1 crowd |
| AVOCADO | Martinez-Baselga et al. (IEEE T-RO 2025), *AVOCADO: Adaptive Optimal Collision Avoidance driven by Opinion* | S1 crowd |
| GameAI-ORCA | Sunshine-Hill (Game AI Pro 3, 2017), *RVO and ORCA: How They Really Work* — **industry, not peer reviewed** | S2 games |
| DriverSF | Jenner & Ocio Barriales (Game AI Pro 3, 2017), *Fast Cars, Big City: The AI of Driver San Francisco* — **industry, not peer reviewed** | S2 games |
| PIBT | Okumura et al. (Artificial Intelligence 2022), *Priority Inheritance with Backtracking* | S3 robots |
| Grover | Grover, Liu & Sycara (IJRR), *The Before, During, and After of Multi-Robot Deadlock* | S3 robots |
| Dergachev | Dergachev & Yakovlev (IEEE CASE 2021), *Distributed Multi-agent Navigation Based on Reciprocal Collision Avoidance and Locally Confined Multi-agent Path Finding* | S3 robots |
| TreeSearch | Xu et al. (IEEE T-ITS 2020), *Cooperative Driving at Unsignalized Intersections Using Tree Search* | S4 traffic |
| AROW | Shah et al. (IEEE T-ITS 2024), *AROW: V2X-based Automated Right-of-Way Algorithm* | S4 traffic |
| RightOfWay | Pruekprasert et al. (IEEE ITSC 2019), *Decision Making for Autonomous Vehicles at Unsignalized Intersection in Presence of Malicious Vehicles* | S4 traffic |

Locators (§, table, figure) point into those papers; full detail is in the sub-area files
(`s1-crowd-simulation.md` to `s4-traffic-vehicles.md`). Anything marked *(my view)* is my own
interpretation, not a paper's claim.

**Three things to say up front about the evidence:**
- This is not a systematic review: 27 sources, seven web searches, no bibliographic database.
  Counts describe what I read, not the field.
- Nine of these eleven were read as arXiv copies of the published papers, so section numbers
  may differ slightly in the publisher's version. Grover, AROW and DriverSF were read
  selectively, not cover to cover.
- The two games sources are practitioner book chapters with no measurements. I found no
  peer-reviewed games paper.

---

## Part 1 — Avoidance rules scale well, and stall in exactly our scenarios

### 1.1 The standard avoidance rule (ORCA) in one sentence
- Each agent looks at its neighbours' positions and velocities and picks the velocity closest
  to the one it wants that will not cause a collision in the next few seconds, assuming each
  neighbour does half the dodging (Charlton, §3; GameAI-ORCA, §19.2.1, §19.5).
- No messages are exchanged. Agents only observe (GameAI-ORCA, §19.2).
- It is the default in games: velocity-obstacle methods "have in recent years become the
  standard for collision avoidance in video games" (GameAI-ORCA, §19.1).

### 1.2 Scale is not the problem
- The same rule on a graphics card ran up to **5 × 10⁵ agents at about 33 ms per frame**, up to
  30 times faster than a multi-core CPU (Charlton, §4).
- *Careful:* the paper's abstract says 100,000 people at 60 frames per second; its results
  section says 5 × 10⁵ at about 30. I report both.
- Realism was judged by eye: "Various expected behaviors such as lane formation can be
  observed" (Charlton, §4). No collision counts or flow statistics.
- *(my view)* The avoidance layer will not be what stops us reaching 10,000 agents.

### 1.3 But it stalls in symmetric conflicts — reported four times in these eleven papers
- **Corners and doorways in shipped games:** agents "simply become stuck", which "in general
  leads to frequent deadlocks" (GameAI-ORCA, §19.6).
- **Robots in a circle:** "ORCA experiences deadlocks from geometrical symmetries, so it fails
  in all cooperative circle scenarios" (AVOCADO, §V-B).
- **Two pedestrians head-on:** with the earlier collision-free model, "the two agents are
  unable to pass each other" (AVM, §3).
- **40 agents, three narrow passages:** ORCA with path planning "was not able to solve a single
  instance" (Dergachev, §V).
- When neighbours leave no safe velocity, the rule falls back to the least bad one and "there
  is no guarantee of collision-free motion" (Charlton, §3).

### 1.4 It is not a bug: symmetry forces a deadlock
- Grover proves that two robots approaching head-on under a purely reactive controller
  **necessarily** deadlock, and that giving them different controller gains does not prevent it
  (Grover, Theorem 1; §1).
- The number of possible deadlock arrangements grows fast: 1, 1, 4, 18 for one to four robots
  (Grover, §5).
- Their position: "a guaranteed way to resolve deadlock is to allow it to occur and then
  correct it using a reactive mechanism" (Grover, §7).
- *Careful:* their fix (rotate the robots around each other) is shown for two and three robots
  only, and I read this paper selectively.
- *(my view)* This is the theoretical justification for the FYP's whole topic: an avoidance
  rule answers "how do I move" and cannot answer "who goes first".

### 1.5 The one model validated against real pedestrians breaks ties with a coin flip
- AVM steers each pedestrian sideways away from where neighbours are *predicted* to be, and
  weights oncoming people twice as heavily as people walking the same way (AVM, §2.1).
- **It is the only paper of the 27 validated against human data:** the speed–density
  relationship and the timing of lane formation, against laboratory corridor experiments (AVM,
  §5; §4.4).
- When the other person is exactly straight ahead, the dodge direction "is chosen randomly"
  (AVM, §2.1).
- It still jams: at default settings, around 1.35 people per m² (AVM, §4.3).
- The authors name a human strategy their agents lack: agents "always jostle to move further
  and are apparently unaware of the strategy of simply standing still" (AVM, §5).
- **Caveats to raise myself:** calibration "was performed manually", and the authors say "the
  comparability of experiments and simulations is limited" (AVM, §5; §4.4).
- *(my view)* "Standing still and letting the other pass" is a yielding rule, which is what
  this FYP is trying to extract.

---

## Part 2 — Rules that decide who goes first already exist

### 2.1 PIBT: a priority rule that scales to 10,000
- On a grid, each step, agents are handled in priority order. Each takes the free neighbouring
  cell nearest its goal. If the cell is occupied, the occupant inherits the pusher's priority
  and must move first; if it cannot, the pusher tries another cell (PIBT, §4.1–§4.2,
  Algorithm 1).
- Priority is **how long the agent has been waiting since it last reached a goal**, plus a
  unique tie-breaker per agent that the paper only requires to be "distinct for agents"
  (PIBT, §4.2).
- **About 10 ms per step for 10,000 agents** on a laptop, runtime only (PIBT, §5.3).
- It needs no dialogue and no negotiation.
- **Limit that matters for us:** the guarantee that everyone reaches their goal needs a loop
  through every pair of neighbouring cells (PIBT, Theorem 1). A corridor or doorway has no
  loop, and the paper shows agents getting stuck there (PIBT, Fig. 5).
- It is a grid method, lock-step, with identical agents.

### 2.2 Dergachev: the same idea bolted onto pedestrian-style agents
- Agents move freely with ORCA. If an agent's average speed over 250 steps is near zero **and a
  neighbour reports the same**, it is treated as a deadlock (Dergachev, §IV-A; §V).
- The stalled agents then share positions and goals, lay a small grid over just that area,
  solve it with the same deterministic solver, follow the plan, and return to ORCA
  (Dergachev, §IV).
- **Result:** with 40 agents and three narrow passages, 99% of cases solved, against 0 for
  plain ORCA (Dergachev, §V). The headline is success going from 10–15% to 95–99% (§I).
- On an open map with no narrow passages the difference "is negligible" (Dergachev, §V).
- **Who gets precedence inside the local puzzle: "Each agent in the MAPF mode is randomly
  assigned a unique priority"** (Dergachev, §IV-B).
- Tested up to 40 agents only; no human data.
- *(my view)* This is the architecture closest to what the FYP needs: avoid by default, detect
  a stall, arbitrate locally, resume. In a simulator the message exchange is unnecessary,
  because the simulator already knows everyone's goals and speeds.
- *Note on how I found it:* this paper was not in my first pass. I had drafted the conclusion
  that nobody had added arbitration to continuous-space agents, ran a search to test that
  claim, and this paper overturned it.

### 2.3 What these three share
- Grover explains why arbitration is needed; PIBT shows it can be cheap at scale; Dergachev
  shows it can sit on top of an avoidance rule.
- In all three, **the order of precedence is arbitrary**: an identifier in PIBT, a random draw
  in Dergachev, and in Grover the direction of rotation is not stated in what I read.

---

## Part 3 — Where does the order come from? Traffic gives three answers

### 3.1 First come, first served — and what it costs
- Issue #20 (game theory) found no arrival-order rule anywhere. **It exists in traffic and is
  the standard baseline** at intersections without lights (TreeSearch, §I, §III-B).
- TreeSearch compared it against a computer-searched crossing order:
  - With 20 vehicles there are about 10 billion possible orders. The searched order ranked
    648th. **First come, first served ranked 4,563,421,793rd**, roughly the middle
    (TreeSearch, §IV-C).
  - Average delay under first come, first served rose from **1.3 s to 39.8 s** when demand went
    from 150 to 300 vehicles per lane per hour. The searched order stayed at about 1.1 s
    (TreeSearch, Table I).
- *Careful:* these numbers are from the arXiv preprint, simulation only, with all vehicles
  automated and sharing their intentions by radio.
- *(my view)* The intuitive "whoever arrived first passes first" rule is fair and simple and
  gets worse as the crowd gets denser. So the question for the FYP is not whether a simple rule
  exists but when a better one pays off.

### 3.2 AROW: arrival order with a referee, and a plan for rule-breakers
- At a four-way stop, vehicles arriving within about 2 seconds of each other pick one of
  themselves as arbitrator by a fixed rule, and it assigns crossing turns earliest-arrival
  first (AROW, §IV, heuristics H1 and H2).
- **Ties are broken at random, and the authors treat the choice as arbitrary:** "Based on user
  preference, it can be changed" (AROW, §IV, stage S31).
- **Rule-breakers:** if a vehicle crosses out of turn, the rest restart, at most twice, then
  fall back to plain first come, first served (AROW, §IV-F; §VI-A).
- With full compliance, ambiguous situations dropped to zero; with a quarter of vehicles not
  complying, 0.2% of cases against 4% for an ordinary all-way stop (four vehicles; AROW,
  §VI-B.3).
- It was **no faster** than an ordinary stop sign; the gain is removing hesitation
  (AROW, §VII).
- Tested with at most 16 vehicles, in simulation. I read this paper selectively.
- *(my view)* Strip out the radio messages, which a simulator does not need, and what is left
  is a complete rule: detect near-simultaneous arrival, order by arrival, break exact ties
  somehow, and have a fallback for those who ignore it. The "somehow" is the slot our
  LLM-derived rule would fill.

### 3.3 RightOfWay: the only rule taken from outside its authors' own design
- No radio messages. A vehicle gives way, in this order, to one that is **(A) already in the
  intersection, (B) on its left-hand side, (C) closer by more than 2 metres** (RightOfWay,
  §II-C; §IV-A.1).
- The source is Japanese traffic law, and the authors note it is country-specific: "left in
  Japan, right in Australia" (RightOfWay, §II-C).
- **Where it runs out:** with four vehicles, one on each approach, everyone has someone on
  their left. The side rule is switched off and the order becomes random (RightOfWay, §IV-A.1).
- If everyone is stopped, a vehicle moves with probability 0.25 per step. The paper's reason:
  "it is impossible to avoid such a situation using only deterministic choices, and a solution
  is to introduce some randomness" (RightOfWay, §III-E).
- **A result I did not expect:** with one vehicle that always claims priority among three
  rule-followers, the intersection cleared *faster* than with four rule-followers (53.98
  against 56.87 time steps), because "the selfish vehicle makes the decision making easier"
  (RightOfWay, §V-B, Table I). No collisions in either case.
- Four vehicles only; simulation only; the rule comes from a driving guide, not from observed
  drivers.
- *(my view)* This is the most relevant single paper for the FYP. It shows a "who yields" rule
  can work without communication, that its content is a local social convention, and exactly
  where it fails. **For pedestrians there is no traffic code to copy**, which is the opening
  for a Singapore-specific rule elicited from an LLM.

---

## Part 4 — Does who the agent is change the outcome?

### 4.1 A shipped game already uses per-agent traits
- In *Driver San Francisco*, each AI driver had personality traits such as "How strongly
  hitting other vehicles should be avoided" and "Likeliness to drive in the oncoming traffic",
  which "affected every stage of the path planning" (DriverSF, §17.2.2).
- The weights were "scaled by factors we arrived at empirically" (DriverSF, §17.6.6): tuned by
  hand, with no data.
- **Caveat:** industry source, no measurements, and I read it selectively.
- *(my view)* It is the closest precedent for our personas, and it is unvalidated. A
  population-grounded trait table is what we would add.

### 4.2 AVOCADO: "who yields, and by how much" as one number
- ORCA assumes each side does exactly half the dodging. AVOCADO replaces "half" with a number
  between 0 and 1 per neighbour and updates it by watching whether the neighbour actually
  swerves (AVOCADO, §IV-A, §IV-B).
- No communication: it uses "only relative position and velocity measurements from onboard
  sensors" (AVOCADO, §III).
- It can start with a prior belief about how cooperative the other is (AVOCADO, Table I).
- **A wrong prior causes collisions:** "Extreme bias values can lead to collisions" (AVOCADO,
  §V-A, Fig. 6).
- Tested with 19 real pedestrians sharing a space with three robots, but not compared against
  recorded human behaviour (AVOCADO, §VI).
- *(my view)* A persona could set that starting number. The warning is that it must then adapt,
  not stay fixed.

### 4.3 How large is the fleet, really?
- DriverSF reports "thousands of vehicles" at 60 frames per second (§17.7), but distant
  vehicles are "simply placed at the position defined by their path" with no physics
  (§17.2.1), and ordinary traffic runs on routes designed never to cross (§17.2).
- *(my view)* Two cheap tricks for the 10,000-agent goal that have nothing to do with a faster
  rule: keep routine agents on non-conflicting routes, and run the expensive rule only where it
  matters.

---

## Part 5 — Bigger-picture points

### 5.1 The gap, in one sentence
- The machinery for *applying* an order of precedence exists and scales. What is missing is a
  principled source for the order itself.
- Across the 35 rules I catalogued from all 27 sources: 11 break ties by a random draw, 6 by
  arrival order, 9 do not say, and the authors who comment call their choice arbitrary
  (`research-gap.md` §5).
- One rule takes its order from traffic law. None takes it from how people actually behave.
- *(my view)* So the FYP's contribution would be the precedence order, plugged into an existing
  arbitration scheme, not a new scheme.

### 5.2 How this connects to the game-theory review (issue #20)
- Issue #20 said the rule need not involve communication. These papers agree in practice: PIBT
  and RightOfWay work with none, and where messages are used (AROW, Dergachev) they carry facts
  a simulator already has.
- Issue #20 could not find an arrival-order rule. It is here, with numbers on its cost
  (TreeSearch).
- RightOfWay's "decide in priority order" is the same structure as issue #20's
  leader–follower rule.

### 5.3 Three results that cut against our assumptions
- First come, first served is poor under load (TreeSearch, Table I).
- A fixed prior about the other agent, if wrong, is worse than a neutral one (AVOCADO, §V-A).
- A rule-breaker can make things faster, not slower (RightOfWay, §V-B). *(my view)* So
  "everyone cooperates" may not be the right baseline for realism, which echoes the
  over-cooperation concern from GameChat.

### 5.4 Caveats to raise myself
- Small, seed-led sample; conclusions already changed once when I searched harder.
- **Only one of these eleven is validated against human data** (AVM).
- **None shows one rule working for two kinds of agent.**
- I did not search cellular-automaton pedestrian models, where older "two people want the same
  cell" rules exist, or data-driven crowd models.
- Five papers could not be obtained, including the two surveys of pedestrian models.

### 5.5 Decisions I need from the meeting
1. **Is the framing right?** The FYP supplies the precedence order for an existing arbitration
   mechanism, as opposed to inventing a mechanism.
2. **Which mechanism to build on?** Dergachev's detect-then-arbitrate layer over the current
   pedestrian model, or a PIBT-style priority rule.
3. **Is first come, first served the baseline to beat?**
4. **A classification question from the review:** I counted two agents requesting the same
   grid cell as a conflict, which puts PIBT under "resolve by rule" rather than "avoid by
   rule". Is that the reading you want?
5. **May I request the two missing surveys** through the library?
