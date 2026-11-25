# Search log — issue #12

Queries run, routes used, what was rejected, what could not be reached. Kept so the
review can be re-checked and so nothing that failed is silently dropped.

Date of searching: **2026-09-19**.

## Method note — how "opened and confirmed" was satisfied

The issue requires every paper to be opened and its fields confirmed from the page. Most
publishers in this field block automated fetches (see the dead-end table). Where the
publisher page was unreachable, the routes used instead were, in order:

1. the **Crossref API record** (`https://api.crossref.org/works/<doi>`) — authoritative
   for title, authors, year, venue, volume, issue, pages, and often carries the
   publisher-supplied abstract;
2. the **OpenAlex record** (`https://api.openalex.org/works/doi:<doi>`) — reconstructs
   abstracts;
3. the **Semantic Scholar record**;
4. an **open-access PDF** where one existed, downloaded and text-extracted locally.

Each entry in `verbal-conflict-resolution.md` states which of these it rests on and
whether it is abstract-level or full text. All responses are cached in
[`../../refs/`](../../refs/) as `cr_*.json`, `oa_*.json`, `s2_*.json`, or `*.pdf`/`*.txt`.

**This is weaker than reading the article page itself**, and it is recorded that way
rather than described as "opened the paper".

## Seeds from the issue

| Seed | Status | Note |
|---|---|---|
| Pütz — quick termination of verbal conflicts | ✅ verified, listed | **Two authors: Pütz & Hassan**, 2024, JLAC 14(2):199–228. The issue listed Pütz alone. |
| Rahim (1983) ROCI-II `[foundational]` | ✅ verified, listed | AMJ 26(2):368–376, doi:10.2307/255985. Five-style names taken from Rahim & Magner (1995), since the 1983 abstract does not list them. 28-item instrument deliberately NOT reproduced. |
| Weider-Hatfield (1988) | ✅ verified, listed | MCQ 1(3):350–366. |
| "Resolving disagreements" (EFL, LLJ) | ✅ verified, listed | Toluei & Tahririan, LLJ 51(6):718–733. |
| Conversation Argument Coding Scheme (CACS) — find the primary source | ⚠️ **partially: identified, not opened** | See "Could not be reached" below. |
| Pomerantz (1984) `[secondhand]` | ⚠️ bibliographically verified only | Chapter confirmed (Structures of Social Action, pp. 57–101, doi:10.1017/cbo9780511665868.008). No abstract or full text obtainable, so **no categories are claimed from it**. Not listed as an entry. |
| Dersley & Wootton (2000) `[secondhand]` | ✅ verified, listed | ROLSI 33(4):375–406, doi:10.1207/s15327973rlsi3304_02. |
| Greatbatch & Dingwall (1991), "Dispute Resolution without Disputing" `[secondhand]` | ❌ **misattributed in the issue** | The paper with that exact title is **Angela Cristina Garcia**, *American Sociological Review* 56(6):818–835 (1991), doi:10.2307/2096258, single-authored. Crossref and OpenAlex agree. Greatbatch & Dingwall have separate mediation work (e.g. Dingwall, Greatbatch & Ruggerone, *Mediation Quarterly* 15(4), 1998; a 2008 chapter "Talk and Identity in Divorce Mediation"), but not this title. Listed under Garcia. |
| Rees-Miller (2000) `[secondhand]` | ⚠️ bibliographically verified only | *Journal of Pragmatics* 32(8):1087–1111, doi:10.1016/S0378-2166(99)00088-0. **No abstract available** from Crossref, OpenAlex or Semantic Scholar; Elsevier blocks automated access. No findings claimed. Not listed as an entry. |
| Sillars — verbal tactics coding, find the primary source | ✅ verified, listed | Primary published source: **Sillars, Coletti, Parry & Rogers (1982)**, HCR 9(1):83–95. The **coding manual** is Sillars (1986), University of Montana — see "Could not be reached". |

## Queries run

Crossref/OpenAlex/Semantic Scholar API lookups (by DOI or bibliographic query):
- `A measure of styles of handling interpersonal conflict Rahim`
- `Complaint sequences within antagonistic argument Dersley Wootton`
- `Dispute resolution without disputing interactional organization mediation hearings Greatbatch Dingwall` → returned **Garcia**
- `Power severity and context in disagreement Rees-Miller`
- `Agreeing and disagreeing with assessments preferred dispreferred turn shapes Pomerantz`
- `Conversational Argument Coding Scheme origins development Canary Seibold`
- `Sillars verbal tactics coding scheme interpersonal conflict integrative distributive avoidance`
- `Confirmatory factor analysis styles handling interpersonal conflict … Rahim Magner 1995`
- `Conflict in Dating and Marital Relationships Caughlin Vangelisti SAGE Handbook of Conflict Communication`
- `Strategic Interruptions in Small Claims Mediation Garcia Conflict Resolution Quarterly`

