# Work Log — Issue #134: RF-45: hallucinated decisions: the share of replies that rest on something not in the agent's input, or choose something not possible, on RF-39 and RF-40, with a hand check of the coder

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/134
**Branch:** feat/134-rf45-hallucinated-decisions (cut from `origin/feat/129-rf40-turn-taking-talk`, which carries RF-43's merged PR #143; RF-44's PR #145 is open and not needed here)
**Started:** 2026-11-25 07:54 UTC

## Understanding the issue
The supervisor's point 6 (SV12): "Check whether the decisions it made are hallucinated choices (Assess the percentage on the hallucination responses)". The issue drafts six categories that code can check against the session record:
1. misperceived the other;
2. misremembered itself;
3. says one thing, plans another;
4. says a side it does not take;
5. not an available action;
6. made-up source.

**The definition must be agreed with the user before anything is counted** (issue task 1, acceptance criterion 1). Then:
- write a frozen codebook `analysis/codebooks/hallucination_v1` and `analysis/hallucination.py` (standard library), with one true and one false hand-made case per category;
- run it on RF-39 (3,987 decision points) and RF-40 (5,256);
- hand-check a seeded sample of 150 decisions plus every flag in a small category, and show the user 20 of the judgements;
- write `llm_negotiation/runs/rf45_hallucination/report.md`.

No model call, USD 0.

## Plan
1. Read the session record's fields and real replies, to ground the definition (done before the question, without counting anything).
2. Ask the user to agree the definition.
3. Codebook, module and tests.
4. Run on RF-39 and RF-40; hand check; report; push; PR into `feat/129-rf40-turn-taking-talk`.

## Progress log

### 2026-11-25 07:54 UTC — Branch, and what the records hold
- What I did: cut the branch; read the RF-40 session record's structure and a few decision points with their full prompts. **Nothing was counted** beyond the record's own parse errors (needed to see how category 5 is stored).
- Found, per decision point:
  - `view.seen[i]`: the other's `signal` (none, nod, eye_contact, hold_up_hand, wave_on), `motion` (walking or still), `changes` since last look in the agent's own frame (moved_left or moved_right, "moved over to your left"; slowed_down, sped_up, turned), `factor_lines` (cane, suitcase, phone and so on), `bearing_rad`, `heading_relative_rad`;
  - `view.heard` (message, frame), and `view.history` (own earlier intent, signal, message, `sideways_m` with positive meaning left, `back_m`);
  - `parsed` (intent, reason, message, signal, steps), `coded` (side, slowed, stopped, backed_up), `parse_error` (unreadable after the retry; for example `start: 'other_passes'`, 52 times in RF-40) and `flags`.
- An example for category 1, from `T_head_on_02dfbadb_9950986f_r1` decision 3. The reason says "he's drifting into my line", but the view says only "walking in the opposite direction to you", with no change listed. The other had moved 0.5 m to *his* left, away from her line.
- Next step: ask the user to agree the definition.

### 2026-11-25 08:00 UTC — The definition, agreed with the user
The user answered three questions (all the recommended options), before anything was counted:
1. **The headline "hallucination share"** counts categories **1** (misperceived the other), **2** (misremembered itself), **5** (not an available action, meaning unreadable after the retry) and **7** (below): a reply that rests on something not in its input, or chooses something not possible. **3** (says one thing, plans another) and **4** (says a side it does not take) are reported beside it as **self-contradiction**. **6** (made-up source) is quoted from RF-14, not recounted. Every category is also reported on its own.
2. **A new category 7, "misstated the setting"** (from RF-44, PR #145): a claim about the corridor, the walls, the rules or what a step can do that the description contradicts, for example "there is no room to pass" when the widths given leave room.
3. **Misreading the side of a heard message** (RF-40's E3) counts in category 1, tagged `misread_heard_side`, so it can be shown on its own.

### 2026-11-25 08:08 UTC — Coder built; first run; one fix (v2)
- Built `analysis/codebooks/hallucination_v1.json` (43 patterns, generated from a script so the JSON escaping is not done by hand), `analysis/hallucination.py` and 17 tests (one true and one false case per category, hedges, heard-side frames, an end-to-end tiny run). All passed. Committed.
- **First run** (v1): RF-39 3,987 and RF-40 5,256 decision points, matching the issue's counts. Headline 7.0% and 7.4%.
- **A clear coding bug, found by reading 10 category-7 flags:** v1's `no_room` took "a little room" (as in "make a little room for her", *giving* room) for a claim of no room. Most of category 7's 3.3% came from it. Fixed in **`hallucination_v2`**, which is v1 plus that one fix. v1 is kept unchanged, because its rule is never to edit a frozen version. Added a regression test (18 pass).
- I also read 4 flags of each other rule. I did **not** tune anything else on the data. Plans worded like claims (an intent "… Person 1 on my right" meaning *where to pass*; "against the wall" as a plan) are left for the hand check to measure, so that the precision reported is honest rather than fitted.
- One flag shows a genuine frame error: "She has already moved to her left", when the view says she "moved over to your left", which is her right.
- **v2 run:** headline 189 of 3,987 (4.7%) in RF-39, 282 of 5,256 (5.4%) in RF-40. The hand-check sheet has 282 entries: 150 seeded random decision points (seed 134) plus 132 flags of rules with fewer than 30 flags.

### 2026-11-25 08:33 UTC — Hand check, scoring, report
- **Hand check:** read and judged 282 entries: the random sample of 150 (every flag judged, and every miss recorded), plus every flag of the rules with fewer than 30 flags (132). One entry was skipped while reading and then judged; a script confirmed that every flag of every judged entry has a verdict.
- **First scores:** category 1's precision was 35% and its recall 2 of 9; category 3's precision 29% (RF-8's reused codebook); category 7 had only 2 judged flags.
- **Added:** a seeded extra precision sample of 55 flags (`7:no_room` 20, `7:wall_close` 15, `1:moved_side` 20; seed 1345), so that category 7 and the largest category-1 rule rest on more than a handful. The flags are judged for precision only, not recall.
- **Extended the scoring:**
  - precision by rule, with estimated right flags;
  - **the true share from the random sample** (flags judged right plus misses), which does not depend on the coder.
  
  18 tests still pass.
- **Results:**
  - **True headline 14 of 150 (9.3%, CI 5.6 to 15.1)**; self-contradiction 12 of 150 (8.0%); category 1 9 of 150 (6.0%); 5 of 150 unreadable (3.3%); categories 2, 4 and 7 0 of 150.
  - 9 of the 14 are in talk sessions.
  - Reliable rules: 5, 4, `1:moved_into_line` (16/16), `1:moved_side` (25/27), `1:misread_heard_side` (10/14).
  - Unreliable rules: 3 (24/77), 7 (4/37), `1:speech` (1/26), `1:signal_wave` (1/15), `1:trait_elderly` (2/15), `1:position_side` (0/8).
- Wrote `llm_negotiation/runs/rf45_hallucination/report.md` and `hand_check_for_user.md` (20 judgements for the user, task 4).
- Verification: `analysis/tests` 115 passed (2 min 56 s); `test_repo_hygiene.py` running.

What "input" means (the assistant's coding choice, recorded here): **the prompt of that decision point only.** Each call is fresh; the model sees no earlier prompt, only the history lines this one repeats. A claim is supported if the current view's structured fields (or the history it repeats) show it.

## Open questions / risks
1. **One judge (the assistant).** The 20 judgements in `hand_check_for_user.md` are for the user to agree or correct; a second human judge would give an agreement figure.
2. **The coding choices change the share** (report section 4):
   - a nod counts as a greeting;
   - the agent repeating its own earlier intent is not counted;
   - judgements of ease are not misstatements;
   - "hold my line" followed by a sidestep is a contradiction.
3. **The coder is not fit to give the share on its own:** category 1's recall is 2 of 9, and categories 3 and 7 are mostly false positives. A `hallucination_v3` needs a *fresh* hand check, because these judgements were used to find the faults.
4. **150 decisions give wide intervals.** Per condition, only a descriptive split.
5. **Category 6 is RF-14's count** (earlier rounds). RF-39's and RF-40's debriefs were not re-read.
6. **The "missed" field was recorded for the random sample only.** For the small-rule and extra entries I noted misses in free text but did not count them; recall is from the random sample.
7. **Category 7's side check** can take a side named later in the sentence, for a plan, as the side where room is lacking. Seen once in the hand check; it lowers recall, not precision.

## Summary (fill in at the end)
**What changed**
- `analysis/hallucination.py` (new), with the codebooks `analysis/codebooks/hallucination_v1.json` (frozen, superseded) and `hallucination_v2.json` (one fix), and 18 tests in `analysis/tests/test_hallucination.py`.
- `llm_negotiation/runs/rf45_hallucination/`:
  - `report.md`;
  - `hallucination.md` and `.json` (tables), `flags.csv`;
  - the hand-check sheets, `hand_check_judgements.json` (337 judged), `hand_check_extra_keys.json`;
  - `hand_check_for_user.md`.

**Findings:** about 1 decision in 11 is hallucinated (9.3%, CI 5.6 to 15.1).
- Mostly the agent invents or mis-sides the other's sideways movement, or misreads the side of a heard message; that is the same frame problem as RF-43.
- 3.3% are unreadable replies.
- A further 8% say one thing and plan another.

The keyword coder is a screen, not a measure: later runs should report a hand-checked random sample.

**How it was verified:**
- the definition was agreed before counting;
- hand check of 337 decision points, with precision per rule and recall on the random sample;
- `analysis/tests` 115 passed;
- earlier analyses unchanged (no existing module was edited).
