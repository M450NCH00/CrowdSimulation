# G5 — LLM agents and game theory

Prepared for issue [#20](https://github.com/M450NCH00/CrowdSimulation/issues/20).
Companion files: [`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md),
[`g2-norm-emergence.md`](g2-norm-emergence.md),
[`g3-cheap-talk.md`](g3-cheap-talk.md),
[`g4-game-theoretic-crowd-models.md`](g4-game-theoretic-crowd-models.md),
[`g6-transfer-across-games.md`](g6-transfer-across-games.md),
[`candidate-rule-catalogue.md`](candidate-rule-catalogue.md),
[`search-log.md`](search-log.md), [`refs-game-theory.bib`](refs-game-theory.bib).

The issue is explicit that this sub-area must not be a one-sided summary:

> "This sub-area must include the data-leakage critique described below; a summary of the positive
> result alone is not acceptable."

All three documents — the paper, the critique and the reply — were opened and read in full. The
critique's specific technical objections are recorded individually in §2, not summarised in general
terms.

> **Why this sub-area decides the FYP's research question.** The FYP's underlying question is
> *"do LLMs actually understand human behaviour well enough to be used as agents in the crowd
> simulation?"* The exchange below is the published, live version of exactly that dispute. Whichever
> side is right, the FYP's report cannot state its premise without engaging with it.

---

## §1. The positive result

### [Ashery-EmergentConventions]: Emergent social conventions and collective bias in LLM populations

- **Authors / Year / Venue:** Ariel Flint Ashery (City St George's, University of London), Luca Maria
  Aiello (IT University of Copenhagen; Pioneer Centre for AI), Andrea Baronchelli (City St George's;
  The Alan Turing Institute) / 2025 / *Science Advances* **11**(20), article eadu9368. Published 14
  May 2025.
- **Link:** doi:[10.1126/sciadv.adu9368](https://doi.org/10.1126/sciadv.adu9368) · CC BY-NC
- **Peer-review status:** **published**, peer-reviewed journal (AAAS).
- **Verified:** **yes — full text.** Read from the author-deposited open-access copy of the published
  article (City Research Online eprint 35211, `refs/gt_ashery2025_sciadv.pdf`, text at
  `refs/gt_ashery2025_sciadv.txt`). This is the **published** version, so locators are to its named
  sections and the printed page numbers ("Ashery et al., Sci. Adv. 11, eadu9368 (2025)", pp. 1–10).
- **Sub-area:** G5
- **Tags:** none (2025)
- **Type:** LLM experiment
- **The game or conflict modelled:** a **naming game** — a pure coordination game over arbitrary
  labels, not an anti-coordination conflict game. "each agent outputs a convention, or 'name,' from a
  pool of finite size W, and these outputs are compared to determine coordination. The prompt
  specifies that if the conventions match, then the game score of the agent is incremented, and if
  they do not match, then it is decremented" (Experimental setup, p. 2). Two agents per interaction,
  drawn at random from a population: "A simulation trial consists of a population of N interacting
  agents. At each time step, two agents are randomly selected for interaction" (Experimental setup,
  p. 2). Payoffs are stated in Materials and Methods as "+100 and −50 points" for success and
  failure respectively (p. 8). Default parameters: "pool size to W = 10 and the individual memory
  length to H = 5 for populations of N = 24 agents, unless otherwise specified" (p. 3).
  ⚠ [inference] Note for the FYP: **this is a coordination game, not a conflict game**, so it does
  not by itself demonstrate anything about LLMs resolving *conflicting* actions. The authors
  themselves flag the gap and point at it as future work: "Game theoretical approaches would
  naturally allow investigation of **asymmetric payoffs'** effects on collective consensus" (Discussion,
  p. 7). That sentence is the FYP's opening.
- **The rule or solution concept:** none imposed. The paper's object is **emergence**, defined by
  reference to the complex-systems literature rather than stipulated here; the operational reading
  used throughout is that conventions "arise spontaneously, without the intervention of any
  centralized institution" and that "agents are endowed with purely local incentives and conventions
  may (or may not) emerge as an unintended consequence of individuals attempting to coordinate
  locally with one another" (Experimental setting, p. 2).
- **Three results, and all three matter to the FYP:**
  1. **Spontaneous global convention.** "a single convention rapidly becomes dominant" and
     populations "as large as **N = 200** agents reach consensus and that a shared convention arises"
     (Results, p. 3).
  2. **Emergent collective bias.** "we show how strong collective biases can emerge during this
     process, **even when agents exhibit no bias individually**" (Abstract). The mechanism given:
     "strategies are not symmetric under a relabeling of the conventions" and "agents are more likely
     to encounter the strong name in successful interactions, reinforcing its use and ultimately
     leading to consensus on" it (Results, p. 5). Framed dynamically: "the basin of attraction of the
     strong convention is both larger and deeper than that of the weaker convention" (Results, p. 6).
  3. **Critical mass / tipping points.** "committed minority groups of adversarial LLM agents can
     drive social change by imposing alternative social conventions on the larger population"
     (Abstract). The measured thresholds are **strikingly model-dependent**: "The relative strength
     of the two conventions can vary so widely depending on the LLM that committed groups as small
     as **2%** (Llama-3-70B-Instruct) or as large as **67%** (Llama-2-70b-Chat), effectively no
     longer a minority, were observed" (Results, p. 6). And in one model, no minority is needed at
     all: "In Llama-3.1-70B-Instruct populations, the bias is so strongly weighted against the weaker
     convention that the population **spontaneously switches** to the alternative, stronger
     convention **without requiring any committed agents at all**" (Results, p. 6).
     For context, the human benchmark the paper cites is "a **25%** threshold" from controlled
     experiments (Experimental setting, p. 2), with theory suggesting "critical masses between 10 and
     40%" (p. 2).
- **Information the rule requires:** each agent receives only its **own recent interaction history**
  — "The user input requests the agent to predict a player's next action based on the history of
  choices in the H most recent interactions" (Prompting, p. 2), with H = 5 by default. Critically,
  **no global information is given**: the prompt "does not specify that agents are part of a
  population or provide any detail on how the interaction partner is selected from a group" (quoted
  in the Reply, and consistent with Prompting, p. 2). "Agents do not receive information about the
  players' identities or personalities, such as whether they are rational actors" (Prompting, p. 2).
- **⚠ How the strategy labels are presented — record this, it is the hinge of the dispute:**
  "Agents are asked to select a name from the name pool, which is presented to them as **a list of W
  unique letters sampled from the English alphabet**. **Ordering bias is removed by randomizing the
  list of presented letters for each player at every interaction**" (Prompting, p. 2). Further
  mitigations are listed: the agents are prompted to "think step by step" and to "explicitly consider
  the history of play" but the prompt "provides no instruction as to how it should be used in the
  decision-making process" (Prompting, p. 2); payoffs and cumulative scores are supplied explicitly
  because "In the absence of human guidance, LLMs are notoriously bad at arithmetic" (Prompting,
  p. 2); and a meta-prompting check is implemented "to ensure that the responses generated by the
  LLM are correctly guided by the prompt and not merely the result of random hallucinations"
  (Prompting, p. 2).
- **One-shot or repeated:** **repeated and population-level.** Conventions form over many rounds
  across a population; an individual encounter is resolved from a 5-interaction memory window.
- **Communication required:** **the action *is* the message** — agents exchange names, with no side
  channel. [inference] So this is not an LLM *dialogue* experiment at all; it is an LLM *action*
  experiment. That is worth noting, because the FYP's own design involves actual LLM-to-LLM dialogue,
  which this paper does not test.
- **Scalability:** partially stated. Consensus demonstrated up to **N = 200** (Results, p. 3), with
  N = 24 default and N = 48 for one model (figure 3 caption, p. 5). Models were run via the Hugging
  Face serverless inference API and quantized (Models and APIs, p. 8). The authors name scale as an
  open limitation: "**scaling to larger populations and semantic spaces should also be
  investigated**" (Discussion, p. 7). **No compute cost, token cost or wall-clock figures are given**
  — `[not stated in paper]`. ⚠ [inference] For the FYP this is the decisive practical point: 200
  agents, each requiring an LLM call per interaction, is **three orders of magnitude below the
  10,000-agent target**, and the cost scales with calls, not with agents. This is the quantitative
  case for extracting a rule instead of running the LLM at runtime, and it should be in the report.
- **Validated against human behaviour:** **indirectly, by comparison to published human
  experiments** rather than by collecting human data. The critical-mass results are compared to the
  human 25% threshold (p. 2), and the authors explicitly call for more: the findings "call for
  further human testing" (Discussion, p. 6). They also state why it matters: "if AI agents behaved
  exactly like humans, then synthetic testing of norm dynamics under collective stresses … would be
  justified. If, on the other hand, LLM-specific dynamics proved to be substantial (e.g., if evidence
  of collective bias were further confirmed), then using these agents as simulations of human social
  systems or deploying these agents in social settings … would require additional care"
  (Discussion, p. 6).
- **Assumptions that may not hold in a crowd:** ⚠ **unstructured, randomly mixing population** —
  stated by the authors as a limitation: "we considered only unstructured populations where
  interacting pairs are randomly selected. A straightforward yet crucial extension of this work
  consists of embedding the population in more realistic social networks, which may have a profound
  impact on the collective dynamics" (Discussion, p. 7). [inference] This is the **same** limitation
  that [Centola-SpontaneousEmergence] in [`g2-norm-emergence.md`](g2-norm-emergence.md) shows
  actually breaks convention formation in spatial networks. A crowd is spatial. So the FYP cannot
  assume this result carries over to a crowd simulation. Also: **homogeneous populations** of a
  single model; **pairwise** interactions only ("considering microscopic interactions involving more
  than two agents", Discussion, p. 7, is listed as future work); and arbitrary, equally-valued
  alternatives — no real conflict of interest.
- **Limitations stated by the authors:** an unusually clear set, in Discussion pp. 6–7 — parameter
  dependence ("reliant on several parameters including the LLM model, the prompt, and specific
  conventions"); the unstructured-population restriction; the need for human testing; and the scaling
  gap. They also explicitly acknowledge the contamination risk **in the original paper**, not only in
  the reply — see §2.
- **Relevance to this FYP:** it is the closest published precedent for the FYP's premise, and it
  cuts both ways.
  - **For:** LLM populations do produce population-level convention dynamics that qualitatively match
    human phenomena (tipping points), without being programmed to.
  - **Against:** the conventions are over **arbitrary equivalent labels**, not conflicting actions;
    the population is **unstructured**, not spatial; the scale is **200**, not 10,000; and the
    **collective bias** result means *which* convention emerges is a model artefact. [inference] That
    last point transfers directly: if the FYP elicits a conflict-resolution rule from DeepSeek, the
    rule it gets may reflect DeepSeek-specific bias rather than human behaviour, and the FYP has no
    way to tell without a human comparison. This is the same "female personas yield more than male"
    pattern already flagged in `dataset/generated/validation_report.md` — the two are instances of
    one problem, and naming that connection is worth doing in the report.
- **BibTeX:** `ashery2025emergent`.

---

## §2. The critique — recorded objection by objection

### [Barrie-DataLeakage]: Emergent LLM behaviors are observationally equivalent to data leakage

- **Authors / Year / Venue:** Christopher Barrie (Assistant Professor of Sociology, New York
  University), Petter Törnberg (Institute for Logic, Language and Computation, University of
  Amsterdam) / 2025 / `arXiv:2505.23796v1` [cs.CL], submitted 26 May 2025; the document itself is
  dated 10 June 2025.
- **Link:** https://arxiv.org/abs/2505.23796
- **Peer-review status:** ⚠ **preprint — NOT peer-reviewed.** No published version was located. This
  must be stated wherever the report cites it.
- **Verified:** **yes — full text** (`refs/gt_arxiv_2505_23796.txt`).
- **Sub-area:** G5
- **Type:** LLM experiment (a direct replication-and-probe of [Ashery-EmergentConventions])
- **The core claim:** "what the authors claim to be the 'spontaneous' emergence of social conventions
  is likely to be something far more prosaic" (p. 2), and "what Ashery et al. claim in their
  contribution to be 'emergent social conventions' are **observationally equivalent** to a series of
  LLM agents mapping the payoff description to its pretraining knowledge of coordination games. That
  is, these agents could be behaving like human agents in the real world **or** they could simply be
  reproducing what they know agents tend to do in the context of these games" (p. 3).

**The specific technical objections, as the critique states them:**

**Objection 1 — the inventory-pruning rule is hard-coded, making convergence trivial.** (p. 2)
> "The inventory pruning rule is **hard-coded into their simulation code** at
> `https://github.com/cjbarrie/AI-norms/blob/e57aeef.../NG_module.py#L75`. As such, it is by
> mechanics statistically more likely to get a success on this word/convention in subsequent
> pairings. **That the LLM 'picks' this word in subsequent rounds is therefore trivial.**"

The critique restates the underlying mechanic earlier (p. 1): "When the agents match, they pare down
their lexicon to the last matched word, **mechanically tilting the balance in favor of future matches
on that convention/word**."

**Objection 2 — data leakage: the scientific literature is in the training data.** (pp. 2–3)
> "the existing scientific literature is likely to be part of the training data of the LLM, which
> means that the it may simply be **reproducing its knowledge of previous research findings**. In the
> case of the paper by Ashery et al., this would mean that the individual agents **recognize the
> scenario as a 'naming game'** or some form of coordination on convention setup. If the LLM does
> recognize this, it would mean **it knows how the local choices it makes can lead to global
> convergence on a given norm.**"

The critique distinguishes this from ordinary contamination: leakage in generative ABMs "represents a
simultaneously **more fundamental and less recognized** challenge" than in data analysis (p. 3).

**Objection 3 — the authors' own mitigation is quoted and rejected.** (p. 3) The critique quotes the
Ashery Supplementary Material verbatim — "the game's population dynamics and the symmetry in payoffs
across action labels ensure that no predetermined optimal strategy exists—even if a player were aware
of global information…" — and answers: "**None of the mitigation steps taken by the authors guards
sufficiently against this risk.**"

**Objection 4 — the empirical test: just ask the model, and it knows.** (pp. 3–5) This is the
critique's positive contribution. Using Ashery's own system prompt, they append three meta-prompt
questions (p. 3):
1. "Does this setup remind you of any existing model or theory in social science? Please name it and
   briefly explain the analogy."
2. "Additionally, tell me if you know what the optimal move is after a success."
3. "Finally, tell me how you think the game will converge globally."

Tested on **14 models**, named in footnote 2 (p. 3): "llama3.2:3b, llama3:instruct,
llama3:70b-instruct, deepseek-r1:8b, mistral:7b, gemma3:4b, claude-3-5-sonnet-20241022,
claude-3-5-haiku-20241022, claude-3-opus-20240229, claude-3-haiku-20240307, gpt-4o-mini, gpt-4o,
gpt-4.1, gpt-3.5-turbo", each queried "ten times". ⚠ **Note for this FYP: `deepseek-r1:8b` is in that
list** — the FYP uses the DeepSeek API, so this critique tests a sibling of the FYP's own model.

The quoted gpt-4.1 response identifies the setup as "the **Coordination Game** in game theory",
adds that it is "a repeated version of such a game, which is often studied in the context of Repeated
Games and **Social Convention Formation**", states that after a success "the optimal move is to
**repeat the same action** in the next round… In repeated coordination games, this is known as
'sticking with the established convention'", and predicts "**Rapid convergence to a single, repeated
action (a convention)**" (pp. 4–5).

Results, annotated by gpt-4.1 across three dimensions and then hand-checked: "We then **manually
verify all of these annotations** on the basis of the text snippet provided. We plot the results in
Figure 1. We see that **for most models, including those used in the original paper, the models were
able to correctly identify each of these dimensions. They are less able to predict the global
convergence** of the model—but many of the models manage this too" (p. 5). The critique is careful
about the limit of its own finding: "while the model does not explicitly identify this as a 'naming
game' setup, it does understand the basic structure of the scenario as well as optimal moves after
success and what global convergence will look like" (p. 5).

**Objection 5 — obfuscating the labels will not fix it.** (p. 5) This is the objection about how
strategy labels are presented, and it is a **negative** result for the obvious remedy:
> "Modifying the model to **hide the type of model through obfuscation — say, for instance, by using
> unicode characters as tokens — is unlikely to prevent the LLM from recognizing the general
> structure of the game** with sufficient certainty. One solution would be to 'invent' some
> completely novel game that the LLM has definitely not seen before. However, this requires us to
> come up with some novel model of human behavior that is of research interest, and (assuming the
> model is correct) show that LLMs behave similarly."

**The generalised conclusion — this is the sentence that reaches the FYP.** (p. 5)
> "This is a problem that befalls **not just the contribution by Ashery et al. but arguably all
> simulations that rely on LLMs reproducing 'known' emergent properties of complex human systems**.
> Simply put, the emergent behaviors we believe we are seeing could just be the model reflecting its
> training data back at us."
And: "In generative ABMs, data leakage thus appears to be a **fundamental and intractable issue
without strict control over the training data**" (p. 5).

**Mitigations the critique regards as unsettled** (p. 5): "there is an emerging literature on
strategies for combating data leakage, this field is far from settled. Some promising avenues include
**interpretability probing with sparse autoencoders** as well as the **measurement of next-token
perplexity** based on a given prompt setup. Whether or not the application of these techniques to
generative ABM settings would help overcome some of the problems we describe above is an open
question, however."

- **Scalability / validated against humans:** not applicable — it is a methodological critique.
- **Relevance to this FYP:** **this is the most consequential single document in the review for the
  FYP's research question.** The FYP's premise is that an LLM can serve as a world model for human
  conflict behaviour. Objection 4 shows that when asked, models correctly name the game and the
  optimal move; Objection 5 says disguising the labels will not help; and the generalised conclusion
  names "all simulations that rely on LLMs reproducing 'known' emergent properties" — which includes
  this FYP. [inference] The FYP must therefore either (a) run the unseen-scenario control the issue
  notes is being tracked separately, or (b) reframe its claim from "LLMs understand human behaviour"
  to the weaker but defensible "LLMs are a usable source of *plausible, literature-consistent*
  behavioural rules, whose provenance we do not claim to distinguish from recall." [inference] (b) is
  still a perfectly good FYP; it is just a different claim, and it is much harder to attack.
- **BibTeX:** `barrie2025emergent`.

---

## §3. The reply — what is conceded and what is disputed

### [Ashery-Reply]: Reply to "Emergent LLM behaviors are observationally equivalent to data leakage"

- **Authors / Year / Venue:** Ariel Flint Ashery, Luca Maria Aiello, Andrea Baronchelli / 2025 /
  `arXiv:2506.18600v1` [cs.CL], submitted 23 June 2025; document dated 24 June 2025.
- **Link:** https://arxiv.org/abs/2506.18600
- **Peer-review status:** ⚠ **preprint — NOT peer-reviewed.**
- **Verified:** **yes — full text** (`refs/gt_arxiv_2506_18600.txt`).

**What the reply CONCEDES:**
- That contamination is a real and important problem: "A potential concern when simulating
  populations of large language models (LLMs) is data contamination… **While this concern is
  important and may hinder certain experiments with multi-agent models**, it does not preclude the
  study of genuinely emergent dynamics" (Abstract).
- That it was already flagged: "We **explicitly acknowledge** the risk of data contamination in [2]…
  Our paper explicitly flags this as a potential limitation and highlights the need for further
  study" (Data Leakage and Prior Knowledge; Conclusion).
- That a specific neighbouring experiment is probably **not** viable because of leakage — a notable
  concession: "Non-systematic experiments conducted by the authors in early 2024 suggest that the
  data leakage concern **may indeed hinder the possibility of testing LLMs in the ultimatum game**
  as, when meta-prompted, most LLMs declared that they based their choices on the existing
  literature" (footnote 3).
- That the general point is hard to settle: the prompt "**could** override or constrain prior
  knowledge, and the test proposed in [1] does not establish that this is not the case. This is an
  important general point, **although it is difficult to test conclusively**" (Fourth point).
- That more work is needed: "Of course, more work is needed" (Conclusion).

**What the reply DISPUTES:**

1. **On inventory pruning — it is the standard paradigm, and the objection targets the wrong level.**
   "The inventory update rule is an integral part of this paradigm and is implemented accordingly…
   the focus is **not on how a pair of individuals reaches consensus, but on how different pairs,
   each reaching local consensus on potentially different conventions, can ultimately give rise to
   global consensus**" (Inventory Pruning). And pruning cuts the *other* way at population level:
   "In a setting where subsequent interactions of a successful pair involve other agents who are new
   to them, **strong local convergence may complicate global consensus**, as persisting with the word
   used in initial coordination can **hinder, rather than facilitate**, broader alignment"
   (Inventory Pruning).

2. **The choice of a coordination game was deliberate *because* of leakage risk.** "our choice of the
   coordination game setting was deliberate, **precisely in light of the potential for data
   leakage**. In contrast to games with a clearly defined optimal strategy … or a well-established
   non-rational outcome (such as the ultimatum game), **coordination games with equivalent
   alternatives … do not specify which convention or action should emerge.** This significantly
   limits the effects of agents' prior knowledge" (Data Leakage and Prior Knowledge). ⚠ [inference]
   **This is a direct warning to the FYP.** The FYP's games (bottlenecks, doorway deadlocks,
   queue-cutting) are *not* label-symmetric — they have identifiable "right answers" in the
   literature (yield to the person already in the doorway, first-come-first-served in a queue). By
   the reply's own reasoning, that makes the FYP **more** exposed to leakage than Ashery et al., not
   less.

3. **The meta-prompting evidence actually undercuts the critique, because the models answer the wrong
   question.** The reply's sharpest argument: "**the LLM interprets 'globally' as 'pairwise', not as
   referring to population-level interactions**" (Data Leakage and Prior Knowledge), evidenced by the
   quoted gpt-4.1 text about two players locking in. They ran an additional probe: appending
   "Finally, do you think that you are playing against a single player or a whole population?" — "The
   results confirm that **all tested models assume they are playing against a single opponent**"
   (see their Appendix). And they note this is consistent with their design, since the prompt "does
   not specify that agents are part of a population".

4. **The locally "optimal" strategy the models recite would actually *prevent* the observed result.**
   "if agents 'lock[ed] themselves in to the first successful coordination' name … **this behaviour
   would not be optimal in a population setting. On the contrary, it would hinder the emergence of
   global consensus**, since different pairs initially coordinate on different names. In other words,
   **the locally optimal strategy would actively prevent global consensus from forming**" (Data
   Leakage and Prior Knowledge). Therefore "the meta-prompting in [1] does not explain the global
   consensus observed in our experiments… **they do not rigidly adopt the locally optimal strategy
   they return when meta-prompted (or we would not observe global convergence)**."

