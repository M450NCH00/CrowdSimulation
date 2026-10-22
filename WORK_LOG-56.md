# Work Log — Issue #56: [Docs] RF-1: record the resolve-first direction in CLAUDE.md, the READMEs and the decision log

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/56
**Branch:** docs/56-record-resolve-first-direction
**Started:** 2026-10-22

## Understanding the issue

At the supervisor meeting of October 2026 the method changed (track issue #55, "RF: resolve
first, then extract rules"). Until now (#30) a model was asked to negotiate or state a rule
directly. The supervisor now wants: (1) test whether LLM agents can resolve a conflict at all,
without asking for a rule; (2) if they can, extract the hidden rule or pattern, with the LLM's
reference for it; (3) verify the rule against real human behaviour; (4) include as many factors
as possible, find which ones drive the decision, and map factors to decision.

`CLAUDE.md` still tells a new session that the Phase 1 behaviour dataset is the current task, so
the repository's instructions point at an old goal. This issue only records the new direction,
in four places: `CLAUDE.md` (current task, the meeting notes word for word with the date, a
pending sign-offs list), the root `README.md` roadmap table, `llm_negotiation/README.md`, and the
decision record in `llm_negotiation/docs/architecture.md` section 8. No code, config or template
changes.

**Assumptions:**
- A1. **Base branch.** `origin/main` is still at the initial commits, and this repository stacks
  each branch on the previous one. PR #54 (`docs/supervisor-meeting-notes-issues-24-to-52`) is
  open and holds the talking points this issue asks me to read, so the branch is cut from it and
  the PR will target it. `git checkout main` was not run (memory note on half-failed checkouts).
- A2. **Meeting date.** Not recorded anywhere in the repository. Asked the user: **Tuesday
  20 October 2026**.
- A3. **Pending sign-offs.** Task 3 lists seven items "matching the decisions listed in #55".
  #55 also lists a decision the task's list leaves out: whether the "no new simulation code until
  the literature review is discussed" instruction is lifted. It is unconfirmed (root `README.md`,
  "Status of that instruction"), so it is listed as PENDING too. Listing a pending item records
  no approval, so this is on the safe side.
- A4. **"Word for word".** The notes are copied character for character from the issue body,
  one quoted line per line of the notes. Blank `>` lines are put between them so Markdown does
  not run them together into one paragraph; that changes the rendering, not the words. A script
  checks the copy against the issue body.
- A5. **Where the October points go in `architecture.md`.** Section 8 is rule generation (#30),
  and conditions A and B are what the new direction replaces, so the points go in a new
  subsection 8.6. They are the supervisor's, not this project's choices, so they are not
  numbered DD (which the file defines as this project's own decisions needing sign-off); they get
  their own prefix, SV, in the same bold-lead style.
- A6. **The issue drafts.** `issue_drafts/` is untracked and was there before this branch. It
  is the user's; it is not committed here.

## Plan

1. Read the prescribed files (done): `CLAUDE.md`, `README.md` roadmap table, the opening of
   `llm_negotiation/README.md`, `architecture.md` section 8 (and 9.4 for numbering), Part 6 of the
   talking points, and track issue #55.
2. `CLAUDE.md`: replace "Current task" with the four-step RF pipeline and the track's
   constraints; keep the budget, `.env` and workflow notes; keep Phase 1's facts as a short
   on-hold note; update the "Roadmap" section to point at RF.
3. `CLAUDE.md`: "Supervisor decisions" with the 2026-10-20 notes word for word, and a summary
   below, marked as a summary.
4. `CLAUDE.md`: "Pending sign-offs", each PENDING (the seven of task 3, plus A3).
5. `README.md`: RF rows in the roadmap table; step 4 marked superseded by RF; a short line in
   "Current focus".
6. `llm_negotiation/README.md`: "Direction since October 2026".
7. `architecture.md`: section 8.6, and the file's opening paragraph mentions it.
8. Verify: script-check the verbatim copy; grep that no sign-off reads as approved; re-read each
   acceptance criterion.
9. Push, open the PR against `docs/supervisor-meeting-notes-issues-24-to-52`, comment on the issue.

## Progress log

### 2026-10-22 — Branch, reading, the meeting date
- What I did: checked the remote, `gh auth` and the tree (only the untracked `issue_drafts/`).
  Cut `docs/56-record-resolve-first-direction` from the current branch (A1). Read the prescribed
  files and #55. Asked the user for the meeting date.
- Why: the issue says to ask for the date if it is not known; nothing in the repository gives it.
- Result / what I found: the meeting was on 2026-10-20. `CLAUDE.md` on this branch does not carry
  the "no new simulation code" instruction at all, though the root `README.md` still reports it
  as unconfirmed. Architecture decisions run to DD119 (section 9.4).
- Next step: edit `CLAUDE.md`.

## Open questions / risks

## Summary (fill in at the end)
