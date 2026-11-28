# Screening designs (issue #62, RF-7)

Which cells of the full factorial a resolution experiment runs, on which case geometries, which
of them are repeated exactly, and which sessions form counterfactual pairs. Code:
`negsim/resolution/screening.py` (the designs themselves) and `negsim/resolution/design.py`
(the session list); tests: `tests/test_screening.py`. Built on the mock; nothing here makes a
paid call.

## 1. Why

The resolution layer's design (RF-3) crosses every factor in full. With 12 two-level factors
that is 4,096 cells per case and condition, before any repeat; with 16, 65,536. A screen needs
far fewer: a **regular fractional factorial of resolution IV** holds up to 16 two-level factors
in 32 cells, with no main effect aliased with another main effect or with any two-factor
interaction. So RF-5's core and situational factors, and RF-6's pairwise ones, fit one 32-cell
screen. Interactions are left to Phase B (RF-13), where **counterfactual pairs**, two sessions
identical but for one factor, give the most direct evidence that one factor changes a decision.

D14 (`resolution.md`) adds two things: variation comes from **case geometries**, not blanket
repeats, and a small **exact-repeat set** measures the model's own randomness, the noise floor
that RF-8 compares counterfactual flip rates and stability against.

## 2. The config

Every key below is optional; a design without them is exactly RF-3's (section 8).

```yaml
design:
  kind: fractional          # full (the default) | fractional | sample
  cells: 32                 # fractional: 16 or 32 (default: the fewer that hold the factors)
                            # sample: how many cells to draw (required); full: not allowed
  seed: 62                  # draws the sample, the exact-repeat set, and the session order
  geometries:               # the cases the design runs on: one encounter type (section 5)
    - head_on_de176842@2    #   walking lines aligned
    - head_on_02dfbadb@2    #   20 cm apart
  exact_repeats: {cells: 8, times: 3}   # section 6
  factors:                  # as before (encounter-protocol.md, section 8); in a fractional
    ...                     # design each factor has one level (fixed) or two (screened)
  counterfactual_pairs:     # section 7
    - base: {age_pair: same, ..., mapping: p1_lower}
      factor: urgency
      to: p1                # optional when the factor has two levels
```

With `design.geometries` the config's `cases` block gives at most the `store`: the geometries
are the cases. `configs/resolution/resolve_screening_mock_rehearsal.yaml` is a complete example
of round 1's shape (D15): 32 cells of a 2^(12-7) design, two geometries, 8 cells repeated 3
times, all three conditions and one pair, 252 sessions.

## 3. `fractional`: a regular 2^(k-p) design

**Two-level factors only.** A factor listed with two levels is *screened*: it is a column of the
fraction. A factor listed with one level is *fixed*: the same in every cell. A factor with more
levels is refused (narrow it to two, or use `sample`). `age_pair` and `gender_pair` must
therefore be narrowed for a fraction (for example `[same, p1_older]`), and `task` gives way to
`urgency`, its two-level form (RF-5).

