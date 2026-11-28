# Search log — issue #2 literature review

Date of search: **2026-09-06**. Searcher: Claude Code, working from
[`../github_issue_workflow.md`](../github_issue_workflow.md).

This file records what was searched, what was found, what was *rejected*, and where
the search failed. It exists so the review in [`papers.md`](papers.md) can be audited
and re-run.

## Outcome summary

The issue asked for **5** papers. **8** are reported (7 in the original review, plus one added 2026-09-08 — see the addendum below). This is a deliberate overshoot on
scope coverage, not padding, and each extra entry is justified below:

- Five entries (Aher, Argyle, Cheng, Wang, Hullman) address the primary claim — the
  validity of LLM-elicited human behaviour data.
- One entry (Zhong et al.) covers the issue's **fourth scope bullet** — "data-driven or
  learned behaviour models for crowd/pedestrian simulation" — which none of the five
  LLM papers touches, and which is the half of the argument that connects to CrowdGym.
- One entry (Park et al.) is the mechanism/existence-proof paper, retained mainly for a
  *negative* result: its cost figure is the evidence for this project's DD1 decision to
  freeze answers offline rather than call an LLM per agent per step.
- One entry (Deshpande et al.) was **added after the fact**, when correcting entry 3
  left DD2 with no citation supporting it. See the addendum below.

No entry is included that lacks a specific, stated transfer to this project. Every
entry is marked `Verified: yes`; two are preprints, both labelled `[non-archival]`.

## Sources searched

| Source | Coverage | Result |
|---|---|---|
| arXiv | abstract pages for all 7 candidates + ar5iv full texts | primary verification source; worked throughout |
| ACL Anthology | `2023.acl-long.84` landing page | supplied venue, pages, DOI, BibTeX for Cheng et al. |
| ACM Digital Library | attempted for `10.1145/3586183.3606763` and `10.1145/3481299` | **blocked — HTTP 403 to automated fetches** (see dead ends) |
| Semantic Scholar (Graph API) | 8 lookup attempts across 2 batched runs | **mostly rate-limited — HTTP 429** (see dead ends) |
| Google Scholar / general web search | all suggested queries below | used to locate candidates and cross-check numbers; never used as sole evidence |
| Cambridge Core | `10.1017/pan.2023.2` landing page | confirmed *Political Analysis* publication of Argyle et al. |
| Author open-access mirror | Carleton University copy of TOMACS survey PDF | used after ACM DL 403; verified against the PDF's own ACM reference block |

## Queries run

From the issue's suggested list and follow-ups:

1. `Argyle "Out of One, Many" language models simulate human samples Political Analysis`
2. `Park "Generative Agents: Interactive Simulacra of Human Behavior" UIST 2023`
3. `Horton "Large Language Models as Simulated Economic Agents" homo silicus arXiv`
4. `Cheng Durmus Jurafsky "Marked Personas" stereotypes LLM persona generation ACL 2023`
5. `data-driven crowd simulation pedestrian behavior model learned from real data survey`
6. `"Data-driven Crowd Modeling Techniques: A Survey" ACM Transactions Modeling Computer Simulation 10.1145/3481299`
7. `"Data-driven Crowd Modeling Techniques: A Survey" authors Zhu Wang TOMACS 2022 volume 32` — *note: this query embedded a wrong author guess ("Zhu Wang"); the search corrected it to Jinghui Zhong et al., which was then confirmed from the PDF front matter. Recorded because it is exactly the kind of half-remembered attribution the issue's "never cite from memory of a title alone" rule is aimed at.*
8. `Generative Agents TrueSkill "29.89" crowdworker condition believability ablation ranking`
9. `"LLM-based Human Simulations Have Not Yet Been Reliable" Wang citations published venue 2026`

## Forward-citation search (issue protocol step 3)

Checking who cites the seed papers is what produced the two most useful entries. Papers
citing Park et al. and Argyle et al. surfaced a visible cluster of *critical* work:

- **Wang et al., "LLM-based Human Simulations Have Not Yet Been Reliable"** (arXiv
  2501.08579) — adopted as entry 4.
- **Hullman et al., "This human study did not involve human subjects"** (arXiv
  2602.15785) — adopted as entry 5.
- "Social Simulations with Large Language Model Risk Utopian Illusion" (arXiv
  2510.21180) — *seen, not adopted*; see rejections.
