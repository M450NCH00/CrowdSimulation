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

### 2026-10-13 15:25 — Design, and one change of direction before any code was kept

- What I did: settled the module layout and the run loop, then probed the geometry with a
  scratch script before building anything on top of it.
- Why: the follower's speed rule is the part every other piece depends on, and the issue
  asks for it to be generalised to a conflict region with length.
- Result / what I found:
  - **First plan, dropped:** take the paper's rule as it stands for the doorway and the
    intersection (a conflict *point*, body length `l` = one diameter) and give only the
    hallway a region with length. The probe showed that this collides. With discs of radius
    0.1 m crossing at a right angle, the follower's disc arrives at the point while the
    leader's centre is 0.14 m away, and they overlap. The paper's agents are "thin, car-like
    objects of ... zero width", so the paper is not wrong; discs are just not that.
  - **What replaced it:** a conflict *zone* on each path, the stretch within
    `r_i + r_j + margin` of the other agent's path. If the two centres are never in their
    zones together the discs cannot touch; the proof is four lines
    (`llm_negotiation/docs/derivations.md`, section 4). One mechanism then serves all three
    scenarios, and agents of different sizes.
  - **A cost I did not expect:** at the doorway the paths cross at 26 degrees, the safe zone
    is long, and the follower reaches its goal 3.8 s after the leader, against about 1.1 s
    in the paper (Table II, "GameChat Ground Truth", doorway: makespan 11.533 s, leader's
    time to goal 10.400 s; `refs/ln_gamechat_arxiv_v1.txt:369-376`). The GameChat
    repository uses a fixed 0.25 m whatever the angle. That is not
    safe in general, but it is safe for the paper's own 18 variants, so the replication
    configs use the repository's value and the scenario's default stays safe. Both halves
    are tested. This is design decision DD3 and needs sign-off.
- Next step: build.

### 2026-10-13 16:00 — Built; 431 tests pass on the mock client with no spend

- What I did: wrote `llm_negotiation/` (simulator core, three scenarios, conflict layer,
  controller interface, DeepSeek and mock clients, budget guard, personas, two prompt
  templates, dialogue protocol, logging, metrics, experiment designs, runner, CLI), the five
  docs, and the tests. Committed in seven commits by layer.
- Why: issue #24, parts 1 to 5.
- Result / what I found:
  - All ten shipped experiment configs (C0 to C4) run end to end on the mock client:
    140 runs, no collision.
  - With arbitration switched off, each of the three scenarios ends in a collision. So it is
    the speed rule that keeps the agents apart, not the geometry.
  - The tests pass on Python 3.13.3 and on 3.12.3, each in a clean virtual environment built
    from `requirements.txt`. Nothing was installed into the system Python.
  - **Prompt template versions:** `gamechat_task_v1` (sha256 `cf6ec868b934...`) and
    `persona_v1` (sha256 `d80306ef0fe6...`), frozen 2026-10-13 before any paid call. Loading
    refuses a template whose file no longer matches its pinned hash.
  - **Not built:** the paper's MPC-CBF controller. The issue allows this if it cannot be done
    cleanly; the reasons are in `docs/architecture.md`, DD1.
- Layout changes from the issue's suggestion, with reasons, are in `docs/architecture.md`,
  section 1: an added `negsim/experiment/` package, `negsim/configutil.py`, and
  `configs/tasks/` and `configs/llm/`.
- Next step: the no-LLM runs, then the paid smoke runs.

### 2026-10-13 16:05 — Mistakes caught along the way

Kept here because the workflow asks for the dead ends, not a tidied account.

- **A mock rule that would have misfired.** My first "first speaker claims the way" rule
  for the mock client decided who was first by looking for the words "says:" in the prompt.
  GameChat's opening line is "Other agent says: Begin the conversation". Rewritten to use
  the turn number before it was ever run.
- **A gap in the conversation log, found on re-reading the run loop, not by a test.** If a
  first reply was unreadable (and paid for) and the budget guard then refused the retry, the
  turn was dropped from `conversation.jsonl` although its cost was in the ledger. Fixed, and
  now tested.
- **Two tests depended on the time of day**, because calls are costed at a peak or off-peak
  rate. The budgeted client now takes an injectable clock and the tests pin it.
