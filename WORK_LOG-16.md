# Work Log — Issue #16: [Research] Literature: gender and age personas in LLM-to-LLM conflict resolution

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/16
**Branch:** `docs/16-demographic-personas-literature`
**Base branch:** `docs/14-deep-read-paper-summaries` (stack tip — `literature/` is not yet on `main`)
**Started:** 2026-09-21

## Understanding the issue

The FYP wants LLM agents to negotiate who yields in a spatial conflict (GameChat-style),
then distil a reusable resolution pattern. Phase 1's `run01` dataset already shows a
systematic effect: **female personas yield more than male personas** across many
scenario/age cells (`dataset/generated/validation_report.md`, "REVIEW" section, 54 items,
e.g. `bus_queue_boarding/child: yield_likelihood male=0.433 female=0.867, Δ=-0.43`).

The question this review must serve is **not** "is there a gender effect" — run01 already
shows one. It is: **is that effect realism or artifact?** Inside a transcript the two are
indistinguishable. They separate only by comparing the LLM effect against human evidence.
Hence the deliverable that matters is `realism-vs-bias-comparison.md`, and every other
file feeds it:

- B1/B2 (LLM side) → the left column: what effects LLMs show, how personas were specified,
  whether the persona did anything at all.
- B3/B4 (human side) → the right column: what real pedestrians and real disputants do.
- B5 → population composition, so a simulated crowd's demographic mix is defensible.

### Assumptions I am making (flagging per CLAUDE.md)

1. **Location scope = Singapore.** CLAUDE.md states "Scope confirmed 2026-09-04: dataset is
   Singapore-only, organised by age group and gender". B5 therefore targets Singapore
   sources. Recorded, not blocking.
2. **Base branch = `docs/14`, not `main`.** `main` contains no `literature/` directory at
   all; PRs #9 → #13 → #15 are a stack. Branching off `main` would make the PR diff
   unreadable against the literature it must not duplicate. This follows the convention
   already established by PRs #13 and #15.
3. **"Age" includes the persona age *bands* used in run01** (child, teenager, young adult,
   middle-aged, elderly), matching `dataset/personas.yaml`, when judging whether an LLM
   paper's age manipulation is comparable.

## Plan

1. Preconditions; read existing `literature/**` and all `refs.bib` files so nothing is
   re-collected. Record what is already present.
2. **Confirm the GameChat claim** the issue flags: that GameChat's agents carry no gender
   or age. Check the cached PDF text (`refs/mahadevan2025_gamechat.txt`) directly rather
   than trusting the existing summary.
3. Open every verified seed lead, one at a time. Confirm title/authors/year/venue/DOI from
   the page itself. Record peer-review status; for arXiv preprints, check for a published
   version.
4. Extract per templates L (B1/B2) and H (B3/B4). Locator on every number.
5. Fill gaps with targeted searches where a sub-area is short of 2 qualifying papers.
6. Verify the `[secondhand]` seed (Wang / Morgenstern / Dickerson) or report not found.
7. Build `realism-vs-bias-comparison.md`, including the run01 row.
8. B5: Singapore population composition sources.
9. `search-log.md`, including the novelty check.
10. Self-verify against §5b of `github_issue_workflow.md` and the issue's acceptance
    criteria, then PR.

## Progress log

### 2026-09-21 — Preconditions and scoping
- What I did: checked remote/auth/tree-clean; enumerated branches and PR bases; read
  `literature/paper-summaries/03-gamechat.md` and every existing `refs.bib`; pulled the
  gender findings out of `dataset/generated/validation_report.md`.
- Why: the issue forbids re-collecting papers already in the repo, and I needed the exact
  run01 numbers for the comparison table's run01 row.
