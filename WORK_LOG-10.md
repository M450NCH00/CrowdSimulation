# Work Log — Issue #10: [Docs] Select papers for FYP introduction + Draft sample introduction (Assignment 1)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/10
**Branch:** `docs/10-intro-paper-selection-draft`
**Started:** 2026-09-13

## Understanding the issue

After the second supervisor meeting the research question is: *can LLMs resolve
conflicts by communicating with each other, and does that communication contain a
reusable pattern* that a crowd simulation can apply later without re-running the
LLM-to-LLM exchange? Assignment 1 needs an introduction built on that question.

The issue has two parts:

1. **Paper selection** — choose 3–5 papers **only** from the issue #8 literature review
   (`literature/llm-conflict-resolution/`) that together cover Background, Research gap
   and Study introduction, then write an honest coverage assessment. If coverage is
   insufficient, stop and write `open-gaps.md` only.
2. **Introduction draft** — ≤12-word title, ≤500-word body, IEEE referencing, fixed
   three-part structure, every factual claim cited, no web search, no fabricated
   findings, uncertain support marked `[needs verification against full text]`.

`open-gaps.md` is always produced.

### Assumptions (flagged per CLAUDE.md)

1. **Base branch.** The workflow says branch from `main`, but the literature this issue
   must draw on exists only on `docs/8-lit-review-llm-conflict-resolution` (PR #9, not
   merged). The issue itself names that branch. I branched from its tip (`c87153b`) and
   the PR will target that branch so the diff contains only issue #10's work.
2. **Deliverable location.** The issue gives filenames but no directory. I am placing
   them in `literature/llm-conflict-resolution/assignment1-intro/`, next to the sources
   they cite. Trivial to move if the user prefers a different folder.
3. **What counts as a "source".** The review files summarise papers, but where a full
   text is cached in `refs/` (Wu et al., GameChat, Moeller et al.) I check claims against
   that text as well, not just the summary. This is still inside the sourcing rule, since
   these are the files the review itself cites, and no new papers are introduced.

## Plan

1. Branch + work log (this file), commit.
2. Read both topic files, `refs.bib` and the issue #8 work log; list every candidate
   paper against the three introduction components.
3. Re-check every finding I intend to use against the cached primary source in `refs/`,
   not just against the review's summary. Record any discrepancy.
4. Select 3–5 papers; write `paper-selection.md` with the per-paper template and an
   honest coverage assessment.
5. If coverage is sufficient, draft `introduction-draft.md`; count words mechanically;
   run the issue's quality checklist line by line.
6. Write `open-gaps.md` (always).
7. Verify per workflow §5b; update README status; push; open PR against the issue #8
   branch.

## Progress log

### 2026-09-13 — branch created, work log seeded
- What I did: read issue #10 and `github_issue_workflow.md`; confirmed the working tree
  was clean and `docs/8-lit-review-llm-conflict-resolution` matched its remote; created
  `docs/10-intro-paper-selection-draft` from it.
- Why: the literature is not on `main` yet (see Assumption 1).
- Result / what I found: 14 papers in the review (12 in the 2016–2026 window + 2
  supervisor-assigned); full text cached for 3 of them (Wu, GameChat, Moeller).
- Next step: map candidates to introduction components and re-check claims against
  `refs/`.

### 2026-09-13 — claims re-checked against cached sources; 5 papers selected
- What I did: mapped all 14 review papers to the three introduction components.
  Re-checked every finding I intended to use against `refs/`: Wu full text (§1,
  §6.1–6.2, Table 2, Limitations), GameChat v2 full text (§I, §IV-C, §IV-E, §V-B,
  Table III), Moeller article HTML (Results, Fig. 2A, participants), and the Ashery,
  Zhang and Wang abstracts. Wrote `paper-selection.md`.
- Why: the issue forbids extrapolating findings, and the review's summaries are
  secondary, so a claim is only as good as the primary text behind it.
- Result / what I found:
  - **Selected:** Wu [1], Zhang-DFD [2], GameChat [3], Ashery [4], Moeller [5].
  - **Discrepancy in the issue #8 review:** it says GameChat evaluated only 2 agents,
    but cached arXiv v2 has 3/4/5-agent results (Table IV). Recorded in
    `paper-selection.md`; I did not edit the issue #8 file, which is out of scope here.
  - **Moeller percentages are derived.** The paper states counts (10, 5 and 4 of 19);
    26% and 21% are the review's rounding. The draft uses counts.
  - **Hard choice:** Wang 2015 is the only paper that says *why* crowd simulation
    matters, but a sixth reference breaks the cap. I kept Wu because it gives
    full-text-verified cost evidence for the gap. The alternative is recorded.
  - **Framing decision:** Zhang-DFD already distils LLM behaviour into rule code for
    crowd evacuation, so the gap cannot honestly be "nobody extracts patterns". It is
    stated as "not from LLM-to-LLM conflict dialogue, and not checked against humans",
    and the human-validation half rests on an abstract, so it carries
    `[needs verification against full text]`.
