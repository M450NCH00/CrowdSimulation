# Work Log — Issue #60: RF-5: the core factors (seven, including a memory note) with visibility switches, and up to four situational factors

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/60
**Branch:** feat/60-core-factors-visibility-situational (cut from `feat/58-step1-encounter-protocol`, which PR #86 merged into `feat/59-execute-plans-physical-outcomes`; track #55's branches stack, see the memory note on `git checkout main`)
**Started:** 2026-10-23

## Understanding the issue

Step 4 needs more factors than age, gender and errand, so that the factor analysis (RF-8) can
find which ones drive a decision. This issue adds the **core** factors that every round keeps
(D15) and up to four **situational** ones, on the mock only:

- **Seven person attributes**, two levels each: `urgency` (routine, urgent), `mobility_aid`
  (none, cane), `load` (none, large_suitcase), `distraction` (none, phone), `assertiveness`
  (gives_way, holds_ground), `residence` (local, visitor), `memory_note` (none,
  bad_experience). Three are observable (mobility aid, load, distraction), four are not.
- **Where the lines go** (D2): a person's own lines in ABOUT YOU, the memory note in YOUR
  NOTES, what someone else can see of them in WHO YOU CAN SEE (only when that person is in view
  *and* the factor's visibility switch is on), the situational lines in WHERE YOU ARE, the same
  for everyone.
- **`load` widens the body**, fixed from the start of the run (D1: bodies never change size
  during a run).
- **Visibility switches** for the observable ones, as design factors, like
  `demographics_visible`.
- **Design coding:** each factor is "neither agent" or "one agent"; the existing `mapping`
  factor balances which agent.
- **Validation:** a rule reading `assertiveness`, `residence` or `memory_note` is
  `needs_communication`.
- **Tests**, including that everything written before this issue renders exactly as before.

**What I found before planning.**

1. The issue says the lines go into "a new template version, `resolve_v2`". That name is
   taken: RF-17 (#73) froze `resolve_v2` after this issue was written. `resolve_v2`'s own
   provenance already says "Factor lines (RF-5, RF-6) are rendered by their own templates and
   placed here verbatim", and the `View` already has the slots (`Me.factor_lines`, `notes`,
   `SeenPerson.factor_lines`). So the lines go into a **new frozen template of their own**,
   `resolve_factors_v1` (kind `resolution_factors`), and `resolve_v2` renders them unchanged.
   No core template is edited or re-versioned. *A deviation from the issue's wording, recorded
   here; the issue's intent (new wording only in a new frozen template) is kept.*
2. **Task 6 is not true today.** A rule naming `either.assertiveness` is refused as
   `unknown_field`, which `negsim.rulegen.validate` counts as `schema_error`, not
   `needs_communication`. It needs the three attributes in the rule loader's table of
   unobservable fields (`negsim/rules/fields.py`, `UNOBSERVABLE`).
3. **Adding attributes to the persona table changes old records** unless kept out of
   `default_visibility()`: that dict is built from the table and recorded by every avoidance,
   negotiation, rule-generation and resolution run, and two tests pin it exactly. The new
   attributes have their own switches in the resolution design, and the older layers' prompts
   have no line for them, so they are left out of it.
4. `load`'s body can be widened the way `docs/parameters.md`, section 5, already documents for
   linking a persona to a physical change: a per-agent `agents.overrides.<id>.radius` in the
   run's scenario config. The replays must apply the same override, so the session record has
   to carry it.

## Plan

1. **Schema:** declare the seven in `ATTRIBUTES` with their levels (`AttributeSpec.levels`);
   keep them out of `default_visibility()` (both copies); a level value is spelled out in a
   derived persona id, not marked as free text.
2. **Factor template** `resolve_factors_v1.yaml`, a new kind `resolution_factors`, frozen in
   the manifest: the self, other and note lines per level, and the situational lines.
3. **`negsim/resolution/factors.py`:** the situational factors' table, the template loader,
   `SessionFactors` (one session's levels, switches and lines: own, notes, what others see,
   the place), the values config `configs/resolution/factors_v1.yaml` (`load`'s added width,
   `surroundings`' hearing ranges, all `[placeholder]`), and `with_bodies` (the scenario
   override for a wider body).
4. **Views:** `view_in` takes a person's own lines and the situational lines; the protocol
   passes a session's factor lines into every view.
5. **Design:** optional factors, each "neither" or "p1"; `urgency` as the two-level form of
   `task` (one or the other); the visibility switches; the situational factors. A config that
   names none of them gives the same cells, ids, session records and outcome columns as before.
6. **Experiment:** a wider body in the live run, in plain ORCA and in both replays; the
   hearing range of the session's `surroundings`; factor levels in the outcome row; the cost
   preview counts the factor lines.
7. **Validation (task 6):** the three unobservable attributes in `UNOBSERVABLE`.
8. **Tests** (task 8) and a mock rehearsal config with the factors on.
9. **Docs:** `resolution.md`, `parameters.md` (new placeholders), `encounter-protocol.md`,
   `log-schema.md`, the READMEs.

## Progress log

### 2026-10-23 — Start
- What I did: merged PR #86 (RF-3) into `feat/59-...`, closed #58 by hand and ticked it in #55
  (the user's request). Read #60, `resolution.md` (D1, D2, D7, D15, D16), the persona schema and
  loader, `resolve_v2`, the view, perceive, protocol, design, experiment and replay modules,
  `parameters.md` section 8, and the tests that pin the visibility defaults.
- Why: to place each piece of the issue in the code RF-2 to RF-3 left.
- Result / what I found: the four points under "What I found before planning".
- Next step: the schema and the factor template.

## Open questions / risks

## Summary (fill in at the end)
