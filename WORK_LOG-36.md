# Work Log — Issue #36: [Research] PT-2 Literature: testing rules on unseen scenarios (transfer, generalisation, scenario descriptions)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/36
**Branch:** `docs/36-unseen-scenario-testing-literature`
**Started:** 2026-10-18

## Understanding the issue

Issue #34 proposes, **without anyone's agreement yet**, that rules extracted from LLM agents be
written over a portable vocabulary and tested on scenarios they were not extracted from (queue
cutting, bus and MRT boarding, lifts), described as simulator-independent *scenario cards*. The
claim to test is "the same kind of conflict, in any simulator", not "any conflict", because the
game-theory review found no evidence that conventions transfer between structurally different games
(`literature/game-theory/g6-transfer-across-games.md`, "What this means for the FYP", points 1-2).

This issue is literature only (no code, no paid calls). It asks:

- **Q1** how other fields test whether a model, policy or rule generalises to situations it was not
  built from (Melting Pot; Zhang et al. 2026's out-of-domain test, cross-referenced only;
  cross-scenario validation of pedestrian models);
- **Q2** what the behavioural-spillover studies g6 §3 could not obtain say about conventions
  carrying over to structurally different games: read what is open, stub the rest;
- **Q3** how test scenarios are specified so that several simulators can run them (RiMEA, ISO 20414,
  IMO MSC.1/Circ.1238, OpenSCENARIO, ODD, SteerBench, JuPedSim journeys/stages), and what each
  cannot express;
- **Q4** how LLM-agent studies separate recall of a norm from generalisation (cross-referencing g5
  §4 and Cross et al. 2025, not re-summarising them);
- **Q5** a draft test protocol for the FYP: transfer levels L0-L4, hold-out, freezing, baselines,
  metrics, and scenario-card fields, each cited or marked as a proposal.

Deliverables go in `literature/unseen-scenarios/`, sources in `refs/`.

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** `origin/main` is still `5a0f7be` and has none of the files the issue says to
  read. Branches have been stacked since #8 (the user chose this for #30 and #32). The files the
  issue names are all on `docs/35-simulator-independent-rule-representations` (PR #43, head
  `affa370`, in sync with origin), and #36 is the next issue in the same track, so I cut this branch
  from there and will target the PR at it. A merge into a non-default branch will not close #36 by
  itself.
