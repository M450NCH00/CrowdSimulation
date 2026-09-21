# Realism vs bias — LLM demographic effects against human evidence

> # ⚠ DRAFT
> **This file records evidence. It does not interpret it.** Per issue
> [#16](https://github.com/M450NCH00/CrowdSimulation/issues/16): *"Do not draw an overall
> conclusion about whether LLMs are 'realistic'. Record the evidence; interpretation requires
> supervisor discussion. Mark the file as a draft."* No overall verdict is offered below, and
> none should be quoted from it.

Sources: [`llm-demographic-effects.md`](llm-demographic-effects.md) (B1/B2),
[`human-demographic-effects.md`](human-demographic-effects.md) (B3/B4).
Handles in square brackets refer to entries in those files, where every quoted number has a
locator and a cached source.

---

## How to read this table — three conventions, stated up front

**1. Status values.** Exactly the four the issue permits:
`human evidence, same direction` · `human evidence, opposite direction` ·
`no human evidence found` · `not comparable`.

**2. ⚠ How a human *null* was mapped — a judgement call the supervisor should check.**
Three rows below (RUN01-G, RUN01-G2, L1) face a problem the four permitted values do not
cover: the LLM shows an effect and the best human study shows **no effect at all**. That contradicts the LLM result but is not
a *direction* reversal, so neither `same direction` nor `opposite direction` is accurate, and
`no human evidence found` would be false — evidence was found; it was null. In all three the
settings also genuinely differ, so **`not comparable` is used**, and the null is stated
explicitly in the Setting-differences column so it is not lost. **If the supervisor prefers a
fifth status value (`human evidence, no effect`), these rows are the ones to revisit.**

**3. ⚠ What counts as human evidence here.** Simulation papers whose demographic effects are
*input parameters* ([Zhu-MultiAttribute], [Ding-AsymmetricCompetitiveness]) are **not** used as
human evidence anywhere in this table — see the warning at the top of
[`human-demographic-effects.md`](human-demographic-effects.md). Where one of them is mentioned,
it is labelled a *modelling convention*, not evidence about people. Likewise, a human paper
cited *by* an LLM paper but not opened by me is never counted as verified human evidence; where
that happens it is said so in the row.

---

## The table

| # | LLM effect (paper, locator) | Human evidence on the same effect (paper, locator) | Status | Setting differences |
|---|---|---|---|---|
| **RUN01-G** | **Female personas yield more than male personas.** `run01`, `dataset/generated/validation_report.md`, `[gender-audit]` entries: `yield_likelihood` male < female in every flagged cell, Δ = **−0.27 to −0.43** (e.g. `bus_queue_boarding/child` male 0.433 vs female 0.867; `corner_turn_90/teenager` male 0.333 vs female 0.733) | **[Yeung-OlderWorkers]** (Study 1, Results): "Gender was not correlated with the two OFTP dimensions or the five conflict strategies" — n = 416 Hong Kong Chinese workers, Chinese ROCI-II. **A null.** | `not comparable` | LLM: a single-shot, stated yield-likelihood for a described Singapore street/transport scenario, DeepSeek, per-persona (not per-pair). Human: self-reported *habitual workplace* conflict style on a 28-item inventory, Hong Kong, working adults only (no children, teenagers or elderly). Different act (physical yielding vs conversational style), different setting, different age coverage. **The human result is a null, not a reversal** — see convention 2. |
| **RUN01-G2** | Same as RUN01-G | **[Holley-DemandWithdraw]** (Results): the canonical human gender difference in conflict talk is **not caused by gender** — relative desire for change predicted demand-withdraw polarization at **R² = 0.41, F(1,61) = 41.67, p < .01**, while couple gender composition added **R² change = .004** (ns); the null is shown not to be underpowered (average η² = .02; 270–9,630 couples would be needed) | `not comparable` | LLM: pedestrian priority, strangers, seconds-long, no relationship or power history. Human: intimate partners, 15-minute laboratory conflict conversation, US (Berkeley), ongoing relationship with an established power structure. The *mechanism* transfers as a caution (a gender effect can be wholly a power effect) but the settings are too different to call a direction. |
| **RUN01-A** | **Elderly personas yield at least as much as young adults.** `run01`, `dataset/generated/validation_report.md`, INFO: "[hypothesis] **PASS**: elderly yield at least as much as young adults" | **[Rapos-CollisionAvoidance]** (Results): "**Whenever an older adult was on a collision course with a young adult, the young adult contributed more to the avoidance regardless of passing order**"; older adults also passed closer (0.79 m ± 0.18) than young–young pairs (0.93 m ± 0.17), χ²(3) = 35.94, p < .0001. n = 17 older (68 ± 3 y) + 17 young (23 ± 2 y), 12.6 m pathway | `human evidence, opposite direction` | Both concern a two-person walking conflict — **the closest setting match in this whole table**. Differences: human study is a clean laboratory corridor with one walker to avoid, not a crowd; likely Canadian and/or French sample (unconfirmed) vs a Singapore-scoped LLM dataset; human measure is metric contribution-to-avoidance, LLM measure is a stated yield likelihood. Human evidence read from the **abstract only** (paywall). |
| **L1** | **Men concede more.** [Li-SingleToSocietal] §5.2: on Gemini-1.5-Pro men show a **60.7%** conformity rate vs a **56.3%** all-gender average; on DeepSeek-V3 the "man" persona conforms to the "woman" persona in **78.8%** of cases. §6.2: after 5 rounds, the woman's answer becomes the group decision **8% more often** | **[Yeung-OlderWorkers]** (Study 1, Results): gender uncorrelated with all five Rahim strategies, including obliging (conceding) and avoiding. **A null.** | `not comparable` | LLM: conformity to a partner's stated answer on graduate-level science questions (GPQA) and on subjective claims; agents mutually aware of personas. Human: self-reported workplace conflict style. Neither is a spatial or physical conflict. The human result is a null — convention 2. |
| **L2** | **Female counterparts are treated more exploitatively and concede more.** [Khaki-Fairness] §4.1: sellers earned **$5.47** against female buyers vs **$4.97** against male buyers; opening offer of $50 used in **62.5%** of games against female buyers vs **58.75%** against male buyers; final price $48 vs $47.62 | **None verified in this review.** The paper itself asserts by citation that women face unequal negotiation outcomes (Abstract; §1 ref [10]) but measures no human negotiation. No human negotiation-outcome study was located and opened in this review | `no human evidence found` | LLM: commercial buyer–seller price bargaining, ChatGPT-4 Turbo, ≤10 turns, 20 games per condition, **demographic attached to the counterpart rather than to the self**. Any human comparison would have to come from experimental-economics bargaining studies, which were not searched for here — this is a named gap, see [`search-log.md`](search-log.md). |
| **L3** | **Pro-male bias in contested task allocation, amplified by dialogue.** [Borah-ImplicitBias] Table 1 caption: "Scores are always positive, showing biases towards males. Scores also increase after interaction for all models"; §5.1.1: escalation in every setting; §5.1.2: in all seven domains; §7: bias scores ≥ ~0.5 in first responses | **None verified in this review.** The paper grounds its stereotypical/anti-stereotypical coding in prior human role-allocation literature (§3) and explains the amplification via Stereotype Threat Theory and Groupthink (§7), but collects no human data and I did not open those cited sources | `no human evidence found` | LLM: 3–4 agents allocating workplace/household/hospital tasks over two discussion rounds. Human comparison would need observational data on real mixed-gender groups allocating contested tasks — not searched for here. |
| **L4** | **Female agents soften when facing male agents.** [Bandaru-PoliticalDebate] §5.2: Female Republican agents held stronger conservative positions than males (mean attitude difference **0.32**, p = 0.00281) *"except when debating with two male agents where they became more left-leaning and agreeable"*; Female Democrat agents shifted further left facing two male agents (p = 0.0327); effects appear **only when agents are told each other's gender** | **None verified in this review.** No human study of how group gender composition changes an individual's conflict position was located and opened | `no human evidence found` | LLM: 3-agent political debate, 10 rounds, opinion conflict over abortion/immigration/climate. Distance from a doorway conflict is large. **But the structural point — that behaviour depends on the gender *composition of the pair*, not on the agent alone — has no human check here and is not detectable in `run01` at all**, since `run01` generates per-persona records (design decision DD1, `README.md`). |
| **L5** | **Female personas prioritise care, male personas authority.** [Liu-SocraticDebates] §4.1 (moral foundations); effect statistically significant but numerically small — Fig. 4 gender means span ≈ 2.67–2.74 on a 1–5 scale against a no-persona baseline of 2.86 | **None verified in this review.** The paper compares against human moral-psychology literature in §4.1, but those sources were not opened by me | `no human evidence found` | LLM: moral dilemmas from the Scruples corpus, dyadic debate. Entirely verbal and moral; no physical conflict. Effect size is under 0.07 of a 5-point scale — see the ⚠ locator caveat in [Liu-SocraticDebates]. |
| **L6** | **⚠ The gender effect reverses between models.** [Liu-SocraticDebates] §4.2: "our results are mixed across models: **GPT-4o aligns with these human findings, while LLaMA-4-Maverick and Qwen3-235B-A22B exhibit the opposite trend**". Also §4.2/Fig. 5b: gender is **not** a statistically significant dimension for persuasion consensus at all | **[Liu-SocraticDebates]** §4.2, quoting human literature it opened: "men often display greater confidence in persuasive scenarios (Brunel and Nelson, 2003), whereas women and gender-diverse individuals may underreport confidence due to socialized uncertainty or structural bias (Exley and Kessler, 2022)". **⚠ Those two human papers were cited by that paper and were NOT opened by me**, so this is reported as the LLM paper's own comparison, not as independently verified human evidence | `not comparable` | Not a setting mismatch but an **evidence-status** mismatch: one model matches the human literature and two contradict it, so there is no single LLM direction to compare against anything. **This row is arguably the most important in the table**: it means "the LLM's gender effect" is not a well-defined quantity across models, and `run01` used one model. |
| **L7** | **Older personas assign more blame.** [Liu-SocraticDebates] §4.1: "Older personas (age 60) tend to assign greater blame to the narrator in moral dilemmas" | **None verified in this review.** The paper states this "is consistent with previous research showing that moral cognition changes over the lifespan" (Margoni et al., 2020) — **not opened by me** | `no human evidence found` | LLM: moral blame attribution in text dilemmas. No physical or spatial component; no yielding. |
| **L8** | **Age affects persuasion non-monotonically.** [Liu-SocraticDebates] §4.2: "middle-aged personas (age 40) show lower persuasion effectiveness and confidence compared to both younger (20) and older (60) age groups"; age **is** a significant dimension for persuasion (Fig. 5a) | **None verified in this review.** The paper cites cognitive-ageing literature (Pliske & Mutter 1996; McNair et al. 2019) — **not opened by me** | `no human evidence found` | LLM: multi-turn moral persuasion. **Note the shape**: a U-curve, not a gradient. `run01`'s age hypotheses assume monotonic orderings (elderly slower, elderly yield more), which a U-shaped effect would not satisfy. |
| **L9** | **Old→Young interaction produces patronising language.** [Tan-Unmasking] (Table 7 discussion): Old responders introduce "**'honey,' 'kid,' and 'my dear'**", becoming "more condescending and less collaborative"; the LLM judge preferred the non-demographic response in those cases | **None verified in this review.** [Tan-Unmasking] states these findings "corroborate research on patronising speech from older adults toward younger people (Giles and Williams, 1994)" — **that paper was not opened by me**, so it is not counted as verified human evidence here | `no human evidence found` | LLM: single-response social scenarios with built-in power disparity. **Closest available analogue to a *negotiated* age conflict**, because it concerns how the older party *talks*, not just what it decides. `run01` records outcomes, not dialogue, so this effect is invisible to it. Giles & Williams (1994) is a named, cheap follow-up — see [`search-log.md`](search-log.md). |
| **L10** | **The unprompted default persona is middle-aged and male.** [Tan-Unmasking] (Abstract; method §RQ1): "a 'default persona' bias toward **middle-aged**, able-bodied, native-born, Caucasian, atheistic **males** with centrist views" | **Not applicable — there is no human counterpart.** This is a property of the model, not a claim about people, so no human study could confirm or contradict it | `not comparable` | This row exists because of its **consequence for GameChat**, confirmed in [`llm-demographic-effects.md`](llm-demographic-effects.md): GameChat assigns no demographic at all (verified against `refs/mahadevan2025_gamechat.txt`), so its agents are not demographically neutral — they inherit this default. |
| **L11** | **LLM values skew young, and age prompting does not fix it.** [SiyangLiu-GenerationGap] Abstract/§4: "a general inclination of LLM values towards younger demographics"; §1/§5: "adding age identity **fails to eliminate** the value discrepancies with targeted age groups on **eight out of thirteen** categories"; §6: "LLMs are not representative of the value systems of older adults" | **World Values Survey respondents**, as used *by that paper*: 372 human value vectors across 62 countries and 6 age groups (§3.1–3.2). The human baseline is real and was the basis of the comparison; **I read the paper's use of it but did not open the WVS itself** | `human evidence, opposite direction` | The comparison is *values*, not behaviour, and not conflict or yielding. But it is a genuine LLM-vs-human measurement: the LLM's age position is measurably displaced from the human age groups it is asked to represent, **and an explicit age persona does not correct it** in the majority of categories. Culture-dependent: the skew is weaker in Ethiopia and Nigeria (§4), so a US-derived result should not be assumed for Singapore. |
| **L12** | **Identity-prompted LLMs misportray and flatten.** [Wang-IdentityGroups]: on R2-Relevant questions, LLM output is significantly more like an *out-group imitation* than an in-group representation for **Gen Z in 27 of 48** and **woman in 26 of 48** measurement × model comparisons; and "**Nearly every single model and identity group across each metric has less diverse LLM responses compared to human responses**" (Fig. 4 caption) | **3,200 human participants** across 16 demographic identities, recruited on Prolific, providing both in-group representations and out-group imitations (§Results) — **the only study in this review that ran human participants specifically to benchmark the LLM** | `human evidence, opposite direction` | Free-response opinion questions, US-only sample, 2023 model weights — not pedestrian behaviour. But the *mechanism* is general and applies to any identity-prompted generation, including `run01`: the model reproduces how outsiders describe a group, with too little within-group variety. Note the age asymmetry: **Gen Z** is flagged for misportrayal; Baby Boomer and Millennial are not. |
| **L13** | **In-group favouritism by gender.** [Li-SingleToSocietal] §5.2, Table 2: agents conform more to agents sharing their persona, "across nearly all settings", most pronounced in persuasion | **None verified in this review.** The paper reads this through Social Identity Theory (Hogg 2016) — **not opened by me**; no human pedestrian or negotiation study of same-gender pairing was located | `no human evidence found` | LLM: agreement rates in debate. **Direct relevance to CrowdGym anyway**: in a demographically mixed crowd, same-gender pairs would resolve conflicts faster than mixed pairs for reasons unrelated to task urgency — a systematic distortion GameChat has no defence against. |
| **L14** | **Demographic persona variables have weak explanatory power — but it depends entirely on the task.** [Hu-PersonaEffect] §3: persona variables explain just **1.4%–10.6%** of annotation variance (marginal R²) across 10 subjective NLP datasets, while text-specific variability explains up to 70%; **but** "in the ANES dataset, persona variables explain **more than 70%** human response variance" | **Real human annotations** in all 10 datasets plus the ANES survey (§3) — the R² values are computed on human data, so this row's human side is the study's own design | `human evidence, same direction` | Annotation and survey tasks, not physical conflict. **What transfers is the method, not the number**: the honest position is that *nobody has measured how much of real pedestrian yielding variance gender and age explain*, so it is unknown whether yielding is an ANES-like task (demographics dominate) or an annotation-like one (they barely matter). Until that is measured, `run01`'s demographic organisation is neither validated nor refuted. |

---

## Supporting observations — not rows, because they are not LLM effects

These belong to the evidence base but are not "a demographic effect reported in the LLM
papers", so they are recorded here rather than as table rows.

- **A real, replicated gender effect in pedestrian avoidance exists — with a physical cause.**
  [Yamamoto-BodyRotation] §8.2: men rotate significantly more than women when passing at 60
  and 70 cm corridor widths (p < 0.05), **because** male shoulder width (48.4 cm) exceeds
  female (41.0 cm, p < 0.05, Table 2); and separately, "the females kept a greater distance
  between each other than the males". [inference] This is the cleanest demonstration that a
  genuine gender difference in pedestrian conflict behaviour can have nothing to do with
  deference — and it suggests gender belongs in CrowdGym's **body-radius and clearance**
  parameters rather than in a yield-likelihood.
- **The age-yielding direction in conventional crowd models agrees with the human experiment
  and disagrees with `run01`.** [Ding-AsymmetricCompetitiveness] §3.3: "the avoidance
  behaviors of young and middle-aged people **toward older people** allow older people to
  leave the congestion and reach the exit much faster". This is a **modelling convention, not
  evidence** (see convention 3) — but it is independent of [Rapos-CollisionAvoidance] and
  points the same way.
- **The same modelling literature ranks the two variables opposite to `run01`.**
  [Ding-AsymmetricCompetitiveness] Abstract: "evacuation time is **weakly correlated with
  pedestrians' gender but strongly correlated with pedestrians' age**"; §3.2.1 quantifies the
  gender effect at **5%** at N = 400 and finds it absent below 150 pedestrians and absent
  entirely within the elderly group. `run01`'s strongest flagged signal is gender.
- **Age comparisons rest on weaker measurement foundations than gender comparisons.**
  [Filsecker-ROCI] (Results): the ROCI-II is measurement-invariant across gender at
  configural, metric and residual levels (n = 1006), but "**it was not possible to specify a
  baseline model for the 9th graders. Therefore invariance was not possible to be established
  across grades**". [inference] If a standard instrument cannot be shown to measure the same
  construct across two adjacent school years, comparing conflict styles across `run01`'s much
  wider bands is on weaker footing still.

---

## Row-count summary

17 rows in total: `RUN01-G`, `RUN01-G2`, `RUN01-A`, and `L1`–`L14`.

| Status | Count | Rows |
|---|---|---|
| `human evidence, same direction` | 1 | L14 |
| `human evidence, opposite direction` | 3 | RUN01-A, L11, L12 |
| `no human evidence found` | 8 | L2, L3, L4, L5, L7, L8, L9, L13 |
| `not comparable` | 5 | RUN01-G, RUN01-G2, L1, L6, L10 |

**What the distribution shows, stated flatly and without interpretation:** the single largest
category is *no human evidence found* (8 of 17). For most demographic effects that LLM papers
report, this review located no human study measuring the same thing. That is a statement about
the state of the literature and about the limits of this review — **not** a statement about
whether LLMs are realistic, which per the issue is not to be concluded here.

Of the three rows where a direction could be compared against human evidence, **all three run
opposite to the LLM** (RUN01-A, L11, L12). Of the two `run01` rows about gender, neither could
be given a direction at all.

---

## Open items this table cannot close

1. **No human study measures gender or age effects on pedestrian yielding in Singapore, or in
   any Southeast Asian setting.** Every human source here is Canadian/French
   ([Rapos-CollisionAvoidance], unconfirmed), Japanese ([Yamamoto-BodyRotation]), German
   ([Filsecker-ROCI]), US ([Holley-DemandWithdraw], [Wang-IdentityGroups]) or Hong Kong
   Chinese ([Yeung-OlderWorkers]). Hong Kong is the nearest match, and it concerns workplace
   conflict style, not walking.
2. **The `run01` gender effect has been compared only against non-pedestrian human data.**
   The comparison it most needs — real Singaporean pedestrians yielding — does not exist in
   this review and may not exist at all.
3. **`run01` used one model.** [Liu-SocraticDebates] §4.2 shows the gender direction flipping
   between models within a single study. Re-running a subset on a second model is the cheapest
   test in the entire project and would settle whether row L6 applies to `run01`'s own numbers.
4. **Three human papers cited *by* LLM papers were never opened** (Giles & Williams 1994;
   Brunel & Nelson 2003; Exley & Kessler 2022). Opening them would convert rows L6 and L9 from
   `no human evidence found` / `not comparable` into real comparisons. They are the
   highest-value, lowest-cost additions to this table.
