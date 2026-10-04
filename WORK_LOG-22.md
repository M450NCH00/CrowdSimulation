# Work Log — Issue #22: [Research] Literature: rule-based conflict avoidance and resolution in simulators and games

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/22
**Branch:** `docs/22-simulation-conflict-rules-literature`
**Started:** 2026-10-04

## Understanding the issue

Issue #20 catalogued *theory* (conventions, correlated equilibria, priority from asymmetries).
This issue catalogues **rules as actually implemented and evaluated in working systems** —
crowd simulators (S1), games and game engines (S2), multi-agent path finding and multi-robot
navigation (S3), and traffic / autonomous vehicles (S4) — so the FYP can reuse and extend an
existing rule rather than invent one. Because the long-term aim is a rule that drops into any
agent-based simulator, **portability across agent types is assessed for every rule**.

Every paper gets one primary category:

- **A** — avoid conflict by following a rule (the conflict state is never instantiated);
- **B** — resolve conflict through communication (a channel carrying information not inferable
  from physical state);
- **C** — resolve conflict by following a rule (contention exists, a rule arbitrates, no
  negotiation).

Hard constraints I am holding myself to:

- **Recency:** only papers published 2016 or later get a template entry. ORCA, RVO, social
  force, boids, CBS and similar go in `pre-window-foundations.md` as pointers only.
- **Sourcing:** nothing is summarised that I did not open in full text. A paper I cannot open
  gets a `[NOT OBTAINED]` stub and a line in `missing-papers.md` — no abstract-based summary.
- **Locators:** every claim and number carries a section / table / figure / algorithm locator.
- **No over-generalising:** if a paper tests 100 agents, the entry says 100 agents.

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** The workflow says branch from `main`, but `main` has no `literature/`
  and no `refs/`; every literature PR is still open and each issue branch is cut from the
  previous one (see WORK_LOG-20 A1). The issue also requires cross-referencing the issue #20
  catalogue, which exists only on `docs/20-game-theory-conflict-rules`. I therefore cut this
  branch from that branch (`fc80940`). The PR will target that branch, as PR #21 targets #18's.
- **A2. `[NOT OBTAINED]` stubs live inside the sub-area file** they would have belonged to, as
  a headed block with exactly the issue's six lines, rather than as one file per paper. The
  issue says "create the file with only this content", but its deliverables list has one file
  per sub-area, not per paper. `missing-papers.md` is the consolidated list either way.
- **A3. Cache prefix.** Sources for this issue are cached as `refs/sr_*` (simulation rules),
  following the `gt_*` prefix used for issue #20.
- **A4. "Published in 2016 or later"** is judged on the version I cite. A preprint first posted
  in-window with no published version is eligible and labelled `[preprint]`.

## Plan

1. Branch + work log. **(done)**
2. Fetch and read the twelve verified seeds; resolve each arXiv seed to a published version
   where one exists; check the mutex-propagation paper's year; confirm or fail the
   `[secondhand]` velocity-obstacle survey; decide whether CrowdVLA is in scope.
3. Search S2 (games) and S4 (traffic) from scratch — no seeds given. S4 must supply genuine
   category B examples (negotiation / protocol-based merging and intersections).
