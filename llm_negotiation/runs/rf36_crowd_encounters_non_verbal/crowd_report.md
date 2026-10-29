# RF-36: crowd encounters in the non-verbal condition (Step 1, paired with RF-35)

Issue #119, track #55. Paid run of 2026-10-29 (Thursday, off-peak; pilot calls 04:01 to 04:05 UTC, the
rest 10:01 to 10:36 UTC), approved by the user for this issue only with a cap of USD 0.15 (`CLAUDE.md`,
pending item 1). Every number below comes from a file named with it; the process is in
`WORK_LOG-119.md`. The machine-written tables are `analysis/group_analysis.md`, `analysis/group_pairs.csv`
and `analysis/group_summary.json`; `report.md` is the run's own report.

**Why this run (the user's decision of 2026-10-29, after RF-35).** In RF-35 each prompted person planned
once, alone, and 14 of 64 crowd encounters resolved against plain ORCA; the deep contacts were between
the prompted people themselves. The non-verbal condition lets them see each other move and signal and
decide again (up to 3 decision points each, D3, D5). RF-36 is RF-35's 72 sessions with only the
condition changed: the same cases, cells, people, bystanders and seeds, so each session pairs with
RF-35's.

## In short

- **The non-verbal condition did not help in a crowd; if anything it made things worse.** Against plain
  ORCA on the same seed (RF-35's measure), **9 of 60 design sessions resolved** (0.15, 95% CI 0.08 to
  0.26), against RF-35's 13 on the same 60. Paired: both 8, RF-36 only 1, RF-35 only 5 (sign test
  p = 0.22).
- **Compared directly, session by session, RF-36's plans are worse than RF-35's** in 30 of 60, the same
  in 22, better in 8 (p < 0.001); by collisions alone, more in 26, the same in 31, fewer in 3
  (p < 0.001).
- **The plans added collisions against plain ORCA in 39 of 60 sessions and removed them in none**
  (RF-35, the same 60: 29 and 1); 487 collisions against plain ORCA's 321 (RF-35: 373).
- **The extra contact is grazing with bystanders, not the deep contact between the prompted people.**
  Collisions between two prompted people walking towards each other are unchanged (72 against 70,
  median 13.8 mm both). Grazes with bystanders walking the same way tripled (114 against 38, median
  0.4 mm), and with oncoming bystanders rose a little (265 against 238).
