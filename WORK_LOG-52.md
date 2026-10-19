# Work Log — Issue #52: [Research] Literature: describing environments to LLMs (simulators and crowds first), and how well each method works

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/52
**Branch:** docs/52-environment-description-llm-review
**Started:** 2026-10-19

## Understanding the issue

negsim tells an LLM much less about a scene than a person in it could perceive. Layer 1 (live
negotiation) handles exactly two agents, and the place is one fixed paragraph per scenario type
(`persona_v1.yaml`, `scenes:`) plus a short report of distances and speeds. Layer 4 (rule
generation) describes one other person in detail (`describe.py`, `first_person`, `third_person`)
and everyone else in one line: "Other people are walking around you as well."
(`rulegen_negotiate_v2.yaml`, `place_others`).

Before any prompt is redesigned, the issue asks for a literature review, five papers read in full,
on how studies describe a simulator's environment (crowd simulators first) to an LLM, and what
evidence there is on how well each method works. Questions: Q1 methods (form, content, how numbers
and directions are written); Q2 measured comparisons of formats; Q3 how many agents are described
and how; Q4 perceivable versus omniscient, and visible attributes; Q5 the research gap, with the
searches behind it; Q6 a verdict for negsim (a proposal), with offline token counts for 2, 5 and 10
nearby people.

Literature only: no code, no change to `llm_negotiation/`, no LLM calls of any kind.

