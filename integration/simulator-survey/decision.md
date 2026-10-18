# Use or build: the decision (PT-6, part 2 of 2; issue #40)

## Status

**Everything in this file is a proposal that needs the supervisor's sign-off:**
- **The recommendation:** which simulator plays which role.
- **The weights:** they are the user's and the supervisor's to set. Mine are a starting point,
  and the sensitivity section shows which choices change the answer.
- **The scores:** they are my judgement, from the trials in `hands-on.md` (cited per cell).
- **The idea they serve:** track #34's portable-rule idea is itself unagreed.

**Fit with CrowdGym is conditional.** Whether CrowdGym is built on JuPedSim is unknown. The user
chose to leave `ntu-fyp-25/crowdgym` unopened (`WORK_LOG-40.md` A2), so that question
(`survey.md` §2) stays open.

## The three options

The roles to fill (issue #40):
- **R1:** a second continuous testbed;
- **R2:** a discrete testbed (queue cutting);
- **R3:** a host for boarding scenarios.

negsim stays as it is, as the ORCA testbed, in every option. Changing negsim is out of scope.

| | R1, continuous | R2, discrete | R3, boarding | What we build |
|---|---|---|---|---|
| **(a) Use** | JuPedSim, built-in stages only | Mesa | JuPedSim door, built-in stages | the two adapters per simulator |
| **(b) Refer and build** | negsim with a second motion model, plus queues, service points and vehicles | our own discrete queue model, pure Python | negsim, extended | all of it; JuPedSim, Mesa and Menge as references |
| **(c) Hybrid** | JuPedSim for motion, with **our own queue-order layer** on direct steering | Mesa | JuPedSim door, plus our vehicle timer and counter | the adapters, the queue-order layer (~15 lines in the trial), the vehicle script |

**Why (a) and (c) differ.** (a) uses JuPedSim as shipped. Its queue stage cannot admit anyone
part-way, and keeps people listed after they leave (`hands-on.md`, trial 1). So under (a) queue
cutting can run only in Mesa. (c) keeps JuPedSim for motion but owns the queue order, as the
trial's own-queue route did.

## Criteria and proposed weights

| Criterion | Proposed weight | What a 5 means |
|---|---|---|
| **What the FYP's claim needs**: the same conflict type in testbeds that differ in structure (#34, point 6) | 25 | each unseen conflict type (queue, boarding) runs in ≥2 structurally different testbeds |
| **Effort to build and maintain** | 20 | little new code; nothing to keep in step with upstream |
| **Risk**: defects, API surprises, schedule | 15 | no known defect on the path we would use; no schedule threat |
| **Credibility in a report** | 15 | an examiner recognises the motion and queue mechanics as established, not home-made |
| **Speed at scale** (10,000 agents) | 10 | clearly faster than negsim's 0.062–0.073 simulated s per computing s |
| **Fit with CrowdGym** (conditional) | 10 | adapters likely to carry over to the target |
| **Reproducibility and logging** | 5 | deterministic; logs what a conflict analysis needs |

**Why these weights.**
- **The claim gets the most weight,** because the FYP's question is "the same kind of conflict,
  in any simulator" (#34). A testbed set that cannot run the same conflict twice cannot test that.
- **Effort is next,** because this is one student's FYP.
- **Reproducibility gets little,** because it does not separate the options: all are
  deterministic.

## The matrix

Scores run from 1 to 5.

| Criterion (weight) | (a) Use | (b) Refer and build | (c) Hybrid |
|---|---|---|---|
| Claim (25) | **2**: queue cutting only in Mesa, since JuPedSim's queue cannot admit (trial 1); boarding in JuPedSim and Mesa | **2**: both testbeds ours; a negsim extension shares negsim's code and assumptions, so it differs least from negsim | **5**: queue cutting in JuPedSim (own order layer) and Mesa; boarding in JuPedSim and Mesa; JuPedSim's models differ from ORCA (trials 1, 2) |
| Effort (20) | **4**: least new code; built-in stages | **1**: queues, service, waiting and vehicles in negsim; `architecture.md` §5 keeps queue cutting out of scope | **3**: the order layer was 47 lines including the scene (trial 1); two pinned dependencies |
| Risk (15) | **2**: stale queue entries bite any scenario where someone leaves the line; `target` silently ignored (trial 3) | **2**: no upstream risk, but a large build on the FYP's schedule | **3**: the stale-entry defect is avoided by not using the stage; Mesa churn (`seed=` deprecated, missing `networkx`, weakly held callbacks) contained by pinning |
| Credibility (15) | **4**: established, citable engines | **2**: home-made mechanics an examiner must take on trust | **4**: established motion models; our layer is small and testable |
| Speed (10) | **4**: JuPedSim 2.9–3.4× negsim per simulated second at 10,000; Mesa 15.5 µs per event (trial 4) | **2**: negsim at 0.062–0.073 simulated s per computing s, before any additions | **4**: as (a); the perception pass must run every 0.1 s, not every iteration (trial 4) |
| CrowdGym (10, conditional) | **4** if CrowdGym is on JuPedSim | **2** | **4** if CrowdGym is on JuPedSim |
| Reproducibility (5) | **4**: all deterministic; conflict events we log ourselves | **4** | **4** |
| **Weighted total** | **3.20** | **1.90** | **3.90** |

**How the totals were computed.** Each total is Σ(weight × score) / Σ weights. The scores in
this table are those totals' only input; the computation is repeated in the work log.

## Sensitivity: what would change the answer

| Change | (a) | (b) | (c) | Leader |
|---|---|---|---|---|
| proposed weights | 3.20 | 1.90 | 3.90 | (c) |
| all weights equal | 3.43 | 2.14 | 3.86 | (c) |
| drop effort | 3.00 | 2.12 | 4.12 | (c) |
| drop risk | 3.41 | 1.88 | 4.06 | (c) |
| drop credibility | 3.06 | 1.88 | 3.88 | (c) |
| drop speed, or drop CrowdGym fit | 3.11 | 1.89 | 3.89 | (c) |
| **drop the claim criterion** | **3.60** | 1.87 | **3.53** | **(a), narrowly** |
| raise effort's weight from 20 to 90, others unchanged | 3.53 | 1.53 | 3.53 | tie; below 90, (c) |

**Only one choice changes the answer:** whether the same conflict type must run in two
testbeds.
- **If it must** (the reading of #34 this repository has used), (c) leads under every other
  weighting tried.
- **If one testbed per conflict type is enough,** (a) and (c) are within 0.1 of each other.
- **(b) is last in every row.**

That question is the supervisor's, and it is worth asking directly.

## Recommendation (a proposal; needs sign-off)

**Option (c), hybrid:**

| Role | Proposed | Why | Condition |
|---|---|---|---|
| R1, second continuous testbed | **JuPedSim 1.4.2**, CFS as default, social force as a second motion model | different motion model and step (0.01 s) from negsim; both adapter hooks work; deterministic; 10,000 agents 2.9–3.4× faster than negsim (trials 3, 4) | pin the version; do not use `NotifiableQueueStage` where the order can change |
| R2, discrete testbed | **Mesa 3.5.1**, with `networkx==3.7` pinned | discrete events; order and time waited are first-class; seeded; admit and refuse are one decision point (trial 1) | keep the queue logic framework-light (lists + `schedule_event`), so that moving to pure Python stays cheap if Mesa's API churns |
| R3, boarding host | **JuPedSim**, with a scripted vehicle (arrival spawn, release, capacity counter) | waiting, release and two-way door flow work; the cost of the conflict emerges from motion (trial 2) | add the discrete door in Mesa as the second testbed for the same conflict |
| Not now | **SUMO** | the door conflict needs no vehicle model (trial 2) | revisit only for network-level boarding (timetables, several vehicles) |
| Not now | **Vadere, Menge** | outside #40's permission; desk evidence only (`shortlist.md`) | Vadere if the supervisor wants a continuous testbed that also differs in time |

**Rules the adapters must follow,** whichever option is chosen (from the trials):
1. **Know each agent's journey type** before setting a target. In JuPedSim, a target outside
   direct steering is dropped silently (trial 3). Log a decision as applied only when it took
   effect.
2. **Sample perception every 0.1 s, not every 0.01 s iteration.** A full Python read costs as
   much as an iteration at 10,000 agents (trial 4).
3. **Store queue places; never search for them.** Searching made a Mesa step 7.5× slower at
   10,000 (trial 4).
4. **Compare runs by spawn order, not by id.** JuPedSim's ids are process-wide (determinism
   section).
5. **Write the conflict-event log ourselves**, in both simulators. Neither records decisions
   (logging section). Close JuPedSim's writer, or short runs are lost.

## What this decision does not settle

- **Whether CrowdGym is built on JuPedSim** (A2). The CrowdGym row is scored as if it is. If it
  is not, (a) and (c) each lose 0.2, and the order stays the same.
- **Whether the JuPedSim models are realistic for Singapore crowds.** No calibration was done.
  Every number in `hands-on.md` is a model property.
- **The adapter and rule-engine design.** Those are later issues (#41, #42).
