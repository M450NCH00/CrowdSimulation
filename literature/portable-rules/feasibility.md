# Feasibility: can a conflict rule be written once and carried out faithfully by several simulators?

> For issue [#35](https://github.com/M450NCH00/CrowdSimulation/issues/35), PT-1 of the
> portable-rules track ([#34](https://github.com/M450NCH00/CrowdSimulation/issues/34)). Written on
> 2026-10-18.
>
> - **Status:** draft for PT-7 and the supervisor. Nothing here is agreed, and #34's idea itself is
>   still a proposal that needs the supervisor's sign-off.
> - **Citations:** every claim cites an entry by its handle. Entries are in
>   [representations.md](representations.md) and [novelty-check.md](novelty-check.md), where each
>   carries its own locators. Locators repeated here are the entries'. My own reasoning is marked
>   `[inference]`.

Companion files: [verdict](verdict.md) (one page) · [representations](representations.md) ·
[novelty check](novelty-check.md) · [search log](search-log.md) · [missing papers](missing-papers.md)
· [refs](refs-portable-rules.bib)

---

## 0. The answer in one paragraph

**Writing a conflict rule down independently of any simulator is well-trodden; carrying it out
*faithfully* in several simulators has never been shown for behaviour rules, and the closest
evidence says the behaviour will differ unless many details outside the rule are also fixed.**

- Institutional grammar and normative MAS have represented norms independently of any system for
  decades. None of those representations is executed across systems (§3).
- The one simulation standard that does achieve "write once, run in many tools", FMI, does it by
  shipping **one executable implementation** behind a small interface. Even then importing tools
  drift: 5 of 10 violated the calling sequence on the Integer and Boolean reference tests (§3.2).
- No crowd, pedestrian, game or robot-navigation study read here ran the same behaviour rule in two
  simulators and compared the behaviour (§4).
- In social simulation, where such docking has been done, every study found the behaviour changed.
  The causes were details nobody had counted as part of the rule: update order, tie-breaking, ≤
  against <, run length (§4.3, §6).

**Verdict: feasible with changes** (§8). The portable claim must be stated at the level of
*decisions* ("the same Situation gives the same Decision"), with behaviour across simulators
treated as something to *measure*, not to assume.

---

## 1. The idea, restated in my own words

This restates #34's "The idea". It is not a new proposal.

Today a rule in `llm_negotiation/rule_db/` says: *when two agents meet in this geometric way, and
these negsim measurements hold, give them these two roles and these ORCA settings*
(`llm_negotiation/docs/rule-format.md` §§1–7). The idea is to split that rule in two:

- **A core.** Who is involved, by role; what each role must, may or must not do; under which
  conditions. It is stated only in a small, fixed, versioned **vocabulary**:
  - **conflict types**: what is contested, i.e. room to pass, one-at-a-time access (to a passage,
    a queue or a vehicle door), or limited capacity;
  - **roles** for any number of people, given by position or by ranking a feature;
  - **features** with definitions every simulator can follow, each marked with who can know it;
  - **actions** stated as intentions (proceed, wait, give way aside, join the back of the line,
    ...).
- **Simulator-specific parts.** How far to step aside, what ORCA share to use. These move into
  two **adapters** per simulator, one turning the simulator's state into a Situation and one
  turning a Decision into the simulator's controls, plus an optional per-rule **binding**.

A **standalone engine** matches cores to Situations and imports nothing from any simulator. Two
sets of **conformance tests** check the parts: Situation → Decision, and scene → Situation. A
simulator "supports the rules" when its adapters pass both. Trained models could stand in for the
engine behind the same interface. Rules are then tested on **unseen scenarios** described in
simulator-independent **scenario cards**, in testbeds chosen to differ, with CrowdGym as the
target.

The claim to be tested is "the same kind of conflict, in any simulator", not "any conflict".

---

## 2. What is unclear or inconsistent in the idea

The acceptance criteria ask for these to be flagged. Each item is my reading `[inference]`, with
the evidence that makes it matter.

| # | The point | Why it matters |
|---|---|---|
| **F1** | **"Today's rules would become the ORCA binding, unchanged"** conflicts with **"a rule states its decision only in terms of the vocabulary"**. Today's conditions are negsim measurements: `pair.time_to_collision_s <= 6.0`, encounter classes from headings, corridor width (`rule-format.md` §§1, 3, 5). None is in #34's feature list. | Either those conditions move into the binding, and the binding then decides *when* a rule applies (not only "how much"), or they move into the perception adapter as "a conflict exists". Either way a simulator-specific part makes a decision. That is the "wrapper incorporates information that will ultimately have to be encoded in the software controller" problem ([Gomes-CoSim] §5.2). The idea needs to say which. |
| **F2** | **The worked example crosses sub-types.** `single_file_first_arrival` moves from `exclusive_access.passage` to `exclusive_access.queue`, yet the claim is "the same kind of conflict" with rules "scoped by conflict type". | In a passage the constraint is physical and hard; in a queue it is a norm, and "a norm might be infringed" ([Tessier-ConflictingAgents] §4, p. 16). The example therefore tests transfer across a boundary that the idea elsewhere says to respect. Is the scope the type or the sub-type? |
| **F3** | **`wait` against `join_tail`.** In the queue, "the newcomer waits, which in a queue means joining the back", yet `join_tail` is also its own action. | Either the adapter turns `wait` into joining the back, so the adapter changes what the action means, or the core must say `join_tail` and the "same" rule needs different actions in different sub-types. |
| **F4** | **`arrival_order` has two meanings in the example itself.** Today's rule ranks by `agent.time_to_segment_s`, a *predicted* arrival at present speed, with ties within 0.5 s (`rule_db/rules/single_file_first_arrival.v1.yaml`, `roles.by`). A queue's arrival order is a *recorded* history. | One term, two definitions: the issue's "two implementations of the same term disagree", before any second simulator exists. Docking studies found exactly such hidden differences ([Axtell-Docking] §5.1; [Wilensky-MakingModelsMatch] ¶5.7). |
| **F5** | **"scene → expected Situation" tests cannot be shared verbatim** between a continuous simulator and a discrete queue model. A scene has to be *built* in each one. | So that set is per simulator, written against a shared expected Situation. And both test sets are **open-loop** (one snapshot), while docking failures came from closed-loop effects: activation order, event order, timing ([Axtell-Docking] §4.2; [Wilensky-MakingModelsMatch] ¶5.17, ¶5.19). |
| **F6** | **Timing is unspecified.** #34 notes today's matching delay is counted in steps, but does not say in what unit the core states time, or **how often the engine is called**. | Results depend on the coupling step ([Gomes-CoSim] §4.3). Step-counted triggers caused the main quantitative mismatch in [Kleinmeier-Cooperation] (§II C). Even Menge's comparison ran each motion model at its own time step ([Curtis-Menge] Figure 4). |
| **F7** | **Ties and comparison strictness are not mentioned.** | An unspecified tie-break and a ≤ that should have been < each changed a published result ([Edmonds-Replication] ¶8.3–¶8.6, ¶9.2; [Galan-Reimplementing] note 4). Today's format already makes a tie policy compulsory (`rule-format.md` §6). The core must keep it. |
| **F8** | **Knowledge conflicts are outside the hierarchy.** All three types (`passing_room`, `exclusive_access`, `capacity`) are resource conflicts. | A queue-cutting dispute is partly a knowledge conflict, "agents' information is not the same" ([Tessier-ConflictingAgents] §3.2, p. 14), as in "I was here first". Only L4 "abstain" covers it. |
| **F9** | **The "Or else" is borrowed from IG but has nothing to attach to.** No listed action reacts to a breach, and no role is "the one who saw it". | Queue cutting is a breach. It needs violation-handling norms for the breaker and meta-norms for observers ([Mellema-Sanctions] §6), and monitoring roles for bystanders ([Frantz-IG2Codebook] §6.1). |
| **F10** | **"Roles for any number of people" against pairwise evaluation.** Today a rule is "evaluated once per pair" (`rule-format.md` §5). | Who is *in* a many-person Situation (sensing radius, queue membership) is decided by the perception adapter, so two adapters can assemble different Situations from the "same" scene (F5). |
| **F11** | **"A simulator supports the rules when its adapters pass both sets"** overstates what tests can show. | Passing shows that no tested fault was found, not compliance ([Bertsch-ReferenceFMUs] §2.1; [Wang-LCIM] §2.1; [Edmonds-Replication] ¶6.3). |

None of these makes the idea unworkable. F1, F4 and F6 have to be decided before PT-8 writes
vocabulary v0 [inference].

---

## 3. Q1. Representations: how other fields write rules down independently of what runs them

### 3.1 The representations, side by side

| Representation (entry) | Parts of one rule or norm | Can a system run it directly? | What translation needs |
|---|---|---|---|
| **ADICO**, Crawford and Ostrom 1995 (as quoted in [Frantz-IG2] §2; the original is a stub) | Attribute, Deontic, aIm, Condition, Or else. AIC is a strategy, ADIC a norm, ADICO a rule | No. A coding scheme for text | A human coder; a codebook |
| **IG 2.0** ([Frantz-IG2] §3; [Frantz-IG2Codebook] §2.1) | Attribute, Object (direct and indirect), Deontic on a continuum, Aim, Context split into Activation Condition and Execution Constraint, Or else as a nested statement. Constitutive statements are PMFECO. Three levels: Core, Extended, Logico | No. IG Script is parseable into tables and trees, not run (Codebook §4.1; IG Parser README) | Coders; a declared *profile* of features used (Codebook §4.6); domain understanding to place contexts (§2.4) |
| **nADICO / nesting** (credited in [Frantz-IG2] §3.1; the 2014 chapter is a stub) | Horizontal (AND, OR, XOR) and vertical (monitored → consequential) nesting, to any depth (Codebook §2.2.2) | No | As for IG 2.0 |
| **Deontic and modal logic** in normative MAS ([Hollander-NormativeABS] ¶2.20) | Obligations, permissions, prohibitions | Only inside a reasoner built for it | A reasoner per system; the field had "not" settled external formats (¶5.4) |
| **Condition/action pairs** ([Hollander-NormativeABS] ¶2.21) | A condition and an action, plus an inference engine | Yes, inside the system that defines them; "coded directly into the agent's decision making system" | Re-implementation in each system |
| **Binary strings; game strategies** ([Hollander-NormativeABS] ¶2.22–¶2.23; [Neumann-HomoSocionicus] Table 4) | Presence bits; a strategy | Yes, inside one model | Re-implementation; often only an observer calls the result a norm (Neumann ¶5.17) |
| **Violation-modality norms** ([Mellema-Sanctions] Definition 6.1) | Activation, deactivation, deadline, fulfilment or violation, repair, punishment; violation-handling against meta-norms | No. A logic meant to "guide an implementation" | Manual implementation; decidability open (§7) |
| **LLM norm quintuple** ([Ren-CRSEC] §2.1) | Natural-language content, utility, descriptive or injunctive, activated, valid | Only by an LLM | Not translatable without an LLM |
| **MTL over a predicate vocabulary** ([Manas-TR2MTL] §IV-A, §V-C) | Temporal-logic formula over CommonRoad and Lanelet predicates | By a monitor, yes | Hand-written functions mapping predicates to the simulator's state (§V-C) |
| **Behaviour FSM** ([Curtis-Menge] §3.5) | Prioritised Conditions, Targets, Actions; the output is a preferred velocity | Inside Menge only | Re-implementation elsewhere; scenarios were converted by script (§4.1) |
| **Psychology layer** ([Kleinmeier-Cooperation] §II B) | Perception → cognition (self-category) → behaviour | Inside Vadere | "Easily implemented in different pedestrian simulation programs": claimed, not done |
| **Behaviour trees + one engine** ([EscuderoJimenez-HuNavSim2] §III, §IV-B) | Action and condition nodes | Yes. One engine drives four host simulators | A wrapper per host simulator |
| **FMU** ([Blochwitz-FMI] §2; [FMI-3.0.2] §1.2) | XML model description, C functions, binaries, resources | **Yes. Executable as shipped** | None for the model; the importer couples variables, and wrappers couple whole tools |
| **HLA object models** (through [Wang-LCIM] §4.1) | Federation and simulation object models conforming to the Object Model Template | Federations exchange data over a Runtime Infrastructure (§4.1); the model code stays in each federate `[inference]` | The template "specifies the structure but not semantic of data exchanged" |

**Supported claims:**

1. **The representations that are independent of the system that follows them are not
   executable**, and the executable ones are not independent. IG and logics are coding schemes or
   specifications; condition/action pairs, strategies, FSMs and psychology layers live inside one
   system ([Frantz-IG2] §3; [Hollander-NormativeABS] ¶2.19–¶2.23; [Neumann-HomoSocionicus] Table 4;
   [Curtis-Menge] §3.4).
2. **Two architectures do run one artefact in several systems: FMI and HuNavSim.** Both ship the
   *execution*, not a description ([FMI-3.0.2] §1.3; [EscuderoJimenez-HuNavSim2] §III).
3. **How norms travel between systems was an open question in the normative-MAS survey literature
   read here** ([Hollander-NormativeABS] ¶5.4, ¶5.10). The nearest mechanism reported is
   electronic institutions' practice of defining a norm "at general level" and redefining it "at a
   specific level depending on context" (¶4.7). That is core plus binding, with no cross-system
   evidence reported.

### 3.2 The interoperability standard: what made "write once, run in many" work for FMI, and what limits it

**What made it work**, by the sources' own account:

1. **A small, deliberately weak scope.** FMI exchanges models "in a less powerful, but much simpler
   way" than a modelling language, because full languages "require a huge effort to support them
   in a tool" ([Blochwitz-FMI] §1). The guiding ideas include "Few functions" and "Hide data
   structure" ([FMI-3.0.2] §1.3).
2. **The execution travels, not a description.** "To be simulator independent, the FMU must export
   its implementation in self-contained binary form" ([FMI-3.0.2] §1.3). The importer only calls
   standard C functions (§1.2).
3. **A typed interface with a machine-readable description**: XML read in each tool's "favorite
   programming language", plus capability flags ([Blochwitz-FMI] §2.3). Units are defined as SI
   exponents because tools write unit strings differently ([FMI-3.0.2] §2.4.3).
4. **Stability and versioning.** Support "is a major investment for tool vendors", so stability and
   backward compatibility come first, with semantic versioning and minor features "optional and
   ignorable" ([FMI-3.0.2] §1.3).
5. **An industrial driver and joint definition**: Daimler's supplier-exchange problem, 14 use
   cases, and co-design by competing vendors ([Blochwitz-FMI] §1, §7).
6. **Testing infrastructure**: a cross-check with reference results in CSV, a compliance checker
   for exporters, and reference FMUs for importers ([Bertsch-ReferenceFMUs] §1, §2).

**What limits it:**

1. **Meaning is not standardised.** Each wrapper decides how a tool's variables connect, and "there
   is simply no best choice of wrappers for all scenarios" ([Gomes-CoSim] §5.2). A standard of this
   kind reaches LCIM's syntactic level. HLA "can only reach the syntactic level in general", and
   semantic interoperability only "within the application range" of one reference model
   ([Wang-LCIM] §4.1).
2. **Results depend on how units are coupled**: the step size, the orchestration, algebraic loops
   ([Gomes-CoSim] §4.3). Determinism is a property of the composition (§3.3).
3. **Implementations drift.** "More than 80" tools support FMI 1.0. Run against reference FMUs, "five
   tools show errors" (calling-sequence violations on the Integer and Boolean FMUs in Model
   Exchange) out of 10 tested, and a forward-compatible version string was "problematic for all but
   one" (§1, §4.3). The cross-check's coverage depends on what vendors submit
   (Abstract), and the standard "is considered to be not fully formalized" (§2), all in
   [Bertsch-ReferenceFMUs].
4. **Capabilities differ even under one standard.** The common answer is a shared minimal feature
   set, with "wrappers" handling the rest ([Gomes-CoSim] §5.2).
5. **Neither standard has a rule layer.** FMI and HLA move models and data, not norms
   `[inference]`.

### 3.3 What carries over to conflict rules `[inference]`

- **The shape of #34's architecture has precedent; its content does not.**
  - #34's standalone engine is FMI's shipped execution, one implementation every simulator calls.
    The adapters are FMI's "tool dependent wrapper" ([Blochwitz-FMI] §4.3) and HuNavSim's
    "communication wrapper" ([EscuderoJimenez-HuNavSim2] §III).
  - What FMI never had to solve, the adapters must: turning *different* simulators' states into
    the *same* Situation. That is semantic work at LCIM levels 3–5 ([Wang-LCIM] Table 1).
- **The part of the idea that FMI's history supports most is the engine.** One implementation of
  the matching logic, shared by every simulator, avoids the re-implementation failures of group 6.
  The part it supports least is the assumption that adapters will agree.

---

## 4. Q2. Precedent: has any study run the same behaviour rule in two or more simulators?

### 4.1 The plain answer

**No crowd, pedestrian, game or robot-navigation study read in this review ran the same behaviour
rule in two simulators and reported whether the behaviour stayed the same.** This agrees with the
simulation-rules review, which found no source evaluating one rule with two kinds of agent
(`../simulation-rules/research-gap.md` §3(a)). That review asked about agent types; this one
searched specifically for simulators ([search-log.md](search-log.md) §2, Q2 queries).

### 4.2 The nearest cases in those four fields

| Study | What was held fixed | What varied | Was behaviour compared? |
|---|---|---|---|
| [Curtis-Menge] (crowd) | The behaviour specification and scenario | Three motion models, inside one framework | **Yes.** "The differences in behavior due to the Pedestrian Model are clear" (§4.1, Figure 4), and each model ran at its own time step (Figure 4 labels, decoded) |
| [EscuderoJimenez-HuNavSim2] (robot navigation) | One behaviour engine (behaviour trees + social force) | Four host simulators through wrappers (Table I) | **No.** It runs in four, with no cross-host comparison |
| [Kleinmeier-Cooperation] (pedestrian) | — | — | **No.** Locomotion-independent "by design", implemented in Vadere only (§II A–B) |
| [Francis-SocNavPrinciples] (robot navigation) | Proposed: metric implementations shared across simulators | Simulators, through "bridge code" | **No.** A proposal in progress (§X-D) |

No game study was found that ran one AI behaviour in two engines and compared it; the searches are
logged in [search-log.md](search-log.md).

### 4.3 The adjacent field that did it: docking and replication in social simulation

| Study | The rule carried across | Systems | Did the behaviour stay the same? | Why not, where it did not |
|---|---|---|---|---|
| [Axtell-Docking] (1996) | Axelrod's cultural-transmission rule | Axelrod's Culture Model; Sugarscape | **11 of 12 comparisons**, after alignment | Agent **activation order** (with or without replacement); later, *which* agent changes (§4.1–§4.2, §5.1) |
| [Edmonds-Replication] (2003) | Riolo et al.'s tag-donation rule | Original; Java; SDML | The two re-implementations agreed with **each other**, not the original | An unspecified **tie-break**; one **≤** that, as <, removed all donation (¶8.3–¶8.6, ¶9.2) |
| [Wilensky-MakingModelsMatch] (2007) | The ethnocentrism model's rules | Ascape; NetLogo | **Two of three measures**, after four rounds | Reset timing, misread measures, **event order**, an **unshuffled agent list** (¶5.7–¶5.20) |
| [Galan-Reimplementing] (2005) | Axelrod's norms and metanorms games | Original; RePast | **Short run yes; long run reversed** | Run length; mutation rate; payoffs; equally valid selection rules (¶6.2–¶6.12) |
| [Donkin-Replicating] (2017) | — | NetLogo and Repast | Not read (stub) | — |

**Supported claim:** where one rule has been carried into a second implementation and measured, the
behaviour matched **only after details outside the rule's text were aligned**, and sometimes not
fully. Those details were update order, event order, tie handling, comparison strictness and run
length. `[inference]` A portable rule core will inherit this unless those details are declared,
fixed or tested.

### 4.4 Recorded separately, as the issue asks: same scenario, different simulators or models

These compare *simulators or models* on one scenario. They do not carry a behaviour rule across.

- **Read:** [Curtis-Menge] Cross Flow and Obstacle Course swap pedestrian models and global
  planners within one framework (§4.1). Menge also notes that in SteerSuite "a single simulation
  scenario can be run multiple times with different pedestrian models" (§5).
- **Found, not read** (listed so the next person need not search again; no claim made about their
  results; details in [search-log.md](search-log.md) §3):
  - a RiMEA-based comparison of microscopic pedestrian models (*SNE* journal);
  - SocNavBench (Biswas et al., *ACM THRI* 2022);
  - a 2020 resource-use comparison of Gazebo, Webots and V-REP (arXiv:2008.04627);
  - a 2004 VTI comparison of car-following models across traffic simulators;
  - "Characterizing the Complexity of Social Robot Navigation Scenarios" (mixtures of ORCA and
    social-force agents).

---

## 5. Q3. Vocabulary: taxonomies the core could adopt

| Part of #34's vocabulary | What exists to adopt (entry) | Gap left |
|---|---|---|
| **Conflict types** | Top level: **physical (resource)** against **knowledge** conflicts; physical conflicts are over "a resource which cannot be shared out or which is scanty", with space the critical one for robots ([Tessier-ConflictingAgents] §3, pp. 13–14). Hardness of the crucial constraint: physical is hard, a norm "might be infringed" (§4, p. 16) | **No source read classifies pedestrian situations by what is contested.** #34's `passing_room` / `exclusive_access` / `capacity` would be new below Tessier's top level, so it should be cited as an extension of it |
| **Situation names** below the types | Hallway scenarios (frontal approach, overtaking, intersection, blind corner); doorway scenarios (narrow doorway, entering or exiting a room, elevator); crowd and group scenarios ([Francis-SocNavPrinciples] Table III) | Robot-centred and geometric. **No queue, boarding or alighting scenario** |
| **Roles** | **Position rules** of Ostrom's action situation, "positions that actors can occupy" ([Frantz-IG2Codebook] §2.4). IG's role taxonomy relative to an action: originator, recipient, experiencer, advantaged, disadvantaged (§5.4). Monitoring roles for bystanders (§6.1). Robot roles "Any / Servant / Leader" ([Francis-SocNavPrinciples] Table III) | **No source gives roles by place in a line** ("directly behind", "newcomer") |
| **Features and who can know them** | **Information rules**, "channels of information flow" ([Frantz-IG2Codebook] §2.4), for "who can know it". Units as SI exponents ([FMI-3.0.2] §2.4.3). Today's "what a rule may read" (`rule-format.md` §5) | **No pedestrian feature vocabulary with operational definitions was found.** Q3 is only partly answered here |
| **Actions** | Handling patterns: flight, subservience, delegation, compromise, consensus ([Tessier-ConflictingAgents] §5.1, pp. 17–19). Regulative functions: comply, violate, detect violation, sanction, accept, reject, appeal ([Frantz-IG2Codebook] §5.5). Behaviour-tree action names ([EscuderoJimenez-HuNavSim2] §IV-B) | No closed list of pedestrian conflict actions |
| **Rule structure** | IG 2.0's components, especially **Activation Condition / Execution Constraint** and the nested Or else ([Frantz-IG2] §3.1). Mellema's **deactivation, deadline, repair, punishment** and the violation-handling / meta-norm split ([Mellema-Sanctions] §1, §6). **Profiles** declaring the feature set used ([Frantz-IG2Codebook] §4.6) | Execution semantics, from none of them |

Ontologies of pedestrian interactions and crowds turned up in the search but could not be read in
this session. They are logged as leads: Orellana and Renso's interactions ontology; Bandini et al.
2008; a crowd-simulation-scenario ontology on CEUR ([search-log.md](search-log.md) §3). **Q3 is
therefore answered for conflict types, roles and rule structure, and partly for features and
actions.**

---

## 6. Q4. Failure modes: what goes wrong when a rule is abstracted from its simulator

| # | Failure mode | Evidence (entry and locator) |
|---|---|---|
| **1** | **Detail is lost between description and implementation** | Ambiguities resolvable only by meeting the author ([Axtell-Docking] §5.1). Unspecified tie-breaking ([Edmonds-Replication] ¶8.3). "When" a value resets ([Wilensky-MakingModelsMatch] ¶5.7). Implementation artefacts in "translating a model described in natural language into a computer program" ([Galan-Reimplementing] ¶1.3). "A reimplementation of a paper is unlikely to be the same as the author's original" ([Curtis-Menge] §1). Loss of "semantic integrity" in coding ([Frantz-IG2] §2) |
| **2** | **Two implementations of the "same" term disagree** | "Two models are derived from exactly the same concepts, but their implementations differ ... the same entities ... represent different concepts" ([Wang-LCIM] §3.1). Measures misread from variable names ([Wilensky-MakingModelsMatch] ¶5.15). Coders' interpretational scope ([Frantz-IG2Codebook] §2.5). Five of ten FMI importers mishandling one input type ([Bertsch-ReferenceFMUs] §4.3). In this repository already: `arrival_order` as predicted against recorded (F4) |
| **3** | **Thresholds depend on the motion model and the step** | Each motion model needed its own Δt in Menge's controlled comparison ([Curtis-Menge] Figure 4). A "4 steps, 0.05" trigger and the speed mismatch it caused ([Kleinmeier-Cooperation] Listing 3, §II C). ≤ against < reversing a result ([Edmonds-Replication] ¶9.2). Error grows with the coupling step ([Gomes-CoSim] §4.3). Logic built on equal time steps ([Mellema-Sanctions] §3). #34 already records that today's thresholds are tuned to ORCA |
| **4** | **Update order, event order and timing, none of them in the rule's text** | Activation with or without replacement ([Axtell-Docking] §4.2). Event order and unshuffled lists ([Wilensky-MakingModelsMatch] ¶5.17, ¶5.19). Determinism and confluence as properties of the composition ([Gomes-CoSim] §3.3) |
| **5** | **The same rule, a different motion model, different behaviour** | Trajectories differing by pedestrian model under one behaviour specification ([Curtis-Menge] §4.1). One scene under social force and optimal steps: walking over agents against total blocking ([Kleinmeier-Cooperation] Figure 1) |
| **6** | **Adapters absorb decisions and drift apart** | Wrappers carrying controller logic; "no best choice of wrappers" ([Gomes-CoSim] §5.2). Importers deviating from a mature standard ([Bertsch-ReferenceFMUs] §4.3). A header type mismatch forcing recompilation ([Blochwitz-FMI] §2.4) |
| **7** | **Conformance tests show non-conformance, not conformance** | "If the FMU compliance checker does not find a problem, it is not guaranteed that the FMU is error free" ([Bertsch-ReferenceFMUs] §2.1). "We may ... show when two systems are NOT conceptually interoperable" ([Wang-LCIM] §2.1). "One cannot prove that implementations are the same" ([Edmonds-Replication] ¶6.3). Small samples make equivalence easy to "pass" ([Axtell-Docking] §4.2) |
| **8** | **Short runs mislead** | A metanorm result reversing with longer runs ([Galan-Reimplementing] ¶6.2) |
| **9** | **Meaning holds only within a scope** | Semantic interoperability "only within the application range" of one reference model ([Wang-LCIM] §4.1). A norm's constraint is softer than a physical one ([Tessier-ConflictingAgents] p. 16) |
| **10** | **A computational trick passes for a rule** | A global-knowledge advisor "intermixing a target system with a computational trick" ([Neumann-HomoSocionicus] ¶6.21–¶6.22). A rule engine reading features no claimant could know would repeat this `[inference]` |

`[inference]` Modes 1, 2 and 7 are what the issue named. Modes 3, 4 and 5 are the ones most likely
to defeat the claim "the same kind of conflict, in any simulator", because they arise *between* the
core and the motion model, where neither the core's text nor open-loop tests reach.

---

## 7. Q5. Novelty

Answered in full in [novelty-check.md](novelty-check.md).

- arXiv:2409.00993 was read in full. It overlaps the FYP's method (LLM agents reaching norms
  through dialogue) but writes nothing down, runs in one game, and lists transfer as future work.
- Prior work writes LLM-derived norms down only for LLM readers ([Ren-CRSEC]), or formalises
  human-written law ([Manas-TR2MTL]), or distils behaviour into code for one simulator ([Zhang-DFD],
  in this repository).
- **What is new is the combination**: an LLM-elicited conflict rule made into a
  simulator-independent artefact and checked in more than one simulator on held-out conflict types.
  **What is not new is every ingredient**, the vocabulary least of all.

---

## 8. Q6. Verdict and recommended representation

### 8.1 Verdict: **feasible with changes**

`[inference]`, from §§3–6:

- **Feasible.**
  - Every structural part of #34's architecture has a working analogue. A shared executable engine
    is FMI's FMU or HuNavSim's manager. Per-simulator wrappers exist in FMI, HuNavSim and TR2MTL's
    predicate mapping. A behaviour layer separate from motion exists in Menge and Vadere, and an
    explicit norm structure in IG 2.0 and Mellema.
  - Today's rule format already does several things the failure record demands: units on every
    comparison, a compulsory tie policy, defined missing values, and "what a rule may read"
    (`rule-format.md` §§4–6).
- **With changes**, because the evidence does not support "carried out faithfully" as a property of
  the architecture:
  1. **Restate the claim at two levels.** *Decision conformance*: the same Situation gives the same
     Decision, testable exactly, open-loop. *Behavioural equivalence*: to be measured per
     simulator, with the standard fixed in advance, relational or distributional
     ([Axtell-Docking] §6). Never assumed.
  2. **Move every simulator-dependent quantity out of the core and declare it.** Activation
     thresholds (F1), timing in seconds and the engine's call rate (F6), and update order where it
     affects matching ([Axtell-Docking] §4.2; [Wilensky-MakingModelsMatch] ¶5.17).
  3. **Define each vocabulary term operationally**, with a unit, its strictness, its tie
     behaviour, who can know it, and reference test cases (F4, F7; [FMI-3.0.2] §2.4.3;
     [Edmonds-Replication] ¶9.2).
  4. **Add what institutional grammar and the norm literature show is missing**: a deontic, a
     deactivation (today's `expiry`), a deadline, an Or else, and violation-handling against
     meta-norm roles (F9; [Mellema-Sanctions] §1, §6).
  5. **Treat transfer across sub-types (passage → queue) as a hypothesis to test**, not a
     consequence of sharing a type name (F2).
  6. **Own the conformance tests centrally.** Single-feature diagnostic cases with reference
     outputs and tolerances, then multi-feature cases ([Bertsch-ReferenceFMUs] §2.5–§2.6). Add
     closed-loop docking tests with long runs ([Edmonds-Replication] ¶10.1;
     [Galan-Reimplementing] ¶6.2).

### 8.2 Recommended representation: **extend this repository's own format, restructured around an adapted IG 2.0**

`[inference]` **Neither "adopt IG 2.0" nor "build from scratch".**

- **Do not adopt IG 2.0 as it stands.** It is a coding scheme for text with no execution
  semantics, its taxonomies are open by design, and its fine levels cost coders effort
  ([Frantz-IG2] §3.2–§3.3; [Frantz-IG2Codebook] §5).
- **Do adopt its structure**, mapped onto today's format:

  | IG 2.0 (Frantz-IG2 §3.1) | In the core |
  |---|---|
  | Attribute | role (any number, by position or by ranking a feature) |
  | Deontic | must / may / must not (today every directive is implicitly "must") |
  | Aim, Object | action, and whom or what it is done to |
  | Activation Condition | conflict type + vocabulary features (today's `encounter` + `when`) |
  | Execution Constraint | qualifiers that stay portable (which side; until clear) |
  | Or else | a nested consequential rule for the breaker; meta-norm roles for observers |

  Below an Execution Constraint, a per-simulator **binding** holds the "how much" (ORCA share,
  step-aside distance) and the declared thresholds.
- **Keep what the repository's format already gets right.** Rules are data, not code; there is a
  JSON Schema plus load-time checks; units are compulsory; a tie policy is required; a comparison
  on a missing value is false; there is "what a rule may read"; and there are provenance, status
  and a canonical form (`rule-format.md` §§1–9, §13).
- **Borrow two mechanisms from outside**: IG's **profiles**, so that a rule set declares which
  vocabulary version and features it uses ([Frantz-IG2Codebook] §4.6), and FMI's **semantic
  versioning with ignorable minor features** ([FMI-3.0.2] §1.3).

### 8.3 The main risks

1. **The behaviour will differ across simulators even when the core is identical.** Every docking
   study read found this, and Menge found it within one framework (§4.3; [Curtis-Menge] §4.1).
   *Mitigation*: claim decision conformance; measure behaviour against a pre-fixed equivalence
   standard.
2. **Adapters will implement the "same" term differently, and tests catch only what they test**
   (§6 modes 2, 6, 7). *Mitigation*: operational definitions; centrally owned reference cases;
   tolerances; FMI-style cross-checks.
3. **The vocabulary means something only within its scope.** Crossing from a passage to a queue
   crosses from a physical to a normative constraint, and knowledge conflicts and breaches are
   outside today's types (F2, F8, F9; [Wang-LCIM] §4.1; [Tessier-ConflictingAgents] p. 16).
   *Mitigation*: scope rules by sub-type until a test widens them; abstain outside the vocabulary.

### 8.4 What this review does **not** support

- Any claim that a rule "behaves the same" in two simulators: not shown anywhere in the four
  fields (§4.1).
- Any claim that portability has been demonstrated for arbitration rules: also absent in the
  simulation-rules review (`../simulation-rules/research-gap.md` §3).
- Any claim that the vocabulary itself is novel (§7).
- Any claim beyond structurally similar conflicts: no evidence that conventions transfer between
  structurally different games (`../game-theory/g6-transfer-across-games.md`, "What this means for
  the FYP").
