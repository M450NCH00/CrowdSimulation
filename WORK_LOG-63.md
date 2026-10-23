# Work Log — Issue #63: [Feature] RF-8: analysis package for factor effects, a decision tree, the factor-to-decision mapping, and stated against measured

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/63
**Branch:** feat/63-analysis-factor-effects-mapping (cut from `feat/62-screening-designs-counterfactual-pairs`, as every RF branch is stacked on the previous one; PR #89 is merged into `feat/61-...`)
**Started:** 2026-10-23

## Understanding the issue
Step 4 asks which factors drive the decision. A model's own explanation can name factors that
made no difference, so a factor "matters" only if changing it changes the outcome: a statistical
question about the outcome table, not about what the agents say. RF-8 builds the tool that
answers it, on synthetic and mock data only (no LLM call, no real data: RF-10 runs it).

A new top-level folder `analysis/` (its own `requirements.txt`: pandas, statsmodels,
scikit-learn, matplotlib), so negsim keeps its standard-library-only design. It:

- loads one or more `outcomes.csv` and reshapes them to **one row per agent per session**: own
  factors, the other's factors **as the agent was told them** (counted as seen only at decision
  points where they were printed), the pairwise values from the agent's own point of view,
  condition and geometry, and the outcomes;
- fits a logistic regression per binary outcome and a linear one for start distance, with
  odds ratios and 95% CIs, Holm-corrected p-values and standard errors clustered by session,
  per condition and pooled with condition as a factor;
- grows a decision tree of depth at most 3 (text and figure);
- compares counterfactual pairs' flip rate with the noise floor from the exact-repeat set;
- reports behaviour stability per exact-repeat cell and lists coin-flip cells;
- writes the mapping table (each observed factor combination with outcome probabilities and
  counts);
- puts stated against measured (how often each factor is named in the private `reason`, the
  debrief `kind` counts) beside each factor's measured effect;
- codes the free-text `intent` with a versioned keyword codebook and reports the mismatch rate
  between intent and the plan coded from `steps`;
- writes `report.md`; and is tested on synthetic data.

## Plan
1. **negsim's outcome row** (task 2): add, per person, at how many decision points the other's
   age, gender and observable factor lines were printed (as `_pairwise_columns` does for the
   pairwise lines), and the encounter's member order, which the CSV lacks: the physical columns
   `_a`/`_b` follow the encounter's order (whoever noticed first), not p1/p2, so without it a
   passing side cannot be given to a person. Tests on the mock.
2. `analysis/`: `load.py` (read and reshape), `effects.py` (regressions), `tree.py`,
   `noise.py` (flip rate, noise floor, stability), `mapping.py`, `stated.py`, `intent.py` with a
   versioned codebook, `report.py`, `__main__.py` (`python -m analysis <outcomes.csv> ...`).
3. Synthetic tests, the issue's list (task 12).
4. Run it on the RF-7 screening mock rehearsal (252 sessions) end to end.
5. Docs: `analysis/README.md`, `log-schema.md` and `encounter-protocol.md` for the new columns,
   the READMEs' status.

## Progress log

### 2026-10-23 — what the outcome rows lacked
- What I did: read `resolution.md`, `log-schema.md` (resolution experiments), `encounter-protocol.md`
  section 7, `screening-designs.md`, `literature/trained-deciders/verdict.md`, and the code that
  writes an outcome row (`experiment.outcome_row`, `outcomes.physical_outcome`).
- Found two gaps:
  1. **The physical columns are not per person.** `passing_side_a`, `stopped_b` and so on follow
     the encounter's member order, which starts with whoever noticed first
     (`protocol._start`), not person 1. The row drops `agent_a`/`agent_b`, so a passing side
     could not be given to a person from the CSV alone. Only `who_passed_first` (an agent id)
     could be mapped.
  2. **"As told" was counted only for the pairwise lines** (`p1_pairwise_lines_shown`), as the
     issue says.
