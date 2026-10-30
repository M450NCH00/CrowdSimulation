# Work Log — Issue #122: RF-37: human targets: measurable targets from published studies; rules, plain ORCA and Step 1's agents measured against them

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/122
**Branch:** feat/122-rf37-human-targets (from `feat/110-rf32-group-head-on` at `e2538f0`, after PR #121
(RF-14) was merged into it on 2026-10-30; `main` is not used in this track)
**Started:** 2026-10-30, 11:36 UTC

## Understanding the issue

The user's goal, stated on 2026-10-30 while RF-14's PR was open: **resolve conflicts in a way accurate
to human behaviour**, in crowds of 10,000 agents or more. Nothing measures that today:

- RF-18's "helps" measures the crowd's efficiency (severe conflicts, throughput, delay, gridlock);
- RF-31's identity check measures agreement with the LLM agents, who are not the reference;
- RF-14 grades rules in words, without the studies' numbers;
- lane formation is reported, not judged.

This issue turns RF-14's cached evidence into **measurable targets with sources and tolerances**, adds
the measures, and judges each rule arm, plain ORCA and Step 1's own agents against the targets.
No model call. Under #55 decision 6 (published studies only), targets come from numbers reported in
published studies, not from trajectory datasets.

**Order fixed by the issue:** the tolerances are agreed with the user (task 0) **before any rule is
measured**, as RF-18's "helps" was before its run.

## Plan

1. Task 0: ask the user for the tolerance rule; record the answer here word for word.
2. Inventory what the code already measures (`docs/metrics.md`, `negsim/ruleset_eval/measures.py`,
   the identity check of RF-31, `negsim/resolution/groups.py`), so new measures reuse what exists.
3. Task 1: fill the source gaps (C3 speed against density; S2 Figure 4 shares; Rapos2021's distance
   definition; Knorr2016's traits), caching each in `refs/` (`rf37_*`).
4. Task 2: frozen targets file `llm_negotiation/configs/human_targets/head_on_v1.yaml` and its loader,
   with tests (every value names its source; frozen by hash, as templates are).
5. Task 3: the measures, tested on hand-built trajectories with known answers.
6. Task 4: study-matched scenarios as variants of existing layouts; earlier configs unchanged.
7. Task 5: the report (each arm, plain ORCA and Step 1's agents against each target; the side both
   ways for Singapore).
8. Task 6: run on round 1 (`rf18_round1_realistic`'s rules, RF-10 under `keep_line` and RF-30).
9. Task 7: a proposal for #55's promotion table, for the user.
10. Task 8: docs and READMEs; section 5b checks; full test suite; PR stacked on
    `feat/110-rf32-group-head-on`.

## Progress log

### 2026-10-30 11:36 UTC — PR #121 merged, #69 closed, branch cut
- What I did: at the user's request, merged PR #121 (RF-14) into `feat/110-...` (11:35 UTC), closed #69
  by hand with a note (a stacked merge does not fire `Closes`), ticked it in #55 with its result, and cut
  this branch from `origin/feat/110-rf32-group-head-on`.
- Next step: task 0 (the tolerances), then the inventory.

## Open questions / risks

1. **Tolerances** (task 0): not yet agreed.
2. **Study settings differ from the simulator's**: lab tasks with instructed walkers, one walker going
   straight in Huber2014, young adults in France, Germany, Canada and China; none in Singapore. Every
   comparison whose setting cannot be matched is labelled `[setting differs]`.

## Summary (fill in at the end)
