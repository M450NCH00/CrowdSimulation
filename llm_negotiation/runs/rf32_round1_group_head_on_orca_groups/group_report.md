# RF-32: round 1 (head-on) with three or four people

Issue #110, track #55. Paid run of 2026-10-28 (Wednesday, off-peak, calls 05:13 to 05:37 UTC), approved
by the user for this issue only with a cap of USD 0.15 (`CLAUDE.md`, pending item 1). Every number
below comes from a file named with it; the process is in `WORK_LOG-110.md`. The per-pair tables are
`analysis/group_analysis.md` (machine-written), `analysis/group_pairs.csv` (one row per conflict pair)
and `analysis/group_summary.json`.

## In short

- **The agents do not resolve a head-on in a small group as they did in pairs.** 4 of 64 design
  sessions resolved in `plan_only` (0.06, 95% CI 0.02 to 0.15), against **35 of 64 for round 1's
  pairs** in the same condition (0.55, 0.43 to 0.66; Fisher's exact test p < 0.0001). 2 v 1: 4 of
  32 (0.12). 2 v 2: 0 of 32. With the exact repeats, 6 of 72.
- **What fails is still coordination with the oncoming people.** All 62 collisions in `plan_only`
  are between people walking opposite ways, none between friends. Most come about 6 s in, when the
  groups meet. Pairs settled on a side (27 of 35 resolved pairs passed right to right); in groups the
  few resolved conflict pairs passed right to right 7 times, left to left 7 times, and not abreast 7 times.
- **The agents do act as groups.** A friend tucks in behind the other ("single file", in 45 of 245
  debriefs "behind"), or a pair splits to let someone through between them. Each worked sometimes:
  2 of 10 times the oncoming person went between the friends, and 2 of 8 times one friend fell in
  behind. Most meetings never got that far: the run stops at the first collision.
- **Round 1's rules, as crowd rules, carry over to groups; as descriptions of the agents, they do
  not.** Under ORCA, the left-turn rule (`ext_head_on_0ecc2d1a6e`) resolves **all 64** group meetings
  (plain ORCA: 0), as it resolved every pair in RF-31. The cane rule resolves none; both rules
  together resolve the 32 without a cane. But on the 21 conflict pairs the agents resolved, no rule
  reproduces what the agents did much better than plain ORCA (left turn 7 of 21, plain ORCA 5 of 21).
- **The one solid rule of RF-11 holds:** a person who holds their ground mostly does not slow in
  their first plan (20 of 32 here, 21 of 33 in round 1). Giving way means slowing less often in a
  group (with a friend, 108 of 186 first plans slowed; round 1's pairs 90 of 123).

## 1. The run

| | |
| --- | --- |
| Cases | `rf32_group_v1` (`docs/cases.md`, section 10): 2 v 1 and 2 v 2 in round 1's 1.75 m corridor, each aligned and 20 cm apart; a pair abreast 0.63 m apart (Zanlungo et al. 2017) |
| Sessions | 72 (64 of the design, 8 exact repeats): 16 cells × 4 cases, independent condition only (the user, 2026-10-27) |
| Design | full factorial on person 1's age (25 or 70), gender, cane and assertiveness; person 1 is the westbound person of the case's pair (in 2 v 1 the one walking alone); companions 25, their companion's gender, no cane, give way |
| As RF-30 | core template `resolve_v6`, factors `resolve_factors_v2`, `protocol.execution: keep_line`, `no_conflict_waits_for_plans`, `deepseek-flash` at temperature 1.0, reply cap 300 |
| New | plug-in `passing_group` (everyone in the case prompted; every pair walking opposite ways counts; WHO YOU ARE WITH for a person walking with a friend); `protocol.orca_within_groups: true` (below) |
| Pilot | `runs/rf32_round1_group_head_on`: 8 sessions, USD 0.00752, as built (ORCA off between friends too); 0 of 8 resolved, 3 of 8 by friends walking into each other |
| This run | the pilot's 8 carried out again under `orca_within_groups` with no call (every decision came at the trigger), and 64 new sessions |
| Cost | **USD 0.061869 for #110** (pilot 0.007520, 58 calls; this run 0.054349, 449 calls); all off-peak, no transport error, no upper-bound costs. Balance USD 0.62 → **0.56** |
| Unreadable | 7 of 252 decision points after their retry (5 a later step's `start` written as an event, e.g. `"other_passes"`) |
| Model | `deepseek-flash` (`DeepSeek-V4.1-Flash-1017` in the price table) |

**`orca_within_groups` (the user's decision after the pilot).** In `plan_only` ORCA was left out
between every two members of an encounter, friends included; the pilot lost 3 of 8 sessions to a
friend walking into the other before they met anyone (for example "tuck in behind my friend",
written as a 20° turn at full speed). The user chose that ORCA keeps friends apart, as it keeps
walls and outsiders, and that the plans alone decide between people walking opposite ways, which is
what `plan_only` measures (`docs/resolution.md`, D6, as amended).

## 2. Resolved, by layout (`analysis/group_analysis.md`)

| Layout | Resolved in `plan_only` (95% CI) | Fisher p against pairs | plain ORCA | ORCA + left turn | ORCA + cane rule | ORCA + both |
| --- | --- | --- | --- | --- | --- | --- |
| 2 v 1, aligned | 2 / 16 (0.12; 0.04 to 0.36) | 0.004 | 0 | 16 | 0 | 8 |
| 2 v 1, 20 cm apart | 2 / 16 (0.12; 0.04 to 0.36) | 0.004 | 0 | 16 | 0 | 8 |
| 2 v 2, aligned | 0 / 16 (0.00; 0.00 to 0.19) | < 0.001 | 0 | 16 | 0 | 8 |
| 2 v 2, 20 cm apart | 0 / 16 (0.00; 0.00 to 0.19) | < 0.001 | 0 | 16 | 0 | 8 |
| **all** | **4 / 64 (0.06; 0.02 to 0.15)** | **< 0.0001** | **0** | **64** | **0** | **32** |
| round 1's pairs (RF-10 under `keep_line`, independent) | 35 / 64 (0.55; 0.43 to 0.66) | | 0 | | | |

- **The gate.** RF-10's gate (0.50 of the design sessions in `plan_only`) would not be met by groups:
  0.06. RF-30 met it narrowly with pairs (0.53 pooled over three conditions). The comparison is with
  round 1's independent pairs, the same condition.
- **The exact repeats** (4 cells, 3 identical runs each): the two 2 v 1 cells resolved 1 of 3 each, the
  two 2 v 2 cells 0 of 3. One resolved session in a cell is not a property of the cell.
- **2 v 2 in round 1's corridor** cannot be passed four abreast (2.0 m of bodies in 1.75 m), so
  someone must fall in behind. That is part of what was tested (the user answered "Run as built"),
  and it may be the corridor as much as the agents.

## 3. How they failed, and what they tried

**Every collision is with an oncoming person** (62 of 72 sessions; 3 more ended in a near miss and
1 otherwise), none between friends. 56 of the collisions came 5.5 to 6.5 s into the run, when
the groups meet.

**First plans** (the first readable plan of each person; `analysis/group_summary.json`, `first_plans`):

| | People | Side of the turns: right / left / both / none | Slowed | Mean largest turn |
| --- | --- | --- | --- | --- |
| walking alone (2 v 1) | 31 | 11 / 0 / 9 / 11 | 16 | 7.1° |
| walking with a friend | 186 | 61 / 37 / 78 / 10 | 108 | 12.3° |
| round 1's pairs | 123 | 53 / 17 / 47 / 6 | 90 | 12.8° |

- **The lone person turns less** (7.1° on average; 11 of 31 do not turn at all). Some hold their
  line and leave it to the pair ("holding my line so they make room for me"); others ease aside
  ("shift slightly to the left to give the two oncoming men room to pass"). The intents were read,
  not coded.
- **Friends turn left more often than pairs did** (37 of 98 one-sided plans, against 17 of 70),
  because **most turn away from their friend**: of the 106 one-sided first plans of friends in all
  72 sessions, 86 turn to the side away from the friend and 20 towards them (WHO YOU ARE WITH told
  each which side the friend was on): the pair opens up to let someone through between them.
- **Nearly every plan starts now**, as in round 1 (1 of 217 starts at a distance).

**How two friends got past each oncoming person** (in `plan_only`; 160 friend-pair and oncoming-person
meetings):

| Formation when the oncoming person drew level | Meetings | The oncoming person resolved its pair with each friend |
| --- | --- | --- |
| between (the oncoming person went between the friends) | 10 | 2 |
| single file (one friend fell in behind the other) | 8 | 2 |
| abreast (the oncoming person passed outside) | 1 | 0 |
| not reached (the run stopped on a collision first) | 141 | 0 |

**Side, among the conflict pairs the plans resolved** (21 of 192): right to right 7, left to left 7,
not abreast 7. Round 1's resolved pairs: right to right 27, left to left 8. The keep-right majority of
pairs (RF-11: 62%) does not show in groups.

## 4. Do round 1's rules still describe them? (the identity check per conflict pair)

Each rule switched on with ORCA, on each session's own run and seed, everyone carrying what the
session gave them (age, gender, the cane, their own assertiveness), against the session's own
`plan_only` per conflict pair. A rule **reproduces** a pair when the same person left the conflict
zone first and both passed on the same sides (RF-31's measure).

| Rule arm | Reproduced, of the 21 resolved pairs | Same first | Same sides | Pairs resolved by ORCA under it (of 192) | Matched |
| --- | --- | --- | --- | --- | --- |
| plain ORCA | 5 | 8 | 12 | 32 | - |
| RF-31's left turn (`ext_head_on_0ecc2d1a6e` v2) | 7 | 15 | 7 | **192** | 192 |
| RF-31's cane rule (`ext_head_on_6455ca5589` v2, RF-33's database) | 6 | 10 | 12 | 32 | 96 |
| both (cane rule wins where both match, v3, as RF-18 and RF-33) | 6 | 12 | 9 | 120 | 192 |
| RF-12's slow-down (format 3) | 9 | 12 | 12 | 32 | 192 |
| RF-12's other two (format 3: plain ORCA in effect) | 5 | 8 | 12 | 32 | 192 |

- **As a stall-remover, the left-turn rule carries over to groups.** Every group meeting resolves under
  it, with no collision and no near miss, while plain ORCA passes every group within the
  near-miss distance. Its translation sends everyone left; in a group that is consistent, so groups
  pass left to left as pairs did.
- **As a description of the LLM agents, no rule holds up.** The agents resolved too few pairs (21)
  for the check to say much. On those, the left-turn rule gets the first person out right more often
  (15 against 8), but the sides less often (7 against 12), because the agents passed right to right as
  often as left to left. RF-31 found the same with pairs (0.20 against plain ORCA's 0.36).
- **The cane rule** (whoever faces a person with a cane slows) matches in the 32 sessions with a cane,
  and under it ORCA resolves none of them, as in RF-31's identity check and RF-33's gridlock. The agents
  facing a cane slowed in 49 of 76 first plans (0.64), against 108 of 186 for all friends (0.58): a small
  difference, not the rule.

## 5. The debriefs (`analysis/group_summary.json`, `debriefs`)

- 245 debriefs, kinds: common sense 154, habit 78, none 11, local custom 2 (pairs: local custom 12 of
  123). **No debrief names a law, guidance or study** (no source given), as with pairs.
- What they name: the elderly person or the cane in 111 (half the sessions had one), "behind" in 45
  (falling in behind a friend), "keep right" 7, "keep left" 3, "single file" 1. Pairs said "keep left"
  12 times in 123 debriefs; in groups the stated convention is rarer still, and nothing new is named:
  no rule or source that pairs did not give.

## 6. What it means: does round 1's rule hold with more people?

- **For Step 1:** with three or four people the LLM agents mostly fail a head-on that pairs resolved
  about half the time. They try group strategies (one falls behind, or the pair splits), but in the
  independent condition each decides once, alone, and the plans of five or six people rarely fit
  together. The pavement dance that remained for pairs (RF-30) becomes the common case.
- **For RF-14 (verification):** the agents' behaviour in groups gives no new support to a keep-right
  or keep-left convention (sides split evenly), and no new source. The assertiveness rule (holds ground,
  does not slow) holds in groups. Whether people in a group pass this way is for RF-14's evidence:
  how pedestrian groups pass in a corridor (abreast, V-shape, single file) is studied in the dyad
  literature (Moussaïd et al. 2010; Zanlungo et al.), which this run does not test.
- **For RF-18's reruns:** the left-turn rule's "helps" extends to small groups in a corridor (64 of 64
  against plain ORCA's 0); the cane rule fails there too. Neither is a model of what the agents do in a
  group.

## 7. Caveats

- **The run stops at the first collision** (`on_collision: stop`, as round 1's scenario). Pair-level
  numbers after it are censored: 141 of 160 friend-oncoming meetings were never reached, and the 21
  resolved pairs are a lower bound. The session-level share is unaffected.
- **Independent condition only** (the user's choice for this issue): each person decides once at the
  trigger, as pairs did in the comparison. Groups might do better if they could see each other move
  or speak (non-verbal and talk); RF-30 found no gain from either with pairs.
- **The design is small** (4 factors on one person, 16 cells), so the factor effects are not estimated
  here; with 4 resolved sessions there is nothing to estimate.
- **Assumptions of the build** (`WORK_LOG-110.md`): friends are told they walk together and on which
  side; the oncoming people are not told the others are together; everyone in the case is prompted;
  every opposite pair counts; round 1's corridor; 0.63 m between friends (measured in a Japanese mall).
- **`orca_within_groups`** is the user's reading of `plan_only` for groups, decided after the pilot.
  The pilot's own folder keeps the result as built (0 of 8, 3 by friends).
- The 8 re-executed pilot sessions keep their live encounter end (under the old rule: all
  collisions); their physical columns are the new replays'. All 8 also collide under the new rule.
- One model at temperature 1.0; the exact repeats show large randomness.

## Files

`sessions/` (every prompt and raw reply; 8 with `reexecuted_from`), `replay/` (both replays and plain
ORCA per session), `outcomes.csv`, `outcomes.jsonl`, `decisions.jsonl`, `debriefs.jsonl`, `report.md`,
`summary.json`, `cost.json`; `analysis/` (this issue's per-pair analysis:
`python -m negsim.resolution.groups runs/rf32_round1_group_head_on_orca_groups --pairs
runs/rf10_round1_head_on_keep_line --arm ...`, the arms as in `analysis/group_summary.json`).
