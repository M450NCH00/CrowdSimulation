# Work Log — Issue #131: RF-42: record the supervisor meeting of November 2026, and fix the shared design of the action-space experiments (RF-43 to RF-52)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/131
**Branch:** docs/131-rf42-meeting-action-space (cut from `feat/129-rf40-turn-taking-talk`, the latest RF work; local, 6 commits ahead of origin)
**Started:** 2026-11-25 04:22 UTC

## Understanding the issue
At the supervisor meeting after RF-40 (November 2026; slides `presentations/2026-11_supervisor_meeting_round1.pptx`, untracked), the supervisor made eight suggestions about how the agents are asked to act. They cover a grid, left and right, an absolute frame, words instead of numbers, a menu, hallucination, persona speech, and a page on game agents. Issues RF-43 to RF-52 (#132 to #141) act on them. This issue:
1. records the meeting word for word, in `CLAUDE.md`, `README.md` and the decision record (architecture section 8.7), as RF-1 (#56) did for 2026-10-20;
2. writes `llm_negotiation/docs/action-space.md`: the variants, what they share, and every choice the later issues need, each with a recommendation;
3. asks the user each choice and records the answers with the date; updates later issues where an answer changes them;
4. updates #55 if the order changes.

Documents only: no code, template or model call.

Already decided by the user (2026-11-25, before this branch): **the grid is an add-on** that does not modify the current environment's code. It lives in new files with its own entry point; if an existing file would have to change, the user is asked first. Recorded in #139 to #141, #131 and #55.

Assumptions:
- The meeting date is not in the repo. The slides file is dated 2026-11-03 14:23 local time; the last meeting (2026-10-20) was a Tuesday, so 2026-11-03 is a Tuesday two weeks later. To ask the user, not assumed.
- The points are phrased "can ...": recorded as the supervisor's suggestions, not decisions, unless the user says otherwise.

## Plan
1. Gather sourced numbers for the recommendations: the repo's own sourced values (body size, walking speed, RF-37's targets), and the cell size of grid pedestrian models (Burstedde et al. 2001; checked, not quoted from memory).
2. Draft `docs/action-space.md` with every choice marked "proposed".
3. Ask the user (several rounds of questions, each with a recommendation).
4. Record the answers in `docs/action-space.md`; the meeting in `CLAUDE.md`, `README.md`, architecture section 8.7; update #55 and the later issues where an answer changes them.
5. Check the docs against the sources (workflow 5b), push, open the PR.

## Progress log

### 2026-11-25 04:22 UTC — Branch and work log
- What I did: cut the branch from `feat/129-rf40-turn-taking-talk` (the repo's practice: RF branches stack on the previous one; never `git checkout main`).
- Note: `presentations/` is untracked and unrelated to this issue; left alone, not committed.
- Next step: gather the sourced numbers.

### 2026-11-25 04:25 UTC — Sourced numbers for the recommendations
- **The repo's own sourced values:**
  - body radius 0.25 m (effective shoulder width 49.8 cm, Yamamoto et al. 2019), preferred speed 1.3 m/s and corridor width 1.75 m (Moussaïd et al. 2009), backing speed 0.92 m/s (Nakahara et al. 2005): all in `docs/parameters.md`;
  - H1, 0.93 ± 0.17 m between centres (Rapos et al. 2021, abstract), in `configs/human_targets/head_on_v1.yaml`;
  - Huber et al. 2014's instructed speeds (slow 1.15, normal 1.42 m/s), checked in `refs/rf14_huber2014_speed_path.txt:452`.
- **The grid model:** Burstedde et al. 2001. A web search confirmed the paper and its 40 × 40 cm cell, but not the time step. I downloaded the open-access arXiv version (cond-mat/0102397) to `refs/rf42_burstedde2001_ca_arxiv.pdf` and extracted the text with pypdf 5.1.0 (`python -I`). Read in the text:
  - the cell: "approximately 40 × 40 cm²", "the typical space occupied by a pedestrian in a dense crowd" (lines 132-135);
  - the time step: "approximately 0.3 sec", from 1.3 m/s (lines 142-146);
  - clashes: "If the target cell is occupied, the particle does not move", and of several aiming at one cell one moves while "its rivals for the same target keep their position" (lines 168-174); the simpler variant picks at random with probability 1/m (line 324).
- **Round 1's geometries** (`configs/cases/source_head_on.yaml`): walking lines aligned, and 20 cm apart (±0.1 m). On a 0.4 m grid both round to the centre lane, so the grid's second geometry is proposed as one lane apart (0.4 m, as `apart_40cm`).

### 2026-11-25, between 04:25 and 05:29 UTC — The user's answers (two rounds of questions)
Asked with a recommendation each; the user's answers, recorded as AS1 to AS9 in `llm_negotiation/docs/action-space.md`:
- **Meeting date:** "Just 'November 2026'". The exact date is not recorded.
- **AS2, conditions:** RF-49 runs silent and talk; RF-52 silent only (recommended).
- **AS6 and AS7, the grid:** 0.4 m cells, 5 lanes (recommended). The clash rule was stated in every option.
- **AS5, the absolute frame:** compass walls, heading not told, rechecked after RF-43 (recommended).
- **AS3, the menu's amounts:** accepted as proposed (recommended).
- **AS4, menu code:** extend the existing code behind a flag (recommended). The grid stays strictly add-on (AS1, decided before this branch).
- **AS8, RF-41:** after RF-45, as planned (recommended).
- **AS9, the order:** as proposed (recommended).
- **Not asked (the assistant's choice, marked as such in the doc):** the template names, and the proposals left for RF-50 and RF-51 (the moves, slower walkers, the geometries, the grid's measures).

### 2026-11-25 05:29 UTC — Written up, and the issues updated
- **New:** `llm_negotiation/docs/action-space.md`.
- **Edited:**
  - `CLAUDE.md`: the meeting word for word under "Supervisor decisions", and AS1 as a constraint for every RF issue;
  - `llm_negotiation/docs/architecture.md`: section 8.8, SV7 to SV14 and a pointer to AS1 to AS9;
  - `README.md`: current focus, and roadmap rows RF-40 to RF-52 (RF-40 and RF-41 had no rows);
  - `llm_negotiation/README.md`: the RF order list.
- **Correction before commit:** the first draft called the template names and the clash rule the user's decisions. Corrected: the template names are the assistant's (not asked); the clash rule was part of every option of the grid question.
- **Issues:**
  - a dated "Decided in RF-42" note at the top of #130, #135, #136, #137, #138, #139, #140 and #141 (old bodies backed up in the session's scratchpad);
  - #55: the order confirmed (RF-41 after RF-45), the decisions, and the meeting's date not recorded.
- **Tests:** the 8 test files that read `CLAUDE.md`, `README.md` or `architecture.md` (outside repo hygiene and avoidance runs) gave 301 passed, 12 skipped. Repo hygiene and avoidance runs are running in the background (about 25 minutes).

## Open questions / risks
- ~~The meeting's date~~: the user chose "November 2026", with no exact date.
- Pushing this branch needs `feat/129-rf40-turn-taking-talk` pushed first (it is 6 commits ahead of origin), or the PR will carry RF-40's commits.
- **AS5 is provisional.** RF-48 must not be built until the user has rechecked it against RF-43.
- **The placeholders** (slow down a lot × 0.5, stop and wait 1 s, step back 0.5 m, the 30° sidestep angle, the grid's N ticks for a deadlock) are for the supervisor.
- **"Slow down a little" (× 0.81)** is a ratio of instructed walking speeds (Huber et al. 2014), not a measured slowing in an encounter.
- **H1** comes from Rapos et al. 2021's abstract only (RF-37 read the abstract).
- **The grid corridor is 2.0 m wide, against round 1's 1.75 m.** Its passing distances come in 0.4 m steps, and adjacent lanes (0.4 m) are closer than two bodies (0.5 m). Grid results compare with the continuous runs by rates only.
- **How a grid result reaches the continuous 10,000-agent simulation** is open (RF-52, task 3).

## Summary
- **What changed:**
  - the supervisor meeting of November 2026 is recorded word for word in `CLAUDE.md`, numbered SV7 to SV14 in architecture section 8.8, and shown in both READMEs;
  - the user's nine decisions on how to act on it (AS1 to AS9) are in `llm_negotiation/docs/action-space.md`: the variants, the baseline (RF-40's silent condition), the measures, the conditions, the menu and its amounts, the absolute frame, the grid (an add-on; 0.4 m cells, 5 lanes, Burstedde et al.'s clash rule), RF-41's place, and the order of work.
- **Why:** RF-43 to RF-52 share these choices. Fixing them once keeps each later issue small.
- **How it was verified:**
  - every number in `action-space.md` was checked against its source file and line (section 12);
  - the decisions were checked against the user's answers;
  - the test files that read the edited documents pass (see the progress log).
- No code, template or model call; USD 0.
