# Behaviour checks of the rule layer (issues #28 and #32)

Issue #28 asks for rule-following to be compared with "plain ORCA" in the five scenarios of
issue #26, with at least 20 seeds per condition, "reported with numbers and not asserted in
advance". This file reports those numbers and what they show (sections 1 to 5, Appendix A).
Issue #32's checks, two people who meet inside a single-file passage, are section 6 and
Appendix B (`runs/si32_passage_*`).

They are statements about this algorithm, these five seed rules and these parameters.
**None of them is evidence about how people walk.** The seed rules are test fixtures
(`status: test_seed`, `rule_db/README.md`); several parameters are placeholders
(`parameters.md`, `baseline.md`); checking rules against human evidence is the work of a
later sub-issue (SI-6).

Every number here is read from the committed run logs under `runs/si2_*` by
`python -m negsim.rules.report`, whose output is Appendix A; a test
(`tests/test_rules_report.py`) checks that the appendix still matches it line for line.
The numbers in the sections before it are taken from the appendix.

## 1. What was run

| Experiment (`configs/rule_following/`) | Scenario | Factors | Runs |
|---|---|---|---|
| `si2_head_on` | `wide_corridor_head_on` | layout (exactly symmetric; 10 cm offset) × people (no personas; a woman of 25 and a man of 70) × baseline × mode | 320 |
| `si2_keep_left_vs_right` | `wide_corridor_head_on`, exactly symmetric | baseline × rule (`keep_left_head_on` alone; `keep_right_head_on` alone) | 80 |
| `si2_open_crossing` | `open_crossing` | layout (arriving together; agent 1 half a metre later) × baseline × mode | 160 |
| `si2_overtaking` | `overtaking` | layout (directly behind; 5 cm off) × baseline × mode | 160 |
| `si2_bottleneck` | `corridor_to_bottleneck`, arbiter on | flow (opposing; merging) × speeds (equal; agent 0 at 1.10 m/s) × baseline × mode | 320 |
| `si2_bidirectional_flow` | `bidirectional_flow`: fifty agents each way | baseline × mode | 80 |
| `si2_head_on_r5` | as `si2_head_on`, sensing radius 5 m | as `si2_head_on` | 320 |
| `si2_overtaking_r5` | as `si2_overtaking`, sensing radius 5 m | as `si2_overtaking` | 160 |
| `si2_bidirectional_flow_ablation` | as `si2_bidirectional_flow`, primary baseline | `default` without `overtaker_keeps_clear`; without `keep_left_head_on` | 40 |

The last is a follow-up the issue did not ask for (section 3.11); everything else below is
about the first eight.

- **Baseline**: `orca_perturbed_v1` (primary) or `orca_unperturbed_v1` (secondary), both
  frozen (`baseline.md`). **Mode**: `plain`, the baseline alone; or `rules`, the same
  baseline with `directives: {provider: rules, ruleset: default}`, which switches on
  `keep_left_head_on`, `overtaker_keeps_clear`, `single_file_first_arrival` and
  `younger_yields_head_on` (`rule-format.md`, section 10). Nothing else differs between a
  plain condition and its rule condition.
- **20 seeds per condition, 1,600 runs in all**, every one written from a clean tree at
  commit `a4e1ead`. No model was called and nothing was spent.
- **What a seed changes.** Under the perturbed baseline, the perturbation, which is drawn
  from the run's seed. In the two-way flow, also the agents' starting jitter, which moves
  with the repeat. Under the unperturbed baseline nothing else is random, so in the
  two-agent scenarios its 20 seeds give byte-identical trajectories (each table in
  Appendix A lists the conditions where that is so): their "± 0" is the absence of
  randomness, not a measured spread.
- **Plain and rule runs do not share seeds.** A run's seed is the experiment's base seed
  plus its index, so the plain run and the rule run of one repeat draw different
  perturbations. The comparisons below are between two samples of 20, not 20 paired
  differences. The crossing shows how large that seed-to-seed noise is: no seed rule applies
  there, so its plain and rule runs differ only in their seeds (section 3.3).

## 2. How to read the tables

Each row of Appendix A is one condition: its 20 runs, summarised. A spread is
**mean ± standard deviation over the 20 runs**, followed by **[min, max]** when the runs
differ. The metrics are `metrics.md`'s, with its thresholds, unchanged:

