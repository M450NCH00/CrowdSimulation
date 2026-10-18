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

---

## Q2. Learning interpretable rules from labelled decisions

### Cross-references (not summarised again)

- **[Yang-S2AN]** (Yang et al. 2024, AAMAS; `literature/simulation-rules/s3-mapf-robotics.md`,
  and `research-gap.md` §6). The one direct comparison in this repository of a **learned** order
  against a **hand-written** one (PIBT, PBS). The learned network wins on success rate in
  obstacle-dense maps and where PBS times out at 140–250 agents (§5.2). It loses on speed (PIBT
  "less than 1 second"; S2AN "within seconds" up to 180 agents), scale (250 agents at most),
  information needed (the whole instance, centrally) and readability ("cannot be written down as a
  rule") (that entry, citing §1, §5.2, §5.3). This learned model is **not** interpretable: it is a
  contrast case for Q2, not an example of it.
- **[Zhang-DFD]**'s baselines: PySR (classical symbolic regression) and LLM-SR. Both produce
  readable formulas from (perception, choice) pairs. PySR was the worst model in every column of
  both tables (DTW 171.38 / 184.93 / 118.92 against DFD's 4.65 / 2.87 / 1.11; Table 4, p. 19 of the
  paper). Not read separately; listed in the [search log](search-log.md) as leads.

### [Rudin-StopExplaining]: Stop Explaining Black Box Machine Learning Models for High Stakes Decisions and Use Interpretable Models Instead
- Authors / Year / Venue / Link: Cynthia Rudin / 2019 / *Nature Machine Intelligence* 1:206–215,
  doi:10.1038/s42256-019-0048-x / https://arxiv.org/abs/1811.10154 (the author's pre-publication
  version, per its arXiv comment)
- Status: published in *Nature Machine Intelligence*; Read: full text of arXiv v3 (the author's
  version), `refs/td_rudin2019_stop.txt`. Locators are to that version's section numbers. **It is a
  perspective (argument) paper**, not an experiment: its claims are the author's, supported by
  cited studies and one worked example.
- Model type, and its teacher: argues for models that are interpretable by construction (sparse
  logical models such as rule lists and decision trees; integer scoring systems), trained on the
  data, rather than black boxes explained afterwards (§1; §5).
- Inputs and outputs: structured features → a decision. Worked example: a three-rule list from
  CORELS on age, priors and (optionally) gender predicts re-arrest about as well as the 130+ factor
  COMPAS tool (Fig. 3; Table 1, "similar true and false positive rates").
