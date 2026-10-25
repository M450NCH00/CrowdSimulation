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

### 2026-10-25 — Built, rehearsed, first paid batch; paused on the reply cap
- Config `round1_head_on_v4pro.yaml` (RF-27's, with `resolve_v6`, `deepseek-v4-pro`, cap USD
  0.30); against RF-10's config the diff is only the experiment name, the description, the
  condition, the kept pairs' comment, the model and the cap. Test
  `test_rf28s_config_is_rf10s_independent_sessions_on_deepseek_v4_pro` (templates and every `llm`
  setting but the model equal to RF-10's; the same 96 sessions and people). The ethnicity guard's
  skip list gets the config, as RF-27's.
- Mock rehearsal (`runs_mock/rf28/`, 96 of 96): the same session ids, cells, people, weights as
  RF-10's, and **all 96 first prompts word for word RF-10's**.
- Pricing page re-read at 05:44 UTC: text identical to the morning's check; recorded in
  `docs/pricing-check.md`. Balance USD 1.08.
- Paid batch of 6 (USD 0.011625, USD 0.0019 a session as estimated): model `deepseek-v4-pro`,
  fingerprint `a307abda487cd1b463329ccb945ce396`. **11 of 12 replies readable; 1 cut off at the
  300-token reply cap on both attempts** (`finish_reason: length`): v4-pro pretty-prints its JSON,
  one key per line, so a plan of 4 or 5 steps runs past 300 tokens. The readable replies took 91
  to 166 tokens. flash, compact, never came near the cap (RF-9's largest reply: 214).
- **Paused before the rest:** a truncated reply leaves the agent with no plan, which is a
  formatting artefact, not the model's judgement, and would count against v4-pro. Asked the user
  whether to raise the cap (a ceiling only: it changes no reply that fits, and costs only the
  tokens written).

### 2026-10-25 — The run of record at a reply cap of 600
- **The user chose (AskUserQuestion): raise the cap to 600 in a fresh run.** A resumed run must
  keep its config, so `round1_head_on_v4pro_cap600.yaml` is the first config with
  `max_tokens: 600` under `rf28_round1_head_on_v4pro_cap600`, its own cap USD 0.28 so that the
  issue stays within USD 0.30. `CLAUDE.md`'s approval note names both experiments. The first
  config and its 6 sessions are kept (`runs/rf28_round1_head_on_v4pro/NOTE.md`). Mock run of 6:
  the first prompts are still RF-10's word for word (the cap is not in the prompt).
- Paid batch of 6: nothing cut off (longest 247 tokens), but 3 of 12 decision points unreadable
  for formats the unchanged parser refuses (`"until": {"event": "other_passes"}`, `"until":
  {"seconds": 0}`). The parser stays unchanged (the user's decision for RF-27 and this issue), so
  I went on and added `analysis.compare --readable-only` (with a test) so that the report can
  show the comparison without them.
- The other 90: 96 of 96 completed. USD 0.164082 (385 calls, off-peak, no error; one transport
  retry costed as an upper bound, USD 0.0048). Issue total **USD 0.176** of USD 0.30. Balance
  **USD 0.91**. Largest reply 325 tokens (so the raise mattered), none cut off.
- **Result:** 18 of 64 resolved against flash's 22 (McNemar p = 0.57); readable only (48), 15
  against 18 (p = 0.68). Fails the gate. Unreadable 18 of 192 (flash 5).
- **How it fails, read further** (scratch script; numbers in the report): same-wall collisions
  2 against 18; one of the two aside in 37 of 64 sessions (flash 11); 40 of 113 readable first
  plans without a turn (flash 6 of 123), 22 of them giving holding the line as the reason; near
  misses 24 against 5; median closest gap 0.003 m against -0.029 m. **Exploratory, chosen after
  seeing the near misses:** no contact 42 against 27 of 64, paired McNemar p = 0.014. The gate is
  not moved.
- Wrote `comparison_report.md`; README row; `CLAUDE.md` balance. Every number checked against its
  file; two first drafts corrected (quotes taken from the first, 300-cap run; "the longest reply
  was within" a cap it had in fact exceeded at 300).

## Open questions / risks
- **Cap and parser:** the comparison differs from RF-10's in the reply cap as well as the model
  (flash's replies stayed under 300, so not for flash); v4-pro writes more formats the parser
  refuses. The readable-only comparison gives the same answer.
- **For the user:** the common failure across RF-10, RF-27 and RF-28 is the sidestep's size. The
  next test I would suggest is a step format in metres sideways (RF-27's option 2), on flash.
  A model of another family (`gpt-6-astra`) or thinking mode is the other route; both are the
  user's decision, each in its own issue.
- **For the supervisor (RF-11):** head-on fails the gate on every setup; v4-pro's "one holds the
  line, the other gives way" is a side-choice pattern that could still be extracted.

## Summary
**What changed.** `configs/resolution/round1_head_on_v4pro.yaml` (the first 6 sessions) and
`round1_head_on_v4pro_cap600.yaml` (the run of record): RF-10's independent sessions on
`deepseek-v4-pro`, the prompts word for word RF-10's; tests pinning both to RF-10's sessions;
`analysis.compare --readable-only`; the paid runs with the analysis and `comparison_report.md`;
the pricing check; `CLAUDE.md` (approval and balance); README.

**Result.** The stronger model does not resolve head-on more often (18 against 22 of 64,
p = 0.57). It coordinates differently (one holds the line, the other gives way: almost no
same-wall collisions, contact rarer, exploratory p = 0.014) but the lone sidestep is too small,
leaving near misses. Head-on fails the gate on every setup tried.

**How it was verified.** Config tests against RF-10's sessions; the mock rehearsal (96 of 96, the
same ids, cells, people; every first prompt word for word RF-10's); the pricing page re-read and
the balance before paying; a paid batch of 6 read before the rest (twice); the ledger against the
balance; the comparison tests (9); every number in the report checked against its file.
