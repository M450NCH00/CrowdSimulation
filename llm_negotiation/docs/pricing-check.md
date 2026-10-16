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
| not done | — | — | issue #30's pilot | **Not done.** No paid call has been made in issue #30: the pilot is held until the supervisor's approval is recorded (`rule-generation.md`, section 10). The check is due immediately before the pilot | — | — |

The pilot's worst-case preview (USD 0.619 as the issue specifies the design) is priced at
the table of 2026-10-13. If the check finds other prices, the preview, and Q5 of
`WORK_LOG-30.md` with it, must be worked out again.