- Fidelity: the central claim is about accuracy, not fidelity. "When considering problems that
  have structured data with meaningful features, there is often no significant difference in
  performance between more complex classifiers ... and much simpler classifiers (logistic
  regression, decision lists)" (§2 (i); Appendix B). Her reason: the **Rashomon set**. If many
  models fit the data about equally well, some of them are likely to be simple (section "A
  Technical Reason Why Accurate Interpretable Models Might Exist in Many Domains").
- On explanations of a black box: an explanation model can match the black box's outputs while
  using "completely different features", and "is thus not faithful to the computation" (§2 (ii)).
- Behaviour outside the training data: not addressed.
- Cost: interpretable models "can entail significant effort to construct, in terms of both
  computation and domain expertise" (§3 (ii)); optimal sparse models are hard optimisation problems
  (§5). Per decision, a rule list is a few comparisons. `[inference]`
- Can a person read what it does?: that is the paper's definition of interpretable, with sparsity
  as a measure because "humans can handle at most 7±2 cognitive entities at once" (§1).
- Guarantees: none claimed. Instability: small changes in the data can give very different trees,
  which the author ties to the Rashomon effect (Appendix E).
- Bias or protected-attribute checks: argued, not run. A transparent model shows which features it
  uses, so a reader can see whether it uses race (§2 (ii)). `[inference]`
- What it means for "several models trained on the rules": `[inference]` (1) Situation features in
  this FYP are structured and meaningful (arrival order, age, mobility aid): the case where Rudin
  says simple models usually match complex ones. So a deep model must earn its place by beating a
  shallow tree **on our data**, not by assumption. (2) Appendix E predicts that two trees trained on
  slightly different rule or LLM samples may look very different while deciding alike. Compare
  trained deciders by their **decisions**, not by their shapes. (3) Her claim is made for
  high-stakes decisions on structured data; crowd decisions are not tested in the paper.
- BibTeX: `rudin2019stop`

### [Bastani-VIPER]: Verifiable Reinforcement Learning via Policy Extraction
- Authors / Year / Venue / Link: Osbert Bastani, Yewen Pu, Armando Solar-Lezama / 2018 /
  *Advances in Neural Information Processing Systems 31* (NeurIPS 2018) /
  https://proceedings.neurips.cc/paper/2018/hash/e6d8545daa42d5ced125a4bf747b3688-Abstract.html ;
  https://arxiv.org/abs/1805.08328
- Status: published at NeurIPS 2018; Read: full text, arXiv v2 (proofs in the appendix not
  followed), `refs/td_bastani2018_viper.txt`.
- Model type, and its teacher: a **decision tree** extracted by imitation from a trained neural
  policy (a deep Q-network or a policy-gradient network; iLQR for one task) (§2; §4). VIPER extends
  DAgger: the student is trained on the states **it itself visits**, and each state is weighted by
  how much the choice of action matters there, using the teacher's Q-function (§1; §2).
- Inputs and outputs: low-dimensional state (7 numbers for Pong; the cart-pole state) → a
  discrete action (§4).
- Fidelity to the teacher, and how it was measured: by reward, not by decision agreement. Trees
  match the teacher's perfect reward on Atari Pong (769 nodes; 21.0 against 21.0), toy Pong (31
  nodes) and cart-pole (3 nodes suffice) (§1; §4; Fig. 4a). On half-cheetah a 9,757-node tree
  reaches 4,014 against the network's 4,189 (§4). Against plain DAgger, VIPER's trees are an order
  of magnitude smaller for the same reward (769 against 7,967 nodes at R = 21; Fig. 4c; §4).
- Behaviour outside the training data: not tested as such. Instead, **verification found a
  failure the reward did not show**: in toy Pong, Z3 found a start state "near the edge of the
  screen" where the 31-node tree can miss the ball, although it "plays perfectly" over 50 rollouts
  (§4). The authors repaired it by hand by adding one top-level node, then proved the property
  (§4).
- Cost: verifying the trees took seconds (robustness 2.9 s per point; correctness under 5 s; §4),
  against 12 s to over an hour per point with Reluplex on the network (§4). Training cost is not
  given as a single figure. Population: single-agent tasks.
- Can a person read what it does?: `[inference]` a 3- or 31-node tree, yes; a 769- or 9,757-node
  tree, not in practice. The paper's goal is verifiability, not readability (§1).
- Guarantees: the general algorithm, Q-DAgger, has "theoretical guarantees improving on DAGGER's"
  (§2). **For trees these do not carry over**: the tree loss is not convex, so VIPER fits each
  iteration with CART as "a heuristic" (§2, "Extracting decision tree policies"). Properties of the
  extracted tree
  (correctness, stability, robustness) can be **proved** with standard solvers (§3; §4), with the
  stated limit that the dynamics must be polynomial (Taylor approximations used; §3).
- Bias or protected-attribute checks: none.
- What it means for "several models trained on the rules": `[inference]` Three lessons. (1)
  **Sample the student's own situations**, not only the teacher's: a tree trained only on the
  situations a rule-following simulation produced may meet situations it never saw once it drives
  the simulation itself (the DAgger point, §1–§2). (2) Weight situations by how much the decision
  matters (for us, those close to deadlock). (3) A tree over Situation features can be **checked
  exhaustively** for properties such as "the decision never depends on X"; a neural model cannot
  be, at the same cost. The domain here is control, not crowds.
- BibTeX: `bastani2018verifiable`

---

## Q4. Checking a trained decider for bias

