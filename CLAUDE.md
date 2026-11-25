# Project: Crowd Behaviour Modelling using LLM: Conflict Resolution

## Overview
This is a Final Year Project (FYP). Crowd simulation models the movement/dynamics of many entities (agents). Simulations can stall when agents have conflicting actions — e.g. two people trying to cross the same bridge from opposite sides.

**Current framing (as of the second supervisor meeting):** rather than using an LLM as a static "world model" to generate a behaviour dataset, the project now has LLMs **communicate with each other to resolve a conflict directly** (e.g. two agents needing to cross the same narrow hallway from opposite directions), then looks for a **reusable pattern** in how the conflict gets resolved — so future conflicting scenarios in the simulation can apply the pattern without re-running the full LLM-to-LLM exchange each time. Any pattern found needs validation against real human behavioural data if available, or against sociological research on real human conflict resolution if not.

## Repo layout note
This repository **is** the `CrowdSimulation` working folder (no `/CrowdSimulation` prefix needed on new paths — put work directly under the relevant existing folder (`dataset/`, `pipeline/`, `integration/`, `literature/`), or a new top-level folder here if it genuinely doesn't fit an existing one). See `README.md` for the directory layout and live status of each roadmap step.

Three reference documents live **outside this repo**, in the parent FYP folder (not moved here, not tracked in this git history):
- `ChooZhenMing_FYP_Project_Plan_Strategy.docx`
- `Conflicting Agents Conflict Management in a Multi-agent Systems.pdf`
- `CrowdGym A Crowd Simulation Environment for Reinforcement Learning.pdf`
  — the senior's prior FYP (Goh Chen Wei, NTU AY2025/26), the baseline this project improves on.

Check `integration/crowdgym_mapping.md` and `dataset/schema/README.md` first, they already distil the parts of the CrowdGym report that matter here (AgentType params, `RL_take_action`, journeys, RiMEA test scenarios). Only ask the user for the PDF's current path if you need something beyond what's already distilled there; don't assume a relative path to it still resolves after the move.

## Background — continuation of a senior's project
This FYP continues a senior's prior FYP, **CrowdGym** (see above). Treat their existing method as the baseline to improve on, not something to redo from scratch.

Goal: improve on the senior's method and ultimately reach a crowd simulation capable of handling **10,000 agents** without becoming too slow.

## Current task (from second supervisor meeting — supersedes Phase 1 below)
Supervisor's explicit instruction: **review literature before any further experimentation.** No new dataset generation, no simulation/experiment code, until the literature review is complete and discussed.

Direction:
- Have 2+ LLM agents communicate to resolve a conflict (start small — e.g. 2 agents in a narrow hallway crossing from opposite directions — before attempting the general case).
- Look for a **reusable pattern** in how the conflict resolves, so it can be applied to future conflicting scenarios without re-running the full LLM-to-LLM exchange.
- Validate the pattern against real human behavioural data if available, or against sociological research on real human conflict resolution otherwise.
- Supervisor-provided starting papers:
  - Wang, Zhang, Shi, Yang & Hu, "Modeling and simulating for congestion pedestrian evacuation with panic," *Physica A*, 2015.
  - Wu, Peng, Zheng, Liu, Han, Kwon, Onizuka, Tang & Xiao, "Shall We Team Up: Exploring Spontaneous Cooperation of Competing LLM Agents," EMNLP Findings 2024 (aclanthology.org/2024.findings-emnlp.297) — one of its three case studies is LLM agents negotiating room exits during an emergency evacuation; primary anchor for the conflict-resolution search.
- Literature review tracked via two GitHub issues (find 5 papers on why LLM-generated behaviour data is valid, superseded in priority by: find 10+ papers on LLM-to-LLM conflict resolution + sociological grounding). **Deliverable path for the new review:** `literature/llm-conflict-resolution/` (not `/CrowdSimulation/literature/...` — that prefix is stale, see Repo layout note above; fix this path in the GitHub issue itself if it still shows the old prefix).

## Phase 1 — dataset generation (superseded, on hold, not deleted)
Original task from the **first** supervisor meeting: generate a dataset of typical human behaviours under different scenarios by prompting an LLM, to test whether LLMs understand human behaviour well enough to act as simulation agents. Superseded by the direction above, but the artifacts below are kept, they may be useful for later comparison/validation or if the supervisor revisits this approach.

- LLM used: **DeepSeek API** (~$2 credit budget; spend tracked in `pipeline/config.py` -> `ALREADY_SPENT_USD`).
- Dataset covers everyday scenarios (crossing a road, taking a lift, queuing, ...) and conflict-causing ones (bottlenecks, crossflow, doorway deadlocks, ...) — see `dataset/scenarios.yaml`.
- Scope confirmed 2026-09-04: dataset is Singapore-only, organised by age group and gender (`dataset/personas.yaml`). Design decisions (DD1-DD4, e.g. generating per persona rather than per persona-pair) are recorded in `README.md` with supervisor sign-off.
- `run01` complete: 420 API calls, 140 aggregated records, actual cost $0.097. Automated validation passes format/coverage; a systematic "female personas yield more than male" pattern was flagged for supervisor discussion — see `dataset/generated/validation_report.md`. **This flag is still unresolved** and may be relevant background if a similar bias question comes up in the new LLM-to-LLM approach.

## Roadmap
See `README.md` for the live status of each step.

1. **Literature review (current focus)** — `literature/llm-conflict-resolution/`. No experimentation until this is done.
2. Design a small-scale conflict scenario (e.g. 2-agent narrow hallway).
3. Implement the LLM-to-LLM communication exchange for that scenario.
4. Analyze exchanges for a reusable resolution pattern.
5. Validate the pattern against real data or sociological literature.
6. Bridge the validated pattern into CrowdGym — `integration/crowdgym_mapping.md`.
7. Iterate with supervisor feedback before the next meeting.

(Phase 1 steps — schema/pipeline/generate/validate under `dataset/` and `pipeline/` — are on hold; see "Phase 1" section above.)

## Notes for Claude Code
- When asked to work on a GitHub issue, follow `github_issue_workflow.md`.
- **Do not resume Phase 1 dataset-generation work or write new simulation/experiment code** until the literature review above is marked complete, this is a standing supervisor instruction, not just a suggestion, so don't proceed past it even if asked to "just get started" without an explicit note that the review is done.
- Check `integration/crowdgym_mapping.md` and `dataset/schema/README.md` before proposing anything that touches CrowdGym — go back to the original PDF (outside this repo) only for details not already covered there.
- Flag clearly when something is a design decision vs. an assumption you're making, since supervisor sign-off matters for this project.
- When helping with dataset or pattern validation, prioritize methods that are explainable and defensible in a report, not just automated metrics.
- `.env` holds the DeepSeek API key. Never print it, commit it, or include it in any output — `.gitignore` already excludes `.env` from version control.