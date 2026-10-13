# LLM backend: DeepSeek

Everything here about DeepSeek's API was read from DeepSeek's own documentation at
`https://api-docs.deepseek.com` on **2026-10-13**, not recalled. Text extracts of the pages
are cached in `refs/ln_deepseek_api_docs_2026-10-13.txt`; locators below are `docs:LINE`
into that file. **Re-check the pricing page before any paid run**: the change log records
two price changes in the two months before this was written.

## 1. What the documentation says

| Fact | Value | Page | Locator |
|---|---|---|---|
| Base URL (OpenAI format) | `https://api.deepseek.com` | `/` (Your First API Call) | `docs:17` |
| Endpoint used | `POST /chat/completions` | `/api/create-chat-completion` | `docs:852` |
| Model names | `deepseek-flash` (DeepSeek-V4.1-Flash), `deepseek-v4-pro` (DeepSeek-V4-Pro-0813) | `/quick_start/pricing`, `/api/create-chat-completion` | `docs:121`, `docs:1105` |
| Legacy names | `deepseek-chat` and `deepseek-reasoner` were announced on 2026-04-24 to be "discontinued in three months (2026-07-24)". They are not in the current model list. | `/updates` | `docs:2239` |
| Thinking mode | On by default: `thinking.type` defaults to `enabled` | `/api/create-chat-completion` | `docs:1121` |
| Temperature | Default 1; "Has no effect in thinking mode" | `/api/create-chat-completion`, `/guides/thinking_mode` | `docs:1199-1203`, `docs:501` |
| Suggested temperatures | 1.3 for "General Conversation", 1.0 for data analysis, 0.0 for coding | `/quick_start/parameter_settings` | `docs:190-200` |
| JSON output | `response_format: {"type": "json_object"}`. The prompt must contain the word "json" and an example of the format. `max_tokens` must be set sensibly. "the API may occasionally return empty content." | `/guides/json_mode` | `docs:393-399` |
| `max_tokens` | 1 to 393,216; default 8K outside thinking mode | `/api/create-chat-completion` | `docs:1131-1137` |
| `seed` | **No such parameter.** The request parameters are `messages`, `model`, `thinking`, `reasoning_effort`, `max_tokens`, `response_format`, `stop`, `stream`, `stream_options`, `temperature`, `top_p`, `tools`, `tool_choice`, `logprobs`, `top_logprobs`, `user_id`, and the deprecated `frequency_penalty` and `presence_penalty`. The word "seed" does not occur in any cached page. | `/api/create-chat-completion` | `docs:872-1337` |
| `top_p` | Fixed at 1.0 outside thinking mode; a value passed is ignored | `/api/create-chat-completion` | `docs:1205-1213` |
| Usage fields | `prompt_tokens` (= `prompt_cache_hit_tokens` + `prompt_cache_miss_tokens`), `completion_tokens`, `completion_tokens_details.reasoning_tokens` | `/api/create-chat-completion` | `docs:1580-1604` |
| Context caching | Automatic, on for everyone; repeated prompt prefixes are billed at the cache-hit rate | `/guides/kv_cache` | `docs:754` |
| Token rule of thumb | "1 English character ≈ 0.3 token" | `/quick_start/token_usage` | `docs:217` |
| Errors | 400, 401, 402 (out of balance), 422; and 429, 500, 503, for which the advice is to wait and retry | `/quick_start/error_codes` | `docs:256-274` |
| Concurrency limit | 2,500 simultaneous requests for `deepseek-flash` | `/quick_start/rate_limit` | `docs:292` |

### Prices (USD per million tokens)

From `/quick_start/pricing` (`docs:150-168`), copied into
`configs/llm/deepseek_pricing.yaml`, which is the only place the code reads them from.

| | `deepseek-flash` peak | `deepseek-flash` off-peak | `deepseek-v4-pro` peak | `deepseek-v4-pro` off-peak |
|---|---|---|---|---|
| Input, cache hit | 0.006 | 0.003 | 0.044 | 0.022 |
| Input, cache miss | 0.30 | 0.15 | 1.32 | 0.66 |
| Output | 1.20 | 0.60 | 3.96 | 1.98 |

"Off-peak rates are half of the peak rates. Peak hours are 01:00 - 04:00 and 06:00 - 10:00
UTC, Monday through Friday, excluding Chinese public holidays" (`docs:168`). In Singapore
time the peak windows are 09:00-12:00 and 14:00-18:00 on weekdays.

Price changes on record: peak and off-peak pricing was introduced on 2026-08-16
(`docs:2191`), and prices were reduced with the release of DeepSeek-V4.1-Flash on
2026-09-10 (`docs:2061-2115`).

### What has changed since Phase 1

`pipeline/config.py` uses the model name `deepseek-chat` and prices marked "AS_OF 2025-09".
Both are out of date: the name is no longer in the model list, and the prices and the
pricing scheme have changed twice since. Phase 1 is frozen, so that file was left alone;
nothing in `llm_negotiation/` reads it.