- Next step: coverage is sufficient (with that condition), so draft the introduction.

### 2026-09-13 — introduction drafted; over the word limit twice, then a wording error caught
- What I did: wrote `introduction-draft.md` with a sentence-by-sentence source map and
  the issue's checklist below the reference list (marked "not for submission"). Counted
  words with a script over explicit `BODY START/END` markers, counting headings,
  citation tokens and the verification marker, as Word would.
- Why: the issue sets ≤500 words and every claim cited; checking by eye is not reliable
  for either.
- Result / what I found:
  - **First draft: 560 words.** Cut to 517, then to 496. The cuts were wording only; no
    cited finding was dropped.
  - **Caught an overstatement while re-checking.** The draft said GameChat's urgency
    ranking was "set by the designers rather than discovered". Re-reading §IV-C and
    Table II: the prompt does *not* give the LLM the ordering. The LLM infers urgency
    from free-text tasks, and the designers only define the ground truth it is scored
    against. Rewrote it as "success is judged against an urgency ranking the designers
    fixed in advance". The issue #8 review makes the same overstatement; logged as a
    correction in `open-gaps.md`, not fixed in that branch's files.
  - Also changed "a standard collision-avoiding controller" to "an existing" one: the
    paper does not call MPC-CBF standard.
  - **Final: title 11 words; body 494 words** with the marker (489 without); sections
    151 / 151 / 192 against targets ~150–200 / ~100–150 / ~150–200. Research Gap is
    slightly over its ~150 guide; the total is within limit.
  - Mechanical checks: citations first appear in order [1]→[5]; the cited set equals the
    reference list. Every sentence without a citation was listed and checked. Each is a
    transition, the project's own aim or scope, or reasoning from cited findings, and
    each is labelled in the source map.
- Next step: write `open-gaps.md`.

### 2026-09-13 — open-gaps.md written
- What I did: listed 5 items to resolve before submission (G1–G5) and 5 nice-to-have
  unsourced claims (N1–N5), plus the 3 corrections to the issue #8 review.
- Why: the issue requires this file always, and requires that unsupported claims go here
  rather than into the draft.
- Result / what I found: G1 (Zhang full text) is the only blocking item. N1 matters
  most: no paper in the review shows a *crowd simulation* (as opposed to robots)
  stalling on a conflict, so the draft's deadlock sentences talk about "agents" and
  "doorway tests", not crowd simulation.
- Next step: verification pass per workflow §5b, README status, push, PR.

### 2026-09-13 — verification pass (workflow §5b); README status added
- What I did: re-read the draft end to end against the source map; re-ran the word count
  and citation checks; checked the issue's acceptance criteria one by one (listed in the
  Summary). Added an "Assignment 1 introduction" note under README's "Current focus".
- Why: §5b requires every number to be traced and every task answered or explicitly
  marked incomplete.
- Result / what I found: three small mismatches between the checklist or source map and
  the final wording (a quoted transition that no longer existed; the G5 row still
  describing the pre-edit sentence; the word-count item not stating the number). All
  fixed. Every number in the body (18; 50%; 100% as "every scenario"; 2.8 s; 100
  agents; $1,000; 10/19, five, four; 10,000) was traced: all except 10,000 go to a
  table, section or passage, and 10,000 is the project target, not a claim.
- Next step: push, open PR against the issue #8 branch, comment on the issue.

### 2026-09-13 — Zhang et al. full text supplied by the user; G1 resolved, draft revised
- What I did: the user shared the Zhang et al. PDF (TOMACS "Just Accepted" version). I
  found the same file in the parent FYP folder, copied it to `refs/zhang2026_dfd.pdf`
  (CC-BY 4.0, so redistribution is permitted) and extracted text to
  `refs/zhang2026_dfd.txt`. Read it in full, then string-matched every quote I use
  against the extracted text.
- Why: G1 was the one blocking item. The research-gap paragraph rested on an inference
  from the abstract.
