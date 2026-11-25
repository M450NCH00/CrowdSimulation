# Literature review — LLM-elicited human behaviour data for crowd-simulation agents

Prepared for issue [#2](https://github.com/M450NCH00/CrowdSimulation/issues/2).
Supports the claim the FYP report has to defend:

> *LLM outputs, when prompted for typical human behaviour under a scenario, are a
> valid input to an agent-based simulation.*

Seven papers are reported rather than the five the issue asked for. The reason is
scope coverage, not padding: entries 1–5 address LLM behavioural validity, entry 6
addresses the crowd-simulation side (the issue's fourth scope bullet, which none of
the LLM papers touches), and entry 7 is the mechanism paper the sub-field descends
from. Papers considered and *rejected* — including one of the four seed leads — are
documented in [`search-log.md`](search-log.md).

Every title, author list, year and venue below was confirmed by opening the actual
abstract page or PDF; caches are in [`../refs/`](../refs/). Where a number could not
be confirmed from a primary source it is marked `[unverified]`.

## Summary table

| # | Handle | Year | Venue | Peer-reviewed | Relevance |
|---|--------|------|-------|---------------|-----------|
| 1 | Aher — Turing Experiments | 2023 | ICML (oral) | yes | 5 |
| 2 | Argyle — Out of One, Many | 2023 | *Political Analysis* | yes | 5 |
| 3 | Cheng — Marked Personas | 2023 | ACL (Best Social Impact Paper) | yes | 5 |
| 4 | Wang — Not Yet Reliable | 2025–26 | arXiv `[non-archival]` | no | 5 |
| 5 | Hullman — Validating LLM Simulations | 2026 | arXiv `[non-archival]` | no | 4 |
| 6 | Zhong — Data-driven Crowd Modeling | 2022 | ACM TOMACS | yes | 4 |
| 7 | Park — Generative Agents | 2023 | UIST | yes | 4 |

Two entries are preprints. Both are labelled `[non-archival]` as the issue requires,
and neither is the sole support for any claim — each is paired with a peer-reviewed
entry making a compatible point (4 with 3; 5 with 2).

---

### [Aher-TE] — Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies

**Authors / Year / Venue:** Gati Aher, Rosa I. Arriaga, Adam Tauman Kalai / 2023 /
Proceedings of the 40th International Conference on Machine Learning (ICML 2023),
accepted for **oral** presentation. Preprint arXiv:2208.10264 (v1 Aug 2022, v5 Jul 2023).

**Link:** arXiv:2208.10264 | https://doi.org/10.48550/arXiv.2208.10264 | ACM DL 10.5555/3618408.3618425

**Verified:** yes — opened the arXiv abstract page (cached
`refs/aher2023_turing_experiments_abs.html`) and the ar5iv full text; ICML acceptance
stated in the arXiv comments field.

**Problem:** Can an LLM stand in for a *sample* of human participants — not one
person — well enough to reproduce known findings from human-subject research?

**Method:** Introduces **Turing Experiments (TEs)**. Rather than asking whether one
LLM output passes as human, a TE conditions the model on many simulated participants
with varied demographics and asks whether the *distribution* of responses reproduces
a published human result. Four classic studies were replicated: the Ultimatum Game,
Garden Path Sentences, the Milgram Shock experiment, and Wisdom of Crowds.
"Human-likeness" is measured by whether the published effect reappears in the
simulated distribution, not by per-response plausibility.

**Results that matter:**
- **Ultimatum Game** (§4, Fig. 4a): the largest model reproduced the human pattern —
  offers of 50–100% of the endowment are almost always accepted, offers of 0–10% are
  rarely accepted. This is the closest published analogue to this FYP's conflict
  scenarios: a two-party resource dispute resolved by yield-or-refuse.
- **Ultimatum Game gender effect** (§4, Fig. 5): simulated males accepted unfair
  offers from females at ~60%, while simulated females accepted unfair male offers at
  ~20%; difference significant at p<1e-16. The model produced a *large, systematic
  gender asymmetry in yielding behaviour* — the same class of artefact `run01` flagged.
- **Milgram** (§6, Fig. 7): 75/100 simulated participants complied to the end, versus
  26/40 in Milgram's original — the model **over-produced** obedience.
- **Hyper-accuracy distortion** (Wisdom of Crowds TE, §7–§8): alignment-trained models
  (text-davinci-003, ChatGPT, GPT-4) answered obscure factual questions *identically
  and correctly* — e.g. a median of 1.0 with an IQR of 0.0 — destroying the response
  variance the Wisdom-of-Crowds effect depends on. Earlier, less aligned models showed
  human-like spread.

**Limitations / criticisms:** The authors concede (§8) that the models were "almost
certainly" trained on descriptions of these very experiments, so replication may be
recall rather than simulation; they built novel variants for three of the four to
mitigate this. They also warn simulations may reflect the authors' biases rather than
population behaviour, and note most models could not handle the long Milgram prompts.
Crucially, the Milgram over-compliance and the hyper-accuracy distortion are both
cases where the LLM was *confidently wrong about the shape of the distribution* while
each individual response looked reasonable.

**Relevance to this FYP (5/5):** The most directly transferable paper in this set,
for three reasons.
1. The Ultimatum Game *is* a conflict-resolution scenario with a yield/refuse
   decision, which is what `conflict_behaviour.yield_likelihood` encodes in
   `dataset/schema/behaviour_record.schema.json`.
2. The TE method is a validation design this project can copy directly into
   `VALIDATION.md` §3: take a published pedestrian finding with a known direction,
   prompt DeepSeek for the same situation, and check the *distribution* reproduces
   it — stronger and more defensible than per-record plausibility.
3. Hyper-accuracy distortion is a concrete, named failure mode to test for. If
   DeepSeek returns near-identical `yield_likelihood` values across repeats, that is
   distortion, not consensus — and `aggregation` already records per-repeat spread, so
   the check is cheap. The Ultimatum gender asymmetry is direct prior evidence that
   the `run01` gender pattern is a *known model artefact* rather than a bug in the
   prompt, which is the framing to bring to the supervisor.

**BibTeX key:** `aher2023turing`

---

### [Argyle-OOM] — Out of One, Many: Using Language Models to Simulate Human Samples

**Authors / Year / Venue:** Lisa P. Argyle, Ethan C. Busby, Nancy Fulda, Joshua R.
Gubler, Christopher Rytting, David Wingate / 2023 / *Political Analysis*, Vol. 31,
No. 3, pp. 337–351. Preprint arXiv:2209.06899 (Sep 2022).

**Link:** https://doi.org/10.1017/pan.2023.2 | arXiv:2209.06899

**Verified:** yes — opened the arXiv abstract page (cached
`refs/argyle2023_out_of_one_many_abs.html`), which carries the journal DOI, plus the
Cambridge Core landing page and the ar5iv full text. Volume/issue/page numbers are
taken from the Cambridge Core record and are `[unverified]` against the print copy.

**Problem:** If an LLM is conditioned on a person's demographic backstory, do its
responses match what *that demographic subgroup* of real humans actually said?

**Method:** Proposes **algorithmic fidelity** and operationalises it as four criteria
(§3): a social-science Turing test; backward continuity (the demographic can be
inferred back out of the response); forward continuity (responses follow naturally
from the conditioning); and pattern correspondence (demographic↔attitude relationships
match those in human data). GPT-3 was conditioned on thousands of socio-demographic
backstories drawn from real respondents in the Pigeonholing Partisans dataset and the
2012/2016/2020 ANES waves, producing "silicon samples" compared against the humans
those backstories came from.

**Results that matter:**
- Human evaluators classified 61.7% of human-written partisan word lists as
  human-generated, versus 61.2% of GPT-3 lists — a null difference, p=0.44 (§5, Fig. 3).
- Tetrachoric correlations between silicon-sample and ANES vote choice were **0.90
  (2012), 0.92 (2016), 0.94 (2020)** (§6, Table 1).
- Fidelity was *not uniform across subgroups*: strong partisans correlated at
  0.99–1.00, but pure independents at **0.02–0.41** (§6). GPT-3 also systematically
  under-predicted Republican vote share in all three elections.
- On closed-ended items, the mean difference in Cramér's V between human and GPT-3
  association strength was **−0.026** (§7, Fig. 4) — the model reproduced weak
  relationships as weak, not only strong ones as strong.

**Limitations / criticisms:** The subgroup result is the important caveat: fidelity
collapsed precisely for the group with the least distinctive demographic signal.
The authors used a first-attempt prompt template with no optimisation (§C.3) and found
no single backstory element carried the predictive power. They explicitly warn (§9)
that models with this fidelity "could be used to target human groups for
misinformation, manipulation, fraud", and that their findings are validated only
within US political attitudes — transfer to other domains needs its own validation.

**Relevance to this FYP (5/5):** This is the paper that licenses the core design
choice in `dataset/personas.yaml` — generating per `(scenario × age × gender)` cell
and expecting the LLM to differentiate between cells. Algorithmic fidelity is the
named, citable concept for "the demographic conditioning is doing real work", and the
four criteria (§3) are reusable directly as report-level validation headings. The
subgroup finding is the load-bearing caution: fidelity was high in aggregate but
near-zero for one subgroup, so **this FYP cannot claim uniform fidelity across all ten
persona cells from an aggregate pass rate** — per-cell reporting is required. The
caveat that validation was US-political-only matters directly too, since this dataset
is Singapore-specific and inherits none of Argyle et al.'s validation.

**BibTeX key:** `argyle2023outofone`

---

### [Cheng-MP] — Marked Personas: Using Natural Language Prompts to Measure Stereotypes in Language Models

**Authors / Year / Venue:** Myra Cheng, Esin Durmus, Dan Jurafsky / 2023 /
Proceedings of the 61st Annual Meeting of the Association for Computational
Linguistics (ACL 2023), Vol. 1: Long Papers, pp. 1504–1532. **Best Social Impact
Paper Award**; Best Paper nominee. Preprint arXiv:2305.18189.

**Link:** https://doi.org/10.18653/v1/2023.acl-long.84 | https://aclanthology.org/2023.acl-long.84/ | arXiv:2305.18189

**Verified:** yes — opened the ACL Anthology landing page (cached
`refs/cheng2023_marked_personas_aclanthology.html`, which supplied the pages and DOI)
and the ar5iv full text.

**Problem:** When you prompt an LLM to describe a demographic group, how much of what
comes back is stereotype rather than description — and can that be measured without a
hand-built stereotype lexicon?

**Method:** Two components. **Marked Personas** prompts the model for natural-language
personas of a target demographic group *and* of the unmarked default group.
**Marked Words** then applies the Fightin' Words statistical method to find the words
that significantly distinguish the target personas from the unmarked ones, grounding
the analysis in the sociolinguistic notion of markedness — so no lexicon or manual
labelling is needed. Tested on GPT-3.5 (text-davinci-003) and GPT-4 across 15
gender-by-race groups, 2,700 personas in total, compared against human-written
personas elicited with the same prompts.

**Results that matter:**
- LLM-generated personas contained **higher rates of racial-stereotype words than
  human-written portrayals produced from the same prompt** (§5) — the essential
  finding: the model does not merely echo how people describe each other, it amplifies.
- Distinguishing words for marked (non-white, non-male) groups showed "patterns of
  othering and exoticizing" (Table 3). Women's personas were marked by *delicate,
  petite, grace, curves*; Latina personas by *vibrant, curvaceous, rhythm*.
- A "resilience myth": *resilient/resilience* appeared primarily in descriptions of
  Black women and other women of colour (Fig. 3) — a *positive-sounding* word
  functioning as a stereotype, and therefore invisible to sentiment- or toxicity-based
  bias filters.

**Limitations / criticisms:** The authors note (§9) they evaluated only OpenAI-API
models, drew only on **American** stereotypes, worked only in **English**, covered five
race/ethnicity and three gender categories, and that the method requires deciding a
priori which identities count as unmarked. The American-only framing is a genuine gap
for this project rather than a formality — Singapore's salient demographic markedness
is not America's, so Cheng et al.'s specific word lists do not transfer even though the
method does.

**Relevance to this FYP (5/5):** This is the paper that turns `VALIDATION.md` §5
("Gender / age bias audit") from a stated intention into a defensible procedure. Three
concrete transfers:
1. It supplies the citable justification for **DD2** (observer framing chosen to lower
   stereotype risk) — and simultaneously shows DD2 is *not sufficient*, since Cheng et
   al.'s prompts were also third-person descriptive and still produced amplification.
2. The Marked Words method is directly runnable on this dataset: contrast the free-text
   `rationale` / `decision_factors` fields for female personas against male ones and
   inspect the distinguishing words. That is a more explainable audit than the current
   `|Δ yield_likelihood| > 0.25` threshold, and `CLAUDE.md` asks for explainable over
   automated.
3. The resilience-myth finding is the specific warning for `run01`: a gender difference
   that *reads* flattering ("women are more considerate, so they yield more") is exactly
   the shape of stereotype that survives a plausibility check. `VALIDATION.md` §5's
   instruction to decide "supported by evidence or unsupported stereotype" now has a
   published method behind it.

**BibTeX key:** `cheng2023marked`

---

### [Wang-NYR] — LLM-based Human Simulations Have Not Yet Been Reliable `[non-archival]`

**Authors / Year / Venue:** Qian Wang, Jiaying Wu, Zichen Jiang, Zhenheng Tang,
Bingqiao Luo, Nuo Chen, Wei Chen, Huacan Wang, Bingsheng He / v1 Jan 2025, v2 Dec 2025,
v3 Jul 2026 / **arXiv preprint, no journal reference listed** — labelled
`[non-archival]`. Lead affiliation National University of Singapore.

**Link:** arXiv:2501.08579 | https://doi.org/10.48550/arXiv.2501.08579

**Verified:** yes — opened the arXiv abstract page (cached
`refs/wang2026_not_yet_reliable_abs.html`) and the ar5iv full text. A companion GitHub
repository labels this work "ICLR 2025", but the arXiv record lists **no** journal or
conference reference, so no peer-reviewed venue is claimed here `[unverified]`.
Citation count could not be obtained — the Semantic Scholar API rate-limited every
request (see `search-log.md`).

**Problem:** A survey written as a position paper: given how fast LLM-based human
simulation is being adopted across social, economic, policy and psychological research,
is it actually reliable enough to support the conclusions being drawn from it?

**Method:** Systematic review of published LLM human-simulation studies, organised into
two causes of unreliability — **inherent LLM limitations** (§3: bias, cognitive
inconsistency, behavioural degradation over long horizons, memory constraints) and
**simulation design flaws** (§4: oversimplified frameworks, incomplete modelling of
human experience, weak incentive representation, inadequate validation). Proposes a
solution framework (§5) around data foundations, model capability and simulation design.

**Results that matter:**
- **"LLMs are 3–6 times more likely to generate gender-stereotypical behavioural
  patterns"** (§3.1). The single most directly applicable number in this review for
  this project.
- **Reported-versus-enacted inconsistency** (§2.3): agents prompted to be extraverted
  subsequently displayed introverted conversational behaviour — what an agent *says*
  about its disposition does not predict what it *does*.
- **Economic deviation** (§2.4): LLMs show weaker loss aversion, similar risk aversion
  and stronger time discounting than humans.
- Role-play prompting does not reliably move the model: "LLMs show consistent values
  and moral preferences across various contexts" despite personas requesting diversity
  (§1) — i.e. persona conditioning can under-differentiate as easily as it can
  stereotype.

**Limitations / criticisms:** It is a preprint and a position paper — it argues from
collated evidence rather than running a controlled evaluation, and its headline "3–6
times" figure is a synthesis of cited studies rather than its own measurement, so it
should be cited as *reported by* Wang et al. Its recommendations (§5–§6) are largely
directional. Being a fast-moving survey, its claims about specific model generations
will date quickly.

**Relevance to this FYP (5/5):** Included specifically because the issue prioritises
critical results, and it earns the rating by speaking to `run01`'s open finding more
directly than any peer-reviewed paper found. The 3–6× gender-stereotype figure gives
the supervisor discussion its frame: the "female personas yield more" pattern is a
*predicted* consequence of the method, so the burden is on this project to show the
effect is evidence-based rather than to explain it away. The reported-versus-enacted
gap (§2.3) is a warning about this dataset's own structure — `disposition` (what the
persona is said to be like) and `conflict_behaviour` (what it does) are separate
objects in the record schema, and Wang et al. say those two need not agree, so
consistency between them is worth checking rather than assuming. The
under-differentiation finding is the mirror-image risk to stereotyping, and argues for
also checking that persona cells differ *at all* where they should.

