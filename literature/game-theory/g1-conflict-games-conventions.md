# G1 — Conflict games and resolution without communication

Prepared for issue [#20](https://github.com/M450NCH00/CrowdSimulation/issues/20).
Companion files: [`g2-norm-emergence.md`](g2-norm-emergence.md),
[`g3-cheap-talk.md`](g3-cheap-talk.md),
[`g4-game-theoretic-crowd-models.md`](g4-game-theoretic-crowd-models.md),
[`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md),
[`g6-transfer-across-games.md`](g6-transfer-across-games.md),
[`candidate-rule-catalogue.md`](candidate-rule-catalogue.md),
[`search-log.md`](search-log.md), [`refs-game-theory.bib`](refs-game-theory.bib).

**This is the priority sub-area.** It defines the target object of the whole FYP: a rule
that resolves a conflict game without runtime communication.

---

## ⚠ Read this first: two kinds of entry in this file, and why the difference matters

The issue's sourcing rules require that every paper was opened and that every claim carries a
locator. That is satisfiable for the modern papers. It is **not** satisfiable for several of the
`[foundational]` seeds, because the primary texts are behind publisher paywalls or are printed
books. This file therefore separates:

- **§1 Fully-read entries.** Full text opened and cached under `refs/`. Locators point to
  sections, equations and figures I read.
- **§2 Bibliographically-confirmed entries.** Existence, authorship, venue, volume, pages and
  DOI confirmed from a **Crossref record I fetched and cached**, but the **primary text was not
  opened**. For these I record *only* the bibliographic facts plus, where available, the
  publisher's own abstract. **No locator into the body is given, because I did not read the
  body.** Where the concept is needed, I state it as reported *by a paper I did read*, and
  attribute it that way.

[inference] §2 is a real limitation of this review, not a formality. It means that for
Aumann's correlated equilibrium, Maynard Smith & Parker's uncorrelated asymmetry, Schelling's
focal point and Lewis's convention, this FYP currently has **second-hand definitions only**.
Before the report quotes any of these as a formal definition, the primary text must be obtained
through the university library. That is logged as a risk in
[`search-log.md`](search-log.md) and in `WORK_LOG-20.md`.

---

# §1. Fully-read entries

### [Foley-ConflictConvention]: Conflict and convention in dynamic networks

- **Authors / Year / Venue:** Michael Foley, Patrick Forber, Rory Smead, Christoph Riedl / 2018 /
  *Journal of the Royal Society Interface* **15**(140), article 20170835.
- **Link:** doi:[10.1098/rsif.2017.0835](https://doi.org/10.1098/rsif.2017.0835) · open access
  via PMC5908527
- **Peer-review status:** **published**, peer-reviewed journal. The issue listed this seed as
  `arXiv:1802.08298`; **a published version exists and is what is cited here.** Bibliographic
  fields confirmed from the Crossref record (`refs/gt_cr_foley2018.json`).
- **Verified:** **yes — full text.** Published version read from the PMC copy
  (`refs/gt_foley2018_rsif_pmc.txt`); the preprint was also read
  (`refs/gt_arxiv_1802_08298.txt`) and agrees. **All locators below are to the published
  version's numbered sections and figures.**
- **Sub-area:** G1
- **Tags:** none (2018)
- **Type:** simulation (agent-based, reinforcement learning)
- **The game or conflict modelled:** "games of conflict (snowdrift, hawk–dove, chicken)"
  (Abstract), two parties per interaction, played repeatedly across a population of *N* agents.
  Payoff matrix given in figure 1*a*: hawk–hawk = (0, 0); hawk–dove = (1, x₂); dove–hawk =
  (x₁, 1); dove–dove = (y₁, y₂). "The highest pay-off results from playing hawk against dove,
  the lowest from playing hawk against hawk and all players would prefer their opponent to play
  dove" (§1). The mixed Nash equilibrium is stated explicitly: "host plays dove with probability
  x₁/(1 − y₁ + x₁) and the visitor plays dove with probability x₂/(1 − y₂ + x₂)" (§1).
- **The rule or solution concept:** a **convention, defined as a correlated equilibrium** that
  correlates behaviour on an **external cue**. Stated in the Abstract: "An important way to
  resolve games of conflict … involves adopting a convention: a correlated equilibrium that
  avoids any conflict between aggressive strategies." The mechanism is spelled out in §1:
  "Correlating behaviour on some external cue (say a coin toss) can produce a convention, such
  as taking turns playing aggressively (e.g. player one plays hawk when heads, dove otherwise;
  and player two plays hawk when tails, dove otherwise)."
  In this model the cue is **the host/visitor role**: "using their role as host versus visitor
  as the public cue (figure 1*b*)" (§1). Two named conventions result, and the paper is careful
  that they are **equally efficient** under symmetric payoffs:
  - **bourgeois strategy** — "they play hawk when hosting and dove when visiting" (§1). "Hosts
    always receive the maximal pay-off and visitors always receive x₂" (§3).
  - **paradoxical strategy** — "one plays dove when hosting and hawk when visiting" (§1). "This
    equilibrium grants the visitors the maximal pay-off while the hosts receive x₁" (§3).
- **Information the rule requires:** exactly **one bit — am I the host or the visitor in this
  encounter?** The paper is explicit that no beliefs about others are needed: "reinforcement
  learning does not require individuals to track the behaviors or payoffs of other players in
  the population … an agent only tracks the payoffs associated with their own behavior" (§2.1),
  and in §4: "our model shows that learners with no such beliefs or expectations can establish
  convention-like behaviour". Agents keep separate weight vectors for hosting and visiting
  (§2.1), which is what makes the role usable as a cue.
- **One-shot or repeated:** the **convention is population-level and acquired by repeated
  play**, not by a single encounter. Simulations "run for 10⁶ rounds of play" (Data Generation
  and Analysis). *But* once established, application is per-encounter and stateless: "Once the
  correlated equilibrium is established, visiting any agent yields the same pay-off as everyone
  is deploying the same strategies conditional on the same cues" (§3). [inference] This split —
  **expensive offline acquisition, trivial online application** — is exactly the shape the FYP
  wants, and it is the single most useful structural fact in this entry.
- **Communication required:** **none.** No message passing appears anywhere in the model; agents
  observe only their own role, their own payoff and their own weights (§2.1, equations (1)–(2)).
  **This is a candidate for the FYP's runtime rule.**
- **Scalability:** stated, and favourable. "Perhaps surprisingly, the dynamical results are
  insensitive to population size — we see the same qualitative dynamics in populations of sizes
  from 20 to 2000 (figure 3*d*)" (§3). A representative large run uses *N* = 500 (figure 2
  caption) and a degree-distribution run uses *N* = 1000 (figure 3*e* caption). Simulations were
  "written in C++" (Data Generation and Analysis). **No wall-clock or asymptotic cost is
  reported** — `[not stated in paper]` for computational cost as such; the claim is about
  *behavioural* insensitivity to *N*, which is a different (and weaker) claim.
- **Validated against human behaviour:** **no.** No human data is collected. The paper appeals
  to human behaviour only rhetorically — the host–guest norm is "a phenomenon common to human
  interaction" (Abstract) — and cites others for the claim that correlated equilibria "are also
  readily learned by humans" (§1, its reference [45]). [inference] That citation is the route to
  [Duffy-CorrelatedEq] below, which *is* a human experiment — and which, as of 2026-10-02, has been
  read in full.
- **Assumptions that may not hold in a crowd:**
  - **The cue must be shared and unambiguous.** The model's cue is host/visitor, which is
    well-defined because one agent initiates. [inference] In a corridor conflict there is no
    equivalent built-in asymmetry unless the simulator supplies one.
  - **No resource scarcity.** Stated by the authors: "our model represents scarcity of resources
    indirectly as variation in pay-off biases … though we do not consider catastrophic scarcity
    or interaction outcomes" and "the model assumes that losses incurred when playing dove
    against hawks are not overwhelming" (§4).
  - **Payoffs fixed and identical across encounters** (figure 1*a*, §2.1).
  - Interaction partners are chosen by the agent, and the network is unstructured to begin with:
    "Starting from uniform homogeneous mixing (fully connected network)" (figure 1*c* caption).
- **Limitations stated by the authors:** the scarcity limitation quoted above (§4); and the
  finding that outcome depends on the update asymmetry — symmetric updating yields hub-and-spoke
  "network solutions" rather than conventions (§3), so the result is contingent on the modelling
  choice that "hosts have no control over who decides to visit them" (§2.1).
- **Relevance to this FYP:** the **single most important entry in this review.** It supplies
  (a) the target object — a convention as a correlated equilibrium on an observable cue;
  (b) a worked, communication-free mechanism for acquiring it; (c) the offline/online split; and
  (d) a warning: **which** convention emerges is not free. "Rather than the correlated
  equilibrium associated with ownership norms … we usually see the opposite host–guest norm …
  evolve on dynamic networks" (Abstract). [inference] Applied to the FYP: if conventions are
  *extracted from an LLM* rather than evolved, the FYP must ask which of several equally
  efficient conventions the LLM returns, and whether that choice is defensible — a question that
  parallels the collective-bias finding in [`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md).
- **BibTeX:** `foley2018conflict` — see [`refs-game-theory.bib`](refs-game-theory.bib).

---

### [Chen-NPersonHawkDove]: Evolutionary dynamics of N-person Hawk-Dove games

- **Authors / Year / Venue:** Wei Chen, Carlos Gracia-Lázaro, Zhiwu Li, Long Wang, Yamir Moreno /
  2017 / *Scientific Reports* **7**, article 4800.
- **Link:** doi:[10.1038/s41598-017-04284-6](https://doi.org/10.1038/s41598-017-04284-6) · open
  access
- **Peer-review status:** **published**, peer-reviewed journal. The issue listed this seed as
  `arXiv:1702.03969`; the published version is cited. Fields confirmed from Crossref
  (`refs/gt_cr_chen2017.json`).
- **Verified:** **yes — full text**, read from `refs/gt_arxiv_1702_03969.txt` (arXiv v1).
  ⚠ **Locator caveat:** the published Scientific Reports article and the preprint may differ in
  pagination and equation numbers. Equation numbers below are the **preprint's**. They should be
  re-checked against the published PDF before being quoted in the report.
- **Sub-area:** G1
- **Tags:** none (2017)
- **Type:** formal theory + numerical solution
- **The game or conflict modelled:** the Hawk–Dove game generalised from 2 to **N** parties. "we
  propose a generalization of HDG for N agents, hereafter N-person HDG" (Introduction). What is
  contested is a single divisible resource *R*. Groups of size *N* are sampled from a population
  of size *Z*; *n_H* and *n_D* are the numbers of hawks and doves, *N* = *n_H* + *n_D*
  (Introduction). Payoffs (preprint eqs (1)–(2)):
  - Hawks: `P_H = (R − (n_H − 1)c_H) / n_H` when *n_H* > 0, where *c_H* is the cost of injury and
    "(n_H − 1)c_H represents the total injury suffered by all the hawks".
  - Doves: `P_D = R/N` when *n_H* = 0, and 0 when *n_H* > 0 — "doves only get payoffs when there
    are no hawks".
  The paper is explicit that HDG is "an **anti-coordination game** with two possible strategies"
  (Introduction), and that for *N* = 2 the Hawk–Dove and Snowdrift games coincide but for *N* > 2
  "the mathematical formulation differs drastically between both situations" (Introduction).
- **The rule or solution concept:** **not a convention.** The solution concept is an
  **evolutionarily stable mixed population state** under replicator dynamics — a *fraction* of
  doves, not a rule an individual follows. The headline threshold: "There is a critical value
  `c_cv = R/(N − 1)` for the cost c_H beyond which" doves survive; "for c_H < c_cv the dynamics
  leads to the extinction of the doves" (Introduction; restated at the preprint's §"ccv =
  R/(N−1)" discussion). A **second** variant adds a genuine decision rule: doves aggregate to
  expel hawks **only if they meet a threshold** — "If the fraction of doves exceeds or equals the
  threshold (n_D/N ≥ T), the doves expel the hawks, paying a cost c_D" (preprint eq. (6) region).
  Thresholds explored are T = 0.2, 0.4, 0.6, 0.8; "For T = 1 the previous N-person HDG model is
  recovered" (preprint, §on threshold).
- **Information the rule requires:** for the threshold variant, each dove must know **the
  fraction of doves in its own group**, *n_D*/*N* — i.e. a count of how many co-present agents
  share its strategy. [inference] That is a strictly harder observation than Foley's one-bit
  role cue, but it is plausibly available to a simulated agent with a neighbourhood query.
- **One-shot or repeated:** **repeated / population-level.** The analysis is replicator dynamics
  over a population, in "either a very large or an infinite population" plus a finite-*Z* case
  (Introduction). There is **no dyad-level rule that works on a single encounter between
  strangers**. The threshold condition itself, however, is evaluated per encounter.
- **Communication required:** **none stated.** No signalling or messaging appears in the model.
- **Scalability:** *N* is a **model parameter**, not a computational limit — this is the entry's
  main value. "we derive an exact equation for the evolution of the fraction of doves in a
  well-mixed population, which can be solved numerically" (Introduction), so cost is that of
  solving one equation rather than simulating *N* interacting agents. **No computational cost
  figures are given** — `[not stated in paper]`.
- **Validated against human behaviour:** **no.** The framing is animal behaviour ("In the animal
  world…", Abstract); no human or animal data is fitted.
- **Assumptions that may not hold in a crowd:** **well-mixed population** with random group
  sampling (Introduction) — a crowd is spatially structured, not well-mixed; a single shared
  resource value *R* for all agents; strategies fixed per agent rather than chosen per
  encounter; and payoff-proportional reproduction (replicator dynamics) rather than within-
  lifetime decision-making.
- **Limitations stated by the authors:** the well-mixed / infinite-population idealisation is
  stated as a modelling choice throughout the Introduction rather than flagged as a limitation.
  [inference] I did not find an explicit limitations passage in the preprint; treat the
  well-mixedness as the binding one.
- **Relevance to this FYP:** it is the only entry that takes the conflict game **beyond two
  parties**, which the issue correctly identifies as necessary for crowd-scale conflicts. Its
  contribution to the rule catalogue is the **threshold rule** ("act aggressively only if at
  least a fraction T of those present agree"), which is implementable from a local count.
  [inference] Its *warning* is equally important: for *N* > 2 the tractable object stops being an
  individual decision rule and becomes a population statistic. If the FYP wants a *rule* at
  crowd scale, it should expect to pay for that either in per-agent observation (the threshold)
  or in giving up the closed-form analysis.
- **BibTeX:** `chen2017nperson`.

---

### [Hall-IteratedHawkDove]: Dominance, sharing, and assessment in an iterated Hawk–Dove game

- **Authors / Year / Venue:** Cameron L. Hall, Mason A. Porter, Marian S. Dawkins / 2020 /
  *Journal of Theoretical Biology* **493**, article 110101.
- **Link:** doi:[10.1016/j.jtbi.2019.110101](https://doi.org/10.1016/j.jtbi.2019.110101)
- **Peer-review status:** **published**, peer-reviewed journal (Elsevier). The issue listed this
  seed as `arXiv:1907.02160`; a published version exists. Fields confirmed from Crossref
  (`refs/gt_cr_10_1016_j_jtbi_2019_110101.json`).
- **Verified:** **full text of the preprint only.** Read from `refs/gt_arxiv_1907_02160.txt`
  (arXiv v2, 31 Oct 2019, stamped "Preprint submitted to Journal of Theoretical Biology").
  The published Elsevier version is paywalled and was **not** opened.
  ⚠ **All locators below are to the preprint.** Section numbers in the published version may
  differ and must be re-checked before quoting.
- **Sub-area:** G1
- **Tags:** none (2020)
- **Type:** formal theory + simulation
- **The game or conflict modelled:** an **iterated** Hawk–Dove game between **two** animals, A
  and B, "who interact with each other repeatedly in a contest for resources" (§2), resource
  value normalised to 1. Three stated modifications to the classical game (§2): "(1) We study an
  iterated game in which each stage is an HD game. (2) We assume that there is always an explicit
  winner and loser in any Hawk–Hawk interaction … (3) We assume that Hawk–Hawk conflicts have a
  biased outcome, in that one animal is more likely than its opponent to win the fight." The
  classical payoffs are reproduced in its figure 1, and the paper notes the classification depends
  on the fight cost *c*: "When c > 1 … the classical HD game is an example of the 'Snowdrift' game
  (also called the 'Chicken' game). When c ∈ (0, 1), the HD game is an example of a 'Prisoner's
  Dilemma'" (§2). Hawk–Hawk outcomes use a cost of winning *c_W* and of losing *c_L*, with the
  winner getting 1 − *c_W* and the loser −*c_L*, and 1 − *c_W* > −*c_L* (§2).
- **The rule or solution concept:** **evolutionary stability of conditional strategies indexed by
  resource holding potential (RHP)**. The outcomes are not one rule but a *menu* of stable
  behaviours: sharing, dominance relationships, or assessment-then-settle. The headline results
  (Abstract): "sharing is stable only when the cost of fighting is low and the animals in a
  contest have similar RHPs, whereas dominance relationships are stable in most other
  situations"; and, for the case where RHPs cannot be observed, "(1) … the most successful
  strategies involve a limited period of assessment followed by a stable relationship in which
  fights are avoided and (2) … the duration of assessment depends both on the costliness of
  fighting and on the difference between the animals' RHPs."
- **Information the rule requires:** **the two agents' relative RHP** — how likely each is to win
  a fight. The paper treats the availability of this information as the central variable and
  splits the analysis accordingly: §3 is "Analysis of strategies for animals with knowledge of
  p_A" and §4 is "Analysis of strategies for animals with **no** knowledge of p_A". Where RHP is
  unobservable, the information must be **bought by fighting**: assessment is a limited period of
  costly escalation used to learn *p_A* (§4, Abstract). The authors motivate this by noting that
  neither classical HD nor iterated Prisoner's Dilemma "includes any element of assessment, where
  an animal uses information about its opponent from signals, resource ownership, or past
  experience to guide its behaviour" and that "it is well-established that conditional strategies
  with assessment are far better models of animal conflict than strategies that do not involve
  assessment" (§2).
- **One-shot or repeated:** **strictly repeated, and dyad-level.** The outcome is a *relationship*
  between a specific pair. It does **not** work on a single encounter between strangers: the whole
  point of the assessment result is that the first several encounters are spent learning, and only
  then are fights avoided (§4). "We assume that each HD interaction is identical, such that animals
  do not get stronger or weaker over time" (§2).
- **Communication required:** **none at runtime** in the modelled strategies; assessment happens
  through *fighting*, not signalling. The authors note signalling as an alternative route to the
  same information (§2) but do not model it. [inference] This makes the entry a candidate for the
  FYP's runtime rule **only** in its "knowledge of RHP" form (§3), where the rule reduces to
  "defer to the stronger agent" and needs no assessment period.
- **Scalability:** `[not stated in paper]`. The model is strictly pairwise (two animals, §2);
  no population-scale or computational-cost result is given. Software is released at
  `bitbucket.org/CameronLHall/dominancesharingassessmentmatlab/` (Abstract) — **not run**, per
  the repo's guardrail on executing third-party research code.
- **Validated against human behaviour:** **no.** The domain is animal conflict; the paper cites
  empirical animal-behaviour literature (Archer 1988; Huntingford & Turner 1987; Guhl 1968 and
  others, §1) as motivation but fits no data.
- **Assumptions that may not hold in a crowd:** fixed RHP per agent over time ("animals do not get
  stronger or weaker over time", §2); a constant resource value in every stage ("the available
  resource has the same value in each stage game", §2); and above all **persistent pairing** —
  the agents meet each other repeatedly and can build a relationship. [inference] A crowd of
  10,000 agents in a corridor is mostly composed of strangers who meet once, which is precisely
  the case this model does **not** cover.
- **Limitations stated by the authors:** the paper frames the unobservable-RHP case as the
  realistic one and its own §3 (observable RHP) as the idealisation; the fixed-RHP and
  constant-resource assumptions are stated explicitly in §2 as modelling choices.
- **Relevance to this FYP:** two contributions and one constraint.
  - **Rule contributed:** *defer to the agent with the higher RHP* — a priority rule keyed to an
    observable (or assumed-observable) **attribute asymmetry**, as opposed to Foley's *role*
    asymmetry. [inference] This is the game-theoretic anchor for the FYP's persona attributes: if
    age, gender or mobility maps onto anything like RHP, this paper is the reason a persona could
    legitimately determine who yields. That connects directly to
    `literature/demographic-personas/` from issue #16.
  - **Constraint placed on the extraction:** assessment is **costly and takes time**. A rule that
    needs to learn the other agent's type cannot be a one-shot rule. If the FYP wants one-shot
    resolution, the type must be *observable at a glance* or *not used at all*.
- **BibTeX:** `hall2020dominance`.

---

# §2. Bibliographically-confirmed entries (primary text NOT opened)

Each row below was confirmed by fetching its Crossref record (all cached in
`refs/gt_crossref_all.json`). The `[secondhand]` tag from the issue is **discharged as to
existence**, and explicitly **not discharged as to content**.

> ⚠ **One exception, 2026-10-02.** [Duffy-CorrelatedEq] sits in this section for historical reasons
> but is **no longer a §2 entry** — its full text was supplied by the user and read, and its entry
> has been rewritten accordingly. It is left in place so existing cross-references keep working.
> Everything else in §2 remains unread at source.

> ⚠ **One exception, 2026-10-02.** [Duffy-CorrelatedEq] sits in this section for historical reasons
> but is **no longer a §2 entry** — its full text was supplied by the user and read, and its entry
> has been rewritten accordingly. It is left in place so existing cross-references keep working.
> Everything else in §2 remains unread at source.

### [MaynardSmith-AnimalConflict]: The Logic of Animal Conflict `[foundational]`

- **Authors / Year / Venue:** J. Maynard Smith, G. R. Price / 1973 / *Nature* **246**, pp. 15–18.
- **Link:** doi:[10.1038/246015a0](https://doi.org/10.1038/246015a0)
- **Peer-review status:** published, peer-reviewed journal.
- **Verified:** **bibliographic record only** (Crossref, cached). Nature's 1973 archive is
  paywalled; **full text not opened.**
- **Justification for `[foundational]`:** this is the origin of the Hawk–Dove game itself, the
  game every other G1 entry generalises. There is no modern replacement for a 1973 origin paper.
- **2016-or-later pairing (required by the issue):** [Foley-ConflictConvention] (2018),
  [Chen-NPersonHawkDove] (2017) and [Hall-IteratedHawkDove] (2020) are all applications of this
  game, and all were read in full. [Hall-IteratedHawkDove] §2 cites it by name as the source of
  the classical game.
- **What can be said with a source:** that it originates the Hawk–Dove game, **as reported by**
  [Hall-IteratedHawkDove] §2: "a model that is based on the classical Hawk–Dove (HD) game …,
  which was developed to describe a single conflict between animals over a shareable resource
  (Maynard Smith and Price, 1973; Maynard Smith, 1979, 1982)". **No definition is quoted from the
  1973 paper itself, because it was not read.**
- **BibTeX:** `maynardsmith1973logic`.

### [MaynardSmith-AsymmetricContests]: The logic of asymmetric contests `[foundational]`

- **Authors / Year / Venue:** John Maynard Smith, G. A. Parker / 1976 / *Animal Behaviour*
  **24**(1), pp. 159–175.
- **Link:** doi:[10.1016/S0003-3472(76)80110-8](https://doi.org/10.1016/S0003-3472(76)80110-8)
- **Peer-review status:** published, peer-reviewed journal (Elsevier).
- **Verified:** **bibliographic record only** (Crossref, cached). ScienceDirect paywalled; **full
  text not opened.**
- ⚠ **Citation error found in the issue's top-priority seed.** [Foley-ConflictConvention] cites
  this paper in its reference list as *"J. Maynard Smith and G. R. Parker. The logic of asymmetric
  animal contests. **Nature, 146**:15–18, 1976"* (preprint reference [32]). That is wrong on the
  venue, volume, pages and one initial: it conflates this paper with
  [MaynardSmith-AnimalConflict] (*Nature* **246**:15–18, 1973). The correct record is the one
  above, verified independently from Crossref. **This is exactly why the issue forbids citing
  from another paper's reference list**, and it is recorded in
  [`search-log.md`](search-log.md).
- **Justification for `[foundational]`:** it is the stated origin of the idea that an arbitrary
  observable asymmetry can settle a contest — the closest classical analogue to a priority rule
  such as "whoever arrived first passes first". The issue flags it as a priority seed once
  confirmed; it **is** confirmed to exist, but **not read**.
- **2016-or-later pairing:** [Foley-ConflictConvention] (2018) §1, §3 and §4 is a direct modern
  treatment of the bourgeois/paradoxical asymmetry this paper is credited with, and was read in
  full.
- **What can be said with a source:** that the bourgeois strategy has been "invoked as an
  explanation for norms of ownership or territoriality", **as stated by**
  [Foley-ConflictConvention] §1 (which attributes the idea to Maynard Smith 1982 and Maynard
  Smith & Parker 1976). **The formal notion of an "uncorrelated asymmetry" is NOT recorded here,
  because the primary text was not opened.** Obtaining it is a stated next step.
- **BibTeX:** `maynardsmith1976asymmetric`.

### [Aumann-CorrelatedEquilibrium]: Subjectivity and correlation in randomized strategies `[foundational]`

- **Authors / Year / Venue:** Robert J. Aumann / 1974 / *Journal of Mathematical Economics*
  **1**(1), pp. 67–96.
- **Link:** doi:[10.1016/0304-4068(74)90037-8](https://doi.org/10.1016/0304-4068(74)90037-8)
- **Peer-review status:** published, peer-reviewed journal (Elsevier).
- **Verified:** **bibliographic record only** (Crossref, cached). **Full text not opened.**
- **Related record also confirmed:** Aumann, "Correlated Equilibrium as an Expression of Bayesian
  Rationality", *Econometrica* **55**(1), 1987, doi:[10.2307/1911154](https://doi.org/10.2307/1911154)
  — also **not opened**. [inference] For the FYP's purposes the 1987 paper is probably the more
  useful of the two, because it is the one that states the *information* assumptions (a common
  prior and a shared signal) in the form this project needs.
- **Justification for `[foundational]`:** correlated equilibrium is the solution concept
  [Foley-ConflictConvention] builds on, and hence the formal object the FYP would be claiming to
  extract. The issue requires its definition and information assumptions be recorded.
- **⚠ Requirement not met.** The issue asks me to "Record the formal definition and its
  information assumptions." **I cannot, from the primary source.** What I can record, with a
  locator, is how a paper I read uses it: [Foley-ConflictConvention] §1 describes a correlated
  equilibrium in this class of games as arising when "individuals are able to coordinate their
  strategies on an external cue or signal", gives the coin-toss turn-taking example, and §4 notes
  that "other scholars have identified correlated equilibria as central to conventions". That is
  a **usage**, not Aumann's definition. The gap is logged in
  [`search-log.md`](search-log.md) §framing check as the main thing blocking a fully rigorous
  framing claim.
- **BibTeX:** `aumann1974subjectivity`, `aumann1987correlated`.

### [Schelling-StrategyOfConflict]: The Strategy of Conflict / focal points `[foundational]`

- **Author / Year / Venue:** Thomas C. Schelling. Two records confirmed:
  - the book *The Strategy of Conflict* (Harvard University Press, 1960), located via reviews
    indexed in Crossref — e.g. the review in *Economica* **28**(109), 1961, p. 96,
    doi:[10.2307/2550465](https://doi.org/10.2307/2550465), and in *Econometrica* **31**(3), 1963,
    p. 614, doi:[10.2307/1910005](https://doi.org/10.2307/1910005);
  - the journal precursor: Schelling, "The strategy of conflict. Prospectus for a reorientation of
    game theory", *Journal of Conflict Resolution* **2**(3), 1958, pp. 203–264,
    doi:[10.1177/002200275800200301](https://doi.org/10.1177/002200275800200301).
- **Peer-review status:** the 1960 item is a **scholarly monograph** (not peer-reviewed in the
  journal sense); the 1958 item is a peer-reviewed journal article.
- **Verified:** **bibliographic records only.** Neither the book nor the 1958 article was opened.
  Note the issue's own instruction that "a book chapter locator is a page range" — I have no page
  range to give, because I did not read it.
- **Justification for `[foundational]`:** Schelling is the standard primary source for focal
  points and tacit coordination, and tacit coordination is precisely "resolution without
  communication".
- **⚠ Requirement not met.** The issue asks me to "record the definition of a focal point as
  stated there." **I cannot.** No definition of a focal point is asserted anywhere in this review.
  [inference] The 1958 *Journal of Conflict Resolution* article is the most promising route to an
  openable primary source and should be tried through the university library first, since it
  predates the book and covers the same material.
- **BibTeX:** `schelling1960strategy`, `schelling1958strategy`.

### [Vanderschraaf-ConventionAsCE]: Convention as correlated equilibrium

- **Author / Year / Venue:** Peter Vanderschraaf / 1995 / *Erkenntnis* **42**(1), pp. 65–87.
- **Link:** doi:[10.1007/BF01666812](https://doi.org/10.1007/BF01666812)
- **Peer-review status:** published, peer-reviewed journal (Springer).
- **Verified:** **bibliographic record only** (Crossref, cached). Springer paywalled; **full text
  not opened.**
- **Why it is listed despite not being read:** it is the paper whose *title* is the framing claim
  this FYP would be making, and [Foley-ConflictConvention] §4 cites it for exactly that claim
  ("other scholars have identified correlated equilibria as central to conventions" — its
  reference [17] is this paper). **It is the highest-value single acquisition target for the
  framing check.** See [`search-log.md`](search-log.md).
- **BibTeX:** `vanderschraaf1995convention`.

### [Duffy-CorrelatedEq]: Correlated Equilibria, Good and Bad: An Experimental Study

> ⚠ **UPGRADED 2026-10-02.** This entry was originally **abstract-only**. The full text was
> subsequently supplied by the user and read. It is rewritten below from the full text, and locators
> are now to the **printed page numbers 701–721**. A fuller treatment, including the experimental
> design in detail, is in [`conflict-avoidance-shortlist.md`](conflict-avoidance-shortlist.md) §A3.

- **Authors / Year / Venue:** John Duffy (University of Pittsburgh), Nick Feltovich (University of
  Aberdeen Business School) / 2010 / *International Economic Review* **51**(3), August 2010,
  pp. 701–721.
- **Link:** doi:[10.1111/j.1468-2354.2010.00598.x](https://doi.org/10.1111/j.1468-2354.2010.00598.x)
- **Peer-review status:** **published**, peer-reviewed journal (Wiley).
- **Verified:** **yes — full text**, cached as `refs/gt_duffy2010_ier.pdf` (text at `.txt`).
- **Sub-area:** G1
- **Tags:** none (2010 — outside the 2016+ window, retained because it is the only **human
  experiment on correlated equilibrium in a conflict game** found in this review)
- **Type:** human experiment
- **The game or conflict modelled:** **Chicken**, two parties, payoffs in figure 1 (p. 702):
  (D,D) = 0,0; (D,C) = 9,3; (C,D) = 3,9; (C,C) = 7,7. Three Nash equilibria — (D,C) → (9,3),
  (C,D) → (3,9), and mixed with each playing D with probability 2/5 → (5.4, 5.4) (p. 704). Chosen
  because it is "perhaps the simplest game with the property that there exist correlated equilibrium
  payoff pairs that lie outside the convex hull of Nash equilibrium payoff pairs" (§2, p. 703).
- **The rule or solution concept:** correlated equilibrium implemented through a **mediator** — "a
  nonstrategic third party" who "chooses one of the four pure-strategy profiles according to a
  commonly known probability distribution, and to each player 'recommends' that player's component in
  the profile… The probability distribution is a correlated equilibrium of the original game **if
  each player at least weakly prefers following her recommended action to choosing any other
  action**" (p. 704). The incentive conditions reduce to four linear inequalities (p. 704):
  2*p_DC* ≥ 3*p_DD*; 3*p_CD* ≥ 2*p_CC*; 2*p_CD* ≥ 3*p_DD*; 3*p_DC* ≥ 2*p_CC*, summing to 1.
- **Information the rule requires:** a **private per-agent signal** (the recommendation), **public
  knowledge of the distribution** it was drawn from, and a **trusted third party** to draw it
  (p. 704). [inference] The clearest statement in this review of what a signal-based rule actually
  costs — and all three are things a simulator can supply, because the simulator *is* the mediator.
- **One-shot or repeated:** each round is one-shot, but subjects played **40 rounds** under
  **round-robin matching** "in an attempt to minimize incentives for reputation building" (p. 708),
  so no dyad-level history accumulates.
- **Communication required:** **none between the players.** "Subjects were asked not to communicate
  directly with one another, so the only interactions were via the computer program" (p. 708). The
  signal comes from the mediator. **Candidate for the FYP's runtime rule.**
- **Scalability:** `[not stated in paper]`.
- **Validated against human behaviour:** **yes — this is the entry's whole point.** 16 sessions ×
  12 subjects = **192 subjects**, 7,580 observations, 1,920 per treatment (§4, p. 708). Four
  treatments (table 1, p. 707): *good* (a payoff-superior CE, expected payoffs 6.333), *bad* (a CE
  that is payoff-**inferior** to every symmetric Nash-hull payoff, 4.8), *Nash* (a convex combination
  of Nash equilibria, 6), and *very good* (**not** a CE but highest payoffs, 6.8 — the control for
  experimenter demand).
  - **Result 1** (p. 712): recommendations shift outcomes "**if and only if the recommendations come
    from a correlated equilibrium**."
  - **The striking null** (p. 711): no significant difference between *no recommendations* and *very
    good recommendations* (χ² = 3.511, df = 3, p > 0.20). "It suggests that **subjects will not
    blindly follow just *any* recommendations, but rather will follow them only if they are
    consistent with implementation of a correlated equilibrium.**"
  - **Compliance rates** (table 3, p. 713), against a mixed-NE baseline of 0.400 for D and 0.600 for
    C: good 0.735 / 0.732; Nash 0.567 / 0.777; bad 0.477 / 0.631 (not significant overall); very
    good 0.511 / 0.608, with D-following collapsing to **0.227** in the last five rounds.
  - **Result 4** (p. 719): following pays only where the distribution is a sensible CE — forgone
    payoffs −0.467/round (good) and −0.428/round (Nash), both significantly below zero; +0.026 (bad)
    and +0.059 (very good), neither significant.
- **Assumptions that may not hold in a crowd:** an abstract points game with no space, movement or
  time pressure; a trusted mediator; and subjects who understand the announced distribution — the
  authors themselves raise (footnote 19, p. 720) that compliance may partly track **how easy Bayes'
  rule is** in each treatment.
- **Limitations stated by the authors:** "our results cast a bit of doubt on the usefulness of this
  solution concept as a descriptive notion, as the correlated equilibrium **point predictions are not
  observed**" (p. 720) — directional predictions hold, point predictions do not. Plus the Bayes'-rule
  confound above, and a framing caveat (footnote 11, p. 708): "We acknowledge the possibility that
  our use of the term '**recommendations**' itself might have influenced subjects to follow them."
- **Relevance to this FYP:** four things, two of which are only visible in the full text.
  - **A realistic compliance bar.** "it is **not necessary for recommendations always to be
    followed** in order for them to have an effect. Recommendations in these treatments were followed
    only roughly **70%–75%** of the time, but this was enough to have a significant effect on the
    distribution of outcomes" (p. 719). [inference] The FYP does not need universal obedience for its
    extracted rule to change the simulation.
  - **A constraint on which rules are worth extracting.** "it is particularly difficult to induce
    subjects to follow recommendations based on correlated equilibria that are Pareto inferior to the
    available Nash equilibria. This finding would seem to **greatly limit the class of empirically
    relevant correlated equilibria to those that Pareto improve upon the set of Nash equilibria**"
    (p. 720).
  - **⚠ The signal must be supplied, not discovered.** "when subjects do not receive recommendations,
    their choices can be described fairly well… by mixed-strategy Nash equilibrium. This result
    suggests that **theoretical rationales for correlated equilibria that do not rely on extrinsic,
    third-party recommendations… might be difficult to observe in practice**" (p. 719), though the
    authors note fixed pairings or communication might have changed this. [inference] Humans did
    **not** invent the coordinating convention for themselves. This corroborates, from a different
    literature, the spatial-network failure recorded in
    [`g2-norm-emergence.md`](g2-norm-emergence.md), and is a further argument for installing the
    rule offline rather than hoping it emerges.
  - **⚠ An open question that is almost a project brief** (p. 720): the authors ask whether "**the
    form of recommendations matters**" and whether "the message space for recommendations [must]
    correspond precisely to the action space, or might it be larger… or consist of a set of messages
    with no clear mapping to the action space". [inference] An LLM is exactly a device that issues
    recommendations in natural language over an unbounded message space. This also connects to the
    strategy-label presentation dispute in
    [`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md) §2.
- **⚠ Two citation errors in its reference list** (p. 721), recorded because independent verification
  is this review's method: Gul is cited in the body as "Gul (1988)" (p. 702) but listed as
  *Econometrica* **66** (1998); and Hart & Mas-Colell's "A Simple Adaptive Procedure Leading to
  Correlated Equilibrium" is listed as *Econometrica* **60** (2000) — volume 60 is 1992, and the 2000
  paper is volume 68. Use Crossref, not this list, if citing either.
- **BibTeX:** `duffy2010correlated`.

### [MestertonGibbons-IteratedHDRevisited]: The Iterated Hawk–Dove Game Revisited: The Effect of Ownership Uncertainty on Bourgeois as a Pure Convention

- **Authors / Year / Venue:** Mike Mesterton-Gibbons, Tugba Karabiyik, Tom N. Sherratt / 2014 /
  *Dynamic Games and Applications* **4**(4), pp. 407–431.
- **Link:** doi:[10.1007/s13235-014-0111-5](https://doi.org/10.1007/s13235-014-0111-5)
- **Peer-review status:** published, peer-reviewed journal (Springer).
- **Verified:** **bibliographic record only** (Crossref, cached). **Full text not opened.**
- **How it was found:** from the reference list of [Foley-ConflictConvention] (preprint reference
  [33]) — and therefore, per the issue's rules, it is listed here **only** as a confirmed-to-exist
  lead, with no content claims.
- **Why it matters:** the title alone identifies it as directly on-point for the FYP — whether
  "bourgeois" survives as a **pure convention** when **ownership is uncertain**. [inference]
  "Ownership uncertainty" is the biological analogue of a simulator that cannot reliably tell
  which agent arrived first, which is a failure mode the FYP will hit. Recommended acquisition.
- **BibTeX:** `mestertongibbons2014iterated`.

---

## Summary of G1 against the issue's acceptance criteria

| Criterion | Status |
|---|---|
| ≥ 2 qualifying entries | **Met** — **4** fully-read entries (Foley, Chen, Hall, and — since 2026-10-02 — Duffy & Feltovich) |
| Every listed paper independently opened | **Partially met.** **4** opened in full (Duffy & Feltovich upgraded from abstract-only on 2026-10-02); 6 confirmed bibliographically only. Each is labelled. Nothing is cited *for content* from another paper's reference list. |
| Peer-review status recorded | Met for all 10 |
| Every claim carries a locator | Met for the fully-read entries. For §2 entries **no body locators are given at all**, by design |
| Information the rule requires, recorded | Met for all entries where a rule exists |
| One-shot vs repeated, recorded | Met |
| `[foundational]` tagged, justified, paired with a 2016+ application | Met for Maynard Smith & Price, Maynard Smith & Parker, Aumann, Schelling |

**Draft status:** this file is a **draft pending supervisor review**. The §1/§2 split, and in
particular the un-obtained Aumann and Schelling definitions, are the items most in need of a
decision (get them from the library, or reframe the report so it does not depend on them).