| Column | What it is |
|---|---|
| Deadlock runs, collision runs | Runs that ended in deadlock; runs with any overlap of two bodies or of a body and a wall |
| Pairs: avoided / resolved / failed | Every pair interaction, categorised (`metrics.md`, section 9; DD57): `failed` if the two collided or deadlocked, else `resolved` if either was exposed to the other or had a yield event, else `avoided`. Summed over the 20 runs |
| Exposure, all agents | Conflict exposure time (`metrics.md`, section 3), summed over the agents of a run: the time during which ORCA had to change the velocity an agent wanted because of another agent |
| Yield events, near misses | Per run (`metrics.md`, sections 4 and 5) |
| Min separation | The smallest gap between two bodies in the run, in millimetres; negative is an overlap |
| Mean time to goal | Over the agents of a run that arrived; "–" if none did |
| Largest path deviation | The furthest any agent of the run got from the line it meant to walk (issue #26's tables report the same quantity) |
| Backward / hurried episodes | Issue #26's two artefacts (`metrics.md`, section 10), summed over the 20 runs |
| Rules fired | Matches begun, by rule and version, summed over the 20 runs |
| Agent 0 passed | Head-on only: the side agent 0 passed on as it saw it (its largest excursion across its starting heading, more than 5 cm); `none` if it never left its line |

The second table of each experiment says what decided the outcomes (how many pairs had
exposure, a yield, a collision, a deadlock, or were still open at the time limit) and what
the matching policy did: evaluations by outcome, matches ended by reason, formation
mismatches (each agent's own evaluation against the shared snapshot when a pair forms,
`rule-matching.md`, section 1, check (b); 0 means they agreed), and cross-pair conflicts.

## 3. Results

### 3.1 Head-on in a corridor wide enough to pass (`si2_head_on`)

Two agents start 16 m apart in a corridor 1.75 m wide; alone, each would arrive in 12.2 s.
The rules that can apply: `keep_left_head_on` (priority 10; the corridor between them,
1.75 m, is at least 1.0 m) and, with the two personas, whose ages differ by 45 years,
`younger_yields_head_on` (priority 20; once the time to collision is 6 s or less).

The exactly symmetric layout without personas:

| Baseline | Mode | Deadlocks | Mean time to goal (s) | Exposure, both agents (s) | Min separation (mm) | Agent 0 passed |
|---|---|---|---|---|---|---|
| unperturbed | plain | 20 of 20, at 20.4 s | – | 34.8 | 21.1 | `none` 20 |
| unperturbed | rules | 0 | 12.20 | 6.4 | 4.08 | left 20 |
| perturbed | plain | 0 | 12.32 ± 0.04 [12.30, 12.40] | 6.6 ± 0.1 | 10.1 ± 4.8 [0.09, 15.8] | left 9, right 11 |
| perturbed | rules | 0 | 12.20 | 6.4 | 4.08 ± 0.01 | left 20 |

- **Against the secondary baseline, `keep_left_head_on` is the difference between arriving
  and not.** Unperturbed ORCA deadlocks in 20 of 20 runs, as issue #26 found; with the rule
  both arrive at 12.2 s, as if alone, passing right shoulder to right shoulder.
- **Against the primary baseline there is no deadlock to remove.** The perturbation breaks
  the symmetry and plain ORCA passes on whichever side the noise picks (left in 9 runs,
  right in 11), a little late (12.32 s). The rule fixes the side (left in 20) and the time
  (12.20 s in every run), and the pair passes closer (4.08 mm, against 10.1 mm and a spread
  from 0.09 to 15.8 mm): both commit to a side when they first see each other, 12.4 m apart,
  instead of letting one emerge from the noise.
- **With the 10 cm offset plain ORCA already passes on the nearer side**, left in 20 of 20,
  under both baselines, and `keep_left_head_on` agrees with it: nothing changes but the
  smallest gap, 5.14 mm without the rule and 7.74 mm with it.
- **`younger_yields_head_on` outranks `keep_left_head_on`** whenever the woman of 25 and the
  man of 70 meet (20 of 20 rule runs in each layout and baseline). One rule per pair
  (`rule-matching.md`, section 5): the pair gets that rule's shares, 1.0 for the younger and
  0 for the older, **and no side**. What the younger then does depends on the baseline:
  - *unperturbed, exactly symmetric*: **she walks backwards** down the corridor in front of
    him, as issue #26 found for shares (1.0, 0.0) with no side: a backward episode in 20 of
    20 runs, a largest deviation of 0.700 m (the retreat), arrival at 24.9 s against his
    12.2 s, one yield event per run;
  - *perturbed, exactly symmetric*: **she steps aside** the whole half metre (largest
    deviation 0.506 ± 0.004 m), on a side the noise picks (left 14, right 6), and he walks
    his line (it moves him by less than 0.1 mm);
  - *10 cm offset*, either baseline: she steps aside 0.402 m to the nearer side, as issue
    #26's (1.0, 0.0) offset run did.

  **The same rule produces a sidestep or a retreat depending on a perturbation of 1e-4 m/s.**
  A rule that sets a share but no side is underspecified in an exactly symmetric meeting.
- **No pair is `avoided`.** Every pair is `resolved` (exposure in all of them), apart from the
  40 deadlocked ones, which are `failed`. Section 4 comes back to this.

### 3.2 Keep left against keep right (`si2_keep_left_vs_right`)

The exactly symmetric head-on, each rule switched on alone (the two cannot be on together:
`rule-matching.md`, section 4).

**Every number is the same for the two rules except the side**: under both baselines, both
arrive at 12.20 s, exposure 6.4 s, smallest gap 4.08 mm, largest deviation 0.251 to 0.252 m,
no yield; agent 0 passes left in 20 of 20 runs under `keep_left_head_on` and right in 20 of
20 under `keep_right_head_on`. In this simulator the two conventions are mirror images: the
scenario, ORCA and the baseline's tie-break are symmetric under reflection. Which convention
people in a given place follow, and whether it matters to them, is not something these runs
can say.

### 3.3 Crossing (`si2_open_crossing`)

No seed rule is written for a crossing, so the rule runs evaluate the rules (every step, as
nothing holds: 2,420 to 5,600 `no_rule_matched` per condition), match nothing, and must
behave as the plain runs do.

- **They do.** Under the secondary baseline the plain and rule runs are byte-identical
  (trajectories and events), including the deadlock of the exactly symmetric crossing (20 of
  20 in each; issue #26 found it):
  the default rule set does nothing about a crossing deadlock, because `keep_left_head_on`
  is written for head-on meetings.
- **Under the primary baseline the differences are the seed noise.** Arriving together,
  plain against rules: exposure 6.8 ± 0.0 against 6.8 ± 0.1 s, time to goal 12.30 against
  12.31 ± 0.02 s, smallest gap 5.27 ± 1.45 [2.55, 7.77] against 3.85 ± 2.29 [0.005, 7.81] mm.
  These come from runs that differ only in their seeds. So under the perturbed baseline a
  difference of a millimetre or two in the mean smallest gap, or of a few hundredths of a
  second, is not by itself the effect of a rule.

### 3.4 Overtaking (`si2_overtaking`)

Agent 0 prefers 1.48 m/s and starts 4 m behind agent 1, which prefers 1.10 m/s; alone they
would arrive in 26.9 s and 32.6 s. `overtaker_keeps_clear` gives the faster of the two (by
present speed, ties within 0.05 m/s) the whole share and a side, left, and the slower none.

| Layout | Baseline | Plain: time to goal 0 / 1 (s) | Rules: time to goal 0 / 1 (s) | Hurried episodes, plain / rules |
|---|---|---|---|---|
| Directly behind | unperturbed | 29.50 / 29.20 (no overtaking) | 27.40 / 32.60 | 20 / 0 |
| Directly behind | perturbed | 27.46 / 31.96 | 27.40 / 32.60 | 20 / 0 |
| 5 cm off | unperturbed | 27.20 / 32.40 | 27.30 / 32.60 | 40 / 0 |
| 5 cm off | perturbed | 27.20 / 32.40 | 27.30 / 32.60 | 40 / 0 |

(Per-agent times are means over 20 runs, from the experiment's `summary.csv`; their standard
deviation is at most 0.05 s.)

- **The slower walker is never pushed along with the rule**: it arrives at 32.60 s, its time
  alone, in all 80 rule runs, with no hurried episode, against 120 episodes in the 80 plain
  runs. It stays on its line (it moves by at most 0.21 mm).
- **The overtaker does all of the stepping aside**: a largest deviation of 0.502 m directly
  behind and 0.452 m 5 cm off. Plain ORCA, where it overtakes, has both step aside (largest
  0.273 and 0.239 m). With the rule the overtaker arrives no later than under the primary
  baseline's plain ORCA (27.40 against 27.46 s).
- **Without the rule, under the secondary baseline, the faster walker never overtakes**: the
  two walk together at 1.29 m/s, 0.5 mm apart, from 13.4 s to 29.1 s (issue #26's "hurried
  along"). The primary baseline's perturbation lets it go round (27.46 s), but the slower one
  is still hurried (31.96 s instead of 32.6 s).
- **The overtaker brushes past.** The smallest gap is 7 to 10 µm in every rule run, during
  the pass. ORCA keeps the bodies apart and no more; a rule that wants room would set a
  `clearance_margin`.
- **A shorter mean time to goal is not better here.** It is 29.71 s without the rule and
  30.00 s with it (primary baseline, directly behind), only because plain ORCA hurries the
  slower walker.

### 3.5 Into a single-file segment (`si2_bottleneck`)

A corridor 1.75 m wide narrows to 0.8 m for 4 m, so that only one agent fits; the arbiter of
issue #24 (Strategy 1: whoever would get there sooner leads) is on in every run.
`single_file_first_arrival` makes the agent with the shorter time to the segment the leader
(ties within 0.5 s), and keeps its order until the pair interaction ends.

- **Who goes first never depends on the rule**, because the rule says what Strategy 1
  already does. Where every plain run of a condition has the same leader, so does every rule
  run. Where the noise decides a tie (opposing, equal speeds, primary baseline), it decides
  it in both: agent 0 first in 12 plain runs and 10 rule runs, agent 1 in 8 and 10. Every
  metric agrees within the seed noise.
- **With equal speeds the rule "fires" but decides nothing.** When the pair forms, the two
  times to the segment tie, and the rule does not apply (`no_match`). The arbiter decides
  by its own rule, on that same step (at 2.2 s opposing, at the start merging), and holds
  the follower back. On the next step the rule, evaluated again because nothing holds the
  pair, matches on times to the segment that the arbiter's slowdown has already changed (7.8
  s for the follower against 3.1 s, in the first opposing run) and names the leader the
  arbiter chose. That happens in all 80 equal-speed rule runs; the
  arbiter's order (`role_source: strategy1` in every handoff) is never replaced. **A rule
  that reads a quantity the arbiter's decision changes can ratify that decision after the
  fact.** The count of matches overstates what the rule did.
- **With agent 0 slower** (1.10 m/s), agent 1 reaches the segment about a second sooner, the
  rule matches when the pair forms, and the arbiter takes its order from it
  (`role_source: negotiated` in all 80 such rule runs, `strategy1` in all 80 plain runs): the
  same leader, now named by the rule.
- **The only `avoided` pairs of all the two-agent runs** are here: merging, with agent 0
  slower, 20 of 20 in each of the four conditions. Agent 1 is through first and the two never
  come into conflict.

### 3.6 Fifty each way (`si2_bidirectional_flow`)

Fifty agents walk each way along a corridor 4 m wide and 50 m long, from a lattice 1 m
apart, each moved by up to 0.1 m (a jitter that changes with the repeat). Alone, the mean
time to goal would be 33.5 s and the last agent would arrive at 38.4 s (issue #26). Two seed
rules apply: `keep_left_head_on` between agents walking opposite ways, and
`overtaker_keeps_clear` between agents walking the same way when one is catching up. The
logs are thinned here (`trajectory_stride: 100`, no per-interaction files): each outcome
counts every pair, match and artefact, but which rule held which pair is not in the committed
logs.

| Baseline | Mode | Last arrival (s) | Mean time to goal (s) | Agents later than 60 s, per run | Overlap episodes, per run | Deepest overlap, per run (mm) | Agent-steps with no allowed velocity, per run |
|---|---|---|---|---|---|---|---|
| perturbed | plain | 83.4 ± 10.2 [68.4, 114.3] | 38.67 ± 5.95 [33.99, 54.46] | 6.8 ± 10.9 [1, 48]; 136 in all | 234 ± 217 [48, 842] | 32 ± 26 [6, 90] | 4,894 ± 3,530 [1,654, 14,863] |
| perturbed | rules | 46.9 ± 10.6 [40.8, 84.2] | 35.87 ± 0.73 [34.92, 37.57] | 0.1 ± 0.3 [0, 1]; 2 in all | 107 ± 29 [63, 177] | 201 ± 101 [48, 456] | 2,616 ± 356 [2,042, 3,406] |
| unperturbed | plain | 77.5 ± 11.5 [48.6, 98.7], over the 19 runs that finished | 39.03 ± 6.53 [34.04, 56.62] | 6.7 ± 10.8 [0, 41]; 134 in all | 249 ± 234 [46, 837] | 33 ± 26 [8, 98] | 5,240 ± 4,006 [1,665, 16,167] |
| unperturbed | rules | 44.9 ± 3.9 [41.2, 57.7] | 35.98 ± 0.96 [34.73, 38.31] | 0 | 111 ± 47 [45, 246] | 191 ± 100 [32, 373] | 2,644 ± 526 [1,944, 3,964] |

(Mean ± standard deviation [min, max] over the 20 runs of each condition, from each run's
`outcome.json`: `makespan_s`; `totals.mean_time_to_goal_s`, over the agents that arrived;
the arrival times above 60 s, or none by the run's limit of 120 s; `collisions.agent_agent`;
`collisions.max_overlap_m`; `totals.fallback_agent_steps`.)

- **With the rules the crowd clears sooner and far more predictably.** Under the primary
  baseline the last agent arrives at 46.9 s instead of 83.4 s; the mean time to goal, 35.9 s,
  is 2.4 s more than walking alone, against 5.2 s more, and its spread across seeds falls from
  ± 5.95 to ± 0.73 s. Agents more than 60 s on the way: 2 in 20 rule runs, 136 in 20 plain
  runs. Under the secondary baseline one plain run jams: at its 120 s limit 8 agents are still
  in the corridor. That is not a deadlock by the test of `metrics.md`, which needs every
  agent nearly still. No rule run jams.
- **Fewer collisions of every kind, except in depth.** Per run, overlap episodes fall from
  234 to 107, near misses from 830 to 399, agent-steps with no allowed velocity from 4,894 to
  2,616; over the 20 runs, failed pairs fall from 3,619 to 1,674 (primary baseline; the
  secondary is alike). **But the deepest overlap of a run is about six times deeper**: 201 ±
  101 mm, up to 456 mm, against 32 ± 26 mm, up to 90 mm. Two discs of radius 250 mm that
  overlap by 200 mm are not a near miss: one has walked well into the other. No rule asks for
  that; it is what ORCA does when this crowd follows these rules.
- **Where the overlaps happen.** One rule run (`021_perturbed_rules_r1`) was run again
  outside the repository with every step and every pair logged, and reproduced the committed
  run exactly. Of its 128 overlap episodes, 60 began in a pair held by
  `overtaker_keeps_clear`, 10 in a pair held by `keep_left_head_on`, and 58 in a pair that no
  rule held; 121 began on a step on which one of the two agents had no velocity that met all
  its constraints, the case ORCA's paper gives no guarantee for, to which issue #26 traced
  every overlap. The two deepest (240 and 238 mm) began in a pair under no rule and in a pair
  under `overtaker_keeps_clear`, both on such steps. So the depth is not confined to the pairs
  a rule holds, and these runs alone do not say which rule, if either, is behind it (open
  question Q10). The follow-up of section 3.11 does: it comes with `overtaker_keeps_clear`.
- **More pairs register some exposure, for less exposure in all.** Pairs with exposure:
  55,227 with the rules, against 40,544 without; total exposure per run 984 ± 83 s against
  1,321 ± 707 s (primary baseline). So in the flow the categories do move, and away from
  `avoided` (29,011 pairs against 40,460): one more sign that `avoided` does not measure how
  well a crowd gets on (section 4).
- **What the rules did.** About 2,470 matches of `keep_left_head_on` and 4,500 of
  `overtaker_keeps_clear` per run (98,825 and 180,065 over the 40 rule runs), all but 1% ending
  when the pair had passed. No ambiguous match, no cross-pair conflict (the two rules set only
  `left` or no side, and neither sets a speed or an order, so nothing can contradict), and no
  formation mismatch.

### 3.7 Sensitivity: a sensing radius of 5 m (`si2_head_on_r5`, `si2_overtaking_r5`)

The issue asks how the avoided and resolved counts change.

- **They do not change, in any condition.** Head-on: 0 avoided, 20 resolved and 0 failed in
  every condition at both radii, except the exactly symmetric plain runs under the secondary
  baseline, which deadlock (20 failed) at both radii. Overtaking: 0 / 20 / 0 in every
  condition at both radii.
- **In the head-on, the radius changes when ORCA starts steering and how hard.** At 5 m the
  two see each other later, so ORCA steers later and harder: with `keep_left_head_on`,
  exposure 3.8 s instead of 6.4 s and a smallest gap of 5.84 mm instead of 4.08 mm, with
  the same 12.20 s. The secondary baseline's deadlock comes at 20.0 s instead of 20.4 s, and
  the rule removes it at both radii.
- **At 5 m, plain perturbed ORCA loses most of its spread** (12.20 s and 5.84 ± 0.01 mm in
  every run; still left in 11, right in 9), and `keep_left_head_on` then changes nothing but
  the side. At 12.5 m it also made the pass quicker (section 3.1).
- **`younger_yields_head_on` behaves as at 12.5 m**: a retreat in all 20 unperturbed
  symmetric runs, a sidestep (largest deviation 0.504 m) on a side the noise picks under the
  perturbed baseline.
- **Overtaking is unchanged, as it must be**: the two start 4 m apart, inside both radii,
  so they perceive each other from the first step either way.

### 3.8 Issue #26's two artefacts, rule runs against baseline runs

Counted in every run as `metrics.md`, section 10 defines them (thresholds with no source),
and not fixed.

| Episodes | Walking backwards | Being hurried along |
|---|---|---|
| Two-agent scenarios, plain runs (720) | 0 | 240 |
| Two-agent scenarios, rule runs (800) | 40 | 0 |
| Two-way flow, plain runs (40) | 688 | 823 |
| Two-way flow, rule runs (40) | 179 | 561 |

- **Between two agents, walking backwards happens only under `younger_yields_head_on`**,
  exactly head-on, under the unperturbed baseline: one episode in each of its 20 runs, at
  either radius. Never in a plain run, and never under the primary baseline (section 3.1).
- **Between two agents, being hurried along happens only in the overtaking plain runs**: one
  episode per run directly behind, two per run 5 cm off, under both baselines and at both
  radii (240 in all), and **never with `overtaker_keeps_clear`** (section 3.4).
- **In the flow both are frequent, and fewer with the rules**: walking backwards 688 against
  179 episodes, hurried 823 against 561, both baselines together. `metrics.md`, section 10,
  warns that "hurried" can over-count in a crowd, where a neighbour behind need not be the
  cause.

So the rules remove being hurried along where `overtaker_keeps_clear` applies to two agents,
and produce walking backwards where `younger_yields_head_on` gives a share without a side in
exact symmetry.

### 3.9 Which rules fired, and how often

| Rule | Where it fired | Matches begun |
|---|---|---|
| `keep_left_head_on` | every head-on rule run without personas (80, and 80 at 5 m), every `keep_left` run of the comparison (40), every flow rule run (40) | one per two-agent run, 200 in all; 98,825 in the flow |
| `keep_right_head_on` | every `keep_right` run of the comparison (40) | 40 |
| `younger_yields_head_on` | every head-on rule run with the two personas (80, and 80 at 5 m), always in place of `keep_left_head_on` | 160 |
| `overtaker_keeps_clear` | every overtaking rule run (80, and 80 at 5 m), every flow rule run (40) | one per two-agent run, 160 in all; 180,065 in the flow |
| `single_file_first_arrival` | every bottleneck rule run (160) | 160: deciding the order in the 80 with unequal speeds, ratifying the arbiter's in the 80 with equal speeds (section 3.5) |

No rule fired in the crossing, for which none is written. **Across all 1,600 runs there was
no `ambiguous_match`, no `cross_pair_conflict`, and no formation mismatch in 271,189 checks**:
every time a pair formed, each agent's own evaluation of the rules, from its own perception
record, agreed with the shared snapshot (`rule-matching.md`, section 1).

### 3.10 What following rules costs per step (benchmark)

`python -m negsim.rules.benchmark` builds the flow as issue #26's benchmark does (the same
starting density at every size, the two crowds 6 m apart), lays the primary baseline on it
(40 neighbours, 12.5 m, the perturbation), and steps it 100 times under plain ORCA and with
the `default` rule set, in turn, three times each. Nothing is logged during the timing. One
process, one thread, pure Python 3.13.3, on the laptop of issue #26 (AMD Ryzen 5 7535HS,
Windows 11), with nothing else running, from a clean tree at `3a9bdff`
(`runs/si2_benchmark/benchmark.json`). A measurement, not a pass mark.

| Agents | Plain, ms per step | With rules, ms per step | Added | Inside the rule provider, ms per step | Its share of a rule step | Open pairs per step | Evaluations per step |
|---|---|---|---|---|---|---|---|
| 100 | 52.1 (51.8, 52.1, 56.6) | 120.6 (118.2, 120.6, 121.4) | 68.5 ms, × 2.3 | 62.7 (60.2, 62.7, 63.3) | 52% | about 3,200 | 1,850 |
| 1,000 | 513.5 (511.5, 513.5, 535.8) | 1,531.0 (1,519.8, 1,531.0, 1,546.2) | 1,017.5 ms, × 3.0 | 1,017.4 (991.7, 1,017.4, 1,021.2) | 66% | about 25,000 | 19,600 |

(The median of three repeats, each the mean over 100 steps, with the three in brackets.
Open pairs and evaluations are those of the first rule repeat.)

- **Following the rules costs 2.3 times the plain step at 100 agents and 3.0 times at
  1,000**, and the time added is the provider's own: at 1,000 agents, 1,017 ms of the 1,018 ms.
- **Where it goes.** A profile of 150 steps of the shipped flow (100 agents, primary
  baseline, `default`; run outside the repository) puts 45.5 s of its 59.9 s in the matching
  policy, and 23.5 s of those in one thing: measuring the corridor width between two agents,
  by ray casts every 0.25 m, for each snapshot. Which pairs need a snapshot again and again
  is plain from the fully logged run of section 3.6: of its 179,493 evaluations that tried a
  rule, 171,986 (96%) were same-direction pairs classed as overtaking whose speeds were within
  0.05 m/s of each other, so that `overtaker_keeps_clear` did not apply and, nothing holding
  them, they were evaluated again on the next step (DD53: "on every step while no rule
  holds"). Another 584,551 evaluations had no rule to try (almost all of them pairs not
  approaching each other) and cost almost nothing.
- **The baseline itself costs more than issue #26's configuration**: plain ORCA here takes
  52 and 514 ms per step, against 12.5 and 148 ms in issue #26's benchmark, which used the
  scenario's own 10 neighbours instead of the baseline's 40 `[placeholder]`.
- **For the project's 10,000-agent goal**, a rule step at 1,000 agents already takes 1.5 s
  for 0.1 s of simulated time. Performance work is not part of this issue; the profile says
  where it would start: the corridor width is measured again for the same pair on every
  step, and pairs that tie are evaluated again although nothing about them has changed
  (open question Q11).

### 3.11 Follow-up: the flow with one rule left out (`si2_bidirectional_flow_ablation`)

**Not asked for by the issue.** Section 3.6 found the deepest overlaps about six times deeper
with the `default` rule set, and could not say which rule, if either, they come with (Q10).
Two rules act in the flow, so this experiment runs it on the primary baseline with each of
them left out in turn, 20 seeds each, from a clean tree at `3a9bdff`. The first level reuses
the seeds and starting positions of section 3.6's perturbed rule runs, so the two can be
compared repeat by repeat; the second level's seeds follow on.

| Rules on | Runs | Last arrival (s) | Mean time to goal (s) | Agents later than 60 s, or never, in all | Overlap episodes, per run | Deepest overlap, per run (mm) | Agent-steps with no allowed velocity, per run | Near misses, per run |
|---|---|---|---|---|---|---|---|---|
| none: plain ORCA (section 3.6) | 20 | 83.4 ± 10.2 [68.4, 114.3] | 38.67 ± 5.95 [33.99, 54.46] | 136 | 234 ± 217 [48, 842] | 32 ± 26 [6, 90] | 4,894 ± 3,530 [1,654, 14,863] | 830 ± 104 [636, 1,058] |
| both: `default` (section 3.6) | 20 | 46.9 ± 10.6 [40.8, 84.2] | 35.87 ± 0.73 [34.92, 37.57] | 2 | 107 ± 29 [63, 177] | 201 ± 101 [48, 456] | 2,616 ± 356 [2,042, 3,406] | 399 ± 36 [359, 514] |
| `keep_left_head_on` alone | 20 | 45.5 ± 13.9 [39.1, 83.0] | 34.98 ± 1.03 [34.48, 38.56] | 4 | 210 ± 46 [169, 325] | 54 ± 16 [29, 88] | 4,057 ± 381 [3,447, 5,194] | 437 ± 42 [399, 565] |
| `overtaker_keeps_clear` alone | 20 | 15 runs end at the 120 s limit; the other 5 at 67.4 to 89.5 | 53.12 ± 14.42 [36.58, 99.92], of those that arrive | 1,381 (1,064 never arrive) | 2,190 ± 1,133 [325, 3,722] | 306 ± 56 [146, 439] | 36,105 ± 18,800 [5,635, 59,968] | 1,312 ± 267 [733, 1,690] |

(Read from the runs' `outcome.json` as in section 3.6. The full tables are in Appendix A.)

- **The deep overlaps come with `overtaker_keeps_clear`.** With `keep_left_head_on` alone the
  deepest overlap of a run is 54 ± 16 mm, near plain ORCA's 32 mm and far from the 201 mm of
  the two rules together. On the same seeds and starting positions it is shallower than with
  both rules in 19 of the 20 repeats.
- **`overtaker_keeps_clear` alone gridlocks the flow.** In 15 of its 20 runs agents are still
  in the corridor at the 120 s limit (1,064 of the 2,000 never arrive), with thousands of
  overlap episodes, overlaps up to 439 mm, and about seven times plain ORCA's agent-steps with
  no allowed velocity. It is the only condition of all the runs that does worse than plain
  ORCA on every count in the table.
- **`keep_left_head_on` is what clears the flow.** Alone it clears it as fast as the two rules
  together (mean time to goal 34.98 ± 1.03 s, against 35.87 ± 0.73 s), with about as many
  overlap episodes as plain ORCA (210 against 234 per run) and overlaps a little deeper than
  plain ORCA's (54 against 32 mm), far shallower than with both rules. Added to it, the
  overtaking rule halves the overlap episodes and deepens the worst.
- **A likely mechanism, not tested here.** `overtaker_keeps_clear` gives the agent in front a
  share of 0 toward the one catching up: it makes no room at all, and the one behind must
  find all of it. In a dense crowd the one behind often has no velocity that satisfies every
  neighbour; ORCA then takes the least bad one, with no guarantee (issue #26), and nothing on
  the other side gives way. The counts of agent-steps with no allowed velocity are
  consistent with that. `keep_left_head_on` leaves the shares at 0.5 each.
- **What it means for rules.** A rule that hands one agent all the avoiding (shares 1 and 0)
  meets the issue's consistency check (the shares sum to 1, which is ORCA's condition for a
  pair) and works for two agents (section 3.4); in a dense crowd it gridlocks the flow on its
  own and deepens the overlaps alongside keep-left. The check guarantees nothing on steps with
  no allowed velocity, which a dense crowd has thousands of.

## 4. What the numbers say about the measures themselves

**The outcome categories hardly move.** Across the 1,520 two-agent runs, the only pairs whose
category a rule changes are deadlocks becoming `resolved` (40 head-on pairs at each radius).
Every other pair is `resolved` with or without rules, because two agents on a collision
course always come within ORCA's 3 s horizon, which counts as exposure, even when a rule
has them pass with no loss of time. So `avoided` / `resolved` / `failed` separates
deadlocked from not deadlocked, and the rest is carried by the continuous metrics: exposure,
the smallest gap, times, deviations, the side taken, who leads. In the flow the categories do
move, but toward fewer `avoided` pairs for a crowd that clears much sooner (section 3.6).
For `avoided` to mean
"settled early" rather than "never on a collision course", it would need a threshold on how
much an agent's velocity was changed, or on the time to collision. That is open question
Q8 of `WORK_LOG-28.md`; the definitions are the issue's and #26's, and are not changed here.

**Under the perturbed baseline, exposure counts changes the size of the perturbation.** An
agent that a rule gives a share of 0 takes none of the avoiding, so ORCA keeps its velocity
exactly on the edge of what the pair allows. The perturbation, up to 1e-4 m/s, pushes the
velocity it wants across that edge on some steps, and ORCA pulls it back; exposure counts
any change above 1e-6 m/s (`metrics.md`, section 3), so those steps count. The
agent with share 0, in every run of the conditions that have one:

| Condition | Its exposure, perturbed (s) | Its exposure, unperturbed (s) | Its largest deviation, perturbed | Its largest logged change of velocity, perturbed |
|---|---|---|---|---|
| Head-on, symmetric, `younger_yields_head_on` | 1.49 ± 0.13 | 0 | 0.06 mm | 0.0001 m/s |
| Head-on, 10 cm offset, `younger_yields_head_on` | 2.88 ± 0.14 | 0 | 0.29 mm | 0.0003 m/s |
| Overtaking, directly behind, `overtaker_keeps_clear` | 3.67 ± 0.21 | 0 | 0.21 mm | 0.0002 m/s |
| Overtaking, 5 cm off, `overtaker_keeps_clear` | 3.61 ± 0.22 | 0 | 0.21 mm | 0.0002 m/s |

(From the 20 runs of each condition; the change of velocity is read from the logged
trajectory rows, every tenth step.) So under the primary baseline part of the exposure in
these conditions is the perturbation, not avoidance. A threshold above the perturbation, such
as 1e-3 m/s, would remove it; that is a change to a metric of issue #26 and is left as open
question Q7.

## 5. What these checks do not show

- Anything about people. The rules are test fixtures; the walking speed and corridor come
  from France, the body radius from Japan, none of it from Singapore (`parameters.md`); the
  neighbour limit and the sensing radii are placeholders (`baseline.md`).
- Rules under imperfect or delayed perception: the shared snapshot assumes perception is
  perfect and simultaneous (`rule-matching.md`, section 1).
- A crossing rule (none is written), or three or more agents ordered at one segment (out of
  scope; the arbiter works pair by pair).
- Paired comparisons: plain and rule runs do not share seeds (section 1).

## 6. Issue #32: two people who meet inside a single-file passage

Issue #32 asks for the arbiter's fallback, the seed rule `passage_shorter_backs_out` and plain
ORCA to be compared in its two new scenarios, over at least 20 seeds, reporting deadlocks,
time to clear, total backing distance and makespan, "whatever happens is a result". As in
sections 1 to 5, these are statements about this simulator, one seed rule that is a test
fixture (`rule_db/README.md`) and these parameters (`parameters.md`; the passage's width and
length are placeholders, the backing speeds one small cited sample), **not evidence about
people**. Every number below is in Appendix B, generated from the committed logs under
`runs/si32_passage_*` by `python -m negsim.rules.report`.

### 6.1 What was run

| Experiment (`configs/rule_following/`) | Scenario | Factors | Runs |
|---|---|---|---|
| `si32_passage_meet_middle` | `passage_meet_middle_v1`: two pedestrians, a passage 0.8 m wide and 4 m long, the two placed 0.1 m apart inside it | travelled (symmetric: 1.7 m each; asymmetric: agent 0 2.7 m, agent 1 0.7 m) × start (rest; walking) × mode (`arbiter`, `seed_rule`, `orca_only`) | 240 |
| `si32_passage_meet_with_speeds` | `passage_meet_with_speeds_v1`: as above, but agent 1 walks at 1.10 m/s (at most 1.4) and backs at 0.43 m/s, agent 0 backs at 0.92 m/s | travelled (asymmetric: agent 0 2.0 m, agent 1 1.4 m; symmetric: 1.7 m each) × start × mode (the three, and `time_optimal`) | 320 |

- **Modes.** `arbiter`: the primary baseline as it is, plain ORCA with the arbiter's fallback
  (`derivations.md`, section 17.1). `seed_rule`: the seed rule alone (`directives: {provider:
  rules, enable: {passage_shorter_backs_out: 1}}`, no rule set), with the arbiter as its
  fallback, which decides when the rule ties (distances walked in within 0.1 m of each other).
  `orca_only`: plain ORCA with the arbiter switched off. `time_optimal`, a reference no rule
  can state: agent 0 told to back up by a static directive. With these speeds, backing out
  agent 0 is quicker (`derivations.md`, section 18: x / v_back is 2.0 / 0.92 = 2.2 s against
  1.4 / 0.43 = 3.3 s, and 1.85 s against 3.95 s at equal distances), but a rule cannot read a
  backing speed: nobody can see one.
- **Start.** `rest`: the scenario's default, the two standing face to face (`start_speed: 0`);
  `walking`: each walking toward the other at its preferred speed when the run starts
  (`start_speed: preferred`). Open question Q2 of `WORK_LOG-32.md`.
- **20 paired seeds per condition**, 560 runs, the primary baseline (`orca_perturbed_v1`), every
  run written from a clean tree at commit `d57e854`. Unlike sections 1 to 5, the seeds are
  **paired** (issue #30's default): the conditions of one repeat share a seed, so a condition's
  20 runs and another's draw the same perturbations. The unperturbed baseline is not run: its
  20 seeds would be 20 copies of one run. No model was called and nothing was spent.

### 6.2 How to read the tables

Each row of Appendix B is one condition over its 20 runs; a spread is mean ± standard
deviation [min, max], as in section 2. "(in n)" after a spread means only n of the 20 runs had
the value.

| Column | What it is |
|---|---|
| Ended | How the runs ended: `completed` (both arrived), `deadlock` (`metrics.md`, section 7), `timeout` (60 s), `collision` |
| Out first, Backed out | Who came out of the passage first at its far end (`first_out`, `log-schema.md`); who made a back-up manoeuvre (`derivations.md`, section 17) |
| First out, Both out | **Time to clear**, read two ways: when the first of the two came out of the passage at its far end (the meeting is over), and when the second did (the passage is clear of both). A time is counted from the start of the run |
| Backing, intentional / artefact / both | How far the back-up manoeuvres moved the backer backwards; how far issue #26's walking-backwards artefact moved anyone backwards, within its episodes (`metrics.md`, section 10); and their sum. Neither is ever counted as the other (DD98) |
| Makespan | When the second of the two arrived; "–" if either did not |
| Min separation | The smallest gap between the two bodies, in millimetres. "−0.0" is a gap that rounds to zero from below at the log's six decimals (an overlap under a micrometre, which is not a collision) |

The second table says what decided each condition: the rule matches begun, the handoffs (to
the arbiter, to a back-up manoeuvre, back to ORCA), when the manoeuvres began, how they ended,
their backing and waiting times, and the artefacts' episodes.

### 6.3 Results

**From rest, the arbiter's fallback never gets the two through.** In all 80 runs that start at
rest under `arbiter`, neither comes out: 28 deadlocks and 12 timeouts in the equal-speed
scenario, 24 and 16 with the slow backer. The leader may not close in faster than it already
does, and nothing pushes a follower that stands in front of a standing leader
(`derivations.md`, section 17.1). Plain ORCA without the arbiter deadlocks too: all 40 runs at
equal speeds, and 32 deadlocks and 8 timeouts with the slow backer.

**Walking, the arbiter's fallback gets them through by the artefact.** In all 80 walking
`arbiter` runs the one further in (or agent 0, on a tie) comes out first, and in every one of
them agent 1, the follower, has exactly one walking-backwards episode: 2.18 m when the two have
walked in equally far (in both scenarios), 1.21 m with agent 0 2.0 m further in, and 1.85 m in
the slow backer's own layout. Averaged over its episode, the follower moves backwards at 0.95
to 1.09 m/s (the mean distance over the mean backward time); for the slow backer that is more than twice
its cited backing speed of 0.43 m/s, and close to its walking speed. Nobody chose that speed:
it is what ORCA does to a follower that the arbiter holds to speed 0 and gives all of the
avoiding (share 1), in a passage it cannot step aside in (`derivations.md`, section 17.1). In
every walking layout it is the soonest to the first out (1.08 to 1.80 s), and it has the
shortest makespan in all but one (with the slow backer at equal distances, `time_optimal`'s
13.47 s beats its 13.60 s). It is not a decision anyone takes.

**The seed rule gets the two through in all 160 of its runs, from rest and walking, with no
collision**, by intentional backing at the cited speeds. Who backs out: agent 1 in every run,
the one that has walked less far in. On a tie (equal distances) the arbiter takes the pair
first, and the rule matches only once the arbiter's leader has crept far enough for the
distances to differ by more than 0.1 m: from rest, the manoeuvre began after 1.87 s on average
(1.20 to 2.30 s) in both scenarios; walking, after one step.

**Time to clear and makespan, the seed rule against the arbiter's way (walking, equal
speeds).** The rule is slower by 0.70 s to the first out (2.50 against 1.80 s) on the tie and
by 0.82 s (1.90 against 1.08 s) with agent 0 further in; by 0.91 s and 1.15 s in makespan. Two
things differ: how fast the follower backs (0.92 m/s in the manoeuvre; 0.95 to 1.09 m/s on
average when the artefact moves it), and the other's pace (in a manoeuvre the other comes on no
faster than the backer backs, DD95; under the arbiter the leader walks at its own speed). With
the slow backer the gap is larger (first out 5.25 against 1.60 s; makespan 16.74 against
13.20 s): the manoeuvre backs agent 1 out at 0.43 m/s, and agent 0 comes on at that pace.

**The distance criterion against the time criterion** (with the slow backer, its own layout:
agent 0 2.0 m in, agent 1 1.4 m in). The seed rule backs out agent 1, the one that has walked
less far in: 2.02 m of intentional backing, makespan 16.70 s from rest and 16.74 s walking.
Backing out agent 0 instead (`time_optimal`) takes 2.66 m of backing, 0.64 m more, and is
through sooner: makespan 13.68 s and 13.87 s, about 3 s less. At equal distances
(1.7 m each), backing out agent 0 gives 13.29 s and 13.47 s, against 19.11 s and 16.91 s under
the seed rule, which ties there, waits for the arbiter's leader to creep ahead, and then backs
out agent 1. This is section 18 of `derivations.md` in numbers: the criterion that adds the
least walking is not the one that clears the passage soonest when the two back up at
different speeds.

**Plain ORCA with the slow backer, walking, does get through** (all 40 runs), slowly: first out
at 18.80 and 21.79 s, makespan 29.64 and 32.65 s. In the run traced
(`121_asymmetric_walking_orca_only_r1`, its trajectory), agent 0 pushes agent 1 back out of
the passage, the two moving as one at 0.10 m/s for about 16 s with agent 1 pressed against a
wall, until agent 1 is out and steps aside. That speed is at the artefact's
threshold of 0.1 m/s (`metrics.md`, section 10), so whether a run counts an episode varies
between seeds (12 of the 40 do); the count says nothing about the runs' differences. At equal
speeds the same start deadlocks.

**Backing distance, both kinds.** The seed rule's runs have no artefact at equal speeds. With
the slow backer, every one of its 80 runs has one walking-backwards episode, of 0.26 to 0.33 m
on average. In the run traced (`021_asymmetric_rest_seed_rule_r1`, run again with every step
logged), the episode is exactly the backer's **waiting** phase, 4.7 to 5.9 s: outside the
passage on its centre line, ORCA pushes it back 0.33 m and 0.15 m aside as the other comes out
(open question Q4). The
time-optimal runs have the same when walking (33 of 40 runs, agent 0, the backer). DD98
counts this as the artefact, by design: only the backing out itself is intentional. At equal
speeds the wait (0.60 to 0.90 s) is shorter than an episode's 1 s minimum.

**No run collided**, and in every run the two came within 12 mm of each other.

### 6.4 What these checks do not show

- Anything about people: the rule is a test fixture, and how people settle such a meeting is
  for the validation sub-issue (SI-6). The passage's width and length are placeholders; the
  backing speeds come from ten young adults in one study (`parameters.md`).
- Which start is the right one for SI-3b's cases: at rest the arbiter's fallback stalls,
  walking it gets through by the artefact (Q2). Both are reported because they disagree.
- A waiting backer that steps aside before the other comes out, as a person might (Q4); three
  or more people in a passage, or people queued behind a backer (out of scope).
- The unperturbed baseline: with it, the 20 seeds of a condition would be one run.

## Appendix A. The full tables

Generated by `python -m negsim.rules.report` from the committed logs; checked against it by
`tests/test_rules_report.py`.

### si2_head_on

320 runs, from `a4e1ead` 320.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) | Agent 0 passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| symmetric, no_personas, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.6 ± 0.1 [6.6, 6.8] | 0.0 ± 0.0 | 1.0 ± 0.0 | 10.127 ± 4.823 [0.091, 15.838] | 12.32 ± 0.04 [12.30, 12.40] | 0.254 ± 0.002 [0.251, 0.259] | 0 / 0 | – | left 9, right 11 |
| symmetric, no_personas, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 4.079 ± 0.007 [4.067, 4.089] | 12.20 ± 0.00 | 0.252 ± 0.000 [0.252, 0.252] | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| symmetric, no_personas, unperturbed, plain | 20 | 20 | 0 | 0 / 0 / 20 | 34.8 ± 0.0 | 2.0 ± 0.0 | 1.0 ± 0.0 | 21.118 ± 0.000 | – | 0.000 ± 0.000 | 0 / 0 | – | none 20 |
| symmetric, no_personas, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 4.080 ± 0.000 | 12.20 ± 0.00 | 0.251 ± 0.000 | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| symmetric, f25_m70, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.6 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 11.866 ± 2.900 [7.623, 15.880] | 12.30 ± 0.00 | 0.253 ± 0.001 [0.253, 0.254] | 0 / 0 | – | left 7, right 13 |
| symmetric, f25_m70, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 4.9 ± 0.1 [4.7, 5.1] | 0.0 ± 0.0 | 1.0 ± 0.0 | 6.489 ± 4.332 [0.077, 14.267] | 12.36 ± 0.02 [12.35, 12.40] | 0.506 ± 0.004 [0.501, 0.516] | 0 / 0 | younger_yields_head_on@1 ×20 | left 14, right 6 |
| symmetric, f25_m70, unperturbed, plain | 20 | 20 | 0 | 0 / 0 / 20 | 34.8 ± 0.0 | 2.0 ± 0.0 | 1.0 ± 0.0 | 21.118 ± 0.000 | – | 0.000 ± 0.000 | 0 / 0 | – | none 20 |
| symmetric, f25_m70, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 9.2 ± 0.0 | 1.0 ± 0.0 | 0.0 ± 0.0 | 352.107 ± 0.000 | 18.55 ± 0.00 | 0.700 ± 0.000 | 20 / 0 | younger_yields_head_on@1 ×20 | none 20 |
| offset, no_personas, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.135 ± 0.005 [5.125, 5.144] | 12.20 ± 0.00 | 0.202 ± 0.000 [0.202, 0.202] | 0 / 0 | – | left 20 |
| offset, no_personas, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 7.738 ± 0.010 [7.722, 7.760] | 12.20 ± 0.00 | 0.202 ± 0.000 [0.202, 0.202] | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| offset, no_personas, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.137 ± 0.000 | 12.20 ± 0.00 | 0.202 ± 0.000 | 0 / 0 | – | left 20 |
| offset, no_personas, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 7.740 ± 0.000 | 12.20 ± 0.00 | 0.202 ± 0.000 | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| offset, f25_m70, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.137 ± 0.006 [5.128, 5.148] | 12.20 ± 0.00 | 0.202 ± 0.000 [0.202, 0.202] | 0 / 0 | – | left 20 |
| offset, f25_m70, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.2 ± 0.1 [5.9, 6.4] | 0.0 ± 0.0 | 1.0 ± 0.0 | 3.553 ± 0.007 [3.537, 3.563] | 12.25 ± 0.00 | 0.402 ± 0.000 [0.402, 0.402] | 0 / 0 | younger_yields_head_on@1 ×20 | left 20 |
| offset, f25_m70, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.137 ± 0.000 | 12.20 ± 0.00 | 0.202 ± 0.000 | 0 / 0 | – | left 20 |
| offset, f25_m70, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 3.3 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 3.552 ± 0.000 | 12.25 ± 0.00 | 0.402 ± 0.000 | 0 / 0 | younger_yields_head_on@1 ×20 | left 20 |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| symmetric, no_personas, perturbed, plain | 40 of 40 | 12.32 ± 0.04 [12.30, 12.40] | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| symmetric, no_personas, perturbed, rules | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 940, rule_matched 20 | passed 20 | 0 | 0 |
| symmetric, no_personas, unperturbed, plain | 0 of 40 | – | 20 / 20 / 0 / 20 / 0 | – | – | – | – |
| symmetric, no_personas, unperturbed, rules | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 940, rule_matched 20 | passed 20 | 0 | 0 |
| symmetric, f25_m70, perturbed, plain | 40 of 40 | 12.30 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| symmetric, f25_m70, perturbed, rules | 40 of 40 | 12.51 ± 0.03 [12.50, 12.60] | 20 / 0 / 0 / 0 / 0 | no_rule_matched 931, rule_matched 20 | passed 20 | 0 | 0 |
| symmetric, f25_m70, unperturbed, plain | 0 of 40 | – | 20 / 20 / 0 / 20 / 0 | – | – | – | – |
| symmetric, f25_m70, unperturbed, rules | 40 of 40 | 24.90 ± 0.00 | 20 / 20 / 0 / 0 / 0 | kept 20, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| offset, no_personas, perturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, no_personas, perturbed, rules | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 920, rule_matched 20 | passed 20 | 0 | 0 |
| offset, no_personas, unperturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, no_personas, unperturbed, rules | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 920, rule_matched 20 | passed 20 | 0 | 0 |
| offset, f25_m70, perturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, f25_m70, perturbed, rules | 40 of 40 | 12.30 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 940, rule_matched 20 | passed 20 | 0 | 0 |
| offset, f25_m70, unperturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, f25_m70, unperturbed, rules | 40 of 40 | 12.30 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 940, rule_matched 20 | passed 20 | 0 | 0 |

