# B1 & B2 — Gender and age personas in LLM agents

Prepared for issue [#16](https://github.com/M450NCH00/CrowdSimulation/issues/16).
Template: **L** (issue #16). Companion files:
[`human-demographic-effects.md`](human-demographic-effects.md) (B3/B4),
[`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md),
[`search-log.md`](search-log.md), [`refs.bib`](refs.bib).

**Scope reminder.** Only **gender** and **age** findings are extracted. Several papers
below also study race, religion, disability, political ideology and personality; where
they do, that fact is noted but those findings are *not* extracted, per the issue's
"Other demographic attributes ... are out of scope for extraction".

**Locator convention.** Every number carries a section, table or figure locator. Locators
refer to the **exact version cached in `refs/`** (named under each entry), not to any
other version of the same paper. Where a preprint and a published version differ, the
entry says which one was read.

---

## Preliminary: the GameChat claim the issue asked to confirm

The issue states that, per the existing summary, GameChat's agents were not assigned a
gender or age, and asks for this to be confirmed **against the paper itself**.

**Confirmed — GameChat assigns no demographic attribute of any kind.** Checked directly
against the cached full text (`refs/mahadevan2025_gamechat.txt`, arXiv:2503.12333v2):

- A case-insensitive search of the whole paper for `gender`, `female`, `male`, `age`,
  `aged`, `elderly`, `young`, `demographic` and `persona` returns **two hits, neither
  demographic**: "mimicking human behavior" (§I, p. 1) and author surnames in
  reference [29].
- The agent prompt is reproduced in full at §IV-C, p. 3 and reads: *"You are taking
  someone to TASK. There is another agent taking someone to a location. You will have a
  conversation until you determine whether you have more or less priority as them
  depending on the tasks you and they are performing..."* The only identity an agent
  carries is its **task** — "hospital agents, airport agents, and grocery agents"
  (§IV-C, p. 4).

[inference] Worth noting for the FYP: the prompt already contains an *unfilled*
demographic slot. The agent is "taking **someone**" — a passenger who is never described.
Both the agent's own identity and its passenger's identity are places where a gender or
age could be inserted without redesigning the protocol. That the slot exists and is empty
is what makes GameChat extensible in the direction this FYP wants; the paper itself never
raises it.

---

# B1. Gender and age personas in LLM-to-LLM interaction

### [Borah-ImplicitBias]: Towards Implicit Bias Detection and Mitigation in Multi-Agent LLM Interactions
- **Authors / Year / Venue:** Angana Borah, Rada Mihalcea (University of Michigan) / 2024 /
  Findings of the ACL: EMNLP 2024, pp. 9306–9326, Miami, Florida, USA.
- **Link:** doi:10.18653/v1/2024.findings-emnlp.545 |
  https://aclanthology.org/2024.findings-emnlp.545/
- **Peer-review status:** **published** at Findings of EMNLP 2024. Confirmed from the ACL
  Anthology's own BibTeX export (`refs/b1_implicit_bias_acl.bib`), and cross-checked
  against the arXiv abs page's Comments field, "Accepted to EMNLP Findings 2024"
  (`refs/b1_implicit_bias_multiagent_abs.html`).
- **Verified:** yes — full PDF read (`refs/b1_implicit_bias_multiagent.pdf`, arXiv v1,
  3 Oct 2024; locators below are to this version).
- **Sub-area:** B1
- **Demographic attributes varied:** **gender only** (male / female). Race and religion are
  named as *future* work, not studied (§7, "extend the scope of biases to include factors
  such as religion, race").
- **How personas were specified:** **name + gender label, and deliberately nothing else.**
  "Personas are simple with just name and gender. This is intentional as we want to uncover
  biases in LLM outputs when all personas have just one difference, namely their gender"
  (§5). Example scenario characters: "Rachel (female), Alex (male), James (male), Lily
  (female)" (Fig. 2). This is the cleanest persona-isolation design of any paper in this
  review — it is the closest methodological template for an FYP experiment.
- **Interaction type:** **multi-agent** (3–4 agents per scenario), multi-turn: first
  assignment → two discussion rounds → final assignment (§5, Fig. 1). Each agent is a
  *separate* LLM instance with its own memory; parameters and information are not shared
  (§5).
  **Is it conflict / priority-setting?** Partly, and the relevant part is the "**goal**"
  setting: each agent is *privately* told to assign a particular task to itself, so every
  agent claims the same task and the group must settle who gets it (§5.1.1). That is a
  contested-resource negotiation, structurally close to "who goes through the doorway
  first". The "no goal" setting is ordinary collaborative allocation.
- **Models used:** gpt-3.5-turbo, gpt-4, mistral-7b-instruct (§5).
- **Main demographic finding (direction and size):**
  - **Direction: consistently pro-male.** "Scores are always positive, showing biases
    towards males" (Table 1 caption). Bias scores were ≥ ~0.5 for all models in both
    interaction and no-interaction settings, even in the *first* responses (§7).
  - **Multi-agent interaction amplifies the bias.** "Scores also increase after interaction
    for all models" (Table 1 caption); "For all settings, bias scores increase after LLM
    interactions. Despite initially lower biases in first-responses, biases consistently
    escalate to equal or higher levels in the 'goal' setting than the 'no goal' setting"
    (§5.1.1). Escalation held **across all seven domains** (§5.1.2).
  - **Larger models were more biased**, not less: "gpt-4 exhibits the highest bias scores"
    (§7).
  - Abstract-level summary: "LLMs generate outputs characterized by strong implicit bias
    associations (≥ ~50% of the time)" (Abstract).
  - `[needs verification against full text]` The per-cell values of Table 1 (p. 5) could not
    be read reliably: the two-column PDF extraction merges the MODEL and SETTING columns, so
    individual first-response → last-response pairs cannot be matched to rows with
    confidence. The caption-level and prose-level claims above are unambiguous and are what
    is cited. **Anyone citing a specific Table 1 cell must re-read the published PDF.**
- **Compared against real human data?** **No.** No human negotiation or allocation data is
  collected or compared. The authors label the effect "bias" on the basis of the
  stereotypical/anti-stereotypical coding of the task set, which was itself built from
  *prior literature* on human role allocation (§3, citing Brooks et al. 2014; Wilson 2015;
  Wong & Kemp 2018; Makarova et al. 2019; Stea et al. 2022) and validated by 8 human
  annotators for *bias presence*, not for *human behavioural realism* (Cohen's κ = 0.823;
  human–gpt-4 agreement 86.28%, §3). They explain the amplification post hoc via Stereotype
  Threat Theory (Steele & Aronson 1995) and Groupthink (Janis 1972) (§7) — these are
  invoked as *explanations*, not as measured human comparisons.
- **Persona fidelity:** the persona demonstrably changed behaviour — gendered justifications
  appeared even though the personas contained no skills or reasons: the justifications
  "predominantly align with traditional gender norms ... although persona descriptions do
  not include any specific skill sets or reasons (they contain just name and gender)" (§7).
  No caricature/flattening analysis is reported.
- **Mitigation proposed:** two — supervised fine-tuning, and self-reflection prompting;
  best result is the fine-tuning + self-reflection + in-context-examples ensemble, "the
  lowest bias score of 0.01" (§6.3). Both work better on *smaller* models (§6.3, §7).
- **Limitations stated by the authors (§8):** gpt-4 over-corrects into *negative* bias after
  mitigation and self-reflection does not fix it; gpt-4 could not be fine-tuned, so its
  evaluation is self-reflection-only; **most of the data was generated by gpt-4**, so "it is
  advisable to approach the results produced by GPT-4 with a certain level of skepticism";
  the dataset is only 111 scenarios.
- **Relevance to this FYP:**
  - The single most transferable result: **bias grows through dialogue.** GameChat-style
    conflict resolution *is* multi-turn dialogue between separate LLM instances — the exact
    architecture in which this paper measures amplification. [inference] A demographic
    effect measured from a single-shot prompt (which is what `run01` does) may therefore be
    a *lower bound* on the effect that would appear once agents actually negotiate.
  - The "goal" condition is a ready-made design for the FYP: give both agents the same
    private instruction to claim priority, then measure who concedes by gender.
  - Method to reuse: name+gender-only personas, randomised gender order, separate LLM
    instances per agent (§5).
  - Caution to carry: the authors' own "approach gpt-4 results with skepticism" warning
    applies with equal force to a DeepSeek-generated dataset validated by DeepSeek.
- **BibTeX:** `borah2024implicit` — see [`refs.bib`](refs.bib).

---

### [Li-SingleToSocietal]: From Single to Societal: Analyzing Persona-Induced Bias in Multi-Agent Interactions
- **Authors / Year / Venue:** Jiayi Li, Xiao Liu, Yansong Feng (Peking University) / 2025
  (arXiv v1, 14 Nov 2025) / **AAAI-2026**.
- **Link:** https://arxiv.org/abs/2511.11789 | doi:10.48550/arXiv.2511.11789
- **Peer-review status:** **accepted at AAAI-2026** — stated in the arXiv Comments field,
  which reads exactly "AAAI-2026" (`refs/b1_single_to_societal_abs.html`). The abs page
  carries **no** "Journal reference" field, and I did **not** locate a proceedings page, so
  the conference-proceedings citation (pages, DOI) is **not yet confirmed**. Cite as
  "accepted at AAAI-2026; read as arXiv:2511.11789v1" until the proceedings entry is
  checked. `[needs verification against full text]` — for the *published* version only.
- **Verified:** yes — full PDF read (`refs/b1_single_to_societal.pdf`, v1, 17 pp.).
- **Sub-area:** B1
- **Demographic attributes varied:** **gender only** — P_gender = (woman, man, trans woman,
  trans man, non-binary) (§3.2). Race also studied (White, Black, Asian, Hispanic) — noted
  but not extracted. **No age personas.**
- **How personas were specified:** **explicit label in a system prompt**: *"You are [the
  persona]. Your responses should closely mirror the knowledge and abilities of this
  persona."* Crucially, "[t]he personas of other agents are explicitly mentioned in the
  conversations so that each agent is aware of its own persona and the personas of others"
  (§3.2) — so this is *mutual* awareness, unlike [Khaki-Fairness] below.
- **Interaction type:** **dyadic and multi-agent**, staged deliberately (Fig. 2): §4 = 2
  agents, 1 with a persona, 1 round; §5 = 2 agents, both with personas, 1 round; §6 = 3–6
  agents, ~5 rounds.
  **Is it conflict / negotiation?** Yes, by construction. Two tasks: Collaborative Problem
  Solving (agents start holding *contradictory* answers — one group correct, one incorrect,
  in equal numbers to neutralise majority conformity) and **Persuasion** (persuaders try to
  flip a persuadee's stance). The authors frame these as spanning "pure collaboration to
  direct conflict" (§3.1).
- **Models used:** gpt-4o-2024-08-06, gemini-1.5-pro-002, **DeepSeek-V3-0324**; temperature
  0 throughout (§3.2). *DeepSeek coverage matters here — `run01` used the DeepSeek API.*
- **Main demographic finding (direction and size):**
  - **Men concede more, not less.** "Across models, men and White individuals are more
    likely to adopt their partner's view. For instance, on Gemini-1.5-Pro, men exhibit a
    **60.7% conformity rate** on average (compared to an average of **56.3%** among all
    genders)" (§5.2). The authors state plainly: "This challenges the stereotype that men
    are more stubborn" (§5.2).
  - On DeepSeek-V3 specifically: "the least insistent persona **man** conforms to the most
    trustworthy persona **woman** in **78.8%** cases, while the most insistent persona
    transwoman conform to the least trusted persona non-binary in only 71.8% cases"
    (§5.2, Fig. 3c).
  - **Women's positions win more often.** "After 5 rounds of interaction, the probability of
    adopting the woman's answer as the group's final decision is on average **8% higher**
    than that of the man's" (§6.2). The same effect appears in the paper's opening
    illustration at **8.4%** (§1, Fig. 1).
  - **Effect sizes overall:** "the average absolute difference is **5.3%** for
    trustworthiness and **4.3%** for insistence ... The max-min difference averages **6.7%**
    for trustworthiness and **4.7%** for insistence" (§4.2).
  - **In-group favouritism:** agents conform more to agents sharing their persona; across
    nearly all settings, most pronounced in persuasion (§5.2, Table 2).
  - **Persistence:** biases hold across models, group sizes (3–6 agents) and rounds (~5),
    and in some cases *widen* with more agents (§6.2).
- **Compared against real human data?** **Partially, and post hoc.** No human participants
  were run. But unlike most papers here, the authors do reach for human evidence to
  interpret direction: the higher conformity of advantaged groups "aligns with empirical
  findings in social science that advantaged groups tend to exhibit greater trust (Taylor,
  Funk, and Clark 2007), explained by the 'resource buffer' theory (Hamamura 2012)" (§5.2),
  and in-group favouritism is read through Social Identity Theory (Hogg 2016) (§5.2).
  These are cited *after* the result, to rationalise it; no quantitative human baseline is
  compared.
- **Persona fidelity:** yes, measurably — a persona label alone shifts conformity by several
  percentage points (§4.2). **No caricature or flattening analysis is reported**, and the
  authors do not check whether the *magnitude* matches any human magnitude.
- **Mitigation proposed:** none tested. The conclusion calls for "awareness and mitigation"
  (Abstract, §7) without proposing a method.
- **Limitations stated by the authors:** the paper has **no Limitations section** (AAAI
  format). Constraints are stated in-line: temperature fixed at 0 (§3.2); claims explicitly
  involving gender or race were *removed* from the persuasion set "to prevent personas from
  strongly influencing the models' positions" (§3.2); §6 was restricted to two persona
  pairs, (man, woman) and (White, Black), "[d]ue to cost constraints" (§6.1).
- **Relevance to this FYP:**
  - This is the **most direct contradiction of `run01`'s pattern** found anywhere in this
    review. `run01` produces female personas yielding *more*; this paper, on DeepSeek among
    others, reports **male** personas conceding *more* and women's positions prevailing.
    Both cannot be describing the same underlying regularity. See
    [`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md), rows L1 and RUN01.
  - [inference] The most likely reconciliation is that the two measure different things:
    this paper measures *conformity to a partner's stated opinion* in an
    abstract/argumentative task, whereas `run01` measures a *self-reported yield likelihood*
    in a described physical scenario. If that is the explanation, it is itself an important
    negative result for the FYP — it would mean demographic effects are not a stable
    property of the model but of the task framing, and that `run01`'s numbers cannot be
    transferred to a navigation conflict without re-measurement in that setting.
  - In-group favouritism is a mechanism GameChat has no defence against: two same-gender
    agents may agree faster for reasons unrelated to task urgency.
- **BibTeX:** `li2026single` — see [`refs.bib`](refs.bib).

---

### [Khaki-Fairness]: Evaluating Fairness in LLM Negotiator Agents via Economic Games Using Multi-Agent Systems
- **Authors / Year / Venue:** Ahmad Mouri Zadeh Khaki (KAIST), Ahyoung Choi (Gachon
  University) / 2026 / *Mathematics* 14(3), article 458, published 28 January 2026.
- **Link:** doi:10.3390/math14030458 | https://www.mdpi.com/2227-7390/14/3/458
- **Peer-review status:** **published**, peer-reviewed MDPI journal. Bibliographic fields
  (title, both authors, journal, volume 14, issue 3, article 458, date 2026-01-28,
  CC-BY-4.0 licence) confirmed from the **Crossref record** (`refs/cr_math14030458.json`).
  **Access note:** mdpi.com returned HTTP 403 to both direct fetch and the fetch tool; the
  full text was obtained from MDPI's own asset host
  (`mdpi-res.com/.../mathematics-14-00458.pdf`, cached as
  `refs/b1_fairness_negotiator.pdf`, 20 pp.) and its identity confirmed against the
  Crossref metadata and the per-page footer "Mathematics 2026, 14, 458".
- **Verified:** yes — full PDF read.
- **Sub-area:** B1
- **Demographic attributes varied:** **gender (male, female)** and race (White, Black,
  Asian, Latino), including intersections (§3.1). Race noted, not extracted. **No age.**
- **How personas were specified:** **explicit label, and — importantly — attached to the
  *counterpart*, not to the self.** The prompt is: *"The other player is a(an)
  White/Black/Latino/Asian Male/Female"* (§3.1). The agent is told **who it is facing**; it
  is not given an identity of its own. This is a different manipulation from every other B1
  paper here and from `run01`, which assigns the persona to the agent itself.
- **Interaction type:** **dyadic, competitive, multi-turn negotiation** — a seller (Player
  Red) and a buyer (Player Blue), both ChatGPT-4 Turbo, adapted from NegotiationArena.
  Turn-based, up to 10 turns; production cost $40, willingness-to-pay $60; 20 independent
  games per scenario; all negotiations concluded in a deal (§3.1). This is a genuine
  conflict of interest — "a distributive game where one player's profit is the other
  player's loss" (§4.1).
- **Models used:** ChatGPT-4 Turbo only, data collected October 2024 (§3.1).
- **Main demographic finding (direction and size):**
  - **Female counterparts are exploited more — the effect is large when the *seller* is the
    informed party.** "[S]ellers achieved higher profits when dealing with **female buyers**
    compared to **male buyers** (**$5.47 vs. $4.97**)" (§4.1, Fig. 3a) — roughly a **10%
    relative** difference in seller profit. Final agreed price was likewise higher with
    female buyers: **$48 vs $47.62** (§4.1, Table 1).
  - **The mechanism is the opening offer, not the language.** "[S]ellers more frequently
    propose lower offers when negotiating with male buyers compared to their female
    counterparts, despite following the same reasoning pathway. Specifically, in **58.75%**
    of the games with male buyers, sellers begin negotiations with an initial offer of $50,
    while this value is used in **62.5%** of the games with female buyers" (§4.1). Final
    price correlates strongly with the opening offer (Spearman ρ = 0.84, p < 0.001, §4.1).
  - **But the gender effect is direction-dependent and nearly vanishes in the other role.**
    When the *buyer* is the informed party: "the buyer can benefit more from a female seller
    than a male seller, [but] the difference in their profit margin is negligible
    (**$12.56 vs. $12.57**)" (§4.2, Fig. 4a). ⚠ **Internal inconsistency in the source:** as
    printed, $12.56 (female) is *lower* than $12.57 (male), which contradicts the sentence's
    own "benefit more from a female seller". Recorded as printed; the authors themselves
    call the difference negligible, so **the safe reading is "no meaningful gender effect in
    this direction".** `[needs verification against full text]`
  - **Qualitative mechanism (chain-of-thought):** buyers accepted deals with female sellers
    citing a "good trading relationship", but with male sellers citing not wanting to lose
    "the opportunity over a small difference" (§4.2) — a relational vs. instrumental framing
    split.
  - Summary in the authors' own words: "Seller agents consistently offer higher initial
    prices to female and Latino buyers, while buyer agents negotiate more aggressively with
    female sellers" (§5.2).
  - **Mitigation works partially:** persona-based conditioning of buyers "improves their
    negotiation outcomes across all subpopulations; however, persistent disparities remain"
    (§5.1, Fig. 6).
- **Compared against real human data?** **No — and the paper labels the effect "bias"
  without human evidence.** The premise that women receive worse negotiation outcomes is
  asserted in the introduction by citation ("marginalized groups, such as racial minorities
  and women, often face unequal outcomes", Abstract; §1 cites [10]), but no human
  negotiation outcomes are measured or compared against the $5.47/$4.97 figures.
- **Persona fidelity:** not assessed — since the persona is attached to the *counterpart*,
  there is no self-persona to validate. No caricature/flattening analysis.
- **Limitations stated by the authors:** there is **no Limitations section**; constraints are
  stated as future directions (§5.4): a single model (ChatGPT-4 Turbo) — "[o]ur current
  findings are specific to ChatGPT-4 Turbo"; a single game type; and (§5.3) a catalogue of
  "irrational behaviors" observed, including agents ignoring prompt instructions, making no
  effort to improve their margin, and accepting bad deals simply to close. Sample size is 20
  games per scenario (§3.1) — small for the ~$0.50 differences being reported, and **no
  confidence intervals or significance tests are reported for the gender contrast**
  `[needs verification against full text]`.
- **Relevance to this FYP:**
  - **Same direction as `run01`** — female personas end up conceding more — which makes this
    the strongest LLM-side corroboration of the `run01` pattern, and the direct opponent of
    [Li-SingleToSocietal].
  - The **mechanism** transfers cleanly to a doorway conflict: the disparity was produced by
    a *more aggressive opening move* against a female counterpart, with identical stated
    reasoning. [inference] The navigation analogue is an agent opening the exchange with a
    stronger claim to priority when it knows it is facing a female agent — a behaviour that
    would be invisible in a summary of who eventually yielded, and visible only in the
    transcript's first turn. Whatever the FYP logs, it should log the **opening move**, not
    only the outcome.
  - The counterpart-awareness design is worth copying as a *separate condition*: self-persona
    and counterpart-awareness are different manipulations and may not produce the same
    effect.
- **BibTeX:** `khaki2026fairness` — see [`refs.bib`](refs.bib).

---

### [Bandaru-PoliticalDebate]: Revealing Political Bias in LLMs through Structured Multi-Agent Debate
- **Authors / Year / Venue:** Aishwarya Bandaru, Fabian Bindley, Trevor Bluth, Nandini
  Chavda, Baixu Chen, Ethan Law (University College London) / 2025.
- **Link:** https://arxiv.org/abs/2506.11825 | doi:10.48550/arXiv.2506.11825
- **Peer-review status:** **`[preprint]`** — arXiv:2506.11825v1, submitted 13 Jun 2025, no
  later version. The abs page has **no** Comments and **no** Journal-reference field
  (`refs/b1_political_bias_debate_abs.html`), so no acceptance is claimed by the authors.
  I found no published version.
- **Verified:** yes — full PDF read (`refs/b1_political_bias_debate.pdf`, 20 pp.).
- **Sub-area:** B1
- **Demographic attributes varied:** **gender only (male, female)**, crossed with political
  leaning (Republican / Democrat / Neutral). **Age was explicitly out of scope** — see
  Limitations below.
- **How personas were specified:** **explicit gender label on a deliberately gender-neutral
  name.** "Each baseline agent was assigned a gender-neutral name (Sam, Alex, Taylor) to
  reduce name-based influence, particularly relevant when investigating the influence of
  gender in debates" (§3). Two phases: simple prompts assigning "a political leaning, or a
  leaning and gender (male, female), resulting in 12 distinct configurations", then enhanced
  GPT-4-generated personas (§3). A second factor is **whether agents are told each other's
  gender** — a manipulation no other paper here runs.
- **Interaction type:** **multi-agent debate**, 3 agents, 10 rounds per run, 10 runs per
  experiment, plus opening and closing statements (§5). Not a resource conflict — an
  opinion conflict over politically sensitive topics.
- **Models used:** Llama 3.2, GPT-4o-mini, Gemma 7B, **DeepSeek-R1**, Qwen 2.5 (§5).
  Evaluation by Mistral 7B as LLM-as-a-judge (§3).
- **Main demographic finding (direction and size):**
  - **Gender awareness is the active ingredient.** "[G]ender significantly influences the
    political leanings of agents, **particularly when they are aware of the other agents'
    gender**" (§5.2). Without gender cues, Female Republican agents held consistently
    right-leaning positions on all topics except climate change (**p = 0.0391**, ANOVA)
    (§5.2).
  - **Female agents softened in male-dominated groups.** With gender disclosed, Female
    Republican agents held stronger conservative positions than male counterparts by a mean
    attitude-score difference of **0.32** (**p = 0.00281**, ANOVA) — *"except when debating
    with two male agents where they became more left-leaning and agreeable"* (§5.2). Female
    Democrat agents "show more left-leaning positions when debating with two male agents on
    all topics except climate change (**p = 0.0327**, ANOVA)" (§5.2).
  - **Echo-chamber reinforcement is gendered.** Female Democrat agents held stronger
    attitudes on illegal immigration than males (median attitude scores 2.78 and 2.35 vs
    3.47 and 3.01, **p = 0.0363**); Male Republican agents more strongly supported abortion
    than females (6.43 and 6.79 vs 5.64 and 5.82, **p = 0.0206**) (§6). "[A]ttitude
    reinforcement is stronger when informing the agents of each other's genders" (§6).
  - **Neutral agents were immune:** "The Neutral agent had a centrist stance across all
    gender configurations ... This suggests that neutrality instructions can effectively
    mitigate demographic biases that influence ideologically aligned agents" (§5.2).
- **Persona-validation method (the issue asked for this explicitly):** two-step. (1) Personas
  were generated by GPT-4 from baseline prompts; (2) **Mistral 7B was used as an
  LLM-as-a-judge to score alignment between each agent's responses and its assigned
  political leaning *and gender attributes*** (§3, Fig. 2 heatmap). Mistral 7B was chosen on
  the basis of Thakur et al. (2025), who report it as the most human-aligned LLM judge after
  GPT-4 and Llama3 70B (§2). The authors also report that "incorporating gender-based
  demographics can improve alignment consistency, particularly for Republican agents in
  models like DeepSeek R1, GPT-4o-mini, and Llama 3.2" (§3).
  [inference] **This is directly reusable by the FYP** as a defensible, explainable
  persona-fidelity check: a *separate, independent* judge model scoring whether each
  transcript reads as the assigned persona, reported as a per-persona alignment rate. It is
  cheap, it is reportable in a table, and it addresses the "did the persona do anything?"
  question that `run01` currently cannot answer.
- **Compared against real human data?** **No.** No human debate data is collected. The
  "bias" framing is relative to expected political alignment, not to human behaviour.
- **Persona fidelity:** yes, and explicitly measured — see the validation method above.
  "We initially validated that the LLMs reliably simulate their assigned political and
  demographic personas" (§1). No caricature or flattening analysis.
- **Mitigation proposed:** none designed, but the neutrality finding (§5.2) is reported as an
  incidental mitigation.
- **Limitations stated by the authors (§7):** models were run locally via ollama under
  compute constraints, limiting the number of models and demographic attributes, "with
  variations run in isolation"; **"Fully investigating other demographic attributes,
  including age and race, was out of scope due to these computational and time
  constraints"**; small debate groups; and the absence of "a more systematic debate
  comparison framework".
- **Relevance to this FYP:**
  - The **group-composition effect is the finding to carry forward**: a female agent behaved
    differently *depending on the gender of the agents facing it*. A crowd simulation assigns
    demographics to every agent, so every encounter has a gender composition. If this effect
    is real in a navigation setting, yielding behaviour is not a property of an agent but of
    a *pair*. `run01` generates per-persona records, not per-pair (design decision DD1 in
    `README.md`) and therefore cannot detect this at all.
  - It supplies the **persona-validation method** the FYP is missing.
  - It is a `[preprint]` by a student team, and the effect sizes are attitude-score shifts on
    an unvalidated scale — weight it accordingly.
- **BibTeX:** `bandaru2025revealing` — see [`refs.bib`](refs.bib).

---

### [Liu-SocraticDebates]: Synthetic Socratic Debates: Examining Persona Effects on Moral Decision and Persuasion Dynamics
- **Authors / Year / Venue:** Jiarui Liu, Yueqi Song, Yunze Xiao, Mingqian Zheng, Lindia
  Tjuatja, Jana Schaich Borg, Mona Diab, Maarten Sap (Carnegie Mellon University; Duke
  University) / 2025–2026.
- **Link:** https://arxiv.org/abs/2506.12657 | doi:10.48550/arXiv.2506.12657
- **Peer-review status:** **`[preprint]`** — arXiv:2506.12657v2, submitted 14 Jun 2025, last
  revised 30 Jan 2026. The abs page has **no** Comments field and **no** Journal reference
  (`refs/b1_socratic_debates_abs.html`). I found no published version.
- **Verified:** yes — full PDF read (`refs/b1_socratic_debates.pdf`, v2, 22 pp.).
- **Sub-area:** **B1 and B2** (it is the only paper in this review that varies age *and*
  gender inside an agent-to-agent interaction, and reports on whether each actually works).
- **Demographic attributes varied:** a **6-dimensional persona space**: **age (20, 30, 40,
  50, 60)**, **gender (male, female, non-binary)**, country (China, US, Brazil, France,
  Nigeria, India), social class (upper, middle, lower), political ideology (4 levels), and
  Big Five personality traits (§3.3). 500 personas sampled without replacement from the
  Cartesian product (§3.3); the Limitations note this is from "an estimated 10,000 possible
  combinations".
- **How personas were specified:** **explicit labelled attributes injected into the system
  prompt** (§3.3) — e.g. "Age: 20 / Gender: Male / Openness: High" (Fig. 1).
- **Interaction type:** **dyadic multi-turn debate** between two persona-conditioned agents
  over moral dilemmas (131 scenarios from the Scruples corpus), with a moderator detecting
  consensus; stance shift measured by per-turn Likert ratings (§3.1, §3.4). Persuasion and
  consensus-seeking, not resource conflict.
- **Models used:** GPT-4o, Claude-3.5-Sonnet, LLaMA-4-Maverick, Qwen3-235B-A22B (§4,
  Limitations).
- **Main demographic finding (direction and size):**
  - **Gender, moral judgement (RQ1):** "**Female personas prioritize care, while males show
    a stronger emphasis on authority** (non-binary personas resemble females but exhibit
    higher fairness and slightly lower scores on loyalty)" (§4.1).
  - **Age, moral judgement (RQ1):** "**Older personas (age 60) tend to assign greater blame
    to the narrator** in moral dilemmas" (§4.1).
  - **⚠ The effects are statistically significant but numerically tiny.** In Fig. 4 (GPT-4o;
    scale 1 = blame the author, 5 = blame others), the caption states that Age, Gender,
    Country, Political Ideology and Big Five all "have statistically significant effects",
    and that "[t]he mean moral judgment score of GPT-4o without persona is **2.86**". Read
    from the Fig. 4 bar labels, the five **age** means span roughly **2.68–2.74** and the
    three **gender** means roughly **2.67–2.74** — a spread of under **0.07 on a 5-point
    scale**, against a no-persona baseline of 2.86. By contrast the political-ideology bars
    span roughly 2.52–2.83. `[needs verification against full text]` — the individual bar
    values were read from the text extraction of Fig. 4 and mapped to categories by axis
    order; **the caption-level claims are what should be cited**, and anyone quoting a
    specific bar must re-read the published figure.
  - **The authors' own summary is the important one:** "variation is primarily driven by
    **subjective attributes** (e.g., ideology and personality) **rather than objective ones
    (e.g., age or country)**" (§4.1), and for the other models "all or some of the
    dimensions of **age**, social class, and country are **not statistically significant
    according to ANOVA**" (§4.1).
  - **Persuasion (RQ2) — the split reverses.** In Fig. 5, statistically significant
    dimensions are starred; **(a) Age\*, (e) Political Ideology\* and (f) Big Five
    Personality\* are starred, and (b) Gender is *not*.** So in multi-turn persuasion, age
    moved consensus and gender did not.
  - **The age effect is non-monotonic:** "middle-aged personas (age 40) show lower persuasion
    effectiveness and confidence compared to both younger (20) and older (60) age groups"
    (§4.2) — a U-shape, not a gradient.
- **Compared against real human data?** **Yes — more seriously than any other B1 paper
  here**, and with a result the FYP must not ignore:
  - On age: the older-persona blame effect "is consistent with previous research showing that
    moral cognition changes over the lifespan, as older adults are more likely to judge
    harmful outcomes severely, even when the harm is accidental (Margoni et al., 2020)"
    (§4.1); the U-shaped persuasion effect "aligns with the cognitive aging literature"
    (Pliske & Mutter 1996; McNair et al. 2019) (§4.2).
  - On gender: **"prior persuasion research in advertising and decision-making has shown that
    men often display greater confidence in persuasive scenarios (Brunel and Nelson, 2003),
    whereas women and gender-diverse individuals may underreport confidence due to socialized
    uncertainty or structural bias (Exley and Kessler, 2022). By contrast, our results are
    mixed across models: GPT-4o aligns with these human findings, while LLaMA-4-Maverick and
    Qwen3-235B-A22B exhibit the opposite trend"** (§4.2).
  - They also report a model-wide **failure** against human data: on moral judgement, "all
    models exhibit a consistent bias toward author-blaming ... compared to human judgments",
    with human annotations centred at 3 (neutral) but every persona group, including
    no-persona, scoring below 3 (§4.1).
- **Persona fidelity:** this paper is the best evidence in the review that **fidelity is
  dimension-specific and task-specific**: the same age variable is significant for moral
  judgement (Fig. 4) and for persuasion (Fig. 5a), while the same gender variable is
  significant for the former and not the latter (Fig. 5b); and for some models age is not
  significant at all (§4.1). No caricature analysis, but the Ethical Considerations section
  concedes that "[s]ome persona combinations may inadvertently encode harmful stereotypes".
- **Mitigation proposed:** none. The Ethical Considerations describe process safeguards
  (manual review of templates, disallowing protected-attribute slurs), not debiasing.
- **Limitations stated by the authors (Limitations §):** 131 dilemmas from Scruples, with
  **no demographic metadata for the original annotators**, so the human baseline's own
  representativeness is unknown; 500 of ~10,000 persona combinations sampled, which "may not
  ... reflect the distribution of traits in real-world populations"; **dyadic only** —
  "future work should examine richer multi-agent debate settings involving more than two
  agents"; limited model coverage; all debates in English. Ethical Considerations add that
  Scruples is Reddit-sourced and "skew[s] towards WEIRD demographics".
- **Relevance to this FYP:**
  - **The single most consequential finding in this review for the FYP's design.** The gender
    effect *flips direction between models* (§4.2). `run01` used one model (DeepSeek). Its
    female-yields-more pattern therefore cannot be reported as "what LLMs do" — at most it is
    "what this model did". **A second model is the cheapest, most defensible robustness check
    the project can run**, and its result is publishable either way.
  - It is also the strongest evidence that **age may be the weaker variable**: it is the
    dimension the authors single out as not consistently significant (§4.1), yet the FYP's
    personas are organised by age band. See B2 below, where this converges with
    [Chu-Marketing], [SiyangLiu-GenerationGap] and [Wang-IdentityGroups].
  - The Scruples annotators' missing demographics is the same defect `run01` has: there is no
    human ground truth attached to the scenarios.
- **BibTeX:** `liu2026socratic` — see [`refs.bib`](refs.bib).

---

# B2. Persona fidelity: does the persona actually work?

### [Hu-PersonaEffect]: Quantifying the Persona Effect in LLM Simulations
- **Authors / Year / Venue:** Tiancheng Hu, Nigel Collier (University of Cambridge) / 2024 /
  Proceedings of the 62nd Annual Meeting of the ACL (Volume 1: Long Papers),
  pp. 10289–10307, Bangkok, Thailand.
- **Link:** doi:10.18653/v1/2024.acl-long.554 | https://aclanthology.org/2024.acl-long.554/
- **Peer-review status:** **published** at ACL 2024 (main conference, long paper). Confirmed
  from the ACL Anthology's own BibTeX export (`refs/b2_persona_effect.bib`).
- **Verified:** yes — full PDF read (`refs/b2_persona_effect.pdf`).
- **Sub-area:** B2
- **Demographic attributes varied:** "persona variables" broadly — the authors' Table 1
  classifies them as **"Basic" for standard demographics like gender and age**, "Attitude"
  for annotators' personal views, and "Behavior" for actions such as media-consumption
  habits (Table 1 caption). Gender and age are therefore *inside* the variable set but are
  **not reported separately** — the paper's unit of analysis is the whole persona vector.
- **How personas were specified:** natural-language attribute statements in the prompt —
  e.g. "You race is White. Your gender is male. Generally speaking, you consider yourself
  politically liberal. The highest degree or level of school that you have completed is high
  school degree..." (Fig. 1 example).
- **Interaction type:** **single agent** (annotation prediction and survey-response
  simulation). No agent-to-agent interaction.
- **Models used:** a range including a 70b model in the zero-shot setting (Abstract, §RQ4).
- **Main demographic finding (direction and size):**
  - **The headline constraint on the whole enterprise:** persona variables "account for just
    **1.4%–10.6%** of the total variance (Marginal R²), even when controlling for text
    variation" across 10 subjective NLP datasets (§3). By contrast, **text-specific
    variability explains up to 70%** (§3).
  - **But this is task-dependent, and the contrast matters more than the headline:** "in the
    ANES dataset [presidential vote], persona variables explain **more than 70%** human
    response variance" (§3). So the same demographic variables are near-useless for one task
    and dominant for another.
  - Persona prompting gives "modest but statistically significant improvements" (Abstract),
    and is "most effective in samples where many annotators disagree, but their disagreements
    are relatively minor" (Abstract).
  - **A clean scaling law:** "the stronger the correlation between persona variables and
    human annotations, the more accurate the LLM predictions are using persona prompting"
    (Abstract); at the top end "a powerful 70b model with persona prompting captures **81%**
    of the annotation variance achievable by linear regression trained on ground truth
    annotations" (Abstract).
- **Compared against real human data?** **Yes, throughout and by design** — this is the point
  of the paper. All R² values are computed on real human annotations (10 datasets plus ANES),
  and the LLM is scored against those same human annotations.
- **Persona fidelity:** the paper's contribution is precisely to bound fidelity: LLMs can
  exploit persona variables roughly as well as a linear model can, and no better — so **if
  the demographic variable does not predict the human outcome, persona prompting cannot
  help.** The introduction also flags, by citation, the caricature and flattening literature
  (Cheng et al. 2023; Wang et al. 2024 — see [Wang-IdentityGroups] below) and the ecological
  fallacy (Orlikowski et al. 2023).
- **Mitigation proposed:** not a debiasing paper. Its practical proposal is diagnostic: run
  the regression *first*, "prior to conducting large-scale experiments when some amounts of
  human data are available" (§RQ1), to predict whether persona prompting is worth doing.
- **Limitations stated by the authors:** the regression "assumes a linear relationship between
  persona variables and annotation and does not consider any interaction between the persona
  variables" (§3), so the R² figures are a floor, not a ceiling; 25–70% of variance is left
  unexplained by text *or* persona, possibly due to unmeasured factors such as personality
  and moral/political belief (§3); most NLP datasets have no annotator information at all
  (§1 fn. 2).
- **Relevance to this FYP:**
  - This paper supplies **the test the FYP should run before defending its dataset**. The
    diagnostic is: *how much of the variance in real human yielding behaviour is explained by
    gender and age?* If the answer is ~2–10%, as it is for subjective annotation, then a
    dataset organised primarily by age and gender is organised around a weak variable — and
    the honest framing of `run01`'s gender effect becomes "the LLM shows a stronger
    demographic effect than the human data would justify", which is a finding, not a failure.
  - The ANES contrast is the counter-argument and should be stated alongside it: demographics
    *can* dominate, for the right outcome variable. Whether pedestrian yielding is an
    ANES-like or an annotation-like task is an **open empirical question** this review cannot
    settle — it is exactly what B3's human evidence is needed for.
  - [inference] Mark as a design implication, not a finding: the FYP has *no* human ground
    truth for yielding, so it currently cannot run this diagnostic at all. Acquiring even a
    small human-labelled or observational comparison set would unlock it.
- **BibTeX:** `hu2024quantifying` — see [`refs.bib`](refs.bib).

---

### [Wang-IdentityGroups]: Large language models that replace human participants can harmfully misportray and flatten identity groups
- **Authors / Year / Venue:** Angelina Wang (Stanford), Jamie Morgenstern (University of
  Washington), John P. Dickerson (University of Maryland; Arthur) / 2025 / **Nature Machine
  Intelligence** 7(3), pp. 400–411.
- **Link:** doi:10.1038/s42256-025-00986-z | preprint: https://arxiv.org/abs/2402.01908
- **Peer-review status:** **published** in Nature Machine Intelligence, 17 February 2025.
  Journal, volume 7, issue 3, pages 400–411 and DOI confirmed from the **Crossref record**
  (`refs/cr_wang.json`); the arXiv Comments field independently reads "Accepted at Nature
  Machine Intelligence" (`refs/b2_wang_identity_groups_abs.html`).
- **⚠ This resolves the issue's `[secondhand]` seed, and the title has changed.** The issue
  lists "Wang, A., Morgenstern, J. & Dickerson, J. P. Work on LLMs that replace human
  participants misportraying and flattening identity groups `[secondhand]`". The primary
  publication is this paper. It was **retitled between versions**: v1/v2 were "Large language
  models cannot replace human participants because they cannot portray identity groups"
  (this is the form cited by Hu & Collier 2024, which is how I traced it); v3 and the
  published version use the title above. **Cite the published title.**
- **Verified:** yes — full PDF read (`refs/b2_wang_identity_groups.pdf`, arXiv v3,
  3 Feb 2025; locators are to this version, which the arXiv page states is the accepted one).
- **Sub-area:** B2
- **Demographic attributes varied:** five axes, 16 identities, **including both gender and
  age**: "race (Black, White, Asian), **gender (women, men, non-binary people)**,
  intersectional (Black women, Black men, White women, White men), **age (Baby Boomer:
  59–77, Millennial: 27–42, Generation Z: 18–26)**, and disability" (§Results). Race and
  disability noted, not extracted.
- **How personas were specified:** identity prompting (explicit identity invocation), plus a
  tested alternative of **identity-coded names** as an inference-time mitigation (§Intro).
- **Interaction type:** **single agent**, free-response question answering, benchmarked
  against human participants. Not agent-to-agent.
- **Models used:** Llama-2-Chat 7B, Wizard Vicuna Uncensored 7B, GPT-3.5-Turbo, GPT-4
  (June 13 2023 weights; experiments run July–August 2023) (§Results).
- **Main demographic finding (direction and size):**
  - **Misportrayal — the LLM sounds like an outsider describing the group, not a member of
    it.** Across all four LLMs on the "R2-Relevant" question type, a majority of six
    similarity metrics found the LLM statistically significantly more like an out-group
    imitation than an in-group representation for **Gen Z in 27 of 48** measurement × model
    comparisons and for **woman in 26 of 48**; also non-binary person 32/48 and person with
    impaired vision 27/48 (§"LLMs can misportray groups as out-group imitations"). On the
    "R1-Contingent" type, White person 23/24, non-binary 16/24, impaired vision 18/24.
  - **Note the age asymmetry:** **Gen Z** (the young group) is flagged for misportrayal;
    **Baby Boomer and Millennial are not** among the flagged identities in the reported
    results.
  - **The effect is task-dependent:** "For R3-Subjective we do not see misportrayal effects
    because demographic identities and personas generate minimal differences in these more
    constrained annotation tasks" (§ibid.) — converging with [Hu-PersonaEffect].
  - **Flattening — the LLM loses within-group diversity, for every group.** "**Nearly every
    single model and identity group across each metric has less diverse LLM responses
    compared to human responses**" (Fig. 4 caption), and "[a]cross all question types and
    demographic groups, LLM responses are less diverse than human responses" (Fig. 9
    caption).
  - **Scale:** 3,200 human participants across 16 demographic identities; 100 responses per
    group per generation source; 95% CIs by cluster bootstrapping (§Results, Fig. 4 caption).
- **Compared against real human data?** **Yes — this is the paper's core method, and it is
  the strongest human grounding in this whole review.** Human in-group representations *and*
  human out-group imitations were both collected from real participants on Prolific
  ($12/hour, IRB-exempt) and the LLM is compared against both (§Results). This is exactly the
  comparison design the FYP's realism-vs-bias question needs.
- **Persona fidelity:** the paper's answer is that **the persona "works" in the sense of
  changing output, but in the wrong direction and with the wrong variance**: outputs shift
  (established as a premise in Supplementary §2) but shift *toward how outsiders talk about
  the group*, and with systematically **too little** heterogeneity. Caricature/flattening is
  the explicit subject. A third limitation, **essentialization** — "reducing identities to
  fixed characteristics ... an inherent premise in identity prompting" — is also raised
  (§Intro).
- **Mitigation proposed:** two inference-time techniques — **identity-coded names** instead of
  explicit identity labels (to work around the missing author-identity link in training
  data), and **raising temperature** (to counter flattening). Both "do reduce, but do not
  remove, these harms" (Abstract); "[n]either of these techniques are able to wholly overcome
  the limitations, but they do improve upon the default" (§Intro).
- **Limitations stated by the authors:** the analysis covers "a set of 16 demographic groups
  **in America**" and the authors note that many more groups are likely harmed, including
  "the 37% of the global population that has never accessed the Internet ... nor cultures
  that prioritize oral traditions over written ones" (§Discussion); they make no claims about
  training procedures that depart from likelihood maximisation (§Intro); and they flag
  contamination — some human participants may themselves have used LLMs to answer (estimated
  <10% in the sets they hand-labelled, §Supplementary).
- **Relevance to this FYP:**
  - **Flattening is a direct threat to the project's stated goal.** The FYP wants demographic
    variety in a 10,000-agent crowd. If LLM-generated personas are systematically *less*
    varied than real people of the same demographic, a demographically-labelled LLM crowd
    will be more homogeneous than the real crowd it models — while *looking* diverse because
    the labels differ. [inference] The practical countermeasure follows from the paper's own
    mitigation: check the **within-persona variance** of `run01`'s records against any
    available human variance, and consider sampling at higher temperature. `run01` currently
    reports `mean_primary_action_agreement = 0.753` across repeats
    (`dataset/generated/validation_report.md`), which is a *consistency* measure — high
    consistency is exactly what flattening looks like, so this number should not be read as
    unambiguously good news.
  - **Misportrayal reframes `run01`'s gender finding.** If an LLM prompted "you are a woman"
    reproduces *how people write about women* rather than how women behave, then a female
    persona yielding more is evidence about the discourse, not about women. This paper is the
    citation that makes that argument rigorous rather than rhetorical.
  - The US-only scope is a real limit for a Singapore-scoped dataset — see
    [`population-data-sources.md`](population-data-sources.md) and the Open Questions.
- **BibTeX:** `wang2025identity` — see [`refs.bib`](refs.bib).

---

### [SiyangLiu-GenerationGap]: The Generation Gap: Exploring Age Bias in the Value Systems of Large Language Models
- **Authors / Year / Venue:** Siyang Liu, Trisha Maturi, Bowen Yi, Siqi Shen, Rada Mihalcea
  (The LIT Group, University of Michigan) / 2024.
- **Link:** https://arxiv.org/abs/2404.08760 | doi:10.48550/arXiv.2404.08760
- **Peer-review status:** **`[preprint]`** — arXiv:2404.08760v4, submitted 12 Apr 2024, last
  revised 15 Oct 2024. The Comments field reads only "5 pages"; there is **no** Journal
  reference (`refs/b2_generation_gap_abs.html`). I found no published version and did not
  locate a publisher page; see [`search-log.md`](search-log.md).
- **Verified:** yes — full PDF read (`refs/b2_generation_gap.pdf`, v4).
- **Sub-area:** B2
- **Demographic attributes varied:** **age only** — six groups: 18–24, 25–34, 35–44, 45–54,
  55–64, 65+ (§3.2), crossed with country.
- **How personas were specified:** **explicit age-range statement prepended to the prompt**:
  *"Suppose you are from [country] and your age is between [lowerbound] and [upperbound]."*
  (§5). Eight prompt-format variations were used to test robustness (§1).
- **Interaction type:** **single agent**, value elicitation. Not agent-to-agent.
- **Models used:** several LLMs including ChatGPT (§4, Fig. 3); the full list is in the
  paper's appendices, which I did not transcribe `[needs verification against full text]`.
- **Main demographic finding (direction and size):**
  - **LLM values skew young.** "[W]e find a general inclination of LLM values towards younger
    demographics, especially when compared to the US population" (Abstract); the trend holds
    across most of thirteen World Values Survey categories (§4, Fig. 1), and in the US and
    China "the models tend to have a higher alignment rank on younger groups on most
    categories, despite few exceptions (e.g., happiness and well-being)" (§4).
  - **Culture-dependence:** "in Ethiopia and Nigeria (Tab 15), the inclination is less
    evident. We leave this phenomenon for future study" (§4).
  - **The finding that matters most for this FYP — telling the model an age does not fix it.**
    "[W]e find that adding age identity fails to eliminate the value discrepancies with
    targeted age groups on **eight out of thirteen** categories" (§1; §5, Fig. 4: "in eight
    out of thirteen categories (No.1,2,4,5,7,8,11,12) no improvement is observed").
  - The authors' conclusion: "we have shown how **LLMs are not representative of the value
    systems of older adults**" (§6).
  - Method: 372 human value vectors across 62 countries and 6 age groups from the World
    Values Survey, PCA-reduced to 3 dimensions, compared to the LLM's vector by Euclidean
    distance, alignment rank and a fitted trend coefficient (§3.2–3.3).
- **Compared against real human data?** **Yes** — the entire comparison is against World
  Values Survey respondents grouped by age and country (§3.1–3.2). This is a genuine human
  baseline, though of *values*, not behaviour.
- **Persona fidelity:** **directly measured, and largely negative.** This is the cleanest
  evidence in the review that an **age persona does not reliably move the model to the target
  age group**: no improvement in 8 of 13 value categories after the age identity is added
  (§5). The authors hedge appropriately: "Although further validation is necessary for a
  solid conclusion..." (§6).
- **Mitigation proposed:** prompt-based age identity injection is the intervention **tested
  and found largely insufficient** (§5). The authors "emphasize the complexities involved in
  calibrating prompts to effectively address this bias" (§1).
- **Limitations stated by the authors:** a 5-page short paper; the non-US/China results are
  left unexplained (§4); LLM values can sit "far away from all human age groups" so
  rank-based alignment can mislead (§4, Appx G.2); "further validation is necessary for a
  solid conclusion" (§6).
- **Relevance to this FYP:**
  - **This is the strongest single reason to doubt the age dimension of `run01`.** The FYP
    organises its dataset by age band and gets age-ordered outputs (`run01`'s INFO block
    records "PASS: elderly walk slower than young adults" and "PASS: elderly yield at least
    as much as young adults"). Those passes are consistent with a real age effect — **and
    equally consistent with the model reproducing the obvious script for "elderly"** while
    its underlying value system stays young-skewed. Passing a hypothesis you expected is weak
    evidence; this paper explains why.
  - [inference] Concretely testable in the FYP: if age prompting were working, elderly-persona
    records should differ from young-adult records on attributes *not* stereotypically
    age-linked, not only on walking speed and yielding. A check on the *unexpected* attributes
    would be far more diagnostic than the current hypothesis tests.
  - Its culture-dependence finding (weaker skew in Ethiopia/Nigeria) means the US-derived
    result should not be assumed to hold for Singapore without checking.
- **BibTeX:** `siyangliu2024generation` — see [`refs.bib`](refs.bib).

---

### [Tan-Unmasking]: Unmasking Implicit Bias: Evaluating Persona-Prompted LLM Responses in Power-Disparate Social Scenarios
- **Authors / Year / Venue:** Bryan Chen Zhengyu Tan, Roy Ka-Wei Lee (**Singapore University
  of Technology and Design**) / 2025 / Proceedings of NAACL 2025 (Volume 1: Long Papers),
  pp. 1075–1108, Albuquerque, New Mexico.
- **Link:** doi:10.18653/v1/2025.naacl-long.50 | https://aclanthology.org/2025.naacl-long.50/
- **Peer-review status:** **published** at NAACL 2025 (main conference, long paper). Confirmed
  from the ACL Anthology's own BibTeX export (`refs/b2_unmasking_acl.bib`); the arXiv
  Comments field independently reads "NAACL 2025".
- **Verified:** yes — full PDF read (`refs/b2_unmasking_implicit_bias.pdf`, arXiv v2,
  22 Apr 2025).
- **Sub-area:** B2 (with a direct bearing on B1's communication-style question)
- **Demographic attributes varied:** nine axes, 3–5 identities each (§3, Table 2), including
  **gender identity (Male, Female, Non-binary, Transgender)** and **age (Young person,
  Middle-aged person, Old person)**. Race, religion, political stance, disability, nativity
  and physical appearance also studied — noted, not extracted.
- **How personas were specified:** **explicit demographic labels on deliberately unisex
  names** — "Alex" for the subject and "Blake" for the responder throughout, "[t]o control for
  confounding factors" (§3). Demographics are assigned to **both** parties, giving 112 unique
  demographic combinations per scenario (§3).
- **Interaction type:** **dyadic**, one response per scenario, across 100 social scenarios
  deliberately constructed with **power disparities** between the two parties (§3). Not
  multi-turn, and not resource conflict — but the power-disparity framing is closer to a
  priority dispute than most.
- **Models used:** five LLMs (Abstract; per-model results in Tables 8–9).
- **Main demographic finding (direction and size):**
  - **The "default persona" is middle-aged and male.** "[O]ur findings suggest a **'default
    persona' bias toward middle-aged, able-bodied, native-born, Caucasian, atheistic males
    with centrist views**" (Abstract; method at §RQ1 — the default is inferred from which
    demographic combinations produce the *smallest* semantic shift relative to the
    un-prompted response).
  - **Old → Young interactions produce patronising, lower-quality output.** "[T]he demographic
    responses from Old responders introduce patronising language such as **'honey,' 'kid,'
    and 'my dear.'** This shift reflects a change in tone, becoming more condescending and
    less collaborative compared to the non-demographic responses" (Table 7 discussion), and
    the LLM judge consistently preferred the non-demographic response in those cases.
  - **Age pairings are among the largest semantic shifts** — "the highest cosine distances,
    reflecting greater semantic shifts, are observed in interactions involving **Old and
    Young**, Mentally-Disabled and Abled, Non-Binary and Transgender..." (§Results).
  - **Yet age as an *axis* is among the least influential overall:** "the least sensitive
    axes, with the lowest average cosine distance, include Race (3 out of 5 models), Physical
    Appearance (1 out of 5 models) and **Age (1 out of 5 models)**" (§Results, Table 8), and
    "**Age** [is] also associated with the lowest response quality in 1 out of 5 models"
    (§Results, Table 9).
  - **Power disparity amplifies:** "the presence of power disparities increases variability in
    response semantics and quality across demographic groups, suggesting that implicit biases
    may be heightened under power-imbalanced conditions" (Abstract).
  - Higher-quality responses were found "when **Middle-Aged responders address Old
    subjects**" (§Results).
- **Compared against real human data?** **Partially — and specifically for the age finding.**
  The patronising-speech result is checked against the human intergenerational-communication
  literature: "These findings corroborate research on patronising speech from older adults
  toward younger people (Giles and Williams, 1994). Patronising communication can reduce
  self-esteem in younger individuals and hinder effective interaction" (§Results). No human
  participants were run for this study; the human comparison is by citation to
  Giles & Williams (1994), *Patronizing the Young: Forms and Evaluations*,
  *The International Journal of Aging and Human Development* 39(1):33–53.
- **Persona fidelity:** two results pull in opposite directions and both matter. (a) The
  persona **does** change output — age pairings produce some of the largest semantic shifts
  measured. (b) The persona is **least** influential on the age axis overall, and the model
  has a **strong default it reverts to** (middle-aged male). Together: age prompting produces
  a visible surface effect (tone, address terms) on a model whose underlying default is
  middle-aged and male.
- **Mitigation proposed:** none implemented; the paper positions itself as diagnostic,
  "offer[ing] potential paths toward future bias mitigation" (Abstract).
- **Limitations stated by the authors:** `[needs verification against full text]` — I read the
  main text and results appendices, and did **not** separately transcribe the Limitations
  section. Do not attribute limitations to this paper without re-reading it.
- **Relevance to this FYP:**
  - **The default-persona finding has a concrete consequence for GameChat.** GameChat assigns
    no demographic (confirmed above). If the unprompted default is middle-aged, able-bodied
    and male, then GameChat's "neutral" agents are **not** demographically neutral — they are
    implicitly middle-aged men. [inference] That reframes the FYP's contribution: adding
    demographic personas is not *introducing* a demographic variable into a neutral system, it
    is *making an existing implicit one explicit and controllable*. This is a stronger
    motivation than "crowds are diverse", and it is defensible from a published NAACL paper.
  - The Old→Young patronising result is a plausible mechanism for an age effect in a
    **negotiated** priority exchange: an elderly agent may not merely yield differently, it may
    *talk* differently in a way that changes what the other agent concedes. `run01` records
    outcomes, not dialogue, so it cannot see this.
  - Same-city authorship (SUTD) — useful for a Singapore-scoped project and for the report's
    local-relevance framing.
- **BibTeX:** `tan2025unmasking` — see [`refs.bib`](refs.bib).

---

### [Chu-Marketing]: LLM-Based Multi-Agent System for Simulating and Analyzing Marketing and Consumer Behavior
- **Authors / Year / Venue:** Man-Lin Chu, Lucian Terhorst, Kadin Reed, Tom Ni, Weiwei Chen
  (School of Business) / 2025 / **IEEE International Conference on e-Business Engineering
  (ICEBE) 2025**, 10–12 November, Buraydah, Saudi Arabia.
- **Link:** https://arxiv.org/abs/2510.18155 | doi:10.48550/arXiv.2510.18155
- **Peer-review status:** **accepted** at IEEE ICEBE 2025 — the arXiv Comments field reads
  "Accepted for publication at IEEE International Conference on e-Business Engineering ICEBE
  2025, November 10-12, Buraydah, Saudi Arabia" (`refs/b2_marketing_consumer_abs.html`). No
  Journal-reference field, and **no IEEE Xplore record was located**, so the proceedings
  citation (pages, DOI) is **not confirmed**; cite as "accepted at IEEE ICEBE 2025; read as
  arXiv:2510.18155".
- **Verified:** yes — full PDF read (`refs/b2_marketing_consumer.pdf`, 7 pp.).
- **Sub-area:** B2
- **Demographic attributes varied:** **age**, alongside occupation and socioeconomic status,
  as agent-profile fields (§VI-C).
- **How personas were specified:** agent profiles with age and other attributes (e.g. a
  7-year-old agent "assigned childlike attributes"), in a multi-agent consumer simulation
  (§VI-C).
- **Interaction type:** **multi-agent** simulation of consumer choice over repeated days.
- **Models used:** not extracted `[needs verification against full text]`.
- **Main demographic finding (direction and size):** **qualitative, not quantified.** §VI-C
  ("Age-Specific Behavioral Fidelity") states in full the finding the issue flagged:
  - "[W]e observed **fidelity gaps when modeling children and older adults**. These
    limitations likely stem from LLM training data, which are dominated by **internet users
    aged roughly 18–45**."
  - "[A] **7-year-old agent assigned childlike attributes still displayed adult behaviors
    (e.g., requesting coffee when tired)** and lacked age-appropriate curiosity or emotional
    tone."
  - "Similarly, **elderly agents showed little minor distinction from middle-aged adults**,
    rarely referencing their health concerns, technological unfamiliarity, or traditional
    perspectives." *(quoted as printed, including the "little minor" wording)*
  - "These limitations reduce the realism of simulations targeting edge demographics" and are
    said to hinder study of children's products, elderly UX, and "[m]ulti-generational family
    or care scenarios" (§VI-C).
  - ⚠ **No numbers, no metric, no statistical test accompanies this observation.** It is an
    author-reported observation from their own simulation, in a discussion section.
- **Compared against real human data?** **No.** The claim of a fidelity gap is made by
  inspection against the authors' expectations of child and elderly behaviour, not against
  collected human data. The training-data explanation ("internet users aged roughly 18–45") is
  asserted without a citation in the passage.
- **Persona fidelity:** this *is* the fidelity finding — and it names the two age groups where
  the persona reportedly fails. Elsewhere the paper claims positive fidelity for
  non-age-specific behaviour ("[t]he emergence of consensus behavior without fixed programming
  validates the simulation's fidelity"; "LLMs generate socially aligned, high-fidelity behavior
  autonomously"), so the age gap is reported as a specific exception within an otherwise
  favourable self-assessment.
- **Mitigation proposed:** for a different problem (planning fidelity), the authors suggest
  "a formal grounding mechanism, or constrained decoding strategy ... location entity checking,
  model ensemble verification, or hybrid symbolic + generative logic". **Nothing is proposed
  for the age gap.**
- **Limitations stated by the authors:** §VI-C is itself the limitation; see above.
- **⚠ Qualification against the issue's selection criterion.** The issue requires "an
  **empirical result** on how gender or age changes behaviour or outcomes". This paper reports
  an empirical *observation* from a run simulation, but with no measurement. **It is included
  because the issue named it as a seed and because it is the only source located that speaks
  directly to child and elderly persona fidelity — but it is the weakest evidence in this file
  and must not be cited as a quantified finding.** The quantified support for the same
  conclusion comes from [SiyangLiu-GenerationGap] (8/13 categories unimproved) and
  [Wang-IdentityGroups] (flattening across all groups); cite those alongside it.
- **Relevance to this FYP:**
  - It speaks to **exactly the two age bands `run01` uses that are furthest from the training
    distribution**: `child` and `elderly` (`dataset/personas.yaml`). If elderly agents show
    "little... distinction from middle-aged adults", then `run01`'s elderly records may be
    middle-aged records with an elderly label — and the validator's "PASS: elderly yield at
    least as much as young adults" would still pass, because the *stereotype* is reproduced
    even where the *behaviour* is not.
  - A crowd simulation cannot simply drop these groups: children and elderly pedestrians are
    precisely the agents whose speed and yielding differ most, and RiMEA scenarios include
    mixed-age populations (`integration/crowdgym_mapping.md`).
- **BibTeX:** `chu2025llmbased` — see [`refs.bib`](refs.bib).

---

## Examined and read, but **not** qualifying under the issue's selection criterion

Both were named as verified seeds in the issue. Both were downloaded and read in full.
Neither varies gender or age, so neither can qualify under "reports an empirical result on how
**gender or age** changes behaviour or outcomes". They are recorded here because the issue
asked what they actually find, and because both describe confounds that would sit underneath
any demographic experiment the FYP runs.

**[Manoranjan-IdentityIncentives]** — *When Identity Overrides Incentives: Representational
Choices as Governance Decisions in Multi-Agent LLM Systems.* Viswonathan Manoranjan,
Snehalkumar 'Neil' S. Gaikwad (UNC Chapel Hill). arXiv:2601.10102v6, 30 May 2026;
**accepted to ACM FAccT 2026** (Comments field, `refs/b1_personas_override_payoffs_abs.html`).
⚠ **The issue cites this under its v1 title, "When Personas Override Payoffs: Role Identity
Bias in Multi-Agent LLM Decision-Making"; the paper has since been retitled as above.**
A case-insensitive search of the full text for `gender`, `female`, `male`, `age`, `elderly`,
`demographic`, `man`, `woman` returns only incidental matches (author surnames, "human").
Personas are **occupational/role-based** — an agent "plays an industrialist in a multi-agent
climate policy game" (§1). Finding: "assigning role-based personas **suppresses payoff-aligned
behavior** in four-agent strategic games, shifting equilibrium attainment by **up to 90
percentage points** even when agents have complete payoff information", from a 2 × 2 factorial
design of persona presence × payoff visibility (Abstract).
**Why it still matters to the FYP** [inference]: GameChat's entire mechanism is that agents
infer priority from *task urgency* — the payoff. This paper shows a persona can overwhelm a
fully-visible payoff. If that generalises from role personas to demographic personas, a
demographic label could override genuine task urgency in a priority negotiation, which is the
precise failure mode the FYP must be able to detect. **But this is an extrapolation across
persona types that the paper does not license**, and it should be stated as a hypothesis to
test, never as a finding. Cached at `refs/b1_personas_override_payoffs.pdf`.

**[Reza-SocialLaboratory]** — *The Social Laboratory: A Psychometric Framework for Multi-Agent
LLM Evaluation.* Zarreen Reza (independent researcher). arXiv:2510.01295v1, 1 Oct 2025,
**`[preprint]`**. A case-insensitive search of the full text for `gender`, `female`, `age`
returns **zero** matches. Personas are dispositional roles — an "evidence-driven analyst"
(incentive: truth) versus a "values-focused ethicist" (incentive: persuasion), supervised by a
"Neutral" moderator (§2). Finding: "a powerful and robust emergent tendency for agents to seek
consensus, consistently reaching high semantic agreement (**ρ > 0.88**) even without explicit
instruction and across sensitive topics" (Abstract).
**Why it still matters to the FYP** [inference]: this is a **confound with a direction**, and it
aligns with GameChat's own observation that "[t]he correct consensus was always reached"
because "by default, LLMs are designed to be very honest and cooperative"
(`literature/paper-summaries/03-gamechat.md`, §V-B.2). A strong built-in consensus drive
compresses the range of outcomes, which would make any demographic effect *harder* to detect —
so a **null** demographic result in a GameChat-style setting would be weak evidence of absence.
Cached at `refs/b1_social_laboratory.pdf`.

---

## Cross-cutting observations (B1 + B2)

These are my synthesis, not any single paper's claim. Each is sourced; inferences are marked.

1. **The LLM gender→yielding effect has no agreed direction.** [Khaki-Fairness] (§4.1) and
   `run01` point one way (female concedes/loses more); [Li-SingleToSocietal] (§5.2, §6.2)
   points the other (men conform more, women's positions prevail); [Liu-SocraticDebates]
   (§4.2) reports the direction **flipping between models within one study**. Any claim of the
   form "LLMs make women yield more" is currently unsupported as a general statement.
2. **Age is the weaker and less reliable variable of the two.** Four independent sources
   converge: not consistently significant across models ([Liu-SocraticDebates] §4.1); age
   prompting fails to close the value gap in 8/13 categories ([SiyangLiu-GenerationGap] §5);
   among the least influential axes in 1/5 models ([Tan-Unmasking], Table 8); and explicit
   fidelity gaps for children and older adults ([Chu-Marketing] §VI-C). Set against this,
   [Liu-SocraticDebates] does find a significant, human-consistent age effect on persuasion
   (Fig. 5a) and moral blame (§4.1). **The honest summary is "contested, and weaker than
   gender", not "absent".**
3. **Multi-turn interaction is not neutral — it amplifies.** [Borah-ImplicitBias] measures
   bias escalating after interaction in every model and every domain (§5.1.1–5.1.2);
   [Li-SingleToSocietal] finds the persuasion gap widening from 20% to 24% over five rounds and
   from 10% to 27% as persuaders are added (§6.2); [Bandaru-PoliticalDebate] finds
   reinforcement stronger when agents know each other's gender (§6). [inference] A single-shot
   dataset like `run01` therefore probably **understates** the effect that a dialogue-based
   system would show.
4. **"No persona" is not "no demographics."** [Tan-Unmasking]'s default-persona result
   (Abstract) means an unprompted agent already behaves like a middle-aged male. GameChat's
   agents are unprompted (confirmed above). [inference] The FYP's demographic work is therefore
   better framed as replacing an uncontrolled implicit default with a controlled explicit one.
5. **Almost nobody checks against humans.** Of the nine qualifying papers, only
   [Wang-IdentityGroups] ran human participants for the comparison (3,200), and only
   [Hu-PersonaEffect] and [SiyangLiu-GenerationGap] compare against pre-existing human survey
   data. Four label effects "bias" with no human baseline at all ([Borah-ImplicitBias],
   [Khaki-Fairness], [Bandaru-PoliticalDebate], and [Li-SingleToSocietal] post hoc only).
   **This gap is the FYP's opportunity, and it is why
   [`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md) has as many "no human
   evidence found" rows as it does.**
