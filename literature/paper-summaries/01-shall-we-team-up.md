# [Wu-SWTU] — Shall We Team Up: Exploring Spontaneous Cooperation of Competing LLM Agents

Prepared for issue [#14](https://github.com/M450NCH00/CrowdSimulation/issues/14). Group 1
(LLM-side). Template: Group 1.

## Citation

**Authors / Year / Venue / DOI:** Zengqing Wu, Run Peng, Shuyuan Zheng, Qianying Liu,
Xu Han, Brian Inhyuk Kwon, Makoto Onizuka, Shaojie Tang, Chuan Xiao / 2024 / *Findings of
the Association for Computational Linguistics: EMNLP 2024*, pp. 5163–5186 /
doi:10.18653/v1/2024.findings-emnlp.297 — **confirmed from:** the paper's own first page
(title, author list and affiliations, p. 5163) and its running footer, which prints the
venue line "Findings of the Association for Computational Linguistics: EMNLP 2024, pages
5163–5186" (p. 5163). Cached at `refs/wu2024_shall_we_team_up.pdf`, text extract at
`refs/wu2024_shall_we_team_up.txt`.

*Page locators below are the printed journal pages (5163–5186); the PDF's page 1 is
printed page 5163.*

## Accessibility

**Full text read** — 24 pages including appendices, downloaded as PDF and text-extracted
locally.

---

## 1. Research question

Whether cooperation can develop **spontaneously** among LLM agents in competitive
settings — that is, without prompts telling them to cooperate. The authors state they
"doubt the necessity of shaping agents' behaviors for accurate social simulations" and
instead emphasise "spontaneous phenomena, wherein agents deeply engage in contexts and
make adaptive decisions without explicit directions" (Abstract, p. 5163). The framing
question in §1 is whether cooperation "can naturally develop among agents, even in a
competitive environment" (§1, p. 5163).

## 2. Setup

**Three case studies** (§4–§6):

| Case study | Scenario | Agents | Goals |
|---|---|---|---|
| 1. Keynesian Beauty Contest (KBC) | agents simultaneously choose a number; the player closest to 2/3 of the average wins (§4, p. 5166; task description, Appendix, p. 5186) | multiple players | competing (one winner) |
| 2. Bertrand Competition (BC) | two firms set prices each round; demand and profit computed following Calvano et al. (2020) (§5, p. 5168) | 2 firms | competing |
| 3. Emergency Evacuation (EE) | 33×33 cell grid room with three exits (left, right, bottom); evacuees choose a target exit and move (§6.1, p. 5170) | **100 agents** | aligned in wanting to escape, competing for exits — the authors note all agents want to escape quickly, "often leading to congestion" (§6.1, p. 5170) |

**Models and parameters:** GPT-4 throughout — specifically `gpt-4-0314` via the OpenAI
`ChatCompletion.create` function, `openai==0.28.0` (§4, p. 5166); temperature 0.7 in the
KBC baseline "without explicit instructions or personas" (Fig. 3 caption / §4.2,
p. 5167).

**Scale:** KBC — "we simulated 15 runs for each setting with GPT-4 as backbone" (§4,
p. 5166). BC — runs terminate at 1200 rounds or after continuous collusion (§5.1,
p. 5168). EE — 100 agents, stop when all escape or at 50 rounds, "5 runs with different
initial locations of agents" (§6.1, p. 5170).

**Framework:** SABM (Wu et al., 2023b), chosen "for its lightweight, user-friendly
implementation" (§2, p. 5164).

## 3. Communication protocol

**What agents could say:** free-form natural language. In EE, agents are asked "to share
their feelings with others", and "[o]nly Agents within a specific distance can hear the
messages" (§6.1, p. 5170). The authors deliberately avoided instructive wording,
designing prompts "to avoid instructive descriptions (e.g. 'you may cooperate')" and
keywords revealing the nature of the simulation (e.g. "price war") (§2, p. 5164).

**Turn structure:** each round runs four phases — Communication, Planning, Action, Update
(§6.1, p. 5170). In BC the order of communication and planning is swapped "to align with
previous" work (§3, p. 5165). In KBC agents "communicate sequentially" within a
communication period that "can vary in length from one round to multiple rounds" (§3,
p. 5165).

**Termination / frequency:** in EE, "[f]or each round, one agent has 20% probability to
communicate and adjust its plan (phase 1 and 2)", otherwise it acts on its existing plan;
the authors say this "well prevents agents to talk every round … which results in a more
realistic simulation" (§6.1, p. 5170). Simulation ends when all agents escape or at 50
rounds (§6.1, p. 5170).

**Information available:** in EE each agent is given "the distance to three exits and the
congestion levels around those exits", plus its own chat history (§6.1, p. 5170). Agents
therefore hold private position/plan state and share information by speaking.

## 4. What the agents did — findings

**Named findings:**
- **Spontaneous cooperation** — the paper's own term for cooperative behaviour emerging
  without instruction (Abstract, p. 5163).
- In BC: **tacit collusion** (informal coordination without explicit agreement) and
  **cartel collusion** (formal agreement to fix prices), defined at §5.1, p. 5168. Prices
  falling between the Bertrand equilibrium and the cartel price are counted as
  spontaneous cooperation (§5.1, p. 5168).
- In EE: cooperation is operationalised as "information sharing, encouragement, and exit
  guidance" (§6.1, p. 5170).

**Frequency / distribution data:**
- **EE, Table 2 (p. 5171)** — cumulative agents escaped (of 100) by round:
  at round 15, Without Communication 51.2 vs With Communication 48.8; at round 50, With
  Communication 100.0, Without Communication 99.8, With Comm. + Uncooperative persona
  99.0. The authors' defensible claim from this table is the narrower one they state:
  communication "is the only baseline group to successfully escape within 50 rounds in
  all five runs" (§6.2, p. 5171).
- **EE, Fig. 9 (p. 5170)** — the distribution of escapes across the three exits becomes
  "more balanced when evacuees are able to communicate", which the authors attribute to
  agents sharing both proximity and congestion information (§6.2, p. 5171).
- KBC/BC distributions appear in Figs. 3–5 (pp. 5167–5168); exact per-round values are
  `[not stated in paper]` in numeric form.

**Stability across runs:** the EE result rests on **5 runs** and Table 2 reports means
without dispersion — no variance, confidence interval or significance test is reported
for Table 2 `[not stated in paper]`. For KBC the authors report convergence being
*gradual* rather than immediate, and contrast it with a control condition where
instructing cooperation produces immediate convergence (§7, p. 5171).

## 5. Pattern extraction (critical for this FYP)

**No.** The paper does **not** extract any reusable rule, policy, decision function or
heuristic that could be applied without re-running the LLM. Every result comes from
running GPT-4 agents in the loop; the contribution is the observation of spontaneous
cooperation, not its distillation. The closest the authors come is a plan for future
work: "we plan to convert our case studies into standardized benchmarks or datasets to
facilitate further research" (Limitations, p. 5172) — benchmarks, not extracted policies.

## 6. Validation / ground truth (critical for this FYP)

**Mixed — and this differs by case study, which matters.**

- **KBC: validated against real human data.** "[O]ur simulation result from the baseline
  generally aligns with the large-scale empirical experiment conducted by The New York
  Times (N = 61,140) in terms of numerical choice distribution (Leonhardt and Quealy,
  2015)" — both LLM and NYT players predominantly chose 33, with sub-peaks near 0, 22, 50
  and 66 "well mirrored" (§4.2 "Comparison With Human Data", p. 5168, Fig. 5).
- **BC: validated against prior findings, not new human data.** The authors state their
  agents' behaviour "aligns with these findings" from earlier economics work (§5.2,
  p. 5169) and that results "align with those from simulations" (§5.2, p. 5169).
