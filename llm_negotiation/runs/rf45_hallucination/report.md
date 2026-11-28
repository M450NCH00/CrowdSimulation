# RF-45: hallucinated decisions in round 1 (RF-39 and RF-40)

Issue #134, track #55. The supervisor's point 6 of November 2026 (SV12): "Check whether the decisions it made are hallucinated choices (Assess the percentage on the hallucination responses)". No model call, USD 0. The process is in `WORK_LOG-134.md`.

## In short

- **About 1 decision in 11 is hallucinated:** 14 of 150 randomly sampled decision points (**9.3%, 95% CI 5.6 to 15.1**), RF-39 and RF-40 pooled. Each of the 150 was read in full against what its prompt showed, so this share does not depend on the keyword coder. By run: RF-39 6 of 66, RF-40 8 of 84. **Another 8.0%** (12 of 150) contradict themselves: the stated intent says one thing and the plan does another.
- **What the hallucinations are:**
  - **Inventing the other person's movement (category 1, 6.0% of the sample).** Nearly always a side or a drift the view does not show ("he's drifting into my path", "she's drifting to my right", when nothing lateral is shown), or the other's move converted the wrong way ("he's moved to his right, which is my left", when he moved to the agent's right).
  - **Misreading the side of a heard message** (RF-40's E3): "on your left" restated as "her left, which is my right".
  - **Unreadable replies (category 5, 3.3%):** a step that waits for `other_passes`, for example.
  - **Almost none** misremember their own moves (2: 0 of 150), invent a trait (an "older lady with a cane" who is 25 with no cane: 2 cases in 9,243), or misstate the corridor (7: 0 of 150).
- **The errors cluster in talk:** 9 of the 14 are in talk sessions (9 of 57 sampled talk decisions, against 5 of 93 in the other conditions). Talk is where sides are named and must be converted. This is descriptive only; the sample is small.
- **The keyword coder is not good enough to give the share on its own.** Its headline (4.7% in RF-39, 5.4% in RF-40) mixes rules that are almost always right with rules that are mostly wrong, and it misses most of category 1:

| Rule (precision from the hand check) | Precision | Use it in later runs? |
| --- | --- | --- |
| `5:unreadable` | 5 / 5 | yes |
| `4:coming_through_on_your_side` (RF-40's coding) | 29 / 29 | yes |
| `1:moved_into_line`, `1:moved_side` | 16 / 16, 25 / 27 | yes |
| `1:misread_heard_side` | 10 / 14 | yes, with care |
| `3:intent_against_plan` (RF-8's codebook, reused) | 24 / 77 | no: it flags "keep to my right" while already against the right wall, and reads "without stopping" as stop |
| `7:no_room`, `7:wall_close` | 2 / 21, 2 / 16 | no: most are fair judgements ("little room to maneuver" at the wall) or plans and negations ("not going to squeeze against the wall") |
| `1:speech`, `1:signal_wave`, `1:trait_elderly`, `1:position_side` | 1 / 26, 1 / 15, 2 / 15, 0 / 8 | no: "her greeting" for a nod; repeating its own earlier intent; the agent describing *itself* as "an old man with a cane"; plans ("pass Person 1 on my right") read as positions |

  Category 1's recall on the random sample was 2 of 9: it misses claims inside compound sentences ("coming toward me **and drifting to my right**"), "toward" (not "towards"), and restatements with extra words ("that's **actually** my left").

## 1. The definition (agreed with the user on 2026-11-25, before anything was counted)

A decision point is flagged when its reply:
1. **misperceived the other:** says the other signalled, spoke, stopped, slowed or moved aside, or has a trait, when the view does not show it; or puts them on the wrong side. Misreading the side of a heard message is tagged `misread_heard_side`.
2. **misremembered itself:** an earlier move, a position, a signal or a message that its history (or the wall distances) contradict.
3. **says one thing, plans another:** RF-8's intent-against-plan coding.
4. **says a side it does not take:** RF-40's coding of a message against the speaker's own move.
5. **not an available action:** unreadable after the retry.
6. **made-up source:** not recounted. RF-14 found no checkable reference: 0 of 27 extractor references, and no source named in 2,681 debriefs (`literature/rule-verification/references-check.md`).
7. **misstated the setting** (added by the user from RF-44): a claim about the corridor, the walls or the rules that the description contradicts.

**Headline** = 1, 2, 5 and 7. **Self-contradiction** = 3 and 4, reported beside it.

**The input** is that decision point's prompt: each call is fresh, and its history lines repeat the agent's own earlier intents. So "he waved me on", when only the agent's own earlier intent says so, is *not* counted (the assistant's coding choice; see section 4).

## 2. Data and method

- **Data:** every decision point of RF-39 (3,987; `runs/rf39_round1_head_on_sidestep_reprompt`) and RF-40 (5,256; `runs/rf40_round1_head_on_turn_taking`), all conditions, read from the committed session records.
- **The coder:** `analysis/hallucination.py` with the frozen keyword codebook `analysis/codebooks/hallucination_v2.json`. A claim is a pattern match on the reason, intent (and, for some rules, the message), checked against the view's structured fields: the other's signal, motion, changes, traits, age and bearing; what was heard; the agent's history; the wall distances.
  - `hallucination_v1` was the first version. v2 fixes one clear bug, found by reading 10 flags *before* the hand check: "a little room" (giving room) was read as "no room".
  - Nothing else was tuned on the data, so the precision below is honest rather than fitted.
- **The hand check** (`hand_check_judgements.json`, sheets `hand_check_sheet.md` and `hand_check_sheet_extra.md`):
  - a seeded random sample of **150** decision points (seed 134), each read in full: every flag judged, and every hallucination the coder missed recorded;
  - **every flag** of each rule with fewer than 30 flags (132 decision points);
  - a seeded extra sample of **55** flags of the three larger rules whose precision mattered (`7:no_room`, `7:wall_close`, `1:moved_side`; seed 1345).
  
  The judge is the assistant. **20 judgements are set out for the user to agree or correct** in `hand_check_for_user.md`.

  Re-run: `python -m analysis.hallucination llm_negotiation/runs/rf39_round1_head_on_sidestep_reprompt llm_negotiation/runs/rf40_round1_head_on_turn_taking --out llm_negotiation/runs/rf45_hallucination`.

## 3. The numbers

**From the random sample** (the share to quote; `hallucination.md`, "The hand check"):

| | Share of 150 |
| --- | --- |
| **Headline (1, 2, 5, 7)** | **14 (9.3%, 5.6 to 15.1)** |
| Self-contradiction (3, 4) | 12 (8.0%, 4.6 to 13.5) |
| 1. misperceived the other | 9 (6.0%, 3.2 to 11.0) |
| 2. misremembered itself | 0 (0 to 2.5%) |
| 3. says one thing, plans another | 12 (8.0%) |
| 4. says a side it does not take | 0 (0 to 2.5%) |
| 5. unreadable | 5 (3.3%) |
| 7. misstated the setting | 0 (0 to 2.5%) |

**From the coder, over every decision point** (`hallucination.md`; read with the precision above, not as true shares):

| | RF-39 | RF-40 |
| --- | --- | --- |
| Headline, coded | 189 / 3,987 (4.7%) | 282 / 5,256 (5.4%) |
| 1, coded | 37 / 3,875 (1.0%) | 106 / 5,135 (2.1%) |
| 3, coded | 763 / 3,359 (22.7%) | 1,234 / 4,577 (27.0%) |
| 4, coded (of messages stating the speaker's own side) | 13 / 59 | 18 / 73 |
| 5, unreadable (exact) | 112 / 3,987 (2.8%) | 121 / 5,256 (2.3%) |
| 7, coded | 38 / 3,875 (1.0%) | 50 / 5,135 (1.0%) |

Two of these counts are reliable:
- **Category 5** is exact.
- **Category 4** is about right (29 of 29 flags judged right). RF-40's 18 of 73 matches its own report: 16 of 27 "on your right" said the wrong way, plus 2 "I'll keep" messages.

From the rule precisions, the coder's high-precision category-1 rules hold about 74 real cases in the 9,243 decision points; with recall near a quarter, the true count is perhaps 300 or so `[inference]`. That agrees with the sample's 6% (3 to 11%).

**Sessions with a coded headline flag resolve less often** (an association, not a cause): RF-39 45 of 148 against 347 of 620 without (Fisher p < 0.001); RF-40 88 of 212 against 369 of 556 (p < 0.001). Part of this is mechanical: an unreadable reply leaves an agent with no new plan.

## 4. Coding choices (the assistant's, for the user to check)

- **A nod counts as a greeting.** "Return her greeting" after a nod is not category 1. "He said hello" after only a nod is.
- **Repeating its own earlier intent is not a hallucination.** "He already waved me on" is not flagged when the prompt's history shows the agent's own earlier intent saying so. The claim is in its input, even if no wave was ever shown.
- **Judgements of ease are not misstatements.** "Too narrow to pass *easily*", "little room to maneuver" while at the wall, and "too narrow for both of us to keep our exact lines" are not category 7. Categorical claims are: "too narrow to avoid them anyway" (0.7 + 0.5 m in 1.75 m), and "my left, where there's little room" with 1.50 m to the left wall.
- **Holding the line, then sidestepping, is category 3.** An intent of "hold my line" with a plan that sidesteps counts as a contradiction. "Keep walking and give room" with a sidestep does not, nor does "keep to my right" while already against the right wall.
- **Restating the other's *words* correctly is not category 1**, even when the other's movement differs ("she's keeping to her left, which is my right", after "I'm keeping to my left").

## 5. For later runs (RF-46, RF-49, RF-52) and RF-41

**Recommendations, not decisions:**
1. **Report a hand-checked share for every run:** a seeded random sample of 150 decision points read in full, as here. The coder alone under-counts category 1 and over-counts 3 and 7.
2. **Use the coder only as a screen,** with the reliable rules (5, 4, `1:moved_into_line`, `1:moved_side`, `1:misread_heard_side`, `2:own_signal`).
3. **A `hallucination_v3`** could:
   - drop or fix the low-precision rules (greeting, self-reference, plans read as positions, negated or planned "against the wall");
   - catch compound sentences and "toward";
   - replace RF-8's codebook for category 3 with one that knows the agent's position.
   
   Its precision and recall must be measured on a **fresh** sample, because these judgements were used to find the faults.
4. **RF-41:** use the reliable rules' flag as the hallucination column (as AS8 asks), not the whole headline.
5. **For RF-47, RF-48, RF-50/51:** the commonest hallucination is inventing or mis-siding the other's sideways movement, the same frame problem RF-43 found. An absolute frame and code-written side notes (RF-43, section 6) target exactly this.

## 6. Limits

- **One judge, the assistant.** The user is asked to check 20 judgements; a second human judge would give agreement figures.
- **150 decisions give wide intervals**, and per condition only a descriptive split.
- **Category 6 is RF-14's count, from earlier rounds;** RF-39's and RF-40's debriefs (`resolve_debrief_v2`) were not re-read.
- **The input definition matters.** Counting only what the view shows, and not the agent's own earlier claims, makes the share lower than a stricter reading would.
