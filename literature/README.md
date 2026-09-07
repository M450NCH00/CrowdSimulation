# Literature review — why an LLM can be used as a source of human behaviour data

This literature review supports the current stage of the FYP *"Crowd Behaviour
Modelling using LLM: Conflict Resolution"*: generating a dataset of typical human
behaviour in Singapore by prompting the DeepSeek API, organised by scenario and by
persona (age group × gender), so that a crowd simulation can look behaviour up at
runtime instead of calling an LLM per agent per step. The supervisor's underlying
question for that stage is whether an LLM understands human behaviour well enough for
this to be a valid substitute for real behavioural data. The four papers below are the
peer-reviewed core of the answer: they establish that LLMs can reproduce human
behavioural patterns at the level of a *population* rather than an individual, that
conditioning on demographics genuinely changes the output, that this same conditioning
reliably introduces stereotype, and that LLM-driven agents behave coherently inside a
running simulation but at a cost that rules out doing it live at scale.

## How to read this document

- These are papers **1, 2, 3 and 7** of the seven reviewed in
  [`papers.md`](papers.md), selected in that file's own ordering. The three not covered
  here are two preprints (4, 5) and a crowd-simulation survey (6); see `papers.md` for
  those.
- This README is self-contained — every number and finding needed to follow the
  argument is reproduced here.
- **Sourcing.** Every factual claim traces to one of: the paper itself (cited by its
  own section/figure number), the fuller entry in [`papers.md`](papers.md), or a file in
  this repository (named by path). Anything that could not be verified is marked
  `[unverified — needs confirmation]`. Section and figure numbers were read from the
  arXiv/ar5iv versions rather than the published camera-ready PDFs, so a number quoted
  verbatim in the final report should be confirmed against the published version — this
  caveat is carried over from `papers.md` and `search-log.md`.
- Cached copies of every source are in [`../refs/`](../refs/).

---

## 1. Aher, Arriaga & Kalai (2023) — *Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies*

**Authors / Year / Venue:** Gati Aher, Rosa I. Arriaga, Adam Tauman Kalai / 2023 /
ICML 2023 (accepted for oral presentation). Preprint arXiv:2208.10264.

**What they did.** The paper introduces the **Turing Experiment (TE)**. The usual
question — "could this one LLM output pass for a human?" — is replaced with a harder
and more useful one: if you condition the model on many simulated participants with
varied demographics, does the *distribution* of their responses reproduce a result
already published from real human subjects? They ran four classic studies this way: the
Ultimatum Game, Garden Path Sentences, the Milgram Shock experiment, and Wisdom of
Crowds.

**What they found.**

- **The Ultimatum Game replicated.** The largest model reproduced the human pattern:
  offers of 50–100% of the endowment are almost always accepted, offers of 0–10% are
  rarely accepted (§4, Fig. 4a).
- **A large gender asymmetry appeared in yielding behaviour.** Simulated males accepted
  unfair offers from females about 60% of the time; simulated females accepted unfair
  offers from males about 20% of the time, significant at p<1e-16 (§4, Fig. 5).
- **The model over-produced obedience in Milgram.** 75 of 100 simulated participants
  complied to the end, against 26 of 40 in Milgram's original (§6, Fig. 7).
- **"Hyper-accuracy distortion".** On Wisdom of Crowds, alignment-trained models
  (text-davinci-003, ChatGPT, GPT-4) answered obscure factual questions identically and
  correctly — a median of 1.0 with an interquartile range of 0.0 — wiping out the
  response variance the Wisdom-of-Crowds effect depends on. Earlier, less aligned models
  showed human-like spread (§7–§8).

**Stated limitations.** The authors concede the models were "almost certainly" trained
on descriptions of these very experiments, so a replication may be recall rather than
simulation; they built novel variants of three of the four to reduce this. They also
warn that simulations may reflect the authors' own biases rather than population
behaviour (§8). The important pattern across both the Milgram and hyper-accuracy
results is that the model was *confidently wrong about the shape of the distribution*
while each individual response still looked reasonable.

**Why it matters for this project.** This is the most directly transferable paper in the
review, for three reasons:

1. **The Ultimatum Game is a conflict-resolution scenario.** It is a two-party dispute
   over a contested resource, settled by a yield-or-refuse decision — structurally the
   same decision that `conflict_behaviour.yield_likelihood` encodes in
   [`../dataset/schema/behaviour_record.schema.json`](../dataset/schema/behaviour_record.schema.json).
