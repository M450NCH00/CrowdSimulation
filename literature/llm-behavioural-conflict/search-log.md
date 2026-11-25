# Search log — LLMs resolving spatial conflict without conversation

> All work done on 2026-10-05, on branch `docs/22-simulation-conflict-rules-literature`, at the
> user's direct request (no GitHub issue). Records what was searched, how each source was
> handled, what was excluded, and what remains uncertain.

Companion files: [review](llm-behavioural-conflict.md) · [refs](refs-llm-behavioural.bib)

## §1. What was read first

- `literature/simulation-rules/` — `search-log.md`, `research-gap.md`, `s1-crowd-simulation.md`,
  `missing-papers.md` — to match conventions and to find what was already covered.
- `literature/llm-conflict-resolution/` — `search-log.md` and the first three entries of
  `topic1-llm-conflict.md` — because [Zhang-DFD], [Mahadevan-GameChat] and [Chen-MAPF] are
  already there.
- The titles in every `.bib` under `literature/`, to avoid duplicates. None of the 11 entries
  added here was already in the repo.
- **Not read:** `integration/crowdgym_mapping.md`, `dataset/schema/README.md`. Nothing here
  proposes a CrowdGym change.

## §2. Method

**Finding.** Web search only (queries in §3). Every candidate's title, author list and date
were then confirmed from the arXiv API (`refs/lb_arxiv_api_metadata_1.xml`,
`refs/lb_arxiv_api_metadata_2.xml`); no identifier was guessed.

**Fetching.** PDFs were downloaded from arXiv with `curl` and converted with
`pdftotext -layout`. The first line of each extract was checked against the expected title. No
wrong paper was downloaded.

**Caching.** Only the **text extracts** are in `refs/` (`refs/lb_*.txt`, 20 files). The PDFs
were not kept: several exceed the 5 MB the repo otherwise git-ignores. Re-download from
`https://arxiv.org/pdf/<id>`; the id is in each filename.

**Published versions.** Checked by a Crossref title search for nine titles. Found: RA-L records
for [Song-VLMSocialNav] and [Fang-Etiquette], the AAAI record for [Zhang-ProAgent], and the
two paywalled evacuation papers. Not found: [Wang-SAMALM], [Seo-LLMDR], [Zhao-MotionAgents],
[Garg-FMDeadlock] (a different CDC 2024 paper came back; relation not established).
[Cross-HypotheticalMinds] is ICLR 2025 by the header of its own PDF; [Agashe-LLMCoordination]'s
venue comes from an ACL Anthology identifier in a search result and the Anthology page was not
opened.

**What "read" means here — weaker than in issue #22.** No entry was read in full. Each was
read by keyword-led passes (`grep` for conflict, yield, collision, deadlock, communication,
prompt, limitation and similar, with the surrounding passage), plus the abstract, and for six
entries one or two whole sections. Each entry's *Verified* line lists what was read. This was a
deliberate trade: 20 papers screened in one session rather than 6 read properly.

**What extraction lost.** Two-column layouts are interleaved; tables lost alignment
([Song-VLMSocialNav] Table I, [Wang-SAMALM] Table I, [Seo-LLMDR] Table I); results shown only
in plots are gone ([Garg-FMDeadlock], all of them).

## §3. Searches actually run (13)

1. `large language model pedestrian crowd simulation agents collision avoidance yielding decision without communication arXiv`
2. `LLM deadlock resolution multi-robot navigation narrow corridor leader assignment "large language models" high-level planner`
3. `LLM-driven social force model pedestrian simulation human-like behaviour bottleneck counterflow evacuation 2024 2025`
4. `vision-language model socially aware robot navigation social conventions yield pass on right crowd pedestrians`
5. `LLM agents Overcooked zero-shot coordination infer partner intention without communication collision narrow corridor layout`
6. `LLM multi-agent path finding deadlock detection resolution PIBT language model decentralized`
7. `"large language model" agents fire evacuation cellular automata Safety Science 2025 pedestrians conflict same cell`
8. `Hypothetical Minds theory of mind LLM agents Melting Pot no communication spatial coordination`
9. `LLM pedestrian agents "human-like" walking behaviour corridor passing side preference yielding evaluation against real trajectories language model simulation`
10. `LLM commonsense priority who should yield robots humans doorway elderly "social norms" navigation zero-shot deadlock symmetry breaking`
11. `LLM generates crowd simulation agent behaviour rules parameters persona-conditioned social force ORCA "language model" pedestrians heterogeneous`

