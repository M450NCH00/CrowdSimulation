# Evaluating a trained decider beside the rules

> For issue [#38](https://github.com/M450NCH00/CrowdSimulation/issues/38), PT-4 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34).
>
> **Status: a proposal (design decision for the supervisor), not agreed.** The checks are mine,
> built from the sources in [entries.md](entries.md). Each check names the source it comes from;
> where none does, it is marked `[inference]`. Nothing here has been run.

Companion files: [entries](entries.md) · [options](options.md) · [verdict](verdict.md)

---

## §1. The principle

A trained decider sits behind the same Situation → Decision interface as the rules (track #34,
point 4), so it is judged by the **same conformance tests** as the rule engine, plus the checks
below. Every check is run on the rule engine too, so each number for a trained decider has a
rule-engine number beside it.

What "better than the rules" can mean has to be fixed **before** any training: closer to human
evidence; same decisions at lower cost; or decisions where no rule matches. `[inference]` These
are different claims, and each needs a different check below.

---

## §2. Fidelity, generalisation and cost

| # | Check | How | Pass criterion (to be fixed in advance) | Source |
|---|---|---|---|---|
| E1 | **Agreement with the teacher on held-out Situations** | Decision agreement rate (deterministic deciders); KL divergence or total variation between action distributions (stochastic ones), on Situations not used in training | Set per teacher before training | Named as the missing check by [Li-GenWorld] §8 |
| E2 | **Held out by conflict type** | Train on some conflict types, test on others, following the track's seen/unseen split and its levels L0–L4 (#34, point 5) | Agreement on seen types; on unseen types, the human-evidence reference (E9) | `[inference]`; only [Zhang-DFD] has an out-of-domain set (its Tables 3–4) |
| E3 | **Closed-loop test** | Let the decider drive the simulation, and evaluate on the Situations **it** produces, not only on those the teacher's run produced | Same criteria as E1, on the student's own Situations | [Bastani-VIPER] §1–§2 (the DAgger point) |
| E4 | **Class balance** | Compare the share of each decision (wait, proceed, give way …) in training labels, in the teacher's own run, and in the decider's closed-loop run | Deployed shares within a set tolerance of the teacher's | [Amano-MobilityLM] §3 (74% trained → above 94% deployed) |
| E5 | **Rule compliance where a rule matches** | On Situations where a rule applies, the share of decisions that equal the rule's | 100% for a decider meant to stand in for the rules; otherwise report the share | [Chen-SACADRL] Table I (a norm given as reward: about 85%) |
| E6 | **Abstention** | On out-of-vocabulary Situations (L4), does the decider abstain? | It must; a decider that cannot abstain fails L4 | `[inference]`: the rule engine can return "no match"; trees, networks and tables answer everything unless given a default. [Li-GenWorld] §4 backs off to coarser keys, which is not abstaining |
| E7 | **Teacher stability** | For LLM teachers: repeat each Situation K times and record the spread; for several LLMs, record where they disagree | Report, and exclude unstable Situations from "agreement" claims | [Li-GenWorld] §4 (σ per key); [Plaza-ModelCrowds] §4; [Chopra-Archetypes] Fig. 6 |
| E8 | **Cost at scale** | Time per decision, and per simulation step at 1,000 and 10,000 agents, on stated hardware | Within the step budget the simulator needs (to be set by PT-6) | Per-decision figures: [Li-GenWorld] §7.1.5, [Chen-SACADRL] §IV-A |
| E9 | **Validity against human evidence** | Compare the decider's outcomes with the human reference behaviours collected for the unseen scenarios (issue #37) | The criteria the track fixes for the rules | [Zhang-DFD] §6.1 (validity "depends directly on the reference data") |
| E10 | **Readability** (interpretable deciders only) | Size (nodes, rules); and whether a reader can state what it does | Small enough to read in full `[inference]` | [Rudin-StopExplaining] §1 (sparsity); [Bastani-VIPER] §4 (3 to 9,757 nodes) |

Two notes:
- Compare deciders by **decisions**, not by structure: two trees can differ in shape and decide
  alike ([Rudin-StopExplaining] Appendix E).
- An aggregate metric can hide large differences between deciders; E1 and E5 are per decision for
  that reason ([Amano-MobilityLM] §1, Fig. 3).

---

## §3. Bias checks, including the counterfactual test

The FYP's two rules (issue #38):
1. no model may take `ethnic_group` as an input;
2. wherever a rule says an attribute must not matter, the decision must not change when it does.

Rule 1 is **fairness through unawareness** ([Kusner-CF] Definition 1), which is not sufficient on
its own: other inputs, or the labels, can carry the attribute ([Kusner-CF] §2.1, §5). Rule 2 is a
**counterfactual** test restricted to the attributes that should not matter, which is how
[Garg-CFText] handles "asymmetric counterfactuals". So the checks are:

| # | Check | How | Pass criterion | Source |
|---|---|---|---|---|
| B1 | **No `ethnic_group` input** (rule 1) | Static check of the decider's input schema: `ethnic_group` is not a feature, and is not in any text prompt given to a language-model decider | Must pass; no tolerance | Rule 1; [Kusner-CF] Definition 1 |
| B2 | **No proxy for `ethnic_group`** | In the scenario generator, confirm that no Situation feature is caused by `ethnic_group` (assigned independently; no group-dependent spawn points, speeds or roles). Then check independence empirically on the generated Situations | Must pass by construction; then [Kusner-CF] Lemma 1 holds for any decider on those features | [Kusner-CF] Lemma 1, §3.2 `[inference: that the simulator lets us check this by construction]` |
| B3 | **Counterfactual gap for "must not matter" attributes** (rule 2) | For each attribute A that a rule declares irrelevant in a conflict type, and each test Situation x: change A to each other value, keeping every other feature fixed, and compute the gap = mean |decision(x) − decision(x′)| (for a stochastic decider, the difference in action probabilities) | **0** for deterministic deciders (rules, tables, trees); for stochastic ones, a tolerance fixed in advance, with a confidence interval | [Garg-CFText] Definition 2, "Metrics" |
| B4 | **Exclude intended effects** | Attributes a rule says **should** matter (for example age or a mobility aid, where a rule gives priority) are not tested in B3; instead E5 checks the decider follows the rule | Documented list, per conflict type, of which attributes must not matter | [Garg-CFText], "Asymmetric Counterfactuals" |
| B5 | **Exhaustive check for small trees** | For a tree or rule list, check that no path tests a "must not matter" attribute in that conflict type. This proves B3 for every Situation, not only sampled ones | No such split | [Bastani-VIPER] §3–§4 (verification of extracted trees) `[inference: applying it to this property]` |
| B6 | **Teacher test, before labels are used** | Run the LLM teacher on a full factorial: every Situation template × every combination of the persona attributes (age band, gender, and the others in the vocabulary); estimate each attribute's effect with a mixed-effects regression, Situation template as a random effect | Effects of "must not matter" attributes not distinguishable from 0; any intended effect reported with its size | [Tamkin-Discrim] §2, §3.1–§3.2 |
| B7 | **Label-side test for session outcomes** | If `outcomes.jsonl` is used as a teacher, compare outcome rates (who went first, who conceded) across values of each "must not matter" attribute, including `ethnic_group` in runs where the group was on | No difference beyond a tolerance fixed in advance | `[inference]`; `outcomes.jsonl` records each person's `ethnic_group` (`llm_negotiation/docs/log-schema.md`) |

Why B6 and B7 matter even though B1 passes: a student that never sees `ethnic_group` can still
learn the teacher's group effect if the labels carry it and any input correlates with the group.
B2 closes the correlation route; B6 and B7 detect the effect in the labels. `[inference]`

**Constraint.** B6 and B7 for `ethnic_group` need the fictional group switched on in a teacher
run. The supervisor's ethics sign-off for fictional groups is still pending (`WORK_LOG-32.md`, Q1),
and nothing in track #34 may switch the group on. So these two checks, **for `ethnic_group`
only**, wait for that sign-off; B1 and B2 do not need the group switched on.

**What the counterfactual test does not cover.** Intersections of attributes ([Tamkin-Discrim]
§6.1 names this limit for its own design); effects that only appear in groups of more than two
people `[inference]`; and fixes that work on the tested values but not on others (counterfactual
training did not generalise to held-out identity terms, [Garg-CFText] Table 2).

---

## §4. What to report, per decider

One row per decider, the rule engine first:

| Decider | Teacher | E1 agreement | E3 closed-loop agreement | E4 deployed shares | E5 compliance | E6 abstains? | E8 ms per decision; s per step at 10,000 | E9 against human reference | B1 | B2 | B3 gap per attribute | B6/B7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Rule engine | — | — | — | | 100% by definition | yes | | | pass | | 0 | n/a |
| … | | | | | | | | | | | | |

Report the teacher's own B6 result next to the decider's B3, so that a reader can see whether a
bias came from the teacher or the student. `[inference]`
