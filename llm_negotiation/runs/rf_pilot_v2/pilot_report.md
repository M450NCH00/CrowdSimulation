# RF-9 pilot report: round 1 (head-on), Step 1, all three conditions

Issue #64. Model `deepseek-flash` (DeepSeek-V4.1-Flash-1017), temperature 1.0, reply cap 400
tokens, thinking off. Run on Saturday 2026-10-24, all off-peak. Every number here is computed from
the committed files named beside it; nothing is a finding about people.

## 1. What was run

| Run | Folder | Template, execution | Sessions | Spend (ledger) |
| --- | --- | --- | --- | --- |
| First batch, paused | `runs/rf_pilot/` | `resolve_v4`, `rf4` | 12 of 72 | USD 0.013398 |
| The pilot | `runs/rf_pilot_v2/` | `resolve_v5`, `as_prompted` | 72 of 72 | USD 0.061703 |
| **Issue #64** | | | **84** | **USD 0.075101** of the USD 0.20 cap |

The design (both runs): `wide_corridor_head_on` on two geometries (walking lines aligned, and 20 cm
apart), the 2 x 2 x 2 cells of `age_pair` (same, p1 older), `gender_pair` (p1 female, p1 male) and
`mapping`, both errands non-urgent, plus an exact-repeat set of 2 cells run 5 times each: 24
sessions per condition. The other's age and gender are given from 10 m (`resolve_v4` and later).

**Why the first batch was paused** (`WORK_LOG-64.md`): 14 of its 60 decision points were
unreadable after the retry (a `start` on a later step), and none of its 12 sessions resolved,
because the executor did not do what the prompt tells an agent a plan does: a turn of θ held the
agent about 2 m × tan θ from its path, and after a step the agent was steered back to its old line.
The user chose to allow a start on any step (`resolve_v5`) and to carry plans out as prompted
(`protocol.execution: as_prompted`). Replayed under `as_prompted`, the first batch's own plans
resolve 4 of 12 (0 under `rf4`). The rest of this report is the second run unless it says otherwise.

The DeepSeek balance went from USD 1.49 before the first paid call to USD 1.41 after the pilot:
USD 0.08 billed, against the ledger's estimate of USD 0.075 (the balance is shown to the cent).

## 2. Tokens and cost (`analysis/pilot_measures.md`, `cost.json`)

| | Sends | Prompt tokens mean / max | Reply tokens mean / max | Cache-hit share | Cut off at the cap | Largest share of the preview's bound on one prompt |
| --- | --- | --- | --- | --- | --- | --- |
| Decision point | 351 | 991 / 1,361 | 138 / 214 | 0.72 | 0 | 0.51 |
| Debrief | 141 | 1,551 / 1,889 | 75 / 113 | 0.68 | 0 | 0.44 |

- **Actual cost USD 0.061703 against a worst-case preview of USD 4.85**: a session used at most
  1.9% of its bound. Cache hits are 70% of input tokens (the fixed system message is reused).
- **Per session, off-peak:** independent USD 0.00046 (max 0.00057), non-verbal 0.00104 (max
  0.00137), talk 0.00107 (max 0.00136); all 72: USD 0.00086 on average. At peak, double.
- **Sends per session** (a retried call counts twice): independent 4.0 (bound 4 calls), non-verbal
  8.7 (max 11; bound 8 calls), talk 7.8 (max 9; bound 8 calls).
- **Decision points per agent:** independent always 1; non-verbal 3 for 39 of 48 agents, 2 for 5,
  1 for 4; talk 3 for 44 of 48, 1 for 4. The cap of 3 is reached in most interactive sessions.
- **Limits:** no reply came near the 400-token cap (largest 214), and no prompt came near the
  preview's bound (at most 51%). The history of earlier decisions stays one line each.

## 3. What the agents did

**Trigger reasons** (non-verbal / talk): `other_turned` 72 / 84, `other_moved_left` 37 / 34,
`other_moved_right` 15 / 36, `plan_failing` 23 / 13, `other_slowed_down` 4 / 8; every encounter
starts with `trigger` and `perceives`.

**Unreadable replies, by reason:** 63 of 492 sends; after the retry, 27 of 315 decision points
(8.6%) had no readable reply (independent 3 of 48, non-verbal 23 of 131, talk 1 of 136).
- `unknown_until`, 58 sends: an event written as an object (`{"other_passes": true}`, `1` or
  `null`), or a step meant to end at a distance (`{"at_distance_m": 2.0}`), which the format does
  not offer.
- `not_json`, 5 sends.
- Under `resolve_v4` (first batch) the commonest was `start_on_later_step` (34 of 81 sends);
  `resolve_v5` removed it.

**Signals and speech:** almost none. Non-verbal: 2 eye contacts, 1 nod in 24 sessions. Talk: 2
eye contacts, 1 raised hand, and **1 spoken message in 24 sessions**.

**Debriefs** (`analysis/debrief_kinds.csv`): of 144, `common_sense` 122 (85%), `habit` 16,
`local_custom` 2, `none` 1, no kind given 3. The bases read as "ordinary courtesy and common sense,
no formal rule or study". Almost no agent names a source.

## 4. Physical outcomes (`outcomes.csv`, `analysis/pilot_measures.md`)

