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

## Open questions / risks

- The smallest effect that counts in a direction target (RF-37, section 3) is still open.
- In rule-set evaluation a cane changes only what a rule reads; the cane user walks at 1.3 m/s.

## Summary (fill in at the end)
