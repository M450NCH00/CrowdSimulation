# RF-35: encounters sampled from crowds (Step 1, independent, two densities)

Issue #117, track #55. Paid run of 2026-10-28 (Wednesday, off-peak, calls 14:10 to 14:53 UTC), approved
by the user for this issue only with a cap of USD 0.10 (`CLAUDE.md`, pending item 1). Every number below
comes from a file named with it; the process is in `WORK_LOG-117.md`. The machine-written tables are
`analysis/group_analysis.md`, `analysis/group_pairs.csv` (one row per conflict pair) and
`analysis/group_summary.json`; `report.md` is the run's own report.

**Why this run (the user's question of 2026-10-28).** Round 1's rules came from two-person sessions and
were then judged in crowds of 100 (RF-18, RF-33). Prompting a whole crowd would cost a call per person
per decision. Instead, a crowd runs under ORCA and one encounter in it is handed to the LLM: the two who
start a head-on conflict and anyone within 10 m predicted to conflict with them, at most 4 prompted;
everyone else stays ORCA and is part of what the prompted people see. The cost grows with the number of
encounters, not the size of the crowd.

## In short

- **The LLM's plans do not beat ORCA inside a crowd.** Scored against plain ORCA on the same seed (the
  user's measure, below), **14 of 64 design sessions resolved** (0.22, 95% CI 0.14 to 0.33): 8 of 32 at
  25 per way, 6 of 32 at 50 per way. Per session the plans were better than plain ORCA in 6, the same in
  8 and **worse in 50** (sign test p < 0.001). Nobody was stuck under either.
- **"Worse" is mostly a few millimetres.** In 32 of 64 sessions the encounter's people collided exactly
  as often as under plain ORCA, and the verdict turned on the deepest overlap (median 14 mm with plans,
  5 mm without; the deepest 54 mm). Counting depths within 1 cm as equal, 34 of 64 would be resolved
  (0.53, 0.41 to 0.65). What does not depend on that choice: **the plans added collisions in 30 of 64
  sessions and removed them in 2** (389 against 336 over all 64).
- **The extra contact is between the encounter's own people.** Of the 389 collisions with an encounter
  member after its start, 247 are grazes with oncoming bystanders (median 2.8 mm), but the deep ones are
  between the encounter's own people walking opposite ways: 72 collisions, median 13.8 mm, up to 54 mm.
  The prompted people's plans steer them into each other more than ORCA would; the bystanders matter less.
- **The pair measure cannot be met in a crowd, by anyone.** Under the scenario's own definition (every
  conflict pair clear with no collision or near miss), 0 of 64 sessions resolved in `plan_only`, and 0
  under plain ORCA. Of 264 conflict pairs, 12 resolved with plans (11 right to right) and none under
  plain ORCA. Round 1's pairs, for scale: 35 of 64.
- **The plans read as sensible.** In 205 readable first plans (216 people, the 64 design sessions)
  nobody stopped, backed up or "carried on"; nearly half slowed (96); side changes were right more often
  than left (70 right, 38 left, 68 both ways, 29 none).
  People step towards a wall, slow for someone with a cane, pass a slow walker ahead. A person who holds
  their ground rarely slowed (10 of 82); one who gives way usually did (86 of 134).
