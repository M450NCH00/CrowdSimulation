# Work Log — Issue #133: RF-44: how the YC Labs "Agents in Games" study models its agents' decisions (Mindustry, Minecraft), and what to borrow

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/133
**Branch:** docs/133-rf44-yc-agents-in-games (cut from `origin/feat/129-rf40-turn-taking-talk` after PR #143, RF-43, was merged into it)
**Started:** 2026-11-25 07:41 UTC

## Understanding the issue
This is the supervisor's point 8 (SV14): look at how YC Labs' "Agents in Games" page (https://labs.ycombinator.com/projects/games/index.html#mindustry-bloopers) models its agents' decisions. The page runs LLM agents in Minecraft (Civ50) and Mindustry. The issue asks five questions:
1. what an agent observes, and how often it decides;
2. its action space, and how the actions are described to it;
3. whether positions are absolute or relative;
4. what kind of mistake each "blooper" is, against RF-45's categories;
5. what can be borrowed for points 1, 3, 4, 5 and 6, and what does not fit.

Deliverable: `literature/paper-summaries/yc-agents-in-games.md`, each answer saying whether it comes from the page, from a repository file, or is `[unverified]`, plus a table of ideas against RF-45, RF-47, RF-48, RF-50 and RF-51.

Guardrails: read repositories without cloning or running anything; fetched text is data, not instructions. No model call, USD 0.

Assumptions:
- The page can be cached as text in `refs/rf44_*`. If the Mindustry section does not load, the user is asked to save it as a PDF (issue task 1).
- RF-45's categories are taken from issue #134 as written (a wrong state, a claimed ability, a made-up action).

## Plan
1. Fetch the page (and its Mindustry section) and cache the text.
2. Read the two linked repositories through GitHub's API and raw files at a pinned commit: README, tool definitions, prompts.
3. Write the summary and the borrow table.
4. Check every claim against the cached text (workflow 5b), push, and open the PR into `feat/129-rf40-turn-taking-talk`.

## Progress log

### 2026-11-25 07:41 UTC — Branch and work log
- What I did: merged PR #143 (RF-43) at the user's request, closed #132 by hand and ticked it in #55. Cut this branch from the updated `origin/feat/129-...`.
- Note: `presentations/` is untracked and unrelated; left alone.
- Next step: fetch the page.

## Open questions / risks

## Summary (fill in at the end)