The template's fields are kept, but for these three sources the important ones are the definition
of the test and its stated limits.

### [Kusner-CF]: Counterfactual Fairness
- Authors / Year / Venue / Link: Matt J. Kusner, Joshua R. Loftus, Chris Russell, Ricardo Silva /
  2017 / *Advances in Neural Information Processing Systems 30* (NeurIPS 2017) /
  https://proceedings.neurips.cc/paper/2017/hash/a486cd07e4ac3d270571622f4f316ec5-Abstract.html ;
  https://arxiv.org/abs/1703.06856
- Status: published at NeurIPS 2017; Read: full text, arXiv v3 (supplementary proofs skimmed),
  `refs/td_kusner2017_cf.txt`.
- Model type, and its teacher: a definition plus a method; demonstrated with logistic or linear
  regression on real data (law-school first-year grades, 21,790 students; §5).
- The definitions it sets side by side (§2.1): *fairness through unawareness* (the protected
  attribute A is "not explicitly used", Definition 1); individual fairness; demographic parity;
  equality of opportunity. Their criticism of unawareness: other inputs "can contain
  discriminatory information analogous to A" (§2.1).
- Its own definition (Definition 5, §3): a predictor is counterfactually fair if, for an
  individual, the distribution of its prediction would be the same had A been different, **with the
  individual's background factors U held fixed** in a causal model. Lemma 1 (§3.2): a predictor
  that uses only **non-descendants** of A in the causal graph is counterfactually fair.
- Fidelity / accuracy cost: on law-school data, RMSE 0.873 (uses race and sex), 0.894 (unaware),
  0.929 and 0.918 (two counterfactually fair models) (Table 1). The unaware model **fails** the
  counterfactual test, because grades it uses are themselves caused by race and sex in the assumed
  model (§5; Fig. 2).
- Behaviour outside the training data: not tested.
- Cost: needs a causal model of how the attributes relate; "even if strong assumptions are
  necessary" (§2.1). Three levels of assumption are offered (§4.2).
- Guarantees: if the causal model is right, Lemma 1 holds by construction (§3.2). Everything
  rests on the assumed graph (§4.2–§4.3).
- What it means for "several models trained on the rules": `[inference]` This FYP's rule "no model
  may take `ethnic_group` as an input" is **fairness through unawareness** (Definition 1), which
  Kusner et al. show is not enough when other inputs carry the attribute. In this simulator, though,
  the causal graph is **ours to write**: `ethnic_group` is assigned, and no feature is caused by it
  unless the scenario generator makes it so (for example by spawning groups at different ends of a
  corridor). So a stronger guarantee is cheap here: check, from the generator, that no Situation
  feature is a descendant of `ethnic_group`; then Lemma 1 applies. The one channel left is the
  **labels**: an LLM teacher that saw the group could pass its bias into labels even when the
  student never sees the group. That needs the counterfactual test of
  [evaluation](evaluation.md) on the teacher too.
- BibTeX: `kusner2017counterfactual`

### [Garg-CFText]: Counterfactual Fairness in Text Classification through Robustness
- Authors / Year / Venue / Link: Sahaj Garg, Vincent Perot, Nicole Limtiaco, Ankur Taly, Ed H. Chi,
  Alex Beutel / 2019 / *Proc. 2019 AAAI/ACM Conference on AI, Ethics, and Society (AIES '19)*,
  pp. 219–226, doi:10.1145/3306618.3317950 / https://arxiv.org/abs/1809.10610
- Status: published at AIES 2019; Read: full text, arXiv v2, `refs/td_garg2019_cftext.txt`. The
  arXiv copy has unnumbered sections; locators name them.
- Model type, and its teacher: CNN toxicity classifiers trained on 160K labelled Wikipedia comments
  (Experiments, "Dataset").
- The test: **counterfactual token fairness (CTF)**. Swap the identity term in an input for each
  other identity term and measure the mean absolute change in the model's output, the "CTF gap"
  (Definition 2; Experiments, "Metrics"). 50 identity terms; 35 used in training and 12 held out
  (Experiments, "Setup").
- Three ways to reduce the gap (Methods): **blindness** (replace every identity term with one
  IDENTITY token), counterfactual augmentation, and counterfactual logit pairing (a penalty on
  output differences between counterfactual pairs).
- Fidelity: gaps on the training terms (Table 1, non-toxic evaluation examples): baseline 0.140,
  blindness 0.000 "by design", augmentation 0.127, logit pairing λ = 5 0.002.
- Behaviour outside the training data: on the 12 **held-out** terms (Table 2) every method is near
  the baseline (0.091): blindness 0.090, logit pairing λ = 5 0.076 (best). "Blindness does not
  appear to provide generalization benefits" (Results).
- Limits stated: **asymmetric counterfactuals** — swaps for which the right output really should
  differ, so forcing equality is wrong (section "Asymmetric Counterfactuals"). Blindness "may still
  discriminate using other signals that are associated with the identity term" (Methods,
  "Blindness").
