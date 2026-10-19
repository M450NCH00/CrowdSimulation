# Verdict: is a portable rule core feasible?

> PT-1 ([#35](https://github.com/M450NCH00/CrowdSimulation/issues/35)), for PT-7: one page.
> Handles are entries in [representations.md](representations.md) and
> [novelty-check.md](novelty-check.md); the argument is in [feasibility.md](feasibility.md).
> #34's idea is still a proposal awaiting the supervisor's sign-off.

**Verdict: feasible with changes.** Writing a conflict rule down independently of any simulator has
been done for decades with norms ([Frantz-IG2]; [Hollander-NormativeABS]). The literature does
**not** support the second half, "carried out faithfully by several simulators":

- **No precedent in the fields that matter.** No crowd, pedestrian, game or robot-navigation study
  read here compared one behaviour rule across two simulators. [EscuderoJimenez-HuNavSim2] runs one
  behaviour engine in four hosts but compares nothing. In [Curtis-Menge], one behaviour layer under
  three motion models gave different trajectories.
- **Where it was tried, it differed.** Every docking study read found behaviour changing on details
  outside the rule's text: update order, tie-breaking, ≤ against <, run length ([Axtell-Docking];
  [Edmonds-Replication]; [Wilensky-MakingModelsMatch]; [Galan-Reimplementing]).
- **What works is shipping execution, not descriptions.** FMI runs in many tools because the
  implementation travels behind a small typed interface ([FMI-3.0.2] §1.3). Even so, 5 of 10
  importers failed reference tests ([Bertsch-ReferenceFMUs] §4.3).

**Changes needed:**

1. Claim **decision conformance** (same Situation → same Decision); *measure* behaviour against an
   equivalence standard fixed in advance ([Axtell-Docking] §6).
2. Put every simulator-dependent quantity in declared bindings: thresholds, timing in seconds, the
   engine's call rate, update order.
3. Define each term operationally: its unit ([FMI-3.0.2] §2.4.3), strictness, ties, who can know it,
   and reference cases. `arrival_order` already has two meanings in #34's own example
   (feasibility F4).
4. Centrally owned conformance tests, single-feature first, with tolerances
   ([Bertsch-ReferenceFMUs]), plus long closed-loop runs.

**Representation:** extend this repository's rule format (data not code; schema; compulsory units
and tie policy; "what a rule may read"), restructured around an **adapted IG 2.0** ([Frantz-IG2]
§3.1):

| IG 2.0 component | In the core |
|---|---|
| Attribute | role |
| Deontic | must / may / must not |
| Aim | action |
| Activation Condition | conflict type + features |
| Execution Constraint | portable qualifiers |
| Or else | breach handling |

Add deactivation, a deadline, and violation-handling against meta-norm roles ([Mellema-Sanctions]),
and IG profiles for versioning ([Frantz-IG2Codebook] §4.6). Do not adopt IG 2.0 as it stands: it
has no execution semantics and its taxonomies are open.

**Main risks:**

1. Behaviour will differ across simulators even with an identical core ([Curtis-Menge] §4.1;
   group 6).
2. Adapters will implement the "same" term differently, and tests catch only what they test
   ([Gomes-CoSim] §5.2; [Wang-LCIM] §3.1).
3. The vocabulary holds only within its scope. Passage → queue crosses from a physical to a
   normative constraint ([Tessier-ConflictingAgents] p. 16). Knowledge conflicts and breaches fall
   outside today's types.

**Novelty:** arXiv:2409.00993 shares the method only; it writes nothing down for reuse. What is new
is the combination, an LLM-elicited conflict rule checked in more than one simulator. No ingredient
on its own is new.
