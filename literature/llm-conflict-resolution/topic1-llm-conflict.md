# Topic 1 — LLM-to-LLM conflict resolution and pattern extraction

Prepared for issue [#8](https://github.com/M450NCH00/CrowdSimulation/issues/8).
Companion file: [`topic2-sociological-grounding.md`](topic2-sociological-grounding.md).
Queries, sources, rejections and dead ends: [`search-log.md`](search-log.md).

This topic supports the claim the FYP now has to defend:

> *Letting LLM agents communicate to resolve a conflict produces a resolution
> pattern that is reusable — it can be extracted once and applied to later
> conflicts without re-running the exchange.*

Every title, author list, year and venue below was confirmed by opening the actual
abstract page, publisher record or PDF; caches are in [`../../refs/`](../../refs/) and
the bibliographic fields were independently cross-checked against Crossref
(`refs/crossref_metadata.json`). Numbers that could not be confirmed from a primary
source are marked `[unverified]`. Preprints are labelled `[non-archival]`.

## Read this first — two findings that affect the project plan

**1. The supervisor's two papers are one citation chain, not two leads.**
Wu et al. §6.1 states: *"We follow Wang et al. (2015) to simulate EE in a grid
environment."* The 2015 *Physica A* paper is the model Wu et al.'s evacuation case
study is built on. So the assigned reading is a single line of work — a 2015 panic
evacuation model, re-run in 2024 with LLM agents in place of rule-based ones.

**2. The core idea of this FYP has already been published, and partly by NTU.**
[Zhang-DFD] (ACM TOMACS, 2026) proposes **Decision Function Distillation**: run LLM
agents, then distil the strategy underlying their decisions into interpretable
rule-based code, so the simulation no longer pays for LLM inference. It is motivated
by the same two constraints as this project (inference cost caps crowd size; opaque
decisions hurt reliability) and is demonstrated **on agent-based crowd evacuation**.
Two of its four authors (Wen Jun Tan, Wentong Cai) are at NTU, the same institution
as the senior's CrowdGym FYP.

This does not make the FYP redundant, but it does mean the project must state its
position relative to [Zhang-DFD] rather than rediscover it. The honest gap is narrow
and worth naming explicitly — see [Zhang-DFD]'s entry and the
["What is actually left to do"](#what-is-actually-left-to-do) section at the end.
**This is a judgement call, not a design decision — it needs supervisor sign-off.**

## Summary table

| # | Handle | Year | Venue | Peer-reviewed | Rel. |
|---|--------|------|-------|---------------|------|
| S1 | Wu — Shall We Team Up *(supervisor-assigned)* | 2024 | EMNLP Findings | yes | 4 |
| 1 | Zhang — Decision Function Distillation | 2026 | ACM TOMACS | yes | **5** |
| 2 | Mahadevan — GameChat | 2025 | IEEE MRS | yes | **5** |
| 3 | Ashery — Emergent Social Conventions | 2025 | *Science Advances* | yes | **5** |
| 4 | Abdelnabi — LLM-Stakeholders Negotiation | 2024 | NeurIPS D&B Track | yes | 4 |
| 5 | Bianchi — NegotiationArena | 2024 | ICML | yes | 4 |
| 6 | Piatti — GovSim | 2024 | NeurIPS | yes | 3 |
| 7 | Chen — Why MAPF with LLMs Has Not Succeeded | 2024 | arXiv `[non-archival]` | no | 4 |

Seven entries beyond the supervisor-assigned one. Six of the seven are peer-reviewed;
the one preprint is included as a *negative* result and is not the sole support for
any claim.

---

### [Wu-SWTU] — Shall We Team Up: Exploring Spontaneous Cooperation of Competing LLM Agents

> **Supervisor-assigned.** Not a search result, and per the issue it is counted
> separately from the 10-paper target.

**Authors / Year / Venue:** Zengqing Wu, Run Peng, Shuyuan Zheng, Qianying Liu, Xu Han,
Brian I. Kwon, Makoto Onizuka, Shaojie Tang, Chuan Xiao / 2024 / *Findings of the
Association for Computational Linguistics: EMNLP 2024*, pp. 5163–5186. Preprint
arXiv:2402.12327.

**Link:** https://aclanthology.org/2024.findings-emnlp.297/ | doi:10.18653/v1/2024.findings-emnlp.297

**Verified:** yes — opened the ACL Anthology landing page (cached
`refs/wu2024_shall_we_team_up_acl.html`) and the full PDF (cached
`refs/wu2024_shall_we_team_up.pdf`, text-extracted to `.txt`); fields cross-checked
against Crossref.

**Topic:** 1

**Problem:** Can LLM agents develop cooperation *spontaneously* — without being told in
the prompt to cooperate — in situations where their interests compete?

**Method:** Three case studies under the authors' SABM framework: Keynesian Beauty
Contest (game theory), Bertrand Competition (economics), and **Emergency Evacuation**
(behavioural science). The EE study is the one that matters here. Following Wang et al.
(2015), 100 agents occupy a 33×33 grid room with three exits (left, right, bottom);
each round runs Communication → Planning → Action → Update. Agents within a set distance
can hear each other; each agent has a **20% probability per round** of communicating and
re-planning, otherwise it continues its existing plan. Simulation stops when all escape
or at 50 rounds; 5 runs with different initial positions. Three conditions: no
communication, communication, and communication with an uncooperative persona.
Experiments used a single version of GPT-4.

**Results that matter:**
- **Exit balancing is the real result** (§6.2, Fig. 9). With communication, escapes
  distribute more evenly across the three exits instead of converging on one. The
  mechanism is explicit: agents share both *proximity* and *congestion* information,
  e.g. one agent's message — *"Bottom exit seems closer with fewer people. Let's choose
  that for a faster escape. Stay strong and help each other!"* — is picked up and
  echoed by another agent.
- **The speed result is much weaker than the prose suggests.** Table 2 (cumulative
  escapes out of 100): at round 50, With Communication reaches 100.0, Without
  Communication 99.8, Uncooperative 99.0. At round 15 the *no-communication* condition
  is actually ahead (51.2 vs 48.8). Over 5 runs and with no dispersion reported, this
  is a very thin margin to carry the claim that communication improves evacuation speed.
  The authors' defensible claim is the narrower one they also state — communication was
  "the only baseline group to successfully escape within 50 rounds in all five runs."
- **Cooperation is learned in-context, not recalled.** Across KBC and BC, convergence is
  gradual (BC takes ~200 rounds to reach the cartel price); explicitly instructing
  cooperation instead produces immediate convergence (Fig. 4a). The authors argue this
  gradualness is evidence against training-data leakage.

**Limitations / criticisms:** The authors concede the EE case is their weakest —
*"It would be beneficial to have more metrics for evaluating spontaneous cooperation in
EE, and leave this for future study."* Single model (GPT-4 only), which they call a
proof-of-concept limitation; cost was $900/$3000/$1000 across the three studies.
My own criticisms: (a) the evacuation conclusion rests on Table 2 margins that are
within plausible run-to-run noise, and no significance test or variance is reported;
(b) "cooperation" in EE is operationalised loosely — encouraging words in a chat log are
counted as cooperative behaviour without a measure distinguishing them from noise;
(c) 100 agents × 50 rounds at GPT-4 prices is exactly the cost wall this FYP has to get
around.

**Relevance to this FYP (4):** It is the closest published precedent for "LLM agents talk
during a spatial conflict, and the talk changes the outcome," and its mechanism transfers
directly: the useful content of the messages is **(exit identity, congestion level)** —
agents resolve conflict by *redistributing across alternatives*, not by taking turns.
For a 2-agent hallway there is no third exit to redistribute to, so this specific pattern
does **not** transfer to the starting scenario; that gap is what makes Topic 2's
turn-taking literature necessary. Its cost figures also justify the distillation approach.

**BibTeX:** `wu-etal-2024-shall` in [`refs.bib`](refs.bib).

---

### [Zhang-DFD] — Sense, Think, Act, Reflect: Distilling Fast and Interpretable Decision Functions from LLM-Driven Crowds

**Authors / Year / Venue:** Yichi Zhang, Philipp Andelfinger, Wen Jun Tan, Wentong Cai /
2026 / *ACM Transactions on Modeling and Computer Simulation* (TOMACS). Open access
(CC-BY).

**Link:** https://doi.org/10.1145/3818686

**Verified:** yes — but by an indirect route, recorded honestly. **ACM DL returned
HTTP 403** to automated fetches (the same block issue #2 hit). Title, authors, venue,
year and DOI were confirmed from the Crossref record (`refs/crossref_metadata.json`) and
the Semantic Scholar record (`refs/s2_zhang2026_dfd.json`), and the BibTeX from the
second author's own publications page (philipp-andelfinger.net). The abstract quoted
below is from the Semantic Scholar record. **I have not read the full text**, so all
method detail below is abstract-level, and no quantitative result is quoted because
none was available without the PDF. Someone should obtain the PDF through the NTU
library before this paper is cited in the report.

**Topic:** 1

**Problem:** LLMs generate human-like agent behaviour, but "the substantial inference
cost restricts the crowd sizes that can be tackled, and the opaque nature of LLM-based
decision making raises reliability concerns."

**Method:** **Decision Function Distillation (DFD)** — extract the strategies underlying
LLM agents' decision making "in a rule-based and interpretable form." The decision
function is produced by an *iterative* process: intermediate insights are gathered from
historical agent trajectories, refined, and finally translated into **commented code**.
Two variants: intermediate insights generated directly as text from few-shot examples,
or explicitly formalised into code snippets. Evaluated on **agent-based crowd evacuation
scenarios**, compared against classical symbolic regression (SR) and a state-of-the-art
LLM-based SR.

**Results that matter:** The abstract states DFD "outperforms both classical and a
state-of-the-art LLM-based SR." `[unverified]` — no magnitude, no speedup figure and no
fidelity-to-LLM measure could be confirmed without the full text.

**Limitations / criticisms:** Cannot be assessed responsibly from the abstract alone.
The obvious question to put to the paper on reading it is whether the distilled function
is validated against *human* behaviour or only against the LLM's own decisions — if only
the latter, it inherits whatever the LLM got wrong, and this FYP's validation step
(roadmap 5) remains an open contribution rather than a duplicated one.

**Relevance to this FYP (5):** This is the closest prior work in existence to roadmap
steps 3–4. The pipeline "run LLM agents → extract the strategy → emit interpretable code
→ drop the LLM at runtime" *is* this project's plan, it is demonstrated on crowd
evacuation, and it is motivated by the same 10,000-agent scalability constraint. Its
output form — commented rule code — is also exactly what
`integration/crowdgym_mapping.md` §B needs for `build_conflict_policy()` /
the overridden `RL_take_action`. Practically it should be treated as the **baseline to
beat or to build on**, not as a competitor to avoid citing.

**BibTeX:** `zhang2026sense` in [`refs.bib`](refs.bib).

---

### [Mahadevan-GameChat] — GameChat: Multi-LLM Dialogue for Safe, Agile, and Socially Optimal Multi-Agent Navigation in Constrained Environments

**Authors / Year / Venue:** Vagul Mahadevan, Shangtong Zhang, Rohan Chandra / 2025 /
2025 IEEE International Symposium on Multi-Robot and Multi-Agent Systems (MRS).
Preprint arXiv:2503.12333.

**Link:** arXiv:2503.12333 | https://arxiv.org/abs/2503.12333

**Verified:** yes — opened the arXiv abstract page (cached
`refs/mahadevan2025_gamechat_abs.html`) and the full PDF (cached
`refs/mahadevan2025_gamechat.pdf`, text-extracted); venue stated in the arXiv comments.

**Topic:** 1

**Problem:** When two agents meet in a doorway or intersection, **spatial symmetry**
means neither has a reason to yield, and they deadlock. Who should go first, when each
agent's urgency is private and there is no central authority?

**Method:** **Two agents** with single-integrator unicycle dynamics. Each has a `gpt-4o-mini`
instance and a task described in natural language. On mutual observation they exchange
messages in turns, each seeing the other's last message, until either they reach a
consensus on whose task has higher priority or **each has sent four messages without
agreement** (a hard cap). The prompt tells them to converse "until you determine whether
you have more or less priority as them depending on the tasks you and they are
performing" and to output `1` once a consensus is reached. Three task types in decreasing
priority (hospital, airport, grocery), plus deliberately harder pairs (Table II) such as
*"fire truck to apartment on fire"* vs *"ambulance to the ER"*. The consensus sets a
**leader/follower** assignment, which is executed by a game-theoretic MPC controller with
**control barrier functions** for collision avoidance. Two scenarios, 18 versions each:
a **0.4 m doorway** (agents start 2 m away, 0.5 m north/south of it, goals on the far side)
and a 0.4 × 0.4 m intersection.

**Results that matter:**
- **The symmetric doorway deadlocks the standard baseline in every single run:**
  MPC-CBF records **18 deadlocks out of 18** doorway scenarios (Table III). GameChat
  records **0 collisions and 0 deadlocks** in both scenarios.
- **Priority correctness doubles from chance to perfect:** non-communicative methods get
  the higher-priority agent through first in **50%** of scenarios — i.e. random — while
  the LLM-dialogue variants reach **100%**. The abstract reports up to **35%** improvement
  in time-to-goal over a naive baseline in the worst case and **20%** over the
  state-of-the-art baseline in the intersection scenario.
- **The dialogue matched the oracle.** The authors report GameChat performed as well as
  *GameChat Ground Truth*, the condition where agents are simply told the true priorities
  — "the correct consensus was always reached."

**Limitations / criticisms:** The authors are unusually candid about two things, and both
matter here. First, that 100% is **post-prompt-engineering**: early runs had LLMs
"hallucinating false instructions, forgetting the consensus, etc.," and "after carefully
modifying the prompts, these problems became less and less frequent." Second, their
explanation for why consensus always succeeds — *"by default, LLMs are designed to be
very honest and cooperative"* — is an admission that the result depends on alignment
training, not on negotiation competence. An agent with an incentive to overstate its
urgency is untested, and [Bianchi-NegArena] shows exactly that exploit works. Also: only
two agents in the evaluation (the paper sketches a k>2 extension), only one small model,
simulation only, and the priority ordering is supplied by the designer — the LLM
*applies* a hierarchy rather than discovering one.

**Relevance to this FYP (5):** This is the FYP's proposed starting scenario, already
built. Most importantly, **its architecture is the pattern-extraction answer in
miniature**: the LLM exchange does nothing but produce a *symmetry-breaking signal* —
one bit, "who leads" — which is then handed to a cheap deterministic controller that
does the actual movement. That is the cleanest available evidence that the reusable
artefact from an LLM conflict exchange is a **priority/right-of-way ordering**, not a
trajectory, and it maps directly onto the trigger-and-lookup structure already specified
in `integration/crowdgym_mapping.md` §B. The 4-message cap is also a concrete, citable
precedent for bounding exchange length.

**BibTeX:** `mahadevan2025gamechat` in [`refs.bib`](refs.bib).

---

### [Ashery-Conventions] — Emergent social conventions and collective bias in LLM populations

**Authors / Year / Venue:** Ariel Flint Ashery, Luca Maria Aiello, Andrea Baronchelli /
2025 / *Science Advances* 11(20), eadu9368.

**Link:** doi:10.1126/sciadv.adu9368 | open-access record:
https://openaccess.city.ac.uk/id/eprint/35211/

**Verified:** yes — opened the City Research Online open-access record (cached
`refs/ashery2025_social_conventions_oa.html`); title, authors, journal, volume, issue,
article number and DOI cross-checked against Crossref. (science.org and the ADS mirror
both refused automated fetches — see `search-log.md`.)

**Topic:** 1

**Problem:** Can a decentralised population of communicating LLM agents **bootstrap a
shared convention** — a coordination rule nobody imposed?

**Method:** A classic naming-game setup adapted to LLM agents: pairs are drawn
repeatedly from a population, each must produce a name, and both are rewarded only if
they match. No agent sees the global state; no coordination rule is programmed. The
paper then tests (a) whether a population-wide convention emerges, (b) whether
collective bias appears, and (c) whether a committed adversarial minority can overturn
an established convention.

**Results that matter:**
- **Universally adopted conventions emerge spontaneously** in decentralised LLM
  populations, with no explicit programming.
- **"Strong collective biases can emerge during this process, even when agents exhibit
  no bias individually"** — a population-level artefact invisible at the individual level.
- **A committed minority can flip an established convention**, imposing an alternative
  on the majority.

**Limitations / criticisms:** The naming game is deliberately abstract — the "conflict"
is a pure coordination problem with no spatial geometry, no asymmetric stakes and no
physical cost to yielding, so the distance to a hallway crossing is real. Specific
population sizes and model coverage are `[unverified]` here, since I verified this
entry from the open-access metadata record rather than the full text.

**Relevance to this FYP (5):** This is the strongest peer-reviewed evidence that
**a reusable pattern is the kind of thing LLM-to-LLM interaction actually produces** —
which is the core premise of the whole project, and until now supported mainly by
preprints. It also delivers two warnings this FYP must design around. (1) *Collective
bias from unbiased individuals*: a convention distilled from LLM exchanges may encode a
population-level artefact rather than a human behaviour — this is the same class of
problem as the unresolved "female personas yield more" flag in
`dataset/generated/validation_report.md`, and it is the direct argument for why roadmap
step 5 (validation against human data) cannot be skipped. (2) *Minority-driven flips*:
an extracted pattern is not guaranteed stable, so the project should check whether its
pattern is reproducible across runs before treating it as a rule.

**BibTeX:** `ashery2025emergent` in [`refs.bib`](refs.bib).

---

### [Abdelnabi-Negotiation] — Cooperation, Competition, and Maliciousness: LLM-Stakeholders Interactive Negotiation

**Authors / Year / Venue:** Sahar Abdelnabi, Amr Gomaa, Sarath Sivaprasad,
Lea Schönherr, Mario Fritz / 2024 / *Advances in Neural Information Processing Systems 37*
(NeurIPS 2024), **Datasets and Benchmarks Track**. Preprint arXiv:2309.17234
(v1 Sep 2023, v2 Jun 2024).

**Link:** arXiv:2309.17234 | https://proceedings.neurips.cc/paper_files/paper/2024/hash/984dd3db213db2d1454a163b65b84d08-Abstract-Datasets_and_Benchmarks_Track.html

**Verified:** yes — opened the arXiv abstract page (cached
`refs/abdelnabi2024_negotiation_abs.html`); NeurIPS D&B track publication confirmed from
the NeurIPS proceedings page and the NeurIPS 2024 poster listing. Note the venue is
**NeurIPS 2024, not ICLR 2024** — an incorrect venue was returned by an early search and
is recorded as a correction in `search-log.md`.

**Topic:** 1

**Problem:** How well can LLM agents actually negotiate with each other when the
negotiation is multi-party, multi-issue, and includes players who are greedy or
adversarial?

**Method:** A testbed of scorable negotiation games — multi-agent, multi-issue and
"semantically rich," requiring arithmetic, inference, exploration and planning over
dynamic multi-turn dialogue. Multiple metrics quantify performance and **alignment with
the assigned role**. The authors supply procedures to generate new games and raise
difficulty, making it an evolving benchmark, and explicitly evaluate interaction dynamics
when greedy and adversarial players are introduced.

**Results that matter:**
- **The benchmark is hard:** "GPT-3.5 and small models mostly fail, and GPT-4 and SoTA
  large models (e.g., Llama-3 70b) still underperform."
- Safety-relevant dynamics are a first-class result: the presence of a greedy or
  adversarial agent measurably shifts the interaction, rather than being absorbed by
  the other agents' cooperativeness.

**Limitations / criticisms:** The negotiations are semantic and numeric, with no spatial
or embodied component — nothing here is about occupying the same physical space. The
games are complex enough that failures are hard to attribute to negotiation ability
specifically rather than to arithmetic or long-context weakness, which the authors
partly acknowledge by separating the metrics. Exact per-model scores are `[unverified]`
here (verified from the abstract, not the results tables).

**Relevance to this FYP (4):** It is the counterweight to [Mahadevan-GameChat]'s tidy
100%. GameChat's agents always reached the correct consensus because they were honest
and the task was easy; this benchmark shows that once agents have real incentives to
misrepresent, even frontier models underperform. For this FYP that sets the honest scope:
the 2-agent hallway is tractable *because* it is simple, and any claim that the extracted
pattern generalises to richer conflicts needs evidence, not extrapolation. The
role-alignment metrics are also a usable model for checking whether an agent given a
persona actually behaves like it.

**BibTeX:** `abdelnabi2024cooperation` in [`refs.bib`](refs.bib).

---

### [Bianchi-NegArena] — How Well Can LLMs Negotiate? NegotiationArena Platform and Analysis

**Authors / Year / Venue:** Federico Bianchi, Patrick John Chia, Mert Yuksekgonul,
Jacopo Tagliabue, Dan Jurafsky, James Zou / 2024 / *Proceedings of the 41st International
Conference on Machine Learning* (ICML 2024), PMLR 235:3935–3951. Preprint arXiv:2402.05863.

**Link:** arXiv:2402.05863 | https://proceedings.mlr.press/v235/bianchi24a.html

**Verified:** yes — opened the arXiv abstract page (cached
`refs/bianchi2024_negotiationarena_abs.html`) and the PMLR v235 landing page, which
supplied volume, pages and the official BibTeX.

**Topic:** 1

**Problem:** How well do LLM agents negotiate *with each other*, and does how they talk
change what they get?

**Method:** **NegotiationArena**, a framework for LLM-vs-LLM negotiation across three
scenario families: **allocating a shared resource (ultimatum games)**, aggregating
resources (trading games), and buy/sell price negotiations. Each scenario supports
multiple turns of free-form dialogue between the agents rather than single-shot offers.

**Results that matter:**
- **Rhetorical strategy has a large, measurable payoff.** "By pretending to be desolate
  and desperate, LLMs can improve their payoffs by **20%** when negotiating against the
  standard GPT-4."
- LLM agents' outcomes can be "significantly boosted" by behavioural tactics generally —
  i.e. the *framing* of a message, not just its informational content, drives the split.

**Limitations / criticisms:** Non-spatial and non-embodied, like [Abdelnabi-Negotiation].
The headline 20% is demonstrated against GPT-4 as the fixed opponent, so it measures an
exploit of one model rather than a general property of negotiation. Full per-scenario and
per-model breakdowns are `[unverified]` here (verified from the abstract and proceedings
record, not the results tables).

**Relevance to this FYP (4):** The ultimatum-game scenario is a two-party dispute over a
single indivisible resource — structurally the same problem as one hallway and two
agents. The important transfer is a **threat to validity**: if an agent can gain 20% by
performing desperation, then a hallway agent instructed to "explain why you need to pass"
may resolve the conflict by *rhetorical escalation* rather than by any humanlike
right-of-way norm. Any pattern this FYP extracts must therefore be checked against the
possibility that it is an artefact of persuasion dynamics between models. It also implies
the persona wording in a hallway prompt is load-bearing and should be varied as an
ablation, not fixed.

**BibTeX:** `pmlr-v235-bianchi24a` in [`refs.bib`](refs.bib).

---

### [Piatti-GovSim] — Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents

**Authors / Year / Venue:** Giorgio Piatti, Zhijing Jin, Max Kleiman-Weiner,
Bernhard Schölkopf, Mrinmaya Sachan, Rada Mihalcea / 2024 / *Advances in Neural
Information Processing Systems 37* (NeurIPS 2024). Preprint arXiv:2404.16698.

**Link:** arXiv:2404.16698 | https://arxiv.org/abs/2404.16698

**Verified:** yes — opened the arXiv abstract page (cached
`refs/piatti2024_govsim_abs.html`); NeurIPS 2024 stated in the arXiv comments field.
**Note a title change:** the early preprint is titled *"…Emergence of **Sustainability
Behaviors** in a Society of LLM Agents"* (this is the form cited by Wu et al.), while the
published version reads *"…Emergence of **Sustainable Cooperation**…"*. Cite the published
title.

**Topic:** 1

**Problem:** When LLM agents share a renewable common resource, can they restrain
themselves enough to keep it alive — the classic tragedy-of-the-commons conflict?

**Method:** **GovSim**, a generative simulation platform for strategic interaction and
cooperative decision-making. A society of LLM agents must balance exploiting a shared
resource against sustaining it for future rounds, with communication between agents.
Tested across leading open and closed LLMs, with an ablation on communication and a
variant using "universalization"-based moral reasoning.

**Results that matter:**
- **Most models fail:** "the highest survival rate below **54%**" — i.e. even the best
  LLM sustained the resource in fewer than 54% of runs.
- **Communication is the critical ingredient**: removing inter-agent communication
  sharply degrades sustainability.
- Agents prompted with **universalization** reasoning ("what if everyone did this?")
  achieve significantly better outcomes. The dominant failure mode is inability to reason
  about long-term consequences.

**Limitations / criticisms:** The conflict is temporal and N-party (present vs. future
consumption across a group), not a two-party spatial standoff, so the transfer is
structural rather than direct. Exact agent counts and per-model survival rates are
`[unverified]` here (verified from the abstract, not the results tables).

**Relevance to this FYP (3):** Lower relevance than the entries above, and included for
one specific reason: it is the clearest demonstration that **a single prompt-level
reasoning frame ("universalization") reliably changes the resolution outcome**. That is a
candidate *reusable pattern* of exactly the kind this project is hunting — not a rule
about who yields, but a reasoning schema that can be dropped into an agent cheaply. It
is also a useful corrective to [Mahadevan-GameChat]: with communication alone and no such
frame, LLM societies fail the majority of the time.

**BibTeX:** `piatti2024cooperate` in [`refs.bib`](refs.bib).

---

### [Chen-MAPF] — Why Solving Multi-agent Path Finding with Large Language Model has not Succeeded Yet

**Authors / Year / Venue:** Weizhe Chen, Sven Koenig, Bistra Dilkina / 2024 /
arXiv:2401.03630 `[non-archival]`. Verified as a preprint — Semantic Scholar lists the
venue as arXiv.org with no conference record (`refs/s2_topic_metadata.json`).

**Link:** arXiv:2401.03630 | https://arxiv.org/abs/2401.03630

**Verified:** yes — opened the arXiv abstract page (cached
`refs/chen2024_mapf_llm_abs.html`).

**Topic:** 1

**Problem:** Can LLMs solve multi-agent path finding (MAPF) — coordinating multiple
agents' routes so they don't collide — directly?

**Method:** LLMs are applied to standard MAPF benchmark maps of increasing difficulty:
an empty room with no obstacles, then the standard "room" and "maze" maps. The authors
then run further experiments to test hypotheses about *why* performance collapses, and
close with a position on what different research communities would need to contribute.

**Results that matter:**
- **Success on the empty map, failure on room and maze maps.** The motivating success
  disappears as soon as obstacles force genuine spatial coordination.
- The paper's position is that multi-agent planning is distinctively hard for LLMs
  because it combines coordination with planning and resists the external-tool
  scaffolding that rescues LLMs in other domains.
- No specific numerical success rates were confirmable from the abstract —
  `[unverified]`.

**Limitations / criticisms:** A position paper, not peer-reviewed, and by design it
reports a negative result rather than a method. Its LLM evaluations date from early 2024,
so the specific model failures may not hold for current models — though the structural
argument (coordination + planning + no tool scaffolding) is model-independent and
the authors include Sven Koenig, a principal authority on MAPF.

**Relevance to this FYP (4):** This is the paper that keeps the project's scope honest,
and it is the reason the supervisor's "start small" instruction is right rather than
merely cautious. It says plainly that LLMs **cannot** be handed the whole spatial
coordination problem. Read alongside [Mahadevan-GameChat], the two produce a clean and
defensible design principle for the FYP: *do not ask the LLM to plan paths; ask it only
to resolve the priority question, and let a conventional controller move the agents.*
That division of labour is precisely what CrowdGym's overridden `RL_take_action` conflict
handler already assumes (`integration/crowdgym_mapping.md` §B), so it also argues the
existing integration design is sound.

**BibTeX:** `chen2024why` in [`refs.bib`](refs.bib).

---

## What this topic adds up to

Three points survive from the seven entries, and they are consistent with each other:

1. **The reusable artefact is a priority ordering, not a trajectory.** GameChat's whole
   LLM contribution is one bit — who leads — handed to a cheap controller; Chen et al.
   show the LLM fails if asked for more than that; Wu et al.'s useful message content is
   likewise a short factual signal (which exit, how crowded). Every entry that works
   keeps the LLM's output small and symbolic.
2. **Extraction of a reusable pattern is an established, publishable move, and one team
   has already made it for crowds.** Zhang et al.'s DFD does LLM → interpretable rule
   code on evacuation scenarios; Ashery et al. show conventions emerge from LLM
   interaction at all.
3. **Whatever pattern emerges must be treated as suspect until validated against humans.**
   Ashery et al. show population-level bias arising from individually unbiased agents;
   Bianchi et al. show payoffs move 20% on rhetorical framing alone. Both are mechanisms
   by which a "pattern" could be an artefact of LLMs rather than a fact about people.

## What is actually left to do

Given [Zhang-DFD] exists, the defensible remaining contributions are narrower than the
roadmap currently implies, and worth putting to the supervisor explicitly:

- **Validation against real human behaviour.** DFD (as far as the abstract shows)
  distils LLM behaviour and compares against symbolic-regression baselines; it does not
  appear to check the distilled rule against human data. Roadmap step 5 is therefore
  still open — and Topic 2 shows the data to do it with **exists** (see the dataset flag
  at the top of [`topic2-sociological-grounding.md`](topic2-sociological-grounding.md)).
- **The two-agent conflict primitive specifically.** GameChat solves it with a
  *designer-supplied* priority hierarchy (hospital > airport > grocery). Nobody in this
  set derives the ordering from the agents' own exchange and then validates it as a
  humanlike right-of-way norm. That is a real gap and it is small enough for an FYP.
- **Integration with CrowdGym at 10,000 agents.** None of these papers targets that
  scale; Wu et al. stop at 100 agents and GameChat at two.

*Flagged as an assumption, not a design decision:* this reading of the gap is mine, from
the literature alone, and needs supervisor sign-off before the scenario design in
roadmap step 2 is built around it.
