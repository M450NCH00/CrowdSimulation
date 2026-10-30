# Round 1 against the human targets (issue #122, RF-37)

Targets: `configs/human_targets/head_on_v1.yaml` (sha256 `7b732845fd93`). Method: `docs/human-targets.md`. No model call, USD 0.

**Tolerances** (the user's decision of 2026-10-30, fixed before any rule was measured): a value target is met
within one reported SD of the study's mean; a target with no reported spread is judged on its direction, by the
exact two-sided sign test at 0.05; two studies that disagree are shown with no verdict.

**Every comparison marked `[setting differs]` is in a setting unlike the study's** (each target's `differs` in the
targets file says how). The verdicts are about the simulation against the study's numbers, not proof about people.

## Subjects

| Subject | Head-on pairs | Pairs at three speeds | Crowd runs | Note |
| --- | --- | --- | --- | --- |
| plain | 30 | 90 | 50 |  |
| passed_screening | 30 | 90 | 50 |  |
| cane_rule_alone | 30 | 90 | 50 |  |
| all_runnable | 30 | 90 | 50 |  |
| reference_default | 30 | 90 | 50 |  |
| step1_independent | 52 | 0 | 0 | 52 of 96 sessions resolved by the plans alone |
| step1_non_verbal | 53 | 0 | 0 | 53 of 96 sessions resolved by the plans alone |
| step1_talk | 47 | 0 | 0 | 47 of 96 sessions resolved by the plans alone |

## Verdicts

| Target | plain | passed_screening | cane_rule_alone | all_runnable | reference_default | step1_independent | step1_non_verbal | step1_talk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 [setting differs] | outside: 0.5096 (n 1) | outside: 1.2504 (n 1) | outside: 0.5096 (n 1) | outside: 1.2504 (n 1) | outside: 0.5041 (n 1) | within: 0.9593 (n 28) | within: 0.9309 (n 29) | within: 0.9681 (n 28) |
| H2 [setting differs] | outside: 0.51 (n 9) | outside: 1.2504 (n 9) | outside: 0.5078 (n 9) | within: 0.9197 (n 9) | outside: 0.5058 (n 9) | within: 0.9417 (n 24) | outside: 0.9779 (n 24) | within: 0.9025 (n 19) |
| H3 [setting differs] | agrees: 30 to 0; m: 2.9801, 3.7168, 4.8504 | opposite: 1 to 29; m: 5.0929, 5.03, 5.0608 | agrees: 30 to 0; m: 2.9401, 3.6393, 4.7143 | opposite: 4 to 26; m: 4.7676, 4.7816, 4.8993 | agrees: 30 to 0; m: 3.2347, 4.0412, 5.1245 | not comparable | not comparable | not comparable |
| H4 [setting differs] | 0.2491 m/s; 1.0 slow | 0.0199 m/s; 0.0 slow | 0.2725 m/s; 1.0 slow | 0.0734 m/s; 0.1333 slow | 0.1529 m/s; 0.2833 slow | 0.2704 m/s; 0.6923 slow | 0.2182 m/s; 0.6604 slow | 0.1812 m/s; 0.6064 slow |
| H5 | 0.2491 m/s; 1.0 slow | 0.0199 m/s; 0.0 slow | 0.2725 m/s; 1.0 slow | 0.0734 m/s; 0.1333 slow | 0.1529 m/s; 0.2833 slow | 0.2704 m/s; 0.6923 slow | 0.2182 m/s; 0.6604 slow | 0.1812 m/s; 0.6064 slow |
| H6 [setting differs] | not comparable | not comparable | not comparable | not comparable | not comparable | agrees: 12 to 3, p 0.0352 | agrees: 15 to 3, p 0.00754 | not shown: 10 to 3, p 0.0923 |
| H7 [setting differs] | not comparable | not comparable | not comparable | not comparable | not comparable | agrees | opposite (assertiveness) | agrees |
| H8 [setting differs] | not shown: 3 to 0, p 0.25 | not comparable | not shown: 3 to 0, p 0.25 | not shown: 1 to 0, p 1 | not shown: 3 to 0, p 0.25 | agrees: 18 to 3, p 0.00149 | agrees: 20 to 2, p 0.000121 | agrees: 15 to 3, p 0.00754 |
| C1 [setting differs] | opposite: 3 of 50 runs; own right 0.5068 | not shown: 32 of 50 runs; own right 0.3823 | opposite: 4 of 50 runs; own right 0.4986 | not shown: 27 of 50 runs; own right 0.3903 | agrees: 40 of 50 runs; own right 0.3201 | not comparable | not comparable | not comparable |
| C3 [setting differs] | agrees: 46 to 4, p 0 | agrees: 43 to 7, p 0 | agrees: 50 to 0, p 0 | agrees: 47 to 3, p 0 | agrees: 49 to 1, p 0 | not comparable | not comparable | not comparable |

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
| cane_rule_alone | 30 | 0.5091 | 0.500479 | 0.515961 |
| all_runnable | 30 | 1.1512 | 0.500479 | 1.250364 |
| reference_default | 30 | 0.5057 | 0.500123 | 0.514699 |
| step1_independent | 52 | 0.9511 | 0.625094 | 1.250361 |
| step1_non_verbal | 53 | 0.9522 | 0.624539 | 1.253824 |
| step1_talk | 47 | 0.9416 | 0.607523 | 1.253893 |

**Speed against density** (C3; Zhang2012 reports a free speed of 1.55 ± 0.18 m/s, no difference from one-way
flow below 1.0 person/m², and a flow per metre of width that levels off from about 1.0 and peaks at 1.5 /(m·s) at
2.0 person/m²). Mean speed (m/s) and flow per metre (/(m·s)) by density bin, over every sample:

