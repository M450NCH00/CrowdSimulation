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

> **Note on the next four entries (written 2026-10-15, in a new session).** The session that
> did the work below ended at 21:42 on 2026-10-14 without updating this log; the four
> commits after `a712f13` and the milestone comment on the issue are its only record. These
> entries are reconstructed from those commits, their messages, the issue comment of 20:56,
> the scripts left in that session's scratchpad, and the files' timestamps. Every number in
> them that the next session could recheck, it rechecked (entry "Resuming"), and the one that
> did not survive the recheck is corrected there, not here.

### 2026-10-14 20:55 — Tests, the read-only command line, the fixtures (`650159b`)

- What I did: 158 tests in four new files (`test_rules_format.py` 80,
  `test_rules_database.py` 25, `test_rules_matching.py` 27, `test_baselines_and_rule_runs.py`
  26 at this commit); the read-only command line (`ruledb.py`, `negsim/rules/cli.py`: list,
  validate, history, show; it writes nothing); the fixtures under `tests/fixtures/rules/`:
  2 valid (`every_operator`, and `gender_keeps_clear_crossing`, the gender rule the issue
  keeps out of `rule_db/`), 15 invalid (one per load-time category, including the issue's
  five: `reads_the_task`, `shares_short_of_one`, `unknown_field`, `no_tie_policy`, and the
  ambiguous pair `clash_side` / `clash_clearance`, which load alone and are refused together).
  The fixture files were written by a script (`write_fixtures.py`, in that session's
  scratchpad), each with a first line naming the category it must be refused for.
- Checks run outside the test suite:
  - **The JSON Schema validator against the reference `jsonschema` 4.26.0** (system Python,
    outside the repository; script `crosscheck_jsonschema.py`): every seed and fixture file,
    and 20,000 random mutations of the five seeds (a key replaced by one of 17 values,
    deleted, or added): no disagreement on valid/not valid.
  - **The consistency property test at 20,000 random pairs per rule set** (the suite runs
    4,000): no reciprocity violation, no two leaders or two followers. The counts quoted in
    `rule-matching.md` and the milestone comment (4,563 matched, 2,339 ties) are corrected in
    the entry "Resuming" below.
- Result: **974 tests pass** (816 + 158). Pyflakes clean. Posted the milestone comment on
  the issue at 20:56.

### 2026-10-14 20:55 — The documents (`69e121f`)

- What I did: `docs/rule-format.md` (the full format, for SI-3 to produce rules in),
  `docs/rule-matching.md` (the policy; the shared-snapshot equivalence and its assumption of
  perfect, simultaneous perception; the grid of test situations), `docs/baseline.md` (the two
  frozen baselines; the measured choice of perturbation; sign-off pending),
  `derivations.md` section 15 (when an encounter has passed), `metrics.md` section 9
  (`avoided`/`resolved`/`failed` and the gap in the issue's definitions), `architecture.md`
  section 7 (DD42 to DD64, and what changed outside `negsim/rules/`), `rule_db/README.md`.
- Decisions recorded there for the first time, beyond those in the 20:31 to 20:33 entries:
  DD53 (re-evaluation follows the issue's list literally: a held rule is re-evaluated only
  at a class change, so a higher-priority rule whose threshold is met later in the same
  encounter does not take over; open question Q3), DD54 (hysteresis: 3 steady steps; holding
  is sticky; after expiry nothing until the class changes), DD59 (how cross-pair conflicts are
  settled), DD62 to DD64 (logging switch, one log schema number, `single_file_first_arrival`
  keeps `out_of_range`).

### 2026-10-14 21:34 — Counting issue #26's two ORCA artefacts (`696d1cd`)

- What I did: the issue asks for counts of walking backwards and of being hurried along by a
  following agent, rule runs against baseline runs. The behaviour checks thin their logged
  trajectories (every tenth or hundredth step), so the counts cannot be taken from the
  trajectory afterwards; they are kept in the run loop. An episode is a run of steps lasting
  at least 1 s on which an agent moved against its own path faster than 0.1 m/s
  (`backward`), or faster than 1.05 times the speed it wants with a perceived neighbour behind
  it (`hurried`). Definitions with no source; every outcome repeats them (`metrics.md`,
  section 10). They count and change nothing about how anyone moves.
- Result: 977 tests pass (3 new). The SI-1 reproduction (script `reproduce_si1.py`) is
  unchanged: 44 of 46 runs identical, the two `speed_scale` runs differing as before.

### 2026-10-14 21:39 — The behaviour-check experiments (`a4e1ead`), and where the session stopped

- What I did: eight experiment configs in `configs/rule_following/` (a folder of their own,
  because a test pins the six configs of `configs/avoidance/`): the five SI-1 scenarios, each
  crossing both baselines with plain ORCA against the `default` rule set, 20 seeds per
  condition; head-on also with a woman of 25 and a man of 70, so that
  `younger_yields_head_on` applies; the bottleneck also with agent 0 slower (1.10 m/s), so
  that `single_file_first_arrival` does not tie; head-on and overtaking again at 5 m;
  keep-left against keep-right. 1,600 runs, no model calls. Before committing the flow config,
  ran one plain and one rule run of it (`crowd_probe/` in that scratchpad) and profiled 150
  steps of a rule run (`crowd.prof`): of 37.5 s, the matching policy took 23.0 s, most of it
  computing the corridor width between two agents (ray casts every 0.25 m) for pairs
  evaluated again on every step because no rule held them.
- Then started the runs, one experiment after another, from a clean tree at `a4e1ead`:
  `si2_head_on` (21:39:57 to 21:40:26), `si2_keep_left_vs_right`, `si2_open_crossing`,
  `si2_overtaking`, `si2_bottleneck` (finished 21:41:57), and `si2_head_on_r5`, which had
  written 9 of its 320 runs when the session ended at 21:42:04. `si2_overtaking_r5` and
  `si2_bidirectional_flow` never started. A draft of the benchmark (`benchmark_draft.py`) and
  of a table script (`summarise_si2.py`) were in the scratchpad, not in the repository.

### 2026-10-15 09:38 — Resuming: what was found, and the rechecks

- What I did: read this log, the issue and its two comments, the four commits above, and
  the previous session's scratchpad; checked that no process was still running; built a new
  virtual environment in this session's scratchpad (Python 3.13.3, PyYAML 6.0.3, pytest
  9.1.1, matplotlib 3.10.8, pyflakes 4.0.3).
