# Topic 2 — Sociological / real-human conflict-resolution research

Prepared for issue [#8](https://github.com/M450NCH00/CrowdSimulation/issues/8).
Companion file: [`topic1-llm-conflict.md`](topic1-llm-conflict.md).
Queries, sources, rejections and dead ends: [`search-log.md`](search-log.md).

This topic supports the validation half of the project:

> *If LLM-to-LLM exchanges produce a resolution pattern, does that pattern match how
> real humans resolve the same conflict?*

Verification conventions are the same as Topic 1: every field confirmed from a primary
source, caches in [`../../refs/`](../../refs/), bibliographic fields cross-checked
against Crossref, `[unverified]` on anything not confirmed, `[non-archival]` on preprints.

---

## ⚠ DATASET FOUND — this changes the validation plan

The issue asked for any real-world human conflict-resolution dataset to be flagged
prominently. **Two exist, both openly licensed, and one is directly usable.**

### 1. Jülich Pedestrian Dynamics Data Archive — the primary find

- **URL:** https://ped.fz-juelich.de/database/ · **DOI:** `10.34735/ped.da`
- **Maintainer:** Institute for Advanced Simulation 7: Civil Safety Research,
  Forschungszentrum Jülich, Germany
- **Licence:** **CC-BY 4.0** — free to use "as long as you name the source of the data"
- **Contents:** video recordings *and* extracted individual trajectories from controlled
  laboratory experiments, including **unidirectional and bidirectional corridor flow**,
  **bottlenecks** (single and group), **90° and 120° crossing**, single-file motion,
  stairs, social groups, wheelchair users and age effects. Some experiments add motion
  capture, pressure sensors, heart-rate and questionnaires. Trajectories extracted with
  the group's own PeTrack software. Individual experiments carry their own DOIs
  (`10.34735/ped.2005.1` … `10.34735/ped.2022.7`).
- **Verified:** yes — opened the archive's database page (cached
  `refs/juelich_ped_data_archive.html`); the accompanying peer-reviewed data paper is
  [Boomers-DataGuidance] below.

**Why this matters.** The project's validation step (roadmap 5) was written assuming
real behavioural data probably would not be available and sociological literature would
have to stand in. That assumption is wrong. **Bidirectional corridor and bottleneck
trajectories of real people are public, free, and already in the exact geometry of the
planned 2-agent hallway scenario.** Validation can therefore be quantitative — compare
who yields, when, and by how much — rather than argued by analogy to sociology.

**Caveat, stated honestly:** these are *crowd-flow* experiments. Most runs involve many
participants, so isolating clean **two-person** head-on encounters will require filtering
the trajectories for sparse moments, and it is not yet confirmed how many such encounters
the archive contains. [Yamamoto-BodyRot] below is the complementary find: a controlled
experiment built specifically on **two** pedestrians passing in a narrow corridor.

### 2. Echeverría-Huarte et al. — raw trajectories on Zenodo

Deposited at **`10.5281/zenodo.19592341`**, containing "the raw trajectories of all
participants across all experiments" from five studies in Spain and Japan
(see [Echeverria-CCW] below). Useful for side-preference / tie-breaking baselines rather
than head-on conflict specifically.

**Recommendation (for supervisor sign-off, not a decision I am making):** roadmap step 5
should be rewritten around the Jülich archive as the ground truth, with sociological
literature used to *interpret* the pattern rather than to substitute for data.

---

## Summary table

| # | Handle | Year | Venue | Peer-reviewed | Rel. |
|---|--------|------|-------|---------------|------|
| S1 | Wang — Congestion Evacuation with Panic *(supervisor-assigned)* | 2015 | *Physica A* | yes | 3 |
| 1 | Moeller — Transparent Decision Game | 2023 | *eLife* | yes | **5** |
| 2 | Yamamoto — Body-Rotation in Passing | 2019 | *Transp. Res. B* | yes | **5** |
| 3 | Boomers — Crowd Management Data Guidance | 2023 | *Collective Dynamics* | yes | **5** |
| 4 | Echeverría-Huarte — Locomotor Bias | 2026 | *Nature Communications* | yes | 4 |
| 5 | Terwilliger — Invisible Walls | 2026 | arXiv `[non-archival]` | no | 3 |

Five entries beyond the supervisor-assigned one; four are peer-reviewed. Combined with
Topic 1's seven, the review reports **12 papers within 2016–2026**, against the issue's
target of 10.

Note the 2015 anchor is counted separately, as the issue requires.

---

### [Wang-Panic] — Modeling and simulating for congestion pedestrian evacuation with panic

