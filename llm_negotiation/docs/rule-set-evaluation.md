# Rule-set evaluation: the rules together, against plain ORCA (issue #74, RF-18)

Track #55's end state is a simulation that runs ORCA and the extracted rules, with no LLM call
(`resolution.md`, D9). Translation (`rule-translation.md`) checks each rule alone: on the Step 1
sessions it came from (the identity check) and, in one flow, for gridlock (crowd screening). This
layer runs **the staged rules switched on together**, beside plain ORCA on the same seeds, in
several scenarios, and gives each rule set and each rule a **verdict** on whether it helps.

**Its place in the track** (the user, 2026-10-27; #55, "Decisions"): an extracted rule is first run
in the simulation (does it help?, this layer), then checked against human evidence (is it what
people do?, RF-14). The two are separate filters and both are recorded. A verdict here never
removes a rule from RF-14:

| | Matches human evidence (RF-14) | Does not |
| --- | --- | --- |
| **Helps in the simulation (RF-18)** | The goal: promote | A stall-removing heuristic, not a model of people: stays staged, labelled as such |
| **Does not help** | A finding: record why (the translation? the ORCA layer? the measure?) | Dropped |

    python run_experiment.py configs/rule_set_evaluation/rf18_round1.yaml --plan
    python run_experiment.py configs/rule_set_evaluation/rf18_round1.yaml
    python -m negsim.rules.benchmark --database runs/rf18_round1/rule_db_staging --ruleset all_runnable \
        --people-from configs/rule_set_evaluation/rf18_round1.yaml --agents 100 1000

Code: `negsim/ruleset_eval/` (`experiment.py`, `measures.py`, `verdicts.py`). No model is called, so
it costs nothing and needs no approval.

## 1. The config

A config says `layer: rule_set_evaluation` and gives:

| Key | Meaning |
| --- | --- |
| `rules` | Each rule switched on in some arm: the staging database it comes `from` and the `version`. Optional `priority` (with a `reason`): see section 2 |
| `left_out` | Rules not run, each with its reason; listed in the report, so that what was left out is counted |
| `arms` | Each a rule set: `rules` (of the ones above), or `database` and `ruleset` of another database (a reference). `judged: false` gives numbers and no verdict (the default for a reference). Plain ORCA is always run and is named `plain` |
| `scenarios` | Each a `name` (each its own), a `scenario` file, optional `scenario_overrides`, a `note`, and `rotate_people` (below). Since issue #112: `population`, `purpose` and `pool` (section 1.1) |
| `baseline`, `seed`, `seeds` | The baseline laid on every run (default `orca_perturbed_v1`), the base seed, and how many paired seeds (seed `seed + 1` to `seed + seeds`) |
| `people` | `ages`, `genders` and core `factors` (a cane, a suitcase, a phone, assertiveness, ...), given to the people in a fixed mix (`negsim.rulegen.replay.mixed_population`), the same for every arm on a seed |
| `alpha` | The sign test's level (0.05) |
| `verdict_rule` | 1 (fixed before round 1's run) or 2 (collisions count separately; the default), section 3 |
| `logging.trajectory_stride` | As for an avoidance run (10); the lane measure reads the trajectory |

### 1.1 Populations and purposes (issue #112, RF-33)

A scenario may take its people from a **population profile** (`population: configs/populations/<name>.yaml`,
`docs/population-profiles.md`) in place of `people`, and must then say its **`purpose`**, which must
be the profile's:

| Purpose | People | Its verdict |
| --- | --- | --- |
| `realistic` | Sourced shares (`singapore_street_v1`), exact on every seed, new people on every seed | **The verdict of record** |
| `stress` | Exaggerated shares (`stress_all_factors_v1`: RF-18's crowd) | Reported beside it, labelled: whether a rule works where it applies. **Never a verdict of record on its own** |

The user's decision of 2026-10-27. Once one scenario says its purpose, every one must. A rule's
`overall` in `summary.json` then comes from its **realistic scenarios only**, with `by_purpose`
beside it (the report's rule table has a column for each). `pool: N` (profiles of quotas only):
a small scenario's people are the first of a crowd of N at exact shares, a new pair on each seed
(exact quotas for two people would give the two largest kinds of person on every seed). With a
profile of quotas, `rotate_people` is refused: every seed already has new people. The summary
records each such scenario's profile (file, hash, limits) and how many people of each kind it had on
each seed. A config without these keys is described, run and judged exactly as before (tested
against RF-18's committed run).

**The user's two decisions after RF-33's first run (2026-10-27):**
- **More seeds where a factor is rare.** A scenario may give its own `seeds` in place of the
  config's; round 1's realistic scenarios have 30, its stress ones 10 (as RF-18). With 10 seeds
  only 9 of 10 agreeing is significant; with 30, 21 of 30 is (p = 0.043).
- **A flag for RF-14.** A rule whose stress verdict is **harms** but whose verdict of record is
  not gets `flag: harms_where_common` in `summary.json` (a column of the report's rule table).
  **[design]** The flag is given by this rule to any rule, not to the cane rule by hand. It
  changes no verdict.

**People.** In a crowd the mix is fixed, as in crowd screening. In a scenario with few people,
`rotate_people: true` gives each seed a window on the mix that moves on by **one** person per seed.
Not by the number of people: the mix gives factors in blocks (a cane to four people in a row), so a
window that jumped by two would only ever pair two people alike, and a rule whose roles are given
by a condition (`rule-format.md`, section 15.2) would never apply.

## 2. The run's own staging database

A run reads one rule database, and rules staged by different experiments live in different ones.
So every chosen rule's versions, up to the one switched on, are **copied byte for byte** into
`runs/<experiment>/rule_db_staging/` (`StagingDatabase.copy_in`), with one rule set per arm of that
database (`StagingDatabase.write_ruleset`). Nothing is edited: a copy whose text differs from its
source is refused, as is another set under a frozen name. The database must load whole before any
run.

**Two rules that clash.** Two rules at one priority that could tell one pair different things are
refused together (`rule-matching.md`, section 4). Translation gives every rule priority 500, so
rules of one encounter can clash. A rule's `priority` in the config settles it: the run's database
gets **one more version** of the rule, the same in every field but `priority` (its canonical form,
which leaves priority out, is unchanged), with the reason in its provenance's `notes`, and that
version is switched on. The staged original is untouched. Which rule wins is a decision, recorded
in the config with its reason.

## 3. What "helps" means (fixed with the user before any run; amended after round 1)

Rule 1 was fixed in `WORK_LOG-74.md` (task 0), before any code or run of issue #74, by the user's
choice; rule 2 amends it (below).

- **Unit:** each arm in each scenario, against plain ORCA on the same seeds and people (paired
  seeds, `baseline.md`, section 6); 10 seeds.
- **Main measure, severe conflicts:** the number of pair interactions at tier T3 or T4 (a near miss,
  a collision or a deadlock while the pair was open; `metrics.md`, section 11.3).
- **Side measures, the cost to the crowd:** throughput (agents arrived per minute of the run) and
  delay per agent (section 4).
- **Gridlock:** a run that ends in deadlock, or at its time limit with people still walking.
- **Better or worse** on a measure only if the **exact two-sided sign test** over the seeds, ties
  dropped, gives p < 0.05: with 10 seeds and no ties, 9 of 10 must agree.
- **Verdicts**, tested in this order (`verdicts.py`):

| Verdict | When |
| --- | --- |
| **not used** | No rule of the arm matched on any seed |
| **harms** | It gridlocks on a seed where plain ORCA did not, or severe conflicts are worse |
| **helps** | Severe conflicts fewer, and throughput and delay not worse |
| **trade-off** | Severe conflicts fewer, but throughput or delay worse |
| **no change** | Anything else (worse throughput or delay alone is no change: only severe conflicts and gridlock harm) |

**Rule 2: collisions count separately** (the user's decision of 2026-10-27, after round 1's run, and
the default since: `verdict_rule: 2`). Rule 1's main measure counts a near miss and a collision
alike (T3 + T4 pairs), so a pair that collides instead of nearly missing is not worse by it; round
1's set 2 had fewer near misses and more collisions on every seed, and rule 1 called it a
trade-off. Under rule 2 an arm **also harms** if **collided pairs** (T4) or **collision episodes**
are worse by the same sign test; everything else is rule 1. Both rules' verdicts are in
`summary.json` (`verdict_by_rule`), and the report shows rule 1's beside rule 2's where they differ.
`alpha` and `verdict_rule` only judge finished runs: changing them re-judges the runs on disk
without running them again.

- **A rule's verdict** in a scenario is that of the arm with the rule alone. **[design]** Its overall
  reading over the scenarios takes, in order: harms anywhere, helps somewhere, a trade-off
  somewhere, no change somewhere, else not used.
- **Lane formation is reported, not judged**: it is about realism, which is RF-14's filter.

## 4. Measures (`measures.py`)

Read back from each finished run folder, so they can be recomputed without running again.

| Measure | How |
| --- | --- |
| Severe conflicts | `outcome.json`, `interaction_outcomes.tiers`: T3 + T4 |
| Collision episodes, near misses | `outcome.json` |
| Throughput | 60 × arrived / the run's simulated time. The run lasts until the last person arrives, so **one person far behind lowers it** even when most arrive sooner; read it with delay |
| Delay per agent | Time to goal minus path length over preferred speed (`config.json`, each agent), mean over those who arrived |
| Lane formation | Two-way flow only. Each agent's mean lateral position on its own left (positive) or right, over the trajectory samples it spends within 10 m of the corridor's middle (**[design]**, where the two groups meet); the share of agents on their left and on their right |
| Rule conflicts | Pairs matched by more than one rule over their life, ambiguous matches, cross-pair conflicts, and plans not started because the person had one in force (`plans_skipped_busy`, `rule-matching.md`, section 7) |
| Uncovered conflicts | Pair interactions at tier T1 or above that no rule matched (rule arms only), grouped by encounter class and tier. A pair's class is the one it spent most of its evaluations in (a pair often forms before it is on a collision course, as `none`), else its class at the start |
| Wall time per step | Measured around each run; indicative only (the machine may be busy). The cost figure of record is the benchmark's (section 6) |

**Uncovered conflicts close the loop:** each frequent kind is proposed as a designed scenario for
a later round of Steps 1 to 4.

## 5. Files

```
runs/<experiment>/
  config.json             the config, the software, the git state, every file copied
  rule_db_staging/        the run's own database (section 2)
  runs/<scenario>/<arm>/<seed>/
    config.json outcome.json   as for any avoidance run (log-schema.md)
    measures.json         every measure of section 4, the run's wall time
    events.jsonl interactions.jsonl pair_interactions.jsonl trajectory.csv   not committed (about 25 MB a crowd run)
  summary.json            per scenario and arm: means, paired seeds, tests, verdict, rule and uncovered conflicts; rule verdicts
  report.md               the same, as tables
```

The runs are deterministic, so the uncommitted logs are rebuilt by running the experiment again
with `--overwrite`. Running again without it resumes: a run whose `measures.json` exists is not run
again. A folder holding runs of another config is refused, except for the numbers of seeds (since
issue #112): a run on a given seed does not depend on how many seeds there are (its people depend on
the seed alone), so more seeds add runs and keep those on disk. Each such change is recorded in the
experiment's `config.json` (`seeds_changed`: when, the commit, from and to); the runs added then
record their own commit in their own `config.json`.

## 6. Rerun after every round, and cost

**After every round**, a round's last issue copies the config under a new `experiment_name`, adds
the round's staged rules and arms (and any new priorities, with reasons), and compares its report
with the previous round's. The per-rule verdicts are what RF-14 and its successors read.

**Cost towards 10,000 agents**: `python -m negsim.rules.benchmark` times plain ORCA against a rule
set step by step in the two-way flow, at any crowd size (issue #28); since issue #74 it takes
`--database`, `--ruleset` and `--people-from`, so that the rule set of record is timed with the
people its rules read.

## 7. Limits

- Two of the three scenarios have two people. Only the two-way flow is a crowd.
- In RF-18's crowd, half the people carry a cane (the mix of crowd screening; 48 of 100), which no
  real crowd does; a rule about canes applies far more often than it would. **The user's decision of
  2026-10-27:** simulate realistic scenarios wherever possible, and keep scenarios with exaggerated
  shares only to test rules that would rarely apply in a normal one, labelled as such. Since issue
  #112 (RF-33) a scenario can do so (section 1.1); round 1 in a realistic crowd is
  `configs/rule_set_evaluation/rf18_round1_realistic.yaml`. The realistic profile's own limits
  (residents only; a cane and a phone from abroad; placeholders) are in `docs/population-profiles.md`.
- A rule reads a cane at any distance; Step 1's agents saw one only within 5 m.
- The verdict is about the simulation, not about people: whether a rule is what people do is
  RF-14's question.
