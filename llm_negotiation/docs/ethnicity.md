# Real ethnicity as a factor (issue #92, RF-26)

The user decided on 2026-10-24, after RF-9 (#64), that **real ethnicity replaces the fictional
group of issue #32 in track #55**. The simulated settings are Singaporean, so the groups are
Singapore's own census groups, at their real shares of the resident population. Both real
ethnicity and perceived attractiveness are included in RF-10's screen, because bias can affect
the decision a person makes.

**That measurement is the point. Applying such a difference to people is not.** The screen asks
whether the model treats people of different ethnicities differently. No rule may ever read a
person's ethnicity (section 7), and RF-11 keeps any rule that does out of the rule database.

The fictional group stays in the rule-generation layer only (#30, #32), unchanged
(`fictional-groups.md`). It is not used in this track.

Code: `negsim/resolution/ethnicity.py` (the shares and the draw), `factors.py` (the lines),
`design.py` (the design factors), `experiment.py` (the gate, the rows, `--plan`),
`negsim/ethics.py` (the sentence), `negsim/rules/fields.py` (the rule check). Tests:
`tests/test_ethnicity.py`. Mock rehearsal: `configs/resolution/resolve_ethnicity_mock_rehearsal.yaml`.

## 1. What each person is told

The lines are in the frozen factor template **`resolve_factors_v2`**, which is
`resolve_factors_v1` word for word plus an `ethnicity` block. `resolve_factors_v1` is unchanged.

| Group | In ABOUT YOU (oneself) | Under the person in WHO YOU CAN SEE (the other) |
| --- | --- | --- |
| Chinese | `- You are Chinese.` | `They look Chinese.` |
| Malay | `- You are Malay.` | `They look Malay.` |
| Indian | `- You are Indian.` | `They look Indian.` |
| Others | `- You are of another ethnicity, neither Chinese, Malay nor Indian.` | `They look neither Chinese, Malay nor Indian.` |

- **One's own group** is always told when the factor is on. It is the first of the person's
  factor lines in ABOUT YOU, before a cane or a suitcase.
- **The other's group** is told only when the design's switch `ethnicity_visible` is on. It is the
  first line under that person, before their observable factors (a cane, a suitcase, a phone).
  So it reaches an agent exactly where the observable factors do: only for someone in view, and
  from 10 m under `resolve_v3` and later (D2; the user's amendment of 2026-10-23), within 5 m
  under `resolve_v2`. In the head-on case every decision point is 5 to 10 m away, so a design
  that varies ethnicity needs `resolve_v3` or later (the default for a design with factors).
  RF-10 is to use `resolve_v5`.
- **The wording of Others** is the user's choice of 2026-10-24 (open question 1): the census's
  residual group named by what it is not, with no sub-group (such as Eurasian) invented.
- **"They look ..."** is an inference a person makes from appearance, not a fact about the other
  person. Whether that is acceptable is open question 2, for the supervisor (section 9).
- No line names a walking convention, a side, an order of passing, or anything said to be typical
  of a group (tested).

## 2. Only in the prompt

Ethnicity changes nothing in the simulator: no body, speed, view or hearing. A factor's effect is
therefore an effect on the decision only. It is not in the perception record that rules read, and
ORCA's neighbour search is unchanged.

## 3. The groups and their shares

`configs/resolution/ethnicity_sg_2026.yaml`, from the Singapore Department of Statistics,
*Population Trends, 2026* (published 2026-09-25), read on 2026-10-24 and cached as text in
`refs/rf26_singstat_population_trends_2026.txt`:

> "The ethnic composition of the resident population remained broadly stable over the decade,
> comprising 73.9% Chinese, 13.5% Malays, 9.0% Indians, and 3.6% Others as at end-June 2026."
> (https://www.singstat.gov.sg/publication-resources/population-trends-2026)

| Group | Share of residents |
| --- | --- |
| Chinese | 73.9% |
| Malay | 13.5% |
| Indian | 9.0% |
| Others | 3.6% |

**Limits, said wherever the shares are used:**
- **Residents only.** The shares are of the resident population: 4.23 million of a total
  population of 6.21 million as at end-June 2026 (the same page). About 1.98 million
  non-residents are not covered by this breakdown.
- **A visitor** (`residence: visitor`, RF-5) is drawn at the same resident shares. This is the
  user's decision of 2026-10-24 (open question 4). No source gives the ethnic mix of visitors.

Updating the shares later is a new file (`ethnicity_sg_<year>.yaml`), never an edit. A design may
name another file in `design.ethnicity_shares`. The file is checked on loading: the four groups,
in order, adding up to 100 (within 0.15, for a published table rounded to 0.1), with the source
and at least one stated limit.

## 4. The design

| Factor | Levels (base first) | What it sets |
| --- | --- | --- |
| `ethnicity_pair` | `same`, `different` | whether the two people are of one group |
| `ethnicity_visible` | `true`, `false` | whether each is told the other's group (a switch of `ethnicity_pair`; `true` when left out) |

Both are two-level, so a fractional screen holds them as columns (RF-7). A config that names
neither has the same cells, session ids and records as before.

**The draw.** Each session's two groups are drawn with the design's seed:
- **Person 1** at the shares;
- **Person 2** of a `same` session: person 1's group;
- **Person 2** of a `different` session: one of the other three groups, at their shares
  renormalised (for example, after a Chinese person 1, Malay with 13.5 / 26.1 = 51.7%).

So the screen estimates same against different while each person keeps the population's real mix.
Both groups are kept on the session's personas (`ethnicity`) and in its record.

**The random stream** is named by the design's seed, the case, and the cell (for a counterfactual
pair, the pair). It is never named by the condition or the repeat. This is my design choice
(`WORK_LOG-92.md`, A1), not a decision of the user's:
- an exact repeat is the same two people, so its prompts stay identical (D14);
- the same cell on the same case is the same two people under all three conditions;
- a counterfactual pair that flips another factor keeps both groups, and one that flips
  `ethnicity_pair` keeps person 1's group and changes only person 2's.

**What the draw does to the mix of persons.** Person 1, and both people of a `same` session, are
at the resident shares. Person 2 of a `different` session is not: excluding person 1's group
(usually Chinese) makes the smaller groups more common. With half the sessions `same` and half
`different`, the expected shares among all persons are Chinese 60.8%, Malay 20.1%, Indian 13.6%,
Others 5.5% (against 73.9, 13.5, 9.0 and 3.6% of residents). This follows from task 2's rule, and
`--plan` prints it.

**`--plan`** prints, for the design's sessions, the expected and the drawn number of sessions
for each pair of groups (person 1 / person 2), and the shares among persons, drawn and expected.
For the mock rehearsal's 72 sessions (36 per condition, the same people in both): Chinese /
Chinese expected 26.6; Others / Others expected 1.3; six of the sixteen pairs are expected fewer
than one session. **At real shares the smaller groups get few sessions**, so a per-group effect
(for example, toward Indian people) cannot be estimated from a screen of RF-10's size (section 9).

## 5. What is logged

- **The session record**: `session.personas[<agent>].ethnicity`, `session.visibility.ethnicity`,
  and `factors.ethnicity` (by agent) with `factors.ethnicity_visible`; `templates.factors` is
  `resolve_factors_v2`. The design in `config.json` gains `ethnicity_shares` (the file and its
  shares).
- **The outcome row** (`outcomes.jsonl`, `outcomes.csv`):

| Column | Meaning |
| --- | --- |
| `ethnicity_pair`, `ethnicity_visible` | the cell's levels |
| `p1_ethnicity`, `p2_ethnicity` | each person's group |
| `p1_other_ethnicity_shown`, `p2_...` | at how many of the person's decision points it was told the other's group: the other in view at a detail where factor lines are printed, with the switch on. Every group has a line, so this is the count of the line in the prompts (tested) |

- **RF-8's analysis** (`analysis/load.py`) reads the other's group **as told**, never as set: the
  predictor `same_ethnicity` is 1 when the agent was told the other's group and it is its own,
  and `ethnicity_unseen` is 1 when it was not told. The groups are kept as descriptive columns
  (`own_ethnicity`, `other_ethnicity` as told, `other_ethnicity_actual`), not as predictors: at
  real shares the smaller groups are too rare for a term of their own, which would make RF-8's
  separation problem worse (`WORK_LOG-63.md`, open questions 1 and 2). This is my choice
  (`WORK_LOG-92.md`, A3). The session-level terms `ethnicity_pair[different]` and
  `ethnicity_visible[False]` come from the design columns as for any factor.

## 6. The ethics gate

Real ethnicity is **off by default**: it is on only when a design names `ethnicity_pair`. **No
paid run may switch it on** unless `CLAUDE.md` holds this sentence, with the date filled in:

> Ethics sign-off for the real-ethnicity factor (issue #92): approved by the supervisor on YYYY-MM-DD

A paid run without it is refused before anything is sent: no session, no ledger line, and
`refused_no_sign_off` in `invocations.jsonl`. `--plan` says so. **A mock run needs none.** The
check is `negsim/ethics.py`'s, shared with perceived attractiveness (`pairwise-factors.md`,
section 6) and the fictional group (`fictional-groups.md`, section 6), each with its own sentence:
**one sign-off never stands for another** (tested both ways). Only the user adds the sentence,
once the supervisor has approved; nothing in negsim writes it.

**Recorded on 2026-10-24.** The user added the sentence to `CLAUDE.md`, approved by the
supervisor on 2026-10-24 (PR #93), before this issue was built. So a paid run may vary real
ethnicity once its own paid-run approval and cap are recorded (`CLAUDE.md`, pending sign-offs,
item 1). The gate is tested against a file without the sentence.

## 7. Rules: no rule may read it

The rule loader refuses, as `protected_attribute` and before every other check, a rule whose
condition or roles (the field, the role names, the tie policy) name real ethnicity:
- anything containing `ethnic` (`ethnicity`, `ethnicity_pair`, `p1_ethnicity`, `same_ethnicity`),
  as since issue #32, reported as before ("a person's group");
- a census group's name, or a word for race, as a whole word, ignoring case: `chinese`, `malay`,
  `malays`, `indian`, `indians`, `race`, `races`, `racial` (`REAL_ETHNICITY_WORDS`), reported as
  "a person's ethnicity".

**Others** is not protected on its own: it is an ordinary English word, and a rule naming "the
others" reads no group. A value such as `"Indian"` in a condition is refused, as is a role named
`the_chinese_one`. In rule generation such a rule is **kept and counted** as `protected_attribute`
and never written as a rule: a model trying to condition a rule on ethnicity is a finding.

**This keeps ethnicity out of the rule database only.** It stays in the design, the outcome rows,
RF-8's factor analysis and the factor-to-decision mapping, which is what the screen is for.

## 8. Personas for a crowd of 10,000 (documented, not built)

RF-18 runs crowds with ORCA and the extracted rules, with no LLM call. **Rules never read
ethnicity** (section 7), so a crowd run's outcome cannot depend on it, and a crowd needs no
groups at all. If a mined conflict from a crowd run is later prompted with ethnicity (D9), each
person would be drawn once, at the start of the run, at the resident shares with the run's seed,
and kept for the run: about 7,390 Chinese, 1,350 Malay, 900 Indian and 360 Others in 10,000. The
same limits apply (residents only; visitors at the same shares).

## 9. What it cannot show, and the open points

- **Same against different, not each group.** The screen's factor is `ethnicity_pair`. At real
  shares a per-group effect gets few sessions (section 4). Open question 3: a `balanced` option,
  with equal shares and the analysis weighted back to the real shares, would estimate
  group-specific effects better. Not built: the issue says build it only if the user asks.
- **Told, not seen.** The model is told a group in words; no appearance is described. An effect
  is an effect of the word.
- **"They look ..."** (open question 2, *for the supervisor*): telling an agent another's
  ethnicity as an inference from appearance.
- **Residents only, and visitors at the same shares** (section 3).
- **The persons' mix** differs from the residents' because of the `different` sessions' second
  draw (section 4).
- **The mock does not read the lines.** The rehearsal checks the pipeline, not a model.
