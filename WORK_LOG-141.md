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

### 2026-11-26 08:20 to 08:47 UTC — the build (mock only)
- **Read:** RF-51's runner, session, records and work log; the continuous runner's paid path
  (`make_client`, `run_resolution`, the ethics gates, `stop_at_cap`); the budget guard; RF-45's coder
  and report; `analysis.load` and `analysis.effects`; RF-40's comparison report.
- **Built, new files only (AS1):**
  - `negsim/grid/paid.py`: the paid entry point. RF-52's config names RF-51's as `base_config` and
    sets only the name, the model settings and the budget. `SharedBudgetGuard` puts one cap on both
    frames' ledger lines together. `--confirm`, a refusal in peak hours (checked before every
    session), the ethics gates, aborted sessions set aside and rerun on resume, fingerprints in
    `summary.json`.
  - `configs/grid/rf52_round1_grid.yaml` and `rf52_round1_grid_abs.yaml`: RF-40's model settings
    (`deepseek-flash`, temperature 1.0, 300 tokens, thinking off), cap USD 0.80 shared, gate 0.50,
    RF-40's fingerprint expected.
  - `negsim/grid/baseline.py`: RF-50's scripted pairs on each session's lanes and seed, written as
    `scripted_walkers.csv` beside the run (context for the gate, USD 0).
  - `analysis/grid.py`: the gate, RF-50's measures, the frames paired (McNemar), sides, RF-45's coder
    through an adapter, the grid's own side checks, the hand-check sheet, and the factor effects
    through `analysis.effects` unchanged, on RF-40's factor columns for the same sessions.
  - Tests: `tests/test_grid_paid.py` (6) and `analysis/tests/test_grid.py` (8).
- **Changed while building:**
  - The first cap test used USD 0.0005, below one call's worst case (3 attempts × about USD 0.001),
    so nothing was sent. Raised to 0.006.
  - Resuming after a raised cap was refused as "another config". The comparison now leaves out the
    budget as well as the source path: a cap changes no session. (The continuous runner leaves out
    only the source.)
- **RF-40's silent rate:** `docs/action-space.md` quotes 163 of 256; over all 272 silent sessions it
  is 175 (0.64 either way). The 256 leave out the 16 counterfactual-pair sessions. The analysis
  reports both, and the grid the same two ways.
- **DeepSeek's pricing page** (fetched 08:4x UTC): `deepseek-flash` is still DeepSeek-V4.1-Flash-1017;
  prices (0.003 / 0.15 / 0.60 off-peak, double at peak) and peak hours (01-04 and 06-10 UTC, weekdays)
  match `configs/llm/deepseek_pricing.yaml` exactly. Its `date_checked` (2026-11-02) is left as it is:
  it is an existing file (AS1), and nothing in it changed.
- **Peak hours until 10:00 UTC** (a Thursday): no paid call before then.

### 2026-11-26 10:01 to 10:09 UTC — the pilot (paid), and the run of record started
- **Balance before:** USD 2.96 (08:47 UTC; no paid call between then and the pilot).
- **Pilot:** 8 sessions per frame (`--limit 8`), 10:01:14 to 10:05:48 UTC. Own frame USD 0.006286
  (50 calls), absolute frame USD 0.004649 (36 calls); USD 0.0109 against the shared cap of 0.80.
  At about USD 0.0007 a session, all 544 come to about USD 0.38.
- **Fingerprint:** `bc19ba97cbe016479903222bb1578db6` on all 86 calls, RF-40's. No unreadable reply, no
  parse error.
- **Gate on the pilot:** 7 of 8 in each frame (not a result, 8 sessions).
- **Read every reply against its view** (`scratchpad/readpilot.py`). The views are right: the other's
  side and lane match the lanes, and the absolute prompt numbers lanes from the blue wall.
  - Own frame: the mix-up of the other's left and right is still there: "She moved a lane to her left"
    when she moved to her own right (two sessions), "They've drifted a lane to their left" after a move
    to their right. One dance where an agent steps towards the side the other just moved to.
  - Absolute frame: lane numbers are cited correctly ("She is in lane 4, so I shift towards the blue
    wall (lane 2)"). A new failure appears: both choose the same wall ("yellow"), which on the grid is
    the same direction, and they squeeze past one lane apart.
- **Fixed in the analysis after reading the replies** (no session changed):
  - **A bug of mine:** the analysis numbered lanes as internal lane + 1; the prompt numbers them
    `lanes - lane` (lane 1 at the blue wall, +y; `negsim/grid/prompt.py`, `_lane_number`). Now
    `lane_number()`, used by the lane checks and the hand-check sheet, and only in the absolute frame.
  - **New checks** for the error the supervisor raised (SV8): `other_move_side` (the other "moved to
    her left / my right" against the view's `lanes_moved_left`, the other's own sides being the
    reader's opposite) and `other_move_wall` (against `lanes_moved_plus_y`). Wider patterns for the
    pilot's wording ("coming toward me in lane 2", "we are head-on in lane 3", "the yellow side",
    "they've"). Test added; the analysis's 9 grid tests pass.
- **Run of record started 10:09 UTC** (`scratchpad/full.sh`): the rest of each frame, without
  `--limit`, `--client deepseek --confirm`, own frame then absolute, stopping at the cap. About 17 s a
  session, so about 2.5 h: well inside off-peak (until 01:00 UTC).

## Open questions / risks

## Summary (fill in at the end)
