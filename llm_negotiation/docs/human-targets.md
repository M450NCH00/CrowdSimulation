# Human targets: rules, plain ORCA and Step 1's agents against published studies (issue #122, RF-37)

The track's goal, stated by the user on 2026-10-30: **resolve conflicts in a way accurate to human
behaviour**, in crowds of 10,000 agents or more. Before this layer, no measure checked that:

- RF-18's "helps" counts severe conflicts, throughput and delay, which is efficiency;
- RF-31's identity check measures agreement with the LLM agents, who are not the reference;
- RF-14 grades rules in words.

This layer turns RF-14's cached evidence into **targets with sources and tolerances**, and measures
every rule arm, plain ORCA and Step 1's own agents against them.

    python run_experiment.py configs/rule_set_evaluation/rf37_head_on.yaml        # pairs matched to the studies
    python run_experiment.py configs/rule_set_evaluation/rf37_flow_density.yaml   # the flow at two more sizes
    python -m negsim.human_targets.report                                           # runs/rf37_human_targets/

Code: `negsim/human_targets/` (`targets.py`, `measures.py`, `judge.py`, `report.py`). No model is called.

## 1. The targets file

`configs/human_targets/head_on_v1.yaml` is frozen: a change of any value, tolerance or source is a
new file (`head_on_v2.yaml`), never an edit. The test pins its hash.

Under #55's decision 6 (published studies only), every target comes from a number or a finding
reported in a published study. Each target gives:

| Key | Meaning |
| --- | --- |
| `claim` | the finding, in words |
| `kind` | `value` (a mean and a reported SD) or `direction` (a finding with no reported spread) |
| `measure` | which measure of section 4 it is compared with; only measures the code computes are accepted |
| `value`, `sd`, `unit` | for a value target |
| `check` | for a direction target: how it is judged (section 3) |
| `reported` | the study's numbers that are shown beside the verdict but not used as a tolerance |
| `applies` | which pairs or runs it applies to: `pair_ages` (by `age_groups`, **[design]** young 18 to 35, older 65 to 94), `encounter`, `roles_differ`, `scenario` |
| `source`, `where`, `read` | the source (listed under `sources`, with its cached copy), where in it, and how much was read (`full text` or `abstract`) |
| `setting`, `differs` | the study's setting, and every way the simulation's differs; a non-empty `differs` labels each comparison `[setting differs]` |
| `disagrees_with` | another target the study disagrees with (both must point at each other) |