Conditions whose seeds all gave the same trajectory: symmetric, no_personas, unperturbed, plain; symmetric, no_personas, unperturbed, rules; symmetric, f25_m70, unperturbed, plain; symmetric, f25_m70, unperturbed, rules; offset, no_personas, unperturbed, plain; offset, no_personas, unperturbed, rules; offset, f25_m70, unperturbed, plain; offset, f25_m70, unperturbed, rules.

### si2_keep_left_vs_right

80 runs, from `a4e1ead` 80.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) | Agent 0 passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| perturbed, keep_left | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 4.079 ± 0.007 [4.066, 4.091] | 12.20 ± 0.00 | 0.252 ± 0.000 [0.251, 0.252] | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| perturbed, keep_right | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 4.080 ± 0.006 [4.073, 4.093] | 12.20 ± 0.00 | 0.252 ± 0.000 [0.251, 0.252] | 0 / 0 | keep_right_head_on@1 ×20 | right 20 |
| unperturbed, keep_left | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 4.080 ± 0.000 | 12.20 ± 0.00 | 0.251 ± 0.000 | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| unperturbed, keep_right | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 4.080 ± 0.000 | 12.20 ± 0.00 | 0.251 ± 0.000 | 0 / 0 | keep_right_head_on@1 ×20 | right 20 |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| perturbed, keep_left | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 940, rule_matched 20 | passed 20 | 0 | 0 |
| perturbed, keep_right | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 940, rule_matched 20 | passed 20 | 0 | 0 |
| unperturbed, keep_left | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 940, rule_matched 20 | passed 20 | 0 | 0 |
| unperturbed, keep_right | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 940, rule_matched 20 | passed 20 | 0 | 0 |