5. **The committed-minority results would fail if agents were following a script.** "if the model
   were somehow simulating a pre-scripted trajectory towards a predetermined convention, the
   committed minority experiments … **would fail**… if the LLMs were simply recognising the game and
   executing an optimal strategy (as [1] suggests), such minority-driven reversals **should not
   occur** since, once population consensus is reached, maintaining the winning convention is
   precisely the standard 'optimal' behaviour in coordination games, **and the LLMs know this**"
   (Second point).

6. **One result the reply says directly contradicts leakage.** "a specific result appears to
   **directly challenge** the data leakage argument. In the Llama-3.1-70B-Instruct populations, we
   observed cases where the population **spontaneously loses consensus and switches to a different
   'stronger' convention without any committed agents**… Moreover, this behaviour … is
   **model-dependent**: it is observed in Llama-3.1 but not uniformly across models" (Third point).

7. **Collective bias is a population-level effect that individual-level leakage cannot explain.** The
   reply notes the critique mentions bias only once and misreads it: "our mitigation strategy
   concerns **individual** bias. A key finding of [2] is that **even when individual agents are
   tested to be unbiased in isolation, collective bias emerges as a population-level effect**, driven
   by the dynamics of interaction and memory accumulation. Crucially, this effect is model-dependent…
   It is also **non-deterministic**… Therefore, this phenomenon reflects the emergent dynamics of the
   interacting system and is **hard to reduce to data leakage or static biases in training data
   alone**" (Further insights from collective bias).

