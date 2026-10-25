# Work Log — Issue #101: [Experiment] RF-29: round 1 (head-on), let the agents sidestep by an amount in metres, alongside turning by degrees (resolve_v8) (paid)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/101
**Branch:** feat/101-rf29-sidestep-metres (stacked on `feat/100-rf28-v4pro-head-on`, as the RF issues are)
**Started:** 2026-10-25 (Sunday: off-peak all day)

## Understanding the issue
RF-10, RF-27 and RF-28 failed head-on for one shared reason: the agents' sidesteps, planned in
degrees and seconds, are too small for two bodies. This issue adds a step option to say the
amount: `"sidestep": {"to": "left" | "right", "metres": <number>}`. **Turning by degrees stays**
(the user, 2026-10-25: in a crowd, walking at an angle may be the only way through).

**The user's decisions (2026-10-25, all five as recommended in the issue):**
1. a sidestep walks at the step's `turn` angle, or 30° without one (a placeholder), until that far
   aside, then the agent walks on parallel to its line; a `turn` must be to the same side;
2. the step ends when that far aside, or at its `until` if sooner; `until` optional;
3. `metres` more than 0, at most 3.0 (a placeholder); a wall stops the body as now;
4. `resolve_v8` = `resolve_v6` + the option (not `resolve_v7`), with a parser flag;
5. `deepseek-flash` on RF-10's 96 independent sessions.

**Paid-run approval:** the user answered "Yes" to recording approval for this issue with a cap of
USD 0.08; recorded in `CLAUDE.md`, pending item 1.

## Plan
1. Parser (`reply.py`): `Sidestep`, `Step.sidestep`, read only under `ReplyContext.sidestep`; the
   checks of the decisions. Without the flag a `sidestep` key is an unknown key, flagged and
   ignored, exactly as before.
2. Executor (`execute.py`): the sidestep's velocity, its end (`sidestepped`), `aside_m` in the step
   record (only for a sidestep step, so older records read as before); `steps_from_dicts` reads it.
3. `code_plan`: a sidestep counts towards the plan's side.
4. `resolve_v8` (frozen), the flag on `CoreTemplate`, the protocol passing it to the parser.
5. Tests (`tests/test_resolve_v8.py`); config `round1_head_on_sidestep.yaml`; the ethnicity
   guard's skip list.
6. Mock rehearsal; check the sessions and prompts against RF-10's; pricing; balance; paid batch
   of 6, read; the rest.
7. Compare with RF-10 (all, and readable only); how often agents chose the sidestep and how many
   metres; report; README; `CLAUDE.md` balance.

## Progress log

