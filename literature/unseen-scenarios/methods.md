# Q1, Q2 and Q4. Testing generalisation, transfer between games, and leakage

> For issue [#36](https://github.com/M450NCH00/CrowdSimulation/issues/36) (PT-2), part of the
> portable-rules track (#34). **The portable-rules idea is a proposal and has not been agreed.**
> Each "What the FYP's test protocol should take from it" line is `[inference]`.
>
> **Labels.** `[preprint]` where no published version was found or read. Where an earlier version
> was read in place of the published one, the entry says so, and **locators are to the version
> read**. Cached copies are named in each entry (`refs/us_*`).
>
> **Cross-references, not re-summaries.** Zhang et al. 2026 is summarised in
> `literature/paper-summaries/02-sense-think-act-reflect.md`; the leakage exchange (Barrie &
> Törnberg; Ashery et al.) in `literature/game-theory/g5-llm-agents-game-theory.md` §§2-4; and Cross
> et al. 2025 in `literature/game-theory/g6-transfer-across-games.md` §2. They are referred to, not
> summarised again.

## Answers in brief

- **Q1. Generalisation methods.** Three ways of defining "unseen" turn up, and each tests a
  different thing:
  1. **New partners on a familiar map** (Melting Pot: substrate + held-out background population
     = scenario). Melting Pot says plainly that it does *not* test new physical settings
     ([MeltingPot-1] §4.1; [MeltingPot-2] p. 4).
  2. **A new layout, same task** (Zhang et al.'s out-of-domain set; Tordeux et al.'s train-on-ring,
     test-on-bottleneck).
  3. **A new situation in a test catalogue** (RiMEA's warning that a parameter calibrated in one
     test may be wrong in another; see `scenario-standards.md`, [RiMEA-4.1.1]).

  Cross-scenario validation of pedestrian models exists but is thin: one small cross-geometry
  study ([Tordeux-ANN]), and a calibration framework that names cross-scenario generalisation as
  future work ([Wolinski-ParamEst] §5).
- **Q2. Transfer between structurally different games.** Five of the six g6 §3 leads were read in
  open versions; one is stubbed. Transfer **does happen** in humans, sometimes even between games
  that are "not structurally similar" ([CooperVanHuyck-Transfer] §4). But:
  - every positive case stays **within one class** (coordination games with a payoff-dominant
    equilibrium, or signalling games);
  - transfer is **asymmetric** ([Cason-Spillovers]);
  - it can **harm** ([CooperVanHuyck-Transfer] §4);
  - it depends on **how easy it is to tell games apart** ([Huck-FeedbackSpillover];
    [GrimmMengel-MultipleGames]) and on **meaningful context** ([CooperKagel-Signaling] §VII).
- **Q4. Leakage.** Three methods separate recall from generalisation, and each is cheap to copy:
  1. **counterfactual variants** of a task, with a check that the model understood the changed
     rules ([Wu-Counterfactual]);
  2. **new, author-written variants** of famous experiments ([Aher-TuringExperiments]);
  3. **small adversarial perturbations** of familiar vignettes ([Binz-CogPsychGPT3]).

  All three only *reduce* the doubt. Wu et al. say outright that they do not "guarantee that
  counterfactual world models are unobserved in a pretraining corpus" (§2). That fits g5 §4's
  conclusion that the FYP should test the extracted rules, not claim LLM understanding.

---

## Q1. How other fields test generalisation

### [MeltingPot-1]: Scalable Evaluation of Multi-Agent Reinforcement Learning with Melting Pot

- **Authors / Year / Venue / Link:** Leibo, J. Z., Dueñez-Guzman, E. A., Vezhnevets, A. S.,
  Agapiou, J. P., Sunehag, P., Koster, R., Matyas, J., Beattie, C., Mordatch, I., Graepel, T. /
  2021 / *Proceedings of the 38th International Conference on Machine Learning*, PMLR 139,
  pp. 6187-6199 (confirmed on the PMLR page, https://proceedings.mlr.press/v139/leibo21a.html) /
  arXiv:2107.06857.
- **Status:** published at ICML 2021. **Read:** full text of arXiv v1, which carries the ICML
  header (p. 1). Cached: `refs/us_meltingpot_2107_06857.*`.
- **What is tested for generalisation, and against what:** a multi-agent population learning
  algorithm (MAPLA) is judged on test scenarios, not on training. "Substrate + Background
  Population = Scenario"; "a scenario is a multi-agent environment that we use only for testing;
  we do not allow agents to train in it" (§1). Score: focal-population per-capita return, min-max
  normalised between a random agent and an "exploiter" trained on that scenario (§7).
- **How "unseen" is defined:** **new co-players, same physical world.** "zero-shot ... test
  scenarios that preserve a familiar substrate while substituting a new and unfamiliar background
  population" (§1). Modes (§4.2):
  - **resident**, where focal players are the majority;
  - **visitor**, used to test whether a focal individual "can observe the conventions and norms
    of the dominant background population and act accordingly (without retraining)";
  - **universalization**, everyone plays the same policy.

  Transfer across worlds is excluded by construction: "Policies are not transferable between
  substrates, since X and A can differ between them" (§4.1).
- **How overlap between training and test is prevented:** training has "unlimited access to a
  substrate" but "only access to the raw substrates and not the background populations" (§4.3).
  Background bots are trained separately; to make them generalise, some bots "typically not used in
  the final scenario" are trained alongside (§6, step 2).
- **Results on unseen cases, and where generalisation failed:** "Agents often exhibit a degree of
  overfitting", e.g. prosocial agents with self-play scores like the others "but ... closer to
  random" on test, "due to prosocial agents only learning cooperation strategies during self-play
  training, and so becoming exploitable by defectors at test time" (§7). Universalization scores
  exposed division-of-labour policies that "expect other agents to behave in a particular way"
  (§7).
- **What the FYP's test protocol should take from it:** `[inference]`
  - "new people" (L0) is a real test, not a formality. Melting Pot's failures are failures of
    social generalisation on a known map.
  - **Visitor mode** is the right template for queue cutting: one rule-following agent among
    others who follow a different, established norm.
  - Score against **floors and ceilings** (random; a scenario-specific best), not raw numbers.
  - Melting Pot gives **no** method for new layouts or new conflict types (L2-L4).
- **BibTeX:** `leibo2021meltingpot`.

### [MeltingPot-2]: Melting Pot 2.0

- **Authors / Year / Venue / Link:** Agapiou, J. P., Vezhnevets, A. S., Duéñez-Guzmán, E. A.,
  Matyas, J., Mao, Y., Sunehag, P., Köster, R., Madhushani, U., Kopparapu, K., Comanescu, R.,
  Strouse, D. J., Johanson, M. B., Singh, S., Haas, J., Mordatch, I., Mobbs, D., Leibo, J. Z. /
  2022, v6 dated 31 Oct 2023 / arXiv:2211.13746.
- **Status:** `[preprint]`. No journal reference on arXiv and none found by search on 2026-10-18.
  **Read:** main text (pp. 1-12); the per-substrate appendix only where cited. Cached:
  `refs/us_meltingpot2_2211_13746.*`.
- **What is tested for generalisation, and against what:** as in [MeltingPot-1]; now "a test
  scenario is a Markov game parameterized by a substrate factory ..., a role configuration r, the
  focal-population size ..., and a background population of held-out bots. Of these only [the
  substrate factory] is known at training time" (p. 5).
- **How "unseen" is defined:** new partners **and new role configurations**. Version 2.0 "adds
  full support for asymmetric games" through **roles** that set each player's observation and
  action space (p. 5). The paper is explicit about what is *not* varied: "the kind of
  generalization that Melting Pot probes is mainly along social dimensions, not physical
  dimensions. This is in contrast to most work on generalization in reinforcement learning (e.g.
  Cobbe et al. (2019)), which are primarily concerned with generalization along physical
  dimensions" (p. 4).
- **How overlap between training and test is prevented:** "As long as researchers do not cheat by
  training their agents on the test set ... 'anything goes'" (p. 4); the background bots are
  "held-out" (p. 5).
- **Results on unseen cases, and where generalisation failed:** "On several groups of substrates
  the MAPLAs we ran failed to generalize at all, getting scores very close to random:
  Collaborative Cooking, Running with Scissors, Paintball Capture the Flag" (p. 12). Normalisation
  can mislead: on Coins the random agent scored so badly that "all the MAPLAs ... perform well by
  comparison. However ... None of the MAPLAs we tested actually learned to cooperate" (p. 11).
- **What the FYP's test protocol should take from it:** `[inference]`
  - **Roles** that differ in what a person sees and can do (alighting vs boarding; inside vs
    outside the lift) are a recognised axis of held-out variation, and #34's vocabulary already has
    them.
  - Report results that a reader can check by **looking at behaviour**, not only normalised
    scores (the Coins warning).
- **BibTeX:** `agapiou2022meltingpot2`.

### [Zhang-DFD-OOD]: the out-of-domain test of Zhang et al. 2026 (cross-reference)

Already summarised in `literature/paper-summaries/02-sense-think-act-reflect.md`. Only the design
of the out-of-domain test is added here, from the cached paper (`refs/zhang2026_dfd.txt`).

- **What is tested, against what:** decision functions distilled from LLM-driven evacuation agents,
  against the LLM simulation's own trajectories. The summary notes that all three datasets come from
  the same LLM simulation, so there is no human reference (summary §6).
- **How "unseen" is defined:** "The out-of-domain test dataset is intended to evaluate whether the
  generated decision functions can generalize beyond the specific scenario layout of the training
  dataset", with "five different seeds for the in-domain training dataset, two seeds for the test
  dataset, and three seeds for the out-of-domain test dataset" (§5.1, p. 13). **The text I searched
  does not say how the out-of-domain layout differs** `[unverified]`.
- **How overlap is prevented:** separate seeds and a different layout (§5.1, p. 13). No more is
  stated.
- **Results:** the DFD variants "consistently outperform the baseline methods ... both on the
  in-domain training and test dataset and on the out-of-domain generalization dataset" (§5.3,
  p. 15, on Table 3); the same holds for Table 4 (§5.4, p. 17; the table is on p. 19).
- **What the FYP's test protocol should take from it:** `[inference]` this is the nearest in-field
  precedent for an **L2 test (new layout, same conflict type)**, and it is from NTU. But it shows
  two gaps the FYP should not copy: the layout change is not described, and **the reference is the
  LLM, not people**. The protocol should name the layout change and use human evidence as the
  reference.

### [Tordeux-ANN]: Prediction of Pedestrian Speed with Artificial Neural Networks

- **Authors / Year / Venue / Link:** Tordeux, A., Chraibi, M., Seyfried, A., Schadschneider, A. /
  2019 / *Traffic and Granular Flow '17*, Springer, pp. 327-335, doi:10.1007/978-3-030-11440-4_36
  (Crossref) / arXiv:1801.09782.
- **Status:** published as a conference chapter. **Read:** full text of arXiv v2 (Jan 2018); the
  chapter itself was not obtained. An extended journal version exists (*J. Intelligent
  Transportation Systems* 24(6):556-568, 2020, doi:10.1080/15472450.2019.1621756) and was **not
  read**. Cached: `refs/us_tordeux_1801_09782.*`.
- **What is tested for generalisation, and against what:** a speed model (a fundamental-diagram
  model with three parameters) and a small neural network, against **laboratory pedestrian
  trajectories** from a ring corridor (R) and a bottleneck (B) (§2).
- **How "unseen" is defined:** **a different geometry.** The authors define validation itself this
  way: "checking whether the models are able to describe the dynamics accurately for configurations
  different from the ones used for the calibration (cross-validation)" and "A good model should
  provide realistic dynamics in different conditions (i.e. different geometries, initial or boundary
  conditions) for the same setting of the parameters" (§1, p. 2). Train/test pairs R/R, B/B, R/B,
  B/R and combinations (§5, p. 6).
- **How overlap between training and test is prevented:** across geometries, by construction;
  within one, by bootstrap with half the data held out, 50 sub-samples (§4).
- **Results on unseen cases, and where generalisation failed:** the fitted time gap "significantly
  differs according to the geometry" (Table 1), i.e. one parameter set does not suit both. The
  network's improvement over the model on "unobserved situations, i.e. for the datasets R/B and
  B/R" was "around 15%", and best when trained on both (§5, p. 6). The authors call these "first
  steps" (§6).
- **What the FYP's test protocol should take from it:** `[inference]`
  - **Report every train/test pair**, including the reverse direction.
  - Expect **parameters** (the "binding" in #34's terms) to change with layout, even when the
    behaviour is the same kind. That supports keeping thresholds out of the portable core.
- **BibTeX:** `tordeux2019prediction`.

### [Wolinski-ParamEst]: Parameter Estimation and Comparative Evaluation of Crowd Simulations

- **Authors / Year / Venue / Link:** Wolinski, D., Guy, S. J., Olivier, A.-H., Lin, M., Manocha, D.,
  Pettré, J. / 2014 / *Computer Graphics Forum* 33(2):303-312 (Eurographics 2014),
  doi:10.1111/cgf.12328 (Crossref).
- **Status:** published, peer-reviewed. **Read:** full text of the authors' copy
  (https://gamma.cs.unc.edu/CParameter/eg2014-main.pdf), appendix not read. Cached on disk only.
- **What is tested, against what:** several crowd simulators (Boids-like, social force, RVO2) are
  each **calibrated per dataset** to real or sketched crowd data, then compared (Abstract; §4).
- **How "unseen" is defined:** it is not. Every comparison is after fitting to the same reference
  data.
- **How overlap is prevented:** not addressed.
- **Results, and where generalisation failed:** with default parameters, in "a simple crossing
  scenario between two pedestrians ... none of the algorithms correctly replicate the avoidance
  strategy" (§4, Fig. 3). Cross-scenario use is left open: "We would also like to study how
  parameters can be generalized beyond a given scenario or metric: can a certain set of parameters
  work well across various scenarios?" (§5, "Limitations").
- **What the FYP's test protocol should take from it:** `[inference]` per-scenario calibration
  makes a simulator look good on that scenario and says nothing about the next one. The protocol
  must **freeze any bindings before the held-out scenarios are run**, or it will measure fitting,
  not transfer.
- **BibTeX:** `wolinski2014parameter`.

---

## Q2. Transfer between structurally different games: the g6 §3 leads

g6 §3 listed six "behavioural spillovers" studies it could not open. Open versions were found for
five; the published versions were not read in any case, so **locators are to the versions read**.

### [CooperVanHuyck-Transfer]: Coordination and Transfer

- **Authors / Year / Venue / Link:** Cooper, D. J., Van Huyck, J. / 2018 (online 2017) /
  *Experimental Economics* 21(3):487-512, doi:10.1007/s10683-017-9521-8 (Crossref).
- **Status:** published, peer-reviewed. **Read:** full text of the **accepted manuscript** dated
  20 February 2017 (https://ueaeprints.uea.ac.uk/id/eprint/67255/1/Accepted_manuscript.pdf). Cached
  on disk only.
- **What is tested for transfer, and against what:** whether play learned in one coordination game
  carries over to related ones. **Treatments:** fixed order-statistic game (Fixed); a random
  sequence of order-statistic games (ROS); and stag hunts followed by random order-statistic games
  (SHROS) (Abstract; §2).
- **How "unseen" is defined:** **a different game.** The order-statistic games "have a different
  number of actions, a different payoff structure, and different locations for equilibria than the
  stag hunt games" (§1, p. 7). The authors admit "the absence of any clear metric for similarity
  between games" (fn. 6, p. 4).
- **How overlap is prevented:** the stag hunts were randomised so that "the direct relationship
  between actions" was "less salient" (Author's note, p. 2).
- **Results, and where transfer failed:** "transfer can take place even when games are not
  structurally similar" (§4, p. 24). SHROS groups that had converged on the payoff-dominant
  equilibrium played higher in the new games (Conclusion 3, §3). But **transfer can hurt**: in ROS
  "there is strong transfer between games which harms payoffs relative to the treatment where OS is
  held fixed" (§1, p. 7). Limits stated by the authors:
  - "All of the games in our experiments are coordination games with a payoff dominant equilibrium
    and a secure equilibrium";
  - subjects stayed "in the same cohort throughout", so they knew their partners shared the same
    experience (§4, p. 24).
- **What the FYP's test protocol should take from it:** `[inference]`
  - This **qualifies g6's "no evidence of transfer"**: humans do carry an *equilibrium-selection
    principle* across differently structured games, **within one class** of games.
  - That matches #34's "same kind of conflict" claim, not "any conflict".
  - The cohort caveat matters for L0: transfer may rely on everyone having learned the same thing.
- **BibTeX:** `cooper2018coordination`.

### [Cason-Spillovers]: Behavioral Spillovers in Coordination Games

- **Authors / Year / Venue / Link:** Cason, T. N., Savikhin, A. C., Sheremeta, R. M. / 2012 /
  *European Economic Review* 56(2):233-245, doi:10.1016/j.euroecorev.2011.09.001 (Crossref).
- **Status:** published, peer-reviewed. **Read:** full text of the MPRA version dated 1 September
  2011 (MPRA Paper 52106; earlier title "Cooperation Spillovers in Coordination Games"). Cached on
  disk only.
- **What is tested for transfer, and against what:** minimum-effort and median-effort games played
  in sequence (SeqMin, SeqMed, SeqMedDiff with new groups) or at the same time (Sim) (§3).
- **How "unseen" is defined:** a second game with a different payoff rule (minimum vs median).
- **How overlap is prevented:** in SeqMedDiff, group composition changes between games (§3).
- **Results, and where transfer failed:** "cooperative behavior in the median game influences
  behavior in the minimum game when the games are played sequentially. This spillover occurs (but
  is weaker) even when group composition changes. Behavior in the minimum game does not
  significantly affect play in the median game" (§7, p. 22). In numbers: 8 of 10 groups coordinated
  efficiently on the minimum game after the median game, against 4 of 15 when the two were played
  at the same time (§5, p. 15).
- **What the FYP's test protocol should take from it:** `[inference]` transfer is **directional**.
  A rule extracted in one conflict type and tested on another must be tested in **both directions**
  before any claim is made, as with [Tordeux-ANN]'s R/B and B/R.
- **BibTeX:** `cason2012behavioral`.

### [Huck-FeedbackSpillover]: Feedback Spillover and Analogy-Based Expectations: A Multi-Game Experiment

- **Authors / Year / Venue / Link:** Huck, S., Jehiel, P., Rutter, T. / 2011 / *Games and Economic
  Behavior* 71(2):351-365, doi:10.1016/j.geb.2010.06.007 (Crossref).
- **Status:** published, peer-reviewed. **Read:** full text of the **2007 working paper**, "Learning
  Spillover and Analogy-Based Expectations: A Multi-Game Experiment" (UCL Discovery,
  https://discovery.ucl.ac.uk/id/eprint/14462/1/14462.pdf). The open postprint on HAL
  (halshs-00754551) was blocked by HAL's bot protection. **The published version may differ**, and
  even its title changed. Cached on disk only.
- **What is tested for transfer, and against what:** two games played side by side, with four
  feedback treatments: Fine, Coarse, Feasible and Hard (§1, pp. 2-3).
- **How "unseen" is defined:** not a new game; the question is whether experience in one game
  **contaminates** play in the other.
- **How overlap is prevented:** this *is* the manipulation. In Fine, information is "nicely
  separated for each game"; in Coarse, it is aggregated across games (§1, p. 3).
- **Results, and where transfer failed:** Fine and Feasible converge to Nash equilibrium; in Hard,
  "behavior stabilizes at the same action profiles as in Coarse ... despite the fact that precise
  information is available" (§1, p. 3). "The less accessible, the more likely are (learning)
  spillovers from one game to the other" (§7, p. 24).
- **What the FYP's test protocol should take from it:** `[inference]` whether a person treats two
  situations as one depends on **how easily they can be told apart**. A portable rule that
  matches on conflict type alone is the "coarse" case on purpose. The protocol should test whether
  the **perception adapter** can tell held-out conflict types apart, not only whether the decision
  is right.
- **BibTeX:** `huck2011feedback`.

### [GrimmMengel-MultipleGames]: An Experiment on Learning in a Multiple Games Environment

- **Authors / Year / Venue / Link:** Grimm, V., Mengel, F. / 2012 / *Journal of Economic Theory*
  147(6):2220-2259, doi:10.1016/j.jet.2012.05.011 (Crossref).
- **Status:** published, peer-reviewed. **Read:** full text of the **2009 working paper** (METEOR
  RM/09/007, Maastricht, doi:10.26481/umamet.2009007). **The published version may differ.** Cached
  on disk only.
- **What is tested for transfer, and against what:** 3 × 3 normal-form games drawn at random each
  round for 100 rounds; the number of games and the information about opponents are varied
  (Abstract; §2).
- **How "unseen" is defined:** many games at once; whether players "extrapolate between games"
  (Abstract).
- **How overlap is prevented:** not applicable; overlap is what is measured.
- **Results, and where transfer failed:** "participants do extrapolate between games, but learn to
  play strategically equivalent games in the same way". Play reaches Nash equilibrium "if either
  there are few games or if explicit information about the opponent's behavior is provided";
  "otherwise ... play converges to a distribution of actions which is Non-Nash" (§1, p. 2; §4,
  pp. 21-22). "70% (80%) of all participants in treatment M (MI) display the same choice behavior in
  all games that are strategically equivalent" (§3, p. 14).
- **What the FYP's test protocol should take from it:** `[inference]` people group situations by
  **strategic equivalence**, which is what #34's conflict types try to capture. But with **many
  situation types and little feedback**, people settle on behaviour that is right for none of them.
  An extracted rule set with too many fine-grained types risks the same. This supports a **small,
  coarse vocabulary**, tested for whether its types match the ones people use.
- **BibTeX:** `grimm2012experiment`.

### [CooperKagel-Signaling]: Learning and Transfer in Signaling Games

- **Authors / Year / Venue / Link:** Cooper, D. J., Kagel, J. H. / 2008 (online 2006) / *Economic
  Theory* 34(3):415-439, doi:10.1007/s00199-006-0192-5 (Crossref).
- **Status:** published, peer-reviewed. **Read:** full text of the **final submission** dated 16
  November 2006 (author's site,
  https://www.asc.ohio-state.edu/kagel.4/Cooper%20and%20Kagel,%20ET%20final%20submission.pdf).
  Cached on disk only.
- **What is tested for transfer, and against what:** after play converges to a pooling equilibrium
  in a limit-pricing signalling game, payoffs change so that only separating equilibria exist
  ("crossover"). Crossover subjects are compared with inexperienced and experienced controls
  (Abstract).
- **How "unseen" is defined:** **a related game where the strategic action is different**: subjects
  "transfer much of this knowledge to related games even if the actions necessary to play
  strategically are quite different" (§VII, p. 20).
- **How overlap is prevented:** control sessions without the earlier game (Abstract).
- **Results, and where transfer failed:** positive transfer, explained by a growing share of
  "sophisticated learners" (§VII, pp. 20-21). **Failure condition:** the authors report that their
  "meaningful context" matters. "Using generic context, the same cross-over treatment generates zero
  or even slightly negative cross-game learning", and context can also hurt in another example
  (§VII, p. 21, citing Cooper and Kagel 2006, not read).
- **What the FYP's test protocol should take from it:** `[inference]` how a situation is
  **described** changes whether experience carries over. For LLM-elicited rules, the wording of a
  scenario is part of the treatment. Held-out scenarios should be tested with **more than one
  wording**.
- **BibTeX:** `cooper2008learning`.

### [MengelSciubba-Extrapolation]: Extrapolation and structural similarity in games (stub)

- **Title:** Extrapolation and structural similarity in games
- **Authors, year and venue:** Mengel, F., Sciubba, E. / 2014 / *Economics Letters* 125(3):381-385,
  doi:10.1016/j.econlet.2014.10.015 (confirmed on Crossref)
- **Links tried:** https://repository.essex.ac.uk/20331/ (connection failed twice);
  https://ageconsearch.umn.edu/record/98475 (HTTP 403; this is the 2010 working paper "Extrapolation
  in Games of Coordination and Dominance Solvable Games", FEEM Nota di Lavoro 148.2010);
  the Maastricht repository copy of that working paper (HTTP 403); the TSE seminar copy (HTTP 404)
- **Reason unavailable:** publisher paywall; every open copy found refused automated download
- **Date attempted:** 2026-10-18
- **Status:** awaiting PDF from user

---

## Q4. Leakage: separating "the model already knows the norm" from generalisation

The starting point is g5 §4, read for this issue and not repeated. Its three conclusions:

- the FYP's scenarios have literature-attested answers, so Ashery et al.'s "no right answer"
  defence is not available;
- asking the model is cheap;
- the defensible claim is "an LLM is a usable elicitation device ... which we then extract,
  formalise and test independently of the LLM".

Cross et al. 2025 (g6 §2) adds a two-stage design: reproduce a known result, then predict an
unpublished one and test it against humans. The three entries below are the methods for the
middle step: making the test item something the model cannot simply recall.

### [Wu-Counterfactual]: Reasoning or Reciting? Exploring the Capabilities and Limitations of Language Models Through Counterfactual Tasks

- **Authors / Year / Venue / Link:** Wu, Z., Qiu, L., Ross, A., Akyürek, E., Chen, B., Wang, B.,
  Kim, N., Andreas, J., Kim, Y. / 2024 / *Proceedings of NAACL 2024 (Volume 1: Long Papers)*,
  pp. 1819-1862, doi:10.18653/v1/2024.naacl-long.102 (Crossref) / arXiv:2307.02477.
- **Status:** published at NAACL 2024. **Read:** full text of arXiv v3 (28 March 2024). Cached:
  `refs/us_arxiv_2307_02477.*`.
- **What is tested for generalisation, and against what:** LLMs on 11 tasks under the **default**
  conditions and under **counterfactual** conditions, e.g. base-10 versus base-9 addition (§§2-3).
- **How "unseen" is defined:** a change to the task's "world model" rather than new inputs:
  "generalization to new task variants in counterfactual worlds w_cf, instead of new inputs x" (§2).
- **How overlap between training and test is prevented:** **only partly, and they say so.** "Nor
  do we aim to guarantee that counterfactual world models are unobserved in a pretraining corpus.
  Instead, counterfactuals are simply defined as variations on the default conditions" (§2). A
  **counterfactual comprehension check** tests that the model understood the changed conditions,
  so a failure is not just a misread prompt (§2.1).
- **Results on unseen cases, and where generalisation failed:** above-random but "substantially and
  consistently" worse on counterfactual variants (Abstract; §4), "sometimes even dropping from
  near-perfect to near-zero" (§4). Commoner variants did better: "bases 8 and 16, likely due to
  their relative abundance" (§5.1); performance also fell with distance from the default (§5.2).
- **What the FYP's test protocol should take from it:** `[inference]`
  - For each held-out scenario, keep a **default** version (the familiar real-world one, e.g.
    Singapore MRT etiquette) and a **counterfactual** one where the convention is changed but
    stated (e.g. "at this station, boarders enter first by a posted rule").
  - Add a **comprehension check** that the model read the changed rule.
  - A rule that only works in the default world is evidence of recall.
- **BibTeX:** `wu2024reasoning`.

### [Aher-TuringExperiments]: Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies

- **Authors / Year / Venue / Link:** Aher, G. V., Arriaga, R. I., Kalai, A. T. / 2023 /
  *Proceedings of the 40th International Conference on Machine Learning*, PMLR 202, pp. 337-371
  (confirmed on https://proceedings.mlr.press/v202/aher23a.html) / arXiv:2208.10264.
- **Status:** published at ICML 2023. **Read:** arXiv v5 (9 July 2023): §§1-2 and 6-9, Appendix F.2.
  Cached: `refs/us_arxiv_2208_10264.*`.
- **What is tested for generalisation, and against what:** "Turing Experiments": an LLM simulates
  many participants in a classic study, compared with the published human results (Ultimatum Game,
  garden-path sentences, Milgram, wisdom of crowds) (§1).
- **How "unseen" is defined:** **new variants written by the authors**. "As discussed, the models
  have almost certainly been trained on data that includes descriptions of these experiments. For
  that reason, we created three artificial variations of TEs where the conditions are chosen to
  differ from prior studies" (§8). These were new garden-path sentences, new general-knowledge
  questions, and a "novel destructive obedience scenario" (§8; App. F, with its materials in App. F.2).
- **How overlap between training and test is prevented:** surface novelty only. The authors
  concede the residual similarity: "at its core, the novel experiment is reminiscent of Milgram's
  shock experiment. This similarity is, in some sense, inherent if our goal is to test robustness of
  the simulation to the experimental setting" (App. F).
- **Results on unseen cases, and where generalisation failed:** in the novel scenario, "75 of the
  simulated subjects obeyed" (App. F), the same 75/100 as in the Milgram TE (Fig. 7). The wisdom
  of crowds TE revealed a "hyper-accuracy distortion" in larger, more aligned models (§9).
- **What the FYP's test protocol should take from it:** `[inference]`
  - A **renamed, re-set** version of a known conflict (a "new" boarding situation that is a
    doorway deadlock in disguise) tests robustness to wording, **not** generalisation to a new
    conflict type.
  - In #34's levels, that makes it L1/L2, not L3, and it should be labelled so.
- **BibTeX:** `aher2023using`.

### [Binz-CogPsychGPT3]: Using cognitive psychology to understand GPT-3

- **Authors / Year / Venue / Link:** Binz, M., Schulz, E. / 2023 / *Proceedings of the National
  Academy of Sciences* 120(6):e2218523120, doi:10.1073/pnas.2218523120 (Crossref; arXiv lists the
  same DOI) / arXiv:2206.14576.
- **Status:** published in PNAS. **Read:** arXiv v1 (21 June 2022), Abstract, Introduction and the
  vignette sections. **The published version was not read and may differ.** Cached:
  `refs/us_arxiv_2206_14576.*`.
- **What is tested, against what:** GPT-3 on canonical vignettes and task-based experiments from
  cognitive psychology, compared with human results (Abstract).
- **How "unseen" is defined:** **adversarial vignettes**, small changes to famous problems (e.g.
  reordering Wason's cards; asking about a black cab when only blue and green exist) (section
  "Problems with vignette-based investigations").
- **How overlap between training and test is prevented:** by the perturbations, and by moving to
  generated task-based experiments, because with vignettes "it is ... not possible to decide whether
  it is merely behaving like a parrot, repeating what it has seen in the training data, or whether
  it is reasoning successfully" (section "Task-based investigations").
- **Results on unseen cases, and where generalisation failed:** on 12 standard vignettes, GPT-3
  answered "six correctly and all 12 in a way that could be described as human-like", but on the
  adversarial versions "it makes mistakes that are not human-like" (Fig. 1 caption; vignette
  section).
- **What the FYP's test protocol should take from it:** `[inference]` include **minimal
  perturbations** of each familiar scenario (swap who arrived first; change one role). A human-like
  answer on the canonical version and a non-human-like one on the perturbed version is the
  signature of recall.
- **BibTeX:** `binz2023using`.

**What Q4 adds up to.** `[inference]` None of the three methods proves absence from training data.
Wu et al. explicitly disclaim it (§2), and g5 §4 records Barrie & Törnberg calling leakage
"fundamental and intractable without strict control over the training data". So the protocol
should do three things:

- use these methods to **grade** a result, as stronger or weaker evidence against recall;
- keep the claim at g5 §4's level: the *rules* are tested, the LLM's understanding is not claimed;
- put the burden of proof on **human evidence for held-out conflict types** (PT-3), which is the
  only reference the LLM cannot have tuned itself to.
