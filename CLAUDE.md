# Project: Crowd Behaviour Modelling using LLM: Conflict Resolution

## Overview
This is a Final Year Project (FYP). Crowd simulation models the movement/dynamics
of many entities (agents). Simulations can stall when agents have conflicting
actions — e.g. two people trying to cross the same bridge from opposite sides.
This project models conflict-resolution behaviours by extracting them from an LLM,
which is used as a "world model" for how agents should behave.

## Repo layout note
This repository **is** the `CrowdSimulation` working folder. It used to be a
subfolder inside a larger FYP folder and has been split out on its own so it can
be tracked in git / GitHub Desktop. Everything under this repo root IS the
crowd-simulation work — see `README.md` for the directory layout and the live
status of each roadmap step. There is no more need for a `/CrowdSimulation`
prefix on new work; put it directly under the relevant existing folder
(`dataset/`, `pipeline/`, `integration/`), or a new top-level folder here if it
genuinely doesn't fit an existing one.

Three reference documents live **outside this repo**, in the parent FYP folder
(not moved here, not tracked in this git history):
- `ChooZhenMing_FYP_Project_Plan_Strategy.docx`
- `Conflicting Agents Conflict Management in a Multi-agent Systems.pdf`
- `CrowdGym A Crowd Simulation Environment for Reinforcement Learning.pdf`
  — the senior's prior FYP (Goh Chen Wei, NTU AY2025/26), the baseline this
  project improves on.

Check `integration/crowdgym_mapping.md` and `dataset/schema/README.md` first —
they already distil the parts of the CrowdGym report that matter here (AgentType
params, `RL_take_action`, journeys, RiMEA test scenarios). Only ask the user for
the PDF's current path if you need something beyond what's already distilled
there; don't assume a relative path to it still resolves after the move.

## Background — continuation of a senior's project
This FYP continues a senior's prior FYP, **CrowdGym** (see above). Treat their
existing method as the baseline to improve on, not something to redo from scratch.

Goal: improve on the senior's method and ultimately reach a crowd simulation
capable of handling **10,000 agents** without becoming too slow.

