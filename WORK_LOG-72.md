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

### 2026-10-22 — `docs/resolution.md` (task 1)
- What I did: wrote D1 to D17 from the issue's "Specification" section. Added a short opening
  (status: the user's decisions, needing no sign-off; what the design replaces; where the
  values' sources are), pointers to the issue that builds each part ("RF-2, #57"), and, at the
  end, the track's constraints repeated from #55.
- Why: the issue says to write it "in the docs' usual style" and not to add or drop a decision.
  The pointers and the constraints are not decisions: the first are #55's issue list, the second
  #55's own constraint list.
- Result / what I found: two layout changes only. D3's three conditions are a table, and D13's
  trace from a rule to its raw replies is drawn as a small diagram; their words are the same.
  D2's left/right and "never in a description" paragraph is split into bullets. D15 adds one
  status sentence: no round cap is recorded yet. Every placeholder is marked
  **`[placeholder]`** (hearing range, signal range, change thresholds), in D2, D5 and D12.
- Next step: `parameters.md`.

### 2026-10-22 — `parameters.md` section 8 (task 5)
- What I did: a new section 8 rather than rows in sections 2 and 3, because those two list the
  quantities of shipped configs, and a test (`test_the_parameters_document_lists_every_placeholder_and_every_source`)
  checks section 3 against the configs. These values are in no config yet. 8.1 lists the
  sourced values with locators and caveats, 8.2 the placeholders, 8.3 the prompt guards
  (1 s, 3 decision points, the per-encounter cap) as `[design]`. The three sources were added
  to section 6.
- Why: task 5. The guards are not asked for, but `parameters.md` gives every number a tag,
  and these are numbers.
- Result: `tests/test_crowd_scenarios.py` passes (pytest is not installed globally here, so I ran
  it in a throwaway `uv run --no-project --with pytest==9.1.1 --with PyYAML==6.0.3 --with
  matplotlib==3.10.8` environment, the pins of `requirements.txt`).
- Next step: the decision record.

### 2026-10-22 — Decision record, `CLAUDE.md`, both READMEs (tasks 2 to 4)
- What I did:
  - `architecture.md`: subsection 8.7, one bold-lead entry per D1 to D17, each "(the user,
    2026-10-22)", and a note that D is not DD (A2). The opening paragraph names 8.7. SV2 said
    "which LLM gives the reference ... is pending (#55, decision 7)"; I added that the user
    decided it on 2026-10-22 (both, D8), so the record does not contradict itself.
  - `CLAUDE.md`: the paragraph under "Current task"; the new constraint; items 4 and 7
    "Decided by the user, 2026-10-22" and item 8 "Lifted by the user, 2026-10-22", each with
    the answer; the list's opening sentence, which said "None of these has been given", now
    says which items are pending and which are decided. Two small factual updates beside them:
    the issue range is #56 to #81 (RF-1 to RF-25), and the paid-run constraint says "phase or
    round", as #55 now does. Items 1, 2, 3, 5 and 6 are byte-for-byte unchanged (checked in the
    diff).
  - `README.md`: one row per RF issue in #55's order, Part 1 then Part 2 by round; a line in
    "Current focus"; the "Status of that instruction" box now ends with the user lifting it.
  - `llm_negotiation/README.md`: a paragraph on the design and the RF list in order, under
    "Direction since October 2026"; `resolution.md` added to "Documents".
- Result / what I found: `gh issue list` shows **#56 still open**, although PR #71 is merged:
  `Closes #56` fires only on a merge into the default branch, and PR #71 went into the stacked
  branch. So the README says RF-1 is "delivered ... merged into the stacked branch, not yet
  into `main`". The same will happen to #72 (Q4).
- Next step: verification.

### 2026-10-22 — Verification
- What I did:
  1. A script compared `resolution.md` with the issue body: all 17 headings present; every code
     span and every number with a unit present; all 27 table rows present (after ignoring the
     bold I added to `[placeholder]` and the issue numbers I added); D1's JSON and D2's block
     identical character for character; every sentence of the specification present, except
     the D3 conditions and the D13 trace, which are the two layout changes above (checked by
     eye: same content).
  2. `git diff --stat` against the base: only docs, `refs/` and `.gitignore` changed; no code,
     config or template.
  3. Every number in `parameters.md` section 8 re-read in the cached files, and the line
     locators corrected where my first draft was off by a line or two.
  4. The full test suite, on the same throwaway environment: **exit code 0, no failure**. (The
     count line was not printed: `pytest.ini` already adds `-q`, and my extra `-q` made it
     `-qq`.) Expected, since no code changed; it confirms the `parameters.md` test still reads
     section 3 correctly with section 8 added.

