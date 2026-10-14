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

## Open questions / risks

- **Q1 (carried from #24 and #26). Has the supervisor's "no simulation code until the
  literature review is complete and discussed" instruction been lifted?** Issue #28 made
  it a prerequisite that `CLAUDE.md` record the approval. It does not. The user chose to
  proceed and leave the question open (P1). Nothing in the repository records the
  supervisor's position.
- **Q2. Branch base.** Cut from `feat/26-orca-avoidance-layer`, because PRs #25 and #27
  are not merged; the PR targets that branch and will not close #28 by itself.

## Summary (fill in at the end)

