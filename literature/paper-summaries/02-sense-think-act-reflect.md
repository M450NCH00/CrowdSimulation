# [Zhang-DFD] — Sense, Think, Act, Reflect: Distilling Fast and Interpretable Decision Functions from LLM-Driven Crowds

Prepared for issue [#14](https://github.com/M450NCH00/CrowdSimulation/issues/14). Group 1
(LLM-side). Template: Group 1.

## Citation

**Authors / Year / Venue / DOI:** Yichi Zhang, Philipp Andelfinger, Wen Jun Tan, Wentong
Cai — **all four at Nanyang Technological University, Singapore** / 2026 / *ACM
Transactions on Modeling and Computer Simulation* ("Just Accepted" version) /
doi:10.1145/3818686 — **confirmed from:** the paper's own title page, which lists the
four authors with NTU affiliations and prints "https://doi.org/10.1145/3818686" and
"ACM 1558-1195/2026/6-ART" in the footer (p. 1). The footer also states the licence:
"This work is licensed under a Creative Commons Attribution 4.0 International License"
(p. 1). Dates printed at the end: "Received 17 April 2026; revised 17 April 2026;
accepted 22 May 2026" (p. 27). Cached at `refs/zhang2026_dfd.pdf`, text extract at
`refs/zhang2026_dfd.txt`.

⚠ **Version note:** this is the **"Just Accepted"** version (watermarked as such). No
volume, issue or article number is assigned yet, so the reference must say "to be
published" until the final version appears.

⚠ **Correction to earlier repo notes:** `literature/llm-conflict-resolution/topic1-llm-conflict.md`
(issue #8) says two of the four authors are at NTU. The title page shows **all four** are.

## Accessibility

**Full text read** — 33 pages including appendices.

*Note on tables:* `pdftotext` misaligns the bolded cells in Tables 3 and 4; the values
quoted below were read from the rendered PDF pages (pp. 17 and 19), not from the raw text
extract.

---

## 1. Research question

To what degree can the rules guiding an LLM-driven agent's decision making be
**automatically distilled into human-readable, commented functions**, so that a
simulation keeps LLM-like behaviour without paying LLM inference cost at run time. The
stated aim: "to combine the capability of LLMs to flexibly react to an environment in a
human-like manner with the speed and reliability of mechanistic agent models" (§1, p. 2).

The motivation is two stated drawbacks of LLM-driven agents: inference cost, which "limits
the scalability beyond relatively modest numbers of individuals", and opacity, which makes
behaviour "difficult to predict, validate, or interpret" (§1, p. 2).

## 2. Setup

**Scenario:** building evacuation on a **33 × 33 cellular grid**, each agent occupying one
cell, with exits at the left, bottom and right spanning one to three cells (§3, p. 6). The
scenario is based on Wang et al.'s evacuation model (§3, p. 6; §6.1, p. 19).

**Agents:** **N = 100 in all experiments** (§5.1, p. 13). Each agent has a position plus
two static attributes — **physical ability** and **mental condition**, each 0 or 1 —
giving four persona groups labelled red, green, yellow and blue (§3, p. 7). Goals are
aligned (everyone wants out) but exits are a contested resource (§3, pp. 6–7).

**Per-step decision:** "a Bernoulli trial with a configurable probability determines
whether an agent makes a new decision on its target exit" (§3, p. 7); movement is then
deterministic toward the chosen exit, falling back to A* if an agent becomes stuck (§3,
p. 7).

**Models (four different LLMs, by role):**
- ground truth generation: **Gemma3:27b**, locally deployed, temperature 0, top_k 64,
  top_p 1, num_predict 512, num_ctx 128,000 (§5.1, p. 13; Appendix A, p. 26);
- general insights: **GPT-4o-mini**; code-based insights: **GPT-4.1-mini** (§5.1, p. 13);
- decision-function refinement: **Llama-3.1-8B-Instruct** (§5.1, p. 13).

**Scale:** each simulation ran **T = 51 timesteps**; visible range V = 10 cells; 20
insights; λ = 10 islands; five random seeds for the in-domain training set, two for the
test set, three for the out-of-domain set; training data comprised **9,955
(perception, exit-choice) pairs**, split 4:1 train/validation (§5.1, p. 13).

**Baselines:** PySR (classical symbolic regression) and LLM-SR (state-of-the-art
LLM-based SR); PySR was given a comparable compute budget but "terminated after two days,
compared to five days with DFD and DFD-C" (§5.1, p. 13). Ablations: LLM-SR-GI, DFD-P,
DFD-M, DFD-CM (Table 2, p. 14).

## 3. Communication protocol

**The agents in this paper do not negotiate with each other; communication enters only
through the borrowed ground-truth simulation.** The authors rely on Wu et al.'s
LLM-driven crowd simulation, whose workflow has four phases, the first being "[a]
communication phase, in which the individuals communicate with each other to help with
their information gathering and decision making" (§4.2, p. 9).

**What was kept and what was replaced:** "we focus on the exit selection and substitute
the LLM-driven immediate movement by a simple heuristic, which substantially reduces the
time required for data generation" (§4.2, p. 9).

**Where the talk goes:** conversations survive only in the *textual* agent-centric
trajectory data used for insight generation — Table 1 (p. 9) lists the textual features as
crowdedness, mental, historical exits, **conversations**, feelings about situation,
feelings about exits, and exit choice. The **numerical perception data**, which is what
the final decision function consumes, contains only x/y coordinates, crowdedness,
capability, mental, distances and exit crowdedness (Table 1, p. 9).

**Turn structure / termination:** `[not stated in paper]` — the paper does not describe
how many turns agents take or how a conversation ends; it cites Wu et al. for the
simulation workflow.

## 4. What the agents did — findings

This paper reports on **distilled functions**, not on agent strategies, so "what the
agents did" is expressed as fidelity of the distilled function to the LLM ground truth.

**Named methods:** DFD (few-shot examples → decision function) and **DFD-C** (an
intermediate step generating "commented code snippets that formalize partial insights"),
plus ablations DFD-P (insights from the task description only), DFD-M and DFD-CM (agent
memory) (§4.3, p. 10; Table 2, p. 14).

**Quantitative results:**
- **Subregion density error (Table 3, p. 17; lower is better)** — PySR 36.46 / 39.07 /
  40.08 (train / test / generalize); LLM-SR 23.48 / 19.61 / 26.21; LLM-SR-GI 19.71 /
  17.79 / 25.13; **DFD 18.67 / 15.62 / 19.01**; DFD-C 15.36 / 15.64 / 21.72; DFD-M
  17.63 / 16.63 / 15.32. Best per column: DFD-C (train), DFD (test), DFD-M (generalize).
- **DTW loss (Table 4, p. 19; lower is better)** — **DFD 4.65 / 2.87 / 1.11**, best in all
  three columns; PySR worst at 171.38 / 184.93 / 118.92; the handcrafted Wang et al. model
  5.35 / 5.15 / 39.38.
- **Crowd density maps (Fig. 8, p. 17)** — the DFD variants and LLM-SR-GI "correctly
  reproduce the tendencies in the ground truth", whereas PySR "heavily overemphasizes
  evacuations through the bottom exit" (§5.3, p. 15).

**Stability / honesty notes reported by the authors:**
- **Agent memory did not help**: "the final generated function did not make use of the
  history" (§5.2, p. 14), a null result they repeat in the Conclusions (§7, p. 21).
- **DFD sometimes copies its own prompt**: "DFD repeatedly recites commented code from its
  original prompt verbatim, failing to convert the current insights into the corresponding
  code" (§5.3, p. 15; visible in Fig. 7, p. 16).
- The final DFD function lost its comments during refinement: "Initially, DFD produced
  commented code, but gradually eliminated the comments over the course of the function
  refinement process" (Appendix B.1, p. 27).

## 5. Pattern extraction (critical for this FYP)

**Yes — this is the paper's entire contribution, and it is the closest existing work to
this FYP's extraction step.**

- **Form:** a **decision function in commented Python-like code** that maps perception
  features to a score for each of the seven exit cells; the final function is simplified
  by discarding unused parameters and re-calibrated (§4.4, p. 11; examples in Fig. 7,
  p. 16 and Fig. 14, p. 29). At run time "each agent invokes the decision function with
  probability p to obtain the exit choice", after which a greedy or A* policy moves it
  (§4.4, pp. 11–12; Fig. 5, p. 12).
- **How derived:** three phases — (a) Ground Truth Generation from the LLM-driven
  simulation, (b) Insight Extraction (natural-language "insights" via the Expel approach,
  optionally formalised into code snippets), (c) Function Refinement, an island-based
  evolutionary loop in which the LLM proposes function skeletons whose coefficients are
  numerically optimised with Powell's method against MSE on the training data (§4.1, p. 8;
  §4.3, p. 10; §4.4, p. 11; Alg. 1, p. 12).
- **Cost/benefit versus running the LLM:** "the subsequent simulations do not rely on an
  LLM and are thus accelerated by several orders of magnitudes" (§5.5, p. 18); measured
  values are **t_sim,LLM ≈ 1 day** versus **t_sim,DF ≈ 1 minute**, with insight generation
  ≈ 1 minute and distillation ≈ 5 days, so the cost amortises after **N_sim > ~10**
  simulation runs (§5.5, p. 19). The distilled function's runtime is "in the same range of
  1 to 2 seconds per time step" as the handcrafted Wang et al. model (§5.5, p. 18).
- **Fidelity loss:** not expressed as a single percentage. It is reported as the gap to
  ground truth in Tables 3 and 4 (pp. 17, 19) — e.g. DFD's DTW of 2.87 on test data versus
  0 for a perfect match `[inference: the zero baseline is mine; the paper does not state
  it]`.

## 6. Validation / ground truth (critical for this FYP)

**Validated against LLM-generated behaviour, not against human behaviour.**

- All three datasets — in-domain training, in-domain test, out-of-domain — are "generated
  by the LLM-driven agent-based simulation from [88]" (§5.1, p. 13), i.e. by Wu et al.'s
  simulation.
- Fidelity metrics compare the distilled function to that LLM ground truth: MSE of
  predicted versus true exit, MAE of agent counts per subregion, and DTW between escape
  time series (§5.1, p. 13).
- **The authors state the consequence themselves:** "As our approach is agnostic of the
  realism of the ground truth trajectories, the validity of the distilled function depends
  directly on the reference data" (§6.1, p. 19).
- They also note the wider problem: "systematic and rigorous validation approaches have
  not been established yet" for LLM-driven agent behaviour (§1, p. 2).
- **How they justify the absence:** by scoping. "Since the focus of our paper is on the
  distillation methodology, we relied on the simulation environment and LLM prompts from
  an existing study" (§6.1, p. 19), and they name maintaining validity of LLM-driven
  behaviours as future work (§6.1, p. 19).
- **Real human data is named only as an alternative they did not take:** distilling
  "directly from trajectories extracted from real-world observations, e.g., from video
  footage" is described as "[a]n interesting alternative" (§6.2, pp. 19–20).
- A handcrafted model (Wang et al.) appears in Tables 3–4 and Fig. 8j as a **reference
  point**, not as ground truth; the authors note its deviation "is expected" because it
  "was not crafted based on our LLM-based ground truth" (§5.3, p. 15).

## 7. Limitations stated by the authors

- **Validity is inherited from the reference data** (§6.1, p. 19), as quoted above.
- **Applicability rests on two assumptions**: that agents follow a sense–think–act cycle,
  and that the LLM's pre-training covers the domain; for specialised domains such as
  biology or chemistry "the 'commonsense knowledge' of current LLMs may not suffice"
  (§6.3, p. 20).
- **Scenario transfer needs prompt work**: applying DFD to a new scenario requires
  adjusting the insight-generation prompt, the handcrafted few-shot code pairs, and the
  evaluation and seed functions (§6.3, p. 20).
- **Memory did not help** in their experiments, and they suggest it may matter only where
  path dependencies dominate (§7, p. 21).
- **Agent interaction is not encoded as a feature**: "Encoding context information on agent
  interactions as features could further increase the fidelity" — stated as future work
  (§7, p. 21).
- **Isolated decision functions are a limit**: extending to "more complex and dynamic
  scenarios that require nuanced and multi-step decision-making" would need integration
  into richer mechanistic models (§7, p. 21).

## 8. Relevance to this FYP

- **This is the project's closest prior work and its natural baseline.** The pipeline
  "run LLM agents → extract the strategy → emit interpretable code → drop the LLM at run
  time" is this FYP's roadmap steps 3–4, already published, on crowd evacuation, by an NTU
  group (§1, p. 2; §4, pp. 8–12).
- **The output form matches what CrowdGym needs**: a cheap function called per agent per
  decision, with movement handled by a conventional policy (§4.4, pp. 11–12; Fig. 5,
  p. 12) — the same shape as the trigger-and-lookup handler in
  `integration/crowdgym_mapping.md` §B. [inference]
- **Two gaps this FYP can still claim**, both grounded in the paper's own text rather than
  in my reading of what is missing: the distilled function is not validated against human
  behaviour (§6.1, p. 19), and **agent interactions are explicitly future work** (§7,
  p. 21) — so distilling a rule *from the dialogue between agents in conflict* is not what
  DFD does. [inference: that this constitutes the FYP's remaining contribution is my
  judgement, not the paper's claim.]
- **It supplies the amortisation argument in measured numbers** (§5.5, p. 19): distillation
  pays for itself after roughly ten simulation runs.

## BibTeX

`zhang2026sense` — see [`refs.bib`](refs.bib).
