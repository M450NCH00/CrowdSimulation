# Parameters of the avoidance scenarios: what each number is, and where it comes from

Issue #24 left the hallway's sizes and speeds as unsourced placeholders (`WORK_LOG-24.md`,
Q3). For the avoidance scenarios of issue #26 every quantity in a config carries a tag,
and this file gives the source behind it. The rule: **a number is cited, with a place a
reader can look it up, or it is called a placeholder.** A test reads the tags out of the
config files and fails if a quantity has none, or if a placeholder is missing from section
3 (`tests/test_crowd_scenarios.py`).

| Tag in the config | Meaning |
|---|---|
| `[cited: ...]` | The value was read in the source named. Section 2 gives the locator. |
| `[derived: ...]` | Worked out from cited values by the rule named. Section 2 shows the arithmetic. |
| `[placeholder]` | A round, plausible value with no source. Section 3 lists every one. **Do not report a result that depends on one as if it rested on data.** |
| `[design]` | A choice about the scene or about the numerics, not a physical quantity. Section 4. |

Locators are file and line in `refs/` at the repository root. Every one was read in the
cached copy, not recalled.

Sections 1 to 7 are the avoidance scenarios' parameters. Section 8 (issue #72) holds the values
of the resolution design, `resolution.md`, D12: what an LLM agent is told it can see and hear.
Issue #73 (RF-17) put them in a config, `configs/resolution/llm_view_v1.yaml` (block
`llm_view`), with these tags.

## 1. The agent type

One agent type, `pedestrian`, is used by all five scenarios, with identical values
(tested: `test_every_shipped_scenario_uses_the_same_pedestrian`), so that a difference
between scenarios is not a difference between the bodies walking through them.

The two versioned configs of issue #32 (`passage_meet_middle_v1`,
`passage_meet_with_speeds_v1`, scenario type `passage_meeting`) use the same `pedestrian`
with one more physical parameter, `backing_speed`: how fast it backs out of a single-file
passage. In `passage_meet_with_speeds_v1`, agent 1 is a second type, `slow_backer`, that walks,
hurries and backs up more slowly. `backing_speed` is optional in every agent type and written
into a resolved scenario only when set, so the five scenarios above resolve, and hash, as
before; an agent whose type does not set it backs up at 0.92 m/s (`DEFAULT_BACKING_SPEED`,
cited below), never faster than its maximum speed.

## 2. Cited and derived values

| Parameter | Value | Status | Source and locator | What the source measured, and the caveat |
|---|---|---|---|---|
| `radius` | 0.25 m | cited | Yamamoto et al. 2019, Sec 4.3; `b3_yamamoto_bodyrotation.txt:649-652` | "the effective shoulder width ... of a model pedestrian correspond to 2a = 49.8 cm". Half of it is 0.249 m, rounded here to 0.25. Fitted to four men aged 18 to 25 passing each other in a corridor (line 330). It is an *effective* width: the same passage gives the unclothed average for Japanese men of 20 to 24 as 44.9 cm (line 660). A disc of this radius is as deep as it is wide; a body is not (bust depth 31.0 cm in the same fit). |
| `preferred_speed` | 1.3 m/s | cited | Moussaïd et al. 2009, Sec 2(c) and Sec 4(a); `si1_moussaid2009_pmc.txt:108` and `:119` | Measured: "The desired velocities are normally distributed with an average value of 1.29 ± 0.19 m/s (mean ± s.d.)", 40 people aged 18 to 30 walking alone along a corridor in Bordeaux. The authors' own simulations use "v0 = 1.3 m/s". Consistent with Bohannon 1997, whose mean comfortable gait speeds run from 1.272 to 1.462 m/s across age and sex groups (`si1_bohannon1997_pubmed_abstract.txt:18-19`). |
| `preferred_speed` of the faster walker in `overtaking` | 1.48 m/s | derived | same, Sec 4(a) | The measured mean plus one standard deviation: 1.29 + 0.19. |
| `preferred_speed` of the slower walker in `overtaking` | 1.10 m/s | derived | same, Sec 4(a) | The measured mean minus one standard deviation: 1.29 − 0.19. |
| `max_speed` | 2.0 m/s | cited | Menge, `examples/core/4square/4squareS.xml`, line 15 (`max_speed="2"`); `si1_menge_4squareS.xml:15` | A setting used in a pedestrian simulator, not a measurement. It lies inside the range of mean *maximum* gait speeds Bohannon 1997 reports, 1.749 to 2.533 m/s (`si1_bohannon1997_pubmed_abstract.txt:19-21`). An agent only exceeds its preferred speed when ORCA has it get out of the way. |
| `time_horizon` (τ) | 3.0 s | cited | Karamouzas, Skinner and Guy 2014, p. 3; `si1_karamouzas2014_1412_1082.txt:136-138` | From recorded pedestrian trajectories: "an appropriate value is τ0 ≈ 3 s, which is consistent with previous research demonstrating an interaction time horizon of 2–4 s". The authors call it a lower-bound estimate of the range of unscreened interactions. Menge's ORCA example uses the same number (`si1_menge_4squareS.xml:22`, `tau="3.0"`). |
| `time_horizon_obst` | 0.15 s | cited | Menge, same file, line 22 (`tauObst="0.15"`); `si1_menge_4squareS.xml:22` | A setting used in practice, not a measurement. The ORCA paper says only that it can be smaller than τ (`si1_orca_vandenberg2011.txt:579`). It must be at least one time step (`derivations.md`, section 12). |
| `max_neighbours` | 10 | cited | Menge, same file, line 15 (`max_neighbors="10"`); `si1_menge_4squareS.xml:15` | A setting used in practice. RVO2's examples use 10 as well (`Blocks.cc:88` and `Circle.cc:69`, in `si1_rvo2_75822bb_excerpts.txt`). **It is the parameter the crowd result is most sensitive to**: see the README. |
| `sensing_radius` (R) | 12.5 m | derived | ORCA paper, Sec 5.1; `si1_orca_vandenberg2011.txt:411` | "robots B that are farther away from robot A than (v_A^max + v_B^max) τ will never collide with robot A within τ time, so they can safely be left out". With τ = 3.0 s and both maximum speeds 2.0 m/s that is 12.0 m. The paper's sentence measures between centres and leaves out the two radii, which add 0.5 m: 12.5 m. Menge's example uses 5 m (`neighbor_dist="5"`), which is shorter than this bound. |
| `width` of `wide_corridor_head_on`; `approach_width` of `corridor_to_bottleneck` | 1.75 m | cited | Moussaïd et al. 2009, Sec 2(a); `si1_moussaid2009_pmc.txt:100` | "The experimental corridor (length = 7.88 m, width = 1.75 m)", in which pairs of people walked toward each other and passed. The *length* is not used here: see `length` in section 4. |
| `backing_speed` (and the default, `DEFAULT_BACKING_SPEED`) | 0.92 m/s | cited | Nakahara et al. 2005, "Results and Discussion", p. 824; `si32_nakahara2005_backward_walking.txt:156-159` | "The mean (SD) walking speeds calculated across all individuals in this study were 0.43 (0.111) m/s for slow speed condition, 0.92 (0.114) m/s for normal speed condition, and 1.68 (0.201) m/s for fast speed condition", walking *backwards*. The normal condition's instruction was "Walk at a normal, comfortable speed" (line 57). **Ten people, one woman and nine men, aged 21.8 years on average (lines 52-53)**, barefoot on a walkway, in Japan; the authors say the normal value is similar to Grasso et al. 1998 (line 160), which was not read. |
| `backing_speed` of `slow_backer` | 0.43 m/s | cited | same, p. 824 | The study's *slow* condition ("Walk slowly as if you were waiting at a bus stop", line 57) for the same ten young adults. Used for a person who backs up slowly: the number is the study's, the person it is given to is this project's choice. |
| `preferred_speed` of `slow_backer` | 1.10 m/s | derived | Moussaïd et al. 2009, Sec 4(a) | As the slower walker of `overtaking`: the measured mean minus one standard deviation. |
| `approach_width` of `passage_meeting` | 1.75 m | cited | Moussaïd et al. 2009, Sec 2(a) | As `corridor_to_bottleneck`'s. |
| `width` and `length` of `bidirectional_flow` | 4.0 m, 50.0 m | cited | Moussaïd et al. 2009, Sec 2(c); `si1_moussaid2009_pmc.txt:109` | "Simulations of bidirectional flows were conducted in a 6×50 m street with the pedestrians of each flow starting from the central, 4 m wide area". That is the authors' *simulation* of a street they had filmed, in which the outer metre on each side was taken up by people standing at shop fronts. Here the central 4 m is a corridor with walls. |

