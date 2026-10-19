# Work Log — Issue #38: [Research] PT-4 Literature: models trained on extracted rules (distillation, learned deciders, rule-guided learning)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/38
**Branch:** `docs/38-trained-deciders-literature`
**Started:** 2026-10-18

## Understanding the issue

Track #34 proposes (**not agreed; needs the supervisor's sign-off**) that rules be stated over a
portable vocabulary, behind a Situation → Decision interface. Point 4 of that idea puts **trained
models** behind the same interface, so that rules, trained models and a live LLM are
interchangeable deciders. Before anything is trained, this issue asks what the literature says
about the options. Literature only: no code, no training, no paid calls.

Six questions:
- **Q1** distilling LLM decisions into fast deciders: what has been done, with what fidelity and
  cost, and how the distilled model behaved outside its training data (cross-reference Zhang et al.
  2026 and Fang et al. 2026 without re-summarising them);
- **Q2** learning interpretable rules from labelled decisions, compared with hand-written rules on
  accuracy, generalisation and readability (including [Yang-S2AN] by cross-reference);
- **Q3** rules as constraints or rewards for learned policies (reward machines, shielding,
  norm-aware or constrained RL): guarantees, training cost, carry-over between simulators;
- **Q4** checking a trained decider for bias: counterfactual tests, counterfactual fairness, how
  LLM-agent studies test demographic effects; plus this FYP's two rules (no `ethnic_group` input;
  where a rule says an attribute must not matter, the decision must not change when it does);
- **Q5** teachers: rules, LLM decisions on text situations, logged session outcomes, human data;
  what each can and cannot teach; evidence for several LLM teachers;
- **Q6** verdict: which model types, with which teachers, evaluated how, and which could run at
  10,000 agents.

Priority if short of budget: Q1, Q2, Q4, Q3, Q5. Aim for 8 to 12 entries.

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** `origin/main` (`5a0f7be`) has none of the `literature/` files the issue
  says to read; they exist only along the stacked research branches. As #36 and #37 did, I cut this
  branch from the previous issue in the track, `docs/37-unseen-scenario-human-evidence` (PR #45,
  head `57f9148`, in sync with origin), and will target the PR at it. A merge into a non-default
  branch will not close #38 by itself.
