# Paper selection for the FYP introduction (Assignment 1)

Prepared for issue [#10](https://github.com/M450NCH00/CrowdSimulation/issues/10).
Companion files: [`introduction-draft.md`](introduction-draft.md), [`open-gaps.md`](open-gaps.md).

**Source pool:** only the 14 papers in the issue #8 literature review —
[`../topic1-llm-conflict.md`](../topic1-llm-conflict.md) and
[`../topic2-sociological-grounding.md`](../topic2-sociological-grounding.md). No new
papers were searched for. Where the review cached a full text in [`../../../refs/`](../../../refs/),
the findings below were re-checked against that text rather than against the review's
summary. Each entry states which level it was checked at.

The IEEE numbers `[n]` match the reference list in `introduction-draft.md` and follow the
order of first citation in that draft.

---

## Selected papers

### [1] [Wu-SWTU] — Shall We Team Up: Exploring Spontaneous Cooperation of Competing LLM Agents

- **Authors / Year / Venue:** Z. Wu, R. Peng, S. Zheng, Q. Liu, X. Han, B. I. Kwon,
  M. Onizuka, S. Tang, C. Xiao / 2024 / *Findings of the Association for Computational
  Linguistics: EMNLP 2024*, pp. 5163–5186. Supervisor-assigned.
- **Which introduction component(s) it supports:** 1, 2
- **What specifically it contributes:** It says LLM agents are a growing research topic
  in social simulation because they are more flexible than rule-based agent models
  (§1). In its 100-agent GPT-4 evacuation study, agents that could talk to each other
  spread more evenly across the three exits than agents that could not (§6.1–6.2,
  Fig. 9). The Limitations section says the authors used only one GPT-4 model partly
  because of cost: $900, $3,000 and $1,000 for the three case studies, with $1,000 for
  the evacuation study.
- **What it does NOT cover that the introduction still needs:** It extracts no reusable
  pattern from the agents' messages. Its evacuation conflict is about spreading people
  across exits, not about two agents blocking each other.
- *Checked against:* full text (`refs/wu2024_shall_we_team_up.txt`). The evacuation
  speed result in Table 2 is **not** used, because the margins are too thin (the review
  explains why).

### [2] [Zhang-DFD] — Sense, Think, Act, Reflect: Distilling Fast and Interpretable Decision Functions from LLM-Driven Crowds

- **Authors / Year / Venue:** Y. Zhang, P. Andelfinger, W. J. Tan, W. Cai / 2026 /
  *ACM Transactions on Modeling and Computer Simulation* (TOMACS), doi:10.1145/3818686.
- **Which introduction component(s) it supports:** 1, 2
- **What specifically it contributes:** The abstract says LLMs can produce human-like
  agent behaviour and are useful building blocks for agent-based simulations, but their
  inference cost limits how large a crowd can be simulated. It proposes Decision
  Function Distillation (DFD), which turns LLM agents' decision strategies into
  interpretable, commented rule code. DFD is tested on agent-based crowd evacuation and
  beats classical and LLM-based symbolic regression. It is the closest existing work to
  this project's "extract a reusable rule" step, so the research gap has to be stated
  against it.
- **What it does NOT cover that the introduction still needs:** The abstract does not
  say whether the distilled rules are checked against real human behaviour, or whether
  they come from agents talking to each other about a conflict
  `[needs verification against full text]`.
- *Checked against:* **abstract only** (Semantic Scholar record,
  `refs/s2_zhang2026_dfd.json`). ACM DL blocked automated access during issue #8. No
  numbers from this paper are used.

### [3] [Mahadevan-GameChat] — GameChat: Multi-LLM Dialogue for Safe, Agile, and Socially Optimal Multi-Agent Navigation in Constrained Environments

- **Authors / Year / Venue:** V. Mahadevan, S. Zhang, R. Chandra / 2025 / *2025 IEEE
  International Symposium on Multi-Robot and Multi-Agent Systems (MRS)*; arXiv:2503.12333.
- **Which introduction component(s) it supports:** 1, 2, 3
- **What specifically it contributes:** It explains how symmetry causes deadlock: two
  agents equally far from a shared doorway collide if both go and deadlock if both
  wait (§I, Fig. 1). Its baseline controller, MPC-CBF, deadlocked in all 18 doorway
  scenarios. When the two agents instead talked through natural-language dialogue,
  there were no deadlocks, and the more urgent agent went first in 100% of cases
  instead of 50% (Table III, abstract). Two further facts support the gap argument:
  each dialogue took 2.767 s on average (§V-B.2), and a "correct" outcome means matching
  an urgency ranking the authors fixed in advance (hospital > airport > grocery, §IV-C).
  The LLMs are not given that ranking; they infer urgency from the task descriptions
  (§IV-C, Table II).
- **What it does NOT cover that the introduction still needs:** It is about robot
  navigation, not crowd simulation. It extracts no reusable pattern and does not
  validate against human behaviour; real-world validation is listed as future work
  (§VI).
- *Checked against:* full text of **arXiv v2 (9 May 2026)**
  (`refs/mahadevan2025_gamechat.txt`). Section and table numbers are from that version
  and may differ in the IEEE MRS proceedings.
- *Correction to the issue #8 review:* `topic1-llm-conflict.md` says GameChat was
  evaluated with only two agents and only "sketches a k>2 extension". The cached v2
  full text includes 3-, 4- and 5-agent doorway results (§IV-E, §V-B.4, Table IV).
  The introduction does not rely on either version of this point. The review also says
  "the priority ordering is supplied by the designer — the LLM *applies* a hierarchy
  rather than discovering one". That is slightly overstated: the prompt does not contain
  the ordering (§IV-C). The designers define the ground truth, and the LLM infers
  urgency from free-text tasks. The draft is worded to match the paper, not the review.

### [4] [Ashery-Conventions] — Emergent social conventions and collective bias in LLM populations

- **Authors / Year / Venue:** A. F. Ashery, L. M. Aiello, A. Baronchelli / 2025 /
  *Science Advances* 11(20), eadu9368.
- **Which introduction component(s) it supports:** 2, 3
- **What specifically it contributes:** The abstract reports that populations of LLM
  agents spontaneously settle on shared conventions without being programmed to. This
  is peer-reviewed evidence that a stable, reusable pattern can emerge when LLM agents
  interact (component 3). The abstract also reports that strong collective biases can
  appear even when no single agent is biased. That is the argument for why a pattern
  extracted from LLMs must be checked against humans (component 2).
- **What it does NOT cover that the introduction still needs:** The task is an abstract
  naming game, with no physical space, no conflict over who passes, and no conversion
  of the convention into a simulation rule.
- *Checked against:* **abstract only** (City Research Online open-access record,
  `refs/ashery2025_social_conventions_oa.html`). Population sizes and models are not
  used.

### [5] [Moeller-Transparent] — Human and macaque pairs employ different coordination strategies in a transparent decision game

- **Authors / Year / Venue:** S. Moeller, A. M. Unakafov, J. Fischer, A. Gail, S. Treue,
  I. Kagan / 2023 / *eLife* 12, e81641.
- **Which introduction component(s) it supports:** 3
- **What specifically it contributes:** In a face-to-face touchscreen version of
  Bach-or-Stravinsky, a game in which each partner prefers a different option but both
  gain by choosing the same one, 19 human pairs (38 participants) resolved the conflict
  in a small number of classifiable ways: 10 pairs took turns, 5 settled on a fixed
  choice favouring one partner, and 4 failed to coordinate (Results, "Human pairs
  mainly converge on fair coordination", Fig. 2A; participants in Materials and
  methods). This shows that human conflict-resolution patterns exist and can be
  classified, which gives a benchmark to validate against.
- **What it does NOT cover that the introduction still needs:** The game is played on a
  screen, not in physical space, so treating it as a model of a hallway standoff is
  this project's own analogy, not something the paper claims. It says nothing about
  LLMs.
- *Checked against:* full article page (`refs/moeller2023_transparent_game.html`). The
  counts 10/5/4 of 19 are quoted from the text; the review's percentages (53/26/21%)
  are rounded from them.

---

## Candidates considered but not selected

The issue caps the introduction at 3–5 references. These were close calls, and the
reasons are recorded so the choice can be revisited.

| Paper | Would have supported | Why not selected |
|---|---|---|
| Wang 2015 — Congestion evacuation with panic *(supervisor-assigned)* | 1: why crowd simulation matters (stadium evacuation, casualties under panic, abstract) | Best fit for "why it matters", but a sixth reference would exceed the cap. It was dropped instead of Wu [1], which also covers LLM agents in simulation and gives the cost figure. Abstract-level only. **Most likely swap-in** — see `open-gaps.md`. |
| Chen 2024 — MAPF with LLMs | 2: LLMs fail at full spatial planning | Preprint `[non-archival]`; supports scope design rather than the gap the issue defines. |
| Bianchi 2024 — NegotiationArena | 2: LLM negotiation outcomes move with rhetoric | Non-spatial. It is a threat to validity, better placed in a methods section than an introduction. |
| Abdelnabi 2024 — LLM-Stakeholders Negotiation | 2: even frontier models underperform at negotiation | Overlaps with Ashery [4]'s caution and is non-spatial. |
| Piatti 2024 — GovSim | 3: communication is critical to LLM cooperation | Temporal, many-party commons problem; weaker link to a two-agent standoff than GameChat [3]. |
| Yamamoto 2019 — Body rotation in passing | 3: two-person narrow-corridor geometry | Describes how bodies physically pass, not who yields; the full text was not read. |
| Boomers 2023 / Jülich archive | 3: human validation data exists | A data paper with no behavioural finding to cite in an introduction. Better in methodology. |
| Echeverría-Huarte 2026 — Locomotor bias | 3: individual directional bias | Free walking with no conflict to resolve. |
| Terwilliger 2026 — Invisible walls | 1/3: spatial norms | Preprint `[non-archival]`. |

---

## Coverage assessment

- **Background: partially covered.** LLMs as agents in social and agent-based
  simulation is covered by [1] §1 and [2]. Crowd simulation, with evacuation congestion
  as the example, is covered by [1] §6 and [2]. Conflicts causing deadlock is covered by
  [3], but in **multi-robot navigation**, not crowd simulation; no selected paper shows a
  crowd simulation stalling. *Why* crowd simulation matters is only implied through
  evacuation. The draft is worded to stay within what these sources say. Both gaps are
  listed in `open-gaps.md`.
- **Research gap: covered, with one condition.** [3] shows each conflict needs a fresh
  LLM dialogue and uses a designer-set priority ranking. [1] shows the cost. [2] shows
  that a distillation approach already exists, so the gap is **not** "nobody extracts
  rules"; it is "no reviewed work extracts rules from LLM-to-LLM conflict dialogue and
  checks them against humans". [4] explains why that check matters. **Condition:** the
  claim that [2] does not validate against humans comes from its abstract only and is
  marked `[needs verification against full text]`. If the full text shows human
  validation, the gap paragraph must be rewritten. The gap is also limited to the
  reviewed literature; it is not the result of a systematic search.
- **Study introduction: covered.** [3] shows a two-agent dialogue can break a doorway
  deadlock. [4] shows conventions emerge from LLM interaction. [5] shows human
  conflict-resolution patterns exist and are classifiable. The weak point is that [5]
  is not spatial; the draft calls the hallway link an analogy.
- **Overall: sufficient for a 3–5 citation introduction**, provided the Zhang et al. [2]
  full text is checked before submission. Part 2 was therefore attempted. Nothing in the
  draft is unsourced, but two background points are deliberately narrower than the
  issue's ideal wording because the selected papers do not support more (see
  `open-gaps.md`).
