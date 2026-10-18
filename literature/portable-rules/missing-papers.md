# Missing papers: one consolidated list

> For issue [#35](https://github.com/M450NCH00/CrowdSimulation/issues/35). These sources were
> confirmed to exist, but their full text could not be opened on 2026-10-18.
>
> - **None is summarised anywhere in this review**: no abstract-based summary, no partly filled
>   template.
> - Each has a six-line stub, with "Status: awaiting PDF from user", in
>   [representations.md](representations.md), in the group it would belong to.
> - If you can supply the PDFs, a follow-up can add the entries. A university library subscription
>   would probably cover M1–M3 `[unverified]`.

**Count: 4 sources not obtained** (3 peer-reviewed, 1 book). In addition, **2 published versions
were not obtained** and an earlier version was read in their place. **1 standard was not
attempted.**

## Not obtained (stubbed; no summary anywhere)

| # | Source | Venue | Why it could not be opened | Link to try | Would go in | Why it matters |
|---|---|---|---|---|---|---|
| M1 | Crawford, Ostrom (1995). **A Grammar of Institutions.** | *American Political Science Review* 89(3), 582–600 | Paywalled. OpenAlex reports no open copy. The only free copy found is a JSTOR printout on a third-party site, which I did not use | https://doi.org/10.2307/2082975 | Group 1 | **Highest priority.** The original ADICO, named in #34's idea as the structure to borrow. It is cited here only as [Frantz-IG2] §2 quotes it. The 2005 reprint (chapter 5 of Ostrom, *Understanding Institutional Diversity*) is an alternative |
| M2 | Frantz, Purvis, Nowostawski, Savarimuthu (2014). **Modelling Institutions Using Dynamic Deontics.** | *Coordination, Organizations, Institutions, and Norms in Agent Systems IX* (COIN 2013), LNCS, Springer, pp. 211–233 | Springer paywall; Academia.edu returned HTTP 403; OpenAlex reports no open copy | https://doi.org/10.1007/978-3-319-07314-9_12 | Group 1 | Medium. The issue's `[unverified lead]` for nested ADICO "applied to an agent-based simulation". It is **confirmed to exist**, and its authors and venue are now known. Its nesting idea is covered through IG 2.0, which credits it ([Frantz-IG2] §3.1). Frantz's 2015 Otago PhD thesis is open access and covers the same work (https://hdl.handle.net/10523/5906), but the repository's JavaScript portal blocked automated download |
| M3 | Frantz, Siddiki (2022). **Institutional Grammar: Foundations and Applications for Institutional Analysis.** | Palgrave Macmillan (Springer), doi:10.1007/978-3-030-86372-2 | Paywalled book; OpenAlex reports no open copy | https://link.springer.com/book/9783030863715 | Group 1 | Low to medium. The codebook and the 2021 paper were read and cover IG 2.0's structure. Chapter 4, "Institutional Grammar 2.0: Conceptual Foundations and General Syntax" (pp. 75–140), would be the section to read |
| M4 | Donkin, Dennis, Ustalakov, Warren, Clare (2017). **Replicating complex agent based models, a formidable task.** | *Environmental Modelling & Software* 92, 142–151 | **Open access (CC BY 4.0)**, but ScienceDirect and the Aberystwyth repository both refused automated download (HTTP 403) | https://doi.org/10.1016/j.envsoft.2017.01.020 (should open in an ordinary browser) | Group 6 | **High, and probably the easiest to get.** A search snippet described one model replicated in NetLogo and Repast with results differing in trend, not only magnitude. That snippet is **not** used as evidence anywhere. If confirmed, it would be a fifth docking study for Q2, and the only one comparing two modern toolkits |

## Published versions not obtained (an earlier version was read)

| # | Source | Version read instead | Why | What could differ |
|---|---|---|---|---|
| V1 | Francis et al. (2025), *ACM THRI* 14(2), doi:10.1145/3700599 (CC BY) | arXiv:2306.16740**v4** (September 2023) | ACM returned HTTP 403; the Aston repository was unreachable | The published version is 65 pages against 42. Table III, the scenario cards and the common API may have been revised. **Locators in [Francis-SocNavPrinciples] are to arXiv v4** |
| V2 | Kleinmeier, Köster, Drury (2020), *J. R. Soc. Interface* 17(171), doi:10.1098/rsif.2020.0396 | arXiv:2005.12712**v2** (dated 8 October 2020) | The publisher returned HTTP 403 | Probably little: v2 is dated after acceptance. Not checked |

## Standard not attempted

| # | Source | Why | Effect |
|---|---|---|---|
| S1 | IEEE 1516 (HLA) | Sold by IEEE; no open copy was sought | HLA is covered through [Wang-LCIM] §4 and [Gomes-CoSim] §5.2 only. Nothing in this review rests on the standard's own text |

## What obtaining these would change

- **M1** would let the review cite ADICO from its source. It would not change the
  recommendation, which builds on IG 2.0, read in full ([Frantz-IG2]).
- **M4** would add a modern two-toolkit replication to Q2's evidence. Its direction, from a
  snippet only, agrees with the four studies read. If it agrees, risk 1 in
  [verdict.md](verdict.md) gets stronger.
- **V1** could add or rename scenarios in Q3's table of situation names.
