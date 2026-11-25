# Work Log — Issue #5: [Docs] Biweekly progress deliverable for supervisor meeting

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/5
**Branch:** docs/5-biweekly-update-1 (based on `docs/4-literature-readme`)
**Started:** 2026-09-07

## Understanding the issue

A recurring biweekly progress document for the supervisor, answering 11 numbered
questions in order. The hard part is not the writing — it is the **sourcing rule**.
The issue is explicit that sections 3, 6, 10 and 11 are where it would be easy to
"fill gaps with plausible-sounding but unchecked claims", and requires anything
unsourceable to be marked `[unverified — needs confirmation]` rather than asserted.

Specific traps the issue sets, which I read as deliberate:

- **§5/§6** — "read CrowdGym's actual input/agent-behaviour interface in this repo
  before answering; if CrowdGym's interface isn't yet clear from the code/docs, say so
  explicitly instead of guessing." **CrowdGym's source is not in this repo at all.**
  Confirmed by search: the only file mentioning CrowdGym or `RL_take_action` is
  `integration/crowdgym_mapping.md`, and that file itself ends with "Confirm exact
  class/method names against the CrowdGym source before implementing" and "Nothing
  here calls CrowdGym yet". So §5 and §6 must be answered second-hand and labelled.
- **§8/§9** — pull from the *actual* dataset output and pipeline, "not from the
  original plan if the plan changed". The real output exists on disk at
  `dataset/generated/` (git-ignored, so not in the repo, but present locally).
- **§10** — "state plainly if verification is incomplete — does not imply more
  validation happened than actually did." Two of the checks in `VALIDATION.md` are
  explicitly still-to-do by hand.
- **§4** — "do not restate it more ambitiously than what's actually there."

### Assumptions made

