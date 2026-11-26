# Work Log — Issue #141: RF-52: round 1 (head-on) on the grid, in the agent's own frame and in an absolute frame (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/141
**Branch:** feat/141-rf52-grid-run (cut from `origin/feat/129-rf40-turn-taking-talk` after PR #150; it already holds
the commit recording the user's approval, f5d1a35f9)
**Started:** 2026-11-26 08:20 UTC (from `date -u`)

## Understanding the issue
RF-51 (#140) put LLM agents on RF-50's grid, mock only, in two frames: their own left and right
(`resolve_grid_v1`, variant D) and lanes numbered from the blue wall (`resolve_grid_abs_v1`, variant E).
RF-52 runs both, paid, on RF-40's 272 silent sessions each, and asks:
- **Do LLM agents resolve head-on on the grid** (RF-10's gate, 0.50)?
- **Are the left and right errors gone** once the angle is gone and positions are given as lanes?

Fixed before this issue (recorded in `CLAUDE.md` and on #141):
- **Paid run approved for #141 only, cap USD 0.80** on its own calls, both frames together. Off-peak,
  pilot first. Balance USD 2.96 when approved.
- **The gate is RF-10's 0.50:** the share of sessions the agents' own plans resolve; the grid's measures
  stand for `plan_only`, and the ORCA baselines are reported as not available.
- **AS1:** the grid is an add-on. No existing file is edited; the user is asked before any existing file
  changes. Before the PR, `git diff --stat` against the base lists only new files (plus approved changes).
- **AS2:** silent only.
- **Two checks before any paid call** (`docs/action-space.md` section 3): the balance, and the model's
  fingerprint against RF-40's (`bc19ba97...`).

**Assumptions of mine (flagged):**
- **RF-51's files count as "existing" under AS1.** RF-51's entry point refuses any paid client by design
  ("RF-52 adds the paid run"). Rather than edit it, the paid run goes in a new module that imports it.
  This keeps `git diff --stat` to new files only and leaves RF-51's mock-only guard intact.
- **The cap is one cap over both frames**, enforced in code: a guard over the ledger lines of both
  experiment names together, not two caps of 0.40.
- **The random walkers' reference rate is reported beside the gate.** The user chose 0.50 as the gate;
  the random walkers (USD 0) are reported only as context, as proposed in the issue, and decide nothing.
- **RF-49 has not run** (not approved), so the comparison with the continuous menu is "not available";
  the comparison with RF-40's free steps uses RF-40's silent `plan_only` rate (0.64).

## Plan
1. **A paid entry point, new file `negsim/grid/paid.py`** (`python -m negsim.grid.paid`): reads an RF-52
   config that names RF-51's config as its base and sets its own experiment name, client and cap. It
   adds what RF-51's mock runner lacks: the paid client behind a budget guard over both frames, the
   ethics gates (RF-40's design varies attractiveness and ethnicity), `--confirm`, a refusal in peak
   hours unless asked, aborted sessions set aside and rerun on resume, invocations, and each
   response's model fingerprint in the summary.
2. **Configs** `configs/grid/rf52_round1_grid.yaml` and `rf52_round1_grid_abs.yaml`, and tests on the
   mock (the guard over both names, refusals, resume after an abort).
3. **Off-peak (from 10:00 UTC):** check DeepSeek's prices page against the price table, the balance,
   and the fingerprint on the pilot's first replies. Pilot a few sessions per frame, read the replays.
4. **The rest of both frames**, off-peak, stopping at the cap.
5. **Analysis, new module `negsim/grid/report.py`:** the gate with Wilson intervals, by frame and
   geometry; RF-50's measures; the frames paired session by session; unreadable replies; RF-45's
   hallucination share through an adapter from the grid's view to the shape `analysis.hallucination`
   reads; the side errors; the factor effects; the random walkers' rate on the same seeds; RF-40's
   silent rate beside it.
6. Report, README rows, `docs/action-space.md` section 8.4, the balance in `CLAUDE.md`, task 3's
   question for the user, PR.

## Progress log

## Open questions / risks

## Summary (fill in at the end)