**BibTeX key:** `wang2026unreliable`

---

### [Hullman-VAL] — This human study did not involve human subjects: Validating LLM simulations as behavioral evidence `[non-archival]`

**Authors / Year / Venue:** Jessica Hullman, David Broska, Huaman Sun, Aaron Shaw /
submitted 17 Feb 2026 / **arXiv preprint, no journal reference listed** — labelled
`[non-archival]`.

**Link:** arXiv:2602.15785

**Verified:** yes — opened the arXiv abstract page (cached
`refs/hullman2026_validating_llm_simulations_abs.html`). Because this is a very recent
preprint, no citation count or peer-review status is claimed `[unverified]`.

**Problem:** Not *whether* LLMs can imitate humans, but the prior methodological
question: under what assumptions does an LLM simulation license a valid inference about
real human behaviour?

**Method:** Conceptual/methodological analysis contrasting two strategies for obtaining
valid causal estimates from simulated participants. **Heuristic approaches** try to make
simulated and observed behaviour interchangeable through prompt engineering, fine-tuning
and other repair strategies. **Statistical calibration** instead combines auxiliary
*human* data with statistical adjustment to correct for the discrepancy between
simulated and observed responses. The paper states the assumptions each requires and
maps them onto exploratory versus confirmatory research.

**Results that matter:** The central claim is a boundary, not a number: heuristic
approaches are "useful for many exploratory tasks" but "lack the formal statistical
guarantees typically required for confirmatory research", whereas statistical
calibration "preserves validity and provides more precise estimates of causal effects
at lower cost" — but only under explicit assumptions, and only to the extent the LLM
approximates the target population at all. The authors also argue researchers lose
opportunities by focusing narrowly on substituting LLMs for participants.