- Result / what I found:
  - **The gap claim holds.** All datasets come from the LLM-driven simulation and
    fidelity is measured against it (§5.1). §6.1: "the validity of the distilled
    function depends directly on the reference data". Real-world data appears only as
    an alternative (§6.2).
  - **A nuance the abstract hid, and my first draft did not account for:** the ground
    truth is Wu et al.'s simulation, which includes a communication phase, and the
    agents' conversations feed insight generation (§4.2). So "DFD ignores communication"
    would have been wrong. The final functions use only numerical perception features
    (§3, Fig. 14), and interaction features are future work (§7). The gap sentence
    already says "conflict dialogue … validates against people", so it survives; the
    nuance is recorded in source-map row G7.
  - **G2 resolved as a side effect.** §1 opens with evacuation simulation being
    "essential for emergency planning and building design", which covers why crowd
    simulation matters without Wang 2015 or a sixth reference.
  - **New quantitative evidence:** §5.5 gives ≈ 1 day per LLM-driven run vs ≈ 1 minute
    for the distilled function (100 agents, §5.1).
  - **Two more errors in the issue #8 review:** it says two of the four authors are at
    NTU, but all four are listed at NTU. It also says DFD is "motivated by the same
    10,000-agent scalability constraint", but the paper never mentions 10,000. Added to
    the corrections in `open-gaps.md`, with a note that the review's Zhang entry can be
    upgraded to full-text-verified.
- Draft changes:
  - Background: added "Such simulations inform emergency planning and building design
    [2]".
  - Research Gap: replaced the marked sentence with the §5.5 run-time comparison and
    the §6.1 validity statement. Changed "entirely" to "directly" to match the paper's
    wording. Cut the Wu $1,000 sentence to stay under 500; Zhang's measured run times
    make the cost point more directly.
  - Reference [2] is now "to be published" (no volume or article number yet).
  - Body is **494 words** with no markers (157 / 147 / 190). Citation order is still
    [1]→[5], matching the reference list.
- Also updated: the source map (full-text locations for all [2] rows), the Zhang entry
  and coverage assessment in `paper-selection.md` (now "sufficient", no condition), and
  in `open-gaps.md` G1/G2 marked resolved, G3 and N2 updated. README status updated.

### 2026-09-13 — aim widened to include human validation; pattern examples made concrete
- What I did: at the user's request, (1) rewrote the aim sentence to include a third
  question, "whether that pattern matches how people resolve the same conflicts";
  (2) replaced "such as who gives way and why" with "such as a right-of-way ordering [3]
  or turn-taking [5]"; (3) replaced "Extracted patterns will be validated against such
  sociological evidence, treating the human benchmark as a mix of strategies, not one
  rule" with "A humanlike pattern should reproduce this mix of strategies, not a single
  rule", which avoids repeating validation now that the aim states it.
- Why: the research-gap paragraph argues that human validation is the missing piece, so
  an aim without it did not answer the gap. The user also asked what "pattern" means;
  naming the two rule forms the cited papers actually show makes the term concrete at
  no word cost.
- Wording choice, flagged: the aim says "how people resolve the same conflicts", not
  "real human data". The only human evidence cited in the introduction is Moeller [5]
  (non-spatial). Using the Jülich trajectories as ground truth is still awaiting
  supervisor sign-off, and whether they contain clean two-person encounters is
  unconfirmed.
- Result: body **496 words** (157 / 147 / 192). Citation first-appearance order is still
  [1]→[5]; the new [3]/[5] citations are repeats. Source map rows S1, S1b and S4 and the
  objective/scope checklist items were updated.

