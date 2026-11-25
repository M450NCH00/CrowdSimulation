# S2 — Video games and game AI

> **Draft pending supervisor review.** Prepared for issue
> [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). Read date for every entry:
> 2026-10-04.

Companion files: [S1](s1-crowd-simulation.md) · [S3](s3-mapf-robotics.md) · [S4](s4-traffic-vehicles.md) ·
[rule catalogue](rule-catalogue-simulation.md) · [category summary](category-summary.md) ·
[research gap](research-gap.md) · [pre-window foundations](pre-window-foundations.md) ·
[missing papers](missing-papers.md) · [search log](search-log.md) · [refs](refs-simulation-rules.bib)

## Read this first: what this sub-area does and does not contain

**Section 1 (peer-reviewed) is empty. Section 2 (industry) has four entries.** That is stated
plainly because the issue forbids counting industry sources toward any peer-reviewed minimum.

- The issue gave no seeds for S2 and warned that "academic coverage of game navigation is thin".
  That is what I found. No peer-reviewed, 2016-or-later paper describing a conflict rule *as
  shipped in a game* was obtained and read. The search is recorded in
  [search-log.md](search-log.md) §3.
- Peer-reviewed work that *mentions* games does exist elsewhere in this review, but only as a
  claimed application, never as an evaluation in a game: [Okumura-PIBT] lists games among MAPF
  applications (PIBT §1); [Ma-TokenPassing] lists "game characters in video games" (§1);
  [Yang-S2AN] motivates itself with "gaming scenarios" (§1); [Sung-ArrivalTime] is written for
  "video games and the film industry" (Abstract). None of them tests anything in a game.
- So everything below is **`[industry, not peer reviewed]`**: three chapters of *Game AI Pro 3*
  (an edited practitioner book) and one engine documentation page. They are valuable for exactly
  the reason the issue gives — they describe rules that shipped — and they are weak for exactly
  the reason it gives: none reports a measurement.

- Categories **A / B / C** are the issue's. `[inference]` marks my judgement.
- **Locators** are the chapters' own section and figure numbers. Book page numbers are from the
  Crossref records for *Game AI Pro 3* (A K Peters/CRC Press, 2017) and from the running page
  numbers in the PDFs.

---

## Section 1 — Peer-reviewed sources

*None obtained.* See above and [search-log.md](search-log.md) §3.

---

## Section 2 — Industry sources `[industry, not peer reviewed]`

### [SunshineHill-RVO-ORCA]: RVO and ORCA: How They Really Work

- Authors / Year / Venue: Ben Sunshine-Hill / 2017 / *Game AI Pro 3: Collected Wisdom of Game AI
  Professionals*, chapter 19, pp. 237–248, A K Peters/CRC Press (reprinted in *Game AI Pro 360*,
  2019).
- Link: https://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter19_RVO_and_ORCA_How_They_Really_Work.pdf
  | https://doi.org/10.4324/9781315151700-19
- Peer-review status: **[industry, not peer reviewed]** — a chapter in an edited practitioner
  book.
- Verified: yes (full text read). **Read from** `refs/sr_gameaipro3_ch19_rvo_orca.txt`.
- Sub-area: S2
- **Primary category: A.**
- Category justification: velocity-obstacle agents "do not explicitly communicate or coordinate
  with each other. Cooperation between them is an emergent effect of their observations, decisions,
  and actions over time" (§19.2), and they act on *projected* collisions every frame (§19.3). That
  is avoidance by observation, not arbitration and not communication.