- **A2. Cache prefix.** Sources for this issue are cached as `refs/us_*` (unseen scenarios),
  following `gt_*` (#20), `sr_*` (#22) and `pr_*` (#35).
- **A3. What is committed** (the repository is public; #35's A7). Text extracts and PDFs are
  committed only for openly licensed copies, arXiv, and public standards/documentation pages that
  allow it; copies with no open licence are kept on disk only, text included, and listed in
  `.gitignore` with a re-download link.
- **A4. Reads beyond "these, and only these".** Issue #34's "Constraints for every issue in this
  track" was already read for #35 and binds this issue too (no paid calls; mark design decisions vs
  assumptions). I also looked at the *format* of #35's work log and `missing-papers.md` to keep the
  same conventions; no content from them is used. To give Zhang et al.'s out-of-domain test a
  locator I search the cached text `refs/zhang2026_dfd.txt` for that one passage, because the
  summary's sections 2 and 6 mention the out-of-domain set but not how it was built.
- **A5. Stubs** for sources that cannot be opened go in the file where the entry would have gone
  (`methods.md` or `scenario-standards.md`) with exactly the issue's six lines, and are listed in
  `missing-papers.md`.

## Plan

1. Branch and work log. **(done)**
2. Read what the issue lists. **(done)**
3. Confirm and cache the seed sources in the issue's priority order: (1) scenario standards,
   (2) generalisation methods, (3) the six spillover leads, (4) leakage.
4. Write `scenario-standards.md` (Q3), with one comparison table of what each format can and cannot
   express.
5. Write `methods.md` (Q1, Q2, Q4).
6. Write `test-protocol-draft.md` (Q5), citing an entry or marking "proposal" for every level,
   metric and card field.
7. Write `verdict.md` (one page), `search-log.md`, `missing-papers.md`,
   `refs-unseen-scenarios.bib`.
8. Verify against §5b of the workflow (locators, open questions, every Q answered), push, open the
   PR against the #35 branch.

## Progress log

### 2026-10-18 — Branch, background read
- What I did: cut `docs/36-unseen-scenario-testing-literature` from the #35 branch (A1); read issue
  #34's "The idea", g6 §2-§3 and "What this means for the FYP", g5 §4, the Zhang summary §§2 and 6,
  and the scenario ids in `dataset/scenarios.yaml`.
- Why: the issue's "Before starting" list.
- Result / what I found: the 14 scenario ids include three that the unseen-scenario track names as
  targets (`lift_boarding_capacity`, `bus_queue_boarding`, `mrt_door_alight_board`). Queue cutting is
  not among them. The Zhang summary records only that there were "three [seeds] for the
  out-of-domain set" (§2) and that all three datasets come from the same LLM simulation (§6), so the
  out-of-domain construction must be located in the cached paper text.
- Next step: cache the scenario standards.

### 2026-10-18 — Scenario standards cached and read (Q3, priority 1)
- What I did: cached and read, in their relevant sections, RiMEA 4.1.1 (German/English, CC BY-ND),
  IMO MSC.1/Circ.1533 and Circ.1238, ISO 20414's public page, NIST TN 1822 (Ronchi et al. 2013),
  OpenSCENARIO XML 1.4.0 §§7.2 and 7.6, the ODD second update (JASSS 2020), SteerBench (CAVW 2009)
  and JuPedSim 1.4.2's routing page.
- Why: the issue's first priority.
- Result / what I found:
  - **The seed link for RiMEA/IMO is dead.** `ped.fandom.com/wiki/Test_Cases` returns HTTP 410:
    the wiki has been closed. I went to the primary documents instead (RiMEA via rimea.de, the IMO
    circulars via two hosting sites).
  - **MSC.1/Circ.1238 is superseded.** Circ.1533 (2016) says "This circular supersedes
    MSC.1/Circ.1238" (para. 11). The issue asks for standards at their current version, so the entry
    cites Circ.1533 and notes the test list is unchanged in substance from what TN 1822 reviews.
  - **ISO 20414 is paywalled** (CHF 204 per a reseller listing, not used as evidence). Only the
    ISO page's abstract and status are used, plus NIST TN 1822 as an open precursor; the standard
    is stubbed.
  - **OpenSCENARIO's "latest" URL in the issue 404s**; versions 1.3.0, 1.3.1 and 1.4.0 are listed,
    so 1.4.0 is cited.
  - **SteerBench** (an `[unverified lead]`) is confirmed: CAVW 20(5-6):533-548, 2009,
    doi:10.1002/cav.277 (Crossref). The copy read is the Wiley typeset PDF on a Utrecht course site.
- Next step: Q1 methods (Melting Pot, Zhang's out-of-domain test, cross-scenario pedestrian studies).

### 2026-10-18 — A slip while cleaning up, caught and undone
- What I did: to delete my own intermediate `.html` downloads I ran `rm refs/*.html`, which also
  deleted 46 tracked `.html` caches from earlier issues. `git status` showed them as unstaged
  deletions; the commit I made right after (`4051e61`) contained only my own files. I restored
  them with `git checkout -- refs/` and confirmed a clean tree.
- Why it matters: nothing was lost, but it was a destructive glob over a shared folder. From here
  on I delete only files I name explicitly.

### 2026-10-18 — Methods, spillovers and leakage sources (Q1, Q2, Q4)
- What I did: read Melting Pot 1.0 (ICML 2021, PMLR 139) and 2.0 (arXiv, no published version
  found), the out-of-domain passage of Zhang et al. (cached `refs/zhang2026_dfd.txt`, §5.1),
  Wolinski et al. 2014 (CGF) and Tordeux et al. (arXiv:1801.09782, published as a TGF'17 chapter).
  For Q2, found open versions of five of the six g6 §3 leads and read them; Mengel & Sciubba (2014)
  could not be obtained (Essex repository unreachable, AgEcon HTTP 403, Maastricht HTTP 403). For
  Q4, read Wu et al. (NAACL 2024), Aher et al. (ICML 2023) and Binz & Schulz (arXiv v1 of the
  PNAS 2023 paper).
- Result / what I found:
  - **Melting Pot does not test transfer across physical settings.** "Policies are not
    transferable between substrates" (MP1 §4.1); MP2 says its generalisation is "mainly along
    social dimensions, not physical dimensions" (MP2, Introduction, p. 4). Its "unseen" is new
    co-players on a familiar map: the FYP's L0, not L2-L3.
  - **Zhang et al.'s out-of-domain set is a different layout with 3 seeds** (§5.1, p. 13), but the
    text I searched does not say how the layout differs, and its ground truth is still the LLM
    simulation.
  - **Cross-scenario pedestrian validation exists but is thin.** Tordeux et al. train on ring or
    bottleneck data and test on the other; Wolinski et al. calibrate per scenario and leave
    cross-scenario generalisation as future work (§5). RiMEA itself warns that a parameter calibrated
    in one situation may not suit another (Annex A2, p. 26).
  - **The spillover studies are more positive than g6 expected, with conditions.** Cooper & Van
    Huyck find transfer from stag hunt to order-statistic games "even when games are not
    structurally similar" (§4, p. 24), but all games share a payoff-dominant and a secure
    equilibrium. Cason et al. find median→minimum transfer but not minimum→median (§7). Huck et
    al. find spillover depends on how accessible game-specific feedback is (§7). Cooper & Kagel
    report positive transfer with meaningful context and zero or negative transfer with generic
    context (§VII, p. 21, citing their own 2006 work).
- Next step: write `scenario-standards.md`, then `methods.md`.

## Open questions / risks

(to be filled during the work)

## Summary (fill in at the end)
