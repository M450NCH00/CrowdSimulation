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

### 2026-10-18 — Q1 queue cutting: seeds confirmed, two primary texts read, six stubs
- What I did: confirmed every Q1 seed on Crossref; checked open copies with OpenAlex (not
  Unpaywall, which refuses placeholder emails, and I will not send the user's address to it; a
  past work log raised the same question); read Brintzenhofe (2023, open-access chapter), Langer et
  al. (1978), Folkes (1985), and pp. 493-500 of Allon and Hanany (2012). Wrote `queue-cutting.md`.
- Why: Q1 is the issue's first priority.
- Result / what I found:
  - **Milgram 1978 vs 1986 resolved**: data collected by graduate students in spring 1978,
    published in 1986 after Milgram's death (Brintzenhofe p. 65). The 129 queues reported by
    secondary summaries match the sum of the per-condition trial counts (Table 3.2, p. 70).
  - **Schmitt et al. 1992 confirmed** (`[unverified lead]` resolved): JPSP 63(5):806-815.
  - Milgram, Schmitt, Mann, Helweg-Larsen and LoMonaco (2008), Dold and Khadjavi (2017) and
    Oberholzer-Gee (2006) are all closed. Stubbed. The last three are new leads found through a
    review (Furnham et al. 2020), which I use only as a lead finder.
  - **A6 (judgement call).** Brintzenhofe reproduces, with APA permission, Schmitt et al.'s Table 1
    and Milgram et al.'s per-position reaction data together with raw archive data. I use these
    numbers, attributed to the chapter and flagged `repro`, but I do not summarise the two papers
    themselves. The supervisor may judge this too close to "secondary"; if so, drop QC-1 to QC-5
    to grade C.
  - **A mistake caught on re-reading**: my first draft said silent buffers suppress objection.
    Table 3.2 does not show that (two-intruder comparisons go both ways), so I rewrote it as "no
    consistent buffer effect in the table" and noted the claim is in the unread paper.
  - Langer's "any reason works for a small favour" was **not replicated** by Folkes (1985), who
    found the *type* of reason matters (uncontrollable > controllable).
  - Rendering table images: the Brintzenhofe tables are images in the PDF, so I rendered pages
    with PyMuPDF in a throwaway `uv run --with pymupdf` environment (nothing installed into the
    project).
- Next step: Q2 boarding and alighting.

### 2026-10-18 — Q2 boarding and alighting, and Q4 Singapore
- What I did: searched for field and laboratory studies of metro and bus doors; read four
  (Seriani et al. 2017 London Underground field video; Seriani et al. 2019 and Luangboriboon et al.
  2020 PAMELA experiments; Harris et al. 2022 field meta-analysis); checked the seed simulation
  papers for field data. Ran ten Singapore searches (logged in `singapore.md` §4); read Cheung et
  al. 2024 (Wi-Fi tracking at two Circle Line stations) and five official pages (MOT 2019, 2025,
  2026; SMRT 2018; BCA 2023), plus two Hong Kong documents that describe Singapore's escalator
  advice.
- Result / what I found:
  - **Biggest Q2 gap**: the two studies that measure boarders entering before alighting ends (Li
    2020 CityU thesis, Hong Kong and mainland China; Baali et al. 2024, HAL) could not be opened.
    The thesis is behind a copyright click-through form, **which I did not accept on the user's
    behalf**; HAL is behind bot protection. Both stubbed.
  - Many open-access publishers (Hindawi/Wiley, MDPI, Elsevier OA, EconStor, HAL, USF Digital
    Commons, Universidad de Chile) refuse automated downloads. UCL Discovery, Springer, Collective
    Dynamics and Taylor & Francis's OA API worked. Papers stubbed for this reason should open in a
    normal browser.
  - **The two lab studies disagree on crowding** (flow falls above ~4 pass/m² vs no clear fall up
    to ~5); recorded, not resolved.
  - **Seriani et al. 2019's manuscript abstract contradicts its own §4.2** on whether boarding or
    alighting comes first; I follow the body and flag it.
  - The seed simulations (Lindner 2025, Chen 2018) have **no field data** to use; Lindner's model
    has no queue at all.
  - **Q4 result: no Singapore observation of any target behaviour was found.** Singapore supplies
    the promoted norms (give way to alighters; priority queues; hold the handrail; lifts for bulky
    items) and one perception survey (52% to 56% "noticing gracious behaviour", 2016-2018, now
    under methodology review), but no compliance rates.
  - **A wording issue in `dataset/scenarios.yaml`** (`escalator_entry_merge.sg_variant` mentions a
    Singapore "stand on both sides" campaign): no source found supports it. Flagged for the
    supervisor; I have not edited the dataset file (out of scope, and it is agreed scope).
- Next step: Q3 lifts and escalators (the remaining budget allows a short pass), then Q5/Q6.

