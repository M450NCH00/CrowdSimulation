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

## Open questions / risks

- (to be filled during the work)

## Summary (fill in at the end)

- (to be filled at the end)
