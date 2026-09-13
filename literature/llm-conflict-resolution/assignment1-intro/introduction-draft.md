# Sample introduction — Assignment 1 (draft)

> **Formatting note:** Intended for submission in Times New Roman, font size 12,
> double-spaced. This Markdown file will not render that way; apply it when moving the
> text into Word.
>
> **Zhang et al. [1] verified against full text (2026-09-13).** The earlier
> `[needs verification against full text]` marker has been resolved and removed; see
> `open-gaps.md` G1.
>
> **Structure:** written as continuous prose, separated by paragraphs only, with no
> section headings, to match the Word submission. Paragraphs 1–3 are the background,
> paragraph 4 the research gap, and paragraphs 5–7 introduce the study.
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
Understanding how people will move through a building during an emergency underpins
evacuation planning and building design, such as where to place exits [1]. Agent-based
crowd simulation supports this by modelling each person as an autonomous agent whose
decisions, such as which exit to take, together shape the crowd's movement [1], [2].

These decisions can conflict. Evacuees all hurrying to leave can congest the exits [2],
and even two agents approaching a doorway symmetrically can become stuck: neither has a
reason to give way, so if both advance they collide, and if both wait they deadlock [3].
In doorway tests, an existing collision-avoiding controller deadlocked in all 18
scenarios [3].

Large language models (LLMs) offer another way to model such decisions. Able to produce
human-like behaviour without hand-written rules, LLM agents are increasingly used in
social and agent-based simulation [1], [2]. Communication appears to help: evacuees that
could message one another spread more evenly across exits [2], and two LLM agents
discussing their tasks' urgency never deadlocked in a doorway, with the more urgent
agent going first in every scenario, versus 50% without communication [3].

However, these benefits are paid for at every conflict. In that doorway study, each
encounter needed a new LLM dialogue averaging 2.8 seconds, and success was judged
against an urgency ranking the designers fixed in advance [3]. Zhang et al. tackle
inference cost by distilling LLM agents' exit decisions into interpretable rule code,
cutting an evacuation run from about a day to about a minute [1]. Yet these rules are
judged against the LLM-generated behaviour, not human data, so their validity depends
directly on that reference [1]. This matters because conventions emerging among LLM
agents can carry strong collective biases even when no individual agent is biased [4].
No reviewed study extracts a reusable rule from LLM-to-LLM conflict dialogue and
validates it against human conflict resolution. Without such a rule, each conflict still
requires a fresh LLM exchange.

This project therefore investigates whether LLM agents can resolve spatial conflicts
through communication, whether their resolutions follow a reusable pattern, and whether
that pattern matches how people resolve the same conflicts. It begins with the simplest
case, two agents meeting head-on in a narrow hallway. Repeated exchanges will be
analysed for a recurring rule, such as a right-of-way ordering [3] or turn-taking [5].

Two findings suggest this is feasible. LLM agent populations settle on shared
conventions without explicit programming [4], and human conflict resolution is itself
patterned: in a game where partners preferred different options, 10 of 19 pairs took
turns, five settled on a fixed choice favouring one partner, and four failed to
coordinate [5]. A humanlike pattern should reproduce this mix of strategies, not a
single rule.

Finally, a validated pattern will be integrated into CrowdGym, the simulator this
project builds on. If such a pattern exists, conflicts among 10,000 agents could be
resolved with a lightweight rule instead of per-encounter LLM calls, avoiding the
inference cost that limits LLM-driven crowds [1].
<!-- BODY END -->

---

### References

[1] Y. Zhang, P. Andelfinger, W. J. Tan, and W. Cai, "Sense, think, act, reflect:
Distilling fast and interpretable decision functions from LLM-driven crowds," *ACM
Trans. Model. Comput. Simul.*, to be published, doi: 10.1145/3818686.

