# Verdict: how should extracted rules be tested on scenarios they were not extracted from?

> PT-2 ([#36](https://github.com/M450NCH00/CrowdSimulation/issues/36)), for PT-7: one page.
> Handles are entries in [methods.md](methods.md) and
> [scenario-standards.md](scenario-standards.md); the protocol is
> [test-protocol-draft.md](test-protocol-draft.md). #34's idea, and this protocol, are proposals
> awaiting the supervisor's sign-off.

**Verdict: testable, but the literature supplies only parts of the method.** No field read here
holds out a whole *type* of situation when testing a behaviour rule:

- **Melting Pot** holds out co-players, never worlds ("Policies are not transferable between
  substrates", [MeltingPot-1] §4.1).
- **Pedestrian modelling** has one small cross-geometry study ([Tordeux-ANN]) and a calibration
  framework that leaves cross-scenario generalisation as future work ([Wolinski-ParamEst] §5).
- **Evacuation V&V** reuses tests outside their context, and warns against doing so
  ([Ronchi-TN1822] Abstract).

The whole-type hold-out is therefore the FYP's own design, argued from the transfer evidence.

**The transfer evidence is better than g6 found, and it supports scoping by conflict type.** With
five of g6 §3's six leads now read:

- Humans **do** carry a convention to a differently structured game: "even when games are not
  structurally similar" ([CooperVanHuyck-Transfer] §4, p. 24). But always **within one class**
  (coordination games with a payoff-dominant equilibrium; signalling games).
- Transfer is **directional** ([Cason-Spillovers] §7) and can **harm** ([CooperVanHuyck-Transfer]
  §1, p. 7).
- It depends on how easily situations are **told apart** ([Huck-FeedbackSpillover] §7;
  [GrimmMengel-MultipleGames] §4) and on **meaningful context** ([CooperKagel-Signaling] §VII).

This qualifies g6's "no evidence" and backs #34's narrower claim, "the same kind of conflict".

**No existing scenario format can describe the held-out scenarios.** None of the eight read says
who should go first in a contested resource. None has communication. Only JuPedSim has a queue, and
nobody can join it part-way ([JuPedSim-1.4.2]). The card has to be **assembled**:

| Card part | Taken from |
|---|---|
| Background / Aim / Setup | [RiMEA-4.1.1] |
| Geometry / Scenario / Expected result / Test method | [Ronchi-TN1822] §3.0 |
| Population by age, gender and mobility | [IMO-Circ1533] Table 3.1 |
| Initial state, then events started by triggers | [OpenSCENARIO-1.4] |
| Journeys of stages | [JuPedSim-1.4.2] |
| Pass/fail scored from logged trajectories | [SteerBench-2009] |
| Patterns, including expected misses | [ODD-2020] |

**Leakage can be graded, not ruled out** (counterfactual variants, [Wu-Counterfactual]; new
variants, [Aher-TuringExperiments]; perturbations, [Binz-CogPsychGPT3]). The claim stays at g5
§4's level: test the rules, not the LLM's understanding.

**Changes to the starting protocol:**

1. **Split L0** into new seeds (≥ 10 populations × 5 runs, [IMO-Circ1533] App. 3) and new
   co-players in visitor and resident modes ([MeltingPot-1] §4.2).
2. **Run L3 in both directions** wherever rules exist on both sides ([Cason-Spillovers];
   [Tordeux-ANN]).
3. **Add a wording axis and a convention axis** for the LLM stage. A reworded familiar conflict is
   never L3 ([Aher-TuringExperiments] App. F).
4. **Freeze bindings as well as cores** before held-out runs. Parameters shift with layout
   ([Tordeux-ANN] Table 1), and re-tuning would hide failure ([Wolinski-ParamEst]).

**Main risks:**

1. **Human evidence for held-out types (PT-3) is the bottleneck.** Without it, L3 scores only
   motion (does it clear?), not fidelity (is it what people do?).
2. **L4 (abstain) has no literature behind it** (open question U1).
3. **Few conflict types** (five in #34's draft): leave-one-type-out results will be case studies,
   not statistics. Queue cutting is not yet in `dataset/scenarios.yaml`.
