# Work Log — Issue #28: [Feature] SI-2: rule format, rule database, and rule-following mode

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/28
**Branch:** `feat/28-rule-format-database-following`
**Started:** 2026-10-14 19:46 (UTC+8)

## Understanding the issue

This is the second of the six sub-issues planned in #26. SI-1 (#26, PR #27) built an ORCA
avoidance layer in which every agent holds, for each neighbour it perceives, an
`AvoidanceDirective` (side preference, responsibility share, speed scale, clearance
margin, passage order). Those directives came from a `DirectiveProvider`, and the only
providers were `NullProvider` (plain ORCA) and `StaticProvider` (directives written in an
experiment config).

This issue replaces config-written directives with **stored rules**. A rule is data: a
condition on what a pair of agents can both perceive, an assignment of roles, and a
directive per role. Rules live in a **rule database** (one YAML file per rule version,
with provenance and a status) that later sub-issues will write LLM-negotiated (SI-3) and
extracted (SI-4) rules into, and evaluate and validate (SI-5, SI-6). A new
`RuleDatabaseProvider` supplies directives from the database behind the existing
provider interface. No LLM is called; spend must stay at zero.

What has to exist at the end:

1. **Two frozen, versioned baselines**: `orca_perturbed_v1` (primary: plain ORCA with a
   small random perturbation of preferred velocity) and `orca_unperturbed_v1`
   (secondary), both with 40 neighbours `[placeholder]` and a 12.5 m sensing radius
   `[placeholder]`, recorded in `docs/baseline.md` with sign-off pending.
2. **A rule format** that cannot execute code: whitelisted fields, seven comparison
   operators with units, `all`/`any` groups, symmetric or ordered role assignment with
   a tie policy, a directive per role, a priority, provenance and status. A versioned
   JSON Schema, and load-time checks for mutual observability, α_i + α_j ≥ 1, and
   complementary passage order.
3. **A rule database** under `llm_negotiation/rule_db/`, immutable per version, loaded
   into an index keyed by encounter class, with a read-only command-line tool.
4. **A matching policy**: shared snapshot per pair, when rules are (re)evaluated,
   holding with hysteresis, priority, ambiguity, no-match fallback, cross-pair
   conflicts — implemented and documented in `docs/rule-matching.md`.
5. **A change to `speed_scale`**: it expires when the encounter has *passed* (p·v > 0
   and the two clear of each other), not when the neighbour leaves the sensing radius.
   The same expiry for every field held from a rule match.
6. **Five seed rules** (`test_seed`) and test fixtures, including deliberately invalid ones.
7. **Logging**: per pair interaction, every evaluation and match with rule id and
   version, roles, directives, the snapshot, expiry, and an outcome category
   (`avoided` / `resolved` / `failed`); the active rule set per run. Log schema bumped.
8. **Verification**: unit tests, a consistency property test, behaviour checks over the
   five SI-1 scenarios against both baselines with ≥ 20 seeds per condition, a
   sensing-radius sensitivity check, keep-left versus keep-right, counts of the two known
   #26 artefacts, and a benchmark of matching overhead.

Out of scope, as the issue lists: any LLM call, rule extraction, evaluation on unseen
scenarios, validation against human evidence, ordering three or more agents at a
single-file segment, fixing the #26 ORCA artefacts, performance work, Singapore
parameters, running RVO2.

### Prerequisites (checked before anything else)

- **P1. `CLAUDE.md` must record that simulation work has been approved — FAILED.**
  `CLAUDE.md` on this branch chain does not say "no simulation code" (that instruction
  sits on the unmerged `docs/5-biweekly-update-1` branch, as `WORK_LOG-24.md` found), but
  it does not record any approval either. `README.md:26-29` still states the supervisor's
  "no simulation or experiment code until the literature review is complete and
  discussed" instruction, marked "unconfirmed", and the roadmap row for the literature
  review still reads "awaiting supervisor discussion". No issue or PR comment answers Q1
  of `WORK_LOG-24.md` / `WORK_LOG-26.md`. As the issue instructs, I stopped and asked the
  user. **The user's answer (2026-10-14, in this session): "Proceed, leave Q1 open."** So
  I am proceeding, the failed prerequisite is logged as an accepted risk (Q1 below), and I
  have not written anything into `CLAUDE.md` claiming approval.