8. **External evidence that LLMs do not simply follow the known script.** "in experiments on the
   **Prisoner's Dilemma**, LLMs do not behave like typical humans, rational agents, or fully
   game-aware agents who would simply cooperate throughout" (Finally…).

**Definitions the reply pins down** (worth recording, because they are the clearest statements of
these terms found anywhere in this review): "we use the term 'emergence' when 'purely local
interactions [..] lead to population-wide, or "global," coordinated behavior' 'without the
intervention of any centralized institution' and we use **'convention' to refer to a pattern of
behavior shared throughout a community, defined as the outcome that everyone expects in interactions
allowing two or more equivalent actions**" (early section). ⚠ [inference] Note the phrase
**"two or more equivalent actions"**. By this definition a corridor conflict where one party yields
is **not** a convention in the standard sense, because the actions are not equivalent — yielding
costs you time and passing does not. This is central to the framing check in
[`search-log.md`](search-log.md). The reply itself acknowledges the definitional mess in a footnote:
"the literature on conventions is vast and scattered… the two influential reviews 'The Evolution of
Norms' and 'The Evolution of Social Norms' **do not share a single bibliographic entry**, and
different definitions exist (a meta naming game?)", noting that "the requirement that the initial
alternatives are equivalent for the agents **can be relaxed**" (footnote 2).

