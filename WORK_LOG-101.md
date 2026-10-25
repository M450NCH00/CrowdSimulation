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

## Open questions / risks
- The 30° default and the 3 m limit are placeholders (the issue says so).

## Summary (fill in at the end)