**`mapping` is a column like any other.** Mapping (which of the case's two agents is person 1)
must stay counterbalanced in every kind of design. In a fraction it is one of the screened
factors, so it is balanced 16 and 16 in 32 cells and its main effect is clear of every
two-factor interaction; it counts towards the 16. (Speaking order is not a factor of this
layer: the agents at one decision point are prompted on the same world state. The `rulegen`
layer is unchanged and keeps its `order` factor; section 9.)

**The construction.** With N cells (16 or 32) there are b = log2 N base factors, crossed in
full in standard order (the first changes fastest). Each further factor's column is the
product of some base columns, its **generator**. The screened factors take the columns in the
order of `ALL_FACTORS` (the order of an outcome row), so `mapping`, last in that order, takes
the last column. Level 1 of a factor (as listed in the config) is -1, level 2 is +1.

**Which cells.** `cells` sets N; by default the fewer of 16 and 32 that hold the screened
factors at resolution IV, that is k <= N/2 (Chen & Cheng 2006, section 2:
`refs/rf7_chen_cheng2006_excerpts.txt`, lines 137 to 142). Refused, with a message: more than
16 screened factors (no 32-cell design holds them at resolution IV: fix some at one level);
more than N/2 in N cells; fewer than b (the full factorial has fewer cells than asked: use
`full`). k = b is the full factorial of N cells.

**The generators come from published tables** (`screening.GENERATORS`, with `SOURCES`):

| Cells | Factors | Design | Generators (factors b+1, b+2, ...) | Source |
| --- | --- | --- | --- | --- |
| 16 | 5 | 2^(5-1), res. V | 1234 | NIST, `refs/rf7_nist_2to5m1.txt` |
| 16 | 6 | 2^(6-2), res. IV | 123, 234 | NIST, `rf7_nist_2to6m2.txt` |
| 16 | 7 | 2^(7-3), res. IV | 123, 234, 134 | NIST, `rf7_nist_2to7m3.txt` |
| 16 | 8 | 2^(8-4), res. IV | 234, 134, 123, 124 | NIST, `rf7_nist_2to8m4.txt` |
| 32 | 6 | 2^(6-1), res. VI | 12345 | NIST, `rf7_nist_2to6m1.txt` |
| 32 | 7 | 2^(7-2), res. IV | 1234, 1245 | NIST, `rf7_nist_2to7m2.txt` |
| 32 | 8 | 2^(8-3), res. IV | 123, 124, 2345 | NIST, `rf7_nist_2to8m3.txt` |
| 32 | 9 | 2^(9-4), res. IV | 2345, 1345, 1245, 1235 | NIST, `rf7_nist_2to9m4.txt` |
| 32 | 10 | 2^(10-5), res. IV | 1234, 1235, 1245, 1345, 2345 | NIST, `rf7_nist_2to10m5.txt` |
| 32 | 11 | 2^(11-6), res. IV | 123, 234, 345, 134, 145, 245 | NIST, `rf7_nist_2to11m6.txt` |
| 32 | 12 to 16 | 2^(k-(k-5)), res. IV | the first k - 5 of 123, 124, 125, 134, 135, 145, 234, 235, 245, 345, 12345 | Chen & Cheng 2006 (below) |

- **NIST**: NIST/SEMATECH *e-Handbook of Statistical Methods*, section 5.3.3.4.7, "Summary
  tables of useful fractional factorial designs", Table 3.17
  (https://www.itl.nist.gov/div898/handbook/pri/section3/pri3347.htm, cached as
  `refs/rf7_nist_table_3_17.html`), whose summaries the page attributes to Box, Hunter & Hunter
  (1978) and Montgomery (2000). Each design's generators are in its linked file, cached as
  `refs/rf7_nist_2to<k>m<p>.txt` ("DEFINITION" column). A test reads the cached files and checks
  that the generators in the code are theirs.
- **Chen & Cheng 2006**: H. H. Chen and C.-S. Cheng, "Doubling and projection: a method of
  constructing two-level designs of resolution IV", *The Annals of Statistics* 34(1): 546-558,
  doi 10.1214/009053605000000813 (preprint arXiv:math/0605616; passages in
  `refs/rf7_chen_cheng2006_excerpts.txt`). Table 3.17 stops at 11 factors in 32 runs. Chen &
  Cheng's Corollary 3.6 (excerpt lines 468 to 477) shows that for 5N/16 < k < N/2, so for 11 to
  15 factors in 32 runs, every regular resolution IV design is obtained by deleting columns from
  the saturated resolution IV design (k = N/2 = 16), which is unique up to isomorphism (lines 199
  to 206) and has minimum aberration (lines 529 to 537). That saturated 2^(16-11) design is the
  set of every odd-length product of the 5 base factors (the 5 base factors, the 10 three-letter
  products and 12345): the product of two odd-length words has even length, so no main effect
  can equal another or a two-factor interaction. **The 12 to 15 factor designs are not copied
  from a printed table**: they delete the last 16 - k columns of the list above, the deletion
  that gives minimum aberration, found by searching every deletion that keeps the base factors
  (`tests/test_screening.py` repeats the search). Keeping the base factors loses nothing: an
  affine map of the saturated design takes any 5 independent columns to them. As a check, the
  search finds for 11 factors the same word-length pattern as NIST's design (A4 = 25, A6 = 27).

**Resolution is checked on the cells.** Whatever the table says, `screening.aliasing_problems`
checks the run matrix itself before a design is used: every column balanced, no two columns
equal up to sign, and no column equal up to sign to the product of two others. A design that
fails is refused. `screening.word_length_pattern` gives (A1, ..., Ak), the number of defining
words of each length; the four-letter words count which two-factor interactions are aliased
with each other:

| Cells | Factors | A4 (A5, A6) |
| --- | --- | --- |
| 16 | 5, 6, 7, 8 | 0 (A5 = 1), 3, 7, 14 |
| 32 | 6, 7, 8, 9, 10 | 0 (A6 = 1), 1 (A5 = 2), 3 (A5 = 4), 6 (A5 = 8), 10 (A5 = 16) |
| 32 | 11, 12, 13, 14, 15, 16 | 25, 38, 55, 77, 105, 140 (all even designs: no word of odd length) |

**What a resolution IV screen can and cannot say.** Every main effect is estimated clear of
every two-factor interaction (assuming three-factor and higher interactions are negligible),
but two-factor interactions are aliased in chains with each other. With 12 factors in 32 cells,
38 four-letter words tie the 66 two-factor interactions into alias sets. RF-8 reports main
effects from the screen; an interaction suspected there is resolved with counterfactual pairs
or a Phase B design (RF-13).

## 4. `sample`: a balanced random sample

`cells` cells drawn from the full factorial with the seed (`random.Random("sample:<seed>")`).
Each factor's levels are drawn as a balanced column (every level `N // L` or `N // L + 1`
times; which levels get the extra one is drawn), the columns shuffled independently and zipped
into cells; a draw with two equal cells is drawn again (up to 1,000 times, then refused). Unlike
`fractional`, `sample` takes factors of any number of levels, but it promises nothing about
aliasing: it is for designs no table holds. Asking for every cell gives the full factorial.