- Cost: one regularisation term in training (Methods). Per decision: unchanged.
- Can a person read what it does?: no (CNN).
- Guarantees: blindness guarantees a zero gap for the listed terms only (Methods, "Blindness").
- What it means for "several models trained on the rules": `[inference]` (1) The CTF gap is
  directly usable as **the counterfactual bias test**: same Situation, flip one attribute, measure
  the change in the decider's output, averaged over Situations. (2) The asymmetric case is exactly
  this FYP's second rule: the test applies **only where a rule says an attribute must not matter**.
  Where a rule says age or a mobility aid *should* matter (giving way to the elderly), a gap is
  expected and is not bias. (3) Removing an input (blindness, or our "no `ethnic_group`") passes the
  test trivially for that input, and tells you nothing about proxies.
- BibTeX: `garg2019counterfactual`

### [Tamkin-Discrim]: Evaluating and Mitigating Discrimination in Language Model Decisions
- Authors / Year / Venue / Link: Alex Tamkin, Amanda Askell, Liane Lovitt, Esin Durmus, Nicholas
  Joseph, Shauna Kravec, Karina Nguyen, Jared Kaplan, Deep Ganguli (Anthropic) / 2023 /
  arXiv:2312.03689 / https://arxiv.org/abs/2312.03689
- Status: `[preprint]`. No published version found (Crossref title search, 2026-10-18).
  **Conflict of interest to note:** the authors work at Anthropic and test Anthropic's Claude 2;
  this review is written with an Anthropic model. Read: full text, arXiv v1,
  `refs/td_tamkin2023_discrim.txt`.
- Model type, and its teacher: no trained model; an LLM used as a decision-maker on 70 yes/no
  decision questions (loans, visas, hiring), written by an LLM and checked by people (§2; Table 1).
- The test: fill each question template with every combination of age (20–100 by tens), gender
  (3) and race (5): 9 × 3 × 5 × 70 = 9,450 prompts (§2). **Explicit** (attributes stated) and
  **implicit** (a name suggests race and gender) versions (§2). The effect of each attribute is
  estimated by a **mixed-effects regression** on the logit of p(yes), with question template as a
  random effect; the coefficient is the "discrimination score", 0 meaning none (§3.1, §3.2).
- Results for Claude 2: positive discrimination for women, non-binary and non-white subjects, and
  **negative discrimination for subjects over 60**; smaller when race and gender are implicit
  (§3.3; Figs. 2–3). Robust to the question's style and format in direction (§4; Fig. 4).
- Mitigation: appended prompt statements ("illegal to discriminate", "ignore demographics") bring
  the score to about 0.15 while keeping about 92% correlation with the original decisions (§5.3,
  §5.4; Fig. 6).
- Behaviour outside the training data: n/a. Limits stated (§6.1): paragraph-long inputs only; no
  intersectional effects; names as proxies are hard to choose; sensitivity to prompt wording
  "remains possible".
