# Search log — issue #22

> For issue [#22](https://github.com/M450NCH00/CrowdSimulation/issues/22). All work was done on
> 2026-10-04. This file records what was searched, how each source was found and read, what was
> excluded, what went wrong, and what remains uncertain. §7 is the canonical list of open
> questions and risks.

Companion files: [S1](s1-crowd-simulation.md) · [S2](s2-games.md) · [S3](s3-mapf-robotics.md) ·
[S4](s4-traffic-vehicles.md) · [rule catalogue](rule-catalogue-simulation.md) ·
[category summary](category-summary.md) · [research gap](research-gap.md) ·
[pre-window foundations](pre-window-foundations.md) · [missing papers](missing-papers.md) ·
[refs](refs-simulation-rules.bib)

---

## §1. What was read first

- The issue, and `github_issue_workflow.md`.
- Issue #20's outputs, because this issue must cross-reference them:
  `literature/game-theory/candidate-rule-catalogue.md` (rules R1–R14 and its §2–§3),
  the opening of `conflict-avoidance-shortlist.md`, the arrival-order passages of its
  `search-log.md` (§9–§10), and `WORK_LOG-20.md`.
- **Not read:** `integration/crowdgym_mapping.md` and `dataset/schema/README.md`. CLAUDE.md asks
  for these to be checked before proposing anything that touches CrowdGym. Nothing here proposes a
  CrowdGym change — the issue puts implementation out of scope — so I did not open them. Every
  "Relevance to this FYP" line is therefore about the FYP's stated aims, not about CrowdGym's
  actual interfaces. **If these files are used to plan implementation, that mapping still has to
  be done.**

## §2. Method, stated so it can be audited

**Fetching.** Sources were downloaded with `curl` and converted with `pdftotext -layout`. Every
download was checked against its expected title on the first page before anything else was done
with it — the safeguard adopted after issue #20's three wrong-paper downloads. No wrong paper was
downloaded this time. Identifiers were looked up through the arXiv API or Crossref by title; none
was guessed.

**Published versions.** For every arXiv seed and every arXiv addition I checked the arXiv record's
journal reference and DOI fields and, where those were empty, searched Crossref by title. Results
are in §3–§4.

**Caching.** Everything is under `refs/sr_*`. Six PDFs over 5 MB are git-ignored with their text
extracts tracked (`.gitignore`); locators refer to the `.txt` files.

**What "read" means here.** Each entry's *Verified* line states one of:
- *full text read* — every section of the body;
- *partly* / *selectively* — with the sections read listed, and the sections not read listed.

**Nine entries were read selectively**: [Grover-Deadlock], [Wang-MAPFSurvey], [Zhang-Mutex]
(formal sections skimmed), [Jenner-DriverSF], [MartinezBaselga-AVOCADO] (related work and proofs
skipped), [ShalevShwartz-RSS], [Malikopoulos-SignalFree], [Shah-AROW], [Mariani-CoordSurvey].
The issue's template says "Verified: yes (full text read)". For these nine I have written what is
true instead, and scoped every claim to the sections read. In three further entries the main text
was read in full but an appendix was not: [Okumura-PIBT], [Zhou-LSRP], and [Yang-S2AN] (whose
appendix was not in the copy obtained).

**What text extraction lost.** This affects what could be reported, and is flagged per entry:
- *Equations.* Most mathematical symbols are dropped. For [Sung-ArrivalTime] every equation body
  is gone; for others most are. Rules are described from the surrounding prose.
- *Figures.* Anything shown only in a plot is unavailable. This is why several entries give no
  success rates or agent-count axes: [Yang-S2AN] Fig. 6, [Zhang-Mutex] Figs. 3–4,
  [MartinezBaselga-AVOCADO] Figs. 11–14, [Dergachev-ORCA-MAPF] Fig. 3.
- *Tables.* Some lost their row alignment: [Chakravarty-PIBT-FreeSpace] Tables 1–3, [Ma-DCC] Table
  II, [Shah-AROW] Table VIII, [Sudkhot-BDI-RVO] Table 3, [Pruekprasert-RightOfWay] Table I
  (two of three columns), [Dergachev-ORCA-MAPF] Table I. I quoted only cells whose meaning was
  unambiguous.
- *Two-column layouts* interleave left and right columns line by line. Readable, but a quotation
  that spans a column break is flagged where I rely on one ([Shah-AROW], the 15.5% figure).

**Opening the PDFs themselves would recover all of this.** It is the single cheapest way to
improve the review.

---

## §3. The issue's seeds — outcome for each

| Seed | Outcome | Published version | Entry |
|---|---|---|---|
| Okumura et al., PIBT, IJCAI 2019 | Opened. Journal version located as the issue asked: *Artificial Intelligence* 310, 103752 (2022), via the arXiv record's DOI. Read as arXiv v5 | Yes — journal version preferred | [Okumura-PIBT] |
| "Where Paths Collide" MAPF survey | Opened. **The cached copy is v2 (31 Jul 2025); the issue linked v1.** Read selectively. References mined: it supplied the description of request–response communication that led to [Ma-DCC] | None found — `[preprint]` | [Wang-MAPFSurvey] |
| Free-space PIBT post-processing pipeline | Opened; the published MDPI version was read, and the arXiv preprint cached alongside | Yes — *Mathematics* 14(7), 1195 (2026) | [Chakravarty-PIBT-FreeSpace] |
| Loosely Synchronized Rule-Based Planning | Opened | Yes — AAAI 2025 | [Zhou-LSRP] |
| Attention-based Priority Learning | Opened | Yes — AAMAS 2024 | [Yang-S2AN] |
| MAPF with mutex propagation (*Artificial Intelligence*) | **Year check done: 2022, inside the window.** Journal version paywalled; the open ICAPS 2020 version (also in-window) was read instead | Journal version not obtained (M4) | [Zhang-Mutex] + stub |
| Fast Simulation of Crowd Collision Avoidance | Opened | Yes — CGI 2019, Springer LNCS | [Charlton-FastCrowd] |
| Crowd Simulation with Arrival Time Constraints | Opened (publisher PDF; the HTML page refused the download tool) | Yes — *Symmetry* 12(11), 1804 | [Sung-ArrivalTime] |
| Collision Avoidance and Path Planning in Crowd Simulation | Opened. Venue recorded as a smaller letters journal, as asked; included because it has pseudocode | Yes — *ICIC Express Letters* 17(1) | [Sudkhot-BDI-RVO] |
| AVOCADO | Opened. Category checked as asked: **A, not a boundary case** | Yes — IEEE T-RO (DOI from the paper; volume and pages not identified) | [MartinezBaselga-AVOCADO] |
| "A survey on velocity obstacle paradigm" `[secondhand]` | **Confirmed to exist** — title, three authors, journal, volume 174, article 104645, April 2024, from Crossref. **Not obtained** (paywall; Unpaywall reports no open copy) | — | stub (M1) |
| CrowdVLA | Opened and scope-checked. **Excluded**: a learned vision–language–action policy, not a conflict rule | `[preprint]` | none — see [S1](s1-crowd-simulation.md), "Seed excluded" |

All twelve seeds are accounted for: ten have entries, one is a confirmed-but-unobtained stub, one
is excluded with a reason.

---

## §4. How each non-seed source was found

The issue's rule is that every entry be "confirmed from the paper's own page". All seventeen
non-seed sources were. How I came to look for each is recorded here, because it is not always
"by search" and I do not want to imply it was.

| Source | How it was found | Confirmed via |
|---|---|---|
| [Ma-TokenPassing] | It is the baseline in [Okumura-PIBT] §5.2 | arXiv API by title; AAMAS notice on the paper |
| [Ma-DCC] | It is the survey's example of request–response communication ([Wang-MAPFSurvey] §6.5, Table 9) | arXiv API by title; Crossref |
| [Tordeux-CFSM] | It is the baseline "CSM" in [Xu-AVM] §3 | arXiv API by title; Crossref |
| [Grover-Deadlock] | **Prior knowledge** — I knew of the paper; not reached from a seed | arXiv API by title; Crossref |
| [Xu-AVM] | **Prior knowledge** | arXiv API by title; Crossref |
| [ShalevShwartz-RSS] | **Prior knowledge** | arXiv API by title |
| [Malikopoulos-SignalFree] | **Prior knowledge** | arXiv API by title; Crossref |
| [Xu-TreeSearch] | **Prior knowledge** | arXiv API by title; Crossref |
| [Shah-AROW] | Web search (query 3 in §5) | arXiv; Crossref |
| [Ahmed-MergeAssist] | Web search (query 3) | arXiv |
| [Mariani-CoordSurvey] | Web search (query 3) | arXiv record's journal reference |
| [SunshineHill-RVO-ORCA] | **Prior knowledge** of the chapter; located with query 2 | publisher's free PDF; Crossref |
| [Martel-ACSyndicate], [Jenner-DriverSF] | The table of contents of *Game AI Pro 3* on gameaipro.com, after query 2 | publisher's free PDFs; Crossref |
| [Epic-UnrealAvoidance] | **Prior knowledge** that the engine documents its avoidance system | the page itself |
| [Dergachev-ORCA-MAPF] | Web search (query 5) — **late** | arXiv; Crossref |
| [Pruekprasert-RightOfWay] | Web search (query 7) — **late** | arXiv; Crossref |

**Seven sources came from prior knowledge rather than from a traceable search** — four
peer-reviewed, one preprint and two industry. That is a selection effect: they are papers I happened to know, which favours
well-known work. It does not affect whether what is written about them is accurate — each was read
at source — but it does affect how representative the sample is.

---

## §5. Searches actually run

**Web searches (seven in total):**

1. `"A survey on velocity obstacle paradigm" Robotics and Autonomous Systems 2024 104645` — to
   confirm the `[secondhand]` seed.
2. `Game AI Pro 3 chapter "RVO and ORCA: How They Really Work" pdf gameaipro.com` — S2.
3. `cooperative merging negotiation protocol connected vehicles V2V message exchange right-of-way
   arXiv` — S4, for category B.
4. `AIIDE OR "Motion, Interaction and Games" OR "IEEE Transactions on Games" crowd navigation
   local collision avoidance game characters paper 2018..2024` — S2, peer-reviewed. *Late.*
5. `navmesh local avoidance game engine agents deadlock doorway peer-reviewed paper` — S2. *Late.*
6. `pedestrian cellular automaton floor field conflict resolution rule friction two pedestrians
   same cell 2018 2020 paper` — S1, category C. *Late.*
7. `intersection priority rule autonomous vehicles conflict resolution right-of-way rule-based
   unsignalized 2020 paper` — S4, category C. *Late.*

Queries 4–7 were run **after** the sub-area files and first drafts of the synthesis files were
written, to test claims I was about to make. See §6, item 1.

**The issue's eight suggested queries — which were run:**

| Suggested query | Run? |
|---|---|
| `multi-agent path finding rule-based deadlock resolution` | Not as written. Covered by the seeds and by query 5 |
| `crowd simulation collision avoidance survey` | **No.** The two surveys I know of were both unobtainable (M1, M2) |
| `game AI crowd navigation agents` | In substance, as query 4 |
| `navmesh local avoidance game engine` | In substance, as query 5 |
| `intersection priority rule autonomous vehicles conflict` | In substance, as query 7 |
| `cooperative merging negotiation protocol vehicles` | In substance, as query 3 |
| `pedestrian lane formation rule simulation` | **No.** [Xu-AVM] covers lane formation but was found from prior knowledge |
| `bottleneck counterflow crowd model rule` | **No** |

**Databases not searched at all:** Google Scholar, Scopus, Web of Science, IEEE Xplore, the ACM
Digital Library, DBLP. No forward- or backward-citation chaining was done beyond the cases listed
in §4. This is a thin search and the review should be described as seed-led.

**Leads identified and not read** (titles and identifiers as they appeared in search results; none
confirmed beyond that, none summarised):

- "Deadlock-free, Safe, and Decentralized Multi-Robot Navigation in Social Mini-Games via
  Discrete-Time Control Barrier Functions" (arXiv:2308.10966) — doorway, hallway and corridor
  intersection scenarios on physical robots. **Probably the most relevant unread lead.**
- "Development of a conflict-free unsignalized intersection organization method for multiple
  connected and autonomous vehicles" (*PLOS ONE*, open access) — a right-of-way judgement model.
- "Unsignalized Intersection Management Strategy for Mixed Autonomy Traffic Streams"
  (arXiv:2204.03499) — heuristic priority queues.
- "Driving Conflict Resolution of Autonomous Vehicles at Unsignalized Intersections: A Differential
  Game Approach" (arXiv:2201.01424).
- "Deep Integration of Physical Humanoid Control and Crowd Navigation" (ACM MIG 2020) — the one
  peer-reviewed games-venue result from query 4; it appears to be a learned controller.
- "Collision Avoidance for Preplanned Locomotion" (*Game AI Pro*, chapter 22) — pre-window (2013).
- Kirchner, Nishinari and Schadschneider (2003), "Friction effects and clogging in a cellular
  automaton model for pedestrian dynamics", *Physical Review E* 67(5) — pre-window; record
  confirmed in Crossref. A category C rule for pedestrians, by the look of the search result. Not
  read.

**Cached but not summarised:** "Improving LaCAM for Scalable Eventually Optimal Multi-Agent
Pathfinding" (Okumura, arXiv:2305.03632; `refs/sr_lacam2_2305_03632.txt`). Downloaded as a
candidate and not read, to keep the S3 list bounded. [Zhou-LSRP] §6 says the swap operation it
borrows is "similar to the concept of the swap operation in PIBT (Okumura 2023)", i.e. this paper.
A reasonable next read.

---

## §6. Mistakes, corrections and things that should lower your confidence

**1. Two conclusions in the first draft were wrong, and only a late search caught them.** The
first drafts of `category-summary.md` and `research-gap.md` said that no traffic entry was
primarily a rule-based arbitration, and that no source arbitrated between continuous-space agents.
I then ran queries 4–7 to test those claims before committing them. Queries 5 and 7 each returned
a counter-example on the first page of results — [Dergachev-ORCA-MAPF] and
[Pruekprasert-RightOfWay]. Both were read, added, and the synthesis files rewritten. **The lesson
for a reader is that the "none found" statements that remain are only as strong as seven web
searches.** The lesson for the workflow is that the test searches should have come before the
synthesis, not after.

**2. A misattributed citation, caught before commit.** I drafted a line in `missing-papers.md`
saying [Grover-Deadlock] cites the buffered-Voronoi-cells paper (M5). On checking Grover's
reference list, the "Zhou et al. 2017" it cites is by different authors. The line was removed and
M5 now carries no description at all.

**3. Provenance claims corrected.** I first wrote that three papers were "found by search" with a
query named. They were not; I knew of them. The entries now say so (§4).

**4. A subtitle I could not verify.** I first gave the unobtained paper M3 a subtitle from memory.
Crossref gives only "Implicit crowds"; the files now use that.

**5. A softened comparison.** I first wrote that PIBT beats Token Passing "on both runtime and
quality". The paper says faster, and "comparable to or better" in quality (§5.2.2). Corrected in
[S3](s3-mapf-robotics.md) and [research-gap.md](research-gap.md).

**6. Internal inconsistencies found *in the sources*.** Recorded in the entries, not resolved:
- [Charlton-FastCrowd]: abstract says 100,000 people at 60 fps; results say up to 5 × 10⁵ at about
  30 fps.
- [Sudkhot-BDI-RVO]: 40,000 agents (abstract, conclusion), "ten thousands" (§5.3), 720,000 (§5.4).
- [Chakravarty-PIBT-FreeSpace]: abstract says "over 500 agents"; the largest tabulated count is
  200.
- [Ma-TokenPassing]: text says runtime "smaller than 500 milliseconds for 200 agents"; its own
  table gives 538.22 ms.
- [MartinezBaselga-AVOCADO]: the noise schedule is described two contradictory ways within §IV-D.
- [Dergachev-ORCA-MAPF]: the procedure is said to be deterministic so that all agents agree, and
  priorities are said to be assigned randomly; how the two are reconciled is not stated.

**7. A dating error in a seed.** [Wang-MAPFSurvey] §3.4.4 says PIBT was "Originally proposed by
Okumura et al. (2022a)". It was first published at IJCAI 2019. Flagged in the entry.

---

## §7. Open questions and risks (canonical list)

**R1. The sample is small, seed-led and not systematic.** 27 sources; seven web searches; no
bibliographic database; seven sources from prior knowledge (§4, §5). Every count in
`category-summary.md` and `research-gap.md` describes this sample. *None should be quoted in the
report as a property of the field.*

**R2. The conclusions have already moved once under new evidence** (§6, item 1). They should be
expected to move again.

**R3. S2 has no peer-reviewed entry.** Four industry sources, none with a measurement. One
late query found one games-venue paper, which looks like a learned controller and was not read.
The acceptance criterion "all four sub-areas covered" is met only in the weak sense that S2 has
entries and this log explains why none is peer-reviewed.

**R4. Five papers are missing, and two matter.** The velocity-obstacle survey (M1) and the
crowd-simulation survey (M2) are the sources most likely to contradict the S1 findings. M2 should
open in an ordinary browser.

**R5. One classification choice drives the S3 column.** Treating a planner-level contest for a
vertex as a conflict state makes the PIBT family C rather than A
([category-summary.md](category-summary.md) §4, case 1). **Needs supervisor sign-off.**

**R6. The A/B boundary does not say how to treat a simulator, or conventional signals.** Three
hard cases turn on it ([category-summary.md](category-summary.md) §4, cases 5–7). I have proposed
splitting B into "information shared, then a rule decides" and "the agents bargain". **That is a
proposed design decision, not something the issue authorised.**

**R7. One window call is borderline.** [Tordeux-CFSM] was published in 2016 but posted to arXiv in
December 2015. I counted it in. If the window is judged on first appearance it must move to the
pointer list, and S1 falls to five entries.

**R8. Nine entries were read selectively** (§2). For those, "not stated in paper" means "not stated
in the sections read". The most consequential case: [Grover-Deadlock]'s direction of rotation —
the actual tie-break — is recorded as not stated, and may be in the appendix or the earlier paper
it defers to.

**R9. Fifteen entries were read as arXiv copies of published papers.** [Okumura-PIBT],
[Zhou-LSRP], [Ma-TokenPassing], [Ma-DCC], [Grover-Deadlock], [Dergachev-ORCA-MAPF],
[Charlton-FastCrowd], [MartinezBaselga-AVOCADO], [Tordeux-CFSM], [Xu-AVM],
[Malikopoulos-SignalFree], [Xu-TreeSearch], [Shah-AROW], [Pruekprasert-RightOfWay],
[Mariani-CoordSurvey]. Section, equation and table numbers, and in two cases the numbers themselves ([Xu-TreeSearch] Table I, [Xu-AVM]), are
the arXiv copy's. **Re-check against the publisher's version before the report quotes a locator or
a figure.**

**R10. Whole areas were not searched.** In-window cellular-automaton pedestrian models (where
category C rules for pedestrians would be expected); data-driven and example-based crowd models;
human-like driver models for intersections; the peer-reviewed games literature beyond one query.
[research-gap.md](research-gap.md) §1 and §4 name what each could overturn.

**R11. Numbers shown only in figures are missing** (§2). Several "does it work" bullets are
qualitative for this reason and not because the paper is.

**R12. Industry claims cannot be checked.** "Thousands of vehicles" at 60 FPS
([Jenner-DriverSF]), "frequent deadlocks" at corners ([SunshineHill-RVO-ORCA]), are practitioners'
statements with no data behind them in the source.

**R13. Relevance statements are not grounded in CrowdGym.** I did not read the CrowdGym mapping
(§1). Whether any of these rules fits `RL_take_action` or the journey model is untested.

**R14. Three results cut against the FYP's working assumptions and should be put to the
supervisor rather than left in a file:**
- a survey's judgement that communication-free ("emergent") approaches are unsuitable where
  individual-level guarantees are needed ([Mariani-CoordSurvey] §3.8);
- measured evidence that the intuitive arrival-order rule performs badly under load
  ([Xu-TreeSearch] Table I);
- evidence that replacing a hand-written priority with a learned one costs speed, scale and
  interpretability ([Yang-S2AN]).

---

## §8. Acceptance criteria — checked one by one

| Criterion | Status |
|---|---|
| Every summarised paper is 2016 or later; no pre-window paper has a template entry | **Met, with one flagged borderline** — [Tordeux-CFSM] (R7). All others are 2017–2026 |
| `pre-window-foundations.md` exists and lists older methods as pointers only | **Met.** 14 pointers; one-line rules are taken from in-window sources and say so |
| Every entry independently verified from the paper's own page | **Met.** Each was opened; first page checked against the title; venue confirmed in Crossref or on the paper |
| Peer-review status recorded for every entry; industry sources separated and labelled | **Met.** S2 has a separate, labelled industry section and an empty peer-reviewed section |
| Every claim and number carries a locator | **Met as far as I can check.** Locators are section / table / figure / algorithm numbers of the cached copy. Where a number could not be recovered, the entry says so instead |
| Every entry has a primary category with a justification citing a locator | **Met.** Two surveys are `uncategorised` with an explanation |
| Every entry records trigger, information required and tie-breaking, or marks them `[not stated in paper]` | **Met.** Surveys carry `n/a` |
| Unobtainable papers have a `[NOT OBTAINED]` stub with no summary content, and appear in `missing-papers.md` | **Met.** 5 papers + 1 industry documentation source. The "why it matters" column in `missing-papers.md` uses only what *other, read* sources say, or says nothing |
| All four sub-areas covered, or the search log explains why not | **Met in the weak sense** for S2 (R3) |
| `rule-catalogue-simulation.md` exists with every row sourced and no merged rules | **Met.** 35 rows; ten look-alike groups listed and left unmerged |
| `category-summary.md` reports counts per category and notes any imbalance | **Met** |
| `research-gap.md` cites specific entries for every claim | **Met as far as I can check**; `[inference]` marks the rest |
| No rule is described as scaling or working beyond what its paper claims | **Met as far as I can check.** "Max agents tested" is the paper's own largest reported count; four cases where the paper's own numbers conflict are flagged, not resolved |
| No claim anywhere lacks a source | **Met as far as I can check.** Statements of mine are marked `[inference]`. Two unsourced remarks *in sources* are flagged as such: "move right if in conflict" ([Wang-MAPFSurvey] §6.5) and the remark on African and Asian intersections ([Mariani-CoordSurvey] §3.2.4) |

"As far as I can check" is deliberate: these were verified by re-reading and by the scripted
checks recorded in `WORK_LOG-22.md`, not by a second reader.
