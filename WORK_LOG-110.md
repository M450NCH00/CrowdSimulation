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

## Open questions / risks

- The companion line and "everyone told nothing of the other group" are assumptions.
- 2 v 2 in a 1.75 m corridor cannot be passed four abreast; a low resolved share there may be the
  corridor, not the agents. Reported by layout.
- The design is smaller than RF-30's (4 factors, not 16): only the number of people and these
  factors differ from RF-30's sessions, with RF-30's others at their base levels.

## Summary (fill in at the end)