[2] Z. Wu *et al.*, "Shall we team up: Exploring spontaneous cooperation of competing
LLM agents," in *Findings Assoc. Comput. Linguistics: EMNLP 2024*, Miami, FL, USA,
2024, pp. 5163–5186, doi: 10.18653/v1/2024.findings-emnlp.297.

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
literature. P = paragraph number. Zhang et al. [1] page/section numbers refer to the
"Just Accepted" TOMACS version cached at `refs/zhang2026_dfd.pdf`.

| # | Sentence (abridged) | Cite | Where in the source | Level checked |
|---|---|---|---|---|
| P1a | Understanding how people move in an emergency underpins evacuation planning and building design, e.g. exit placement | [1] | §1, first sentence ("essential for emergency planning and building design, e.g., for appropriate placement of emergency exits"); paraphrased | full text |
| P1b | Agent-based crowd simulation models each person as an autonomous agent whose decisions (e.g. exit choice) together shape crowd movement | [1], [2] | [1] §1 (ABM captures "individual behaviors and interactions"); §2.2 ("outcomes of agent-based simulations emerge from applying behavioral rules and interactions at the level of individuals"); §3 (agents choose target exits). [2] §6.1 (evacuees choose a target exit each round) | full text / full text |
| P2a | Evacuees all hurrying to leave can congest exits | [2] | §6.1 ("all agents are willing to escape as quickly as possible, often leading to congestion") | full text |
| P2b | Two agents approaching a doorway symmetrically: neither has a reason to yield; both go = collide, both wait = deadlock | [3] | §I, Fig. 1 caption | full text (arXiv v2) |
| P2c | Existing controller (MPC-CBF) deadlocked in all 18 doorway scenarios | [3] | Table III, MPC-CBF row, "# DLs" = 18 | full text (arXiv v2) |
| P3a | LLMs produce human-like behaviour without hand-written rules; increasingly used in social / agent-based simulation | [1], [2] | [1] abstract and §1 ("Increasingly, LLMs play the role of agents in simulated environments"; hand-defined agent behaviours are "difficult to generalize"); [2] §1 (trending topic; more flexible than rule-based agent modelling) | full text / full text |
| P3b | Communicating evacuees spread more evenly across exits | [2] | §6.2 "Effect of Communication on Exit Choices", Fig. 9 | full text |
| P3c | LLM dialogue on task urgency: no deadlocks; more urgent agent first 100% vs 50% | [3] | Table III (0 DLs; % CP 100 vs 50); abstract | full text (arXiv v2) |
| P4a | In that doorway study, each encounter needed a new dialogue, 2.8 s on average | [3] | §IV-C (dialogue starts when agents observe each other); §V-B.2 (mean 2.767 s, SD 0.441 s) | full text (arXiv v2) |
| P4b | Success judged against an urgency ranking fixed in advance by the designers | [3] | §IV-C ("in decreasing order of priority … hospital, airport, grocery"); §V-B.2 ("correct consensus"). The prompt does **not** give the LLM this ranking; the LLM infers urgency from task text (Table II) | full text (arXiv v2) |
| P4c | DFD distils LLM agents' exit decisions into interpretable rule code; run time ≈ 1 day → ≈ 1 minute | [1] | §1 contributions; §3–4; §5.5 (t_sim,LLM ≈ 1d, t_sim,DF ≈ 1m; 100 agents, 51 steps per §5.1) | full text |
| P4d | Rules judged against LLM-generated behaviour, not human data; validity depends directly on that reference | [1] | §5.1 (all datasets generated by the LLM-driven simulation); §6.1 ("the validity of the distilled function depends directly on the reference data"); §6.2 (real-world observations only as an alternative) | full text |
| P4e | Emergent conventions carry collective bias without individual bias | [4] | abstract | abstract only |
| P4f | No reviewed study both extracts a rule from LLM-to-LLM conflict dialogue and validates it against human conflict resolution | — | Limited to the 14 papers in the issue #8 review; follows from P4a–P4e. Nuance: DFD's ground truth *does* include inter-agent conversation ([1] §4.2), but its decisions are exit choices, its final functions use only numerical perception features (§3, Fig. 14), interaction features are future work (§7), and it is not human-validated (P4d) | Own synthesis — see `open-gaps.md` G5 |
| P4g | Without a rule, a new exchange for every conflict | — | Follows from P4a | Own reasoning |
| P5a | Aim (communication → reusable pattern → match to how people resolve the same conflicts); start with 2-agent hallway | — | — | Own aim / scope |
| P5b | Example rule forms: right-of-way ordering, turn-taking | [3], [5] | [3] §IV-C (consensus sets leader/follower by priority); [5] Results, Fig. 2A (10 of 19 pairs took turns) | full text / full article |
| P6a | LLM populations settle on conventions without programming | [4] | abstract | abstract only |
| P6b | 10/19 turn-taking, 5 fixed favouring one, 4 failed | [5] | Results, "Human pairs mainly converge on fair coordination", Fig. 2A | full article |
| P6c | A humanlike pattern should reproduce this mix of strategies, not a single rule | — | Follows from P6b | Own reasoning |
| P7 | Integrate into CrowdGym; 10,000 agents with a rule instead of per-encounter LLM calls | [1] for inference cost limiting crowd size | [1] §1, p. 2 ("limits the scalability beyond relatively modest numbers of individuals"). The 10,000 figure is this project's target, not from [1] | Own scope (CrowdGym uncited — `open-gaps.md` G4) |

