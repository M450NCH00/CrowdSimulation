# Work Log — Issue #41: [Docs] PT-7 Synthesis: feasibility verdict, final statement of the idea, and supervisor brief

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/41
**Branch:** docs/41-portable-rules-synthesis-brief
**Started:** 2026-10-19

## Understanding the issue

PT-7 closes the evaluation half of track #34 (portable conflict rules). PT-1 to PT-6 each answered
one question; this issue joins their answers up. It produces four documents under
`portable_rules/docs/` and one README row:

- `feasibility.md`: a verdict (feasible / feasible with changes / not supported) for each of the six
  parts of #34's idea, citing the PT file each rests on, with the main risk; plus Part 3, what is new
  against Zhang et al. 2026, arXiv:2409.00993 and the rest, and what the evidence does **not**
  support.
- `idea.md`: the idea restated in its corrected form, one page, every change from #34 marked with
  its reason.
- `supervisor-brief.md`: at most two pages, no repository jargon or file paths in the main text;
  #34's decisions 1-7 plus new ones, each with options, a recommendation and evidence.
- `implementation-plan.md`: future issues, one paragraph each, adjusted to the verdicts. Not created
  on GitHub.
- `README.md`: a roadmap row for PT-7 / the track.

Documents only: no code, no paid calls, no change to `llm_negotiation/`, no new literature search.

