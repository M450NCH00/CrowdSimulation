# Work Log — Issue #122: RF-37: human targets: measurable targets from published studies; rules, plain ORCA and Step 1's agents measured against them

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/122
**Branch:** feat/122-rf37-human-targets (from `feat/110-rf32-group-head-on` at `e2538f0`, after PR #121
(RF-14) was merged into it on 2026-10-30; `main` is not used in this track)
**Started:** 2026-10-30, 11:36 UTC

## Understanding the issue

The user's goal, stated on 2026-10-30 while RF-14's PR was open: **resolve conflicts in a way accurate
to human behaviour**, in crowds of 10,000 agents or more. Nothing measures that today:

- RF-18's "helps" measures the crowd's efficiency (severe conflicts, throughput, delay, gridlock);
- RF-31's identity check measures agreement with the LLM agents, who are not the reference;
- RF-14 grades rules in words, without the studies' numbers;
- lane formation is reported, not judged.

This issue turns RF-14's cached evidence into **measurable targets with sources and tolerances**, adds
the measures, and judges each rule arm, plain ORCA and Step 1's own agents against the targets.
No model call. Under #55 decision 6 (published studies only), targets come from numbers reported in
published studies, not from trajectory datasets.

**Order fixed by the issue:** the tolerances are agreed with the user (task 0) **before any rule is
measured**, as RF-18's "helps" was before its run.

## Plan

1. Task 0: ask the user for the tolerance rule; record the answer here word for word.
2. Inventory what the code already measures (`docs/metrics.md`, `negsim/ruleset_eval/measures.py`,
   the identity check of RF-31, `negsim/resolution/groups.py`), so new measures reuse what exists.
