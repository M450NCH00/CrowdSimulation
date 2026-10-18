# Search log: issue #36

> For issue [#36](https://github.com/M450NCH00/CrowdSimulation/issues/36), PT-2 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). All work was done on 2026-10-18 in
> one session. This file records what was read first, how sources were found and read, every search
> and its outcome, what went wrong, and the leads not followed.

Companion files: [verdict](verdict.md) · [methods](methods.md) ·
[scenario standards](scenario-standards.md) · [test protocol draft](test-protocol-draft.md) ·
[missing papers](missing-papers.md) · [refs](refs-unseen-scenarios.bib)

---

## §1. What was read first

As the issue asks, and only these:

- issue #34, "The idea";
- `literature/game-theory/g6-transfer-across-games.md`, §3 and "What this means for the FYP" (§2
  was read as well, because the issue cross-references Cross et al. 2025 there);
- `literature/game-theory/g5-llm-agents-game-theory.md` §4;
- `literature/paper-summaries/02-sense-think-act-reflect.md`, sections 2 and 6;
- the scenario ids and descriptions in `dataset/scenarios.yaml`.

Further reads, each for a stated reason (work log A4):

1. **The cached Zhang et al. text** (`refs/zhang2026_dfd.txt`), searched for the out-of-domain
   passage only, because the summary does not say how that dataset was built.
2. **The table of rule fields in `llm_negotiation/docs/rule-format.md`**, for the names of today's
   encounter classes, used in the protocol's first fold.
3. **The format** of #35's work log, `missing-papers.md`, `search-log.md` and `.bib`, to follow the
   same conventions. No content from them is used.

## §2. How sources were found and read

- **Order.** The issue's priority order: (1) scenario standards, (2) generalisation methods, (3) the
  spillover leads, (4) leakage.
- **Confirmation.** Every entry was confirmed from its own first page or catalogue page, and from
  Crossref, the arXiv API or the PMLR page for venue, volume, pages and DOI.
- **Caching.** Every source read is cached under `refs/us_*` as a text extract (`pdftotext -enc
  UTF-8`, `-layout` for the two-column RiMEA and the IMO circulars; HTML pages stripped of tags by a
  short script). Copies with no open licence are kept on disk only and listed in `.gitignore` with a
  re-download link (work log A3).
- **Reading.** Cached text was searched with `grep` and read in the relevant sections. Each entry
  states what was read. Standards were read in their relevant sections only, as the issue allows.

## §3. Searches and outcomes

| # | Query or action | Outcome |
|---|---|---|
| S1 | Fetch `ped.fandom.com/wiki/Test_Cases` (seed) | **HTTP 410: the wiki is closed.** Went to the primary documents |
| S2 | RiMEA guideline PDF (web search, then the rimea.de page) | rimea.de rate-limited curl (HTTP 429); the page, read another way, links v4.1.1 (German/English), v4.1.0, v4.0.1. **v4.1.1 downloaded** |
| S3 | "MSC.1/Circ.1238 ... Annex 3 test cases pdf" | Found Circ.1238 and **Circ.1533, which supersedes it** (para. 11). Both downloaded |
| S4 | OpenSCENARIO storyboard (seed URL `latest/`) | **HTTP 404**; v1.4.0 pages found by search; versions listed: 1.3.0, 1.3.1, 1.4.0 |
| S5 | JASSS ODD (seed URL) | Downloaded |
| S6 | JuPedSim routing (seed URL) | Downloaded; docs version 1.4.2 |
| S7 | ISO 20414 page (seed URL), then "ISO 20414 ... open access paper Ronchi" | Public page cached; **no open copy or open paper on the standard found**. NIST TN 1822 used as the open precursor |
| S8 | NIST TN 1822 (`[unverified lead]`) | **Confirmed** and downloaded from nvlpubs.nist.gov |
| S9 | SteerBench (`[unverified lead]`) | **Confirmed** (Crossref, doi:10.1002/cav.277); publisher PDF on a Utrecht course site |
| S10 | Melting Pot 1.0 and 2.0 (arXiv) | Downloaded; ICML 2021 version confirmed on PMLR; for 2.0, **no published version** (arXiv has no journal reference; a web search found nothing) |
| S11 | "pedestrian model calibrated on one scenario validated on another ..." (extended search) | Leads only. None directly quantified cross-scenario loss. Followed up with S12 and S13 |
| S12 | Tordeux et al., neural-network pedestrian prediction | arXiv:1801.09782 read; the 2020 journal version (JITS) is paywalled, **not read**; the Cologne repository link returned 404 |
| S13 | Wolinski et al. 2014 | HAL copies returned bot-check pages; **authors' copy** from gamma.cs.unc.edu read |
| S14 | "Coordination and transfer" (g6 lead 1) | Cooper & Van Huyck, *Exp. Econ.* 2018; **accepted manuscript** from UEA eprints read |
| S15 | Cason, Savikhin, Sheremeta (g6 lead 2) | **MPRA version** (Sept 2011) read |
| S16 | Mengel & Sciubba (g6 lead 3) | Essex repository unreachable (twice); AgEcon HTTP 403 (and 202 with empty body); Maastricht HTTP 403; TSE HTTP 404. **Stubbed** |
| S17 | Huck, Jehiel, Rutter (g6 lead 4) | HAL postprint blocked by bot protection; **2007 working paper** from UCL Discovery read |
| S18 | Grimm & Mengel (g6 lead 5) | **2009 working paper** (METEOR RM/09/007) read |
| S19 | Cooper & Kagel (g6 lead 6) | **Final submission** (Nov 2006) from the author's site read |
| S20 | Leakage methods (no seed beyond g5/g6): Wu et al. 2024, Aher et al. 2023, Binz & Schulz 2023, chosen from memory and then confirmed | All three on arXiv; venues confirmed on Crossref / PMLR |
| S21 | Crossref check of 14 DOIs and titles; arXiv API for journal references | All confirmed; see the `.bib` notes |

## §4. What went wrong, and was corrected

- **A destructive glob.** `rm refs/*.html`, meant for my own intermediate downloads, also deleted
  46 tracked `.html` caches from earlier issues. They were never committed as deleted, and were
  restored with `git checkout -- refs/` (work log, progress entry 3).
- **Two internal inconsistencies in sources**, recorded rather than resolved:
  - TN 1822 calls the elevator test "Verif.2.7" in its heading (p. 24) but "Verif.2.8" in §3.1.2's
    summary (p. 17);
  - the ODD paper numbers "Design concepts" as element 4 (§1, Fig. 1) and as element 5 (§5).
- **A seed lead pointed to a superseded document** (Circ.1238), and two seed URLs were dead (S1,
  S4).

## §5. Leads not followed (for a later session)

- **Cobbe et al. (2019), "Quantifying Generalization in Reinforcement Learning"** (ICML). Melting
  Pot 2.0 cites it as the physical-generalisation contrast (p. 4). It would inform how many
  training layouts an L2 test needs. Not opened.
- **Cooper & Kagel (2006)** on meaningful versus generic context in cross-game learning, cited in
  [CooperKagel-Signaling] §VII. It is the source of the context condition; not opened.
- **Cooper & Kagel (2003), "Lessons Learned: Generalizing Learning Across Games"** (*AER P&P*).
  Seen in a search result only.
- **Haruvy & Stahl, "Learning transference between dissimilar symmetric normal form games"**, cited
  by [CooperVanHuyck-Transfer] as the one study of dissimilar games. Not opened.
- **Peysakhovich & Rand (2016)**, cited in [CooperVanHuyck-Transfer] fn. 23 for cross-game transfer
  of a prosocial norm. Not opened.
- **The ODD guidance supplement and Supplement S7 (TRACE-based experiment template)** of
  [ODD-2020]. S7 may be a better model for the card's experiment section. Not opened.
- **The published versions** of the four spillover studies read as working papers or manuscripts,
  of Binz & Schulz (PNAS), and of Tordeux et al. (JITS 2020); see
  [missing-papers.md](missing-papers.md).
- **Selective prediction / abstention** literature, for L4. No search was run (open question U1 in
  the work log).
