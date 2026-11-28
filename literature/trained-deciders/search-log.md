# Search log: issue #38

> For issue [#38](https://github.com/M450NCH00/CrowdSimulation/issues/38), PT-4 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). All work done on 2026-10-18 in one
> session. Records what was read first, how sources were confirmed and fetched, every search and its
> outcome, the unread leads, and what went wrong.

Companion files: [entries](entries.md) · [options](options.md) · [evaluation](evaluation.md) ·
[verdict](verdict.md) · [missing papers](missing-papers.md) · [BibTeX](refs-trained-deciders.bib)

---

## §1. What was read first

As the issue asks, and only these: issue #34, "The idea"; `literature/paper-summaries/02-sense-think-act-reflect.md`
([Zhang-DFD]); the [Fang-Etiquette] entry in `literature/llm-behavioural-conflict/llm-behavioural-conflict.md`;
`literature/simulation-rules/research-gap.md` §6. The issue also points to the [Yang-S2AN] entry in
`s3-mapf-robotics.md`, which I read for the cross-reference.

For conventions only (no content used as evidence): #37's `missing-papers.md` and `search-log.md`,
its work log's assumptions and open questions, and the `.gitignore` notes on cached sources.

Later, to answer Q5, two repository files were checked for facts about this FYP (not literature):
`README.md` (the issue #16 finding that demographic effects reverse between models) and
`llm_negotiation/docs/log-schema.md` (what `outcomes.jsonl` records).

## §2. How sources were confirmed and fetched

- **Confirmation.** arXiv API (`export.arxiv.org/api/query?id_list=...`) for title, authors, date,
  journal reference and comments; then the published version on the Crossref API
  (`api.crossref.org/works?query.bibliographic=...`, and `/works/<doi>`), on the NeurIPS proceedings
  pages (VIPER, Counterfactual Fairness), on PMLR (reward machines, ICML 2018) and on the ACL
  Anthology (Plaza-del-Arco et al., via its BibTeX export). The page title was checked against the
  paper's title in each case.
- **DBLP**: its search API returned non-JSON responses for every query, so it was not used.
- **Fetching.** All 13 full texts are arXiv copies, downloaded from `arxiv.org/pdf/<id>` to
  `refs/td_*.pdf` and extracted with `pdftotext -enc UTF-8` to `refs/td_*.txt`. A first pass with
  `-layout` interleaved the two columns of most copies, so all were re-extracted in reading order
  (no `-layout`). The extracts were searched with `grep`, and only the passages needed were read
  into the conversation.
- **What is committed.** All `refs/td_*` files are arXiv copies, which this repository's convention
  (#35 to #37) allows committing. None is a publisher copy.

## §3. Seed leads: status

| Lead (as given in the issue) | Status |
|---|---|
| Zhang et al. 2026, *ACM TOMACS* | Cross-referenced from its existing summary; not re-read |
| Fang et al. 2026, *IEEE RA-L*, arXiv:2602.09002 | Cross-referenced from its existing entry; not re-read |
| Amano & Yamaguchi 2026, arXiv:2608.19778 | **Confirmed** (arXiv; accepted at SIGSPATIAL 2026). Full entry |
| Icarte et al., reward machines, ICML 2018 and *JAIR* 2022 `[unverified lead]` | **Confirmed**: ICML 2018 (PMLR 80:2107–2116) and *JAIR* 73:173–208 (2022). *JAIR* read; ICML confirmed only |
| Alshiekh et al. 2018, "Safe Reinforcement Learning via Shielding", AAAI `[unverified lead]` | **Confirmed** (AAAI 32(1), doi:10.1609/aaai.v32i1.11797). Full entry |
| Kusner et al. 2017, "Counterfactual Fairness", NeurIPS `[unverified lead]` | **Confirmed** (NeurIPS 2017 proceedings page). Full entry |
| Rudin 2019, *Nature Machine Intelligence* `[unverified lead]` | **Confirmed** (1:206–215, doi:10.1038/s42256-019-0048-x). Full entry |
| Yang-S2AN (cross-reference only) | Cross-referenced from its S3 entry |
| PySR and LLM-SR (Zhang's baselines) | **Not read**; listed in §5 |

## §4. Searches

| # | Query (web search, standard) | Purpose | Outcome |
|---|---|---|---|
| S1 | distilling LLM agent decisions into small model agent-based simulation scalability fidelity out-of-distribution | Q1 | Found GenWorld (arXiv:2606.27650) → **entry [Li-GenWorld]**; Chopra et al. (AAMAS 2025) → **entry [Chopra-Archetypes]**; Taillandier et al. (arXiv:2507.19364) and the Gao et al. survey (arXiv:2312.11970) → leads, not read. No result measured out-of-distribution behaviour of a distilled agent model |
| S2 | LLM-generated labels train decision tree policy distillation autonomous driving or traffic agents interpretable surrogate of LLM | Q1/Q2: an LLM-to-tree distillation | No LLM-to-tree source found. RAPID (arXiv:2410.12568, LLM → RL policy for driving) and an on-policy LM distillation (arXiv:2604.07944) → leads, not read |
| S3 | multiple LLMs disagree annotators ensemble of LLM teachers label aggregation simulation of human behaviour "silicon samples" model differences | Q5: several LLM teachers | Found Plaza-del-Arco et al. (arXiv:2307.12973; LREC-COLING 2024 workshop) → **entry [Plaza-ModelCrowds]**. Four further leads (arXiv:2309.05619; ACL 2026 long 752; GEM 2026 main 21; arXiv:2411.12147) not read |

The other entries ([Bastani-VIPER], [Hu-LogicRules], [Garg-CFText], [Tamkin-Discrim],
[Chen-SACADRL]) were chosen by me as known candidates for Q2–Q5 (named from memory) and then
confirmed on their own pages (§2); no web search was needed to find them. That is a source of
selection bias: the set leans to well-cited work I already knew of.

## §5. Unread leads (for a later session)

Confirmed to exist (arXiv record fetched in this session), not read:
- Taillandier et al. 2025, "From the Fluency Fallacy to the Micro-to-Macro Validity Gap",
  arXiv:2507.19364 `[preprint]`. Relevant to option L (small language models in social simulation).
- Wu et al. 2024, "Robust RL with LLM-Driven Data Synthesis and Policy Adaptation for Autonomous
  Driving" (RAPID), arXiv:2410.12568 `[preprint]`. Relevant to Q1 and option P (LLM-generated
  training data for a driving policy, per its title).

Named in search results or references, **not confirmed**:
- PySR (Cranmer, 2023) and LLM-SR (Shojaee et al., 2025) — Zhang's baselines; Q2.
- CORELS (Angelino et al.), the rule-list learner in [Rudin-StopExplaining] Fig. 3; Q2.
- Programmatically interpretable RL (Verma et al. 2018, arXiv:1804.02477), cited in
  [Bastani-VIPER]; Q2.
- Constrained policy optimisation and normative supervisors (norm-aware RL); Q3. No source was
  searched for specifically; the issue's "norm-aware or constrained reinforcement learning" is
  covered here only by [Chen-SACADRL].
- LLM-ensemble annotation papers from S3 (four, listed above); Q5.
- Gradient boosting as a decider: no source looked for (option N rests on Rudin only).

## §6. What went wrong, and limits of the search

- DBLP unavailable (§2).
- Three web searches only; most entries came from leads I knew, so the review is likely to miss
  recent or less-cited work, especially on Q1 (LLM → fast decider in crowds) and Q3
  (between-simulator transfer of rule-guided policies).
- Two entries are by authors with a stake: [Tamkin-Discrim] (Anthropic authors, Anthropic model;
  this review was written with an Anthropic model) — noted in the entry.
- Section numbers for [Alshiekh-Shielding] are those of the arXiv long version.