## Current task: resolve first, then extract rules (track #55, since 2026-10-20)
At the supervisor meeting of 2026-10-20 the method changed. Until then (issue
#30) an LLM was asked to negotiate or state a conflict rule directly. The work
now follows four steps, tracked in issue #55 and built in issues #56 to #81
(RF-1 to RF-25; RF-16 to RF-25 were added on 2026-10-22, so the RF numbers no
longer follow the order of work, which #55 gives):

1. **Step 1 — resolve.** Test whether LLM agents can resolve a conflict,
   without asking them for a rule.
2. **Step 2 — extract.** If they can, extract the hidden rule or pattern from
   how they resolved it, and ask the LLM for the reference the rule comes from.
3. **Step 3 — verify.** Verify the rule against real human behaviour.
4. **Step 4 — factors.** Include as many factors as possible, find which ones
   actually drive the decision, and build a mapping from factors to decision.

The step numbers are labels, not the order of work: factor screening (RF-10)
comes before rule extraction (RF-11) and verification (RF-14). The rule format
no longer matters much (see "Supervisor decisions"). The code is in
`llm_negotiation/` (negsim); `README.md` has the roadmap and
`llm_negotiation/README.md` the section "Direction since October 2026".

Step 1 follows `llm_negotiation/docs/resolution.md` (decisions D1 to D17),
decided by the user on 2026-10-22 on their own authority, with no supervisor
sign-off needed. An agent's reply says what it physically does (`intent`, then
`steps`), with no `priority` field: who went first is measured in the replay.
Its description follows what a person would perceive (a 75° view to 10 m,
detail within 5 m, hearing from any direction). There are three conditions
(independent, non-verbal, talk), prompting is event-driven, and each agent is
debriefed afterwards for the reference behind its decision. The work goes one
scenario at a time, in rounds (D15 to D17). Architecture section 8.7 holds the
decision record.

Constraints for every RF issue (from #55):
- No paid call unless this file records the supervisor's approval of paid runs
  and the cap for that phase or round (see "Pending sign-offs").
- No reply format may ask an agent who goes first.
- Perceived attractiveness and ethnicity stay off by default. No paid run with
  either switched on until this file records that factor's own ethics sign-off.
  (Since 2026-10-24 real ethnicity replaces the fictional group in this track;
  see "Pending sign-offs", item 3.)
- No rule may read a person's ethnicity (or group), in any version of the rule format.
  *Amended 2026-10-26 (issue #108, RF-31), agreed by the supervisor (see "Supervisor
  decisions"):* perceived attractiveness is readable from rule format 4 only, as a person's
  own view of the other (`self.finds_other_attractive`, inside `own_when`). Rule formats 1 to 3
  still refuse it, and so does format 4 anywhere else.
- Prompt templates are frozen: a wording change means a new template version,
  never an edit.
- Every feature is built and tested on the mock client first.
- Configs and templates from before this track must keep behaving exactly as
  before.

Budget:
- LLM used for dataset generation: **DeepSeek API** (~$2 credit budget; current
  spend tracked in `pipeline/config.py` -> `ALREADY_SPENT_USD`) — be mindful of
  token usage when touching the prompting scripts.
- The negotiation work's paid calls are logged separately, one line per call, in
  `llm_negotiation/spend_ledger.jsonl`. The total spent is the two added
  together; neither file alone gives it.
- **Balance checked 2026-10-24: USD 1.49** (DeepSeek's balance endpoint; 1.48
  topped up, 0.01 granted), before issue #64's pilot. The records above add up
  to about USD 0.10 of a USD 2.00 credit, so about USD 0.41 is unaccounted for:
  either the credit was not 2.00, or the key was used outside these records.
  Plan caps against the balance, not against USD 2.00 (`WORK_LOG-64.md`).
  After issue #64's pilot (USD 0.075 in the ledger): **USD 1.41**, checked
  2026-10-24. After issue #65's screen (USD 0.290 in the ledger, cap 0.35):
  **USD 1.13**, checked 2026-10-24. After issue #98's comparison (USD 0.050 in the
  ledger, cap 0.08): **USD 1.08**, checked 2026-10-25.
  After issue #100's run on deepseek-v4-pro (USD 0.176 in the ledger, cap
  0.30): **USD 0.91**, checked 2026-10-25.
  After issue #101's run (USD 0.049 in the ledger, cap 0.08): **USD 0.86**,
  checked 2026-10-25.
  After issue #104's run (USD 0.221 in the ledger, cap 0.30): **USD 0.65**,
  checked 2026-10-25.
  After issue #66's extraction (USD 0.023 in the ledger, cap 0.05): **USD 0.64**,
  checked 2026-10-26.
  After issue #67's translation (USD 0.0017 in the ledger, cap 0.03): **USD 0.62**,
  checked 2026-10-26 (0.63 just before it).
  After issue #108's translation and its retry (USD 0.0029 in the ledger, cap 0.05):
  **USD 0.62**, checked 2026-10-26 (the endpoint shows two decimals; 0.62 just before it too).
  After issue #110's run with its pilot (USD 0.0619 in the ledger, cap 0.15): **USD 0.56**,
  checked 2026-10-28 (0.62 just before it).
  After issue #115's run with its pilot (USD 0.1688 in the ledger, cap 0.20): **USD 0.39**,
  checked 2026-10-28 (0.56 just before it).
  After issue #117's run with its pilot (USD 0.0707 in the ledger, cap 0.10): **USD 0.32**,
  checked 2026-10-28 (0.39 just before it).

### Phase 1 (on hold): the behaviour dataset
The task from the first supervisor meeting, on hold since the second meeting.
The supervisor wanted a **dataset of typical human behaviours under different
scenarios**, generated by prompting LLMs. The underlying research question:
*do LLMs actually understand human behaviour well enough to be used as agents
in the crowd simulation?*

- Dataset covers everyday scenarios (crossing a road, taking a lift, queuing, ...)
  as well as conflict-causing ones (bottlenecks, crossflow, doorway deadlocks,
  ...) — see `dataset/scenarios.yaml`.
- **Scope confirmed 2026-09-04**: dataset is Singapore-only, organised by age
  group and gender (`dataset/personas.yaml`). The design decisions for how the
  dataset is generated and mapped to CrowdGym (DD1-DD4, e.g. generating per
  persona rather than per persona-pair) are recorded in `README.md` and have
  supervisor sign-off.
- First generation run (`run01`) is done: 420 API calls, 140 aggregated records,
  actual cost $0.097. Automated validation passes format/coverage; a systematic
  "female personas yield more than male" pattern was flagged for supervisor
  discussion — see `dataset/generated/validation_report.md`.

## Roadmap
See `README.md` for the live status of each step. The RF issues, in the order
they are to be worked, are listed in track issue #55. Phase 1's steps (dataset
schema, prompting pipeline, generation, validation, the bridge to CrowdGym) are
in `README.md`, "Order of work (from the plan) and current status".