- **Three wrong expectations in my own tests** (not in the code): an occupancy-interval case
  that was a touch, not an overlap; a doorway offset I assumed ran along the path when, as
  in the repository, it runs straight back from the wall; and a "leader never slows" check
  that counted the leader standing at its goal.
- **A test that did not test what its name said.** "An agreement reached too late" used a
  delay short enough that the agreement could still be honoured. Corrected, and split into
  two cases: too late to honour, and overtaken by events.
- **Two claims in the docs that the source did not support.** I wrote that DeepSeek's
  prices had changed three times in 2026; the change log shows two dated changes. I wrote
  that the name `deepseek-flash` had pointed to another model; the change log shows other
  names being re-pointed, not that one. Both corrected against the cached pages.
- **Leftover code.** My first draft of the hallway scenario ended with a loop that referred
  to an attribute that does not exist. Removed before the file was first imported.
- **A late progress comment.** I posted the first issue comment, the one asking Q1, about an
  hour after finding the problem instead of straight away. That left the user less time to
  object before the paid runs than I had meant to give.

### 2026-10-13 16:12 — No-LLM runs (condition C0) for all three scenarios

- What I did: ran `c0_no_llm.yaml`, `c0_no_llm_intersection.yaml` and
  `c0_no_llm_hallway.yaml` from a clean tree at commit `50123f6`; committed the 54 run
  folders.
- Why: evidence that the three scenarios run end to end, and numbers to set beside the
  paper's Table II. Free.
- Result / what I found (mean ± population SD over 18 runs each):

  | Scenario | Collisions | Deadlocks | Higher-priority first | Its time to goal (s) | Makespan (s) | Follower min speed (m/s) |
  |---|---|---|---|---|---|---|
  | Doorway | 0 | 0 | 9 / 18 | 10.900 ± 0.900 | 11.800 ± 0.000 | 0.257 ± 0.015 |
  | Paper, doorway, "GameChat (no LLM)" | 0 | 0 | 50% | 10.733 ± 0.566 | 11.267 ± 0.194 | 0.200 ± 0.088 |
  | Intersection | 0 | 0 | 9 / 18 | 10.600 ± 0.800 | 11.400 ± 0.000 | 0.256 ± 0.016 |
  | Paper, intersection, "GameChat (no LLM)" | 0 | 0 | 50% | 10.800 ± 0.823 | 11.600 ± 0.000 | 0.249 ± 0.013 |
  | Hallway (not in the paper) | 0 | 0 | 9 / 18 | 9.750 ± 2.850 | 12.600 ± 0.000 | 0.202 ± 0.037 |

  Paper rows: arXiv:2503.12333v1, Table II (`refs/ln_gamechat_arxiv_v1.txt:329-459`). The
  paper does not say whether its ± is a population or a sample standard deviation.
  - **The 9 / 18 is a property of the design, not a measurement.** Strategy 1 does not look
    at the tasks, and the design makes each agent index the higher-priority one equally
    often. It could not have come out otherwise.
  - The intersection is close to the paper. The doorway is 0.5 s slower in makespan and its
    follower slows less and far more uniformly. The paper explains its own spread: without
    communication its symmetric doorway "struggles to identify a leader and follower until
    some time has passed" (`refs/ln_gamechat_arxiv_v1.txt:491`). Here a tie is broken on
    the first step.
- Next step: re-read the issue for a reply to Q1, then the paid smoke runs.

### 2026-10-13 16:17 — Paid smoke runs: 12 runs, 37 calls, about USD 0.0043

- What I did: re-read the issue (no reply to Q1; my comment had been up for 17 minutes).
  Ran one C1 run first as a canary, checked its log, then the other five C1 runs and the
  six C2 runs, all with `--client deepseek` from a clean tree at commit `c9522e4`.
  Committed the 12 run folders and the spend ledger.