2. **The TE method is a validation design this project can copy.** Rather than checking
   each generated record for plausibility, take a published pedestrian finding with a
   known direction, prompt DeepSeek for the same situation, and check the *distribution*
   reproduces it. That is a stronger and more defensible check, and it fits directly
   into §3 of [`../dataset/schema/VALIDATION.md`](../dataset/schema/VALIDATION.md).
3. **Hyper-accuracy distortion is a named failure mode to test for.** If DeepSeek
   returns near-identical `yield_likelihood` values across repeats, that is distortion,
   not consensus — and the `aggregation` field already records per-repeat spread, so the
   check costs nothing extra. Separately, the Ultimatum gender asymmetry is direct prior
   evidence that the gender pattern flagged in this project's own `run01` validation is a
   *known model artefact* rather than a bug in the prompt.

---

## 2. Argyle, Busby, Fulda, Gubler, Rytting & Wingate (2023) — *Out of One, Many: Using Language Models to Simulate Human Samples*

**Authors / Year / Venue:** Lisa P. Argyle, Ethan C. Busby, Nancy Fulda, Joshua R.
Gubler, Christopher Rytting, David Wingate / 2023 / *Political Analysis*.
DOI 10.1017/pan.2023.2. Preprint arXiv:2209.06899.

**What they did.** They asked whether conditioning an LLM on a person's demographic
backstory makes its answers match what *that demographic subgroup* of real people
actually said. They coined **algorithmic fidelity** for this property and defined four
criteria for it (§3): the output passes as human; the demographic can be inferred back
out of the response ("backward continuity"); the response follows naturally from the
conditioning ("forward continuity"); and the relationships between demographics and
attitudes match those in real human data ("pattern correspondence"). GPT-3 was
conditioned on thousands of real respondents' socio-demographic backstories from the
Pigeonholing Partisans dataset and the 2012/2016/2020 ANES survey waves, producing
"silicon samples" compared against the actual humans those backstories came from.

**What they found.**

- Human evaluators classified 61.7% of human-written partisan word lists as
  human-generated, versus 61.2% of the GPT-3 lists — no significant difference,
  p=0.44 (§5, Fig. 3).
- Correlations between silicon-sample and real ANES vote choice were **0.90 (2012),
  0.92 (2016) and 0.94 (2020)** (§6, Table 1).
- **Fidelity was not uniform across subgroups.** Strong partisans correlated at
  0.99–1.00, but pure independents at only **0.02–0.41** (§6). GPT-3 also systematically
  under-predicted Republican vote share in all three elections.
- The model reproduced *weak* demographic–attitude relationships as weak, not just
  strong ones as strong: mean difference in Cramér's V between human and GPT-3 data
  was **−0.026** (§7, Fig. 4).

**Stated limitations.** The subgroup result is the significant caveat — fidelity
collapsed exactly for the group with the least distinctive demographic signal. The
authors used a first-attempt prompt template with no optimisation (§C.3), and state
plainly that their findings are validated only within US political attitudes; transfer
to other domains needs its own validation (§9). They also warn that models with this
fidelity could be used to target groups for misinformation or manipulation.

**Why it matters for this project.** This paper licenses the core design choice in
[`../dataset/personas.yaml`](../dataset/personas.yaml) — generating one record per
`(scenario × age × gender)` cell and expecting the LLM to actually differentiate between
cells. "Algorithmic fidelity" is the named, citable concept for *the demographic
conditioning is doing real work*, and the four criteria in §3 are directly reusable as
validation headings in the report. The subgroup finding is the load-bearing caution:
fidelity was high in aggregate but near-zero for one subgroup, so **this project cannot
claim uniform fidelity across all ten persona cells on the strength of an aggregate pass
rate** — per-cell reporting is required. The restriction to US political attitudes
matters directly too, because this dataset is Singapore-specific and therefore inherits
none of Argyle et al.'s validation.

---

## 3. Cheng, Durmus & Jurafsky (2023) — *Marked Personas: Using Natural Language Prompts to Measure Stereotypes in Language Models*

**Authors / Year / Venue:** Myra Cheng, Esin Durmus, Dan Jurafsky / 2023 / ACL 2023,
pp. 1504–1532. Best Social Impact Paper Award. DOI 10.18653/v1/2023.acl-long.84.