> **Supervisor-assigned.** Published 2015, deliberately outside the 2016–2026 window,
> and per the issue it does **not** count toward the 10-paper target.

**Authors / Year / Venue:** Jinhuan Wang, Lei Zhang, Qiongyu Shi, Peng Yang, Xiaoming Hu /
2015 / *Physica A: Statistical Mechanics and its Applications* 428:396–409.

**Link:** doi:10.1016/j.physa.2015.01.057

**Verified:** yes — opened the RePEc bibliographic record (cached
`refs/wang2015_congestion_panic_repec.html`); title, full author list, journal, volume,
pages and DOI cross-checked against Crossref. ScienceDirect itself refuses automated
fetches (see `search-log.md`), so the abstract was read from the RePEc record.

**Topic:** 2 (with a foot in crowd modelling rather than behavioural science)

**Problem:** How does panic change the dynamics of a crowd evacuating a congested venue
such as a stadium, and what interventions reduce casualties?

**Method:** A **multi-agent** congestion evacuation model incorporating panic behaviour.
Pedestrians are divided into four classes, each carrying a status of *normal*,
*being overtaken*, or *casualty*. Each individual's direction of movement is determined
by three factors: **competitive ability**, **distance to exits**, and the **number and
density of occupants within the agent's view field**.

**Results that matter:**
- Agents spontaneously cluster into **arch formations** at exits — the classic
  congestion signature.
- **Panicked individuals fixate on one exit and ignore alternatives.**
- **Obstacles reduce casualties** by relieving congestion.
- **Virtual leaders improve efficiency** when exits are partly blocked.
- The authors claim the model "can reproduce the real evacuation process in a stadium
  quite well." No quantitative validation figure was confirmable from the abstract —
  `[unverified]`.

**Limitations / criticisms:** It is a simulation model validated qualitatively against
known phenomena, not a study of human participants, so it is evidence about *models* of
behaviour rather than about behaviour. "Competitive ability" is an assigned parameter,
not a measured trait. By the issue's own scope rules this sits close to the excluded
category of crowd-physics work — it is included because the supervisor assigned it and
because it is the direct ancestor of Wu et al.'s evacuation setup.

**Relevance to this FYP (3):** Its real value is as the **bridge between the two
supervisor papers**: Wu et al. §6.1 builds its LLM evacuation case study on this model,
so it defines the state variables the LLM agents were given (distance to exits,
congestion in view). Two of its findings transfer to the hallway scenario as testable
expectations: that **exit fixation under panic** is the failure mode communication is
supposed to fix, and that **competitive ability** — an asymmetry between agents — is what
breaks the symmetry of a standoff. That asymmetry is the classical-model analogue of
GameChat's LLM-negotiated priority.

**BibTeX:** `wang2015modeling` in [`refs.bib`](refs.bib).

---

### [Moeller-Transparent] — Human and macaque pairs employ different coordination strategies in a transparent decision game

**Authors / Year / Venue:** Sebastian Moeller, Anton M. Unakafov, Julia Fischer,
Alexander Gail, Stefan Treue, Igor Kagan / 2023 / *eLife* 12:e81641.

**Link:** doi:10.7554/eLife.81641 | https://elifesciences.org/articles/81641

**Verified:** yes — opened the eLife article page (cached
`refs/moeller2023_transparent_game.html`); fields cross-checked against Crossref.

**Topic:** 2

**Problem:** When two individuals face a conflict about *which* of two mutually-preferred
options to coordinate on — each preferring a different one — how do real humans resolve
it, and do they resolve it fairly?

**Method:** Two agents sit **face to face at a shared transparent touchscreen**, so each
can see the other's hand moving in real time ("transparent games"). They play a
transparent version of **Bach-or-Stravinsky**, a coordination game that "entails a
conflict about which of two individually-preferred opposing options to choose to achieve
coordination" — structurally the same problem as two people meeting head-on with opposite
preferred sides. **19 human pairs (38 participants, 23 female, mean age 26.1)**, 300–400
trials each, after 100 solo trials to establish each participant's own preference.
Nine macaque pairs were run for comparison.

**Results that matter:**
- **Turn-taking is the dominant human resolution.** **53% (10 of 19 pairs)** converged on
  fair, balanced turn-taking, with the "fraction of choosing own" near 0.5 — i.e. they
  alternated who got their preferred option, equalising payoffs over time.
- **26% (5 pairs)** instead settled on a **fixed** assignment favouring one agent, and
  **21% (4 pairs)** failed to coordinate. So a stable resolution emerged in ~79% of pairs,
  by one of exactly **two** mechanisms: alternate, or defer permanently.
