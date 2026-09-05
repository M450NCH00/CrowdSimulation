# How to tell whether the generated dataset is any good

Short answer: you **cannot prove it is "accurate"** in an absolute sense — whether
an LLM captures real human behaviour well enough *is the research question*. What
you can do is build a defensible case across several angles and **report the
divergences honestly**. CLAUDE.md asks for explainable, defensible methods over
black-box metrics, so each check below is something you can write up and cite.

There are five different things people mean by "accurate" here — keep them apart.

## 1. Format validity  (automatable — `validate.py`)

Every record parses, matches `behaviour_record.schema.json`, enums are legal,
numbers in range, all 140 cells present. Necessary, not interesting. If this
fails, fix the prompt or the parser and re-aggregate (no new API spend needed —
`aggregate.py` re-reads the raw file).

## 2. Reliability / internal consistency  (automatable — `validate.py`)

- **Repeat agreement.** `aggregation.primary_action_agreement` = fraction of the
  N repeats that gave the modal action; `yield_likelihood_std` = spread. Low
  agreement (< 0.6) is **kept and reported** — it is a finding: the LLM's "world
  model" is unstable for that cell.
- **Persona effect.** If a scenario returns the *same* `primary_action` for all
  10 personas, age/gender is not influencing the model there — flag it.
- **Cross-scenario coherence.** A persona that is `assertiveness: low` in a
  bottleneck should not be `speed_up / push through` in a near-identical merge
  without a reason in the narrative. `validate.py` does a light version; deeper
  checks are manual.

## 3. Face validity vs the literature  (semi-automatable — `validate.py` + citing)

This is the core defensible check.

- **Walking speed bands.** `validate.py` compares the free-walking scenario
  (`covered_walkway_walking`) speed for each age against published free-flow
  ranges (Weidmann 1993 adult mean ~1.34 m/s; Bohannon 1997 gait-speed norms;
  child gait literature). Out-of-band = REVIEW.
- **Directional hypotheses** (stated up front, then checked):
  - elderly slower than young adults — well established, should PASS;
  - children slower than young adults — should PASS;
  - elderly yield at least as much as young adults in deadlocks — weaker
    evidence, report whichever way it goes;
  - young adults at least as assertive as elderly (ordinal check).
- **Scenario sanity rules** you assert from domain knowledge, e.g. at the MRT
  door, boarders should mostly `halt` / `yield_step_aside` (alight-first norm);
  if the data says `push through`, that is a flag.

Write these as a short table in the report: hypothesis, evidence source,
result, comment.

## 4. Blind spot-check  (manual — you must do this)

Before looking at the generated data, hand-write the expected behaviour for
**~15 (scenario, persona) cells** based on literature and local knowledge
(one paragraph + expected `primary_action` + rough `yield_likelihood`). Then
diff against what DeepSeek produced. Record agree / partial / disagree and a
one-line reason for each. This is the single most convincing thing in the
report because it is pre-registered and explainable.

`validate.py` writes `dataset/generated/spotcheck_template.csv` (15 randomly
sampled cells, `expected_*` columns blank) and, separately,
`spotcheck_answers.csv` (the generated values). Fill the template first, then
open the answers file and record a verdict per row.

## 5. Gender / age bias audit  (semi-automatable — `validate.py` flags, you judge)

`validate.py` flags every `(scenario, age)` where male vs female differ by
`|Δ yield_likelihood| > 0.25` or have a different `primary_action`. For each
flagged cell decide: is this difference supported by evidence (e.g. small
gender gap in walking speed is documented) or is it an unsupported stereotype?
Unsupported ones are either corrected in the prompt and regenerated, or kept
and explicitly discussed as a limitation. Do **not** silently accept them.

## 6. Downstream / simulation validity  (manual — later, step 7+)

Wire the dataset into CrowdGym (`integration/crowdgym_mapping.md`), re-run the
senior's RiMEA-adapted Bottleneck / Corner / Crossflow scenarios, and check:

- do bottleneck deadlocks now **resolve** (they didn't reliably under pure
  SFM/CFS), and in a time consistent with `expected_resolution_time`?
- is pedestrian flow / density within RiMEA acceptance ranges and the Weidmann
  fundamental diagram?
- does the heterogeneous crowd (age/gender speed spread) change congestion
  patterns in a plausible direction vs the senior's homogeneous baseline?

## 7. Optional: human rating

Give a handful of raters (supervisor + a few peers) ~20 sampled records and a
Likert item: *"this describes how people in Singapore actually behave in this
situation"*. Even n≈5 raters gives an inter-rater number to report.

---

### What "done" looks like for step 6

- `validate.py` FAIL count = 0 (format + coverage clean).
- Every REVIEW item has a one-line resolution (accepted / corrected / kept as
  limitation).
- Blind spot-check table (15 rows) with an agreement rate and commentary.
- A short "Threats to validity" paragraph: LLM knowledge cutoff, Western-default
  bias, stereotyping risk, single-model (DeepSeek only), no real Singapore
  pedestrian ground-truth data used.
