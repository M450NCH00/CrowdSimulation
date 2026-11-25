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

### 2026-11-25 06:33 UTC — Search, fetch and read
- What I did: ran the searches below; downloaded 13 sources into `refs/rf43_*` and extracted their text with pypdf 5.1.0; read the parts that give numbers. Rendered Cohn & Blackwell's Figure 1 (pymupdf 1.25.1) because the extract separates the bar labels from their values: DeepSeek-reasoner 0.84, DeepSeek-chat 0.48 (3rd and 14th bars from the top; matches the text's "striking how much better Deepseek-reasoner is").
- Not reached (all bot checks or 403s, tried directly and through the web-fetch agent): Majid et al. 2004 (MPG repository: Anubis; Oxford, ScienceDirect: 403; PubMed: cookie wall), Schober 1993 (ScienceDirect 403, PubMed cookie wall), two CogSci papers on eScholarship (HTML instead of PDF). OpenAlex answered 429 (rate limit); Crossref has no abstract for these. They are cited only through cached secondary sources (COMFORT for Levinson 2003 and Majid et al. 2004; Tversky & Hard for Schober), marked so.
- Dropped after a look: Constant & Mellet 2018 (Frontiers; women's error rate on the Bergen test, nothing on front against back view beyond Gormley et al.); the 8.4% "objective" left-right confusion figure from a Psychology Today summary (not in van der Ham et al. 2021 itself).
- Caching: following RF-16 and RF-17, full copies with no open licence confirmed are local only (gitignored, `.gitignore` gains an `rf43` block); `refs/rf43_excerpts.txt` is tracked and holds every cited passage with its line number in the full extract. Van der Ham et al. 2021 is CC BY 4.0 and tracked in full.
- Result: LLM side has five text-only or text-relevant studies with numbers (SpatialText, FoREST, GSU, Cohn & Blackwell, VoT) plus one image study (Leonard et al.); human side has Tversky & Hard, van der Ham et al., Gormley et al.; Siebinga's model of the pavement dance. Nothing found on what pedestrians or cyclists say to someone coming the other way.
- Next step: write `literature/frames-of-reference/README.md`.

## Search terms
Web search (standard unless marked):
1. LLM spatial perspective-taking benchmark frame of reference left right another person's viewpoint → FoREST, ViewSpatial-Bench (VLM)
2. "frames of reference" large language models spatial reasoning intrinsic relative absolute evaluation arXiv → FoREST, COMFORT, 2605.28277 (not read), survey 2511.15722 (not read)
3. left-right confusion prevalence healthy adults percentage study → van der Ham et al. 2021
4. "on your left" cyclist passing pedestrian call frame of reference convention → forums and opinion pieces only; no study
5. (extended) text-only LLM "perspective taking" spatial left right facing each other benchmark GPT-4 error rate egocentric allocentric → SpatialText
6. Ratcliff 1979 manikin test left right judgement figure facing towards away rotation errors → no usable source
7. Majid Bowerman Kita Haun Levinson 2004 "Can language restructure cognition? The case for space" … → record only; copy blocked
8. reasoning models o1 DeepSeek-R1 spatial reasoning benchmark perspective orientation improvement thinking mode → no direct comparison; led to 9
9. Sidhu Hockenmaier 2026 frame of reference LLM spatial language → GSU (the lead left open in #52's search log, S12)
10. Schober 1993 "Spatial perspective-taking in conversation" … → record only; copy blocked
11. Tversky Hard 2009 "Embodied and disembodied cognition: Spatial perspective-taking" … → author copy
12. LLM cardinal directions qualitative spatial reasoning benchmark "absolute" vs "relative" directions accuracy navigation instructions → Cohn & Blackwell 2025
13. Bergen Left-Right Discrimination Test front view back view figures error rates Ofte Hugdahl → Gormley et al. 2008, Constant & Mellet 2018
14. van der Ham 2021 "left-right confusion" QJEP open access pdf → Leiden repository copy
15. pedestrians verbal communication passing head-on study "excuse me" sidestep coordination conversation analysis → Siebinga 2024; no study of speech
16. LLM text "facing each other" "your left" "my right" perspective taking test language model mistakes speaker listener left right → Leonard et al. 2024
Also reused: `literature/environment-description/` (#52) for Martorell's grid encodings and Chen's MAPF.

## Open questions / risks

## Summary (fill in at the end)