Conditions whose seeds all gave the same trajectory: unperturbed, keep_left; unperturbed, keep_right.

### si2_open_crossing

160 runs, from `a4e1ead` 160.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| symmetric, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.268 ± 1.448 [2.552, 7.771] | 12.30 ± 0.00 | 0.149 ± 0.001 [0.148, 0.151] | 0 / 0 | – |
| symmetric, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.8 ± 0.1 [6.8, 7.0] | 0.0 ± 0.0 | 1.0 ± 0.0 | 3.850 ± 2.287 [0.005, 7.807] | 12.31 ± 0.02 [12.30, 12.35] | 0.151 ± 0.003 [0.148, 0.156] | 0 / 0 | – |
| symmetric, unperturbed, plain | 20 | 20 | 0 | 0 / 0 / 20 | 50.2 ± 0.0 | 2.0 ± 0.0 | 1.0 ± 0.0 | 1.105 ± 0.000 | – | 1.984 ± 0.000 | 0 / 0 | – |
| symmetric, unperturbed, rules | 20 | 20 | 0 | 0 / 0 / 20 | 50.2 ± 0.0 | 2.0 ± 0.0 | 1.0 ± 0.0 | 1.105 ± 0.000 | – | 1.984 ± 0.000 | 0 / 0 | – |
| agent_1_later, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.734 ± 0.014 [5.700, 5.756] | 12.35 ± 0.00 | 0.036 ± 0.000 [0.035, 0.036] | 0 / 0 | – |
| agent_1_later, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.737 ± 0.010 [5.717, 5.750] | 12.35 ± 0.00 | 0.036 ± 0.000 [0.035, 0.036] | 0 / 0 | – |
| agent_1_later, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.733 ± 0.000 | 12.35 ± 0.00 | 0.036 ± 0.000 | 0 / 0 | – |
| agent_1_later, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.733 ± 0.000 | 12.35 ± 0.00 | 0.036 ± 0.000 | 0 / 0 | – |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| symmetric, perturbed, plain | 40 of 40 | 12.50 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| symmetric, perturbed, rules | 40 of 40 | 12.50 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 2425 | – | 0 | 0 |
| symmetric, unperturbed, plain | 0 of 40 | – | 20 / 20 / 0 / 20 / 0 | – | – | – | – |
| symmetric, unperturbed, rules | 0 of 40 | – | 20 / 20 / 0 / 20 / 0 | no_rule_matched 5600 | – | 0 | 0 |
| agent_1_later, perturbed, plain | 40 of 40 | 12.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| agent_1_later, perturbed, rules | 40 of 40 | 12.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 2420 | – | 0 | 0 |
| agent_1_later, unperturbed, plain | 40 of 40 | 12.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| agent_1_later, unperturbed, rules | 40 of 40 | 12.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 2420 | – | 0 | 0 |

