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

## Open questions / risks

## Summary (fill in at the end)
