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

### 2026-11-28 03:20 UTC — task 2, the reasoning text (commit `f0f687b0a`)
- `LLMResponse.reasoning_content` (new, default `None`); `DeepSeekClient._parse` reads
  `message.reasoning_content`; the mock returns a fixed reasoning text, and counts it in the
  completion and reasoning tokens, **only when thinking is on**.
- `negotiation.protocol.Attempt` has a `reasoning_content` field, written to the record **only when it
  is not `None`**. The resolution, grid and rule-generation protocols all record attempts through it,
  so one change covers them. Extraction and translation build their own records; RF-53 leaves them
  alone (thinking mode in them is out of scope).
- Checked that thinking-off records are unchanged in two ways:
  - tests (`tests/test_reasoning_text.py`): an attempt with no reasoning has exactly `ATTEMPT_KEYS`,
    in order; a mock resolution session with thinking off has no `reasoning_content` anywhere, and
    one with thinking on has it in every attempt;
  - a 4-session mock rehearsal of RF-40's config (`round1_head_on_turn_taking.yaml --limit 4`), once
    with the four changed files stashed and once with them: the same 68 files, identical once
    timestamps, latencies and git state are removed (CSVs byte for byte), and no
    `reasoning_content` key.
- No existing config or test runs the mock with thinking on, so no earlier mock record changes either.

### 2026-11-28 03:21 UTC — task 1, SV15 (commit `546ec455d`)
- Recorded as SV15 in `CLAUDE.md` (beside the November meeting's notes, marked as the user's report of
  2026-11-25 and not part of them), architecture section 8.8 and `docs/action-space.md` section 1.
- The words are the user's ("we can try to run the experiment with thinking mode on"); the
  supervisor's exact words are not recorded. **To ask the user** whether they have them.

### 2026-11-28 03:28 UTC — task 4, the probe runner (commit `a2f248451`)
- **Why a module of its own** (`negsim/probe/`, `python -m negsim.probe`): a probe is one question and
  one answer, with no simulation, session or conversation, so none of the existing experiment layers
  fits, and the CLI (`negsim/experiment/cli.py`) stays as it is [my choice]. It reuses the client, the
  budget guard, the spend ledger and the price table unchanged.
- **The probes, frozen** as `configs/probe/frames_probes_v1.yaml`, from RF-43's `probes.md`. My wording
  choices, none changing what a probe asks:
  - the other person is "Person 2" throughout, so that group C's note is `resolve_v9`'s
    `heard_seen_facing` sentence word for word, and A and C differ only by the note (tested);
  - the answer instruction comes last and allows a short phrase (group D's "your right");
  - each question names its options, as probe 1 does in `probes.md`; probes 13 and 15 name only left
    and right, so that "cannot tell" is the model's own answer.
  The file's SHA-256 (line endings normalised, as for templates) is in the config; an edited file is
  refused. A test checks every probe's expected answer against `probes.md`'s "**Expected: ...**".
- **The scorer** (`negsim/probe/score.py`) reads the reply's first line for one label of the probe's
  kind: plain keyword matching, so that a score can be checked by eye. A line naming both options is
  read by the first and flagged `ambiguous`; an empty or unreadable one is `unclear`, reported apart.
- **The config** (`configs/probe/rf53_stage1_frames_probe.yaml`): `deepseek-flash`, temperature 1.0 in
  both arms (no effect with thinking on), reply cap 300 off and **8,000 on** (task 3's inference that
  the cap counts the reasoning), reasoning effort at DeepSeek's default (`high`), no system message,
  JSON mode off. **`budget.cap_usd: 0`** until the approval is recorded, so the guard refuses every
  paid call (tested).
- **The order of calls** is repeat by repeat, so `--limit 40` is the pilot: one repeat of every probe in
  both arms (tested).
- **Paid-run safeguards:** `--confirm`, no call in peak hours without `--allow-peak` (checked before each
  call), a fingerprint check against RF-40's in `summary.json`, resume without resending, and a failed
  call set aside and sent again (all tested on a fake transport).
- **Mock rehearsal:** 400 calls, then a resume that sent nothing. The first rehearsal found a scorer
  bug: "Lane 3." was read as unclear (the pattern refused a digit before a full stop). Fixed (a decimal
  such as "3.5" is still refused) and tested; the rehearsal then scored all 400 right with
  `probe_expected`, and all 400 wrong with `probe_wrong`.
- **`--plan`:** worst case USD 2.02 (every call at the peak rate using its whole cap, which the guard
  assumes); estimates off-peak: thinking off USD 0.009; thinking on USD 0.07, 0.13, 0.25 or 0.49 at
  500, 1,000, 2,000 or 4,000 reasoning tokens a call.

## Open questions / risks
- **`max_tokens` and the reasoning:** inferred, not stated by DeepSeek. If 8,000 is too small,
  replies end with `finish_reason: length` and an empty answer, scored `unclear`; the pilot shows it.
- **The scorer is keyword matching.** It can misread a first line that reasons instead of answering
  (for example "Their left is my right, so I go left" reads as "left", flagged `ambiguous`). The
  report needs a hand check of the ambiguous and unclear replies, and a sample of the rest.
- **Temperature differs in effect between the arms** (1.0 with thinking off; none with it on), so the
  spread of answers is not comparable between arms, only the shares correct.
- **The wording is the assistant's** where it departs from `probes.md` (above); the user may want it
  changed before the run (a new version, `frames_probes_v2`).
- The supervisor's exact words for SV15 are not recorded.

## Summary (fill in at the end)