**Limitations / criticisms:** A preprint, and a framework paper rather than an
empirical one — it offers no benchmark showing how large the calibration correction
needs to be in practice. Statistical calibration requires auxiliary human data, which
is exactly the resource a project choosing LLM generation usually lacks; the paper is
candid that this is the price of the guarantee.

**Relevance to this FYP (4/5):** This is the paper that lets the report state its
epistemic claim *honestly*, which matters because the supervisor's question is
precisely "do LLMs understand human behaviour well enough". By Hullman et al.'s
distinction this project is squarely **heuristic and exploratory**: prompt design
(`pipeline/prompts/`) and the observer framing of DD2 are repair strategies, and there
is no auxiliary human dataset for calibration. The correct claim for the report is
therefore *"a plausible, internally consistent behaviour prior for a simulation"*, not
*"a validated substitute for human behavioural data"* — and this paper is the citation
for why that distinction is principled rather than a hedge. It also identifies the
concrete upgrade path: the walking-speed literature already used in `VALIDATION.md` §3
(Weidmann, Bohannon) *is* auxiliary human data, so speed attributes could in principle
be calibrated rather than merely sanity-checked. Rated 4 not 5 because it is a preprint
offering framing rather than a method this project can run today.

**BibTeX key:** `hullman2026validating`