- Result / what I found:
  - `main` has **no** `literature/` directory; all literature lives on the open PR stack
    #9 → #13 → #15. Branching off `docs/14` accordingly.
  - Existing bib coverage (must not duplicate): Rahim conflict-style instrument papers,
    CA-based verbal conflict papers (Putz, Toluei, Dersley, Garcia, Pomerantz,
    Rees-Miller), LLM multi-agent papers (GameChat, Shall We Team Up, Sense/Think/Act/
    Reflect, NegotiationArena, GovSim, Abdelnabi, Ashery), and pedestrian-dynamics papers
    (Yamamoto body rotation, Boomers data guidance, Echeverría-Huarte, Terwilliger, Jülich
    archive). **None of these are demographic-effect papers** — the overlap risk is low;
    the Rahim cluster is the one to cross-reference rather than re-enter, per the issue's
    B4 instruction.
  - run01's effect is large and consistent in direction: every flagged
    `yield_likelihood` delta is male < female, Δ ranging −0.27 to −0.43.
- Next step: verify the GameChat "no gender/age" claim from the cached full text.

### 2026-09-21 — GameChat claim confirmed before anything else
- What I did: searched the cached GameChat full text (`refs/mahadevan2025_gamechat.txt`)
  case-insensitively for `gender`, `female`, `male`, `age`, `aged`, `elderly`, `young`,
  `demographic`, `persona`.
- Why: the issue explicitly says "Confirm this against the GameChat paper itself before
  relying on it", and the whole novelty claim rests on it.
- Result: **two hits, neither demographic** ("mimicking human behavior" §I p.1, and author
  surnames in ref [29]). The agent prompt (§IV-C p.3) gives each agent only a *task*. The
  existing summary was right. Noted separately that the prompt contains an unfilled slot —
  the agent is "taking **someone**", a passenger who is never described.
- Next step: open the B1 seeds.

### 2026-09-21 — B1/B2 extraction; two seeds turned out not to qualify
- What I did: opened all 7 B1 seeds and all 5 B2 seeds (including the `[secondhand]` one).
- Why: the issue forbids secondhand citation, so each had to be opened and its metadata
  confirmed from a publisher page, an ACL BibTeX export, an arXiv abs page or Crossref.
- Result / what I found:
  - **Two B1 seeds do not qualify.** *When Personas Override Payoffs* (now retitled *When
    Identity Overrides Incentives*, FAccT 2026) and *The Social Laboratory* both use
    **role-based, not demographic** personas — verified by full-text search, which returns
    zero `gender`/`age` matches in the latter. Recorded with their findings under "Examined
    and read, but not qualifying" rather than silently dropped, since the issue asked what
    they actually find.
  - **The `[secondhand]` seed resolved.** Traced Wang / Morgenstern / Dickerson through
    Hu & Collier's reference list to arXiv:2402.01908, then confirmed published as **Nature
    Machine Intelligence 7(3):400–411** via Crossref. It had been **retitled** between
    versions. It is now the best human-grounded paper in the review (3,200 participants).
  - **Two other seed titles are out of date in the issue**, and one year is wrong
    (Minegishi is 2021, not 2020) — all recorded in `search-log.md`.
  - **The most consequential single finding:** Liu et al. (*Synthetic Socratic Debates*)
    §4.2 report the gender effect **flipping direction between models** — GPT-4o matches the
    human literature while LLaMA-4-Maverick and Qwen3 reverse it. `run01` used one model.
- Next step: B3/B4.

### 2026-09-21 — B3 turned out to be the weak sub-area, for a substantive reason
- What I did: opened the three B3 seeds, then went looking for genuinely empirical work.
- Why: reading the seeds showed a problem the issue's template does not anticipate.
- Result / what I found:
  - **Two of the three B3 seeds are simulations whose demographic effect is an input
    parameter.** Zhu et al. *assign* women 0.98 m/s against men's 1.35 m/s (Table 3), then
    conclude that crowds with more women evacuate more slowly. Ding & Liu assign age and
    gender competitiveness coefficients. Neither is a discovery about people.
  - **Decision (change of direction from my original plan):** rather than treat these as
    human evidence, I added an explicit type-(a)/type-(b) warning at the top of
    `human-demographic-effects.md` and **excluded both from the comparison table**. This
    was not in the plan; I changed it after reading the sources. Both are still recorded in
    full, because the issue specifically wanted a baseline for how conventional models
    encode demographics.
  - **Searched for real measurements** and found the one that matters: Rapos et al. 2021
    (*Gait & Posture*), which measures who yields between older and young adult walkers.
    **Only the abstract was obtainable** (Elsevier); recorded as abstract-verified.
  - Also found that `yamamoto2019body`, **already in the repo from issue #8**, contains a
    gender finding no repo file records. Per the issue's instruction I referenced it rather
    than creating a duplicate BibTeX entry.