## 5. Geometries (D14)

`design.geometries` lists the cases the design runs on, `id` or `id@version` (without a version,
the latest). They must be of **one encounter type and one scenario plug-in** (refused
otherwise), and no two may have the same geometry. **Each cell runs once on each geometry**, so
every level of every factor meets every geometry equally often (tested). Each session records
its geometry (`geometry`, the case's variant, for example `layout=apart_20cm`), and so does its
outcome row; session ids already name the case. Round 1's head-on cases offer four geometries:
`head_on_de176842` (aligned), `head_on_02dfbadb` (20 cm apart), `head_on_59908410` (40 cm) and
`head_on_ff0aa402` (52 cm).

Without `design.geometries`, the config's `cases` choose the cases as before, and every cell
still runs on every case; the cases may then be of several encounter types, and no `geometry`
is recorded.

## 6. The exact-repeat set (D14)

`exact_repeats: {cells: n, times: t}` (t >= 2) picks n of the design's cells and runs each t
times **in all** (its design session and t - 1 more), **on one geometry**, with identical
prompts. Its sessions are marked `exact_repeat_set: true` and numbered `_r1` to `_r<t>`; every
other session is `_r1` and `false`.

- **The cells** are chosen with the seed (`random.Random("exact_repeats:<seed>")`), balanced
  across each screened factor's levels where possible (`screening.balanced_subset`: from 20
  random starts, swap a chosen cell for another while that lowers the total imbalance; the best
  end wins). For 8 of the 32 cells of a 12-factor fraction it finds every factor at 4 and 4 (tested).
- **The geometry** of each chosen cell: the cases taken in turn, in an order drawn with the same
  seed, so that 8 cells on 2 geometries are 4 on each.
