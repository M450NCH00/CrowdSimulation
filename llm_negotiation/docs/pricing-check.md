# The pricing check

Every cost this platform reports, every worst-case preview and every budget guard reads the
prices in `configs/llm/deepseek_pricing.yaml`, and nothing else. DeepSeek changed its prices
twice in the two months before that table was written (`llm-backend.md`, section 1). So
**before any paid call**, the table is compared with DeepSeek's own pricing page, as the
README says and as issue #30 makes a prerequisite of its pilot. This file is how that check
is done, and the record of every time it was.

## 1. How

1. Open the page the table names, `source_url`:
   `https://api-docs.deepseek.com/quick_start/pricing`. Read it there, not from memory or a
   search result.
2. For every model the experiment will call (the pilot of issue #30: `deepseek-flash`),
   compare with the table: the model's name and version, the input price on a cache hit and
   on a cache miss, the output price, each at the peak and the off-peak rate; and the peak
   hours (`peak_hours_utc`).
3. Save the page's text under `refs/` with the date in its name, as
   `refs/ln_deepseek_api_docs_2026-10-13.txt` was, so that the check can be re-read later.
4. **If anything differs**, change the table to what the page says and set `date_checked`;
   say what changed, from what to what, in the record below; run the tests
   (`tests/test_llm.py` reads the table, and some of its numbers are pinned there) and the
   experiment's `--plan` again, since the preview changes with the prices. A price that has
   gone up can make a preview exceed its cap.
5. **If nothing differs**, set `date_checked` alone, and record that.
6. Commit the table and this record together, before the paid run, and name the commit in
   the record.

The check is valid for the paid run that follows it, not for a run days later.

## 2. The record

| Date checked | Page | By | For | Result | Change to the table | Commit |
|---|---|---|---|---|---|---|
| 2026-10-13 | `https://api-docs.deepseek.com/quick_start/pricing` | issue #24 | the C1 and C2 smoke runs | The prices of `llm-backend.md`, section 1 | The table was written | (issue #24's branch) |
| 2026-10-24 | `https://api-docs.deepseek.com/quick_start/pricing` (`refs/ln_deepseek_pricing_2026-10-24.txt`) | issue #64 | RF-9's pilot (`rf_pilot`) | Every price of `deepseek-flash` and `deepseek-v4-pro`, peak and off-peak, and the peak hours, as in the table. The model version of `deepseek-flash` is now `DeepSeek-V4.1-Flash-1017` (it was `DeepSeek-V4.1-Flash`); the page adds that the legacy names `deepseek-v4-flash` and `deepseek-v4-flash-vision-exp` are served by it. New on the page, not used here: Search and Fetch APIs billed per request (from 2026-11-01), and the granted balance is spent before the topped-up one | `date_checked` 2026-10-24; `deepseek-flash.model_version` to `DeepSeek-V4.1-Flash-1017`. No price changed, so no preview changed | 58c7b20 |
| 2026-10-25 | `https://api-docs.deepseek.com/quick_start/pricing` (`refs/ln_deepseek_pricing_2026-10-25.txt`) | issue #98 | RF-27's comparison (`rf27_round1_head_on_v7`) | Every price of `deepseek-flash` and `deepseek-v4-pro`, peak and off-peak, the model versions (`DeepSeek-V4.1-Flash-1017`, `DeepSeek-V4-Pro-0813`) and the peak hours, as in the table. The page now says that the off-peak hours include weekends and Chinese public holidays in full, and that thinking mode is the default (this platform disables it) | `date_checked` 2026-10-25 alone. No price changed, so no preview changed | the commit "docs: pricing check of 2026-10-25, no change (issue #98)" |
| 2026-10-25 (05:44 UTC) | `https://api-docs.deepseek.com/quick_start/pricing` (text identical to `refs/ln_deepseek_pricing_2026-10-25.txt`) | issue #100 | RF-28's run on `deepseek-v4-pro` (`rf28_round1_head_on_v4pro`) | The page re-read before this run: its text is identical to the morning's check, so every price of `deepseek-v4-pro` (off-peak 0.022 / 0.66 / 1.98 per million, cache hit / miss / output; peak double), its version `DeepSeek-V4-Pro-0813` and the peak hours are as in the table | none (`date_checked` is already 2026-10-25) | the commit "docs: pricing check for #100's run, no change" |
| 2026-10-25 (06:38 UTC) | `https://api-docs.deepseek.com/quick_start/pricing` (text identical to `refs/ln_deepseek_pricing_2026-10-25.txt`) | issue #101 | RF-29's run under `resolve_v8` (`rf29_round1_head_on_sidestep`) | The page re-read before this run: its text is identical to the morning's check, so every price of `deepseek-flash` (off-peak 0.003 / 0.15 / 0.60 per million, cache hit / miss / output; peak double), its version `DeepSeek-V4.1-Flash-1017` and the peak hours are as in the table | none (`date_checked` is already 2026-10-25) | the commit "docs: pricing check for #101's run, no change" |
| 2026-10-25 (08:18 UTC) | `https://api-docs.deepseek.com/quick_start/pricing` (text identical to `refs/ln_deepseek_pricing_2026-10-25.txt`) | issue #104 | RF-30's run (`rf30_round1_head_on_keep_line`) | The page re-read before this run: its text is identical to the morning's check, so every price of `deepseek-flash` (off-peak 0.003 / 0.15 / 0.60 per million; peak double), its version and the peak hours are as in the table | none (`date_checked` is already 2026-10-25) | the commit "docs: pricing check for #104's run, no change" |
| not done | — | — | issue #30's pilot | **Not done.** No paid call has been made in issue #30: the pilot is held until the supervisor's approval is recorded (`rule-generation.md`, section 10). The check is due immediately before the pilot | — | — |

The pilot's worst-case preview (USD 0.619 as issue #30 specifies the design, USD 0.648 since
issue #32 moved it to prompt version 2: `rule-generation.md`, section 10.1) is priced at the
table of 2026-10-13. If the check finds other prices, the preview, and the options of Q5 with
it, must be worked out again.
