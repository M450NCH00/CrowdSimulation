# Search log: issue #37

> For issue [#37](https://github.com/M450NCH00/CrowdSimulation/issues/37), PT-3 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). All work done on 2026-10-18 in one
> session. Records what was read first, how sources were confirmed and fetched, every search and its
> outcome, and what went wrong.

Companion files: [verdict](verdict.md) · [reference behaviours](reference-behaviours.md) ·
[queue cutting](queue-cutting.md) · [boarding and alighting](boarding-alighting.md) ·
[lifts and escalators](lifts-escalators.md) · [Singapore](singapore.md) ·
[missing papers](missing-papers.md) · [BibTeX](refs-unseen-evidence.bib)

---

## §1. What was read first

As the issue asks, and only these: issue #34, "The idea"; the scenarios `bus_queue_boarding`,
`mrt_door_alight_board`, `lift_boarding_capacity`, `escalator_entry_merge` and
`merge_two_corridors` in `dataset/scenarios.yaml` (with their `decision_factors`); and
`literature/demographic-personas/human-demographic-effects.md`, skimmed (its warning section,
"Identified but not obtained", "Cross-cutting observations"). For conventions only (no content
used), the format of #36's `missing-papers.md` and `search-log.md` and its work log's assumptions.

## §2. How sources were confirmed and fetched

- **Confirmation**: every DOI was checked on the Crossref API (`api.crossref.org/works/<doi>`);
  titles without a known DOI were searched on Crossref or OpenAlex.
- **Open copies**: looked up on OpenAlex (`api.openalex.org`, `open_access` and `locations`).
  **Unpaywall was not used**: it refuses placeholder emails, and sending the user's address to it
  was flagged as an open question in an earlier work log, so I did not.
- **Rendering**: tables that are images in a PDF (Brintzenhofe Tables 3.2 and 3.3) were rendered
  with PyMuPDF in a throwaway `uv run --with pymupdf` environment, then read as images.
- **Caching**: `refs/he_*`. Openly licensed copies are committed; the rest are on disk only and
  listed in `.gitignore` with their download links.

## §3. Searches, in order

### Q1. Queue cutting
| # | Where | Query | Outcome |
|---|---|---|---|
| 1 | Web | Milgram Liberty Toledo Wackenhut "Response to intrusion into waiting lines" ... 1986 51(4) 683 | Brintzenhofe 2023 chapter found; secondary summaries (not used) |
| 2 | Web | Mann 1969 "Queue culture: the waiting line as a social system" ... pdf | Publisher page only (paywalled) |
| 3 | Web | Schmitt Dubé Leclerc 1992 "Intrusions into waiting lines ..." | Not found by web search; **confirmed on Crossref** |
| 4 | Web | Brintzenhofe "Revisiting Milgram's 1978" ... open access chapter | T&F page; CC BY-NC-ND per Crossref |
| 5 | Crossref | the five seed DOIs plus a title search for Schmitt et al. | All confirmed; Schmitt et al. is JPSP 63(5):806-815 |
| 6 | OpenAlex | open-access status of the seven Q1 DOIs | Only Brintzenhofe open |
| 7 | Web | "Investigating Human Interaction through Mathematical Analysis" Brintzenhofe pdf oapen | OAPEN records; OAPEN returned HTTP 403 and its REST API "not allowed"; **the T&F open-access API delivered the chapter** |
| 8 | Web | "Response to intrusion into waiting lines" Milgram pdf | No open copy; secondary accounts only |
| 9 | Web | Langer Blank Chanowitz 1978 "mindlessness of ostensibly thoughtful action" pdf | A third-party copy (communicationcache.com); same site also had **Folkes 1985** |
| 10 | Web (extended) | queue jumping field experiment replication reaction intruder line cutting 2015..2025 | Furnham et al. 2020 review (used only for leads); Oberholzer-Gee lead |
| 11 | Web | Mann "queue culture" 1969 Melbourne football queue pdf full text | Nothing usable |
| 12 | OpenAlex | Helweg-Larsen 2008, Dold & Khadjavi 2017, Zhou & Soman 2003 | All closed |
| 13 | Web | Dold Khadjavi "Jumping the queue" ... working paper pdf | Published version only |
| 14 | Web | Helweg-Larsen LoMonaco 2008 "Queuing among U2 fans" pdf | Not found |
| 15 | Web | Oberholzer-Gee 2006 "A market for time" ... pdf | Not found by web search; OpenAlex found the 2003 EconStor working paper; **EconStor served a bot check** |

### Q2. Boarding and alighting
| # | Where | Query | Outcome |
|---|---|---|---|
| 16 | Web (extended) | field observation metro platform boarding alighting passengers "let off first" door video study | Hong Kong (TR-A 2020), Beijing, Cairo, London leads |
| 17 | Web (extended) | controlled experiment boarding alighting train door mock-up platform markings passenger flow laboratory | PAMELA and Santiago lab studies |
| 18 | WebFetch | the two World Transit Research seed pages and the CityU thesis page | Seed citations confirmed; thesis full-text link found |
| 19 | OpenAlex | "Seriani boarding alighting"; "Seriani Fernandez platform"; "alighting boarding metro field observation video" | ~30 records; open copies for UCL manuscripts, Springer, Collective Dynamics |
| 20 | Downloads | CityU thesis; Hindawi; HAL; ScienceDirect OA; MDPI | **All refused automated access** (copyright form; HTTP 403; Anubis bot check) |
| 21 | Downloads | UCL Discovery (3 manuscripts); Springer (Harris 2022); Collective Dynamics (2) | Succeeded |
| 22 | arXiv API | Baali et al.; Moussaïd + boarding | No arXiv version |
| 23 | Semantic Scholar API | open-PDF pointers for four DOIs | Rate-limited (HTTP 429) for two; one closed, one pointing to the blocked ScienceDirect copy |
| 24 | Web (extended) | bus stop queuing behaviour field observation passengers form queue or crowd boarding order study | No study of boarding order; modelling and qualitative work only |
| 25 | WebFetch | Lindner et al. 2025 (SUMO) via tib-op.org | Read; **no field data** |

### Q4. Singapore
Ten searches, S1-S10, are listed with outcomes in [`singapore.md`](singapore.md) §4.

### Q3. Lifts and escalators
| # | Where | Query | Outcome |
|---|---|---|---|
| 26 | Web | Holborn escalator trial standing both sides Transport for London report results capacity walking pdf | **TfL FOI report** (read); press on the 2016 trial (not used) |
| 27 | Web | field observation escalator standing walking proportion passengers study peak hour metro walk lane percentage | Davis & Dutta 2002, Santiago, Delhi leads (not followed) |
| 28 | Web | elevator lift boarding behaviour field observation passengers crowded lift who enters last wheelchair priority study | **Taipei MRT lift study** (read on the journal's e-book site, pages 26-48) |

## §4. What went wrong, and judgement calls

- **Bot protection is the main obstacle.** Seven open-access hosts refused automated downloads
  (Hindawi/Wiley, MDPI, ScienceDirect OA, HAL, EconStor, USF Digital Commons, Universidad de
  Chile). Their papers are stubbed as "browser", not "library", in `missing-papers.md`.
- **A copyright click-through** (CityU theses) was not accepted on the user's behalf.
- **Reproduced tables (A6)**: Milgram's and Schmitt's numbers come from tables reproduced with APA
  permission in an open chapter; used with the `repro` flag. A supervisor decision.
- **An overclaim corrected on re-reading**: the first draft of `queue-cutting.md` said silent
  bystanders suppress objection; Table 3.2 does not show it. Rewritten before commit.
- **An internal contradiction in a source**: Seriani et al. 2019's manuscript abstract ("boarding is
  first") contradicts its §4.2 ("alighting occurs first"); the body is followed and the conflict
  flagged.
- **The Taipei article** is in Chinese, and its e-book text layer interleaves the two columns. All
  numbers used were checked against Table 4, which extracted cleanly.
- **Untrusted content**: no fetched page contained instructions to act on.
