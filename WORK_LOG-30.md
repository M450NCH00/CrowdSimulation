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

### 2026-10-15 16:24 — Part 1 done: pair exposure, tiers, paired seeds, schema v2, viewer

- What I did: read `WORK_LOG-28.md`, every document under `docs/` that this issue names, and
  the code of the run loop, perception, directives, the rule package, the experiment runner,
  the LLM layer, the negotiation protocol, the log schema and the viewer. Built the scratchpad
  virtual environment and took the baseline (984 passed). Then Part 1, in three commits
  (`99abe41`, `c89e58f`, `71f57b3`):
  - **1.1 Pair exposure and tiers.** `negsim/avoidance/exposure.py` (the obstacle depth, using
    ORCA's own `agent_half_plane` geometry, so `orca.py` is unchanged); the run loop records
    each agent's intended velocity and tests every open pair before anyone moves; tiers in
    `negsim/metrics/avoidance.py`; log schema version 4; `metrics.md` section 11,
    `derivations.md` section 16.
  - **1.2 Paired seeds.** `design.seeding: paired` (default) or `per_run`; the 15 committed
    configs of #26 and #28 pinned to `per_run`; `baseline.md` section 6.
  - **1.3 Schema v2**, frozen in the manifest; the loader dispatches on `schema_version`
    (`RuleSchemas`); `rule-format.md` sections 12 and 13. The canonical form
    (`negsim/rules/canonical.py`) was written here too, since section 13 defines it.
  - **1.4 Viewer**: rule runs were labelled "plain ORCA (no directives)" for every agent.
- Why: the issue's Part 1 is what the rest depends on (tiers for case eligibility, paired
  seeds for replay, schema v2 for the writer).
- Result / what I found:
  - **1037 passed** (53 new), pyflakes clean. Eight existing tests changed, each because it
    pinned what the issue changes (log schema version 3 in four places, the exact
    `interaction_outcomes` and `scenario.metrics` dicts, the per-run seeds of one design,
    and three documentation checks); #28's A2 reading applies (the issue wins, no regression).
  - **How each directive field acts** (checked in the code, `metrics.md` 11.1):
    `speed_scale` and `passage_order` act on the intended velocity (before the projection);
    `side_preference` and `responsibility_share` only inside the projection and only on a
    collision course; `clearance_margin` only inside the projection but on every step.
    **Consequence:** a rule of sides and shares cannot make a pair T0 where the baseline put
    it on a collision course; on the same seed its first exposed step is the baseline's
    (tested: the two runs are identical before that step and diverge on it).
  - **Plain ORCA's two-agent passes are T3**, not T1: ORCA passes the bodies within a few
    millimetres, inside the 0.1 m near-miss distance. Under the primary baseline, one seed
    each: head-on, crossing, overtaking, bottleneck all T3. A clearance margin of 0.15 m
    takes the head-on to T1; offsets of ±0.26 m give a T3 near miss with no pair exposure
    at all; ±0.3 m, a staggered crossing, a 0.6 m overtaking offset, a merging bottleneck
    give T0. So T1 and T2 cases will be rare in the two-agent baselines; the crowd should
    supply them. Recorded in `metrics.md` without a claim I have not checked over seeds.
  - A bug of my own, found by the tests: a number that rounds to a whole number at 12
    significant digits stayed a float in the canonical form (20.000000000001 gave `20.0`,
    not `20`), so two equal rules could hash differently. Fixed: round first, then test for
    a whole number.
  - A test of my own was wrong first (a brute-force distance that skipped rays which cross
    the obstacle and leave it); the measure was right (0.380 m/s, checked by hand).