- Domain simulated: game characters (NPCs). The chapter names no specific game. [§19.1]
- The rule, stated precisely: the chapter explains two pre-window rules (see
  [pre-window-foundations.md](pre-window-foundations.md)) and then, which is its real content,
  **how practitioners modify them**:
  - *RVO as explained here:* each agent "would move only halfway out of the way of a collision,
    anticipating that the other agent would do its part" (§19.2.1).
  - *ORCA as explained here:* "ORCA forces agents to maintain their current passing sides"; when a
    few neighbours rule out every velocity it "linearly relax[es] all constraints", giving the
    velocity "that maximizes the minimum passing distance" (§19.5).
  - *Modification 1 — weights.* The share each agent dodges need not sum to 1. Weights of 0.1
    settle slowly into a stable arrangement; weights of 0.9 oscillate; original VO is the special
    case of weight 1 (§19.7.1).
  - *Modification 2 — substepping.* Run several avoidance iterations per movement step, feeding
    each iteration's velocities into the next, starting with low weights and ramping up to 0.5
    (§19.7.2).
  - *Modification 3 — time horizons.* Ignore collisions projected after the agent would have
    stopped or turned a corner; for cornering, discard collisions beyond a "cornering plane"
    (§19.7.3, Fig. 19.6).
  - *Modification 4 — penalties instead of hard constraints.* Score each candidate velocity by
    distance from the preferred velocity plus penalties that grow as a projected collision gets
    nearer; optionally add a penalty for each neighbour whose passing side the candidate would
    change (§19.8, §19.8.1).
- Trigger condition: continuously, every frame (and several times per frame with substepping), on
  projected collision. [§19.3, §19.7.2]
- Information required: neighbours' positions and velocities; own preferred velocity. The chapter
  identifies a hidden assumption: each agent assumes "the current velocity of the other agent is
  also their preferred velocity" (§19.3), which path-following breaks at every corner (§19.6).
- Tie-breaking: **this chapter's main contribution to the review.** It names the quantity being
  decided — **sidedness**, i.e. which side two agents pass on — and gives three definitions:
  absolute (by the vector between centres at closest approach), relative to current relative
  velocity, and relative to desired velocity. The first two are always symmetric between the two
  agents; the third "can be inconsistent between A and B", so "'sidedness' as a tool for
  coordination generally uses one of the first two formulations" (§19.4). ORCA's tie-break is
  therefore: **keep whatever passing side the initial geometry already implies** (§19.5). For an
  exactly head-on pair, where the geometry implies none, the chapter gives no rule beyond an aside
  in an example that an agent "breaks ties by going west" (§19.3): `[not stated in chapter]` as a
  general rule.
- Guarantees claimed: the chapter is mostly about *the absence* of guarantees. "The proof of
  collision-free movement only holds for a world containing two agents (and no obstacles)" (§19.3).
  The penalty formulation "makes no guarantees of collision avoidance" (§19.8).
- Evaluation: **none.** The chapter argues from worked examples (Figs. 19.1–19.6). No numbers,
  agent counts, or comparisons. Its §19.9 advises readers to build their own scenario library and
  test rig, noting "It is difficult to formulate criteria to determine whether a particular
  algorithm 'passes' a particular test".
- Does it work: by the author's account, RVO works in practice for reasons other than its proof,
  and ORCA has a specific shipped-game failure. **Reported failures:** (i) three agents defeat the
  two-agent guarantee, producing several frames of velocity "flicker" before settling (§19.3);
  (ii) "ORCA's solver often does not succeed" because half-plane constraints from a few neighbours
  exclude everything (§19.5); (iii) **cornering** — ORCA agents at corners "simply become stuck …
  unwilling to cross paths and unable to make progress otherwise", which "in general leads to
  frequent deadlocks" (§19.6, Fig. 19.5); (iv) weights summing to less than 1 guarantee an eventual
  sharp veer and collision without substepping (§19.7.1). These are an experienced practitioner's
  assertions, not measured results.
- Validated against real human or real traffic data: no. One remark bears on realism: a
  rate-of-progress utility is "unrealistic … from the point of view of actual human behavior",
  whereas an energy-style utility (squared distance from preferred velocity) gives agents that
  "exhibit human-like trajectories, often slowing slightly to avoid a collision rather than turning
  left or right" (§19.8.2). No data is cited for either statement.