- **Understanding predicts strategy:** turn-takers understood the payoff structure far
  better than non-turn-takers (**70% vs 6%**, p<0.00005).
- **Human turn-taking was prosocial and symmetric**: humans "equally often initiated
  switches to and from their preferred option." Macaques never turn-took spontaneously;
  the two that learned it after training with a human confederate did so *competitively*
  — the faster agent simply took its own preference.
- Timing carries the coordination: following behaviour correlated strongly with the
  visibility of the partner's action before one's own move (r=0.64–0.92, p<0.001 in the
  trained macaque pair).

**Limitations / criticisms:** Abstract and screen-based, not spatial — there is no
physical cost to yielding and no walking involved, so the transfer to a hallway is by
structural analogy. Only 19 human pairs, and the 53%/26%/21% split is therefore based on
10/5/4 pairs — small counts for a three-way categorisation. Data availability statement
`[unverified]` (not found in the article content retrieved).

**Relevance to this FYP (5):** This is **the** sociological grounding paper for the
project, because it answers the precise question the LLM experiment will ask. For a
symmetric two-party conflict over an indivisible good, real humans resolve it by
**turn-taking (alternation) about half the time and by a fixed priority the rest of the
time** — and those are exactly the two candidate patterns an LLM hallway exchange could
produce. It therefore gives the project a **pre-registered prediction**: if the LLM
agents converge on a single fixed rule ("the one on the right always goes"), that is
*less* humanlike than a mixture in which roughly half of pairs alternate. It also supplies
the mechanism that makes alternation possible — mutual visibility of the partner's action
timing — which is what the LLM dialogue channel stands in for. Note the contrast with
[Mahadevan-GameChat], whose agents reached the "correct" priority 100% of the time:
humans do not do that, and 100% consistency should itself be treated as a validation
failure signal.

**BibTeX:** `moeller2023human` in [`refs.bib`](refs.bib).

---

### [Yamamoto-BodyRot] — Body-rotation behavior of pedestrians for collision avoidance in passing and cross flow

**Authors / Year / Venue:** Hiroki Yamamoto, Daichi Yanagisawa, Claudio Feliciani,
Katsuhiro Nishinari / 2019 / *Transportation Research Part B: Methodological*
122:486–510.

**Link:** doi:10.1016/j.trb.2019.03.008 | preprint arXiv:1903.07742

**Verified:** yes — opened the arXiv abstract page (cached
`refs/yamamoto2019_body_rotation_abs.html`); journal, volume, pages and full author list
cross-checked against Crossref.

**Topic:** 2

**Problem:** How do two pedestrians physically resolve a head-on encounter when the
corridor is too narrow for both, and can that be modelled geometrically?

**Method:** Controlled experiments in which **two pedestrians pass each other** in a
narrow corridor — which the authors argue is the most fundamental case for studying this,
since it is the minimal interaction. Body rotation (the angle between body orientation
and walking direction) is measured. The work then extends to **cross flow**, and develops
an **ellipse-based geometric model** plus a simulation reproducing the observed deviation
between body orientation and direction of travel. The paper runs 40 pages with 21 figures
and 4 tables.

**Results that matter:**
- **Body rotation is triggered by a width threshold:** rotation occurs when the corridor
  width is **smaller than the combined widths of the two pedestrians** — a sharp,
  geometric switching condition rather than a gradual response.
- The ellipse model explains the observed rotation, and the simulation reproduces the
  experimentally observed orientation/direction deviation.
- Exact participant counts, corridor dimensions and rotation angles are `[unverified]` —
  the abstract does not state them and the full text was not obtained.

**Limitations / criticisms:** This is about the *physical* resolution (how bodies fit
past each other), not the *decision* (who concedes the centreline). Laboratory setting
with instructed passing, so the social component is thin. It sits nearer the crowd-physics
boundary the issue asks to avoid — it earns inclusion because of the two-person
narrow-corridor geometry, which is the FYP's exact scenario and is otherwise almost
unstudied in isolation.

**Relevance to this FYP (5):** It supplies the **scenario parameters**, which the project
otherwise has to invent. The width threshold — corridor narrower than the sum of two
shoulder widths — is a principled, citable definition of "the hallway is too narrow for
both," and it connects directly to fields already in the CrowdGym mapping
(`Radius side`, derived from `personas.yaml` shoulder widths; see
`integration/crowdgym_mapping.md` §A, and the passage-width trigger in §B). It also marks
the boundary of what the LLM should decide: below that threshold the conflict is real and
needs a priority decision; above it, body rotation resolves it with no negotiation at all.
Same research group as [Echeverria-CCW].

**BibTeX:** `yamamoto2019body` in [`refs.bib`](refs.bib).

---

