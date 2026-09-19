# How humans resolve conflicts through talk — codeable strategies

Prepared for issue [#12](https://github.com/M450NCH00/CrowdSimulation/issues/12).
Companion files: [`candidate-coding-scheme.md`](candidate-coding-scheme.md),
[`modality-note.md`](modality-note.md), [`search-log.md`](search-log.md),
[`refs.bib`](refs.bib).

**Purpose.** Supply categories that an LLM-to-LLM conflict transcript can be *coded
against*, so the project can ask: is the strategy these two agents used one that real
people actually use, and do they use it as often as people do?

**Inclusion test (the issue's).** A paper is listed only if it yields something a
transcript can be coded against — named resolution strategies, a coding scheme, a
termination-format classification, or an empirically derived sequence pattern. Papers
that only describe conflict as a phenomenon are excluded and recorded in
[`search-log.md`](search-log.md).

## How to read the verification lines

Every entry states the route by which it was confirmed. Publishers blocked automated
access to most full texts (John Benjamins, Taylor & Francis, SAGE, Wiley, Elsevier,
JSTOR — all logged in `search-log.md`), so several entries are **abstract-level**. That
is stated in the entry, and any category or number that could not be traced to a primary
source is marked `[needs verification against full text]`. Caches are in
[`../../refs/`](../../refs/).

Entries are tagged `[foundational]` where they predate the issue's 2016–2026 window,
each with a justification.

## Summary table

| # | Handle | Year | Sub-area | Codeable output | Frequency data | IRR | Verified from |
|---|--------|------|----------|-----------------|----------------|-----|---------------|
| 1 | Rahim — ROCI-II five styles `[foundational]` | 1983 | A1 | 5 conflict-handling styles | none reported | none reported (reliability = α / test–retest) | abstract record |
| 2 | Rahim & Magner — CFA `[foundational]` | 1995 | A1 | same 5 styles, defined | none reported | α .72–.76 / .65–.80; test–retest .60–.83 | **full text** |
| 3 | Weider-Hatfield — ROCI-II critique `[foundational]` | 1988 | A1 | argues 3, not 5, styles | none reported | none reported | abstract record |
| 4 | Pütz & Hassan — conflict termination | 2024 | A2 | 3 termination formats | **yes** (rank order; counts unverified) | none reported | abstract record |
| 5 | Toluei & Tahririan — closing disagreements | 2022 | A2 | 2 closure acts + non-resolution conditions | none reported | none reported | abstract record |
| 6 | Dersley & Wootton — complaint sequences `[foundational]` | 2000 | A2 | 2 denial types | "predominantly" denials | none reported | abstract record |
| 7 | Sillars et al. — VTCS `[foundational]` | 1982 | A3 | 3 verbal tactic classes | none reported | none reported in abstract | abstract page |
| 8 | Garcia — mediation minimises argument `[foundational]` | 1991 | A4 | positional constraints on accusation/denial | none reported | none reported | abstract record |
| 9 | Garcia — strategic interruptions | 2025 | A4 | mediator strategic interruption | **yes** (136 in 23 sessions) | none reported | abstract record |
| 10 | Hale et al. — KODIS corpus | 2025 | A4 | outcome: agreement vs impasse | **yes** (~18% impasse) | not for outcomes | **full text** |
| 11 | Hila & Hauser — LLM deductive coding | 2025 | A5 | (method) | n/a | κ = .744, α = .746 | **full text (abstract page)** |
| 12 | Borse et al. — LLM vs human raters | 2025 | A5 | (method) | n/a | κ > .6 (3 themes), moderate (1) | **full text (abstract page)** |

Sub-areas A1–A4 each have at least one entry. A5 has two and is kept short, as the issue
asks. **Not listed, and why:** the Conversational Argument Coding Scheme (categories
could not be opened), Pomerantz 1984, and Rees-Miller 2000 — see `search-log.md`.

---

## A1. Conflict-style taxonomies

### [Rahim-1983] — A Measure of Styles of Handling Interpersonal Conflict `[foundational]`

**Authors / Year / Venue:** M. Afzalur Rahim / 1983 / *Academy of Management Journal*
26(2):368–376.
**Link:** doi:10.2307/255985
**Verified:** yes — Crossref record (`refs/cr_*.json`) and OpenAlex record
(`refs/oa_rahim1983.json`) opened; title, author, year, journal, volume, issue and pages
confirmed. The publisher page itself was not reachable (JSTOR/AOM block automated
access). **Abstract-level only.**
**Sub-area:** A1
**Tags:** `[foundational]` — this is the origin article for the five-style taxonomy that
later work (including entries 2 and 3) is built on and argues with. No post-2016 paper
replaces it as the source of the taxonomy; entry 2 is the in-depth psychometric follow-up
and entry 3 the critique.

**The codeable scheme it provides:** five styles of handling interpersonal conflict.
The 1983 abstract states only that "five factorially independent and reliable scales for
conflict styles" were constructed; **it does not name them on the abstract page**. The
names and definitions used in this review are taken from entry 2, which is by the same
lead author and was read in full: **integrating, obliging, dominating, avoiding,
compromising**, arranged on two dimensions, *concern for self* × *concern for others*
(Rahim & Magner 1995, pp. 122–123, Figure 1).

**Frequency data:** none reported — the article is about instrument construction, not
about how often each style occurs.

**Inter-rater reliability:** none reported, and **not applicable in the usual sense**:
ROCI-II is a self-report questionnaire, not a transcript coding scheme, so its
reliability is internal consistency and test–retest (see entry 2), not agreement between
coders.

**Empirical basis:** seven non-random samples used for item generation and selection,
with a national sample of managers used for the final factor analysis (n = 1,219, per
entry 2, p. 123). Participants rate statements about themselves; no interaction is
observed.

**How an LLM transcript would be coded against it:** the five styles can be used as
labels for what an agent *does* in the exchange — e.g. an agent that proposes a solution
meeting both agents' stated needs → integrating; an agent that concedes and emphasises
the other's need → obliging; an agent that insists on its own passage and refuses
alternatives → dominating; an agent that changes the subject or declines to engage →
avoiding; an agent that proposes splitting the difference (e.g. alternating who passes
first) → compromising.

**What it cannot validate:** anything about *sequence* (who moves first, how many turns),
and anything about frequency, since no base rates are reported. Crucially, the taxonomy
was validated as a measure of self-reported disposition, not as a scheme for coding
observed talk — using it on transcripts is an extension the report must defend, not an
established use.

**Limitations stated by the authors themselves:** `[needs verification against full
text]` — not obtainable from the abstract record.

**BibTeX:** `rahim1983measure`.

### [RahimMagner-1995] — Confirmatory Factor Analysis of the Styles of Handling Interpersonal Conflict `[foundational]`

**Authors / Year / Venue:** M. Afzalur Rahim, Nace R. Magner / 1995 / *Journal of Applied
Psychology* 80(1):122–132.
**Link:** doi:10.1037/0021-9010.80.1.122 (PDF cached at `refs/rahim_magner_cfa.pdf`,
text at `refs/rahim_magner_cfa.txt`)
**Verified:** yes — **full text read**, obtained as a PDF and text-extracted locally.
**Sub-area:** A1
**Tags:** `[foundational]` — retained because it is the source of the five-style
definitions used here and of the psychometric figures; no post-2016 replacement was
found that defines the styles from the original authors.

**The codeable scheme it provides:** the five styles, each defined on the two dimensions
(pp. 122–123, Figure 1):
- **Integrating** — "high concern for self as well as the other party … concerned with
  collaboration between parties (i.e., openness, exchange of information, and examination
  of differences) to reach a solution acceptable to both parties."
- **Obliging** — "low concern for self and high concern for the other party … attempts to
  play down the differences and emphasizes commonalities to satisfy the concerns of the
  other party."
- **Dominating** — "high concern for self and low concern for the other party …
  identified with a win-lose orientation or with forcing behavior to win one's position."
- **Avoiding** — "low concern for self as well as for the other party … associated with
  withdrawal, passing-the-buck, sidestepping."
- **Compromising** — "moderate concern for self as well as the other party … associated
  with give-and-take or sharing whereby both parties give up something to make a mutually
  acceptable decision."

The same pages record **competing taxonomies**, which matters for the coding scheme
draft: two styles (cooperation, competition — Deutsch); three (nonconfrontation,
solution-orientation, control — Putnam & Wilson 1982); four (yielding, problem solving,
inaction, contending — Pruitt 1983); and Hocker & Wilmot's three-type clustering
"(1) avoidance, (2) competitive (distributive) and (3) collaborative (integrative)"
(p. 123).

**Frequency data:** none reported — the paper tests factor structure, not prevalence.

**Inter-rater reliability:** none (self-report instrument). The reliabilities it reports,
as Rahim's earlier findings: **test–retest .60–.83** (collegiate sample, n = 119,
one-week interval) and **Cronbach's α .72–.76 (managerial) and .65–.80 (collegiate)**
(p. 123).

**Empirical basis:** confirmatory factor analysis of ROCI-II's 28 items across **five
samples** — 484 management students, 550 public administrators, 214 university
administrators, 250 bank managers/employees in Bangladesh, 578 managers/employees
(abstract, p. 122).

**How an LLM transcript would be coded against it:** as entry 1, but with usable
definitions: each agent's turn, or its overall stance in the exchange, is assigned the
style whose concern-for-self / concern-for-other profile it matches.

**What it cannot validate:** it says nothing about talk. Every sample rated
questionnaire items; no conversation was coded.

**Limitations stated by the authors themselves:** the paper reports "general support for
the invariance of the 5-factor model … and **4 of the 5 samples**" (abstract) — i.e. one
sample did not fit. It also reproduces Weider-Hatfield's conclusion against the five-style
paradigm (p. 123, quoted in entry 3).

**BibTeX:** `rahim1995confirmatory`.

### [WeiderHatfield-1988] — Assessing the Rahim Organizational Conflict Inventory-II (ROCI-II) `[foundational]`

**Authors / Year / Venue:** Deborah Weider-Hatfield / 1988 / *Management Communication
Quarterly* 1(3):350–366.
**Link:** doi:10.1177/0893318988001003005
**Verified:** yes — Crossref record with full publisher abstract
(`refs/cr_10_1177_0893318988001003005.json`) and OpenAlex record opened. SAGE blocks
automated access to the article page. **Abstract-level only.**
**Sub-area:** A1
**Tags:** `[foundational]` — it is the critique of the instrument this review uses; the
issue names it for exactly that purpose.

**The codeable scheme it provides:** none of its own. It is included because it
constrains how entries 1 and 2 may be used: it "commends the internal reliabilities of
the scale but **questions the factor structure of the items**" and "calls for research on
the predictive validity of the instrument" (abstract).

**Frequency data:** none reported.
**Inter-rater reliability:** none reported.

**Empirical basis:** a review and reassessment of the instrument, not new interaction
data. `[needs verification against full text]` for the exact analyses.

**How an LLM transcript would be coded against it:** not directly. Its use is to force a
statement in the report that the five-style taxonomy's dimensionality is contested, so
that coding an LLM transcript into five styles is presented as a choice, not a settled
standard.

**What it cannot validate:** anything, by itself.

**Limitations stated by the authors themselves:** the conclusion most relevant here is
quoted by Rahim & Magner (1995, p. 123): "although the conflict literature has
historically embraced the 'five-style' paradigm, recent evidence indicates that
individuals might select among **three, not five**, distinct conflict styles" (p. 364).
⚠ **That quotation was read in Rahim & Magner's paper, not in Weider-Hatfield's own
text.** It must be checked against the original before the report quotes it.

**BibTeX:** `weiderhatfield1988assessing`.

---

## A2. Conversation analysis of disagreement

### [Putz-Hassan-2024] — The quick termination of verbal conflicts expressed through disagreement: Three patterns of conflict minimization during computer science project meetings

**Authors / Year / Venue:** Ole Pütz, Hafsa Hassan / 2024 / *Journal of Language
Aggression and Conflict* 14(2):199–228.
**Link:** doi:10.1075/jlac.00112.put
**Verified:** yes — Crossref record with the publisher abstract
(`refs/cr_10_1075_jlac_00112_put.json`) and the Semantic Scholar record
(`refs/s2_10_1075_jlac_00112_put.json`) opened. John Benjamins returned HTTP 403 to
automated fetches of both the journal page and the catalogue page. **Abstract-level
only.**
⚠ **Correction to the issue's seed:** the issue lists this as "Pütz, O." The paper has
**two authors — Pütz and Hassan** — and was published in **2024**, in volume 14(2).

**Sub-area:** A2 (in-window; the closest fit in this review to the project's setting)

**The codeable scheme it provides:** **three conflict termination formats** —
**submission**, **stand-off**, and **compromise** (abstract). Conflict itself is defined
operationally as **continued disagreement**, which gives a usable threshold for deciding
when an exchange counts as a conflict at all. The paper also analyses **episode length**
(number of disagreements) and **disagreement mitigation** as indicators of severity, and
its subtitle promises **three patterns of conflict minimization**.
`[needs verification against full text]` — the three minimization patterns are named in
the subtitle but not enumerated in the abstract.

**Frequency data:** **yes, in rank order** — "most conflicts end after two or three
disagreements", and "among the termination formats, **submission is the most frequent,
followed by stand-off and compromise**" (abstract). Exact counts, percentages and the
table they come from are `[needs verification against full text]`.

**Inter-rater reliability:** none reported in the abstract. Conversation-analytic work
of this kind typically does not report kappa; confirm against the full text before the
report claims either way.

**Empirical basis:** a corpus of **meetings in which computer scientists discuss the
progress of projects they are working on** (abstract). Number of meetings, hours and
number of conflict episodes are `[needs verification against full text]`. The setting is
task-focused discussion among peers — the closest analogue in this review to two LLM
agents negotiating a shared problem.

**How an LLM transcript would be coded against it:** first decide whether a conflict
exists at all (is there *continued* disagreement, i.e. a disagreement pursued past the
first turn?). If yes, code the ending: one agent drops its position and the other's
stands → **submission**; neither concedes and the exchange stops with both positions
intact → **stand-off**; both give something up and a joint position is reached →
**compromise**. Episode length is countable directly: how many disagreement turns before
termination. The project's own transcripts can then be compared with "most end after two
or three disagreements" and with the submission > stand-off > compromise ordering.

**What it cannot validate:** whether a resolution is *correct* or fair; the paper
describes how conflicts end, not whether the ending was good. It is also workplace talk
among colleagues with ongoing relationships and power differences (the abstract notes
power relations are discussed), none of which a two-agent hallway exchange has.

**Limitations stated by the authors themselves:** `[needs verification against full
text]`.

**BibTeX:** `putz2024quick`.

### [Toluei-Tahririan-2022] — Resolving disagreements: a conversation analytic study on disagreements in completion sequences among EFL learners

**Authors / Year / Venue:** Bahareh Toluei, Mohammad Hassan Tahririan / 2022 (issue dated
2023) / *The Language Learning Journal* 51(6):718–733.
**Link:** doi:10.1080/09571736.2022.2061580
**Verified:** yes — Crossref record and the Semantic Scholar record carrying the full
publisher abstract (`refs/s2_10_1080_09571736_2022_2061580.json`) opened. Taylor &
Francis returned HTTP 403. **Abstract-level only.**
**Sub-area:** A2

**The codeable scheme it provides:** **acts that close a disagreement sequence** —
(a) **relinquishing a position** by accepting the position maintained by another, and
(b) **acknowledging the repair** performed by another party (abstract). The study is
explicitly organised around patterns that **do and do not** bring disagreements to a
close, so it also supplies the **non-resolution** side the issue asks for; the exact
non-resolution conditions are `[needs verification against full text]` (the abstract
retrieved is truncated at that sentence).

**Frequency data:** none reported in the abstract.

**Inter-rater reliability:** none reported in the abstract.

**Empirical basis:** **50 hours of interaction**, from **20 video-recorded English
discussion task sessions** collected over **10 weeks**, with **15 Farsi-speaking advanced
EFL students** working in **groups of three** (abstract).

**How an LLM transcript would be coded against it:** at the end of a disagreement
sequence, ask what closed it. If one agent explicitly accepts the other's position
("alright, you go first") → **relinquishing a position**. If the closure follows one
agent correcting a misunderstanding and the other accepting the correction ("oh, you're
carrying something — go ahead") → **acknowledging repair**. If neither occurs and the
sequence lapses → code as non-resolution.

**What it cannot validate:** the speakers are language learners in a classroom task, so
disfluency, teacher authority and L2 proficiency shape the talk in ways that do not
transfer. The disagreements arise in *completion sequences* (one speaker completing
another's turn), a narrower environment than a general standoff.

**Limitations stated by the authors themselves:** `[needs verification against full
text]`.

**BibTeX:** `toluei2022resolving`.

### [Dersley-Wootton-2000] — Complaint Sequences Within Antagonistic Argument `[foundational]`

**Authors / Year / Venue:** Ian Dersley, Anthony Wootton / 2000 / *Research on Language &
Social Interaction* 33(4):375–406.
**Link:** doi:10.1207/s15327973rlsi3304_02
**Verified:** yes — Crossref record and OpenAlex record with the full abstract
(`refs/oa_dersley2000.json`) opened. Taylor & Francis blocks the article page.
**Abstract-level only.** This was a `[secondhand]` seed in the issue and is now
independently confirmed.
**Sub-area:** A2
**Tags:** `[foundational]` — it is the canonical account of what immediately follows a
complaint in hostile argument; entries 4 and 5 cover the in-window CA work.

**The codeable scheme it provides:** a classification of **initial replies to
complaints/accusations**, which "predominantly consist of denials, which are made up of
2 main types — **'didn't do it'** and **'not at fault'** denials" (abstract). The paper
also addresses **whether the preference for agreement is reversed within argument
sequences** — relevant because it bears on whether LLM agents' habitual agreeableness is
humanlike in a dispute.

**Frequency data:** qualitative only — "predominantly" denials, and the abstract refers
to the "shape and **distribution**" of the two denial types, but gives no numbers.
`[needs verification against full text]`.

**Inter-rater reliability:** none reported (conversation analysis; single-case sequential
analysis rather than coded counts).

**Empirical basis:** "a corpus of audio and audiovisual recordings of people engaged in
acrimonious argument, in which complaints and accusations are being made about the
behavior of copresent parties" (abstract). Corpus size is `[needs verification against
full text]`.

**How an LLM transcript would be coded against it:** where one agent blames the other
("you should have waited"), code the reply: denial of the act → **"didn't do it"**;
accepting the act but rejecting blame ("I was already through the doorway") → **"not at
fault"**; anything else (apology, counter-complaint, concession) falls outside the two
types and is evidence that LLM agents respond to blame differently from people in
acrimonious argument.

**What it cannot validate:** resolution. The paper is about how antagonistic sequences
*continue*, not how they end.

**Limitations stated by the authors themselves:** `[needs verification against full
text]`.

**BibTeX:** `dersley2000complaint`.

---

## A3. Interaction coding schemes built for conflict talk

### [Sillars-1982] — Coding Verbal Conflict Tactics: Nonverbal and Perceptual Correlates of the "Avoidance-Distributive-Integrative" Distinction `[foundational]`

**Authors / Year / Venue:** Alan L. Sillars, Stephen F. Coletti, Doug Parry, Mark A.
Rogers / 1982 / *Human Communication Research* 9(1):83–95.
**Link:** doi:10.1111/j.1468-2958.1982.tb00685.x
**Verified:** yes — the Oxford Academic abstract page was opened and returned title,
full author list, year, journal, volume, issue, pages, DOI and abstract.
**Abstract-level only** (the full text is paywalled).
⚠ Crossref lists three authors; the publisher page lists **four** (Rogers included). The
publisher page is taken as correct.
**Sub-area:** A3
**Tags:** `[foundational]` — this is the validation article for the Verbal Tactics Coding
Scheme, a scheme built specifically to be applied to conflict transcripts. It remains in
use: Caughlin & Vangelisti (2006, section "Negativity and positivity") describe researchers
"using Sillars' (1986) Verbal Tactics Coding Scheme or similar measures" as standard
practice for separating integrative from distributive strategies.

**The codeable scheme it provides:** three classes of conflict statement —
**avoidance**, **integrative**, and **distributive**: "Coding procedures developed by
Sillars (1980a) classified statements made during interpersonal conflict into
'avoidance,' 'integrative,' and 'distributive' categories" (abstract). The **subcategory
list** (the individual tactics within each class) is in the VTCS manual — Sillars (1986),
*Procedures for coding interpersonal conflict: The Verbal Tactics Coding Scheme*,
University of Montana — which **could not be obtained**; see `search-log.md`. Any use of
the subcategories is therefore `[needs verification against full text]`.

**Frequency data:** none reported in the abstract.

**Inter-rater reliability:** none reported in the abstract. Since VTCS is a transcript
coding scheme, a published reliability figure very likely exists in the full text or the
manual; this is the single most valuable thing to retrieve for this project.

**Empirical basis:** two studies correlating coded verbal tactics with observer
perceptions of "disclosiveness and competitiveness" and with nonverbal behaviours
(abstract). Sample sizes are `[needs verification against full text]`.

**How an LLM transcript would be coded against it:** each utterance gets one of three
labels — refusing to engage, deflecting, or changing the subject → **avoidance**;
information exchange, proposing options, asking about the other's needs →
**integrative**; demands, threats, blame, insisting on one's own passage →
**distributive**. This is the most directly applicable scheme in the review, because it
was designed for utterance-level coding of conflict talk rather than for self-report.

**What it cannot validate:** outcomes. The scheme codes tactics, not how the conflict
ended, so it needs pairing with entry 4 (termination formats).

**Limitations stated by the authors themselves:** the abstract notes that much of the
verbal–nonverbal relationship found in study 2 "stemmed from the talkativeness of
integrative approaches" — i.e. the integrative category partly tracks how much a party
talks, a confound that matters directly for LLM agents, which are verbose by default.

**BibTeX:** `sillars1982coding`.

---

## A4. Dispute resolution / mediation interaction

### [Garcia-1991] — Dispute Resolution Without Disputing: How the Interactional Organization of Mediation Hearings Minimizes Argument `[foundational]`

**Authors / Year / Venue:** Angela Cristina Garcia / 1991 / *American Sociological Review*
56(6):818–835.
**Link:** doi:10.2307/2096258
**Verified:** yes — Crossref record and OpenAlex record with the full abstract
(`refs/oa_garcia1991.json`) opened. JSTOR blocks automated access to the article.
**Abstract-level only.**
⚠ **Correction to the issue's seed.** The issue lists this paper under "Greatbatch, D. &
Dingwall, R. (1991)". The title belongs to **Angela Cristina Garcia**, single-authored,
*ASR* 56(6), 1991. Greatbatch and Dingwall have a separate body of mediation work (e.g.
*Mediation Quarterly* 1998; a 2008 chapter), but not this paper. Details in
`search-log.md`.
**Sub-area:** A4
**Tags:** `[foundational]` — the canonical account of *why* mediated disputes produce
less argument; entry 9 is the in-window companion by the same author.

**The codeable scheme it provides:** not a category list but an **empirically derived
sequence pattern**: mediation "constrains **how accusations and denials are positioned
and formulated**", so disputing parties address the mediator rather than each other,
which removes the adjacency that makes an accusation require an immediate denial
(abstract). What can be coded from a transcript is therefore **who a turn is addressed
to** and **whether an accusation is adjacent to its denial**.

**Frequency data:** none reported in the abstract.
**Inter-rater reliability:** none reported (conversation analysis).

**Empirical basis:** mediation hearings; number of hearings is `[needs verification
against full text]`.

**How an LLM transcript would be coded against it:** mainly as a **contrast case**. Two
LLM agents talk directly to each other with no third party, so Garcia's mechanism
predicts *more* direct accusation–denial adjacency than in mediation. If the project
later adds a mediator agent, this is the paper that says what should change.

**What it cannot validate:** two-party unmediated conflict, which is the project's
scenario. Include it for the mediation contrast, not as a source of categories.

**Limitations stated by the authors themselves:** `[needs verification against full
text]`.

**BibTeX:** `garcia1991dispute`.

### [Garcia-2025] — Strategic Interruptions in Small Claims Mediation: How Precipitous Timing of Mediator Interventions Can Facilitate Conflict Resolution

**Authors / Year / Venue:** Angela Cora Garcia / 2025 / *Conflict Resolution Quarterly*
43(4):577–590.
**Link:** doi:10.1002/crq.70021
**Verified:** yes — Crossref record and OpenAlex record with the full abstract
(`refs/oa_garcia2025_crq.json`) opened. Wiley returned HTTP 403. **Abstract-level only.**
**Sub-area:** A4 (in-window)

**The codeable scheme it provides:** the category **"strategic interruption"** —
mediator interruptions "used strategically, to stop disputant actions which may be
counterproductive at that point or to further the mediator's work in assisting disputants
in resolving their dispute" (abstract), distinguished from interruptions that are
"impolite, oppressive, or intrusive". The sub-types of strategic interruption are
`[needs verification against full text]`.

**Frequency data:** **yes** — **136 strategic interruptions** identified across **23
mediation sessions** (abstract). No breakdown by type is available at abstract level.

**Inter-rater reliability:** none reported (conversation analysis).

**Empirical basis:** a previously collected data set of **23 mediation sessions** held in
the Midwest and West Coast regions of the United States (abstract).

**How an LLM transcript would be coded against it:** only if a third agent is added.
In a two-agent exchange the codeable residue is thin: whether either agent cuts the other
off, and whether that cut-off advances or blocks resolution.

**What it cannot validate:** two-party conflict resolution; this is about a third party's
technique.

**Limitations stated by the authors themselves:** `[needs verification against full
text]`.

**BibTeX:** `garcia2025strategic`.

### [KODIS-2025] — KODIS: A Multicultural Dispute Resolution Dialogue Corpus

**Authors / Year / Venue:** James Hale, Sushrita Rakshit, Kushal Chawla, Jeanne M. Brett,
Jonathan Gratch / 2025 / arXiv:2504.12723 `[non-archival]`.
**Link:** https://arxiv.org/abs/2504.12723 (PDF cached at `refs/kodis2025.pdf`, text at
`refs/kodis2025.txt`)
**Verified:** yes — **full text read**.
**Sub-area:** A4 (dispute interaction, text-based)

**The codeable scheme it provides:** at the level this project needs, a **binary outcome
coding — agreement vs impasse** — applied to dyadic disputes conducted in **text chat**,
plus per-turn **emotion labels** generated by GPT-4 and validated against participants'
own annotations (§"GPT4 Emotion Labelling"). The corpus is "a dyadic dispute resolution
corpus containing thousands of dialogues from over 75 countries", built around "a typical
customer service dispute designed by experts to evoke strong emotions and conflict"
(abstract).

**Frequency data:** **yes, and directly usable** — "about **18% of the KODIS dialogues
ended in an impasse**", against "only **3.5% of the CaSiNo dialogues**" (a deal-making
corpus). The paper's point is that disputes fail far more often than deal-making
negotiations, because "disputes are backward-looking", evoke stronger emotions and have
more entrenched positions (§1).

**Inter-rater reliability:** for outcomes, none is needed — agreement/impasse is recorded
by the task, not coded. For the emotion labels, the authors check construct validity of
GPT labels against participant self-annotation (Appendix A) but note they "do not have
independent human annotations" for some target cultures — a limitation they state
themselves.

**Empirical basis:** **4,061 participants** from **over 75 countries**, paired in dyads;
disputes conducted by **text chat**; rich dispositional, process and outcome measures.

**How an LLM transcript would be coded against it:** the cleanest comparison in this
review. Run the project's two-agent exchanges, record what fraction end without an
agreement, and compare against **~18%**. If LLM agents resolve essentially every conflict
(as GameChat's 100% consensus rate in the issue #8 review suggests they might), that is a
measurable divergence from human dyads in a comparable text-chat setting.

**What it cannot validate:** the dispute is a customer-service scenario with money at
stake and assigned roles, not a spatial standoff. Its participants are paid crowdworkers;
the authors note this "may shape their responses". And the outcome measure is coarse:
agreement vs impasse says nothing about *which strategy* produced the agreement.

**Limitations stated by the authors themselves:** participants "act as part of a paid
service, which may shape their responses in ways that do not match" real disputes;
anonymity during the interaction may shape behaviour; reliance on GPT labelling risks
"the illusion of objectivity"; and labelling schemes may carry constructs "labeled and
interpreted differently across cultures".

**BibTeX:** `hale2025kodis`.

---

## A5. LLM-assisted qualitative coding (secondary — method support only)

Kept short, as the issue instructs. These support *how* many transcripts could be coded;
they are not evidence about human behaviour, and using an LLM to code LLM output has an
obvious circularity that the report must address.

### [HilaHauser-2025] — Assessing the Reliability of Large Language Models for Deductive Qualitative Coding

**Authors / Year / Venue:** Angjelin Hila, Elliott Hauser / 2025 / arXiv:2507.14384
`[non-archival]`.
**Link:** https://arxiv.org/abs/2507.14384
**Verified:** yes — arXiv abstract page opened.
**Sub-area:** A5

**The codeable scheme it provides:** none of its own; it *applies* the Comparative
Agendas Project Master Codebook (21 policy domains) to U.S. Supreme Court case summaries
using four prompting strategies (zero-shot, few-shot, definition-based, Step-by-Step Task
Decomposition).

**Frequency data:** not applicable.

**Inter-rater reliability:** **yes, the headline result** — the decomposition strategy
reached **accuracy 0.775, Cohen's κ = 0.744, Krippendorff's α = 0.746**, which the authors
describe as reaching thresholds for substantial agreement.

**Empirical basis:** Supreme Court case summaries — **single documents, not dialogue**.

**How an LLM transcript would be coded against it:** it is the procedural precedent for
having an LLM apply this project's coding scheme to its own transcripts: give the model
the codebook, decompose the task into steps, and report κ against a human-coded subset.

**What it cannot validate:** anything about human conflict behaviour. And because the
texts are not conversations, its reliability figures do not transfer directly to coding
dialogue.

**Limitations stated by the authors themselves:** semantic ambiguity within case
summaries is noted as a challenge.

**BibTeX:** `hila2025assessing`.

### [Borse-2025] — Investigation of the Inter-Rater Reliability between Large Language Models and Human Raters in Qualitative Analysis

**Authors / Year / Venue:** Nikhil Sanjay Borse, Ravishankar Chatta Subramaniam,
N. Sanjay Rebello / 2025 / arXiv:2508.14764 `[non-archival]`.
**Link:** https://arxiv.org/abs/2508.14764
**Verified:** yes — arXiv abstract page opened.
**Sub-area:** A5

**The codeable scheme it provides:** none of its own; it replicates an existing manual
coding of **group discussion transcripts**.

**Frequency data:** not applicable.

**Inter-rater reliability:** **Cohen's κ > 0.6 (substantial) for three themes, moderate
for one**, after optimising prompts and hyperparameters, for ChatGPT-4o and
ChatGPT-4.5-preview.

**Empirical basis:** audio transcripts of **14 undergraduate student groups** discussing
problem-solving strategies, at a university in the midwestern United States.

**How an LLM transcript would be coded against it:** it is the closer precedent of the
two, because the coded material is **multi-party discussion transcripts**, like this
project's. It also sets the expectation that agreement is theme-dependent.

**What it cannot validate:** human conflict behaviour. Note also the authors' own finding
that the models were weaker on "domain-general constructs" — conflict strategy labels are
exactly that kind of construct.

**Limitations stated by the authors themselves:** limitations "in rating domain-general
constructs"; results are from one course context.

**BibTeX:** `borse2025investigation`.

---

## What this review adds up to

1. **There is a usable scheme for endings, with base rates.** Pütz & Hassan's
   submission / stand-off / compromise, plus "most conflicts end after two or three
   disagreements" and the frequency ordering, is the single most useful finding for
   validation, because it supports comparison of *how often*, not just *whether*.
2. **There is a usable scheme for tactics.** Sillars' avoidance / integrative /
   distributive was built for coding conflict transcripts and is still used.
3. **There is a usable outcome base rate from text chat.** KODIS's ~18% impasse rate in
   human dyadic disputes is the natural comparison for how often LLM agents fail to
   resolve.
4. **The styles taxonomy is contested and is not a transcript scheme.** Rahim's five
   styles are well known but were validated as self-report, and Weider-Hatfield argues
   for three factors, not five. Using them to code talk is a defensible choice that must
   be argued, not assumed.
5. **The biggest hole is reliability figures.** Only the A5 method papers report kappa.
   None of the human-behaviour entries reports inter-rater reliability at abstract level.
   Retrieving the VTCS manual and the Pütz & Hassan full text is the highest-value next
   step.
