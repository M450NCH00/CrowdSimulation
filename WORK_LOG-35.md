# Work Log — Issue #35: [Research] PT-1 Literature: simulator-independent rule representations (is a portable rule core feasible?)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/35
**Branch:** `docs/35-simulator-independent-rule-representations`
**Started:** 2026-10-18

## Understanding the issue

Every rule this repository extracts is written in negsim's own terms: geometric encounter
classes, ORCA directive fields, thresholds tuned to ORCA, and at most two roles
(`llm_negotiation/docs/rule-format.md` §§2–7; issue #34, "Why this track exists"). Issue #34
proposes, **without anyone's agreement yet**, a *portable rule core*: a rule written once over a
fixed, versioned vocabulary (conflict types, roles, features, actions), carried out by each
simulator through a perception adapter and an action adapter, checked by shared conformance
tests, and tested on unseen scenarios.

This issue does not build any of that. It asks the literature one question: **can a conflict
rule be written down once, independently of any simulator, and still be carried out faithfully by
several different simulators?** In six parts:

- **Q1** how other fields write rules or norms independently of the system that follows them
  (institutional grammar, normative MAS, and one simulation interoperability standard, with what
  made "write once, run in many" work there and what limits it);
- **Q2** whether any crowd, pedestrian, game or robot-navigation study ran the *same behaviour
  rule* in two or more simulators, kept apart from studies that run different simulators on the
  same scenario;
- **Q3** existing taxonomies or ontologies the vocabulary could adopt;
- **Q4** the failure modes of abstracting a rule away from its simulator, with evidence;
- **Q5** novelty: arXiv:2409.00993 read in full, plus a search for LLM-derived norms written down
  for reuse by other systems;
- **Q6** a verdict (feasible / feasible with changes / not supported) and a recommended
  representation (adopt IG 2.0, adapt it, or extend this repository's own format).

The answer has to be bounded by what the entries support; the game-theory review already says
the "generic simulator" requirement is a design goal, not a finding
(`literature/game-theory/g6-transfer-across-games.md`, "What this means for the FYP", point 1).

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** The workflow says branch from `main`, but `origin/main` is still
  `5a0f7be` and has none of the four files this issue says to read. Every branch since #8 is
  stacked on the one before; for #30 and #32 the user was asked and chose to stack each time
  (`WORK_LOG-30.md` P2, `WORK_LOG-32.md` P1). I therefore cut this branch from
  `feat/32-fictional-ethnicity-passage-meetings` (`81d85f8`, PR #33's head, in sync with
  origin) and will target the PR at that branch. A merge into a non-default branch will not
  close #35 by itself.
- **A2. Cache prefix.** Sources for this issue are cached as `refs/pr_*` (portable rules),
  following `gt_*` (#20) and `sr_*` (#22). PDFs are tracked as before unless oversized; those
  go in `.gitignore` with a re-download link, as in #20 and #22.
- **A3. One section read beyond "these, and only these".** I also read #34's "Constraints for
  every issue in this track", because those constraints bind this issue (no paid calls; no change
  to `llm_negotiation/`; mark decisions and assumptions; nothing may switch the group on).
- **A4. Stubs** for sources I cannot open live in `representations.md` under their group, with
  exactly the issue's six lines, and are listed in `missing-papers.md` (#22's A2 reading).
- **A5. "Read in full"** means the whole body text, read from the cached extract; reference
  lists and appendices only where a claim needs them. An entry read only in part says which
  sections.
- **A6. Extra entry group.** Q2 needs studies that are none of the five seed groups (model
  docking and replication; same controller in several robot simulators). They go in a sixth group
  in `representations.md`, "Precedent: the same rule in more than one simulator".

## Plan

1. Branch and work log. **(done)**
2. Read what the issue lists, and only that (A3 aside). **(done)**
3. Read arXiv:2409.00993 in full from `refs/gt_arxiv_2409_00993.txt`; check for a published
   version.
4. Confirm every seed lead from its own page (arXiv API, Crossref, publisher or journal page);
   resolve the `[unverified lead]`s; download what is open, check each first page against the
   expected title, cache text as `refs/pr_*`.
5. Targeted searches, each logged with its query and outcome: Q2 (same rule in two or more
   simulators), Q3 (taxonomies of pedestrian situations and conflicts), Q5 (LLM-derived norms
   written down for reuse).
6. Write the entries (`representations.md`), grouped as the seed leads are, plus A6's group.
7. `novelty-check.md`.
8. `feasibility.md`: the idea restated in my own words with what is unclear or inconsistent in
   it, then Q1–Q6, every claim citing an entry.
9. `verdict.md`, one page at most, written for PT-7.
10. `search-log.md`, `missing-papers.md`, `refs-portable-rules.bib`.
11. Check every acceptance criterion and workflow §5b; post progress comments at milestones;
    push; open the PR against PR #33's branch; comment on the issue.

## Progress log

### 2026-10-18 — Preconditions, branch, and the required reading
- What I did: checked preconditions (remote `M450NCH00/CrowdSimulation`, `gh` authenticated,
  tree clean, not a linked worktree); read the issue (no comments) and the four items it lists:
  #34 "Why this track exists" and "The idea"; `g6-transfer-across-games.md` "What this means for
  the FYP"; `research-gap.md` §3 and §5; `rule-format.md` §§1–7. Also #34's constraints (A3).
- Why: workflow steps 0–3; the issue's "Before starting".
- Result / what I found:
  - `origin/main` has none of the four files; they exist only on the stack (A1).
  - Three things in the reading that shape the search: (1) the review of 35 simulator rules found
    **no source that evaluates one rule with two different kinds of agent** (`research-gap.md`
    §3(a)), so Q2 needs a search of its own; (2) the same review separates a rule's *form*
    (portable) from its *content* (a local convention, e.g. which side) (§3, on
    [Pruekprasert-RightOfWay]); (3) today's format already treats "what a rule may read" as a
    question of what **both** agents can compute identically (`rule-format.md` §5). That is a
    conformance question in miniature, and it is where Q4's "two implementations of the same term
    disagree" would bite.
- Next step: the novelty paper, then the seed leads.

## Open questions / risks
<Anything uncertain, anything you're unsure is the right call, anything that should be double-checked by a human.>

## Summary (fill in at the end)
<What changed, why, how it was verified.>
