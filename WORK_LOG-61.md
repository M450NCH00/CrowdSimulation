# Work Log — Issue #61: RF-6: pairwise perception factors (perceived attractiveness, familiarity), shown only to the observer

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/61
**Branch:** feat/61-pairwise-perception-factors (cut from `feat/60-core-factors-visibility-situational`, which PR #87 merged into `feat/58-step1-encounter-protocol`; track #55's branches stack, see the memory note on `git checkout main`)
**Started:** 2026-10-23

## Understanding the issue

The supervisor suggested attractiveness as a factor, "represented in a matrix". Attractiveness is
not a property of one person: it is how one person sees another, and it need not be mutual. So
this issue adds **pairwise** factors, one value per (who looks, who is seen), on the mock only:

- **Perceived attractiveness**, a matrix: row = who is looking, column = who is seen, levels
  `unremarkable` and `attractive`, diagonal empty.
- **Familiarity**, symmetric: `strangers` or `acquaintances`.
- **Where the lines go** (D2): under the seen person's label in WHO YOU CAN SEE, in the
  observer's own view only, and only while that person is in view. Nobody is told what someone
  else perceives, and nothing is said of a person who is only heard.
- **Switches** `attractiveness_visible`, `familiarity_visible`: off means no line at all, for
  either level (on, *both* levels have a line: "You do not find them especially attractive." is
  said too, unlike RF-5's base levels, which say nothing).
- **Design factors** `attractiveness_0_sees_1`, `attractiveness_1_sees_0`, `familiarity`.
- **Outcome rows**: each person's own perception as 0 or 1, for RF-8.
- **Ethics gate**: attractiveness off by default; a paid run with it on is refused unless
  `CLAUDE.md` records the supervisor's sign-off, reusing the fictional-group gate.
- **Validation**: a rule that reads perceived attractiveness is `protected_attribute` (kept,
  counted, never written). It stays in RF-8's analysis and the factor-to-decision mapping.
- **Docs only**: a full matrix for 10,000 agents is 10^8 entries; a crowd version would keep
  only neighbours within sensing range.

**What I found before planning.**

1. **Most of the plumbing exists.** RF-2 gave `SeenPerson` a `pairwise_lines` slot ("for this
   observer only (RF-6)"), RF-17's `Perceiver.look` and `view_in` take `pairwise_lines` by agent
   id and attach them only to people in view, and `resolve_v2` prints them after the factor
   lines, verbatim. So no core template changes: the lines go into a **new frozen template of
   their own**, as RF-5's did (`resolve_pairwise_v1`, kind `resolution_pairwise`).
2. **"The session config".** A resolution experiment has no per-session config: sessions come
   from the design. I read task 1's block as the *session's* pairwise block: written with each
   session (`design.jsonl`, the session record) in the issue's format, and loadable from it. The
   design's sessions add `agents` (which case agent each row is), because person 1 is agent 1
   under `mapping: p1_higher`. Without `agents`, rows are agents 0, 1, ... by id, so the issue's
   block loads as written ("agent 0 finds agent 1 attractive"). *An interpretation, recorded.*
3. **Rows are the design's persons.** `attractiveness_0_sees_1` is row 0 looking at column 1:
   person 1 looking at person 2. Every other person factor is by slot (person 1 has the other
   level) and only `mapping` ties a slot to the case geometry; indexing by case agent instead
   would tie the perception to which end of the corridor someone starts at. *My choice,
   recorded.*
4. **Only in full detail, as RF-5.** `resolve_v2` prints a person's extra lines only within the
   detail range (5 m, D2); from 5 to 10 m it prints one short line. Changing that needs a new core
   template. **Consequence, found in RF-5's rehearsal records:** in the head-on case
   (`head_on_02dfbadb`, round 1), every decision point fired 5.0 to 9.8 m away (the first at
   9.8 m, at the edge of the seeing range), so *no* RF-5 observable line and no RF-6 line would
   ever reach an agent there. The independent condition has only that one decision point. In the
   passage (0.6 m) and overtaking (4.0 m) cases they do. Flagged below for the user.
5. **The gate.** `negsim.rulegen.experiment` checks one exact sentence in `CLAUDE.md`. The
   resolution experiment has no gate yet (the group is never on there). I move the check to a
   small shared module and add a second sentence for attractiveness.
6. **Protected words.** The rule loader's protected check reads a stem (`ethnic`) and whole
   words. I add stems for attractiveness (`attract` and a few synonyms). The refusal message has
   to name what was read (today it always says "a person's group").

## Plan

1. **Template** `resolve_pairwise_v1.yaml` (kind `resolution_pairwise`), frozen: one line per
   factor and level, the issue's wording.
2. **`negsim/resolution/pairwise.py`:** the factors and levels, the template loader,
   `PairwiseFactors` (load the block, check it, the lines one observer is told of each other
   person, the 0/1 values, `as_dict`).
3. **Protocol and view:** `EncounterSession(pairwise=...)` passes the observer's own lines into
   its views; nothing else changes.
4. **Design:** the three factors and two switches (switch only with its factor); the session's
   `pairwise` block; the switches in `visibility`. A config with none of them: same cells, ids
   and records as before. `uses_factors` keeps meaning RF-5's factors.
5. **Experiment:** `templates.pairwise`; the record's `pairwise`; numeric outcome columns; the
   cost preview counts the longest pairwise lines; the ethics gate (`refused_no_sign_off`) in
   `run_resolution` and a note in `--plan`.
6. **Validation (task 7):** perceived attractiveness protected in the rule loader and the
   rule-generation check, with its own message.
7. **Tests** (task 9) and a mock rehearsal config.
8. **Docs:** a new `docs/pairwise-factors.md` (the block, rendering, switches, design, columns,
   the gate's exact sentence, rules, 10,000 agents), and `resolution.md`, `log-schema.md`,
   `encounter-protocol.md`, `rule-format.md`, the READMEs, and a pointer in `CLAUDE.md`'s
   pending sign-offs to the sentence's exact form (not the sign-off itself).

## Progress log

### 2026-10-23 — Start
- What I did: read #61, `resolution.md` (D2), the persona schema, `fictional-groups.md` (the
  gate), `rulegen/validate.py`, the rule loader's protected check and its tests, RF-5's factors
  module, template, design, experiment and work log, and the view, perceive, prompt and protocol
  modules. Checked the trigger distances in RF-5's rehearsal records (`runs_mock/`, not tracked).
- Result / what I found: the six points under "What I found before planning".
- Next step: the template and the pairwise module.

## Open questions / risks

1. **Lines only within 5 m (point 4 above).** In round 1's head-on case no RF-5 observable line
   and no RF-6 line reaches an agent, because every decision point there is beyond the detail
   range. A `resolve_v3` that prints these lines on the short line too (5 to 10 m) would fix it
   for both issues; it is a new core template, so it is for the user to decide, and D2 would
   need a note.

## Summary (fill in at the end)
