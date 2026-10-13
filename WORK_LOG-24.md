# Work Log — Issue #24: [Feature] LLM negotiation simulator: reimplement GameChat, add age and gender personas, dynamic state, and conversation logging

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/24
**Branch:** `feat/24-llm-negotiation-simulator`
**Started:** 2026-10-13 14:45 (UTC+8)

## Understanding the issue

Build the experimental platform for the FYP's current direction: a small simulator in which two
agents that are about to conflict hold a natural-language negotiation through an LLM, and the
outcome of that negotiation (who goes first) drives their motion. The conversations are the
research output — rules will be extracted from the logs in a later issue — so logging is a
first-class deliverable, not an afterthought.

The design starts from GameChat (Mahadevan, Zhang, Chandra, arXiv:2503.12333) and extends it in
three ways: (1) personas with age and gender, (2) dynamic situational information (speed, size,
distance to the conflict region) available during the negotiation, (3) complete logging of every
conversation. The LLM is DeepSeek, behind a client interface with a deterministic mock so that all
tests run with zero spend, and behind a hard budget cap (USD 0.50 for this issue).

Everything goes in a new top-level folder `llm_negotiation/`. The Phase 1 folders (`pipeline/`,
`dataset/`) must not be touched or imported.

Out of scope (the issue lists these explicitly): rule extraction, race personas, more than two
negotiating agents, CrowdGym integration, scaling to 10,000 agents.

### Assumptions and judgement calls (mine, not instructions from the issue)

- **A1. Branch base.** The workflow says to branch from `main`. `main` (`5a0f7be`) holds only the
  Phase 1 dataset work: it has no `literature/`, no `refs/`, and a `README.md` without the current
  roadmap. Every issue since #8 is an open, stacked PR, each cut from the previous one
  (WORK_LOG-20 A1, WORK_LOG-22 A1). Later issues (rule extraction, validation against the human
  conflict-resolution literature) will need the simulator logs and the literature in one tree. I
  therefore cut this branch from the tip of the chain, `docs/22-simulation-conflict-rules-literature`
  (`a1aafb9`), and the PR will target that branch, as PR #23 targets #20's. Nothing in
  `llm_negotiation/` depends on the literature files, so rebasing onto `main` later is a one-line
  `git rebase --onto` plus the `README.md` hunk.
- **A2. Prerequisite check — passed on the issue's own terms, with a caveat I am not burying.**
  See the first progress entry and open question Q1.
- **A3. Reference branch of the GameChat repository.** The issue names branch `model-arcs`. That
  branch contains no LLM code; the GameChat dialogue code is on the default branch `main`. I
  follow `main` and document `model-arcs` as the issue asks. Evidence in the second progress entry.

## Plan

1. Preconditions, branch, this log. **(done)**
2. Read the sources before writing code: GameChat repository (both branches, read not run),
   the paper (arXiv v1 HTML and the cached v2), DeepSeek's official API docs as of today.
   **(done)**
3. Design, recorded in `llm_negotiation/docs/architecture.md`, with every design decision marked
   as a decision.
4. Core simulator: unicycle dynamics, world, geometry, the three scenarios (doorway,
   intersection, hallway).
5. Conflict layer: conflict region and detection, time to region, Strategy 1 role assignment,
   the generalised follower speed bound; derivation in `docs/derivations.md`.
6. Control layer: one controller interface, path-tracking backend. MPC-CBF only if it can be done
   cleanly; otherwise documented as a follow-up.
7. Personas (YAML schema, loader, validation) and prompt rendering with per-attribute visibility.
8. Situation report (observation to text) with individually switchable fields.
9. LLM layer: client interface, DeepSeek client, mock client, pricing, spend ledger, budget guard.
10. Negotiation protocol: JSON turn format, parsing with one retry, consensus on complementary
    stances, both timing modes.
11. Run logging (config, conversation, trajectory, outcome, transcript, summary) with a versioned
    schema; metrics.
12. Experiment configs for C0–C4, the runner, counterbalancing of speaking order and spawn side.
13. Tests on the mock client (unit + integration).
14. Live smoke runs within the cap: C1 (6 doorway runs) and C2 (6 hallway runs). Check the issue
    for a reply to Q1 before spending anything.
15. Docs, README, verification of every acceptance criterion, PR.

## Progress log

### 2026-10-13 14:45 — Preconditions, issue read, prerequisite check

- What I did: checked the remote, `gh auth status` (OK), working tree (clean), fetched `origin`.
  Read the issue (no comments on it). Performed the prerequisite check the issue asks for.
- Why: workflow steps 0–1, and the issue's "Prerequisite check" section, which says to stop if
  `CLAUDE.md` still tells me not to write simulation code until the literature review is complete.