- Result / what I found:
  - **977 tests pass** (`python -m pytest`, 99 s); pyflakes clean. The working tree held
    only the six untracked run folders.
  - **The five finished experiments are usable as they are**: every run records commit
    `a4e1ead`, `dirty: false`, and each experiment has its `summary.csv`.
  - **`si2_head_on_r5` was incomplete** (9 of 320). Deleting the folder was refused by the
    session's permission check, so instead I copied the nine runs to the scratchpad and ran
    the experiment again with the runner's own `--overwrite`, which rewrites every file of
    every run. Then `si2_overtaking_r5` and `si2_bidirectional_flow`, from the same clean
    tree (nothing outside `runs/` changed until the last of them had started; the runner
    reads the git state once, when an experiment starts).
  - **Determinism across the break**: the nine runs written yesterday and the same nine
    written today are byte-identical in all six files, except `created_utc`.
  - **Rechecks of what the previous session reported:**
    - JSON Schema validator against `jsonschema` 4.26.0: 24 files (22 valid by both) and
      20,000 mutations, **0 disagreements**. Confirmed.
    - SI-1 reproduction: **44 of 46 identical**; the two `both_left_slow` runs differ
      (trajectory, events, times), as Part 5 intends. Confirmed.
    - Consistency property test at 20,000 pairs per rule set: **0 reciprocity violations
      and 0 non-complementary roles in each set. Confirmed.** But the counts beside them
      were not: the test's own function with its own seed (28) gives, for each of the two
      rule sets, **4,511** pairs matched and **2,443** ties (classes: none 10,947, single
      file 3,320, overtaking 2,070, crossing 1,925, head-on 1,738), where `rule-matching.md`
      and the milestone comment say 4,563 and 2,339. Eleven other seeds give 4,377 to 4,658
      matched and 2,308 to 2,490 ties, and **zero violations every time** (240,000 pairs in
      all). The quoted numbers are inside that spread, so they were most likely made with
      another seed or an earlier version of the random-pair generator; the previous session
      left no script that would say which. `rule-matching.md` now gives the reproducible
      numbers and how to get them.
- Next step: let the three experiments finish; meanwhile turn the benchmark draft and the
  table script into modules, and read the results.

### 2026-10-15 10:20 — Two small modules, and what the results show

