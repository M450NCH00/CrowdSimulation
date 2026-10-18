# Work Log — Issue #37: [Research] PT-3 Literature: human evidence for the unseen scenarios (queue cutting, boarding, lifts), Singapore first

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/37
**Branch:** `docs/37-unseen-scenario-human-evidence`
**Started:** 2026-10-18

## Understanding the issue

Track #34 proposes (**not agreed; needs the supervisor's sign-off**) that rules be written over a
portable vocabulary and tested on scenarios they were not extracted from, with **human evidence as
the reference**. This issue collects that human evidence. Literature only: no code, no paid calls.

Five candidate unseen scenarios: four already in the agreed Singapore scope in
`dataset/scenarios.yaml` (`bus_queue_boarding`, `mrt_door_alight_board`, `lift_boarding_capacity`,
`escalator_entry_merge`), plus queue cutting (not in that file). The `decision_factors` of those
four, and of `merge_two_corridors`, list what the evidence should speak to: queue position and
discipline, letting alighting passengers off first, door markings, crowding, time pressure, who has
waited longest, prams/wheelchairs/elderly priority, standing on one or both sides of an escalator,
zipper-merge alternation.

Questions: Q1 queue cutting; Q2 boarding and alighting at train/bus doors (field or controlled data
only; simulation papers count only for the field data they cite); Q3 lifts and escalators (only if
budget remains); Q4 Singapore-specific evidence (report "nothing found" honestly, with searches);
Q5 age and gender effects (cross-reference `literature/demographic-personas/human-demographic-effects.md`,
do not repeat it); Q6 graded, testable reference behaviours, with a grading scale I define and mark
as a proposal. Also: resolve whether Milgram et al.'s queue-intrusion paper is 1978 or 1986.

Deliverables go in `literature/unseen-scenario-evidence/`, sources in `refs/`.

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** `origin/main` has none of the `literature/` files the issue says to read;
  they exist only along the stacked research branches. As #36 did (its A1), I cut this branch from
  the previous issue in the same track, `docs/36-unseen-scenario-testing-literature` (PR #44, head
  `cc4cb73`, in sync with origin), and will target the PR at it. A merge into a non-default branch
  will not close #37 by itself.
- **A2. Cache prefix.** Sources for this issue are cached as `refs/he_*` ("human evidence"),
  following `gt_*` (#20), `sr_*` (#22), `pr_*` (#35) and `us_*` (#36).
- **A3. What is committed** (the repository is public; same rule as #35's A7 and #36's A3). Text
  extracts and PDFs are committed only for openly licensed copies, arXiv, and public
  government/official pages that allow it; copies with no open licence are kept on disk only, text
  included, and listed in `.gitignore` with a re-download link.
- **A4. Reads beyond "these, and only these".** I looked at the *format* of #36's
  `missing-papers.md` and `search-log.md`, and at its work log's assumptions, to keep the same
  conventions; no content from them is used as evidence.
- **A5. Stubs** for sources that cannot be opened go in the file where the entry would have gone,
  with exactly the issue's six lines, and are listed in `missing-papers.md`.

## Plan

1. Branch and work log. **(done)**
2. Read what the issue lists. **(done)**
3. Q1 queue cutting: confirm and read Milgram et al. (resolve 1978/1986), Mann 1969, Langer et al.
   1978, Schmitt et al. 1992 (unverified lead), Allon & Hanany 2012 (structure + cited empirics);
   look for replications and recent field work.
4. Q2 boarding/alighting: the seed modelling papers, used only for the field data they cite; look
   for field observations and controlled experiments (platform markings, alight-first, door
   sharing, crowding).
5. Q4 Singapore: LTA, SMRT, SBS Transit, academic work; log every search.
6. Q3 lifts and escalators if budget remains, else a stub with leads.
7. Q5 age/gender effects, extracted from each entry and cross-referenced.
8. Q6 `reference-behaviours.md` with a proposed grading scale; `verdict.md` (one page);
   `search-log.md`; `missing-papers.md`; `refs-unseen-evidence.bib`; README row.
9. Verify against §5b of the workflow, push, open the PR against the #36 branch.

## Progress log

### 2026-10-18 — Branch, background read
- What I did: cut the branch from the #36 branch (A1); read issue #34's "The idea", the five
  scenarios in `dataset/scenarios.yaml`, and skimmed `human-demographic-effects.md` (its warning
  section, "Identified but not obtained", and "Cross-cutting observations").
- Why: the issue's "Before starting" list.
- Result / what I found: the demographic file's B3 has no study of queueing, boarding or lifts;
  its strongest measured pedestrian finding is that young adults contribute more to avoidance when
  meeting an older adult ([Rapos-CollisionAvoidance]), and it warns that much "demographic"
  crowd evidence is a simulation input, not a measurement. The same warning applies here: boarding
  models whose behaviour is an input are not human evidence.
- Next step: Q1, starting with Milgram et al.

## Open questions / risks

(filled in as work proceeds)

## Summary (fill in at the end)
