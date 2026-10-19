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
- **Which introduction component(s) it supports:** 1 (its cost figure below supported 2
  in the first draft, and was cut in revision 2; see the note)
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
- *Revision 2 note:* once Zhang et al. [2] was read in full, its measured run times (one
  LLM-driven run ≈ 1 day vs ≈ 1 minute distilled) made the cost point more directly than
  Wu's dollar figure, so the Wu cost sentence was cut to stay under 500 words. Wu is
  still cited for evacuation congestion, LLM agents in simulation, and exit balancing.

### [2] [Zhang-DFD] — Sense, Think, Act, Reflect: Distilling Fast and Interpretable Decision Functions from LLM-Driven Crowds

- **Authors / Year / Venue:** Y. Zhang, P. Andelfinger, W. J. Tan, W. Cai (all Nanyang
  Technological University) / 2026 / *ACM Transactions on Modeling and Computer
  Simulation* (TOMACS), "Just Accepted" (received 17 Apr 2026, accepted 22 May 2026),
  doi:10.1145/3818686. CC-BY 4.0.
- **Which introduction component(s) it supports:** 1, 2
- **What specifically it contributes:** §1 says evacuation crowd simulation is
  "essential for emergency planning and building design" and that LLMs increasingly act
  as agents in simulation. It proposes Decision Function Distillation (DFD), which turns
  LLM agents' exit-choice decisions into interpretable, commented rule code (§1, §3–4).
  One LLM-driven run of the 100-agent evacuation took about a day, against about a
  minute with the distilled function (§5.1, §5.5). The functions are judged by how
  closely they reproduce the LLM-generated ground truth, and the authors state that
  "the validity of the distilled function depends directly on the reference data"
  (§5.1, §6.1). Real-world observations are named only as an alternative source (§6.2).
  It is the closest existing work to this project's "extract a reusable rule" step, so
  the research gap has to be stated against it.
- **What it does NOT cover that the introduction still needs:** It does not validate
  against human data, and it does not target pairwise conflict resolution. Its ground
  truth includes agents' conversations (§4.2), but the final functions use only
  numerical perception features, and encoding agent interactions is left to future
  work (§7).
- *Checked against:* **full text** of the Just Accepted PDF, provided by the user on
  2026-09-13 and cached as `refs/zhang2026_dfd.pdf` (text: `refs/zhang2026_dfd.txt`).
  The first draft of this entry was abstract-only; see `WORK_LOG-10.md`.

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
| Wang 2015 — Congestion evacuation with panic *(supervisor-assigned)* | 1: why crowd simulation matters (stadium evacuation, casualties under panic, abstract) | A sixth reference would exceed the cap. First chosen as the likely swap-in for "why it matters"; no longer needed, because Zhang [2] §1 now covers that point from full text. Abstract-level only. |
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

*Revised 2026-09-13 after reading the Zhang et al. [2] full text. The first version was
"partially covered / covered with one condition"; see `WORK_LOG-10.md`.*

- **Background: covered, with one limitation.** Why crowd simulation matters: [2] §1
  (emergency planning and building design). What crowd simulation is, with evacuation
  congestion as the example: [1] §6.1 and [2] §1. LLMs as agents in simulation: [1] §1
  and [2] §1. Conflicts causing deadlock: [3], but in **multi-robot navigation**, not
  crowd simulation; no selected paper shows a crowd simulation stalling. The draft talks
  about "agents" and "doorway tests" for this reason (`open-gaps.md` N1).
- **Research gap: covered.** [3] shows each conflict needs a fresh LLM dialogue and is
  scored against a designer-fixed ranking. [2] shows that distillation already exists
  (so the gap is **not** "nobody extracts rules"), quantifies the speed-up, and, per its
  own §6.1, is judged only against LLM-generated behaviour. [4] explains why human
  validation matters. The gap is stated as "no reviewed study extracts a rule from
  LLM-to-LLM conflict dialogue and validates it against humans". It is limited to the
  reviewed literature, not the result of a systematic search (`open-gaps.md` G5).
- **Study introduction: covered.** [3] shows a two-agent dialogue can break a doorway
  deadlock. [4] shows conventions emerge from LLM interaction. [5] shows human
  conflict-resolution patterns exist and are classifiable. The weak point is that [5]
  is not spatial; the draft calls the hallway link an analogy.
- **Overall: sufficient for a 3–5 citation introduction.** The earlier blocking
  condition (Zhang full text) is resolved and the claim held. Remaining items in
  `open-gaps.md` are non-blocking.
