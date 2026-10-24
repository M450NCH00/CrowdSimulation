# Architecture

What the pieces are, how a run flows through them, and which choices were this project's
own. Decisions are numbered **DD** and marked as decisions: they are not facts taken from
the paper or the issue, and each needs the supervisor's sign-off. Assumptions are numbered
**A**.

Sections 1 to 5 describe the negotiation simulator of issue #24. Section 6 describes the
avoidance layer added by issue #26, which sits beside it: ORCA, perception, directives,
and the handoff to the arbiter. Section 7 describes the rule layer of issue #28: the rule
format, the rule database, the matching policy, and the frozen baselines. Section 8
describes rule generation of issue #30: conflict cases, the design matrix, the two
protocols, validation, the writer and its staging databases, replay and screening; its
subsection 8.6 records the supervisor's direction of 2026-10-20 (numbered **SV**), under which
those protocols no longer generate rules, and its subsection 8.7 the user's resolution design of
2026-10-22 (numbered **D**, as in `resolution.md`), which needs no sign-off. Section 9
describes issue #32: a fictional group that no rule may read, and two people who meet inside a
single-file passage, with the `back_up` directive and rule format 3.

## 1. The pieces

```
run_experiment.py            command line: load a config, pick a client, run, report

negsim/
  experiment/   config.py    experiment YAML -> list of RunPlan (the design, counterbalanced)
                runner.py    one RunPlan -> one simulation -> one log folder
                batch.py     all the runs of an experiment, the client, summary.csv
                avoidance.py avoidance experiments (issue #26): config, design, run, summary
                cli.py       what run_experiment.py calls
  scenarios/                 scenario YAML -> ScenarioSpec (agents, walls, paths, region)
                             doorway, intersection, hallway; a base class; a registry
                             crowd_base.py and five avoidance scenarios (issue #26)
  core/                      Pose, Control, dynamics models, AgentSpec, World, geometry
  conflict/                  conflict zone, detection, time to the region, who leads
  control/                   controller interface, path tracker, Strategy 1 speed bound
  avoidance/                 the ORCA layer (issue #26): section 6
  rules/                     the rule format, database, matching policy and provider (issue #28): section 7
  negotiation/               prompt templates, persona rendering, situation report,
                             turn parsing, consensus, the dialogue protocol
  personas/                  persona schema and YAML loader
  llm/                       client interface, DeepSeek client, mock client,
                             price table, spend ledger, budget guard
  metrics/                   makespan, minimum speed, path deviation, deadlock, ground truth
                             avoidance.py: yield events, near misses, collisions (issue #26)
  runlog/                    log schema, writers, the schema check
  viz/                       transcript renderer, trajectory plot, animated viewer

configs/   scenarios/  personas/  experiments/  avoidance/  baselines/  rule_following/  tasks/  llm/
rule_db/   schema/  rules/  rulesets/  MANIFEST.json            (issue #28)
tests/     runs/       docs/       LICENSES/
```

Dependencies point one way: `core` knows nothing else; `conflict` and `control` build on
`core`; `scenarios` builds on those; `llm` and `personas` stand alone; `negotiation` uses
`llm`, `personas` and `scenarios`; `experiment` ties everything together. Nothing imports
from `pipeline/` or `dataset/`, and a test checks that
(`test_repo_hygiene.py::test_phase_1_code_is_not_imported`). `avoidance` builds on `core`,
on `conflict` and `control` (for the arbiter) and on `personas` (for which attributes
exist). It imports neither `llm` nor `negotiation`, and a test checks that too
(`test_avoidance_runs.py::test_the_avoidance_layer_does_not_import_the_llm_package`).

Additions to the layout issue #24 suggested, and why: `negsim/experiment/`, because the
run loop has to be importable for the tests and `run_experiment.py` should stay thin;
`negsim/configutil.py`, the one place configs are read and validated;
`configs/tasks/` and `configs/llm/`, because GameChat's task strings and DeepSeek's prices
are data with a source, not code.

The simulator, both clients and the logging use only the Python standard library. PyYAML
reads the configs; matplotlib is needed only for the optional plot.

## 2. One run, step by step

```
            experiment YAML ──> RunPlan
                                   │
       scenario YAML ──> ScenarioSpec ──> World (two agents, walls, clock)
                                   │
   every time step:                ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │ 1 NEGOTIATION   can the agents see each other?  -> the dialogue starts │
   │      per turn:  world ──observe──> situation report (switchable lines) │
   │                 persona + template ──> system prompt (fixed per agent) │
   │                 prompt ──LLM client──> raw reply ──parse──> message,   │
   │                                                             stance     │
   │                 two complementary stances in a row ──> agreed leader   │
   │                                                                        │
   │ 2 ARBITRATION   detector: predicted paths ──> conflict zone            │
   │                 would both be in it at once?  -> a conflict is live    │
   │                 leader = agreed leader, if it can still be honoured;   │
   │                          otherwise Strategy 1 (shorter time to zone)   │
   │                 follower's speed bound = d_i v_j / (d_j + L + l_j)     │
   │                                                                        │
   │ 3 MOTION        controller(agent, speed bound) ──> (v, omega)          │
   │                 world.step: every agent moves from the same instant    │
   │                                                                        │
   │ 4 BOOKKEEPING   region entries, goals, collisions, deadlock            │
   └────────────────────────────────────────────────────────────────────────┘
                                   │
   config.json   conversation.jsonl   trajectory.csv   outcome.json   transcript.md
```

The dialogue produces one thing the motion uses: which agent leads. Everything else about
the motion is deterministic. That is GameChat's architecture (`gamechat-notes.md`), and it
is what makes the conversation logs usable for rule extraction: the mapping from
"what was said" to "what happened" is a single, recorded bit.

## 3. Design decisions

### Simulator

**DD1. Controller: one interface, a path-tracking backend, no MPC-CBF.**
A controller is a class with `compute(agent, speed_bound, world) -> Control`, registered
under a name and chosen per scenario (`controller.backend`). Conflict resolution reaches it
only as an upper bound on speed, which is how the paper describes enforcing the follower's
slowdown. The one backend, `path_tracking`, steers at a point a fixed distance ahead on
the agent's desired path and drives at exactly the bound.

The paper's MPC with control-barrier-function constraints is **not implemented**. The
issue allowed that if it could not be done cleanly. Reasons: it would add CasADi, do-mpc
and Ipopt, none of which is installed here; its tuning in the repository differs between
the two scenarios (two sets of cost weights, one commented out, `config.py:58-69`); and
with the speed rule active the repository's MPC does not treat the other agent as an
obstacle at all (`gamechat-notes.md`, D14), so for the two-agent question studied here it
adds obstacle avoidance and nothing else. *Follow-up if wanted:* a backend
`mpc_cbf` implementing the same `compute`, with the speed bound as the upper limit of the
velocity constraint, its packages in a separate optional requirements file. Asking for
`backend: mpc_cbf` today fails with a message pointing here.

**DD2. Conflict detection has two predictors.** `heading_ray` casts a ray along each
agent's heading, as GameChat does, and is used for the doorway and the intersection.
`desired_path` uses the agents' desired paths and is used for the hallway, where two
agents meeting head-on have collinear rays that never "intersect". Both produce the same
thing, a conflict zone on each agent's path.

**DD3. The conflict zone is computed, and is long enough to be safe.** By default a zone
is the stretch of an agent's path within `r_i + r_j + safety_margin` of the other's
(`derivations.md`, section 4), which guarantees that two agents obeying the speed rule
never touch, whatever their sizes and speeds. The paper's point model does not give that
guarantee for discs, and the repository's fixed 0.25 m does not give it at shallow angles
(`derivations.md`, section 5). The replication experiments (C0 and C1 in the doorway)
nevertheless set the zone half-length to the repository's 0.25 m, so that their timings
can be compared with the paper's; that is safe for those agents and is tested.

**DD4. Exact ties are broken by agent index.** Symmetric starts tie exactly in a
deterministic simulator. The lower index leads, and the experiment design swaps which
participant is agent 0 to balance it. A seeded random tie-break is available
(`arbitration.tie_break: random`).

**DD5. An agreement is honoured only while it can be, and only when it matters.** If the
agent that agreed to follow is already inside the conflict zone when the agreement is
reached (possible in `concurrent` mode), it carries on, and the run records
`negotiated_roles_not_feasible`. If the two agents would not be in the zone at the same
time anyway, nobody slows down, whatever was agreed.