## Supervisor decisions
Ethics sign-off for the perceived-attractiveness factor (issue #61): approved by the supervisor on 2026-10-24

Ethics sign-off for the real-ethnicity factor (issue #92): approved by the supervisor on 2026-10-24

Rules may read perceived attractiveness (issue #108, RF-31): agreed by the supervisor, reported by
the user on 2026-10-26, "since we want to research on whether it affects decision in real time".
As `docs/pairwise-factors.md` section 7 required, this was the supervisor's decision. It applies
from rule format 4, and only as a person's own view of the other (`self.finds_other_attractive`,
in an own-only condition). Real ethnicity stays unreadable by every rule, in every version. The
ethics-gate sentences for paid runs above are unchanged.

### Meeting of Tuesday 2026-10-20
The user's notes from the meeting, word for word:

> Can prompt LLM to provide the reference where the rule came from
>
> First step is asking LLM to resolve the conflict, and only after that do the rule (and verify the rules with real human behaviour)
>
> The format of the rule is no longer important (Do not focus on this part too much), because we can ask AI to translate those mapping to different simulators.
>
> Our main goal is:
>
> Ask whether LLM can resolve the conflict
>
> If it is able to resolve the conflict, try to find the hidden rule/pattern that it resolves the conflict
>
> We can include as many factors as possible, and try to find which parameters are the one that actually contributes to the decision made by the LLM
>
> After that, verify the extracted rule with real human behaviour
>
> See the factors affecting the decision (See which factors contributes to the decision)
>
> The rule can be more specific (for example the keep left rule)
>
> Can also include more factors (e.g. attractiveness of the agent (represented in a matrix)...) - and there can be a mapping

**Summary (not the supervisor's words; the notes above are the record):**
- Resolve first: test whether LLM agents can resolve a conflict before asking
  for any rule. Only then extract the rule or pattern behind how they resolved it.
- Ask the LLM for the reference a rule comes from.
- Verify extracted rules against real human behaviour. What counts as "real
  human behaviour" is pending (see below).
- Include many factors and find which ones actually drive the LLM's decision;
  build a mapping from factors to decision. More factors may be added, for
  example the agent's attractiveness represented as a matrix (an ethics
  sign-off is pending, see below).
- The rule format no longer matters much, since an LLM can translate a rule for
  each simulator. Rules may be more specific, for example "keep left".

## Pending sign-offs
Items 1, 5 and 6 are still pending (item 1 was approved for issues #64, #65, #98, #100, #101, #104, #66, #67, #108, #110, #115, #117 and #119 only).
**Do not treat any of them as approved** until the user records the
supervisor's answer in this file, with a date. Items 2 and 3, the ethics
sign-offs for perceived attractiveness and real ethnicity, were recorded by the
user as approved by the supervisor on 2026-10-24. Items 4, 7 and 8 were decided
by the user on 2026-10-22, on their own authority, as part of the resolution
design (`llm_negotiation/docs/resolution.md`); they need no supervisor sign-off.

**The code's ethics gates read one exact sentence each**, not the items below:
a paid run that varies the factor is refused until this file holds the
factor's sentence, word for word, with the date. Perceived attractiveness:
`llm_negotiation/docs/pairwise-factors.md`, section 6 (issue #61). Real
ethnicity: `llm_negotiation/docs/ethnicity.md`, section 6 (issue #92). The fictional group:
`llm_negotiation/docs/fictional-groups.md`, section 6 (issue #32; no longer
used in this track). Numbers in brackets are the decisions of track issue #55.

1. **PENDING** — Paid runs, and their cap: a total of about USD 1.80, split per
   phase (#55, 1). Until it is recorded, no paid call. The balance is now
   USD 1.49 (see "Budget"), so the total needs revising.
   - **Approved for issue #64 only, 2026-10-24:** the user confirmed approval of
     paid runs for RF-9's pilot (#64), and only for it, with a cap of
     **USD 0.20** on that experiment's own calls (`experiment_name: rf_pilot`).
     Every other paid run still needs its own approval and cap recorded here.
   - **Approved for issue #65 only, 2026-10-24:** the user approved paid runs for
     RF-10's round 1 screen (#65), and only for it, with a cap of **USD 0.35** on
     that experiment's own calls (`experiment_name: rf10_round1_head_on`; 288
     sessions, about USD 0.25 off-peak, `WORK_LOG-65.md`).
   - **Approved for issue #98 only, 2026-10-25:** the user approved paid runs for
     RF-27's comparison of `resolve_v7` with `resolve_v6` (#98), and only for it,
     with a cap of **USD 0.08** on that experiment's own calls
     (`experiment_name: rf27_round1_head_on_v7`; 88 sessions estimated, 96
     run, independent condition only, USD 0.050 off-peak, `WORK_LOG-98.md`).
   - **Approved for issue #100 only, 2026-10-25:** the user approved paid runs for
     RF-28's run of the same head-on sessions on `deepseek-v4-pro` (#100), and
     only for it, with a cap of **USD 0.30** on its own calls (96 sessions,
     independent condition only, about USD 0.19 off-peak, `WORK_LOG-100.md`). The
     cap covers both of its experiments together: `rf28_round1_head_on_v4pro`
     (6 sessions at a reply cap of 300, USD 0.0116) and, by the user's decision
     the same day, `rf28_round1_head_on_v4pro_cap600` (the run of record, reply
     cap 600, its own cap USD 0.28).
   - **Approved for issue #101 only, 2026-10-25:** the user answered "Yes" to
     recording paid-run approval for RF-29's run of the head-on sessions under
     `resolve_v8` (the sidestep option) on `deepseek-flash` (#101), and only for
     it, with a cap of **USD 0.08** on that experiment's own calls
     (`experiment_name: rf29_round1_head_on_sidestep`; 96 sessions, independent
     condition only, about USD 0.05 off-peak, `WORK_LOG-101.md`).
   - **Approved for issue #104 only, 2026-10-25:** the user approved paid runs for
     RF-30's rerun of head-on's non-verbal and talk conditions under
     `protocol.execution: keep_line` (#104), and only for it, with a cap of
     **USD 0.30** on that experiment's own calls (`experiment_name:
     rf30_round1_head_on_keep_line`; RF-10's design, 192 sessions, about USD 0.24
     off-peak, `WORK_LOG-104.md`).
   - **Approved for issue #66 only, 2026-10-26:** the user answered "Yes I
     approve" to paid runs for RF-11's rule extraction from round 1 (#66), and
     only for it, with a cap of **USD 0.05** on that experiment's own calls
     (`experiment_name: rf11_round1_head_on`; three extraction calls, about
     USD 0.006 each off-peak, `WORK_LOG-66.md`). The user also decided the same
     day that head-on goes on to extraction although its gate passed narrowly.
   - **Approved for issue #67 only, 2026-10-26:** the user approved paid runs for
     RF-12's translation of RF-11's four candidate rules into rule format 3 (#67), and
     only for it, with a cap of **USD 0.03** on that experiment's own calls
     (`experiment_name: rf12_round1_head_on`; four calls, worst case USD 0.028,
     `WORK_LOG-67.md`).
   - **Approved for issue #108 only, 2026-10-26:** the user approved paid runs for
     RF-31's re-translation of round 1's four candidate rules into rule format 4 (#108),
     and only for it, with a cap of **USD 0.05** on that experiment's own calls
     (`experiment_name: rf31_round1_head_on`; four calls, worst case USD 0.043,
     `WORK_LOG-108.md`). *The same day* the user answered "Yes" to retrying the one
     unreadable translation (`x_head_on_6455ca5589`) as a further paid call, inside the
     same cap: USD 0.05 for #108's calls together, of which USD 0.0025 was spent before
     the retry (`experiment_name: rf31_round1_head_on_retry`, its own cap the rest).
   - **Approved for issue #110 only, 2026-10-28:** the user approved paid runs for RF-32's
     round 1 with three or four people (#110), and only for it, with a cap of **USD 0.15** on that
     experiment's own calls (`experiment_name: rf32_round1_group_head_on`; 72 sessions, independent
     condition only, about USD 0.07 off-peak from RF-10's measured cost per call, `WORK_LOG-110.md`).
     The user also answered "Run as built" to the issue's design choices listed there.
   - **Approved for issue #115 only, 2026-10-28:** the user approved paid runs for RF-34's
     non-verbal run of RF-32's group sessions (#115), and only for it, with a cap of **USD 0.20** on
     that experiment's own calls (`experiment_name: rf34_round1_group_head_on_non_verbal`; 72
     sessions, non-verbal condition only, about USD 0.12 to 0.14 off-peak, up to about 0.20 at the
     mock's call count, `WORK_LOG-115.md`).
   - **Approved for issue #117 only, 2026-10-28:** the user approved paid runs for RF-35's
     encounters sampled from crowds (#117), and only for it, with a cap of **USD 0.10** on that
     experiment's own calls (`experiment_name: rf35_crowd_encounters`; 72 sessions, independent
     condition only, about USD 0.07 off-peak from RF-32's measured cost per call, `WORK_LOG-117.md`).
   - **Approved for issue #119 only, 2026-10-29:** the user answered "ok run as built, do with your
     recommendation" to paid runs for RF-36's non-verbal run of RF-35's crowd encounters (#119), and only
     for it, with the recommended cap of **USD 0.15** on that experiment's own calls (`experiment_name:
     rf36_crowd_encounters_non_verbal`; 72 sessions, non-verbal condition only, about USD 0.11 to 0.12
     off-peak from RF-35's measured cost per call, a pilot first, `WORK_LOG-119.md`). The same answer
     keeps D5 as written (a bystander coming into view prompts again).
2. **Approved by the supervisor, 2026-10-24** — Ethics sign-off for perceived
   attractiveness as a factor (#55, 3). *The user decided on 2026-10-24* that
   attractiveness (both directions) is **in** RF-10's design, because bias can
   affect the decision a person makes. For the code's gate, see above.
3. **Approved by the supervisor, 2026-10-24** — Ethics sign-off for **real
   ethnicity** as a factor. *The user decided on 2026-10-24* that real
   ethnicity replaces the fictional group in this track: Singapore's ethnic
   groups at their resident shares (SingStat, *Population Trends 2026*,
   end-June 2026: 73.9% Chinese, 13.5% Malay, 9.0% Indian, 3.6% Others), built
   in RF-26 (issue #92), and included in RF-10. For the code's gate, see above.
   The fictional group (issue #32) stays only in the rule-generation layer,
   unchanged; its own sign-off is no longer needed for this track. *Earlier
   wording:* whether the fictional group stays, and its ethics sign-off,
   pending since issue #32.
4. **Decided by the user, 2026-10-22** — Whether to add the silent condition
   beside the talk condition (#55, 4): three conditions, namely independent,
   non-verbal and talk (`resolution.md`, D3).
5. **PENDING** — How far the portable-rules track (#34) is paused: only the
   build (#42 onward), or the remaining literature issues (#35 to #41) as well
   (#55, 5).
6. **PENDING** — What "verify with real human behaviour" means: published
   studies only (RF-14 as written), or observed data such as recorded pedestrian
   trajectories, video or field observation in Singapore (#55, 6).
7. **Decided by the user, 2026-10-22** — Which LLM gives the reference for a
   rule: the extractor model that writes the rule from the results, or the
   agents themselves, asked afterwards in a debrief (#55, 7): both, the agents
   in a debrief and the extractor in RF-11 (`resolution.md`, D8).
8. **Lifted by the user, 2026-10-22** — Whether the "no new simulation code
   until the literature review is discussed" instruction is lifted (#55, 2):
   the design needs new simulation code (RF-4, RF-17), and the user is fine with
   adding it. Recorded as unconfirmed in `README.md` from issue #24 until then.

## Notes for Claude Code
- When asked to work on a GitHub issue, follow `github_issue_workflow.md`
- Check `integration/crowdgym_mapping.md` and `dataset/schema/README.md` before
  proposing anything that touches CrowdGym — go back to the original PDF
  (outside this repo) only for details not already covered there.
- Flag clearly when something is a design decision vs. an assumption you're
  making, since supervisor sign-off matters for this project.
- When helping with dataset validation, prioritize methods that are explainable
  and defensible in a report, not just automated metrics.
- `.env` holds the DeepSeek API key. Never print it, commit it, or include it in
  any output — `.gitignore` already excludes `.env` from version control.
