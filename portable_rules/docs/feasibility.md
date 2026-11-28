# Feasibility verdict and novelty (PT-7, Parts 1 and 3)

> Issue [#41](https://github.com/M450NCH00/CrowdSimulation/issues/41), track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34), 2026-10-19.
> Companion files: [idea](idea.md) · [supervisor brief](supervisor-brief.md) ·
> [implementation plan](implementation-plan.md).

## Status

- **#34's idea is a proposal, not agreed.** These verdicts judge it; they do not adopt it. Every
  recommendation here needs the supervisor's sign-off.
- **Inputs: complete.** PT-1 to PT-6 are all merged (PRs #43 to #48). No document in this folder
  works around a missing input.
- **No new literature was searched.** Every verdict rests on a PT file, cited in each row. Bracketed
  handles such as [Curtis-Menge] are the PT files' own; follow the PT file to the source.
  Statements marked `[synthesis]` are mine, drawn from two or more PT files read together, or from
  the repository's current state; they carry no source of their own.

The PT files, and the short names used below:

| Short name | File | Question |
|---|---|---|
| **PT-1** | [`literature/portable-rules/verdict.md`](../../literature/portable-rules/verdict.md) (and `feasibility.md` F1-F11, `novelty-check.md`) | Can a rule core be written once and carried out by several simulators? |
| **PT-2** | [`literature/unseen-scenarios/verdict.md`](../../literature/unseen-scenarios/verdict.md) (and `test-protocol-draft.md`) | How should rules be tested on scenarios they were not extracted from? |
| **PT-3** | [`literature/unseen-scenario-evidence/verdict.md`](../../literature/unseen-scenario-evidence/verdict.md) (and `reference-behaviours.md`) | Is there human evidence to test those scenarios against? |
| **PT-4** | [`literature/trained-deciders/verdict.md`](../../literature/trained-deciders/verdict.md) | Which trained models, if any, are worth adding? |
| **PT-5** | [`integration/simulator-survey/shortlist.md`](../../integration/simulator-survey/shortlist.md) | Which simulators to try? |
| **PT-6** | [`integration/simulator-survey/decision.md`](../../integration/simulator-survey/decision.md) (and `hands-on.md`) | Use, build, or both? |

---

## Part 1. A verdict for each part of the idea

### Summary

| Part of #34's idea | Verdict | Rests on | The change it needs, in one line |
|---|---|---|---|
| 1. Portable core and vocabulary | **Feasible with changes** | PT-1 | adapt institutional grammar; define every term operationally; add breach handling and observer roles |
| 2. Adapters and bindings | **Feasible with changes** | PT-1, PT-6 | today's rules cannot become the ORCA binding "unchanged": their *when* conditions must move |
| 3. Engine and conformance tests | **Feasible with changes** | PT-1, PT-4, PT-6 | claim decision conformance, not identical behaviour; tests find faults, they do not prove conformance |
| 4. Trained deciders | **Feasible with changes, narrowed** | PT-4 | optional and secondary; small trees against an LLM lookup table only; RL policies **not supported** |
| 5. Testing on unseen scenarios | **Feasible with changes; human fidelity not supported for two of five scenarios** | PT-2, PT-3 | fidelity tests only where graded evidence exists; motion-only elsewhere; results are case studies |
| 6. Testbeds | **Feasible with changes** | PT-5, PT-6 | JuPedSim needs our own queue-order layer; CrowdGym stays a conditional target |

**No part is rejected outright.** Five sub-claims are **not supported** and must be dropped or
narrowed; they are listed under each part and collected in Part 3.3. PT-8 must not start on any of
them as stated.

**Two findings come only from reading the PT files together** `[synthesis]`, and they shape the
sequence more than any single verdict:

- **S1. No LLM-elicited rule exists yet.** All six rules in the rule database are hand-written test
  seeds (`llm_negotiation/rule_db/rules/*.yaml`: `source_type: hand_written`, `status: test_seed`),
  and the paid pilot that would elicit the first ones is held (README roadmap, step 3c). Every
  portability test can be built and run on the seeds, but **a result about LLM-elicited rules needs
  the pilot first**. Until then, results must be labelled "hand-written seed rules".
- **S2. The best human evidence for the held-out scenarios is about behaviour the vocabulary cannot
  yet express.** Queue cutting is the best-evidenced unseen scenario (PT-3), but most of that
  evidence is about **who objects** to a cutter (QC-1 to QC-5: bystanders) and about **asking with a
  reason** (QC-6 to QC-8). The first needs breach handling and observer roles, which #34's
  vocabulary lacks (PT-1, F9). The second is the kind of rule today's pipeline rejects as
  `needs_communication` (#34, decision 4). Likewise the train-door evidence, "alighting starts
  before boarding" (BA-1), needs roles given by category, which today's format cannot write (#34,
  decision 3). So **what the unseen tests can check against people depends on decisions 3 and 4 and
  on PT-8 adding breach handling**, not only on the evidence.

---

### 1.1 The portable core and its vocabulary — **feasible with changes**

**Evidence.**
- Writing a conflict rule down independently of what runs it has decades of precedent in norm
  representation: institutional grammar IG 2.0 and normative agent-based simulation (PT-1,
  [Frantz-IG2]; [Hollander-NormativeABS]).
- No crowd, pedestrian, game or robot-navigation study read compared one behaviour rule across two
  simulators (PT-1, "No precedent").
- #34's own draft already holds four term-level faults (PT-1 `feasibility.md`):
  - **F1:** today's conditions (time to collision, encounter class) are not in the vocabulary.
  - **F2:** the worked example crosses from passage to queue, a sub-type boundary the idea says to
    respect.
  - **F3:** `wait` against `join_tail` is unresolved.
  - **F4:** `arrival_order` means a *predicted* arrival in today's rule and a *recorded* one in a
    queue.
- Knowledge conflicts and breaches fall outside the three conflict types (PT-1 F8, F9;
  [Tessier-ConflictingAgents] §3.2; [Mellema-Sanctions] §6).

**Changes needed (PT-1, "Changes needed" 1-3 and "Representation").**
1. Restructure the core around an **adapted** IG 2.0: role, must/may/must not, action, activation
   (conflict type plus features), portable qualifiers, breach handling. Add deactivation, a
   deadline, violation handling against observer roles, and versioned profiles. Do not adopt IG 2.0
   as it stands: it has no execution semantics and its taxonomies are open.
2. Define every term operationally: unit, strictness, tie policy, who can know it, reference cases.
3. Split `arrival_order` into predicted and recorded (F4); state time in seconds, never steps (F6).
4. Decide whether a rule's scope is the conflict **type** or the **sub-type** (F2). `[synthesis]`
   recommendation: the sub-type by default, with any crossing (passage → queue) run as a logged
   transfer test. This keeps the claim within what the transfer evidence supports (PT-2: transfer
   holds within a class, is directional, and can harm).

**Main risk.** The vocabulary holds only within its scope. Passage → queue crosses from a physical
constraint to a normative one (PT-1, risk 3; [Tessier-ConflictingAgents] p. 16).

**Not supported:** a vocabulary that covers "any conflict". The claim stays "the same kind of
conflict" (PT-1; PT-2).

---

### 1.2 The adapters and bindings — **feasible with changes**

**Evidence.**
- What travels well between tools is *execution behind a small typed interface*, not a description
  (PT-1, [FMI-3.0.2] §1.3). Even then, 5 of 10 importers failed the reference tests (PT-1,
  [Bertsch-ReferenceFMUs] §4.3).
- Wrappers absorb decisions and drift apart (PT-1, risk 2; [Gomes-CoSim] §5.2).
- **Both adapter hooks work in practice** in JuPedSim 1.4.2 and Mesa 3.5.1: positions, queue order,
  mid-run speed and route changes (PT-6, trial 3; `hands-on.md`).
- PT-6 also found traps any adapter must handle. In JuPedSim a target set outside direct steering
  is dropped silently. A full Python perception read costs as much as an iteration at 10,000 agents,
  so perception should sample every 0.1 s (PT-6, "Rules the adapters must follow" 1-5).

**Changes needed.**
1. **Drop "today's rules become the ORCA binding, unchanged".** Their *when* conditions are negsim
   measurements, so either the binding or the perception adapter decides *when* a rule applies, not
   only "how much" (PT-1 F1). `[synthesis]` recommendation: move conflict detection into negsim's
   perception adapter, which then states "a conflict of type X exists, with these roles". Treat that
   adapter as making a decision, and test it.
2. Put every simulator-dependent quantity in declared bindings: thresholds, timing in seconds, the
   engine's call rate, update order (PT-1, change 2).
3. Freeze bindings as well as cores before any held-out run (PT-2, change 4; [Tordeux-ANN] Table 1).

**Main risk.** Two adapters implement the "same" term differently, and the tests catch only what
they test (PT-1, risk 2).

---

### 1.3 The engine and conformance tests — **feasible with changes**

**Evidence.**
- A standalone engine is cheap: arbitration rules have already run at 10,000 agents (PT-4, point 1,
  citing `research-gap.md` §6).
- Behaviour differs across simulators even with an identical rule: one behaviour layer under three
  motion models gave different trajectories (PT-1, risk 1; [Curtis-Menge] §4.1). Every docking study
  read found differences on details outside the rule's text: update order, tie-breaking, ≤ against
  <, run length (PT-1; [Axtell-Docking]; [Edmonds-Replication]; [Wilensky-MakingModelsMatch];
  [Galan-Reimplementing]).
- Passing a test shows that no tested fault was found, not conformance (PT-1 F11;
  [Bertsch-ReferenceFMUs] §2.1).
- "Scene → expected Situation" tests cannot be shared verbatim between a continuous and a discrete
  simulator (PT-1 F5).

**Changes needed.**
1. Claim **decision conformance** (same Situation → same Decision). **Measure** behaviour against an
   equivalence standard fixed in advance (PT-1, change 1; [Axtell-Docking] §6).
2. Own the conformance tests centrally, single-feature first, with tolerances; add long closed-loop
   runs (PT-1, change 4; F5).
3. Write the scene tests per simulator, against a shared expected Situation (F5).
4. Restate "a simulator supports the rules when its adapters pass both sets" as "no fault found by
   these tests" (F11).

**Main risk.** Identical decisions still give different motion (PT-1, risk 1). Results must report
behavioural differences, not hide them.

**Not supported:** "the same behaviour in every simulator", and "passing the tests means
conformance".

---

### 1.4 Trained deciders — **feasible with changes, narrowed**

**Evidence.**
- The rule engine is already cheap. A rule-regularised teacher beat its own distilled student
  (PT-4, point 1; [Hu-LogicRules] Table 2).
- Small decision trees or rule lists on Situation features run at 10,000 agents, can be checked
  exhaustively, and are as portable as the rules, since they read the same inputs (PT-4, point 2;
  [Li-GenWorld] §4; [Bastani-VIPER] §4).
- RL policies with rule rewards need one policy per simulator, and no transfer between simulators
  has been tested anywhere (PT-4, point 4; [Chen-SACADRL]; [Icarte-RewardMachines]). A small
  language model at run time takes 0.5-2 s per call (PT-4, point 4; [Li-GenWorld] §7.1.5).
- No source compares a learned interpretable model with hand-written rules, and none tests a
  trained decider across simulators (PT-4, point 7).

**Changes needed.**
1. The engine stays the **reference** decider. Add a trained model only for a claim fixed in
   advance: closer to human evidence, the same decisions more cheaply, or decisions where no rule
   matches (PT-4, point 1).
2. Train only small trees or rule lists, against an LLM-filled lookup table as baseline (PT-4,
   point 2). Use the **shield** pattern: a trained decider proposes, the engine blocks what breaks a
   hard rule (PT-4, point 4; [Alshiekh-Shielding]).
3. Teachers: LLM decisions from several models, disagreement reported; rules combined with those
   labels; session outcomes as held-out data only; human data as the reference (PT-4, point 3).

**Main risk.** The teacher's bias passes into the student. Demographic effects reverse between
models (PT-4, point 3, citing issue #16). Teacher labels from several LLMs are also **paid calls**
`[synthesis]`.

**Not supported:** RL policies, or a language model at run time, as portable deciders.

---

### 1.5 Testing on unseen scenarios — **feasible with changes; human fidelity not supported for two of five scenarios**

**Evidence.**
- **The protocol is buildable, but in part it is the FYP's own design.** No field read holds out a
  whole *type* of situation when testing a behaviour rule (PT-2; [MeltingPot-1] §4.1).
- **The transfer evidence supports scoping by conflict type.** Humans carry a convention across
  structurally different games, but always within one class; transfer is directional and can harm
  (PT-2; [CooperVanHuyck-Transfer]; [Cason-Spillovers]).
- **No existing scenario format can describe the held-out scenarios,** so the scenario card has to
  be assembled from seven sources (PT-2, card table).
- **Human evidence by scenario (PT-3):**

  | Scenario | Evidence |
  |---|---|
  | Queue cutting | grade B for the pattern, not the rates (old, Western, partly second-hand) |
  | Train doors | partly (B/C) |
  | Lifts | priority only (B) |
  | Bus boarding | **none** |
  | Escalator merging | weak |

  No statement reaches grade A. **No Singapore observation of any of the five behaviours exists**;
  every reference behaviour must be borrowed from London, New York or Taipei, and labelled so. Age
  and gender differences in these scenarios cannot be checked against human data.
- **Only five conflict types** exist in the draft, so leave-one-type-out results will be case
  studies, not statistics (PT-2, risk 3).
- **L4 (abstain outside the vocabulary) has no literature behind it** (PT-2, risk 2; U1).
- **S2 above** `[synthesis]`: the queue-cutting evidence is mostly about objectors and requests;
  the train-door evidence needs roles by category.

**Changes needed.**
1. Adopt PT-2's four protocol changes:
   - split L0 into new seeds and new co-players;
   - run L3 both ways wherever rules exist on both sides;
   - add a wording axis and a convention axis, since a reworded familiar conflict is never L3;
   - freeze bindings with cores.
2. Score **fidelity** (is it what people do?) only where graded evidence exists. That means queue
   cutting (pattern level), train doors (alighting first, door-side waiting) and lifts (priority).
   Score bus boarding and escalators on **motion** only (does it clear?) until evidence is obtained
   (PT-2, risk 1; PT-3).
3. Label every reference behaviour with its city and year. Make no Singapore-specific fidelity
   claim (PT-3, Q4).
4. Report results as case studies (PT-2, risk 3).
5. Keep L4 as an explicitly unsupported proposal (PT-2, U1).
6. `[synthesis]` Note in every result whether the rules tested are hand-written seeds or
   LLM-elicited (S1).

**Main risk.** Human evidence for the held-out types is the bottleneck (PT-2, risk 1). Fourteen
sources need a library or browser download (PT-3, point 2). The two that would fill the biggest gap
(how often people board before alighting has finished, BA-8) are among them.

**Not supported:** "human evidence is the reference" for bus boarding and escalator merging; any
Singapore-specific or age/gender fidelity claim in these scenarios.

---

### 1.6 The testbeds — **feasible with changes**

**Evidence.**
- PT-5 shortlisted JuPedSim (the second continuous testbed), Mesa (the discrete queue model) and
  SUMO (conditional). Vadere and Menge cannot be installed under the trial's rules and stay desk
  references (PT-5).
- PT-6 ran JuPedSim 1.4.2 and Mesa 3.5.1 from pinned wheels (PT-6):
  - **JuPedSim's built-in queue cannot admit anyone part-way**, and keeps people listed after they
    leave. Our own queue-order layer with direct steering worked in 47 lines including the scene
    (trial 1).
  - The door, the waiting set and two-way door flow work, with no deadlock (trial 2).
  - Both simulators are deterministic.
  - At 10,000 agents JuPedSim ran 2.9-3.4× negsim's speed per simulated second (trial 4). That is
    still slower than real time: 0.21 simulated s per computing s (README, PT-6 findings).
- PT-6's recommendation is the **hybrid**: JuPedSim for motion and boarding, with our own queue
  layer; Mesa as the discrete testbed; SUMO not needed. It leads under every weighting tried but one.
- Whether CrowdGym is built on JuPedSim is unknown; its code is not available to this project
  (PT-5; PT-6, "Fit with CrowdGym is conditional").

**Changes needed.**
1. Replace #34's "a second continuous simulator with queues and waiting areas" with "JuPedSim for
   motion, with our own queue-order layer". The queue the simulator ships cannot express "admit"
   (PT-6, trial 1).
2. Keep CrowdGym as a **conditional** target. Plan no CrowdGym binding until its code, or at least
   its dependency list, is available (PT-5; PT-6).
3. Ask the supervisor the one question that changes PT-6's answer: must each unseen conflict type
   run in two structurally different testbeds? (PT-6, sensitivity).

**Main risk.** The CrowdGym fit may not hold. The JuPedSim models are uncalibrated for Singapore
crowds, so every number from them is a model property, not evidence about people (PT-6, "What this
decision does not settle").

---

## Part 3. What is new

### 3.1 Against the closest prior work

| Work | What it shares with this idea | What it does not do |
|---|---|---|
| **Zhang et al. 2026** (NTU, ACM TOMACS; the repository's closest prior work) | Distils an LLM-driven crowd into commented code that plain agents run, dropping the LLM at run time (summary §1, §8; PT-1 `novelty-check.md` §3) | One simulator, and its features are that simulator's own (exit cells, positions, crowdedness). Its "out-of-domain" set is a **new layout of the same evacuation task** (paper §5.1), i.e. PT-2's L2, not a new conflict type. It is validated against LLM ground truth, **not human behaviour**: "the validity of the distilled function depends directly on the reference data" (§6.1). No negotiation between agents; agent interaction is not a feature (§7) |
| **Horiguchi et al. 2024, arXiv:2409.00993** (PT-1's novelty check) | LLM agents reach norms through dialogue: the FYP's *method* | Nothing is written down as a rule or run by another system. One abstract game. Transfer is future work. Prior art for the method only (PT-1 `novelty-check.md` §1-§2) |
| **Ren et al. 2024, CRSEC** (IJCAI) | LLM-derived norms stored as structured records | The norm's core is natural language, read only by LLM agents, in one environment (PT-1 `novelty-check.md` §3) |
| **Manas et al. 2024, TR2MTL** (IEEE IV) | The closest *shape*: a formal rule over a fixed predicate vocabulary, run through a hand-written predicate mapping (in effect a perception adapter) | Translates **human-written** traffic law, not LLM-elicited rules; one simulator. Its main error, wrong logical connectives, warns whoever has an LLM write cores (PT-1 `novelty-check.md` §3) |
| **Savarimuthu et al. 2024** | Names both adapters for LLM agents | Argues *against* fixed symbolic norms in open systems. The strongest counter-position, which the report must answer (PT-1 `novelty-check.md` §3) |
| **HuNavSim 2; Menge; FMI** | One behaviour engine in four hosts; behaviour apart from motion; execution behind a typed interface | No behavioural comparison across hosts; one behaviour layer under three motion models gave different trajectories (PT-1 verdict) |
| **Docking studies** (Axtell; Edmonds and Hales; Wilensky and Rand; Galán) | Test whether one rule behaves the same in two implementations | Social simulation, not crowds; every one found differences (PT-1 verdict) |
| **Melting Pot** | Held-out testing of social behaviour | Holds out co-players, never worlds (PT-2) |
| **Trained deciders** (PT-4 sources) | Distillation, interpretable models, shields | None compares a learned interpretable model with hand-written rules; none tests a trained decider across simulators (PT-4, point 7) |

### 3.2 The new part

The new part is the **combination**. No ingredient on its own is new (PT-1, "Novelty"; PT-1
`novelty-check.md` §4):

> Conflict rules elicited from LLM agents, written as simulator-independent artefacts, carried out
> by non-LLM agents in more than one structurally different simulator, and tested on conflict types
> held out from extraction, against graded human evidence.

Within that, the two most novel elements are also the riskiest `[synthesis]`:
- **The cross-simulator test** has a known failure record (PT-1, caveat 2).
- **The whole-type hold-out** has no precedent for behaviour rules (PT-2).

The vocabulary is the **least** novel part. The report should present it as an adaptation of
institutional grammar, not as a new grammar (PT-1 `novelty-check.md` §4, caveat 1).

### 3.3 What the evidence does not support

| Claim | Why not | Source |
|---|---|---|
| The same rule gives **the same behaviour** in every simulator | Identical rules gave different trajectories; every docking study found differences | PT-1 risk 1; group 6 |
| Passing conformance tests **proves** a simulator conforms | Tests find faults; they cannot show their absence | PT-1 F11 |
| Today's rules become the ORCA binding **unchanged** | Their *when* conditions are negsim measurements outside the vocabulary | PT-1 F1 |
| Rules transfer across **structurally different** conflict classes ("any conflict") | Human transfer was found only within a class, directional, sometimes harmful | PT-2; `g6-transfer-across-games.md` |
| Unseen-scenario results are **statistically general** | Five conflict types: case studies | PT-2 risk 3 |
| The rules match **Singapore** behaviour, or **age/gender** differences, in these scenarios | No Singapore observation; age and gender almost unmeasured | PT-3 Q4, Q5 |
| Human evidence is the reference for **bus boarding** and **escalator merging** | None, or weak | PT-3 table |
| Abstaining outside the vocabulary (L4) is the **right** behaviour | No source tests abstention | PT-2 U1 |
| Trained deciders are **better** than the rules, or portable as RL policies | No comparison exists; RL transfer untested | PT-4 points 4, 7 |
| The tests show that **LLMs understand** human behaviour | They test the extracted rules, not the LLM's understanding; leakage can only be graded | PT-2 (g5 §4 level) |
| Results speak for **LLM-elicited** rules today | None exists yet; all six rules are hand-written seeds | S1 `[synthesis]` |
| The portable pipeline runs **10,000 agents in real time** | Components scale (rules, lookup tables, small trees; JuPedSim at 10,000), but JuPedSim ran at 0.21 simulated s per computing s, and no end-to-end run exists | PT-4 point 5; PT-6 trial 4 |
| **No one** has done this | Only "none found in this review": English-language, one session; two leads unread | PT-1 `novelty-check.md` §4, caveat 3 |

---

## Open questions

1. **Scope: type or sub-type** (F2)? This document recommends the sub-type; the supervisor should
   decide.
2. **Where conflict detection lives** in negsim (F1): the perception adapter (recommended) or the
   binding?
3. **The identity check.** Can the six seed rules be re-expressed as cores without any behaviour
   change in negsim? Only PT-8 and the engine issue can show it. If not, this verdict on part 2
   weakens.
4. **Does breach handling (F9) make queue cutting an L3 test or an L4 one?** No seen rule uses
   observer roles. Until one is elicited, the objection evidence (QC-1 to QC-5) can only score a
   rule elicited for queues themselves (the PT-2 "exploiter" ceiling), not a transferred one
   `[synthesis]`.
5. **Unread leads** (named as follow-ups, not searched):
   - arXiv:2509.02515 and NormSage (PT-1 `novelty-check.md` §4);
   - the 14 sources PT-3 could not download;
   - CrowdGym's code (`WORK_LOG-39.md` Q1; `WORK_LOG-40.md` A2).
