# Proposed implementation sequence (PT-7, Part 5)

> Issue [#41](https://github.com/M450NCH00/CrowdSimulation/issues/41), track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34), 2026-10-19.
> **A proposal.** None of these issues is created here; PT-8 (#42) already exists. Inputs complete
> (PT-1 to PT-6 merged). Verdicts: [feasibility.md](feasibility.md); target design: [idea.md](idea.md).

## How the verdicts changed the starting sequence

The issue's starting order was PT-8 → engine and negsim adapters → scenario cards and testbeds →
prompt version 3 → evaluation harness → trained deciders → CrowdGym binding. Four changes:

1. **A gate before PT-8.** The supervisor answers the brief's decisions 1-10, and confirms that the
   standing "no new simulation code" instruction is lifted for this track. PT-8 writes code (#34,
   constraints).
2. **The evaluation harness moves before prompt version 3.** No LLM-elicited rule exists yet
   (feasibility S1). So every free step (engine, testbeds, cards, harness) can be built and checked
   on the six hand-written seed rules first. The first paid step then comes after them, once vocabulary,
   bindings, cards and pass criteria are all frozen, as PT-2's freezing rules require.
3. **PT-8's paper test grows.** It must also check that the graded human evidence can be written as
   cores at all (feasibility S2), not only that today's rules can.
4. **Trained deciders and the CrowdGym binding become conditional:** on decision 7, and on access
   to CrowdGym's code (decision 10).

Order and dependencies:

```
gate (supervisor) → PT-8 → engine + negsim adapters ─┬→ evaluation harness → prompt v3 + pilot → trained deciders (if in scope)
                                                      └→ cards + testbeds ──┘
CrowdGym binding: blocked until CrowdGym's code or dependency list is available
```

---

## The issues

### PT-8 (#42, exists): vocabulary v0, rule-core format, and the paper test

Write vocabulary v0 and the core format on the adapted IG 2.0 shape (role; deontic; action;
activation by conflict sub-type and features; portable qualifiers; breach handling; deactivation;
deadline), with versioned profiles (PT-1, Representation).

**Settle first** the points PT-1 says must be decided before v0:
- F1: where negsim's *when* conditions go;
- F2: whether scope is the type or the sub-type (recommended: sub-type);
- F3: `wait` against `join_tail`;
- F4: predicted against recorded arrival;
- F6: time in seconds, and the engine's call rate as a binding;
- F7: tie policy;
- F9: breach handling and observer roles;
- F10: how many-person Situations are assembled.

Add roles by category and a "kind of reason" feature **only if** decisions 3 and 4 allow them.

**The paper test has three parts:**
1. Hand-convert the six seed rules into cores.
2. Try to write a core, or a pass criterion, for each graded reference behaviour: QC-1 to QC-8,
   BA-1, BA-2, BA-4, LE-1, LE-2. Record which cannot be written and why.
3. Confirm that the L4 candidate (`signalised_crossing`) falls **outside** the vocabulary.

Also write down the seen/held-out split (decision 6). Freeze v0 at the end. Zero spend.

### Rule engine and negsim adapters, with an identity check

Build a standalone engine, in a new top-level folder that imports nothing from any simulator. It
matches cores to a Situation and returns a Decision.

Write negsim's two adapters:
- the perception adapter takes over today's when-conditions as conflict detection (C4);
- the action adapter maps intentions onto today's directives, through a declared ORCA binding.

**The identity check is the acceptance test.** Re-run the six seed rules through the engine on the
seeds and configurations of issue #28's free runs. Require identical decisions and identical
trajectories. Any difference is a bug, or a finding that weakens verdict 1.2.

Start the central conformance set: Situation → Decision cases, single-feature first, with
tolerances (PT-1, change 4).

**Constraint:** #34 forbids changes to `llm_negotiation/` unless an issue says so. The adapters
must wrap negsim from outside. If a hook inside negsim turns out to be needed, this issue must ask
first and name the change. Zero spend.

### Scenario cards and the testbeds of PT-6

Write cards in PT-2's assembled format (RiMEA, Ronchi, IMO, OpenSCENARIO, JuPedSim journeys,
SteerBench scoring, ODD patterns):
- queue cutting first, then the train door and lift priority, each with pass criteria fixed before
  any run and each reference behaviour labelled with its city and year (C7);
- bus boarding and escalator merging as **motion-only** cards.

Build the two testbeds of PT-6's hybrid (C8), with pinned versions:
- **JuPedSim 1.4.2:** our own queue-order layer on direct steering, never `NotifiableQueueStage`
  where order changes; the platform door with a scripted vehicle.
- **Mesa 3.5.1, with `networkx` pinned:** the queue as lists plus `schedule_event`; the door as a
  capacity-one cell.

Write both adapters per testbed following PT-6's five adapter rules: journey-aware targets;
perception every 0.1 s; stored queue places; compare runs by spawn order; our own conflict-event
log. Write per-simulator scene → Situation tests against shared expected Situations (F5).

Cards live in this track's folder. `dataset/scenarios.yaml` (Phase 1) is not edited. Zero spend.

### Evaluation harness

Implement PT-2's protocol (C7):
- levels L0 to L4, with L0 split into new seeds and new co-players;
- L3 run both ways wherever rules exist on both sides;
- wording and convention axes;
- freezing recorded as the commit hash of cores, bindings, adapters and cards in every run log.

Baselines:
- no rule;
- a simple stated convention;
- the LLM deciding directly, optional and paid, so off by default;
- a rule elicited for the held-out type itself as the ceiling.

Two kinds of metric:
- **decision conformance** across testbeds on the shared Situations;
- **behavioural difference** against an equivalence standard fixed in advance (PT-1, change 1).

Score motion metrics on every card, and fidelity metrics only where graded evidence exists. Report
raw scores, results as case studies, and every result labelled by rule origin (C9). Rehearse the
whole harness on the seed rules. Zero spend.

### Prompt version 3 and the paid pilot

Have the LLM state the core directly in the frozen vocabulary v0, for the **seen** conflict types
only. This joins the held pilot of the existing plan (SI-3b, then SI-4).

Add a validator for the error TR2MTL found most often: wrong logical connectives (PT-1
`novelty-check.md` §3). Rehearse on the mock client first. Run the paid pilot only with a recorded
approval and a hard spend cap (issue #30's Q5). The result is the first LLM-elicited rules. Run
them through the harness; this is the first result that speaks for LLM-elicited rules.

This is the first step in the sequence that spends money; the only other is trained deciders'
teacher labels. The fictional group stays off pending the ethics sign-off.

### Trained deciders (only if decision 7 puts them in scope)

Train small trees or rule lists on Situation features against an LLM-filled lookup table, with the
engine as reference and shield (C6). Teachers:
- LLM labels from several models, with disagreement reported; these are paid calls, needing their
  own budget;
- the rules;
- a rule-only student as the pipeline check (E5 = 100%).

Evaluate with PT-4's checks E1, E3, E4 and E6, and bias checks B1 to B3. B6 and B7 for
`ethnic_group` wait for the ethics sign-off.

### CrowdGym binding (blocked)

Write CrowdGym's two adapters and its binding, and run its conformance and scene tests. **Blocked**
until CrowdGym's code, or at least its dependency list, is available (PT-5 §2; PT-6). If it is built
on JuPedSim, the JuPedSim adapters should carry over largely as they are; if not, this is a new
testbed. Do not plan the details before that is known.

---

## Follow-ups that are not implementation

These need a human route, not a session:
- **Obtain the missing sources:**
  - PT-3's fourteen, chiefly Milgram et al. 1986, Schmitt et al. 1992, the two boarding-before-
    alighting studies (BA-8) and the two Singapore bus studies;
  - PT-1's two unread leads: arXiv:2509.02515 and NormSage.
- **Singapore observation** of the five behaviours would replace borrowed evidence. That would be
  new data collection with people, so it needs the supervisor and ethics approval. It is named here
  only as an option.

## Risks to the sequence

- The identity check may fail. Then cores cannot carry today's rules without loss, and PT-8 must
  be revisited before anything else.
- The pilot may stay held. Then every result in this track speaks only for hand-written rules (S1),
  and the report must say so.
- Decision 8 may come back "no". Then PT-6's option (a), using JuPedSim and Mesa as shipped, is as
  good, and the queue-order layer in the testbeds issue can be dropped.
