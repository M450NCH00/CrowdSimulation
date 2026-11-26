# RF-52: round 1 (head-on) on the grid, in the agent's own frame and in an absolute frame

Issue #141, track #55. Run 2026-11-26 on `deepseek-flash`. The generated tables are in `grid.md`.

## Summary

- **LLM agents resolve head-on meetings on the grid in both frames.** RF-10's gate is 0.50.
  - Own frame: **237 of 272 sessions (0.87, 95% CI 0.83 to 0.91)**.
  - Absolute frame: **231 of 272 (0.85, 0.80 to 0.89)**.
- **That is more than RF-40's free steps in the continuous corridor.** On the same 272 silent sessions, RF-40 resolved 175 (0.64, 0.58 to 0.70).
  - Paired session by session, the grid resolves 88 sessions that RF-40 did not, and RF-40 resolves 26 that the grid's own frame did not (McNemar p < 0.001). The absolute frame gives 81 against 25.
  - **This compares two changes at once:** the world (cells, no ORCA) and the action space (a menu instead of free steps).
  - The grid is also an easy world: any fixed convention (both keep right, both keep left, one steps two lanes) resolves all 272 sessions. Random walkers resolve 125 (0.46).
  - **The continuous menu (RF-49) has not run** (not approved), so the grid cannot yet be compared with the menu alone.
- **The two frames resolve about equally often, but they fail in different ways** (paired p = 0.54).
  - **Absolute frame:** the left and right errors disappear when the two start one lane apart. 2 of 272 agents stepped towards the other, against 50 of 272 in the own frame, and 131 of 136 sessions resolved.
  - **But it does worse when the two start aligned:** 100 of 136 (0.74), against 118 of 136 (0.87) in the own frame. Both agents prefer "the yellow wall" (91 and 89 of 136 first moves, against 13 and 16 for blue). That wall is one person's right and the other's left, so the two move the same way. 63 aligned sessions danced, and all were same-wall pairs.
- **The left and right errors persist in the agent's own frame,** in the form the supervisor described (SV8).
  - When an agent says which way the other moved **in its own sides** ("she moved to my left"), it is right: 50 of 50 claims.
  - When it says so **in the other person's sides** ("she moved a lane to her left"), it is wrong: **43 of 43 claims**. It reuses the side it was given in its own frame.
  - RF-40's silent condition shows the same pattern, just more rarely: 3 of 4 such claims wrong. The grid's wording ("they have moved one lane to your right") seems to invite the restatement far more often.
  - The absolute frame has no such claims at all.
- **Hallucinated decisions, by RF-45's method** (a seeded sample of 150 decision points, 75 per frame, each read in full against its prompt):
  - own frame: **5 of 75 (0.07, 0.03 to 0.15)**;
  - absolute frame: **1 of 75 (0.01, 0.00 to 0.07)**;
  - RF-45 found 8 of 84 (0.10) for RF-40.
  - Separately, **14 of the 150** make a move that, by their own account of where the other is or went, closes the gap ("she is one lane to my right, so moving right opens the gap"). These are not misreadings of the prompt but reasoning about the geometry.
- **Cost:** USD 0.348 of the USD 0.80 cap, both frames together. The balance went from USD 2.96 to **USD 2.62**. All 2,996 calls returned RF-40's model fingerprint.

## 1. What ran

