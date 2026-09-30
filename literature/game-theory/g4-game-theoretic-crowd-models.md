# G4 — Game-theoretic crowd and pedestrian models

Prepared for issue [#20](https://github.com/M450NCH00/CrowdSimulation/issues/20).
Companion files: [`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md),
[`g2-norm-emergence.md`](g2-norm-emergence.md),
[`g3-cheap-talk.md`](g3-cheap-talk.md),
[`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md),
[`g6-transfer-across-games.md`](g6-transfer-across-games.md),
[`candidate-rule-catalogue.md`](candidate-rule-catalogue.md),
[`search-log.md`](search-log.md), [`refs-game-theory.bib`](refs-game-theory.bib).

This is the sub-area where conflict-resolution rules are actually **embedded in working
simulators**. The issue flags two properties as highest value: **validation against human
experimental data**, and **behaviour as the number of agents grows**. Both are addressed below, and
one entry states the scaling problem in a single sentence that the FYP should quote.

> **The sentence.** "[Game theory] is an adequate framework to handle the conflicting impulses of
> interacting agents endowed with planning capacities … **Unfortunately, the problem becomes
> intractable when the number of interacting agents grows.**" — [Bonnemain-GamePlayers], §1.
> That is the 10,000-agent problem, stated by a pedestrian-dynamics paper, with a proposed way out.

---

### [Bonnemain-GamePlayers]: Pedestrians in static crowds are not grains, but game players

- **Authors / Year / Venue:** Thibault Bonnemain, Matteo Butano, Théophile Bonnet, Iñaki
  Echeverría-Huarte, Antoine Seguin, Alexandre Nicolas, Cécile Appert-Rolland, Denis Ullmo / 2023 /
  *Physical Review E* **107**(2), article 024612. Published 28 February 2023.
- **Link:** doi:[10.1103/PhysRevE.107.024612](https://doi.org/10.1103/PhysRevE.107.024612)
- **Peer-review status:** **published**, peer-reviewed journal (APS). The issue listed this seed as
  `arXiv:2201.08592`; the published version exists and is cited. Fields confirmed from Crossref
  (`refs/gt_cr_10_1103_physreve_107_024612.json`).
- **Verified:** **full text of the preprint** (`refs/gt_arxiv_2201_08592.txt`). ⚠ The published APS
  version is paywalled and was **not** opened. **All locators below are to the preprint's
  sections**, and must be re-checked against the published article before the report quotes page
  numbers.
- **Sub-area:** G4
- **Tags:** none (2023)
- **Type:** formal theory + simulation, compared against published controlled experiments
- **The game or conflict modelled:** a **dense static crowd crossed by an intruder**. What is
  contested is **space** — each pedestrian wants to stay put and avoid effort, the intruder wants to
  pass. Number of parties: the whole crowd, treated in the mean-field limit. The payoff structure is
  a **cost functional**, not a matrix: agents "plan a global strategy that minimizes their overall
  discomfort" (Abstract). The paper's behavioural insight is stated at §1: the outcome is that
  agents anticipate that "it will cost them less effort" to let the intruder through than to flee —
  "the a priori cost-inefficient strategy … to let the intruder through may prove overall more
  efficient than running away from it" (§1).
- **The rule or solution concept:** a **Mean Field Game (MFG) equilibrium**, attributed to "Lasry
  and Lions … as well as Huang et al." (§1). The solution is not a discrete rule but an **optimal
  control field**: the MFG "can be reduced to a system of two coupled partial differential
  equations" (§2), namely a **Hamilton–Jacobi–Bellman** equation for the value function
  *u*(*t*, *x*) and a **Fokker–Planck** equation for the density *m*(*t*, *x*), given as system (3)
  in the preprint. The individual decision rule is the optimal drift
  **a\*(t, x) = −∇u(t, x)/μ** (§2) — i.e. each agent moves down the gradient of the value function.
  The key structural step: "the optimization problem (2) does not feature explicit coupling between
  agents anymore" (§2).
- **Information the rule requires:** **the local value-function gradient and the local crowd
  density** — i.e. a *field*, not the identity, type or intention of any individual neighbour. No
  agent needs to know who anyone else is. [inference] This is the cheapest information requirement
  of any entry in this review, and it is the reason the approach scales.
- **One-shot or repeated:** **neither, in the usual sense.** It is a single continuous-time optimal
  control problem over a planning horizon, solved once; there is no repeated play and no shared
  history. Note the model is **anticipatory**: the MFG has "mixed initial and final boundary
  conditions" (§2, on the forward–backward structure), so agents effectively plan against the
  future crowd state.
- **Communication required:** **none.** Coordination is entirely mediated by the density field.
  **This is a candidate for the FYP's runtime rule** — with the caveat below that it is a
  *continuous field* rule, not a discrete priority rule, so it answers "how do I move" rather than
  "who goes first".
- **Scalability — the field's own diagnosis, and the reason to read this paper:**
  - **The problem, stated plainly** (§1): "Game theory is an adequate framework to handle the
    conflicting impulses of interacting agents endowed with planning capacities: agents are now able
    to optimise their strategy taking into account the choices (or strategies) of others. So far,
    its use in pedestrian dynamics has mostly been restricted to evacuation tactics in discrete
    models. **Unfortunately, the problem becomes intractable when the number of interacting agents
    grows.**"
  - **The way out** (§1): "To overcome this quandary, we turn to Mean Field Games (MFG)".
  - **Why that solves it** (§2): the *N*-agent coupled game is replaced by **two PDEs whose cost is
    independent of the number of agents** — "the optimization problem (2) does not feature explicit
    coupling between agents anymore", and the system reduces to the HJB/FP pair (3). The paper
    additionally exploits "an elegant analogy with the nonlinear Schrödinger equation" (Abstract;
    §2 on the mapping) to analyse the resulting equations.
  - The contrast with the dominant alternative is also stated: force-based and constant-velocity
    models "owe their high computational tractability to" their short-horizon assumptions (§1) —
    i.e. cheapness has been bought by dropping anticipation, which is the thing this paper restores.
  - ⚠ **No wall-clock timings or complexity bounds are given.** The scalability claim is structural
    (cost independent of *N*), not measured. `[not stated in paper]` for actual runtimes.
- **Validated against human behaviour:** **yes — and this is the strongest human validation in this
  sub-area.** The model is compared against **controlled experiments with human participants**, and
  against two other model classes, in the paper's figure 1: its four columns are (1) simulations of
  a mono-layer of vibrated disks, (2) an agent-based model with imminent-collision anticipation,
  (3) "Results of the mean-field game introduced in this paper", and (4) "**Controlled experiments**"
  (figure 1 caption). The caption states the comparison was density-matched: "The crowd's density
  and intruder's size have been adjusted to match the experimental data (average density of 2.5
  ped/m²)". The specific human observation reproduced is named in the caption — "the relatively
  symmetrical density dip in front and behind the intruder, as well as the **transverse moves**" —
  and the Abstract states that existing models fail on exactly this: current models "fail to
  reproduce key features experimentally observed when dense crowds are crossed by an intruder,
  namely, transverse displacements toward regions of higher density." The paper also notes a
  real-world observation at larger scale: the phenomenon "was filmed at much larger scale in a dense
  crowd of protesters in Hong-Kong" (§1).
- **Assumptions that may not hold in a crowd:** the mean-field limit itself (agents respond to an
  averaged density, not to individuals) — reasonable in a **dense** crowd, questionable in a sparse
  one or in a two-agent corridor conflict; **homogeneous agents** with a common cost functional, so
  no personas or heterogeneous types; full rationality over a planning horizon with anticipation of
  the future density field; and the paper's own scope limit — it argues for relevance "at the
  **operational** level" (§1, repeatedly), i.e. short-timescale movement, explicitly distinguished
  from the strategic and tactical levels (§1).
- **Limitations stated by the authors:** the scope is deliberately narrow — the goal is "to
  demonstrate the practical relevance of this approach at the operational level, using an
  **elementary** MFG belonging to one of the first class of models introduced by Lasry and Lions"
  (§1). The model is presented as minimal, not complete.
- **Relevance to this FYP:**
  - **It supplies the scalability argument in the crowd-simulation literature's own words**, which
    is worth more to the report than the same point made from a multi-agent-systems paper: explicit
    *N*-agent game theory is intractable as *N* grows, and the escape route is to stop representing
    the coupling agent-by-agent (§1, §2).
  - [inference] But it is **not the escape route this FYP should take.** MFG's answer is to average
    the agents away. The FYP needs *heterogeneous* agents with personas (issue #16) making
    *discrete* right-of-way decisions. The FYP's escape route is the other one — a fixed rule
    evaluated per agent, per [Shoham-SocialLaws] — whose cost is also independent of *N* but which
    keeps individual agents distinguishable. Stating both routes and saying why the FYP takes the
    second is a strong paragraph for the report.
  - It is also the **benchmark for what "validated against human behaviour" should look like** in
    this project: a named published experiment, a matched density, and a specific qualitative
    feature (transverse displacement) that competing models get wrong.
- **BibTeX:** `bonnemain2023pedestrians`.

---

### [Camara-PedestrianModelsII]: Pedestrian Models for Autonomous Driving Part II: High-Level Models of Human Behavior

- **Authors / Year / Venue:** Fanta Camara, Nicola Bellotto, Serhan Cosar, Florian Weber, Dimitris
  Nathanael, Matthias Althoff, Jingyuan Wu, Johannes Ruenz, Andre Dietrich, Gustav Markkula, Anna
  Schieben, Fabio Tango, Natasha Merat, Charles Fox / 2021 / *IEEE Transactions on Intelligent
  Transportation Systems* **22**(9), pp. 5453–5472.
- **Link:** doi:[10.1109/TITS.2020.3006767](https://doi.org/10.1109/TITS.2020.3006767)
- **Peer-review status:** **published**, peer-reviewed journal (IEEE). The issue listed this seed as
  `arXiv:2003.11959`; the **published** version was obtained (accepted manuscript deposited in the
  White Rose Research Online repository) and is cited. Fields confirmed from Crossref
  (`refs/gt_cr_10_1109_tits_2020_3006767.json`).
- **Verified:** **yes — full text** of the published/accepted version
  (`refs/gt_camara2021_tits2.txt`). Locators are to its numbered sections and the page numbers
  printed in the running header of that PDF.
- **Sub-area:** G4
- **Tags:** none (2021)
- **Type:** survey
- **Used as the issue instructed:** as "an entry point" to be mined, with each referenced paper then
  "confirm[ed] independently". Its own §IV-A (pp. 11–12 of the accepted manuscript) is the source of
  the three follow-up leads below, and **each has been independently confirmed via Crossref**, with
  the sequential-chicken paper read in full.
- **The game or conflict modelled:** many, surveyed. The relevant framing is the survey's **order
  hierarchy** (§IV-A, p. 11): a *first-order* model predicts one pedestrian with no others present;
  a *second-order* model lets the observer model "X's own first-order model of another pedestrian
  Y's behaviour, which X can use to plan to avoid Y"; and then "We could then imagine third and
  higher order models… as both agents try to 'out-think each other' during their planning. **This
  would lead to an infinite computational regress.**"
- **The rule or solution concept:** the survey catalogues rather than proposes. Three
  game-theoretic families are distinguished in §IV-A:
  1. **Two-agent game theory interactions** (§IV-A-1, pp. 11–12), including the sequential chicken
     model — see [Fox-SequentialChicken] below.
  2. **Small group game theory models** (§IV-A-2, p. 12), including the **Stackelberg** pedestrian
     model — see [Johora-SharedSpaces] below.
  3. **Crowd game theory models** (§IV-A-3, p. 12), evacuation-focused: "Mesmer et al. modelled
     pedestrians' decision-making and interactions during evacuations with game theory. In [192] a
     model of pedestrian behavior in an evacuation used game theory and showed that **pedestrians
     get greater benefits by cooperating**" (§IV-A-3).
- **The information problem, stated as a limitation of the field** (§IV-A, pp. 11–12): the
  trajectory-selection models "assume that the choice of the entire continuous trajectory is drawn
  from a finite set of previously observed and costed trajectories as a single decision at the start
  of the interaction and **does not model responses to the other agent during the interaction**.
  They are used only as descriptive models rather than as real-time control because **they require
  each pedestrian's final goal location to be known in advance** to form the cost matrix — which is
  only obtainable by looking ahead in the data to see what happened post hoc." [inference] This is a
  precise, citable statement of why much of this literature is **not** usable as a runtime rule, and
  it is a useful exclusion criterion for the FYP.
- **A second information-requirement finding worth recording** (§IV-A, p. 11), on Ma et al.'s
  fictitious-play model: "The fictitious play assumes that each pedestrian has a known destination
  goal, **some known visual features (age, gender, initial body heading etc)** and a known utility
  function", with the utility functions "learned entirely automatically from video data of
  actualized trajectories, rather than set by theories", and "Performance is degraded when the
  pedestrian's goal locations are not known". [inference] Direct link to issue #16: this is a
  published pedestrian model in which **age and gender are inputs to a game-theoretic decision**,
  which is prior art the FYP's persona work should cite.
- **One-shot or repeated:** varies across surveyed models; the survey's own point is that most
  assume a single decision at the start of the interaction (§IV-A, quoted above).
- **Communication required:** the survey separates **interaction** models from **signalling** models
  (§IV-A vs §IV-B). Its signalling section reports human data that is directly relevant to whether
  runtime communication is even available to pedestrians: "pedestrian head turning towards a vehicle
  was sufficient for drivers to confidently infer pedestrians intent in **52%** of interaction cases
  observed… **Mutual eye contact** between driver and pedestrian was observed only in **13%** of
  interaction cases, accompanied by explicit signalling in **2%** of total cases" (§IV-B-1, p. 12,
  attributed to Nathanael et al.'s naturalistic study). [inference] This is strong empirical support
  for the FYP's premise: real humans resolve the overwhelming majority of these conflicts with **no
  explicit communication at all**. 2% explicit signalling is a number worth putting in the report.
- **Scalability:** the "infinite computational regress" of higher-order models (§IV-A, p. 11) is the
  survey's structural scaling statement. It also reports that the Stackelberg model "is able to
  handle several interactions at the same time" (§IV-A-2, p. 12). No complexity bounds are given —
  `[not stated in paper]`.
- **Validated against human behaviour:** the survey's headline verdict is a **negative** one and the
  FYP should quote it: the survey "shows that although there are good models for optimal walking
  behavior, **high-level psychological and social modeling of pedestrian behavior still remains an
  open research question requiring many conceptual and experimental resources to validate all types
  of models**" (Abstract). It also notes of the signalling literature that these models are "more
  mature, but **their results have not yet been quantified to the extent of enabling translation into
  algorithms**" (§IV, p. 11).
- **Assumptions that may not hold in a crowd:** the surveyed models are overwhelmingly
  **pedestrian–vehicle** rather than pedestrian–pedestrian, and mostly **two-party**. [inference]
  Transfer to a crowd is not automatic, and the survey does not claim it.
- **Limitations stated by the authors:** the Abstract's open-research-question verdict, quoted
  above; and the epistemological problem they raise about signalling models and higher-order
  knowledge, "There appears to be a potentially infinite regress here" (§IV-B, p. 12).
- **Relevance to this FYP:**
  - Supplies an **exclusion criterion** with a citation: a model that needs goal locations known in
    advance, or that is fitted post hoc, cannot be a runtime rule (§IV-A).
  - Supplies the **2% explicit-signalling** figure (§IV-B-1) — empirical support for building a
    communication-free rule.
  - Supplies **prior art for demographic inputs** to game-theoretic pedestrian decisions (§IV-A, Ma
    et al.), linking this issue to issue #16.
  - Supplies an honest statement that this field is **not yet validated** (Abstract), which the FYP
    should quote rather than overclaim around.
- **BibTeX:** `camara2021pedestrian`.

---

### [Fox-SequentialChicken]: When Should the Chicken Cross the Road? — Game Theory for Autonomous Vehicle–Human Interactions

- **Authors / Year / Venue:** C. W. Fox, F. Camara, G. Markkula, R. A. Romano, R. Madigan, N. Merat
  (Ibex Automation Ltd; University of Lincoln; Institute for Transport Studies, University of Leeds)
  / 2018 / *Proceedings of the 4th International Conference on Vehicle Technology and Intelligent
  Transport Systems* (**VEHITS 2018**), pp. 431–439.
- **Link:** doi:[10.5220/0006765404310439](https://doi.org/10.5220/0006765404310439) ·
  open access via SciTePress
- **Peer-review status:** **published**, peer-reviewed conference proceedings. Fields confirmed from
  Crossref (`refs/gt_crossref_all.json`, key `fox2018`).
- **Verified:** **yes — full text** (`refs/gt_fox2018_vehits.pdf`, SciTePress PDF; text at
  `refs/gt_fox2018_vehits.txt`). Locators are to its numbered sections and the printed page numbers
  (432–433 for the model).
- **How it was found:** mined from [Camara-PedestrianModelsII] §IV-A-1 (its reference [75]) and
  then **independently confirmed and opened**, per the issue's instruction.
- **Sub-area:** G4
- **Tags:** none (2018)
- **Type:** formal theory + simulation
- **The game or conflict modelled:** **sequential chicken** — "an initial model for negotiation
  between an autonomous vehicle and another vehicle at an unsigned intersections or (equivalently)
  with a pedestrian at an unsigned road-crossing (jaywalking), using discrete sequential game
  theory" (Abstract). Two parties, labelled Y and X. Fully specified (§2, pp. 432–433): a 1-metre
  grid world, two straight roads meeting at right angles, one agent on each; each agent chooses
  speed *a* ∈ {1, 2} m/s each 1-second turn, simultaneously and in secret; *y* and *x* are the two
  agents' distances to the intersection. Payoffs: "We assign (negative) utility *U_crash* to each
  player for a crash; otherwise −*U_time*·*T* where *T* is the number of seconds it takes to reach
  the intersection from the start of the game, and *U_time* is the (positive) value of saving one
  second of travel time" (§2). Crash states are "(y, x) ∈ {(0, 0), (1, 1)}" (§2). The recursion over
  sub-games is given explicitly in §2 as *v_{y,x,t}* over the four next states
  (*y*−1,*x*−1), (*y*−1,*x*−2), (*y*−2,*x*−1), (*y*−2,*x*−2), "computable via standard matrix Game
  Theory" (§2).
- **The rule or solution concept:** **meta-strategy convergence**, a novel equilibrium-selection
  rule. The problem it solves is stated in the Abstract: "Unlike most Game Theory applications in
  Economics, active vehicle control requires **real-time selection from multiple equilibria with no
  history**, and we present and argue for a novel solution concept, meta-strategy convergence,
  suited to this task." It operates after standard refinements: "After removing dominated and
  non-ESS equilibria, we know of no good remaining solution concepts under the assumption that the
  other player is also rational… In the absence of any other way to select from the remaining
  equilibria's strategies, we form a new meta-strategy which chooses one of them" (§2, p. 433). The
  paper's own justification is temporal: it is "based on everything we currently know about the
  'rational' process of equilibrium pruning and selection, including the absence of information in
  some cases, and on a temporal ordering of rational reasoning" (§2, p. 433).
- **⚠ The headline result, and it is a warning:** "The model shows that when only vehicle position
  is used to signal intent, **the optimal behaviors for both agents must include a non-zero
  probability of allowing a collision to occur.** This suggests extensions to reduce this
  probability in future, such as other forms of signaling and control" (Abstract). [inference] This
  is a formal result that a **position-only, communication-free rule cannot be collision-free** in
  this game. For the FYP that is important and slightly uncomfortable: a purely
  communication-free convention over positions will deadlock or collide with some positive
  probability. The report should state this rather than claiming a communication-free rule is
  strictly sufficient.
- **Information the rule requires:** **both agents' positions (*y*, *x*) and the elapsed time *t*** —
  nothing else. Plus the modelling assumption of shared utilities: "Assume that both players have
  identical utility functions, and **know this to be the case**" (§2, p. 433). No identities, no
  types, no messages, **no history** (Abstract). This is a genuinely minimal information
  requirement.
- **One-shot or repeated:** **one-shot, explicitly.** "real-time selection from multiple equilibria
  **with no history**" (Abstract). The game is finite by construction: "This ensures a finite game,
  because the vehicles are guaranteed to move closer to the intersection at each step. Formally, y
  and x are decreasing variants" (§2, p. 432). **This is the only fully-read entry in the review
  that is designed from the start for a single encounter between strangers with no shared past.**
- **Communication required:** **none.** Intent is signalled only through position — that is the
  premise of the headline result ("when only vehicle position is used to signal intent", Abstract).
  **This is a strong candidate for the FYP's runtime rule.**
- **Scalability:** `[not stated in paper]`. The model is two-agent; the backward-induction tree
  search (algorithm 1, §2) is over the joint position–time state space, so [inference] cost grows
  with the product of the two agents' position ranges and would grow combinatorially with more
  agents — but the paper makes no such claim and I am not attributing one to it. Note the model is
  solvable **offline** into a lookup table over (*y*, *x*, *t*), which is the property that matters
  for the FYP.
- **Validated against human behaviour:** **not in this paper** — but yes in the follow-up, which is
  why the chain matters. [Camara-PedestrianModelsII] §IV-A-1 (p. 12) reports: "Camara et al. [41],
  [34] evaluated the model [75] by fitting one parameter to **controlled laboratory experiments
  where pedestrians were asked to play sequential chicken**. This behavioural parameter was found to
  be a **ratio between the utility of avoiding a collision and the utility of saving time**." The
  follow-up papers are confirmed to exist from the survey's reference list — Camara, Romano,
  Markkula, Madigan, Merat & Fox, "Empirical game theory of pedestrian interaction for autonomous
  vehicles", *Proc. Measuring Behavior* 2018 (survey ref [41]); and Camara, Cosar, Bellotto, Merat &
  Fox, "Towards pedestrian-AV interaction: method for elucidating pedestrian preferences", *Proc.
  IEEE/RSJ IROS Workshops* 2018 (survey ref [34]) — but ⚠ **neither was opened**, so the human-fit
  claim is recorded **as the survey states it**, attributed to the survey, and is **not** treated as
  a direct reading of the experiment. A related published follow-up was independently confirmed via
  Crossref: Camara, Cosar, Bellotto & Merat, "Continuous Game Theory Pedestrian Modelling Method for
  Autonomous Vehicles", in *Human Factors in Intelligent Vehicles*, 2022,
  doi:10.1201/9781003338475-1 — also **not opened**.
- **Assumptions that may not hold in a crowd:** identical and commonly known utility functions (§2,
  p. 433) — which rules out heterogeneous personas as stated; discretised 1 m grid and 1 s turns;
  exactly two agents at right angles; full rationality on both sides, with the authors being
  explicit that they *want* this ("for AVs which will eventually interact with other autonomous
  vehicles, we want all players to be completely mechanized and rational", §2, p. 433) — a
  pedestrian crowd is the opposite case.
- **Limitations stated by the authors:** the non-zero collision probability (Abstract), presented by
  the authors as motivating future work; and the model's self-description as "intended to be the
  simplest possible which captures the dynamics of interest… but which can also serve as a
  foundation for many more complex ones" (§1, p. 432).
- **Relevance to this FYP:** the **closest existing thing to what the FYP wants to build**, in the
  pedestrian domain:
  - A communication-free, history-free, one-shot decision rule over observable positions,
    precomputable offline into a table — structurally the `DO : S → A` of
    [Shoham-SocialLaws].
  - With human-experimental grounding available downstream, and with the fitted parameter being an
    interpretable ratio (collision-avoidance utility vs time-saving utility) — [inference] which is
    plausibly something an LLM *could* be asked to supply per persona, linking this issue to the
    FYP's dataset work.
  - And with an honest negative result attached (non-zero collision probability) that the FYP should
    inherit rather than ignore.
- **BibTeX:** `fox2018chicken`.

---

### [Bouzat-RoomEvacuation]: Game theory in models of pedestrian room evacuation

- **Authors / Year / Venue:** S. Bouzat, M. N. Kuperman (Consejo Nacional de Investigaciones
  Científicas y Técnicas; FiEstIn, Centro Atómico Bariloche (CNEA), Bariloche, Argentina) / 2014 /
  *Physical Review E* **89**(3), article 032806.
- **Link:** doi:[10.1103/PhysRevE.89.032806](https://doi.org/10.1103/PhysRevE.89.032806)
- **Peer-review status:** **published**, peer-reviewed journal (APS). Fields confirmed from Crossref
  (`refs/gt_crossref_all.json`, key `bouzat2014`).
- ⚠ **The issue's seed link was a ResearchGate listing**, and instructed me to "Locate the published
  version rather than citing the ResearchGate listing." Done: the published version is the *Physical
  Review E* article above, and the preprint is `arXiv:1311.1708`.
- **Verified:** **full text of the preprint** (`refs/gt_bouzat2014_arxiv.txt`, arXiv:1311.1708v1,
  7 Nov 2013). The published APS version is paywalled and was **not** opened. **Locators below are
  to the preprint's named sections** and must be re-checked against the published article.
- **Sub-area:** G4
- **Tags:** none (2014)
- **Type:** simulation
- **The game or conflict modelled:** **cell contention in a lattice-gas evacuation model** — which
  is the closest analogue in this review to the FYP's bridge/doorway conflict. "We analyze the
  pedestrian evacuation of a rectangular room with a single door considering a Lattice Gas scheme
  with the addition of behavioral aspects of the pedestrians" (Abstract). *N* pedestrians on an
  *L* × *W* lattice. The conflict is defined precisely: "When a given site is chosen by more than
  one agent on their attempt to jump, we say that there is a conflict at that site" (§Second stage).
  **Conflicts can involve 2, 3 or 4 agents**: "A conflict can involve two, three or four agents, due
  to the existence of four allowed directions for arriving to a given site" (§Second stage) — so
  this is genuinely multi-party, not just dyadic. Payoff structure: "We consider game rules
  analogous to those from the **Prisoner's Dilemma and Stag Hunt** games, with payoffs associated to
  **the probabilities of the individuals to advance to the selected site**" (Abstract).
- **The rule or solution concept:** a **strategy-dependent win-probability matrix**, stated exactly
  (§Second stage). Each pedestrian holds a fixed attitude, cooperative (C) or defective (D), from
  the start. For a two-agent conflict the win probabilities are:

  |   | C | D |
  |---|---|---|
  | **C** | ½ | 0 |
  | **D** | 1/P | 1/(2P) |

  with the paper's own reading: "First, in a two cooperators game there is always a winner (that
  jumps to the desired position) which is chosen at random between the two players. Second, in a
  game between a cooperator and a defector, **the cooperator has no chance to advance while the
  defector advance with probability 1/P**. Third, in a game between two defectors, each of the
  agents has probability 1/(2P) of becoming the winner." Here "P ≥ 1 is a parameter that measures
  the conflictive attitude of the defectors, which makes them focus more on the competition than on
  the possibilities of movement" (§Second stage). The resolution procedure is explicit: "As a result
  of the game, a winner may be selected to jump to the desired site, while the rest of the players
  (the losers) will lose their opportunity to move at that time step… with certain probability… a
  game can have **no winner**. In such a case, all the players will lose their opportunity to move"
  (§Second stage). Motion itself mixes random and goal-directed components via a randomness
  parameter *R*: "With probability R (0 ≤ R ≤ 1), the direction of the jump attempt is chosen at
  random… Conversely, with probability 1 − R the direction of jump attempt is chosen according to a
  desired (or rational) direction" (§Model).
- **The headline result:** "We find that, **even when defecting is the rational choice for any
  agent, under certain conditions, cooperators can take advantage from mutual cooperation and leave
  the room more rapidly than defectors**" (Abstract).
- **Information the rule requires:** **each agent's own strategy label (C or D), the set of agents
  contending for the same cell, and their strategy labels.** That is a local neighbourhood query
  plus one bit per contender. [inference] Cheap and entirely available to a simulator — this is the
  most directly implementable rule in the review.
- **One-shot or repeated:** **one-shot per conflict.** Each cell contention is resolved
  independently, with no history and no memory of previous encounters. Strategies are fixed per
  agent for the whole run, so there is no learning. **Works between strangers meeting once.**
- **Communication required:** **none.** **This is a candidate for the FYP's runtime rule** — and
  notably it is already in the form of a simulator's conflict-resolution subroutine, which no other
  entry is.
- **Scalability:** `[not stated in paper]`. No computational cost result or large-*N* study is
  reported in what I read. [inference] The rule itself is O(number of contenders) per contested
  cell per timestep, which is trivially cheap, but the paper does not say so and I am not
  attributing the claim to it.
- **Validated against human behaviour:** **no.** No human data is fitted. The paper's motivation is
  applied — "understanding the dynamics of the movement of pedestrians and anticipating the problems
  that may arise in an emergency situation is critical in the design of large spaces" (§Introduction)
  — but the validation is internal.
- **Assumptions that may not hold in a crowd:** ⚠ the most important one is that **the C/D strategy
  is an exogenous fixed trait assigned at the start** ("from the beginning of the dynamics each
  pedestrian adopts an attitude", §Second stage) — it is an **input assumption, not a result**. The
  model does not explain why anyone cooperates; it assigns cooperation and reports the consequence.
  [inference] This is exactly the type-(b) trap flagged in
  `literature/demographic-personas/human-demographic-effects.md` for issue #16: a simulation whose
  demographic or behavioural effect is a restatement of its own parameter. The FYP must not cite
  this paper as *evidence that* pedestrians cooperate. Other assumptions: discrete lattice and
  discrete time; a single door; four-neighbour movement only.
- **Limitations stated by the authors:** the game-rule mapping is presented as an analogy ("game
  rules **analogous to** those from the Prisoner's Dilemma and Stag Hunt games", Abstract) rather
  than a derivation, and the strategy assignment is stated as a modelling assumption throughout
  §Second stage.
- **Relevance to this FYP:**
  - **The single most directly transferable rule in the review**: a drop-in conflict-resolution
    subroutine for cell contention, multi-party, one-shot, communication-free, with an explicit
    probability matrix and a single tunable parameter *P*.
  - [inference] It also shows the FYP where an LLM could plug in: this model **assumes** the C/D
    label and the parameter *P*. The FYP's contribution could be to have the LLM supply the label
    and *P* **per persona and per scenario**, instead of assigning them arbitrarily. That turns the
    paper's weakness (exogenous strategies) into the FYP's contribution, and it is a concrete,
    testable design proposal to put to the supervisor.
  - The `P` parameter also gives a precedent for the "no winner" outcome — a formal way to represent
    the stall the FYP is trying to eliminate.
- **BibTeX:** `bouzat2014game`.

---

### [Johora-SharedSpaces]: Modeling Interactions of Multimodal Road Users in Shared Spaces

- **Authors / Year / Venue:** Fatema T. Johora, Jörg P. Müller / 2018 / *2018 21st International
  Conference on Intelligent Transportation Systems* (**IEEE ITSC**), pp. 3568–3574.
- **Link:** doi:[10.1109/ITSC.2018.8569687](https://doi.org/10.1109/ITSC.2018.8569687)
- **Peer-review status:** **published**, peer-reviewed conference proceedings (IEEE). Fields
  confirmed from Crossref (`refs/gt_crossref_all.json`, key `johora2018`).
- **Verified:** **bibliographic record only.** IEEE Xplore is paywalled and no open author copy was
  located. **Full text not opened.** A related confirmed record — Johora's 2022 Springer monograph
  *Modeling Interactions among Pedestrians and Cars in Shared Spaces*,
  doi:10.1007/978-3-658-38345-9 — was also **not** opened.
- **How it was found:** mined from [Camara-PedestrianModelsII] §IV-A-2 (its reference [109]), as the
  issue instructed, and **independently confirmed to exist** via Crossref.
- **Sub-area:** G4
- **Tags:** none (2018)
- **What is recorded, and how it is attributed:** because I did not open the paper, everything below
  is **as reported by [Camara-PedestrianModelsII] §IV-A-2, p. 12**, and is attributed to the survey,
  not to Johora & Müller:
  > "Johora and Müller [109] proposed a three-layer trajectory prediction model composed of a
  > trajectory planner, a force-based (social force) model and a game theoretic decision model. The
  > game theory model is based on **Stackelberg games, a sequential leader-follower game** where
  > pedestrians have three different possible actions: **continue, decelerate and deviate** and the
  > car has two possible actions: **continue and decelerate**. This model is able to **handle
  > several interactions at the same time**."
- **Why it is listed anyway:** the issue specifically asked for "the Stackelberg leader-follower
  pedestrian model", and this is it. Three properties make it worth acquiring: the **discrete action
  set** (continue / decelerate / deviate) is exactly the vocabulary a crowd-simulation rule needs;
  the **leader–follower asymmetry** is a priority rule of the kind G1 is about; and the survey's
  claim that it handles several interactions simultaneously speaks to the scaling question.
- **⚠ No template fields are filled in**, because filling them from a survey's one-paragraph summary
  would be precisely the secondhand sourcing the issue forbids. It is listed as a **confirmed,
  unacquired lead** and flagged in [`search-log.md`](search-log.md) as an acquisition target.
- **BibTeX:** `johora2018modeling`.

---

## Summary of G4

| | |
|---|---|
| **Qualifying entries** | **4 fully-read** (Bonnemain 2023, Camara 2021, Fox 2018, Bouzat & Kuperman 2014), plus 1 confirmed-but-unacquired lead (Johora & Müller 2018) — **criterion met** |
| **Validated against human data** | **Bonnemain 2023 only**, directly (figure 1, column 4: controlled experiments, density-matched at 2.5 ped/m²). Fox 2018 has human validation **downstream**, reported by the survey but not read at source. The other two: no. |
| **Scalability stated** | **Bonnemain 2023** — explicit: *N*-agent game theory "becomes intractable when the number of interacting agents grows" (§1), solved by reducing to two *N*-independent PDEs (§2). **Camara 2021** — "infinite computational regress" for higher-order models (§IV-A). Fox and Bouzat: `[not stated in paper]`. |
| **Most transferable rule** | **Bouzat & Kuperman's cell-contention matrix** — multi-party, one-shot, communication-free, already in simulator-subroutine form |
| **Most structurally relevant** | **Fox et al.'s sequential chicken** — one-shot, no history, position-only, precomputable offline |

**Three things to carry into the report** (all [inference] from sourced statements above):

1. Quote Bonnemain §1 for the scaling problem, then say the FYP takes the *other* escape route —
   a per-agent fixed rule rather than a mean-field average — because the FYP needs heterogeneous
   personas, which mean-field averaging destroys.
2. Quote Camara §IV-B-1 for the 2% explicit-signalling figure. It is the best empirical support in
   this review for building a communication-free rule in the first place.
3. Inherit Fox et al.'s negative result honestly: a position-only communication-free rule carries a
   **non-zero collision probability** (Abstract). Do not claim a communication-free convention is
   strictly sufficient.

**Draft status:** draft pending supervisor review.