### [Boomers-DataGuidance] — Pedestrian Crowd Management Experiments: A Data Guidance Paper

**Authors / Year / Venue:** Ann Katrin Boomers, Maik Boltes, Juliane Adrian,
Mira Beermann, Mohcine Chraibi, Sina Feldmann, Frank Fiedrich, Niklas Frings, Arne Graf,
Alica Kandler, Deniz Kilic, Krisztina Konya, Mira Küpper, Andreas Lotter, Helena Lügering,
Francesca Müller, Sarah Paetzke, Anna-Katharina Raytarowski, Olga Sablik, Tobias Schrödter,
Armin Seyfried, Anna Sieben, Ezel Üsten / 2023 / *Collective Dynamics*.

**Link:** doi:10.17815/cd.2023.141 | preprint arXiv:2303.02319

**Verified:** yes — opened the arXiv abstract page (cached
`refs/boomers2023_data_guidance_abs.html`). **Correction worth noting:** the arXiv page still says "under review for Collective Dynamics," but Semantic
Scholar shows it **published** with DOI `10.17815/cd.2023.141`
(`refs/s2_topic_metadata.json`). Cite it as published, not as a preprint.

**Topic:** 2 — included primarily as the **citable reference for the dataset flagged at
the top of this file**.

**Problem:** Making large-scale pedestrian experiment data reusable: documenting what was
run, under what conditions, and how to interpret the released trajectories.

**Method:** Documents **seven experiment series** — Train Platform, Crowd Management,
Single-File, Personal Space, Boarding and Alighting, Bottleneck, and Tiny Box —
conducted with **approximately 1,000 participants**. Experiments are run under laboratory
conditions specifically so that a single variable can be isolated. All data is deposited
in the Jülich Pedestrian Dynamics Data Archive under **CC-BY 4.0**.

**Results that matter:** It is a data paper, so the "result" is the corpus itself. The
directly relevant series for this project are **Personal Space** (interpersonal distance
norms), **Bottleneck** (competition for a constrained opening) and **Single-File**
(ordering in a passage too narrow to overtake).

**Limitations / criticisms:** No behavioural hypothesis is tested — by design. The
experiments are instructed laboratory tasks, so yielding behaviour observed in them is
not fully spontaneous. Most series are many-participant crowd flows rather than isolated
dyads, which is the filtering caveat noted in the dataset flag above.

**Relevance to this FYP (5):** High for practical rather than theoretical reasons: it is
the reference that makes the dataset usable and citable, it documents licensing and
experimental conditions (needed to justify comparisons in the report), and it identifies
which experiment series to pull. It converts roadmap step 5 from "argue by analogy to
sociology" into "measure against trajectories."

**BibTeX:** `boomers2023pedestrian` in [`refs.bib`](refs.bib).

---

### [Echeverria-CCW] — Individual locomotor bias drives counterclockwise motion in pedestrian crowds

**Authors / Year / Venue:** Iñaki Echeverría-Huarte, Claudio Feliciani, Zhigang Shi,
Katsuhiro Nishinari, Angel Sánchez, Angel Garcimartín, Iker Zuriguel / 2026 /
*Nature Communications* 17:4869.

**Link:** doi:10.1038/s41467-026-73713-w

**Verified:** yes — opened the PMC full-text record (cached
`refs/echeverria2026_locomotor_bias.html`); fields cross-checked against Crossref.
(nature.com itself redirects to an authentication endpoint — see `search-log.md`.)

**Topic:** 2

**Problem:** When pedestrians roam freely in a shared space, a collective
counterclockwise rotation appears. Is that an emergent product of social interaction, or
of something individual?

**Method:** **Five experimental studies across Spain and Japan**: a confined arena in
Spain (50 participants, 23M/27F, mean age 25.7), a Spanish schoolyard (107 teenagers aged
13–14), a confined arena in Japan (39 participants, 25M/14F, mean age 26.8), a Japanese
nursery (children ~5 years old), and an individual-motion study (209 participants,
88M/121F). Overhead cameras tracked trajectories; participants were classified as
left- or right-turners and rotational bias measured via a polarization parameter.

**Results that matter:**
- **The counterclockwise bias is robust and reproducible** across countries, ages and
  densities (collective polarization M̄ ≈ 0.2; individual polarization peaking near
  m̄ᵢ ≈ 1; z = −5.63, n = 156, P < 0.001, |r| = 0.45).
- **It originates from individual tendency, not interaction** — the headline claim,
  which the authors say "challenge[s] the traditional view that social dynamics shape
  pedestrian motion."
- **It is not laterality.** The effect persisted regardless of handedness, footedness or
  eye dominance, and appeared even when 100% of participants were right-turners or
  left-handed.
