# Search log — issue #8 literature review

Date of search: **2026-09-12**. Searcher: Claude Code, working from
[`../../github_issue_workflow.md`](../../github_issue_workflow.md).

This file records what was searched, what was found, what was **rejected**, and where
the search failed, so that the reviews in
[`topic1-llm-conflict.md`](topic1-llm-conflict.md) and
[`topic2-sociological-grounding.md`](topic2-sociological-grounding.md) can be audited
and re-run. It follows the same convention as the issue #2 search log.

## Outcome summary — count vs. the 10-paper target

The issue asked for **10 or more papers within 2016–2026**, in addition to the two
supervisor-assigned papers. **12 are reported**, split:

| | Papers | Peer-reviewed | Preprints |
|---|---|---|---|
| Topic 1 — LLM conflict resolution | 7 | 6 | 1 |
| Topic 2 — sociological grounding | 5 | 4 | 1 |
| **Total (2016–2026)** | **12** | **10** | **2** |
| Supervisor-assigned (counted separately) | 2 | 2 | 0 |

Both preprints are labelled `[non-archival]` in the reviews, and **neither is the sole
support for any claim** — Chen et al. (Topic 1) is a negative result that agrees with the
peer-reviewed Mahadevan et al.; Terwilliger et al. (Topic 2) is the lowest-relevance
entry in this review and supports no claim on its own.

The target was met without padding. Every entry has a stated, specific mechanism that
transfers either to the 2-agent hallway scenario or to validating a pattern against real
behaviour; entries that lacked one were rejected (see below).

## Two findings that were not anticipated by the issue

1. **The two supervisor-assigned papers are one citation chain.** Wu et al. (2024) §6.1:
   *"We follow Wang et al. (2015) to simulate EE in a grid environment."* The issue
   presented them as two separate starting points.
2. **A real human dataset exists** (Jülich Pedestrian Dynamics Data Archive, CC-BY,
   doi:10.34735/ped.da), including **bidirectional corridor** experiments. The issue
   asked for this to be flagged prominently if found — it is, at the top of
   `topic2-sociological-grounding.md`. It changes roadmap step 5 from "argue from
   sociology" to "measure against trajectories."

A third finding, recorded here because it affects project scope rather than the search:
**Zhang et al., ACM TOMACS 2026** already publishes the core idea of roadmap steps 3–4
(distil an interpretable decision function from LLM-driven crowd agents, demonstrated on
evacuation), with two NTU co-authors. Discussed in `topic1-llm-conflict.md`.

## Sources searched

| Source | Coverage | Result |
|---|---|---|
| ACL Anthology | `2024.findings-emnlp.297` landing page | supplied venue, pages, DOI, BibTeX for Wu et al. |
| arXiv | abstract pages for 8 candidates; 2 full PDFs | primary verification source; worked throughout |
| **Crossref API** | 7 DOIs | **authoritative** author lists / volumes / pages; used to double-check every DOI-bearing entry |
| Semantic Scholar (Graph API) | forward citations of Wu et al. (58 results); 2 metadata lookups | worked via **DOI** route; **arXiv-id route returned HTTP 429** |
| NeurIPS proceedings | Abdelnabi et al. D&B track page | corrected the venue (NeurIPS, not ICLR) |
| PMLR | `v235/bianchi24a` landing page | supplied volume, pages, official BibTeX |
| PMC (PubMed Central) | Echeverría-Huarte et al. full text | used after nature.com refused; gave abstract + data availability |
| eLife | article 81641 | full participant counts and per-pair result breakdown |
| City Research Online (open access) | Ashery et al. record | used after science.org refused |
| RePEc / IDEAS | Wang et al. 2015 record | used after ScienceDirect refused |
| ped.fz-juelich.de | data archive database page | confirmed the dataset, licence and DOI |
| Author homepage | philipp-andelfinger.net publications | supplied BibTeX for Zhang et al. after ACM DL refused |
| Google/general web search | all suggested queries below | used to locate candidates; **never used as sole evidence** |

## Queries run

