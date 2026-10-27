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

### 2026-10-27 about 08:30 UTC — The layer, and a clash found before any run
- What I did: `negsim/ruleset_eval/` (`experiment.py`: config, the run's own staging database, the
  runs, summary and report; `measures.py`; `verdicts.py`, the rule of task 0), wired into
  `run_experiment.py`; `StagingDatabase.copy_in` and `write_ruleset` in `negsim/rulegen/writer.py`;
  config `configs/rule_set_evaluation/rf18_round1.yaml`.
- Tried the measures on RF-31's screening run (seed 30901) first: plain ORCA 791 severe conflicts,
  the left-turn rule 566; lanes 50/50 against 63/37 to the left; but throughput 115 against 78 per
  minute, because one person ended 40 s late and throughput counts arrivals over the whole run, while
  mean delay improved (1.37 s against 0.77 s). The measure agreed in task 0 stays; the doc and the
  report say how to read it.
- **Found before any run: the two rules cannot be switched on together.** Both translations have
  priority 500 (the translator's default), and the loader's pre-run check finds a head-on in which one
  person has a cane where both match with different directives, so it refuses set 2 as `ambiguous`
  (`rule-matching.md`, section 4). That is task 4's first answer: the rule set of round 1 clashes.
- **Asked the user, who chose "the cane rule wins" (the narrower rule where both match).** Built as a
  config `priority` (with a required `reason`): the run's staging database gets one more version, v3,
  the same rule with priority 600 and the reason in its provenance notes; the staged original is
  untouched; v3 is switched on in every arm.
- **A bug found in the smoke run:** two-person scenarios moved the mix of people on by two per seed,
  but the mix gives a cane to four people in a row, so every pair was two cane users or none, and the
  cane rule (roles by a condition, `tie: no_match`) could never match. Changed to one person per seed
  (canes in mixed pairs on 2 of the 10 seeds), with a test.
- Smoke result (2 seeds): in the narrow passage, plain ORCA deadlocks on every seed (they start face to
  face) and neither rule matches: the pair's class is `single_file_segment`, not `head_on`.
- Committed the build (159cf715) before the run of record, so its runs record a clean commit.
- Next step: the run of record (150 runs), tests, the benchmark, docs.

### 2026-10-27 about 08:40 UTC — Tests, the benchmark option, the doc (while the run goes)
- Tests: `tests/test_ruleset_eval.py`, 21 passed (the sign test; every verdict; the config's
  refusals; the byte-for-byte copy and its refusal; a rule set frozen once; two clashing rules refused
  unless one gets a priority, with the canonical form unchanged; people moving on by one; **task 8**:
  `keep_left_head_on` and `younger_yields_head_on` together, where the higher priority wins as
  documented, and an overtaking rule in a head-on, not used, with the head-on logged as uncovered;
  resume; lanes only in the flow; delay; the command).
- `scenario_overrides` added to a scenario entry (a smaller crowd in the tests; other crowd sizes later).
- `negsim.rules.benchmark`: `--database`, `--ruleset`, `--people-from`; the defaults as before.
- Doc: `docs/rule-set-evaluation.md`.

### 2026-10-27 about 09:10 UTC — The run of record: 150 runs, no model call
- What I did: `python run_experiment.py configs/rule_set_evaluation/rf18_round1.yaml` at commit
  159cf715 (clean). Report: `runs/rf18_round1/evaluation_report.md` (mine) and `report.md` (written by
  the code).
- **Check:** seeds 30901 and 30902 of the flow reproduce RF-31's screening runs exactly (plain ORCA,
  the left-turn rule, the cane rule: status, time, collisions and every tier count), although the
  rules are copies, and the cane rule a new version (v3, priority 600).
