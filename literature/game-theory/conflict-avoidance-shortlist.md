# Reading shortlist — rules that *avoid* conflict, not just resolve it

> **Why this file exists.** The six sub-area files from issue [#20](https://github.com/M450NCH00/CrowdSimulation/issues/20)
> catalogue everything found. This file is the **filtered shortlist** against one specific
> criterion, set after reading them:
>
> > *In a simulator or game, rules that agents follow in order to avoid conflict — so that the
> > conflict is resolved by not arising in the first place.*
>
> Three papers that were **unobtainable** when the sub-area files were written have since been
> supplied and read in full: [Camara-EmpiricalGT], [Duffy-CorrelatedEq] and [Johora-SharedSpaces].
> Their entries here are the primary record; the sub-area files have been updated to match.

Companion files: [G1](g1-conflict-games-conventions.md) · [G2](g2-norm-emergence.md) ·
[G3](g3-cheap-talk.md) · [G4](g4-game-theoretic-crowd-models.md) · [G5](g5-llm-agents-game-theory.md) ·
[G6](g6-transfer-across-games.md) · [rule catalogue](candidate-rule-catalogue.md) ·
[search log](search-log.md) · [refs](refs-game-theory.bib)

**Draft pending supervisor review.** Updated 2026-10-02.

---

## 0. The distinction this file is built on

Reading the shortlist against the criterion exposed a split that the sub-area files did not make,
and it is worth stating because it changes which papers are actually useful:

| | What the rule does | Papers |
|---|---|---|
| **Ex-ante — prevention** | The rule means the clash **never arises**. Agents' trajectories or actions are shaped so they do not contend for the same resource. | Shoham & Tennenholtz; Foley et al.; Fox et al.; Johora & Müller; Camara et al.; Bonnemain et al. |
| **Ex-post — resolution** | The clash **happens**, then a procedure picks a winner. | Bouzat & Kuperman; Duffy & Feltovich |

[inference] **Both are useful to this FYP, but they answer different questions.** Ex-ante rules
answer *"how do I move so that we never deadlock?"* Ex-post rules answer *"we are both here, who
goes?"* A crowd simulator needs both: an ex-ante rule to keep the contention rate low, and an
ex-post rule for the residual cases the ex-ante rule does not catch. Saying so explicitly is a
cleaner architecture than treating "conflict resolution" as one thing, and it is worth putting to
the supervisor as a framing for the implementation.

A third category appears in Johora & Müller and is worth naming separately: **reactive rules** —
simple angular conditions evaluated locally with no game solved at all. They are ex-ante, almost
free to compute, and they handle the majority of cases in that paper's simulator.

---

# Part A — the three newly obtained papers

---

## A1. [Camara-EmpiricalGT]: Empirical game theory of pedestrian interaction for autonomous vehicles

- **Authors / Year / Venue:** Fanta Camara, Richard Romano, Gustav Markkula, Ruth Madigan, Natasha
  Merat, Charles Fox (Institute for Transport Studies, University of Leeds; School of Computer
  Science, University of Lincoln; Ibex Automation Ltd) / 2018 / *Proceedings of Measuring Behavior
  2018* (11th International Conference on Methods and Techniques in Behavioral Research), Manchester,
  UK, 6–8 June 2018, eds. Grant, Allen, Spink & Sullivan, Manchester Metropolitan University,
  **pp. 238–244**. ISBN 978-1-910029-39-8.
- **Link:** White Rose Research Online eprint 129303 (accepted version)
- **Peer-review status:** **published**, peer-reviewed conference proceedings.
- **Verified:** **yes — full text.** PDF supplied by the user 2026-10-02 and cached as
  `refs/gt_camara2018_measuringbehavior.pdf` (text at `.txt`). ⚠ **Locator note:** this is the
  **accepted version** deposited in White Rose; it carries no printed page numbers, so locators
  below are to **numbered sections**, not pages. Two numbers (the Table 2 counts and the Figure 3
  optima) are read from **images** that the text layer does not contain — they are marked where used.
- **Sub-area:** G4 · **Type:** human experiment + method paper · **Category:** ex-ante
- **Funding declared:** EU Horizon 2020 grants No 723395 (InterACT) and No 645376 (FLOBOT).

### Why it exists — a real operational failure that is exactly your problem

This is the clearest statement in the whole review of *why a yielding rule cannot simply be "always
yield"*. From the Abstract:

> "If AVs are programmed to stop every time another road user obstructs them, then **other road users
> simply learn that they can take priority at every interaction, and the AV will make little or no
> progress.**"

And it is not hypothetical. §1 reports a real deployment — an autonomous minibus run continuously on
commuter routes in La Rochelle (France) and Trikala (Greece) for several weeks:

> "once the local population has learned that the vehicle was programmed to be perfectly safe and
> stop at any obstacle, pedestrians and other vehicles would regularly take advantage of the AV to
> push in front of it." (§1)

§1 adds, almost in passing, the single most on-point sentence in this file for the FYP's hallway
scenario:

> "A well-known scenario is for two pedestrians to meet similarly and make several attempts dodging
> from side to side in order to agree on how to pass. **Two polite road users can be almost as
> dangerous as two dominant ones — by continually trying to yield to one another they get closer to a
> collision without the decision being made.**" (§1)

[inference] That is the "after you" deadlock, named in the literature, with the mechanism stated:
**symmetric politeness is itself a failure mode.** Any rule the FYP extracts must break symmetry;
a rule that makes everyone more courteous will make the stall worse, not better.

### The model it measures (§2.1) — Sequential Chicken, restated

Two agents *Y* and *X* approach the same intersection. If neither yields they collide, each
receiving negative utility *U_crash*; otherwise each reaches its destination at time delay *T* with
utility −*T*·*U_time*. Positions are discretised onto a plus-maze of grid squares; time into turns
in which both players pick a speed of 1 or 2 squares per turn. Two assumptions matter:

> "It assumes that **no lateral motion is permitted**, and that there is **no communication between
> the agents other than seeing each other's positions**." (§2.1)

The sub-game at state (*y*, *x*, *t*) is solved by recursion over the four successor states, and
then — the property that matters most for implementation:

> "Under a mild approximation (Fox et al., 2018) the solution may further **drop all dependency on
> time *t*** so that state values and optimal strategies becomes **functions only of the player
> positions (*y*, *x*)**." (§2.1)

[inference] So the runtime object is a **2-D lookup table indexed by the two agents' positions**.
That is about as cheap as a decision rule can be, and it is the strongest evidence in this review
that a game-theoretic rule can be afforded at 10,000 agents — the game is solved once, offline, and
runtime is a table read.

The paper restates the headline theoretical result and, unlike the VEHITS paper, explains *why* it
is not a defect:

> "The model shows that if the two players play optimally, **there must exist a non-zero probability
> for a collision to occur.** This corresponds to the intuition that a perfectly safe vehicle which
> yields in every case will make no progress. **Players must include some credible threat of
> collision to avoid being taken advantage of.**" (§2.1)

### The experiment, in detail

**Purpose — and a caveat the authors state up front.** The model computes optimal strategies *given*
(*U_crash*, *U_time*) but does not supply those numbers. The long-term aim is to measure them from
real traffic CCTV. This study does not do that:

> "The present study is intended to illustrate only the method for measuring such behaviors rather
> than report results, so instead uses a simplified proxy. Rather than interact physically, pairs of
> human subjects play a **board-game version** of Sequential Chicken." (§2.2)

**Participants.** "Sixteen participants aged from 22 to 48 were divided into 8 groups of 2 players"
(§2.2). Each group sat with an experimenter around a table in a university room for about 10
minutes. Conducted under University of Lincoln research ethics policy.

**Condition 1 — "Natural game."** Players Y and X start 10 squares from the intersection
(*y* = 10, *x* = 10). They were told "their goals were to **avoid a collision and to be the first to
cross over this intersection as quickly as possible** as if they were trying to commute to their
office to work there in a morning" (§2.2). Each player holds two cards marked 1 and 2; each turn
both select one **in secret**, reveal simultaneously, and move together. Three games per group
(**24 games total**).

**Condition 2 — "Chocolate game."** After the three natural games, three more per group with
explicit material rewards: "the winner is the first to pass the intersection, and will receive two
chocolates (Celebrations, Mars Inc.), while the second to pass the intersection will receive one
chocolate, that both will receive no chocolates if there were any collision" (§2.2). Chocolates
handed over after each game. Three games per group (**24 games**, 48 overall).

**How behaviour was measured (§2.3).** Bayesian inference of θ = (*U_crash*, *U_time*) from the
observed moves *D*, assuming players play Bayes-optimally under the model *M*. With a flat prior,
P(θ|M,D) ∝ P(D|θ,M), and the likelihood is a product over games and turns of the two players'
action probabilities, read directly off the optimal strategies. Two methodological points worth
copying:

1. **A noise model, because the pure model assigns zero probability to things that happen.** "M
   assigns zero or near-zero probabilities to many events which are found to occur in the data.
   Uncontrolled, this can be **catastrophic for any Bayesian model of real data**" (§2.3). They
   therefore use a mixture *M′* that generates each observation from *M* with probability (1−*s*)
   and uniformly at random otherwise, with **s = 1/10**.
2. **A Gaussian Process over the likelihood surface.** Log-likelihoods are sampled on a regular
   grid and a GP regression (Rasmussen & Williams 2006) with an RBF kernel is fitted to them,
   giving interpolated estimates *and* uncertainty between sampled points (§2.3, §3).

### Findings

- **Collisions went *up* when the reward was made explicit.** Table 2 (read from the table image):
  natural games — 24 games, **5 collisions**, average delay ≈ 1.368 boxes (≈ 0.684 s); chocolate
  games — 24 games, **8 collisions**, average delay 1.125 boxes (0.5625 s); total 48 games, **13
  collisions**. The text confirms: "More collisions have occurred in the chocolate game than in the
  natural game" (§3).
- **The fitted preferences are startling.** The GP peak for the natural case and the chocolate case
  both sit around (*U_crash*, *U_time*) = **(0, 30)** (§3; Figure 3 panel titles give
  "U_crash = 0, U_time = 30" with log-likelihoods −113.921 and −101.610 respectively — read from the
  figure image). The authors are blunt about what that means:

  > "From the viewpoint of real-world interactions, it is **surprising to see a preference towards
  > time-saving over crash avoidance** in the players. In the real world, the cost of crash is
  > usually millions of times more than the value of a second of commuting time, but here the players
  > behave the opposite way." (§4)

  Their explanation: "This may be because the **board-game-like nature of the experimental setting
  encourages the players to think in terms of winning and losing** rather than just optimizing their
  personal utility. In the chocolate game this is made to be explicit by rewards the players
  specifically as winner and loser in the interaction. This leads to more collisions in this more
  competitive game." (§4)
- **Only the ratio is identified, not the absolute values.** "The shapes of the likelihood surfaces
  are roughly radial, which suggest that it may only be **the ratio between the two parameters**
  which is important rather than their absolute values. Possibly the angles of the contour lines
  define equivalence classes of parameters." (§4)
- **The pipeline claim.** "The model can be trained on human behavior then **transferred into a
  controller to specify new robotic behaviors**." (§4)

### Research gaps

**Stated by the authors (§4):**
- Realism: "We do not consider either the model or the experimental setup to be especially realistic
  versus real-world interactions, but they are sufficiently complex to illustrate the general method."
- Sample size: "The number of experiments performed was quite small, and future work including
  further experiments may produce more peaky posterior distributions."
- Model extensions wanted: "continuous positions and speeds, uncertain beliefs in opposite player
  utility function, lateral motion"; and data collection from "'big' real-world CCTV video of
  road-user interactions".
- The collision threat is load-bearing and they want to soften it: future work could add "additional,
  smaller negative utilities such as humiliating annoying pedestrians with horns or spraying them
  with water jets, in order to reduce or eliminate the necessity of actually hitting them whilst
  still allowing autonomous vehicles to make progress."

**Gaps I identify that this FYP could fill** — all `[inference]`:
- **No demographics.** Participants are recorded only as "aged from 22 to 48". Age and gender are
  not analysed, despite the model having exactly one free behavioural parameter per agent that could
  plausibly vary with them. This is a clean join to `literature/demographic-personas/` (issue #16).
- **Homogeneity is baked in.** "The basic model assumes both agents share the same parameters
  *U_crash* and *U_time* and both know this to be the case" (§2.1). Heterogeneous agents are
  precisely what a persona-driven crowd needs, and the paper does not have them.
- **Only one dyad type.** Pedestrian–pedestrian corridor conflict is mentioned (the "dodging from
  side to side" passage, and Figure 2's Barnes-dance crossing) but never modelled or measured.

### How it helps this FYP

1. **It is the complete template for the FYP's own method**, at one-tenth the scale: *define a game
   → leave the human-preference parameters free → measure them from behaviour → fold the fitted
   model into a controller.* The FYP's version replaces "measure from 16 humans around a table" with
   "elicit from an LLM per persona". That makes the contribution easy to state and easy to defend,
   because the surrounding method is already published.
2. **It gives the FYP a named, cheap target parameter.** One scalar — the ratio of collision-avoidance
   utility to time-saving utility (§4) — determines the behaviour. Asking DeepSeek for *that ratio*
   per persona and per scenario is a far more tractable elicitation task than asking for free-text
   behaviour, and it plugs straight into an existing published model.
3. **⚠ It is also a warning about the FYP's elicitation method, and this is the most valuable thing
   in the paper.** The fitted *U_crash* ≈ 0 means the participants behaved as though **crashing was
   free**, because the board-game framing made them think in terms of winning rather than survival
   (§4). The FYP elicits behaviour from an LLM given a *described* scenario — which is also a
   game-like frame, one step further removed from real stakes than a board game is. **If a board game
   can drive the measured crash cost to zero, a text prompt plausibly can too.** The report should
   state this risk explicitly and, ideally, test it by varying the framing of the scenario
   description and checking whether the elicited behaviour moves.

---

## A2. [Johora-SharedSpaces]: Modeling Interactions of Multimodal Road Users in Shared Spaces

- **Authors / Year / Venue:** Fatema T. Johora, Jörg P. Müller (TU Clausthal; DFG Research Training
  Group SocialCars, GRK 1931) / 2018 / *2018 21st International Conference on Intelligent
  Transportation Systems* (**IEEE ITSC**), Maui, Hawaii, 4–7 November 2018, **pp. 3568–3574**.
- **Link:** doi:[10.1109/ITSC.2018.8569687](https://doi.org/10.1109/ITSC.2018.8569687)
- **Peer-review status:** **published**, peer-reviewed conference proceedings (IEEE). Self-described
  in §V as a "work-in-progress paper".
- **Verified:** **yes — full text.** PDF supplied by the user 2026-10-02 and cached as
  `refs/gt_johora2018_itsc.pdf`. Locators are to numbered sections and the printed page numbers
  3568–3574.
- **Sub-area:** G4 · **Type:** simulation, validated against real observational data ·
  **Category:** ex-ante (both reactive and game-theoretic layers)

> **This is the paper closest to what you want to build.** It is a working crowd-and-vehicle
> simulator in which agents follow explicit rules so that conflicts are avoided, it is validated
> against real video data, and it contains an ablation showing what happens when the rule layer is
> removed. Read this one first.

### The setting, and a definition worth adopting

Shared spaces are mixed-traffic environments — introduced by Hans Monderman in the 1970s — where
"motorized and non-motorized road users share the same space with **equal priority**. Their movements
are **not regulated by traffic rules**, hence they interact more frequently to negotiate priority
over the shared space" (Abstract). Movements are "conducted based on **social protocols** (e.g.
courtesy behavior) and **informal rules** (e.g. colored road surface) instead of traffic regulations"
(§I).

[inference] That is the FYP's setting almost exactly: no formal right-of-way, equal priority,
resolution by informal convention. Where the FYP has a corridor, this has a plaza.

The paper also gives a **formal definition of a conflict**, quoted from Gettman & Head, which the FYP
should adopt because it is inherently ex-ante:

> "an observable situation in which two or more road users approach each other in time and space to
> such an extent that there is a **risk of collision, if their movements remain unchanged**" (§II)

A conflict is therefore a *predicted* collision, not an actual one — so "avoiding conflict" means
acting before the risk materialises. That is precisely your criterion, formalised.

### The gap it addresses (§II)

> "A restriction of the state of the art is that **only single bilateral conflicts are considered**.
> This means that, at a time, each road user can only handle a single conflict with another user, but
> **not all conflicts she is encountering at that time**. These models also do not consider courtesy
> behavior of car drivers for car-car interactions."

### Its taxonomy of interactions (§II) — directly reusable

- **Simple Interaction** — "direct mapping of percepts to actions":
  - *Reactive Interaction*: "When road users do not have time to think or plan their actions, they
    behave reactively."
  - *Car Following* (cars only).
- **Complex Interaction** — "road users need to decide an action among different alternatives":
  - *Implicit Interaction between Two Road Users*: "Each road user chooses her best action to avoid
    conflicts with another user by **predicting their action**."
  - *Implicit Interaction among Multiple Road Users*: e.g. a pedestrian crossing who "needs to
    interact with cars coming from both directions".
  - *Explicit Interaction*: communication — **"we do not consider it in this paper"**.

And **courtesy behaviour** is defined as a crosscutting action: "a road user decelerates and
eventually stops to give priority to others. We model this behavior **both as reactive and complex
interaction**" (§II).

[inference] This taxonomy is worth lifting wholesale into the FYP's design. It says: *most conflicts
should be handled by a cheap local rule; only the genuinely ambiguous ones deserve a solved game.*
That is the right architecture for 10,000 agents, and it is already published and validated.

### The three-layer architecture (§III)

**Layer 1 — Trajectory planning (§III-A).** The environment is converted to a visibility graph and
**A\*** plans a free-flow trajectory per road user. "However, humans keep some distance from
obstacles. Hence, to model this behavior we fine-tune the placement of the inner path vertices
regarding their distance to obstacles."

**Layer 2 — Force-based modelling (§III-B).** The classical **social force model** (Helbing & Molnár
1995), extended with three additional forces. The full equation (§III-B):

```
dv_α(t)/dt = f°_α + Σ f^soc_αB + Σ_{β≠V} f^soc_αV + I^stopping_αβ + I^courtesy_αβ + I^following_αβ
```

where the driving force is `f°_α = (v*_α(t) − v_α(t)) / τ` for relaxation time τ, and the repulsive
social forces are `f^soc_αβ = V°_αβ · exp(−d_αβ(t)/σ) · n̂_αβ · F_αβ` and
`f^soc_αB = U°_αB · exp(−d_αB(t)/R) · n̂_αB`. The three added terms are **reactive rules stated as
explicit angular conditions** — and these are the cheapest conflict-avoidance rules in this whole
review:

- **Car-to-pedestrian reactive interaction (§III-B-a):** "If the nearest conflict of a car driver α
  is with pedestrian(s) β and β has **already started moving in front of α or is very close to α**,
  then α **decelerates to let β pass**. This type of interaction only happens if
  θ_{ē_α n̂_βα} ≤ 15 ‖ θ_{ē_α n̂_βα} ≥ 345."
- **Car following (§III-B-b):** triggers only if the leader is in the follower's movement direction
  (θ ≤ 10 ‖ ≥ 350) and their directions roughly agree (θ ≤ 5 ‖ ≥ 355); the follower maintains
  `p_α = x_α(t) + v̂_β(t)·d_α`, or halves its speed to keep a safe distance.
- **Courtesy behaviour (§III-B-c):** `I^courtesy_αβ = s_current / 2` — "α decelerates and eventually
  stops when β is passing **in front of** α. This type of interaction only happens if
  θ_{ē_α n̂_βα} ≤ 20 ‖ ≥ 340 **and** 70 < θ_{ē_β n̂_βα} < 100 ‖ 260 < θ < 290."

[inference] Note what these are: **`DO : S → A` functions over observable geometry**, exactly the
form Shoham & Tennenholtz define (see [G2](g2-norm-emergence.md), Definition 3.1). The condition is a
pair of angle tests; the action is "decelerate". Nothing is negotiated, nothing is communicated, and
the cost is a couple of dot products. This is the most concrete instance of the FYP's target object
found anywhere in the review.

**Layer 3 — Game-theoretic decision (§III-C).** For complex interactions only:

> "We use **one-shot Stackelberg games**, which are **sequential leader-follower games**, where the
> leader player commits to an action first; then followers choose an action to optimize their utility
> considering the action chosen by the leader. For a single game, restrict the number of leaders to
> one, while there may be one or more followers. For each implicit interaction only one game is
> played and the games are independent of each other. In multiple players game, the leader player
> makes a decision *s_l* by considering the nearest follower and the total number of followers.
> **All followers follow the same action *s_f*.**" (§III-C)

Solved by **subgame perfect Nash equilibrium** via backward induction:
`B_f(s_l) = {s_f ∈ S_f | max(u_f(s_f|s_l))}` and
`SPNE = ⟨{s_l ∈ S_l | max(u_l(s_l, B_f(s_l)))}, B_f(s_l)⟩` (§III-C).

**The action sets (§III-B)** — a discrete, implementable vocabulary:
- **Continue** — cars continue free-flow at previous speed; pedestrians continue at maximum speed.
- **Decelerate** — "road users decelerate and eventually stop".
- **Deviate (pedestrian only)** — the pedestrian "first passes the car β from behind from a position
  *p_α* and then continues moving towards the original destination", with
  `p_α = x_β(t) − 0.5·v_β(t)` if the car keeps moving and `p_α = x_β(t) − v_β(t)` if it stops.
  Cars get no deviate option "because of the non-holonomic constraints of the vehicular movement".

**The payoffs (§III-C-1)** — and this is where the FYP's opportunity is. Outcomes are "ordinally
valued from **2 to −100**" (Figure 2a), with mutual Continue = (−100, −100). The payoff of each action
is a sum of parameters *F₁…F₁₂*, which are switched by **six observable boolean factors**:

| Factor | Condition | Sets |
|---|---|---|
| *x₁* | current speed of β is below normal (*S_current* < *S_normal*) | *F₁, F₆, F₁₁* |
| *x₂* | number of active interactions < *N* (= 2) | *F₂, F₇* |
| *x₃* | **number of give-ways α has already allowed**, *G_α* < *M* (= 3) | *F₃, F₈* |
| *x₄* | α is a car driver **following** another car | *F₄, F₉* |
| *x₅* | α is a pedestrian **in a group** | *F₅, F₁₀* |
| *x₆* | α is a car driver **followed by** another car | *F₁₂* |

Car: Continue = *F₁+F₂+F₃+F₄+F₅*; Decelerate = *F₆+F₇+F₈+F₉+F₁₀*.
Pedestrian: Continue = *F₁+F₉+F₁₀*; Decelerate = *F₆+F₄+F₅*; Deviate = *F₁₁+F₁₂*.

**⚠ And then the authors admit they cannot calibrate it:**

> "As we were not able to determine the parameters *F₁*…*F₁₂* based on a substantial amount of real
> interaction scenarios, there remains a considerable doubt about providing correct values for other
> and more complex scenarios. Hence, while we did perform a sensitivity analysis on a certain amount
> of interaction scenarios and analyzed the behavior of our model, **we do not present the values of
> these parameters in this paper.**" (§III-C-1)

*N* and *M* fared no better: "the parameters *N* and *M* were chosen in a **'trial-and-error' manner**
through simulation experiments" (§III-C-1). And *G_α*, the give-way count, is not even observed —
"We generate the value of *G_α* **randomly**" (§III-C-1).

**Conflict recognition (§III-D).** Simple interactions are handled **locally**: "simple interactions
are dealt with by local action and **does not require synchronization or communication**. If a simple
interaction situation is detected by a road user within its **FOV (set to 180° in this paper)**, it is
classified based on the interaction angle... and the corresponding action is performed." Complex
interactions go to "a (virtual) central mediation entity, further referred to as **host agent**",
which picks the **faster agent (the car) as leader** and organises a game with that leader and its
followers only — and the stated reason is computational: otherwise "the host may need to consider
**all possible subsets of conflicts as one game (worst-case scenario)** which will make the situation
more complex."

### The evaluation, in detail

- **Data:** **117 conflict scenarios** drawn from video of a real shared-space area in **Hamburg**
  (dataset from Pascucci et al.), with real road-user trajectories (§IV).
- **Implementation:** **LightJason**, a Java-based BDI multi-agent framework; runs on an Intel Core
  i5 with 16 GB RAM (§IV).
- **Scenario 1** — three pedestrians and one car. The car decelerates to let them cross; the model
  reproduces this **reactively** (the ≤15°/≥345° rule fires). "in both simulation and reality, the
  car driver decelerates; yet, the timing and the way of acting differ in both cases: The
  acceleration and deceleration of simulated car driver is **sharp** compare to real car driver. The
  mechanism of speed handing of cars in our model need to be improved." (§IV-a)
- **Scenario 2** — Car2 vs Ped4 & Ped5; Car3 and Car4 following Car2; Car4 vs Ped6. Both cars
  decelerate. "both Car2 and Car4 act as leader and decide to decelerate; their payoff function
  reflects **courtesy** of the drivers towards the pedestrians, as decelerating will maximize its
  value." (§IV-b)
- **⚠⚠ THE ABLATION — the single most useful experimental result in this file.** They re-ran
  Scenario 2 **with the game-theoretic layer switched off**, leaving only the social force model:

  > "In Figure 5e **all cars deviate from their trajectory instead of stopping and pedestrians
  > sometimes go back and forth and sometimes stop.**" (§IV-b)

  [inference] "Pedestrians sometimes go back and forth" **is the deadlock dance** — the same failure
  Camara et al. describe as two polite road users dodging side to side. This is a published,
  controlled demonstration that **removing the rule layer reproduces exactly the stall the FYP exists
  to eliminate, and adding it back fixes it.** If you need one citation for "why a conflict rule is
  necessary in a crowd simulator", this is it.
- **Scenario 3** — car-to-car courtesy: "when the driver of the blue car perceives the green car, she
  slows down and lets the green car pass first." Handled reactively. No real data available for
  comparison (§IV-c).
- **Aggregate validation (§IV):** real vs simulated trajectories for all 117 scenarios (Figures 7a,
  7b). "The trajectories of real and simulated road users **closely match**. However, the time step
  wise position of each road user differs... because of speed difference between real and simulated
  road users and also the fact that a **large safety distance is maintained between road users in
  simulation**."
- **⚠ The calibration gap, in their own numbers (§IV):** mean and SD of speed —
  simulated cars **2.779 / 2.966**; simulated pedestrians **0.8469 / 0.7813**; real cars **1.27 /
  1.007**; real pedestrians **0.502 / 0.2526**. So simulated agents move roughly **twice as fast as
  the real ones they are validated against**, with much higher variance. "The calibration of the
  acceleration and deceleration parameters is a part of our future work." Figure 8a shows pedestrian
  trajectory error clustering low but **car trajectory error with a median around 17 m and a tail to
  ~40 m**.

### Research gaps

**Stated by the authors (§V):**
- "Future research will focus on **calibrating and validating the model parameters using genetic
  algorithms**."
- "Next, we will try to find out **other factors** which might influence road users decision making."
- "The **explicit interaction** and **pedestrian group dynamic** will be integrated into our
  simulation model."
- **⚠ Scalability, stated as the top priority:** "**Most importantly, we shall study larger scenarios
  with larger numbers interactions. Doing so, we shall explore the scalability of various interaction
  types** for different scenarios varying in number and heterogeneity of users as well as in topology.
  In particular, **more efficient algorithms for recognizing, framing and resolving conflicts
  interactions will be required** for realistically simulating larger shared space scenarios."
- Within the model: follower-to-follower and follower-to-other-agent conflicts are explicitly out of
  scope of a single game (§III-D).

**Gaps I identify** — all `[inference]`:
- **The 12 payoff parameters are the hole in the middle of the paper**, and the authors say so. The
  model is otherwise complete and validated.
- **No demographics at all.** The six factors are situational (speed, group, following) and not
  personal — no age, gender or mobility. Yet *x₅* ("pedestrian in a group") shows the framework
  already accepts a per-agent social attribute, so adding demographic factors is a small extension,
  not a redesign.
- **Agents are homogeneous within type.** Every pedestrian uses the same *F* values.
- **The host agent is centralised.** It collects conflicts across the whole environment each cycle.
  At 10,000 agents that is a bottleneck the paper never tests — and it is the same thing their own
  future-work paragraph flags.

### How it helps this FYP

1. **It is your architecture, already published and validated.** Three layers — plan, reactive
   forces, game-theoretic decisions — with the cheap reactive rules carrying most of the load and
   solved games reserved for genuine ambiguity. Adopt this and the FYP's structure is defensible on
   day one.
2. **⚠ It hands you a precisely-shaped contribution.** The paper has a 12-parameter payoff function
   keyed to six observable factors, and **openly cannot calibrate it** (§III-C-1). The authors'
   proposed fix is genetic algorithms (§V). **The FYP's alternative is to elicit those payoffs from an
   LLM, per persona and per scenario.** That is a direct, publishable comparison — *GA-calibrated vs
   LLM-elicited payoffs on the same model and the same 117 Hamburg scenarios* — and it reuses an
   existing validated simulator instead of building one. Note how well the factors suit an LLM:
   *G_α* (how many times have I already given way?), group membership, being followed — these are
   social-context judgements, which is what an LLM is actually good at, and *G_α* is currently
   **generated randomly**.
3. **It gives you the ablation you will need in your own evaluation.** Run with the rule layer, run
   without, show the dithering returns. The method is already demonstrated in §IV-b.
4. **It supplies the discrete action vocabulary** — {continue, decelerate, deviate} — which maps
   cleanly onto `dataset/action_space.yaml` and is far more tractable than free-text behaviour.
5. **It states the scalability problem you are trying to solve**, in the conclusion of a peer-reviewed
   paper, as that paper's own top priority for future work. That is a strong justification sentence
   for your introduction.

---

## A3. [Duffy-CorrelatedEq]: Correlated Equilibria, Good and Bad: An Experimental Study

- **Authors / Year / Venue:** John Duffy (University of Pittsburgh), Nick Feltovich (University of
  Aberdeen Business School) / 2010 / *International Economic Review* **51**(3), August 2010,
  **pp. 701–721**. Manuscript received July 2008; revised January 2009.
- **Link:** doi:[10.1111/j.1468-2354.2010.00598.x](https://doi.org/10.1111/j.1468-2354.2010.00598.x)
- **Peer-review status:** **published**, peer-reviewed journal (Wiley).
- **Verified:** **yes — full text.** PDF supplied by the user 2026-10-02 and cached as
  `refs/gt_duffy2010_ier.pdf`. Locators are to the printed page numbers 701–721.
  *(This entry supersedes the abstract-only entry in [G1](g1-conflict-games-conventions.md).)*
- **Sub-area:** G1 · **Type:** human experiment · **Category:** ex-post (resolution by signal)

### The game and the concept

The game is **Chicken** (Figure 1, p. 702), chosen because it is "perhaps the simplest game with the
property that there exist correlated equilibrium payoff pairs that lie outside the convex hull of
Nash equilibrium payoff pairs" (§2, p. 703). Strategies are **defect (D)** and **cooperate (C)**:

| | **D** | **C** |
|---|---|---|
| **D** | 0, 0 | 9, 3 |
| **C** | 3, 9 | 7, 7 |

Three Nash equilibria: (D,C) → (9,3); (C,D) → (3,9); and mixed, each playing D with probability 2/5
→ (5.4, 5.4) (§2, p. 704).

**The correlated-equilibrium mechanism, as implemented (p. 704).** A "mediator" — a non-strategic
third party — "chooses one of the four pure-strategy profiles according to a commonly known
probability distribution, and to each player 'recommends' that player's component in the profile.
(The mediator never recommends a mixed strategy.) The probability distribution is a correlated
equilibrium of the original game **if each player at least weakly prefers following her recommended
action to choosing any other action**." For this game the incentive conditions reduce to four linear
inequalities (p. 704): 2*p_DC* ≥ 3*p_DD*; 3*p_CD* ≥ 2*p_CC*; 2*p_CD* ≥ 3*p_DD*; 3*p_DC* ≥ 2*p_CC*,
with the four probabilities summing to 1.

[inference] This is the cleanest statement in the whole review of what a signal-based avoidance rule
actually costs: **a trusted device, a publicly known distribution, and a private per-agent signal.**
A simulator can supply all three trivially — it *is* the mediator.

### The experiment, in detail

**Design.** Four recommendation distributions, each a separate between-subjects treatment
(Table 1, p. 707):

| Treatment | p(D,D) | p(D,C) | p(C,D) | p(C,C) | Expected payoffs | Is it a CE? |
|---|---|---|---|---|---|---|
| **Good** | 0.000 | 0.333 | 0.333 | 0.333 | (6.333, 6.333) | Yes — beats every symmetric Nash-hull payoff |
| **Bad** | 0.200 | 0.400 | 0.400 | 0.000 | (4.8, 4.8) | Yes — but **worse** than every symmetric Nash-hull payoff |
| **Nash** | 0.000 | 0.500 | 0.500 | 0.000 | (6, 6) | Yes — a convex combination of Nash equilibria |
| **Very good** | 0.000 | 0.100 | 0.100 | 0.800 | (6.8, 6.8) | **No** — not a CE, but highest payoffs of all |
| *(mixed NE, for reference)* | 0.160 | 0.240 | 0.240 | 0.360 | (5.4, 5.4) | — |

The *bad* treatment is novel: "As far as we know, there are no existing experimental studies of
correlated equilibria that are payoff-reducing relative to Nash equilibrium" (p. 706). The *very
good* treatment is the control for experimenter demand — it looks attractive but is not an
equilibrium, so "a player receiving a D recommendation will prefer to follow it... but a player
receiving a C recommendation will not, instead preferring to choose D" (p. 707).

**Procedure (§3, pp. 707–708).**
- **16 sessions** (4 per treatment) × **12 subjects** = **192 subjects**; **7,580 observations**,
  1,920 per treatment.
- Each session is **40 rounds: 20 with recommendations, 20 without**, with the order counterbalanced
  across sessions. So recommendations are varied *within* subject; treatment type *between* subjects.
- Subjects were "primarily undergraduate students from University of Pittsburgh", recruited by
  newspaper advertisements and e-mail; nobody participated twice.
- Instructions read aloud "in an attempt to make the rules of the game common knowledge", followed by
  a **comprehension quiz** graded anonymously, with wrong answers discussed aloud.
- **Deliberately neutral framing** (p. 708): "Instead of relatively loaded terms such as 'opponent'
  or 'partner,' we used phrases such as 'the player matched with you.'" Actions were labelled **X and
  Y, not D and C**. And crucially: "we never went so far as to instruct subjects to follow
  recommendations, or even to point out that following recommendations might lead to higher payoffs;
  rather, we merely provided the outcome distribution." One quiz item read: "You are required to
  follow the recommendations shown on your computer screen (circle one): TRUE **FALSE**".
- Run in **z-Tree**; **round-robin matching** "in an attempt to minimize incentives for reputation
  building"; no identifying information about opponents in any round.
- Payment: one round from each half chosen at random, $1 per point, plus a $5 show-up fee; average
  total ≈ $15; sessions 45–60 minutes.

### Findings

**Result 1 (p. 712).** "When no recommendations are given, aggregate outcome frequencies are broadly
similar to mixed-strategy Nash equilibrium frequencies... When recommendations are given, they lead
to significant differences in aggregate outcome frequencies... **if and only if the recommendations
come from a correlated equilibrium.**"

Supporting numbers (Table 2, p. 709): the pure-strategy-Nash outcome rate rises from **49.7%** with no
recommendations to **56.5%** (Nash recs) and **57.9%** (good recs), but *falls* to 48.1% (bad) and
46.9% (very good). The mutually destructive (D,D) outcome falls to 11.3% (Nash) and 14.0% (good) from
15.9% (none), but rises to 19.2% (bad) and 16.9% (very good).

**The striking null (p. 711).** There is no significant difference between *no recommendations* and
*very good recommendations* (χ² = 3.511, df = 3, p > 0.20):

> "The finding of no difference between no recommendations and very good recommendations is striking:
> It suggests that **subjects will not blindly follow just *any* recommendations, but rather will
> follow them only if they are consistent with implementation of a correlated equilibrium.**"

**Result 2 (p. 715).** "Subjects are most likely to follow recommendations in the good- and
Nash-recommendations treatments. In the bad-recommendations treatment, recommendations have less
effect on behavior. In the very good-recommendations treatment, subjects either don't follow
recommendations at all or **learn over time not to follow them**." Following rates (Table 3, p. 713),
against a mixed-NE baseline of 0.400 for D and 0.600 for C: good — **0.735 / 0.732**; Nash — **0.567
/ 0.777**; bad — 0.477 / 0.631 (not significant overall); very good — 0.511 / 0.608, with D-following
collapsing to **0.227** in the last five rounds.

**Result 3 (p. 716).** Following is history-dependent: "The more successful following recommendations
has been in the past... the more likely a subject is to follow recommendations in the current round."
But the authors caution that "the low pseudo-*R*² values suggest that past success is only a minor
factor."

**Result 4 (p. 719).** Following pays, but only where the distribution is a sensible CE. Forgone
payoffs averaged **−0.467**/round (good) and **−0.428**/round (Nash), both significantly below zero;
but +0.026 (bad) and +0.059 (very good), neither significant. Spearman correlations between
following-frequency and forgone payoff: −0.312 (good, p ≈ 0.02) and −0.469 (Nash, p < 0.001); ≈ 0 in
the other two.

**The three lessons the authors draw (pp. 719–720).**
1. "it is **not necessary for recommendations always to be followed** in order for them to have an
   effect. Recommendations in these treatments were followed only roughly **70%–75%** of the time, but
   this was enough to have a significant effect on the distribution of outcomes."
2. "correlated equilibrium is likely a **necessary condition** for recommendations to have any
   substantial effect on behavior."
3. "it is particularly difficult to induce subjects to follow recommendations based on correlated
   equilibria that are **Pareto inferior** to the available Nash equilibria. This finding would seem
   to **greatly limit the class of empirically relevant correlated equilibria to those that Pareto
   improve upon the set of Nash equilibria.**"

**⚠ And the negative result that matters most to this FYP (p. 719):**

> "when subjects do not receive recommendations, their choices can be described fairly well... by
> mixed-strategy Nash equilibrium. This result suggests that **theoretical rationales for correlated
> equilibria that do not rely on extrinsic, third-party recommendations... might be difficult to
> observe in practice** — though we acknowledge the possibility that if subjects had interacted in
> **fixed pairings** instead of under the random matching protocol we adopted, or had opportunities
> for **communication**, then spontaneously arising correlated equilibrium might have been more
> likely to have been observed."

[inference] In plain terms: **humans did not invent the coordinating signal for themselves.** Left
alone with strangers, they played the inefficient mixed equilibrium. The convention had to be handed
to them. This corroborates, from a completely different literature, the finding already recorded in
[G2](g2-norm-emergence.md) that conventions do not emerge spontaneously under unfavourable
interaction structure — and it is another argument for the FYP's offline-extraction design.

### Research gaps

**Stated by the authors (pp. 719–720):**
- "our results cast a bit of doubt on the usefulness of this solution concept as a descriptive notion,
  as the correlated equilibrium **point predictions are not observed**" — directional predictions
  hold, point predictions do not.
- An alternative explanation they could not rule out (footnote 19, p. 720): following rates may track
  **how easy Bayes' rule is** in each treatment. Posterior probabilities are 0, 0.5 or 1 in the good
  and Nash treatments but 1/3, 2/3, 1/9 or 8/9 in the others; "the increased cognitive requirements
  involved in calculating expected payoffs using these latter fractions might have pushed frequencies
  of following recommendations toward one-half."
- A framing caveat (footnote 11, p. 708): "We acknowledge the possibility that our use of the term
  '**recommendations**' itself might have influenced subjects to follow them to some extent."
- Future work: a **strategic** mediator whose own payoff depends on the players' payoffs (p. 720).
- **⚠ And an open question that is almost a project brief for this FYP** (p. 720):

  > "A second useful extension would be to consider some '**language**' issues as they apply to
  > correlated equilibrium. For instance, one might wonder whether **the form of recommendations
  > matters**: for example, whether subjects are told, 'It is recommended that you play C,' as in our
  > design, or they simply see the message 'C' on their screens. The salience and literal meanings of
  > recommendations are also of interest: **Must the message space for recommendations correspond
  > precisely to the action space**, or might it be larger (for example, including also 'no message')
  > or consist of a set of messages with no clear mapping to the action space (such as the message
  > space {@, &})?"

**Gaps I identify** — `[inference]`:
- **No demographics.** 192 subjects, no age or gender breakdown reported.
- **Abstract game only.** Chicken with points; nothing spatial, no movement, no time pressure.
- ⚠ **Two citation errors in the reference list** (p. 721), noted because this review's whole method
  is independent verification: Gul is cited in the body as "Gul (1988)" (p. 702) but listed as
  *Econometrica* **66** (1998); and Hart & Mas-Colell's "A Simple Adaptive Procedure Leading to
  Correlated Equilibrium" is listed as *Econometrica* **60** (2000) — volume 60 is 1992, the 2000
  paper is volume 68. Use Crossref, not this list, if you cite either.

### How it helps this FYP

1. **It is the human-validation leg** for signal-based conflict avoidance — the only human experiment
   in the whole review that tests a correlated-equilibrium rule in a genuine conflict game.
2. **It gives you a realistic compliance figure.** 70–75% following was enough to shift outcomes
   significantly (p. 719). [inference] So the FYP does **not** need every agent to obey the extracted
   rule for the simulation to behave differently — a useful bar to set, and one you can cite.
3. **⚠ It constrains which rules are worth extracting.** Humans follow a recommendation only if it is
   a correlated equilibrium *and* payoff-improving on the Nash alternatives (Results 1 and 4, and the
   "greatly limit the class" conclusion). A rule the LLM proposes that makes agents worse off than
   just muddling through will be ignored by humans — so if the FYP wants its rule to be behaviourally
   plausible, it has to check that the rule actually pays.
4. **⚠ It tells you the signal must be supplied, not discovered.** No correlated equilibrium arose
   spontaneously (p. 719). The FYP must install the convention; it cannot expect agents to find it.
5. **The "language issues" open question (p. 720) is a direct invitation.** The authors ask whether
   the *form* of a recommendation matters and whether the message space must match the action space.
   **An LLM is precisely a device that issues recommendations in natural language over an unbounded
   message space.** [inference] This is the single cleanest "the literature asked for this, we did it"
   framing available to the FYP, and it also connects to the strategy-label presentation dispute
   recorded in [G5](g5-llm-agents-game-theory.md) §2 (Objection 5).

---

# Part B — the already-reviewed papers that meet the criterion

Compact entries. Full per-paper templates are in the sub-area files.

### B1. [Shoham-SocialLaws] — AAAI-92, pp. 276–281 · **ex-ante** · full entry in [G2](g2-norm-emergence.md)
**The reference case.** A *social law* is a set of (action, condition) prohibitions (Def. 2.1); a
*legal plan* is a total function **`DO : S → A`** from the agent's own state to an action (Def. 3.1).
The motivating example *is* your question: "Why not adopt a convention... according to which each
robot keeps to the right of the path? **If each robot obeys the convention, we will have avoided all
head-on collisions** without any need for either a central arbiter or negotiation" (§1).
**Experiment:** none — it is a formal/complexity paper. **Findings:** designing such a law is
NP-complete (Thm 3.1), but "computed **off-line**" (§3), so runtime is one function evaluation;
polynomial under bounded fan-out and two further restrictions (Thm 4.2). **Gap:** assumes universal
compliance and a finite enumerable state space; no empirical work at all. **For the FYP:** this is
the formal type of your deliverable and the scalability argument for 10,000 agents.

### B2. [Foley-ConflictConvention] — *J. R. Soc. Interface* 15:20170835 (2018) · **ex-ante** · [G1](g1-conflict-games-conventions.md)
**Rule:** condition your action on **one bit** — am I host or visitor? — giving either the *bourgeois*
(aggressive at home) or *paradoxical/host–guest* (aggressive away) convention. The paper's own words:
these "effectively **avoid any conflict** between aggressive hawk strategies" (§3). **Experiment:**
agent-based simulation in C++, 10⁶ rounds, exhaustive sweep of the conflict payoff space.
**Findings:** conventions emerge from reinforcement learning with no beliefs about others (§2.1, §4);
dynamics are insensitive to population size from **20 to 2000** (§3); the **host–guest** norm — the
one already there *concedes* — "evolves far more readily" than ownership (§4). **Gaps:** no human
data; no resource scarcity; the cue must be supplied by the environment. **For the FYP:** proof that
one bit of role asymmetry is enough, plus the offline-learn / online-apply split. And a warning: the
convention that evolves is the **opposite** of first-come-first-served.

### B3. [Fox-SequentialChicken] — VEHITS 2018, pp. 431–439 · **ex-ante** · [G4](g4-game-theoretic-crowd-models.md)
The model that [Camara-EmpiricalGT] fits to humans. **Rule:** a precomputed strategy over
(*y*, *x*, *t*) — and, under a mild approximation, over (*y*, *x*) alone — selected among multiple
equilibria by a novel refinement, *meta-strategy convergence*. **Information:** both positions, plus
commonly known identical utilities. **One-shot with no history** (Abstract) — the only fully-read
entry designed for strangers meeting once. **Finding/gap:** optimal play "must include a non-zero
probability of allowing a collision to occur" (Abstract). **For the FYP:** the cheapest runtime rule
in the review, and an honest negative result to inherit.

### B4. [Bonnemain-GamePlayers] — *Phys. Rev. E* 107:024612 (2023) · **ex-ante** · [G4](g4-game-theoretic-crowd-models.md)
**Rule:** move down the gradient of a value function, `a*(t,x) = −∇u(t,x)/μ`, with *u* and the crowd
density *m* solving a coupled HJB/Fokker–Planck pair (§2). **Experiment:** compared against
**controlled human experiments**, density-matched at 2.5 ped/m², reproducing transverse displacements
that force-based models miss (Abstract; fig. 1 col. 4). **Finding you should quote** (§1): explicit
*N*-agent game theory "becomes **intractable when the number of interacting agents grows**" — solved
by reducing to two PDEs whose cost is independent of *N*. **Gap for you:** the mean-field step
**averages the agents away**, destroying the personas you need, and it answers "how do I move", not
"who goes first".

### B5. [Bouzat-RoomEvacuation] — *Phys. Rev. E* 89:032806 (2014) · **ex-post** · [G4](g4-game-theoretic-crowd-models.md)
**Rule:** when 2–4 agents contend for the same lattice cell, a win-probability matrix keyed on their
cooperate/defect labels picks a winner — C vs C = ½ each; C vs D = 0 and 1/*P*; D vs D = 1/(2*P*) —
and sometimes **nobody** moves. **Finding:** "even when defecting is the rational choice for any
agent, under certain conditions, cooperators can take advantage from mutual cooperation and leave the
room more rapidly than defectors" (Abstract). **Gap / opportunity:** the C/D label is assigned
arbitrarily at the start and never justified — the same shape of opening as Johora & Müller's
uncalibrated *F* parameters, and the FYP could fill both with LLM-elicited values.

### B6. [Camara-PedestrianModelsII] — *IEEE T-ITS* 22(9):5453–5472 (2021) · survey · [G4](g4-game-theoretic-crowd-models.md)
Not a rule — the map of the area, and the source of the **2% explicit-signalling** figure
(§IV-B-1): in naturalistic observation, mutual eye contact occurred in only 13% of interactions and
explicit signalling in 2%. That is your best empirical justification for building a
communication-free rule at all.

---

## What to do with all this — the short version

[inference], built on the sourced statements above.

1. **Build the three-layer architecture from [Johora-SharedSpaces] §III.** Cheap reactive angular
   rules for the common cases, a solved game only for genuine ambiguity, trajectory planning
   underneath. It is validated against 117 real scenarios and it already works.
2. **Make the uncalibrated payoffs your contribution.** Johora & Müller cannot set their *F₁…F₁₂*
   (§III-C-1) and propose genetic algorithms (§V); Bouzat & Kuperman assign C/D labels arbitrarily;
   Fox et al. leave (*U_crash*, *U_time*) free and Camara et al. need 16 people around a table to
   estimate one ratio. **Every one of these models has a parameter-shaped hole, and an LLM queried
   per persona is a candidate filler for all of them.** That is a much sharper contribution than
   "LLMs understand human behaviour".
3. **Use [Johora-SharedSpaces] §IV-b as your evaluation template.** Run with the rule layer, run
   without, and show the dithering comes back. It is the published demonstration that the rule layer
   is what prevents the stall.
4. **Carry three warnings into the report, each with a citation:**
   - A rule of "always yield" is self-defeating — other agents learn to exploit it
     ([Camara-EmpiricalGT] Abstract, with the La Rochelle/Trikala minibus evidence, §1), and symmetric
     politeness causes its own deadlock (§1).
   - A communication-free position-only rule cannot be collision-free
     ([Fox-SequentialChicken] Abstract).
   - **Game-like framing distorts elicited preferences.** A board game drove the measured crash cost
     to zero ([Camara-EmpiricalGT] §4). A text prompt to an LLM is at least as artificial a frame.
5. **Answer Duffy & Feltovich's open "language" question** (p. 720). They ask whether the *form* of a
   recommendation matters and whether its message space must match the action space. An LLM is a
   natural-language recommendation device. That is a clean, citable motivation for the whole project.

---

**Draft status: pending supervisor review.** Decisions needed: whether to adopt the Johora & Müller
three-layer architecture as the FYP's implementation target, and whether to reframe the contribution
as *LLM-elicited calibration of existing validated conflict models* rather than as a new model.
