# Conflict cases (issue #30, Part 2; issue #32)

A **conflict case** is one conflict, taken from a finished run of the primary baseline and
frozen as data, from which rules are generated (`rule-generation.md`). Generation is
**offline**: a case is a moment of a run that is over, not a run in progress (a decision of
the issue). Both conditions of rule generation are shown the same case, the negotiating
agents of condition A each first-person, the stating model of condition B third-person; what
happened under the baseline is kept in the case for later analysis and shown to neither.

The code is `negsim/rulegen/cases.py`; the cases are under `llm_negotiation/cases/`.

## 1. What a case holds

One file per version, `cases/<case_id>.v<n>.json`:

| Key | What it is |
|---|---|
| `case_format_version` | 1 or 2: the version of this format. 2 (issue #32) is a case whose records are of perception version 3, or a re-stepped one (section 7); a case that holds neither is written as 1, as before |
| `case_id`, `version` | The case's stable id (section 3), and its version, from 1 |
| `scenario` | The scenario and its version: `type`, `file` (the scenario YAML), `schema_version` (2), `resolved_sha256` (the SHA-256 of the resolved scenario as the run used it, its version in effect), `description`, `variant` (the level of each factor of the source experiment), `n_agents`, `dt_s`, `geometry`, and `single_file_segments` (`name`, `width_m`, `length_m`) |
| `source` | The run it came from: `experiment`, `run_id`, `run_index`, `seed`, `seeding`, `repeat`, `baseline` (`name`, `sha256`), `perturbation`, `git_commit`, `git_dirty`, `created_utc`, `log_schema_version`, and `pair_id` |
| `agents` | The two agents, the lower-numbered first |
| `formation` | When the pair formed: `step`, `time_s`, and its `encounter_class` then |
| `snapshot` | **Every field a rule may read** for the pair at that step (`rule-format.md`, section 5), as a match records it (`log-schema.md`): `pair` and `agent` values. The demographic fields are empty: a case has no persona, a session gives the agents theirs (`rule-generation.md`, section 2) |
| `observations` | **Each agent's own perception record** of the other at that step, whole (`perception.md`), keyed by agent: what it could tell, first-person |
| `bodies` | What each agent knows of itself physically: `radius_m`, `preferred_speed_mps`, `max_speed_mps`, `group` |
| `private` | One empty slot per agent for its private information, `{"task": null}`. A session fills it (`rule-generation.md`); a case never does |
| `severity_tier` | The pair's tier under the baseline (`metrics.md`, section 11) |
| `baseline_outcome` | **What happened under the baseline, for later analysis only, shown to no condition**: `category`, `severity_tier`, `tier_detail`, `pair_exposure_time_s`, `conflict_exposure_time_s`, `first_pair_exposed_step`, `min_separation_m`, `passed_time_s`, `end_time_s`, `end_reason`, `run_status`, the two agents' `time_to_goal_s`, and `first_through` (at a single-file segment); and, format 2 from a run of log schema 5, `first_out`, the agent that came out of the segment first (two who start inside a passage both enter it at once, so there `first_through` is null) |
| `derived_from` | Format 2, a re-stepped case only (section 7): `case` (the version it was made from, `case_id@version`), `method` (`re-stepped`), `perception_schema_version`, `git_commit` and `git_dirty` of the code that made it, and what was `checked` |

The snapshot is the one the run loop evaluates rules on, from the logged records (their
rounding to six decimal places aside): a test steps the same run to the same step and
compares (`tests/test_rulegen_cases.py::test_a_case_holds_what_the_two_agents_saw_when_the_pair_formed`).

## 2. Where cases come from

**The source runs.** Five experiments under `configs/cases/`, one per SI-1 scenario, all on
the primary baseline (`orca_perturbed_v1`), plain ORCA, paired seeds, two repeats, run from
a clean tree (`runs/si3_source_*`). In the two-agent scenarios the tier depends on the
geometry, not on the seed (the perturbation only breaks exact symmetry), so each varies its
layout instead:

| Experiment | Layouts | Pairs by tier |
|---|---|---|
| `si3_source_head_on` | aligned; lines 20, 40 and 52 cm apart | 8 T3 |
| `si3_source_open_crossing` | at the crossing together; one 0.5 m and 1 m ahead | 4 T3, 2 T0 (1 m ahead) |
| `si3_source_overtaking` | in line; 30 and 45 cm aside | 6 T3 |
| `si3_source_bottleneck` | opposing; merging | 2 T3 (opposing), 2 T0 (merging) |
| `si3_source_bidirectional_flow` | the 50 + 50 flow | 116 T1, 619 T2, 1,349 T3, 140 T4, 7,441 T0 (two runs) |

**Every eligible two-agent pair is T3.** Plain ORCA passes two bodies on a collision course
with their discs a few millimetres apart, inside the near-miss distance, so the baseline's
ordinary pass is a near miss (`metrics.md`, section 11). At 52 cm apart the intended
velocities are never on a collision course, and the pair is still T3: ORCA steps them
within 0.1 m of each other. T1, T2 and T4 cases come from the crowd.

**Eligibility** (`configs/cases/si3_cases_v1.yaml`, `eligibility`):

1. **The primary baseline, plain ORCA**: a run with another baseline, any directive, a log
   schema before version 4 (no tiers), or no interaction records is not a source.
2. **Tier T1 and above**, as the issue says.
3. **Both agents perceived each other when the pair formed.** A case is the two agents'
   views of one moment, and the log holds each agent's view only from when it first
   perceived the other. **DD70 (decision).** A pair that formed one-sided (one agent
   perceived the other a step or more before it was perceived itself, when more agents than
   `max_neighbours` were in range) is not eligible.
4. **The two were approaching each other when the pair formed** (`formation_classes`:
   head-on, crossing, overtaking or single-file, not `none`). **DD71 (decision).** In the flow,
   agents of one group start side by side, 1 m apart, and every such pair forms at 0 s, not
   approaching; some of them collide or wait much later, when the other group arrives, but
   the moment they formed says nothing about that conflict, and a case is that moment.

What that leaves, of the 9,689 pair interactions of the 26 source runs: 7,445 below T1,
1,727 one-sided formations, 307 not approaching when they formed, and **210 eligible**.
**Rule 3 is a selection, and it is not neutral in a crowd:** of the flow's 2,224 pairs at
T1 or above, 1,727 formed one-sided. An eligible crowd case is one whose two agents came
into each other's view at the same step, which favours pairs that were not crowded out of
each other's 40 nearest neighbours. (Open question Q4 of `WORK_LOG-30.md`.)

## 3. Stable ids, immutability, versions

**A case id is stable**: the short name of its scenario (`head_on`, `crossing`,
`overtaking`, `bottleneck`, `flow`, and since issue #32 `passage`) and the first eight
hexadecimal characters of the SHA-256 of `<experiment>/<run_id>/pair<pair_id>`. Extracting
again from the same runs gives the same ids and the same files, byte for byte: nothing in a
case depends on when it was extracted. (Tested for `si3_v1`: all 18 files come back as frozen,
`tests/test_rulegen_cases.py::test_extracting_again_from_issue_30s_runs_gives_the_committed_files`.
That is why a case's format version follows what it holds, DD112 of `WORK_LOG-32.md`.)

**A case is frozen** as a rule is (`rule-format.md`, section 8): `cases/MANIFEST.json`
records the SHA-256 of every case file (line endings normalised to LF), the store refuses to
read a file that is not listed or does not match, and refuses to write different contents
under a frozen name. A changed case is the next version, a new file, and the old one stays.

## 4. Sampling: strata

The eligible pairs are grouped into **strata** by the keys `strata.by` names, any of
`scenario`, `variant` (the source experiment's level), `tier`, `encounter_class` (at
formation) and, since issue #32, `experiment` (the source experiment, which tells apart two
scenarios of one type whose experiments name their levels alike). Each stratum gives up to its quota, `per_stratum` (a number, or a number per
scenario with a `default`). Within a stratum the candidates are sorted by case id and drawn
by a random stream of the stratum's own, seeded by `strata.seed` and the stratum's key, so
adding a source or a stratum never changes what another stratum draws.
*Tested:* `::test_sampling_is_stratified_seeded_and_each_stratum_draws_on_its_own`.

## 5. The case set `si3_v1`

`configs/cases/si3_cases_v1.yaml`: strata by scenario, layout and tier; one case per
stratum, two per tier in the flow; seed 30. **18 cases**:

| Case | Scenario | Layout | Tier | Formed | Source run, pair |
|---|---|---|---|---|---|
| `bottleneck_a35e31ca` | corridor_to_bottleneck | flow=opposing | T3 | single_file_segment at 2.2 s | `si3_source_bottleneck/002_opposing_r2`, pair 0 (agents 0 and 1) |
| `crossing_6c29d99f` | open_crossing | layout=together | T3 | crossing at 0.0 s | `si3_source_open_crossing/002_together_r2`, pair 0 (agents 0 and 1) |
| `crossing_bda974ab` | open_crossing | layout=ahead_50cm | T3 | crossing at 0.0 s | `si3_source_open_crossing/004_ahead_50cm_r2`, pair 0 (agents 0 and 1) |
| `flow_03ea57f6` | bidirectional_flow | base | T2 | head_on at 18.2 s | `si3_source_bidirectional_flow/001_base_r1`, pair 4733 (agents 45 and 93) |
| `flow_0c9186e8` | bidirectional_flow | base | T3 | head_on at 14.2 s | `si3_source_bidirectional_flow/002_base_r2`, pair 3996 (agents 26 and 85) |
| `flow_41cdaf6f` | bidirectional_flow | base | T3 | head_on at 8.6 s | `si3_source_bidirectional_flow/002_base_r2`, pair 2398 (agents 0 and 62) |
| `flow_47cc586f` | bidirectional_flow | base | T1 | head_on at 9.3 s | `si3_source_bidirectional_flow/002_base_r2`, pair 2458 (agents 10 and 60) |
| `flow_ba3c7962` | bidirectional_flow | base | T4 | head_on at 9.2 s | `si3_source_bidirectional_flow/001_base_r1`, pair 2448 (agents 0 and 66) |
| `flow_dd54f3c3` | bidirectional_flow | base | T1 | head_on at 14.1 s | `si3_source_bidirectional_flow/002_base_r2`, pair 3968 (agents 30 and 76) |
| `flow_dee42245` | bidirectional_flow | base | T2 | head_on at 16.4 s | `si3_source_bidirectional_flow/001_base_r1`, pair 4579 (agents 41 and 85) |
| `flow_e1aad74a` | bidirectional_flow | base | T4 | head_on at 10.0 s | `si3_source_bidirectional_flow/002_base_r2`, pair 2527 (agents 5 and 67) |
| `head_on_02dfbadb` | wide_corridor_head_on | layout=apart_20cm | T3 | head_on at 1.4 s | `si3_source_head_on/004_apart_20cm_r2`, pair 0 (agents 0 and 1) |
| `head_on_59908410` | wide_corridor_head_on | layout=apart_40cm | T3 | head_on at 1.4 s | `si3_source_head_on/005_apart_40cm_r1`, pair 0 (agents 0 and 1) |
| `head_on_de176842` | wide_corridor_head_on | layout=aligned | T3 | head_on at 1.4 s | `si3_source_head_on/001_aligned_r1`, pair 0 (agents 0 and 1) |
| `head_on_ff0aa402` | wide_corridor_head_on | layout=apart_52cm | T3 | head_on at 1.4 s | `si3_source_head_on/008_apart_52cm_r2`, pair 0 (agents 0 and 1) |
| `overtaking_23c5d31e` | overtaking | layout=aside_30cm | T3 | overtaking at 0.0 s | `si3_source_overtaking/003_aside_30cm_r1`, pair 0 (agents 0 and 1) |
| `overtaking_2d08db11` | overtaking | layout=in_line | T3 | overtaking at 0.0 s | `si3_source_overtaking/001_in_line_r1`, pair 0 (agents 0 and 1) |
| `overtaking_3cf825b8` | overtaking | layout=aside_45cm | T3 | overtaking at 0.0 s | `si3_source_overtaking/005_aside_45cm_r1`, pair 0 (agents 0 and 1) |

Every stratum of the two-agent scenarios had two eligible pairs (the two repeats), one of
which was drawn; the flow's strata had 12 (T1), 8 (T2), 160 (T3) and 10 (T4).
`cases/extractions/si3_v1.json` has the full report: per source run, how many pairs it had,
how many were eligible and why the others were not; per stratum, what was eligible and what
was drawn.

## 6. Commands

```
python -m negsim.rulegen.cases extract configs/cases/si3_cases_v1.yaml [--dry-run]
python -m negsim.rulegen.cases restep --set si3_v1 --new-set si3_v2 [--dry-run]
python -m negsim.rulegen.cases list [--set si3_v1]
python -m negsim.rulegen.cases show head_on_de176842
python -m negsim.rulegen.cases check
```

`extract` writes the new case files, the case set (in the manifest, with the SHA-256 of its
config) and the extraction report; run again, it writes nothing. `restep` (issue #32,
section 7) writes the next version of every case of a set and records them as a new set;
`--dry-run` re-steps and checks every case and writes nothing. `check` exits 1 if the store
does not match its manifest.

A config's description is YAML: an unquoted ` #` starts a comment, and the rest of the line
is lost. `si3_cases_v1.yaml` lost "#30, from the primary baseline on the five SI-1 scenarios."
that way (its frozen set reads "The first case set of issue"); `si32_passage_cases_v1.yaml`
quotes its description.

## 7. Case format 2, and new versions by re-stepping (issue #32)

Issue #32 added fields to the perception record (version 3: the passage fields and the
fictional group, `perception.md`) and to the rule format (version 3). A case is immutable, so
a case with the new fields is **its next version**, and the old one is kept: issue #30's
configs, which name `set: si3_v1`, read exactly what they read before.

**Re-stepping** (`restep_case`). The case's source run is rebuilt from its own config (the
scenario as resolved then, its seed, baseline, perturbation and visibility; the scenario's
SHA-256 must match the case's), run again up to the step its pair formed, and the two
perception records the run builds at that step are taken, with the shared snapshot of the
newer rule format. **Every field of the old version's records and snapshot must come out
equal** (the records' schema version aside); if any does not, nothing is written and the
error names the field. Only the records and the snapshot change; everything else of the case
(its scenario, source, agents, formation, bodies, private slots, tier and baseline outcome) is
copied. The new version says what it was made from (`derived_from`). A test re-steps a case
and shows that a single changed number is caught
(`tests/test_rulegen_cases.py::test_a_case_gets_a_next_version_with_newer_records_by_re_stepping_its_source_run`).

Why re-step rather than re-extract: the source runs' logs were written with perception
version 2 and do not have the new fields, and running the source experiments again would make
new runs, not the same ones. Re-stepping reproduces the moment exactly and checks that it did.

## 8. The case sets of issue #32

**`si3_v2`**: the 18 cases of `si3_v1`, each at version 2, re-stepped at commit `d57e854` from
a clean tree. Every field of every version 1 came out equal. Their records add the passage
fields (`perception.md`, "Passage fields"): all four null in 17 of the 18, whose pairs have no
passage; in the bottleneck case, which forms before the segment, `in_segment` is false for
both and the three distances null. Use the set with prompt version 2 (`rule-generation.md`,
section 3.1).

**`si32_passage_v1`**: two people who meet inside a single-file passage, from
`configs/cases/si32_passage_cases_v1.yaml`. The sources are two experiments under
`configs/cases/` on the primary baseline (`runs/si32_source_passage_meet_middle`,
`..._meet_with_speeds`, 16 runs, `d57e854`, clean): each layout of distances walked in, at
rest and walking, two repeats. Every one of their 16 pairs forms on step 0, both inside, of
class `single_file_segment`, and is eligible: T3 walking, T3 or T4 from rest. The tier there
follows the seed (from rest the same layout deadlocks under one seed and times out under the
other), not the situation, so the strata are the **source experiment and the layout**, one
case each (DD115):

| Case | Scenario | Layout | Distances walked in (agent 0, 1) | Tier | Baseline run | Source run, pair |
|---|---|---|---|---|---|---|
| `passage_bf7d97c7` | passage_meet_middle_v1 | symmetric, rest | 1.7, 1.7 m | T4 | deadlock | `si32_source_passage_meet_middle/002_symmetric_rest_r2`, pair 0 |
| `passage_067961e3` | passage_meet_middle_v1 | symmetric, walking | 1.7, 1.7 m | T3 | completed | `si32_source_passage_meet_middle/004_symmetric_walking_r2`, pair 0 |
| `passage_10e542c2` | passage_meet_middle_v1 | asymmetric, rest | 2.7, 0.7 m | T4 | deadlock | `si32_source_passage_meet_middle/005_asymmetric_rest_r1`, pair 0 |
| `passage_02fac1e4` | passage_meet_middle_v1 | asymmetric, walking | 2.7, 0.7 m | T3 | completed | `si32_source_passage_meet_middle/008_asymmetric_walking_r2`, pair 0 |
| `passage_f89f5745` | passage_meet_with_speeds_v1 | asymmetric, rest | 2.0, 1.4 m | T4 | deadlock | `si32_source_passage_meet_with_speeds/002_asymmetric_rest_r2`, pair 0 |
| `passage_c51d042c` | passage_meet_with_speeds_v1 | asymmetric, walking | 2.0, 1.4 m | T3 | completed | `si32_source_passage_meet_with_speeds/003_asymmetric_walking_r1`, pair 0 |
| `passage_eae0ce13` | passage_meet_with_speeds_v1 | symmetric, rest | 1.7, 1.7 m | T4 | deadlock | `si32_source_passage_meet_with_speeds/006_symmetric_rest_r2`, pair 0 |
| `passage_25f09e61` | passage_meet_with_speeds_v1 | symmetric, walking | 1.7, 1.7 m | T3 | completed | `si32_source_passage_meet_with_speeds/007_symmetric_walking_r1`, pair 0 |

Under the baseline, **neither got through in any case that starts at rest** (the arbiter's way
stalls there, `derivations.md` section 17.1, and `behaviour-checks.md` section 6), and agent 0
(the one further in, or the lower index when the two have walked in equally far) came out
first in every case that starts walking (`first_out`). These
cases are format 2: perception records of version 3, which tell each agent how far each has
walked in and how far each end is. The extraction report is `cases/extractions/si32_passage_v1.json`.
*Tested:* `::test_the_committed_re_stepped_set_and_the_passage_set`.

Which start SI-3b's cases should come from, at rest or walking, is open question Q2 of
`WORK_LOG-32.md`: both are in the set.
