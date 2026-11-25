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

### 2026-11-25 07:49 UTC — Fetch, read, write
- What I did:
  - Fetched the page with curl. It came gzip-compressed, about 170 KB of HTML. I turned it into text with a standard-library HTML parser (a script kept in the scratchpad, run with `python -I`, outside the download folder). **The whole page loaded, including the Mindustry section and the bloopers**, so the user does not need to save a PDF (issue task 1).
  - Read the two repositories through `gh api` (metadata and file trees) and `raw.githubusercontent.com` at pinned commits. Nothing was cloned, installed or run.
    - `yc-software/minecraft-agent-harness`, MIT, `775d558`: README, `docs/tools.md`, `docs/architecture.md`, `docs/multi-agent.md`, `src/prompt.js`, `src/skills/perception.js`, `src/tools/game/observation.js`, `src/tools/game/failures.js`.
    - `olamlabs/multi-agent-mindustry`, GPL-3.0, `1374e46`: root README, `mindustry-series/README.md`, `instruction.md`, `instructions/seat-1.md`, `environment/sim/instruction.md`, `environment/sim/tools.mjs`.
  - Wrote `literature/paper-summaries/yc-agents-in-games.md`.
- Search terms: none needed. The issue gave the URL, and the page links both repositories.
- Fetched text: treated as data. One passage addresses agents ("give the link to your agent with 'help me understand and set this up'", page line 1187). It is the authors' advice to readers, not an instruction to me, and I did not act on it.
- Found:
  - **The Mindustry series was 50 against 50, not "teams of 10"** as the issue says (`mindustry-series/README.md:276`). Recorded as a correction in the summary.
  - **Both interfaces use absolute coordinates.** Mindustry uses compass axes on a tile grid ("x east and y north"). Directional left and right appear nowhere in the tools, the observation or the instructions.
  - **The bloopers are wrong beliefs about state or ability, not spatial errors.** Three of them are false claims about what an action or unit can do, which RF-45's draft categories do not cover. Suggested a category "misstated the setting" for RF-45.
- 5b check: re-read each citation against the cached files. Two corrections: the chicken protocol is at page line 982, not 951; the tool reference ends at line 117. Extended the excerpts to cover `attack` (tools line 56) and the protocol.
- Caching: as in RF-43, the full copies are local only (`.gitignore`, `rf44` block). `refs/rf44_excerpts.txt` is tracked and holds every cited passage.
- Next step: commit, push, open the PR.

## Open questions / risks
1. **The source is a blog-style write-up**: no rates, no repeats, no tests. The bloopers are hand-picked anecdotes, so nothing here is evidence of how often game agents err.
2. **The Mindustry instructions read are the repository's current version** (pushed 2026-11-19), possibly newer than the series on the page (October 2026). The correction about Gamma's zero building damage may have been added after the games.
3. **The agents' own prompt text in Civ50 and Bed Wars** (soul or personality, objective wording beyond the quoted goals) is not published on the page. Only the prompt builder's structure was read.
4. **The page's model names** (GPT-6.1 Sol, Claude Opus 5.5) differ from the repositories' defaults (GPT-6.1 Terra, `gpt-6-luna`). The exact settings of each run are not given beyond the harness and model.
5. **"Misstated the setting" as a new RF-45 category** is my suggestion; RF-45 agrees its definition with the user before counting.
6. **The borrow table's "fits"** are my judgements, against the issues as written. They are not tested.

## Summary (fill in at the end)
**What changed**
- `literature/paper-summaries/yc-agents-in-games.md`: answers to the issue's questions 1 to 5, each with its source line, and the borrow table naming the issue that would use each idea.
- `refs/rf44_excerpts.txt`: every cited passage.
- `.gitignore`: the `rf44` block; full copies stay local.

**Findings in short**
- **How the decisions are modelled:**
  - the agents act through a fixed menu of named, high-level tools (Minecraft, 51 of them) or a small API (Mindustry), and each tool is described in plain words of its physical effect;
  - the agent names a target in absolute coordinates, and a pathfinder moves the body, so there are no angles and no left or right;
  - failures come back with a code and a hint for the next call;
  - decisions are event-driven (wake on messages or damage), with no pause.
- **What fits this project:**
  - the menu and target style, for RF-47 and RF-50/51;
  - absolute compass axes on a tile grid, for RF-48 and RF-50/51;
  - grounding lines ("Never claim a tool action succeeded unless its result supports that") and correcting a known false belief in the instructions, for RF-45 and later templates;
  - recording private reasoning, for RF-53.
- **What does not fit:** memory files, code and scripts, a 360° view, and no pause for talk.

**How it was verified:** workflow 5b. Every answer names its source line, or is marked `[inference]`. Two line numbers were corrected. The open questions are listed. No code changed, so no tests were needed.
