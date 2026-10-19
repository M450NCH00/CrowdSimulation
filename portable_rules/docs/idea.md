# The idea, restated (PT-7, Part 2)

> Issue [#41](https://github.com/M450NCH00/CrowdSimulation/issues/41), track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34), 2026-10-19.
> **Still a proposal. It needs the supervisor's sign-off.** Inputs complete (PT-1 to PT-6 merged).
> Changes from #34 are marked **[C1]** to **[C10]**; the table below gives each reason. Evidence:
> [feasibility.md](feasibility.md).

## In one paragraph

LLM agents settle a conflict between people, and the settlement is written down as a **rule**.
This idea makes that rule usable outside the simulator it came from, and tests it where it was
never extracted. A rule states *who must, may or must not do what, in which kind of conflict*,
using a small, fixed list of words that any simulator can be taught to read. Each simulator gets
two small translators: one describes its scene in those words, the other carries out the decision.
A separate rule engine makes the decision. The claim is narrow: **in the same kind of conflict, a
rule gives the same decision in any simulator that passes the shared tests** [C1]. How people
actually move after that decision is *measured* and compared, not promised [C1].

## The parts

1. **The rule core.**
   - Its shape is adapted from institutional grammar: role; must, may or must not; action; when it
     applies; extra conditions; what happens on a breach [C3].
   - The vocabulary has four lists:
     - **conflict types**: room to pass; one at a time through a passage, a queue or a vehicle
       door; limited capacity;
     - **roles**, for any number of people, including observers of a breach [C3];
     - **observable features**;
     - **actions** stated as intentions.
   - Every word has a definition every simulator can follow: unit, strictness, tie rule, who can
     know it, and worked examples [C3]. "Arrival order" becomes two words, predicted and recorded
     [C3]. Time is in seconds, never steps [C3].
   - A rule applies to one **sub-type** of conflict. Using it in another sub-type (passage to queue)
     is a deliberate, logged transfer test [C2].
2. **Two translators per simulator, plus bindings.**
   - The *perception* translator says which conflict exists and who holds which role. In negsim this
     takes over today's "when" conditions (time to collision, encounter class). That is a decision,
     so it is tested [C4].
   - The *action* translator turns a decision into the simulator's controls.
   - The "how much" (distances, ORCA shares, thresholds, call rate) lives in a declared, versioned
     binding per simulator. The binding is frozen before any held-out test [C4].
   - Today's six seed rules must be shown to behave **identically** in negsim after conversion
     [C4].
3. **The rule engine and its tests.**
   - The engine imports nothing from any simulator.
   - Two kinds of tests, owned centrally:
     - situation → expected decision, shared by all simulators;
     - scene → expected situation, written per simulator against the shared expected situation [C5].
   - Passing means "no fault found by these tests", not "conforms" [C5].
   - Long closed-loop runs compare behaviour against an equivalence standard fixed in advance [C5].
4. **Trained deciders: optional, secondary.**
   - Only small decision trees or rule lists, against an LLM-filled lookup table [C6].
   - The engine stays the reference, and blocks any decision that breaks a hard rule [C6].
   - No reinforcement-learning policies; no language model at run time [C6].
5. **Tests on unseen scenarios.**
   - Scenarios are written as simulator-independent cards, assembled from existing standards [C7].
   - Whole sub-types are held out (queue, vehicle door, capacity), and levels run from L0 to L4.
     PT-2 adds four changes: L0 split; L3 both ways; wording and convention axes; bindings frozen
     too [C7].
   - **Fidelity** to people is scored only where graded evidence exists: queue cutting (pattern
     level), train doors, lift priority. Bus boarding and escalators are scored on **motion**
     only [C7].
   - Every reference behaviour is labelled with its city and year. None is from Singapore [C7].
   - Results are case studies [C7].
   - Results say whether the rules were hand-written seeds or LLM-elicited [C9].
   - Testing against the queue-cutting objection evidence, or against "alighting first", needs
     observer roles and roles by category in the vocabulary first [C10].
6. **Testbeds.**
   - negsim (ORCA, continuous, fixed step);
   - JuPedSim (other motion models, a 0.01 s step), **with our own queue-order layer** [C8];
   - Mesa (discrete, event-driven) as the queue model.
   - SUMO is not needed. CrowdGym is the target **only once its code is available** [C8].

**The example, corrected.** `single_file_first_arrival` becomes: "in a one-at-a-time *passage*, the
claimant with the earliest *predicted* arrival proceeds; the others wait." Applying it to a queue,
where arrival is *recorded* and "wait" means joining the back, is no longer an example of the same
rule. It is an **L3 transfer test**, run on purpose and reported either way [C2, C3].

## What changed from #34, and why

| | Change | Why | Source |
|---|---|---|---|
| **C1** | Claim decision conformance; measure behaviour, do not promise it | Identical rules gave different trajectories; every docking study found differences | PT-1 verdict, change 1, risk 1 |
| **C2** | Scope is the sub-type; crossing sub-types is a logged test | #34's own example crossed passage → queue, a physical → normative boundary | PT-1 F2; PT-2 (transfer within a class) |
| **C3** | Adapted IG 2.0 shape; operational definitions; breach handling and observer roles; arrival order split; seconds | Terms already disagree inside #34 (F4); queue cutting is a breach (F9) | PT-1 changes 2-3, F4, F6, F7, F9 |
| **C4** | Today's rules are **not** the ORCA binding "unchanged": their when-conditions move to the perception translator; an identity check | Those conditions are negsim measurements outside the vocabulary | PT-1 F1, change 2; PT-2 change 4 |
| **C5** | Tests show faults, not conformance; scene tests per simulator; closed-loop runs | Reference tests miss what they do not test; snapshots miss order and timing effects | PT-1 F5, F11, change 4 |
| **C6** | Trained deciders narrowed to small trees vs a lookup table; engine as reference and shield | RL needs a policy per simulator, untested transfer; run-time language models are too slow | PT-4 points 1, 2, 4 |
| **C7** | Protocol changes; fidelity only where evidence exists; borrowed evidence labelled; case studies | Evidence: queue B, doors B/C, lifts B, bus none, escalator weak; no Singapore data; five types | PT-2 verdict; PT-3 verdict |
| **C8** | JuPedSim with our own queue layer, Mesa, no SUMO; CrowdGym conditional | JuPedSim's queue cannot admit part-way; CrowdGym's engine unknown | PT-6 trial 1, recommendation; PT-5 |
| **C9** | **New:** results labelled by rule origin | No LLM-elicited rule exists yet; the paid pilot is held | feasibility S1 `[synthesis]` |
| **C10** | **New:** the vocabulary must reach the evidence | The best queue evidence is about objectors and requests; door evidence needs roles by category | feasibility S2 `[synthesis]`; PT-3 QC-1-8, BA-1 |

**Unchanged from #34:** the four parts of the core vocabulary; the Situation → Decision interface;
the held-out sub-types; human evidence as the reference wherever it exists; the narrow claim "the
same kind of conflict"; `ethnic_group` unreadable by any rule.