**Assumptions:**
- A1. **Base branch.** As the issue says, and as in track #34, the branch is cut from
  `docs/beginners-guide-issues-35-41` (PR #51), not `main`, and the PR will target it. `git checkout
  main` was not run (memory note on half-failed checkouts).
- A2. **Token counts (Q6).** "Counting tokens offline" is read as: render example descriptions as
  text and count them with an open tokenizer that runs locally, with no API call. DeepSeek publishes
  its tokenizer on Hugging Face; if it cannot be obtained offline, an open tokenizer of a similar
  family is used and named, and the counts are labelled estimates.
- A3. **Which negsim files may be read.** The issue lists what to read "before starting". For Q6 I
  may need to see an actual rendered description to count it; I will build examples from the
  templates already read (the `situation` block and `persona_v1.yaml`) rather than open more code.

## Plan

1. Read only the prescribed inputs (done; see the first progress entry).
2. Search: confirm the seed leads from their own pages (arXiv API, venue pages), and run new searches
   for the three relevance tiers. Record every search and every paper screened in `search-log.md`.
3. Choose the five, by tier: at least one with a measured comparison of description formats.
4. Fetch the five full texts to `refs/ed_*.pdf`, extract to `refs/ed_*.txt` with `pdftotext`, and
   search the extracts rather than reading whole documents.
5. Write `entries.md` (five full entries, every claim quoted with a locator), in the priority order
   the issue gives: Q1-Q3 for each, then Q5, Q4, Q6.
6. Write `findings.md` (method table, results with quotations, research gap with its searches),
   `verdict.md` (one page, a proposal, with offline token counts), `missing-papers.md`, the BibTeX.
7. Check every quotation against the cached text (a script), then `.gitignore` any non-open copies.
8. Push, open the PR against `docs/beginners-guide-issues-35-41`, comment on the issue.

## Progress log

### 2026-10-19 — Branch and prescribed reading
- What I did: checked `gh auth`, the remote and a clean tree; cut
  `docs/52-environment-description-llm-review` from `docs/beginners-guide-issues-35-41`. Read the
  prescribed inputs only: `describe.py` (module docstring, `first_person`, `third_person`),
  `situation.py` (module docstring), `persona_v1.yaml`, the `situation` block of
  `rulegen_negotiate_v2.yaml`; in `llm-behavioural-conflict.md` the entries [Wang-SAMALM],
  [Baimbetova-PedAwareAV], [Yoldas-YieldBias], [Seo-LLMDR] and the [Cross-HypotheticalMinds] row;
  `paper-summaries/02-sense-think-act-reflect.md` and `03-gamechat.md`. For conventions only:
  `literature/trained-deciders/` (entries, search log, missing papers) and `.gitignore`.
- Why: the issue limits the starting reading to these.
- Result / what I found: negsim's description today, in the issue's terms: **first-person or
  third-person prose**, in fixed lines; geometry as passage width and wall distances; one other
  agent with distance, egocentric direction ("ahead of you and 30° to your left"), speed, heading,
  whether the gap is closing, body width, and (when visible) apparent age and gender; numbers in SI
  units at fixed rounding (0.1 m along, 0.01 m across, 0.01 m/s, whole degrees). Anyone beyond the
  one neighbour: one generic line.
- Next step: searches and screening.

### 2026-10-19 — Searches, screening, and the five chosen
- What I did: confirmed the seven new seed leads from their arXiv abs pages (the arXiv API
  returned HTTP 429 every time, so the abs pages were used, as in earlier issues). Ran 10 web
  searches across the three tiers and for the gap (listed in `search-log.md` §3). Downloaded 15
  full texts into a scratch folder and screened each by searching its extract for the
  perception-to-text step, any cap or radius on who is described, and any measured comparison.
- Why: the issue asks for the five *most relevant*, by tier, preferring measured results and
  peer review, with at least one measured comparison of formats.
- Result / what I found: **the five**:
  1. [Durupinar-AffectCrowd] (tier 1, `[preprint]` 2026): Unity crowd simulator; perception by an
     8 m range, 200° field of view and occlusion; the three nearest visible people described in
     full, the rest as counts; prompt printed (Appendix A); seven prompt variants tested.
  2. [Ntarouis-CrowdGenAgents] (tier 1, PED 2025 in *Acta Polytechnica CTU Proceedings* 57, 2026,
     CC BY 4.0): radius-based perception with absolute positions and relative distances; runs at
     10 to 250 agents with request counts and latency. Its prompts are in a Zenodo supplement that
     refused automated download (HTTP 403): logged in `missing-papers.md` for the user to fetch.
  3. [Park-GenerativeAgents] (tier 2, UIST 2023): the sandbox world as a tree, each agent knowing
     only the subgraph it has seen; a perception radius; the architecture tier 1 papers build on.
  4. [Chen-MAPFLLM] (tier 2 with a measured format comparison): MAPF; image, obstacle-coordinate
     list and ASCII map compared (Table 3), and success by number of agents (Table 1). Published
     in TMLR 2025 under a new title; the OpenReview PDF refused download (403), so arXiv v2 is read.
  5. [Martorell-TextToSpace] (tier 2/3, measured): six text encodings of a grid world in three
     classes (Cartesian, topographic, prose), LLaMA 1B to 90B, with GLM statistics. Published in
     *Explainable Artificial Intelligence* (CCIS, Springer, 2025, pp. 268-291); arXiv v1 read.
- **Decision (mine, logged):** the issue's tiers, read strictly, would fill all five slots from
  tier 1 (at least six tier 1 candidates exist), which would leave no measured format comparison.
  I took the two tier 1 papers that specify the perception-to-text step most completely, then the
  three best measured or foundational ones. Talk like a Graph (tier 3, ICLR 2024) and BALROG
  (tier 2, ICLR 2025) were the closest misses: Chen already covers text against image in a
  multi-agent setting, and Martorell covers text against text in a spatial task, which is the
  comparison negsim needs; Talk like a Graph encodes abstract graphs, not space.
- Next step: write the five entries from the cached extracts.

### 2026-10-19 — Entries written and checked
- What I did: read the needed passages of each extract (methods, prompts, results, limits) by
  keyword search; rendered Chen et al.'s Table 1, Table 3 and Figure 9 with PyMuPDF to confirm cells
  the extract scrambled. Wrote `entries.md`. Wrote a checker that pulls every quoted fragment, looks
  for it in the named extract (whitespace, curly quotes and line-break hyphens normalised) and
  reports the page from the extract's form feeds.
- Result: 106 fragments, all found except quotations of negsim's own templates and of titles. **21
  page locators were wrong** (Ntarouis and Park, off by one or two pages from my hand count of page
  numbers) and were fixed by an exact-match replacement script. One unquoted claim ("100 human
  evaluators") was then backed with a quotation. The Park extract garbles μ, σ and d; quotations
  exclude the glyphs.
- Also found: Chen's Table 1 caption says ROOM-32-32-4 and the text ROOM-32-32-1; Martorell reports
  positive β for the classes that did worse, without a sign convention. Both are flagged in the
  entries rather than resolved.

### 2026-10-19 — Findings, verdict, token counts
- What I did: wrote `findings.md` (Q1 method table, Q2 results, Q3 table, Q4, Q5 gaps G1-G7 each with
  its searches), `verdict.md`, `token-estimates.md`, `search-log.md`, `missing-papers.md`, the BibTeX,
  a README row (5l), a findings paragraph and the layout-tree block.
- **Token counts (Q6):** downloaded DeepSeek-V3's `tokenizer.json` from Hugging Face (a file, not an
  LLM call) and counted locally with `tokenizers` 0.23.3. Situation block: today 220 tokens whatever
  N; everyone in prose 301 / 545 / 940 for 2 / 5 / 10 people; hybrid (3 nearest in full + summary)
  333 / 448 / 448; one JSON line per person 282 / 479 / 805. The script is embedded in
  `token-estimates.md`; I re-ran the embedded copy and it reproduced the table exactly.
- Extra reading beyond the prescribed list, for specific needs (assumption A3 widened): the pricing
  block of `pipeline/config.py` (cost line), the headings of `literature/demographic-personas/` (Q4
  cross-reference), `refs/td_amano2026_mobility.txt` (screening).
- Q4 outcome: none of the five describes others' age, gender or disability, so Q4's attribute half
  is answered by cross-reference to [Yoldas-YieldBias] and issue #16, as the issue asked, plus gap G6.

### 2026-10-19 — Pushed and PR opened
- Pushed `docs/52-environment-description-llm-review`; opened PR #53 against
  `docs/beginners-guide-issues-35-41` (stacked on #51), and linked it on the issue. The issue is left
  open for the PR's `Closes #52`.

## Open questions / risks

1. **Selection rule (my decision, needs a look).** Read strictly, the issue's tier order would fill
   all five slots from tier 1 and leave no measured format comparison. I took two tier 1 papers and
   three measured or foundational ones. If the supervisor prefers more crowd papers, SenseWalk and
   Liu et al. are the next tier 1 candidates (search log §4, §5).
2. **Chen et al.'s numbers are from arXiv v2.** The TMLR 2025 version is revised and retitled and
   could not be downloaded (OpenReview 403). Table 3 is the main Q2 evidence, so it should be
   checked against the published version before it is cited in the report (missing-papers V1).
3. **Ntarouis & Geraerts' prompts are unseen** (Zenodo supplement, 403). Their Q1 "numbers and
   directions" is "not reported" until the user fetches it in a browser.
4. **Thin evidence behind the proposal.** The two measured comparisons are puzzles (pathfinding,
   grid navigation), one with 5 scenarios a cell; the crowd paper's prompt variants never touch the
   perception text. The proposal is a design to test, and says so; its parameters (8 m, 200°, three
   in full) come from one preprint and are **design decisions for the supervisor**, not findings.
5. **Peer-review status of Ntarouis & Geraerts is inferred** from its place in the PED 2025 section
   of a proceedings journal; the PDF itself does not describe the review process.
6. **Token counts are estimates**: DeepSeek does not state that `deepseek-chat` uses exactly the
   published V3 tokenizer; only the situation block is counted; the example people are random and
   not filtered by a field of view.
7. **Gap claims are bounded by 13 web searches and 3 Crossref queries.** G4 (egocentric vs
   coordinates) may be partly answered by unread leads (Sidhu & Hockenmaier 2026; a TU Delft thesis).
8. **Durupinar is a single-author preprint** and prints no rendered perception description, so the
   form of its "distance and direction" is unknown.
9. Martorell's β signs and Chen's map-name inconsistency are flagged, not resolved.

## Summary (fill in at the end)

**What changed.** New folder `literature/environment-description/` with `entries.md` (five full
entries), `findings.md` (Q1-Q5), `verdict.md` (Q6, one page, a proposal), `token-estimates.md`
(offline counts and the script), `search-log.md`, `missing-papers.md` and
`refs-environment-description.bib`; cached sources `refs/ed_*` (the 12 MB Park PDF is git-ignored;
its extract is tracked); README row 5l, a findings paragraph and the layout tree. Nothing in
`llm_negotiation/` changed; no LLM was called.

**Why.** negsim describes one other person in detail and everyone else in one generic line; before
any prompt is redesigned, the issue asked what the literature says about describing multi-person
scenes to an LLM and how well each method works.

**What it found.** No comparison of description formats for pedestrian or crowd conflicts was found
(G1), nor a measure of decision quality against the number of nearby people described (G2). The
measured comparisons are spatial puzzles: a text map beat a coordinate list and an image for
multi-agent pathfinding at 4 and 8 agents ([Chen-MAPFLLM], Table 3); Cartesian encodings beat grid
drawings and prose for grid navigation ([Martorell-TextToSpace]). The one crowd simulator with an
explicit perception rule caps full descriptions at three people ([Durupinar-AffectCrowd]). Proposed
(to test, not adopt): a perceivability rule, the three nearest in full plus a summary line, motion for
each, capacities stated explicitly; four tests T1-T4 first.

**How it was verified (§5b).**
- Every quotation in `entries.md` and `findings.md` checked by script against the cached extracts;
  page locators taken from the extracts' form feeds (21 corrected). Table values checked on rendered
  pages where the extract scrambled them; every table value names its table.
- "Open questions / risks" above is not empty.
- Each of Q1-Q6 is answered in `findings.md` / `verdict.md`; Q4's attribute half is answered by
  cross-reference, as the issue asked, since none of the five covers it.
- Sources cached in `refs/ed_*`; every record confirmed from its own page.
- The token-count script was re-run from its embedded copy and reproduced the table.