- **P2. PRs #25 and #27 merged into main — NOT MERGED.** Both are open; `main` has two
  commits. #25 targets `docs/22-simulation-conflict-rules-literature` and #27 targets
  `feat/24-llm-negotiation-simulator`. As the issue instructs, this branch is cut from
  the #27 branch, `feat/26-orca-avoidance-layer` at `54e349b`, and the PR will target that
  branch and say so (Q2 below).
- **P3. Read `WORK_LOG-26.md`, DD26 to DD32 and its open questions.** Done (and
  `architecture.md` section 6.3, `derivations.md` sections 9 to 14, `perception.md`,
  `metrics.md`, `log-schema.md`, `parameters.md`, and every module under
  `negsim/avoidance/`). I implement as those decisions stand. Where this issue changes
  one, the change is recorded below as a decision.

### Assumptions and judgement calls (mine, not instructions from the issue)

- **A1.** The PR targets `feat/26-orca-avoidance-layer` (P2), so GitHub will not close
  #28 on merge.
- **A2.** Where the issue's text and an existing test disagree because the issue asks for
  a change the test pins (the `speed_scale` duration of Part 5, the log schema version of
  Part 7), the issue wins, the test's assertion is changed to the new behaviour, and the
  change is listed in the summary. "All existing tests must still pass" is read as "no
  regression", not as "nothing the issue asks to change may change".

## Plan

Written before writing code; the progress log records where it changes.

1. Preconditions, prerequisites, baseline test run (done: 795 pass, pyflakes clean).
2. **Perception record v2**: the pair-level fields a rule needs (encounter class, heading
   difference, minimum corridor width between the two, age difference, time to the
   single-file segment), computed once per pair in a fixed order so that both agents get
   identical values; `docs/perception.md` and the version bumped.
3. **Rule format**: field catalogue (observable or not, unit, visibility needed), the
   JSON Schema and a validator for the subset of JSON Schema it uses (the repository
   allows only `yaml`, `pytest` and `matplotlib` as third-party imports), parsing,
   condition evaluation, and the load-time checks.
4. **Rule database**: files, a SHA-256 manifest that makes versions immutable, rule sets,
   the index by encounter class, the read-only command line.
5. **Matching policy and the provider**: the per-pair state machine, the
   `RuleDatabaseProvider`, and the smallest change to the run loop that lets a provider
   update directives during an interaction and lets directives expire when the encounter
   has passed.
6. **Baselines**: the two frozen configs, the perturbation, and how an experiment uses
   them. Choose the perturbation magnitude by measurement before freezing it.
7. **Logging**: log schema v3 (pair interactions, rule events, active rule set), with
   validation that still accepts every committed folder of versions 1 and 2.
8. **Seed rules and fixtures.**
9. **Tests**: unit tests per piece; the consistency property test.
10. **Behaviour checks**: the five SI-1 scenarios × two baselines × plain/rules × ≥ 20
    seeds; sensitivity at 5 m; keep-left versus keep-right; the #26 artefact counts; the
    benchmark. Numbers reported, nothing asserted in advance.
11. **Docs**: `baseline.md`, `rule-format.md`, `rule-matching.md`, updates to
    `perception.md`, `derivations.md`, `architecture.md`, `log-schema.md`, READMEs.
12. Verify every acceptance criterion; push; PR against the #27 branch.

## Progress log

### 2026-10-14 19:46 — Preconditions, issue read, prerequisites, baseline

- What I did: checked the remote and `gh auth status` (OK), the working tree (clean),
  fetched `origin`. Read the issue (no comments). Ran the three prerequisite checks above
  and asked the user about P1. Read `WORK_LOG-26.md` in full, the documents it points to,
  and every module of the avoidance layer, the experiment runner, the log schema and the
  tests that touch them. Built a fresh virtual environment in the session scratchpad
  from `requirements.txt` (Python 3.13.3; PyYAML 6.0.3, pytest 9.1.1, matplotlib 3.10.8)
  plus pyflakes 4.0.3, the version #26 used.
