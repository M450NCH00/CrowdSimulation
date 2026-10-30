# RF-10's factor effects (Phase A) against human evidence

Issue #69 (RF-14). Sources keyed as in `../sources.md`. Effects from
`llm_negotiation/runs/rf10_round1_head_on/screen_report.md`, sections 4 and 5. Round 1 has Phase A
only (RF-13, Phase B, moved to round 2 by the user, 2026-10-27).

**Perceived attractiveness and real ethnicity are graded like every factor, but whatever the evidence
says, an effect of either is reported as the model's bias, never as a rule** (#69, update of
2026-10-24; `CLAUDE.md`). No rule reads ethnicity; attractiveness only from rule format 4, as a
person's own view (RF-31).

| Factor and effect (what the LLM agents did) | Strength in RF-10 | Human evidence | Grade |
| --- | --- | --- | --- |
| **Own assertiveness** ("determined, tend to hold your ground") → the first plan slows less | OR 0.26 [0.14, 0.48], **Holm-significant** | Personality traits were not correlated with crossing order, path or speed adjustments; speed and heading decided the roles ([Knorr2016], abstract). The giver slows, the one going first mostly does not ([Olivier2013], abstract). | **Contradicted** as a personal factor: in people, who slows follows the role, and the role follows speed and heading, not personality. Which traits Knorr2016 measured is `[needs full text]`; if assertiveness itself was not among them, the grade would fall to No evidence. |
| **Knowing the other** (acquaintances) → signals | OR 221 [23, 2116], **Holm-significant** | Civil inattention is "a socially organized boundary mechanism through which regard without interest is allocated to unacquainted persons without sharing an invitation to become involved in engagement", kept distinct from "those ratified to receive focused attention" ([Arminen2023], full text, introduction, after Goffman 1963). No study counting signals between acquaintances when passing was found. | **Partly supported** (consistent with the sociology; not measured as such). |
| **Finding the other attractive** → signals | OR 5.29 [2.39, 11.72], **Holm-significant** | Attractive faces hold gaze longer ([Valuch2015], full text: hypothesis (a) supported; laboratory, photographs). Nothing found on signalling to an attractive stranger when passing. | **Partly supported** as attention only. **Reported as the model's bias, never a rule.** |
| **The other is 70** (against 25) → slows | OR 3.44 [1.57, 7.57], uncorrected; Step 1: a 25-year-old slows for a 70-year-old in 75 of 83 first plans, for a 25-year-old in 137 of 262 | The young adult "contributed more to the avoidance regardless of passing order" ([Rapos2021], abstract). | **Supported** in direction (who adjusts more); the evidence is of the share of the avoidance, not of slowing as such. |
| **Visiting from the United States** → the first plan turns right | OR 2.37 [1.42, 3.95], uncorrected | Right preference where traffic keeps right ([Moussaid2009]; [CircleAntipode2019]; [Jung2013]); no study of United States pedestrians among the sources read. | **Partly supported** (in direction, by analogy). |
| **The other has a cane** → signals | p = 0.003, uncorrected | Breaches of civil inattention toward visibly marked people were 10-fold ([Arminen2023], abstract). | **Partly supported** (looks, not signals). |
| **Real ethnicity** (same group, a pair of groups) | Nothing beyond the noise floor; largest term `same_ethnicity` on planning right, p = 0.019 uncorrected | Not searched: there is no effect to verify. | **Not graded** (no effect). Reported as: no evidence that the model treats people differently by the group it was told, at the size the screen could see. |

Not graded: own distraction (kept left at the meeting, p = 0.002 uncorrected) and one's own mobility
aid (signalling, p = 0.008), about as strong as the other's age but not on the Phase B shortlist and
without a search of their own here; and the weakest factors (urgency, memory note, time of day,
surroundings, gender, own age; smallest p from 0.03 to 0.09 uncorrected). RF-10, section 5.

**What this says about the model:** the one Holm-significant factor that bears on how a person
avoids, assertiveness, is the one the human evidence contradicts; the LLM agents decide the roles by
disposition where people decide them by motion. The factors that the evidence supports (the other's
age; one's country of residence for the side) are the ones a common-sense reading would predict.
