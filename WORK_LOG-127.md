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

## Open questions / risks
- ~~For the user: the scale, the execution, the meaning of `[]`, and the cap.~~ Decided 2026-11-01 (above).
- Prices were last checked 2026-10-26 (`configs/llm/deepseek_pricing.yaml`): re-check before paying.
- The mock never sidesteps, so the rehearsal checks bookkeeping and call counts, not behaviour; the
  pilot's replays must be read for sidesteps and later decisions before the rest is paid for.
- Repeat 1 pairs with RF-30 by session, but RF-30 ran under `keep_line` and `resolve_v6`: the
  comparison changes two things, the template and (for later decisions only) the execution.

## Summary (fill in at the end)
