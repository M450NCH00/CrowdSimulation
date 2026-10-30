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

### 2026-10-28 14:07 UTC — mock rehearsal read; cost estimate
- All 72 ran (13:15 to 14:07 UTC: each session reruns a 50- or 100-person flow). Every encounter reached the cap of 4 (21 more within 10 m on average left to ORCA); 2 to 4
  of them prompted (a member is prompted only once it perceives someone it conflicts with). 6.8 calls a
  session; prompts about 4,000 characters, 1.23 times RF-32's (3,261), at USD 0.000121 a call there.
- Estimate about USD 0.07 for 72 sessions; proposed cap USD 0.10.
- `groups.py` on the mock records: started at 14:08, stopped after the pilot (it reruns two 50- or
  100-person flows a session; the pilot's analysis below exercised the same code).

### 2026-10-28 14:09 UTC — the user's answer: paid runs approved, cap USD 0.10
- Recorded in `CLAUDE.md`; the config's cap set. Balance checked: USD 0.39.

### 2026-10-28 14:10 to 14:21 UTC — pilot (paid): 8 sessions, USD 0.008887, off-peak
- Calls 14:10:10 to 14:13:03 UTC (ledger): 60 calls, all off-peak, no transport error. About USD 0.0011
  a session: 72 sessions ≈ USD 0.08, inside the cap.
- Plans are sensible: people step aside towards a wall, slow for the elderly, pass a slow walker ahead,
  "keep my line and let the crowd sort itself out". Live: 5 passed, 3 no conflict left, none collided.
  One reply refused on a distance; genuine (the partner was 0.67 m away, the reply said until 1.4 m).
- **Problem found: the pair measure does not work in a crowd.** In `plan_only`, 1 of 37 conflict pairs
  resolved; plain ORCA on the same seeds 0 of 37. 36 and 33 of them count a collision: grazes of 1 to
  30 mm with a bystander or with each other, which ORCA makes all the time in a dense flow (16 to 91
  collisions per source run). Under this measure no crowd encounter can be resolved, by anyone.
- I asked the user, since it redefines Step 1's measure; it does not change the sessions (scored from
  the replays).

### 2026-10-28, before 14:32 UTC — the user's decisions: score against plain ORCA; run the rest
- **Measure (the user's choice):** a crowd encounter is resolved when, from its start on the same seed,
  its people collide no more often and no deeper than under plain ORCA, and none is stuck. Built in
  `groups.py` (`contacts`, `against_orca`): episodes ending at or after the start that involve one of
  the encounter's people (walls included), the deepest overlap, stuck = a deadlock or not arrived;
  better / same / worse per session, the sign test over sessions. The pair measure stays reported.
- **The remaining 64 sessions** started from a clean tree (commit `fd3ac8a`, `0920bb7` after the rewrite below), off-peak.

### 2026-10-28 14:32 to 15:38 UTC — the run (paid): 72 sessions, USD 0.070697, off-peak
- Calls 14:32:58 to 14:53:36 UTC (ledger); the rest of the time is the replays (each reruns a 50- or
  100-person flow three times). 424 calls for the 64, USD 0.061811; with the pilot 484 calls (256
  decisions, 228 debriefs) over 72 sessions, **USD 0.070697**, inside the cap of 0.10. All off-peak,
  no transport error. Balance (`GET /user/balance`, the key not printed): **USD 0.32** (0.39 before).
- All 72 completed; 6.7 calls a session; every encounter reached the cap of 4. Live: 59 passed, 13 no
  conflict left. 12 unreadable decision points (9 an `until` distance beyond the current one), 16
  retried. Debriefs: common sense 124, habit 88, none 16.
- The scenario's own measure (every conflict pair clear, no collision or near miss): 0 of 72 in every
  mode, plain ORCA included, as the pilot found; the measure of record is against plain ORCA.
- Analysis (`groups.py ... --pairs runs/rf10_round1_head_on_keep_line`) started at 15:39 UTC.

### 2026-10-28 15:39 to 16:09 UTC — analysis; then the report
- Against plain ORCA: **14 of 64 resolved** (0.22, 0.14 to 0.33): 8 of 32 at 25 per way, 6 of 32 at 50;
  better 6, same 8, worse 50 (sign test p < 0.001); collisions 389 with plans against 336; nobody
  stuck. Pair measure: 0 of 64 in every mode; 12 of 264 conflict pairs with plans, 0 with plain ORCA.
- Looked further (from the replays' `events.jsonl`): in 32 of 64 sessions the count is the same and the
  verdict turns on depth (median deepest 14 mm with plans, 5 mm without). Tolerance check: 26 of 64 at
  5 mm, 34 at 1 cm; the count alone: more in 30, fewer in 2. The deep contacts (median 13.8 mm, up to
  54 mm) are between the encounter's own people walking opposite ways; grazes with bystanders are
  about 3 mm. Exact repeats scored identically within each set.
- **Found [mine]:** the replays are 2.0 GB, 1.9 GB of it the two interaction logs, which the viewer and
  the outcomes do not need and `negsim.resolution.replay` rebuilds from the records. They are now
  gitignored and untracked (the pilot's 32, committed in `fd3ac8a`, too); the rest of each replay is
  committed (about 130 MB). The pilot commit still held those 32 files (258 MB) in history.
- **The user's decision (16:46 UTC): rewrite, then push.** `git filter-branch --index-filter` over the
  branch's 11 unpushed commits only, removing the RF-35 replays' two interaction logs; the final tree is
  unchanged (empty diff) and the files stay on disk. The pilot commit is now `0920bb7`.
- `test_ethnicity`'s list of configs now includes RF-35's (the same factor template as RF-32), with a note.
- `crowd_report.md` written; README row; `CLAUDE.md` balance.

### 2026-10-28 16:15 to 16:44 UTC — full suite
- 2,212 passed, 10 skipped, 2 failed (27 min 56 s): the two exact counts that new committed cases and
  source runs break (`test_avoidance_runs`: version-5 run folders +4, RF-35's flow sources;
  `test_resolution`: crowd cases +8). Both updated with a note; both pass.

## Open questions / risks

- Same-direction people in an encounter are treated as one "group" by `orca_within_groups` and by the
  analysis's formations (there labelled friends); in a crowd they are strangers.
- The 8 cases come from four source runs (two seeds per density); different crowds would give other
  encounters.

- At a depth tolerance (5 mm or 1 cm), 26 or 34 of 64 would resolve: whether millimetres should count
  is the user's choice (`crowd_report.md`, open question 1).
- The non-verbal condition for the same encounters (as RF-34 did for groups) is not run.

## Summary (fill in at the end)

- **Built:** crowd-encounter cases from RF-18's flow at 25 and 50 per way (`rf35_crowd_v1`, 8 cases);
  `design.others.population` (bystanders from a profile at exact shares, the same for exact repeats);
  RF-35's config; the measure against plain ORCA on the same seed (`groups.contacts`, `against_orca`);
  13 tests.
- **Ran:** 72 sessions, USD 0.070697 with the pilot (cap 0.10), all off-peak; balance USD 0.32.
- **Found:** inside a crowd the LLM's plans do not beat ORCA: 14 of 64 resolved against plain ORCA,
  worse in 50, better in 6; extra collisions in 30 sessions, fewer in 2; the deep ones between the
  encounter's own people. The plans themselves are sensible (keep right, slow when giving way, room for
  a cane), and the debriefs name no source. Report: `runs/rf35_crowd_encounters/crowd_report.md`.
- **Full suite:** 2,212 passed, 10 skipped after the two count updates.