- Decision: add to negsim's outcome row (as the issue suggests, "as `_pairwise_columns` does"):
  `p<n>_other_age_shown`, `p<n>_other_gender_shown` (always) and `p<n>_other_observable_shown`
  (only with a design that varies an RF-5 factor, as the pairwise columns appear only with a
  pairwise design), and `encounter_agents`. Session records, replays and every other file are
  unchanged; resuming an experiment rebuilds its tables from the records.
- **Observable factors and "printed".** A base level (no cane) has no line, so "printed" is
  vacuous for it. The row counts the decision points where the other was in view at a detail that
  prints their factor lines; the analysis counts the factor as told when, in addition, the level
  has a line and the switch is on. From the agent's side that is exactly what it could know: a
  cane line, or nothing.
- Result: 5 new tests in `tests/test_factors.py` (head-on under `resolve_v3` and `resolve_v2`, a
  passage case within 5 m with the demographics visible and hidden, a design without factors),
  counted independently from the views. Pass.

### 2026-10-23 — the package, and a first run on the RF-7 mock rehearsal
- What I did: `analysis/` (load, effects, tree, noise, mapping, stated, intent, report, cli) and
  two codebooks; ran the RF-7 screening rehearsal (252 mock sessions, USD 0) and resumed it once to
  rebuild its tables with the new columns; ran `python -m analysis` on it.
- Found, and fixed before committing the codebook:
  - every intent came out "unreadable": a missing `parse_error` comes back from a data frame as
    NaN, which is truthy;
  - the side pattern needed whitespace after the verb ("Move over to my right" got no side).
- Found, and kept (the check doing its job): "Keep going for a moment, then slow down." with a
  plan coded as not slowing, 20 times. The mock's plan sets 0.8 m/s, and at a later decision point
  the agent was already slower, so `code_plan` (a speed below the speed at the decision) does not
  call it slowing. The intent says slow down; the plan does not: a mismatch.
- On the mock: the noise floor is exactly 0 (the mock is deterministic and the repeats send
  identical prompts, RF-7), every exact-repeat cell is stable, and most logistic models are
  `separation`. The mock's "effects" are its path cycling, not findings; the report says so in a
  banner when `config.json` names the mock client.

### 2026-10-23 — Holm's family changed from one model to the whole report
- What happened: the test "with no planted effect, nothing is significant after correction" failed
  with Holm over one model's terms: two terms through, out of some 45 models.
- Why: a family of one model controls the error per model; a report of 45 models then has a
  false positive almost every time. Checked on 20 synthetic no-effect screens (seeds 100 to 119):
  at least one false positive in **17 of 20** reports with a family of one model, **2 of 20** with
  one subset, **0 of 20** with the whole report.
- Decision: the default family is every term of every model in the report; `--holm-family
  subset|model` remain for a reader who states the narrower one. The first attempt (per model) is
  kept in the test's comment. Power: the planted effects (OR about 4.5 and 7) still pass at
  p_holm < 0.05 with 400 sessions.
- Also: a subset with one session divided by zero in statsmodels' cluster correction; such a
  model is now `no data` ("one session"), as is one with no more rows than parameters.
- Result: 42 analysis tests pass.

