# Work Log — Issue #39: [Research] PT-5 Simulators, part 1: desk survey of crowd simulators and how they work

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/39
**Branch:** `docs/39-simulator-desk-survey`
**Started:** 2026-10-18

## Understanding the issue

Track #34 proposes (**not agreed; needs the supervisor's sign-off**) a portable rule core: rules
stated over a fixed vocabulary, with two adapters per simulator (state → *Situation*, *Decision* →
the simulator's own controls). Testing that idea needs simulators that differ from negsim in the
ways portability can break (continuous or discrete space, fixed steps or events, motion model,
infrastructure), a simulator that can host queues, service points and vehicles, and eventually
CrowdGym.

This issue is the desk half of the choice: for each candidate, find out how it works (one step,
motion models, behaviour layer, space and time, scenario description, native support for queues,
waiting areas, service points, vehicles, groups and events, where the two adapters would attach,
reported scale, and practicalities), from documentation, papers and source read on GitHub.
**Nothing is installed, cloned-and-run or executed.** The hands-on trial and the use-or-build
decision are #40 (PT-6).

Candidates in priority order: negsim (from `architecture.md` §1, §6.1, §6.2 only), CrowdGym (from
the repo's two notes), JuPedSim, SUMO with its JuPedSim coupling, Vadere, Menge, Mesa; then, if
budget remains, PedSim / pedsim_ros, SteerSuite, RVO2, Sumonity; then a paragraph each on AnyLogic,
MassMotion and Pathfinder.

Deliverables: `integration/simulator-survey/{survey,comparison,shortlist,search-log}.md`, and the
cached pages in `refs/`.

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** As in #36 to #38, `origin/main` does not contain the earlier track files
  (`literature/portable-rules/`, `literature/unseen-scenarios/`), which this survey cross-references.
  I cut this branch from `docs/38-trained-deciders-literature` (PR #46, head `6df0e64`, in sync with
  origin) and will target the PR at it. A merge into a non-default branch will not close #39 by
  itself.
- **A2. CrowdGym.** I asked the user at the start, as the issue requires; the answer (2026-10-18)
  was that the report and code **cannot be shared now**. CrowdGym is described only from
  `integration/crowdgym_mapping.md` and `dataset/schema/README.md`, and everything those notes do
  not settle is listed as not checked.
- **A3. Cache prefix** `refs/sim_*`, following `pr_*` (#35), `us_*` (#36), `he_*` (#37), `td_*`
  (#38). Files cached by earlier issues (`refs/us_jupedsim_routing.txt`,
  `refs/pr_curtis2016_menge_cd.txt`, `refs/pr_arxiv_2005_12712v2_kleinmeier.txt`) are reused, not
  fetched again.
- **A4. What is committed** (the repository is public; same rule as #35 to #38). Committed: GitHub
  metadata (`gh api` JSON, facts), arXiv and CC-licensed papers, and documentation that states an
  open licence. Documentation pages and source files with no stated licence for the text are kept
  on disk only and listed in `.gitignore` with their URL, so they can be re-fetched.
- **A5. "Reading source on GitHub"** means fetching single files at a pinned commit through
  `raw.githubusercontent.com` or `gh api`, saving them in `refs/`, and searching them with grep. No
  clone, no build, no import, no execution.
- **A6. "Version read".** For documentation, the version the page states (e.g. "stable" = a release
  number); for source, the commit SHA of the default branch on 2026-10-18, recorded in each section.

## Plan

1. Branch and work log; ask the CrowdGym question. **(done)**
2. negsim and CrowdGym from the in-repo documents (no fetching).
3. JuPedSim: GitHub metadata, routing (cached), the Python API reference for `Simulation`, agent
   state, motion models, release notes; source of `simulation.py` at a pinned commit.
4. SUMO + JuPedSim coupling: the coupling page, the pedestrian / person / stop pages, TraCI.
5. Vadere: site, GitHub metadata, the psychology layer (cached arXiv:2005.12712), the remote
   control (TraCI) interface, scenario format.
6. Menge: site, GitHub metadata, cached Curtis et al. 2016, plug-in / external-control points.
7. Mesa: docs (space, scheduling, event-driven `DEVSimulator`), metadata.
8. If budget remains: PedSim / pedsim_ros, SteerSuite, RVO2, Sumonity; commercial tools.
9. `comparison.md`, `shortlist.md`, `search-log.md`; verification pass (every cell sourced, every
   acceptance criterion); push and PR against the #38 branch.

## Progress log

### 2026-10-18 — Start
- What I did: read the issue (no comments), `github_issue_workflow.md`, and the track memory. Asked
  the user once about CrowdGym (answer: cannot share now). Created the branch from the #38 branch.
  Read `architecture.md` §1, §6.1, §6.2, `crowdgym_mapping.md`, `dataset/schema/README.md` and
  `research-gap.md` §3. Found earlier caches for JuPedSim routing, Menge and Vadere's psychology
  layer.
- Why: the issue names these as the sources for negsim and CrowdGym, and §3 as the list of ways
  portability can break.
- Result / what I found: `crowdgym_mapping.md` says CrowdGym keeps "the physical movement model
  (CFS ...)" running and routes agents with an `AgentJourneyDirector`, and that the senior's
  verification speed of 0.8 m/s was "a JuPedSim default". Those are clues, not an answer: see the
  CrowdGym section of the survey.
- Next step: fetch JuPedSim's documentation and metadata.

### 2026-10-18 — Metadata for every candidate
- What I did: `gh api` for each repository (licence, last release, tags, head commit, commits in the
  last six months), saved as `refs/sim_gh_*.json`; the GitLab API for Vadere.
- Why: the issue asks for licence, last release and recent activity from the GitHub metadata.
- Result / what I found:
  - `projectmesa/mesa` now resolves to `mesa/mesa`;
  - `vadere/vadere` and `SteerSuite/SteerSuite` are not on GitHub. Vadere lives on GitLab LRZ, with
    a GitHub copy at `pedestrian-dynamics-HM/vadere`;
  - **mistake:** my first loop wrote the 404 body of `/releases/latest` in front of `null`, which
    made five files invalid JSON. I noticed when a summary script failed, repaired them with a small
    script, and pretty-printed all twelve.
- Next step: JuPedSim.

### 2026-10-18 — JuPedSim, SUMO, Vadere, Menge, Mesa
- What I did: cached the documentation pages and single source files listed in `search-log.md`
  (G4 to G12) and searched them with grep. I did not read whole pages into the conversation.
- Result / what I found (the facts are in `survey.md`; these are the turning points):
  - JuPedSim's `iterate()` runs strategic → tactical → operational systems
    (`simulation.cpp:96-132`). There is no per-step callback.
  - JuPedSim's `agent.target` is ignored unless the journey is a single direct-steering stage.
  - JuPedSim 1.4.x defaults `desired_speed` to 1.2 m/s for CFS and to 0.8 m/s only for the social
    force model. That bears on the CrowdGym question.
  - SUMO's coupling runs several JuPedSim iterations per SUMO step (`MSPModel_JuPedSim.cpp:412-417`).
    Only the CFS model is "tested extensively".
  - Vadere's optimal steps model is event-driven (Kleinmeier 2019, §2.1.4). Its Python TraCI
    wrapper is marked work in progress.
  - Menge has an `ExternalEvtTrigger` meant for outside code, and an aircraft-boarding plug-in.
  - Mesa 3.5 moved event scheduling onto `Model`.
  - **Dead ends:**
    - first SUMO fetches used wrong-case page names (404), and `TraCI.html` is a redirect stub;
      all were re-fetched;
    - an exact-title arXiv query for the Vadere paper returned nothing. I used the *Collective
      Dynamics* copy (CC BY 4.0), found through Crossref.
- Next step: the lower-priority tools and the commercial tools.

### 2026-10-18 — Lower priority and commercial tools; the CrowdGym search hit
- What I did: READMEs and metadata for pedsim_ros, libpedsim, SteerSuite, RVO2 and Sumonity; the
  Sumonity boarding paper (CC BY 3.0 DE); MassMotion's product page. Tried AnyLogic and Pathfinder.
- Result / what I found:
  - AnyLogic answers automated requests with HTTP 403, and Pathfinder timed out. Both are stubbed
    as *browser* leads; nothing is claimed about them.
  - A `gh search repos crowdgym` (to see whether a public CrowdGym exists) listed
    `ntu-fyp-25/crowdgym` (Python, 2026-06-11). **I did not open it.** The user had just said the
    code cannot be shared, and reading it anyway would go around that answer. I am asking instead
    (Q1).
- Next step: write `survey.md`.

### 2026-10-18 — survey.md, comparison.md, shortlist.md, search-log.md
- What I did: wrote the four deliverables and committed each.
  - `comparison.md` is the matrix split into four tables (A to D), all with the same rows. One
    Markdown table with twenty columns would not be readable. **This is a judgement call:** the
    issue says "one matrix"; the four tables are that matrix, split by column group.
  - A script checked that every cell has a source key, or a `[not documented]` / `[not checked]`
    marker. It flagged the Fit column (my inferences, with no key), so each Fit cell now points to
    its survey section.
- Two findings came up while writing the shortlist, and were added to the survey and matrix:
  - JuPedSim's CFS states expose no current velocity;
  - standard SUMO "teleport[s] passengers onto the bus" (Lindner et al. 2025, §3.2).
- Shortlist: JuPedSim (second continuous testbed, queues and waiting), Mesa (discrete queue model),
  and SUMO + JuPedSim as a conditional third (boarding host). Each comes with what #40's trials
  must test.
  - Vadere and Menge are not shortlisted. Chiefly, #40 may install only PyPI packages (Java and C++
    builds are excluded), and Menge is dormant. Vadere is named as the alternate.
- Next step: verification pass.

### 2026-10-18 — Verification pass (workflow §5b)
- What I did: re-checked every number in `survey.md` against its cached source (releases, dates,
  defaults, step lengths, scale figures, line ranges), and spot-checked the headings cited.
- Result: the numbers match. Seven locators were wrong and are fixed:
  - **survey, while writing:**
    - Menge's built-in ORCA and PedVO were cited to the paper, which does not name them; they now
      cite the repository tree;
    - two SUMO headings were wrong ("Vehicle Types" should be "Available vType Attributes";
      "Stops" should be "Stops and waypoints");
    - the `doors` sentence sits under "Access Lanes";
  - **survey, in this pass:**
    - the JuPedSim notebook names and the Zenodo DOI were cited to the cached index text, which
      has neither (links are dropped when a page is reduced to text);
    - the TraCI client/server sentence sits under "SUMO startup", not "Introduction";
  - **search log, in this pass:**
    - it said Pathfinder "timed out twice", but the product page had answered one probe before two
      download timeouts;
    - I had also written that AnyLogic's pages "open normally in a browser", which I never
      checked. Both are corrected.
- Also corrected: "Tau and Mass are parameters of the GCFM and social force models". JuPedSim's
  social force model calls it `reaction_time`, not `tau`.

## Open questions / risks

- **Q1 (for the user): is `ntu-fyp-25/crowdgym` the senior's CrowdGym, and may it be read?** A
  public repository by that name came up in a GitHub search. I left it unopened because of the
  answer "Can't share now". If it is CrowdGym and may be read, its dependency file answers "built
  on JuPedSim?" in minutes. Until then the question stays open (survey §2).
- **Q2. Shortlisting JuPedSim partly because of CrowdGym rests on Q1.** If CrowdGym turns out not
  to use JuPedSim, JuPedSim still stands as the second continuous testbed, but the "adapters carry
  over to the target" argument falls away.
- **Q3. The shortlist is shaped by #40's permission** (PyPI packages only). If the supervisor wants
  a continuous testbed that also differs in *time* (event-driven steps), that is Vadere, and it
  needs a Java exception that #40 does not grant.
- **Q4. "[not documented]" is not "absent".** Examples: JuPedSim groups, pedestrian queues in SUMO,
  vehicles in Vadere. These were looked for in the pages listed and not found. A feature documented
  elsewhere would change a cell. #40's trials are the check.
- **Q5. "stable" documentation moves.** The JuPedSim and Mesa versions are inferred from content
  (the model list; the 3.5.0 deprecation note), not stated on the pages. Documentation copies are
  disk-only (A4), so re-checking them later means re-fetching a page that may have changed.
- **Q6. Scale figures are not comparable.**
  - negsim's is measured on this laptop;
  - Menge's are in a chart I did not extract;
  - Vadere states only a qualitative limit;
  - JuPedSim, SUMO and Mesa state none.
  #40 trial 4 has to measure, not read.
- **Q7. Vadere's activity count** (100 commits in six months on GitLab) conflicts with its GitHub
  copy (none after v4.0). I report it as "active", not as a number (search log G3).
- **Q8. The commercial paragraph is thin.** AnyLogic and Pathfinder could not be read. MassMotion
  is described from a marketing page. None is a candidate, but a report that compares against
  practice would need the browser leads.
- **Q9. Design decision vs assumption.** The roles in the shortlist come from #34's point 6, which
  is a proposal, not agreed. So is every "fit" judgement, which is marked `[inference]`.

## Summary

**What changed.**
- `integration/simulator-survey/` (new):
  - `survey.md`: one section per simulator, using the template. negsim, CrowdGym, JuPedSim,
    SUMO + JuPedSim, Vadere, Menge and Mesa in full; pedsim_ros / libpedsim, SteerSuite, RVO2 and
    Sumonity briefly; MassMotion from public pages; AnyLogic and Pathfinder could not be read;
  - `comparison.md`: the matrix, a row per simulator and a column per template field, in four
    tables, every cell sourced;
  - `shortlist.md`: JuPedSim, Mesa, and SUMO (conditional), with what #40 must test with each;
  - `search-log.md`: 19 fetch groups, leads not followed, and coverage.
- `refs/sim_*`:
  - committed: metadata (12 JSON files), PyPI summaries, the Menge file listing, and two
    CC-licensed papers;
  - on disk only: documentation pages and single source files, listed in a new `.gitignore`
    block (A4).
- `README.md`: roadmap row 5i, three findings, and the layout entry.

**Why.** Track #34's idea needs testbeds that differ from negsim, a host for queues, service points
and vehicles, and CrowdGym as the target. #40 has to choose between using a simulator and building
one, and this survey is what it chooses from.

**How it was verified** (workflow §5b; there is no test suite for documents):
- every quantitative claim carries a section, file:line or page heading, and was re-checked
  against the cached text. Seven locators were corrected (verification entry above);
- a script confirmed that every cell of `comparison.md` has a source key or a
  `[not documented]` / `[not checked]` marker;
- "Open questions / risks" has nine entries;
- every candidate in the issue's list is covered, or the gap is explained (search log, coverage
  table);
- every source is cached in `refs/`;
- **nothing was installed, cloned-and-run or executed.** The only code run was my own fetch and
  formatting scripts in the scratchpad: `curl`, `gh api`, and `pdftotext` on two downloaded PDFs.

**Acceptance criteria:**

| Criterion | Where |
|---|---|
| negsim, CrowdGym, JuPedSim, SUMO, Vadere, Menge, Mesa covered, or gaps explained | `survey.md` §1–§7; CrowdGym's gaps are `[not checked]`, with the reason (A2) |
| Every cell in `comparison.md` cites a source or says `[not documented]` | `comparison.md`; script check, verification entry |
| Hooks for both adapters assessed for every candidate | `survey.md` "Hooks" lines; `comparison.md` table D |
| Queues, waiting areas, service points, vehicles assessed for every candidate | `survey.md` "Native support"; `comparison.md` table C |
| The CrowdGym question answered, or left open with what is needed | `survey.md` §2, "Is CrowdGym built on JuPedSim? Left open."; Q1 |
| Nothing installed, cloned-and-run or executed | this summary; search log header |
| `shortlist.md` names two or three candidates, and what PT-6 should test with each | `shortlist.md` |
| "Open questions / risks" not empty | Q1–Q9 |
