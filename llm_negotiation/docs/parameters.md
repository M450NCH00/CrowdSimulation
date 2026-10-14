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

## 1. The agent type

One agent type, `pedestrian`, is used by all five scenarios, with identical values
(tested: `test_every_shipped_scenario_uses_the_same_pedestrian`), so that a difference
between scenarios is not a difference between the bodies walking through them.

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
| `width` and `length` of `bidirectional_flow` | 4.0 m, 50.0 m | cited | Moussaïd et al. 2009, Sec 2(c); `si1_moussaid2009_pmc.txt:109` | "Simulations of bidirectional flows were conducted in a 6×50 m street with the pedestrians of each flow starting from the central, 4 m wide area". That is the authors' *simulation* of a street they had filmed, in which the outer metre on each side was taken up by people standing at shop fronts. Here the central 4 m is a corridor with walls. |

## 3. Placeholders

Three quantities in the shipped scenarios are `[placeholder]`. Nothing else is.

| Scenario | Parameter | Value | Why it has no source, and what would replace it |
|---|---|---|---|
| `corridor_to_bottleneck` | `bottleneck_width` | 0.8 m `[placeholder]` | The scenario needs a width that only one agent can use at a time. For two discs 0.5 m across that is anything under 1.0 m, and 0.8 m is the hallway width of issue #24. **It is not a width at which real people cannot pass.** The one source read on this, Yamamoto et al. 2019, had pairs pass each other at widths down to 60 cm by turning their bodies (Sec 3, lines 344–345; "the males did not need to rotate for W = 100 cm in most cases", line 1282). Discs cannot turn sideways. A sourced value would need either a model of the body that can, or a segment narrow enough that people do not try. |
| `corridor_to_bottleneck` | `bottleneck_length` | 4.0 m `[placeholder]` | The hallway length of issue #24, itself a placeholder. No source was looked for: any length makes the segment single-file. |
| `bidirectional_flow` | `spawn_spacing` | 1.0 m `[placeholder]` | The spacing of the lattice the two crowds start on, which sets their starting density (about one person per square metre). Round, and not taken from the street observation the corridor's size comes from, whose density was not read. |

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
| `wall_clearance`, `wall_thickness` | 0.5 m | Where the lattice starts, and how walls are drawn. Wall thickness has no effect on the motion. |
| `lookahead` | 2.0 m (0.6 m in the bottleneck) | How far ahead on its path an agent aims. Shorter where the path has corners. |
| `cell_size` | 2.0 m | Grid cell of the neighbour search. No effect on the result. |
| `safety_margin` of `single_file` | 0.1 m | As in issue #24. |
| `deadlock` window and speed | 3.0 s, 0.01 m/s | As in issue #24. |
| Metric thresholds: `near_miss_distance`, `yield_speed_fraction`, `yield_min_duration`, `exposure_eps` | 0.1 m, 0.5, 1.0 s, 1e-6 m/s | Definitions, not measurements. They decide what gets *counted*, so `metrics.md` records them and every outcome file repeats them. None has a source. |
| `seed` | 26 | Of the starting jitter. |

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

## 7. What is missing

- **Weidmann's 1.34 m/s**, the usual citation for free walking speed, was not obtained in
  any form. Menge uses that number without citing it. The preferred speed here rests on
  Moussaïd et al. instead.
- **Nothing is from Singapore.** Phase 1 of the project was Singapore-only. The walking
  speed and the corridor are from France and the body widths from Japan. A Singaporean
  anthropometric or gait source was not looked for in this sub-issue.
- **The samples are small.** The radius comes from four young men; the widths by gender
  from nine people.
- **The body is a disc.** Its radius is half a shoulder width, so it is as deep as it is
  wide, which a person is not, and it cannot turn sideways (section 3).
- **The ORCA settings are borrowed from practice**, not fitted to data: `time_horizon_obst`
  and `max_neighbours` are what one simulator's example uses.
