# B3 & B4 — Gender and age in real human crowds and real human conflict

Prepared for issue [#16](https://github.com/M450NCH00/CrowdSimulation/issues/16).
Template: **H** (issue #16). Companion files:
[`llm-demographic-effects.md`](llm-demographic-effects.md) (B1/B2),
[`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md),
[`search-log.md`](search-log.md), [`refs.bib`](refs.bib).

**Scope reminder.** Only **gender** and **age** findings are extracted.

---

## ⚠ Read this before using any B3 entry: the "human evidence" here is not all human

The B3 literature divides sharply into two kinds of source, and **the issue's
realism-vs-bias question depends entirely on telling them apart**:

- **(a) Measurements of people.** Experiments or observations where real pedestrians walked
  and something was recorded. In this file: [Rapos-CollisionAvoidance],
  [Yamamoto-BodyRotation], and (with a caveat) [Minegishi-SlowPedestrians].
- **(b) Simulations in which the demographic effect is an input assumption.** Cellular-automata
  and floor-field evacuation models where women are *assigned* a slower speed or a lower
  "competitiveness" coefficient, and the model then *outputs* that crowds with more women
  evacuate more slowly. In this file: [Zhu-MultiAttribute] and [Ding-AsymmetricCompetitiveness].

**Type (b) cannot be used as human evidence in
[`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md).** Its gender and age effects
are not discoveries; they are restatements of the parameters. Two of the three B3 seeds the
issue lists are of type (b). Both are still recorded in full below — they are genuinely useful
as evidence of *how conventional crowd models encode demographics*, which is exactly what the
issue asked for from the Symmetry paper — but each entry states explicitly which numbers are
assumptions and which are results, and traces the assumption back to its own cited source
where the paper gives one.

[inference] This is itself a finding worth putting to the supervisor: the citation chain
underneath "gender affects crowd dynamics" is much shorter and thinner than the volume of
literature suggests, because many papers inherit the same handful of speed measurements.

---

# B3. Gender and age in real crowd and pedestrian behaviour

### [Rapos-CollisionAvoidance]: Collision avoidance behaviours between older adult and young adult walkers
- **Authors / Year / Venue:** Victoria Rapos, Michael E. Cinelli, Robyn Grunberg, Sheryl
  Bourgaize (Wilfrid Laurier University), Armel Crétual, Anne-Hélène Olivier (Univ Rennes /
  Inria) / 2021 / *Gait & Posture* 88, pp. 210–215.
- **Link:** doi:10.1016/j.gaitpost.2021.05.033
- **Peer-review status:** **published**, peer-reviewed journal (Elsevier).
- **Verified:** **abstract only.** Bibliographic fields confirmed from the **Crossref record**
  (`refs/cr_olderyoung.json`); the structured abstract was read from the **Europe PMC record**
  of the publisher's abstract. **Full text not accessed** — sciencedirect.com and
  linkinghub.elsevier.com returned errors/redirect blocks to every route I tried, and Europe
  PMC records it as "Subscription required"; HAL holds a metadata-only record
  (`hal.science/hal-03368055v1`, no deposited file) and its page was also blocked.
  **Everything below is from the abstract. Locators are therefore to abstract sections
  (Methods / Results), not to body sections.** `[needs verification against full text]` for
  anything beyond what is quoted here.
- **Sub-area:** B3
- **Tags:** none (2021, within the 2016–2026 window)
- **Demographic attributes studied:** **age** (older adults vs young adults). Gender is not
  reported in the abstract.
- **Data basis:** **experiment.** "Seventeen older adults (x̄ = 68 ± 3 years) and seventeen
  young adults (x̄ = 23 ± 2 years) walked at a comfortable walking speed along a 12.6 m
  pathway while avoiding another walker. Trials were randomized equally to include 20
  interactions with the same age group and 21 interactions with the opposite age group"
  (Methods). Outcome measure: minimum predicted distance (mpd).
- **Main finding (direction and size):**
  - "Older adults had riskier avoidance behaviours, **passing closer to the other pedestrian
    (0.79 m ± 0.18 m) compared to when two young adults were on a collision course
    (0.93 m ± 0.17 m)** (χ²(3) = 35.94, p < .0001)" (Results).
  - **The finding that matters most for this FYP:** "**Whenever an older adult was on a
    collision course with a young adult, the young adult contributed more to the avoidance
    regardless of passing order**" (Results).
- **Does it concern yielding, conceding, or conflict resolution specifically?** **Yes —
  directly, and it is the only source in this review that measures who yields to whom by age
  in a real pedestrian encounter.** A two-walker collision course in a corridor is the
  physical analogue of the FYP's doorway conflict, and "who contributed more to the
  avoidance" is precisely the yielding variable. The mechanism the authors propose is
  capability, not courtesy: the framing is "[a]ge-related changes to visuomotor processing,
  kinesthetic input, and intersegmental dynamics" increasing collision and fall risk
  (Background), and the older adults' behaviour is described as "riskier", not as more
  assertive.
- **Location and population studied:** not stated in the abstract; the authors are at
  Wilfrid Laurier University (Canada) and Univ Rennes / Inria (France), so a Canadian and/or
  French sample is likely but **unconfirmed** `[needs verification against full text]`.
  This matters — see the culture caveat under Open Questions.
- **Limitations stated by the authors:** the abstract states only a forward-looking one:
  "Future studies should further investigate age-related visuomotor deficits during collision
  avoidance tasks in cluttered environments using virtual reality in order to tease out
  factors that contribute most to avoidance behaviours in older adults" (Significance). A
  limitations section was not accessible. The sample is small (17 + 17) and the task is a
  single clean corridor encounter, not a crowd.
- **Relevance to this FYP:**
  - **This is the human baseline for the FYP's age hypothesis, and it points the opposite
    way to `run01`.** `run01`'s validator records "PASS: elderly yield at least as much as
    young adults" (`dataset/generated/validation_report.md`, INFO). Rapos et al. measure real
    pedestrians and find the **young adult** doing more of the avoidance work when meeting an
    older adult — i.e. in the real encounter, the older pedestrian yields *less*. See
    [`realism-vs-bias-comparison.md`](realism-vs-bias-comparison.md), row H1/RUN01-AGE.
  - [inference] The two results are not necessarily contradictory in intent: the LLM appears
    to be modelling a *norm* (older people are cautious and defer), while the experiment
    measures an *outcome* (older adults hold their line and the young adult moves). A crowd
    simulator needs the outcome, not the norm. This distinction — normative belief versus
    measured behaviour — is the sharpest available framing of the FYP's whole research
    question, and it is exactly what an LLM trained on text would be expected to get wrong.
  - Practical consequence for CrowdGym integration: if young agents absorb the avoidance
    burden around elderly agents, then in a dense mixed-age crowd the *young* agents' paths
    are the ones that deform. A model that instead makes elderly agents yield will
    redistribute congestion incorrectly.
- **BibTeX:** `rapos2021collision` — see [`refs.bib`](refs.bib).

---

### [Yamamoto-BodyRotation]: Body-rotation behavior of pedestrians for collision avoidance in passing and cross flow
- **⚠ Already present in this repository.** This paper is already catalogued in
  `literature/llm-conflict-resolution/refs.bib` as `yamamoto2019body` (from issue #8). Per the
  issue's "Do not re-collect papers already present. If an existing paper is relevant here,
  reference it rather than duplicating its entry", **it is not re-entered as a new
  reference.** What follows is the *gender finding only*, which the existing entry does not
  record and which no existing repo file mentions (a grep of `literature/**` for `gender`,
  `female` and `male` returns nothing).
- **Authors / Year / Venue:** Hiroki Yamamoto, Daichi Yanagisawa, Claudio Feliciani, Katsuhiro
  Nishinari / 2019 / *Transportation Research Part B: Methodological* 122 — as recorded in the
  existing `refs.bib`.
- **Link:** preprint read: https://arxiv.org/abs/1903.07742
- **Peer-review status:** **published** (journal entry already in the repo's `refs.bib`).
- **Verified:** yes — full text read, **from the arXiv preprint**
  (`refs/b3_yamamoto_bodyrotation.pdf`). Locators below are to the preprint; section and
  table numbers may differ in the journal version. `[needs verification against full text]`
  for the published version.
- **Sub-area:** B3
- **Demographic attributes studied:** **gender**, and incidentally **age** (participants
  spanned 21–68, but age is not analysed as a factor).
- **Data basis:** **experiment.** "Corridor experiment 2", at RCAST, The University of Tokyo:
  "five male participants, ages 21, 24, 29, 66, and 68, and four female participants, ages
  36, 45, 61, and 64" (§7). Corridor width W varied over 60, 70, 80, 90, 100, 120, 140 cm;
  "72 × 7 (widths) = 504 datasets were obtained in total" (§7). Body rotation measured by
  strapped-on tablets recording angular velocity at ~50 Hz (§8.1). (The earlier "corridor
  experiment 1" used four male adolescents only, §7.)
- **Main finding (direction and size):**
  - "**θ_ave is significantly larger for the males than for the females at W = 60 and 70 cm
    (p < 0.05)**" (§8.2) — i.e. men rotate their bodies more when squeezing past.
  - **The mechanism is body size, not deference:** "since the shoulder widths of the males
    were significantly larger than those of the females, the males had to rotate more than the
    females" (§8.2). Table 2: male shoulder width **48.4 cm (SD 3.7)**, female **41.0 cm
    (SD 1.4)**, "significantly different in terms of statistics (p < 0.05)", while bust depths
    (26.0 vs 23.4 cm) were **not** significantly different.
  - **A second, behavioural gender difference:** from the fitted error parameters,
    "β_a,M < β_a,F and β_b,M < β_b,F, it can be concluded that the **females kept a greater
    distance between each other than the males** in the passing situation in our experiment"
    (§8.2).
  - Female pairs "did not need to rotate" at the wider corridor settings — their data were
    usable only for W = 60–80 cm, against 60–100 cm for male pairs (§8.2).
- **Does it concern yielding, conceding, or conflict resolution specifically?** **Partly.**
  It concerns *how* two pedestrians resolve a narrow-passage conflict without stopping —
  body rotation and interpersonal distance — which is the sub-second behaviour underneath a
  yield. It does **not** measure who gives way or who goes first.
- **Location and population studied:** Japan (The University of Tokyo); nine adults aged
  21–68. Small sample.
- **Limitations stated by the authors:** corridor experiment 1 used "all four participants
  ... male adolescents", which is why experiment 2 was run "to demonstrate that the obtained
  results are valid for all pedestrians" (§7); the authors note the measured shoulder widths
  exceed published statistical values, "likely due to clothing thickness" (Table 2 note).
  Nine participants is a small base for a significance claim, and the effect is confined to
  the two narrowest corridor widths.
- **Relevance to this FYP:**
  - **This is a real gender difference in pedestrian conflict behaviour whose cause is
    anthropometric.** It is the cleanest available example of the distinction the whole issue
    turns on: a genuine, measurable, replicable gender effect that has **nothing to do with
    deference, politeness or social role**.
  - [inference] It therefore sets a trap for the FYP. If an LLM is asked "does gender affect
    how pedestrians pass each other?", the true answer is yes — but for reasons an LLM
    reproducing social discourse is unlikely to give, and the *behavioural* consequence
    (women maintaining more clearance, men rotating more) is not "women yield more". If
    `run01`'s gender effect is really a proxy for body size, it is being encoded in the wrong
    variable: CrowdGym already has per-agent radius parameters
    (`integration/crowdgym_mapping.md`), so shoulder width belongs in the geometry, not in a
    yield-likelihood.
  - Actionable: this gives a defensible, non-stereotyped way to put gender into the
    simulation — as body radius and preferred clearance — separate from any yield-likelihood
    claim.
- **BibTeX:** already present as `yamamoto2019body` in
  `literature/llm-conflict-resolution/refs.bib`. **Not duplicated** in this folder's
  `refs.bib`.

---

### [Minegishi-SlowPedestrians]: Experimental study of the walking behavior of crowds mixed with slow-speed pedestrians as an introductory study of elderly-mixed evacuation crowds
- **Authors / Year / Venue:** Yoshikazu Minegishi / **2021** / *Fire Safety Journal* 120,
  article 103041.
- **Link:** doi:10.1016/j.firesaf.2020.103041
- **Peer-review status:** **published**, peer-reviewed journal (Elsevier).
- **⚠ Year correction.** The issue lists this seed with a ScienceDirect PII of the form
  `S0379711220300345`, which reads as a 2020 item. The **Crossref record**
  (`refs/cr_slowped.json`) gives the journal issue as **March 2021**, *Fire Safety Journal*
  **volume 120, article 103041**. Cite 2021.
- **Verified:** **abstract only.** Bibliographic fields confirmed from the Crossref record;
  the abstract was retrieved from the **Semantic Scholar record** of the publisher abstract.
  **Full text not accessed** — sciencedirect.com returned a client error, doi.org redirected
  to linkinghub.elsevier.com which returned only a "Redirecting" stub, and the paper is **not
  in Europe PMC**. `[needs verification against full text]` applies to everything not quoted
  below. *Transcription note: the retrieved abstract contains a dropped word — "there are
  many people who are slow-footed, especially people" — where the published text almost
  certainly reads "especially elderly people". Quoted as retrieved; verify before citing that
  sentence.*
- **Sub-area:** B3
- **Tags:** none (2021)
- **Demographic attributes studied:** **age — but only indirectly.** The experiment
  manipulates **walking speed**, not age. Age enters through the framing: the study is
  positioned "as an introductory study of elderly-mixed evacuation crowds" (title) and
  motivated by slow-footedness among (elderly) people (Abstract). **The abstract reports no
  age split and no gender split of participants.**
- **Data basis:** **experiment** — "a parametric evacuation experiment. Walking behaviors on a
  simple straight 12.6 m path are examined" (Abstract). Participant count is **not stated in
  the abstract** `[needs verification against full text]`.
- **Main finding (direction and size):**
  - "Compared with a no-slow-speed pedestrian crowd, the overall flow rate on the 1.2 m wide
    path **decreased to 71% for the 10% slow-speed-pedestrian mixed case and to 61% for the
    20% case**" (Abstract).
  - "Analysis of the trajectories of average pedestrians in relative coordinates based on the
    speed of slow-speed pedestrians revealed that **the behavior when passing the slow-speed
    pedestrians was strongly governed by the density of pedestrians and the percentage of
    slow-speed pedestrians**" (Abstract).
- **Does it concern yielding, conceding, or conflict resolution specifically?** It concerns
  **overtaking**, which is a conflict-resolution decision (whether and how to pass someone in
  your way). **However — and this must be flagged — the issue's note for this seed says the
  paper "discusses how people's inclination to care for or wait for elderly pedestrians
  affects overtaking decisions". I could not confirm that claim.** The abstract attributes
  passing behaviour to *density and mix proportion*, and says nothing about caring for or
  waiting for anyone. The claim may well be in the full text, which I could not reach. **Do
  not cite the "inclination to care for" claim until the full text is obtained.**
- **Location and population studied:** not stated in the abstract; the author is
  Japan-based (Minegishi publishes in *Japan Architectural Review*), so a Japanese sample is
  likely but **unconfirmed**.
- **Limitations stated by the authors:** not available from the abstract.
- **⚠ Qualification against the issue's selection criterion.** The issue requires an
  empirical result on how **gender or age** changes behaviour. On the evidence available to
  me, this paper reports an effect of **speed heterogeneity**, with age as motivation rather
  than as a measured variable. **On the abstract alone it does not strictly qualify.** It is
  retained here because the issue named it as a verified seed, because the speed→age link is
  explicit in its own title, and because the flow-rate numbers are directly usable. It should
  be re-assessed once the full text is available.
- **Relevance to this FYP:**
  - The **71% / 61% flow-rate numbers are directly usable as a CrowdGym validation target**:
    a mixed-speed crowd in the simulator should show a comparable degradation, and if it does
    not, the simulation's overtaking logic is wrong independently of any LLM question.
  - [inference] It supports treating **age primarily as a speed parameter** rather than as a
    yielding disposition — which is how CrowdGym's AgentType parameters already work
    (`integration/crowdgym_mapping.md`), and which converges with the reading of
    [Yamamoto-BodyRotation] above: the defensible demographic effects in the pedestrian
    literature are *physical* (speed, size), not *attitudinal*.
- **BibTeX:** `minegishi2021experimental` — see [`refs.bib`](refs.bib).

---

### [Zhu-MultiAttribute]: An enhanced multi-attribute crowd evacuation model incorporating the effects of environmental impact factors
- **Authors / Year / Venue:** Lingjie Zhu, Xiaomeng Xu, Jian Wang, Jiahao Chen, Zhengjia Ma,
  Qiang Wang, Qifei Wang (China Jiliang University; Tianjin University; Beijing Academy of
  Science and Technology) / 2024 / *Heliyon* 10(4), e26299.
- **Link:** doi:10.1016/j.heliyon.2024.e26299 |
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10879021/
- **Peer-review status:** **published**, peer-reviewed journal; open access (CC BY-NC-ND 4.0
  per the Crossref licence field, `refs/cr_zhu_heliyon.json`).
- **Verified:** yes — full text read from the PMC version (`refs/b3_multiattribute_evac.html`,
  text extract `.txt`). Metadata cross-confirmed from Crossref.
- **Sub-area:** B3
- **Tags:** none (2024)
- **Demographic attributes studied:** **gender**, plus a combined "children or elderly"
  category. Also environmental familiarity and social relationships (not extracted).
- **Data basis:** **simulation — a calibrated model, not a measurement.** An enhanced floor
  field model (FFM) with Dynamic and Static Floor Fields, applied to a sports centre: "92.9 m
  long and 62.3 m wide ... approximately 5869 square meters ... three floors and eight exits
  ... 2252 seats designed to evacuate 2000 to 3000 people", with "the gender ratio of sports
  centers to 3:1, with children and the elderly accounting for 15% of all evacuation
  personnel" (§3).
- **⚠ The gender effect is an input, not a result.** Table 3 **assigns** movement speeds:
  emergency-state horizontal walking **male 1.35 m/s, female 0.98 m/s, children or elderly
  0.65 m/s**; emergency top-down **1.06 / 0.77 / 0.40 m/s**. The text is explicit that these
  are "[t]he evacuation speeds **assigned** to evacuees in this study" (§2.4.2), sourced to
  the paper's reference [30]. Body parameters are likewise assigned: males 45–80 kg,
  154–180 cm, radius 0.33–0.42; females 40–75 kg, 150–170 cm, radius 0.30–0.39 (§3).
- **Main finding (direction and size):**
  - "At the same initial population density, the **evacuation time of the population increases
    with an increase in the proportion of females** in the evacuation scenario. **The reason
    behind this phenomenon is that, compared to males, females have slower movement
    speeds**" (§4) — the authors state the circularity themselves.
  - "In comparison to environmental factors such as obstacles, the gender and the proportion
    of pedestrians familiar with the environment significantly influence asymmetrical
    evacuation ... **Among these, gender exerts a more substantial impact on evacuation**"
    (§5, conclusions (2)–(3)).
  - "[T]he increase in the proportion of pedestrians familiar with the environment has no
    significant effect on evacuation time compared with the gender ratio" (§4).
- **Does it concern yielding, conceding, or conflict resolution specifically?** **No.** It
  concerns aggregate evacuation time and spatial asymmetry. No pairwise yielding decision is
  modelled or measured.
- **Location and population studied:** a simulated Chinese sports centre; no human
  participants.
- **Limitations stated by the authors:** `[needs verification against full text]` — I read the
  abstract, model description, results and conclusions and did not locate a dedicated
  limitations section. **The limitation that matters is not one they state:** the headline
  gender result is entailed by Table 3's assigned speeds. Also note that **"children or
  elderly" are collapsed into a single 0.65 m/s category**, so this model cannot distinguish
  a child from an elderly pedestrian at all, and assigns **no gender split within** that
  category.
- **Relevance to this FYP:**
  - Use it as **evidence of modelling convention**, not as evidence about people: it
    documents that a 2024 peer-reviewed crowd model encodes gender purely as a speed and
    body-size parameter, with **no** yielding, deference or negotiation component. That is a
    useful baseline against which the FYP's contribution (a *negotiated* resolution) can be
    positioned.
  - **It cannot support any claim that women yield more.** It contains no yielding variable.
  - [inference] The collapsing of children and elderly into one parameter is a concrete
    weakness in existing models that the FYP could improve on, and it mirrors
    [Chu-Marketing]'s finding on the LLM side that these are exactly the two groups LLMs also
    fail to distinguish — an interesting convergence, and a place where LLM-derived behaviour
    could add something conventional models lack.
- **BibTeX:** `zhu2024enhanced` — see [`refs.bib`](refs.bib).

---

### [Ding-AsymmetricCompetitiveness]: Modeling and Research on Multi-Speed Heterogeneous Crowd Evacuation with Asymmetric Competitiveness
- **Authors / Year / Venue:** Yuanchun Ding, Binwen Liu (Jiangxi University of Science and
  Technology) / 2025 / *Symmetry* 17(2), article 298, published 16 February 2025.
- **Link:** doi:10.3390/sym17020298 | https://www.mdpi.com/2073-8994/17/2/298
- **Peer-review status:** **published**, peer-reviewed MDPI journal; CC BY 4.0.
  Authors, journal, volume, issue, article number and date confirmed from the **Crossref
  record** (`refs/cr_sym17020298.json`) and from the PDF's own citation block.
  **Access note:** mdpi.com returned HTTP 403; the PDF was obtained from MDPI's asset host
  (`mdpi-res.com`). ⚠ **The PDF itself is not committed** — at 19 MB it would have bloated
  the repository; the **text extract `refs/b3_asymmetric_competitiveness.txt` is tracked and
  is what the locators below refer to**, and `.gitignore` records the URL to re-download the
  PDF from.
- **Verified:** yes — full PDF read.
- **Sub-area:** B3
- **Tags:** none (2025)
- **Demographic attributes studied:** **age** (young / middle-aged / old) and **gender**
  (male / female), both entering a per-pedestrian "competitiveness" score.
- **Data basis:** **simulation — a multi-speed cellular automata (CA) model.** Single-exit
  room, N from 50 to 400 pedestrians, pheromone radius r, avoidance probability and avoidance
  threshold as control parameters (§3).
- **⚠ Again, the demographic coefficients are inputs.** Competitiveness is "expressed as a
  power function" of a speed factor, an **age factor** and a **gender factor**, with values
  given in Table 2 (§2). The empirical grounding the authors cite for the gender coefficient
  is: "**males are about 19% more competitive than females** [21,22,35]" and "The statistics
  of Shi et al. [22] showed that **males were overall 0.2 m/s to 0.3 m/s faster than females**
  on average" (§1). So the assumption is at least sourced — but it is still an assumption,
  and it is the same kind of speed statistic that [Zhu-MultiAttribute] uses.
- **Main finding (direction and size):** this model is markedly more informative than
  [Zhu-MultiAttribute] because it separates age from gender and because it explicitly models
  **avoidance behaviour**, which is a yielding mechanism.
  - **The headline comparison, from the Abstract:** "**evacuation time is weakly correlated
    with pedestrians' gender but strongly correlated with pedestrians' age**."
  - **Gender effect, quantified:** "with N = 400, **the evacuation time of all male
    pedestrians is 5% lower than that of all female pedestrians**" (§3.2.1); below 150
    pedestrians the gender curve is flat and "[g]ender composition was not significantly
    correlated with evacuation time" (§3.2.1).
  - **Gender effect disappears inside the elderly group:** "**the evacuation time of the
    elderly is not affected by the gender composition**, and the time curve goes flat, which
    is due to the fact that the elderly, both men and women, move slower, and the increase in
    the proportion of males does not enable them to reach the exit more quickly" (§3.2.1).
  - **Gender matters more for middle-aged than young:** "gender composition has a greater
    impact on evacuation time for middle-aged people than for young people. Using N = 400 as
    an example, the age composition of 1:0:0 and 0:1:0 reduces the evacuation time by **7 and
    8%**, respectively" (§3.2.1).
  - **Age effect, quantified:** "an increase in the proportion of older people **from 40% to
    80%**, resulting in a **13% increase in evacuation time**" (§3.2.2).
  - **Avoidance (= yielding) is strongly age-directed:** avoidance behaviour "reduce[s] the
    total evacuation time by **12 to 17%**" (§3.3). And: "**Older people are much more
    affected by avoidance behaviors than young and middle-aged people, and the avoidance
    behaviors of young and middle-aged people toward older people allow older people to leave
    the congestion and reach the exit much faster**" (§3.3).
  - Optimal avoidance probability ≈ 0.5; steepest gains for avoidance threshold 0.4–0.8
    (Abstract).
- **Does it concern yielding, conceding, or conflict resolution specifically?** **Yes, in
  model form.** "Avoidance behaviour" is exactly a yield, and the model resolves same-cell
  contests by a competitiveness-weighted winning probability: "where p_i is the winning
  probability of person i ... If a person, i, wins, eliminate the outed ... until the
  two-by-two competition between all ends and a winner is determined" (§2). That is a
  demographic priority-resolution rule — the conventional-model counterpart of what the FYP
  wants an LLM dialogue to produce.
- **Location and population studied:** simulated; no human participants. Chinese authors,
  Chinese-sourced speed statistics.
- **Limitations stated by the authors:** `[needs verification against full text]` — the PDF's
  text extraction is heavily garbled by duplicated line rendering, and I did not reliably
  locate a limitations section. The structural limitation is as above: age and gender enter as
  coefficients, so the age > gender conclusion partly reflects the coefficient magnitudes
  chosen in Table 2.
- **Relevance to this FYP:**
  - **The direction of its yielding rule agrees with [Rapos-CollisionAvoidance] and disagrees
    with `run01`.** Young and middle-aged agents avoid *for* older ones; older pedestrians are
    the beneficiaries, not the yielders. Two independent sources — one a measurement of real
    walkers, one a modelling convention — line up against `run01`'s "elderly yield at least as
    much as young adults".
  - The **"weakly correlated with gender, strongly correlated with age"** framing is the
    direct inverse of `run01`, whose *flagged* pattern is a strong gender effect (Δ up to 0.43
    in yield likelihood) while its age hypotheses pass quietly. [inference] If this modelling
    consensus is right, `run01` has the relative importance of its two variables backwards.
  - It is the best available answer to the issue's request for "a non-LLM model coupling age
    and gender to competitiveness and avoidance behaviour ... as a baseline for how
    conventional crowd models encode demographic attributes into conflict behaviour."
- **BibTeX:** `ding2025modeling` — see [`refs.bib`](refs.bib).

---

# B4. Gender and age in real human conflict resolution through talk

### [Holley-DemandWithdraw]: Exploring the Basis for Gender Differences in the Demand-Withdraw Pattern
- **Authors / Year / Venue:** Sarah R. Holley, Virginia E. Sturm, Robert W. Levenson
  (University of California, Berkeley) / 2010 / *Journal of Homosexuality* 57(5),
  pp. 666–684.
- **Link:** doi:10.1080/00918361003712145 |
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3014221/
- **Peer-review status:** **published**, peer-reviewed journal. Authors, journal, volume,
  issue, pages and date confirmed from the **Crossref record** (`refs/cr_holley.json`).
- **Verified:** yes — full text read from the PMC author manuscript
  (`refs/b4_demand_withdraw.html`, extract `.txt`). Note this is the NIH author manuscript
  (NIHMSID NIHMS256891); page numbers differ from the journal version, so locators below are
  to **sections**, not pages.
- **Sub-area:** B4
- **Tags:** **`[foundational]`** (2010, pre-2016). **Justification:** the demand-withdraw
  pattern is *the* canonical, most-replicated gender finding in human conflict communication,
  and this paper is the decisive test of whether the pattern is caused by gender or by power
  — which is precisely the realism-versus-artifact distinction this whole issue exists to
  support. No post-2016 study located does the same job.
- **Demographic attributes studied:** **gender** (and, structurally, couple composition:
  heterosexual, gay, lesbian).
- **Data basis:** **experiment / observational coding.** 63 couples — heterosexual, gay and
  lesbian — at the Berkeley Psychophysiology Laboratory. Couples held three 15-minute
  conversations (events of the day, conflict, positive), each preceded by a five-minute
  silent period, video-recorded with partially hidden cameras; "[b]ecause demand-withdraw
  behaviors are most commonly manifest during times of conflict, we only utilized data from
  [the] conflict conversation" (Method).
- **Main finding (direction and size):**
  - **The gender pattern is real but is not caused by gender.** "The demand-withdraw pattern
    was seen regardless of type of couple. Further, for all couples, **differences in the
    amount of change desired in partners during a conflict interaction predicted differences
    in demand and withdraw behaviors**" (Abstract).
  - **Effect size of the real predictor:** relative desire for change explained
    **R² = 0.41, F(1, 61) = 41.67, p < .01** of demand-withdraw polarization (Results).
  - **Effect size of couple type:** entering sexuality group and its interaction added
    **R² change = .004** and did not contribute significantly (Results). Separating gay from
    lesbian couples changed nothing: "Sexuality group and the interaction between sexuality
    group and relative power were not significant predictors in any of these analyses"
    (Results).
  - **The null is a real null, not underpowered** — the authors do the arithmetic: average
    η² = .02 for the non-significant group differences, and to reach significance would have
    required "from 270 couples ... to 9,630 couples ... (across all reported findings of no
    group differences, the average number of couples needed would be 2,266). Taken together,
    it appears that the overall finding of no significant differences ... reflects an actual
    lack of differences between the groups rather than simply a lack of statistical power"
    (Results).
  - The authors' conclusion: "an oft-observed difference in heterosexual relationships may
    result from **social conventions that afford men greater power and women less power**"
    (Abstract).
- **Does it concern yielding, conceding, or conflict resolution specifically?** **Yes.**
  Withdrawing from a conflict discussion is a conceding/disengaging move, and demanding is a
  pressing move. This is the conversational analogue of who holds their ground.
- **Location and population studied:** United States (Berkeley, California). Note the
  recruitment gap the authors disclose: "the gay and lesbian couples in this study were
  recruited in the early 1990's, whereas the cross-sex couples were recruited more recently
  (2004–2005)".
- **Limitations stated by the authors:** the recruitment criteria differed between the
  cross-sex and same-sex samples (age difference between partners, presence of children),
  "because each of the two samples was originally recruited to match criteria used in other
  research studies"; the cohort gap above, with the note that "attitudes toward gay and
  lesbian relationships have changed significantly"; and a call to "replicate this study with
  samples matched on all recruitment variables". They defend the pooling on the grounds that
  the groups "were well-matched on key variables known to relate to relationship functioning
  (e.g. age, relationship satisfaction)" and that "identical laboratory methodologies were
  used".
- **Relevance to this FYP — this is the conceptual keystone of the whole review:**
  - It demonstrates, on real humans, that **a robust and genuinely observable gender
    difference in conflict behaviour can be entirely accounted for by a non-gender structural
    variable** (who wants change / who holds power). The gender difference is real in the
    aggregate *and* the wrong causal model.
  - [inference] This is the sharpest possible argument about `run01`. If an LLM has learned
    "women concede more" from text, it has learned a surface correlation whose real driver is
    situational power. Transplanted into a doorway conflict — where the power asymmetry is
    completely different (it is about urgency, speed and position, not domestic negotiating
    power) — the gender term should *not* carry over, and applying it anyway would be exactly
    the stereotype artifact the issue warns about. **This gives the FYP a principled,
    citable reason to prefer situational variables (urgency, hurry, crowding, relative speed)
    over demographic ones in the resolution pattern it extracts** — and it is an argument a
    supervisor can check, not a hand-wave.
  - It also supplies the design: the FYP's analogue of "study same-sex couples" is to hold
    the *situation* constant and vary only the demographic label, and vice versa. If the
    demographic effect survives when urgency is equalised, it is a model artifact.
- **BibTeX:** `holley2010exploring` — see [`refs.bib`](refs.bib).

---

### [Yeung-OlderWorkers]: Focus on Opportunities or Limitations? Their Effects on Older Workers' Conflict Management
- **Authors / Year / Venue:** Dannii Y. Yeung, Alvin K.-K. Ho (City University of Hong Kong)
  / 2020 / *Frontiers in Psychology* 11, article 571874, published 5 November 2020.
- **Link:** doi:10.3389/fpsyg.2020.571874
- **Peer-review status:** **published**, peer-reviewed open-access journal. Authors, journal,
  volume and date confirmed from the **Crossref record** (`refs/cr_frontiers_age.json`).
- **Verified:** yes — full text read (`refs/b4_frontiers_age.html`, extract `.txt`).
- **Sub-area:** B4
- **Tags:** none (2020)
- **Demographic attributes studied:** **age** (primary) and **gender** (tested, null — see
  below).
- **Data basis:** **two survey studies.** Study 1: "416 Hong Kong Chinese participants ...
  57.7% were females and their age ranged between 20 and 68 years (M = 39.13; SD = 12.42)",
  recruited via a university alumni mailing list and campus flyers, paid HKD50; habitual use
  of the five conflict strategies measured with the **Chinese version of the Rahim
  Organizational Conflict Inventory-II (ROCI-II)**, 28 items, 5-point Likert (Study 1
  Participants / Measures). Study 2: "268 managerial employees and professionals were asked
  to recall a real-life workplace conflict that happened in the past six months and their use
  of the five conflict strategies in this incident" (Abstract).
- **Main finding (direction and size):** ⚠ **the zero-order and the mediated results point in
  opposite directions, and only the mediated ones are in the abstract.** Both are recorded
  here.
  - **Zero-order (Study 1):** "**age was negatively correlated with obliging (r = −0.18;
    p < 0.001) and avoiding (r = −0.12; p = 0.015)**" (Results). That is: in this sample, the
    *older* workers reported *less* obliging and *less* avoiding — less conceding, not more.
  - **Mediated:** "a significant negative indirect effect of age existed on all five
    strategies through focus on opportunities" and "[a] significant positive indirect effect
    of age on obliging ... and avoiding ... through focus on limitations" (Results; Abstract).
    So once occupational future time perspective is split into its two components, the path
    through *perceived limitations* runs the other way.
  - The authors' summary: "older employees reported increased perceived limitations than
    their younger counterparts, which was consequently related to their **greater use of
    obliging and avoiding**" (Discussion), and "aging workers' increased perception of
    limitations make them utilize **less constructive strategies** when facing conflict at
    work" (Abstract).
  - A prediction that failed: "In contrast to the predicted negative indirect effect, the
    present study found a **positive** indirect effect of age on dominating through focus on
    limitations. As a result, H2 was partly supported" (Results).
  - **The gender result — a clean null:** "**Gender was not correlated with the two OFTP
    dimensions or the five conflict strategies, thus it was excluded from the following
    analyses**" (Study 1, Results). In a 416-person Hong Kong Chinese sample, sex predicted
    none of the five Rahim conflict styles.
- **Does it concern yielding, conceding, or conflict resolution specifically?** **Yes.**
  "Obliging" in the Rahim taxonomy is conceding, and "avoiding" is disengaging. The paper
  groups these as "passive strategies", against "constructive" (integrating, compromising)
  and "destructive" (dominating) (Introduction).
- **Location and population studied:** **Hong Kong Chinese workers** — the closest cultural
  match to Singapore of any paper in this review, and the reason it is weighted heavily here.
- **Limitations stated by the authors:** `[needs verification against full text]` — I read
  the abstract, introduction, both studies' methods and results, and the discussion of the
  age findings; I did **not** separately transcribe the limitations section. Evident
  constraints: both studies are **self-report**, Study 2 is **retrospective recall**, the
  sample is university-connected and highly educated ("64.9% completed a bachelor's degree or
  higher"), and the design is **cross-sectional**, so "age" is confounded with cohort.
- **Relevance to this FYP:**
  - **Connects directly to the Rahim taxonomy already collected in this repo** (`rahim1983`,
    `rahim1995`, `weiderhatfield1988` in
    `literature/human-conflict-resolution/refs.bib`) — which is what the issue asked B4 to do
    — and adds the age and gender dimension those entries lack.
  - **The null gender result is a genuinely important data point for `run01`.** The strongest
    single pattern in `run01` is a gender effect on yielding. Here, in an Asian sample, using
    the standard instrument, **gender predicts no conflict style at all**. That does not prove
    `run01` is wrong — a stated yield-likelihood in a street scenario is not a self-reported
    workplace conflict style — but it means the LLM's confident gender effect has no support
    from the nearest available human measurement.
  - **The age result is genuinely mixed and should be reported as mixed.** Quoting only the
    abstract would suggest "older people concede more"; the zero-order correlations in the
    same paper say the opposite. [inference] A supervisor-facing summary should say: *in the
    nearest cultural setting, age has no simple relationship with conceding; the direction
    depends on which psychological mechanism is controlled for.* That is a much weaker claim
    than `run01`'s age ordering assumes.
  - Cross-sectional design means the "age" effect may be a cohort effect — a caveat that
    applies equally to any age persona an LLM has learned from text written at one point in
    time.
- **BibTeX:** `yeung2020focus` — see [`refs.bib`](refs.bib).

---

### [Filsecker-ROCI]: The structure of conflict styles in adolescents: Psychometric properties of the Adapted Rahim Organizational Conflict Style Inventory-II (ROCI-II)
- **Authors / Year / Venue:** Michael Filsecker, Hermann Josef Abs, Nina Roczen / 2020 /
  *European Journal of Psychological Assessment* 36(4), pp. 525–536.
- **Link:** doi:10.1027/1015-5759/a000527 | open copy: doi:10.25656/01:23783 |
  https://www.pedocs.de/volltexte/2022/23783/
- **Peer-review status:** **published**, peer-reviewed journal (Hogrefe).
- **Verified:** yes — full text read (`refs/b4_filsecker_roci.pdf`). ⚠ **This is the accepted
  manuscript, not the version of record.** The PDF states so itself: "This version of the
  article may not completely replicate the final version published in the journal. It is not
  the version of record and is therefore not suitable for citation." Licence CC BY-NC.
  **Cite the journal DOI; locators here are to the accepted manuscript.** Note also that the
  peDOCS cover page gives the pages as 526–536 while the article's own citation line gives
  525–536; the Hogrefe record should be checked before the page range is used
  `[needs verification against full text]`.
- **Sub-area:** B4
- **Tags:** none (2020)
- **Demographic attributes studied:** **gender** (boys / girls) and, partially, **school
  grade** as a narrow age proxy (grades 8, 9, 10).
- **Data basis:** **survey, psychometric.** "The sample consisted of **4112 students from 65
  schools** who participated in the pilot project 'Living and Learning Democracy' ... In each
  school the questionnaires were completed by a blind selection of up to four classes drawn
  from grades 8, 9, and 10, making a total of 176 classes ... The median age of participants
  was **15 years (M = 15.05, SD = 1.13) and 51% were girls**" (Method). Split into four
  sub-samples for EFA, E/CFA and CFA replication; invariance tested on Sample 4
  (n = 1006; boys 464, girls 534).
- **Main finding (direction and size):**
  - **Gender invariance holds at all three levels.** "The two-group CFA, testing **configural
    invariance**, fit the data well. Next we examined the metric equivalence of the ROCI-II.
    The analysis indicated that the **factor loadings were invariant for boys and girls** ...
    In the next model residual covariances were constrained to equality; this also produced
    evidence for the **measurement invariance of the ROCI-II across gender**" (Results;
    Tables 4–5).
  - **Age/grade invariance does *not* hold.** "Concerning school grades, **it was not possible
    to specify a baseline model for the 9th graders. Therefore invariance was not possible to
    be established across grades.** Nevertheless we explore the invariance between grades 8
    and 10 and it was possible to obtain evidence of equivalence of the measurement model
    across these two specific grades" (Results).
  - The authors' motivation includes that in the original Rahim work "**no measurement
    invariance between males and females was explored**" and "no sample data from adolescents
    was used" (Introduction) — i.e. the standard instrument's cross-gender comparability was
    untested until this paper.
- **Does it concern yielding, conceding, or conflict resolution specifically?** **Indirectly.**
  The instrument measures the five Rahim styles, which include obliging (conceding) and
  avoiding — but **this paper reports no gender or grade differences in style use.** It
  establishes only whether such comparisons *would be valid*.
- **Location and population studied:** Germany; adolescents, median age 15.
- **Limitations stated by the authors:** `[needs verification against full text]` — I read the
  introduction, method and the invariance results, and did not transcribe a limitations
  section. Evident constraints: the age range is extremely narrow (grades 8–10, roughly ages
  14–16), so this says nothing about adult or elderly age differences; the sample is a single
  German school-reform pilot; and the version read is the accepted manuscript.
- **⚠ Qualification against the issue's selection criterion.** The issue requires "an
  empirical result on how gender or age changes **behaviour or outcomes**". Strictly, this
  paper reports a **psychometric** result — that the instrument behaves equivalently across
  gender — not a behavioural difference. It is included because the issue named it as a seed
  and framed it correctly ("Invariance is a prerequisite for any valid claim that genders
  differ in conflict style"), and it earns its place as a methodological gatekeeper rather
  than as evidence of a gender effect.
- **Relevance to this FYP:**
  - It **licenses the comparison** that [Yeung-OlderWorkers] makes and that the FYP would
    need: because the ROCI-II is gender-invariant, a finding that men and women score
    differently can be read as a real difference rather than as the instrument behaving
    differently.
  - **It withholds the same licence for age.** Invariance could not be established across
    grades 8–10 — a span of roughly two years. [inference] If a standard conflict-style
    instrument cannot be shown to measure the same construct across two adjacent school
    years, then comparing conflict styles across `run01`'s far wider bands (`child`,
    `teenager`, `young_adult`, `middle_aged`, `elderly`) is on much weaker measurement
    footing than comparing across gender. This is an independent, purely methodological reason
    — separate from all the LLM-side evidence in
    [`llm-demographic-effects.md`](llm-demographic-effects.md) — to treat the FYP's age
    dimension more cautiously than its gender dimension.
  - Its adolescent sample is a partial match for `run01`'s `teenager` band — the band that
    shows the *largest* flagged gender gaps in
    `dataset/generated/validation_report.md` (Δ = −0.27 to −0.43 across many scenarios).
    There is no human evidence in this paper for or against those gaps.
- **BibTeX:** `filsecker2020structure` — see [`refs.bib`](refs.bib).

---

## Identified but not obtained

**Holt, J. L. & DeVore, C. J. (2005). "Culture, gender, organizational role, and styles of
conflict resolution: A meta-analysis." *International Journal of Intercultural Relations*
29(2), pp. 165–196. doi:10.1016/j.ijintrel.2005.06.002.**

Bibliographic fields confirmed from the **Crossref record** (`refs/cr_holt_devore.json`) —
so the paper is confirmed to exist, with those authors, in that journal, at those pages.
**But I could not open it, and it is therefore not entered as a B4 source.** Crossref carries
no abstract; Semantic Scholar reports the abstract "elided by the publisher"; Unpaywall
reports `is_oa: false` with no open location; ScienceDirect is blocked to me. Copies circulate
on academia.edu and ResearchGate, which are not authoritative sources for verifying a
citation.

This is the canonical meta-analysis of gender and conflict style (reportedly 36 studies of
organization members), and it is the **single most valuable missing piece in B4**. It is
recorded here rather than summarised from search results, because the issue's sourcing rules
forbid reporting findings that I have not read on the page. **Recommended action: obtain it
through the university library and add a Template H entry.** See
[`search-log.md`](search-log.md).

---

## Cross-cutting observations (B3 + B4)

My synthesis, not any single paper's claim. Inferences are marked.

1. **The best-measured human demographic effects in pedestrian behaviour are physical, not
   attitudinal.** Shoulder width driving body rotation ([Yamamoto-BodyRotation] §8.2); walking
   speed driving evacuation time ([Zhu-MultiAttribute] §2.4.2, §4; [Minegishi-SlowPedestrians]
   Abstract); visuomotor decline driving risky clearances ([Rapos-CollisionAvoidance]
   Results). **Nothing measured in B3 shows anyone yielding out of deference to a
   demographic.**
2. **Where real pedestrians were actually measured, the young yield to the old.**
   [Rapos-CollisionAvoidance] (Results) finds the young adult contributing more to avoidance
   when meeting an older adult; [Ding-AsymmetricCompetitiveness] (§3.3) encodes the same
   direction as a modelling convention. `run01` produces the opposite ordering.
3. **In the nearest cultural setting, gender predicts no conflict style at all.**
   [Yeung-OlderWorkers] (Results) finds gender uncorrelated with all five Rahim strategies in
   416 Hong Kong Chinese workers.
4. **The canonical human gender difference in conflict talk is not caused by gender.**
   [Holley-DemandWithdraw] (Results): relative desire for change explains R² = 0.41; couple
   gender composition adds R² = .004.
5. **Age comparisons rest on weaker measurement foundations than gender comparisons.** The
   standard instrument is gender-invariant but could not be shown grade-invariant across two
   adjacent school years ([Filsecker-ROCI] Results). [inference] Combined with observation 2
   in [`llm-demographic-effects.md`](llm-demographic-effects.md), *both* the human-measurement
   side and the LLM side independently say age is the shakier of the two variables — while the
   `run01` dataset is organised primarily by age band.