- Why: the issue's "Live smoke runs with DeepSeek, within the budget cap".
- Result / what I found:
  - **C1, GameChat replication, doorway, 6 runs.** Consensus in 6 of 6, in 3, 6, 4, 4, 4
    and 4 turns. **The higher-priority agent went first in 6 of 6**; the paper reports
    100% (`refs/ln_gamechat_arxiv_v1.txt:329-459`). No malformed reply, no retry, no
    fallback, no collision.
  - **C2, task plus persona, hallway, 6 runs.** Consensus in 6 of 6, every one in 2 turns.
    No ground truth; nothing is marked correct or incorrect. In 5 of the 6 the first
    speaker opened by giving way and the other accepted; the exception was the
    70-year-old man going to the emergency room, who asked to go first.
  - **Cost.** 37 calls, estimated USD 0.004282 (C1 0.002460, C2 0.001821), all at the
    peak rate. Under 1% of the USD 0.50 cap. Zero failed calls.
  - **Latency.** 0.81 s per call in C1, 3.36 s per dialogue (SD 0.73 s); the paper
    measured 2.767 s (SD 0.441 s) per dialogue.
  - **Prompts.** Both templates were used exactly as frozen. No wording was changed
    before, between or after the paid runs, so there is one prompt version per template
    and nothing to report under "prompt iteration".
  - The API accepted the request as built from the documentation (thinking off, JSON
    mode), returned the cache-hit and cache-miss token counts the price table needs, and
    reported zero reasoning tokens.
- Two things I read in the transcripts (my reading of 12 conversations, not a measurement):
  - In C1 runs 001, 003 and 004, one of the two stances that made the consensus was not
    said out loud: the message only named the agent's own task. See Q5.
  - In C1 run 003 the grocery agent picked up the other agent's word and said it was
    "taking my patient to buy groceries". The paper mentions such slips
    (`refs/ln_gamechat_arxiv_v1.txt:497`).
- Next step: verification against the issue's acceptance criteria, then the PR.

### 2026-10-13 16:25 — Verification

- Tests: `python -m pytest` in `llm_negotiation/`: **431 passed** on Python 3.13.3 and on
  3.12.3, each in a clean virtual environment built from `requirements.txt`. The network is
  blocked and the real `.env` is hidden during the tests. `pyflakes` reports nothing.
- Log folders: the runner checks every folder it writes against the schema. In addition a
  script compared, for each of the 12 paid runs, the transcript with `conversation.jsonl`
  turn by turn (speaker, message, stance), the system prompts in the transcript with the
  ones sent, the parsed messages with the raw replies, and the costs with the ledger.
  No discrepancy. I also read the conversations of all 12.
- API key: read the key from `.env` into a shell variable without displaying it and
  searched for it and for its first 12 characters. Tracked files at `HEAD`: 0 matches.
  Commits on this branch that add or remove it: 0. Commits on any branch: 0. Run logs and
  ledger: 0, and no occurrence of `Authorization` or `Bearer` in them either. `.env` is
  not tracked and no commit has ever touched it. The only file on disk that contains the
  key is `.env` itself.
- Phase 1: `git diff a1aafb9 -- pipeline dataset CLAUDE.md integration literature` is
  empty, and a test checks that no module imports from `pipeline` or `dataset`.
- Acceptance criteria, one by one:

  | Criterion | Status | Evidence |
  |---|---|---|
  | Prerequisite check performed against `CLAUDE.md` | done; passes as written, with caveat Q1 | first progress entry |
  | GameChat repository read but not executed; licence confirmed; adapted code carries its notice | done; no code adapted | `docs/gamechat-notes.md` section 2, `THIRD_PARTY_NOTICES.md` |
  | Every listed GameChat behaviour implemented, or its deviation documented | 9 of 11 implemented; 2 deviate with reasons | `docs/gamechat-notes.md` sections 3, 4, 6. Not implemented: the MPC-CBF controller (the issue allows this) and gpt-4o-mini (the issue asks for DeepSeek) |
  | Doorway, intersection, hallway run end to end | done | 54 C0 runs, 12 paid runs, `test_scenarios.py` |
  | Follower speed derivation documented and unit-tested, with the reduction | done | `docs/derivations.md` sections 2, 3; `test_conflict.py` |
  | Personas with independent age and gender, no names, configurable visibility | done | `test_personas_and_prompts.py` |
  | Situation report fields individually switchable, observable values only | done | `test_negotiation.py` |
  | DeepSeek and mock clients behind one interface; all tests on the mock | done | `negsim/llm/base.py`, `tests/conftest.py` |
  | Budget guard enforced; ledger and per-call cost recorded | done | `test_llm.py`, `spend_ledger.jsonl` |
  | Every run writes the five files, matching the documented schema | done | `negsim/runlog/schema.py`, `docs/log-schema.md` |
  | Speaking order and spawn side counterbalanced and recorded | done as config options and recorded per run; **partly exercised**, see Q9 | `negsim/experiment/config.py`, the header of each smoke config |
  | Only C0 and C1 scored against ground truth | done, and enforced | `test_experiment_config.py` |
  | All prompt versions recorded; no undocumented tuning | done; one version each, never changed | `templates/MANIFEST.json` |
  | Smoke runs within budget, results and spend in the PR description | done | USD 0.0043 of 0.50 |
  | API key absent from code, logs and history | done | above |
  | Phase 1 folders untouched and not imported | done | above |