- Scalability: `[not stated in chapter]`.
- Domain assumptions that limit portability: the chapter is candid that the method's origin
  assumptions — decentralised, observation-only — "are not of much use to game developers" (§19.2),
  since a game knows every agent's state and can cheat (substepping uses exactly this).
- Portability to a generic simulator: [inference] high, and the chapter makes the point itself by
  tracing the rule from robots to games. The four modifications are simulator-side devices that
  need no change to the agent model. Substepping in particular is available to any simulator and
  to no real robot.
- Limitations and future work stated by the author: "there is no perfect collision avoidance
  system, only one that works well with your scenarios" (§19.9); predicting collisions in path
  space rather than world space is "as far as we know, intractable in the general case" (§19.7.3).
- Relevance to this FYP: [inference] **vocabulary and warning.** *Sidedness* is the right name for
  what a pedestrian tie-break decides, and *keep the passing side the geometry already implies* is
  a stateable rule the FYP could test an LLM's answers against. The corner deadlock is a shipped
  system's version of the FYP's doorway problem.
- BibTeX: `sunshinehill2017rvoorca`

---

### [Martel-ACSyndicate]: Steering against Complex Vehicles in Assassin's Creed Syndicate

- Authors / Year / Venue: Eric Martel / 2017 / *Game AI Pro 3*, chapter 15, pp. 191–202,
  A K Peters/CRC Press.
- Link: https://www.gameaipro.com/GameAIPro3/ (chapter 15 PDF) |
  https://doi.org/10.4324/9781315151700-15
- Peer-review status: **[industry, not peer reviewed]**.
- Verified: yes (full text read). **Read from** `refs/sr_gameaipro3_ch15_acsyndicate.txt`.
- Sub-area: S2
- **Primary category: A.**
- Category justification: pedestrians steer around a moving vehicle's hull before contact; "NPCs
  should reject a path request if it is physically impossible for them to pass" (§15.2.1). Nothing
  is arbitrated between the pedestrian and the vehicle — the pedestrian always gives way.
- Domain simulated: game characters (pedestrian NPCs) avoiding horse-drawn carriages, in a named
  shipped game. "the solution provided here was only for the navigation of humanoids. Steering
  behaviors for the vehicles themselves are handled differently and will not be described here"
  (§15.2). **So this is a mixed-agent-type scene of which only one side's rule is documented.**
- The rule, stated precisely: (1) represent the vehicle by 2-D oriented bounding boxes of its rigid
  parts, grown by half the character width (§15.3.1); (2) merge them into one contour and expand
  to a convex hull (§15.3.3–§15.3.4, Listings 15.2–15.3); (3) if the straight segment from the
  NPC to its destination intersects the hull, steer to the hull vertex that can be reached in a
  straight line without crossing the hull and that "minimize[s] the angle between our avoidance
  vector and our current intended heading" (§15.4.2, Fig. 15.10); (4) separate cases for a
  destination or a start point inside the hull (§15.4.3–§15.4.4).
- Trigger condition: on predicted collision — when a physics broad-phase box overlap reports a
  candidate and the segment test confirms an intersection. [§15.4.1–§15.4.2]
- Information required: the vehicle's part geometry and overall velocity; own position and
  destination. The velocity of sub-parts was deliberately not modelled (§15.5.2).
- Tie-breaking: which side to pass a vehicle on is decided by **minimum deviation from intended
  heading** (§15.4.2), with the note that "Depending on the relative velocities, you might want to
  control on which side the avoidance occurs". A human-derived heuristic is offered: "an agent
  crossing a moving vehicle will often try to go behind it", and the suggestion to vary the target
  vertex by whether the agent is moving with, against, or across the vehicle (§15.5.2). An exactly
  symmetric case: `[not stated in chapter]`.
- Guarantees claimed: if the segment does not intersect the expanded hull, "the NPC is free to go
  in straight line and will not collide with the obstacle" (§15.4.2). Nothing else.
