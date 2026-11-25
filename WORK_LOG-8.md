# Work Log — Issue #8: [Research] Literature review: LLM-to-LLM conflict resolution + sociological grounding (no experimentation)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/8
**Branch:** `docs/8-lit-review-llm-conflict-resolution`
**Started:** 2026-09-12

## Understanding the issue

The second supervisor meeting changed the project's direction. Instead of using an LLM
as a static world model to emit a behaviour dataset (Phase 1, issue #1/#2), the project
now wants **two or more LLM agents to talk to each other until a conflict resolves**
— the canonical toy case being two agents crossing a narrow hallway from opposite
directions — and then to extract a **reusable resolution pattern** from those exchanges,
so that CrowdGym can apply the pattern to future conflicts without paying for a fresh
LLM-to-LLM exchange every time. The pattern then has to be validated against real human
behaviour: a dataset if one exists, sociological literature if not.

This issue is the **literature step only**. The supervisor's instruction is explicit and
standing: no dataset generation, no simulation code, no experimentation until the review
is done and discussed. So this branch produces documents and nothing else.

Concretely the issue asks for:

- **10+ papers from 2016–2026**, *in addition to* the two supervisor-assigned papers.
  The 2015 Wang et al. paper is deliberately outside the window and must not be counted
  toward the 10.
- Split across **Topic 1** (LLM agents communicating to resolve conflict, especially work
  that extracts a *pattern/strategy* rather than reporting one-off runs) and **Topic 2**
  (sociological / behavioural work on how real humans resolve small-scale spatial and
  interpersonal conflict, usable as validation ground truth).
- Every title/author/year/venue confirmed by opening the real abstract or PDF.
- A prominent flag if any **real-world human conflict-resolution dataset** turns up in
  Topic 2 — the issue notes this would materially change the project's validation plan.

### Assumptions I am making (flagged per CLAUDE.md)

1. **Deliverable path.** The issue body says `/CrowdSimulation/literature/llm-conflict-resolution/`.
   Per the repo-layout note in `CLAUDE.md`, that `/CrowdSimulation` prefix is stale — this
   repository *is* that folder. I am writing to `literature/llm-conflict-resolution/` and
   will correct the path in the issue body itself, as CLAUDE.md instructs.
2. **Conventions inherited from issue #2.** That review established the house style:
   a summary table, per-entry template, `[unverified]` markers on any number not confirmed
   from a primary source, preprints labelled `[non-archival]`, and source caches under
   `refs/`. I am following all of it rather than inventing a second format.
3. **"Peer-reviewed where possible."** Topic 1 is a fast-moving 2023–2026 area where a lot
   of the best work is arXiv-only. I will prefer peer-reviewed venues, label every preprint
   `[non-archival]`, and make sure no load-bearing claim rests on a preprint alone.

## Plan

1. Branch + work log (this file), commit.
2. Verify the two supervisor-assigned papers from primary sources first — they anchor both
   topics and Wu et al. is the forward/backward citation hub for Topic 1.
3. Topic 1 search: ACL Anthology, arXiv, Semantic Scholar, Google Scholar. Run the issue's
   suggested queries plus follow-ups. Do the bidirectional citation sweep around Wu et al.
4. Topic 2 search: pedestrian behaviour / spatial conflict / turn-taking literature, plus an
   explicit hunt for a real human conflict-resolution **dataset** (this is the highest-value
   possible find in this issue).
5. Verify every candidate by opening its abstract page or PDF; cache each to `refs/`.
6. Write `topic1-llm-conflict.md`, `topic2-sociological-grounding.md`, `refs.bib`,
   `search-log.md`. Commit in logical increments.
7. Verify per workflow §5b (research-task verification), then push and open the PR.

## Progress log

### 2026-09-12 — branch created, work log seeded
- What I did: read issue #8 and `github_issue_workflow.md`, inspected the issue #2
  deliverables (`literature/papers.md`, `literature/search-log.md`) to match the house
  format and quality bar, branched from an up-to-date `main`.
- Why: the workflow requires the plan to exist before the work, and issue #2 already set
  a standard for this repo's literature output that this review should not fall below.
- Result / what I found: working tree clean; `refs/` already exists as the source cache
  convention; the deliverable path in the issue carries the stale `/CrowdSimulation`
  prefix and needs correcting.
- Next step: verify the two supervisor-assigned papers from primary sources.

### 2026-09-12 — anchor papers verified; the two supervisor papers turn out to be one citation chain
- What I did: verified Wu et al. (2024) from the ACL Anthology landing page and the
  full PDF (cached + `pdftotext`-extracted to `refs/`), and Wang et al. (2015) from the
  RePEc record for *Physica A* 428:396-409.
- Why: the issue requires every field confirmed from a primary source, and Wu et al. is
  the designated hub for the Topic 1 citation sweep.
- Result / what I found: Wu et al. §6.1 states "We follow Wang et al. (2015) to simulate
  EE in a grid environment" — the supervisor's two papers are **one chain**, not two
  independent leads. Also extracted the real Table 2 numbers, which matter: the
  evacuation case study's effect is much weaker than the paper's prose suggests
  (see the criticism recorded in `topic1-llm-conflict.md`).
- Next step: forward citation sweep on Wu et al.

### 2026-09-12 — forward citation sweep surfaces the closest prior work to this FYP
- What I did: Semantic Scholar citations API on Wu et al.; 58 citing papers enumerated.
  The arXiv-id route returned HTTP 429 (same rate-limiting issue #2 hit); the DOI route
  worked.
- Why: issue protocol step 4 requires checking both citation directions.
- Result / what I found: **Zhang, Andelfinger, Tan & Cai, ACM TOMACS 2026, "Sense, Think,
  Act, Reflect: Distilling Fast and Interpretable Decision Functions from LLM-Driven
  Crowds"** — Decision Function Distillation, demonstrated on crowd evacuation, motivated
  by LLM inference cost limiting crowd size. This is roadmap steps 3-4 of this FYP,
  already published, by a group that includes two NTU authors. Flagged to the supervisor
  in an issue comment rather than buried in the review.
  ACM DL 403s to automated fetches (same dead end as issue #2), so the abstract was
  verified via the Semantic Scholar record (paper is CC-BY) and the BibTeX from the
  second author's own publications page.
- Next step: Topic 1 breadth, then Topic 2.

### 2026-09-12 — Topic 1 and Topic 2 candidate sets assembled
- What I did: ran the issue's suggested queries plus follow-ups; verified GameChat
  (MRS 2025), Abdelnabi et al., Piatti et al. (GovSim, NeurIPS 2024), NegotiationArena
  (ICML 2024), Chen et al. (MAPF); on the Topic 2 side Yamamoto et al. (TR-B 2019),
  Moeller et al. (eLife 2023), Echeverria-Huarte et al. (Nat. Comms. 2026), and the
  Julich data guidance paper.
- Why: the issue wants breadth across both topics with every entry primary-source verified.
- Result / what I found: two things worth calling out.
  (a) **GameChat** (Mahadevan, Zhang & Chandra, IEEE MRS 2025) is almost exactly this
  FYP's proposed scenario — LLM agents in *natural-language dialogue* resolving who
  yields in doorways and corridors, with a deadlock-freedom guarantee.
  (b) **A real dataset exists.** The Julich Pedestrian Dynamics Data Archive publishes
  open trajectory data from controlled corridor/bottleneck experiments, and
  Echeverria-Huarte et al. deposit raw trajectories on Zenodo. This is the "materially
  changes the validation plan" case the issue asked to flag prominently.
  Piatti et al.'s **title changed between the arXiv preprint and the NeurIPS version**
  ("Sustainability Behaviors" -> "Sustainable Cooperation"); recorded because citing the
  preprint title would misattribute the published paper.
  APS (Phys. Rev. E) 403s to automated fetches — recorded as a dead end.
- Next step: close the remaining Topic 2 gap on decision-level (not physics-level) work,
  then write the deliverables.

### 2026-09-12 - deliverables written, issue path corrected, README status added
- What I did: wrote the four deliverables under `literature/llm-conflict-resolution/`,
  corrected the stale `/CrowdSimulation/` prefix in the issue #8 body itself (CLAUDE.md
  instructs this), and added a "Current focus" roadmap-status table to `README.md`.
- Why: the issue's deliverable list is the contract; CLAUDE.md says README carries the
  live status of each roadmap step, and it still described only the on-hold Phase 1.
- Result / what I found: 12 papers reported within 2016-2026 against a target of 10
  (Topic 1: 7, Topic 2: 5), plus the two supervisor-assigned anchors marked as assigned
  rather than found. 10 of the 12 are peer-reviewed. I deliberately did **not** rewrite
  the README's Phase 1 framing - out of scope for this issue.
- Next step: verification pass per workflow section 5b.

## Open questions / risks

- **Zhang et al. (TOMACS 2026) is cited from its abstract, not its full text.** ACM DL
  blocks automated access. Nothing in the review depends on a number from it, but before
  the FYP report cites its *results* the PDF should be pulled through the NTU library.
  This is the single biggest gap in the review.
- **The project's position relative to Zhang et al. is unresolved.** I set out what I
  think is genuinely left (validation against human data; deriving rather than assuming
  the priority ordering; scale), but that is my reading of the literature, not a
  supervisor decision.
- **Whether the Julich archive actually contains clean two-person head-on encounters is
  unconfirmed.** The archive certainly has bidirectional corridor data, but most series
  are many-participant flows. Isolating dyadic encounters may need filtering and the
  yield may be low. Worth checking before step 5 is planned around it.
- **Two relevant papers were dropped for verification failure, not irrelevance**
  (Corbetta et al. 2016, Phys. Rev. E; the Springer gaze-cues paper). Both are on topic.
  Someone with institutional access should retrieve them.
- **One promising lead could not be located at all** - a head-on avoidance experiment
  with 32 participant pairs and a cost-benefit decision framework, described in a search
  summary but never traced to a primary source. It is cited nowhere; see `search-log.md`.
- **Recency vs. peer review**, flagged at the start, was handled by labelling and pairing
  rather than a firm rule. 10 of 12 entries are peer-reviewed, a better ratio than I
  expected, but the supervisor may still want preprints excluded from the report.
- **The gender-bias flag from `run01` is still unresolved** and now has a literature
  hook: Ashery et al. show population-level bias emerging from individually unbiased LLM
  agents. That is a plausible mechanism for the same artefact, and may be worth raising
  as one combined discussion point rather than two separate ones.

## Summary

**What changed.** Added `literature/llm-conflict-resolution/` containing
`topic1-llm-conflict.md`, `topic2-sociological-grounding.md`, `refs.bib` and
`search-log.md`; cached 22 source files under `refs/`; corrected the stale deliverable
path inside issue #8; added a roadmap-status section to `README.md`. No code, no dataset
generation, no simulation work - the standing supervisor instruction was respected.

**Count against target.** The issue asked for 10+ papers from 2016-2026 beyond the two
supervisor-assigned ones. **12 are reported** - Topic 1: 7 (6 peer-reviewed, 1 preprint),
Topic 2: 5 (4 peer-reviewed, 1 preprint). Both supervisor papers are included and marked
as assigned rather than as search results. Both preprints are labelled `[non-archival]`,
and neither is the sole support for any claim.

**Three findings the supervisor should see before roadmap step 2:**

1. **The two assigned papers are one citation chain.** Wu et al. (2024) section 6.1:
   "We follow Wang et al. (2015) to simulate EE in a grid environment."
2. **A real human dataset exists** - the Julich Pedestrian Dynamics Data Archive
   (CC-BY, doi:10.34735/ped.da), including bidirectional corridor trajectories. The
   project plan assumed this probably would not exist. Roadmap step 5 can now be
   quantitative. Flagged at the top of `topic2-sociological-grounding.md` as required.
3. **Roadmap steps 3-4 have largely been published already** - Zhang, Andelfinger, Tan
   and Cai, ACM TOMACS 2026, distil interpretable decision functions from LLM-driven
   crowds, demonstrated on evacuation, with two NTU co-authors. The FYP needs a stated
   position relative to it; my reading of the remaining gap is in
   `topic1-llm-conflict.md`, flagged there as an assumption needing sign-off.

**How it was verified** (workflow section 5b, research-task verification):

- **Every entry uses all ten template fields.** Checked mechanically: 8/8 entries in
  Topic 1 and 6/6 in Topic 2 carry every field, no blanks.
- **Every entry is `Verified: yes`** with the route stated. Three entries (Zhang, Ashery,
  Piatti) are verified at *abstract level only*, and each says so explicitly in its own
  Verified field rather than implying full-text reading.
- **Bibliographic fields double-checked.** For all 7 DOI-bearing entries, author lists,
  titles, venues, volumes and pages were independently re-fetched from the Crossref API
  and compared against the publisher page.
- **BibTeX keys cross-checked mechanically** - all 14 keys cited in the reviews exist in
  `refs.bib`; no dangling references.
- **Quantitative claims are sourced or marked.** 12 `[unverified]` markers are present
  where a number could not be traced to a primary source, rather than the number being
  quietly dropped or asserted.
- **Sources cached** - 22 files in `refs/`, so every claim can be re-checked later.
- **Dead ends recorded, not hidden** - ACM DL, APS, Springer, nature.com, science.org,
  ScienceDirect, ADS, DBLP and the Semantic Scholar arXiv route all refused automated
  access. Each is logged with its workaround or, where there was none, the affected
  candidate was **rejected rather than cited unverified** (2 papers dropped this way).

**One process note worth carrying forward:** the Wu et al. PDF came back as unreadable
binary through the fetch tool. Downloading it and running `pdftotext` locally is what
surfaced the review's most important criticism - that Table 2's evacuation-speed margins
(100.0 vs 99.8 escaped at round 50) are far thinner than the paper's prose implies, and
that the authors themselves concede the evacuation metrics are inadequate. A summary of
that PDF would have reproduced the paper's own framing uncritically.