**Assumptions:**
- A1. **Base branch.** `origin/main` is still at the initial commits; track #34's PRs were merged
  into stacked branches (#48's base is `docs/39-simulator-desk-survey`). Following that convention
  (memory note; `WORK_LOG-40.md`), this branch is cut from `docs/40-simulator-hands-on-trial` and the
  PR will target it.
- A2. **"Merged" prerequisite.** PT-1 to PT-6 are merged (PRs #43-#48), though their issues are
  still open. Their files are all present on this branch. No input is missing.
- A3. **New folder.** `portable_rules/docs/` does not exist yet; the issue names it, so it is
  created as a new top-level folder (`CLAUDE.md` allows one when no existing folder fits).

## Plan

1. Read only the prescribed inputs: four `verdict.md` files (PT-1 to PT-4), PT-5's `shortlist.md`,
   PT-6's `decision.md`; open longer files only to check a verdict.
2. Read the novelty sources: PT-1's `novelty-check.md`, the Zhang et al. summary.
3. Cross-check the verdicts against each other and against the repository's actual state (the rule
   database), and note where they interact. Those interactions are the synthesis.
4. Write `feasibility.md` (Parts 1 and 3).
5. Write `idea.md` (Part 2), marking each change.
6. Write `supervisor-brief.md` (Part 4); check length and jargon.
7. Write `implementation-plan.md` (Part 5).
8. README row and directory layout (Part 6).
9. Verify per workflow §5b: every verdict cites a PT file; every number re-checked; open questions
   non-empty; every part answered.
10. Push, open the PR against `docs/40-simulator-hands-on-trial`, comment on #41.

## Progress log

### 2026-10-19 — Start, and a half-failed checkout recovered
- What I did: `git checkout main` failed with "unable to write symref for HEAD: Permission denied",
  leaving main's tree staged on `docs/40-...`, exactly as the memory note of 2026-10-18 records.
  Checked nothing was lost (`git diff --cached main` and `git diff` both empty), then
  `git stash push -m "half-failed checkout of main (issue #41 start) - safe to drop"` restored the
  branch tree. Then `git checkout -b docs/41-portable-rules-synthesis-brief` from `docs/40-...`.
- Why: `git reset --hard` is not available in auto mode; the stash is reversible.
- Result: branch created at `cee6ed1`. **The stash `stash@{0}` holds nothing of value and can be
  dropped by the user** (`git stash drop`).
- Next step: read the inputs.

### 2026-10-19 — Inputs read; two cross-file findings
- What I did: read the six prescribed inputs in full, plus #34's body. Opened longer files only to
  check specific points:
  - PT-1 `feasibility.md` F1-F11 (cited by the PT-1 verdict as F4);
  - PT-1 `novelty-check.md` (the issue names it for Part 3);
  - PT-2 `test-protocol-draft.md` §§1-4 (levels, hold-out, freezing, baselines);
  - PT-3 `reference-behaviours.md` (the QC, BA and LE statements);
  - the Zhang et al. summary, and §5.1 of the cached paper (`refs/zhang2026_dfd.txt`), to see what
    its "out-of-domain" set is.
- Why: Part 3 compares the idea against Zhang et al.; whether its out-of-domain test is a new
  conflict type or a new layout decides the comparison.
- Result:
  - Zhang et al.'s out-of-domain set is "beyond the specific scenario layout of the training
    dataset" (§5.1): a new layout of the same evacuation task, i.e. PT-2's L2, not a new conflict
    type.
  - **S1.** Checked the rule database itself: all six rules carry `source_type: hand_written`,
    `status: test_seed`. No LLM-elicited rule exists; the paid pilot is held (README step 3c). No
    PT file states this consequence for the track.
  - **S2.** Reading PT-3's statements against PT-1's F9 and #34's decisions 3 and 4: QC-1 to QC-5
    are about objectors (observer roles, breach handling), QC-6 to QC-8 about reasoned requests
    (`needs_communication`), BA-1 needs roles by category. So the best held-out evidence tests what
    the draft vocabulary cannot express.
- Next step: write `feasibility.md`.

### 2026-10-19 — Verdicts and the restated idea written
- What I did: wrote `portable_rules/docs/feasibility.md` (Parts 1 and 3) and `idea.md` (Part 2).
- Decisions made, all marked as proposals in the files:
  - Every part rated **feasible with changes**; none rejected outright. Five sub-claims rated
    **not supported**, each with what to do instead:
    - identical behaviour across simulators;
    - tests proving conformance;
    - today's rules as an unchanged ORCA binding;
    - human fidelity for bus boarding and escalators;
    - RL or run-time language-model deciders.

    I considered rating part 5 (unseen testing) "not supported" outright, because two of five
    scenarios have no usable evidence. I chose "feasible with changes", since the protocol works
    and three scenarios have graded evidence. I rated the human-fidelity sub-claim for the other
    two "not supported".
  - Two `[synthesis]` recommendations go beyond any PT file, and are labelled so:
    - scope by sub-type (PT-1 F2 left it open);
    - put negsim's conflict detection in the perception adapter (F1 left it open).
- Result: `idea.md` marks ten changes, C1 to C10. C9 and C10 are new; they come from S1 and S2.
- Note: `idea.md`'s restatement (paragraph, parts, example) is about one page. The change table
  follows it as a supplement. The issue asks for the restatement on one page *and* for every change
  marked. I read the table as the marking, not as part of the page.
- Next step: the brief.

### 2026-10-19 — Brief, implementation plan, README
- What I did:
  - Wrote `supervisor-brief.md`. The first draft was 1,221 words, too long for two pages; I rewrote
    it to 983 words.
  - Scanned the brief for repository jargon (negsim, ORCA, PT-n, L0-L4, binding, adapter, file
    paths, issue numbers): no hits.
  - Changed "surveyed seven crowd simulators" to "six besides our own": `survey.md` §§1-7 includes
    negsim.
  - Checked author names for Frantz and Siddiki, Edmonds and Hales, and Wolinski et al. in the PT
    bib files.
- Decisions:
  - The brief keeps #34's decisions 1-7 and adds three new ones:
    - 8: two testbeds per held-out type, PT-6's only sensitive choice;
    - 9: what counts as human evidence, from PT-3's points 1 and 2;
    - 10: the go-ahead and the order of work, from S1, the unconfirmed standing instruction, and
      CrowdGym access.
  - Two smaller asks are folded in rather than given their own numbers:
    - PT-4's "which attributes must not matter" goes into decision 7;
    - CrowdGym's code goes into decision 10.
- `implementation-plan.md` changes the starting order in four ways:
  - a supervisor gate before PT-8;
  - the evaluation harness moved before prompt version 3, so every free step is checked on the
    seed rules before the first paid step;
  - PT-8's paper test extended to the graded evidence (S2);
  - trained deciders and the CrowdGym binding made conditional.
- README: roadmap row 5k, a three-point findings block, and `portable_rules/` in the directory
  layout.
- Two-page check: no PDF or Word renderer is installed (no pandoc, LibreOffice, python-docx or
  reportlab), so the length is an **estimate**: 983 words of mostly prose ≈ 2 A4 pages at 11 pt.
  Not measured.

## Open questions / risks

1. **Q1. Brief length is estimated, not measured** (no renderer). If it runs over when pasted into
   Word, the "What the evidence does not support" paragraph is the first to cut; it repeats
   `feasibility.md` §3.3.
2. **Q2. Two `[synthesis]` recommendations rest on my reading, not a source:** scope by sub-type
   (F2) and conflict detection in the perception adapter (F1). Both are in the brief only
   indirectly (decisions 1 and 2), and need the supervisor or PT-8 to settle.
3. **Q3. Is S2 overstated?** It assumes "objection" can only be expressed with observer roles. PT-8
   might express QC-1 as a pass criterion on a card rather than as a rule. Then queue cutting would
   test a transferred rule's *effect* on objection, not a rule about objecting. PT-8's paper test,
   part 2, is designed to find out.
4. **Q4. "Feasible with changes" for unseen testing is a judgement call** (see the progress entry
   above). A stricter reader could call it "not supported" until PT-3's missing papers are
   obtained.
5. **Q5. Stacked base.** The PR targets `docs/40-simulator-hands-on-trial`, following the track's
   convention (A1). `main` still lacks all of track #34.
6. **Q6. The stash** `stash@{0}` from the half-failed checkout holds nothing of value; the user can
   drop it.
7. **Q7. Issues #35 to #40 are still open**, though their PRs are merged into stacked branches. I
   did not close them (workflow §7).

## Summary

**What changed:** a new folder `portable_rules/docs/` with four documents, and three README edits.
No code, no API calls, no change to `llm_negotiation/`, the dataset or the pipeline.

| File | Part | Content |
|---|---|---|
| `feasibility.md` | 1, 3 | A verdict per part, each citing its PT file: all six feasible with changes; five sub-claims not supported. Two cross-file findings (S1, S2). Novelty against Zhang et al. 2026, arXiv:2409.00993, CRSEC, TR2MTL and others. A 13-row table of what the evidence does not support |
| `idea.md` | 2 | The idea in plain language; ten changes from #34 marked C1-C10, with reasons and sources |
| `supervisor-brief.md` | 4 | 983 words, no repository jargon; decisions 1-10 (three new), each with options, recommendation, evidence |
| `implementation-plan.md` | 5 | Seven future issues, one paragraph each, reordered to the verdicts; none created |
| `README.md` | 6 | Roadmap row 5k; findings block; directory layout |

**Why:** issue #41 closes the evaluation half of track #34. The supervisor needs one short document
to decide on, and PT-8 needs to know which parts it may start on.

**How it was verified (workflow §5b):**
- **Every verdict cites its PT file.** Each verdict row and section names PT-1 to PT-6 and the
  source handle. Statements resting on no single source are marked `[synthesis]`.
- **Numbers re-checked against the PT files:**
  - from PT-1: 5 of 10 FMI importers;
  - from PT-4: 0.5-2 s per language-model call;
  - from PT-3: 14 missing sources and the evidence grades;
  - from PT-6: 47 lines, 2.9-3.4×, 0.21 simulated s per computing s;
  - from the rule database: six rules, all `hand_written` / `test_seed`.
- **Open questions are non-empty** (Q1-Q7 above; each document also lists its own).
- **Every part of the issue is answered.** Parts 1-6 are all delivered. No input was missing, and
  each document says so.
- **No new literature search.** Gaps are named as follow-ups: PT-3's 14 sources; arXiv:2509.02515;
  NormSage; CrowdGym's code.
- **Sources** are the PT files' own cached copies under `refs/`; nothing new was fetched.
- **Zero spend; no code.**