- Evaluation: **none.** No numbers. The claim of success is "Converting obstacles' shapes to a
  convex hull really improved the quality of the navigation of our NPCs" (§15.6).
- Does it work: by the author's account, in the shipped game. **Stated gaps:** "the steering
  technique described here will not identify situations where vehicles will completely block a
  path" (§15.2.1); a multi-contour case was not implemented (§15.3.2); the region between contour
  and hull can be concave and "No trivial solution is available" (§15.4.3).
- Validated against real human or real traffic data: no. Human behaviour is invoked as a design
  heuristic — "mimicking what humans would do gives the best results" (§15.5.2) — without data.
- Scalability: `[not stated in chapter]`. A performance remark only: shapes are evaluated lazily
  and cached "for all surrounding characters" (§15.6).
- Domain assumptions that limit portability: 2-D (characters cannot fly, §15.3.1); the obstacle is
  a rigid body; **one-sided** — the other party does not avoid.
- Portability to a generic simulator: [inference] the geometric part ports to any simulator with
  non-circular agents. As a *conflict* rule it is the degenerate case: a fixed asymmetry by agent
  type (pedestrian yields to vehicle), decided at design time. That is a legitimate and very cheap
  rule, and it corresponds to issue #20's attribute-asymmetry rules (see the cross-reference in
  [rule-catalogue-simulation.md](rule-catalogue-simulation.md) §3).
- Limitations and future work stated by the author: triangulate the hull interior for local path
  planning; model sub-part velocities if needed. [§15.5]
- Relevance to this FYP: [inference] minor, but it is the only source in S2 documenting a
  pedestrian–vehicle rule in a shipped title, and its *go behind a crossing vehicle* heuristic is a
  concrete, testable claim about human behaviour that the LLM dataset could be checked against.
- BibTeX: `martel2017acsyndicate`

---

### [Jenner-DriverSF]: Fast Cars, Big City: The AI of Driver San Francisco

- Authors / Year / Venue: Chris Jenner, Sergio Ocio Barriales / 2017 / *Game AI Pro 3*, chapter 17,
  pp. 215–229, A K Peters/CRC Press.
- Link: https://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter17_The_AI_of_Driver_San_Francisco.pdf
  | https://doi.org/10.4324/9781315151700-17
- Peer-review status: **[industry, not peer reviewed]**.
- Verified: **partly.** Read: §17.2 (including §17.2.1–§17.2.2), §17.5, §17.6.3, §17.6.6–§17.6.8,
  §17.7. Not read: §17.1, §17.3–§17.4 (road network and route finding), §17.6.1–§17.6.2,
  §17.6.4–§17.6.5 (search area, static field, physics model, path following). **Read from**
  `refs/sr_gameaipro3_ch17_driversf.txt`.
- Sub-area: S2 (vehicles in a game; it could be cross-filed under S4).
- **Primary category: A.**
- Category justification: the chapter documents two systems and both are avoidance. *Civilian
  traffic* cannot conflict by construction: "Each spline had been defined to ensure that it did not
  interact with any other spline", so each vehicle follows it "knowing that there was no chance of
  colliding with other civilian vehicles" (§17.2). *Active Life AI* picks, from candidate paths,
  the one with the lowest cost, where proximity to other vehicles and predicted collisions are cost
  terms (§17.5, §17.6.6).