Conditions whose seeds all gave the same trajectory: symmetric, unperturbed, plain; symmetric, unperturbed, rules; agent_1_later, unperturbed, plain; agent_1_later, unperturbed, rules.

### si2_overtaking

160 runs, from `a4e1ead` 160.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| directly_behind, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 17.8 ± 0.6 [17.2, 19.0] | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.023 ± 0.021 [0.000, 0.061] | 29.71 ± 0.02 [29.70, 29.75] | 0.273 ± 0.001 [0.273, 0.275] | 0 / 20 | – |
| directly_behind, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 10.7 ± 0.2 [10.2, 11.0] | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.007 ± 0.000 [0.007, 0.008] | 30.00 ± 0.00 | 0.502 ± 0.000 [0.502, 0.502] | 0 / 0 | overtaker_keeps_clear@1 ×20 |
| directly_behind, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 45.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.486 ± 0.000 | 29.35 ± 0.00 | 0.000 ± 0.000 | 0 / 20 | – |
| directly_behind, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 7.0 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.007 ± 0.000 | 30.00 ± 0.00 | 0.502 ± 0.000 | 0 / 0 | overtaker_keeps_clear@1 ×20 |
| offset, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 12.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.152 ± 0.002 [0.149, 0.155] | 29.80 ± 0.00 | 0.239 ± 0.000 [0.239, 0.239] | 0 / 40 | – |
| offset, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 10.0 ± 0.2 [9.6, 10.4] | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.007 ± 0.001 [0.007, 0.010] | 29.95 ± 0.00 | 0.452 ± 0.000 [0.452, 0.452] | 0 / 0 | overtaker_keeps_clear@1 ×20 |
| offset, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 12.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.152 ± 0.000 | 29.80 ± 0.00 | 0.239 ± 0.000 | 0 / 40 | – |
| offset, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.007 ± 0.000 | 29.95 ± 0.00 | 0.452 ± 0.000 | 0 / 0 | overtaker_keeps_clear@1 ×20 |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| directly_behind, perturbed, plain | 40 of 40 | 31.96 ± 0.05 [31.90, 32.00] | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| directly_behind, perturbed, rules | 40 of 40 | 32.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 3080, rule_matched 20 | passed 20 | 0 | 0 |
| directly_behind, unperturbed, plain | 40 of 40 | 29.50 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| directly_behind, unperturbed, rules | 40 of 40 | 32.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 3080, rule_matched 20 | passed 20 | 0 | 0 |
| offset, perturbed, plain | 40 of 40 | 32.40 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, perturbed, rules | 40 of 40 | 32.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 3120, rule_matched 20 | passed 20 | 0 | 0 |
| offset, unperturbed, plain | 40 of 40 | 32.40 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, unperturbed, rules | 40 of 40 | 32.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 3120, rule_matched 20 | passed 20 | 0 | 0 |

Conditions whose seeds all gave the same trajectory: directly_behind, unperturbed, plain; directly_behind, unperturbed, rules; offset, unperturbed, plain; offset, unperturbed, rules.

### si2_bottleneck

