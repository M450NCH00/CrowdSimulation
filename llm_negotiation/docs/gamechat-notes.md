# GameChat: what was read, what it says, and where this project departs from it

GameChat (Mahadevan, Zhang and Chandra, arXiv:2503.12333) is the design this platform
starts from. This file records what the paper and its public code say, with locators, and
every place where `llm_negotiation/` does something different, with the reason.

Read on 2026-10-13 for issue #24. Nothing from the GameChat repository was run, installed
or copied; see section 2.

## 1. Sources

| Source | What it is | Where to re-check it |
|---|---|---|
| Paper, version 1 | arXiv:2503.12333v1, 16 Mar 2025. **All section, equation and table numbers in this file are version 1's**, as in issue #24. | `refs/ln_gamechat_arxiv_v1.txt` (text from the arXiv HTML; formulas kept as LaTeX). Locators below are written `v1:LINE`. |
| Paper, version 2 | arXiv:2503.12333v2, 9 May 2026. | `refs/mahadevan2025_gamechat.txt` and `.pdf` (cached for issue #14). Written `v2:LINE`. |
| Repository | `github.com/vgmahadevan/GameChat`, cloned 2026-10-13. | Branch `main` at `c49c35ac49f3e5f4a08b03638e943ca77763763c`; branch `model-arcs` at `2f9c6528cb19df252d4927daddc4683632fae336`. Locators are `file:line` on `main` unless a branch is named. |
| Project page | `gamechat-uva.github.io` | Links the repository with no branch named. Its BibTeX gives the venue as the 2025 IEEE International Symposium on Multi-Robot and Multi-Agent Systems (MRS). |

Not read: the published IEEE version (only the two arXiv versions were), and the upstream
project the repository was forked from.

### Version 1 against version 2

Version 2 adds an extension to more than two agents (Sec IV-E, Table IV) and a table of
"nuanced tasks" (Table II), so the results table moves from Table II to Table III. It
drops the unicycle equation, so its "eq. 2" is the MPC problem and the velocity constraint
is (2d) where version 1 has (3d). It also says "Table II shows the possible task strings"
(`v2:233`) although the strings are in its Table I; version 1 has the reference right
(`v1:241`). Nothing that this platform implements differs between the two versions.

## 2. The repository

### 2.1 The code is on `main`, not on `model-arcs`

Issue #24 names branch `model-arcs` as the reference implementation. It is not: **the
GameChat dialogue code is on the default branch, `main`.**

| | `main` (`c49c35a`, 2025-03-06) | `model-arcs` (`2f9c652`, 2024-11-30) |
|---|---|---|
| LLM code | `LLM_utils.py` (prompt, `LLMAgent`, role query); dialogue loop at `main.py:78-105` | none: a search of every `.py`, `.txt`, `.md` and `.yaml` file for `openai`, `gpt-4`, `LLMAgent`, `llm` matches nothing |
| LLM code in history | added in the 6 commits that are only on `main` (2024-11-21 to 2025-03-06, all by the paper's first author) | `git log -S openai` and `git log -S LLMAgent` over the branch find no commit |
| `requirements.txt` | 9 lines; line 9 is `openai` | 8 lines; no `openai` |
| What `main.py` drives | MPC controllers plus the dialogue (`main.py:45-53`, `:80-103`) | learned controllers loaded from weight files (`model-arcs:main.py:15-18`, `:51-69`) |
| Size | 9 Python files | 30 Python files (`train.py`, `models.py`, `model_controller.py`, ...) and about 1,400 data, video, weight and figure files (629 `.json`, 343 `.mp4`, 230 `.pdf`, 139 `.pth`, 42 `.csv`, 26 `.png`) |
| README | headings only, no text | the upstream `mpc-cbf` README |

The two branches split at `9549830` (2024-10-25); 6 commits are only on `main` and 69 only
on `model-arcs`. Relative to that split, `main` adds `LLM_utils.py` and removes
`models.py`, `model_controller.py` and `train.py`. `model-arcs` is the development branch
of LiveNet, the learned controller the paper cites as related work (`v1:82`): 68 of its
69 own commits are by Srikar Gouru, LiveNet's first author, and the comments in its
`main.py` label the weight files it loads "livenet" (`model-arcs:main.py:51-52`). Branch
`vagul` is the same commit as `main`.

**This implementation follows `main`.**

### 2.2 Licence

`LICENSE` is the MIT licence, "Copyright (c) 2022 Elena Oikonomou", identical on both
branches. The name and the `mpc-cbf` title of the `model-arcs` README indicate that the
notice was inherited from the project the repository was forked from, not written by
the GameChat authors.

`llm_negotiation/` is a clean reimplementation: no source code was copied or adapted. Two
pieces of *text* are reproduced so that condition C1 can replicate the paper: the initial
prompt and the task strings. Both are quoted from the paper; the wording of the turn
messages ("Other agent says: ...") is the repository's. They are listed, with the MIT
notice, in `THIRD_PARTY_NOTICES.md`.

### 2.3 The repository is a snapshot of the paper's first version

It handles two agents only (`config.py:36`); there is no code for the version 2 extension
to more agents or for the nuanced tasks. The last commit is titled "post submission
cleanup starts". Conversation durations noted in comments at `main.py:287-290` (2.86,
2.48, 2.52, 2.61 s) are the ones in the captions of the paper's Figures 7 and 8
(`v1:487`, `v1:489`).

## 3. The eleven facts listed in issue #24

Each was checked against version 1 of the paper and against `main`.

| # | Fact | Paper | Repository | Holds? |
|---|---|---|---|---|
| 1 | Unicycle dynamics, state (x, y, heading), controls (v, omega) | Sec IV-A, eq. 2 (`v1:164-174`) | `environment.py:48-62`, Euler step at `:33` | yes |
| 2 | Conflict = heading rays intersect and occupancy intervals overlap | Sec IV-B (`v1:224`) | rays: `util.py:17-51`. Interval overlap: **not there**, see D2 | paper yes, repository differs |
| 3 | Dialogue starts on first mutual observation, turn by turn, stops at consensus or after four messages each | Sec IV-B (`v1:222`), Sec IV-C (`v1:269`) | `main.py:84-96` | yes; timing differs, see D9 |
| 4 | Leader at maximum speed; follower slows just enough to arrive as the leader clears | Sec IV-B (`v1:224`) | `mpc_cbf.py:236-245` | yes |
| 5 | Fallback Strategy 1: shorter time to the conflict point leads; follower speed `d_i v_max / (l + d_j)` | Sec IV-D (`v1:284-300`) | `mpc_cbf.py:236-243` | paper yes, repository differs, see D1 |
| 6 | "Velocity-bound formula in Sec IV-B appears garbled" | — | — | **no, see below** |
| 7 | hospital > airport > grocery; several phrasings each (Table I) | Sec IV-C (`v1:241-267`) | `config.py:15-18`, `LLM_utils.py:9-32` | yes; strings differ, see D7 |
| 8 | v_max 0.3 m/s, omega_max 1.0 rad/s, radius 0.1 m, step 0.2 s, runtime 15 s; doorway 0.4 m; starts and goals; 18 variants; 0.25 m asymmetry | Sec V-A (`v1:475`) | `config.py:37-54`, `scenarios.py:8-23`, `:64-85`, `main.py:262-263` | paper yes; repository differs on runtime and widths, see D10, D13 |
| 9 | Metrics: collisions, deadlocks, % higher-priority first, its time to goal, makespan, follower's minimum speed, path deviation | Sec V (`v1:471`), Table II (`v1:329`) | `main.py:107-212` | yes; two are measured differently, see D11, D12 |
| 10 | MPC with CBF constraints; do_mpc, CasADi, Ipopt | Sec IV-A (`v1:176-212`), Sec V-A (`v1:475`) | `mpc_cbf.py:1-2`, `:46-95` | yes |
| 11 | gpt-4o-mini through the `openai` package | Sec IV-C (`v1:237`), Sec V-A (`v1:475`) | `LLM_utils.py:3`, `:56-59` | yes |

**Fact 6: the formula is not garbled in the paper.** In the LaTeX carried by the version 1
HTML the expression is `\frac{d_{i}v_{\text{max}}}{l+d_{j}}` in Sec IV-B (`v1:224`), in
the proof of Theorem IV.1 (`v1:232`) and in Sec IV-D (`v1:300`): the same thing three
times. It only looks broken in the PDF text extract, where the fraction is split over
three lines (`v2:192-194`). This implementation uses the Sec IV-D definition as the issue
asks; there was no inconsistency to resolve.

One real slip in version 1, of no consequence here: constraint (3c) of the MPC problem is
printed as "the occupied spaces intersect" (`v1:194`) where it must mean "do not".

## 4. Where the repository and the paper disagree, and what this project does

"Follows" says which of the two this implementation takes, or that it takes neither.

| ID | Subject | Paper (v1) | Repository (`main`) | This implementation | Why |
|---|---|---|---|---|---|
| D1 | Follower speed | `d_i v_max / (l + d_j)`; no value is given for `l` (`v1:300`) | `(d_i - 0.25) v_max / (d_j + 0.25)`, with distances from the agents' centres to the ray intersection and a hard-coded 0.25 m (`mpc_cbf.py:233-243`) | The generalised bound of `derivations.md`, `d_i v_j / (d_j + L + l_j)`. With the zone half-length fixed at 0.25 m it is exactly the repository's expression. | **Follows the paper's form, and for the replication the repository's number.** The paper's formula taken literally for discs lets them overlap (`derivations.md` section 5). |
| D2 | When a conflict exists | Rays intersect and the occupancy intervals overlap (`v1:224`) | Rays intersect and a "liveliness" angle between relative position and relative velocity is below 0.7 rad (`mpc_cbf.py:212-219`, `util.py:6-14`, `config.py:22`); the speed rule is applied only for two steps after each detection (`mpc_cbf.py:224`) | Rays (or desired paths) define a conflict zone; a conflict exists while the occupancy intervals overlap (`negsim/conflict/timing.py`) | **Paper.** The liveliness test is not described in the GameChat paper. |
| D3 | Who leads without an agreement | Shorter *time* to the conflict point (`v1:296`) | The agent *further away* follows (`mpc_cbf.py:236`); the same thing when speeds are equal | Shorter time, each agent at its own maximum speed | **Paper**, because agents here may have different speeds. |
| D4 | Exact ties | Assumed away: "due to numerical error ... asymmetry is maintained" (`v1:326`) | Strict `>` at `mpc_cbf.py:236`: on an exact tie neither agent is the follower | Explicit tie-break: lower agent index, or a seeded random draw | **Neither.** This simulator is deterministic, so symmetric starts do tie. The index tie-break is balanced by swapping which participant is agent 0. |
| D5 | Initial prompt | `v1:239` | `LLM_utils.py:45` adds "more, less, **or the same** priority" and "If you are doing the same task or have the same priority then say so." | The paper's text, minus the consensus sentence (D6) | **Paper**, as the issue asks. Same-priority pairs are not part of the replication. |
| D6 | How consensus is signalled | "output the number 1 and nothing else" (`v1:239`) | Consensus when the character `1` occurs in both agents' latest outputs (`main.py:89`, `:94`); then each agent is asked separately to output 2 or 3 for leader or follower (`LLM_utils.py:67-77`) | Every turn returns JSON with `message` and `stance`; consensus is complementary stances on consecutive turns | **Neither**; required by issue #24. See section 5. |
| D7 | Task strings | Five per type (Table I, `v1:243-267`) | Hospital has six, differently worded, e.g. "the operating room at the hospital" (`LLM_utils.py:9-16`); airport and grocery match the paper | The paper's (`configs/tasks/gamechat_tasks.yaml`) | **Paper.** |
| D8 | Who speaks first | Not stated | Always agent 0 (`main.py:85-87`) | Configurable and counterbalanced | **Neither**; an experimental control the issue requires. |
| D9 | Talking while moving | "The robots keep moving around the environment while communicating" (`v1:269`); two cases, consensus before the conflict and during it (`v1:469`) | The whole dialogue runs before the simulation loop and its wall-clock duration is measured (`main.py:84-96`). "Pre-SMG" applies the roles from the first step (`main.py:101-103`); "SMG" applies them once simulated time passes the measured duration (`main.py:124-126`) | `pre_conflict`: time stands still during the dialogue (the paper's first case). `concurrent`: one message per configured interval of simulated time, each agent seeing the state at that moment | **Paper's two cases.** A fixed interval is used rather than measured latency so that runs are reproducible; latency is still logged. |
| D10 | Maximum runtime | 15 s (`v1:475`) | 20.0 s (`config.py:37`) | 15 s for the doorway and the intersection | **Paper.** (The paper's own hard-coded baseline has a makespan of 18.4 s, `v1:479`, which a 15 s limit would not allow.) |
| D11 | Collision | Occupied spaces intersect (`v1:106`) | Centres closer than 0.15 m, for two agents of radius 0.1 m (`main.py:205`): up to 5 cm of overlap goes uncounted | Centres closer than `r_i + r_j`; agent-wall contact is checked as well | **Paper.** |
| D12 | Deadlock | "no robot can move toward its goal for a few seconds" (`v1:36`) | Both commanded speeds below 0.01 m/s on a single step (`main.py:210`) | Every unfinished agent below 0.01 m/s for 3 s | **Paper**; "a few" read as 3, a design choice. |
| D13 | Width of the passage | Doorway 0.4 m; intersection 0.4 m by 0.4 m (`v1:475`) | 0.5 m clear in both: wall discs of radius 0.05 m centred 0.3 m from the axis (`scenarios.py:21-23`), and of radius 0.1 m centred 0.35 m from it (`scenarios.py:71-85`) | 0.4 m | **Paper.** |
| D14 | Controller | MPC with CBF constraints for the other agent and the obstacles (`v1:212`) | MPC with CBFs for the obstacles; when the speed rule is active the other agent is *not* a CBF obstacle (`mpc_cbf.py:113-115`), so separation comes from the speed rule alone | A path tracker, with the speed rule as its upper bound on speed | **Neither.** See `architecture.md`, "Controller backends". |
| D15 | Reversing | `u_min <= u <= u_max`, constraint (3d) (`v1:200-202`) | Symmetric bounds, so negative speed is allowed (`mpc_cbf.py:72-74`) | Speed in `[0, v_max]` | **Neither**; pedestrians do not reverse. |
| D16 | Roles from the dialogue | One leader, one follower (`v1:222`) | Each agent is asked on its own and the two answers are not compared (`main.py:100`); the question is asked even if no consensus was reached; in the "Pre-SMG" case it is asked a second time (`main.py:102-103`), so the roles used need not be the ones recorded | Both roles come from one agreed pair of stances, so they cannot disagree | **Neither.** |
| D17 | Random choices | Task strings drawn at random (`v1:475`) | Unseeded `np.random.choice` (`LLM_utils.py:36-41`) | Seeded per run; the seed is logged | **Neither**; needed for reproducibility. |
| D18 | Doorway goals and initial headings | "goals on the opposite side" (`v1:475`) | Goals 1 m past the door, 0.2 m off-centre on the far side; headings turned 10 degrees inward (`scenarios.py:11-15`) | The repository's | **Repository**; the paper does not say. |
| D19 | Asymmetric starts | One agent moved 0.25 m "away from the goal" (`v1:475`) | Moved 0.25 m straight back from the wall (`scenarios.py:12-13`, `main.py:262`) | The repository's | **Repository**; it makes the paper's phrase precise. |

Two smaller things in the repository worth knowing: one wall disc of the intersection is
listed on the wrong wall (`scenarios.py:79`), and an agent's speed is overwritten *after*
the MPC solve (`mpc_cbf.py:242-245`), not imposed as the constraint the paper describes
(`v1:224`).

## 5. The turn format: why not "output the number 1"

GameChat's agents reply in free text and are told to "output the number 1 and nothing
else" once they think they agree; the code then looks for the character `1` in both
latest outputs and asks each agent, separately, whether it is the more important one.

This platform asks for a JSON object on every turn, `{"message": ..., "stance": ...}`,
with `stance` one of `I_GO_FIRST`, `YOU_GO_FIRST`, `UNDECIDED`. Only `message` reaches the
other agent. Consensus is complementary stances on consecutive turns. Issue #24 requires
this; the reasons it is the better design for this project are:

1. **A substring test is fragile.** `"1" in output` is true for "1 minute", "priority 1"
   or "gate 11". The repository's prompt works around it by telling the model to output
   nothing else, and the paper reports having to tune prompts until such problems "became
   less and less frequent" (`v1:497`).
2. **The two agents' roles cannot contradict each other.** They come from one pair of
   stances, not from two independent questions with nothing checking the answers (D16).
3. **It leaves a trace.** A stance on every turn shows how each agent's position moved
   during the conversation, which is the material rule extraction will work from. A
   single "1" at the end shows only that the conversation stopped.
4. **It costs fewer calls.** No separate role question per agent.

What it changes for the replication: the model is asked to state a position on every
turn, which GameChat's agents never were. A model might commit earlier, or differently,
because it was asked. That is a difference in the instrument, and condition C1's results
should be read with it in mind.

## 6. What this platform does not reproduce

- **The MPC-CBF controller** (D14) and therefore the baselines built on it (MPC-CBF,
  SMG-CBF). Only "GameChat (no LLM)", "Ground Truth" and the two communicating variants
  have counterparts here: conditions C0 and C1.
- **gpt-4o-mini.** The model is DeepSeek's `deepseek-flash` (`llm-backend.md`). A
  different model may rank tasks differently; the paper notes that "different models
  reasoned" about the task and chose a small one for speed (`v1:475`).
- **The kinematics, exactly.** With the zone half-length at 0.25 m the speed rule is the
  repository's, but the agents here follow their straight paths exactly, where
  GameChat's are steered by an optimiser. `README.md` sets this platform's C0 numbers
  beside the paper's Table II.
- **More than two agents** (version 2, Sec IV-E), which issue #24 puts out of scope.
