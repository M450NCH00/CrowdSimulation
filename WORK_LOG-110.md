# Work Log — Issue #110: RF-32: round 1 with three or four people: do the agents resolve a head-on as pairs did, and do round 1's rules still describe them?

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/110
**Branch:** feat/110-rf32-group-head-on (from `feat/112-rf33-realistic-scenarios`; PR #113 merged
into `feat/74-...` on 2026-10-27, and `main` is not used in this track)
**Started:** 2026-10-28, 04:44 UTC

## Understanding the issue

Every Step 1 session so far had exactly two people, and round 1's rules (RF-11, translated by
RF-12 and RF-31, run in crowds by RF-18 and RF-33) were extracted from those pairs. Crowd runs only
show that a rule does not break a crowd; they do not show whether the LLM agents themselves behave
that way when more than two people meet. This issue asks the agents directly, in round 1's corridor:

1. **Do they still resolve it** when three or four people meet head-on (2 v 1, 2 v 2), at about the
   pair rate (RF-30: 0.53 pooled, 0.55 independent, in `plan_only`)?
2. **Is the pattern the same?** Who gives way, the passing side, when they start and how far they
   turn, per conflict pair; and whether a side-by-side pair stays together or splits.
3. **Do round 1's rules still describe them?** RF-31's identity check per conflict pair, against
   plain ORCA on the same seeds.

**Already decided (track #55, the user, 2026-10-27):** RF-32 amends D11 for this issue only (two-
person cases in rounds 1 to 3), uses the layouts 2 v 1 and 2 v 2, and the independent condition only.
It comes after RF-18 and RF-33 and before RF-14.

**Which rules.** RF-33 (realistic crowd, 30 seeds, the verdict of record): the left-turn rule
(`ext_head_on_0ecc2d1a6e`) helps; the cane rule (`ext_head_on_6455ca5589`, RF-31's retry) harms
(gridlock on 1 seed of 30); both together help. The issue says to check the rules that help plus
any harmful one whose cause is unclear, so both are checked here, and RF-12's format 3 rules for
comparison.

**Paid.** The build is mock only. The paid run needs its own approval and cap in `CLAUDE.md`
(pending item 1): about USD 0.10 to 0.20 by the issue; balance USD 0.62 (2026-10-26).

## Plan

Session 1 (this one): the build, on the mock, and the cost preview; then ask for the paid run.

1. Record the decisions in `docs/resolution.md` (a note under D11) and here.
2. **A scenario type for groups**, `group_head_on` (`negsim/scenarios/group_head_on.py`): round 1's
   corridor with any number of people per direction, each at a lateral offset. A new file; the
   two-person `wide_corridor_head_on` is not touched.
3. **Frozen cases** the way round 1's were made: a source experiment on the primary baseline
   (`configs/cases/rf32_source_group_head_on.yaml`, plain ORCA, two repeats), then extraction by
   stratum (`configs/cases/rf32_group_cases_v1.yaml`), giving case set `rf32_group_v1`.
4. **The plug-in** `passing_group` (`negsim/resolution/scenarios/passing_group.py`, template
   `scenario_passing_group_v1`): every person of the case is in the encounter (cap 4), nearest
   first; the conflict pairs are every pair walking opposite ways; a person walking with a friend
   is told so.
5. **Factors for every person**: a design key that gives the case's other people (the companions)
   a persona and the base level of each factor the design varies, so their own lines and what
   others see of them (the cane) render like the design's two.
6. **Config** `configs/resolution/round1_group_head_on.yaml`: RF-30's template, execution, model and
   reply cap; the design below; independent only.
7. **Mock rehearsal** of the whole run, then `--plan` for the worst case.
8. Ask the user to approve the paid run and its cap.

Session 2: the paid run (pilot with `--limit`, read, then the rest), the analysis
(`group_report.md`) and the identity check per conflict pair.

## Design choices (mine unless marked; for the user to see before the paid run)

- **Corridor: round 1's** (1.75 m wide, 20 m long, each group starting 8 m from the middle), as the
  issue says. *Consequence:* four bodies abreast (2.0 m) do not fit, so in 2 v 2 someone must fall
  in behind; three abreast (1.5 m) leave 0.25 m in all. That is part of what is tested.
- **Side by side: 0.63 m between centres**, across the direction of walking. *Sourced:* Zanlungo,
  Yücel, Brščić, Kanda & Hagita 2017, "Intrinsic group behaviour: dependence of pedestrian dyad
  dynamics on principal social and personal features", *PLOS ONE* 12(11): e0187253, Table 1: the
  abreast distance x of 716 leisure dyads, 628 ± 6.1 mm (σ 162); work dyads 713 mm. Measured in a
  shopping mall in Japan, not Singapore, and not in a 1.75 m corridor. Cached as
  `refs/rf32_zanlungo2017_arxiv.{pdf,txt}` (arXiv 1703.02672v1).
- **Geometries: round 1's two**, each group as a whole: aligned (the lone person on the centre
  line, a pair centred on it), and 20 cm apart (each group shifted 10 cm to its own left, as
  round 1's `apart_20cm` shifts each person).
- **Companions are told** they walk with a friend and on which side ("WHO YOU ARE WITH").
  Without it an agent would not know: a person abreast is at 90°, outside the 75° view cone. An
  assumption, not sourced. The people coming the other way see two people side by side and are not
  told they are together.
- **Who is in the encounter:** everyone in the case, nearest first, cap 4 (the issue).
- **Conflict pairs: every pair walking opposite ways**, not only those predicted to conflict at the
  start (in 2 v 2 aligned the two diagonal pairs start 0.63 m apart, outside the conflict reach,
  and could still be walked into). A companion pair is not a conflict pair, but a collision between
  companions fails every conflict pair of theirs (`physical_outcome` counts a collision with anyone).
- **Persons of the design:** person 1 is the westbound member of the case's pair (in 2 v 1 the lone
  person), person 2 the eastbound one; companions are 25, of their companion's gender, with the base
  level of each factor the design varies (no cane, gives way) and a routine errand.
