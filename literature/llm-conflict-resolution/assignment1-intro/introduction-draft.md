# Sample introduction — Assignment 1 (draft)

> **Formatting note:** Intended for submission in Times New Roman, font size 12,
> double-spaced. This Markdown file will not render that way; apply it when moving the
> text into Word.
>
> **Before submission:** remove the `[needs verification against full text]` marker
> once the Zhang et al. [2] full text has been checked (see `open-gaps.md`, item G1).
> If the check fails, rewrite the marked sentence; do not just delete the marker.
>
> Prepared for issue [#10](https://github.com/M450NCH00/CrowdSimulation/issues/10).
> Paper choices and their evidence: [`paper-selection.md`](paper-selection.md).
> The sentence-by-sentence source map and checklist are below the reference list and
> are **not** part of the submission.

---

<!-- TITLE START -->
## Extracting Reusable Conflict-Resolution Patterns from LLM Agent Dialogue for Crowd Simulation
<!-- TITLE END -->

<!-- BODY START -->
### Background

In agent-based crowd simulation, each pedestrian is modelled as an autonomous agent; in
emergency evacuation, for example, evacuees all trying to leave quickly can congest the
exits [1], [2]. Local conflicts are harder still. When two agents approach a doorway
symmetrically, neither has a reason to give way: if both advance they collide, and if
both wait they deadlock [3]. In doorway tests, an existing collision-avoiding controller
deadlocked in all 18 scenarios [3].

Large language models (LLMs) offer another option. Because they can produce human-like
behaviour without hand-written rules, LLM agents are increasingly used in social and
agent-based simulation [1], [2]. Communication between them appears to help: GPT-4
evacuees that could message one another spread more evenly across three exits [1], and
two LLM agents discussing their tasks' urgency never deadlocked in a doorway, with the
more urgent agent going first in every scenario, compared with 50% without communication
[3].

### Research Gap

However, these benefits are paid for at every conflict. In GameChat, each encounter
needs a new LLM dialogue averaging 2.8 seconds, and success is judged against an urgency
ranking the designers fixed in advance [3]. Cost partly restricted Wu et al. to one
GPT-4 model; their 100-agent evacuation study alone cost $1,000 [1]. Zhang et al. tackle
this cost, which they note limits crowd size, by distilling LLM agents' decisions into
interpretable rule code, but they benchmark those rules against symbolic regression
rather than human behaviour [2] [needs verification against full text]. That check
matters: conventions that emerge among LLM agents can carry strong collective biases
even when no individual agent is biased [4]. None of the reviewed studies extracts a
reusable rule from LLM-to-LLM conflict dialogue and validates it against how people
resolve the same conflict. Without such a rule, each conflict still requires a fresh LLM
exchange.

### Introducing the Study

This project therefore investigates whether LLM agents can resolve spatial conflicts
through communication and, if so, whether their resolutions follow a reusable pattern.
It begins with the simplest case: two agents meeting head-on in a narrow hallway, a
symmetric standoff that dialogue has been shown to break [3]. Repeated exchanges will be
analysed for a recurring rule, such as who gives way and why.

Two findings suggest this is feasible. LLM agent populations settle on shared
conventions without explicit programming [4], and human conflict resolution is itself
patterned: in a face-to-face game where each partner preferred a different option, 10 of
19 pairs took turns, five settled on a fixed choice favouring one partner, and four
failed to coordinate [5]. Extracted patterns will be validated against such sociological
evidence, treating the human benchmark as a mix of strategies rather than a single rule.

Finally, a validated pattern will be integrated into CrowdGym, the simulation
environment this project builds on. If a reusable pattern exists, conflicts among 10,000
agents could be resolved with a lightweight rule instead of per-encounter LLM calls,
avoiding the inference cost that limits LLM-driven crowds [2].<!-- BODY END -->

---

### References

[1] Z. Wu *et al.*, "Shall we team up: Exploring spontaneous cooperation of competing
LLM agents," in *Findings Assoc. Comput. Linguistics: EMNLP 2024*, Miami, FL, USA,
2024, pp. 5163–5186, doi: 10.18653/v1/2024.findings-emnlp.297.

[2] Y. Zhang, P. Andelfinger, W. J. Tan, and W. Cai, "Sense, think, act, reflect:
Distilling fast and interpretable decision functions from LLM-driven crowds," *ACM
Trans. Model. Comput. Simul.*, 2026, doi: 10.1145/3818686.

[3] V. Mahadevan, S. Zhang, and R. Chandra, "GameChat: Multi-LLM dialogue for safe,
agile, and socially optimal multi-agent navigation in constrained environments," in
*Proc. IEEE Int. Symp. Multi-Robot Multi-Agent Syst. (MRS)*, 2025. [Online]. Available:
https://arxiv.org/abs/2503.12333

[4] A. F. Ashery, L. M. Aiello, and A. Baronchelli, "Emergent social conventions and
collective bias in LLM populations," *Sci. Adv.*, vol. 11, no. 20, Art. no. eadu9368,
2025, doi: 10.1126/sciadv.adu9368.

[5] S. Moeller, A. M. Unakafov, J. Fischer, A. Gail, S. Treue, and I. Kagan, "Human and
macaque pairs employ different coordination strategies in a transparent decision game,"
*eLife*, vol. 12, Art. no. e81641, 2023, doi: 10.7554/eLife.81641.

---
---

## Not for submission — source map

Every factual sentence in the body, mapped to what the cited paper actually says. "Own"
marks sentences that are this project's aims, scope or reasoning, not claims about the
literature.

| # | Sentence (abridged) | Cite | Where in the source | Level checked |
|---|---|---|---|---|
| B1 | Agent-based crowd sim models pedestrians as agents; evacuation, evacuees rushing to leave, congestion | [1], [2] | [1] §6.1 ("all agents are willing to escape as quickly as possible, often leading to congestion"); [2] abstract ("agent-based crowd evacuation scenarios") | full text / abstract |
| B2 | Symmetric doorway: neither has a reason to yield; both go = collide, both wait = deadlock | [3] | §I, Fig. 1 caption | full text (arXiv v2) |
| B3 | Existing controller (MPC-CBF) deadlocked in all 18 doorway scenarios | [3] | Table III, MPC-CBF row, "# DLs" = 18 | full text (arXiv v2) |
| B4 | LLMs produce human-like behaviour; increasingly used in social / agent-based simulation | [1], [2] | [1] §1 (trending topic; more flexible than rule-based agent modelling); [2] abstract ("human-like agent behavior … useful building blocks for agent-based simulations") | full text / abstract |
| B5 | Communicating GPT-4 evacuees spread more evenly across three exits | [1] | §6.2 "Effect of Communication on Exit Choices", Fig. 9 | full text |
| B6 | LLM dialogue: no deadlocks; more urgent agent first 100% vs 50% | [3] | Table III (0 DLs; % CP 100 vs 50); abstract | full text (arXiv v2) |
| G1 | Each encounter needs a new dialogue, 2.8 s on average | [3] | §IV-C (dialogue starts when agents observe each other); §V-B.2 (mean 2.767 s, SD 0.441 s) | full text (arXiv v2) |
| G2 | Success judged against an urgency ranking fixed in advance by the designers | [3] | §IV-C ("in decreasing order of priority … hospital, airport, grocery"); §V-B.2 ("correct consensus"). The prompt does **not** give the LLM this ranking; the LLM infers urgency from task text (Table II) | full text (arXiv v2) |
| G3 | One GPT-4 model partly due to cost; evacuation study cost $1,000 | [1] | Limitations, "Limited Experimentation on LLMs" ({$900, $3000, $1000}, third = EE) | full text |
| G4 | Cost limits crowd size; DFD distils decisions into interpretable rule code | [2] | abstract | **abstract only** |
| G5 | Rules benchmarked against symbolic regression "rather than human behaviour" | [2] | abstract states the SR comparison; the "rather than human behaviour" half is inferred from the abstract **not** mentioning human validation | **abstract only — carries `[needs verification against full text]` in the draft** |
| G6 | Emergent conventions carry collective bias without individual bias | [4] | abstract | abstract only |
| G7 | No reviewed study both extracts from LLM-to-LLM conflict dialogue and validates against humans | — | Limited to the 14 papers in the issue #8 review; follows from G1–G6 | Own synthesis — see `open-gaps.md` G5 |
| G8 | Without a rule, a new exchange for every conflict | — | Follows from G1 | Own reasoning |
| S1 | Aim; start with 2-agent hallway; analyse for a recurring rule | [3] for "symmetric standoff dialogue can break" | [3] Table III / §V-B | Own scope + full text |
| S2 | LLM populations settle on conventions without programming | [4] | abstract | abstract only |
| S3 | 10/19 turn-taking, 5 fixed favouring one, 4 failed | [5] | Results, "Human pairs mainly converge on fair coordination", Fig. 2A | full article |
| S4 | Treat human result as a mix of strategies | [5] | Follows from S3 | Own reasoning |
| S5 | Integrate into CrowdGym; 10,000 agents with a rule instead of per-encounter LLM calls | [2] for inference cost limiting crowd size | [2] abstract | Own scope (CrowdGym uncited — `open-gaps.md` G4) |

## Not for submission — quality checklist (from the issue)

- [x] **Title is informative, not too general or too specific, ≤12 words** — 11 words
  (hyphenated "Conflict-Resolution" counted as one; 12 if split).
- [x] **Background introduces the topic, narrows to specific issues, reviews literature**
  — crowd simulation → pairwise deadlock → LLM agents and communication; cites [1]–[3].
  *Caveat:* "why crowd simulation matters" is carried only by the evacuation example
  (see `open-gaps.md` G2).
- [x] **Research gap defines the problem and the need for further research** — cost per
  conflict, success judged against a designer-fixed ranking, and existing distillation not checked against
  humans; bias risk [4] shows why that check is needed.
- [x] **Objective of the study is described** — first sentence of "Introducing the
  Study".
- [x] **Scope outlines the parameters of the project** — 2-agent hallway → pattern
  analysis → validation against sociological evidence → CrowdGym integration.
- [x] **Paragraphs connected with transitional devices** — "Large language models …
  offer another option", "However", "That check matters:", "therefore", "Two
  findings suggest this is feasible", "Finally".
- [x] **In-text citations IEEE, consistent, all in reference list** — [1]–[5], numbered
  by first appearance; checked mechanically (see work log).
- [x] **Reference list IEEE, consistent, only cited works** — 5 entries, all cited.
  *Caveat:* [2] has no volume/issue yet and [3] has no page numbers or IEEE DOI
  (`open-gaps.md` G3).
- [x] **Word count ≤500 (excluding title and reference list)** — **494 words** counting
  headings, citation numbers and the verification marker (489 without the marker);
  counted by script, see `WORK_LOG-10.md`.
- [x] **No claim is unsourced** — see the source map above. Rows G7, G8 and S4 are the
  author's own reasoning from cited findings, and S1/S5 are the project's own scope;
  none of them states a new fact about the literature.