- Next step: B4, then the comparison table.

### 2026-09-21 — B4, and the keystone paper
- What I did: processed the Filsecker seed, then searched for papers reporting actual
  gender/age *differences*, since that seed only tests measurement invariance.
- Result / what I found:
  - **Yeung & Ho 2020** (Frontiers, **Hong Kong Chinese** sample, ROCI-II) — the nearest
    cultural match to Singapore available. Reports a **null gender effect** on all five
    conflict strategies, and age effects whose **zero-order and mediated directions
    disagree** (age is *negatively* correlated with obliging, r = −0.18, while the mediated
    path through "focus on limitations" is positive). Only the mediated result is in its
    abstract; both are recorded.
  - **Holley, Sturm & Levenson 2010** `[foundational]` — the decisive test of whether the
    canonical demand/withdraw gender difference is caused by gender. It is not: relative
    desire for change explains R² = 0.41, couple gender composition adds R² = .004. This is
    the conceptual keystone for the whole realism-vs-bias question.
  - **Holt & DeVore (2005)**, the canonical meta-analysis, **could not be obtained** —
    confirmed to exist via Crossref, but the abstract is elided by the publisher, it is not
    open access, and ScienceDirect is blocked. Reported as not obtained rather than
    summarised from search results, per the sourcing rules.
- Next step: comparison table, B5, search log.

### 2026-09-21 — Comparison table: a case the issue's status values do not cover
- What I did: built `realism-vs-bias-comparison.md`, 17 rows.
- Decision point worth recording: **three rows put an LLM effect against a human *null*.**
  That contradicts the LLM result but is not a direction reversal, so none of the four
  permitted status values fits cleanly. I used `not comparable` (the settings also genuinely
  differ) and stated the null explicitly in the Setting-differences column, then flagged the
  judgement call at the top of the file so the supervisor can overrule it with a fifth value.
- Result: 1 `same direction`, 3 `opposite direction`, 8 `no human evidence found`,
  5 `not comparable`. **Of the three rows where a direction could be compared, all three run
  opposite to the LLM.** No overall conclusion drawn — the issue forbids it and the file is
  marked DRAFT.

### 2026-09-21 — Verification pass
- What I did: checked every internal link resolves; checked all 17 BibTeX keys are defined
  and used, and that the 6 cross-referenced external keys match the repo's actual keys;
  grepped for statistical claims lacking a locator marker; re-counted the comparison table's
  status rows.
- Result: links and keys all pass. The locator grep returned 20 hits, all of which turned
  out to be line-wrap artifacts (the locator sits on the next line of the same bullet) —
  confirmed by reading each. **One real defect found and fixed:** the comparison table's
  row-count summary did not match its own rows. Recounted and corrected.

## Open questions / risks

- **Location scope.** Recorded as Singapore per `CLAUDE.md` (assumption 1 above). If the
  supervisor widens the simulation beyond Singapore, `population-data-sources.md` must be
  redone — and `siyangliu2024generation` §4 shows the LLM age skew is itself
  culture-dependent, so the LLM-side findings would need rechecking too.
- **⚠ Which Singapore population?** Citizens, residents and total population have different
  age and sex mixes. A public-space crowd is the *total* population, which includes a large
  non-resident share. `pipeline/` currently carries population weights marked `VERIFY`
  (README, A1) and does not appear to make this distinction. **This needs a decision before
  any weighting is relied on.**
