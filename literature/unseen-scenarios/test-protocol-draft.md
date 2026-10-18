# Q5. A draft protocol for testing rules on unseen scenarios

> For issue [#36](https://github.com/M450NCH00/CrowdSimulation/issues/36) (PT-2).
> **Status: a draft built from the literature, for discussion. Not agreed; it needs the supervisor's
> sign-off**, like the portable-rules idea (#34) it serves. Nothing here has been run.
>
> **How to read it.** Every level, metric and card field either cites an entry, as
> `[Handle]` from `methods.md` or `scenario-standards.md`, or is marked **(proposal)**. A proposal
> is my design suggestion with no source behind it. Where the issue's starting proposal is
> changed, the change and its reason are stated under **Change**.

## 0. What the protocol is for

The claim to test is #34's: "the same kind of conflict, in any simulator", not "any conflict". The
literature supports that framing. Humans do carry a convention to a differently structured game,
but every positive case stays within one class of games
([CooperVanHuyck-Transfer] §4, p. 24; [CooperKagel-Signaling] §VII). Transfer is also directional
([Cason-Spillovers] §7) and can be harmful ([CooperVanHuyck-Transfer] §1, p. 7). So the protocol
has to measure **how far** a rule carries, in **which direction**, and whether it **stops** where
it should.

Three things are tested separately, because the sources test them separately:
1. **the decision**: does the rule core pick the outcome people pick? (human reference: PT-3);
2. **the perception**: does the simulator's adapter recognise the conflict type correctly? This
   is separate because people bundle situations they cannot tell apart, and get them wrong
   ([Huck-FeedbackSpillover] §7; [GrimmMengel-MultipleGames] §4);
3. **the outcome in motion**: does the crowd clear without deadlock or collision when the rule
   runs in a simulator? ([SteerBench-2009] metrics).

## 1. Transfer levels

| Level | Issue's definition | Kept / changed | Source for the level |
|---|---|---|---|
| **L0** | new seeds and people | **Kept, split in two** (see Change 1) | [MeltingPot-1] §§1, 4.2; [IMO-Circ1533] App. 3 |
| **L1** | new parameters | Kept | [RiMEA-4.1.1] Test 12d (width varied 0.8-1.2 m, p. 41); [Tordeux-ANN] Table 1 |
| **L2** | a new layout, same conflict type | Kept; the layout change must be described | [Zhang-DFD-OOD] §5.1; [Tordeux-ANN] §5 |
| **L3** | a new conflict type whose features are in the vocabulary | Kept; **run both directions where possible** (Change 2) | [CooperVanHuyck-Transfer]; [Cason-Spillovers]; [CooperKagel-Signaling] |
| **L4** | a conflict type outside the vocabulary; the right outcome is to abstain | Kept as a **(proposal)**: no source tests abstention | none found; see §6, open question U1 |

Two axes are added, **orthogonal to the levels** (Change 3):

| Axis | Values | Source |
|---|---|---|
| **W: wording** | the scenario as usually described; reworded/renamed; minimally perturbed (one fact changed) | [Aher-TuringExperiments] §8, App. F; [Binz-CogPsychGPT3]; [CooperKagel-Signaling] §VII, p. 21 |
| **C: convention** | default world; counterfactual world with the changed convention stated | [Wu-Counterfactual] §§2, 2.1 |

W and C matter at the **rule-extraction** stage (the LLM sees text) and when PT-3's human evidence
is compared with LLM answers. They do not apply to a frozen rule running in a simulator, where
wording no longer exists.

**Change 1: split L0.**
- **L0a**, new seeds: the same population drawn again. Sample size from [IMO-Circ1533] Appendix
  3, paras 1-2: "a minimum of 50 different simulations ... at least 10 different randomly
  generated populations ... repeated at least 5 times". Or use TN 1822's convergence method to
  choose the number of runs ([Ronchi-TN1822] §4.1.3).
- **L0b**, new co-players: the rule-following agents mixed with others who follow a different or
  established norm, in Melting Pot's **visitor** and **resident** modes ([MeltingPot-1] §4.2).
- *Why:* Melting Pot's main finding is that agents fail on unfamiliar co-players on a familiar
  map ([MeltingPot-1] §7; [MeltingPot-2] p. 12). "New people" is not one thing. For queue cutting
  in particular, the realistic test is one newcomer among people who already keep a queue norm,
  which is visitor mode.

**Change 2: test L3 in both directions where the data allow.**
- Transfer from median to minimum games was positive, but not from minimum to median
  ([Cason-Spillovers] §7, p. 22).
- Tordeux et al. report R/B and B/R separately ([Tordeux-ANN] §5, p. 6).
- A single direction can make a rule look portable when it is not. **(proposal)** report a 2 × 2
  for every pair of conflict types where rules exist on both sides.

**Change 3: add W and C.**
- The LLM may know the familiar version of a scenario ([Wu-Counterfactual] §2;
  [Binz-CogPsychGPT3], vignette section).
- Renaming a scenario tests wording, not a new conflict type. Aher et al. concede that their
  "novel" obedience scenario was "at its core ... reminiscent of Milgram's"
  ([Aher-TuringExperiments] App. F).
- So **a reworded familiar conflict counts as W, never as L3**.

## 2. Hold-out design

- **Whole conflict types are held out** (the issue's proposal; kept). This is **stricter than
  Melting Pot**, which holds out partners but never worlds ("Policies are not transferable between
  substrates", [MeltingPot-1] §4.1; "mainly along social dimensions, not physical dimensions",
  [MeltingPot-2] p. 4). No source I found holds out a whole conflict type for a behaviour rule.
  The design is therefore **(proposal)**, justified by the transfer evidence in §0.
- **First fold (proposal).**
  - Today's rules come from negsim's encounter classes `head_on`, `crossing`, `overtaking` and
    `single_file_segment` (`llm_negotiation/docs/rule-format.md`, rule fields table).
  - In #34's draft vocabulary these fall under `passing_room` and `exclusive_access.passage`.
  - Held out: `exclusive_access.queue` (queue cutting), `exclusive_access.vehicle_door` (bus and
    MRT boarding against alighting: `bus_queue_boarding`, `mrt_door_alight_board` in
    `dataset/scenarios.yaml`), and `capacity` (`lift_boarding_capacity`).
  - Queue cutting is **not** among the 14 scenario ids in `dataset/scenarios.yaml`, so it needs a
    new card.
- **Later folds (proposal):** if rules are later extracted for a held-out type, rotate
  (leave-one-type-out) and fill in the 2 × 2s of Change 2.
- **L4 candidate (proposal):** `signalised_crossing` from `dataset/scenarios.yaml`. It is governed
  by an external signal and involves vehicles, and #34's draft vocabulary has neither. Whether it
  really falls outside the vocabulary is for PT-8 to decide.

## 3. Freezing

| What is frozen | When | Source |
|---|---|---|
| Rule cores, their versions, and the vocabulary version | before any held-out scenario is run | [MeltingPot-2] p. 4 ("do not cheat by training ... on the test set"); [Wolinski-ParamEst] §5 (per-scenario fitting says nothing about the next scenario) |
| Bindings and adapter parameters (the "how much") | same | [Tordeux-ANN] Table 1 (parameters shift with geometry, so re-tuning on the test layout would hide a failure); [RiMEA-4.1.1] A2, p. 26 |
| Pass criteria and acceptance bands per card | before the run | [RiMEA-4.1.1] Test 1 (stated band, p. 29); [Ronchi-TN1822] §4.1.3 step 1 ("define the acceptance criteria" first); [IMO-Circ1533] App. 2 (expected results stated in each test) |
| The list of patterns expected, **including those expected to fail** | before the run; failures reported | [ODD-2020] §4, "Linking ODD to pattern-oriented modelling" (report patterns "consistently failed to reproduce", to avoid HARKing) |
| Mechanism **(proposal)** | | record the git commit hash of the rule database, adapters and cards in each run's log; any change after a held-out run starts a new, labelled version |

## 4. Comparisons: baselines

| Baseline | Role | Source |
|---|---|---|
| **No rule**: the simulator's default avoidance only (ORCA in negsim) | floor | [MeltingPot-1] §7 (random agent as lower bound) |
| **A simple stated convention**, e.g. first-come-first-served everywhere, or "alighting before boarding" | literature reference point | [Zhang-DFD-OOD] (Wang et al.'s handcrafted model used as a reference point, summary §6) |
| **The LLM deciding directly** in the held-out scenario (no extracted rule) | tests whether extraction lost or gained anything; leakage-exposed (§5) | (proposal); compare [Zhang-DFD-OOD], where distilled functions are scored against the LLM ground truth |
| **A rule extracted from the held-out type itself** (an "exploiter") | ceiling: how good a rule *for that type* can be | [MeltingPot-1] §7 (exploiter trained on the test scenario as upper bound) |
| **Trained deciders** behind the same Situation → Decision interface (PT-4) | alternative portable decider | #34 point 4; (proposal) to run them on the same cards |

The exploiter needs care. Melting Pot found it is not always the best ([MeltingPot-1] §7;
[MeltingPot-2] p. 11). **(proposal)** Report raw scores next to any normalised score, because
normalisation once made agents that "actually" never cooperated look good ([MeltingPot-2] p. 11).

## 5. Metrics

| Metric | What it measures | Source |
|---|---|---|
| **Decision agreement with the human reference**: who proceeds, who waits or joins the back, per situation | the decision (test 1 in §0) | reference from PT-3; form from [Aher-TuringExperiments] and Cross et al. 2025 (g6 §2): agent outputs against human results for the same stimuli |
| **Type-recognition accuracy** of the perception adapter on held-out scenes | the perception (test 2) | [Huck-FeedbackSpillover] §7; [GrimmMengel-MultipleGames] §3, p. 14 (people treat strategically equivalent games alike); #34 point 3 (scene → Situation conformance tests) |
| **Abstention rate at L4**, and **false-confidence rate** (a decision issued where it should abstain) | stopping where it should | **(proposal)**; no source found (U1) |
| **Collisions, time efficiency, effort efficiency** per agent; pass/fail per card | outcome in motion (test 3) | [SteerBench-2009] "Metrics of Evaluation" (three primary metrics), computed only from logged trajectories |
| **Deadlock rate and time to clear** | outcome in motion | [SteerBench-2009] "Test Case Design Choices" (deadlock avoidance) as the case; the measure itself is (proposal) |
| **Effect on others** (background agents' outcome) and **inequality** of outcomes | side effects, e.g. a rule that is efficient but unfair to a persona group | [MeltingPot-1] §4.4 (background-population return; inequality) |
| **Transfer gap** = in-type score − held-out score, reported per direction | how far the rule carries | [Tordeux-ANN] §5; [Cason-Spillovers] §7 |
| **Default − counterfactual gap** (axis C) and **canonical − perturbed gap** (axis W), for the LLM stage | leakage signal | [Wu-Counterfactual] §4; [Binz-CogPsychGPT3] Fig. 1 |
| **Spread across populations and seeds**; number of runs to convergence | behavioural uncertainty | [IMO-Circ1533] App. 3; [Ronchi-TN1822] §4 |

## 6. The scenario card

A card describes **one test scenario** independently of any simulator. It is **not** a rule and
**not** a model description: ODD's authors keep experiments separate from models because "the same
experiments are sometimes executed using different models" ([ODD-2020] §5). That is the card's job
here.

| Field | Content | Borrowed from |
|---|---|---|
| `id`, `version` | stable name, version | (proposal) |
| `context_of_use` | what the scenario is for, and where it should **not** be reused | [Ronchi-TN1822] Abstract and §2.1 (IMO tests misused outside the maritime context); [ISO-20414] public abstract (scope excludes trains, ships in motion) |
| `background`, `aim` | why the scenario exists; what behaviour it probes | [RiMEA-4.1.1] Test 12a, 12d, 16 (Background / Aim / Setup) |
| `patterns` | observed human patterns the rule should reproduce, **and those it is expected to miss** | [ODD-2020] element 1 and §4 |
| `conflict_type`, `level`, `held_out` | from the vocabulary; L0-L4; whether held out in the current fold | #34 point 1; levels and hold-out as above (proposal) |
| `geometry` | polygons and named zones (door, platform edge, queue area, lift car) | [RiMEA-4.1.1] §3.1; [IMO-Circ1533] App. 1 §2.2; [Ronchi-TN1822] §3.0 "Geometry" |
| `journeys` | the stages people pass through: waypoint, queue, waiting area, service point or door, exit | [JuPedSim-1.4.2] journeys and stages; `service point` and joining part-way are additions (proposal) |
| `population` | persona mix by age band, gender, mobility aid (Singapore personas) | [IMO-Circ1533] App. 1, Table 3.1; [RiMEA-4.1.1] §3.2; `dataset/personas.yaml` |
| `roles` | who is a newcomer, who is alighting, who is in the lift | [MeltingPot-2] p. 5 (roles set observation and action spaces); #34 point 1 |
| `agents` | start position, heading, desired speed, goal per agent or per group | [SteerBench-2009] "Overview of SteerBench" |
| `initial_state` | everything at t = 0, with **no conditional logic** | [OpenSCENARIO-1.4] §7.2.1 (Init) |
| `events` | actions started by triggers (door opens when the bus stops; a newcomer arrives at t = 20 s and heads for the middle of the queue) | [OpenSCENARIO-1.4] §§7.2.1, 7.6 |
| `stop_condition` | when the run ends | [OpenSCENARIO-1.4] §7.2.1 (stopTrigger) |
| `background_norm` | what the non-tested agents do, and whether the tested agents are visitors or residents | [MeltingPot-1] §4.2 |
| `communication` | whether talk is allowed, and what it may reveal | (proposal); none of the eight formats has it (`scenario-standards.md`, comparison table) |
| `wording_variants` | canonical / reworded / perturbed / counterfactual text for the LLM stage | [Aher-TuringExperiments] §8; [Binz-CogPsychGPT3]; [Wu-Counterfactual] §2 |
| `expected_result`, `acceptance_band`, `reference_evidence` | what should happen, with what tolerance, and from which human source | [Ronchi-TN1822] §3.0 (expected result); [RiMEA-4.1.1] Test 1 (band), Test 16 (empirical percentiles) |
| `test_method`, `metrics` | how the result is judged; all metrics computed from logged trajectories and decisions | [Ronchi-TN1822] §3.0 (test method); [SteerBench-2009] (algorithm-blind evaluation) |
| `repetitions` | populations × seeds | [IMO-Circ1533] App. 3 |
| `required_capabilities` | what a simulator must support to run the card (queues, triggers, doors); a simulator that lacks one must say so, not silently skip | [OpenSCENARIO-1.4] §7.2.2.7 (optional features "may be ignored, depending on the simulator's support") (the "must say so" part is a proposal) |

## 7. What this protocol cannot do

- **It cannot prove the LLM did not know the answer.** It can only grade the evidence
  ([Wu-Counterfactual] §2; g5 §4). The claim stays at g5 §4's level: the extracted rules are
  tested, not the LLM's understanding.
- **Its reference for held-out conflict types depends on PT-3.** Without human evidence for queue
  cutting, boarding and lifts, L3 can only be scored on motion metrics, which say a rule *works*,
  not that it is *what people do*.
- **L4 has no literature behind it** (U1). Whether "abstain" is even the right target may depend
  on what the simulator does when no rule applies, which is for PT-8.
