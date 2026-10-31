# RF-38: round 1's rules in head-on pairs with one cane user (issue #124)

Run of 2026-10-31, no model call, USD 0. The machine-written tables are `report.md` (human targets) and
`../rf38_cane_head_on/report.md` (RF-18's measure); the numbers here come from their `summary.json` files.

## What was run

RF-37 drew its head-on pairs from a realistic crowd of 100. Such a crowd has about 3 cane users, so the
cane rule (`ext_head_on_6455ca5589`: whoever faces a person with a cane slows) applied in about 6% of
pairs, and its numbers there were plain ORCA's. **The user decided on 2026-10-31** to test a rare rule in
meetings that do happen, with the rare factor in exactly one person.

- **150 runs**: RF-37's corridor (1.75 m, Moussaid et al. 2009) at 1.3 m/s, 30 seeds × plain ORCA and
  RF-37's four arms (same rules, versions, priorities, baseline and base seed).
- **The people** (`one_with: {mobility_aid: cane}`, `negsim.populations.one_with_people`): on each seed a
  realistic crowd at the profile's exact shares; the cane user is its first cane holder, the other its
  first person without a cane; the cane user's end alternates by seed. **[design] The crowd is 1,000, not
  100**: 100 people round to 3 canes, all aged 65 to 79, while 1,000 give 35 at the profile's ages
  (3 under 65, 12 aged 80 and over). The 30 cane users were aged 36 to 90: 3 under 65, 6 aged 80 and over.
- **Step 1's agents**: the sessions of RF-10 (independent) and RF-30 (non-verbal, talk) under `keep_line`
  with exactly one cane user, resolved by the plans alone: 20, 27 and 16 of 40 each. Their people come from
  the screening design, not a realistic crowd: every cane user is 25 or 70.

## Results

| | Plain ORCA | Left-turn rule | Cane rule (alone, or with the left-turn rule) | Keep-left defaults | Step 1's agents (ind. / non-verbal / talk) |
| --- | --- | --- | --- | --- | --- |
| Cane rule matched | – | – | **30 of 30 pairs** | – | – |
| H2 pass distance with an older adult (0.79 ± 0.18 m) | outside, 0.51 | outside, 1.25 | **outside, 0.50** | outside, 0.51 | within 0.93 / outside 0.98 / within 0.84 |
| The other moves aside more than the cane user | 12 to 18 | always equal | **30 to 0** | 24 to 6 | 14 to 3 / 21 to 2 / 12 to 4 |
| The other slows more than the cane user | 13 to 13 | 16 to 12 | **30 to 0** | 25 to 4 | 16 to 4 / 23 to 4 / 13 to 3 |
| Who passes first: cane user / other / together | 0 / 0 / 30 | 0 / 0 / 30 | 13 / 0 / 17 | 0 / 0 / 30 | 6 / 5 / 9, 9 / 2 / 16, 4 / 2 / 10 |
| H6 the giver adapts more | not comparable | not comparable | agrees, 13 to 0 | not comparable | 8 to 3 / agrees 9 to 1 / 5 to 1 |
| H7 roles not predicted by traits | not comparable | not comparable | **opposite (older)** | not comparable | agrees / opposite (assertiveness) / agrees |
| H8 with an older adult, the young adapts more | 2 to 3 | not comparable | 5 to 0, not shown | 5 to 0, not shown | 7 to 2 / agrees 10 to 0 / 6 to 1 |
| RF-18's measure against plain ORCA | | helps | no change | (not judged) | |

Every comparison but H5's is in a setting unlike the study's (`report.md`). H1 (two young adults) does not
apply to the rule arms: no pair has two young adults.

## Findings

1. **Where it applies, the cane rule does what it says.** The other person moves aside and slows more than
   the cane user in all 30 pairs, and the cane user passes first in 13 (together in the rest).
2. **Step 1's agents do the same.** In every condition the other person makes more room for the cane
   user than the cane user does (lateral share 0.60 to 0.64), significantly in independent and non-verbal.
   So the rule's idea matches the agents it was extracted from.
3. **But the pass distance is not human.** The cane pairs pass at 0.50 m between centres, which is two
   0.25 m bodies touching, where people pass at 0.61 to 0.97 m (H2). Plain ORCA gives the same (0.51 m).
   The rule changes who gives way, not how far apart they pass: that distance comes from the ORCA layer
   underneath. Step 1's agents pass at 0.84 to 0.98 m.
4. **H7 "opposite (older)" here is the cane, not age.** The rule lets the cane user go first, and the cane
   users are mostly older, so "older" predicts who goes first. Knorr et al. 2016 studied gender, height and
   personality, not mobility aids. Under the adopted promotion table this verdict still counts against the
   rule; whether a confounded trait should count is a question for the user.
5. **In a cane pair the left-turn rule never acts** when both rules are on: the cane rule outranks it
   (priority 600, the user's choice of 2026-10-27), so `all_runnable` equals `cane_rule_alone` here.
6. **The keep-left defaults also make the other give way** (24 to 6), through their younger-yields rule,
   because the cane user is usually the older one.

## Under the promotion table adopted on 2026-10-31

The cane rule's verdict of record under RF-18's measure is still RF-33's **harms** (gridlock on 1 of 30
seeds in a realistic crowd). In these pairs it is "no change". RF-14 graded it partly supported. It is
outside on H2 and, through the confound above, opposite on H7. That puts it in the table's "harms /
otherwise" cell, **dropped**. Nothing has been removed from any database; this is for the user. The
left-turn rule stays staged (it does not harm, but is outside on H1 and H2).

## Limits

- No published study is about a cane user in a head-on meeting. The who-adapts rows are described, not
  judged.
- In rule-set evaluation a cane changes only what a rule reads: the cane user walks at 1.3 m/s with a
  0.25 m body, like everyone else.
- Step 1's cane users are aged 25 or 70 (the screening design), not a realistic crowd's.
- The share of cane users under 65 (0.5%) is a placeholder (the user's value of 2026-10-27), and the
  shares from 65 come from the United States (NHATS 2011).
