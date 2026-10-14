# How rules are matched to pairs of agents

The `RuleDatabaseProvider` (`negsim/rules/provider.py`) supplies directives from the rules
of `rule-format.md`. This file is the policy it follows: which rule a pair of agents follows,
from step to step. The code is `negsim/rules/matching.py`; what it records is in
`log-schema.md` (`pair_interactions.jsonl`).

The unit is the **pair interaction**: two agents, from the first step on which either
perceives the other to the first on which neither does, one of them has arrived, or the run
has ended (`negsim/avoidance/simulation.py`, `PairInteraction`).

## 1. Evaluation on a shared snapshot

**Rules are evaluated once per pair, on a single snapshot shared by the two agents, and each
agent receives the directive of its role.** The snapshot holds every field a rule can read
(`rule-format.md`, section 5) for that pair at that step (`negsim/rules/snapshot.py`).

**Why that is the same as each agent evaluating the rules on its own.** Suppose each agent
applied the rules itself, to what it perceives. It would come to the same rule and to
complementary roles as the other, because:

1. **Every field a rule reads is one both agents compute identically.** Pair-level fields
   are symmetric in the two agents (a distance, a closing speed, a time to collision, a
   difference of headings, the corridor between them); the record's pair-level fields are
   computed once, with the lower-numbered agent first, and shared (`perception.md`). An
   agent-level field (an age, a speed) counts only if the *other* agent can see it too, and
   rules that read something else are refused at load (`unobservable_field`).
2. **The visibility settings are the same for both agents** in a run.
3. **Perception is perfect and simultaneous**: both agents perceive the same state of the
   world, at the start of the same step, without error or delay.

Under 1 to 3, the snapshot agent A builds from its own record equals the one agent B builds
from its own, value for value, and equals the shared one. Every rule therefore matches or
fails the same way for both, they pick the same rule by the same priority, and a role
assignment, which orders the same two values, gives them complementary roles.

**This rests on assumption 3, and it is an assumption, stated plainly: perception here is
perfect and simultaneous.** Real people misjudge ages, speeds and distances, and two people
do not see each other at the same instant. With imperfect perception the two could disagree
about which rule applies, and the equivalence would fail. Nothing in this sub-issue models
that.

**Where the equivalence fails even here.** One agent can perceive the other without being
perceived, when their sensing radii differ or more than `max_neighbours` agents are in range
(issue #26's assumption A6; counted as `one_sided_steps`). The shared snapshot is then still
evaluated and the agent that perceives gets its role's directive; the other, which has no
half-plane for the pair at all, is not affected. ORCA's pairwise guarantee does not cover
such steps anyway.

**Checked three ways.** (a) `tests/test_rules_matching.py` builds, for 300 random states
under each of five visibility settings, the shared snapshot and each agent's snapshot from its
own record, and finds them equal. (b) In every run, on the step a pair forms, each agent's
own evaluation (`RuleDatabaseProvider.directive(record)`, which is what the provider
interface asks) is compared with the shared one; disagreements are counted in
`outcome.json` as `rules.formation_mismatches` and recorded per pair as `independent_agrees`.
(c) The consistency property test (section 9).

## 2. When rules are evaluated

- **When a pair forms**: on the first step on which a neighbour enters an agent's sensing
  radius.
- **On every step while no rule holds.** So a rule conditioned on, say, the time to
  collision fires on the first step its threshold is met, not only when the two first see
  each other (`tests/test_rules_matching.py::test_a_rule_whose_threshold_is_met_later_fires_later`).
- **Whenever the pair's encounter class changes** while a rule holds (section 3 says what
  counts as a change). Only rules of strictly higher priority than the held one can then
  replace it; if none matches, the evaluation's outcome is `kept`.

This is the issue's policy as written. One consequence, noted here because it can surprise:
**while a rule holds and the class does not change, nothing is evaluated**, so a rule of
higher priority whose threshold is met later in the same encounter does not replace it. The
pair keeps the convention it settled on.

## 3. Holding a match, and hysteresis

**A rule that has matched holds** until it expires (section 6), whatever its own condition
does meanwhile: a time-to-collision condition that held when the two were on a collision
course stops holding once they step aside, and the rule stays. The only way out early is a
rule of strictly higher priority at a re-evaluation.

**Hysteresis, so that rules do not flap between steps.** Three mechanisms:

1. **A class change counts only when it is steady**: the new class must be seen on
   `hysteresis_steps` steps in a row (3 by default, 0.3 s; a definition with no source). A
   class that flickers at a boundary (a heading difference near 60° or 120°) triggers
   nothing.
2. **Holding is sticky** (above), and a replacement must have strictly higher priority, so
   within one encounter the priority of the held rule only ever goes up: no rule can come
   back.
3. **After a match expires, the pair is not evaluated again until its (steady) class has
   changed.** Two agents that have just passed each other are still in range and may jostle
   back and forth across "approaching"; they do not pick the rule up again. A genuinely new
   encounter (they separate for three steps and then approach again) is evaluated afresh.

*Tested:* `test_a_class_that_flickers_triggers_nothing_and_a_steady_change_does`,
`test_after_expiry_the_pair_is_evaluated_again_only_once_its_class_has_changed`.

## 4. Several matches

**The highest priority wins.** Rules are tried highest priority first; the first priority
at which any rule matches decides.

**Two matching rules at the same priority with different directives are an error.** Where
possible it is found before any run: when an experiment switches its rules on, every pair of
rules at the same priority whose encounter classes overlap is tried on a **grid of test
situations** (section 8), and if both match one of them with different directives the rule
set is refused (`ambiguous`), naming the situation. Two such rules can therefore not be
switched on together; `keep_left_head_on` and `keep_right_head_on` are such a pair.

