# G6 — Generality and transfer across games (lower priority)

Prepared for issue [#20](https://github.com/M450NCH00/CrowdSimulation/issues/20).
Companion files: [`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md),
[`g2-norm-emergence.md`](g2-norm-emergence.md),
[`g3-cheap-talk.md`](g3-cheap-talk.md),
[`g4-game-theoretic-crowd-models.md`](g4-game-theoretic-crowd-models.md),
[`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md),
[`candidate-rule-catalogue.md`](candidate-rule-catalogue.md),
[`search-log.md`](search-log.md), [`refs-game-theory.bib`](refs-game-theory.bib).

This sub-area supports the supervisor's requirement that the extracted rules "should not be tied to
spatial conflict, and should ideally apply to any generic simulator".

---

## ⚠ Finding: this sub-area IS thin, and the issue's exact question was not answered

The issue anticipated this and gave explicit permission:

> "This supports the supervisor's requirement that the rules apply to a generic simulator. **If this
> sub-area turns out to be thin, report that honestly rather than stretching unrelated work into
> it.**"

**Reporting it honestly.** The issue's question is: *does a convention learned in one game transfer to
**structurally different** games?* After the searches logged in [`search-log.md`](search-log.md) §G6,
**I did not find a paper that answers that question for conflict games or for conventions in the
[`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md) sense.** What I found instead
falls into three groups:

1. **One qualifying entry that is genuinely about behaviour crossing between games**
   ([Rossetti-ConcurrentGames], below) — but the games are **cooperation** games (donation/prisoner's
   dilemma), **not** anti-coordination conflict games, and the effect studied is **simultaneous
   spillover** between games played in parallel, not **transfer** of a learned convention to a new
   game. It qualifies under the issue's criterion (b) — evidence about when such rules do and do not
   hold — and not under criterion (a).
2. **One methodologically important entry on generalisation** ([Cross-ValidatingGABM], below) which
   gives a *method* for testing whether LLM agents generalise beyond what they might have memorised.
   It tests generalisation to **novel conditions within a paradigm**, not to structurally different
   games. Its real value to this FYP is as the answer to the leakage critique in
   [`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md), so it is cross-filed.
3. **A set of confirmed-but-unopened leads** in the experimental-economics "behavioural spillovers"
   literature, listed in §3, which is where the issue's actual question appears to live. These are
   mostly paywalled and were **not** obtained. This is the honest gap.

**One qualifying entry, not two.** The issue's acceptance criteria require ≥2 qualifying entries for
G1–G5 and pointedly **do not list G6** among them. That is consistent with what I found. I have not
padded the file to reach an arbitrary count.

---

## §1. Qualifying entry

### [Rossetti-ConcurrentGames]: Dynamics of cooperation in concurrent games

- **Authors / Year / Venue:** Charlotte S. L. Rossetti (Max Planck Institute for Evolutionary
  Biology), Oliver P. Hauser (University of Exeter), Christian Hilbe / 2025 / *Nature Communications*
  **16**, article 1524. Received 31 May 2024; accepted 4 January 2025.
- **Link:** doi:[10.1038/s41467-025-56083-7](https://doi.org/10.1038/s41467-025-56083-7) · open
  access
- **Peer-review status:** **published**, peer-reviewed journal (Springer Nature), open access.
  Fields confirmed from Crossref (`refs/gt_crossref_all.json`, key `rossetti2025`).
- **Verified:** **yes — full text** (`refs/gt_natcomms2025_concurrent.pdf`, publisher PDF; text at
  `refs/gt_natcomms2025_concurrent.txt`). Locators are to named sections and figures.
- **Sub-area:** G6
- **Tags:** none (2025)
- **Type:** formal theory + simulation + human experiment
- **The game or conflict modelled:** **two donation games played concurrently** — a "high" game *H*
  with a larger cooperation benefit and a "low" game *L* with a smaller one, played in parallel
  against either the same partner or different partners, for "infinitely many rounds" in the
  theoretical treatment (Results, §on formalism). ⚠ **These are cooperation dilemmas, not
  anti-coordination conflict games.** The contested thing is a contribution, not a right of way.
  Three treatments: **control** (one game), **same-partner** (both games, one partner),
  **different-partners** (both games, two partners) (figure 2a–c).
- **The rule or solution concept:** **strategies in the repeated game, evolving under an evolutionary
  learning process**, with the key definition being what it means for behaviour to cross games:
  "if the entries satisfy [independence], we say players treat both games as independent…
  **[otherwise] we say players link their behavior across games**" (Results, §on formalism). Strategies
  are written as vectors *p* over conditional cooperation probabilities in each game given outcomes in
  both (equation (2)). The reference heuristic is direct reciprocity: "simple heuristics based on
  direct reciprocity: cooperate when others do and cease cooperation when partners defect" (Abstract),
  with the control treatment producing behaviour "consistent with Generous Tit-for-Tat" (figure 2
  caption).
- **The results that bear on G6:**
  - **Linking happens.** "Our findings indicate that **individuals often link their behavior across
    games**, particularly under cognitive constraints like imperfect recall" (Abstract). In the
    experiment: "in the different-partners treatment, we find that a player's behavior in one [game
    depends on] actions that occurred in the other" (Results).
  - **And it is costly.** "**both the same-partner treatment and the different-partners treatment
    resulted in less cooperation than the control**" (Results). "Overall, the same-partner treatment
    results in more cooperation, whereas the different-partners treatment leads to reduced
    cooperation" (Results). Headline: "A behavioral experiment with 316 UK-based students suggests
    that **concurrent games negatively affect cooperation**" (Abstract).
  - **The linking is a bias, not an optimisation.** "all three treatments yield equivalent results if
    players are **artificially restricted to treat each game as independent**" (Results, referring to
    Fig. S1) — i.e. the difference between treatments exists *only because* players fail to separate
    the games. The paper models four candidate causes explicitly: **imperfect recall, spillovers,
    preferential updating, and narrow bracketing** (figure 3 panel headings), with parameters
    "Error probability / Probability of spillover / Weight for biased updating / Probability of
    occurrence" respectively.
  - **Robustness:** "Our qualitative results remain valid for a wide range of parameter [values]"
    (figure 2g–h caption), and the authors report checking games other than the donation game:
    "games are different from the donation game. For example, in Fig. S4…" (Results).
