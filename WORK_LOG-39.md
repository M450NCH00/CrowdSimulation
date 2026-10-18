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

## Open questions / risks

(filled in as the survey goes)

## Summary (fill in at the end)