- **Data availability:** raw trajectories for all experiments deposited at Zenodo
  `10.5281/zenodo.19592341`.

**Limitations / criticisms:** Free roaming, not conflict resolution — there is no
contested resource, so it is background behaviour rather than negotiation. The claim that
bias is individual rather than social is strong and contests an established position; it
should be cited as the authors' well-evidenced claim, not as settled consensus.

**Relevance to this FYP (4):** Two concrete uses. First, it is evidence for a **default
tie-breaker that requires no communication at all**: a stable individual-level directional
bias. If two LLM agents in a hallway resolve their standoff by both drifting to a
consistent side, that is a humanlike outcome with an identified mechanism — and it is a
*cheaper* pattern to implement in CrowdGym than any negotiated priority. Second, it is a
warning against over-attributing outcomes to the LLM dialogue: this paper's whole point is
that a population-level regularity can come from individual bias rather than interaction,
so the project must test whether its pattern survives when communication is removed —
which is precisely the ablation Wu et al. ran.

**BibTeX:** `echeverriahuarte2026individual` in [`refs.bib`](refs.bib).

---

### [Terwilliger-InvisibleWalls] — Invisible walls: how pedestrians navigate around social interactions

**Authors / Year / Venue:** Jack Terwilliger, Julia Di Silvestri, Seika Murase,
Anne Elizabeth Clark White, Federico Rossano / 2026 / arXiv:2607.20876 `[non-archival]`.

**Link:** https://arxiv.org/abs/2607.20876

**Verified:** yes — opened the arXiv abstract page (cached
`refs/terwilliger2026_invisible_walls_abs.html`). No peer-reviewed venue found; treated
as a preprint.

**Topic:** 2

**Problem:** Conversations between people create a spatial territory with no physical
marker. How do passing pedestrians infer that boundary, and when do they violate it?

**Method:** **Four field experiments with 4,911 participants** — observational, in real
shared spaces rather than a laboratory. The study examines which cues pedestrians use
when deciding whether to walk through the space between people who may be interacting:
**gaze, proximity, body orientation, and talk**.

**Results that matter:**
- Pedestrians integrate **gaze, interpersonal distance, body orientation and speech** to
  infer whether an interaction is in progress, and route around it.
- **Norm violation is contagious:** "pedestrians also collectively violate these spatial
  norms by walking through an interaction if other pedestrians had already done so."
  Observing a breach makes further breaches more likely.
- Exact effect sizes per cue are `[unverified]` — not stated in the abstract.

**Limitations / criticisms:** A preprint, not peer-reviewed, and it is about *avoiding*
a social territory rather than *resolving a standoff*, so the mechanism transfers only
partially. Field observation gives realism but weaker control over confounds than the
laboratory studies above. Large N (4,911) reflects observations in public space rather
than recruited, consenting experimental subjects — worth noting if the report leans on it.

**Relevance to this FYP (3):** Modest and specific. It is the best available evidence
that **spatial right-of-way in humans is governed by inferred social norms, not by
geometry alone** — which is the underlying justification for using an LLM (a model of
social convention) rather than a purely geometric controller for conflict resolution. The
contagion result is also a caution for the CrowdGym integration: if a yielding rule is
applied uniformly to all 10,000 agents, the simulation will miss the real
observation-driven variability that this paper documents. Included at relevance 3 rather
than higher because of the preprint status and the indirect mechanism; it is not the sole
support for any claim in this review.

**BibTeX:** `terwilliger2026invisible` in [`refs.bib`](refs.bib).

---

## What this topic adds up to

**The human answer to a symmetric two-party spatial conflict is known, and it is not a
single rule.** [Moeller-Transparent] shows real pairs resolving an indivisible-good
conflict by **turn-taking about half the time (53%)** and by **fixed deference about a
quarter of the time (26%)**, with the rest failing to coordinate. That distribution — not
any one rule — is the target an LLM-derived pattern should be compared against.

Three further ingredients for the comparison:

- **A trigger condition:** conflict is real only when the corridor is narrower than the
  two pedestrians' combined width ([Yamamoto-BodyRot]); above that, geometry resolves it.
- **A no-communication baseline:** stable individual directional bias can produce
  coordinated outcomes with no negotiation at all ([Echeverria-CCW]), so the LLM dialogue
  must be shown to beat that baseline.
- **A norms caveat:** human spatial right-of-way follows inferred social norms and is
  contagious rather than uniform ([Terwilliger-InvisibleWalls]).

And, unexpectedly, **the data to do this quantitatively already exists** — see the
dataset flag at the top of this file.
