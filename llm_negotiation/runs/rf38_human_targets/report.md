# Round 1 in head-on pairs with one cane user, against the human targets (issue #124, RF-38)

Targets: `configs/human_targets/head_on_v1.yaml` (sha256 `7b732845fd93`). Method: `docs/human-targets.md`. No model call, USD 0.

**Tolerances** (the user's decision of 2026-10-30, fixed before any rule was measured): a value target is met
within one reported SD of the study's mean; a target with no reported spread is judged on its direction, by the
exact two-sided sign test at 0.05; two studies that disagree are shown with no verdict.

**Every comparison marked `[setting differs]` is in a setting unlike the study's** (each target's `differs` in the
targets file says how). The verdicts are about the simulation against the study's numbers, not proof about people.

## Subjects

| Subject | Head-on pairs | Pairs at three speeds | Crowd runs | Note |
| --- | --- | --- | --- | --- |
| plain | 30 | 0 | 0 |  |
| passed_screening | 30 | 0 | 0 |  |
| cane_rule_alone | 30 | 0 | 0 |  |
| all_runnable | 30 | 0 | 0 |  |
| reference_default | 30 | 0 | 0 |  |
| step1_independent | 20 | 0 | 0 | 20 of 40 sessions with exactly one person at mobility_aid cane resolved by the plans alone |
| step1_non_verbal | 27 | 0 | 0 | 27 of 40 sessions with exactly one person at mobility_aid cane resolved by the plans alone |
| step1_talk | 16 | 0 | 0 | 16 of 40 sessions with exactly one person at mobility_aid cane resolved by the plans alone |

## Verdicts

| Target | plain | passed_screening | cane_rule_alone | all_runnable | reference_default | step1_independent | step1_non_verbal | step1_talk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 [setting differs] | not comparable | not comparable | not comparable | not comparable | not comparable | within: 0.8926 (n 9) | within: 0.9947 (n 15) | within: 0.8805 (n 9) |
| H2 [setting differs] | outside: 0.51 (n 27) | outside: 1.2504 (n 27) | outside: 0.5043 (n 27) | outside: 0.5043 (n 27) | outside: 0.506 (n 27) | within: 0.9303 (n 11) | outside: 0.9776 (n 12) | within: 0.8386 (n 7) |
| H3 [setting differs] | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable |
| H4 [setting differs] | 0.2491 m/s; 1.0 slow | 0.0199 m/s; 0.0 slow | 0.414 m/s; 1.0 slow | 0.414 m/s; 1.0 slow | 0.1364 m/s; 0.25 slow | 0.3445 m/s; 0.75 slow | 0.283 m/s; 0.7037 slow | 0.2525 m/s; 0.7188 slow |
| H5 | 0.2491 m/s; 1.0 slow | 0.0199 m/s; 0.0 slow | 0.414 m/s; 1.0 slow | 0.414 m/s; 1.0 slow | 0.1364 m/s; 0.25 slow | 0.3445 m/s; 0.75 slow | 0.283 m/s; 0.7037 slow | 0.2525 m/s; 0.7188 slow |
| H6 [setting differs] | not comparable | not comparable | agrees: 13 to 0, p 0.000244 | agrees: 13 to 0, p 0.000244 | not comparable | not shown: 8 to 3, p 0.227 | agrees: 9 to 1, p 0.0215 | not shown: 5 to 1, p 0.219 |
| H7 [setting differs] | not comparable | not comparable | opposite (older) | opposite (older) | not comparable | agrees | opposite (assertiveness) | agrees |
| H8 [setting differs] | not shown: 2 to 3, p 1 | not comparable | not shown: 5 to 0, p 0.0625 | not shown: 5 to 0, p 0.0625 | not shown: 5 to 0, p 0.0625 | not shown: 7 to 2, p 0.18 | agrees: 10 to 0, p 0.00195 | not shown: 6 to 1, p 0.125 |
| C1 [setting differs] | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable |
| C3 [setting differs] | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable | not comparable |

How to read a cell: a value target gives the subject's mean and the pairs it applies to; a direction target
gives how many seeds, pairs or runs went the study's way against the other (H3 also its mean start of turning
at 1.15, 1.42 and 1.78 m/s; C1 how many runs separated, and the mean share on their own right); H4 and H5 give
the mean speed change and the share of walkers slowing by more than 0.1 m/s, with no verdict.
**A significant direction can be a small effect**: these runs are nearly deterministic, so a consistent
difference of centimetres is significant. Read H3 with its numbers.

