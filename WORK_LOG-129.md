# Work Log — Issue #129: [Experiment] RF-40: round 1 (head-on), talk as a turn-taking exchange: the simulation pauses, A speaks, B hears all of it and answers (order counterbalanced)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/129
**Branch:** feat/129-rf40-turn-taking-talk (cut from `feat/127-rf39-sidestep-reprompt`: PR #128 is not merged yet)
**Started:** 2026-11-01 13:13 UTC

## Understanding the issue
In RF-30 and RF-39, talk ran as speech in real time while walking: both agents are asked on the same
state; a message takes simulated time to say (2.5 words a second, a placeholder) and is heard only
once said in full, within hearing range; the listener answers at its next decision. In RF-39's talk
dances, 96 of 108 replies naming a side were never said before the encounter ended. The user had
meant a conversation: the simulation pauses, A is asked, B hears all of A's message and answers.

**The user's decisions (2026-11-01, in conversation and recorded on #129):**
- turn-taking exchange; who is asked first counterbalanced over a cell's repeats, analysed as a factor;
- the pause applies to signals too;
- a silent condition (no signal, no talk, asked again) replaces independent ("I always thought that
  independent works in the way silent works");
- heard messages word for word, with a fixed note beside each on which way the speaker faces
  ("their left is your right"); no probe beforehand;
- RF-40's size: silent, non-verbal and talk, 272 sessions each (816), no other new factor.

## Plan
1. `silent` condition (templates offer it from `resolve_v9`; the three earlier conditions stay
   required, so v1 to v8 load as before).
2. `protocol.exchange: turn_taking` beside the default `real_time`, left out of records when default.
3. `resolve_v9`: v8 for the paused exchange, the silent section, the note beside a heard message.
4. Experiment layer: who is asked first; template/exchange agreement; `first_asked` column.
5. Tests: the default path unchanged; the pause; the note; silent; the config.
6. Analysis: silent, `asked_first`.
7. Mock rehearsal, cost estimate; then the user's approval and cap before any paid call.

## Progress log

### 2026-11-01 13:13 UTC — Branch
- Cut from `feat/127-rf39-sidestep-reprompt` (stacked: PR #128 is open).

### 2026-11-01 13:34 UTC — The build
- **Conditions** (`view.py`): `CONDITIONS` stays the three every template has; `ALL_CONDITIONS` adds
  `silent` and is what a session, a design and a config are checked against. `SIGNALLING_CONDITIONS`:
  the reply parser ignores and flags a signal outside non-verbal and talk (silent like independent).
  Session ids: `S_`. A template without a silent section refuses it by name.
- **The exchange** (`protocol.py`): `ProtocolSettings.exchange` (`real_time` default, not recorded).
  The default decision point now goes through `_ask` and `_apply`, in the same order as before (ask
  everyone, then carry out every reply); the 232 tests of the protocol, perception, `resolve_v8`,
  RF-39, re-execution and prompt files pass unchanged after the refactor. `_paused_exchange`: those
  due in turn (`first_asked` first, then the encounter's order); each reply carried out at once and
  its signal or message made at once, at the turn's look time; whoever perceives it, prompted before
  and with decision points left, is asked next in the pause whatever its last prompt
  (`signalled:n`, `heard:n`); each member at most once a pause.
- **Why a time offset per turn** (`_TURN_S`, 1 µs; `view_in(look_time_s=...)`): a look shows what
  came after the agent's last look and before the look, and an agent's looks must be strictly later
  one after another. A turn looking at the same instant as the turn before it would miss what that
  turn made, or the first speaker would never see the answer. No simulated time passes.
- **The note** (`perceive.frame_of`, `Heard.frame`): a speaker in view heading within 45° of the
  listener's opposite way faces it; within 45° of its own way walks its way; otherwise no note.
  45° is mine, a placeholder. `Heard.frame` is left out of a view record when unset, so earlier
  records are written as before.
- **`resolve_v9`** (frozen, MANIFEST): v8 word for word except: the silent section (independent's
  instructions and reply format, plus "You may be asked again later, if something changes."); talk's
  "It takes as long to say as it would in life." → "They hear all of it before they decide what to
  do."; non-verbal and talk's signal sentence gains ", and see your signal before they decide what to
  do"; `heard_seen_facing` / `heard_seen_same_way`. Flags `exchange: turn_taking`, `heard_frame: true`.
  **The wording is my draft, for the user to review before a paid run.**
- **Experiment layer:** a template's exchange must match `protocol.exchange` (v9 refused under
  `real_time`, v1 to v8 under `turn_taking`) and must offer every condition the config lists.
  `first_asked(session)`: person 1 in odd repeats, person 2 in even ones (pairs, all first runs:
  person 1). `outcomes.csv` gains `first_asked` (`p1`/`p2`) only in a paused exchange.
- **Config** `configs/resolution/round1_head_on_turn_taking.yaml`: RF-39's with conditions silent,
  non-verbal and talk, `resolve_v9`, `exchange: turn_taking`, cap 0 (no approval). `--plan`: 816
  sessions, 272 a condition. People: by unit, so silent's are RF-39's non-verbal ones (tested).
- **The gate** is RF-10's, carried over unchanged (0.50 of the first runs, now over silent,
  non-verbal and talk). [Mine: the user may want a different gate for RF-40.]
- **Docs:** `resolution.md` D3 amended; `encounter-protocol.md` section 4 (the paused exchange and
  its assumptions) and the protocol keys; `CLAUDE.md`'s conditions line and pending item 4 (#55's
  "silent" was what became non-verbal, not this one).
- **Analysis:** `analysis.load` knows silent (no signal) and adds `asked_first` when the column is
  there; `analysis.sidestep_reprompt` takes silent as the dance reference when there is no independent.
- Tests: `tests/test_rf40_turn_taking.py`, 16, pass; `analysis` tests touched pass (17).
  Enumeration-sensitive files (repo hygiene, ethnicity, factors, extraction, rules database, baselines,
  rulegen describe and cases): 277 passed, 1 failed, the known one: `test_ethnicity`'s list of configs
  written after #92 needed the new config. Added; passes.

### 2026-11-01 — Mock rehearsal (`runs_mock/rf40/`, 816 of 816)
- Sessions finished 13:46 UTC; replays and tables after. `outcomes.csv` has `first_asked`: person 1 in
  every session of repeats 1 and 3 (192 each), person 2 in repeats 2 and 4, person 1 in all 48 pair
  sessions.
- Calls a session: silent 9.99, non-verbal 11.25, talk 11.31 (at most 17). In 399 non-verbal and 431
  talk pauses the second agent was asked because of the first's signal or message. Silent made no
  signal and said nothing. Every heard message from someone in view carried the note (36, all facing).
- **Hearing range:** of the mock's 113 talk utterances, 56 were heard by nobody (out of range). In a
  paused exchange a message is said when the agent decides, often 9 to 10 m away. For the user.
- **Cost** (off-peak, RF-39's measured cost a call: non-verbal USD 0.000174, talk 0.000180; silent
  costed as non-verbal): the mock's calls give **USD 1.56**; scaled by RF-39's real calls against its
  mock's (0.77, 0.75), **USD 1.19**. Recommended cap **USD 1.80**, a pilot first. Balance USD 4.18.

## Open questions / risks
- **Hearing range in the pause** (for the user): a message is heard only within 8.9 m (quiet) or
  3.2 m (busy), as D2 says. At the first decision (about 9 to 10 m apart) a message in a busy cell is
  not heard at all. The user expected B always to hear A. Kept as D2 has it until the user decides.
- An answer reaches the first speaker only at its next decision point (each member once a pause).
- `resolve_v9`'s wording is mine; the gate is RF-10's carried over.
- No paid call without the user's recorded approval and cap for #129.

## Summary (fill in at the end)