## 3. Placeholders

Eight quantities in the shipped scenarios are `[placeholder]`: three of issue #26 and five
of issue #32. Nothing else is.

| Scenario | Parameter | Value | Why it has no source, and what would replace it |
|---|---|---|---|
| `corridor_to_bottleneck` | `bottleneck_width` | 0.8 m `[placeholder]` | The scenario needs a width that only one agent can use at a time. For two discs 0.5 m across that is anything under 1.0 m, and 0.8 m is the hallway width of issue #24. **It is not a width at which real people cannot pass.** The one source read on this, Yamamoto et al. 2019, had pairs pass each other at widths down to 60 cm by turning their bodies (Sec 3, lines 344–345; "the males did not need to rotate for W = 100 cm in most cases", line 1282). Discs cannot turn sideways. A sourced value would need either a model of the body that can, or a segment narrow enough that people do not try. |
| `corridor_to_bottleneck` | `bottleneck_length` | 4.0 m `[placeholder]` | The hallway length of issue #24, itself a placeholder. No source was looked for: any length makes the segment single-file. |
| `bidirectional_flow` | `spawn_spacing` | 1.0 m `[placeholder]` | The spacing of the lattice the two crowds start on, which sets their starting density (about one person per square metre). Round, and not taken from the street observation the corridor's size comes from, whose density was not read. |
| `passage_meet_middle_v1`, `passage_meet_with_speeds_v1` | `passage_width` | 0.8 m `[placeholder]` | The bottleneck's width, for the same reason, with the same caveat: not a width at which real people cannot pass. |
| `passage_meet_middle_v1`, `passage_meet_with_speeds_v1` | `passage_length` | 4.0 m `[placeholder]` | The bottleneck's length. It sets how far in two people can be when they meet, and so how far one has to back out. |
| `passage_meet_with_speeds_v1` | `max_speed` of `slow_backer` | 1.4 m/s `[placeholder]` | A person who cannot hurry much. Below the cited maximum gait speeds of every group in Bohannon 1997 (1.749 m/s and up), so it is not one of them. It matters under the arbiter, which has a follower pushed backwards at nearly the leader's speed (`derivations.md`, section 17): a follower that cannot retreat that fast is hit. |

One more placeholder appears in an experiment, not in a scenario: `si1_bidirectional_flow`
runs the flow a second time with `max_neighbours` 40 `[placeholder]`, to show what the
neighbour limit does. Forty has no source.

## 4. Design choices

These are tagged `[design]`. They are choices about the scene or about the numerics; none
is a claim about people.

