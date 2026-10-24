# analysis: which factors drive the LLM agents' decisions (RF-8, issue #63)

Step 4 of track #55 asks which factors contribute to the decision. Reading an extracted rule
cannot answer that, because a model's explanation can name factors that made no difference. A
factor matters only if changing it changes the outcome, which is a statistical question about
the outcome table. This package answers it for one or more resolution experiments
(`llm_negotiation/docs/encounter-protocol.md`), and sets what the agents *said* drove them beside
what *did*.

It is a package of its own, with its own pinned dependencies, so that negsim keeps its
standard-library-only design. It never imports negsim at run time and never calls an LLM.

## Running it

From the repository root, with the pinned dependencies (`requirements.txt`):

```
uv run --no-project --python 3.13 --with-requirements analysis/requirements.txt \
    python -m analysis llm_negotiation/runs/<experiment>/outcomes.csv [more outcomes.csv ...]
```

The output goes to `analysis/` beside the first file (or `--out <folder>`). `--help` lists the
options: the mode whose physical outcomes are analysed (`plan_only` by default, the Step 1
measure), the tree's outcome and depth, named interactions (`--interaction own_urgency:other_load`),
the mapping's factors, the Holm family, the coin-flip threshold, and the codebooks.

An `outcomes.csv` written before issue #63 lacks two kinds of column the analysis needs (what each
agent was told of the other, and the encounter's order). Running its experiment again rebuilds its
tables from the session records, with no LLM call; the analysis says so when it meets one.

## What it writes

| File | Contents | Issue task |
| --- | --- | --- |
| `agents.csv` | one row per agent per session, from that agent's point of view | 2 |
| `effects_terms.csv`, `effects_models.csv` | every term (odds ratio or coefficient, 95% CI, p, Holm p) and every model's status | 4 |
| `tree.txt`, `tree.png` | a decision tree of depth 3 or less | 5 |
| `noise_floor.csv`, `flip_rates.csv` | the noise floor from the exact-repeat set; the counterfactual flip rates against it | 6 |
| `stability.csv` | stability per cell of the exact-repeat set, coin-flip cells marked | 7 |
| `mapping.csv` | every observed factor combination with outcome counts and shares | 8 |
| `reason_mentions.csv`, `debrief_kinds.csv`, `stated_vs_measured.csv` | stated against measured | 9 |
| `intent_check.csv`, `intent_summary.csv` | coded intents against coded plans; the mismatch rate | 10 |
| `report.md` | all of the above, for reading | 11 |

## How each part works

Each module's docstring is the full statement; in short:

- **`load.py`, one row per agent.** Own factors; the other's factors **as the agent was told
  them**: the other's age and gender only where they were printed (full detail, demographics
  visible), an observable core factor only where its line was printed (marked level, switch on,
  the other in view at a detail that prints it), a pairwise value only where its line was shown,
  the other's ethnicity (issue #92) only where it was told (`same_ethnicity`, `ethnicity_unseen`;
  the groups themselves are descriptive columns, too rare at real shares to be predictors).
  The physical columns' `_a` and `_b` are mapped to person 1 and person 2 through
  `encounter_agents`.
- **`effects.py`, factor effects.** Logistic regression per binary outcome (odds ratios), linear
  regression for start distance and decision points; standard errors clustered by session for the
  per-agent models (HC1 for the per-session ones); each condition separately and all together with
  condition as a factor. **Holm's correction runs over every term of the report by default**, so
  that the chance of any false positive in a report is at most alpha (see "Decisions" below). A
  model whose outcome is separated has no finite estimate and is reported as `separation`, never
  as an effect.
- **`tree.py`, the decision tree.** Depth at most 3, with its accuracy on held-out sessions
  beside always guessing the commoner outcome.
- **`noise.py`, flip rates and stability.** The noise floor is the flip rate between repeats of
  one cell (identical prompts), with a bootstrap interval over cells; a counterfactual pair's flip
  rate (Wilson interval) counts only where its lower end is above the noise floor's upper end.
  Stability is #30's: the share of a cell's repeats with the commonest outcome.
- **`mapping.py`, the mapping.** The lookup table a large simulation could use instead of the
  LLM; the tree is its compressed form.
- **`stated.py`, stated against measured.** Keyword mentions of each factor in the private
  `reason` (`codebooks/reasons_v1.json`) and the debrief kinds, beside each factor's strongest
  measured effect.
- **`intent.py`, intent against plan.** The free-text `intent` coded by keywords
  (`codebooks/intent_v1.json`) into keep to a side, slow down, stop and wait, back up, carry on,
  or `other`; a mismatch is an intent that says something the plan does not do.

## Decisions and assumptions (issue #63)

These are this issue's choices, not the supervisor's; `WORK_LOG-63.md` gives the reasons.

1. **Holm's family is the whole report** by default. On 20 synthetic screens with no effect, a
   family of one model let at least one term through in 17 reports, a family of one subset in
   2, and the whole report in none. `--holm-family subset|model` is there for a reader who states
   the narrower family.
2. **"As told" is coded as 0/1 predictors.** Where both levels of a factor have a line (age,
   gender, the pairwise factors, real ethnicity), "not told" is its own indicator
   (`other_demographics_unseen`, `pairwise_unseen`, `ethnicity_unseen`), not folded into the base level. An
   observable core factor's base level has no line, so "told it has a cane" against everything
   else is exactly what the agent could know.
3. **An age is "high" when above the lowest age in the data** (a design has two ages).
4. **The codebooks are drafts** written before any model reply. RF-9's pilot reads real intents
   and reasons and writes `intent_v2.json` and `reasons_v2.json`; a codebook is never edited once
   a result rests on it.
5. **The noise floor is compared condition by condition**, and pooled with pooled.
6. **A coin-flip cell** is one whose commonest behaviour came up in fewer than 3 of 4 of its
   repeats; with 3 repeats, any cell whose repeats disagree.

## Tests

```
uv run --no-project --python 3.13 --with-requirements analysis/requirements.txt \
    python -m pytest analysis/tests -o addopts=""
```

On synthetic data (`tests/synthetic.py`): a planted effect is recovered with the right sign;
with none, nothing is significant after correction (fixed seed); stated against measured is
exact on a hand-made table; a planted factor effect is above the noise floor and noise alone is
not; stability and the mismatch rate are exact on hand-made tables; a factor never printed to an
agent is not counted as seen; and `python -m analysis` writes the report, the tree and the
mapping. One test imports negsim (with PyYAML) to check that `factors.py` agrees with it.
