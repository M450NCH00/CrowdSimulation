# [SiyangLiu-GenerationGap] — The Generation Gap: Exploring Age Bias in the Value Systems of Large Language Models

Prepared for issue [#18](https://github.com/M450NCH00/CrowdSimulation/issues/18). Group L
(LLM-side). Template: L.

> ## ⚠ Read this before using this summary
>
> **This paper is about value systems, not conflict behaviour.** It measures how closely an
> LLM's survey responses match those of human age cohorts. It contains no agents, no
> interaction, no negotiation and no conflict. It is **upstream evidence about how LLMs
> represent older adults**, and it must not be cited as evidence about how LLMs behave in
> conflict.

## Citation

**Authors / Year / Venue / DOI:** Siyang Liu, Trisha Maturi, Bowen Yi, Siqi Shen and Rada
Mihalcea (The LIT Group, Department of Computer Science and Engineering, University of
Michigan, Ann Arbor) / 2024 / Proceedings of the 2024 Conference on Empirical Methods in
Natural Language Processing, pages 19617–19634, Miami, Florida, USA /
doi:10.18653/v1/2024.emnlp-main.1094.

**Confirmed from:** the ACL Anthology's own BibTeX export for this paper, fetched and cached
at `refs/p18_05_generation_gap_acl.bib`, which supplies all five authors, the booktitle,
month, year, address, publisher, page range and DOI. The paper's own title page, read from the
published PDF, carries the same five authors and the Michigan affiliation, and the page
footers show 19618 onwards.

**Peer-review status: published at a peer-reviewed venue** — EMNLP 2024 main conference.

**⚠ Version read, and a correction to an earlier repository entry.** The version read here is
the **published EMNLP 2024 PDF**, cached at `refs/p18_05_generation_gap_emnlp.pdf` with a text
extract at `.txt`. All locators below refer to it.

An earlier entry in this repository — `literature/demographic-personas/llm-demographic-effects.md`,
written for issue #16 — records this paper as a **`[preprint]`** on the grounds that the arXiv
abstract page carries no Comments field and no journal reference, and states that no published
version was located. **That is wrong.** A published version exists, at the venue above. The
error arose from relying on arXiv metadata fields that the authors had not filled in. The
correction is carried into this issue's `refs-demographics.bib`, and is flagged in
[`reading-notes-demographics.md`](reading-notes-demographics.md) and in the work log so the
parent issue's file can be fixed.

Note also that the arXiv v4 is a **5-page** document (its Comments field reads "5 pages")
while the published paper spans pages 19617–19634. Anyone comparing the two should not assume
the section numbering matches.

## Accessibility

**Full text read**, published version.

---

## 1. Research question

Whether, and in which value categories, the values expressed by LLMs align more closely with
particular human age groups (§1, and the Abstract).

A second question is pursued in §5: whether adding age identity information to the prompt
reduces the discrepancy between an LLM's values and those of the targeted age cohort.

## 2. Setup

**Models — six.** Listed in Table 1 (§3.2), with the paper's own version labels:

| Model | Version as given |
|---|---|
| ChatGPT | GPT-3.5-turbo 0613 |
| InstructGPT | GPT-3.5-turbo-instruct |
| Mistral | mistral-7B-v0.1 |
| Vicuna | vicuna-7b-v1.5 |
| FLAN-T5 | flan-t5-xxl |
| FLAN-UL2 | flan-ul2 |

Table 1 also categorises them by commercial versus open, chat-based versus completion-based,
RLHF, and instruction training.

**Demographic attribute varied: age only.** Six age groups, given in a footnote in §3.1:
**18–24, 25–34, 35–44, 45–54, 55–64, and 65+**. No gender persona is studied.

**How personas were specified.** Two distinct conditions:

1. **No identity** — the model simply answers the survey inquiries (§3.2).
2. **Explicit age and country identity**, added as a sentence at the start of the required
   component of the original prompt, instructing the model to suppose it is from a given
   country with an age between a stated lower and upper bound (§5). This is an **explicit
   label**, not a name cue and not a backstory.

**Prompt design.** Three components per inquiry were identified: context, question ID and
content, and options. To guard against prompt sensitivity the authors built **eight distinct
prompt variants per inquiry**, altering wording and the order of components, while
deliberately avoiding major changes because the WVS content and structure were designed by
professionals (§3.2, and its footnote 2).

They report checking the stability of this: on **95.5% of questions**, more than half of the
eight prompts produced responses centred on the same choice or adjacent options, which they
take as justification for averaging across the eight variants (§3.2). They also catalogue
seven types of unexpected reply and their coping method for each, in Table 3.

**Other attributes studied alongside age:** **country**, which is crossed with age throughout.
No gender, no race, no socioeconomic status.

## 3. Interaction design

**Single agent.** There is no multi-agent setting, no dialogue and no turn-taking.

**Task type: a value survey.** The model answers single-choice questions drawn from the World
Values Survey, with numeric responses quantifying inclination across the offered options
(§3.1).

**Is anything contested between agents?** **No.** Nothing is contested, because there is only
one agent and no interaction. This is the single most important structural fact about the
paper for the FYP's purposes.

**Turn structure and termination:** `[not stated in paper]` — not applicable to a
single-response survey design.

## 4. How the effect was measured

**The comparison data — stated precisely, as the issue requires.**

- **Survey:** the **7th wave of the World Values Survey** (Haerpfer et al., 2020) (§3.1).
- **Scale:** the survey probes **94,000 individuals globally** across **13 value categories**
  spanning social, political, economic, religious and cultural values (§3.1).
- **Human cohorts:** respondents were grouped **by age group and by country**, and the average
  value for each age-by-country cohort was computed to represent it, with invalid negative
  codes ignored (§3.1).
- **Coverage used in the analysis:** **372 value vectors representing people across 62
  countries and 6 age groups** (§3.3).
- Countries named in the reported results include the US, China, Germany, Great Britain,
  Ethiopia and Nigeria (§4, Figure 2 and its discussion).

**Representation.** A vector V_c represents the values in category c, with each WVS question
treated as a dimension (§3.3). Min-max normalisation and standardisation are applied, followed
by principal component analysis reducing to three dimensions.

**Three metrics** (§3.3):

1. **Euclidean distance** between two value representations.
2. **Alignment Rank** — the ascending rank of the distances between the LLM's values and those
   of the six human age groups. Rank 1 for an age group means that group has the narrowest
   value gap with the LLM (Figure 2 caption).
3. **Trend Coefficient** — the slope of the value gap between LLM and humans across the six age
   groups, obtained by fitting a linear relation to the ranks. **A positive trend coefficient
   signifies a widening gap from younger to older groups, indicating a model leaning towards
   younger age groups** (Figure 1 caption).

**Significance testing** (§Appendix F, summarised in the appendix text): a MANOVA to test for
significant differences among human values across age groups, and a t-distribution test for a
significant tendency of LLMs towards younger groups.

**Conditions compared:** no-identity prompting versus age-identity prompting, with the change
in Euclidean distance as the outcome (§5, Figure 4).

## 5. Findings

⚠ **All findings below concern value alignment. None concerns behaviour in conflict.**

### 5a. LLM values lean young

The headline result is a general inclination of LLM values towards younger demographics,
especially relative to the US population (Abstract; §4, Figure 1). In the US and China, the
models tend to rank younger groups higher on alignment across most categories, with a few
exceptions the authors name, such as happiness and well-being (§4).

The direction is given by the trend coefficient, defined so that positive means a gap widening
from younger to older groups (Figure 1 caption).

### 5b. The lean is not uniform across categories or countries

The authors state that the inclination toward younger groups differs across value categories
(Abstract). Geographically, they report that in **Ethiopia and Nigeria the inclination is less
evident**, and they explicitly leave this for future study rather than explaining it (§4,
referring to Table 15).

### 5c. Age-identity prompting largely fails to close the gap

This is the finding with the most direct bearing on the FYP.

After adding the age identity sentence to the prompt, the change in Euclidean distance between
LLM values and the values of the targeted human age group shows **no improvement in eight of
the thirteen categories** — the paper names them as categories 1, 2, 4, 5, 7, 8, 11 and 12
(§5, Figure 4; also stated in §1).

The authors qualify this with occasional successes in specific instances, and present one in a
case study: for an inquiry about the frequency of using radio news, adding age to the prompt
brought the model's response closer to the US population of that age group, with the model
reporting higher radio news use for the older group (§5, Figure 5).

### 5d. An important caveat the authors themselves raise

The LLM's values can sit **far from every human age group**, not merely from some of them
(§4, Figure 3, second sub-figure; discussed in Appendix G.2).

The authors are explicit about what this means for the scope of their claim: their focus is on
characterising the *inclination* of LLM values toward particular age groups, and they are
claiming a **significant tendency over age, rather than claiming that LLMs significantly
resemble any specific age group** (Appendix G.2, and repeated in the appendix discussion of
significance testing).

**This qualification should travel with every use of this paper.** The result is about relative
ordering, not about the LLM matching any real cohort.

### 5e. The authors' own conclusion

In the Conclusion they state that they investigated value alignment with specific age groups
using WVS data, that the findings suggest a general inclination toward younger demographics,
and they advocate continued community effort on age bias, noting that calibration efforts
should reckon with the complexities of prompt engineering and aim at equitable representation
across age groups.

## 6. What "bias" is measured against

**Standard (b): deviation from real human beliefs — an accuracy standard — but measured as
relative inclination, not as absolute resemblance.**

This paper is the only one of the three Group L papers in this issue whose comparison target is
real human data.

- **The human data is named and specific:** the 7th wave of the World Values Survey, 94,000
  respondents, 13 categories, grouped into 372 age-by-country cohorts across 62 countries
  (§3.1, §3.3).
- Every metric is a distance or rank **between the LLM and those human cohorts** (§3.3).

**But the accuracy claim is deliberately limited.** Because the LLM's values may be distant
from all human age groups, the authors restrict their claim to the *tendency* across age
groups rather than to resemblance of any one group (Appendix G.2). So this is an accuracy
standard applied to the *shape* of the age gradient, not to the *level*.

There is also a trace of standard (a) in the framing: the Conclusion calls for equitable
representation across diverse age groups, which is a parity goal rather than an accuracy goal.
The measurement, however, is squarely (b).

## 7. Mitigation

**Method tested: adding explicit age identity to the prompt** (§5).

**Reported effect: largely insufficient.** No improvement in eight of thirteen categories
(§5, Figure 4), with occasional success in specific instances such as the radio-news case
study (§5, Figure 5). The authors describe the difficulty as one of calibrating prompts
effectively (§1).

They note in the Limitations that time and cost prevented them from trying more sophisticated
prompts for age alignment, which they say might be more effective.

**`[inference]` — would this mitigation move the LLM toward or away from realistic human group
differences?**

**Toward realism, in intent — which makes it unusual among the Group L papers here.** Unlike
the parity-targeted mitigations in `09-implicit-bias-multi-agent.md` and
`10-fairness-llm-negotiator.md`, this intervention aims to make the model's values *match a
specific human cohort more closely*, and it is evaluated by whether the distance to that cohort
shrinks. That is an accuracy target, and it is the same target the FYP needs.

The result is therefore discouraging for the FYP rather than reassuring: **the one mitigation
in these five papers that is aimed at realism is the one reported as mostly not working.**

## 8. Limitations stated by the authors

From the Limitations section:

1. **LLM values may not resemble any human age group**, which the authors acknowledge raises a
   question about the importance of any trend. They conjecture this follows from human
   preference optimisation producing extreme preferences unlike the subtler preferences of
   humans, and they call for future work reflecting on whether over-aligning LLMs with human
   preference is problematic. They restate that their study emphasises inclination rather than
   absolute difference.
2. **Limited prompt exploration** — time and cost prevented trying more sophisticated prompts
   for age alignment, which might have eliminated the value disparity more effectively.
3. **The WVS questionnaire is not tailored to age discrepancies.** The authors state that its
   question design is not perfectly suited to characterising age differences, which limits the
   depth of the analysis.

From the Ethics Statement: WVS data was acquired with the publisher's permission, and AI
assistants were used to help improve the writing while the authors take responsibility for
originality.

## 9. Relevance to this FYP

`[inference]` — my judgement.

**First, what this paper cannot do.** It cannot tell the FYP anything about how LLM agents
behave in a conflict, how they negotiate priority, or whether an elderly persona yields. There
are no agents and no interaction. Any use of it for those purposes would misrepresent it.

**What it can do:**

1. **It is upstream evidence that the elderly persona is the weak one.** The FYP's dataset is
   organised by age band, with `elderly` among them. This paper reports that the models tested
   lean young in their value systems and that telling a model an age largely fails to move it
   to the target cohort in most categories. If a model's underlying value representation is
   young-skewed and resists an explicit age instruction, an `elderly` persona label may be
   producing a surface-level performance of age rather than a shift in the model's
   representation.
2. **It suggests a concrete diagnostic.** The paper's design — instruct an age, then measure
   the distance to the real cohort — is reusable in principle. The obstacle for the FYP is that
   it has no human cohort data on pedestrian yielding to measure distance against, which is
   precisely the gap recorded in the parent issue's comparison table.
3. **Its culture-dependence result matters for a Singapore-scoped project.** The young lean was
   less evident in Ethiopia and Nigeria (§4). A result derived from US and Chinese cohorts
   should not be assumed to hold for Singapore without checking, and Singapore is not among the
   countries named in the reported results.
4. **Which Group H paper could it be compared against?** **Neither, directly.** Paper 1 measures
   self-reported workplace conflict strategy, Paper 2 measures instrument structure; this paper
   measures survey values. The constructs do not meet. This is set out in
   [`reading-notes-demographics.md`](reading-notes-demographics.md).
5. **A caution about `run01`'s passing age hypotheses.** `run01` records that elderly personas
   walk slower and yield at least as much as young adults, and treats these as passes. This
   paper gives a reason why such passes are weak evidence: a model can reproduce the expected
   age script without its underlying representation shifting toward that cohort at all.

## BibTeX

`siyangliu2024generation` — see [`refs-demographics.bib`](refs-demographics.bib).
