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

## Open questions / risks

## Summary (fill in at the end)
