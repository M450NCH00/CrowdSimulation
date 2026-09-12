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

## Open questions / risks

- **Recency vs. peer review tension.** Topic 1's most relevant work is 2024–2026 and much
  of it is arXiv-only. Over-weighting preprints would weaken the report; excluding them
  would miss the closest prior work. Handling this by labelling and pairing, but the
  supervisor may want a firmer rule.
- **Whether a real behavioural dataset exists at all** for two-person narrow-passage
  conflict. If none does, the project's validation step falls back entirely to
  sociological literature, which is a weaker form of validation and should be surfaced
  to the supervisor early rather than discovered at validation time.

## Summary (fill in at the end)

<pending>