## 2. How this platform uses the API

| Choice | Value | Status | Reason |
|---|---|---|---|
| Model | `deepseek-flash` | **design decision** | The cheaper of the two documented models. GameChat likewise "chose a smaller one that would run faster" (`gamechat-notes.md`). |
| Thinking mode | off (`thinking: {"type": "disabled"}`) | **design decision** | With it on, temperature has no effect, so the experiment's one sampling setting would be inert; it also adds output tokens and latency. GameChat's gpt-4o-mini is not a reasoning model. |
| Temperature | 1.0, fixed per experiment in its config | **design decision** | The API default. GameChat set none (`LLM_utils.py:56-59`), so it too ran at its API's default. |
| `max_tokens` | 300 | **design decision** | Room for a two-sentence message in JSON. A reply cut off at the limit is invalid JSON, which the protocol treats as malformed. |
| JSON output | on; both templates contain the word "JSON" and show the format | required by the API | |
| HTTP client | Python standard library (`urllib`), not the `openai` package | **design decision** | One endpoint is used. No SDK version to pin, and only `negsim/llm/deepseek.py` ever handles the header that carries the key. |
| Transport retries | 2 retries, on 429, 500, 503 and network errors | **design decision** | The documented advice for those codes. 400, 401, 402 and 422 abort the experiment. |

`negsim/llm/base.py` defines the client interface. `DeepSeekClient` and `MockClient`
implement it, and nothing else in the code base knows which one it has. Any other
OpenAI-compatible provider would be a third implementation of the same interface, or the
same class with another base URL, plus an entry in a price table.

## 3. Reproducibility: what can and cannot be fixed

Every run records the model name, the model string and `system_fingerprint` returned by
the API, the temperature, `max_tokens`, the thinking setting, and the run's seed.

The seed governs what the *simulator* draws: which of a task type's phrasings each agent
gets, and a random tie-break if that is switched on. **It does not govern the model.** The
API has no seed parameter, so the model's output can differ between two calls with the
same prompt and the same settings, at any temperature above zero and possibly at zero.
Two runs of the same condition are therefore two samples, not one result measured twice.
Use `design.repeats` and report the spread.

A model name is also not a fixed model. The change log shows names being re-pointed: the
name `deepseek-chat` meant DeepSeek-V3.2 from 2025-12-01 (`docs:2247`) and a mode of
`deepseek-v4-flash` from 2026-04-24 (`docs:2239`), and on 2026-09-10 requests for
`deepseek-v4-flash` were re-routed to DeepSeek-V4.1-Flash (`docs:2109`). The model string
and fingerprint the API returns are logged for every call so that a change can be detected.

## 4. The key

`DEEPSEEK_API_KEY`, and optionally `DEEPSEEK_BASE_URL`, are read from the environment or
from `.env` at the repository root, the same variable names as `.env.example` and Phase 1.
`.env` is git-ignored.

The key is held in a private attribute of the client and sent only in the `Authorization`
header. Request headers are never logged: the logs hold the messages and the sampling
settings. Any error text is scrubbed of the key before it is raised. The tests run a whole
negotiation through the real client with a fake key and a fake transport, then search
every file written for the key and for the words `Authorization` and `Bearer`
(`test_runs.py::test_the_api_key_never_reaches_any_log_file`).

## 5. Spend ledger and budget guard

- **Ledger.** `spend_ledger.jsonl`, one line per paid call: time, experiment, run, turn,
  attempt, model, token counts, price tier, estimated cost, running total. It persists
  across runs and is committed, so the spend is part of the record.
- **Estimated cost.** Tokens as the API reports them, times the table above, at the peak
  or off-peak rate for the UTC time of the call. Chinese public holidays are not modelled:
  a weekday inside a peak window is always costed at the peak rate, which can only
  overstate. The provider's bill is the authoritative figure; this is an estimate of it.
- **Cap.** Set per experiment (`budget.cap_usd`, default 0.50). Before each call the guard
  works out the most the call could cost: the prompt's length in characters times 0.45
  tokens (DeepSeek's 0.3 rule of thumb, inflated by half), all at the cache-miss peak
  rate, plus the full `max_tokens` at the peak output rate, times the three sends a call
  can make. If the ledger's total plus that exceeds the cap, the call is refused and the
  experiment stops. The recorded total can therefore never pass the cap; the price is that
  the last few cents of a budget are not spendable.
- **Failed sends.** A send that times out may still have been billed. It is recorded at its
  worst-case cost and flagged `cost_is_upper_bound`.
- **The mock client is never charged and never writes to the ledger.** Its runs go to
  `runs_mock/`, which git ignores.

## 6. Timing

Wall-clock latency is recorded for every call in both timing modes. In `concurrent` mode
the simulated clock advances by a configured amount per message, not by the measured
latency, so that a run does not depend on network conditions. The paper reports that
"each message is generated within one second" (`gamechat-notes.md`, D9), which is where
the default of 1.0 s comes from.