### 2026-10-18 — Q3 lifts and escalators (short pass)
- What I did: three searches; read London Underground's Holborn pilot report (FOI release, 2016)
  and a Taipei MRT field study of accessible-lift users (Huang and Chang 2022, in Chinese, read on
  the journal's e-book site). Wrote `lifts-escalators.md` with the leads not followed.
- Result / what I found: in Taipei, when a wheelchair, pram or walking-frame user needed priority,
  everyone gave way in 24% of trips and nobody in 49%; at Holborn, standing on both sides lasted
  only while staff asked. **No study of who takes the last place in a lift** was found. The Taipei
  e-book's text layer interleaves the two columns, so I checked every number against Table 4,
  which extracted cleanly; journal page = e-book page minus 10 (I first wrote p. 15 for the
  abstract and corrected it to p. 16).

### 2026-10-18 — Q5, Q6, verdict, and verification
- What I did: wrote `reference-behaviours.md` (grading scale A-D plus flags, marked a proposal; 23
  statements; Q5 table and cross-reference with `human-demographic-effects.md`), `verdict.md`,
  `missing-papers.md`, `search-log.md`, `refs-unseen-evidence.bib` (36 records), and a README
  row, findings paragraph and layout entry.
- Verification (workflow §5b):
  - Re-checked every page locator I was unsure of against the cached text (London manuscript,
    Harris, Brintzenhofe, Taipei); corrected Harris §3.4 from p. 75 to p. 74.
  - Cross-checked that each "Reference behaviours it supports" line matches the statement IDs;
    six were wrong after renumbering and were fixed.
  - **BibTeX given names**: several had come from memory, not from a page read. Replaced with
    initials as Crossref gives them.
  - Confirmed the Taipei DOI resolves (doi.org → the issue's e-book).
  - A heredoc mangled a backslash in a Python edit (as my notes warn); nothing was written, and
    the edit was redone from a script file.
- Result: every issue question is answered (Q3 as a short pass, stated as such); see Summary.

## Open questions / risks

1. **Reproduced tables as evidence (A6).** QC-1 to QC-5 use Milgram's and Schmitt's numbers as
   reproduced, with APA permission, in Brintzenhofe (2023). If the supervisor rejects this, they
   drop to grade C until the 1986 and 1992 papers are obtained (M1, M2).
2. **The grading scale is mine**, adapted from the issue's suggestion. In particular "independent
   research groups" for grade A and the `old` cut-off (before 2001) are judgement calls.
3. **BA-8 has no number**: how often MRT boarders start before alighting ends. The two studies
   that measure it (M7, M8) are blocked only by a click-through form and bot protection; a human
   can download both in minutes. This is the highest-value follow-up.
4. **The `scenarios.yaml` escalator wording** (Singapore "stand on both sides" campaign) is not
   supported by any source found. I did not edit the dataset, since its scope is agreed; this
   needs a decision.
5. **No Singapore observation exists in what I searched**, but the search was English-only and
   did not cover DR-NTU, ScholarBank or Public Transport Council studies. "Nothing found" is
   bounded by that.
6. **Lab studies of boarding** (PAMELA) used instructed participants who knew they were observed;
   BA-1 and BA-2 may overstate courtesy at real doors.
7. **Q3 is a short pass** (two primary sources). Escalator step-on timing and merging (the actual
   `escalator_entry_merge` behaviour) and lift "last place" have no evidence here.
8. **Branch base (A1)**: this branch stacks on #36's (PR #44), so the PR targets that branch and
   merging it will not close #37 automatically.

## Summary

**What changed.** New folder `literature/unseen-scenario-evidence/` with the nine deliverables the
issue lists, 19 cached sources in `refs/he_*` (5 committed under open licences; 14 on disk only
and listed in `.gitignore` with links), a README row, findings paragraph and layout entry, and
this work log.

**Answers.**
- **Q1 queue cutting**: answered from Brintzenhofe's reproduction of Milgram et al. and Schmitt et
  al., plus Langer 1978 and Folkes 1985. Objection concentrates directly behind the cut, grows
  with two intruders, shrinks for a "friend"; the kind of reason and the size of the favour
  matter; "any reason works" is contested. Milgram **1978 vs 1986 resolved** (run 1978, published
  1986).
- **Q2 boarding and alighting**: partly answered (alighting first, door-side waiting, overlap,
  lanes, waiting for the next train); the non-compliance rate is a gap; bus boarding has no
  evidence.
- **Q3 lifts and escalators**: answered in a short pass (Taipei lift priority; Holborn escalator
  pilot); explicitly not a full review.
- **Q4 Singapore**: nothing observed; the searches are documented; official norms, a perception
  survey, one platform study and escalator incident counts recorded.
- **Q5 age and gender**: almost nothing measured; cross-referenced with the demographic file.
- **Q6**: 23 graded statements (none grade A; 2 contested; 1 gap), grading scale marked a proposal.

**How it was verified.** Every source confirmed on Crossref, OpenAlex, or its own page; every
number re-read against the cached text or page image; locators spot-checked with scripts over the
cached text; statement IDs and handles cross-checked; stubs carry exactly the six required lines.
No code, no paid calls.