320 runs, from `a4e1ead` 320.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opposing, equal, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 5.5 ± 0.1 [5.3, 5.7] | 1.0 ± 0.0 | 1.0 ± 0.0 | 6.583 ± 0.011 [6.566, 6.603] | 15.90 ± 0.00 | 0.513 ± 0.000 [0.513, 0.513] | 0 / 0 | – |
| opposing, equal, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 5.5 ± 0.1 [5.2, 5.7] | 1.0 ± 0.0 | 1.0 ± 0.0 | 6.582 ± 0.009 [6.562, 6.596] | 15.90 ± 0.00 | 0.513 ± 0.000 [0.513, 0.513] | 0 / 0 | single_file_first_arrival@1 ×20 |
| opposing, equal, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 5.6 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 6.581 ± 0.000 | 15.90 ± 0.00 | 0.513 ± 0.000 | 0 / 0 | – |
| opposing, equal, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 5.6 ± 0.0 | 1.0 ± 0.0 | 1.0 ± 0.0 | 6.581 ± 0.000 | 15.90 ± 0.00 | 0.513 ± 0.000 | 0 / 0 | single_file_first_arrival@1 ×20 |
| opposing, agent_0_slower, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 5.6 ± 0.1 [5.4, 5.8] | 0.0 ± 0.0 | 1.0 ± 0.0 | 8.037 ± 0.013 [8.016, 8.065] | 16.70 ± 0.00 | 0.511 ± 0.000 [0.511, 0.511] | 0 / 0 | – |
| opposing, agent_0_slower, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 5.6 ± 0.1 [5.4, 5.7] | 0.0 ± 0.0 | 1.0 ± 0.0 | 8.031 ± 0.012 [8.005, 8.050] | 16.70 ± 0.00 | 0.511 ± 0.000 [0.511, 0.511] | 0 / 0 | single_file_first_arrival@1 ×20 |
| opposing, agent_0_slower, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 5.6 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 8.033 ± 0.000 | 16.70 ± 0.00 | 0.511 ± 0.000 | 0 / 0 | – |
| opposing, agent_0_slower, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 5.6 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 8.033 ± 0.000 | 16.70 ± 0.00 | 0.511 ± 0.000 | 0 / 0 | single_file_first_arrival@1 ×20 |
| merging, equal, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 0.2 ± 0.0 [0.1, 0.2] | 0.0 ± 0.0 | 0.0 ± 0.0 | 283.878 ± 0.008 [283.867, 283.891] | 15.80 ± 0.00 | 0.012 ± 0.000 [0.012, 0.012] | 0 / 0 | – |
| merging, equal, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 0.1 ± 0.0 [0.1, 0.2] | 0.0 ± 0.0 | 0.0 ± 0.0 | 283.879 ± 0.008 [283.867, 283.894] | 15.80 ± 0.00 | 0.012 ± 0.000 [0.012, 0.012] | 0 / 0 | single_file_first_arrival@1 ×20 |
| merging, equal, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 0.1 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 283.877 ± 0.000 | 15.80 ± 0.00 | 0.012 ± 0.000 | 0 / 0 | – |
| merging, equal, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 0.1 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 283.877 ± 0.000 | 15.80 ± 0.00 | 0.012 ± 0.000 | 0 / 0 | single_file_first_arrival@1 ×20 |
| merging, agent_0_slower, perturbed, plain | 20 | 0 | 0 | 20 / 0 / 0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 281.911 ± 0.009 [281.891, 281.927] | 16.60 ± 0.00 | 0.012 ± 0.000 [0.012, 0.012] | 0 / 0 | – |
| merging, agent_0_slower, perturbed, rules | 20 | 0 | 0 | 20 / 0 / 0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 281.915 ± 0.007 [281.904, 281.929] | 16.60 ± 0.00 | 0.012 ± 0.000 [0.012, 0.012] | 0 / 0 | single_file_first_arrival@1 ×20 |
| merging, agent_0_slower, unperturbed, plain | 20 | 0 | 0 | 20 / 0 / 0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 281.913 ± 0.000 | 16.60 ± 0.00 | 0.012 ± 0.000 | 0 / 0 | – |
| merging, agent_0_slower, unperturbed, rules | 20 | 0 | 0 | 20 / 0 / 0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 0.0 ± 0.0 | 281.913 ± 0.000 | 16.60 ± 0.00 | 0.012 ± 0.000 | 0 / 0 | single_file_first_arrival@1 ×20 |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| opposing, equal, perturbed, plain | 40 of 40 | 18.00 ± 0.00 | 20 / 20 / 0 / 0 / 0 | – | – | – | – |
| opposing, equal, perturbed, rules | 40 of 40 | 18.00 ± 0.00 | 20 / 20 / 0 / 0 / 0 | kept 40, no_rule_matched 20, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| opposing, equal, unperturbed, plain | 40 of 40 | 18.00 ± 0.00 | 20 / 20 / 0 / 0 / 0 | – | – | – | – |
| opposing, equal, unperturbed, rules | 40 of 40 | 18.00 ± 0.00 | 20 / 20 / 0 / 0 / 0 | kept 40, no_rule_matched 20, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| opposing, agent_0_slower, perturbed, plain | 40 of 40 | 19.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| opposing, agent_0_slower, perturbed, rules | 40 of 40 | 19.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | kept 40, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| opposing, agent_0_slower, unperturbed, plain | 40 of 40 | 19.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| opposing, agent_0_slower, unperturbed, rules | 40 of 40 | 19.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | kept 40, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| merging, equal, perturbed, plain | 40 of 40 | 17.80 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| merging, equal, perturbed, rules | 40 of 40 | 17.80 ± 0.00 | 20 / 0 / 0 / 0 / 0 | kept 60, no_rule_matched 20, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| merging, equal, unperturbed, plain | 40 of 40 | 17.80 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| merging, equal, unperturbed, rules | 40 of 40 | 17.80 ± 0.00 | 20 / 0 / 0 / 0 / 0 | kept 60, no_rule_matched 20, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| merging, agent_0_slower, perturbed, plain | 40 of 40 | 19.40 ± 0.00 | 0 / 0 / 0 / 0 / 0 | – | – | – | – |
| merging, agent_0_slower, perturbed, rules | 40 of 40 | 19.40 ± 0.00 | 0 / 0 / 0 / 0 / 0 | kept 20, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| merging, agent_0_slower, unperturbed, plain | 40 of 40 | 19.40 ± 0.00 | 0 / 0 / 0 / 0 / 0 | – | – | – | – |
| merging, agent_0_slower, unperturbed, rules | 40 of 40 | 19.40 ± 0.00 | 0 / 0 / 0 / 0 / 0 | kept 20, rule_matched 20 | agent_arrived 20 | 0 | 0 |

Conditions whose seeds all gave the same trajectory: opposing, equal, unperturbed, plain; opposing, equal, unperturbed, rules; opposing, agent_0_slower, unperturbed, plain; opposing, agent_0_slower, unperturbed, rules; merging, equal, unperturbed, plain; merging, equal, unperturbed, rules; merging, agent_0_slower, unperturbed, plain; merging, agent_0_slower, unperturbed, rules.

### si2_bidirectional_flow

80 runs, from `a4e1ead` 80.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| perturbed, plain | 20 | 0 | 20 | 40460 / 52694 / 3619 | 1320.7 ± 707.0 [708.9, 3146.2] | 43.1 ± 48.9 [1.0, 129.0] | 830.5 ± 103.8 [636.0, 1058.0] | -32.305 ± 26.462 [-90.114, -5.826] | 38.67 ± 5.95 [33.99, 54.46] | 4.125 ± 2.088 [1.004, 8.777] | 333 / 413 | – |
| perturbed, rules | 20 | 0 | 20 | 29011 / 65988 / 1674 | 984.0 ± 83.4 [861.8, 1223.5] | 29.2 ± 16.0 [1.0, 56.0] | 399.3 ± 35.8 [359.0, 514.0] | -200.627 ± 100.664 [-456.333, -48.471] | 35.87 ± 0.73 [34.92, 37.57] | 2.974 ± 0.237 [2.578, 3.341] | 72 / 282 | keep_left_head_on@1 ×49111, overtaker_keeps_clear@1 ×89715 |
| unperturbed, plain | 20 | 0 | 20 | 38788 / 54188 / 3776 | 1392.5 ± 813.6 [711.3, 3812.2] | 45.4 ± 50.3 [1.0, 158.0] | 830.5 ± 105.7 [642.0, 1005.0] | -32.538 ± 25.925 [-98.112, -8.014] | 39.03 ± 6.53 [34.04, 56.62] | 4.169 ± 2.436 [0.831, 10.274] | 355 / 410 | – |
| unperturbed, rules | 20 | 0 | 20 | 28078 / 67028 / 1738 | 954.4 ± 120.2 [748.6, 1213.0] | 33.8 ± 24.0 [1.0, 83.0] | 402.1 ± 42.4 [357.0, 525.0] | -190.717 ± 99.931 [-372.684, -31.800] | 35.98 ± 0.96 [34.73, 38.31] | 3.124 ± 0.153 [2.863, 3.342] | 107 / 279 | keep_left_head_on@1 ×49714, overtaker_keeps_clear@1 ×90350 |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| perturbed, plain | 2000 of 2000 | 83.37 ± 10.24 [68.40, 114.30] | 40544 / 37718 / 3619 / 0 / 0 | – | – | – | – |
| perturbed, rules | 2000 of 2000 | 46.91 ± 10.60 [40.80, 84.20] | 55227 / 38348 / 1674 / 0 / 0 | kept 54976, no_rule_matched 14887462, rule_matched 138826 | agent_arrived 685, passed 138141 | 0 | 0 |
| unperturbed, plain | 1992 of 2000 | 77.47 ± 11.53 [48.60, 98.70] | 42014 / 39944 / 3776 / 0 / 13 | – | – | – | – |
| unperturbed, rules | 2000 of 2000 | 44.92 ± 3.91 [41.20, 57.70] | 55755 / 40614 / 1738 / 0 / 0 | kept 70275, no_rule_matched 14868525, rule_matched 140064 | agent_arrived 1534, passed 138530 | 0 | 0 |

### si2_head_on_r5

320 runs, from `a4e1ead` 320.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) | Agent 0 passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| symmetric, no_personas, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.841 ± 0.008 [5.831, 5.859] | 12.20 ± 0.00 | 0.253 ± 0.000 [0.253, 0.253] | 0 / 0 | – | left 11, right 9 |
| symmetric, no_personas, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.842 ± 0.006 [5.832, 5.855] | 12.20 ± 0.00 | 0.253 ± 0.000 [0.253, 0.253] | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| symmetric, no_personas, unperturbed, plain | 20 | 20 | 0 | 0 / 0 / 20 | 31.4 ± 0.0 | 2.0 ± 0.0 | 1.0 ± 0.0 | 21.083 ± 0.000 | – | 0.000 ± 0.000 | 0 / 0 | – | none 20 |
| symmetric, no_personas, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.842 ± 0.000 | 12.20 ± 0.00 | 0.253 ± 0.000 | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| symmetric, f25_m70, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 5.839 ± 0.005 [5.830, 5.849] | 12.20 ± 0.00 | 0.253 ± 0.000 [0.253, 0.253] | 0 / 0 | – | left 11, right 9 |
| symmetric, f25_m70, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 3.7 ± 0.2 [3.2, 3.9] | 0.0 ± 0.0 | 1.0 ± 0.0 | 4.274 ± 0.005 [4.265, 4.283] | 12.25 ± 0.00 | 0.504 ± 0.000 [0.504, 0.504] | 0 / 0 | younger_yields_head_on@1 ×20 | left 11, right 9 |
| symmetric, f25_m70, unperturbed, plain | 20 | 20 | 0 | 0 / 0 / 20 | 31.4 ± 0.0 | 2.0 ± 0.0 | 1.0 ± 0.0 | 21.083 ± 0.000 | – | 0.000 ± 0.000 | 0 / 0 | – | none 20 |
| symmetric, f25_m70, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 7.9 ± 0.0 | 1.0 ± 0.0 | 0.0 ± 0.0 | 306.951 ± 0.000 | 18.55 ± 0.00 | 0.657 ± 0.000 | 20 / 0 | younger_yields_head_on@1 ×20 | none 20 |
| offset, no_personas, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 9.963 ± 0.010 [9.949, 9.985] | 12.20 ± 0.00 | 0.203 ± 0.000 [0.203, 0.203] | 0 / 0 | – | left 20 |
| offset, no_personas, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 9.964 ± 0.008 [9.952, 9.985] | 12.20 ± 0.00 | 0.203 ± 0.000 [0.203, 0.203] | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| offset, no_personas, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 9.965 ± 0.000 | 12.20 ± 0.00 | 0.203 ± 0.000 | 0 / 0 | – | left 20 |
| offset, no_personas, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 9.965 ± 0.000 | 12.20 ± 0.00 | 0.203 ± 0.000 | 0 / 0 | keep_left_head_on@1 ×20 | left 20 |
| offset, f25_m70, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 9.967 ± 0.008 [9.948, 9.976] | 12.20 ± 0.00 | 0.203 ± 0.000 [0.203, 0.203] | 0 / 0 | – | left 20 |
| offset, f25_m70, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 3.5 ± 0.2 [2.9, 3.8] | 0.0 ± 0.0 | 1.0 ± 0.0 | 8.557 ± 0.006 [8.549, 8.574] | 12.25 ± 0.00 | 0.406 ± 0.000 [0.406, 0.406] | 0 / 0 | younger_yields_head_on@1 ×20 | left 20 |
| offset, f25_m70, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 3.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 9.965 ± 0.000 | 12.20 ± 0.00 | 0.203 ± 0.000 | 0 / 0 | – | left 20 |
| offset, f25_m70, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 1.9 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 8.555 ± 0.000 | 12.25 ± 0.00 | 0.406 ± 0.000 | 0 / 0 | younger_yields_head_on@1 ×20 | left 20 |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| symmetric, no_personas, perturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| symmetric, no_personas, perturbed, rules | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 360, rule_matched 20 | passed 20 | 0 | 0 |
| symmetric, no_personas, unperturbed, plain | 0 of 40 | – | 20 / 20 / 0 / 20 / 0 | – | – | – | – |
| symmetric, no_personas, unperturbed, rules | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 360, rule_matched 20 | passed 20 | 0 | 0 |
| symmetric, f25_m70, perturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| symmetric, f25_m70, perturbed, rules | 40 of 40 | 12.30 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 360, rule_matched 20 | passed 20 | 0 | 0 |
| symmetric, f25_m70, unperturbed, plain | 0 of 40 | – | 20 / 20 / 0 / 20 / 0 | – | – | – | – |
| symmetric, f25_m70, unperturbed, rules | 40 of 40 | 24.90 ± 0.00 | 20 / 20 / 0 / 0 / 0 | kept 20, rule_matched 20 | agent_arrived 20 | 0 | 0 |
| offset, no_personas, perturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, no_personas, perturbed, rules | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 360, rule_matched 20 | passed 20 | 0 | 0 |
| offset, no_personas, unperturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, no_personas, unperturbed, rules | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 360, rule_matched 20 | passed 20 | 0 | 0 |
| offset, f25_m70, perturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, f25_m70, perturbed, rules | 40 of 40 | 12.30 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 360, rule_matched 20 | passed 20 | 0 | 0 |
| offset, f25_m70, unperturbed, plain | 40 of 40 | 12.20 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, f25_m70, unperturbed, rules | 40 of 40 | 12.30 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 360, rule_matched 20 | passed 20 | 0 | 0 |