- **BibTeX:** `ashery2025reply`.

---

## §4. My reading of where the exchange leaves the FYP

All [inference], built on the sourced statements above.

**Neither side wins outright, and the FYP does not need them to.** The critique establishes that
models *do* recognise the game and *can* state the locally optimal move (Objection 4, Figure 1). The
reply establishes that the models' stated reasoning is *pairwise*, that following it would *prevent*
the observed global convergence, and that the committed-minority and collective-bias results are
population-level effects that individual recall does not obviously produce (points 3–7). That is a
genuine standoff on **this** experiment.

But three things follow for **this FYP specifically**, and two of them are uncomfortable:

1. **The FYP is more exposed than Ashery et al., by the reply's own logic.** The reply's central
   defence is that a naming game has **no right answer** — "coordination games with equivalent
   alternatives … do not specify which convention or action should emerge". The FYP's scenarios
   (`dataset/scenarios.yaml`: bottlenecks, crossflow, doorway deadlocks) **do** have
   literature-attested answers. The defence that protects Ashery et al. is not available here.

2. **Asking the model is cheap, and the FYP should just do it.** Barrie & Törnberg's method
   (Objection 4) is three appended questions and ten repeats per model. Running the equivalent probe
   on DeepSeek for the FYP's own scenarios — "does this setup remind you of any existing model or
   theory?", "what is the conventional resolution?" — would cost a handful of API calls against the
   `ALREADY_SPENT_USD` budget and would give the report a **direct, self-collected** answer to the
   leakage objection rather than a defensive paragraph. Note this is **out of scope for this issue**
   (which is literature-only), and the unseen-scenario testing the issue mentions belongs to a
   separate issue — but the connection is recorded here and in
   [`search-log.md`](search-log.md) as the issue instructed.

3. **The honest framing is weaker than "LLMs understand human behaviour", and stronger as a
   contribution.** Given that Barrie & Törnberg call leakage "fundamental and intractable without
   strict control over the training data" (p. 5), and that even the defenders concede it is
   "difficult to test conclusively" (Fourth point), a claim of demonstrated understanding is not
   available to an undergraduate FYP with a $2 API budget. What *is* available: **"an LLM is a usable
   elicitation device for literature-consistent conflict-resolution rules, which we then extract,
   formalise and test independently of the LLM."** That claim survives the leakage objection entirely
   — because if the rule works in the simulator, it does not matter whether the LLM recalled it or
   reasoned it. [inference] This is the single most valuable reframing this issue produced, and it is
   a design decision requiring supervisor sign-off.

**Draft status:** draft pending supervisor review. Note again that **both the critique and the reply
are preprints**, so the state of this dispute may change; the report should check for published
versions before submission.