- **Information the rule requires:** the player's own recall of outcomes in **both** games. The
  paper's point is that this is where the trouble starts: linking is driven "particularly under
  cognitive constraints like imperfect recall" (Abstract).
- **One-shot or repeated:** **repeated** — infinitely repeated in theory, multi-round in the
  experiment. Not applicable to a single encounter between strangers.
- **Communication required:** **none** modelled; behaviour is the only channel.
- **Scalability:** `[not stated in paper]` for computational cost. The experiment is *n* = 316
  human participants (Abstract); the theory is pairwise with an evolutionary learning process
  "averaged over 100 simulations" (figure 2 caption). The paper does note a scaling consequence of
  the change in perspective: once games are not independent, "the cooperation dynamics need to be
  described at a different level: instead of the standard game-perspective, models now need to take a
  population-perspective. **This change in perspective drastically increases a model's
  computational** [cost]" (Introduction). [inference] That is a relevant warning: modelling
  cross-game effects is expensive.
- **Validated against human behaviour:** **yes** — "A behavioral experiment with **316 UK-based
  students**" (Abstract), with the design "based on a similar design as in previous empirical
  studies" (Results).
- **Assumptions that may not hold in a crowd:** two games, two or three parties, repeated play with
  identifiable partners, and cooperation-dilemma payoffs. **None of these describe a corridor
  conflict between strangers.**
- **Limitations stated by the authors:** the parameter-robustness checks are presented as
  supplementary (figure 2g–h, Fig. S1, Fig. S4); the theoretical model assumes an evolutionary
  learning process rather than within-lifetime reasoning.
- **Relevance to this FYP:** it is the **only** entry found that directly measures behaviour crossing
  between games in humans, and what it says is a **caution**:
  - [inference] Transfer across games in humans is **real but harmful** — it reduces cooperation, and
    it happens because people fail to keep the games separate (Results; Fig. S1). So "our rule
    generalises across games" should not be assumed to be good news. If a crowd agent applies a
    corridor convention in a queue where it does not fit, the FYP's own results will degrade in the
    same way.
  - [inference] The practical design implication is concrete: an extracted rule should be
    **explicitly scoped to a conflict type**, and the simulator should select among rules by conflict
    type rather than applying one rule everywhere. That is a testable design proposal, and it is the
    opposite of what "one generic rule for any simulator" would suggest.
  - It also supplies the vocabulary — **spillover**, **narrow bracketing**, **linking behaviour across
    games** (figure 3; Results §formalism) — for describing the failure mode.
- **BibTeX:** `rossetti2025dynamics`.