- Cost: 9,450 model calls per model tested (§2). `[inference]`
- What it means for "several models trained on the rules": `[inference]` (1) It is the template for
  testing an **LLM teacher** before its labels are used: full factorial over the attributes,
  decision probability as the outcome, mixed-effects model with Situation as a random effect. (2)
  The age finding matters here: this FYP's rules may *intend* age to matter (priority to the
  elderly), so the regression must separate intended effects (written in a rule) from unintended
  ones. (3) The 92% correlation figure is a way to report what a fairness fix costs: agreement with
  the unfixed decisions.
- BibTeX: `tamkin2023evaluating`

---

## Q3. Rules as constraints or rewards for learned policies

### [Icarte-RewardMachines]: Reward Machines: Exploiting Reward Function Structure in Reinforcement Learning
- Authors / Year / Venue / Link: Rodrigo Toro Icarte, Toryn Q. Klassen, Richard Valenzano, Sheila A.
  McIlraith / 2022 / *Journal of Artificial Intelligence Research* 73:173–208,
  doi:10.1613/jair.1.12440 / https://arxiv.org/abs/2010.03950. It extends the conference paper:
  Toro Icarte, Klassen, Valenzano & McIlraith (2018), "Using Reward Machines for High-Level Task
  Specification and Decomposition in Reinforcement Learning", *Proc. ICML 2018*, PMLR 80:2107–2116,
  https://proceedings.mlr.press/v80/icarte18a.html (confirmed from the PMLR page; **not read**:
  the journal version "builds upon our previous work" and gives "a cleaner definition", §1).
- Status: published in *JAIR*; Read: §1, §3, §4 (method descriptions and stated theorems, proofs
  not followed), §5 (findings list and §5.4), §7, of arXiv v2, `refs/td_icarte2022_rm.txt`.
- Model type, and its teacher: RL policies (tabular Q-learning, DQN, DDPG) whose **reward** is
  written as a finite-state machine over high-level events, a "reward machine" (Definition 3.1).
  A **labelling function** maps each environment transition to the events that are true (§3,
  Definition 3.3). The rules are the reward; there are no labelled decisions.
- Inputs and outputs: environment state plus the machine's current state → action (§4.1, the
  cross-product).
- Fidelity: n/a (no teacher to match). What the machine adds is sample efficiency: "CRM and HRM
  outperform the cross-product baselines in all our experiments"; CRM "converges to the best
  policies in all but one experiment"; HRM learns faster at first "but converges to suboptimal
  policies" (§5, findings list).
- Behaviour outside the training data: not tested for reward machines. The authors say that
  generalising to unseen tasks is something they "do not know how to achieve ... using RMs" (§7).
- Cost: the methods that exploit the machine cost more compute per step than the baseline (§5.4;
  Table 4). Without them, one task was not solved by DDPG in "30 millions steps (over 3 days of
  computation)" (§5.4). Domains: gridworlds, a continuous water world, half-cheetah (§5.1–§5.3).
  Single agent.
- Can a person read what it does?: the **reward** can be read (it is a small automaton; Fig. 1b);
  the learned policy cannot. `[inference]`
- Guarantees: CRM with tabular Q-learning "converges to an optimal policy" for the machine-defined
  task, given infinite visits (Theorem 4.1); automated reward shaping keeps the set of optimal
  policies (§4.4); HRM "might converge to sub-optimal solutions" (§4.3). Assumption: a **correct
  labelling function**; noisy event detectors are an open problem (§7). Expressiveness: any reward
  that depends on history only through regular-language patterns (§3, the three properties).
- Bias or protected-attribute checks: none.
- What it means for "several models trained on the rules": `[inference]` The **labelling function
  plays the role of the proposed perception adapter**: it turns simulator state into the
  propositions a rule talks about. So a rule core written over the vocabulary could be compiled into
  a reward machine with no change, and an RL policy trained in one simulator would get its reward
  from the same rules as the engine. But the guarantee is "optimal for the reward", not "obeys the
  rule": a penalty can be outweighed. And the policy is learned per simulator, so it does not carry
  over; only the reward does.
