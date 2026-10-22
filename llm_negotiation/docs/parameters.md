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
They are in no config yet; RF-17 (#73) will put them in one, with these tags.

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
perception record that rules read is unchanged. The same tags apply as in the table at the top. In the locators of `rf16_moussaid2011_excerpts.txt`, a number in square brackets is a line of the full text extract, as the excerpt file prints it.

### 8.1 Cited values

| Parameter | Value | Status | Source and locator | What the source measured, and the caveat |
|---|---|---|---|---|
| View half-angle | 75° each side of straight ahead (150° in total) | cited | Moussaïd et al. 2011, Fig. 2 caption; `rf16_moussaid2011_excerpts.txt`, [555]-[562] | "The model parameters are τ=0.5s, φ=75°, dmax=10m, k=5.103, vi0=1.3 m/s". φ is a half-angle: "the vision field of pedestrian i ranges to the left and to the right by φ degrees with respect to the line of sight" ([134]-[140]). **A model's parameter, not a measured limit of vision**: it is the value with which the authors' simulations matched the corridor experiments of Moussaïd et al. 2009 (the same 7.88 m by 1.75 m corridor, [548]-[555]). The same paper uses **φ=45°** for its high-density street simulations ([597]-[601]). |
| Seeing range | 10 m | cited | same; [559] | dmax, "the 'horizon distance' of pedestrian i" ([163]-[164]): the distance assumed when nothing is in the way. Same caveat: a model's parameter, and **8 m** in the high-density simulations ([601]). |
| Who is hidden | not described if hidden behind someone nearer | cited | same, Fig. 1 caption; [542]-[543] | "Pedestrian p4 is hidden by pedestrian p2 and, therefore, not visible." The model "correctly handles situations in which pedestrians are hidden or outside the field of view" ([339]-[340]). A modelling choice the authors argue for, not a measurement. |
| Detail range | 5 m | cited | Rio et al. 2018, abstract; `rf16_rio2018_abstract.txt:20-22` | The neighbourhood is modelled with "weights that decay exponentially to zero by 5 m". **Two caveats.** It was measured with "a participant walked in a virtual crowd whose speed and heading were manipulated" (lines 17-18): following a crowd, not avoiding someone coming the other way. And the same model is "a circularly symmetric region", in which influence decreased "with distance, but not with lateral position (eccentricity)" (lines 18-19): it supports the 5 m, **not** the cone. Here it decides how much is said about a person, not whether they are seen. |
| How many people are described | everyone visible, no fixed count | cited | Wirth et al. 2023, abstract; `rf16_wirth2023_abstract.txt:19-23` | "Our results rule out a topological neighborhood" (a fixed number of nearest neighbours), "are approximated by a metric neighborhood, but are best explained by a visual neighborhood", in which "an individual is influenced by the optical motions of all visible neighbors" (lines 19-20). Real and virtual crowds, with density manipulated (lines 20-21). |

### 8.2 Placeholders

None of these has a source. **Do not report a result that depends on one as if it rested on
data.**

| Parameter | Value | Why it has no source, and what would replace it |
|---|---|---|
| Hearing range | `[placeholder]`, no value yet | How far speech carries. It should depend on RF-5's `surroundings` factor (a quiet corridor against a busy station). RF-17 (#73) sets a value; a source on speech audibility against background noise would replace it. |
| Eye-contact and nod range | `[placeholder]`, no value yet | How far away a signal (`eye_contact`, `nod`, and the rest of D1's list) can be seen. Within the seeing range by definition; nothing read gives a distance for eye contact. |
| Change thresholds of D5 ("noticeably") | 0.2 m sideways, 0.2 m/s, 5° `[placeholder]` | What counts as the other having changed speed or direction noticeably, which can prompt an agent again. Round values. A source on the smallest change in another walker's speed or heading that people react to would replace them. |
| Largest turn in a reply (`turn.degrees`) | 0° to 90° `[placeholder]` | Issue #57 (RF-2): the reply parser refuses a turn beyond it (`negsim/resolution/reply.py`, `MAX_TURN_DEGREES`), and the step format tells the agent the range. 90° is walking straight sideways, the most a heading offset can mean; nothing read says how far people turn to pass. A source on avoidance heading changes would replace it. |

### 8.3 Design values

Tagged `[design]`: choices about cost and prompting, not claims about people.

| Parameter | Value | Why |
|---|---|---|
| Gap between two prompts of one agent | at least 1 s | `resolution.md`, D5: keeps an agent from being asked again for every small change. |
| Decision points per agent per encounter | at most 3 (1 in the independent condition) | D3 and D5: a cost limit. |
| Cap on people prompted in one encounter | only if needed | D11 and D12: a cost limit for scenes with more than two people (rounds 4 and 6), not a human number; the report says how often it is reached. |
| What "you would meet Person 1 in about t s" means | the time of closest approach at the current velocities, `-(r·v)/(v·v)` | Issue #57 (RF-2), `negsim/resolution/adapter.py`: defined even when the two would pass each other without touching, unlike a time to collision; stated only for a person in view who is getting closer. |

**Not read:** the published PNAS version of Moussaïd et al. 2011 (its PMC full text is not
available for download, and Europe PMC's PDF route refused the request, 403); the full texts of
Rio et al. 2018 and Wirth et al. 2023. The values above were checked in the accepted
manuscript and in the two abstracts.
