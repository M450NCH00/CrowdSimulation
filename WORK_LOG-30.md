# Work Log — Issue #30: [Feature] SI-3a: conflict cases, rule-generation protocols, and rule writer (mock rehearsal and pilot)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/30
**Branch:** `feat/30-conflict-cases-rule-generation`
**Started:** 2026-10-15 15:41 (UTC+8)

## Understanding the issue

This is the third of the six sub-issues of #26 (SI-3), split in two; this is SI-3a. SI-1
(#26) built an ORCA avoidance layer whose agents follow per-neighbour directives; SI-2 (#28)
made those directives come from stored rules (a declarative rule format, a frozen rule
database, a matching policy, two frozen baselines). Nothing yet turns a conflict into a
**new** rule. This issue builds that pipeline and rehearses it end to end on the mock
client; SI-3b will run the paid collection and the evaluation.

Two ways of generating a rule from the same conflict case are to be compared later:

- **Condition A (negotiated).** Two LLM agents, each seeing the case first-person plus its
  own private information (a task), negotiate a standing rule for future encounters in turns
  of `{message, proposal, accept}`; agreement is accepting the other's latest proposal by its
  canonical hash.
- **Condition B (stated).** One LLM sees both agents third-person (both agents' private
  information) and states a rule; K repeats measure stability.

What has to exist at the end, by part:

1. **Fixes the pipeline depends on.** (1.1) A pair-level conflict measure, *pair exposure*:
   the time the two agents' intended velocities (after directives, before ORCA's projection)
   put them inside each other's truncated velocity obstacle; it does not depend on
   responsibility shares, unlike #26's per-agent exposure. Severity tiers T0 to T4 per pair
   interaction, beside #28's avoided/resolved/failed. Thresholds in config and docs. (1.2)
   Paired seeds: a baseline run and a rule run of the same scenario instance use the same
   seed; a test that a rule run with no rule reproduces the baseline trajectory exactly.
   (1.3) Rule schema version 2 (`source_type: stated`, `intent`, `screening`); version 1
   files load unchanged. (1.4) The viewer shows which rule fired for each pair and labels
   directives correctly.
2. **Conflict cases** extracted from primary-baseline runs on the five SI-1 scenarios:
   tier T1 and above, sampled stratified by tier and scenario, stored as immutable,
   versioned JSON with stable ids and a manifest under `llm_negotiation/cases/`.
3. **A persona design matrix** (age pair, gender pair, task, demographics visible or not,
   persona-to-agent mapping, speaking/description order): balanced, reproducible, seeded,
   no names.
4. **Situation descriptions**: deterministic, frozen templates covering all five scenario
   types; first-person (no non-observable information about the other) and third-person;
   neutral wording; a generated field glossary; a meaningless placeholder as format example.
5. **Condition A protocol**, reusing #24's dialogue loop, limit, retry and transcripts.
6. **Condition B protocol**, K repeats, stability by canonical hash.
7. **Validation**: every proposed rule through the existing loader, categorised as valid,
   needs communication, inconsistent, schema error or format limit, nothing discarded.
8. **A rule writer** that writes only to a per-experiment staging database, assigns ids and
   provenance itself (ignoring anything the model writes there), deduplicates by canonical
   hash, and a promotion command that requires a reason (no rule promoted here).
9. **Single-rule replay** on the case's own scenario with paired seeds, and **crowd
   screening** of each valid rule alone in `bidirectional_flow`, results stored on the rule.
10. **A rule-generation experiment type** driven by YAML: budget guard and ledger, a
    worst-case cost preview with explicit confirmation before any paid call, full logging,
    and a mock client that exercises every path.
11. **A paid pilot** (USD 0.05 cap). **Held** in this session (P1 below).

### Decisions taken in the issue (the user's defaults; recorded as decisions)

- **Offline generation**: rules come from cases taken from finished runs; no live
  negotiation during a run.
- **Equal information**: A and B get the same situation information, neither sees what
  happened under plain ORCA; they differ only in perspective (A: own private information;
  B: both agents' private information).
- **Output form**: both conditions produce a full rule in the rule format, validated by the
  existing loader.
- **Rules needing private information** (*supervisor*): rejected and recorded as "needs
  communication"; the format is not extended to read private information.
- **Clashing rules**: generated rules are never enabled together here; each is evaluated
  alone. Combining rules is SI-4.
- **Q3** (a rule with a timing condition losing to an earlier match): deferred to SI-4; it
  only arises when rules are combined.
- **Q11** (matching cost): deferred; single-rule replay keeps one rule enabled.

### Prerequisites (checked before anything else)

- **P1. `CLAUDE.md` must record that the supervisor has approved simulation work (Q1 of
  `WORK_LOG-28.md`) — FAILED.** No branch's `CLAUDE.md` records an approval (checked on every
  remote branch: only `docs/5-biweekly-update-1` mentions the instruction, and it states the
  "no simulation/experiment code" instruction itself). `README.md:26-32` still marks that
  instruction "unconfirmed (2026-10-13)". The issue makes this a hard stop because it spends
  money, so I stopped and asked the user. **The user's answer (2026-10-15, in this session):
  "Mock-only, hold the pilot"** — build and verify Parts 1 to 10 on the mock client at zero
  spend, and stop before the pricing check and the USD 0.05 paid pilot (Part 11) until the
  approval is recorded in `CLAUDE.md`. Nothing in `CLAUDE.md` is changed by me to claim
  approval.