- **A-path**: deliverable goes to `docs/biweekly-updates/update-01.md` (dropping the
  obsolete `/CrowdSimulation` prefix, as in issues #2 and #4). No prior update exists,
  so the numbering starts at 01.
- **A-branch**: the issue suggests `docs/biweekly-update-1` and permits renaming to fit
  an existing convention. Used `docs/5-biweekly-update-1` to match the repo's
  `<type>/<issue-number>-<slug>` convention from `github_issue_workflow.md` while
  keeping the biweekly numbering. Based on `docs/4-literature-readme` because §1 and §2
  need `literature/`, which is not on `main` yet.

## Plan

1. Preconditions, branch, work log. *(done)*
2. Gather **primary** evidence before writing anything: the real run01 raw output,
   the aggregated records, the validation report, the pipeline config/code, the
   scenario and persona registries, and the CrowdGym mapping doc.
3. Establish what is genuinely unknown (CrowdGym interface, adapter status) so it can
   be labelled rather than guessed.
4. Write all 11 sections in order, each claim carrying a source.
5. Verify: re-read every number against its source; check §3/§6/§10/§11 specifically.
6. Push, PR, comment on the issue.

## Progress log

### 2026-09-07 — Evidence gathered from primary sources before writing
- What I did: Pulled real numbers rather than reusing the summaries in `README.md` /
  `CLAUDE.md`. Recomputed run totals from `dataset/generated/raw/run01.jsonl` and
  statistics from `behaviour_records.jsonl`; read `pipeline/config.py`,
  `pipeline/generate.py`, `dataset/scenarios.yaml`, `dataset/personas.yaml`,
  `integration/crowdgym_mapping.md` and `dataset/generated/validation_report.md`.
- Why: The issue's sourcing rule, and its instruction to use actual output over the
  original plan.
- Result / what I found:
  - **Run01 confirmed from the raw log**: 420 calls, all `status: ok`, **420/420
    parsed successfully (0 failures)**, model `deepseek-chat`, temperature 1.0,
    `max_tokens` 1200, `response_format: json_object`, 3 repeats per cell, prompt
    version v1. Tokens: 485,496 prompt (377,600 cache-hit / 107,896 cache-miss) +
    132,844 completion = 618,340. **Actual cost $0.0966**, which matches the $0.097
    quoted in `CLAUDE.md`.
  - **My first attempt at this miscounted.** I parsed the raw JSONL with top-level
    keys (`cost_usd`, `usage`, `model`) and got 420 failures, $0 cost, model `None`.
    The real structure nests these under `request` / `response`. Recomputed correctly.
    Recording it because the wrong numbers would have looked plausible in the report.
  - **The gender pattern is much broader than the validation report's flag list.**
    `validation_report.md` flags 11 cells on the `|Δ| > 0.25` threshold. Computing the
    difference across *all* 70 `(scenario, age)` cells: **51 have female yielding more,
    8 have male yielding more, 11 are equal; mean Δ (female − male) = +0.101.** So the
    threshold-based flags understate a dataset-wide skew. This is a new finding, not in
    any existing repo document.
  - **33 of 140 records have `yield_likelihood_std` exactly 0** — identical values
    across all 3 repeats. That is precisely the "hyper-accuracy distortion" check the
    literature review (Aher et al.) recommends, and it now has a number.
  - **Two of the seven action-space actions were never produced**: the distribution is
    halt 46, yield_step_aside 34, proceed 31, slow 26, speed_up 3, and **back_off 0,
    reroute 0**. Also new, not in any existing document.
  - **CrowdGym source is absent from this repo.** Only `integration/crowdgym_mapping.md`
    references it; `integration/adapter.py` is a sketch in that document and does not
    exist as a file. So §5/§6 are answered from the senior's report second-hand and
    labelled as such, and §7 is explicitly conditional on that.
- Next step: write the 11 sections.

### 2026-09-07 - Deliverable written; a missing validation check found
- What I did: Wrote all 11 sections of `docs/biweekly-updates/update-01.md`, then
  re-verified every asserted number programmatically against its source file.
- Why: Plan steps 4-5; the issue's sourcing rule and its acceptance criteria.
- Result / what I found:
  - **20/20 numeric assertions verified OK** against the raw log, the aggregated
    records, `validation_report.json` and `pipeline/config.py`. Nothing in the
    document is a number I did not recompute or read directly from source.
  - **A fourth new finding surfaced while writing section 10.**
    `dataset/schema/VALIDATION.md` section 3 lists **four** directional
    hypotheses; the report contains only **three**. Reading
    `pipeline/validate.py` (lines ~120-145) confirms the fourth - "young adults
    at least as assertive as elderly" - **is never implemented**. It did not
    fail; it was never run, and the report gives no sign it was skipped. Added
    to section 10 as a process weakness, to section 11 as a likely question, and
    to the next-steps list. Also noted that the third hypothesis is checked with
    a tolerance (`el_y >= ya_y - 0.05`), so "at least as much" permits a small
    shortfall.
  - Section 11 was renumbered 1-16 after inserting that question; an "6a."
    marker would not have rendered as a list item.
- Next step: push and open the PR.

### 2026-09-08 - Propagated the DD2 / Cheng correction into update-01.md
- What I did: Merged the corrected literature branch in, then updated the biweekly
  document everywhere the Cheng et al. error had propagated.
- Why: The correction (see `WORK_LOG-4.md`) changed what can be claimed for DD2, and
  update-01.md repeated the wrong claim in section 2 and relied on it in section 9.
- Result / what I found - six sections touched:
  - **Header**: added a "Revised 2026-09-08" line naming the affected sections.
  - **Section 1**: seven papers -> eight; added the Deshpande row to the table.
  - **Section 2**: kept the wrong two sentences in place and appended a visible
    correction block under them, rather than silently rewriting - the supervisor should
    be able to see what changed. Added a Paper 8 paragraph.
  - **Section 3**: "Seven papers cannot establish it" -> "Eight".
  - **Section 9**: the DD2 bullet now says the "lower stereotype risk" wording is too
    strong, and states the narrower defensible claim.
  - **Section 10**: new weakness bullet - the dataset has **no prompt-side stereotype
    mitigation**, only the not-yet-performed audit. This is the substantive consequence:
    we previously believed DD2 was doing protective work, and it is not.
  - **Section 11**: new question 4 ("what is your evidence observer framing reduces
    stereotype risk?"); questions renumbered 1-17.
  - **Next steps**: added rewording DD2 in `README.md`, and testing the two framings
    directly on a subset - the remaining ~$1.90 budget covers it easily.
- Verified: all 11 sections still present and in order; section 11 numbering sequential
  1-17; next steps 1-7; 5 unverified markers retained; re-ran the numeric check - all
  7 spot-checks still pass (no data changed). The two new Cheng claims are quotable
  verbatim from the cached PDF text.
- Note: `README.md`'s DD2 wording itself is NOT changed here - that is a repo design
  record, and editing it is the user's call. It is in the next-steps list.

## Open questions / risks

1. **Sections 5 and 6 are second-hand and cannot be fixed from this repo.**
   CrowdGym's source is not here; `integration/crowdgym_mapping.md` is the only
   file that mentions it, and it was written from the senior's report. Class and
   method names, the `AgentType` field list, the `RL_take_action` signature and
   the exact RiMEA cases are all marked `[unverified - needs confirmation]`.
   Resolving this needs the CrowdGym source or a re-read of the senior's PDF,
   which is outside the repository.
2. **The gender finding is mine, not the validator's.** The 51/8/11 split across
   70 cells is recomputed for this document. It is a stronger statement than
   `validation_report.md` makes, and it should be sanity-checked before it goes
   in front of the supervisor - the underlying numbers are verified, but the
   framing ("the threshold understates a dataset-wide skew") is my reading.
3. **The missing fourth hypothesis is a finding about our own tooling**, not the
   dataset. I have reported it but not fixed it - implementing it is a code
   change outside this documentation issue's scope. It is in the next-steps list.
4. **Whether `back_off` / `reroute` absence is a defect is genuinely unclear.**
   It may be correct behaviour for these 14 scenarios. I have stated both
   possibilities rather than picking one.
5. **The $0.0966 cost is measured, but the dollar conversion is not.** The
   pricing table in `pipeline/config.py` is marked `VERIFY` in-file. Token counts
   are hard numbers; the dollar figure inherits an assumption.
6. **Section 3's gap claim is deliberately limited.** It is stated as five
   specific absences in the seven reviewed papers, with the wider-literature
   claim marked unverified. If the supervisor wants a stronger novelty claim,
   that needs a broader survey than this review.
7. **Date and authorship in the header** - I used the repo's git user (Choo Zhen
   Ming) and today's date. Adjust if the meeting date differs.
8. **DD2's wording in `README.md` is still the old, too-strong claim** ("lower
   stereotype risk"). I did not edit it - it is a signed-off design record and the
   rewording is your call. `update-01.md` section 9 and the next-steps list both flag it.
9. **Branch is stacked three deep** (`main` <- lit review <- lit README <- this).
   GitHub retargets automatically as each merges, but if you would rather merge
   PR #3 first and rebase these onto `main`, that is straightforward.

## Summary

**What changed.** Added `docs/biweekly-updates/update-01.md`, a supervisor-facing
progress document answering all 11 questions from the issue in order.

**Sourcing approach.** Rather than reusing the summaries already in `README.md`
and `CLAUDE.md`, I recomputed the run statistics from primary sources: the raw
per-call log `dataset/generated/raw/run01.jsonl`, the aggregated
`behaviour_records.jsonl`, `validation_report.json`, `pipeline/config.py`,
`pipeline/generate.py`, `pipeline/validate.py`, the scenario/persona registries
and `integration/crowdgym_mapping.md`.

**Four findings not previously recorded anywhere in the repo:**

1. **The gender skew is dataset-wide.** `validation_report.md` flags 11 cells on
   a `|delta| > 0.25` threshold. Across all 70 `(scenario, age)` cells: **51
   female-yields-more, 8 male-yields-more, 11 equal, mean delta +0.101.** The
   threshold understates a systematic direction.
2. **33 of 140 records have zero variance across all 3 repeats** - the
   hyper-accuracy-distortion pattern Aher et al. describe, now quantified.
3. **`back_off` and `reroute` were never produced** - 2 of 7 actions unused.
4. **A stated validation check is silently missing** - `VALIDATION.md` lists four
   directional hypotheses, `validate.py` implements three.

**Honesty constraints applied.** Sections 5 and 6 are explicitly labelled
second-hand because CrowdGym's source is not in this repository and
`integration/adapter.py` does not exist. Section 10 states plainly that the two
most convincing checks (the blind spot-check and the human gender-audit
judgement) **have not been done**, and that consistency is not accuracy. Section
3 states the gap as five specific absences rather than asserting novelty, and
marks the wider-literature claim unverified. Section 4 quotes the goal from
`CLAUDE.md` without enlarging it.

**How it was verified.**
- **20 of 20 numeric assertions re-verified programmatically** against their
  source files: record and scenario counts, 420 calls, 420/420 parsed, cost
  $0.0966, all four token totals, mean agreement 0.753, 12 low-agreement cells,
  0 FAIL / 54 REVIEW / 3 INFO, locality 40/69/31, 33 zero-variance records, the
  70-cell gender split, mean delta, the action distribution, n_repeats, model,
  temperature, max_tokens, and the budget arithmetic.
- All 11 sections confirmed present and in order.
- Five `[unverified - needs confirmation]` markers placed, in sections 3, 6 and 7.
- Sections 10 and 11 carry no unverified markers because every claim in them
  cites a source, which is what the acceptance criterion requires.