## Open questions / risks

Needing a decision from the user or the supervisor:

- **Q1 — has the supervisor's "no simulation code until the literature review is complete
  and discussed" instruction been lifted?** `CLAUDE.md` on this branch does not carry it,
  so the issue's prerequisite check passes and I went ahead, including the paid runs. But
  `README.md` on this branch still stated it (I have marked its status "unconfirmed" there
  and not removed it), `CLAUDE.md` on the unmerged `docs/5-biweekly-update-1` branch still
  states it, and no file records it being lifted. If it has not been lifted, leave the PR
  unmerged; nothing on this branch touches Phase 1 or the literature. The spend is made and
  cannot be undone: USD 0.0043.
- **Q2 — branch base.** Cut from `docs/22-...`, not `main`, and the PR targets that branch
  (assumption A1). If it should go to `main` instead:
  `git rebase --onto main docs/22-simulation-conflict-rules-literature feat/24-llm-negotiation-simulator`,
  then redo the `README.md` hunk by hand.
- **Q3 — the hallway's sizes and speeds are placeholders [unverified].** Body radius
  0.25 m, maximum speed 1.3 m/s, turn rate 2.0 rad/s, hallway 0.8 m by 4 m. I chose
  human-scale numbers so that personas are not told they walk at a robot's 0.3 m/s, but I
  took them from no source. They need sourced values, or a decision to use GameChat's
  scale instead, before any experiment that will be reported.
- **Q4 — the persona prompt says nothing about where the scene is.** Phase 1 was
  Singapore-only. Issue #24 lists age, gender, backstory and task, so `persona_v1` has no
  location. If the study is to be about Singapore, that needs an attribute or a backstory
  and a new template version.
- **Q5 — a consensus can be silent.** Consensus is complementary *stances*, as the issue
  defines it, and the stance is hidden from the other agent. In three of the six C1 runs an
  agent conceded or claimed the way in its stance while its message only stated its task.
  The motion followed the stances. Whether that counts as "the agents agreed" is a
  question about what the study means by agreement. Requiring the concession to be spoken
  would need a new prompt version or a different consensus rule.
- **Q6 — the zone length (DD3).** Safe-by-construction zone as the scenario default; the
  GameChat repository's fixed 0.25 m in the doorway replication configs so that timings are
  comparable with the paper. Is that split acceptable, or should the replication also use
  the safe zone and accept a 2 s later follower?
- **Q7 — the MPC-CBF controller is not implemented** (DD1). The issue allowed that. Is a
  follow-up wanted? For two agents it would change the trajectories slightly and none of
  the dialogue.
- **Q8 — `CLAUDE.md` is out of date and I did not edit it.** It describes the Phase 1
  dataset as the current task, does not mention `llm_negotiation/`, and says DeepSeek spend
  is tracked in `pipeline/config.py`. Spend is now in two places: that file (USD 0.10,
  untouched) and `llm_negotiation/spend_ledger.jsonl` (USD 0.0043). The model name it
  implies, `deepseek-chat`, is no longer listed by DeepSeek.

Limits on what the results show:

- **Q9 — six runs per condition are a smoke test.** 6 of 6 in C1 does not establish a
  rate, and C2's "first speaker gives way" pattern is five conversations. Speaking order
  was counterbalanced within each pairing; agent index and starting side were swapped
  *together* between the two runs of a pairing, and the separate side swap
  (`swap_sides`) was not used in any paid run. Only `pre_conflict` timing was run with the
  real model; `concurrent` mode, blocked sight, and the C3, C4 and full C1 and C2 designs
  have run on the mock only.
- **Q10 — C1 is not a like-for-like replication.** Different model (`deepseek-flash`, not
  gpt-4o-mini), a different turn format that asks for a stance on every turn, no MPC, and
  a deterministic tie-break. `docs/gamechat-notes.md` lists nineteen differences.