- **The same cells in every condition.**
- **Identical prompts.** A session's id and repeat number are request metadata, never sent, so
  the repeats of a cell send the same messages byte for byte (tested on the mock, call for call).
  The model has no seed, so its replies may differ: that spread is the noise floor.

`repeats` (RF-3: every cell run that many times) still works for a full design; a design names
`repeats` or `exact_repeats`, not both.

## 7. Counterfactual pairs

Each entry of `counterfactual_pairs` is a **base cell** (a level of every screened factor; a
fixed factor may be left out) and a **factor** to flip, with `to` its other level (needed only
when the factor has more than two levels; it may be a level the design does not otherwise use).
It becomes, in every condition and on every case, **two sessions identical except for that
factor**: same case, same seed (the case's run), same mapping (flipping `mapping` is refused),
same templates. Both carry the same `pair_id` (`<I|N|T>_<case>_x<pair code>`), a `pair_role`
(`base` or `flipped`) and the `pair_factor`. Their ids are `<I|N|T>_<case>_<cell code>_x<pair
code>`, so a pair's base never collides with a design session of the same cell; the pair code
is eight hexadecimal characters of the base cell's code, the factor and the level. A base cell
may be a cell of the design, or of the exact-repeat set, or neither. A pair listed twice is
refused.

**A pair that flips one person's group of real ethnicity** (issue #92): `factor: p1_ethnicity` or
`p2_ethnicity`, with `ethnicity: {p1, p2}` the base's groups (fixed, not drawn) and `to` the
flipped person's other group. Its sessions also carry `pair_change` (`malay->indian`), and their ids
end in `_base` and `_flipped`, because the two cells may be the same (`ethnicity.md`, section 4).
Its pair code includes the groups; every other pair's code is as before.

## 8. What stays as before

A config that names none of `kind`, `cells`, `geometries`, `exact_repeats` and
`counterfactual_pairs` has exactly the cells, session ids, order, records and cost preview it
had before issue #62: `design.as_dict()` names the new keys only when a config does, and a
session's `geometry` and `pair_*` keys appear only when used. Tested against RF-3's algorithm for
every resolution config that existed before it (`configs/resolution/`), and, before the commit, by comparing the plans
of those configs with the commit before (identical sessions, configs and previews). A config
that adds `kind: full` and nothing else gives the same sessions too.

## 9. The `rulegen` layer is unchanged (a decision)

The issue was written when only issue #30's layer (`negsim/rulegen/design.py`) existed, and
points to it. RF-3 (#58) has since built the resolution layer, whose design said "RF-7 (#62)
builds the screening designs", and geometries and the exact-repeat set are D14's, which only
the resolution layer has. So the screening designs are built there, for RF-10's screen. The
rulegen layer (#30's, superseded by track #55) is left exactly as it was, with its `order`
factor ("the `rulegen` layer keeps it as before", task 5). The fraction, the sample and the
balanced subset are in `screening.py`, independent of either layer, if the rulegen layer ever
needs them. **This is an assumption made in issue #62, recorded in `WORK_LOG-62.md`.**

## 10. `--plan`

```
python run_experiment.py configs/resolution/resolve_screening_mock_rehearsal.yaml --plan
```

prints, besides the worst-case cost per condition (`encounter-protocol.md`, section 6: up to 3
decision points per agent, plus the debriefs), the design's kind and cells (for a fraction, its
2^(k-p) form and resolution), the geometries, the exact-repeat set and how many sessions it
adds, the pairs, and per condition how many sessions are the design's, exact repeats, and in
pairs.

**The rehearsal's worst-case preview is USD 17.36** (252 sessions, deepseek-flash at peak
prices, every call allowed its 2 attempts of 3 transport tries each). That is a strict bound,
not an estimate, but the paid runner refuses a run whose bound exceeds its cap, and track #55
estimates round 1 at "of the order of USD 0.50". RF-9's pilot measures what a session costs;
the cap of round 1, or the bound, will have to be set from it (`WORK_LOG-62.md`, open questions).