## Not for submission — quality checklist (from the issue)

- [x] **Title is informative, not too general or too specific, ≤12 words** — 11 words
  (hyphenated "Conflict-Resolution" counted as one; 12 if split).
- [x] **Background introduces the topic, narrows to specific issues, reviews literature**
  — P1 opens broadly (why people's movement in an emergency matters, and how crowd
  simulation models it) [1], [2] → P2 narrows to decisions that conflict, down to a
  two-agent deadlock [2], [3] → P3 covers LLM agents and communication [1]–[3].
- [x] **Research gap defines the problem and the need for further research** — P4: cost
  per conflict and a designer-fixed ranking [3], existing distillation judged only
  against LLM behaviour [1], bias risk [4] showing why human validation is needed.
- [x] **Objective of the study is described** — P5, first sentence: three linked
  questions (resolve by communication; reusable pattern; matches how people resolve the
  same conflicts).
- [x] **Scope outlines the parameters of the project** — P5–P7: 2-agent hallway →
  pattern analysis (right-of-way ordering or turn-taking as example forms) → comparison
  with the human mix of strategies [5] → CrowdGym integration.
- [x] **Paragraphs connected with transitional devices** — there are no headings, so
  each paragraph opens with a link to the one before: "These decisions can conflict",
  "Large language models … offer another way to model such decisions", "However, these
  benefits are paid for at every conflict", "This project therefore investigates", "Two
  findings suggest this is feasible", "Finally".
- [x] **In-text citations IEEE, consistent, all in reference list** — [1]–[5], numbered
  by first appearance. **Renumbered in revision 4:** the new opening cites Zhang et al.
  first, so Zhang is now [1] and Wu et al. [2]. Checked mechanically.
- [x] **Reference list IEEE, consistent, only cited works** — 5 entries, all cited.
  *Caveat:* [1] is an accepted article with no volume/issue/article number yet ("to be
  published"), and [3] has no page numbers or IEEE DOI (`open-gaps.md` G3).
- [x] **Word count ≤500 (excluding title and reference list)** — **497 words**, no
  headings; counted by script, see `WORK_LOG-10.md`.
- [x] **No claim is unsourced** — see the source map above. Rows P4f, P4g and P6c are
  the author's own reasoning from cited findings, and P5a/P7 are the project's own aim
  and scope; none of them states a new fact about the literature.
