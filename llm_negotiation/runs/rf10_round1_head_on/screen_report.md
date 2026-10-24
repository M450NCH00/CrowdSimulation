# RF-10: round 1 (head-on in a corridor), Phase A screen

Issue #65, track #55. Paid run of 2026-10-24 (Saturday, off-peak), approved by the user for this
issue only with a cap of USD 0.35 (`CLAUDE.md`, pending item 1). Every number below comes from a
file in this folder; the file is named with it. The process, the decisions and the dead ends are
in `WORK_LOG-65.md`.

## In short

- **Step 1: on their own plans, the LLM agents do not resolve a head-on meeting more often than
  not.** 59 of the design's 192 sessions resolved in `plan_only` (0.31, 95% CI 0.25 to 0.38),
  against a gate of 0.50 fixed in the config before the run. **Head-on fails the gate.** By the
  issue's rule, no rule is extracted from round 1 in RF-11 unless the supervisor says otherwise.
- **They pick compatible sides but sidestep too little.** At the meeting the two were on
  compatible sides in every session (both kept right in 123, both left in 69), but 116 of the
  192 collided: when level, they were a median 0.29 m apart sideways, for bodies 0.5 m wide
  (0.7 m with a load). In the sessions that resolved they were 0.88 m apart.
- **Signalling and talking did not help**: independent 0.34, non-verbal 0.27, talk 0.31; the
  intervals overlap widely.
- **Factors**: after Holm's correction over the whole report, four effects survive, all on *how*
  agents behave rather than on whether they resolve: assertiveness (less slowing), and
  familiarity and perceived attractiveness (more signalling). No factor survives on resolution
  itself; the strongest uncorrected is person 1's assertiveness (OR 0.47).
- **The model's own randomness is large**: identical prompts gave the same behaviour in only 47%
  of repeats on average, and all 24 exact-repeat cells are coin flips (`stability.csv`). No
  counterfactual pair moved behaviour beyond that noise floor.

## 1. The run (`cost.json`, `summary.json`, `../../spend_ledger.jsonl`)

