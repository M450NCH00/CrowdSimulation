# Work Log — Issue #69: RF-14: Step 3, verify extracted rules, debrief sources and factor effects against human evidence

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/69
**Branch:** docs/69-rf14-verify-rules-human-evidence (from `feat/110-rf32-group-head-on` at `6d1c3f4`,
after PRs #120 and #118 were merged into it on 2026-10-30; `main` is not used in this track)
**Started:** 2026-10-30, 00:19 UTC

## Understanding the issue

Step 3 of track #55 for round 1 (head-on): check the rules extracted in RF-11 (#66), the references
the extractor gave, the sources the agents named in their debriefs, and the factor effects of RF-10's
screen (#65) against human evidence. Grade each rule and effect, write the evidence down, and promote
only rules that both match human evidence and help in the simulation (RF-18, #74, and RF-33, #112).
No model call, no code apart from promotion.

**Prerequisite (#55, decision 6), answered.** The user said on 2026-10-30, at the start of this
issue: "RF-14's scope: what counts as 'real human behaviour', published studies only is what I
decided." So **published studies only**, the user's own decision (recorded in `CLAUDE.md`, pending
sign-offs item 6, like items 4, 7 and 8). Task 8 (a plan for observed data) is therefore not done.

**What there is to verify (inventory, 00:20 to 00:35 UTC):**

- **Rules.** RF-11 wrote 25 rules over three runs; four were kept (found in at least 2 of 3 runs):
  - `x_head_on_aacce0961b`: a person who holds their ground keeps their line at full speed and only
    steps aside or slows at close range (held out 0.83 against 0.75).
  - `x_head_on_6455ca5589`: a person who gives way slows when the other is elderly, has a cane,
    pulls a suitcase or looks at a phone (0.71 against 0.75: below its baseline).
  - `x_head_on_0ecc2d1a6e`: people almost never stop or back up (1.00 = baseline). Its format 4
    translation (RF-31) is a different rule: both turn 10° to their left from 9.8 m.
  - `x_head_on_4eb7a97c8d`: people signal in the non-verbal and talk conditions (needs communication).
  - Not kept, but in every run's words: keep to your own right (RF-11, section 4). The agents passed
    right to right in 47 of 76 resolved sessions.
- **Simulation verdicts** (RF-18; verdict of record from RF-33's realistic crowd): the left-turn
  translation of `0ecc2d1a6e` **helps**; the cane translation of `6455ca5589` **harms** (gridlock on 1
  seed of 30); `aacce0961b`'s translation never matches and is now refused by the loader; `4eb7a97c8d`
  was not expressible. So only one rule can be promoted at all: the left-turn translation, and only if
  human evidence supports it.
- **Extractor references: 27** over the 25 rules (23 in readable rules, 4 inside the raw text of the
  schema-error rules). **24 say "no known source"**; **3 cite "as reported by participants"** (a
  Singapore keep-left convention, courtesy to elders, keep-side custom). None names a law, guidance
  or a study. Nothing to look up as a publication; the three are claims about people and are checked
  as claims.
- **Debrief sources: none.** 2,681 debriefs over the 14 paid runs (round 1 head-on and RF-32 to RF-36):
  the `source` field is null in every one, and no debrief has kind `law_or_guidance` or
  `published_study`. Kinds: common sense, habit, local custom, none. The `local_custom` debriefs (141)
  make three checkable claims: (a) Singaporeans keep left on walkways, (b) giving way to seniors is a
  Singapore courtesy, (c) keeping right is a widespread informal convention.
- **Factor effects** (RF-10, Holm-significant): own assertiveness makes a first plan slow less (OR
  0.26); knowing the other makes a person signal (OR 221); finding the other attractive makes a
  person signal (OR 5.29). Phase B shortlist, uncorrected: residence in the United States makes a plan
  turn right (OR 2.37); the other being 70 makes a person slow (OR 3.44). Ethnicity: nothing beyond the
  noise floor. Attractiveness and ethnicity are reported as the model's bias whatever the evidence
  says, never as a rule.

## Plan

1. Record the user's decision on #55 decision 6 (`CLAUDE.md`, `README.md`, `docs/architecture.md`, #55).
2. Task 1: one check record per extractor reference (27).
3. Task 2: debrief sources: the counts above, and the three `local_custom` claims checked like
   references.
4. Task 3: independent search per rule and per claim, for and against, starting from the
   repository's literature folders; cache every source read in `refs/` (`rf14_*`).
5. Task 4: grade every rule and effect: Supported, Partly supported, No evidence, Contradicted. Compare
   numbers where a study gives them (side shares, passing distances, who adjusts).
6. Task 5: one evidence file per rule.
7. Task 6: promote only rules graded Supported or Partly supported that RF-18 found to help.
8. Task 7: summary table.
9. Section 5b checks; PR stacked on `feat/110-rf32-group-head-on`.

## Progress log

### 2026-10-30 00:19 UTC — PRs merged, branch cut
- What I did: at the user's request, merged PR #120 (RF-36) into `feat/117-...`, then PR #118 (RF-35)
  into `feat/110-...` (00:17 UTC), so `feat/110-...` carries both. Closed #117 and #119 by hand with a
  note (stacked merges do not fire `Closes`), ticked both in #55 with their results, and moved #55's
  decision 6 to "decided by the user, 2026-10-30: published studies only". Cut this branch from
  `origin/feat/110-rf32-group-head-on`.
- Next step: inventory.

### 2026-10-30 00:35 UTC — Inventory done, decision 6 recorded
- What I did: read RF-11's extraction report and run files, RF-31's translation report, RF-33's
  evaluation report, RF-10's screen report; counted every debrief of every paid run.
- Result: see "Understanding the issue". The main surprise: neither the extractor nor any agent names
  a checkable source, so tasks 1 and 2 reduce to checking claims, and the weight of the issue is in
  task 3's independent search.
- Next step: independent search.

## Open questions / risks

- Only one rule (the left-turn translation) can be promoted, by the decision table of #55.

## Summary (fill in at the end)