| Parameter | Value | Why |
|---|---|---|
| `dt` | 0.1 s | The time step of issue #24's hallway. |
| `max_time` | 60 to 120 s | Long enough for every scenario to finish or to be seen not to. |
| `goal_tolerance` | 0.2 m | An agent has arrived when its progress along its path is this close to the end. |
| `length`, `start_distance` of `wide_corridor_head_on` | 20 m, 8 m | The cited corridor was 7.88 m long. This one is longer, so that the two start 16 m apart, outside each other's 12.5 m sensing radius, and are seen to walk freely before they interact. Only the width is taken from the source. |
| `lateral_offsets` | 0, or ±0.05 m | Exactly head-on, or 10 cm off it: "slightly offset", as the issue puts it. |
| `approach_distances`, `goal_distance` of `open_crossing` | 8 m | Start outside nothing in particular; far enough to be walking steadily at the crossing. |
| `headway`, `travel_distance` of `overtaking` | 4 m, 40 m | Far enough for the faster walker to catch up and get past. |
| `approach_length`, `start_setback`, `merge_distance`, `lateral_offset` of `corridor_to_bottleneck` | 8, 7, 0.6, 0.4 m | The layout of issue #24's hallway, fitted into the 1.75 m corridor. |
| `agents_per_direction` | 50 | The default the issue asks for. |
| `spawn_jitter` | 0.1 m | Breaks the lattice's symmetry (`orca.md`, section 6). |
| `spawn_pattern`, `spawn_min_distance` of `bidirectional_flow` | not set (the lattice); 0.6 m when `random` | Optional, set in no shipped scenario. `random` places each group at random in the block the lattice would fill, at the same density, no two starts closer than the distance centre to centre (a 0.5 m body and 10 cm); the jitter is not used. Drawn one start at a time, a start too close is drawn again, so at the shipped density no more than about 0.7 m can be had. Neither key is written into a resolved scenario unless set, so runs and cases made before they existed resolve as they did. |
| `wall_clearance`, `wall_thickness` | 0.5 m | Where the lattice starts, and how walls are drawn. Wall thickness has no effect on the motion. |
| `lookahead` | 2.0 m (0.6 m in the bottleneck) | How far ahead on its path an agent aims. Shorter where the path has corners. |
| `cell_size` | 2.0 m | Grid cell of the neighbour search. No effect on the result. |
| `safety_margin` of `single_file` | 0.1 m | As in issue #24. |
| `deadlock` window and speed | 3.0 s, 0.01 m/s | As in issue #24. |
| Metric thresholds: `near_miss_distance`, `yield_speed_fraction`, `yield_min_duration`, `exposure_eps` | 0.1 m, 0.5, 1.0 s, 1e-6 m/s | Definitions, not measurements. They decide what gets *counted*, so `metrics.md` records them and every outcome file repeats them. None has a source. |
| Metric thresholds of issue #30: `pair_exposure_eps`, `collision_course_min_s` | 1e-3 m/s, 0 s | Definitions of pair exposure and of tier T1 (`metrics.md`, section 11). The first is five times the most that the primary baseline's perturbation can move a relative velocity (2 × 1e-4 m/s), so that the perturbation alone never makes a step count; the second counts any exposed step. Neither has a source. |
| `seed` | 26 | Of the starting jitter. |
| `approach_length`, `merge_distance`, `lateral_offset`, `exit_setback` of `passage_meeting` | 8, 0.6, 0.4, 7 m | The bottleneck's layout, with `exit_setback` in the place of `start_setback`: where a path ends beyond the far end. |
| `travelled` of `passage_meeting` | `[1.7, 1.7]`; `[2.7, 0.7]`; `[2.0, 1.4]` | Where the two start: how far each has walked into the 4 m passage. Each pair leaves them 0.1 m apart (4.0 − 0.5 − 0.1 = 3.4 m between the two walked-in distances): placed at the meeting point. Symmetric; asymmetric, agent 0 2.0 m further in; and, with the slow backer, a meeting at which the distance-optimal and the time-optimal choice of who backs out differ (`derivations.md`, section 18). |
| `start_speed` of `passage_meeting` | 0 m/s; `preferred` in the walking variant | Both start at rest, face to face: they have met. `preferred` starts each walking toward the other at its own preferred speed, as the agents of every other scenario start, and as the arbiter's way in a passage was first measured. **The choice decides what the arbiter's way does**: from rest it does not get the two through, walking it does, by an ORCA artefact (`derivations.md`, section 17.1), so the behaviour checks report both (`behaviour-checks.md`, section 6). |
| `safety_margin` of `single_file` in `passage_meeting` | 0.1 m | As in issue #24, and also what a backing agent adds to the two radii to find how far out it must back (`derivations.md`, section 17). |
| `groups.westbound` in `passage_meet_with_speeds_v1` | `slow_backer` | Which agent backs up slowly: agent 1, which has walked less far in. |

## 5. Physical parameters and demographic attributes are separate

An agent's size and speeds come from its agent type and from per-agent overrides in the
**scenario** config. Its age and gender come from a persona attached to it by an
**experiment** config (`population`). The two never meet in the code: the scenario schema
has no key for age, gender or persona, and `population` accepts nothing physical. So a
persona changes what a neighbour *perceives* and nothing about how the agent moves.

*Tested:* the same run with no personas, with a woman of 25 and a man of 70, and with the
two swapped gives the same trajectory to the last digit
(`tests/test_avoidance_runs.py::test_a_persona_changes_nothing_physical`).

The reason is the one the issue gives. If older agents were always slower, a rule found
later that mentions age could not be told apart from a rule about speed.

**Linking them is possible, and has to be written down.** An experiment that wants a
70-year-old to walk more slowly sets the persona under `population` and the speed under
`scenario_overrides.agents.overrides` for the same agent, in the same file, where it can
be read (tested: `test_speed_and_age_change_together_only_when_a_config_says_both`).

**No table of defaults by age and gender is shipped.** The issue allows one if every value
in it is cited or tagged. What was found does not fill a table:

| What | Value | Source and locator | Limit |
|---|---|---|---|
| Comfortable gait speed, women in their seventies | 1.272 m/s | Bohannon 1997, abstract; `si1_bohannon1997_pubmed_abstract.txt:18-19` | One end of a table of 12 age-by-sex groups. The other end is men in their forties, 1.462 m/s. **The other ten cells were not read**: the paper is behind a paywall and only its abstract was obtained. 230 healthy volunteers timed over 7.62 m (line 15); the abstract does not say where, and the author's address is the University of Connecticut. |
| Maximum gait speed | 1.749 m/s (women in their seventies) to 2.533 m/s (men in their twenties) | same, lines 19–21 | As above. |
| Shoulder width, men | 48.4 cm (SD 3.7) | Yamamoto et al. 2019, Table 2; `b3_yamamoto_bodyrotation.txt:1068-1079` | Five men aged 21 to 68 and four women aged 36 to 64 (line 1098), clothed, in Japan. The paper notes these are larger than the unclothed statistics. |
| Shoulder width, women | 41.0 cm (SD 1.4) | same | As above. |

A table for the four personas of issue #24 (ages 25 and 70, female and male) would have
one cited speed out of four and no size by age at all. The rest would be placeholders
dressed as a table, so it was left out.

## 6. Sources

