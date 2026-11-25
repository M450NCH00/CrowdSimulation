# Work Log — Issue #132: RF-43: literature: whose left and right? Frames of reference in LLMs and in people, and what fixes the confusion

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/132
**Branch:** docs/132-rf43-frames-of-reference (cut from `origin/feat/129-rf40-turn-taking-talk`, which carries RF-42's merged PR #142)
**Started:** 2026-11-25 06:21 UTC

## Understanding the issue
The supervisor's point 2 (SV8, meeting of November 2026): DeepSeek mistakes the other person's left and right for its own, even when told they face each other. RF-40 (#129) measured it (`llm_negotiation/runs/rf40_round1_head_on_turn_taking/comparison_report.md`, "In short" and section 5):
- own-frame words ("I'll keep to my left") matched the speaker's own move in 44 of 46;
- listener-frame words ("coming through on your right") matched in 11 of 27;
- of 100 heard side messages where both moved aside, the listener made room in 35 (p = 0.004 against a coin);
- 44 listener replies restated the side in the other's frame; 18 fitted. `resolve_v9`'s facing note ("Person N is facing you: their left is your right, and their right is your left", `negsim/negotiation/templates/resolve_v9.yaml:216`) was sometimes applied to words already in the listener's frame.

This issue is a literature review, before the fixes are built (RF-47 words, RF-48 absolute frame, RF-50/51 grid). It answers four questions: (1) is frame conversion a known LLM weakness, with error rates and what they depend on; (2) which fixes were measured for LLMs and by how much; (3) frames of reference and left-right confusion in people, which frame pedestrians and cyclists use with someone coming the other way, absolute-direction cultures; (4) for this project, which fix fits each RF-40 error, which representations RF-47, RF-48, RF-50/51 should test, and whether DeepSeek's thinking mode is worth a try. Plus a labelled recommendation for RF-42's AS5 (absolute-frame words; whether to tell the heading), and optionally ~20 static probe prompts (not run).

Out of scope: any model call, template or code. Paid: no.

Assumptions:
- "Cache sources in `refs/`" follows the repo's practice: `refs/rf43_*` files, with the text extracted where a PDF is cached.
- Where a paper cannot be fetched (paywall or bot block), it is cited from its abstract only and marked so, or `[unverified]`.

## Plan
1. Search (terms kept below): LLM spatial perspective-taking and frame-of-reference benchmarks; egocentric vs allocentric descriptions; fixes (absolute directions, grids, chain-of-thought, worked examples, code); people's frames (Levinson 2003, left-right confusion rates, pedestrian/cyclist "on your left" conventions, absolute-direction cultures).
2. Fetch and cache the open-access sources in `refs/rf43_*`; read the parts that give numbers, and note the table or figure.
3. Write `literature/frames-of-reference/README.md`: a source table (what was tested, model, result, where), then answers to questions 1 to 4, each claim sourced or `[unverified]`; the AS5 recommendation; the optional probe prompts.
4. Check every number against its cached source (workflow 5b), then push and open the PR into `feat/129-rf40-turn-taking-talk`.

## Progress log

### 2026-11-25 06:21 UTC — Branch and work log
- What I did: cut the branch from `origin/feat/129-rf40-turn-taking-talk` (RF branches stack; never `git checkout main`); read RF-40's report (sections "In short", 5), `docs/action-space.md` (AS5, section 11) and `resolve_v9`'s facing note.
- Note: `presentations/` is untracked and unrelated; left alone.
- Next step: search.

## Search terms

## Open questions / risks

## Summary (fill in at the end)