**Pass distance over all pairs, any ages** (no round 1 rule reads age, so in the rule arms and plain ORCA the
distance does not depend on who the two are; the realistic crowd gives few pairs of two young adults):

| Subject | Pairs | Mean centre distance (m) | Smallest | Largest |
| --- | --- | --- | --- | --- |
| plain | 30 | 0.5098 | 0.500728 | 0.515961 |
| passed_screening | 30 | 1.2504 | 1.25036 | 1.250364 |
| cane_rule_alone | 30 | 0.5046 | 0.5 | 0.512085 |
| all_runnable | 30 | 0.5046 | 0.5 | 0.512085 |
| reference_default | 30 | 0.5058 | 0.500123 | 0.514699 |
| step1_independent | 20 | 0.9133 | 0.625094 | 1.25011 |
| step1_non_verbal | 27 | 0.9871 | 0.624539 | 1.253824 |
| step1_talk | 16 | 0.8622 | 0.617734 | 1.152859 |

**How often each rule matched** (runs in which it matched at least once, of each arm's pairs):

| Arm | Pairs | Rules matched |
| --- | --- | --- |
| plain | 30 | none |
| passed_screening | 30 | `ext_head_on_0ecc2d1a6e@2` 30 |
| cane_rule_alone | 30 | `ext_head_on_6455ca5589@3` 30 |
| all_runnable | 30 | `ext_head_on_6455ca5589@3` 30 |
| reference_default | 30 | `keep_left_head_on@1` 15, `younger_yields_head_on@1` 15 |

**Who adapts in a pair with one person at mobility_aid cane** (described, not a target: no study read is about
this; H8 is about age). Counts are the other's way against the cane
user's, ties dropped, with the exact sign test's p:

| Subject | Pairs | The other's mean lateral share | The other deviates more | The other slows more | Passed first: cane user / other / together / none |
| --- | --- | --- | --- | --- | --- |
| plain | 30 | 0.5 | 12 to 18, p 0.362 | 13 to 13, p 1 | 0 / 0 / 30 / 0 |
| passed_screening | 30 | 0.5 | 0 to 0, p 1 | 16 to 12, p 0.572 | 0 / 0 / 30 / 0 |
| cane_rule_alone | 30 | 0.5044 | 30 to 0, p 0 | 30 to 0, p 0 | 13 / 0 / 17 / 0 |
| all_runnable | 30 | 0.5044 | 30 to 0, p 0 | 30 to 0, p 0 | 13 / 0 / 17 / 0 |
| reference_default | 30 | 0.75 | 24 to 6, p 0.00143 | 25 to 4, p 0.000104 | 0 / 0 / 30 / 0 |
| step1_independent | 20 | 0.597 | 14 to 3, p 0.0127 | 16 to 4, p 0.0118 | 6 / 5 / 9 / 0 |
| step1_non_verbal | 27 | 0.6302 | 21 to 2, p 6.6e-05 | 23 to 4, p 0.000311 | 9 / 2 / 16 / 0 |
| step1_talk | 16 | 0.6389 | 12 to 4, p 0.0768 | 13 to 3, p 0.0213 | 4 / 2 / 10 / 0 |

**H7 with the cane held fixed** (not the verdict of record, which is H7's row above). A trait is tested
apart from the cane: in pairs where both or neither have it, by H7's sign test; in pairs with one cane user,
by whether the cane user passes first as often when the trait is at its level on the cane user's side
("with") as on the other's ("against"), by Fisher's exact test. A trait whose pairs all fall on one side cannot
be told apart from the cane and is not counted. Bonferroni over every test made.

| Subject | H7 as recorded | With the cane held fixed | assertiveness | gender | older |
| --- | --- | --- | --- | --- | --- |
| plain | not comparable | not comparable | – | – | – |
| passed_screening | not comparable | not comparable | – | – | – |
| cane_rule_alone | opposite (older) | agrees; not separable: gender, older | holder first with 4 of 4, against 2 of 2, p 1 | holder first with 0 of 0, against 6 of 6, not separable | holder first with 7 of 7, against 0 of 0, not separable |
| all_runnable | opposite (older) | agrees; not separable: gender, older | holder first with 4 of 4, against 2 of 2, p 1 | holder first with 0 of 0, against 6 of 6, not separable | holder first with 7 of 7, against 0 of 0, not separable |
| reference_default | not comparable | not comparable | – | – | – |
| step1_independent | agrees | agrees; not separable: assertiveness, older | holder first with 3 of 5, against 0 of 0, not separable | holder first with 1 of 4, against 5 of 7, p 0.242 | holder first with 2 of 5, against 0 of 0, not separable |
| step1_non_verbal | opposite (assertiveness) | agrees; not separable: assertiveness, older | holder first with 7 of 7, against 0 of 0, not separable | holder first with 6 of 6, against 3 of 5, p 0.182 | holder first with 5 of 5, against 0 of 0, not separable |
| step1_talk | agrees | agrees; not separable: assertiveness, older | holder first with 2 of 3, against 0 of 0, not separable | holder first with 3 of 3, against 1 of 3, p 0.4 | holder first with 1 of 2, against 0 of 0, not separable |

**When the cane user is the younger** (who passed first: cane user / other / together / none). If age,
not the cane, decided who went first, the other would go first here. By group: the cane user under 65, the other 65 or over.

| Subject | Younger by years | Younger by age group |
| --- | --- | --- |
| plain | 6 pairs: 0 / 0 / 6 / 0 | 0 pairs: 0 / 0 / 0 / 0 |
| passed_screening | 6 pairs: 0 / 0 / 6 / 0 | 0 pairs: 0 / 0 / 0 / 0 |
| cane_rule_alone | 6 pairs: 4 / 0 / 2 / 0 | 0 pairs: 0 / 0 / 0 / 0 |
| all_runnable | 6 pairs: 4 / 0 / 2 / 0 | 0 pairs: 0 / 0 / 0 / 0 |
| reference_default | 6 pairs: 0 / 0 / 6 / 0 | 0 pairs: 0 / 0 / 0 / 0 |
| step1_independent | 0 pairs: 0 / 0 / 0 / 0 | 0 pairs: 0 / 0 / 0 / 0 |
| step1_non_verbal | 0 pairs: 0 / 0 / 0 / 0 | 0 pairs: 0 / 0 / 0 / 0 |
| step1_talk | 0 pairs: 0 / 0 / 0 / 0 | 0 pairs: 0 / 0 / 0 / 0 |

## The targets

**H1.** Two young adults on a collision course pass with their centres this far apart at the closest point. *Rapos V, Cinelli ME, Grunberg R, Bourgaize S, Cretual A, Olivier A-H (2021)*, Results (abstract) (abstract).
Setting: Laboratory, Canada, a 12.6 m pathway, 17 young and 17 older adults, comfortable speed.
Target: 0.93 ± 0.17 m (met from 0.76 to 1.1).
- Differs: crossing paths at several angles in the study; head-on in the simulation
- Differs: [inferred] the distance is between body centres (Meerhoff2018's method in the same line of work); Rapos2021's own methods were not read

**H2.** When an older adult is on a collision course, the two pass closer than two young adults do. *Rapos V, Cinelli ME, Grunberg R, Bourgaize S, Cretual A, Olivier A-H (2021)*, Results (abstract) (abstract).
Setting: As H1.
Target: 0.79 ± 0.18 m (met from 0.61 to 0.97).
- Differs: the abstract does not say whether the other walker was older or young
- Differs: crossing paths at several angles in the study; head-on in the simulation
- Differs: [inferred] the distance is between body centres, as H1

**H3.** A walker starts to turn further before the point of minimal distance the faster it walks. *Huber M, Su Y-H, Krueger M, Faschian K, Glasauer S, Hermsdoerfer J (2014)*, Table 1 (start of turning, 180 degrees); Results 2.2; Methods 4.4 (definitions) (full text).
Setting: Laboratory, Germany, instructed speeds; the other walker (the interferer) went straight and did not avoid.
Reported: {"fast": 2.7, "normal": 2.4, "slow": 2.1, "speeds_mps": {"fast": 1.78, "normal": 1.42, "slow": 1.15}}.
- Differs: in the study only one walker avoided; in the simulation both may, unless the scenario makes one go straight
- Differs: the authors note that some starts coincided with the first tracked point, so the true values may be larger

**H4.** In a head-on meeting walkers change their path and not their speed. *Huber M, Su Y-H, Krueger M, Faschian K, Glasauer S, Hermsdoerfer J (2014)*, Results 2.1 and 3.1; Table 1 (no start of braking at 180 degrees) (full text).
Setting: As H3.
- Differs: in the study only one walker avoided

**H5.** In a head-on meeting walkers slow down significantly while they decide on which side to pass. *Moussaid M, Helbing D, Garnier S, Johansson A, Combe M, Theraulaz G (2009)*, Section 4.2 and Figure 3 (the decision zone) (full text).
Setting: Laboratory, France, a corridor 7.88 x 1.75 m, 40 people aged 18 to 30.

**H6.** The walker who gives way (passes second) contributes more to the avoidance than the one who passes first. *Olivier A-H, Marin A, Cretual A, Berthoz A, Pettre J (2013)*, Abstract (abstract).
Setting: Laboratory, France, crossing paths.
- Differs: crossing paths at several angles in the study; head-on in the simulation, where both may pass "together"

**H7.** Who passes first is predicted by the walkers' initial speed and heading, not by gender, height or personality traits. *Knorr AG, Willacker L, Hermsdoerfer J, Glasauer S, Krueger M (2016)*, Abstract (experiments 1 and 2) (abstract).
Setting: Laboratory, Germany, pairs at their natural speed on paths that would collide halfway.
- Differs: which personality traits were measured is not in the abstract; the simulation tests the traits its people have (assertiveness, and age and gender)

**H8.** When an older adult meets a young adult, the young adult contributes more to the avoidance, whoever passes first. *Rapos V, Cinelli ME, Grunberg R, Bourgaize S, Cretual A, Olivier A-H (2021)*, Results (abstract) (abstract).
Setting: As H1.
- Differs: crossing paths at several angles in the study; head-on in the simulation

**C1.** In a two-way street flow the two directions separate, each keeping mostly to one side of the street. *Moussaid M, Helbing D, Garnier S, Johansson A, Combe M, Theraulaz G (2009)*, Section 4.4 (ii) and Figure 5b (observed, blue bars) (full text).
Setting: Field, Bordeaux (Sainte-Catherine street), 2,670 pedestrians tracked in an 8 x 6 m field, inflow about 0.65 per second each way.
Reported: {"own_right": 0.77, "own_left": 0.23}.
- Differs: the simulation's flow starts all at once on a lattice; the street's people entered over 30 minutes
- Differs: which side is kept is a parameter by place (sides, below); this target judges the separation, not the side

**C3.** In a two-way flow walking speed falls as density rises, and the flow per metre of width levels off from about 1.0 person per square metre. *Zhang J, Klingsch W, Schadschneider A, Seyfried A (2012)*, Sections 2, 4.1 and 4.3; Conclusion (full text).
Setting: Laboratory, Duesseldorf, up to 350 participants, mostly students, corridors 3.0 and 3.6 m wide.
Reported: {"free_speed_mps": 1.55, "free_speed_sd_mps": 0.18, "plateau_from_density_per_m2": 1.0, "peak_specific_flow_per_m_s": 1.5, "at_density_per_m2": 2.0}.
- Differs: the simulation's corridor is 4.0 m wide
- Differs: the free speed spread (1.55 +/- 0.18 m/s) is of the free walk, not of the speed at a density, so it is shown and not used as a tolerance

## Sides (a parameter by place, not judged)

For Singapore no published study was found (#69), so no side is judged. Places with a study:

- france: right {"both_walk": {"right": 0.8, "left": 0.2}, "other_stands": {"right": 0.6, "left": 0.41}, "street_flow": {"right": 0.77, "left": 0.23}} (moussaid2009, full text, figures read by pixel measurement)
- beijing: right {"right": 0.6875} (circle_antipode2019, full text, preprint)
- korea: left {"kept_left_under_a_keep_left_rule": 0.593, "said_they_prefer_right": 0.737} (jung2013, abstract)
- japan: left {} (echeverria2026, full text)

| Subject | Both on own left | Both on own right | Mixed | Share left |
| --- | --- | --- | --- | --- |
| plain | 15 | 15 | 0 | 0.5 |
| passed_screening | 30 | 0 | 0 | 1.0 |
| cane_rule_alone | 15 | 15 | 0 | 0.5 |
| all_runnable | 15 | 15 | 0 | 0.5 |
| reference_default | 24 | 6 | 0 | 0.8 |
| step1_independent | 5 | 15 | 0 | 0.25 |
| step1_non_verbal | 12 | 15 | 0 | 0.4444 |
| step1_talk | 8 | 8 | 0 | 0.5 |

**The side both ways.** The corridor is symmetric about its centre line, so a rule that turns right in place of
left gives the mirror image of the left-turn rule's runs: every target but the side is the same, apart from the
baseline's random perturbation `[derived: mirror symmetry; not run]`. Which side matches Singapore is unknown.

## Left out

- **C2** (moussaid2009): At low density a two-way flow spreads almost uniformly across the street. Reason: a result of the authors' model (their Supplementary Figure 6), not an observation; under decision 6 it is not human evidence.
- **H9** (none): Walkers do not stop or back up in a head-on meeting. Reason: no study read reports stopping or backing up, and none counts them; the simulation's stops and backing up are reported, not judged.