- Why: workflow steps 0 and 1, and the issue's prerequisites.
- Result / what I found:
  - **Baseline: 795 passed** (`python -m pytest` in `llm_negotiation/`, 77 s), the count
    #26 ended on. `pyflakes negsim tests run_experiment.py`: nothing.
  - Things in the existing code that shape the design:
    - The provider is asked once, when an interaction begins
      (`simulation.py:508`), and its directive holds until the neighbour is out of range.
      Re-evaluation, holding, preemption and expiry all need the run loop to be able to
      change a directive during an interaction. That is the one place the loop must
      change, besides `speed_scale`.
    - `_travel_speed` (`simulation.py:543-551`) takes the smallest `speed_scale` over
      every perceived neighbour: that is where Part 5's change goes.
    - `validate_run_dir` requires `perception_schema_version` to equal the *current*
      version (`runlog/schema.py`). Bumping it as the issue asks would make the 46
      committed SI-1 folders fail; the check has to become version-aware.
    - Four existing tests pin something the issue changes: three pin log schema version
      2 (`test_avoidance_runs.py`: `test_config_json_is_fully_resolved`,
      `test_a_negotiation_run_now_says_its_kind_and_the_new_version`,
      `test_every_committed_run_folder_still_passes_the_schema_check`), one pins the old
      `speed_scale` duration (`test_avoidance_sim.py::test_speed_scale_slows_the_agent_only_while_the_neighbour_is_in_range`).
      See A2.
    - One test fixes the list of configs in `configs/avoidance/` at the six of #26, so
      the new experiment configs go in a folder of their own.
    - Only `yaml`, `pytest` and `matplotlib` may be imported
      (`test_repo_hygiene.py`), so the JSON Schema validator is written here, for the
      keywords the schema uses. `jsonschema` 4.26.0 is installed in the system Python, not
      in the virtual environment; it can be used outside the repository as an oracle.
    - RVO2's own perturbation (cached by #26): a vector of length uniform in [0, 1e-4]
      and direction uniform, added to every preferred velocity every step, with a
      preferred speed of 1 (`refs/si1_rvo2_75822bb_excerpts.txt:785-797`, `Blocks.cc:162-186`;
      `:822-832`, `Roadmap.cc:322-331`). The starting point for the perturbation magnitude.
- Next step: commit this log, then perception record v2.

### 2026-10-14 19:56 — Perception record version 2: the pair-level fields

- What I did: added to the perception record what both agents of a pair can tell about
  the two of them together (`pair_features` in `perception.py`): `encounter_class`,
  `heading_difference_rad`, `min_corridor_width_m`, `age_difference_years`,
  `single_file_segment`, and each agent's `time_to_segment_s`. Version 2 of the record;
  `docs/perception.md` describes each field. Made run-folder validation check a folder
  against the perception version it declares. 20 tests (`tests/test_pair_features.py`).
- Why: Part 2, mutual observability. A rule may only read what both agents compute
  identically. The environment fields of version 1 are measured at the observer's own
  position along its own path, so two agents get different values; the issue asks for
  pair-level fields such as the encounter class and the corridor width between the two.
- Decisions (numbered in `architecture.md`, section 7, when written up):
  - The pair fields are computed **once per pair and step, lower-numbered agent first**,
    and the same object goes into both records. Equal "up to rounding" would not be
    enough for the equivalence argument of Part 4; equal to the last bit is.
  - **Encounter classes**: `single_file_segment` first (a declared segment too narrow for
    the pair, which each agent is inside or facing), then `none` if `p · w ≥ 0` (not
    approaching), then by heading difference: below 60° overtaking, above 120° head-on,
    crossing between. The 60/120 split is the range 0–180° cut in three equal parts: a
    definition with no source, `[placeholder]`.
  - **`min_corridor_width_m`** is measured at right angles to the line between the two,
    every 0.25 m, and a side with no wall within the environment range counts as the
    environment range. So it is never null, and "wide enough" is true in open ground.
  - The class needs `speed` and `size` visible; without them it is null and no rule fires.
- Result: 815 tests pass (795 + 20). The 46 SI-1 runs, run again with this code, give
  identical trajectories and events; their outcomes and interaction records are equal once
  the new record fields are set aside.