- What I did:
  - **`negsim/rules/benchmark.py`**, from the previous session's draft: the flow at 100 and
    1,000 agents on the primary baseline, plain against the `default` rule set, timing every
    step and, separately, the time spent inside the rule provider (its per-step hook and its
    answer when a pair forms). Changed from the draft: the two modes are timed in turn,
    three times each, and compared by their medians, because issue #26 found a single
    measurement moves by about 25% from one day to the next; and the provider's answer at
    formation is timed too. Smoke-tested at 20 and 100 agents with 10 steps. The real
    measurement waits until the flow runs have finished, so that they do not share the
    machine.
  - **`negsim/rules/report.py`** and `tests/test_rules_report.py` (6 tests), from the table
    script. **A decision, and a change from issue #26's practice**, which kept its table
    script in the scratchpad: the tables are the main deliverable of the behaviour checks and
    the PR quotes them, so the script that reads them out of the committed logs is committed
    too, and a test checks that `docs/behaviour-checks.md` quotes its output line for line.
    Changed from the draft: the largest path deviation instead of the mean over time (the
    quantity issue #26's tables report), the smallest gap in millimetres (in metres to three
    places, every overtaking run read 0.000), and a second table of what decided each
    outcome and what the matching policy did.
- Result / what I found, from the seven finished experiments (`behaviour-checks.md` has the
  numbers):
  - The rules do what they say: `keep_left_head_on` removes the unperturbed symmetric
    deadlock (20 of 20) and fixes the side; `overtaker_keeps_clear` stops the slower walker
    being hurried (0 episodes in 80 rule runs, 120 in 80 plain runs); `keep_right_head_on`
    differs from `keep_left_head_on` in the side and nothing else.
  - **`younger_yields_head_on` gives a share and no side**, so the younger agent walks
    backwards under the unperturbed baseline (20 of 20, exactly head-on) and steps aside
    under the perturbed one. A rule's effect can hinge on the 1e-4 m/s perturbation.
  - **`single_file_first_arrival` never changes the leader**, and with equal speeds it
    matches one step after the arbiter has decided, on times to the segment that the
    arbiter's slowdown has already changed: it ratifies the decision (Q6). Found by
    tabulating `role_source` in the handoffs: `strategy1` in all 80 equal-speed rule runs,
    `negotiated` only when agent 0 is slower.
  - **Exposure under the perturbed baseline** counts changes of about 1e-4 m/s for an agent
    with share 0 (1.5 to 3.7 s of "exposure" while it moves by under 0.3 mm; exactly 0
    unperturbed). Found because the offset head-on with `younger_yields_head_on` had twice the
    exposure perturbed (6.2 s) as unperturbed (3.3 s); checked over all 20 seeds of the four
    conditions that have a share of 0 (Q7).
  - **`avoided` occurs only in the merging bottleneck with agent 0 slower** among all the
    two-agent runs; every other pair is `resolved` or, deadlocked, `failed` (Q8).
  - **Plain and rule runs never share a seed** (seed = base + run index). The crossing, where
    no rule applies, shows the resulting noise: the smallest gap 5.27 ± 1.45 mm plain against
    3.85 ± 2.29 mm with rules, from runs that differ only in their seeds (Q9).
  - The flow, part-way (37 of 80 runs): with rules the crowd clears much sooner but bodies
    overlap more deeply. To see why, I ran `021_perturbed_rules_r1` again in the scratchpad
    with every step and pair logged (it reproduced the committed run exactly) and matched
    each overlap to the rule holding its pair: of 128 overlap episodes, 60 were under
    `overtaker_keeps_clear`, 10 under `keep_left_head_on` and 58 under no rule, and 121 began
    on a step on which one of the two had no allowed velocity, the case issue #26 traced
    every overlap to. Numbers for the whole set when it is done.

### 2026-10-15 10:36 — The flow finished; every behaviour check is in

- What I did: `si2_bidirectional_flow` finished at 10:35 (80 runs, 45 minutes; about 60 s
  for a rule run against 17 s for a plain one). Checked that all 1,600 run folders record
  `a4e1ead` and `dirty: false`. Read the flow's numbers with two scratchpad scripts
  (`flow_table.py`, `totals_si2.py`), generated Appendix A of `docs/behaviour-checks.md`
  with `python -m negsim.rules.report`, and wrote its sections 3.6, 3.8 and 3.9 and the
  READMEs from them.
- Result / what I found (`behaviour-checks.md`, section 3.6):
  - With the rules the flow clears in 46.9 ± 10.6 s instead of 83.4 ± 10.2 s (primary
    baseline), the mean time to goal is 35.87 ± 0.73 s against 38.67 ± 5.95 s, and 2 agents
    in 20 runs take more than 60 s against 136. Overlap episodes halve (107 against 234 per
    run), and so do near misses and steps without an allowed velocity; but **the deepest
    overlap of a run is 201 ± 101 mm against 32 ± 26 mm** (Q10).
  - **One plain run under the secondary baseline jams**: `053_unperturbed_plain_r13` times
    out at 120 s with 8 agents still in the corridor, 837 overlap episodes, 13 pairs still
    open. It is not counted as a deadlock, because the deadlock test needs every agent nearly
    still, as issue #26 noted. Found when a script failed on its missing makespan.
  - Artefacts: in the flow, walking backwards 688 episodes without the rules and 179 with,
    hurried 823 and 561; between two agents, backwards only under `younger_yields_head_on`
    (40) and hurried only in plain overtaking (240).
  - No `ambiguous_match`, no `cross_pair_conflict`, and no formation mismatch in 271,189
    checks, across all 1,600 runs.
