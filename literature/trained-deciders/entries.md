# Trained deciders: literature entries

> For issue [#38](https://github.com/M450NCH00/CrowdSimulation/issues/38), PT-4 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). Literature only. The idea these
> entries serve (trained models behind the same Situation → Decision interface as the rules) is
> **a proposal, not agreed**; it needs the supervisor's sign-off.
>
> - Every entry was confirmed from its own page (arXiv record plus the publisher or proceedings
>   page), and its status is recorded.
> - Locators are to the version read, which is named in each entry. `[inference]` marks my own
>   reasoning, not the source's claim.
> - Text extracts are in `refs/td_*.txt`, made with `pdftotext -enc UTF-8` (reading order, no
>   `-layout`, because most copies are two-column).

Companion files: [options](options.md) · [evaluation](evaluation.md) · [verdict](verdict.md) ·
[search log](search-log.md) · [missing papers](missing-papers.md) ·
[BibTeX](refs-trained-deciders.bib)

**Contents**
- Q1 distillation of LLM decisions: [Zhang-DFD] and [Fang-Etiquette] (cross-references) ·
  [Amano-MobilityLM] · [Chopra-Archetypes] · [Li-GenWorld]
- Q2 interpretable learned rules: [Rudin-StopExplaining] · [Bastani-VIPER] · [Yang-S2AN]
  (cross-reference)
- Q3 rules as constraints or rewards: [Icarte-RewardMachines] · [Alshiekh-Shielding] ·
  [Chen-SACADRL]
- Q4 bias checks: [Kusner-CF] · [Garg-CFText] · [Tamkin-Discrim]
- Q5 teachers: [Hu-LogicRules] · [Plaza-ModelCrowds]

---

## Q1. Distilling LLM decisions into fast deciders

### Cross-references (not summarised again)

- **[Zhang-DFD]** (Zhang, Andelfinger, Tan & Cai 2026, *ACM TOMACS*, Just Accepted;
  `literature/paper-summaries/02-sense-think-act-reflect.md`). For this issue the points that
  matter, with that summary's locators:
  - *Model and teacher*: LLM-written, numerically refined Python decision functions; teacher is
    Gemma3:27b driving an evacuation simulation (summary §2, §5).
  - *Out-of-domain*: it is the only Q1 source with a held-out "generalize" set, and DFD stays
    ahead of PySR and LLM-SR there (Tables 3 and 4, pp. 17 and 19 of the paper).
  - *Cost*: distillation about 5 days against about 1 day per LLM-driven simulation run, so it
    pays back after about 10 runs (§5.5, p. 19). N = 100 agents in every experiment (§5.1).
  - *Validity*: "depends directly on the reference data" (§6.1), which is LLM-generated, not human.
- **[Fang-Etiquette]** (Fang, Xiao, Hsu & Lee 2026, *IEEE RA-L* 11:3947–3954;
  `literature/llm-behavioural-conflict/llm-behavioural-conflict.md`). GPT-4o judgements on SCAND
  frames, distilled by supervised fine-tuning into Qwen-2.5 7B because GPT-4o is too slow for
  real-time use (that entry, "fine-tuning subsection"). The student picks among paths a geometric
  planner has already made collision-free. One robot, four scenarios, three trials each (§V-B).
  `[inference]` It shows that the "small language model" option can run in real time for **one**
  agent; it says nothing about 10,000.

### [Amano-MobilityLM]: Distilling Aggregate Mobility Statistics into a Language Model Policy for Post-Event Crowd Simulation
- Authors / Year / Venue / Link: Tatsuya Amano, Hirozumi Yamaguchi / 2026 / accepted as a short
  paper at ACM SIGSPATIAL 2026 (arXiv comment) / https://arxiv.org/abs/2608.19778. The arXiv
  record gives DOI 10.1145/3841645.3843407, which **did not resolve on Crossref** on 2026-10-18.
- Status: `[preprint]` (accepted, not yet published); Read: full text (4 pages), arXiv v1,
  `refs/td_amano2026_mobility.txt`.
- Model type, and its teacher: a single shared language model (gpt-oss-20b with a LoRA adapter)
  is the decision policy for every agent (§2.1; §4). Two teachers: synthetic decision examples
  sampled from the base policy, with rationales written by gpt-5-mini (format pass, §2.1, §4); then
  the model's own rollouts resampled so that their destination shares match **real** aggregate
  origin–destination counts from mobile-network data (§3; §4).
- Inputs and outputs: persona plus local situation as text → one of three actions: go to a point
  of interest, wait, or leave (§2.2). Output carries a short PERCEIVE/STATE/GOAL/DECIDE rationale
  that the simulator discards (§2.1; Fig. 2).
- Fidelity to the teacher, and how it was measured: against the human aggregates, not against an
  LLM. Destination-share error (summed absolute difference of three shares) falls from 0.31 (no
  grounding) to 0.23 (Fig. 3b), "about a quarter" (§1; §5); grid correlation is about 0.76 for
  every calibrated policy and "alone leaves them indistinguishable" (§1; Fig. 3a). A key finding:
  naive fine-tuning **amplifies the majority class** — training at a 74% station share deploys
  "above 94%" (§1; §3).
- Behaviour outside the training data: one test. Calibrated on the dry game day, run on the
  rainy day with a rain sentence added; mall-occupancy cosine similarity to the real rainy day rises
  from 0.59 to 0.74 (§5). The authors call this "demonstrated under a single condition" (§6).
- Cost: one H100 GPU for fine-tuning; 1,756 and 1,663 training examples (§4). Run-time cost per
  decision is **not reported**. Largest population tested: **500 agents** × 10 seeds (§4), although
  the real crowds were about 31,000 (§4).
- Can a person read what it does?: only the per-decision rationale, which is discarded (§2.1).
  `[inference]` The policy itself is a 20B-parameter model and is not readable.
- Guarantees: none stated.
- Bias or protected-attribute checks: none. Personas carry age band, group makeup and residence
  type (§2.2); no test of whether these change decisions.
- What it means for "several models trained on the rules": `[inference]` Two transferable lessons.
  (1) A student fine-tuned on a skewed label set can exaggerate the majority decision; any rule-
  trained student should be checked for this (in our data the majority might be "wait"). (2) An
  aggregate metric can hide large behavioural differences (§1; Fig. 3); a decider must be checked
  decision by decision, not only by crowd-level flow. It is **not** a fast decider: per-decision
  inference is still an LLM call.
- BibTeX: `amano2026distilling`

### [Chopra-Archetypes]: On the Limits of Agency in Agent-Based Models
- Authors / Year / Venue / Link: Ayush Chopra, Shashank Kumar, Nurullah Giray-Kuru, Ramesh
  Raskar, Arnau Quera-Bofarull / 2025 / *Proc. AAMAS 2025*, pp. 500–509, DOI 10.65109/fbdx5907
  (Crossref) / https://arxiv.org/abs/2409.10568
- Status: published at AAMAS 2025; Read: full text, arXiv v3, `refs/td_chopra2025_agency.txt`.
- Model type, and its teacher: no trained model. "LLM archetypes": agents are grouped by their
  prompt attributes, the LLM (GPT-3.5 or GPT-4o) is queried M times per archetype, and each agent
  **samples** its action from its archetype's estimated distribution (§3, Eq. 7; Fig. 1). This is
  a lookup table filled by an LLM. `[inference]`
- Inputs and outputs: age, gender, location (borough) and income in the prompt, plus shared
  disease and stimulus context (§4, prompt template; §5) → a binary action ("will
  you work?", isolation) (§5).
- Fidelity to the teacher: not measured against fresh LLM calls. Measured against **real** data:
  positive time-varying correlation with Bureau of Labor Statistics participation rates in "3 of 5
  boroughs" (§5; Fig. 2). Forecast MSE (Table 1): unemployment 24.59 (archetypes) against 41.05
  (heuristic) and 56.98 (LLM-as-agent, 300 agents scaled up); infections 95.17 against 2914.73 and
  4311.70.
- Behaviour outside the training data: counterfactual prompts (pandemic fatigue offset; earlier
  Omicron) are run (§7; Fig. 5), but these are not checked against any observation. Not tested in
  the sense of a held-out ground truth.
- Cost: "only 400 queries for 8.4 million agents" per weekly decision (§5); archetypes use "95%
  less run-time compared to LLM-as-agents and marginally more than heuristic agents" (§6; Fig. 4).
  Largest population: **8.4 million** (Abstract; §5).
- Can a person read what it does?: `[inference]` yes in the sense that the table (archetype →
  action probability) can be printed and inspected; no in the sense that why the LLM chose those
  probabilities is not recorded.
- Guarantees: none.
- Bias or protected-attribute checks: none run. The authors list "robustness and fairness" as
  open (§8, Limitations). Gender and age are direct inputs.
- Other stated limits: sensitivity to the model and to M — at M = 1, GPT-4o beats GPT-3.5; at larger
  M, GPT-3.5 improves "significantly" (§8; Fig. 6); archetypes "may not always capture the desired
  heterogeneity" (§8).
- What it means for "several models trained on the rules": `[inference]` The cheapest possible
  learned decider is a table keyed by Situation features, filled by repeated teacher calls. This
  scales (8.4M agents) because the number of distinct Situations, not agents, sets the cost. It is
  the natural baseline every trained model should beat. It also shows **scale beat agency** here:
  heuristic agents at full scale beat LLM agents at 300 (§6; Table 1). That is one domain
  (epidemic and labour), not crowd conflict.
- BibTeX: `chopra2025limits`

### [Li-GenWorld]: GenWorld: Empirically Grounded Urban Simulation Infrastructure for Scalable LLM-Agent Studies
- Authors / Year / Venue / Link: Gen Li, Jieyuan Lan, Pengcheng Xu, Zongyuan Wu, Masaki Ogura, Tao
  Feng / 2026 / arXiv:2606.27650 / https://arxiv.org/abs/2606.27650
- Status: `[preprint]`; no published version found (arXiv record has no journal reference;
  2026-10-18). Read: §1–§4, §7.1.5, §7.2 and §8 by keyword-led passes; §5 (population synthesis)
  skimmed. `refs/td_li2026_genworld.txt`.
- Model type, and its teacher: "policy compilation". A teacher LLM (Gemma 3 27B) is queried K =
  10–30 times per discretised context key; its scores are averaged into a categorical distribution
  and stored as a lookup table (§4; §8 "Distillation Fidelity"). The simulator also supports rule-
  based and "distilled-student" policies behind the same interface (§6.1, Layer 2;
  Algorithm 1, line 7, "rule/teacher/student").
- Inputs and outputs: persona and state binned into a context key (persona bins, time bins, coarse
  location type, scenario and day-type indicators) → a choice from a finite, validated candidate
  set (§3; §4 "Action Primitives and Context Discretization"; "Policy Compilation").
- Fidelity to the teacher: **not measured**. "We also do not quantitatively compare distilled
  outputs against fresh teacher queries (e.g., via KL divergence or decision agreement rate)" (§8).
  Schedules are compared with the national time-use survey, r > 0.86 (§7.2).
- Behaviour outside the training data: unseen context keys "may require backing off to coarser keys
  or a conservative default" (§4); transfer to other cities "may not" hold "without local
  calibration" (§8 "Generalizability"). Not tested.
- Cost: lookup at 0.54 µs per query, 1.85 M queries/s in Python on one desktop CPU (§4; §7.1.5),
  against 0.5–2 s per call for a local 7B model (§7.1.5). About 200,000 agents (§2.4; §8).
- Can a person read what it does?: `[inference]` the table can be printed; the teacher's reasons
  are not kept.
- Guarantees: none.
- Bias or protected-attribute checks: none.
- What it means for "several models trained on the rules": `[inference]` Same lesson as
  [Chopra-Archetypes], with two additions. (1) The teacher's own **variability** per key is recorded
  (σ, §4) and used to find unstable regions; a rule-or-LLM-trained decider should record the same.
  (2) The authors name the missing check themselves: agreement with fresh teacher calls. That check
  belongs in [evaluation](evaluation.md).
- BibTeX: `li2026genworld`
