# Work Log — Issue #144: RF-53: thinking mode on: does DeepSeek's reasoning fix left and right, and change round 1? A static probe, then RF-40's sessions (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/144
**Branch:** `feat/144-rf53-thinking-mode-probe` (cut from `origin/main` after PR #153 brought the track into `main`)
**Started:** 2026-11-28 03:14 UTC

## Understanding the issue
The supervisor also suggested, in the November 2026 meeting, running with DeepSeek's thinking mode on
(the user's report of 2026-11-25). Every run so far has had thinking off. RF-43 found that reasoning
models do better on compass-direction questions, but not on two people facing each other, and
recommended a static probe before a full run.

**This session's scope: stage 1 only** (the user, 2026-11-28: "do what you think is best for RF-53
stage 1 first"; budget not a worry, a top-up is possible). Stage 2 (RF-40's sessions with thinking
on) is not started: it needs its own design from stage 1's numbers, and its own approval and cap.

Stage 1 sends RF-43's 20 probes (`literature/frames-of-reference/probes.md`) 10 times with thinking
off and 10 times with it on, on `deepseek-flash`: 400 calls.

## Plan
1. Task 1: record the supervisor's point as SV15 (`CLAUDE.md`, architecture 8.8, action-space section 1).
2. Task 3: check DeepSeek's current documentation, cache it in `refs/`.
3. Task 2: keep the reasoning text (client, response, attempt record), only when thinking is on; the
   mock returns one when thinking is on; tests that thinking-off records are unchanged.
4. Task 4: a probe runner (`python -m negsim.probe`), the probes as a frozen file, a scorer, a config,
   tests, and a mock rehearsal. Then ask the user for approval and a cap. No paid call before it is
   recorded in `CLAUDE.md`.

## Progress log

### 2026-11-28 03:14 to 03:16 UTC — start; task 3, DeepSeek's documentation
- Branch cut from `origin/main` (`git switch -c`, not `git checkout main`).
- Fetched `/guides/thinking_mode`, `/api/create-chat-completion` and `/quick_start/pricing`;
  cached as `refs/ln_deepseek_thinking_mode_docs_2026-11-28.txt`. Findings:
  - **The reasoning text** comes back as `message.reasoning_content`, beside `content`.
  - **Not sent back:** without `tools`, earlier turns' reasoning "does not need to be passed back;
    even if passed to the API, it will be ignored". negsim sends no `tools`, and the protocols send
    back only the parsed reply, so nothing changes there.
  - **Parameters ignored in thinking mode:** temperature, presence_penalty, frequency_penalty
    ("will not trigger an error but will also have no effect"). `top_p` takes effect only in thinking
    mode (0.95 to 1.0); negsim does not send it.
  - **The effort:** `reasoning_effort` defaults to `high` when thinking is on. negsim does not send it,
    so stage 1 runs at the default, `high`.
  - **`max_tokens`:** "the maximum number of tokens that can be generated", default 8K without thinking
    and 64K with it. The page does not say outright that the reasoning counts, but the larger default
    in thinking mode implies it does `[inference]`. So the thinking-on calls get a cap far above
    RF-40's 300, and the pilot checks `finish_reason` and `completion_tokens` against
    `reasoning_tokens`.
  - **Model and price:** `deepseek-flash` is `DeepSeek-V4.1-Flash-1017`, at the prices in
    `configs/llm/deepseek_pricing.yaml` (checked 2026-11-02): unchanged. Peak hours are Monday to
    Friday only; `pricing.tier_at` already says so.
- RF-40's fingerprint for the check: `bc19ba97cbe016479903222bb1578db6` (RF-52's configs).

## Open questions / risks

## Summary (fill in at the end)
