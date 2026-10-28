# RF-34: round 1 (head-on) with three or four people, non-verbal

Issue #115, track #55; follows RF-32 (#110). Paid run of 2026-10-28 (Wednesday, off-peak, calls 11:02 to
11:30 UTC), approved by the user for this issue only with a cap of USD 0.20 (`CLAUDE.md`, pending item 1).
Every number below comes from a file named with it; the process is in `WORK_LOG-115.md`. The per-pair
tables are `analysis/group_analysis.md` (machine-written), `analysis/group_pairs.csv` (one row per
conflict pair) and `analysis/group_summary.json`.

## In short

- **Seeing each other move and signal helps groups a little, not to the pairs' level.** 9 of 64 design
  sessions resolved in `plan_only` (0.14, 95% CI 0.08 to 0.25), against **4 of 64 in RF-32's
  independent run** (0.06) and **37 of 64 for round 1's pairs in the non-verbal condition** (RF-30,
  0.58, 0.46 to 0.69; Fisher's exact test p < 0.0001). 2 v 1: 7 of 32 (0.22). 2 v 2: 2 of 32 (0.06).
- **The gain over RF-32 is not significant, and it is not the same sessions.** Paired by cell and case:
  9 sessions resolved here only, 4 in RF-32 only, **none in both**, 51 in neither (exact sign test
  p = 0.27). Which session resolves looks like chance, as RF-11 found for pairs.
- **What fails is still the meeting with the oncoming people.** All 58 collisions are between people
  walking opposite ways, none between friends, at 6.0 to 7.7 s, when the groups meet.