4. Fill gaps in S1 (lane formation, bottleneck, counterflow) and S3 (communication-based MAPF).
5. Cache every source under `refs/sr_*` and first-page-check each download against the expected
   title (the lesson from issue #20's three wrong-paper downloads).
6. Write the four sub-area files with the issue's per-paper template.
7. Write `pre-window-foundations.md`, `missing-papers.md`, `refs-simulation-rules.bib`.
8. Write `rule-catalogue-simulation.md` (draft; one row per rule; no merging), cross-referenced
   to issue #20's `candidate-rule-catalogue.md`.
9. Write `category-summary.md` and `research-gap.md` from the collected entries only.
10. Write `search-log.md`; verify acceptance criteria one by one (workflow step 5b); PR.

## Progress log

### 2026-10-04 — Branch and work log created
- What I did: checked preconditions (`gh auth` OK, tree clean, remote correct), read the issue
  (no comments on it), cut the branch from `docs/20-game-theory-conflict-rules`, seeded this log.
- Why: workflow steps 0–3. Base choice explained in A1.
- Result / what I found: issue #20's catalogue (R1–R14) is on the parent branch and readable,
  so the cross-reference the issue asks for is possible.
- Next step: fetch the seed papers.

### 2026-10-04 — Sourcing: seeds fetched, published versions resolved, five papers unobtainable
- What I did: downloaded all twelve seeds; checked each first page against its expected title;
  resolved arXiv seeds to published versions through the arXiv record and Crossref; looked up
  non-seed candidates through the arXiv API by title (no identifier was guessed).
- Why: the issue's sourcing rules, and the lesson from issue #20's three wrong-paper downloads.
- Result / what I found:
  - No wrong paper was downloaded this time.
  - **Every seed given as an arXiv link that I summarised has a published version, except the
    MAPF survey**: PIBT → *Artificial Intelligence* 2022; free-space PIBT → *Mathematics* 2026;
    LSRP → AAAI 2025; fast crowd avoidance → CGI 2019; AVOCADO → IEEE T-RO.
  - **The `[secondhand]` velocity-obstacle survey is confirmed to exist** (Vesentini, Muradore,
    Fiorini, *Robotics and Autonomous Systems* 174, 104645, 2024) **and is paywalled.** Not read.
  - Mutex propagation: the issue asked for a year check. The journal version is 2022 (in window)
    but paywalled; the open ICAPS 2020 version (also in window) was read in its place.
  - Five papers and one industry documentation page could not be opened. Each has a stub with no
    summary content; `missing-papers.md` consolidates them.
  - CrowdVLA was opened and excluded: a learned vision–language–action policy, not a rule.
- Next step: read.

### 2026-10-04 — Reading, and a decision about what "full text read" means
- What I did: read 25 sources from the cached text extracts.
- Why: no entry may be written from an abstract.
- Result / what I found:
  - **Nine were read selectively, not in full.** They are long (a 100-page survey, a 40-page
    technical paper, papers whose core is proofs). The issue's template says "Verified: yes (full
    text read)". I wrote what is true instead — the sections read and not read — and scoped every
    claim to them. This is a deviation from the template, made deliberately.
  - **Text extraction lost equations, figures and some table alignment.** Several results that
    exist only in plots could not be reported. Flagged per entry and in `search-log.md` §2.
  - **Six sources contradict themselves** on a headline number or a mechanism. Recorded, not
    resolved (`search-log.md` §6 item 6).
- Next step: write the sub-area files.

### 2026-10-04 — Sub-area files written; S2 has no peer-reviewed entry
- What I did: wrote S1–S4 with the issue's template; committed; posted a progress comment on the
  issue.
- Result / what I found: **S2 is industry-only** — three *Game AI Pro 3* chapters and one engine
  documentation page. Stated at the top of `s2-games.md`, with an empty peer-reviewed section, as
  the issue requires.
- Next step: synthesis files.

### 2026-10-04 — A direction change: two first-draft conclusions were wrong
- What I did: wrote first drafts of the catalogue, `category-summary.md` and `research-gap.md`.
  Before committing them I ran four more web searches aimed at the "none found" claims I was about
  to make.
- Why: the drafts said (1) no traffic source was primarily a rule-based arbitration and (2) no
  source arbitrated between continuous-space agents. Both were conclusions that a single
  counter-example would overturn, resting on three web searches.
- Result / what I found: **both were overturned on the first page of results.**
  - Pruekprasert et al. (IEEE ITSC 2019): an explicit right-of-way priority order taken from
    Japanese traffic rules, with no vehicle-to-vehicle messaging.
  - Dergachev and Yakovlev (IEEE CASE 2021): continuous-space agents using the same avoidance rule
    as the pedestrian models, plus stall detection and local arbitration.
  - Both were read in full and added (27 sources, 35 rules). `category-summary.md` and
    `research-gap.md` were rewritten, not patched. The gap statement changed from "the arbitration
    layer is missing for pedestrians" to "the mechanism exists; the source of the precedence order
    is what is missing".
