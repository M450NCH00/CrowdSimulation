# Candidate coding scheme for LLM-to-LLM conflict transcripts

> ## ⚠ DRAFT — pending supervisor approval
> This is a **proposal assembled from the papers in
> [`verbal-conflict-resolution.md`](verbal-conflict-resolution.md)**, not an established
> instrument. Every category is attributed to its source. Where different papers use
> different labels for what *looks* like the same strategy, the labels are kept **side by
> side**: whether they are genuinely the same construct is a judgement that needs
> supervisor sign-off, and this file does not make it.

Prepared for issue [#12](https://github.com/M450NCH00/CrowdSimulation/issues/12).

## What this scheme is for

Given a transcript of two LLM agents resolving a conflict, assign categories that let the
project ask two questions:
1. **Possibility** — is this a strategy humans use at all?
2. **Frequency** — do humans use it *as often* as the agents do? (The second is the one
   that makes validation more than an anecdote, so base rates are carried through below.)

## Three layers, because the sources operate at different levels

The papers do not describe one thing. They describe utterances, episode endings, and
overall outcomes. Mixing them into a single flat list would misrepresent all three, so
the draft keeps them separate.

| Layer | Unit | What is assigned | Source |
|---|---|---|---|
| **L1 Tactic** | each utterance / turn | one of 3 tactic classes | Sillars et al. 1982 |
| **L2 Termination** | the conflict episode | one of 3 termination formats, or a closure act | Pütz & Hassan 2024; Toluei & Tahririan 2022 |
| **L3 Outcome** | the whole dialogue | agreement vs impasse | Hale et al. 2025 (KODIS) |

A fourth, optional layer — **L0 Style** (Rahim's five) — is described at the end, kept
separate because it was built for self-report questionnaires, not transcripts.

---

## L1 — Tactic, per utterance

**Source: Sillars, Coletti, Parry & Rogers (1982), the Verbal Tactics Coding Scheme
(VTCS).** Categories quoted from the abstract: statements are classified into
"avoidance", "integrative" and "distributive".

| Code | Source label | What would assign it in a hallway transcript |
|---|---|---|
| L1-AV | **avoidance** (Sillars et al. 1982) | declining to engage, changing the subject, non-committal replies |
| L1-IN | **integrative** (Sillars et al. 1982) | asking the other's constraint, sharing own constraint, proposing an option that serves both |
| L1-DI | **distributive** (Sillars et al. 1982) | demanding passage, blaming, threatening, insisting without giving reasons |

**Missing and needed:** the VTCS **subcategories** live in the Sillars (1986) coding
manual, which could not be obtained (see `search-log.md`). Coding at three classes only
is coarser than published VTCS use. **No inter-rater reliability figure was obtainable**
for VTCS at abstract level — a gap that matters, because L1 is the layer most exposed to
coder disagreement.

**Known confound, stated by the authors:** in Sillars et al.'s study 2, much of the
verbal–nonverbal relationship "stemmed from the talkativeness of integrative approaches".
LLM agents are verbose by default, so an LLM transcript may score integrative for reasons
that have nothing to do with cooperativeness. This must be controlled or acknowledged.

---

## L2 — How the episode ended

Two papers describe endings, and **they do not use the same labels or the same unit.**
Presented side by side, unmerged.

### L2a — Termination formats (Pütz & Hassan 2024)

Preconditions from the same paper: a conflict exists only where there is **continued
disagreement** (a disagreement pursued beyond the first turn), and episode length is
counted in **number of disagreements**.

| Code | Source label | What would assign it |
|---|---|---|
| L2a-SUB | **submission** | one agent drops its position; the other's position stands |
| L2a-STA | **stand-off** | neither concedes; the exchange ends with both positions intact |
| L2a-COM | **compromise** | both give something up; a joint position is reached |

### L2b — Closure acts (Toluei & Tahririan 2022)

| Code | Source label | What would assign it |
|---|---|---|
| L2b-REL | **relinquishing a position** by accepting the position maintained by another | "fine, you go first" |
| L2b-REP | **acknowledging the repair** performed by another party | closure follows a correction being accepted ("oh, you're carrying a box — go ahead") |
| L2b-NON | *non-resolution* (the paper identifies conditions under which disagreements are **not** resolved) | sequence lapses with no closure act; **exact conditions `[needs verification against full text]`** |

### Apparent correspondences — NOT merged

| Family | Rahim et al. (L0) | Pütz & Hassan (L2a) | Toluei & Tahririan (L2b) | Sillars (L1) |
|---|---|---|---|---|
| *one side gives way* | **obliging** | **submission** | **relinquishing a position** | — |
| *both give something up* | **compromising** | **compromise** | — | — |
| *neither gives way* | **dominating** (one side pressing) | **stand-off** (the joint outcome) | non-resolution | **distributive** |
| *disengagement* | **avoiding** | — | — | **avoidance** |
| *joint problem-solving* | **integrating** | — | — | **integrative** |

**Why these are not collapsed.** They differ in unit and in what they claim:
- *obliging* is a **disposition of one party** measured by questionnaire;
- *submission* is a **property of how an episode ended**, observed in talk;
- *relinquishing a position* is a **single action** that closes a sequence.

An agent can perform one act of relinquishing without having an obliging style, and an
episode can end in submission for reasons other than either party's disposition (for
example, running out of time). Treating these three as one label would silently assert a
theoretical claim the sources do not make. **Supervisor decision required.**

Note also that *stand-off* and *dominating* sit awkwardly together: stand-off describes a
**dyadic** result, dominating describes **one agent's** behaviour. A transcript can be
coded for both, but they are not alternatives to each other.

---

## L3 — Outcome of the whole dialogue

**Source: Hale et al. (2025), KODIS.** Binary: **agreement** vs **impasse**, recorded by
the task rather than coded, in **text-chat** dyadic disputes.

---

## Base rates — what to compare the LLM output against

| Measure | Human value | Source | Caveat |
|---|---|---|---|
| Distribution of termination formats | **submission most frequent, then stand-off, then compromise** | Pütz & Hassan 2024, abstract | rank order only; exact counts `[needs verification against full text]` |
| Episode length | **most conflicts end after two or three disagreements** | Pütz & Hassan 2024, abstract | workplace project meetings |
| Dialogue outcome | **~18% ended in impasse** (vs 3.5% in the CaSiNo deal-making corpus) | Hale et al. 2025, §1 | customer-service dispute, paid participants |
| Reply to a complaint | denials "predominantly", split between **"didn't do it"** and **"not at fault"** | Dersley & Wootton 2000, abstract | acrimonious argument; no counts |
| Mediator behaviour | 136 strategic interruptions across 23 sessions | Garcia 2025, abstract | only relevant if a third agent is added |

**The single most useful comparison** is the impasse rate. If the project's agents resolve
essentially every conflict, that is a measurable divergence from ~18% of human dyads in a
comparable text-only setting.

---

## L0 — Conflict style (optional, contested)

**Source: Rahim (1983); definitions quoted from Rahim & Magner (1995).** Five styles on
*concern for self* × *concern for others*: **integrating, obliging, dominating, avoiding,
compromising**.

**Two reasons this layer is optional, not recommended as primary:**
1. **It is a self-report instrument.** ROCI-II measures what people say about their own
   dispositions; it was not validated for coding observed talk.
2. **Its dimensionality is disputed.** Weider-Hatfield (1988) concluded that individuals
   "might select among three, not five, distinct conflict styles" (quoted in Rahim &
   Magner 1995, p. 123), and Rahim & Magner themselves report invariance holding for only
   4 of their 5 samples. Alternative taxonomies they list include two styles (cooperation,
   competition), three (nonconfrontation, solution-orientation, control — Putnam & Wilson
   1982), and four (yielding, problem solving, inaction, contending — Pruitt 1983).

⚠ **Licensing:** per the issue, use the **five-style taxonomy only**. The 28-item ROCI-II
instrument is commercially licensed and must not be reproduced in this repo or the report.

---

## Genuine disagreements between the sources

1. **How many style categories exist at all.** Five (Rahim) vs three (Weider-Hatfield's
   conclusion; Hocker & Wilmot's avoidance / competitive / collaborative clustering) vs
   four (Pruitt) vs two (Deutsch). The scheme above sidesteps this by using Sillars'
   three tactic classes at L1, which happen to align with the three-way clustering — but
   that alignment is itself an observation, not a validated equivalence.
2. **Whether agreement is still the preferred response during an argument.** Dersley &
   Wootton (2000) examine claims that "the preference for agreement" is **reversed**
   within argument sequences. This matters directly: LLM agents are trained to be
   agreeable, so if human disputants shift to preferring disagreement mid-argument and
   LLM agents do not, that is a validity problem for the whole approach.

## How to apply this scheme (proposed procedure)

1. Segment each transcript into turns; mark where continued disagreement begins
   (Pütz & Hassan's threshold).
2. Code every turn at **L1**; code the episode at **L2a** and **L2b**; record **L3**.
3. Have a **human** code a random subset and report **Cohen's κ** against the LLM coding.
   Precedents: κ = 0.744 with step-by-step task decomposition on documents
   (Hila & Hauser 2025); κ > 0.6 on three of four themes for group-discussion transcripts
   (Borse et al. 2025).
4. Compare distributions against the base-rate table above.

⚠ **Circularity warning.** Using an LLM to code LLM-generated transcripts risks the coder
sharing the generator's blind spots. Borse et al. report that models were weakest on
"domain-general constructs", which is exactly what conflict-strategy labels are. Any
LLM-assisted coding must be backed by a human-coded subset with a reported κ.

## What this scheme cannot do yet

- **No published reliability** for any of the human-behaviour categories (L1, L2a, L2b).
- **VTCS subcategories missing** — the 1986 manual was not obtained.
- **The CACS is absent** — its categories could not be opened (see `search-log.md`); it
  remains the most obvious addition if the full text can be obtained through NTU.
- **No spatial or non-verbal component** — see [`modality-note.md`](modality-note.md).
