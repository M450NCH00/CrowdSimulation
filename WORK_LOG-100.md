# Work Log — Issue #100: [Experiment] RF-28: round 1 (head-on) on deepseek-v4-pro: is it the model? (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/100
**Branch:** feat/100-rf28-v4pro-head-on (stacked on `feat/98-rf27-resolve-v7-walking-lines`, as the RF
issues are; PR #99 merged into `feat/96-...` on 2026-10-25)
**Started:** 2026-10-25 (Sunday: off-peak all day)

## Understanding the issue
RF-10 and RF-27 found that `deepseek-flash` agents resolve about a third of head-on meetings on
their own plans, and that telling them where the other is (`resolve_v7`) did not help (22 → 17
of 64, p = 0.44). This issue runs the same sessions on `deepseek-v4-pro`, changing nothing else,
to see whether a stronger model resolves them.

**The user's decisions (2026-10-25):** v4-pro before OpenAI's `gpt-6-astra` (about 4× flash's
price against about 80×, no new code); core template **`resolve_v6`** (the recommendation), so
the comparison is RF-10's independent sessions with only the model changed. Approval of paid runs
for this issue only, cap USD 0.30, recorded in `CLAUDE.md`.

## Plan
1. Config `configs/resolution/round1_head_on_v4pro.yaml`: RF-27's config (RF-10's 96 independent
   sessions, counterfactual pairs kept so the people match) with `templates.core: resolve_v6`,
   `llm.model: deepseek-v4-pro`, cap USD 0.30. A test that it reproduces RF-10's sessions.
2. Mock rehearsal; check the session ids, people and seeds against RF-10's.
3. Pricing check for `deepseek-v4-pro`; balance; paid batch of 6, read; the rest.
4. `analysis.gate`, `analysis.lateral`, `analysis.compare` against RF-10; report; README;
   `CLAUDE.md` balance.

## Progress log

## Open questions / risks
- v4-pro's replies may be longer: the reply cap stays 300 (RF-9's), so a truncated reply would
  show as unreadable. Watched in the first batch.

## Summary (fill in at the end)
