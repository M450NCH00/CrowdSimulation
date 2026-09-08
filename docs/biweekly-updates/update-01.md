# Biweekly progress update 01

**FYP:** Crowd Behaviour Modelling using LLM: Conflict Resolution
**Student:** Choo Zhen Ming
**Date:** 2026-09-07
**Covers:** work up to and including dataset generation run01 (2026-09-04) and the
literature review completed 2026-09-06/07.
**Revised:** 2026-09-08 — a correction to the Cheng et al. entry changed what can be
claimed for **DD2**; an eighth paper was added. Affected: §1, §2, §3, §9, §10, §11.

## Sourcing convention used in this document

Every factual claim below points at where it came from: a paper, a file in this
repository, or the actual generated output. Claims that could not be checked against a
source are marked **`[unverified — needs confirmation]`** rather than asserted. Numbers
labelled *(recomputed)* were calculated directly from the raw run output for this
document, not copied from an existing summary.

Two structural limits worth stating at the top, because they shape sections 5, 6 and 7:

- **CrowdGym's source code is not in this repository.** The only file referring to it is
  `integration/crowdgym_mapping.md`, which was written from the senior's FYP report, and
  which itself ends: *"Confirm exact class/method names against the CrowdGym source
  before implementing."* Everything said about CrowdGym's internals here is therefore
  second-hand.
- **The adapter that would connect the dataset to CrowdGym does not exist yet.**
  `integration/adapter.py` appears only as a sketch inside the mapping document; there
  is no such file. Nothing has been run against CrowdGym.

---

## 1. Papers read

Eight papers, in `literature/papers.md`, with a plain-language write-up of four of them
in `literature/README.md` and the full search record in `literature/search-log.md`.
Cached copies of every source are in `refs/`. (Paper 8 was added on 2026-09-08; see §2.)

