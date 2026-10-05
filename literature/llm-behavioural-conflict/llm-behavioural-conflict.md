# LLMs resolving spatial conflict *without conversation*

> **Draft pending supervisor review.** Search and reading done on 2026-10-05, on branch
> `docs/22-simulation-conflict-rules-literature`. Not tied to a GitHub issue. This file fills
> the hole named in [`../simulation-rules/research-gap.md`](../simulation-rules/research-gap.md)
> §6: *"No source read uses a language model."*

Companion files: [search log](search-log.md) · [refs](refs-llm-behavioural.bib)

## The question

Is there published work where an LLM resolves (or avoids) a **spatial conflict between agents**
in a crowd simulation or a game, where the resolution does **not** come from the agents talking
to each other, but from the LLM's knowledge of **how people behave**?

Each candidate was tested against three criteria:

| | Test | Fails if |
|---|---|---|
| **T1** | The LLM's output decides a spatial conflict between moving agents (who yields, which side, who goes first), or avoids one | the LLM only picks goals, routes or moods, and a classical rule handles the encounter |
| **T2** | No conversation between the conflicting agents | the agents exchange natural-language messages to settle it (as in [Mahadevan-GameChat], already in [`../llm-conflict-resolution/`](../llm-conflict-resolution/topic1-llm-conflict.md)) |
| **T3** | What decides is the LLM's knowledge of human behaviour or social convention | the LLM is used as a generic spatial planner, or the rule is written into the prompt by the authors |

`[inference]` marks my reading. Unmarked statements are the cited source's. Locators point into
the cached text extracts named on each entry (`refs/lb_*.txt`). **Every entry was read
selectively** — the sections read are listed per entry — so "not stated" means "not stated in
the sections read".

## Bottom line

