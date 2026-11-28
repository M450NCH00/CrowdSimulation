# Search log: issue #52

> For issue [#52](https://github.com/M450NCH00/CrowdSimulation/issues/52). All work done on
> 2026-10-19 in one session. Records what was read first, how sources were confirmed and fetched,
> every search, every paper screened with one line on why it was or was not chosen, the unread
> leads, and what went wrong.

Companion files: [entries](entries.md) · [findings](findings.md) · [verdict](verdict.md) ·
[token estimates](token-estimates.md) · [missing papers](missing-papers.md) ·
[BibTeX](refs-environment-description.bib)

---

## §1. What was read first

As the issue asks, and only these: `llm_negotiation/negsim/rulegen/describe.py` (module docstring,
`first_person`, `third_person`); `llm_negotiation/negsim/negotiation/situation.py` (module
docstring); `persona_v1.yaml` and the `situation` block of `rulegen_negotiate_v2.yaml`; in
`literature/llm-behavioural-conflict/llm-behavioural-conflict.md` the entries [Baimbetova-PedAwareAV],
[Yoldas-YieldBias], [Seo-LLMDR], [Wang-SAMALM] and the [Cross-HypotheticalMinds] row;
`literature/paper-summaries/02-sense-think-act-reflect.md` and `03-gamechat.md`.

Later, for specific needs: the headings of `literature/demographic-personas/` (to cross-reference,
Q4); `refs/td_amano2026_mobility.txt` (screening, §4); the pricing block of `pipeline/config.py`
(the cost line in Q6). For conventions only: `literature/trained-deciders/` and `.gitignore`.

## §2. How sources were confirmed and fetched

- **Confirmation.** The arXiv API returned HTTP 429 on every attempt (with and without a pause), so
  each arXiv record was confirmed from its abs page (`arxiv.org/abs/<id>`: citation meta tags,
  Comments, Journal-ref, submission history). Published versions were confirmed on the Crossref API
  (`api.crossref.org/works/<doi>` and `query.bibliographic`), the journal's own article page
  (Acta Polytechnica CTU Proceedings, OJS), and ML Anthology (TMLR). The page title was checked
  against the paper's title each time.
- **Fetching.** Full texts were downloaded into a scratch folder, extracted with `pdftotext -enc
  UTF-8` (reading order, no `-layout`), and searched with a keyword-in-context script; only the
  passages needed were read into the conversation. The five chosen were then copied to
  `refs/ed_*.{pdf,txt}` with their abs or landing pages.
- **Tables.** Chen et al.'s Tables 1 and 3 and Figure 9 were checked on pages rendered with PyMuPDF.
- **Quotation check.** A script checked every quotation in `entries.md` and `findings.md` against the
  extracts and reported the PDF page from the extract's form feeds; 21 page locators were corrected
  as a result (my first count of page markers was off by one or two pages).

## §3. Searches

Web searches used the `standard` mode unless marked. "Lead" means a title worth following that was
not read.

| ID | Query | Tier aimed at | Outcome |
|---|---|---|---|
| S1 | LLM agents crowd simulation perception prompt neighbours described in text pedestrian | 1 | Durupinar 2026, Amano 2026, SenseWalk 2026, Jimenez-Romero 2025, Ntarouis & Geraerts 2026, Liu et al. 2025. Chosen: Durupinar, Ntarouis |
| S2 | comparison of scene representation formats for LLM driving prompt text vs JSON vs coordinates ablation | 2/3 | No driving format comparison found; leads 2605.04475, 2311.17076, GROKE |
| S3 | Why solving multi-agent path finding with large language model has not succeeded yet map representation | 2 | Chen, Koenig & Dilkina 2024 (arXiv 2401.03630). Chosen |
| S4 | Is a picture worth a thousand words spatial reasoning vision language models SpatialEval text-only vision-only | 3 | Identified the SpatialEval lead: Wang et al., NeurIPS 2024, arXiv 2406.14852 |
| S5 | LLM social robot navigation crowd prompt describe pedestrians positions velocities text ablation of scene description | 2 | Xiao & Yamasaki 2026; leads NaviWM, SRLM; no scene-description ablation found |
| S6 | grid map representation for LLM path planning text matrix vs coordinate list comparison success rate | 3 | Martorell 2025, Li et al. 2026 (2604.10690), GROKE, 2507.12391. Chosen: Martorell |
| S7 | BALROG benchmark agentic LLM VLM games language-only vs vision observations | 2/3 | BALROG, ICLR 2025 (screened, not chosen) |
| S8 | LLM autonomous driving surrounding vehicles described in text prompt number of vehicles performance degrades DiLu scenario description | 2 | No vehicle-count result; leads DiLu, Tanahashi et al. 2023, LimSim++ |
| S9a–c | Venue checks: "From Text to Space" Martorell …; "Why Solving Multi-agent Path Finding …" venue; Durupinar "How Affect Propagates …" | — | Martorell: Springer CCIS chapter (confirmed on Crossref). Chen: TMLR 2025, retitled (confirmed on ML Anthology). Durupinar: no published version |
| S10 | comparing prompt formats for pedestrian conflict LLM crowd simulation text description ablation egocentric versus coordinates (**extended**) | 1 (gap G1) | No format comparison for pedestrian conflicts; returned Durupinar again, PEDRA (video generation), a VLM crossing-intention paper (2606.09142) |
| S11 | LLM agent performance as number of nearby agents in prompt increases observation length scaling multi-agent simulation | 1/2 (gap G2) | No neighbour-count result; leads 2604.17191, OpenCity; Wu et al. 2024 (already in the repository) |
| S12 | egocentric versus allocentric spatial description LLM benchmark frame of reference relative directions accuracy | 3 (gap G4) | Leads: Sidhu & Hockenmaier 2026 (GSU), a TU Delft thesis, MENTALMAP, a COSIT 2026 paper |
| S13 | arxiv "Solving Multi-Agent Path Finding as an LLM Benchmark" How, How Good and Why | — | No arXiv copy of the TMLR version; OpenReview PDF refused (403) |
| C1–C3 | Crossref `query.bibliographic` for Park et al.; Durupinar; Ntarouis & Geraerts | — | Park: UIST '23, doi:10.1145/3586183.3606763. Durupinar: no record. Ntarouis: doi:10.14311/APP.2026.57.0263 |

## §4. Papers screened

"Screened" means the full text was downloaded and searched for the perception-to-text step, any
selection or cap on who is described, and any measured comparison of formats. "Considered" means
title, record or abstract only: nothing is claimed about the content of those.

| # | Paper | Year / status | How far | Chosen? | Why, in one line |
|---|---|---|---|---|---|
| 1 | Durupinar, "How Affect Propagates among LLM Agents" | 2026 / preprint | Screened, read in full | **Yes** | Tier 1; explicit perception rule and cap; prompt printed; prompt variants measured |
| 2 | Ntarouis & Geraerts, "Generative agents in crowd simulation" | 2026 / PED 2025 proceedings | Screened, read in full | **Yes** | Tier 1, peer-reviewed; radius perception; 10–250 agents measured |
| 3 | Park et al., "Generative Agents" | 2023 / UIST | Screened, read in full | **Yes** | Tier 2, peer-reviewed; the reference design for prose environments and partial knowledge |
| 4 | Chen, Koenig & Dilkina, "Why Solving Multi-agent Path Finding with LLMs has not Succeeded Yet" | 2024 / TMLR 2025 (retitled) | Screened, read in full | **Yes** | Tier 2 with a measured comparison of formats and of agent counts |
| 5 | Martorell, "From Text to Space" | 2025 / CCIS (Springer) | Screened, read in full | **Yes** | Measured comparison of six text formats, published |
| 6 | Liu, Shatzel, Haworth & Schneider, "Emergent Crowds Dynamics from Language-Driven Multi-Agent Interactions" (2508.15047) | 2025 / preprint | Screened | No | Tier 1, but perception is a rendered image per agent plus dialogue, with no format comparison, and its supplement reference is broken in the PDF ("Supplemental ??") |
| 7 | Xiao & Yamasaki, "Probing Prompt Design for Socially Compliant Robot Navigation with VLMs" (2601.14622) | 2026 / preprint | Screened | No | Varies system guidance and motivational framing; the scene is an image, so it is not a comparison of scene descriptions |
| 8 | Paglieri et al., "BALROG" (2411.13543) | 2024 / ICLR 2025 | Screened | No (closest miss) | Measured text-only vs text + image in games; [Chen-MAPFLLM] already covers text vs image in a multi-agent spatial task, and negsim is text-only |
| 9 | Fatemi, Halcrow & Perozzi, "Talk like a Graph" (2310.04560) | 2023 / ICLR 2024 | Downloaded, skimmed | No (closest miss) | Measured text encodings of abstract graphs; [Martorell-TextToSpace] compares encodings of space, which is negsim's case |
| 10 | Wang et al., "Is A Picture Worth A Thousand Words?" (SpatialEval, 2406.14852) | 2024 / NeurIPS | Downloaded, not searched in depth | No | A vision-language modality question; negsim is text-only |
| 11 | Li, Zhu, Das & Dube, "Do LLMs Build Spatial World Models?" (2604.10690) | 2026 / preprint | Downloaded, not searched in depth | No | Grid vs adjacency encodings of mazes; preprint, and a published comparison of spatial text formats (Martorell) was available |
| 12 | Shami et al., "GROKE" (2601.07375) | 2026 / preprint (under review) | Downloaded, not searched in depth | No | Map encodings for evaluating route instructions; further from agents perceiving people |
| 13 | Tanahashi et al., "Evaluation of LLMs for Decision Making in Autonomous Driving" (2312.06351) | 2023 / NeurIPS 2023 ML4AD symposium | Downloaded (short paper), not searched in depth | No | Tier 2 (driving) without a measured format comparison indicated; time went to tier 1 instead |
| 14 | Jimenez-Romero, Yegenoglu & Blum, "Multi-Agent Systems Powered by LLMs: Applications in Swarm Intelligence" (2503.03800) | 2025 / preprint | Downloaded, not searched in depth | No | Ants and birds in NetLogo, not people; no measured format comparison indicated |
| 15 | Lin et al., "SenseWalk" (2607.00989) | 2026 / preprint | Downloaded, not searched in depth | No | Tier 1 candidate left unread for time; listed as a lead (§5) |
| 16 | Amano & Yamaguchi, "Distilling Aggregate Mobility Statistics into a Language Model Policy" (2608.19778) | 2026 / accepted short paper | Searched the cached extract (`refs/td_amano2026_mobility.txt`) | No | Its situation text concerns points of interest and events; no description of other agents found |
| 17 | Nguyen et al., "GROVE" (2606.25504) | 2026 / accepted at IROS 2026 (arXiv comment) | Considered (record only) | No | Turns a text prompt into a pedestrian scenario, the opposite direction to this issue's question (from its abstract) |
| 18 | Yamada et al., "Evaluating Spatial Understanding of LLMs" (2310.14540) | 2023 / TMLR 2024 (arXiv comment; the lead's venue is now confirmed) | Considered (record only) | No | Varies spatial structures (grids, rings, trees) rather than description formats (from its abstract) |
| 19 | Sidhu & Hockenmaier, "Grid Spatial Understanding: A Dataset for Textual Spatial Reasoning over Grids, Embodied Settings, and Coordinate Structures" (2603.17333) | 2026 / preprint | Considered (record only) | No | The lead's title was incomplete; confirmed full title above. Frame-of-reference evidence for gap G4: a lead (§5) |
| 20 | Repository entries: [Baimbetova-PedAwareAV], [Yoldas-YieldBias], [Seo-LLMDR], [Wang-SAMALM], [Cross-HypotheticalMinds], [Zhang-DFD], [Mahadevan-GameChat] | 2023–2026 | Their repository entries only (read for other questions) | No | Not re-read: none of the entries records a comparison of description formats; [Yoldas-YieldBias] is used as the Q4 cross-reference |

## §5. Unread leads

Worth reading in a follow-up, in rough order of use to negsim:

1. Sidhu & Hockenmaier 2026 (arXiv 2603.17333): egocentric frames of reference in text; bears on gap G4.
2. Lin et al. 2026, SenseWalk (arXiv 2607.00989): an LLM crowd simulator with a perception step (tier 1).
3. NaviWM (arXiv 2510.23509): structured agent state for LLM social navigation.
4. "Do LLM-derived graph priors improve multi-agent coordination?" (arXiv 2604.17191): prompt length vs number of agents.
5. Li et al. 2026 (arXiv 2604.10690) and GROKE (arXiv 2601.07375): further measured format comparisons (preprints).
6. "Navigating Mazes with Large Language Models" (TU Delft repository thesis) and the COSIT 2026 spatial-reasoning paper (LIPIcs vol. 393): output frame of reference.
7. arXiv 2605.04475 (neuro-symbolic driving scene summaries in JSON) and Compositional Chain-of-Thought (arXiv 2311.17076): JSON scene graphs vs captions.
8. SRLM (arXiv 2403.15648), DiLu (ICLR 2024), LimSim++ (arXiv 2402.01246): text scene descriptions in robots and driving.

## §6. What went wrong

- The arXiv API refused every request (HTTP 429); abs pages were used instead.
- Zenodo (Ntarouis & Geraerts' supplement) and OpenReview (Chen et al.'s TMLR PDF) refused
  automated download (HTTP 403). Both are listed for the user in [missing-papers.md](missing-papers.md).
- Page markers: my first pass counted printed page numbers by hand and was off by one or two pages for
  two papers; the quotation script, which counts form feeds, caught it and the locators were fixed
  before `entries.md` was committed.
- The Park et al. extract garbles the μ, σ and d glyphs; the quotations exclude them and the values are
  given as printed, with a note.