- BibTeX: `toroicarte2022reward`; `toroicarte2018using` (the ICML version, cited only)

### [Alshiekh-Shielding]: Safe Reinforcement Learning via Shielding
- Authors / Year / Venue / Link: Mohammed Alshiekh, Roderick Bloem, Rüdiger Ehlers, Bettina
  Könighofer, Scott Niekum, Ufuk Topcu / 2018 / *Proc. AAAI Conference on Artificial Intelligence*
  32(1), doi:10.1609/aaai.v32i1.11797 / https://arxiv.org/abs/1708.08611
- Status: published at AAAI 2018; Read: §1, §4–§9 of arXiv v2 (the long version), proofs in §6.1
  not followed, `refs/td_alshiekh2018_shield.txt`. ⚠ Section numbers are those of the arXiv copy and
  may differ from the AAAI version.
- Model type, and its teacher: any RL learner, with a **shield** between it and the environment.
  The shield is synthesised in advance from a temporal-logic safety specification and a coarse
  finite-state **abstraction** of the environment (§1; §4; §6).
  - *Preemptive*: the shield gives the learner the list of safe actions each step (§5.1).
  - *Post-posed*: the shield watches the learner's action and replaces it "if and only if the chosen
    action is unsafe" (§1; §5.2). This one "works even if the learning algorithm is already in the
    execution phase", and "the learning agent does not even need to know that it is shielded"
    (§5.2).
- Inputs and outputs: the abstraction's labels of the state plus the proposed action → a safe
  action (§5).
- Fidelity: n/a. Effects: shielded agents never violate the specification and "tend to learn more
  rapidly" in the grid worlds (§8.1; Fig. 11); in the car example the unshielded learner "still
  experiences crashes at the end", the shielded one "never crashes" (§8.2; Fig. 12).
- Behaviour outside the training data: the guarantee holds wherever the environment behaves as
  the abstraction says (§6.1, §7). Not tested beyond that.
- Cost: synthesis took 0.6–2 s for the grid-world and car shields (§8.1, §8.2). Shields "can be
  relatively large" because their state space is the product of the abstraction's and the
  specification's (§7). Single learning agent in each domain (§8).
- Can a person read what it does?: the specification can; the shield is an automaton generated
  from it. `[inference]`
- Guarantees: **correctness** (the specification is never violated) and **minimal interference**
  (an action is blocked only if it could lead to a violation), both proved (§6.1). Convergence:
  learners that converge on standard MDPs still converge, via a product MDP (§7). Assumptions: the
  environment can be modelled as an MDP, an abstraction has been built, and (preemptive case) the
  learner sees the shield's state (§5, Assumption 1).