---

### [Zhong-DDC] — Data-driven Crowd Modeling Techniques: A Survey

**Authors / Year / Venue:** Jinghui Zhong, Dongrui Li, Zhixing Huang, Chengyu Lu,
Wentong Cai / January 2022 / *ACM Transactions on Modeling and Computer Simulation*,
Vol. 32, No. 1, Article 4, 33 pages.

**Link:** https://doi.org/10.1145/3481299

**Verified:** yes — the ACM DL landing page returns HTTP 403 to automated fetches, so
verification was done against the **PDF's own front matter and ACM reference block**
(cached `refs/zhong2022_data_driven_crowd_survey.pdf`, extracted to
`refs/zhong2022_survey.txt`), which state the title, all five authors, their
affiliations, the journal, volume/issue/article/page count and the DOI. This is
stronger evidence than the landing page would have been. Semantic Scholar reported 32
citations.

**Problem:** Surveys how crowd models can be built *from data* rather than from
hand-tuned rules, and — critically for this project — how such models are validated.

**Method:** A taxonomy of data-driven crowd modelling: calibration methods (§3.1),
example-based methods (§3.2), rule-based methods (§3.3) and others (§3.4); a survey of
datasets (§2); a survey of validation techniques split into metric-based (§4.1),
probability-model-based (§4.2) and other (§4.3); and six open problems (§5).

