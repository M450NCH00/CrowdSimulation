# Verdict: trained deciders (PT-4, for PT-7)

> Issue [#38](https://github.com/M450NCH00/CrowdSimulation/issues/38). Answers Q6. Evidence:
> [options](options.md), [entries](entries.md); test plan: [evaluation](evaluation.md).
> **A recommendation for the supervisor, not an agreed plan.** Statements without a handle are
> `[inference]`.

**1. The rule engine stays the reference decider.** A trained model is worth adding only for a
claim fixed in advance: closer to human evidence, the same decisions more cheaply, or decisions
where no rule matches. The rules are already cheap (arbitration rules have run at 10,000 agents,
`research-gap.md` §6), and a rule-regularised teacher beat its own distilled student ([Hu-LogicRules] Table 2).

**2. Worth training first: small decision trees or rule lists on Situation features**, against an
**LLM-filled lookup table** as baseline. Both use the rules' inputs, so they are as portable as the
rules, and both run at 10,000 agents (0.54 µs per lookup, [Li-GenWorld] §4; 8.4 M agents,
[Chopra-Archetypes] §5). Small trees can be read and checked exhaustively ([Bastani-VIPER] §4).
Simple models usually match complex ones on such features ([Rudin-StopExplaining] §2 (i)), so a
neural model or boosting comes in only if trees miss agreement by a stated margin.

**3. Teachers, in order.**
- **LLM decisions on text Situations, from several models**, with their disagreement reported, not
  voted away: aggregates beat the best single model in most labelling tasks
  ([Plaza-ModelCrowds] §4), but demographic effects reverse between models (issue #16). Test the
  teacher for bias first ([Tamkin-Discrim]; evaluation B6).
- **The rules, combined with those labels**: rules helped most where other labels were few
  ([Hu-LogicRules] Table 3). A rule-only student is a pipeline check (it must reproduce the rules,
  E5 = 100%).
- **Session outcomes** (`outcomes.jsonl`): held-out comparison data, not labels — few, LLM-made,
  and carrying `ethnic_group`.
- **Human data**: the evaluation reference (E9); #37's evidence is rates, not labelled decisions.

**4. Not worth training now.**
- **RL policies with rule rewards**: one per simulator, no between-simulator transfer tested
  anywhere, hours to days of training, and a reward-given norm followed about 85% of the time
  ([Chen-SACADRL] Table I; [Icarte-RewardMachines] §5.4). Adopt the **shield** pattern instead: a
  trained decider proposes, the rule engine blocks what breaks a hard rule
  ([Alshiekh-Shielding] §5.2, §6.1).
- **A small language model at run time**: 0.5–2 s per call ([Li-GenWorld] §7.1.5); 500 agents at
  most ([Amano-MobilityLM] §4). Possibly a cheaper *teacher*.

**5. At 10,000 agents.** Rules, lookup table, small trees: yes. A small neural network: about 87 s
per round on one core (8.7 ms per decision, [Chen-SACADRL] §IV-A), so only batched or at conflicts
only. Small or live LLM: no.

**6. How to evaluate** ([evaluation](evaluation.md)): agreement with the teacher on held-out and
closed-loop Situations (E1, E3); deployed class shares (E4; 74% → 94%+ in [Amano-MobilityLM] §3);
abstention outside the vocabulary (E6); and bias: no `ethnic_group` input (B1), no proxy by
construction (B2, [Kusner-CF] Lemma 1), a counterfactual gap of 0 for every attribute a rule says
must not matter (B3, [Garg-CFText]), and the teacher test (B6). B6 and B7 for `ethnic_group` wait
for the ethics sign-off on fictional groups.

**7. Limits.** Two sources are about pedestrian conflicts ([Chen-SACADRL]; [Fang-Etiquette]). None
compares a *learned interpretable* model with *hand-written* rules, and none tests a trained
decider across simulators. Point 2 is the cheapest experiment, not a proven one.

**For the supervisor:** (a) are trained deciders in scope; (b) which teachers (track #34,
decision 7); (c) per conflict type, which attributes must not matter.