### 2026-09-13 — revision 4: paragraph-only structure with a gentler opening; references renumbered
- What I did: at the user's request, removed the three section headings, since the Word
  submission is continuous prose, and rewrote the opening so it leads into the topic
  instead of starting on a definition. The opening now moves from why people's movement
  in an emergency matters ([Zhang] §1: evacuation planning, building design, exit
  placement) → how agent-based crowd simulation models it ([Zhang] §1, §2.2; [Wu] §6.1)
  → "These decisions can conflict" (congestion → two-agent doorway deadlock) → LLMs as
  "another way to model such decisions". The old separate conflicts sentence ("Local
  conflicts are harder still") was folded into that new second paragraph.
- Why: without headings the old first sentence ("In agent-based crowd simulation, each
  pedestrian is modelled…") dropped the reader straight into jargon, and each paragraph
  now has to carry its own transition.
- Additional references: **none added.** The user allowed more than 5 if needed. I
  considered Wang 2015 (stadium evacuation, casualties under panic) for a more vivid
  hook, but Zhang et al. §1, already cited and full-text verified, supports the opening,
  whereas Wang is abstract-only and would add a reference plus ~20 words.
- Consequences:
  - **IEEE renumbering.** The opening now cites Zhang first, so Zhang is [1] and Wu is
    [2]; GameChat [3], Ashery [4] and Moeller [5] are unchanged. Applied mechanically to
    the draft (in-text citations, reference-list order, source map), `paper-selection.md`
    (numbers and entry order) and `open-gaps.md`. Earlier entries in this log keep the
    old numbering.
  - **Clarity fix.** Once headings were gone, "In GameChat" had no antecedent (GameChat
    is never named in the prose). A first attempt, "Each such encounter needs a new LLM
    dialogue", overgeneralised a GameChat-specific figure, so it now reads "In that
    doorway study, each encounter needed…".
  - Trims to stay ≤500: dropped "GPT-4" and "three" from the exit-balancing clause,
    shortened the Moeller game description, shortened the DFD run-time clause, and cut
    the repeated "symmetric standoff that dialogue has been shown to break [3]" from P5
    (P2–P3 already establish it).
- Result: **497 words** with no headings (P1–P7: 52 / 58 / 75 / 138 / 63 / 66 / 45;
  background 185, gap 138, study 174). First appearance is [1]→[5]; the cited set equals
  the reference list. The source map was rebuilt per paragraph (P1a…P7), and every row
  was re-pointed to its source section.

## Open questions / risks

- ~~**The research gap depends on an abstract.**~~ Resolved 2026-09-13. Full text read;
  the claim holds (see the entry above).
- **Base branch is a stacked PR.** This branch is built on the unmerged issue #8 branch.
  If PR #9 changes before merging, this branch will need rebasing; if PR #9 is merged
  first, retarget this PR to `main`.
- ~~**Five-reference cap forced out the only "why crowd simulation matters" source.**~~
  Resolved 2026-09-13: Zhang et al. §1 covers it (G2).
- **GameChat citation vs version read.** Cited as IEEE MRS 2025, read as arXiv v2 (May
  2026). The section numbers and the 2.767 s figure need checking against the published
  version (G3).
- **Moeller is non-spatial.** The draft treats a touchscreen coordination game as an
  analogue of a hallway standoff and says so, but a marker may still see this as a stretch.
  No decision-level spatial yielding study exists in the review (N3).
- **CrowdGym is named without a citation** (G4). Whether an unpublished FYP report can be
  cited is for the supervisor to decide.
- **Voice.** The issue asks for the user's own academic voice. I wrote plain, paraphrased
  academic English, but the user should rewrite it into their own style before Turnitin
  submission. The work is theirs to submit, and phrasing generated by a model is not
  theirs.
- **Issue #8 review has two overstatements** about GameChat (agent count; "designer
  supplies the hierarchy"). Recorded in `open-gaps.md`; I did not edit the issue #8 files
  from this branch, to keep the PR scoped.

## Summary

**What changed.** Added `literature/llm-conflict-resolution/assignment1-intro/` with:
- `paper-selection.md` — 5 papers (Wu 2024, Zhang 2026, Mahadevan/GameChat 2025,
  Ashery 2025, Moeller 2023), each with the issue's template filled in, plus the
  evidence level checked, 9 considered-but-rejected candidates with reasons, and a
  coverage assessment: first **sufficient, conditional on the Zhang full text**; after
  the full text was read, **sufficient** with no condition.
- `introduction-draft.md` — 11-word title; 497-word paragraph-only body (after revision 4) in the required three-part
  structure; 5 IEEE references; a not-for-submission source map and quality checklist.
- `open-gaps.md` — 5 items to check before submission (G1 blocking, now resolved along
  with G2), 5 claims left out for lack of a source, and 6 corrections to the issue #8
  review.

Also added a status note to `README.md`. No papers were searched for; no code, dataset
or simulation work.

**Why.** Assignment 1 needs an introduction for the post-meeting-2 research question,
and the issue requires every claim to trace to the existing review.

**How it was verified.**
- *Word counts by script*, over explicit body markers: title 11; body 494 including
  headings, citation numbers and the verification marker (489 without). The first two
  drafts (560, 517) failed and were cut.
- *Citation integrity by script*: first-appearance order is [1]→[5]; the in-text set
  equals the reference-list set.
- *Uncited sentences listed by script* and each classified as a transition, the
  project's own aim or scope, or own reasoning; all are labelled in the source map.
- *Every number and finding traced to primary text in `refs/`*, not to the review's
  summaries: Wu full text, GameChat arXiv v2 full text, Moeller article HTML, and the
  Ashery, Zhang and Wang abstracts. This caught one overstatement in my own draft
  (GameChat's ranking) that the review also contained.
- *Acceptance criteria:*
  - [x] paper-selection.md selects 3–5 papers with the full template → 5
  - [x] coverage assessment present and honest → Background marked *partially covered*;
    Research gap covered with a stated condition
  - [x] n/a: coverage insufficient → Part 2 not attempted
  - [x] coverage sufficient → introduction-draft.md exists and passes the checklist, with
    two caveats stated in the checklist (G2, G3)
  - [x] no claim lacks an in-text citation (factual claims; aims and reasoning labelled)
  - [x] no citation outside the reference list and vice versa
  - [x] no fabricated findings; abstract-only claims labelled, one marked for full-text
    verification
  - [x] body ≤500 words
  - [x] open-gaps.md present
