# Work Log — Issue #155: RF-54, the sideways gap after a sidestep: do pairs recover from a same-wall start? resolve_v11 on RF-40's silent sessions

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/155
**Branch:** feat/155-rf54-sideways-gap (cut from `origin/main` at 3c2ef541e, PR #154's merge)
**Started:** 2026-11-28 08:28 UTC

## Understanding the issue
The previous session's handoff proposed a template, after `resolve_v9`, telling each agent whether
the other's sideways drift was moving away from its path or into it, to target "the swap" of RF-53's
pilot (13 of its 18 failures). Before building it, the 13 sessions were re-read wall by wall (see the
first progress entry). 10 of the 13 began with both people stepping towards the same wall at
decision 1. So the cue cannot fix the first decision; it can only help a pair recover after it. The
user chose, on 2026-11-28, to target that recovery ("Recovery cue (Recommended)"): tell each person,
computed by code, whether the sideways gap between their centre and the other's has grown, shrunk or
stayed the same since they last looked, and when both moved over to the same side.

Decided by the user on 2026-11-28:
- the template is `resolve_v11`; `resolve_v10` stays RF-46's (#135) ("Yes push it to v11");
- the target is recovery from a same-wall start (above);
- the user will top up the DeepSeek balance by USD 5 and asks for the paid steps one by one. The
  approval and cap are asked for after the mock rehearsal.

## Plan
1. Template `resolve_v11`: `resolve_v9` word for word plus the gap lines and a flag
   (`sideways_gap: true`). Freeze it in MANIFEST.
2. The perceiver works out the gap only under a template with the flag, measured across the
   observer's path direction (a new optional `Body.path_rad`). New `SeenPerson` fields default to
   None and are left out of the record, so earlier templates record exactly as before.
3. Tests: old templates unchanged; decision 1 unchanged; a sidestep followed by a plain step gives
   numbers that match the trajectory; same-wall and opposite-wall cases word correctly.
4. Config `configs/resolution/rf54_round1_head_on_sideways_gap.yaml` (RF-40's silent sessions, only the
   template changed), with a test.
5. Mock rehearsal, cost estimate, then ask the user for size and cap.

## Progress log

### 2026-11-28 08:27 UTC — the swap re-read: most of it is a same-wall start
- What I did: scratch scripts over RF-53's pilot and RF-40's silent design sessions
  (`decisions.jsonl`, `outcomes.csv`, the `plan_only` replays): the wall each person's first
  sidestep went towards (agent 0 faces +x, agent 1 faces −x, checked in the trajectory), whether
  both changed wall at the same decision time, and the outcome.
- Result:

  | | RF-40, thinking off (256) | Pilot, thinking on (64) |
  | --- | --- | --- |
  | Same wall at decision 1 | 111 (0.43), 44 resolved | 18 (0.28), 8 resolved |
  | Opposite walls at decision 1 | 136 (0.53), 115 resolved | 40 (0.63), 37 resolved |
  | One never sidesteps | 9 | 6 |

  10 of the pilot's 13 "swap" failures began on the same wall; 6 of those 10 had both changing wall at
  the same pause (neither sees the other's new choice in silent). The pilot report's description
  ("both step correctly, to opposite sides") fits 3 of 13. Its example, `S_head_on_de176842_8ea28db3_r1`,
  is a same-wall start: person 0 stepped to their right (−y), person 1 to their left (−y).
- The pilot report's "both towards the same wall" (3 of 64) is measured when the two come level,
  after the corrections, so it does not contradict this.
- Next step: ask the user which target `resolve_v11` should have (asked; "Recovery cue").

## Open questions / risks
- Both may correct at the same pause (the dance), as 6 of the pilot's 10 same-wall failures did. The
  cue may raise recoveries and the dance together.
- The gap is centre to centre; the agent must compare it with the two widths itself. Saying how much
  room they need would be a second change (left out on purpose).
- People do the pavement dance too (inference, to check against RF-14's studies).

## Summary (fill in at the end)
