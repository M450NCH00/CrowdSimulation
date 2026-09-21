# Search log — issue #16

What was searched, what was found, what was deliberately excluded, and what could not be
obtained. Companion files: [`llm-demographic-effects.md`](llm-demographic-effects.md),
[`human-demographic-effects.md`](human-demographic-effects.md),
[`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md),
[`population-data-sources.md`](population-data-sources.md), [`refs.bib`](refs.bib).

Work carried out **2026-09-21**.

---

## 0. Novelty check (required by the issue)

> **The question:** does any paper already combine **(a)** LLM agents resolving a *spatial or
> navigation* conflict through dialogue with **(b)** *gender or age personas*?

### Answer: **No. No such paper was found.**

The two halves exist separately, and the gap between them is clean:

- **(a) exists, without demographics.** [Mahadevan-GameChat] (`arXiv:2503.12333v2`; IEEE MRS
  2025) has two agents negotiating doorway and intersection priority in natural language.
  **Verified directly against the cached full text** (`refs/mahadevan2025_gamechat.txt`): a
  case-insensitive search of the entire paper for `gender`, `female`, `male`, `age`, `aged`,
  `elderly`, `young`, `demographic` and `persona` returns **two hits, neither demographic**
  ("mimicking human behavior", §I p. 1, and author surnames in reference [29]). The agent
  prompt (§IV-C, p. 3) gives each agent only a **task** — "hospital agents, airport agents,
  and grocery agents" (§IV-C, p. 4). The same holds for the other navigation-conflict papers
  already in this repo: `chen2024why` (LLM multi-agent path finding) and `zhang2026sense`
  carry no demographic personas.
- **(b) exists, without navigation.** Every qualifying B1 paper puts gender or age personas
  into interacting LLM agents, but the conflicts are **verbal or economic**: task allocation
  ([Borah-ImplicitBias]), answer conformity and persuasion ([Li-SingleToSocietal]), price
  bargaining ([Khaki-Fairness]), political debate ([Bandaru-PoliticalDebate]), moral dilemmas
  ([Liu-SocraticDebates]). **None involves physical space, movement, right-of-way, or a
  spatial resource.**

**Nearest misses, and why each falls short:**

| Paper | How close it gets | Why it is not the gap |
|---|---|---|
| [Manoranjan-IdentityIncentives] (FAccT 2026) | Personas *override* payoffs in a 4-agent strategic game, by up to 90 percentage points | Personas are **occupational/role-based** (e.g. "industrialist"), not demographic. Confirmed by full-text search — see [`llm-demographic-effects.md`](llm-demographic-effects.md). |
| [Khaki-Fairness] (*Mathematics* 2026) | Gendered dyadic negotiation with concession dynamics, closest *structure* to a priority dispute | The contested resource is **price**, not space. No movement, no simultaneity, no deadlock. |
| [Tan-Unmasking] (NAACL 2025) | Gender **and** age personas on both parties, in scenarios built around **power disparity** | Single-response social scenarios, not spatial, not multi-turn negotiation. |
| [Ding-AsymmetricCompetitiveness] (*Symmetry* 2025) | Age and gender coupled to competitiveness **and to avoidance behaviour** in a navigation conflict | **No LLM and no dialogue** — a cellular-automata model with demographic coefficients. |

### What this means for how the FYP frames its gap

[inference] The gap is real, narrow and precisely stateable, which is better for the report
than a vague one. A defensible framing:

> GameChat-style agents negotiate spatial priority through dialogue but carry **no demographic
> identity**; the persona-bias literature gives demographic identities to interacting agents
> but only in **verbal and economic** conflicts. No published work joins them.

**Two caveats the FYP should state alongside that claim, so it is not overstated:**

1. **"No demographic identity" does not mean "neutral".** [Tan-Unmasking] (Abstract) finds
   the unprompted LLM default persona to be "middle-aged, able-bodied, native-born, Caucasian,
   atheistic males with centrist views". GameChat's agents are unprompted, so they inherit
   that default. The contribution is therefore **making an implicit demographic explicit and
   controllable**, not introducing one where none existed.
2. **Absence of a paper is not absence of a finding.** This review searched in English, via
   the routes listed in §2 below, over roughly one working session. A negative novelty result
   at that depth should be stated as "none found in this review", not as "none exists".

---

## 1. What was read first, to avoid re-collection

Per the issue's "Before searching" instruction, existing repo material was read before any
search:

- `literature/paper-summaries/` (issue #14) — including a full read of `03-gamechat.md`.
- `literature/llm-conflict-resolution/` (issue #8) and `literature/human-conflict-resolution/`
  (issue #12), plus all three `refs.bib` files.
- `dataset/generated/validation_report.md`, for the exact `run01` numbers.

**Branch note:** `main` contains **no** `literature/` directory at all — all of it lives on the
open PR stack #9 → #13 → #15. This branch is therefore based on
`docs/14-deep-read-paper-summaries` (the stack tip), not on `main`, following the convention
PRs #13 and #15 already established.

**Overlap found:** minimal. A grep of `literature/**` for `gender`, `female`, `male` and
`demand-withdraw` returns **nothing**. The existing collection covers the Rahim conflict-style
instrument, conversation-analytic work on verbal conflict, LLM multi-agent cooperation, and
pedestrian dynamics — **but no demographic-effect paper**. This issue does not duplicate any
existing entry.

**One paper deliberately not re-entered:** `yamamoto2019body` (Yamamoto, Yanagisawa, Feliciani
& Nishinari, *Transportation Research Part B* 122) is already in
`literature/llm-conflict-resolution/refs.bib` from issue #8. It turns out to contain a **gender
finding that no existing repo file records** (men rotate more when passing; shoulder width
48.4 cm vs 41.0 cm, p < 0.05). Per the issue's instruction to "reference it rather than
duplicating its entry", the finding is written up in
[`human-demographic-effects.md`](human-demographic-effects.md) but **no new BibTeX entry was
created**.

---

## 2. Search routes used

Because publisher sites block automated access unevenly, most verification went through
metadata APIs rather than article pages:

- **Crossref REST API** — authoritative title/author/venue/volume/pages/DOI/licence. Used for
  every non-ACL entry. Cached as `refs/cr_*.json`.
- **ACL Anthology `.bib` exports** — used verbatim for the three ACL/NAACL papers. Cached as
  `refs/*_acl.bib`.
- **arXiv abstract pages** — used for the `Comments` and `Journal reference` fields, which is
  how peer-review status was determined for every preprint. Cached as `refs/*_abs.html`.
- **Europe PMC REST** and **Semantic Scholar Graph API** — used to obtain publisher abstracts
  for two paywalled Elsevier papers.
- **Unpaywall** — used to check open-access availability before giving up on a paywalled paper.
- **data.gov.sg v2 API** — used for B5 dataset metadata.
- Web search was used **only to locate candidates**. No finding, number or citation in any
  deliverable comes from a search-result summary.

**Query themes run:** `LLM persona gender negotiation`; `persona-induced bias multi-agent`;
`LLM age persona fidelity`; `gender differences conflict management styles Rahim ROCI-II`;
`age differences conflict resolution strategies older adults`; `gender differences pedestrian
collision avoidance who yields`; `demand withdraw meta-analysis gender`; `Singapore
population by age group and sex`.

---

## 3. Coverage against the acceptance criteria

The issue requires **at least 2 qualifying papers per sub-area, or an explanation**.

| Sub-area | Qualifying papers | Met? |
|---|---|---|
| **B1** — gender/age personas in LLM-to-LLM interaction | 5: [Borah-ImplicitBias], [Li-SingleToSocietal], [Khaki-Fairness], [Bandaru-PoliticalDebate], [Liu-SocraticDebates] | ✅ |
| **B2** — persona fidelity | 5: [Hu-PersonaEffect], [Wang-IdentityGroups], [SiyangLiu-GenerationGap], [Tan-Unmasking], [Chu-Marketing] (+ [Liu-SocraticDebates], which spans B1 and B2) | ✅ |
| **B3** — real crowd/pedestrian behaviour | 5 recorded, but **only 2–3 are measurements of people**: [Rapos-CollisionAvoidance] and [Yamamoto-BodyRotation] firmly; [Minegishi-SlowPedestrians] with a qualification. [Zhu-MultiAttribute] and [Ding-AsymmetricCompetitiveness] are **simulations whose demographic effects are input parameters** | ⚠ see below |
| **B4** — human conflict resolution through talk | 3: [Holley-DemandWithdraw] `[foundational]`, [Yeung-OlderWorkers], [Filsecker-ROCI] | ✅ |

**B2 age fidelity, including older adults** (explicitly required): covered by
[Chu-Marketing] §VI-C (children and elderly), [SiyangLiu-GenerationGap] §5–6 (older adults'
value systems; age prompting fails in 8/13 categories), [Wang-IdentityGroups] (Baby Boomer /
Millennial / Gen Z axis; Gen Z misportrayed), [Tan-Unmasking] (Young / Middle-aged / Old),
and [Liu-SocraticDebates] §4.1 (age not consistently significant across models).

### ⚠ B3 is the weak sub-area, and the weakness is in the literature, not the search

Two of the three B3 seeds the issue supplied turned out to be **simulation models that assign
the demographic effect as a parameter and then recover it as a result** — [Zhu-MultiAttribute]
assigns female pedestrians 0.98 m/s against male 1.35 m/s (Table 3) before concluding that
crowds with more women evacuate more slowly; [Ding-AsymmetricCompetitiveness] assigns age and
gender competitiveness coefficients (Table 2). Both are recorded in full, because the issue
explicitly wanted a baseline for "how conventional crowd models encode demographic attributes
into conflict behaviour" — but **neither can serve as human evidence**, and neither is used as
such in [`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md).

That leaves **one paper in the entire review that actually measures who yields to whom by
demographic** ([Rapos-CollisionAvoidance]), and it was readable only as an abstract. This is
reported rather than padded, as the issue instructs.

---

## 4. Seeds: what happened to each

### Verified and written up (13)
All B1 and B2 seeds except the two below; all three B3 seeds; the one B4 seed. Each was opened
independently and its bibliographic fields confirmed from a publisher page, an ACL export, an
arXiv abstract page or a Crossref record.

### ⚠ Seeds whose titles in the issue are out of date (2)

1. **"When Personas Override Payoffs: Role Identity Bias in Multi-Agent LLM Decision-Making"**
   (`arXiv:2601.10102`) has been **retitled**. The current v6 (30 May 2026) is *"When Identity
   Overrides Incentives: Representational Choices as Governance Decisions in Multi-Agent LLM
   Systems"*, **accepted to ACM FAccT 2026**.
2. **The Wang / Morgenstern / Dickerson `[secondhand]` seed** has also been retitled — v1/v2
   were *"Large language models cannot replace human participants because they cannot portray
   identity groups"*; the published version is *"Large language models that replace human
   participants can harmfully misportray and flatten identity groups"*.

Also: **[Minegishi-SlowPedestrians] is a 2021 paper, not 2020.** The issue's ScienceDirect PII
(`S0379711220300345`) reads as 2020, but the Crossref record gives *Fire Safety Journal*
**volume 120, article 103041, March 2021**.

### ⚠ Seeds read but **not qualifying** (2)

Both were opened in full and both fail the issue's own selection criterion ("reports an
empirical result on how **gender or age** changes behaviour or outcomes"), because neither
varies gender or age:

- **[Manoranjan-IdentityIncentives]** — full-text search for `gender`, `female`, `male`, `age`,
  `elderly`, `demographic`, `man`, `woman` returns only incidental matches. Personas are
  occupational.
- **[Reza-SocialLaboratory]** (*The Social Laboratory*, `arXiv:2510.01295v1`, `[preprint]`) —
  full-text search for `gender`, `female`, `age` returns **zero** matches. Personas are
  "evidence-driven analyst" and "values-focused ethicist".

Both are recorded in [`llm-demographic-effects.md`](llm-demographic-effects.md) under
"Examined and read, but not qualifying", with their findings, because the issue asked what they
actually find and because both describe confounds relevant to any FYP experiment.

### ✅ The `[secondhand]` seed — verified

**Wang, A., Morgenstern, J. & Dickerson, J. P.** was traced through the reference list of
[Hu-PersonaEffect] (which cites the v1 title) to `arXiv:2402.01908`, then confirmed published
as **Nature Machine Intelligence 7(3):400–411, doi:10.1038/s42256-025-00986-z** from the
Crossref record (`refs/cr_wang.json`). Full text read. It is now the strongest human-grounded
paper in the review (3,200 human participants). **No seed remains unverified.**

---

## 5. Could not be obtained

| Item | Status | Why it matters |
|---|---|---|
| **Holt, J. L. & DeVore, C. J. (2005)**, "Culture, gender, organizational role, and styles of conflict resolution: A meta-analysis", *IJIR* 29(2):165–196, doi:10.1016/j.ijintrel.2005.06.002 | **Confirmed to exist** (Crossref, `refs/cr_holt_devore.json`) but **not opened**. Crossref carries no abstract; Semantic Scholar reports the abstract "elided by the publisher"; Unpaywall returns `is_oa: false` with no open location; ScienceDirect blocked. Copies on academia.edu / ResearchGate were **not** used, as they are not authoritative for verifying a citation | **The single most valuable missing item.** It is the canonical meta-analysis of gender and conflict style and would materially strengthen B4. **Obtainable through the university library.** |
| **[Rapos-CollisionAvoidance]** full text | Abstract only (Europe PMC record of the publisher abstract) | Its headline finding is already the most important human result in the review; the full text would confirm the **sample's country**, the participant instructions, and the limitations. |
| **[Minegishi-SlowPedestrians]** full text | Abstract only (Semantic Scholar record) | Needed to check the issue's claim that it discusses "inclination to care for or wait for elderly pedestrians" — **which the abstract does not support**. Also needed for participant counts. |
| **Giles & Williams (1994)**, *Patronizing the Young*, *Int. J. Aging and Human Development* 39(1):33–53 | Not opened | Cited by [Tan-Unmasking] as human corroboration of its Old→Young patronising-language finding. Opening it would upgrade row L9 of the comparison table from `no human evidence found` to a real comparison. |
| **Brunel & Nelson (2003)**; **Exley & Kessler (2022)** | Not opened | Cited by [Liu-SocraticDebates] §4.2 as the human baseline for gender and persuasive confidence. Opening them would upgrade row L6. |
| **Census of Population 2020** (SingStat) | Not opened | Would give a richer B5 breakdown; not required for the current scope. |

**Publisher access problems encountered** (recorded so the next person does not repeat them):
sciencedirect.com and linkinghub.elsevier.com blocked every route tried; mdpi.com returned
HTTP 403 while **mdpi-res.com served the same PDFs fine**; link.springer.com required
authentication; hal.science returned an access-control challenge.

⚠ **One trap worth recording:** `https://www.population.gov.sg/library/population-in-brief/`
returns **HTTP 200 but renders a "page could not be found" message** — a soft 404 that a
status-code link check will not catch. The working path is the direct PDF URL recorded in
[`population-data-sources.md`](population-data-sources.md).

---

## 6. Exclusions and scope discipline

- **Only gender and age were extracted.** [Li-SingleToSocietal], [Khaki-Fairness],
  [Tan-Unmasking], [Liu-SocraticDebates], [Wang-IdentityGroups] and [Borah-ImplicitBias] all
  study race and/or other attributes; their presence is noted in each entry and **no race,
  religion, disability or political-ideology finding is extracted anywhere**, per the issue.
- **Position papers were not collected.** Every entry reports an empirical result, with two
  qualifications flagged in-place: [Chu-Marketing]'s age finding is a qualitative observation
  with no metric, and [Filsecker-ROCI]'s result is psychometric rather than behavioural. Both
  are labelled as such rather than quietly counted.
- **Recency windows respected.** LLM papers 2024–2026 (all within the 2020+ window, all but one
  within the prioritised 2023–2026). Crowd/pedestrian papers 2019–2025 (within 2016–2026).
  Human conflict papers 2020 (×2), plus **one `[foundational]` pre-2016 paper**,
  [Holley-DemandWithdraw] (2010), with its justification recorded in both
  [`human-demographic-effects.md`](human-demographic-effects.md) and [`refs.bib`](refs.bib).
- **No padding.** Where a sub-area is thin (B3), it is said so above rather than filled with
  marginal papers.

---

## 7. Follow-ups worth doing, in priority order

1. **Obtain Holt & DeVore (2005)** through the university library. Highest value per unit
   effort in this entire review.
2. **Open Giles & Williams (1994), Brunel & Nelson (2003) and Exley & Kessler (2022).** Three
   short reads that would convert two `no human evidence found` / `not comparable` rows into
   real comparisons.
3. **Re-run a `run01` subset on a second model.** Not a literature task, but it is what
   [Liu-SocraticDebates] §4.2 makes unavoidable: that paper reports the gender direction
   *flipping between models*. `run01`'s finding currently rests on one model.
4. **Get the [Rapos-CollisionAvoidance] full text**, if only to confirm the sample's country —
   the review's most important human result is currently of unconfirmed nationality.
5. **Search experimental-economics bargaining literature for human gender effects.** Not
   attempted here; it is the natural human comparison for [Khaki-Fairness] (row L2).