**I found no paper that passes all three tests inside a crowd simulation.** In the six
LLM-driven crowd simulators I opened, the LLM sits *above* the conflict: it chooses goals,
routes, evacuate-or-stay decisions or steering parameters, and where the paper says how an
encounter between two agents is handled, it is a classical rule — a social force model,
BioCrowds, force-based steering, or a random draw (see [§4](#4-crowd-simulation-near-misses--why-each-was-excluded)).

The papers that do pass all three tests are in two neighbouring domains:

- **one robot among real pedestrians** ([Song-VLMSocialNav], [Fang-Etiquette], and for several
  robots [Wang-SAMALM]) — the model is asked what a person would do under walking etiquette, and
  that answer decides yield / side / stop;
- **one vehicle against pedestrians** ([Baimbetova-PedAwareAV], and the audit
  [Yoldas-YieldBias]).

A second group passes T1 and T2 but **not T3**: the LLM resolves deadlocks between agents
without any dialogue, but as a planner, with no appeal to human behaviour ([Seo-LLMDR],
[Garg-FMDeadlock], [Zhao-MotionAgents]).

`[inference]` So the specific combination this FYP proposes — agent-versus-agent conflict
among simulated pedestrians, settled by behaviour knowledge elicited from an LLM, with no
dialogue at run time — was **not found** in this search. That is a statement about 13 web
searches on one day, not about the field; [search-log.md](search-log.md) §5 says what could
overturn it. The closest crowd-simulation candidates already in this repo, [Zhang-DFD] and
CrowdVLA, have still not been read in full and are the most likely counter-examples.

## Summary table

| # | Handle | Year | Venue | Domain | T1 | T2 | T3 |
|---|---|---|---|---|---|---|---|
| A1 | [Song-VLMSocialNav] | 2025 | IEEE RA-L | robot among pedestrians (hardware) | ✓ | ✓ | ✓ (partly prompted) |
| A2 | [Fang-Etiquette] | 2026 | IEEE RA-L | robot among pedestrians (hardware) | ✓ weak | ✓ | ✓ |
| A3 | [Wang-SAMALM] | 2025 | arXiv `[preprint]` | several robots among simulated pedestrians | ✓ | ✓ (central critic) | ✓ weak |
| A4 | [Baimbetova-PedAwareAV] | 2026 | arXiv; accepted IEEE ITSC | vehicle vs pedestrians (SUMO) | ✓ | ✓ | ✓ |
| A5 | [Yoldas-YieldBias] | 2026 | arXiv `[preprint]` | vehicle vs pedestrian (text / image audit) | ✓ | ✓ | ✓ — and audits it |
| B1 | [Seo-LLMDR] | 2025 | arXiv `[preprint]` | grid path finding, 4–64 agents | ✓ | ✓ | ✗ |
| B2 | [Garg-FMDeadlock] | 2024 | arXiv `[preprint]` | connected multi-robot system, 5–50 | ✓ | ✓ | ✗ |
| B3 | [Zhao-MotionAgents] | 2025 | arXiv `[preprint]` | floor-plan navigation, 2–5 agents | ✓ | ✓ | ✗ |
| C1 | [Zhang-ProAgent] | 2024 | AAAI | Overcooked-AI (game) | weak | ✓ | ✗ (infers partner, not people in general) |
| C2 | [Cross-HypotheticalMinds] | 2025 | ICLR | Melting Pot (game) | weak | ✓ | ✗ |
| C3 | [Agashe-LLMCoordination] | 2025 | Findings of NAACL | Overcooked-AI, Hanabi (games) | weak | ✓ | ✗ |

Peer-reviewed: A1, A2, C1, C2, C3 (A4 accepted, proceedings record not yet found). Preprints:
A3, A5, B1, B2, B3.

---

## 1. Tier A — passes all three tests, in a neighbouring domain

### [Song-VLMSocialNav]: VLM-Social-Nav: Socially Aware Robot Navigation Through Scoring Using Vision-Language Models

- Authors / Year / Venue: Daeun Song, Jing Liang, Amirreza Payandeh, Amir Hossain Raj, Xuesu
  Xiao, Dinesh Manocha / 2025 / *IEEE Robotics and Automation Letters* 10(1), 508–515.
- Link: https://doi.org/10.1109/LRA.2024.3511409 | https://arxiv.org/abs/2404.00210
- Peer-review status: published (Crossref record confirmed by title search).
- Verified: Abstract, §III (approach and scoring module), §IV-A to §IV-C and the discussion read; related work
  skipped. **Read from** `refs/lb_vlmsocialnav_2404_00210.txt` (arXiv v3). ⚠ Table I lost its
  row alignment in extraction; no cell is quoted.
- What the model decides: on detecting a person, door or gesture, GPT-4V is shown the robot's
  camera image and asked *"How will you navigate concerning the person in your view? You will
  need to follow general walking etiquette"*; it answers in the fixed form *"Move DIRECTION
  with SPEED"* — direction ∈ {left, straight, right}, speed ∈ {slow down, speed up, constant,
  stop} (Fig. 3). That answer becomes a social cost term added to a standard local planner
  (DWA) (Eqs. 1–4, Algorithm 1).
- How the conflict is resolved: the planner minimises the deviation between the robot's action
  and "a navigation behavior humans would adopt in accordance with social conventions"
  (§III, Eq. 2). No message passes between robot and person.
- Source of the behaviour knowledge: the VLM's "pre-trained large internet-scale dataset"
  (§III-C) — **plus rules written into the prompt**: *"Move to the right when passing by a
  person. Do not obstruct others' paths."* (Fig. 3). The authors note the convention is local
  and swap the line for a left-walking country (§III-C). `[inference]` So T3 is only partly
  met: the side-of-passing rule is supplied, not elicited.
- Scenarios: frontal approach, frontal approach with gesture, intersection, **narrow doorway**
  — "The robot is expected to wait outside the door and yield to the human" (§IV-B).
- Evaluation: a Turtlebot 2 with real participants; 21 runs per method and scenario; baselines
  DWA and behaviour cloning trained on the SCAND dataset; a user-study questionnaire (§IV,
  Tables I–II).
- Does it work: Abstract — at least 27.38% improvement in average success rate and 19.05% in
  average collision rate over the four scenarios, and the best user-study score. Qualitatively,
  DWA passes a person on either side while this method "predominantly bypasses the person on
  the right side", and at an intersection passes behind the person where DWA cuts in front
  (§IV-B).
- Validated against human behaviour: by a user study of perceived social compliance, not
  against recorded trajectories.
- Limitations stated: response time of 2–3 seconds per query, so the VLM is queried only when a
  social cue is detected; "problematic in more dynamic scenarios that require frequent
  interactions" (discussion).
- Relevance to this FYP: `[inference]` **the closest published precedent for the mechanism.**
  The four scenarios are the FYP's (head-on, crossing, doorway), the conflict is settled with
  no dialogue, and the model's output is exactly the kind of small discrete answer —
  side, speed, yield — that the dataset records. Two differences matter: only *one* party (the
  robot) follows the model, and the 2–3 s latency is the cost wall that distillation into a
  rule is meant to remove.
- BibTeX: `song2025vlmsocialnav`

### [Fang-Etiquette]: From Obstacles to Etiquette: Robot Social Navigation With VLM-Informed Path Selection

- Authors / Year / Venue: Zilin Fang, Anxing Xiao, David Hsu, Gim Hee Lee / 2026 / *IEEE
  Robotics and Automation Letters* 11, 3947–3954.
- Link: https://doi.org/10.1109/LRA.2026.3662586 | https://arxiv.org/abs/2602.09002
- Peer-review status: published (Crossref record confirmed by title search).
- Verified: Abstract, §I, the fine-tuning subsection, §V-B and §VI read by keyword-led passes;
  the formulation and perception modules skimmed. Section numbers below are given only where
  the extract shows them. **Read from** `refs/lb_etiquette_2602_09002.txt` (arXiv v1).
- What the model decides: a geometric planner samples collision-free candidate paths; a
  fine-tuned VLM picks the socially best one — "Acting as a proxy for the average human, the
  VLM assesses whether each candidate path adheres to social norms" (problem formulation).
- Source of the behaviour knowledge: GPT-4o's judgements, **distilled** into a smaller model
  (Qwen-2.5 7B) by supervised fine-tuning on frames from the SCAND dataset labelled by GPT-4o,
  because GPT-4o's "high inference latency makes it impractical for real-time decision-making"
  (fine-tuning subsection).
- Scenarios: four controlled contexts on a real robot, including a queue and a photographer
  with a subject; three trials per scenario; five baselines, among them [Song-VLMSocialNav]
  (§V-B).
- Does it work: Abstract — lowest personal-space-violation duration, least pedestrian-facing
  time, and no social-zone intrusions.
- Limitations stated: the VLM sees one frame and has no memory (so it can miss a long queue);
  several simultaneous human activities "can confuse the VLM's prioritization of social norms";
  the ideal path may not be among the candidates (§VI).
- Relevance to this FYP: `[inference]` T1 is weak here — the conflicts are with *standing*
  social arrangements (a queue, a line of sight), not a contest for the same space. Its value
  is the architecture: **large model → distilled smaller model → picks among options a
  geometric planner already guarantees are safe.** That is the same division of labour as
  roadmap steps 3–5.
- BibTeX: `fang2026etiquette`

### [Wang-SAMALM]: Multi-Agent LLM Actor-Critic Framework for Social Robot Navigation

- Authors / Year / Venue: Weizheng Wang, Ike Obi, Byung-Cheol Min / 2025 / arXiv:2503.09758v1
  `[preprint]`. No published version found by a Crossref title search.
- Link: https://arxiv.org/abs/2503.09758
- Verified: Abstract, contribution list and the experiments section read by keyword-led passes; the critic-score
  equations were not followed. **Read from** `refs/lb_samalm_2503_09758.txt`.
- What the model decides: each robot has its own LLM "actor" that "directly generate[s] control
  signals"; a global LLM critic scores group-level behaviour and per-robot critics score each
  robot's context; low-scoring actions are re-queried (Abstract).
- T2: the robots do not converse with one another. `[inference]` But a global critic that sees
  every robot is a central arbiter, so this is not a decentralised, communication-free rule.
- Source of the behaviour knowledge: "zero-shot navigation through commonsense inference"
  (Abstract), with socially acceptable distances set per "robot personality" in the prompt.
- Evaluation: simulation only; 3 robots among 10 simulated humans and 5 robots among 10 humans
  (experiments section), 50 test cases, baselines LLaMA-8B/70B/405B, GPT-3.5, GPT-4, GPT-4o used as centralised
  planners. ⚠ Table I did not survive extraction legibly; no number is quoted.
- Relevance to this FYP: `[inference]` evidence that several LLM-driven movers can share a
  space with pedestrians without dialogue — at the price of several LLM calls per robot per
  step, which does not scale toward 10,000 agents.
- BibTeX: `wang2025samalm`

### [Baimbetova-PedAwareAV]: Pedestrian-Aware LLM-Driven Behavioral Planning for Autonomous Vehicles

- Authors / Year / Venue: Aidana Baimbetova, Haruki Yonekura, Hamada Rizk, Hirozumi Yamaguchi /
  2026 / arXiv:2605.16858v1. The arXiv record states it is accepted at the 29th IEEE ITSC; the
  proceedings record was not looked up.
- Link: https://arxiv.org/abs/2605.16858
- Verified: Abstract, the framework section and the results paragraphs read by keyword-led
  passes.
  **Read from** `refs/lb_pedaware_av_2605_16858.txt`.
- What the model decides: scene state is turned into a text prompt; the LLM is asked to "infer
  pedestrian intent, anticipate risk, and generate cautious tactical driving decisions"
  (Abstract), choosing one of five manoeuvres — stay idle, turn left, turn right, accelerate,
  decelerate (framework section). A motion planner executes it.
- Evaluation: SUMO; jaywalking and "turn-back" crossings. Zero-shot, 68% collision-free success
  against 17.7% for deep-RL baselines; with few-shot episodic memory, 96.0% against 82.0% for a
  custom DQN in the single-pedestrian scenario (Abstract). Models are small: Gemma3-1B,
  Qwen3-1.7B, LLaMA3.2-1B (experiments section).
- Relevance to this FYP: `[inference]` the same mechanism in the vehicle–pedestrian setting,
  which [`../llm-conflict-resolution/search-log.md`](../llm-conflict-resolution/search-log.md)
  earlier set aside because the two parties are so unequal. Useful here for one point only:
  ~1B-parameter models already do this, which bears on the DeepSeek budget.
- BibTeX: `baimbetova2026pedaware`

### [Yoldas-YieldBias]: LLM-Driven Autonomous Vehicles Inherit Human Driver Biases in Pedestrian Yielding

- Authors / Year / Venue: Irem Yoldas, Martim Brandão, Jie Zhang, Odinaldo Rodrigues / 2026 /
  arXiv:2609.00192v1 `[preprint]`.
- Link: https://arxiv.org/abs/2609.00192
- Verified: Abstract, §I, §III (scenario construction), §IV-A to §IV-B and the limitations
  paragraph read; the VLM half (§IV-C) not read. **Read from**
  `refs/lb_yieldbias_2609_00192.txt`. ⚠ Two-column extraction interleaves text and figure
  labels; I quote only figures that appear in running prose.
- What it is: **not a resolver — an audit of one.** It asks whether an LLM's decision to yield
  changes with *who* the pedestrian is, holding the scene fixed ("All Else Being Equal" test).
- Method: 3,157 unique text driving scenarios, each re-issued with a pedestrian attribute
  injected — gender, ethnicity, religion, disability, age, skin tone, socio-economic status,
  and gender × age / disability / ethnicity combinations (§III, Table I). LLMs tested
  zero-shot: Qwen-3, Llama-3.1, Mistral, GPT-4o (§IV-A).
- Results that matter (§IV-B):
  - Qwen-3 "yielded the least to female pedestrians (61%) and the most when no gender was
    indicated (92%)".
  - "The group 'paralyzed' received lower yield rates across all models"; Qwen-3's was 10%.
  - Llama-3.1 yielded 99.6–100% for every disability label except "paralyzed" (95%).
  - Mistral: 98% for female, 97% for male — small, but significant by chi-square.
  - GPT-4o: high yield rates, "most pairwise differences were not statistically significant".
- Authors' reading: the findings "raise questions about the 'common sense' model paradigm"
  (Abstract).
- Limitations stated: the image-based test is "not as robust" as the text-based one.
- Relevance to this FYP: `[inference]` **directly relevant to `run01`'s flagged pattern** that
  female personas yield more than male ones (`dataset/generated/validation_report.md`). This
  paper measures the mirror quantity — whether an LLM yields *to* a person differently by
  demographic — and finds it does, differently per model, and without being asked. It supplies
  (a) a ready audit design (same scene, one attribute changed, chi-square on yield rate) that
  could be run on the FYP dataset, and (b) a citable warning that "the LLM knows how people
  behave" and "the LLM reproduces stereotypes about people" are not separable without such a
  test. It belongs with issue #16's material in
  [`../demographic-personas/`](../demographic-personas/llm-demographic-effects.md).
- BibTeX: `yoldas2026yieldbias`

---

## 2. Tier B — conflict resolved by an LLM without dialogue, but not from knowledge of people

### [Seo-LLMDR]: LLMDR: LLM-Driven Deadlock Detection and Resolution in Multi-Agent Pathfinding

- Authors / Year / Venue: Seungbae Seo, Junghwan Kim, Minjeong Shin, Bongwon Suh / 2025 /
  arXiv:2503.00717v1 `[preprint]` (the first page says it has been submitted to the IEEE).
- Link: https://arxiv.org/abs/2503.00717
- Verified: Abstract, §I, §III-B, §IV, §V-A to §V-C read; §II and §V-D skimmed. **Read from**
  `refs/lb_llmdr_2503_00717.txt`.
- What the model decides: given a short log of agent positions, the LLM (i) labels agents as
  deadlocked ("No movement", "Wandering") or not, (ii) groups deadlocked agents within
  Manhattan distance 2, and (iii) assigns each group a strategy, "leader" or "radiation"
  (Prompt 1, §IV-A).
- How the conflict is resolved: the strategy is turned into a **priority order** — lead agents,
  then radiate agents, then non-deadlocked agents, then "yield agents" who "prioritize staying
  to allow the lead agent to move" — and handed to PIBT, which produces collision-free
  one-step moves (§IV-B, Algorithm 2). No agent communicates.
- T3: **fails.** The criteria are written into the prompt by the authors — e.g. *"Use the
  'leader' method ... when any agent in the group has a goal more than 8 Manhattan units
  away"* (Prompt 1) — and the lead agent is defined as the one farthest from its goal (§IV-B).
  `[inference]` The LLM here is a classifier applying a hand-written rule, not a source of the
  rule.
- Evaluation: four standard MAPF maps, 4–64 agents, on top of three learned solvers (DHC, DCC,
  EPH), with gpt-3.5-turbo and gpt-4o (§V-A).
- Does it work: on the warehouse map with 64 agents, success rate rises from 1% to 83% (DHC),
  14% to 74% (DCC) and 6% to 68% (EPH base model) (Table I, last row). ⚠ The table's row labels
  were displaced in extraction; I take the last of five rows to be 64 agents, which matches the
  prose ("DHC struggled in the 64-agent scenario, but with LLMDR, it achieved the highest
  success rate", §V-B). A stronger model gives shorter episodes (§V-C).
- Relevance to this FYP: `[inference]` **this is the LLM analogue of the gap in
  [`../simulation-rules/research-gap.md`](../simulation-rules/research-gap.md) §5.** That file
  concludes the field has machinery for applying a precedence order (PIBT among it, rule SR18)
  and no good source for the order. LLMDR plugs an LLM into exactly that slot — and then fills
  the slot with a designer's rule of thumb. It shows the plumbing works; it leaves the FYP's
  question (can the *order itself* come from knowledge of people?) untouched.
- BibTeX: `seo2025llmdr`

### [Garg-FMDeadlock]: Foundation Models to the Rescue: Deadlock Resolution in Connected Multi-Robot Systems

- Authors / Year / Venue: Kunal Garg, Songyuan Zhang, Jacob Arkin, Chuchu Fan / 2024 /
  arXiv:2404.06413v2 `[preprint]`. A Crossref title search returned a *different* CDC 2024
  paper by an overlapping author; I did not establish whether the two are related.
- Link: https://arxiv.org/abs/2404.06413
- Verified: Abstract, §I, the planner description and the experimental set-up read by
  keyword-led passes. **Read from** `refs/lb_fm_deadlock_2404_06413.txt`. ⚠ All results are in
  box plots that did not survive extraction; no number is quoted.
- What the model decides: once a deadlock is detected, an LLM or VLM is prompted with the
  robots' positions, goals and the obstacles seen so far, and returns **a leader and a set of
  waypoints for it**; the team re-forms as leader–followers and a learned low-level controller
  keeps it safe and connected (Abstract).
- Evaluation: "Room" environments with 5 robots and "Maze" environments with 25 and 50; GPT-4,
  GPT-4o, GPT-3.5 and Claude 2/3 models; compared with A* and a random baseline (experiments section).
- Does it work: Abstract — foundation models do better than grid-based planners in
  goal-reaching rate and computation time in complex environments.
- T3: fails — no appeal to human behaviour. Also a cooperative team that must stay within
  communication range, i.e. not agents with competing goals.
- Relevance to this FYP: `[inference]` an independent second case of "LLM breaks the symmetry by
  naming who leads; a cheap controller does the motion" — the same shape as
  [Mahadevan-GameChat], minus the dialogue.
- BibTeX: `garg2024fmdeadlock`

### [Zhao-MotionAgents]: Navigating Motion Agents in Dynamic and Cluttered Environments through LLM Reasoning

- Authors / Year / Venue: Yubo Zhao, Qi Wu, Yifan Wang, Yu-Wing Tai, Chi-Keung Tang / 2025 /
  arXiv:2503.07323v2 `[preprint]`.
- Link: https://arxiv.org/abs/2503.07323
- Verified: Abstract, the multi-agent formulation in §3, and §4.2.2 read by keyword-led passes.
  **Read from** `refs/lb_motionagents_2503_07323.txt`.
- What the model decides: one LLM generates trajectories for all agents on a tokenised floor
  plan; the trajectories are simulated; "If a collision occurs at time t, the agent queries the
  LLM using its current position ... requesting a refined path" (§3). Training-free.
- Evaluation: two and three agents, at most three retries (§4.2.2); a five-agent example is
  shown qualitatively. Performance falls as agents are added but "remain[s] within a reasonable
  and practical range" (§4.2.2).
- One remark worth keeping: when each agent repairs its path independently, scores are slightly
  lower, "which aligns with real-world observations — for instance, when two people walk toward
  each other and both instinctively step in the same direction" (§4.2.2). `[inference]` That is
  the symmetric-tie failure of [`../simulation-rules/research-gap.md`](../simulation-rules/research-gap.md)
  §5, reproduced by an LLM.
- T3: fails — the LLM is a spatial reasoner; human behaviour appears only as that analogy.
- BibTeX: `zhao2025motionagents`

---

## 3. Tier C — games: partner behaviour inferred from observation, no dialogue

Screened, not studied. In all three the "conflict" is mostly over *tasks*; the spatial part
(two cooks, one corridor) is handled by a path-finding routine under the LLM.

| Handle | What the LLM does | Why it is only a partial match | Read |
|---|---|---|---|
| [Zhang-ProAgent] — AAAI 2024, 38(16), 17591–17599 | In Overcooked-AI, infers the teammate's intention from its observed actions and corrects that belief against what the teammate then does; the authors contrast this with methods that rely on communication (related work) | A blocked path is handled by the controller finding "an alternative interconnected route" (qualitative results). It loses to a trained baseline on the Forced Coordination layout (results) | keyword-led; `refs/lb_proagent_2308_11339.txt` |
| [Cross-HypotheticalMinds] — ICLR 2025 | In Melting Pot, a theory-of-mind module writes hypotheses about other agents' strategies in natural language, scores them by how well they predict behaviour, and plans on the best one | An action plan is carried out "with a pathfinding algorithm" (method overview). The authors attribute a loss to "the limited spatial reasoning abilities of ungrounded LLMs like GPT4" (results) | keyword-led; `refs/lb_hypotheticalminds_2407_07086.txt` |
| [Agashe-LLMCoordination] — Findings of NAACL 2025 | Benchmarks LLMs on pure-coordination games (Overcooked-AI layouts, Hanabi), including theory-of-mind questions | Benchmark of coordination, not a conflict method | abstract and layout list only; `refs/lb_llmcoordination_2310_03903.txt` |

`[inference]` What these add: the idea that an LLM can resolve a coordination problem by
**modelling the other party from what it does**, with no messages. None claims the model's
picture of the partner comes from knowledge of people in general.

---

## 4. Crowd-simulation near-misses — why each was excluded

These are the papers closest to the FYP's own setting. Each fails T1 or T2.

| Paper | What the LLM does | What actually handles the encounter | Fails |
|---|---|---|---|
| Ma, Yu, Tang, Li (2026). *An LLM-powered Agent Framework for Heterogeneous Evacuation Behavior Modeling under a Moving Threat in a Public Plaza.* arXiv:2609.37009 `[preprint]` | Persona-conditioned (Five-Factor) agents read an ASCII view and choose a route or target; route options are annotated with "crowding" | **A random draw**: "when several entities select the same cell, one is chosen at random and the others are assigned feasible cells" (§2.3.6). Eleven pedestrians (§3) | T1 |
| Calzolari et al. (2026). *LLM-Driven Personalities for Decision Making in Emergency Simulations.* arXiv:2606.31038 `[preprint]` | OCEAN-conditioned agents choose Evacuate / Continue / Panic, and whether to help; 600 agents | Movement "using the crowd simulation algorithm BioCrowds" (§3.3) | T1 |
| Nguyen et al. (2026). *GROVE: Grounded Pedestrian Simulation via Natural Language for Interactive Social Robot Navigation.* arXiv:2606.25504 (accepted IROS 2026 per arXiv) | Turns a text description into behaviour trees for simulated pedestrians | "the SFM handles local collision avoidance among agents" (method section) | T1 |
| Lin et al. (2026). *SenseWalk.* arXiv:2607.00989 `[preprint]` | Persona-driven visitor trajectories in zoned venues | A social force model "to guarantee physical realism" and prevent collisions (method section) | T1 |
| Amano & Yamaguchi (2026). *Distilling Aggregate Mobility Statistics into a Language Model Policy for Post-Event Crowd Simulation.* ACM SIGSPATIAL 2026 short paper; arXiv:2608.19778 | A fine-tuned language-model policy chooses each agent's destination | Not about encounters at all | T1 |
| Liu, Shatzel, Haworth, Schneider (2025). *Emergent Crowds Dynamics from Language-Driven Multi-Agent Interactions.* arXiv:2508.15047 `[preprint]` | LLMs generate **inter-agent dialogue**, and set each agent's goal and steering parameters from it | Force-based steering (§3.3) | T2 (and T1) |
| Ruan et al. (2025). *Benchmarking LLMs' Swarm Intelligence* (SwarmBench). arXiv:2505.04364 | Decentralised LLM agents on a grid | Agents use **local communication** (abstract) | T2 — abstract only |
| Shindo et al. (2026). *SocialGrid.* arXiv:2604.16022 `[preprint]` | An *Among Us*-style benchmark | Social deduction; the abstract reports agents "getting stuck in repetitive behaviors or failing to navigate basic obstacles" | scope — abstract only |
| Li & Zhou (2025). *LLM-Flock.* arXiv:2505.06513 | Decentralised flocking / formation control | Formation, not conflict | scope — abstract only |
| *Socially-Aware Robot Navigation Enhanced by Bidirectional Natural Language Conversations Using LLMs.* arXiv:2409.04965 | — | Conversation is the method, by its title | T2 — **title only, not opened** |

Already in this repo and not re-read here:

- **[Mahadevan-GameChat]** — fails T2 by design (dialogue).
- **[Zhang-DFD]** (ACM TOMACS 2026) — distils rules from LLM-driven evacuation agents. Could
  pass all three tests. It is still recorded at abstract level only in
  [`../llm-conflict-resolution/topic1-llm-conflict.md`](../llm-conflict-resolution/topic1-llm-conflict.md).
  **The full text needs reading before the bottom line above is quoted.**
- **CrowdVLA** (arXiv:2604.05525) — excluded from issue #22 as "not a conflict rule" after a
  scope check only ([`../simulation-rules/s1-crowd-simulation.md`](../simulation-rules/s1-crowd-simulation.md),
  "Seed excluded"). It is a non-conversational, per-pedestrian model in a crowd simulation, so
  it may pass T1 and T2; whether it passes T3 depends on whether its behaviour comes from the
  language model's prior or from fine-tuning data. **Not determined.**

### Not obtained

No summary is given for these; the descriptions are other papers' or the publisher's abstract
as returned by a search engine, and are marked as such.

- Dang, Zhu, Li, Xie, Zhang (2025). *Large-language-model-driven agents for fire evacuation
  simulation in a cellular automata environment.* *Safety Science* 191, 106935.
  https://doi.org/10.1016/j.ssci.2025.106935 — paywalled. `[secondhand]` Ma et al. describe it
  as combining "LLMs with a cellular-automaton environment to examine how agent backgrounds and
  communication relate to fire-evacuation outcomes" (their §1). **A cellular automaton is where
  a same-cell conflict rule would live, so this is the unread paper most likely to matter.**
- Yang, Ceferino, Zhang, Gu, Guo, Kondo (2026). *When agents learn to think: Large language
  model-enhanced agent-based modeling for crowd evacuation in disaster scenarios.* *Reliability
  Engineering & System Safety* 269, 112056. https://doi.org/10.1016/j.ress.2025.112056 —
  paywalled.
- A wayfinding study by Dang et al. (2025) that "included human participants as a reference"
  `[secondhand]` (Ma et al. §1). Title not identified.

---

## 5. What this adds up to

All `[inference]`.

1. **The FYP's exact combination was not found.** No paper opened here has LLM-derived
   behaviour knowledge deciding an *agent-versus-agent* encounter between *simulated
   pedestrians* with no dialogue. Conditional on a thin search and three unread candidates
   ([Zhang-DFD], CrowdVLA, Dang et al.).
2. **In LLM crowd simulators the conflict layer is still classical.** Five of the six opened
   put a social force model, BioCrowds, force-based steering or a random draw underneath the
   LLM; the sixth is about destination choice and does not discuss encounters (§4). This matches [`../simulation-rules/research-gap.md`](../simulation-rules/research-gap.md)
   §5: the precedence order is random or unstated — now including in simulators whose agents
   are otherwise driven by a language model.
3. **Where an LLM does decide the encounter, it emits a small discrete answer and a classical
   controller executes it.** Side and speed ([Song-VLMSocialNav]); one path among safe
   candidates ([Fang-Etiquette]); a priority order for PIBT ([Seo-LLMDR]); a leader
   ([Garg-FMDeadlock]). No paper has the LLM produce trajectories that are then trusted
   without a safety layer — [Zhao-MotionAgents] comes closest and needs retries.
4. **The cost wall is confirmed from a third direction.** 2–3 s per query
   ([Song-VLMSocialNav]); distillation to a 7B model for real-time use ([Fang-Etiquette]);
   several LLM calls per robot per step ([Wang-SAMALM]). Nothing here runs an LLM per agent per
   step at anything like 10,000 agents; the largest count in Tier A or B is 64 ([Seo-LLMDR]),
   with one LLM call per detection window, not per agent.
5. **T3 is rarely clean.** In the best match the passing-side rule is typed into the prompt
   ([Song-VLMSocialNav]); in [Seo-LLMDR] the whole decision rule is. Whether the *model* knows
   the convention, as opposed to obeying an instruction, is tested by none of them. That is the
   supervisor's research question, and it appears to be open.
6. **The one paper that tests what the model "knows" about people finds demographic bias in
   yielding** ([Yoldas-YieldBias]). It should be read alongside `run01`'s gender pattern
   before that pattern is interpreted as either realism or artefact.

## 6. Open questions and risks

- **R1. Thin search.** 13 web searches, one day, arXiv-heavy; no Scopus, Web of Science, IEEE
  Xplore, ACM DL or Google Scholar; no citation chaining. See [search-log.md](search-log.md).
- **R2. Every entry was read selectively**, mostly by keyword-led passes over the text
  extract. Claims are scoped to the passages cited. None is safe to quote in the report
  without opening the PDF at the locator.
- **R3. Three unread candidates could overturn the bottom line**: [Zhang-DFD] (full text),
  CrowdVLA (full text), Dang et al. 2025 (not obtained).
- **R4. Six of eleven entries are preprints**, including two of the three in Tier B.
- **R5. The three tests are mine.** Splitting "passes T1/T2/T3" this way is a judgement about
  what "strictly related" means. **Needs supervisor sign-off** if the tiers are used in the
  report.
- **R6. Tier A is a different problem in one respect that matters**: one model-driven party
  among real or scripted humans. Two model-driven parties facing each other — the symmetric
  case — is not tested by any Tier A paper.
- **R7. Numbers lost to extraction**: [Song-VLMSocialNav] Table I, [Wang-SAMALM] Table I,
  [Garg-FMDeadlock] all results. [Seo-LLMDR] Table I is quoted on an assumption about row
  order that is stated in the entry.
- **R8. Not checked against CrowdGym.** As in issue #22, relevance lines are about the FYP's
  aims, not `integration/crowdgym_mapping.md`.