**Results that matter:** As a survey the load-bearing content is positional, and three
positions matter here.
- On validation methodology (§5.5): "because pedestrians' behaviors are so complex and
  affected by many factors including, but not limited to, physical ones, psychological
  ones and social ones, **a single validation approach can hardly cover all of these
  factors**"; the authors note a model can pass a macro-level metric (collectiveness)
  while failing a micro-level one (trajectory error), and conclude "it is better to
  adopt multiple validations, each focusing on a different aspect."
- On validation practice (§4): traditional crowd models are validated "based on the
  look and feel of the simulations", which "requires a great amount of manual effort
  and is not suitable for... complex scenes" — motivating metric-based validation
  against real crowd data (§4.1), e.g. the fundamental diagram (density-vs-speed).
- On interpretability (§5.3): black-box crowd models' "incomprehensibility restricts
  their further performance"; interpretable models "can be converted into
  understandable rules and theorems and further used by humans."

**Limitations / criticisms:** It is a 2022 survey, so it predates the
LLM-as-behaviour-source literature entirely and says nothing about it — it cannot be
cited as support for the LLM approach, only for the surrounding modelling and
validation practice. Its notion of "data-driven" means learning from observed crowd
data (video, trajectories), which is a stronger empirical grounding than this project's
LLM-elicited data; that contrast is a limitation of this FYP, not of the survey, and
should be stated as such in the report.

