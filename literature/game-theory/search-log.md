# Search log — issue #20 (game theory for communication-free conflict resolution)

What was searched, what was found, what was deliberately excluded, what could not be obtained, and
the **framing check** the issue requires. Sub-area files:
[G1](g1-conflict-games-conventions.md) · [G2](g2-norm-emergence.md) · [G3](g3-cheap-talk.md) ·
[G4](g4-game-theoretic-crowd-models.md) · [G5](g5-llm-agents-game-theory.md) ·
[G6](g6-transfer-across-games.md) · [rule catalogue](candidate-rule-catalogue.md) ·
[refs](refs-game-theory.bib)

Work carried out **2026-09-30**.

---

## 0. THE FRAMING CHECK (required by the issue)

> The issue asks: "state, with sources, whether the literature supports describing this FYP's
> extracted pattern as a **convention** or **correlated equilibrium**, and note any mismatch between
> the standard definitions and what this project actually plans to extract. If the standard concepts
> do not fit, say so plainly; that is a useful finding, not a failure."

### Answer, in one paragraph

**Partly, and the mismatch is real.** "Correlated equilibrium" is defensible **if** the FYP's rule
conditions each agent's action on a shared observable cue, and there is direct support for calling
such a thing a convention. **But two of the standard definitions of *convention* require that the
alternatives being chosen between are *equivalent* or *arbitrary*, and the FYP's conflict scenarios
are not.** In a doorway deadlock, passing and yielding are not equivalent — one costs you time and the
other does not. On the strictest reading, what the FYP extracts is therefore **not a convention** in
the technical sense, and calling it one without qualification would be wrong. The better term, which
is precise, standard in multi-agent systems, and does not carry the equivalence requirement, is
**social law** in Shoham & Tennenholtz's sense. Full reasoning below.

### The evidence, with sources

**(a) "Convention as a correlated equilibrium" is a real, citable position.** The highest-priority
seed in the issue asserts it in its own abstract: "An important way to resolve games of conflict
(snowdrift, hawk–dove, chicken) involves adopting a convention: **a correlated equilibrium** that
avoids any conflict between aggressive strategies" ([Foley-ConflictConvention], *J. R. Soc. Interface*
15:20170835, Abstract). It attributes the position to others: "other scholars have identified
correlated equilibria as central to conventions" (§4), citing Vanderschraaf (1995), whose paper is
literally titled *Convention as correlated equilibrium* (confirmed, **not opened** — see §4 below).
So the framing has a home in the literature.

**(b) But the definitions of "convention" that I could read carry an equivalence requirement.**
- The clearest statement found anywhere in this review is in [Ashery-Reply]: "we use **'convention' to
  refer to a pattern of behavior shared throughout a community, defined as the outcome that everyone
  expects in interactions allowing **two or more equivalent actions**".
- [Centola-SpontaneousEmergence] built its whole experiment on that requirement: "to eliminate any
  preexisting bias in the evolutionary process, we studied the emergence of **arbitrary linguistic
  conventions, in which none of the options had any a priori value or advantage over the others**"
  (Introduction).
- [Foley-ConflictConvention] uses the same language: convention-like behaviour is "strategic behaviour
  uniformly adopted from among **equally viable alternatives** that is self-enforcing" (§4), and the
  bourgeois/paradoxical pair are described as "equally efficient" (§1).
- Young's definition, **as quoted by** [Foley-ConflictConvention] §4, is the one that does *not*
  obviously require equivalence: "a pattern of behaviour that is customary, expected and
  self-enforcing".

**(c) The FYP's scenarios do not satisfy the equivalence requirement.** `dataset/scenarios.yaml`
covers bottlenecks, crossflow and doorway deadlocks. In each, the two available actions — proceed, or
yield — have **asymmetric payoffs for the agent taking them**: yielding costs time, proceeding does
not. That is the defining feature of an anti-coordination *conflict* game, and it is why
[Chen-NPersonHawkDove] classifies Hawk–Dove as "an **anti-coordination** game" (Introduction) as
opposed to a coordination game.

**(d) The literature itself notes the definitions are unsettled, which helps.**
[Ashery-Reply] footnote 2 is unusually candid: "the literature on conventions is vast and scattered.
As noted in [9], the two influential reviews 'The Evolution of Norms' and 'The Evolution of Social
Norms' **do not share a single bibliographic entry**, and different definitions exist (a meta naming
game?). For example, **the requirement that the initial alternatives are equivalent for the agents can
be relaxed** (see e.g. [13])." So the equivalence requirement is a common but not universal condition.