- Bias or protected-attribute checks: none.
- What it means for "several models trained on the rules": `[inference]` This is the strongest
  pattern for a trained decider in this FYP: **a learned decider proposes, the rule engine
  disposes.** Hard rules (no collision; never act on `ethnic_group`) become the shield; the learned
  model chooses among what is left. A post-posed shield needs nothing from the learner, so it would
  sit in the rule engine and serve every simulator, which suits point 3 of the idea. What does
  **not** carry over is the abstraction: each simulator needs its own, the same work as the
  proposed perception adapter. The guarantees are for safety properties ("something bad never
  happens"), so a rule such as "the first to arrive goes first" fits; a soft preference does not.
- BibTeX: `alshiekh2018safe`

### [Chen-SACADRL]: Socially Aware Motion Planning with Deep Reinforcement Learning
- Authors / Year / Venue / Link: Yu Fan Chen, Michael Everett, Miao Liu, Jonathan P. How / 2017 /
  *Proc. 2017 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*,
  pp. 1343–1350, doi:10.1109/IROS.2017.8202312 / https://arxiv.org/abs/1703.08862
- Status: published at IROS 2017; Read: full text, arXiv v2, `refs/td_chen2017_sacadrl.txt`.
- Model type, and its teacher: a value network trained by deep RL in self-play, where a **social
  norm enters only as a reward penalty**: configurations in which another agent is on the
  "undesirable side" when passing, crossing or overtaking are penalised (§III-A; Eqs. 9–12; Fig. 4).
  Left-handed and right-handed versions are trained from the same start (§III-A).
- Inputs and outputs: the agent's state and up to three neighbours' observable states (four-agent
  network) → a velocity (§III-B; Fig. 5).
- Fidelity to the rule, and how it was measured: "norm preference", the share of trajectories that
  violate the left- or right-handed rule for more than 0.5 s, on 200 random test cases reflected to
  balance left and right (§IV-B; Table I). Trained policies reach an **85–15 split** for their
  norm, not 100–0, which the authors explain as a trade-off with time efficiency (§IV-B). ORCA is
  about 50–50 (§IV-B). On perfectly symmetric cases the norm is always followed (§IV-B).
- A finding worth noting: trained **without** the norm penalty, the policy still develops a
  convention, but a mixed one: it "prefers passing on the right but also overtaking on the right",
  so emergent conventions "don't always correspond to human social norms" (§IV-B).
- Behaviour outside the training data: one transfer, **simulation to a real robot**. Ten runs with
  goals over 50 m apart among real pedestrians (about 10.2 people per minute within 2 m); the
  vehicle "generally respected social norms" and the safety driver never intervened (§IV-C). No
  norm-preference figure is given for the hardware runs.
- Cost: training about nine hours for 3,000 episodes (four-agent network; §IV-A); 8.7 ms per
  decision in Python on one CPU (§IV-A); 10 Hz on the robot (§IV-C). Largest group trained: four
  agents (§IV-B).
- Can a person read what it does?: no; the norm is readable only in the reward (Fig. 4).
- Guarantees: none; the penalty set's size changes convergence speed, and too large a set "could
  lead to instability or divergence" (§III-A).
- Bias or protected-attribute checks: none. Agent attributes are radius and preferred speed only
  (§IV-A).
- What it means for "several models trained on the rules": `[inference]` (1) A rule given as a
  reward is followed **mostly** (85%), not always; anyone using rules as rewards should expect to
  measure compliance, not assume it. (2) Policies left alone invent conventions that differ from
  human ones, a reason to supply the rule rather than hope it emerges. (3) At 8.7 ms per decision,
  10,000 agents deciding every step is about 87 s per step on one core; this would need batching
  on a GPU or deciding only at conflicts. (4) This is the only Q3 source with a transfer to a new
  environment, and the evidence for it is qualitative.
- BibTeX: `chen2017socially`

---

## Q5. Teachers

The answer to Q5, teacher by teacher, is in [options](options.md) §1 (Q5). These two entries are
the evidence beyond the Q1–Q4 entries.

### [Hu-LogicRules]: Harnessing Deep Neural Networks with Logic Rules
- Authors / Year / Venue / Link: Zhiting Hu, Xuezhe Ma, Zhengzhong Liu, Eduard Hovy, Eric P. Xing /
  2016 / *Proc. 54th Annual Meeting of the Association for Computational Linguistics (ACL 2016)*,
  pp. 2410–2420, doi:10.18653/v1/P16-1228 / https://arxiv.org/abs/1603.06318
- Status: published at ACL 2016; Read: §1, §3 (method; the derivation of Eq. 4 not followed), §5,
  §6 of arXiv v6, `refs/td_hu2016_logicrules.txt`.
- Model type, and its teacher: a neural network (CNN for sentiment, BLSTM for named entities) as
  **student**, trained to match both the human labels and the soft predictions of a **teacher**
  built at each iteration by projecting the student onto the space allowed by a few first-order
  logic rules (for example the "but" rule: the sentiment of "A but B" follows B) (§3.2, §3.3;
  Fig. 1; Eq. 2). The teacher is rules **plus** the student, not rules alone.
- Inputs and outputs: a sentence → a sentiment class; a token sequence → entity tags (§4).
- Fidelity / accuracy: on SST2 sentiment, base CNN 87.2%, distilled student 88.8%, rule-regularised teacher
  89.3% (Table 2, rows 1, 7, 8). The teacher q "performs better than" the student p in general
  (§3.4), and the gap is larger where rules link several examples (§5.2).
- Behaviour with less data (the nearest thing to "outside the training data"): with 5% of the
  labels, 79.9% (base) against 81.5% (student) and 82.5% (teacher); with all labels, 87.2%
  against 88.8% and 89.3% (Table 3). The rules help **more when labels are scarce** (§5.1).
- Cost: one set of network parameters, no extra parameters for the rules (§5.1 on Table 2; §5.2);
  the student is "more lightweight and efficient", and needed when "rule evaluation is expensive or
  impossible at prediction time" (§3.4).
- Can a person read what it does?: the rules can be read; the student cannot.
- Guarantees: none. The rules are soft (weighted), and the student can break them (§3.3).
- Bias or protected-attribute checks: none.
- What it means for "several models trained on the rules": `[inference]` This is the closest
  evidence to the issue's question "does a model trained on the rules help anyway?". The answer it
  supports is narrow. **Rules help a student when combined with other labels**, most when labels
  are few. That is evidence for rules plus LLM or human labels, not for a student trained on rule
  labels alone. And the rule-based teacher beat its own student, which argues for keeping the rule
  engine at run time wherever it is cheap enough; this FYP's rules are cheap (see
  [options](options.md)).