- **⚠ The strongest human comparison rests on one abstract.** Rapos et al. 2021 is the only
  located study that measures who yields to whom by age between real pedestrians, and only
  its abstract was obtainable. Its sample's *country* is unconfirmed. If that result is
  misread, row RUN01-A of the comparison table changes.
- **⚠ Holt & DeVore (2005) is missing**, and it is the canonical meta-analysis for B4's
  gender side. Obtainable through the university library; recommended before the supervisor
  meeting.
- **Three human papers cited *by* LLM papers were never opened** (Giles & Williams 1994;
  Brunel & Nelson 2003; Exley & Kessler 2022). They are named in `search-log.md` as the
  cheapest way to upgrade two comparison-table rows.
- **`run01` used one model.** Given that Liu et al. §4.2 report the gender direction flipping
  between models, `run01`'s female-yields-more finding cannot currently be described as "what
  LLMs do". A second-model subset run is a literature-motivated experiment, but the standing
  supervisor instruction in `README.md` is **no new generation until the literature review is
  discussed**, so it is recorded as a recommendation, not done.
- **I could not read Table 1 of `borah2024implicit` reliably** (the two-column extraction
  merges the MODEL and SETTING columns). Caption- and prose-level claims are cited instead,
  and the entry warns anyone citing a specific cell to re-read the PDF.
- **An internal inconsistency in `khaki2026fairness` §4.2** is recorded as printed: the text
  says buyers "benefit more from a female seller" while the numbers show $12.56 vs $12.57 in
  the other direction. The authors call the difference negligible; the entry says so.
- **Repo size.** `refs/` now holds roughly 90 MB. I deliberately did **not** commit one 19 MB
  PDF (`b3_asymmetric_competitiveness.pdf`), keeping its tracked text extract instead and
  recording the download URL in `.gitignore`. If repo growth is a concern, the other large
  PDFs are the next candidates for the same treatment.

## Summary

**What changed.** Added `literature/demographic-personas/` with six files:
`llm-demographic-effects.md` (B1/B2 — 10 qualifying papers plus 2 read-and-rejected),
`human-demographic-effects.md` (B3/B4 — 8 entries), `realism-vs-bias-comparison.md`
(17 rows, marked DRAFT), `population-data-sources.md` (B5 — 5 verified Singapore sources),
`search-log.md` (including the novelty check), and `refs.bib` (17 entries). Cached every
obtainable source under `refs/`. Updated `README.md` with the roadmap status, three findings
that bear on `run01`, and a pointer from the existing A1 population-weights assumption to the
new B5 sources.

**Why.** Issue #16 asks whether `run01`'s female-personas-yield-more pattern is realism or
artifact. That cannot be answered from an LLM transcript; it needs an LLM-side effect placed
beside human evidence on the same behaviour. The four sub-areas feed that one comparison.

**How it was verified** (no test suite applies; §5b of `github_issue_workflow.md`):
- Every paper opened independently; bibliographic fields confirmed from a publisher page, an
  ACL Anthology BibTeX export, an arXiv abstract page or a Crossref record — all cached under
  `refs/`. Two papers were obtainable only as abstracts and are labelled as such everywhere
  they are used. One could not be obtained at all and is reported, not summarised.
- Peer-review status recorded for all 17 entries; every arXiv item checked for a published
  version, which turned up three published versions the issue did not list and two retitled
  papers.
- Locator on every number, checked mechanically and by reading.
- Uncertainty marked `[needs verification against full text]` where it applies; inferences
  marked `[inference]` and kept separate from reported findings.
- Internal links all resolve; all 17 BibTeX keys defined and used; the 6 keys referencing
  existing repo entries checked against the repo's actual keys.
- One real defect found and fixed during verification (the row-count summary).

**What I did not do.** No LLM was run, no experiment, no bias benchmark — out of scope per the
issue. No dataset was regenerated, per the standing supervisor instruction in `README.md`.
Holt & DeVore (2005) could not be opened and is therefore absent from B4 rather than
summarised secondhand.