- Domain simulated: vehicles in a shipped open-world driving game. [§17.2]
- The rule, stated precisely:
  - *Civilian traffic:* follow a point around a looping spline that intersects no other spline
    (§17.2). This is a standing convention fixed at design time — the issue's own example shape for
    category A.
  - *Active Life AI, mid level:* lay a grid of nodes, one per lane, about 100 m ahead; score every
    path through it by summing node costs; keep the five cheapest (§17.5). In the chapter's
    simplified example, moving straight costs 1, changing lane 2, driving next to another car +1,
    driving in the oncoming lane +1 (§17.5). In the real game, nearness to other vehicles was
    evaluated at their *predicted* positions, read from their published vehicle paths (§17.5).
  - *Active Life AI, low level:* simulate each candidate with the game's physics; score each frame
    by three terms — movement against the gradient of a potential field (static plus a dynamic
    field around other vehicles), deviation from desired speed, and "a large penalty" for any
    collision found; nudge the path down the potential gradient and repeat for "three or four
    iterations"; take the lowest-scoring of the five (§17.6.3, §17.6.6–§17.6.8).
- Trigger condition: continuously — paths were regenerated "approximately every second" and cover
  "the next couple of seconds" (§17.2.1).
- Information required: every vehicle "owned a vehicle path" giving its predicted movement, which
  other vehicles' planners read (§17.2.1, §17.5). ⚠ **Boundary note.** A predicted path is an
  intended plan, not physical state, so reading it meets the issue's definition of a B channel. I
  still classify the entry A, because nothing is exchanged *between* agents and no outcome depends
  on a message: the simulator simply exposes its own state to the planner. This is a
  simulator-versus-robot difference that the A/B boundary does not anticipate; raised in
  [category-summary.md](category-summary.md) §4.
- Tie-breaking: lowest total score. `[not stated in chapter]` for equal scores. The interesting
  part is that **the weights are per-agent personality traits**: "Likeliness to drive in the
  oncoming traffic", "Likeliness to drive on sidewalks", "Preferred driving speed", and "How
  strongly hitting other vehicles should be avoided", which "affected every stage of the path
  planning" (§17.2.2). A rule-obeying driver "will receive big penalties from driving on sidewalks
  or in the oncoming lane, whereas a reckless driver would not differentiate" (§17.5).
- Guarantees claimed: none. Collisions are penalised, not excluded: paths that lead to collisions
  "were likely to be rejected" (§17.6.4 — a section I did not read in full; this sentence was found
  by keyword search).
- Evaluation: **none in the form of measurements.** The conclusion asserts that the system let "the
  game … run a simulation with thousands of vehicles" at 60 FPS (§17.7).
- Does it work: it shipped. No failure cases are reported in the sections I read.
- Validated against real human or real traffic data: no.
- Scalability: "thousands of vehicles", 60 FPS (§17.7) — stated without a count, hardware, or
  method, and achieved through level-of-detail: distant vehicles are "simply placed at the position
  defined by their path" with no physics at all (§17.2.1). So "thousands" is not thousands of
  agents running the conflict rule.
- Domain assumptions that limit portability: a road network of splines and lanes; centralised
  simulator with full state; three levels of detail keyed to distance from the player (§17.2.1).
- Portability to a generic simulator: [inference] two ideas port. (1) Design-time separation —
  give routine agents routes that cannot meet — removes conflicts for the bulk of a crowd at zero
  runtime cost; (2) level of detail — run the expensive rule only where it will be seen or will
  matter — is how the game reaches its scale. Neither is a conflict-resolution rule.
- Limitations and future work stated by the authors: `[not stated in the sections read]`.
- Relevance to this FYP: [inference] **the closest precedent in the whole review for the FYP's
  persona idea**: a shipped system in which a per-agent trait vector parameterises how strongly
  each agent avoids others and which norms it will break. It is unvalidated and hand-tuned
  ("scaled by factors we arrived at empirically", §17.6.6) — which is the gap an LLM-elicited,
  population-grounded trait table would fill. Also directly relevant to the 10,000-agent target:
  the scale comes from level of detail, not from a fast rule.
- BibTeX: `jenner2017driversf`

---

### [Epic-UnrealAvoidance]: Using Avoidance With the Navigation System in Unreal Engine

- Authors / Year / Venue: Epic Games (no named author) / page titled "Unreal Engine 5.8
  Documentation"; no publication date printed on the page; retrieved 2026-10-04 / Epic Developer
  Community documentation.
