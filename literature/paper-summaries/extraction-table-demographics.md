# Extraction table — demographic papers (issue #18)

Prepared for issue [#18](https://github.com/M450NCH00/CrowdSimulation/issues/18), Part 2.
One row per paper. Companion files: summaries
[`07`](07-older-workers-conflict-management.md), [`08`](08-roci-ii-adolescents.md),
[`09`](09-implicit-bias-multi-agent.md), [`10`](10-fairness-llm-negotiator.md),
[`11`](11-generation-gap-age-bias.md); notes in
[`reading-notes-demographics.md`](reading-notes-demographics.md).

> **⚠ No synthesis in this file.** Per the issue, this table records what each paper reports,
> in its own terminology. **No row asserts that any finding here is equivalent to, supports,
> or contradicts any finding in another row.** Every judgement of that kind — including every
> comparison between a Group L result and a Group H result — lives in
> [`reading-notes-demographics.md`](reading-notes-demographics.md), with its reasoning.
>
> Constructs that share a word across rows are **not** thereby the same construct. "Avoiding"
> in row 1 is a Rahim subscale score from a workplace questionnaire; "avoidance" appears
> nowhere in rows 3–5. Readers should not align them.

**Measurement type** is one of: self-report, observed behaviour, LLM output, or other
(specified).

---

| Paper | Group | Attribute(s) | Setting or task | Anything contested? | Effect reported (paper's own terms) | Measurement type | Human data used? | "Bias" standard (Group L only) |
|---|---|---|---|---|---|---|---|---|
| **07** Yeung & Ho (2020), *Focus on Opportunities or Limitations?* | H | **Age** (Study 1 range 20–68; Study 2 range 23–66). **Gender** measured and reported. | Workplace conflict with a co-worker. Study 1: habitual use of five conflict management strategies. Study 2: use in one recalled real-life conflict incident from the previous six months. | **No.** No interaction occurs; participants report on their own past or typical behaviour. | **Indirect effects** of age through two mediators. Through "focus on opportunities", negative on all five strategies in Study 1 (integrating B = −0.005; compromising B = −0.005; obliging B = −0.003; avoiding B = −0.003; dominating B = −0.008) and on three in Study 2. Through "focus on limitations", positive on obliging (B = 0.003), avoiding (B = 0.005) and dominating (B = 0.006) in Study 1, and on the same three in Study 2. **Direct effects** in Study 1 observed only for obliging and avoiding, with younger employees using these two "passive strategies" more. **Zero-order:** age with obliging r = −0.18, with avoiding r = −0.12 (Study 1); no significant age correlation with any strategy in Study 2. **Gender uncorrelated with all five strategies** in Study 1. | self-report | **Yes** — the participants are the human data (N = 416 and N = 268, Hong Kong Chinese workers). | n/a (Group H) |
| **08** Filsecker, Abs & Roczen (2020), *The structure of conflict styles in adolescents* | H | **Gender** (boys/girls). **School grade** (8, 9, 10) as a narrow age proxy. | Conflict styles with schoolmates, measured by questionnaire in class. German secondary schools, N = 4112, median age 15. | **No.** Psychometric study; no conflict episode occurs. | **Measurement findings only.** A revised **17-item, three-factor** structure — "Integrating; Dominating; Avoiding" — replaced the five-factor model; Obliging items loaded on Integrating and were removed. Configural, metric and residual **invariance across gender** achieved (metric Δχ² = 12.884, Δdf = 15; residual Δχ² = 0.037, Δdf = 1). **Invariance across grades could not be established** — no baseline model could be specified for 9th graders (CFI .828, TLI .793); equivalence held between grades 8 and 10 only. **Substantive findings: none. No substantive gender differences reported.** | self-report | **Yes** — the participants are the human data (N = 4112 German adolescents). | n/a (Group H) |
| **09** Borah & Mihalcea (2024), *Towards Implicit Bias Detection and Mitigation in Multi-Agent LLM Interactions* | L | **Gender** only (male/female). Personas contain "just name and gender". | Task assignment among 3–4 LLM agents across seven domains, 111 scenarios. Protocol: first assignment, two discussion rounds, final assignment. | **Yes, in one of three settings.** In the "interaction (goal)" setting each agent is privately told to assign the same common task to itself, so all agents claim it. The "no goal" and "no interaction" settings are uncontested. | Bias scores "are always positive, showing biases towards males", and "increase after interaction for all models". Highest score 0.6990 (gpt-4, no interaction); every first-response → last-response pair rises, e.g. 0.2727 → 0.5741 (gpt-35-turbo, goal setting). Escalation held across all seven domains. Larger models showed higher bias scores. Best mitigation result: 0.01 (fine-tuned gpt-35-turbo with self-reflection + in-context examples). | LLM output | **No human behavioural baseline.** Human annotators (8, Cohen's κ = 0.823) validated that scenarios contain implicit bias; prior literature defined which tasks count as stereotypical. No human task-assignment behaviour was measured. | **(a) equal treatment.** Score zero is defined as tasks "evenly distributed across genders"; the paper positions its metric beside demographic parity and equalized odds. |
| **10** Mouri Zadeh Khaki & Choi (2026), *Evaluating Fairness in LLM Negotiator Agents* | L | **Gender** (male, female) **crossed with race** (White, Black, Asian, Latino), including intersectional cells. No age. | Buyer–seller price negotiation between two ChatGPT-4 Turbo agents, adapted from NegotiationArena. Production cost $40, willingness to pay $60, up to 10 turns, 20 games per scenario. | **Yes.** Described by the paper as "a distributive game where one player's profit is the other player's loss". | **Gender, reported separately (§4.1):** sellers achieved higher profit against female buyers than male buyers, $5.47 vs $4.97; final agreed price $48 vs $47.62; the $50 opening offer used in 62.5% of games with female buyers vs 58.75% with male buyers. **Gender in the reverse role (§4.2):** difference "negligible", $12.56 vs $12.57. **⚠ §4.3 reports only combined gender-by-race cells, so no gender-only effect is available for that scenario.** Authors' summary: sellers offer higher initial prices to "female and Latino buyers"; buyers negotiate more aggressively with female sellers. | LLM output | **No.** The claim that women face unequal outcomes in human interaction is asserted by citation in §1; no human negotiation data is measured or compared. | **(a) equal treatment**, despite an accuracy-flavoured framing in the Abstract. Measurement is against a demographic-blind baseline and across-group parity; RQ3 targets mitigating disparity. |
| **11** Liu, Maturi, Yi, Shen & Mihalcea (2024), *The Generation Gap* | L | **Age** only — six groups: 18–24, 25–34, 35–44, 45–54, 55–64, 65+. Crossed with country. No gender. | World Values Survey questions answered by six LLMs. Single agent, single-choice survey items, eight prompt variants per inquiry. | **No.** One agent, no interaction, nothing contested. | "A general inclination of LLM values towards younger demographics", measured by trend coefficient and alignment rank against human cohorts. Inclination varies by value category and is "less evident" in Ethiopia and Nigeria. Adding age identity to the prompt produced **no improvement in eight of thirteen categories**. Authors state LLM values may sit far from every human age group, and restrict their claim to "a significant tendency over age" rather than resemblance to any cohort. | LLM output | **Yes** — World Values Survey wave 7, 94,000 respondents, 13 categories, 372 value vectors across 62 countries and 6 age groups. | **(b) real human beliefs**, measured as relative inclination across age groups rather than absolute resemblance. A parity note appears in the Conclusion ("equitable representation"), but the measurement is accuracy-based. |

---

## Column notes

**"Anything contested?"** is answered structurally, not by topic. A paper counts as contested
only where two or more parties have opposed interests in the same outcome within the study
itself. By that test, two of the five papers involve a contest: row 09 in its goal setting
only, and row 10 throughout.

**"Human data used?"** distinguishes two very different things, and the distinction is not
visible in a yes/no answer alone, so it is spelled out in each cell:

- In rows 07 and 08 the humans **are the study** — they are the participants.
- In row 11 human survey data is the **comparison target** for LLM output.
- In row 09 humans **validated the stimuli** but no human behaviour was measured.
- In row 10 no human data enters at all.

**Attribute coverage across the five papers**, recorded as a fact about the set rather than as
a synthesis:

| | Gender studied | Age studied |
|---|---|---|
| Group H | 07 (measured, reported null), 08 (measurement invariance only) | 07 (20–68, 23–66), 08 (grades 8–10 only) |
| Group L | 09, 10 | 11 |

**No paper in this set varies gender and age together**, and **no Group L paper in this set
studies age in an interactive or contested setting**.