| Condition | `plan_only` resolved | `plan_only` collision | `plan_orca` resolved | `plan_orca` collision | Plain ORCA resolved |
| --- | --- | --- | --- | --- | --- |
| independent | 8 / 24 | 12 | 8 / 24 | 0 | 0 / 24 |
| non-verbal | 5 / 24 | 16 | 8 / 24 | 0 | 0 / 24 |
| talk | 4 / 24 | 19 | 5 / 24 | 0 | 0 / 24 |

- "Resolved" is the scenario's: both cleared, with no collision, no near miss and no deadlock.
  Plain ORCA never collides here but always passes within the near-miss distance (0.005 to 0.01 m),
  so it never resolves. By geometry, `plan_only`: aligned 8 of 36, 20 cm apart 9 of 36.
- **Who passed first** (`plan_only`): mostly `none` (a collision, 47) or `together` (15); one of
  the two clearly first in 10 sessions.
- **Passing sides** (`plan_only`, each in its own frame): both kept to their **right** in 56 of 72
  sessions, both to their left in 16; plain ORCA splits 36 / 36. Among intents that name a side,
  130 say right and 14 left (`intent_v2`). The model keeps right, although Singapore drives on the
  left; RF-14 should check this against what pedestrians there do.
- **Why it often fails**, read from the transcripts: many plans step aside and then step back
  before the meeting ("turn right 20° for 1.5 s, then left 20° for 1.5 s"); and a small drift by
  the other (more than 10° off opposite) is described as "walking across your direction of travel
  ... at 162° to it". 28 of the 30 replies given that description reasoned about the other
  *crossing*.
- **The encounter can end too early.** Prompting stops once no conflict has been predicted for 1 s
  (`no_conflict`, 16 sessions), but the plans keep running. In 3 of those 16 a step back to the
  old line then brought the two together and they collided, with nobody asked again (sample 2).
- More interaction did not help: talk resolved least and collided most. The pilot is too small to
  say whether that is the condition or chance (4 of 24 against 8 of 24).

## 5. Variability (`analysis/noise_floor.csv`, `analysis/stability.csv`)

Identical prompts gave a different outcome often. Over the 6 exact-repeat cells (2 per condition,
5 runs each; 60 pairs of runs), the share of pairs whose outcome differs:

| Outcome | All | Independent | Non-verbal | Talk |
| --- | --- | --- | --- | --- |
| Behaviour (who first, sides, stop, back up) | 0.77 | 0.90 | 0.75 | 0.65 |
| Who passed first | 0.58 | 0.70 | 0.70 | 0.35 |
| Passing side | 0.37 | 0.50 | 0.20 | 0.40 |

5 of the 6 cells are coin flips (stability of behaviour below 0.75). **This is the noise floor a
factor's effect has to clear**, and it is high: a counterfactual pair that changes one factor is
expected to flip the behaviour three times in four even if the factor does nothing.

## 6. Intent against plan (`analysis/intent_summary.csv`, codebook `intent_v2`)

A mismatch is an intent that says something its plan does not do (`analysis/intent.py`). With the
codebook written from these intents (`intent_v2`, task 6): **78 of 286 compared decision points
(27%, 95% CI 22% to 33%)**; independent 13%, non-verbal 34%, talk 27%. The two commonest kinds:
a vague intent ("keep walking to the supermarket and pass Person 1 without fuss") with a plan that
turns (44), and "staying to my right" with no turn, which is consistent if the agent is already on
the right (20): a keyword codebook cannot tell a position from a move. The draft `intent_v1` gave
41%, mostly because it did not read "giving him room" as moving aside (51 of 54 such intents came
with a turn). The rate is measured on the same intents the codebook was written from.

## 7. Three sample transcripts

Each is the session's `.md` under `sessions/`, with every prompt and raw reply.

1. **Talk, resolved:** `T_head_on_02dfbadb_54f8aa95_r1` (same age, p1 male). Agent 0 drifts right;
   agent 1 drifts left, then reads agent 0's drift as "walking across ... from my left to my right"
   and goes on left; agent 0 switches left at its second decision point, and at 5.5 s steps left
   25° then right 20°. They pass, each on its left, 0.22 m apart (plain ORCA: 0.01 m). Neither
   said a word. Debriefs: "habit", "ordinary pedestrian courtesy".
2. **Non-verbal, collision in `plan_only`:** `N_head_on_de176842_48eb8404_r2` (p1 older). Both
   decide at 2.4 s to step right and then back left ("turn right 20° for 1.5 s, then left 20° for
   1.5 s"; "right 10° for 1.5 s, then left 10° for 2.5 s"). At 4.2 s, while both are stepped
   aside, no conflict has been predicted for a second, so the encounter ends and neither is asked
   again; their plans carry on, they step back into each other's way and touch. Debriefs: "everyday courtesy ... giving an older person a bit of extra
   room".
3. **Independent, resolved:** `I_head_on_02dfbadb_b4042637_r1` (p1 older). Agent 0 slows to 1.2
   m/s and keeps right 10° for 3 s; agent 1 waits 2.8 s and then turns right 15°. They pass, each
   on its right, 0.17 m apart. Debriefs: "common sense", "giving an elderly person extra room".

## 8. What this means for RF-10

See `WORK_LOG-64.md`, "Recommendation for Phase A". In short: the cost is small (about USD 0.001
a session off-peak); the variability is not. Fix the remaining reply-format failures and the
"across" wording before screening, and size the screen against the noise floor, not the budget.
