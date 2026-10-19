# Work Log — Issue #20: [Research] Literature: game theory for communication-free conflict resolution rules

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/20
**Branch:** `docs/20-game-theory-conflict-rules`
**Started:** 2026-09-30

## Understanding the issue

The FYP wants to extract a **reusable pattern** from LLM-to-LLM conflict resolution, so that
future conflicts in the crowd simulation are resolved by *applying the pattern* rather than by
re-running an LLM exchange every time. The latest supervisor meeting sharpened the target:

1. The pattern **need not be a dialogue pattern.** It can be a rule agents follow to reach
   consensus **without communicating at all** — a traffic convention.
2. The rule **should not be tied to spatial conflict**; ideally it applies to any generic
   simulator. So the narrow-hallway case is one instance of a general class of conflict games,
   not the subject.

Game theory formalises exactly this object. This issue is **literature only**: collect the
theory and the applied work needed to (a) define precisely what is being extracted, and (b)
justify it in the report.

The payoff artefact is `candidate-rule-catalogue.md` — one row per candidate *runtime* rule
found in the literature, each sourced. The gating test for every paper:

> Could this be written as a function mapping observable agent state → action, per agent,
> with **no dialogue at runtime**? If no, and the paper offers no evidence about when such
> rules hold, exclude it.

### Assumptions I am making (issue was not ambiguous, but these are judgement calls)