| | |
| --- | --- |
| Sessions | 288 of 288 completed (96 per condition): 192 of the design (32 cells × 2 geometries × 3 conditions), 48 exact repeats (8 cells × 3, per condition), 48 in 4 counterfactual pairs |
| Factors | 16 two-level factors in a 2^(16-11) resolution IV fraction (`config.json`) |
| Template and execution | `resolve_v6` (RF-9's fixes), `protocol.execution: as_prompted`, `no_conflict_waits_for_plans` |
| Sends | 1,887 (1,316 decisions, 571 debriefs), all off-peak, no API error |
| Cost | **USD 0.289517** (ledger), USD 0.00101 a session: independent 0.00056, non-verbal 0.00133, talk 0.00120 (RF-9: 0.00046, 0.00104, 0.00107) |
| Balance | USD 1.41 before, **USD 1.13** after (`GET /user/balance`): consistent with the ledger at cent precision |
| Unreadable replies | 63 of 1,887 sends (3.3%; RF-9's pilot: 63 of 492, 12.8%); 30 of 1,283 decision points (2.3%) still unreadable after the retry |

Cost per session rose because non-verbal and talk sessions now use their decision points: the
encounter stays open while plans run (RF-9's third fix).

**RF-9's fixes worked on the model.** The model wrote 1,098 of its 2,763 step ends (40%) as
`{"at_distance_m": d}`, the form `resolve_v6` added, and no event as an object; the drift wording
("in the opposite direction to you, drifting to your left by N°") replaced "walking across"
everywhere it applied. **A new unreadable form** took most of what is left: an event used as a
later step's start (`"start": "other_passes"`, 53 sends), which `resolve_v6` does not accept. A
later template could read it as "when the other has passed"; nothing was changed mid-run.

## 2. Step 1: can the agents resolve it? (`analysis/gate.md`, `analysis/lateral.md`)

**The gate**, fixed before the run (`config.json`, `resolution_gate`): the encounter type counts as
resolved by the LLM if at least 0.50 of the design's sessions resolve in `plan_only`, pooled over
32 cells × 2 geometries × 3 conditions (exact repeats and pairs left out). The reason is recorded
with it: a judgement, not a sourced number.

| Group | Resolved in `plan_only` | Rate (95% CI) |
| --- | --- | --- |
| **All (the gate)** | **59 / 192** | **0.31 (0.25 to 0.38): fails** |
| Independent | 22 / 64 | 0.34 (0.24 to 0.47) |
| Non-verbal | 17 / 64 | 0.27 (0.17 to 0.38) |
| Talk | 20 / 64 | 0.31 (0.21 to 0.43) |
| Walking lines aligned | 32 / 96 | 0.33 (0.25 to 0.43) |
| Walking lines 20 cm apart | 27 / 96 | 0.28 (0.20 to 0.38) |
| Baseline: `plan_orca` (the plans, with ORCA on top) | 65 / 192 | 0.34 (0.28 to 0.41) |
| Baseline: plain ORCA | 0 / 192 | 0.00 (0.00 to 0.02) |

- "Resolved" is the scenario's: both cleared with no collision, no near miss and no deadlock. Plain
  ORCA never collides here but always passes within the near-miss distance, so it never counts
  as resolved (as in RF-9).
- Weighted back to two residents met at random (`ethnicity_weight`), all 288 sessions: 0.331
  against 0.326 unweighted, from 90 effective sessions (`report.md`, section 8).
- RF-9's pilot resolved 0.24 under `resolve_v5`, with 63 unreadable sends; the fixes moved the
  rate up a little but not near the gate.

**How it fails.** Of the 133 unresolved sessions, 116 collided, 17 were near misses, and none
deadlocked. The sides are not the problem: at the closest approach both agents kept right (in
their own frames) in 123 sessions and both kept left in 69, so every pair chose compatible sides.
The size of the sidestep is the problem:

| `plan_only` outcome | Sessions | Lateral separation when level, median (IQR) | Each agent's move aside, median |
| --- | --- | --- | --- |
| collision | 116 | 0.29 m (0.13 to 0.44) | 0.28 m |
| near miss | 17 | 0.62 m (0.56 to 0.68) | 0.34 m |
| resolved | 59 | 0.88 m (0.73 to 0.97) | 0.45 m |

Each agent is told its body's width: 0.5 m, or 0.7 m when it carries a load (RF-5). So two
centres less than 0.5 to 0.7 m apart sideways collide. The first plans of unresolved sessions turn less (median
largest turn 12°, against 15°), and 19 of them do not turn at all (1 among the resolved). Delayed
starts are rare (3) and plans that step aside and back are not more common among the failures
(28% against 37% of first plans). So the agents agree on a side but under-size the sidestep.
Whether that is the model's spatial judgement or what the description leaves out (it gives the
other's distance and bearing, not how far their walking line is from one's own) is open; it
matters for any rule taken from these plans.

## 3. Independent, non-verbal, talk (task 6)

- Resolution does not differ between conditions (section 2).
- **Signals** were common in the two conditions that allow them: 431 in all (nod 184, eye contact
  122, wave on 98, hold up a hand 27). In non-verbal, sessions in which a signal was seen resolved
  14 of 47, those without 3 of 17; in talk, 15 of 53 against 5 of 11. Too few to say a resolution
  depended on a signal.
- **Talk** was used far more than in RF-9 (messages in 34 of 64 talk sessions, against 1 in 24): 86
  messages, many of them greetings between acquaintances ("Hey, good to see you!") or "Go ahead,
  plenty of room!". Sessions with a message resolved 10 of 34, without 10 of 30.
- So: **no evidence that signalling or talking helps the agents resolve a head-on meeting.** It
  changes what they do (more decision points, greetings), not whether they pass.

## 4. Factors (`analysis/report.md`, `effects_terms.csv`, `flip_rates.csv`)

**What the agents were told.** Each agent's own factors are in every one of its prompts. The other
person's age, gender, observable factors (cane, load, phone), ethnicity and the pairwise lines
(attractiveness, familiarity) were printed at **1,282 of the 1,283 decision points** (`p*_other_*_shown`
and `p*_pairwise_lines_shown` in `outcomes.csv`): under `resolve_v4` and later they are given from
10 m, and every head-on decision point is within 10 m. **Giving them from 10 m is a prompt choice,
not a sourced recognition distance** (the user's decisions of 2026-10-23 and 2026-10-24).

**Significant after Holm's correction** (the family is every term of every model in the report,
fixed before the run):

| Outcome | Factor | Odds ratio [95% CI] | Holm p |
| --- | --- | --- | --- |
| first plan slows down | own assertiveness ("determined and tend to hold your ground") | 0.26 [0.14, 0.48] | 0.015 |
| signals at least once | knows the other (acquaintances) | 221 [23, 2116] | 0.002 |
| signals at least once | finds the other attractive | 5.29 [2.39, 11.72] | 0.027 |

(The fourth and fifth surviving terms are the conditions' effect on the number of decision
points, which is by design.)

**On resolution itself nothing survives.** The largest uncorrected effects on `resolved_plan_only`:
person 1's assertiveness OR 0.47 [0.26, 0.84], p = 0.011; person 1's load OR 0.58 [0.33, 1.02],
p = 0.06; urgency and distraction p ≈ 0.1. With over a hundred terms in the family, an uncorrected
p of 0.01 is weak evidence.

**Separation**, as RF-8 warned: models whose outcome is (nearly) separated by the predictors
(for example `stopped`: 3 events in 576 rows) have no finite estimate and are listed as such in
`report.md`. By the user's decision of 2026-10-24, they are not refitted (no Firth regression); a
factor's claim rests on its counterfactual pair and its descriptive table.

**Counterfactual pairs against the noise floor** (`flip_rates.csv`). Identical prompts flip the
behaviour (who passed first, sides, stopping, backing up together) in 0.86 of pairs (95% interval
0.79 to 0.93), who passed first alone in 0.69, the passing side in 0.42. None of the four pairs
(perceived attractiveness; ethnicity pair; person 2 Chinese → Indian; Malay → Indian; 6 pairs
each) flips any component above the noise floor's upper end. **The screen has no evidence that
the person's group, as the agent was told it, changes behaviour** beyond the model's own
randomness, and it could only have seen a large effect.

**Real ethnicity** (`report.md`, section 8; descriptive, as RF-26 set out). Drawn balanced, the
sessions per pair of groups ran from 6 (Chinese/Others, Malay/Chinese, Others/Indian) to 42
(Malay/Malay), persons 20% to 28% per group (`--plan`). A difference between groups in that table
is the model's behaviour towards people it was told are of a group, never a fact about those
groups. The largest uncorrected term involving it is `same_ethnicity` on planning to the right
(OR 1.59 [1.08, 2.35], p = 0.019), not significant after correction. **No rule may read
ethnicity or perceived attractiveness**, whatever Phase B finds.

## 5. Phase B shortlist (task 7)

Five factors, each kept because it moved a behaviour clearly, even where it did not move
resolution. Only perceived attractiveness had a counterfactual pair in Phase A, and it was not
distinguishable from the noise floor; the others need pairs in Phase B.

| Factor | Effect sizes (OR [95% CI], all conditions) | Against the noise floor | Why kept |
| --- | --- | --- | --- |
| **Assertiveness** (own) | slows: 0.26 [0.14, 0.48], Holm-significant; resolves (p1): 0.47 [0.26, 0.84]; signals: 11.8 [2.7, 50.9] | no pair yet | The one factor that moves both the plan and, uncorrected, resolution. |
| **Familiarity** (acquaintances) | signals: 221 [23, 2116], Holm-significant; slows: 2.36 [1.41, 3.96]; plans right: 1.88 [1.26, 2.79] | no pair yet | Changes the whole exchange (greetings, signals); a candidate for "people who know each other negotiate". |
| **Residence** (visiting from the United States) | plans right: 2.37 [1.42, 3.95], p < 0.001 uncorrected; kept left at the meeting: 0.58 [0.33, 0.99] | no pair yet | Bears directly on a keep-left or keep-right rule, which the supervisor named, and on RF-14's check against Singapore. |
| **The other's age** (70 against 25) | slows: 3.44 [1.57, 7.57]; kept left: 0.50 [0.29, 0.87] | no pair yet | Giving way to an older person is a plausible, checkable convention. |
| **Perceived attractiveness** (finds the other attractive) | signals: 5.29 [2.39, 11.72], Holm-significant; slows: 1.97 [1.26, 3.06]; passed first: 0.38 [0.16, 0.91] | pair: who first 0.33 (noise 0.69), side 0.67 (noise 0.42), not distinguishable | The bias the user asked about. **May be studied, never read by a rule.** |

Next in line, about as strong (uncorrected) as the other's age: own distraction (kept left at
the meeting, p = 0.002) and mobility aid (signalling, p = 0.003 for the other's cane, 0.008 for
one's own). The weakest across every outcome: urgency, memory note, time of day, surroundings,
gender and own age (smallest p from 0.03 to 0.09). Ethnicity is in section 4 (`same_ethnicity`,
p = 0.019 uncorrected; no pair beyond the noise floor). The geometry term was nowhere below
p = 0.05.

Phase B (RF-13) should give each shortlisted factor its own counterfactual pairs, with more pairs
per factor than here (6 is too few against a noise floor of 0.4 to 0.9).

## 6. Caveats

- **Underpowered for 16 factors**, as planned (`WORK_LOG-65.md`): about 94 resolved sessions in
  288, 59 in the design. Only large effects could show.
- **The gate is a judgement** (0.50), recorded before the run with its reason. Against people, who
  almost never collide head-on, it is lenient.
- **Near misses count as failures.** 17 sessions passed within the near-miss distance without
  touching. Counting them as resolved would give 76 of 192 (0.40), still below the gate.
- **The model's randomness** (temperature 1.0, unchanged) dominates repeated behaviour; a lower
  temperature is the user's or the supervisor's decision (`llm-backend.md`, section 2).
- **One scenario.** These are head-on findings only (D15).