**Otherwise it is logged at run time**: if two rules at the top priority do match one pair
with different directives (the grid was too large to try, section 8), the evaluation's
outcome is `ambiguous_match`, an `ambiguous_match` event is written, and **the rule with the
lower `rule_id` is applied**. Two rules that agree are not ambiguous; the lower `rule_id` is
recorded as the one applied.

## 5. No match, and one rule per pair

**No match: the baseline.** A pair that no rule matches follows plain ORCA, and the
evaluation is logged as `no_rule_matched`, with how many rules were tried.

**One rule per pair.** A single winning rule supplies the whole directive of the pair; any
field it does not set takes its baseline value. Fields are never merged across rules. So
when `younger_yields_head_on` (priority 20) and `keep_left_head_on` (priority 10) both
match, the pair gets the shares of the first and no side, not the side of the second. This
keeps "which rule did what" traceable to one rule.

## 6. Expiry

A match ends, and both agents' directives return to the baseline, on the **first** of:

- **the encounter has passed** (rules with `expiry: passed`, the default): the two are
  separating, `p · v > 0` with `p` and `v` their relative position and velocity, and their
  centres are further apart than the two radii plus the pair's clearance margin
  (`derivations.md`, section 15);
- **the pair interaction ends**: neither perceives the other any more (`out_of_range`),
  one of them has arrived (`agent_arrived`), or the run has ended (`run_ended`);
- **a rule of strictly higher priority replaces it** (`replaced`).

A rule with `expiry: out_of_range` skips the first. Every match records when it ended and
why.

`speed_scale` follows the same expiry for every provider, not only for rules: for the
static provider of issue #26 the run loop stops applying a directive's `speed_scale` on the
step its encounter has passed (`derivations.md`, section 15).

## 7. Several neighbours

**Rules are matched per pair.** An agent in range of several neighbours has one match per
pair, and each pair's directive acts on that pair's ORCA half-plane.

**Cross-pair conflicts.** The matches of one agent's pairs can contradict each other. Where
the contradiction is in a field the rules set explicitly, it is logged as a
`cross_pair_conflict` (an event, and on each pair involved) when it appears, and settled as
follows:

| Field | Conflict | How it is settled |
|---|---|---|
| `side_preference` | `left` toward one neighbour, `right` toward another | Nothing to settle: a side preference acts only on its own pair's half-plane, so each pair keeps its own side. Logged because an agent told to keep left and keep right at once is a sign two rules disagree |
| `speed_scale` | Two different scales | An agent has one preferred speed: the smallest scale applies (DD40, as for any several directives) |
| `passage_order` | Leader toward one, follower toward another | Each pair's order goes to the arbiter on its own. Ordering three or more agents at one segment is out of scope (`architecture.md`, section 4) |

Shares and clearance margins are per pair and cannot conflict.

## 8. The grid of test situations

Used to find, before any run, two rules at one priority that could tell one pair different
things (`negsim/rules/ambiguity.py`). For two rules it tries every combination of:

- the encounter classes both can apply to (the specific one, or the four real classes if
  both are written for `any`);
- for every pair-level field either rule compares: each constant it is compared with, a
  value just below and just above each (closer than a third of the gap to the next
  constant), and "missing";
- for every agent-level field either rule reads, for each of the two agents independently:
  the same values, plus, for a field used in a role assignment, values that put the two
  agents in either order beyond the tie tolerance and within it; and "missing".

**Why it is enough.** A comparison is between one field and one constant, so whether it
holds can change only at that constant; one value in each interval between constants, and
the constants themselves, give every combination of outcomes the comparisons on a field can
take. A role assignment depends only on the order of two values and whether they tie, which
the extra values cover. So if two rules can both match some situation, they both match one
of the grid's.

**What it can get wrong, and which way.** It varies fields independently, so it can try an
age difference of 30 for two agents whose ages are equal. A situation that cannot happen can
only make it report a clash that would never arise, never miss one that would. Such a report
is answered by giving one of the rules another priority.

A grid of more than 200,000 situations is not tried: the pair is listed in the run's config
as unchecked (`directives.unchecked_pairs`), and the run-time check of section 4 is all that
covers it. None of the shipped rules comes near that.

## 9. The consistency property test

Over many random pairs (two agents placed anywhere in open ground or in the bottleneck,
moving any way at any speed, with random ages and genders), the seed rules are evaluated on
the shared snapshot and the two resulting directives are combined as ORCA would combine them
(`resolve_pair`). Counted: reciprocity violations (shares short of 1, opposite sides, two
leaders or two followers) and non-complementary passage orders.

On 20,000 random pairs for each of two rule sets, `default` and `default` with
`keep_right_head_on` in place of `keep_left_head_on`: 4,563 pairs matched a rule; **0
reciprocity violations and 0 non-complementary roles**; 2,339 times a rule applied but its
two agents tied and the rule did not match (`no_match`), falling back cleanly to a rule of
lower priority or the baseline. All five encounter classes occurred (none 10,961, single
file 3,261, overtaking 2,093, crossing 1,936, head-on 1,749). The test suite runs 4,000 per
rule set (`test_the_seed_database_never_gives_a_pair_inconsistent_directives`).

## 10. Decisions in this policy

The issue fixes most of the policy. Where it had to be completed, these are decisions, not
instructions (`architecture.md`, section 7, numbers them):

- re-evaluation while a rule holds happens only at a class change (the issue's list, taken
  literally), with the outcome `kept` when nothing of higher priority matches;
- hysteresis is the three mechanisms of section 3, with 3 steps;
- after expiry, nothing until the class changes;
- the cross-pair conflicts counted are those of section 7, and only between fields the rules
  set themselves;
- a run-time ambiguity is logged once per entry of the pair's evaluation log, not once per
  step.
