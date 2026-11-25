# Architecture

What the pieces are, how a run flows through them, and which choices were this project's
own. Decisions are numbered **DD** and marked as decisions: they are not facts taken from
the paper or the issue, and each needs the supervisor's sign-off. Assumptions are numbered
**A**.

## 1. The pieces

```
run_experiment.py            command line: load a config, pick a client, run, report

negsim/
  experiment/   config.py    experiment YAML -> list of RunPlan (the design, counterbalanced)
                runner.py    one RunPlan -> one simulation -> one log folder
                batch.py     all the runs of an experiment, the client, summary.csv
  scenarios/                 scenario YAML -> ScenarioSpec (agents, walls, paths, region)
                             doorway, intersection, hallway; a base class; a registry
  core/                      Pose, Control, unicycle step, AgentSpec, World, geometry
  conflict/                  conflict zone, detection, time to the region, who leads
  control/                   controller interface, path tracker, Strategy 1 speed bound
  negotiation/               prompt templates, persona rendering, situation report,
                             turn parsing, consensus, the dialogue protocol
  personas/                  persona schema and YAML loader
  llm/                       client interface, DeepSeek client, mock client,
                             price table, spend ledger, budget guard
  metrics/                   makespan, minimum speed, path deviation, deadlock, ground truth
  runlog/                    log schema, writers, the schema check
  viz/                       transcript renderer, trajectory plot

configs/   scenarios/  personas/  experiments/  tasks/  llm/
tests/     runs/       docs/
```

Dependencies point one way: `core` knows nothing else; `conflict` and `control` build on
`core`; `scenarios` builds on those; `llm` and `personas` stand alone; `negotiation` uses
`llm`, `personas` and `scenarios`; `experiment` ties everything together. Nothing imports
from `pipeline/` or `dataset/`, and a test checks that
(`test_repo_hygiene.py::test_phase_1_code_is_not_imported`).

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
