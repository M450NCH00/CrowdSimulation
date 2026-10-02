# Candidate rule catalogue — runtime conflict-resolution rules found in the literature

> ## ⚠ DRAFT — PENDING SUPERVISOR REVIEW
> Nothing in this file is settled. In particular, the **"Implementable in a generic simulator"**
> column is my judgement, marked `[inference]` throughout, and the **apparent correspondences**
> noted in §2 are explicitly *not* merged — whether two similarly-shaped rules are the same rule is
> a judgement requiring sign-off.

Prepared for issue [#20](https://github.com/M450NCH00/CrowdSimulation/issues/20). This is the payoff
artefact of that issue. Sub-area files:
[G1](g1-conflict-games-conventions.md) ·
[G2](g2-norm-emergence.md) ·
[G3](g3-cheap-talk.md) ·
[G4](g4-game-theoretic-crowd-models.md) ·
[G5](g5-llm-agents-game-theory.md) ·
[G6](g6-transfer-across-games.md) ·
[search log](search-log.md) · [refs](refs-game-theory.bib)

## Rules of this file (from the issue, restated so they can be checked)

1. **Every row cites a source.** No row states a rule that no paper states.
2. **No row generalises a paper's rule beyond what the paper claims.** Where I extend a rule to the
   FYP's setting, that extension lives in the "Implementable" column marked `[inference]`, never in
   the rule statement itself.
3. **No two rules are merged.** Where two papers give versions of the same rule under different
   names, both rows appear and the apparent correspondence is noted separately in §2.
4. **Only rules I read at source are listed.** A rule known to me only through another paper's
   summary is in §3, not in the table.

---

## §1. The catalogue

| # | Rule (name and one-line statement) | Source (paper, locator) | Game it resolves | Information required | One-shot? | Communication needed | Validated against humans? | Implementable in a generic simulator? |
|---|---|---|---|---|---|---|---|---|
| **R1** | **Bourgeois** — play aggressive when you are the host (the one visited), passive when you are the visitor. | [Foley-ConflictConvention], *J. R. Soc. Interface* 15:20170835, §1 ("they play hawk when hosting and dove when visiting") and §3 (payoffs to each role) | Hawk–Dove / snowdrift / chicken, 2 parties (§1, figure 1*a*) | **One bit: am I host or visitor?** Role is "the public cue" (§1). No beliefs about the other agent needed (§2.1, §4) | **No** as a *convention* — acquired over 10⁶ rounds (Data Generation). **Yes** as an *application* once established (§3) | **None** — no messaging anywhere in the model (§2.1) | **No** (this paper). Correlated equilibria "are also readily learned by humans" is cited to others (§1) | **Yes** `[inference]` — one bit of role state, one table lookup. But the simulator must *define* the role; a corridor has no built-in host/visitor |
| **R2** | **Paradoxical (host–guest)** — play passive when you are the host, aggressive when you are the visitor. The host concedes. | [Foley-ConflictConvention], §1 ("one plays dove when hosting and hawk when visiting") and §4 ("a host–guest norm, where the host concedes resources to a visitor, evolves far more readily") | Same as R1 | Same as R1 | Same as R1 | **None** | **No** directly; the paper calls it "a phenomenon common to human interaction" (Abstract) | **Yes** `[inference]` — identical cost to R1. Listed separately because it is a **different rule with the same information requirement**, and the paper's central result is that these two are *not* equally likely |
| **R3** | **Correlate on an external cue** — both parties condition their action on a shared public signal (e.g. a coin toss), e.g. "player one plays hawk when heads, dove otherwise; player two plays hawk when tails, dove otherwise". | [Foley-ConflictConvention], §1, quoted verbatim | Any game of conflict meeting the figure 1*a* payoff ordering (§1) | **A signal observed by both parties**, plus a fixed mapping from signal to action | **Yes** — the cue is per-encounter; no history needed | **None** — the cue is not a message between players | **No** in this paper | **Yes** `[inference]` — a simulator can trivially broadcast a shared random signal. This is the most *generic* rule in the table and the least tied to space |
| **R4** | **Private recommendation from a trusted device** — a non-strategic mediator draws a pure-strategy profile from a publicly announced distribution and privately recommends each party its own component. | [Duffy-CorrelatedEq], *Int. Econ. Rev.* 51:701–721, pp. 704, 707 (**full text**) | **Chicken**, 2 parties; payoffs (D,D)=0,0 (D,C)=9,3 (C,D)=3,9 (C,C)=7,7 (fig. 1, p. 702) | **A private signal** per agent, **public knowledge of the distribution**, and a **trusted third party** to draw it (p. 704) | **Yes** per round; round-robin matching, so no dyad history (p. 708) | **None between the players** — the recommendation comes from a third party | **YES** — **192 subjects**, 7,580 observations (p. 708). Recommendations shift outcomes "if and only if the recommendations come from a correlated equilibrium" (Result 1, p. 712); compliance **70–75%** was enough to matter (p. 719) | **Yes** `[inference]` — the simulator *is* the trusted device. ⚠ Two constraints: the rule must be **payoff-improving on Nash** or people ignore it (p. 720), and **no CE arose spontaneously without the mediator** (p. 719) |
| **R5** | **Defer to the higher RHP** — where resource holding potential (relative likelihood of winning a fight) is known, the lower-RHP party yields; a stable dominance relationship results. | [Hall-IteratedHawkDove], *J. Theor. Biol.* 493:110101, **read via arXiv:1907.02160v2**, Abstract and §3 ("Analysis of strategies for animals with knowledge of p_A") | Iterated Hawk–Dove, 2 parties (§2) | **Relative RHP of both parties.** §3 assumes it is known; §4 is the case where it is not | **Yes, if RHP is observable.** **No** if it must be assessed — assessment costs a "limited period" of fighting (Abstract, §4) | **None** — assessment is by fighting, not signalling (§2, §4) | **No** — animal-behaviour model, no data fitted | **Yes, conditionally** `[inference]` — only if the simulator exposes a comparable per-agent attribute. This is the natural hook for the FYP's personas, but the rule is only one-shot if the attribute is visible without a fight |
| **R6** | **Threshold aggregation** — take the collective action only if at least a fraction *T* of those present are of your own type; otherwise retreat. | [Chen-NPersonHawkDove], *Sci. Rep.* 7:4800, **read via arXiv:1702.03969**, preprint eq. (6) region: "If the fraction of doves exceeds or equals the threshold (n_D/N ≥ T), the doves expel the hawks, paying a cost c_D" | **N-person** Hawk–Dove, arbitrarily many parties (Introduction) | **A local count**: *n_D*/*N* among co-present agents, i.e. how many of those present share my strategy | **Yes** per encounter (the threshold is evaluated per group) | **None** stated | **No** — animal framing, no data fitted | **Yes** `[inference]` — a neighbourhood count is a standard simulator primitive. The only rule in the table that is natively **multi-party** by design |
| **R7** | **Social law / legal plan** — a total function `DO : S → A` from the agent's own observable state to an action, constrained by a set of prohibitions fixed offline. Canonical instance: *keep to the right*. | [Shoham-SocialLaws], AAAI-92 pp. 276–281, **Definition 3.1** (the function), **Definition 2.1** (the law as (action, condition) pairs), §1 (the keep-right example) | **Any** conflict over shared state; not payoff-based; arbitrarily many parties (§1) | **The agent's own current state `s`, and nothing else** (Definition 3.1). Requires that all agents adopted the same law in advance (§1) | **Yes** — stateless, no history (Definition 3.1) | **None.** "we will have avoided all head-on collisions without any need for either a central arbiter or negotiation" (§1) | **No** — formal/complexity paper, no empirical work | **Yes, and this is the reference case** `[inference]` — the rule *is* a state→action function, which is the issue's own implementability test. Offline synthesis is NP-complete (Theorem 3.1) but "computed off-line" (§3); runtime cost is one evaluation |
| **R8** | **Sequential-chicken equilibrium via meta-strategy convergence** — from the joint state (own distance, other's distance, elapsed time), select a speed from the equilibrium set using the meta-strategy convergence refinement. | [Fox-SequentialChicken], VEHITS 2018 pp. 431–439, §2 (model and recursion, pp. 432–433; meta-strategy convergence, p. 433) | **Sequential chicken** at an unsigned intersection / jaywalking crossing, 2 parties (Abstract, §2) | **Both parties' positions (y, x) and elapsed time t**; plus identical, commonly known utilities (§2, p. 433) | **Yes, explicitly** — "real-time selection from multiple equilibria **with no history**" (Abstract) | **None.** Intent is signalled by position only (Abstract) | **Yes, via [Camara-EmpiricalGT]** (now read in full): 16 participants, 8 pairs, 48 board-game runs, **13 collisions**; fitted optimum (*U_crash*, *U_time*) ≈ **(0, 30)** (§2.2, §3) | **Yes** `[inference]` — solvable offline into a lookup table over (y, x, t). ⚠ Carries the paper's own negative result: "optimal behaviors for both agents **must include a non-zero probability of allowing a collision**" (Abstract) |
| **R9** | **Strategy-dependent cell contention** — when *k* agents contend for the same cell, the winner is drawn from a win-probability matrix keyed on the contenders' cooperate/defect labels; C vs C = ½ each, C vs D = 0 and 1/P, D vs D = 1/(2P) each; and with some probability **no one** moves. | [Bouzat-RoomEvacuation], *Phys. Rev. E* 89:032806, **read via arXiv:1311.1708v1**, §"Second stage: solving the conflicts" (matrix and its three-part reading, verbatim) | **Cell contention in a lattice-gas evacuation**, "two, three or four agents" per conflict (§Second stage) | **Each contender's C/D label** and the set of contenders for that cell | **Yes** — each contention resolved independently, no memory | **None** | **No** — no human data fitted | **Yes — the most directly transferable rule found** `[inference]` — it is already written as a simulator conflict-resolution subroutine, multi-party, with a single tunable parameter *P*. ⚠ But the C/D label is an **exogenous assumption**, not a result (see §4) |
| **R10** | **Act on the announced type pair, with the High type compromising** — after simultaneous two-sided revelation of private types, actions depend on the announced pair; in the fully revealing equilibrium "the High-type is expected to compromise". | [Ganguly-BoSCheapTalk], *Int. J. Game Theory* 52:957–992, Abstract and §1, p. 961 | **Battle of the Sexes** with two-sided private information — an anti-coordination conflict game, 2 parties (§1, p. 959) | **Own type + the other's simultaneous announcement**; in a simulator, the observable type pair | **Yes** — single pre-play stage plus a single simultaneous move | ⚠ **Pre-play only** — one round of *simultaneous* cheap talk. Fails under one-sided **and** under sequential communication (Abstract) | **No** in this paper; it positions itself against an existing experimental literature (§1, p. 959) | **Yes, with the talk stage removed** `[inference]` — a crowd simulator *assigns* types, so revelation is unnecessary and the residual object is a function of the observable type pair |
| **R11** | **Mean-field optimal drift** — move down the gradient of the value function, `a*(t, x) = −∇u(t, x)/μ`, where *u* solves an HJB equation coupled to a Fokker–Planck equation for the crowd density. | [Bonnemain-GamePlayers], *Phys. Rev. E* 107:024612, **read via arXiv:2201.08592**, §2 (system (3) and the optimal control expression) | **Dense static crowd crossed by an intruder**; whole crowd, mean-field limit (Abstract, §1) | **Local value-function gradient and local crowd density** — a field, not any neighbour's identity or type (§2) | Neither — a single continuous-time optimal-control problem with anticipation over a horizon (§2, forward–backward structure) | **None** — coordination is mediated entirely by the density field | **YES** — compared against controlled experiments, density-matched at 2.5 ped/m², reproducing transverse displacements that other models miss (figure 1 column 4 and caption; Abstract) | **Partly** `[inference]` — cost is independent of *N* (§2), which is why it scales. ⚠ But it answers *how do I move*, not *who goes first*, and the mean-field step **averages agents away**, destroying the personas the FYP needs |
| **R12** | **Stackelberg priority** — in a conflict, the faster party is designated leader and commits to an action first; all followers then best-respond to it. Actions: {continue, decelerate} for cars, {continue, decelerate, deviate} for pedestrians. | [Johora-SharedSpaces], IEEE ITSC 2018 pp. 3568–3574, §III-C (game), §III-B (action sets), §III-D (leader selection) | Priority negotiation in a **shared space** with no traffic rules; 2+ parties (§II) | Six observable booleans (§III-C-1): other's speed below normal; active interactions < *N*=2; own give-ways so far *G_α* < *M*=3; following a car; pedestrian in a group; followed by a car | **Yes** — "For each implicit interaction only one game is played and the games are **independent of each other**" (§III-C) | **None.** Explicit interaction defined but "we do not consider it in this paper" (§II) | **Yes** — simulated against **117 real conflict scenarios** from Hamburg video; trajectories "closely match" (§IV). ⚠ Simulated agents move ~2× real speed (§IV) | **Yes** `[inference]` — already implemented in a BDI simulator. ⚠ But the 12 payoff parameters are **uncalibrated and unpublished** (§III-C-1), and the host agent is centralised |
| **R13** | **Reactive angular yield** — decelerate for an agent already crossing in front of you, decided by a pair of angle tests, with no game solved at all. | [Johora-SharedSpaces], §III-B-a (car→pedestrian: fires if θ ≤ 15° ‖ ≥ 345°) and §III-B-c (courtesy: fires if θ_{ē_α n̂_βα} ≤ 20° ‖ ≥ 340° **and** 70° < θ_{ē_β n̂_βα} < 100° ‖ 260° < θ < 290°) | Imminent crossing conflict, 2 parties | **Relative angle and distance** to the nearest conflicting agent, within a **180° field of view** (§III-D) | **Yes** — stateless, evaluated per timestep | **None.** "simple interactions are dealt with by local action and **does not require synchronization or communication**" (§III-D) | **Yes**, as part of the same 117-scenario validation; Scenario 1 is resolved by this rule alone (§IV-a) | **Yes — the cheapest rule in this table** `[inference]`. Two dot products and a comparison. This is literally a `DO : S → A` function over observable geometry |
| **R14** | **Position-only speed choice with a credible collision threat** — pick a speed from a precomputed table indexed by the two agents' positions; the optimal policy necessarily retains a non-zero collision probability so the other party cannot exploit you. | [Camara-EmpiricalGT], *Proc. Measuring Behavior* 2018 pp. 238–244, §2.1 | Sequential chicken at an unsigned intersection / crossing, 2 parties | **Both positions only.** "no communication between the agents other than seeing each other's positions" (§2.1); the policy "may further **drop all dependency on time *t***" (§2.1) | **Yes** | **None** (§2.1) | **Yes** — 16 participants, 8 pairs, 48 runs (§2.2) | **Yes** `[inference]` — a 2-D lookup table over (*y*, *x*). ⚠ Inherits the non-zero collision probability, and the fitted human parameters came out at *U_crash* ≈ 0, which is a framing artefact (§4) |

---

## §2. Apparent correspondences — NOT merged, flagged for supervisor sign-off

The issue requires that where two papers give versions of the same rule under different names, both
rows are listed and the apparent correspondence is noted. Four such pairings. In each case I state
what looks the same and **what is actually different**, because the differences are the reason they
should not be collapsed.

**C1. R1/R2 (role asymmetry) ↔ R5 (attribute asymmetry) ↔ R10 (type asymmetry).**
All three are "priority goes to whichever party has the distinguishing property". The differences are
substantive:
- R1/R2 keys on a **relational, per-encounter** property (who is host) that is **arbitrary** — Foley
  et al.'s whole point is that bourgeois and paradoxical are equally efficient (§1).
- R5 keys on an **intrinsic, persistent** property (RHP) that is **not** arbitrary — the higher-RHP
  agent genuinely wins fights more often (§2).
- R10 keys on a **privately held type** that must be revealed or supplied.
[inference] Calling these "the same rule" would erase the distinction between an *arbitrary*
convention and a *payoff-justified* priority — and that distinction is exactly what the framing check
in [`search-log.md`](search-log.md) turns on. **Do not merge.**

**C2. R7 (social law / legal plan) ↔ R8, R9, R11 (all of which are state→action functions).**
R7 is the *general form*; R8, R9 and R11 are *instances* of that form in specific games. [inference]
It is tempting to say R7 subsumes them. But R7 is defined over an abstract, **finite, enumerable**
state space (§3), R11 is over a **continuous field**, and R9 is **stochastic** (a win probability, not
an action). R7's own definition gives a deterministic total function `DO : S → A`. So R9 and R11 are
not literally legal plans in Shoham & Tennenholtz's sense. **Do not merge**; treat R7 as a target
form that the others approximate.

**C3. R3 (correlate on an external cue) ↔ R4 (private recommendation from a trusted device).**
Both are correlated-equilibrium implementations. The difference is the **signal's visibility**: R3's
cue is **public and shared** ("say a coin toss", Foley §1); R4's recommendation is **private per
agent** with only the *distribution* public (Duffy & Feltovich, Abstract). [inference] That changes
what the simulator must provide, and R4's human-validated condition — that it only works if
payoff-enhancing — may not apply to R3. **Do not merge.**

**C5. R12/R13 (Johora & Müller) ↔ R7 (social law) ↔ R8/R14 (sequential chicken).** R13's angular
rules are `DO : S → A` functions and so are instances of R7's form; R14 is a table-driven instance of
the same form; R12 is not — it solves a game at runtime rather than evaluating a fixed function.
[inference] So **R12 and R13 come from the same paper but are different kinds of object**, and the
paper's own architecture keeps them separate on purpose: cheap functions for the common case, a
solved game only for genuine ambiguity. **Do not merge**, and note that this split is itself the
design recommendation.

**C4. R6 (threshold aggregation) ↔ R9's multi-party contention.**
Both handle more than two parties. But R6's threshold is a **decision rule an agent applies** (act
only if enough allies are present), whereas R9 is a **resolution procedure the simulator applies**
(pick a winner from a matrix). Different locus of control. **Do not merge.**

---

## §3. Rules known only at second hand — deliberately NOT in the table

Listed here so they are not lost, and kept out of §1 because I did not read their sources.

- **Stackelberg leader–follower priority** — pedestrians choose from {continue, decelerate, deviate},
  the car from {continue, decelerate}, in a sequential leader–follower game. Known **only** from
  [Camara-PedestrianModelsII] §IV-A-2, p. 12, summarising Johora & Müller (IEEE ITSC 2018,
  doi:10.1109/ITSC.2018.8569687). That paper is **confirmed to exist but was not opened** (IEEE
  paywall). [inference] The discrete action set is exactly the vocabulary a crowd rule needs, so this
  is the highest-value acquisition for the catalogue. See [`g4-...`](g4-game-theoretic-crowd-models.md).
- **Uncorrelated asymmetry / the classical bourgeois convention as Maynard Smith & Parker state it** —
  the primary source (*Animal Behaviour* 24:159–175, 1976) is **confirmed but not opened**. R1/R2 in
  the table come from Foley et al., who were read; the classical formulation is **not** in the table
  because I cannot state it from source. See [`g1-...`](g1-conflict-games-conventions.md) §2.
- **Aumann's correlated equilibrium, formally** — R3 and R4 are *instances* read at source; the
  general definition and its information assumptions are **not** recorded anywhere in this review,
  because Aumann (1974, 1987) was not opened. This is the largest single gap.
- **Farrell & Rabin's conditions for when cheap talk matters** — abstract read, body **not** opened
  (AEA returned HTTP 403). No self-committing/self-signaling conditions are stated in this review.

---

## §4. Reading the catalogue — what it actually tells the FYP

All `[inference]`, built on the sourced rows above.

**Eleven rules, and only one of them needs runtime communication.** R10 needs a pre-play talk stage,
and even that becomes unnecessary if the simulator supplies types. Every other rule in the table is
communication-free at runtime. **The supervisor's hypothesis — that conflict can be resolved by a
convention rather than a dialogue — is well supported by the literature.** That is the single
clearest result of this issue.

**Five rules are genuinely one-shot between strangers** (R3, R6, R7, R8, R9), which is the case a
crowd of 10,000 mostly consists of. R1/R2 are one-shot to *apply* but need population-level
acquisition first; R5 is one-shot only if the attribute is visible; R11 is not a per-encounter rule
at all.

**Only two rules are human-validated, and neither is a priority rule.** R4 (Duffy & Feltovich,
Chicken with recommendations) and R11 (Bonnemain et al., mean-field vs controlled crowd experiments).
Both are at abstract/preprint reading level respectively for the published text. R8's human fit exists
but was read only through the survey. **So the honest position is: the *class* of rules the FYP wants
is human-validated at one remove, but no specific priority convention in this table has been shown to
match human corridor behaviour.** That is a gap the FYP could actually fill, and it is worth putting
to the supervisor as a possible contribution.

**The two most promising rules for this FYP, and why:**
- **R9 (cell contention)** is the most immediately implementable — it is already a simulator
  subroutine, it is multi-party, one-shot and communication-free, and it has exactly one free
  parameter *P*. ⚠ And it has a weakness that is an **opportunity**: the cooperate/defect label is
  assigned arbitrarily at the start, which the paper never justifies. **The FYP could have the LLM
  supply that label and *P* per persona and per scenario.** That converts Bouzat & Kuperman's
  unexplained input into the FYP's contribution, connects directly to
  `dataset/personas.yaml` and `dataset/scenarios.yaml`, and is testable. This is the most concrete
  design proposal to come out of this issue.
- **R7 (social law)** is the right *target form* — and Shoham & Tennenholtz prove that finding such a
  law by search is NP-complete but offline (Theorem 3.1, §3). **The FYP's LLM is a candidate
  heuristic for that offline search.** That reframes the project as "can an LLM heuristically solve an
  NP-complete social-law synthesis problem?", which is a sharper research question than "do LLMs
  understand human behaviour" and is much harder to attack on data-leakage grounds
  (see [`g5-...`](g5-llm-agents-game-theory.md) §4).

**What the catalogue does *not* contain, and should be noted as a negative result.** No rule found
anywhere in this review resolves a conflict by **arrival order** ("whoever arrived first passes
first"), despite the issue naming that as the paradigm case and despite it being the obvious human
convention. The nearest thing is R1/R2, where the *role* (host/visitor) is a proxy for prior presence
— and Foley et al.'s result is that the **host–guest** norm (the one who was there first **concedes**)
evolves more readily than the ownership norm (§4). [inference] That is the opposite of
first-come-first-served, and it is a genuinely interesting finding to raise: the intuitive human rule
the FYP set out to formalise may be the *less* evolutionarily natural of the two options. Whether
first-come-first-served appears in the unobtained sources (especially Maynard Smith & Parker 1976 and
Mesterton-Gibbons et al. 2014, whose title is about ownership uncertainty) is an open question.

---

**Updated 2026-10-02:** rows **R4** and **R8** upgraded from abstract/second-hand to full text, and
rows **R12-R14** added, after three previously-unobtainable papers were supplied and read. See
[`conflict-avoidance-shortlist.md`](conflict-avoidance-shortlist.md).

**Draft status: pending supervisor review.** Specific decisions needed: (a) whether the four
correspondences in §2 should be merged or kept distinct; (b) whether to pursue R9 + LLM-supplied
parameters as the implementation route; (c) whether to reframe the project around R7's
offline-synthesis question.