- What I should have done differently: run the test searches **before** drafting the synthesis.
  Logged in `search-log.md` §6 item 1. The "none found" statements that remain are only as strong
  as seven web searches, and the files say so.
- Next step: verification.

### 2026-10-04 — Smaller mistakes caught before commit
- A citation I misattributed: I wrote that the multi-robot deadlock paper cites the buffered
  Voronoi cells paper. Its "Zhou et al. 2017" is a different paper. Removed.
- Provenance I overstated: three papers were described as "found by search" when I already knew
  of them. Corrected; `search-log.md` §4 now says which sources came from prior knowledge (seven).
- A comparison I overstated: "PIBT beats Token Passing on runtime and quality" → the paper says
  faster, and "comparable to or better" on quality.
- A subtitle from memory for an unobtained paper, replaced by the Crossref title.
- Fifteen of my own paraphrases were set in quotation marks in the sub-area files, where a reader
  would take them for the paper's words. Found by the automated quote check below; changed to
  italics.

### 2026-10-04 — Verification (workflow step 5b; no test suite applies)
- What I did, by script (`verify.py`, `quotes2.py`, `quotes3.py` in the session scratchpad — not
  committed):
  - (a) all 11 deliverables exist;
  - (b) 27 entries defined; **0 dangling** entry-handle references across all files; every entry
    is referenced from at least one synthesis file;
  - (c) 28 BibTeX keys named in entries, **0 undefined** (48 records in the bib);
  - (d) **0 broken** relative links;
  - (e) 37 `refs/sr_*` files named in the text, **0 missing**, all tracked in git;
  - (f) 35 catalogue rows, numbered 1–35 without gaps; **0** out-of-range `SR` references; every
    row cites an entry; rows by primary category A 18, B 6, C 11 — matching `category-summary.md`;
  - (g) primary categories recomputed from the entries: A 11, B 7, C 7, uncategorised 2 = 27 —
    matching the summary table cell by cell;
  - (h) no entry's venue line carries a year before 2016;
  - (i) every entry contains all 22 template fields;
  - (j) 5 `[NOT OBTAINED]` stubs, each present in `missing-papers.md`.
- **Quotation check.** Every double-quoted string of five or more words in the four sub-area files
  (236 after the fix above) was compared with the cached text of the source it is attributed to.
  206 matched at 75% or more of their three-word sequences. The other 30 were inspected by hand:
  quotations spanning a column break in a two-column PDF, quotations containing an ellipsis or a
  symbol that extracts differently (`v_arb`, `v_low`, `OCA_i`), two quotations correctly
  attributed to a *different* cached source, and one quotation from the issue itself. **None was
  a fabricated or materially altered quotation.**
- What this does not verify: that each *paraphrase* is faithful, that each locator points at the
  right section, or that the classifications are right. Those rest on my reading.
- Next step: PR.

## Open questions / risks

Canonical list: `literature/simulation-rules/search-log.md` §7 (R1–R14). The ones that need a
decision or that most limit what can be claimed:

- **R1/R2 — the sample is small and seed-led, and the conclusions already moved once.** 27
  sources, seven web searches, no bibliographic database, seven sources from prior knowledge. No
  count in these files should be quoted as a property of the field.
- **R3 — S2 has no peer-reviewed entry.**
- **R4 — five papers are missing; two matter** (the velocity-obstacle survey and the Eurographics
  crowd-simulation survey). The second should open in an ordinary browser.
- **R5 — needs sign-off: a classification choice.** I treated a planner-level contest for a grid
  cell as a "conflict state", which makes the PIBT family category C rather than A. A different
  reading would move up to five S3 entries.
