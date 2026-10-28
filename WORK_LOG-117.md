# Work Log — Issue #117: RF-35: encounters sampled from crowds: do LLM agents resolve a conflict inside a crowd? (Step 1, independent, two densities)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/117
**Branch:** feat/117-rf35-crowd-encounters (from `feat/110-rf32-group-head-on` after PR #116 merged into
it, commit `ce5575c`; `main` is not used in this track)
**Started:** 2026-10-28, 13:09 UTC

## Understanding the issue

Round 1's rules came from two-person sessions and were judged in crowds of 100 (RF-18, RF-33). That
tells whether a rule helps a crowd, which is fair for any rule; it says nothing of how the LLM agents
behave in a crowd, so there is nothing yet to extract crowd rules from. **The user's decision
(2026-10-28): sample encounters from crowds, not whole crowds.** A crowd runs under ORCA; one encounter
in it (the two who start a conflict and anyone within 10 m predicted to conflict with them, cap 4
prompted) is given to the LLM; everyone else stays ORCA, as background the prompted people can see.
Cost grows with the number of encounters, not the crowd's size.

Step 1 only (resolve first): RF-32 and RF-34 found small groups resolve a head-on 0.06 to 0.14 of the
time, so first ask whether agents resolve crowd encounters at all.

**The user's decisions (2026-10-28):** two densities, 25 and 50 per way in RF-18's flow; the independent
condition; bystanders drawn from RF-33's realistic profile `singapore_street_v1`.

**Paid.** Build on the mock; the paid run needs its own approval and cap in `CLAUDE.md`. Balance USD 0.39.

## Plan

1. Source runs `configs/cases/rf35_source_crowd_flow.yaml` (free) and a case set `rf35_crowd_v1`.
2. `design.others: {population: <profile>}`: each session's bystanders drawn from the profile at exact
   shares, the same for every session of one case and cell (so exact repeats are exact); the old form
   unchanged.
3. Config `configs/resolution/rf35_crowd_encounters.yaml`: `passing_crowd`, cap 4, RF-32's template and
   execution; the design's two with distraction and load fixed at their base level, so that a
   bystander's phone or suitcase is shown to whoever sees them.
4. Mock rehearsal, `--plan`, estimate; tests; ask for the paid run.
5. Paid run (pilot first), analysis by density and encounter size, `crowd_report.md`.

## Progress log

### 2026-10-28 12:55 to 13:09 UTC — before the branch: PRs merged, issues closed, #55, this issue
- At the user's request: PR #114 (RF-32) merged into `feat/112-...` and PR #116 (RF-34) into
  `feat/110-...` (merge commits, 12:55 UTC); #110 and #115 closed by hand with a note; #55 ticks both and
  lists #117 as next.
- The user answered three design questions (density, condition, bystanders); recorded above and in #117.
- Branched from the merged tip (`ce5575c`).

### 2026-10-28 13:11 UTC — source runs started
- What I did: `configs/cases/rf35_source_crowd_flow.yaml` (the flow at 25 and 50 per way, two repeats,
  plain ORCA, perturbed baseline), committed before this log (the workflow puts the log first; noted).
  Runs started from a clean tree.
- Read while it runs: `passing_crowd` (exists, mock only), `design.others` (#110: one fixed persona for
  everyone else), `others_in` (each case's other people, any scenario), `populations.quota_people`
  (exact shares from a seed), `SessionFactors` (a factor is rendered only if the design varies it).

### 2026-10-28 13:12 to 13:18 UTC — cases, bystanders, config, tests
- Source runs (13:11 to 13:12 UTC, free): every person arrived in all four; collisions 16 and 15 at 25
  per way, 91 and 81 at 50 per way (plain ORCA, as RF-18 found in its flow).
- Case set `rf35_crowd_v1`: 302 eligible pairs (T3 and above, head-on when formed); two per density and
  tier: 25 per way T3 `flow_1b5b9b8d`, `flow_b0c1353e`, T4 `flow_06018e0c`, `flow_61f018fc`; 50 per way T3
  `flow_32e86a8e`, `flow_826d5092`, T4 `flow_9274de21`, `flow_bf8bfa07`.
  **Changed from the issue [mine]:** tiers T3 and T4, not T2 to T4: 4 per density do not split evenly
  over three tiers, and a T2 pass is no conflict to resolve.
- `design.others.population` (`design.py`): everyone beyond the design's two drawn with
  `populations.quota_people` (exact shares), seeded by the design's seed, the case and the cell, so an
  exact repeat has the same people. Their persona carries only the factors the design has (a factor is
  rendered only then), so the config fixes `distraction` at its base level for the two, and a
  bystander's phone is shown. The old form (#110) is unchanged.
- **Found, and changed [mine]:** `load` in the design crashed the plan: a bystander drawn with a
  suitcase gets a wider body (issue #60), which only the design's two have radii for, and which would
  change the case's run. `load` left out of the design (its 1% is a placeholder; the user's option named
  age, gender, a cane and a phone), and `others.population` now refuses `load` with a clear message.
- **Design kind [mine]:** `sample` (a balanced 8 of the 16 cells): the fractional kind has 16 or 32.
- **Protocol [mine]:** `orca_within_groups: true` (in the flow a run's group is its walking direction:
  the user's RF-32 decision then means the plans decide only between people walking opposite ways) and
  `distance_to_partner: true` (in a crowd the nearest person in view at the trigger may be a stranger).
- `--plan`: 72 sessions over 8 cases, at most 8 calls a session; loose worst case USD 23.5 (crowd
  prompts are long: everyone in view is described).
- `tests/test_rf35_crowd.py` (6): cases, config, exact shares, exact repeats, a bystander's cane or
  phone in what others are told, the population form's checks and the old form unchanged. RF-32's and
  RF-34's tests pass.
- `groups.py`: a case without a `layout` (the flow) is labelled by its variant (`density=...`); the
  resolved share by encounter size. `docs/resolution.md`: a note under D11.
- Mock rehearsal of all 72 started at 13:15:17 UTC (`runs_mock/rf35/`).

## Open questions / risks

- Same-direction people in an encounter are treated as one "group" by `orca_within_groups` and by the
  analysis's formations (there labelled friends); in a crowd they are strangers.
- The 8 cases come from four source runs (two seeds per density); different crowds would give other
  encounters.

## Summary (fill in at the end)