- **What changes: groups now lean right, as pairs did.** The resolved conflict pairs passed right to
  right 20 times and left to left 4 times (RF-32: 7 and 7; RF-30's non-verbal pairs: 23 and 14). One
  friend falling in behind the other now works far more often (11 of 14 such meetings passed cleanly,
  against 2 of 8 in RF-32).
- **Signals are few and carry no side**: 48 in 64 sessions, nods (24) and a raised hand (22); RF-30
  found the same with pairs. Each person's three decision points are mostly used by 4.4 s (median),
  and the first collision comes a median 1.7 s after the last one (pairs: also 4.4 s).
- **Round 1's rules:** as with independent groups, under ORCA the left-turn rule resolves all 64 group
  meetings (plain ORCA none), the cane rule none; no rule reproduces what the agents did much better
  than plain ORCA (best: RF-12's slow-down, 8 of 37 resolved conflict pairs; plain ORCA 1).
- **The assertiveness rule weakens here**: a person who holds their ground did not slow in 15 of 32
  first plans (RF-32: 20 of 32; round 1: 21 of 33).

## 1. The run

| | |
| --- | --- |
| Cases, design | RF-32's run of record (`round1_group_head_on_orca_groups.yaml`), unchanged: `rf32_group_v1` (2 v 1 and 2 v 2, round 1's 1.75 m corridor, aligned and 20 cm apart, friends abreast 0.63 m apart); 16 cells × 4 cases, seed 110, so the same people; 8 exact repeats; 72 sessions |
| As RF-32 | `resolve_v6`, `resolve_factors_v2`, `keep_line`, `no_conflict_waits_for_plans`, `orca_within_groups`, `deepseek-flash` at temperature 1.0, reply cap 300 |
| What differs | **the condition: non-verbal** (D3: signals and movement, up to 3 decision points each, D5), the user's decision of 2026-10-28 after RF-32; and `protocol.distance_to_partner: true` (below) |
| Pilot | `runs/rf34_round1_group_head_on_non_verbal`: 8 sessions, USD 0.018599, as built; not used below |
| This run | `runs/rf34_round1_group_head_on_non_verbal_partner`: all 72 sessions, 990 calls, USD 0.150197 |
| Cost | **USD 0.168796 for #115** (pilot and run) of the USD 0.20 cap; all off-peak, no transport error. Balance USD 0.56 → **0.39** |
| Unreadable | 10 of 722 decision points after their retry (8 a later step's `start` written as an event, 2 an unknown `until`); none refused on a distance |

**`distance_to_partner` (the user's decision after the pilot).** A reply's `at_distance_m` was checked
against the time-to-meet person, else the nearest person in view. In a group, once one friend falls in
behind the other, the nearest is the friend just ahead (0.5 to 0.7 m), while the plan is carried out
against the oncoming partner 5 to 7 m away; "until 3 m" was refused twice and the decision point lost
(5 of 83 in the pilot). With the setting on, the check uses the partner, as the executor does. A refused
reply changes what happens next, so the pilot could not be re-executed: all 72 sessions ran again.

## 2. Resolved, by layout (`analysis/group_analysis.md`)

| Layout | Resolved in `plan_only` (95% CI) | RF-32, independent | Fisher p against RF-30's non-verbal pairs | plain ORCA | ORCA + left turn | ORCA + cane rule | ORCA + both |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 v 1, aligned | 5 / 16 (0.31; 0.14 to 0.56) | 2 / 16 | 0.09 | 0 | 16 | 0 | 8 |
| 2 v 1, 20 cm apart | 2 / 16 (0.12; 0.04 to 0.36) | 2 / 16 | 0.002 | 0 | 16 | 0 | 8 |
| 2 v 2, aligned | 2 / 16 (0.12; 0.04 to 0.36) | 0 / 16 | 0.002 | 0 | 16 | 0 | 8 |
| 2 v 2, 20 cm apart | 0 / 16 (0.00; 0.00 to 0.19) | 0 / 16 | < 0.0001 | 0 | 16 | 0 | 8 |
| **all** | **9 / 64 (0.14; 0.08 to 0.25)** | **4 / 64** | **< 0.0001** | **0** | **64** | **0** | **32** |
| round 1's pairs (RF-30, non-verbal) | 37 / 64 (0.58; 0.46 to 0.69) | | | | | | |

**Paired with RF-32** (the same cell and case; exact sign test on the sessions only one resolved):

| Layout | Both resolved | Non-verbal only | Independent only | Neither | p |
| --- | --- | --- | --- | --- | --- |
| 2 v 1, aligned | 0 | 5 | 2 | 9 | 0.45 |
| 2 v 1, 20 cm apart | 0 | 2 | 2 | 12 | 1.0 |
| 2 v 2, aligned | 0 | 2 | 0 | 14 | 0.5 |
| 2 v 2, 20 cm apart | 0 | 0 | 0 | 16 | 1.0 |
| **all** | **0** | **9** | **4** | **51** | **0.27** |

- **The gate** (RF-10's 0.50 in `plan_only`) is not met by groups in either condition.
- **The exact repeats** (4 cells, 3 identical runs each): one 2 v 1 cell resolved 2 of 3, the other three
  0 of 3. With no session resolved in both conditions, the resolved sessions say little about their cell.
- **By factor** (design sessions, 32 each way): with a cane 6, without 3; person 1 holds their ground 3,
  gives way 6; same age 7, person 1 older 2. Too few resolved sessions to estimate an effect.

## 3. What they did

**The later decision points** (`analysis/group_summary.json`, `later_points`): 415 after each person's
first (2.85 decision points a person on average; RF-30's pairs 2.66), 408 readable. What prompted them:
someone oncoming turned (438 reasons), moved left or right (453), slowed (198); the plan failing (78);
the friend coming into view after one fell in behind (59). The median last decision point is at 4.4 s,
the median first collision 1.7 s after it: people use their three decision points while the groups
close in, and none is left for the moment they meet. RF-30's pairs used theirs by the same 4.4 s.

**Signals**: 48 in the design sessions, nod 24, raised hand 22, wave on 1, eye contact 1; seen 76 times by
an oncoming person, 17 by a friend (only one walking behind can see the other). A nod or a raised hand
says "I see you", not which side; RF-30 found the same with pairs.

**First plans** (the first readable plan of each person, `first_plans`):

| | People | Side: right / left / both / none | Slowed | Mean largest turn |
| --- | --- | --- | --- | --- |
| walking alone (2 v 1) | 32 | 17 / 2 / 2 / 11 | 20 | 7.6° |
| walking with a friend | 190 | 93 / 37 / 50 / 10 | 131 | 13.7° |
| RF-32, with a friend (independent) | 186 | 61 / 37 / 78 / 10 | 108 | 12.3° |
| RF-30's pairs (non-verbal) | 123 | 57 / 25 / 37 / 4 | 83 | 13.2° |

The first decision point is the same moment as RF-32's (the trigger), so the shift to the right in the
first plans (93 of 130 one-sided, against 61 of 98 in RF-32) cannot come from anything seen yet. It may
be the model's randomness or the prompt's wording for the condition (signals allowed); this run does not
tell them apart.

**How two friends got past each oncoming person** (in `plan_only`; 160 friend-pair and oncoming-person
meetings):

| Formation when the oncoming person drew level | Meetings | Passed cleanly | RF-32 (independent) |
| --- | --- | --- | --- |
| single file (one friend fell in behind the other) | 14 | **11** | 2 of 8 |
| between (the oncoming person went between the friends) | 11 | 2 | 2 of 10 |
| abreast (the oncoming person passed outside) | 7 | 2 | 0 of 1 |
| not reached (the run stopped on a collision first) | 128 | 0 | 0 of 141 |

Falling into single file, then adjusting as the others move, is what works; opening a gap for someone
to go through still mostly fails.

**Side, among the conflict pairs the plans resolved** (37 of 192; RF-32: 21): right to right 20, left
to left 4, not abreast 13. With pairs RF-11 found 62% keep right; RF-30's non-verbal pairs 23 right, 14 left.

## 4. Do round 1's rules still describe them? (the identity check per conflict pair)

| Rule arm | Reproduced, of the 37 resolved pairs | Same first | Same sides | Pairs resolved by ORCA under it (of 192) | Matched |
| --- | --- | --- | --- | --- | --- |
| plain ORCA | 1 | 8 | 13 | 32 | - |
| RF-31's left turn (`ext_head_on_0ecc2d1a6e` v2) | 3 | 17 | 4 | **192** | 192 |
| RF-31's cane rule (`ext_head_on_6455ca5589` v2) | 2 | 8 | 15 | 32 | 96 |
| both (as RF-18 and RF-33) | 4 | 16 | 11 | 120 | 192 |
| RF-12's slow-down (format 3) | **8** | 15 | 17 | 32 | 192 |
| RF-12's other two (format 3: plain ORCA in effect) | 1 | 8 | 13 | 32 | 192 |

- The left-turn rule still resolves every group meeting under ORCA, and still gets the sides wrong
  (4 of 37), now more so because the agents pass right to right.
- No rule describes the agents: the best, RF-12's slow-down, reproduces 8 of 37 resolved pairs.

## 5. The debriefs

- 252 debriefs: habit 128, common sense 116, none 8. **No debrief names a law, guidance or study**, as
  with pairs and RF-32.
- What they name: the elderly person or the cane in 106, "behind" in 46, "keep right" 30, "keep left" 17,
  "single file" 11, "between" 2. "Keep right" is named more often than in RF-32 (7) and in round 1's
  non-verbal pairs (4 of 128; "keep left" 27): it follows the side they took, not a source.

## 6. What it means

- **For Step 1:** groups do not resolve a head-on at the pairs' rate even when they can see each other
  move and signal (0.14 against 0.58). The independent condition was not the main reason RF-32's groups
  failed. What does help is falling into single file and adjusting; what remains is the same pavement
  dance, now with more people, and decision points that run out before the meeting.
- **For RF-14 (verification):** groups that see each other drift towards keep right (20 of 24 abreast
  resolved pairs), as pairs did; no new source is named. The assertiveness rule weakens (15 of 32 hold
  ground and do not slow). How real groups pass (single file, V-shape, abreast) is for RF-14's evidence
  (Moussaïd et al. 2010; Zanlungo et al. 2017).
- **For RF-18's reruns:** unchanged from RF-32: the left-turn rule removes the stall in small groups
  (64 of 64), the cane rule does not; neither describes the agents.
- **Open for the user** (not done here): the talk condition; a wider corridor for 2 v 2 (0 of 16 in the
  20 cm-apart case, in both conditions); and whether D5's cap of 3 decision points, used up by 4.4 s,
  is too few for groups (a change to the user's design, `resolution.md`).

## 7. Caveats

- **The run stops at the first collision**: 128 of 160 friend-oncoming meetings were never reached, so
  the pair-level numbers are lower bounds. The session-level share is unaffected.
- **Not significant against RF-32** (paired p = 0.27; unpaired Fisher p = 0.24); the design was sized
  for RF-32's comparison with pairs, not for this one.
- **`distance_to_partner`** is new in this run; RF-32's independent sessions did not need it (every
  decision came at the trigger, before anyone fell behind), so the comparison is still like for like.
- RF-32's assumptions carry over (friends told of each other, the oncoming people not; everyone
  prompted; every opposite pair counts; round 1's corridor; 0.63 m between friends).
- One model at temperature 1.0; the exact repeats and the paired table show large randomness.

## Files

`sessions/` (every prompt and raw reply), `replay/` (both replays per session), `outcomes.csv`,
`outcomes.jsonl`, `decisions.jsonl`, `debriefs.jsonl`, `report.md`, `summary.json`, `cost.json`;
`analysis/` (`python -m negsim.resolution.groups runs/rf34_round1_group_head_on_non_verbal_partner
--pairs runs/rf30_round1_head_on_keep_line --pairs-condition non_verbal --against
runs/rf32_round1_group_head_on_orca_groups --arm ...`, the arms as in `analysis/group_summary.json`).