**(e) Meanwhile, a term that fits exactly is available.** [Shoham-SocialLaws] defines a **social law**
as a set of (action, condition) prohibitions (Definition 2.1) and a **legal plan** as a total function
`DO : S → A` (Definition 3.1), with the motivating example being *keep to the right* (§1). **Nothing in
that definition requires the alternatives to be equivalent or arbitrary.** Keeping right and keeping
left are arbitrary relative to each other, but "yield to the person in the doorway" is a perfectly good
social law even though yielding is costlier than proceeding. And the concept comes with the
offline/online cost split the FYP needs (Theorem 3.1 plus the "computed off-line" remark, §3).

### What I recommend the report do (this is a design decision needing sign-off)

1. **Use "social law" or "convention-like rule" as the primary term**, sourced to
   [Shoham-SocialLaws] Definitions 2.1 and 3.1. It is precise, it fits, and it is standard in the
   multi-agent-systems literature the FYP is contributing to.
2. **Use "correlated equilibrium" only for rules that genuinely condition on a shared cue** — R3 and
   R4 in the [rule catalogue](candidate-rule-catalogue.md). It would be an overclaim for rules like
   R9 (a stochastic contention matrix), which is not an equilibrium concept at all.
3. **If the report uses "convention", attach Young's definition** ("customary, expected and
   self-enforcing", quoted in [Foley-ConflictConvention] §4) **rather than the equivalence-based
   ones**, and say why in a footnote. That is defensible; using the equivalence-based definitions
   would not be.
4. **State the mismatch explicitly rather than hiding it.** It is a genuine finding: *the
   conflict-resolution rules this project targets sit in a gap between "convention" (which usually
   presumes equivalent alternatives) and "norm" (which usually presumes enforcement). "Social law" is
   the closest fit.*

### One caveat on this whole check

⚠ **I could not open Aumann (1974/1987), Lewis (1969), Schelling (1960) or Vanderschraaf (1995)** —
see §4. So this framing check rests on definitions **as quoted inside papers I did read**, plus
Shoham & Tennenholtz's own definitions, which I read at source. It is enough to establish that a
mismatch exists and to recommend a term. It is **not** enough to state Aumann's formal definition of
correlated equilibrium in the report. **Getting Vanderschraaf (1995) and Aumann (1987) from the
university library is the single highest-value follow-up from this issue.**

---

## 1. What was read first, to avoid re-collection

Per the repo's convention (`CLAUDE.md`) and the precedent set by issues #16 and #18, existing
material was read before searching:

