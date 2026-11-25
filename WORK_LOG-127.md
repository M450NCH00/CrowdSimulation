# Work Log — Issue #127: [Experiment] RF-39: round 1 (head-on), the sidestep with a second chance: does re-prompting end the pavement dance? (non-verbal and talk with resolve_v8, every cell repeated)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/127
**Branch:** feat/127-rf39-sidestep-reprompt (cut from `origin/feat/110-rf32-group-head-on`, as the RF issues are)
**Started:** 2026-11-01 03:23 UTC (Sunday: off-peak all day)

## Understanding the issue
Round 1's main failure under `keep_line` is the pavement dance: both agents move aside, towards
the same wall (RF-29: 25 of 32 collisions). RF-29 gave the agents the sidestep in metres
(`resolve_v8`) but only in the independent condition (one decision point, no chance to try again).
RF-30 let agents be prompted again and signal or talk, but with `resolve_v6` (no sidestep). No run
has had both. In life a dance usually ends with a second move (one holds, the other steps again)
or a word ("I'll go left").

**The user's request (2026-11-01, in conversation):** draft this experiment's design and estimate
its cost on the mock. The user is topping up the DeepSeek balance: "money is not an issue, the main
objective is to get enough data to extract good rule". **No paid run is approved yet**: the config's
cap is 0 until the user records the approval and cap in `CLAUDE.md` (pending item 1).

## Plan
1. Config `configs/resolution/round1_head_on_sidestep_reprompt.yaml`: RF-30's with `resolve_v8`,
   all three conditions, every cell repeated; a test that repeat 1 is RF-30's and RF-29's sessions
   and people.
2. Before any paid call (the lesson of RF-29): trace a later decision replacing a sidestep part-way
   through the executor, and check that the second prompt reports the move aside.
3. Mock rehearsal; cost from measured costs per session.
4. Put the design choices to the user; record their answers; then pilot and run.

## Progress log

### 2026-11-01 03:23 UTC — Issue, branch
- Created issue #127 (RF-39) from the conversation; branch cut from `origin/feat/110-...`.

