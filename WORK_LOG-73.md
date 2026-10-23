# Work Log — Issue #73: RF-17: what an LLM agent perceives: view cone, occlusion, hearing, changes since it last looked

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/73
**Branch:** feat/73-llm-agent-perception-view (cut from `feat/57-resolve-templates-view-parser`, which PR #83 merged into `docs/72-record-resolution-design`; track #55's branches stack, see the memory note on `git checkout main`)
**Started:** 2026-10-23

## Understanding the issue

RF-2 (#57) defined the `View`, everything one LLM agent is told at one decision point
(`docs/resolution.md`, D2), and built it only for the snapshot of a frozen two-person case. This
issue builds the `View` from the **running simulation**, the way a person in the agent's place
would perceive it:

- **seen:** everyone whose centre is within 75° of the agent's heading and 10 m, not hidden
  behind a nearer person's disc or (switchable) a wall; full detail within 5 m, one short line
  beyond; no fixed count (`max_people` is an optional cost cap that records what it left out);
- **heard:** speech since the last decision point, from anyone within the hearing range, from
  any direction; an unseen speaker is "someone" with a rough direction and a distance band;
- **signals:** only if the observer could see the signaller when it was made (eye contact and
  nod also within an eye-contact range);
- **changes since you last looked** (D5 thresholds), **time to meet** (only when the closest
  approach is inside the safety distance), **history lines** (own earlier intents and what came
  of them);
- **stable labels** for the whole encounter;
- a config block `llm_view` with sourced values and marked placeholders.

It changes **only what the LLM is told** (D10): ORCA's neighbour search and the perception
record rules read stay byte for byte as they are.

Out of scope: when agents are prompted (RF-3), carrying out plans (RF-4), any change to ORCA or
the perception record. Paid calls: none.

## Plan

1. Branch, work log (this file).
2. Read `resolution.md` (D2, D5, D10, D12), `perception.py`, `simulation.py`, `perception.md`,
   `parameters.md`, architecture DD8, and RF-2's `negsim/resolution/`.
3. **Template:** `resolve_v1` cannot word task 4 (an unseen speaker is always "Someone behind
   you") or task 8 (the history says only finished or ongoing). Asked the user; they chose a new
   version, `resolve_v2`: `resolve_v1` word for word plus only the missing lines. `resolve_v1`
   stays as it is, and views still render through it.
4. `configs/resolution/llm_view_v1.yaml` (the `llm_view` block, tagged) and its loader.
5. `negsim/resolution/perceive.py`: sight (cone, range, occlusion by discs and walls), hearing,
   signals, changes, time to meet, history, labels; a builder that reads a running
   `AvoidanceSimulation` without changing it.
6. Tests: the list of task 9, plus "building views every step leaves a run byte for byte the
   same".
7. Docs (`parameters.md` section 8, `resolution.md`, READMEs), full test suite, push, PR
   (targets `feat/57-resolve-templates-view-parser`), comment on #73.

## Progress log

### 2026-10-23 — Read the issue, the spec and the code
- What I did: closed #57 by hand (PR #83 merged into a stacked branch), ticked it in #55, read
  #73 and everything in its "Before starting" list, and RF-2's package.
- Result / what I found:
  - **`resolve_v1` falls short of tasks 4 and 8**, although its provenance says it holds lines
    for every block RF-17 fills: `heard_unseen` is fixed as "Someone behind you says", which is
    false for a speaker hidden ahead or beyond the seeing range ahead, and has no distance band;
    `history_outcome` is only "finished" or "still carrying out". A signal on a short (5 to 10 m)
    line has no wording either. **Decision (the user's, 2026-10-23): add `resolve_v2`.**
  - Sight through walls already has a switch in the world (`World.mutually_visible`,
    architecture DD8); RF-17 uses the same segment-through-rectangle test.
  - The conflict zone's safety distance is the two radii plus the scenario's
    `single_file.safety_margin` (`negsim.conflict.detection.ConflictDetector.clearance`).
- Next step: the config and `perceive.py`.

## Open questions / risks

## Summary (fill in at the end)