**Topic 1** (issue's suggested list plus follow-ups):

1. `arXiv "Shall We Team Up" Zengqing Wu spontaneous cooperation competing LLM agents`
2. Forward-citation sweep: Semantic Scholar `citations` endpoint on
   `DOI:10.18653/v1/2024.findings-emnlp.297` — **this is what produced the two best
   Topic 1 entries** (Zhang et al., and the route to Ashery et al.)
3. Backward sweep: read the full reference list of the Wu et al. PDF — produced
   Abdelnabi et al. and Piatti et al. directly
4. `"Sense, Think, Act, Reflect" distilling fast interpretable decision functions
   LLM-driven crowds TOMACS`
5. `arXiv Zhang Andelfinger Tan Cai "Decision Function Distillation" LLM crowd simulation`
6. `LLM agents narrow corridor passing conflict who yields two agent spatial coordination
   right of way` — **produced GameChat**, the single closest paper to the FYP's scenario
7. `NegotiationArena Bianchi "how well can LLMs negotiate" ICML 2024 two agent bargaining`
8. `Abdelnabi "Cooperation, Competition, and Maliciousness" ... ICLR 2024 openreview`
   — *this query embedded a wrong venue guess; the search corrected it to NeurIPS 2024
   Datasets and Benchmarks Track, which was then confirmed from the NeurIPS proceedings
   page. Recorded because it is exactly the kind of half-remembered attribution the
   issue's "never cite from memory or from a title alone" rule exists to catch.*
9. `Ashery Aiello Baronchelli emergent social conventions collective bias populations of
   LLM agents Science Advances 2025`

**Topic 2:**

10. `pedestrian "head-on" avoidance experiment who yields right-of-way negotiation narrow
    passage study two pedestrians` — produced Yamamoto et al. and the Echeverría-Huarte lead
11. `implicit coordination human dyads turn-taking shared resource conflict who goes first
    social norm experiment psychology` — **produced Moeller et al.**, the strongest
    Topic 2 entry
12. `Jülich pedestrian dynamics data archive open trajectory dataset bidirectional
    corridor experiments` — produced the dataset flag and Boomers et al.
13. `pedestrian social norms right-of-way decision "who gives way" gaze signalling
    negotiation behavioural study 2020..2026`
14. `head-on collision avoidance 32 pairs pedestrians cost-benefit framework sideways
    velocity experiment` — **failed**, see dead ends

## Papers considered and rejected

Rejections matter as much as inclusions; these were all looked at and deliberately left out.

| Candidate | Why rejected |
|---|---|
| Park et al., *Generative Agents* (UIST 2023) | Already reviewed as entry 7 of issue #2 (`literature/papers.md`). No conflict component — agents cooperate or coexist. Not duplicated here. |
| Qian et al., *Communicative Agents for Software Development*; Hong et al., *MetaGPT*; Li et al., *CAMEL* | The issue's explicit exclusion: multi-agent LLM collaboration with **aligned** goals and no actual conflict. |
| Du et al., *Improving Factuality through Multiagent Debate* | Debate over facts, not a contested resource. No conflict of interest between agents. |
| Lan et al. (Avalon), Du & Zhang (Werewolf), Wu et al. (Werewolf reasoning) | Social-deduction games. The "conflict" is hidden-role deception, and the mechanism (lying to conceal identity) does not transfer to a hallway crossing. |
| Guo et al., *Embodied LLM Agents Learn to Cooperate in Organized Teams* | Closer, but the structure studied is hierarchy/team organisation, not resolution of a symmetric two-party conflict. Cut for relevance, not quality. |
| Mozikov et al., *The Good, the Bad, and the Hulk-like GPT* | Emotion-conditioned bargaining. A reasonable 11th Topic 1 entry; cut because Bianchi et al. already covers "framing changes negotiation payoffs" from a peer-reviewed venue. |
| Numerous 2026 LLM-society papers from the forward sweep (*Moltbook* studies, collusion audits, emotional-contagion-in-crowds, misalignment surveys) | Large-scale LLM societies or safety auditing. The issue asks for work closer to a 2-agent conflict, not population-scale emergent behaviour — Ashery et al. was kept as the single best-evidenced representative of that cluster. |
| Corbetta et al., *Experimental characterization of collision avoidance in pedestrian dynamics* (Phys. Rev. E 94:022318, 2016) | In window and on topic, but **could not be verified** — APS returned HTTP 403 (see dead ends). Excluded rather than cited unverified. |
| Gaze-cues paper, *Int. J. Social Robotics* (2023), doi:10.1007/s12369-023-01064-3 | Genuinely relevant mechanism (non-verbal signalling of skirting intention), but **verification failed** — Springer redirects into a cookie/auth loop. Excluded rather than cited from a search-result summary. |
| Pedestrian–vehicle right-of-way negotiation studies (shared space, unsignalised crosswalks) | The conflict is human-vs-vehicle with a large asymmetry in mass, speed and legal status. Mechanism does not transfer cleanly to two pedestrians. |
| Moussaïd et al. (2011), Goffman, *Relations in Public* | Correct topic, but **outside the 2016–2026 window**, which the issue says to enforce strictly with only the two supervisor papers exempt. |

## Dead ends and failures

- **ACM Digital Library — HTTP 403** to automated fetches on `10.1145/3818686`. Same
  block issue #2 hit. Worked around via Crossref + Semantic Scholar + the author's own
  publications page. **Consequence: the Zhang et al. entry is abstract-level only, and
  says so.** The full text should be pulled through the NTU library before the report
  cites its results.
- **APS (journals.aps.org) — HTTP 403.** Cost us the Corbetta et al. 2016 paper, which
  was rejected rather than cited unverified.
- **SpringerLink — cookie/auth redirect loop** (`idp.springer.com` → back to the article
  with `error=cookies_not_supported`). Cost us the gaze-cues paper.
- **nature.com — HTTP 303** to an authentication endpoint. Worked around via PMC.
- **science.org and NASA ADS** — refused (ADS returned HTTP 405). Worked around via the
  City Research Online open-access record.
- **ScienceDirect** — refused. Worked around via RePEc for Wang et al. 2015.
- **Semantic Scholar arXiv-id route — HTTP 429** (rate limited), repeatedly. The **DOI
  route worked**. This is the same failure issue #2 documented; if a third review needs
  S2 at volume, request an API key.
- **DBLP** — both TLS verification failure from Python and an unparseable response via
  curl. Venue confirmation was done via NeurIPS/PMLR proceedings pages instead.
- **The Wu et al. PDF could not be read by the fetch tool** (returned as binary garbage).
  Resolved by downloading it and running `pdftotext -layout` locally — which is how the
  real Table 2 numbers, the Wang et al. citation, and the authors' own admission about
  the weakness of the evacuation metrics were obtained. Worth repeating for future
  reviews: **fetching a PDF summary is not the same as reading the paper**, and in this
  case the summary would have missed the review's most important criticism.
- **Query 14 failed outright.** A search result described a head-on avoidance experiment
  with "32 participant pairs" at 2/6/10 m initial distances with a cost–benefit decision
  framework. No amount of follow-up searching located the actual paper, and the
  description came from a search-engine summary rather than a primary source. **It is
  therefore not cited anywhere in this review.** Flagged here because it sounds highly
  relevant and someone should try to find it properly — it may be the
  *Transportation Research Part B* 2025 "geometric cognition pedestrian dynamics model"
  paper, but that was not confirmed.

## Verification method

For each entry: the abstract page or PDF was opened directly and cached to
[`../../refs/`](../../refs/). For every entry with a DOI, the author list, title, venue,
volume and pages were then independently re-fetched from the **Crossref API**
(`refs/crossref_metadata.json`) and compared against the page — this caught nothing
wrong, but it is what makes "verified" mean something more than "a web page said so."

Where a number in the reviews could not be traced to a primary source it is marked
`[unverified]` rather than dropped, so a reader can see the gap. Three entries
(Zhang, Ashery, Piatti) are verified at abstract level only, and each says so in its
"Verified" field.