### 2026-11-01 03:30 UTC — Config
- RF-30's config with three changes: `templates.core: resolve_v8`; `conditions: [independent,
  non_verbal, talk]`; `design.repeats: 4` in place of `exact_repeats` (8 cells x 3). The people are
  drawn by unit (case and cell, and each pair), not by repeat, so repeat 1 keeps RF-30's ids and
  people (RF-29's for independent), and every repeat of a cell has the same people.
- `--plan`: 816 sessions, 272 per condition (32 cells x 2 geometries x 4 = 256, plus 16 in pairs).
  The plan's worst case (USD 51.59) is every call at its token cap with every retry, at peak: not
  an estimate.
- **Assumption [mine]:** 4 repeats. Why: round 1's noise floor (0.83 of identical-prompt pairs
  change behaviour; 23 of 24 repeated cells coin flips) means one run per cell says little about a
  cell; with 4, each factor level has 16 cells x 2 geometries x 4 = 128 sessions per condition.

### 2026-11-01 03:40 UTC — A gap in `keep_line` across a later decision (found before paying)
- Traced a sidestep to the right (0.4 m), replaced part-way (0.26 m aside) by a later decision:
  - a sidestep 0.8 m the other way, then walk: ends 0.54 m left of the start line and keeps it. Correct.
  - stop 1 s, then walk: keeps the 0.26 m line. Correct.
  - **a plan whose first step waits** (`start: after_seconds` or `at_distance_m`): while waiting,
    the agent steers back to its path (0.26 to 0.07 m in 1 s). The sidestep is given back.
  - **`[]` ("carry on as you are")**: the agent steers back to its path (0.26 to 0.05 m in 2.5 s),
    the opposite of what it said.
- Cause: `execute.py`'s keep-the-line branch needed the *current* plan to have begun a step; a new
  plan waiting or empty falls through to "steer to the path".
- How often it would have mattered: in RF-30's run, 5 of 655 later decisions (3 `[]`, 2 a waiting
  first step). Rare there, but RF-39 is about later decisions after a sidestep, and RF-29 lost a
  paid run to the same kind of gap.
- **Fix [my decision; the user may choose `keep_line` instead]:** a new execution,
  `keep_line_replan`: `keep_line`, and once the agent has carried out any step in the encounter it
  keeps its line whenever no step is running. `keep_line` is unchanged, so RF-29's and RF-30's runs
  re-execute exactly as recorded. With one decision point the two are identical (tested), so
  RF-39's independent condition is carried out as RF-29's re-execution was.
- **The other reading of `[]`** (not built): "carry on" could mean "go on with the rest of my
  plan" rather than "keep where I am now". `execute.py` says an empty plan "changes nothing", and
  a later decision "replaces what is left of its plan". I kept the replacement and only stopped the
  drift back; flagged for the user.
- Documented in `execute.py`, `docs/resolution.md` (`steps[].until`) and `docs/encounter-protocol.md`.

### 2026-11-01 03:45 UTC — Tests
- `tests/test_rf39_sidestep_reprompt.py`, 14 tests, all pass: the three later plans keep the line
  under `keep_line_replan` and steer back under `keep_line` (as before); a later sidestep the other
  way ends where it says and keeps that line; with one decision point the two executions give the
  same track (4 plans); a mock pavement dance under `resolve_v8` in non-verbal prompts both agents
  again, and the second prompt says "Since then you have moved 0.4 m over to your right/left."; the
  config (816 sessions; repeat 1 and pairs have RF-30's and RF-29's ids and people).

### 2026-11-01 — Cost from measured costs (`spend_ledger.jsonl`, off-peak)
- Per session: independent USD 0.00051 (RF-29, `resolve_v8`, 4.0 calls); non-verbal 0.00111 and
  talk 0.00120 (RF-30, `resolve_v6`, 7.5 calls).
- RF-39: 272 x (0.00051 + 0.00111 + 0.00120) = **about USD 0.77 off-peak**; peak hours double it.
  More decision points after sidesteps, and `resolve_v8`'s longer system message (mostly cached),
  could add 10 to 30%.

### 2026-11-01 — Mock rehearsal (`runs_mock/rf39/`, 816 of 816)
- Every session ran under `resolve_v8` and `keep_line_replan` (`config.json`). Calls a session:
  independent 4.11, non-verbal 8.57, talk 8.69 (RF-30's real run: 7.53; the mock re-prompts a
  little more often here, so it overstates).
- Cost at the measured cost a call (RF-29 independent USD 0.000128, RF-30 non-verbal 0.000147 and
  talk 0.000159, off-peak) times the mock's calls: 0.14 + 0.34 + 0.38 = **USD 0.86 off-peak**.
  With the estimate per session above (0.77), **USD 0.77 to 0.86 off-peak**; peak would double it.
- Recommended cap: **USD 1.20** (about 40% over the higher estimate), `stop_at_cap`, a pilot of
  about 24 sessions first.
- Tests after the change: `test_execute.py`, `test_reexecute.py`, `test_resolve_v8.py`,
  `test_ethnicity.py`, `test_repo_hygiene.py`, `test_rules_schema_v4.py` and the new file: two
  enumeration lists needed the new execution and config (`AS_PROMPTED_TURNS`; the ethnicity
  configs list), then all pass (48 passed, 11 skipped in the two files rerun).

### 2026-11-01 — The user's decisions
Asked in four questions; the answers, word for word where given:
- **Paid runs:** "Approve cap of USD 1.20, but do not do the run first as I have not top up the
  money". Recorded in `CLAUDE.md` (pending item 1, #127 only); `budget.cap_usd: 1.20`. **No paid
  call until the user says the balance has been topped up** (last checked USD 0.17, 2026-10-29).
- **Scale:** 3 conditions x 4 repeats (816 sessions), as built.
- **Executor:** `keep_line_replan`, as built.
- **`[]` mid-sidestep:** keep the line where the agent is now, as built.

Next, once the user says the balance is topped up: re-check the pricing page, check the balance,
a pilot (`--limit 24`), read its replays for sidesteps and later decisions, then the rest off-peak.

### 2026-11-01 — Six decision points (the user's decision)
- The user asked whether one re-prompt is enough, since in life a dance can take three tries. It
  is up to 2 re-prompts now (D5: 3 decision points an agent in non-verbal and talk). In RF-30, 293
  of 384 agents used all 3, and 71 of the 92 failed sessions ended with the agents out of decisions
  and ORCA taking over. But the commonest reason for a later prompt was the other's signal (112) or
  slight turn, not a dance.
- Recommended raising the limit to 6, and the cap to about USD 1.60 after a new mock; the user:
  "Yes please do that". `protocol.max_decision_points: 6`. The prompts give no number ("You may be
  asked again later"), so no wording changes. **The cap stays USD 1.20 until the user approves a
  new one** (recorded in `CLAUDE.md`), after the mock below.
- Caveat for the report: repeat 1 pairs with RF-30 only up to the third decision; the sessions that
  reach it (most failures) go on differently.

### 2026-11-01 — Why that side: the debrief asks it (`resolve_debrief_v2`)
- The user's point: the results do not say whether an agent took a side because it prefers it or
  because either side would have done. Round 1 (RF-10 and RF-30 first plans with a side, 595):
  - right 62% when the lines are 20 cm apart, 61% when aligned: a lean, the same in both layouts;
  - in RF-10's exact repeats, an agent took the same side all 3 times in 5 of 13 (38%), against 29%
    for a coin weighted 62/38 (few agents: weak evidence);
  - 82% of reasons name the side, but almost none say why that side: a custom 2 to 4%, the other's
    position about 4% (a keyword coding of the private reasons, mine; `[unverified]` beyond that).
- Two measures in RF-39:
  1. **From behaviour (the main one):** with every cell 4 times, whether a cell's side is stable
     (a preference) or a coin flip, the lean overall, by layout, and by factor.
  2. **Asked:** `resolve_debrief_v2`, v1 word for word plus "If you moved to one side, why that side
     and not the other? ... or nothing: either side would have done as well. That is a perfectly
     good answer too." and the reply keys `side_basis` (`custom_or_rule`, `where_they_were`,
     `more_room`, `what_they_did`, `either_side`, `did_not_move_aside`) and `side_detail`. Asked
     after the encounter, so it cannot steer a decision; the first prompts stay RF-30's. **The
     wording is my draft, for the user to review before the paid run** (a change means v3).
  - The two are compared: round 1 found that what agents say drives them often does not show in
    what they do (`docs/round1-results.md`, 4.4), so the stated reason is checked against the
    behaviour, not taken as the cause.
- Code: the parser reads the side keys only under the template's `side_question` flag (as
  `resolve_v8`'s `sidestep` flag); a missing or unknown side basis is flagged, not refused, so the
  rest of the debrief is kept; records and `debriefs.jsonl` gain the keys only when asked, so
  earlier runs are written as before; the mock adds the keys only when the question asks for them.
  7 more tests (21 in the file).

### 2026-11-01 — Mock rehearsal with 6 decision points and `resolve_debrief_v2` (`runs_mock/rf39_dp6/`)
- 816 of 816; `config.json` has `max_decision_points: 6` and `resolve_debrief_v2`. (`--overwrite`
  is refused for a resolution experiment, which resumes; hence a new folder.)
- Calls a session: independent 4.11 (unchanged), non-verbal 11.14 (was 8.57 with 3), talk 11.43
  (was 8.69); at most 15. All 1,554 debriefs read, with a side basis (the mock's two answers).
- Cost at the measured cost a call: 0.14 + 0.45 + 0.49 = **about USD 1.08 off-peak** (the side
  keys add about 30 output tokens a debrief, a few per cent). USD 1.20 would leave about 10%.
  Recommended cap: **USD 1.60**. **The user raised the cap to USD 1.60** (recorded in `CLAUDE.md`) and
  answered "Wording is fine" to `resolve_debrief_v2`'s question. The top-up condition still holds.

### 2026-11-01 06:53 UTC — Top-up, balance, prices
- The user: "I have topped up up to 5 us dollar in my deepseek api, so now help me work on GitHub
  issue #127". The top-up condition is met; recorded in `CLAUDE.md` (Budget and pending item 1).
- Balance (`GET /user/balance`, the key not printed): **USD 5.17** (5.17 topped up, 0.00 granted).
- Pricing page re-read 06:50 UTC: every price, both model versions and the peak hours as in
  `deepseek_pricing.yaml`; `date_checked` 2026-11-01 (`docs/pricing-check.md`; `test_llm.py` pins
  the date). Sunday, so off-peak all day.
- The run order is shuffled, so `--limit 24` takes a mix of the three conditions (in the mock's
  order the first 24 were 3 independent, 11 non-verbal, 10 talk).
- Next: the pilot, `--client deepseek --confirm --limit 24`, then read its replays.

### 2026-11-01 07:02 UTC — Pilot (24 sessions, USD 0.0370, off-peak)
- 2 independent, 13 non-verbal, 9 talk; no transport error, no session aborted.
- **Sidesteps:** 132 of 145 readable decisions use one; first plans pick left 25, right 22.
- **Later decisions:** 33 agents were asked a second time, 14 a fifth time, 4 a sixth (the new limit).
  Commonest reasons: the other's signal (64), `plan_failing` (57), the other slowing (46), moving
  aside (50).
- **Pavement dance survives the second chance in these sessions:** in the collisions read
  (`N_..e57e5fb0_r1`, `T_..1caa9a84_r1`, `N_..7eed7b59_r1`), one agent sidesteps to its right and
  the other to its left (the same wall), and each keeps its own side for 5 or 6 decisions, both
  ending against that wall, "straight ahead" of each other, until they collide. Talk did not break it
  either: "plenty of room on your right" / "I'll keep to my right" (both meaning the same wall). This
  is what the run is to measure, not a fault; the full run says how often.
- **Executor:** the line is kept across later decisions (agent 0 in `T_..1caa9a84_r1`: right wall
  0.87, 0.37, 0.25 m at decisions 2, 3, 5). The second prompt reports the own move ("Since then you
  have moved 0.5 m over to your right.").
- **What an agent is told about the other's move aside:** only within 5 m (the detail range, D-design
  of `resolution.md`), as in RF-30: "Since you last looked, they have moved over to your right"
  appears 14 times. A prompt triggered by `other_moved_*` farther away does not say it. Not changed
  (the perception design, and the comparison with RF-30), but worth a line in the report.
- **Unreadable:** 2 of 147 decisions after the one retry (`until: {"event": "other_passes"}`);
  4 retries in 197 calls (RF-30: 23 in 1,446).
- **Debriefs:** 48 of 48 read. `side_basis`: more room 20, where they were 18, either side 5, what
  they did 3, custom or rule 2. The details are concrete (wall distances, the other's position).
- **Resolved by the LLM:** non-verbal 9 of 13, talk 6 of 9, independent 0 of 2 (too few to read).
- **Cost:** per session independent USD 0.00071, non-verbal 0.00160, talk 0.00164; calls a session
  8.7 and 8.4 (the mock: 11.1 and 11.4), at USD 0.00019 a call (RF-30: 0.00015). Projected for 816:
  **about USD 1.07**, inside the USD 1.60 cap.
- Decision [mine, within the approved plan]: the pilot shows nothing to fix; run the remaining 792
  sessions now (Sunday, off-peak until Monday 01:00 UTC), `stop_at_cap`.

### 2026-11-01 07:13 UTC — `analysis.sidestep_reprompt` (while the run went on)
- The gate, `lateral` and `compare` count first runs only (`design_rows`), right for pairing with RF-29
  and RF-30 but blind to repeats 2 to 4. New module for RF-39's two questions: the first plans' kind
  (a dance or not) and how many of each resolved, per condition (Fisher's exact); how a dance ended
  (who changed side, a side said or pointed to); the first side across a cell's 4 repeats against a
  weighted coin (chi-square, df 1); the side against the room in the first prompt and the debrief's
  `side_basis`. Standard library only, 6 tests (Fisher checked against R's values); the analysis suite
  90 passed. Rehearsed on the mock run (20 s for 816 sessions).

### 2026-11-01 10:17 UTC — The run finished (816 of 816, USD 0.988492)
- Last call 10:17 UTC; 5,753 calls (4,151 decisions, 1,602 debriefs), all off-peak, no error, no
  upper-bound cost. Cap USD 1.60; the mock's estimate 1.08, the pilot's projection 1.07.
- Balance **USD 4.18** (5.17 before; the difference is the ledger's to the cent). Recorded in `CLAUDE.md`.
- Calls a session: independent 4.03, non-verbal 8.59, talk 8.54 (the mock: 4.11, 11.14, 11.43).
- Unreadable after the retry: independent 29 of 544 (RF-29: 2 of 192), non-verbal 57 of 1,705, talk
  26 of 1,738; debriefs 0 of 1,602.

### 2026-11-01 11:40 UTC — Analysis
- Ran `analysis.gate`, `analysis.lateral`, `analysis.compare` (RF-30 non-verbal and talk, RF-29
  independent, and readable-only), `analysis.sidestep_reprompt` and the factor report
  (`python -m analysis`). Written up in `runs/rf39_round1_head_on_sidestep_reprompt/comparison_report.md`.
- **Found: the model's fingerprint changed.** RF-29 and RF-30 (2026-10-25): `e72d3c7f…`; RF-32 (10-28)
  onward, this run included: `bc19ba97…` (checked in each run's session records). Same model name and
  listed version. Not recorded before. The comparisons with RF-29/30 change the model too; RF-39's
  own comparisons between conditions do not.
- **`compare.py`'s stability line is not comparable here** (it counts shared sessions, mostly one run a
  cell: "58 of 64"). Left as is; the report says so and uses the 4-repeat stability instead.
- Main results (the report has the tables): a second chance rescues 47 of 120 (non-verbal) and 41 of 124
  (talk) dances at the start, against 0 of 90 in independent; one agent changes side in 74 of the 88
  rescues, nobody in 118 of the 156 failures. The side: the same in all 4 repeats 0.30 / 0.29 against a
  coin's 0.13 / 0.15 (non-verbal, talk; independent within a coin); visitors from the US go right; no
  factor predicts resolution. "More room" (39% of answers) does not predict the side (0.53 in the
  layout where it is defined); visitors name a custom in 4 of 377. Gate on first runs 92 of 192 (0.48),
  fails narrowly; RF-30 passed at 0.53.
- Read examples (for the report's claims): in the 20 cm layout "more room" is read both ways ("kept me
  in the wider gap" / "kept me tight to the wall and left the wider space on his side"); in talk the
  speaker names its own side ("I'll keep to my left, plenty of room") and the other does not switch;
  one agent "plenty of room on your right" from that same side.
- Coding choices [mine]: a message "names a side" if it has the word `left` or `right`; "more room" is
  a wall at least 5 cm farther; "changed side" is a later readable decision with the other side.
- Run folder: 225 MB. As RF-35 and RF-36, the two interaction logs (13 MB, rebuilt from the session
  records) are gitignored; session records, transcripts, events and trajectories are committed.

### 2026-11-01 — Why the other did not act on "I'll keep left" (the user's question); a correction
- The user asked whether it was timing (both prompted at once), left/right confusion, or a choice.
- Traced each talk-dance message through the session records' `utterances`: 108 replies named a side;
  **96 were never said** (the encounter ended first: median reply 2.2 s before the end, at 3.5 m; 7.5
  words, 3 s to say; heard only once said in full). 12 heard, 8 with no later decision for the
  listener, 4 (2 sessions) with one: in all 4 the listener cited the words and took the wrong side
  (perspective). Speakers: 3 of 6 "your left/right" messages named the speaker's own side.
- **Correction:** the report said "the other ... does not switch", implying it heard; it mostly never
  heard. Fixed in `comparison_report.md` (In short, sections 2 and 7), marked as corrected.
- Design levers, for the user (not changed): a message heard only when said in full; the 2.5 words a
  second placeholder; agents talking late and in long, greeting-first sentences (a template change
  would be a new version).

### 2026-11-01 — Talk as built against the user's intent; RF-40 opened (#129)
- The user's intended talk design: the simulation pauses, A is asked, B hears A's full message and
  answers. As built (RF-3, #58): both asked on the same state, speech takes simulated time (D3:
  "speaking takes simulated time"; 2.5 words a second a placeholder). RF-30's and RF-39's talk results
  are therefore real-time speech while walking, not a conversation.
- The user: "Yes" to a new issue with the order counterbalanced. Opened **#129 (RF-40)**; open there:
  signals paused too or not, a perception line for the other's frame, which conditions to run.
- Measured for the user's other questions: talk replies carry a message in 0.49 of decisions (0.30 of
  first decisions), a signal in 0.69; non-verbal a signal in 0.54. Talk does not resolve better than
  non-verbal (0.59 and 0.59 over all repeats; RF-30 0.47 against 0.58, not significant).

## Open questions / risks
- ~~For the user: the scale, the execution, the meaning of `[]`, and the cap.~~ Decided 2026-11-01 (above).
- ~~Prices were last checked 2026-10-26~~: re-checked 2026-11-01, unchanged.
- ~~The mock never sidesteps~~: the pilot's replays were read (sidesteps in 132 of 145 decisions).
- Repeat 1 pairs with RF-30 by session, but RF-30 ran under `keep_line` and `resolve_v6`, with 3
  decision points, **and on another model fingerprint**: the comparison changes four things at once.
- For the user: whether the fingerprint change (from RF-32 on) should be noted in the earlier reports
  (RF-32 to RF-36) and in `docs/round1-results.md`, whose round 1 numbers come from both.
- For the user: the gate is at its threshold (0.48 here, 0.53 in RF-30). Whether head-on "passes"
  Step 1 is a judgement on a rate of about one half, not a clear pass or fail.
- The keyword coding (a side named, "more room" at 5 cm) is mine and unchecked by a second reader.

## Summary
**What changed:** RF-39's config (`resolve_v8` in all three conditions, every cell 4 times,
`keep_line_replan`, 6 decision points, `resolve_debrief_v2`), the executor fix `keep_line_replan`, the
debrief's side question, `analysis.sidestep_reprompt`, and the paid run (816 sessions, USD 0.988 of
the USD 1.60 cap) with its report.

**Why:** to see whether a second chance ends the pavement dance (round 1's main failure) and whether
the side an agent takes is a preference or a coin flip.

**Results:** a second chance rescues about a third of dances (0.39 non-verbal, 0.33 talk; 0 with one
decision), by one agent changing side; overall 0.59 against 0.36. The side is a weak, person-level
preference (US visitors right; assertive, hurried right; older left) that the agents' stated reasons do
not match. No factor predicts resolution. Gate 0.48 (fails narrowly). No paired difference from RF-30
or RF-29, on a changed model fingerprint.

**Verified:** 21 RF-39 tests and the 276 in the files the changes touch (before the run); `test_llm.py`
after the price date; the analysis suite (90 passed, the new module's 6 among them); with the run folder staged,
`test_repo_hygiene`, `test_resolution`, `test_avoidance_runs` and `test_rf39_sidestep_reprompt`: 180
passed (29 min). The report's numbers
were re-read against `analysis/*.md` and the scripts' output (three corrections: the debriefs' base
1,536, "most" of the gain, the residence counts' base). The full negsim suite (about 33 min) was not run.