- "Human Behavior Simulation: Objectives, Methodologies, and Open Problems" (arXiv
  2412.07788) — *seen, not adopted*; see rejections.

## Candidates considered and rejected

**Horton, Filippas & Manning, "Large Language Models as Simulated Economic Agents:
What Can We Learn from Homo Silicus?"** (arXiv 2301.07543; NBER w31122; Semantic
Scholar reports 544 citations and an ACM EC venue).
*This was one of the four seed leads in the issue, so its exclusion needs a reason.*
It was verified as real and correctly attributed, and it is genuinely relevant.
It was ranked below the seven adopted entries because its mechanism — eliciting
economic preferences by endowing an LLM with information and preferences — is already
covered, more directly and with a human baseline, by [Aher-TE]'s Ultimatum Game, which
is itself a two-party conflict over a contested resource and therefore closer to this
FYP's scenarios. Horton et al. also report qualitative correspondence with classic
findings rather than a fidelity metric against human response distributions, which is
what this project's validation needs. **Recommend citing it in the FYP report as
supporting context; it is simply not one of the load-bearing entries.** Note also
that Semantic Scholar's venue field for it ("ACM Conference on Economics and
Computation") was **not** independently confirmed and should be checked before citing.

**"Social Simulations with Large Language Model Risk Utopian Illusion"** (arXiv
2510.21180). Topically on-point and critical. Not adopted because its contribution
(LLM social simulations drift toward unrealistically harmonious outcomes) overlaps
Wang et al.'s §3–§4 while being a more recent, less-established preprint, and adopting
it would have made three of seven entries non-peer-reviewed. **Worth revisiting** — the
"utopian illusion" framing is arguably a sharper description of a conflict-resolution
dataset's failure mode (agents that always de-escalate) than anything in the adopted
set, and it deserves a look before the report is written.

**"Human Behavior Simulation: Objectives, Methodologies, and Open Problems"** (arXiv
2412.07788). Broad survey, substantially overlapping Wang et al. Rejected as redundant.

**"LLM Social Simulations Are a Promising Research Method"** (arXiv 2504.02234).
Rejected: it is the positive-position counterpart to Wang et al., and the issue
explicitly prioritises critical results, which were already better served.

**Various data-driven crowd-simulation papers** — neural pedestrian movement models
(ScienceDirect S0378437118307696), clustering-based crowd simulation (arXiv 1506.04480),
LCrowdV (arXiv 1606.08998), "Learning to Simulate Crowd Trajectories with Graph
Networks" (WWW '23). All rejected in favour of the Zhong et al. survey, which covers
this whole family *and* — uniquely — surveys crowd-model **validation**, which is what
this project actually needs. Individual trajectory-learning papers would add technique
detail with no bearing on the dataset's validity argument.

**Excluded by the issue's own scope rules:** LLM agents for coding/tool-use;
prompt-engineering how-to material with no behavioural evaluation; pure
pathfinding/physics crowd papers. Several such results appeared in query 5 and were
discarded without further checking.

## Addendum (2026-09-08) — one correction and one paper added

After the review was written, a question about **DD2** (observer framing vs first-person
role-play) prompted a re-check of Cheng et al.'s actual prompt set. That check changed
two things:

- **Correction to entry 3.** The entry claimed Cheng et al.'s prompts "were also
  third-person descriptive", and cited the paper as the justification for DD2. Both were
  wrong. **Table A9** of the published paper (now cached at
  `refs/cheng2023_marked_personas.pdf`, extracted to `.txt`) lists **six** prompts
  spanning *both* framings — three first-person (*"Imagine you are a(n) [X]. Please
  describe yourself."*) and three third-person (*"Describe a(n) [X]."*, *"Imagine a(n)
  [X]. Please describe [pronoun]."*). The authors state they "did not find statistically
  significant differences in distributions of top words across prompts" and analysed
  them in aggregate. So the paper does not support DD2 and, if anything, mildly counts
  against it.
- **Entry 8 added: Deshpande et al. (2023), EMNLP Findings.** The correction left DD2
  with no citation at all. This paper — persona *assignment* raises ChatGPT toxicity up
  to 6x across >500k generations — is the closest peer-reviewed support for the
  mechanism DD2 relies on. Found by searching for work on persona-assignment effects
  after the Cheng re-check; verified from the ACL Anthology landing page.

Method note for future searches: the original review verified Cheng et al. from the ACL
Anthology landing page and the ar5iv HTML, neither of which renders appendix Table A9.
The error would have been caught earlier by reading the published PDF. **Where a claim
depends on exactly what a prompt said, go to the PDF appendix.**

## Dead ends and failures

**ACM Digital Library returns HTTP 403 to automated fetches.** Both
`dl.acm.org/doi/10.1145/3481299` and `dl.acm.org/doi/fullHtml/10.1145/3586183.3606763`
refused. The issue names ACM DL as a required source, so this is a partial failure of
the search protocol rather than a choice. Mitigations used:
- For Zhong et al., an author open-access PDF mirror was retrieved and the citation
  verified from the paper's **own front matter and ACM reference block** — title,
  five authors with affiliations, journal, Vol. 32 No. 1 Article 4, 33 pages, DOI
  `10.1145/3481299`. This is stronger evidence than a landing page.
- For Park et al., arXiv and ar5iv supplied the full text; the UIST venue and DOI were
  taken from the ACM citation record as surfaced in search results.
- **A human on a university network can open both DOIs directly and should spot-check
  them.** Nothing in `papers.md` depends on an unverified ACM claim, but the check is
  cheap.

**Semantic Scholar Graph API rate-limited (HTTP 429).** Eight lookups were attempted
across two runs, the second with 25-second spacing; only two returned — Horton et al.
(544 citations) and Zhong et al. (32 citations). Consequence: **citation counts are not
used as evidence anywhere in `papers.md`**, and the `[non-archival]` labels on the two
preprints rest on the absence of a journal reference in the arXiv record rather than on
a citation threshold. An API key would fix this if the counts are wanted for the report.

**Wang et al.'s venue could not be settled.** A companion GitHub repository labels the
work "ICLR 2025", but the arXiv record lists no journal or conference reference. Marked
`[unverified]` in `papers.md` and treated as a preprint. Should be resolved before the
report cites it.

**Argyle et al. volume/issue/pages** (*Political Analysis* 31(3):337–351) come from the
Cambridge Core record, not from the article PDF. Marked `[unverified]` in `papers.md`.

**PDF text extraction of the ACL Anthology copy of Cheng et al. failed** (returned raw
compressed PDF streams). Worked around via the ar5iv HTML rendering of arXiv:2305.18189;
the ACL Anthology landing page supplied the authoritative venue, pages and DOI.

## Note on section numbers

Section, figure and table references in `papers.md` were read from the ar5iv HTML
renderings of the arXiv versions, not from the published camera-ready PDFs. Numbering is
normally identical but is not guaranteed to be. Two fetches of Aher et al. gave slightly
different section attributions for the hyper-accuracy-distortion discussion, so it is
cited there as "§7–§8" rather than a single section. **Anyone quoting a specific number
in the final report should confirm its location against the published version.**

## One reading that was corrected mid-search

The first extraction of Park et al.'s evaluation implied the human crowdworker baseline
ranked below every ablated condition. Cross-checking against a second independent source
gave the actual ordering — full 29.89 > no-reflection 26.88 > no-reflection-no-planning
25.64 > **crowdworker 22.95** > no-memory-planning-reflection 21.21 — i.e. the human
baseline ranks fourth of five, above only the most severely ablated system. The
corrected reading is what appears in `papers.md`, and it materially weakens the
"outperforms humans" headline, which is why the correction is recorded rather than
quietly fixed.

## Cached sources

All in [`../refs/`](../refs/), so every claim above can be re-checked without re-running
the search:

```
refs/aher2023_turing_experiments_abs.html
refs/argyle2023_out_of_one_many_abs.html
refs/cheng2023_marked_personas_abs.html
refs/cheng2023_marked_personas_aclanthology.html
refs/hullman2026_validating_llm_simulations_abs.html
refs/park2023_generative_agents_abs.html
refs/wang2026_not_yet_reliable_abs.html
refs/zhong2022_data_driven_crowd_survey.pdf
refs/zhong2022_survey.txt          (pdftotext extraction of the above)
refs/cheng2023_marked_personas.pdf (published PDF — added 2026-09-08 for Table A9)
refs/cheng2023_marked_personas.txt (pdftotext extraction of the above)
refs/semanticscholar.json          (API responses, mostly 429s — kept as the record)
refs/s2_preprints.json             (follow-up API attempt for the two preprints)
```
