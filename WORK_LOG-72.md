# Work Log — Issue #72: [Docs] RF-16: record the 2026-10-22 resolution design and write docs/resolution.md

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/72
**Branch:** docs/72-record-resolution-design
**Started:** 2026-10-22

## Understanding the issue

On 2026-10-22 the user replaced the Step 1 design of track #55. The first version of RF-2 (#57)
asked each agent for a fixed menu (`priority`, `side`, `speed`, `back_up`), which framed every
meeting as "who goes first". The new design asks an agent what it physically does (`steps`), what
it is trying to do (`intent`) and, privately, why (`reason`); it can signal, and in the talk
condition speak. There is no priority field: who went first is measured in the replay. The
description an agent is given follows what a person would perceive (a 75° half-angle cone to
10 m, full detail within 5 m, hearing from any direction). Agents are prompted only when a
conflict is predicted and again only on something new. The work then goes one scenario at a
time, in rounds.

The user decided this on their own authority; it does not need the supervisor's sign-off. Every
later RF issue builds on it, so this issue writes it down once, in one place, before any code:

1. `llm_negotiation/docs/resolution.md`: the specification, D1 to D17, as given in the issue.
2. `CLAUDE.md`: one paragraph under "Current task"; items 4, 7 and 8 of "Pending sign-offs"
   marked as the user's decisions of 2026-10-22; items 1, 2, 3, 5, 6 unchanged; one more
   constraint (no reply format may ask who goes first).
3. `architecture.md` section 8: one decision-record entry per D1 to D17.
4. Both READMEs: the RF list in #55's new order, with RF-16 to RF-25.
5. `parameters.md`: the sourced values (75°, 10 m, 5 m) and the placeholders, with cached
   source excerpts in `refs/`.

No code, config or template changes.