- **EE: not validated against human behaviour.** No comparison to human evacuation data
  is reported. The authors concede the metrics themselves are inadequate: "It would be
  beneficial to have more metrics for evaluating spontaneous cooperation in EE, and leave
  this for future study" (§7, p. 5171).

The summary claim in the Conclusion is broader than the EE evidence: the phenomenon
"aligns well with real-world data" (§8, p. 5171) — which is supported for KBC, and
**not** demonstrated for EE.

## 7. Limitations stated by the authors

- **Single model.** Experiments used one version of GPT-4; the authors call the work "a
  proof-of-concept study, which needs to be further tested across different LLMs to prove
  its generalizability" (Limitations, p. 5172).
- **Cost drove that choice.** The three case studies cost "{$900, $3000, $1000}"
  respectively, alongside rate limits and context-window limits (Limitations, p. 5172).
- **Benchmarking contribution overstated.** They "did not focus sufficiently on collecting
  comprehensive datasets or creating robust benchmarks to substantiate this claim fully"
  (Limitations, p. 5172).
- **Claim about simulating humans is qualified.** They state their claim "is not that
  simulating human behavior using these LLM agents is entirely justified", only that
  uninstructed agents are more humanlike than instructed ones (Limitations, p. 5172).
- **EE metrics insufficient** (§7, p. 5171), as above.

## 8. Relevance to this FYP

- **It is the closest published precedent for "LLM agents talk during a spatial conflict
  and the talk changes the outcome"**, and it supplies the mechanism: the useful content
  of messages is *(which exit, how congested)*, and agents resolve congestion by
  redistributing across alternatives (§6.2, p. 5171).
- **It does not do what this FYP proposes.** No pattern is extracted (see §5 above), so
  the FYP's extraction step is not pre-empted by this paper.
- **It sets the cost argument concretely**: $1,000 for a 100-agent, 50-round evacuation
  study (Limitations, p. 5172) is direct evidence that per-conflict LLM calls do not
  scale to 10,000 agents. [inference] — the scaling conclusion is mine; the paper reports
  the cost, not the implication.
- **Its exit-redistribution mechanism does not transfer to a 2-agent hallway**, where
  there is no third alternative to redistribute to. [inference]
- **The 20% communication probability** (§6.1, p. 5170) is a citable precedent for not
  running the LLM every step — a cheaper design than per-step inference. [inference]

## BibTeX

`wu2024shall` — see [`refs.bib`](refs.bib).
