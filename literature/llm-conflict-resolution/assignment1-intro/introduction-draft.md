# Sample introduction — Assignment 1 (draft)

> **Formatting note:** Intended for submission in Times New Roman, font size 12,
> double-spaced. This Markdown file will not render that way; apply it when moving the
> text into Word.
>
> **Zhang et al. [2] verified against full text (2026-09-13).** The earlier
> `[needs verification against full text]` marker has been resolved and removed; see
> `open-gaps.md` G1.
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

In agent-based crowd simulation, each pedestrian is modelled as an autonomous agent;
during evacuation, evacuees all trying to leave quickly can congest the exits [1], [2].
Such simulations inform emergency planning and building design [2]. Local conflicts are
harder still. When two agents approach a doorway symmetrically, neither has a reason to
give way: if both advance they collide, and if both wait they deadlock [3]. In doorway
tests, an existing collision-avoiding controller deadlocked in all 18 scenarios [3].

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
ranking the designers fixed in advance [3]. Zhang et al. tackle inference cost by
distilling LLM agents' exit decisions into interpretable rule code; one LLM-driven
evacuation run took about a day, against about a minute for the distilled rules [2]. Yet
these rules are judged against the LLM-generated behaviour, not human data, so their
validity depends directly on that reference [2]. This matters because conventions
emerging among LLM agents can carry strong collective biases even when no individual
agent is biased [4]. None of the reviewed studies extracts a reusable rule from
LLM-to-LLM conflict dialogue and validates it against how people resolve the same
conflict. Without such a rule, each conflict still requires a fresh LLM exchange.

### Introducing the Study

This project therefore investigates whether LLM agents can resolve spatial conflicts
through communication, whether their resolutions follow a reusable pattern, and whether
that pattern matches how people resolve the same conflicts. It begins with the simplest
case: two agents meeting head-on in a narrow hallway, a symmetric standoff that dialogue
has been shown to break [3]. Repeated exchanges will be analysed for a recurring rule,
such as a right-of-way ordering [3] or turn-taking [5].

Two findings suggest this is feasible. LLM agent populations settle on shared
conventions without explicit programming [4], and human conflict resolution is itself
patterned: in a face-to-face game where each partner preferred a different option, 10 of
19 pairs took turns, five settled on a fixed choice favouring one partner, and four
failed to coordinate [5]. A humanlike pattern should reproduce this mix of strategies,
not a single rule.

Finally, a validated pattern will be integrated into CrowdGym, the simulation
environment this project builds on. If a reusable pattern exists, conflicts among 10,000
agents could be resolved with a lightweight rule instead of per-encounter LLM calls,
avoiding the inference cost that limits LLM-driven crowds [2].
<!-- BODY END -->

---

### References

[1] Z. Wu *et al.*, "Shall we team up: Exploring spontaneous cooperation of competing
LLM agents," in *Findings Assoc. Comput. Linguistics: EMNLP 2024*, Miami, FL, USA,
2024, pp. 5163–5186, doi: 10.18653/v1/2024.findings-emnlp.297.

[2] Y. Zhang, P. Andelfinger, W. J. Tan, and W. Cai, "Sense, think, act, reflect:
Distilling fast and interpretable decision functions from LLM-driven crowds," *ACM
Trans. Model. Comput. Simul.*, to be published, doi: 10.1145/3818686.

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
literature. Zhang et al. [2] page/section numbers refer to the "Just Accepted" TOMACS
version cached at `refs/zhang2026_dfd.pdf`.