- **A1. Branch base.** `github_issue_workflow.md` says branch from an up-to-date `main`. But
  `main` contains **no** `literature/` and **no** `refs/` — every literature PR (#9, #13, #15,
  #17, #19) is still open, and the established convention in this repo is that each issue
  branch is cut from the previous issue branch. I therefore cut this branch from
  `origin/docs/18-demographic-paper-summaries` (`f3427b1`), so prior literature and the
  `refs/` cache stay readable and citable. Deviation logged here deliberately.
- **A2. "Verified" means I opened the page myself.** Following the standard already set by
  issues #16/#18, every entry records whether I read the **full text** or the **abstract page
  only**, and locators are scoped accordingly (an abstract-only entry cites abstract sections,
  never invented page numbers).
- **A3. Paywalled classics.** Several `[foundational]` seeds (Maynard Smith & Price 1973,
  Maynard Smith & Parker 1976, Aumann 1974/1987, Schelling 1960, Lewis 1969) are behind
  publisher paywalls or are printed books. Where I cannot open the primary text, I will say so
  in `search-log.md` and **not** fabricate a locator into it. A confirmed bibliographic record
  (Crossref/publisher page) plus an explicitly-marked secondary statement of the definition is
  the fallback, and it will be labelled as such.

## Plan

1. Set up branch + work log; create `literature/game-theory/`. **(done)**
2. Read the three arXiv G1 seeds and the G4/G5 seeds — cache each to `refs/`.
3. Verify every `[secondhand]` foundational seed's bibliographic record; open primary text
   where reachable; report honestly where not.
4. Mine the G4 survey (`arXiv:2003.11959`) for the sequential-chicken and Stackelberg
   pedestrian work, then confirm each referenced paper independently.
5. G5: Science Advances paper + the data-leakage critique + the authors' reply. Record the
   critique's *specific* technical objections (incl. the strategy-label presentation point).
6. G6 (lower priority): search for convention/strategy transfer across structurally different
   games. Report thinness honestly if thin.
7. Write the six sub-area files using the issue's per-paper template.
8. Write `candidate-rule-catalogue.md` (draft, pending supervisor review) — one row per rule,
   every row sourced, no merging of similarly-named rules.
9. Write `search-log.md` including the required **framing check** (does the literature support
   calling this FYP's extracted pattern a *convention* or a *correlated equilibrium*?).
10. Write `refs-game-theory.bib`; verify acceptance criteria one by one; PR.

## Progress log

### 2026-09-30 — Branch and work log created
- What I did: checked preconditions (`gh auth` OK, tree clean), inspected branch topology,
  cut `docs/20-game-theory-conflict-rules` from `origin/docs/18-demographic-paper-summaries`,
  created `literature/game-theory/`, seeded this log.
- Why: workflow step 0–3. Base choice explained in A1 above.
- Result / what I found: all five prior literature PRs are open; `main` has no `literature/`.
  `refs/ashery2025_social_conventions_oa.html` is **already cached** from issue #16, so the G5
  anchor paper is partly in hand already.
- Next step: fetch and read the G1 arXiv seeds.

### 2026-09-30 - Sourcing and verification pass
- What I did: resolved every arXiv seed to its published version; fetched and cached 24
  Crossref records plus publisher/repository copies; read in full: Foley 2018 (RSIF),
  Chen 2017, Hall 2020, Shoham & Tennenholtz (AAAI-92), Centola & Baronchelli 2015,
  Morris-Martin 2019, Ganguly & Ray 2023, Bonnemain 2023, Camara 2021 (published version),
  Fox 2018, Bouzat & Kuperman 2014, Ashery 2025, Barrie & Toernberg 2025, Ashery reply 2025,
  Rossetti 2025, Cross 2025.
- Why: the issue's sourcing rules forbid citing anything not opened, and prefer published
  versions over preprints.
- Result / what I found:
  - **All five arXiv seeds are published.** Foley -> J. R. Soc. Interface 15:20170835 (2018);
    Chen -> Sci. Rep. 7:4800 (2017); Hall -> J. Theor. Biol. 493:110101 (2020); Bonnemain ->
    Phys. Rev. E 107:024612 (2023); Camara -> IEEE T-ITS 22(9):5453-5472 (2021).
  - **All 12 `[secondhand]` seeds confirmed to exist. None was "not found."** But 7 could
    not be *opened* (paywalls and printed books), so 4 of the `[foundational]` definitions
    the issue asked me to record - Aumann, Schelling, Lewis, Maynard Smith & Parker - are
    **not** in the review. Stated per entry rather than paraphrased from second hand.
  - **Citation error in the top-priority seed.** Foley et al. cite Maynard Smith & Parker
    (1976) as "Nature 146:15-18", conflating it with Maynard Smith & Price (1973). Correct:
    Animal Behaviour 24:159-175. Caught only because I checked independently.
  - **Workaround for the Shoham & Tennenholtz paywall**: the 1995 AIJ version the issue
    named is paywalled, but the AAAI-92 conference version is free and covers the same
    model. Read that, and said so on every locator.
- Next step: write the six sub-area files.

### 2026-09-30 - A mistake worth logging: I guessed three identifiers and got three wrong papers
- What I did: guessed an arXiv ID for Bouzat & Kuperman, an arXiv ID for Johora & Mueller,
  and a PMC ID for Centola & Baronchelli, instead of looking each up.
- Result / what I found: all three downloads were the **wrong paper** - a differential
  geometry survey, a face-recognition paper, and a phylogenomics paper respectively. All
  three were caught by checking the first page of the extracted text against the expected
  title, and the files were deleted. Correct IDs were then obtained properly
  (arXiv:1311.1708; PMC4343158 via the Europe PMC API; Johora & Mueller has no open copy).
- Why it matters: **no wrong-paper content reached any deliverable**, but it easily could
  have. This is why every entry in the review names the exact `refs/` file it was read from,
  and why the mistake is recorded in `search-log.md` section 2 rather than quietly fixed.
- Next step: apply the same first-page check to anything added later.

### 2026-09-30 - Sub-area files written, and the framing check came back partly negative
- What I did: wrote all six sub-area files, `candidate-rule-catalogue.md`, `search-log.md`
  (including the required framing check) and `refs-game-theory.bib`.
- Why: deliverables listed in the issue.
- Result / what I found - the three findings that actually change the project:
  1. **The supervisor's hypothesis is well supported.** 11 candidate rules catalogued; only
     R10 needs runtime communication, and it stops needing it once the simulator supplies
     types. Communication-free conflict resolution is the norm in this literature, not the
     exception.
  2. **The framing check is partly negative, which is a useful finding.** Two standard
     definitions of *convention* require the alternatives to be *equivalent* (Ashery reply;
     Centola & Baronchelli Introduction; Foley section 4). The FYP's scenarios are
     anti-coordination games where yielding costs more than proceeding, so they fail that
     test. **"Social law"** (Shoham & Tennenholtz, Definitions 2.1 and 3.1) fits exactly and
     has no equivalence requirement. Recommended reframing, needs sign-off.
  3. **A negative result I did not expect: no arrival-order rule exists in anything I read.**
     "Whoever arrived first passes first" - the issue's own paradigm case - appears in no
     paper. Worse, Foley et al. section 4 find the **host-guest** norm (the one already there
     *concedes*) "evolves far more readily" than the ownership norm. That is the opposite of
     first-come-first-served. Either the rule lives in an unobtained source, or this is a gap
     the FYP could fill.
- Next step: verification pass, then PR.

### 2026-09-30 - Verification (workflow step 5b, no test suite applies)
- What I did: (a) confirmed all 9 required deliverables exist; (b) checked all 36 BibTeX keys
  referenced in the prose are defined - 0 undefined; (c) checked all 29 `[Paper-Handle]`
  cross-references resolve to a definition - 0 dangling; (d) checked every inter-file
  markdown link resolves - 0 broken; (e) checked every `refs/gt_*` cache file named in the
  review exists on disk and is tracked in git - 0 missing, 62 files committed; (f) re-read
  each entry to confirm its locators are scoped to what was actually read.
- Result: all clean. "Open questions / risks" below is non-empty (7 risks), as step 5b
  requires.
- Next step: PR.

### 2026-10-02 - Three previously-unobtainable papers supplied by the user, read, and folded in
- What I did: the user supplied PDFs for Camara et al. (2018, Measuring Behavior), Duffy & Feltovich
  (2010, IER) and Johora & Mueller (2018, IEEE ITSC), and reported Maynard Smith & Parker (1976) and
  Mesterton-Gibbons et al. (2014) as unobtainable. Cached all three under `refs/`, read each in full,
  verified every quoted passage against the extracted text, and wrote
  `literature/game-theory/conflict-avoidance-shortlist.md`.
- Why: the user asked for a filtered shortlist against a sharper criterion than the issue's -
  *rules agents follow so that conflict does not arise in the first place* - plus detailed summaries.
- Result / what I found:
  - **A distinction the sub-area files had not made:** the shortlist splits into **ex-ante**
    (the clash never arises) and **ex-post** (the clash happens, then a procedure picks a winner).
    Two of my earlier top picks - Bouzat & Kuperman, Duffy & Feltovich - are ex-post. Said so.
  - **Johora & Mueller is the most transferable paper in the whole review.** Three-layer simulator
    (A* / social-force reactive rules / one-shot Stackelberg games), validated against 117 real
    conflict scenarios from Hamburg video. It contains an **ablation** (section IV-b): with the game
    layer removed, "all cars deviate from their trajectory instead of stopping and pedestrians
    sometimes go back and forth" - i.e. removing the rule layer reproduces the exact deadlock this
    FYP targets. And its **12-parameter payoff function is explicitly uncalibrated** (section
    III-C-1), which is a precisely-shaped opening for LLM-elicited payoffs.
  - **Camara et al. gives the FYP's own method template** - define a game, leave the human-preference
    parameters free, measure them, fold into a controller - and a warning: the fitted optimum was
    (U_crash, U_time) ~ (0, 30), i.e. participants behaved as though crashing were free, which the
    authors attribute to the board-game framing (section 4). A text prompt to an LLM is at least as
    artificial a frame.
  - **Duffy & Feltovich at full text changed one of my claims.** The abstract-only entry recorded
    that recommendations work when payoff-enhancing. The full text adds a finding I could not see
    before: **no correlated equilibrium arose spontaneously without the mediator** (p. 719). The
    signal has to be supplied. Also found two citation errors in its reference list (Gul, and
    Hart & Mas-Colell), recorded.
  - Found an **open question in Duffy & Feltovich (p. 720)** that reads as a brief for this FYP:
    does the *form* of a recommendation matter, and must the message space match the action space?
    An LLM is exactly a natural-language recommendation device over an unbounded message space.
- Housekeeping, so the read-depth labels stay honest: upgraded the Duffy entry in G1 from
  abstract-only to full text; filled in the Johora entry in G4, which was previously a
  confirmed-but-unopened lead with blank template fields; added a Camara 2018 entry to G4; corrected
  the Fox human-validation bullet, which had attributed the human fit to the T-ITS survey's summary;
  added rules **R12-R14** and a fifth correspondence to the rule catalogue; updated the acquisition
  list in `search-log.md` section 9; added `camara2018empirical` to the bib and rewrote two notes.
- Verified: all 30 paper-handle cross-references resolve, all 37 bib keys referenced in prose are
  defined, 0 broken inter-file links, no stale "not opened" claims remain for the three acquired
  papers.
- Next step: none outstanding for this request. The two still-missing papers both bear on risk R6
  (whether an arrival-order rule exists in this literature).

## Open questions / risks

Carried forward into `literature/game-theory/search-log.md` section 10, which is the
canonical list. Summarised here:

- **R1 (was a risk, now confirmed).** 7 cited works were never opened, including 4 of the
  `[foundational]` definitions the issue asked for. Every affected entry says so and asserts
  no definition without a locator into something I read. **The report must not quote Aumann,
  Schelling, Lewis or Maynard Smith & Parker until they are obtained from the library.**
- **R2 (confirmed).** G6 is thin - 1 qualifying entry. Reported as such rather than padded,
  which the issue explicitly permitted. 7 confirmed-but-unobtained leads are listed so the
  search is not repeated.
- **R3 (confirmed, and the most consequential finding).** The framing check came back
  **partly negative**: the equivalence-based definitions of *convention* do not fit the FYP's
  scenarios. Recommended term is **social law**. Needs supervisor sign-off.
- **R4 (new, and the risk with the largest downside).** `arXiv:2409.00993` - Horiguchi,
  Yoshida & Ikegami (2024), "Evolution of Social Norms in LLM Agents using Natural Language"
  - is **LLM agents deriving norms through dialogue**, i.e. the FYP's own method, posted as a
  preprint in 2024. Only its first page was read. **Until it is read in full, the FYP's
  novelty claim is unverified.** A novelty check of the kind issue #16 ran is needed.
- **R5 (new).** By the defenders' own argument, **this FYP is more exposed to the
  data-leakage critique than Ashery et al. are.** Their defence is that a naming game has no
  right answer; the FYP's scenarios (doorway deadlocks, bottlenecks, queue-cutting) have
  literature-attested answers. A reframing is proposed in `g5-llm-agents-game-theory.md`
  section 4: claim the LLM is a usable *elicitation device* for literature-consistent rules,
  which are then extracted and tested independently - a claim that survives the leakage
  objection entirely. Needs sign-off.
- **R6 (new).** Four entries were read as **preprints, not published versions** (Chen, Hall,
  Bonnemain, Bouzat & Kuperman). Section and equation numbers may differ. Each entry carries
  the warning; they must be re-checked before the report quotes page numbers.
- **R7 (new).** G3 is the genuine shortfall: only **one** entry there is both peer-reviewed
  and read in full, and that sub-area's conclusion rests substantially on it. Obtaining
  Farrell & Rabin (1996) is the highest-value small task remaining.

## Summary

**What changed.** Added `literature/game-theory/` with the nine deliverables the issue
specified: six sub-area files (G1-G6), `candidate-rule-catalogue.md`, `search-log.md` and
`refs-game-theory.bib` (36 entries). Added 62 cached source files under `refs/` so every
locator can be re-checked later. Updated `README.md` with roadmap step 5b and the headline
findings.

**Why.** Issue #20 sharpened the FYP's extraction target after the latest supervisor meeting:
the pattern need not be a dialogue pattern, and may be a rule agents follow to reach consensus
without communicating at all - and it should not be tied to spatial conflict. This review
collects the theory and applied work needed to define that object precisely and defend it in
the report.

**What it found, in one line each.**
1. **The supervisor's hypothesis holds.** 11 candidate runtime rules catalogued; only one
   needs runtime communication, and not even that one if the simulator supplies types.
2. **"Convention" is the wrong word; "social law" is the right one.** The framing check came
   back partly negative, which is a useful finding rather than a failure.
3. **Do not let the rule emerge in-simulation.** Two independent sources find global
   conventions fail to form in spatially structured populations. A crowd is spatially
   structured - which is an argument *for* the offline LLM extraction this project already
   does.
4. **No arrival-order rule exists in anything read**, and the closest analogue points the
   other way. Possibly a gap the FYP can fill.
5. **The FYP is more leakage-exposed than the paper it would cite for support**, and a
   defensible reframing is proposed.

**How it was verified.** No test suite applies; workflow step 5b was followed. All 9
deliverables present; 36/36 BibTeX keys referenced in prose are defined; 29/29 paper-handle
cross-references resolve; 0 broken inter-file links; every `refs/gt_*` cache file named in the
review exists on disk and is tracked (62 committed); every entry's locators re-read and
confirmed scoped to what was actually opened.

**What is explicitly NOT claimed.** No definition is asserted for Aumann's correlated
equilibrium, Schelling's focal point, Lewis's convention, or Maynard Smith & Parker's
uncorrelated asymmetry, because those primary texts could not be opened. Four entries were
read as preprints and say so. G3 and G6 are flagged as thin. An acquisition list in priority
order is in `search-log.md` section 9.
