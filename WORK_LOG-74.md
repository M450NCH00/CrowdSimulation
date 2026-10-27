# Work Log — Issue #74: RF-18: all rules so far with ORCA, against plain ORCA, with a log of uncovered conflicts (rerun after every round)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/74
**Branch:** feat/74-rf18-rule-set-crowd-runs (from `feat/108-rf31-rule-format-4`; PR #109 merged into
`feat/67-...` on 2026-10-27, and `main` is not used in this track)
**Started:** 2026-10-27, about 07:40 UTC

## Understanding the issue

Track #55's end state is a simulation that runs ORCA plus the extracted rules, with no LLM call
(`docs/resolution.md`, D9). RF-12 and RF-31 screened each translated rule **alone**, in one flow,
for one thing only: whether it gridlocks the crowd. This issue builds the tool that runs **the rule
set as a whole** against plain ORCA on paired seeds, in several scenarios including one no rule was
extracted from, and asks:

- does it change what happens, and does it **help** (the user's filter, decided 2026-10-27: an
  extracted rule is first run in the simulation, then checked against human evidence in RF-14)?
- which conflicts does no rule cover (the loop back to new scenarios)?
- what does it cost per step (towards 10,000 agents)?

Since the user's reorder of 2026-10-27 this issue comes **before RF-14**. No rule is promoted yet,
so it runs on the staged rules and gives each one a verdict that RF-14 reads. A verdict here never
removes a rule from RF-14 (#55, "Decisions", the two filters). No LLM call, so no cost and no
approval needed.

**What round 1 has to run** (from the staging databases of RF-12 and RF-31):

| Extracted rule | Format 3 (RF-12) | Format 4 (RF-31) | Runnable here? |
| --- | --- | --- | --- |
| `0ecc2d1a6e` keep your side | v1-v2, plain ORCA in effect | v1-v2 (`rf31_round1_head_on`), both turn 10° left; passed screening | **yes** |
| `6455ca5589` slow for a cane | v1-v2, both slow; failed screening | v1-v2 (`rf31_round1_head_on_retry`); failed screening | **yes** (set 2 only) |
| `aacce0961b` hold your ground | v1-v2, plain ORCA in effect | v1-v2, now refused by the loader (`constant_roles`) | no |
| `4eb7a97c8d` signal and speak | not expressible | not expressible | no |

## Plan

0. **Task 0 first:** record the order in `README.md` and `llm_negotiation/README.md`, and fix what
   "helps" means **before any run** (below). Commit it before any run, so the record shows it was
   fixed first.
1. **A new layer, `rule_set_evaluation`** (`negsim/ruleset_eval/`, run by `run_experiment.py`):
   - a config that lists the arms (rule sets), where each rule comes from, the scenarios, seeds and
     the crowd's people;
   - it assembles **one staging database** for the run from the source staging databases, by
     copying each chosen rule's files byte for byte (every version, so its history runs 1, 2, ...),
     with its own manifest and one rule set file per arm; nothing is edited;
   - each arm × scenario × seed is an avoidance run beside plain ORCA on the same seed.
2. **Measures** per run (task 3): gridlock, collision episodes, near misses, the severity tiers of
   the pair interactions, throughput, delay per agent (time to goal minus path length over preferred
   speed), lane formation in the two-way flow (from the trajectory), rule matches.
3. **Rule conflicts** (task 4): ambiguous matches and cross-pair conflicts, from the outcome and the
   pair records. **Uncovered conflicts** (task 5): every pair interaction at tier T1 or above that no
   rule matched, grouped by encounter class at its start, scenario and tier.
4. **Verdicts** per arm and scenario (helps, trade-off, no change, harms), by the rule fixed in
   task 0; and per rule.
5. **Cost** (task 3's runtime): extend `negsim.rules.benchmark` to take a database, a rule set and
   the crowd's factors, and time 100 and 1,000 agents.
6. **Report**, `summary.json`, and the rerun config (task 7).
7. **Tests** on the mock-free path with two hand-made rules (task 8), plus the assembly, measures
   and verdicts.
8. Docs: `docs/rule-set-evaluation.md`, `log-schema.md`, the READMEs.

## Decisions made in this issue (mine, for the user to check)

- **D-A. One translation per extracted rule, the latest format.** RF-31 re-translated round 1's rules
  into format 4, so its translations replace RF-12's. RF-12's format 3 translations share their rule
  ids with RF-31's and could not be in one database with them anyway; two of the three act as plain
  ORCA. They are counted as left out, with the reason.
- **D-B. Arms.** Plain ORCA; set 1 = rules that passed crowd screening (`0ecc2d1a6e`, alone); the
  retried cane rule alone; set 2 = every runnable staged rule (both together). Set 1 is one rule,
  so "the set as a whole" first matters in set 2.
- **D-C. A reference arm, not judged:** `rule_db/`'s hand-written `default` set (keep left head-on
  and the rest, issue #28), so that an extracted rule can be compared with a hand-written one. It
  gets numbers, not a verdict.
- **D-D. Scenarios.** `bidirectional_flow` (the crowd, 100 people), `corridor_to_bottleneck`
  (two people, opposing), and as the scenario **no rule was extracted from**, `passage_meet_middle_v1`
  (round 2's narrow passage layout). Overtaking was the other candidate the issue names, but no head-on
  rule can match a same-direction pair, so it would only show "no change".
- **D-E. The crowd's people:** RF-31's screening population (ages 25 and 70, both genders, and
  canes, suitcases, phones and assertiveness cycling), so that results compare with screening.
  Half the crowd carries a cane, which is no real crowd's share (open question 2).

## Progress log

### 2026-10-27 about 07:40 UTC — Started
- What I did: read #74 and #55, the replay and crowd screening code (`negsim/rulegen/replay.py`), the
  provider and database (`negsim/rules/`), `rule-matching.md`, `metrics.md`, `log-schema.md`, the
  benchmark, and RF-31's report and configs.
- Found: a run reads one rule database, and RF-12's and RF-31's stagings share rule ids, hence
  D-A and the assembled database. Lane formation and delay per agent are not measured anywhere yet.
  `pair_interactions.jsonl` has what uncovered conflicts need (tier, encounter class, matches).
- Next step: task 0, the definition of "helps", for the user to confirm before any run.

### 2026-10-27 about 07:55 UTC — Task 0: what "helps" means, fixed before any run (the user's choice)
- Asked the user, who chose the proposed rule ("Proposed rule (Recommended)"). Fixed here, before any
  code or run of this issue:
  - **Unit:** per arm and scenario, against plain ORCA on the **same seeds** (paired, `baseline.md`
    section 6), **10 seeds** per scenario.
  - **Main measure, severe conflicts:** the number of pair interactions at tier **T3 or T4** (a near
    miss, a collision or a deadlock while the pair was open; `metrics.md`, section 11.3) in a run.
  - **Side measures, the cost to the crowd:** throughput (agents arrived per minute) and **delay per
    agent** (time to goal minus the path's length over the agent's preferred speed, mean over those
    who arrived).
  - **Gridlock:** the run ends in deadlock, or at its time limit with people still walking (as crowd
    screening).
  - **Better or worse** on a measure only if the **exact two-sided sign test** over the seeds, ties
    dropped, gives **p < 0.05** (with 10 seeds and no ties: 9 of 10 must agree).
  - **Verdicts**, in this order:
    - **not used**: no rule of the arm matched on any seed;
    - **harms**: it gridlocks on a seed where plain ORCA did not, or severe conflicts are
      significantly worse;
    - **helps**: severe conflicts significantly fewer, and throughput and delay not significantly
      worse;
    - **trade-off**: severe conflicts significantly fewer, but throughput or delay significantly
      worse;
    - **no change**: anything else.
  - **Lane formation is reported, not judged:** it is about realism, which is RF-14's filter.
  - **A rule's verdict** is that of the arm with the rule alone; set 2's verdict is the set's.
- Also: the order recorded in `README.md` and `llm_negotiation/README.md` (RF-18, RF-32, RF-14,
  RF-15; RF-13 in round 2).
- Next step: the layer (plan step 1).

## Open questions / risks

1. ~~**The definition of "helps"**~~ fixed with the user before any run (entry above).
2. **Half the crowd carries a cane** (D-E). The cane rule's harm in screening may come from that share.
3. Round 1 gives one rule that changes ORCA's outcome, so set 1 is a single rule. The tool is the
   lasting part; round 1's numbers are thin.

## Summary (fill in at the end)