**Assumptions:**
- A1. **Base branch.** `origin/main` is still at the initial commits (PR #3). PR #71 (#56) was
  merged into `docs/supervisor-meeting-notes-issues-24-to-52`, not into `main`, and branches in
  this repository stack on the previous issue's branch. So this branch is cut from
  `docs/56-record-resolve-first-direction` (whose tree is the same as the merge base's) and the
  PR targets it. See the first progress entry for how I found this out.
- A2. **Numbering in the decision record.** `architecture.md` numbers this project's own
  decisions DD (each needing the supervisor's sign-off) and the supervisor's points SV. D1 to
  D17 are neither: they are the user's decisions, which need no sign-off. They keep the numbers
  D1 to D17 that #55 and the later issues already use (for example "`docs/resolution.md`, D15
  to D17"), in a new subsection 8.7, with a sentence saying that D is not DD.
- A3. **"Do not add or drop any decision."** `resolution.md` carries the issue's specification
  as written. Where I found a caveat in a source (for example on the 75°), it goes in
  `parameters.md` and in this log's open questions, not into the decisions.
- A4. **Source names in `refs/`.** Existing caches are prefixed by issue (`si1_`, `si32_`). The
  new ones are prefixed `rf16_`.

## Plan

1. Read the prescribed files: `CLAUDE.md`, `README.md` roadmap, `llm_negotiation/README.md`,
   `architecture.md` section 8, `parameters.md` (done).
2. Fetch and cache the three sources: Moussaïd, Helbing & Theraulaz 2011 (arXiv 1105.2152);
   Rio, Dachner & Warren 2018 (abstract); Wirth, Dachner, Rio & Warren 2023 (abstract). Check
   each number against the cached text.
3. Write `docs/resolution.md` (D1 to D17), every placeholder marked.
4. `parameters.md`: a new section for the resolution design's values.
5. `architecture.md`: subsection 8.7, D1 to D17, and the file's opening paragraph.
6. `CLAUDE.md`: the paragraph, the three decided items, the constraint.
7. Both READMEs: the RF list in #55's order.
8. Verify: every D present, every placeholder marked, every number against its cached source,
   items 1, 2, 3, 5, 6 unchanged, no code or config touched.
9. Push, PR against `docs/56-record-resolve-first-direction`, comment on #72.

## Progress log

### 2026-10-22 — Base branch, and a checkout of main that showed it was the wrong base
- What I did: followed the workflow's step 0 (`git checkout main && git pull`), then created the
  branch. `main` fast-forwarded to `152da57`, the merge of PR #3, and `llm_negotiation/` and many
  files in `refs/` showed as untracked.
- Why: the workflow says to start from an up-to-date `main`.
- Result / what I found: `origin/main` really is at PR #3. PR #71 merged into
  `docs/supervisor-meeting-notes-issues-24-to-52`; the branches stack (memory note). The
  "untracked" files were all ones that docs/56's `.gitignore` ignores but main's older one does
  not (`llm_negotiation/runs_mock/`, `llm_negotiation/views/`, some PDFs). A batch check found
  none of them in docs/56's tree, so nothing could be overwritten and nothing was lost. I reset
  the new, still empty branch onto `docs/56-record-resolve-first-direction` with
  `git checkout -B`. The working tree is clean.
- Next step: the work log's first commit, then the sources.

### 2026-10-22 — The three sources, fetched and checked
- What I did: downloaded Moussaïd, Helbing & Theraulaz 2011 from `arxiv.org/pdf/1105.2152`
  and extracted its text with pypdf 6.16.2. Got the Rio et al. 2018 and Wirth et al. 2023
  abstracts from the Europe PMC REST API (PubMed's web pages now answer scripts with a cookie
  wall). Checked the PNAS citation (108(17), 6884–6888) in Europe PMC too, since I had first
  typed it from memory.
- Why: task 5 asks for the sourced values with cached excerpts, and every number must be read
  in the cached copy, not recalled (`parameters.md`'s rule).
- Result / what I found:
  - **Moussaïd 2011:** the line the issue quotes is there, word for word: Fig. 2's caption,
    "The model parameters are τ=0.5s, φ=75°, dmax=10m, k=5.103, vi0=1.3 m/s" (extract lines
    555-562). φ is the half-angle: "the vision field of pedestrian i ranges to the left and to
    the right by φ degrees" (134-140). dmax is "the 'horizon distance'" (163). Occlusion is part
    of the model: "Pedestrian p4 is hidden by pedestrian p2 and, therefore, not visible" (542-543).
    **Caveat:** these are a model's parameters, set so that simulations match corridor
    experiments, not measured limits of vision; and the same paper uses **φ=45°, dmax=8m** for
    its high-density street simulations (599-601). The published PNAS version could not be
    read: its PMC full text is not available for download ("the publisher of this article does
    not allow"), and Europe PMC's PDF route answered 403. The arXiv copy says "Article accepted
    for publication in PNAS".
  - **Rio 2018 abstract:** "weights that decay exponentially to zero by 5 m". **Caveat:** the
    same sentence models the neighbourhood as "a circularly symmetric region", and influence
    did not decrease "with lateral position (eccentricity)". So this source supports the 5 m but
    not a cone. And it measured following a virtual crowd's speed and heading, not avoiding
    someone.
  - **Wirth 2023 abstract:** "Our results rule out a topological neighborhood", best explained
    by "a visual neighborhood", "the optical motions of all visible neighbors". This supports
    both "no fixed count" and describing only those who are visible (occlusion).
  - **Licence.** The arXiv copy has arXiv's non-exclusive distribution licence, not an open
    one. The repository is mixed here (issue #52 tracked arXiv copies; issues #35 to #37 kept
    unlicensed copies out of git). I took the cautious route of issues #35 to #37: the full PDF
    and text are local and listed in `.gitignore`, and a tracked excerpt file
    (`refs/rf16_moussaid2011_excerpts.txt`) holds every cited passage verbatim, each with its
    line number in the full extract. Abstracts are tracked, as Bohannon 1997's is.
- Next step: `docs/resolution.md`.

## Open questions / risks

(filled in as the work goes)

## Summary (fill in at the end)