- `CLAUDE.md`, `README.md`, `github_issue_workflow.md`
- `literature/demographic-personas/` (issue #16) — including its search log's novelty-check method,
  which shaped the treatment of prior art in [G6](g6-transfer-across-games.md) §3, and its type-(a)
  vs type-(b) distinction (measurements of people vs simulations where the effect is an input
  assumption), which is reused for [Bouzat-RoomEvacuation] in [G4](g4-game-theoretic-crowd-models.md)
- `literature/paper-summaries/` (issues #14, #18), `literature/llm-conflict-resolution/` (#8),
  `literature/human-conflict-resolution/` (#12) and all their `refs.bib` files
- `refs/` — where **`ashery2025_social_conventions_oa.html` was already cached from issue #16**, so
  the G5 anchor paper was partly in hand before this issue started

**Branch note.** `main` contains **no** `literature/` and no `refs/`; every prior literature PR (#9,
#13, #15, #17, #19) is still open, and the repo's established practice is to cut each issue branch
from the previous one. This branch was therefore cut from
`origin/docs/18-demographic-paper-summaries` (`f3427b1`) rather than from `main`, deliberately, so the
prior literature and the `refs/` cache stay citable. Logged as assumption A1 in `WORK_LOG-20.md`.

**No duplication.** Nothing catalogued in issues #8/#12/#14/#16/#18 is re-entered here.
`ashery2025` appears in this issue's bib because this issue is the first to **read and analyse** it
(issue #16 only cached the page).

---

## 2. Sourcing method, stated so it can be audited

1. **Every bibliographic field** was confirmed from a **Crossref record fetched during this work** and
   cached — 24 records in `refs/gt_crossref_all.json` plus individual files `refs/gt_cr_*.json`.
   Nothing was taken from a search-engine summary.
2. **Published versions were preferred over preprints**, as the issue requires. See §3.
3. **Every paper's read-depth is stated in its own entry** as one of: full text / abstract only /
   bibliographic record only. Locators are scoped to what was actually read — an abstract-only entry
   cites abstract sections and **never invents page numbers**.
4. **Where a preprint was read but the published version was not**, the entry says so and warns that
   section and equation numbers must be re-checked. This applies to Chen 2017, Hall 2020,
   Bonnemain 2023 and Bouzat & Kuperman 2014.
5. **No content claim anywhere is sourced to another paper's reference list.** Where a rule or result
   is known only through a survey's summary, it is attributed to the survey, in the survey's words,
   and excluded from the rule catalogue's main table (see [catalogue](candidate-rule-catalogue.md) §3).
6. **Third-party research code was not executed**, per the repo guardrail. Two repositories were
   encountered — Hall et al.'s MATLAB code and the `cjbarrie/AI-norms` code that Barrie & Törnberg
   link to — and neither was run, cloned or installed.

### ⚠ A methodological mistake I made, recorded because it affects trust in the rest

Three times I **guessed an identifier** rather than looking it up, and each time I got the wrong paper:
a guessed arXiv ID for Bouzat & Kuperman returned a differential-geometry paper; a guessed arXiv ID for
Johora & Müller returned a face-recognition paper; and a guessed PMC ID for Centola & Baronchelli
returned a phylogenomics paper. **All three were caught by checking the first page of the downloaded
text against the expected title**, and the wrong files were deleted. The correct identifiers were then
obtained from search or from the Europe PMC API (`refs/gt_centola2015_pmc.*` is the correct
PMC4343158). No wrong-paper content reached any deliverable. Recording it because the same check
should be applied to anything I add later, and because it is the reason every entry in this review
names the exact cache file it was read from.

---

## 3. Published versions located for all five arXiv seeds

The issue's sourcing rules require checking whether a published version exists and preferring it.
**All five arXiv seeds turned out to be published.**

| Issue's seed | Published version found | Cited version |
|---|---|---|
| `arXiv:1802.08298` | **J. R. Soc. Interface 15(140):20170835 (2018)**, doi:10.1098/rsif.2017.0835 — open access via PMC5908527 | **Published** (read in full) |
| `arXiv:1702.03969` | **Sci. Rep. 7:4800 (2017)**, doi:10.1038/s41598-017-04284-6 — open access | **Published** (read via preprint; caveat stated) |
| `arXiv:1907.02160` | **J. Theor. Biol. 493:110101 (2020)**, doi:10.1016/j.jtbi.2019.110101 | **Published** (read via preprint; caveat stated) |
| `arXiv:2201.08592` | **Phys. Rev. E 107:024612 (2023)**, doi:10.1103/PhysRevE.107.024612 | **Published** (read via preprint; caveat stated) |
| `arXiv:2003.11959` | **IEEE T-ITS 22(9):5453–5472 (2021)**, doi:10.1109/TITS.2020.3006767 | **Published** (accepted manuscript read in full) |

The issue's ResearchGate seed link was also resolved to its published version, as instructed:
"Game theory in models of pedestrian room evacuation" → **Phys. Rev. E 89:032806 (2014)**,
doi:10.1103/PhysRevE.89.032806, preprint `arXiv:1311.1708`.

**Two G5 documents have NO published version** and are cited as preprints, stated in their entries:
Barrie & Törnberg (`arXiv:2505.23796`) and Ashery et al.'s reply (`arXiv:2506.18600`).

### ⚠ Citation error found in the issue's top-priority seed

[Foley-ConflictConvention] cites Maynard Smith & Parker (1976) in its reference list as
*"The logic of asymmetric animal contests. **Nature, 146**:15–18, 1976"*. That conflates it with
Maynard Smith & Price (1973), *Nature* **246**:15–18. The correct record, verified independently from
Crossref, is *Animal Behaviour* **24**(1):159–175, doi:10.1016/S0003-3472(76)80110-8. Recorded because
it is a concrete demonstration of why the issue forbids citing from another paper's reference list —
had I trusted the seed, the FYP's bibliography would have carried a fabricated-looking citation into
the report.

---

## 4. Every `[secondhand]` seed: verified, or reported as not found

The issue requires each `[secondhand]` seed to be "opened and confirmed, or reported as not found".
**All 12 were confirmed to exist. None was "not found". But existence is not the same as access, and
7 could not be opened.**

| Seed (issue's wording) | Confirmed record | Opened? |
|---|---|---|
| Maynard Smith & Price, "The logic of animal conflict" | *Nature* **246**:15–18 (1973), doi:10.1038/246015a0 | ❌ paywall |
| Maynard Smith & Parker (1976), "The logic of asymmetric contests" | *Animal Behaviour* **24**:159–175, doi:10.1016/S0003-3472(76)80110-8 | ❌ paywall |
| Schelling, focal points / tacit coordination | *The Strategy of Conflict* (HUP, 1960), confirmed via indexed reviews (doi:10.2307/2550465, doi:10.2307/1910005); **plus** the journal precursor, *J. Conflict Resolution* **2**(3):203–264 (1958), doi:10.1177/002200275800200301 | ❌ neither opened |
| Aumann, correlated equilibrium | *J. Math. Econ.* **1**(1):67–96 (1974), doi:10.1016/0304-4068(74)90037-8; **and** *Econometrica* **55**(1) (1987), doi:10.2307/1911154 | ❌ paywall |
| Shoham & Tennenholtz, social laws | *Artif. Intell.* **73**:231–252 (1995), doi:10.1016/0004-3702(94)00007-N | ❌ paywall — **but the AAAI-92 conference version WAS opened and read in full**, see [G2](g2-norm-emergence.md) |
| Lewis, *Convention: A Philosophical Study* | Harvard UP (1969); Blackwell reissue doi:10.1002/9780470693711; review doi:10.2307/2218418 | ❌ printed book |
| Farrell & Rabin, "Cheap Talk" | *J. Econ. Perspectives* **10**(3):103–118 (1996), doi:10.1257/jep.10.3.103 | ⚠ **abstract only** — AEA's page advertises a complimentary PDF, but every route returned an HTML challenge or **HTTP 403** |
| Crawford & Sobel (1982), "Strategic Information Transmission" | *Econometrica* **50**(6):1431–1451, doi:10.2307/1913390. ⚠ **A 2021 corrigendum exists**: Kono & Kandori, *Econometrica* **89**(1):1–10, doi:10.3982/ECTA17617 | ❌ paywall |
| The Science Advances paper | *Sci. Adv.* **11**(20):eadu9368, doi:10.1126/sciadv.adu9368 | ✅ **full text**, OA copy |
| The data-leakage critique | `arXiv:2505.23796` (preprint) | ✅ **full text** |
| The authors' reply | `arXiv:2506.18600` (preprint) | ✅ **full text** |
| "Game theory in models of pedestrian room evacuation" (RG link) | *Phys. Rev. E* **89**:032806 (2014) | ✅ **full text via preprint** |

**Additional leads mined from the T-ITS survey, as the issue instructed, each independently confirmed
via Crossref:**

| Lead | Record | Opened? |
|---|---|---|
| Fox et al., sequential chicken | VEHITS 2018, pp. 431–439, doi:10.5220/0006765404310439 | ✅ **full text** (SciTePress, open) |
| Johora & Müller, Stackelberg pedestrian model | IEEE ITSC 2018, pp. 3568–3574, doi:10.1109/ITSC.2018.8569687 | ❌ IEEE paywall; no author copy found |
| Camara et al., empirical fit to human lab experiments | *Proc. Measuring Behavior* 2018 (survey ref [41]) | ❌ not obtained |
| Camara et al., pedestrian preferences | *Proc. IEEE/RSJ IROS Workshops* 2018 (survey ref [34]) | ❌ not obtained |
| Camara et al., continuous game theory pedestrian model | *Human Factors in Intelligent Vehicles* 2022, doi:10.1201/9781003338475-1 | ❌ not obtained |
| Shi, Zhang & Wang, evacuation game theory | *J. Stat. Mech.* 2017:043407, doi:10.1088/1742-5468/aa68b3 | ❌ paywall — **dropped**, since Bouzat & Kuperman already covers this ground and was read in full |

---

## 5. Searches run

Queries were taken from the issue's suggested list and extended. Run via web search plus direct
Crossref bibliographic queries (two batches, cached).

- `correlated equilibrium convention coordination` → led to Foley 2018 and, through its reference
  list, to Vanderschraaf 1995, Young 1993, Duffy & Feltovich 2010 and Mesterton-Gibbons 2014
- `uncorrelated asymmetry bourgeois strategy contest` → Maynard Smith & Parker record; no openable
  primary text
- `focal point tacit coordination experiment` → Schelling records only
- `social norm emergence multi-agent systems` → Morris-Martin et al. 2019 (open access, read in full);
  Shoham & Tennenholtz records
- `cheap talk coordination game experiment` → Farrell & Rabin, Crawford & Sobel, Charness 2000,
  Cooper et al. 1992 records; Ganguly & Ray 2023 (open access, read in full)
- `game theoretic pedestrian conflict model` / `mean field game crowd dynamics` → Bonnemain 2023,
  Bouzat & Kuperman 2014, the T-ITS survey
- `LLM agents game theory equilibrium` → the G5 trio; also Cross et al. 2025 and Horiguchi et al. 2024
- `convention transfer across games spillover` → the G6 spillover literature (mostly paywalled, listed
  in [G6](g6-transfer-across-games.md) §3) and Rossetti et al. 2025 (open access, read in full)
- Additional, not in the issue's list: `spontaneous emergence of conventions experiment` → Centola &
  Baronchelli 2015 (read in full) and Centola et al. 2018 *Science* "Experimental evidence for tipping
  points in social convention" (doi:10.1126/science.aas8827, **confirmed, not opened** — it is the
  human 25% critical-mass study that [Ashery-EmergentConventions] benchmarks against, and is a
  recommended acquisition)

---

## 6. Deliberate exclusions (applying the issue's selection criterion)

The criterion: a paper qualifies only if it yields (a) a rule precise enough to be a runtime decision
function, or (b) evidence about when such a rule does or does not work.

- **Trajectory-prediction models requiring known goal locations** — excluded on the survey's own
  account: they "require each pedestrian's final goal location to be known in advance to form the cost
  matrix — which is only obtainable by looking ahead in the data to see what happened post hoc"
  ([Camara-PedestrianModelsII] §IV-A). Post-hoc descriptive models cannot be runtime rules.
- **Higher-order recursive belief models** — excluded on the survey's own account: they lead to "an
  infinite computational regress" (§IV-A).
- **`arXiv:2304.05763` ("Learning coordination through new actions")** — surfaced in a cheap-talk
  search and opened at abstract level. **Excluded**: it is about adding an unused third action, not
  about communication, and offers no evidence about communication-free rules.
- **Charness & Grosskopf (2001)** — read in full but it is an **unpublished working paper**; retained
  in [G3](g3-cheap-talk.md) as a lead with its template fields deliberately left blank rather than
  filling a review with unreviewed numbers. Yang (2016), also a working paper, excluded for the same
  reason.
- **Shi, Zhang & Wang (2017)** — confirmed, paywalled, and redundant given Bouzat & Kuperman. Dropped
  rather than padding G4.

**No sub-area was padded.** G6 is reported as thin, with one qualifying entry, exactly as the issue
permitted.

---

## 7. Where each sub-area landed against the issue's ≥2 requirement

| Sub-area | Fully read | Other | ≥2 met? |
|---|---|---|---|
| **G1** | 3 (Foley 2018, Chen 2017, Hall 2020) | 1 abstract-level (Duffy & Feltovich 2010) + 6 bibliographic-only | ✅ |
| **G2** | 3 (Shoham & Tennenholtz 1992, Centola & Baronchelli 2015, Morris-Martin 2019) | 2 bibliographic-only (Lewis, Young) | ✅ |
| **G3** | 2 (Ganguly & Ray 2023; Charness & Grosskopf 2001 — **unpublished**) | 1 abstract-only (Farrell & Rabin) + 1 bibliographic-only (Crawford & Sobel) | ⚠ **met on the letter, weak in substance** — see below |
| **G4** | 4 (Bonnemain 2023, Camara 2021, Fox 2018, Bouzat & Kuperman 2014) | 1 confirmed lead (Johora & Müller) | ✅ |
| **G5** | 3 (Ashery 2025, Barrie & Törnberg 2025, Ashery reply 2025) | — | ✅ all three required documents |
| **G6** | 2 (Rossetti 2025; Cross et al. 2025 — **preprint**, cross-filed) | 7 confirmed leads | ⚠ **thin, reported as such** (G6 is not in the issue's ≥2 list) |

### ⚠ G3 is the genuine shortfall — stating it plainly as the issue requires

Only **one** G3 entry is both peer-reviewed **and** read in full (Ganguly & Ray 2023). The named survey
(Farrell & Rabin) was reachable at abstract level only; one entry is fully read but unpublished; one is
bibliographic only. The sub-area's conclusion — that sequential communication does not support the
revealing equilibrium, so the FYP's LLM dialogue is a discovery device rather than a resolution
mechanism — therefore rests substantially on a **single paper**. It is a good paper (open access, IJGT,
2023, and its game is a genuine anti-coordination conflict game), and its two negative results are
stated in its own abstract, so the conclusion is soundly sourced. But it is **one** source, and the
report should say so. **Obtaining Farrell & Rabin (1996) and Charness (2000) through the university
library would move G3 from provisional to solid, and is the highest-value small task remaining.**

---

## 8. Connection noted, not pursued — the G5 leakage critique and unseen-scenario testing

The issue instructed: "sub-area G5 below covers a published critique that LLM 'emergent' behaviour may
be training-data recall, and testing on unseen or disguised scenarios is the control for that. **Note
the connection in `search-log.md` but do not expand this issue to cover it.**"

**Noted, and not expanded.** For the record, the connection is tighter than the issue's wording
suggests, in three specific ways, all sourced in [G5](g5-llm-agents-game-theory.md):

1. **Disguising the scenario is predicted not to work.** Barrie & Törnberg address the obvious control
   directly and reject it: "Modifying the model to hide the type of model through obfuscation — say,
   for instance, by using unicode characters as tokens — **is unlikely to prevent the LLM from
   recognizing the general structure of the game** with sufficient certainty" (p. 5). Their own
   proposed remedy is much more demanding: "'invent' some completely novel game that the LLM has
   definitely not seen before". Whoever picks up the unseen-scenario issue should start from that
   sentence, because it means *relabelling* the FYP's scenarios will not be a sufficient control.
2. **The probe itself is cheap and directly reusable.** Their method is three appended meta-prompt
   questions, ten repeats, across 14 models (p. 3, footnote 2). **`deepseek-r1:8b` is in that list** —
   a sibling of the model this project uses. Running the equivalent probe on the FYP's own scenarios
   would cost a handful of API calls against `ALREADY_SPENT_USD`.
3. **There is a published methodology for the stronger control.** [Cross-ValidatingGABM] (`arXiv:2507.22049`,
   preprint, read in full) gives a two-stage design — replicate a known human result, then generate and
   test a **novel** prediction — on the grounds that a prediction absent from the literature cannot be
   recall. Cross et al. concede they have not closed their own loop ("the empirical testing of our
   novel predictions with human participants… would provide strong evidence of generalization",
   Discussion), which is itself worth knowing before the FYP commits to that design.

**No scenario design, prompt, or experiment was produced in this issue.**

---

## 9. Acquisition list, in priority order

> ### ✅ UPDATE 2026-10-02 — three items acquired, two reported unobtainable
> The user supplied PDFs for **items 3, 5 and 6** below. All three have been **read in full**, cached
> under `refs/`, and written up in
> [`conflict-avoidance-shortlist.md`](conflict-avoidance-shortlist.md); the corresponding entries in
> [`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md) and
> [`g4-game-theoretic-crowd-models.md`](g4-game-theoretic-crowd-models.md) have been upgraded from
> "abstract only" / "not opened" to full text.
>
> | # | Item | Status |
> |---|---|---|
> | 3 | Farrell & Rabin (1996), JEP | ❌ **still not obtained** |
> | 5 | Maynard Smith & Parker (1976), *Animal Behaviour* | ❌ **reported unobtainable by the user** |
> | 6 | Johora & Müller (2018), IEEE ITSC | ✅ **obtained and read in full** |
> | 7 | Mesterton-Gibbons et al. (2014), *Dyn. Games Appl.* | ❌ **reported unobtainable by the user** |
> | — | Camara et al. (2018), *Proc. Measuring Behavior* (was listed under G4 leads) | ✅ **obtained and read in full** |
> | — | Duffy & Feltovich (2010), *Int. Econ. Rev.* (was abstract-only) | ✅ **obtained and read in full** |
>
> ⚠ **The two that remain unobtainable both bear on the same open question** — whether an
> **arrival-order / prior-possession** rule exists in this literature (risk R6 below). Maynard Smith
> & Parker is the origin of the uncorrelated-asymmetry idea, and Mesterton-Gibbons et al. is about
> bourgeois under *ownership uncertainty*. Until one of them is read, this review's negative finding
> stands as **"no arrival-order rule was found in anything opened"**, not as "none exists".

Everything below is confirmed to exist. This is the shopping list for the university library.

1. **Vanderschraaf (1995), "Convention as correlated equilibrium"**, *Erkenntnis* 42:65–87 — closes
   the framing check in §0.
2. **Aumann (1987)**, *Econometrica* 55(1) — the formal definition of correlated equilibrium **with
   its information assumptions**, which this review does not have.
3. **Farrell & Rabin (1996)**, JEP 10(3):103–118 — fixes the G3 shortfall.
4. **`arXiv:2409.00993`** (Horiguchi, Yoshida & Ikegami, "Evolution of Social Norms in LLM Agents
   using Natural Language") — **possible prior art for the FYP's own method** (LLM agents deriving
   norms through dialogue, 2024). Needs a novelty check of the kind issue #16 ran. Freely available;
   only its first page was read here.
5. **Maynard Smith & Parker (1976)**, *Animal Behaviour* 24:159–175 — the uncorrelated-asymmetry
   formulation, and the most likely home of an arrival-order / prior-possession rule, which the
   [rule catalogue](candidate-rule-catalogue.md) §4 records as **absent** from everything read.
6. **Johora & Müller (2018)**, IEEE ITSC — the Stackelberg rule's discrete action set.
7. **Mesterton-Gibbons, Karabiyik & Sherratt (2014)**, *Dyn. Games Appl.* 4:407–431 — bourgeois under
   **ownership uncertainty**, i.e. what happens when the simulator cannot tell who arrived first.
8. **Centola et al. (2018)**, *Science* 360:1116–1119 — the human 25% critical-mass study that
   [Ashery-EmergentConventions] benchmarks against.
9. **Charness (2000)**, *Games Econ. Behav.* 33:177–194 — a published test of Aumann's conjecture,
   replacing the working paper currently in G3.
10. Lewis (1969), Schelling (1960 or the 1958 JCR article), Crawford & Sobel (1982) **and its 2021
    corrigendum**, Young (1993) — the remaining `[foundational]` primary texts.

---

## 10. Open questions and risks

- **R1. Seven of the review's cited works were never opened**, including four of the `[foundational]`
  definitions the issue asked to have recorded. Every affected entry says so, and no definition is
  asserted without a locator into something I read. But the report must not quote Aumann, Schelling,
  Lewis or Maynard Smith & Parker until §9 items are obtained.
- **R2. Four entries were read as preprints, not published versions** (Chen, Hall, Bonnemain, Bouzat &
  Kuperman). Section and equation numbers may have changed. Each entry carries the warning.
- **R3. The framing check came back partly negative.** The standard equivalence-based definitions of
  *convention* do not fit the FYP's scenarios (§0). This changes how the report should word its
  contribution and needs supervisor sign-off.
- **R4. Possible prior art.** `arXiv:2409.00993` is LLM agents deriving norms through dialogue, in
  2024. Until it is read, the FYP's novelty claim is unverified. This is the risk with the largest
  downside.
- **R5. The FYP is more exposed to the leakage critique than Ashery et al. are**, by the defenders'
  own argument: their defence is that a naming game has no right answer, and the FYP's scenarios do
  ([G5](g5-llm-agents-game-theory.md) §4). A reframing is proposed there; it needs sign-off.
- **R6. No arrival-order rule was found anywhere.** The intuitive "whoever arrived first passes first"
  convention does not appear in any paper read, and Foley et al.'s result points the *other* way — the
  host–guest norm, where the one already there concedes, "evolves far more readily" (§4). Either the
  rule lives in an unobtained source (§9 items 5 and 7), or this is a real gap in the literature and a
  possible contribution.

---

**Draft status:** this file and all six sub-area files are **drafts pending supervisor review**.