- **Design:** full factorial of 16 cells on `age_pair` (same, p1 older), `gender_pair`,
  `mobility_aid` (person 1 has a cane) and `assertiveness` (person 1 holds their ground): the two
  factors round 1's rules read, and age, which the cane rule's extraction mentioned (elderly). Four
  cases (2 layouts × 2 geometries), an exact-repeat set of 4 cells × 3. About 72 sessions.

## Progress log

### 2026-10-28 04:44 UTC — branch and reading
- What I did: branched from `feat/112-rf33-realistic-scenarios`; read #55, #110, `resolution.md`,
  `encounter-protocol.md`, the protocol, scenarios, design, factors, outcomes, replay, experiment and
  identity-check code, and RF-30's, RF-11's and RF-31's reports.
- Result / what I found:
  - the protocol, outcomes and replays already take encounters of more than two (RF-3, for
    `passing_crowd`); outcome rows put further members in `others` (JSON only);
  - `wide_corridor_head_on` is strictly two people, and the case format names "the two agents" of
    a pair, so group cases are a pair out of a 3- or 4-person run, as the flow cases are out of 100;
  - conflict pairs are fixed at the start from `conflict_predicted`, which would miss 2 v 2's
    diagonal pairs; the design gives personas to the design's two only; a plug-in's description
    side sees no geometry, so it cannot say where a companion is;
  - the identity check is pair-centred (person 1 and 2 only).
- Next step: the scenario type and the cases.

### 2026-10-28 04:56 UTC — scenario type, source runs and cases
- What I did: `negsim/scenarios/group_head_on.py` (a new type; `wide_corridor_head_on` untouched),
  `configs/scenarios/group_head_on.yaml` (round 1's file but for the people), the source experiment
  `configs/cases/rf32_source_group_head_on.yaml` (4 layouts × 2 repeats, plain ORCA, free), and the
  case set `configs/cases/rf32_group_cases_v1.yaml`.
- Result: the first source run was from a dirty tree, so I committed the scenario and ran it again
  with `--overwrite` (clean, `c288360`). Plain ORCA: everyone arrives in all 8 runs, every head-on
  pair passes within the near-miss distance (T3), as in round 1. **In 2 v 2 the diagonal pairs meet
  too** (agents 1 and 2 reach 0.0 m). So counting only pairs predicted in conflict at the start would
  miss real conflicts, and the case's pair can be a diagonal one.
- Decision (mine): `min_tier: T3` (round 1's set used T1, but every round 1 pair was T3), one case
  per layout. All four drew the pair (1, 2): in 2 v 1 the lone person and the eastbound person on
  their right-hand side; in 2 v 2 a diagonal pair. Because of that, the plug-in lets any oncoming
  pair start the encounter (hook `trigger_pairs`).

### 2026-10-28 05:06 UTC — plug-in, hooks, everyone's persona, config; mock rehearsal
- What I did: two scenario hooks with the protocol's old rule as their default (`trigger_pairs`,
  `conflict_pairs`); `scene_of` passes the layout, so a plug-in can say where a friend walks;
  `passing_group` with frozen template `scenario_passing_group_v1` (WHO YOU ARE WITH);
  `design.others`; `configs/resolution/round1_group_head_on.yaml`.
- Result: `--plan` 72 sessions, worst case USD 3.73 (the loose bound; `stop_at_cap`). The mock
  rehearsal ran all 72: everyone prompted (6 calls for 3 people, 8 for 4); the trigger came from a
  facing pair even where the case's pair is diagonal; all opposite pairs counted; the friend's side
  right in each layout; an oncoming 70-year-old with a cane described with her cane. Plain ORCA
  resolves none (near misses), as in round 1.
- Tests: `tests/test_rf32_group.py`. Docs: `resolution.md` (D11 note), `encounter-protocol.md`
  (sections 2 and 8), `cases.md` (section 10).

### 2026-10-28 05:12 UTC — the user's answers: paid runs approved, design as built
- The user approved paid runs for #110 only, **cap USD 0.15** (I had proposed 0.10; the user chose
  0.15), and answered "Run as built" to the five design choices above. Recorded in `CLAUDE.md`.
