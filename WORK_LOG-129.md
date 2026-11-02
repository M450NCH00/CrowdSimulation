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

### 2026-11-02 00:33 UTC — The user's answers; approval and cap
- The user (pasting the questions of the previous session): "I approve the run", and on whether the
  first speaker can answer in the same pause: "I want it so that A only hears it in the next prompt,
  because after B reply, A will observe that B has replied and then reply back". **As built**: each
  member at most once a pause; B's reply is made one turn after A's look, so at A's next decision point
  (D5's 1 s gap) `heard:B` makes A due, and its prompt carries B's words. Only D5's own gate (a conflict
  still predicted, or the plan ended) can keep A from being asked. Two tests pin it.
- Asked the rest (AskUserQuestion): **hearing range** "Always heard"; **cap** "USD 1.80"; **resolve_v9's
  wording and RF-10's gate** "Accept both". Recorded in `CLAUDE.md` (pending item 1, #129 only).
- **Built** `protocol.always_heard` (false by default, left out of records when off, refused without
  `turn_taking`): in a pause everyone in the encounter hears a message whatever the distance
  (`Exchange.say(..., always=members)`); anyone outside the encounter still within D2's range. A
  departure from D2, stated in `encounter-protocol.md` section 4 and `resolution.md` (D3's amendment).
  The config sets it, and `cap_usd: 1.80`. Tests: 3 new in `test_rf40_turn_taking.py`.
- Pricing page re-read 00:37 UTC: no change (`date_checked` 2026-11-02, `docs/pricing-check.md`).
  Balance (`GET /user/balance`, the key not printed): **USD 4.18**.
- Timing [mine]: Monday; peak 01:00 to 04:00 and 06:00 to 10:00 UTC (double rate). The pilot in the
  04:00 to 06:00 window, the rest from 10:00 UTC.
- Mock rerun into `runs_mock/rf40_always_heard/` (a resolution run resumes and never overwrites).

### 2026-11-02 01:30 UTC — Mock rehearsal with always heard (816 of 816)
- Started 00:34, finished 01:30 UTC (with the related tests running beside it).
- **Heard:** of 113 messages, 0 heard by nobody (the first mock: 56). Decision points asked because
  of a heard message: 92 (the first mock: 36). Calls a session: silent 9.99, non-verbal 11.25, talk
  11.52 (was 11.31).
- **Cost** (off-peak, RF-39's cost a call): the mock's 8,909 calls give **USD 1.57**; scaled by RF-39's
  real calls against its mock's, **USD 1.20**. Inside the cap of USD 1.80.
- Related tests (protocol, perception, pairwise, ethnicity, v6, RF-32, RF-34, RF-39, RF-40, hygiene):
  380 passed, 12 skipped; `test_llm.py` 45 passed. Committed `3a876e41`.
- Next: the pilot, `--client deepseek --confirm --limit 24`, at 04:00 UTC (off-peak), then its replays.

### 2026-11-02 04:10 UTC — Pilot (24 sessions, USD 0.0392, off-peak)
- Started 04:01:32, ended 04:10:04 UTC. 10 silent, 6 non-verbal, 8 talk; no transport error, no session
  aborted. Model fingerprint `bc19ba97...` throughout, as in RF-39.
- **The pause works as the user decided.** In talk, B hears A's message in full in the same pause, with
  the note (`facing`); A hears B's answer at its next decision point, 1 s later, asked because of it
  (`heard:n`). 32 messages, none unheard. E.g. `T_..b7fe7ead_r2`: "Hi! Fancy seeing you here." / "Sorry,
  I can't stop, I'm on my way to the emergency room." / (next decision) "Oh no, go ahead, don't let me
  keep you!" / "Thanks, I'm coming through!". Both still wave each other on at times: data, not a fault.
- **Silent:** no signal and no message in any of its 77 readable replies (80 decisions), no flag; asked
  again as in non-verbal.
- **Unreadable:** 6 of 159 decisions after the retry (3.8%; RF-39's full run 112 of 3,987, 2.8%):
  `start: "other_passes"` 3, `until` 5 m with the other at 5.0 m 1, `until: {"after_seconds": 4}` 1,
  bad JSON 1. The same kinds as before; nothing in `resolve_v9`'s new wording.
- **Debriefs:** 47 of 48, none unreadable; the missing one is an agent whose only reply was unreadable
  (nothing to debrief). `side_basis`: where they were 24, more room 16, custom or rule 4, either side 3.
- **Resolved by the LLM:** silent 6 of 10, non-verbal 5 of 6, talk 4 of 8 (too few to read).
- **Cost:** 213 calls, USD 0.0392; projected for 816 **about USD 1.33**, inside the cap of USD 1.80.
- Decision [mine, within the approved plan]: nothing to fix. The rest split around peak hours (double
  rate): 220 sessions now (04:14, about 80 min at the pilot's pace), the remaining 572 from 10:01 UTC.

### 2026-11-02 05:30 UTC — Second batch (220 sessions, off-peak)
- 04:13:26 to 05:30:28 UTC; 244 of 816 done, USD 0.3781 in the ledger (2,124 calls, all off-peak, no
  error). Projected for 816: about USD 1.26. The remaining 572 scheduled from 10:01 UTC.

### 2026-11-02 13:40 UTC — The run is complete (816 of 816)
- The remaining 572: 10:01:32 to 13:40:02 UTC (the last paid call 13:11, then replays and tables).
  No sleep events during the run (Kernel-Power 506/507: last at 00:01 UTC).
- **Spend:** USD 1.2261 in the ledger (5,420 decision calls, 1,631 debriefs; 7,051 calls, all off-peak,
  no error), cap USD 1.80. Balance (`GET /user/balance`): **USD 2.96** (4.18 before). Recorded in
  `CLAUDE.md`'s Budget.
- **Runner's headline** (`report.md`), resolved by the LLM: silent 64%, non-verbal 54%, talk 58%
  (RF-39: independent 37%, non-verbal 60%, talk 61%). Collisions 270 of 816. Unreadable decisions after
  the retry: 121. Not read yet: the gate, `asked_first`, dances, what talk said; the report comes next.
- `.gitignore`: RF-40's replay `interactions.jsonl` and `pair_interactions.jsonl`, as RF-39's.

### 2026-11-02 — Analysis and report
- Ran `analysis.gate`, `analysis.lateral`, `analysis.sidestep_reprompt`, `analysis.compare` (RF-39
  non-verbal and talk) and the factor report (`python -m analysis <outcomes.csv>`; a folder is refused).
- New module `analysis/turn_taking.py` (standard library; 6 tests in `analysis/tests/test_turn_taking.py`;
  the analysis suite 97 passed): talk by decision number; a heard side against the listener's next
  move, by the message's frame; speakers' words against their own moves; who is asked first.
- Written up in `runs/rf40_round1_head_on_turn_taking/comparison_report.md`. Main results: the gate
  passes (123 of 192 first runs, 0.64); silent 0.64 against RF-39's independent 0.36 (p < 0.0001),
  non-verbal and talk no better than silent; at the first pause 4 of 499 talk replies name a side
  (greetings instead); a heard side is followed by a fitting move in 35 of 100 (coin p = 0.004);
  "coming through on your X" contradicts the speaker's own move in 16 of 27; who is asked first: no
  effect (talk p = 0.10).
- Coding choices [mine]: the frame and "restates the side" keyword matches; "fits" compares with the
  speaker's side at the decision it spoke.
- Claims re-read against the tables: two corrected before commit (decision points 5,256, not calls
  5,420; 124 side messages heard, 100 of them with both aside).

## Open questions / risks
- ~~Hearing range in the pause~~: decided 2026-11-02, always heard within the encounter (a departure
  from D2 the report must state).
- ~~An answer reaches the first speaker only at its next decision point~~: the user's choice, 2026-11-02.
- ~~`resolve_v9`'s wording; the gate~~: accepted by the user, 2026-11-02.
- ~~No paid call without approval~~: approved for #129, cap USD 1.80 (`CLAUDE.md`).

## Summary
RF-40 built the turn-taking exchange (`protocol.exchange: turn_taking`, `always_heard`), the silent
condition and `resolve_v9`, and ran 816 sessions for USD 1.2261 of the USD 1.80 cap (balance USD 2.96).
Head-on passes the gate at 0.64. Being asked again, not signals or words, is what resolves; talk does
not coordinate a side (report: `runs/rf40_round1_head_on_turn_taking/comparison_report.md`).