- BibTeX: `hu2016harnessing`

### [Plaza-ModelCrowds]: Wisdom of Instruction-Tuned Language Model Crowds. Exploring Model Label Variation
- Authors / Year / Venue / Link: Flor Miriam Plaza-del-Arco, Debora Nozza, Dirk Hovy / 2024 /
  *Proc. 3rd Workshop on Perspectivist Approaches to NLP (NLPerspectives) @ LREC-COLING 2024*,
  pp. 19–30, ELRA and ICCL / https://aclanthology.org/2024.nlperspectives-1.2/ ;
  https://arxiv.org/abs/2307.12973
- Status: published at a peer-reviewed workshop (ACL Anthology record); Read: full text, arXiv v2,
  `refs/td_plaza2024_crowds.txt`.
- Model type, and its teacher: no trained decider; four open instruction-tuned LLMs (T0, Flan-T5,
  Flan-UL2, Tk-Instruct) used as **annotators** on five subjective classification tasks (sentiment,
  age and gender of the author, hate speech) in four languages, then aggregated by majority vote or
  by MACE, a Bayesian model that estimates each annotator's competence (§2, §3, §3.3).
- Fidelity: against human gold labels. "In most cases, the aggregated labels ... outperform even
  the best individual LLM"; on average, aggregated labels are "4.2 F1-points better than the
  average LLM" (§1). MACE was the best method "in 6 out of 14 tasks" (§4). MACE's competence score
  correlates with real performance (Spearman 0.93) (§4).
- Behaviour across tasks: the models **specialise**. No single model is best everywhere, and on one
  task in one language no method beats random choice (§4; Table 3).
- Against human labels: even simple supervised models trained on human labels beat the best
  zero-shot result in all but 4 cases, with an average gap of 10.5 F1 to the best supervised models
  (§4, Table 4); "treating LLMs as annotators cannot rival using human annotators" (§1).
- Cost: zero-shot prompting of open models; no training. Closed models were not tested (Limitations).
- Bias or protected-attribute checks: two of the tasks *predict* the author's age and gender
  (§2.1); no test of whether labels depend on such attributes.
- What it means for "several models trained on the rules": `[inference]` The one direct piece of
  evidence here **for using several LLMs as teachers**: aggregation is more robust than any one
  model, and competence can be estimated without gold labels. Two cautions carry over. (1) It is
  text classification, not behavioural decisions. (2) Aggregation assumes "there is a single correct
  answer" (§4). Where models disagree about a demographic effect (the issue #16 finding that effects
  reverse between models, `README.md`), a vote hides the disagreement; the disagreement itself
  should be kept and reported.
- BibTeX: `plazadelarco2024wisdom`
