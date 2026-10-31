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
   rule; whether a confounded trait should count is a question for the user. The two checks below (added
   the same day) test this.
5. **In a cane pair the left-turn rule never acts** when both rules are on: the cane rule outranks it
   (priority 600, the user's choice of 2026-10-27), so `all_runnable` equals `cane_rule_alone` here.
6. **The keep-left defaults also make the other give way** (24 to 6), through their younger-yields rule,
   because the cane user is usually the older one.

## H7 with the cane held fixed (added 2026-10-31, at the user's request)

Two checks of finding 4, on the same runs (no new run, no model call). Both are in `report.md` beside H7's
row, which they do not replace: H7's verdict of record is unchanged.

**1. When the cane user is the younger, who goes first?** If age decided, the other would.

| Subject | Cane user younger by years: cane user / other / together | Younger by age group (under 65 against 65+) |
| --- | --- | --- |
| Cane rule (alone, or with the left-turn rule) | 6 pairs: **4 / 0 / 2** | no pair |
| Plain ORCA, left-turn rule, keep-left defaults | 6 pairs: 0 / 0 / 6 | no pair |
| Step 1's agents | no pair (the other is always 25) | no pair |

In all 30 cane-rule pairs the other person never goes first, whatever the ages. Where the cane user is the
younger by years (for example 71 against 80, 38 against 51), the cane user still goes first in 4 of 6 and
passes together in 2. But **by the targets' age groups, which H7 uses, no pair has a cane user under 65 and
the other 65 or over**: the realistic crowd's 3 younger cane users met people aged 19 to 51. So this is
evidence by years, not a test of H7's own "older".

**2. H7's check with the cane held fixed** (`judge.not_predicted_by_traits_given`, **[design]**). For each
trait, pairs where both or neither have a cane keep H7's sign test. In pairs with one cane user, the trait
is either on the cane user's side or on the other's; if the trait adds nothing to the cane, the cane user
goes first equally often either way (Fisher's exact test). If every pair is on one side, the trait cannot be
told apart from the cane and is not counted. Bonferroni over all the tests made.

| Subject | H7 as recorded | With the cane held fixed | Not separable from the cane |
| --- | --- | --- | --- |
| Cane rule (alone, or with the left-turn rule) | opposite (older) | agrees (assertiveness only: the cane user first 4 of 4 and 2 of 2, p 1) | older, gender |
| Step 1, independent | agrees | agrees (gender, p 0.24) | assertiveness, older |
| Step 1, non-verbal | **opposite (assertiveness)** | agrees (gender, p 0.18) | assertiveness, older |
| Step 1, talk | agrees | agrees (gender, p 0.40) | assertiveness, older |

What this shows:

- **The cane rule's "opposite" goes away once the cane is held fixed, but age is not cleared.** Every pair
  that differs in age group has the older person holding the cane, so these runs cannot say whether age
  matters apart from the cane. The "agrees" rests on assertiveness alone (6 pairs).
- **Gender was confounded too.** In the 6 cane-rule pairs that differ in gender and have a first, the cane
  user is the man every time. H7 as recorded gave gender p 0.031, just over its Bonferroni threshold
  (0.0167).
- **Step 1's non-verbal "opposite (assertiveness)" is the same kind of confound.** In Step 1's one-cane
  sessions that resolved, the other person always gives way, so whenever the two differ in assertiveness the
  cane user is the one who holds ground. Assertiveness cannot be told apart from the cane there either.
  (Whether RF-10's screening design pairs them on purpose was not checked.)

The checks support reading finding 4 as a confound, and suggest the same for Step 1's non-verbal row. They
cannot show that age plays no part: no pair separates the two. A run that could test age apart from the cane
would need pairs with a cane user under 65 meeting someone 65 or over: a design choice (`one_with` with an
age condition), not a realistic crowd's draw.

**Decided by the user on 2026-10-31** (on their own authority, choosing the recommendation of three options
set out in the session: as recorded, cane held fixed, or not comparable):

- **For RF-38, H7 as recorded is the verdict of record.** The check was fixed before any rule was measured
  (the user's decision of 2026-10-30), and the outcome does not depend on it: the cane rule is dropped by
  RF-33's harms and H2 alone. The check with the cane held fixed stays beside it, as a description.
- **From the next run on, H7 is "not comparable" in pairs that a factor outside its study's sample
  separates**, such as a cane (Knorr et al. 2016 did not study mobility aids). The same goes for Step 1's
  subjects. Under the promotion table, "not comparable" does not count against a rule. Not built yet: see
  `docs/human-targets.md`, section 8.

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