| Short name | Full reference | Cached copy in `refs/` |
|---|---|---|
| Moussaïd et al. 2009 (written "Moussaid et al. 2009" in the configs, which are plain ASCII) | M. Moussaïd, D. Helbing, S. Garnier, A. Johansson, M. Combe, G. Theraulaz, "Experimental study of the behavioural mechanisms underlying self-organization in human crowds", *Proc. R. Soc. B* 276(1668), 2755–2762, 2009. DOI 10.1098/rspb.2009.0405. Read in the PubMed Central copy, PMC2839952. | `si1_moussaid2009_pmc.txt` (text), `si1_moussaid2009_pmc.html` |
| Yamamoto et al. 2019 | H. Yamamoto, D. Yanagisawa, C. Feliciani, K. Nishinari, "Body-rotation behavior of pedestrians for collision avoidance in passing and cross flow", arXiv:1903.07742v2. Cached by issue #16. | `b3_yamamoto_bodyrotation.txt`, `b3_yamamoto_bodyrotation.pdf` |
| Karamouzas et al. 2014 | I. Karamouzas, B. Skinner, S. J. Guy, "Universal power law governing pedestrian interactions", arXiv:1412.1082v1. The journal version was not read. | `si1_karamouzas2014_1412_1082.txt`, `.pdf` |
| Bohannon 1997 | R. W. Bohannon, "Comfortable and maximum walking speed of adults aged 20–79 years: reference values and determinants", *Age and Ageing* 26(1), 15–19, 1997. DOI 10.1093/ageing/26.1.15. **Abstract only**, through PubMed (PMID 9143432). | `si1_bohannon1997_pubmed_abstract.txt` |
| Menge 4squareS.xml | The Menge crowd-simulation framework, `github.com/MengeCrowdSim/Menge`, file `examples/core/4square/4squareS.xml` on branch `master` at commit `00f97ea` (the file last changed in `577b517`). Apache-2.0. An example configuration of a pedestrian simulator; cited for what is used in practice, not as evidence about pedestrians. | `si1_menge_4squareS.xml` |
| ORCA paper | van den Berg, Guy, Lin, Manocha, "Reciprocal n-body collision avoidance"; `orca.md`, section 1. | `si1_orca_vandenberg2011.txt`, `.pdf` |
| Nakahara et al. 2005 | K. Nakahara, T. Ishii, H. Ida, K. Nakazawa, H. Yamamoto, "The influence of walking speed on symmetry for temporal-spatial and GRF parameters in backward walking", *Proceedings of the XXIII International Symposium on Biomechanics in Sports* (ISBS 2005), Beijing, 823–826. ISBS Conference Proceedings Archive, open access (`ojs.ub.uni-konstanz.de/cpa/article/view/1194`). Read in full (issue #32). | `si32_nakahara2005_backward_walking.txt` (text, pypdf), `.pdf` |
| Moussaïd et al. 2011 | M. Moussaïd, D. Helbing, G. Theraulaz, "How simple rules determine pedestrian behavior and crowd disasters", *PNAS* 108(17), 6884–6888, 2011. DOI 10.1073/pnas.1016507108. **Read in the accepted manuscript**, arXiv:1105.2152v1 ("Article accepted for publication in PNAS"); the published version could not be downloaded (section 8.3). Issue #72. | `rf16_moussaid2011_excerpts.txt` (tracked: every cited passage, with its line number in the full extract). The full PDF and text, `rf16_moussaid2011_arxiv.pdf` and `.txt`, are local only: arXiv's non-exclusive licence is not an open one (`.gitignore`). |
| Rio et al. 2018 | K. W. Rio, G. C. Dachner, W. H. Warren, "Local interactions underlying collective motion in human crowds", *Proc. R. Soc. B* 285(1878): 20180611, 2018. DOI 10.1098/rspb.2018.0611. **Abstract only**, through the Europe PMC API (PMID 29769363). Issue #72. | `rf16_rio2018_abstract.txt` |
| Wirth et al. 2023 | T. D. Wirth, G. C. Dachner, K. W. Rio, W. H. Warren, "Is the neighborhood of interaction in human crowds metric, topological, or visual?", *PNAS Nexus* 2(5): pgad118, 2023. DOI 10.1093/pnasnexus/pgad118. **Abstract only**, through the Europe PMC API (PMID 37200800). Issue #72. | `rf16_wirth2023_abstract.txt` |
| Pearsons et al. 1977 | K. S. Pearsons, R. L. Bennett, S. Fidell, *Speech Levels in Various Noise Environments*, EPA-600/1-77-025, U.S. Environmental Protection Agency, May 1977. A U.S. government report. Issue #73. | `rf17_pearsons1977_epa.txt` (pypdf 5.1.0 text of the scan at `nonoise.org/epa/Roll2/roll2doc16.pdf`; the scan itself is local only) |
| ISO 9921-1:1996 | ISO 9921-1:1996, *Ergonomic assessment of speech communication, Part 1: Speech interference level and communication distances for persons with normal hearing capacity in direct communication (SIL method)*. Withdrawn; replaced by ISO 9921:2003. **Read in the free preview** published by iTeh Standards. Issue #73. | `rf17_iso9921_1_1996_excerpts.txt` (tracked); the preview is local only (copyright ISO) |
| Watt et al. 2007 | R. Watt, B. Craven, S. Quinn, "A role for eyebrows in regulating the visibility of eye gaze direction", *Quarterly Journal of Experimental Psychology* 60(9), 1169–1177, 2007. DOI 10.1080/17470210701396798. Read in the accepted manuscript (University of Stirling, STORRE hdl 1893/1679). Issue #73. | `rf17_watt2007_excerpts.txt`, `rf17_watt2007_fig4.png` (tracked); the manuscript is local only |
| De Bruyn & Orban 1988 | B. De Bruyn, G. A. Orban, "Human velocity and direction discrimination measured with random dot patterns", *Vision Research* 28(12), 1323–1335, 1988. DOI 10.1016/0042-6989(88)90064-8. **Abstract only**, through the Europe PMC API (PMID 3256150). Issue #73. | `rf17_debruyn1988_abstract.txt` |
| Gurnsey et al. 2010 | R. Gurnsey, G. Roddy, N. F. Troje, "Limits of peripheral direction discrimination of point-light walkers", *Journal of Vision* 10(2):15, 2010. DOI 10.1167/10.2.15. **Abstract only**, through the Europe PMC API (PMID 20462316). Issue #73. | `rf17_gurnsey2010_abstract.txt` |
| Mateeff et al. 2000 | S. Mateeff, G. Dimitrov, B. Genova, L. Likova, M. Stefanova, J. Hohnsbein, "The discrimination of abrupt changes in speed and direction of visual motion", *Vision Research* 40(4), 409–415, 2000. DOI 10.1016/s0042-6989(99)00185-6. **Abstract only**, through the Europe PMC API (PMID 10820621). Issue #73. | `rf17_mateeff2000_abstract.txt` |
| Dachner et al. 2022 | G. C. Dachner, T. D. Wirth, E. Richmond, W. H. Warren, "The visual coupling between neighbours explains local interactions underlying human 'flocking'", *Proc. R. Soc. B* 289(1970): 20212089, 2022. DOI 10.1098/rspb.2021.2089. CC BY 4.0; full text through the Europe PMC API (PMC8889174). Issue #73. | `rf17_dachner2022_pmc.txt` |

## 7. What is missing

- **Weidmann's 1.34 m/s**, the usual citation for free walking speed, was not obtained in
  any form. Menge uses that number without citing it. The preferred speed here rests on
  Moussaïd et al. instead.
- **Nothing is from Singapore.** Phase 1 of the project was Singapore-only. The walking
  speed and the corridor are from France and the body widths from Japan. A Singaporean
  anthropometric or gait source was not looked for in this sub-issue.
- **The samples are small.** The radius comes from four young men; the widths by gender
  from nine people; the backing speeds from ten young adults, nine of them men (issue #32).
  No backward walking speed of older people was read, so the slow backer's 0.43 m/s is young
  adults walking slowly on purpose, not an older person's pace.
- **The body is a disc.** Its radius is half a shoulder width, so it is as deep as it is
  wide, which a person is not, and it cannot turn sideways (section 3).
- **The ORCA settings are borrowed from practice**, not fitted to data: `time_horizon_obst`
  and `max_neighbours` are what one simulator's example uses.

## 8. What an LLM agent perceives: the values of the resolution design (issue #72)

The description an LLM agent is given (`resolution.md`, D2) says whom it can see, in how much
detail, and whom it can hear. These values shape **only what the LLM is told** (D10). ORCA's
neighbour search keeps the `sensing_radius` and `max_neighbours` of section 2, and the
perception record that rules read is unchanged. The same tags apply as in the table at the top.
The config keys of `llm_view_v1.yaml` are in backticks; `negsim/resolution/perceive.py` reads
them (`LLMViewSettings`), and `tests/test_perceive.py` checks that every key is tagged, that
none is a placeholder, and that section 8.4 gives each researched value. In the locators of `rf16_moussaid2011_excerpts.txt`, a number in square brackets is a line of the full text extract, as the excerpt file prints it.

### 8.1 Cited values

| Parameter | Value | Status | Source and locator | What the source measured, and the caveat |
|---|---|---|---|---|
| View half-angle (`half_angle_deg`) | 75° each side of straight ahead (150° in total) | cited | Moussaïd et al. 2011, Fig. 2 caption; `rf16_moussaid2011_excerpts.txt`, [555]-[562] | "The model parameters are τ=0.5s, φ=75°, dmax=10m, k=5.103, vi0=1.3 m/s". φ is a half-angle: "the vision field of pedestrian i ranges to the left and to the right by φ degrees with respect to the line of sight" ([134]-[140]). **A model's parameter, not a measured limit of vision**: it is the value with which the authors' simulations matched the corridor experiments of Moussaïd et al. 2009 (the same 7.88 m by 1.75 m corridor, [548]-[555]). The same paper uses **φ=45°** for its high-density street simulations ([597]-[601]). |
| Seeing range (`range_m`) | 10 m | cited | same; [559] | dmax, "the 'horizon distance' of pedestrian i" ([163]-[164]): the distance assumed when nothing is in the way. Same caveat: a model's parameter, and **8 m** in the high-density simulations ([601]). |
| Who is hidden (`occlusion`) | not described if hidden behind someone nearer: the straight line from the agent's centre to the other's passes through a nearer person's disc | cited | same, Fig. 1 caption; [542]-[543] | "Pedestrian p4 is hidden by pedestrian p2 and, therefore, not visible." The model "correctly handles situations in which pedestrians are hidden or outside the field of view" ([339]-[340]). A modelling choice the authors argue for, not a measurement. |
| Detail range (`detail_range_m`) | 5 m | cited | Rio et al. 2018, abstract; `rf16_rio2018_abstract.txt:20-22` | The neighbourhood is modelled with "weights that decay exponentially to zero by 5 m". **Two caveats.** It was measured with "a participant walked in a virtual crowd whose speed and heading were manipulated" (lines 17-18): following a crowd, not avoiding someone coming the other way. And the same model is "a circularly symmetric region", in which influence decreased "with distance, but not with lateral position (eccentricity)" (lines 18-19): it supports the 5 m, **not** the cone. Here it decides how much is said about a person, not whether they are seen. |
| How many people are described (`max_people`: null) | everyone visible, no fixed count | cited | Wirth et al. 2023, abstract; `rf16_wirth2023_abstract.txt:19-23` | "Our results rule out a topological neighborhood" (a fixed number of nearest neighbours), "are approximated by a metric neighborhood, but are best explained by a visual neighborhood", in which "an individual is influenced by the optical motions of all visible neighbors" (lines 19-20). Real and virtual crowds, with density manipulated (lines 20-21). |

### 8.2 Placeholders

Issue #73 first set the hearing range (7 m), the distance band of an unseen speaker (3 m), the
eye-contact range (4 m) and D5's change thresholds (0.2 m sideways, 0.2 m/s, 5°) as placeholders.
At the user's request (2026-10-23) each was replaced by a sourced value before any run read it:
section 8.4. One placeholder of the resolution design was left, and issue #58 (RF-3) added three for the encounter protocol. None of these has a source. **Do not report a result that depends on one as if it rested on
data.** Issue #60 (RF-5) added three more, for the factors that act outside the prompt: section 8.7.

| Parameter | Value | Why it has no source, and what would replace it |
|---|---|---|
| Largest turn in a reply (`turn.degrees`) | 0° to 90° `[placeholder]` | Issue #57 (RF-2): the reply parser refuses a turn beyond it (`negsim/resolution/reply.py`, `MAX_TURN_DEGREES`), and the step format tells the agent the range. 90° is walking straight sideways, the most a heading offset can mean; nothing read says how far people turn to pass. A source on avoidance heading changes would replace it. |
| How fast a message is said (`protocol.speech_words_per_second`) | 2.5 words a second `[placeholder]` | Issue #58 (RF-3): D3 says speaking takes simulated time; a message is heard `len(words) / 2.5` s after its decision point. 2.5 words a second (150 a minute) is a commonly quoted conversational rate, but no source on it has been read or cached. A measured speech rate, ideally for short utterances in public, would replace it. |
| How long without a predicted conflict ends an encounter (`protocol.no_conflict_end_s`) | 1 s `[placeholder]` | Issue #58, task 4 ("no conflict has been predicted for 1 s `[placeholder]`"). Shorter ends encounters on a momentary gap in the prediction; longer keeps prompting after the two are clear. Nothing measures it. |
| The reply cap (`llm.max_tokens`) | 400 tokens `[placeholder]` | Issue #58, task 7 ("the reply cap at 400 tokens `[placeholder]`, as in #30's config"). It bounds the cost preview (`encounter-protocol.md`, section 6); RF-9's pilot measures how long replies are. |

### 8.3 Design values

Tagged `[design]`: choices about cost and prompting, not claims about people.

| Parameter | Value | Why |
|---|---|---|
| Gap between two prompts of one agent | at least 1 s | `resolution.md`, D5: keeps an agent from being asked again for every small change. |
| Decision points per agent per encounter | at most 3 (1 in the independent condition) | D3 and D5: a cost limit. |
| Cap on people prompted in one encounter | only if needed | D11 and D12: a cost limit for scenes with more than two people (rounds 4 and 6), not a human number; the report says how often it is reached. |
| What "you would meet Person 1 in about t s" means | the time of closest approach at the current velocities, `-(r·v)/(v·v)` | Issue #57 (RF-2), `negsim/resolution/adapter.py`: defined even when the two would pass each other without touching, unlike a time to collision; stated only for a person in view who is getting closer. From the running simulation (issue #73), only for the encounter partner, and only when that closest approach is nearer than the encounter's safety distance: the two radii and the scenario's `single_file.safety_margin`, as the conflict zone counts it. |
| Walls block sight (`walls_block_sight`) | on | Issue #73: someone behind a wall is not seen, with the same segment-through-rectangle test as the world's (`architecture.md`, DD8). A switch, because a scene may have walls low enough to see over. |
| Where a person faces | their direction of travel; when standing still or walking backwards, the direction their path takes where they are | Issue #73 (`negsim/resolution/perceive.py`). The simulator turns a disc to face its velocity, which for someone backing out of a passage is the wrong way; a person waiting to go on is taken to face the way they are going. The view cone is centred on it. |
| What "moved over to your left" means | where the other is now lies at least `direction_deg` (2°, section 8.4) off the straight line they were walking along when the agent last looked, counting only the part of the offset across the agent's own left and right | Issue #73. Someone crossing at a steady angle has not "moved over"; someone who steps aside has. No source gives a noticeable sideways shift in metres, so the direction threshold is used: the offset is a change in the direction from their old position to their new one. |
| Where a voice came from | ahead within 45° of where the listener faces, behind within 45° of the opposite way, otherwise to the left or right | Issue #73: four quarters, a rough direction as the issue asks. As it was when the words were said. |
| Who `max_people` keeps | the nearest, and always the encounter partner | Issue #73: off by default. When set, the view records how many it left out (`labels["people_left_out"]`), so a report can count how often the cap is reached. |

### 8.4 What an agent hears, and what it notices (issue #73)

Researched for issue #73 at the user's request (2026-10-23), to replace the placeholders that issue
first shipped. Locators are lines of the cached files in `refs/` (a number in square brackets is a
line of the full extract, as an excerpt file prints it).

| Parameter | Value | Status | Source and locator | What the source measured, and the caveat |
|---|---|---|---|---|
| Hearing range (`hearing_range_m`) | 3.2 m | derived | Pearsons, Bennett & Fidell 1977, Table I, `rf17_pearsons1977_epa.txt:1090`; Table II, `:1146`; conclusion 2(f), `:266-268`. ISO 9921-1:1996, eq. (3), `rf17_iso9921_1_1996_excerpts.txt` [456]-[462], and note 5, [492]-[496] | **Arithmetic.** Speech falls 6 dB per doubling of distance (ISO 9921-1 eq. (3): L(r) = L(1 m) − 20 lg r). It is understood while it is no quieter than the background: Pearsons et al. found 94% of sentences understood at a speech-to-background ratio of 0 dB. So r = 10^((L_speech − L_background)/20) = 10^((64 − 54)/20) = 3.16 m, rounded to 3.2 m. **Inputs:** a *raised* voice, 64 dB at 1 m (Table I, the average of men 65, women 63 and children 65, about 100 talkers in an anechoic chamber), because a message is meant to reach someone the speaker is not already talking with (an assumption); the background of a *public indoor place*, 54 dB (Table II, department stores, the only public place measured). **Caveats.** The range depends steeply on the background: in a quiet home (45 dB) the same voice carries about 9 m, in a train (74 dB) 0.3 m, so RF-5's `surroundings` factor should set the background (`resolution.md`, D12). The 94% was measured in a 70 dB ambient. The 6 dB rule holds indoors up to about 2 m, and up to 8 m when the reverberation time is under 2 s (ISO note 5); in small rooms speech stays nearly constant beyond 1 m (Pearsons, `:209-213`), so indoors the range is if anything longer. All talkers were American, in the 1970s. |
| "Close by" for an unseen speaker (`heard_close_m`) | 1.0 m | cited | Pearsons et al. 1977, conclusion 2(d), `rf17_pearsons1977_epa.txt:254-260` | In ambient levels up to 45 dB, as in homes, the distance people talked at averaged 1 m; above 70 dB it fell to 0.4 m. The distance people choose to talk at is taken as "close by". It was measured in homes; the department stores' distance was not reported. Nothing read measures how well people judge the distance of a voice. |
| Eye-contact and nod range (`eye_contact_range_m`) | 10 m (all of the seeing range) | derived | Watt, Craven & Quinn 2007, Fig. 4, `rf17_watt2007_fig4.png`; text, `rf17_watt2007_excerpts.txt` [139]-[141], [162], [202], [204]-[212] | Observers judged whether a face looked 4° left or right of them; the "critical distance" is where they were still right 84% of the time. Read off Fig. 4: with neutral eyebrows about 12 to 14 m for a 0.1 s glance and about 18 to 25 m for 0.5 s; with lowered eyebrows about 8.5 m at 0.1 s. Experiment 1 gives about 15 m for 1 s and about 8 m for 20 ms ([139]-[141]). **Every neutral-eyebrow value exceeds the 10 m seeing range**, so eye contact can be seen anywhere in view; the value is capped at `range_m`. **Caveats:** two observers per experiment, photographs on a monitor scaled to stand for distance, in good light. **A nod has no source**; it moves the whole head, so it is taken to be at least as visible as a 4° eye turn (an assumption). |
| Speed change (`change_thresholds.speed_fraction`) | 7% of the earlier speed | cited | De Bruyn & Orban 1988, abstract, `rf17_debruyn1988_abstract.txt:19-20` | Speed discrimination thresholds (84% correct, staircase) were about 7% of the speed at the optimal speeds, 4 to 64 deg/s. At 1.3 m/s that is 0.09 m/s. **Caveats:** random-dot patterns on a screen, not a walker; a person coming head-on changes speed mostly in depth, which this did not test. Comparing two speeds 1 s apart, as D5 does (at least 1 s between prompts), is if anything easier than comparing them back to back (Mateeff et al. 2000, `rf17_mateeff2000_abstract.txt:14-19`). |
| Direction change, and moving over (`change_thresholds.direction_deg`) | 2° | cited | Gurnsey, Roddy & Troje 2010, abstract, `rf17_gurnsey2010_abstract.txt:16`; De Bruyn & Orban 1988, `rf17_debruyn1988_abstract.txt:25-26` | Gurnsey et al.: the smallest deviation of a point-light walker's heading from straight towards the observer that can be detected, between 1 and 2 degrees at large sizes; the upper end is used. De Bruyn & Orban: 1.8° for the direction of moving dots. Used for "turned" and for "moved over" (section 8.3). **Caveat:** thresholds of attentive observers in a laboratory. |

**These are thresholds of perception, not of reaction.** In experiments on following, the
Warren lab perturbs a neighbour's heading by ±10° and speed by ±0.3 m/s (Dachner et al. 2022,
`rf17_dachner2022_pmc.txt:270`), sizes that reliably produce a response. A change between the
perceptual threshold and those sizes may be noticed without being acted on. D5 asks whether
something noticeable happened, so the perceptual thresholds are used; the 1 s gap and the cap of
three decision points (D5) limit how often an agent is prompted again.

**Not read:** the published PNAS version of Moussaïd et al. 2011 (its PMC full text is not
available for download, and Europe PMC's PDF route refused the request, 403); the full texts of
Rio et al. 2018 and Wirth et al. 2023. The values above were checked in the accepted
manuscript and in the two abstracts.

### 8.5 Carrying out a plan (issue #59)

Tagged `[design]`: definitions of what a step in a reply means physically, and of the outcome
columns. None is a claim about people, and none has a source. `negsim/resolution/execute.py`,
`scenarios/passing.py` and `outcomes.py` hold them.

| Parameter | Value | Why |
|---|---|---|
| A step's speed when it gives none | the agent's own speed (its preferred speed, under the run's directives) | D1 makes `speed_mps` optional. A step that only turns is read as "turn, and keep walking". |
| Which way a turn is measured from | the desired path direction: toward the point `lookahead` metres further along the path, as plain ORCA aims | The issue: "offsets the preferred direction from the desired path direction". Held for the step, so an agent that has moved off its path still turns from the way back to it. |
| Which way a back-up step backs | against the path's direction where the agent is, at its `backing_speed`, its distance measured along that direction from where the step began | The simulator's own back-up manoeuvre (issue #32) backs along a passage's axis. A plan's back-up can happen anywhere, so the path is the only axis there is. A back-up step that also has an `until` ends at whichever comes first. |
| When a back-up step has backed far enough | within 1 mm (`BACKED_UP_EPS_M`) | The same tolerance as the simulator's back-up manoeuvre (`BACK_UP_REACHED_M`). |
| When the plan is in force | from its decision, including any delay before its first step | In `plan_only`, ORCA leaves the two to their plans from the decision on. Otherwise ORCA would steer them during a delayed start and get the credit. |
| The arbiter in each mode | lifted in `plan_only`, kept in `plan_orca` | The arbiter's speed bound also keeps the two apart, so `plan_only` lifts it as well as ORCA's avoidance. `plan_orca` runs everything of the plain run on top of the plan. |
| When the encounter is handed back to ORCA (`plan_only`) | when the protocol releases it, one of the two arrives, or the two have passed each other (separating, and further apart than the two radii and the safety margin) with no plan of theirs left to run | D6: "ORCA then takes over" once the encounter is not resolved by the LLM. After the pass, ORCA has nothing to do between the two. |
| `other_stops` | the partner's speed is below 0.01 m/s | The issue's number: the deadlock monitor's `speed_eps`. |
| `other_passes` | the partner is behind the agent (behind its path direction) and the distance is growing; or the partner has arrived; or, for the one overtaken, the partner was behind when the step began and is now ahead, with the distance growing | The issue's definition, plus the last case: without it, the person being overtaken would never see the other pass. **Known limit:** for the person ahead, an overtaker who gives up and drops back is "behind and getting further", so the event fires. |
| `i_am_out_of_the_stretch` | the agent has been inside a single-file segment since the step began, and now is not, by either end | "From the passage fields": inside means the centre is in the segment's free space, as the perception record's `in_segment` counts it. Backing out and walking through both count. An agent that is never inside one never gets out of one. |
| The conflict zone of a passing encounter | the shared single-file segment, left at the far end by the two radii and the safety margin (as the arbiter's `first_out`); in a corridor wide enough to pass, a disc of radius the two radii plus the safety margin round the midpoint of the two at their closest approach | Gives "who passed first" and "time to clear". In a wide corridor two people who pass side by side leave the disc on the same step: `together`. |
| `passing_side` | the side the agent went by on, in its own frame, at the closest approach, if the two were abreast then (along-path offset within the two radii) | Empty when they were not side by side, as in a passage they go through one at a time. |
| `stopped`, `backed_up` | speed below the deadlock monitor's `speed_eps`; moving against its path faster than the backward-walking threshold, 0.1 m/s (`metrics.md`, section 10) | Thresholds already in the run, reused so that no new number is added. In the passage cases that start at rest, both agents count as stopped from the start. |
| "Resolved" (passing scenarios) | both left the conflict zone, with no collision, no near miss (`near_miss_distance`) and no deadlock, before the run's time limit | The issue's definition. A plain ORCA pass within 0.1 m is a near miss, so it is not resolved. |

### 8.6 The encounter protocol (issue #58)

Tagged `[design]` unless they are in section 8.2: when an agent is asked, what its reply does,
and when an encounter ends. None is a claim about people; several are assumptions to review
(`WORK_LOG-58.md`). `negsim/resolution/protocol.py` and `scenarios/` hold them;
`encounter-protocol.md` explains each in context. The gap between prompts, the cap of three
decision points and the cap on prompted people are in section 8.3.

| Parameter | Value | Why |
|---|---|---|
| When a conflict is predicted (passing scenarios) | a shared too-narrow single-file segment whose zone is still live; or, not yet passed, a closest approach still to come nearer than the two radii and the safety margin at the present velocities **or** the desired ones (along the path, at the preferred speed) | "The existing detector plus approaching" (issue #58, task 1): the arbiter's own zone for passages, and the time-to-meet line's safety distance in a corridor. The desired velocities keep two people who have both stopped face to face in conflict. The trigger also needs the distance to be shrinking (D4). |
| Who a crowd encounter holds (`passing_crowd`) | the two who started it, then everyone still walking within 10 m of either and predicted in conflict with either, nearest first | Only to rehearse more than two prompted people (D11) before rounds 4 and 6. 10 m is the seeing range (section 8.1). The cap keeps the first N. |
| A member's first prompt | when D4 holds for it toward any member; its partner is the nearest such member | Issue #58 says every member is prompted at the first decision point; D4 says one is prompted only if it perceives the other. Read together: everyone who perceives is asked then, and anyone else when they first do. |
| A plan that has "ended" (D5) | a plan with at least one step, all carried out | `[]` means "carry on as I am": treating it as ended would ask the agent again a second later. |
| An unreadable reply (after its retry) | uses up the decision point; the agent carries on with its plan, or with `[]` if it had none; its look is dropped from its perception | `[]` keeps the encounter under `plan_only`, so ORCA never steps in for an unreadable reply. Dropping the look keeps WHAT YOU HAVE DONE SO FAR to decisions the agent made. |
| When a signal is made | during the step after the decision point | Everyone at a decision point looks first and replies after, so a signal made there must be new to the others at their next look; RF-17's view counts what came after a look. |
| When a message is heard | `len(words) / speech_words_per_second` after its decision point, by everyone within the hearing range then | D3: speaking takes simulated time. The rate is a placeholder (section 8.2). |
| "Passed" as an encounter's end | every conflict pair separating, further apart than the two radii and the margin, **and** no conflict predicted between them (or one has arrived) | RF-4's pass test alone reads two people standing still as separating when a rounding error makes their relative velocity point apart (found on the passage case). |
| When ORCA takes over (D6) | every prompted member has used its decision points (or arrived) and has no plan left to carry out, while a conflict is still predicted | "Still unresolved after its last decision point": the last decision point has played out. The release is recorded so the replay repeats it. |
| `not_resolved_by_llm` | the end was `orca_took_over`, `deadlock` or `collision`, or the time limit with a conflict still predicted | The encounter ended without the LLM agents' plans resolving it. |
| `resolved_by_llm` | `resolved_plan_only` and not `not_resolved_by_llm` | The `plan_only` replay runs on after ORCA takes over, so its physical "resolved" can be ORCA's work; this column credits the LLM only. |
| The plan coding (`code_plan`) | `side`: the sign of its turns (`none`, `left`, `right`, `both`); `slowed`: a speed below the agent's speed at the decision; `stopped`: a speed of 0; `backed_up`: a back-up step; `start_distance_m`, `start_after_s` | Issue #58, task 9: "coded mechanically". |

### 8.7 The core and situational factors (issue #60)

`configs/resolution/factors_v1.yaml` holds the numbers of the two factors that act outside the
prompt; `negsim/resolution/factors.py` reads them (`FactorValues`). Every one is a placeholder.
**Do not report a result that depends on one as if it rested on data.** Every other core and
situational factor exists only in the prompt: the simulator does not slow a person with a cane,
narrow the view of one looking at a phone, or fill a busy place with people.

| Parameter | Value | Why it has no source, and what would replace it |
|---|---|---|
| How much wider a person pulling a large suitcase is (`load.large_suitcase.width_added_m`) | 0.2 m `[placeholder]` | Task 3: "a sourced value if `docs/parameters.md` has one, otherwise a placeholder". None was found in the repository or its references. A disc cannot have a suitcase behind it, so a disc 0.2 m wider (0.50 m to 0.70 m with the shipped pedestrian) stands in for the body and the suitcase: it overstates the width beside the person and leaves out the length behind them. Fixed for the whole run (D1). A measured width of pedestrians with wheeled luggage, as they walk, would replace it. Issue #32's eight passage cases start the pair 0.1 m apart, so with 0.2 m added they overlap or touch, and a design with `load` is refused on them (no loaded body may start within the near-miss distance). The user chose new cases over a smaller width: `rf5_passage_v1` starts the pair 0.3 m apart (`cases.md`, section 9). The 4 head-on and 3 overtaking cases fit. |
| Hearing range when it is quiet (`surroundings.quiet.hearing_range_m`) | 8.9 m `[placeholder]` | The arithmetic of section 8.4 with a background of 45 dB, which Pearsons et al. 1977 call typical of homes (conclusion 2(d), `rf17_pearsons1977_epa.txt:254-260`; Table II gives 41 dB inside suburban homes, `:1143`; its inside-urban value is unreadable in the scan, `:1142`): 10^((64 − 45)/20) = 8.9 m. The inputs are cited; that a quiet public place is as quiet as a home is an assumption, so the value is a placeholder. A measured background level of the kind of place a scenario stands for would replace it. |
| Hearing range when it is busy (`surroundings.busy.hearing_range_m`) | 3.2 m `[placeholder]` | `llm_view_v1.yaml`'s value: the same voice against a department store's 54 dB (Table II, `:1146`), section 8.4. That a busy place is as loud as a department store, and no louder, is an assumption. The trains of Table II (74 dB, `:1147`) would give 0.3 m. |

Tagged `[design]`: how the factors are coded and shown. None is a claim about people.

| Parameter | Value | Why |
|---|---|---|
| The coding of a core factor | `neither` (both people at the base level) or `p1` (person 1 at the other level, person 2 at the base); `mapping` balances which agent is person 1 | Task 5. For `assertiveness` and `residence`, whose base level also has a line, `neither` means both give way, or both live in Singapore. |
| `urgency` | the two-level form of #30's `task`: `neither` is two routine errands, `p1` person 1's urgent one; a design has one or the other | Task 1: "formalise it as a two-level factor rather than adding a duplicate". `task`'s level `none` gives no errand at all, so it varies having an errand as well as its urgency; `urgency` varies only the urgency. |
| A visibility switch left out of a design | on | An observable factor is seen unless the design says otherwise, as age and gender are. |
| Which situational factors | `surroundings` and `time_of_day` | The session's choice (task 7), with the reasons in `WORK_LOG-60.md`: `surroundings` is the one that also acts on the talk condition (the hearing range); `time_of_day` changes nothing physical and tests whether the setting moves a decision. `companion` was not taken: the simulator moves one disc, so "walking with a friend" would describe a body and a pair the replay does not have. Two slots of the 16 are left for each round's own factors. |
| Where an observable factor is seen | under the person in WHO YOU CAN SEE, in full detail only (within 5 m) | D2: from 5 to 10 m a person gets one short line. So someone with a cane 8 m away is described without it. |
| What a switched-off `load` hides | the words, not the width | The body is as wide as it is, and WHO YOU CAN SEE gives every person's width. |