---

## §2. Cross-filed entry — the method for testing generalisation

### [Cross-ValidatingGABM]: Validating Generative Agent-Based Models of Social Norm Enforcement: From Replication to Novel Predictions

- **Authors / Year / Venue:** Logan Cross, Nick Haber, Daniel L. K. Yamins (Departments of Computer
  Science, Psychology, and Graduate School of Education, Stanford University) / 2025 /
  `arXiv:2507.22049v1` [cs.MA], submitted 29 July 2025.
- **Link:** https://arxiv.org/abs/2507.22049
- **Peer-review status:** ⚠ **preprint — NOT peer-reviewed.** No published version located.
- **Verified:** **yes — full text** (`refs/gt_arxiv_2507_22049.txt`).
- **Sub-area:** **G6 by the issue's letter, G5 by its actual value.** Cross-filed; see
  [`g5-llm-agents-game-theory.md`](g5-llm-agents-game-theory.md).
- **Type:** LLM experiment
- **⚠ What it does and does not test.** It does **not** test transfer of a convention to a
  structurally different game. It tests whether a validated LLM-agent architecture **generalises to
  novel experimental conditions within the same paradigm**. Recording that distinction plainly,
  because conflating the two would be exactly the stretching the issue warned against.
- **The games modelled:** two social-dilemma paradigms taken from the psychological literature —
  third-party punishment (TPP), and a **public goods game** with gossip and ostracism, the latter
  drawn from "Feinberg et al. (2014)'s work on gossip" (Introduction).
- **The method — this is the transferable part** (Abstract; Introduction):
  1. **"Model Validation: First, we conduct an iterative model comparison to identify the minimal
     agent architecture (set of cognitive components) sufficient to reproduce known behavioral
     effects in complex social settings."** Each candidate "model" is "a different LLM agent
     architecture — specifically, different combinations of prompts which we call cognitive
     components" (Introduction).
  2. **"Novel Prediction Generation: Second, we"** test predictions the source studies did not make,
     using the validated architecture (Introduction).
  The rationale is stated crisply: "By presenting agents with the same experimental stimuli used in
  human studies, we can **directly test whether their stimulus-to-behavior mappings match those
  observed in human participants**" (Introduction).
- **Results:** the architecture replicates the gossip effect but not everything — "**an additional
  strategic component is necessary** to replicate the additional boost in cooperation rates in the
  condition that allows both ostracism and gossip" (Abstract). Novel predictions: "**TPP rates
  significantly drop in settings where punishment is anonymous, yet a substantial amount of TPP
  persists, suggesting that both reputational and intrinsic moral motivations play a role**"
  (Abstract); and "open discussion periods before rounds of the public goods game further increase
  contributions, allowing groups to develop social norms for cooperation" (Abstract).
- **Limitations stated by the authors — and they are the honest ones:** "The most immediate
  opportunity to strengthen the validation of the model would be **the empirical testing of our novel
  predictions with human participants. Such verification would provide strong evidence of
  generalization for our model architecture**" (Discussion). I.e. **the generalisation claim is not
  yet closed** — the novel predictions have not been checked against humans. They also note the need
  for "exploration of more complex architectures for domains where these minimal components prove
  insufficient" and for "expanding the dimensionality of behavioral measures we compare between
  agents and humans" (Discussion).
- **Relevance to this FYP:** [inference] **this is the design of the control experiment that answers
  Barrie & Törnberg.** The leakage critique says an LLM reproducing a known result may be recalling
  it. Cross et al.'s answer is procedural: first show the agent reproduces the known result, then make
  it predict something **not in the literature**, then check that against humans. A prediction that
  is not in the training data cannot be recall. Applied to this FYP, that is a two-stage validation
  plan:
  - **Stage 1** — show the LLM-derived rule reproduces a known crowd-dynamics result (the RiMEA
    scenarios already distilled in `integration/crowdgym_mapping.md` are the obvious candidates).
  - **Stage 2** — have it predict a scenario outcome nobody has published, and compare.
  Stage 2 is what would let the report claim more than literature-consistency. Note the FYP has no
  human-subject budget, so Stage 2's comparison target would have to be argued for — and Cross et al.
  concede they have not closed that loop either. **Out of scope for this issue** (which is literature
  only), recorded as a lead.
- **BibTeX:** `cross2025validating`.

---

## §3. Confirmed leads NOT obtained — where the issue's actual question lives

