# Work Log — Issue #119: RF-36: crowd encounters, non-verbal: do LLM agents resolve a conflict inside a crowd when they can see each other move and signal?

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/119
**Branch:** feat/119-rf36-crowd-encounters-non-verbal (from `feat/117-rf35-crowd-encounters`, PR #118 open,
commit `a59eeab`; `main` is not used in this track)
**Started:** 2026-10-29, 01:23 UTC

## Understanding the issue

RF-35 (#117) sampled encounters from RF-18's two-way flow and ran them in the independent condition:
against plain ORCA on the same seed, 14 of 64 design sessions resolved (0.22), worse in 50, better in 6;
the plans added collisions in 30 sessions and removed them in 2, the deep ones between the encounter's
own people walking towards each other. In the independent condition each person plans once, alone, and
never sees what the others then do. **The user decided on 2026-10-29**, after RF-35 (its open question
2), to run the same encounters in the non-verbal condition, as RF-34 did for RF-32's groups.

Question: with signals and movement, up to three decision points each (D3, D5), do crowd encounters
resolve more often than in RF-35, and do the plans still add collisions against plain ORCA?

**Paid.** The build is mock only; the paid run needs its own approval and cap in `CLAUDE.md` (pending
item 1). Balance USD 0.32 (after #117, 2026-10-28).

## Plan

1. Config `configs/resolution/rf36_crowd_encounters_non_verbal.yaml`: RF-35's config with
   `conditions: [non_verbal]`; everything else the same except the name, description and the cap,
   which is `0.0` until the user approves one.
2. Mock rehearsal of the 72 sessions; check that later decision points fire in a crowd, and why.
3. `--plan` and an estimate from RF-35's cost per call and RF-34's ratio of non-verbal to
   independent calls.
4. The analysis: `--against` paired with RF-35 by the measure against plain ORCA (the pair measure is
   0 for everyone in a crowd), and the two conditions' contacts compared directly per session (the same
   case and cell give the same bystanders and the same crowd). Tests on the mock.
5. Ask the user to approve the paid run and its cap.
6. Paid run: pilot with `--limit`, read, then the rest; analysis and `crowd_report.md`.

## Progress log

### 2026-10-29 01:23 UTC — issue, branch
- What I did: opened #119; #55 lists it after #117 as next. Branched from #117's branch.
- Found while reading: `groups --against` pairs sessions by `resolved.plan_only`, the scenario's own
  measure, which no session meets in a crowd (RF-35: 0 of 64, plain ORCA too). It needs the measure
  against plain ORCA as well.
- Next step: the config and the mock rehearsal.

## Open questions / risks

## Summary (fill in at the end)