Also in the file:
- `sides`: which side people pass on, by place. It is a **parameter, not a target**: for Singapore no
  published study was found (#69), so it is not judged, and the loader refuses a file that judges it.
- `not_targets`: what was looked at and left out, with the reason.

**Version 1's targets** (sources in `literature/rule-verification/sources.md` and the file):

| Target | What | Kind | Source |
| --- | --- | --- | --- |
| H1 | Pass distance between centres, two young adults: 0.93 ± 0.17 m | value | Rapos2021, abstract |
| H2 | The same with an older adult: 0.79 ± 0.18 m | value | Rapos2021, abstract |
| H3 | The start of turning is further from the closest point at higher speed (2.1, 2.4, 2.7 m at 1.15, 1.42, 1.78 m/s) | direction | Huber2014, full text |
| H4 | No speed change in a head-on meeting | direction; disagrees with H5 | Huber2014, full text |
| H5 | A significant slowing while deciding the side | direction; disagrees with H4 | Moussaid2009, full text |
| H6 | The one who gives way contributes more | direction | Olivier2013, abstract |
| H7 | Roles are predicted by speed and heading, not by gender, height or personality | direction | Knorr2016, abstract |
| H8 | With an older adult, the young adult contributes more | direction | Rapos2021, abstract |
| C1 | A two-way street flow separates into two lanes (observed: 0.77 on their own right) | direction | Moussaid2009, full text, Figure 5b |
| C3 | Speed falls with density; the flow levels off from about 1.0 person/m² (peak 1.5 /(m·s) at 2.0) | direction | Zhang2012, full text |

**Left out:**
- **C2**: a near-uniform spread at low density. It is a result of Moussaid2009's model, not an
  observation.
- **H9**: no stopping or backing up. No study reports or counts it, so these are reported, not
  judged.

**What is inferred or read from figures:**
- H1's distance is between centres `[inferred]`. Rapos2021's minimal predicted distance is Olivier
  et al. 2012's measure, which Meerhoff et al. 2018 compute between shoulder midpoints.
- The side shares and C1's 0.77 were **read from Moussaid2009's figures by pixel measurement**
  (`literature/rule-verification/scripts/read_moussaid2009_figures.py`).

## 2. The tolerances (the user's decision of 2026-10-30, task 0, before any rule was measured)

- **Within 1 SD**: a value target is met when the subject's mean, over the pairs it applies to, lies
  within the study's mean ± one reported SD. H1: 0.76 to 1.10 m; H2: 0.61 to 0.97 m.
- **Direction only** for a target with no reported spread. Its numbers are shown beside the verdict.
- **Studies that disagree: report, no verdict.** Today this is H4 against H5, on slowing.

The loader refuses any other tolerance. Changing one means a new schema and file.

## 3. Verdicts (`judge.py`)

| Verdict | Meaning |
| --- | --- |
| within, outside | a value target |
| agrees, opposite, not shown | a direction target: significantly the study's way, significantly the other way, or neither, by RF-18's exact two-sided sign test at 0.05 (ties and undefined pairs dropped) |
| no verdict (studies disagree) | H4 and H5: the mean speed change and the share of walkers slowing by more than 0.1 m/s **[design]** are shown |
| not comparable | nothing the target applies to (for example H3 with one walking speed, H6 when every pair passes together) |

| Check | What the sign test counts | The study's way |
| --- | --- | --- |
| `increases_with_speed` | each seed: the two walkers' mean start of turning at the fastest speed against the slowest (the same people on a seed) | faster turns earlier |
| `giver_adapts_more` | each pair with distinct roles: the giver's share of the lateral deviation above or below half | the giver more |
| `younger_adapts_more` | each pair of an older and a young walker: the young one's share | the young more |
| `not_predicted_by_traits` | for each trait the two differ in (assertiveness, gender, older), whether the walker at the trait's first level passed first | no trait significant at 0.05 divided by the number of traits tested (Bonferroni, **[design]**) |
| `segregated` | each run: whether more walkers kept to one own side than chance would (the sign test of left against right, p < 0.05) | most runs separated |
| `speed_decreases_with_density` | each run: the sign of the least-squares slope of speed on density | most runs negative |

**A significant direction can be a small effect.** Rule and ORCA runs vary little from seed to seed,
so a consistent difference of centimetres is significant. The report shows the magnitudes beside
each verdict. Whether to add a smallest effect that counts would amend task 0, so it is the user's
decision.

## 4. Measures (`measures.py`)

Read back from finished run folders. **Per pair**, the trajectory must be logged on every step:

| Measure | Definition |
| --- | --- |
| `min_centre_distance_m` | the smallest distance between the two centres while both walk; the step is the **point of minimal distance** (PoMD, Huber2014) |
| `lateral_deviation_max_m`, `lateral_share` | the largest distance from the walker's own line (through its start, along its path), and its share of the two walkers' together |
| `turning_start_m` | Huber2014's start of turning: the first step before the PoMD whose angular speed (the change in the direction of the step's displacement per second) exceeds `TURN_RATE_FLOOR_RAD_S`, 0.05 rad/s **[design]**, as the distance along the path from there to the PoMD. Huber's threshold is each walker's own turning when walking alone; a simulated walker alone has none |
| `speed_change_mps` | Huber2014's speed change: the highest speed minus the lowest local minimum with a higher speed on both sides |
| `side` | the side the walker kept to at the PoMD, in its own frame, as Step 1's outcomes define it |
| `passed_first` | the first to be `CLEAR_DISTANCE_M` (1.0 m, **[design]**) past the PoMD along its path; `together` on the same step. Step 1's sessions use their own `who_passed_first` |

