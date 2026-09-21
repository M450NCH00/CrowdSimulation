# [Khaki-Fairness] — Evaluating Fairness in LLM Negotiator Agents via Economic Games Using Multi-Agent Systems

Prepared for issue [#18](https://github.com/M450NCH00/CrowdSimulation/issues/18). Group L
(LLM-side). Template: L.

## Citation

**Authors / Year / Venue / DOI:** Ahmad Mouri Zadeh Khaki (Mechanical Engineering Research
Institute, KAIST, Daejeon) and Ahyoung Choi (Department of AI and Software, Gachon University,
Seongnam-si) / 2026 / *Mathematics*, volume 14, issue 3, article 458 /
doi:10.3390/math14030458.

**Confirmed from:** the article's own title page, which prints both authors with their
affiliations, and the per-page footer that reads "Mathematics 2026, 14, 458" on every page of
the PDF. Cross-checked against the Crossref record cached at `refs/cr_math14030458.json`,
which returns the same two authors, journal, volume 14, issue 3, article number 458, a
publication date of 28 January 2026, and a CC BY 4.0 licence.

**Peer-review status: published** in a peer-reviewed journal. The title page records the
editorial dates.

**Version read:** the published PDF. **Access note:** mdpi.com returned HTTP 403 to every
route attempted, so the file was obtained from MDPI's own asset host
(`mdpi-res.com/d_attachment/mathematics/mathematics-14-00458/article_deploy/mathematics-14-00458.pdf`)
and cached at `refs/b1_fairness_negotiator.pdf`, with a text extract at `.txt`. Its identity
was confirmed against the Crossref metadata and the page footers.

## Accessibility

**Full text read.**

---

## 1. Research question

Three questions are posed in §1:

1. Do LLM-based negotiation agents exhibit demographic bias, for example gender or racial
   bias, in interactive negotiation settings?
2. How do social and gender biases emerge in seller–buyer negotiations?
3. Can persona-based conditioning serve as a practical intervention to mitigate such biases
   and improve outcomes for underrepresented groups?

The Abstract frames the motivation differently and more strongly: it observes that in human
interactions marginalised groups including racial minorities and women often face unequal
outcomes, and asks whether LLM-based agents, being trained on human data, reflect those
existing biases in their negotiation strategies. **This framing and the actual measurement
differ in an important way — see §6.**

## 2. Setup

**Model.** A single model: **ChatGPT-4 Turbo**, used for both agents (§3.1). The authors give
three reasons for the choice: its reliability in multi-turn rule-based negotiation tasks,
stable API access during the data collection period, which they date to **October 2024**, and
a deliberate decision to validate the methodological framework on one model before extending
it (§3.1). They also note that ChatGPT-4 is recognised for adhering to structured game
instructions where free-tier models struggle.

**Demographic attributes varied — gender is crossed with race.** The design varies
**gender (male, female)** and **race (White, Black, Asian, Latino)**, and the paper describes
its analysis as including an intersectional fairness analysis of male and female agents from
those four racial groups (§1; Abstract). So there are six single-attribute subpopulations —
two genders and four races — plus intersectional combinations, plus a demographic-blind
baseline.

⚠ **An unresolved inconsistency in the number of conditions.** §3.2 states that for each of
the three awareness scenarios the game was simulated 20 times across **nine** gender/race
permutations including a baseline condition, giving **540 individual game runs**
(9 × 3 × 20). But §4.1 describes Figure 3 as showing results for **six** subpopulations — two
genders and four races — along with a baseline case, which is seven. I cannot reconcile these
from the text; it is possible the nine counts intersectional cells and the six counts
single-attribute ones. Both are reported as printed.
`[needs verification against the published figures]`

**How personas were specified.** This is the design feature that most distinguishes this paper
from the other Group L papers here. The demographic is attached **to the counterpart, not to
the agent itself**. The prompt used to inform an agent of the other player's demographic is a
single explicit sentence stating that the other player is a White, Black, Latino or Asian male
or female, selected according to the scenario being investigated (§3.1).

**Neither agent is given an identity of its own.** An agent is told who it is facing. There is
no self-persona, no name, and no backstory.

**Other attributes studied alongside gender:** race, as above. No age is studied.

**Number of runs:** 20 independent games per experimental scenario (§3.1), 540 in total per
§3.2. Only negotiations that ended in agreement were analysed, and outliers were removed
(§3.2). The authors report that under their settings all negotiations concluded with a
successful deal, with no mutual rejections (§3.1).

## 3. Interaction design

**Dyadic and competitive.** Two autonomous LLM agents: a **seller (Player Red)** and a
**buyer (Player Blue)**, each a role-conditioned instance of ChatGPT-4 Turbo, in a framework
adapted from the NegotiationArena platform (§3.1).

**Task type: buyer–seller price negotiation.**

**Is anything contested?** **Yes, and it is zero-sum by construction.** The seller is given
private knowledge of the production cost; the buyer is given private knowledge of its maximum
willingness to pay. Each has a role-specific goal — the seller to maximise profit, the buyer
to minimise expenditure — plus constraints and chain-of-thought prompting instructions to
reason step by step before each decision (§3.1). The paper describes the game as distributive,
where one player's profit is the other's loss (§4.1).

The authors justify the choice of game on the grounds that it links strategic choices —
initial offers, concessions and acceptance decisions — to a measurable outcome, the profit
margin, allowing quantitative assessment of differential treatment across demographic groups
(§3.1).

**Parameters.** Production cost is set at $40 and willingness to pay at $60, a deliberate
positive gap between the agents' target values intended to increase the likelihood of
agreement (§3.1).

**Turn structure and termination.** Turn-based, **up to 10 turns**, beginning with the seller
making an initial price offer. Either agent may propose counteroffers or accept or reject at
any turn (§3.1). Termination is therefore agreement, rejection, or the 10-turn cap.

In the scenario where only the buyer is informed, the seller was additionally prompted to open
with a preset initial offer of **$50**, so that the buyer's role could be isolated from
variation in the seller's opening (§4.2).

**Three awareness scenarios** (§4.1, §4.2, §4.3): seller informed of the buyer's demographic;
buyer informed of the seller's demographic; both informed.

## 4. How the effect was measured

**Primary metric: profit margin** for the informed player, against the demographic-blind
**baseline** in which neither party knows the other's gender or race (§4.1).

**Supporting metrics** reported in Tables 1 and 2: final agreed price (FAP), the seller's
initial offer, the buyer's counteroffer, and the average number of negotiation turns (§4.1).

**Statistics.** A 95% confidence interval was computed using the Student's t-distribution with
n − 1 degrees of freedom, per Equation (1) in §3.2, alongside descriptive measures.

**Qualitative analysis.** The agents' chain-of-thought traces were analysed interpretively to
identify the origins of demographic bias in offers, concessions and acceptance behaviour. The
authors state explicitly that this CoT analysis is used as an interpretive mechanism rather
than as a quantitative evaluation metric (§3.1).

## 5. Findings

⚠ **This section follows the issue's precision rule: gender results are reported separately
from race results wherever the paper separates them, and where it reports only combined
gender-by-race results, that is said.**

### 5a. Scenario 1 — seller informed of the buyer's demographic (§4.1)

**Gender, reported separately:** sellers achieved **higher profits against female buyers than
male buyers, $5.47 versus $4.97** (§4.1, Figure 3a).

**Race, reported separately** (recorded for completeness, not extracted as a finding): the
highest seller profit came against Latino buyers, at a sale price of $45.75 giving a margin of
$5.75; the lowest came against White buyers, $1.03 less, giving $4.72; Black and Asian buyers
gave $5.12 and $5.30 respectively.

**Baseline comparison:** the paper notes that in none of the negotiations with social groups
did the seller achieve a higher profit than in the baseline case of $5.85.

**Intersectional (gender × race combined):** the paper states that results for intersectional
groups followed a similar trend, shown in Figure 3b, without separating gender from race in
the text. The distributive plot in Figure 3c is described as showing that baseline, Latino and
female buyers tend to benefit sellers more, while White, male and Black buyers give sellers
less advantage, with Asian buyers approximately in the middle. **This sentence mixes gender
and race categories in a single ranking and the paper does not disentangle them; I have not
attempted to.**

**Mechanism — the opening offer, reported separately by gender.** Sellers more frequently
proposed lower opening offers against male buyers than female buyers, despite following the
same reasoning pathway: an initial offer of $50 was used in **58.75% of games with male buyers
and 62.5% of games with female buyers** (§4.1). In 6.25% of games with male buyers the seller
opened with a different value, with the corresponding female figure appearing in the same
passage. The authors report a similar trend across racial groups.

**Final agreed price by gender** (§4.1, Table 1): higher with female buyers, **$48**, than
with male buyers, **$47.62**. Table 1's female row is printed as 47.62 ± 0.68 for the seller's
initial offer, 42.84 ± 0.71 for the buyer's counteroffer, 4.30 ± 0.14, and 44.97 ± 0.70.
⚠ These Table 1 row values do not align straightforwardly with the $48 / $47.62 figures quoted
in the body text, and I could not resolve the column mapping from the text extraction.
`[needs verification against the published table]`

**Correlation:** a strong relationship between the final agreed price and the seller's initial
offer, Spearman's ρ = 0.84, p < 0.001, from which the authors conclude that the seller's
opening offer is a critical determinant of the final price (§4.1).

### 5b. Scenario 2 — buyer informed of the seller's demographic (§4.2)

**Gender, reported separately — and the effect is negligible here.** The paper states that the
buyer can benefit more from a female seller than a male seller, but that the difference in
profit margin is negligible: **$12.56 versus $12.57**.

⚠ **An internal inconsistency, reported as printed.** As written, $12.56 for the female seller
is *lower* than $12.57 for the male seller, which contradicts the sentence's own claim that
buyers benefit more from a female seller. The authors themselves describe the difference as
negligible. **The defensible reading is that no meaningful gender effect was found in this
direction.** `[needs verification against the published figures]`

**Race, reported separately:** the smallest buyer profit margin came against a White seller at
$12.42; the highest against an Asian seller at $12.72; Latino and Black sellers fell between,
at $12.55 and $12.57.

**Baseline:** unlike scenario 1, the informed player here beat the baseline of $12.40 against
all subpopulations, which the authors read as showing that awareness benefits buyers more than
sellers in this game.

**Intersectional (gender × race combined):** the paper reports that male sellers across all
intersectional groups showed similar trends, but that Black female sellers at $12.65 offered
greater benefit to buyers than Latina female sellers at $12.55; that White female sellers were
among the subpopulations with higher payoffs than their male counterparts; that Latino male
and female sellers offered equal payoffs; and that Asian male sellers at $12.80 were the only
group whose payoffs exceeded their female counterparts at $12.65. **These are combined
gender-by-race cells and the paper does not decompose them.**

**Qualitative mechanism (CoT).** The paper reports a framing difference in the buyers'
reasoning: acceptance of deals with female sellers was justified in relational terms, referring
to maintaining a good trading relationship, whereas acceptance with male sellers was justified
in instrumental terms, referring to not losing the opportunity over a small difference (§4.2).

### 5c. Scenario 3 — both players informed (§4.3)

The results the paper reports here are **entirely intersectional**, and it does not separate
gender from race. The highest buyer payoff arose when an Asian male buyer negotiated with a
Black female seller, $16.6; the lowest when a Black female buyer interacted with a White female
seller, $12.7. Among same-group pairings, Asian male and Latina female buyers at $13.70 showed
the lowest and White male buyers at $15.9 the highest.

**No gender-only result is reported for scenario 3, so none is extracted.**

### 5d. Persona-based conditioning (§4.4, §5.1)

Conditioning buyers with a constraint-based persona improved their negotiation outcomes across
all subpopulations, but persistent disparities remained (§5.1, Figure 6).

### 5e. The authors' own summary

In §5.2 the authors summarise the pattern as: seller agents consistently offering higher
initial prices to female and Latino buyers, while buyer agents negotiate more aggressively
with female sellers. In §5.1 they answer their three research questions directly: agents aware
of a counterpart's gender or race produce systematically different outcomes and unequal profit
margins (RQ1); the biases emerge through strategic behaviours — differences in initial offers,
counteroffers and bargaining persistence — rather than through explicit language (RQ2); and
persona-based conditioning partially mitigates but does not eliminate the disparities (RQ3).

## 6. What "bias" is measured against

**Standard (a): deviation from equal treatment across groups — a fairness standard. The paper
is *framed* as though it were standard (b), but it does not measure against human data.**

The evidence for that reading:

- The Abstract asks whether LLM agents reflect existing biases in human interaction, which is
  an accuracy question, and asserts that in human interactions women and racial minorities
  often face unequal outcomes, citing prior literature (§1, reference [10]).
- **But no human negotiation outcomes are measured or compared anywhere in the paper.** There
  is no human baseline, no human participant, and no comparison of the $5.47/$4.97 figures
  against any human bargaining result.
- What is actually measured is the difference between demographic-aware conditions and the
  **demographic-blind baseline**, and differences across demographic groups within those
  conditions (§4.1–4.3).
- The normative target is equality: RQ3 asks about mitigating bias and improving outcomes for
  underrepresented groups, and the conclusions call for stricter control over demographic
  exposure during interactions (§6).

So the human claim is carried entirely by citation in the introduction, and the measurement is
a parity comparison. For the FYP's purposes this paper supplies the LLM side of a comparison
and not the human side.

## 7. Mitigation

**Method: persona-based conditioning of the buyer agent** with a constraint-based persona
(§4.4, §5.1).

**Reported effect:** it improves buyers' outcomes across all subpopulations, but persistent
disparities remain, so the intervention reduces without eliminating the disparity (§5.1). The
Abstract describes this as suggesting a way to empower underrepresented groups.

Further directions the authors propose rather than test (§5.4): incorporating another agent as
a coach; an explicitly programmed debiasing algorithm that detects social dynamics and advises
players; using LLMs as fairness-proponent agents in a multi-agent debate; and evaluating the
negotiation behaviour of fairness-enforced models.

**`[inference]` — would this mitigation move the LLM toward or away from realistic human group
differences?**

**Unknown, and the paper is not structured to tell us — but the target is parity, so if real
human negotiators do show gender differences in outcome, the mitigation moves away from
realism.** The intervention is evaluated by whether disparities shrink, not by whether outcomes
come to resemble human negotiation data. There is a second, subtler point: the intervention is
applied **asymmetrically**, to the buyer only, as a way of improving the outcomes of the
disadvantaged party. That is a fairness intervention in design as well as in evaluation. A
realism-oriented project would need to ask a different question — whether the conditioned
agent's behaviour looks more or less like a real negotiator's — which this paper does not ask.

## 8. Limitations stated by the authors

⚠ **The paper has no section headed Limitations.** Constraints are stated as future directions
in §5.4 and as observations in §5.3.

From §5.4, Future Directions:
- The findings are specific to ChatGPT-4 Turbo, and the authors recommend extending the
  framework to other models such as LLaMA, Claude, Gemini and Qwen, noting that different
  training data, architectures and alignment strategies are likely to produce different
  degrees and forms of fairness.
- Only one game type was used; they suggest evaluating fairness through other games, naming
  salary negotiations and mock job interviews.
- They note that mitigating discriminatory behaviour is a substantial research direction in its
  own right, and that removing bias effectively would require investigating training datasets
  before training.
- They flag that future work will extend the framework to further pricing scenarios, including
  narrow, zero-surplus and asymmetric valuation regimes.

From §5.3, on irrational behaviours observed in the agents, the authors describe three failure
modes: the LLM failing to follow prompt instructions; agents making no further effort to
improve their profit margins; and an agent accepting a bad deal simply to close a deal.

**Not stated by the authors, but relevant:** the sample is 20 games per scenario (§3.2), which
is small relative to the ~$0.50 differences reported, and while §3.2 specifies that 95%
confidence intervals were computed, **I did not find a confidence interval or significance
test reported alongside the headline gender contrast of $5.47 versus $4.97 in §4.1.** This is
my own observation, recorded separately in
[`reading-notes-demographics.md`](reading-notes-demographics.md).

## 9. Relevance to this FYP

`[inference]` — my judgement.

1. **It is the only paper of the five in which two agents contest a scarce resource through
   multi-turn dialogue**, which makes it structurally the nearest analogue to GameChat-style
   priority negotiation. What is contested is price rather than space, but the shape — two
   parties, opposed interests, turn-taking, a concession dynamic, a termination cap — matches.
2. **The mechanism is the finding to carry across, not the number.** The disparity was produced
   by a **more aggressive opening move** against a female counterpart, with the agents'
   *stated* reasoning unchanged. The navigation analogue would be an agent opening the exchange
   with a stronger claim to priority when it knows it faces a female agent. That would be
   invisible in a summary of who eventually yielded, and visible only in the first turn of the
   transcript. **If the FYP logs anything, it should log the opening move as well as the
   outcome.**
3. **The counterpart-awareness design is worth copying as a separate condition.** Assigning an
   agent its own gender and telling an agent its counterpart's gender are different
   manipulations. `run01` does the former; this paper does the latter. They should not be
   assumed to produce the same effect.
4. **The role-asymmetry result is a caution against over-reading any single number.** The
   gender effect was substantial when the seller was informed and negligible when the buyer
   was informed. A demographic effect in one role does not imply one in the reverse role.
5. **Single model, single game, 20 runs per cell.** Whatever is taken from this paper should
   carry those three qualifiers.

## BibTeX

`khaki2026fairness` — see [`refs-demographics.bib`](refs-demographics.bib).