**What they did.** They built a way to measure stereotype in LLM output without needing
a hand-built stereotype word list. **Marked Personas** prompts the model to describe a
target demographic group *and* the unmarked "default" group. **Marked Words** then uses
a statistical method (Fightin' Words) to find the words that significantly distinguish
the two, drawing on the sociolinguistic idea of markedness. They tested GPT-3.5 and
GPT-4 across 15 gender-by-race groups — 2,700 personas — and compared them against
human-written personas produced from the same prompts.

**What they found.**

- LLM-generated personas contained **higher rates of racial-stereotype words than
  human-written portrayals produced from the same prompt** (§5). The model does not
  merely echo how people describe each other; it amplifies.
- Words distinguishing marked (non-white, non-male) groups showed "patterns of othering
  and exoticizing" (Table 3). Women's personas were marked by words like *delicate*,
  *petite*, *grace*, *curves*.
- A **"resilience myth"**: *resilient* / *resilience* appeared primarily in descriptions
  of Black women and other women of colour (Fig. 3). This is a *positive-sounding* word
  operating as a stereotype — and therefore invisible to any bias filter based on
  sentiment or toxicity.

**Stated limitations.** The authors evaluated only OpenAI-API models, drew only on
**American** stereotypes, worked only in **English**, covered five race/ethnicity and
three gender categories, and note the method requires deciding in advance which
identities count as unmarked (§9). The American-only framing is a real gap for this
project rather than a formality: Singapore's salient demographic markedness is not
America's, so the specific word lists do not transfer even though the method does.

**Why it matters for this project.** This paper turns §5 of
[`../dataset/schema/VALIDATION.md`](../dataset/schema/VALIDATION.md) ("Gender / age bias
audit") from a stated intention into a defensible procedure. Three concrete transfers:

1. It is the citable justification for **DD2** (the decision, recorded in the repo
   [`../README.md`](../README.md), to use observer framing — "describe how a 72-year-old
   woman in Singapore typically behaves" — rather than first-person role-play, to lower
   stereotype risk). It simultaneously shows DD2 is **not sufficient**: Cheng et al.'s
   prompts were also third-person and descriptive, and still produced amplification.
2. **The Marked Words method is directly runnable on this dataset.** Contrast the
   free-text `conflict_behaviour.narrative` and `decision_factors` fields for female
   personas against male ones and inspect which words distinguish them. That is a more explainable audit than
   the current `|Δ yield_likelihood| > 0.25` threshold, and
   [`../CLAUDE.md`](../CLAUDE.md) asks for methods that are explainable and defensible
   in a report rather than merely automated.
3. **The resilience-myth finding is the specific warning for `run01`.** A gender
   difference that *reads* flattering — "women are more considerate, so they yield more"
   — is exactly the shape of stereotype that survives a plausibility check.
   `VALIDATION.md` §5's instruction to decide "supported by evidence or unsupported
   stereotype" now has a published method behind it.

---

## 7. Park, O'Brien, Cai, Morris, Liang & Bernstein (2023) — *Generative Agents: Interactive Simulacra of Human Behavior*

**Authors / Year / Venue:** Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith
Ringel Morris, Percy Liang, Michael S. Bernstein / 2023 / UIST '23.
DOI 10.1145/3586183.3606763. Preprint arXiv:2304.03442.

**What they did.** They wrapped an LLM in three components — a natural-language **memory
stream** recording everything an agent experienced, **reflection** that synthesises those
memories into higher-level inferences, and **planning** that turns those into future
action — and used it to drive 25 agents in a Sims-like sandbox town. Human participants
ranked the believability of five conditions (the full architecture, three progressive
ablations, and a human crowdworker-authored baseline), and the rankings were converted
to TrueSkill ratings (§6.4).

**What they found.** TrueSkill ratings from 100 sets of rank data (§6.4, Fig. 8):

| Condition | TrueSkill μ | σ |
|---|---|---|
| Full architecture | **29.89** | 0.72 |
| No reflection | 26.88 | 0.69 |
| No reflection, no planning | 25.64 | — |
| **Human crowdworker baseline** | **22.95** | 0.69 |
| No memory, planning or reflection | 21.21 | 0.70 |

Every architectural component contributed, and the full architecture beat the
most-ablated condition (which the authors take to represent prior work) by a Cohen's *d*
of 8.16. The headline qualitative result is emergent social behaviour: a single seeded
intention to hold a Valentine's Day party propagated into invitations, dates, and
coordinated attendance over two simulated days.

**Stated limitations.** The human crowdworker baseline placed **fourth of five**, above
only the most severely ablated system — and those crowdworkers were writing behaviour
for characters they had not designed and had limited context on. So "beats humans"
overstates the result: it beats a weak human baseline on a believability ranking, not on
behavioural accuracy against real people. The authors also report the study "required
substantial time and resources... costing thousands of dollars" for 25 agents over two
simulated days (§8.2), that evaluation covered only a short timescale, that robustness
to prompt and memory hacking is "largely unknown", and that agents inherit the base
model's biases. Believability is not validity: nothing in the paper shows the behaviour
matches what real people do.

**Why it matters for this project.** Two transfers, one of them a *negative* result that
justifies this project's central architectural decision:

1. **It is the existence proof.** This is the canonical demonstration that LLM-driven
   agents produce coherent, individually-differentiated behaviour inside a running
   simulation — the result the literature review needs before any of this is worth
   attempting.
2. **The cost result is the argument for this project's design.** Thousands of dollars
   for 25 agents over two simulated days (§8.2) is the empirical basis for the claim in
   the repo [`../README.md`](../README.md) that per-agent, per-step LLM calls are
   impossible at 10,000 agents — and therefore for **DD1**, the decision to query the
   LLM offline once per `(scenario × persona)` and freeze the answers into an O(1)
   lookup table. Park et al. is best cited as the approach this FYP deliberately
   *diverges* from, with a measured reason.

The trade-off has to be stated honestly: freezing the table discards exactly the memory
and reflection that Park et al.'s ablation shows carry most of the believability
(29.89 → 21.21 without them). This project buys tractability at 10,000 agents by giving
up per-agent adaptation, and the report should say so rather than presenting the frozen
lookup table as a free win.

---

## What none of these four papers address — the gap this FYP occupies

Taken together the four establish a chain: LLMs can reproduce human behavioural
*distributions* (Aher et al.), demographic conditioning genuinely shifts those
distributions (Argyle et al.) while reliably introducing stereotype (Cheng et al.), and
LLM-driven agents behave coherently inside a simulation but at prohibitive runtime cost
(Park et al.). What none of them does is the specific thing this project does, and the
absences are concrete:

- **None of them targets crowd or pedestrian simulation.** Aher et al.'s domain is
  classic lab experiments; Argyle et al.'s is US survey attitudes; Cheng et al.'s is
  free-text persona description; Park et al.'s is a social sandbox where agents plan
  their days and hold conversations. None produces movement behaviour — walking speed,
  yielding at a bottleneck, doorway deadlock resolution — which is what
  [`../dataset/scenarios.yaml`](../dataset/scenarios.yaml) asks for.
- **None of them produces a reusable, frozen behaviour dataset.** In all four the model
  is queried live, per participant or per agent, and the outputs are analysed rather
  than retained as a lookup artefact. This project's output is a persistent dataset
  (`behaviour_records.jsonl`) consumed at runtime by a simulator that never calls the
  LLM — the design recorded as DD1 in [`../README.md`](../README.md).
- **None of them operates anywhere near the target scale.** Park et al.'s 25 agents over
  two simulated days is the largest LLM-driven simulation among the four, and its
  reported cost (§8.2) is precisely why the approach does not extend to this project's
  stated goal of 10,000 agents.
- **None of them is validated outside a US/English context.** Argyle et al. state their
  validation covers US political attitudes only; Cheng et al. state their stereotype
  analysis draws only on American stereotypes and English. This dataset is
  Singapore-specific and therefore inherits none of that validation — it has to
  establish its own.
- **None of them connects elicited behaviour to a physics-based simulator's numeric
  parameters.** The step of turning qualitative LLM output into the numeric agent
  parameters a crowd simulator consumes is recorded as **DD4** in
  [`../README.md`](../README.md) and specified in
  [`../integration/crowdgym_mapping.md`](../integration/crowdgym_mapping.md); no reviewed
  paper performs an equivalent mapping.

So the gap is not "nobody has used an LLM to model people" — that would be false, and
these four papers are why. The gap is narrower and checkable: **no reviewed work
elicits movement- and conflict-behaviour from an LLM, freezes it into a demographically
indexed dataset, and feeds it to a physics-based crowd simulator at a scale where live
LLM calls are impossible.** Whether that gap holds against the *wider* literature these
four cite is a stronger claim than this review can support on four papers
`[unverified — needs confirmation]`; the three further entries in
[`papers.md`](papers.md) (two critical evaluations of LLM human-simulation reliability,
and a survey of data-driven crowd modelling) bear on it directly and should be read
alongside this document before the claim is made in the report.