- Decisions (numbered on from #28's DD64; `architecture.md` will list them):
  - **DD65.** Tiers are the conflict classification from #30 on; #28's categories are kept
    exactly as defined (per-agent exposure) for continuity, with `pair_exposed` logged so
    they can be recomputed on pair exposure.
  - **DD66.** Paired seeding is the default; committed configs pinned to `per_run`.
  - **DD67.** Pair exposure: the bodies' obstacle (no clearance margin), the larger of the two
    horizons, depth tolerance 1e-3 m/s (five times what the perturbation can move the
    relative velocity), overlapping bodies exposed.
  - **DD68.** `collision_course_min_s` = 0 s: T1 is any exposed step, so T0 is exactly "no
    exposure" as the issue words it; it is a setting.
  - **DD69.** The canonical form: the keys `encounter`, `when`, `roles`, `directive`, and
    `expiry` if stated; no unit conversion, no reordering of lists, no removal of fields at
    their baseline values; numbers to 12 significant digits; proposal id = 12 hex
    characters. `expiry` is included because it changes how long the directive applies; the
    issue names "condition, roles, and directive".
- Next step: conflict cases (Part 2): case-source baseline runs on the five scenarios, then
  the extractor and the store.

### 2026-10-15 16:26–16:48 — Parts 2 to 4: cases, the design matrix, the descriptions (logged afterwards)

- **How this entry was written.** The session that did Parts 2 to 4 committed them
  (`c644294`, `0e34feb`, `bac47d5`, `4bab440`, `47c44fb`) but ended before it logged them.
  This entry was written on 2026-10-16, in the next session, from those commits, their
  messages and the documents they added, not from a memory of the work. Nothing is claimed
  here that those do not show.
- What was done:
  - **Part 2, conflict cases** (`docs/cases.md`). Five case-source experiments on the primary
    baseline, one per SI-1 scenario, under `configs/cases/` (26 runs, paired seeds, layouts
    varied in the two-agent scenarios because their tiers depend on the geometry, not the
    seed); the extractor and the frozen case store (`negsim/rulegen/cases.py`, a SHA-256
    manifest, stable ids, a case set with its extraction report); case set `si3_v1`, 18 cases
    (`configs/cases/si3_cases_v1.yaml`). Of 9,689 pair interactions, 210 were eligible.
    Decisions **DD70** (a pair that formed one-sided is not eligible) and **DD71** (a pair
    must be approaching when it forms), both in `cases.md`.
  - **Part 3, the persona design matrix** (`negsim/rulegen/design.py`): six factors (age
    pair, gender pair, task, demographics visible, mapping, order), crossed in full per case
    and condition, ids derived from what a session is, the order shuffled by the seed, no
    names.
  - **Part 4, the situation descriptions** (`negsim/rulegen/describe.py`): three templates
    frozen with #24's tool (`rulegen_common_v1`, `rulegen_negotiate_v1`, `rulegen_state_v1`),
    first- and third-person renderers for the five scenario types, the field glossary
    generated from the field catalogue and the rule schema with its SHA-256 pinned in the
    common template, a placeholder format example.
- Result: 67 tests added (11 for cases, 15 for the design, 41 for the descriptions); 1,037
  after Part 1 plus 67 is the 1,104 that pass at the start of the next session (below).
- Two things the commits left unrecorded here: `cases.md` cites "open question Q4 of
  `WORK_LOG-30.md`", which this log did not have; it is added below, as is a Q3 for the
  Part 1 finding that plain ORCA's ordinary pass is a near miss. Both numbers were given in
  the 2026-10-16 session.

### 2026-10-16 09:15 — Session resumed: what was left, and what an end-to-end run found

- What I found: the branch at `47c44fb` (Parts 1 to 4), and in the working tree, uncommitted
  and untested, the code of Parts 5 to 10 written at the end of the last session: six new
  modules (`negsim/rulegen/protocol.py`, `validate.py`, `writer.py`, `replay.py`, `mock.py`,
  `experiment.py`) and changes to three (#24's dialogue loop split out as
  `request_with_retry`; a budget guard scoped to one experiment; a way to reload a rule
  database). No tests, no command-line wiring, no experiment configs, no documents.
- What I did first: a fresh virtual environment in this session's scratchpad (Python
  3.13.3, PyYAML 6.0.3, pytest 9.1.1, matplotlib 3.10.8, pyflakes 4.0.3); **1,104 passed**
  with the uncommitted code in place (233 s); pyflakes found three unused imports. Then an
  end-to-end mock run in the scratchpad (2 cases, 48 sessions) before writing any test.
- What it found (each fixed, and each now has a test):
  1. **Replay crashed** on a run folder path of 261 characters: Windows' limit is 260. The
     folder names repeated the rule id twice. Now `replay/<rule_id>/baseline` and `.../rule`.
  2. **The model was told something false.** After a counter-proposal (an `accept` of the
     other's latest id written beside a different rule), the other agent was told "They put
     <id> under "accept", which is not the id of your latest proposal" when it *was* that
     id. That line is now shown only for a stale, own or unknown id; a counter-proposal is
     shown as the new proposal it is.
  3. **The manual-review phrase "the faster"** flagged every rule that orders the two by
     speed ("the faster one does the avoiding"), which says nothing about scaling. The
     phrases are now patterns (scaling, "the more ..., the more ...", a rate, more than two
     people); "%" and "percent" are gone.
  4. **Running an experiment again crashed**: replay and screening rewrote the next rule
     version with new timestamps, which the frozen staging database refuses. Writing,
     replay and screening are now idempotent, and a rule that more sessions support later is
     stored as its next version.
  5. Smaller: the stored rule took its words and priority from whichever session came first
     in the shuffled list (now the earliest, documented, since the canonical form leaves
     them out); its author named the model asked for, not the one that replied (a mock run
     said "from deepseek-flash"); the output bound used the reply cap plus a wrapper (now the
     cap, as the issue's formula says); a paid client was built, needing the API key, before
     the run was confirmed; resuming overwrote the log of an aborted session; a changed config
     could be resumed into the same folder; `screening.jsonl` was rewritten with only the
     latest invocation's entries; a scoped budget guard let an unlabelled call escape its
     cap; formulas were told from constants by arithmetic alone, so "1/2" (a constant
     written oddly) was a format limit while "0.6 per year" and "left if older" (values that
     depend on something) were schema errors.
- Why the order: running the whole pipeline once before writing tests found bugs that unit
  tests of the parts, written to the code as it stood, would have encoded.
- Next step: tests for Parts 5 to 10, the command line, the configs, then the documents.

## Open questions / risks

- **Q1 (carried from #24, #26, #28). Has the supervisor's "no simulation code until the
  literature review is complete and discussed" instruction been lifted?** Not recorded in
  `CLAUDE.md`. The paid pilot (Part 11) is held until it is.
- **Q2. Branch base.** Stacked on PR #29's branch (P2).
- **Q3. Is the near-miss distance right for ORCA?** Plain ORCA passes two bodies a few
  millimetres apart, inside the 0.1 m near-miss distance (`metrics.md` section 5, a
  `[design]` value), so under the primary baseline every eligible two-agent pair is T3 and
  T1, T2 and T4 cases come only from the crowd (`cases.md`, section 2). Either that is the
  finding (ORCA's passes are near misses by a human standard), or the distance should be
  tied to a cited personal-space figure. A question for the supervisor; nothing was changed.
- **Q4. The one-sided-formation rule is a selection** (DD70, `cases.md` section 2): of the
  flow's 2,224 pairs at T1 or above, 1,727 formed one-sided and are not eligible, so the crowd
  cases favour pairs that came into each other's view at the same step. Whether that biases
  what rules are generated is untested.

## Summary (fill in at the end)

<What changed, why, how it was verified.>
