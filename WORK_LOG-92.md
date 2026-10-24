# Work Log — Issue #92: RF-26: round 1, real ethnicity as a factor (Singapore's ethnic groups at their resident shares), replacing the fictional group (mock only)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/92
**Branch:** feat/92-real-ethnicity-factor
**Started:** 2026-10-24

## Understanding the issue
The resolution layer (track #55) has no group factor: the fictional group of #32 lives only in
the rule-generation layer. The user decided on 2026-10-24 that real ethnicity replaces it in this
track: Singapore's four census groups at their resident shares (SingStat, *Population Trends
2026*). RF-10's screen needs a two-level factor, so the factor is `ethnicity_pair` (`same` or
`different`), and each session's two groups are drawn with the design's seed so that the
population's real mix is kept. An agent is told its own ethnicity, and the other's ("They look
Chinese.") when `ethnicity_visible` is on. The outcome rows and RF-8's loader carry the groups and
whether the agent was told. A paid run that varies it is gated on the exact sentence in
`CLAUDE.md`, and no rule may read it. Mock only: no paid call in this issue.

**The state at the start.** `CLAUDE.md` already holds the gate's sentence ("Ethics sign-off for
the real-ethnicity factor (issue #92): approved by the supervisor on 2026-10-24"), recorded by the
user in PR #93 before this work began. So the issue's "test that the repository records no
sign-off" no longer describes the repository: the tests check the gate against a file without the
sentence, and that the repository's `CLAUDE.md` holds it (as `test_pairwise.py` already does for
attractiveness).

**The user's answers, 2026-10-24** (asked at the start, via the question tool):
- Open question 1, the wording of Others: *"neither Chinese, Malay nor Indian"*. Itself:
  "- You are of another ethnicity, neither Chinese, Malay nor Indian."; seen: "They look neither
  Chinese, Malay nor Indian."
- Open question 4, a visitor's ethnicity: *drawn from the same resident shares*, recorded as a
  stated limit.
- Open question 3 (balanced shares): not asked for, so not built (the issue says build the real
  shares, `balanced` only if asked).
- Open questions 2 and 5 are the supervisor's; 5 was answered on 2026-10-24 (approved). 2 stays
  open in the docs.

## Plan
1. Cache the source page as text (`refs/rf26_singstat_population_trends_2026.txt`) and write
   `configs/resolution/ethnicity_sg_2026.yaml` (groups, shares, sentence, URL, date, the
   resident-only limit, and the visitor decision).
2. `negsim/resolution/ethnicity.py`: load and check the shares; the draw for a session (person 1
   at the shares; person 2 the same group, or from the other three renormalised); the expected
   number of sessions per group pair.
3. Freeze `resolve_factors_v2`: `resolve_factors_v1` word for word plus an `ethnicity` block (a
   `self` and an `other` line per group). `FactorTemplate` accepts the block, optional, and
   `SessionFactors` renders it (own line in ABOUT YOU; the other's line under them, with the
   observable factors, so from 10 m under `resolve_v3` and later).
4. `design.py`: `ethnicity_pair` and `ethnicity_visible`, the groups drawn per session and kept
   on the personas, the switch in `visibility`; optional `design.ethnicity_shares`.
5. `experiment.py`: the factor template defaults to `resolve_factors_v2` only for a design with
   ethnicity; the ethics gate; outcome columns `p1_ethnicity`, `p2_ethnicity`,
   `p<n>_other_ethnicity_shown`; `--plan` prints sessions per group pair.
6. `negsim/ethics.py`: the real-ethnicity sentence. `negsim/rules/fields.py`: the real group
   names (and race words) are protected; tests over every path.
7. `analysis/`: the ethnicity columns, as told.
8. Tests, a mock rehearsal config run on the mock, then docs (`docs/ethnicity.md`,
   `resolution.md` D2 and D7, `encounter-protocol.md`, `fictional-groups.md`, READMEs).

**My design choices** (assumptions, not decisions of the user or the supervisor; each is open to
change):
- **A1. The draw's key.** Seeded by the design's seed, the case and the cell (or, for a
  counterfactual pair, the pair). Not by condition or repeat: the exact-repeat set stays identical
  prompts (D14), the same two people meet under all three conditions, and a pair that flips
  another factor keeps both groups. A pair that flips `ethnicity_pair` keeps person 1's group.
- **A2. Where the lines go.** The ethnicity line comes first among the factor lines, both in
  ABOUT YOU and under a seen person (identity before circumstances, after age and gender).
- **A3. The analysis.** Predictors `same_ethnicity` (told, and the same as one's own) and
  `ethnicity_unseen`, the two the screen's design can estimate. The groups themselves are kept as
  descriptive columns, not predictors: at real shares the smaller groups have too few sessions
  for a per-group term (separation, RF-8's open question).
- **A4. Rules.** Field names with "ethnic" were already refused (the stem, #32). New: the real
  group names (Chinese, Malay, Indian) and "race", "races", "racial" are protected words, reported
  as "a person's ethnicity". "Others" is an ordinary English word and is not protected on its own.

## Progress log

### 2026-10-24 — Source cached, plan written
- What I did: read the issue, track #55, and the code the issue lists (`factors.py`, `design.py`,
  `pairwise.py`, `ethics.py`, `experiment.py`, `protocol.py`, `prompt.py`, `rules/fields.py`,
  `rulegen/validate.py`, `analysis/`). Asked the user open questions 1 and 4. Fetched the SingStat
  page and cached its text.
- Result: the page holds the issue's sentence word for word: "The ethnic composition of the
  resident population remained broadly stable over the decade, comprising 73.9% Chinese, 13.5%
  Malays, 9.0% Indians, and 3.6% Others as at end-June 2026." Total population 6.21 million,
  resident population 4.23 million (line 144 of the cached text). The shares add up to 100.0.
- Next step: the shares config and `ethnicity.py`.

### 2026-10-24 — The factor built, and the mock rehearsal
- What I did: `configs/resolution/ethnicity_sg_2026.yaml`; `negsim/resolution/ethnicity.py` (the
  shares, the draw, the expected pairs); froze `resolve_factors_v2` (sha256 `2e528b1d...`), checked
  by diff to be `resolve_factors_v1` plus the `ethnicity` block and its provenance;
  `FactorTemplate` and `SessionFactors` render it; `design.py` draws the groups; `experiment.py`
  gets the default template, the gate, the outcome columns and `--plan`'s table; `ethics.py` the
  sentence. Then the rehearsal config `resolve_ethnicity_mock_rehearsal.yaml` (16-cell fraction of
  seven factors, two head-on geometries, independent and talk, one counterfactual pair flipping
  `ethnicity_pair`; `resolve_v5`, `as_prompted`).
- Result: the rehearsal ran 72 of 72 sessions on the mock (2 min 32 s). Checked from the session
  records, independently of the row code: at all 142 decision points where the switch was on
  and the other was in view, the prompt held the right "They look ..." line; at none of the 111
  with the switch off. One's own line was in every prompt, before the cane. Both counterfactual
  pairs kept person 1's group and changed only person 2's.
- **A dead end in my own check, not in the code:** my first check flagged 111 "leaks" because it
  searched for "They look". That is `resolve_v4`/`resolve_v5`'s own wording for age and gender
  ("They look about 25 years old."). Rechecked with the exact ethnicity lines: no leak.
- **Finding (for the user, and for RF-10's sizing):** task 2's rule keeps person 1 at the shares,
  but person 2 of a `different` session is drawn from the other three groups, so the smaller
  groups are more common among *persons* than among residents. With half the sessions `same`:
  expected Chinese 60.8%, Malay 20.1%, Indian 13.6%, Others 5.5% (residents 73.9, 13.5, 9.0, 3.6).
  This is what the issue's rule implies, not a bug; `--plan` now prints the expected and drawn
  shares among persons, and `docs/ethnicity.md`, section 4, says so. In the rehearsal's 72
  sessions, 6 of the 16 pairs of groups are expected fewer than one session.
- Next step: the rule check, the analysis, tests, docs.

### 2026-10-24 — Rules, the analysis, tests, docs
- What I did: `negsim/rules/fields.py`: `REAL_ETHNICITY_WORDS` (chinese, malay, malays, indian,
  indians, race, races, racial), attributed to a new protected attribute `ethnicity` ("a
  person's ethnicity"). `analysis/`: `same_ethnicity` and `ethnicity_unseen` as predictors, the
  groups as descriptive columns, `factor_of` and `BASE_LEVEL` entries, a test. `tests/test_ethnicity.py`
  (51 tests). Docs: `docs/ethnicity.md` (new), `resolution.md` (status, D2, D7, constraints),
  `encounter-protocol.md`, `rule-format.md` (section 14), `log-schema.md`, `fictional-groups.md`
  (not used in track #55), `pairwise-factors.md`, both READMEs, `analysis/README.md`, and the
  pointer in `CLAUDE.md` to the gate's section (the sign-off sentences themselves untouched).
- Why the rule check keeps "ethnic" reported as before: a field such as `ethnicity_pair` was
  already refused by the stem `ethnic` (issue #32), with the message "a person's group". Changing
  that message would change what the rule-generation layer writes for such a rule. So only the
  new words are reported as "a person's ethnicity"; the category is `protected_attribute` either
  way.
- Result: `tests/test_ethnicity.py` 47 passed, 4 skipped (the non-experiment YAML files in
  `configs/resolution/`); `analysis/tests` 56 passed. The analysis ran end to end on the
  rehearsal's `outcomes.csv`.
- **A mistake of mine, caught:** the first full-suite run, started in the background, ran from
  the repository root (the `cd` did not carry into the background shell), so pytest collected
  `analysis/` and failed to import `negsim`. Rerun with `uv run --directory llm_negotiation`.
- **Two placeholder assertions** I had written into the test file (`... or True`) were replaced
  before the first run: one now pins `resolve_factors_v1`'s hash as it was before this issue
  (`bb3351d4...`, from commit 03f1f86's manifest).

### 2026-10-24 — The user's decision: a balanced draw, weighted back (open question 3)
- **The user's question, after PR #94 was opened:** should the agents follow Singapore's ratio,
  since too few Indian sessions would give less accurate results for Indian people? The build
  drew at the real shares, so the user's concern was an argument *for* equal shares. I
  recommended equal shares for the screen, weighted back to the real shares for population-level
  figures (survey practice). **The user said yes**, so the `balanced` option the issue held back
  "unless the user asks" was built.
- What I did: `design.ethnicity_draw` (`real`, the default, unchanged; or `balanced`).
  `balanced_assignment` rotates the four groups through `same` units and the twelve ordered pairs
  through `different` units, in blocks of four that balance both people, in a seeded order within
  each stratum. Every session of an ethnicity design gets `ethnicity_weight`, carried into the
  record and the outcome row. `--plan` prints drawn, expected and weighted counts per pair, and any
  pair never drawn. `analysis/groups.py` gives outcomes by own group and the other's as told,
  unweighted, and session outcomes weighted, with Kish's effective number of sessions. The rehearsal
  is now `balanced`, experiment `resolve_ethnicity_mock_rehearsal_v2` (a new run folder).
- **Two changes of direction while building it, both found by reading `--plan`:**
  1. First weights: the pair's chance at the shares over its chance under the design (1/4, 1/12).
     With 16 `different` units, not a multiple of 12, some pairs came up twice, and the weighted
     persons were Malay 25.8% against 20.1% expected. Replaced with post-stratification on the
     pairs actually drawn.
  2. Then the target itself was wrong. The weights restored the real mix *within* each level, but
     kept the design's 50/50 same/different and task 2's rule that keeps person 1 at the shares
     inside `different`. Neither is what "a Singapore pair" means: two residents met at random,
     each at the shares, are a same-group pair 57.4% of the time. The weight is now (share of
     person 1's group) x (share of person 2's) x sessions / sessions with that pair, under either
     draw. So under `real` the weights are no longer 1. This is my methodological choice (A5
     below), not the user's.
- Result: the balanced rehearsal ran 72 of 72 on the mock. Persons drawn: Chinese 26.4%, Malay
  27.8%, Indian 23.6%, Others 22.2%. Every pair was drawn at least twice. Weighted: 73.9, 13.5, 9.0,
  3.6% exactly, and the weights add up to 72. Analysis section 8 renders. Kish's effective number
  of sessions is 24 of 72: Chinese / Chinese, 10 sessions, carries 39 of the 72 weight. That is the
  price in precision of population-level figures under `balanced`.
- Tests: `tests/test_ethnicity.py` 53 passed (rotation balance, design balance and people kept
  across conditions, weights to random resident pairs, weight in record and row under both draws,
  validation, `real` unchanged); `analysis/tests` 59 passed (new `test_groups.py`).
- **A5 (my choice):** the weights' target is two residents met at random. An alternative would be
  "a pair that meets as the design says", for example keeping the 50/50 same/different. Easy to
  change if the user or the supervisor prefers it.

## Open questions / risks
1. **"They look Malay"** (issue's open question 2, *for the supervisor*): telling an agent another
   person's ethnicity as an inference from appearance. Built as the issue words it; not decided.
2. **The persons' mix is not the residents'** (progress log, the rehearsal). Person 2 of a
   `different` session over-represents the smaller groups. If the user wants every person at the
   resident shares, the rule must change (for example, draw both independently and let
   `ethnicity_pair` be observed rather than set, which a fractional screen cannot hold). Needs the
   user's view before RF-10. *Later the same day:* the `ethnicity_weight` corrects it for any
   population-level figure, under either draw, so the rule can stay as the issue gives it.
3. **Few sessions for the smaller groups.** At real shares, a per-group effect cannot be estimated
   from RF-10's screen. *Resolved by the user's decision of 2026-10-24:* `balanced` is built, and
   RF-10 should name `ethnicity_draw: balanced`. Still open: a per-group term in RF-8's models is
   not built (the report tabulates groups descriptively). With RF-9's 77% flip rate, even a
   balanced screen may not show one. Population-level figures under `balanced` rest on about a
   third of the sessions (Kish).
4. **My design choices A1 to A4** (the plan): the draw's key, the line order, the analysis
   predictors, and which words the rule check protects. Each is documented and easy to change;
   none is the user's or the supervisor's decision.
5. **"race" as a protected word** may refuse an unrelated rule that uses the word ("a race to the
   door"). Such a rule is kept and counted, never lost, so the cost of a false positive is a
   rule held back for a human to read. No existing rule, config or run uses any of the words
   (searched `rule_db/`, `configs/`, `cases/`, `runs/`).
6. **Paid runs still need their own approval.** The ethics sentence is recorded, but RF-10's paid
   run also needs `CLAUDE.md`'s pending item 1 (approval and cap) for that issue.
7. **The issue's "test that the repository records no sign-off"** no longer matches the
   repository: the user recorded the sentence on 2026-10-24 (PR #93). The test checks that the
   repository records it, and the gate is tested against files without it.
8. **`BEGINNERS_GUIDE.md` not updated.** It was last brought up to date for issues #35 to #41 and
   still describes the fictional group; updating it is a separate pass.

## Summary (fill in at the end)
**What changed.** Real ethnicity is a factor of the resolution layer (track #55), on the mock. It
replaces the fictional group, which stays in the rule-generation layer, unchanged.
- The shares are data (`configs/resolution/ethnicity_sg_2026.yaml`; source cached in
  `refs/rf26_singstat_population_trends_2026.txt`), including the resident-only limit and the
  visitor decision.
- `ethnicity_pair` (same, different) and `ethnicity_visible` are design factors. The groups are
  drawn with the seed (`negsim/resolution/ethnicity.py`, `design.py`).
- The lines are in the new frozen template `resolve_factors_v2`, the default for a design that
  varies ethnicity (`factors.py`).
- Outcome columns: `p1_ethnicity`, `p2_ethnicity`, `p<n>_other_ethnicity_shown`. `--plan` prints
  the sessions per pair of groups and the persons' mix (`experiment.py`).
- The ethics gate is its own sentence (`ethics.py`). The rule check protects the census group
  names and race words (`rules/fields.py`).
- RF-8's analysis reads it as told (`analysis/`).
- Mock rehearsal: `configs/resolution/resolve_ethnicity_mock_rehearsal.yaml`. Docs:
  `docs/ethnicity.md` and the updates listed above.

**Why.** The user's decision of 2026-10-24 (#55), so that RF-10's screen can include real
ethnicity, and RF-10 must not start before this is merged.

**How it was verified.**
- Full negsim suite: `uv run --directory llm_negotiation ... python -m pytest`, 1840 passed, 4
  skipped (11 min 32 s). The 26 test files that read docs were rerun after the doc edits: 1123
  passed, 4 skipped.
- `analysis/tests`: 56 passed.
- The 72-session mock rehearsal ran to completion, and its prompts were checked line by line
  against the session records (progress log). The analysis ran end to end on its
  `outcomes.csv`.
- No paid call was made: the spend ledger is untouched.

**Acceptance criteria.**
- `ethnicity_pair` and `ethnicity_visible` work in a screening design on the mock, with the
  groups drawn at the sourced shares: met.
- A paid run that varies ethnicity is refused without the recorded sign-off, and a mock run is
  not: met (tested with a file lacking the sentence, and with only the other factors'
  sentences).
- A rule that names ethnicity is `protected_attribute`: met (12 field forms × both prefix sets,
  plus 7 paths in rule generation and the loader).
- Every config and template from before behaves as before: met. Every older resolution config
  plans with no ethnicity anywhere, `resolve_factors_v1`'s hash is unchanged, and the full suite
  passes.