**DD6. Collision and deadlock are defined physically.** A collision is two discs
overlapping, or a disc overlapping a wall; the run stops there. A deadlock is every
unfinished agent below 0.01 m/s for 3 s. Both are stricter readings of the paper than the
repository's (`gamechat-notes.md`, D11, D12).

**DD7. The hallway.** Each agent keeps to its own right in the waiting areas and joins
the centre line just before the hallway mouth, so that a waiting follower stands beside
the leader's way out, not in it. The layout is symmetric under a half turn.

**A1. The hallway's sizes and speeds are placeholders.** Body radius 0.25 m, maximum speed
1.3 m/s, hallway 0.8 m by 4 m: round, plausible, human-scale values chosen so that
personas are not told they walk at a robot's 0.3 m/s. They are **not sourced**. Replace
them before reporting an experiment (`WORK_LOG-24.md`, Q3).

**A2. Agents are already walking when they first see each other.** An agent's "current
speed" before the first step is its maximum speed, not zero. Otherwise the first situation
report would say everyone is standing still.

**DD8. Sight is not blocked by walls, by default.** GameChat does not model occlusion,
and with it the agents at the intersection would not see each other until they were at
the corner. `observation.walls_block_sight: true` turns it on; `observation.max_range`
limits how far an agent can see. Both the dialogue's start and conflict detection wait
for mutual sight.

### Negotiation

**DD9. Turn format and consensus** are as issue #24 specifies: JSON with `message` and
`stance`; consensus is complementary stances on consecutive turns; one retry on malformed
output, then `UNDECIDED`. What is tolerated when reading a reply is deliberately little
(`log-schema.md`). The departure from GameChat is discussed in `gamechat-notes.md`,
section 5.

**DD10. A failed turn is silence.** After two unreadable replies the turn's message is
empty and the other agent is told that no intelligible reply came. The dialogue goes on.

**DD11. Timing.** `pre_conflict` (the default): the whole dialogue takes place at the
instant the agents first see each other, with the clock stopped. `concurrent`: one message
every `seconds_per_message` of simulated time (default 1.0 s), the agents moving under
Strategy 1 until they agree. The interval is configured, not measured, so that a run does
not depend on the network. If one agent is already through the zone when the next message
is due, the dialogue stops (`conflict_over`).

