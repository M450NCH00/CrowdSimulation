# Reading notes — demographic papers (issue #18)

Prepared for issue [#18](https://github.com/M450NCH00/CrowdSimulation/issues/18), Part 3.
**Nothing in this file is paper content.** It is observation, comparison and judgement about
the five papers summarised in [`07`](07-older-workers-conflict-management.md),
[`08`](08-roci-ii-adolescents.md), [`09`](09-implicit-bias-multi-agent.md),
[`10`](10-fairness-llm-negotiator.md) and [`11`](11-generation-gap-age-bias.md). Paper claims
carry locators; everything else is mine.

---

## 1. Comparability check

**The question:** for each Group L paper, which Group H paper could serve as its human
baseline, and what weakens the comparison?

**The short answer: none of the three Group L papers has a fair human baseline in this set.**
I set out each case rather than forcing a match, because a forced comparison would be worse
than none.

### 09 (implicit bias in multi-agent task assignment) → no fair baseline here

| Candidate | Verdict | Mismatches |
|---|---|---|
| **07** Yeung & Ho | **Not comparable** | **Construct:** 09 measures how tasks are *allocated between people*; 07 measures a person's *self-described style* of handling a dispute. Allocating a task to someone else is not a conflict-handling style. **Task:** contested task claiming vs recalled workplace disagreement. **Measurement:** LLM output vs self-report. **Population:** 07's gender result is a null in a sample of Hong Kong Chinese working adults; 09's agents have no age, nationality or occupation. |
| **08** Filsecker et al. | **Not comparable** | 08 reports **no substantive gender difference at all** — it is a measurement study. There is nothing to compare a direction against. Additional mismatches: German adolescents; school setting; and the revised instrument no longer contains an Obliging factor. |

**The best available comparison for 09 is a partial and negative one:** 07 reports that gender
predicted none of the five conflict strategies in 416 adults (Study 1, Descriptive Analyses;
Table 1 gender column −0.08 to 0.06, none significant). That is a human null in a different
construct and setting. It does not contradict 09's pro-male allocation bias, because the two
measure different things — but it does mean **nothing in this set of papers provides positive
human evidence that a gender difference of the kind 09 measures exists in people.**

### 10 (LLM negotiator fairness) → 07 is the closest, and it is still weak

**07 is the nearest thing to a baseline in this set**, because it is the only Group H paper
whose constructs (obliging, avoiding, dominating) describe conceding and pressing, which is
what a negotiation measures.

Mismatches, all of which weaken it:

- **Construct.** 10's outcome is a **monetary profit margin**; 07's outcome is a **Likert-scale
  self-rating of strategy use**. There is no mapping between $0.50 of seller profit and a
  0.1-point shift on a five-point obliging subscale.
- **Who carries the demographic.** In 10 the gender label is attached to the **counterpart**
  (§3.1) — an agent is told who it faces and has no identity of its own. In 07 the gender is
  the participant's own. These are different manipulations and there is no reason to expect
  them to behave alike.
- **Measurement type.** LLM output vs self-report.
- **Population.** 07 is Hong Kong Chinese working adults aged 20–68. 10's agents have no
  nationality and no age.
- **Direction check.** 10 reports female counterparts conceding more when the seller is
  informed (§4.1, $5.47 vs $4.97); 07 reports **no gender effect in either direction**
  (Study 1, Descriptive Analyses). A positive LLM effect against a human null is not a
  direction reversal, and should not be written up as one.
- **Role asymmetry inside 10 itself.** The gender effect was substantial in one role and
  negligible in the other (§4.2, $12.56 vs $12.57). A baseline comparison against a single
  number from 10 would be comparing against an effect the paper itself shows is unstable
  across roles.

**Verdict: a comparison is possible but should be reported as weak, and should carry the
direction caveat above.**

### 11 (age bias in LLM value systems) → no fair baseline here

| Candidate | Verdict | Mismatches |
|---|---|---|
| **07** Yeung & Ho | **Not comparable** | **Construct:** 11 measures *values*; 07 measures *conflict strategy use*. A value survey response and a conflict strategy are different objects. 11 has no interaction and nothing contested (§3.1–3.2). |
| **08** Filsecker et al. | **Not comparable** | 08's age proxy spans grades 8–10 only, and invariance across those grades **could not be established** (Results). 11's age groups run 18–24 to 65+. Non-overlapping ranges, and the narrower one is not measurably comparable within itself. |

**However — 11 already has its own human baseline built in**, and it is better than anything
either Group H paper could supply for it: World Values Survey wave 7, 94,000 respondents, 372
cohorts across 62 countries and six age groups (§3.1, §3.3). For value alignment, 11 does not
need a baseline from this set.

### Summary of the comparability check

**No Group L → Group H comparison in this set is strong.** One is weak-but-arguable (10 → 07);
the rest are not comparable. The reason is structural rather than accidental: **the two Group H
papers measure self-reported dispositions in people with ongoing relationships, and the three
Group L papers measure output behaviour in systems with no relationships at all.**

`[suggestion for the parent issue, not applied here]` —
`literature/demographic-personas/realism-vs-bias-comparison.md` is out of scope for #18, but
this check supports two of its existing rows and sharpens a third. Specifically: its `RUN01-G`
and `L1` rows use the 07 null via `not comparable`, which this deeper read supports; and its
`L2` row, currently `no human evidence found`, could note that 07 is the nearest candidate
baseline and why it still fails.

---

## 2. Fairness versus realism

**The tension, stated once:** the FYP wants a simulation that reproduces how people actually
behave. Two of the three Group L papers treat **equal treatment** as the correct target. Where
real groups do differ, optimising toward parity moves a model *away* from the FYP's goal.
Where real groups do not differ, parity and realism coincide. **Neither paper measures which
case it is in.**

### Where the framing assumes parity is correct

**09 — explicitly and structurally.** The bias score is defined so that zero means tasks
"evenly distributed across genders" (§4), and the paper positions its metric alongside
demographic parity and equalized odds (§4). The best mitigation result, 0.01, is described as
almost neutral (§6.3). Every evaluative statement in the paper treats movement toward zero as
improvement.

**10 — in the measurement and the intervention, though not in the rhetoric.** The Abstract asks
whether LLM agents *reflect existing human biases*, which is an accuracy question. But the
measurement is against a demographic-blind baseline (§4.1–4.3), RQ3 asks about mitigating bias
and improving outcomes for underrepresented groups (§1), and the intervention is applied
asymmetrically — conditioning the buyer only (§4.4). That is a fairness design throughout.

### Where the framing targets accuracy

**11 — alone among the three.** Its mitigation adds an age identity and is evaluated by whether
the Euclidean distance to the *targeted human cohort* shrinks (§5). That is the accuracy
standard the FYP needs.

**And it is the one reported as mostly failing** — no improvement in eight of thirteen
categories (§5, Figure 4).

### Where the conflict actually bites for this FYP

1. **A debiased model is not a more realistic model, and may be a less realistic one.** If the
   FYP ever adopts a debiasing technique from 09 or 10 to address the `run01` gender pattern,
   it would be optimising toward parity on the assumption that parity is what humans do. That
   assumption is untested in both papers.
2. **09 contains a concrete demonstration of the risk.** After mitigation, gpt-4 produced
   *negative* bias scores — anti-stereotypical assignments — and did not produce equally
   representative assignments after self-reflection (§6.3; §8). A model pushed past parity into
   counter-stereotype is not closer to human behaviour; it has simply overshot in the other
   direction.
3. **The honest framing for the FYP report.** The project's question is not "is the LLM fair?"
   but "is the LLM accurate?". These are different questions with different, sometimes opposed,
   answers. Most of the LLM bias literature — including two of the three Group L papers here —
   answers the first. **That mismatch is itself a finding worth stating explicitly to the
   supervisor**, because it explains why so much apparently relevant literature cannot settle
   the FYP's question.
4. **A caveat on my own framing.** Nothing above argues that the FYP *should* reproduce group
   differences it finds. Whether a crowd simulator ought to encode a real demographic
   difference is an ethical question separate from whether the difference is real. I am
   recording the measurement distinction, not taking a position on that.

---

## 3. Phase 1 link

**The `run01` pattern.** The Phase 1 validation report flags a systematic effect in which
female personas yield more than male personas
(`dataset/generated/validation_report.md`, REVIEW section). Every flagged `yield_likelihood`
cell runs the same way — male below female — with deltas from **−0.27 to −0.43**, for example
`bus_queue_boarding/child` at male 0.433 against female 0.867, and `corner_turn_90/teenager`
at male 0.333 against female 0.733.

**Which of these five papers bears on that pattern?**

### Bears on it directly

**07, and the bearing is negative.** In 416 Hong Kong Chinese workers, gender was not
correlated with either OFTP dimension or with any of the five conflict strategies, and was
excluded from the mediation analyses on that basis (Study 1, Descriptive Analyses). Table 1's
gender column gives −0.08 to 0.06 across the five strategies, none flagged significant.

This is the nearest human measurement in the set to "do women concede more", and it finds
nothing. Two qualifications that must travel with it: the construct is self-reported workplace
conflict style, not physical yielding; and the population is working adults, which excludes
three of `run01`'s five age bands — including `child` and `teenager`, the bands where
`run01`'s deltas are largest.

**10, and the bearing is same-direction but from the LLM side, not the human side.** Sellers
profited more against female buyers than male buyers, $5.47 against $4.97 (§4.1). That is an
LLM producing a female-concedes-more outcome, consistent in direction with `run01`. **It is not
corroboration that the pattern is realistic** — it is a second LLM showing the same thing, and
10 has no human baseline at all (§6). Note also that 10's manipulation is
counterpart-awareness, while `run01` assigns the persona to the agent itself.

**09, and the bearing is mechanistic rather than directional.** Bias scores rise from first to
last response in all six interacting conditions (§5.1.1, Table 1). `run01` is single-shot. If
this amplification generalises, `run01`'s deltas may be a floor rather than a ceiling for what
a dialogue-based system would produce. This is a prediction about the FYP's setting, not an
established fact about it.

### Bears on it only indirectly

**11** concerns age, not gender, and values, not behaviour. Its relevance to the `run01` gender
pattern is nil. Its relevance to `run01`'s **age** hypotheses is discussed in
[`11`](11-generation-gap-age-bias.md) §9.

### Does not bear on it

**08** reports no substantive gender differences (Results). It cannot speak to the `run01`
pattern in either direction.

### What the five papers together do *not* establish

**None of these five papers measures whether real people of different genders yield differently
in a brief physical encounter with a stranger.** The `run01` pattern therefore remains
unvalidated by this set. The nearest human evidence is a null in a different construct.

---

## 4. Tensions between papers

Stated, not resolved.

**Tension 1 — is gender a meaningful predictor of conflict behaviour at all?**

- **07:** gender was uncorrelated with all five conflict strategies in 416 working adults, and
  was dropped from the analysis for that reason (Study 1, Descriptive Analyses).
- **09:** bias scores are always positive, showing bias towards males, across three models and
  seven domains (Table 1 caption; §5.1.2).
- **10:** sellers profit more against female buyers, $5.47 against $4.97 (§4.1).

The constructs differ, so the tension may be apparent rather than real. **Not resolved here.**

**Tension 2 — within 07 itself, the direct and mediated age effects point opposite ways.**

- Direct effects were observed only for obliging and avoiding, with **younger** employees using
  these passive strategies more (General Discussion, Focus on Opportunities and on Limitations
  as Mediators).
- Indirect effects through focus on limitations were **positive** for obliging (B = 0.003) and
  avoiding (B = 0.005), i.e. older workers using them more (Study 1, Indirect Effect of Age…).

The paper itself notes the direct result fails to replicate the age-related increase in passive
strategies reported in earlier work (same section). **Not resolved here.**

**Tension 3 — 07's two studies disagree at the zero-order level.**

- Study 1: age correlated with obliging at r = −0.18 and avoiding at r = −0.12 (Table 1).
- Study 2: neither age nor its quadratic term was related to any of the five strategies, with r
  from −0.02 to 0.07 (Study 2, Descriptive Analyses).

**Not resolved here.**

**Tension 4 — does an explicit demographic label actually change the model?**

- **09:** yes, decisively — gendered justifications appeared although personas contained only
  name and gender (§7).
- **11:** largely no — adding age identity produced no improvement in eight of thirteen value
  categories (§5, Figure 4).

The attributes differ (gender vs age) and the outcomes differ (task allocation vs survey
values). **Not resolved here** — but see Gaps below, because this is the tension the FYP most
needs closed.

**Tension 5 — does the standard five-factor conflict-style model hold?**

- **07** uses the 28-item five-factor Chinese ROCI-II and reports satisfactory fit:
  χ²(138) = 474.40, CFI = 0.90, TLI = 0.87, RMSEA = 0.08, SRMR = 0.07 (Study 1, Measures).
- **08** could not reproduce five factors in adolescents and settled on a 17-item three-factor
  structure, with Obliging items loading on Integrating and removed (Discussion).

Different populations and different language versions. **Not resolved here.**

---

## 5. Gaps — what these five papers do not cover that the FYP still needs

1. **Human evidence on gender or age effects in brief conflicts between strangers.** None of
   the five studies a one-off encounter between people with no relationship. Both Group H
   papers study people embedded in ongoing relationships — co-workers, schoolmates.
2. **Any observed conflict behaviour at all on the human side.** Both Group H papers are
   self-report questionnaires. Neither observed, recorded or transcribed a conflict. The FYP
   wants to validate generated *dialogue* and has no observed human dialogue here to validate
   against.
3. **Any spatial or physical conflict.** No paper here involves movement, space, right-of-way,
   or simultaneity.
4. **Age in an interactive LLM setting.** 11 studies age but has one agent and no interaction
   (§3.1–3.2); 09 and 10 are interactive but study gender only. **No paper in this set puts an
   age persona into a contested interaction.** Given that `dataset/personas.yaml` is organised
   primarily by age band, this is the largest single gap.
5. **Children and the elderly.** 07 covers ages 20–68 and 23–66; 08 covers roughly ages 14–16;
   11's youngest band starts at 18. **No human evidence here covers `run01`'s `child` band, and
   none covers the elderly in a conflict setting.**
6. **Singapore, or any Southeast Asian population.** The human samples are Hong Kong Chinese
   (07) and German (08). 11's reported country results name the US, China, Germany, Great
   Britain, Ethiopia and Nigeria — not Singapore.
7. **Gender and age varied together.** No paper in this set does it, so no interaction between
   the two attributes can be assessed.
8. **A human baseline of the kind 11 has, for behaviour rather than values.** 11 demonstrates
   what a proper LLM-versus-human comparison looks like when survey data exists. The FYP has no
   equivalent dataset for pedestrian yielding, which is why its comparison table has so many
   unfilled rows.

---

## 6. My own methodological concerns

**Kept separate from the authors' stated limitations, which are recorded in §7 or §8 of each
summary.** These are my observations and may be wrong.

1. **07 reports its total and direct effects only inside figures.** The numeric values of `c`
   and `c'` appear in Figures 1 and 2 as path-diagram labels and nowhere in the text or tables
   (Figure 1 caption; Figure 2 caption). A reader without figure access cannot extract them,
   and a reader relying on the Abstract would get only the indirect effects — which, as
   Tension 2 shows, point the opposite way from the Study 1 direct effects. **The Abstract is
   not a safe summary of this paper.**
2. **07's headline framing is mediated, and the mediator does not exist in the FYP's setting.**
   Nearly all the paper's age effects run through occupational future time perspective. A
   doorway encounter has no career runway. The construct that carries the result does not
   transfer.
3. **08 has no Limitations section** in the accepted manuscript I read, and I could not locate
   an equivalent passage. For a paper that discards two of five factors from a widely used
   instrument, the absence of a stated-limitations discussion is notable.
4. **08's accepted manuscript contains several internal inconsistencies** — two tables both
   numbered 4, a text/table mismatch on the PTS correlations, a reference to an undefined scale
   "RES" with a value (.324) appearing nowhere in the tables, Sample 4 given as both 471/535
   and 464/534, and Sample 1 given as both 1056 and 1156. All are recorded in
   [`08`](08-roci-ii-adolescents.md). Most are probably artifacts of the accepted manuscript
   rather than the version of record, **but I cannot confirm that without the published
   version.**
5. **09's evaluation runs on data its own strongest model generated.** gpt-4 produced the
   scenarios and is also the most-biased model under test. The authors flag this themselves
   (§8). My added concern is that the **stereotypical/anti-stereotypical coding itself** was
   built into the generated scenarios, so the metric measures conformity to a gpt-4-instantiated
   notion of what is stereotypical. This is structurally the same concern that applies to
   `run01`, where DeepSeek generates and automated checks over the same outputs validate.
6. **10 computes confidence intervals but I did not find one attached to its headline gender
   contrast.** §3.2 specifies a 95% CI via Equation (1), yet the $5.47 versus $4.97 comparison
   in §4.1 is reported without an interval or a significance test. With 20 games per cell and a
   difference of about $0.50, the result's stability is not demonstrable from what is printed.
7. **10's condition count is internally inconsistent** — nine permutations in §3.2 against six
   subpopulations plus a baseline in §4.1. I could not resolve it.
8. **10's §4.2 sentence contradicts its own numbers** ($12.56 for female against $12.57 for
   male, described as buyers benefiting more from female sellers). Recorded as printed in
   [`10`](10-fairness-llm-negotiator.md).