### 2026-10-25 — Built and tested
- Parser, executor, `code_plan`, `resolve_v8` (frozen; against `resolve_v6`: the sidestep line in
  the step format, the `until` sentence's exception "or sidesteps", and the flag), the config.
  Against RF-10's config the diff is the name, the description, the condition, the pairs' comment
  and `templates.core`.
- Extra parser checks I added within the decisions (each a failure, retried): a sidestep that walks
  backwards (`sidestep_with_back_up`) or stands still (`speed_mps` 0, `sidestep_standing_still`),
  and an unknown key inside the sidestep object (`unknown_sidestep`). A `turn` of 0° in a sidestep
  step counts as no turn (the 30° default).
- Executor detail: the sideways part of the last move is clipped so that the agent lands exactly
  at its distance (checked: 30° per move, 0.4 m in 7 moves, then straight on at the new line).
- `tests/test_resolve_v8.py`: 27 tests; with `test_execute.py` and `test_resolve_v6.py`, 92 pass.
  The first draft of the angle check was off by one row (a track row is the state after its
  step's move); fixed in the test, not the code.

### 2026-10-25 — Rehearsed, priced, first paid batch
- A session test: under `resolve_v8` a mock session reads and carries out a sidestep (coded side
  right); under `resolve_v6` the same reply is unreadable (`missing_until`), as before.
- Mock rehearsal (`runs_mock/rf29/`, 96 of 96): the same 96 session ids, cells, people and weights
  as RF-10's; **every first user message identical**; the system message differs only by the
  sidestep line and the `until` exception.
- Pricing page re-read at 06:38 UTC: identical to the morning's; recorded. Balance USD 0.91.
- Paid batch of 6 (USD 0.003309): 12 of 12 readable; the sidestep used in 11 of 12 plans,
  mostly 0.3 m (0.3 to 0.6); every sidestep step ended at its distance or at its `until`. All 6
  collided, 5 of them with one agent sidestepping to its own right and the other to its own left
  (towards the same wall). A first sign only; running the other 90.

### 2026-10-25 — The paid run, and an executor rule that undoes sidesteps
- 96 of 96. USD 0.048995 (384 calls, off-peak, no error; the batch of 6 included), cap USD 0.08.
  Balance **USD 0.86**. 2 of 192 decision points unreadable. Model and fingerprint as RF-10's.
- The agents used the option: 117 of 127 readable first plans sidestep (5 more with a separate
  turn as well); metres asked median 0.4 (IQR 0.4 to 0.5); 107 sidestep steps ended at their
  distance. First-plan sides: 34 pairs the same own side, 26 opposite (same wall).
- `plan_only`: **4 of 64 resolved** against RF-10's 22 (McNemar p = 0.0003; readable only
  p = 0.0005). Collisions 54 (RF-10 37); compatible-but-narrow collisions 20 (RF-10 9);
  same-wall 17 (RF-10 18); colliding pairs a median 0.18 m apart sideways when level.
- **Why, found by tracing a replay:** a step with no `turn` (the usual follow-up, "walk at 1.3
  m/s until 0.9 m away") steers towards the path's lookahead point, which pulls the agent back to
  its **original** line. Under `as_prompted` (issue #64) the line is kept only between steps and
  after the last, not during a later plain step. Agent 1 of `I_head_on_de176842_0f57f8a5_r1`
  sidestepped 0.37 m and was 0.06 m aside by the meeting. Over the run, 53 of 108 colliding
  agents kept less than half their largest move aside when level (RF-10: 5 of 74).
- **My error:** decision 2 says the agent keeps the new line after a sidestep. I implemented the
  sidestep step but did not test a sidestep followed by a plain step, so the run does not carry
  out decision 2 whenever a plain step follows, which is most plans. The rule is RF-4's, kept by
  #64 for plain steps; it affected RF-10, RF-27 and RF-28 as well, less (their turns ran longer).
- **Every decision point of the independent runs (RF-10, 27, 28, 29) came at the trigger,
  before any plan moved** (checked: 0 of 192 each after it). So their replays can be rebuilt from
  the recorded plans under corrected execution, exactly, with no paid call.
- Stopped here and asked the user how to correct it (a new execution setting, off for every
  earlier config, and re-replays of the four runs).

### 2026-10-25 — keep_line, and the four runs carried out again
- **The user chose (AskUserQuestion): a new execution setting plus free re-replays of all four
  runs.** `protocol.execution: keep_line` = `as_prompted`, and a step with no turn walks parallel
  to the path from where the agent is. Off for every earlier config (they name `as_prompted` or
  nothing). Tests (`tests/test_reexecute.py`, 6).
- `negsim/resolution/reexecute.py`: copies each session record with the execution set, rebuilds
  both replays and `outcomes.csv` with the experiment's own functions, refuses a session with a
  decision after the trigger. **Check of the tool: under RF-29's own execution it reproduced RF-29
  exactly** (96 sessions, 66 physical columns, 0 differences).
- Re-executed RF-10, RF-27, RF-28 (cap 600) and RF-29's independent sessions under `keep_line`
  (`runs/*_keep_line/`, 17 MB each, no LLM call). Resolved: RF-10 35, RF-27 27, RF-28 21, RF-29
  27 of 64. Paired against RF-10 under `keep_line`: p = 0.22, 0.024 (worse), 0.22. RF-10 under
  `keep_line` against as run: 13 gained, 0 lost, p = 0.0002. Collisions under `keep_line` are
  mostly the pavement dance (RF-10 16 of 27, RF-29 25 of 32).
- Wrote `comparison_report.md` (two figures corrected against `gate.md` and the counts before
  committing); dated addenda in RF-10's `screen_report.md` and RF-27 and RF-28's reports; README;
  `CLAUDE.md` balance **USD 0.86**.

## Open questions / risks
- The 30° default and the 3 m limit are placeholders (the issue says so).
- `keep_line` is one reading of the prompt, decided by the user; not a sourced fact about walking.
- **Decided by the user, 2026-10-25: later rounds use `keep_line`** (recorded in #55's decisions).
- **For the user:** redoing head-on's three
  conditions under it (paid, a lean round), since RF-10's "signalling and talk do not help" was
  measured under the rule that undid sidesteps; keeping `resolve_v6`.
- **For the supervisor:** the gate is not re-decided here; independent under `keep_line` is 0.55
  (CI 0.43 to 0.66).

## Summary
**What changed.** `resolve_v8` (the sidestep option, turning kept) with its parser, executor,
coding and tests; RF-29's config and paid run; `protocol.execution: keep_line`;
`negsim.resolution.reexecute`; four re-executed runs; the report and the addenda; README;
`CLAUDE.md` (approval and balance).

**Result.** As run, the sidestep made head-on worse (4 of 64), because the executor undid it.
With the line kept, RF-10's own plans resolve 35 of 64; neither `resolve_v7`, the sidestep, nor
v4-pro beats that (v4-pro is worse). The remaining failure is coordination: the pavement dance.

**How it was verified.** Parser, executor and template tests (28), the session test, the
re-execution tests (6); a mock rehearsal matching RF-10's sessions; the pricing check and the
balance before paying; a paid batch of 6 read before the rest; the re-execution tool checked to
reproduce RF-29 exactly under its own execution; every number in the report checked against its
file.