- plain: 0.0-0.25: 1.3109, 0.1639 (269); 0.25-0.5: 1.2775, 0.3785 (166); 0.5-0.75: 1.12, 0.6295 (41); 0.75-1.0: 1.0875, 0.8969 (26); 1.0-1.25: 1.0174, 1.0614 (43); 1.25-1.5: 1.0878, 1.4272 (66); 1.5-1.75: 1.0422, 1.6212 (41); 1.75-2.0: 1.0377, 1.8954 (88); 2.0-2.25: 1.0936, 2.2466 (144); 2.25-2.5: 0.9518, 2.1925 (89); 2.5-2.75: 0.8595, 2.1918 (42); 2.75-3.0: 0.4794, 1.3463 (29); 3.0-3.25: 0.4028, 1.2317 (21); 3.25-3.5: 0.3645, 1.2027 (20); 3.5-3.75: 0.3328, 1.1822 (14); 3.75-4.0: 0.2885, 1.1057 (5); 4.0-4.25: 0.3551, 1.438 (7)
- passed_screening: 0.0-0.25: 1.2985, 0.1623 (213); 0.25-0.5: 1.2817, 0.3654 (92); 0.5-0.75: 1.2297, 0.683 (35); 0.75-1.0: 1.1846, 0.936 (25); 1.0-1.25: 1.2408, 1.3206 (44); 1.25-1.5: 1.2404, 1.6303 (63); 1.5-1.75: 1.2285, 1.9367 (72); 1.75-2.0: 1.2361, 2.2493 (86); 2.0-2.25: 1.253, 2.588 (133); 2.25-2.5: 1.2336, 2.8154 (69); 2.5-2.75: 1.0807, 2.749 (21)
- cane_rule_alone: 0.0-0.25: 1.2887, 0.1611 (263); 0.25-0.5: 1.1822, 0.344 (180); 0.5-0.75: 1.01, 0.5416 (73); 0.75-1.0: 0.8922, 0.7213 (66); 1.0-1.25: 0.9903, 1.0421 (53); 1.25-1.5: 0.8745, 1.1487 (51); 1.5-1.75: 0.8537, 1.3495 (52); 1.75-2.0: 0.9104, 1.6541 (91); 2.0-2.25: 0.948, 1.9413 (115); 2.25-2.5: 0.7855, 1.8169 (100); 2.5-2.75: 0.7085, 1.8038 (64); 2.75-3.0: 0.5361, 1.4995 (53); 3.0-3.25: 0.3396, 1.0336 (47); 3.25-3.5: 0.2561, 0.8491 (48); 3.5-3.75: 0.1381, 0.4908 (70); 3.75-4.0: 0.1285, 0.4891 (45); 4.0-4.25: 0.264, 1.0651 (18); 4.25-4.5: 0.2614, 1.1213 (6)
- all_runnable: 0.0-0.25: 1.2767, 0.1596 (237); 0.25-0.5: 1.263, 0.3763 (120); 0.5-0.75: 1.1949, 0.663 (56); 0.75-1.0: 1.1003, 0.8942 (43); 1.0-1.25: 1.1552, 1.2327 (50); 1.25-1.5: 1.1211, 1.4612 (48); 1.5-1.75: 1.2016, 1.8725 (57); 1.75-2.0: 1.1339, 2.0611 (82); 2.0-2.25: 1.1549, 2.3769 (101); 2.25-2.5: 1.1277, 2.6001 (80); 2.5-2.75: 0.9547, 2.4417 (45); 2.75-3.0: 0.7478, 2.1174 (21); 3.0-3.25: 0.6002, 1.8367 (19); 3.25-3.5: 0.709, 2.3252 (10)
- reference_default: 0.0-0.25: 1.2584, 0.1573 (200); 0.25-0.5: 1.0616, 0.3077 (165); 0.5-0.75: 0.7375, 0.4095 (139); 0.75-1.0: 0.8282, 0.6745 (90); 1.0-1.25: 0.7335, 0.7854 (81); 1.25-1.5: 0.647, 0.8407 (95); 1.5-1.75: 0.7024, 1.0966 (108); 1.75-2.0: 0.753, 1.3703 (130); 2.0-2.25: 0.6974, 1.4325 (170); 2.25-2.5: 0.5739, 1.3244 (175); 2.5-2.75: 0.47, 1.2048 (138); 2.75-3.0: 0.2676, 0.7511 (86); 3.0-3.25: 0.1893, 0.5773 (69); 3.25-3.5: 0.1673, 0.5543 (46); 3.5-3.75: 0.1533, 0.5452 (14)

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
| cane_rule_alone | 19 | 11 | 0 | 0.6333 |
| all_runnable | 30 | 0 | 0 | 1.0 |
| reference_default | 21 | 9 | 0 | 0.7 |
| step1_independent | 15 | 37 | 0 | 0.2885 |
| step1_non_verbal | 22 | 31 | 0 | 0.4151 |
| step1_talk | 23 | 24 | 0 | 0.4894 |

**The side both ways.** The corridor is symmetric about its centre line, so a rule that turns right in place of
left gives the mirror image of the left-turn rule's runs: every target but the side is the same, apart from the
baseline's random perturbation `[derived: mirror symmetry; not run]`. Which side matches Singapore is unknown.

## Left out

- **C2** (moussaid2009): At low density a two-way flow spreads almost uniformly across the street. Reason: a result of the authors' model (their Supplementary Figure 6), not an observation; under decision 6 it is not human evidence.
- **H9** (none): Walkers do not stop or back up in a head-on meeting. Reason: no study read reports stopping or backing up, and none counts them; the simulation's stops and backing up are reported, not judged.