- A mistake in my own test, not the code: I expected the bottleneck's width between the
  two agents to be 0.8 m. They start at (−9, −0.4) and (9, 0.4), the line between them is
  tilted, and the width at right angles to it is 0.8 / cos(atan(0.8/18)) = 0.80079 m. The
  test now computes that.

### 2026-10-14 about 20:15 — Choosing the perturbation, by measurement, before freezing the baselines

(Entry headings are the times of the commits they describe; this step has no commit of its own,
so its time is approximate.)

- What I did: ran the three exactly symmetric SI-1 layouts (head-on, crossing, directly
  behind) and the 10 cm offset head-on with 40 neighbours, R = 12.5 m and plain ORCA, at
  six magnitudes, 20 seeds each; then at R = 5 m for 0 and 1e-4. Script in the scratchpad
  (`perturbation_probe.py`).
- Result:

  | Magnitude (m/s) | Symmetric head-on | Symmetric crossing | Directly behind | 10 cm offset head-on |
  |---|---|---|---|---|
  | 0 | deadlock 20/20 | deadlock 20/20 | no overtaking, 29.5 s | 12.2 s, left 20/20 |
  | 1e-6 to 1e-3 | 0/20; 12.3–12.4 s; left 9, right 11 | 0/20; 12.5–12.6 s | overtakes; 31.7–32.1 s | 12.2 s, left 20/20 |
  | 1e-2 | 0/20; 12.3 s; left 8, right 12 | 0/20; 12.4–12.5 s | 32.0–32.2 s | 12.2 s, left 20/20 |
  | 1e-4, R = 5 m | 0/20; 12.2 s | 0/20; 12.4 s | 31.9–32.0 s | 12.2 s, left 20/20 |

- Decision: **1e-4 m/s**, length uniform on [0, 1e-4] and direction uniform, every agent,
  every step: RVO2's own examples (`Blocks.cc:178-186`, `Roadmap.cc:322-331`), where the
  preferred speed is 1. It breaks every exact deadlock in 20 of 20 seeds, as every value
  from 1e-6 does; it leaves a non-degenerate meeting unchanged to the 0.1 s reported; it
  is 0.008% of the walking speed and 1/1,900 of the cited spread of walking speeds (0.19
  m/s). Smaller would work too; this one has a source.