## Open questions / risks

- **Q1. The 75° rests on a model's parameter, and a second source cuts against the cone.**
  Moussaïd et al. 2011 chose φ=75° and dmax=10 m for their simulation of a 1.75 m corridor, and
  used φ=45°, dmax=8 m for their dense street. Rio et al. 2018 found influence did not depend
  on lateral position, in "a circularly symmetric region". Neither undoes D2 or D12 (the user's
  decisions; the issue says not to change them), and the 75° is a reasonable choice for the
  head-on round. But a report should call it "the vision field of a pedestrian model fitted to
  corridor data", not a measured field of view. Raised here for the user; RF-17 may want a
  sentence on it.
- **Q2. The detail range comes from following, not avoiding.** Rio et al. measured a walker
  matching a virtual crowd's speed and heading. The specification already says so ("measured
  while walking *with* a crowd"). Using it for how much is *said* about a person is this
  design's choice.
- **Q3. Published PNAS version of Moussaïd 2011 not read.** Only the accepted manuscript
  (arXiv v1). PMC's full text is not downloadable for this publisher and Europe PMC's PDF route
  gave 403. A browser can fetch it in minutes, if the user wants the final wording checked.
- **Q4. Issues #56 and #72 will not close themselves.** Their PRs merge into stacked branches, so
  `Closes #N` does not fire. Close them by hand, or when the stack reaches `main`.
- **Q5. Licence route for the arXiv copy.** I kept the full PDF and text out of git and tracked
  verbatim excerpts. Issue #52 tracked full arXiv copies instead. If the user prefers that, it
  is two lines of `.gitignore`.
- **Q6. Edits slightly beyond the task list**, each to keep the files consistent: SV2's note in
  `architecture.md`, the issue range and "phase or round" in `CLAUDE.md`, the "Status of that
  instruction" box in `README.md`, the design values in `parameters.md` 8.3. Easy to revert if
  unwanted.
- **Q7. The hearing and signal ranges have no value at all**, not even a round one. The
  specification gives none, so none was invented; RF-17 (#73) has to choose them.

## Summary (fill in at the end)

**What changed.** The user's resolution design of 2026-10-22 is written down once, in one
place, before any code:

- `llm_negotiation/docs/resolution.md` (new): D1 to D17, the specification every later RF
  issue points to, with every placeholder marked.
- `llm_negotiation/docs/architecture.md`: subsection 8.7, one decision-record entry per D1 to
  D17, each "the user, 2026-10-22", numbered D (not DD: no sign-off needed).
- `CLAUDE.md`: Step 1 follows `resolution.md`; pending items 4, 7 and 8 recorded as the user's
  decisions of 2026-10-22; items 1, 2, 3, 5 and 6 unchanged and still PENDING; the constraint
  that no reply format may ask who goes first.
- `README.md` and `llm_negotiation/README.md`: the RF issues in #55's order of work, Part 1
  then Part 2 by round, with RF-16 to RF-25.
- `llm_negotiation/docs/parameters.md`: section 8, the view half-angle (75°) and seeing range
  (10 m) from Moussaïd et al. 2011, the detail range (5 m) from Rio et al. 2018, "no fixed
  count" from Wirth et al. 2023, each with locator and caveat; hearing range, signal range and
  change thresholds as placeholders.
- `refs/`: the Moussaïd 2011 excerpts (the full copy is local only, by licence) and the two
  abstracts.

**Why.** Every later RF issue builds on this design, and `CLAUDE.md` still listed three of the
user's decisions as pending.

**How it was verified.** A script checked `resolution.md` against the issue's specification
(all headings, code spans, numbers, table rows and blocks present; two layout changes, checked
by eye). Every number in `parameters.md` was re-read in the cached sources. The diff touches no
code, config or template. The full test suite passes.

**Not done / for the user:** Q1 to Q7 above, in particular the caveat on the 75° (Q1) and that
#56 and #72 will need closing by hand (Q4).