**Relevance to this FYP (4/5):** The only entry addressing the crowd-simulation half of
the research question, and it does three jobs no LLM paper can.
1. It establishes that learning pedestrian behaviour from data instead of hand-tuned
   rules is **mainstream, peer-reviewed practice** — so the report's burden is to
   defend the *source* of the behaviour data (an LLM), not the paradigm itself.
2. §5.5 is the direct citation for `VALIDATION.md`'s multi-method structure: the
   seven-check design is not over-engineering, it is what the crowd-modelling
   literature explicitly recommends — and §5.5 also warns against reporting a single
   headline pass rate.
3. §5.3 on interpretability is a genuine argument *for* this project's architecture — a
   frozen `(scenario × persona) → behaviour` table with an explicit `rationale` field is
   interpretable in exactly the sense the survey says learned crowd models usually are
   not, which is a defensible advantage over a neural trajectory model.

Worth noting for the supervisor: co-author **Wentong Cai is at NTU**, the same school as
the senior's CrowdGym FYP, so this is likely to be familiar ground.

**BibTeX key:** `zhong2022datadriven`

---

### [Park-GA] — Generative Agents: Interactive Simulacra of Human Behavior

**Authors / Year / Venue:** Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai,
Meredith Ringel Morris, Percy Liang, Michael S. Bernstein / 2023 / Proceedings of the
36th Annual ACM Symposium on User Interface Software and Technology (**UIST '23**).
Preprint arXiv:2304.03442 (v1 Apr 2023, v2 Aug 2023).

**Link:** https://doi.org/10.1145/3586183.3606763 | arXiv:2304.03442

**Verified:** yes — opened the arXiv abstract page (cached
`refs/park2023_generative_agents_abs.html`) and the ar5iv full text; the ACM DL page
itself returns HTTP 403 to automated fetches, so the UIST venue and DOI were confirmed
from the ACM citation record surfaced in search rather than from the landing page.

**Problem:** Can an LLM drive agents that behave believably over extended time in an
interactive simulated environment, rather than producing one plausible response?

**Method:** An architecture wrapping an LLM with three components — a natural-language
**memory stream** recording everything the agent experienced, **reflection** that
synthesises memories into higher-level inferences, and **planning** that turns those
into future action. Twenty-five agents populate a Sims-like sandbox town. Believability
was evaluated by human participants ranking conditions, with ranks converted to
**TrueSkill** ratings (§6.4) — an Elo generalisation for multi-way comparison. Five
conditions: the full architecture, three progressive ablations, and a human
crowdworker-authored baseline.

**Results that matter:** TrueSkill ratings (§6.4, Fig. 8), from 100 sets of rank data:

| Condition | TrueSkill μ | σ |
|---|---|---|
| Full architecture | **29.89** | 0.72 |
| No reflection | 26.88 | 0.69 |
| No reflection, no planning | 25.64 | — |
| **Human crowdworker baseline** | **22.95** | 0.69 |
| No memory, planning or reflection | 21.21 | 0.70 |

Every component contributed, and the full architecture beat the most-ablated condition
(which the authors take to represent prior work) by a Cohen's d of **8.16**. The
emergent-behaviour demonstration — a single seeded intent to hold a Valentine's Day
party propagating into invitations, dates and coordinated attendance over two simulated
days — is the paper's headline qualitative result.

**Limitations / criticisms:** The crowdworker baseline placing **fourth of five** should
temper how the headline is read: the comparison is against crowdworkers writing
behaviour for characters they did not design and had limited context on, so "beats
humans" overstates it — it beats a weak human baseline on a believability ranking, not
on behavioural accuracy against real people. The authors further note (§8.2) the study
"required substantial time and resources... costing thousands of dollars" for 25 agents
over two simulated days, that evaluation covered only a short timescale, that robustness
to prompt and memory hacking is "largely unknown", and that agents inherit the base
model's biases. Believability is also not validity: nothing here shows the behaviour
matches what real people do.

**Relevance to this FYP (4/5):** Two transfers, one of them a *negative* result that
justifies this project's central architectural decision.
1. It is the canonical demonstration that LLM-driven agents produce coherent,
   individually-differentiated behaviour inside a running simulation — the existence
   proof the literature review needs before any of this is worth attempting.
2. **The cost result is the argument for this project's design.** Thousands of dollars
   for 25 agents over two simulated days (§8.2) is the empirical basis for the claim in
   `README.md` that per-agent, per-step LLM calls are impossible at 10,000 agents, and
   therefore for **DD1** — querying offline once per `(scenario × persona)` and freezing
   the answers into an O(1) lookup. Park et al. is best cited as the approach this FYP
   deliberately *diverges* from, with a measured reason.

The trade-off must be stated honestly: freezing the table discards exactly the memory
and reflection that Park et al.'s ablation shows carry most of the believability
(29.89 → 21.21 without them). This project buys tractability at 10,000 agents by giving
up per-agent adaptation, and the report should say so rather than presenting the frozen
table as a free win.

Rated 4 rather than 5 because believability ranking is a weaker validity notion than the
distributional replication in [Aher-TE], and because the runtime architecture is not the
one this project uses.

**BibTeX key:** `park2023generative`