- **People did use the condition.** 55 of 60 sessions had later decision points (310 in all) and 127
  raised hands. But **181 of the 310 later decision points fired only because a bystander came into
  view** (D5 as written, kept by the user's decision). In a crowd, "decide again" is mostly about
  strangers, not about the person in the conflict.
- **The pairing holds:** plain ORCA's contacts are identical in all 60 pairs.
- **The design is short by 6 sessions.** The run stopped at the cap: 66 of 72 completed, 60 of the 64
  design sessions (4 at 50 per way missing) and 6 of the 8 exact repeats. The paired comparison is over
  the 60.
- **Cost USD 0.1471** for 66 sessions and the aborted one, 844 calls, at the cap; balance USD 0.32 →
  **0.17**.

## 1. The run

| | |
| --- | --- |
| As RF-35 | the cases `rf35_crowd_v1` (8 encounters from RF-18's two-way flow at 25 and 50 people per way), `passing_crowd` with 4 prompted at most, the `sample` design of 8 cells (seed 117), bystanders from `singapore_street_v1` at exact shares, `resolve_v6`, `resolve_factors_v2`, `keep_line`, `orca_within_groups`, `distance_to_partner`, `deepseek-flash` at temperature 1.0, reply cap 300 |
| Changed | `conditions: [non_verbal]`, with `max_decision_points: 3` (D5, `min_gap_s` 1.0), as RF-30 and RF-34 |
| New | once the driver has released the encounter to ORCA, nobody is prompted (`encounter.not_prompted_after_release`). Without it the first mock session crashed: a conflict pair walking the same way kept the protocol's encounter open after the driver had released it. A prompt after a release always crashed before, so earlier records are unchanged. In the paid run, one session had someone due after a release |
| Pilot | the first 8 sessions (USD 0.017626), then the user's decision to finish the run under the approved cap; they are part of the 66 |
| Completed | 66 of 72: every design session but 67 to 70 (`flow_bf8bfa07`, `flow_32e86a8e` twice, `flow_826d5092`, all at 50 per way), and the exact repeats but the last two (the third copies of `flow_61f018fc_7a65e7bc` and `flow_32e86a8e_4da0c5b8`). Session 67 was aborted after 13 calls by `stop_at_cap`; its cost is in the ledger, it has no record |
| Cost | **USD 0.147095**, 844 calls (628 decisions, 216 debriefs), all off-peak, no transport error; 12.6 calls a session (RF-35 6.7) at USD 0.00017 a call |
| Encounters (all 66) | 2 to 4 of the 4 members prompted: 4 in 33 sessions, 3 in 23, 2 in 10; 64 ended "passed", 2 "no conflict" |

## 2. Results against plain ORCA (the measure of record)

Resolved: from the encounter's start, its people collide no more often and no deeper than under plain
ORCA on the same seed, and nobody is stuck (`groups.py`, `against_orca`; RF-35, section 2).

| Density | Sessions | RF-36 resolved (95% CI) | RF-35, same sessions | Better | Same | Worse | Collisions: RF-36 / RF-35 / plain ORCA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 25 per way | 32 | 8 (0.25; 0.13 to 0.42) | 8 | 0 | 8 | 24 | 193 / 163 / 152 |
| 50 per way | 28 | 1 (0.04; 0.01 to 0.18) | 5 | 1 | 0 | 27 | 294 / 210 / 169 |
| All | 60 | **9 (0.15; 0.08 to 0.26)** | **13** | 1 | 8 | 51 | **487 / 373 / 321** |

(Better, same and worse are RF-36's plans against plain ORCA. RF-35's columns are its sessions with the
same keys: `analysis/group_analysis.md`, "Paired with the other crowd experiment".)

**Paired with RF-35** (same cell and case):

| Density | Pairs | Both | RF-36 only | RF-35 only | Neither | p | RF-36 plans against RF-35's: better / same / worse (p) | By collisions alone (p) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25 per way | 32 | 8 | 0 | 0 | 24 | 1.0 | 3 / 19 / 10 (0.09) | 0 / 22 / 10 (0.002) |
| 50 per way | 28 | 0 | 1 | 5 | 22 | 0.22 | 5 / 3 / 20 (0.004) | 3 / 9 / 16 (0.004) |
| All | 60 | 8 | 1 | 5 | 46 | 0.22 | **8 / 22 / 30 (< 0.001)** | **3 / 31 / 26 (< 0.001)** |

At 25 per way the same 8 sessions resolve under both conditions, and in all 8 the plans' contacts equal
plain ORCA's: the plans change nothing there. The one session only RF-36 resolved
(`flow_32e86a8e_4da0c5b8`, "better": one collision, 0.36 mm deep) is an exact-repeat set, and its second
copy is "worse" (0.91 mm).

**How sensitive this is to depth** (not the measure of record; RF-35's open question 1):

| Depth tolerance | RF-36, of 60 | RF-35, the same 60 |
| --- | --- | --- |
| none (the measure of record) | 9 | 13 |
| 5 mm | 14 | 23 |
| 1 cm | 21 | 31 |
| 2 cm | 21 | 31 |

RF-36 is lower at every tolerance. The collision count does not depend on it: more than plain ORCA in
39 sessions, the same in 21, fewer in none (RF-35, the same 60: 29, 30, 1). The deepest overlap per
session has a median of 15.2 mm with RF-36's plans, 15.3 mm with RF-35's and 5.2 mm under plain ORCA;
the deepest is 56 mm.

**Who collides** (plans, from each replay's `events.jsonl`; episodes ending at or after the encounter's
start that involve a member; the 60 design sessions):

| Pair | RF-36 | RF-35, same 60 | Median overlap, RF-36 | Deepest, RF-36 |
| --- | --- | --- | --- | --- |
| member and oncoming bystander | 265 | 238 | 2.7 mm | 14.5 mm |
| member and bystander, same way | **114** | 38 | 0.4 mm | 24.3 mm |
| two members, opposite ways | 72 | 70 | 13.8 mm | 56.3 mm |
| two members, same way | 36 | 27 | 1.3 mm | 17.0 mm |
| all | **487** | 373 | | |

(Counted with a scratch script that reproduces RF-35's committed table exactly on RF-35's 64 sessions;
collisions start a median 1.5 s after the encounter's start, RF-35 1.3 s.) Seeing each other and
signalling did not reduce the deep head-on contact between the prompted people. The increase is mostly
sub-millimetre grazes with people walking the same way: later plans slow or turn people who are walking
among others going their way.

**Under the pair measure** (every conflict pair clear with no collision or near miss), 0 of 60, as RF-35
and plain ORCA; 6 of 249 conflict pairs resolved (RF-35: 12 of 264). Round 1's non-verbal pairs (RF-30),
for scale: 37 of 64.

**Exact repeats.** Two complete sets of three gave identical scores; two sets ran two copies each, and
one of those differed (better, then worse: 0.36 against 0.91 mm). RF-35's four sets were all identical;
with later decision points, temperature 1.0 shows.

## 3. The non-verbal condition in a crowd

| | RF-36 |
| --- | --- |
| Design sessions with a later decision point | 55 of 60 |
| Later decision points | 310 (283 readable) |
| Of which fired only by a bystander coming into view | **181** |
| Raised hands | 127 (no other signal used) |
| Who saw the signals | 530 sightings by people walking the same way, 109 by oncoming people |
| Reasons naming someone, for later points | `came_into_view` of someone walking the same way 803, `signalled` by an oncoming person 88, the plan ended 48, `came_into_view` of an oncoming person 37, an oncoming person turned 30, plan failing 14, slowed 13, moved sideways 11, sped up 3 |

(The analysis labels people walking the same way "friend"; in a crowd they are strangers, RF-35's open
question 3. `analysis/group_analysis.md`, "Decision points after each person's first".)

**Unreadable replies: 61 of 549 decision points** (all 66 sessions; 46 people), after their retry: 30
first, 19 second, 12 third. 56 are a distance in the plan beyond the current one: `until` (52) or
`start` (4), nearly all at 0.5 to 1.5 m when the partner was 0.5 to 0.8 m away (one 3.0 m at 2.2 m). With `distance_to_partner` the
partner is the right reference, so these refusals are genuine (RF-35 had 9 of the kind); the other 5 are
2 not JSON, 2 an unknown `until` (`after_seconds`) and 1 a step with no `until`. An unreadable reply uses
up the decision point and the person carries on with the plan they had (`protocol.py`). The rate is
higher than RF-35's (12 of 240) because later decision points come when people are already close.

## 4. First plans and debriefs

| | People | Readable | Slowed | Right | Left | Both | None |
| --- | --- | --- | --- | --- | --- | --- | --- |
| All first plans | 203 | 174 | 110 | 70 | 31 | 41 | 32 |
| Gives way | 126 | 112 | 89 | 57 | 26 | 26 | 3 |
| Holds ground | 77 | 62 | 21 | 13 | 5 | 15 | 29 |
| Facing someone with a cane | 75 | 60 | 40 | 27 | 11 | 14 | 8 |
| Round 1's non-verbal pairs (for scale) | 128 | 123 | 83 | 57 | 25 | 37 | 4 |

(The 60 design sessions; "all" is `alone` plus `with_friend`. RF-35's first plans: 216 people, 205
readable, 96 slowed, 70 right, 38 left.) The first plans read as in RF-35: keep right, slow when giving
way, a person who holds their ground rarely slows (21 of 77).

Debriefs (216): common sense 107, habit 101, none 8; **no source named**. Keep right 37, keep left 15,
behind someone 34, the elderly or a cane 63. Round 1's non-verbal pairs, for scale: keep left 27, keep
right 4. In crowds the agents say "keep right" more often than "keep left", as in RF-35 (26 and 8).

## 5. What this means

- **Step 1 in a crowd is still not resolved**, and the non-verbal condition does not change that. Being
  able to see others move and signal, and to decide again, did not reduce the deep contact between the
  prompted people (72 against 70); it added shallow contact with bystanders.
- **D5 decides most later decision points in a crowd.** Prompting again whenever anyone comes into view
  means that 181 of 310 later decisions were about strangers walking past. This is D5 as written, kept by
  the user's decision of 2026-10-29. A D5 that counts only the people in the encounter would give fewer,
  more relevant later decisions, but would be a new design decision, not tested here.
- **The same pattern as RF-30, RF-32 and RF-34:** signalling and deciding again did not help pairs
  (RF-30) and helped groups only a little (RF-34). In crowds it did not help at all.
- **For Step 2:** as after RF-35, there is no crowd behaviour that beats ORCA to extract a rule from.

## 6. Open questions

1. The 6 sessions not run (4 design, 2 repeats) would cost about USD 0.013 at this run's rate. Run them
   (a new cap needed), or keep the 60 pairs? The paired result (5 against 1; 30 worse against 8 better)
   would not turn with 4 more pairs.
2. Should D5 count only the encounter's own people in a crowd? A design decision for the user.
3. RF-35's questions 1 (a depth tolerance) and 3 (strangers walking the same way treated as one group by
   `orca_within_groups`) still apply.

## 7. Files

- `runs/rf36_crowd_encounters_non_verbal/`: sessions, `decisions.jsonl`, `debriefs.jsonl`,
  `outcomes.csv`, `report.md`, `analysis/` (`python -m negsim.resolution.groups
  runs/rf36_crowd_encounters_non_verbal --pairs runs/rf30_round1_head_on_keep_line --pairs-condition
  non_verbal --against runs/rf35_crowd_encounters`). Replays: each replay's `config.json`,
  `outcome.json`, `events.jsonl` and `trajectory.csv` are committed; the two interaction logs are not,
  and are rebuilt from the session records (`python -m negsim.resolution.replay`).
- `configs/resolution/rf36_crowd_encounters_non_verbal.yaml`.
- `negsim/resolution/protocol.py` (no prompt after the driver's release), `negsim/resolution/groups.py`
  (`paired_crowd`, `resolved_within`).
- `tests/test_rf36_crowd_non_verbal.py`.