- **A2. Cache prefix.** Sources for this issue are cached as `refs/td_*` ("trained deciders"),
  following `pr_*` (#35), `us_*` (#36) and `he_*` (#37).
- **A3. What is committed** (the repository is public; same rule as #35 to #37). Extracts and PDFs
  are committed only for openly licensed copies and arXiv; copies with no open licence are kept on
  disk only and listed in `.gitignore` with a re-download link.
- **A4. Reads beyond "these, and only these".** For format only (no content used as evidence): the
  `missing-papers.md` and `search-log.md` of #37, its work log's assumptions and open questions, and
  the `.gitignore` convention. The issue itself names `s3-mapf-robotics.md` for [Yang-S2AN].
- **A5. Stubs** for sources that cannot be opened go in `entries.md` where the entry would have
  gone, with exactly the issue's six lines, and are listed in `missing-papers.md`.

## Plan

1. Branch and work log. **(done)**
2. Read what the issue lists. **(done)**
3. Q1 distillation: confirm Amano & Yamaguchi 2026; search for further LLM → small-model
   distillation of agent decisions (crowd, driving, social navigation, agent-based modelling).
4. Q2 interpretable learned rules: Rudin 2019; Zhang's baselines (PySR, LLM-SR); a policy-to-tree
   distillation source (e.g. VIPER) and a learned-vs-hand-written comparison.
5. Q4 bias: Kusner et al. 2017; a counterfactual-input test for LLM decisions.
6. Q3 rule-guided RL: reward machines (ICML 2018 / JAIR 2022), shielding (AAAI 2018), one
   norm-aware or constrained RL source.
7. Q5 teachers, drawn from the entries plus any source on multi-teacher distillation.
8. `options.md`, `evaluation.md`, `verdict.md`, `search-log.md`, `missing-papers.md`,
   `refs-trained-deciders.bib`; README row.
9. Verify against §5b of the workflow; push; open the PR against the #37 branch.

## Progress log

### 2026-10-18 — Branch set-up, and a git mishap
- What I did: ran `git checkout main && git pull` as §0 of the workflow says. The checkout
  **half-failed**: it rewrote the index and working tree to `main`'s tree, then could not write
  `.git/HEAD` ("unable to write symref for HEAD: Permission denied"), leaving HEAD on the #37
  branch with the whole of `main` showing as staged changes. I checked that the index and working
  tree matched `main` exactly (`git diff --cached main` and `git diff` both empty), so nothing was
  lost. `git reset --hard HEAD` was refused by the auto-mode guard, so I used the reversible route:
  `git stash push -m "accidental half-checkout of main ..."`, which restored the #37 tree. The
  stash (`stash@{0}`) only holds `main`'s tree and can be dropped by the user
  (`git stash drop`); I have not dropped it. Then `git checkout -b` from the #37 branch (A1)
  worked, so the permission error looks transient (a lock from another process).
- Why: the workflow says to start from an up-to-date `main`; this project's PRs are stacked, so
  the real base is the previous issue's branch (A1).
- Result: branch created at `57f9148`, tree clean.
- Next step: Q1.

### 2026-10-18 — Sources confirmed and cached; Q1 written
- What I did: confirmed 11 seed and own-choice leads on the arXiv API, then their published
  versions on Crossref (ACL 2016, AAAI 2018, AIES 2019, IROS 2017, AAMAS 2025, *Nature MI* 2019,
  *JAIR* 2022) and on the proceedings pages (NeurIPS 2017 and 2018, PMLR/ICML 2018). DBLP's API
  returned non-JSON, so I did not use it. Three searches for further Q1 work surfaced GenWorld
  (arXiv:2606.27650) and, for Q5, Plaza-del-Arco et al. (LREC-COLING 2024 workshop). Downloaded all
  13 arXiv PDFs to `refs/td_*.pdf`. The first `-layout` extraction interleaved the two columns, so
  I re-extracted all of them in reading order (no `-layout`).
- Q1 read: [Amano-MobilityLM] (full), [Chopra-Archetypes] (full), [Li-GenWorld] (keyword-led).
- Result / what I found:
  - **No Q1 source distils LLM decisions into a fast trained model and measures fidelity to the
    teacher on held-out situations**, except [Zhang-DFD] (already summarised). Amano's student is
    still a 20B LLM; GenWorld says outright it did not compare the table with fresh teacher calls;
    Chopra validates only against real aggregates.
  - The approach that actually reached large populations is a **lookup table keyed by binned
    context, filled by repeated LLM calls** (8.4 M agents in Chopra; about 200,000 in GenWorld at
    0.54 µs per lookup). It is not on the issue's list of model options; I am adding it to
    `options.md` as the baseline that trained models must beat. That is my call, not the issue's.
  - Amano found that fine-tuning on skewed labels exaggerates the majority class (74% → above 94%).
    That is a concrete risk for a decider trained on rule labels.
  - Seed lead status: Amano & Yamaguchi confirmed (accepted at SIGSPATIAL 2026, DOI not yet live).
- Next step: Q2 (Rudin, VIPER, Yang-S2AN cross-reference).

### 2026-10-18 — Q2 and Q4 written
- What I did: read [Rudin-StopExplaining] (full) and [Bastani-VIPER] (full); cross-referenced
  [Yang-S2AN] from its S3 entry and Zhang's PySR / LLM-SR baselines. Then Q4 (ahead of Q3, as the
  issue's priority order says): [Kusner-CF], [Garg-CFText], [Tamkin-Discrim], all full text.
- A mistake caught on re-check: my first VIPER draft said the extraction has a guarantee on the
  student's loss. Re-reading §2, that guarantee is for Q-DAgger; for trees the authors say the loss
  is not convex and they use CART "as a heuristic". Corrected before committing.
- An append via a bash heredoc failed on quoting (as the memory note on heredocs warns); I now
  write each section to a scratch file and append it.
- Result / what I found:
  - **Q2**: no source in this set compares an interpretable model *learned from labels* with a
    *hand-written* rule on the same task. Rudin is an argument (no trade-off on structured data,
    with the CORELS example); VIPER compares a tree with its neural teacher; S2AN compares a
    network, not an interpretable model, with hand-written rules. So the Q2 comparison the issue
    asks for is only half answered. Recorded in "Open questions".
  - **Q4**: the FYP's "no `ethnic_group` input" is fairness through unawareness, which Kusner et
    al. show is not sufficient when other inputs carry the attribute. But in a simulator the causal
    graph is ours, so the stronger condition (no feature descends from `ethnic_group`) can be
    checked from the scenario generator. The remaining channel is the **labels** of an LLM
    teacher. Garg's asymmetric counterfactuals fit the FYP's second rule: the test applies only
    where a rule says the attribute must not matter.
  - Tamkin et al. is by Anthropic about Anthropic's model; I flagged the conflict of interest in
    the entry, since this review is written with an Anthropic model.
- Next step: Q3 (reward machines, shielding, SA-CADRL).

### 2026-10-18 — Q3 and Q5 written; 13 entries in all
- What I did: Q3 — [Icarte-RewardMachines] (*JAIR* 2022; the ICML 2018 version confirmed on PMLR,
  pp. 2107–2116, but not read, since the journal version builds on it), [Alshiekh-Shielding]
  (arXiv long version; I flagged that its section numbers may differ from the AAAI paper),
  [Chen-SACADRL] (full). Q5 — [Hu-LogicRules] and [Plaza-ModelCrowds]; the latter's venue was
  confirmed from the ACL Anthology BibTeX (NLPerspectives @ LREC-COLING 2024, pp. 19–30). Checked
  `README.md` for the issue #16 finding (effects flip between models) and
  `llm_negotiation/docs/log-schema.md` for what `outcomes.jsonl` records: it includes each person's
  `ethnic_group`, which matters for the teacher discussion.
- Result / what I found:
  - **Q3**: none of the three tests carry-over **between simulators**. SA-CADRL's sim-to-robot
    transfer is the only transfer, and it is qualitative ("generally respected social norms", no
    number). A norm given as reward was followed about 85% of the time, not always. Shielding's
    guarantee is proved but relative to an abstraction that each simulator would need. Reward
    machines need a correct labelling function, which is the same job as the proposed perception
    adapter.
  - **Q5**: [Hu-LogicRules] is the only evidence on "does a model trained on rules help anyway",
    and it shows rules helping **alongside** human labels, most when labels are scarce, with the
    rule teacher beating its student. No source tests a student trained on rule labels alone.
    [Plaza-ModelCrowds] supports several LLM teachers (aggregate beats the best single model in
    most tasks), but in text classification and still well below human-label training.
  - **Count**: 13 full entries, one above the issue's 8–12 aim; every source in it was obtained, so
    `missing-papers.md` will list only versions not read.
- Next step: `options.md` (with the Q1–Q5 answers), `evaluation.md`, `verdict.md`.

### 2026-10-18 — Synthesis files, verification, README
- What I did: wrote `options.md` (§1 answers to Q1–Q5; §2 one table of seven options, every cell
  citing an entry or marked `[inference]`; §3 what the table cannot carry), `evaluation.md` (checks
  E1–E10 and bias checks B1–B7), `verdict.md` (Q6), `search-log.md`, `missing-papers.md`,
  `refs-trained-deciders.bib`, and a README row, findings block and layout lines.
- Decisions I made (flagged in the files as proposals):
  - Added an **LLM-filled lookup table** as an option, although the issue does not list it, because
    it is the only approach in the sources that reached large populations.
  - Put the Q1–Q5 answers in `options.md` §1, since the deliverables list has no separate file for
    them.
  - The checks and pass criteria in `evaluation.md` are mine.
- Verification (workflow §5b):
  - The key numbers were grepped against the cached extracts: 60 quoted values across 12
    extracts, plus Rudin's two (130+ factors, 7±2) and Zhang's DTW values against its summary.
    All were found. This is a check of the main figures, not of every number in every entry.
  - Every handle used in the three synthesis files resolves to an entry or a named
    cross-reference.
  - `verdict.md` cut from 666 to 563 words, to keep it to one page (#37's is 576).
  - Two wording overreaches corrected on re-read: VIPER's guarantee (see the Q2/Q4 entry above);
    and "a rule teacher beat its student", changed to "a rule-regularised teacher", because Hu et
    al.'s teacher is the network projected onto the rules, not the rules alone.
  - Two lead descriptions in the search log that came only from search snippets were removed
    (issue: do not summarise from abstracts).
- Next step: push, open the PR against the #37 branch, comment on the issue.

### 2026-10-18 — Pushed; PR #46 opened
- Pushed `docs/38-trained-deciders-literature`; opened PR #46 against
  `docs/37-unseen-scenario-human-evidence` (A1), and commented the link on #38.

## Open questions / risks

1. **Q2 is answered only in part.** No source compares an *interpretable model learned from
   labels* with *hand-written rules* on the same task. Rudin argues there is usually no accuracy
   loss; VIPER compares a tree with its neural teacher; [Yang-S2AN] compares a network, not an
   interpretable model. The verdict's main recommendation (train small trees first) therefore rests
   on argument and other domains, not on a direct test.
2. **No source tests carry-over of a trained decider between simulators** (Q3). SA-CADRL's
   sim-to-robot transfer is qualitative. The claim that trees and tables "are as portable as the
   rules" is my inference from their inputs.
3. **Only two sources are about pedestrian conflicts** ([Chen-SACADRL], [Fang-Etiquette]); the
   rest are evacuation, mobility, epidemics, control or text. Nothing here shows what happens in a
   queue.
4. **The lookup-table option is my addition**, not on the issue's list. It is presented as a
   baseline, and the supervisor may prefer to drop it.
5. **Evaluation pass criteria are mine** and mostly not yet set (tolerances, margins). The list of
   attributes that "must not matter" per conflict type does not exist yet; B3 cannot run without it.
   That is a supervisor decision (verdict, item (c)).
6. **B6 and B7 for `ethnic_group`** need the fictional group switched on in a teacher run, which
   waits for the supervisor's ethics sign-off (`WORK_LOG-32.md`, Q1). I did not switch anything on.
7. **Selection bias.** Only three web searches were run; ten of the 13 entries came from leads I
   knew (five named in the issue, five from memory), confirmed afterwards. Recent or less-cited
   work, especially on Q1 and Q3, is likely missed. Unread leads are in `search-log.md` §5.
8. **Conflict of interest**: [Tamkin-Discrim] is by Anthropic about Anthropic's model; this review
   was written with an Anthropic model. It is used only for its test design, not its findings
   about Claude.
9. **The 10,000-agent costs are my multiplication** of per-decision figures from different
   hardware, not measurements.
10. **13 entries**, one above the issue's 8–12 aim.
11. **Git state the user should know about.** The first `git checkout main` half-failed with
    "unable to write symref for HEAD: Permission denied" (probably a lock held by another program).
    I recovered with `git stash`, which left `stash@{0}` holding only `main`'s tree. It is safe to
    drop (`git stash drop stash@{0}`) and I have not dropped it.
12. **Branch base (A1)**: this branch stacks on #37's (PR #45), so the PR targets that branch and
    merging it will not close #38 automatically.

## Summary

**What changed.** A new folder, `literature/trained-deciders/`, answering issue #38's six
questions:
- `entries.md`: 13 entries plus cross-references to Zhang, Fang and Yang-S2AN;
- `options.md`: the Q1–Q5 answers, and one table of seven decider options;
- `evaluation.md`: fidelity, generalisation and cost checks E1–E10, and bias checks B1–B7,
  including the counterfactual test and the "no `ethnic_group` input" rule;
- `verdict.md`: one page, Q6;
- `search-log.md`, `missing-papers.md` (0 not obtained), `refs-trained-deciders.bib`.

Also: 13 arXiv copies and their text extracts in `refs/td_*`, and a README row, findings block and
layout lines. No code, no training, no paid calls; nothing in `llm_negotiation/` changed.

**Why.** Track #34, point 4, proposes trained models as alternative deciders behind the rules'
Situation → Decision interface. This issue checks the literature before anything is trained.

**Verdict, in one line.** Keep the rule engine as the reference. Train small trees on Situation
features first, against an LLM-filled lookup table, with LLM decisions from several models
(disagreement kept) plus the rules as teachers. Do not train RL policies now; use the rule engine
as a shield. Evaluate by held-out and closed-loop agreement, class shares, abstention and the bias
checks.

**How it was verified.** See the last progress entry: main numbers grepped against the extracts,
handles resolved, verdict length checked, two overreaches corrected. Every Q1–Q6 is answered;
Q2 and Q3 are marked as answered only in part, with the reason.