Conditions whose seeds all gave the same trajectory: symmetric, no_personas, unperturbed, plain; symmetric, no_personas, unperturbed, rules; symmetric, f25_m70, unperturbed, plain; symmetric, f25_m70, unperturbed, rules; offset, no_personas, unperturbed, plain; offset, no_personas, unperturbed, rules; offset, f25_m70, unperturbed, plain; offset, f25_m70, unperturbed, rules.

### si2_overtaking_r5

160 runs, from `a4e1ead` 160.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| directly_behind, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 17.6 ± 0.6 [17.1, 19.4] | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.017 ± 0.017 [0.000, 0.059] | 29.72 ± 0.03 [29.70, 29.75] | 0.273 ± 0.001 [0.272, 0.275] | 0 / 20 | – |
| directly_behind, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 10.7 ± 0.2 [10.2, 11.0] | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.007 ± 0.000 [0.007, 0.008] | 30.00 ± 0.00 | 0.502 ± 0.000 [0.502, 0.502] | 0 / 0 | overtaker_keeps_clear@1 ×20 |
| directly_behind, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 45.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.486 ± 0.000 | 29.35 ± 0.00 | 0.000 ± 0.000 | 0 / 20 | – |
| directly_behind, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 7.0 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.007 ± 0.000 | 30.00 ± 0.00 | 0.502 ± 0.000 | 0 / 0 | overtaker_keeps_clear@1 ×20 |
| offset, perturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 12.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.153 ± 0.002 [0.151, 0.158] | 29.80 ± 0.00 | 0.239 ± 0.000 [0.239, 0.239] | 0 / 40 | – |
| offset, perturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 10.1 ± 0.3 [9.5, 10.6] | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.007 ± 0.000 [0.006, 0.008] | 29.95 ± 0.00 | 0.452 ± 0.000 [0.452, 0.452] | 0 / 0 | overtaker_keeps_clear@1 ×20 |
| offset, unperturbed, plain | 20 | 0 | 0 | 0 / 20 / 0 | 12.8 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.152 ± 0.000 | 29.80 ± 0.00 | 0.239 ± 0.000 | 0 / 40 | – |
| offset, unperturbed, rules | 20 | 0 | 0 | 0 / 20 / 0 | 6.4 ± 0.0 | 0.0 ± 0.0 | 1.0 ± 0.0 | 0.007 ± 0.000 | 29.95 ± 0.00 | 0.452 ± 0.000 | 0 / 0 | overtaker_keeps_clear@1 ×20 |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| directly_behind, perturbed, plain | 40 of 40 | 31.98 ± 0.06 [31.80, 32.00] | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| directly_behind, perturbed, rules | 40 of 40 | 32.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 2740, rule_matched 20 | passed 20 | 0 | 0 |
| directly_behind, unperturbed, plain | 40 of 40 | 29.50 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| directly_behind, unperturbed, rules | 40 of 40 | 32.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 2740, rule_matched 20 | passed 20 | 0 | 0 |
| offset, perturbed, plain | 40 of 40 | 32.40 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, perturbed, rules | 40 of 40 | 32.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 2700, rule_matched 20 | passed 20 | 0 | 0 |
| offset, unperturbed, plain | 40 of 40 | 32.40 ± 0.00 | 20 / 0 / 0 / 0 / 0 | – | – | – | – |
| offset, unperturbed, rules | 40 of 40 | 32.60 ± 0.00 | 20 / 0 / 0 / 0 / 0 | no_rule_matched 2700, rule_matched 20 | passed 20 | 0 | 0 |

Conditions whose seeds all gave the same trajectory: directly_behind, unperturbed, plain; directly_behind, unperturbed, rules; offset, unperturbed, plain; offset, unperturbed, rules.

### si2_bidirectional_flow_ablation

40 runs, from `3a9bdff` 40.

| Condition | Runs | Deadlock runs | Collision runs | Pairs: avoided / resolved / failed | Exposure, all agents (s) | Yield events | Near misses | Min separation (mm) | Mean time to goal (s) | Largest path deviation (m) | Backward / hurried episodes | Rules fired (matches begun) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| without_overtaker_keeps_clear | 20 | 0 | 20 | 40940 / 51853 / 3423 | 982.4 ± 187.4 [810.6, 1477.0] | 6.2 ± 15.5 [0.0, 61.0] | 437.4 ± 42.4 [399.0, 565.0] | -53.932 ± 16.490 [-87.756, -29.371] | 34.98 ± 1.03 [34.48, 38.56] | 4.052 ± 2.237 [3.039, 12.331] | 27 / 314 | keep_left_head_on@1 ×49635 |
| without_keep_left_head_on | 20 | 0 | 20 | 1557 / 79567 / 8914 | 7044.4 ± 3145.2 [1674.2, 10677.4] | 190.7 ± 46.9 [99.0, 246.0] | 1312.5 ± 267.5 [733.0, 1690.0] | -305.705 ± 56.359 [-438.633, -146.260] | 53.12 ± 14.42 [36.58, 99.92] | 3.060 ± 0.909 [2.224, 6.263] | 1611 / 232 | overtaker_keeps_clear@1 ×453072 |

| Condition | Arrived | Makespan (s) | Pairs with exposure / a yield / a collision / a deadlock / open at timeout | Evaluations, by outcome | Matches ended, by reason | Formation mismatches | Cross-pair conflicts |
|---|---|---|---|---|---|---|---|
| without_overtaker_keeps_clear | 2000 of 2000 | 45.48 ± 13.86 [39.10, 83.00] | 52834 / 7489 / 3423 / 0 / 0 | kept 2807, no_rule_matched 17933967, rule_matched 49635 | agent_arrived 4, passed 49631 | 0 | 0 |
| without_keep_left_head_on | 936 of 2000 | 78.24 ± 7.82 [67.40, 89.50] | 69004 / 86930 / 8914 / 0 / 32404 | kept 564890, no_rule_matched 38474839, rule_matched 453072 | agent_arrived 199, out_of_range 1, passed 449239, run_ended 3633 | 0 | 0 |

## Appendix B. The tables of issue #32

Generated by `python -m negsim.rules.report si32_passage_meet_middle si32_passage_meet_with_speeds`
from the committed logs; checked against it by `tests/test_rules_report.py`.

### si32_passage_meet_middle

240 runs, from `d57e854` 240.

| Condition | Runs | Ended | Out first | Backed out | First out (s) | Both out (s) | Backing, intentional (m) | Backing, artefact (m) | Backing, both (m) | Makespan (s) | Min separation (mm) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| symmetric, rest, arbiter | 20 | deadlock 14, timeout 6 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 7.0 ± 4.8 [0.0, 11.5] |
| symmetric, rest, seed_rule | 20 | completed 20 | agent 0 20 | agent 1 20 | 4.47 ± 0.31 [3.80, 4.90] | 9.53 ± 0.36 [8.80, 10.10] | 2.30 ± 0.00 [2.30, 2.30] | 0.00 ± 0.00 | 2.30 ± 0.00 [2.30, 2.30] | 14.76 ± 0.39 [14.00, 15.40] | 0.2 ± 0.3 [0.0, 0.7] |
| symmetric, rest, orca_only | 20 | deadlock 20 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 0.0 ± 0.0 [0.0, 0.0] |
| symmetric, walking, arbiter | 20 | completed 20 | agent 0 20 | – | 1.80 ± 0.00 | 6.67 ± 0.05 [6.60, 6.70] | 0.00 ± 0.00 | 2.18 ± 0.01 [2.17, 2.19] | 2.18 ± 0.01 [2.17, 2.19] | 11.89 ± 0.02 [11.80, 11.90] | 2.0 ± 0.6 [1.0, 2.8] |
| symmetric, walking, seed_rule | 20 | completed 20 | agent 0 20 | agent 1 20 | 2.50 ± 0.00 | 7.60 ± 0.00 | 2.26 ± 0.00 [2.26, 2.26] | 0.00 ± 0.00 | 2.26 ± 0.00 [2.26, 2.26] | 12.80 ± 0.00 | 2.0 ± 1.2 [0.5, 4.9] |
| symmetric, walking, orca_only | 20 | deadlock 20 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 0.0 ± 0.0 [0.0, 0.0] |
| asymmetric, rest, arbiter | 20 | deadlock 14, timeout 6 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 7.0 ± 4.8 [0.0, 11.5] |
| asymmetric, rest, seed_rule | 20 | completed 20 | agent 0 20 | agent 1 20 | 1.60 ± 0.00 | 6.59 ± 0.13 [6.50, 7.00] | 1.38 ± 0.00 [1.38, 1.38] | 0.00 ± 0.00 | 1.38 ± 0.00 [1.38, 1.38] | 11.85 ± 0.09 [11.80, 12.20] | 1.3 ± 1.5 [0.0, 4.3] |
| asymmetric, rest, orca_only | 20 | deadlock 20 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 0.0 ± 0.0 [0.0, 0.0] |
| asymmetric, walking, arbiter | 20 | completed 20 | agent 0 20 | – | 1.08 ± 0.04 [1.00, 1.10] | 5.57 ± 0.05 [5.50, 5.60] | 0.00 ± 0.00 | 1.21 ± 0.04 [1.17, 1.33] | 1.21 ± 0.04 [1.17, 1.33] | 10.80 ± 0.00 | 2.2 ± 0.4 [1.3, 2.6] |
| asymmetric, walking, seed_rule | 20 | completed 20 | agent 0 20 | agent 1 20 | 1.90 ± 0.00 | 6.71 ± 0.03 [6.70, 6.80] | 1.37 ± 0.00 [1.37, 1.37] | 0.00 ± 0.00 | 1.37 ± 0.00 [1.37, 1.37] | 11.95 ± 0.05 [11.90, 12.00] | 1.5 ± 2.4 [0.0, 7.4] |
| asymmetric, walking, orca_only | 20 | deadlock 20 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 0.0 ± 0.0 [0.0, 0.0] |

