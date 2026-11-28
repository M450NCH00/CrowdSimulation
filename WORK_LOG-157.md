# Work Log — Issue #157: RF-55, which half of resolve_v11 helped? Only "they have moved over" on short lines: resolve_v12 on RF-40's silent sessions

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/157
**Branch:** feat/157-rf55-short-moved (cut from `origin/main` at b789c7129, PR #156's merge)
**Started:** 2026-11-28 12:55 UTC

## Understanding the issue
RF-54 (#155) raised the resolved share of RF-40's 256 silent design sessions from 163 to 191
(McNemar p = 0.009). Its template, `resolve_v11`, changed two things at once: on short lines (5 to
10 m) it says that the other moved at all, which `resolve_v9` left out, and at every distance it adds
the gap numbers and "both moved over". RF-55 adds only the first, in `resolve_v9`'s own words, to tell
the two apart.

Decided by the user on 2026-11-28: run the separation test next (after merging PR #156), before RF-46.
The approval and cap are asked for after the mock rehearsal.

## Plan
1. Template `resolve_v12`: `resolve_v9` word for word, plus a short-line key that prints `resolve_v9`'s
   "Since you last looked, they have moved over to your {side}." (only the move over). Freeze it.
2. `prompt.py`: print it on short lines only when the template has the key; earlier templates are
   unchanged (tested).
3. Tests: earlier templates unchanged; decision 1 unchanged; a sidestep then walking on, seen from
   5 to 10 m, prints the line; slowed down and turned are not printed on short lines.
4. Config `configs/resolution/rf55_round1_head_on_short_moved.yaml` (RF-40's silent sessions, only the
   template changed), with a test.
5. Mock rehearsal, cost estimate, then ask the user for the cap.

## Progress log

### 2026-11-28 13:00 UTC — resolve_v12, the short-line move, config and tests
- What I did:
  - `resolve_v12.yaml`, frozen in MANIFEST (sha256 `32ecec62…`): `resolve_v9` word for word except the
    header, the provenance and one view key, `seen_short_moved` ("  Since you last looked, they have
    {changes}.", the same words as `seen_changes`).
  - `negsim/resolution/prompt.py`: under a template with that key, a short line prints the person's
    `moved_left` or `moved_right` change, which the perceiver already worked out for every person
    (`changes_since`) and `resolve_v9` printed on full lines only. No change to `perceive.py` or the
    view record.
  - `configs/resolution/rf55_round1_head_on_short_moved.yaml`: RF-54's config with the name, the
    template and a placeholder cap (USD 0.01). `--plan`: 272 silent sessions.
  - `tests/test_rf55_short_moved.py` (10 tests); `test_ethnicity.py`'s list of configs after #92.
- Decisions of mine (to check):
  - **Only the move over**, not `resolve_v9`'s other changes (slowed down, turned) on short lines:
    the move is the part `resolve_v11` added there.
  - **`resolve_v9`'s own threshold** (where they are lies 2° or more off the line they were walking
    along), not RF-54's 0.1 m. At 7 m with 1 s between looks, 2° is about 4 cm across, so it fires on
    smaller moves than `resolve_v11`'s line did.
- Result: 10 passed; RF-54's 16 still pass. Among them: with the same replies, `resolve_v9` and
  `resolve_v12` give the same encounter, the same view records and system messages, and prompts that
  differ only by the added lines, on short lines only; a full line is `resolve_v9`'s.
- Next step: the mock rehearsal (running), then the cost estimate and the user's cap.

### 2026-11-28 13:23 UTC — mock rehearsal and the cost estimate
- What I did: `python run_experiment.py configs/resolution/rf55_round1_head_on_short_moved.yaml --out
  runs_mock/rf55` (13:00 to 13:22 UTC).
- Result: 272 sessions completed, USD 0. 2,717 calls (RF-54's mock: 2,717), 1,360 prompt tokens a call
  (RF-54's mock: 1,369). The short-line move is in 99 of 1,238 later prompts, in no opening prompt. (The
  mock's policy rarely sidesteps before 5 m; the real model sidesteps at decision 1 in most sessions.)
- **Cost estimate** (off-peak): RF-54's real run cost USD 0.3512 for 2,134 calls (USD 0.000165 a call),
  with slightly longer prompts than these. At RF-54's call count, about USD 0.35; at the mock's (which
  overstated RF-54's calls by 27%), about USD 0.45. **About USD 0.33 to 0.45 for 272 sessions.** Run
  off-peak only (Saturday and Sunday are off-peak all day in `pricing.tier_at`).
- Next step: ask the user for the approval and cap; record them in `CLAUDE.md` before any paid call.

### 2026-11-28 13:33 UTC — approval, cap, balance and the pilot (24 sessions, paid, off-peak)
- The user chose "Approve, cap USD 0.60 (Recommended)": all 272 sessions. Recorded in `CLAUDE.md`
  (pending sign-offs, item 1, #157 only) and the config, with a test that the two agree (commits
  `6041d5404`, `2f945cecc`: the first committed a test file that did not compile, a string my heredoc
  broke across two lines; fixed in the second, and 27 RF-54 and RF-55 tests pass).
- Balance (`GET /user/balance`, the key not printed): **USD 5.26** at 13:22 UTC.
- Pilot: `--client deepseek --confirm --limit 24`, 13:24:22 to about 13:31 UTC. 174 calls, **USD 0.0281**,
  all off-peak, no API error. Projected for 272: about USD 0.32.
- Checks: the opening prompt of all 24 sessions is RF-40's word for word; fingerprint `bc19ba97…` on
  all 126 attempts; the move is in 37 of the 54 later short-line prompts; no gap line anywhere. One
  session read by hand (`S_head_on_02dfbadb_1868bff4_r3`): the side is named right (person 0's step to
  −y is person 1's left), and a person whose own sidestep waits for 3 m is told it has not moved yet.
- Outcomes against RF-40's same 24 (too few to read): resolved 22 against 19.
- Decision [mine, within the approved plan]: nothing to fix; the remaining 248 started 13:33:11 UTC.

## Open questions / risks
- `resolve_v12` tells *that* the other moved but not *where they now are* against the agent. If RF-55
  matches RF-54, the gap numbers added nothing; if it matches RF-40, the gain was the numbers (or
  "both moved over"); in between, both helped. A tie at this size (256) cannot be read finely:
  RF-54's gain was 28 sessions.

## Summary (fill in at the end)
