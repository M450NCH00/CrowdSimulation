# Work Log — Issue #124: RF-38: rare factors on purpose: head-on pairs with exactly one cane user, drawn from a realistic crowd, against the human targets

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/124
**Branch:** feat/124-rf38-cane-pairs (from `origin/feat/110-rf32-group-head-on` at `8588a29`, after PR #123
(RF-37) was merged into it on 2026-10-31; `main` is not used in this track)
**Started:** 2026-10-31, 05:37 UTC

## Understanding the issue

RF-37 judged round 1's rules in head-on pairs drawn from a realistic crowd (`singapore_street_v1`, the
first two of a crowd of 100). Such a crowd has about 3 people with a cane, so a pair holds one on about 6%
of seeds (1 - 97/100 × 96/99). The cane rule (`ext_head_on_6455ca5589`, whoever faces a person with a cane
slows) almost never matched: in RF-37's `head_on`, `cane_rule_alone` has plain ORCA's numbers (H1 0.5096 m
for both). The stress crowd (half with a cane, half aged 70) shows a rule where it applies, but in meetings
that are not realistic.

The user decided on 2026-10-31, after RF-37, to test rare rules in meetings that do happen, with the rare
factor in exactly one person. Their four answers (all the recommended option):

1. **Where:** a new issue (this one), after merging PR #123 as reviewed.
2. **The draw:** "From a real crowd": the cane user is one of a realistic crowd's cane holders (so mostly
   65+, other traits at the profile's shares), the other from the people without a cane; the end that
   starts with the cane alternates by seed.
3. **Factors:** "Any factor, run cane": the draw can require any factor level; only the cane is run.
4. **Scenarios:** "1.3 m/s only": the head-on at Moussaid2009's speed, not Huber2014's three speeds.

No model call; USD 0.

## Plan