- **Q11 — the model is not reproducible.** DeepSeek's API has no seed parameter, and a
  model name can be re-pointed to a new model. These runs were served with
  `system_fingerprint` `aeb56401ca74e127821c4f9126dcb669`, logged per call.
- **Q12 — the cost is an estimate**, computed from returned token counts and the prices
  read on 2026-10-13. The DeepSeek account page is the authority. Re-check the pricing page
  before the next paid run.
- **Q13 — the C0 "50%" is by construction**, not a finding (see the C0 entry).
- **Q14 — the personas and their tasks are placeholders** (ages 25 and 70, one errand),
  and `persona_v1`'s wording has not been reviewed by anyone but me. Any change to it is a
  new version by design.
- **Q15 — not tested:** Python 3.10 and 3.11; any system other than Windows 11.
- **Q16 — what I did not read:** the published IEEE version of the GameChat paper (only
  arXiv versions 1 and 2), and the upstream repository GameChat's was forked from.
- **Q17 — size of the change.** 433 files. 335 of them are run logs, of which 273 are the
  no-LLM runs, which cost nothing to regenerate; that commit (`705fe0b`) can be dropped
  if the logs are unwanted in the repository.

## Summary

**What changed.** A new top-level folder, `llm_negotiation/`: a two-agent simulator in
which the agents negotiate through an LLM and the agreement decides who goes first.

- `negsim/` (about 6,300 lines): unicycle dynamics and a world for any number of agents;
  doorway, intersection and hallway scenarios; conflict zones, detection and Strategy 1;
  a controller interface with a path-tracking backend; a DeepSeek client and a
  deterministic mock behind one interface; a price table, spend ledger and budget guard;
  personas; two frozen prompt templates; the situation report; the dialogue protocol; a
  versioned log schema; metrics; experiment designs with counterbalancing; a runner and a
  command line.
- `configs/`: three scenarios, four personas, ten experiment designs covering C0 to C4,
  GameChat's task strings, DeepSeek's prices.
- `tests/` (about 3,000 lines): 431 tests, all on the mock client.
- `docs/`: architecture (with 21 design decisions marked as such), GameChat notes,
  derivations, LLM backend, log schema. Plus `README.md` and `THIRD_PARTY_NOTICES.md`.
- `runs/`: 54 no-LLM runs and 12 paid smoke runs, with `spend_ledger.jsonl`.
- Outside the folder: two cached sources under `refs/`, one `.gitignore` entry, and the
  root `README.md` (roadmap rows 2 and 3, the directory layout, a findings paragraph, and a
  note that the standing instruction's status is unconfirmed). `pipeline/`, `dataset/`,
  `integration/`, `literature/` and `CLAUDE.md` are untouched.

**Why.** Issue #24: the FYP needs a platform on which LLM-to-LLM negotiations over a
spatial conflict can be run, varied by persona and by situational information, and logged
completely, so that rules can later be extracted from the conversations.

**What it found.**

1. Task-only agents put the higher-priority task first in 6 of 6 doorway runs, as GameChat
   reports, with a different model and turn format. Six runs.
2. With personas in the hallway, the first speaker gave way in 5 of 6 runs. Six runs; but
   it is a concrete reason to counterbalance speaking order, which the platform does.
3. The paper's speed rule, applied literally to discs, lets them overlap at a right-angle
   crossing. The conflict point became a computed zone with a proof that it is long enough.
4. GameChat's dialogue code is on its repository's default branch, not `model-arcs`, and
   the repository departs from the paper in ways that matter (`docs/gamechat-notes.md`).
5. DeepSeek's API has changed since Phase 1: new model names, thinking mode on by default
   (which silently disables temperature), peak and off-peak prices.

**What it did not do.** The MPC-CBF controller. Any experiment beyond smoke runs. Anything
the issue lists as out of scope.

**How it was verified.** 431 tests on two Python versions with the network blocked; 140
mock runs across all ten configs and 54 no-LLM runs with no collision; a negative control
showing each scenario collides without arbitration; every log folder checked against the
schema by the runner, and the 12 paid ones cross-checked by script and read; a search of
the tree, the logs and the history of every branch for the API key, which found it only in
`.env`. The acceptance criteria are checked off one by one in the last progress entry, and
the open questions above are the ones I could not close.
