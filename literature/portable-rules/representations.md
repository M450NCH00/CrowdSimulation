# Representations: how other fields write rules down independently of what runs them

> For issue [#35](https://github.com/M450NCH00/CrowdSimulation/issues/35) (PT-1 of the
> portable-rules track, [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34)). Work
> done on 2026-10-18. One entry per source, in the issue's template, grouped as the issue's seed
> leads are, plus a sixth group for Q2's precedent studies (work log A6).

Companion files: [feasibility](feasibility.md) · [verdict](verdict.md) ·
[novelty check](novelty-check.md) · [search log](search-log.md) ·
[missing papers](missing-papers.md) · [refs](refs-portable-rules.bib)

**How to read an entry.**
- Every claim carries a locator: a section (§), table, figure, equation, paragraph number (JASSS
  articles number their paragraphs) or page. Quotations are verbatim from the cached text named in
  the entry.
- `[inference]` marks my own reasoning. The line "For the portable rule core" is always
  `[inference]`.
- Status labels: `[preprint]`, `[standard]`, `[documentation]`. Anything unlabelled is published
  and peer reviewed.
- A source I could not open has a **stub** of exactly six lines and no summary. All stubs are
  listed in [missing-papers.md](missing-papers.md).

**Groups**
1. [Institutional grammar](#1-institutional-grammar)
2. [Normative multi-agent systems](#2-normative-multi-agent-systems)
3. [Simulation interoperability](#3-simulation-interoperability)
4. [Behaviour layers in crowd and robot simulators](#4-behaviour-layers-in-crowd-and-robot-simulators)
5. [Taxonomies](#5-taxonomies)
6. [Precedent: the same rule in more than one simulator](#6-precedent-the-same-rule-in-more-than-one-simulator)

Cross-references only, not summarised again (as the issue asks): Shoham and Tennenholtz's social
laws, [`../game-theory/g2-norm-emergence.md`](../game-theory/g2-norm-emergence.md); Zhang et al.
2026, decision functions written as code,
[`../paper-summaries/02-sense-think-act-reflect.md`](../paper-summaries/02-sense-think-act-reflect.md).

---

## 1. Institutional grammar

The original grammar (ADICO, Crawford and Ostrom 1995) could not be obtained ([stub
below](#crawford-adico-a-grammar-of-institutions)). Its five components are cited in this review
**as [Frantz-IG2] quotes them** (§2 there), not from the 1995 paper.

### [Frantz-IG2]: Institutional Grammar 2.0: A specification for encoding and analyzing institutional design

- Authors / Year / Venue: Christopher K. Frantz, Saba Siddiki / 2021 / *Public Administration*
  99(2), 222–247 (Wiley).
- Link: https://doi.org/10.1111/padm.12719 | accepted manuscript:
  https://hdl.handle.net/11250/3032234
- Status: published at *Public Administration* (Crossref record). Read as the accepted
  manuscript, which "has not been through the copyediting, typesetting, pagination and
  proofreading process" (its first page). Section numbers are the manuscript's.
- Read: full text, from `refs/pr_frantz2021_ig2_padm_accepted.txt`. ⚠ Figures 1–14 are images, and
  only their captions survive in the extract. Nothing below rests on a figure's content.
- What it represents: norms, rules and strategies as written in policies and regulations
  ("institutional statements"), and "constitutive" statements that define entities and roles.
- Structure:
  - **The original grammar, as quoted here** (§2): Attribute (A) "identifies to whom an
    institutional statement applies"; Aim (I) "the activity linked in an institutional statement
    to the Attribute"; Condition (C) "the temporal, spatial, or procedural parameter that
    describes when, where and how the statement applies"; Deontic (D) "the prescriptive operator
    that indicates whether the Attribute is required, allowed, or forbidden to perform the
    specified Aim within noted Conditions"; Or else (O) "a payoff associated with the fulfillment
    of the institutional statement". A statement with AIC is a *strategy*, with ADIC a *norm*, and
    with all five a *rule* (§2). Siddiki et al. (2011) added the Object (B) (§2).
  - **IG 2.0's changes** (§3.1):
    - the Attribute separates the actor from its properties;
    - the Object splits into direct and indirect;
    - the Deontic is "unchanged" but "explicitly recognizes the continuity of the concept" (may,
      should, must);
    - several Aims are split into atomic statements joined by AND, OR or XOR ("horizontal
      nesting");
    - the Condition, renamed **Context**, splits into **Activation Conditions**, which "describe
      conditions under which a statement is activated as a whole", and **Execution
      Constraints**, which "qualify the action of a statement and thus guide its execution";
    - the Or else becomes a complete nested statement ("vertical nesting", from nADICO, Frantz et
      al. 2013).
  - **Three levels of expressiveness**, each subsuming the one below (§3): IG Core; IG Extended,
    adding component-level nesting, property hierarchies and a Context taxonomy (§3.2); and IG
    Logico, adding role and institutional-function annotations, statement cross-references and
    transformation rules (§3.3).
  - **Constitutive statements**, coded PMFECO: Constituting Properties, Modal, Constitutive
    Function, Constituted Entity, Context, Or else. F, E and C are necessary (§4.1).
- Executable or descriptive: **descriptive; a system must translate it first.** IG is an encoding
  of text for analysis. IG Extended "builds a bridge between advanced computational analyses while
  generating coded institutional information that is still human readable" (§3). IG Logico
  "provides an interface for reasoning over policies and institutions more generally as well as
  supporting advanced computational models" (§3.3). The paper cites agent-based uses (Smajgl et
  al. 2008; Frantz et al. 2015; §2) but defines no execution semantics itself. Its syntax and
  semantics are deferred to online resources (§3.3; Appendix).
- How it travels between systems: as a shared coding specification, applied by human coders with
  a codebook ([Frantz-IG2Codebook]). Executing one coded statement in two systems is not
  discussed.
- Evidence that it works in two or more systems: none reported. §2 cites applications across
  policy domains; none runs one coded statement in two systems.
- Failure modes and limits stated by the authors:
  - the original grammar has "ontological inconsistencies ... that challenge conceptual and
    operational distinction among syntactic components" (§1);
  - coders' "over-commitment to retaining the structural integrity of institutional statements in
    syntactic parsing ... sometimes amounts to a loss of semantic integrity". Sanctions can sit in
    other sections, and "institutional statements do not always correspond to sentences" (§2);
  - rewording statements to fit the regulative pattern led "to reliability challenges" (§2);
  - IG Extended "imposes more responsibility and cognitive load on the coder" (§3.2), and IG Logico
    comes "at the expense of general accessibility to coders" (§3.3);
  - the Context taxonomy "is not assumed to be exhaustive" (§3.2);
  - "the IG is an approach that is relatively nascent", and the authors "urge the user community to
    challenge its theoretical and operational foundations" (§5).
- For the portable rule core: **adapt** [inference].
  - Its parts map one-to-one onto #34's list: Attribute ↔ role, Deontic ↔ must / may / must not,
    Aim ↔ action, Object ↔ the other party or the contested thing, Or else ↔ what follows a breach.
  - The most useful single idea is the **Activation Condition / Execution Constraint split**. It
    gives *when a rule applies* (the core's conflict type and features) a different place from
    *how the action is qualified* (which side; until clear). A simulator's "how much" binding
    would sit beneath an Execution Constraint, not replace it.
  - What IG does not give: a closed vocabulary (its taxonomies are open, §3.2), execution
    semantics, or any account of two systems reading the same statement the same way.
- BibTeX: `frantz2021ig2`

---

### [Frantz-IG2Codebook]: Institutional Grammar 2.0 Codebook

- Authors / Year / Venue: Christopher K. Frantz, Saba N. Siddiki / version 1.4, 20 October 2024
  (first posted 2020) / arXiv:2008.08937v5 [cs.MA].
- Link: https://arxiv.org/abs/2008.08937
- Status: `[preprint]`. It is a coding manual that accompanies [Frantz-IG2] and the authors' 2022
  book. The arXiv record's DOI field points to the *Public Administration* paper
  (10.1111/padm.12719), not to the codebook. No separately published version.
- Read: these sections: 1.1, 2.1–2.6, 4.1 (coding symbols; IG Script syntax), 4.6 (profiles,
  opening), 5 (taxonomies), 6 and 7, from `refs/pr_arxiv_2008_08937v5_ig2_codebook.txt`. Also the
  README of the IG Parser, which reads IG Script, `[documentation]`, accessed 2026-10-18
  (`refs/pr_igparser_readme_2026-10-18.md`). Not read: §3 and §§4.2–4.5 (worked coding examples,
  about 80 of the 122 pages).
- What it represents: rules and norms in text, coded as institutional statements.
- Structure:
  - **Regulative components** (Table 2, §2.1):
    - Attributes: "An actor (individual or corporate) that carries out, or is expected to/to not
      carry out, the action (i.e., Aim) of the statement";
    - Deontic: "A prescriptive or permissive operator that defines to what extent the action of
      an institutional statement is compelled, restrained, or discretionary", with strengths that
      "situate along a continuum";
    - Aim: "The goal or action of the statement assigned to the statement Attribute";
    - Object: "The inanimate or animate part of an institutional statement that is the receiver
      of the action", direct or indirect, possibly abstract, possibly a statement itself;
    - Context: an "Activation Condition" (instantiates the setting) or an "Execution Constraint"
      (qualifies the action), defaulting to "under all conditions" and "no constraints";
    - Or else: "A sanctioning provision ... represented in a nested institutional statement".
  - Attributes, Aim and Context are necessary; Object, Deontic and Or else are optional (§1.1).
  - The Or else "does not reflect an IG component, but rather a logical connective that links two
    institutional statements". Consequences can nest "across an arbitrary number of levels"
    (§2.2.2).
  - **Action situations.** Statements sit in an action situation governed by seven rule types:
    position, boundary, choice, scope, information, aggregation and pay-off rules (§2.4, after
    Crawford and Ostrom 2005). Position rules give the "positions that actors can occupy within an
    action situation"; information rules the "channels of information flow" (§2.4).
    Activation Conditions "precede the regulated action and activate a given institutional
    statement in the first place"; Execution Constraints "describe constraints on actions once
    enacted" (§2.4).
  - **IG Script**, a machine-readable notation: `componentSymbol(content)`, braces for nesting,
    square brackets for annotations. For example, `A(citizen) D(must) I(conform) with Bdir(policy)
    O{A(official) D(may) I(sanction) Bdir(citizen) Cex(immediately)}` (§4.1.2).
  - **Profiles** state which features a dataset uses, e.g. `IG Core+CExt`. "A coded dataset should
    be accompanied with the applied coding configuration" (§4.6).
  - **Taxonomies** (§5):
    - Context: temporal, spatial and domanial; procedural order and method; purpose; state; event
      (§5.1);
    - Role: originator, recipient, possessor, experiencer, advantaged, disadvantaged (§5.4);
    - Regulative functions: comply/violate; detect compliance/violation; reward/sanction;
      accept/reject/appeal (§5.5);
    - Animacy, Metatype and Constitutive functions (§5.2, §5.3, §5.6).
  - **Statement-level annotations** mark statements as monitored, consequential or monitoring. The
    last is for "a third-party observer (e.g., bystander, appointed monitor), who may or may not
    be the enforcer" (§6.1).
- Executable or descriptive: **descriptive, but machine-readable.** IG Script "manages the
  trade-off between computational representation on the one hand, and retaining general human
  readability of the encoded text on the other" (§4.1.1). The IG Parser turns it into tabular
  output (Google Sheets or CSV) or a visual statement tree (README, "Tabular output" and "Visual
  output"). That is data for analysis, not decisions a system carries out.
- How it travels between systems: a shared, versioned specification. The coding instructions are
  "intentionally tool-agnostic, and open to adaptation to arbitrary encoding means (e.g.,
  spreadsheets, text annotation tools, etc.)" (§7). Levels are "backward-compatible, i.e.,
  statements coded at higher levels of expressiveness can be reduced to any lower level of
  expressiveness" (§2.6). Extending a taxonomy "is explicitly permitted", if declared in the
  dataset specification (§5).
- Evidence that it works in two or more systems: none reported in the sections read.
- Failure modes and limits stated by the authors:
  - telling an Activation Condition from an Execution Constraint "necessitates understanding of the
    institutional domain. Without this, the coder may encounter difficulty" (§2.4);
  - whether a statement is coded as regulative or constitutive can depend on the coder's
    "interpretational scope", and "a potential inconsistent interpretation of statements of such
    character can lead to reliability challenges" (§2.5);
  - the taxonomies "are subject to ongoing empirical evaluation and may experience refinement in
    the future" (§5); the regulative-functions taxonomy "does not claim exhaustiveness" (§5.5).
- For the portable rule core: **adapt** [inference]. Three parts are directly reusable:
  1. the action-situation rule types. Their *position* rules are what #34 calls roles given by
     position, and their *information* rules are its "note of who can know it";
  2. **profiles**, as the model for a rule set declaring which vocabulary version and features it
     uses;
  3. the regulative-function and monitoring annotations. They give a queue-cutting rule a place
     for "violate", "detect violation", and a bystander who may or may not enforce.

  What the codebook cannot supply is a closed vocabulary: every taxonomy in it is explicitly open.
- BibTeX: `frantz2024ig2codebook`

---

### [Crawford-ADICO]: A Grammar of Institutions

- Title: A Grammar of Institutions
- Authors, year and venue: Sue E. S. Crawford, Elinor Ostrom / 1995 / *American Political Science
  Review* 89(3), 582–600, doi:10.2307/2082975
- Link tried: https://doi.org/10.2307/2082975 (Cambridge Core); OpenAlex open-access lookup; web
  search for a repository copy
- Reason unavailable: paywalled; OpenAlex reports no open copy; the only free copy found is a
  JSTOR printout on a third-party site, which I did not use
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

---

### [Frantz-DynamicDeontics]: Modelling Institutions Using Dynamic Deontics

- Title: Modelling Institutions Using Dynamic Deontics
- Authors, year and venue: Christopher Frantz, Martin K. Purvis, Mariusz Nowostawski, Bastin Tony
  Roy Savarimuthu / 2014 / *Coordination, Organizations, Institutions, and Norms in Agent Systems
  IX*, Lecture Notes in Computer Science, Springer, pp. 211–233, doi:10.1007/978-3-319-07314-9_12
- Link tried: https://www.academia.edu/22055003/Modelling_Institutions_Using_Dynamic_Deontics
  (HTTP 403); https://doi.org/10.1007/978-3-319-07314-9_12; OpenAlex open-access lookup
- Reason unavailable: Springer paywall; OpenAlex reports no open copy; Academia.edu refused access
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

---

### [Frantz-IGBook]: Institutional Grammar: Foundations and Applications for Institutional Analysis

- Title: Institutional Grammar: Foundations and Applications for Institutional Analysis
- Authors, year and venue: Christopher K. Frantz, Saba N. Siddiki / 2022 / Palgrave Macmillan
  (Springer International Publishing), book, doi:10.1007/978-3-030-86372-2
- Link tried: https://link.springer.com/book/9783030863715; https://doi.org/10.1007/978-3-030-86372-2;
  OpenAlex open-access lookup
- Reason unavailable: paywalled book; OpenAlex reports no open copy
- Date attempted: 2026-10-18
- Status: awaiting PDF from user

---

## 2. Normative multi-agent systems

### [Neumann-HomoSocionicus]: Homo Socionicus: a Case Study of Simulation Models of Norms

- Authors / Year / Venue: Martin Neumann / 2008 / *Journal of Artificial Societies and Social
  Simulation* 11(4), 6.
- Link: https://www.jasss.org/11/4/6.html (no DOI is shown on the article page)
- Status: published at JASSS (received 11 December 2007, accepted 17 June 2008; article page).
- Read: full text (the HTML article, ¶1.1–¶7.7 and notes), from
  `refs/pr_jasss_11_4_6_neumann2008.txt`.
- What it represents: a survey of normative agent-based **social simulation** models, examined
  from sociological role theory (Abstract; ¶1.2).
- Structure: the survey defines no structure for a norm. It judges models by three
  "methodological core problems" (Abstract): *transmission* (how norms spread), *transformation*
  (what makes agents follow them, including internalisation) and *function* (what norms do for the
  society) (¶3.2). It sorts models into two traditions (¶4.3):
  - **game-theoretic**: a norm exists, after Axelrod, to "the extent to which individuals usually
    act in a certain way and are often punished when seen not be acting in this way" (¶5.3);
  - **cognitive (AI)**: a norm is "an explicit action routine", e.g. the finder-keeper norm of
    Conte and Castelfranchi (¶5.21, ¶5.27).
  Table 4 (¶6.2) records each model's *implementation* of norms: "dynamical propensities",
  "conditional strategies", "decision tree", or a threshold.
- Executable or descriptive: **executable, but only as each model's own code.** No model in the
  survey has a norm representation separate from its implementation (Table 4, ¶6.2). In the
  game-theoretic models agents "do not 'know' norms. Their behaviour can only be interpreted as
  normative from the perspective of an external observer" (¶5.17). The conclusion asks for future
  work "based on explicit representations of norms" (¶7.7).
- How it travels between systems: not addressed. The two traditions even use different terms:
  "Tradition and theoretical background has a direct impact on the terminology used" (¶4.3).
- Evidence that it works in two or more systems: none as such. The survey notes that Axelrod's
  1986 model "has been analysed and replicated several times" and Conte and Castelfranchi's
  "replicated several times" (¶5.2), and that a re-implementation found Axelrod's metanorm result
  "not unequivocal" (Note 7, citing Galán and Izquierdo 2005: [Galan-Reimplementing] in group 6).
- Failure modes and limits stated by the author:
  - "the degree of resolution of intra agent processes remains too low for a comprehensive
    understanding of normative behaviour regulation" (Abstract);
  - an advisor agent with "global knowledge of all successful proposal values" makes a model work,
    but risks "intermixing a target system with a computational trick". In the real world it
    "would equate to an omniscient central bureaucracy" (¶6.21–¶6.22);
  - an internalisation formula is implemented "on a rather ad hoc basis" and can produce an effect
    "similar (but not identical) to processes in human societies" without representing them
    (¶6.12).
- For the portable rule core: **reject as a representation; keep as evidence** [inference].
  - It offers no representation to adopt.
  - It shows that by 2008 normative social simulation kept every norm inside model-specific code
    (Table 4), so no shared norm format came from that field.
  - Its "computational trick" warning (¶6.22) applies to a standalone rule engine that decides
    from a global Situation. If a Situation holds a feature no claimant could know, a rule that
    reads it is that trick. #34's "a note of who can know it" for each feature, and today's
    "what a rule may read" (`llm_negotiation/docs/rule-format.md` §5), are the guard against it.
- BibTeX: `neumann2008homosocionicus`

---

### [Hollander-NormativeABS]: The Current State of Normative Agent-Based Systems

- Authors / Year / Venue: Christopher D. Hollander, Annie S. Wu / 2011 / *Journal of Artificial
  Societies and Social Simulation* 14(2), 6.
- Link: https://doi.org/10.18564/jasss.1750 | https://www.jasss.org/14/2/6.html
- Status: published at JASSS (received 7 September 2010, accepted 20 February 2011; article
  page). This is the issue's "JASSS 14(2), 6" lead; title and authors are now confirmed.
- Read: full text (the HTML article, ¶1.1–¶6.6), from `refs/pr_jasss_14_2_6_hollander2011.txt`.
- What it represents: a survey of norms in multi-agent systems and agent-based simulation, with a
  "norm life cycle" model (¶1.4, ¶3.1).
- Structure: no single structure; four **representation schemes** "used in recent research"
  (¶2.19):
  1. **modal (deontic) logic**: "obligations, permissions, and prohibitions" (¶2.20);
  2. **condition/action pairs** in rule-based systems, "commonly used by systems that take
     advantage of offline design, where the norms are coded directly into the agent's decision
     making system" (¶2.21);
  3. **binary strings**, where each digit marks the presence or absence of a norm (¶2.22);
  4. **game-theoretic strategies**: "Norms are represented by the strategies that an agent uses"
     (¶2.23).

  A norm is "any behavioral rule that is considered valid by the majority of a population" (¶2.6).
  Normative agents must be able to "represent norms in a format that allows them to be reasoned
  over and modified during the lifetime of the agent" (¶1.3).
- Executable or descriptive: all four schemes are executable inside the system that defines them.
  None is described as shared between systems. "In order for norms to be used in agent-based
  systems, norms must be specified in a way that enables them to be processed by artificial
  agents. Research in this area is still in its infancy" (¶2.19).
- How it travels between systems: **not addressed, and flagged as open.** "Currently many systems
  are implicit in their representation, but we have seen a trend towards attempting to develop
  external formats and specifications; many of which are based on deontic logic" (¶5.4). The
  authors ask whether communication protocols "such as FIPA or KQML" could "be extended to
  represent norms for inter- and intra-agent communication" (¶5.10). The nearest mechanism they
  report is in **electronic institutions**: "institutional ontologies are often used to allow norms
  to be defined at general level and then redefined at a specific level depending on context they
  are used in" (¶4.7).
- Evidence that it works in two or more systems: none reported.
- Failure modes and limits stated by the authors:
  - in passive transmission "it is possible for the acquired norm to be different from the
    original norm due to bias, error, or some other factor" (¶3.10). A norm may also be modified
    during "transcription" into an agent's knowledge base, with results "akin to human
    misunderstanding" (¶3.25);
  - the simple approach to norm recognition "may not scale to more complex systems where multiple
    norms exist throughout multiple groups" (¶3.15);
  - "All of the research reviewed for this paper examines at most only two groups interacting with
    each other at the same time" (¶3.17);
  - sanctions work only in a "goldilocks zone" of cost and force "that appears to completely
    depend on the problem context" (¶5.9);
  - of the five levels of norm development (Boella et al. 2008), "Most existing normative systems
    belong in the first two levels": norms designed offline and implicit, or explicitly
    represented (¶5.2–¶5.3).
- For the portable rule core: **adapt the framing; no representation to adopt** [inference].
  - #34's core is a condition/action representation (scheme 2) made explicit, Boella's level 2.
  - This survey says the field had not settled how such norms travel between systems (¶5.4,
    ¶5.10). So the idea is not re-inventing a solved problem, and it cannot cite a solution
    either.
  - The electronic-institution practice of defining a norm generally and then "redefin[ing it] at
    a specific level depending on context" (¶4.7) is the closest structural precedent here for
    core plus binding. The survey reports no evidence that it worked across systems.
  - It also lists norm creation by "negotiation by agents within a group" as one of three routes
    in the natural world (¶3.36), which places the FYP's negotiated rules in a recognised
    category.
- BibTeX: `hollander2011normative`

---

### [Mellema-Sanctions]: Linking sanctions to norms in practice

- Authors / Year / Venue: René Mellema, Frank Dignum (Umeå University) / 2022 / arXiv:2205.10295v1
  [cs.LO].
- Link: https://arxiv.org/abs/2205.10295
- Status: `[preprint]`. The arXiv record has no journal reference or DOI, and a Crossref search
  by title found no published version. The issue's lead said "Mellema et al."; there are two
  authors.
- Read: full text, including both appendices, from `refs/pr_arxiv_2205_10295_mellema_sanctions.txt`.
  ⚠ Several formulas in Propositions 4.5–4.9 are garbled in the extract. The norm definitions used
  below (Definitions 5.1 and 6.1, and §6's example) came through readable.
- What it represents: norms for **social simulation**, specified in a temporal logic that tracks
  violations, repairs and punishments.
- Structure: the components a norm specification needs, taken from earlier work (§1): "(i)
  Activation condition (ii) Deactivation condition (iii) Fulfilment/Violation condition (iv)
  Deadline (v) Repair (vi) Punishment".
  - Formally, NORM_O(i, a, α, β, δ, φ, ρ, π) for obligations and NORM_F(i, a, α, β, φ, ρ, π) for
    prohibitions: norm label i, agent a, activation α, deactivation β, deadline δ,
    fulfilment/violation φ, repair ρ, punishment π (Definition 6.1, §6).
  - These are built on violation modalities in CTL∗ with a linear past, separating violation by
    acting from violation by omitting to act (Definitions 4.2–4.3, §4).
  - "A violation handling norm activates for all the agents that have caused a violation, whereas
    meta-norms activate for all agents that see a violation" (§6). In the worked example, a
    bystander in a plaza must "call out" a litterer, and another must call out a bystander who did
    not (§6).
- Executable or descriptive: **descriptive** (a logic). It is meant to "guide an implementation of
  normative systems" (Abstract); the authors "have started" an agent architecture based on it (§7).
- How it travels between systems: not addressed. The motivation is that existing deontic
  formalisations "are hardly used" in social simulation "because they do not give the right kind
  of handles for the designer of a simulation to work with" (§1).
- Evidence that it works in two or more systems: none reported.
- Failure modes and limits stated by the authors:
  - the logic assumes equal time steps: "Using the depth of tree to give the time point does mean
    that we assume that every time step takes the same amount of time" (§3);
  - "the way in which we mark a (lack of) action to cause a violation is still preliminary", and
    it brings in "all the traditional problems of the material conditional" (§7);
  - "The question of decidability and complexity of the resulting logic is also still open" (§7);
  - an obligation over a conjunction cannot be split into its parts (§5), and "we cannot have two
    obligations for different deadlines at the same time" (§5);
  - linking two norms needs a variable carried from one to the other, which "in an actual
    implementation ... would be easier to manage" (§6).
- For the portable rule core: **adapt the component list; reject the logic** [inference].
  - Two of its six parts are missing from both IG and #34's idea: a **deactivation condition**
    (when a rule stops applying, which today's format has as `expiry`, `rule-format.md` §7) and a
    **deadline**.
  - Its split between **violation-handling norms** (for the one who broke the rule) and
    **meta-norms** (for those who saw it) is the structure queue cutting needs: the newcomer who
    cut in, and "the person directly behind a queue-cutter" (#34).
  - The logic itself is too heavy and too unsettled to execute: decidability is open and the
    causal marking "preliminary" (§7).
  - Its equal-time-step assumption (§3) is the same portability hazard #34 notes for negsim's
    step-counted matching delay.
- BibTeX: `mellema2022sanctions`

---

## 3. Simulation interoperability

The issue asks for one interoperability standard from simulation engineering. **FMI** is that
standard here: the 2011 paper that introduced it, the current specification, and an empirical
study of how well tools implement it. HLA could not be read as a standard (IEEE 1516 is
paywalled). It is covered through [Wang-LCIM]'s analysis (§4 there) and [Gomes-CoSim]
(§5.2 there).

### [Blochwitz-FMI]: The Functional Mockup Interface for Tool independent Exchange of Simulation Models

- Authors / Year / Venue: T. Blochwitz, M. Otter, M. Arnold, C. Bausch, C. Clauß, H. Elmqvist,
  A. Junghanns, J. Mauss, M. Monteiro, T. Neidhold, D. Neumerkel, H. Olsson, J.-V. Peetz, S. Wolf
  / 2011 / *Proceedings of the 8th International Modelica Conference*, Dresden, pp. 105–114
  (Linköping University Electronic Press).
- Link: https://doi.org/10.3384/ecp11063105 | https://ep.liu.se/ecp/063/013/ecp11063013.pdf
- Status: published (conference proceedings; open access from the publisher).
- Read: full text, from `refs/pr_blochwitz2011_fmi_modelica.txt`. ⚠ Table 1 (§5, comparing FMI
  with proprietary interfaces) lost its alignment in extraction and is not used.
- What it represents: **models** (dynamic systems), not rules; packaged so that other tools can
  run them.
- Structure: a Functional Mockup Unit (FMU) is one zip file containing (§2.2):
  1. "An XML-file" defining every variable exposed to the environment, and for co-simulation
     "a set of capability flags";
  2. "a small set of easy to use C-functions", in source and/or binary form;
  3. further data (icon, documentation, tables, libraries).

  There are two interface types (§2): **Model Exchange**, where the importing tool's solver
  integrates the model's equations, and **Co-Simulation**, where each subsystem is "solved
  independently from each other by their individual solver" between "discrete communication
  points", under a master algorithm.
- Executable or descriptive: **executable as shipped.** The FMU carries compiled or compilable
  code. The importing tool calls its functions (`fmiDoStep`, `fmiGetReal`, ...; §3.2, §4.2); it
  does not re-implement the model. Only the XML description is read in each tool's "favorite
  programming language" (§2.3).
- How it travels between systems: **a shared standard plus wrappers.** A whole simulation tool can
  take part through "a simulation tool dependent wrapper which communicates by a (proprietary)
  interface with the simulation tool"; the master "does not notice the usage of an FMI wrapper"
  (§4.3, Figure 9).
- Evidence that it works in two or more systems: §6 lists six tools supporting FMI 1.0 at the time
  (Dymola, JModelica.org, Silver, SimulationX, Simulink through Dymola, a Fraunhofer master), and
  more planned. Within the MODELISAR project, "Daimler has set up 14 automotive use cases for the
  evaluation and improvement of FMI" (§1). Their outcomes are not reported here.
- What made "write once, run in many tools" work, by this paper's own account:
  - **a deliberately small scope.** Modelling languages "require a huge effort to support them in
    a tool. It is therefore common to provide also low level interfaces, to exchange models in a
    less powerful, but much simpler way" (§1). FMI 1.0 covers "ordinary differential equations in
    state space form with events" (§3.1), with "the minimum amount of different data types"
    (§2.4);
  - **an industrial driver**: "initiated, organized and pushed by Daimler to significantly improve
    the exchange of simulation models between suppliers and OEMs" (§7);
  - **joint definition by competing vendors**: "defined in close collaboration of different tool
    vendors within the MODELISAR project" (§7).
- Failure modes and limits stated by the authors:
  - if a tool's header uses a different type (e.g. "typedef float fmiReal" instead of "typedef
    double"), "the FMU needs to be recompiled" (§2.4);
  - the data types defined are "not sufficient for embedded systems" (§2.4);
  - the variable structure is "flat" (§2.4);
  - time events are "based on real variables which could lead to inexact results" (§5, note 5).
- For the portable rule core: **adapt the architecture, not the content** [inference].
  - FMI is the clearest case in this review of "write once, run in many simulators" working at
    scale. It works because what travels is **one executable implementation behind a small, typed
    interface**. Each tool does not re-implement a description.
  - #34's standalone rule engine has that shape: one engine, called by every simulator through
    Situation → Decision. The adapters are the "tool dependent wrapper".
  - The lesson for scope is FMI's own: start "less powerful, but much simpler".
- BibTeX: `blochwitz2011fmi`

---

### [FMI-3.0.2]: Functional Mock-up Interface Specification, version 3.0.2

- Authors / Year / Venue: Modelica Association Project FMI / 27 November 2024 / standard document.
- Link: https://fmi-standard.org/docs/3.0.2/
- Status: `[standard]`.
- Read: these sections: 1.2 (Overview), 1.3 (Properties and Guiding Ideas) and the opening of
  2.4.3 (Physical Units), from `refs/pr_fmi_3_0_2_specification.txt`. The rest of the 53,000-word
  standard (the C API, state machines, interface types in detail) was not read.
- What it represents: models, packaged for exchange between simulation tools.
- Structure: an FMU is "a ZIP archive and an application programming interface (API) to exchange
  dynamic models using a combination of XML files, binaries and C code" (§1.2). There are three
  interface types: Co-Simulation, where "the FMU typically contains its own solver or scheduler";
  Model Exchange, which "requires the importer to perform numerical integration"; and Scheduled
  Execution (§1.2). "All required computations are triggered by calling standardized C functions
  from the importer into the FMU" (§1.2).
- Executable or descriptive: executable, by design. "To be simulator independent, the FMU must
  export its implementation in self-contained binary form" (§1.3, "Simulator independence").
- How it travels between systems: a shared standard. Its guiding ideas, which are the
  specification's own account of what makes it portable (§1.3):
  - **"Simulator independence**: It is possible to compile, link and distribute an FMU without
    knowing the environment in which the FMU will be loaded";
  - **stability**: support "is a major investment for tool vendors. Stability and backwards
    compatibility of the FMI has therefore high priority";
  - **semantic versioning**, and **"Version independence"**: an FMU of a given major and minor
    version is valid for any minor version of the same major version, "because features of minor
    versions are optional and ignorable";
  - **"Hide data structure"**: the standard "shall not unnecessarily restrict or prescribe a
    certain implementation of FMUs or simulators";
  - **"Few functions"**, "orthogonal", for "a compact, easy-to-use, and hence attractive API".

  **Units** are defined as exponents of "the seven SI base units" (plus rad), because "there is no
  standard to represent units in strings, and there are different ways how this is performed in
  different tools" (§2.4.3).
- Evidence that it works in two or more systems: not the purpose of the document. See
  [Bertsch-ReferenceFMUs].
- Failure modes and limits stated by the standard: §1.3 lists properties "this version of the FMI
  standard does not have". Model Exchange is for ODEs in state-space form, "not for a general
  differential-algebraic equation (DAE) system", and the XML has "No explicit definition of the
  variable hierarchy".
- For the portable rule core: **adopt three practices** [inference]:
  1. semantic versioning, with minor features "optional and ignorable", for the vocabulary
     (#34's "fixed, versioned vocabulary");
  2. units as SI exponents rather than strings, for every feature (today's format already
     requires a unit on every numeric comparison, `rule-format.md` §4);
  3. a short list of guiding ideas fixed **before** the format is written, as FMI did.
- BibTeX: `fmi2024spec302`

---

### [Bertsch-ReferenceFMUs]: Improving Interoperability of FMI-supporting Tools with Reference FMUs

- Authors / Year / Venue: Christian Bertsch, Awad Mukbil, Andreas Junghanns (Bosch; TU Clausthal;
  QTronic) / 2017 / *Proceedings of the 12th International Modelica Conference*, Prague,
  pp. 533–540.
- Link: https://doi.org/10.3384/ecp17132533
- Status: published (conference proceedings; open access).
- Read: full text, from `refs/pr_bertsch2017_fmi_reference_fmus.txt`. ⚠ Tables 1 and 2 (per-tool
  results) are symbol-coded and the symbols did not survive extraction. The counts below come from
  the prose of §4.2–§4.3.
- What it represents: **conformance tests** for tools that import FMUs.
- Structure: a reference FMU is "an FMU specifically implemented to test compliance with a
  certain aspect of the FMI standard of a simulation tool. It has the ability to detect and log
  errors and wrong practices". It must be available "in source code" (§2.2). There are
  single-feature "diagnostic FMUs", whose failures are "very easy to interpret", and
  "multi-feature" FMUs for "more subtle errors that only occur due the interplay of different
  effects" (§2.5).
- Executable or descriptive: executable test artefacts.
- How it travels between systems: through the FMI **cross check**. Exporting tools upload test
  FMUs "together with reference solutions as comma-separated values (CSV) files, and importing
  tools can run those FMUs and report the results" (§1). A pass means the output is correct
  "within specified tolerances" (§2.6).
- Evidence that it works in two or more systems: yes, with measured defects. "More than 80
  simulation tools support FMI version 1.0 and more than 40 support version 2.0" (§1). Reference
  FMUs were run in **10 importing tools**, needing "more than 200 simulation models" for Windows
  64-bit alone (§4.2):
  - "five tools show errors in ME due to violations of the calling sequence" with Integer and
    Boolean inputs (§4.3);
  - string inputs and outputs "are not supported by typical block-oriented simulation tools"
    (§4.3);
  - a "2.0.1" version string, meant to be forward compatible, "is problematic for all but one
    tested importing tools" (§4.3);
  - one tool crashed on an FMU with a CSV resource, and two violated the set–step–get order in
    co-simulation (§4.3);
  - overall, "In most tools the FMI import support has a quite mature quality level" (§4.2).
- Failure modes and limits stated by the authors:
  - "it is up to the tool vendors which FMUs to submit" to the cross check, so "the features
    tested ... are incomplete and interpretation of failures is difficult"; there are "no means ...
    to prove standard compliance for FMI import" (Abstract);
  - "the FMI standard is considered to be not fully formalized" (§2);
  - "If the FMU compliance checker does not find a problem, it is not guaranteed that the FMU is
    error free" (§2.1);
  - commercial importing tools are "black-boxes, and the only way to test them is to run special
    FMUs" (§2.1).
- For the portable rule core: **adopt the testing design** [inference].
  - This is the best evidence in the review that implementations of one well-specified standard
    still drift apart, and of how a community catches it.
  - #34's conformance tests should copy three things: single-feature diagnostic cases, each with a
    reference output and a tolerance; a separate multi-feature layer; and reference cases written
    by the standard's owners, not chosen by each simulator's implementer.
  - It also bounds what passing tests can prove: absence of detected faults, not compliance (§2.1).
- BibTeX: `bertsch2017referencefmus`

---

### [Gomes-CoSim]: Co-simulation: A Survey

- Authors / Year / Venue: Cláudio Gomes, Casper Thule, David Broman, Peter Gorm Larsen, Hans
  Vangheluwe / 2018 / *ACM Computing Surveys* 51(3), article 49, 1–33.
- Link: https://doi.org/10.1145/3179993 | accepted version:
  https://people.kth.se/~dbro/papers/gomes-et-al-2018-co-simulation-survey.pdf
- Status: published at ACM Computing Surveys. Read as the "author prepared accepted version"
  (its first page), from co-author Broman's KTH page. An earlier, longer preprint exists as
  arXiv:1702.00686 ("Co-simulation: State of the art", 2017); it was not read.
- Read: these sections: 1, 2 (opening), 3.3, 4.3, 5.2, 6.5 (opening) and 7, from
  `refs/pr_gomes2018_cosim_survey_accepted.txt`. Not read: the orchestration algorithms (§§3.1,
  4.1–4.2, 5.1) and the classification tables (§6.2–§6.4).
- What it represents: coupled **models and simulators**. Co-simulation is "the theory and
  techniques to enable global simulation of a coupled system via the composition of simulators.
  Each simulator is broadly defined as a black box capable of exhibiting behaviour, consuming
  inputs and producing outputs" (§1).
- Structure: simulation units (SUs) coupled through inputs and outputs by an orchestrator.
  Discrete-event (DE, §3), continuous-time (CT, §4) and hybrid (§5) approaches.
- Executable or descriptive: executable units, coupled at run time.
- How it travels between systems: standards (FMI for continuous time, HLA for discrete event;
  §5.2) plus **wrappers that adapt each unit**, a practice the authors call "semantic adaptation"
  (§5.2).
- Evidence that it works in two or more systems: "From 2011 to 2016, there has been at least 48
  reported industrial applications of co-simulation ... most reports describe the coupling of two
  simulators" (§1). The "large majority ... represent ad-hoc couplings between two simulators of
  two different domains" (§7).
- Failure modes and limits stated by the authors:
  - **wrappers carry domain decisions**: "There is simply no best choice of wrappers for all
    scenarios", adaptations "require that a person with the domain knowledge describes how the
    SUs can be adapted", and "the wrapper incorporates information that will ultimately have to
    be encoded in the software controller" (§5.2);
  - **results depend on the coupling step**: "the larger the co-simulation step size, the larger
    is the error". Whether "decreasing the communication step size lead[s] to a more accurate
    co-simulation trace ... cannot be answered yet in general co-simulation" (§4.3);
  - **determinism is a property of the composition**, not of the parts. "Proving confluence is hard
    in general for black box DE co-simulation because it depends on knowledge about how the child
    SUs react to external events" (§3.3);
  - **capabilities differ even under one standard**: "even with a standardized interface, SUs have
    different capabilities". The common answer is to assume one shared feature set and "delegate
    to wrappers the responsibility of leveraging extra features (or mitigating the lack of)"
    (§5.2);
  - "both standards [FMI and HLA] have limitations for hybrid co-simulation"; "correct handling
    and representation of time" is needed "to achieve a sound approach for simultaneity" (§5.2);
  - "the adaptations required to combine simulators from different formalisms, even conforming to
    the same standard, are very difficult to generalize to any co-simulation scenario" (§7).
- For the portable rule core: **adopt as a warning** [inference].
  - Each limit above has a direct counterpart in #34's idea.
  - The perception adapter decides the conflict type, and that is a domain decision made in a
    wrapper (§5.2). Two adapters can disagree about when a conflict starts.
  - Outcomes will depend on how often each simulator calls the engine, the coupling step (§4.3).
    negsim, a continuous simulator and a discrete queue model call it at different rates.
  - Simultaneous claims are the heart of a conflict, and simultaneity is what the authors single
    out as hard to standardise (§5.2).
  - The answer the field uses, a shared minimal feature set with the rest in wrappers (§5.2), is
    #34's vocabulary-plus-binding split.
- BibTeX: `gomes2018cosim`

---

### [Wang-LCIM]: The Levels of Conceptual Interoperability Model: Applying Systems Engineering Principles to M&S

- Authors / Year / Venue: Wenguang Wang, Andreas Tolk, Weiping Wang / 2009 / *Proceedings of the
  Spring Simulation Multiconference (SpringSim'09)*, San Diego (SCS).
- Link: https://arxiv.org/abs/0908.0191
- Status: published in the SpringSim'09 proceedings (the arXiv comment, and the paper's own
  footer: "Published by SCS in the SpringSim'09 Proceedings"). Read as the arXiv copy; no DOI
  found.
- Read: full text, from `refs/pr_arxiv_0908_0191_lcim.txt`. ⚠ Tables 1–4 lost their column
  alignment in extraction. The level names and meanings below were checked against the prose of
  §2.2 and §3.1.
- What it represents: a **framework for rating interoperability** between simulations, not a
  representation of rules.
- Structure: seven levels (Table 1, §2.2):
  - L0, none;
  - L1, technical: a common communication protocol, "bits and bytes";
  - L2, syntactic: a common data structure, the "format of information exchanged";
  - L3, semantic: a common reference model, the "meaning of data";
  - L4, pragmatic: a common workflow model, the "use of data" and its context;
  - L5, dynamic: a common execution model, the "effect of data";
  - L6, conceptual: a common conceptual model, its "assumptions, constrains etc.".

  Higher levels need the lower ones: "When higher levels are reached, the lower levels must have
  been satisfied" (§3.1).
- Executable or descriptive: descriptive (a rating scheme), used either to rate existing systems
  ("descriptive role") or to set requirements for new ones ("prescriptive role", §3).
- How it travels between systems: not applicable. Its subject is exactly that question.
- Evidence that it works in two or more systems: its application to HLA and BOM (§4) is an
  analysis, not an experiment.
- Failure modes and limits stated by the authors:
  - the two Q4 failure modes, in so many words: "It is possible that two models are derived from
    exactly the same concepts, but their implementations differ. It is also possible, that the
    same entities are used in the simulation, but represent different concepts" (§3.1);
  - **HLA**: its Object Model Template "specifies the structure but not semantic of data
    exchanged", so "HLA can only reach the syntactic level in general". A shared reference FOM
    (RPR-FOM) reaches the semantic level "but only within the application range of this specific
    FOM" (§4.1);
  - **BOM** "does not capture the assumptions and constrains of conceptual models" and "can only
    satisfy up to the dynamic level" (§4.2);
  - "we may not be able to prove that two systems are conceptually interoperable, we may find ways
    to point to critical areas or to show when two systems are NOT conceptually interoperable"
    (§2.1);
  - "technically feasible compositions are conceptually meaningless, and the results of such
    compositions are worthless", if the technical structures are not aligned with the conceptual
    ones (§5).
- For the portable rule core: **adopt as the yardstick** [inference].
  - A shared rule file, schema and engine API give L1–L2. That is what HLA reaches and no more.
  - The vocabulary's definitions aim at L3. The conformance tests check L3 (scene → Situation)
    and part of L5 (Decision → controls → effect).
  - L6, shared assumptions such as update order and time step, is where [group 6](#6-precedent-the-same-rule-in-more-than-one-simulator)'s
    docking studies find implementations diverge.
  - RPR-FOM's lesson, semantic interoperability "only within the application range" of one
    reference model (§4.1), supports #34's "the same kind of conflict, in any simulator, not any
    conflict".
- BibTeX: `wang2009lcim`

---