- Found: the perturbation changes one SI-1 result qualitatively. Directly behind a slower
  walker, unperturbed ORCA never overtakes (the #26 "hurried along" artefact); perturbed,
  the faster walker goes round, on a side the noise picks.

### 2026-10-14 20:31 — The rules package, the seeds, the frozen database

- What I did: wrote `negsim/rules/` (`fields`, `errors`, `jsonschema_subset`,
  `conditions`, `snapshot`, `model`, `ambiguity`, `database`, `matching`, `provider`), the
  JSON Schema `rule_db/schema/rule.v1.schema.json`, the five seed rules, the `default`
  rule set, and `rule_db/MANIFEST.json`. Dry-ran the parser on every file before freezing.
- Decisions, beyond what the issue fixes:
  - **Field prefixes.** `pair.<name>` in a condition; `either.<name>` / `both.<name>` for an
    agent-level field in a condition (at least one / each of the two); `agent.<name>` in a
    role assignment. A prefix that names one agent from its own point of view
    (`observer.`, `neighbour.`, `self.`, ...) is refused as `unobservable_field`: the two
    agents would read different agents' values.
  - **A comparison on a missing value is false**, `!=` and `in` included, so a rule never
    fires on what its agents could not see.
  - **Units.** A numeric comparison must state its unit and it must fit the field (`m`, `s`,
    `m/s`, `rad`, `years`; `deg` accepted for angles and converted); a category takes none.
  - **The JSON Schema validator is written here** (`jsonschema_subset.py`): the repository
    allows only `yaml`, `pytest` and `matplotlib` as imports. It implements exactly the
    keywords the schema uses, and refuses a schema with any other, so nothing is ignored
    silently. To check it I will compare it with `jsonschema` 4.26.0 from the system Python,
    outside the repository.
  - **Immutability is enforced, not just asked for**: the manifest freezes the SHA-256 of
    every file (line endings normalised to LF, as the prompt templates do, because git on
    this machine has `core.autocrlf=true`). A file whose bytes changed, or that is not
    listed, does not load; versions of a rule must run 1, 2, 3. A status change or added
    validation evidence is therefore a new version. Rule sets are frozen the same way, so
    an experiment that names `default` means the same rules forever. There is no write tool:
    the issue keeps the command line read-only, so the manifest was made by a one-off script
    in the session scratchpad, and adding a version is a manual step until SI-3 adds a writer.
  - **Tie policy.** Only `no_match` is offered, and a role assignment without `tie:` is
    refused (`no_tie_policy`) before the schema check, so its reason is plain. An optional
    `tie_within` (with its unit) makes near-equal values a tie; without it, only exact
    equality is.
  - **A third consistency rule**: two roles told to pass on opposite sides are refused
    (`side`), beside the issue's two (shares, passage order). DD30 already treats that as a
    violation at run time; a rule can be checked for it before.
  - **Ambiguity is checked when a rule set is switched on**, over a grid built from the two
    rules' own thresholds (`ambiguity.py`, `rule-matching.md`). Because every comparison is
    one field against one constant, the grid covers every combination of outcomes; it can
    report a clash that cannot happen (fields varied independently), never miss one. The
    database also reports, as information, pairs that cannot be switched on together:
    `keep_left_head_on` and `keep_right_head_on`.
- The seeds: `keep_left_head_on` (head-on, `pair.min_corridor_width_m >= 1.0 m`: two
  effective shoulder widths of 49.8 cm, Yamamoto et al. 2019, rounded), `keep_right_head_on`
  (its mirror, not in `default`), `overtaker_keeps_clear` (roles by `agent.speed_mps`
  descending, ties within 0.05 m/s; overtaker share 1 and left, as issue #26's static
  version had it), `single_file_first_arrival` (roles by `agent.time_to_segment_s`, ties
  within 0.5 s; `expiry: out_of_range`, reason below), `younger_yields_head_on` (the
  issue's example with the real field names). Each says it is a test fixture and not a
  claim about people. Authorship is recorded as the user's specification written out by
  Claude Code: that is what happened.
- Result: the database loads, 5 versions, 0 refused; `default` switches on cleanly; the
  keep-left/keep-right clash is found with a concrete situation.

### 2026-10-14 20:32 — The run loop: pairs, expiry, a perturbation, and where the provider plugs in

- What I did: `PairInteraction` in `simulation.py` (open while either agent has an
  interaction open with the other); outcome categories at the end of a run; the "passed"
  test; the perturbation; two optional hooks on `DirectiveProvider`.
- Decisions:
  - **The provider interface gains optional hooks** (`follows_pairs`, `update(view)`,
    `close_pair(...)`, `summary()`), all no-ops by default. The rule provider still
    answers `directive(record)` from the record alone, but the matching policy needs to
    follow a pair from step to step: re-evaluation, holding, expiry. The alternative,
    rebuilding a perception record for every interaction on every step and calling
    `directive` again, costs a ray cast per wall per interaction per step and could not
    tell when a match ended out of range. `NullProvider` and `StaticProvider` are
    unchanged. Nothing in ORCA, the linear programs, the neighbour search, the
    coordination with the arbiter or `resolve_pair` changed.
  - **`speed_scale` expires when the encounter has passed, for every provider** (Part 5).
    For a provider that does not follow pairs the run loop expires it; one that does (the
    rules) replaces the whole directive itself, so that a rule saying
    `expiry: out_of_range` is honoured. "Separation exceeds the summed radii plus any
    clearance margin" is read as the distance between centres exceeding r_i + r_j + c,
    with c the pair's clearance margin.
  - **The issue's outcome categories leave a gap.** `avoided` needs no exposure and no
    yield; `resolved` needs exposure. A pair with no exposure but a yield event is
    neither, and that is exactly the follower the arbiter holds back at a single-file
    segment: its preferred speed is capped before ORCA sees a conflict. I put it under
    `resolved` ("settled by somebody waiting", as `metrics.md` already reads a yield):
    `failed` (collision or deadlock) first, then `resolved` (exposure or a yield), else
    `avoided`. Each pair also records which ingredients it had, so another reading can be
    computed from the logs. Needs sign-off (Q4).
  - **A yield counts for a pair if it overlaps the pair interaction in time.** In a crowd
    that can blame a pair for a wait caused by someone else, which moves pairs from
    `avoided` to `resolved`, never the other way (Q5).
- Three tests of issue #26 asserted the old `speed_scale` duration and now fail by design;
  rewritten to assert the new one (listed below, with what each kept).
- Result: of the 46 SI-1 runs, **44 reproduce exactly and 2 differ**: the two
  `both_left_slow` runs (scale 0.6), whose makespan goes from 18.7 s and 18.6 s to 15.4 s
  because the slowdown now ends at passing (9.4 s) instead of at 17.5 s. Their conflict
  exposure is unchanged, 6.6 s. The committed folders are left as they were: they are the
  record of what that code did.

### 2026-10-14 20:33 — Baselines, experiments, log schema version 3; tests and checks

- What I did: `configs/baselines/orca_perturbed_v1.yaml` and `orca_unperturbed_v1.yaml`,
  frozen by `configs/baselines/MANIFEST.json`, loaded by `negsim/experiment/baselines.py`
  (a changed file is refused and the error names the `_v2` to write instead).
  `baseline:` and `provider: rules` in avoidance experiments. Log schema version 3 and
  `docs/log-schema.md`. An end-to-end run of the head-on (scratchpad config): with the
  default rule set, `keep_left_head_on` matches when the pair forms (step 14) and expires
  when it has passed (step 62); with a woman of 25 and a man of 70,
  `younger_yields_head_on` wins at priority 20 and the 25-year-old takes the whole share;
  each agent evaluating on its own record agrees with the shared snapshot.
- Decisions: `logging.interactions: false` now leaves out `pair_interactions.jsonl` as
  well, instead of adding a switch (one switch for both per-interaction files; the crowd
  configs of #26 already set it). The log schema version is global, so a negotiation run
  now says 3, with nothing else changed.
- **Existing tests changed: seven functions, not the four my first issue comment said.**
  Each pinned something the issue tells me to change; each keeps every other assertion:
  - `test_avoidance_sim.py::test_speed_scale_slows_the_agent_only_while_the_neighbour_is_in_range`
    → renamed `..._only_until_the_encounter_has_passed`; same checks, split at the step
    the pair passed.
  - `test_avoidance_sim.py::test_a_smaller_speed_scale_takes_longer_and_shows_up_as_yielding`:
    "0.3 takes more than twice as long as 1.0" (23.5 s against 24.4 s now) becomes
    strictly increasing times; the yield counts `[0, 0, 2]` are unchanged.
  - `test_avoidance_sim.py::test_speed_scale_never_takes_an_agent_past_its_maximum_speed`:
    the wanted speed is checked before the pair passed instead of whenever a neighbour
    is in range.
  - `test_avoidance_runs.py`: `test_config_json_is_fully_resolved` and
    `test_a_negotiation_run_now_says_its_kind_and_the_new_version` (version 2 → 3);
    `test_schema_check_notices_damage_to_the_other_files` (its example of an unsupported
    version was 3; now `LOG_SCHEMA_VERSION + 1`);
    `test_every_committed_run_folder_still_passes_the_schema_check` (counts version 3
    folders too).
- Mistake: a shell heredoc with nested quotes failed while rewriting the validator; redone
  with the edit tool, and nothing was half-written.
- Result: **816 tests pass**, pyflakes clean. Committed in three commits (`fd3e94f`,
  `9408260`, `cc3a718`); each of the first two was tested on its own with the rest stashed
  (815 each). Nothing spent.
- Next step: the command-line tool, the fixtures, the tests of the rules package, the
  property test; then the documents; then the behaviour checks.

## Open questions / risks

- **Q1 (carried from #24 and #26). Has the supervisor's "no simulation code until the
  literature review is complete and discussed" instruction been lifted?** Issue #28 made
  it a prerequisite that `CLAUDE.md` record the approval. It does not. The user chose to
  proceed and leave the question open (P1). Nothing in the repository records the
  supervisor's position.
- **Q2. Branch base.** Cut from `feat/26-orca-avoidance-layer`, because PRs #25 and #27
  are not merged; the PR targets that branch and will not close #28 by itself.

## Summary (fill in at the end)