- **Verdicts, by the rule fixed before the run:**
  - flow: set 1 (left turn) **helps** (severe conflicts fewer on 10 of 10 seeds; throughput and delay
    better on 9 of 10); the cane rule alone **harms** (gridlock on seeds 30902 and 30904); set 2
    **trade-off** (severe fewer on 9 of 10, delay worse on 10 of 10);
  - bottleneck: **no change** for all three (the pair is a single-file meeting until the last two
    steps, so the rule's plan starts too late);
  - passage: **not used** for all three (plain ORCA deadlocks on every seed; the pair is
    `single_file_segment` throughout, which no round 1 rule covers).
  - Per rule: `ext_head_on_0ecc2d1a6e` **helps**, `ext_head_on_6455ca5589` **harms**.
- **Exploratory, after the run (not part of the verdict):** sign tests on collided pairs (T4) and
  collision episodes. Set 2 has **more collided pairs on 9 of 10 seeds (p = 0.02) and more collision
  episodes on 10 of 10 (p = 0.002)**: its fewer severe conflicts are fewer near misses only. The main
  measure (T3 + T4 pairs) cannot see a near miss turning into a collision. The left-turn rule's gain is
  in near misses too (T3 10 of 10); its collisions are fewer on 7 of 10, not significant. **I did not
  change the verdicts after seeing the data**; the report gives both readings and asks the user about
  a fix for later reruns (open question 4).
- Uncovered conflicts: overtaking dominates the flow under every rule arm (set 2: 15,368 pairs at T1
  or above), then crossing; single-file meetings in the two small scenarios. Both are rounds 2 and 3's
  scenarios already, so nothing new is proposed.
- Rule conflicts: 0 pairs matched by several extracted rules; 31,094 cross-pair conflicts in set 2
  (the cane rule's slowing spreads, the smallest scale applying); under the left-turn rule 45,373
  matches did not start a plan because one was in force (4,077 did).
- The hand-written reference (`rule_db` `default`) cut severe conflicts further (439 against plain
  804 and set 1's 569) and sent 69% of the crowd left; numbers only, as D-C.

### 2026-10-27 about 09:40 UTC — The cost per step (quiet machine)
- `python -m negsim.rules.benchmark --database runs/rf18_round1/rule_db_staging --ruleset <set>
  --people-from configs/rule_set_evaluation/rf18_round1.yaml --agents 100 1000`, for both sets, nothing
  else running; no Kernel-Power 506/507 events in the two hours before.
- Set 1: ×1.84 at 100 agents, ×1.51 at 1,000; set 2: ×1.73 and ×1.57; matching is 35 to 38% of a rule
  step. Plain ORCA: 70 ms a step at 100, 687 at 1,000 (about tenfold). Issue #28's hand-written set
  was ×2.32 and ×2.98 (its absolute times differ: plain ORCA then took 52 ms at 100).
- Reading: towards 10,000 agents, plain ORCA's own growth is the larger cost; the rules add about half.

### 2026-10-27 about 10:20 UTC — Committing the run (after a pause: the shell's permission check failed)
- The run folder's tracked files came to 55.5 MB, 44.0 MB of it `events.jsonl` (set 2's runs log
  tens of thousands of cross-pair conflicts and collisions). **Decision (mine): `events.jsonl` of
  RF-18's runs is not committed** either (gitignored with the other bulky logs); nothing in the
  verdicts reads it, and the runs are deterministic (the first two seeds reproduced RF-31's runs
  exactly), so `--overwrite` rebuilds it. Committed: 11.5 MB in 469 files (`config.json`,
  `outcome.json`, `measures.json` per run; the summary, reports, benchmarks, the staging database).

## Open questions / risks

1. ~~**The definition of "helps"**~~ fixed with the user before any run (entry above).
2. **Half the crowd carries a cane** (D-E). The cane rule's harm in screening may come from that share.
3. Round 1 gives one rule that changes ORCA's outcome, so set 1 is a single rule. The tool is the
   lasting part; round 1's numbers are thin.
4. **Should collisions count separately in the verdict, for later reruns?** Proposal: an arm also
   harms if collided pairs (T4) or collision episodes are significantly worse. Not applied to this
   run; under it set 2 would be "harms" and set 1 would stay "helps". The user's decision.
5. **D-F (mine): a rule's overall reading over scenarios** puts harms first, then helps, trade-off, no
   change, not used. Both round 1 rules have only one scenario where they are used, so it changes
   nothing here.
6. "Covered" means a rule matched the pair at some point (the bottleneck's pair counts as covered
   although it was a single-file meeting for most of its encounter). A stricter count (the share of a
   pair's evaluations matched) could come later.

## Summary (fill in at the end)

**What changed.** A new layer, `rule_set_evaluation` (`negsim/ruleset_eval/`, run by
`run_experiment.py`): staged rules switched on together, in a staging database of the run's own
(copied byte for byte, one rule set per arm, a new priority only as a new version with a reason),
against plain ORCA on paired seeds in several scenarios; measures (severe conflicts, collisions,
throughput, delay, lane formation, rule conflicts, uncovered conflicts); verdicts by the rule fixed
with the user before any run (`verdicts.py`); `summary.json` and `report.md`. `StagingDatabase`
gained `copy_in` and `write_ruleset`; `negsim.rules.benchmark` gained `--database`, `--ruleset` and
`--people-from`. Round 1's run of record: `runs/rf18_round1/` (`evaluation_report.md`).

**Why.** #74, reordered by the user on 2026-10-27 to come before RF-14: an extracted rule is first
run in the simulation (does it help?), then checked against human evidence.

**Result.** The left-turn rule helps in the two-way flow; the cane rule harms; together they are a
trade-off by the agreed rule, which understates harm (collisions up on every seed). Neither rule
applies to single-file meetings (the bottleneck, the narrow passage). What no rule covers: overtaking,
then single-file meetings: rounds 2 and 3. Cost ×1.5 to ×1.6 per step at 1,000 agents.

**How it was verified.** `tests/test_ruleset_eval.py` (21 tests, including task 8's two hand-made
rules together and an unmatched conflict logged); the run's first two flow seeds reproduce RF-31's
screening runs exactly; the benchmark run on a quiet machine. Full suite at 8f3e91eb: 2,121 passed,
10 skipped, 1 failed: `test_stop_at_cap_...`, the known peak-hour `cost.json` gap of #64 (run at
09:54 UTC, DeepSeek's peak; the same numbers as on #108's branch before this one), not touched here.
PR #111, against `feat/108-rf31-rule-format-4`.