| | Own frame | Absolute frame |
| --- | --- | --- |
| Config | `configs/grid/rf52_round1_grid.yaml` | `configs/grid/rf52_round1_grid_abs.yaml` |
| Base (RF-51) | `round1_grid.yaml`, `resolve_grid_v1` | `round1_grid_abs.yaml`, `resolve_grid_abs_v1` |
| Sessions | 272 (RF-40's silent sessions, same ids) | 272 (the same) |
| Decision points | 944 | 946 |
| Calls (with retries and debriefs) | 1,506 | 1,490 |
| Cost (USD, ledger) | 0.1719 | 0.1757 |

- **The model:** `deepseek-flash`, temperature 1.0, 300 tokens, thinking off (RF-40's settings). Every call returned fingerprint `bc19ba97cbe016479903222bb1578db6`, RF-40's, so the model did not drift between the two runs. `deepseek-flash`'s fingerprint has changed without notice before, between 2026-10-25 and 2026-10-28.
- **Silent only (AS2).** Lanes of 0.4 m, 5 lanes, a tick of about 0.31 s, Burstedde et al.'s clash rule (RF-50). Up to 6 decision points per agent, event-driven, and a debrief (`resolve_debrief_v3`).
- **The cap:** one cap of USD 0.80 over both frames, enforced in code. `negsim/grid/paid.py`'s guard sums both experiments' ledger lines.
  - The pilot (8 sessions per frame) ran 10:01 to 10:06 UTC. Its fingerprint and replies were read before the rest.
  - The rest ran 10:09 to 12:02 UTC, off-peak.
- **The gate** is the user's decision of 2026-11-26: RF-10's 0.50 on the share of sessions the agents' own plans resolve. The grid's measures stand for `plan_only` (it has no avoidance steering), and the ORCA baselines are not available.
- **"Resolved"** is RF-50's definition, round 1's: passed, never blocked face to face, not squeezed past (closer than 0.5 m, so adjacent lanes count), no deadlock (3.0 s without progress), within 60 s.

## 2. The gate, and what to compare it with

| | Resolved | 95% CI | Gate |
| --- | --- | --- | --- |
| Own frame | 237 / 272 (0.87) | 0.83 to 0.91 | pass |
| Absolute frame | 231 / 272 (0.85) | 0.80 to 0.89 | pass |
| RF-40 silent, free steps, continuous corridor | 175 / 272 (0.64) | 0.58 to 0.70 | (passed in RF-40) |
| Scripted: any fixed convention (keep right, keep left, one steps two lanes) | 272 / 272 | 0.99 to 1.00 | |
| Scripted: one holds, the other steps one lane | 136 / 272 | | |
| Scripted: random moves, on each session's seed | 125 / 272 (0.46) | 0.40 to 0.52 | |
| Scripted: both step towards the same wall, or both hold | 0 / 272 | | |

Without the 16 counterfactual-pair sessions (as RF-40's report counts): own 223 of 256, absolute 216 of 256, RF-40 163 of 256.

- **Against RF-40, session by session** (the same people, factors and layouts):

  | Frame | Both | Grid only | RF-40 only | Neither | McNemar exact p |
  | --- | --- | --- | --- | --- | --- |
  | Own | 149 | 88 | 26 | 9 | < 0.001 |
  | Absolute | 150 | 81 | 25 | 16 | < 0.001 |

- **What this difference can and cannot say.** The grid changes several things at once:
  - the world: cells instead of continuous space, a 2.0 m corridor instead of 1.75 m, no ORCA;
  - what agents choose: a menu of nine described actions instead of free steps;
  - how they are told positions: lanes instead of metres and angles.

  RF-49 (the same menu in the continuous corridor) would separate the menu from the world. It is not approved, so that comparison is **not available**.
- **The grid is an easy world for this meeting.** Every agreed convention resolves every session. So the LLM agents' 0.85 to 0.87 is well above random moves (0.46) but below any convention the pair might share. What remains is coordination: who goes which way.

**By layout:**

| Layout | Own | Absolute |
| --- | --- | --- |
| Aligned (both in the centre lane) | 118 / 136 (0.87) | **100 / 136 (0.74)** |
| One lane apart, person 1 off centre | 61 / 64 (0.95) | 60 / 64 (0.94) |
| One lane apart, person 2 off centre | 58 / 72 (0.81) | **71 / 72 (0.99)** |

## 3. The two frames

**Overall they do not differ:** both resolved 201, own frame only 36, absolute frame only 30, neither 5 (McNemar p = 0.54). They differ by layout, for two separate reasons.

### 3.1 One lane apart: the absolute frame removes the wrong-way step

Each person sees the other one lane to their own right. A step to the right goes into the other's lane.

- **Own frame:** 50 of 272 agents' first move was to their right, towards the other. Read in full, these replies mostly place the other correctly ("one lane to my right") and then say the step "opens the gap" or "gives us more room" (section 4.3).
- **Absolute frame:** 2 of 272 agents' first move went towards the other's lane. With lane numbers, the agents work out which way is away: "She is in lane 4, so I shift towards the blue wall (lane 2)."

### 3.2 Aligned: the absolute frame loses the mirror that coordinates the own frame

In the own frame, "both step to their own right" is a pass, because the two are mirrored. In the absolute frame, "both step towards the yellow wall" is the same direction, so it is a dance.

| Aligned, first moves | Own frame | Absolute frame |
| --- | --- | --- |
| Person 1 (heads +x) | right 67, left 35, no step 34 | yellow (its right) 91, blue 13, no step 32 |
| Person 2 (heads -x) | right 79, left 28, no step 29 | yellow (its left) 89, blue 16, no step 31 |
| Pairs that went opposite ways (a pass) | 38 (both right 33, both left 5): all resolved | 13: all resolved |
| Pairs that went the same way (towards one wall) | 38: all danced, 32 resolved | **63 (62 both yellow)**: all danced, 42 resolved |
| One stepped, one did not | 57: 47 resolved | 57: 45 resolved |

- **In the own frame,** the agents lean to their own right, about 2 to 1. Because the two are mirrored, that lean coordinates them.
- **In the absolute frame,** both lean to the yellow wall, about 6 to 1, whichever of their own sides it is on. That makes them collide.
- The factor models show the same lean (section 6): agent 0, whose right is yellow, plans right with OR 29.
- **Why yellow is not known.** Yellow is the second wall named in the prompt and in the ACTIONS list, so it is not a first-listed bias. It is also the side of lanes 4 and 5. One template cannot tell the name from the number. The second template that swaps the names, open since RF-48 (`docs/action-space.md` section 11), would.

## 4. Do the left and right errors persist? (SV8)

### 4.1 Which side the other moved to

Both RF-40's view and the grid's give the other's move in the reader's own frame:
- RF-40: `moved_left` or `moved_right`;
- the grid: "they have moved one lane to your right".

The check below reads every claim about which side the other moved to, in a readable decision point whose view gives a move. It compares each claim with the view (`analysis.grid.move_side_comparison`).

| Run | Points with a move | Claims | Wrong | In the reader's own sides ("to my left") | In the other's sides ("to her left") |
| --- | --- | --- | --- | --- | --- |
| Grid, own frame | 289 | 93 | **43 (0.46)** | 50 claims, 0 wrong | **43 claims, 43 wrong** |
| Grid, absolute frame | 267 | 0 | 0 | none | none |
| RF-40 silent | 584 | 93 | 4 (0.04) | 89 claims, 1 wrong | 4 claims, 3 wrong |

- **This is the supervisor's point, measured.** DeepSeek takes the other's left and right to be its own:
  - "He moved a lane to his right" after he moved to the reader's right, which is his left;
  - "She has shifted a lane to her right, away from my line" after a move to her left.
- When it keeps to its own sides, it is right.
- Among claims, the grid's are wrong about ten times as often as RF-40's (0.46 against 0.04). That is mostly because its agents restate the other's move in the other's sides far more often (43 claims against 4).
- **Whether it changes the outcome is not shown.** Own-frame sessions with such a claim resolve less often (25 of 35, against 212 of 237). But a claim needs a move and a later decision point. Among sessions with more than two decision points the gap disappears (25 of 35 against 77 of 99, Fisher p = 0.49).
- **In the absolute frame the error cannot occur in this form:** agents say "moved towards the yellow wall", and the check of those claims against the view (`other_move_wall`) flagged none.

### 4.2 The grid's other side checks (all readable points)

| Frame | Points | Wrong side or lane count for the other | "In my lane" when not | Other's move on the wrong side | Wrong lane number (absolute) | Any |
| --- | --- | --- | --- | --- | --- | --- |
| Own | 936 | 1 | 2 | 43 | – | 46 (0.05) |
| Absolute | 946 | 1 | 1 | 0 | 2 | 4 (0.004) |

- **How far the checks can be trusted.** These are keyword checks, refined on the pilot's replies and then read against samples:
  - the move-side check was right in 12 of 12 flags read;
  - a check of the intent's side against the option was mostly wrong in its first form (it read the other's side as the agent's own). It now reads only an intent that opens with the agent's own move.

  The checks miss some errors: the hand check found one move-side error with wording the regex does not cover.
- **The absolute frame's agents still speak of left and right** in 66 of 946 points (0.07). One of the hand-checked points gets it wrong: "the blue wall" called "my left" when it was on the agent's right.

### 4.3 Moves against the reply's own geometry

The hand check (section 5) found a kind of error that is neither a misreading of the prompt nor one of RF-45's categories. The reply places the other correctly, then chooses a move that by its own account closes the gap, saying it gives room:
- "She's one lane to my right, so shifting slightly right opens the gap between us";
- "She already shifted towards the yellow wall to pass me, so I'll ease a little further that way".

It occurred in **9 of 75 own-frame points (0.12) and 5 of 75 absolute-frame points (0.07)**. In the own frame it is the step into the other's lane (section 3.1). In the absolute frame it is following the other towards the same wall (section 3.2).

## 5. Hallucinated decisions (RF-45's method)

RF-45's definition and categories (`analysis/codebooks/hallucination_v2.json`). The headline is categories 1 (misperceived the other), 2 (misremembered itself), 5 (not an available action) and 7 (misstated the setting).

- **The sample:** a seeded random sample of 50 per frame (seed 141), then a seeded extra 25 per frame (seed 1410) to reach RF-45's 150.
- **The judge:** each point was read in full against what its prompt gave, by the assistant. The judgements and notes are in `hand_judgements.json`, the sheets in `hand_check_sheet.md` and `hand_check_sheet_extra.md`.

| | Own frame | Absolute frame | RF-40 (RF-45) |
| --- | --- | --- | --- |
| **Headline (1, 2, 5, 7)** | **5 / 75 (0.07, 0.03 to 0.15)** | **1 / 75 (0.01, 0.00 to 0.07)** | 8 / 84 (0.10) |
| Self-contradiction (3, 4) | 0 / 75 | 1 / 75 | |
| A left/right mix-up | 2 / 75 | 1 / 75 | |
| A move against its own geometry (section 4.3) | 9 / 75 (0.12) | 5 / 75 (0.07) | not counted |

- **What the six hallucinations were:**
  - the other's move put on the wrong side (2);
  - "we're both in our own lane" or "directly ahead in my lane" when that is false (2);
  - "they moved into the lane I shifted to" when they had not (1);
  - "I've already moved to lane 5" from lane 4 (1).
- **RF-45's keyword coder,** with only the rules its hand check found reliable: own frame 20 of 944 (0.02), absolute 0 of 946.
- **Unreadable replies:** own frame 8 of 944 after the retry, all with the same cause: the action written as "step a little to **my** left" where the menu says "to **your** left". RF-47's parser takes options by their exact names, so these changed nothing, as the rules say. The absolute frame's options name walls and had none.
- **The difference between the frames** (5 against 1 of 75) is in the expected direction but not significant at this size (Fisher p = 0.21).

## 6. Factor effects

These are RF-40's factor columns for the same sessions, with the grid's outcomes in place of the continuous ones (`analysis.effects`, unchanged). The models are logistic, with standard errors clustered by session and a Holm correction over all 45 models. The terms significant after Holm:

| Outcome | In | Term | OR (95% CI) |
| --- | --- | --- | --- |
| Resolved | both frames | one lane apart (against aligned) | 2.9 (1.7 to 5.0) |
| Resolved | absolute | one lane apart | 10.2 (3.8 to 27.1) |
| First plan a step left / right | both frames | own assertiveness ("holds their ground") | 0.05 / 0.12: assertive agents step aside far less |
| First plan right | absolute | agent 0 (heads +x, yellow on its right) | 29 (12 to 71): the yellow-wall lean |
| First plan right | both frames | own frame (against absolute) | 3.2 (2.4 to 4.2) |

- **No person factor changes whether a session resolves** once the layout is in the model. That covers age, gender, a mobility aid, a load, the phone, ethnicity, attractiveness and familiarity.
- **Own assertiveness** (RF-40's strongest effect, OR 8.4 on passing first) shows here as holding one's lane.
- **RF-40's effects on slowing cannot be checked:** the other's mobility aid, age, load, familiarity and attractiveness. Only 39 of 1,088 agents first chose to slow down. With a menu on the grid, agents step aside instead.
- **The debriefs** give "common sense" for most decisions (373 of 544 agents in the own frame, 386 in the absolute frame), then habit (105, 81), then none (57, 75). A local custom is given 6 times. No agent gives a law or official guidance, or a published study, both of which the debrief offers.

## 7. Limits

- **Two changes at once against RF-40:** the world and the action space (section 2). RF-49 would separate them.
- **An easy meeting:** two people in a 5-lane corridor, silent. Any shared convention resolves it. What the grid tests is coordination and reading the geometry, and it is better at showing the side errors than at ranking frames by success.
- **One template per frame.** The yellow-wall lean may be the name, the lane numbers or the position. The swapped template would tell.
- **One judge for the hand check:** the assistant, as in RF-45. The 14 judgements with a note are the ones to check first (`hand_judgements.json`).
- **The keyword checks** have known misses (section 4.2). The share to quote comes from the hand check.
- **Silent only (AS2):** whether talk or signals fix the same-wall failure was not tested.

## 8. For the user: how a grid result would reach the continuous simulator (task 3)

The 10,000-agent goal runs in continuous space (ORCA plus rules). Translating grid results into rules is out of RF-52's scope. Here are three ways a grid result could feed the continuous simulator, for you to choose from:

1. **The grid as a test bench only.** The grid's results decide how the continuous prompt is written, and no grid rule is carried over. On this run, that would mean:
   - give positions with a shared reference (lanes or walls), which removes the wrong-way steps;
   - keep some own-frame or mirrored wording, so that "both keep to one side" is a pass and not a dance.
2. **Rules extracted from grid sessions and translated** (as RF-12 and RF-31 translate rules). One lane becomes a lateral offset of 0.4 m, and each menu option the amount RF-47's table gives (RF-51 derived the cells from those amounts, so the way back is the inverse of its rounding). Rules about lanes may not survive in a continuous corridor without lanes.
3. **The menu carried over, not the grid:** run RF-49 (the menu in the continuous corridor, own and absolute frames) to see whether the grid's gains come from the menu or from the cells. It needs its own approval and cap.

*The assistant's recommendation:* option 1 now, with option 3 as the test that tells whether the grid's gains come from the menu. RF-49 is already built (RF-47, RF-48). This is the user's decision (#141, task 3).

## 9. Files

| File | What |
| --- | --- |
| `runs/rf52_round1_grid/`, `runs/rf52_round1_grid_abs/` | The runs: `config.json`, `sessions/*.json` (every prompt, reply and grid plan), `trajectories/`, `outcomes.csv`, `summary.json` (counts, gate, cost, fingerprints, cap), `invocations.jsonl`, `scripted_walkers.csv` |
| `runs/rf52_grid_analysis/grid.md`, `grid.json` | The generated tables (`python -m analysis.grid`) |
| `sessions.csv`, `agents.csv`, `points.csv` | One row per session, agent and decision point, with flags |
| `effects_terms.csv`, `effects_models.csv` | The factor models |
| `hand_check_sheet.md`, `hand_check_sheet_extra.md`, `hand_check_extra_keys.json`, `hand_judgements.json` | The hand check |

To reproduce, from the repo root:
```
python -m negsim.grid.baseline runs/rf52_round1_grid runs/rf52_round1_grid_abs          # in llm_negotiation/
python -m analysis.grid llm_negotiation/runs/rf52_round1_grid llm_negotiation/runs/rf52_round1_grid_abs \
  --rf40 llm_negotiation/runs/rf40_round1_head_on_turn_taking \
  --hand llm_negotiation/runs/rf52_grid_analysis/hand_judgements.json --n-hand 50 \
  --out llm_negotiation/runs/rf52_grid_analysis
```