**Per crowd**, any stride:
- `lanes`: RF-18's lane measure, unchanged.
- `speed_by_density`: on each logged step, the people within 1 m either side of the corridor's
  middle (Zhang2012's measuring area), their number over the area, and their mean speed.

## 5. The subjects

| Subject | Runs |
| --- | --- |
| plain ORCA and round 1's four arms | `rf37_head_on`: `wide_corridor_head_on`, Moussaid2009's 1.75 m corridor, two people from a realistic crowd (`singapore_street_v1`, pool 100), 30 seeds, at 1.3 m/s and at Huber2014's three speeds; `rf18_round1_realistic`'s `flow_realistic` (50 + 50) with `rf37_flow_density`'s 15 + 15 and 75 + 75 |
| Step 1's agents, one subject per condition | the sessions of RF-10 (independent) and RF-30 (non-verbal, talk) carried out under `keep_line` whose plans alone resolved the meeting, measured on their `plan_only` replays |

In rule-set evaluation a person's factors change nothing physical: every body is 0.25 m and walks at
the scenario's speed. Step 1's sessions give a suitcase carrier a 0.35 m body.

**The side both ways.** A rule that fixes a side is not rerun with the other side: that would be a
changed rule. The corridor is symmetric about its centre line, so a right-turn version gives the
mirror image of the left-turn rule's runs. Every target but the side is therefore the same, apart
from the baseline's random perturbation `[derived: mirror symmetry]`.

## 6. #55's promotion table (proposed in task 7; adopted by the user on 2026-10-31)

The earlier table promoted a rule that **helps** in the simulation (RF-18) and **matches human
evidence** (RF-14). This one adds this layer and changes what the simulation must show:

| | Supported or partly supported (RF-14), and no applicable target **outside** or **opposite** (RF-37) | Otherwise |
| --- | --- | --- |
| **Does not harm** in a realistic scenario (RF-18) | **Promote** | Stays staged, labelled with the targets it misses |
| **Harms** | A finding: record why | Dropped |

- **"Does not harm" in place of "helps".** The goal is human accuracy, not efficiency. A rule as
  efficient as people are need not beat plain ORCA. Harm (gridlock, more collisions) still blocks
  promotion.
- **Targets that do not count against a rule:**
  - *not comparable* and *no verdict* targets do not block promotion; they are listed beside it;
  - the side is not a target while Singapore's is unknown.
- **No combined score.** The targets are shown side by side.

**Adopted by the user on 2026-10-31** (issue #124), on the user's own authority after RF-37's report;
no supervisor view is recorded. It replaces #55's table of 2026-10-27. Under it, no round 1 rule is
promoted: the left-turn rule is outside on H1, and the cane rule is outside on H1 and opposite on C1.
A smallest effect that counts (section 3) was not set with it and stays open.

## 7. Limits

- Every study is a laboratory or a street in France, Germany, Canada or China. None is in Singapore,
  and several studied crossing paths rather than head-on meetings. Each comparison says so.
- Four sources were read as abstracts only. Their full texts are closed or behind a bot check, and
  the user can fetch them in a browser: Rapos2021, Olivier2012, Olivier2013 and Knorr2016. Without
  them:
  - H1 uses the inferred centre-to-centre definition;
  - H6 and H7 are judged on direction;
  - for H7, which personality traits were measured is unknown.
- H7's speed-and-heading half is not tested: the two walkers do not differ in speed or heading in
  these runs.
- In the realistic crowd, few pairs are two young adults. The report also gives the pass distance
  over all pairs, which in the rule arms and plain ORCA does not depend on age (no round 1 rule
  reads age).