| # | Paper | Year | Venue | Peer-reviewed |
|---|---|---|---|---|
| 1 | Aher, Arriaga & Kalai — *Using LLMs to Simulate Multiple Humans and Replicate Human Subject Studies* — [arXiv:2208.10264](https://arxiv.org/abs/2208.10264) | 2023 | ICML (oral) | yes |
| 2 | Argyle et al. — *Out of One, Many: Using Language Models to Simulate Human Samples* — [doi:10.1017/pan.2023.2](https://doi.org/10.1017/pan.2023.2) | 2023 | *Political Analysis* | yes |
| 3 | Cheng, Durmus & Jurafsky — *Marked Personas* — [doi:10.18653/v1/2023.acl-long.84](https://doi.org/10.18653/v1/2023.acl-long.84) | 2023 | ACL (Best Social Impact Paper) | yes |
| 4 | Wang et al. — *LLM-based Human Simulations Have Not Yet Been Reliable* — [arXiv:2501.08579](https://arxiv.org/abs/2501.08579) | 2025–26 | arXiv `[non-archival]` | no |
| 5 | Hullman et al. — *Validating LLM Simulations as Behavioral Evidence* — [arXiv:2602.15785](https://arxiv.org/abs/2602.15785) | 2026 | arXiv `[non-archival]` | no |
| 6 | Zhong et al. — *Data-driven Crowd Modeling Techniques: A Survey* — [doi:10.1145/3481299](https://doi.org/10.1145/3481299) | 2022 | ACM TOMACS | yes |
| 7 | Park et al. — *Generative Agents: Interactive Simulacra of Human Behavior* — [doi:10.1145/3586183.3606763](https://doi.org/10.1145/3586183.3606763) | 2023 | UIST | yes |
| 8 | Deshpande et al. — *Toxicity in ChatGPT: Analyzing Persona-assigned Language Models* — [doi:10.18653/v1/2023.findings-emnlp.88](https://doi.org/10.18653/v1/2023.findings-emnlp.88) | 2023 | EMNLP Findings | yes |

Two are preprints and are labelled `[non-archival]`; neither is the sole support for any
claim. Section and figure numbers cited below were read from the arXiv/ar5iv versions
rather than published camera-ready PDFs, so anything quoted verbatim in the final report
should be confirmed against the published version.

## 2. Why each paper is relevant

**Paper 1 — Aher et al. (the most directly transferable).** Introduces the *Turing
Experiment*: instead of asking whether one LLM output passes as human, condition the
model on many simulated participants and ask whether the *distribution* reproduces a
published human result. Three things transfer:

- Their **Ultimatum Game** replication (§4, Fig. 4a) is structurally the decision this
  project encodes — a two-party dispute over a contested resource settled by
  yield-or-refuse, which is exactly `conflict_behaviour.yield_likelihood`.
- They found a **large gender asymmetry in yielding**: simulated males accepted unfair
  offers from females ~60% of the time, females accepted unfair male offers ~20%,
  p<1e-16 (§4, Fig. 5). This is prior evidence about our own gender finding (§10).
- **"Hyper-accuracy distortion"** (§7–§8): aligned models answered obscure questions
  identically and correctly (median 1.0, IQR 0.0), destroying response variance. This
  gives us a named failure mode to test for, and we now have a number for it (§10).

**Paper 2 — Argyle et al. (justifies the persona axis).** Defines **algorithmic
fidelity** and tests it by conditioning GPT-3 on real respondents' demographic
backstories. Silicon-sample vote choice correlated with real ANES data at 0.90/0.92/0.94
for 2012/2016/2020 (§6, Table 1). This is the licence for generating per
`(scenario × age × gender)` cell and expecting real differentiation. The critical
caveat: fidelity was **not uniform** — strong partisans correlated at 0.99–1.00 but pure
independents at only 0.02–0.41 (§6). So we cannot claim uniform fidelity across our ten
persona cells from an aggregate pass rate. They also state their validation covers US
political attitudes only, so our Singapore dataset inherits none of it.

**Paper 3 — Cheng, Durmus & Jurafsky (the bias audit method).** Their *Marked Personas*
method finds stereotype without a pre-built lexicon, by contrasting personas of a target
group against the unmarked default. They found LLM personas contain **higher rates of
stereotype words than human-written portrayals from the same prompt** (§5), and — most
relevant to us — a "resilience myth" (Fig. 3) where a *positive-sounding* word functions
as a stereotype and so survives any sentiment- or toxicity-based filter. This is both
the justification for **DD2** (observer framing) and the proof DD2 is insufficient:
their prompts were also third-person descriptive and still amplified. Their limitation
is real for us: they draw only on American stereotypes and English.

> **Correction, 2026-09-08.** The two sentences above about DD2 were wrong and are
> retained only so the change is visible. Checking **Table A9** of the published PDF
> (cached at `refs/cheng2023_marked_personas.pdf`) shows Cheng et al. used **six**
> prompts spanning *both* framings — three first-person (*"Imagine you are a(n) [X].
> Please describe yourself."*) and three third-person (*"Describe a(n) [X]."*, *"Imagine
> a(n) [X]. Please describe [pronoun]."*) — and report **no statistically significant
> difference** in top-word distributions across them. So the paper does **not** justify
> DD2's choice of observer framing; it is mild evidence *against* the premise that
> framing changes stereotype content. (A null result, and possibly underpowered — it was
> not a targeted framing experiment.) What it does establish is that persona prompting
> amplifies stereotype relative to human-written text **whichever framing is used**, so
> DD2 is not a mitigation that removes the need to audit. The citation DD2 actually
> rests on is now paper 8. The error came from verifying Cheng et al. against the ACL
> Anthology landing page and ar5iv HTML, neither of which renders the appendix.

**Paper 4 — Wang et al. (the critical survey).** Reports that LLMs are **"3–6 times more
likely to generate gender-stereotypical behavioural patterns"** (§3.1) — the single most
applicable number in the review to our §10 finding. Also reports a
**reported-versus-enacted gap** (§2.3): agents prompted to be extraverted later behaved
introvertedly. That matters structurally, because our record schema keeps `disposition`
(what the persona is said to be like) and `conflict_behaviour` (what it does) as
separate objects, and Wang et al. say those need not agree.

**Paper 5 — Hullman et al. (how honest to be).** Distinguishes **heuristic** approaches
(prompt engineering, fine-tuning — "useful for many exploratory tasks" but lacking
"the formal statistical guarantees typically required for confirmatory research") from
**statistical calibration** (combining auxiliary human data with statistical adjustment).
By this distinction, this project is **heuristic and exploratory**, so the defensible
claim is "a plausible, internally consistent behaviour prior", not "a validated
substitute for human behavioural data".

**Paper 6 — Zhong et al. (the crowd-simulation side).** Establishes that learning
pedestrian behaviour from data rather than hand-tuned rules is mainstream peer-reviewed
practice, so the burden is to defend the *source* of the data, not the paradigm. §5.5
states that "a single validation approach can hardly cover all of these factors" and
recommends "multiple validations, each focusing on a different aspect" — which is the
citation for the multi-check structure of `dataset/schema/VALIDATION.md`. §5.3 argues
interpretability matters, which favours our frozen lookup table over a black-box model.
(Co-author Wentong Cai is at NTU, the same school as the senior's CrowdGym FYP.)

**Paper 7 — Park et al. (the existence proof, and the cost argument).** The canonical
demonstration that LLM-driven agents behave coherently in a running simulation. Its
believability ablation (§6.4, Fig. 8) gave TrueSkill μ = 29.89 for the full architecture
versus 21.21 with no memory/planning/reflection. But it "required substantial time and
resources... costing thousands of dollars" for **25 agents over two simulated days**
(§8.2). That number is the evidence for **DD1** — querying offline once per
`(scenario × persona)` and freezing the answers — and it is honest to note the ablation
also shows what freezing discards.

**Paper 8 — Deshpande et al. (the citation DD2 actually rests on).** Added 2026-09-08
after the correction above. Across **over half a million ChatGPT generations**, assigning
a persona ("you are X") **increased toxicity up to 6×** versus the default assistant,
producing "incorrect stereotypes, harmful dialogue, and hurtful opinions"; certain groups
were targeted ~3× more regardless of which persona was assigned. This is the evidence for
the mechanism DD2 relies on: first-person persona *assignment* measurably changes model
behaviour, and observer framing never issues such an instruction. Two limits, which the
report must carry: it measures **toxicity**, not stereotype content or behavioural
fidelity; and its setting is open-ended dialogue, not constrained JSON output about
pedestrian behaviour. So it supports a mechanism claim, not a quantitative transfer.

## 3. Has this been done before, and what is the research gap

**It has partly been done before, and the review says so.** Using an LLM as a source of
human behaviour is established: papers 1, 2 and 7 all do it, and paper 6 shows
data-driven crowd modelling is a mature field. The gap is therefore *not* "nobody has
used an LLM to model people" — that would be false.

The gap is narrower and is stated by pointing at what is **absent** in the reviewed
work. From `literature/README.md`, five specific absences:

1. **None of papers 1, 2, 3, 7 targets crowd or pedestrian simulation.** Their domains
   are classic lab experiments (1), US survey attitudes (2), free-text persona
   description (3), and a social sandbox where agents plan days and converse (7). None
   produces movement behaviour — walking speed, yielding at a bottleneck, doorway
   deadlock resolution.
2. **None produces a reusable, frozen behaviour dataset.** In all four the model is
   queried live and outputs are analysed, not retained as a lookup artefact.
3. **None operates near the target scale.** Park et al.'s 25 agents over two simulated
   days is the largest LLM-driven simulation among them, and its cost (§8.2) is
   precisely why the approach does not extend to 10,000 agents.
4. **None is validated outside a US/English context.** Argyle et al. state their
   validation covers US political attitudes only; Cheng et al. state their analysis
   draws only on American stereotypes and English.
5. **None maps elicited behaviour onto a physics-based simulator's numeric parameters.**
   That step is this project's DD4 / `integration/crowdgym_mapping.md`.

So the claimed gap is: **no reviewed work elicits movement- and conflict-behaviour from
an LLM, freezes it into a demographically indexed dataset, and feeds it to a
physics-based crowd simulator at a scale where live LLM calls are impossible.**

**Honest limits on that claim:**

- Whether the gap holds against the **wider literature these papers cite** is
  **`[unverified — needs confirmation]`**. Eight papers cannot establish it. Forward
  citations of papers 1, 2 and 7 were checked (see `literature/search-log.md`), but
  that is not an exhaustive survey.
- Two candidates found and *not* adopted bear on this and should be read before the
  claim goes in the report: *"Social Simulations with Large Language Model Risk Utopian
  Illusion"* (arXiv 2510.21180) and *"Human Behavior Simulation: Objectives,
  Methodologies, and Open Problems"* (arXiv 2412.07788). Both are recorded in
  `search-log.md`.
- Whether the senior's CrowdGym report itself already anticipates an LLM behaviour
  source is **`[unverified — needs confirmation]`** — that PDF is outside this
  repository and was not re-read for this update.

## 4. Ultimate project goal

Stated as it appears in `CLAUDE.md`, without enlargement:

> Model conflict-resolution behaviours by extracting them from an LLM, which is used as
> a "world model" for how agents should behave. Continue the senior's prior FYP
> (**CrowdGym**), treating their existing method as the baseline to improve on, and
> **"ultimately reach a crowd simulation capable of handling 10,000 agents without
> becoming too slow."**

The immediate task, from the first supervisor meeting, is narrower: build a dataset of
typical human behaviours under different scenarios by prompting LLMs, in service of the
research question *do LLMs actually understand human behaviour well enough to be used as
agents in the crowd simulation?*

Note that "10,000 agents without becoming too slow" is the stated end goal, not
something this stage claims to have achieved or measured. No performance work has been
done.

## 5. Why this dataset suits CrowdGym

**First, the honest caveat the issue asked for: CrowdGym's interface is not fully clear
from this repository, because CrowdGym's source is not in it.** A search for
`RL_take_action` or `CrowdGym` across the repo matches exactly one file —
`integration/crowdgym_mapping.md` — which was written from the senior's report and ends
with the instruction to confirm exact class and method names against the CrowdGym source
before implementing. So what follows is the *designed* fit, not a verified one.

As documented in `integration/crowdgym_mapping.md`, the design assumes two integration
points:

1. **`AgentType` parameters (CrowdGym report, Table I).** One `AgentType` per
   `(age_group, gender)` cell — 10 types — with distribution weights from
   `personas.yaml`. The mapping document gives starting formulas turning record fields
   into CrowdGym's `Speed`, `Tau`, `Mass`, `Radius side` and `Radius front`. This is
   DD4: the LLM supplies coarse qualitative attributes, and a documented mapping turns
   them into numbers.
2. **An overridden `RL_take_action`** as the conflict handler, which fires when an agent
   is close to, closing on, and blocked by another, then looks up
   `(scenario_id, age_group, gender)` and applies the record's `primary_action`,
   `fallback_action`, `yield_likelihood` and `priority_rules`.

The dataset is shaped for this: records are keyed exactly on
`(scenario_id, age_group, gender)`, the actions come from a closed vocabulary in
`dataset/action_space.yaml` where each action already carries a `crowdgym_effect`
mapping to a `(N, 3)` command row, and the scenarios in `dataset/scenarios.yaml` carry
geometry fields (`plane_size_m`, `passage_width_m`, `num_exits`, `exit_width_m`) that
the mapping document says feed CrowdGym scenario construction directly. `DD3` keeps the
dataset language-neutral JSON/CSV so the in-progress C++ port needs only a new adapter.

**What is not yet true:** no adapter exists, and nothing has been executed against
CrowdGym. `integration/crowdgym_mapping.md` lists `integration/adapter.py` as a "sketch
— not yet implemented", and there is no such file in the repository.

## 6. How the simulation currently works

**Everything in this section is second-hand** — from `integration/crowdgym_mapping.md`
and the summary in the repo `README.md`, both written from the senior's FYP report,
which is outside this repository and was not re-read for this update. Marked
accordingly.

- CrowdGym is a crowd-simulation environment for reinforcement learning, built by the
  senior (Goh Chen Wei, NTU AY2025/26). Agents are spawned by a **Spawner** from a list
  of **`AgentType`s**, each carrying numeric parameters including `Speed`, `Tau`, `Mass`
  and front/side radii (CrowdGym report, Table I, as cited in the mapping document).
- Movement uses **physical models — Social Force and a Collision-Free Speed model
  (CFS)**. The mapping document records that the senior found CFS "less jittery at
  exits" and recommends keeping it running underneath any behaviour override.
- Route choice is handled by an **`AgentJourneyDirector`** using a weighted-distance
  method.
- Agents act through a **`RL_take_action`** entry point which consumes an `(N, 3)`
  action array — per agent `[move_x, move_y, delta_facing]`.
- Verification runs used **RiMEA test scenarios**, and the senior's runs used
  `Speed = 0.8 m/s`, a JuPedSim default chosen for model-to-model comparison.
- **The stated problem this FYP addresses**: per the repo `README.md`, CrowdGym's
  rule-based models *deadlock* at bottlenecks and, in the senior's own words, "cannot
  handle the situation as a human would".

**`[unverified — needs confirmation]`** for this whole section: exact class and method
names, the precise `AgentType` field list, whether `RL_take_action` has the signature
assumed, and the exact RiMEA cases tested. All require the CrowdGym source or a re-read
of the senior's PDF.

## 7. How the dataset will help the simulation

This follows from 5 and 6 rather than being a general claim.

The specific failure in §6 is that a purely physical model has no notion of *who yields
to whom*: two agents meeting head-on in a one-person doorway apply symmetric repulsion
and deadlock. The dataset supplies exactly the asymmetry that is missing — for each
`(scenario, age, gender)` it gives a `primary_action`, a `fallback_action`, a scalar
`yield_likelihood`, and free-text `priority_rules` (e.g. deference to someone with a
stroller or an elderly person).

Mechanically, per `integration/crowdgym_mapping.md`:

- **Heterogeneity** enters through `AgentType`: 10 types with different speeds,
  reaction times and body sizes instead of one homogeneous population.
- **Deadlock breaking** enters through the conflict handler. Because the dataset is
  per-persona and not per-persona-*pair* (DD1), the adapter composes a pairwise outcome:
  `p_self_yields = clip(yield_self + priority_bias(rules_self, other) −
  priority_bias(rules_other, self), 0, 1)`, then samples. Two agents with different
  yield likelihoods break symmetry, which is what the physical model cannot do alone.
- **Tractability at scale** is the point of DD1: because the table is frozen, runtime
  cost is an O(1) dictionary lookup per triggered conflict, with **no API call during
  simulation**. This is what makes 10,000 agents conceivable where Park et al.'s
  per-agent live-LLM approach costs thousands of dollars for 25 agents (§8.2).

**Caveats:** this is the designed mechanism, not a demonstrated one — nothing has been
run. The pairwise composition rule is an unvalidated design decision, and
`priority_bias` is described as "a small hand-maintained table built during validation"
that does not exist yet. Whether the resulting behaviour actually resolves deadlocks, or
improves on the senior's RiMEA numbers, is **`[unverified — needs confirmation]`**.

## 8. What dataset was generated

All figures below are from the actual output in `dataset/generated/` (git-ignored, so
present locally rather than in the repository), not from the plan.

- **140 records** — one per `(scenario × persona)` cell — from **14 scenarios × 10
  personas** (5 age groups: child, teenager, young_adult, middle_aged, elderly × 2
  genders).
- **Scenario split**: 10 conflict scenarios and 4 everyday ones (counted from
  `dataset/scenarios.yaml`). Conflict types across the set: deadlock, congestion,
  resource_competition, none.
- **Format**: `behaviour_records.jsonl` (canonical, one JSON object per line, matching
  `dataset/schema/behaviour_record.schema.json`) plus `behaviour_records.csv` (flattened
  scalar view; list fields omitted). Raw per-call output is in `raw/run01.jsonl`.
- **Fields per record**: `record_id`, `schema_version`, `country`, `scenario_id`,
  `age_group`, `gender`, and five objects —
  - `movement_profile`: `walking_speed_mps` {estimate, low, high}, `reaction_speed`,
    `body_size`, `acceleration_tendency`
  - `disposition`: `patience`, `assertiveness`, `rule_compliance`, `risk_tolerance`,
    `situational_awareness`
  - `conflict_behaviour`: `primary_action`, `fallback_action`, `yield_likelihood`,
    `expected_resolution_time`, `decision_factors`, `priority_rules`, `narrative`,
    `locality`
  - `aggregation`: `n_repeats`, `primary_action_agreement`, `yield_likelihood_std`,
    `notes`
  - `provenance`: `model`, `prompt_version`, `generated_utc`, `run_id`,
    `raw_response_ids`
- **Action vocabulary is closed** (7 actions in `dataset/action_space.yaml`). Observed
  distribution across the 140 records *(recomputed)*: `halt` 46, `yield_step_aside` 34,
  `proceed` 31, `slow` 26, `speed_up` 3, and **`back_off` 0, `reroute` 0** — two of the
  seven actions were never produced.
- **Locality self-labelling** (from `validation_report.md`): universal 40, mixed 69,
  singapore_specific 31.

## 9. How the dataset was generated

The pipeline actually run, from `pipeline/config.py`, `pipeline/generate.py` and the
raw log — not the originally planned approach.

- **Model**: `deepseek-chat` via the DeepSeek API (confirmed on all 420 calls).
- **Parameters**: `temperature = 1.0`, `max_tokens = 1200`,
  `response_format = {"type": "json_object"}` (structured JSON forced at the API level).
- **Generation unit**: one prompt per `(scenario × persona)` cell, repeated
  **`REPEATS = 3`** times with an identical prompt, for consistency checking. 14 × 10 ×
  3 = **420 calls**.
- **Prompting**: a fixed system prompt (`pipeline/prompts/system_sg.txt`, hashed into
  every raw record as `system_prompt_sha1`) establishing Singapore context — MRT/bus
  norms, alight-before-boarding markings, escalator habits, tropical weather sheltering,
  multi-ethnic context, "chope" — plus a per-cell user prompt from
  `pipeline/prompts/user_template.txt` and an explicit output contract
  (`pipeline/prompts/output_contract.json`). Prompt version `v1`.
- **Persona framing is observer, not role-play** (DD2): "describe how a 72-year-old
  woman in Singapore typically behaves". DD2 records this as chosen "to lower stereotype
  risk"; **that wording is now known to be too strong** (see the correction in §2). The
  defensible claim is narrower: observer framing avoids the persona-*assignment* effects
  Deshpande et al. document, but it is **not** established that it produces less
  stereotyped content — Cheng et al. found no significant difference between framings.
  The `run01` gender pattern in §10 occurred *under* observer framing, which is the local
  demonstration that DD2 is not a mitigation.
- **Aggregation**: `pipeline/aggregate.py` collapses the 3 repeats per cell into one
  canonical record, recording `primary_action_agreement` and `yield_likelihood_std` so
  the spread across repeats is retained rather than discarded.
- **Budget control**: `pipeline/estimate_cost.py` renders every prompt offline and
  projects cost before any call; the generator is budget-gated and resumable (it skips
  `raw_id`s already present in the raw log).

**Actual run cost and usage** *(recomputed from `raw/run01.jsonl`)*:

| Metric | Value |
|---|---|
| Calls | 420 (all `status: ok`) |
| Successfully parsed | **420 / 420 — 0 failures** |
| Prompt tokens | 485,496 (377,600 cache-hit / 107,896 cache-miss) |
| Completion tokens | 132,844 |
| Total tokens | 618,340 |
| **Actual cost** | **$0.0966** |

This matches the $0.097 recorded in `CLAUDE.md`. Budget is $2.00 with
`ALREADY_SPENT_USD = 0.10` in `pipeline/config.py`, so roughly $1.90 remains — enough
for further runs, which matters for the recommendations in §10.

**Caveat carried from `pipeline/config.py`**: the DeepSeek pricing table is marked
`VERIFY` in-file, so the $0.0966 figure depends on rates that were assumed, not
confirmed against DeepSeek's current pricing page.

## 10. Is the dataset verified, how, and is the verification method sound

**Short answer: partially. Automated checks pass; the two most convincing checks have
not been done yet.** `dataset/schema/VALIDATION.md` defines seven checks. Current status:

| # | Check | Status |
|---|---|---|
| 1 | Format validity | **Done, passes** — 0 FAIL |
| 2 | Reliability / internal consistency | **Done** — 12 low-agreement cells flagged for review |
| 3 | Face validity vs literature | **Partly done** — 3 of the 4 stated hypotheses tested, all PASS; the 4th is not implemented |
| 4 | Blind spot-check (~15 cells, by hand) | **NOT DONE** |
| 5 | Gender / age bias audit | **Flagged automatically; human judgement not yet applied** |
| 6 | Downstream / simulation validity | **NOT DONE** (requires step 7) |
| 7 | Optional human rating | **NOT DONE** |

From `dataset/generated/validation_report.md`: **0 FAIL, 54 REVIEW items, 3 INFO**. The
three reported directional hypotheses all passed: elderly walk slower than young
adults; children walk slower than young adults; elderly yield at least as much as young
adults. Mean `primary_action_agreement` is 0.753.

**Four findings computed for this update that are not in the existing report:**

1. **The gender skew is dataset-wide, not just the 11 flagged cells.** The validation
   report flags cells crossing a `|Δ yield_likelihood| > 0.25` threshold. Computing the
   difference across **all 70** `(scenario, age)` cells *(recomputed)*: **51 cells have
   female yielding more, 8 have male yielding more, 11 are equal; mean Δ (female −
   male) = +0.101.** So the threshold-based flag list *understates* the pattern — this
   is a systematic direction across the dataset, not a handful of outliers.
2. **33 of 140 records have `yield_likelihood_std` of exactly 0** *(recomputed)* —
   identical values across all three repeats. This is the "hyper-accuracy distortion"
   pattern Aher et al. describe (§7–§8), where an aligned model collapses response
   variance. With only 3 repeats it is weak evidence, but it is the right check and it
   now has a number.
3. **Two of the seven actions were never produced** — `back_off` and `reroute` are
   absent from all 140 records *(recomputed)*. Either those situations genuinely do not
   arise in these 14 scenarios, or the prompt does not elicit them.
4. **One stated validation check is silently missing.** `dataset/schema/VALIDATION.md`
   §3 lists **four** directional hypotheses, but only **three** appear in the report.
   Reading `pipeline/validate.py` (lines ~120–145) confirms the fourth — *"young adults
   at least as assertive as elderly"* — **is never implemented**. It did not fail; it
   was never run. Worth noting too that the third hypothesis is checked with a
   tolerance (`el_y >= ya_y - 0.05`), so "at least as much" allows a small shortfall.

**Is the verification method sound?** Partly, and its weaknesses are known:

- **Sound**: it is multi-method rather than a single score, which is what Zhong et al.
  §5.5 explicitly recommends ("a single validation approach can hardly cover all of
  these factors"). Directional hypotheses were stated *before* checking. Anchoring
  walking speeds to published ranges (Weidmann 1993, Bohannon 1997) is external
  grounding rather than self-consistency.
- **Weak — consistency is not accuracy.** `primary_action_agreement` measures whether
  the model repeats itself, not whether it is right. Three repeats at temperature 1.0 is
  a thin basis for either.
- **Weak — no human baseline at all.** By Hullman et al.'s distinction this is entirely
  *heuristic* validation; there is no auxiliary human data and no statistical
  calibration. The blind spot-check (check 4) is the closest thing to a pre-registered
  human comparison and **it has not been done** — `VALIDATION.md` itself calls it "the
  single most convincing thing in the report".
- **Weak — the gender audit is currently automated flagging only.** `VALIDATION.md` §5
  requires a human to judge each flagged cell as evidence-based or stereotype, and says
  "Do not silently accept them." That judgement has not been made. Cheng et al. supply a
  method (Marked Words on the `conflict_behaviour.narrative` and `decision_factors`
  fields) that has not been run.
- **Weak — the mitigation we assumed we had, we do not have.** DD2 (observer framing)
  was recorded as reducing stereotype risk. As of the 2026-09-08 correction in §2, that
  is unsupported: Cheng et al. tested both framings and found no significant difference,
  and the `run01` gender skew occurred under observer framing anyway. So the dataset has
  **no prompt-side stereotype mitigation** — only the (not yet performed) audit.
- **Weak — a stated check is missing without being reported as missing.** The
  assertiveness hypothesis is in `VALIDATION.md` but not in `validate.py`, and the
  report gives no indication it was skipped. A validation suite that silently omits one
  of its own stated checks is a process weakness independent of this dataset.
- **Not started — no downstream validity.** Nothing has been run in CrowdGym, so there
  is no evidence the dataset improves simulation behaviour (§7).

**Plainly: the dataset is format-valid and internally consistent, with three
literature-anchored directional checks passing. It is not yet validated against human
behaviour, and the gender pattern is an open, unresolved issue rather than a closed
one.**

## 11. Potential questions the professor might ask

Grounded in the specific weak points surfaced above.

**On the gender finding (§10) — the most likely line of questioning.**

1. *"Your dataset says women yield more than men in 51 of 70 cells. Is that a finding
   about Singaporeans, or an artefact of the model?"* — Current honest answer: most
   likely an artefact. Wang et al. §3.1 report LLMs are 3–6× more likely to produce
   gender-stereotypical behaviour, and Aher et al. found the same direction in the
   Ultimatum Game. We cannot currently distinguish the two.
2. *"What is your evidence that any of these gender differences are real?"* — There is
   none in the dataset itself. This needs external pedestrian literature, and if the
   evidence is absent, `VALIDATION.md` §5 requires either regenerating with a corrected
   prompt or keeping it and documenting it as a limitation.
3. *"Would the dataset still be useful if you removed gender entirely?"* — Worth having
   an answer ready; it would halve the persona count to 5 and remove the most
   contestable axis, at the cost of some heterogeneity.

4. *"You chose observer framing to reduce stereotype risk. What is your evidence that
   it does?"* — **Weaker than we first wrote.** Cheng et al. tested both first-person and
   observer framings and found no significant difference in stereotype word
   distributions. Deshpande et al. supports the narrower claim that persona *assignment*
   raises toxicity up to 6x, which observer framing avoids — but that is about assignment
   effects, not stereotype content. The honest answer is that DD2 avoids one known
   failure mode and is not a stereotype mitigation.

**On validation (§10).**

5. *"You say validation passes. What exactly passed?"* — Format and internal
   consistency, plus 3 directional hypotheses. Not human accuracy.
6. *"Why haven't you done the blind spot-check?"* — It is the check `VALIDATION.md`
   calls the most convincing, it needs no API budget, and it has not been done. There is
   no good answer except that it is next.
7. *"Three repeats at temperature 1.0 — is that enough to measure consistency?"* — Almost
   certainly not, and 33/140 records showing zero variance may reflect the small sample
   as much as model behaviour. ~$1.90 of budget remains, so more repeats are affordable.
8. *"Your validation document lists four hypotheses and your report shows three. What
   happened to the fourth?"* — It was never implemented in `validate.py`. This is the
   most awkward question in this list, because the report gives no sign the check was
   skipped.

**On the dataset itself (§8, §9).**

9. *"Two of your seven actions never appear. Is your action space wrong, or your
   prompt?"* — Unresolved; `back_off` and `reroute` were never produced.
10. *"Only 31 of 140 records are labelled Singapore-specific. Is the localisation doing
   any work?"* — A fair challenge to the whole Singapore framing, given the effort in
   the system prompt.
11. *"Your population weights — where did they come from?"* — They are **placeholders**.
   `personas.yaml` marks them `VERIFY` against SingStat, and `README.md` records this as
   assumption **A1**. This should be fixed before the report.
12. *"Is your cost figure right?"* — $0.0966 is measured from the raw log, but the
    pricing table in `config.py` is marked `VERIFY`, so the dollar conversion rests on
    assumed rates.

**On CrowdGym integration (§5, §6, §7).**

13. *"Have you actually run any of this in CrowdGym?"* — No. There is no adapter; the
    interface is documented from the senior's report and not verified against source.
14. *"Your speeds are 1.0–1.5 m/s but the senior's verification runs used 0.8 m/s. How
    will you compare?"* — `crowdgym_mapping.md` flags exactly this and says not to
    compare across the two baselines without rescaling or re-running.
15. *"You generate per persona but conflicts are pairwise. How do you get a pairwise
    outcome from single-persona data?"* — DD1: composed via `yield_likelihood` plus a
    `priority_bias` table that does not exist yet. This is an unvalidated design
    decision and probably the biggest technical risk.

**On the research gap and scope (§3, §4).**

16. *"How do you know nobody has done this?"* — We do not, at seven papers. The gap is
    stated as five specific absences in the reviewed work, and the wider-literature
    claim is explicitly marked unverified.
17. *"You want 10,000 agents. What is your evidence the frozen-table approach gets you
    there?"* — Only that it removes API calls from the loop. No performance measurement
    has been done at any scale.

---

## Status against the roadmap

From `README.md`:

1. ✅ Dataset schema
2. ✅ Scenario registry, persona list, action space
3. ✅ Prompt templates
4. ✅ Token-cost estimator
5. ✅ Generated — run01, 420 calls, 140 records, $0.0966
6. 🔶 Validation — automated checks pass (0 FAIL); 54 REVIEW items outstanding; blind
   spot-check and gender-audit judgement still to be done by hand
7. ⬜ Wire into CrowdGym — not started; adapter not written

**Added since the last update:** the literature review (issue #2, 7 papers) and its
standalone README (issue #4).

## Proposed next steps

1. **Do the blind spot-check** (`VALIDATION.md` §4). No API cost, and it is the most
   convincing single item available.
2. **Resolve the gender pattern** — apply Cheng et al.'s Marked Words contrast to the
   `narrative` / `decision_factors` fields, and decide per flagged cell: evidence-based
   or stereotype. Bring the 51/70 figure to the supervisor as a decision point.
3. **Replace the placeholder population weights** with real SingStat figures (assumption
   A1).
4. **Raise `REPEATS`** above 3 for at least a subset, to test whether the 33 zero-variance
   records are real distortion or small-sample noise. Budget allows it.
5. **Reword DD2 in `README.md`** to match what the literature supports — "avoids
   persona-assignment effects (Deshpande et al.)" rather than "lower stereotype risk" —
   and consider testing the two framings directly on a subset of cells, which the
   remaining budget easily covers.
6. **Implement the missing fourth directional hypothesis** in `pipeline/validate.py`,
   and make the validator report stated-but-unimplemented checks explicitly rather than
   omitting them silently.
7. **Confirm the CrowdGym interface against the actual source** before writing the
   adapter, as `crowdgym_mapping.md` instructs.
