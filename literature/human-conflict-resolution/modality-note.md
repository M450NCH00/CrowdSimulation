# Modality note — this validation covers verbal strategy only

Prepared for issue [#12](https://github.com/M450NCH00/CrowdSimulation/issues/12).
Short by design. Its job is to let the report **cite** the acknowledgment rather than
assert it.

## The limitation being acknowledged

The project's agents resolve conflict by exchanging text. The scheme in
[`candidate-coding-scheme.md`](candidate-coding-scheme.md) is therefore built from studies
of **talk**. But the FYP's target scenario — two people meeting head-on in a narrow
hallway — is one that real people usually resolve **without speaking**: by gaze, body
angle, slowing down, or stepping aside.

So validating an LLM transcript against verbal conflict-resolution categories tests
whether the agents *talk* about the conflict the way people do. It does **not** establish
that people resolve *this* conflict that way in the first place.

## What was found to support this (sourced)

**1. Conflict behaviour has a non-verbal component that verbal coding does not capture,
and the two can diverge.**
Caughlin & Vangelisti (2006), in *The SAGE Handbook of Conflict Communication*, section
"Negativity and positivity", record that the link between negative reciprocity and
dissatisfaction has been found "with measures focusing primarily on **nonverbal**
behaviors …, ones focusing mainly on **verbal** behaviors …, and schemes **mixing verbal
and nonverbal** assessments". They then state the divergence directly: "There is some
evidence that the affective aspect of negative reciprocity is more important than the
verbal exchanges: **Pike and Sillars (1985) replicated the usual findings pertaining to
negative reciprocity with affect codes but found contrary findings with verbal codes.**"
*Verified: full text of the chapter read (`refs/sage_conflict_dating_marital.pdf`).*

That is the strongest available statement for the report: coding the same conflicts
verbally versus affectively produced **contrary** results in at least one study, so a
verbal-only scheme is a partial view by demonstration, not merely in principle.

**2. Verbal tactics and non-verbal behaviour are empirically linked, so the verbal
channel is not self-contained.**
Sillars, Coletti, Parry & Rogers (1982) is itself a study of the **nonverbal correlates**
of the avoidance / distributive / integrative distinction; its second study "confirmed
predicted connections between verbal approaches and nonverbal behaviors", while noting
that much of this "stemmed from the talkativeness of integrative approaches".
*Verified: Oxford Academic abstract page.*

**3. A text-only human baseline does exist, which limits how damaging the gap is.**
Hale et al. (2025) collected **4,061 participants' dyadic disputes conducted in text
chat** (KODIS). So for the *text* modality there is a human comparison with real base
rates (~18% impasse). The mismatch is not "text versus human"; it is "text versus
spatial".
*Verified: full text read (`refs/kodis2025.pdf`).*

## What was NOT found

**No paper in this search states how people resolve a physical passing conflict
non-verbally and compares that with how they would resolve it verbally.** That
comparison — the one that would tell us how much the verbal-only scheme misses for a
hallway — does not appear in the material gathered here, and the issue puts researching
it out of scope.

The nearest evidence is already in this repo from issue #8, not from this search:
`literature/llm-conflict-resolution/topic2-sociological-grounding.md` records
**Yamamoto et al. (2019)**, a controlled experiment on **body rotation** when two
pedestrians pass in a narrow corridor — a purely physical resolution with no talk at all,
triggered when the corridor is narrower than the pedestrians' combined width. Cite that
alongside this note if the report needs to show that the non-verbal channel does the work
in the target scenario.

## Suggested wording for the report

> This validation compares LLM agents' *verbal* conflict-resolution strategies against
> categories derived from studies of human talk. Human resolution of a physical passing
> conflict is largely non-verbal (Yamamoto et al., 2019), and verbal and non-verbal
> coding of the same conflicts can yield contrary findings (Pike & Sillars, 1985, as
> reported in Caughlin & Vangelisti, 2006). The claim supported here is therefore that
> the agents' *dialogue* resembles human conflict talk, not that people resolve hallway
> encounters through dialogue.

⚠ **Pike & Sillars (1985) has not been opened.** It is cited above as reported by
Caughlin & Vangelisti. Retrieve it before the report cites it directly.
