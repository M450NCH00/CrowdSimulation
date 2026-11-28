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

### 2026-11-28 08:51 UTC — resolve_v11, the gap measure, tests, config, the start-walls analysis
- What I did:
  - `negsim/resolution/view.py`: a `Sideways` record (gap then and now, each one's move across, metres,
    + to the agent's left) and `SeenPerson.sideways`, None by default and left out of the record when
    None (as `from_a_m`).
  - `negsim/resolution/perceive.py`: `Body.path_rad` (optional, last field, so the grid's positional
    `Body(...)` is unchanged; None falls back on facing); `_Look.me` keeps the agent's own body at each
    look; `sideways_since()` works it out, only under a core template with `sideways_gap`.
  - `negsim/resolution/prompt.py`: `CoreTemplate.sideways_gap` and `_gap()`, on full and short lines.
  - `resolve_v11.yaml`, frozen in MANIFEST (sha256 `c6d2694f…`): `resolve_v9` word for word plus the
    flag and four view keys.
  - `configs/resolution/rf54_round1_head_on_sideways_gap.yaml`: RF-40's with silent only, the core
    template and a placeholder cap (USD 0.01) until the approval. `--plan`: 272 silent sessions.
  - `analysis/start_walls.py` (with tests): the start-and-recovery table, to replace the scratch scripts.
- Decisions of mine (to check):
  - **Across the path, not the direction of travel.** Mid-sidestep the travel direction is turned by
    up to 30°, and the metres along the corridor would read as sideways.
  - **Both sides named.** The first wording ("has grown from 0.2 m to 0.6 m, and their centre is now
    0.6 m to your left") hid a crossing: in the 20 cm geometry, both stepping to their own right takes
    each across the other's line. Now: "their centre was 0.2 m to your right of yours and is now 0.6 m
    to your left of yours, so the gap between your centres has grown." Changed before freezing.
  - **Printed only once one of the two has moved across** (to 0.1 m), so decision 1 is resolve_v9's.
- Found on the way: under resolve_v9, someone 5 to 10 m away gets one short line with no
  "they have moved over" (that is full detail only). At decision 2 the two are about 7.8 m apart, so
  RF-40's agents were not told that the other had moved at all; only their own move. resolve_v11's
  line is printed on short lines too, so it also adds the other's move there. That is part of what
  RF-54 tests, and the report must say so.
- **Correction:** the first entry's "6 of those 10" dances rounded decision times to whole seconds.
  `analysis/start_walls.py` counts two changes of wall less than D5's 1.0 s apart (turn-taking may ask
  the second person 0.1 s after the first): **7 of the pilot's 10** failed same-wall sessions, and
  2 of RF-40's 256 sessions in all. Issue #155's body corrected the same day.

  | | RF-40 (256) | Pilot (64) |
  | --- | --- | --- |
  | same wall: sessions, resolved, dances (failed) | 111, 44, 0 (0) | 18, 8, 10 (7) |
  | opposite walls | 136, 115, 2 (1) | 40, 37, 4 (3) |
  | one never sidesteps | 9, 4, 0 | 6, 1, 0 |
- Result: `tests/test_rf54_sideways_gap.py`, 15 passed, including a scripted sidestep followed by a
  plain step (same wall and opposite walls), whose numbers match the 0.4 m sidesteps and the 20 cm
  offset; decision 1 and every v9 record unchanged. `analysis/tests/test_start_walls.py`, 3 passed.
- Next step: the related suites and the mock rehearsal (running), then the cost estimate.

### 2026-11-28 09:16 UTC — mock rehearsal and the cost estimate
- What I did: `python run_experiment.py configs/resolution/rf54_round1_head_on_sideways_gap.yaml --out
  runs_mock/rf54` (08:50 to about 09:00 UTC). Related suites rerun (a first run was cut off by my own
  20-minute `timeout`; it showed one failure: `test_ethnicity`'s list of configs written after
  issue #92, which every new config breaks; RF-54's added).
- Result: 272 sessions completed, USD 0. 2,717 calls, 1,369 prompt tokens a call (RF-40's real silent
  calls: 1,367). In 1,782 prompts, the gap line is in 426 of the 1,160 later ones and in none of the
  opening ones; the "both moved over" line in none (the mock's policy never moves both the same way).
- **Cost estimate** (off-peak): RF-40's silent sessions cost USD 0.3751 for 2,265 real calls (USD
  0.000166 a call). The template adds a line or two to some later prompts (about 1%). At RF-40's call
  count, USD 0.38; at the mock's (which overstated RF-39's calls), USD 0.45. **About USD 0.38 to 0.46
  for 272 sessions; about USD 0.11 to 0.14 for repeat 1 and the pairs (80).** Peak hours cost more:
  run off-peak only.
- Next step: ask the user for the size and the cap; record them in CLAUDE.md before any paid call.
- Related suites (12 modules, 22 min): 365 passed, 21 skipped, 1 failed: `test_ethnicity`'s config
  list for RF-54, the run having started before the fix was added; rerun alone after it, it passes
  (12 passed, 22 skipped of that selection). The full suite is still to run before the PR.

### 2026-11-28 10:45 UTC — approval, cap and balance (commit `d73bdfec0`)
- The user answered "Yes go with your recommendation": all 272 sessions, cap **USD 0.60**. Recorded in
  `CLAUDE.md` (pending sign-offs, item 1, #155 only) and the config (`budget.cap_usd: 0.60`), with a
  test that the two agree (`test_rf54_sideways_gap.py`, 16 passed).
- Balance (`GET /user/balance`, the key not printed): **USD 5.61** at 10:44 UTC (0.61 plus the user's
  USD 5 top-up). Recorded in `CLAUDE.md`'s Budget.
- Saturday, so off-peak all day (`pricing.tier_at`).
- Next step: the pilot, `--client deepseek --confirm --limit 24`, started 10:46 UTC, then its replays.

### 2026-11-28 11:00 UTC — the pilot (24 sessions, paid, off-peak)
- 10:46:54 to 10:58:26 UTC. 211 calls, **USD 0.0369** (ledger: 211 lines), all off-peak, no error.
  Projected for 272: about USD 0.42, inside the cap of USD 0.60.
- Checks: the opening prompt of all 24 sessions is RF-40's word for word; the model fingerprint is
  RF-40's (`bc19ba97…`, 163 of 163 attempts); the gap line in 196 later prompts, "both moved over" in
  72 (the mock never moved both the same way, so this is its first real use). Read two collisions by
  hand: the numbers follow the trajectory (both stepping towards the +y wall in the 20 cm geometry is
  told as "both moved over to your left/right" and "now in line with yours … shrunk").
- Outcomes against RF-40's same 24 sessions (too few to read): resolved (plan only) 15 against 18
  (12 both, 6 lost, 3 gained); unreadable 2 against 3. Of the 20 design sessions, 12 started on the
  same wall (RF-40: 8 of these 20); decision 1's prompt is identical, so that is sampling at
  temperature 1.0. Same-wall starts resolved 5 of 12.
- Seen in both collisions read: told the gap shrank, both people stepped further towards the same
  wall. When both reach the wall and stop moving across, the gap line is not printed (neither moved),
  as designed.
- Decision [mine, within the approved plan]: nothing to fix; the remaining 248 started 11:00:07 UTC
  (resuming the same folder, `stop_at_cap`).

### 2026-11-28 11:45 UTC — the full suite (while the run goes on)
- `llm_negotiation/tests`: **2,525 passed, 22 skipped** (42 min); `analysis/tests`: **138 passed**.
  Both at commit `3a1753abf`.

### 2026-11-28 12:45 UTC — the run is complete (272 of 272), compared with RF-40
- The remaining 248: 11:00:07 to 12:40:03 UTC. No sleep events (Kernel-Power 506/507) in the last 3 h.
- **Spend:** USD 0.3512 in the ledger (2,134 lines with the pilot's 211, all off-peak, no error), cap
  USD 0.60, below the estimate (0.38 to 0.46). Balance (`GET /user/balance`): **USD 5.26** (5.61 before).
  Recorded in `CLAUDE.md`'s Budget.
- Analysis: `analysis.compare` (repeat 1) and `runs/rf54_round1_head_on_sideways_gap/analysis/rf54_tables.py`
  (all 256 design sessions, RF-40's own churn, `analysis.start_walls`, the reaction after both moved
  the same way). Written up in `runs/rf54_round1_head_on_sideways_gap/comparison_report.md`.
- Result: resolved 191/256 against 163/256 (McNemar p = 0.009; RF-40's repeats against each other,
  p 0.18 to 0.85); 20 cm apart 0.56 to 0.73 (p = 0.011), aligned 0.71 to 0.77 (p = 0.37). Repeat 1
  alone 47/64 against 42/64 (p = 0.50). Same-wall starts recovered 0.55 against 0.40 (Fisher p = 0.037).
  Both towards the same wall when level, 61 to 39. Dances: 2 of RF-54's same-wall starts, 0 of RF-40's.
- Decisions of mine (to check):
  - **Starts are not held equal.** Decision 1's prompt is identical, but its reply is sampled, so RF-54
    drew fewer same-wall starts (97 against 111, p = 0.24). I estimated the share of the gain from the
    starts by swapping the per-start rates: about 7 of 28 sessions. This is an estimate, not a test.
  - **The reaction measure** is from the `plan_only` replay's positions, the same in both runs: a
    decision after both moved 0.1 m or more towards the same wall since that person's last decision.
    Stepping back rose only from 0.12 to 0.17 (p = 0.16); the replies were not read one by one.
- The confound found at 08:51 stands: on short lines `resolve_v11` also says the other moved at all.
- Next step: commit, push, open the PR (closes #155).

## Open questions / risks
- The dance stayed rare (2 of 97 same-wall starts); the worry above did not happen at this size.
- Which half of `resolve_v11` helped: the other's move on short lines, or the gap numbers. A template
  with only the first would separate them (about USD 0.35), not decided.
- The gap is centre to centre; the agent must compare it with the two widths itself. Saying how much
  room they need would be a second change (left out on purpose).
- People do the pavement dance too (inference, to check against RF-14's studies).

## Summary (fill in at the end)
- **Built:** `resolve_v11` (frozen), the gap measure (`Sideways`, `Body.path_rad`, `sideways_since`,
  only under `sideways_gap: true`), its config and tests, `analysis/start_walls.py`. Earlier templates
  and configs record exactly as before (tested; full suite 2,525 passed, 22 skipped; analysis 138).
- **Run:** paid, USD 0.3512 of a USD 0.60 cap, 272 sessions, balance USD 5.26.
- **Found:** RF-53's swap was mostly a same-wall start. With the cue, RF-40's silent sessions resolved
  0.75 against 0.64 (p = 0.009), and same-wall starts recovered 0.55 against 0.40; the per-decision
  reaction moved less (0.12 to 0.17, not significant). The cue also adds the other's move on short lines,
  so the two causes are not separated.