- **The debriefs give no source.** 124 common sense, 88 habit, 16 none; no study, code or custom named.
  "Keep right" came up 26 times, "keep left" 8 (round 1's pairs: 3 and 12).
- **Cost USD 0.0707** for 72 sessions, 484 calls, inside the cap; balance USD 0.39 → **0.32**.

## 1. The run

| | |
| --- | --- |
| Crowds | RF-18's two-way flow (`bidirectional_flow`) at **25 and 50 people per way** (50 and 100 people), plain ORCA, two repeats each: `runs/rf35_source_crowd_flow` (free). Collisions per source run 16 and 15 at 25 per way, 91 and 81 at 50 |
| Cases | `rf35_crowd_v1`: of 302 head-on pairs at tier T3 and above, two per density and tier (T3, T4): `flow_1b5b9b8d`, `flow_b0c1353e`, `flow_06018e0c`, `flow_61f018fc` (25 per way); `flow_32e86a8e`, `flow_826d5092`, `flow_9274de21`, `flow_bf8bfa07` (50 per way) |
| Encounter | `passing_crowd`, `max_prompted: 4`. Every encounter reached the cap (on average 22 more people within 10 m left to ORCA, 10 to 39). 2 to 4 of the 4 prompted (a member is prompted only once it perceives someone it conflicts with): 4 in 32 sessions, 3 in 24, 2 in 8 |
| Design | `sample`, 8 cells of age pair, gender pair, cane and assertiveness for the two who start the conflict; seed 117; 64 sessions plus 8 exact repeats (4 × 3), so 72 |
| Bystanders | Everyone else drawn from RF-33's `singapore_street_v1` at exact shares (age, gender, cane, phone), the same for one case and cell (`design.others.population`, new). A bystander's cane or phone is shown to whoever sees them |
| As RF-32 | `resolve_v6`, `resolve_factors_v2`, `keep_line`, `orca_within_groups`, the independent condition, `deepseek-flash` at temperature 1.0, reply cap 300 |
| New for crowds | `distance_to_partner: true` (RF-34's setting: in a crowd the nearest person in view may be a stranger) |
| Pilot | the first 8 sessions (USD 0.008887), then the user's decision on the measure; they are part of the 72 |
| Cost | **USD 0.070697** for 72 sessions (pilot included), 484 calls (256 decisions, 228 debriefs), all off-peak, no transport error; 6.7 calls a session |
| Unreadable | 12 of 240 decision points after their retry (9 an `until` distance beyond the current one); one refusal in the pilot was genuine (the partner was 0.67 m away, the reply said until 1.4 m) |

In the independent condition each prompted person decides once, at the trigger: no later decision
points in any session.

## 2. The measure (the user's decision after the pilot)

The pilot showed that the pair measure (no collision, no near miss) fails almost every crowd pair, plain
ORCA included: a dense ORCA flow grazes all the time (1 to 30 mm). **The user chose (2026-10-28) to score
a crowd encounter against plain ORCA on the same seed:** resolved when, from the encounter's start, its
people collide no more often and no deeper than under plain ORCA, and none is stuck (a deadlock, or not
arriving). Collisions count every episode that involves one of the encounter's people and ends at or
after its start, walls included. Each session is better, the same or worse than plain ORCA (by stuck,
then count, then depth); the sign test is over sessions (`groups.py`, `contacts`, `against_orca`). The
pair measure stays in the tables for comparison.

## 3. Results

| Density | Sessions | Resolved against plain ORCA (95% CI) | Better | Same | Worse | Collisions, plans / plain ORCA | Pair measure, plans / plain ORCA |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 25 per way | 32 | 8 (0.25; 0.13 to 0.42) | 0 | 8 | 24 | 163 / 152 | 0 / 0 |
| 50 per way | 32 | 6 (0.19; 0.09 to 0.35) | 6 | 0 | 26 | 226 / 184 | 0 / 0 |
| All | 64 | **14 (0.22; 0.14 to 0.33)** | 6 | 8 | 50 | 389 / 336 | 0 / 0 |

**How sensitive this is to depth.** The measure counts any extra depth as worse, even a fraction of a
millimetre (one exact-repeat set is "worse" with one collision of 0.9 mm). Counting differences in depth
up to a tolerance as equal:

| Depth tolerance | Resolved of 64 |
| --- | --- |
| none (the measure of record) | 14 |
| 5 mm | 26 |
| 1 cm | 34 |
| 2 cm | 34 |

The collision count does not depend on the tolerance: more than plain ORCA in 30 sessions, the same in
32, fewer in 2 (sign test p < 0.001).

**Who collides** (with plans, from each replay's `events.jsonl`, episodes ending at or after the start
that involve an encounter member):

| Pair | Collisions | Median overlap | Deepest |
| --- | --- | --- | --- |
| member and oncoming bystander | 247 | 2.8 mm | 15.3 mm |
| two members, opposite ways | 72 | 13.8 mm | 53.8 mm |
| member and bystander, same way | 42 | 4.0 mm | 26.5 mm |
| two members, same way | 28 | 7.2 mm | 17.8 mm |

Collisions start a median 1.3 s after the encounter's start. The plain ORCA runs are not saved per
session, so the same table for plain ORCA is not available.

**Exact repeats.** The four sets of three gave identical scores within each set (verdict, collisions,
depth), at temperature 1.0.

**Encounter size.** Every session had 4 people in its encounter, so the share by encounter size has one
row (0 of 64 under the pair measure).

## 4. First plans and debriefs

| | People | Slowed | Right | Left | Both | None |
| --- | --- | --- | --- | --- | --- | --- |
| All first plans | 216 (205 readable) | 96 | 70 | 38 | 68 | 29 |
| Gives way | 134 | 86 | 57 | 31 | 41 | 0 |
| Holds ground | 82 | 10 | 13 | 7 | 27 | 29 |
| Facing someone with a cane | 77 | 32 | 26 | 17 | 24 | 8 |
| Round 1's pairs (for scale) | 128 | 90 | 53 | 17 | 47 | 6 |

(The kinds overlap; "gives way" and "holds ground" are the person's assertiveness. Counts of readable
plans; `analysis/group_analysis.md`, "First plans".)

Some first intents, as written: "Step aside toward the wall on my right to let the oncoming people pass,
since I give way easily"; "Keep my line and speed toward the supermarket, holding my ground against the
oncoming crowd"; "Slow down and ease to the right a little to let the older man pass and keep distance
from the person ahead of me".

Debriefs (all 72 sessions, 228): common sense 124, habit 88, none 16; no source named. Terms: keep right 26, keep left 8,
behind someone 40, the elderly or a cane 81.

## 5. What this means

- **Step 1 in a crowd: not resolved, as far as this measure goes.** The agents' plans are reasonable as
  intentions but, carried out step by step among 50 or 100 ORCA walkers, they produce slightly more and
  deeper contact than ORCA alone. This is the same pattern as RF-32 and RF-34: what works for two people
  works less well with more people involved.
- **The deep contacts are between the prompted people**, so the problem is coordination between the
  LLM agents (each plans alone in the independent condition), not the bystanders. The non-verbal
  condition helped groups a little (RF-34); it may help here too.
- **Whether a few millimetres should count** is a choice about the measure (open question 1). At a 1 cm
  tolerance about half the encounters resolve; the added collisions in 30 sessions remain either way.
- **For Step 2:** there is no crowd behaviour yet that beats ORCA to extract a rule from. The plans do
  show stable tendencies (keep right; slow down when giving way; give room to someone with a cane) that
  agree with round 1's pairs.

## 6. Open questions

1. Should a depth difference below some tolerance (5 mm, 1 cm) count as the same? It changes 14 of 64
   into 26 or 34. The measure of record stays as the user chose it until they decide.
2. Run the same encounters in the non-verbal condition (as RF-34 did for groups)?
3. Same-direction members are treated as one group by `orca_within_groups` and labelled "friends" by
   the analysis's formations; in a crowd they are strangers.
4. The 8 cases come from four source runs (two seeds per density); other crowds would give other
   encounters.

## 7. Files

- `runs/rf35_crowd_encounters/`: sessions, `decisions.jsonl`, `debriefs.jsonl`, `outcomes.csv`,
  `report.md`, `analysis/`. Replays: each replay's `config.json`, `outcome.json`, `events.jsonl` and
  `trajectory.csv` are committed; the two interaction logs (1.9 GB over 72 sessions) are not, and are
  rebuilt from the session records (`python -m negsim.resolution.replay`).
- `configs/resolution/rf35_crowd_encounters.yaml`, `configs/cases/rf35_*.yaml`, `cases/flow_*.v1.json`.
- `tests/test_rf35_crowd.py`.
