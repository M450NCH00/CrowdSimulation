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

## Open questions / risks

## Summary (fill in at the end)