These were located by search and their existence is not in doubt, but **none was opened**, so no
content claims are made about any of them. Listed so the next person does not repeat the search. The
first three are the "behavioural spillovers" experimental-economics literature, which appears to be
where the issue's question — *does a convention transfer to a structurally different game?* — is
actually studied.

| Lead | Venue | Why it looks on-point | Status |
|---|---|---|---|
| "Coordination and transfer" | *Experimental Economics*, 2017, doi:10.1007/s10683-017-9521-8 | Title is the issue's question | Springer paywall; **not opened** |
| "Behavioral spillovers in coordination games" | *European Economic Review*, 2012, ScienceDirect `S0014292111000900` | Spillover between median and minimum games | Elsevier paywall; **not opened** |
| "Extrapolation and structural similarity in games" | *Economics Letters*, 2014, ScienceDirect `S0165176514003966` | **"structural similarity" is exactly the issue's framing** | Elsevier paywall; **not opened** |
| "Feedback spillover and analogy-based expectations: A multi-game experiment" | *Games and Economic Behavior*, 2010, ScienceDirect `S0899825610001065` | Multi-game experiment | Elsevier paywall; **not opened** |
| "An experiment on learning in a multiple games environment" | *Journal of Economic Theory*, 2012, ScienceDirect `S0022053112000658` | Learning across concurrent games | Elsevier paywall; **not opened** |
| "Learning and transfer in signaling games" | *Economic Theory*, 2006, doi:10.1007/s00199-006-0192-5 | Transfer in signalling games | Springer paywall; **not opened** |
| Horiguchi, Yoshida & Ikegami, "Evolution of Social Norms in LLM Agents using Natural Language" | `arXiv:2409.00993` (preprint) | LLM agents forming norms **through dialogue**, building on Axelrod's metanorm games — closest published thing to the FYP's own dialogue setup | **Downloaded and opened at first-page level only**, not read in full; see note below |

**Note on `arXiv:2409.00993`.** This one deserves follow-up in its own right, and possibly does not
belong in G6 at all. From its first page (read): Horiguchi, Yoshida & Ikegami (University of Tokyo)
"explores the potential for LLM agents to spontaneously generate and adhere to normative strategies
through natural language discourse, building upon the foundational work of Axelrod's metanorm games",
and reports that "through dialogue, LLM agents can form complex social norms". It also gives the
definition of a metanorm: "a norm that punishes those who do not adhere to a certain norm (Axelrod,
1986)". [inference] That is **LLM agents deriving norms by dialogue** — the FYP's method — and it is a
**2024 preprint**, i.e. likely prior art that the FYP's novelty claim needs to address. I am **not**
filling in a template entry from a first page. **Recommended as the highest-priority acquisition
coming out of this issue**, alongside a novelty check of the kind issue #16 ran. Logged in
[`search-log.md`](search-log.md).

---

## What this means for the FYP

1. **The "generic simulator" requirement is not yet supported by evidence, and the report should say
   so.** No paper found demonstrates that a conflict-resolution convention learned in one game
   transfers to a structurally different one. The supervisor's requirement is a reasonable *design
   goal*; it is not a finding this review can cite. Stating that plainly is better than implying
   support exists.

2. **The one piece of human evidence points the other way.** [Rossetti-ConcurrentGames] finds that
   when humans do let behaviour cross between games, cooperation **falls**, and it falls because they
   fail to keep the games separate (Results; Fig. S1). [inference] So generality should be treated as
   a **risk to be managed by scoping rules to conflict types**, not as a free property to be claimed.

3. **The route to a defensible generality claim is structural, not empirical.** [inference] Two
   entries already read elsewhere in this review give it: [Shoham-SocialLaws]' `DO : S → A` is
   defined over an abstract state space with no spatial commitment at all
   ([`g2-norm-emergence.md`](g2-norm-emergence.md), Definition 3.1), and
   [Foley-ConflictConvention] states its own within-class generality explicitly — "the results apply
   equally to **any game of conflict** meeting the pay-offs defined in figure 1*a*"
   ([`g1-conflict-games-conventions.md`](g1-conflict-games-conventions.md), §1). So the FYP can
   legitimately claim generality **over the class of games with the conflict payoff ordering**,
   sourced to Foley §1, without claiming empirical transfer to structurally *different* games. That
   is a narrower claim and it is actually supported.

**Draft status:** draft pending supervisor review. This is the sub-area most in need of a decision
about whether to invest further — §3 lists exactly what to buy, and `arXiv:2409.00993` is the item
that matters most for novelty.
