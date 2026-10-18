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

### 2026-10-18 — Deliverables written
- What I did: wrote `scenario-standards.md` (8 entries + comparison table), `methods.md` (5 Q1
  entries incl. the Zhang cross-reference, 5 Q2 entries + 1 stub, 3 Q4 entries),
  `test-protocol-draft.md`, `verdict.md`, `search-log.md`, `missing-papers.md` and
  `refs-unseen-scenarios.bib`; added a README row, tree entry and three findings. Posted a progress
  comment on #36 after Q3.
- Decisions made while writing (all marked in the files):
  - **Kept L0-L4, with three changes** argued from the entries: split L0 (new seeds / new
    co-players, Melting Pot's visitor and resident modes); run L3 in both directions (Cason et al.;
    Tordeux et al.); add a wording axis W and a convention axis C for the LLM stage (Aher et al.;
    Binz & Schulz; Wu et al.; Cooper & Kagel).
  - **Marked as proposals with no source:** the whole-conflict-type hold-out (stricter than
    Melting Pot), L4 abstention, the first fold, the L4 candidate (`signalised_crossing`), and the
    `communication`, `service point` and "must say so" parts of the card.
  - **Verdict trimmed** from 592 to 552 words to fit one page.
- Checks made: every locator in the four main files was re-checked against the cached text
  (corrections: SteerBench section names, IMO Annex 2 page, TN 1822 quotation, Zhang table pages,
  Cooper & Van Huyck p. 24 not 25, Aher appendix F not F.2, a section number I had guessed for
  Cooper & Kagel removed). The ODD author list, first typed from memory, was checked against the
  article page (all 19 names matched; one spelling fixed).
- Next step: verification per §5b, push, PR.

## Open questions / risks

- **U1. L4 (abstain) has no literature behind it.** No source tests a rule that should *decline*
  to act outside its scope; I did not search the selective-prediction / abstention literature.
  Whether "abstain" is the right L4 target may depend on what a simulator does when no rule
  applies (PT-8).
- **U2. The whole-conflict-type hold-out is my design, not a precedent.** Melting Pot never holds
  out worlds; no pedestrian study holds out a conflict type. It is argued from the transfer
  evidence and needs the supervisor's sign-off like the rest of #34.
- **U3. g6's conclusion now needs a caveat, which I have not written into g6.** g6 says no evidence
  was found of transfer between structurally different games. [CooperVanHuyck-Transfer] reports
  transfer "even when games are not structurally similar", within coordination games. Editing g6
  is outside this issue's deliverables; flagged here and in the verdict for PT-7.
- **U4. Four spillover studies were read as working papers or manuscripts.** Huck et al.'s working
  paper even has a different title; Grimm & Mengel's JET version is much longer. Conclusions drawn
  from them could change against the published text (`missing-papers.md` V1-V5).
- **U5. ISO 20414 was not read.** TN 1822 is a precursor, not the standard; the card's test fields
  might change once Annex A/B are seen.
- **U6. Q4's three studies were my choice**, named from memory and then confirmed, because the issue
  gave no seeds beyond g5/g6. Other approaches (e.g. contamination-detection methods) are not
  covered.
- **U7. Zhang et al.'s out-of-domain layout is not described in the text searched.** It may be in a
  figure; the rendered PDF was not checked.
- **U8. Branch base (A1).** The PR targets the #35 branch, so merging it will not close #36
  automatically.
- **U9. What is committed (A3).** Eleven cached sources with no open licence are kept on disk only.
  The user may prefer a different line, e.g. committing the JASSS or JuPedSim text.
- **U10. The protocol's "simple convention" baseline examples** ("first-come-first-served",
  "alighting before boarding") are my examples, not taken from the human-evidence reviews; PT-3
  should supply the real ones.

## Summary

**What changed.** New folder `literature/unseen-scenarios/` with the seven deliverables the issue
lists; 20 sources read (7 scenario formats, 13 studies) and 2 stubbed (ISO 20414; Mengel & Sciubba
2014); text extracts under `refs/us_*` (arXiv, CC BY-ND and US-government copies tracked, the rest
on disk only via `.gitignore`); README row, tree entry and three findings.

**Why.** Issue #36 (PT-2 of #34) asks how extracted rules should be tested on scenarios they were
not extracted from, and how such scenarios should be written down so several simulators can run
them.

**Answers, in one line each** (details in `verdict.md`):
- **Q1:** "unseen" means new partners (Melting Pot), a new layout (Zhang; Tordeux) or a new test
  situation (RiMEA). No field holds out a whole type of situation.
- **Q2:** five of six leads read. Transfer happens within a class of games; it is directional,
  sometimes harmful, and sensitive to discriminability and context.
- **Q3:** no format states who goes first, models communication, or allows joining a queue
  part-way; the card must be assembled from seven formats.
- **Q4:** leakage can be graded (counterfactual, new-variant and perturbation tests), not excluded.
- **Q5:** a draft protocol with three changes to L0-L4, freezing of cores *and* bindings, five
  baselines, nine metrics and twenty card fields, each sourced or marked "(proposal)".

**How it was verified (workflow §5b).**
- Every quantitative claim and definition in `methods.md`, `scenario-standards.md`,
  `test-protocol-draft.md` and `verdict.md` carries a locator, or is marked `[inference]`,
  `[unverified]` or "(proposal)". Each locator was re-checked against the cached text; the
  corrections are listed in the last progress entry. A scan for numbers without a nearby locator
  found only headings, list numbers and the continuation lines of quotations.
- Every entry was confirmed from its own page plus Crossref, the arXiv API or PMLR; statuses are
  recorded.
- Q1-Q5 are each answered; each of g6 §3's six spillover leads is read (five) or stubbed (one);
  the verdict is 552 words.
- "Open questions / risks" above is not empty.
- Sources are cached in `refs/` (`refs/us_*`).
- There is no test suite for a literature deliverable; no code was changed and no paid API call was
  made.
