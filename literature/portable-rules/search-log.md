# Search log: issue #35

> For issue [#35](https://github.com/M450NCH00/CrowdSimulation/issues/35), PT-1 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). All work was done on 2026-10-18.
> This file records what was read first, how sources were found and read, every search and its
> outcome, what was excluded, what went wrong, and the leads not followed.

Companion files: [verdict](verdict.md) · [feasibility](feasibility.md) ·
[representations](representations.md) · [novelty check](novelty-check.md) ·
[missing papers](missing-papers.md) · [refs](refs-portable-rules.bib)

---

## §1. What was read first

As the issue asks, and only these:

- issue #34, "Why this track exists" and "The idea";
- `literature/game-theory/g6-transfer-across-games.md`, "What this means for the FYP";
- `literature/simulation-rules/research-gap.md`, §3 and §5;
- `llm_negotiation/docs/rule-format.md`, §§1–7.

Three further reads, each for a stated reason (work log A3):

1. **#34's "Constraints for every issue in this track"**, because they bind this issue.
2. **Issue #20's risk R4 (`WORK_LOG-20.md`) and `g6-transfer-across-games.md` §3**, which the issue
   cites as the reason the novelty paper matters.
3. **One rule file, `llm_negotiation/rule_db/rules/single_file_first_arrival.v1.yaml`**, to check
   #34's worked example. Its role assignment reads `agent.time_to_segment_s`, which became flag F4
   in [feasibility.md](feasibility.md).

For the cross-references the issue lists (`g2-norm-emergence.md`;
`paper-summaries/02-sense-think-act-reflect.md`), only the lines cited were opened. GameChat's
cached text (`refs/mahadevan2025_gamechat.txt`) was term-searched, not read.

**Not read:** `integration/crowdgym_mapping.md` and `dataset/schema/README.md`. Nothing here
proposes a CrowdGym change, as in issue #22's search log §1.

## §2. Method

- **Identification.** Every identifier was looked up, never guessed: arXiv records through the
  arXiv API (journal reference, DOI, comment); DOIs and titles through Crossref; open-access status
  and copies through OpenAlex. JASSS articles of 2003–2008 carry no DOI on their pages and are
  cited by URL.
- **Download.** `curl`, one empty folder per source. **Every first page was checked against the
  expected title. No wrong paper was downloaded.**
- **Text.** `pdftotext -enc UTF-8` in reading order, or HTML stripped with a standard-library
  script for JASSS and the FMI specification. Page breaks survive as form feeds. The first pass
  used pdftotext's default Latin-1, which garbled names; all extracts were re-made as UTF-8 with
  identical line counts (commit `fa46612`).
- **Caching** (work log A2, A7): `refs/pr_*.txt` for every source read.
  - PDFs are committed where openly licensed or from arXiv. Three without an open licence are
    gitignored, with re-download links in `.gitignore`.
  - Chapter 1 of *Conflicting Agents*, read from the user's own copy, is cached on disk but not
    committed.
- **Reading.** "Read in full" means the whole body. Sections are listed in each entry where only
  part was read. All locators come from the cached text.

**Searches.** 30 web searches. "Standard" mode was the default; "extended" was used for three hard
questions (marked E). No paid API was called.

| # | Query (abridged) | For | What it found |
|---|---|---|---|
| 1 | "Linking sanctions to norms in practice" Mellema | Seed check | arXiv:2205.10295 (Mellema and Dignum) |
| 2 | Horiguchi … ALIFE 2024 proceedings | Q5: published version | Only the arXiv listing and reposts |
| 3 | Crawford Ostrom "A Grammar of Institutions" pdf, DLC | Seed | No repository copy; an unofficial JSTOR printout (not used); the 2005 book reprint |
| 4 | "Modelling Institutions Using Dynamic Deontics" pdf nADICO | Seed | Academia.edu record (403); nADICO PRIMA 2013 |
| 5 | Frantz thesis Otago nADICO | Seed alternative | OUR Archive handle 10523/5906 (portal blocked) |
| 6 E | Same pedestrian model in different simulators, results differ | Q2 | No direct study; a headed-SFM comparison; a validation review |
| 7 | Docking, same model in two toolkits, Axtell Epstein | Q2 | Axtell et al. 1996; Arifin et al. 2010 (WSC); Legendi et al. 2013 |
| 8 | Same robot controller in Gazebo, Webots, CoppeliaSim | Q2 | Simulator-level comparisons only (resources, physics fidelity) |
| 9 | HuNavSim, simulator-agnostic wrappers | Q2 | HuNavSim 2.0 (arXiv:2507.17317) and 1.0 |
| 10 | IDM implementation differences, SUMO, Aimsun, VISSIM | Q2/Q4 | No direct IDM comparison; a 2004 VTI comparison of car-following models |
| 11 | Vadere JuPedSim same model comparison | Q2 | No direct study; a UCLouvain thesis comparing models within Vadere; a RiMEA comparison (SNE) |
| 12 | Replication NetLogo Repast Mesa Edmonds Hales Wilensky Rand | Q2 | Donkin et al. 2017; Grimm et al. 2025 (ODD replication of 18 models); the HUMAT re-implementation guide |
| 13 | Sim-to-sim social navigation, ORCA against SFM | Q2 | SocNavBench; "Stranger Danger!"; "Following the Human Thread"; "Characterizing the Complexity ..." |
| 14 | Ontology of pedestrian interactions, OWL | Q3 | Boje's crowd-simulation-scenario ontology (CEUR); Bandini et al. 2008; Orellana and Renso; a road-user ontology |
| 15 | Taxonomy of pedestrian–pedestrian interactions | Q3 | No taxonomy; merging studies; pedestrian–vehicle conflict studies |
| 16 | SteerBench test cases | Q3 | Singh et al. 2009 (CAVW); a 2011 MIG follow-up |
| 17 | Conflict typology in MAS, Tessier, *Conflicting Agents* | Q3 | The book (held locally by the user) |
| 18 E | LLM-generated norms, machine-readable, reused by other systems | Q5 | CRSEC; arXiv:2509.02515 (survey); arXiv:2605.02335 (position paper) |
| 19 | LLMs for institutional grammar coding (ADICO) | Q5 | A 2024 Warsaw seminar; machine coding with NLP (Rice et al. 2021) |
| 20 | CRSEC, IJCAI 2024 | Q5 | Publication details |
| 21 | LLM translating traffic rules into temporal logic (TR2MTL) | Q5 | TR2MTL (IEEE IV 2024) |
| 22 | LLM norms, JaCaMo NPL, deontic specification generation | Q5 | Savarimuthu et al. 2024 (COINE) |
| 23 E | LLM agents negotiate rules, rules reused in simulation | Q5 | Only this repository's own public issues (#24, #26), and LLM crowd papers without rule extraction (arXiv:2508.15047, arXiv:2607.25140) |
| 24 | Blochwitz 2011 FMI pdf | Q1 | Linköping proceedings |
| 25 | FMI cross-check, tool interoperability problems | Q1/Q4 | Bertsch et al. 2017; an FMUtoolbox cross-check paper; a forum report (anecdotal, not used) |
| 26 | LCIM, Tolk, HLA | Q1 | Wang, Tolk, Wang 2009 (arXiv:0908.0191); Tolk and Muguira 2003; Mittal et al. (arXiv:2407.20696) |
| 27 | Gomes et al. co-simulation | Q1 | arXiv:1702.00686; the accepted version on Broman's page; Schweiger et al. 2019 |
| 28 | Axtell et al. "Aligning Simulation Models" | Q2 | Axelrod's page (preprint); Deep Blue |
| 29 | Same game AI in two engines; GDL reasoners disagree | Q2 | **No study**; developer anecdotes; single-engine papers |
| 30 | Crowd behaviour model ported to another simulator | Q2 | A MASON → NetLogo pedestrian-model reproduction (blog post only, not used); CrowdWalk; a quantitative comparison of crowd models (arXiv:1401.0366) |

## §3. What happened to each seed lead

| Seed | Outcome |
|---|---|
| Frantz and Siddiki 2021, IG 2.0 | **Read in full** (accepted manuscript) → [Frantz-IG2] |
| IG 2.0 codebook, arXiv:2008.08937 | **Read in sections** (v5) → [Frantz-IG2Codebook] |
| Frantz and Siddiki 2022, book | **Not obtained** → stub M3 |
| Crawford and Ostrom 1995 `[unverified lead]` | **Confirmed to exist** (APSR 89(3)); **not obtained** → stub M1 |
| "Modelling Institutions Using Dynamic Deontics" `[unverified lead]` | **Confirmed**: Frantz, Purvis, Nowostawski, Savarimuthu, COIN IX, LNCS, 2014; **not obtained** → stub M2 |
| Neumann 2008, JASSS 11(4) 6 | **Read in full** → [Neumann-HomoSocionicus] |
| JASSS 14(2) 6 ("confirm the title and authors") | **Confirmed**: Hollander and Wu (2011), "The Current State of Normative Agent-Based Systems"; **read in full** → [Hollander-NormativeABS] |
| "Linking sanctions to norms in practice" `[unverified lead]` | **Confirmed**: Mellema **and Dignum** (two authors), arXiv:2205.10295, 2022; **read in full** → [Mellema-Sanctions] |
| Gomes et al. 2018 `[unverified lead]` | **Confirmed**: *ACM Computing Surveys* 51(3), art. 49; **read in sections** (accepted version) → [Gomes-CoSim] |
| Curtis, Best, Manocha 2016, Menge | **Read in full** → [Curtis-Menge] |
| arXiv:2005.12712 ("confirm the authors and the published version") | **Confirmed**: Kleinmeier, Köster, Drury; *J. R. Soc. Interface* 17(171), 2020; **read in full** (arXiv v2) → [Kleinmeier-Cooperation] |
| Francis et al. 2023 `[unverified lead]` | **Confirmed and published**: *ACM THRI* 14(2), 2025; **read in sections** (arXiv v4) → [Francis-SocNavPrinciples] |
| arXiv:2409.00993 | **Read in full** → [Horiguchi-NormsLLM] in [novelty-check.md](novelty-check.md) |
| Shoham and Tennenholtz; Zhang et al. 2026 | Cross-reference only, as asked |

**Added, not seeds:**
- Q1 and Q4: [Blochwitz-FMI], [FMI-3.0.2], [Bertsch-ReferenceFMUs], [Wang-LCIM].
- Q2: [EscuderoJimenez-HuNavSim2], [Axtell-Docking], [Edmonds-Replication],
  [Wilensky-MakingModelsMatch], and [Galan-Reimplementing] (found through
  [Neumann-HomoSocionicus] Note 7).
- Q3: [Tessier-ConflictingAgents].
- Q5: [Ren-CRSEC], [Manas-TR2MTL], [Savarimuthu-NormativeLLM].
- Stubbed: [Donkin-Replicating].

**Totals:** 19 entries in `representations.md` (14 read in full, 5 in sections), 4 entries in
`novelty-check.md` (1 in full, 3 in sections), 4 stubs.
- **In full (15):** Frantz-IG2, Neumann, Hollander, Mellema, Blochwitz, Bertsch, Wang-LCIM, Menge,
  Kleinmeier, HuNavSim 2.0, Axtell, Edmonds, Wilensky, Galán, Horiguchi.
- **In sections (8):** the IG 2.0 codebook, the FMI 3.0.2 specification, Gomes, Francis, Tessier,
  CRSEC, TR2MTL, Savarimuthu.

That is 14 entries read in full plus the novelty paper, against the issue's aim of 8–12 plus the
novelty check. The extra entries came from Q2, which needed the docking studies.

## §4. Exclusions and scope discipline

- **Scenario standards** (for example ASAM OpenSCENARIO) are PT-2's (#36). Francis et al.'s
  scenario *cards* are used only for Q3's situation names.
- **Simulators as software** (JuPedSim, Vadere, Menge as tools) are PT-5's (#39). Entries describe
  only how behaviour is represented.
- **Human evidence** about queues, boarding and lifts is PT-3's (#37). **Trained models** are PT-4's
  (#38).
- **Rule-interchange standards outside simulation engineering** were *not searched*: W3C RIF,
  OASIS LegalRuleML, W3C ODRL. They are about rule portability between engines, and are listed as
  leads in §6. The issue asked for one standard "from simulation engineering", and FMI meets that.
- **Search snippets are never used as evidence.** Several snippets described results (Donkin et al.,
  the MASON → NetLogo reproduction, HuNavSim's wrappers before the paper was read). None is cited
  as a finding.

## §5. Mistakes caught, and judgement calls

1. **Encoding.** The first extracts were Latin-1 and garbled accented names. Re-made as UTF-8 before
   any locator was written.
2. **A count in an issue comment.** I first posted "21 entries"; it was 19 entries plus 4 stubs.
   The comment was corrected in place, saying so.
3. **A count in `README.md`.** I first wrote "5 papers unobtained"; it is 4, plus 2 read only as
   preprints. Corrected before commit.
4. **An overstatement about FMI.** I first wrote that 5 of 10 tools "failed one reference test".
   [Bertsch-ReferenceFMUs] says "five tools show errors in ME due to violations of the calling
   sequence" on the Integer and Boolean FMUs. Corrected in `feasibility.md`.
5. **Two figures decoded by me.**
   - Menge's Figure 4 labels came out with two strings interleaved character by character
     (`∆tO=RC0.A1 s` = "Δt ORCA = 0.1 s"). The decoding is unambiguous but mine; the entry says so.
   - Francis et al.'s Table III columns were jumbled; the scenario rows were reconstructed by
     order, and the entry flags this.
6. **Unofficial copy declined.** The only free copy of Crawford and Ostrom 1995 was a third-party
   JSTOR printout; it was not used.
7. **A `git add` with ignored paths** failed once; the commit was redone with the same files.
8. **Branch base.** Stacked on PR #33's branch, not `main` (work log A1).

## §6. Leads not followed (in priority order)

1. **Donkin et al. 2017** (M4): open access, blocked only for automated download.
2. **Arifin et al. 2010** (Winter Simulation Conference): four implementations of one model,
   docked; https://www.informs-sim.org/wsc10papers/052.pdf.
3. **W3C RIF, OASIS LegalRuleML, W3C ODRL**: standards for exchanging rules and norms between
   engines. The closest thing outside simulation to a "portable rule core". Not searched (§4).
4. **Vázquez-Salceda et al. (2008)**, *AI and Law* 16, "From human regulations to regulated software
   agents' behavior: connecting the abstract declarative norms with the concrete operational
   implementation" (cited in [Mellema-Sanctions]). Abstract-to-concrete norms is exactly core to
   binding.
5. **Grimm et al. (2025)**, *Ecological Modelling*: 18 models replicated with ODD and NetLogo.
6. **Pedestrian ontologies**: Orellana and Renso (interactions ontology); Bandini et al. 2008; Boje's
   crowd-simulation-scenario ontology (CEUR).
7. **SteerBench** (Singh et al. 2009, *CAVW* 20(5–6)): a test-case taxonomy for steering.
8. **Schweiger et al. 2019**, "An Empirical Survey on Co-simulation" (arXiv:1901.06262):
   practitioners' problems with FMI.
9. **Frantz's 2015 Otago thesis** (nADICO; dynamic deontics in agent-based models).
10. **NormSage** (Fung et al. 2023) and **arXiv:2509.02515** (classic MAS against LLM norms), for
    Q5.
11. **HuNavSim 1.0** (*RA-L* 2023) and **MengeROS** (Aroor et al. 2017).
12. **Same-scenario comparisons** (§4.4 of `feasibility.md`): a RiMEA comparison; SocNavBench; a 2020
    Gazebo/Webots/V-REP comparison (arXiv:2008.04627); the 2004 VTI car-following comparison.

## §7. Open questions and risks

The canonical list is in `WORK_LOG-35.md`, "Open questions / risks". In short:

- Q2's "none found" is bounded by these 30 searches.
- Two figures were reconstructed.
- Eight entries were read in sections only.
- The docking evidence comes from social simulation, and carrying it over to crowd simulators is an
  inference.
- The recommended representation is a design proposal needing sign-off.
- `refs/` now holds text extracts of copyrighted works in a public repository, as earlier issues
  did. Whether to keep doing so is the user's call.