| # | Sentence (abridged) | Cite | Where in the source | Level checked |
|---|---|---|---|---|
| B1 | Agent-based crowd sim models pedestrians as agents; evacuees rushing to leave congest exits | [1], [2] | [1] §6.1 ("all agents are willing to escape as quickly as possible, often leading to congestion"); [2] §1 (ABM "simulates human behavior … according to specified agent attributes, behaviors, and mechanisms") | full text / full text |
| B2 | Such simulations inform emergency planning and building design | [2] | §1, first sentence ("essential for emergency planning and building design, e.g., for appropriate placement of emergency exits") | full text |
| B3 | Symmetric doorway: neither has a reason to yield; both go = collide, both wait = deadlock | [3] | §I, Fig. 1 caption | full text (arXiv v2) |
| B4 | Existing controller (MPC-CBF) deadlocked in all 18 doorway scenarios | [3] | Table III, MPC-CBF row, "# DLs" = 18 | full text (arXiv v2) |
| B5 | LLMs produce human-like behaviour; increasingly used in social / agent-based simulation | [1], [2] | [1] §1 (trending topic; more flexible than rule-based agent modelling); [2] §1 ("Increasingly, LLMs play the role of agents in simulated environments") and abstract | full text / full text |
| B6 | Communicating GPT-4 evacuees spread more evenly across three exits | [1] | §6.2 "Effect of Communication on Exit Choices", Fig. 9 | full text |
| B7 | LLM dialogue: no deadlocks; more urgent agent first 100% vs 50% | [3] | Table III (0 DLs; % CP 100 vs 50); abstract | full text (arXiv v2) |
| G1 | Each encounter needs a new dialogue, 2.8 s on average | [3] | §IV-C (dialogue starts when agents observe each other); §V-B.2 (mean 2.767 s, SD 0.441 s) | full text (arXiv v2) |
| G2 | Success judged against an urgency ranking fixed in advance by the designers | [3] | §IV-C ("in decreasing order of priority … hospital, airport, grocery"); §V-B.2 ("correct consensus"). The prompt does **not** give the LLM this ranking; the LLM infers urgency from task text (Table II) | full text (arXiv v2) |
| G3 | DFD distils LLM agents' exit decisions into interpretable rule code | [2] | §1 contributions; §3 (decision function maps perception/agent state to exit scores); §4.4 | full text |
| G4 | One LLM-driven run ≈ 1 day vs ≈ 1 minute with the distilled rules | [2] | §5.5 (t_sim,LLM ≈ 1d, t_sim,DF ≈ 1m; 100 agents, 51 steps per §5.1; ground truth from locally deployed Gemma3:27b, App. A) | full text |
| G5 | Rules judged against LLM-generated behaviour, not human data; validity depends directly on the reference | [2] | §5.1 (all three datasets generated by the LLM-driven simulation; fidelity metrics vs that ground truth); §6.1 ("agnostic of the realism of the ground truth trajectories, the validity of the distilled function depends directly on the reference data"); §6.2 (real-world observations named only as an alternative) | full text |
| G6 | Emergent conventions carry collective bias without individual bias | [4] | abstract | abstract only |
| G7 | No reviewed study both extracts a rule from LLM-to-LLM conflict dialogue and validates against humans | — | Limited to the 14 papers in the issue #8 review; follows from G1–G6. Nuance: DFD's ground truth *does* include inter-agent conversation ([2] §4.2), but its decisions are exit choices, its final functions use only numerical perception features (§3, Fig. 14), interaction features are future work (§7), and it is not human-validated (G5) | Own synthesis — see `open-gaps.md` G5 |
| G8 | Without a rule, a new exchange for every conflict | — | Follows from G1 | Own reasoning |
| S1 | Aim (communication → reusable pattern → match to how people resolve the same conflicts); start with 2-agent hallway | [3] for "symmetric standoff dialogue can break" | [3] Table III / §V-B | Own aim/scope + full text |
| S1b | Example rule forms: right-of-way ordering, turn-taking | [3], [5] | [3] §IV-C (consensus sets leader/follower by priority); [5] Results, Fig. 2A (10 of 19 pairs took turns) | full text / full article |
| S2 | LLM populations settle on conventions without programming | [4] | abstract | abstract only |
| S3 | 10/19 turn-taking, 5 fixed favouring one, 4 failed | [5] | Results, "Human pairs mainly converge on fair coordination", Fig. 2A | full article |
| S4 | A humanlike pattern should reproduce this mix of strategies, not a single rule | [5] | Follows from S3 (human pairs split across turn-taking, fixed choice, failure) | Own reasoning |
| S5 | Integrate into CrowdGym; 10,000 agents with a rule instead of per-encounter LLM calls | [2] for inference cost limiting crowd size | [2] §1, p. 2 ("limits the scalability beyond relatively modest numbers of individuals"). The 10,000 figure is this project's target, not from [2] | Own scope (CrowdGym uncited — `open-gaps.md` G4) |

## Not for submission — quality checklist (from the issue)

- [x] **Title is informative, not too general or too specific, ≤12 words** — 11 words
  (hyphenated "Conflict-Resolution" counted as one; 12 if split).
- [x] **Background introduces the topic, narrows to specific issues, reviews literature**
  — crowd simulation and why it matters [1], [2] → pairwise deadlock [3] → LLM agents and
  communication [1]–[3].
- [x] **Research gap defines the problem and the need for further research** — cost per
  conflict [3], success judged against a designer-fixed ranking [3], existing
  distillation judged only against LLM behaviour [2], bias risk [4] showing why human
  validation is needed.
- [x] **Objective of the study is described** — first sentence of "Introducing the
  Study": three linked questions (resolve by communication; reusable pattern; matches how
  people resolve the same conflicts).
- [x] **Scope outlines the parameters of the project** — 2-agent hallway → pattern
  analysis (right-of-way ordering or turn-taking as example forms) → comparison with the
  human mix of strategies [5] → CrowdGym integration.
- [x] **Paragraphs connected with transitional devices** — "Large language models …
  offer another option", "However", "Yet", "This matters because", "therefore", "Two
  findings suggest this is feasible", "Finally".
- [x] **In-text citations IEEE, consistent, all in reference list** — [1]–[5], numbered
  by first appearance; checked mechanically (see work log).
- [x] **Reference list IEEE, consistent, only cited works** — 5 entries, all cited.
  *Caveat:* [2] is an accepted article with no volume/issue/article number yet ("to be
  published"), and [3] has no page numbers or IEEE DOI (`open-gaps.md` G3).
- [x] **Word count ≤500 (excluding title and reference list)** — **496 words** counting
  headings and citation numbers; counted by script, see `WORK_LOG-10.md`.
- [x] **No claim is unsourced** — see the source map above. Rows G7, G8 and S4 are the
  author's own reasoning from cited findings, and S1/S5 are the project's own scope;
  none of them states a new fact about the literature.