Two further queries were run **after** the tiers had been drafted, to test the bottom line:

12. `LLM asked "who should yield" two pedestrians narrow corridor OR doorway persona age gender language model prediction compared with human behaviour` — produced [Yoldas-YieldBias].
13. `LLM zero-shot crowd navigation agents each controlled by language model collision avoidance decentralized no communication benchmark deadlock "social" hallway intersection multi-agent` — produced [Zhao-MotionAgents].

Query 12 was the direct test of
"is there a paper where an LLM is asked who yields between two pedestrians". It returned
none — the nearest hit was vehicle-to-pedestrian yielding.

**Three sources came from prior knowledge**, then located by a search: [Garg-FMDeadlock],
[Zhang-ProAgent], [Cross-HypotheticalMinds].

**Not searched:** Google Scholar, Scopus, Web of Science, IEEE Xplore, ACM DL, DBLP. No
forward or backward citation chaining.

## §4. Leads seen in results and not opened

Titles as they appeared in search results; none confirmed, none summarised.

- "Robots Ask the Way: Communication-Enabled Social Navigation" (arXiv:2607.01044) —
  communication-based by title.
- "Logic-Guided Socially-aware Robot Navigation World Model" (arXiv:2510.23509).
- "SocialNav: Training Human-Inspired Foundation Model for Socially-Aware Embodied Navigation"
  (arXiv:2511.21135).
- "Act on What You See: Unlocking Safe Social Navigation in Vision-Language-Action Models"
  (arXiv:2606.10495).
- "LLM-Powered Embodied Intelligence for Socially-Aware Robot Navigation in Human-Robot
  Interaction" (ACM, doi:10.1145/3748777.3748807).
- "Multi-Agent Path Finding via Offline RL and LLM Collaboration" (arXiv:2509.22130).
- "FACA: Fair and Agile Multi-Robot Collision Avoidance in Constrained Environments with
  Dynamic Priorities" (arXiv:2511.14024) — unclear from the title whether an LLM is involved.
- "Benchmarking Open-Ended Multi-Agent Coordination in Language Agents" (arXiv:2606.08340).
- "A Human-Like Pedestrian Model for Automated Driving Simulations" (arXiv:2609.29175) —
  unclear whether LLM-based.
- "Smart Agent-Based Modeling: On the Use of Large Language Models in Computer Simulations"
  (arXiv:2311.06330) — the framework behind [Wu-SWTU], already in the repo.
- "Large language models empowered agent-based modeling and simulation: a survey and
  perspectives" (*Humanities and Social Sciences Communications*, 2024) — **a survey; the
  obvious next read** for finding crowd-simulation work this search missed.
- "Large Language Models for Multi-Robot Systems: A Survey" (arXiv:2502.03814) — the
  corresponding survey for Tier B.

## §5. What would overturn the bottom line

The review's central claim is a "none found". It would be false if any of these turns out to
have an LLM's behaviour knowledge decide a pedestrian-versus-pedestrian encounter without
dialogue:

1. **[Zhang-DFD]** full text — in the repo at abstract level since issue #8.
2. **CrowdVLA** full text — in the repo, scope-checked only.
3. **Dang et al., *Safety Science* 2025** — not obtained; LLM agents in a cellular automaton,
   which is where a same-cell rule would be.
4. Either survey in §4.
5. Anything in a bibliographic database, none of which was searched.

## §6. Things that should lower your confidence

- **Selective reading throughout** (§2). The tier a paper sits in depends on passages found by
  keyword; a paper could do more than the passages I saw.
- **Exclusions on one sentence.** GROVE, SenseWalk and the plaza-evacuation paper are excluded
  from T1 on the single sentence quoted for each in the review's §4.
- **Three near-misses were judged from the abstract** (SwarmBench, SocialGrid, LLM-Flock) and
  one from its **title alone** (arXiv:2409.04965). They are labelled as such.
- **The three tests are my construction**, and T3 in particular is a judgement — e.g.
  [Song-VLMSocialNav] is placed in Tier A although its passing-side rule is in the prompt.
- **arXiv-heavy sample.** Six of eleven entries are preprints.
- **Fetched content was treated as data.** No fetched page contained instructions addressed to
  the reader.