| Condition | Rules fired (matches begun) | Handoffs: to the arbiter / to a manoeuvre / back to ORCA | Manoeuvre began (s) | Manoeuvres ended, by reason | Backing / waiting time (s) | Backward / hurried episodes | Backward time (s) |
|---|---|---|---|---|---|---|---|
| symmetric, rest, arbiter | – | 20 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| symmetric, rest, seed_rule | passage_shorter_backs_out@1 ×20 | 20 / 20 / 0 | 1.87 ± 0.31 [1.20, 2.30] | other_cleared 20 | 2.50 ± 0.00 / 0.70 ± 0.00 | 0 / 0 | 0.00 ± 0.00 |
| symmetric, rest, orca_only | – | 0 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| symmetric, walking, arbiter | – | 20 / 0 / 20 | – | – | – | 20 / 0 | 2.00 ± 0.00 |
| symmetric, walking, seed_rule | passage_shorter_backs_out@1 ×20 | 20 / 20 / 0 | 0.10 ± 0.00 | other_cleared 20 | 2.40 ± 0.00 / 0.60 ± 0.00 | 0 / 0 | 0.00 ± 0.00 |
| symmetric, walking, orca_only | – | 0 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| asymmetric, rest, arbiter | – | 20 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| asymmetric, rest, seed_rule | passage_shorter_backs_out@1 ×20 | 0 / 0 / 0 | 0.00 ± 0.00 | other_cleared 20 | 1.50 ± 0.00 / 0.70 ± 0.02 | 0 / 0 | 0.00 ± 0.00 |
| asymmetric, rest, orca_only | – | 0 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| asymmetric, walking, arbiter | – | 20 / 0 / 20 | – | – | – | 20 / 0 | 1.27 ± 0.06 [1.20, 1.40] |
| asymmetric, walking, seed_rule | passage_shorter_backs_out@1 ×20 | 0 / 0 / 0 | 0.00 ± 0.00 | other_cleared 20 | 1.50 ± 0.00 / 0.90 ± 0.00 | 0 / 0 | 0.00 ± 0.00 |
| asymmetric, walking, orca_only | – | 0 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |

### si32_passage_meet_with_speeds

320 runs, from `d57e854` 320.

| Condition | Runs | Ended | Out first | Backed out | First out (s) | Both out (s) | Backing, intentional (m) | Backing, artefact (m) | Backing, both (m) | Makespan (s) | Min separation (mm) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| asymmetric, rest, arbiter | 20 | deadlock 12, timeout 8 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 5.7 ± 4.9 [0.0, 11.2] |
| asymmetric, rest, seed_rule | 20 | completed 20 | agent 0 20 | agent 1 20 | 4.90 ± 0.00 | 10.51 ± 0.11 [10.40, 10.70] | 2.02 ± 0.00 [2.02, 2.02] | 0.33 ± 0.03 [0.29, 0.36] | 2.35 ± 0.03 [2.31, 2.38] | 16.70 ± 0.11 [16.60, 16.90] | 0.3 ± 0.2 [0.0, 0.6] |
| asymmetric, rest, orca_only | 20 | deadlock 16, timeout 4 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 0.0 ± 0.0 [-0.0, 0.0] |
| asymmetric, rest, time_optimal | 20 | completed 20 | agent 1 20 | agent 0 20 | 3.00 ± 0.00 | 8.39 ± 0.12 [8.30, 8.60] | 2.66 ± 0.00 [2.66, 2.66] | 0.00 ± 0.00 | 2.66 ± 0.00 [2.66, 2.66] | 13.68 ± 0.11 [13.60, 13.90] | 4.6 ± 2.1 [0.2, 7.1] |
| asymmetric, walking, arbiter | 20 | completed 20 | agent 0 20 | – | 1.60 ± 0.00 | 7.00 ± 0.00 | 0.00 ± 0.00 | 1.85 ± 0.01 [1.84, 1.87] | 1.85 ± 0.01 [1.84, 1.87] | 13.20 ± 0.00 | 6.5 ± 1.0 [5.2, 7.8] |
| asymmetric, walking, seed_rule | 20 | completed 20 | agent 0 20 | agent 1 20 | 5.25 ± 0.05 [5.20, 5.30] | 10.54 ± 0.08 [10.40, 10.70] | 2.02 ± 0.00 [2.01, 2.02] | 0.26 ± 0.02 [0.23, 0.31] | 2.27 ± 0.02 [2.24, 2.32] | 16.74 ± 0.08 [16.60, 16.90] | 0.4 ± 0.3 [0.0, 1.2] |
| asymmetric, walking, orca_only | 20 | completed 20 | agent 0 20 | – | 18.80 ± 0.02 [18.70, 18.80] | 23.44 ± 0.05 [23.40, 23.50] | 0.00 ± 0.00 | 0.41 ± 0.64 [0.00, 1.37] | 0.41 ± 0.64 [0.00, 1.37] | 29.64 ± 0.05 [29.60, 29.70] | 0.0 ± 0.0 |
| asymmetric, walking, time_optimal | 20 | completed 20 | agent 1 20 | agent 0 20 | 3.30 ± 0.00 | 8.62 ± 0.12 [8.50, 8.90] | 2.66 ± 0.00 [2.66, 2.66] | 0.35 ± 0.27 [0.00, 0.64] | 3.01 ± 0.27 [2.66, 3.30] | 13.87 ± 0.11 [13.70, 14.10] | 5.1 ± 3.2 [0.3, 9.7] |
| symmetric, rest, arbiter | 20 | deadlock 12, timeout 8 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 5.7 ± 4.9 [0.0, 11.2] |
| symmetric, rest, seed_rule | 20 | completed 20 | agent 0 20 | agent 1 20 | 7.27 ± 0.39 [6.60, 7.70] | 12.93 ± 0.43 [12.20, 13.60] | 2.32 ± 0.00 [2.32, 2.32] | 0.31 ± 0.02 [0.30, 0.34] | 2.63 ± 0.02 [2.62, 2.66] | 19.11 ± 0.41 [18.40, 19.70] | 0.0 ± 0.0 [0.0, 0.0] |
| symmetric, rest, orca_only | 20 | deadlock 16, timeout 4 | neither 20 | – | – | – | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | – | 0.0 ± 0.0 [0.0, 0.0] |
| symmetric, rest, time_optimal | 20 | completed 20 | agent 1 20 | agent 0 20 | 2.70 ± 0.00 | 8.05 ± 0.11 [7.90, 8.20] | 2.30 ± 0.00 [2.30, 2.30] | 0.00 ± 0.00 | 2.30 ± 0.00 [2.30, 2.30] | 13.29 ± 0.14 [13.10, 13.50] | 2.9 ± 1.9 [0.3, 6.4] |
| symmetric, walking, arbiter | 20 | completed 20 | agent 0 20 | – | 1.80 ± 0.00 | 7.40 ± 0.00 | 0.00 ± 0.00 | 2.18 ± 0.01 [2.17, 2.20] | 2.18 ± 0.01 [2.17, 2.20] | 13.60 ± 0.00 | 1.8 ± 0.6 [1.0, 2.8] |
| symmetric, walking, seed_rule | 20 | completed 20 | agent 0 20 | agent 1 20 | 5.20 ± 0.00 | 10.72 ± 0.06 [10.60, 10.90] | 2.20 ± 0.00 [2.20, 2.20] | 0.29 ± 0.02 [0.25, 0.35] | 2.49 ± 0.02 [2.46, 2.55] | 16.91 ± 0.07 [16.80, 17.10] | 0.2 ± 0.2 [0.0, 0.6] |
| symmetric, walking, orca_only | 20 | completed 20 | agent 0 20 | – | 21.79 ± 0.05 [21.70, 21.90] | 26.45 ± 0.05 [26.40, 26.50] | 0.00 ± 0.00 | 0.50 ± 0.78 [0.00, 1.67] | 0.50 ± 0.78 [0.00, 1.67] | 32.65 ± 0.05 [32.60, 32.70] | 0.0 ± 0.0 |
| symmetric, walking, time_optimal | 20 | completed 20 | agent 1 20 | agent 0 20 | 2.90 ± 0.00 | 8.27 ± 0.07 [8.20, 8.40] | 2.30 ± 0.00 [2.30, 2.30] | 0.59 ± 0.05 [0.55, 0.77] | 2.89 ± 0.05 [2.85, 3.07] | 13.47 ± 0.08 [13.40, 13.60] | 6.6 ± 2.4 [1.7, 10.0] |

| Condition | Rules fired (matches begun) | Handoffs: to the arbiter / to a manoeuvre / back to ORCA | Manoeuvre began (s) | Manoeuvres ended, by reason | Backing / waiting time (s) | Backward / hurried episodes | Backward time (s) |
|---|---|---|---|---|---|---|---|
| asymmetric, rest, arbiter | – | 20 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| asymmetric, rest, seed_rule | passage_shorter_backs_out@1 ×20 | 0 / 0 / 0 | 0.00 ± 0.00 | other_cleared 20 | 4.70 ± 0.00 / 1.16 ± 0.06 | 20 / 0 | 1.16 ± 0.06 [1.10, 1.30] |
| asymmetric, rest, orca_only | – | 0 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| asymmetric, rest, time_optimal | – | 0 / 0 / 0 | 0.00 ± 0.00 | other_cleared 20 | 2.90 ± 0.00 / 0.73 ± 0.05 | 0 / 0 | 0.00 ± 0.00 |
| asymmetric, walking, arbiter | – | 20 / 0 / 20 | – | – | – | 20 / 0 | 1.80 ± 0.00 |
| asymmetric, walking, seed_rule | passage_shorter_backs_out@1 ×20 | 0 / 0 / 0 | 0.00 ± 0.00 | other_cleared 20 | 4.70 ± 0.00 / 1.33 ± 0.07 | 20 / 0 | 1.27 ± 0.07 [1.20, 1.40] |
| asymmetric, walking, orca_only | – | 0 / 0 / 0 | – | – | – | 6 / 0 | 4.08 ± 6.40 [0.00, 13.70] |
| asymmetric, walking, time_optimal | – | 0 / 0 / 0 | 0.00 ± 0.00 | other_cleared 20 | 2.90 ± 0.00 / 0.97 ± 0.05 | 13 / 0 | 0.65 ± 0.49 [0.00, 1.00] |
| symmetric, rest, arbiter | – | 20 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| symmetric, rest, seed_rule | passage_shorter_backs_out@1 ×20 | 20 / 20 / 0 | 1.87 ± 0.39 [1.20, 2.30] | other_cleared 20 | 5.40 ± 0.00 / 1.02 ± 0.04 | 20 / 0 | 1.02 ± 0.04 [1.00, 1.10] |
| symmetric, rest, orca_only | – | 0 / 0 / 0 | – | – | – | 0 / 0 | 0.00 ± 0.00 |
| symmetric, rest, time_optimal | – | 0 / 0 / 0 | 0.00 ± 0.00 | other_cleared 20 | 2.50 ± 0.00 / 0.80 ± 0.00 | 0 / 0 | 0.00 ± 0.00 |
| symmetric, walking, arbiter | – | 20 / 0 / 20 | – | – | – | 20 / 0 | 2.00 ± 0.00 |
| symmetric, walking, seed_rule | passage_shorter_backs_out@1 ×20 | 20 / 20 / 0 | 0.10 ± 0.00 | other_cleared 20 | 4.80 ± 0.00 / 1.23 ± 0.04 | 20 / 0 | 1.21 ± 0.06 [1.10, 1.30] |
| symmetric, walking, orca_only | – | 0 / 0 / 0 | – | – | – | 6 / 0 | 4.99 ± 7.81 [0.00, 16.70] |
| symmetric, walking, time_optimal | – | 0 / 0 / 0 | 0.00 ± 0.00 | other_cleared 20 | 2.50 ± 0.00 / 1.00 ± 0.00 | 20 / 0 | 1.00 ± 0.00 |

