# G2 — Emergence and stability of conventions and norms in multi-agent systems

Prepared for issue [#20](https://github.com/M450NCH00/CrowdSimulation/issues/20).
Companion files: [`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md),
[`g3-cheap-talk.md`](g3-cheap-talk.md),
[`g4-game-theoretic-crowd-models.md`](g4-game-theoretic-crowd-models.md),
[`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md),
[`g6-transfer-across-games.md`](g6-transfer-across-games.md),
[`candidate-rule-catalogue.md`](candidate-rule-catalogue.md),
[`search-log.md`](search-log.md), [`refs-game-theory.bib`](refs-game-theory.bib).

The question here: how does a shared rule arise, spread and stabilise across a population; does
it need communication; and what makes it break.

> **Headline finding of this sub-area, stated up front because it is a problem for the FYP.**
> The one human experiment in this file finds that a global convention emerges from purely local
> interaction **only in homogeneously mixing populations**, and **fails to emerge in spatially
> embedded networks** ([Centola-SpontaneousEmergence], Results). A crowd simulation is spatially
> embedded almost by definition. See §"What this means for the FYP" at the end.

---

### [Shoham-SocialLaws]: On the synthesis of useful social laws for artificial agent societies (preliminary report)

- **Authors / Year / Venue:** Yoav Shoham, Moshe Tennenholtz (Robotics Laboratory, Department of
  Computer Science, Stanford University) / 1992 / *Proceedings of the Tenth National Conference on
  Artificial Intelligence* (**AAAI-92**), pp. 276–281.
- **Link:** https://cdn.aaai.org/AAAI/1992/AAAI92-043.pdf (AAAI open proceedings)
- **Peer-review status:** **published**, peer-reviewed conference proceedings. The paper's own
  subtitle calls it a "(preliminary report)".
- ⚠ **This is not the paper the issue named — read this note.** The issue's `[secondhand]` seed
  is the **journal** version: Shoham & Tennenholtz, "On social laws for artificial agent societies:
  off-line design", *Artificial Intelligence* **73**(1–2), 1995, pp. 231–252,
  doi:[10.1016/0004-3702(94)00007-N](https://doi.org/10.1016/0004-3702(94)00007-N). That record is
  **confirmed to exist** (Crossref, cached in `refs/gt_crossref_all.json`, key `shoham1995`) but is
  **paywalled at Elsevier and was not opened**. A 1996 MIT Press reprint
  (doi:10.7551/mitpress/2026.003.0017) is also confirmed and also paywalled. I therefore opened the
  **AAAI-92 conference version**, which is freely available and covers the same model. **Every
  locator below is to the AAAI-92 paper**, and claims should be re-checked against the 1995 journal
  version before the report cites the journal version. A related confirmed record, "On Traffic Laws
  for Mobile Robots (Extended Abstract)", AIPS 1992, doi:10.1016/b978-0-08-049944-4.50057-4, was
  also not opened.
- **Verified:** **yes — full text** of the AAAI-92 version (`refs/gt_shoham1992_aaai.txt`).
- **Sub-area:** G2
- **Tags:** none in the issue's sense; **but note this is a 1992 paper.** The issue permits
  1960s–1990s canonical sources in G1–G3. See the 2016+ pairing note below.
- **Type:** formal theory (complexity analysis)
- **The game or conflict modelled:** **not a game in the payoff sense at all** — and that is the
  point. The conflict is over *shared state* among independently programmed agents: "The planned
  spacetime paths of robots might intersect, an object needed by one robot might be removed by
  another, **bottlenecks might occur**, and so on" (§1). Number of parties is arbitrary. **No
  payoff structure is given**; the model is state-transition based, not utility based.
- **The rule or solution concept:** a **social law**, defined formally, plus a **legal plan** which
  is literally the runtime decision function this FYP is looking for.
  - The motivating example is exactly the supervisor's traffic analogy: "Why not adopt a
    convention, or, as we'd like to think of it, a social law, according to which each robot keeps
    to the right of the path? **If each robot obeys the convention, we will have avoided all
    head-on collisions without any need for either a central arbiter or negotiation.**" (§1)
  - **Definition 2.1** (§2): "Given a set of states S, a first order [language] … and φ ∈ C is a
    sentence. A social law is a set of [pairs]" — i.e. a social law is a set of
    *(action, condition)* pairs, read as **prohibitions**.
  - **Definition 3.1** (§3), the runtime object: "Given a social agent ⟨S, L, A, SL, T⟩ and a
    social law sl ∈ SL, a **legal plan is a total function DO : S → A** such that if (a, φ) ∈ sl
    and s ⊨ φ holds, then DO(s) ≠ a." The paper adds: "Note that a plan forces the agent to take
    action at every step, but we certainly allow the user to include the null action" (§3).
  - **Definition 3.2** (§3) introduces **focal states**: "For this purpose we identify a subset of
    the set of states, which we call focal states. We will be interested in a social law which
    will ensure that each agent, given two focal states, is able to construct a plan guaranteed to
    move him from one state to the other — **no matter what actions are taken by other agents**."
  - **Definition 3.3** (§3), the design problem: "**[The Useful Social Law Problem (USLP)]** Given
    a social multi-agent system and a set of focal states, find a useful law if one exists, or, if
    no such law exists, announce that this is the case."
  - The paper states the design trade-off explicitly (§3): "The more restrictive the law, the more
    can the planner rely on the effects of his actions, but, on the other hand, the more
    restrictive the law, the fewer actions are available to the planner in the first place. In
    selecting a social law we wish to strike a good balance, allowing each agent enough freedom to
    achieve its goals but not enough freedom to foil those of others."
- **Information the rule requires:** **the agent's own current state `s`, and nothing else.**
  `DO : S → A` takes only *s*. No observation of other agents, no shared history, no common
  knowledge of rationality appears in Definition 3.1. What *is* required is that all agents have
  **adopted the same law in advance**: "The society will adopt a set of laws; each programmer will
  obey these laws, and will be able to assume that all others will as well" (§1).
- **One-shot or repeated:** **one-shot, per encounter, with no history.** The legal plan is a
  stateless function of the current state. The convention is population-level and is **acquired by
  offline design, not by learning or by play** — the journal version's subtitle is literally
  "off-line design".
- **Communication required:** **none.** This is the paper's central claim, quoted above (§1):
  collisions are avoided "without any need for either a central arbiter or negotiation". The
  authors are careful not to overclaim: "While we certainly do not argue against the utility of
  either a central coordinator or a negotiation mechanism, we do argue that it is essential to add
  a mechanism that will **minimize the need** for either" (§1). **This is the strongest candidate
  in the entire review for the FYP's runtime rule.**
- **Scalability:** stated, with a precise result, and it cuts **in the FYP's favour**.
  - **Theorem 3.1** (§3): "The USLP is **NP-complete**."
  - But the paper immediately notes why that is acceptable: "We point again that, since the USLP is
    **computed off-line**, this result is not entirely negative" (§3).
  - **Theorem 4.2** (§4): "The BUSLP is polynomial if restrictions 1, 2, and 3 hold, and
    NP-complete otherwise." The first restriction is stated as: "For each state s, the number of
    transitions which might change s is bounded by O(log(n))" where *n* is the number of states
    (§4); the authors add "These three restrictions may or may not be acceptable; although we
    expect that they are reasonable in some interesting applications, we take no stance on this
    here" (§4).
  - [inference] This is the scalability argument the FYP needs for 10,000 agents, and it is a
    *structural* one rather than an optimisation one: **the hard work is NP-complete but paid once,
    offline; the runtime cost per agent per step is one function evaluation.** No LLM call, no
    negotiation, no search. That is what makes 10,000 agents conceivable at all.
- **Validated against human behaviour:** **no.** No human or empirical data; the paper is a
  formal-complexity contribution about robots and programs.
- **Assumptions that may not hold in a crowd:**
  - **Universal compliance.** Every agent obeys the law (§1). A crowd contains agents who push in,
    panic, or ignore conventions. The model has no notion of a defector.
  - **Finite, enumerable state space** with "the number of states in the representation of an agent
    is finite and is denoted by n" and "the total size of an agent's representation is polynomial
    in n" (§3). A continuous-space crowd simulator does not have this without discretisation.
  - **Goals expressed as reachability between focal states** (Definition 3.2) — a strong
    restriction on what an agent can want.
  - **Guarantees are worst-case** ("no matter what actions are taken by other agents",
    Definition 3.2), which is stronger than a crowd model usually needs and may make useful laws
    non-existent where a probabilistic guarantee would suffice.
- **Limitations stated by the authors:** the NP-completeness of the general problem (Theorem 3.1);
  the explicit refusal to claim the polynomial-case restrictions are realistic ("we take no stance
  on this here", §4); and the paper's own self-description as a "preliminary report".
- **Relevance to this FYP:** **this is the paper the FYP's whole design should be built on top
  of.** Concretely:
  - It gives the **formal type** of the thing being extracted: `DO : S → A`, a total function from
    observable state to action. The issue's implementability test ("could this be written as a
    function mapping observable agent state to an action, for each agent, with no dialogue at
    runtime?") is, almost word for word, Definition 3.1.
  - It gives the **argument for why extraction is worth doing at all**: offline design cost,
    online execution cost. That is the honest answer to "why not just call the LLM each time".
  - It gives the **vocabulary** — social law, legal plan, focal state, useful law — which is more
    precise than "pattern" and is already standard in multi-agent systems.
  - [inference] It also reframes the FYP's contribution in a way worth putting to the supervisor:
    Shoham & Tennenholtz **synthesise** social laws by search, and prove that search is
    NP-complete. The FYP would instead **elicit** them from an LLM. That is a different method for
    the same problem, and it makes the FYP's research question sharper: *is an LLM a usable
    heuristic for an NP-complete offline design problem?* This is a design-decision-level framing
    choice and needs sign-off.
- **BibTeX:** `shoham1992synthesis` (AAAI-92, read) and `shoham1995social` (AIJ 1995, confirmed
  but not read).

---

### [Centola-SpontaneousEmergence]: The spontaneous emergence of conventions: An experimental study of cultural evolution

- **Authors / Year / Venue:** Damon Centola, Andrea Baronchelli / 2015 / *Proceedings of the
  National Academy of Sciences* **112**(7), pp. 1989–1994.
- **Link:** doi:[10.1073/pnas.1418838112](https://doi.org/10.1073/pnas.1418838112) · PMC4343158
- **Peer-review status:** **published**, peer-reviewed journal.
- **Verified:** **yes — full text**, read from the PMC copy (`refs/gt_centola2015_pmc.txt`).
  Locators are to the article's named sections (Significance / Introduction / Results / figure
  captions), since the PMC rendering does not carry page numbers.
- **Sub-area:** G2
- **Tags:** none (2015; just outside the 2016+ preference, retained because it is the **human
  experiment** that anchors this sub-area and is the direct human counterpart to the LLM result in
  [`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md))
- **Type:** human experiment (web-based, controlled, with model comparison)
- **The game or conflict modelled:** a **naming game** — a pure coordination problem, not an
  anti-coordination conflict. "Both players simultaneously assigned names to a pictured object
  (i.e., a human face), blindly attempting to coordinate in the real-time exchange of naming
  choices … If the players coordinated on a name, they were rewarded with a successful payment; if
  they failed, they were penalized" (Results, experimental design paragraph). Two parties per
  round; the population is *n* = 24, 48 or 96. ⚠ [inference] **This is a coordination game, not a
  conflict game**, so it does not itself qualify under G1's criterion; it qualifies here under
  criterion (b) — evidence about when convention-formation rules do and do not work.
- **The rule or solution concept:** an **emergent convention**, with no solution concept imposed.
  The paper's thesis is stated in the Significance statement: "the simplest explanation is that
  universally accepted conventions are the unintended consequence of individuals' efforts to
  coordinate locally with one another."
- **Information the rule requires:** **strikingly little, and the paper engineered it that way.**
  "Participants in our study did not have any information about the size of the population that was
  attempting to coordinate nor about the number of neighbors to whom they were connected"
  (Results). "After a single round, the participants could see only the choices that they and their
  partner had made, and their cumulative pay was updated accordingly" (Results). And from the
  Significance statement: global conventions emerge "even though people have no knowledge about
  the population, or that they are coordinating at a global scale." The paper explicitly contrasts
  itself with prior work that assumed "either an explicit reward for universal coordination or a
  mechanism that aggregates and reports the collective state of the population, which has made it
  impossible to evaluate the hypothesis that global coordination is the result of purely local
  incentives" (Introduction).
- **One-shot or repeated:** **repeated, and the number of rounds matters.** Convention formation in
  the mixing condition takes ~20–22 rounds: "In all trials, an emergent convention grew quickly,
  reaching over 60% of the population by round 12, and achieving universal adoption between rounds
  20 and 22" (Results). Individual *application* is per-encounter and stateless once the convention
  exists: "by round 22, players who had never interacted with one another were all using the same
  convention and were able to consistently coordinate with new partners" (Results).
- **Communication required:** **none beyond the action itself.** Players exchange only their naming
  choices; there is no side channel. The name *is* the action. [inference] So this is a
  convention-discovery process that runs on actions alone — which is directly relevant to the
  cheap-talk question in [`g3-cheap-talk.md`](g3-cheap-talk.md).
- **Scalability:** **stated, tested, and positive — up to n = 96.** The authors raise the question
  themselves: "The speed of self-organized conventions in these networks raises the question of
  whether these coordination dynamics scale up as population sizes increase. There are good reasons
  for skepticism" (Results), and give those reasons: more competing alternatives, and a smaller
  fraction of the population reachable in a fixed number of rounds. They then test it: "As a final
  test of increasing scale, we replicated a trial of the homogenously mixing population in which
  the network size was again doubled. Figure 4 shows that a shared social convention spontaneously
  emerged in a population of n = 96 subjects. Global coordination in the n = 96 population emerged
  on a time scale comparable to that of the initial trials (n = 24), despite the fact that subjects
  had no information about how large the coordinating population was" (Results). Summary claim:
  "large homogenously mixing populations were significantly more likely (P < 0.01) to spontaneously
  create social conventions than smaller populations with less connectivity" (Results). **No
  computational cost is involved — these are human subjects.** `[not stated in paper]` for compute.
- **Validated against human behaviour:** **yes — it *is* human behaviour.** Web-based controlled
  experiment; n = 24 (eight independent trials, figure 1 caption), n = 48 (figure 3 caption), and
  one n = 96 trial (Results, figure 4).
- **⚠ The result that matters most to this FYP — network structure decides the outcome:**
  - **Spatially embedded networks: global convention FAILS.** "In spatial networks, populations
    enjoyed rapid local coordination, in some cases achieving a 50% success rate … as early as
    round 4. However, this initial success rate quickly decelerated. After 25 rounds of play,
    average success rates failed to reach above 75%. Throughout all of the spatial network trials,
    the dominant local conventions … were never used by more than 45% of the population" (Results).
    Mechanism: "behavior in the spatial networks evolved through a process of local coarsening, in
    which emergent regions of coordinated behavior competed with bordering local conventions. In
    each of the trials, these dynamics inhibited the spontaneous emergence of global coordination
    by creating entrenched competition between endogenously formed groups" (Results).
  - **Random networks: also FAILS.** "In all random network trials, global social conventions never
    emerged. Moreover, the sizes of the dominant social conventions … were equivalent across all
    trials of the spatial and random networks, averaging 33% of the population" (Results).
  - **Homogeneously mixing populations: SUCCEEDS.** "In all trials with homogenously mixing
    populations, success rates increased to 100% well before the end of the study" (Results). And
    the mechanism is counter-intuitive: "Initially, success rates were lower because actors did not
    have repeated interactions with their partners, which prevented 'neighborhoods' of entrenched
    behavior from forming. However, **local failure accelerated global coordination**" (Results).
- **Assumptions that may not hold in a crowd:** the successful condition assumes **random global
  re-pairing every round** — any agent may meet any other. A crowd is the opposite: you interact
  with whoever is physically adjacent. [inference] By this paper's own results, a crowd is the
  *spatial* condition, which is the condition where global conventions **do not** form.
- **Limitations stated by the authors:** the scale limitation is addressed rather than left open
  (n = 96 max); the time-scale caveat is stated: "Within the brief time scale of the experimental
  observations (30 rounds of play on average)…" (Results), i.e. the spatial networks might converge
  eventually, just not within the observed window. The authors also note that prior small-group
  results can be "qualitatively different from the dynamics in larger groups" (Introduction), which
  is a caution against extrapolating their own numbers either way.
- **Relevance to this FYP:** it supplies the sub-area's **human ground truth**, and it supplies a
  **serious problem** that the FYP should raise with the supervisor rather than discover later:
  - [inference] If the FYP's plan were "let agents discover a convention through local interaction
    in the simulation", this paper predicts it will produce **competing regional conventions with a
    contested boundary** — exactly the kind of standoff the FYP is trying to eliminate — because
    the crowd is spatially embedded.
  - [inference] That is in fact an **argument for the FYP's actual approach**: extract the
    convention **offline from an LLM** and install it in every agent, rather than hoping it emerges
    in-simulation. The convention then arrives pre-shared, sidestepping the symmetry-breaking
    problem entirely. This paper is the evidence for why the offline route is the right one, and
    that is a strong point to put in the report.
- **BibTeX:** `centola2015spontaneous`.

---

### [MorrisMartin-NormEmergence]: Norm emergence in multiagent systems: a viewpoint paper

- **Authors / Year / Venue:** Andreasa Morris-Martin, Marina De Vos, Julian Padget / 2019 /
  *Autonomous Agents and Multi-Agent Systems* **33**(6), pp. 706–749.
- **Link:** doi:[10.1007/s10458-019-09422-0](https://doi.org/10.1007/s10458-019-09422-0)
- **Peer-review status:** **published**, peer-reviewed journal (Springer), open access. A related
  AAMAS extended abstract is also confirmed (doi:10.65109/vefw9936, 2020) and was not opened.
- **Verified:** **yes — full text** (`refs/gt_morrismartin2019_jaamas.txt`, publisher PDF).
- **Sub-area:** G2
- **Tags:** none (2019)
- **Type:** survey
- **The game or conflict modelled:** none specifically — it surveys the field. Relevant because it
  records **how the MAS literature operationalises "a convention has emerged"**, which the FYP will
  need in order to *measure* success.
- **The rule or solution concept:** it catalogues rather than proposes. Key operational definition
  (p. 710, §on norm emergence): "For a large number of agent societies, **norm emergence is
  observed when a large percentage of the population adopts the norm or chooses the same
  action**", and the survey reports the thresholds actually used: "percentages range from **35 to
  100**" (p. 716). It also records the top-down/bottom-up distinction in the Abstract: norms "can be
  established or revised from the top-down (authority) or from the bottom-up (populace)."
- **Information the rule requires:** varies by surveyed approach. The survey notes a
  representational trade-off (p. 712): "When an implicit norm representation is used, there is no
  need for agents to have an [explicit norm representation]" — i.e. some approaches need agents to
  reason about the norm, others only to behave consistently with it.
- **One-shot or repeated:** the surveyed emergence processes are all repeated/population-level by
  construction.
- **Communication required:** varies; the survey covers both communicating and non-communicating
  approaches. It notes that some designs plant influential agents: "agents to influence convention
  emergence. These agents may be planted in the society" (p. 717).
- **Scalability:** `[no single result]`. The survey does not give a general cost bound. What it
  *does* give is a structural failure mode with a scale flavour — see next bullet.
- **⚠ The failure mode this file exists to record — sub-conventions.** This is the MAS-literature
  version of Centola's spatial-network result, and it corroborates it from simulation:
  - "**Sub-conventions** [102,103] are an obstacle to 100% convergence. They can emerge in agent
    societies, where a smaller set of agents converge to a norm that is different from the norm of
    the majority of the population. These agents are usually located in **isolated regions where
    they are not likely to interact with the larger population**" (p. 716).
  - "Villatoro et al. [102] refers to regions of a network that can maintain a sub-convention as
    **Self Reinforcing Substructures (SRS)**. Unfortunately, these sub-conventions can **persist
    throughout the simulation run if no mechanism is in place to resolve them**" (p. 716).
  - "Hu and Leung [57] study local norm emergence … They study a community network structure where
    there are dense connections in small communities and sparse connections between communities
    within a population. Results show that from a set of norms with equal payoff, **diverse norms
    emerge in the system within individual communities: local norm emergence, with no global norm
    emergence observed**" (p. 716).
  - The survey also flags an unresolved measurement problem: "In the literature, there is little or
    no mention of how long it is acceptable for this percentage [to be reached]" (p. 716).
- **Validated against human behaviour:** **no** — it surveys agent-based work.
- **Assumptions that may not hold in a crowd:** as a survey, it inherits all of them; its own
  caution is that the surveyed field lacks agreement on both the convergence threshold and the
  acceptable time-to-convergence (p. 716).
- **Limitations stated by the authors:** the paper is explicitly a "viewpoint paper" (title) whose
  third contribution is "future topics for study … through a discussion of the challenges and
  opportunities in norm emergence" (Abstract) — i.e. it presents the field as unsettled.
- **Relevance to this FYP:**
  - Gives a **defensible, citable success metric**: percentage of the population adopting the same
    action, with the literature's own range of 35–100% (p. 716). The FYP will need exactly this to
    validate an extracted rule, and "explainable and defensible in a report" is a stated
    requirement for this project.
  - **Independently corroborates** [Centola-SpontaneousEmergence]'s spatial failure, from a
    different method (simulation rather than human experiment) and a different literature. Two
    independent routes to the same conclusion is much stronger than one.
  - Supplies the vocabulary **Self Reinforcing Substructure** for the failure mode. [inference] In
    crowd terms: two halves of a corridor settling on opposite conventions and deadlocking at the
    midpoint. Naming it makes it testable.
- **BibTeX:** `morrismartin2019norm`.

---

### [Lewis-Convention]: Convention: A Philosophical Study `[foundational]`

- **Author / Year / Venue:** David Lewis / 1969 / Harvard University Press. A 2002 Blackwell
  reissue is the record Crossref indexes: doi:[10.1002/9780470693711](https://doi.org/10.1002/9780470693711).
  A contemporary review is also indexed, confirming the original: *The Philosophical Quarterly*
  **20**(80), 1970, p. 286, doi:[10.2307/2218418](https://doi.org/10.2307/2218418).
- **Peer-review status:** **scholarly monograph** (not peer-reviewed in the journal sense).
- **Verified:** **bibliographic record only.** The book was **not** opened — it is a printed
  monograph and no open copy was located. The issue notes that "a book chapter locator is a page
  range"; **I have no page range to give**, because I did not read it.
- **Justification for `[foundational]`:** Lewis is the standard primary source for the analysis of
  a convention, and the FYP proposes to call its extracted object a convention.
- **⚠ Requirement not met.** The issue asks me to "Confirm and record the definition." Confirmed to
  exist; **definition not recorded**, because the text was not read. What can be said with a
  locator is that Lewis's account is one of those that "involve agents' expectations or beliefs
  about the behaviour of other agents", **as characterised by** [Foley-ConflictConvention] §4
  (whose reference [56] is Lewis 1969) — and that this is a point of **contrast**, since Foley's
  agents have no such beliefs. [inference] That contrast is itself useful to the FYP: if Lewis
  requires mutual expectation and the FYP's agents have none, then "convention" in Lewis's sense
  may be the wrong word for what the FYP extracts. Pursued in
  [`search-log.md`](search-log.md) §framing check.
- **2016-or-later pairing:** [Centola-SpontaneousEmergence] (2015) and
  [MorrisMartin-NormEmergence] (2019) both operationalise convention emergence empirically and
  were read in full; [Ashery-EmergentConventions] (2025) in
  [`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md) cites the convention literature
  directly and was read in full.
- **BibTeX:** `lewis1969convention`.

### [Young-EvolutionOfConventions]: The Evolution of Conventions `[foundational]`

- **Author / Year / Venue:** H. Peyton Young / 1993 / *Econometrica* **61**(1), pp. 57–84.
- **Link:** doi:[10.2307/2951778](https://doi.org/10.2307/2951778)
- **Peer-review status:** published, peer-reviewed journal.
- **Verified:** **bibliographic record only** (Crossref, cached). JSTOR paywalled; **full text not
  opened.**
- **Justification for `[foundational]`:** it is the canonical formal treatment of how conventions
  evolve in a population, and it supplies the definition that the papers I *did* read actually
  quote.
- **What can be said with a source:** Young's definition of a convention, **as quoted by**
  [Foley-ConflictConvention] §4: "Peyton Young defines a convention as a 'pattern of behaviour that
  is customary, expected and self-enforcing'". That is a quotation of Young *inside* a paper I read
  in full, and it is attributed as such — **not** presented as my own reading of Young.
- **2016-or-later pairing:** [Foley-ConflictConvention] (2018), read in full, is an explicit modern
  test of convention evolution and equilibrium selection, citing Young for both the definition and
  the equilibrium-selection problem (§4).
- **BibTeX:** `young1993evolution`.

---

## What this means for the FYP

Three things, in order of importance. All three are [inference] unless marked otherwise.

1. **The formal type of the deliverable is settled, and it has a name.** `DO : S → A`, a total
   function from observable state to action, obeying a set of prohibitions fixed offline
   ([Shoham-SocialLaws], Definitions 2.1 and 3.1). The FYP should adopt this vocabulary — *social
   law*, *legal plan* — because it is precise, standard in multi-agent systems, and already carries
   the offline/online cost split the 10,000-agent target depends on (Theorem 3.1 plus the
   "computed off-line" remark, §3).

2. **Do not plan to let the convention emerge inside the simulation.** Two independent sources say
   it will not work in a spatially structured population: a human experiment
   ([Centola-SpontaneousEmergence], Results — spatial and random networks never reached global
   convention; dominant conventions averaged 33% of the population) and a survey of agent-based
   work ([MorrisMartin-NormEmergence], p. 716 — Self Reinforcing Substructures persist "if no
   mechanism is in place to resolve them"; Hu & Leung observed "no global norm emergence"). A crowd
   is spatially structured. **This is positive news for the FYP's chosen method**, because
   extracting the rule offline from an LLM and installing it in every agent makes the convention
   pre-shared and skips the symmetry-breaking problem that defeats in-simulation emergence.

3. **There is a citable success metric, and a gap next to it.** "A large percentage of the
   population adopts the norm or chooses the same action", with reported thresholds of 35–100%
   ([MorrisMartin-NormEmergence], p. 710 and p. 716) — **not** inference, that is the survey's
   wording. The gap the same page records is that nobody agrees how *fast* convergence must be.
   The FYP will have to pick a threshold and a time budget and defend both; picking them from this
   survey's range is more defensible than inventing them.

**Draft status:** draft pending supervisor review. The open item is whether the report adopts
Shoham & Tennenholtz's "social law" framing in place of "conflict-resolution pattern" — that is a
design decision, not an assumption, and it needs sign-off.