Web searches:
- `"Conversational Argument Coding Scheme" CACS categories assertion proposition reason objection reliability coding manual`
- `Rahim ROCI-II five conflict styles … 2016..2026 validation study open access`
- `arXiv 2024 2025 large language models qualitative coding deductive coding scheme inter-rater reliability Cohen's kappa human coders dialogue`
- `conversation analysis mediation talk "dispute resolution" coding categories 2018..2026 open access …`
- `open access 2019..2026 study coding conflict conversations "conflict management styles" OR "conflict tactics" transcripts Cohen's kappa …`
- `communicationcache.com Sillars "verbal tactics coding scheme" … subcategories`
- `Pütz Hassan "quick termination of verbal conflicts" Bielefeld repository OR PUB OR open access full text`

## Dead ends and blocks

| Source | What happened | Workaround used |
|---|---|---|
| John Benjamins (`jbe-platform.com`, `benjamins.com`) | HTTP 403 on both the journal page and the catalogue page | Crossref + Semantic Scholar abstracts |
| Taylor & Francis | HTTP 403 | Crossref/OpenAlex/S2 abstracts |
| Wiley (`onlinelibrary.wiley.com`) | HTTP 403 | OpenAlex abstract |
| SAGE (`journals.sagepub.com`; `sk.sagepub.com`) | article/chapter paywalled; `us2.sagepub.com` PDF link returned HTML, not a PDF | Crossref abstract; for the handbook chapter, a separate SAGE-hosted PDF did download and was read |
| JSTOR / Academy of Management | not reachable | Crossref + OpenAlex |
| Elsevier / ScienceDirect | blocked; no abstract in any aggregator for Rees-Miller | none — recorded as unverified content |
| `pedocs.de` (EJPA 2020 conflict-styles paper) | connection refused, then curl timeout | dropped; the A1 slot is covered by Rahim & Magner (full text) |
| ResearchGate / Academia.edu | login-walled | not used |

## Papers considered and rejected (failed the codeability test)

The issue's test: *given an LLM transcript, which category from this paper would be
assigned, and on what textual evidence?*

| Candidate | Why rejected |
|---|---|
| EJPA 2020 "The structure of conflict styles in adolescents" | Could not be downloaded (see above). Would in any case be a **self-report factor-structure** study, like Rahim's — no transcript categories. |
| Wikipedia "Conflict management"; `mondodigitale.org` teaching PDFs; `db.arabpsychology.com` scale listing | Not primary sources. Used for nothing. |
| "Towards a Theory of Close Analysis for Dispute Mediation Discourse" (*Argumentation*, 2015) | Theoretical framework for analysis, no named category set retrievable; also pre-window with no codeable scheme confirmed. Not opened. |
| arXiv `2609.11101` ProMediConv; arXiv `2509.06586` LLM dispute-mediation simulation | These are **LLM-agent** papers, not human-behaviour papers. Validating LLM output against other LLM output is the circularity the issue warns about. Out of scope here; may be relevant to methods later. |
| General IRR/NVivo methods papers surfaced by the kappa search | Method papers about reliability procedure, not conflict categories. |

## Could not be reached (would materially improve the review)

1. **CACS category list.** `canary2010origins` (CMM 4(1-2):7–26) and the Seibold & Weger
   (2017) chapter in *Researching Interactive Communication Behavior* are both confirmed
   to exist, but every route to their category list was blocked (T&F 403; SAGE Knowledge
   paywall; the one SAGE-hosted PDF that downloaded turned out to be a different chapter).
   The web search returned a partial description — "groups' arguments consisted mainly of
   Assertions, Elaborations, and Agreement" — but that came from a **search-result
   summary, not from an opened paper**, so it is **not** used anywhere in the review.
   **Highest-value retrieval through the NTU library.**
2. **Sillars (1986) VTCS coding manual** — holds the subcategories under avoidance /
   integrative / distributive, and probably a published reliability figure.
3. **Pütz & Hassan (2024) full text** — holds the exact frequency counts behind
   "submission most frequent", the three named minimization patterns, and the corpus size.
4. **Pike & Sillars (1985)**, cited in `modality-note.md` via Caughlin & Vangelisti.
5. **Pomerantz (1984)** and **Rees-Miller (2000)** full texts.

## Coverage against the issue's sub-areas

| Sub-area | Covered? | By |
|---|---|---|
| A1 conflict-style taxonomies | ✅ | Rahim 1983; Rahim & Magner 1995; Weider-Hatfield 1988 |
| A2 CA of disagreement (incl. non-resolution) | ✅ | Pütz & Hassan 2024; Toluei & Tahririan 2022 (non-resolution); Dersley & Wootton 2000 |
| A3 interaction coding schemes for conflict talk | ⚠️ partial | Sillars et al. 1982 (three classes only; manual and CACS not obtained) |
| A4 dispute resolution / mediation | ✅ | Garcia 1991; Garcia 2025; Hale et al. 2025 (KODIS) |
| A5 LLM-assisted coding (optional) | ✅ | Hila & Hauser 2025; Borse et al. 2025 |

**A3 is the weak sub-area.** One scheme, at its coarsest level, with no reliability
figure. That is stated rather than padded with additional papers that do not meet the
codeability test.