- Balance checked: **USD 0.62** (DeepSeek's endpoint), as recorded after #108.
- Estimate from RF-10's measured cost: USD 0.00013 a call, so about USD 0.07 for 72 sessions.

### 2026-10-28 05:13 UTC — pilot (paid): 8 sessions, USD 0.00752, 0 resolved
- What I did: `--client deepseek --confirm --limit 8`, 05:13 to 05:15 UTC, off-peak. Read every plan
  and each replay's collision.
- Result: cost on estimate (USD 0.0008 to 0.0010 a session). **All 8 ended in a collision.** The plans
  are rich: pairs split to let the other pair through between them ("so they can pass between
  us"), people tuck in behind a friend, many give way to the person with the cane. Three of 32
  replies were unreadable after their retry (a later step's `start` written as `"other_passes"`;
  the template is frozen, so this stays and is reported).
- **Problem found: 3 of the 8 collisions were two friends walking into each other**, before they
  reached anyone (for example "tuck in behind my friend" as a 20° turn at full speed, the friend hit
  0.3 s later). `plan_only` switches ORCA off between every pair of encounter members, and with
  groups that includes friends. The driver also never hands a group back to ORCA, because two
  friends walking in parallel never "pass" each other.
- I stopped the paid run and asked the user, since it changes what is measured.

### 2026-10-28, between 05:15 and 05:25 UTC — the user's decision: ORCA keeps friends apart
(The pilot ended at 05:15; the clock read 05:25 after the re-execution below; commit `c332ea5` at 05:26.)
- The user chose "ORCA keeps friends apart": the plans alone decide only between people walking
  opposite ways, which is what D6 measures.
- Built: `protocol.orca_within_groups` (off by default, named in a record only when on, so every
  earlier record replays exactly as before). The driver keeps ORCA between two members of one group
  (the run's `group`), and its hand-back counts only cross-group pairs. Replays read the setting
  from the record; `reexecute --orca-within-groups` sets it.
- **The pilot re-executed under it (free; every decision was at the trigger): still 0 of 8.** The
  three friend collisions became collisions with the oncoming people at about 6 s. So the failure
  is in the plans against the oncoming people, not an artefact.
- New config `round1_group_head_on_orca_groups.yaml` (experiment `rf32_round1_group_head_on_orca_groups`,
  cap USD 0.1425 = 0.15 − the pilot's 0.00752). Its folder was created with `--limit 0`, and the 8
  re-executed pilot records were copied into it, so the run reads them back and pays for 64.
  *Caveat:* those 8 records keep their live encounter end (under the old rule, all collisions);
  their physical columns are the new replays'. All 8 also collide under the new rule, so
  `not_resolved_by_llm` is the same either way.
- The pilot's own folder (`runs/rf32_round1_group_head_on`, 8 sessions, as built) stays as the record.
- Tests added: the setting's default and checks, the driver within and across groups, the pilot's
  tuck-in plan hitting the friend with the setting off and not with it on, and the re-execution.

### 2026-10-28 05:28 UTC — the paid run of the other 64 started (off-peak)
- Calls 05:26:45 to 05:37:22 UTC (ledger), the run ended 05:40:59 with its replays. 449 calls, USD
  0.054349, off-peak, no transport error. 8 sessions read back (the re-executed pilot), 64 run.
- Balance after: **USD 0.56** (0.62 before). #110's spend: USD 0.061869 of the USD 0.15 cap.

### 2026-10-28 05:37 UTC — the group analysis, built and run
- What I did: `negsim/resolution/groups.py` (`python -m negsim.resolution.groups`), tested on the mock
  rehearsal first. Per conflict pair it runs `plan_only`, plain ORCA and each rule arm on the session's
  own run and seed: RF-33's database (left turn, cane rule, both, as RF-18/RF-33 ran them) and RF-12's
  three format 3 translations. Everyone carries the session's persona, as in a crowd run.
- Result (`runs/rf32_round1_group_head_on_orca_groups/group_report.md`):
  - **4 of 64 design sessions resolved in `plan_only` (0.06, CI 0.02 to 0.15) against round 1's
    independent pairs' 35 of 64 (0.55)**, Fisher p < 0.0001. 2 v 1: 4 of 32; 2 v 2: 0 of 32.
  - Every one of the 62 collisions is with an oncoming person, none between friends (checked by group).
  - Friends mostly turn away from each other (86 of 106 one-sided first plans) or fall in behind;
    resolved pairs' sides split evenly (7 right, 7 left, 7 not abreast).
  - Under ORCA the left-turn rule resolves 64 of 64, the cane rule 0, both 32 (the sessions without a
    cane). Per resolved conflict pair (21) no rule reproduces the agents much better than plain ORCA.
  - Holds ground and did not slow: 20 of 32 (round 1: 21 of 33).
- Checked two of my own claims before writing them: that friends turn away from each other
  (counted: 86 of 106), and that lone people expect the pair to make room (mixed; quoted, not counted).

### 2026-10-28 05:45 UTC — the full suite
- `pytest` over `llm_negotiation/` (started just after commit `de5a980` at 05:06 UTC, before the
  analysis module and the setting):
  **2,162 passed, 5 failed, 10 skipped** (32 min). All 5 were enumerations that a new scenario type,
  plug-in, cases and source runs change: committed run versions (+8 source runs), registered scenario
  types (+`group_head_on`), case counts (+4 group cases), registered plug-ins (+`passing_group`), and
  the ethnicity check of configs (RF-32's configs name RF-30's `resolve_factors_v2` with no ethnicity
  varied; allowed for them, and their sessions still have no ethnicity). Each updated with a note.
- After: those five tests and `tests/test_ethnicity.py`, `tests/test_resolution.py` and
  `tests/test_rf32_group.py` (21 tests) all pass (153 passed, 10 skipped).

## Open questions / risks

- The companion line and "everyone told nothing of the other group" are assumptions.
- 2 v 2 in a 1.75 m corridor cannot be passed four abreast; a low resolved share there may be the
  corridor, not the agents. Reported by layout.
- The design is smaller than RF-30's (4 factors, not 16): only the number of people and these
  factors differ from RF-30's sessions, with RF-30's others at their base levels.
- **The run stops at the first collision**, so pair-level numbers are censored (141 of 160
  friend-oncoming meetings never reached). The session-level share is not affected.
- **Independent condition only.** Groups might do better seeing each other move or talking; RF-30
  found no gain from either with pairs. A non-verbal run would cost about as much again.
- **For the user:** whether this finding needs follow-up before RF-14: a non-verbal condition, a
  wider corridor for 2 v 2, or extracting rules from group sessions (out of scope here, the issue says).
- The full suite was not rerun after the analysis module, `orca_within_groups` and the test updates;
  the touched test files were (above). A full run before merging is advisable.

## Summary

**What changed.**
- Simulation: a new scenario type `group_head_on` (round 1's corridor with people side by side, 0.63 m
  apart, Zanlungo et al. 2017), its source runs and the case set `rf32_group_v1` (four cases, extracted
  by round 1's rules with `min_tier: T3`).
- Resolution layer:
  - the plug-in `passing_group` with frozen template `scenario_passing_group_v1` (WHO YOU ARE WITH);
  - two scenario hooks (`trigger_pairs`, `conflict_pairs`) whose defaults are the protocol's old rule;
  - `design.others`, a persona for everyone beyond the design's two;
  - `protocol.orca_within_groups` (the user's decision after the pilot), read by replays and
    `reexecute --orca-within-groups`;
  - the analysis `python -m negsim.resolution.groups`.
- Configs: `round1_group_head_on.yaml` (the pilot, as built) and
  `round1_group_head_on_orca_groups.yaml` (the run of record).
- Docs: `resolution.md` (D6 and D11 notes), `encounter-protocol.md`, `cases.md` section 10; `CLAUDE.md`
  (approval, balance), `README.md` (RF-32's row).

**Why.** Issue #110: do LLM agents resolve a head-on in a small group as pairs did, and do round 1's
rules still describe them?

**Result.** No: 4 of 64 (0.06) against 35 of 64 for pairs. The agents act as groups (split, fall in
behind) but do not coordinate with the oncoming people. Round 1's left-turn rule still removes the
stall under ORCA (64 of 64), but no rule describes what the agents did.

**Verified.** Mock rehearsal of all 72 sessions and of the analysis; `tests/test_rf32_group.py` (21
tests: scenario type, cases, plug-in, hooks' defaults, `design.others`, `orca_within_groups` including
the pilot's tuck-in plan, re-execution, analysis); the full suite (2,162 passed, 5 enumeration failures
fixed and rerun); every report number taken from the files named with it; two interpretive claims
counted or reworded. Paid: USD 0.0619 of USD 0.15, off-peak, balance USD 0.56.