- Result / what I found:
  - `CLAUDE.md` on `origin/main` and on this branch are byte-identical (`git diff origin/main HEAD
    -- CLAUDE.md` is empty). Neither contains the instruction. **The stop condition as the issue
    wrote it is not met.**
  - I then looked for the instruction elsewhere, because a check that passes only because I
    looked in one place is not much of a check:
    - `CLAUDE.md` **does** contain it on one branch: `origin/docs/5-biweekly-update-1`
      (commit `1d4a338`, 2026-09-12, lines 25 and 59 — "don't proceed past it even if asked to
      'just get started' without an explicit note that the review is done"). That branch is PR #7,
      still open, and is not an ancestor of `main` or of this branch. Every branch since issue #8
      was cut from a lineage that never received that edit, so **the `CLAUDE.md` Claude Code has
      been loading since 2026-09-12 is the older, pre-instruction version.** It still describes the
      Phase 1 dataset as the current task.
    - `README.md:24-25` on this branch chain **does** contain it: "Standing supervisor
      instruction: no new dataset generation and no simulation or experiment code until the
      literature review is complete and discussed." Roadmap rows 2 and 3 in the same file read
      "blocked on step 1 discussion" and "not started".
    - Nothing in the repository records the instruction being lifted.
- Decision: **proceed.** The issue defines the gate as the contents of `CLAUDE.md`, the user
  wrote that gate and then asked for this issue to be worked, and by that test the gate is open.
  But the test passes because of which branch the edit landed on, not because anyone removed the
  instruction, so I am treating this as a finding to report rather than a box ticked. It is open
  question **Q1** below, it goes in the first issue comment and at the top of the PR, and I will
  re-read the issue for a reply before making any paid API call.
- Next step: read the sources.

### 2026-10-13 15:10 — Sources read: GameChat repository, paper v1 and v2, DeepSeek docs

- What I did:
  - Cloned `github.com/vgmahadevan/GameChat` into the session scratchpad with `--no-checkout`
    and read files through `git show`. Nothing was checked out, installed or executed.
  - Downloaded the arXiv v1 HTML and extracted its text (keeping the LaTeX of each formula);
    re-read the v2 text already cached in `refs/mahadevan2025_gamechat.txt`.
  - Downloaded ten pages of DeepSeek's official API documentation (`api-docs.deepseek.com`).
- Why: the issue lists eleven facts to verify against paper and repository, and says not to
  take prices or model names from memory.
- Result / what I found:
  - **The GameChat code is on `main`, not `model-arcs`.** `main` (`c49c35a`, 2025-03-06) has
    `LLM_utils.py`, the dialogue loop in `main.py`, and `openai` in `requirements.txt`.
    `model-arcs` (`2f9c652`, 2024-11-30) is the LiveNet learned-controller branch: a search of its
    `.py`/`.txt`/`.md` files for `openai|gpt-4|LLMAgent|llm` finds nothing, and `git log -S` over
    its history finds no commit that ever added `openai` or `LLMAgent`. The two branches diverged
    at `9549830` (2024-10-25); 6 commits are only on `main`, 69 only on `model-arcs`. The paper's
    project page links the repository without naming a branch.
  - **License:** MIT, "Copyright (c) 2022 Elena Oikonomou" — the notice is inherited from the
    upstream `mpc-cbf` project the repository was forked from, not written by the GameChat authors.
  - **All eleven listed facts check out against the v1 paper**, with the section references the
    issue gives (they follow v1's numbering; v2 renumbers the results table from II to III and
    drops the dynamics equation).
  - **The "garbled formula" in Sec IV-B is not garbled in the paper.** The LaTeX in the v1 HTML
    is `\frac{d_i v_max}{l+d_j}` in Sec IV-B, in the proof of Theorem IV.1, and in Sec IV-D — the
    same expression three times. It only looks broken in the PDF text extract, where the fraction
    is split over three lines (`refs/mahadevan2025_gamechat.txt` lines 192–194).
  - **The repository disagrees with the paper in at least seven places** that matter here: the
    follower speed rule (a hard-coded 0.25 m margin on both distances, `mpc_cbf.py:237-239`), the
    conflict test (a "liveliness" angle threshold, not overlapping occupancy intervals,
    `mpc_cbf.py:217`), the prompt text, the hospital task strings, the maximum runtime (20 s vs
    15 s), the collision threshold (centre distance 0.15 m for two 0.1 m-radius agents), and the
    passage widths (0.5 m clear vs 0.4 m). All recorded with line references in
    `llm_negotiation/docs/gamechat-notes.md`.
  - **DeepSeek has changed since Phase 1.** The documented models are now `deepseek-flash`
    (DeepSeek-V4.1-Flash) and `deepseek-v4-pro`; `deepseek-chat`, which `pipeline/config.py` uses,
    is no longer in the model list and was announced for discontinuation on 2026-07-24. Thinking
    mode is on by default and **temperature has no effect in thinking mode**, so the client must
    switch thinking off for the temperature setting to mean anything. Pricing is now split into
    peak and off-peak hours. There is no `seed` parameter.
- Next step: design, then code.

## Open questions / risks

- **Q1 — needs the user's confirmation: has the supervisor's "no simulation code until the
  literature review is complete and discussed" instruction been lifted?** `CLAUDE.md` on this
  branch does not carry it, so the issue's prerequisite check passes and I went ahead. But
  `README.md:24-25` on this branch still states it, `CLAUDE.md` on the unmerged
  `docs/5-biweekly-update-1` branch still states it, and no file records it being lifted. If it
  has not been lifted, this PR should simply stay unmerged; nothing here touches Phase 1 or the
  literature. Either way `CLAUDE.md` needs the user's attention: the version in force describes
  the Phase 1 dataset as the current task and does not mention this platform.

## Summary (fill in at the end)
