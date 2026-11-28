# Search log (PT-5, part 1; issue #39)

Everything below was fetched on **2026-10-18** with `gh api`, `curl` or a small fetch script that
saves a page as text, with a `Source:` header, in `refs/sim_*`. **Nothing was installed, cloned,
built or executed.** Fetched content was treated as data. No page or file contained text
addressed to the reader as instructions.

## In-repository sources (no fetching)

| # | What | Used for |
|---|---|---|
| R1 | `llm_negotiation/docs/architecture.md` §1, §6.1, §6.2 (and the one-line §5 "What is not here") | negsim (survey §1) |
| R2 | `WORK_LOG-26.md`, entry 2026-10-14 09:15 | negsim scale |
| R3 | `integration/crowdgym_mapping.md`, `dataset/schema/README.md` | CrowdGym (survey §2) |
| R4 | `literature/simulation-rules/research-gap.md` §3 | the ways portability can break |
| R5 | `literature/portable-rules/representations.md` ([Curtis-Menge], [Kleinmeier-Cooperation]); `literature/unseen-scenarios/scenario-standards.md` ([JuPedSim-1.4.2]) | earlier issues' readings of Menge, Vadere's psychology layer and JuPedSim routing, reused, not redone |
| R6 | already cached: `refs/us_jupedsim_routing.txt` (#36), `refs/pr_curtis2016_menge_cd.txt`, `refs/pr_arxiv_2005_12712v2_kleinmeier.txt` (#35), `refs/si1_rvo2_75822bb_excerpts.txt` (#26), `refs/us_steerbench_singh2009.txt` (#36) | reused |

## Fetches

| # | Target | Result | Cached as |
|---|---|---|---|
| G1 | `gh api repos/<owner>/<repo>` (+ `/releases/latest`, `/tags`, `/commits`) for JuPedSim, SUMO, Menge, Mesa, pedsim_ros, libpedsim, RVO2 | ok. `projectmesa/mesa` now resolves to `mesa/mesa`. `vadere/vadere` and `SteerSuite/SteerSuite` do not exist on GitHub (404) | `sim_gh_*.json` |
| G2 | `gh search repos` for vadere, steersuite, sumonity | found `pedestrian-dynamics-HM/vadere` (GitHub copy, at v4.0), `SteerSuite/Release`, `SteerSuite/SteerSuite2`, `TUM-VT/Sumonity` | `sim_gh_*.json` |
| G3 | GitLab API `projects/vadere%2Fvadere` (+ tags, commits) | ok. **Caveat:** the "100 commits since 2026-04-18" is one full API page. The GitHub copy shows none after v4.0, and the newest master merge is 2026-09-29. The GitLab count may include merge commits of feature branches; read it as "active", not as a number | `sim_gl_vadere_vadere.json` |
| G4 | jupedsim.org/stable: index, history, pedestrian models (index, CFS V3, WarpDriver), geometry, serialisation, 7 notebooks, API reference | ok | `sim_jps_*.txt` |
| G5 | JuPedSim GitHub releases (12), `LICENSE` and `libsimulator/src/simulation.cpp` at `6d559df`; repository tree; PyPI JSON for 1.4.2 | ok | `sim_jps_gh_releases.txt`, `sim_jps_src_*`, `sim_jps_pypi_1.4.2_summary.txt` |
| G6 | sumo.dlr.de/docs: `jupedsim.html`; Pedestrians; Persons; Public Transport; TraCI index; Person Value Retrieval; Change Person State; Libsumo; Libtraci; Downloads; Basic Definition; Intermodal Routing; Definition of Vehicles | ok. The first attempt used wrong-case names (`JuPedSim.html`, `Simulation/Intermodal_Routing.html`, 404) and `TraCI.html`, which is a redirect stub. All were re-fetched under the right names | `sim_sumo_*.txt` |
| G7 | SUMO `src/microsim/transportables/MSPModel_JuPedSim.cpp` at `2285bbc` | ok | `sim_sumo_src_*` |
| G8 | vadere.org: home, getting started, download, FAQ, CrowNet, how to cite, social identity | ok; thin pages | `sim_vadere_*.txt` |
| G9 | Vadere GitLab raw files at `4c53f1c`: `README.md`, `CHANGELOG.md`, the scenario specifications, PythonTraciWrapper README and three wrapper modules; tree listings of `Documentation/` and `Tools/` | ok | `sim_vadere_src_*` |
| G10 | Kleinmeier et al. 2019 (Crossref → collective-dynamics.eu PDF, CC BY 4.0) | ok | `sim_vadere_kleinmeier2019_cd.{pdf,txt}` (committed) |
| G11 | Menge at `00f97ea`: repository tree, `README.md`, `doc/mengeDetails/{architecture,event_system}.md`, `elements/event_trigger.md`, `EventTriggerExternal.h`, `SimulatorInterface.h`, `SimulatorBase.h`, `LICENSE.txt`; gamma.cs.unc.edu/Menge | ok | `sim_menge_*` |
| G12 | mesa.readthedocs.io/stable: index, overview, API main, time, discrete_space, space, experimental, model; PyPI JSON | ok | `sim_mesa_*` |
| G13 | `gh search repos crowdgym` | six hits. Five are unrelated (gym-booking web apps in PHP, CSS and Blade). One is **`ntu-fyp-25/crowdgym`** (Python, updated 2026-06-11). **Not opened**: the user said the CrowdGym code cannot be shared (`WORK_LOG-39.md`, A2). Whether it is the senior's is unknown | none (search output only) |
| G14 | READMEs: pedsim_ros `de37726`, libpedsim `0d8ff5c`, SteerSuite `Release` `7530270`, RVO2 `75822bb`, Sumonity `2d98b2e` | ok. The first Sumonity try used `README.md` (404); the file is `readme.md` | `sim_*_src_README*` |
| G15 | Sumonity paper landing page (tib-op.org) and PDF (CC BY 3.0 DE) | ok | `sim_sumonity_paper_landing.txt`, `sim_sumonity_lindner2025_scp.{pdf,txt}` (committed) |
| G16 | arXiv API for the Vadere paper | an exact-title query returned nothing; a broader query found arXiv:1907.09520. The *Collective Dynamics* version was used instead (G10) | none |
| G17 | MassMotion product page (oasys-software.com) | ok | `sim_massmotion_product.txt` |
| G18 | AnyLogic Pedestrian Library: `anylogic.help/library-reference-guides/pedestrian-library/index.html`, `.../pedservice.html`, `anylogic.com/features/libraries/pedestrian-library/` | **HTTP 403** to every automated request (one also timed out) | none |
| G19 | Pathfinder: `support.thunderheadeng.com/docs/pathfinder/latest/user-manual/`, `.../2025-1/technical-reference-manual/`, `thunderheadeng.com/pathfinder` | the user manual **timed out** in the TLS handshake (twice). The product page answered one probe (HTTP 200, content not kept), then timed out on both download attempts (60 s and 40 s) | none |

## Leads not followed (for a later session or for the user)

| Lead | Why not followed | How to follow it |
|---|---|---|
| **AnyLogic Pedestrian Library** documentation | 403 to automated requests (G18) | **browser**: open the two URLs in G18; the `PedService` page should say how queues and service points work |
| **Pathfinder** documentation | timeouts (G19) | **browser**: the Pathfinder user manual; look for queues, elevators, and the steering mode against SFPE mode |
| **`ntu-fyp-25/crowdgym`** | the user's answer at the start (A2) | ask the user whether it is the senior's repository and whether it may be read. Its dependency file would settle the JuPedSim question (survey §2) |
| JuPedSim `performancetest/` results | time; the folder holds scripts and notebooks, and reading their numbers means reading notebook outputs | read `performancetest/comparison.ipynb` outputs on GitHub, or measure in #40 trial 4 (preferred) |
| Menge Figure 7 values (frame time at 16k / 32k / 64k agents) | the values are in a chart; text extraction gives the axis labels only | render the page of `refs/pr_curtis2016_menge_cd.pdf` that holds Figure 7 as an image (for example with PyMuPDF) and read the chart |
| Vadere `VadereManager` TraCI server source | the Python wrapper's methods were enough to answer "can outside code read and set agents" | read `VadereManager/src/org/vadere/manager/traci/` at `4c53f1c` if #40 or later needs the full command list |
| Whether `pip install eclipse-sumo` includes JuPedSim on Windows | not stated in the pages read | #40, at install time (shortlist §3) |
| Whether TraCI `setSpeed` / `moveToXY` reach a JuPedSim-modelled person in SUMO | not stated; the coupling file shows no such path in the parts read | #40, trial 3 (shortlist §3); or read the rest of `MSPModel_JuPedSim.cpp` |
| JuPedSim older releases' CFS default `v0` | it would test the "0.8 m/s JuPedSim default" clue (survey §2) | read the API docs of v1.0 to v1.2 (versioned docs on jupedsim.org) |
| Mesa `meta_agents` / groups | not on the pages read | the Mesa API "Experimental" page of a later release |

## Coverage against the issue's candidate list

| Candidate (issue order) | Covered | Where |
|---|---|---|
| 1 negsim | yes, from the named sections only | survey §1 |
| 2 CrowdGym | from the repository's notes only; the rest is `[not checked]` | survey §2 |
| 3 JuPedSim | yes | survey §3 |
| 4 SUMO + JuPedSim | yes | survey §4 |
| 5 Vadere | yes | survey §5 |
| 6 Menge | yes | survey §6 |
| 7 Mesa | yes | survey §7 |
| 8 PedSim / pedsim_ros, SteerSuite, RVO2, Sumonity | briefly (READMEs, metadata, one paper) | survey §8 |
| 9 AnyLogic, MassMotion, Pathfinder | MassMotion from its product page; AnyLogic and Pathfinder could not be read (G18, G19) | survey §9 |