- **R6 — needs sign-off: the A/B boundary is silent on simulators and on conventional signals.**
  Three hard cases turn on it. I propose splitting B into "information shared, then a rule
  decides" and "the agents bargain". That is my proposal, not something the issue authorised.
- **R7 — one borderline window call:** the collision-free speed model was published in 2016 and
  posted to arXiv in December 2015. Counted in; flagged.
- **R8/R9 — nine entries read selectively; fifteen read as arXiv copies of published papers.**
  Locators and two sets of numbers must be re-checked against publisher versions before the
  report quotes them.
- **R10 — whole areas not searched:** in-window cellular-automaton pedestrian models, data-driven
  crowd models, human-like driver models. Each could overturn a claim in `research-gap.md`.
- **R13 — relevance statements are not grounded in CrowdGym.** I did not read
  `integration/crowdgym_mapping.md`; nothing here proposes a CrowdGym change.
- **R14 — three results cut against the FYP's working assumptions** and should be raised with the
  supervisor: a survey judging communication-free approaches unsuitable where individual-level
  guarantees are needed; measured evidence that first-come-first-served performs badly under
  load; and evidence that a learned priority costs speed, scale and interpretability.

## Summary

**What changed.** Added `literature/simulation-rules/` with the eleven deliverables the issue
specified: four sub-area files (27 entries: S1 6, S2 4 industry-only, S3 10, S4 7);
`rule-catalogue-simulation.md` (35 rules, each sourced, none merged, ten look-alike groups listed,
cross-referenced to issue #20's R1–R14); `category-summary.md`; `research-gap.md`;
`pre-window-foundations.md` (14 pointers, no summaries); `missing-papers.md` (5 papers + 1
documentation page); `refs-simulation-rules.bib` (48 records); `search-log.md`. Cached the sources
under `refs/sr_*`. Updated `README.md` with roadmap step 5c and three findings.

**Why.** The supervisor confirmed the rule this FYP extracts need not involve communication at
runtime and need not be specific to pedestrians. Issue #20 collected the theory. This issue
collects what has actually been implemented and evaluated, so the project can reuse a rule rather
than invent one, and assesses how far each rule would carry to a different kind of agent.

**What it found, in one line each.**
1. **The mechanism exists; the precedence order is the missing piece.** Avoidance rules for
   pedestrians and game characters stall in symmetric conflicts (six sources report it; one proves
   why). Arbitration rules exist for grid robots, for vehicles, and once for continuous-space
   agents. The order they apply is random, identifier-based, or first-come-first-served in nearly
   every rule read, and is called arbitrary by its authors.
2. **Issue #20's open question is answered.** An arrival-order rule exists — it is the standard
   baseline at unsignalised intersections — and the one paper with numbers shows it doing badly
   under load.
3. **A precedence rule's content is local.** The one rule with an outside source copies a national
   traffic code and notes that other countries differ. For pedestrians there is no code to copy.
4. **Categories split by sub-area, not evenly.** A 11, B 7, C 7 overall; but all ten pedestrian
   and game entries are avoidance (A), and no B entry involves actual bargaining.
5. **One of 25 rule-bearing sources is validated against human data**, and none demonstrates a
   rule on two kinds of agent. Both figures describe this sample only.

**What it did not find or could not do.** No peer-reviewed games source. Five papers not
obtained. No systematic search. Numbers that exist only in figures.

**How it was verified.** No test suite applies; workflow step 5b was followed. Scripted checks:
11/11 deliverables; 27 entries with 0 dangling references; 0 undefined BibTeX keys; 0 broken
links; 0 missing cache files; 35 catalogue rows all sourced; category counts recomputed from the
entries and matching the summary; all template fields present in every entry; 236 quotations
compared against cached source text with none found fabricated. The "Open questions / risks"
section is non-empty, as step 5b requires. Every task in the issue is either done or marked as not
done with a reason (`search-log.md` §3, §5, §8).
