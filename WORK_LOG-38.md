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

## Open questions / risks

## Summary (fill in at the end)