9. **11's own caveat deserves more weight than its title gives it.** The paper's claim is about
   *relative inclination* across age groups, not resemblance to any cohort, and it states that
   LLM values may be far from all human age groups (Appendix G.2). A title containing "Age
   Bias" invites a stronger reading than the paper supports.
10. **A concern about my own work on the parent issue.** ⚠ In
    `literature/demographic-personas/llm-demographic-effects.md` and its `refs.bib`, written for
    issue #16, I recorded paper 11 as a **`[preprint]`** and stated that no published version
    was located. **That is wrong** — it is published at EMNLP 2024, pages 19617–19634,
    doi:10.18653/v1/2024.emnlp-main.1094, confirmed from the ACL Anthology BibTeX export cached
    at `refs/p18_05_generation_gap_acl.bib`. The error came from trusting the arXiv Comments and
    Journal-reference fields, which the authors left empty. **The corrected entry is in
    [`refs-demographics.bib`](refs-demographics.bib); the #16 files still carry the error and
    should be fixed** — see the work log, since those files belong to an open PR.
11. **A general concern about this set.** Three of the five papers were published in or after
    2024 and two of those are venue-fresh. Replication status for all three Group L papers is
    unknown, and none of the three has been independently reproduced as far as I could
    determine. Single-model results — 10 uses only ChatGPT-4 Turbo (§3.1) — should be weighted
    accordingly.