- **P2. PRs #25, #27 and #29 merged, and this branch created from `main` — FAILED.** PRs #25
  and #27 are merged (2026-10-15 06:43 UTC), but into their stacked base branches
  (`docs/22-simulation-conflict-rules-literature` and `feat/24-llm-negotiation-simulator`),
  not into `main`. PR #29 is open (base `feat/26-orca-avoidance-layer`, mergeable). `main`
  (`5a0f7be`, 2026-09-06) has no `llm_negotiation/` at all; 96 commits of
  `feat/28-rule-format-database-following` are not on it. Also, #25 was merged before #27, so
  `docs/22-…` has `feat/24`'s work but not `feat/26`'s. As the issue instructs, I stopped and
  asked rather than stacking a fourth PR. **The user's answer (2026-10-15, in this session):
  "Stack on #29's branch"** — this branch is cut from `feat/28-rule-format-database-following`
  at `ec10073`, and the PR will target that branch (so it will not close #30 on merge).
- **P3. Pricing check before any paid call.** Not reached: no paid call is made in this
  session (P1).

## Plan

Written before writing code; the progress log records where it changes. Baseline first:
**984 tests pass** (`python -m pytest` in `llm_negotiation/`, 169 s, in a fresh virtual
environment in the session scratchpad: Python 3.13.3, PyYAML 6.0.3, pytest 9.1.1,
matplotlib 3.10.8, pyflakes 4.0.3); pyflakes clean.

1. **Pair exposure and tiers (1.1).** In the run loop, after every agent's intended velocity
   is fixed and before anyone moves, test each open pair: is `v̂_i − v̂_j` inside the truncated
   velocity obstacle of the two bodies (radii only, horizon τ) by more than a tolerance?
   Count per pair. Tiers from the pair's own exposure, yields, near misses, collisions and
   deadlock. Thresholds in `MetricThresholds` (scenario `metrics:`) and every outcome. Log
   schema version 4. Derivation (`derivations.md`), definitions (`metrics.md`), and how each
   directive field acts (before or inside the projection). Tests: tiers, the measure against
   hand-computed cases, independence from shares (same state, any shares), recomputation
   from the trajectory log.
2. **Paired seeds (1.2).** `design.seeding: paired` (the new default): a run's seed is the
   design's base seed plus its repeat number, the same for every level; `per_run` keeps #26
   and #28's base-plus-index, and their committed configs are pinned to it so that they stay
   reproducible. Test: a baseline run and a rule run with no rule enabled write identical
   trajectories.
3. **Rule schema v2 (1.3).** `rule.v2.schema.json` beside v1, frozen in the manifest; the
   loader picks the schema by the rule's `schema_version`; `Rule` gains `intent`,
   `screening`, `schema_version`; `history` compares them. Migration notes in
   `rule-format.md`.
4. **Viewer (1.4).** Rule runs: which rule fired for each pair (an event per match, with the
   roles and directives), the provider labelled as rules, not "plain ORCA".
5. **Canonical form and hash** (`negsim/rules/canonical.py`), documented for SI-4.
6. **Cases (Part 2).** Baseline source experiments on the five SI-1 scenarios (primary
   baseline, paired seeds, a few geometries each), an extractor (eligibility T1+, stratified
   sampling by configurable strata, seeded), and a case store with a SHA-256 manifest
   (`llm_negotiation/cases/`). Commit the source runs and the cases.
7. **Design matrix (Part 3).** Factors and levels from config, per-case restrictions,
   balanced full factorial, deterministic session ids, seeded order.
8. **Descriptions (Part 4).** Frozen templates (new `kind`, frozen with the existing tool),
   first- and third-person renderers for all five scenario types, the glossary generated from
   `rule-format.md` section 5 and the rule schema (its hash pinned in the template), a
   placeholder format example.
9. **Protocols (Parts 5, 6).** Extract the ask-and-retry core of #24's `Dialogue.take_turn`
   into a function both use; condition A (turn parsing, proposal ids, agreement, counter-
   proposals, "no rule without talking", outcomes); condition B (K repeats, stability).
10. **Validation (Part 7)**, with a fixed precedence among the categories.
11. **Writer, staging database, promotion (Part 8).**
12. **Replay and screening (Part 9).**
13. **Experiment type (Part 10)**: config, case selection, sessions, validation, writer,
    replay, screening, logging, cost preview and confirmation, experiment-scoped budget cap,
    mock policies for every path, the command line.
14. **Pilot (Part 11)**: the config and its cost preview only; not run (P1).
15. **Docs**: `metrics.md`, `derivations.md`, `rule-format.md`, `architecture.md`,
    `log-schema.md`; new `cases.md`, `rule-generation.md`, `pricing-check.md`; READMEs.
16. **Verify**: full suite with the network blocked, pyflakes, an end-to-end mock run, a
    search for the API key; push; PR into `feat/28-rule-format-database-following`.

## Progress log

### 2026-10-15 15:41 — Prerequisites checked; branch created

- What I did: read `github_issue_workflow.md` and the issue; checked P1 and P2 (above);
  asked the user; created `feat/30-conflict-cases-rule-generation` from
  `feat/28-rule-format-database-following` (`ec10073`).
- Why: both prerequisites are hard stops in the issue.
- Result / what I found: both failed; the user chose to proceed mock-only and to stack.
- Next step: read the code and documents of #24, #26 and #28 that this issue builds on, then
  fill in the understanding and the plan.

## Open questions / risks

- **Q1 (carried from #24, #26, #28). Has the supervisor's "no simulation code until the
  literature review is complete and discussed" instruction been lifted?** Not recorded in
  `CLAUDE.md`. The paid pilot (Part 11) is held until it is.
- **Q2. Branch base.** Stacked on PR #29's branch (P2).

## Summary (fill in at the end)

<What changed, why, how it was verified.>