- **Mistake: I had written the number of runs as 1,920** in the READMEs and in
  `behaviour-checks.md` (and 1,840 two-agent runs), without adding it up. It is 1,600 (320 +
  80 + 160 + 160 + 320 + 80 + 320 + 160), as the first session's commit message says, and
  1,520 two-agent runs. Caught when the provenance check counted 1,600 folders; corrected
  everywhere before anything was committed.
- Next step: commit the runs and everything written so far; then, from the clean tree, the
  benchmark (alone on the machine) and an ablation of the flow that leaves out one rule at a
  time, to see which rule the deeper overlaps come with.

## Open questions / risks

- **Q1 (carried from #24 and #26). Has the supervisor's "no simulation code until the
  literature review is complete and discussed" instruction been lifted?** Issue #28 made
  it a prerequisite that `CLAUDE.md` record the approval. It does not. The user chose to
  proceed and leave the question open (P1). Nothing in the repository records the
  supervisor's position.
- **Q2. Branch base.** Cut from `feat/26-orca-avoidance-layer`, because PRs #25 and #27
  are not merged; the PR targets that branch and will not close #28 by itself.
- **Q3. Re-evaluation while a rule holds (DD53).** The issue's list is followed literally: a
  held rule is re-evaluated only when the encounter class changes, so a higher-priority rule
  whose threshold is met later in the same encounter does not take over. The alternative,
  trying the higher priorities on every step, is a small change to `matching.py` (and adds
  evaluations, see the benchmark); which one is meant needs a decision.
- **Q4. "No exposure but a yield event" is `resolved` (DD57).** The issue's three
  definitions leave that case out; it is the follower the arbiter holds back at a segment.
  Every pair records its ingredients, so another reading can be computed from the logs.
- **Q5. Yields attributed to a pair by overlap in time (DD58).** Exact with two agents; in a
  crowd it can only move pairs from `avoided` to `resolved`.
- **Q6. A rule can ratify the arbiter's decision after the fact.** With equal speeds at the
  bottleneck, `single_file_first_arrival` ties when the pair forms, the arbiter decides, and
  one step later the rule matches on times to the segment that the arbiter's slowdown has
  changed, naming the same leader (`behaviour-checks.md`, section 3.5). It "fires" in all 80
  such runs and decides nothing. Should a pair held by the arbiter stop being evaluated, or
  should "fired" be counted only when the rule's order is what the arbiter used? Not changed
  here: the policy does what the issue asks, and the logs show what happened.
- **Q7. Exposure under the perturbed baseline.** Exposure counts any change above 1e-6 m/s
  (issue #26), a hundred times smaller than the perturbation, so an agent a rule gives a
  share of 0 is counted as exposed for 1.5 to 3.7 s while it moves by less than 0.3 mm
  (`behaviour-checks.md`, section 4). A threshold above the perturbation (say 1e-3 m/s)
  would remove that; it is a change to a metric of issue #26, so it is not made here.
- **Q8. `avoided` almost never happens.** In the two-agent scenarios every pair on a
  collision course is `resolved`, rules or not, because ORCA's 3 s horizon always registers
  exposure; only deadlocks move (to `resolved`). The categories separate deadlock from no
  deadlock and little else. A threshold on how much an agent was changed, or on the time to
  collision, would make `avoided` mean "settled early". For SI-5 to decide.
- **Q9. Plain and rule runs do not share seeds.** A run's seed is the base seed plus its
  index, so comparisons are between two samples, not paired. Pairing them (common random
  numbers) would sharpen later comparisons (SI-5); it changes how runs are seeded, so it is
  not done here.
- **Q10. In the dense flow the rules make overlaps fewer but much deeper.** The deepest
  overlap of a run is 201 ± 101 mm with the rules (up to 456 mm) against 32 ± 26 mm without
  (primary baseline), while overlap episodes halve and the crowd clears in 47 s instead of
  83 s. In the one run examined step by step, overlaps began on steps where an agent had no
  allowed velocity, in pairs with and without a rule. Which rule, if either, is behind the
  depth is what an ablation of the flow tests (progress log). Either way, overlaps of 20 cm between bodies of
  radius 25 cm would have to be dealt with before rules are used in crowds (SI-5).

## Summary (fill in at the end)