## Open questions / risks
1. **Separation will be common in round 1.** On the mock rehearsal (504 agent rows, 18
   varying predictors plus geometry and condition), 9 of the 15 pooled models were `separation`: rare outcomes (backed up, a plan
   that turns, resolved) with many 0/1 predictors. D14 aims at about 10 events per factor; with
   16 factors that is about 160 events, more than most per-agent outcomes will have in 480 rows.
   The analysis reports separation honestly and never as an effect, but RF-10 will need one of:
   Firth's penalised logistic regression (not in statsmodels; a small implementation or another
   package), fewer predictors per model, or leaning on counterfactual pairs for the rare
   outcomes. **Not decided here; for RF-10 (#65).**
2. **Holm over the whole report is conservative.** With about 400 terms, the smallest p-value
   must be below 0.05/400 (about 1.2e-4) to pass. A modest real effect in round 1 may not. The
   narrower families (`--holm-family subset|model`) exist, but which one RF-10 reports must be
   fixed **before** it sees the results, or the choice becomes a forking path. Suggest RF-10
   states it in its issue.
3. **The codebooks are drafts** (`intent_v1`, `reasons_v1`), written with no model reply to read.
   The issue says the intent codebook is "started in the pilot (RF-9)"; RF-9 should read real
   intents and reasons and write v2 of both. Keyword mentions are not a reading of the text (for
   example "her" is not counted as gender, and "left" in "little room left" would be coded as keeping to a
   side).
4. **Session-level models use the design levels, not "as told"**: a session's outcome
   (resolved, decision points) depends on both people, so there is no single point of view.
5. **"Clearly above the noise floor" is non-overlapping intervals**, which is stricter than a
   test of the difference at 5%. Chosen because it is easy to state and defend; a reader who
   wants the difference test can compute it from `flip_rates.csv` and `noise_floor.csv`.
6. **The flips and stability compare physical behaviour only** (who passed first, sides,
   stopped, backed up), as the issue lists. Flips of the coded plan are not computed.
7. **Where the output goes.** By default `analysis/` beside the first `outcomes.csv`; for a paid
   run under `llm_negotiation/runs/` that folder would sit beside committed data. Whether RF-10
   commits it is RF-10's choice. The negsim tests that scan `runs/` look only for `config.json`
   and API keys, so an `analysis/` folder there does not disturb them (checked).
8. **An `outcomes.csv` written before this issue** lacks the new columns and is refused with how
   to rebuild it (resume the experiment: no LLM call). No resolution experiment is committed yet,
   so nothing in the repository needs it.

## Summary (fill in at the end)
**What changed.**
- `analysis/` (new top-level package, own pinned `requirements.txt`): `python -m analysis
  <outcomes.csv> [...]` reshapes to one row per agent per session with the other's factors as the
  agent was told them, and writes logistic and linear models (clustered by session, per condition
  and pooled, Holm over the whole report by default), a depth-3 decision tree (text and PNG, with
  held-out accuracy), the mapping table, counterfactual flip rates against the exact-repeat noise
  floor, stability with coin-flip cells, stated against measured (reason keywords, debrief kinds),
  the intent-against-plan mismatch rate, and `report.md`. Versioned keyword codebooks
  `intent_v1.json` and `reasons_v1.json` (drafts for RF-9). No LLM call; negsim stays
  standard-library only.
- negsim's resolution outcome rows: `p<n>_other_age_shown`, `p<n>_other_gender_shown`,
  `p<n>_other_observable_shown` (with an RF-5 design) and `encounter_agents`. Session records,
  replays and every other file unchanged; `encounter-protocol.md` section 7 and `log-schema.md`
  change log updated.
- Docs: `analysis/README.md`; status in the root README, `llm_negotiation/README.md` and
  `resolution.md`.

**Why.** Step 4 asks which factors drive the decision; that is a question about the outcome table,
not about what agents say. RF-10 needs the tool before its paid screen.

**How it was verified.**
- `analysis/tests`: 42 tests, all pass (the issue's task 12 list, plus the a/b mapping, Holm
  families, separation, the CLI end to end, and a check that `analysis/factors.py` agrees with
  negsim).
- Holm family checked on 20 synthetic no-effect screens: false positives in 17 (per model), 2 (per
  subset), 0 (whole report).
- negsim's full suite: **1769 passed** (1764 before, plus 5 new outcome-row tests), 8 min 54 s.
- End to end on the RF-7 screening mock rehearsal (252 mock sessions, USD 0): report, tree,
  mapping written; noise floor 0 and every repeat cell stable, as a deterministic mock should give;
  the intent check found 20 real mismatches of a mock path (progress log).
- Acceptance criteria: `python -m analysis <outcomes.csv>` writes the report, the tree and the
  mapping (tested, `test_cli.py`); the synthetic tests pass.
