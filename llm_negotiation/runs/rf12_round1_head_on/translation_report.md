# RF-12, round 1 (head-on): what rule format 3 kept of the extracted rules

Issue #67. Paid run of 2026-10-26, 10:01 to 10:05 UTC (off-peak), approved for this issue only
with a cap of USD 0.03 (`CLAUDE.md`). Four calls to `deepseek-flash` at temperature 0, one per
rule, none retried: **USD 0.0017** (worst case USD 0.028). Template `translate_v1`; method in
`docs/rule-translation.md`. The machine-written table is `report.md`; the numbers here are from
`summary.json`, `translations/`, `identity/` and the staged rules
(`rule_db_staging/extracted/`).

## What went in

RF-11's four kept rules (`candidate`, found in 2 or 3 of its 3 runs), from
`runs/rf11_round1_head_on/head_on/extracted_rules/`:

| Extracted rule | In words (shortened) | RF-11's category |
| --- | --- | --- |
| `x_head_on_0ecc2d1a6e` | In the 20 cm layout the pair keep the side their final plan takes, and almost never stop or back up | valid |
| `x_head_on_4eb7a97c8d` | People signal (eye contact, a nod, a wave) when the other drifts to their side or the plan fails, and speak to warn or greet | needs_communication |
| `x_head_on_6455ca5589` | A person who gives way slows on the first plan when the other is elderly, has a cane, pulls a suitcase or looks at a phone | valid |
| `x_head_on_aacce0961b` | A person who holds their ground keeps their line at full speed and steps aside or slows only at close range | valid |

## Findings

**1. Format 3 could say almost nothing of these rules.** Every rule depends on something format 3
cannot read. Of the factors the four rules use, format 3 has a field only for the other's age
and the distance at which a person decided (`readable`, 2 of 4 rules). It has no field for a
cane, a suitcase, a phone, the layout, how many decisions a person made, or whether the two know
each other (`no_field`, 4 of 4). Assertiveness, urgency and a bad memory are known only to the
person, so the loader refuses them (`unobservable`, 2 of 4). The signalling rule depends on the
condition (`communication`, 1 of 4). The
translator listed what it lost in its own words: conditions in 4 of 4 rules, speeds in 3, a turn
angle or step aside in 2, a start distance in 2, a duration in 1, signals or words in 1. The
mechanical check of the extracted rules' words agrees: start distances in 4, speeds in 3, turn
angles in 2.

**2. Three translations are valid, one is not expressible, and two of the three valid ones are
plain ORCA.**

| Translated rule | Category | What it says |
| --- | --- | --- |
| `ext_head_on_0ecc2d1a6e` | valid | Both people in a head-on: speed scale 1, no side preference. **The same as plain ORCA** |
| `x_head_on_4eb7a97c8d` | not expressible | Null: "the rule is entirely about signalling and speaking, which the format cannot express". Not written |
| `ext_head_on_6455ca5589` | valid | **Both** people in every head-on slow to 0.73 of their speed. The condition (a person who gives way, facing an older or encumbered other) is gone, so a rule about one person became a rule about everyone |
| `ext_head_on_aacce0961b` | valid | Both people in a head-on: speed scale 1, no side preference. **The same as plain ORCA** |

The translator did what the template asked: it added nothing, and listed every part it dropped.
"The one who gives way" cannot be written, because nobody can see who gives way. Its note on
`6455ca5589` says the format cannot read the other's "told age" either. Format 3 could have said
"the younger of the two slows" (roles by `agent.age`). That is close to the extracted rule's age
branch, but it is not the extracted rule, and the template says to add nothing. Whether a
translator should make that step is a judgement this run does not settle.

**3. The identity check: no translation changes what ORCA does in the Step 1 sessions.** Each
valid rule was switched on alone and run on the 76 resolved Step 1 sessions it was extracted from.
It matched all 76. In every session the outcome was plain ORCA's:

| | Same agent first | Same passing sides | Both (reproduced) |
| --- | --- | --- | --- |
| Each of the three translated rules | 0.67 | 0.55 | **0.36** |
| Plain ORCA, same seeds | 0.67 | 0.55 | **0.36** |

So 36% of the agents' outcomes are what plain ORCA would have done anyway, and the translated
rules add nothing to that. For the two no-op rules this is by construction. For the symmetric
slow-down it shows that slowing both people changes neither who passes first nor the sides in a
two-person head-on. Plain ORCA's replay was the run each session recorded in all 76 sessions, so
the check itself is sound. In none of the 76, under any rule or none, did ORCA "resolve" the
meeting in Step 1's sense: in all 288 round 1 sessions plain ORCA never collides but always comes
within the near-miss distance.

**4. Crowd screening: the slow-down fails.** In the two-way flow (50 + 50, two seeds), the two
no-op rules give exactly the baseline's runs (passed). `ext_head_on_6455ca5589` (both slow to 0.73
in every head-on) **gridlocks the flow on both seeds**: it times out at 120 s with 80 and 34 of 100
arrived, where the baseline finished in 52 s and 79 s. It had 1,518 and 2,262 collision episodes
against 86 and 68. A rule that looked harmless for two people breaks a crowd, as #30's mock rules
did (`rule-generation.md`, section 8). This is the reason the screening step exists.

**5. Needs communication.** One of the four rules was extracted as needing communication. Its
translation is null, so it was not written. No written rule is marked not runnable.

## What this means for the track

- Round 1's rules, as format 3 can say them, are not usable: two are plain ORCA, and the third
  would gridlock a crowd. What made the LLM agents' behaviour differ from ORCA (who gives way,
  what they see of the other, when they start, by how much they turn) is exactly what format 3
  cannot read or say.
- This supports the supervisor's remark that the rule format is not what matters. It also shows
  that **negsim's format 3, in particular, is too narrow for these rules.** RF-18 (#74), which
  runs all rules with ORCA in crowds, would have nothing useful to run from round 1 unless the
  format is extended (out of scope here) or rules are run in another way.
- The identity check is a useful baseline for later rounds: a translated rule earns credit only
  above plain ORCA's share (0.36 here).

## Limitations

- **One translation per rule** at temperature 0. Another sample, or another model, might write
  "the younger slows", which format 3 can say. That would be a different rule from the one
  extracted.
- The identity check compares who passed first and the passing sides only. It cannot tell a lost
  translation apart from ORCA under any rule behaving unlike the agents' plans.
- Crowd screening ran two seeds of one flow.

## Files

`translations/<x_rule_id>.json` (prompts and raw replies), `rule_db_staging/extracted/` (the
three written rules, v1 as translated and v2 with their screening), `identity/<ext_rule_id>.csv`
(76 rows each), `screening/` (each crowd run's `config.json`, `outcome.json` and
`events.jsonl`; the bulky logs are not committed and are rebuilt by running the experiment
again), `summary.json`, `report.md`.
