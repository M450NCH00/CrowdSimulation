# Work Log — Issue #64: [Experiment] RF-9: round 1 (head-on), paid pilot of Step 1, all three conditions

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/64
**Branch:** feat/64-rf9-paid-pilot-head-on (cut from `feat/63-analysis-factor-effects-mapping`, as every RF branch is stacked on the previous one; PR #90 is merged into `feat/62-...`)
**Started:** 2026-10-24, 13:13 Singapore time (Saturday: off-peak all day)

## Understanding the issue
RF-9 is round 1's paid pilot: the head-on case, all three conditions, age and gender as the only
factors, about 20 sessions per condition with an exact-repeat set. It measures what every cost
figure so far only estimated (tokens per decision point and per debrief, decision points and
calls per session, the cache-hit share), checks the loop end to end with the real model, gives a
first noise-floor estimate, and from that recommends Phase A's (RF-10's) cap and design.

### The budget audit before the issue (the user asked for it first, 2026-10-24)
Before starting, the user asked me to check that the budget is right, since the structure had
changed over earlier issues. What I found, and told the user:

1. **The DeepSeek balance is USD 1.49, not about 1.90.** `pipeline/config.py` assumes USD 2.00
   of credit; recorded spend is USD 0.097 (Phase 1, run01) + USD 0.0043 (the 37 calls in
   `llm_negotiation/spend_ledger.jsonl`, issue #24's smoke runs) = USD 0.101. The balance endpoint
   (`GET /user/balance`, free, not a model call; the key was not printed) said
   `total_balance 1.49` (topped up 1.48, granted 0.01). About USD 0.41 is unaccounted for in the
   repo: either the starting credit was not 2.00, or the key was used outside this repo's records.
   Only DeepSeek's usage page can say which. The pending total of about USD 1.80 (sign-off item 1)
   no longer fits.
2. **The worst-case gate made the pilot impossible at any realistic cap.** The resolution runner
   refuses a paid run whose worst-case preview exceeds the cap. A pilot-shaped design (72
   sessions) is bounded at USD 4.77; one talk session alone at USD 0.095, above the issue's
   USD 0.05 target, so even the issue's fallback (10 sessions per condition) is refused. The bound
   assumes 6 sends per call, tokens inflated 1.5 times, peak cache-miss prices and every reply at
   the 400-token cap; mock sessions use at most 7.7% of it (RF-7).
3. **A realistic estimate**, from the same 72 sessions on the mock (prompt tokens counted at
   DeepSeek's 0.3 per character), no cache: USD 0.10 to 0.18 off-peak, 0.19 to 0.36 at peak, for
   replies of 40 to 300 tokens; 0.21 off-peak if every reply hit the cap.
4. **No guard covers the whole budget.** Each experiment's guard counts only its own ledger lines
   (scoped by `experiment_name`); nothing checks the total, or the account balance.
5. **Prices are unchanged** on 2026-10-24, but the model version is now `DeepSeek-V4.1-Flash-1017`
   (the table says `DeepSeek-V4.1-Flash`).

### The user's decisions (2026-10-24)
- **Paid runs approved for this issue only**, with a **cap of USD 0.20** on this experiment's own
  calls (the user chose it from options I gave: 0.20, 0.15, 0.10). Recorded in `CLAUDE.md`.
- **Fix the worst-case check for this issue.**
- **The other person's age and gender are given from 10 m** (`WORK_LOG-61.md`, open question 7):
  a new core template, `resolve_v4`.

## Plan
1. `CLAUDE.md`: record the approval (this issue only, cap USD 0.20) and the balance finding.
2. **`resolve_v4`**: `resolve_v3` word for word plus `seen_short_age` and `seen_short_gender`,
   worded as the full-detail lines, under the short line of someone 5 to 10 m away. Frozen in the
   manifest. `prompt.py` renders them when the template has them; the outcome row counts age and
   gender as told at a short-line decision point under `resolve_v4`. The default core template
   stays `resolve_v3`, so no earlier config changes; the pilot names `resolve_v4`.
3. **The worst-case check**: `budget.over_cap` in a resolution config, `refuse` (the default,
   as before) or `stop_at_cap`: a confirmed paid run may start although its worst case exceeds
   the cap, and the per-call guard (unchanged) stops it at the cap. The recorded spend still cannot
   pass the cap. An older config is described, and behaves, exactly as before.
4. Tests on the mock for both, then the full suite.
5. The pricing check of `docs/pricing-check.md`, committed before the paid run.
6. `configs/resolution/rf_pilot.yaml`; `--plan`, `--client deepseek` (preview only), `--confirm`.
7. The report (task 4), the recommendation (task 5), the intent codebook v1 (task 6).

## Progress log

### 2026-10-24 13:13 — Start
- What I did: the budget audit above; read #55, #64, `llm-backend.md`, `pricing-check.md`,
  `budget.py`, `pricing.py`, the resolution experiment's preview and gate, `prompt.py`,
  `resolve_v3`, `WORK_LOG-61.md` open question 7.
- Next step: `CLAUDE.md`, then `resolve_v4`.

### 2026-10-24 13:30 — CLAUDE.md, resolve_v4, the worst-case check
- What I did:
  - `CLAUDE.md`: the approval under sign-off item 1 (this issue only, USD 0.20, `rf_pilot`'s own
    calls), and under "Budget" the balance check and the unexplained USD 0.41; the total spend is
    `ALREADY_SPENT_USD` plus the ledger.
  - **`resolve_v4`** (frozen in the manifest, 2026-10-24): `resolve_v3` plus `seen_short_age` and
    `seen_short_gender`, worded as `seen_age` and `seen_gender`. `prompt.py` prints them under a
    short line when the template has them and the demographics are visible;
    `CoreTemplate.prints_demographics(detail)` says whether a template does. The outcome row's
    `*_other_age_shown` and `*_other_gender_shown` now count a short-line decision point under
    `resolve_v4`. **Not the default:** `default_core` still gives `resolve_v3` for a design with
    factors, so the screening rehearsal and every earlier config render as before; the pilot names
    `resolve_v4`, and RF-10 must too.
  - **The worst-case check:** `budget.over_cap` in a resolution config, `refuse` (default) or
    `stop_at_cap`. Under `stop_at_cap` a confirmed paid run starts although its preview exceeds the
    cap; `--plan` says so; the per-call budget guard (unchanged) refuses the first call that could
    take the experiment's recorded spend past the cap, that session is kept as aborted, and the run
    stops. The key appears in `config.json` only when it is `stop_at_cap`, so an older folder still
    resumes. `--confirm` is still required.
- Why not a looser bound instead: the bound is a true worst case (six sends per call, a reply at
  the cap each time); shrinking it would stop it being one. The guard already makes the cap hard,
  so the preview's refusal added no safety, only a block. Why opt-in: the issue said "for this
  issue", and earlier configs must behave as before. The rule-generation layer keeps its own
  refusal untouched.
- Why not a session-level gate (start a session only if its whole bound fits): one talk session's
  bound is USD 0.095, so with USD 0.20 the run would stop after spending about USD 0.10, roughly
  half the cap, for no gain in safety. The cost of the per-call gate is at most one session's
  calls paid for and set aside.
- Result: tests. `test_encounter_protocol.py`: by default a confirmed paid run over the cap is
  refused and nothing is sent or recorded; under `stop_at_cap` (eight sessions, cap USD 0.004,
  the mock's tokens charged at the table's prices through the real `BudgetedClient`) the run
  stops with one aborted session, at least one finished first, the ledger stays under the cap,
  and a rerun stays under it too; `stop_at_cap` still needs `--confirm`; `over_cap` is described
  only when not the default. `test_pairwise.py`: `resolve_v4` is `resolve_v3` plus the two lines,
  prints them for anyone in view within 10 m when visible (and each alone when only one is), and
  otherwise renders exactly what `resolve_v3` does. `test_factors.py`: in the head-on case the
  outcome row counts age and gender at every decision point under `resolve_v4`, none under v2 and
  v3. 134 passed in the three files.
- Mock rehearsal of `configs/resolution/rf_pilot.yaml` (`runs_mock/`, not tracked): 72 sessions
  completed; the other's age and gender were shown at all 312 decision points (RF-6's rehearsal
  under `resolve_v3`: 0 of 31). `--plan`: worst case USD 4.770835, cap USD 0.20, DOES NOT FIT, and
  the `stop_at_cap` line.
- `analysis/pilot.py` (task 4's measures the main analysis does not give): tokens per send by
  kind against the preview's bound, cache-hit share, cost by tier and condition, sends per
  session, decision points per agent, trigger reasons, unreadable replies by reason, signals and
  messages, who passed first and passing sides per mode. Standard library only; 3 tests on a
  hand-made folder; the analysis suite 45 passed.
- Pricing check (2026-10-24, `refs/ln_deepseek_pricing_2026-10-24.txt`): no price and no peak
  hour changed; `deepseek-flash` is now `DeepSeek-V4.1-Flash-1017`. Recorded in
  `pricing-check.md`; the table is updated after the full suite.
- Next step: the full suite, commits, then the paid run.

### 2026-10-24 — Full suite; pricing table; the first paid sessions; paused
- What I did: full negsim suite **1781 passed** (13 min; 1769 before this issue, 12 new). Updated
  `deepseek_pricing.yaml` (`date_checked` 2026-10-24, `model_version` `DeepSeek-V4.1-Flash-1017`)
  and the date pinned in `test_llm.py`; committed with the record (58c7b20) before any paid call.
  `--client deepseek` without `--confirm`: `awaiting_confirmation`, nothing sent, no ledger line.
- **One paid session first** (`--confirm --limit 1`, Saturday, off-peak): a talk session, 10
  sends, USD 0.001370; replies 93 to 166 tokens; most of each prompt was a cache hit after the
  first send. Then **11 more** (`--limit 11`), a mix of the three conditions by the design's
  shuffled order. **12 of 72 sessions, USD 0.013398 spent** (ledger, `experiment: rf_pilot`).
  Independent sessions cost about USD 0.0004 to 0.0006, non-verbal and talk about 0.0010 to
  0.0015: the whole pilot would cost about USD 0.07 off-peak.
- **Finding 1: 14 of 60 decision points (23%) were unreadable after the retry.** 35 of 81 sends
  were unreadable: 34 `start_on_later_step`, 1 `unknown_until`. The model puts `start` on a
  later step, which the format allows only on the first. Mostly with meaning:
  `{"at_distance_m": 2.0}`, `{"after_seconds": 1.5}`, `"now"`. It wants a later step to wait for a
  distance or a time. The retry fixed only 6 of 20 such decision points: the retry instruction
  says only "Your last reply could not be read", not why, so the model sends the same thing again.
  An unreadable decision point gives that agent no plan.
- **Finding 2: no session was resolved, even with every decision readable.** In `plan_only`, 11
  of 12 sessions ended in a collision and none resolved; `plan_orca` resolved 0 of 12; plain ORCA 0
  of 12 (it passes at 0.004 to 0.010 m, a near miss). The 6 sessions with no unreadable decision
  point collided too. Example, `I_head_on_02dfbadb_4c33115a_r5`: both agents planned the sensible
  mirror moves "shift slightly right", turn right 8° and 10° for 3.8 s at 1.3 m/s, which as the
  prompt describes a turn ("walk at this angle to your left or right of the direction you are
  going") would move each about 0.6 to 0.7 m sideways. The replay moved them 0.26 and 0.32 m, and
  they collided (overlap 0.087 m). **Cause:** RF-4's executor (`execute.py`, `_step_velocity`)
  rotates the direction toward a point `lookahead_m` = 2.0 m further along the path. As the agent
  leaves its path that point pulls it back, so a turn of θ holds the agent at a sideways offset of
  about 2.0 m × tan θ: 0.17 m at 5°, 0.28 m at 8°, 0.35 m at 10°, 0.54 m at 15°. The executor
  does what its docstring says, but not what the prompt tells the agent a turn does.
- Why I stopped: both findings are design questions (the reply format and retry text are frozen
  templates; what a turn means is RF-4's executor and the prompt's wording), and the remaining 60
  sessions would mostly measure these two artifacts. The money already spent is kept: the 12
  sessions' records, prompts and raw replies are committed, as D13 requires.
- Next step: the user's decision.

### 2026-10-24 — The user's decisions; resolve_v5 and protocol.execution
- **The user's decisions** (options I gave; the user chose):
  1. A turn walks at its angle, as the prompt says ("make the executor match the prompt"),
     opt-in per config so earlier replays rebuild as before.
  2. **A start is allowed on any step** (not my recommendation, which was a retry message saying
     why a reply failed; the user chose to accept what the model was evidently trying to say).
  3. Rerun the whole pilot under a new experiment name with the rest of the cap, keeping the 12
     sessions as a documented first batch.
- **A third mismatch found while checking the fix (free, no LLM call).** I replayed the 12 paid
  sessions' recorded plans with turns at their angle: still 2 of 12 resolved in `plan_only`, 8
  collisions. The trajectories showed why: the plans are time-bounded sidesteps ("left 10 degrees
  for 2 s"), and when a step ends the executor steers the agent back to its original line, often
  before the meeting (agent 0 of `I_head_on_02dfbadb_54f8aa95_r1` reached y = 0.52 m and was back
  near 0.25 m when they met). The prompt says only "After the last step ends, you walk on towards
  where you are going". A scratch patch that keeps the line after a step resolved 4 of 12. I asked
  the user; **the user chose: keep the new line until the encounter is over.**
- What I built:
  - **`resolve_v5`** (frozen 2026-10-24): `resolve_v4` except two sentences of the step format
    (any step may have a start, `after_seconds` counted from now; a later step waits for its
    start, the agent walking on meanwhile) and `later_step_start: true`. The retry and the
    description are `resolve_v4`'s. `ReplyContext.later_step_start` lets the parser accept a later
    start only under a template that says so; `steps_from_dicts` (the replay) accepts it, since the
    parser decided when the reply came.
  - **The executor:** a later step whose start has not come puts the plan back in `WAITING` for
    that step (`Plan.waiting_for`), with the agent walking its path meanwhile, as between steps.
    No earlier plan has a later start, so RF-4's runs are unchanged.
  - **`protocol.execution`**: `rf4` (default) or `as_prompted`. Under `as_prompted` a turn walks
    at its angle off the path's direction where the step began, and between steps and after the
    last, until the encounter is over, the agent walks parallel to its path at its own speed
    (only once a step has run, so an empty plan still reproduces the plain run). The session record
    names it only when not `rf4`, and the replay reads it from there. I first wrote this as
    `protocol.turn: offset | angle`; renamed to `execution` when the third change joined it, since
    it is no longer only about turns.
  - Replayed under the real `as_prompted` code, rf_pilot's 12 plans resolve 4 of 12 in `plan_only`
    and in `plan_orca` (plain ORCA 0 of 12), with 7 collisions left in `plan_only`. What remains
    looks like coordination failures (one agent goes to its left and the other to its right, both
    to the same side of the passage) and zigzag plans, which the pilot is meant to measure.
- Tests: `test_execute.py` (a turn as prompted moves 1.3 × 2.5 × sin 8° aside and holds −8°, under
  `rf4` it settles under 0.30 m; after its steps the agent keeps its line as prompted and steers
  back under `rf4`; empty plans give the same run under both; a later step waits for its start
  from the decision, or starts at once if due; `at_distance_m` on a later step; the parser takes a
  later start only when allowed; the replay reads `execution` and rebuilds the live run).
  `test_pairwise.py` (`resolve_v5` is `resolve_v4` but for two step-format lines; the protocol
  reads a later start only under `resolve_v5` and records `execution`; `execution` described only
  when not the default). 114 passed in the two files.
- `configs/resolution/rf_pilot_v2.yaml`: `rf_pilot`'s design with `resolve_v5`,
  `execution: as_prompted`, cap USD 0.18 (the issue's USD 0.20 less rf_pilot's USD 0.013398,
  rounded down). `rf_pilot.yaml` is left as it was, since its run folder holds its config. Mock
  rehearsal: 72 sessions, all on `resolve_v5` and `as_prompted`.

## Open questions / risks

## Summary (fill in at the end)