3. Task 1: fill the source gaps (C3 speed against density; S2 Figure 4 shares; Rapos2021's distance
   definition; Knorr2016's traits), caching each in `refs/` (`rf37_*`).
4. Task 2: frozen targets file `llm_negotiation/configs/human_targets/head_on_v1.yaml` and its loader,
   with tests (every value names its source; frozen by hash, as templates are).
5. Task 3: the measures, tested on hand-built trajectories with known answers.
6. Task 4: study-matched scenarios as variants of existing layouts; earlier configs unchanged.
7. Task 5: the report (each arm, plain ORCA and Step 1's agents against each target; the side both
   ways for Singapore).
8. Task 6: run on round 1 (`rf18_round1_realistic`'s rules, RF-10 under `keep_line` and RF-30).
9. Task 7: a proposal for #55's promotion table, for the user.
10. Task 8: docs and READMEs; section 5b checks; full test suite; PR stacked on
    `feat/110-rf32-group-head-on`.

## Progress log

### 2026-10-30 11:36 UTC — PR #121 merged, #69 closed, branch cut
- What I did: at the user's request, merged PR #121 (RF-14) into `feat/110-...` (11:35 UTC), closed #69
  by hand with a note (a stacked merge does not fire `Closes`), ticked it in #55 with its result, and cut
  this branch from `origin/feat/110-rf32-group-head-on`.
- Next step: task 0 (the tolerances), then the inventory.

### 2026-10-30 11:38 UTC — Task 0: tolerances agreed with the user, before any measuring
- Asked the user two questions; the answers, word for word as chosen:
  - Tolerance: **"Within 1 SD (Recommended)"**: the simulated mean must fall within the study's mean
    ± 1 reported standard deviation (Rapos2021's two young adults, 0.93 ± 0.17 m: 0.76 to 1.10 m).
    Targets with no reported spread are judged on direction only.
  - Studies that disagree: **"Report, no verdict (Recommended)"**: the simulation's value is shown
    beside both studies, with no pass or fail on that target until a further source settles it. Today
    this applies to H4 against H5 (slowing in a head-on: Huber2014 none at 180°, Moussaid2009 a
    significant decrease).
- Fixed before any rule was measured. The targets file will carry these two rules, and changing them
  is a new version of the file.
- Next step: the inventory of existing measures.

### 2026-10-30 15:11 UTC — Inventory: what is already measured, and where the data is
Read `docs/metrics.md`, `docs/rule-set-evaluation.md`, `negsim/ruleset_eval/measures.py`,
`negsim/resolution/outcomes.py` (Step 1's physical outcome columns) and the function list of
`negsim/resolution/groups.py`.

| Target | Measured today | Where | What is missing |
| --- | --- | --- | --- |
| H1, H2 passing distance | `min_separation_m`, the smallest gap between the two **bodies' surfaces** | `outcomes.py`; `metrics.md` section 7 | Rapos2021's distance may be between centres (task 1); centres = gap + both radii (0.5 m) |
| H3 start of turning | nothing | | new measure, Huber2014's own definition (below) |
| H4, H5 slowing | yield events (below half the preferred speed for at least 1 s) | `metrics.md` section 4 | too coarse: a new speed change, Huber's maximum minus minimum speed |
| H6, H8 who adapts more | `path_deviation_max_m` per agent over the whole run; `who_passed_first` (zone exit) | `metrics.md` section 7; `outcomes.py` | each agent's share of the pair's lateral deviation, within the encounter |
| H7 what decides the roles | `who_passed_first` | `outcomes.py` | every Step 1 head-on agent walks at 1.3 m/s on the same line: speed must vary to test it |
| H9 stopping, backing up | `stopped_*`, `backed_up_*`, `backed_distance_*_m` | `outcomes.py`; `metrics.md` section 10 | nothing |
| S1 to S5 side | `passing_side_a`, `passing_side_b`, own frame, at the closest approach | `outcomes.py` | not in `ruleset_eval`'s measures; reuse |
| C1, C2 lanes | `lanes()`: share on own left or right within 10 m of the middle | `measures.py` | reported for one density only, not judged |
| C3 speed against density | nothing | | new measure, and a source (task 1) |

**Where the data is.**
- **Step 1's agents**: `runs/rf10_round1_head_on_keep_line/replay/` (96 independent sessions) and
  `runs/rf30_round1_head_on_keep_line/replay/` (192 non-verbal and talk). Scenario
  `wide_corridor_head_on`: **1.75 m wide, Moussaid2009's corridor**, both at 1.3 m/s, layouts with
  lateral offsets. Trajectories are **committed at stride 1** (0.1 s), modes `plan_only` and
  `plan_orca`. These targets can be measured with no new run. Plain ORCA's columns are in
  `outcomes.csv`, but its trajectories are not on disk; it is rerun deterministically.
- **Rule arms**: `rf18_round1_realistic` has **no open head-on of two people**. Its scenarios are
  the two-way flow, the single-file bottleneck and the narrow passage. Its trajectories are at stride
  10 (1 s) and are not committed. The pair targets for rules therefore need the study-matched head-on
  of task 4, at stride 1. The flow gives C1 and C2.

**Huber2014's definitions** (`refs/rf14_huber2014_speed_path.txt`, section 4.4, read in full):
- PoMD is the point on the walker's path where it is nearest the interferer.
- **Start of turning** is the first point where the angular speed exceeds the walker's own baseline
  turning magnitude: the mean of its maximal angular speed when walking with no interferer, per
  participant and speed. It is reported as the distance from PoMD along the walking direction.
- **Speed change** is the lowest local minimum (between two peaks) subtracted from the maximum.
- **Table 1 gives means only, with no spread.** By task 0's rule, H3 is therefore judged **on
  direction**: the start of turning is further from PoMD at higher speed, which was significant
  between all three speeds. The 2.4 m (normal speed, 180°) is reported beside, with no verdict. The
  authors also note that some onsets were cut off by the tracked area, so the true values may be
  larger.
- **[design, for the measure]** In the simulator an agent walking alone goes dead straight. Its
  baseline turning magnitude is therefore close to zero, apart from the 1e-4 m/s perturbation, so a
  floor is needed. It will be set from the same agent's no-interferer run on the same seed, plus a
  stated floor, and reported with the measure.
- Next step: task 1, the source gaps.

## Open questions / risks

1. ~~**Tolerances** (task 0): not yet agreed.~~ Agreed 11:38 UTC (above).
2. **Study settings differ from the simulator's**: lab tasks with instructed walkers, one walker going
   straight in Huber2014, young adults in France, Germany, Canada and China; none in Singapore. Every
   comparison whose setting cannot be matched is labelled `[setting differs]`.

## Summary (fill in at the end)