- Link: https://dev.epicgames.com/documentation/en-us/unreal-engine/using-avoidance-with-the-navigation-system-in-unreal-engine
- Peer-review status: **[industry, not peer reviewed]** — vendor documentation. ⚠ **Venue/date
  flag:** undated web documentation; the in-window judgement rests on the engine version named in
  the page title.
- Verified: yes (the whole page read; it is a how-to guide of which only the "Overview" describes
  behaviour). **Read from** `refs/sr_unreal_avoidance.txt`.
- Sub-area: S2
- **Primary category: A** (secondary: C, undocumented).
- Category justification: both documented methods choose a velocity to avoid a predicted collision
  (Overview). The page also says the RVO implementation includes "a priority system to help resolve
  potential collisions" (Overview), which is an arbitration device and would be C — but the page
  says nothing more about it, so I cannot classify on it.
- Domain simulated: game characters ("Agents"). [Overview]
- The rule, stated precisely — as far as the page goes, which is not far enough to reimplement:
  - *RVO:* "calculates the velocity vectors for each Agent to avoid a collision with nearby
    Agents", assuming neighbours "are traveling with a constant velocity within each time step";
    "The optimal velocity vector chosen is the closest match to the Agent's preferred velocity"
    (Overview). It "does not use the Navigation Mesh for avoidance, so Agents can potentially go
    'out of bounds'" (comparison table).
  - *Detour Crowd Manager:* "an adaptive RVO sampling calculation … calculating a coarse sample of
    velocities with a bias toward the Agent's direction", plus "visibility and topology path
    corridor optimizations" (Overview).
- Trigger condition: continuously, within an "Avoidance Consideration Radius" (set to 100 in the
  guide's step 4). [§4 of the guide]
- Information required: nearby agents' positions and velocities within the radius. [Overview]
- Tie-breaking: `[not stated]`. The "priority system" is named and not described.
- Guarantees claimed: none.
- Evaluation: none. The guide's only evidence is qualitative: without avoidance, agents heading for
  opposite targets produce "collisions in the center of the Level" (§3 of the guide).
- Does it work: `[not stated]` beyond the above.
- Validated against real human or real traffic data: no.
- Scalability: the Detour Crowd Manager "Has a fixed maximum number of Agents defined in the
  project settings" (comparison table). No number is given.
- Domain assumptions that limit portability: tied to the engine's Character and AI Controller
  classes.
- Portability to a generic simulator: [inference] not applicable as a rule — it is a product
  feature. What it evidences is adoption: a mainstream engine ships two variants of the same
  velocity-obstacle family and found it necessary to add a priority mechanism on top.
- Limitations and future work: the two limitations in the comparison table, quoted above.
- Relevance to this FYP: [inference] corroboration only. It supports [SunshineHill-RVO-ORCA]'s
  claim that velocity-obstacle methods are "the standard for collision avoidance in video games"
  (§19.1) with a vendor's own page, and it hints — no more — that shipped systems layer an
  arbitration rule over the avoidance rule.
- BibTeX: `epic2026unrealavoidance`

---

## Sources opened but not given an entry

- **Recast Navigation, `dtCrowdAgentParams` reference** (https://recastnav.com/structdtCrowdAgentParams.html;
  `refs/sr_detourcrowd.txt`). `[industry, not peer reviewed]`. A parameter list for the open-source
  crowd library that Unreal's Detour Crowd Manager is named after. The only behavioural statement
  is that `separationWeight` sets "How aggresive the agent manager should be at avoiding collisions
  with this agent". There is no rule description to put in the template, so no entry and no
  catalogue row.
- **Unity manual, NavMesh Agent / inner workings of the navigation system.** Not obtained: the
  pages returned a script-redirect stub to the download tool. Listed in
  [missing-papers.md](missing-papers.md) as an industry source, with no content recorded.
