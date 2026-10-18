# Trained deciders: model options

> For issue [#38](https://github.com/M450NCH00/CrowdSimulation/issues/38), PT-4 of track
> [#34](https://github.com/M450NCH00/CrowdSimulation/issues/34). Every claim cites an entry in
> [entries.md](entries.md) (handles in brackets, with that entry's locator), or is marked
> `[inference]`. The idea being evaluated — trained models behind the same Situation → Decision
> interface as the rules — is **a proposal, not agreed**.

Companion files: [entries](entries.md) · [evaluation](evaluation.md) · [verdict](verdict.md) ·
[search log](search-log.md) · [missing papers](missing-papers.md)

---

## §1. What the literature says, question by question

### Q1. Distilling LLM decisions into fast deciders
- **What has been done.** Three patterns:
  - LLM-written code, refined against LLM decisions ([Zhang-DFD]);
  - a smaller language model fine-tuned on a larger one's judgements ([Fang-Etiquette]) or on its
    own rollouts reweighted to real aggregates ([Amano-MobilityLM]);
  - a **table keyed by binned context, filled by repeated LLM calls** ([Chopra-Archetypes] §3;
    [Li-GenWorld] §4).
- **Fidelity.** Only [Zhang-DFD] measures fidelity to the teacher on held-out *and*
  out-of-domain data (its Tables 3–4). [Li-GenWorld] says it did not compare the table with fresh
  teacher calls (§8). [Chopra-Archetypes] and [Amano-MobilityLM] measure against real aggregates
  instead (§5 and Fig. 3b respectively).
- **Cost.** Distillation took about 5 days and pays back after about 10 runs ([Zhang-DFD] §5.5).
  A table lookup costs 0.54 µs ([Li-GenWorld] §4); 400 LLM queries covered 8.4 million agents for
  one weekly decision ([Chopra-Archetypes] §5).
- **Outside the training data.** One held-out domain ([Zhang-DFD]), one unseen weather prompt
  ([Amano-MobilityLM] §5), otherwise untested. Unseen table keys need a back-off rule
  ([Li-GenWorld] §4).
- **A warning.** Fine-tuning on skewed labels exaggerated the majority class, 74% → above 94%
  ([Amano-MobilityLM] §3).

### Q2. Interpretable models learned from labelled decisions
- On structured, meaningful features, simple models (rule lists, logistic regression) often match
  complex ones ([Rudin-StopExplaining] §2 (i), Appendix B). This is an argument with one worked
  example (CORELS against COMPAS, Fig. 3, Table 1), not a meta-analysis.
- A neural policy can be distilled into a decision tree with the teacher's reward, from 3 nodes
  (cart-pole) to 769 (Atari Pong); training on the student's **own** states keeps trees an order
  of magnitude smaller than plain imitation ([Bastani-VIPER] §4, Fig. 4c). The small trees could
  be verified in seconds, and verification found a failure that 50 perfect rollouts had hidden
  ([Bastani-VIPER] §4).
- **The comparison the issue asks for — learned interpretable model against hand-written rule —
  was not found.** The one learned-against-hand-written comparison in this repository uses a
  network, not an interpretable model, and found the learned order better in dense instances and
  worse on speed, scale, information needed and readability ([Yang-S2AN], via `research-gap.md`
  §6). So Q2 is answered only in part.

### Q3. Rules as constraints or rewards for learned policies
- **Shielding** gives proved correctness and minimal interference for safety properties, relative
  to an abstraction of the environment ([Alshiekh-Shielding] §6.1). A post-posed shield needs
  nothing from the learner (§5.2).
- **Reward machines** give convergence to the optimal policy for the rule-defined reward (tabular
  CRM, Theorem 4.1), assuming a correct labelling function ([Icarte-RewardMachines] §7).
  "Optimal for the reward" is not "always obeys the rule".
- **A norm as a reward penalty** was followed in about 85% of random cases, not always
  ([Chen-SACADRL] §IV-B, Table I).
- **Training cost**: hours for four agents ([Chen-SACADRL] §IV-A), up to days for a hard task
  ([Icarte-RewardMachines] §5.4).
- **Carry-over between simulators**: not tested by any source. The only transfer is simulation to
  one robot, reported qualitatively ([Chen-SACADRL] §IV-C). `[inference]` What could carry over is
  the reward or the shield, written over the vocabulary; the policy itself is trained per simulator.

### Q4. Checking a trained decider for bias
- **Fairness through unawareness** — not using the protected attribute — is what the FYP's "no
  `ethnic_group` input" rule is. It is not enough when other inputs carry the attribute
  ([Kusner-CF] §2.1, Definition 1; the unaware model fails their test, §5, Fig. 2).
- **Counterfactual fairness**: the decision must not change if the attribute had been different,
  in a causal model; it holds for any predictor using only non-descendants of the attribute
  ([Kusner-CF] Definition 5, Lemma 1).
- **The working test** is the counterfactual gap: swap the attribute, measure the change in output
  ([Garg-CFText] Definition 2, "Metrics"). It applies only where the right output should not
  change; where it should ("asymmetric counterfactuals"), forcing equality is wrong
  ([Garg-CFText], "Asymmetric Counterfactuals").
- **LLM-agent and LLM-decision studies** vary attributes in a full factorial over fixed templates,
  and estimate effects with a mixed-effects regression ([Tamkin-Discrim] §2, §3.1).
- How the FYP's two rules map onto this is in [evaluation](evaluation.md) §3.

### Q5. Teachers: what each can and cannot teach
- **The rules.** A student trained only on rule labels can at best copy the rules: nothing the
  rules do not contain can be learned (the issue's premise). No source tests whether such a student
  helps anyway. The nearest evidence: rules distilled **together with** other labels improve the
  student, most when those labels are scarce (5% labels: 79.9 → 81.5–82.5%), and the rule teacher
  beats its own student ([Hu-LogicRules] Tables 2–3, §3.4). `[inference]` Two uses survive for a
  rule-only student: covering situations no rule matches (but it has no basis there except
  extrapolation, which is what [evaluation](evaluation.md) §2 must test), and acting as a cheap
  stand-in where rule evaluation is "expensive or impossible" ([Hu-LogicRules] §3.4). Neither
  applies yet, since this FYP's rules are cheap. `[inference]`
- **LLM decisions on text Situations.** Can teach behaviour the rules do not state. Fidelity to the
  LLM can be measured; validity cannot be inherited from it ([Zhang-DFD] §6.1). An LLM teacher can
  carry demographic effects into its labels: Claude 2's decisions shifted with age, gender and race
  in a factorial test ([Tamkin-Discrim] §3.3). Several LLMs: an aggregate beat the best single model
  in most text-labelling tasks ([Plaza-ModelCrowds] §1, §4), and one study found results changing
  with the model and the number of queries ([Chopra-Archetypes] §8, Fig. 6). `[inference]` Because
  demographic effects reverse between models (issue #16, `README.md`), a vote across models should
  not be the label where they disagree; the disagreement is a finding.
- **Session outcomes** (`outcomes.jsonl`: who conceded, who went first). `[inference]` These are
  the only labels that come from **negotiated** decisions rather than one-shot judgements, so they
  are the closest to what the FYP studies. But they are few (one row per session), produced by
  LLMs (so the LLM caveats apply), and each row records the people's `ethnic_group`
  (`llm_negotiation/docs/log-schema.md`), so the input filter and the label-side test of
  [evaluation](evaluation.md) §3 are both needed. No source in this review uses negotiation
  outcomes as training labels.
- **Human data.** The only teacher that can make a decider *valid* rather than *faithful*. No
  source here trains a decider on individual human conflict decisions; [Amano-MobilityLM] and
  [Chopra-Archetypes] fit to human **aggregates** only. `[inference]` For this FYP, human data is
  better used as the reference in evaluation (as track #34 proposes) than as training labels, since
  the human evidence collected in issue #37 is mostly published rates, not labelled individual
  decisions.

---

## §2. The options table

Cost at 10,000 agents is `[inference]` throughout: per-decision costs from the entries, multiplied
by 10,000 decisions in one round. In a crowd only agents in a conflict need to decide, so this is
an upper bound per step.

| Option | Teacher (where labels come from) | Inputs | Portability across simulators | Cost at 10,000 agents | Readability | Evidence for | Evidence against |
|---|---|---|---|---|---|---|---|
| **R. Rules alone** (the rule engine; the reference) | none: rules extracted from LLM negotiation | Situation features named by the rule | High if the rule is written over the vocabulary (proposal, track #34) `[inference]` | Arbitration rules ran at 10,000 agents, about 10 ms per step (via `research-gap.md` §6, [Okumura-PIBT]) | Full | Rule teacher beat its distilled student ([Hu-LogicRules] Table 2); simple models often match complex ones on structured features ([Rudin-StopExplaining] §2 (i)) | Cannot decide where no rule matches `[inference]`; learned order beat hand-written in dense instances ([Yang-S2AN] §5.2) |
| **T. LLM-filled lookup table** (added by me; not on the issue's list) | LLM, K repeated calls per binned Situation | Binned Situation features | High: the table is keyed by vocabulary features, not simulator state `[inference]` | 0.54 µs per lookup → about 5 ms per round ([Li-GenWorld] §4) `[inference]` | Table can be printed; LLM's reasons are lost ([Chopra-Archetypes]; [Li-GenWorld]) `[inference]` | Reached 8.4 M agents with 400 queries ([Chopra-Archetypes] §5); beat both heuristic and LLM agents on forecast error ([Chopra-Archetypes] Table 1) | Fidelity to fresh teacher calls never measured ([Li-GenWorld] §8); unseen keys need back-off ([Li-GenWorld] §4); depends on model and K ([Chopra-Archetypes] Fig. 6) |
| **D. Decision tree, rule list or logistic model** | Rules, LLM labels, or both; trained on the student's own Situations | Situation features | High: same inputs as the rules `[inference]` | A few comparisons per decision; negligible `[inference]` | Full for small trees; not for 769+ nodes ([Bastani-VIPER] §4) `[inference]` | Trees matched teacher reward at 3–769 nodes ([Bastani-VIPER] §4); verifiable in seconds, and verification found a hidden failure ([Bastani-VIPER] §4); no accuracy loss expected on structured features ([Rudin-StopExplaining] §2 (i)) | Unstable: different samples give different trees ([Rudin-StopExplaining] Appendix E); no comparison with hand-written rules found (§1, Q2); tree guarantees are heuristic, not proved ([Bastani-VIPER] §2) |
| **N. Gradient boosting or a small neural network** | Rules, LLM labels, or both | Situation features (or raw state, which loses portability) | High with Situation features; low with raw state `[inference]` | Neural: 8.7 ms per decision in Python → about 87 s per round on one core ([Chen-SACADRL] §IV-A) `[inference]`; boosting not measured here | None ([Rudin-StopExplaining] §2 (ii)) | Rules distilled into a network improve it, most with few labels ([Hu-LogicRules] Table 3); counterfactual training can close the bias gap for known attributes ([Garg-CFText] Table 1) | Usually no better than simple models on structured data ([Rudin-StopExplaining] Appendix B); counterfactual fixes did not generalise to held-out terms ([Garg-CFText] Table 2); **no gradient-boosting entry was read** |
| **L. Small language model** (fine-tuned on a larger LLM) | Larger LLM's decisions; optionally real aggregates | Situation as text | High: text is simulator-free `[inference]` | 0.5–2 s per call for a local 7B model ([Li-GenWorld] §7.1.5) → about 1.4–5.6 hours per round, sequential `[inference]` | Rationale only, and discarded ([Amano-MobilityLM] §2.1) | Real-time for one robot ([Fang-Etiquette]); responds to unseen context in text ([Amano-MobilityLM] §5) | Majority-class amplification ([Amano-MobilityLM] §3); tested on 500 agents at most ([Amano-MobilityLM] §4); inherits LLM demographic effects ([Tamkin-Discrim] §3.3) `[inference]` |
| **P. RL policy with rule rewards, optionally shielded** | Rules as reward ([Icarte-RewardMachines]; [Chen-SACADRL]) or as shield ([Alshiekh-Shielding]) | Simulator state (plus shield or machine state) | Low: trained per simulator; only reward or shield carry over (§1, Q3) `[inference]` | 8.7 ms per decision ([Chen-SACADRL] §IV-A) → about 87 s per round on one core `[inference]` | Policy: none; reward and shield: readable ([Icarte-RewardMachines] Fig. 1b) | Shield: proved safety, faster learning ([Alshiekh-Shielding] §6.1, §8); norm learned to 85% ([Chen-SACADRL] Table I) | Norm only 85%, not 100% ([Chen-SACADRL] Table I); hours to days of training ([Chen-SACADRL] §IV-A; [Icarte-RewardMachines] §5.4); no between-simulator transfer tested (§1, Q3) |
| *Reference: live LLM per decision* | — | Situation as text | High `[inference]` | Many LLM calls per round; 19 M calls a day for 200,000 agents in one estimate ([Li-GenWorld] §4) | Rationale per call | Flexible ([Amano-MobilityLM] §1) | Heuristic agents at full scale beat LLM agents at 300 ([Chopra-Archetypes] §6, Table 1) |

---

## §3. What this table cannot carry

- **No source is about pedestrian conflict decisions** except [Chen-SACADRL] (passing sides, four
  agents) and [Fang-Etiquette] (one robot). Every other row rests on other domains: evacuation
  ([Zhang-DFD]), mobility and daily routines, epidemics and labour, control, text. `[inference]`
  The issue's rule on overreach applies: none of this shows what happens in a queue.
- **Gradient boosting** has no entry; its row rests on Rudin's argument only.
- **Cost figures** are from different hardware and languages (Python on one CPU in
  [Li-GenWorld] and [Chen-SACADRL]); the 10,000-agent figures are my multiplication, not
  measurements.
