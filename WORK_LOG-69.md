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

**What there is to verify (inventory, 00:19 to 00:24 UTC):**

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

### 2026-10-30 00:24 UTC — Inventory done, decision 6 recorded
*(Time corrected at 00:30 UTC from the commit time: the entry first said 00:35, an estimate written
ahead of the clock.)*
- What I did: read RF-11's extraction report and run files, RF-31's translation report, RF-33's
  evaluation report, RF-10's screen report; counted every debrief of every paid run.
- Result: see "Understanding the issue". The main surprise: neither the extractor nor any agent names
  a checkable source, so tasks 1 and 2 reduce to checking claims, and the weight of the issue is in
  task 3's independent search.
- Next step: independent search.

### 2026-10-30 00:25 to 00:32 UTC — Searches and sources
- What I did: searched the repository's literature folders (only Rapos et al. 2021 was relevant), then
  12 web searches and Europe PMC's API (`literature/rule-verification/search-log.md`). Cached 18 files
  as `refs/rf14_*`.
- Result: the key studies are Moussaïd et al. 2009 (side convention, slowing in head-on), Olivier et al.
  2013 and Knorr et al. 2016 (roles in avoidance; personality not correlated), Huber et al. 2014 (head-on:
  path, not speed), Rapos et al. 2021 (young adults adjust more for older ones), Nummenmaa et al. 2009
  (gaze), Arminen & Heino 2023 (civil inattention), Valuch et al. 2015 (attractive faces hold gaze),
  Echeverría-Huarte et al. 2026 (Japan keeps left), Jung & Jung 2013 (Korea: guidance and preference
  diverge). **No published study of which side Singapore pedestrians keep**; only guidance (MOT 2024).
- Dead ends: HAL, mediaTUM and Turku returned Anubis bot checks; those pages were deleted and the
  abstracts taken from Europe PMC. Cary 1978 (civil inattention in passing) has no Europe PMC record.
  Wolff 1973 is a book chapter: citation only. A Vassallo et al. 2017 link was an HTML page, deleted.

### 2026-10-30 00:32 UTC — Promotion tried on a scratch copy: refused
- What I did: `python -m negsim.rulegen promote runs/rf31_round1_head_on/rule_db_staging/extracted
  ext_head_on_0ecc2d1a6e --reason "dry run" --database <scratch copy of rule_db>`.
- Result: refused before copying: `promote` loads the whole staging database strictly, and RF-31's
  `ext_head_on_aacce0961b` is refused there (`constant_roles`, the user's decision of 2026-10-26). The real
  `rule_db/` was never touched.
- Decision: **not promoting in this issue.** Besides the code change, the rule's grade (Partly
  supported) is borderline under "published studies only": the side, left, has guidance but no study in
  Singapore. That is the user's call (open question 1).

### 2026-10-30 00:37 UTC — Deliverables written
- What I did: wrote `literature/rule-verification/` (README with the summary table, references check,
  six evidence files, sources, search log). Checked numbers against the run files: the Step 1
  comparisons were computed on the 216 sessions of `rf10_round1_head_on_keep_line` and
  `rf30_round1_head_on_keep_line` outside the exact-repeat set (my filters did not reproduce RF-11's 192;
  stated in the report's limits). Corrected two counts while checking (keep-left debriefs 56, of which 53
  name Singapore; the "every other factor" line, which wrongly said nothing else reached p < 0.03).
- Result: every kept rule is Partly supported; assertiveness as a factor is Contradicted (Knorr 2016,
  abstract); neither the extractor nor any agent named a checkable source.

## Open questions / risks

1. **Promote `ext_head_on_0ecc2d1a6e` (both turn 10° left)?** #55's table says promote (Partly
   supported, helps), but (a) under "published studies only" the side has no Singapore evidence, and
   (b) `promote` needs a small code change to skip the refused rule in RF-31's staging database. My
   recommendation: do not promote yet; keep it staged, labelled "helps; shared side supported, left in
   Singapore rests on guidance", and promote only if a Singapore side study turns up or the user accepts
   guidance plus Japan as enough.
2. **Abstract-only sources.** Olivier2013, Knorr2016, Nummenmaa2009, Rapos2021 and Jung2013 were read
   as abstracts (bot checks). In particular, the Contradicted grade for assertiveness depends on which
   traits Knorr2016 measured. The user can fetch the PDFs in a browser in minutes.
3. **The passing-distance comparison assumes the 0.25 m default radius** (`hallway.yaml`, marked a
   placeholder); a suitcase widens a body.
4. **Grades are one reader's judgment** on sources found in one session; #37's scale was not used (no
   supervisor approval).

## Summary (fill in at the end)

- **Changed:** recorded the user's decision on #55 decision 6 (published studies only) in `CLAUDE.md`,
  `README.md`, `docs/architecture.md` and #55. Wrote `literature/rule-verification/` (RF-14's report,
  evidence per rule, references check, sources, search log) and cached 18 sources in `refs/rf14_*`. No
  code changed; nothing promoted; no model call, USD 0.
- **Found:** 0 of 27 extractor references and 0 of 2,681 debriefs name a checkable source. All four kept
  rules are Partly supported; the keep-right pattern has no evidence for Singapore; assertiveness, the
  screen's one sure factor for avoidance, is contradicted by Knorr 2016; the other's age is supported
  (Rapos 2021: 0.90 of young agents slow for a 70-year-old against 0.52 for a peer).
- **Verified (section 5b):** every number in the report carries its run file or source and section;
  every task is answered or marked (task 6 not done, with reasons; task 8 not needed); the open
  questions are listed; sources are cached in `refs/`. No test was run: no code changed (the only file
  under `llm_negotiation/` touched is `docs/architecture.md`).