**DD12. Prompt templates are frozen files.** All wording an agent sees, including the
situation-report lines, is in one YAML file per template version, whose SHA-256 is pinned
in `templates/MANIFEST.json` and checked on every load. Changing a word means a new
version file, a new manifest entry and a note in the work log;
`python -m negsim.negotiation.freeze <key> "<reason>"` adds the entry. Two templates
exist: `gamechat_task_v1` (the paper's prompt) and `persona_v1`.

**DD13. What `persona_v1` says and does not say.** It tells the agent who it is, what the
scene is, what it can see of the other person, and how to reply. It does not say how the
question should be settled: nothing about courtesy, urgency, age or precedence. It does
not tell the agents how many messages they have, or what happens if they do not agree;
GameChat's prompt does not either. The format example uses placeholders, not a real
stance, so as not to suggest one.

**DD14. What an agent may know about the other.** By default: approximate age ("They look
about 70 years old"), gender, current speed, body width, and position. Not the task or the
backstory, which can only be learned by talking. Never, under any setting, the other
agent's maximum speed, goal, path or assigned role. `situation.py` has the table.

**A3. The four shipped personas** (ages 25 and 70, female and male, one errand) are
placeholders that exercise the platform. Issue #24 does not say which ages or tasks the
study should use.

**DD15. No location in the persona prompt.** Phase 1 was Singapore-only. Issue #24 lists
age, gender, backstory and task, so `persona_v1` says nothing about where the scene is. A
location can be added as a persona attribute, or through `backstory`, in a new template
version (`WORK_LOG-24.md`, Q4).

### Experiments

**DD16. The design is explicit about its confounds.** `first_speaker`, `assignment`
(which participant is agent 0) and `sides` (which side agent 0 starts on) are separate
factors, each of which can be fixed, flipped or counterbalanced, and each of which is
recorded in every run. Agent index matters because of DD4; speaking order may matter
because the first speaker frames the exchange.

**DD17. Ground truth is refused where there is none.** `scoring.ground_truth` is accepted
only for conditions C0 and C1, only for agents without personas, and only for two
different task types. A persona run has no field that marks its outcome right or wrong.

**DD18. Paying is opt-in, twice.** Every shipped config names the mock client; a paid run
needs `--client deepseek` on the command line. Mock runs are written to `runs_mock/`,
which git ignores, so a rehearsal can neither be mistaken for a result nor make a paid run
look already done.

**DD19. Runs are resumable.** A run whose folder holds a finished outcome is skipped, so
an experiment interrupted by the budget guard or a network failure can be continued
without paying twice. An aborted run is redone.

### LLM

**DD20. DeepSeek settings**: `deepseek-flash`, thinking off, temperature 1.0,
`max_tokens` 300, standard-library HTTP client. See `llm-backend.md`, section 2.

**DD21. The budget guard refuses on the worst case.** See `llm-backend.md`, section 5.

## 4. Ready for more than two agents, but not built for them

`World` holds any number of agents and steps them together. `Arbiter.resolve` loops over
all pairs and gives each agent the tightest bound from any conflict it is the follower in
(`test_conflict.py::test_arbiter_handles_three_agents_pairwise`). What is missing for
three or more: a consistent ordering (pairwise roles can form a cycle in which everybody
waits), a dialogue among more than two, and scenarios. The experiment runner checks that
there are exactly two agents. Issue #24 puts the rest out of scope.

## 5. What is not here

- The MPC-CBF controller (DD1).
- Rule extraction from the logs, and its validation against the literature.
- Race, pseudo-race or fictional-race personas. The persona schema is a table of
  attributes (`negsim/personas/schema.py`), so adding one is a table entry and a template
  line, with no change to the loader, the visibility settings or the renderer (tested in
  `test_personas_and_prompts.py`, "the schema is a table").
- Queue-cutting, non-spatial conflicts, CrowdGym integration, scaling.

## 6. The avoidance layer (issue #26)

The simulator of sections 1 to 5 settles a conflict in one way: it decides who goes first.
A rule taken from it could only ever prescribe priority. This layer adds the other half:
agents that step out of each other's way, under directives that say how. It is the first
of six sub-issues; it contains no rule, no rule database and no call to a model.

It is a second kind of run, beside the first. A negotiation run and an avoidance run have
different scenarios, different experiment configs and different log files, and share the
core, the arbiter, the personas and the logging conventions.

### 6.1 Where each piece lives

| Piece | Module | What it is |
|---|---|---|
| ORCA half-planes | `negsim/avoidance/orca.py` | `agent_half_plane`: the velocities one agent may choose because of one neighbour, with a share and an optional side. `wall_half_plane`: the same for a wall block. From the paper (`orca.md`). |
| Linear programs | `negsim/avoidance/lp.py` | `solve`: the allowed velocity nearest the preferred one, and the fallback when there is none. Adapted from RVO2, with its notice. |
| Neighbour search | `negsim/avoidance/neighbours.py` | `SpatialGrid`: the nearest `k` agents within a radius, and all pairs within a distance. |
| Perception | `negsim/avoidance/perception.py` | `PerceptionRecord`, versioned; `perceive` builds one; the visibility rules (`perception.md`). |
| Directives | `negsim/avoidance/directives.py` | `AvoidanceDirective`; `resolve_pair`, which combines the two directives of a pair and reports a `ReciprocityViolation`; the `DirectiveProvider` interface with `NullProvider` and `StaticProvider`. |
| Layer coordination | `negsim/avoidance/coordination.py` | `SingleFileDetector`, a detector for the arbiter of issue #24; `Coordinator`, which decides which pairs the arbiter holds and logs each `Handoff`. |
| The run loop | `negsim/avoidance/simulation.py` | `AvoidanceSimulation`: one step for every agent, the interactions, the bookkeeping. |
| Benchmark | `negsim/avoidance/benchmark.py` | Milliseconds per step for a crowd of a given size. |
| Viewer | `negsim/viz/viewer.py`, `negsim/viz/viewer.html` | An animated, interactive view of run folders of either kind, as one self-contained HTML file. Reads only the logs. Added on request after the PR for issue #26 was opened. |
| Dynamics | `negsim/core/dynamics.py` | `DynamicsModel`, with `UnicycleDynamics` (issue #24) and `HolonomicDynamics` (ORCA). `World` takes one. |
| Metrics | `negsim/metrics/avoidance.py` | Yield events, near misses, collision episodes (`metrics.md`). Exposure is counted in the run loop, where the half-planes are. |
| Scenarios | `negsim/scenarios/crowd_base.py` and one module per scenario | `CrowdScenario`, `CrowdScenarioSpec`, `AgentType`; `wide_corridor_head_on`, `open_crossing`, `overtaking`, `corridor_to_bottleneck`, `bidirectional_flow`. Configs in `configs/scenarios/`, `schema_version: 2`. |
| Experiments | `negsim/experiment/avoidance.py` | `AvoidanceExperiment`: a config with `layer: avoidance`, expanded into runs; one run; a whole experiment. Configs in `configs/avoidance/`. |
| Logs | `negsim/runlog/schema.py`, `writer.py` | Log schema version 2: `run_kind`, the files and fields of an avoidance run, `AvoidanceRunLogger` (`log-schema.md`). |

### 6.2 One step

```
   every time step, for every agent that has not arrived, all from the same state:
   ┌──────────────────────────────────────────────────────────────────────────────┐
   │ 1 PERCEIVE     neighbours = nearest max_neighbours agents within R            │
   │                a new neighbour starts an interaction:                         │
   │                   world ──perceive──> PerceptionRecord                        │
   │                   record ──DirectiveProvider──> AvoidanceDirective            │
   │                                                                              │
   │ 2 RESOLVE      two agents that perceive each other:                           │
   │                   their two directives ──resolve_pair──> shares, side,        │
   │                   clearance, leader   (a contradiction is logged and repaired) │
   │                                                                              │
   │ 3 COORDINATE   a pair with a single-file segment ahead of both, and in each   │
   │                other's way there ──> the arbiter: leader, follower's bound    │
   │                                                                              │
   │ 4 CHOOSE       preferred velocity = along the path, at preferred speed        │
   │                   x speed_scale, capped by the arbiter's bound                │
   │                one half-plane per wall in reach (hard)                        │
   │                one half-plane per neighbour (share, side, clearance)          │
   │                linear program ──> the allowed velocity nearest the preferred  │
   │                   none allowed? ──> the fallback (counted)                    │
   │                                                                              │
   │ 5 MOVE         velocity ──DynamicsModel──> new position, velocity realised    │
   │                                                                              │
   │ 6 BOOKKEEPING  arrivals, collisions, near misses, yields, exposure, deadlock  │
   └──────────────────────────────────────────────────────────────────────────────┘
        config.json   trajectory.csv   interactions.jsonl   events.jsonl   outcome.json
```

### 6.3 Design decisions

**DD22. A second kind of run beside the first; nothing existing changes.** Avoidance
scenarios have their own config schema (`schema_version: 2`) and builder, avoidance
experiments their own config (`layer: avoidance`), loader and folder (`configs/avoidance/`),
and avoidance runs their own files. No existing scenario or experiment config was edited,
and none is read differently. *Checked:* the 432 tests of issue #24 pass unchanged, and
the 54 committed no-LLM runs of issue #24, run again with this code, come out identical
(`WORK_LOG-26.md`).

**DD23. Dynamics are pluggable; the avoidance layer is holonomic.** `World` takes a
`DynamicsModel`, which turns one agent's command into its motion and reports the velocity
actually realised. The default is the unicycle of issue #24, whose command is `(v, omega)`;
the avoidance scenarios use the holonomic model, whose command is a velocity vector, as
ORCA assumes. The layer hands a velocity to the model and reads back what was realised,
which is what neighbours then observe; it does not know which model it is. A vehicle model
would take the same command and realise the nearest motion it can. Nothing in
`negsim/avoidance/` would change for it, though ORCA's guarantee would then need the
tracking error accounted for. That, non-holonomic ORCA, is out of scope, and a scenario
that asks for any other model is refused for now.
*Tested:* `test_another_dynamics_model_can_be_plugged_in_without_touching_the_layer`.

**DD24. ORCA is written from the paper; the linear programs are adapted from RVO2.**
`orca.md`, section 2. RVO2 was read, not run, and is not a dependency. Its licence is
Apache-2.0; `lp.py` carries its notice.

**DD25. Neighbour search is a uniform grid**, not the k-d tree the paper suggests. It is
rebuilt in one pass and its cost per query does not grow with the crowd. *Tested* against
looking at every agent.

**DD26. An exact tie between the two passing sides is not broken.** `orca.md`, section 4.
RVO2 breaks it to the right; its behaviour is available as `orca.tie_break: right`.

**DD27. Walls follow the paper, not RVO2.** `orca.md`, section 5.

**DD28. The directive has the five fields the issue proposed, unchanged.**

| Field | Values | What it does to ORCA |
|---|---|---|
| `side_preference` | `left`, `right`, `none` | On a collision course, the pair leaves the velocity obstacle across that leg instead of the nearer one. |
| `responsibility_share` | 0 to 1; 0.5 is ORCA | On a collision course, the fraction of the needed change this agent makes. |
| `speed_scale` | 0 or more; 1 is no change | Multiplies the agent's preferred speed while the neighbour is perceived. |
| `clearance_margin` | metres, 0 or more | Added to the combined radius of the pair. |
| `passage_order` | `leader`, `follower`, `none` | Handed to the arbiter as the agreed leader at a single-file segment. |

Implementation did not show a better set. What it showed is that four of the five are
properties of a *pair*, not of an agent, which is DD29 to DD32.

**DD29. Shares: the share divides the avoidance; the room that is left is always split in
half; a pair whose shares sum to less than 1 is logged and scaled up in proportion.**
`derivations.md`, section 9. The issue's condition, α_i + α_j ≥ 1, is right for a pair on
a collision course and silent about a pair that is not; applying the share there too would
make (1, 1) unsafe.

**DD30. A pair has one side.** If one agent states a side both use it; if they state
different sides, that is a `reciprocity_violation` and neither is used.
`derivations.md`, section 10. The issue names only the shares as a reciprocity
constraint. Opposite sides break the same guarantee, so they are checked and logged the
same way, as is DD32's case of two claims to go first.

**DD31. The pair uses the larger of the two clearance margins.** `derivations.md`,
section 11.

**DD32. The arbiter decides the order at a single-file segment; ORCA is never switched
off.** Section 6.4 and `derivations.md`, section 13. The arbiter is used unchanged through
a new detector, `SingleFileDetector`. While it holds a pair the follower takes all of the
avoidance and the leader none.

**DD33. A perception record is built once per interaction, and the task is never in it.**
`perception.md`. Two choices beyond the issue: the agent's own task is left out as well as
the neighbour's, and `single_file_ahead_m` was added so that a rule can tell that
`passage_order` applies.

**DD34. An agent has arrived when its progress along its path reaches the end, and an
agent that has arrived leaves the scene.** Progress is used, not distance to the goal
point, because an agent that was pushed sideways may pass beside its goal. An arrived
agent is no longer anyone's neighbour and cannot be collided with; otherwise the first
agents through a corridor would block its end. Issue #24's agents stay where they are,
which is unchanged.

**DD35. A collision is what it was; a crowd scenario may record it and go on.**
`metrics.md`, section 6. `on_collision: stop` is the default and is issue #24's behaviour.

**DD36. Physical parameters and demographic attributes are set in different places and
cannot reach each other.** `parameters.md`, section 5.

**DD37. Log schema version 2 adds a kind of run and leaves the old one alone.**
`log-schema.md`. A negotiation run gains one field, `run_kind`. A folder written under
version 1 is still valid and is checked against version 1; a test runs the check over
every committed run folder.

**DD38. Exposure counts other agents, not walls, and is measured on the velocity the
directives leave; a yield is measured against the agent's own preferred speed.**
`metrics.md`, sections 3 and 4.

**DD39. The default sensing radius is the paper's bound**, 12.5 m, not the 5 m used in
practice. `parameters.md`, section 2. The other ORCA settings are from practice.

**DD40. With several neighbours, the smallest `speed_scale` applies.** A directive is
about one neighbour, but an agent has one preferred speed. The most cautious of its active
directives wins.

**DD41. An avoidance experiment's design is a set of named factors, crossed.** Each level
of a factor may change the scenario, the directives, the arbitration settings, who the
agents are, or what they can see. Each run records the level of every factor.

**A4. A holonomic agent may move in any direction, backwards included**, at up to its
maximum speed. That is ORCA as published. Issue #24's unicycle agents cannot reverse.

**A5. An agent's preferred velocity points at a spot a fixed distance ahead on its
desired path** (`navigation.lookahead`), at its preferred speed. After stepping aside it
drifts back to its line over that distance.

**A6. An agent that perceives a neighbour which does not perceive it uses its own
directive as it stands**, as RVO2 would. The pairwise guarantee does not cover that step;
such steps are counted (`one_sided_steps`). It can only happen when sensing radii differ
or when there are more agents in range than `max_neighbours`.

### 6.4 When control passes between ORCA and the arbiter

For a pair of agents, **from ORCA to the arbiter** on the first step on which all three
hold:

1. **Each perceives the other**: each is among the other's perceived neighbours. Before
   that neither has a directive about the other, so there is no `passage_order` to use.
2. **A single-file segment lies ahead of both.** A segment the scenario declares, on both
   their paths, too narrow for the two to pass in (narrower than their two diameters
   together), which neither has cleared.
3. **The arbiter's own test says they would be in each other's way there**: the conflict
   zone of the pair is live and the two would occupy it at overlapping times if each
   walked at its preferred speed (`negsim.conflict.timing.is_social_minigame`).

and **from the arbiter back to ORCA** on the first step on which the conflict zone is no
longer live, because one of the two has cleared it, or one of the two has arrived.

Since issue #32 there is a third way out: **from the arbiter to a back-up manoeuvre**, on
the step on which one of the two starts to back out of the segment on a `back_up`
directive (a handoff `to: back_up`). The directive has already said who goes first and how,
so the arbiter does not hold the pair, or take it, while the manoeuvre lasts; when it ends
the other has cleared the zone and there is nothing to take (`derivations.md`, section 17,
DD93). The two agents' `control_mode` is then `back_up`.

Between the first two steps:

- **The arbiter decides the order**, by `decide_roles` as in issue #24: the directives'
  leader if there is one and it can still be honoured, otherwise the shorter time to the
  zone, otherwise the lower index. It gives the follower a speed bound.
- **The bound caps the speed the follower wants to walk at**, not its maximum speed.
- **ORCA goes on building a half-plane between the two**, with the follower's share 1 and
  the leader's 0, and half-planes for every wall and every other agent as always.
- The trajectory's `control_mode` is `arbiter` for both, and `role`, `role_source`,
  `speed_bound_mps`, `zone_d_in_m` and `zone_d_out_m` are filled in.
- **One exception, at the very end.** The follower's bound is timed so that it reaches the
  zone as the leader leaves it. On the last step or two before the leader is out, the
  arbiter's own test (condition 3) can therefore find that the two no longer overlap in
  time, while the zone is still live. The pair is still held on such a step and
  `control_mode` is still `arbiter`, but the arbiter assigns no roles: `role` is empty,
  `in_conflict` is false, the bound is lifted, and the two shares are the pair's own
  again. In the committed opposing runs that is one step, at 8.9 s, before control passes
  back at 9.0 s.

Outside those steps `control_mode` is `orca` and those columns are empty.

Each handoff is an event in `events.jsonl` and an entry in the outcome, with the step, the
pair, the leader and where the leader came from. `role_source` keeps the arbiter's own
words: `negotiated` means the leader was supplied from outside, which in an avoidance run
is the directives' `passage_order` (there is no dialogue); `strategy1` means the arbiter's
own rule; `physical_precedence` means the agreed follower was already inside the zone.

The conflict zone is the segment plus a run-out at each end as long as the two radii and
the safety margin together (`derivations.md`, section 13).

**What can go wrong, and is checked for.** If the two first perceive each other when one
is already inside the zone, the arbiter can no longer keep it out. With the shipped
scenario they perceive each other 2.2 s in, each 3.55 m before its zone. A scenario with a
short sensing radius and a fast approach could be late; the arbiter then falls back on
physical precedence, as in issue #24, and ORCA is still there.

*Tested:* `tests/test_avoidance_sim.py`, from
`test_control_passes_to_the_arbiter_and_back_exactly_once` to
`test_a_segment_wide_enough_for_the_pair_is_not_single_file_for_it`.

### 6.5 What is not here

- Rules, the rule database, rule-following: section 7 (issue #28).
- Any call to a model. Negotiating a directive is a later sub-issue; it will be a
  `DirectiveProvider`.
- Non-holonomic ORCA and vehicle dynamics (DD23).
- An ordering of three or more agents at a single-file segment. The arbiter resolves
  pairs, as in section 4; a cycle of followers is possible. The shipped bottleneck has two
  agents.
- Following closely in single file. Two agents going the same way through a segment are
  made to take turns: the second waits until the first is out. The arbiter was built for
  agents going opposite ways, where that is necessary.
- Bodies that are not discs (`parameters.md`, section 7).

## 7. The rule layer (issue #28)

Section 6 built a layer in which every agent holds a directive for each neighbour, from a
`DirectiveProvider`. This section replaces directives written in a config with **stored
rules**: a rule maps a condition on what two agents can both perceive to a directive per
role, and lives in a rule database that records where it came from. It is the second of six
sub-issues; it calls no model.

### 7.1 Where each piece lives

| Piece | Where | What it is |
|---|---|---|
| Pair-level perception | `negsim/avoidance/perception.py` | `PairFeatures`, `pair_features`, `encounter_of`: what both agents of a pair can tell about the two of them. Perception record version 2 (`perception.md`) |
| What a rule may read | `negsim/rules/fields.py` | The fields, their units and the visibility each needs; the fields refused, with reasons |
| Conditions | `negsim/rules/conditions.py` | Comparisons and `all`/`any` groups. Data, never code |
| Snapshot | `negsim/rules/snapshot.py` | The values one evaluation reads, for one pair at one step: from the world (shared) or from one agent's record |
| A rule | `negsim/rules/model.py` | `Rule`, `RoleAssignment`, `Match`; parsing and the load-time checks |
| Schema | `rule_db/schema/rule.v1.schema.json`, `negsim/rules/jsonschema_subset.py` | The versioned JSON Schema and the validator for its keywords |
| Ambiguity | `negsim/rules/ambiguity.py` | The grid of test situations; two rules that can clash |
| Database | `negsim/rules/database.py`, `rule_db/` | Rule files, the manifest that freezes them, rule sets, the index by encounter class (`ActiveRuleSet`) |
| Matching | `negsim/rules/matching.py` | The policy of `rule-matching.md`: `RuleMatcher`, `PairRules`, `evaluate` |
| Provider | `negsim/rules/provider.py` | `RuleDatabaseProvider`, behind the `DirectiveProvider` interface |
| Command line | `negsim/rules/cli.py`, `ruledb.py` | Read-only: list, validate, history, show |
| Tables, benchmark | `negsim/rules/report.py`, `negsim/rules/benchmark.py` | The tables of the behaviour checks, read from the committed logs (`behaviour-checks.md`); what matching costs per step |
| Pair interactions | `negsim/avoidance/simulation.py` | `PairInteraction`: the unit rules are matched on and outcomes are categorised on |
| Baselines | `configs/baselines/`, `negsim/experiment/baselines.py` | The two frozen baselines (`baseline.md`) |
| Experiments | `negsim/experiment/avoidance.py`, `configs/rule_following/` | `baseline:` and `provider: rules` in avoidance experiments; the experiments of the behaviour checks |
| Logs | `negsim/runlog/schema.py` | Log schema version 3 (`log-schema.md`) |

### 7.2 One step, with rules

```
   every time step, before ORCA:
   ┌──────────────────────────────────────────────────────────────────────────────┐
   │ PERCEIVE      as in section 6.2; a new neighbour's record is version 2         │
   │ PAIRS         open and close pair interactions; note which have passed         │
   │ RULES         for every open pair (RuleMatcher):                               │
   │                 class now ──hysteresis──> steady class                         │
   │                 held and passed? ──> the match expires                         │
   │                 nothing held? ──> shared snapshot ──> rules for the class,     │
   │                                     highest priority first ──> roles ──>       │
   │                                     one directive per agent                    │
   │                 held and the steady class changed? ──> only strictly higher    │
   │                                     priority may replace it                    │
   │               changed directives ──> the agents' interactions                  │
   │ then RESOLVE, COORDINATE, CHOOSE, MOVE as in section 6.2, unchanged            │
   └──────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 What changed outside `negsim/rules/`, and what did not

The issue asks for the rule provider to work behind the existing interface "with no other
layer changed". **Unchanged**, byte for byte since the branch this one is cut from: ORCA
(`orca.py`), the linear programs (`lp.py`), the neighbour search (`neighbours.py`), the
coordination with the arbiter (`coordination.py`), the arbiter itself (`negsim/conflict`,
`negsim/control`), the core (`negsim/core`), `resolve_pair`, `NullProvider` and
`StaticProvider`. **Changed**, and why:

- `perception.py`: the pair-level fields a rule may read (Part 2 asks for them).
- `directives.py`: `DirectiveProvider` gains optional hooks with no-op defaults (DD56).
- `simulation.py`: pair interactions and their outcome categories (Part 7); the run loop
  calls the hooks; `speed_scale` expires when the encounter has passed (Part 5, DD55); the
  baseline's perturbation (Part 1, DD60).
- `negsim/experiment/`, `negsim/runlog/`: baselines, `provider: rules`, log schema 3.

Of the 46 committed runs of issue #26, 44 come out exactly the same with this code; the two
that use `speed_scale` differ, as Part 5 intends (`derivations.md`, section 15).

### 7.4 Design decisions

Marked as decisions: they are this project's choices where the issue left room, and each
needs the supervisor's sign-off. `WORK_LOG-28.md` gives the reasoning at the time.

**DD42. The pair-level fields are computed once per pair and step, lower-numbered agent
first, and shared** by both records and the snapshot (`perception.md`). Equal to the last
bit, which the equivalence of `rule-matching.md`, section 1, needs.

**DD43. Encounter classes**: single-file first, then `none` if not approaching
(`p · w ≥ 0`), then by heading difference, below 60° overtaking, above 120° head-on,
between them crossing. The two angles cut 0–180° in three equal parts and have no source
`[placeholder]`. The class needs `speed` and `size` visible.

**DD44. The corridor width between two agents** is measured at right angles to the line
between them, every 0.25 m, and a side with no wall in range counts as the environment
range, so it is never missing.

**DD45. A rule names a field with a prefix**: `pair.`, `either.`, `both.` (conditions),
`agent.` (role assignments). A name that picks one agent from its own point of view
(`observer.`, `neighbour.`, ...) is refused as unobservable.

**DD46. A comparison on a missing value is false**, whatever the operator.

**DD47. Every number in a condition states its unit**, which must fit the field; angles may
also be in degrees.

**DD48. The JSON Schema is checked by a validator written here**, for exactly the keywords
the schema uses, because only `yaml`, `pytest` and `matplotlib` may be imported. It refuses
a schema with any other keyword. Checked against `jsonschema` 4.26.0 outside the repository
on every rule file and 20,000 mutations: no disagreement (`WORK_LOG-28.md`).

**DD49. Immutability is enforced by a SHA-256 manifest** (line endings normalised), for
rules, rule sets and the schema. A change of status, or added evidence, is a new version.
There is no tool that writes to the database yet: the command line is read-only, as the
issue asks, and SI-3 will need a writer.

**DD50. A role assignment must state its tie policy**; version 1 offers only `no_match`.
An optional `tie_within` makes near-equal values a tie.

**DD51. A third consistency rule**: two roles told to pass on opposite sides are refused at
load, beside the issue's two (shares, passage order). DD30 already calls that a violation at
run time.

**DD52. Ambiguity is checked when rules are switched on**, on the grid of
`rule-matching.md`, section 8; the database also reports, as information, the pairs that
could not be switched on together.

**DD53. Re-evaluation follows the issue's list literally**: when a pair forms, on every step
while nothing holds, and when the class changes. A held rule is not re-evaluated otherwise,
so a higher-priority rule whose threshold is met later in the same encounter does not
replace it.

**DD54. Hysteresis**: a class change counts after 3 steady steps; holding is sticky and
replacements must have strictly higher priority; after expiry nothing until the class has
changed.

**DD55. When an encounter has passed** (`derivations.md`, section 15): the issue's
definition, applied to `speed_scale` for every provider and to every field of a rule match;
a rule may say `expiry: out_of_range` instead.

**DD56. The provider interface gains optional hooks** (`follows_pairs`, `update`,
`close_pair`, `summary`), all no-ops by default. The rule provider still answers
`directive(record)` from the record alone; the hooks let it follow a pair from step to step
without a full perception record being rebuilt for every interaction on every step.

**DD57. An outcome with no exposure but a yield event is `resolved`** (`metrics.md`,
section 9): the issue's three definitions leave it out.

**DD58. A yield counts for a pair if it overlaps the pair in time**, which can over-count in
a crowd, in the direction of `resolved`.

**DD59. Cross-pair conflicts**: side, speed scale and passage order, between fields the
rules set themselves, settled as `rule-matching.md`, section 7, says.

**DD60. The baseline's perturbation is RVO2's**: length uniform on [0, 1e-4] m/s, direction
uniform, every agent, every step, from its own random stream (`baseline.md`, section 3).

**DD61. Baselines are frozen and laid under an experiment's own overrides**; their 40
neighbours and 12.5 m are tagged `[placeholder]`, as the issue says.

**DD62. `logging.interactions: false` leaves out both per-interaction files**
(`interactions.jsonl` and `pair_interactions.jsonl`); the outcome counts both either way.

**DD63. The log schema version is one number for both kinds of run**: a negotiation run now
says 3, with nothing else changed.

**DD64. `single_file_first_arrival` keeps the `out_of_range` expiry**: its passage order
matters while the arbiter holds the pair, which can outlast "passed" between the two bodies.

### 7.5 What is not here

- Any call to a model; negotiating rules (SI-3); extracting them (SI-4); evaluating and
  validating them (SI-5, SI-6).
- A tool that writes to the rule database (DD49).
- Imperfect or delayed perception, which would break the equivalence of
  `rule-matching.md`, section 1.
- Ordering three or more agents at a single-file segment, and following in single file
  (section 6.5): a rule can name a leader for a pair, and the arbiter still works pair by
  pair.
- A fix for the artefacts of issue #26 (walking backwards, being hurried along, all-round
  vision); the behaviour checks count them.

## 8. Rule generation (issue #30)

Sections 6 and 7 let agents follow rules; nothing yet produced a new one. This section turns a
conflict into a **candidate rule**, in two ways to be compared later: two model agents
negotiating a standing rule (condition A), and one model stating a rule (condition B). It is
the first half of the third of six sub-issues (SI-3a). Everything is built and rehearsed on
the mock client; the paid pilot is held (`rule-generation.md`, section 10).

### 8.1 Where each piece lives

| Piece | Where | What it is |
|---|---|---|
| Pair exposure, tiers | `negsim/avoidance/exposure.py`, `negsim/metrics/avoidance.py`, `negsim/avoidance/simulation.py` | A conflict measure that reads no directive, and the severity tiers T0 to T4 (`metrics.md`, section 11) |
| Paired seeds | `negsim/experiment/avoidance.py` | `design.seeding: paired` (`baseline.md`, section 6) |
| Rule schema 2, canonical form | `rule_db/schema/rule.v2.schema.json`, `negsim/rules/model.py`, `negsim/rules/database.py`, `negsim/rules/canonical.py` | `stated`, `intent`, `screening`; when two rules are the same rule (`rule-format.md`, sections 12 and 13) |
| Cases | `negsim/rulegen/cases.py`, `cases/`, `configs/cases/` | Conflicts of finished baseline runs, frozen (`cases.md`) |
| Design matrix | `negsim/rulegen/design.py` | Sessions: a case, a persona pair, a condition, an order, a repeat |
| Descriptions | `negsim/rulegen/describe.py`, `negsim/negotiation/templates/rulegen_*_v1.yaml` | The situation in words, the field glossary, the format example, all frozen |
| Protocols | `negsim/rulegen/protocol.py`, `negsim/negotiation/protocol.py` (`request_with_retry`) | Condition A (negotiate) and B (state), on issue #24's ask-and-retry loop |
| Validation | `negsim/rulegen/validate.py` | The category of every proposal |
| Writer, promotion | `negsim/rulegen/writer.py`, `negsim/rulegen/cli.py` | Staging databases; `python -m negsim.rulegen promote` |
| Replay, screening | `negsim/rulegen/replay.py` | Each rule alone, on its case's run and in the two-way flow |
| Experiment type | `negsim/rulegen/experiment.py`, `configs/rule_generation/` | `layer: rule_generation`: the whole pipeline, the cost preview, the logs |
| Mock paths | `negsim/rulegen/mock.py` | Mock-client policies that take every path of both protocols |
| Budget scope | `negsim/llm/budget.py` | A cap on one experiment's own calls |

### 8.2 One experiment, step by step

```
   cases (frozen) ──> design matrix ──> sessions, in a seeded order
        │
        ├── cost preview ──> paid client? needs the preview under the cap and --confirm
        │
        ├── condition A: two agents, first-person prompts, turns of
        │     {message, proposal, accept, no_rule_possible} ──> agreed / no rule possible /
        │     no agreement / parse failure                     (every turn kept, every attempt)
        ├── condition B: one call, third-person, {rule, reason}, K repeats
        │
        ├── validation: every proposal ──> valid / needs communication / inconsistent /
        │                                   schema error / format limit     (none discarded)
        ├── writer: valid agreed or stated rules ──> rule_db_staging/<condition>/  (rule_db/
        │                                             is never written; promotion is by hand)
        ├── replay: each rule alone on its case's own run, beside the baseline on the same seed
        ├── screening: each rule alone in the 50 + 50 flow, beside the flow with no rule
        │                ──> the rule's next version, with its screening block
        └── report: categories, agreement, stability, tokens and cost against the preview
```

### 8.3 What changed outside `negsim/rulegen/`, and what did not

**Unchanged** since the branch this one is cut from: ORCA (`orca.py`), the linear programs,
the neighbour search, the coordination with the arbiter, the arbiter, the core, the matching
policy (`negsim/rules/matching.py`) and the rule provider. **Changed**, and why:

- `avoidance/simulation.py`, `avoidance/exposure.py`, `metrics/avoidance.py`,
  `runlog/schema.py`, `scenarios/crowd_base.py`: pair exposure and the tiers, log schema 4
  (Part 1.1). The run loop records each agent's intended velocity before the projection;
  nothing it does changed.
- `experiment/avoidance.py`: paired seeds (Part 1.2), and a way to reload a rule database
  that grows while an experiment writes to it.
- `rules/model.py`, `rules/database.py`, `rules/cli.py`, `rules/canonical.py`: schema 2 and
  the canonical form (Part 1.3).
- `viz/viewer.py`: which rule fired for each pair (Part 1.4).
- `avoidance/perception.py`: reading a perception record back from a log, for cases.
- `negotiation/protocol.py`: #24's turn loop split out as `request_with_retry`, which both
  protocols reuse; `Dialogue` behaves as before (its tests pass unchanged).
- `negotiation/prompts.py`, `negotiation/freeze.py`: a template may say its `kind`, and only
  negotiation templates are offered to negotiation experiments.
- `llm/budget.py`: the scoped cap (DD83). `experiment/cli.py`, `run_experiment.py`: the
  new layer and `--confirm`.

The committed experiments of issues #26 and #28 are pinned to `per_run` seeding, so that they
stay reproducible (DD66).

### 8.4 Design decisions

Marked as decisions, as in section 7.4: this project's choices where the issue left room,
each needing the supervisor's sign-off. `WORK_LOG-30.md` gives the reasoning at the time.

**DD65. Tiers are the conflict classification from issue #30 on** (`metrics.md`, section
11.3); the categories of issue #28 are kept as they were.

**DD66. Paired seeding is the default**; the committed configs of #26 and #28 are pinned to
`per_run` (`baseline.md`, section 6).

**DD67. Pair exposure** uses the bodies' obstacle (no clearance margin), the larger of the
two horizons, a depth tolerance of 1e-3 m/s, and counts overlapping bodies as exposed
(`metrics.md`, section 11.2).

**DD68. `collision_course_min_s` is 0 s**: T1 is any exposed step.

**DD69. The canonical form** keeps `encounter`, `when`, `roles`, `directive` and `expiry`,
numbers to 12 significant digits, and nothing else changed; a proposal id is 12 hexadecimal
characters (`rule-format.md`, section 13).

**DD70. A pair that formed one-sided is not a case**, and **DD71. a pair must be approaching
when it forms** (`cases.md`, section 2).

**DD72. The design's levels mean:** a base age of 25 and an older person of 70; errands "the
emergency room" (urgent) and "the supermarket" (routine), GameChat's highest- and
lowest-priority task types; four gender pairs; the full factorial; session ids from what a
session is; no names (`rule-generation.md`, section 2).

**DD73. What a description shows**, and how numbers are rounded: an agent's own perception
record and its own state and errand, never the other's errand, usual or maximum speed, goal
or path; third-person, both; a generated glossary whose hash is pinned; a placeholder format
example (`rule-generation.md`, section 3).

**DD74. A turn of condition A has a fourth key, `no_rule_possible`**, and "no rule is
possible" is an outcome when both say so on consecutive turns.

**DD75. Agreement** is accepting the other's latest proposal by its proposal id, or any
longer prefix of its hash, in either case, without proposing a different rule in the same
turn; re-proposing the same canonical rule is not a difference. The words and priority of
an agreed rule are the proposer's.

**DD76. A turn unreadable after its one retry ends a negotiation** (`parse_failure`), where
issue #24's dialogue counted it as silence.

**DD77. Stability** counts "no rule" and "parse failure" as answers and leaves aborted repeats
out.

**DD78. Validation's precedence** (needs communication, then format limit, then the loader's
reasons); a field the session hides needs communication; a formula must depend on something;
roles given by a category are a format limit; the manual-review patterns
(`rule-generation.md`, section 6).

**DD79. The writer** stores only valid agreed or stated rules, once per condition, case and
canonical rule, in the earliest supporting session's words, and stores a rule again as its
next version when more sessions support it.

**DD80. Replay** uses the people and visibility of the rule's earliest supporting session, on
the case's own run, and checks that the baseline reproduces the case.

**DD81. Screening** is in the 50 + 50 flow on the primary baseline, seeds from 30900 paired,
with a crowd given the design's two ages and two genders in turn; **gridlock** is a deadlock,
or the time limit reached with people still walking, on a seed on which the baseline did
neither. A canonical rule is screened once per invocation and visibility.

**DD82. The cost preview's terms**: S includes room for a failed reply and the retry
instruction, m is the reply cap plus the longest turn wrapper, every text is estimated 1.5
times high as the budget guard does, and every send of a turn is counted, 2 × (1 + transport
retries); peak cache-miss prices (`rule-generation.md`, section 9).

**DD83. A pilot's cap is on its own calls** (a scoped budget guard), since the ledger already
holds earlier spending; a scoped guard labels unlabelled calls and refuses others'.

**DD84. A paid run needs `--confirm` after its preview**; running again resumes; a changed
config needs a new name.

### 8.5 What is not here

- The paid pilot (held), the full paid collection and the A versus B comparison (SI-3b).
- Generated rules switched on together, semantic equivalence of rules, Q3, rules inferred
  from behaviour (SI-4).
- Live negotiation during a run, unseen scenarios (SI-5); evidence about people (SI-6).
- Matching cost (Q11), and a rule format that reads private information.

### 8.6 The supervisor's direction of 2026-10-20

From the supervisor meeting of Tuesday 2026-10-20 (track issue #55). These are the
supervisor's points, not this project's choices, so they are numbered **SV**, not DD. The
user's notes are recorded word for word in the root `CLAUDE.md`, "Supervisor decisions"; each
point here summarises one or more of them. What is still undecided is listed in `CLAUDE.md`,
"Pending sign-offs". `WORK_LOG-56.md` records how they were written down.

**SV1. Resolve first, rule after.** The first step is to ask whether LLM agents can resolve a
conflict, without asking them for a rule; only after that is a rule extracted. Conditions A and
B (section 8.2, DD74 to DD79), which ask for a rule directly, are therefore **no longer the way
rules are generated**. They stay built and unchanged, and their configs behave as before.

**SV2. Find the hidden rule or pattern** in how the agents resolved the conflict, and **ask the
LLM for the reference** the rule comes from. Which LLM gives the reference, the extractor or the
agents in a debrief, was pending (#55, decision 7); the user decided on 2026-10-22: both (D8).

**SV3. Verify the extracted rule with real human behaviour.** Whether that means published
studies or observed data is pending (#55, decision 6).

**SV4. Include as many factors as possible, and find which ones drive the decision**, with a
mapping from factors to decision. More factors may be added, for example the agent's
attractiveness, represented as a matrix. Its ethics sign-off is pending (#55, decision 3); no
paid run may switch it on until `CLAUDE.md` records it.

**SV5. The rule format no longer matters much**, since an LLM can translate a rule for each
simulator. Rule format 3 (section 9) stays as it is, and translating extracted rules into it
(#67) is low priority. The portable-rules track (#34) is on hold; how far the pause reaches is
pending (#55, decision 5).

**SV6. A rule may be more specific**, for example "keep left".

### 8.7 The resolution design of 2026-10-22

On 2026-10-22 the user replaced the first version of Step 1 (#57), whose reply was a fixed menu
(`priority`, `side`, `speed`, `back_up`) that framed every meeting as "who goes first". The new
design is specified in full in `resolution.md`; this subsection is its decision record.

These are **the user's decisions**, made on their own authority. They need no sign-off from the
supervisor, so they are numbered **D**, as in `resolution.md` and the RF issues, not **DD**
(this project's proposals, each needing the supervisor's sign-off) and not **SV** (the
supervisor's points). D1 is not DD1. Every entry below is **the user, 2026-10-22**.
`WORK_LOG-72.md` records how they were written down.

They also settle three items that `CLAUDE.md` listed as pending: the silent condition (#55,
decision 4: three conditions, D3), who gives a rule's reference (decision 7: both, D8), and the
"no new simulation code" instruction (decision 8: lifted; RF-4 and RF-17 add simulation code).
The other pending items are unchanged.

**D1. The reply says what the agent physically does** (the user, 2026-10-22): an optional
`message` (talk only) and `signal` (non-verbal and talk), then `intent`, then `steps` (each with
a start, a speed, a turn, a backing distance and an `until`), then a private `reason`. **There is
no `priority` field**: who went first is measured in the replay. Agents stay discs of a fixed
size: no turning sideways, no change of body size.

**D2. The description follows what a person would perceive** (the user, 2026-10-22): fixed text
first for the prompt cache; then ABOUT YOU, YOUR NOTES, WHERE YOU ARE, WHO YOU CAN SEE (75°,
10 m, not hidden, full detail within 5 m), WHAT YOU CAN HEAR (any direction), WHAT YOU HAVE DONE
and TIME TO MEET. Left and right are the agent's own. Never another's errand or private factors,
the fictional group, a walking convention, "usually", "one of you has to go first", or
`persona_v1`'s scene text. *Amended by the user, 2026-10-23 (issue #61):* a person's factor lines
(RF-5's observable ones, RF-6's pairwise ones) are given from 10 m, under the short line too
(core template `resolve_v3`); under `resolve_v2` they were given only within 5 m, and so never in
the head-on case. *Amended by the user, 2026-10-24 (issue #64):* the other's age and gender are
given from 10 m too, under the core template `resolve_v4`, which a config names.

**D3. Three conditions, first person only** (the user, 2026-10-22): independent (one decision
point, no message, no signal), non-verbal (signals and movement, up to 3 decision points) and
talk (non-verbal plus `message`, up to 3). No third-person condition: #30's condition B is not
used.

**D4. An agent is prompted only when a conflict is predicted** (the user, 2026-10-22): it sees
or hears the other, the distance is shrinking, the conflict detector predicts both in the same
zone at the same time, and it is not already in an encounter with them. Seeing someone is not
enough.

**D5. It is prompted again only when something new happens** (the user, 2026-10-22), and the
conflict still matters. Only the agent who noticed; at least 1 s apart; at most 3 decision
points per encounter; every decision point logs why it fired. The thresholds of "noticeably" are
placeholders.

**D6. Plans are measured in `plan_only`, with `plan_orca` as a second replay** (the user,
2026-10-22): in the live loop ORCA does not steer the encounter's agents apart, because plain
ORCA already passes a head-on pair. An encounter unresolved after its last decision point is
recorded as **not resolved by the LLM**, and what ORCA does next is recorded separately.

**D7. Memory** (the user, 2026-10-22): within an encounter, the WHAT YOU HAVE DONE lines; across
encounters, only as designed notes (RF-5's `memory_note`), so that sessions stay independent.

**D8. References come from a debrief and from the extractor** (the user, 2026-10-22): after the
encounter, never during it, each prompted agent is asked outside its role what its decision was
based on, with "none" a good answer; every source is stored as `unchecked`; RF-11's extractor
also gives references; RF-14 checks both.

**D9. The LLM is used only in encounters set up on purpose or mined from crowd runs** (the user,
2026-10-22). The full simulation (RF-18) runs ORCA and the extracted rules with no LLM call. A
resolution that relied on a signal or a word becomes a rule tagged `needs_communication`, and
the report counts them.

**D10. The view cone, occlusion and hearing are for the LLM only** (the user, 2026-10-22). ORCA's
neighbour search and the perception record that rules read are unchanged.

**D11. Two-person cases in rounds 1 to 3** (the user, 2026-10-22); rounds 4 and 6 add more than
two prompted people, with a cap per encounter as a cost limit.

**D12. The values** (the user, 2026-10-22): 75°, 10 m (Moussaïd et al. 2011), 5 m (Rio et al.
2018), no fixed count (Wirth et al. 2023); the hearing range, the signal range and the change
thresholds are placeholders (`parameters.md`, section 8).

**D13. Every prompt and raw reply is kept and committed** (the user, 2026-10-22); a paid
session's record is never deleted or overwritten. Replays can be rebuilt from their seed and the
recorded plans. Every rule traces back to the raw replies.

**D14. Variation comes from geometry, not blanket repeats** (the user, 2026-10-22): 2 or 3 case
geometries per factor cell, a small exact-repeat set for the noise floor, and the total size set
from RF-9's measured variability.

**D15. One scenario at a time** (the user, 2026-10-22): the pipeline is built once (Part 1),
then each scenario is a round (build, pilot, screen, extract, test with earlier rounds' rules,
verify). Round 1 is full depth, later rounds lean by default. Every round keeps RF-5's core
factors and gets its own cap in `CLAUDE.md` before its paid runs.

**D16. A scenario is a plug-in** (the user, 2026-10-22): it supplies its geometry and cases, its
encounter definition, its description lines in a frozen `scenario_<name>_v1.yaml`, its events,
its factors and its outcome measure. The pipeline never names a scenario; adding one never edits
the core templates or another scenario's code.

**D17. The scenario order** (the user, 2026-10-22): head-on in a corridor, meeting in a narrow
passage, "excuse me" from behind, boarding a train, the escalator, queue cutting. Scenarios with
cars are dropped for now.

## 9. Fictional groups and meetings inside a passage (issue #32)

Two additions, each from the person to the log. **A fictional group** (`ethnic_group`): a
label with nothing behind it, which agents may see and **no rule may read**, as a factor of
rule generation that is off unless a config switches it on, and that no paid run may switch on
until the supervisor's ethics sign-off is recorded (`fictional-groups.md`). **A meeting inside
a single-file passage**: scenarios that start two people there, perception fields that say how
far each has walked in, a directive `back_up` and a manoeuvre that carries it out, and rule
format 3, which can say "the one who has walked less far in backs out" (`derivations.md`,
sections 17 and 18). Prompt version 2 tells a model both.

### 9.1 Where each piece lives

| Piece | Where | What it is |
|---|---|---|
| The group's labels | `negsim/personas/groups.py`, `negsim/personas/schema.py` | The default labels, their check, a guard list of real group names, the framing word |
| Perception record 3 | `negsim/avoidance/perception.py` | The passage fields (computed once per pair) and the group, hidden by default (`perception.md`) |
| No rule may read a group | `negsim/rules/fields.py`, `negsim/rules/model.py` | `protected_reference`, `protected_part`: refused before every other check (`protected_attribute`) |
| Rule format 3 | `rule_db/schema/rule.v3.schema.json`, `negsim/rules/fields.py`, `negsim/rules/model.py`, `negsim/rules/conditions.py` | `back_up`, true-or-false values, each field's `since` version; the check that exactly one role backs up (`rule-format.md`, section 14) |
| The seed rule | `rule_db/rules/passage_shorter_backs_out.v1.yaml` | A test fixture, not in the `default` set |
| The directive | `negsim/avoidance/directives.py` | `back_up`, and how a pair's two directives combine on it |
| The manoeuvre | `negsim/avoidance/simulation.py` | Back out, wait, go on; its phases in the trajectory, events and outcome; who came out of a segment first |
| The arbiter lets go | `negsim/avoidance/coordination.py` | A pair in a manoeuvre is `released`, with a handoff `to: back_up` |
| Intentional backing apart from the artefact | `negsim/metrics/avoidance.py`, `negsim/avoidance/simulation.py` | The backing phase never counted as walking backwards; the artefact's distance within its episodes |
| The scenarios | `negsim/scenarios/passage_meeting.py`, `configs/scenarios/passage_meet_*_v1.yaml`, `negsim/scenarios/crowd_base.py` | `passage_meeting`; `backing_speed`; `start_speed` |
| The group in the design | `negsim/rulegen/design.py` | `design.ethnicity`: group pair, label rotation, visibility |
| Outcomes for analysis | `negsim/rulegen/outcomes.py` | One row per session: who proposed, conceded, took the larger share, went first, backed up |
| Prompt version 2 | `negsim/negotiation/templates/rulegen_*_v2.yaml`, `negsim/rulegen/describe.py` | Frozen; a line is used only by a template that has it (`rule-generation.md`, section 3.1) |
| Validation | `negsim/rulegen/validate.py` | `protected_attribute`; what a later format added is a format limit of an earlier one |
| The mock | `negsim/rulegen/mock.py` | `rulegen_paths_v2`: the old paths and three new ones |
| Case format 2 | `negsim/rulegen/cases.py` | Re-stepping (`cases.md`, section 7), the `experiment` stratum key |
| The behaviour checks' tables | `negsim/rules/report.py` | `passage_tables` (`behaviour-checks.md`, section 6) |

### 9.2 One step with a manoeuvre

```
   perceive ──> pair features (the passage fields, once per pair) ──> provider: directives
        │
        ├── back_up for one of a pair, both inside a segment too narrow for them (read from
        │   the geometry alone), the other ahead of it ──> a manoeuvre starts; the arbiter
        │   lets go of the pair
        │
        ├── backing: the backer walks back along the segment at its backing speed to the
        │   run-out beyond its end (shares 0 for it and 1 for the other, the other's speed
        │   capped at the backer's) ──> waiting: preferred velocity 0 (shares 1 and 0)
        │
        ├── the other out of the conflict zone by the arbiter's own measure, or arrived, or
        │   out of sight ──> the manoeuvre ends; the backer goes on along its path
        │
        └── ORCA for everyone, as before; the backing phase is logged as intentional
            backing, never as the walking-backwards artefact
```

### 9.3 What changed outside the new pieces, and what did not

**Unchanged**: ORCA (`orca.py`), the linear programs, the neighbour search, the arbiter's own
decisions (who leads, the speed bounds), the matching policy's precedence and hysteresis, the
two baselines, and every committed run, case and frozen template: rule formats 1 and 2 load as
before, prompt version 1 renders as before, issue #30's case set and its configs read what
they read (the pilot's excepted, below), and its extraction gives the same files. **Changed**,
and why:

- `avoidance/simulation.py`: the manoeuvre, `segment_exit_times`, log schema 5.
- `avoidance/coordination.py`: `released` pairs (DD93).
- `rules/matching.py`, `rules/ambiguity.py`: a cross-pair conflict on `back_up` (an agent backs
  out for one pair at a time), and the values a true-or-false field can take.
- `rules/snapshot.py`, `rules/fields.py`: the passage fields in the shared snapshot, and the
  version each field was added in (DD90).
- `metrics/avoidance.py`: `EpisodeTracker.total_amount`, so that the artefact's distance counts
  what its episodes count (DD98).
- `experiment/avoidance.py`, `runlog/schema.py`: `first_out` and the exit times, log schema 5
  (DD99, DD111).
- `viz/viewer.py`, `viz/viewer.html`: backing, waiting and the other, and the new event.
- `rulegen/experiment.py`, `rulegen/writer.py`: a session records the rule format its prompt
  described, and its rules are validated and written in it; the sign-off check for a paid run
  with the group on.
- `configs/rule_generation/si3_pilot.yaml`: prompt version 2 and the re-stepped cases, its
  design and its cap unchanged (DD117).

### 9.4 Design decisions

Marked as decisions, as in sections 7.4 and 8.4: this project's choices where the issue left
room, each needing the supervisor's sign-off. `WORK_LOG-32.md` gives the reasoning at the time.

- **DD85.** The default labels: Kestrop, Dremmik, Pellund, in that order of rotation; Brannoq
  a spare. Each searched, and every search recorded (`fictional-groups.md`, section 2).
- **DD86.** The framing word defaults to "ethnic group", a setting recorded with every
  session. **Pending supervisor review.**
- **DD87.** `ethnic_group` is a persona attribute: hidden by default, absent from a persona that
  does not give it, flagged on its definition as not readable by rules.
- **DD88.** `protected_attribute`: any reference to the group, anything derived from it, a
  label, or a session's own framing words, in a condition or a role assignment, refused first.
- **DD89.** The passage fields are computed once per pair from the two positions and the
  passage; "ahead" is the end on the other's side.
- **DD90.** Every rule field records the format version that added it; a rule reads only its
  own version's fields; a template's glossary is generated for the format it describes.
- **DD91.** `passage_meeting` places the two at the meeting point, 0.1 m apart, **at rest by
  default** (`start_speed`; open question Q2 of `WORK_LOG-32.md`).
- **DD92.** `backing_speed`, an optional agent-type parameter, 0.92 m/s when not set
  (Nakahara et al. 2005), never above the maximum speed.
- **DD93.** A pair in a manoeuvre is taken from the arbiter, which does not take it meanwhile.
- **DD94.** The manoeuvre: back to the run-out beyond the end at the backing speed, wait, go
  on. It starts only inside a segment the two meet in, read from the geometry.
- **DD95.** While backing, shares 0 and 1 and the other's speed capped at the backing speed;
  while waiting, 1 and 0.
- **DD96.** `back_up` names the other as leader; two who back up are a reciprocity violation.
- **DD97.** A rule that sets `back_up` must back up exactly one of two roles, and not the one
  that goes first; a rule that sets none of it is not checked for it (open question Q3).
- **DD98.** The backing phase is never the walking-backwards artefact; everything else is, a
  waiting backer pushed back included.
- **DD99.** Log schema 5; folders of versions 1 to 4 are checked against their own.
- **DD100.** Rule schema 3: version 2 with `back_up` and true-or-false values.
- **DD101.** The label rotation is cyclic: person 2 of a `different` pair gets the next label.
- **DD102.** `ethnicity_visible: false` hides the groups from both people, a person's own too.
- **DD103.** The ethics sign-off is one exact sentence in `CLAUDE.md`, with a date; only the user
  adds it; a mock run needs none.
- **DD104.** What a rule does to each person is read on the case's own snapshot with the
  session's people in it.
- **DD105.** The rule-generation log is version 2 (`outcomes.jsonl`, the group).
- **DD106.** Prompt version 2 is version 1 with four kinds of line and the format-3 glossary;
  version 1 stays a config's default.
- **DD107.** `protected_attribute` is a validation category of its own, before every other.
- **DD108.** What a later rule format added is a format limit for a session shown an earlier one.
- **DD109.** A new mock policy beside the old, whose paths are unchanged.
- **DD110.** Cases get new versions by re-stepping their source runs, checked field by field.
- **DD111.** Who came out of a single-file segment first, and when each did, are logged.
- **DD112.** A case's format version follows its content.
- **DD113.** A manoeuvre ends when the other is out of the conflict zone by the arbiter's own
  measure.
- **DD114.** The behaviour checks: the issue's three modes, a time-optimal reference, 20 paired
  seeds, the primary baseline.
- **DD115.** The passage cases are stratified by source experiment and layout.
- **DD116.** Outside the passage of a pair that has one, `in_segment` is false, not null; the
  distances are null. **Flagged**: the issue says the fields are null outside the passage.
- **DD117.** The pilot runs on prompt version 2 with the re-stepped cases; its design and its
  cap are unchanged.
- **DD118.** The floor for m is the largest valid mock reply, stated as a lower bound; option
  (b)'s reply cap is 400 tokens.
- **DD119.** The priority order proposed for option (d) of issue #30's Q5.

### 9.5 What is not here

- Real ethnicities, or any description of the fictional groups; any paid run with the group on
  (the sign-off is pending).
- Three or more people in a passage, people queued behind a backer, and a backer that steps
  aside before the other comes out (Q4).
- The paid pilot and SI-3b; live decisions during a run (SI-5); evidence about people (SI-6).