1. Record the promotion table as adopted (the user's "Yes set that as adopted", 2026-10-31):
   `docs/human-targets.md` section 6, `README.md`, #55.
2. **The draw** (`negsim/populations.py`): `quota_people(..., one_with=(factor, level))`, applied after
   today's draw so that the crowd and its random stream are unchanged; the holder is the first at the level
   in the shuffled crowd, the others the first not at it; the holder's agent cycles with the seed. Checks:
   an unknown factor or level, no holder in the crowd, a profile that is not of quotas.
3. **The scenario key** (`negsim/ruleset_eval/experiment.py`): `one_with: {factor: level}`, only with a
   population of quotas and a `pool`; recorded in the config and the summary only when given, so earlier
   configs and summaries are unchanged.
4. **Config** `configs/rule_set_evaluation/rf38_cane_head_on.yaml`: RF-37's rules, arms, baseline, base
   seed; one scenario, `head_on_cane`, 30 seeds.
5. **Report** (`negsim.human_targets.report`): the runs it reads become a parameter (`--study rf37` as
   before, byte for byte; `--study rf38`); RF-38 adds how often each rule matched, who adapts in a cane pair
   (the cane user against the other), and Step 1's resolved sessions with exactly one cane user.
6. Run, read, write up; tests; docs and READMEs; full suite; PR stacked on `feat/110-...`.

## Progress log

### 2026-10-31 05:37 UTC — Branch cut, promotion table adopted
- What I did: merged PR #123 at the user's request (05:31 UTC), closed #122 by hand, ticked it in #55,
  opened this issue, cut this branch. Recorded the promotion table as adopted in `docs/human-targets.md`
  section 6, `README.md` (RF-14 and RF-37 rows) and #55's decisions (the old table kept, marked replaced).
- Why: the user answered "Yes set that as adopted" to marking the promotion rule adopted. The smallest
  effect that counts was not given a value, so it stays open (written as open in section 6).
- Found: the issue's first version swapped H6 and H8 (H6 is "the giver adapts more", Olivier2013; H8 "with
  an older adult the young adult adapts more", Rapos2021). Corrected in the body, with a comment.
- Found: Step 1 has sessions with exactly one cane user (the screening design varied the cane): resolved
  by the plans alone, independent 20 of 40, non-verbal 27 of 40, talk 16 of 40. Enough to include them as
  the issue proposed. Their people come from the screening design, not a realistic crowd; the report says so.
- Next step: the draw and its tests.

### 2026-10-31 05:44 UTC — The draw, the scenario key, the config; run
- What I did: `one_with` in `negsim/populations.py` (`Profile.people`, `quota_people`, `one_with_people`,
  `Profile.check_one_with`) and as a rule-set evaluation scenario key (`negsim/ruleset_eval/experiment.py`:
  parsed, recorded in `as_dict`, the summary, the report and `--plan` only where given). Config
  `configs/rule_set_evaluation/rf38_cane_head_on.yaml`. Ran 150 runs, 05:44:11 to 05:44:39 UTC, USD 0.
- **[design] `pool: 1000`, not RF-37's 100**, found in the first smoke test: with 100 people the quotas
  give 3 canes, always in the 65–69, 70–74 and 75–79 bands, so every cane user was 65 to 79. The profile
  gives cane users 11% under 65 and 33% aged 80+; a crowd of 1,000 gives 35 canes, 3 under 65 and 12 aged
  80+. The user chose "From a real crowd ... other traits at real shares", which 100 would not give.
  Stated in the config, the docs and the findings.
- Result (RF-18's measure): the cane rule matched in **30 of 30** pairs (RF-37: about 6%); no change against
  plain ORCA; no gridlock or collision in any arm. The left-turn rule helps (as in RF-37's pairs).

### 2026-10-31 05:48 UTC — The report, `--study rf38`
- What I did: the runs `negsim.human_targets.report` reads became a `Study` (`--study rf37`, the default,
  or `rf38`). RF-38 adds `rule_matches`, `holder_pairs` (who adapts: the other against the cane user) and
  Step 1's sessions filtered to exactly one cane user.
- Check: `--study rf37` written to the scratchpad gives `report.md` and `summary.json` **byte for byte** as
  committed in `runs/rf37_human_targets/`.
- Result (`runs/rf38_human_targets/report.md`, read in `findings.md`):
  - the other person moves aside and slows more than the cane user in **30 of 30** pairs under the cane
    rule; the cane user passes first in 13, together in 17;
  - Step 1's agents do the same: the other moves aside more 14 to 3, 21 to 2, 12 to 4 (independent,
    non-verbal, talk);
  - **H2 outside for every rule arm**: the cane rule 0.50 m (two bodies touching), plain ORCA 0.51, the
    left-turn rule 1.25, against 0.61 to 0.97; Step 1's agents within (0.93, 0.84) or just outside (0.98);
  - **H7 opposite (older) for the cane rule**: the cane user, usually older, goes first. Confounded: Knorr
    2016 studied gender, height and personality, not canes. Left for the user (open question below);
  - `all_runnable` equals `cane_rule_alone` in cane pairs: the cane rule outranks the left-turn rule.
- Under the adopted table: the cane rule's verdict of record is still RF-33's harms, it is outside on H2,
  so it falls in "harms / otherwise", dropped. Nothing was removed from any database.

### 2026-10-31 05:55 UTC — Tests and docs
- Tests: `tests/test_populations.py` (exactly one holder, alternating end, no extra draw, ages from 1,000
  against 100, refusals), `tests/test_ruleset_eval.py` (the key's checks, described only where given,
  RF-38's config is RF-37's `head_on` with only the people changed, a run gives every arm the same pair),
  new `tests/test_human_target_report.py` (the studies, `holder_pairs` on hand-made pairs, Step 1's
  filter). The touched modules: 115 passed.
- Docs: `docs/population-profiles.md` section 6, `docs/rule-set-evaluation.md` section 1.1,
  `docs/human-targets.md` section 8, both READMEs, `.gitignore` (RF-38's big logs, as RF-37's).

### 2026-10-31 06:27 UTC — Full suite
- Full suite (started 05:52 UTC, 35 min): **2272 passed, 10 skipped** (RF-37's 2251 + 21 new). The
  `analysis/` package is untouched and was not rerun.

### 2026-10-31 13:13 UTC — H7 with the cane held fixed (the user's follow-up)
- What I did: the user asked what "age standing in for the cane" means, then asked for both checks I
  suggested: (1) who goes first when the cane user is the younger; (2) H7's check with the cane counted as
  a known factor. Added `judge.holder_younger` and `judge.not_predicted_by_traits_given` **[design]**
  (sign test for pairs the cane does not separate; Fisher's exact test for pairs with one cane user, trait
  on the cane user's side or the other's; a trait whose pairs all fall on one side is "not separable",
  not counted). `fisher` moved unchanged from `resolution/groups.py` to `ruleset_eval/verdicts.py` (groups
  re-exports it), so the judge does not import the experiment stack. `report --study rf38` shows both
  beside H7's row; **H7's verdict of record is unchanged**.
- Why the Fisher form, not a sign test on the pairs where trait and cane point at different people: there,
  the cane user going first would make the trait look significant the other way, which is still the cane.
  The question is whether the trait shifts who goes first once the cane is fixed.
- Check: `--study rf37` written to the scratchpad is byte for byte as committed; RF-38's summary keeps every
  earlier key unchanged and adds `h7_known_factor` and `holder_younger`.
- Result (`findings.md`, new section): the cane rule's H7 becomes "agrees" with **age and gender not
  separable** (every pair differing in age group has the older person holding the cane; every pair
  differing in gender with a first has a male cane user). By years, a younger cane user still went first in
  4 of 6 pairs, the other never. **No pair has a cane user under 65 meeting someone 65 or over**, so age
  apart from the cane is not tested. Also found: Step 1 non-verbal's "opposite (assertiveness)" is the same
  kind of confound (in its one-cane resolved sessions, the one holding ground is always the cane user).

### 2026-10-31 13:27 UTC — The user's decision on H7 in cane pairs
- I set out three options with their pros and cons: H7 as recorded (fixed in advance, but it penalises the
  rule for something the study did not measure), with the cane held fixed (asks the study's question, but
  designed after the result, and it cannot test age here), or "not comparable" (the study's sample had no
  cane users). I recommended: as recorded for RF-38, and "not comparable" from the next run.
- **The user chose the recommendation** ("ok let's go with your recommendation"), on their own authority.
- Recorded in `docs/human-targets.md` section 8, `findings.md`, `README.md`. No code changed: RF-38's
  verdicts stay as they are, and the outcome does not change (the cane rule is dropped by harms and H2).
  The "not comparable" treatment is not built yet (see open questions).

## Open questions / risks

- The smallest effect that counts in a direction target (RF-37, section 3) is still open.
- In rule-set evaluation a cane changes only what a rule reads; the cane user walks at 1.3 m/s.
- **For the user:** H7 counts "older" as a trait that must not decide roles. In cane pairs it is
  confounded with the cane, which Knorr 2016 did not study. Should a verdict driven by a confounded trait
  count against a rule under the adopted table? *Since 13:13 UTC:* the two checks support the confound
  reading but cannot clear age (no pair separates it from the cane). Testing age apart from the cane would
  need pairs with a cane user under 65 meeting someone 65 or over: a design choice, not a realistic draw.
  *Decided 13:27 UTC* (see the progress log): H7 as recorded for RF-38; "not comparable" from the next run.
- Not built: the "not comparable" treatment of H7 needs a list, per target, of the factors outside its
  study's sample (a new targets file version). Only the cane is identified so far.
- Whether RF-10's screening design pairs "holds ground" with the cane on purpose was not checked.
- **For the user:** the adopted table puts the cane rule in "dropped". Nothing has been removed.
- The pass distance of every rule arm is ORCA's (bodies touching). A rule that only says who gives way
  cannot meet H1 or H2; a margin in the rule, or in the ORCA layer, would be needed.

## Summary (fill in at the end)

- **What changed:** `one_with` (exactly one person at a factor's level, drawn from a realistic crowd) in
  `negsim/populations.py` and rule-set evaluation scenarios; `configs/rule_set_evaluation/rf38_cane_head_on.yaml`
  (RF-37's `head_on` with one cane user, `pool: 1000`); `negsim.human_targets.report --study rf38` (rule matches,
  who adapts in a cane pair, Step 1's one-cane sessions). The promotion table adopted (`docs/human-targets.md`, 6).
- **Result:** the cane rule applied in 30 of 30 pairs and the other person gave way in every one, as Step 1's
  agents also do; but every rule arm passes at ORCA's 0.50 m, outside H2; H7 opposite through the cane-age
  confound. Under the adopted table the cane rule is dropped (nothing removed).
- **Verified:** RF-37's report and summary regenerate byte for byte; earlier configs are described as before
  (tested); full suite 2272 passed, 10 skipped. No model call, USD 0.
