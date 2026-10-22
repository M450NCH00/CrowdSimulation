# Work Log — Issue #57: RF-2: Step 1 templates (independent, non-verbal, talk) and a debrief, the View structure, the scenario interface, and the reply parser

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/57
**Branch:** feat/57-resolve-templates-view-parser (cut from `docs/72-record-resolution-design`, as track #55's branches stack; see the memory note on `git checkout main`)
**Started:** 2026-10-22

## Understanding the issue

Step 1 of track #55 asks whether LLM agents can resolve a conflict, and how, without being
asked for a rule. This issue writes the prompts an agent is shown and reads its replies, as
`llm_negotiation/docs/resolution.md` (D1 to D3, D8, D16) decides:

- a `View`: everything one agent is told at one decision point, block by block (D2);
- a scenario plug-in interface, description side (D16), with the passing scenarios of rounds
  1 to 3 in one frozen scenario template `scenario_passing_v1.yaml`;
- a core template `resolve_v1.yaml` with one section per condition (independent, non-verbal,
  talk) and a debrief template `resolve_debrief_v1.yaml`, frozen with the existing tool;
- a reply parser (D1) and a debrief parser (D8), with one retry;
- mock policies `resolve_paths_v1` and `debrief_paths_v1`, and tests.

Out of scope: views from the running simulation (RF-17), carrying out plans (RF-4), running
sessions (RF-3), new persona factors (RF-5, RF-6). Paid calls: none.

## Plan

1. Branch, work log (this file).
2. Templates: `scenario_passing_v1` (the place lines of `rulegen_negotiate_v2` word for word,
   the three passing events), `resolve_v1` (role, per-condition instructions and reply format,
   every D2 block's lines, the decision-point wrapper), `resolve_debrief_v1`. Register three
   new template kinds in `prompts.TEMPLATE_KINDS` (adding kinds changes nothing for the
   existing templates). Freeze the three with `negsim.negotiation.freeze`.
3. `negsim/resolution/`: `view.py` (the `View` and its blocks, rendering), `scenario.py`
   (`Scenario` base, `PassingScenario`), `adapter.py` (first decision point of a frozen
   two-person case), `prompt.py` (messages for a decision point, the debrief), `reply.py`
   (reply and debrief parsers), `mock.py` (the two mock policies).
4. Tests: render every case in every condition; nothing the agent cannot perceive; no
   convention words; no "first"/"priority"; every parser path; the fixed text byte-identical
   across agents and decision points; a toy second scenario defined only in the tests.
5. Full test suite; the existing templates must still render byte for byte as before.
6. Push, PR (targets `docs/72-record-resolution-design`), comment on #57.

## Progress log

### 2026-10-22 — Read the issue, the spec and the existing code
- What I did: read #55 (track), #57, `docs/resolution.md`, `prompts.py`, `parsing.py`,
  `freeze.py`, `rulegen/describe.py`, `rulegen/mock.py`, the `request_with_retry` helper of
  `negotiation/protocol.py`, and the case files.
- Why: the issue's "Before starting" list.
- Result / what I found:
  - #56 and #72 are merged, so #57 is the next unchecked issue of #55's order.
  - **The frozen cases' snapshots are often not a decision point under D2.** The head-on and
    bottleneck cases are frozen at 12.3 to 12.4 m apart and the crossings at 11.3 to 11.7 m,
    beyond D2's 10 m seeing range; in the overtaking cases the person ahead has the other
    straight behind them (bearing about 180°), outside the 75° cone; the passage cases are at
    0.6 m. The 16 `flow_*` files are pairs out of 100-person crowds. So the adapter applies
    D2's cone and ranges as written, and an agent who sees nobody is told so; the real first
    decision point is found by RF-3's trigger (D4), not by this adapter.
- Next step: write the templates.

## Open questions / risks

## Summary (fill in at the end)
